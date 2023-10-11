import os
import sqlite3
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly

def get_browser_name(file_name):

    if 'brave' in file_name.lower():
        return 'Brave'
    elif 'microsoft' in file_name.lower():
        return 'Edge'
    elif 'opera' in file_name.lower():
        return 'Opera'
    elif 'chrome' in file_name.lower():
        return 'Chrome'
    else:
        return 'Unknown'

def get_chromeNetworkActionPredictor(files_found, report_folder, seeker, wrap_text, timezone_offset):

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('Network Action Predictor'):
            continue # Skip all other files
            
        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        select
        user_text,
        url,
        number_of_hits,
        number_of_misses
        from network_action_predictor
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'{browser_name} - Network Action Predictor')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{browser_name} - Network Action Predictor.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('User Text','URL','Number of Hits','Number of Misses') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'{browser_name} - Network Action Predictor'
            tsv(report_folder, data_headers, data_list, tsvname)

        else:
            logfunc(f'No {browser_name} - Network Action Predictor data available')
        
        db.close()

__artifacts__ = {
        "ChromeNetworkActionPredictor": (
                "Chromium",
                ('*/Chrome/Default/Network Action Predictor*','*/app_sbrowser/Default/Network Action Predictor*', '*/app_opera/Network Action Predicator*'),
                get_chromeNetworkActionPredictor)
}