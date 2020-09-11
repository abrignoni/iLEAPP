import gzip
import re
import os
import shutil
import sqlite3
from pathlib import Path
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, tsv, is_platform_windows 


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
				logfunc(str(filename.stem))
				file_found = str(Path(filename.parent))
				
				db = sqlite3.connect(ungzipedfile)
				cursor = db.cursor()
				
			if version.parse(iOSversion) >= version.parse("9"):
				cursor.execute('''
				SELECT
					DATETIME(TIMESTAMP, 'UNIXEPOCH') AS TIMESTAMP,
					DATETIME(TIMESTAMPLOGGED, 'UNIXEPOCH') AS "TIMESTAMP LOGGED",
					APPLICATIONNAME AS "APPLICATION NAME / BUNDLE ID",
					ASSERTIONID AS "ASERTION ID",
					ASSERTIONNAME AS "ASSERTION NAME",
					AUDIOROUTE AS "AUDIO ROUTE",
					MIRRORINGSTATE AS "MIRRORING STATE",
					OPERATION,
					PID,
					ID AS "PLAUDIOAGENT_EVENTPOINT_AUDIOAPP TABLE ID" 
					FROM
					PLAUDIOAGENT_EVENTPOINT_AUDIOAPP
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
				SELECT
					DATETIME(TIMESTAMP, 'UNIXEPOCH') AS TIMESTAMP,
					BULLETINBUNDLEID AS "BULLETIN BUNDLE ID",
					TIMEINTERVAL / 60 AS "TIME INTERVAL IN SECONDS",
					COUNT AS "COUNT",
					POSTTYPE AS "POST TYPE",
					ID AS "PLSPRINGBOARDAGENT_AGGREGATE_SBBULLETINS_AGGREGATE TABLE ID" 
				FROM
					PLSPRINGBOARDAGENT_AGGREGATE_SBBULLETINS_AGGREGATE
				''')
				all_rows = cursor.fetchall()
				usageentries = len(all_rows)
				if usageentries > 0:
					for row in all_rows:    
						data_list2.append((row[0],row[1],row[2],row[3],row[4],row[5]))
				else:
					logfunc('No data available in Aggregate Bulletins')		
			
			if version.parse(iOSversion) >= version.parse("10"):
					cursor.execute('''
					SELECT
						DATETIME(TIMESTAMP, 'UNIXEPOCH') AS TIMESTAMP,
						NOTIFICATIONBUNDLEID AS "BULLETIN BUNDLE ID",
						TIMEINTERVAL / 60 AS "TIME INTERVAL IN SECONDS",
						COUNT AS "COUNT",
						NOTIFICATIONTYPE AS "NOTIFICATION TYPE",
						ID AS "PLSPRINGBOARDAGENT_AGGREGATE_SBNOTIFICATIONS_AGGREGATE TABLE ID" 
					FROM
						PLSPRINGBOARDAGENT_AGGREGATE_SBNOTIFICATIONS_AGGREGATE 
					''')
					all_rows = cursor.fetchall()
					usageentries = len(all_rows)
					if usageentries > 0:
						
						for row in all_rows:    
							data_list3.append((row[0],row[1],row[2],row[3],row[4],row[5]))				
					else:
						logfunc('No data available in Aggregate Notifications')
						
			if version.parse(iOSversion) >= version.parse("9"):
				cursor.execute('''
				SELECT
						DATETIME(AIRDROP_TIMESTAMP + SYSTEM, 'UNIXEPOCH') AS ADJUSTED_TIMESTAMP,
						STATE,
						SUBEVENT,
						BUNDLEID AS BUNDLE_ID,
						PID,
						DATETIME(AIRDROP_TIMESTAMP, 'UNIXEPOCH') AS ORIGINAL_AIRDROP_TIMESTAMP,
						DATETIME(TIME_OFFSET_TIMESTAMP, 'UNIXEPOCH') AS OFFSET_TIMESTAMP,
						SYSTEM AS TIME_OFFSET,
						AIRDROP_ID AS "PLXPCAGENT_EVENTFORWARD_AIRDROP TABLE ID"
					FROM
						(
						SELECT
							BUNDLEID,
							AIRDROP_ID,
							AIRDROP_TIMESTAMP,
							TIME_OFFSET_TIMESTAMP,
							MAX(TIME_OFFSET_ID) AS MAX_ID,
							SYSTEM,
							PID,
							SUBEVENT,
							STATE
						FROM
							(
						SELECT
							PLXPCAGENT_EVENTFORWARD_AIRDROP.TIMESTAMP AS AIRDROP_TIMESTAMP,
							PLXPCAGENT_EVENTFORWARD_AIRDROP.BUNDLEID,
							PLXPCAGENT_EVENTFORWARD_AIRDROP.PID,
							PLXPCAGENT_EVENTFORWARD_AIRDROP.SUBEVENT,
							PLXPCAGENT_EVENTFORWARD_AIRDROP.STATE,
							PLXPCAGENT_EVENTFORWARD_AIRDROP.ID AS "AIRDROP_ID",
							PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
							PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
							PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM,
							BUNDLEID 
						FROM
							PLXPCAGENT_EVENTFORWARD_AIRDROP 
						LEFT JOIN
							PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET 
							)
						AS AIRDROPSTATE 
						GROUP BY
							AIRDROP_ID 
						)
				''')
				
				all_rows = cursor.fetchall()
				usageentries = len(all_rows)
				if usageentries > 0:
					for row in all_rows:    
						data_list4.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
				else:
					logfunc('No data available in Airdop Connection Info')
					
		if version.parse(iOSversion) >= version.parse("9"):
			cursor.execute('''
			SELECT
				DATETIME(TIMESTAMP, 'UNIXEPOCH') AS TIMESTAMP,
				APPNAME AS "APP NAME",
				APPEXECUTABLE AS "APP EXECUTABLE NAME",
				APPBUNDLEID AS "BUNDLE ID",
				APPBUILDVERSION AS "APP BUILD VERSION",
				APPBUNDLEVERSION AS "APP BUNDLE VERSION",
				APPTYPE AS "APP TYPE",
				CASE APPDELETEDDATE 
					WHEN 0 THEN "NOT DELETED" 
					ELSE DATETIME(APPDELETEDDATE, 'UNIXEPOCH') 
				END "APP DELETED DATE",
				ID AS "PLAPPLICATIONAGENT_EVENTNONE_ALLAPPS TABLE ID" 
			FROM
				PLAPPLICATIONAGENT_EVENTNONE_ALLAPPS
			''')
			
			all_rows = cursor.fetchall()
			usageentries = len(all_rows)
			if usageentries > 0:
				for row in all_rows:    
					data_list5.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
			else:
				logfunc('No data available in Powerlog App Info')
				
		if version.parse(iOSversion) >= version.parse("11"):
			cursor.execute('''
			SELECT
				DATETIME(TIMESTAMP, 'UNIXEPOCH') AS TIMESTAMP,
				DATETIME(START, 'UNIXEPOCH') AS "START",
				DATETIME(END, 'UNIXEPOCH') AS "END",
				STATE AS "STATE",
				FINISHED AS "FINISHED",
				HASERROR AS "HAS ERROR",
				ID AS "PLXPCAGENT_EVENTPOINT_MOBILEBACKUPEVENTS TABLE ID" 
			FROM
				PLXPCAGENT_EVENTPOINT_MOBILEBACKUPEVENTS
			''')
			
			all_rows = cursor.fetchall()
			usageentries = len(all_rows)
			if usageentries > 0:
				for row in all_rows:    
					data_list6.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
			else:
				logfunc('No data available in Powerlog Backup Info')
		
		if version.parse(iOSversion) >= version.parse("11"):
			cursor.execute("""
			SELECT
					DATETIME(APPDELETEDDATE, 'UNIXEPOCH') AS "APP DELETED DATE",
					DATETIME(TIMESTAMP, 'UNIXEPOCH') AS TIMESTAMP,
					APPNAME AS "APP NAME",
					APPEXECUTABLE AS "APP EXECUTABLE NAME",
					APPBUNDLEID AS "BUNDLE ID",
					APPBUILDVERSION AS "APP BUILD VERSION",
					APPBUNDLEVERSION AS "APP BUNDLE VERSION",
					APPTYPE AS "APP TYPE",
					ID AS "PLAPPLICATIONAGENT_EVENTNONE_ALLAPPS TABLE ID" 
				FROM
					PLAPPLICATIONAGENT_EVENTNONE_ALLAPPS 
				WHERE
					APPDELETEDDATE > 0

			""")
			all_rows = cursor.fetchall()
			usageentries = len(all_rows)
			if usageentries > 0:
				for row in all_rows:    
					data_list7.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
						
		if version.parse(iOSversion) == version.parse("10"):
			cursor.execute("""
			SELECT
					DATETIME(APPDELETEDDATE, 'UNIXEPOCH') AS "APP DELETED DATE",
					DATETIME(TIMESTAMP, 'UNIXEPOCH') AS TIMESTAMP,
					APPNAME AS "APP NAME",
					APPEXECUTABLE AS "APP EXECUTABLE NAME",
					APPBUNDLEID AS "BUNDLE ID",
					APPBUILDVERSION AS "APP BUILD VERSION",
					APPBUNDLEVERSION AS "APP BUNDLE VERSION",
					--APPTYPE AS "APP TYPE",
					ID AS "PLAPPLICATIONAGENT_EVENTNONE_ALLAPPS TABLE ID" 
				FROM
					PLAPPLICATIONAGENT_EVENTNONE_ALLAPPS 
				WHERE
					APPDELETEDDATE > 0
			""")
			iall_rows = cursor.fetchall()
			usageentries = len(all_rows)
			if usageentries > 0:
				for row in all_rows:    
					data_list7.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
								
		if version.parse(iOSversion) == version.parse("9"):
			cursor.execute("""
			SELECT
					DATETIME(APPDELETEDDATE, 'UNIXEPOCH') AS "APP DELETED DATE",
					DATETIME(TIMESTAMP, 'UNIXEPOCH') AS TIMESTAMP,
					APPNAME AS "APP NAME",
					APPBUNDLEID AS "BUNDLE ID",
					ID AS "PLAPPLICATIONAGENT_EVENTNONE_ALLAPPS TABLE ID" 
				FROM
					PLAPPLICATIONAGENT_EVENTNONE_ALLAPPS 
				WHERE
					APPDELETEDDATE > 0
			""")
			all_rows = cursor.fetchall()
			usageentries = len(all_rows)
			if usageentries > 0:
				for row in all_rows:    
					data_list7.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

		if version.parse(iOSversion) >= version.parse("10"):
			cursor.execute('''
			SELECT
			DATETIME(LIGHTNINGCONNECTOR_TIMESTAMP + SYSTEM, 'UNIXEPOCH','LOCALTIME') AS ADJUSTED_TIMESTAMP,
			CASE IOACCESSORYPOWERMODE 
				WHEN "1" THEN "UNPLUGGED" 
				WHEN "3" THEN "PLUGGED IN" 
			END  AS "IO ACCESSORY POWER MODE",
			DATETIME(LIGHTNINGCONNECTOR_TIMESTAMP, 'UNIXEPOCH') AS ORIGINAL_LIGHTNINGCONNECTOR_TIMESTAMP,
			DATETIME(TIME_OFFSET_TIMESTAMP, 'UNIXEPOCH') AS OFFSET_TIMESTAMP,
			SYSTEM AS TIME_OFFSET,
			LIGHTNINGCONNECTOR_ID AS "PLBATTERYAGENT_EVENTFORWARD_LIGHTNINGCONNECTORSTATUS TABLE ID" 
			FROM
			(
			SELECT
				LIGHTNINGCONNECTOR_ID,
				LIGHTNINGCONNECTOR_TIMESTAMP,
				TIME_OFFSET_TIMESTAMP,
				MAX(TIME_OFFSET_ID) AS MAX_ID,
				IOACCESSORYPOWERMODE,
				SYSTEM
			FROM
				(
				SELECT
					PLBATTERYAGENT_EVENTFORWARD_LIGHTNINGCONNECTORSTATUS.TIMESTAMP AS LIGHTNINGCONNECTOR_TIMESTAMP,
					IOACCESSORYPOWERMODE,
					PLBATTERYAGENT_EVENTFORWARD_LIGHTNINGCONNECTORSTATUS.ID AS "LIGHTNINGCONNECTOR_ID" ,
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM
				FROM
					PLBATTERYAGENT_EVENTFORWARD_LIGHTNINGCONNECTORSTATUS
				LEFT JOIN
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET 
				)
				AS LIGHTNINGCONNECTOR_STATE 
			GROUP BY
				LIGHTNINGCONNECTOR_ID 
			)
			''')
			
			all_rows = cursor.fetchall()
			usageentries = len(all_rows)
			if usageentries > 0:
				for row in all_rows:    
					data_list8.append((row[0],row[1],row[2],row[3],row[4],row[5]))
			else:
				logfunc('No data available in Powerlog Lightning Connector Status')
		
		if version.parse(iOSversion) >= version.parse("9"):
			cursor.execute('''
			SELECT
				DATETIME(LOCATIONAGENT_TIMESTAMP + SYSTEM, 'UNIXEPOCH') AS ADJUSTED_TIMESTAMP,
				DATETIME(TIMESTAMPLOGGED+ SYSTEM, 'UNIXEPOCH') AS "TIMESTAMP LOGGED (ADJ)",
				DATETIME(TIMESTAMPEND + SYSTEM, 'UNIXEPOCH') AS "TIMESTAMP END (ADJ)",
				BUNDLEID AS "BUNDLE ID",
				TYPE AS "TYPE",
				LOCATIONDESIREDACCURACY AS "LOCATION DESIRED ACCURACY",
				LOCATIONDISTANCEFILTER AS "LOCATION DISTANCE FILTER",
				CLIENT AS "CLIENT",
				EXECUTABLE AS "EXECUTABLE",
				DATETIME(TIME_OFFSET_TIMESTAMP, 'UNIXEPOCH') AS OFFSET_TIMESTAMP,
				SYSTEM AS TIME_OFFSET,
				LOCATIONAGENT_ID AS "PLLOCATIONAGENT_EVENTFORWARD_CLIENTSTATUS TABLE ID" 
				FROM
				(
				SELECT
					LOCATIONAGENT_ID,
					LOCATIONAGENT_TIMESTAMP,
					TIME_OFFSET_TIMESTAMP,
					MAX(TIME_OFFSET_ID) AS MAX_ID,
					TIMESTAMPEND,
					TIMESTAMPLOGGED,
					BUNDLEID,
					TYPE,
					LOCATIONDESIREDACCURACY,
					LOCATIONDISTANCEFILTER,
					CLIENT,
					EXECUTABLE,
					SYSTEM
				FROM
					(
					SELECT
						PLLOCATIONAGENT_EVENTFORWARD_CLIENTSTATUS.TIMESTAMP AS LOCATIONAGENT_TIMESTAMP,
						TIMESTAMPEND,
						TIMESTAMPLOGGED,
						BUNDLEID,
						TYPE,
						LOCATIONDESIREDACCURACY,
						LOCATIONDISTANCEFILTER,
						CLIENT,
						EXECUTABLE,
						PLLOCATIONAGENT_EVENTFORWARD_CLIENTSTATUS.ID AS "LOCATIONAGENT_ID" ,
						PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
						PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
						PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM
					FROM
						PLLOCATIONAGENT_EVENTFORWARD_CLIENTSTATUS
					LEFT JOIN
						PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET
					)
					AS LOCATIONAGENT_STATE 
				GROUP BY
					LOCATIONAGENT_ID 
				)        
			''')
			
			
			all_rows = cursor.fetchall()
			usageentries = len(all_rows)
			if usageentries > 0:
				if version.parse(iOSversion) >= version.parse("9"):
					for row in all_rows:    
						data_list9.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]))
			else:
				logfunc('No data available in Location Use by App')

		if version.parse(iOSversion) >= version.parse("10"):
			cursor.execute('''
			SELECT
				DATETIME(TIMESTAMP, 'UNIXEPOCH') AS TIMESTAMP,
				BUILD,
				DEVICE,
				HWMODEL,
				PAIRINGID AS "PAIRING ID",
				ID AS "PLCONFIGAGENT_EVENTNONE_PAIREDDEVICECONFIG TABLE ID" 
			FROM
				PLCONFIGAGENT_EVENTNONE_PAIREDDEVICECONFIG
			''')
		else:
			cursor.execute('''
			SELECT
				DATETIME(TIMESTAMP, 'UNIXEPOCH') AS TIMESTAMP,
				BUILD,
				DEVICE,
				ID AS "PLCONFIGAGENT_EVENTNONE_PAIREDDEVICECONFIG TABLE ID" 
			FROM
				PLCONFIGAGENT_EVENTNONE_PAIREDDEVICECONFIG
			''')
			
		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			if version.parse(iOSversion) >= version.parse("10"):
				for row in all_rows:    
					data_list11.append((row[0],row[1],row[2],row[3],row[4],row[5]))
			else:
				for row in all_rows:    
					data_list11.append((row[0],row[1],row[2],row[3]))

		if version.parse(iOSversion) >= version.parse("9"):
			cursor.execute('''
			SELECT
					DATETIME(TIMESTAMP + SYSTEM, 'UNIXEPOCH') AS ADJUSTED_TIMESTAMP,
					DATETIME(TIMESTAMPEND + SYSTEM, 'UNIXEPOCH') AS ADJUSTED_END_TIMESTAMP,
					BUNDLENAME AS 'BUNDLE ID',
					PROCESSNAME AS 'PROCESS NAME',
					CELLIN AS 'CELL IN',
					CELLOUT AS 'CELL OUT',
					WIFIIN AS 'WIFI IN',
					WIFIOUT AS 'WIFI OUT',
					DATETIME(TIMESTAMP, 'UNIXEPOCH') AS ORIGINAL_TIMESTAMP,
					DATETIME(TIME_OFFSET_TIMESTAMP, 'UNIXEPOCH') AS OFFSET_TIMESTAMP,
					SYSTEM AS TIME_OFFSET,
					TABLE_ID AS "PLPROCESSNETWORKAGENT_EVENTINTERVAL_USAGEDIFF TABLE ID"
				FROM
				(
				SELECT
					TABLE_ID,
					TIMESTAMP,
					TIME_OFFSET_TIMESTAMP,
					MAX(TIME_OFFSET_ID) AS MAX_ID,
					TIMESTAMPEND,
					BUNDLENAME,
					PROCESSNAME,
					CELLIN,
					CELLOUT,
					WIFIIN,
					WIFIOUT,
					SYSTEM
				FROM
				(
				SELECT
					PLPROCESSNETWORKAGENT_EVENTINTERVAL_USAGEDIFF.TIMESTAMP,
					PLPROCESSNETWORKAGENT_EVENTINTERVAL_USAGEDIFF.TIMESTAMPEND,
					PLPROCESSNETWORKAGENT_EVENTINTERVAL_USAGEDIFF.BUNDLENAME,
					PLPROCESSNETWORKAGENT_EVENTINTERVAL_USAGEDIFF.PROCESSNAME,
					PLPROCESSNETWORKAGENT_EVENTINTERVAL_USAGEDIFF.CELLIN,
					PLPROCESSNETWORKAGENT_EVENTINTERVAL_USAGEDIFF.CELLOUT,
					PLPROCESSNETWORKAGENT_EVENTINTERVAL_USAGEDIFF.WIFIIN,
					PLPROCESSNETWORKAGENT_EVENTINTERVAL_USAGEDIFF.WIFIOUT,
					PLPROCESSNETWORKAGENT_EVENTINTERVAL_USAGEDIFF.ID AS "TABLE_ID",
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM
				FROM
					PLPROCESSNETWORKAGENT_EVENTINTERVAL_USAGEDIFF 
				LEFT JOIN
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET 
				)
				GROUP BY
				TABLE_ID 
					 )
			''')
			all_rows = cursor.fetchall()
			usageentries = len(all_rows)
			if usageentries > 0:
				for row in all_rows:    
					data_list12.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]))
					
		if version.parse(iOSversion) >= version.parse("9"):
			cursor.execute('''
			SELECT
				DATETIME(TIMESTAMP + SYSTEM, 'UNIXEPOCH') AS ADJUSTED_TIMESTAMP,
				BUNDLEID AS 'BUNDLE ID',
				CONNECTIONTYPE AS 'CONNECTION TYPE',
				ISDROPPED AS 'IS DROPPED',
				LINKQUALITY AS 'LINK QUALITY',
				PRIORITY AS 'PRIORITY',
				TOPIC AS 'TOPIC',
				SERVERHOSTNAME AS 'SERVERHOSTNAME',
				SERVERIP AS 'SERVER IP',
				DATETIME(TIMESTAMP, 'UNIXEPOCH') AS ORIGINAL_TIMESTAMP,
				DATETIME(TIME_OFFSET_TIMESTAMP, 'UNIXEPOCH') AS OFFSET_TIMESTAMP,
				SYSTEM AS TIME_OFFSET,
				TABLE_ID AS "PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH TABLE ID"
			FROM
			(
			SELECT
				TABLE_ID,
				TIMESTAMP,
				TIME_OFFSET_TIMESTAMP,
				MAX(TIME_OFFSET_ID) AS MAX_ID,
				BUNDLEID,
				CONNECTIONTYPE,
				ISDROPPED,
				LINKQUALITY,
				PRIORITY,
				TOPIC,
				SERVERHOSTNAME,
				SERVERIP,
				SYSTEM
			FROM
			(
			SELECT
				PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH.TIMESTAMP,
				PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH.BUNDLEID,
				PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH.CONNECTIONTYPE,
				PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH.ISDROPPED,
				PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH.LINKQUALITY,
				PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH.PRIORITY,
				PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH.TOPIC,
				PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH.SERVERHOSTNAME,
				PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH.SERVERIP,
				PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH.ID AS "TABLE_ID",
				PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
				PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
				PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM
			FROM
				PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH 
			LEFT JOIN
				PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET 
			)
			GROUP BY
			TABLE_ID 
				)
			''')
			all_rows = cursor.fetchall()
			usageentries = len(all_rows)
			if usageentries > 0:
				for row in all_rows:    
					data_list13.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]))

		if version.parse(iOSversion) >= version.parse("9"):
			cursor.execute('''
			 SELECT
			DATETIME(TIMEZONE_TIMESTAMP + SYSTEM, 'UNIXEPOCH') AS ADJUSTED_TIMESTAMP,
			TIMEZONENAME AS "TIME ZONE NAME",
			COUNTRYCODE AS "COUNTRY CODE",
			LOCALEID AS "LOCALE ID",
			SECONDSFROMGMT / 3600 AS "SECONDS FROM GMT",
			TIMEZONEISINDST AS "TIME ZONE IN DST",
			TRIGGER AS "TRIGGER",
			DATETIME(TIME_OFFSET_TIMESTAMP, 'UNIXEPOCH') AS OFFSET_TIMESTAMP,
			SYSTEM AS TIME_OFFSET,
			TIMEZONE_ID AS "PLLOCALEAGENT_EVENTFORWARD_TIMEZONE TABLE ID" 
			FROM
			(
			SELECT
				TIMEZONE_ID,
				TIMEZONE_TIMESTAMP,
				TIME_OFFSET_TIMESTAMP,
				MAX(TIME_OFFSET_ID) AS MAX_ID,
				TIMEZONENAME,
				COUNTRYCODE,
				LOCALEID,
				SECONDSFROMGMT,
				TIMEZONEISINDST,
				TRIGGER,
				SYSTEM
			FROM
				(
				SELECT
					PLLOCALEAGENT_EVENTFORWARD_TIMEZONE.TIMESTAMP AS TIMEZONE_TIMESTAMP,
					TIMEZONENAME,
					COUNTRYCODE,
					LOCALEID,
					SECONDSFROMGMT,
					TIMEZONEISINDST,
					TRIGGER,
					PLLOCALEAGENT_EVENTFORWARD_TIMEZONE.ID AS "TIMEZONE_ID" ,
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM
				FROM
					PLLOCALEAGENT_EVENTFORWARD_TIMEZONE
				LEFT JOIN
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET
				)
				AS TIMEZONE_STATE 
			GROUP BY
				TIMEZONE_ID 
			)
			''')
			all_rows = cursor.fetchall()
			usageentries = len(all_rows)
			if usageentries > 0:
				for row in all_rows:    
					data_list14.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9]))
					
		if version.parse(iOSversion) >= version.parse("9"):
			cursor.execute('''
			SELECT
				DATETIME(TORCH_TIMESTAMP + SYSTEM, 'UNIXEPOCH') AS ADJUSTED_TIMESTAMP,
				BUNDLEID AS BUNDLE_ID,
				CASE LEVEL
				WHEN "0" THEN "OFF"
				WHEN "1" THEN "ON"
				END AS STATUS,
				DATETIME(TORCH_TIMESTAMP, 'UNIXEPOCH') AS ORIGINAL_TORCH_TIMESTAMP,
				DATETIME(TIME_OFFSET_TIMESTAMP, 'UNIXEPOCH') AS OFFSET_TIMESTAMP,
				SYSTEM AS TIME_OFFSET,
			TORCH_ID
			FROM
				(
				SELECT
					BUNDLEID,
					TORCH_ID,
					TORCH_TIMESTAMP,
					TIME_OFFSET_TIMESTAMP,
					MAX(TIME_OFFSET_ID) AS MAX_ID,
					SYSTEM,
					LEVEL
				FROM
						(
						SELECT
							PLCAMERAAGENT_EVENTFORWARD_TORCH.TIMESTAMP AS TORCH_TIMESTAMP,
							PLCAMERAAGENT_EVENTFORWARD_TORCH.BUNDLEID,
							PLCAMERAAGENT_EVENTFORWARD_TORCH.LEVEL,
							PLCAMERAAGENT_EVENTFORWARD_TORCH.ID AS "TORCH_ID",
							PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
							PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
							PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM,
							BUNDLEID 
						FROM
							PLCAMERAAGENT_EVENTFORWARD_TORCH 
						LEFT JOIN
							PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET 
						) 
						AS TORCHESTATE 
				GROUP BY
					TORCH_ID 
				)
			''')
			all_rows = cursor.fetchall()
			usageentries = len(all_rows)
			if usageentries > 0:
				for row in all_rows:    
					data_list15.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
					
		if version.parse(iOSversion) >= version.parse("9"):
			cursor.execute('''
			SELECT
			DATETIME(VIDEO_TIMESTAMP + SYSTEM, 'UNIXEPOCH') AS ADJUSTED_TIMESTAMP,
			CLIENTDISPLAYID AS "CLIENT DISPLAY ID",
			STATE,
			CLIENTPID AS "CLIENT PID",
			DATETIME(TIME_OFFSET_TIMESTAMP, 'UNIXEPOCH') AS OFFSET_TIMESTAMP,
			SYSTEM AS TIME_OFFSET,
			VIDEO_ID AS "PLVIDEOAGENT_EVENTFORWARD_VIDEO TABLE ID" 
			FROM
			(
			SELECT
				VIDEO_ID,
				VIDEO_TIMESTAMP,
				TIME_OFFSET_TIMESTAMP,
				MAX(TIME_OFFSET_ID) AS MAX_ID,
				CLIENTDISPLAYID,
				STATE,
				CLIENTPID,
				SYSTEM
			FROM
				(
				SELECT
					PLVIDEOAGENT_EVENTFORWARD_VIDEO.TIMESTAMP AS VIDEO_TIMESTAMP,
					CLIENTDISPLAYID,
					STATE,
					CLIENTPID,
					PLVIDEOAGENT_EVENTFORWARD_VIDEO.ID AS "VIDEO_ID" ,
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM
				FROM
					PLVIDEOAGENT_EVENTFORWARD_VIDEO
				LEFT JOIN
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET
				)
				AS VIDEO_STATE 
			GROUP BY
				VIDEO_ID 
			)
			''')
			all_rows = cursor.fetchall()
			usageentries = len(all_rows)
			if usageentries > 0:
				for row in all_rows:    
					data_list16.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
					
		if version.parse(iOSversion) >= version.parse("9"):
			cursor.execute('''
			SELECT
			DATETIME(VOLUME_TIMESTAMP + SYSTEM, 'UNIXEPOCH') AS ADJUSTED_TIMESTAMP,
			VOLUME AS "VOLUME PERCENTAGE",
			CASE MUTED 
				WHEN "0" THEN "NO" 
				WHEN "1" THEN "YES" 
			END AS "MUTED",
			DATETIME(VOLUME_TIMESTAMP, 'UNIXEPOCH') AS ORIGINAL_VOLUME_TIMESTAMP,
			DATETIME(TIME_OFFSET_TIMESTAMP, 'UNIXEPOCH') AS OFFSET_TIMESTAMP,
			SYSTEM AS TIME_OFFSET,
			VOLUME_ID AS "PLAUDIOAGENT_EVENTFORWARD_OUTPUT TABLE ID" 
			FROM
			(
			SELECT
				VOLUME_ID,
				VOLUME_TIMESTAMP,
				TIME_OFFSET_TIMESTAMP,
				MAX(TIME_OFFSET_ID) AS MAX_ID,
				VOLUME,
				MUTED,
				SYSTEM
			FROM
				(
				SELECT
					PLAUDIOAGENT_EVENTFORWARD_OUTPUT.TIMESTAMP AS VOLUME_TIMESTAMP,
					VOLUME,
					MUTED,
					PLAUDIOAGENT_EVENTFORWARD_OUTPUT.ID AS "VOLUME_ID" ,
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM
				FROM
					PLAUDIOAGENT_EVENTFORWARD_OUTPUT
				LEFT JOIN
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET
				)
				AS VOLUME_STATE 
			GROUP BY
				VOLUME_ID 
			)
			''')
			all_rows = cursor.fetchall()
			usageentries = len(all_rows)
			if usageentries > 0:
				for row in all_rows:    
					data_list17.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
					
		if version.parse(iOSversion) >= version.parse("9"):
			cursor.execute('''
			SELECT
			DATETIME(WIFIPROPERTIES_TIMESTAMP + SYSTEM, 'UNIXEPOCH') AS ADJUSTED_TIMESTAMP,
			CURRENTSSID,
			CURRENTCHANNEL,
			DATETIME(TIME_OFFSET_TIMESTAMP, 'UNIXEPOCH') AS OFFSET_TIMESTAMP,
			SYSTEM AS TIME_OFFSET,
			WIFIPROPERTIES_ID AS "PLWIFIAGENT_EVENTBACKWARD_CUMULATIVEPROPERTIES TABLE ID" 
			FROM
			(
			SELECT
				WIFIPROPERTIES_ID,
				WIFIPROPERTIES_TIMESTAMP,
				TIME_OFFSET_TIMESTAMP,
				MAX(TIME_OFFSET_ID) AS MAX_ID,
				CURRENTSSID,
				CURRENTCHANNEL,
				SYSTEM
			FROM
				(
				SELECT
					PLWIFIAGENT_EVENTBACKWARD_CUMULATIVEPROPERTIES.TIMESTAMP AS WIFIPROPERTIES_TIMESTAMP,
					CURRENTSSID,
					CURRENTCHANNEL,
					PLWIFIAGENT_EVENTBACKWARD_CUMULATIVEPROPERTIES.ID AS "WIFIPROPERTIES_ID" ,
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM
				FROM
					PLWIFIAGENT_EVENTBACKWARD_CUMULATIVEPROPERTIES
				LEFT JOIN
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET 
				)
				AS WIFIPROPERTIES_STATE 
			GROUP BY
				WIFIPROPERTIES_ID 
			)    
			''')
			all_rows = cursor.fetchall()
			usageentries = len(all_rows)
			if usageentries > 0:
				for row in all_rows:    
					data_list18.append((row[0],row[1],row[2],row[3],row[4],row[5]))

	
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
			data_headers2 = ('Timestamp','Bulletin Bundle ID','Time Interval in Seconds','Count','Post Type','Aggregate Table ID')   
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
			data_headers3 = ('Timestamp','Notification Bundle ID','Time Interval in Seconds','Count','Notification Type','Aggregate Table ID')   
			report.write_artifact_data_table(data_headers3, data_list3, file_found)
			report.end_artifact_report()
			
			tsvname = 'Powerlog Agg Notifications from GZ backup'
			tsv(report_folder, data_headers3, data_list3, tsvname)
			
			tlactivity = 'Powerlog Agg Notifications from GZ backup'
			timeline(report_folder, tlactivity, data_list3, data_headers3)

	if version.parse(iOSversion) >= version.parse("9"):
		if len(data_list4) > 0:
			report = ArtifactHtmlReport('Powerlog Airdrop Connections Info')
			report.start_artifact_report(report_folder, 'Airdrop Connections Info')
			report.add_script()
			data_headers4 = ('Adjusted Timestamp','State','Subevent','Bundle ID','PID','Original Airdrop Timestamp','Offset Timestamp','Time Offset', 'Airdrop Table ID' )   
			report.write_artifact_data_table(data_headers4, data_list4, file_found)
			report.end_artifact_report()

			tsvname = 'Powerlog Airdrop Connections Info from GZ backup'
			tsv(report_folder, data_headers4, data_list4, tsvname)

			tlactivity = 'Powerlog Airdrop Connections Info from GZ backup'
			timeline(report_folder, tlactivity, data_list4, data_headers4)

	if version.parse(iOSversion) >= version.parse("9"):
		if len(data_list5) > 0:
			report = ArtifactHtmlReport('Powerlog App Info')
			report.start_artifact_report(report_folder, 'App Info')
			report.add_script()
			data_headers5 = ('Timestamp','App Name','App Executable Name','Bundle ID','App Build Version','App Bundle Version','App TYpe','App Deleted Date','Table ID' )   
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
			data_headers6 = ('Timestamp','Start','End','State','Finished','Has error','Table ID' )   
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
			data_headers7 = ('App Deleted Date','Timestamp','App Name','App Executable Name','Bundle ID','App Build Version','App Bundle Version','App Type','Table ID')  
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
			data_headers7 = ('App Deleted Date','Timestamp','App Name','App Executable Name','Bundle ID','App Build Version','App Bundle Version','App Type','Table ID')             
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
			data_headers7 = ('App Deleted Date','Timestamp','App Name','Bundle ID','Table ID') 
			report.write_artifact_data_table(data_headers7, data_list7, file_found)
			report.end_artifact_report()
			
			tsvname = 'Powerlog Deleted Apps from GZ backup'
			tsv(report_folder, data_headers7, data_list7, tsvname)
			
			tlactivity = 'Powerlog Deleted Apps from GZ backup'
			timeline(report_folder, tlactivity, data_list7, data_headers7)

	if version.parse(iOSversion) >= version.parse("10"):
		if len(data_list8) > 0:
			report = ArtifactHtmlReport('Powerlog Lightning Connector Status')
			report.start_artifact_report(report_folder, 'Lightning Connector Status')
			report.add_script()
			data_headers8 = ('Adjusted Timestamp','Accesory Power Mode','Original Lightnint Connector Timestamp','Offset Timestamp','Table ID', 'System' )   
			report.write_artifact_data_table(data_headers8, data_list8, file_found)
			report.end_artifact_report()

			tsvname = 'Powerlog Lightning Connector Status from GZ backup'
			tsv(report_folder, data_headers8, data_list8, tsvname)

			tlactivity = 'Powerlog Lightning Connector Status from GZ backup'
			timeline(report_folder, tlactivity, data_list8, data_headers8)
			
	if version.parse(iOSversion) >= version.parse("9"):
		if len(data_list9) > 0:
			report = ArtifactHtmlReport('Powerlog Location Use by App')
			report.start_artifact_report(report_folder, 'Location Use by App')
			report.add_script()
			data_headers9 = ('Adjusted Timestamp','Timestamp Logged','Timestamp End','Bundle ID','Type','Location Desired Accuracy','Location Distance Filter','Client','Executable','Offset Timestamp','Time Offset', 'Client Status Table ID' )   
			report.write_artifact_data_table(data_headers9, data_list9, file_found)
			report.end_artifact_report()
			
			tsvname = 'Powerlog Location Use by App from GZ backup'
			tsv(report_folder, data_headers9, data_list9, tsvname)
			
			tlactivity = 'Powerlog Location Use by App from GZ backup'
			timeline(report_folder, tlactivity, data_list9, data_headers9)
	
	if version.parse(iOSversion) >= version.parse("10"):
		if len(data_list11) > 0:
			report = ArtifactHtmlReport('Powerlog Paired Device Configuration')
			report.start_artifact_report(report_folder, 'Paired Device Configuration')
			report.add_script()
			data_headers11 = ('Timestamp','Build','Device','HW Model','Pairing ID','PairedDeviceConfig Table ID' )   
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
			data_headers11 = ('Timestamp','Build','Device','PairedDeviceConfig Table ID' )  
			report.write_artifact_data_table(data_headers11, data_list11, file_found)
			report.end_artifact_report()
			
			tsvname = 'Powerlog Paired Device Conf from GZ backup'
			tsv(report_folder, data_headers11, data_list11, tsvname)
			
			tlactivity = 'Powerlog Paired Device Configuration from GZ backup'
			timeline(report_folder, tlactivity, data_list11, data_headers11)
			
	if version.parse(iOSversion) >= version.parse("9"):
		if len(data_list12) > 0:
			report = ArtifactHtmlReport('Powerlog Process Data Usage')
			report.start_artifact_report(report_folder, 'Process Data Usage')
			report.add_script()
			data_headers12 = ('Adjusted Timestamp','Adjusted End Timestamp','Bundle ID','Process Name','Cell In','Cell Out','WiFI In','WiFi Out','Original Timestamp','Offset Timestamp','Time Offset','Usage Diff Table ID')   
			report.write_artifact_data_table(data_headers12, data_list12, file_found)
			report.end_artifact_report()
			
			tsvname = 'Powerlog Process Data Usage from GZ backup'
			tsv(report_folder, data_headers12, data_list12, tsvname)
			
			tlactivity = 'Powerlog Process Data Usage from GZ backup'
			timeline(report_folder, tlactivity, data_list12, data_headers12)
			
	if version.parse(iOSversion) >= version.parse("9"):
		if len(data_list13) > 0:		
			report = ArtifactHtmlReport('Powerlog Push Message Received')
			report.start_artifact_report(report_folder, 'Push Message Received')
			report.add_script()
			data_headers13 = ('Adjusted Timestamp','Bundle ID','Connection Type','Is Dropped','Link Quality','Priority','Topic','Server Hostname','Server IP','Original Timestamp','Offset Timestamp','Time Offset','Aggregate Table ID')   
			report.write_artifact_data_table(data_headers13, data_list13, file_found)
			report.end_artifact_report()
			
			tsvname = 'Powerlog Push Message Received from GZ backup'
			tsv(report_folder, data_headers13, data_list13, tsvname)
			
			tlactivity = 'Powerlog Push Message Received from GZ backup'
			timeline(report_folder, tlactivity, data_list13, data_headers13)

	if version.parse(iOSversion) >= version.parse("9"):
		if len(data_list14) > 0:
			report = ArtifactHtmlReport('Powerlog Timezones')
			report.start_artifact_report(report_folder, 'Timezones')
			report.add_script()
			data_headers14 = ('Adjusted Timestamp','Timezone Name','Country Code','Locale ID','Seconds from GMT','Timezone in DTS','Trigger','Offset Timestamp','Time Offset','Timezon Table ID')   
			report.write_artifact_data_table(data_headers14, data_list14, file_found)
			report.end_artifact_report()
			
			tsvname = 'Powerlog Timezones from GZ backup'
			tsv(report_folder, data_headers14, data_list14, tsvname)
			
			tlactivity = 'Powerlog Timezones from GZ backup'
			timeline(report_folder, tlactivity, data_list14, data_headers14)
			
	if version.parse(iOSversion) >= version.parse("9"):
		if len(data_list15) > 0:
			report = ArtifactHtmlReport('Powerlog Torch')
			report.start_artifact_report(report_folder, 'Torch')
			report.add_script()
			data_headers15 = ('Adjusted Timestamp','Bundle ID','Status','Original Torch Timestamp','Offset Timestamp','Time Offset','Torch ID')   
			report.write_artifact_data_table(data_headers15, data_list15, file_found)
			report.end_artifact_report()
			
			tsvname = 'Powerlog Torch from GZ backup'
			tsv(report_folder, data_headers15, data_list15, tsvname)
			
			tlactivity = 'Powerlog Torch from GZ backup'
			timeline(report_folder, tlactivity, data_list15, data_headers15)
			
	if version.parse(iOSversion) >= version.parse("9"):
		if len(data_list16) > 0:
			report = ArtifactHtmlReport('Powerlog App Playing Video')
			report.start_artifact_report(report_folder, 'App Playing Video')
			report.add_script()
			data_headers16 = ('Adjusted Timestamp','Client Display ID','State','Client PID','Offset Timestamp','Time Offset','Event Forward Video Table ID')   
			report.write_artifact_data_table(data_headers16, data_list16, file_found)
			report.end_artifact_report()
			
			tsvname = 'Powerlog App Playing Video from GZ backup'
			tsv(report_folder, data_headers16, data_list16, tsvname)
			
			tlactivity = 'Powerlog App Playing Video from GZ backup'
			timeline(report_folder, tlactivity, data_list16, data_headers16)
						
	if version.parse(iOSversion) >= version.parse("9"):	
		if len(data_list17) > 0:		
			report = ArtifactHtmlReport('Powerlog Volume Percentage')
			report.start_artifact_report(report_folder, 'Volume Percentage')
			report.add_script()
			data_headers17 = ('Adjusted Timestamp','Volume Percentage','Muted','Original Volume Timestamp','Offset Timestamp','Time Offset','Event Forward Output Table ID')   
			report.write_artifact_data_table(data_headers17, data_list17, file_found)
			report.end_artifact_report()
			
			tsvname = 'Powerlog Volume Percentage from GZ backup'
			tsv(report_folder, data_headers17, data_list17, tsvname)
			
			tlactivity = 'Powerlog Volumen Percentage from GZ backup'
			timeline(report_folder, tlactivity, data_list17, data_headers17)
			
	if version.parse(iOSversion) >= version.parse("9"):
		if len(data_list18) > 0:
			report = ArtifactHtmlReport('Powerlog WiFi Network Connections')
			report.start_artifact_report(report_folder, 'WiFi Network Connections')
			report.add_script()
			data_headers18 = ('Adjusted Timestamp','Current SSID','Current Channel','Offset Timestamp','Time Offset','Cummilative Prop. Table ID')   
			report.write_artifact_data_table(data_headers18, data_list18, file_found)
			report.end_artifact_report()
			
			tsvname = 'Powerlog Wifi Network Connections from GZ backup'
			tsv(report_folder, data_headers18, data_list18, tsvname)
			
			tlactivity = 'Powerlog Wifi Network Connections from GZ backup'
			timeline(report_folder, tlactivity, data_list18, data_headers18)