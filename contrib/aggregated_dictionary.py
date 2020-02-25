import os

import sqlite
from common import logfunc
from settings import report_folder_base


AGGREGATED_DICT_DIR_NAME = "Aggregated Dict/"

passcode_type_query = """
    select
    date(daysSince1970*86400, 'unixepoch', 'utc') as day,
    key,
    value
    case
            when value = -1 then '6 digit'
            when value = 0 then 'No passcode'
            when value = 1 then '4 digit'
            when value = 2 then 'Custom alphanumeric'
            when value = 3 then 'Custom numeric'
            else value 
            END as passcodeType
    from Scalars
    where key = 'com.apple.passcode.PasscodeType'
"""


def get_sql_output(query, db_path):
    """
    Returns back results of SQL query on being passed a query.

    Args:
        query (str): a valid sql query as a string
        db_path (str): path to connect to SQLite database
    """
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows


def passcode_type_section():
    """
    Writes passcode type to HTML file
    """
    rows = get_sql_output(passcode_type_query, filefound[0])

    if not rows:
        logfunc("No Aggregated dictionary Passcode Type data available")
        return

    logfunc(f"Aggregated dictionary Passcode Type function executing")

    fname = "Passcode Type.html"
    full_fname = f"{report_folder_base}{AGGREGATED_DICT_DIR_NAME}{fname}"

    with open(full_fname, "w", encoding="utf8") as f:
        f.write("<html><body>")
        f.write("<h2> Passcode Type report</h2>")
        f.write(f"Passcode Type entries: {len(rows)}<br>")
        f.write(f"Passcode Type located at: {filefound[0]}<br>")
        f.write(
            "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
        )
        f.write("<br/>")
        f.write("")
        f.write(f'<table class="table sticky">')
        f.write(
            f"<tr><th>Timestamp</th><th>Key</th><th>Value</th><th>Passcode Type</th></tr>"
        )
        for row in all_rows:
            f.write(
                f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td></tr>"
            )
        f.write(f"</table></body></html>")

    logfunc(f"Aggregated dictionary Passcode Type function completed")


def aggdict(filefound):
    logfunc(f"Aggregated dictionary funcion executing")

    try:
        dir_name = f"{report_folder_base}Aggregated Dict/"
        os.makedirs(dir_name, exists_ok=True)
    except Exception:
        logfunc("Error creating aggdict() report directory")

    try:
        passcode_type_section()
    except Exception:
        logfunc("Error in Aggregated dictionary Passcode Type section.")

    try:
        db = sqlite3.connect(filefound[0])
        cursor = db.cursor()
        cursor.execute(
            """
		select 
		date(daysSince1970*86400, 'unixepoch', 'utc') as day,
		key, value
		from Scalars
		where key like 'com.apple.passcode.NumPasscode%'
		"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Aggregated dictionary Passcode Sucess-Fail function executing")
            with open(
                reportfolderbase + "Aggregated Dict/Passcode Sucess-Fail.html",
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Passcode Sucess-Fail report</h2>")
                f.write(f"Passcode Sucess-Fail entries: {usageentries}<br>")
                f.write(f"Passcode Sucess-Fail located at: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(f"<tr><th>Timestamp</th><th>Key</th><th>Value</th></tr>")
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(
                    f"Aggregated dictionary Passcode Sucess-Fail function completed"
                )
        else:
            logfunc("No Aggregated dictionary Passcode Sucess-Fail data available")
    except:
        logfunc("Error in Aggregated dictionary Passcode Sucess-Fail section.")

    try:
        db = sqlite3.connect(filefound[0])
        cursor = db.cursor()
        cursor.execute(
            """
		SELECT
		DATE(DAYSSINCE1970*86400, 'unixepoch') AS DAY,
		KEY AS "KEY",
		VALUE AS "VALUE"
		FROM
		SCALARS
		where key = 'com.apple.fingerprintMain.templateCount'
		"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(
                f"Aggregated dictionary Passcode Finger Template function executing"
            )
            with open(
                reportfolderbase + "Aggregated Dict/Passcode Finger Template.html",
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Passcode Finger Template report</h2>")
                f.write(f"Passcode Finger Template entries: {usageentries}<br>")
                f.write(f"Passcode Finger Template located at: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(f"<tr><th>Timestamp</th><th>Key</th><th>Value</th></tr>")
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(
                    f"Aggregated dictionary Passcode Finger Template function completed"
                )
        else:
            logfunc("No Aggregated dictionary Passcode Finger Template data available")
    except:
        logfunc("Error in Aggregated dictionary Passcode Finger Template section.")

    try:
        db = sqlite3.connect(filefound[0])
        cursor = db.cursor()
        cursor.execute(
            """
		SELECT
		       DATE(DAYSSINCE1970*86400, 'unixepoch') AS DAY,
			   KEY AS "KEY",
			   VALUE AS "VALUE"
			FROM
			   SCALARS
		"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Aggregated dictionary Scalars function executing")
            with open(
                reportfolderbase + "Aggregated Dict/Scalars.html", "w", encoding="utf8"
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Scalars report</h2>")
                f.write(f"Scalar entries: {usageentries}<br>")
                f.write(f"Scalars located at: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(f"<tr><th>Timestamp</th><th>Key</th><th>Value</th></tr>")
                for row in all_rows:
                    key = textwrap.fill(row[1])
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{key}</td><td>{row[2]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"Aggregated dictionary Scalars function completed")
        else:
            logfunc("No Aggregated dictionary Scalars data available")
    except:
        logfunc("Error in Aggregated dictionary Scalars section.")

    try:
        db = sqlite3.connect(filefound[0])
        cursor = db.cursor()
        cursor.execute(
            """
		SELECT
				DATE(DISTRIBUTIONKEYS.DAYSSINCE1970*86400, 'unixepoch') AS "DAY",
				DISTRIBUTIONVALUES.SECONDSINDAYOFFSET AS "SECONDS IN DAY OFFSET",
				DISTRIBUTIONKEYS.KEY AS "KEY",
				DISTRIBUTIONVALUES.VALUE AS "VALUE",
				DISTRIBUTIONVALUES.DISTRIBUTIONID AS "DISTRIBUTIONVALUES TABLE ID"
			FROM
				DISTRIBUTIONKEYS 
				LEFT JOIN
					DISTRIBUTIONVALUES 
					ON DISTRIBUTIONKEYS.ROWID = DISTRIBUTIONVALUES.DISTRIBUTIONID
		"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Aggregated dictionary Distribution Keys function executing")
            with open(
                reportfolderbase + "Aggregated Dict/Distribution Keys.html",
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Distribution Keys report</h2>")
                f.write(f"Distribution Keys entries: {usageentries}<br>")
                f.write(f"Distribution Keys located at: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Day</th><th>Seconds in Day Offset</th><th>Key</th><th>Value</th><th>Table ID</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"Aggregated dictionary Distribution Keys function completed")
        else:
            logfunc("No Aggregated dictionary Distribution Keys data available")
    except:
        logfunc("Error in Aggregated dictionary Distribution Keys section.")
