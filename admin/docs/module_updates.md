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

Ensure the `__artifacts_v2__` dictionary includes all required fields, especially the `output_types` field. This dictionary should be the very first thing in the script, before any imports or other code. Do not keep the older `__artifacts__` dictionary. If the script has a comment block with information about the module, use the information to populate the `__artifacts_v2__` dictionary and then remove the comment block.

```python
__artifacts_v2__ = {
    "artifact_id": {
        # ... existing fields ...
        "output_types": "all"  # or ["html", "csv", "timeline", "lava"]
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
@artifact_processor(__artifacts_v2__["artifact_id"])
def get_artifactname(files_found, report_folder, seeker, wrap_text, timezone_offset):
# ... function body ...
```
### 4. Adjust the main function

Modify the function to return data instead of generating reports:
```python
def get_artifactname(files_found, report_folder, seeker, wrap_text, timezone_offset):
    # Prepare return variables
    data_list = []
    data_headers = ()
    source_path = ''

    # Process files and data
    for file_found in files_found:
        source_path = file_found
        # ... process data ...
        data_list.append((col1, col2, col3))
        
    data_headers = (('Timestamp', 'datetime'), 'Column2', 'Column3')
    return data_headers, data_list, source_path
```


### 5. Remove manual report generation code

Delete any code related to manual report generation, including:

- Creating `ArtifactHtmlReport` objects
- Calling `report.start_artifact_report`
- Writing data to TSV files
- Generating timeline or KML files

## Reasoning

This update simplifies module maintenance by:

1. Centralizing output generation logic
2. Reducing code duplication across modules
3. Ensuring consistent output formats
4. Making it easier to add new output types in the future

By focusing modules on data extraction and processing, we improve code readability and maintainability while allowing for more flexible and extensible output generation.