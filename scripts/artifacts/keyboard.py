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
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "User Activity",
        "notes": "Field units and semantics for app_usage_database.plist are not "
                 "documented; values are reported as stored.",
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
    },
    "keyboardVulgarWordUsage": {
        "name": "Keyboard Vulgar Word Usage",
        "description": "Words and usage values stored in VulgarWordUsage.db",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-28",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "User Activity",
        "notes": "The last-use timestamp is interpreted as Apple Cocoa epoch; "
                 "no populated sample was available to verify.",
        "paths": ("*/mobile/Library/Keyboard/VulgarWordUsage.db*",),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "message-2",
        "sample_data": {
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
        },
    },
    "keyboardAutocorrectionRejections": {
        "name": "Keyboard Autocorrection Rejections",
        "description": "Typed text and the corresponding autocorrection held in the "
                       "rejections table of AutocorrectionRejections.db, with the "
                       "stored rejection counts and timestamps",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-13",
        "last_update_date": "2026-08-13",
        "requirements": "none",
        "category": "User Activity",
        "notes": "Column meanings are quoted from the CREATE TABLE comments stored in "
                 "the database itself: 'typed' is 'originally typed by the user', "
                 "'correction' is the 'autocorrection performed or rejected', and "
                 "'performed_count' is 'hard acceptances'. A row therefore does not by "
                 "itself establish that the correction was rejected rather than "
                 "applied. The same schema documents both timestamp columns as "
                 "'seconds since unix epoch'; each defaults to -1e10, and rows still "
                 "holding that default are reported as an empty cell rather than a "
                 "date. The schema does not define how a soft rejection differs from a "
                 "hard one, so those counts are reported as stored. Across the 11 "
                 "tested images every populated row carried hard_rejections=1, "
                 "soft_rejections=0, performed_count=0 and journaled NULL, with "
                 "last_soft_rejection at its default, so the soft-rejection, "
                 "acceptance and journaled paths are present in the schema but "
                 "unexercised by the tested data. The file was present on all 11 "
                 "tested filesystem extractions of iOS 17.1 and later and absent from "
                 "all 10 tested filesystem extractions of iOS 16.5.1 and earlier; that "
                 "is an observation about these images, not a statement about when the "
                 "file was introduced. The schema text was byte-identical across all "
                 "11, at properties.version 2.",
        "paths": ("*/mobile/Library/Keyboard/AutocorrectionRejections.db*",),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "keyboard",
        "sample_data": {
            "otto_ios17": "iOS 17.5.1 | 5 rows",
            "iphone12_ios18": "iOS 18.7 | 12 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 3 rows",
            "hc_ios18_7": "iOS 18.7.8 | 2 rows",
            "hc_ios26": "iOS 26.5.2 | 2 rows",
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows (file not present)",
            "hickman_ios13": "iOS 13.3.1 | 0 rows (file not present)",
            "hickman_ios14": "iOS 14.3 | 0 rows (file not present)",
            "hickman_ios15": "iOS 15 | 0 rows (file not present)",
            "jess_ios15": "iOS 15.0.2 | 0 rows (file not present)",
            "magnet_ios16": "iOS 16.1.1 | 0 rows (file not present)",
            "belkactf6": "iOS 16.3 | 0 rows (file not present)",
            "abe_ios16": "iOS 16.5 | 0 rows (file not present)",
            "felix23_ios16": "iOS 16.5 | 0 rows (file not present)",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows (file not present)",
        },
    },
    "keyboardInlineCompletionRejections": {
        "name": "Keyboard Inline Completion Rejections",
        "description": "Typed text and the corresponding inline completion held in the "
                       "inline_completion_rejections table of "
                       "AutocorrectionRejections.db, with the stored rejection counts "
                       "and timestamps",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-13",
        "last_update_date": "2026-08-13",
        "requirements": "none",
        "category": "User Activity",
        "notes": "A second table in the same database as the Keyboard Autocorrection "
                 "Rejections artifact, carrying the same columns. Its stored CREATE "
                 "TABLE comments document 'typed' as 'originally typed by the user' "
                 "and 'correction' as the 'completion performed or rejected', so this "
                 "table describes completions rather than autocorrections and a row "
                 "does not by itself establish that the completion was rejected. "
                 "Unlike the rejections table it carries no comment on "
                 "'performed_count', and its unique index covers 'correction' alone "
                 "rather than the typed/correction pair. Timestamps are documented in "
                 "the schema as 'seconds since unix epoch' and default to -1e10; rows "
                 "still holding that default are reported as an empty cell. The "
                 "soft/hard distinction is not defined in the schema, so those counts "
                 "are reported as stored. Populated on 3 of the 11 tested images, one "
                 "row each, every one carrying hard_rejections=1, soft_rejections=0, "
                 "performed_count=0 and journaled NULL. The table is created with IF "
                 "NOT EXISTS, so it is guarded at read time in case an earlier "
                 "properties.version predates it.",
        "paths": ("*/mobile/Library/Keyboard/AutocorrectionRejections.db*",),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "keyboard",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 1 row",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows (file not present)",
            "hickman_ios13": "iOS 13.3.1 | 0 rows (file not present)",
            "hickman_ios14": "iOS 14.3 | 0 rows (file not present)",
            "hickman_ios15": "iOS 15 | 0 rows (file not present)",
            "jess_ios15": "iOS 15.0.2 | 0 rows (file not present)",
            "magnet_ios16": "iOS 16.1.1 | 0 rows (file not present)",
            "belkactf6": "iOS 16.3 | 0 rows (file not present)",
            "abe_ios16": "iOS 16.5 | 0 rows (file not present)",
            "felix23_ios16": "iOS 16.5 | 0 rows (file not present)",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows (file not present)",
        },
    },
}

