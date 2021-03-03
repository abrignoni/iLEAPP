import glob
import os
import sys
import stat
import pathlib
import plistlib
import sqlite3
import json
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, open_sqlite_db_readonly, does_table_exist


def get_locationDallB(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	db = open_sqlite_db_readonly(file_found)
	iOSversion = scripts.artifacts.artGlobals.versionf
	if version.parse(iOSversion) >= version.parse("11"):
		logfunc("Unsupported version for LocationD App Harvest on iOS " + iOSversion)
	else:
		logfunc(iOSversion)
		cursor = db.cursor()
		cursor.execute("""
		select
		datetime(timestamp + 978307200,'unixepoch'),
		bundleid,
		altitude,
		horizontalaccuracy,
		verticalaccuracy,
		state,
		age,
		routinemode,
		locationofinteresttype,
		latitude,
		longitude,
		speed,
		course,
		confidence
		from appharvest
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []    
		if usageentries > 0:
			for row in all_rows:
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13]))

			description = ''
			report = ArtifactHtmlReport('LocationD App Harvest')
			report.start_artifact_report(report_folder, 'App Harvest', description)
			report.add_script()
			data_headers = ('Timestamp','Bundle ID','Altitude','Horizontal Accuracy','Vertical Accuracy','State','Age','Routine Mode','Location of Interest Type','Latitude','Longitude','Speed','Course','Confidence')     
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'LocationD Cell App Harvest'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'LocationD Cell App Harvest'
			timeline(report_folder, tlactivity, data_list, data_headers)
			
			kmlactivity = 'LocationD Cell App Harvest'
			kmlgen(report_folder, kmlactivity, data_list, data_headers)
		else:
			logfunc('No data available for LocationD App Harvest')
			
	if does_table_exist(db, "cdmacelllocation"):
		cursor = db.cursor()
		cursor.execute("""
		select
		datetime(timestamp + 978307200,'unixepoch'),
		mcc,
		sid,
		nid,
		bsid,
		zoneid,
		bandclass,
		channel,
		pnoffset,
		altitude,
		speed,
		course,
		confidence,
		horizontalaccuracy,
		verticalaccuracy,
		latitude,
		longitude
		from cdmacelllocation
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []    
		if usageentries > 0:
			for row in all_rows:
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16]))
		
			description = ''
			report = ArtifactHtmlReport('LocationD CDMA Location')
			report.start_artifact_report(report_folder, 'CDMA Location', description)
			report.add_script()
			data_headers = ('Timestamp','MCC','SID','NID','BSID','ZONEID','BANDCLASS','Channel','PNOFFSET','Altitude','Speed','Course','Confidence','Horizontal Accuracy','Vertical Accuracy','Latitude','Longitude')     
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'LocationD CDMA Location'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'LocationD CDMA Location'
			timeline(report_folder, tlactivity, data_list, data_headers)
			
			kmlactivity = 'LocationD CDMA Location'
			kmlgen(report_folder, kmlactivity, data_list, data_headers)
		else:
			logfunc('No data available for LocationD CDMA Location')
	
	if does_table_exist(db, "celllocation"):
		cursor = db.cursor()
		cursor.execute("""
		select
		datetime(timestamp + 978307200,'unixepoch'),
		mcc,
		mnc,
		lac,
		ci,
		uarfcn,
		psc,
		altitude,
		speed,
		course,
		confidence,
		horizontalaccuracy,
		verticalaccuracy,
		latitude,
		longitude
		from celllocation
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []    
		if usageentries > 0:
			for row in all_rows:
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14]))
		
			description = ''
			report = ArtifactHtmlReport('LocationD Cell Location')
			report.start_artifact_report(report_folder, 'Cell Location', description)
			report.add_script()
			data_headers = ('Timestamp','MCC','MNC','LAC','CI','UARFCN','PSC','Altitude','Speed','Course','Confidence','Horizontal Accuracy','Vertical Accuracy','Latitude','Longitude')     
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'LocationD Cell Location'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'LocationD Cell Location'
			timeline(report_folder, tlactivity, data_list, data_headers)
			
			kmlactivity = 'LocationD Cell Location'
			kmlgen(report_folder, kmlactivity, data_list, data_headers)
		else:
			logfunc('No data available for LocationD Cell Location')

	if does_table_exist(db, "ltecelllocation"):
		cursor = db.cursor()
		cursor.execute("""
		select 
		datetime(timestamp + 978307200,'unixepoch'),
		mcc,
		mnc,
		ci,
		uarfcn,
		pid,
		altitude,
		speed,
		course,
		confidence,
		horizontalaccuracy,
		verticalaccuracy,
		latitude,
		longitude
		from ltecelllocation	
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []    
		if usageentries > 0:
			for row in all_rows:
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13]))
		
			description = ''
			report = ArtifactHtmlReport('LocationD LTE Location')
			report.start_artifact_report(report_folder, 'LTE Location', description)
			report.add_script()
			data_headers = ('Timestamp','MCC','MNC','CI','UARFCN','PID','Altitude','Speed','Course','Confidence','Horizontal Accuracy','Vertical Accuracy','Latitude','Longitude')     
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'LocationD LTE Location'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'LocationD LTE Location'
			timeline(report_folder, tlactivity, data_list, data_headers)
			
			kmlactivity = 'LocationD LTE Location'
			kmlgen(report_folder, kmlactivity, data_list, data_headers)
		else:
			logfunc('No data available for LocationD LTE Location')

	cursor = db.cursor()
	cursor.execute("""
	select
	datetime(timestamp + 978307200,'unixepoch'),
	mac,
	channel,
	infomask,
	speed,
	course,
	confidence,
	score,
	reach,
	horizontalaccuracy,
	verticalaccuracy,
	latitude,
	longitude
	from wifilocation
	""")

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []    
	if usageentries > 0:
		for row in all_rows:
			data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]))
	
		description = ''
		report = ArtifactHtmlReport('LocationD WiFi Location')
		report.start_artifact_report(report_folder, 'WiFi Location', description)
		report.add_script()
		data_headers = ('Timestamp','MAC','Channel','Infomask','Speed','Course','Confidence','Score','Reach','Horizontal Accuracy','Vertical Accuracy','Latitude','Longitude')     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'LocationD WiFi Location'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'LocationD WiFi Location'
		timeline(report_folder, tlactivity, data_list, data_headers)
		
		kmlactivity = 'LocationD WiFi Location'
		kmlgen(report_folder, kmlactivity, data_list, data_headers)
	else:
		logfunc('No data available for LocationD WiFi Location')
	