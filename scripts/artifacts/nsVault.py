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
                 " Attachment is the file in the same app container at the folder the row's album records (ZVIDEOALBUM.ZALBUM_PATH),"
                 " named as the row's Video Name, and is blank when no such file was extracted. On hexordia_ios1651 the photo table"
                 " follows the same layout: each of its three photo rows records a storage path equal to its album's path plus its"
                 " file name, and each of those files was extracted. No tested image held a video row, so the video link has only"
                 " been exercised on constructed data.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/FolderLockAdvanced.sqlite*', '*/mobile/Containers/Data/Application/*/Documents/FolderLockAdvanced/Videos/*',),
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
        client.ZVIDEO_SIZE AS "Video Size",
        metadata.ZALBUM_PATH AS "Album Path"
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

    # Each album records its folder relative to the app container (ZALBUM_PATH, for
    # example Documents/FolderLockAdvanced/Videos/My Videos), so a video is looked up in
    # the database's own container, in its album's folder, by its name. A file of the
    # same name elsewhere is not this row's video.
    container = os.path.normpath(os.path.dirname(os.path.dirname(source_path))) if source_path else ''
    extracted = {}
    if container:
        for file_found in files_found:
            file_found = str(file_found)
            if os.path.isfile(file_found):
                extracted[os.path.normpath(file_found)] = file_found

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        modified_date = convert_cocoa_core_data_ts_to_utc(record[0])
        attachment = ''
        album_path, name = record[9], record[6]
        if container and isinstance(album_path, str) and isinstance(name, str) and album_path and name:
            candidate = os.path.normpath(os.path.join(container, album_path, name))
            # A recorded path that climbs out of the container names another app's file.
            try:
                inside = os.path.commonpath([container, candidate]) == container
            except ValueError:  # a different drive on Windows
                inside = False
            if inside and candidate in extracted:
                stored = extracted[candidate]
                attachment = check_in_media(stored, os.path.basename(stored)) or ''
        data_list.append(
            (modified_date, record[1], record[2], record[3], record[4],
             record[5], record[6], attachment, record[7], record[8]))

    return data_headers, data_list, source_path
