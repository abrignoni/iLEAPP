"""Create and load LEAPP case data files."""

from pathlib import Path
from leapps.functions.data_sources.json_files import save_content_to_json_file, get_json_file_content


def create_casedata(leapp, path):
    """Collect case metadata from user input and write it to a case data file."""
    case_data_values = {}
    print("--- LEAPP Case Data file creation ---\n")
    print("Enter the following information:")
    case_data_values["Case Number"] = input("Case Number: ")
    case_data_values["Agency"] = input("Agency: ")
    case_data_values["Examiner"] = input("Examiner : ")
    print()
    case_data_filename = ""
    while not case_data_filename:
        case_data_filename = input("Enter the name of the Case Data file: ")
    case_data_filename += leapp.casedata_extension
    filename = Path(path).joinpath(case_data_filename)
    json_data = {"leapp": "case_data", "case_data_values": case_data_values}
    save_content_to_json_file(filename, json_data)
    print("\nCase Data file saved:", filename)
    print()


def load_casedata(case_data_path):
    """Load and validate a LEAPP case data JSON file.

    Returns the ``case_data_values`` dictionary when valid, otherwise an empty
    dictionary.
    """
    case_data_path = Path(case_data_path)
    case_data_load_error = None
    case_data = get_json_file_content(case_data_path)

    if case_data:
        if isinstance(case_data, dict):
            if case_data.get("leapp") != "case_data":
                case_data_load_error = "File was not a valid case data file"
                print(case_data_load_error)
                return {}
            print(f"Case Data loaded: {case_data_path}")
            return case_data.get("case_data_values", {})
        case_data_load_error = "File was not a valid case data file: invalid format"
        print(case_data_load_error)
        return {}
