"""
This module provides functionality for initializing, processing, and finalizing
artifact data from forensic analysis. It manages both a SQLite database for
structured data storage and a JSON file for metadata and configuration.

Global Variables:
    lava_data (dict): Main data structure containing artifacts, modules, and metadata.
    lava_db (sqlite3.Connection): SQLite database connection for artifact storage.
    lava_db_name (str): Name of the SQLite database file.
    lava_json_name (str): Name of the JSON metadata file.

Functions:
    sanitize_sql_name: Sanitizes strings for use as SQL identifiers.
    quote_sql_name: Quotes an identifier so reserved words are safe in SQL.
    get_sql_type: Maps Python types to SQL types.
    initialize_lava: Initializes the LAVA data structure and database.
    lava_process_artifact: Processes and stores artifact data.
    lava_add_module: Adds module information to the LAVA data.
    lava_create_sqlite_table: Creates a SQLite table for artifact data.
    lava_insert_sqlite_data: Inserts data rows into a SQLite table.
    lava_iter_artifact_rows: Streams stored artifact rows back from LAVA.
    lava_get_media_item: Retrieves media item information from database.
    lava_insert_sqlite_media_item: Inserts media item metadata into database.
    lava_get_media_references: Retrieves media reference information.
    lava_insert_sqlite_media_references: Inserts media reference into database.
    lava_get_full_media_info: Retrieves complete media information with joins.
    lava_finalize_output: Finalizes and saves LAVA output files.
"""

import json
import sqlite3
import sys
import os
from platform import platform
from collections import OrderedDict
import math
import re
import datetime
import queue
import threading

from scripts.version_info import leapp_name, leapp_version
from scripts.context import Context

# Global variables
lava_data = None
lava_db = None
lava_db_name = '_lava_artifacts.db'
lava_json_name = '_lava_data.lava'
lava_db_path = None
_QUEUE_STOP = object()
LAVA_SCHEMA_VERSION = 2


def sanitize_sql_name(name):
    """
    Sanitizes a given name by removing invalid characters and formatting it.
    This function takes a string `name` and performs the following operations:
    1. Removes any character that is not a word character (alphanumeric or underscore) or whitespace.
    2. Replaces consecutive whitespace characters with a single underscore.
    3. Ensures that the resulting string starts with a letter or an underscore; if not, it prepends an underscore.
    4. Converts the entire string to lowercase.
    Args:
        name (str): The name to be sanitized.
    Returns:
        str: The sanitized SQL name.
    """

    sanitized = re.sub(r'[^\w\s]', '', name)
    sanitized = re.sub(r'\s+', '_', sanitized)
    # Ensure the name starts with a letter or underscore
    if sanitized and not sanitized[0].isalpha() and sanitized[0] != '_':
        sanitized = '_' + sanitized
    return sanitized.lower()


def quote_sql_name(name):
    """
    Wraps an identifier in double quotes so it is safe to interpolate into SQL.

    sanitize_sql_name() removes the characters SQLite cannot parse, but it cannot stop a
    header from sanitizing down to a reserved word. A 'From', 'To' or 'Order' column used
    to emit `CREATE TABLE ... (from TEXT, ...)`, a syntax error that killed the artifact at
    report time even though the parser itself ran fine. Quoting makes reserved words legal.
    Any embedded double quote is doubled, per the SQL standard, so the quoting holds.
    Args:
        name (str): The identifier to quote.
    Returns:
        str: The identifier wrapped in double quotes.
    """

    return '"' + str(name).replace('"', '""') + '"'


def get_sql_type(python_type):
    """
    Convert Python type names to SQL type names for database schema creation.
    Args:
        python_type (str): The name of the Python type as a string (e.g., 'datetime', 'date', 'str').
    Returns:
        str: The corresponding SQL type name. Returns 'INTEGER' for datetime and date types,
             and 'TEXT' as the default for all other types.
    """

    type_map = {
        'datetime': 'INTEGER',
        'date': 'TEXT',
    }
    return type_map.get(python_type, 'TEXT')


def bind_dates_as_text(value):
    """
    Return a date or datetime as the text sqlite3's default adapters wrote for it.

    Those adapters are deprecated as of Python 3.12 and warn on every value they convert.
    str() returns exactly what they did, isoformat(" ") for a datetime and isoformat() for a
    date, so binding its result stores the same text. Any other value is returned unchanged.
    """
    if isinstance(value, datetime.date):
        return str(value)
    return value


