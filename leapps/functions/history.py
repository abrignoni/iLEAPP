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
    _record_path("input_paths", path, _get_limit("path_history_limit", 10))


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
    _record_path("output_paths", path, _get_limit("path_history_limit", 10))


def _record_path(key, path, limit):
    """
    Internal helper to record a path in history.
    """
    if not path:
        return
    path = os.path.abspath(path)
    history_data = _read_json(get_history_path())
    history_data["schema_version"] = SCHEMA_VERSION
    paths = history_data.get(key, [])

    # Deduplicate and move to top
    if path in paths:
        paths.remove(path)
    paths.insert(0, path)

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


def record_recent_run(leapp_id, leapp_version, lava_file_path):
    """
    Records a successful tool run in history.
    """
    if not is_history_enabled():
        return
    if not lava_file_path or not os.path.exists(lava_file_path):
        return

    lava_file_path = os.path.abspath(lava_file_path)
    history_data = _read_json(get_history_path())
    history_data["schema_version"] = SCHEMA_VERSION
    runs = history_data.get("runs", [])

    # Deduplicate by lava_file_path
    runs = [r for r in runs if r.get("lava_file_path") != lava_file_path]

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
    lava_file_path = os.path.abspath(lava_file_path)
    history_data = _read_json(get_history_path())
    runs = history_data.get("runs", [])
    new_runs = [r for r in runs if r.get("lava_file_path") != lava_file_path]
    if len(runs) != len(new_runs):
        history_data["runs"] = new_runs
        _atomic_write_json(get_history_path(), history_data)


def clear_history():
    """
    Deletes the history file.
    """
    if os.path.exists(get_history_path()):
        try:
            os.remove(get_history_path())
        except OSError as e:
            logger.error("Failed to clear history: %s", e)
