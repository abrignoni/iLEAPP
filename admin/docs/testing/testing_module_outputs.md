# Testing Module Outputs

This document describes the process of testing the various output formats supported by LEAPP modules using the `test_module_output.py` script.

## Overview

The `test_module_output.py` script is designed to test a single LEAPP module's output capabilities. It uses pre-created test cases and generates all supported output formats (HTML, TSV, LAVA, etc.) for the selected module. This process allows for comprehensive verification of the module's functionality and output accuracy.

## Running the Script

To run the script, use the following command from the root directory of the LEAPP project:

```python admin/test/scripts/test_module_output.py <module_name>```


Replace `<module_name>` with the name of the module you want to test (with or without the .py extension).

## Process

1. **Module Validation**: The script first validates that the specified module exists.

2. **Test Case Selection**: It then loads the available test cases for the module and prompts you to select one.

3. **Test Data Extraction**: The script extracts the test data for the selected case into a temporary folder.

4. **Module Execution**: The script runs the selected module against the test data, generating all supported output formats.

5. **Output Generation**: The results are saved in the `admin/test/output` directory.

## Output Verification

After the script completes, you should manually verify the generated outputs:

1. Check the `admin/test/output` directory for the generated files.
2. Verify that all expected output formats (HTML, TSV, LAVA, etc.) are present.
3. Review the content of each output file to ensure accuracy and completeness.
4. Compare the results with expected outcomes based on the test case data.

## Advantages

- Allows testing of individual modules without running the entire LEAPP suite.
- Provides a quick way to verify all output formats supported by a module.
- Uses pre-created test cases, ensuring consistent and repeatable testing.

## Limitations

- This is a manual verification process and requires human review of the outputs.
- It does not automatically compare results against expected outcomes.

## Future Improvements

Future versions of this testing process may include:

- Automated comparison of results against known good outputs.
- Integration into CI/CD workflows for automated testing.
- Performance benchmarking capabilities.

Remember, this testing process is intended for later-stage verification and complements the earlier, data-focused testing steps in the LEAPP module testing workflow.

