# Module Description: Parses Message, Call, and Media AppIntent Data from the siriremembers.sqlite3 database
# Author: @SQL_McGee through https://github.com/MetadataForensics
# Date: 2024-01-29
# Artifact version: 0.0.1
# Requirements: none

# This query was the product of research completed by James McGee, Metadata Forensics, LLC, for "Siri's Memory Lane: Exploring the siriremembers Database"
# https://metadataperspective.com/2024/01/29/siris-memory-lane-exploring-the-siriremembers-database/
# Additional data at https://github.com/MetadataForensics/siriremembers

import sqlite3
import textwrap
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_SiriRemembers(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    SiriRemembers = ''
    
    for file_found in files_found:
        file_name = str(file_found)
        if file_name.endswith('siriremembers.sqlite3'):
            SiriRemembers = str(file_found)
            source_file_sms = file_found.replace(seeker.directory, '')
   
    db = open_sqlite_db_readonly(SiriRemembers)
    
    cursor = db.cursor()
    
    # Messages
    
    cursor.execute('''
    SELECT *
    FROM (
    SELECT
        datetime(intents.start_date, 'UNIXEPOCH') as "Timestamp",
		CASE 
		WHEN apps.bundle_id = 'com.apple.MobileSMS' THEN
			CASE
				WHEN intents.direction = '1' THEN
					COALESCE((
						SELECT entities.tokens
						FROM intent_entities
						JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
						JOIN entities ON entities.id = intent_entities.entity_id
						WHERE
							intent_entities.intent_id = intents.id
							AND parameter_names.name = 'recipients'
					), 'Owner')
				WHEN intents.direction = '2' THEN 'Owner'
			END
		WHEN apps.bundle_id = 'com.toyopagroup.picaboo' THEN
			CASE
				WHEN intents.direction = '1' THEN
					COALESCE((
						SELECT entities.tokens
						FROM intent_entities
						JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
						JOIN entities ON entities.id = intent_entities.entity_id
						WHERE
							intent_entities.intent_id = intents.id
							AND parameter_names.name = 'speakableGroupName'
					), 'Owner')
				WHEN intents.direction = '2' THEN 'Owner'
			END
		WHEN apps.bundle_id = 'com.burbn.instagram' THEN
			CASE
				WHEN intents.direction = '1' THEN
					COALESCE((
						SELECT entities.tokens
						FROM intent_entities
						JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
						JOIN entities ON entities.id = intent_entities.entity_id
						WHERE
							intent_entities.intent_id = intents.id
							AND parameter_names.name = 'speakableGroupName'
					), 'Owner')
				WHEN intents.direction = '2' THEN 'Owner'
			END
		WHEN apps.bundle_id = 'org.whispersystems.signal' THEN
			CASE
				WHEN intents.direction = '1' THEN
					COALESCE((
						SELECT entities.uuid
						FROM intent_entities
						JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
						JOIN entities ON entities.id = intent_entities.entity_id
						WHERE
							intent_entities.intent_id = intents.id
							AND parameter_names.name = 'recipientHandles'
					), 'Owner')
				WHEN intents.direction = '2' THEN 'Owner'
				END
		ELSE
		    CASE
				WHEN intents.direction = '1' THEN
					COALESCE((
						SELECT entities.tokens
						FROM intent_entities
						JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
						JOIN entities ON entities.id = intent_entities.entity_id
						WHERE
							intent_entities.intent_id = intents.id
							AND parameter_names.name = 'recipients'
					), 'Owner')
				WHEN intents.direction = '2' THEN 'Owner'
			END
	END as "Recipient",
	CASE 
		WHEN apps.bundle_id = 'com.apple.MobileSMS' THEN
			CASE
				WHEN intents.direction = '1' THEN
					COALESCE((
						SELECT entities.uuid
						FROM intent_entities
						JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
						JOIN entities ON entities.id = intent_entities.entity_id
						WHERE
							intent_entities.intent_id = intents.id
							AND parameter_names.name = 'recipientHandles'
					), 'Owner')
				WHEN intents.direction = '2' THEN 'Owner'
			END
		WHEN apps.bundle_id = 'com.toyopagroup.picaboo' THEN
			CASE
				WHEN intents.direction = '1' THEN
					COALESCE((
						SELECT entities.tokens
						FROM intent_entities
						JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
						JOIN entities ON entities.id = intent_entities.entity_id
						WHERE
							intent_entities.intent_id = intents.id
							AND parameter_names.name = 'speakableGroupName'
					), 'Owner')
				WHEN intents.direction = '2' THEN 'Owner'
			END
		WHEN apps.bundle_id = 'com.burbn.instagram' THEN
			CASE
				WHEN intents.direction = '1' THEN
					COALESCE((
						SELECT entities.uuid
						FROM intent_entities
						JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
						JOIN entities ON entities.id = intent_entities.entity_id
						WHERE
							intent_entities.intent_id = intents.id
							AND parameter_names.name = 'recipientHandles'
					), 'Owner')
				WHEN intents.direction = '2' THEN 'Owner'
			END
		WHEN apps.bundle_id = 'org.whispersystems.signal' THEN
			CASE
				WHEN intents.direction = '1' THEN
					COALESCE((
						SELECT entities.uuid
						FROM intent_entities
						JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
						JOIN entities ON entities.id = intent_entities.entity_id
						WHERE
							intent_entities.intent_id = intents.id
							AND parameter_names.name = 'recipientHandles'
					), 'Owner')
				WHEN intents.direction = '2' THEN 'Owner'
				END
		ELSE
			CASE
				WHEN intents.direction = '1' THEN
					COALESCE((
						SELECT entities.uuid
						FROM intent_entities
						JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
						JOIN entities ON entities.id = intent_entities.entity_id
						WHERE
							intent_entities.intent_id = intents.id
							AND parameter_names.name = 'recipientHandles'
					), 'Owner')
				WHEN intents.direction = '2' THEN 'Owner'
			END
	END as "Recipient Handle",
	CASE 
		WHEN apps.bundle_id = 'com.apple.MobileSMS' THEN
			CASE
				WHEN intents.direction = '2' THEN
					COALESCE((
						SELECT entities.tokens
						FROM intent_entities
						JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
						JOIN entities ON entities.id = intent_entities.entity_id
						WHERE
							intent_entities.intent_id = intents.id
							AND parameter_names.name = 'sender'
					), 'Sender')
				WHEN intents.direction = '1' THEN 'Owner'
			END
		WHEN apps.bundle_id = 'com.toyopagroup.picaboo' THEN
			CASE
				WHEN intents.direction = '2' THEN
					COALESCE((
						SELECT entities.tokens
						FROM intent_entities
						JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
						JOIN entities ON entities.id = intent_entities.entity_id
						WHERE
							intent_entities.intent_id = intents.id
							AND parameter_names.name = 'sender'
					), 'Sender')
				WHEN intents.direction = '1' THEN 'Owner'
			END
		WHEN apps.bundle_id = 'com.burbn.instagram' THEN
			CASE
				WHEN intents.direction = '2' THEN
					COALESCE((
						SELECT entities.tokens
						FROM intent_entities
						JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
						JOIN entities ON entities.id = intent_entities.entity_id
						WHERE
							intent_entities.intent_id = intents.id
							AND parameter_names.name = 'speakableGroupName'
					), 'Sender')
				WHEN intents.direction = '1' THEN 'Owner'
			END
		WHEN apps.bundle_id = 'org.whispersystems.signal' THEN
			CASE
				WHEN intents.direction = '1' THEN
					COALESCE((
						SELECT entities.uuid
						FROM intent_entities
						JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
						JOIN entities ON entities.id = intent_entities.entity_id
						WHERE
							intent_entities.intent_id = intents.id
							AND parameter_names.name = 'recipientHandles'
					), 'Owner')
				WHEN intents.direction = '2' THEN
					COALESCE((
						SELECT entities.uuid
						FROM intent_entities
						JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
						JOIN entities ON entities.id = intent_entities.entity_id
						WHERE
							intent_entities.intent_id = intents.id
							AND parameter_names.name = 'recipientHandles'
					), 'Sender')
				END
		ELSE
		    CASE
				WHEN intents.direction = '2' THEN
					COALESCE((
						SELECT entities.tokens
						FROM intent_entities
						JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
						JOIN entities ON entities.id = intent_entities.entity_id
						WHERE
							intent_entities.intent_id = intents.id
							AND parameter_names.name = 'sender'
					), 'Sender')
				WHEN intents.direction = '1' THEN 'Owner'
			END
	END as "Sender",
	CASE 
		WHEN apps.bundle_id = 'com.apple.MobileSMS' THEN
			CASE
				WHEN intents.direction = '2' THEN
					COALESCE((
						SELECT entities.uuid
						FROM intent_entities
						JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
						JOIN entities ON entities.id = intent_entities.entity_id
						WHERE
							intent_entities.intent_id = intents.id
							AND parameter_names.name = 'senderHandle'
					), 'Sender')
				WHEN intents.direction = '1' THEN 'Owner'
			END
		WHEN apps.bundle_id = 'com.toyopagroup.picaboo' THEN
			CASE
				WHEN intents.direction = '2' THEN
					COALESCE((
						SELECT entities.tokens
						FROM intent_entities
						JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
						JOIN entities ON entities.id = intent_entities.entity_id
						WHERE
							intent_entities.intent_id = intents.id
							AND parameter_names.name = 'speakableGroupName'
					), 'Sender')
				WHEN intents.direction = '1' THEN 'Owner'
			END
		WHEN apps.bundle_id = 'com.burbn.instagram' THEN
			CASE
				WHEN intents.direction = '2' THEN
					COALESCE((
						SELECT entities.uuid
						FROM intent_entities
						JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
						JOIN entities ON entities.id = intent_entities.entity_id
						WHERE
							intent_entities.intent_id = intents.id
							AND parameter_names.name = 'recipientHandles'
					), 'Sender')
				WHEN intents.direction = '1' THEN 'Owner'
			END
		WHEN apps.bundle_id = 'org.whispersystems.signal' THEN
			CASE
				WHEN intents.direction = '1' THEN
					COALESCE((
						SELECT entities.uuid
						FROM intent_entities
						JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
						JOIN entities ON entities.id = intent_entities.entity_id
						WHERE
							intent_entities.intent_id = intents.id
							AND parameter_names.name = 'recipientHandles'
					), 'Owner')
				WHEN intents.direction = '2' THEN
					COALESCE((
						SELECT entities.uuid
						FROM intent_entities
						JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
						JOIN entities ON entities.id = intent_entities.entity_id
						WHERE
							intent_entities.intent_id = intents.id
							AND parameter_names.name = 'recipientHandles'
					), 'Sender')
				END
		ELSE
		    CASE
				WHEN intents.direction = '2' THEN
					COALESCE((
						SELECT entities.uuid
						FROM intent_entities
						JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
						JOIN entities ON entities.id = intent_entities.entity_id
						WHERE
							intent_entities.intent_id = intents.id
							AND parameter_names.name = 'senderHandle'
					), 'Sender')
				WHEN intents.direction = '1' THEN 'Owner'
			END
	END as "Sender Handle",
    CASE 
        WHEN intents.direction = '1' THEN 'Sent'
        WHEN intents.direction = '2' THEN 'Received'
    END as "Direction",
	CASE
		WHEN intents.donated_by_siri = '0' THEN 'No'
		WHEN intents.donated_by_siri = '1' THEN 'Yes'
	END as "Donated by Siri",
    apps.bundle_id as "Application Bundle ID",
	CASE
        WHEN intents.donated_by_siri = '1' AND 
             intents.start_date = LEAD(intents.start_date) OVER (ORDER BY intents.id) THEN
            LEAD(SUBSTR(intents.dkevent_uuid, INSTR(intents.dkevent_uuid, ':') + 1)) OVER (ORDER BY intents.id)
        WHEN intents.donated_by_siri = '1' AND 
             intents.start_date = LAG(intents.start_date) OVER (ORDER BY intents.id) THEN
            LAG(SUBSTR(intents.dkevent_uuid, INSTR(intents.dkevent_uuid, ':') + 1)) OVER (ORDER BY intents.id)
        ELSE 
            SUBSTR(intents.dkevent_uuid, INSTR(intents.dkevent_uuid, ':') + 1)
    END as "Application UUID",
    domains.name as "Domain ID",
    verbs.name as "Verb ID",
    intents.id as "Intents ID",
    intents.uuid as "Intents UUID",
        CASE 
            WHEN intents.donated_by_siri = '1' AND intents.start_date = LEAD(intents.start_date) OVER (ORDER BY intents.id) THEN 'Active'
            WHEN intents.donated_by_siri = '1' AND intents.start_date = LAG(intents.start_date) OVER (ORDER BY intents.id) THEN 'Active'
            WHEN intents.donated_by_siri = '0' AND intents.start_date = LEAD(intents.start_date) OVER (ORDER BY intents.id) THEN 'Inactive'
            WHEN intents.donated_by_siri = '0' AND intents.start_date = LAG(intents.start_date) OVER (ORDER BY intents.id) THEN 'Inactive'
            ELSE 'Active'
        END as "is_active_flag"
    FROM intents
    LEFT OUTER JOIN domains ON domains.id = intents.domain_id
    LEFT OUTER JOIN verbs ON verbs.id = intents.verb_id
    LEFT OUTER JOIN apps ON apps.id = intents.app_id
    LEFT OUTER JOIN groups ON groups.id = intents.group_id
    WHERE domains.name = 'Messages'
    ) AS subquery
    WHERE "is_active_flag" = 'Active';
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            data_list.append(
            (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13]))
            
        report = ArtifactHtmlReport('Siri Remembers - Messages')
        report.start_artifact_report(report_folder, 'Siri Remembers - Messages')
        report.add_script()
        data_headers = (
            'Timestamp', 'Recipient', 'Recipient Handle', 'Sender', 'Sender Handle', 'Direction', 'Donated by Siri', 'Application Bundle ID', 
            'Application UUID', 'Domain ID', 'Verb ID', 'Intents ID', 'Intents UUID', 'Active Row')
        report.write_artifact_data_table(data_headers, data_list, SiriRemembers)
        report.end_artifact_report()

        tsvname = 'Siri Remembers - Messages'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Siri Remembers - Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in Siri Remembers - Messages')
    
    # Calls
    
    cursor.execute('''
    SELECT
	datetime(intents.start_date, 'UNIXEPOCH') as "Timestamp",
	COALESCE((
        SELECT 
            CASE 
				WHEN intents.direction = '0' AND intents.donated_by_siri = '1' THEN entities.tokens
                WHEN intents.direction = '1' THEN entities.tokens
                ELSE 'Owner'
            END
        FROM intent_entities
        JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
        JOIN entities ON entities.id = intent_entities.entity_id
        WHERE
            intent_entities.intent_id = intents.id
            AND parameter_names.name = 'contacts'
    ), 'Owner') as "Recipient",
    COALESCE((
        SELECT 
            CASE 
				WHEN intents.direction = '0' AND intents.donated_by_siri = '1' THEN entities.uuid
                WHEN intents.direction = '1' THEN entities.uuid
                ELSE 'Owner'
            END
        FROM intent_entities
        JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
        JOIN entities ON entities.id = intent_entities.entity_id
        WHERE
            intent_entities.intent_id = intents.id
            AND parameter_names.name = 'contactHandles'
    ), 'Owner') as "Recipient Handle",
    COALESCE((
        SELECT 
            CASE 
                WHEN intents.direction = '2' THEN entities.tokens
                ELSE 'Owner'
            END
        FROM intent_entities
        JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
        JOIN entities ON entities.id = intent_entities.entity_id
        WHERE
            intent_entities.intent_id = intents.id
            AND parameter_names.name = 'contacts'
    ), 'Owner') as "Sender",
    COALESCE((
        SELECT 
            CASE 
                WHEN intents.direction = '2' THEN entities.uuid
                ELSE 'Owner'
            END
        FROM intent_entities
        JOIN parameter_names ON parameter_names.id = intent_entities.parameter_name_id
        JOIN entities ON entities.id = intent_entities.entity_id
        WHERE
            intent_entities.intent_id = intents.id
            AND parameter_names.name = 'contactHandles'
    ), 'Owner') as "Sender Handle",
    CASE 
        WHEN intents.direction = '1' THEN 'Outgoing'
        WHEN intents.direction = '2' THEN 'Incoming'
		WHEN intents.direction = '0' AND intents.donated_by_siri = '1' THEN 'Outgoing'
    END as "Direction",
	CASE 
		WHEN intents.duration_seconds = '0' THEN 'Not Answered or Missed'
		ELSE strftime('%H:%M:%S', intents.duration_seconds, 'unixepoch')
	END as "Duration",
	CASE
		WHEN intents.donated_by_siri = '0' THEN 'No'
		WHEN intents.donated_by_siri = '1' THEN 'Yes'
	END as "Donated by Siri",
    apps.bundle_id as "Application Bundle ID",
	SUBSTR(intents.dkevent_uuid, INSTR(intents.dkevent_uuid, ':') + 1) as "Application UUID",
    domains.name as "Domain ID",
    verbs.name as "Verb ID",
    intents.id as "Intents ID",
    intents.uuid as "Intents UUID"
    FROM intents
    LEFT OUTER JOIN domains ON domains.id = intents.domain_id
    LEFT OUTER JOIN verbs ON verbs.id = intents.verb_id
    LEFT OUTER JOIN apps ON apps.id = intents.app_id
    LEFT OUTER JOIN groups ON groups.id = intents.group_id
    WHERE domains.name = "Calls"
    GROUP BY intents.uuid;
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            data_list.append(
            (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13]))
            
        report = ArtifactHtmlReport('Siri Remembers - Calls')
        report.start_artifact_report(report_folder, 'Siri Remembers - Calls')
        report.add_script()
        data_headers = (
            'Timestamp', 'Recipient', 'Recipient Handle', 'Sender', 'Sender Handle', 'Direction', 'Duration', 'Donated by Siri', 'Application Bundle ID', 'Application UUID', 'Domain ID', 'Verb ID', 'Intents ID', 'Intents UUID')
        report.write_artifact_data_table(data_headers, data_list, SiriRemembers)
        report.end_artifact_report()

        tsvname = 'Siri Remembers - Calls'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Siri Remembers - Calls'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in Siri Remembers - Calls')

    # Media
    
    cursor.execute('''
    SELECT
	datetime(intents.start_date, 'UNIXEPOCH') as "Timestamp",
	CASE
		WHEN entities.tokens like '%mediatype%' or entities.tokens like '% zzz%' THEN
			CASE 
				WHEN entity_types.name = 'MediaSearchItem'
					THEN SUBSTR(entities.tokens, 1, INSTR(entities.tokens, 'mediatype') - 1)
				WHEN entity_types.name = 'INMediaItem'
					THEN SUBSTR(entities.tokens, 1, INSTR(entities.tokens, ' zzz') - 1)
				END
		ELSE entities.tokens
	END AS "Media",
    apps.bundle_id as "Application Bundle ID",
	CASE
		WHEN intents.donated_by_siri = '0' THEN 'No'
		WHEN intents.donated_by_siri = '1' THEN 'Yes'
	END as "Donated by Siri",
	SUBSTR(intents.dkevent_uuid, INSTR(intents.dkevent_uuid, ':') + 1) as "Application UUID",
    domains.name as "Domain ID",
    verbs.name as "Verb ID",
    intents.id as "Intents ID",
    intents.uuid as "Intents UUID"
    FROM intents
    LEFT OUTER JOIN domains ON domains.id = intents.domain_id
    LEFT OUTER JOIN verbs ON verbs.id = intents.verb_id
    LEFT OUTER JOIN apps ON apps.id = intents.app_id
    LEFT OUTER JOIN group_entities on group_entities.group_id = intents.group_id
    LEFT OUTER JOIN entities on entities.id = group_entities.entity_id
    LEFT OUTER JOIN entity_types on entity_types.id = entities.type_id
    WHERE domains.name = 'Media'
    GROUP BY intents.uuid;
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            data_list.append(
            (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
            
        report = ArtifactHtmlReport('Siri Remembers - Media')
        report.start_artifact_report(report_folder, 'Siri Remembers - Media')
        report.add_script()
        data_headers = (
            'Timestamp', 'Media', 'Application Bundle ID', 'Donated by Siri', 'Application UUID', 'Domain ID', 'Verb ID', 'Intents ID', 'Intents UUID')
        report.write_artifact_data_table(data_headers, data_list, SiriRemembers)
        report.end_artifact_report()

        tsvname = 'Siri Remembers - Media'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Siri Remembers - Media'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in Siri Remembers - Media')
        
__artifacts__ = {
    "Siri Remembers": (
        "Siri Remembers",
        ('*/mobile/Library/com.apple.siri.inference/siriremembers*'),
        get_SiriRemembers)
}
