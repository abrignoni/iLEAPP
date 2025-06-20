import sys
import os
import zipfile
import importlib
import json
from unittest.mock import MagicMock, patch, PropertyMock
from contextlib import ExitStack
from pathlib import Path
from datetime import datetime, timezone, date
import time
from functools import wraps
import shutil
import subprocess
import argparse
import inspect

# Adjust import paths as necessary
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
import scripts.ilapfuncs as ilapfuncs
import scripts.lavafuncs # Import lavafuncs to make its globals patchable
from scripts.context import Context

def mock_logdevinfo(message):
    print(f"[LOGDEVINFO] {message}")

def mock_logfunc(message):
    print(f"[LOGFUNC] {message}")

def process_artifact(zip_path, module_name, artifact_name, artifact_data, target_os_version=None):
    module = importlib.import_module(f'scripts.artifacts.{module_name}')
    
    # Get the function to test
    func_to_test = getattr(module, artifact_name)
    
    # Extract the original function from the decorated one
    original_func = func_to_test
    while hasattr(original_func, '__wrapped__'):
        original_func = original_func.__wrapped__

    # Prepare mock objects
    mock_report_folder = 'mock_report_folder'
    mock_seeker = MagicMock()
    mock_wrap_text = MagicMock()
    timezone_offset = 'UTC'
    
    # <<< NEW COUNTERS >>>
    check_in_media_call_count = 0
    check_in_media_embedded_call_count = 0

    # Capture original functions before patching if we need to call them
    original_check_in_media = ilapfuncs.check_in_media
    original_check_in_media_embedded = ilapfuncs.check_in_embedded_media
    
    # Configure mock_seeker.file_infos.get() to return a mock
    # with a dynamic source_path based on the input extraction_path.
    def mock_file_infos_get_side_effect(key_extraction_path):
        mock_file_info = MagicMock()
        # Use the unique extraction_path (path in temp dir for the test)
        # as the source_path for hashing purposes. In a real run,
        # source_path is the original path in the evidence.
        mock_file_info.source_path = key_extraction_path
        # Provide default datetime objects for creation and modification dates
        mock_file_info.creation_date = datetime.now(timezone.utc)
        mock_file_info.modification_date = datetime.now(timezone.utc)
        return mock_file_info

    mock_seeker.file_infos.get.side_effect = mock_file_infos_get_side_effect
    
    all_files = []
    
    # Create the base temp directory if it doesn't exist
    base_temp_dir = Path('admin/test/temp')
    base_temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a unique temporary directory within the base temp directory
    temp_dir = base_temp_dir / f'extract_{module_name}_{artifact_name}_{int(time.time())}'
    
    # Define mock_report_folder path within the temp_dir and create it
    mock_report_folder_path = temp_dir / 'mock_reports'
    mock_report_folder_path.mkdir(parents=True, exist_ok=True)
    
    # Get the module file path
    module_file_path = module.__file__

    last_commit_info = get_last_commit_info(module_file_path)
    
    try:
        # Extract all files from the zip
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            
            # Recursively get all files
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    all_files.append(os.path.join(root, file))
        
        # Mock for lava_db connection and cursor
        mock_lava_cursor_instance = MagicMock()
        mock_lava_cursor_instance.execute.return_value = mock_lava_cursor_instance
        mock_lava_cursor_instance.fetchone.return_value = None # Simulate media not in LAVA / no specific query result needed for GETs
        mock_lava_cursor_instance.fetchall.return_value = []   # Simulate no results for queries expecting multiple rows

        mock_lava_db_instance = MagicMock()
        mock_lava_db_instance.cursor.return_value = mock_lava_cursor_instance
        mock_lava_db_instance.commit.return_value = None # For any INSERT/UPDATE operations in LAVA functions
        
        # <<< NEW MOCKS FOR CHECK_IN_MEDIA >>>
        def mocked_check_in_media(file_path, *args, **kwargs):
            nonlocal check_in_media_call_count
            check_in_media_call_count += 1
            # Simplified return for counter, avoiding deep side effects of original if problematic
            return f"mock_hash_for_{os.path.basename(str(file_path))}"


        def mocked_check_in_embedded_media(*args, **kwargs):
            nonlocal check_in_media_embedded_call_count
            check_in_media_embedded_call_count += 1
            # Similar to above, call original or return dummy
            return "mock_embedded_html_path"

        def mocked_lava_get_full_media_info(media_ref_id):
            # Return a tuple that mimics the real function's output, needed by some artifacts.
            # The last element should be a Unix timestamp for the modification date.
            # Using Jan 24, 1984 - the day the first Mac went on sale.
            mac_bday_ts = 443750400
            return (
                'mock_media_id',
                'mock_source_path',
                'mock_extraction_path',
                'image/png',
                'mock_metadata',
                mac_bday_ts, # created_at
                mac_bday_ts  # updated_at (modification_date)
            )

        patches = [
            patch('scripts.ilapfuncs.logdevinfo', mock_logdevinfo),
            patch(f'scripts.artifacts.{module_name}.logdevinfo', mock_logdevinfo, create=True),
            patch(f'scripts.artifacts.{module_name}.logfunc', mock_logfunc, create=True),
            patch('scripts.lavafuncs.lava_db', mock_lava_db_instance), # Patch lava_db in the lavafuncs module
            # <<< ADD PATCHES FOR CHECK_IN_MEDIA FUNCTIONS >>>
            # Patch it in ilapfuncs (where it's defined)
            patch('scripts.ilapfuncs.check_in_media', mocked_check_in_media),
            patch('scripts.ilapfuncs.check_in_embedded_media', mocked_check_in_embedded_media),
            # Also patch it directly in the artifact module's namespace if it's imported there like:
            # from scripts.ilapfuncs import check_in_media
            patch(f'scripts.artifacts.{module_name}.check_in_media', mocked_check_in_media, create=True),
            patch(f'scripts.artifacts.{module_name}.check_in_embedded_media', mocked_check_in_embedded_media, create=True),
            patch(f'scripts.artifacts.{module_name}.lava_get_full_media_info', mocked_lava_get_full_media_info, create=True)
        ]
        
        # If a target OS version is provided, mock iOS.get_version()
        if target_os_version:
            mock_ios_get_version = MagicMock(return_value=target_os_version)
            patches.append(patch('scripts.ilapfuncs.iOS.get_version', mock_ios_get_version))

        with ExitStack() as stack:
            for p in patches:
                stack.enter_context(p)
            
            all_artifacts_info = getattr(module, '__artifacts_v2__', {})
            artifact_info = all_artifacts_info.get(artifact_name, {})

            Context.set_report_folder(str(mock_report_folder_path))
            Context.set_seeker(mock_seeker)
            Context.set_files_found(all_files)
            Context.set_artifact_info(artifact_info)
            Context.set_module_name(module_name)
            Context.set_module_file_path(module_file_path)
            Context.set_artifact_name(artifact_name)

            start_time = time.time()
            try:
                sig = inspect.signature(original_func)
                if len(sig.parameters) == 1:
                    data_headers, data_list, _ = original_func(Context)
                else:
                    data_headers, data_list, _ = original_func(all_files, str(mock_report_folder_path), mock_seeker, mock_wrap_text, timezone_offset)
            finally:
                Context.clear()
                
            end_time = time.time()
        
        return data_headers, data_list, end_time - start_time, last_commit_info, check_in_media_call_count, check_in_media_embedded_call_count
    
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)

