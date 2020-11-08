import glob
import os
import pathlib
import plistlib
import sqlite3
import json
from packaging import version
import scripts.artifacts.artGlobals

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, kmlgen, timeline, is_platform_windows 


def get_knowClocation(files_found, report_folder, seeker):
	iOSversion = scripts.artifacts.artGlobals.versionf
	if version.parse(iOSversion) < version.parse("12"):
		logfunc("Unsupported version for KnowledgC Location on iOS " + iOSversion)
		return ()

	file_found = str(files_found[0])
	db = sqlite3.connect(file_found)
	cursor = db.cursor()
	# The following SQL query is taken from https://github.com/mac4n6/APOLLO/blob/master/modules/knowledge_app_location_activity.txt
	# from Sarah Edward's APOLLO project, and used under terms of its license found under Licenses/apollo.LICENSE.txt	
	cursor.execute(
	"""
	SELECT
		DATETIME(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH') AS "START", 
      	DATETIME(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH') AS "END",
		ZOBJECT.ZVALUESTRING AS "BUNDLE ID", 
		ZSTRUCTUREDMETADATA.Z_DKLOCATIONAPPLICATIONACTIVITYMETADATAKEY__LATITUDE || ", " || ZSTRUCTUREDMETADATA.Z_DKLOCATIONAPPLICATIONACTIVITYMETADATAKEY__LONGITUDE AS "COORDINATES",
		ZSTRUCTUREDMETADATA.Z_DKLOCATIONAPPLICATIONACTIVITYMETADATAKEY__LOCATIONNAME AS "NAME",
		ZSTRUCTUREDMETADATA.Z_DKLOCATIONAPPLICATIONACTIVITYMETADATAKEY__DISPLAYNAME AS "DISPLAY NAME",
		ZSTRUCTUREDMETADATA.Z_DKLOCATIONAPPLICATIONACTIVITYMETADATAKEY__FULLYFORMATTEDADDRESS AS "FORMATTED ADDRESS",
		ZSTRUCTUREDMETADATA.Z_DKLOCATIONAPPLICATIONACTIVITYMETADATAKEY__CITY AS "CITY",
		ZSTRUCTUREDMETADATA.Z_DKLOCATIONAPPLICATIONACTIVITYMETADATAKEY__STATEORPROVINCE AS "STATE/PROVINCE",
		ZSTRUCTUREDMETADATA.Z_DKLOCATIONAPPLICATIONACTIVITYMETADATAKEY__COUNTRY AS "COUNTRY",
		ZSTRUCTUREDMETADATA.Z_DKLOCATIONAPPLICATIONACTIVITYMETADATAKEY__POSTALCODE_V2 AS "POSTAL CODE",
		ZSTRUCTUREDMETADATA.Z_DKLOCATIONAPPLICATIONACTIVITYMETADATAKEY__SUBTHOROUGHFARE AS "SUBTHOROUGHFARE",
		ZSTRUCTUREDMETADATA.Z_DKLOCATIONAPPLICATIONACTIVITYMETADATAKEY__THOROUGHFARE AS "THOROUGHFARE",
		ZSTRUCTUREDMETADATA.Z_DKLOCATIONAPPLICATIONACTIVITYMETADATAKEY__PHONENUMBERS AS "PHONE NUMBERS",
		ZSTRUCTUREDMETADATA.Z_DKLOCATIONAPPLICATIONACTIVITYMETADATAKEY__URL AS "URL",
		ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__ACTIVITYTYPE AS "ACTIVITY TYPE", 
		ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__CONTENTDESCRIPTION AS "CONTENT DESCRIPTION",
		ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__USERACTIVITYREQUIREDSTRING AS "USER ACTIVITY REQUIRED STRING",
		ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__ITEMRELATEDCONTENTURL AS "CONTENT URL",
		ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__ITEMRELATEDUNIQUEIDENTIFIER AS "UNIQUE ID",
		ZSTRUCTUREDMETADATA.Z_DKLOCATIONAPPLICATIONACTIVITYMETADATAKEY__LATITUDE AS "LATITUDE",
		ZSTRUCTUREDMETADATA.Z_DKLOCATIONAPPLICATIONACTIVITYMETADATAKEY__LONGITUDE AS "LONGITUDE",
		ZSOURCE.ZSOURCEID AS "SOURCE ID",
		ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__USERACTIVITYUUID AS "ACTIVITY UUID",
		ZSOURCE.ZITEMID AS "ITEM ID",
		ZSOURCE.ZSOURCEID AS "SOURCE ID",
      CASE ZOBJECT.ZSTARTDAYOFWEEK 
         WHEN "1" THEN "Sunday"
         WHEN "2" THEN "Monday"
         WHEN "3" THEN "Tuesday"
         WHEN "4" THEN "Wednesday"
         WHEN "5" THEN "Thursday"
         WHEN "6" THEN "Friday"
         WHEN "7" THEN "Saturday"
      END "DAY OF WEEK",
      ZOBJECT.ZSECONDSFROMGMT/3600 AS "GMT OFFSET",
      DATETIME(ZOBJECT.ZCREATIONDATE+978307200,'UNIXEPOCH') AS "ENTRY CREATION", 
      ZOBJECT.ZUUID AS "UUID",
      ZOBJECT.Z_PK AS "ZOBJECT TABLE ID" 
   FROM
      ZOBJECT 
      LEFT JOIN
         ZSTRUCTUREDMETADATA 
         ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK 
      LEFT JOIN
         ZSOURCE 
         ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK 
   WHERE
      ZSTREAMNAME = "/app/locationActivity" 
	"""
	)

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	if usageentries > 0:
		data_list = []    
		for row in all_rows:
			data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27], row[28], row[29], row[30]))

		description = ''
		report = ArtifactHtmlReport('KnowledgeC Location Activity')
		report.start_artifact_report(report_folder, 'Location Activity', description)
		report.add_script()
		data_headers = ('Timestamp','End','Bundle ID','Coordinates','Name','Display Name','Formatted Address', 'City','State/Province','Country','Postal Code','Subthoroughfare','Thoroughfare','Phone Numebers','URL','Activity Type', 'Content Description','User Activity Required String','Content URL','Unique ID','Latitude','Longitude','Source ID','Activity UUID','Item ID','Source ID','Day of the Week','GMT Offset','Entry Creation','UUID','Zonject Table ID')     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'KnowledgeC Location Activity'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'KnowledgeC Location Activity'
		timeline(report_folder, tlactivity, data_list, data_headers)
		
		kmlactivity = 'KnowledgeC Location Activity'
		kmlgen(report_folder, kmlactivity, data_list, data_headers)
	else:
		logfunc('No data available for KnowledgeC Location Activity')
	
