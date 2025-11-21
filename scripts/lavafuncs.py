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
    get_sql_type: Maps Python types to SQL types.
    initialize_lava: Initializes the LAVA data structure and database.
    lava_process_artifact: Processes and stores artifact data.
    lava_add_module: Adds module information to the LAVA data.
    lava_create_sqlite_table: Creates a SQLite table for artifact data.
    lava_insert_sqlite_data: Inserts data rows into a SQLite table.
    lava_get_media_item: Retrieves media item information from database.
    lava_insert_sqlite_media_item: Inserts media item metadata into database.
    lava_get_media_references: Retrieves media reference information.
    lava_insert_sqlite_media_references: Inserts media reference into database.
    lava_get_full_media_info: Retrieves complete media information with joins.
    lava_finalize_output: Finalizes and saves LAVA output files.
"""

import json
import sqlite3
import os
from collections import OrderedDict
import re
import datetime

from scripts.context import Context

# Global variables
lava_data = None
lava_db = None
lava_db_name = '_lava_artifacts.db'
lava_json_name = '_lava_data.lava'


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
        'date': 'INTEGER',
    }
    return type_map.get(python_type, 'TEXT')


def initialize_lava(input_path, output_path, input_type):
    '''
    Initialize the LAVA data.
    Args:
        input_path: The path to the input file.
        output_path: The path to the output file.
        input_type: The type of input file.
    '''

    global lava_data, lava_db

    lava_data = {
        "param_input": input_path,
        "param_output": output_path,
        "param_type": input_type,
        "processing_status": "In Progress",
        "lava_db_name": lava_db_name,
        "modules": [],
        "artifacts": OrderedDict(),
        "meta": {
            "modules": []
        }
    }

    db_path = os.path.join(output_path, lava_db_name)
    lava_db = sqlite3.connect(db_path)

    cursor = lava_db.cursor()
    cursor.execute('''CREATE TABLE _lava_media_items (
                        id TEXT PRIMARY KEY,
                        source_path TEXT,
                        extraction_path TEXT,
                        type TEXT,
                        metadata TEXT,
                        created_at INTEGER,
                        updated_at INTEGER)''')
    cursor.execute('''CREATE TABLE _lava_media_references (
                        id TEXT PRIMARY KEY,
                        media_item_id TEXT,
                        module_name TEXT,
                        artifact_name TEXT,
                        name TEXT,
                        media_path TEXT,
                        FOREIGN KEY (media_item_id) REFERENCES _lava_media_items(id))''')
    cursor.execute('''CREATE VIEW _lava_media_info AS
                        SELECT
                            lmr.id as 'media_ref_id',
                            lmr.media_item_id,
                            lmr.module_name,
                            lmr.artifact_name,
                            lmr.name,
                            lmr.media_path,
                            lmi.source_path,
                            lmi.extraction_path,
                            lmi.type,
                            lmi.metadata,
                            lmi.created_at,
                            lmi.updated_at
                        FROM _lava_media_references as lmr
                        LEFT JOIN _lava_media_items as lmi ON lmr.media_item_id = lmi.id''')


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
    global lava_data

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

                # Sanitize value if it's a column name, otherwise pass through
                if value in column_names:
                    sanitized_params[final_key] = sanitize_sql_name(value)
                else:
                    sanitized_params[final_key] = value

            data_views["conversation"] = sanitized_params

        artifact['data_views'] = data_views

    lava_data["artifacts"][category].append(artifact)

    return sanitized_table_name, object_columns, column_map


def lava_add_module(module_name, module_status, file_count=None):
    """
    Adds a module to the global lava_data structure.
    Parameters:
        module_name (str): The name of the module to be added.
        module_status (str): The status of the module (e.g., 'active', 'inactive').
        file_count (int, optional): The number of files associated with the module. Defaults to None.
    Returns:
        None
    Global Variables:
        lava_data (dict): A global dictionary that contains a list of modules under the key 'modules'.
    """

    global lava_data

    module = {
        "module_name": module_name,
        "module_status": module_status
    }
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
    global lava_db

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
            columns.append(f"{sanitized_name} {sql_type}")
            object_columns[sanitized_name] = data_type
        else:
            original_name = item
            sanitized_name = sanitize_sql_name(original_name)
            columns.append(f"{sanitized_name} TEXT")

        column_map[sanitized_name] = original_name

    columns_sql = ', '.join(columns)
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {sanitized_table_name} ({columns_sql})")
    lava_db.commit()

    return sanitized_table_name, column_map, object_columns


def lava_insert_sqlite_data(table_name, data, object_columns, headers, column_map):
    """
    Insert data into a SQLite database table with automatic column sanitization and type conversion.
    This function handles the insertion of multiple rows of data into a specified SQLite table,
    with special handling for complex data types (dict, list) and datetime conversions.
    Args:
        table_name (str): The name of the SQLite table to insert data into.
        data (list): A list of rows to insert, where each row is a sequence of values
                     corresponding to the headers.
        object_columns (dict): A dictionary mapping column names to their data types.
                              Supports 'datetime' type for automatic timestamp conversion.
        headers (list): A list of column headers. Each header can be a string or a tuple
                       where the first element is the column name.
        column_map (dict): Column mapping configuration (currently unused in the function).
    Returns:
        None
    """

    global lava_db

    if not data:
        return

    cursor = lava_db.cursor()

    # Use the sanitized column names directly
    sanitized_columns = [sanitize_sql_name(h[0] if isinstance(h, tuple) else h) for h in headers]

    # Prepare the SQL query
    placeholders = ', '.join(['?' for _ in sanitized_columns])
    query = f"INSERT INTO {table_name} ({', '.join(sanitized_columns)}) VALUES ({placeholders})"

    # Prepare the data for insertion
    rows_to_insert = []
    for row in data:
        processed_row = []
        for sanitized_column, value in zip(sanitized_columns, row):
            if isinstance(value, dict) or isinstance(value, list):
                value = json.dumps(value)
            if sanitized_column in object_columns and object_columns[sanitized_column] == 'datetime':
                # Convert datetime to integer (Unix timestamp)
                if isinstance(value, str):
                    try:
                        dt = datetime.datetime.fromisoformat(value)
                        value = int(dt.timestamp())
                    except ValueError:
                        # If conversion fails, keep the original value
                        pass
                elif isinstance(value, datetime.datetime):
                    value = int(value.timestamp())
            processed_row.append(value)
        rows_to_insert.append(tuple(processed_row))

    # Execute the insert
    cursor.executemany(query, rows_to_insert)
    lava_db.commit()


def lava_get_media_item(media_id):
    """
    Retrieve a media item from the lava database by its ID.
    Args:
        media_id (str): The unique identifier of the media item to retrieve.
    Returns:
        sqlite3.Row or None: A row object containing all columns from the _lava_media_items table
    """

    global lava_db
    cursor = lava_db.cursor()
    query = f"SELECT * FROM _lava_media_items WHERE id='{media_id}'"
    return cursor.execute(query).fetchone()
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

    global lava_db
    created_at = media_item.created_at if media_item.created_at else 'NULL'
    updated_at = media_item.updated_at if media_item.updated_at else 'NULL'
    cursor = lava_db.cursor()
    try:
        cursor.execute(f'''INSERT INTO _lava_media_items
                    ("id", "source_path", "extraction_path", "type", "metadata", "created_at", "updated_at")
                    VALUES ("{media_item.id}", "{media_item.source_path}", "{media_item.extraction_path}",
                    "{media_item.mimetype}", "{media_item.metadata}", {created_at}, {updated_at})''')
        lava_db.commit()
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

    global lava_db
    cursor = lava_db.cursor()
    query = f"SELECT * FROM _lava_media_references WHERE id='{media_ref}'"
    return cursor.execute(query).fetchone()


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

    global lava_db
    cursor = lava_db.cursor()
    cursor.execute(f'''INSERT INTO _lava_media_references
                ("id", "media_item_id", "module_name", "artifact_name", "name", "media_path")
                VALUES ("{media_references.id}", "{media_references.media_item_id}",
                "{media_references.module_name}", "{media_references.artifact_name}",
                "{media_references.name}", "{media_references.media_path}")''')
    lava_db.commit()


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

    global lava_db
    lava_db.row_factory = sqlite3.Row
    cursor = lava_db.cursor()
    query = f'''
    SELECT *
    FROM _lava_media_info
    WHERE media_ref_id = '{media_ref_id}'
    '''
    return cursor.execute(query).fetchone()


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

    global lava_data, lava_db

    lava_data["processing_status"] = "Complete"

    # Sort modules alphabetically
    lava_data["modules"].sort(key=lambda x: x["module_name"])

    # Sort artifacts categories alphabetically
    lava_data["artifacts"] = OrderedDict(sorted(lava_data["artifacts"].items()))

    # Sort artifacts within each category alphabetically
    for category in lava_data["artifacts"]:
        lava_data["artifacts"][category].sort(key=lambda x: x["name"])

    # Save LAVA JSON output
    with open(os.path.join(output_path, lava_json_name), 'w', encoding='utf-8') as f:
        json.dump(lava_data, f, indent=4)

    # Close the SQLite database
    lava_db.close()
