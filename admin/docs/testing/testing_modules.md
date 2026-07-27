# Testing Module Logic and Collecting Results

This document describes the process of testing LEAPP module logic using the `admin/test/scripts/test_module.py` script. This script focuses on executing module logic against specific test data and collecting the raw data output by the module.

## Overview

The `test_module.py` script is designed to run tests on LEAPP modules using previously created test cases (input data ZIPs and `testdata.<module>.json` definitions from `make_test_data.py`). It processes the focused test data, executes the module's artifact extraction function(s), and generates JSON files containing the results. This allows for rapid execution of modules against various test scenarios to observe their output.

## Usage

To test a module and collect its output, use the following command:

```bash
python admin/test/scripts/test_module.py <module_name> [options]
```

**Common Options:**

*   `<module_name>`: Name of the module to test (e.g., `photosMetadata`).
*   `--artifact <artifact_name>`: (Optional) Name of the specific artifact function to test.
*   `--case <case_key>`: (Optional) Specific case key (as defined in `testdata.<module_name>.json`) to test.
*   You can often use "all" for artifact or case to run all available ones for the specified module.

If `artifact_name` or `case_key` are not provided, the script may prompt for selection or run all defined test cases and their associated artifacts for the module.

## Process

1.  The script loads test case definitions from `admin/test/cases/testdata.<module_name>.json`.
2.  It allows selection of specific artifacts and test cases to run (if not specified via command-line arguments).
3.  For each selected test case and artifact:
    a.  It locates the input data ZIP (e.g., `admin/test/cases/data/<module_name>/testdata.<module_name>.<artifact_name>.<case_key>.zip`).
    b.  It extracts these files to a temporary location.
    c.  It executes the module's artifact function, passing the extracted files and mocked versions of necessary iLEAPP components (e.g., `logfunc`, `seeker`, `iOS.get_version()` if `os_version` is specified in the test case definition).
    d.  The script captures the headers and data rows returned by the artifact function.
    e.  These results, along with metadata about the test run, are saved as a new, timestamped JSON file.

The entire process runs quickly, typically completing in seconds, even when testing multiple artifacts and test cases.

## Output

The script generates new, timestamped JSON files for each test run in the `admin/test/results/<module_name>/` directory. For example: `admin/test/results/photosMetadata/get_photosMetadata.case_ios12_basic.20241028153000.json`.

These JSON files contain:

*   Metadata about the test run (module name, artifact name, case key, timestamps, data size, Git commit of the module, etc.).
*   The extracted data (headers and rows) as returned by the module's artifact function.

**Note:** Currently, the script does not perform any automated comparison of these output files against previous results or a "known good" baseline. Verification of the output is a manual process of inspecting these JSON files. No output file is created if the module encounters an error preventing it from returning data.

## Example

```bash
python admin/test/scripts/test_module.py photosMetadata --artifact get_photosMetadata --case case_ios12_basic
```

This command will run the `get_photosMetadata` artifact from the `photosMetadata` module using the test data defined for `case_ios12_basic`. A new JSON file with the results will be created in `admin/test/results/photosMetadata/`.

## Notes

*   The script uses test case definitions from `testdata.<module_name>.json` and input data ZIPs created by `make_test_data.py`.
*   This script focuses on the *data extraction logic* of the module, not the generation of iLEAPP reports (HTML, TSV, etc.). For report testing, see `test_module_output.py`.
*   Ensure `os_version` is specified in your `testdata.<module_name>.json` for cases that test OS-dependent logic, so `test_module.py` can mock `iOS.get_version()` correctly.

## Manual Verification of Results

After running `test_module.py`, you need to:
1. Locate the generated timestamped JSON file in `admin/test/results/<module_name>/`.
2. Manually open and inspect the file.
3. Verify that the `headers` and `data` sections are as expected for the specific test case and module logic.
4. This process needs to be repeated if you are checking for regressions after code changes or testing new functionality.

## Future Enhancements: Golden File Testing

A planned improvement for `test_module.py` is the introduction of "Golden File Testing." This would involve:

1.  **Establishing Golden Files**: A specific, verified output JSON file (e.g., `<artifact>.<case>.golden.json`) would be stored in the repository for each test case, representing the known-correct output.
2.  **Automated Comparison**: `test_module.py` would automatically compare its current run's output against this golden file.
3.  **Pass/Fail Reporting**: The script would report a clear "pass" if the outputs match or "fail" (with differences highlighted) if they don't.
4.  **Updating Golden Files**: A mechanism (e.g., a command-line flag like `--update-golden-files`) would allow developers to easily update the golden file after manually verifying that an intentional change in output is correct.

This enhancement would significantly improve automated regression detection and reduce the manual effort currently required to verify test results.
