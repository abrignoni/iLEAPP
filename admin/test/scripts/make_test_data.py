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
import csv
from io import StringIO
import textwrap
import glob

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

def load_image_manifest():
    manifest_path = os.path.join(repo_root, 'admin', 'image_manifest.json')
    with open(manifest_path, 'r') as f:
        return json.load(f)['images']

def expand_user_path(path):
    return os.path.expanduser(path)

def get_image_info(image_name):
    manifest = load_image_manifest()
    image_data = next((img for img in manifest if img['image_name'] == image_name), None)
    if not image_data:
        raise ValueError(f"Image '{image_name}' not found in manifest")
    
    for path in image_data.get('local_image_paths', []):
        expanded_path = expand_user_path(path)
        if os.path.exists(expanded_path):
            image_data['input_file'] = expanded_path
            return image_data
    
    raise FileNotFoundError(f"No valid path found for image '{image_name}'. Please add your local path to the manifest.")

def read_filepath_list(file_path_list):
    filepath_list = []
    with zipfile.ZipFile(file_path_list, 'r') as zip_ref:
        csv_filename = zip_ref.namelist()[0]  # Assume the first file in the zip is the CSV
        with zip_ref.open(csv_filename) as csvfile:
            csv_content = csvfile.read().decode('utf-8')
            csv_reader = csv.DictReader(StringIO(csv_content))
            for row in csv_reader:
                filepath_list.append(row['path'])
    return filepath_list

def match_files_from_list(filepath_list, patterns):
    matching_files = []
    # Ensure patterns is always a tuple or list
    if isinstance(patterns, str):
        patterns = (patterns,)
    for filepath in filepath_list:
        if any(fnmatch.fnmatch(filepath, pattern) for pattern in patterns):
            matching_files.append(filepath)
    return matching_files

def process_archive(input_file, all_patterns, filepath_list=None):
    matching_files = defaultdict(list if filepath_list else dict)
    file_count = 0
    start_time = time.time()
    local_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Search started at: {local_start_time}")
    
    if filepath_list:
        print(f"Using pre-compiled file path list")
        file_count = len(filepath_list)
        for artifact_name, patterns in all_patterns.items():
            matching_files[artifact_name] = match_files_from_list(filepath_list, patterns)
    else:
        print(f"Searching for files matching all patterns")
        
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

def find_file_in_tar(tar_archive, target_path, tar_filename):
    # Remove the extension from the tar filename
    tar_prefix = os.path.splitext(os.path.basename(tar_filename))[0]
    if tar_prefix.endswith('.tar'):
        tar_prefix = os.path.splitext(tar_prefix)[0]
    
    try:
        prefixed_path = f"{tar_prefix}/{target_path}"
        if tar_archive.getmember(prefixed_path):
            return prefixed_path
    except KeyError:
        pass

    try:
        if tar_archive.getmember(target_path):
            return target_path
    except KeyError:
        pass

    # If both attempts fail, return None
    return None