def _prepare_datetime_value(value):
    """Convert supported datetime values to UTC Unix timestamps for LAVA storage."""

    if isinstance(value, str):
        try:
            parsed = datetime.datetime.fromisoformat(value)
        except ValueError:
            return value
        # An ISO string has always been stored as a whole-second epoch; keep that so a
        # list-returning artifact's LAVA values do not change.
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=datetime.timezone.utc)
        return int(parsed.timestamp())

    if isinstance(value, datetime.datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=datetime.timezone.utc)
        # Use subtraction instead of timestamp() so pre-epoch dates work consistently.
        epoch = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
        return (value - epoch).total_seconds()

    return value


def _prepare_date_value(value):
    """
    Convert supported date values to YYYY-MM-DD strings for LAVA storage.

    Calendar dates are stored without a time or zone, never as midnight timestamps, so a
    date-only field cannot shift by a day when a timezone is applied to it later.
    """

    d = None
    if isinstance(value, datetime.datetime):
        d = value.date()
    elif isinstance(value, datetime.date):
        d = value
    elif isinstance(value, str):
        text = value.strip()
        if text:
            try:
                d = datetime.date.fromisoformat(text[:10])
            except ValueError:
                try:
                    d = datetime.datetime.fromisoformat(text).date()
                except ValueError:
                    d = None
    if d is not None:
        return d.isoformat()

    return value


def _python_text(value):
    """
    The text Python itself would print for a float or a boolean, or the value unchanged.

    An untyped LAVA column is TEXT, and SQLite renders a bound float into it at 15
    significant digits and a boolean as 1 or 0. The HTML, TSV, timeline and KML writers
    print the Python value, so rows replayed out of LAVA would otherwise read
    35.6595662310191 where the list path wrote 35.65956623101914, and 1 where it wrote
    True. Storing Python's own text keeps the replayed outputs identical to the list
    path's; _restore_lava_value turns it back into the value.
    """

    if isinstance(value, bool):
        return 'True' if value else 'False'
    if isinstance(value, float) and math.isfinite(value):
        return repr(value)
    return value


def _prepare_lava_value(value, column_type=None, keep_python_text=False):
    """
    Convert a Python value into the representation stored in the LAVA SQLite table.

    Only column types that need storage conversion get handlers here. Other object
    column types, such as phonenumber, remain normal SQLite TEXT values while their
    type metadata stays available in the LAVA artifact metadata.

    keep_python_text stores a float or boolean in an untyped column as the text Python
    prints for it (see _python_text). Rows that will be replayed for the other outputs
    ask for it; the list path does not, so its stored values are unchanged.
    """

    if isinstance(value, (dict, list)):
        return json.dumps(value)

    if keep_python_text and column_type is None:
        return _python_text(value)

    type_handlers = {
        'datetime': _prepare_datetime_value,
        'date': _prepare_date_value,
    }
    handler = type_handlers.get(column_type)
    if handler:
        value = handler(value)

    # A date or datetime still held as an object would go through sqlite3's deprecated default
    # adapters when bound; store the text they wrote instead.
    return bind_dates_as_text(value)


def _restore_lava_value(value, column_type=None):
    """
    Restore a value streamed back from the LAVA SQLite table for secondary outputs.

    Untyped columns come back through the inverse of _python_text: the text 'True' or
    'False' becomes the boolean, text that is exactly the repr of a finite float
    becomes that float, and text that is exactly the decimal form of an integer becomes
    that integer, so the timeline's JSON carries a number where the list path carried
    a number. A text cell that happens to hold one of those spellings is typed the
    same way; nothing in the table records which it was.
    """

    if value is None:
        return value

    if column_type == 'datetime' and isinstance(value, (int, float)):
        return datetime.datetime.fromtimestamp(value, tz=datetime.timezone.utc)

    if column_type == 'date' and isinstance(value, (int, float)):
        return datetime.datetime.fromtimestamp(value, tz=datetime.timezone.utc).date()

    if column_type == 'media' and isinstance(value, str) and value.startswith('['):
        # A cell holding several media references was stored as a JSON list.
        try:
            return json.loads(value)
        except ValueError:
            return value

    if column_type is None and isinstance(value, str):
        if value == 'True':
            return True
        if value == 'False':
            return False
        try:
            integer = int(value)
        except ValueError:
            integer = None
        if integer is not None and str(integer) == value:
            return integer
        try:
            number = float(value)
        except ValueError:
            return value
        if math.isfinite(number) and repr(number) == value:
            return number

    return value


