import json
import sqlite3
import os
from collections import OrderedDict
import re
import datetime

# Global variables
lava_data = None
lava_db = None

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
    global lava_data, lava_db
    
    lava_data = {
        "param_input": input_path,
        "param_output": output_path,
        "param_type": input_type,
        "processing_status": "In Progress",
        "modules": [],
        "artifacts": OrderedDict()
    }
    
    db_path = os.path.join(output_path, '_lava_artifacts.db')
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
                            lmi.updated_at 
                        FROM _lava_media_references as lmr 
                        LEFT JOIN _lava_media_items as lmi ON lmr.media_item_id = lmi.id''')
    
def lava_process_artifact(category, module_name, artifact_name, data, record_count=None, data_views=None):
    global lava_data
    
    if category not in lava_data["artifacts"]:
        lava_data["artifacts"][category] = []
    
    sanitized_table_name, column_map, object_columns = lava_create_sqlite_table(artifact_name, data)

    artifact = {
        "name": artifact_name,
        "tablename": sanitized_table_name,
        "module": module_name,
        "column_map": column_map
    }
    if record_count is not None:
        artifact["record_count"] = record_count
    if object_columns:
        artifact["object_columns"] = [{"name": name, "type": type_} for name, type_ in object_columns.items()]

    if data_views:
        if chat_params := data_views.get("chat"):
            sanitized_params = {}

            #Boolean value is whether or not to sanitize the column name. Should do this for parameters that map to columns
            keys = {
                "directionSentValue": False,
                "threadDiscriminatorColumn": True,
                "threadLabelColumn": True,
                "textColumn": True,
                "directionColumn": True,
                "timeColumn": True,
                "senderColumn": True,
                "mediaColumn": True,
                "sentMessageLabelColumn": True,
                "sentMessageStaticLabel": False
            }

            for (key, value) in chat_params.items():
                if key in keys:
                    if keys[key]:
                        sanitized_params[key] = sanitize_sql_name(value)
                    else:
                        sanitized_params[key] = value

            data_views["chat"] = sanitized_params

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
            original_name, data_type = item
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
        for i, column in enumerate(headers):
            original_column = column[0] if isinstance(column, tuple) else column
            sanitized_column = sanitize_sql_name(original_column)
            value = row[i]
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
    global lava_db
    cursor = lava_db.cursor()
    query = f"SELECT * FROM _lava_media_references WHERE id='{media_ref}'"
    return cursor.execute(query).fetchone()

def lava_insert_sqlite_media_references(media_references):
    global lava_db
    cursor = lava_db.cursor()
    cursor.execute(f'''INSERT INTO _lava_media_references 
                ("id", "media_item_id", "module_name", "artifact_name", "name")
                VALUES ("{media_references.id}", "{media_references.media_item_id}", 
                "{media_references.module_name}", "{media_references.artifact_name}", 
                "{media_references.name}")''')
    lava_db.commit()

def lava_get_full_media_info(media_ref_id):
    global lava_db
    cursor = lava_db.cursor()
    query = f'''
    SELECT *
    FROM _lava_media_info
    WHERE media_ref_id = '{media_ref_id}'
    '''
    return cursor.execute(query).fetchone()

def lava_finalize_output(output_path):
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
    with open(os.path.join(output_path, '_lava_data.json'), 'w') as f:
        json.dump(lava_data, f, indent=4)
    
    # Close the SQLite database
    lava_db.close()