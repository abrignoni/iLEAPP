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
import atexit
import importlib
import fnmatch
import os
import tarfile
import hashlib
import stat
import struct
import zlib

from pathlib import Path
from shutil import copy2, copyfileobj
from zipfile import ZipFile, BadZipFile
from fnmatch import _compile_pattern
from functools import lru_cache

# Yes, this is hazmat, but we're only using it to unwrap existing keys
import cryptography.hazmat.primitives.keywrap as crypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7


from scripts.ilapfuncs import get_plist_file_content, get_plist_content, logfunc, \
    is_platform_windows, open_sqlite_db_readonly, sanitize_file_path
from scripts.filetype import guess_mime

normcase = lru_cache(maxsize=None)(os.path.normcase)

# A damaged or unsupported member of an otherwise readable zip (bad CRC-32,
# truncated deflate stream, unsupported compression or encryption).
_ZIP_MEMBER_ERRORS = (BadZipFile, zlib.error, RuntimeError, NotImplementedError)


def _remove_partial(path):
    try:
        if path and os.path.isfile(path):
            os.remove(path)
    except OSError:
        pass
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
    manifest_plist_path = os.path.join(directory, "Manifest.plist")
    manifest_db_path = os.path.join(directory, "Manifest.db")
    manifest_is_encrypted_key = get_plist_file_content(manifest_plist_path).get("IsEncrypted")
    if manifest_is_encrypted_key and guess_mime(manifest_db_path) != "application/x-sqlite3":
        return True
    return False


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
            tmp_backup_keybag_index:tmp_backup_keybag_index + 4], byteorder="big")
        tmp_backup_keybag_index += 4

        # Store the actual value itself
        tmp_value = backup_keybag[
            tmp_backup_keybag_index:tmp_backup_keybag_index + tmp_length]
        tmp_backup_keybag_index += tmp_length

        match tmp_string_type:
            case b'CLAS':
                tmp_protection_class['CLAS'] = int.from_bytes(tmp_value, byteorder="big")
            case b'DPIC':
                tmp_double_protection_iter = int.from_bytes(tmp_value, byteorder="big")
            case b'DPSL':
                tmp_double_protection_salt = tmp_value
            case b'ITER':
                tmp_iter = int.from_bytes(tmp_value, byteorder="big")
            case b'KTYP':
                tmp_protection_class['KTYP'] = int.from_bytes(tmp_value, byteorder="big")
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


def _without_cbc_padding(decrypted_contents):
    """Return decrypted contents without their PKCS#7 padding, or None when it is not valid."""
    unpadder = PKCS7(algorithms.AES.block_size).unpadder()
    try:
        return unpadder.update(decrypted_contents) + unpadder.finalize()
    except ValueError:
        return None


def _backup_file_plaintext(decrypted_contents, manifest_size, relative_path):
    """Return a decrypted backup file without its CBC padding.

    The length comes from the PKCS#7 padding the file was stored with, not from
    the Size in its Manifest.db record. The two disagree for SQLite databases
    in both directions, and the stored copy is the one whose header page count
    matches its own length; cutting it to Size drops pages or leaves the
    padding block on the end. Size is only used when the padding is not valid.
    """
    plaintext = _without_cbc_padding(decrypted_contents)
    if plaintext is None:
        logfunc(f'No valid padding at the end of {relative_path}, '
                f'writing the {manifest_size} bytes its Manifest.db record gives')
        return decrypted_contents[0:manifest_size]
    return plaintext


def _probe_volume_case_insensitive(folder):
    """True when this folder's volume folds case.

    os.path.normcase reports the platform convention, not the volume.
    Probe by creating Aa then exclusively creating aA.
    """
    try:
        os.makedirs(folder, exist_ok=True)
    except OSError:
        return os.path.normcase("Aa") == os.path.normcase("aA")
    probe_a = os.path.join(folder, ".leapp_case_probe_Aa")
    probe_b = os.path.join(folder, ".leapp_case_probe_aA")
    for leftover in (probe_a, probe_b):
        try:
            os.remove(leftover)
        except OSError:
            pass
    wrote_a = False
    wrote_b = False
    try:
        fd = os.open(probe_a, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, b"Aa")
        os.close(fd)
        wrote_a = True
        try:
            fd = os.open(probe_b, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, b"aA")
            os.close(fd)
            wrote_b = True
            return False
        except FileExistsError:
            return True
        except OSError:
            return os.path.normcase("Aa") == os.path.normcase("aA")
    except OSError:
        return os.path.normcase("Aa") == os.path.normcase("aA")
    finally:
        if wrote_a:
            try:
                os.remove(probe_a)
            except OSError:
                pass
        if wrote_b:
            try:
                os.remove(probe_b)
            except OSError:
                pass


def _dest_claim_key(data_path, folds_case):
    normalized = os.path.normpath(data_path)
    return normalized.casefold() if folds_case else normalized


def _case_variant_digest(hash_source):
    """Hex tag for a case-variant copy, derived from the source path.

    Hash the evidence-relative spelling, case preserved, separators normalized,
    so the same source maps to the same tag on every search, every run and
    every machine, and each case variant gets its own tag.
    """
    normalized = str(hash_source).replace('\\', '/').lstrip('/')
    return hashlib.sha256(normalized.encode('utf-8', 'surrogatepass')).hexdigest()


