__artifacts_v2__ = {
    "keyboardLexicon": {
        "name": "Keyboard Dynamic Lexicon",
        "description": "Extracts dynamic lexicon data from the keyboard",
        "author": "@your_username",
        "version": "1.0",
        "date": "2023-05-24",
        "requirements": "none",
        "category": "User Activity",
        "notes": "",
        "paths": ('*/mobile/Library/Keyboard/*-dynamic.lm/dynamic-lexicon.dat',),
        "output_types": ["html", "tsv", "lava", "timeline"]
    },
    "keyboardAppUsage": {
        "name": "Keyboard Application Usage",
        "description": "Extracts keyboard application usage data",
        "author": "@your_username",
        "version": "1.0",
        "date": "2023-05-24",
        "requirements": "none",
        "category": "User Activity",
        "notes": "",
        "paths": ('*/mobile/Library/Keyboard/app_usage_database.plist',),
        "output_types": ["html", "tsv", "lava", "timeline"]
    },
    "keyboardUsageStats": {
        "name": "Keyboard Usage Stats",
        "description": "Extracts keyboard usage statistics",
        "author": "@your_username",
        "version": "1.0",
        "date": "2023-05-24",
        "requirements": "none",
        "category": "User Activity",
        "notes": "",
        "paths": ('*/mobile/Library/Keyboard/user_model_database.sqlite*',),
        "output_types": ["html", "tsv", "lava", "timeline"]
    }
}

import plistlib
import sqlite3
import string
from os.path import dirname

from scripts.ilapfuncs import logfunc, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone, artifact_processor, convert_plist_date_to_timezone_offset

@artifact_processor
def keyboardLexicon(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    
    for file_found in files_found:
        if file_found.endswith('dynamic-lexicon.dat'):
            strings_list = []
            with open(file_found, 'rb') as dat_file:
                dat_content = dat_file.read()
                dat_content_decoded = str(dat_content, 'utf-8', 'ignore')
                found_str = ''
                for char in dat_content_decoded:
                    if char in string.printable:
                        found_str += char
                    else:
                        if found_str and len(found_str) > 2 and found_str != 'DynamicDictionary-9':
                            strings_list.append(found_str)
                        found_str = ''
        
        location_file_found = file_found.split("Keyboard/", 1)[1] if "Keyboard/" in file_found else file_found.split("Keyboard\\", 1)[1]
        data_list.append((','.join(strings_list), location_file_found))
    
    data_headers = ('Found Strings', 'File Location')
    return data_headers, data_list, dirname(files_found[0]).split('Keyboard', 1)[0] + 'Keyboard'

@artifact_processor
def keyboardAppUsage(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    
    for file_found in files_found:
        if file_found.endswith('app_usage_database.plist'):
            with open(file_found, "rb") as plist_file:
                plist_content = plistlib.load(plist_file)
                for app in plist_content:
                    for entry in plist_content[app]:
                        start_date = convert_plist_date_to_timezone_offset(entry['startDate'], timezone_offset)
                        data_list.append((start_date, app, entry['appTime'], ', '.join(map(str, entry['keyboardTimes']))))
    
    data_headers = (('Date', 'datetime'), 'Application Name', 'Application Time Used in Seconds', 'Keyboard Times Used in Seconds')
    return data_headers, data_list, files_found[0]

@artifact_processor
def keyboardUsageStats(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    
    for file_found in files_found:
        if file_found.endswith('user_model_database.sqlite'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            datetime(creation_date,'unixepoch'),
            datetime(last_update_date,'unixepoch'),
            key,
            value
            FROM usermodeldurablerecords
            ''')
            
            for row in cursor.fetchall():
                create_ts = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]), timezone_offset)
                update_ts = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[1]), timezone_offset)
                data_list.append((create_ts, update_ts, row[2], row[3], file_found))
    
    data_headers = (('Creation Date', 'datetime'), ('Last Update Date', 'datetime'), 'Key', 'Data Value', 'Source File')
    return data_headers, data_list, 'See source paths in data'
