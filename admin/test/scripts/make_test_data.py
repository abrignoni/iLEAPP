import os
import sys
import json
import zipfile
import tarfile
import fnmatch
import argparse
import time
import platform
import subprocess
from datetime import datetime
from collections import defaultdict
from io import BytesIO

# Add the correct path to the system path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(repo_root)

def get_artifact_info(module_name):
    try:
        module = __import__(f'scripts.artifacts.{module_name}', fromlist=['__artifacts_v2__'])
        return module.__artifacts_v2__
    except ImportError:
        print(f"Error: Could not import module 'scripts.artifacts.{module_name}'")
        sys.exit(1)

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

def process_archive(input_file, all_patterns):
    matching_files = defaultdict(dict)
    print(f"Searching for files matching all patterns")
    start_time = time.time()
    local_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Search started at: {local_start_time}")
    #print("Progress: ", end="", flush=True)
    
    file_count = 0
    if input_file.endswith('.zip'):
        with zipfile.ZipFile(input_file, 'r') as zip_ref:
            for file in zip_ref.namelist():
                file_count += 1
                if file_count % 10000 == 0:
                    print(".", end="", flush=True)
                for artifact, patterns in all_patterns.items():
                    for pattern in patterns:
                        if fnmatch.fnmatch(file, pattern):
                            matching_files[artifact][file] = zip_ref.read(file)
                            break
    elif input_file.endswith('.tar.gz') or input_file.endswith('.tgz'):
        print("Processing tar.gz file")
        with tarfile.open(input_file, 'r:gz') as tar_ref:
            print("Searching files\n")
            for member in tar_ref.getmembers():
                file_count += 1
                if file_count % 10000 == 0:
                    print(".", end="", flush=True)
                for artifact, patterns in all_patterns.items():
                    for pattern in patterns:
                        if fnmatch.fnmatch(member.name, pattern):
                            matching_files[artifact][member.name] = tar_ref.extractfile(member).read()
                            break
    elif input_file.endswith('.tar'):
        with tarfile.open(input_file, 'r') as tar_ref:
            for member in tar_ref.getmembers():
                file_count += 1
                if file_count % 10000 == 0:
                    print(".", end="", flush=True)
                for artifact, patterns in all_patterns.items():
                    for pattern in patterns:
                        if fnmatch.fnmatch(member.name, pattern):
                            matching_files[artifact][member.name] = tar_ref.extractfile(member).read()
                            break
    else:
        raise ValueError("Unsupported file format. Please use .zip, tar, or .tar.gz")
    
    print()  # New line after progress dots
    end_time = time.time()
    local_end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Search completed at: {local_end_time}")
    total_matches = sum(len(files) for files in matching_files.values())
    print(f"Searched {file_count} files, found {total_matches} matching files in {end_time - start_time:.2f} seconds")
    return matching_files

