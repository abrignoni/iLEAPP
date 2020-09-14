import gzip
import re
import os
import json
import shutil
import errno
from pathlib import Path
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, tsv, is_platform_windows 


def get_discordJson(files_found, report_folder, seeker):
	logfunc('Discord files:')
	data_list = []
	for file_found in files_found:
		file_found = str(file_found)
		logfunc(file_found)
		with open(file_found) as f_in:
			for jsondata in f_in:
				#jsondata = jsondata[1:-1]
				jsonfinal = json.loads(jsondata)
				#print (jsonfinal)
				print('')
				
				x = 0
				emdeddedauthor = ''
				authorurl = ''
				authoriconurl = ''
				embededurl = ''
				embededurl = ''
				embededdescript = ''
				footertext = ''
				footericonurl = ''
				
				listlength = len(jsonfinal)		
				while x < listlength:
					
					if 'author' in jsonfinal[x]:
						username = (jsonfinal[x]['author']['username'])
						userid = (jsonfinal[x]['author']['id'])
						if 'bot' in jsonfinal[x]['author']:
							botuser = (jsonfinal[x]['author']['bot'])
						else:
							botuser = ''
						
					if 'timestamp' in jsonfinal[x]:
						timestamp = (jsonfinal[x]['timestamp'])
						
					if 'edited_timestamp' in jsonfinal[x]:
						editedtimestamp = (jsonfinal[x]['edited_timestamp'])
					
					if 'content' in jsonfinal[x]:
						content = jsonfinal[x]['content']
					
					if 'channel_id' in jsonfinal[x]:
						channelid = jsonfinal[x]['channel_id']
						
					if 'attachments' in jsonfinal[x]:
						attachments = jsonfinal[x]['attachments']
						if len(attachments) > 0:
							string = (attachments[0]['url'])
							attachments = string
							recfolder = Path(file_found)
							recfolder = Path(recfolder.parent)
							desde = string.replace('https://', str(recfolder) + '/exported/')
							para = string.replace('https://','/')
							head, tail =  os.path.split(para)
							
						
							try:
								os.makedirs(report_folder + '/' + head)
								shutil.copy(desde, report_folder + '/' + head)
								fileinreport = report_folder + '/' + head
								attachments = f'<a href="{fileinreport}" style="color:red;" target="_blank">{attachments}</a>'
							except:
								pass
						#print(report_folder)
						else:
							attachments = ''
							
					if 'embeds' in jsonfinal[x]:
						if len(jsonfinal[x]['embeds']) > 0:
							y = 0
							lenembeds = (len(jsonfinal[x]['embeds']))		
							while y < lenembeds:
								#print(jsonfinal[x]['embeds'])
								if 'url' in jsonfinal[x]['embeds'][y]:
									embededurl = (jsonfinal[x]['embeds'][y]['url'])
								else:
									embededurl = ''
								
								if 'description' in jsonfinal[x]['embeds'][y]:
									embededdescript = (jsonfinal[x]['embeds'][y]['description'])
								else:
									embededdescript = ''
									
								if 'author' in jsonfinal[x]['embeds'][y]:
									emdeddedauthor = (jsonfinal[x]['embeds'][y]['author']['name'])
									if 'url' in jsonfinal[x]['embeds'][y]['author']:
										authorurl = (jsonfinal[x]['embeds'][y]['author']['url'])
									else:
										authorurl = '' 
									if 'icon_url' in jsonfinal[x]['embeds'][y]['author']:
										authoriconurl =(jsonfinal[x]['embeds'][y]['author']['icon_url'])
									else:
										authoriconurl = ''
								else:
									emdeddedauthor = ''
								
								if 'footer' in jsonfinal[x]['embeds']:
									footertext = (jsonfinal[x]['embeds'][y]['footer']['text'])
									footericonurl = (jsonfinal[x]['embeds'][y]['footer']['icon_url'])
								else:
									footertext = ''
									footericonurl = ''

								y = y + 1
								
						
					data_list.append((timestamp, editedtimestamp, username,  botuser, content, attachments, userid, channelid, emdeddedauthor, authorurl, authoriconurl, embededurl, embededdescript, footertext, footericonurl))
					x = x + 1

	if len(data_list) > 0:		
		report = ArtifactHtmlReport('Discord Messages from Windows')
		report.start_artifact_report(report_folder, 'Discord Messages')
		report.add_script()
		data_headers = ('Timestamp','Edited Timestamp','Username','Bot?','Content','Attachments','User ID','Channel ID','Embedded Author','Author URL','Author Icon URL','Embedded URL','Embedded Script','Footer Text', 'Footer Icon URL')   
		report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
		report.end_artifact_report()
		
		tsvname = 'Discord Messages'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'Discord Messages'
		timeline(report_folder, tlactivity, data_list, data_headers)