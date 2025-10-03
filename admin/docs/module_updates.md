# Updating Modules for Automatic Output Generation

This guide outlines the process of updating existing xLEAPP modules to use the new automatic output generator. This update simplifies module code and ensures consistent output across all artifacts.

## Key Changes

1. Update the `__artifacts_v2__` block
2. Modify imports
3. Add the `@artifact_processor` decorator
4. Adjust the main function
5. Remove manual report generation code
6. Use a distinct data_list for HTML report (if needed)
7. Handling Media Files with the Media Manager (New 2025-05-10)
8. Add chat parameters if the artifact should support a threaded type view
9. Update Device Information Collection

## Detailed Process

### 1. Update the `__artifacts_v2__` block

Ensure the `__artifacts_v2__` dictionary includes all required fields, especially the `output_types` field. This dictionary should be the very first thing in the script, before any imports or other code. The key in this dictionary must exactly match the name of the function that processes the artifact.

If there are double asterisk marks at the start of the search pattern in the paths key, replace them with only one asterisk mark.

```python
__artifacts_v2__ = {
    "function_name": {  # This should match exactly the function name in the script
        "name": "Human-readable Artifact Name",
        "description": "Brief description of what the artifact does",
        "author": "@AuthorUsername",
        "creation_date": "2023-05-24",
        "last_update_date": "2024-12-17",
        "requirements": "none",
        "category": "Artifact Category",
        "notes": "",
        "paths": ('Path/to/artifact/files',),
        "output_types": "all"  # or "standard" or ["html", "tsv", "timeline", "kml", "lava"],
        "artifact_icon": "feather-icon-name"
    }
}
```
Read [Artifact Info Block Structure](./artifact_info_block.md) for more info about `__artifacts_v2__` block

### 2. Modify imports

Remove imports related to manual report generation (ArtifactHtmlReport, tsv, kml, timeline) and unused ones, then add the artifact processor and any necessary media manager functions:

#### Remove this import

```python
from ileapp.scripts.artifact_report import ArtifactHtmlReport
```

#### Modify this import

```python
from ileapp.scripts.ilapfuncs import artifact_processor, get_file_path

# After (ensure all needed functions are imported)
from ileapp.scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,            # For media files on disk
    check_in_embedded_media,   # For media stored as blobs/binary data
    # ... other necessary ilapfuncs ...
)
import os # Often needed for path joining
```

### 3. Add the `@artifact_processor` decorator

Add the decorator to the main function:

```python
@artifact_processor
def artifactname(context):
    # ... function body ...
```

### 4. Adjust the main function

Modify the function to return data instead of generating reports:

```python
def artifactname(context):
    # if artifact needs to iterate through found files
    found_files = context.get_files_found()
    source_path = context.get_source_file_path("filename")
    data_list = []

    # ... Get file contents and process data ...
    # PList file
    pl = get_plist_file_content(source_path)
    for key, val in pl.items():
        data_list.append((key, val))

    # SQLite database
    query = '''SQL query'''
    db_records = get_sqlite_db_records(db_file, query)
    for record in db_records:
        timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        data_list.append((record[0], record[1], record[2],))
    
    data_headers = (('Column1', 'datetime'), 'Column2', 'Column3')
    return data_headers, data_list, source_path
```

