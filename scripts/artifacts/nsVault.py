__artifacts_v2__ = {
    "calculatorVault": {
        "name": "Calculator Vault Application",
        "description": "Parses data from the Calculator# Vault application",
        "author": "@charpy4n6",
        "creation_date": "2025-01-22",
        "last_update_date": "2026-09-19",
        "requirements": "none",
        "category": "Calculator#",
        "notes": "App identity is inferred from the FolderLockAdvanced.sqlite filename observed in testing; the path glob is not bundle-specific."
                 " On hexordia_ios1651 the database sits in the data container of net.newsoftwares.NSVault, the app named 'Calculator #'"
                 " (version 3.3.6), and its ZVIDEO table holds no rows."
                 " Attachment is the file in the same app container's Documents/FolderLockAdvanced/Videos/Movies folder whose"
                 " name equals the row's Video Name, and is blank when no such file was extracted. No tested image held a video"
                 " row, so this link has only been exercised on constructed data.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/FolderLockAdvanced.sqlite*', '*/mobile/Containers/Data/Application/*/Documents/FolderLockAdvanced/Videos/Movies/*',),
        "output_types": "standard",
        "artifact_icon": "eye-off",
        "sample_data": {
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
        }
    }
}

import os
from scripts.ilapfuncs import artifact_processor, check_in_media, get_file_path, get_sqlite_db_records, convert_cocoa_core_data_ts_to_utc

@artifact_processor
def calculatorVault(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "FolderLockAdvanced.sqlite")
    data_list = []

    query = '''
    SELECT
        client.ZMODIFIED_DATE AS "Modified Date",
        metadata.ZALBUM_TITLE AS "Album Title",
        client.ZALBUMID AS "Album ID",
        client.ZSTORAGE_PATH AS "Storage Path",
        client.ZSTORAGE_PATH_THUMBNIL AS "Storage Thumbnail",
        client.ZVIDEO_ID AS "Video ID",
        client.ZVIDEONAME AS "Video Name",
        client.ZVIDOE_DURATION AS "Duration",
        client.ZVIDEO_SIZE AS "Video Size"
    FROM ZVIDEO AS client
    LEFT JOIN ZVIDEOALBUM AS metadata ON client.ZALBUMID = metadata.ZALBUMID
    '''

    data_headers = (
        ('Modified Date', 'datetime'),
        'Album Title',
        'Album ID',
        'Storage Path',
        'Storage Thumbnail',
        'Video ID',
        'Video Name',
        ('Attachment', 'media'),
        'Duration',
        'Video Size')

    # The videos sit in the database's own app container, so only that container's
    # Movies folder is searched; a file of the same name in another container is not
    # this row's video.
    movies = {}
    if source_path:
        container = os.path.dirname(os.path.dirname(source_path))
        movies_dir = os.path.normpath(os.path.join(container, 'Documents', 'FolderLockAdvanced', 'Videos', 'Movies'))
        for file_found in files_found:
            file_found = str(file_found)
            if os.path.normpath(os.path.dirname(file_found)) == movies_dir and os.path.isfile(file_found):
                movies[os.path.basename(file_found)] = file_found

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        modified_date = convert_cocoa_core_data_ts_to_utc(record[0])
        attachment = ''
        stored = movies.get(record[6])
        if stored:
            attachment = check_in_media(stored, os.path.basename(stored)) or ''
        data_list.append(
            (modified_date, record[1], record[2], record[3], record[4],
             record[5], record[6], attachment, record[7], record[8]))

    return data_headers, data_list, source_path
