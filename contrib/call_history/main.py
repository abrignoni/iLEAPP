import os
import sqlite3

from common import logfunc
from contrib.utils import silence_and_log
from settings import *


def calhist(filefound):
    db = sqlite3.connect(filefound[0])
    cursor = db.cursor()
    cursor.execute(
        """
	SELECT 
			ZADDRESS AS "ADDRESS", 
			ZANSWERED AS "WAS ANSWERED", 
			ZCALLTYPE AS "CALL TYPE", 
			ZORIGINATED AS "ORIGINATED", 
			ZDURATION AS "DURATION (IN SECONDS)",
			ZISO_COUNTRY_CODE as "ISO COUNTY CODE",
			ZLOCATION AS "LOCATION", 
			ZSERVICE_PROVIDER AS "SERVICE PROVIDER",
			DATETIME(ZDATE+978307200,'UNIXEPOCH') AS "TIMESTAMP"
		FROM ZCALLRECORD """
    )

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Call History function executing")

        if os.path.isdir(os.path.join(reportfolderbase, "Call History/")):
            pass
        else:
            os.makedirs(os.path.join(reportfolderbase, "Call History"))

        with open(
            reportfolderbase + "Call History/Call History.html", "w", encoding="utf8"
        ) as f:
            f.write("<html><body>")
            f.write("<h2> Call History report</h2>")
            f.write(f"Call History entries: {usageentries}<br>")
            f.write(f"Call History database located at: {filefound[0]}<br>")
            f.write(
                "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
            )
            f.write("<br/>")
            f.write("")
            f.write(f'<table class="table sticky">')
            f.write(
                f"<tr><th>Address</th><th>Was Answered</th><th>Call Type</th><th>Originated</th><th>Duration in Secs</th><th>ISO County Code</th><th>Location</th><th>Service Provider</th><th>Timestamp</th></tr>"
            )
            for row in all_rows:
                an = str(row[0])
                an = an.replace("b'", "")
                an = an.replace("'", "")

                f.write(
                    f"<tr><td>{an}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td></tr>"
                )
            f.write(f"</table></body></html>")
            logfunc(f"Call History function completed")
    else:
        logfunc("No call history available")
