"""
This module provides functionality to search and extract files from various
extraction sources.
It handles file pattern matching, copying files to a data folder, extracting
metadata (creation/modification dates), and decrypting encrypted iTunes backups.

Classes:
    FileInfo: Container for file metadata (source path, creation date, modification date)
    FileSeekerBase: Abstract base class for file searching implementations
    FileSeekerDir: File seeker for local directories
    FileSeekerItunes: File seeker for iTunes backups (supports encryption)
    FileSeekerTar: File seeker for TAR/TAR.GZ archives
    FileSeekerZip: File seeker for ZIP archives
    FileSeekerFile: File seeker for individual files

Functions:
    get_itunes_backup_type: Determines iTunes backup type (db/mbdb)
    get_itunes_backup_encryption: Checks if iTunes backup is encrypted
    check_itunes_backup_status: Validates iTunes backup status and encryption
    decrypt_itunes_backup: Decrypts encrypted iTunes backups using provided passcode
"""

import time as timex
import fnmatch
import os
import tarfile
import hashlib
import struct

from pathlib import Path
from shutil import copyfile
from zipfile import ZipFile
from fnmatch import _compile_pattern
from functools import lru_cache

# Yes, this is hazmat, but we're only using it to unwrap existing keys
import cryptography.hazmat.primitives.keywrap as crypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


from scripts.ilapfuncs import get_plist_file_content, get_plist_content, logfunc, \
    is_platform_windows, open_sqlite_db_readonly, sanitize_file_path

normcase = lru_cache(maxsize=None)(os.path.normcase)
domains = {
    "AppDomain-": "private/var/mobile/Containers/Data/Application",
    "AppDomainGroup-": "private/var/mobile/Containers/Shared/AppGroup",
    "AppDomainPlugin-": "private/var/mobile/Containers/Data/PluginKitPlugin",
    "CameraRollDomain": "private/var/mobile",
    "DatabaseDomain": "private/var/db",
    "HealthDomain": "private/var/mobile",
    "HomeDomain": "private/var/mobile",
    "HomeKitDomain": "private/var/mobile",
    "InstallDomain": "private/var/installd",
    "KeyboardDomain": "private/var/mobile",
    "KeychainDomain": "private/var/protected/trustd/private",
    "ManagedPreferencesDomain": "private/var/Managed Preferences",
    "MediaDomain": "private/var/mobile",
    "MobileDeviceDomain": "private/var/MobileDevice",
    "NetworkDomain": "private/var/networkd",
    "ProtectedDomain": "private/var/protected",
    "RootDomain": "private/var/root",
    "SysContainerDomain-": "private/var/containers/Data/System",
    "SysSharedContainerDomain-": "private/var/containers/Shared/SystemGroup",
    "SystemPreferencesDomain": "private/var/preferences",
    "TonesDomain": "private/var/mobile",
    "WirelessDomain": "private/var/wireless"
}


# iTunes backups functions
def get_itunes_backup_type(directory):
    """
    Determines the type of iTunes backup present in the specified directory.
    This function checks for the presence of specific manifest files that indicate
    the type of iTunes backup format used.
    Args:
        directory (str): The path to the directory containing the iTunes backup files.
    Returns:
        str: The backup type as a string:
            - "db" if Manifest.db exists (iOS 10+ backup format)
            - "mbdb" if Manifest.mbdb exists (older iOS backup format)
            - "" (empty string) if neither manifest file is found
    """
    if os.path.exists(os.path.join(directory, "Manifest.db")):
        return "db"
    if os.path.exists(os.path.join(directory, "Manifest.mbdb")):
        return "mbdb"
    return ""


def get_itunes_backup_encryption(directory):
    """
    Determines whether an iTunes backup is encrypted.
    Args:
        directory (str): The path to the iTunes backup directory.
    Returns:
        bool or None: True if the backup is encrypted, False if not encrypted,
                      or None if the 'IsEncrypted' key is not found in the manifest.
    """
    manifest_path = os.path.join(directory, "Manifest.plist")
    manifest = get_plist_file_content(manifest_path)
    return manifest.get("IsEncrypted")


