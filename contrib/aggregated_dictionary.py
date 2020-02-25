import os
import sqlite3
import textwrap

from common import logfunc
from contrib.utils import get_sql_output, write_html_to_file
from settings import *


AGGREGATED_DICT_DIR_NAME = "Aggregated Dict/"


def fetch_and_write_data(query, db_path, category, additional_cols=None):
    rows = get_sql_output(passcode_type_query, db_path)

    if not rows:
        logfunc(f"No Aggregated dictionary {category} data available")
        return

    logfunc(f"Aggregated dictionary {category} function executing")

    fpath = f"{report_folder_base}{AGGREGATED_DICT_DIR_NAME}{category}.html"

    write_html_to_file(fpath, rows, db_path, category, additional_cols=additional_cols)

    logfunc(f"Aggregated dictionary {category} function completed")


passcode_type_query = """
    select
    date(daysSince1970*86400, 'unixepoch', 'utc') as day,
    key,
    value,
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

passcode_success_fail_query = """
    select 
    date(daysSince1970*86400, 'unixepoch', 'utc') as day,
    key, value
    from Scalars
    where key like 'com.apple.passcode.NumPasscode%'
    """

passcode_finger_template_query = """
    SELECT
    DATE(DAYSSINCE1970*86400, 'unixepoch') AS DAY,
    KEY AS "KEY",
    VALUE AS "VALUE"
    FROM
    SCALARS
    where key = 'com.apple.fingerprintMain.templateCount'
    """

scalars_query = """
    SELECT
           DATE(DAYSSINCE1970*86400, 'unixepoch') AS DAY,
               KEY AS "KEY",
               VALUE AS "VALUE"
            FROM
               SCALARS
    """

distribution_keys_query = """
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


def distribution_key_logic(distribution_keys_query, filefound):
    """
    This is a temporary method because I cannot directly use
    the fetch_and_write_data() method due to the difference in HTML template.

    When we switch out the custom HTML writing to jinja2, we will be able
    to get rid of this method
    """
    rows = get_sql_output(distribution_keys_query, filefound[0])
    if rows:
        logfunc(f"Aggregated dictionary Distribution Keys function executing")
        fpath = reportfolderbase + "Aggregated Dict/Distribution Keys.html"
        num_entries = len(rows)
        with open(fpath, "w", encoding="utf8") as f:
            f.write("<html><body>")
            f.write("<h2> Distribution Keys report</h2>")
            f.write(f"Distribution Keys entries: {num_entries}<br>")
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
            for row in rows:
                f.write(
                    f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></tr>"
                )
            f.write(f"</table></body></html>")
            logfunc(f"Aggregated dictionary Distribution Keys function completed")
    else:
        logfunc("No Aggregated dictionary Distribution Keys data available")


def aggdict(filefound):
    logfunc(f"Aggregated dictionary funcion executing")

    try:
        dir_name = f"{report_folder_base}Aggregated Dict/"
        os.makedirs(dir_name, exist_ok=True)
    except Exception:
        logfunc("Error creating aggdict() report directory")

    try:
        fetch_and_write_data(
            passcode_type_query,
            filefound[0],
            category="Passcode Type",
            additional_cols=["Passcode Type"],
        )
    except Exception:
        logfunc("Error in Aggregated dictionary Passcode Type section.")

    try:
        fetch_and_write_data(
            passcode_success_fail_query, filefound[0], category="Passcode Success-Fail"
        )
    except Exception:
        logfunc("Error in Aggregated dictionary Passcode Sucess-Fail section.")

    try:
        fetch_and_write_data(
            passcode_finger_template_query,
            filefound[0],
            category="Passcode Finger Template",
        )
    except:
        logfunc("Error in Aggregated dictionary Passcode Finger Template section.")

    try:
        fetch_and_write_data(scalars_query, filefound[0], category="Scalars")
    except:
        logfunc("Error in Aggregated dictionary Scalars section.")

    try:
        distribution_key_logic(distribution_key_query, filefound[0])
    except:
        logfunc("Error in Aggregated dictionary Distribution Keys section.")
