import sys
import os
import zipfile
import importlib
import json
from unittest.mock import MagicMock
from pathlib import Path
from datetime import datetime, timezone
import time

# Adjust import paths as necessary
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
import scripts.ilapfuncs as ilapfuncs

def mock_environment():
    # Create mock objects for things we want to fake
    mock_seeker = MagicMock()
    mock_wrap_text = MagicMock()
    
    # You might need to add more mocked objects or functions here
    
    return mock_seeker, mock_wrap_text

def process_zip(zip_path, module_name):
    # Extract the module's processing function
    module = importlib.import_module(f'scripts.artifacts.{module_name}')
    process_func = getattr(module, f'get_{module_name}')
    
    # Set up mocked environment
    mock_seeker, mock_wrap_text = mock_environment()
    
    # Prepare a list to hold all files
    all_files = []
    
    # Extract all files from the zip
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        temp_dir = Path('temp_extract')
        zip_ref.extractall(temp_dir)
        
        # Recursively get all files
        for root, _, files in os.walk(temp_dir):
            for file in files:
                all_files.append(os.path.join(root, file))
    
    # Call the module's processing function
    start_time = time.time()
    data_headers, data_list, _ = process_func(all_files, 'test_report', mock_seeker, mock_wrap_text, 'UTC')
    end_time = time.time()
    
    # Clean up temp directory
    for file in all_files:
        os.remove(file)
    os.rmdir(temp_dir)
    
    return data_headers, data_list, end_time - start_time

def calculate_data_size(data_list):
    return sum(len(str(item).encode('utf-8')) for row in data_list for item in row)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python test_module.py <module_name> <zip_file_path>")
        sys.exit(1)
    
    module_name = sys.argv[1]
    zip_path = sys.argv[2]
    
    start_datetime = datetime.now(timezone.utc)
    headers, data, run_time = process_zip(zip_path, module_name)
    end_datetime = datetime.now(timezone.utc)
    
    result = {
        "metadata": {
            "module_name": module_name,
            "function_name": f"get_{module_name}",
            "number_of_columns": len(headers),
            "number_of_rows": len(data),
            "total_data_size_bytes": calculate_data_size(data),
            "input_zip_path": os.path.abspath(zip_path),
            "start_time": start_datetime.isoformat(),
            "end_time": end_datetime.isoformat(),
            "run_time_seconds": run_time
        },
        "headers": headers,
        "data": data
    }
    
    output_dir = Path('/admin/test/results')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{module_name}_get_{module_name}_{start_datetime.strftime('%Y%m%d%H%M%S')}.json"
    
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Test results saved to {output_file}")