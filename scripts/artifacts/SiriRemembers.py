# Parses Message, Call, and Media AppIntent data from the siriremembers.sqlite3 database.
# The queries are the product of research by James McGee, Metadata Forensics, LLC, for
# "Siri's Memory Lane: Exploring the siriremembers Database":
# https://metadataperspective.com/2024/01/29/siris-memory-lane-exploring-the-siriremembers-database/
# Additional data at https://github.com/MetadataForensics/siriremembers
__artifacts_v2__ = {
    "siriRemembersMessages": {
        "name": "Siri Remembers - Messages",
        "description": "Message AppIntent data from the siriremembers database",
        "author": "@SQL_McGee (James McGee, Metadata Forensics, LLC)",
        "creation_date": "2024-01-29",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Siri Remembers",
        "notes": "Research: https://metadataperspective.com/2024/01/29/"
                 "siris-memory-lane-exploring-the-siriremembers-database/",
        "paths": ('*/mobile/Library/com.apple.siri.inference/siriremembers*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 251 rows",
            "felix_ios17": "iOS 17.6.1 | 7 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 70 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 703 rows",
        }
    },
    "siriRemembersCalls": {
        "name": "Siri Remembers - Calls",
        "description": "Call AppIntent data from the siriremembers database",
        "author": "@SQL_McGee (James McGee, Metadata Forensics, LLC)",
        "creation_date": "2024-01-29",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Siri Remembers",
        "notes": "Research: https://metadataperspective.com/2024/01/29/"
                 "siris-memory-lane-exploring-the-siriremembers-database/",
        "paths": ('*/mobile/Library/com.apple.siri.inference/siriremembers*',),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 8 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 8 rows",
        }
    },
    "siriRemembersMedia": {
        "name": "Siri Remembers - Media",
        "description": "Media AppIntent data from the siriremembers database",
        "author": "@SQL_McGee (James McGee, Metadata Forensics, LLC)",
        "creation_date": "2024-01-29",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Siri Remembers",
        "notes": "Research: https://metadataperspective.com/2024/01/29/"
                 "siris-memory-lane-exploring-the-siriremembers-database/",
        "paths": ('*/mobile/Library/com.apple.siri.inference/siriremembers*',),
        "output_types": "standard",
        "artifact_icon": "music",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 1 row",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
        }
    }
}

import sqlite3

from scripts.ilapfuncs import (artifact_processor, does_table_exist_in_db,
                               get_sqlite_db_records, logfunc)

_MESSAGES_QUERY = '''
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
'''

_CALLS_QUERY = '''
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
'''

_MEDIA_QUERY = '''
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
'''


def _find_db(context):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('siriremembers.sqlite3'):
            return file_found
    return ''


def _run(context, query, headers):
    data_list = []
    source_path = _find_db(context)
    if not source_path:
        return headers, data_list, ''
    rel = context.get_relative_path(source_path)
    if not does_table_exist_in_db(source_path, 'intents'):
        return headers, data_list, rel
    try:
        rows = get_sqlite_db_records(source_path, query)
    except sqlite3.Error as ex:
        logfunc(f'Error reading Siri Remembers data: {ex}')
        return headers, data_list, rel
    for row in rows:
        data_list.append(tuple(row))
    return headers, data_list, rel


@artifact_processor
def siriRemembersMessages(context):
    data_headers = (
        ('Timestamp', 'datetime'), 'Recipient', 'Recipient Handle', 'Sender', 'Sender Handle',
        'Direction', 'Donated by Siri', 'Application Bundle ID', 'Application UUID', 'Domain ID',
        'Verb ID', 'Intents ID', 'Intents UUID', 'Active Row')
    return _run(context, _MESSAGES_QUERY, data_headers)


@artifact_processor
def siriRemembersCalls(context):
    data_headers = (
        ('Timestamp', 'datetime'), 'Recipient', 'Recipient Handle', 'Sender', 'Sender Handle',
        'Direction', 'Duration', 'Donated by Siri', 'Application Bundle ID', 'Application UUID',
        'Domain ID', 'Verb ID', 'Intents ID', 'Intents UUID')
    return _run(context, _CALLS_QUERY, data_headers)


@artifact_processor
def siriRemembersMedia(context):
    data_headers = (
        ('Timestamp', 'datetime'), 'Media', 'Application Bundle ID', 'Donated by Siri',
        'Application UUID', 'Domain ID', 'Verb ID', 'Intents ID', 'Intents UUID')
    return _run(context, _MEDIA_QUERY, data_headers)