def initialize_lava(input_path, output_path, input_type, profile_filename=None):
    '''
    Initialize the LAVA data.
    Args:
        input_path: The path to the input file.
        output_path: The path to the output file.
        input_type: The type of input file.
        profile_filename: The profile file used for module selection, if any.
    '''

    # lava_data and lava_db are module level singletons for the run; this is the one
    # function that creates them, so the global statement is deliberate.
    global lava_data, lava_db, lava_db_path  # pylint: disable=global-statement

    lava_data = {
        "lava_schema_version": LAVA_SCHEMA_VERSION,
        "parser_info": {
            "leapp_name": leapp_name,
            "leapp_version": leapp_version,
            "leapp_mode": "GUI" if "leappGUI" in sys.argv[0] else "CLI", 
            "package": "Source code" if not getattr(sys, 'frozen', False) else "Binary",
            "OS": platform(),
            "start_timestamp": int(datetime.datetime.now(datetime.timezone.utc).timestamp())
        },
        "param_input": input_path,
        "param_output": output_path,
        "param_type": input_type,
        "param_profile": profile_filename,
        "profile_used": profile_filename is not None,
        "processing_status": "In Progress",
        "lava_db_name": lava_db_name,
        "modules": [],
        "artifacts": OrderedDict(),
        "meta": {
            "modules": []
        }
    }

    lava_db_path = os.path.join(output_path, lava_db_name)
    lava_db = sqlite3.connect(lava_db_path)

    cursor = lava_db.cursor()
    cursor.execute('''CREATE TABLE _artifact_search_patterns (
                        id INTEGER PRIMARY KEY,
                        module_name TEXT NOT NULL,
                        artifact_name TEXT NOT NULL,
                        regex TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE _file_path_list (
                        id INTEGER PRIMARY KEY,
                        file_path TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE _artifact_pattern_to_file (
                        id INTEGER PRIMARY KEY,
                        artifact_search_pattern_id INTEGER NOT NULL,
                        file_path_id INTEGER NOT NULL,
                        FOREIGN KEY (artifact_search_pattern_id) REFERENCES _artifact_search_patterns(id),
                        FOREIGN KEY (file_path_id) REFERENCES _file_path_list(id))''')
    cursor.execute('''CREATE TABLE _lava_media_items (
                        id TEXT PRIMARY KEY,
                        source_path TEXT,
                        extraction_path TEXT,
                        type TEXT,
                        metadata TEXT,
                        created_at INTEGER,
                        updated_at INTEGER,
                        is_embedded INTEGER)''')
    cursor.execute('''CREATE TABLE _lava_media_references (
                        id TEXT PRIMARY KEY,
                        media_item_id TEXT,
                        module_name TEXT,
                        artifact_name TEXT,
                        name TEXT,
                        FOREIGN KEY (media_item_id) REFERENCES _lava_media_items(id))''')
    cursor.execute('''CREATE VIEW _lava_media_info AS
                        SELECT
                            lmr.id as 'media_ref_id',
                            lmr.media_item_id,
                            lmr.module_name,
                            lmr.artifact_name,
                            lmr.name,
                            lmi.source_path,
                            lmi.extraction_path,
                            lmi.type,
                            lmi.metadata,
                            lmi.created_at,
                            lmi.updated_at,
                            lmi.is_embedded
                        FROM _lava_media_references as lmr
                        LEFT JOIN _lava_media_items as lmi ON lmr.media_item_id = lmi.id''')


# Conversation view keys whose value is data rather than a column name. LAVA reads these two
# as written and resolves every other key to a column, so the writer must not turn them into
# a column's SQL name when the value happens to match a header, as a 'Sent' direction value
# does beside a 'Sent' time column.
CONVERSATION_VALUE_KEYS = ('directionSentValue', 'sentMessageStaticLabel')


