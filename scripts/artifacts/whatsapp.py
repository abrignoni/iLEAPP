__artifacts_v2__ = {
    "whatsappCallHistory": {
        "name": "Whatsapp Call History",
        "description": "Whatsapp call history extractor",
        "author": "@Vinceckert",
        "version": "1.0.0",
        "date": "2024-05-31",
        "requirements": "none",
        "category": "Whatsapp",
        "notes": "",
        "paths": (
            '*/mobile/Containers/Shared/AppGroup/*/CallHistory.sqlite*',
            '*/mobile/Containers/Shared/AppGroup/*/ContactsV2.sqlite*',
        ),
        "artifact_icon": "phone-call",
        "function": "get_whatsappCallHistory"
    },
    "whatsappMessages": {
        "name": "Whatsapp Messages",
        "description": "",
        "author": "",
        "version": "",
        "date": "",
        "requirements": "",
        "category": "Whatsapp",
        "notes": "",
        "paths": (
            '*/mobile/Containers/Shared/AppGroup/*/ChatStorage.sqlite*',
            '*/mobile/Containers/Shared/AppGroup/*/Message/Media/*/*/*/*.*'
        ),
        "function": "get_whatsappMessages"
    },
    "whatsappContacts": {
        "name": "Whatsapp Contacts",
        "description": "",
        "author": "",
        "version": "",
        "date": "",
        "requirements": "",
        "category": "Whatsapp",
        "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/ContactsV2.sqlite*',),
        "function": "get_whatsappContacts"
    }
}


# import sqlite3
# import io
# import json
import os
import shutil
import nska_deserialize as nd
import scripts.artifacts.artGlobals
import blackboxprotobuf

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import artifact_processor, logfunc, tsv, is_platform_windows, open_sqlite_db_readonly, attach_sqlite_db_readonly, logdevinfo, timeline, kmlgen

