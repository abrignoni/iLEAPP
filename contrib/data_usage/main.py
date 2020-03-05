import os
import sqlite3

from common import logfunc
from settings import *


def datausage(filefound):
    os.makedirs(os.path.join(reportfolderbase, "Data Usage/"))
    try:
        db = sqlite3.connect(filefound[0])
        cursor = db.cursor()
        cursor.execute(
            """
		SELECT
				DATETIME(ZPROCESS.ZTIMESTAMP + 978307200, 'unixepoch') AS "PROCESS TIMESTAMP",
				DATETIME(ZPROCESS.ZFIRSTTIMESTAMP + 978307200, 'unixepoch') AS "PROCESS FIRST TIMESTAMP",
				DATETIME(ZLIVEUSAGE.ZTIMESTAMP + 978307200, 'unixepoch') AS "LIVE USAGE TIMESTAMP",
				ZBUNDLENAME AS "BUNDLE ID",
				ZPROCNAME AS "PROCESS NAME",
				ZWIFIIN AS "WIFI IN",
				ZWIFIOUT AS "WIFI OUT",
				ZWWANIN AS "WWAN IN",
				ZWWANOUT AS "WWAN OUT",
				ZLIVEUSAGE.Z_PK AS "ZLIVEUSAGE TABLE ID" 
			FROM ZLIVEUSAGE 
			LEFT JOIN ZPROCESS ON ZPROCESS.Z_PK = ZLIVEUSAGE.ZHASPROCESS
		"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Data Usage - Zliveusage function executing")
            with open(
                os.path.join(reportfolderbase, "Data Usage/Zliveusage.html"),
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Zliveusage report</h2>")
                f.write(f"Zliveusage entries: {usageentries}<br>")
                f.write(f"Zliveusage located at: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Process Timestamp</th><th>Process First Timestamp</th><th>Live Usage Timestamp</th><th>Bundle ID</th><th>Process Name</th><th>WIFI In</th><th>WIFI Out</th><th>WWAN IN</th><th>WWAN Out</th><th>Table ID</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"Data Usage - Zliveusage function completed")
        else:
            logfunc("No Data Usage - Zliveusage available")
    except:
        logfunc("Error in Data Usage - Zliveusage section.")

    try:
        db = sqlite3.connect(filefound[0])
        cursor = db.cursor()
        cursor.execute(
            """
		SELECT
				DATETIME(ZPROCESS.ZTIMESTAMP+ 978307200, 'unixepoch') AS "TIMESTAMP",
				DATETIME(ZPROCESS.ZFIRSTTIMESTAMP + 978307200, 'unixepoch') AS "PROCESS FIRST TIMESTAMP",
				ZPROCESS.ZPROCNAME AS "PROCESS NAME",
				ZPROCESS.ZBUNDLENAME AS "BUNDLE ID",
				ZPROCESS.Z_PK AS "ZPROCESS TABLE ID" 
			FROM ZPROCESS
		"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Data Usage - Zprocess function executing")
            with open(
                os.path.join(reportfolderbase, "Data Usage/Zprocess.html"),
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Zprocess report</h2>")
                f.write(f"Zprocess entries: {usageentries}<br>")
                f.write(f"Zprocess located at: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Process Timestamp</th><th>Process First Timestamp</th><th>Live Usage Timestamp</th><th>Bundle ID</th><th>Table ID</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"Data Usage - Zprocess function completed")
        else:
            logfunc("No Data Usage - Zprocess available")
    except:
        logfunc("Error in Data Usage - Zprocess Section.")
