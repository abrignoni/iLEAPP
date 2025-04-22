__artifacts_v2__ = {
    "DiscordChatsA": {  # This should match the function name exactly
        "name": "Discord Chats (KV Storage)",
        "description": "Parses Discord chats from \"a\" database",
        "author": "@stark4n6",
        "creation_date": "2025-03-31",
        "requirements": "none",
        "category": "Discord",
        "notes": "",
        "paths": ('*/Library/Caches/kv-storage/@account*/a*'),
        "output_types": "standard",  # or ["html", "tsv", "timeline", "lava"]
        "artifact_icon": "message-circle",
    }
}

import os
import json

from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records

@artifact_processor
def DiscordChatsA(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "a")
    data_list = []
    
    query = '''select data from messages0'''

    data_headers = (('Message Timestamp', 'datetime'), ('Edited Timestamp', 'datetime'),'Sender Username','Sender Global Name','Sender ID','Message','Attachment(s)','Message Type','Call Ended','Message ID','Channel ID',)

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        attach_name = message_type = call_end = sender_id = ''
        blob_data = record[0]
        if len(blob_data) > 1:
            blob_data = blob_data[1:]
            json_load = json.loads(blob_data)
            
            blob_id = json_load.get('id','')
            channel_id = json_load.get('channelId','')
            
            if 'message' in json_load:
                message_ts = str(json_load['message'].get('timestamp','')).replace('T',' ')
                edited_ts = str(json_load['message'].get('edited_timestamp','')).replace('T',' ')
                if edited_ts == 'None':
                    edited_ts = ''
                if json_load['message'].get('type','') == 0:
                    message_type = 'Message'
                elif json_load['message'].get('type','') == 3:
                    message_type = 'Call'
                    call_end = str(json_load['message']['call'].get('ended_timestamp','')).replace('T',' ')
                    
                elif json_load['message'].get('type','') == 7:
                    message_type = 'User Joined'
                elif json_load['message'].get('type','') == 19:
                    message_type = 'Reply'    
                else:
                    message_type = json_load['message'].get('type','')
                message = json_load['message'].get('content','')
                
                if 'author' in json_load['message']:
                    auth_username = json_load['message']['author'].get('username','')
                    global_username = json_load['message']['author'].get('globalName','')
                    sender_id = json_load['message']['author'].get('id','')
                    
                if 'attachments' in json_load['message'] and len(json_load['message']['attachments']) > 0:
                    attachment_list = []
                    for x in json_load['message']['attachments']:
                        attachment_name = x.get('filename','')
                        attachment_url = x.get('url','')

                        attachment_list.append(f"{attachment_name} ({attachment_url})")
                        
                    attach_name = "<br>".join(attachment_list)
            
        data_list.append((message_ts,edited_ts,auth_username,global_username,sender_id,message,attach_name,message_type,call_end,blob_id,channel_id))
        
    return data_headers, data_list, source_path