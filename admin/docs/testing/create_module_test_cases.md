# Creating Module Test Cases

This document describes the process of creating test cases for LEAPP modules using the `make_test_data.py` script.

## Overview

The `make_test_data.py` script is designed to generate test data for LEAPP modules. It processes input files (zip, tar, or tar.gz) to extract relevant files based on the module's artifact patterns and creates structured test cases.

## Usage

To create test cases for a module, use one of the following commands:

```bash
python make_test_data.py <module_name> --image <image_name>
python make_test_data.py <module_name> --case <case_number> --input <input_file>
python make_test_data.py <module_name> --image-prompt
```

Arguments:
- `<module_name>`: Name of the module (e.g., keyboard or keyboard.py)
- `--image <image_name>`: Name of the image from the manifest
- `--case <case_number>`: Case number for the test data
- `--input <input_file>`: Path to the input file (zip, tar, or tar.gz)
- `--image-prompt`: Prompt for image selection from the manifest

## Process

1. The script imports the specified module and retrieves artifact information.
2. It creates or updates a JSON file with test case metadata.
3. The script processes the input archive file, searching for files matching the artifact patterns.
4. For each artifact, it creates a zip file containing the matching files.
5. The JSON file is updated with information about the created test data.

## Output

The script generates the following outputs:

1. A JSON file containing test case metadata.
    - `admin/test/cases/testdata.<module_name>.json`
2. Zip files for each artifact, containing the relevant test data files.
    - `admin/test/cases/data/testdata.<module_name>.<artifact_name>.<case_key>.zip`

## Example

```bash
python make_test_data.py keyboard --image ios_15_image
```

This command will create test data for the keyboard module, using the specified image from the manifest.

## Notes

- The script supports zip, tar, and tar.gz input files.
- Test data is stored in the `admin/test/cases/data` directory.
- JSON metadata files are stored in the `admin/test/cases` directory.
- Always review and update the generated JSON file with additional test case details as needed.

## Test Case JSON File Structure

The script generates a JSON file (e.g., `testdata.<module_name>.json`) that contains metadata and information about the test cases. This file is crucial for defining the scenarios that `test_module.py` will execute. Here's an explanation of its structure:

```json
{
  "case_ios12_basic": {
    "description": "Tests basic data extraction for iOS 12.x.",
    "maker": "Your Name",
    "os_name": "iOS",
    "os_version": "12.5.5",
    "make_data": {
      "input_data_path": "/path/to/iOS12_image.tar.gz",
      "os": "macOS-14.0-...",
      "timestamp": "2024-10-14T10:17:49.432528",
      "last_commit": {
          "hash": "abcdef123...",
      }
    },
    "artifacts": {
      "get_photosMetadata": {
        "search_patterns": [
          "*/mobile/Media/PhotoData/Photos.sqlite*"
        ],
        "file_count": 1
      },
      "another_artifact_function_if_any": {
      }
    }
  }
}
```

- `case_ios12_basic`: A unique identifier for each test case. This key is used by `test_module.py` to find the corresponding input data ZIP and golden file.
  - `description`: A brief description of what this test case covers (to be filled in manually).
  - `maker`: The person who created or last verified the test case (to be filled in manually).
  - `os_name`: Include the name of the operating system this case data originated from (iOS, Android, etc)
  - `os_version`: The specific OS version string (e.g., "12.5.5", "14.1") that this test case represents. `test_module.py` will use this to mock `iOS.get_version()`.
  - `make_data`: Information about the `make_test_data.py` run that generated this case's input data.
    - `input_data_path`: The path to the original full image/archive used.
    - `os`: The operating system on which `make_test_data.py` was run.
    - `timestamp`: The date and time when the input data ZIP was created.
    - `last_commit`: Information about the module's Git commit at the time of data creation.
  - `artifacts`: A dictionary where keys are artifact function names from the module.
    - `artifact_name` (e.g., "get_photosMetadata"):
      - `search_patterns`: The file patterns from the module's `__artifacts_v2__` block used to find relevant files.
      - `file_count`: The number of files found and included in the input ZIP for this artifact and case.

Multiple test cases (e.g., "case_ios12_basic", "case_ios14_advanced") can be included in a single `testdata.<module_name>.json` file. It's recommended to use descriptive case keys.

## Image Manifest

The script uses an `image_manifest.json` file located in the `admin` directory. This manifest contains information about available test images, including their names, descriptions, and local paths.

## Known Issues and Limitations

### Dynamic File Searching in Modules

Some modules, such as `sms.py`, use a two-step process for file searching that can limit the effectiveness of automated test case creation:

1. The module provides an initial search pattern to locate a primary database file.
2. After processing the database, the module performs additional file searches based on data extracted from the database.

For example, the `sms.py` module:
1. First searches for the SMS database file.
2. Then searches for attachment files based on paths stored in the database.

This approach presents challenges for automated test case creation:

- The `make_test_data.py` script only uses the initial search patterns defined in the module.
- It cannot anticipate or include files that would be found by secondary searches within the module.

#### Impact on Test Coverage

This limitation may result in incomplete test data for modules that employ this dynamic searching technique. The created test cases might not include all the files that the module would process in a real-world scenario.

#### Future Improvements

To address this issue and improve test coverage, we need to consider the following approaches:

1. Enhance the `make_test_data.py` script to simulate the module's dynamic file searching behavior.
2. Modify the module structure to separate file searching from data processing, allowing for more comprehensive initial search patterns.
3. Implement a two-pass system in the test case creation process to capture files found by secondary searches.

Until these improvements are implemented, be aware that modules using dynamic file searching may require manual intervention to ensure comprehensive test data.

## Updating the JSON File

After creating test cases with `make_test_data.py`, it's important to manually update the `testdata.<module_name>.json` file with:

1. A meaningful `description` for each test case.
2. Your name as the `maker`.
3. The relevant `os_name` and `os_version` string so `test_module.py` can simulate it.

This information, along with the golden files generated by `test_module.py`, is crucial for understanding test coverage and validating results.

## Requirements

### __artifacts_v2__ Block

The test case creation process requires modules to use the `__artifacts_v2__` block for defining artifacts. This is because the v1 artifact definition has some limitations that can cause issues with the test harness.

If you want to apply this testing process to a v1 script before converting the entire code, you can update the artifact block to v2 format first to capture the results.

## Git Integration

The script now includes git integration to capture information about the last commit that modified the module file. This information is stored in the JSON metadata file for each test case.

## Performance Considerations

The script includes performance optimizations and progress indicators for processing large archive files. It also provides timing information for various stages of the test data creation process.