@artifact_processor
def get_whatsappCallHistory(files_found, report_folder, seeker, wrap_text, timezone_offset):

    CallHistory_db = ""
    ContactsV2_db = ""

    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('CallHistory.sqlite'):
            CallHistory_db = file_found
        elif file_found.endswith('ContactsV2.sqlite'):
            ContactsV2_db = file_found

    data_list =[]

    if CallHistory_db and not ContactsV2_db:
        db = open_sqlite_db_readonly(CallHistory_db)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(ZWACDCALLEVENT.ZDATE+978307200,'unixepoch') as Datetime_begin,
        CASE
            WHEN ((datetime(ZWACDCALLEVENT.ZDATE+978307200,'unixepoch')) = (datetime(((ZWACDCALLEVENT.ZDATE) + (ZWACDCALLEVENT.ZDURATION))+978307200,'unixepoch'))) then 'No Call Duration'
            ELSE (datetime(((ZWACDCALLEVENT.ZDATE) + (ZWACDCALLEVENT.ZDURATION))+978307200,'unixepoch'))
        END Datetime_end, 
        time(ZWACDCALLEVENT.ZDURATION+978307200,'unixepoch') as Duration,
        CASE
            WHEN ZWACDCALLEVENT.ZGROUPCALLCREATORUSERJIDSTRING = ZWACDCALLEVENTPARTICIPANT.ZJIDSTRING then "Incoming" 
            ELSE "Outgoing"
        END Direction,
        CASE ZWACDCALLEVENT.ZOUTCOME
            WHEN 0 THEN 'Ended'
            WHEN 1 THEN 'Missed'
            WHEN 4 THEN 'Rejected'
            ELSE ZWACDCALLEVENT.ZOUTCOME
        END Disconnected_cause,
        ZWACDCALLEVENTPARTICIPANT.ZJIDSTRING as 'Contact ID'
        FROM ZWACDCALLEVENT, ZWACDCALLEVENTPARTICIPANT
        WHERE ZWACDCALLEVENT.Z1CALLEVENTS = ZWACDCALLEVENTPARTICIPANT.Z1PARTICIPANTS
        ''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))

            description = 'Whatsapp - Call History'
            report = ArtifactHtmlReport(description)
            report.start_artifact_report(report_folder, 'Whatsapp - Call History')
            report.add_script()
            data_headers = (
                'Starting Timestamp', 'Ending Timestamp', 'Duration H:M:S', 'Direction', 'Disconnected cause', 'Contact ID')
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()    
            
            tsv(report_folder, data_headers, data_list, description)
        else:
            logfunc('Whatsapp - Call History data available')

    if CallHistory_db and ContactsV2_db:
        db_CallHistory = open_sqlite_db_readonly(CallHistory_db)
        cursor = db_CallHistory.cursor()
        # To avoid modifying the code too much, I'm working on the path string
        if is_platform_windows():
            ContactsV2_db = ContactsV2_db.split('?\\')[1]
        # Attach ContactsV2 database in read only for contact information number and name
        attach_query = attach_sqlite_db_readonly(ContactsV2_db, 'ContactsV2')
        cursor.execute(attach_query)
        cursor.execute('''
            SELECT
            datetime(ZWACDCALLEVENT.ZDATE+978307200,'unixepoch') as Datetime_begin,
            CASE
                WHEN ((datetime(ZWACDCALLEVENT.ZDATE+978307200,'unixepoch')) = (datetime(((ZWACDCALLEVENT.ZDATE) + (ZWACDCALLEVENT.ZDURATION))+978307200,'unixepoch'))) then 'No Call Duration'
                ELSE (datetime(((ZWACDCALLEVENT.ZDATE) + (ZWACDCALLEVENT.ZDURATION))+978307200,'unixepoch'))
            END Datetime_end, 
            time(ZWACDCALLEVENT.ZDURATION+978307200,'unixepoch') as Duration,
            CASE
                WHEN ZWACDCALLEVENT.ZGROUPCALLCREATORUSERJIDSTRING = ZWACDCALLEVENTPARTICIPANT.ZJIDSTRING then "Incoming" 
                ELSE "Outgoing"
            END Direction,
            CASE ZWACDCALLEVENT.ZOUTCOME
                WHEN 0 THEN 'Ended'
                WHEN 1 THEN 'Missed'
                WHEN 4 THEN 'Rejected'
                ELSE ZWACDCALLEVENT.ZOUTCOME
            END Disconnected_cause,
            ZWACDCALLEVENTPARTICIPANT.ZJIDSTRING as 'Contact ID',
            base2.ZFULLNAME,
            base2.ZPHONENUMBER
            FROM ZWACDCALLEVENT, ZWACDCALLEVENTPARTICIPANT
            INNER JOIN ContactsV2.ZWAADDRESSBOOKCONTACT base2 ON ZWACDCALLEVENTPARTICIPANT.ZJIDSTRING = base2.ZWHATSAPPID
            WHERE ZWACDCALLEVENT.Z1CALLEVENTS = ZWACDCALLEVENTPARTICIPANT.Z1PARTICIPANTS
        ''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        
        if usageentries > 0:
            for row in all_rows:                
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7] ))

            description = 'Whatsapp - Call History'
            report = ArtifactHtmlReport(description)
            report.start_artifact_report(report_folder, description)
            report.add_script()
            data_headers = (
                'Starting Timestamp', 'Ending Timestamp', 'Duration H:M:S', 'Direction', 'Disconnected cause', 'Contact ID', 'Contact Fullname', 'Phone Number')
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()            
            
            tsv(report_folder, data_headers, data_list, description)
        else:
            logfunc('Whatsapp - Call History data available')
    else:
        logfunc('Whatsapp - Call History data available')


@artifact_processor
def get_whatsappContacts(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            break
        
    data_list =[]
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    ZFULLNAME,
    ZABOUTTEXT,
    datetime(ZABOUTTIMESTAMP+978307200, 'UNIXEPOCH'),
    ZPHONENUMBER,
    ZPHONENUMBERLABEL,
    ZWHATSAPPID,
    ZIDENTIFIER
    FROM ZWAADDRESSBOOKCONTACT
    ''')
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    
    if usageentries > 0:
        for row in all_rows:            
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5],row[6]))

        description = 'Whatsapp - Contacts'
        report = ArtifactHtmlReport(description)
        report.start_artifact_report(report_folder, description)
        report.add_script()
        data_headers = (
            'Fullname', 'About Text', 'About Text Timestamp', 'Phone Number', 'Phone Number Label', 'Whatsapp ID', 'Identifier')
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()    
        
        tsv(report_folder, data_headers, data_list, description)
        
    else:
        logfunc('Whatsapp - Contacts data available')


