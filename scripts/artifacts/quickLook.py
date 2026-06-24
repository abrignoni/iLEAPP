__artifacts_v2__ = {
    "quickLook": {
        "name": "iCloud Quick Look",
        "description": "Listing of iCloud files accessed by the Quick Look function",
        "author": "",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "iCloud Quick Look",
        "notes": "Check -wal files for possible data remnants if the DB is missing.",
        "paths": ('*/Quick Look/cloudthumbnails.db*',),
        "output_types": "standard",
        "artifact_icon": "eye"
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records


@artifact_processor
def quickLook(context):
    data_headers = (
        ('Last Hit Date', 'datetime'),
        'Last Seen Path',
        'Size')
    data_list = []
    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('cloudthumbnails.db'):
            source_path = file_found
            break

    if not source_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        datetime(last_hit_date, 'unixepoch'),
        last_seen_path,
        size
    FROM thumbnails
    '''
    for row in get_sqlite_db_records(source_path, query):
        data_list.append((row[0], row[1], row[2]))

    return data_headers, data_list, context.get_relative_path(source_path)