def lava_process_artifact(
        category,
        module_name,
        artifact_name,
        data,
        record_count=None,
        func_name=None,
        data_views=None,
        artifact_icon=None,
        source_path=None):

    '''
    Process an artifact and add it to the LAVA data.
    Args:
        category: The category of the artifact.
        module_name: The name of the module that processed the artifact.
        artifact_name: The name of the artifact.
        data: The name of the columns.
        func_name: The name of the function that processed the artifact.
        record_count: The number of records in the artifact.
        data_views: The data views of the artifact.
        artifact_icon: The icon of the artifact.
        source_path: The source path of the artifact.
    '''

    if category not in lava_data["artifacts"]:
        lava_data["artifacts"][category] = []

    # To backward compatibility for modules not updated that are not passing func_name
    if func_name is None:
        func_name = artifact_name

    sanitized_table_name, column_map, object_columns = lava_create_sqlite_table(func_name, data)

    # Add artifact metadata
    artifact_info = Context.get_artifact_info()
    module_info = next((m for m in lava_data['meta']['modules'] if m['module_name'] == module_name), None)

    if not module_info:
        module_info = {
            "module_name": module_name,
            "module_filename": os.path.basename(Context.get_module_file_path()),
            "artifacts": []
        }
        lava_data['meta']['modules'].append(module_info)

    artifact_meta = {
        "artifact_key": sanitized_table_name,
        "tablename": sanitized_table_name,
        "name": artifact_name,
        "description": artifact_info.get('description', ''),
        "author": artifact_info.get('author', ''),
        "created_date": artifact_info.get('creation_date', ''),
        "last_updated_date": artifact_info.get('last_update_date', ''),
        "notes": artifact_info.get('notes', ''),
        "category": category
    }
    module_info['artifacts'].append(artifact_meta)

    artifact = {
        "artifact_key": func_name,
        "name": artifact_name,
        "tablename": sanitized_table_name,
        "module": module_name,
        "column_map": column_map
    }
    if artifact_icon:
        artifact['artifact_icon'] = artifact_icon

    if record_count is not None:
        artifact["record_count"] = record_count

    if source_path:
        artifact['source_path'] = source_path

    if object_columns:
        artifact["object_columns"] = [{"name": name, "type": type_} for name, type_ in object_columns.items()]

    if data_views:
        view_params = None

        # Backward compatibility for chat view. Remove 'chat' once modules are updated.
        if "chat" in data_views:
            view_params = data_views.pop("chat")
            data_views["conversation"] = view_params  # Upgrade to conversation
        elif "conversation" in data_views:
            view_params = data_views.get("conversation")

        if view_params:
            sanitized_params = {}

            # Get original column names for dynamic sanitization check
            column_names = [item[0] if isinstance(item, tuple) else item for item in data]

            # Conversion map for backward compatibility. Remove once modules are updated.
            convert_map = {
                "threadDiscriminatorColumn": "conversationDiscriminatorColumn",
                "threadLabelColumn": "conversationLabelColumn"
            }

            for key, value in view_params.items():
                # Remap old keys to new keys
                final_key = convert_map.get(key, key)

                # Sanitize value if it's a column name, otherwise pass through. A value key
                # carries data, so it passes through even when it equals a column name.
                if final_key not in CONVERSATION_VALUE_KEYS and value in column_names:
                    sanitized_params[final_key] = sanitize_sql_name(value)
                else:
                    sanitized_params[final_key] = value

            data_views["conversation"] = sanitized_params

        artifact['data_views'] = data_views

    lava_data["artifacts"][category].append(artifact)

    return sanitized_table_name, object_columns, column_map


class _LavaArtifactRows:
    """Reusable iterable for reading artifact rows back from the LAVA database."""

    def __init__(self, table_name, headers, object_columns=None, row_count=None):
        self.table_name = table_name
        self.headers = headers
        self.object_columns = object_columns or {}
        self.row_count = row_count
        self.sanitized_columns = [
            sanitize_sql_name(header[0] if isinstance(header, tuple) else header)
            for header in headers
        ]
        quoted_columns = ', '.join(quote_sql_name(column) for column in self.sanitized_columns)
        self.query = f"SELECT {quoted_columns} FROM {quote_sql_name(table_name)} ORDER BY rowid"

    def __len__(self):
        if self.row_count is not None:
            return self.row_count

        cursor = lava_db.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {quote_sql_name(self.table_name)}")
        self.row_count = cursor.fetchone()[0]
        return self.row_count

    def __iter__(self):
        cursor = lava_db.cursor()
        for row in cursor.execute(self.query):
            yield self._restore_row(row)

    def _restore_row(self, row):
        restored_row = []
        for index, value in enumerate(row):
            column = self.sanitized_columns[index]
            value = _restore_lava_value(value, self.object_columns.get(column))
            restored_row.append(value)
        return tuple(restored_row)


