import fnmatch
import os
import sqlite3
import tarfile

from pathlib import Path
from scripts.ilapfuncs import *
from shutil import copyfile
from zipfile import ZipFile

class FileSeekerBase:
    # This is an abstract base class
    def search(self, filepattern_to_search, return_on_first_hit=False):
        '''Returns a list of paths for files/folders that matched'''
        pass

    def cleanup(self):
        '''close any open handles'''
        pass

class FileSeekerDir(FileSeekerBase):
    def __init__(self, directory):
        FileSeekerBase.__init__(self)
        self.directory = directory
        self._all_files = []
        logfunc('Building files listing...')
        self.build_files_list(directory)
        logfunc(f'File listing complete - {len(self._all_files)} files')

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

    def search(self, filepattern, return_on_first_hit=False):
        if return_on_first_hit:
            for item in self._all_files:
                if fnmatch.fnmatch(item, filepattern):
                    return [item]
            return []
        return fnmatch.filter(self._all_files, filepattern)

class FileSeekerItunes(FileSeekerBase):
    def __init__(self, directory, temp_folder):
        FileSeekerBase.__init__(self)
        self.directory = directory
        self._all_files = {}
        self.temp_folder = temp_folder
        logfunc('Building files listing...')
        self.build_files_list(directory)
        logfunc(f'File listing complete - {len(self._all_files)} files')

    def build_files_list(self, directory):
        '''Populates paths from Manifest.db files into _all_files'''
        try: 
            db = open_sqlite_db_readonly(os.path.join(directory, "Manifest.db"))
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT
                fileID,
                relativePath
                FROM
                Files
                WHERE
                flags=1
                """
            )
            all_rows = cursor.fetchall()
            for row in all_rows:
                hash_filename = row[0]
                relative_path = row[1]
                self._all_files[relative_path] = hash_filename
            db.close()
        except Exception as ex:
            logfunc(f'Error opening Manifest.db from {directory}, ' + str(ex))
            raise ex

    def search(self, filepattern, return_on_first_hit=False):
        pathlist = []
        matching_keys = fnmatch.filter(self._all_files, filepattern)
        for relative_path in matching_keys:
            hash_filename = self._all_files[relative_path]
            original_location = os.path.join(self.directory, hash_filename[:2], hash_filename)
            temp_location = os.path.join(self.temp_folder, sanitize_file_path(relative_path))
            if is_platform_windows():
                temp_location = temp_location.replace('/', '\\')
            try:
                os.makedirs(os.path.dirname(temp_location), exist_ok=True)
                copyfile(original_location, temp_location)
                pathlist.append(temp_location)
            except Exception as ex:
                logfunc(f'Could not copy {original_location} to {temp_location} ' + str(ex))
        return pathlist

class FileSeekerTar(FileSeekerBase):
    def __init__(self, tar_file_path, temp_folder):
        FileSeekerBase.__init__(self)
        self.is_gzip = tar_file_path.lower().endswith('gz')
        mode ='r:gz' if self.is_gzip else 'r'
        self.tar_file = tarfile.open(tar_file_path, mode)
        self.temp_folder = temp_folder

    def search(self, filepattern, return_on_first_hit=False):
        pathlist = []
        for member in self.tar_file.getmembers():
            if fnmatch.fnmatch(member.name, filepattern):
                try:
                    clean_name = sanitize_file_path(member.name)
                    full_path = os.path.join(self.temp_folder, Path(clean_name))
                    if member.isdir():
                        os.makedirs(full_path)
                    else:
                        parent_dir = os.path.dirname(full_path)
                        if not os.path.exists(parent_dir):
                            os.makedirs(parent_dir)
                        with open(full_path, "wb") as fout:
                            fout.write(tarfile.ExFileObject(self.tar_file, member).read())
                            fout.close()
                        os.utime(full_path, (member.mtime, member.mtime))
                    pathlist.append(full_path)
                except Exception as ex:
                    logfunc(f'Could not write file to filesystem, path was {member.name} ' + str(ex))
        return pathlist

    def cleanup(self):
        self.tar_file.close()

class FileSeekerZip(FileSeekerBase):
    def __init__(self, zip_file_path, temp_folder):
        FileSeekerBase.__init__(self)
        self.zip_file = ZipFile(zip_file_path)
        self.name_list = self.zip_file.namelist()
        self.temp_folder = temp_folder

    def search(self, filepattern, return_on_first_hit=False):
        pathlist = []
        for member in self.name_list:
            if fnmatch.fnmatch(member, filepattern):
                try:
                    extracted_path = self.zip_file.extract(member, path=self.temp_folder) # already replaces illegal chars with _ when exporting
                    pathlist.append(extracted_path)
                except Exception as ex:
                    member = member.lstrip("/")
                    logfunc(f'Could not write file to filesystem, path was {member} ' + str(ex))
        return pathlist

    def cleanup(self):
        self.zip_file.close()
