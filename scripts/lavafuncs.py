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
    # Remove non-alphanumeric characters and replace spaces with underscores
    sanitized = re.sub(r'[^\w\s]', '', name)
    sanitized = re.sub(r'\s+', '_', sanitized)
    # Ensure the name starts with a letter or underscore
    if sanitized and not sanitized[0].isalpha() and sanitized[0] != '_':
        sanitized = '_' + sanitized
    return sanitized.lower()

def get_sql_type(python_type):
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

def lava_process_artifact(
    category,
    module_name,
    artifact_name,
    data,
    record_count=None,
    data_views=None,
    artifact_icon=None,
    source_path=None):

    '''
    Process an artifact and add it to the LAVA data.
    Args:
        category: The category of the artifact.
        module_name: The name of the module that processed the artifact.
        artifact_name: The name of the artifact.
        data: The data of the artifact.
        record_count: The number of records in the artifact.
        data_views: The data views of the artifact.
        artifact_icon: The icon of the artifact.
        source_path: The source path of the artifact.
    '''
    global lava_data

    if category not in lava_data["artifacts"]:
        lava_data["artifacts"][category] = []

    sanitized_table_name, column_map, object_columns = lava_create_sqlite_table(artifact_name, data)

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
        view_name = None

        # Backward compatibility for chat view. Remove 'chat' once modules are updated.
        if "chat" in data_views:
            view_name = "chat"
            view_params = data_views.pop("chat")
            data_views["conversation"] = view_params # Upgrade to conversation
        elif "conversation" in data_views:
            view_name = "conversation"
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
    global lava_data
    
    module = {
        "module_name": module_name,
        "module_status": module_status
    }
    if file_count is not None:
        module["file_count"] = file_count
    lava_data["modules"].append(module)

def lava_create_sqlite_table(table_name, data):
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
    '''Returns a MediaItem object containing info of the media_id item stored  
    in the media_items table if exists or return None '''
    global lava_db
    cursor = lava_db.cursor()
    query = f"SELECT * FROM _lava_media_items WHERE id='{media_id}'"
    return cursor.execute(query).fetchone()
    # return result.fetchone()

def lava_insert_sqlite_media_item(media_item):
    global lava_db
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
        media_item.created_at if media_item.created_at else None,
        media_item.updated_at if media_item.updated_at else None,
        media_item.is_embedded
    )

    try:
        cursor.execute(sql, params)
        lava_db.commit()
    except sqlite3.IntegrityError as e:
        print(str(e))

def lava_get_media_references(media_ref):
    global lava_db
    cursor = lava_db.cursor()
    query = f"SELECT * FROM _lava_media_references WHERE id='{media_ref}'"
    return cursor.execute(query).fetchone()

def lava_insert_sqlite_media_references(media_references):
    global lava_db
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
    lava_db.commit()

def lava_get_full_media_info(media_ref_id):
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
    '''
    Finalize the LAVA output.
    Args:
        output_path: The path to the output file.
    '''
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
