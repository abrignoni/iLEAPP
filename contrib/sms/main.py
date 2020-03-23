import os
import sqlite3

from common import logfunc
from contrib.utils import silence_and_log
from settings import *


def smschat(filefound):
    db = sqlite3.connect(filefound[0])
    cursor = db.cursor()
    try:
        cursor.execute(
            """
		SELECT
				CASE
					WHEN LENGTH(MESSAGE.DATE)=18 THEN DATETIME(MESSAGE.DATE/1000000000+978307200,'UNIXEPOCH')
					WHEN LENGTH(MESSAGE.DATE)=9 THEN DATETIME(MESSAGE.DATE + 978307200,'UNIXEPOCH')
					ELSE "N/A"
		    		END "MESSAGE DATE",			
				CASE 
					WHEN LENGTH(MESSAGE.DATE_DELIVERED)=18 THEN DATETIME(MESSAGE.DATE_DELIVERED/1000000000+978307200,"UNIXEPOCH")
					WHEN LENGTH(MESSAGE.DATE_DELIVERED)=9 THEN DATETIME(MESSAGE.DATE_DELIVERED+978307200,"UNIXEPOCH")
					ELSE "N/A"
				END "DATE DELIVERED",
				CASE 
					WHEN LENGTH(MESSAGE.DATE_READ)=18 THEN DATETIME(MESSAGE.DATE_READ/1000000000+978307200,"UNIXEPOCH")
					WHEN LENGTH(MESSAGE.DATE_READ)=9 THEN DATETIME(MESSAGE.DATE_READ+978307200,"UNIXEPOCH")
					ELSE "N/A"
				END "DATE READ",
				MESSAGE.TEXT as "MESSAGE",
				HANDLE.ID AS "CONTACT ID",
				MESSAGE.SERVICE AS "SERVICE",
				MESSAGE.ACCOUNT AS "ACCOUNT",
				MESSAGE.IS_DELIVERED AS "IS DELIVERED",
				MESSAGE.IS_FROM_ME AS "IS FROM ME",
				ATTACHMENT.FILENAME AS "FILENAME",
				ATTACHMENT.MIME_TYPE AS "MIME TYPE",
				ATTACHMENT.TRANSFER_NAME AS "TRANSFER TYPE",
				ATTACHMENT.TOTAL_BYTES AS "TOTAL BYTES"
			FROM MESSAGE
			LEFT OUTER JOIN MESSAGE_ATTACHMENT_JOIN ON MESSAGE.ROWID = MESSAGE_ATTACHMENT_JOIN.MESSAGE_ID
			LEFT OUTER JOIN ATTACHMENT ON MESSAGE_ATTACHMENT_JOIN.ATTACHMENT_ID = ATTACHMENT.ROWID
			LEFT OUTER JOIN HANDLE ON MESSAGE.HANDLE_ID = HANDLE.ROWID
			"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"SMS Chat function executing")

            if os.path.isdir(os.path.join(reportfolderbase, "SMS Chat/")):
                pass
            else:
                os.makedirs(os.path.join(reportfolderbase, "SMS Chat"))

            with open(
                reportfolderbase + "SMS Chat/SMS Chat.html", "w", encoding="utf8"
            ) as f:
                f.write("<html><body>")
                f.write("<h2> SMS Chat report</h2>")
                f.write(f"SMS Chat entries: {usageentries}<br>")
                f.write(f"SMS Chat database located at: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Message Date</th><th>Date Delivered</th><th>Date Read</th><th>Message</th><th>Contact ID</th><th>Service</th><th>Account</th><th>Is Delivered</th><th>Is from Me</th><th>Filename</th><th>MIME Type</th><th>Transfer Type</th><th>Total Bytes</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td><td>{row[10]}</td><td>{row[11]}</td><td>{row[12]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"SMS Chat function completed")
        else:
            logfunc("No SMS Chats available")
    except:
        logfunc("Error on SMS Chat function. Possible empty database.")

    db = sqlite3.connect(filefound[0])
    cursor = db.cursor()
    try:
        cursor.execute(
            '''
		SELECT
				CASE
		 			WHEN LENGTH(MESSAGE.DATE)=18 THEN DATETIME(MESSAGE.DATE/1000000000+978307200,'UNIXEPOCH')
		 			WHEN LENGTH(MESSAGE.DATE)=9 THEN DATETIME(MESSAGE.DATE + 978307200,'UNIXEPOCH')
		 			ELSE "N/A"
				END "MESSAGE DATE",
				CASE 
					WHEN LENGTH(MESSAGE.DATE_DELIVERED)=18 THEN DATETIME(MESSAGE.DATE_DELIVERED/1000000000+978307200,"UNIXEPOCH")
					WHEN LENGTH(MESSAGE.DATE_DELIVERED)=9 THEN DATETIME(MESSAGE.DATE_DELIVERED+978307200,"UNIXEPOCH")
					ELSE "N/A"
				END "DATE DELIVERED",
				CASE 
					WHEN LENGTH(MESSAGE.DATE_READ)=18 THEN DATETIME(MESSAGE.DATE_READ/1000000000+978307200,"UNIXEPOCH")
					WHEN LENGTH(MESSAGE.DATE_READ)=9 THEN DATETIME(MESSAGE.DATE_READ+978307200,"UNIXEPOCH")
					ELSE "N/A"
				END "DATE READ",
				MESSAGE.TEXT as "MESSAGE",
				HANDLE.ID AS "CONTACT ID",
				MESSAGE.SERVICE AS "SERVICE",
				MESSAGE.ACCOUNT AS "ACCOUNT",
				MESSAGE.IS_DELIVERED AS "IS DELIVERED",
				MESSAGE.IS_FROM_ME AS "IS FROM ME",
				ATTACHMENT.FILENAME AS "FILENAME",
				ATTACHMENT.MIME_TYPE AS "MIME TYPE",
				ATTACHMENT.TRANSFER_NAME AS "TRANSFER TYPE",
				ATTACHMENT.TOTAL_BYTES AS "TOTAL BYTES"
			FROM MESSAGE
			LEFT OUTER JOIN MESSAGE_ATTACHMENT_JOIN ON MESSAGE.ROWID = MESSAGE_ATTACHMENT_JOIN.MESSAGE_ID
			LEFT OUTER JOIN ATTACHMENT ON MESSAGE_ATTACHMENT_JOIN.ATTACHMENT_ID = ATTACHMENT.ROWID
			LEFT OUTER JOIN HANDLE ON MESSAGE.HANDLE_ID = HANDLE.ROWID
			WHERE "DATE DELIVERED" IS NOT "N/A"'''
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"SMS Chat Message Delivered function executing")
            with open(
                reportfolderbase + "SMS Chat/SMS Message Delivered.html",
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> SMS Chat Message Delivered report</h2>")
                f.write(f"SMS Chat Message Delivered entries: {usageentries}<br>")
                f.write(
                    f"SMS Chat Message Delivered database located at: {filefound[0]}<br>"
                )
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Message Date</th><th>Date Delivered</th><th>Date Read</th><th>Message</th><th>Contact ID</th><th>Service</th><th>Account</th><th>Is Delivered</th><th>Is from Me</th><th>Filename</th><th>MIME Type</th><th>Transfer Type</th><th>Total Bytes</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td><td>{row[10]}</td><td>{row[11]}</td><td>{row[12]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"SMS Chat Message function completed")
        else:
            logfunc("No SMS Chat Message Delivered available")
    except:
        logfunc(
            "Error on SMS Chat Message Delivered function. Possible empty database."
        )

    db = sqlite3.connect(filefound[0])
    cursor = db.cursor()
    try:
        cursor.execute(
            '''
		SELECT
				CASE
		 			WHEN LENGTH(MESSAGE.DATE)=18 THEN DATETIME(MESSAGE.DATE/1000000000+978307200,'UNIXEPOCH')
		 			WHEN LENGTH(MESSAGE.DATE)=9 THEN DATETIME(MESSAGE.DATE + 978307200,'UNIXEPOCH')
		 			ELSE "N/A"
		     		END "MESSAGE DATE",
				CASE 
					WHEN LENGTH(MESSAGE.DATE_DELIVERED)=18 THEN DATETIME(MESSAGE.DATE_DELIVERED/1000000000+978307200,"UNIXEPOCH")
					WHEN LENGTH(MESSAGE.DATE_DELIVERED)=9 THEN DATETIME(MESSAGE.DATE_DELIVERED+978307200,"UNIXEPOCH")
					ELSE "N/A"
				END "DATE DELIVERED",
				CASE 
					WHEN LENGTH(MESSAGE.DATE_READ)=18 THEN DATETIME(MESSAGE.DATE_READ/1000000000+978307200,"UNIXEPOCH")
					WHEN LENGTH(MESSAGE.DATE_READ)=9 THEN DATETIME(MESSAGE.DATE_READ+978307200,"UNIXEPOCH")
					ELSE "N/A"
				END "DATE READ",
				MESSAGE.TEXT as "MESSAGE",
				HANDLE.ID AS "CONTACT ID",
				MESSAGE.SERVICE AS "SERVICE",
				MESSAGE.ACCOUNT AS "ACCOUNT",
				MESSAGE.IS_DELIVERED AS "IS DELIVERED",
				MESSAGE.IS_FROM_ME AS "IS FROM ME",
				ATTACHMENT.FILENAME AS "FILENAME",
				ATTACHMENT.MIME_TYPE AS "MIME TYPE",
				ATTACHMENT.TRANSFER_NAME AS "TRANSFER TYPE",
				ATTACHMENT.TOTAL_BYTES AS "TOTAL BYTES"
			FROM MESSAGE
			LEFT OUTER JOIN MESSAGE_ATTACHMENT_JOIN ON MESSAGE.ROWID = MESSAGE_ATTACHMENT_JOIN.MESSAGE_ID
			LEFT OUTER JOIN ATTACHMENT ON MESSAGE_ATTACHMENT_JOIN.ATTACHMENT_ID = ATTACHMENT.ROWID
			LEFT OUTER JOIN HANDLE ON MESSAGE.HANDLE_ID = HANDLE.ROWID
			WHERE "DATE READ" IS NOT "N/A"'''
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"SMS Chat Message Read function executing")
            with open(
                reportfolderbase + "SMS Chat/SMS Message Read.html",
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> SMS Chat Message Read report</h2>")
                f.write(f"SMS Chat Message Read entries: {usageentries}<br>")
                f.write(f"SMS Chat Message Readdatabase located at: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Message Date</th><th>Date Delivered</th><th>Date Read</th><th>Message</th><th>Contact ID</th><th>Service</th><th>Account</th><th>Is Delivered</th><th>Is from Me</th><th>Filename</th><th>MIME Type</th><th>Transfer Type</th><th>Total Bytes</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td><td>{row[10]}</td><td>{row[11]}</td><td>{row[12]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"SMS Chat Message Read function completed")
        else:
            logfunc("No SMS Chat Message Read available")
    except:
        logfunc("Error on SMS Chat Message Read available. Posible empty database. ")
