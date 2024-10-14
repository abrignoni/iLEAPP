# LEAPP Testing Documentation

This documentation provides an overview of the testing processes used in the LEAPP project, with a current focus on module testing.

## Module Testing

Module testing is a crucial part of ensuring the reliability and accuracy of LEAPP's artifact extraction and analysis capabilities. Our module testing process involves three main steps:

1. [Creating Module Test Cases](create_module_test_cases.md)
2. [Testing Modules](testing_modules.md)
3. [Testing Module Outputs](testing_module_outputs.md)

This three-step process allows for efficient testing, provides a foundation for future CI/CD integration, and enables comprehensive validation of module functionality.

### Creating Module Test Cases

We use a custom script to generate test cases for each module. This process involves:

- Extracting relevant files from input data (zip, tar, or tar.gz files)
- Creating JSON files with test case metadata
- Generating zip files containing test data for each artifact

This step is performed periodically to create small, focused test datasets. It allows for the creation of multiple test cases from various images, including synthetic test cases for edge scenarios.

For more details, see the [Creating Module Test Cases](create_module_test_cases.md) documentation.

### Testing Modules

Once test cases are created, we use another script to run tests on the modules. This process includes:

- Selecting specific modules, artifacts, and test cases to run
- Executing the module's artifact extraction function
- Collecting and formatting the results
- Generating test result files

This step focuses purely on the datasets and can be run quickly and efficiently, making it suitable for frequent use during development.

For more information, refer to the [Testing Modules](testing_modules.md) documentation.

### Testing Module Outputs

The final step in our module testing process involves verifying the various output formats supported by each module. This is done using the `test_module_output.py` script, which:

- Mocks parts of the plugin loader to control which plugins are run
- Uses the test data cases directly
- Generates all supported output formats (HTML, TSV, LAVA, etc.) for the selected module
- Allows for manual verification of the output

This step is intended for later-stage testing and manual verification. While it's more time-consuming than the initial module test, it provides a comprehensive check of the module's output capabilities.

For details on how to use this script and interpret its results, see the [Testing Module Outputs](testing_module_outputs.md) documentation.

## Future Expansions

As the LEAPP project grows, we plan to expand our testing capabilities to potentially include:

- Automated comparison of test results against known good data
- Integration of output verification into CI/CD workflows
- Performance benchmarking

These expansions will be considered and implemented as the project's needs evolve.
