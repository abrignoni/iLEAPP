import fnmatch
import os
import tarfile
from pathlib import Path
from zipfile import ZipFile

from ilapfuncs import *
from settings import temp


def search(pathto, filename):
    return [fname for fname in Path(pathto).rglob(filename)]


def get_archive_member_names(archive_obj):
    """
    Returns list of members names based on parent class of archive.
    
    Note: 
    This function assumes that the caller has done the work to identify the
    correct file type and wrap it in the right class.
    """
    if isinstance(archive_obj, tarfile.TarFile):
        member_names = archive_obj.getnames()
    elif isinstance(archive_obj, ZipFile):
        member_names = archive_obj.namelist()
    else:
        raise ValueError("This file type is not supported")
    return member_names


def search_archive(archive_obj, search_path):
    paths = list()
    member_names = get_archive_member_names(archive_obj)

    for member_name in member_names:
        if fnmatch.fnmatch(member_name, search_path):
            member_path = member_name.lstrip('/')
            try:
                archive_obj.extract(member_name, path=temp)
                paths.append(os.path.join(temp, member_path))
            except Exception:
                logfunc("Could not write file to filesystem")
    return paths