def _case_variant_candidates(root, ext, digest):
    """Candidate alternate names: short tag, full digest, then a counter tail.

    The later tiers only matter when a candidate name is already taken, for
    example by an evidence file that legitimately carries the tagged name. The
    walk over them stays finite because every blocker is a recorded claim or an
    existing file, and both sets are finite.
    """
    yield f"{root}~case-{digest[:8]}{ext}"
    yield f"{root}~case-{digest}{ext}"
    n = 2
    while True:
        yield f"{root}~case-{digest}-{n}{ext}"
        n += 1


def _disambiguated_data_path(data_path, source_key, dest_claims, folds_case,
                             hash_source=None):
    """Pick a dest that does not overwrite a different source.

    When the wanted destination is already claimed by a different source (two
    evidence paths differing only in case fold together on a case-insensitive
    report volume), the copy is written to name~case-<tag>.ext instead. The tag
    names the source rather than the arrival order, so re-searches and repeat
    runs land on the same path with nothing to remember.
    """
    key = _dest_claim_key(data_path, folds_case)
    claimed = dest_claims.get(key)
    if claimed is not None:
        claimed_source, claimed_path = claimed
        if claimed_source == source_key:
            return claimed_path
    elif not os.path.lexists(data_path):
        dest_claims[key] = (source_key, data_path)
        return data_path
    root, ext = os.path.splitext(data_path)
    digest = _case_variant_digest(source_key if hash_source is None else hash_source)
    for alt in _case_variant_candidates(root, ext, digest):
        alt_key = _dest_claim_key(alt, folds_case)
        claimed = dest_claims.get(alt_key)
        if claimed is not None:
            if claimed[0] == source_key:
                return claimed[1]
            continue
        if os.path.lexists(alt):
            continue
        dest_claims[alt_key] = (source_key, alt)
        logfunc(
            f"INFO: destination {data_path} already holds a different source; "
            f"writing {source_key} to {alt}"
        )
        return alt


# _member_content's answer for a link whose target the archive does not hold
_NOT_IN_ARCHIVE = object()


class FileInfo:
    """
    A class to store file metadata information.
    Attributes:
        source_path (str): Where the file sits in the evidence: an archive
            member name as stored, a path relative to the input directory, a
            volume path inside a raw image, or the file name for a single-file
            input. Never a path on the examiner's machine.
        creation_date (datetime): The date and time when the file was created.
        modification_date (datetime): The date and time when the file was last modified.
        kind (str): What the evidence holds at source_path, as the seeker that
            staged it knows: "file", or "link", "folder", "stream", "directory
            index", "deleted", "free space", "link outside the input", "decrypted
            file" (an encrypted iTunes backup's file, staged as plaintext). Only some
            kinds are hashed (HASHED_KINDS): a link's or a folder's staged bytes are
            not what the evidence holds there.
        sha256 (str or None): The SHA-256 of the staged copy, set when staged files
            are hashed (--hash) and the kind is one that is.
    """

    def __init__(self, source_path, creation_date, modification_date, kind='file'):
        self.source_path = source_path
        self.creation_date = creation_date
        self.modification_date = modification_date
        self.kind = kind
        self.sha256 = None


# The kinds whose staged copy holds the bytes the evidence holds under that name, so
# its digest says something about the evidence. A link's copy holds its target's
# bytes or its target's name, and a folder has none.
HASHED_KINDS = frozenset(('file', 'stream', 'directory index', 'deleted', 'free space',
                          'decrypted file'))


