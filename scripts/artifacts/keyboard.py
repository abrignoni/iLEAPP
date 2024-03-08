import plistlib
import sqlite3
import string
from os.path import dirname

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_keyboard(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list_usage = []
    data_list_lex = []
    data_list_stats = []
    tsv_data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        strings_list = []
        
        # Keyboard Lexicon
        if file_found.endswith('dynamic-lexicon.dat'):
            with open(file_found, 'rb') as dat_file:
                dat_content = dat_file.read()
                dat_content_decoded = str(dat_content, 'utf-8', 'ignore')
                found_str = ''
                for char in dat_content_decoded:
                    if char in string.printable:
                        found_str += char
                    else:
                        if found_str:
                            if len(found_str) > 2:  # reduce noise
                                if found_str != 'DynamicDictionary-9':
                                    strings_list.append(found_str)
                            found_str = ''

            if file_found.find("Keyboard/") >= 0:
                slash = '/'
            else:
                slash = '\\'
            location_file_found = file_found.split(f"Keyboard{slash}", 1)[1]
            data_list_lex.append(('<br>'.join(strings_list), location_file_found))
            tsv_data_list.append((','.join(strings_list), location_file_found))

            dir_file_found = dirname(file_found).split('Keyboard', 1)[0] + 'Keyboard'
        
        # Keyboard App Usage
        if file_found.endswith('app_usage_database.plist'):
            with open(file_found, "rb") as plist_file:
                plist_content = plistlib.load(plist_file)
                for app in plist_content:
                    for entry in plist_content[app]:
                        data_list_usage.append((entry['startDate'], app, entry['appTime'], ', '.join(map(str, entry['keyboardTimes']))))
                        
        # Keyboard Usage Stats
        if file_found.endswith('user_model_database.sqlite'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            select
            datetime(creation_date,'unixepoch'),
            datetime(last_update_date,'unixepoch'),
            key,
            value
            from usermodeldurablerecords
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
        
            if usageentries > 0:
                for row in all_rows:
                    create_ts = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),timezone_offset)
                    update_ts = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[1]),timezone_offset)
                    
                    data_list_stats.append((create_ts,update_ts,row[2],row[3],file_found))
                    
        else:
            continue
    
    # Keyboard Lexicon Report
    if data_list_lex:
        report = ArtifactHtmlReport('Keyboard Dynamic Lexicon')
        report.start_artifact_report(report_folder, 'Keyboard Dynamic Lexicon')
        report.add_script()
        data_headers = ('Found Strings', 'File Location')
        report.write_artifact_data_table(data_headers, data_list_lex, dir_file_found, html_no_escape=['Found Strings'])
        report.end_artifact_report()

        tsvname = 'Keyboard Dynamic Lexicon'
        tsv(report_folder, data_headers, tsv_data_list, tsvname)

        tlactivity = 'Keyboard Dynamic Lexicon'
        timeline(report_folder, tlactivity, tsv_data_list, data_headers)

    else:
        logfunc('No Keyboard Dynamic Lexicon data found')

    # Keyboard App Usage Report
    if data_list_usage:
        report = ArtifactHtmlReport('Keyboard Application Usage')
        report.start_artifact_report(report_folder, 'Keyboard Application Usage')
        report.add_script()
        data_headers = ('Date', 'Application Name', 'Application Time Used in Seconds', 'Keyboard Times Used in Seconds')
        report.write_artifact_data_table(data_headers, data_list_usage, file_found)
        report.end_artifact_report()

        tsvname = 'Keyboard Application Usage'
        tsv(report_folder, data_headers, data_list_usage, tsvname)

        tlactivity = 'Keyboard Application Usage'
        timeline(report_folder, tlactivity, data_list_usage, data_headers)

    else:
        logfunc('No Keyboard Application Usage found')
        
    # Keyboard Usage Stats Report
    if data_list_stats:
        report = ArtifactHtmlReport('Keyboard Usage Stats')
        report.start_artifact_report(report_folder, 'Keyboard Usage Stats')
        report.add_script()
        data_headers = ('Creation Date', 'Last Update Date', 'Key', 'Value', 'Source File')
        report.write_artifact_data_table(data_headers, data_list_stats, 'See source paths below')
        report.end_artifact_report()

        tsvname = 'Keyboard Usage Stats'
        tsv(report_folder, data_headers, data_list_stats, tsvname)

        tlactivity = 'Keyboard Usage Stats'
        timeline(report_folder, tlactivity, data_list_stats, data_headers)

    else:
        logfunc('No Keyboard Application Usage found')

__artifacts__ = {
    "keyboard": (
        "Keyboard",
        ('*/mobile/Library/Keyboard/*-dynamic.lm/dynamic-lexicon.dat','*/mobile/Library/Keyboard/app_usage_database.plist','*/mobile/Library/Keyboard/user_model_database.sqlite*'),
        get_keyboard)
}