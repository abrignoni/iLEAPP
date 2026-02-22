from scripts.ilapfuncs import logfunc, artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_quickLook(files_found, report_folder, seeker, wrap_text, timezone_offset):
    file_found = str(files_found[0])
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('cloudthumbnails.db'):
            break

    data_list = []
    if file_found.endswith('cloudthumbnails.db'):
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime("last_hit_date", 'unixepoch') as lasthitdate,
        last_seen_path,
        size
        from thumbnails
        ''')

        all_rows = cursor.fetchall()
        for row in all_rows:
            data_list.append((row[0], row[1], row[2]))

        db.close()
    else:
        logfunc('No Quicklook DB file found. Check -wal files for possible data remnants.')

    data_headers = ('Last Hit Date', 'Last Seen Path', 'Size')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_quickLook": {
        "name": "iCloud Quick Look",
        "description": "Listing of iCloud files accessed by the Quick Look function.",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "iCloud Quick Look",
        "notes": "",
        "paths": ('*/Quick Look/cloudthumbnails.db*',),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