def check_itunes_backup_status(directory, backup_type):
    """
    This function determines whether an iTunes backup is supported based on its
    type and encryption status.
    Args:
        directory (str): The path to the directory containing the iTunes backup.
        backup_type (str): The type of backup, either "db" (actual iTunes backup) or
            "mbdb" (legacy iTunes backup).
    Returns:
        tuple: A tuple containing:
            - bool: Whether the backup is supported (True) or not (False).
            - bool or str: For supported backups, indicates if encrypted (True/False).
                For unsupported backups, this is an error message string.
            - str: A descriptive message about the backup status.
                Possible values:
                - "iTunes backup supported" (unencrypted, db or mbdb type)
                - "iTunes Legacy Encrypted Backup not supported" (encrypted mbdb)
                - "iTunes Encrypted Backup" (encrypted db)
                - "Missing Manifest.db, Manifest.mbdb or Manifest.plist" (unknown type)
    Note:
        Legacy encrypted backups (mbdb type with encryption) are not supported.
        For encrypted db backups, a log message is generated.
    """
    backup_encrypted = get_itunes_backup_encryption(directory)
    if not backup_encrypted and (backup_type == "db" or backup_type == "mbdb"):
        return True, False, "iTunes backup supported"
    if backup_encrypted and backup_type == "mbdb":
        return False, True, "iTunes Legacy Encrypted Backup not supported"
    if backup_encrypted and backup_type == "db":
        logfunc('Detected encrypted iTunes backup')
        return True, True, "iTunes Encrypted Backup"
    return False, "Missing Manifest.db, Manifest.mbdb or Manifest.plist"


def decrypt_itunes_backup(directory, passcode):
    """
    Decrypt an iTunes backup using the provided passcode.
    This function parses the backup's Manifest.plist file to extract the encryption
    keybag and manifest key, then uses the provided passcode to decrypt the protection
    class keys and ultimately the Manifest.db encryption key.
    Args:
        directory (str): Path to the iTunes backup directory containing Manifest.plist
        passcode (str): The backup password/passcode used to encrypt the backup
    Returns:
        tuple: A tuple containing:
            - If successful: ((dict, bytes), str) where dict contains protection classes
              with unwrapped keys, bytes is the unwrapped manifest key, and str is success message
            - If failed: (None, str) where str contains the error message
        Possible return messages:
            - "Decryption successful": Backup was successfully decrypted
            - "No password provided": Passcode was None or invalid type
            - "Incorrect password": Passcode was incorrect, could not unwrap protection class keys
            - "Could not find protection class for Manifest.db": Missing required protection class
    Notes:
        - The function uses PBKDF2 key derivation with the passcode and keybag salt/iterations
        - Protection class keys are unwrapped using AES key unwrapping
        - The manifest key class identifies which protection class is used for Manifest.db
        - Logs decryption status and errors using logfunc()
    """
    protection_classes = {}
    manifest_key_class = None
    manifest_path = os.path.join(directory, "Manifest.plist")
    manifest = get_plist_file_content(manifest_path)

    manifest_key = manifest.get("ManifestKey")
    manifest_key_class = int.from_bytes(manifest_key[0:4], byteorder="little")
    manifest_wrapped_key = manifest_key[4:]
    backup_keybag = manifest.get("BackupKeyBag")

    # Initialize some values
    tmp_backup_keybag_index = 0
    tmp_protection_class = {}
    tmp_salt = ''
    tmp_iter = 0
    tmp_double_protection_salt = ''
    tmp_double_protection_iter = 0
    keybag_uuid = None

    # Iterate across the entire Keybag contents
    while tmp_backup_keybag_index < len(backup_keybag):
        # Grab the type of value we're looking at
        tmp_string_type = backup_keybag[
            tmp_backup_keybag_index:tmp_backup_keybag_index + 4]
        tmp_backup_keybag_index += 4

        # Figure out the length we need to pull
        tmp_length = int.from_bytes(backup_keybag[
            tmp_backup_keybag_index:tmp_backup_keybag_index + 4])
        tmp_backup_keybag_index += 4

        # Store the actual value itself
        tmp_value = backup_keybag[
            tmp_backup_keybag_index:tmp_backup_keybag_index + tmp_length]
        tmp_backup_keybag_index += tmp_length

        match tmp_string_type:
            case b'CLAS':
                tmp_protection_class['CLAS'] = int.from_bytes(tmp_value)
            case b'DPIC':
                tmp_double_protection_iter = int.from_bytes(tmp_value)
            case b'DPSL':
                tmp_double_protection_salt = tmp_value
            case b'ITER':
                tmp_iter = int.from_bytes(tmp_value)
            case b'KTYP':
                tmp_protection_class['KTYP'] = int.from_bytes(tmp_value)
            case b'UUID':
                if keybag_uuid is None:
                    keybag_uuid = tmp_value
                else:
                    if tmp_protection_class:
                        protection_classes[tmp_protection_class['CLAS']] = tmp_protection_class
                    tmp_protection_class = {}
            case b'SALT':
                tmp_salt = tmp_value
            case b'WPKY':
                tmp_protection_class['WPKY'] = tmp_value
            case b'WRAP':
                if tmp_protection_class:
                    tmp_protection_class['WRAP'] = tmp_value

    # Clean up the open protection class
    protection_classes[tmp_protection_class['CLAS']] = tmp_protection_class

    # Decrypt the Manifest password
    try:
        initial_unwrapped_key = hashlib.pbkdf2_hmac(
            'sha256', str.encode(passcode), tmp_double_protection_salt,
            tmp_double_protection_iter)
        unwrapped_key = hashlib.pbkdf2_hmac('sha1', initial_unwrapped_key,
                                            tmp_salt, tmp_iter, dklen=32)
    except TypeError:
        return None, "No password provided"
    # Unwrap all of the protection class keys
    for _, protection_class_value in protection_classes.items():
        protection_class = protection_class_value
        try:
            protection_class['Unwrapped'] = crypt.aes_key_unwrap(
                unwrapped_key, protection_class['WPKY'])
        except crypt.InvalidUnwrap:
            logfunc("Could not unwrap a protection class key, likely due to an incorrect passcode. Exiting.")
            return None, "Incorrect password"

    # Find the right one for the Manifest.db
    if manifest_key_class not in protection_classes:
        logfunc("Did not find the right protection class to decrypt Manifest.db. Exiting.")
        return None, "Could not find protection class for Manifest.db"

    manifest_protection_class = protection_classes[manifest_key_class]
    unwrapped_manifest_key = crypt.aes_key_unwrap(manifest_protection_class["Unwrapped"], manifest_wrapped_key)

    logfunc(f"Manifest.db was successfully decrypted with passcode {passcode}")
    return (protection_classes, unwrapped_manifest_key), "Decryption successful"


