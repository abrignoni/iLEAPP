#!/usr/bin/env python3
from pathlib import Path
import os
import biplist

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, media_to_html


def get_kikBplistmeta(files_found, report_folder, seeker, wrap_text, timezone_offset):
	data_list = []
	for file_found in files_found:
		file_found = str(file_found)
		isDirectory = os.path.isdir(file_found)
		if isDirectory:
			pass
		else:
			sha1org = sha1scaled = blockhash = appname = layout = allowforward = filesize = filename = thumb = appid = id = ''
			with open(file_found, 'rb') as f:
				plist = biplist.readPlist(f)
				for key,val in plist.items():
					if key == 'id':
						id = val
					elif key == 'hashes':
						for x in val:
							if x['name'] == 'sha1-original':
								sha1org = x.get('value', '')
							if x['name'] == 'sha1-scaled':
								sha1scaled = x.get('value', '')
							if x['name'] == 'blockhash-scaled':
								blockhash = x.get('value', '')
					elif key == 'string':
						for x in val:
							if x['name'] == 'app-name':
								appname = x.get('value', '')
							if x['name'] == 'layout':
								layout = x.get('value', '')
							if x['name'] == 'allow-forward':
								allowforward = x.get('value', '')
							if x['name'] == 'file-size':
								filesize = x.get('value', '')
							if x['name'] == 'file-name':
								filename = x.get('value', '')
					elif key == 'image':
						thumbfilename = id
						
						complete = Path(report_folder).joinpath('Kik')
						if not complete.exists():
							Path(f'{complete}').mkdir(parents=True, exist_ok=True)
						
						file = open(f'{complete}{thumbfilename}', "wb")
						file.write(val[0]['value'])
						file.close()
						
						imagetofind = []
						imagetofind.append(f'{complete}{thumbfilename}')
						thumb = media_to_html(id, imagetofind, report_folder)
					
					
					elif key == 'app-id':
						appid = val
						
				data_list.append((id, filename, filesize, allowforward, layout, appname, appid, sha1org, sha1scaled, blockhash, thumb  ))
				aggregate = ''
				
	if len(data_list) > 0:
		head_tail = os.path.split(file_found)
		description = 'Metadata from Kik media directory. Source are bplist files.'
		report = ArtifactHtmlReport('Kik Attachments Bplist Metadata')
		report.start_artifact_report(report_folder, 'Kik Media Metadata', description)
		report.add_script()
		data_headers = ('Content ID ', 'Filename', 'File Size', 'Allow Forward', 'Layout','App Name','App ID', 'SHA1 Original','SHA1 Scaled','Blockhash Scaled', 'Internal Thumbnail')
		report.write_artifact_data_table(data_headers, data_list, head_tail[0],html_escape=False)
		report.end_artifact_report()
		
		tsvname = 'Kik Attachments Bplist Metadata'
		tsv(report_folder, data_headers, data_list, tsvname)
	else:
		logfunc('No data on Kik Attachments Bplist MetadataD')

__artifacts__ = {
    "kikBplistmeta": (
        "Kik",
        ('*/mobile/Containers/Shared/AppGroup/*/cores/private/*/attachments/*'),
        get_kikBplistmeta)
}