class FileSeekerBase:
    """
    Abstract base class for file seeking operations.
    This class provides an interface for searching files and performing cleanup operations
    in different storage contexts (e.g., filesystem, archives, databases).
    """
    def search(self, filepattern, return_on_first_hit=False):
        '''Returns a list of paths for files/folders that matched'''
        raise NotImplementedError

    def __init__(self):
        # Refined by _init_dest_guard once the subclass knows its data folder;
        # the defaults leave the dest-guard a pass-through.
        self._dest_claims = {}
        self._data_folder_folds_case = False

    def cleanup(self):
        '''close any open handles'''

    def _init_dest_guard(self, data_folder):
        self._dest_claims = {}
        self._data_folder_folds_case = _probe_volume_case_insensitive(data_folder)

    def _unique_data_path(self, data_path, source_key, hash_source=None):
        return _disambiguated_data_path(
            data_path, source_key, self._dest_claims,
            self._data_folder_folds_case, hash_source=hash_source
        )


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
    A symbolic link is followed only when its target, with every link on the way
    resolved, is inside directory. A link to anywhere else (an absolute link such as
    etc/localtime, or a relative one that climbs out) resolves on the examiner's own
    machine, so nothing is staged for it: it is logged, its path is returned with no
    file behind it, and file_infos holds the link's own times, so an artifact can
    still report the link.
    """

    def __init__(self, directory, data_folder):
        FileSeekerBase.__init__(self)
        self.directory = directory
        self._real_directory = os.path.normcase(os.path.realpath(directory))
        self._links_outside = {}
        self._all_files = []
        self.data_folder = data_folder
        logfunc('Building files listing...')
        self.build_files_list(directory)
        logfunc(f'File listing complete - {len(self._all_files)} files')
        self.searched = {}
        self.copied = {}
        self.file_infos = {}
        self._init_dest_guard(self.data_folder)

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

    def _leaves_input(self, item):
        '''True when item is a symbolic link whose target, with every link on the
        way resolved, is not inside the input folder.'''
        if not os.path.islink(item):
            return False
        target = os.path.normcase(os.path.realpath(item))
        try:
            return os.path.commonpath([self._real_directory, target]) != self._real_directory
        except ValueError:
            # A target on another drive (Windows).
            return True

    def _outside_link_path(self, item, data_path, source_path):
        '''The data path returned for a link that resolves outside the input folder.
        Nothing is written there. The first time, the link is logged and file_infos
        records the link's own times.'''
        if item not in self._links_outside:
            data_path = self._unique_data_path(data_path, item, hash_source=source_path)
            try:
                link_text = os.readlink(item)
                link_stat = os.lstat(item)
            except OSError:
                link_text = '(unreadable)'
            else:
                self.file_infos[data_path] = FileInfo(source_path, link_stat.st_ctime,
                                                      link_stat.st_mtime,
                                                      kind='link outside the input')
            logfunc(f"INFO: Link '{source_path}' points to '{link_text}', which resolves "
                    "outside the input folder. Its target was not staged.")
            self._links_outside[item] = data_path
        return self._links_outside[item]

    def search(self, filepattern, return_on_first_hit=False, force=False):
        if filepattern in self.searched and not force:
            pathlist = self.searched[filepattern]
            return self.searched[filepattern][0] if return_on_first_hit and pathlist else pathlist
        pathlist = []
        pat = _compile_pattern(normcase(filepattern))
        root = normcase("root/")
        for item in self._all_files:
            if pat(root + normcase(item)) is not None:
                # Relative to the input root, so the staged tree and the recorded
                # source path do not depend on where the extraction sits on the
                # examiner's machine, on a trailing separator in the input path or
                # on the \\?\ prefix the entry points add on Windows. The former
                # prefix slice dropped the first character of every staged path
                # after a trailing separator, and every dot when the input was '.'.
                item_rel_path = os.path.relpath(item, self.directory)
                source_path = item_rel_path.replace('\\', '/')
                data_path = os.path.join(self.data_folder, item_rel_path)
                if self._leaves_input(item):
                    data_path = self._outside_link_path(item, data_path, source_path)
                elif item not in self.copied or force:
                    try:
                        if os.path.isdir(item):
                            pass
                        elif os.path.isfile(item):
                            data_path = self._unique_data_path(
                                data_path, item, hash_source=source_path)
                            os.makedirs(os.path.dirname(data_path), exist_ok=True)
                            copy2(item, data_path)
                            self.copied[item] = data_path
                            creation_date = Path(item).stat().st_ctime
                            modification_date = Path(item).stat().st_mtime
                            # a link inside the input is copied as its target, as a tar
                            # or zip link now is; its kind says it was a link
                            file_info = FileInfo(source_path, creation_date, modification_date,
                                                 kind='link' if os.path.islink(item) else 'file')
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
                    # Manifest.db is stored padded like the files it lists
                    unpadded_manifest_contents = _without_cbc_padding(decrypted_manifest_contents)
                    if unpadded_manifest_contents is None:
                        logfunc('No valid padding at the end of Manifest.db, writing it as decrypted')
                        unpadded_manifest_contents = decrypted_manifest_contents
                    with open(manifest_path, "wb") as new_manifest_contents:
                        new_manifest_contents.write(unpadded_manifest_contents)

            self.build_files_list_from_manifest_db(manifest_path)
        elif backup_type == "mbdb":
            manifest_path = os.path.join(directory, "Manifest.mbdb")
            self.build_files_list_from_manifest_mbdb(manifest_path)
        logfunc(f'File listing complete - {len(self._all_files)} files')
        self.searched = {}
        self.copied = {}
        self.file_infos = {}
        self._init_dest_guard(self.data_folder)

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
                    data_path = self._unique_data_path(
                        data_path, original_location, hash_source=relative_path)
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

                            # Write the decrypt into the expected located, without its padding
                            with open(data_path, "wb") as temp_new_file:
                                temp_new_file.write(_backup_file_plaintext(
                                    decrypted_contents, tmp_file_meta['Size'], relative_path))

                    # If not encrypted, just copy the thing
                    else:
                        copy2(original_location, data_path)

                    source_path = relative_path.replace('\\', '/')
                    # an encrypted backup's file is staged as its plaintext, which is
                    # not the bytes the backup holds; its kind says so
                    file_info = FileInfo(source_path, creation_date, modification_date,
                                         kind='decrypted file' if self.decryption_keys
                                         else 'file')
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


def _compressed_tar_streams():
    """The reader classes tarfile wraps a compressed tar in, for the codecs this Python has."""
    streams = []
    for module, name in (('gzip', 'GzipFile'), ('bz2', 'BZ2File'), ('lzma', 'LZMAFile'),
                         ('compression.zstd', 'ZstdFile')):
        try:
            streams.append(getattr(importlib.import_module(module), name))
        except (ImportError, AttributeError):
            pass
    return tuple(streams)


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

    A tar can store one member name more than once (an appended archive does).
    A search matches each name once. Entries holding the same bytes are staged
    once, from the last entry, which is the one tar itself extracts. When the
    entries differ, the entry recording the latest modification time is staged
    under the name (the earlier entry on a tie), and every other version is
    staged beside it as <name>~tar-entry-<N><ext>, N being the entry's position
    in the archive, and logged. Those other versions are not returned to
    artifacts, so an artifact reads one version of each name.
    """

    def __init__(self, tar_file_path, data_folder):
        FileSeekerBase.__init__(self)
        self.is_gzip = tar_file_path.lower().endswith('gz')
        mode = 'r:gz' if self.is_gzip else 'r'
        self.tar_file = tarfile.open(tar_file_path, mode)
        self.data_folder = data_folder
        self._spool_path = None
        if isinstance(self.tar_file.fileobj, _compressed_tar_streams()):
            self._read_from_a_decompressed_copy(tar_file_path, mode)
        self.searched = {}
        self.copied = {}
        self.file_infos = {}
        self._init_dest_guard(self.data_folder)
        self._search_members, self._other_versions = self._index_member_names()

    def _read_from_a_decompressed_copy(self, tar_file_path, mode):
        """Decompress a compressed tar once and read the plain copy instead.

        A compressed stream can only seek backwards by decompressing again from its
        start. Each search reads its matches in archive order, but artifacts search one
        after another, so reading a compressed tar in place rewinds over and over. On a
        5.36 GB Android extraction that was 56 rewinds and 220 GB decompressed as a
        .tar.gz (347 s against 33 s for the plain tar), and about two hours projected
        as a .tar.xz. The copy sits in the report folder and is deleted by cleanup(),
        or at exit if a run never reaches it. When it cannot be written, the archive is
        read in place as before.
        """
        spool = os.path.join(os.path.dirname(os.path.normpath(self.data_folder)), '_decompressed_input.tar')
        logfunc(f'Decompressing {os.path.basename(tar_file_path)} once so its files can be read in any order')
        started = timex.time()
        written = False
        try:
            self.tar_file.fileobj.seek(0)
            with open(spool, 'wb') as out:
                copyfileobj(self.tar_file.fileobj, out, 16 << 20)
            written = True
        except OSError as ex:
            logfunc(f'Could not write the decompressed copy ({ex.strerror or type(ex).__name__}); '
                    'reading the compressed archive in place, which is much slower')
        finally:
            if not written and os.path.exists(spool):
                os.remove(spool)
        self.tar_file.close()
        if not written:
            self.tar_file = tarfile.open(tar_file_path, mode)
            return
        self._spool_path = spool
        atexit.register(self._discard_spool)
        self.tar_file = tarfile.open(spool, 'r:')
        logfunc(f'Decompressed {os.path.getsize(spool):,} bytes in {timex.time() - started:.0f} s')

    def _index_member_names(self):
        """One member per distinct name, in archive order, and the other versions of any name stored twice."""
        by_name = {}
        for index, member in enumerate(self.tar_file.getmembers()):
            by_name.setdefault(member.name, []).append((index, member))
        search_members = []
        other_versions = {}
        repeated = differing = 0
        for name, entries in by_name.items():
            if len(entries) < 2:
                search_members.append(entries[0][1])
                continue
            repeated += 1
            contents = [self._member_content_key(member) for _, member in entries]
            if len(set(contents)) == 1:
                search_members.append(entries[-1][1])
                continue
            differing += 1
            # Latest recorded time wins; on a tie the earlier entry does.
            pick = max(((member.mtime, -position), position)
                       for position, (_, member) in enumerate(entries))[1]
            search_members.append(entries[pick][1])
            seen = {contents[pick]}
            for position, (index, member) in enumerate(entries):
                if position != pick and contents[position] not in seen:
                    seen.add(contents[position])
                    other_versions.setdefault(name, []).append((index, member))
        if repeated:
            versions = sum(len(v) for v in other_versions.values())
            logfunc(f'INFO: {repeated} member name(s) are stored more than once in this archive. '
                    f'{repeated - differing} repeat the same content and are staged once. '
                    f'{differing} hold different content: the entry recording the latest '
                    f'modification time is staged under the name, and {versions} other version(s) '
                    f'are staged beside it as <name>~tar-entry-<N><ext>, N being the entry\'s '
                    f'position in the archive. Artifacts read the version under the name.')
        return search_members, other_versions

    def _member_content(self, member):
        """A file object over what the member holds, None for a folder or a link to
        one, or _NOT_IN_ARCHIVE for a link whose target the archive does not hold.

        A hard link stores no data of its own and a symbolic link only its target's
        name, so both are read as the member they point to, as the folder seeker
        reads a link that stays inside the input. Read as themselves they staged as
        empty files, and a link to a folder staged that way blocked every file under
        its name: in an Android full file system tar, data/user/0 is a hard link to
        data/data. A link whose target the archive does not hold is handed back by
        search with nothing staged, as the folder seeker hands back a link that
        resolves outside the input, so an artifact can still report the link."""
        if member.isdir():
            return None
        if member.islnk() or member.issym():
            try:
                return self.tar_file.extractfile(member)
            except KeyError:
                logfunc(f"INFO: Link '{member.name}' points to '{member.linkname}', which "
                        "is not in the archive. Its target was not staged.")
                return _NOT_IN_ARCHIVE
        return tarfile.ExFileObject(self.tar_file, member)

    def _member_content_key(self, member):
        """What a member holds: the digest of a regular file's bytes, else its type and link target."""
        if not member.isreg():
            return (member.type, member.linkname, member.size)
        digest = hashlib.sha256()
        with tarfile.ExFileObject(self.tar_file, member) as fin:
            for chunk in iter(lambda: fin.read(1 << 20), b''):
                digest.update(chunk)
        return (member.size, digest.hexdigest())

    def search(self, filepattern, return_on_first_hit=False, force=False):
        if filepattern in self.searched and not force:
            pathlist = self.searched[filepattern]
            return self.searched[filepattern][0] if return_on_first_hit and pathlist else pathlist
        pathlist = []
        pat = _compile_pattern(normcase(filepattern))
        root = normcase("root/")
        for member in self._search_members:
            if pat(root + normcase(member.name)) is not None:
                clean_name = sanitize_file_path(member.name)
                full_path = os.path.join(self.data_folder, Path(clean_name))
                if member.name not in self.copied or force:
                    try:
                        content = self._member_content(member)
                        if content is _NOT_IN_ARCHIVE:
                            # nothing is written; the path is returned, as the folder
                            # seeker returns a link that resolves outside the input
                            full_path = self._unique_data_path(str(full_path), member.name)
                            self.file_infos[full_path] = FileInfo(
                                member.name, 0, member.mtime, kind='link outside the input')
                            self.copied[member.name] = full_path
                        elif content is None:
                            # a folder, or a link to one: no file to hand over
                            os.makedirs(full_path, exist_ok=True)
                        else:
                            full_path = self._unique_data_path(str(full_path), member.name)
                            parent_dir = os.path.dirname(full_path)
                            if not os.path.exists(parent_dir):
                                os.makedirs(parent_dir)
                            with content, open(full_path, "wb") as fout:
                                copyfileobj(content, fout, 1 << 20)
                            file_info = FileInfo(member.name, 0, member.mtime,
                                                 kind='link' if member.issym() or member.islnk()
                                                 else 'file')
                            self.file_infos[full_path] = file_info
                            self.copied[member.name] = full_path
                            os.utime(full_path, (member.mtime, member.mtime))
                            self._stage_other_versions(member.name)
                    except OSError as ex:
                        logfunc(f'Could not write file to filesystem, path was {member.name} ' + str(ex))
                        if member.name not in self.copied:
                            continue  # nothing was written, so there is no file to hand back
                else:
                    full_path = self.copied[member.name]
                pathlist.append(full_path)
                if return_on_first_hit:
                    self.searched[filepattern] = pathlist
                    return full_path
        self.searched[filepattern] = pathlist
        return pathlist

    def _stage_other_versions(self, name):
        """Stage each other version of a name whose entries hold different content."""
        for index, member in self._other_versions.get(name, ()):
            base, ext = os.path.splitext(os.path.join(self.data_folder, Path(sanitize_file_path(name))))
            dest_path = self._unique_data_path(
                f'{base}~tar-entry-{index}{ext}', (name, index),
                hash_source=f'{name}~tar-entry-{index}')
            try:
                parent = os.path.dirname(dest_path)
                if parent:
                    os.makedirs(parent, exist_ok=True)
                with tarfile.ExFileObject(self.tar_file, member) as fin, open(dest_path, 'wb') as fout:
                    copyfileobj(fin, fout)
                os.utime(dest_path, (member.mtime, member.mtime))
                logfunc(f'INFO: {name} is stored more than once with different content; '
                        f'entry {index} ({member.size} bytes) staged as {dest_path}')
            except OSError as ex:
                logfunc(f'Could not write file to filesystem, path was {name} (entry {index}) ' + str(ex))

    def cleanup(self):
        self.tar_file.close()
        if self._spool_path:
            atexit.unregister(self._discard_spool)
            self._discard_spool()

    def _discard_spool(self):
        """Close the archive and delete the decompressed copy made for it."""
        self.tar_file.close()
        if self._spool_path and os.path.exists(self._spool_path):
            os.remove(self._spool_path)
        self._spool_path = None


