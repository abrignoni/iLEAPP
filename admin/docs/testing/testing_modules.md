# Testing Modules

This document describes the process of testing LEAPP modules using the `test_module.py` script.

## Overview

The `test_module.py` script is designed to run tests on LEAPP modules using previously created test cases. It processes the test data, executes the module's artifact extraction function, and generates test results. This script allows for rapid testing of modules against various test cases and artifacts.

## Usage

To test a module, use the following command:

```python
python test_module.py <module_name> [artifact_name] [case_number]
```

- `<module_name>`: Name of the module to test
- `[artifact_name]`: (Optional) Name of the specific artifact to test (or 'all')
- `[case_number]`: (Optional) Specific case number to test (or 'all')

- If `artifact_name` or `case_number` are not provided, the script will prompt you to select from available options or run all.
- Provide `all` on the command line to run all test cases and artifacts.

## Process

1. The script loads test cases for the specified module.
2. It allows selection of specific artifacts and test cases to run.
3. For each selected test case and artifact:
   a. The script extracts test data from the corresponding zip file.
   b. It executes the module's artifact extraction function.
   c. The results are collected and formatted.
4. Test results are saved as JSON files.

The entire process runs quickly, typically completing in seconds, even when testing multiple artifacts and test cases.

## Output

The script generates JSON files containing test results, including:

- Metadata about the test run (module name, artifact name, case number, etc.)
- Execution time and performance metrics
- The extracted data (headers and rows)

Output files are stored in the `admin/test/results` directory. Note that no output file is created if the module encounters an error during execution.

## Example

```python
python test_module.py keyboard
```

This command will start the testing process for the keyboard module, prompting you to select specific artifacts and test cases.

## Notes

- The script uses test data created by the `make_test_data.py` script.
- Test results include information about the last Git commit for the tested module.
- You can run tests for all artifacts and all test cases by selecting 'all' when prompted.
- The script emulates core iLEAPP functionality and mocks certain components to simulate normal running conditions for the module.
- Currently, the script does not create normal outputs (HTML, LAVA, TSV, timeline, etc.) but focuses on collecting the parsed data results.
- Comparison of results against known good data is currently a manual process, but future versions may include automated comparison capabilities.
