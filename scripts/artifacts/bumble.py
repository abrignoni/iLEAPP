# Module Description: Parses Bumble chat messages and some local user account details
# Author: @KevinPagano3
# Date: 2022-04-16
# Artifact version: 0.0.1
# Requirements: none

import datetime
import io
import nska_deserialize as nd
import sqlite3
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, kmlgen, tsv, is_platform_windows, open_sqlite_db_readonly


def get_bumble(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('Chat.sqlite'):
            chat_db = file_found
        if file_found.endswith('yap-database.sqlite'):
            account_db = file_found
        
    db = open_sqlite_db_readonly(chat_db)
    cursor = db.cursor()
    cursor.execute('''
    select
    database2.data,
    case secondaryIndex_isReadIndex.isIncoming
        when 0 then 'Outgoing'
        when 1 then 'Incoming'
    end as "Direction",
    case secondaryIndex_isReadIndex.isRead
        when 0 then ''
        when 1 then 'Yes'
    end as "Message Read"
    from database2
    join secondaryIndex_isReadIndex on database2.rowid = secondaryIndex_isReadIndex.rowid
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    bumble_datecreated = ''
    bumble_datemodified = ''
    bumble_message = ''
    bumble_receiver = ''
    bumble_sender = ''
    
    if usageentries > 0:
        for row in all_rows:

            plist_file_object = io.BytesIO(row[0])
            if row[0] is None:
                pass
            else:
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
                  
            if 'self.dateCreated' in plist:
                bumble_datecreated = datetime.datetime.utcfromtimestamp(plist['self.dateCreated'])
                bumble_datemodified = datetime.datetime.utcfromtimestamp(plist['self.dateModified'])
                bumble_sender = plist.get('self.fromPersonUid','')
                bumble_receiver = plist.get('self.toPersonUid','')
                bumble_message = plist.get('self.messageText','')
            
                data_list.append((bumble_datecreated, bumble_datemodified, bumble_sender, bumble_receiver, bumble_message, row[1], row[2]))
            else: pass
                
        description = 'Bumble - Messages'
        report = ArtifactHtmlReport('Bumble - Messages')
        report.start_artifact_report(report_folder, 'Bumble - Messages')
        report.add_script()
        data_headers = (
            'Created Timestamp','Modified Timestamp','Sender ID','Receiver ID','Message','Message Direction','Message Read')  # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        
        report.write_artifact_data_table(data_headers, data_list, chat_db)
        report.end_artifact_report()
        
        tsvname = f'Bumble - Messages'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Bumble - Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('Bumble - Messages data available')
    
    db = open_sqlite_db_readonly(account_db)
    cursor = db.cursor()
    cursor.execute('''
    select
    data,
    key
    from database2
    where key = 'lastLocation' or key = 'appVersion' or key = 'userName' or key = 'userId'
    ''')
    
    all_rows1 = cursor.fetchall()
    usageentries = len(all_rows1)
    data_list_account = []
    
    if usageentries > 0:
        for row in all_rows1:

            plist_file_object = io.BytesIO(row[0])
            if row[0] is None:
                pass
            else:
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
            
            if row[1] == 'userId':
                bumble_userId = plist.get('root','')
                data_list_account.append(('User ID',str(bumble_userId)))
                
            elif row[1] == 'userName':
                bumble_userName = plist.get('root','')
                data_list_account.append(('User Name',str(bumble_userName)))
                
            elif row[1] == 'lastLocation':
                bumble_timestamp = datetime.datetime.utcfromtimestamp(int(plist['kCLLocationCodingKeyTimestamp']) + 978307200)
                bumble_lastlat = plist.get('kCLLocationCodingKeyRawCoordinateLatitude','')
                bumble_lastlong = plist.get('kCLLocationCodingKeyRawCoordinateLongitude','') 
                
                data_list_account.append(('Timestamp',str(bumble_timestamp)))
                data_list_account.append(('Last Latitude',bumble_lastlat))
                data_list_account.append(('Last Longitude',bumble_lastlong))
                
            elif row[1] == 'appVersion':
                bumble_appVersion = plist.get('root','')
                data_list_account.append(('App Version',str(bumble_appVersion)))
            
            else: pass
            
        description = 'Bumble - Account Details'
        report = ArtifactHtmlReport('Bumble - Account Details')
        report.start_artifact_report(report_folder, 'Bumble - Account Details')
        report.add_script()
        data_headers_account = (
            'Key', 'Values')  # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        
        report.write_artifact_data_table(data_headers_account, data_list_account, account_db)
        report.end_artifact_report()
        
        tsvname = f'Bumble - Account Details'
        tsv(report_folder, data_headers_account, data_list_account, tsvname)
        
        tlactivity = f'Bumble - Account Details'
        timeline(report_folder, tlactivity, data_list_account, data_headers_account)
        
    else:
        logfunc('No Bumble - Account Details data available')
    
    db.close()

__artifacts__ = {
    "bumble": (
        "Bumble",
        ('**/Library/Caches/Chat.sqlite*','**/Documents/yap-database.sqlite*'),
        get_bumble)
}