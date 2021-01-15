import glob
import os
import pathlib
import plistlib
import sqlite3
import scripts.artifacts.artGlobals #use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf
from packaging import version #use to search per version number

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, open_sqlite_db_readonly

def get_screentimeAll(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	db = open_sqlite_db_readonly(file_found)
	
	iOSversion = scripts.artifacts.artGlobals.versionf
	if version.parse(iOSversion) < version.parse("12"):
		logfunc("Unsupported version for Screentime App by Hour on iOS " + iOSversion)
		return ()
	
	
	if version.parse(iOSversion) >= version.parse("13"):
		cursor = db.cursor()
		cursor.execute('''
		select 
		datetime(zusageblock.zstartdate+978307200,'unixepoch'),
		zusagetimeditem.zbundleidentifier,
		zusagetimeditem.zdomain,
		case zusagecategory.zidentifier 
		when 'DH0011' then 'unspecified1'
		when 'DH0012' then 'unspecified2'
		when 'DH0013' then 'unspecified3'
		when 'DH1001' then 'games'
		when 'DH1002' then 'social networking'
		when 'DH1003' then 'entertainment'
		when 'DH1004' then 'creativity'
		when 'DH1005' then 'productivity'
		when 'DH1006' then 'education'
		when 'DH1007' then 'reading & reference'
		when 'DH1008' then 'health & fitness'
		when 'DH1009' then 'other'
		else zusagecategory.zidentifier
		end,
		zusagetimeditem.ztotaltimeinseconds,	
		zusagetimeditem.ztotaltimeinseconds/60.00,	
		zusageblock.znumberofpickupswithoutapplicationusage,	
		zcoredevice.zname,
		case zcoredevice.zplatform
		when 0 then 'unknown'
		when 1 then 'macos'
		when 2 then 'ios'
		when 4 then 'apple watch'
		else zplatform
		end,
		zcoreuser.zgivenname as 'given name',
		zcoreuser.zfamilyname as 'family name',
		zcoreuser.zfamilymembertype
		from zusagetimeditem, zusagecategory, zusageblock, zusage, zcoreuser, zcoredevice 
		where zusagecategory.z_pk = zusagetimeditem.zcategory
		and zusagecategory.zblock = zusageblock.z_pk
		and zusageblock.zusage = zusage.z_pk
		and zusage.zuser = zcoreuser.z_pk
		and zusage.zdevice = zcoredevice.z_pk
			''')
	else:
			cursor = db.cursor()
			cursor.execute('''
			select 
			datetime(zusageblock.zstartdate+978307200,'unixepoch'),
			zusagetimeditem.zbundleidentifier,
			zusagetimeditem.zdomain,
			case zusagecategory.zidentifier 
			when 'DH0011' then 'unspecified1'
			when 'DH0012' then 'unspecified2'
			when 'DH0013' then 'unspecified3'
			when 'DH1001' then 'games'
			when 'DH1002' then 'social networking'
			when 'DH1003' then 'entertainment'
			when 'DH1004' then 'creativity'
			when 'DH1005' then 'productivity'
			when 'DH1006' then 'education'
			when 'DH1007' then 'reading & reference'
			when 'DH1008' then 'health & fitness'
			when 'DH1009' then 'other'
			else zusagecategory.zidentifier
			end,
			zusagetimeditem.ztotaltimeinseconds,	
			zusagetimeditem.ztotaltimeinseconds/60.00,	
			zusageblock.znumberofpickupswithoutapplicationusage,	
			zcoredevice.zname,
			zcoredevice.zlocaluserdevicestate,
			zcoreuser.zgivenname,
			zcoreuser.zfamilyname
			from zusagetimeditem, zusagecategory, zusageblock, zusage, zcoreuser, zcoredevice
			where zusagecategory.z_pk = zusagetimeditem.zcategory
			and zusagecategory.zblock = zusageblock.z_pk
			and zusageblock.zusage = zusage.z_pk
			and zusage.zuser = zcoreuser.z_pk
			and zusage.zdevice = zcoredevice.z_pk
			''')

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	if usageentries > 0:
		data_list = []
		if version.parse(iOSversion) >= version.parse("13"):
					
			for row in all_rows:
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]))

			report = ArtifactHtmlReport('Screentime Timed Items')
			report.start_artifact_report(report_folder, 'Timed Items')
			report.add_script()
			data_headers = ('Hour','Bundle ID','Domain','Category ID', 'App Usage Time Item in Seconds','App Usage Time Item in Minutes','Number of Pickpus w/o App Usage','Name','Platform','Given Name','Family Name','Family Member Type')  
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'Screentime Timed Items'
			tsv(report_folder, data_headers, data_list, tsvname)
		else:
			for row in all_rows: 
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]))
					
			report = ArtifactHtmlReport('Screentime Timed Items')
			report.start_artifact_report(report_folder, 'Timed Items')
			report.add_script()
			data_headers = ('Hour','Bundle ID','Domain','Category ID', 'App Usage Time Item in Seconds','App Usage Time Item in Minutes','Number of Pickpus w/o App Usage','Name','Local User Device State','Given Name','Family Name')   
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'Screentime Timed Items'
			tsv(report_folder, data_headers, data_list, tsvname)
	else:
		logfunc('No data available in table foe Screentime Timed Items')

	if version.parse(iOSversion) >= version.parse("13"):
		cursor = db.cursor()
		cursor.execute('''
		select 
		datetime(zusageblock.zstartdate+978307200,'unixepoch'),
		zusagecounteditem.zbundleidentifier, 
		zusagecounteditem.znumberofnotifications,
		zusagecounteditem.znumberofpickups,
		datetime(zusageblock.zfirstpickupdate+978307200,'unixepoch'),
		zusageblock.znumberofpickupswithoutapplicationusage,
		zcoredevice.zname,
		zcoredevice.zlocaluserdevicestate,
		case zcoredevice.zplatform
		when 0 then 'unknown'
		when 1 then 'macos'
		when 2 then 'ios'
		when 4 then 'apple watch'
		else zplatform
		end,
		zcoreuser.zgivenname,
		zcoreuser.zfamilyname
		from zusagecounteditem, zusageblock, zusage, zcoreuser, zcoredevice  
		where zusagecounteditem.zblock = zusageblock.z_pk
		and zusageblock.zusage = zusage.z_pk
		and zusage.zuser = zcoreuser.z_pk
		and zusage.zdevice = zcoredevice.z_pk
			''')
	else:
			cursor = db.cursor()
			cursor.execute('''
			select 
			datetime(zusageblock.zstartdate+978307200,'unixepoch'),
			zusagecounteditem.zbundleidentifier, 
			zusagecounteditem.znumberofnotifications,
			zusagecounteditem.znumberofpickups,
			datetime(zusageblock.zfirstpickupdate+978307200,'unixepoch'),
			zusageblock.znumberofpickupswithoutapplicationusage,
			zcoredevice.zname,
			zcoredevice.zlocaluserdevicestate,
			zcoreuser.zgivenname,
			zcoreuser.zfamilyname
			from zusagecounteditem, zusageblock, zusage, zcoreuser, zcoredevice 
			where zusagecounteditem.zblock == zusageblock.z_pk
			and zusageblock.zusage == zusage.z_pk
			and zusage.zuser == zcoreuser.z_pk
			and zusage.zdevice == zcoredevice.z_pk
			''')

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	if usageentries > 0:
		data_list = []
		if version.parse(iOSversion) >= version.parse("13"):
					
			for row in all_rows:
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]))

			report = ArtifactHtmlReport('Screentime Counted Items')
			report.start_artifact_report(report_folder, 'Counted Items')
			report.add_script()
			data_headers = ('Hour','Bundle ID','Number of Notifications','Number of Pickups', 'First Pickup','Number of Pickups W/O App Usage','Name','Local User Device State','Platform','Given Name','Family Name')  
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'Screentime Counted Items'
			tsv(report_folder, data_headers, data_list, tsvname)
		else:
			for row in all_rows: 
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9]))
					
			report = ArtifactHtmlReport('Screentime Counted Items')
			report.start_artifact_report(report_folder, 'Counted Items')
			report.add_script()
			data_headers = ('Hour','Bundle ID','Number of Notifications','Number of Pickups', 'First Pickup','Number of Pickups W/O App Usage','Name','Local User Device State','Given Name','Family Name')  
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'Screentime Counted Items'
			tsv(report_folder, data_headers, data_list, tsvname)
	else:
		logfunc('No data available in table foe Screentime Counted Items')
	
	if version.parse(iOSversion) >= version.parse("13"):
		cursor = db.cursor()
		cursor.execute('''
		select
		distinct
		datetime(zusageblock.zstartdate+978307200,'unixepoch'),
		zusageblock.zscreentimeinseconds,
		zusageblock.zscreentimeinseconds/60.00,	
		zcoreuser.zgivenname,
		zcoreuser.zfamilyname,
		zcoredevice.zname,
		case zcoredevice.zplatform
		when 0 then 'unknown'
		when 1 then 'macos'
		when 2 then 'ios'
		when 4 then 'apple watch'
		else zplatform
		end,
		zcoredevice.zlocaluserdevicestate as 'local user device state',
		datetime(zusageblock.zlongestsessionstartdate+978307200,'unixepoch'),
		datetime(zusageblock.zlongestsessionenddate+978307200,'unixepoch'),
		datetime(zusageblock.zlasteventdate+978307200,'unixepoch'),
		(zlongestsessionenddate-zlongestsessionstartdate),
		(zlongestsessionenddate-zlongestsessionstartdate)/60.00 
		from zusagetimeditem, zusagecategory, zusageblock, zusage, zcoreuser, zcoredevice 
		where zusagecategory.z_pk == zusagetimeditem.zcategory
		and  zusagecategory.zblock == zusageblock.z_pk
		and  zusageblock.zusage == zusage.z_pk
		and  zusage.zuser == zcoreuser.z_pk
		and zusage.zdevice == zcoredevice.z_pk
		''')
		
	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	if usageentries > 0:
		data_list = []
		if version.parse(iOSversion) >= version.parse("13"):
					
			for row in all_rows:
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]))

			report = ArtifactHtmlReport('Screentime Generic by Hour')
			report.start_artifact_report(report_folder, 'Generic by Hour')
			report.add_script()
			data_headers = ('Hour','Screentime in Seconds','Screentime in Minutes','Given Name', 'Family Name','Name','Platform','Local User Device State','Longest Session Start','Longest Session End','Last Event Date','Longest Session Time in Seconds','Longest Session Time in Minutes')  
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'Screentime Generic by Hour'
			tsv(report_folder, data_headers, data_list, tsvname)
		
	else:
		logfunc('No data available in table foe Screentime Generic by Hour')
		