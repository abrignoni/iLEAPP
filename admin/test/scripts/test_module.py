import sys
import os
import zipfile
import importlib
import json
from unittest.mock import MagicMock
from pathlib import Path
from datetime import datetime, timezone
import time
from functools import wraps
import shutil
import subprocess

# Adjust import paths as necessary
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
import scripts.ilapfuncs as ilapfuncs

def mock_environment():
    # Create mock objects for things we want to fake
    mock_seeker = MagicMock()
    mock_wrap_text = MagicMock()
    
    # You might need to add more mocked objects or functions here
    
    return mock_seeker, mock_wrap_text

def process_artifact(zip_path, module_name, artifact_name, artifact_data):
    # Import the module
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
    
    # Prepare a list to hold all files
    all_files = []
    
    # Create the base temp directory if it doesn't exist
    base_temp_dir = Path('admin/test/temp')
    base_temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a unique temporary directory within the base temp directory
    temp_dir = base_temp_dir / f'extract_{module_name}_{artifact_name}_{int(time.time())}'
    
    # Get the module file path
    module_file_path = module.__file__

    # Get the last commit information
    last_commit_info = get_last_commit_info(module_file_path)
    
    try:
        # Extract all files from the zip
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            
            # Recursively get all files
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    all_files.append(os.path.join(root, file))
        
        # Call the original function directly
        start_time = time.time()
        data_headers, data_list, _ = original_func(all_files, mock_report_folder, mock_seeker, mock_wrap_text, timezone_offset)
        end_time = time.time()
        
        return data_headers, data_list, end_time - start_time, last_commit_info
    
    finally:
        # Clean up temp directory
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
    print("Available cases:")
    sorted_cases = sorted(test_cases.keys())
    for i, case_num in enumerate(sorted_cases, 1):
        case_data = test_cases[case_num]
        print(f"{i}. {case_num}: {case_data.get('description', 'No description')}")
    
    while True:
        case_choice = input("Enter case number, name, or 'all' for all cases: ").strip().lower()
        if case_choice == 'all':
            return 'all'
        try:
            index = int(case_choice) - 1
            if 0 <= index < len(sorted_cases):
                return sorted_cases[index]
        except ValueError:
            if case_choice in test_cases:
                return case_choice
        print("Invalid choice. Please try again.")

def select_artifact(artifact_names):
    print("Available artifacts:")
    sorted_artifacts = sorted(artifact_names)
    for i, name in enumerate(sorted_artifacts, 1):
        print(f"{i}. {name}")
    
    while True:
        artifact_choice = input("Enter artifact number, name, or 'all' for all artifacts: ").strip().lower()
        if artifact_choice == 'all':
            return 'all'
        try:
            index = int(artifact_choice) - 1
            if 0 <= index < len(sorted_artifacts):
                return sorted_artifacts[index]
        except ValueError:
            if artifact_choice in sorted_artifacts:
                return artifact_choice
        print("Invalid choice. Please try again.")

def main(module_name, artifact_name=None, case_number=None):
    test_cases = load_test_cases(module_name)
    artifact_names = get_artifact_names(module_name, test_cases)
    
    if not artifact_name:
        artifact_name = select_artifact(artifact_names)
    
    if not case_number:
        case_number = select_case(test_cases)
    
    cases_to_process = [case_number] if case_number != 'all' else test_cases.keys()
    artifacts_to_process = [artifact_name] if artifact_name != 'all' else artifact_names
    
    module = importlib.import_module(f'scripts.artifacts.{module_name}')
    artifacts_info = getattr(module, '__artifacts_v2__', {})
    
    for case in cases_to_process:
        case_data = test_cases[case]
        zip_path = Path('admin/test/cases/data') / f"testdata.{module_name}.{artifact_name}.{case}.zip"
        
        for artifact in artifacts_to_process:
            if artifact in case_data['artifacts']:
                artifact_data = case_data['artifacts'][artifact]
                artifact_info = artifacts_info.get(artifact, {})
                start_datetime = datetime.now(timezone.utc)
                headers, data, run_time, last_commit_info = process_artifact(zip_path, module_name, artifact, artifact_data)
                end_datetime = datetime.now(timezone.utc)
                
                result = {
                    "metadata": {
                        "module_name": module_name,
                        "artifact_name": artifact_info.get('name', artifact),
                        "function_name": artifact,
                        "case_number": case,
                        "number_of_columns": len(headers),
                        "number_of_rows": len(data),
                        "total_data_size_bytes": calculate_data_size(data),
                        "input_zip_path": str(zip_path),
                        "start_time": start_datetime.isoformat(),
                        "end_time": end_datetime.isoformat(),
                        "run_time_seconds": run_time,
                        "last_commit": last_commit_info
                    },
                    "headers": headers,
                    "data": data
                }
                
                output_dir = Path('admin/test/results')
                output_dir.mkdir(parents=True, exist_ok=True)
                output_file = output_dir / f"{module_name}_{artifact}_{case}_{start_datetime.strftime('%Y%m%d%H%M%S')}.json"
                
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
                
                print(f"Test results for {module_name} - {artifact} - Case {case} saved to {output_file}")

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
    if len(sys.argv) < 2:
        print("Usage: python test_module.py <module_name> [artifact_name] [case_number]")
        sys.exit(1)
    
    module_name = sys.argv[1]
    artifact_name = sys.argv[2] if len(sys.argv) > 2 else None
    case_number = sys.argv[3] if len(sys.argv) > 3 else None
    
    main(module_name, artifact_name, case_number)
