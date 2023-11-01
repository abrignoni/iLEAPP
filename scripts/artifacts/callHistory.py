__artifacts_v2__ = {
    "callhistory": {
        "name": "Call History",
        "description": "Parses and extract Call History",
        "author": "",
        "version": "0.5",
        "date": "2023-01-01",
        "requirements": "none",
        "category": "Call History",
        "notes": "",
        "paths": ('**/CallHistory.storedata*',),
        "function": "get_callHistory"
    }
}

# Updates: @SQLMcGee, James McGee of Metadata Forensics, LLC
# Date: 2023-03-30 Added column within callHistory for Call Ending Timestamp
# The Call Ending Timestamp provides an "at-a-glance" review of call lengths during analysis and review
# Additional details published within "Maximizing iOS Call Log Timestamps and Call Duration Effectiveness: Will You Answer the Call?" at https://sqlmcgee.wordpress.com/2022/11/30/maximizing-ios-call-log-timestamps-and-call-duration-effectiveness-will-you-answer-the-call/

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone, convert_bytes_to_unit

def get_callHistory(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    for file_found in files_found:
        file_found = str(file_found)
    
        if file_found.endswith('.storedata'):
            break
    
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select
    datetime(ZDATE+978307200,'unixepoch'),
    CASE
        WHEN ((datetime(ZDATE+978307200,'unixepoch')) = (datetime(((ZDATE) + (ZDURATION))+978307200,'unixepoch'))) then 'No Call Duration'
        ELSE (datetime(((ZDATE) + (ZDURATION))+978307200,'unixepoch'))
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
    CASE ZDISCONNECTED_CAUSE
        WHEN 0 then 'Ended'
        WHEN 6 then 'Rejected'
        ELSE ZDISCONNECTED_CAUSE
    END,
    upper(ZISO_COUNTRY_CODE),
    ZLOCATION
    from ZCALLRECORD
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    
    if usageentries > 0:
        
        for row in all_rows:
            starting_time = convert_ts_human_to_utc(row[0])
            starting_time = convert_utc_human_to_timezone(starting_time,timezone_offset)

            ending_time = row[1]
            if ending_time != 'No Call Duration':
                ending_time = convert_ts_human_to_utc(row[1])
                ending_time = convert_utc_human_to_timezone(ending_time,timezone_offset)

            an = str(row[5])
            an = an.replace("b'", "")
            an = an.replace("'", "")

            facetime_data = row[8]
            if facetime_data:
                facetime_data = convert_bytes_to_unit(facetime_data)


            data_list.append((starting_time, ending_time, row[2], row[3], row[4], an, row[6], 
                              row[7], facetime_data, row[9], row[10], row[11]))

        report = ArtifactHtmlReport('Call History')
        report.start_artifact_report(report_folder, 'Call History')
        report.add_script()
        data_headers = ('Starting Timestamp', 'Ending Timestamp', 'Service Provider', 'Call Type', 'Call Direction', 
                        'Phone Number', 'Answered', 'Call Duration', 'FaceTime Data', 'Disconnected Cause', 
                        'ISO Country Code', 'Location')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Call History'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Call History'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Call History data available')