def calculate_data_size(data_list):
    return sum(len(str(item).encode('utf-8')) for row in data_list for item in row)

def load_test_cases(module_name):
    cases_file = Path(f'admin/test/cases/testdata.{module_name}.json')
    with open(cases_file, 'r') as f:
        return json.load(f)

def get_artifact_names(module_name, test_cases):
    artifact_names = set()
    for case in test_cases.values():
        artifact_names.update(case['artifacts'].keys())
    return list(artifact_names)

def select_case(test_cases):
    print("Available test cases:")
    sorted_cases = sorted(test_cases.keys())
    valid_cases = []
    for i, case_num in enumerate(sorted_cases, 1):
        case_data = test_cases[case_num]
        input_path = case_data.get('make_data', {}).get('input_data_path', 'N/A')
        input_filename = os.path.basename(input_path)
        description = case_data.get('description', 'No description')
        
        # Check if any artifact has files
        has_files = any(artifact.get('file_count', 0) > 0 for artifact in case_data['artifacts'].values())
        
        if has_files:
            valid_cases.append(case_num)
            print(f"{len(valid_cases)}. {case_num}")
            print(f"   Input: {input_filename}")
            print(f"   Description: {description}")
            print()
        else:
            print(f"Skipping case {case_num} (no files found for any artifact)")
    
    if not valid_cases:
        print("No valid test cases found with files.")
        return None

    print("\nEnter case number, name, or press Enter for all cases (Ctrl+C to exit):")
    try:
        case_choice = input().strip().lower()
        if case_choice == '' or case_choice == 'all':
            return 'all'
        try:
            index = int(case_choice) - 1
            if 0 <= index < len(valid_cases):
                return valid_cases[index]
        except ValueError:
            if case_choice in valid_cases:
                return case_choice
        print("Invalid choice. Please try again.")
        return select_case(test_cases)
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

