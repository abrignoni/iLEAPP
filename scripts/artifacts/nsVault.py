__artifacts_v2__ = {
    "calculatorVault": {
        "name": "Calculator Vault Application",
        "description": "Parses data from the Calculator# Vault application",
        "author": "@charpy4n6",
        "creation_date": "2025-01-22",
        "last_update_date": "2025-01-23",
        "requirements": "none",
        "category": "Calculator#",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/FolderLockAdvanced.sqlite*', '*/mobile/Containers/Data/Application/*/Documents/FolderLockAdvanced/Videos/Movies/*',),
        "output_types": "standard",
        "html_columns": ['Attachment'],
        "artifact_icon": "eye-off"
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, convert_cocoa_core_data_ts_to_utc, media_to_html

@artifact_processor
def calculatorVault(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "FolderLockAdvanced.sqlite")
    data_list = []
    data_list_html = []

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
          'Attachment', 
          'Duration', 
          'Video Size')
    
    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
            modified_date = convert_cocoa_core_data_ts_to_utc(record[0])
            attachmentName = str(record[6])
            thumb = media_to_html(attachmentName, files_found, report_folder)
            data_list.append(
                  (modified_date, record[1], record[2], record[3], record[4], 
                   record[5], record[6], '', record[7], record[8]))
            data_list_html.append(
                  (modified_date, record[1], record[2], record[3], record[4], 
                   record[5], record[6], thumb, record[7], record[8]))
            
    return data_headers, (data_list, data_list_html), source_path