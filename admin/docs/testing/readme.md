# LEAPP Testing Documentation

This documentation provides an overview of the testing processes used in the LEAPP project, with a current focus on module testing.

## Module Testing

Module testing is a crucial part of ensuring the reliability and accuracy of LEAPP's artifact extraction and analysis capabilities. Our module testing process involves two main steps:

1. [Creating Module Test Cases](create_module_test_cases.md)
2. [Testing Modules](testing_modules.md)

This two-step process allows for efficient testing, provides a foundation for CI/CD, and enables (semi-)automated tests going forward.

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

This step can be run manually during development or potentially automated as part of a CI/CD pipeline to validate parsing consistency across module updates.

For more information, refer to the [Testing Modules](testing_modules.md) documentation.

## Future Expansions

As the LEAPP project grows, we plan to expand our testing documentation and capabilities to cover:

- Automated comparison of test results against known good data
- Unit testing
- Integration testing
- Performance testing
- Continuous Integration (CI) processes


