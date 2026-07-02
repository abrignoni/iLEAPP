"""
This module provides shared history and settings management for LEAPP tools.

It handles:
- OS-specific shared directory resolution (Windows, macOS, Linux).
- Atomic JSON read/write operations for settings and history data.
- Opt-in history tracking for input paths, output paths, and tool runs.
- Shared configuration across different LEAPP parsers and LAVA.

The data is stored in the user's application data directory:
- Windows: %APPDATA%/LEAPP
- macOS: ~/Library/Application Support/LEAPP
- Linux: ~/.config/LEAPP
"""

import os
import json
import platform
import datetime
import logging
from pathlib import Path

# Setup logging to avoid interrupting the main process
logger = logging.getLogger(__name__)

SCHEMA_VERSION = 1

_WINDOWS_EXTENDED_PREFIX = '\\\\?\\'
_WINDOWS_EXTENDED_UNC_PREFIX = '\\\\?\\UNC\\'


def _strip_windows_extended_prefix(path):
    """
    Removes the Windows extended-length path prefix if present.
    """
    if path.startswith(_WINDOWS_EXTENDED_UNC_PREFIX):
        return '\\\\' + path[len(_WINDOWS_EXTENDED_UNC_PREFIX):]
    if path.startswith(_WINDOWS_EXTENDED_PREFIX):
        return path[len(_WINDOWS_EXTENDED_PREFIX):]
    return path


def _path_history_key(path):
    """
    Returns a canonical path string for deduplication comparisons.
    """
    path = _strip_windows_extended_prefix(path)
    path = os.path.normpath(path)
    if platform.system() == "Windows":
        path = os.path.normcase(path)
    return path


def _is_windows_drive_path(path):
    """
    Returns True if path is a Windows drive-letter path (e.g. C:\\foo).
    """
    return len(path) >= 2 and path[1] == ':'


def _with_windows_extended_prefix(path):
    """
    Adds the Windows extended-length prefix for drive-letter paths.
    """
    path = _path_history_key(path)
    if platform.system() == "Windows" and _is_windows_drive_path(path):
        return _WINDOWS_EXTENDED_PREFIX + path
    return path


def _normalize_stored_path(path, prefer_long_path=False):
    """
    Normalizes a path for storage in history.
    """
    canonical = _path_history_key(path)
    if prefer_long_path:
        return _with_windows_extended_prefix(canonical)
    return canonical


def format_path_for_display(path):
    """
    Returns a user-friendly path string for display in menus and UI.
    """
    return _strip_windows_extended_prefix(path)


def get_shared_directory():
    """
    Returns the OS-specific shared directory for LEAPP.
    Windows: %APPDATA%\\LEAPP
    macOS: ~/Library/Application Support/LEAPP
    Linux: ~/.config/LEAPP (or $XDG_CONFIG_HOME/LEAPP)
    """
    home = Path.home()
    system = platform.system()

    if system == "Windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "LEAPP"
        return home / "AppData" / "Roaming" / "LEAPP"
    elif system == "Darwin":
        return home / "Library" / "Application Support" / "LEAPP"
    else:  # Linux and others
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            return Path(xdg_config) / "LEAPP"
        return home / ".config" / "LEAPP"


def get_settings_path():
    """
    Returns the path to the settings.json file.
    """
    return get_shared_directory() / "settings.json"


def get_history_path():
    """
    Returns the path to the history.json file.
    """
    return get_shared_directory() / "history.json"


