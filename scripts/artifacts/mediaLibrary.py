__artifacts_v2__ = {
    "mediaLibrary": {
        "name": "Media Library",
        "description": "Media items (music, video, podcasts, e-books) from Medialibrary.sqlitedb",
        "author": "",
        "creation_date": "2023-11-21",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Media Library",
        "notes": "",
        "paths": ('**/Medialibrary.sqlitedb*',),
        "output_types": "standard",
        "artifact_icon": "music"
    },
    "mediaLibraryInfo": {
        "name": "Media Library - Database Properties",
        "description": "iCloud/account properties from the Medialibrary.sqlitedb _MLDATABASEPROPERTIES table",
        "author": "",
        "creation_date": "2023-11-21",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Media Library",
        "notes": "",
        "paths": ('**/Medialibrary.sqlitedb*',),
        "output_types": "standard",
        "artifact_icon": "info-circle"
    }
}

import sqlite3

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, logfunc

_MEDIA_KIND = {0: 'E-book', 1: 'Audio', 2: 'Film', 4: 'Podcast', 33: 'Video M4V'}

_MEDIA_QUERY = '''
SELECT
    ext.title, ext.media_kind, itep.format,
    ext.location, ext.total_time_ms, ext.file_size, ext.year,
    alb.album, alba.album_artist, com.composer, gen.genre,
    ite.track_number, art.artwork_token,
    itev.extended_content_rating, itev.movie_info,
    ext.description_long, sto.account_id,
    datetime(sto.date_purchased + 978307200, 'unixepoch'),
    sto.store_item_id, sto.purchase_history_id, ext.copyright
FROM item_extra ext
JOIN item_store sto USING (item_pid)
JOIN item ite USING (item_pid)
JOIN item_stats ites USING (item_pid)
JOIN item_playback itep USING (item_pid)
JOIN item_video itev USING (item_pid)
LEFT JOIN album alb ON sto.item_pid = alb.representative_item_pid
LEFT JOIN album_artist alba ON sto.item_pid = alba.representative_item_pid
LEFT JOIN composer com ON sto.item_pid = com.representative_item_pid
LEFT JOIN genre gen ON sto.item_pid = gen.representative_item_pid
LEFT JOIN item_artist itea ON sto.item_pid = itea.representative_item_pid
LEFT JOIN artwork_token art ON sto.item_pid = art.entity_pid
'''


def _find_db(context):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('Medialibrary.sqlitedb'):
            return file_found
    return ''


@artifact_processor
def mediaLibrary(context):
    data_headers = (
        'Title', 'Media Type', 'File Format', 'File', 'Total Time (ms)', 'File Size', 'Year',
        'Album Name', 'Album Artist', 'Composer', 'Genre', 'Track Number', 'Artwork',
        'Content Rating', 'Movie Information', 'Description', 'Account ID',
        ('Date Purchased', 'datetime'), 'Item ID', 'Purchase History ID', 'Copyright')
    data_list = []
    source_path = _find_db(context)
    if not source_path:
        return data_headers, data_list, ''

    try:
        rows = get_sqlite_db_records(source_path, _MEDIA_QUERY)
    except sqlite3.Error as ex:
        logfunc(f'Error reading Media Library: {ex}')
        return data_headers, data_list, context.get_relative_path(source_path)

    for row in rows:
        values = list(row)
        values[1] = _MEDIA_KIND.get(values[1], values[1])
        data_list.append(tuple(values))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def mediaLibraryInfo(context):
    data_headers = ('Key', 'Value')
    data_list = []
    source_path = _find_db(context)
    if not source_path:
        return data_headers, data_list, ''

    wanted = ('MLJaliscoAccountID', 'MPDateLastSynced', 'MPDateToSyncWithUbiquitousStore',
              'OrderingLanguage')
    try:
        rows = get_sqlite_db_records(source_path, 'SELECT * FROM _MLDATABASEPROPERTIES')
    except sqlite3.Error as ex:
        logfunc(f'Error reading Media Library properties: {ex}')
        return data_headers, data_list, context.get_relative_path(source_path)

    for row in rows:
        if row[0] in wanted:
            data_list.append((row[0], row[1]))

    return data_headers, data_list, context.get_relative_path(source_path)
