import os
import sqlite3
import textwrap

from jinja2 import Environment, FileSystemLoader

from common import logfunc
from contrib.utils import (
    DEFAULT_REPORT_TABLE_COLUMNS,
    fetch_and_write_data,
    get_sql_output,
    silence_and_log,
    write_html_template,
)
from settings import *

from .sql import *


template_env = Environment(
    loader=FileSystemLoader("./contrib/aggregated_dictionary/html/")
)


AGGREGATED_DICT_DIR_NAME = "Aggregated Dict/"


def _create_aggregate_dict_dir():
    dir_name = f"{report_folder_base}Aggregated Dict/"
    os.makedirs(dir_name, exist_ok=True)


def aggdict(filefound):
    logfunc(f"Aggregated dictionary funcion executing")

    _create_aggregate_dict_dir()

    fetch_and_write_data(
        passcode_type_query,
        filefound[0],
        template_env,
        AGGREGATED_DICT_DIR_NAME,
        category="Passcode Type",
        report_table_columns=list(DEFAULT_REPORT_TABLE_COLUMNS) + ["Passcode Type"],
    )
    fetch_and_write_data(
        passcode_success_fail_query,
        filefound[0],
        template_env,
        AGGREGATED_DICT_DIR_NAME,
        category="Passcode Success-Fail",
    )
    fetch_and_write_data(
        passcode_finger_template_query,
        filefound[0],
        template_env,
        AGGREGATED_DICT_DIR_NAME,
        category="Passcode Finger Template",
    )
    fetch_and_write_data(
        scalars_query,
        filefound[0],
        template_env,
        AGGREGATED_DICT_DIR_NAME,
        category="Scalars",
    )
    fetch_and_write_data(
        distribution_keys_query,
        filefound[0],
        template_env,
        AGGREGATED_DICT_DIR_NAME,
        category="Distribution Keys",
        report_table_columns=["Day", "Seconds in a Day", "Key", "Value", "Table ID"],
    )


def dbbuff(filefound):
    logfunc(f"Aggregated dictionary DBbuffer function executing")

    db_path = filefound[0]
    category = "DBBuffer"

    _create_aggregate_dict_dir()

    with open(db_path, "r") as rfp:
        rows = [line.split() for line in rfp.readlines()]

    report_table_columns = ["Value"] * 4
    write_html_template(
        "passcode_type.html",
        rows,
        db_path,
        report_table_columns,
        template_env,
        AGGREGATED_DICT_DIR_NAME,
        category=category,
    )

    logfunc(f"Aggregated dictionary DBbuffer function completed")
