import logging
import os
import sqlite3
from functools import wraps

from common import logfunc


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