def lava_iter_artifact_rows(table_name, headers, object_columns=None, row_count=None):
    """
    Return a reusable iterable that streams artifact rows from the LAVA table.

    ArtifactResult rows are consumed once while inserting into LAVA. Secondary
    outputs can call this helper to replay the stored rows without materializing
    the original module result in memory.
    """
    return _LavaArtifactRows(table_name, headers, object_columns, row_count)


def lava_add_module(module_name, module_status, file_count=None, artifact_name=None):
    """
    Adds a module to the global lava_data structure.
    Parameters:
        module_name (str): The name of the module to be added.
        module_status (str): The status of the module (e.g., 'active', 'inactive').
        file_count (int, optional): The number of files associated with the module. Defaults to None.
        artifact_name (str, optional): The selected artifact name when it differs from the module filename.
    Returns:
        None
    Global Variables:
        lava_data (dict): A global dictionary that contains a list of modules under the key 'modules'.
    """


    module = {
        "module_name": module_name,
        "module_status": module_status
    }
    if artifact_name is not None:
        module["artifact_name"] = artifact_name
    if file_count is not None:
        module["file_count"] = file_count
    lava_data["modules"].append(module)


def lava_create_sqlite_table(table_name, data):
    """
    Creates a SQLite table with the specified name and columns based on the provided data.
    Parameters:
        table_name (str): The name of the table to be created in the SQLite database.
        data (list): A list of tuples or strings representing the columns of the table.
                     Each tuple should contain the original column name and its data type.
                     If a string is provided, it is treated as a column name with a default type of TEXT.
    Returns:
        tuple: A tuple containing:
            - sanitized_table_name (str): The sanitized name of the created table.
            - column_map (dict): A mapping of sanitized column names to their original names.
            - object_columns (dict): A mapping of sanitized column names to their data types.
    Raises:
        Exception: If there is an error during the table creation process.
    """

    if not data:
        return None, None, None

    sanitized_table_name = sanitize_sql_name(table_name)
    cursor = lava_db.cursor()

    columns = []
    column_map = {}
    object_columns = {}

    for item in data:
        if isinstance(item, tuple):
            original_name, data_type = item[:2]  # Only take the first two elements as media item can have more
            sanitized_name = sanitize_sql_name(original_name)
            sql_type = get_sql_type(data_type)
            columns.append(f"{quote_sql_name(sanitized_name)} {sql_type}")
            object_columns[sanitized_name] = data_type
        else:
            original_name = item
            sanitized_name = sanitize_sql_name(original_name)
            columns.append(f"{quote_sql_name(sanitized_name)} TEXT")

        column_map[sanitized_name] = original_name

    columns_sql = ', '.join(columns)
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {quote_sql_name(sanitized_table_name)} ({columns_sql})")
    lava_db.commit()

    return sanitized_table_name, column_map, object_columns


