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
DEFAULT_REPORT_TABLE_COLUMNS = ("Timestamp", "Key", "Value")


@silence_and_log("Error in {category} section")
def fetch_and_write_data(
    query, db_path, category, report_table_columns=DEFAULT_REPORT_TABLE_COLUMNS
):
    logfunc(f"Aggregated dictionary {category} function executing")

    rows = get_sql_output(passcode_type_query, db_path)
    if not rows:
        logfunc(f"No Aggregated dictionary {category} data available")
        return

    template = template_env.get_template("passcode_type.html")
    rendered = template.render(
        rows=rows,
        db_path=db_path,
        category=category,
        report_table_columns=report_table_columns,
    )
    fpath = f"{report_folder_base}{AGGREGATED_DICT_DIR_NAME}{category}.html"

    with open(fpath, "w") as fp:
        fp.write(rendered)

    logfunc(f"Aggregated dictionary {category} function completed")


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
        report_table_columns=list(DEFAULT_REPORT_TABLE_COLUMNS) + ["Passcode Type"],
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
    fetch_and_write_data(
        distribution_keys_query,
        filefound[0],
        category="Distribution Keys",
        report_table_columns=["Day", "Seconds in a Day", "Key", "Value", "Table ID"],
    )
