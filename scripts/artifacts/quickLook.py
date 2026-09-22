__artifacts_v2__ = {
    "quickLook": {
        "name": "iCloud Quick Look",
        "description": "Entries from the Quick Look cloudthumbnails.db cache: paths of iCloud files with last-hit dates. A cache entry does not establish that the file was viewed.",
        "author": "@abrignoni",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "iCloud Quick Look",
        "notes": "On iOS 12 test images the database sits under Library/Application Support/Quick Look/; "
                 "on iOS 15-26 test images it sits under Library/Caches/com.apple.QuickLook.thumbnailcache/ "
                 "with the main file a 4 KB shell whose thumbnails table and rows live entirely in the "
                 "-wal sidecar, so the -wal and -shm files must be collected with the database.",
        "paths": ('*/Quick Look/cloudthumbnails.db*',
                  '*/Library/Caches/com.apple.QuickLook.thumbnailcache/cloudthumbnails.db*'),
        "output_types": "standard",
        "artifact_icon": "eye",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1 row",
            "hickman_ios13": "iOS 13.3.1 | 2 rows",
            "abe_ios16": "iOS 16.5 | 4 rows",
            "felix23_ios16": "iOS 16.5 | 5 rows",
            "otto_ios17": "iOS 17.5.1 | 4 rows",
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        }
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
    sources = []

    query = '''
    SELECT
        datetime(last_hit_date, 'unixepoch'),
        last_seen_path,
        size
    FROM thumbnails
    '''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('cloudthumbnails.db'):
            continue
        for row in get_sqlite_db_records(file_found, query):
            data_list.append((row[0], row[1], row[2]))
        sources.append(context.get_relative_path(file_found))

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
