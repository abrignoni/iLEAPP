import time as timex
import fnmatch
import os
import tarfile
import hashlib
import struct

from pathlib import Path
from scripts.ilapfuncs import *
from shutil import copyfile
from zipfile import ZipFile

from fnmatch import _compile_pattern
from functools import lru_cache

from scripts.builds_ids import get_root_path_from_domain
normcase = lru_cache(maxsize=None)(os.path.normcase)

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
    def __init__(self, directory, data_folder):
        FileSeekerBase.__init__(self)
        self.directory = directory
        self._all_files = {}
        self.files_metadata = {}
        self.data_folder = data_folder
        logfunc('Building files listing...')
        if os.path.exists(os.path.join(directory, "Manifest.db")):
            self.build_files_list_from_manifest_db(directory)
            self.backup_type = "Manifest.db"
        elif os.path.exists(os.path.join(directory, "Manifest.mbdb")):
            self.build_files_list_from_manifest_mbdb(directory)
            self.backup_type = "Manifest.mbdb"
        logfunc(f'File listing complete - {len(self._all_files)} files')
        self.searched = {}
        self.copied = {}
        self.file_infos = {}
    
    def build_files_list_from_manifest_db(self, directory):
        '''Populates paths from Manifest.db files into _all_files'''
        try: 
            db = open_sqlite_db_readonly(os.path.join(directory, "Manifest.db"))
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
                self.files_metadata[hash_filename] = file_metadata
            db.close()
        except Exception as ex:
            logfunc(f'Error opening Manifest.db from {directory}, ' + str(ex))
            raise ex

    def build_files_list_from_manifest_mbdb(self, directory):
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

        def process_mbdb_file(directory):
            files = list()
            with open(os.path.join(directory, "Manifest.mbdb"), 'rb') as f:
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
            all_rows = process_mbdb_file(directory)
            for row in all_rows:
                hash_filename = row[0]
                domain = row[1]
                root_path = get_root_path_from_domain(domain)
                relative_path = row[2]
                full_path = os.path.join(root_path, relative_path)
                self._all_files[full_path] = hash_filename
        except Exception as ex:
            logfunc(f'Error opening Manifest.mbdb from {directory}, ' + str(ex))
            raise ex

    def search(self, filepattern, return_on_first_hit=False, force=False):
        if filepattern in self.searched and not force:
            pathlist = self.searched[filepattern]
            return self.searched[filepattern][0] if return_on_first_hit and pathlist else pathlist
        pathlist = []
        matching_keys = fnmatch.filter(self._all_files, filepattern)
        for relative_path in matching_keys:
            hash_filename = self._all_files[relative_path]
            if self.backup_type == "Manifest.db":
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
