__artifacts_v2__ = {
    "keyboardLexicon": {
        "name": "Keyboard Dynamic Lexicon",
        "description": "Extracts dynamic lexicon data from the keyboard",
        "author": "@any333",
        "creation_date": "2023-05-24",
        "last_update_date": "2026-07-22",
        "requirements": "none",
        "category": "User Activity",
        "notes": "",
        "paths": ('*/mobile/Library/Keyboard/*-dynamic.lm/dynamic-lexicon.dat',),
        "output_types": ["html","lava","tsv"],
        "artifact_icon": "vocabulary",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "otto_ios17": "iOS 17.5.1 | 1 row",
            "abe_ios16": "iOS 16.5 | 1 row",
            "felix23_ios16": "iOS 16.5 | 2 rows",
            "hickman_ios13": "iOS 13.3.1 | 1 row",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 1 row",
        }
    },
    "keyboardAppUsage": {
        "name": "Keyboard Application Usage",
        "description": "Extracts keyboard application usage data",
        "author": "@yany333",
        "creation_date": "2023-05-24",
        "last_update_date": "2023-05-24",
        "requirements": "none",
        "category": "User Activity",
        "notes": "",
        "paths": ('*/mobile/Library/Keyboard/app_usage_database.plist',),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "keyboard",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 112 rows",
            "felix23_ios16": "iOS 16.5 | 81 rows",
            "hickman_ios13": "iOS 13.3.1 | 475 rows",
            "hickman_ios14": "iOS 14.3 | 251 rows",
            "jess_ios15": "iOS 15.0.2 | 22 rows",
        }
    },
    "keyboardUsageStats": {
        "name": "Keyboard Usage Stats",
        "description": "Extracts keyboard usage statistics",
        "author": "@any333",
        "creation_date": "2023-05-24",
        "last_update_date": "2023-05-24",
        "requirements": "none",
        "category": "User Activity",
        "notes": "",
        "paths": ('*/mobile/Library/Keyboard/user_model_database.sqlite*',),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "chart-bar",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 4 rows",
            "felix_ios17": "iOS 17.6.1 | 5 rows",
            "fsfull002_ios17": "iOS 17.1 | 4 rows",
            "hc_ios18_7": "iOS 18.7.8 | 4 rows",
            "iphone11_ios17": "iOS 17.3 | 4 rows",
            "iphone12_ios18": "iOS 18.7 | 4 rows",
            "iphone14plus_ios18": "iOS 18.0 | 5 rows",
            "otto_ios17": "iOS 17.5.1 | 4 rows",
            "abe_ios16": "iOS 16.5 | 4 rows",
            "felix23_ios16": "iOS 16.5 | 5 rows",
            "hickman_ios13": "iOS 13.3.1 | 2 rows",
            "hickman_ios14": "iOS 14.3 | 4 rows",
            "jess_ios15": "iOS 15.0.2 | 3 rows",
            "magnet_ios16": "iOS 16.1.1 | 4 rows",
        }
    }
}

import plistlib
import string
from os.path import dirname
from datetime import datetime

from scripts.ilapfuncs import open_sqlite_db_readonly, convert_ts_human_to_utc, artifact_processor

@artifact_processor
def keyboardLexicon(context):
    data_list = []
    files_found = context.get_files_found()
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
def keyboardAppUsage(context):
    data_list = []
    files_found = context.get_files_found()
    for file_found in files_found:
        if file_found.endswith('app_usage_database.plist'):
            with open(file_found, "rb") as plist_file:
                plist_content = plistlib.load(plist_file)
                for app in plist_content:
                    for entry in plist_content[app]:
                        raw_date = str(entry.get('startDate', ''))
                        if raw_date.endswith('Z'):
                            raw_date = raw_date.replace('Z', '+00:00')
                        try:
                            dt_obj = datetime.fromisoformat(raw_date)
                            start_date = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            start_date = raw_date

                        data_list.append((start_date, app, entry['appTime'], ', '.join(map(str, entry['keyboardTimes']))))  
                                                 
    data_headers = (('Date', 'datetime'), 'Application Name', 'Application Time Used in Seconds', 'Keyboard Times Used in Seconds')
    return data_headers, data_list, files_found[0]

@artifact_processor
def keyboardUsageStats(context):
    data_list = []
    files_found = context.get_files_found()
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
                create_ts = convert_ts_human_to_utc(row[0])
                update_ts = convert_ts_human_to_utc(row[1])
                data_list.append((create_ts, update_ts, row[2], row[3], context.get_relative_path(file_found)))
    
    data_headers = (('Creation Date', 'datetime'), ('Last Update Date', 'datetime'), 'Key', 'Data Value', 'Source File')
    return data_headers, data_list, 'See source paths in data'
