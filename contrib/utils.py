import logging
import os
import sqlite3
from functools import wraps

from common import logfunc
from settings import report_folder_base


DEFAULT_REPORT_TABLE_COLUMNS = ("Timestamp", "Key", "Value")


def silence_and_log(log_template):
    def outer_wrapper(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            ret = None
            try:
                ret = function(*args, **kwargs)
            except Exception as e:
                if os.environ.get("DEBUG"):
                    logging.exception("Exception in processing:")
                logfunc(log_template.format(**kwargs))
            return ret

        return wrapper

    return outer_wrapper


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


@silence_and_log("Error in {category} section")
def write_html_template(
    template,
    rows,
    db_path,
    report_table_columns,
    template_env,
    output_dir_name,
    category="",
):
    """
    Note:
        Always pass in category as a kwarg as long as the silence_and_log
        decorator requires it.
    """
    template = template_env.get_template(template)
    rendered = template.render(
        rows=rows,
        db_path=db_path,
        category=category,
        report_table_columns=report_table_columns,
    )
    fpath = f"{report_folder_base}{output_dir_name}{category}.html"

    with open(fpath, "w") as fp:
        fp.write(rendered)


@silence_and_log("Error in {category} section")
def fetch_and_write_data(
    query,
    db_path,
    template_env,
    output_dir_name,
    category="",
    report_table_columns=DEFAULT_REPORT_TABLE_COLUMNS,
):
    """
    Note:
        Always pass in category as a kwarg as long as the silence_and_log
        decorator requires it.
    """
    logfunc(f"Aggregated dictionary {category} function executing")

    rows = get_sql_output(query, db_path)
    if not rows:
        logfunc(f"No Aggregated dictionary {category} data available")
        return

    write_html_template(
        "passcode_type.html",
        rows,
        db_path,
        report_table_columns,
        template_env,
        output_dir_name,
        category=category,
    )

    logfunc(f"Aggregated dictionary {category} function completed")
