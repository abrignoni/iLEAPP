# iLEAPP

iOS Logs, Events, And Plists Parser  
Details in blog post here: https://abrignoni.blogspot.com/2019/12/ileapp-ios-logs-events-and-properties.html

Supports iOS/iPadOS 11, 12, 13, 14, 15, 16, and 17.
Select parsing directly from a compressed .tar/.zip file, or a decompressed directory, or an iTunes/Finder backup folder.

## Features

Parses:  
⚙️ Mobile Installation Logs  
⚙️ iOS 12+ Notifications  
⚙️ Build Info (iOS version, etc.)  
⚙️ Wireless cellular service info (IMEI, number, etc.)  
⚙️ Screen icons list by screen and in grid order.  
⚙️ ApplicationState.db support for app bundle ID to data container GUID correlation.   
⚙️ User and computer names that the iOS device connected to. Function updated by Jack Farley (@JackFarley248, http://farleyforensics.com/).  
etc...

## Requirements

Python 3.10 to Python 3.12.<br>
If on macOS (Intel) make sure Xcode is installed and have command line tools updated to be able to use Python 3.11. 

### Dependencies

Dependencies for your python environment are listed in `requirements.txt`. Install them using the below command. Ensure 
the `py` part is correct for your environment, eg `py`, `python`, or `python3`, etc. 

`py -m pip install -r requirements.txt`  
or  
 `pip3 install -r requirements.txt`

To run on **Linux**, you will also need to install `tkinter` separately like so:

`sudo apt-get install python3-tk`

To install on Windows follow the guide, courtesy of Hexordia, here:
https://www.hexordia.com/s/ILEAPP-Walkthrough.pdf

Windows installation and walkthrough video, by Hexordia, here:
https://www.youtube.com/watch?v=7qvVFfBM2NU

## Compile to executable

To compile to an executable so you can run this on a system without python installed.
If using Python 3.10 and above delete the arguments from the following terminal commands.

*Windows OS*

To create ileapp.exe, run:

```
pyinstaller \scripts\pyinstaller\ileapp.spec
```

To create ileappGUI.exe, run:

```
pyinstaller \scripts\pyinstaller\ileappGUI.spec
```

*macOS*

To create ileapp, run:

```
pyinstaller /scripts/pyinstaller/ileapp_macos.spec
```

To create ileappGUI.app, run:

```
pyinstaller /scripts/pyinstaller/ileappGUI_macos.spec
```

## Usage

### CLI

```
$ python ileapp.py -t <zip | tar | fs | gz> -i <path_to_extraction> -o <path_for_report_output>
```

### GUI

```
$ python ileappGUI.py 
```

### Help

```
$ python ileapp.py --help
```

## Contributing artifact plugins

Each plugin is a Python source file which should be added to the `scripts/artifacts` folder which will be loaded dynamically each time ILEAPP is run.

The plugin source file must contain a dictionary named `__artifacts_v2__` at the very beginning of the module, which defines the artifacts that the plugin processes. The keys in the `__artifacts_v2__` dictionary should be IDs for the artifact(s) which must be unique within ILEAPP. The values should be dictionaries containing the following keys:

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

- `function_name`: The name of the function that processes this artifact. This should match exactly with the function name in the script.
- `name`: A human-readable name for the artifact as it will be displayed in the output files
- `description`: A brief explanation of what the artifact extracts or analyzes
- `author`: The name and/or username of the module's author
- `version`: The current version of the module script
- `date`: The date of the latest update in YYYY-MM-DD format
- `requirements`: Any specific requirements for the artifact, or "none" if there are no special requirements
- `category`: The category the artifact belongs to
- `notes`: Any additional information about the artifact (can be an empty string)
- `paths`: A tuple containing one or more file paths (with wildcards if needed) where the artifact data can be found
- `output_types`: A list of strings or the string 'all' specifying the types of output the artifact produces. Options are:
  - `["html", "tsv", "lava", ...]`: A list containing any combination of these values
  - `"all"`: Generates all available output types
  - `"standard"`: Generates HTML, TSV, LAVA,and timeline output
  - Individual options:
    - `"html"`: Generates HTML output
    - `"tsv"`: Generates TSV (Tab-Separated Values) output
    - `"timeline"`: Generates timeline output
    - `"lava"`: Generates output for LAVA (a specific data processing format)
    - `"kml"`: Generates KML (Keyhole Markup Language) output for Google Earth
    - `"none"`: Any output generated (For modules only collecting device info)
- `artifact_icon`: The name of a feathericon to display in the left sidebar ot the HTML report

This info block provides essential metadata about the artifact and is used by the artifact processor to handle the artifact correctly. The plugin loader will attach this information to the corresponding function, making it accessible via the function's globals.

Note: The key in the `__artifacts_v2__` dictionary must exactly match the name of the function that processes the artifact. This ensures that the artifact processor can correctly associate the artifact information with the processing function.

The functions referenced as entry points in the `__artifacts__` dictionary must be preceded by @artifact_processor and take the following arguments:

* An iterable of the files found which are to be processed (as strings)
* The path of ILEAPP's output folder(as a string)
* The seeker (of type FileSeekerBase) which found the files
* A Boolean value indicating whether or not the plugin is expected to wrap text

For example:

```python
def get_cool_data1(files_found, report_folder, seeker, wrap_text):
    pass  # do processing here
```

Plugins are generally expected to provide output in ILEAPP's LAVA output format, HTML, TSV, and optionally submit records to 
the timeline and/or kml files. Functions for generating this output can be found in the `artifact_report` and `ilapfuncs` modules. 
At a high level, an example might resemble:

```python
__artifacts_v2__ = {
    "cool_artifact_1": {
        "name": "Cool Artifact 1",
        "description": "Extracts cool data from database files",
        "author": "@username",  # Replace with the actual author's username or name
        "version": "0.1",  # Version number
        "date": "2022-10-25",  # Date of the latest version
        "requirements": "none",
        "category": "Really cool artifacts",
        "notes": "",
        "paths": ('*/com.android.cooldata/databases/database*.db',),
        "output_types": "Output types, often 'all'",
        "artifact_icon": "feather-icon-name"
    }
}

from scripts.ilapfuncs import artifact_processor

@artifact_processor
def get_artifactname(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    source_path = ''

    for file_found in files_found:
        source_path = str(file_found)

        # ... process data ...
        data_list.append((col1, col2, col3))

    data_headers = (('Column1', 'datetime'), 'Column2', 'Column3')
    return data_headers, data_list, source_path
```

For more information, read:
- [Updating Modules for Automatic Output Generation](admin/docs/module_updates.md)
- [Updating Complex Modules to Include LAVA Output](admin/docs/module_updates_advanced.md)

## Acknowledgements

This tool is the result of a collaborative effort of many people in the DFIR community.
