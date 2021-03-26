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


def get_whatsappMessages(files_found, report_folder, seeker):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            break
    data_list =[]
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select
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
    ZXMPPTHUMBPATH
    FROM ZWAMESSAGE
    left JOIN ZWAMEDIAITEM
    on ZWAMESSAGE.Z_PK = ZWAMEDIAITEM.ZMESSAGE 
    left JOIN ZWACHATSESSION
    on ZWACHATSESSION.Z_PK = ZWAMESSAGE.ZCHATSESSION
    ''')
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    
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
            
            
            if attachment is not None:
                for match in files_found:
                    if attachment in match:
                        shutil.copy2(match, report_folder)
                        data_file_name = os.path.basename(match)
                        thumb = f'<img src="{report_folder}/{data_file_name}"></img>'
            else:
                thumb = ''
                
            
            if attfile is not None:
                for matchf in files_found:
                    if attfile in matchf:
                        shutil.copy2(matchf, report_folder)
                        data_file_namef = os.path.basename(matchf)
                        attfile = f'<img src="{report_folder}/{data_file_namef}" width="300"></img>'
            else:
                attfile = ''
                    
            data_list.append((row[0], sender, row[3], receiver, row[4], row[6], attfile, thumb, localpath,row[7], lat, lon,))
            
        
        
        description = 'Whatsapp - Messages'
        report = ArtifactHtmlReport('Whatsapp - Messages')
        report.start_artifact_report(report_folder, 'Whatsapp - Messages')
        report.add_script()
        data_headers = (
            'Timestamp', 'Sender Name', 'From ID', 'Receiver', 'To ID', 'Message', 
            'Attachment File', 'Thumb','Attachment Local Path','Starred?', 'Latitude', 'Longitude',)  # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()    
        
        
        tsvname = f'Whatsapp - Messages'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Whatsapp - Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
        kmlactivity = 'Whatsapp - Messages'
        kmlgen(report_folder, kmlactivity, data_list, data_headers)
        
    else:
        logfunc('Whatsapp - Messages data available')
        
    