import fnmatch
import os

from pathlib import Path
from scripts.ilapfuncs import *
from tarfile import TarFile
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

    def search(self, filepattern):
        list = []
        for file in Path(self.directory).rglob(filepattern):
            list.append(file)
        return list

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
                    self.tar_file.extract(member.name, path=self.temp_folder)
                    pathlist.append(os.path.join(self.temp_folder, Path(member.name)))
                except:
                    logfunc('Could not write file to filesystem')
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
                    self.zip_file.extract(member, path=self.temp_folder)
                    member = member.lstrip("/")
                    pathlist.append(os.path.join(self.temp_folder, Path(member)))
                except:
                    logfunc('Could not write file to filesystem')    
        return pathlist

    def cleanup(self):
        self.zip_file.close()
