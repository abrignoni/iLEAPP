import glob
import os
import pathlib
import plistlib
import sqlite3

from common import logfunc
from contrib.utils import silence_and_log
from settings import *
from vendor import ccl_bplist


def medlib(filefound):
    try:
        db = sqlite3.connect(filefound[0])
        cursor = db.cursor()
        cursor.execute(
            """
		select
		ext.title AS "Title",
		ext.media_kind AS "Media Type",
		itep.format AS "File format",
		ext.location AS "File",
		ext.total_time_ms AS "Total time (ms)",
		ext.file_size AS "File size",
		ext.year AS "Year",
		alb.album AS "Album Name",
		alba.album_artist AS "Artist", 
		com.composer AS "Composer", 
		gen.genre AS "Genre",
		art.artwork_token AS "Artwork",
		itev.extended_content_rating AS "Content rating",
		itev.movie_info AS "Movie information",
		ext.description_long AS "Description",
		ite.track_number AS "Track number",
		sto.account_id AS "Account ID",
		strftime('%d/%m/%Y %H:%M:%S', datetime(sto.date_purchased + 978397200,'unixepoch'))date_purchased,
		sto.store_item_id AS "Item ID",
		sto.purchase_history_id AS "Purchase History ID",
		ext.copyright AS "Copyright"
		from
		item_extra ext
		join item_store sto using (item_pid)
		join item ite using (item_pid)
		join item_stats ites using (item_pid)
		join item_playback itep using (item_pid)
		join item_video itev using (item_pid)
		left join album alb on sto.item_pid=alb.representative_item_pid
		left join album_artist alba on sto.item_pid=alba.representative_item_pid
		left join composer com on sto.item_pid=com.representative_item_pid
		left join genre gen on sto.item_pid=gen.representative_item_pid
		left join item_artist itea on sto.item_pid=itea.representative_item_pid
		left join artwork_token art on sto.item_pid=art.entity_pid 
		"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Media Library function executing")
            os.makedirs(os.path.join(reportfolderbase, "Media Library/"))
            with open(
                os.path.join(reportfolderbase, "Media Library/Media Library.html"),
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Media Library report</h2>")
                f.write(f"Media Library entries: {usageentries}<br>")
                f.write(f"Media Library located at: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Title</th><th>Media Type</th><th>File Format</th><th>File</th><th>Total Time (ms)</th><th>File Size</th><th>Year</th><th>Album Name</th><th>Artist</th><th>Composer</th><th>Genre</th><th>Artwork</th><th>Content Rating</th><th>Movie Information</th><th>Description</th><th>Track Number</th><th>Account ID</th><th>Date Purchased</th><th>Item ID</th><th>Purchase History ID</th><th>Copyright</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td><td>{row[10]}</td><td>{row[11]}</td><td>{row[12]}</td><td>{row[13]}</td><td>{row[14]}</td><td>{row[15]}</td><td>{row[16]}</td><td>{row[17]}</td><td>{row[18]}</td><td>{row[19]}</td><td>{row[20]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"Media Library function completed")
        else:
            logfunc("No Media Library available")
    except:
        logfunc("Error in Media Library Section.")
