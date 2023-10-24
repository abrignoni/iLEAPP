from os.path import dirname
from os.path import basename

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, does_column_exist_in_db, convert_ts_human_to_utc, convert_utc_human_to_timezone


def get_reminders(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    
    slash = '\\' if is_platform_windows() else '/'
    
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.sqlite'):
            db = open_sqlite_db_readonly(file_found)
            answer = does_column_exist_in_db(db, 'ZREMCDOBJECT', 'ZLASTMODIFIEDDATE')
        
            if answer:
                #db = open_sqlite_db_readonly(file_found)
                cursor = db.cursor()
                cursor.execute('''
                    SELECT
                    DATETIME(ZCREATIONDATE+978307200,'UNIXEPOCH'),
                    DATETIME(ZLASTMODIFIEDDATE+978307200,'UNIXEPOCH'),
                    ZNOTES,
                    ZTITLE1
                    FROM ZREMCDOBJECT
                    WHERE ZTITLE1 <> ''
                    ''')
    
                all_rows = cursor.fetchall()
                sqlite_file = file_found
                
                if len(all_rows) > 0:
                    location_file_found = sqlite_file.split('Stores'+slash, 1)[1]
                    for row in all_rows:
                        createdate = convert_ts_human_to_utc(row[0])
                        createdate = convert_utc_human_to_timezone(createdate,timezone_offset)
                        
                        moddate = convert_ts_human_to_utc(row[1])
                        moddate = convert_utc_human_to_timezone(moddate,timezone)
                        data_list.append((createdate, row[3], row[2], moddate, location_file_found))
                        
                    dir_file_found = dirname(sqlite_file).split('Stores', 1)[0] + 'Stores'
                    
                    report = ArtifactHtmlReport('Reminders')
                    report.start_artifact_report(report_folder, f'Reminders - {location_file_found}')
                    report.add_script()
                    data_headers = ('Creation Date', 'Title', 'Note to Reminder', 'Last Modified', 'File Location')
                    report.write_artifact_data_table(data_headers, data_list, dir_file_found)
                    report.end_artifact_report()
                    
                    tsvname = 'Reminders'
                    tsv(report_folder, data_headers, data_list, tsvname)
                    
                    tlactivity = 'Reminders'
                    timeline(report_folder, tlactivity, data_list, data_headers)
                else:
                    logfunc(f'No Reminders available on {basename(file_found)}')
                    
                
    
    db.close()
    return

__artifacts__ = {
    "reminders": (
        "Reminders",
        ('**/Reminders/Container_v1/Stores/*.sqlite*'),
        get_reminders)
}
