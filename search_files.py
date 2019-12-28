import os
from pathlib import Path
import tarfile
from zipfile import ZipFile
import fnmatch


def search(pathto, filename):
	list = []
	for file in Path(pathto).rglob(filename):
		list.append(file)
	return list

def searchtar(pathto, val, reportfolderbase):
	temp = reportfolderbase+'temp/'
	pathlist = []
	with tarfile.open(pathto, mode='r:tar') as t:
		for member in t.getmembers():
			if fnmatch.fnmatch(member.name, val):
				t.extract(member.name, path=temp)
				pathlist.append(temp+member.name)
	return pathlist

def searchzip(pathto, val, reportfolderbase):
	temp = reportfolderbase+'temp/'
	pathlist = []
	with ZipFile(pathto, mode='r') as z:
		for member in z.namelist():
			if fnmatch.fnmatch(member, val):
				z.extract(member, path=temp)
				pathlist.append(temp+member)
	return pathlist