from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly


def get_callHistory(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT 
    Z_PK as "CALL ID",
    ZADDRESS AS "ADDRESS", 
    ZANSWERED AS "WAS ANSWERED", 
    ZCALLTYPE AS "CALL TYPE", 
    ZORIGINATED AS "ORIGINATED", 
    ZDURATION AS "DURATION (IN SECONDS)",
    ZISO_COUNTRY_CODE as "ISO COUNTY CODE",
    ZLOCATION AS "LOCATION", 
    ZSERVICE_PROVIDER AS "SERVICE PROVIDER",
    DATETIME(ZDATE+978307200,'UNIXEPOCH') AS "TIMESTAMP"
    FROM ZCALLRECORD  
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            an = str(row[1])
            an = an.replace("b'", "")
            an = an.replace("'", "")
            data_list.append((row[9], row[0], an, row[2], row[3], row[4], row[5], row[6], row[7], row[8]))

        report = ArtifactHtmlReport('Call Logs')
        report.start_artifact_report(report_folder, 'Call Logs')
        report.add_script()
        data_headers = ('Timestamp', 'Call ID', 'Address', 'Was Answered', 'Call Type', 'Originated', 'Duration in Secs', 'ISO Country Code', 'Location', 'Service Provider')
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
