__artifacts_v2__ = {
    "callHistory": {
        "name": "Call History",
        "description": "Extract Call History",
        "author": "@AlexisBrignoni - @JohnHyla",
        "version": "0.8",
        "date": "2020-04-30",
        "requirements": "none",
        "category": "Call History",
        "notes": "",
        "paths": (
            '*/mobile/Library/CallHistoryDB/CallHistory*', 
            '*/mobile/Library/CallHistoryDB/call_history.db*'),
        "output_types": "standard",
        "artifact_icon": "phone-call"
    }
}

# Updates: @SQLMcGee, James McGee of Metadata Forensics, LLC
# Date: 2023-03-30 Added column within callHistory for Call Ending Timestamp
# The Call Ending Timestamp provides an "at-a-glance" review of call lengths during analysis and review
# Additional details published within "Maximizing iOS Call Log Timestamps and Call Duration Effectiveness: Will You Answer the Call?" at https://sqlmcgee.wordpress.com/2022/11/30/maximizing-ios-call-log-timestamps-and-call-duration-effectiveness-will-you-answer-the-call/

from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, convert_bytes_to_unit, convert_cocoa_core_data_ts_to_utc

@artifact_processor
def callHistory(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = ''
    data_list = []

    db_path = get_file_path(files_found, "CallHistory.storedata")
    temp_db_path = get_file_path(files_found, "CallHistoryTemp.storedata")
    old_db_path = get_file_path(files_found, "call_history.db")
    records = []
    records_in_both_db = False

    #call_history.db schema taken from here https://avi.alkalay.net/2011/12/iphone-call-history.html 
    query = '''
    select
    ZDATE,
    CASE
        WHEN ZDATE = (ZDATE + ZDURATION) then NULL
        ELSE (ZDATE + ZDURATION)
    END, 
    ZSERVICE_PROVIDER,
    CASE ZCALLTYPE
        WHEN 0 then 'Third-Party App'
        WHEN 1 then 'Phone Call'
        WHEN 8 then 'FaceTime Video'
        WHEN 16 then 'FaceTime Audio'
        ELSE ZCALLTYPE
    END,
    CASE ZORIGINATED
        WHEN 0 then 'Incoming'
        WHEN 1 then 'Outgoing'
    END,  
    ZADDRESS,
    CASE ZANSWERED
        WHEN 0 then 'No'
        WHEN 1 then 'Yes'
    END,
    strftime('%H:%M:%S',ZDURATION, 'unixepoch'),
    ZFACE_TIME_DATA,
    CASE
		WHEN ZDISCONNECTED_CAUSE = 6 AND  ZSERVICE_PROVIDER LIKE '%whatsapp' AND ZDURATION <> '0.0' then 'Ended'
		WHEN ZDISCONNECTED_CAUSE = 6 AND  ZSERVICE_PROVIDER LIKE '%whatsapp' AND ZORIGINATED = 1 then 'Missed or Rejected'
		WHEN ZDISCONNECTED_CAUSE = 2 AND  ZSERVICE_PROVIDER LIKE '%whatsapp' then 'Rejected'
		WHEN ZDISCONNECTED_CAUSE = 6 AND  ZSERVICE_PROVIDER LIKE '%whatsapp' then 'Missed'
		WHEN ZDISCONNECTED_CAUSE = 0 then 'Ended'
        WHEN ZDISCONNECTED_CAUSE = 6 then 'Rejected'
        ELSE ZDISCONNECTED_CAUSE
    END ZDISCONNECTED_CAUSE,
    upper(ZISO_COUNTRY_CODE),
    ZLOCATION
    from ZCALLRECORD
    '''

    old_query = '''
    select
    datetime(date, 'unixepoch'),
    CASE
        WHEN datetime(date,'unixepoch') = datetime((date + duration),'unixepoch') then NULL
        ELSE datetime((date + duration), 'unixepoch')
    END,
    'N/A' as ZSERVICE_PROVIDER,
    CASE
        WHEN flags&4=4 then 'Phone Call'
        When flags&16=16 then 'FaceTime Call'
    END,
    CASE 
        WHEN flags=0 then 'Incoming'
        WHEN flags&1=1 then 'Outgoing'
    END,
    address,
    CASE read
        WHEN 0 then 'No'
        WHEN 1 then 'Yes'
    END,
    strftime('%H:%M:%S', duration, 'unixepoch'),
    face_time_data,
    'N/A' as ZDISCONNECTED_CAUSE,
    country_code,
    'N/A' as ZLOCATION
    from call
    '''

    db_records = get_sqlite_db_records(db_path, query)
    temp_db_records = get_sqlite_db_records(temp_db_path, query)
    if db_path or temp_db_path:
        if db_records and temp_db_records:
            source_path = "Source file path in the report below"
            records_in_both_db = True
            records = [tuple(list(record) + [db_path]) for record in db_records] + [tuple(list(record) + [temp_db_path]) for record in temp_db_records]
        else:
            records = db_records if db_records else temp_db_records
            source_path = db_path if db_path else temp_db_path
    elif old_db_path:
        records = get_sqlite_db_records(old_db_path, old_query)
        source_path = old_db_path if records else ''
    
    for record in records:
        starting_time = convert_cocoa_core_data_ts_to_utc(record[0])
        ending_time = convert_cocoa_core_data_ts_to_utc(record[1])

        an = str(record[5])
        an = an.replace("b'", "")
        an = an.replace("'", "")

        facetime_data = convert_bytes_to_unit(record[8])

        record_data = [starting_time, ending_time, record[2], record[3], record[4], an, record[6], 
                            record[7], facetime_data, record[9], record[10], record[11]]
        if records_in_both_db:
            record_data.append(record[12])
        data_list.append(tuple(record_data))

    headers = [
        ('Starting Timestamp', 'datetime'), 
        ('Ending Timestamp', 'datetime'), 
        'Service Provider', 
        'Call Type', 
        'Call Direction', 
        ('Phone Number', 'phonenumber'), 
        'Answered', 
        'Call Duration', 
        'FaceTime Data', 
        'Disconnected Cause', 
        'ISO Country Code', 
        'Location'
        ]
    if records_in_both_db:
        headers.append('Source File path')
    
    data_headers = tuple(headers)
    return data_headers, data_list, source_path