# A zip member's DOS date and time records no time zone (APPNOTE.TXT 6.3.10,
# 4.4.6). Two extra fields record the times in UTC:
#
# - NTFS (0x000a), APPNOTE.TXT 6.3.10 section 4.5.5: four reserved bytes, then
#   attributes, each a tag, a size and data. Tag 0x0001 holds Mtime, Atime and
#   Ctime (file creation time), 8 bytes each, which Info-ZIP extrafld.txt calls
#   64-bit NTFS file times: 100-nanosecond intervals since 1601-01-01 UTC.
# - Extended timestamp (0x5455), Info-ZIP extrafld.txt: a flags byte, then the
#   times it flags as Unix seconds, UTC. The central directory copy, which is the
#   one zipfile reads into ZipInfo.extra, need hold only the modification time,
#   and its flags still describe the local header copy.
#
# The NTFS field is preferred, then the extended timestamp, then the DOS date and
# time. A field that is malformed is logged and skipped, never fatal.
_NTFS_EXTRA_ID = 0x000a
_NTFS_TIMES_TAG = 0x0001
_EXTENDED_TIMESTAMP_ID = 0x5455
_FILETIME_AT_UNIX_EPOCH = 116444736000000000
_LATEST_UNIX_SECONDS = 253402300799  # 9999-12-31 23:59:59 UTC, the last whole second datetime holds


