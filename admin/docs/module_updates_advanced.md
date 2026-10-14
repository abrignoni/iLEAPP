# Updating Complex Modules to Include LAVA Output

This guide outlines the process of updating existing complex xLEAPP modules to include LAVA output. These modules typically process a single group of file pattern searches but generate multiple HTML and TSV outputs.

*Note that if you are just attempting to split output into multiple HTML pages or just handle HTML manually for some other reason but the LAVA and TSV is a single table/output you can probably still use the instructions found in [Updating Modules for Automatic Output Generation](module_updates.md). (Refer to `carCD.py` for an example of manual HTML with automatic LAVA/TSV processing)*

## Key Changes

1.  Update the `__artifacts_v2__` block
2.  Modify imports (add LAVA functions)
3.  Media files
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

Add imports for the LAVA functions.

```python
# Existing imports for your module...
# import scripts.artifact_report # For manual HTML reports
# from scripts.ilapfuncs import tsv # For manual TSV

# Add these for LAVA:
from scripts.lavafuncs import lava_process_artifact, lava_insert_sqlite_data
```

### 3. Media Files

The media helpers, `check_in_media` and `check_in_embedded_media`, read the module name,
artifact name, seeker and output folders from the context that `@artifact_processor` sets
up. A module that writes its own output with `output_types` set to `"none"` and no decorator
has no context, so it cannot call them.

If a table needs a media column, give that table its own `@artifact_processor` function
and its own entry in `__artifacts_v2__`. A module can hold several decorated functions.
See [Checking in media](helper_functions.md#checking-in-media).

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
-   Media: the media helpers need `@artifact_processor`. Put a table with a media column in its own decorated function (see step 3).

These changes will add LAVA output capability to your complex module while maintaining its existing HTML and TSV outputs and utilizing special data type handlers for LAVA.
