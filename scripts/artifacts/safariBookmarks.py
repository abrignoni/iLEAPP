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
        "artifact_icon": "bookmark",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 11 rows",
            "dexter_ios18": "iOS 18.3.2 | 8 rows",
            "felix_ios17": "iOS 17.6.1 | 11 rows",
            "fsfull002_ios17": "iOS 17.1 | 9 rows",
            "hc_ios18_7": "iOS 18.7.8 | 9 rows",
            "iphone11_ios17": "iOS 17.3 | 14 rows",
            "iphone12_ios18": "iOS 18.7 | 11 rows",
            "iphone14plus_ios18": "iOS 18.0 | 10 rows",
            "otto_ios17": "iOS 17.5.1 | 9 rows",
        }
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
