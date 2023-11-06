# Discord JSON
# Original Author: Unknown
#
# Version: 1.1.0
# Author:  John Hyla
# Adds connection of chat thread to cached attachment files
#
#


import gzip
import re
import os
import json
import math
import hashlib
import biplist
import shutil
import errno
from pathlib import Path
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, tsv, is_platform_windows, media_to_html, get_resolution_for_model_id



def get_discordJson(files_found, report_folder, seeker, wrap_text, timezone_offset):


	def reduceSize(width: int, height: int, max_width: int, max_height: int) -> (int, int):
		if width > height:
			if width > max_width:
				new_width = max_width
				ratio = width / new_width
				new_height = math.ceil(height / ratio)
			else:
				new_width = width
				new_height = height
		else:
			if height > max_height:
				new_height = max_height
				ratio = height / new_height
				new_width = math.ceil(width / ratio)
			else:
				new_width = width
				new_height = height
		return (new_width, new_height)

	#First find modelID and screen resolution
	resolution = None
	activation_record_found = False
	for file_found in files_found:
		file_found = str(file_found)
		if file_found.endswith('activation_record.plist'):
			activation_record_found = True
			plist = biplist.readPlist(file_found)
			account_token = plist['AccountToken'].decode("utf-8")

			pattern = r'"(.*?)" = "(.*?)";'
			matches = re.findall(pattern, account_token, re.DOTALL)

			# Create a dictionary from the extracted key-value pairs
			parsed_data = {key: value for key, value in matches}

			model_id = parsed_data.get('ProductType')

			if not model_id:
				logfunc(f"Cannot detect model ID. Cannot link attachments")
				break
			resolution = get_resolution_for_model_id(model_id)

			break
	if not activation_record_found:
		logfunc(f'activation_record.plist not found. Unable to determine model/resolution for attachment linking')
	if not resolution:
		logfunc(f"Cannot link attachments due to missing resolution")

	data_list = []

	for file_found in files_found:
		file_found = str(file_found)
		pathed = file_found
		
		try:
			if not file_found.endswith('activation_record.plist') and os.path.isfile(file_found):
				with open(file_found) as f_in:
					for jsondata in f_in:
						#jsondata = jsondata[1:-1]
						jsonfinal = json.loads(jsondata)
						#print (jsonfinal)
						
						x = 0
						emdeddedauthor = ''
						authorurl = ''
						authoriconurl = ''
						embededurl = ''
						embededurl = ''
						embededdescript = ''
						footertext = ''
						footericonurl = ''
						
						timestamp = editedtimestamp = username =  botuser = content = attachments = userid = channelid = emdeddedauthor = authorurl = authoriconurl = embededurl = embededdescript = footertext = footericonurl = pathedtail = ''
						
						listlength = len(jsonfinal)
						if isinstance(jsonfinal, list):	
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
									attachmentsData = jsonfinal[x]['attachments']
									attachmentsArray = []
									if len(attachmentsData) > 0:
										for a in attachmentsData:
											if resolution:
												#Get the width and height from the attachment record
												width = a.get('width')
												height = a.get('height')
												original_proxy_url = a.get('proxy_url')
												#Make sure there is a width or its probably not an image we can do anything with
												if not width:
													#Just show the URL (Could be a voice message or other type)
													attachmentsArray.append(original_proxy_url)
												else:
													# Find the extension in the url
													pattern = r'attachments.+(\.[^?=]{1,4})\??'
													match = re.search(pattern, original_proxy_url)

													if match:
														ext = match.group(1)
													else:
														ext = ''

													#Found an image (maybe video?)
													new_width, new_height = reduceSize(width, height, resolution['Width'], int(resolution['Height']/2))
													if new_height == height and new_width == width:
														if ext == '.gif':
															#Not sure what other extensions might need to omit the = at end?
															proxy_url = original_proxy_url
														else:
															proxy_url = original_proxy_url + '='
													else:
														proxy_url = original_proxy_url
														if proxy_url[-1] == "&":
															proxy_url += f'=&width={new_width}&height={new_height}'
														else:
															proxy_url += f'?width={new_width}&height={new_height}'


													#Generate MD5 with extension appended
													proxy_url_md5 = hashlib.md5(proxy_url.encode('utf-8')).hexdigest() + ext

													#Check if a file by this name was found
													if any(proxy_url_md5 in string for string in files_found):
														#If Yes, generate thumbnail
														attachmentsArray.append(media_to_html(proxy_url_md5, files_found, report_folder))
													else:
														#If no, show the URL, but also show the filename we think should exist in case it can be located elsewhere
														attachmentsArray.append(a.get('proxy_url') + f' ({proxy_url_md5})')
											else:
												#Resolution was not found, just show the URL
												attachmentsArray.append(a.get('proxy_url'))

										#Combine all attachments
										attachments = "<br>".join(attachmentsArray)
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
											
								pathedhead, pathedtail = os.path.split(pathed)	
								
								if timestamp == '':
									pass
								else:
									data_list.append((timestamp, editedtimestamp, username,  botuser, content, attachments, userid, channelid, emdeddedauthor, authorurl, authoriconurl, embededurl, embededdescript, footertext, footericonurl, pathedtail))

								x = x + 1
						else:
							pass
							#logfunc('JSON data is no expected list')
		except ValueError as e:
			pass
			#logfunc('JSON error: %s' % e)
		#logfunc('')
	if len(data_list) > 0:
		logfunc(f'Files found:{len(files_found)}')		
		report = ArtifactHtmlReport('Discord Messages')
		report.start_artifact_report(report_folder, 'Discord Messages')
		report.add_script()
		data_headers = ('Timestamp','Edited Timestamp','Username','Bot?','Content','Attachments','User ID','Channel ID','Embedded Author','Author URL','Author Icon URL','Embedded URL','Embedded Script','Footer Text', 'Footer Icon URL', 'Source File')   
		report.write_artifact_data_table(data_headers, data_list, pathedhead, html_no_escape=['Attachments'])
		report.end_artifact_report()
		
		tsvname = 'Discord Messages'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'Discord Messages'
		timeline(report_folder, tlactivity, data_list, data_headers)

__artifacts__ = {
    "discordjson": (
        "Discord",
        ('*/activation_record.plist', '*/com.hammerandchisel.discord/fsCachedData/*', '*/Library/Caches/com.hackemist.SDImageCache/default/*'),
        get_discordJson)
}