def select_artifact(artifact_names):
    print("Available artifacts:")
    sorted_artifacts = sorted(artifact_names)
    for i, name in enumerate(sorted_artifacts, 1):
        print(f"{i}. {name}")
    
    print("\nEnter artifact number, name, or press Enter for all artifacts (Ctrl+C to exit):")
    try:
        artifact_choice = input().strip().lower()
        if artifact_choice == '' or artifact_choice == 'all':
            return 'all'
        try:
            index = int(artifact_choice) - 1
            if 0 <= index < len(sorted_artifacts):
                return sorted_artifacts[index]
        except ValueError:
            if artifact_choice in sorted_artifacts:
                return artifact_choice
        print("Invalid choice. Please try again.")
        return select_artifact(artifact_names)
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

def convert_to_unix_time(value):
    if isinstance(value, (datetime, date)):
        return int(value.timestamp())
    return value

def process_data(headers, data):
    datetime_indices = [i for i, header in enumerate(headers) if isinstance(header, tuple) and header[1].lower() in ['datetime', 'date']]
    
    processed_headers = [header[0] if isinstance(header, tuple) else header for header in headers]
    processed_data = []
    
    for row in data:
        processed_row = []
        for i, value in enumerate(row):
            if i in datetime_indices:
                processed_row.append(convert_to_unix_time(value))
            elif isinstance(value, (datetime, date)):
                processed_row.append(convert_to_unix_time(value))
            else:
                processed_row.append(value)
        processed_data.append(processed_row)
    
    return processed_headers, processed_data

