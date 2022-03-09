# Get Viber settings, contacts, recent calls and messages information
# Author : Evangelos Dragonas (@theAtropos4n6)
# website : atropos4n6.com
# Date : 2022-03-09
# Version : 0.0.1
# 
# The script queries Settings.data and Contacts.data Viber dbs and creates a report of findings including KML geolcation data
# Settings hold the user's personal data and configurations
# Contacts hold contacts, calls, messages and more..
# 
# The code is divided in 3 queries-artifacts blocks. 
# 
# The 1st parses settings db, extracts and reports on user's available information regarding Viber configuartion
#
# The 2nd parses contacts db, extracts and reports on user's contacts. 
# Be advised that a contact may not participate in a chat (therefore a contact is not a chat 'member') and vice versa. A chat 'member' may not be registered as a Viber contact. 
# Hope it makes sense.
#
# The 3rd parses contacts db, extracts and reports on user's chats. 2 extra columns with each chat's grouped participants and phone numbers is also available. 
#
# Also, be aware that there is more information stored within the above databases. This artifact assist in parsing the most out of it (but not all).
#
# Should you face a bug or want a specific field extracted, DM me.


import glob
import os
import pathlib
import sqlite3
import json

import scripts.artifacts.artGlobals
from packaging import version
from html import escape
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, kmlgen, tsv, is_platform_windows, open_sqlite_db_readonly, media_to_html


