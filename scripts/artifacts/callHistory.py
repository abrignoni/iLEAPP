__artifacts_v2__ = {
    "callHistory": {
        "name": "Call History",
        "description": "Extract Call History",
        "author": "@AlexisBrignoni",
        "version": "0.7",
        "date": "2020-04-30",
        "requirements": "none",
        "category": "Call History",
        "notes": "",
        "paths": ('*/mobile/Library/CallHistoryDB/CallHistory.storedata*','*/mobile/Library/CallHistoryDB/call_history.db*',),
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
    source_path = ""
    storedata_path = get_file_path(files_found, "CallHistory.storedata")
    db_path = get_file_path(files_found, "call_history.db")
    data_list = []

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

    query_old = '''
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

    if storedata_path:
        source_path = storedata_path
    else:
        source_path = db_path
        query = query_old
        
    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        starting_time = convert_cocoa_core_data_ts_to_utc(record[0])
        ending_time = convert_cocoa_core_data_ts_to_utc(record[1])

        an = str(record[5])
        an = an.replace("b'", "")
        an = an.replace("'", "")

        facetime_data = convert_bytes_to_unit(record[8])

        data_list.append((starting_time, ending_time, record[2], record[3], record[4], an, record[6], 
                            record[7], facetime_data, record[9], record[10], record[11]))

    data_headers = (
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
        )
    return data_headers, data_list, source_path