def _filetime_to_unix(value):
    """Unix seconds for an NTFS file time; None for 0, which records no time."""
    if value == 0:
        return None
    seconds = (value - _FILETIME_AT_UNIX_EPOCH) / 10_000_000
    if seconds > _LATEST_UNIX_SECONDS:
        raise ValueError(f'file time {value} is after the year 9999')
    return seconds


def _zip_extra_blocks(extra):
    """Each (header id, data) in a zip extra field, and a problem for a cut block."""
    blocks, offset = [], 0
    while offset + 4 <= len(extra):
        header_id, size = struct.unpack_from('<HH', extra, offset)
        data = extra[offset + 4:offset + 4 + size]
        if len(data) < size:
            return blocks, (f'extra field block 0x{header_id:04x} declares {size} bytes '
                            f'and {len(data)} remain')
        blocks.append((header_id, data))
        offset += 4 + size
    return blocks, None


def _ntfs_extra_times(data):
    """(creation, modification) Unix seconds from an NTFS (0x000a) block's data.

    Returns None when the block holds no times attribute. Raises ValueError when
    the block or its times attribute is shorter than its layout needs, or a time
    is out of range.
    """
    if len(data) < 4:
        raise ValueError(f'{len(data)} bytes, fewer than its 4 reserved bytes')
    offset = 4
    while offset + 4 <= len(data):
        tag, size = struct.unpack_from('<HH', data, offset)
        if offset + 4 + size > len(data):
            raise ValueError(f'attribute 0x{tag:04x} declares {size} bytes and '
                             f'{len(data) - offset - 4} remain')
        if tag == _NTFS_TIMES_TAG:
            if size < 24:
                raise ValueError(f'times attribute holds {size} bytes, not 24')
            modified, _accessed, created = struct.unpack_from('<QQQ', data, offset + 4)
            return _filetime_to_unix(created), _filetime_to_unix(modified)
        offset += 4 + size
    return None