# column_map is unused here but is part of the established call signature: every caller
# receives it from lava_create_sqlite_table and passes it straight through, so dropping
# the parameter would mean touching every artifact that writes to LAVA.
def lava_insert_sqlite_data(
        table_name,
        data,
        object_columns,
        headers,
        column_map,  # pylint: disable=unused-argument
        batch_size=10000,
        async_write=False,
        queue_size=5000,
        keep_python_text=False):
    """
    Insert data into a SQLite database table with automatic column sanitization and type conversion.
    This function handles the insertion of multiple rows of data into a specified SQLite table,
    with special handling for complex data types (dict, list) and object-column type conversions.
    Args:
        table_name (str): The name of the SQLite table to insert data into.
        data (iterable): Rows to insert, where each row is a sequence of values
                         corresponding to the headers.
        object_columns (dict): A dictionary mapping column names to their data types.
                              'datetime' values are stored as Unix timestamps (UTC).
                              'date' values are stored as YYYY-MM-DD strings (no time / TZ).
        headers (list): A list of column headers. Each header can be a string or a tuple
                       where the first element is the column name.
        column_map (dict): Column mapping configuration (currently unused in the function).
        batch_size (int): Maximum rows to insert per SQLite executemany call.
        async_write (bool): If True, prepare and insert rows on a writer thread.
        queue_size (int): Maximum rows waiting for the async writer.
        keep_python_text (bool): Store floats and booleans in untyped columns as the text
                                 Python prints for them, for rows that will be replayed.
    Returns:
        int: Number of rows inserted.
    """


    if not data:
        return 0

    # Use the sanitized column names directly
    sanitized_columns = [sanitize_sql_name(h[0] if isinstance(h, tuple) else h) for h in headers]

    # Prepare the SQL query
    placeholders = ', '.join(['?' for _ in sanitized_columns])
    quoted_columns = ', '.join(quote_sql_name(column) for column in sanitized_columns)
    query = f"INSERT INTO {quote_sql_name(table_name)} ({quoted_columns}) VALUES ({placeholders})"

    column_types = [object_columns.get(column) for column in sanitized_columns]

    def prepare_row(row):
        if isinstance(row, sqlite3.Row):
            row = tuple(row)
        processed_row = []
        for index, value in enumerate(row):
            processed_row.append(_prepare_lava_value(value, column_types[index], keep_python_text))
        return tuple(processed_row)

    if async_write:
        return _lava_insert_sqlite_data_async(
            query,
            data,
            prepare_row,
            batch_size,
            queue_size,
        )

    cursor = lava_db.cursor()
    rows_to_insert = []
    inserted_count = 0
    for row in data:
        rows_to_insert.append(prepare_row(row))
        if len(rows_to_insert) >= batch_size:
            cursor.executemany(query, rows_to_insert)
            inserted_count += len(rows_to_insert)
            rows_to_insert.clear()

    if rows_to_insert:
        cursor.executemany(query, rows_to_insert)
        inserted_count += len(rows_to_insert)

    lava_db.commit()
    return inserted_count


def _lava_insert_sqlite_data_async(query, data, prepare_row, batch_size, queue_size):
    """
    Insert rows on a writer thread using a separate SQLite connection.
    """
    if not lava_db_path:
        raise RuntimeError("LAVA database has not been initialized")

    batch_queue = queue.Queue(maxsize=queue_size)
    state = {"inserted_count": 0}
    errors = []

    def writer():
        db = sqlite3.connect(lava_db_path)
        cursor = db.cursor()
        try:
            while True:
                batch = batch_queue.get()
                if batch is _QUEUE_STOP:
                    break
                prepared_batch = [prepare_row(row) for row in batch]
                cursor.executemany(query, prepared_batch)
                state["inserted_count"] += len(prepared_batch)

            db.commit()
        except (sqlite3.Error, TypeError, ValueError) as ex:
            errors.append(ex)
            db.rollback()
        finally:
            db.close()

    thread = threading.Thread(target=writer, name="LEAPPLavaArtifactWriter", daemon=True)
    thread.start()

    def put_or_raise(item):
        while True:
            if errors:
                raise errors[0]
            try:
                batch_queue.put(item, timeout=0.1)
                return
            except queue.Full:
                continue

    try:
        batch = []
        for row in data:
            batch.append(row)
            if len(batch) >= batch_size:
                put_or_raise(batch)
                batch = []
        if batch:
            put_or_raise(batch)
        put_or_raise(_QUEUE_STOP)
        thread.join()
        if errors:
            raise errors[0]
        return state["inserted_count"]
    finally:
        if thread.is_alive():
            try:
                batch_queue.put(_QUEUE_STOP, timeout=0.1)
            except queue.Full:
                pass
            thread.join()


def lava_update_record_count(category, tablename, record_count):
    """
    Set an artifact's record count after its rows have been written.

    lava_process_artifact() records the count up front, which assumes the caller counted
    the rows before inserting them. Artifacts streamed straight into SQLite only know the
    total once the stream is exhausted, so they register the artifact first and correct
    the count here.

    Args:
        category (str): The category the artifact was registered under.
        tablename (str): The sanitized table name returned by lava_process_artifact.
        record_count (int): The number of rows actually written.
    """

    for artifact in lava_data["artifacts"].get(category, []):
        if artifact.get("tablename") == tablename:
            artifact["record_count"] = record_count
            return


def lava_update_source_path(category, tablename, source_path):
    """
    Set an artifact's source path after its rows have been written.

    An ArtifactResult registers its LAVA table at the first row it writes, which can be before
    the module knows every file it read. A module that sets the source path once its loop is
    over gets the manifest corrected here, the same way lava_update_record_count corrects the
    count.

    Args:
        category (str): The category the artifact was registered under.
        tablename (str): The sanitized table name returned by lava_process_artifact.
        source_path (str): The extraction-relative source path, newline joined.
    """

    if not source_path:
        return
    for artifact in lava_data["artifacts"].get(category, []):
        if artifact.get("tablename") == tablename:
            artifact["source_path"] = source_path
            return
