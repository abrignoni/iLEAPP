#!/usr/bin/env python3

import os
import nska_deserialize as nd

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows


def get_kikBplistmeta(files_found, report_folder, seeker):
	data_list = []
	aggregate = ''
	for file_found in files_found:
		file_found = str(file_found)
		isDirectory = os.path.isdir(file_found)
		if isDirectory:
			pass
		else:    
			with open(file_found, 'rb') as f:
				fileurl = contentid = appid = ''
				deserialized_plist = nd.deserialize_plist(f)
				for key,val in deserialized_plist['$0'].items():
					if key == 'fileURL':
						fileurl = val
					elif key == 'contentID':
						contentid = val
					elif key == 'appID':
						appid = val 
					else:
						aggregate = aggregate + f'{key}: {val} <br>'
						
				data_list.append((contentid, appid, fileurl, aggregate))
				aggregate = ''
				
	if len(data_list) > 0:
		head_tail = os.path.split(file_found)
		description = 'Metadata from Kik media directory. Source are bplist files.'
		report = ArtifactHtmlReport('Kik Attachments Bplist Metadata')
		report.start_artifact_report(report_folder, 'Kik Media Metadata', description)
		report.add_script()
		data_headers = ('Content ID / Filename','App ID','File URL','Additional Metadata')
		report.write_artifact_data_table(data_headers, data_list, head_tail[0],html_escape=False)
		report.end_artifact_report()
		
		tsvname = 'Kik Attachments Bplist Metadata'
		tsv(report_folder, data_headers, data_list, tsvname)
	else:
		logfunc('No data on Kik Attachments Bplist MetadataD')