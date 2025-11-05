# iLEAPP AI Coding Instructions

## Project Overview
iLEAPP (iOS Logs, Events, And Plists Parser) is a forensics tool for extracting and analyzing artifacts from iOS devices. It processes iTunes backups, filesystem dumps, and compressed archives to generate comprehensive forensic reports.

## Core Architecture

### Plugin-Based Artifact System
- **Artifacts live in `scripts/artifacts/`** - Each `.py` file is an auto-loaded plugin
- **Plugin structure**: Every artifact module must define `__artifacts_v2__` dictionary at the top
- **Function decoration**: Use `@artifact_processor` decorator for entry points
- **Context pattern**: Modern artifacts use `Context` class instead of direct parameters

```python
__artifacts_v2__ = {
    "artifact_name": {  # Must match function name exactly
        "name": "Human Readable Name",
        "description": "Brief description", 
        "author": "@username",
        "category": "Category Name",
        "paths": ('*/path/to/files*',),  # Glob patterns for file search
        "output_types": "standard",  # or ["html", "tsv", "lava", "timeline"]
        "artifact_icon": "feather-icon-name"
    }
}

@artifact_processor
def artifact_name(context):
    files_found = context.get_files_found()
    # Process files and return data_headers, data_list, source_path
```

### Data Processing Pipeline
1. **File Discovery**: `search_files.py` finds artifacts using glob patterns from `paths`
2. **Plugin Loading**: `plugin_loader.py` dynamically loads all artifacts from `scripts/artifacts/`
3. **Context Management**: `context.py` provides global state and file access
4. **Report Generation**: `artifact_report.py` creates HTML/TSV/LAVA output formats

### Entry Points
- **CLI**: `ileapp.py` - Command line interface with batch processing support
- **GUI**: `ileappGUI.py` - Tkinter-based graphical interface
- **Batch processing**: JSON configuration files for multiple device analysis

## Development Patterns

### Artifact Development
- **File location**: New artifacts go in `scripts/artifacts/`
- **Import pattern**: `from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records`
- **Database access**: Use `get_sqlite_db_records()` for SQLite, `get_plist_file_content()` for plists
- **Return format**: `(data_headers, data_list, source_path)` tuple

### Common Functions (`scripts/ilapfuncs.py`)
- `get_sqlite_db_records(source_path, query)` - SQLite database queries
- `get_plist_file_content(file_path)` - Plist parsing
- `convert_ts_human_to_utc(timestamp)` - Timestamp conversion
- `artifact_processor` - Decorator for artifact functions

### File Search Patterns
- Use glob patterns in artifact `paths`: `'*/Library/SMS/sms.db*'`
- Wildcards support nested directories: `**/PhotoData/Thumbnails/**`
- Multiple patterns: `('path1', 'path2', 'path3')`

### Output Types
- `"standard"`: HTML + TSV + LAVA + timeline
- `["html", "tsv"]`: Specific formats only
- `"lava"`: LAVA database format for analysis tools
- `"timeline"`: Timeline visualization data

## Testing & Debugging

### Development Workflow
```bash
# Install dependencies
pip install -r requirements.txt

# Run single device analysis
python ileapp.py -t fs -i /path/to/device -o /path/to/output

# Run batch processing
python ileapp.py -b batch_config.json

# GUI mode for development
python ileappGUI.py
```

### Batch Configuration
Use `batch_example.json` as template for multi-device processing. Each entry requires:
- `input_path`, `output_path`, `type` (required)
- `timezone`, `custom_output_folder`, `profile` (optional)

### Profile System
- Create `.ilprofile` files to run specific artifact subsets
- Use `--create-profile` flag to generate profiles interactively
- Profiles contain JSON list of artifact modules to execute

## Key Directories
- `scripts/artifacts/` - All artifact parsers (500+ modules)
- `scripts/` - Core framework code (`ilapfuncs.py`, `search_files.py`, etc.)
- `admin/docs/` - Developer documentation for module updates
- `whl_files/` - Windows-specific binary dependencies

## iOS Forensics Context
- Supports iOS 11-17, various backup types (iTunes, filesystem, compressed)
- Handles encrypted iTunes backups (modern format only)
- Processes mobile containers, application data, system logs
- Common artifact types: SMS, call logs, photos, app data, location services

When adding new artifacts, follow the established `__artifacts_v2__` pattern and ensure proper categorization for the HTML report structure.