def _atomic_write_json(path, data):
    """
    Writes data to a temporary file and then renames it to the destination path.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(".tmp")

    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())

        # On Windows, os.replace might fail if the destination exists and is open
        # but for our small JSON files it should generally be fine.
        os.replace(temp_path, path)
    except OSError as e:
        logger.error("Failed to write history/settings file at %s: %s", path, e)
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass


def _read_json(path, default=None):
    """
    Reads a JSON file and returns the data.
    """
    if default is None:
        default = {}
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except OSError as e:
        logger.error("Failed to read history/settings file at %s: %s", path, e)
        return default


def _has_history_entries(history_data):
    return any(
        history_data.get(key)
        for key in ("input_paths", "output_paths", "runs")
    )


def is_history_enabled():
    """
    Checks if history recording is enabled in settings.
    """
    settings = _read_json(get_settings_path())
    return settings.get("history_enabled", False)


def set_history_enabled(enabled):
    """
    Enables or disables history recording in settings.
    """
    settings = _read_json(get_settings_path())
    settings["schema_version"] = SCHEMA_VERSION
    settings["history_enabled"] = enabled
    if "path_history_limit" not in settings:
        settings["path_history_limit"] = 10
    if "run_history_limit" not in settings:
        settings["run_history_limit"] = 20
    _atomic_write_json(get_settings_path(), settings)


def _get_limit(key, default):
    """
    Returns a limit value from settings.
    """
    settings = _read_json(get_settings_path())
    return settings.get(key, default)


def get_input_paths():
    """
    Returns the list of recently used input paths.
    """
    if not is_history_enabled():
        return []
    history_data = _read_json(get_history_path())
    return history_data.get("input_paths", [])


def record_input_path(path):
    """
    Records a new input path in history.
    """
    if not is_history_enabled():
        return
    prefer_long_path = os.path.isdir(_strip_windows_extended_prefix(path))
    _record_path("input_paths", path, _get_limit("path_history_limit", 10), prefer_long_path)


def get_output_paths():
    """
    Returns the list of recently used output paths.
    """
    if not is_history_enabled():
        return []
    history_data = _read_json(get_history_path())
    return history_data.get("output_paths", [])


def record_output_path(path):
    """
    Records a new output path in history.
    """
    if not is_history_enabled():
        return
    _record_path("output_paths", path, _get_limit("path_history_limit", 10), prefer_long_path=True)


def _record_path(key, path, limit, prefer_long_path=False):
    """
    Internal helper to record a path in history.
    """
    if not path:
        return
    stored_path = _normalize_stored_path(path, prefer_long_path)
    path_key = _path_history_key(path)
    history_data = _read_json(get_history_path())
    history_data["schema_version"] = SCHEMA_VERSION
    paths = history_data.get(key, [])

    # Deduplicate by canonical path and move to top
    paths = [p for p in paths if _path_history_key(p) != path_key]
    paths.insert(0, stored_path)

    # Limit
    history_data[key] = paths[:limit]
    _atomic_write_json(get_history_path(), history_data)


def get_recent_runs():
    """
    Returns the list of recent tool runs.
    """
    if not is_history_enabled():
        return []
    history_data = _read_json(get_history_path())
    return history_data.get("runs", [])


def has_history():
    """
    Returns True if the shared history file has any stored entries.
    """
    history_data = _read_json(get_history_path())
    return _has_history_entries(history_data)


def has_single_leapp_history(leapp_id):
    """
    Returns True if shared paths or this LEAPP tool's runs exist.
    """
    history_data = _read_json(get_history_path())
    if history_data.get("input_paths") or history_data.get("output_paths"):
        return True

    leapp_id = leapp_id.lower()
    return any(
        run.get("leapp_id") == leapp_id
        for run in history_data.get("runs", [])
    )


def record_recent_run(leapp_id, leapp_version, lava_file_path):
    """
    Records a successful tool run in history.
    """
    if not is_history_enabled():
        return
    if not lava_file_path or not os.path.exists(lava_file_path):
        return

    lava_file_path = _normalize_stored_path(lava_file_path, prefer_long_path=True)
    path_key = _path_history_key(lava_file_path)
    history_data = _read_json(get_history_path())
    history_data["schema_version"] = SCHEMA_VERSION
    runs = history_data.get("runs", [])

    # Deduplicate by canonical lava file path
    runs = [r for r in runs if _path_history_key(r.get("lava_file_path", "")) != path_key]

    new_run = {
        "leapp_id": leapp_id.lower(),
        "leapp_version": leapp_version,
        "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        "lava_file_path": lava_file_path
    }
    runs.insert(0, new_run)

    # Limit
    limit = _get_limit("run_history_limit", 20)
    history_data["runs"] = runs[:limit]
    _atomic_write_json(get_history_path(), history_data)


def remove_recent_run(lava_file_path):
    """
    Removes a specific run from history.
    """
    if not is_history_enabled():
        return
    lava_file_path = _normalize_stored_path(lava_file_path, prefer_long_path=True)
    path_key = _path_history_key(lava_file_path)
    history_data = _read_json(get_history_path())
    runs = history_data.get("runs", [])
    new_runs = [r for r in runs if _path_history_key(r.get("lava_file_path", "")) != path_key]
    if len(runs) != len(new_runs):
        history_data["runs"] = new_runs
        _atomic_write_json(get_history_path(), history_data)


def clear_single_leapp_history(leapp_id):
    """
    Clears shared paths and this LEAPP tool's recent runs.
    """
    history_data = _read_json(get_history_path())
    history_data.pop("input_paths", None)
    history_data.pop("output_paths", None)

    leapp_id = leapp_id.lower()
    runs = history_data.get("runs", [])
    history_data["runs"] = [
        run for run in runs
        if run.get("leapp_id") != leapp_id
    ]

    if _has_history_entries(history_data):
        _atomic_write_json(get_history_path(), history_data)
    else:
        clear_history()


def clear_history():
    """
    Deletes the history file.
    """
    if os.path.exists(get_history_path()):
        try:
            os.remove(get_history_path())
        except OSError as e:
            logger.error("Failed to clear history: %s", e)
