__artifacts_v2__ = {
    "reminders": {
        "name": "Reminders",
        "description": "iOS Reminders with creation, modification, due and completion timestamps",
        "author": "@any333",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "Reminders",
        "notes": "Two store generations are read. iOS 16 and later test images keep reminders in a "
                 "ZREMCDREMINDER table; earlier images keep them as REMCDReminder rows in the "
                 "single-table ZREMCDOBJECT, with the entity code resolved per file from "
                 "Z_PRIMARYKEY because the number shifts between releases (23, 24 and 28 on the "
                 "iOS 13, 14 and 15 test images). On iOS 17 and later the store directory moved "
                 "from Library/Reminders/Container_v1 to the Reminders app-group container. On the "
                 "older generation both ZTITLE and ZTITLE1 columns exist and no populated store of "
                 "that generation was available in the local corpus, so the title is read from "
                 "whichever column is set (unexercised path). Completed, Flagged and Marked for "
                 "Deletion are integer flags reported as stored; rows marked for deletion are "
                 "included.",
        "paths": ('*/Container_v1/Stores/*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "belkactf6": "iOS 16.3 | 14 rows (run against the decrypted filesystem copy)",
            "abe_ios16": "iOS 16.5 | 2 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 6 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 3 rows",
            "iphone14plus_ios18": "iOS 18.0 | 37 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        }
    }
}

import os

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, \
    does_table_exist_in_db, does_column_exist_in_db

_COLUMNS = '''
        DATETIME(ZCREATIONDATE + 978307200, 'UNIXEPOCH'),
        DATETIME(ZLASTMODIFIEDDATE + 978307200, 'UNIXEPOCH'),
        DATETIME(ZDUEDATE + 978307200, 'UNIXEPOCH'),
        DATETIME(ZCOMPLETIONDATE + 978307200, 'UNIXEPOCH'),
        {title},
        ZNOTES,
        ZCOMPLETED,
        ZFLAGGED,
        ZMARKEDFORDELETION
'''


def _reminder_entity(file_found):
    '''Z_ENT code for the REMCDReminder entity, resolved from the file's own
    Z_PRIMARYKEY table because the numbering shifts between releases.'''
    for row in get_sqlite_db_records(
            file_found,
            "SELECT Z_ENT FROM Z_PRIMARYKEY WHERE Z_NAME = 'REMCDReminder'"):
        return row[0]
    return None


@artifact_processor
def reminders(context):
    data_headers = (
        ('Creation Date', 'datetime'),
        ('Last Modified', 'datetime'),
        ('Due Date', 'datetime'),
        ('Completion Date', 'datetime'),
        'Title',
        'Notes',
        'Completed',
        'Flagged',
        'Marked for Deletion',
        'File Location')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('.sqlite'):
            continue
        if os.path.basename(file_found).startswith('._'):
            continue    # AppleDouble sidecar, not a database

        if does_table_exist_in_db(file_found, 'ZREMCDREMINDER'):
            query = f'SELECT {_COLUMNS.format(title="ZTITLE")} FROM ZREMCDREMINDER'
        elif does_table_exist_in_db(file_found, 'ZREMCDOBJECT'):
            entity = _reminder_entity(file_found)
            if entity is None:
                continue
            title = 'COALESCE(ZTITLE1, ZTITLE)' \
                if does_column_exist_in_db(file_found, 'ZREMCDOBJECT', 'ZTITLE1') else 'ZTITLE'
            query = (f'SELECT {_COLUMNS.format(title=title)} '
                     f'FROM ZREMCDOBJECT WHERE Z_ENT = {int(entity)}')
        else:
            continue

        rel_path = context.get_relative_path(file_found)
        rows_seen = False
        for row in get_sqlite_db_records(file_found, query):
            data_list.append(tuple(row) + (rel_path,))
            rows_seen = True
        if rows_seen:
            sources.append(rel_path)

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
