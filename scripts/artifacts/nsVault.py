import os
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, timeline, tsv, is_platform_windows, open_sqlite_db_readonly, media_to_html


def get_calculatorVault(files_found, report_folder, seeker, wrap_text, timezone_offset):
    usageentries = 0
    for file_found in files_found:
        if file_found.endswith('FolderLockAdvanced.sqlite'):
            
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
    
            cursor.execute('''
            SELECT
                datetime(client.ZMODIFIED_DATE + 978307200, 'unixepoch') AS "Modified Date",
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
            ''')
    
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            data_list = []

    if usageentries > 0:
        for row in all_rows:
        
                attachmentName = str(row[6])
                thumb = media_to_html(attachmentName, files_found, report_folder)
            
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], thumb, row[7], row[8]))
            

        description = 'Parses data from the Calculator# Vault application'
        report = ArtifactHtmlReport('Calculator Vault')
        report.start_artifact_report(report_folder, 'Calculator Vault', description)
        report.add_script()
        data_headers = ('Modified Date', 'Album Title', 'Album ID', 'Storage Path', 'Storage Thumbnail', 'Video ID', 'Video Name', 'Attachment', 'Duration', 'Video Size')
        report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Attachment'])
        report.end_artifact_report()

        tsvname = 'Calculator Vault'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Calculator Vault'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Calculator Vault data available')

    db.close()

__artifacts__ = {
    "Calculator Vault Application": (
        "Calculator#",
        ('**mobile/Containers/Data/Application/*/Library/FolderLockAdvanced.sqlite*', '**/mobile/Containers/Data/Application/*/Documents/FolderLockAdvanced/Videos/Movies/*'),
        get_calculatorVault)
}