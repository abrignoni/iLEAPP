__artifacts_v2__ = {
    "safariWebsearch": {
        "name": "Safari Browser - Search Terms",
        "description": "Search-engine queries extracted from Safari History.db (search?q= URLs)",
        "author": "",
        "version": "2.0",
        "date": "2026-06-23",
        "requirements": "none",
        "category": "Safari Browser",
        "notes": "",
        "paths": ('**/Safari/History.db*',),
        "output_types": "standard",
        "artifact_icon": "search"
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
