__artifacts_v2__ = {
    "safariWebsearch": {
        "name": "Safari Browser - Search Terms",
        "description": "Search-engine queries extracted from Safari History.db (search?q= URLs)",
        "author": "",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Safari Browser",
        "notes": "",
        "paths": ('**/Safari/History.db*',),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | com.apple.mobilesafari | 95 rows",
            "dexter_ios18": "iOS 18.3.2 | 7 rows",
            "felix_ios17": "iOS 17.6.1 | 4 rows",
            "fsfull002_ios17": "iOS 17.1 | 11 rows",
            "hc_ios18_7": "iOS 18.7.8 | 7 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 26 rows",
            "iphone14plus_ios18": "iOS 18.0 | 12 rows",
            "otto_ios17": "iOS 17.5.1 | 33 rows",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records


@artifact_processor
def safariWebsearch(context):
    data_headers = (('Visit Time', 'datetime'), 'Search Term', 'URL', 'Visit Count', 'Title',
                    'iCloud Sync', 'Load Successful', 'Visit ID', 'Redirect Source',
                    'Redirect Destination')
    data_list = []

    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('History.db'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        datetime(history_visits.visit_time + 978307200, 'unixepoch'),
        history_items.url,
        history_items.visit_count,
        history_visits.title,
        CASE history_visits.origin WHEN 1 THEN 'iCloud Synced' WHEN 0 THEN 'Visited Local Device'
            ELSE history_visits.origin END,
        history_visits.load_successful,
        history_visits.id,
        history_visits.redirect_source,
        history_visits.redirect_destination
    FROM history_items, history_visits
    WHERE history_items.id = history_visits.history_item
        AND history_items.url LIKE '%search?q=%'
    '''
    for row in get_sqlite_db_records(source_path, query):
        url = row[1] or ''
        search = url.split('search?q=')[1].split('&')[0].replace('+', ' ') if 'search?q=' in url else ''
        data_list.append((row[0], search, row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                          row[8]))

    return data_headers, data_list, context.get_relative_path(source_path)
