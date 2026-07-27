# LEAPP Testing Architecture Overview

This document provides an overview of the testing architecture used in the LEAPP project, focusing on how various components work together to create and manage test cases for artifact extraction modules.

## Components

1. **Image Manifest**: A JSON file (`admin/image_manifest.json`) that contains metadata about available test images.
2. **Make Test Data Script**: A Python script (`admin/test/scripts/make_test_data.py`) that generates focused test data (input ZIPs) for LEAPP modules.
3. **Test Case Definitions**: JSON files (`admin/test/cases/testdata.<module>.json`) that define individual test scenarios, including metadata about the source data and specific artifact inputs.
4. **Conditional Behaviors Metadata**: A JSON file (`admin/test/metadata/conditional_behaviors.json`) documenting known conditional logic within modules (e.g., iOS version differences) and linking them to relevant test cases.
5. **Test Module Script**: A Python script (`admin/test/scripts/test_module.py`) for executing module logic against test case data, capturing results, and comparing them against "golden files."
6. **Golden Files**: JSON files (`admin/test/results/<module>/<artifact>.<case>.golden.json`) that store the verified, expected output for a specific module, artifact, and test case. These serve as the baseline for regression testing.
7. **Test Module Output Script**: A Python script (`admin/test/scripts/test_module_output.py`) for running a module within a minimal iLEAPP environment to generate and manually verify standard report outputs (HTML, TSV, etc.).
8. **File Path Lists**: CSV files containing lists of file paths from each test image, used by `make_test_data.py` for efficient file searching.
9. **File Path Search Results**: CSV and markdown files documenting the results of file path pattern searches against full images.

## Workflow

1. **Image Management**:
   - Test images (e.g., full filesystem extractions) are sourced, often from publicly available datasets.
   - Image metadata (including local paths and links to file path lists) is added to `admin/image_manifest.json`.

2. **(Optional) File Path Extraction**:
   - For very large images, file paths can be pre-extracted and stored as CSVs, then referenced in the `image_manifest.json` to speed up test data creation.

3. **Test Data Creation (`make_test_data.py`)**:
   - The `make_test_data.py` script uses an image and module artifact patterns to:
     - Create focused input ZIP files (`admin/test/cases/data/<module>/...`) containing only the necessary files for a module/artifact to run.
     - Create or update the test case definition file (`admin/test/cases/testdata.<module>.json`) which describes the different test scenarios (cases) for the module.

4. **Documenting Conditional Logic (Manual)**:
    - If a module has known conditional behaviors (e.g., based on iOS version), these are documented in `admin/test/metadata/conditional_behaviors.json`, linking the conditions to specific test case names from the `testdata.<module>.json` files.

5. **Module Logic Testing & Golden File Management (`test_module.py`)**:
   - The `test_module.py` script is run for a specific module and test case.
   - It executes the module's logic using the focused input ZIP.
   - Current version creates dated result files that can be compared against previous dated runs.
   - Future plans:
      - **Initial Run/Update**: If a golden file doesn't exist, or if `--update-golden-files` flag is used, the script saves the module's output as a `.golden.json` file in `admin/test/results/...`. This output must be manually verified for correctness before committing.
      - **Regression Testing**: On subsequent runs, the script compares the module's current output against the existing `.golden.json` file. Differences indicate a potential regression or an intentional change that needs a golden file update.

6. **Module Report Output Testing (`test_module_output.py`)**:
    - The `test_module_output.py` script runs the module using test case data in a simulated iLEAPP environment.
    - It generates standard iLEAPP reports (HTML, TSV, etc.) in `admin/test/output/...`.
    - These reports are manually reviewed to ensure output formats are correct and complete.

7. **File Path Analysis**:
   - A script analyzes how well module search patterns match files in the test images.
   - Detailed results are stored in `admin/docs/filepath_results.csv`.
   - A summary is generated in `admin/docs/filepath_search_summary.md`.

## Key Features

- **Decentralized Image Storage**: The manifest allows contributors to use local paths for test images.
- **Focused & Fast Testing**: Subsetted input ZIPs and golden file comparisons enable rapid module logic testing.
- **Flexible Testing**: Test cases can be designed to cover different iOS versions, app installations, or data presence scenarios.
- **Documented Conditional Coverage**: `conditional_behaviors.json` helps track tests against known module variations.
- **Performance Optimization**: File path lists can speed up the initial test data creation process for large images.

## Future Considerations

- Automated updates to test cases when modules or iOS versions change.
- Integration with CI/CD pipelines for continuous testing.
- Expansion of the image manifest to include more diverse test datasets.
