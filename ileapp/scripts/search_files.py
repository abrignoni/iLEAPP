import time as timex
import fnmatch
import os
import tarfile
import hashlib
import struct


from pathlib import Path
from ileapp.scripts.ilapfuncs import *
from shutil import copyfile
from zipfile import ZipFile

from fnmatch import _compile_pattern
from functools import lru_cache

# Yes, this is hazmat, but we're only using it to unwrap existing keys
from cryptography.hazmat.primitives.keywrap import aes_key_unwrap
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from ileapp.scripts.builds_ids import get_root_path_from_domain
normcase = lru_cache(maxsize=None)(os.path.normcase)


def get_itunes_backup_type(directory):
    '''Returns the iTunes backup type'''
    if os.path.exists(os.path.join(directory, "Manifest.db")):
        return "db"
    if os.path.exists(os.path.join(directory, "Manifest.mbdb")):
        return "mbdb"
    return ""


def get_itunes_backup_encryption(directory):
    '''Returns True if the iTunes backup at directory is encrypted,
    False otherwise'''
    manifest_path = os.path.join(directory, "Manifest.plist")
    manifest = get_plist_file_content(manifest_path)
    return manifest.get("IsEncrypted")


def check_itunes_backup_status(directory, backup_type):
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
    tmp_protection_class = None
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
                    if tmp_protection_class is not None:
                        protection_classes[tmp_protection_class['CLAS']] = tmp_protection_class
                    tmp_protection_class = {}
            case b'SALT':
                tmp_salt = tmp_value
            case b'WPKY':
                tmp_protection_class['WPKY'] = tmp_value
            case b'WRAP':
                if tmp_protection_class is not None:
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
    for protection_class_key in protection_classes:
        protection_class = protection_classes[protection_class_key]
        try:
            protection_class['Unwrapped'] = aes_key_unwrap(
                unwrapped_key, protection_class['WPKY'])
        except:
            logfunc("Could not unwrap a protection class key, likely due to an incorrect passcode. Exiting.")
            return None, "Incorrect password"

    # Find the right one for the Manifest.db
    if manifest_key_class not in protection_classes:
        logfunc("Did not find the right protection class to decrypt Manifest.db. Exiting.")
        return None, "Could not find protection class for Manifest.db"

    manifest_protection_class = protection_classes[manifest_key_class]
    unwrapped_manifest_key = aes_key_unwrap(manifest_protection_class["Unwrapped"], manifest_wrapped_key)

    logfunc(f"Manifest.db was successfully decrypted with passcode {passcode}")
    return (protection_classes, unwrapped_manifest_key), "Decryption successful"


class FileInfo:
    def __init__(self, source_path, creation_date, modification_date):
        self.source_path = source_path
        self.creation_date = creation_date
        self.modification_date = modification_date

class FileSeekerBase:
    # This is an abstract base class
    def search(self, filepattern_to_search, return_on_first_hit=False):
        '''Returns a list of paths for files/folders that matched'''
        pass

    def cleanup(self):
        '''close any open handles'''
        pass

