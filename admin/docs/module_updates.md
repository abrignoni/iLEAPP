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

If there are double asterisk marks at the start of the search pattern in the paths key, replace them with only one asterisk mark.

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

Remove imports related to manual report generation (ArtifactHtmlReport, tsv, kml, timeline) and unused ones, then add the artifact processor:

#### Remove this import
```python
from scripts.artifact_report import ArtifactHtmlReport
```

#### Modify this import
```python
from scripts.ilapfuncs import artifact_processor, kmlgen, logfunc, is_platform_windows
```
Remove imports related to manual report generation (tsv, kml and timeline) and unused ones
```python
from scripts.ilapfuncs import logfunc, is_platform_windows
```
Add the artifact processor
```python
from scripts.ilapfuncs import artifact_processor, logfunc, is_platform_windows
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
        source_path = str(file_found)

    if not source_path:
        logfunc('<filename> not found')
        return data_headers, data_list, source_path

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

#### Timestamps
If the artifact is added to the timeline, be sure that the first column is a datetime or date type.

For timestamps in SQLite databases, this code is actually used to support timezone offset parameter chosen by the user. 
```python
start_time = convert_ts_human_to_utc(row[1])
start_time = convert_utc_human_to_timezone(start_time,timezone_offset)
```
If there is no value, script execution is interrupted and artifact is not added to any report. A new function has been added to ilapfuncs.py and must be preferably be used.
```python
start_time = convert_ts_human_to_timezone_offset(row[1], timezone_offset)
```

For plist files, convert_plist_date_to_timezone_offset function has been added to ilapfuncs.py to process the datetime objects (e.g. '2023-05-08T18:22:10Z') and support lava-ouput and timezone offset in other reports.
```python
last_modified_date = convert_plist_date_to_timezone_offset(last_modified_date, timezone_offset)
```

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

These changes ensure that the artifact information is correctly associated with the processing function and that the output generation is handled consistently across all artifacts.