__artifacts_v2__ = {
    "safariHistory": {
        "name": "Safari Browser - History",
        "description": "Safari web history visits",
        "author": "@KevinPagano3",
        "creation_date": "2023-02-14",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Safari Browser",
        "notes": "",
        "paths": ('**/Safari/History.db*',),
        "output_types": "standard",
        "artifact_icon": "globe"
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records


@artifact_processor
def safariHistory(context):
    data_headers = (('Visit Timestamp', 'datetime'), 'Title', 'URL', 'Visit Count',
                    'Redirect Source', 'Redirect Destination', 'Visit ID', 'Origin')
    data_list = []

    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('History.db'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

    # Map visit id -> url so redirect source/destination ids can be resolved to URLs
    id_url = {}
    for row in get_sqlite_db_records(source_path, '''
        SELECT history_visits.id, history_items.url
        FROM history_visits
        LEFT JOIN history_items ON history_items.id = history_visits.history_item'''):
        id_url[str(row[0])] = row[1]

    query = '''
    SELECT
        datetime(history_visits.visit_time + 978307200, 'unixepoch'),
        history_visits.title,
        history_items.url,
        history_items.visit_count,
        history_visits.redirect_source,
        history_visits.redirect_destination,
        history_visits.id,
        CASE history_visits.origin WHEN 0 THEN 'Local Device' WHEN 1 THEN 'iCloud Synced Device' END
    FROM history_visits
    LEFT JOIN history_items ON history_visits.history_item = history_items.id
    '''
    for row in get_sqlite_db_records(source_path, query):
        redirect_source = id_url.get(str(row[4]), '') if row[4] is not None else ''
        redirect_destination = id_url.get(str(row[5]), '') if row[5] is not None else ''
        data_list.append((row[0], row[1], row[2], row[3], redirect_source, redirect_destination,
                          row[6], row[7]))

    return data_headers, data_list, context.get_relative_path(source_path)