class FileInfo:
    """
    A class to store file metadata information.
    Attributes:
        source_path (str): The full path to the source file.
        creation_date (datetime): The date and time when the file was created.
        modification_date (datetime): The date and time when the file was last modified.
    """

    def __init__(self, source_path, creation_date, modification_date):
        self.source_path = source_path
        self.creation_date = creation_date
        self.modification_date = modification_date


class FileSeekerBase:
    """
    Abstract base class for file seeking operations.
    This class provides an interface for searching files and performing cleanup operations
    in different storage contexts (e.g., filesystem, archives, databases).
    """
    def search(self, filepattern, return_on_first_hit=False):
        '''Returns a list of paths for files/folders that matched'''

    def cleanup(self):
        '''close any open handles'''


class FileSeekerDir(FileSeekerBase):
    """
    This class extends FileSeekerBase to provide functionality for searching files
    within a directory structure, copying matched files to a destination folder,
    and caching search results for performance.
    Attributes:
        directory (str): The root directory to search within.
        data_folder (str): The destination folder where matched files will be copied.
        _all_files (list): Internal list containing all file paths found in the directory tree.
        searched (dict): Cache of search results, mapping file patterns to lists of matched paths.
        copied (dict): Mapping of source file paths to their copied destination paths.
        file_infos (dict): Dictionary storing FileInfo objects with metadata for copied files.
    Methods:
        build_files_list(directory): Recursively scans directory and populates _all_files list.
        search(filepattern, return_on_first_hit=False, force=False): Searches for files matching
            the given pattern, copies them to data_folder, and returns matching paths.
    """

    def __init__(self, directory, data_folder):
        FileSeekerBase.__init__(self)
        self.directory = directory
        self._all_files = []
        self.data_folder = data_folder
        logfunc('Building files listing...')
        self.build_files_list(directory)
        logfunc(f'File listing complete - {len(self._all_files)} files')
        self.searched = {}
        self.copied = {}
        self.file_infos = {}

    def build_files_list(self, directory):
        '''Populates all paths in directory into _all_files'''
        try:
            files_list = os.scandir(directory)
            for item in files_list:
                self._all_files.append(item.path)
                if item.is_dir(follow_symlinks=False):
                    self.build_files_list(item.path)
        except OSError as ex:
            logfunc(f'Error reading {directory} ' + str(ex))

    def search(self, filepattern, return_on_first_hit=False, force=False):
        if filepattern in self.searched and not force:
            pathlist = self.searched[filepattern]
            return self.searched[filepattern][0] if return_on_first_hit and pathlist else pathlist
        pathlist = []
        pat = _compile_pattern(normcase(filepattern))
        root = normcase("root/")
        for item in self._all_files:
            if pat(root + normcase(item)) is not None:
                item_rel_path = item.replace(self.directory, '')
                data_path = os.path.join(self.data_folder, item_rel_path[1:])
                if is_platform_windows():
                    data_path = data_path.replace('/', '\\')
                if item not in self.copied or force:
                    try:
                        if os.path.isdir(item):
                            pathlist.append(data_path)
                        elif os.path.isfile(item):
                            os.makedirs(os.path.dirname(data_path), exist_ok=True)
                            copyfile(item, data_path)
                            self.copied[item] = data_path
                            creation_date = Path(item).stat().st_ctime
                            modification_date = Path(item).stat().st_mtime
                            file_info = FileInfo(item, creation_date, modification_date)
                            self.file_infos[data_path] = file_info
                        else:
                            logfunc(f"INFO: Item '{item}' is neither a file nor a directory "
                                    "(e.g. symlink not followed, or broken). Skipped.")
                    except OSError as ex:
                        logfunc(f'Could not copy {item} to {data_path} ' + str(ex))
                else:
                    data_path = self.copied[item]
                pathlist.append(data_path)
                if return_on_first_hit:
                    self.searched[filepattern] = pathlist
                    return data_path
        self.searched[filepattern] = pathlist
        return pathlist


