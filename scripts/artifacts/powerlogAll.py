import glob
import os
import pathlib
import plistlib
import sqlite3
import json
import textwrap
import scripts.artifacts.artGlobals
 
from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly
from scripts.ccl import ccl_bplist
from scripts.parse3 import ParseProto


def get_powerlogAll(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    
    iOSversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(timestamp, 'unixepoch'),
        datetime(timestamplogged, 'unixepoch'),
        applicationname,
        assertionid,
        assertionname,
        audioroute,
        mirroringstate,
        operation,
        pid
        from
        plaudioagent_eventpoint_audioapp
        ''')
        
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            if version.parse(iOSversion) >= version.parse("9"):
                for row in all_rows:    
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))

                report = ArtifactHtmlReport('Powerlog Audio Routing via App')
                report.start_artifact_report(report_folder, 'Audio Routing')
                report.add_script()
                data_headers = ('Timestamp','Timestamped Logged','Bundle ID','Assertion Name','Audio Route','Mirroring State','Operation','PID')   
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = 'Powerlog Audio Routing via App'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'Powerlog Audio Routing via App'
                timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available in Airdop Connection Info')

    if version.parse(iOSversion) >= version.parse("10"):
        cursor.execute('''
        select
        datetime(timestamp, 'unixepoch'),
        bulletinbundleid,
        timeinterval / 60,
        count,
        posttype
        from
        plspringboardagent_aggregate_sbbulletins_aggregate
        ''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            for row in all_rows:    
                data_list.append((row[0],row[1],row[2],row[3],row[4]))

            report = ArtifactHtmlReport('Powerlog Aggregate Bulletins')
            report.start_artifact_report(report_folder, 'Aggregate Bulletins')
            report.add_script()
            data_headers = ('Timestamp','Bulletin Bundle ID','Time Interval in Seconds','Count','Post Type')   
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Powerlog Agg Bulletins'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Powerlog Agg Bulletins'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No data available in Aggregate Bulletins')
    
    if version.parse(iOSversion) >= version.parse("10"):
        cursor.execute('''
        select
        datetime(timestamp, 'unixepoch'),
        notificationbundleid,
        timeinterval / 60,
        count,
        notificationtype
        from
        plspringboardagent_aggregate_sbnotifications_aggregate 
        ''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            for row in all_rows:    
                data_list.append((row[0],row[1],row[2],row[3],row[4]))

            report = ArtifactHtmlReport('Powerlog Aggregate Notifications')
            report.start_artifact_report(report_folder, 'Aggregate Notifications')
            report.add_script()
            data_headers = ('Timestamp','Notification Bundle ID','Time Interval in Seconds','Count','Notification Type')   
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Powerlog Agg Notifications'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Powerlog Agg Notifications'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No data available in Aggregate Notifications')
            
    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(timestamp, 'unixepoch'),
        appname,
        appexecutable,
        appbundleid,
        appbuildversion,
        appbundleversion,
        apptype,
        case appdeleteddate 
        when 0 then "not deleted" 
        else datetime(appdeleteddate, 'unixepoch') 
        end
        from
        plapplicationagent_eventnone_allapps
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            if version.parse(iOSversion) >= version.parse("9"):
                for row in all_rows:    
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))

                report = ArtifactHtmlReport('Powerlog App Info')
                report.start_artifact_report(report_folder, 'App Info')
                report.add_script()
                data_headers = ('Timestamp','App Name','App Executable Name','Bundle ID','App Build Version','App Bundle Version','App TYpe','App Deleted Date' )   
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = 'Powerlog App Info'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'Powerlog App Info'
                timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available in Powerlog App Info')
        
    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(timestamp, 'unixepoch'),
        appname,
        appexecutable,
        appbundleid,
        appbuildversion,
        appbundleversion,
        apptype,
        case appdeleteddate 
        when 0 then "not deleted" 
        else datetime(appdeleteddate, 'unixepoch') 
        end
        from
        plapplicationagent_eventnone_allapps
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            if version.parse(iOSversion) >= version.parse("9"):
                for row in all_rows:    
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))

                report = ArtifactHtmlReport('Powerlog App Info')
                report.start_artifact_report(report_folder, 'App Info')
                report.add_script()
                data_headers = ('Timestamp','App Name','App Executable Name','Bundle ID','App Build Version','App Bundle Version','App TYpe','App Deleted Date')   
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = 'Powerlog App Info'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'Powerlog App Info'
                timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available in Powerlog App Info')

    if version.parse(iOSversion) >= version.parse("11"):
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(timestamp, 'unixepoch'),
        datetime(start, 'unixepoch'),
        datetime(end, 'unixepoch'),
        state,
        finished,
        haserror
        from
        plxpcagent_eventpoint_mobilebackupevents
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            if version.parse(iOSversion) >= version.parse("11"):
                for row in all_rows:    
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5]))

                report = ArtifactHtmlReport('Powerlog Backup Info')
                report.start_artifact_report(report_folder, 'Backup Info')
                report.add_script()
                data_headers = ('Timestamp','Start','End','State','Finished','Has error')   
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = 'Powerlog Backup Info'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'Powerlog Backup Info'
                timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available in Powerlog Backup Info')

    if version.parse(iOSversion) >= version.parse("11"):
        cursor = db.cursor()
        cursor.execute("""
        select
        datetime(appdeleteddate, 'unixepoch'),
        datetime(timestamp, 'unixepoch'),
        appname,
        appexecutable,
        appbundleid,
        appbuildversion,
        appbundleversion,
        apptype
        from
        plapplicationagent_eventnone_allapps 
        where
        appdeleteddate > 0
        """)
    elif version.parse(iOSversion) == version.parse("10"):
        cursor = db.cursor()
        cursor.execute("""
        select
        datetime(appdeleteddate, 'unixepoch'),
        datetime(timestamp, 'unixepoch'),
        appname,
        appexecutable,
        appbundleid,
        appbuildversion,
        appbundleversion,
        --apptype
        from
        plapplicationagent_eventnone_allapps 
        where
        appdeleteddate > 0
        """)
    elif version.parse(iOSversion) == version.parse("9"):
        cursor = db.cursor()
        cursor.execute("""
        select
        datetime(appdeleteddate, 'unixepoch'),
        datetime(timestamp, 'unixepoch'),
        appname,
        appbundleid
        from
        plapplicationagent_eventnone_allapps 
        where
        appdeleteddate > 0
        """)
    else:
        logfunc("Unsupported version for Powerlog Deleted Apps iOS version: " + iOSversion)
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        if version.parse(iOSversion) >= version.parse("11"):	
            for row in all_rows:    
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))

            report = ArtifactHtmlReport('Powerlog Deleted Apps')
            report.start_artifact_report(report_folder, 'Deleted Apps')
            report.add_script()
            data_headers = ('App Deleted Date','Timestamp','App Name','App Executable Name','Bundle ID','App Build Version','App Bundle Version','App Type')  
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Powerlog Deleted Apps'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Powerlog Deleted Apps'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        elif version.parse(iOSversion) == version.parse("10"):
            for row in all_rows:    
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))
                    
            report = ArtifactHtmlReport('Powerlog Deleted Apps')
            report.start_artifact_report(report_folder, 'Deleted Apps')
            report.add_script()
            data_headers = ('App Deleted Date','Timestamp','App Name','App Executable Name','Bundle ID','App Build Version','App Bundle Version','App Type')             
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Powerlog Deleted Apps'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Powerlog Deleted Apps'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        elif version.parse(iOSversion) == version.parse("9"):
            for row in all_rows:    
                data_list.append((row[0],row[1],row[2],row[3]))
                    
            report = ArtifactHtmlReport('Powerlog Deleted Apps')
            report.start_artifact_report(report_folder, 'Deleted Apps')
            report.add_script()
            data_headers = ('App Deleted Date','Timestamp','App Name','Bundle ID',) 
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Powerlog Deleted Apps'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Powerlog Deleted Apps'
            timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in Powerlog Deleted Apps')

    if version.parse(iOSversion) >= version.parse("10"):
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(timestamp, 'unixepoch'),
        build,
        device,
        hwmodel,
        pairingid
        from
        plconfigagent_eventnone_paireddeviceconfig
        ''')
    else:
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(timestamp, 'unixepoch'),
        build,
        device
        from
        plconfigagent_eventnone_paireddeviceconfig
        ''')
        
        
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        
        if version.parse(iOSversion) >= version.parse("10"):
            for row in all_rows:    data_list.append((row[0],row[1],row[2],row[3],row[4]))

            report = ArtifactHtmlReport('Powerlog Paired Device Configuration')
            report.start_artifact_report(report_folder, 'Paired Device Configuration')
            report.add_script()
            data_headers = ('Timestamp','Build','Device','HW Model','Pairing ID' )   
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Powerlog Paired Device Conf'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Powerlog Paired Device Configuration'
            timeline(report_folder, tlactivity, data_list, data_headers)
        
        else:
            for row in all_rows:    data_list.append((row[0],row[1],row[2]))
            
            report = ArtifactHtmlReport('Powerlog Paired Device Configuration')
            report.start_artifact_report(report_folder, 'Paired Device Configuration')
            report.add_script()
            data_headers = ('Timestamp','Build','Device' )  
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Powerlog Paired Device Conf'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Powerlog Paired Device Configuration'
            timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in table')
    
    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(tts + system, 'unixepoch'),
        bundleid,
        case level
        when "0" then "off"
        when "1" then "on"
        end as status,
        datetime(tts, 'unixepoch'),
        datetime(tot, 'unixepoch'),
        system
        from
        (
        select
        bundleid,
        torchid,
        tts,
        tot,
        max(toid),
        system,
        level
        from
        (
        select
        plcameraagent_eventforward_torch.timestamp as tts,
        plcameraagent_eventforward_torch.bundleid,
        plcameraagent_eventforward_torch.level,
        plcameraagent_eventforward_torch.id as "torchid",
        plstorageoperator_eventforward_timeoffset.timestamp as tot,
        plstorageoperator_eventforward_timeoffset.id as toid,
        plstorageoperator_eventforward_timeoffset.system,
        bundleid 
        from
        plcameraagent_eventforward_torch 
        left join
        plstorageoperator_eventforward_timeoffset 
        ) 
        as torchest
        group by
        torchid 
        )
        ''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            for row in all_rows:    
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5]))

            report = ArtifactHtmlReport('Powerlog Torch')
            report.start_artifact_report(report_folder, 'Torch')
            report.add_script()
            data_headers = ('Adjusted Timestamp','Bundle ID','Status','Original Torch Timestamp','Offset Timestamp','Time Offset')   
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Powerlog Torch'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Powerlog Torch'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No data available in Powerlog Torch')

    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(wifipropts + system, 'unixepoch') ,
        currentssid,
        currentchannel,
        datetime(tot, 'unixepoch') ,
        system as time_offset
        from
        (
        select
        wifiorotsid,
        wifipropts,
        tot,
        max(toi),
        currentssid,
        currentchannel,
        system
        from
        (
        select
        plwifiagent_eventbackward_cumulativeproperties.timestamp as wifipropts,
        currentssid,
        currentchannel,
        plwifiagent_eventbackward_cumulativeproperties.id as "wifiorotsid" ,
        plstorageoperator_eventforward_timeoffset.timestamp as tot,
        plstorageoperator_eventforward_timeoffset.id as toi,
        plstorageoperator_eventforward_timeoffset.system
        from
        plwifiagent_eventbackward_cumulativeproperties
        left join
        plstorageoperator_eventforward_timeoffset 
        )
        as wifipropst
        group by
        wifiorotsid 
        )   
        ''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            for row in all_rows:    
                data_list.append((row[0],row[1],row[2],row[3],row[4]))

            report = ArtifactHtmlReport('Powerlog WiFi Network Connections')
            report.start_artifact_report(report_folder, 'WiFi Network Connections')
            report.add_script()
            data_headers = ('Adjusted Timestamp','Current SSID','Current Channel','Offset Timestamp','Time Offset')   
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Powerlog Wifi Network Connections'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Powerlog Wifi Network Connections'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No data available in Powerlog WiFi Network Connections')
