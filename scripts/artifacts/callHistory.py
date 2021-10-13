import sqlite3
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_callHistory(files_found, report_folder, seeker):
    
    for file_found in files_found:
        file_found = str(file_found)
    
        if file_found.endswith('.storedata'):
            break
    
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select
    datetime(ZDATE+978307200,'unixepoch'),
    ZADDRESS,
    ZNAME,
    case ZANSWERED
        when 0 then 'No'
        when 1 then 'Yes'
    end,
    case ZCALLTYPE
        when 0 then 'Third-Party App'
        when 1 then 'Phone'
        when 8 then 'FaceTime Video'
        when 16 then 'FaceTime Audio'
        else ZCALLTYPE
    end, 
    case ZORIGINATED
        when 0 then 'Incoming'
        when 1 then 'Outgoing'
    end,  
    strftime('%H:%M:%S',ZDURATION, 'unixepoch'),
    upper(ZISO_COUNTRY_CODE),
    ZLOCATION, 
    ZSERVICE_PROVIDER
    from ZCALLRECORD
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    
    if usageentries > 0:
        
        for row in all_rows:
            an = str(row[1])
            an = an.replace("b'", "")
            an = an.replace("'", "")
            data_list.append((row[0], an, row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))

        report = ArtifactHtmlReport('Call History')
        report.start_artifact_report(report_folder, 'Call History')
        report.add_script()
        data_headers = ('Timestamp', 'Phone Number', 'Name', 'Answered', 'Call Type', 'Call Direction', 'Call Duration', 'ISO Country Code', 'Location', 'Service Provider')
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
