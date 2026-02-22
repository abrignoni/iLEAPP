from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_safariWebsearch(files_found, report_folder, seeker, wrap_text, timezone_offset):
    file_found = str(files_found[0])
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('History.db'):
            break

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()

    cursor.execute("""
    select
    datetime(history_visits.visit_time+978307200,'unixepoch') ,
    history_items.url,
    history_items.visit_count,
    history_visits.title,
    case history_visits.origin
    when 1 then "icloud synced"
    when 0 then "visited local device"
    else history_visits.origin
    end "icloud sync",
    history_visits.load_successful,
    history_visits.id,
    history_visits.redirect_source,
    history_visits.redirect_destination
    from history_items, history_visits
    where history_items.id = history_visits.history_item
    and history_items.url like '%search?q=%'
    """)

    all_rows = cursor.fetchall()
    data_list = []
    for row in all_rows:
        search = row[1].split('search?q=')[1].split('&')[0]
        search = search.replace('+', ' ')
        data_list.append((row[0], search, row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))

    db.close()

    data_headers = ('Visit Time', 'Search Term', 'URL', 'Visit Count', 'Title',
                    'iCloud Sync', 'Load Successful', 'Visit ID',
                    'Redirect Source', 'Redirect Destination')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_safariWebsearch": {
        "name": "Safari Web Search",
        "description": "",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Safari Browser",
        "notes": "",
        "paths": ('**/Safari/History.db*',),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
