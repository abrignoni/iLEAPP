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

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, tsv, is_platform_windows, media_to_html, get_resolution_for_model_id, get_file_path, get_sqlite_db_records

def get_discordJson(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    pathedhead = pathedtail = ''
    
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
    
    def process_json(jsonfinal):
        #jsonfinal = json.loads(jsondata)
        
        timestamp = editedtimestamp = username =  botuser = content = attachments = userid = channelid = emdeddedauthor = authorurl = authoriconurl = embededurl = embededdescript = footertext = footericonurl = pathedtail = ''
        
        if 'author' in jsonfinal:
            username = (jsonfinal['author']['username'])
            userid = (jsonfinal['author']['id'])
            if 'bot' in jsonfinal['author']:
                botuser = (jsonfinal['author']['bot'])
            else:
                botuser = ''
            
        if 'timestamp' in jsonfinal:
            timestamp = (jsonfinal['timestamp'])
            
        if 'edited_timestamp' in jsonfinal:
            editedtimestamp = (jsonfinal['edited_timestamp'])
        
        if 'content' in jsonfinal:
            content = jsonfinal['content']
        
        if 'channel_id' in jsonfinal:
            channelid = jsonfinal['channel_id']
            
        
        if 'attachments' in jsonfinal:
            attachmentsData = jsonfinal['attachments']
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
    
        if 'embeds' in jsonfinal:
            if len(jsonfinal['embeds']) > 0:
                y = 0
                lenembeds = (len(jsonfinal['embeds']))        
                while y < lenembeds:
                    #print(jsonfinal[x]['embeds'])
                    if 'url' in jsonfinal['embeds'][y]:
                        embededurl = (jsonfinal['embeds'][y]['url'])
                    else:
                        embededurl = ''
                    
                    if 'description' in jsonfinal['embeds'][y]:
                        embededdescript = (jsonfinal['embeds'][y]['description'])
                    else:
                        embededdescript = ''
                        
                    if 'author' in jsonfinal['embeds'][y]:
                        emdeddedauthor = (jsonfinal['embeds'][y]['author']['name'])
                        if 'url' in jsonfinal['embeds'][y]['author']:
                            authorurl = (jsonfinal['embeds'][y]['author']['url'])
                        else:
                            authorurl = '' 
                        if 'icon_url' in jsonfinal['embeds'][y]['author']:
                            authoriconurl =(jsonfinal['embeds'][y]['author']['icon_url'])
                        else:
                            authoriconurl = ''
                    else:
                        emdeddedauthor = ''
                    
                    if 'footer' in jsonfinal['embeds']:
                        footertext = (jsonfinal['embeds'][y]['footer']['text'])
                        footericonurl = (jsonfinal['embeds'][y]['footer']['icon_url'])
                    else:
                        footertext = ''
                        footericonurl = ''

                    y = y + 1
                    
        pathedhead, pathedtail = os.path.split(pathed)    
        
        if timestamp == '':
            pass
        else:
            data_list.append((timestamp, editedtimestamp, username,  botuser, content, attachments, userid, channelid, emdeddedauthor, authorurl, authoriconurl, embededurl, embededdescript, footertext, footericonurl, pathedtail))

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
        source_path = get_file_path(files_found, "a")
        
        try:
            if not file_found.endswith('activation_record.plist') and os.path.isfile(file_found) and file_found != source_path:
                with open(file_found, "r") as f_in:
                    for jsondata in f_in:
                        jsonfinal = json.loads(jsondata)
                        logfunc(str(file_found))
                        if isinstance(jsonfinal, list):
                            jsonfinal = jsonfinal[0]
                            process_json(jsonfinal)
                        else:
                            pass
            elif source_path:
                query = '''select data from messages0'''
                #data_headers = (('Message Timestamp', 'datetime'), ('Edited Timestamp', 'datetime'),'Sender Username','Sender Global Name','Sender ID','Message','Attachment(s)','Message Type','Call Ended','Message ID','Channel ID',)

                db_records = get_sqlite_db_records(source_path, query)
                for record in db_records:
                    attach_name = message_type = call_end = sender_id = ''
                    blob_data = record[0]
                    if len(blob_data) > 1:
                        blob_data = blob_data[1:]
                        json_load = json.loads(blob_data)
                        if 'message' in json_load:
                            jsonfinal = json.loads(json.dumps(json_load['message']))
                            process_json(jsonfinal)
                
        except ValueError as e:
            pass
            #logfunc('JSON error: %s' % e)
        #logfunc('')
    if len(data_list) > 0:
        logfunc(f'Files found:{len(files_found)}')        
        report = ArtifactHtmlReport('Discord - Chats')
        report.start_artifact_report(report_folder, 'Discord - Chats')
        report.add_script()
        data_headers = ('Timestamp','Edited Timestamp','Username','Bot?','Content','Attachments','User ID','Channel ID','Embedded Author','Author URL','Author Icon URL','Embedded URL','Embedded Script','Footer Text', 'Footer Icon URL', 'Source File')   
        report.write_artifact_data_table(data_headers, data_list, pathedhead, html_no_escape=['Attachments'])
        report.end_artifact_report()
        
        tsvname = 'Discord - Chats'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Discord - Chats'
        timeline(report_folder, tlactivity, data_list, data_headers)

__artifacts__ = {
    "discordjson": (
        "Discord",
        ('*/activation_record.plist', '*/com.hammerandchisel.discord/fsCachedData/*', '*/Library/Caches/com.hackemist.SDImageCache/default/*', '*/Library/Caches/kv-storage/@account*/a*'),
        get_discordJson)
}