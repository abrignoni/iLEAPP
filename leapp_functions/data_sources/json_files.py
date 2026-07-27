"""
JSON file data source for Leapp.
This module provides functionality to load and save JSON files,
and convert a JSON file into namedtuples for easier access to its contents.
"""

import json


def get_json_file_content(file_path):
    """
    Load a JSON file and return its content as a dictionary.
    Args:
        file_path (str|Path): The path to the JSON file.
    Returns:
        dict: The content of the JSON file as a dictionary. If an error occurs, an empty dictionary is returned.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors='replace') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        print(f"Error: JSON file '{file_path}' not found.")
    except PermissionError:
        print(f"Error: Permission denied when trying to read '{file_path}'.")
    except IsADirectoryError:
        print(f"Error: Expected a file but found a directory at '{file_path}'.")
    except OSError as e:
        print(f"Error: System error related to the file, disk, or path: {e}")
    except json.JSONDecodeError as e:
        print(f"Error: JSON file '{file_path}' malformed: {str(e)}")
    except UnicodeDecodeError as e:
        print(f"Error: Encoding issue reading '{file_path}': {e}")
    except RecursionError as e:
        print(f"Error: JSON structure too deep to parse in '{file_path}': {e}")
    return {}