[Avoid using SQL Reserved Words in Column Names](#avoiding-sql-reserved-words-in-column-names).

Be sure to mark columns with their data type if they are one of the special handler types. It's ok if all data in a marked column doesn't conform to the marked type, as it will be tested and displayed as provided if it doesn't match.

Currently the special handler types are:

- `datetime`
- `date`
- `phonenumber`
- `media` (See section: [Handling Media Files with the Media Manager](#7-handling-media-files-with-the-media-manager))

#### Timestamps

If the artifact is added to the timeline, be sure that the first column is a datetime or date type.

For timestamps in SQLite databases, these functions are actually used to convert timestamps in UTC in human readable format.

```python
start_time = convert_unix_ts_to_utc(record[0]) # Unix timestamp: e.g. 1733161051
start_time = convert_cocoa_core_data_ts_to_utc(record[0]) # Cocoa Core Data timestamp: e.g. 754853889
```

For plist files, convert_plist_date_to_utc function has been added to ilapfuncs.py to process the datetime objects (e.g. '2023-05-08T18:22:10Z').

```python
last_modified_date = convert_plist_date_to_utc(last_modified_date)
```

### 5. Remove manual report generation code

Delete any code related to manual report generation, including:

- Creating `ArtifactHtmlReport` objects
- Calling `report.start_artifact_report`
- Writing data to TSV files
- Generating timeline or KML files
- Any print or logging statements about no data being available: `print()` or `logdev()`

### 6. Use a distinct data_list for HTML report

Some artifacts contain data with HTML elements that can be rendered in the HTML report but are not of particular interest for other types of output.
For that particular case, you must generate a distinct data_list_html and return a tuple containing the normal data_list in first position and data_list_html in second position.

Example from splitwiseNotifications artifact:
```python
for record in db_records:
    created_ts = convert_unix_ts_to_utc(record[0])
    data_list_html.append((created_ts, record[1], record[2], record[3]))
    if '<strong>' and '</strong>' in record[1]:
        remove_html = record[1].replace('<strong>', '').replace('</strong>', '')
    data_list.append((created_ts, remove_html, record[2], record[3]))

    return data_headers, (data_list, data_list_html), source_path
```

You also have to indicate in `__artifact_v2__` block which columns contain HTML code to render it properly in the HTML report.

Example from splitwiseNotifications artifact:
```python
__artifacts_v2__ = {
    "splitwiseNotifications": {
        # Usual key information about the artifact
        "html_columns": ['Notification']
    }
}
```

### 7. Handling Media Files with the Media Manager

If your artifact processes or references media files (images, videos, audio), use the centralized Media Manager to handle them. This ensures deduplication, consistent display, and proper linking in HTML & LAVA.

**Key Functions:**
- `check_in_media()`: For media files located on the filesystem within the extraction.
- `check_in_embedded_media()`: For media content extracted as binary data (e.g., from a database BLOB).

Both functions will copy/link the media to a central data location in the report, add entries to the LAVA database for media items and their references, and return a `media_ref_id` (a string). This ID is what you'll put in your `data_list`.

**Steps:**

1. **Call `check_in_media` or `check_in_embedded_media`**:

    * **For files on disk (`check_in_media`):**
        ```python
        current_file_path = "**/path/to/image.jpg" # dummy for example
        media_file_on_disk = context.get_source_file_path(current_file_path) 

        if media_file_on_disk: 
            media_ref_id = check_in_media(
                file_path=media_file_on_disk,
                name='if-different-than-name-in-path' # optional
            )
            if media_ref_id:
                data_list.append((timestamp_column, text_column, media_ref_id))
        ```

    * **For embedded binary data (`check_in_embedded_media`):**
        ```python
        original_source_path_of_db = "*/path/to/sqlite.db" # dummy for example
        binary_image_data = db.msg_record.imagedata # dummy for example

        if binary_image_data and original_source_path_of_db:
            media_ref_id = check_in_embedded_media(
                source_file=original_source_path_of_db,
                data=binary_image_data,
                name=db.msg_record.imagename # optional but good idea if name is available
            )
            if media_ref_id:
                data_list.append((timestamp_column, description_column, media_ref_id))
        ```

2. **Update `data_headers`**: Mark the column containing `media_ref_id` with the type `'media'`.
    ```python
    data_headers = (
        ('Timestamp', 'datetime'),
        'Description',
        ('Photo', 'media')  # Basic media column
        # Or with custom style for the HTML display:
        # ('Thumbnail', 'media', 'max-width:100px; max-height:100px;') 
    )
    ```

3. **Return**: The `artifact_processor` will use the `media_ref_id` and the `'media'` type in `data_headers` to automatically:
    * Generate correct HTML tags (`<img>`, `<video>`, `<audio>`).
    * Provide appropriate paths for TSV, KML, and Timeline outputs.
    * Ensure LAVA has the necessary media information.


### 8. Add chat parameters if the artifact should support a threaded type view

Instructions:

The `chatParams` key will contain a dictionary of items to assist LAVA in determining which columns should be used to group messages into threads and which columns should be used to render the elements of the chat message bubble. Whenever a column name is specified it should match the column header as defined in the `data_headers` of the artifact.

```python
__artifacts_v2__ = {
    "get_artifactname": {
        # Other parameters as shown above,
        "chatParams": {
            "threadDiscriminatorColumn": Column that determines which thread messages belong to. This must be unique for each thread
            "threadLabelColumn": Optional column name providing a friendly name for the thread
            "textColumn": Column name containing the text message
            "directionColumn": Column name to determine if the message was sent/received
            "directionSentValue": Any Value that if present in the directionColumn specified above indicates the message was sent (ie: 1, True, "SENT"), any other value treated as received.
            "timeColumn": Column name containing the DateTime for the message (presumably the sent time),
            "senderColumn": Column name containing the senders name/identifier,
            "mediaColumn": Optional column containing an attachment (Further development required on this),
            "sentMessageLabelColumn": Optional column name containing the local users name/identifier (used for a case where the data only contains the remote users information and the senders information is located in a different column (ie an Account ID),
            "sentMessageStaticLabel": Optional string that will provide a static sender name/identifier for artifacts where this is unknown (ie "Local User")
        }
```

Example (From googleChat.py artifact):
```python
__artifacts_v2__ = {
    "get_googleChat": {  # This should match the function name exactly
        "name": "Google Chat",
        # Other parameters as shown above,
        "chatParams": {
            "threadDiscriminatorColumn": "Conversation Name",
            "textColumn": "Message",
            "directionColumn": "Is Sent",
            "directionSentValue": 1,
            "timeColumn": "Timestamp",
            "senderColumn": "Message Author",
            "mediaColumn": "Media"
        }
    }
}
```

### 9. Update Device Information Collection

The `logdevinfo()` function is being deprecated in favor of the new `device_info()` function. This new function provides better organization and structure for device-related information. Not every module uses these functions, so this section is only applicable to modules that do.

#### Old Method (logdevinfo):

```python
logdevinfo(f'<b>IMEI: </b>{imei}')
logdevinfo(f'<b>Serial Number: </b>{serial}')
```

#### New Method (device_info):

```python
device_info("Advertising Identifier", "Apple Advertising Identifier", val, source_path)
device_info("Device Information", "IMEI", imei, source_path)
```

It the module doesn't generate any output, specifiy `"output_types": "none"` in the `__artifacts_v2__` block and replace the return statement
```python
return data_headers, data_list, source_path
``` 
with
```python
return (), [], source_path
``` 


Key differences:

1. No HTML formatting needed - display formatting is handled by the output generator
2. Information is categorized for better organization
3. Values are stored in a structured format that's easier to query and display
4. Source tracking is automatic - the module name is recorded with each value
5. Duplicate handling is built-in - multiple modules can report the same information

The new structure allows for:

- Better organization of device information by category
- Automatic tracking of which modules provided what information
- Easier querying and filtering of device information
- Consistent formatting across all outputs
- De-duplication and conflict resolution

You can view the current categories and labels being used across all modules in the [Device Info Values](device_info_values.md) documentation.

### 10. Get device model from device identifier
The `get_device_model(identifier)` method of the Context class allows you to retrieve the human-readable device model name for a given device identifier (such as "iPhone10,1" or "iPad7,4") in the internal device ID mapping loaded from [data/device_ids.json](../../scripts/data/device_ids.json). This is useful when processing artifacts that include device identifiers and you want to display or use the corresponding model name.

When you are processing data, call the method with a device identifier
```python
model_name = Context.get_device_model(record[x])
```
- record[x] contains a string representing the device identifier (e.g., "iPhone10,1").

The function returns the model name as a string (e.g., "iPhone 8"). If the identifier is not found, it returns an empty string.

### 11. Get OS version from OS build
The `get_os_version(build, device_family='')` method of the Context class allows you to retrieve the operating system version string for a given build number in the internal OS builds mapping loaded from [data/os_builds.json](../../scripts/data/os_builds.json), and device family loaded from [data/device_ids.json](../../scripts/data/device_ids.json). This is useful when processing artifacts that include OS build information and you need to display or use the corresponding OS version.

When you are processing data, call the method with a build and an optional device identifier
```python
os_version = Context.get_os_version(record[x], record[y])
```
- record[x] contains a string representing the OS build number to look up (e.g., "22E240").
- record[y], which is optional, contains a string representing the device identifier (e.g., "iPhone10,1"). It is better to use it if available in order to avoid having multiple versions of different operating system families with the same build number. If it is not provided, the function will search all OS families and return all matching ones.

The function returns the OS version as a string (e.g., "iOS 18.4"). If any matching build number is found, it returns an empty string.

## Reasoning

This update simplifies module maintenance by:

1. Centralizing output generation logic
2. Reducing code duplication across modules
3. Ensuring consistent output formats
4. Making it easier to add new output types in the future

By focusing modules on data extraction and processing, we improve code readability and maintainability while allowing for more flexible and extensible output generation.

## Important Notes

- The key in the `__artifacts_v2__` dictionary must exactly match the name of the function that processes the artifact.
- For the `output_types`:
  - Use **only** "all" if you want to export data in all supported output types: html, tsv, kml, lava and timeline;
  - Use "standard" to export data in html, csv, lava and timeline;
  - Specify the desired types in a list ["html", "tsv", "timeline", "kml", "lava"];
  - For a single output, indicates the types (e.g: "lava")
  - For modules only collecting device info, use "none"
  - You may choose to generate the HTML output manually while still using the other output types. This may be useful for artifacts that need to be split to avoid browser crashes.
- The `artifact_processor` decorator now automatically retrieves the artifact information from the function's globals or the module's `__artifacts_v2__` dictionary.
- The main function should focus solely on data extraction and processing, returning the data for the artifact processor to handle output generation.

### Avoiding SQL Reserved Words in Column Names

When updating modules, it's crucial to avoid using SQL reserved words as column names. This is particularly important now that we're using SQLite for data storage. Common problematic column names include:

- 'value'
- 'values'
- 'key'
- 'order'
- 'group'
- 'index'

To address this:

1. Review your data_headers and ensure no column names use SQL reserved words.
2. If you find a reserved word, modify the column name to something more descriptive or append a relevant qualifier.

Examples of how to modify column names:

- 'value' could become 'data_value', 'setting_value', or 'recorded_value'
- 'key' could become 'encryption_key', 'lookup_key', or 'identifier'
- 'order' could become 'sort_order', 'sequence', or 'priority'
- 'index' could become 'idx', '#', 'Number', or 'N°'

```python
# Before
data_headers = ('timestamp', 'key', 'value')

# After
data_headers = ('timestamp', 'identifier', 'setting_value')
```

By avoiding SQL reserved words in column names, we prevent potential issues with SQLite queries and ensure smoother data handling across all output types.

### Timestamp Handling and Timezone Offsets

A new function `convert_plist_date_to_utc` is being added to `ilapfuncs.py` to address issues with timestamp handling, particularly for plist files. This function:

1. Manages date objects in the format 'YYYY-MM-DDTHH:MM:SSZ' found in plist files.
2. Ensures correct timestamp storage in the lava SQLite database.

When working with timestamps, especially from plist files:

- Use the `convert_plist_date_to_utc` function to process datetime objects.
- Be aware that this change improves consistency between HTML and SQLite outputs.

Example usage:

```python
from ileapp.scripts.ilapfuncs import convert_plist_date_to_utc

# ... in your processing function ...
timestamp = convert_plist_date_to_utc(plist_date)
```

These changes ensure that timestamp handling is consistent across all output types.
