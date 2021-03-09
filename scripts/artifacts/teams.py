import sqlite3
import io
import json
import os
import re
import shutil
import datetime
import nska_deserialize as nd
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, kmlgen, tsv, is_platform_windows, open_sqlite_db_readonly


def get_teams(files_found, report_folder, seeker):
    CacheFile = 0
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            databasedata = file_found
        if file_found.endswith('CacheFile'):
            CacheFile = file_found
    
    if CacheFile != 0:
        with open(CacheFile ,'rb') as nsfile:
            nsplist = nd.deserialize_plist(nsfile)
    
    db = open_sqlite_db_readonly(databasedata)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime('2001-01-01', "ZARRIVALTIME" || ' seconds'),
    ZIMDISPLAYNAME,
    ZCONTENT
    from ZSMESSAGE
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []  
    
    if usageentries > 0:
        for row in all_rows:
            thumb =''
            if '<div><img src=' in row[2]:
                matches = re.search('"([^"]+)"',row[2])
                imageURL = (matches[0].strip('\"'))
                if imageURL in nsplist.keys():
                    data_file_real_path = nsplist[imageURL]
                    for match in files_found:
                        if data_file_real_path in match:
                            shutil.copy2(match, report_folder)
                            data_file_name = os.path.basename(match)
                            thumb = f'<img src="{report_folder}/{data_file_name}"></img>'
            data_list.append((row[0], row[1], row[2], thumb))

        description = 'Teams Messages'
        report = ArtifactHtmlReport('Teams Messages')
        report.start_artifact_report(report_folder, 'Teams Messages', description)
        report.add_script()
        data_headers = ('Timestamp', 'Name', 'Message', 'Shared Media')
        report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Shared Media']
)
        report.end_artifact_report()
        
        tsvname = 'Microsoft Teams Messages'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Microsoft Teams Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Microsoft Teams Messages data available')
    
    cursor.execute('''
    SELECT
    ZDISPLAYNAME,
    zemail,
    ZPHONENUMBER
    from
    ZDEVICECONTACTHASH
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    
    if usageentries > 0:
        for row in all_rows:
            data_list.append((row[0], row[1], row[2]))
            
        description = 'Teams Contact'
        report = ArtifactHtmlReport('Teams Contact')
        report.start_artifact_report(report_folder, 'Teams Contact', description)
        report.add_script()
        data_headers = ('Display Name', 'Email', 'Phone Number')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Teams Contact'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('No Teams Contact data available')
    
    cursor.execute('''
    SELECT
    datetime('2001-01-01', "ZTS_LASTSYNCEDAT" || ' seconds'),
    ZDISPLAYNAME,
    ZTELEPHONENUMBER
    from zuser
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    
    if usageentries > 0:
        for row in all_rows:
            data_list.append((row[0], row[1], row[2]))
            
        description = 'Teams User'
        report = ArtifactHtmlReport('Teams User')
        report.start_artifact_report(report_folder, 'Teams User', description)
        report.add_script()
        data_headers = ('Timestamp Last Sync', 'Display Name', 'Phone Number')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Microsoft Teams User'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Microsoft Teams User'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Teams User data available')
        
    cursor.execute('''
    SELECT
    ZCOMPOSETIME,
    zfrom,
    ZIMDISPLAYNAME,
    zcontent,
    ZPROPERTIES
    from ZSMESSAGE, ZMESSAGEPROPERTIES
    where ZSMESSAGE.ZTSID = ZMESSAGEPROPERTIES.ZTSID
    order by ZCOMPOSETIME
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list_calls = []
    data_list_cards = []
    data_list_unparsed = []
    
    if usageentries > 0:
        for row in all_rows:
            plist = ''
            composetime = row[0].replace('T',' ')
            plist_file_object = io.BytesIO(row[4])
            if row[4].find(b'NSKeyedArchiver') == -1:
                if sys.version_info >= (3, 9):
                    plist = plistlib.load(plist_file_object)
                else:
                    plist = biplist.readPlist(plist_file_object)
            else:
                try:
                    plist = nd.deserialize_plist(plist_file_object)                    
                except (nd.DeserializeError, nd.biplist.NotBinaryPlistException, nd.biplist.InvalidPlistException,
                        nd.plistlib.InvalidFileException, nd.ccl_bplist.BplistError, ValueError, TypeError, OSError, OverflowError) as ex:
                    logfunc(f'Failed to read plist for {row[4]}, error was:' + str(ex))
            if 'call-log' in plist:
                datacalls = json.loads(plist['call-log'])
                callstart = (datacalls.get('startTime'))
                callstart = callstart.replace('T',' ')
                callconnect = (datacalls.get('connectTime'))
                callconnect = callconnect.replace('T',' ')
                callend = (datacalls['endTime'])
                callend = callend.replace('T',' ')
                calldirection = (datacalls['callDirection'])
                calltype = (datacalls['callType'])
                callstate = (datacalls['callState'])
                calloriginator = (datacalls['originator'])
                calltarget = (datacalls['target'])
                calloriginatordname = (datacalls['originatorParticipant']['displayName'])
                callparticipantdname = (datacalls['targetParticipant']['displayName'])
                data_list_calls.append((composetime, row[1], row[2], row[3], callstart, callconnect, callend, calldirection, calltype, callstate, calloriginator, calltarget, calloriginatordname, callparticipantdname))
            elif 'cards' in plist:
                cards = json.loads(plist['cards'])
                cardurl = (cards[0]['content']['body'][0]['selectAction']['url'])
                cardtitle = (cards[0]['content']['body'][0]['selectAction']['title'])
                cardtext = (cards[0]['content']['body'][1]['text'])
                cardurl2 = (cards[0]['content']['body'][0]['url'])
                if (cards[0]['content']['body'][0].get('id')) is not None:
                    idcontent = json.loads(cards[0]['content']['body'][0]['id'])
                    cardlat = (idcontent.get('latitude'))
                    cardlong = (idcontent.get('longitude'))
                    cardexpires = (idcontent.get('expiresAt'))
                    cardexpires  = datetime.datetime.fromtimestamp(cardexpires  / 1000)
                    carddevid = (idcontent.get('deviceId'))
                data_list_cards.append((composetime, row[1], row[2], row[3], cardurl, cardtitle, cardtext, cardurl2, cardlat, cardlong, cardexpires, carddevid))
            else:
                data_list_unparsed.append(composetime, row[1], row[2], row[3], plist)
                
        description = 'Microsoft Teams Call Logs'
        report = ArtifactHtmlReport('Microsoft Teams Call Logs')
        report.start_artifact_report(report_folder, 'Teams Call Logs', description)
        report.add_script()
        data_headers = ('Compose Timestamp', 'From', 'Display Name', 'Content',' Call Start', 'Call Connect', 'Call End', 'Call Direction', 'Call Type', 'Call State', 'Call Originator', 'Call Target', 'Call Originator Name', 'Call Participant Name')
        report.write_artifact_data_table(data_headers, data_list_calls, file_found)
        report.end_artifact_report()
        
        tsvname = 'Microsoft Teams Call Logs'
        tsv(report_folder, data_headers, data_list_calls, tsvname)
        
        tlactivity = 'Microsoft Teams Call Logs'
        timeline(report_folder, tlactivity, data_list_calls, data_headers)
        
        description = 'Microsoft Teams Shared Locations'
        report = ArtifactHtmlReport('Microsoft Teams Shared Locations')
        report.start_artifact_report(report_folder, 'Teams Shared Locations', description)
        report.add_script()
        data_headers = ('Timestamp', 'From', 'Display Name', 'Content','Card URL', 'Card Title', 'Card Text', 'Card URL2', 'Latitude', 'Longitude', 'Card Expires', 'Device ID')
        report.write_artifact_data_table(data_headers, data_list_cards, file_found)
        report.end_artifact_report()
        
        tsvname = 'Microsoft Teams Shared Locations'
        tsv(report_folder, data_headers, data_list_cards, tsvname)
        
        tlactivity = 'Microsoft Teams Shared Locations'
        timeline(report_folder, tlactivity, data_list_cards, data_headers)
        
        kmlactivity = 'Microsoft Teams Shared Locations'
        kmlgen(report_folder, kmlactivity, data_list_cards, data_headers)
        
    else:
        logfunc('No Microsoft Teams Call Logs & Cards data available')
        
    
    db.close()
    

        
        