def lava_discard_artifact(category, tablename):
    """
    Drop a streamed artifact's table and remove it from the manifest.

    An ArtifactResult registers its table and writes rows while the module is still
    running. If the module then raises, the rows already written would otherwise stay
    in the database under a manifest entry with no record count, and the report would
    show a complete-looking table that is short. The run log reports the failure; this
    makes the database and manifest agree with it.

    Args:
        category (str): The category the artifact was registered under.
        tablename (str): The sanitized table name returned by lava_process_artifact.
    """

    cursor = lava_db.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {quote_sql_name(tablename)}")
    lava_db.commit()
    entries = lava_data["artifacts"].get(category)
    if entries is None:
        return
    entries[:] = [a for a in entries if a.get("tablename") != tablename]
    if not entries:
        del lava_data["artifacts"][category]


def lava_commit():
    """Commit the LAVA database.

    The per-row inserts below (media items and references, search patterns, file
    paths and their links) leave their rows in the open transaction; the main loop
    calls this once after each artifact, so a run pays one durable commit per
    artifact instead of one per staged file.
    """
    if lava_db is not None:
        lava_db.commit()


def lava_get_media_item(media_id):
    """
    Retrieve a media item from the lava database by its ID.
    Args:
        media_id (str): The unique identifier of the media item to retrieve.
    Returns:
        sqlite3.Row or None: A row object containing all columns from the _lava_media_items table
    """

    cursor = lava_db.cursor()
    query = "SELECT * FROM _lava_media_items WHERE id = ?"
    return cursor.execute(query, (media_id,)).fetchone()
    # return result.fetchone()


