import fnmatch
import os

from pathlib import Path
from scripts.ilapfuncs import *
from tarfile import TarFile, ExFileObject, TarInfo
from zipfile import ZipFile

class FileSeekerBase:
    # This is an abstract base class
    def search(self, filepattern_to_search):
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
        logfunc('Building files listing')
        self.build_files_list(directory)

    def build_files_list(self, directory):
        '''Populates all paths in directory into _all_files'''
        files_list = os.scandir(directory)
        for item in files_list:
            self._all_files.append(item.path)
            if item.is_dir(follow_symlinks=False):
                self.build_files_list(item.path)

    def search(self, filepattern):
        return fnmatch.filter(self._all_files, filepattern)

class FileSeekerTar(FileSeekerBase):
    def __init__(self, tar_file_path, temp_folder):
        FileSeekerBase.__init__(self)
        self.tar_file = TarFile(tar_file_path)
        self.temp_folder = temp_folder

    def search(self, filepattern):
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
                            fout.write(ExFileObject(self.tar_file, member).read())
                            fout.close()
                        os.utime(full_path, (member.mtime, member.mtime))
                    pathlist.append(full_path)
                except Exception as ex:
                    logfunc(f'Could not write file to filesystem, path was {member.name}' + str(ex))
        return pathlist

    def cleanup(self):
        self.tar_file.close()

class FileSeekerZip(FileSeekerBase):
    def __init__(self, zip_file_path, temp_folder):
        FileSeekerBase.__init__(self)
        self.zip_file = ZipFile(zip_file_path)
        self.name_list = self.zip_file.namelist()
        self.temp_folder = temp_folder

    def search(self, filepattern):
        pathlist = []
        for member in self.name_list:
            if fnmatch.fnmatch(member, filepattern):
                try:
                    self.zip_file.extract(member, path=self.temp_folder) # already replaces illegal chars with _ when exporting
                    member = member.lstrip("/")
                    clean_name = sanitize_file_path(member) # replace illegal chars in path (if any)
                    full_path = os.path.join(self.temp_folder, Path(clean_name))
                    pathlist.append(full_path)
                except Exception as ex:
                    logfunc(f'Could not write file to filesystem, path was {member}' + str(ex))
        return pathlist

    def cleanup(self):
        self.zip_file.close()