import plistlib
import string
from os.path import dirname
from datetime import datetime

from scripts.ilapfuncs import (
    open_sqlite_db_readonly, convert_ts_human_to_utc, artifact_processor,
    does_table_exist_in_db, get_sqlite_db_records,
)

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
                                                 
    data_headers = (('Date', 'datetime'), 'Application Name', 'appTime (as stored)', 'keyboardTimes (as stored)')
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


@artifact_processor
def keyboardVulgarWordUsage(context):
    data_headers = (
        ("Last Used", "datetime"), "Record ID", "Application", "Recipient", "Vulgar Word",
        "Word Reading", "Usage Count", "Journaled",
    )
    data_list = []
    source_path = next(
        (str(path) for path in context.get_files_found()
         if str(path).endswith("VulgarWordUsage.db")),
        "",
    )
    if not source_path or not does_table_exist_in_db(source_path, "vword_usage"):
        return data_headers, data_list, ""

    query = """
        SELECT CASE WHEN last_use_timestamp > 0
                    THEN datetime(last_use_timestamp + 978307200, 'unixepoch') END,
               ROWID, app, recipient, vword, word_reading, usage_count,
               journaled
        FROM vword_usage
        ORDER BY last_use_timestamp
    """
    data_list.extend(tuple(row) for row in get_sqlite_db_records(source_path, query))
    return data_headers, data_list, context.get_relative_path(source_path)


# Both tables in AutocorrectionRejections.db carry identical columns, so one reader
# serves both artifacts. Column meanings come from the CREATE TABLE comments stored
# in the database; see the notes in each artifact block.
_REJECTION_HEADERS = (
    ("Last Hard Rejection", "datetime"),
    ("Last Soft Rejection", "datetime"),
    "Record ID",
    "Typed Text",
    "Correction",
    "Hard Rejections",
    "Soft Rejections",
    "Performed Count",
    "Journaled (as stored)",
)


def _autocorrection_rejection_rows(context, table_name):
    """Read one rejection table, guarding the sentinel timestamp default of -1e10."""
    data_list = []
    source_path = next(
        (str(path) for path in context.get_files_found()
         if str(path).endswith("AutocorrectionRejections.db")),
        "",
    )
    if not source_path or not does_table_exist_in_db(source_path, table_name):
        return _REJECTION_HEADERS, data_list, ""

    query = f"""
        SELECT CASE WHEN last_hard_rejection > 0
                    THEN datetime(last_hard_rejection, 'unixepoch') END,
               CASE WHEN last_soft_rejection > 0
                    THEN datetime(last_soft_rejection, 'unixepoch') END,
               ROWID, typed, correction,
               hard_rejections, soft_rejections, performed_count, journaled
        FROM {table_name}
        ORDER BY MAX(last_hard_rejection, last_soft_rejection)
    """
    data_list.extend(tuple(row) for row in get_sqlite_db_records(source_path, query))
    return _REJECTION_HEADERS, data_list, context.get_relative_path(source_path)


@artifact_processor
def keyboardAutocorrectionRejections(context):
    return _autocorrection_rejection_rows(context, "rejections")


@artifact_processor
def keyboardInlineCompletionRejections(context):
    return _autocorrection_rejection_rows(context, "inline_completion_rejections")
