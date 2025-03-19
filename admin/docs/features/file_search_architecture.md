# ADR: File Pattern Searching in iLEAPP

## Status

Proposed

## Context

The iLEAPP system currently uses a file searching mechanism defined at the plugin level. As the system grows and becomes more complex, there's a need for a more robust and flexible file searching mechanism.

## Decision

We propose to enhance the file pattern searching mechanism to improve flexibility, granularity, and performance.

## Current Architecture

The current file search architecture in iLEAPP is structured as follows:

1. Main Script (`ileapp.py`):
   - Initializes the search process
   - Iterates through plugins and calls their search methods

2. Plugin Loader (`plugin_loader.py`):
   - Loads plugins dynamically
   - Parses the `__artifacts__` or `__artifacts_v2__` blocks in each plugin

3. Plugin Structure:
   - Each plugin defines its search patterns in the artifact info block
   - Example structure:
     ```python
     __artifacts_v2__ = {
         "ArtifactName": {
             "name": "Artifact Display Name",
             "description": "Artifact description",
             "author": "@AuthorUsername",
             "creation_date": "2023-05-24",
             "last_update_date": "2024-12-17",
             "requirements": "none",
             "category": "Category",
             "notes": "",
             "paths": ('path/to/artifact/files',),
             "function": "function_name_for_this_artifact"
         }
     }
     ```

4. File Seekers (`search_files.py`):
   - Contains different file seeker classes for various input types:
     - `FileSeekerDir` for directory searches
     - `FileSeekerItunes` for iTunes backups
     - `FileSeekerTar` for tar archives
     - `FileSeekerZip` for zip archives
   - Each seeker implements a `search` method that takes a file pattern and returns matching files

This architecture allows for plugin-based artifact definition and searching but lacks granularity in defining search patterns and doesn't provide a clear separation between module-level and artifact-level searches. The issue is that some modules produce multiple data sets that should be distinct displays but share the same search pattern. This causes a duplication of the search pattern across artifacts within the same module and potentially a performance impact as the module processes the provided files.

## Proposal #1: Module and Artifact Level Patterns

We propose to enhance the file pattern searching mechanism with the following changes:

1. Introduce module-level and artifact-level search patterns.
2. Implement a new structure in the `__artifacts_v3__` dictionary to accommodate these changes.
3. Modify the plugin loader and artifact processing code to handle the new structure.
4. Keep the `"paths"` key in the artifact object to reduce the risk of breaking changes.
5. Add new `"module_paths"` key to the module object to define the search pattern at the module level.
6. Retain compatibility with the current `"paths"` key in the v2 artifact object.
7. Ensure the search engine is efficient with multiple artifacts that share the same search pattern.

### New Structure

The new `__artifacts_v3__` structure will include module-level and artifact-level paths:

```python
__artifacts_v3__ = {
    ...
    "module_paths": ('Path/to/source/files',),
    "artifacts": {
        "artifact_name": {
            ...
            "paths": ('Path/to/source/files',),
            ...
        },
    }
}
```

This structure allows for defining search patterns at both the module and artifact levels. The `module_paths` will serve as a default for all artifacts within the module, while individual artifacts can override this with their own `paths`.

For the complete `__artifacts_v3__` structure, refer to the [Artifact Info Block documentation](../artifact_info_block.md).

### Consequences

Positive:
1. Greater flexibility in defining search patterns at both module and artifact levels.
2. Improved organization of artifacts within modules.
3. Better control over which files are processed for each artifact.
4. Potential performance improvements by allowing more specific file targeting.

Negative:
1. Requires significant changes to the existing codebase.
2. May introduce complexity in the plugin development process.
3. Existing plugins will need to be updated to the new format.

## Proposal #2: Enhanced Contextual Search Patterns

We propose to implement a more intelligent and context-aware file search mechanism that can differentiate between full file system (FFS) extractions and iTunes backups, and utilize additional contextual information to improve search accuracy and efficiency.

### Current Limitations (Example):

The current search pattern structure can lead to overly broad searches, resulting in unnecessary processing and potential performance issues. For instance, the ChatGPT plugin (`chatgpt.py`) includes a very broad search pattern:

```python
"paths": (
    # ... other paths ...
    '**/Containers/Data/Application/*/tmp/*/*.*',
)
```

This pattern is used because the plugin doesn't know the specific identifier for the ChatGPT app at the time the artifact info block is defined. As a result:

1. The search returns all files in the `/tmp/` folders of all apps on the device.
2. The plugin's function code must then filter these results to find the relevant files.
3. This approach increases the number of files processed and can impact performance, especially on devices with many apps.

### Key Components:

1. **Source Type Detection**: 
   - Implement a mechanism to detect whether the source is an iTunes backup or a full file system extraction.
   - For iTunes backups, check for the existence of `manifest.db` or `manifest.plist` near the root.

2. **Domain-Aware Searching for iTunes Backups**:
   - Utilize the `manifest.db` file in iTunes backups to associate domains with file paths.
   - Allow modules to specify domain information in their search patterns for more precise file targeting.

3. **Application Container Awareness for FFS Extractions**:
   - Implement a pre-processing step to parse application state information (similar to the `applicationstate.py` plugin) before running individual modules.
   - Store and provide access to GUID/identifier information for each application.

4. **Enhanced Search Pattern Structure**:
   - Modify the search pattern structure to include optional contextual information:

```python
"search_patterns": [
    {
        "pattern": "tmp/*/*.*",
        "context": {
            "itunes_domain": "com.openai.chat-AppContainer",
            "ffs_app_id": "com.openai.chat"
        }
    }
]
````


With this enhanced structure, the ChatGPT plugin could specify its search patterns more precisely, reducing the number of irrelevant files processed.

### Benefits:

1. More precise file targeting, reducing the number of false positives in search results.
2. Improved performance by narrowing down the search scope, especially for common filenames or paths.
3. Better handling of different extraction types (FFS vs. iTunes backup) within the same module.
4. Enables modules to process backup file data more effectively, even with limited file sets.
5. Reduces the need for post-search filtering within plugin functions, simplifying plugin code.

### Challenges:

1. Requires significant changes to the existing search mechanism and module structure.
2. Need to ensure backward compatibility with existing modules.
3. May introduce additional complexity in module development.

