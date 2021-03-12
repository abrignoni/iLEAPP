import sqlite3
import io
import json
import nska_deserialize as nd
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, kmlgen, tsv, is_platform_windows, open_sqlite_db_readonly


def get_instagramThreads(files_found, report_folder, seeker):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.db'):
            break
        
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select
    metadata
    from threads
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    fila = 0
    userdict = {}
    data_list = []
    video_calls = []
    
    if usageentries > 0:
        for row in all_rows:
            plist = ''
            plist_file_object = io.BytesIO(row[0])
            if row[0].find(b'NSKeyedArchiver') == -1:
                if sys.version_info >= (3, 9):
                    plist = plistlib.load(plist_file_object)
                else:
                    plist = biplist.readPlist(plist_file_object)
            else:
                try:
                    plist = nd.deserialize_plist(plist_file_object)                    
                except (nd.DeserializeError, nd.biplist.NotBinaryPlistException, nd.biplist.InvalidPlistException,
                        nd.plistlib.InvalidFileException, nd.ccl_bplist.BplistError, ValueError, TypeError, OSError, OverflowError) as ex:
                    logfunc(f'Failed to read plist for {row[0]}, error was:' + str(ex))
            
            for i in plist['NSArray<IGUser *>*users']:
                for x, y in enumerate(plist['NSArray<IGUser *>*users']):
                    userPk = plist['NSArray<IGUser *>*users'][x]['pk']
                    userFull = (plist['NSArray<IGUser *>*users'][x]['fullName'])
                    userdict[userPk] = userFull
                
            inviterPk = plist['IGUser*inviter']['pk']
            inviterFull = plist['IGUser*inviter']['fullName']
            userdict[inviterPk] = inviterFull
        
    cursor.execute('''
    select
    messages.message_id,
    messages.thread_id,
    messages.archive,
    threads.metadata,
    threads.thread_messages_range,
    threads.visual_message_info
    from messages, threads
    where messages.thread_id = threads.thread_id
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    
    if usageentries > 0:
        for row in all_rows:
            plist = ''
            senderpk =''
            serverTimestamp = ''
            message = ''
            videoChatTitle = ''
            videoChatCallID = ''
            dmreaction = ''
            reactionServerTimestamp = ''
            reactionUserID = ''
            sharedMediaID = ''
            sharedMediaURL = ''
            
            plist_file_object = io.BytesIO(row[2])
            if row[2].find(b'NSKeyedArchiver') == -1:
                if sys.version_info >= (3, 9):
                    plist = plistlib.load(plist_file_object)
                else:
                    plist = biplist.readPlist(plist_file_object)
            else:
                try:
                    plist = nd.deserialize_plist(plist_file_object)                    
                except (nd.DeserializeError, nd.biplist.NotBinaryPlistException, nd.biplist.InvalidPlistException,
                        nd.plistlib.InvalidFileException, nd.ccl_bplist.BplistError, ValueError, TypeError, OSError, OverflowError) as ex:
                    logfunc(f'Failed to read plist for {row[2]}, error was:' + str(ex))
                
            #Messages
            senderpk = plist['IGDirectPublishedMessageMetadata*metadata']['NSString*senderPk']
            serverTimestamp = plist['IGDirectPublishedMessageMetadata*metadata']['NSDate*serverTimestamp']
            message = plist['IGDirectPublishedMessageContent*content'].get('NSString*string')
            
            #VOIP calls
            if plist['IGDirectPublishedMessageContent*content'].get('IGDirectThreadActivityAnnouncement*threadActivity') is not None:
                videoChatTitle = plist['IGDirectPublishedMessageContent*content']['IGDirectThreadActivityAnnouncement*threadActivity']['NSString*voipTitle']
                videoChatCallID = plist['IGDirectPublishedMessageContent*content']['IGDirectThreadActivityAnnouncement*threadActivity']['NSString*videoCallId']
                
                
            #Reactions
            reactions = (plist['NSArray<IGDirectMessageReaction *>*reactions'])
            if reactions:
                dmreaction = reactions[0].get('emojiUnicode')
                reactionServerTimestamp = reactions[0].get('serverTimestamp')
                reactionUserID = reactions[0].get('userId')
                
            #Shared media
            if (plist['IGDirectPublishedMessageContent*content'].get('IGDirectPublishedMessageMedia*media')): 
                sharedMediaID = plist['IGDirectPublishedMessageContent*content']['IGDirectPublishedMessageMedia*media']['IGDirectPublishedMessagePermanentMedia*permanentMedia']['IGPhoto*photo']['kIGPhotoMediaID']
                sharedMediaURL =  plist['IGDirectPublishedMessageContent*content']['IGDirectPublishedMessageMedia*media']['IGDirectPublishedMessagePermanentMedia*permanentMedia']['IGPhoto*photo']['imageVersions'][0]['url']['NS.relative']
                
            if senderpk in userdict:
                user = userdict[senderpk]
            else:
                user = ''
                
            data_list.append((serverTimestamp, senderpk, user, message, videoChatTitle, videoChatCallID, dmreaction, reactionServerTimestamp, reactionUserID, sharedMediaID, sharedMediaURL))
            if videoChatTitle:
                video_calls.append((serverTimestamp, senderpk, user, videoChatTitle, videoChatCallID))

        description = 'Instagram Threads'
        report = ArtifactHtmlReport('Instagram Threads')
        report.start_artifact_report(report_folder, 'Instagram Threads', description)
        report.add_script()
        data_headers = ('Timestamp', 'Sender ID', 'Username', 'Message', 'Video Chat Title', 'Video Chat ID', 'DM Reaction', 'DM Reaction Server Timestamp', 'Reaction User ID', 'Shared Media ID', 'Shared Media URL')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Instagram Threads'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Instagram Threads'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Instagram Threads data available')
        
    if len(video_calls) > 0:
        description = 'Instagram Threads Calls'
        report = ArtifactHtmlReport('Instagram Threads Calls')
        report.start_artifact_report(report_folder, 'Instagram Threads Calls', description)
        report.add_script()
        data_headersv = ('Timestamp', 'Sender ID', 'Username',  'Video Chat Title', 'Video Chat ID')
        report.write_artifact_data_table(data_headersv, video_calls, file_found)
        report.end_artifact_report()
        
        tsvname = 'Instagram Threads Calls'
        tsv(report_folder, data_headersv, video_calls, tsvname)
        
        tlactivity = 'Instagram Threads Calls'
        timeline(report_folder, tlactivity, video_calls, data_headersv)
    
    else:
        logfunc('No Instagram Threads Video Calls data available')
        
    db.close()
    

        
        