def create_test_data(module_name, case_number, input_file):
    overall_start_time = time.time()
    print(f"Processing module: {module_name}")
    artifacts = get_artifact_info(module_name)
    
    # Get git information for the module
    module_path = os.path.join(repo_root, 'scripts', 'artifacts', f'{module_name}.py')
    last_commit_info = get_last_commit_info(module_path)
    
    # Update paths for new folder structure
    cases_dir = os.path.join(repo_root, 'admin', 'test', 'cases')
    data_dir = os.path.join(cases_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    json_file = os.path.join(cases_dir, f"testdata.{module_name}.json")
    
    # Check if JSON file exists and is not empty
    if os.path.exists(json_file) and os.path.getsize(json_file) > 0:
        try:
            with open(json_file, 'r') as f:
                json_data = json.load(f)
            print(f"Updating existing JSON file: {json_file}")
        except json.JSONDecodeError:
            print(f"Existing JSON file is invalid.")
            create_new = input("Do you want to create new JSON data? This will overwrite the existing file. (y/n): ")
            if create_new.lower() != 'y':
                print("Aborting operation.")
                sys.exit(1)
            json_data = {}
    else:
        if os.path.exists(json_file):
            create_new = input(f"JSON file {json_file} is empty. Create new JSON data? (y/n): ")
        else:
            create_new = input(f"JSON file {json_file} does not exist. Create new JSON file? (y/n): ")
        
        if create_new.lower() != 'y':
            print("Aborting operation.")
            sys.exit(1)
        json_data = {}
        print(f"Creating new JSON file: {json_file}")
    
    # Check if case number already exists
    case_key = f"case{case_number:03d}"
    if case_key in json_data:
        overwrite = input(f"Case {case_number} already exists. Do you want to overwrite it? (y/n): ")
        if overwrite.lower() != 'y':
            print("Aborting operation.")
            sys.exit(1)
    
    # Create or update case entry
    json_data[case_key] = {
        "description": "",
        "maker": "",
        "make_data": {
            "input_data_path": os.path.abspath(input_file),
            "os": platform.platform(),
            "timestamp": datetime.now().isoformat(),
            "last_commit": last_commit_info
        },
        "artifacts": {}
    }
    
    # Collect all patterns
    all_patterns = {artifact_name: artifact_info['paths'] for artifact_name, artifact_info in artifacts.items()}
    
    # Process archive and get matching files for all artifacts at once
    matching_files = process_archive(input_file, all_patterns)
    
    for artifact_name, artifact_info in artifacts.items():
        artifact_start_time = time.time()
        local_artifact_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\nProcessing artifact: {artifact_name}")
        print(f"Artifact processing started at: {local_artifact_start_time}")
        
        # Create file name in the new data directory
        file_name = os.path.join(data_dir, f"testdata.{module_name}.{artifact_name}.{case_key}.zip")
        
        # Create zip file with matching files
        zip_start_time = time.time()
        with zipfile.ZipFile(file_name, 'w') as zip_file:
            for file_path, file_content in matching_files[artifact_name].items():
                zip_file.writestr(file_path, file_content)
        zip_end_time = time.time()
        
        # Update JSON data for this artifact
        json_data[case_key]["artifacts"][artifact_name] = {
            "search_patterns": artifact_info['paths'],
            "file_count": len(matching_files[artifact_name]),
            "expected_output": {
                "headers": [],
                "data": []
            }
        }
        
        print(f"Test data created: {file_name}")
        print(f"Added {len(matching_files[artifact_name])} files to the test data")
        #print(f"Zip file creation took {zip_end_time - zip_start_time:.2f} seconds")
        artifact_end_time = time.time()
        local_artifact_end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #print(f"Artifact processing completed at: {local_artifact_end_time}")
        #print(f"Total processing time for {artifact_name}: {artifact_end_time - artifact_start_time:.2f} seconds")
    
    # Write updated JSON data
    json_start_time = time.time()
    with open(json_file, 'w') as f:
        json.dump(json_data, f, indent=2)
    json_end_time = time.time()
    
    print(f"\nJSON file updated: {json_file}")
    print(f"JSON file update took {json_end_time - json_start_time:.2f} seconds")
    print("Please update the JSON file with test case details.")
    
    overall_end_time = time.time()
    local_overall_end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\nTotal processing time: {overall_end_time - overall_start_time:.2f} seconds")
    print(f"Script completed at: {local_overall_end_time}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create test data for artifacts")
    parser.add_argument("module_name", help="Name of the module (e.g., keyboard or keyboard.py)")
    parser.add_argument("case_number", type=int, help="Case number for the test data")
    parser.add_argument("input_file", help="Path to the input file (zip, tar, or tar.gz)")
    
    args = parser.parse_args()
    
    # Remove .py extension if present
    module_name = args.module_name[:-3] if args.module_name.endswith('.py') else args.module_name
    
    script_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Starting test data creation for module: {module_name}, case number: {args.case_number}")
    print(f"Input file: {args.input_file}")
    print(f"Script started at: {script_start_time}")
    
    create_test_data(module_name, args.case_number, args.input_file)
    
    print("\nTest data creation completed.")
