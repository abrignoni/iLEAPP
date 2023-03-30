# Updates: @SQLMcGee, James McGee of Metadata Forensics, LLC
# Date: 2023-03-30 Added column within callHistory for Call Ending Timestamp
# The Call Ending Timestamp provides an "at-a-glance" review of call lengths during analysis and review
# Additional details published within "Maximizing iOS Call Log Timestamps and Call Duration Effectiveness: Will You Answer the Call?" at https://sqlmcgee.wordpress.com/2022/11/30/maximizing-ios-call-log-timestamps-and-call-duration-effectiveness-will-you-answer-the-call/

import sqlite3
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_callHistory(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
    
        if file_found.endswith('.storedata'):
            break
    
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select
    datetime(ZDATE+978307200,'unixepoch'),
    case
        when ((datetime(ZDATE+978307200,'unixepoch')) = (datetime(((ZDATE) + (ZDURATION))+978307200,'unixepoch'))) then 'No Call Duration'
        else (datetime(((ZDATE) + (ZDURATION))+978307200,'unixepoch'))
    end, 
    ZNAME,
    ZADDRESS,
    case ZORIGINATED
        when 0 then 'Incoming'
        when 1 then 'Outgoing'
    end,  
    case ZANSWERED
        when 0 then 'No'
        when 1 then 'Yes'
    end,
    strftime('%H:%M:%S',ZDURATION, 'unixepoch'),
    case ZCALLTYPE
        when 0 then 'Third-Party App'
        when 1 then 'Phone'
        when 8 then 'FaceTime Video'
        when 16 then 'FaceTime Audio'
        else ZCALLTYPE
    end,
    ZSERVICE_PROVIDER,
    upper(ZISO_COUNTRY_CODE),
    ZLOCATION
    from ZCALLRECORD
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    
    if usageentries > 0:
        
        for row in all_rows:
            an = str(row[3])
            an = an.replace("b'", "")
            an = an.replace("'", "")
            data_list.append((row[0], row[1], row[2], an, row[4], row[5], row[6], row[7], row[8], row[9], row[10]))

        report = ArtifactHtmlReport('Call History')
        report.start_artifact_report(report_folder, 'Call History')
        report.add_script()
        data_headers = ('Starting Timestamp', 'Ending Timestamp', 'Name', 'Phone Number', 'Call Direction', 'Answered', 'Call Duration', 'Call Type', 'Service Provider', 'ISO Country Code', 'Location')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Call History'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Call History'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Call History data available')

    db.close()
    return

__artifacts__ = {
    "callhistory": (
        "Call History",
        ('**/CallHistory.storedata*'),
        get_callHistory)
}
