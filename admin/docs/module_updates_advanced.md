# Updating Complex Modules to Include LAVA Output

This guide outlines the process of updating existing complex xLEAPP modules to include LAVA output. These modules typically process a single group of file pattern searches but generate multiple HTML and TSV outputs.

*Note that if you are just attempting to split output into multiple HTML pages or just handle HTML manually for some other reason but the LAVA and TSV is a single table/output you can probably still use the instructions found in [Updating Modules for Automatic Output Generation](module_updates.md). (Refer to `carCD.py` for an example of manual HTML with automatic LAVA/TSV processing)*

## Key Changes

1.  Update the `__artifacts_v2__` block
2.  Modify imports (add LAVA and Media Manager functions)
3.  Handle Media Files (if applicable)
4.  Add LAVA output generation to the main function
5.  Use special data type handlers for LAVA output

## Detailed Process

### 1. Update the `__artifacts_v2__` block

Modify the `__artifacts_v2__` dictionary to include all required fields for the complex artifact. This dictionary should be the first thing in the script, before any imports or other code. Make sure to set `output_types` to "none" since we're not using the artifact processor for automated output generation. Additionally, include a "function" key with the name of the main processing function as its value.

```python
__artifacts_v2__ = {
    "complex_artifact": {
        "name": "Complex Artifact Name",
        "description": "Description of the complex artifact",
        "author": "@AuthorUsername",
        "version": "1.0",
        "date": "2023-05-24",
        "requirements": "none",
        "category": "Complex Artifact Category",
        "notes": "",
        "paths": ('Path/to/complex/artifact/files',),
        "output_types": "none",  # Changed from ["HTML", "TSV"] to "none"
        "function": "get_complex_artifact"  # This should match the name of your main processing function
    }
}
```

### 2. Modify Imports

Add imports for LAVA functions and, if your module handles media, the Media Manager functions from `ilapfuncs`.

```python
# Existing imports for your module...
# import scripts.artifact_report # For manual HTML reports
# from scripts.ilapfuncs import tsv # For manual TSV

# Add these for LAVA and Media Management:
from scripts.lavafuncs import lava_process_artifact, lava_insert_sqlite_data
from scripts.ilapfuncs import (
    check_in_media,
    check_in_embedded_media,
    get_file_path, # If you use it to find files
    # ... other necessary ilapfuncs ...
)
import os # Often needed for path joining with 'data' subfolder
```

### 3. Handle Media Files (If Applicable)

If your complex artifact involves media files, use the Media Manager functions (`check_in_media` or `check_in_embedded_media`) to process them. This step should occur *before* you populate your `data_list` with media references and *before* you call `lava_process_artifact`.

1.  **Get `artifact_info`**: Retrieve the artifact's metadata dictionary from `__artifacts_v2__` using the current function's name.
    ```python
    # Inside your main processing function (e.g., get_complex_artifact)
    # This assumes 'complex_artifact' is the key in __artifacts_v2__
    # and 'get_complex_artifact' is the name of the current function.
    # This dict is passed to check_in_media or check_in_embedded_media.
    current_artifact_info = __artifacts_v2__["complex_artifact"]
    ```

2.  **Call `check_in_media` or `check_in_embedded_media`**: These functions return a `media_ref_id` (string), which you then put into your `data_list`.

    *   **For files on disk (`check_in_media`):**
        ```python
        image_file_pattern = "**/path/to/image.jpg" # Pattern to find the media file
        found_image_path_in_extraction = get_file_path(files_found, image_file_pattern)
        
        media_ref_id = None
        if found_image_path_in_extraction:
            media_ref_id = check_in_media(
                artifact_info=current_artifact_info,
                report_folder=report_folder,
                seeker=seeker,
                files_found=files_found, 
                file_path=image_file_pattern, 
                name="Descriptive Name for Media Item" # Optional
            )
        # Add media_ref_id (or placeholder if None) to your data_list
        # e.g., data_list_for_part1.append((timestamp, event_details, media_ref_id))
        ```

    *   **For embedded binary data (`check_in_embedded_media`):**
        ```python
        binary_media_data = record['blob_column'] # Actual bytes of the media
        source_db_path = get_file_path(files_found, "**/source_app.db")
        
        media_ref_id = None
        if binary_media_data and source_db_path:
            media_ref_id = check_in_embedded_media(
                artifact_info=current_artifact_info,
                report_folder=report_folder, 
                seeker=seeker,
                source_file=source_db_path,
                data=binary_media_data,
                name="Embedded Media Item Name" # Optional
            )
        # Add media_ref_id to your data_list
        ```

