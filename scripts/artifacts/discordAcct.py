import gzip
import re
import os
import json
import shutil
import errno
from pathlib import Path
import string
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, tsv, is_platform_windows 

def strings(filename, min=4):
	with open(filename, errors="ignore") as f:  # Python 3.x
	# with open(filename, "rb") as f:           # Python 2.x
		result = ""
		for c in f.read():
			if c in string.printable:
				result += c
				continue
			if len(result) >= min:
				yield result
			result = ""
		if len(result) >= min:  # catch result at EOF
			yield result

def get_discordAcct(files_found, report_folder, seeker, wrap_text, timezone_offset):
	searchlist = []
	for file_found in files_found:
		file_found = str(file_found)
		
		for s in strings(file_found):
			#print(type(s))
			#print(s)
			searchlist.append(str(s),)

		counter = 0
		data_list = []
		for x in searchlist:
			counter += 1
			if 'user_id_cache' in x:
				#print(x)
				wf = searchlist[counter].split('"')
				try:
					data_list.append(('USER_ID_CACHE', wf[1]))
				except:
					pass
				
			if 'email_cache' in x:
				#print(x)
				wfa = searchlist[counter].split('"')
				try:
					data_list.append(('EMAIL_CACHE', wfa[1]))
				except:
					pass

	if len(data_list) > 0:		
		report = ArtifactHtmlReport('Discord Account')
		report.start_artifact_report(report_folder, 'Discord Account')
		report.add_script()
		data_headers = ('Key', 'Value')   
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'Discord Account'
		tsv(report_folder, data_headers, data_list, tsvname)

__artifacts__ = {
    "discordacct": (
        "Discord",
        ('*/mobile/Containers/Data/Application/*/Documents/mmkv/mmkv.default'),
        get_discordAcct)
}