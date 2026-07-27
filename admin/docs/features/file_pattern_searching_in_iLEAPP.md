# File Pattern Searching in iLEAPP

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
             "version": "1.0",
             "date": "2023-05-24",
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


## File Seekers (`search_files.py`)

The `search` method aims to find the files that match a pattern in the extraction, extract and copy them into the report `data` folder, then return their location in a list.
When a file matches the pattern:
- its original location, creation and modification dates are extracted to be stored in the `files_infos` data structure, a dictionary with the key corresponding to 
the location where the file was extracted and the value to a `FileInfo` object;
- it is extracted into the report `data` directory and a trace of its copy is recorded into `copied`, a Set that stores the original location in the extraction.

The result of each search is stored in a dictionary (`searched`) whose key contains the pattern provided and the value a list with the path of extracted files in the `data` folder.
Searching for files within zip, tar or tar.gz archives and then copying them becomes quickly time-consuming, especially when this operation is performed frequently. 
This is why when the `search` method is called, it starts by checking if the `searched` dictionary already contains the pattern and then provides a list containing paths 
of corresponding files in the `data` folder.
If a different pattern leads to finding files that have already been extracted, the files are not copied again due to the stored trace of their copy in the `copied` Set.

This method accepts an optional setting:
- `return_on_first_hit`: which allows to stop the search as soon as the first file has been found and copied into the `data` folder. This feature is particularly 
useful when searching for a media-type file whose pattern is specific enough to target only one file in the extraction.
