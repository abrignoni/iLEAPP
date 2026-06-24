__artifacts_v2__ = {
    "reminders": {
        "name": "Reminders",
        "description": "iOS Reminders with creation and last-modified timestamps",
        "author": "",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Reminders",
        "notes": "",
        "paths": ('**/Reminders/Container_v1/Stores/*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "bell"
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, does_column_exist_in_db


@artifact_processor
def reminders(context):
    data_headers = (
        ('Creation Date', 'datetime'),
        'Title',
        'Note to Reminder',
        ('Last Modified', 'datetime'),
        'File Location')
    data_list = []
    sources = []

    query = '''
    SELECT
        DATETIME(ZCREATIONDATE + 978307200, 'UNIXEPOCH'),
        DATETIME(ZLASTMODIFIEDDATE + 978307200, 'UNIXEPOCH'),
        ZNOTES,
        ZTITLE1
    FROM ZREMCDOBJECT
    WHERE ZTITLE1 <> ''
    '''

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('.sqlite'):
            continue
        if not does_column_exist_in_db(file_found, 'ZREMCDOBJECT', 'ZLASTMODIFIEDDATE'):
            continue

        rel_path = context.get_relative_path(file_found)
        rows = get_sqlite_db_records(file_found, query)
        if not rows:
            continue
        for row in rows:
            data_list.append((row[0], row[3], row[2], row[1], rel_path))
        sources.append(rel_path)

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
