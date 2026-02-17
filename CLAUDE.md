# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

iLEAPP (iOS Logs, Events, And Plists Parser) is a digital forensics tool that extracts and parses artifacts from iOS/iPadOS devices (versions 11-17). It reads from filesystem extractions, tar/zip/gz archives, and iTunes/Finder backups (including encrypted ones), producing HTML reports, TSV files, LAVA databases, timelines, and KML files.

## Commands

```bash
pip install -r requirements.txt                                          # Install dependencies
python ileapp.py -t <fs|tar|zip|gz|itunes|file> -i <input> -o <output>  # CLI
python ileappGUI.py                                                      # GUI
PYTHONPATH=. pylint <file.py> --disable=C,R                              # Lint (CI enforced)
```

Python 3.10 to 3.12. On Linux, also: `sudo apt-get install python3-tk`

Pylint CI runs with `--disable=C,R` (convention and refactor checks disabled; only warnings and errors enforced).

## Architecture

### Execution Flow

1. **Entry point** (`ileapp.py` or `ileappGUI.py`) validates args, creates `OutputParameters`, initializes LAVA database
2. **Plugin discovery** — `PluginLoader` (`scripts/plugin_loader.py`) scans `scripts/artifacts/*.py` for modules containing `__artifacts_v2__` (or legacy `__artifacts__`) dictionaries. Modules are loaded lazily via `importlib.util.LazyLoader`
3. **File seeker creation** — Based on input type, one of: `FileSeekerDir`, `FileSeekerTar`, `FileSeekerZip`, `FileSeekerItunes`, `FileSeekerFile` (all in `scripts/search_files.py`)
4. **Artifact processing loop** — For each plugin, the seeker finds matching files using the plugin's `paths` glob patterns, then calls `plugin.method(files_found, category_folder, seeker, wrap_text, time_offset)`
5. **Report generation** — `scripts/report.py` assembles the final HTML report from individual `.temphtml` artifact reports

### Key Modules

- **`scripts/plugin_loader.py`** — `PluginLoader` and `PluginSpec` dataclass. Discovers plugins, resolves function references, enforces unique names
- **`scripts/ilapfuncs.py`** — Core utilities: `artifact_processor` decorator, `logfunc()`, `logdevinfo()`, `open_sqlite_db_readonly()`, `get_sqlite_db_records()`, `get_plist_file_content()`, `check_in_media()`, `convert_human_ts_to_utc()`, output type helpers, `iOS` version singleton, `OutputParameters`, `GuiWindow`
- **`scripts/search_files.py`** — `FileSeekerBase` and all seeker implementations. Also handles iTunes backup domain mapping and encrypted backup decryption
- **`scripts/context.py`** — `Context` class with static state for the currently-running artifact (report folder, seeker, files found, artifact info, module name). Set by `artifact_processor`, read by plugins via `context.get_files_found()` etc.
- **`scripts/artifact_report.py`** — `ArtifactHtmlReport` class for writing individual HTML report files
- **`scripts/lavafuncs.py`** — LAVA output: SQLite database (`_lava_artifacts.db`) + JSON metadata (`_lava_data.lava`). Functions for table creation, data insertion, media item tracking
- **`scripts/report.py`** — Final HTML report assembly with sidebar navigation and feathericons
- **`scripts/modules_to_exclude.py`** — List of slow-running Photo modules deselected by default in GUI

### Plugin System (Artifact Modules)

All artifact plugins live in `scripts/artifacts/`. Each is a standalone Python file loaded dynamically.

**Plugin structure:**

```python
__artifacts_v2__ = {
    "function_name": {           # Must match the function name exactly
        "name": "Display Name",
        "description": "...",
        "author": "@username",
        "version": "0.1",
        "date": "YYYY-MM-DD",
        "requirements": "none",
        "category": "Category Name",
        "notes": "",
        "paths": ('*/path/to/files*',),     # Tuple of glob patterns
        "output_types": "all",               # or "standard", ["html","tsv"], "lava_only", "none"
        "artifact_icon": "feather-icon-name"
    }
}

from scripts.ilapfuncs import artifact_processor

@artifact_processor
def function_name(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    # ... process files, query SQLite dbs, parse plists ...
    data_headers = (('Column1', 'datetime'), 'Column2', 'Column3')
    return data_headers, data_list, source_path
```

**Two function signatures are supported** by `artifact_processor`:
- **Legacy (5-arg):** `func(files_found, report_folder, seeker, wrap_text, timezone_offset)`
- **Context (1-arg):** `func(context)` — where `context` is the `Context` class with methods like `context.get_files_found()`, `context.get_report_folder()`, etc.

The decorator detects which signature to use via `inspect.signature`. Newer plugins (e.g., `Airbnb.py`) use the context pattern.

**Data header conventions:**
- Plain string: `'Column Name'` — regular column
- Tuple with `'datetime'`: `('Column Name', 'datetime')` — marks column for timeline output
- Tuple with `'media'`: `('Column Name', 'media')` — marks column for media handling

**Output types:**
- `"all"` — HTML + TSV + timeline + LAVA + KML
- `"standard"` — HTML + TSV + timeline + LAVA (no KML)
- `"none"` — no report output (for device info collection only)
- `"lava_only"` — LAVA database only

### File Seekers

Each seeker implements `FileSeekerBase.search(filepattern)` which takes a glob pattern and returns a list of file paths. The seeker extracts matched files to the `data_folder` and tracks `FileInfo` metadata (source path, creation/modification dates).

For iTunes backups, `FileSeekerItunes` handles domain-to-path mapping (e.g., `HomeDomain` → `private/var/mobile`) and optional AES decryption of encrypted backups.

### Common Utility Patterns

- **SQLite**: `open_sqlite_db_readonly(path)` opens in read-only mode preserving WAL/journal. `get_sqlite_db_records(path, query)` is a convenience wrapper returning `sqlite3.Row` objects
- **Plists**: `get_plist_file_content(path)` handles both standard and NSKeyedArchiver plists (auto-deserializes via `nska_deserialize`)
- **Media**: `check_in_media(file_path)` registers media files in the LAVA database and creates hardlinks in the report media folders
- **Device info**: `logdevinfo(message)` writes to device info log; the `identifiers` dict collects device metadata across all plugins
- **iOS version**: `iOS.set_version()` / `iOS.get_version()` — set once by the `last_build` plugin, available to all subsequent plugins
