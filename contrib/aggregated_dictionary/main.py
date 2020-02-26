import os
import sqlite3
import textwrap

from jinja2 import Environment, FileSystemLoader

from common import logfunc
from contrib.utils import get_sql_output, silence_and_log
from settings import *

from .sql import *


template_env = Environment(
    loader=FileSystemLoader("./contrib/aggregated_dictionary/html/")
)


AGGREGATED_DICT_DIR_NAME = "Aggregated Dict/"


@silence_and_log("Error in {category} section")
def fetch_and_write_data(query, db_path, category, additional_cols=None):
    additional_cols = additional_cols or []

    logfunc(f"Aggregated dictionary {category} function executing")

    rows = get_sql_output(passcode_type_query, db_path)
    if not rows:
        logfunc(f"No Aggregated dictionary {category} data available")
        return

    template = template_env.get_template("passcode_type.html")
    rendered = template.render(
        rows=rows, db_path=db_path, category=category, additional_cols=additional_cols
    )
    fpath = f"{report_folder_base}{AGGREGATED_DICT_DIR_NAME}{category}.html"

    with open(fpath, "w") as fp:
        fp.write(rendered)

    logfunc(f"Aggregated dictionary {category} function completed")


@silence_and_log("Error in Distribution Keys section")
def distribution_key_logic(distribution_keys_query, filefound):
    """
    This is a temporary method because I cannot directly use
    the fetch_and_write_data() method due to the difference in HTML template.

    When we switch out the custom HTML writing to jinja2, we will be able
    to get rid of this method
    """
    rows = get_sql_output(distribution_keys_query, filefound)
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

    fetch_and_write_data(
        passcode_type_query,
        filefound[0],
        category="Passcode Type",
        additional_cols=["Passcode Type"],
    )
    fetch_and_write_data(
        passcode_success_fail_query, filefound[0], category="Passcode Success-Fail"
    )
    fetch_and_write_data(
        passcode_finger_template_query,
        filefound[0],
        category="Passcode Finger Template",
    )
    fetch_and_write_data(scalars_query, filefound[0], category="Scalars")
    distribution_key_logic(distribution_keys_query, filefound[0])
