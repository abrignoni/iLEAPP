__artifacts_v2__ = {
    "safariBookmarks": {
        "name": "Safari Browser - Bookmarks",
        "description": "Safari bookmarks",
        "author": "",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Safari Browser",
        "notes": "",
        "paths": ('**/Safari/Bookmarks.db*',),
        "output_types": "standard",
        "artifact_icon": "bookmark"
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records


@artifact_processor
def safariBookmarks(context):
    data_headers = ('Title', 'URL', 'Hidden')
    data_list = []

    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('Bookmarks.db'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

    for row in get_sqlite_db_records(source_path, 'SELECT title, url, hidden FROM bookmarks'):
        data_list.append(tuple(row))

    return data_headers, data_list, context.get_relative_path(source_path)
