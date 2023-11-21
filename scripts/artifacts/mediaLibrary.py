import os
import sys
import sqlite3
import time
import datetime
import re

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, open_sqlite_db_readonly

def get_mediaLibrary(files_found, report_folder, seeker, wrap_text, timezone_offset):
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    # Execute query for retrieving media information
    try:
        cursor.execute(
        """
        SELECT ext.title, ext.media_kind, itep.format,
                ext.location, ext.total_time_ms, ext.file_size, ext.year,
                alb.album, alba.album_artist, com.composer, gen.genre,
                ite.track_number, art.artwork_token,
                itev.extended_content_rating, itev.movie_info,
                ext.description_long, sto.account_id,
                strftime(\'%d/%m/%Y %H:%M:%S\', 
                datetime(sto.date_purchased + 978397200, \'unixepoch\'))
                date_purchased, sto.store_item_id, sto.purchase_history_id, ext.copyright
                from item_extra
                ext join item_store sto using (item_pid)
                join item ite using (item_pid)
                join item_stats ites using (item_pid)
                join item_playback itep using (item_pid)
                join item_video itev using (item_pid)
                left join album alb on sto.item_pid=alb.representative_item_pid
                left join album_artist alba
                on sto.item_pid=alba.representative_item_pid
                left join composer com on
                sto.item_pid=com.representative_item_pid
                left join genre gen on sto.item_pid=gen.representative_item_pid
                left join item_artist itea on
                sto.item_pid=itea.representative_item_pid
                left join artwork_token art on sto.item_pid=art.entity_pid
        """
        )
    except:
        logfunc('Error executing SQLite query')

    all_rows = cursor.fetchall()
    data_list = []
    media_type = ''

    for row in all_rows:
        col_count = 0 
        tmp_row = []

        for media_type in row:
            if col_count == 1:
                if media_type == 0:
                    media_type = "E-book"
                if media_type == 1:
                    media_type = "Audio"
                if media_type == 2:
                    media_type = "Film"
                if media_type == 33:
                    media_type = "Video M4V"
        if media_type == 4:
            media_type = "Podcast"
            if col_count == 4:
                media_type = int(media_type)

            col_count = col_count + 1
            tmp_row.append(str(media_type).replace('\n', ''))

        data_list.append(tmp_row)
    
    # Recover account information
    data_list_info = []
    cursor.execute(
	"""
    select * from _MLDATABASEPROPERTIES;
    """
    )
    iOS_info = cursor.fetchall()

    iCloud_items = [
        'MLJaliscoAccountID', 'MPDateLastSynced',
        'MPDateToSyncWithUbiquitousStore', 'OrderingLanguage']

    for row in iOS_info:
        for elm in iCloud_items:
            if row[0] == elm:
                data_list_info.append((row[0],row[1]))
    
    report = ArtifactHtmlReport('Media Library')
    report.start_artifact_report(report_folder, 'Media Library')
    report.add_script()
    data_headers_info = ('key', 'value')
    data_headers = ('Title','Media Type','File Format','File','Total Time (ms)',
                    'File Size','Year','Album Name','Album Artist','Composer',
                    'Genre','Track Number', 'Artwork','Content Rating',
                    'Movie Information','Description','Account ID',
                    'Date Purchased','Item ID','Purchase History ID','Copyright')
                    
    report.write_artifact_data_table(data_headers_info, data_list_info, file_found, cols_repeated_at_bottom=False)
    report.write_artifact_data_table(data_headers, data_list, file_found, True, False)
    
    report.end_artifact_report()

    tsvname = 'Media Library'
    tsv(report_folder, data_headers_info, data_list_info, tsvname)
    tsv(report_folder, data_headers, data_list, tsvname)
    
__artifacts__ = {
    "mediaLibrary": (
        "Media Library",
        ('**/Medialibrary.sqlitedb'),
        get_mediaLibrary)
}