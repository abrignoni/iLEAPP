__artifacts_v2__ = {
    "wire": {
        "name": "Wire Artifacts",
        "description": "Get Wire",
        "author": "Elliot Glendye",
        "version": "0.0.1",
        "date": "2024-01-17",
        "requirements": "",
        "category": "Wire",
        "notes": "No notes at present.",
        "paths": ('**/store.wiredatabase*'),
        "function": "get_wire"
    }
}

import scripts.artifacts.artGlobals
import sqlite3
from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, open_sqlite_db_readonly

def get_wire(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        iOSversion = scripts.artifacts.artGlobals.versionf
        if version.parse(iOSversion) < version.parse('15'):
            logfunc('Wire parsing has not been tested on iOS version ' + iOSversion)
        
        if file_found.endswith('store.wiredatabase'):
            break
        
        else:
            continue
        
    db = open_sqlite_db_readonly(file_found)
    
    account_query = ('''
    SELECT DISTINCT
        ZUSER.ZHANDLE AS 'User ID',
        ZUSER.ZNAME AS 'Display Name',
        datetime(ZUSERCLIENT.ZACTIVATIONDATE + 978307200, 'unixepoch') AS 'Activation Date',
        ZUSER.ZPHONENUMBER AS 'Phone Number',
        ZUSER.ZEMAILADDRESS AS 'Email Address',
        ZUSERCLIENT.ZACTIVATIONLOCATIONLATITUDE AS 'Activation Latitude',
        ZUSERCLIENT.ZACTIVATIONLOCATIONLONGITUDE AS 'Activation Longitude'
    FROM ZUSER
        LEFT JOIN ZUSERCLIENT ON ZUSER.Z_PK = ZUSERCLIENT.ZUSER;
    ''')

    cursor = db.cursor()
    cursor.execute(account_query)
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    print(data_list)
    
    if usageentries > 0:
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
            
            description = 'A report of Wire account details.'
        
            report = ArtifactHtmlReport('Wire Account')
            report.start_artifact_report(report_folder, 'Wire Account', description)
            report.add_script()
            data_headers = ('User ID', 'Display Name', 'Activation Date', 'Phone Number', 'Email Address', 'Activation Latitude', 'Activation Longitude')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
        
            tsvname = 'Wire Account'
            tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('No Wire account details present')
    
    
    message_query = ('''
    SELECT
        datetime(ZMESSAGE.ZSERVERTIMESTAMP + 978307200, 'unixepoch') AS 'Date / Time',
        ZUSER.ZHANDLE AS 'User ID',
        ZUSER.ZNAME AS 'Display Name',
        ZMESSAGE.ZNORMALIZEDTEXT AS 'Message',
        CASE ZMESSAGE.ZCACHEDCATEGORY
            WHEN 0 THEN 'Audio / Video Call'
            WHEN 2 THEN 'Text Message'
            WHEN 8 THEN 'Media Message'
            WHEN 256 THEN 'Location Message'
        END AS 'Message Type',
        ZMESSAGE.ZDURATION AS 'Call Duration (seconds)'
    FROM ZMESSAGE
        LEFT Join ZUSER On ZUSER.Z_PK = ZMESSAGE.ZSENDER
        WHERE ZMESSAGE.ZCACHEDCATEGORY != 1;
    ''')
    
    cursor = db.cursor()
    cursor.execute(message_query)
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    
    if usageentries > 0:
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))
            
            description = 'A report of Wire messages, including message sender, associated user identifiers and message type.'
        
            report = ArtifactHtmlReport('Wire Messages')
            report.start_artifact_report(report_folder, 'Wire Messages', description)
            report.add_script()
            data_headers = ('Date / Time', 'User ID', 'Display Name', 'Message', 'Message Type', 'Call Duration (seconds)')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
        
            tsvname = 'Wire Messages'
            tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('No Wire messages present')
   
    db.close()
    return