def main(module_name, artifact_name=None, case_number=None):
    try:
        test_cases = load_test_cases(module_name)
        artifact_names = get_artifact_names(module_name, test_cases)
        
        if artifact_name is None:
            artifact_name = select_artifact(artifact_names)
        elif artifact_name.lower() == 'all':
            artifact_name = 'all'
        
        if case_number is None:
            case_number = select_case(test_cases)
        elif case_number.lower() == 'all':
            case_number = 'all'
        
        if case_number is None:
            print("No valid test cases available. Exiting.")
            return

        cases_to_process = [case_number] if case_number != 'all' else [case for case in test_cases.keys() if any(artifact.get('file_count', 0) > 0 for artifact in test_cases[case]['artifacts'].values())]
        artifacts_to_process = [artifact_name] if artifact_name != 'all' else artifact_names
        
        module = importlib.import_module(f'scripts.artifacts.{module_name}')
        artifacts_info = getattr(module, '__artifacts_v2__', {})
        
        for case in cases_to_process:
            case_data = test_cases[case]
            for artifact in artifacts_to_process:
                if artifact in case_data['artifacts']:
                    artifact_data_for_function = case_data['artifacts'][artifact] # Renamed to avoid conflict
                    
                    if artifact_data_for_function.get('file_count', 0) == 0:
                        print(f"\nSkipping artifact: {artifact} for case: {case} (no files found)")
                        continue

                    print(f"\nTesting artifact: {artifact} for case: {case}")
                    zip_path = Path('admin/test/cases/data') / module_name / f"testdata.{module_name}.{artifact}.{case}.zip"
                    artifact_info_v2 = artifacts_info.get(artifact, {}) # Renamed to avoid conflict
                    start_datetime = datetime.now(timezone.utc)
                    
                    # Extract os_version from case_data
                    current_os_version = case_data.get("os_version")
                    if current_os_version:
                        print(f"Using OS version from test case data for {case}: {current_os_version}")
                    else:
                        print(f"Warning: 'os_version' not found in test case data for {case}. iOS.get_version() will not be specifically mocked.")

                    headers, data, run_time, last_commit_info, media_checkins_count, media_embedded_checkins_count = process_artifact(zip_path, module_name, artifact, artifact_data_for_function, target_os_version=current_os_version)
                    
                    processed_headers, processed_data = process_data(headers, data)
                    
                    end_datetime = datetime.now(timezone.utc)
                    
                    result = {
                        "metadata": {
                            "module_name": module_name,
                            "artifact_name": artifact_info_v2.get('name', artifact),
                            "function_name": artifact,
                            "case_number": case,
                            "number_of_columns": len(processed_headers),
                            "number_of_rows": len(processed_data),
                            "total_data_size_bytes": calculate_data_size(processed_data),
                            "media_checkins": media_checkins_count,
                            "media_embedded_checkins": media_embedded_checkins_count,
                            "input_zip_path": str(zip_path),
                            "start_time": start_datetime.isoformat(),
                            "end_time": end_datetime.isoformat(),
                            "run_time_seconds": run_time,
                            "last_commit": last_commit_info
                        },
                        "headers": processed_headers,
                        "data": processed_data
                    }
                    
                    output_dir = Path('admin/test/results') / module_name
                    output_dir.mkdir(parents=True, exist_ok=True)
                    output_file = output_dir / f"{module_name}.{artifact}.{case}.{start_datetime.strftime('%Y%m%d%H%M%S')}.json"
                    
                    with open(output_file, 'w') as f:
                        json.dump(result, f, indent=2, default=str)
                    
                    print(f"Test results for {module_name} - {artifact} - Case {case} saved to {output_file}")
                    print(f"Processed {len(processed_data)} rows in {run_time:.2f} seconds. Media Checkins: {media_checkins_count}. Media Embedded Checkins: {media_embedded_checkins_count}.")
                else:
                    print(f"\nSkipping artifact: {artifact} for case: {case} (not found in test data)")

        print("\nTesting completed.")

    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

def get_last_commit_info(file_path):
    try:
        # Get the last commit hash
        git_log = subprocess.check_output(['git', 'log', '-n', '1', '--pretty=format:%H|%an|%ae|%ad|%s', '--', file_path], universal_newlines=True)
        commit_hash, author_name, author_email, commit_date, commit_message = git_log.strip().split('|')
        
        # Convert the commit date to ISO format
        commit_date = datetime.strptime(commit_date, '%a %b %d %H:%M:%S %Y %z').isoformat()
        
        return {
            'hash': commit_hash,
            'author_name': author_name,
            'author_email': author_email,
            'date': commit_date,
            'message': commit_message
        }
    except subprocess.CalledProcessError:
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Test module artifacts")
    parser.add_argument("module_name", help="Name of the module to test")
    parser.add_argument("-a", "--artifact", help="Name of the artifact to test (or 'all' for all artifacts)", default=None)
    parser.add_argument("-c", "--case", help="Case number to test (or 'all' for all cases)", default=None)
    
    args = parser.parse_args()
    
    main(args.module_name, args.artifact, args.case)
