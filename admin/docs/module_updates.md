# Updating Modules for Automatic Output Generation

This guide outlines the process of updating existing xLEAPP modules to use the new automatic output generator. This update simplifies module code and ensures consistent output across all artifacts.

## Key Changes

1. Update the `__artifacts_v2__` block
2. Modify imports
3. Add the `@artifact_processor` decorator
4. Adjust the main function
5. Remove manual report generation code

## Detailed Process

### 1. Update the `__artifacts_v2__` block

Ensure the `__artifacts_v2__` dictionary includes all required fields, especially the `output_types` field. This dictionary should be the very first thing in the script, before any imports or other code. The key in this dictionary must exactly match the name of the function that processes the artifact.

```python
__artifacts_v2__ = {
    "get_artifactname": {  # This should match the function name exactly
        "name": "Human-readable Artifact Name",
        "description": "Brief description of what the artifact does",
        "author": "@AuthorUsername",
        "version": "1.0",
        "date": "2023-05-24",
        "requirements": "none",
        "category": "Artifact Category",
        "notes": "",
        "paths": ('Path/to/artifact/files',),
        "output_types": "all"  # or ["html", "tsv", "timeline", "lava"]
    }   
}
```

### 2. Modify imports

Remove imports related to manual report generation and add the artifact processor:

#### Remove these imports
```python
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import tsv, timeline, kmlgen, logfunc, is_platform_windows
```

#### Add this import
```python
from scripts.ilapfuncs import artifact_processor
```

### 3. Add the `@artifact_processor` decorator

Add the decorator to the main function:

```python
@artifact_processor
def get_artifactname(files_found, report_folder, seeker, wrap_text, timezone_offset):
    # ... function body ...
```

### 4. Adjust the main function

Modify the function to return data instead of generating reports:

```python
def get_artifactname(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    data_headers = ()
    source_path = ''

    for file_found in files_found:
        source_path = file_found
        # ... process data ...
        data_list.append((col1, col2, col3))
        
    data_headers = (('Column1', 'datetime'), 'Column2', 'Column3')
    return data_headers, data_list, source_path
```

Be sure to mark columns with their data type if they are one of the special handler types. It's ok if all data in a marked column doesn't conform to the marked type, as it will be tested and displayed as provided if it doesn't match.

Currently the special handler types are:
- datetime
- date
- phonenumber
### 5. Remove manual report generation code

Delete any code related to manual report generation, including:

- Creating `ArtifactHtmlReport` objects
- Calling `report.start_artifact_report`
- Writing data to TSV files
- Generating timeline or KML files
- Any print or logging statements about no data being available

## Reasoning

This update simplifies module maintenance by:

1. Centralizing output generation logic
2. Reducing code duplication across modules
3. Ensuring consistent output formats
4. Making it easier to add new output types in the future

By focusing modules on data extraction and processing, we improve code readability and maintainability while allowing for more flexible and extensible output generation.

## Important Notes

- The key in the `__artifacts_v2__` dictionary must exactly match the name of the function that processes the artifact.
- The `artifact_processor` decorator now automatically retrieves the artifact information from the function's globals or the module's `__artifacts_v2__` dictionary.
- The main function should focus solely on data extraction and processing, returning the data for the artifact processor to handle output generation.

### Avoiding SQL Reserved Words in Column Names

When updating modules, it's crucial to avoid using SQL reserved words as column names. This is particularly important now that we're using SQLite for data storage. Common problematic column names include:

- 'value'
- 'values'
- 'key'
- 'order'
- 'group'

To address this:

1. Review your data_headers and ensure no column names use SQL reserved words.
2. If you find a reserved word, modify the column name to something more descriptive or append a relevant qualifier.

Examples of how to modify column names:

- 'value' could become 'data_value', 'setting_value', or 'recorded_value'
- 'key' could become 'encryption_key', 'lookup_key', or 'identifier'
- 'order' could become 'sort_order', 'sequence', or 'priority'

```python
# Before
data_headers = ('timestamp', 'key', 'value')

# After
data_headers = ('timestamp', 'identifier', 'setting_value')
```

By avoiding SQL reserved words in column names, we prevent potential issues with SQLite queries and ensure smoother data handling across all output types.

### Timestamp Handling and Timezone Offsets

A new function `convert_plist_date_to_timezone_offset` is being added to `ilapfuncs.py` to address issues with timestamp handling, particularly for plist files. This function:

1. Manages date objects in the format 'YYYY-MM-DDTHH:MM:SSZ' found in plist files.
2. Converts timestamps to support the timezone offset chosen by the user.
3. Ensures correct timestamp storage in the lava SQLite database.

When working with timestamps, especially from plist files:

- Use the `convert_plist_date_to_timezone_offset` function to process datetime objects.
- Ensure that timestamps are treated as UTC when converting for SQLite storage.
- Be aware that this change improves consistency between HTML and SQLite outputs.

Example usage:

```python
from scripts.ilapfuncs import convert_plist_date_to_timezone_offset

# ... in your processing function ...
timestamp = convert_plist_date_to_timezone_offset(plist_date, timezone_offset)
```

This update resolves previous inconsistencies where timestamps in HTML didn't support timezone offsets and SQLite entries were incorrectly treated as local time instead of UTC.

These changes ensure that timestamp handling is consistent across all output types and correctly respects the user's chosen timezone offset.
