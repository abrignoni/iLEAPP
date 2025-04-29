# Artifact Info Block Structure

## Version 2 (current version)

The artifact info block is defined as a dictionary named `__artifacts_v2__` at the top of the artifact script. It contains key information about the artifact. Here's the structure:

```python
__artifacts_v2__ = {
    "function_name": {
        "name": "Human-readable name of the artifact",
        "description": "Brief description of what the artifact does",
        "author": "@AuthorUsername",
        "version": "X.Y",
        "date": "YYYY-MM-DD",
        "requirements": "Any specific requirements, or 'none'",
        "category": "Category of the artifact",
        "notes": "Additional notes, if any",
        "paths": ('Path/to/artifact/files',),
        "output_types": "Output types, often 'all'",
        "artifact_icon": "feather-icon-name"
    }
}
```

| Field Name      | Description                                                                                                                             | Required |
| :-------------- | :-------------------------------------------------------------------------------------------------------------------------------------- | :---------------- |
| `function_name` | The name of the function that processes this artifact. This should match exactly with the function name in the script.                  | Required          |
| `name`          | A human-readable name for the artifact as it will be displayed in the output files                                                      | Required          |
| `description`   | A brief explanation of what the artifact extracts or analyzes                                                                           | Encouraged          |
| `author`        | The name and/or username of the module's author                                                                                         | Encouraged          |
| `version`       | The current version of the module script                                                                                                | Required          |
| `date`          | The last updated date of the module in YYYY-MM-DD format                                                                                    | Required          |
| `requirements`  | Any specific requirements for the artifact, or "none" if there are no special requirements                                              | Optional          |
| `category`      | The category the artifact belongs to. Used to group artifacts into groups in parsed outputs.                                                                                                    | Required          |
| `notes`         | Any additional information about the artifact (can be an empty string)                                                                  | Optional          |
| `paths`         | A tuple containing one or more file paths (with wildcards if needed) where the artifact data can be found                                 | Required          |
| `output_types`  | Specifies the desired output formats. See 'Output Types Details' below for options.                                                     | Required          |
| `artifact_icon` | The name of the feathericon to display in the left sidebar ot the HTML report. List of available icons on [feathericons.com](https://feathericons.com) website | Optional          |

### Output Types Details

The `output_types` field accepts a list of strings or specific keywords:

-   `["html", "tsv", "lava", ...]` : A list containing any combination of supported output types.
-   `"all"`: Generates all available output types.
-   `"standard"`: Generates HTML, TSV, LAVA, and timeline output.

#### Individual options:
-   `"html"`: Generates HTML output.
-   `"tsv"`: Generates TSV (Tab-Separated Values) output.
-   `"timeline"`: Generates timeline output.
-   `"lava"`: Generates output for LAVA (a specific data processing format).
-   `"kml"`: Generates KML (Keyhole Markup Language) output for Google Earth.
-   `"none"`: No report output generated (useful for modules only collecting device info).

### Purpose

This info block provides essential metadata about the artifact and is used by the artifact processor to handle the artifact correctly. The plugin loader will attach this information to the corresponding function, making it accessible via the function's globals.

Note: The key in the `__artifacts_v2__` dictionary must exactly match the name of the function that processes the artifact. This ensures that the artifact processor can correctly associate the artifact information with the processing function.

## Version 3 (Not implemented yet)

The artifact info block is defined as a dictionary named `__artifacts_v3__` at the top of the artifact script. It contains key information about the artifact. Here's the updated structure:

```python
__artifacts_v3__ = {
    "name": "Human-readable name of the module",
    "description": "Brief description of what the module does",
    "author": "@AuthorUsername",
    "version": "X.Y",
    "date": "YYYY-MM-DD",
    "requirements": "Any specific requirements, or 'none'",
    "performance_profile": "normal", # Options: "fast", "normal", "slow"
    "app_name": "Name of the app this module parses data from",
    "app_id": "Bundle ID or domain associated with the app",
    "category": "Category of the artifact",
    "category_icon": "feather-icon-name",
    "notes": "Additional notes, if any",
    "module_paths": ('Path/to/source/files',),
    "artifacts": {
        "artifact_function_name": {
            "name": "Specific Artifact Display Name",
            "paths": ('Path/to/source/files',),
            "artifact_icon": "feather-icon-name",
            "artifact_notes": "Notes to be displayed at the top of the report",
            "artifact_warning": "Warning message to be displayed prominently"
        },
        # Additional artifacts can be added here
    }
}
```

Key changes and additions:

- `name`: The overall display name of the module
- `app_name`: The name of the application this module parses data from
- `app_id`: The bundle ID or domain developers have used when creating the app and submitting to app stores
- `category_icon`: An icon (using Feather icons names) for the category
- `module_paths`: A tuple containing one or more file paths (with wildcards if needed) where the artifact data can be found. This serves as a default for all artifacts within the module.
- `performance_profile`: Hint about the module's processing time. Options: `"fast"`, `"normal"`, `"slow"`. Defaults to `"normal"` if omitted. Used for UI feedback.
- `artifacts`: A dictionary of artifacts, where each key is the artifact name and the value is a dictionary containing details about that specific artifact:
  - `paths`: (Optional) A tuple of paths specific to this artifact. If provided, it overrides the `module_paths` for this artifact.
  - `artifact_icon`: An icon specific to this artifact (using Feather icons names)
  - `artifact_notes`: Notes to be displayed at the top of the artifact's report
  - `artifact_warning`: A warning message to be displayed prominently for this artifact

Note on paths:
At least one of `module_paths` or `paths` must be provided. The `module_paths` serves as a default search path for all artifacts within the module. Individual artifacts can override this by specifying their own `paths`. This allows for flexibility in defining search paths at both the module and artifact levels.

The plugin loader and artifact processing code will need to be updated to handle this new structure, particularly in how it determines the search paths for each artifact and generates reports.
