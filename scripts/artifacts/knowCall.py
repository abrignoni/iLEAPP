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
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, open_sqlite_db_readonly
from scripts.ccl import ccl_bplist
from scripts.parse3 import ParseProto


def get_knowCall(files_found, report_folder, seeker):
	iOSversion = scripts.artifacts.artGlobals.versionf
	if version.parse(iOSversion) < version.parse("12"):
		logfunc("Unsupported version for KnowledgC Inferred Motion on iOS " + iOSversion)
	else:
		file_found = str(files_found[0])
		db = open_sqlite_db_readonly(file_found)
		cursor = db.cursor()
		cursor.execute("""
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		zobject.zsecondsfromgmt/3600,
		zobject.zvalueinteger,
		(zobject.zenddate - zobject.zstartdate),
		(zobject.zenddate - zobject.zstartdate)/60.00,   
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end,
		datetime(zobject.zcreationdate+978307200,'unixepoch')
		from
		zobject 
		where
		zstreamname = '/inferred/motion'  	
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			data_list = []    
			for row in all_rows:
				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

			description = ''
			report = ArtifactHtmlReport('KnowledgeC Inferred Motion')
			report.start_artifact_report(report_folder, 'Inferred Motion', description)
			report.add_script()
			data_headers = ('Start','End','GMT Offset','Value','Usage in Seconds','Usage in Minutes','Day of Week','Entry Creation')     
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Inferred Motion'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Inferred Motion'
			timeline(report_folder, tlactivity, data_list, data_headers)
		else:
			logfunc('No data available in Inferred Motion')

	cursor = db.cursor()
	cursor.execute('''
		select
		datetime(zobject.zcreationdate+978307200,'unixepoch'), 
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end,
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'), 
		zobject.zvaluestring,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__activitytype,  
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__title, 
		datetime(zstructuredmetadata.z_dkapplicationactivitymetadatakey__expirationdate+978307200,'unixepoch'),
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__itemrelatedcontenturl,
		datetime(zstructuredmetadata.zcom_apple_calendaruikit_useractivity_date+978307200,'unixepoch'),
		datetime(zstructuredmetadata.zcom_apple_calendaruikit_useractivity_enddate+978307200,'unixepoch')
		from zobject, zstructuredmetadata, zsource 
		where zobject.zstructuredmetadata = zstructuredmetadata.z_pk
		and zobject.zsource = zsource.z_pk
		and zstreamname = '/app/activity' 
		order by 'entry creation'
	''')

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = [] 
	for row in all_rows:
		data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))

	description = ''
	report = ArtifactHtmlReport('KnowledgeC App Activity')
	report.start_artifact_report(report_folder, 'App Activity', description)
	report.add_script()
	data_headers = ('Entry Creation','Day of the Week','Start','End','Value String', 'Activity Type', 'Title', 'Expiration Date', 'Content URL', 'Calendar Date', 'Calendar End Date' )     
	report.write_artifact_data_table(data_headers, data_list, file_found)
	report.end_artifact_report()
	
	tsvname = 'KnowledgeC App Activity'
	tsv(report_folder, data_headers, data_list, tsvname)
	
	tlactivity = 'KnowledgeC App Activity'
	timeline(report_folder, tlactivity, data_list, data_headers)   
	
	if version.parse(iOSversion) >= version.parse("12"):
		cursor = db.cursor()
		cursor.execute('''
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		zobject.zvaluestring, 
		zsource.zgroupid,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__activitytype, 
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__contentdescription,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__useractivityrequiredstring,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__itemrelatedcontenturl,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__suggestedinvocationphrase,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__itemrelateduniqueidentifier,
		zsource.zsourceid,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__itemidentifier,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__useractivityuuid,
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end,
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate + 978307200, 'unixepoch'),
		datetime(zstructuredmetadata.z_dkapplicationactivitymetadatakey__expirationdate + 978307200, 'unixepoch')
		from zobject, zstructuredmetadata, zsource 
		where zobject.zstructuredmetadata = zstructuredmetadata.z_pk 
		and zobject.zsource = zsource.z_pk 
		and zstreamname = '/app/activity'
		''')
	else:
		cursor = db.cursor()
		cursor.execute('''
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		zobject.zvaluestring, 
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__activitytype, 
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__title, 
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__itemrelatedcontenturl,
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end,
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate + 978307200, 'unixepoch'),
		datetime(zstructuredmetadata.z_dkapplicationactivitymetadatakey__expirationdate + 978307200, 'unixepoch')
		from zobject, zstructuredmetadata, zsource 
		where zobject.zstructuredmetadata = zstructuredmetadata.z_pk 
		and zobject.zsource = zsource.z_pk 
		and zstreamname = '/app/activity'
		''')

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			data_list = []
			
			if version.parse(iOSversion) >= version.parse("12"):
				for row in all_rows:    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16]))

				report = ArtifactHtmlReport('KnowledgeC Application Activity')
				report.start_artifact_report(report_folder, 'Application Activity')
				report.add_script()
				data_headers = ('Start','End','Bundle ID','Group ID','Activity Type', 'Content Description', 'User Activity Required String', 'Content URL','Suggest Invocation Phrase','Unique ID','Source ID','ID','Activity UUID','Day of Week','GMT Offset','Entry Creation','Expiration Date' )   
				report.write_artifact_data_table(data_headers, data_list, file_found)
				report.end_artifact_report()
				
				tsvname = 'KnowledgeC Application Activity'
				tsv(report_folder, data_headers, data_list, tsvname)
				
				tlactivity = 'KnowledgeC Application Activity'
				timeline(report_folder, tlactivity, data_list, data_headers)
			else:
				for row in all_rows:    
					data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9]))
				report = ArtifactHtmlReport('KnowledgeC Application Activity')
				report.start_artifact_report(report_folder, 'Application Activity')
				report.add_script()
				data_headers = ('Start','End','Bundle ID','Activity Type', 'Title','Content URL','Day of Week','GMT Offset','Entry Creation','Expiration Date') 
				report.write_artifact_data_table(data_headers, data_list, file_found)
				report.end_artifact_report()
				
				tsvname = 'KnowledgeC Application Activity'
				tsv(report_folder, data_headers, data_list, tsvname)
				
				tlactivity = 'KnowledgeC Application Activity'
				timeline(report_folder, tlactivity, data_list, data_headers)
		else:
			logfunc('No data available in Application Activity')
	
	
	if version.parse(iOSversion) >= version.parse("12"):
		cursor = db.cursor()
		cursor.execute('''
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		zobject.zvaluestring, 
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__activitytype, 
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__useractivityrequiredstring ,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__title, 
		datetime(zstructuredmetadata.zcom_apple_calendaruikit_useractivity_date + 978307200, 'unixepoch'), 
		datetime(zstructuredmetadata.zcom_apple_calendaruikit_useractivity_enddate + 978307200, 'unixepoch'),
		zsource.zsourceid,
		case zobject.zstartdayofweek 
		when "1" then "sunday"
		when "2" then "monday"
		when "3" then "tuesday"
		when "4" then "wednesday"
		when "5" then "thursday"
		when "6" then "friday"
		when "7" then "saturday"
		end , 
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate + 978307200, 'unixepoch'),
		datetime(zstructuredmetadata.z_dkapplicationactivitymetadatakey__expirationdate + 978307200, 'unixepoch')
		from
		zobject 
		left join
		zstructuredmetadata 
		on zobject.zstructuredmetadata = zstructuredmetadata.z_pk 
		left join
		zsource 
		on zobject.zsource = zsource.z_pk 
		where
		zstreamname = "/app/activity" 
		and (zvaluestring = "com.apple.mobilecal" or zvaluestring = "com.apple.ical")
		''')
	else:
		cursor = db.cursor()
		cursor.execute('''
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		zobject.zvaluestring, 
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__activitytype, 
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__useractivityrequiredstring ,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__title, 
		datetime(zstructuredmetadata.zcom_apple_calendaruikit_useractivity_date + 978307200, 'unixepoch'), 
		datetime(zstructuredmetadata.zcom_apple_calendaruikit_useractivity_enddate + 978307200, 'unixepoch'),
		zsource.zsourceid,
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end , 
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate + 978307200, 'unixepoch'),
		datetime(zstructuredmetadata.z_dkapplicationactivitymetadatakey__expirationdate + 978307200, 'unixepoch')
		from zobject, zstructuredmetadata, zsource 
		where zobject.zstructuredmetadata = zstructuredmetadata.z_pk 
		and zobject.zsource = zsource.z_pk 
		and zstreamname = '/app/activity'
		and (zvaluestring = 'com.apple.mobilecal' or zvaluestring = 'com.apple.ical')
					''')

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	if usageentries > 0:
		data_list = []
			
		if version.parse(iOSversion) >= version.parse("12"):
					
			for row in all_rows:    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]))

			report = ArtifactHtmlReport('InteractionC Application Activity Calendar')
			report.start_artifact_report(report_folder, 'Application Activity Calendar')
			report.add_script()
			data_headers = ('Start','End','Bundle ID','Activity Type','User Activity Required String','Title','Calendar Date','Calendar End Date','Source ID','Day of Week','GMT Offset','Entry Creation','Expiration Date')   
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Application Activity Calendar'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Application Activity Calendar'
			timeline(report_folder, tlactivity, data_list, data_headers)
		else:
			for row in all_rows:    
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]))
			
			report = ArtifactHtmlReport('InteractionC Application Activty Calendar')
			report.start_artifact_report(report_folder, 'Application Activity Calendar')
			report.add_script()
			data_headers = ('Start','End','Bundle ID','Activity Type', 'Title','Expiration Date','Calendar Date','Calendar End Date','Day of Week','GMT Offset','Entry Creation' ) 
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Application Activity Calendar'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Application Activity Calendar'
			timeline(report_folder, tlactivity, data_list, data_headers)
	else:
		logfunc('No data available in Application Activity Calendar')
			
	if version.parse(iOSversion) >= version.parse("12"):
		cursor = db.cursor()
		cursor.execute('''
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		zobject.zvaluestring, 
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__activitytype, 
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__contentdescription,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__itemrelatedcontenturl,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__useractivityrequiredstring,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__itemidentifier,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__itemrelateduniqueidentifier,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__useractivityuuid,
		zsource.zsourceid,
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end,
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate + 978307200, 'unixepoch'),
		datetime(zstructuredmetadata.z_dkapplicationactivitymetadatakey__expirationdate + 978307200, 'unixepoch')
		from zobject, zstructuredmetadata, zsource 
		where zobject.zstructuredmetadata = zstructuredmetadata.z_pk 
		and zobject.zsource = zsource.z_pk 
		and zstreamname = '/app/activity'
		and (zobject.zvaluestring = 'com.apple.mobilesafari' or zobject.zvaluestring = 'com.apple.safari')
			''')
	else:
		cursor = db.cursor()
		cursor.execute('''
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		zobject.zvaluestring, 
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__activitytype, 
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__itemrelatedcontenturl,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__itemidentifier,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__itemrelateduniqueidentifier,
		zsource.zsourceid,
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end,
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate + 978307200, 'unixepoch'),
		datetime(zstructuredmetadata.z_dkapplicationactivitymetadatakey__expirationdate + 978307200, 'unixepoch')
		from zobject, zstructuredmetadata, zsource 
		where zobject.zstructuredmetadata = zstructuredmetadata.z_pk 
		and zobject.zsource = zsource.z_pk 
		and zstreamname = '/app/activity'
		and (zobject.zvaluestring = 'com.apple.mobilesafari' or zobject.zvaluestring = 'com.apple.safari')
		''')

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	if usageentries > 0:
		data_list = []
			
		if version.parse(iOSversion) >= version.parse("12"):
			
			for row in all_rows:    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14]))

			report = ArtifactHtmlReport('KnowledgeC Application Activity Safari')
			report.start_artifact_report(report_folder, 'Application Activity Safari')
			report.add_script()
			data_headers = ('Start','End','Bundle ID','Activity Type', 'Content Description', 'Content URL','User Activity Required String','ID','Unique ID','Activity UUID','Source ID','Day of Week','GMT Offset','Entry Creation','Expiration Date')  
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Application Activity Safari'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Application Activity Safari'
			timeline(report_folder, tlactivity, data_list, data_headers)
		else:
			for row in all_rows:    
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]))
			
			report = ArtifactHtmlReport('KnowledgeC Application Activty Safari')
			report.start_artifact_report(report_folder, 'Application Activity Safari')
			report.add_script()
			data_headers = ('Start','End','Bundle ID','Activity Type','Content URL','ID','Unique ID','Source ID','Day of Week','GMT Offset','Entry Creation','Expiration Date') 
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Application Activity Safari'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Application Activity Safari'
			timeline(report_folder, tlactivity, data_list, data_headers)
	else:
		logfunc('No data available in Appplication Activity Safari')

	if version.parse(iOSversion) >= version.parse("12"):
		cursor = db.cursor()
		cursor.execute("""
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		zobject.zvaluestring, 
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end,
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate+978307200,'unixepoch')
		from zobject
		where zstreamname = '/app/relevantShortcuts'		
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			data_list = []    
			for row in all_rows:
				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))

			description = ''
			report = ArtifactHtmlReport('KnowledgeC Application Relevant Shortcuts')
			report.start_artifact_report(report_folder, 'App Relevant Shortcuts', description)
			report.add_script()
			data_headers = ('Start','End','Bundle ID','Day of the Week','GMT Offset','Entry Creation')     
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Application Relevant Shortcuts'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Application Relevant Shortcuts'
			timeline(report_folder, tlactivity, data_list, data_headers)
		else:
			logfunc('No data available in Relevant Shortcuts')
	
	if version.parse(iOSversion) >= version.parse("12"):
		cursor = db.cursor()
		cursor.execute("""
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		case zobject.zvalueinteger
		when '0' then 'no' 
		when '1' then 'yes' 
		end,
		(zobject.zenddate - zobject.zstartdate),
		(zobject.zenddate - zobject.zstartdate)/60.00,
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end, 
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate+978307200,'unixepoch')
		from zobject
		where
		zobject.zstreamname = '/display/isBacklit'	
		""")
	elif version.parse(iOSversion) == version.parse("11"):
		cursor = db.cursor()
		cursor.execute("""
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		case zobject.zvalueinteger
		when '0' then 'no' 
		when '1' then 'yes' 
		end,
		(zobject.zenddate - zobject.zstartdate),
		(zobject.zenddate - zobject.zstartdate)/60.00,  
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end, 
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate+978307200,'unixepoch')
		from zobject
		where
		zobject.zstreamname = '/display/isBacklit'
		""")
	else:
		logfunc("Unsupported version for KnowledgC Backlit" + iOSversion)
		return ()
	
	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	if usageentries > 0:
		data_list = []
		if version.parse(iOSversion) >= version.parse("12"):	
			for row in all_rows:    
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))

			report = ArtifactHtmlReport('KnowledgeC Device is Backlit')
			report.start_artifact_report(report_folder, 'Device is Backlit')
			report.add_script()
			data_headers = ('Start','End','Screen is Backlit','Usage in Seconds','Usage in Minutes','Day of Week','GMT Offset','Entry Creation')  
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Device is Backlit'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Device is Backlit'
			timeline(report_folder, tlactivity, data_list, data_headers)
			
		elif version.parse(iOSversion) == version.parse("11"):
			for row in all_rows:    
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
					
			report = ArtifactHtmlReport('KnowledgeC Device is Backlit')
			report.start_artifact_report(report_folder, 'Device is Backlit')
			report.add_script()
			data_headers = ('Start','End','Screen is Backlit','Usage in Seconds','Usage in Minutes','Day of Week','GMT Offset','Entry Creation') 
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Device is Backlit'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Device is Backlit'
			timeline(report_folder, tlactivity, data_list, data_headers)
	else:
		logfunc('No data available in Device is Backlit')
	
	if version.parse(iOSversion) >= version.parse("11"):	
		cursor.execute("""
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		zobject.zvaluedouble,
		(zobject.zenddate - zobject.zstartdate), 
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end,
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate+978307200,'unixepoch')
		from
		zobject 
		where
		zstreamname like '/device/BatteryPercentage'
			"""
			)

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []    
		for row in all_rows:
			data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6]))

		description = ''
		report = ArtifactHtmlReport('KnowledgeC Battery Level')
		report.start_artifact_report(report_folder, 'Battery Level', description)
		report.add_script()
		data_headers = ('Start','End','Battery Level','Usage in Seconds','Day of the Week','GMT Offset','Entry Creation' )     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'KnowledgeC Battery Level'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'KnowledgeC Battery Level'
		timeline(report_folder, tlactivity, data_list, data_headers)
		
	if version.parse(iOSversion) >= version.parse("11"):
		cursor.execute("""
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		zstructuredmetadata.z_dkbluetoothmetadatakey__address, 
		zstructuredmetadata.z_dkbluetoothmetadatakey__name,
		(zobject.zenddate - zobject.zstartdate),
		(zobject.zenddate - zobject.zstartdate)/60.00,  
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end,
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate+978307200,'unixepoch')
		from
		zobject,
		zstructuredmetadata 
		on zobject.zstructuredmetadata = zstructuredmetadata.z_pk 
		where
		zstreamname = '/bluetooth/isConnected'
		"""
		)

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			data_list = []    
			for row in all_rows:
				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))

			description = ''
			report = ArtifactHtmlReport('KnowledgeC Bluetooth Connections')
			report.start_artifact_report(report_folder, 'Bluetooth Connections', description)
			report.add_script()
			data_headers = ('Start','End','Bluetooth Address','Bluetooth Name','Usage in Seconds','Usage in Minutes','Day of Week','GMT Offset','Entry Creation')     
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Bluetooth Connections'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Bluetooth Connections'
			timeline(report_folder, tlactivity, data_list, data_headers)
		else:
			logfunc('No data available in Bluetooth Connections')
	
	if version.parse(iOSversion) >= version.parse("11"):
		cursor.execute("""
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		case zobject.zvalueinteger
		when '0' then 'disconnected' 
		when '1' then 'connected' 
		end,
		(zobject.zenddate - zobject.zstartdate),
		(zobject.zenddate - zobject.zstartdate)/60.00,  
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end, 
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate+978307200,'unixepoch')
		from
		zobject
		where
		zstreamname is '/carplay/isConnected'	
			""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			data_list = []    
			for row in all_rows:
				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

			description = ''
			report = ArtifactHtmlReport('KnowledgeC Car Play Connections')
			report.start_artifact_report(report_folder, 'Car Play Connections', description)
			report.add_script()
			data_headers = ('Start','End','Car Play Connected','Usage in Seconds','Usage in Minutes','Day of Week','GMT Offset','Entry Creation')     
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Car Play Connections'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Car Play Connections'
			timeline(report_folder, tlactivity, data_list, data_headers)
		else:
			logfunc('No data available in Car Play Connections')

	if version.parse(iOSversion) >= version.parse("13"):
		cursor.execute("""
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		zsource.zbundleid,
		zobject.zvaluestring,
		(zobject.zenddate - zobject.zstartdate),
		(zobject.zenddate - zobject.zstartdate)/60.00,  
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end, 
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate+978307200,'unixepoch')
		from
		zobject, zsource 
		where zobject.zsource = zsource.z_pk 
		and zstreamname = '/disk/subsystemAccess'
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			data_list = []    
			for row in all_rows:
				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))

			description = ''
			report = ArtifactHtmlReport('KnowledgeC Disk Subsystem Access')
			report.start_artifact_report(report_folder, 'Disk Subsystem Access', description)
			report.add_script()
			data_headers = ('Start','End','Bundle ID','Value String','Usage in Seconds','Usage in Minutes','Day of Week','GMT Offset','Entry Creation')     
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Disk Subsystem Access'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Disk Subsystem Access'
			timeline(report_folder, tlactivity, data_list, data_headers)
		else:
			logfunc('No data available in Disk Subsystem Access')
			
	if version.parse(iOSversion) >= version.parse("12"):
		cursor.execute("""
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		zobject.zvalueinteger,
		(zobject.zenddate - zobject.zstartdate),
		(zobject.zenddate - zobject.zstartdate)/60.00,   
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end,
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate+978307200,'unixepoch')
		from
		zobject 
		where
		zstreamname = '/inferred/motion' 	
			""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			data_list = []    
			for row in all_rows:
				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

			description = ''
			report = ArtifactHtmlReport('KnowledgeC Do Not Disturb')
			report.start_artifact_report(report_folder, 'Do Not Disturb', description)
			report.add_script()
			data_headers = ('Start','End','Value','Usage in Seconds','Usage in Minutes','Day of Week','GMT Offset','Entry Creation')     
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Do Not Disturb'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Do Not Disturb'
			timeline(report_folder, tlactivity, data_list, data_headers)
		else:
			logfunc('No data available in Do Not Disturb')
	
	data_list = []
	if version.parse(iOSversion) >= version.parse("11"):
			

		extension = ".bplist"
		dump = True
		# create directories
		outpath = report_folder

		try:
			os.mkdir(os.path.join(report_folder, "clean"))
			os.mkdir(os.path.join(report_folder, "dirty"))
		except OSError:
			logfunc("Error making directories")
		file_found = str(files_found[0])
		# connect sqlite databases
		db = open_sqlite_db_readonly(file_found)
		cursor = db.cursor()

		# variable initializations
		dirtcount = 0
		cleancount = 0
		intentc = {}
		intentv = {}

		cursor.execute(
			"""
		SELECT
		Z_PK,
		Z_DKINTENTMETADATAKEY__SERIALIZEDINTERACTION,
		Z_DKINTENTMETADATAKEY__INTENTCLASS,
		Z_DKINTENTMETADATAKEY__INTENTVERB
		FROM ZSTRUCTUREDMETADATA
		WHERE Z_DKINTENTMETADATAKEY__SERIALIZEDINTERACTION is not null
		"""
		)

		all_rows = cursor.fetchall()

		for row in all_rows:
			pkv = str(row[0])
			pkvplist = pkv + extension
			f = row[1]
			intentclass = str(row[2])
			intententverb = str(row[3])
			output_file = open(os.path.join(outpath, "dirty", "D_Z_PK" + pkvplist), "wb") # export dirty from DB
			output_file.write(f)
			output_file.close()

			g = open(os.path.join(outpath, "dirty", "D_Z_PK" + pkvplist), "rb")
			plistg = ccl_bplist.load(g)

			if version.parse(iOSversion) < version.parse("12"):
				ns_keyed_archiver_objg = ccl_bplist.deserialise_NsKeyedArchiver(plistg)
				newbytearray = ns_keyed_archiver_objg
			else:
				ns_keyed_archiver_objg = ccl_bplist.deserialise_NsKeyedArchiver(plistg)
				newbytearray = ns_keyed_archiver_objg["NS.data"]

			dirtcount = dirtcount + 1

			binfile = open(os.path.join(outpath, "clean", "C_Z_PK" + pkvplist), "wb")
			binfile.write(newbytearray)
			binfile.close()

			# add to dictionaries
			intentc["C_Z_PK" + pkvplist] = intentclass
			intentv["C_Z_PK" + pkvplist] = intententverb

			cleancount = cleancount + 1
		'''
		h = open(outpath + "/StrucMetadata.html", "w")
		h.write("<html><body>")
		h.write(
			"<h2>iOS "
			+ iOSversion
			+ " - KnowledgeC ZSTRUCTUREDMETADATA bplist report</h2>"
		)
		h.write(
			"<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
		)
		h.write("<br/>")
		'''
		for filename in glob.glob(outpath + "/clean/*" + extension):
			p = open(filename, "rb")
			cfilename = os.path.basename(filename)
			plist = ccl_bplist.load(p)
			ns_keyed_archiver_obj = ccl_bplist.deserialise_NsKeyedArchiver(
				plist, parse_whole_structure=True
			)  # deserialize clean
			# Get dictionary values
			A = intentc.get(cfilename)
			B = intentv.get(cfilename)

			if A is None:
				A = "No value"
			if B is None:
				A = "No value"

			# logfunc some values from clean bplist
			if version.parse(iOSversion) >= version.parse("13"):
				try:
					NSdata = ns_keyed_archiver_obj["root"]["intent"]["backingStore"][
						"bytes"
					]
				except:
					NSdata = ns_keyed_archiver_obj["root"]["intent"]["backingStore"][
						"data"
					]["NS.data"]
					pass
			else:
				NSdata = ns_keyed_archiver_obj["root"]["intent"]["backingStore"][
					"data"
				]["NS.data"]
				# logfunc(str(NSdata))

			parsedNSData = ""
			# Default true
			if dump == True:
				nsdata_file = os.path.join(outpath, "clean", cfilename + "_nsdata.bin")
				binfile = open(nsdata_file, "wb")
				if version.parse(iOSversion) >= version.parse("13"):
					try:
						binfile.write(
							ns_keyed_archiver_obj["root"]["intent"]["backingStore"][
								"bytes"
							]
						)
					except:
						binfile.write(
							ns_keyed_archiver_obj["root"]["intent"]["backingStore"][
								"data"
							]["NS.data"]
						)
						pass
				else:
					binfile.write(
						ns_keyed_archiver_obj["root"]["intent"]["backingStore"]["data"][
							"NS.data"
						]
					)
				binfile.close()
				messages = ParseProto(nsdata_file)
				messages_json_dump = json.dumps(
					messages, indent=4, sort_keys=True, ensure_ascii=False
				)
				parsedNSData = str(messages_json_dump).encode(
					encoding="UTF-8", errors="ignore"
				)

			NSstartDate = ccl_bplist.convert_NSDate(
				(ns_keyed_archiver_obj["root"]["dateInterval"]["NS.startDate"])
			)
			NSendDate = ccl_bplist.convert_NSDate(
				(ns_keyed_archiver_obj["root"]["dateInterval"]["NS.endDate"])
			)
			NSduration = ns_keyed_archiver_obj["root"]["dateInterval"]["NS.duration"]
			Siri = ns_keyed_archiver_obj["root"]["_donatedBySiri"]
			

			if parsedNSData:
				parsedf = str(parsedNSData).replace("\\n", "<br>")
			else:
				parsedf = str(NSdata).replace("\\n", "<br>")
			
			data_list.append(( str(NSstartDate),str(A), str(B), str(Siri), str(NSendDate), str(NSduration), parsedf, (textwrap.fill(str(NSdata), width=50)), cfilename))

		logfunc("iOS - KnowledgeC ZSTRUCTUREDMETADATA bplist extractor")
		logfunc("By: @phillmoore & @AlexisBrignoni")
		logfunc("thinkdfir.com & abrignoni.com")
		logfunc("")
		logfunc("Bplists from the Z_DKINTENTMETADATAKEY__SERIALIZEDINTERACTION field.")
		logfunc("Exported bplists (dirty): " + str(dirtcount))
		logfunc("Exported bplists (clean): " + str(cleancount))
		logfunc("")
		logfunc("Incepted bplist extractions in KnowledgeC.db completed")
		
		description = ''
		report = ArtifactHtmlReport('KnowledgeC Intents')
		report.start_artifact_report(report_folder, 'Intents', description)
		report.add_script()
		data_headers = ('NS Start Date','Intent Class','Intent Verb','Siri?','NS Send Date','NS Duration','NS Data Protobuf', 'NS Data', 'Traceback' )     
		report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
		report.end_artifact_report()
		
		tlactivity = 'KnowledgeC Intents'
		timeline(report_folder, tlactivity, data_list, data_headers)

	if version.parse(iOSversion) >= version.parse("9"):
		cursor = db.cursor()	
		cursor.execute('''
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		zobject.zvaluestring, 
		(zobject.zenddate-zobject.zstartdate),
		(zobject.zenddate-zobject.zstartdate)/60.00,
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end,
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate+978307200,'unixepoch')
		from zobject
		where zstreamname is '/app/inFocus'
		''')
	
	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	if usageentries > 0:
		data_list = []
		if version.parse(iOSversion) >= version.parse("9"):
			for row in all_rows:    
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))

			report = ArtifactHtmlReport('KnowledgeC Application In Focus')
			report.start_artifact_report(report_folder, 'App In Focus')
			report.add_script()
			data_headers = ('Start','End','Bundle ID', 'Usage in Seconds', 'Usage in Minutes','Day of Week','GMT Offset','Entry Creation')  
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Application in Focus'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Application in Focus'
			timeline(report_folder, tlactivity, data_list, data_headers)
		
	else:
		logfunc('No data available in Application in Focus')
	
	if version.parse(iOSversion) >= version.parse("12"):			
		cursor.execute('''
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		zobject.zvaluestring, 
		zstructuredmetadata .z_dkappinstallmetadatakey__primarycategory,
		zstructuredmetadata .z_dkappinstallmetadatakey__title,
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end,
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate+978307200,'unixepoch')
		from
		zobject, zstructuredmetadata 
		where zobject.zstructuredmetadata = zstructuredmetadata.z_pk 
		and zstreamname = '/app/install'
			''')
	else:
		cursor.execute('''
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		zobject.zvaluestring,
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end,
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate+978307200,'unixepoch')
		from
		zobject, zstructuredmetadata 
		where zobject.zstructuredmetadata = zstructuredmetadata.z_pk 
		and zstreamname = "/app/install"
		''')

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	if usageentries > 0:
		data_list = []
		if version.parse(iOSversion) >= version.parse("12"):
					
			for row in all_rows:    
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))

			report = ArtifactHtmlReport('KnowledgeC Installed Apps')
			report.start_artifact_report(report_folder, 'Installed Apps')
			report.add_script()
			data_headers = ('Start','End','Bundle ID','App Category', 'App Name','Day of Week','GMT Offset','Entry Creation')  
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Installed Apps'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Installed Apps'
			timeline(report_folder, tlactivity, data_list, data_headers)
		else:
			for row in all_rows:    
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5]))
					
			report = ArtifactHtmlReport('KnowledgeC Installed Apps')
			report.start_artifact_report(report_folder, 'Installed Apps')
			report.add_script()
			data_headers = ('Start','End','Bundle ID','Day of Week','GMT Offset','Entry Creation' ) 
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Installed Apps'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Installed Apps'
			timeline(report_folder, tlactivity, data_list, data_headers)
	else:
		logfunc('No data available in Installed Apps')
		
	if version.parse(iOSversion) >= version.parse("12"):			
		cursor.execute("""
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		zobject.zvaluestring, 
		zstructuredmetadata.z_dklocationapplicationactivitymetadatakey__locationname,
		zstructuredmetadata.z_dklocationapplicationactivitymetadatakey__displayname,
		zstructuredmetadata.z_dklocationapplicationactivitymetadatakey__fullyformattedaddress,
		zstructuredmetadata.z_dklocationapplicationactivitymetadatakey__city,
		zstructuredmetadata.z_dklocationapplicationactivitymetadatakey__stateorprovince,
		zstructuredmetadata.z_dklocationapplicationactivitymetadatakey__country,
		zstructuredmetadata.z_dklocationapplicationactivitymetadatakey__postalcode_v2,
		zstructuredmetadata.z_dklocationapplicationactivitymetadatakey__subthoroughfare,
		zstructuredmetadata.z_dklocationapplicationactivitymetadatakey__thoroughfare,
		zstructuredmetadata.z_dklocationapplicationactivitymetadatakey__phonenumbers,
		zstructuredmetadata.z_dklocationapplicationactivitymetadatakey__url,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__activitytype, 
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__contentdescription,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__useractivityrequiredstring,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__itemrelatedcontenturl,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__itemrelateduniqueidentifier,
		zstructuredmetadata.z_dklocationapplicationactivitymetadatakey__latitude,
		zstructuredmetadata.z_dklocationapplicationactivitymetadatakey__longitude,
		zsource.zsourceid,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__useractivityuuid,
		zsource.zitemid,
		zsource.zsourceid,
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end,
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate+978307200,'unixepoch')
		from
		zobject, zstructuredmetadata, zsource 
		where zobject.zstructuredmetadata = zstructuredmetadata.z_pk 
		and zobject.zsource = zsource.z_pk 
		and zstreamname = '/app/locationActivity'
		"""
		)

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			data_list = []
			for row in all_rows:
				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27]))

			description = ''
			report = ArtifactHtmlReport('KnowledgeC Location Activity')
			report.start_artifact_report(report_folder, 'Location Activity', description)
			report.add_script()
			data_headers = ('Timestamp','End','Bundle ID','Name','Display Name','Formatted Address', 'City','State/Province','Country','Postal Code','Subthoroughfare','Thoroughfare','Phone Numebers','URL','Activity Type', 'Content Description','User Activity Required String','Content URL','Unique ID','Latitude','Longitude','Source ID','Activity UUID','Item ID','Source ID','Day of the Week','GMT Offset','Entry Creation')     
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Location Activity'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Location Activity'
			timeline(report_folder, tlactivity, data_list, data_headers)
			
			kmlactivity = 'KnowledgeC Location Activity'
			kmlgen(report_folder, kmlactivity, data_list, data_headers)
		else:
			logfunc('No data available in Location Activity')
			
	if version.parse(iOSversion) >= version.parse("11"):
		cursor.execute("""
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		case zobject.zvalueinteger
		when '0' then 'unlocked' 
		when '1' then 'locked' 
		end,
		(zobject.zenddate - zobject.zstartdate),  
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end,
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate+978307200,'unixepoch')
		from
		zobject
		where zstreamname = '/device/isLocked'
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			data_list = []
			for row in all_rows:
				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6]))

			description = ''
			report = ArtifactHtmlReport('KnowledgeC Device Locked')
			report.start_artifact_report(report_folder, 'Device Locked', description)
			report.add_script()
			data_headers = ('Start','End','Is Locked?','Usage in Seconds','Day of the Week','GMT Offset','Entry Creation' )     
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Device Locked'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Device Locked'
			timeline(report_folder, tlactivity, data_list, data_headers)
		else:
			logfunc('No data in KnowledgeC Device Locked')
		
	if version.parse(iOSversion) >= version.parse("11"):	
		cursor.execute("""
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		zobject.zvaluestring, 
		zstructuredmetadata.z_dknowplayingmetadatakey__album, 
		zstructuredmetadata.z_dknowplayingmetadatakey__artist, 
		zstructuredmetadata.z_dknowplayingmetadatakey__genre, 
		zstructuredmetadata.z_dknowplayingmetadatakey__title, 
		zstructuredmetadata.z_dknowplayingmetadatakey__duration,
		(zobject.zenddate - zobject.zstartdate),
		(zobject.zenddate - zobject.zstartdate)/60.00,    
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end,
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate+978307200,'unixepoch')
		from
		zobject, zstructuredmetadata 
		where zobject.zstructuredmetadata = zstructuredmetadata.z_pk 
		and zstreamname =  '/media/nowPlaying'
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			data_list = []    
			for row in all_rows:
				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12]))

			description = ''
			report = ArtifactHtmlReport('KnowledgeC Media Playing')
			report.start_artifact_report(report_folder, 'Media Playing', description)
			report.add_script()
			data_headers = ('Start','End','Bundle ID','Now Playing Album','Now Playing Artists','Playing Genre','Playing Title', 'Now Playing Duration','Usage in Seconds','Usage in Minutes','Day of Week','GMT Offset','Entry Creation')     
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Media Playing'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Media Playing'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No data available in Media Playing')

	if version.parse(iOSversion) >= version.parse("12"):	
		cursor.execute('''
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		zobject.zvaluestring,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__activitytype, 
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__useractivityrequiredstring,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__itemidentifier,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__itemrelateduniqueidentifier,
		zstructuredmetadata.z_dkapplicationactivitymetadatakey__useractivityuuid,
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end,
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate + 978307200, 'unixepoch'),
		datetime(zstructuredmetadata.z_dkapplicationactivitymetadatakey__expirationdate + 978307200, 'unixepoch')
		from
		zobject, zstructuredmetadata 
		where zobject.zstructuredmetadata = zstructuredmetadata.z_pk 
		and zstreamname = '/app/activity'
		and (zobject.zvaluestring = 'com.apple.mobilenotes' or zobject.zvaluestring = 'com.apple.Notes')
		''')
		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			data_list = []
			for row in all_rows:    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]))

			report = ArtifactHtmlReport('KnowledgeC Notes - Activity')
			report.start_artifact_report(report_folder, 'Notes - Activity')
			report.add_script()
			data_headers = ('Start','End','Bundle ID','Activity Type','User Activity Required String','ID','Unique ID','Activity UUID','Day of Week','GMT Offset','Entry Creation','Expiration Date' )   
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Notes Activity'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Notes Activity'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No data available in Notes Activity')
	
	if version.parse(iOSversion) >= version.parse("11"):		
		cursor.execute("""
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		case zobject.zvalueinteger
		when '0' then 'portrait' 
		when '1' then 'landscape' 
		else zobject.zvalueinteger
		end,
		(zobject.zenddate - zobject.zstartdate),
		(zobject.zenddate - zobject.zstartdate)/60.00,   
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end,
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate+978307200,'unixepoch')
		from
		zobject 
		where
		zstreamname = '/display/orientation'	
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			data_list = []    
			for row in all_rows:
				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

			description = ''
			report = ArtifactHtmlReport('KnowledgeC Screen Orientation')
			report.start_artifact_report(report_folder, 'Screen Orientation', description)
			report.add_script()
			data_headers = ('Start','End','Orientation','Usage in Seconds','Usage in Minutes','Day of Week','GMT Offset','Entry Creation')     
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Screen Orientation'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Screen Orientation'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No data available in Screen Orientation')
			
	if version.parse(iOSversion) >= version.parse("11"):
		cursor.execute("""
			select
			datetime(zobject.zstartdate+978307200,'unixepoch') , 
			datetime(zobject.zenddate+978307200,'unixepoch'), 
			case
			zobject.zvalueinteger
			when '0' then 'unplugged' 
			when '1' then 'plugged in' 
			end,
			(zobject.zenddate - zobject.zstartdate),  
			case zobject.zstartdayofweek 
			when '1' then 'sunday'
			when '2' then 'monday'
			when '3' then 'tuesday'
			when '4' then 'wednesday'
			when '5' then 'thursday'
			when '6' then 'friday'
			when '7' then 'saturday'
			end,
			zobject.zsecondsfromgmt/3600,
			datetime(zobject.zcreationdate+978307200,'unixepoch')
			from
			zobject 
			where
			zstreamname = '/device/isPluggedIn'
			""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			data_list = []    
			for row in all_rows:
				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6]))

			description = ''
			report = ArtifactHtmlReport('KnowledgeC Plugged In')
			report.start_artifact_report(report_folder, 'Plugged In', description)
			report.add_script()
			data_headers = ('Start','End','Is Plugged In?','Usage in Seconds','Day of the Week','GMT Offset','Entry Creation' )     
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Plugged In'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Plugged In'
			timeline(report_folder, tlactivity, data_list, data_headers)
		else:
			logfunc('No data in KnowledgeC Plugged In')

	if version.parse(iOSversion) >= version.parse("12"):
		cursor = db.cursor()	
		cursor.execute('''
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		zstructuredmetadata.z_dksafarihistorymetadatakey__title,
		zobject.zvaluestring, 
		zsource.zbundleid,
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end, 
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate+978307200,'unixepoch')
		from
		zobject,
		zstructuredmetadata, zsource 
		where zobject.zstructuredmetadata = zstructuredmetadata.z_pk 
		and  zobject.zsource = zsource.z_pk 
		and zstreamname = '/safari/history'
		''')
	elif version.parse(iOSversion) == version.parse("11"):
		cursor = db.cursor()	
		cursor.execute('''
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		zobject.zvaluestring, 
		zsource.zbundleid,
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end, 
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate+978307200,'unixepoch')
		from
		zobject, zsource
		where zobject.zsource = zsource.z_pk 
		and zstreamname = '/safari/history'	
		''')
	else:
		logfunc("Unsupported version for KnowledgC Safari iOS " + iOSversion)
		return ()
		
	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	if usageentries > 0:
		data_list = []
		if version.parse(iOSversion) >= version.parse("12"):
					
			for row in all_rows:    
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))

			report = ArtifactHtmlReport('KnowledgeC Safari Browsing')
			report.start_artifact_report(report_folder, 'Safari Browsing')
			report.add_script()
			data_headers = ('Start','End','Title','URL', 'Bundle ID','Day of Week','GMT Offset','Entry Creation')  
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Safari Browsing'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Safari Browsing'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			for row in all_rows:    
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
					
			report = ArtifactHtmlReport('KnowledgeC Safari Browsing')
			report.start_artifact_report(report_folder, 'Safari Browsing')
			report.add_script()
			data_headers = ('Start','End','URL','Bundle ID','Day of Week','GMT Offset','Entry Creation' ) 
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Safari Browsing'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Safari Browsing'
			timeline(report_folder, tlactivity, data_list, data_headers)

	else:
		logfunc('No data available in Safari Browsing')
		
	if version.parse(iOSversion) >= version.parse("12"):	
		cursor.execute("""
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		zobject.zvaluestring,  
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end,
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate+978307200,'unixepoch')
		from
		zobject 
		where
		zstreamname =  '/siri/ui' 
		"""
		)

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			data_list = []   
			for row in all_rows:
				data_list.append((row[0], row[1], row[2], row[3], row[4]))

			description = ''
			report = ArtifactHtmlReport('KnowledgeC Siri Usage')
			report.start_artifact_report(report_folder, 'Siri Usage', description)
			report.add_script()
			data_headers = ('Start','App Name','Weekday','GMT Offset','Entry Creation' )     
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Siri Usage'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Siri Usage'
			timeline(report_folder, tlactivity, data_list, data_headers)
		else:
			logfunc('No data in KnowledgeC Siri Usage')
	
	if version.parse(iOSversion) >= version.parse("12"):	
		cursor.execute("""
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		zobject.zvaluestring, 
		(zobject.zenddate - zobject.zstartdate),
		(zobject.zenddate - zobject.zstartdate)/60.00,  
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end,
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate+978307200,'unixepoch')
		from
		zobject
		where zstreamname = '/app/usage' 
		""")
	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	if usageentries > 0:
		data_list = []    
		for row in all_rows:
			data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

		description = ''
		report = ArtifactHtmlReport('KnowledgeC App Usage')
		report.start_artifact_report(report_folder, 'App Usage', description)
		report.add_script()
		data_headers = ('Start','End','Bundle ID','Usage in Seconds','Usage in Minutes','Day of the Week','GMT Offset','Entry Creation')     
		report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
		report.end_artifact_report()
		
		tsvname = 'KnowledgeC App Usage'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'KnowledgeC App Usage'
		timeline(report_folder, tlactivity, data_list, data_headers)
	else:
		logfunc('No data in KnowledgeC App Usage')

	if version.parse(iOSversion) >= version.parse("12"):
		cursor.execute("""
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end,
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate+978307200,'unixepoch')
		from
		zobject 
		where zstreamname = '/system/userWakingEvent'
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			data_list = []    
			for row in all_rows:
				data_list.append((row[0], row[1], row[2], row[3], row[4]))

			description = ''
			report = ArtifactHtmlReport('KnowledgeC User Waking Event')
			report.start_artifact_report(report_folder, 'User Waking Event', description)
			report.add_script()
			data_headers = ('Start','End','Day of Week','GMT Offset','Entry Creation')     
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC User Waking Events'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC User Waking Events'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No data available in User Waking Event')
			
	if version.parse(iOSversion) >= version.parse("12"):
		cursor.execute("""
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		zobject.zvaluestring, 
		(zobject.zenddate - zobject.zstartdate),
		(zobject.zenddate - zobject.zstartdate)/60.00,   
		zstructuredmetadata .z_dkdigitalhealthmetadatakey__webdomain,
		zstructuredmetadata .z_dkdigitalhealthmetadatakey__webpageurl,
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end,
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate+978307200,'unixepoch')
		from
		zobject, zstructuredmetadata 
		where zobject.zstructuredmetadata = zstructuredmetadata.z_pk 
		and zstreamname = '/app/webUsage'
		"""
		)

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			data_list = []    
			for row in all_rows:
				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))

			description = ''
			report = ArtifactHtmlReport('KnowledgeC Web Usage')
			report.start_artifact_report(report_folder, 'Web Usage', description)
			report.add_script()
			data_headers = ('Start','End','App Name','Usage in Seconds','Usage in Minutes','Domain','URL','Day of the Wekk','GMT Offset','Entry Creation')     
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Web Usage'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Web Usage'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No data available in Web Usage')

	if version.parse(iOSversion) < version.parse("12"):
		cursor.execute("""
		select
		datetime(zobject.zstartdate+978307200,'unixepoch'), 
		datetime(zobject.zenddate+978307200,'unixepoch'),
		zobject.zvaluestring,  
		(zobject.zenddate - zobject.zstartdate),
		(zobject.zenddate - zobject.zstartdate)/60.00,   
		case zobject.zstartdayofweek 
		when '1' then 'sunday'
		when '2' then 'monday'
		when '3' then 'tuesday'
		when '4' then 'wednesday'
		when '5' then 'thursday'
		when '6' then 'friday'
		when '7' then 'saturday'
		end,
		zobject.zsecondsfromgmt/3600,
		datetime(zobject.zcreationdate+978307200,'unixepoch')
		from
		zobject 
		where
		zstreamname = '/widgets/viewed'
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			data_list = []    
			for row in all_rows:
				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

			description = ''
			report = ArtifactHtmlReport('KnowledgeC Widgets Viewed')
			report.start_artifact_report(report_folder, 'Widgets Viewed', description)
			report.add_script()
			data_headers = ('Start','End','Bundle ID','Usage in Seconds','Usage in Minutes','Day of Week','GMT Offset','Entry Creation')     
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Widgets Viewed'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Widgets Viewed'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No data available in Widgets Viewed')