def _extended_timestamp_times(data, problems):
    """(creation, modification) from an extended timestamp (0x5455) block's data.

    The times follow the flags byte in flag bit order (Info-ZIP extrafld.txt):
    bit 0 modification, bit 1 access, bit 2 creation, 4 bytes each. Some writers
    put all of them in the central directory copy and some set bit 3 and add a
    fourth value, which is not read. Every read is bounded by the block's
    declared size: a value the block is too short to hold is None. The same
    bit-order reading is in Alexis Brignoni, 'Full file system extractions in
    zip: MAC times', 2024-05-24,
    https://abrignoni.blogspot.com/2024/05/full-file-system-extractions-in-zip-mac.html
    """
    if not data:
        problems.append('extended timestamp field (0x5455) not read: it holds no flags byte')
        return None
    flags, offset = data[0], 1
    modified = created = None
    if flags & 1:
        if len(data) < offset + 4:
            problems.append(f'extended timestamp field (0x5455) not read: flags 0x{flags:02x} '
                            f'name a modification time and it holds {len(data)} bytes')
            return None
        modified, = struct.unpack_from('<I', data, offset)
        offset += 4
    if flags & 2:
        offset += 4  # access time, not recorded
    if flags & 4 and len(data) >= offset + 4:
        created, = struct.unpack_from('<I', data, offset)
    return created, modified