def create_test_data(module_name, image_name=None, case_number=None, input_file=None):
    overall_start_time = time.time()
    print(f"Processing module: {module_name}")
    artifacts = get_artifact_info(module_name)
    
    # Get git information for the module
    module_path = os.path.join(repo_root, 'scripts', 'artifacts', f'{module_name}.py')
    last_commit_info = get_last_commit_info(module_path)
    
    # Update paths for new folder structure
    cases_dir = os.path.join(repo_root, 'admin', 'test', 'cases')
    data_dir = os.path.join(cases_dir, 'data', module_name)  # Add module_name to the path
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
        json_data = {}
        print(f"Creating new JSON file: {json_file}")
    
    # Use image_name as case_key if provided, otherwise use the given case_number
    case_key = image_name if image_name else f"case{case_number}"
    
    if case_key in json_data:
        overwrite = input(f"Case {case_key} already exists. Do you want to overwrite it? (y/n): ")
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
    
    if image_name:
        json_data[case_key]["image_name"] = image_name
    
    # Collect all patterns
    all_patterns = {artifact_name: artifact_info['paths'] for artifact_name, artifact_info in artifacts.items()}
    
    # Check if file_path_list exists in the image info
    filepath_list = None
    if image_name:
        image_info = get_image_info(image_name)
        if 'file_path_list' in image_info:
            filepath_list_path = os.path.join(repo_root, image_info['file_path_list'])
            if os.path.exists(filepath_list_path):
                print(f"Using file path list: {filepath_list_path}")
                filepath_list = read_filepath_list(filepath_list_path)
            else:
                print(f"Warning: file_path_list specified in manifest does not exist: {filepath_list_path}")

    # Process archive and get matching files for all artifacts at once
    matching_files = process_archive(input_file, all_patterns, filepath_list)
    
    # Open the source archive once
    source_archive = None
    try:
        if input_file.endswith('.zip'):
            source_archive = zipfile.ZipFile(input_file, 'r')
        elif input_file.endswith('.tar.gz') or input_file.endswith('.tgz'):
            source_archive = tarfile.open(input_file, 'r:gz')
        elif input_file.endswith('.tar'):
            source_archive = tarfile.open(input_file, 'r')
        else:
            raise ValueError("Unsupported file format. Please use .zip, .tar, or .tar.gz")

        for artifact_name, artifact_info in artifacts.items():
            artifact_start_time = time.time()
            local_artifact_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\nProcessing artifact: {artifact_name}")
            print(f"Artifact processing started at: {local_artifact_start_time}")
            
            matching_file_count = len(matching_files[artifact_name])
            
            json_data[case_key]["artifacts"][artifact_name] = {
                "search_patterns": artifact_info['paths'],
                "file_count": matching_file_count,
            }
            
            if matching_file_count == 0:
                print(f"No responsive files found for artifact: {artifact_name}")
                json_data[case_key]["artifacts"][artifact_name]["note"] = "No responsive files found for this artifact"
                continue
            
            # Create file name in the new data directory
            file_name = os.path.join(data_dir, f"testdata.{module_name}.{artifact_name}.{case_key}.zip")
            
            # Create zip file with matching files
            zip_start_time = time.time()
            with zipfile.ZipFile(file_name, 'w') as zip_file:
                if isinstance(matching_files[artifact_name], list):
                    # If using filepath_list, we only have file paths
                    for file_path in matching_files[artifact_name]:
                        if isinstance(source_archive, zipfile.ZipFile):
                            if file_path in source_archive.namelist():
                                file_content = source_archive.read(file_path)
                                zip_file.writestr(file_path, file_content)
                            else:
                                print(f"Warning: File not found in zip: {file_path}")
                        else:  # tarfile
                            tar_path = find_file_in_tar(source_archive, file_path, input_file)
                            if tar_path:
                                file_content = source_archive.extractfile(tar_path).read()
                                zip_file.writestr(file_path, file_content)
                            else:
                                print(f"Warning: File not found in tar: {file_path}")
                else:
                    # If processing archive directly, we have file contents
                    for file_path, file_content in matching_files[artifact_name].items():
                        zip_file.writestr(file_path, file_content)
            zip_end_time = time.time()
            
            json_data[case_key]["artifacts"][artifact_name]["expected_output"] = {
                "headers": [],
                "data": []
            }
            
            print(f"Test data created: {file_name}")
            print(f"Added {matching_file_count} files to the test data")
            artifact_end_time = time.time()
            local_artifact_end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if all(artifact.get("file_count", 0) == 0 for artifact in json_data[case_key]["artifacts"].values()):
            print(f"\nNo responsive files found for any artifacts in case {case_key}.")
            json_data[case_key]["note"] = "No responsive files found for any artifacts"
        
        # Write updated JSON data
        json_start_time = time.time()
        with open(json_file, 'w') as f:
            json.dump(json_data, f, indent=2)
        json_end_time = time.time()
        
        print(f"\nJSON file updated: {json_file}")
        print(f"JSON file update took {json_end_time - json_start_time:.2f} seconds")
        print("Please update the JSON file with test case details.")

    finally:
        if source_archive:
            source_archive.close()
    
    overall_end_time = time.time()
    local_overall_end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\nTotal processing time: {overall_end_time - overall_start_time:.2f} seconds")
    print(f"Script completed at: {local_overall_end_time}")

def prompt_for_image(module_name):
    manifest = load_image_manifest()
    print("\nAvailable images:")
    for i, image in enumerate(manifest, 1):
        image_name = image['image_name']
        has_case_data = check_existing_case_data(module_name, image_name)
        case_data_status = "✓ Has case data" if has_case_data else "✗ No case data"
        
        print(f"{i}. {image_name} [{case_data_status}]")
        if 'description' in image:
            wrapped_description = textwrap.wrap(image['description'], width=70, initial_indent='   ', subsequent_indent='   ')
            print('\n'.join(wrapped_description))
        print()

    while True:
        try:
            choice = int(input("Enter the number of the image you want to use: "))
            if 1 <= choice <= len(manifest):
                return manifest[choice - 1]['image_name']
            else:
                print("Invalid choice. Please enter a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def check_existing_case_data(module_name, image_name):
    cases_dir = os.path.join(repo_root, 'admin', 'test', 'cases', 'data', module_name)
    pattern = f"testdata.*.{image_name}.zip"
    existing_files = glob.glob(os.path.join(cases_dir, pattern))
    return len(existing_files) > 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create test data for artifacts")
    parser.add_argument("module_name", help="Name of the module (e.g., keyboard or keyboard.py)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--image", help="Name of the image from the manifest")
    group.add_argument("--case", help="Case number for the test data")
    group.add_argument("--image-prompt", action="store_true", help="Prompt for image selection from the manifest")
    parser.add_argument("--input", help="Path to the input file (zip, tar, or tar.gz)", required='--case' in sys.argv)
    
    args = parser.parse_args()
    
    # Remove .py extension if present
    module_name = args.module_name[:-3] if args.module_name.endswith('.py') else args.module_name
    
    script_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Starting test data creation for module: {module_name}")
    print(f"Script started at: {script_start_time}")
    
    if args.image_prompt:
        selected_image = prompt_for_image(module_name)
        args.image = selected_image
    
    if args.image:
        try:
            image_info = get_image_info(args.image)
            print(f"Using image: {args.image}")
            print(f"Image path: {image_info['input_file']}")
            
            # Check if case data already exists
            if check_existing_case_data(module_name, args.image):
                print(f"Note: Case data already exists for module '{module_name}' using image '{args.image}'.")
                proceed = input("Do you want to proceed and potentially overwrite existing data? (y/n): ")
                if proceed.lower() != 'y':
                    print("Operation aborted.")
                    sys.exit(0)
            
            create_test_data(module_name, image_name=args.image, input_file=image_info['input_file'])
        except (ValueError, FileNotFoundError) as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        if not args.input:
            parser.error("--input is required when --case is used")
        print(f"Using case number: {args.case}")
        print(f"Input file: {args.input}")
        create_test_data(module_name, case_number=args.case, input_file=args.input)
    
    print("\nTest data creation completed.")
