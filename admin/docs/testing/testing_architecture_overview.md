# LEAPP Testing Architecture Overview

This document provides an overview of the testing architecture used in the LEAPP project, focusing on how various components work together to create and manage test cases for artifact extraction modules.

## Components

1. **Image Manifest**: A JSON file (`admin/image_manifest.json`) that contains metadata about available test images.
2. **Make Test Data Script**: A Python script (`make_test_data.py`) that generates test data for LEAPP modules.
3. **Test Cases**: JSON files and associated data files containing test cases for each module.
4. **File Path Lists**: CSV files containing lists of file paths from each test image.
5. **File Path Search Results**: CSV and markdown files documenting the results of file path pattern searches.

## Workflow

1. **Image Management**:
   - Test images are publicly available datasets created by the community.
   - Image metadata is manually added to the `image_manifest.json` file.
   - Actual image files are not stored in the repository due to their large size.

2. **File Path Extraction**:
   - File paths are extracted from each test image and stored as CSV files.
   - These lists allow for faster pattern matching and test coverage analysis.

3. **Test Data Creation**:
   - The `make_test_data.py` script uses the image manifest and file path lists to create test cases.
   - It extracts relevant files from the test images based on module artifact patterns.
   - Test data is stored as zip files in the `admin/test/cases/data` directory.

4. **Test Case Documentation**:
   - JSON files in the `admin/test/cases` directory document test cases for each module.
   - These files contain metadata, artifact information, and expected outputs.

5. **File Path Analysis**:
   - A script analyzes how well module search patterns match files in the test images.
   - Detailed results are stored in `admin/docs/filepath_results.csv`.
   - A summary is generated in `admin/docs/filepath_search_summary.md`.

## Key Features

- **Decentralized Image Storage**: The manifest allows contributors to use local paths for test images.
- **Flexible Testing**: Multiple test images account for different iOS versions and app installations.
- **Performance Optimization**: File path lists speed up the test data creation process.
- **Coverage Tracking**: File path analysis helps track module test coverage and iOS/app version changes.

## Future Considerations

- Automated updates to test cases when modules or iOS versions change.
- Integration with CI/CD pipelines for continuous testing.
- Expansion of the image manifest to include more diverse test datasets.
