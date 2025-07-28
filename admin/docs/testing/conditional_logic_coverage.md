# Documenting Conditional Logic & Coverage

LEAPP modules often contain conditional logic, for example, to handle different database schemas across iOS versions (like in `photosMetadata.py`) or to adapt to the presence or absence of optional files. To effectively test these variations and document their coverage, this project uses a combination of specific test cases and a metadata file.

## Overview

-   **Conditional Behaviors Metadata (`admin/test/metadata/conditional_behaviors.json`)**: This JSON file is manually maintained to document known conditional behaviors for each module and its artifact functions.
-   **Test Case Definitions (`admin/test/cases/testdata.<module>.json`)**: These files define specific test scenarios ("cases"). For modules with conditional logic, distinct cases should be created to target each condition (e.g., a case for iOS 12, another for iOS 13). The `os_version` field within a test case in this file is used by `test_module.py` to simulate that specific iOS version.
-   **Golden Files (`admin/test/results/<module>/<artifact>.<case>.golden.json`)**: The existence of a golden file for a specific test case signifies that the condition targeted by that test case is actively being tested.

## The `conditional_behaviors.json` File

This file provides a structured way to list the different operational conditions a module might encounter and link them to the test cases designed to cover them.

### Structure Example

```json
{
  "photosMetadata": { // Top-level key is the module name
    "get_photosMetadata": { // Key is the artifact function name
      "conditions": { // A way to group conditions, e.g., by type
        "ios_version": [ // An array of specific conditional branches
          {
            "value": "<12", // A string describing the specific condition value
            "description": "Module execution should result in a log message indicating it's unsupported and no data rows returned.",
            "relevant_test_cases": ["case_ios11_unsupported"], // List of case keys from testdata.photosMetadata.json
            "unsupported": true // Optional: true if this condition means the module shouldn't produce data
          },
          {
            "value": "12.x",
            "description": "Uses specific SQL queries for iOS 12 schema.",
            "relevant_test_cases": ["case_ios12_basic"]
          },
          // ... more conditions
        ]
      }
    }
  }
  // ... other modules
}
```

### Key Fields:

*   **Module Name (e.g., `"photosMetadata"`)**: The top-level key.
*   **Artifact Function Name (e.g., `"get_photosMetadata"`)**: Key for the specific function.
*   **`conditions` Object**: Allows grouping of conditions (e.g., by `"ios_version"`, `"file_presence"`).
    *   **Condition Type (e.g., `"ios_version"`)**: An array of specific condition entries.
        *   `"value"`: A string that describes the specific value of the condition (e.g., "<12", "12.x", "file_X_missing").
        *   `"description"`: Human-readable explanation of the module's behavior under this condition.
        *   `"relevant_test_cases"`: An array of strings. Each string is a case key from the corresponding `testdata.<module>.json` file that is designed to test this specific condition.
        *   `"unsupported"`: (Optional) A boolean (`true`/`false`). If `true`, it indicates that for this condition, the module is expected to produce no data, or handle it as an unsupported scenario. The golden file for associated test cases should reflect this (e.g., empty data array).

## Workflow for Documenting and Testing Conditions

1.  **Identify Conditional Logic**: When developing or reviewing a module, identify parts of the code that behave differently based on external factors (iOS version, file existence, file content variations).
2.  **Define Test Cases**:
    *   In the relevant `admin/test/cases/testdata.<module>.json`, create distinct test case entries (e.g., `case_ios12_data`, `case_ios13_data`).
    *   Ensure each case has appropriate metadata, especially `os_version` if testing iOS-dependent logic.
3.  **Generate Test Data**: Use `make_test_data.py` to create the input ZIP files for these specific test cases, ensuring the source data used aligns with the condition being tested.
4.  **Generate/Update Golden Files**: Use `test_module.py --update-golden-files` to create or update the golden files for these test cases. Manually verify their correctness.
5.  **Update `conditional_behaviors.json`**:
    *   Add or update entries for the module and artifact.
    *   Describe each condition (`value`, `description`).
    *   List the relevant test case key(s) in the `relevant_test_cases` array.
    *   Set `unsupported: true` if applicable.
6.  **Commit Changes**: Commit the module code, `testdata.<module>.json`, new/updated golden files, and `conditional_behaviors.json`.

## Viewing Coverage

The primary way to view this coverage currently is by manually inspecting `conditional_behaviors.json` and cross-referencing with the existence of golden files for the listed `relevant_test_cases`.

Future enhancements could involve scripts or Docusaurus integration to parse these files and generate a user-friendly test coverage report that explicitly shows which documented conditions have corresponding, successfully passing tests (i.e., an up-to-date golden file).

This manual documentation, combined with the golden file testing mechanism, provides a robust way to manage and verify tests for complex, conditional module logic.