"""
Run Image List Test

Script to run the image list test with preconfigured paths and artifacts.
"""
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def run_test():
    """
    Run the image list test with preconfigured paths and artifacts.
    """

    # Get the root directory of the project
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    os.chdir(root_dir)

    # Define paths
    input_path = "admin/test/samples_data"
    output_path = "admin/test/output/"
    output_folder = "image_list_test_" + datetime.now().strftime("%Y%m%d-%H%M%S")
    custom_artifacts_path = "scripts/test_artifacts"

    # Ensure output directory exists
    os.makedirs(output_path, exist_ok=True)

    # Construct the command
    cmd = [
        sys.executable,
        "ileapp.py",
        "-t", "fs",
        "-i", input_path,
        "-o", output_path,
        "--custom_output_folder", output_folder,
        "--custom_artifacts_path", custom_artifacts_path
    ]

    print(f"Running command: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
        print("\nTest completed successfully.")
        print(f"Report should be available in: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"\nError running test: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
