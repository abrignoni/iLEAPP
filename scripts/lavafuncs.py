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
    
    #return lava_data, lava_db

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