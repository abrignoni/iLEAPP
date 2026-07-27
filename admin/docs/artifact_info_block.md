# Artifact Info Block Structure

## Version 2 (current version)

The artifact info block is defined as a dictionary named `__artifacts_v2__` at the top of the artifact script. It contains key information about the artifact. Here's the structure:

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
        "artifact_icon": "Tabler-icon-name",
        "sample_data": {
            "sample_name": "Short note about where this artifact has been tested"
        }
    }
}
```

| Field Name      | Description                                                                                                                             | Required |
| :-------------- | :-------------------------------------------------------------------------------------------------------------------------------------- | :---------------- |
| `function_name` | The name of the function that processes this artifact. This should match exactly with the function name in the script.                  | Required          |
| `name`          | A human-readable name for the artifact as it will be displayed in the output files | Required          |
| `description`   | A brief explanation of what the artifact extracts or analyzes | Encouraged          |
| `author`        | The name and/or username of the module's author | Encouraged          |
| `creation_date` | Date when artifact was created, in YYYY-MM-DD format | Encouraged |
| `last_update_date` | Date when artifact was last updated, in YYYY-MM-DD format | Encouraged |
| ~`version`~       | ~The current version of the module script~ | Deprecated          |
| ~`date`~          | ~The last updated date of the module in YYYY-MM-DD format~ | Deprecated          |
| `requirements`  | Any specific requirements for the artifact, or "none" if there are no special requirements. No automation or anything connected, just a note  | Optional          |
| `category`      | The category the artifact belongs to. Used to group artifacts into groups in parsed outputs.                                                                                                    | Required          |
| `notes`         | Any additional information about the artifact (can be an empty string) | Optional          |
| `paths`         | A tuple containing one or more file paths (with wildcards if needed) where the artifact data can be found                                 | Required          |
| `output_types`  | Specifies the desired output formats. See 'Output Types Details' below for options.                                                     | Required          |
| `artifact_icon` | The name of the Tabler icon to display in the left sidebar ot the HTML report. List of available icons on [tabler.io](https://tabler.io/icons) website | Optional          |
| `sample_data`   | Optional human-readable notes about known sample data or test coverage for the artifact. This can include local image names, test case names, row counts, OS versions, or schema variations that were verified. Not used by the artifact processor. | Optional          |

Example:

```python
"sample_data": {
    "josh_ios_15": "23 rows; ZPEERINFO contains peer OS/model/name values",
    "mvs_2026": "6 rows; ZPEERINFO is empty"
}
```

### Path Pattern Matching

The `paths` tuple uses **glob-like** wildcards, but matching is performed by Python's `fnmatch` module in `scripts/search_files.py` — not by `glob` or `pathlib`. Keep the following in mind when writing patterns:

- **Not strict glob semantics.** In true glob (`pathlib`), `*` matches a single path segment and `**` matches zero or more directories recursively. In `fnmatch` (Python 3.11+), `*` and `**` are largely interchangeable — both can span `/` characters. Patterns like `*/mobile/...` and `**/mobile/...` therefore behave the same in practice.
- **Patterns are permissive.** A single `*` in a path pattern may match more than one directory level. Do not assume `*` is limited to one path component.
- **Case sensitivity depends on platform.** For filesystem, tar, and zip extractions, paths are normalized with `os.path.normcase` before matching. On Windows this makes matching case-insensitive; on macOS and Linux it is case-sensitive. iTunes backup matching (`FileSeekerItunes`) does not apply `normcase`, so it is always case-sensitive.
- **Leading `**/` is common.** Patterns such as `**/Safari/History.db` match the suffix of a full extraction path. This works because the seeker prepends a synthetic `root/` prefix to absolute paths before matching.

### Output Types Details

The `output_types` field accepts a list of strings or specific keywords:

-   `["html", "tsv", "lava", ...]` : A list containing any combination of supported output types.
-   `"all"`: Generates all available output types.
-   `"standard"`: Generates `HTML`, `TSV`, `LAVA`, and `timeline` output.

#### Individual options:
-   `"html"`: Generates HTML output.
-   `"tsv"`: Generates TSV (Tab-Separated Values) output.
-   `"timeline"`: Generates timeline output.
-   `"lava"`: Generates output for LAVA (a specific data processing format).
-   `"kml"`: Generates KML (Keyhole Markup Language) output for Google Earth.
-   `"none"`: No report output generated (useful for modules only collecting device info).

### Alternate Views

This section defines additional view types that artifacts can declare configurations for. Every artifact gets a basic `table` view. At this time, the table view does not have any configuration but that may be added in the future. These are alternate views that examiners can use to evaluate the data in a different format.

#### Conversation View
The chat view is designed for artifacts containing conversation-like data, such as messages or chat logs. It presents data in a format similar to messaging applications.

NOTE: Previous version of this confifuration used `"chat"` and "`thread`" in these configs but they have been deprecated. These will still work for now, but those keywords will be removed from LAVA in a few versions once modules have been updated.

``` python
__artifacts_v2__ = {
    "get_artifactname": {
        # Other parameters as shown above,
        "data_views": {
            "table": {}, # optional
            "conversation": {
                "conversationDiscriminatorColumn": "Chat ID",
                "conversationLabelColumn": "Chat Contact ID",
                "textColumn": "Message",
                "senderColumn": "Chat Contact ID",
                "directionColumn": "From Me",
                "directionSentValue": 1,
                "timeColumn": "Message Timestamp",
                "sentMessageLabelColumn": "Account"
            }
        }
    }
```

##### Conversation View Configuration Fields

- `conversationDiscriminatorColumn`: Identifies the column containing the unique identifier for each conversation.
- `conversationLabelColumn`: (Optional) Specifies the column used to label or name each conversation (e.g., contact name, group chat name). If omitted the conversation will be named by the `conversationDiscriminatorColumn`
- `textColumn`: Indicates the column containing the main message text.
- `senderColumn`: Identifies the column containing the sender's information.
- `directionColumn`: Specifies the column indicating whether a message was sent or received.
- `directionSentValue`: Defines the value in the `directionColumn` that indicates a sent message.
- `timeColumn`: Indicates the column containing the timestamp for each message.
- `sentMessageLabelColumn`: (Optional) Specifies the column used to label sent messages (e.g., the account used to send the message). This will override `senderColumn` for any messages determined to be sent. 
- `sentMessageStaticLabel`: (Optional) Specificies a static sender label for sent messages if there is no column containing a local sender id. This will override `sentMessageLabelColumn` or `senderColumn` for any messages determined to be sent.

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
    "creation_date": "YYYY-MM-DD",
    "last_updated_date": "YYYY-MM-DD",
    "requirements": "Any specific requirements, or 'none'",
    "performance_profile": "normal", # Options: "fast", "normal", "slow"
    "app_name": "Name of the app this module parses data from",
    "app_id": "Bundle ID or domain associated with the app",
    "category": "Category of the artifact",
    "category_icon": "Tabler-icon-name",
    "notes": "Additional notes, if any",
    "module_paths": ('Path/to/source/files',),
    "artifacts": {
        "artifact_function_name": {
            "name": "Specific Artifact Display Name",
            "paths": ('Path/to/source/files',),
            "artifact_icon": "Tabler-icon-name",
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
- `category_icon`: An icon (using Tabler icons names) for the category
- `module_paths`: A tuple containing one or more file paths (with wildcards if needed) where the artifact data can be found. This serves as a default for all artifacts within the module.
- `performance_profile`: Hint about the module's processing time. Options: `"fast"`, `"normal"`, `"slow"`. Defaults to `"normal"` if omitted. Used for UI feedback.
- `artifacts`: A dictionary of artifacts, where each key is the artifact name and the value is a dictionary containing details about that specific artifact:
  - `paths`: (Optional) A tuple of paths specific to this artifact. If provided, it overrides the `module_paths` for this artifact.
  - `artifact_icon`: An icon specific to this artifact (using Tabler icons names)
  - `artifact_notes`: Notes to be displayed at the top of the artifact's report
  - `artifact_warning`: A warning message to be displayed prominently for this artifact

Note on paths:
At least one of `module_paths` or `paths` must be provided. The `module_paths` serves as a default search path for all artifacts within the module. Individual artifacts can override this by specifying their own `paths`. This allows for flexibility in defining search paths at both the module and artifact levels.

The plugin loader and artifact processing code will need to be updated to handle this new structure, particularly in how it determines the search paths for each artifact and generates reports.
