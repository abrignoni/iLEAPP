import sqlite3
import io
import json
import os
import shutil
import nska_deserialize as nd
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, kmlgen, tsv, is_platform_windows, open_sqlite_db_readonly


def get_imoHD_Chat(files_found, report_folder, seeker):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            break
        
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select
    case ZIMOCHATMSG.ZTS
        when 0 then ''
        else datetime(ZTS/1000000000,'unixepoch')
    end  as "Timestamp",
    ZIMOCONTACT.ZDISPLAY as "Sender Display Name",
    ZIMOCHATMSG.ZALIAS as "Sender Alias",
    ZIMOCONTACT.ZDIGIT_PHONE,
    ZIMOCHATMSG.ZTEXT as "Message",
    case ZIMOCHATMSG.ZISSENT
        when 0 then 'Received'
        when 1 then 'Sent'
    end as "Message Status",
    ZIMOCHATMSG.ZIMDATA
    from ZIMOCHATMSG
    left join ZIMOCONTACT ON ZIMOCONTACT.ZBUID = ZIMOCHATMSG.ZA_UID
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    
    if usageentries > 0:
        for row in all_rows:
            
            plist = ''
            timestamp = row[0]
            senderName = row[1]
            senderAlias = row[2]
            senderPhone = row[3]
            message = row[4]
            messageStatus = row[5]
            itemAction = ''
            attachmentURL = ''
            thumb = ''
            
            plist_file_object = io.BytesIO(row[6])
            if row[6] is None:
                pass
            else:
                if row[6].find(b'NSKeyedArchiver') == -1:
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
                    
                itemAction = plist['type']
                logfunc(itemAction)
                
                #Check for Attachments
                if plist.get('objects') is not None:
                    attachmentName = plist['objects'][0]['object_id']
                    attachmentURL = "https://cdn.imoim.us/s/object/" + attachmentName + "/"
                    
                    for match in files_found:
                        if attachmentName in match:
                            shutil.copy2(match, report_folder)
                            data_file_name = os.path.basename(match)
                            thumb = f'<img src="{report_folder}/{data_file_name}"></img>'
                    
                else:
                    attachmentURL = ''
                    
            data_list.append((timestamp, senderName, senderAlias, senderPhone, message, messageStatus, itemAction, attachmentURL, thumb))
        
        description = 'IMO HD Chat - Messages'
        report = ArtifactHtmlReport('IMO HD Chat - Messages')
        report.start_artifact_report(report_folder, 'IMO HD Chat - Messages')
        report.add_script()
        data_headers = (
            'Timestamp', 'Sender Name', 'Sender Alias', 'Sender Phone', 'Message', 'Message Status', 'Item Action',
            'Attachment URL', 'Attachment')  # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        
        report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Attachment'])
        report.end_artifact_report()
        
        tsvname = f'IMO HD Chat - Messages'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'IMO HD Chat - Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('IMO HD Chat - Messages data available')
        
    cursor.execute('''
    select
    ZPH_NAME,
    ZALIAS,
    ZPHONE,
    "https://cdn.imoim.us/s/object/" || ZICON_ID || "/" as "Profile Pic",
    ZBUID
    from ZIMOCONTACT
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        description = 'IMO HD Chat - Contacts'
        report = ArtifactHtmlReport('IMO HD Chat - Contacts')
        report.start_artifact_report(report_folder, 'IMO HD Chat - Contacts')
        report.add_script()
        data_headers = ('Contact Name','Contact Alias','Contact Phone','Profile Pic URL','User ID') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'IMO HD Chat - Contacts'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'IMO HD Chat - Contacts'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('IMO HD Chat - Contacts data available')
        
    db.close()