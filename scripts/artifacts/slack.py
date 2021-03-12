from os.path import dirname, join
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_slack(files_found, report_folder, seeker):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('main_db'):
            break
    
    deprecated = 0
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'") 
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    
    for row in all_rows:
        if 'ZSLKDEPRECATEDMESSAGE' in row[0]:
            deprecated = 1
            
    if deprecated == 1:
        squery = ('''
        select distinct
        datetime(ZSLKDEPRECATEDMESSAGE.ZTIMESTAMP, 'unixepoch') as MessageTimeStamp,
        ZSLKDEPRECATEDMESSAGE.ZUSERID as MessageGeneratedFrom,
        ZSLKDEPRECATEDCOREDATAUSER.ZREALNAME as MessageGeneratedFromName,
        ZSLKDEPRECATEDBASECHANNEL.ZNAME as MessageSentToChannelName,
        ZSLKDEPRECATEDMESSAGE.ZTEXT,
        json_extract(ZFILEIDS, '$[0]') as HasSharedFile,
        ZSLKDEPRECATEDMESSAGE.ZCHANNELID,
        ZSLKDEPRECATEDBASECHANNEL.ZTSID,
        ZSLKDEPRECATEDBASECHANNEL.ZTSID1,
        ZSLKDEPRECATEDCOREDATAUSER.ZTSID
        from ZSLKDEPRECATEDMESSAGE, ZSLKDEPRECATEDBASECHANNEL,ZSLKDEPRECATEDCOREDATAUSER
        where  ZSLKDEPRECATEDCOREDATAUSER.ZTSID = ZSLKDEPRECATEDMESSAGE.ZUSERID and 
        (ZSLKDEPRECATEDBASECHANNEL.ZTSID = ZSLKDEPRECATEDMESSAGE.ZCHANNELID or ZSLKDEPRECATEDBASECHANNEL.ZTSID1 = ZSLKDEPRECATEDMESSAGE.ZCHANNELID)
        order by ZSLKDEPRECATEDMESSAGE.ZTIMESTAMP
        ''')
    else:
        squery = ('''
        select distinct 
        datetime(ZSLKMESSAGE.ZTIMESTAMP, 'unixepoch') as MessageTimeStamp,
        ZSLKMESSAGE.ZUSERID as MessageGeneratedFrom,
        ZSLKCOREDATAUSER.ZREALNAME as MessageGeneratedFromName,
        ZSLKBASECHANNEL.ZNAME as MessageSentToChannelName,
        ZSLKMESSAGE.ZTEXT,
        json_extract(ZFILEIDS, '$[0]') as HasSharedFile,
        ZSLKMESSAGE.ZCHANNELID,
        ZSLKBASECHANNEL.ZTSID,
        ZSLKBASECHANNEL.ZTSID1,
        ZSLKCOREDATAUSER.ZTSID
        from ZSLKMESSAGE, ZSLKBASECHANNEL,ZSLKCOREDATAUSER
        where  ZSLKCOREDATAUSER.ZTSID = ZSLKMESSAGE.ZUSERID and 
        (ZSLKBASECHANNEL.ZTSID = ZSLKMESSAGE.ZCHANNELID or ZSLKBASECHANNEL.ZTSID1 = ZSLKMESSAGE.ZCHANNELID)
        order by ZSLKMESSAGE.ZTIMESTAMP
        ''')
        
    cursor.execute(squery) 
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    
    if usageentries > 0:
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9] ))
            
        description = 'Slack Messages'
        report = ArtifactHtmlReport('Slack Messages')
        report.start_artifact_report(report_folder, 'Slack Messages', description)
        report.add_script()
        data_headers = ('Timestamp', 'From', 'From Name', 'Channel Name', 'Message', 'Shared File', 'Channel ID','Channel SID', 'Channel SID1','User SID' )
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Slack Messages'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Slack Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Slack Messages data available')
        
    if deprecated == 1:
        squery = ('''
        select 
        ZSLKDEPRECATEDCOREDATAUSER.ZADMIN,
        ZSLKDEPRECATEDCOREDATAUSER.ZOWNER,
        ZSLKDEPRECATEDCOREDATAUSER.ZREALNAME,
        ZSLKDEPRECATEDCOREDATAUSER.ZFIRSTNAME,
        ZSLKDEPRECATEDCOREDATAUSER.ZLASTNAME,
        ZSLKDEPRECATEDCOREDATAUSER.ZDISPLAYNAME,
        ZSLKDEPRECATEDCOREDATAUSER.ZNAME,
        ZSLKDEPRECATEDCOREDATAUSER.ZPHONE,
        ZSLKDEPRECATEDCOREDATAUSER.ZTIMEZONE,
        ZSLKDEPRECATEDCOREDATAUSER.ZTIMEZONEOFFSET,
        ZSLKDEPRECATEDCOREDATAUSER.ZTIMEZONETITLE,
        ZSLKDEPRECATEDCOREDATAUSER.ZTITLE,
        ZSLKDEPRECATEDCOREDATAUSER.ZTSID,
        ZSLKDEPRECATEDCOREDATAUSER.ZTEAMID
        from ZSLKDEPRECATEDCOREDATAUSER
        ''')
    else:
        squery = ('''
        select 
        ZSLKCOREDATAUSER.ZADMIN,
        ZSLKCOREDATAUSER.ZOWNER,
        ZSLKCOREDATAUSER.ZREALNAME,
        ZSLKCOREDATAUSER.ZFIRSTNAME,
        ZSLKCOREDATAUSER.ZLASTNAME,
        ZSLKCOREDATAUSER.ZDISPLAYNAME,
        ZSLKCOREDATAUSER.ZNAME,
        ZSLKCOREDATAUSER.ZPHONE,
        ZSLKCOREDATAUSER.ZTIMEZONE,
        ZSLKCOREDATAUSER.ZTIMEZONEOFFSET,
        ZSLKCOREDATAUSER.ZTIMEZONETITLE,
        ZSLKCOREDATAUSER.ZTITLE,
        ZSLKCOREDATAUSER.ZTSID,
        ZSLKCOREDATAUSER.ZTEAMID
        from ZSLKCOREDATAUSER
        ''')
        
    cursor.execute(squery) 
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    
    if usageentries > 0:
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13] ))

        description = 'Slack User Data'
        report = ArtifactHtmlReport('Slack User Data')
        report.start_artifact_report(report_folder, 'Slack User Data', description)
        report.add_script()
        data_headers = ('Admin', 'Owner', 'Real Name', 'First Name', 'Last Name', 'Display Name', 'Name','Phone', 'Timezone','Timezone Offset', 'Timezone Title', 'Title', 'SID', 'Team ID' )
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Slack User Data'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('No Slack User data available')

    if deprecated == 1:
        squery = ('''
        select distinct
        datetime(ZSLKDEPRECATEDMESSAGE.ZTIMESTAMP, 'unixepoch') as MessageTimeStamp,   
        ZSLKDEPRECATEDMESSAGE.ZUSERID as MessageGeneratedFrom,
        ZSLKDEPRECATEDCOREDATAUSER.ZREALNAME as MessageGeneratedFromName,
        ZSLKDEPRECATEDBASECHANNEL.ZNAME as MessageSentToChannelName,
        ZSLKDEPRECATEDMESSAGE.ZTEXT,
        json_extract(ZFILEIDS, '$[0]') as HasSharedFile,
        ZSLKDEPRECATEDFILE.ZMODESTRING,
        ZSLKDEPRECATEDFILE.ZTITLE,
        ZSLKDEPRECATEDFILE.ZTYPESTRING,
        datetime(ZSLKDEPRECATEDFILE.ZTIMESTAMPNUMBER, 'unixepoch') as FileTimeStamp,
        ZSLKDEPRECATEDFILE.ZPREVIEW,
        ZSLKDEPRECATEDFILE.ZSIZE, 
        ZSLKDEPRECATEDFILE.ZPRIVATEDOWNLOADURL,
        ZSLKDEPRECATEDFILE.ZPERMALINKURL,  
        ZSLKDEPRECATEDMESSAGE.ZCHANNELID,
        ZSLKDEPRECATEDBASECHANNEL.ZTSID,
        ZSLKDEPRECATEDBASECHANNEL.ZTSID1,
        ZSLKDEPRECATEDCOREDATAUSER.ZTSID
        from ZSLKDEPRECATEDMESSAGE, ZSLKDEPRECATEDBASECHANNEL,ZSLKDEPRECATEDCOREDATAUSER, ZSLKDEPRECATEDFILE
        where  ZSLKDEPRECATEDCOREDATAUSER.ZTSID = ZSLKDEPRECATEDMESSAGE.ZUSERID and
        (ZSLKDEPRECATEDBASECHANNEL.ZTSID = ZSLKDEPRECATEDMESSAGE.ZCHANNELID or ZSLKDEPRECATEDBASECHANNEL.ZTSID1 = ZSLKDEPRECATEDMESSAGE.ZCHANNELID) and
        HasSharedFile = ZSLKDEPRECATEDFILE.ZTSID 
        order by ZSLKDEPRECATEDMESSAGE.ZTIMESTAMP
        ''')
    else:
        squery = ('''
        select distinct 
        datetime(ZSLKMESSAGE.ZTIMESTAMP, 'unixepoch') as MessageTimeStamp, 
        ZSLKMESSAGE.ZUSERID as MessageGeneratedFrom,
        ZSLKCOREDATAUSER.ZREALNAME as MessageGeneratedFromName,
        ZSLKBASECHANNEL.ZNAME as MessageSentToChannelName,
        ZSLKMESSAGE.ZTEXT,
        json_extract(ZFILEIDS, '$[0]') as HasSharedFile,
        ZSLKFILE.ZMODESTRING,
        ZSLKFILE.ZTITLE,
        ZSLKFILE.ZTYPESTRING,
        datetime(ZSLKFILE.ZTIMESTAMP, 'unixepoch') as FileTimeStamp,
        ZSLKFILE.ZPREVIEW,
        ZSLKFILE.ZSIZE, 
        ZSLKFILE.ZPRIVATEDOWNLOADURL,
        ZSLKFILE.ZPERMALINKURL,  
        ZSLKMESSAGE.ZCHANNELID,
        ZSLKBASECHANNEL.ZTSID,
        ZSLKBASECHANNEL.ZTSID1,
        ZSLKCOREDATAUSER.ZTSID
        from ZSLKMESSAGE, ZSLKBASECHANNEL,ZSLKCOREDATAUSER, ZSLKFILE
        where  ZSLKCOREDATAUSER.ZTSID = ZSLKMESSAGE.ZUSERID and
        (ZSLKBASECHANNEL.ZTSID = ZSLKMESSAGE.ZCHANNELID or ZSLKBASECHANNEL.ZTSID1 = ZSLKMESSAGE.ZCHANNELID) and
        HasSharedFile = ZSLKFILE.ZTSID 
        order by ZSLKMESSAGE.ZTIMESTAMP
        ''')
        
    cursor.execute(squery) 
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    
    if usageentries > 0:
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17] ))
            
        description = 'Slack Attachments'
        report = ArtifactHtmlReport('Slack Attachments')
        report.start_artifact_report(report_folder, 'Slack Attachments', description)
        report.add_script()
        data_headers = ('Timestamp', 'From', 'From Name', 'Channel Name', 'Message', 'Shared File', 'Mode', 'Title', 'Type', 'File Timestamp', 'Preview', 'Size', 'Private Download URL', 'Permalink URL', 'Channel ID','Channel SID', 'Channel SID1','User SID' )
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Slack Attachments'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Slack Attachments'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Slack User data available')
    
    if deprecated == 1:
        squery = ('''
        select
        datetime(ZSLKDEPRECATEDBASECHANNEL.ZCREATED, 'unixepoch') as CreatedTime,
        datetime(ZSLKDEPRECATEDBASECHANNEL.ZPURPOSELASTSET, 'unixepoch') as PurposeLastSet,
        datetime(ZSLKDEPRECATEDBASECHANNEL.ZTOPICLASTSET, 'unixepoch') as TopicLastSet,
        datetime(ZSLKDEPRECATEDBASECHANNEL.ZLATEST, 'unixepoch') as Latest,
        ZSLKDEPRECATEDBASECHANNEL.ZNAME as ChannelNames,
        ZSLKDEPRECATEDBASECHANNEL.ZTSID as DMChannels,
        ZSLKDEPRECATEDBASECHANNEL.ZTSID1 as OtherChannels,
        ZSLKDEPRECATEDBASECHANNEL.ZUSERID,
        ZSLKDEPRECATEDBASECHANNEL.ZCREATORID,
        ZSLKDEPRECATEDBASECHANNEL.ZPURPOSECREATORID,
        ZSLKDEPRECATEDBASECHANNEL.ZPURPOSETEXT,
        ZSLKDEPRECATEDBASECHANNEL.ZTOPICCREATORID,
        ZSLKDEPRECATEDBASECHANNEL.ZTOPICTEXT
        from ZSLKDEPRECATEDBASECHANNEL
        ''')
    else:
        squery = ('''
        select
        datetime(ZSLKBASECHANNEL.ZCREATED, 'unixepoch') as CreatedTime,
        datetime(ZSLKBASECHANNEL.ZPURPOSELASTSET, 'unixepoch') as PurposeLastSet,
        datetime(ZSLKBASECHANNEL.ZTOPICLASTSET, 'unixepoch') as TopicLastSet,
        datetime(ZSLKBASECHANNEL.ZLATEST, 'unixepoch') as Latest,
        ZSLKBASECHANNEL.ZNAME as ChannelNames,
        ZSLKBASECHANNEL.ZTSID as DMChannels,
        ZSLKBASECHANNEL.ZTSID1 as OtherChannels,
        ZSLKBASECHANNEL.ZUSERID,
        ZSLKBASECHANNEL.ZCREATORID,
        ZSLKBASECHANNEL.ZPURPOSECREATORID,
        ZSLKBASECHANNEL.ZPURPOSETEXT,
        ZSLKBASECHANNEL.ZTOPICCREATORID,
        ZSLKBASECHANNEL.ZTOPICTEXT
        from ZSLKBASECHANNEL
        ''')
        
    cursor.execute(squery) 
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    
    if usageentries > 0:
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12] ))
            
        description = 'Slack Channel Data'
        report = ArtifactHtmlReport('Slack Channel Data')
        report.start_artifact_report(report_folder, 'Slack Channel Data', description)
        report.add_script()
        data_headers = ('Timestamp Created', 'Purpose Last Set', 'Topic Last Set', 'Latest', 'Channel Names','DM Channels', 'Other Channels', 'User ID', 'Creator ID', 'Purpose Creator ID', 'Purpose Text', 'Topic Creator ID', 'Topic Text' )
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Slack Channel Data'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Slack Channel Data'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
        
    else:
        logfunc('No Slack Channel Data available')
        
    if deprecated == 1:
        squery = ('''
        select
        ZSLKDEPRECATEDTEAM.ZNAME,
        ZSLKDEPRECATEDTEAM.ZDOMAIN,
        ZSLKDEPRECATEDTEAM.ZAUTHUSERID,
        ZSLKDEPRECATEDTEAM.ZTSID
        from ZSLKDEPRECATEDTEAM
        ''')
    else:
        squery = ('''
        select
        ZSLKTEAM.ZNAME,
        ZSLKTEAM.ZDOMAIN,
        ZSLKTEAM.ZAUTHUSERID,
        ZSLKTEAM.ZTSID
        from ZSLKTEAM
        ''')
        
    cursor.execute(squery) 
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    
    if usageentries > 0:
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3] ))
            
        description = 'Slack Team Data'
        report = ArtifactHtmlReport('Slack Team Data')
        report.start_artifact_report(report_folder, 'Slack Team Data', description)
        report.add_script()
        data_headers = ('Name', 'Domain Name', 'Author User ID', 'SID' )
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Team Data'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('No Slack Workspace Data available')
    

    