class FileSeekerDir(FileSeekerBase):
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
        except Exception as ex:
            logfunc(f'Error reading {directory} ' + str(ex))

    def search(self, filepattern, return_on_first_hit=False, force=False):
        if filepattern in self.searched and not force:
            pathlist = self.searched[filepattern]
            return self.searched[filepattern][0] if return_on_first_hit and pathlist else pathlist
        pathlist = []
        pat = _compile_pattern( normcase(filepattern) )
        root = normcase("root/")
        for item in self._all_files:
            if pat( root + normcase(item) ) is not None:
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
                            logfunc(f"INFO: Item '{item}' is neither a file nor a directory (e.g. symlink not followed, or broken). Skipped.")
                    except Exception as ex:
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
                    cipher = Cipher(algorithms.AES(unwrapped_manifest_key), modes.CBC(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'))
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
                root_path = get_root_path_from_domain(domain)
                relative_path = row[2]
                file_metadata = row[3]
                full_path = os.path.join(root_path, relative_path)
                self._all_files[full_path] = hash_filename
                if self.decryption_keys:
                    # Load the file's plist and find the encryption key
                    tmp_file_plist = plistlib.loads(row[3])
                    tmp_plist_root = tmp_file_plist["$top"]["root"]
                    tmp_key_position = tmp_file_plist["$objects"][tmp_plist_root]["EncryptionKey"]
                    tmp_wrapped_key = tmp_file_plist["$objects"][tmp_key_position]["NS.data"]

                    # Store the results into a dict for future
                    self._all_file_meta[full_path] = {}
                    self._all_file_meta[full_path]['Class'] = int.from_bytes(tmp_wrapped_key[0:4], byteorder="little")
                    self._all_file_meta[full_path]['Key'] = tmp_wrapped_key[4:]
                    self._all_file_meta[full_path]['Size'] = tmp_file_plist["$objects"][tmp_plist_root]["Size"]
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
                value = (value<<8) + data[offset]
                offset = offset + 1
                intsize = intsize - 1
            return value, offset
        
        def getstring(data, offset, bin=False):
            """Retrieve a string and new offset from the current offset into the data"""
            if chr(data[offset]) == chr(0xFF) and chr(data[offset+1]) == chr(0xFF):
                return '', offset+2 # Blank string
            length, offset = getint(data, offset, 2) # 2-byte length
            value = "" if bin else data[offset:offset+length].decode()
            return value, (offset + length)

        def process_mbdb_file(manifest_path):
            files = list()
            with open(manifest_path, 'rb') as f:
                data = f.read()
            if data[0:4].decode() != "mbdb": raise Exception("This does not look like an MBDB file")
            offset = 4
            offset = offset + 2 # value x05 x00, not sure what this is
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
                for ii in range(numprops):
                    _, offset = getstring(data, offset, True)
                    _, offset = getstring(data, offset, True)
                hash_filename = hashlib.sha1(f"{domain}-{filename}".encode()).hexdigest()
                files.append((hash_filename,domain,filename))
            return files

        try: 
            all_rows = process_mbdb_file(manifest_path)
            for row in all_rows:
                hash_filename = row[0]
                domain = row[1]
                root_path = get_root_path_from_domain(domain)
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
                            raise Exception
                        tmp_protection_class = protection_classes[tmp_file_meta['Class']]

                        # Grab the file's key
                        tmp_file_wrapped_key = tmp_file_meta['Key']
                        tmp_file_unwrapped_key = aes_key_unwrap(tmp_protection_class['Unwrapped'], tmp_file_wrapped_key)

                        # Open the file and snag the contents
                        with open(original_location, "rb") as temp_original_file:
                            # Decrypt the contents, Apple uses a 0'd out 16-byte IV
                            cipher = Cipher(algorithms.AES(tmp_file_unwrapped_key), modes.CBC(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'))
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
                except Exception as ex:
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
    def __init__(self, tar_file_path, data_folder):
        FileSeekerBase.__init__(self)
        self.is_gzip = tar_file_path.lower().endswith('gz')
        mode ='r:gz' if self.is_gzip else 'r'
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
        pat = _compile_pattern( normcase(filepattern) )
        root = normcase("root/")
        for member in self.tar_file.getmembers():
            if pat( root + normcase(member.name) ) is not None:
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
                    except Exception as ex:
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
    def __init__(self, zip_file_path, data_folder):
        FileSeekerBase.__init__(self)
        self.zip_file = ZipFile(zip_file_path)
        self.name_list = self.zip_file.namelist()
        self.data_folder = data_folder
        self.searched = {}
        self.copied = {}
        self.file_infos = {}

    def decode_extended_timestamp(self, extra_data):
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
        pat = _compile_pattern( normcase(filepattern) )
        root = normcase("root/")
        for member in self.name_list:
            if member.startswith("__MACOSX"):
                continue
            if pat( root + normcase(member) ) is not None:
                if member not in self.copied or force:
                    try:
                        extracted_path = self.zip_file.extract(member, path=self.data_folder) # already replaces illegal chars with _ when exporting
                        f = self.zip_file.getinfo(member)
                        creation_date, modification_date = self.decode_extended_timestamp(f.extra)
                        file_info = FileInfo(member, creation_date, modification_date)
                        self.file_infos[extracted_path] = file_info
                        date_time = f.date_time
                        date_time = timex.mktime(date_time + (0, 0, -1))
                        os.utime(extracted_path, (date_time, date_time))
                        self.copied[member] = extracted_path
                    except Exception as ex:
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

        pattern_to_match_filename_against = None # The specific filename pattern to use

        if '/' in filepattern or '\\' in filepattern: # Original pattern contains path separators
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
        else: # Original pattern does not contain path separators (e.g., "*.json", "myfile.db")
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
        
        # logfunc(f"FileSeekerFile: Attempting to match effective filename pattern '{pattern_to_match_filename_against}' "
        #        f"(derived from artifact pattern '{filepattern}') against actual file basename '{self.single_file_basename}'")

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
                except Exception as ex:
                    logfunc(f'FileSeekerFile: Could not copy file {self.single_file_abs_path} to {dest_data_path}: {str(ex)}')
            else: # Already copied
                copied_dest_path = self.copied.get(self.single_file_abs_path)
                if copied_dest_path:
                    found_data_paths.append(copied_dest_path)
                    # logfunc(f"FileSeekerFile: Matched (already copied). Dest: {copied_dest_path}")
        else:
            logfunc(f"FileSeekerFile: No match for effective filename pattern '{pattern_to_match_filename_against}' against "
                    f"actual file basename '{self.single_file_basename}'")
            
        self.searched[filepattern] = found_data_paths
        return found_data_paths

    def cleanup(self):
        pass