def get_viber(files_found, report_folder, seeker):
	viber_settings = {}
	for file_found in files_found:
		file_found = str(file_found)

		iOSversion = scripts.artifacts.artGlobals.versionf
		if version.parse(iOSversion) < version.parse("14"):
			logfunc("Viber parsing has not be tested on this iOS " + iOSversion + " version. Please contact @theAtropos4n6 for resolving this issue.")

		if version.parse(iOSversion) >= version.parse("14"):
			if file_found.endswith('Settings.data'):
				db = open_sqlite_db_readonly(file_found)
				cursor = db.cursor()
				cursor.execute('''
					SELECT
						Data.key,value
					FROM Data
					WHERE Data.key IN 
						(
						'_myUserName',
						'_currentEmail',
						'_myPhoneNumber',
						'_myCanonizedPhoneNumber',
						'_myFormattedPhoneNumber',
						'_myCountryPhoneCode',
						'_myCountryCode',
						'_myLanguageCode',
						'_wasabiLastKnownUserLocation',
						'_uid',
						'_appVersion',
						'_savedDeviceId',
						'_attemptsToDownloadBackupForRestore',
						'_backupAttemptsCount',
						'_hiddenChatsPINData'
						)
					UNION
					SELECT
						Data.key,
						CASE 
						WHEN value LIKE '-%' THEN value
						ELSE datetime(value,'unixepoch')
						END
					FROM Data
					WHERE Data.key IN 
						('_registrationDate',
						'_autoBackupLastRunTime',
						'_lastBackupStartDate')
					UNION
					SELECT
						Data.key,
						datetime(value,'unixepoch') -- this value is stored in the user localtime
					FROM Data
					WHERE Data.key IS '_birthdate'
					ORDER BY value
				''')
				all_rows = cursor.fetchall()
				usageentries = len(all_rows)
				if usageentries > 0:
					data_list =[]
					for row in all_rows:
						viber_settings[row[0]] = row[1]
						temp_list = list(row)
						if temp_list[0] == '_appVersion':
							temp_list[0] = 'Application Version'
						elif temp_list[0] == '_myUserName':
							temp_list[0] = 'User Name'
						elif temp_list[0] == '_currentEmail':
							temp_list[0] = 'Current Email'
						elif temp_list[0] == '_birthdate':
							temp_list[0] = "Birth Date - UTC (apply user's localtime offset)"
						elif temp_list[0] == '_registrationDate':
							temp_list[0] = 'Registration Date - UTC'
						elif temp_list[0] == '_uid':
							temp_list[0] = 'User ID'
						elif temp_list[0] == '_myPhoneNumber':
							temp_list[0] = 'Phone Number'
						elif temp_list[0] == '_myCanonizedPhoneNumber':
							temp_list[0] = 'Canonized Phone Number'
						elif temp_list[0] == '_myFormattedPhoneNumber':
							temp_list[0] = 'Formatted Phone Number'
						elif temp_list[0] == '_myCountryPhoneCode':
							temp_list[0] = 'Country Phone Code'
						elif temp_list[0] == '_myCountryCode':
							temp_list[0] = 'Country Code'
						elif temp_list[0] == '_myLanguageCode':
							temp_list[0] = 'Language Code'
						elif temp_list[0] == '_wasabiLastKnownUserLocation':
							temp_list[0] = 'Last Known User Location'
						elif temp_list[0] == '_savedDeviceId':
							temp_list[0] = 'Device ID'
						elif temp_list[0] == '_attemptsToDownloadBackupForRestore':
							temp_list[0] = 'Attempts To Download Backup For Restore'
							try:
								int.from_bytes(temp_list[1], byteorder='big') #needs further validation about the byteorder
							except Exception as err:
								logfunc(f'Viber - Settings "_attemptsToDownloadBackupForRestore" could not be extracted. The error was: {err}' )
						elif temp_list[0] == '_backupAttemptsCount':
							temp_list[0] = 'Backup Attempts Count'
							try:
								int.from_bytes(temp_list[1], byteorder='big') #needs further validation about the byteorder
							except Exception as err:
								logfunc(f'Viber - Settings "_backupAttemptsCount" could not be extracted. The error was: {err}' )
						elif temp_list[0] == '_autoBackupLastRunTime':
							temp_list[0] = 'Auto Backup Last Run Time - UTC'
							x = str(temp_list[1])
							if x.startswith("-"):
								temp_list[1] = 'Not Applied'
						elif temp_list[0] == '_lastBackupStartDate':
							x = str(temp_list[1])
							if x.startswith("-"):
								temp_list[1] = 'Not Applied'
						elif temp_list[0] == '_hiddenChatsPINData':
							temp_list[0] = 'Hidden Chats PIN Data'
						row = tuple(temp_list)
						data_list.append((row[0], row[1]))
						

				if usageentries > 0:
					report = ArtifactHtmlReport('Viber - Settings')
					report.start_artifact_report(report_folder, 'Viber - Settings')
					report.add_script()
					data_headers = ('Setting','Value')
					report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
					report.end_artifact_report()

					tsvname = 'Viber - Settings'
					tsv(report_folder, data_headers, data_list, tsvname)
		
				db.close()

			elif file_found.endswith('Contacts.data'):

				db = open_sqlite_db_readonly(file_found)
				cursor = db.cursor()

				cursor.execute('''
					SELECT
						ZABCONTACT.ZMAINNAME AS 'Main Name',
						ZABCONTACT.ZPREFIXNAME AS 'Prefix Name',
						ZABCONTACT.ZSUFFIXNAME AS 'Suffix Name',
						ZABCONTACTNUMBER.ZPHONE AS 'Phone Number',
						ZABCONTACTNUMBER.ZCANONIZEDPHONENUM AS 'Canonized Phone Number',
						ZABCONTACT.ZCONTACTID AS 'Contact ID'
						FROM ZABCONTACT
						LEFT JOIN ZABCONTACTNUMBER ON ZABCONTACT.Z_PK = ZABCONTACTNUMBER.ZCONTACT
						UNION
						SELECT
						ZABCONTACT.ZMAINNAME AS 'Main Name',
						ZABCONTACT.ZPREFIXNAME AS 'Prefix Name',
						ZABCONTACT.ZSUFFIXNAME AS 'Suffix Name',
						ZABCONTACTNUMBER.ZPHONE AS 'Phone Number',
						ZABCONTACTNUMBER.ZCANONIZEDPHONENUM AS 'Canonized Phone Number',
						ZABCONTACT.ZCONTACTID AS 'Contact ID'
					FROM ZABCONTACTNUMBER
					LEFT JOIN ZABCONTACT ON ZABCONTACT.Z_PK = ZABCONTACTNUMBER.ZCONTACT
					ORDER BY ZMAINNAME
				''')
				all_rows = cursor.fetchall()
				usageentries = len(all_rows)
				if usageentries > 0:
					data_list =[]
					for row in all_rows: 
						data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))
						

				if usageentries > 0:
					report = ArtifactHtmlReport('Viber - Contacts')
					report.start_artifact_report(report_folder, 'Viber - Contacts')
					report.add_script()
					data_headers = ('Main Name','Prefix Name','Suffix Name','Phone Number','Canonized Phone Number','Contact ID')
					report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
					report.end_artifact_report()


					tsvname = 'Viber - Contacts'
					tsv(report_folder, data_headers, data_list, tsvname)
					

				cursor.execute('''
					SELECT 	
							CHAT_MEMBER.ZDISPLAYFULLNAME AS 'Sender (Display Full Name)',
							CHAT_MEMBER.ZDISPLAYSHORTNAME AS 'Sender (Display Short Name)',
							CHAT_MEMBER.ZPHONE AS 'Sender (Phone)',
							CHATS.Chat_Name AS 'Chat Name',
							CHATS.CHAT_MEMBERS AS 'Chat Participant(s)',
							CHATS.CHAT_PHONES 'Chat Phone(s)',
							datetime(ZVIBERMESSAGE.ZSTATEDATE+ 978307200,'unixepoch') AS 'Message Creation Date - UTC',
							datetime(ZVIBERMESSAGE.ZDATE+ 978307200,'unixepoch') AS 'Message Change State Date - UTC',
							datetime(RECENT.ZRECENTDATE+ 978307200,'unixepoch') AS 'Call Date - UTC',
							CASE
								WHEN ZCALLTYPE = 'missed' THEN 'Missed Audio Call'
								WHEN ZCALLTYPE = 'missed_with_video' THEN 'Missed Video Call'
								WHEN ZCALLTYPE = 'outgoing_viber' THEN 'Outgoing Audio Call'
								WHEN ZCALLTYPE = 'outgoing_viber_with_video' THEN 'Outgoing Video Call'
								WHEN ZCALLTYPE = 'incoming_with_video' THEN 'Incoming Video Call'
								WHEN ZCALLTYPE = 'incoming' THEN 'Incoming Audio Call'
								ELSE ZCALLTYPE
							end  AS 'Call Type',
							CASE
								WHEN ZVIBERMESSAGE.ZSTATE IN ('send','delivered') THEN 'Outgoing'
								WHEN ZVIBERMESSAGE.ZSTATE = 'received' THEN 'Incoming'
								ELSE ZVIBERMESSAGE.ZSTATE
							END AS 'State',
							RECENT.ZDURATION AS 'Duration',
							ZVIBERMESSAGE.ZSYSTEMTYPE 'System Type Description',
							ZVIBERMESSAGE.ZMETADATA AS 'Message Metadata',
							ZVIBERMESSAGE.ZTEXT AS 'Message Content',
							ZATTACHMENT.ZNAME AS 'Attachment Name',
							ZATTACHMENT.ZTYPE AS 'Attachment Type',
							ZATTACHMENT.ZFILESIZE AS 'Attachment Size',
							ZVIBERLOCATION.ZLATITUDE AS 'Latitude',
							ZVIBERLOCATION.ZLONGITUDE AS 'Longitude',
							CASE
								WHEN CHATS.Chat_Deleted = 1 THEN 'True'
								WHEN CHATS.Chat_Deleted = 0 THEN 'False'
								ELSE CHATS.Chat_Deleted
							END AS 'Conversation Deleted',
							CASE
								WHEN ZVIBERMESSAGE.ZBEINGDELETED = 1 THEN 'True'
								WHEN ZVIBERMESSAGE.ZBEINGDELETED = 0 THEN 'False'
								ELSE ZVIBERMESSAGE.ZBEINGDELETED
							END AS 'Message Deleted',
							ZVIBERMESSAGE.ZTIMEBOMBDURATION AS 'Time Bomb Duration',
							ZVIBERMESSAGE.ZTIMEBOMBTIMESTAMP AS 'Time Bomb Timestamp',
							CASE 
								WHEN CHATS.Chat_Favorite= 1 THEN 'True'
								WHEN CHATS.Chat_Favorite = 0 THEN 'False'
								ELSE CHATS.Chat_Favorite
							END AS 'Conversation Marked Favorite',
							ZVIBERMESSAGE.ZLIKESCOUNT AS 'Likes Count'
					FROM
						ZVIBERMESSAGE
					LEFT JOIN
							(SELECT
								ZVIBERMESSAGE.ZCONVERSATION,
								ZCONVERSATION.ZNAME AS 'Chat_Name',
								ZCONVERSATION.ZBEINGDELETED AS 'Chat_Deleted',
								ZCONVERSATION.ZFAVORITE AS 'Chat_Favorite',
								coalesce(ZVIBERMESSAGE.ZPHONENUMINDEX,ZCONVERSATION.ZINTERLOCUTOR) AS 'MEMBER_ID',
								MEMBER.ZDISPLAYFULLNAME,
								MEMBER.ZDISPLAYSHORTNAME,
								MEMBER.ZNAME AS 'Participant_Name',
								MEMBER.ZCANONIZEDPHONENUM,
								MEMBER.ZPHONE,
								group_concat(DISTINCT(MEMBER.ZDISPLAYFULLNAME)) AS 'CHAT_MEMBERS',
								group_concat(DISTINCT(MEMBER.ZPHONE)) AS 'CHAT_PHONES',
								group_concat(DISTINCT(MEMBER.ZCANONIZEDPHONENUM)) AS 'CHAT_CANONIZED_PHONES'
							FROM ZVIBERMESSAGE,ZCONVERSATION
								LEFT JOIN
										(SELECT 
													ZMEMBER.ZDISPLAYFULLNAME,
													ZMEMBER.ZDISPLAYSHORTNAME,
													ZMEMBER.ZNAME,
													ZPHONENUMBER.ZCANONIZEDPHONENUM,
													ZPHONENUMBER.ZPHONE,
													ZMEMBER.Z_PK
											FROM ZMEMBER
											LEFT JOIN ZPHONENUMBER ON ZMEMBER.Z_PK = ZPHONENUMBER.ZMEMBER
											UNION
											SELECT 
													ZMEMBER.ZDISPLAYFULLNAME,
													ZMEMBER.ZDISPLAYSHORTNAME,
													ZMEMBER.ZNAME,
													ZPHONENUMBER.ZCANONIZEDPHONENUM,
													ZPHONENUMBER.ZPHONE,
													ZMEMBER.Z_PK
											FROM ZPHONENUMBER
											LEFT JOIN ZMEMBER ON ZPHONENUMBER.ZMEMBER  = ZMEMBER.Z_PK
										) AS MEMBER ON MEMBER.Z_PK = MEMBER_ID
								LEFT JOIN ZPHONENUMBER ON MEMBER_ID = ZPHONENUMBER.ZMEMBER
							WHERE ZVIBERMESSAGE.ZCONVERSATION = ZCONVERSATION.Z_PK
							GROUP BY ZVIBERMESSAGE.ZCONVERSATION
					) CHATS ON ZVIBERMESSAGE.ZCONVERSATION = CHATS.ZCONVERSATION

					LEFT JOIN
							(SELECT 
										ZMEMBER.ZDISPLAYFULLNAME,
										ZMEMBER.ZDISPLAYSHORTNAME,
										ZMEMBER.ZNAME,
										ZPHONENUMBER.ZCANONIZEDPHONENUM,
										ZPHONENUMBER.ZPHONE,
										ZMEMBER.Z_PK
								FROM ZMEMBER
								LEFT JOIN ZPHONENUMBER ON ZMEMBER.Z_PK = ZPHONENUMBER.ZMEMBER
								UNION
								SELECT 
										ZMEMBER.ZDISPLAYFULLNAME,
										ZMEMBER.ZDISPLAYSHORTNAME,
										ZMEMBER.ZNAME,
										ZPHONENUMBER.ZCANONIZEDPHONENUM,
										ZPHONENUMBER.ZPHONE,
										ZMEMBER.Z_PK
								FROM ZPHONENUMBER
								LEFT JOIN ZMEMBER ON ZPHONENUMBER.ZMEMBER  = ZMEMBER.Z_PK
							) AS CHAT_MEMBER ON ZVIBERMESSAGE.ZPHONENUMINDEX = CHAT_MEMBER.Z_PK
					LEFT JOIN
							(SELECT
												ZRECENT.ZDURATION,
												ZRECENT.ZCALLLOGMESSAGE,
												ZRECENT.ZDATE AS 'ZRECENTDATE',
												ZRECENTSLINE.ZDATE AS 'ZRECENTSLINEDATE',
												ZRECENT.ZCALLTYPE AS 'CALL TYPE',
												ZRECENTSLINE.ZCALLTYPE AS 'CALL TYPE',
												ZRECENTSLINE.ZPHONENUMBER AS 'PHONE NUMBER'
										FROM ZRECENT
										LEFT JOIN ZRECENTSLINE ON ZRECENT.ZRECENTSLINE = ZRECENTSLINE.Z_PK
							) AS RECENT ON ZVIBERMESSAGE.Z_PK = RECENT.ZCALLLOGMESSAGE 
					LEFT JOIN ZVIBERLOCATION ON ZVIBERMESSAGE.ZLOCATION = ZVIBERLOCATION.Z_PK
					LEFT JOIN ZATTACHMENT ON ZVIBERMESSAGE.ZATTACHMENT = ZATTACHMENT.Z_PK

					ORDER BY ZVIBERMESSAGE.Z_PK
								''')
					
				all_rows = cursor.fetchall()
				usageentries = len(all_rows)
				if usageentries > 0:
					data_list =[]
					for row in all_rows:
						temp_list = list(row)
						temp_chats_names = str(temp_list[4])
						temp_list[4] = temp_chats_names + ',' + str(viber_settings['_myUserName'])
						temp_chats_phones = str(temp_list[5])
						temp_list[5] = temp_chats_phones + ',' + str(viber_settings['_myPhoneNumber'])
						if temp_list[13]:
							y = json.loads(temp_list[13], strict=False) # the key that stores geolocation data is ['pa_message_data']['rich_media']['Buttons'][2]['Map']
							#if the 'Map' key is identified successfully it will assign lat,lon to the corresponding columns, otherwise it will continue on (passing any key,index errors)
							try:
								temp_list[18] = y['pa_message_data']['rich_media']['Buttons'][2]['Map']['Latitude']
								temp_list[19] = y['pa_message_data']['rich_media']['Buttons'][2]['Map']['Longitude']
							except KeyError:
								pass
							except IndexError:
								pass
						if temp_list[10] == 'Outgoing':
							temp_list[0] = viber_settings['_myUserName']
							temp_list[1] = ''
							temp_list[2] = viber_settings['_myPhoneNumber']
						
						if row[15] is not None:
							thumb = media_to_html(row[15], files_found, report_folder)
						else:
							thumb = ''
						
						row = tuple(temp_list)
						data_list.append((row[6], row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[14], row[15], thumb, row[8], row[9], row[10], row[11], row[12], row[16], row[17], row[18],row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[13]))
						

				if usageentries > 0:
					report = ArtifactHtmlReport('Viber - Chats')
					report.start_artifact_report(report_folder, 'Viber - Chats')
					report.add_script()
					data_headers = ('Timestamp', 'Sender (Display Full Name)','Sender (Display Short Name)','Sender (Phone)','Chat Name','Chat Participant(s)','Chat Phone(s)', 'Message Creation Date - UTC','Message Change State Date - UTC','Message Content','Attachment Name', 'Attachment','Call Date - UTC','Call Type','State','Duration (Seconds)','System Type Description','Attachment Type','Attachment Size','Latitude','Longitude','Conversation Deleted','Message Deleted','Time Bomb Duration','Time Bomb Timestamp','Conversation Marked Favorite','Likes Count','Message Metadata')
					report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Attachment']) #html_escape=False
					report.end_artifact_report()
					
					kmlactivity = 'Viber - Chats'
					kmlgen(report_folder, kmlactivity, data_list, data_headers)

					tsvname = 'Viber - Chats'
					tsv(report_folder, data_headers, data_list, tsvname)
					
				db.close()
			else:
				logfunc('No Viber data found.')
		