def zip_member_times(info):
    """The times FileSeekerZip records for a zip member, and what it could not read.

    Returns (creation, modification, staged, problems). creation and modification
    are the FileInfo times: Unix seconds, UTC, from the NTFS field, else from the
    extended timestamp field, else None. staged is the modification time given to
    the staged copy: the modification time above when it is nonzero, else the DOS
    date and time read as local time. problems describes each field not read.
    """
    blocks, cut = _zip_extra_blocks(info.extra or b'')
    problems = [cut] if cut else []
    ntfs = unix = None
    for header_id, data in blocks:
        if header_id == _NTFS_EXTRA_ID and ntfs is None:
            try:
                ntfs = _ntfs_extra_times(data)
            except ValueError as ex:
                problems.append(f'NTFS extra field (0x000a) not read: {ex}')
        elif header_id == _EXTENDED_TIMESTAMP_ID and unix is None:
            unix = _extended_timestamp_times(data, problems)
    created = modified = None
    for times in (ntfs, unix):
        if times:
            if created is None:
                created = times[0]
            if modified is None:
                modified = times[1]
    staged = modified if modified else timex.mktime(info.date_time + (0, 0, -1))
    return created, modified, staged, problems


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
        search(filepattern, return_on_first_hit=False, force=False):
            Searches for files matching the specified pattern in the ZIP archive and extracts them if found.
        cleanup():
            Closes the ZIP file to free up resources.

    A zip can store one member name more than once. A search matches each name
    once. Entries repeating the same content (same CRC-32 and size) are staged
    once, from the entry ZipFile resolves the name to. When the entries hold
    different content, the entry recording the latest modification time is
    staged under the name (the earlier entry on a tie), and every other
    version is staged beside it as <name>~zip-entry-<N><ext>, N being the
    entry's position in the archive, and logged. Those other versions are not
    returned to artifacts, so an artifact reads one version of each name.

    A staged file's times come from zip_member_times: the NTFS extra field, else
    the extended timestamp field, else (for the staged copy only) the DOS date and
    time. A malformed field is logged and skipped.
    """

    # How many members' unreadable time fields are logged one by one.
    _TIME_PROBLEMS_LOGGED = 20

    def __init__(self, zip_file_path, data_folder):
        FileSeekerBase.__init__(self)
        self.zip_file = ZipFile(zip_file_path)
        self.name_list = self.zip_file.namelist()
        self.data_folder = data_folder
        self.searched = {}
        self.copied = {}
        self.file_infos = {}
        self._init_dest_guard(self.data_folder)
        self._search_names, self._chosen, self._other_versions = self._index_member_names()
        self._time_problems = 0

    def _index_member_names(self):
        """Distinct member names, and how to stage a name stored more than once.

        Returns the distinct names in archive order, the entry to stage under
        each name whose copies differ, and the other versions of those names.

        ZipFile keys NameToInfo on the member name while it reads the central
        directory, so that dict is short by exactly the number of names stored more
        than once. Reading its length costs nothing and answers the only question
        the walk below exists to answer. Grouping every member to learn the same
        thing costs a dict entry, a list and a tuple per member: on a 630,560 member
        archive that measured 138 MB, spent to discover that no name repeats.
        NameToInfo is not part of zipfile's documented surface, so an absent one
        falls through to the walk rather than assuming anything.
        """
        by_member_name = getattr(self.zip_file, 'NameToInfo', None)
        if by_member_name is not None and len(self.name_list) == len(by_member_name):
            return list(self.name_list), {}, {}
        by_name = {}
        for index, info in enumerate(self.zip_file.infolist()):
            by_name.setdefault(info.filename, []).append((index, info))
        chosen = {}
        other_versions = {}
        repeated = 0
        for name, entries in by_name.items():
            if len(entries) < 2:
                continue
            repeated += 1
            if len({(info.CRC, info.file_size) for _, info in entries}) == 1:
                continue
            times = self._recorded_mtimes([info for _, info in entries])
            # Latest recorded time wins; on a tie the earlier entry does.
            pick = max(((stamp, -i), i) for i, stamp in enumerate(times))[1]
            chosen[name] = entries[pick][1]
            seen = {(entries[pick][1].CRC, entries[pick][1].file_size)}
            for index, info in entries[:pick] + entries[pick + 1:]:
                content = (info.CRC, info.file_size)
                if content not in seen:
                    seen.add(content)
                    other_versions.setdefault(name, []).append((index, info))
        if repeated:
            versions = sum(len(v) for v in other_versions.values())
            logfunc(f'INFO: {repeated} member name(s) are stored more than once in this archive. '
                    f'{repeated - len(chosen)} repeat the same content (CRC-32 and size) and are '
                    f'staged once. {len(chosen)} hold different content: the entry recording the '
                    f'latest modification time is staged under the name, and {versions} other '
                    f'version(s) are staged beside it as <name>~zip-entry-<N><ext>, N being the '
                    f'entry\'s position in the archive. Artifacts read the version under the name.')
        return list(by_name), chosen, other_versions

    @staticmethod
    def _recorded_mtimes(infos):
        """Modification times recorded for entries of one name, on one clock.

        Uses the NTFS times (0x000a) when every entry carries them, else the
        extended timestamp (0x5455), else the DOS date and time, so entries are
        only ever compared on the same clock.
        """
        def fields(info):
            found = {}
            extra, offset = info.extra, 0
            while offset + 4 <= len(extra):
                header_id, size = struct.unpack_from('<HH', extra, offset)
                body = extra[offset + 4:offset + 4 + size]
                if header_id == 0x5455 and len(body) >= 5 and body[0] & 1:
                    found['unix'] = float(struct.unpack_from('<I', body, 1)[0])
                elif header_id == 0x000a and len(body) >= 16:
                    tag, tag_size = struct.unpack_from('<HH', body, 4)
                    if tag == 1 and tag_size >= 8:
                        found['ntfs'] = struct.unpack_from('<Q', body, 8)[0]
                offset += 4 + size
            found['dos'] = info.date_time
            return found
        recorded = [fields(info) for info in infos]
        for clock in ('ntfs', 'unix', 'dos'):
            if all(clock in r for r in recorded):
                return [r[clock] for r in recorded]
        return [r['dos'] for r in recorded]

    def _member_times(self, member, info):
        """zip_member_times for one member, logging any field it could not read."""
        created, modified, staged, problems = zip_member_times(info)
        if problems:
            self._time_problems += 1
            if self._time_problems <= self._TIME_PROBLEMS_LOGGED:
                logfunc(f'INFO: {member}: {"; ".join(problems)}. Its times come from the '
                        f'next field that holds them, or the zip date and time.')
            if self._time_problems == self._TIME_PROBLEMS_LOGGED:
                logfunc('INFO: further members with time fields that could not be read '
                        'are not logged one by one.')
        return created, modified, staged

    @staticmethod
    def _set_staged_time(path, staged, info):
        """Give the staged copy its time, falling back to the DOS date and time."""
        try:
            os.utime(path, (staged, staged))
            return
        except (OverflowError, ValueError, OSError) as ex:
            dos = timex.mktime(info.date_time + (0, 0, -1))
            if staged == dos:
                raise
            logfunc(f'INFO: {path}: time {staged} could not be set ({ex}); '
                    f'the zip date and time is used.')
        os.utime(path, (dos, dos))

    def search(self, filepattern, return_on_first_hit=False, force=False):
        if filepattern in self.searched and not force:
            pathlist = self.searched[filepattern]
            return self.searched[filepattern][0] if return_on_first_hit and pathlist else pathlist
        pathlist = []
        pat = _compile_pattern(normcase(filepattern))
        root = normcase("root/")
        for member in self._search_names:
            if member.startswith("__MACOSX"):
                continue
            if pat(root + normcase(member)) is not None:
                if member not in self.copied or force:
                    source = self._chosen.get(member, member)
                    dest_path = None
                    try:
                        if member.endswith('/'):
                            # Case-variant directories fold into one on a
                            # case-insensitive volume; their files disambiguate
                            # individually, so directory members take no guard.
                            extracted_path = self._extract_member(member, source=source)
                        else:
                            intended = self._intended_extract_path(member)
                            dest_path = self._unique_data_path(intended, member)
                            extracted_path = self._extract_member(
                                member, dest_path=dest_path, source=source)
                        f = self.zip_file.getinfo(member) if source is member else source
                        creation_date, modification_date, staged = self._member_times(member, f)
                        # a zip keeps a symbolic link as a member holding its target's name
                        kind = ('folder' if member.endswith('/') else
                                'link' if stat.S_ISLNK(f.external_attr >> 16) else 'file')
                        file_info = FileInfo(member, creation_date, modification_date, kind)
                        self.file_infos[extracted_path] = file_info
                        self._set_staged_time(extracted_path, staged, f)
                        self.copied[member] = extracted_path
                    except OSError as ex:
                        logfunc(f'Could not write file to filesystem, path was {member} ' + str(ex))
                        continue
                    except _ZIP_MEMBER_ERRORS as ex:
                        # One corrupt member must not abort the whole run.
                        _remove_partial(dest_path)
                        logfunc(f'Could not extract corrupt zip member, skipped: {member} ({ex})')
                        continue
                    self._stage_other_versions(member)
                else:
                    extracted_path = self.copied[member]
                pathlist.append(extracted_path)
                if return_on_first_hit:
                    self.searched[filepattern] = pathlist
                    return extracted_path
        self.searched[filepattern] = pathlist
        return pathlist

    def _stage_other_versions(self, member):
        """Stage each other version of a name whose copies hold different content."""
        for index, info in self._other_versions.get(member, ()):
            base, ext = os.path.splitext(self._intended_extract_path(member))
            dest_path = self._unique_data_path(
                f'{base}~zip-entry-{index}{ext}', (member, index),
                hash_source=f'{member}~zip-entry-{index}')
            try:
                parent = os.path.dirname(dest_path)
                if parent:
                    os.makedirs(parent, exist_ok=True)
                with self.zip_file.open(info) as fin, open(dest_path, 'wb') as fout:
                    copyfileobj(fin, fout)
                self._set_staged_time(dest_path, self._member_times(member, info)[2], info)
                logfunc(f'INFO: {member} is stored more than once with different content; '
                        f'entry {index} ({info.file_size} bytes) staged as {dest_path}')
            except OSError as ex:
                logfunc(f'Could not write file to filesystem, path was {member} (entry {index}) ' + str(ex))
            except _ZIP_MEMBER_ERRORS as ex:
                _remove_partial(dest_path)
                logfunc(f'Could not extract corrupt zip member, skipped: {member} (entry {index}) ({ex})')

    def _intended_extract_path(self, member):
        clean_member = sanitize_file_path(member)
        parts = [part for part in clean_member.replace('\\', '/').split('/')
                 if part not in ('', '.', '..')]
        if not parts:
            return self.data_folder
        return os.path.join(self.data_folder, *parts)

    def _extract_member(self, member, dest_path=None, source=None):
        """Extract one member, sanitizing names ZipFile.extract() cannot write.

        ZipFile.extract() only replaces a fixed set of printable characters
        (:<>|"?*) and only on Windows; ASCII control characters in the stored
        name (present in real iOS extractions, e.g. chronod icon files) reach
        the OS untouched and Windows rejects them with EINVAL. Members whose
        names need sanitizing are written out manually to a cleaned path.

        dest_path, when given, is the already-disambiguated destination so a
        later case-variant member cannot overwrite an earlier one. source,
        when given, is the entry to read (a ZipInfo) for a name the archive
        stores more than once; otherwise the name resolves as ZipFile resolves it.
        """
        intended = self._intended_extract_path(member)
        if dest_path is None:
            dest_path = intended
        if source is None:
            source = member
        clean_member = sanitize_file_path(member)
        if dest_path == intended and clean_member == member:
            return self.zip_file.extract(source, path=self.data_folder)
        if member.endswith('/'):
            os.makedirs(dest_path, exist_ok=True)
        else:
            parent = os.path.dirname(dest_path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with self.zip_file.open(source) as fin, open(dest_path, 'wb') as fout:
                fout.write(fin.read())
        return dest_path

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
        self._init_dest_guard(self.data_folder)

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
                    dest_data_path = self._unique_data_path(
                        dest_data_path, self.single_file_abs_path,
                        hash_source=self.single_file_basename)
                    os.makedirs(
                        os.path.dirname(dest_data_path) or self.data_folder,
                        exist_ok=True,
                    )
                    copy2(self.single_file_abs_path, dest_data_path)
                    self.copied[self.single_file_abs_path] = dest_data_path
                    s = Path(self.single_file_abs_path).stat()
                    # The file name is all that places this input in the evidence;
                    # the directory it came from is the examiner's, not the device's.
                    file_info_obj = FileInfo(self.single_file_basename, s.st_ctime, s.st_mtime)
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
