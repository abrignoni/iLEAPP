__artifacts_v2__ = {
    "mediaLibrary": {
        "name": "Media Library",
        "description": "Media items (music, video, podcasts, e-books) from MediaLibrary.sqlitedb",
        "author": "@ydkhatri",
        "creation_date": "2023-11-21",
        "last_update_date": "2026-08-13",
        "requirements": "none",
        "category": "Media Library",
        "notes": (
            "Media-kind value mapping observed in testing; not documented by a published source; "
            "unrecognized values are reported as stored. "
            "An item that carries more than one artwork_token row is reported once per token, so the "
            "row count can exceed the number of media items: on one tested iOS 18.3.2 image 1099 items "
            "produced 1339 rows, 240 of them having two tokens each. "
            "Date Purchased is left blank when item_store.date_purchased is 0, which is how the "
            "column reads for items with no stored purchase date; it was 0 on 3529 of 3533 rows "
            "across the seven tested images that hold media items."),
        "paths": ('**/[Mm]edia[Ll]ibrary.sqlitedb*',),
        "output_types": "standard",
        "artifact_icon": "music",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows; item table empty",
            "hickman_ios13": "iOS 13.3.1 | 301 rows",
            "hickman_ios14": "iOS 14.3 | 643 rows",
            "jess_ios15": "0 rows; item table empty",
            "hickman_ios15": "iOS 15.3.1 | 688 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows; item table empty",
            "felix23_ios16": "iOS 16.5 | 0 rows; item table empty",
            "abe_ios16": "iOS 16.5 | 9 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows; item table empty",
            "fsfull002_ios17": "iOS 17.1 | 0 rows; item table empty",
            "iphone11_ios17": "iOS 17.3 | 839 rows",
            "otto_ios17": "iOS 17.5.1 | 7 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows; item table empty",
            "felix_ios17": "iOS 17.6.1 | 0 rows; item table empty",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows; item table empty",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows; item table empty",
            "dexter_ios18": "iOS 18.3.2 | 1339 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows; item table empty",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows; item table empty",
            "hc_ios26": "iOS 26.5.2 | 0 rows; item table empty"
        }
    },
    "mediaLibraryInfo": {
        "name": "Media Library - Database Properties",
        "description": "Key/value rows from the MediaLibrary.sqlitedb _MLDatabaseProperties table",
        "author": "@ydkhatri",
        "creation_date": "2023-11-21",
        "last_update_date": "2026-08-13",
        "requirements": "none",
        "category": "Media Library",
        "notes": (
            "Every key/value row in the table is reported as stored; the meaning of the individual "
            "keys is not documented by a published source. In 20 tested images the table held "
            "between 8 and 37 keys each, 42 distinct keys across all of them."),
        "paths": ('**/[Mm]edia[Ll]ibrary.sqlitedb*',),
        "output_types": "standard",
        "artifact_icon": "info-circle",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 20 rows",
            "hickman_ios13": "iOS 13.3.1 | 31 rows",
            "hickman_ios14": "iOS 14.3 | 31 rows",
            "jess_ios15": "11 rows",
            "hickman_ios15": "iOS 15.3.1 | 29 rows",
            "magnet_ios16": "iOS 16.1.1 | 12 rows",
            "felix23_ios16": "iOS 16.5 | 18 rows",
            "abe_ios16": "iOS 16.5 | 22 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 12 rows",
            "fsfull002_ios17": "iOS 17.1 | 18 rows",
            "iphone11_ios17": "iOS 17.3 | 37 rows",
            "otto_ios17": "iOS 17.5.1 | 19 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 20 rows",
            "felix_ios17": "iOS 17.6.1 | 19 rows",
            "iphone14plus_ios18": "iOS 18.0 | 8 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 12 rows",
            "dexter_ios18": "iOS 18.3.2 | 35 rows",
            "iphone12_ios18": "iOS 18.7 | 8 rows",
            "hc_ios18_7": "iOS 18.7.8 | 13 rows",
            "hc_ios26": "iOS 26.5.2 | 13 rows"
        }
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
    CASE
        WHEN sto.date_purchased IS NULL OR sto.date_purchased = 0 THEN NULL
        ELSE datetime(sto.date_purchased + 978307200, 'unixepoch')
    END,
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
    # The file is named MediaLibrary.sqlitedb on every tested image. Match without
    # regard to case so a differently-cased path cannot silently yield no rows, and
    # so the -wal and -shm siblings the glob also returns are skipped.
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.lower().endswith('medialibrary.sqlitedb'):
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

    try:
        rows = get_sqlite_db_records(
            source_path, 'SELECT key, value FROM _MLDatabaseProperties ORDER BY key')
    except sqlite3.Error as ex:
        logfunc(f'Error reading Media Library properties: {ex}')
        return data_headers, data_list, context.get_relative_path(source_path)

    for row in rows:
        data_list.append((row[0], row[1]))

    return data_headers, data_list, context.get_relative_path(source_path)