def lava_insert_sqlite_media_item(media_item):
    """
    Insert a media item record into the _lava_media_items SQLite table.
    Args:
        media_item: A media item object containing the following attributes:
            - id: Unique identifier for the media item
            - source_path: Original path of the media file
            - extraction_path: Path where the media was extracted
            - mimetype: MIME type of the media file
            - metadata: Additional metadata about the media item
            - created_at: Timestamp when the item was created (optional)
            - updated_at: Timestamp when the item was last updated (optional)
    Returns:
        None
    """

    cursor = lava_db.cursor()
    sql = '''INSERT INTO _lava_media_items
                ("id", "source_path", "extraction_path", "type", "metadata", "created_at", "updated_at", "is_embedded")
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''

    params = (
        media_item.id,
        str(media_item.source_path),
        str(media_item.extraction_path),
        media_item.mimetype,
        media_item.metadata,
        bind_dates_as_text(media_item.created_at) if media_item.created_at else None,
        bind_dates_as_text(media_item.updated_at) if media_item.updated_at else None,
        media_item.is_embedded
    )

    try:
        cursor.execute(sql, params)
    except sqlite3.IntegrityError as e:
        print(str(e))


def lava_get_media_references(media_ref):
    """
    Retrieves a single media reference record from the _lava_media_references table.
    Args:
        media_ref (str): The ID of the media reference to retrieve.
    Returns:
        tuple or None: A tuple containing the row data if found, None otherwise.
    """

    cursor = lava_db.cursor()
    query = "SELECT * FROM _lava_media_references WHERE id = ?"
    return cursor.execute(query, (media_ref,)).fetchone()


def lava_insert_sqlite_media_references(media_references):
    """
    Insert a media reference record into the _lava_media_references table.
    Args:
        media_references: An object containing media reference data with the following attributes:
            - id: Unique identifier for the media reference
            - media_item_id: ID of the associated media item
            - module_name: Name of the module containing the artifact
            - artifact_name: Name of the artifact
            - name: Name/description of the media reference
            - media_path: File path to the media item
    Returns:
        None
    """

    cursor = lava_db.cursor()
    sql = '''INSERT INTO _lava_media_references
                ("id", "media_item_id", "module_name", "artifact_name", "name")
                VALUES (?, ?, ?, ?, ?)'''

    params = (
        media_references.id,
        media_references.media_item_id,
        media_references.module_name,
        media_references.artifact_name,
        media_references.name
    )
    cursor.execute(sql, params)


def lava_get_full_media_info(media_ref_id):
    """
    Retrieves complete media information for a given media reference ID from the LAVA database.
    This function queries the _lava_media_info table to fetch all columns for a specific
    media item identified by its reference ID. The function uses a global database connection
    and sets the row factory to sqlite3.Row for dictionary-like access to results.
    Args:
        media_ref_id (str): The unique media reference identifier to look up in the database.
    Returns:
        sqlite3.Row or None: A Row object containing all media information fields if found,
                            None if no matching media_ref_id exists in the database.
    """

    lava_db.row_factory = sqlite3.Row
    cursor = lava_db.cursor()
    query = '''
    SELECT *
    FROM _lava_media_info
    WHERE media_ref_id = ?
    '''
    return cursor.execute(query, (media_ref_id,)).fetchone()


def lava_insert_sqlite_artifact_search_pattern(artifact_regex_id, module_name, artifact_name, regex):
    """
    Inserts artifact search pattern into the _artifact_search_patterns table.
    Args:
        artifact_regex_id (str): Unique identifier for the artifact search pattern.
        module_name (str): Name of the module containing the artifact.
        artifact_name (str): Name of the artifact.
        regex (str): The regular expression for the artifact search pattern.
    """

    cursor = lava_db.cursor()
    sql = '''INSERT INTO _artifact_search_patterns
                ("id", "module_name", "artifact_name", "regex")
                VALUES (?, ?, ?, ?)'''

    data = (artifact_regex_id, module_name, artifact_name, regex)

    try:
        cursor.execute(sql, data)
    except sqlite3.IntegrityError as e:
        print(str(e))


def lava_insert_sqlite_file_path(file_id, file_path):
    """
    Insert a file path record into the _file_path_list table.
    Args:
        file_id (int): Unique identifier for the file path entry.
        file_path (str): Relative file path to store.
    """

    cursor = lava_db.cursor()
    sql = '''INSERT INTO _file_path_list
                ("id", "file_path")
                VALUES (?, ?)'''

    data = (file_id, file_path)

    try:
        cursor.execute(sql, data)
    except sqlite3.IntegrityError as e:
        print(str(e))


def lava_insert_sqlite_artifact_link_pattern_to_file(artifact_regex_id, file_id):
    """
    Link an artifact search pattern to a file path entry.
    Args:
        artifact_regex_id (int): ID of the artifact search pattern.
        file_id (int): ID of the related file path entry.
    """

    cursor = lava_db.cursor()
    sql = '''INSERT INTO _artifact_pattern_to_file
                ("artifact_search_pattern_id", "file_path_id")
                VALUES (?, ?)'''

    data = (artifact_regex_id, file_id)

    try:
        cursor.execute(sql, data)
    except sqlite3.IntegrityError as e:
        print(str(e))


def lava_finalize_output(output_path):
    """
    Finalizes the LAVA output by completing data processing and saving results.
    This function performs the following operations:
    1. Sets the processing status to "Complete"
    2. Sorts modules alphabetically by module name
    3. Sorts artifact categories alphabetically
    4. Sorts artifacts within each category alphabetically by name
    5. Saves the LAVA data structure to a JSON file
    6. Closes the SQLite database connection
    Args:
        output_path (str): The directory path where the LAVA JSON output file will be saved
    Global Variables:
        lava_data (dict): Global dictionary containing LAVA processing data including modules,
                          artifacts, and processing status
        lava_db: Global SQLite database connection object
        lava_json_name (str): The filename for the LAVA JSON output file
    """


    lava_data["processing_status"] = "Complete"

    # Sort modules alphabetically
    lava_data["modules"].sort(key=lambda x: x["module_name"])

    # Sort artifacts categories alphabetically
    lava_data["artifacts"] = OrderedDict(sorted(lava_data["artifacts"].items()))

    # Sort artifacts within each category alphabetically
    for category in lava_data["artifacts"]:
        lava_data["artifacts"][category].sort(key=lambda x: x["name"])

    lava_data["parser_info"]["end_timestamp"] = int(datetime.datetime.now(datetime.timezone.utc).timestamp())

    # Save LAVA JSON output
    with open(os.path.join(output_path, lava_json_name), 'w', encoding='utf-8') as f:
        json.dump(lava_data, f, indent=4)

    # Close the SQLite database
    lava_db.commit()
    lava_db.close()