@artifact_processor
def get_whatsappMessages(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            break
    data_list =[]
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime(ZMESSAGEDATE+978307200, 'UNIXEPOCH'),
    ZISFROMME,
    ZPARTNERNAME,
    ZFROMJID,
    ZTOJID,
    ZWAMESSAGE.ZMEDIAITEM,
    ZTEXT,
    ZSTARRED,
    ZMESSAGETYPE,
    ZLONGITUDE,
    ZLATITUDE,
    ZMEDIALOCALPATH,
    ZXMPPTHUMBPATH,
    ZMETADATA,
    ZVCARDSTRING
    FROM ZWAMESSAGE
    left JOIN ZWAMEDIAITEM
    ON ZWAMESSAGE.Z_PK = ZWAMEDIAITEM.ZMESSAGE 
    left JOIN ZWACHATSESSION
    ON ZWACHATSESSION.Z_PK = ZWAMESSAGE.ZCHATSESSION
    ''')
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    thumb = ''
    
    if usageentries > 0:
        for row in all_rows:

            if row[1] == 1:
                sender = 'Local User'
                receiver = row[2]
            else:
                sender = row[2]
                receiver = 'Local User'

            if row[8] == 5:
                lon = row[9]
                lat = row[10]
            else:
                lat = ''
                lon = ''

            attfile = row[11]
            attachment = row[12]
            localpath = row[11]

            metadata = row[13]
            attfiletype = row[14]

            if metadata is not None:
                number_forward = ''
                from_forward = ''
                decoded_data, _ = blackboxprotobuf.decode_message(row[13])

                number_forwardings = decoded_data.get("17")
                from_forwaded = decoded_data.get("21")
                if number_forwardings is not None:
                    number_forward = f'{number_forwardings}'
                if from_forwaded is not None:
                    from_forward = f"{from_forwaded.decode('utf-8')}"
            else:
                number_forward = ''
                from_forward = ''

            if attachment is not None:
                attachment = os.path.normpath(attachment)
                for match in files_found:
                    if attachment in match:
                        shutil.copy2(match, report_folder)
                        data_file_name = os.path.basename(match)
                        rel_path = os.path.basename(report_folder)
                        thumb = f'<img src="./{rel_path}/{data_file_name}"></img>'
            else:
                thumb = ''

            if attfile is not None:
                attfile = os.path.normpath(attfile)
                for matchf in files_found:
                    if attfile in matchf:
                        shutil.copy2(matchf, report_folder)
                        data_file_namef = os.path.basename(matchf)
                        rel_path = os.path.basename(report_folder)
                        if(attfiletype.split("/")[0] == "video" ):
                            attfile = f'<video controls style="max-width:300px;"><source src="./{rel_path}/{data_file_namef}" type="{attfiletype}">'
                            if(len(thumb) > 0):
                                previewthumb = thumb
                            if(len(thumb) == 0):
                                previewthumb = 'videofile'
                            attfile += f'<a href="./{rel_path}/{data_file_namef}" target="_blank" title="open {attfiletype.split("/")[0]} file in a new tab">{previewthumb}</a>'
                            attfile += '</video>'
                        if(attfiletype.split("/")[0] == "image"):
                            attfile = f'<a href="./{rel_path}/{data_file_namef}" target="_blank" title="open {attfiletype.split("/")[0]} file in a new tab"><img src="./{rel_path}/{data_file_namef}" style="max-width:300px"></img></a>'
                        if(attfiletype.split("/")[0] == "audio"):
                            attfile = f'<audio controls  style="max-width:300px;""><source src="./{rel_path}/{data_file_namef}" type="{attfiletype}">'
                            attfile += f'<a href="./{rel_path}/{data_file_namef}" target="_blank" title="open {attfiletype.split("/")[0]} file in a new tab">{attfiletype.split("/")[0]}</a>'
                            attfile += '</audio>'
            else:
                attfile = ''

            data_list.append((row[0], sender, row[3], receiver, row[4], row[6], attfile, thumb, localpath, row[7], number_forward, from_forward, lat, lon,))

        
        description = 'Whatsapp - Messages'
        report = ArtifactHtmlReport(description)
        report.start_artifact_report(report_folder, description)
        report.add_script()
        data_headers = (
            'Timestamp', 'Sender Name', 'From ID', 'Receiver', 'To ID', 'Message', 
            'Attachment File', 'Thumb','Attachment Local Path','Starred?', 'Number of Forwardings', 'Forwarded from',  'Latitude', 'Longitude',)  # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()

        tsv(report_folder, data_headers, data_list, description)
        
        timeline(report_folder, description, data_list, data_headers)
        
        kmlgen(report_folder, description, data_list, data_headers)
        
    else:
        logfunc('Whatsapp - Messages data available')