4.  **Update `data_headers`**: For each `data_list` that will contain `media_ref_id`s, ensure the corresponding `data_headers` list marks that column with the type `'media'`.
    ```python
    # For data_headers_part1 if it has a media column:
    data_headers_part1 = [('Timestamp', 'datetime'), 'Description', ('Photo', 'media')]
    #
    # For data_headers_part2 if it also has media:
    data_headers_part2 = ['User', ('Attachment', 'media', 'max-width:50px;')] # Optional style for HTML
    ```
    This `'media'` type is essential for `lava_process_artifact` to correctly handle the `media_ref_id`. It also helps the manual HTML report generation if you have a helper function that understands this tuple format for media.

### 4. Add LAVA output generation to the main function

After processing data (including any media calls), generating your manual HTML and TSV reports, add the LAVA output generation for each distinct dataset.

```python
# In your main processing function, e.g., get_complex_artifact
def get_complex_artifact(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list1 = []
    data_list2 = []
    data_headers1 = ['Column1', 'Column2', 'Column3']
    data_headers2 = ['ColumnA', 'ColumnB', 'ColumnC']

    for file_found in files_found:
        # Process data and populate data_list1 and data_list2
        # ...

    # Generate HTML report for the first artifact
    report1 = ArtifactHtmlReport('Complex Artifact - Part 1')
    report1.start_artifact_report(report_folder, 'Complex Artifact - Part 1')
    report1.add_script()
    report1.write_artifact_data_table(data_headers1, data_list1, file_found)
    report1.end_artifact_report()

    # Generate TSV for the first artifact
    tsv(report_folder, data_headers1, data_list1, 'Complex Artifact - Part 1')

    # Generate HTML report for the second artifact
    report2 = ArtifactHtmlReport('Complex Artifact - Part 2')
    report2.start_artifact_report(report_folder, 'Complex Artifact - Part 2')
    report2.add_script()
    report2.write_artifact_data_table(data_headers2, data_list2, file_found)
    report2.end_artifact_report()

    # Generate TSV for the second artifact
    tsv(report_folder, data_headers2, data_list2, 'Complex Artifact - Part 2')

    # Generate LAVA output
    category = "Complex Artifact Category"
    module_name = "get_complex_artifact"

    # Add special data type handlers for LAVA output
    data_headers1[0] = (data_headers1[0], 'datetime')
    data_headers2[2] = (data_headers2[2], 'date')

    # Process first artifact for LAVA
    table_name1, object_columns1, column_map1 = lava_process_artifact(category, module_name, 'Complex Artifact - Part 1', data_headers1, len(data_list1))
    lava_insert_sqlite_data(table_name1, data_list1, object_columns1, data_headers1, column_map1)

    # Process second artifact for LAVA
    table_name2, object_columns2, column_map2 = lava_process_artifact(category, module_name, 'Complex Artifact - Part 2', data_headers2, len(data_list2))
    lava_insert_sqlite_data(table_name2, data_list2, object_columns2, data_headers2, column_map2)
```

## Important Notes

-   The `output_types` in `__artifacts_v2__` is set to `"none"` because any HTML/TSV generation is manual. LAVA output is added by directly calling `lava_process_artifact` and `lava_insert_sqlite_data`.
-   Call LAVA functions for *each distinct data table* you want to represent in LAVA.
-   The `category` comes from your `__artifacts_v2__` entry. The `module_name` for `lava_process_artifact` is the name of your Python artifact processing function (e.g., `get_complex_artifact`). The `artifact_name_for_lava` should be a unique, descriptive name for *that specific table* being generated.
-   Media Handling:
    *   Use `check_in_media` / `check_in_embedded_media` from `ilapfuncs.py`.
    *   Pass the `data` subfolder path (e.g., `os.path.join(report_folder, 'data')`) as the `report_folder` argument to these media functions.
    *   These functions handle copying/linking media and creating LAVA database entries (`media_items`, `media_references`).
    *   The `media_ref_id` returned is placed in your `data_list`.
    *   `lava_process_artifact` interprets this `media_ref_id` correctly when the column header is typed as `'media'`.

These changes will add LAVA output capability to your complex module while maintaining its existing HTML and TSV outputs and utilizing special data type handlers for LAVA.
