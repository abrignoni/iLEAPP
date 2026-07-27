"""
Text file data source for Leapp.
This module provides functionality to load and save text files.
"""


def get_txt_file_content(file_path, line_by_line=False):
    """
    Load a text file and return its content.
    Args:
        file_path (str|Path): The path to the text file.
        line_by_line (bool): If True, return a list of lines;
            otherwise, return the entire content as a single string.
    Returns:
        list or str: The content of the text file.
        If an error occurs, an empty list or string is returned.

    """
    try:
        with open(file_path, "r", encoding="utf-8") as txt_file:
            if line_by_line:
                return txt_file.readlines()
            return txt_file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except PermissionError:
        print(f"Error: Permission denied when trying to read '{file_path}'")
    except IsADirectoryError:
        print(f"Error: Expected a file but found a directory at '{file_path}'.")
    except UnicodeDecodeError as e:
        print(f"Error: Encoding issue reading '{file_path}': {e}")
    except OSError as e:
        print(f"Error: System error related to the file, disk, or path: {e}")
    return [] if line_by_line else ""