class FileSeekerItunes(FileSeekerBase):
    """
    This is a subclass of FileSeekerBase that provides functionality to
    search and manage files from iTunes backups. It supports both Manifest.db and
    Manifest.mbdb formats for file listing and handles decryption of files if
    decryption keys are provided.
    Attributes:
        directory (str): The directory containing the iTunes backup.
        data_folder (str): The folder where the extracted files will be stored.
        backup_type (str): The type of backup, either 'db' or 'mbdb'.
        decryption_keys (list): A list of keys used for decrypting files, if applicable.
        _all_files (dict): A dictionary mapping full file paths to their corresponding hash filenames.
        _all_file_meta (dict): A dictionary storing metadata for each file.
        files_metadata (dict): A dictionary mapping hash filenames to their metadata.
        searched (dict): A dictionary storing search results for file patterns.
        copied (dict): A dictionary tracking copied files and their destinations.
        file_infos (dict): A dictionary storing file information such as creation and modification dates.
    Methods:
        __init__(directory, data_folder, backup_type, decryption_keys):
            Initializes the FileSeekerItunes instance and builds the file listing based on the backup type.
        get_root_path_from_domain(domain):
            Retrieves the root path associated with a given domain.
        build_files_list_from_manifest_db(manifest_path):
            Populates paths from Manifest.db files into _all_files.
        build_files_list_from_manifest_mbdb(manifest_path):
            Populates paths from Manifest.mbdb files into _all_files.
        search(filepattern, return_on_first_hit=False, force=False):
            Searches for files matching the given pattern and returns their paths.
    """

    def __init__(self, directory, data_folder, backup_type, decryption_keys):
        FileSeekerBase.__init__(self)
        self.directory = directory
        self._all_files = {}
        self._all_file_meta = {}
        self.data_folder = data_folder
        self.files_metadata = {}
        self.decryption_keys = decryption_keys
        self.backup_type = backup_type
        logfunc('Building files listing...')
        if backup_type == "db":
            manifest_path = os.path.join(directory, "Manifest.db")
            if decryption_keys:
                unwrapped_manifest_key = decryption_keys[1]
                with open(manifest_path, "rb") as manifest_contents:
                    cipher = Cipher(algorithms.AES(unwrapped_manifest_key),
                                    modes.CBC(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'))
                    decryptor = cipher.decryptor()
                    decrypted_manifest_contents = decryptor.update(manifest_contents.read()) + decryptor.finalize()
                    manifest_path = os.path.join(data_folder, "Manifest.db")
                    with open(manifest_path, "wb") as new_manifest_contents:
                        new_manifest_contents.write(decrypted_manifest_contents)

            self.build_files_list_from_manifest_db(manifest_path)
        elif backup_type == "mbdb":
            manifest_path = os.path.join(directory, "Manifest.mbdb")
            self.build_files_list_from_manifest_mbdb(manifest_path)
        logfunc(f'File listing complete - {len(self._all_files)} files')
        self.searched = {}
        self.copied = {}
        self.file_infos = {}

    def get_root_path_from_domain(self, domain):
        """
        Retrieve the root path associated with a given domain.
        Args:
            domain (str): The domain for which to retrieve the root path.
        Returns:
            str: The root path associated with the domain, or an empty string
                 if the domain is not found.
        """
        if domain in domains:
            return domains[domain]
        if '-' in domain:
            dash_position = domain.find("-") + 1
            path = domains[domain[:dash_position]]
            bundle_identifier = domain[dash_position:]
            return os.path.join(path, bundle_identifier)
        return ''

    def build_files_list_from_manifest_db(self, manifest_path):
        '''Populates paths from Manifest.db files into _all_files'''
        try:
            db = open_sqlite_db_readonly(manifest_path)
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT fileID, domain, relativePath, file
                FROM Files
                WHERE flags=1
                """
            )
            all_rows = cursor.fetchall()
            for row in all_rows:
                hash_filename = row[0]
                domain = row[1]
                root_path = self.get_root_path_from_domain(domain)
                relative_path = row[2]
                file_metadata = row[3]
                full_path = os.path.join(root_path, relative_path)
                self._all_files[full_path] = hash_filename
                if self.decryption_keys:
                    # Load the file's plist and find the encryption key
                    tmp_file_plist = get_plist_content(row[3])
                    tmp_wrapped_key = tmp_file_plist["EncryptionKey"]["NS.data"]

                    # Store the results into a dict for future
                    self._all_file_meta[full_path] = {}
                    self._all_file_meta[full_path]['Class'] = int.from_bytes(tmp_wrapped_key[0:4], byteorder="little")
                    self._all_file_meta[full_path]['Key'] = tmp_wrapped_key[4:]
                    self._all_file_meta[full_path]['Size'] = tmp_file_plist["Size"]
                self.files_metadata[hash_filename] = file_metadata
            db.close()
        except Exception as ex:
            logfunc(f'Error opening Manifest.db from {manifest_path}, ' + str(ex))
            raise ex

    def build_files_list_from_manifest_mbdb(self, manifest_path):
        '''Populates paths from Manifest.mbdb files into _all_files'''
        def getint(data, offset, intsize):
            """Retrieve an integer (big-endian) and new offset from the current offset"""
            value = 0
            while intsize > 0:
                value = (value << 8) + data[offset]
                offset = offset + 1
                intsize = intsize - 1
            return value, offset

        def getstring(data, offset, binary=False):
            """Retrieve a string and new offset from the current offset into the data"""
            if chr(data[offset]) == chr(0xFF) and chr(data[offset+1]) == chr(0xFF):
                return '', offset+2  # Blank string
            length, offset = getint(data, offset, 2)  # 2-byte length
            value = "" if binary else data[offset:offset+length].decode()
            return value, (offset + length)

        def process_mbdb_file(manifest_path):
            files = []
            with open(manifest_path, 'rb') as f:
                data = f.read()
            if data[0:4].decode() != "mbdb":
                raise UnicodeDecodeError("This does not look like an MBDB file")
            offset = 4
            offset = offset + 2  # value x05 x00, not sure what this is
            while offset < len(data):
                domain, offset = getstring(data, offset)
                filename, offset = getstring(data, offset)
                _, offset = getstring(data, offset, True)
                _, offset = getstring(data, offset, True)
                _, offset = getstring(data, offset, True)
                _, offset = getint(data, offset, 2)
                _, offset = getint(data, offset, 4)
                _, offset = getint(data, offset, 4)
                _, offset = getint(data, offset, 4)
                _, offset = getint(data, offset, 4)
                _, offset = getint(data, offset, 4)
                _, offset = getint(data, offset, 4)
                _, offset = getint(data, offset, 4)
                _, offset = getint(data, offset, 8)
                _, offset = getint(data, offset, 1)
                numprops, offset = getint(data, offset, 1)
                for _ in range(numprops):
                    _, offset = getstring(data, offset, True)
                    _, offset = getstring(data, offset, True)
                hash_filename = hashlib.sha1(f"{domain}-{filename}".encode()).hexdigest()
                files.append((hash_filename, domain, filename))
            return files

        try:
            all_rows = process_mbdb_file(manifest_path)
            for row in all_rows:
                hash_filename = row[0]
                domain = row[1]
                root_path = self.get_root_path_from_domain(domain)
                relative_path = row[2]
                full_path = os.path.join(root_path, relative_path)
                self._all_files[full_path] = hash_filename
        except Exception as ex:
            logfunc(f'Error opening Manifest.mbdb from {self.directory}, ' + str(ex))
            raise ex

    def search(self, filepattern, return_on_first_hit=False, force=False):
        if filepattern in self.searched and not force:
            pathlist = self.searched[filepattern]
            return self.searched[filepattern][0] if return_on_first_hit and pathlist else pathlist
        pathlist = []
        matching_keys = fnmatch.filter(self._all_files, filepattern)
        for relative_path in matching_keys:
            hash_filename = self._all_files[relative_path]
            if self.backup_type == "db":
                original_location = os.path.join(self.directory, hash_filename[:2], hash_filename)
                metadata = get_plist_content(self.files_metadata[hash_filename])
                creation_date = metadata.get('Birth', 0)
                modification_date = metadata.get('LastModified', 0)
            else:
                original_location = os.path.join(self.directory, hash_filename)
                # TO DO: extract creation and modification dates from manifest.mbdb
                creation_date = 0
                modification_date = 0
            data_path = os.path.join(self.data_folder, sanitize_file_path(relative_path))
            if is_platform_windows():
                data_path = data_path.replace('/', '\\')
            if original_location not in self.copied or force:
                try:
                    os.makedirs(os.path.dirname(data_path), exist_ok=True)

                    # Handle encrypted backups differently, don't just copy the encrypted files
                    if self.decryption_keys:
                        protection_classes = self.decryption_keys[0]
                        # Snag the right protection class
                        tmp_file_meta = self._all_file_meta[relative_path]
                        if tmp_file_meta['Class'] not in protection_classes:
                            logfunc(f'Can\'t locate the protection class for {relative_path}: {tmp_file_meta["Class"]}')
                            raise KeyError
                        tmp_protection_class = protection_classes[tmp_file_meta['Class']]

                        # Grab the file's key
                        tmp_file_wrapped_key = tmp_file_meta['Key']
                        tmp_file_unwrapped_key = crypt.aes_key_unwrap(tmp_protection_class['Unwrapped'],
                                                                      tmp_file_wrapped_key)

                        # Open the file and snag the contents
                        with open(original_location, "rb") as temp_original_file:
                            # Decrypt the contents, Apple uses a 0'd out 16-byte IV
                            cipher = Cipher(
                                algorithms.AES(tmp_file_unwrapped_key),
                                modes.CBC(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'))
                            decryptor = cipher.decryptor()
                            decrypted_contents = decryptor.update(temp_original_file.read()) + decryptor.finalize()

                            # Write the decrypt into the expected located, only write the expected size, no padding
                            with open(data_path, "wb") as temp_new_file:
                                temp_new_file.write(decrypted_contents[0:tmp_file_meta['Size']])

                    # If not encrypted, just copy the thing
                    else:
                        copyfile(original_location, data_path)

                    file_info = FileInfo(original_location, creation_date, modification_date)
                    self.file_infos[data_path] = file_info
                    self.copied[original_location] = data_path
                except OSError as ex:
                    logfunc(f'Could not copy {original_location} to {data_path} ' + str(ex))
            else:
                data_path = self.copied[original_location]
            pathlist.append(data_path)
            if return_on_first_hit:
                self.searched[filepattern] = pathlist
                return data_path
        self.searched[filepattern] = pathlist
        return pathlist


class FileSeekerTar(FileSeekerBase):
    """
    This is a class that extends FileSeekerBase to facilitate searching and extracting files
    from a tar archive. It supports both gzip and regular tar files.
    Attributes:
        tar_file_path (str): The path to the tar file.
        data_folder (str): The directory where extracted files will be stored.
        is_gzip (bool): Indicates if the tar file is gzipped.
        tar_file (tarfile.TarFile): The opened tar file object.
        searched (dict): A dictionary to keep track of searched file patterns and their results.
        copied (dict): A dictionary to keep track of files that have been copied.
        file_infos (dict): A dictionary to store file information for extracted files.
    Methods:
        __init__(tar_file_path, data_folder):
            Initializes the FileSeekerTar instance with the specified tar file path and data folder.
        search(filepattern, return_on_first_hit=False, force=False):
            Searches for files matching the given pattern in the tar archive and extracts them to the data folder.
            Returns a list of paths to the extracted files or the first hit if specified.
        cleanup():
            Closes the tar file to free up resources.
    """

    def __init__(self, tar_file_path, data_folder):
        FileSeekerBase.__init__(self)
        self.is_gzip = tar_file_path.lower().endswith('gz')
        mode = 'r:gz' if self.is_gzip else 'r'
        self.tar_file = tarfile.open(tar_file_path, mode)
        self.data_folder = data_folder
        self.searched = {}
        self.copied = {}
        self.file_infos = {}

    def search(self, filepattern, return_on_first_hit=False, force=False):
        if filepattern in self.searched and not force:
            pathlist = self.searched[filepattern]
            return self.searched[filepattern][0] if return_on_first_hit and pathlist else pathlist
        pathlist = []
        pat = _compile_pattern(normcase(filepattern))
        root = normcase("root/")
        for member in self.tar_file.getmembers():
            if pat(root + normcase(member.name)) is not None:
                clean_name = sanitize_file_path(member.name)
                full_path = os.path.join(self.data_folder, Path(clean_name))
                if member.name not in self.copied or force:
                    try:
                        if member.isdir():
                            os.makedirs(full_path, exist_ok=True)
                        else:
                            parent_dir = os.path.dirname(full_path)
                            if not os.path.exists(parent_dir):
                                os.makedirs(parent_dir)
                            with open(full_path, "wb") as fout:
                                fout.write(tarfile.ExFileObject(self.tar_file, member).read())
                                fout.close()
                                file_info = FileInfo(member.name, 0, member.mtime)
                                self.file_infos[full_path] = file_info
                                self.copied[member.name] = full_path
                            os.utime(full_path, (member.mtime, member.mtime))
                    except OSError as ex:
                        logfunc(f'Could not write file to filesystem, path was {member.name} ' + str(ex))
                else:
                    full_path = self.copied[member.name]
                pathlist.append(full_path)
                if return_on_first_hit:
                    self.searched[filepattern] = pathlist
                    return full_path
        self.searched[filepattern] = pathlist
        return pathlist

    def cleanup(self):
        self.tar_file.close()


class FileSeekerZip(FileSeekerBase):
    """
    This is a class that extends FileSeekerBase to facilitate searching and extracting files from a ZIP archive.
    Attributes:
        zip_file (ZipFile): The ZIP file object representing the archive.
        name_list (list): A list of file names contained in the ZIP archive.
        data_folder (str): The directory where extracted files will be stored.
        searched (dict): A dictionary to keep track of searched file patterns and their corresponding paths.
        copied (dict): A dictionary to keep track of files that have been extracted and their paths.
        file_infos (dict): A dictionary to store file information such as creation and modification dates.
    Methods:
        __init__(zip_file_path, data_folder):
            Initializes the FileSeekerZip instance with the specified ZIP file path and data folder.
        decode_extended_timestamp(extra_data):
            Decodes the extended timestamp information from the extra data of a file in the ZIP archive.
        search(filepattern, return_on_first_hit=False, force=False):
            Searches for files matching the specified pattern in the ZIP archive and extracts them if found.
        cleanup():
            Closes the ZIP file to free up resources.
    """

    def __init__(self, zip_file_path, data_folder):
        FileSeekerBase.__init__(self)
        self.zip_file = ZipFile(zip_file_path)
        self.name_list = self.zip_file.namelist()
        self.data_folder = data_folder
        self.searched = {}
        self.copied = {}
        self.file_infos = {}

    def decode_extended_timestamp(self, extra_data):
        """
        Decode extended timestamps from the provided extra data.
        Parameters:
            extra_data (bytes): The byte sequence containing the extended timestamp
                                information.
        Returns:
            tuple: A tuple containing the creation time and modification time as
                   integers. If the timestamps are not found, returns (None, None).
        """

        offset = 0
        length = len(extra_data)

        while offset < length:
            header_id, data_size = struct.unpack_from('<HH', extra_data, offset)
            offset += 4
            if header_id == 0x5455:
                creation_time = modification_time = None
                flags = struct.unpack_from('B', extra_data, offset)[0]
                offset += 1
                if flags & 1:  # Modification time
                    modification_time, = struct.unpack_from('<I', extra_data, offset)
                    offset += 4
                if flags & 4:  # Creation time
                    creation_time, = struct.unpack_from('<I', extra_data, offset)
                    offset += 4
                return creation_time, modification_time
            else:
                offset += data_size
        return None, None

    def search(self, filepattern, return_on_first_hit=False, force=False):
        if filepattern in self.searched and not force:
            pathlist = self.searched[filepattern]
            return self.searched[filepattern][0] if return_on_first_hit and pathlist else pathlist
        pathlist = []
        pat = _compile_pattern(normcase(filepattern))
        root = normcase("root/")
        for member in self.name_list:
            if member.startswith("__MACOSX"):
                continue
            if pat(root + normcase(member)) is not None:
                if member not in self.copied or force:
                    try:
                        # already replaces illegal chars with _ when exporting
                        extracted_path = self.zip_file.extract(member, path=self.data_folder)
                        f = self.zip_file.getinfo(member)
                        creation_date, modification_date = self.decode_extended_timestamp(f.extra)
                        file_info = FileInfo(member, creation_date, modification_date)
                        self.file_infos[extracted_path] = file_info
                        date_time = f.date_time
                        date_time = timex.mktime(date_time + (0, 0, -1))
                        os.utime(extracted_path, (date_time, date_time))
                        self.copied[member] = extracted_path
                    except OSError as ex:
                        logfunc(f'Could not write file to filesystem, path was {member} ' + str(ex))
                else:
                    extracted_path = self.copied[member]
                pathlist.append(extracted_path)
                if return_on_first_hit:
                    self.searched[filepattern] = pathlist
                    return extracted_path
        self.searched[filepattern] = pathlist
        return pathlist

    def cleanup(self):
        self.zip_file.close()


class FileSeekerFile(FileSeekerBase):
    """
    This is a class that extends FileSeekerBase to facilitate searching for and copying a specific file
    based on a provided filename pattern. It validates the input file path and manages the copying of the file to a
    designated data folder while keeping track of searched patterns and copied files.
    Attributes:
        single_file_abs_path (str): The absolute path of the single file to be sought.
        data_folder (str): The folder where the file will be copied.
        single_file_basename (str or None): The basename of the file if valid; otherwise None.
        searched (dict): A dictionary to store previously searched patterns and their results.
        copied (dict): A dictionary to track copied files and their destination paths.
        file_infos (dict): A dictionary to store file information objects for copied files.
    Methods:
        search(filepattern, return_on_first_hit=False, force=False):
            Searches for the file based on the provided filename pattern and copies it
            to the data folder if a match is found.
        cleanup():
            Placeholder method for cleanup operations (currently does nothing).
    """

    def __init__(self, file_path, data_folder):
        FileSeekerBase.__init__(self)
        self.single_file_abs_path = os.path.abspath(file_path)
        self.data_folder = data_folder

        if not os.path.isfile(self.single_file_abs_path):
            logfunc(f"Error: Input path '{file_path}' provided to FileSeekerFile is not a valid file.")
            self.single_file_basename = None
        else:
            self.single_file_basename = os.path.basename(self.single_file_abs_path)

        self.searched = {}
        self.copied = {}
        self.file_infos = {}

    def search(self, filepattern, return_on_first_hit=False, force=False):
        if not self.single_file_basename:
            return []

        if filepattern in self.searched and not force:
            return self.searched[filepattern]

        pattern_to_match_filename_against = None  # The specific filename pattern to use

        if '/' in filepattern or '\\' in filepattern:  # Original pattern contains path separators
            basename_of_pattern = os.path.basename(filepattern)

            # If the original pattern implied a path, we only proceed if its filename component
            # is NOT an overly generic wildcard.
            # Overly generic wildcards for a filename part of a path: '*', '**', '*.*'
            # These suggest matching 'any file' within that path, which isn't specific enough
            # for FileSeekerFile if the user provided one specific file.
            if basename_of_pattern not in ('*', '**', '*.*'):
                pattern_to_match_filename_against = basename_of_pattern
            else:
                # Log that this pattern is too generic for a single file context if it includes paths
                logfunc(f"FileSeekerFile: Artifact pattern '{filepattern}' contains path separators, AND its filename "
                        f"component ('{basename_of_pattern}') is too generic (e.g., '*', '**', '*.*'). "
                        f"FileSeekerFile will not match its single file ('{self.single_file_basename}') "
                        "against such a broad path-based pattern. No match.")
                self.searched[filepattern] = []
                return []
        else:  # Original pattern does not contain path separators (e.g., "*.json", "myfile.db")
            # This is a direct filename pattern.
            pattern_to_match_filename_against = filepattern

        # This safeguard should ideally not be hit if logic above is correct
        if not pattern_to_match_filename_against:
            # logfunc(f"FileSeekerFile: No effective filename pattern was derived from original '{filepattern}' to "
            #         f"match against basename '{self.single_file_basename}'. No match.")
            self.searched[filepattern] = []
            return []

        pat = _compile_pattern(normcase(pattern_to_match_filename_against))
        found_data_paths = []

        # logfunc("FileSeekerFile: Attempting to match effective filename pattern "
        #         f"'{pattern_to_match_filename_against}' (derived from artifact pattern "
        #         f"'{filepattern}') against actual file basename '{self.single_file_basename}'")

        if pat(normcase(self.single_file_basename)) is not None:
            # Match successful, proceed to copy
            dest_data_path = os.path.join(self.data_folder, self.single_file_basename)
            if is_platform_windows():
                dest_data_path = dest_data_path.replace('/', '\\')

            if self.single_file_abs_path not in self.copied or force:
                try:
                    os.makedirs(self.data_folder, exist_ok=True)
                    copyfile(self.single_file_abs_path, dest_data_path)
                    self.copied[self.single_file_abs_path] = dest_data_path
                    s = Path(self.single_file_abs_path).stat()
                    file_info_obj = FileInfo(self.single_file_abs_path, s.st_ctime, s.st_mtime)
                    self.file_infos[dest_data_path] = file_info_obj
                    found_data_paths.append(dest_data_path)
                    # logfunc(f"FileSeekerFile: Matched and copied. Dest: {dest_data_path}")
                except OSError as ex:
                    logfunc("FileSeekerFile: Could not copy file "
                            f"{self.single_file_abs_path} to {dest_data_path}: {str(ex)}")
            else:  # Already copied
                copied_dest_path = self.copied.get(self.single_file_abs_path)
                if copied_dest_path:
                    found_data_paths.append(copied_dest_path)
                    # logfunc(f"FileSeekerFile: Matched (already copied). Dest: {copied_dest_path}")
        else:
            logfunc("FileSeekerFile: No match for effective filename pattern "
                    f"'{pattern_to_match_filename_against}' against "
                    f"actual file basename '{self.single_file_basename}'")

        self.searched[filepattern] = found_data_paths
        return found_data_paths

    def cleanup(self):
        pass
