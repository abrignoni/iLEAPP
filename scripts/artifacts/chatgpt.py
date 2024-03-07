__artifacts_v2__ = {
    "chatgpt": {
        "name": "ChatGPT",
        "description": "Get user's ChatGPT conversations, settings and media files. This parser is based on a research project",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "version": "1.0.1",
        "date": "2024-02-10",
        "requirements": "",
        "category": "ChatGPT",
        "paths": (
            '**/Containers/Data/Application/*/Library/Application Support/conversations-*/*.*', 
            '**/Containers/Data/Application/*/Library/Application Support/drafts-*/*.*',
            '**/Containers/Data/Application/*/Library/Preferences/com.openai.chat.StatsigService.plist',
            '**/Containers/Data/Application/*/Library/Preferences/com.segment.storage.oai.plist',
            '**/Containers/Data/Application/*/Library/Preferences/com.openai.chat.plist',
            '**/Containers/Data/Application/*/tmp/recordings/*.*',
            '**/Containers/Data/Application/*/tmp/photo-*.*',
            '**/Containers/Data/Application/*/tmp/*/*.*',
        ),
        "function": "get_chatgpt"
    }
}


import biplist
import json
import base64
import blackboxprotobuf
import os
from pathlib import Path
from datetime import datetime
from packaging import version
from scripts.ccl import ccl_segb1
from scripts.ccl import ccl_segb2
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, media_to_html,timestampsconv, convert_utc_human_to_timezone,convert_ts_int_to_utc,is_platform_windows
import scripts.artifacts.artGlobals


