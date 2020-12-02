import gzip
import re
import os
import shutil
import sqlite3
from pathlib import Path
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, tsv, is_platform_windows, open_sqlite_db_readonly


def get_powerlogGZ(files_found, report_folder, seeker):
	iOSversion = scripts.artifacts.artGlobals.versionf
	data_list1 = []
	data_list2 = []
	data_list3 = []
	data_list4 = []
	data_list5 = []
	data_list6 = []
	data_list7 = []
	data_list8 = []
	data_list9 = []
	data_list10 = []
	data_list11 = []
	data_list12 = []
	data_list13 = []
	data_list14 = []
	data_list15 = []
	data_list16 = []
	data_list17 = []
	data_list18 = []
	
	logfunc('Unzipped Powerlog databases:')
	for file_found in files_found:
		file_found = str(file_found)
		filename = Path(file_found)
		ungzipedfile= Path(filename.parent,filename.stem)
		with gzip.open(file_found, 'rb') as f_in:
			with open(ungzipedfile, 'wb') as f_out:
				shutil.copyfileobj(f_in, f_out)
				f_out.close()
				logfunc(str(filename.stem))
				file_found = str(Path(filename.parent))
				
				db = open_sqlite_db_readonly(str(ungzipedfile))
				cursor = db.cursor()
				
			if version.parse(iOSversion) >= version.parse("9"):
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
					for row in all_rows:
						data_list1.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
				else:
					logfunc('No data available in Powerlog Audio Routing via app')	
						
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
					for row in all_rows:    
						data_list2.append((row[0],row[1],row[2],row[3],row[4]))
				else:
					logfunc('No data available in Aggregate Bulletins')		
			
			if version.parse(iOSversion) >= version.parse("10"):
					cursor.execute('''
					select
					datetime(timestamp, 'unixepoch'),
					notificationbundleid,
					count as "count",
					notificationtype
					from
					plspringboardagent_aggregate_sbnotifications_aggregate 
					''')
					all_rows = cursor.fetchall()
					usageentries = len(all_rows)
					if usageentries > 0:
						
						for row in all_rows:    
							data_list3.append((row[0],row[1],row[2],row[3]))				
					else:
						logfunc('No data available in Aggregate Notifications')
					
		if version.parse(iOSversion) >= version.parse("9"):
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
				for row in all_rows:    
					data_list5.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))
			else:
				logfunc('No data available in Powerlog App Info')
				
		if version.parse(iOSversion) >= version.parse("11"):
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
				for row in all_rows:    
					data_list6.append((row[0],row[1],row[2],row[3],row[4],row[5]))
			else:
				logfunc('No data available in Powerlog Backup Info')
		
		if version.parse(iOSversion) >= version.parse("11"):
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
			appdeleteddate > 0			""")
			all_rows = cursor.fetchall()
			usageentries = len(all_rows)
			if usageentries > 0:
				for row in all_rows:    
					data_list7.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))
						
		if version.parse(iOSversion) == version.parse("10"):
			cursor.execute("""
			select
			datetime(appdeleteddate, 'unixepoch'),
			datetime(timestamp, 'unixepoch'),
			appname,
			appexecutable,
			appbundleid,
			appbuildversion,
			appbundleversion
			from
			plapplicationagent_eventnone_allapps 
			where
			appdeleteddate > 0
			""")
			iall_rows = cursor.fetchall()
			usageentries = len(all_rows)
			if usageentries > 0:
				for row in all_rows:    
					data_list7.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
								
		if version.parse(iOSversion) == version.parse("9"):
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
			all_rows = cursor.fetchall()
			usageentries = len(all_rows)
			if usageentries > 0:
				for row in all_rows:    
					data_list7.append((row[0],row[1],row[2],row[3]))

		if version.parse(iOSversion) >= version.parse("10"):
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
			if version.parse(iOSversion) >= version.parse("10"):
				for row in all_rows:    
					data_list11.append((row[0],row[1],row[2],row[3],row[4]))
			else:
				for row in all_rows:    
					data_list11.append((row[0],row[1],row[2]))
				
		if version.parse(iOSversion) >= version.parse("9"):
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
				for row in all_rows:    
					data_list15.append((row[0],row[1],row[2],row[3],row[4],row[5]))
					
		if version.parse(iOSversion) >= version.parse("9"):
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
				for row in all_rows:    
					data_list18.append((row[0],row[1],row[2],row[3],row[4]))

	
	if version.parse(iOSversion) >= version.parse("9"):
		if len(data_list1) > 0:
			report = ArtifactHtmlReport('Powerlog Audio Routing via App')
			report.start_artifact_report(report_folder, 'Audio Routing')
			report.add_script()
			data_headers1 = ('Timestamp','Timestamped Logged','Bundle ID','Assertion Name','Audio Route','Mirroring State','Operation','PID', 'Audio App Table ID' )   
			report.write_artifact_data_table(data_headers1, data_list1, file_found)
			report.end_artifact_report()

			tsvname = 'Powerlog Audio Routing via App from GZ backup'
			tsv(report_folder, data_headers1, data_list1, tsvname)

			tlactivity = 'Powerlog Audio Routing via App from GZ backup'
			timeline(report_folder, tlactivity, data_list1, data_headers1)

	if version.parse(iOSversion) >= version.parse("10"):
		if len(data_list2) > 0:
			report = ArtifactHtmlReport('Powerlog Aggregate Bulletins')
			report.start_artifact_report(report_folder, 'Aggregate Bulletins')
			report.add_script()
			data_headers2 = ('Timestamp','Bulletin Bundle ID','Time Interval in Seconds','Count','Post Type')   
			report.write_artifact_data_table(data_headers2, data_list2, file_found)
			report.end_artifact_report()
			
			tsvname = 'Powerlog Agg Bulletins from GZ backup'
			tsv(report_folder, data_headers2, data_list2, tsvname)
			
			tlactivity = 'Powerlog Agg Bulletins from GZ backup'
			timeline(report_folder, tlactivity, data_list2, data_headers2)
			
	if version.parse(iOSversion) >= version.parse("10"):
		if len(data_list3) > 0:
			report = ArtifactHtmlReport('Powerlog Aggregate Notifications')
			report.start_artifact_report(report_folder, 'Aggregate Notifications')
			report.add_script()
			data_headers3 = ('Timestamp','Notification Bundle ID','Count','Notification Type')   
			report.write_artifact_data_table(data_headers3, data_list3, file_found)
			report.end_artifact_report()
			
			tsvname = 'Powerlog Agg Notifications from GZ backup'
			tsv(report_folder, data_headers3, data_list3, tsvname)
			
			tlactivity = 'Powerlog Agg Notifications from GZ backup'
			timeline(report_folder, tlactivity, data_list3, data_headers3)
	
	if version.parse(iOSversion) >= version.parse("9"):
		if len(data_list5) > 0:
			report = ArtifactHtmlReport('Powerlog App Info')
			report.start_artifact_report(report_folder, 'App Info')
			report.add_script()
			data_headers5 = ('Timestamp','App Name','App Executable Name','Bundle ID','App Build Version','App Bundle Version','App TYpe','App Deleted Date')   
			report.write_artifact_data_table(data_headers5, data_list5, file_found)
			report.end_artifact_report()

			tsvname = 'Powerlog App Info from GZ backup'
			tsv(report_folder, data_headers5, data_list5, tsvname)

			tlactivity = 'Powerlog App Info from GZ backup'
			timeline(report_folder, tlactivity, data_list5, data_headers5)
	
	if version.parse(iOSversion) >= version.parse("11"):
		if len(data_list6) > 0:
			report = ArtifactHtmlReport('Powerlog Backup Info')
			report.start_artifact_report(report_folder, 'Backup Info')
			report.add_script()
			data_headers6 = ('Timestamp','Start','End','State','Finished','Has error' )   
			report.write_artifact_data_table(data_headers6, data_list6, file_found)
			report.end_artifact_report()

			tsvname = 'Powerlog Backup Info from GZ backup'
			tsv(report_folder, data_headers6, data_list6, tsvname)

			tlactivity = 'Powerlog Backup Info from GZ backup'
			timeline(report_folder, tlactivity, data_list6, data_headers6)

	if version.parse(iOSversion) >= version.parse("11"):
		if len(data_list7) > 0:
			report = ArtifactHtmlReport('Powerlog Deleted Apps')
			report.start_artifact_report(report_folder, 'Deleted Apps')
			report.add_script()
			data_headers7 = ('App Deleted Date','Timestamp','App Name','App Executable Name','Bundle ID','App Build Version','App Bundle Version','App Type')  
			report.write_artifact_data_table(data_headers7, data_list7, file_found)
			report.end_artifact_report()
			
			tsvname = 'Powerlog Deleted Apps from GZ backup'
			tsv(report_folder, data_headers7, data_list7, tsvname)
			
			tlactivity = 'Powerlog Deleted Apps from GZ backup'
			timeline(report_folder, tlactivity, data_list7, data_headers7)
			
	if version.parse(iOSversion) == version.parse("10"):
		if len(data_list7) > 0:
			report = ArtifactHtmlReport('Powerlog Deleted Apps')
			report.start_artifact_report(report_folder, 'Deleted Apps')
			report.add_script()
			data_headers7 = ('App Deleted Date','Timestamp','App Name','App Executable Name','Bundle ID','App Build Version','App Bundle Version')             
			report.write_artifact_data_table(data_headers7, data_list7, file_found)
			report.end_artifact_report()
			
			tsvname = 'Powerlog Deleted Apps from GZ backup'
			tsv(report_folder, data_headers7, data_list7, tsvname)
			
			tlactivity = 'Powerlog Deleted Apps from GZ backup'
			timeline(report_folder, tlactivity, data_list7, data_headers7)
			
	if version.parse(iOSversion) == version.parse("9"):
		if len(data_list7) > 0:
			report = ArtifactHtmlReport('Powerlog Deleted Apps')
			report.start_artifact_report(report_folder, 'Deleted Apps')
			report.add_script()
			data_headers7 = ('App Deleted Date','Timestamp','App Name','Bundle ID') 
			report.write_artifact_data_table(data_headers7, data_list7, file_found)
			report.end_artifact_report()
			
			tsvname = 'Powerlog Deleted Apps from GZ backup'
			tsv(report_folder, data_headers7, data_list7, tsvname)
			
			tlactivity = 'Powerlog Deleted Apps from GZ backup'
			timeline(report_folder, tlactivity, data_list7, data_headers7)
				
	if version.parse(iOSversion) >= version.parse("10"):
		if len(data_list11) > 0:
			report = ArtifactHtmlReport('Powerlog Paired Device Configuration')
			report.start_artifact_report(report_folder, 'Paired Device Configuration')
			report.add_script()
			data_headers11 = ('Timestamp','Build','Device','HW Model','Pairing ID')   
			report.write_artifact_data_table(data_headers11, data_list11, file_found)
			report.end_artifact_report()
			
			tsvname = 'Powerlog Paired Device Conf from GZ backup'
			tsv(report_folder, data_headers11, data_list11, tsvname)
			
			tlactivity = 'Powerlog Paired Device Configuration from GZ backup'
			timeline(report_folder, tlactivity, data_list11, data_headers11)
	else:
		if len(data_list11) > 0:
			report = ArtifactHtmlReport('Powerlog Paired Device Configuration')
			report.start_artifact_report(report_folder, 'Paired Device Configuration')
			report.add_script()
			data_headers11 = ('Timestamp','Build','Device' )  
			report.write_artifact_data_table(data_headers11, data_list11, file_found)
			report.end_artifact_report()
			
			tsvname = 'Powerlog Paired Device Conf from GZ backup'
			tsv(report_folder, data_headers11, data_list11, tsvname)
			
			tlactivity = 'Powerlog Paired Device Configuration from GZ backup'
			timeline(report_folder, tlactivity, data_list11, data_headers11)
			
	if version.parse(iOSversion) >= version.parse("9"):
		if len(data_list15) > 0:
			report = ArtifactHtmlReport('Powerlog Torch')
			report.start_artifact_report(report_folder, 'Torch')
			report.add_script()
			data_headers15 = ('Adjusted Timestamp','Bundle ID','Status','Original Torch Timestamp','Offset Timestamp','Time Offset')   
			report.write_artifact_data_table(data_headers15, data_list15, file_found)
			report.end_artifact_report()
			
			tsvname = 'Powerlog Torch from GZ backup'
			tsv(report_folder, data_headers15, data_list15, tsvname)
			
			tlactivity = 'Powerlog Torch from GZ backup'
			timeline(report_folder, tlactivity, data_list15, data_headers15)
						
				
	if version.parse(iOSversion) >= version.parse("9"):
		if len(data_list18) > 0:
			report = ArtifactHtmlReport('Powerlog WiFi Network Connections')
			report.start_artifact_report(report_folder, 'WiFi Network Connections')
			report.add_script()
			data_headers18 = ('Adjusted Timestamp','Current SSID','Current Channel','Offset Timestamp','Time Offset')    
			report.write_artifact_data_table(data_headers18, data_list18, file_found)
			report.end_artifact_report()
			
			tsvname = 'Powerlog Wifi Network Connections from GZ backup'
			tsv(report_folder, data_headers18, data_list18, tsvname)
			
			tlactivity = 'Powerlog Wifi Network Connections from GZ backup'
			timeline(report_folder, tlactivity, data_list18, data_headers18)