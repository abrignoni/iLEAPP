import os
from pathlib import Path
import tarfile
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