def get_chatgpt(files_found, report_folder, seeker, wrap_text, time_offset):
    conversations_metadata = []
    conversations_messages = []
    draft_messages = []
    account_list = []
    account_list_files_found = []
    voice_list = []
    photo_list = []
    for file_found in files_found:
        file_found = str(file_found)
        #counter += 1 
        file_name = os.path.basename(file_found)
        if file_name.endswith('.json') and "conversations-" in file_found:
            with open(file_found, 'r', encoding="utf-8") as file:
                data = json.load(file)
                try:
                    conversation_id = data.get("id", "")
                    conversation_title = data.get("title", "")
                    creation_time = convert_utc_human_to_timezone(timestampsconv(int(data.get("creation_date", 0))),time_offset)
                    modification_time = convert_utc_human_to_timezone(timestampsconv(int(data.get("modification_date", 0))),time_offset)
                    model = data.get("configuration", {}).get("model", "")
                    custom_instructions_model = data.get("configuration", {}).get("custom_instructions", {}).get("about_model_message", "")
                    custom_instructions_user = data.get("configuration", {}).get("custom_instructions", {}).get("about_user_message", "")
                    custom_instructions_active = data.get("configuration", {}).get("custom_instructions", {}).get("active", False)
                    is_temporary_chat = data.get("configuration", {}).get("is_temporary_chat", False)
                    conversations_metadata.append((creation_time,modification_time,conversation_title,conversation_id,model,custom_instructions_model,custom_instructions_user,custom_instructions_active,is_temporary_chat,file_found))
                except:
                    logfunc(f'Error parsing ChatGPT - conversation metadata from -> {file_found}')
                try:
                    if isinstance(data.get("tree"), dict) and isinstance(data.get("tree", {}).get("storage"), dict):
                        for message_id, message_details in data.get("tree").get("storage").items():
                            content = message_details.get("content", {})
                            author = content.get("author", {}).get("role", "")
                            parts = content.get("content", {}).get("parts", [""])
                            create_time_raw = content.get("create_time")
                            if create_time_raw:
                                create_time = convert_utc_human_to_timezone(convert_ts_int_to_utc(int(create_time_raw)), time_offset)
                                # create_time = datetime.utcfromtimestamp(create_time_raw).isoformat() + 'Z'
                            else:
                                create_time = ""
                            content_type = content.get("content_type", "")
                            finish_details = content.get("metadata", {}).get("finish_details", {}).get("type", "")
                            voice_mode_message = content.get("metadata", {}).get("voice_mode_message", False)
                            metadata = {key: value for key, value in content.get("metadata", {}).items()}
                            conversations_messages.append((create_time,message_id,conversation_title,conversation_id,author,parts,content_type,finish_details,voice_mode_message,metadata,file_found))
                except:
                    logfunc(f'Error parsing ChatGPT - conversation messages from -> {file_found}')
                
                #parsing collected conversations metadata
                if len(conversations_metadata) > 0:
                    description = f'Metadata from ChatGPT conversations'
                    report = ArtifactHtmlReport(f'ChatGPT - Conversations Metadata')
                    report.start_artifact_report(report_folder, f'ChatGPT - Conversations Metadata', description)
                    report.add_script()
                    data_headers = ('Creation Time','Modification Date','Title','Conversation ID','Model','Custom Instructions (Model)','Custom Instructions (User)','Custom Instructions (Enabled)','Is Temporary','File Path') 
                    report.write_artifact_data_table(data_headers, conversations_metadata, file_found, html_escape=False)
                    report.end_artifact_report()
                    
                    tsvname = f'ChatGPT - Conversations Metadata'
                    tsv(report_folder, data_headers, conversations_metadata, tsvname)

                    tlactivity = f'ChatGPT - Conversations Metadata'
                    timeline(report_folder, tlactivity, conversations_metadata, data_headers)
                else:
                    logfunc(f'No ChatGPT - Conversations Metadata available')

                #parsing collected conversations metadata
                if len(conversations_messages) > 0:
                    description = f'User conversations with ChatGPT'
                    report = ArtifactHtmlReport(f'ChatGPT - Conversations')
                    report.start_artifact_report(report_folder, f'ChatGPT - Conversations', description)
                    report.add_script()
                    data_headers = ('Creation Time','Message ID','Conversation Title','Conversation ID','Author','Parts','Content Type','Finish Details', 'Voice Mode Message','Metadata','File Path')
                    report.write_artifact_data_table(data_headers, conversations_messages, file_found, html_escape=False)
                    report.end_artifact_report()
                    
                    tsvname = f'ChatGPT - Conversations'
                    tsv(report_folder, data_headers, conversations_messages, tsvname)

                    tlactivity = f'ChatGPT - Conversations'
                    timeline(report_folder, tlactivity, conversations_messages, data_headers)
                else:
                    logfunc(f'No ChatGPT - Conversations available')


        if file_name.endswith('.json') and "drafts-" in file_found:
            with open(file_found, 'r', encoding="utf-8") as file:
                data = json.load(file)
                try:
                    conversation_id = data.get("conversation_id", "")
                    text = data.get("content", {}).get("text", "")
                    draft_messages.append((conversation_id,text,file_found))
                except:
                    logfunc(f'Error parsing ChatGPT - draft messages from -> {file_found}')

                    #parsing draft conversations 
                if len(draft_messages) > 0:
                    description = f'User draft conversations with ChatGPT'
                    report = ArtifactHtmlReport(f'ChatGPT - Draft Conversations')
                    report.start_artifact_report(report_folder, f'ChatGPT - Draft Conversations', description)
                    report.add_script()
                    data_headers = ('Conversation ID','Content','File Path')
                    report.write_artifact_data_table(data_headers, draft_messages, file_found, html_escape=False)
                    report.end_artifact_report()
                    
                    tsvname = f'ChatGPT - Draft Conversations'
                    tsv(report_folder, data_headers, draft_messages, tsvname)

                else:
                    logfunc(f'No ChatGPT - Draft Conversations available')

        if file_name.endswith('com.openai.chat.StatsigService.plist'):
            #account_list = []
            with open(file_found, 'rb') as file: #, encoding="utf-8"
                try:
                    plist_data = biplist.readPlist(file)
                except (biplist.InvalidPlistException, biplist.NotBinaryPlistException, OSError) as e:
                    logfunc(f"Error parsing ChatGPT while reading bplist {file_found} file: {str(e)}")

                try:
                    accountID = plist_data.get("accountID", "")
                    planType = plist_data.get("planType", "")
                    userID = plist_data.get("userID", "")
                    userEmail = plist_data.get("userEmail", "")
                    account_list.append((accountID,userID,userEmail,planType,"","","",""))
                    account_list_files_found.append(file_found)
                except:
                    logfunc(f'Error parsing ChatGPT - preferences from -> {file_found}')


        if file_name.endswith('com.segment.storage.oai.plist'):
            with open(file_found, 'rb') as file: #, encoding="utf-8"
                try:
                    plist_data = biplist.readPlist(file)
                except (biplist.InvalidPlistException, biplist.NotBinaryPlistException, OSError) as e:
                    logfunc(f"Error parsing ChatGPT while reading bplist {file_found} file: {str(e)}")

                try:
                    segevents = plist_data.get("segment.events", "")
                    userID = plist_data.get("segment.userId", "")
                    #segment.traits value is a nested plist
                    segment_traits_data = plist_data.get("segment.traits")
                    if segment_traits_data:
                        try:
                            segment_traits = biplist.readPlistFromString(segment_traits_data)

                        except biplist.InvalidPlistException as e:
                            print(f"Error parsing ChatGPT while reading nested plist data from {file_found}: . Error was: {e}")                    
                    workspace_id = segment_traits.get("workspace_id", "")
                    paid_plan = segment_traits.get("has_paid_plan", "")
                    device_id = segment_traits.get("device_id", "")
                    plan_type = segment_traits.get("plan_type", "")
                    account_list.append(("",userID,"",plan_type,paid_plan,workspace_id,device_id,segevents))
                    account_list_files_found.append(file_found)
                except:
                    logfunc(f'Error parsing ChatGPT - Account from -> {file_found}')

        if file_name.endswith('com.openai.chat.plist'):
            # To add suppport
            # BPLIST file with embeeded SEGB v2 files that holds the external IP address of the user's device
            pass

        if file_name.endswith('.png') and "tmp" in file_found:
            filename = (Path(file_found).name)
            filepath = str(Path(file_found).parents[1])
                
            thumb = media_to_html(filename, files_found, report_folder)
            
            platform = is_platform_windows()
            if platform:
                thumb = thumb.replace('?', '')
                
            photo_list.append((thumb, filename, file_found))


        if file_name.endswith('.m4a') and "tmp" in file_found:
            
            filename = (Path(file_found).name)
            filepath = str(Path(file_found).parents[1])
                
            audio = media_to_html(filename, files_found, report_folder)
            
            platform = is_platform_windows()
            if platform:
                audio = audio.replace('?', '')
                
            if (audio, filename, file_found) in voice_list:
                pass
            else:
                voice_list.append((audio, filename, file_found))
    
    #reporting preferences
    if len(account_list) > 0:
        description = f'ChatGPT preferences (account information)'
        report = ArtifactHtmlReport(f'ChatGPT - Preferences')
        report.start_artifact_report(report_folder, f'ChatGPT - Preferences', description)
        report.add_script()
        prefs_files_found = ',\n'.join(account_list_files_found) 
        data_headers = ('Account ID','User ID','Email', 'Plan Type','Paid Plan','Workspace ID', 'Device ID','Segments Events')
        report.write_artifact_data_table(data_headers, account_list, prefs_files_found, html_escape=False)
        report.end_artifact_report()
        
        tsvname = f'ChatGPT - Preferences'
        tsv(report_folder, data_headers, account_list, tsvname)

    #after iterating through all files found we check if there are any images, voice prompts to report
    if len(photo_list) > 0:
        description = 'Images uploaded to ChatGPT'
        report = ArtifactHtmlReport('ChatGPT - Media Uploads')
        report.start_artifact_report(report_folder, 'ChatGPT - Media Uploads', description)
        report.add_script()
        data_headers = ('Thumbnail','File Name','File Path')
        report.write_artifact_data_table(data_headers, photo_list, filepath, html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'ChatGPT - Media Uploads'
        tsv(report_folder, data_headers, photo_list, tsvname)
        
    else:
        logfunc('No ChatGPT - Media Uploads available')

    if len(voice_list) > 0:
        description = 'Voice prompts that were transcribed and uploaded to ChatGPT'
        report = ArtifactHtmlReport('ChatGPT - Voice Prompts')
        report.start_artifact_report(report_folder, 'ChatGPT - Voice Prompts', description)
        report.add_script()
        data_headers = ('Voice Prompt','File Name','File Path' )
        report.write_artifact_data_table(data_headers, voice_list, filepath, html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'ChatGPT - Voice Prompts'
        tsv(report_folder, data_headers, voice_list, tsvname)
        
    else:
        logfunc('No ChatGPT - Voice Prompts available')