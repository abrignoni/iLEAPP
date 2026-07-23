__artifacts_v2__ = {
    "callHistoryGroupCall": {
        "name": "Call History - Group Call",
        "description": "Extract Call History",
        "author": "@SQLMcGee",
        "creation_date": "2025-02-05",
        "last_update_date": "2025-11-12",
        "requirements": "none",
        "category": "Call History",
        "notes": "",
        "paths": ('*/mobile/Library/CallHistoryDB/CallHistory*'),
        "output_types": "standard",
        "artifact_icon": "phone-call",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 16 rows",
            "dexter_ios18": "iOS 18.3.2 | 11 rows",
            "felix_ios17": "iOS 17.6.1 | 4 rows",
            "fsfull002_ios17": "iOS 17.1 | 14 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1003 rows",
            "iphone11_ios17": "iOS 17.3 | 36 rows",
            "iphone12_ios18": "iOS 18.7 | 28 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 41 rows",
            "abe_ios16": "iOS 16.5 | 41 rows",
            "felix23_ios16": "iOS 16.5 | 12 rows",
            "hickman_ios13": "iOS 13.3.1 | 32 rows",
            "hickman_ios14": "iOS 14.3 | 25 rows",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "callHistoryInteractionC": {
        "name": "interactionC Call History - Group Call",
        "description": "Extract Call History",
        "author": "@SQLMcGee",
        "creation_date": "2025-02-05",
        "last_update_date": "2025-11-12",
        "requirements": "none",
        "category": "Call History",
        "notes": "",
        "paths": (
            '*/mobile/Library/CoreDuet/People/interactionC.db*'),
        "output_types": "standard",
        "artifact_icon": "phone-call",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 8 rows",
            "dexter_ios18": "iOS 18.3.2 | 1 row",
            "felix_ios17": "iOS 17.6.1 | 4 rows",
            "fsfull002_ios17": "iOS 17.1 | 2 rows",
            "hc_ios18_7": "iOS 18.7.8 | 458 rows",
            "iphone11_ios17": "iOS 17.3 | 6 rows",
            "iphone12_ios18": "iOS 18.7 | 25 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 13 rows",
            "abe_ios16": "iOS 16.5 | 24 rows",
            "felix23_ios16": "iOS 16.5 | 4 rows",
            "hickman_ios13": "iOS 13.3.1 | 32 rows",
            "hickman_ios14": "iOS 14.3 | 16 rows",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_cocoa_core_data_ts_to_utc, get_file_path

@artifact_processor
def callHistoryGroupCall(context):
    data_list = []
    files_found = context.get_files_found()
    CallHistory = get_file_path(files_found, 'CallHistory.storedata')

    with open_sqlite_db_readonly(CallHistory) as db:
        cursor = db.cursor()

        # Check if Z_4REMOTEPARTICIPANTHANDLES column exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Z_2REMOTEPARTICIPANTHANDLES';")
        table_exists = cursor.fetchone()

        column_exists_4 = False
        column_exists_3 = False

        if table_exists:
            # Check if 'Z_4REMOTEPARTICIPANTHANDLES' exists
            cursor.execute("PRAGMA table_info(Z_2REMOTEPARTICIPANTHANDLES);")
            columns = cursor.fetchall()
            for column in columns:
                if column[1] == 'Z_4REMOTEPARTICIPANTHANDLES':
                    column_exists_4 = True
                if column[1] == 'Z_3REMOTEPARTICIPANTHANDLES':
                    column_exists_3 = True

        # Now decide which SQL query to use based on the columns present
        if column_exists_3:

            cursor.execute('''
            Select 
            "ZCALLRECORD"."ZDATE" As "Call Date/Time", 
            Case 
                When "ZCALLRECORD"."ZDATE" = ("ZCALLRECORD"."ZDATE" + "ZCALLRECORD"."ZDURATION") Then NULL
                Else ("ZCALLRECORD"."ZDATE" + "ZCALLRECORD"."ZDURATION") End As "Call End Date/Time", 
            ZSERVICE_PROVIDER AS "Service Provider",
            CASE ZCALLTYPE
                WHEN 0 then 'Third-Party App'
                WHEN 1 then 'Phone Call'
                WHEN 8 then 'FaceTime Video'
                WHEN 16 then 'FaceTime Audio'
                ELSE ZCALLTYPE
            END AS "Call Type", 
            CASE ZORIGINATED
                WHEN 0 then 'Incoming'
                WHEN 1 then 'Outgoing'
            END AS "Call Direction", 
            GROUP_CONCAT(ZHANDLE.ZVALUE, ', ') AS "Phone Number",
            CASE 
               WHEN COUNT(z_2remoteparticipanthandles.z_2remoteparticipantcalls) = 1 
               THEN 'Direct Call' 
               WHEN COUNT(z_2remoteparticipanthandles.z_2remoteparticipantcalls) > 1 
               THEN 'Group Call - ' || COUNT(z_2remoteparticipanthandles.z_2remoteparticipantcalls) || ' other parties'
            END AS "Call Description",
            CASE ZANSWERED
                WHEN 0 then 'No'
                WHEN 1 then 'Yes'
            END AS "Answered",
            CASE
                WHEN ZDURATION IS '0.0'
                THEN "No Call Duration" 
                WHEN ZDURATION > 0 THEN strftime('%H:%M:%S',(ZDURATION), 'unixepoch')  
            END AS "Call Duration",
            ZFACE_TIME_DATA AS "FaceTime Data",
            CASE
                WHEN ZDISCONNECTED_CAUSE = 6 AND ZSERVICE_PROVIDER LIKE '%whatsapp' AND ZDURATION <> '0.0' then 'Ended'
                WHEN ZDISCONNECTED_CAUSE = 6 AND ZSERVICE_PROVIDER LIKE '%whatsapp' AND ZORIGINATED = 1 then 'Missed or Rejected'
                WHEN ZDISCONNECTED_CAUSE = 2 AND ZSERVICE_PROVIDER LIKE '%whatsapp' then 'Rejected'
                WHEN ZDISCONNECTED_CAUSE = 6 AND ZSERVICE_PROVIDER LIKE '%whatsapp' then 'Missed'
                WHEN ZDISCONNECTED_CAUSE = 0 then 'Ended'
                WHEN ZDISCONNECTED_CAUSE = 2 then 'No Answer'
                WHEN ZDISCONNECTED_CAUSE = 6 then 'Rejected'
                WHEN ZDISCONNECTED_CAUSE = 41 then 'Ended'
                WHEN ZDISCONNECTED_CAUSE = 49 then 'No Answer'
                ELSE ZDISCONNECTED_CAUSE
            END AS "Disconnected Cause",
            UPPER(ZISO_COUNTRY_CODE),
            ZLOCATION
            From ZCALLRECORD
            LEFT OUTER JOIN Z_2REMOTEPARTICIPANTHANDLES ON Z_2REMOTEPARTICIPANTHANDLES.Z_2REMOTEPARTICIPANTCALLS IS ZCALLRECORD.Z_PK
            LEFT OUTER JOIN ZHANDLE ON Z_2REMOTEPARTICIPANTHANDLES.Z_3REMOTEPARTICIPANTHANDLES IS ZHANDLE.Z_PK
            GROUP BY Z_2REMOTEPARTICIPANTCALLS
            ''')

        # Now decide which SQL query to use based on the columns present
        if column_exists_4:

            cursor.execute('''
            Select 
            "ZCALLRECORD"."ZDATE" As "Call Date/Time", 
            Case 
                When "ZCALLRECORD"."ZDATE" = ("ZCALLRECORD"."ZDATE" + "ZCALLRECORD"."ZDURATION") Then NULL
                Else ("ZCALLRECORD"."ZDATE" + "ZCALLRECORD"."ZDURATION") End As "Call End Date/Time", 
            ZSERVICE_PROVIDER AS "Service Provider",
            CASE ZCALLTYPE
                WHEN 0 then 'Third-Party App'
                WHEN 1 then 'Phone Call'
                WHEN 8 then 'FaceTime Video'
                WHEN 16 then 'FaceTime Audio'
                ELSE ZCALLTYPE
            END AS "Call Type", 
            CASE ZORIGINATED
                WHEN 0 then 'Incoming'
                WHEN 1 then 'Outgoing'
            END AS "Call Direction", 
            GROUP_CONCAT(ZHANDLE.ZVALUE, ', ') AS "Phone Number",
            CASE 
               WHEN COUNT(z_2remoteparticipanthandles.z_2remoteparticipantcalls) = 1 
               THEN 'Direct Call' 
               WHEN COUNT(z_2remoteparticipanthandles.z_2remoteparticipantcalls) > 1 
               THEN 'Group Call - ' || COUNT(z_2remoteparticipanthandles.z_2remoteparticipantcalls) || ' other parties'
            END AS "Call Description",
            CASE ZANSWERED
                WHEN 0 then 'No'
                WHEN 1 then 'Yes'
            END AS "Answered",
            CASE
                WHEN ZDURATION IS '0.0'
                THEN "No Call Duration" 
                WHEN ZDURATION > 0 THEN strftime('%H:%M:%S',(ZDURATION), 'unixepoch')  
            END AS "Call Duration",
            ZFACE_TIME_DATA AS "FaceTime Data",
            CASE
                WHEN ZDISCONNECTED_CAUSE = 6 AND ZSERVICE_PROVIDER LIKE '%whatsapp' AND ZDURATION <> '0.0' then 'Ended'
                WHEN ZDISCONNECTED_CAUSE = 6 AND ZSERVICE_PROVIDER LIKE '%whatsapp' AND ZORIGINATED = 1 then 'Missed or Rejected'
                WHEN ZDISCONNECTED_CAUSE = 2 AND ZSERVICE_PROVIDER LIKE '%whatsapp' then 'Rejected'
                WHEN ZDISCONNECTED_CAUSE = 6 AND ZSERVICE_PROVIDER LIKE '%whatsapp' then 'Missed'
                WHEN ZDISCONNECTED_CAUSE = 0 then 'Ended'
                WHEN ZDISCONNECTED_CAUSE = 2 then 'No Answer'
                WHEN ZDISCONNECTED_CAUSE = 6 then 'Rejected'
                WHEN ZDISCONNECTED_CAUSE = 41 then 'Ended'
                WHEN ZDISCONNECTED_CAUSE = 49 then 'No Answer'
                ELSE ZDISCONNECTED_CAUSE
            END AS "Disconnected Cause",
            UPPER(ZISO_COUNTRY_CODE),
            ZLOCATION
            From ZCALLRECORD
            LEFT OUTER JOIN Z_2REMOTEPARTICIPANTHANDLES ON Z_2REMOTEPARTICIPANTHANDLES.Z_2REMOTEPARTICIPANTCALLS IS ZCALLRECORD.Z_PK
            LEFT OUTER JOIN ZHANDLE ON Z_2REMOTEPARTICIPANTHANDLES.Z_4REMOTEPARTICIPANTHANDLES IS ZHANDLE.Z_PK
            GROUP BY Z_2REMOTEPARTICIPANTCALLS
            ''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            start_timestamp = convert_cocoa_core_data_ts_to_utc(row[0])
            end_timestamp = convert_cocoa_core_data_ts_to_utc(row[1])
            data_list.append(
                (start_timestamp, end_timestamp, row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12]))
        
    data_headers = (
        ('Call Date/Time', 'datetime'), ('Call End Date/Time', 'datetime'), 'Service Provider', 
        'Call Type', 'Call Direction', ('Phone Number', 'phonenumber'), 'Call Description', 
        'Answered', 'Call Duration', 'FaceTime Data', 'Disconnected Cause', 'ISO Country Code', 'Location')
    return data_headers, data_list, CallHistory

@artifact_processor
def callHistoryInteractionC(context):
    data_list = []
    files_found = context.get_files_found()
    interactionC = get_file_path(files_found, 'interactionC.db')
    
    with open_sqlite_db_readonly(interactionC) as db:
        cursor = db.cursor()

        cursor.execute('''
            SELECT
            ZINTERACTIONS.ZSTARTDATE AS "Call Date/Time",
            ZINTERACTIONS.ZENDDATE AS "Call End Date/Time",
            ZBUNDLEID AS "Application Bundle ID",
            CASE
                WHEN ZDIRECTION IS 1 THEN "Outgoing"
                WHEN ZDIRECTION IS 0 THEN "Incoming"
            END AS "Direction",
            GROUP_CONCAT(ZDISPLAYNAME, ', ') AS "Display Name",
            GROUP_CONCAT(ZIDENTIFIER, ', ') AS "Phone Number",
            CASE
                WHEN ZRECIPIENTCOUNT IS 1 THEN "Direct Call"
                WHEN ZRECIPIENTCOUNT > 1 THEN 'Group Call - ' || COUNT(ZRECIPIENTCOUNT) || ' other parties'
                ELSE ZRECIPIENTCOUNT
            END AS "Call Description",
            strftime('%H:%M:%S',(ZENDDATE-ZSTARTDATE), 'unixepoch')  AS "Interaction Duration"
            FROM ZINTERACTIONS
            LEFT OUTER JOIN Z_2INTERACTIONRECIPIENT on Z_2INTERACTIONRECIPIENT.Z_3INTERACTIONRECIPIENT is ZINTERACTIONS.Z_PK
            LEFT OUTER JOIN ZCONTACTS on Z_2INTERACTIONRECIPIENT.Z_2RECIPIENTS is ZCONTACTS.Z_PK
            WHERE ZBUNDLEID like "com.apple.InCallService" or ZBUNDLEID like "com.apple.facetime" or ZBUNDLEID like "com.apple.mobilephone"
            GROUP BY Z_3INTERACTIONRECIPIENT
        ''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            start_timestamp = convert_cocoa_core_data_ts_to_utc(row[0])
            end_timestamp = convert_cocoa_core_data_ts_to_utc(row[1])
            data_list.append(
                (start_timestamp, end_timestamp, row[2], row[3], row[4], row[5], row[6], row[7]))
        
    data_headers = (
        ('Call Date/Time', 'datetime'), ('Call End Date/Time', 'datetime'), 'Service Provider', 
        'Call Direction', 'Display Name', ('Phone Number', 'phonenumber'), 'Call Description', 'Interaction Duration')
    return data_headers, data_list, interactionC
