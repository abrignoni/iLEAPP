"""
Multiprocessing helpers for iLEAPP.

This module is designed to be importable in a spawned subprocess.
It provides a per-plugin runner that rehydrates minimal Context state and
returns small, picklable deltas back to the parent process (icons + LAVA metadata).
"""

from __future__ import annotations

import os
import traceback
import typing
import warnings
from collections import OrderedDict

import scripts.plugin_loader as plugin_loader
from scripts.context import Context
from scripts.ilapfuncs import (
    FileInfoSnapshot,
    SeekerProxy,
    check_output_types,
    iOS,
    output_params_from_existing_output_folder_base,
    logfunc,
)
import scripts.lavafuncs as lavafuncs


def _build_file_infos_snapshot(file_infos_subset: dict[str, tuple[str, float, float]]) -> dict[str, FileInfoSnapshot]:
    """
    Convert a picklable subset dict from parent into FileInfoSnapshot objects.

    Input format: { extracted_path: (source_path, ctime, mtime) }.
    """
    snapshot: dict[str, FileInfoSnapshot] = {}
    for extracted_path, info_tuple in (file_infos_subset or {}).items():
        try:
            source_path, ctime, mtime = info_tuple
            snapshot[extracted_path] = FileInfoSnapshot(
                source_path=str(source_path),
                creation_date=float(ctime),
                modification_date=float(mtime),
            )
        except Exception:
            # Best-effort: ignore malformed entries
            continue
    return snapshot


def _init_lava_metadata_only(input_path: str, output_path: str, input_type: str) -> None:
    """
    Initialize lavafuncs.lava_data without creating/initializing tables.

    The parent process should have already created the DB file & base schema.
    """
    lavafuncs.lava_data = {
        "param_input": input_path,
        "param_output": output_path,
        "param_type": input_type,
        "processing_status": "In Progress",
        "lava_db_name": lavafuncs.lava_db_name,
        "modules": [],
        "artifacts": OrderedDict(),
        "meta": {"modules": []},
    }


def run_one_plugin(payload: dict, result_queue) -> None:
    """
    Run a single plugin in a subprocess.

    Expected payload keys:
    - plugin_key: str
    - files_found: list[str]
    - category_folder: str
    - wrap_text: bool
    - time_offset: str
    - output_folder_base: str
    - input_path: str
    - extracttype: str
    - file_infos_subset: dict[str, tuple[str, float, float]]
    - installed_os_version: str (optional)
    - seeker_all_files: list[str] (optional)
    """
    # Suppress common deprecation warnings that appear in every subprocess
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources")
    warnings.filterwarnings("ignore", message=".*pkg_resources is deprecated.*")
    
    try:
        plugin_key: str = payload["plugin_key"]
        files_found: list[str] = payload.get("files_found") or []
        category_folder: str = payload["category_folder"]
        wrap_text: bool = bool(payload.get("wrap_text", True))
        time_offset: str = payload.get("time_offset") or "UTC"
        output_folder_base: str = payload["output_folder_base"]
        input_path: str = payload.get("input_path") or ""
        extracttype: str = payload.get("extracttype") or ""
        file_infos_subset: dict[str, tuple[str, float, float]] = payload.get("file_infos_subset") or {}
        installed_os_version: str = payload.get("installed_os_version") or ""
        seeker_all_files: list[str] = payload.get("seeker_all_files") or []

        # Rehydrate output params + log paths for logfunc()
        out_params_existing = output_params_from_existing_output_folder_base(
            output_folder_base, ensure_dirs=True
        )
        Context.set_output_params(out_params_existing)

        # Propagate installed iOS version into the subprocess (many plugins depend on it)
        if installed_os_version:
            try:
                iOS.set_version(installed_os_version)
                Context.set_installed_os_version(installed_os_version)
            except Exception:
                pass

        # Minimal seeker proxy (media helpers depend on seeker.file_infos)
        seeker_proxy = SeekerProxy(_build_file_infos_snapshot(file_infos_subset), seeker_all_files)

        # Load plugin inside child to avoid pickling callables
        loader = plugin_loader.PluginLoader()
        plugin_spec = loader[plugin_key]

        artifact_info = plugin_spec.artifact_info or {}
        output_types = artifact_info.get("output_types", ["html", "tsv", "timeline", "lava", "kml"])

        # Setup LAVA connection only if needed by this plugin
        wants_lava = check_output_types("lava", output_types) or check_output_types("lava_only", output_types)
        if wants_lava:
            _init_lava_metadata_only(input_path, output_folder_base, extracttype)
            lavafuncs.lava_open_existing(output_folder_base)

        # Execute plugin
        try:
            data_headers, data_list, source_path = plugin_spec.method(
                files_found, category_folder, seeker_proxy, wrap_text, time_offset
            )
        except TypeError as ex:
            logfunc(f"TypeError: {ex}")
            logfunc(f"Traceback: {traceback.format_exc()}")
            raise ex
        except Exception as ex:
            logfunc(f"Exception: {ex}")
            logfunc(f"Traceback: {traceback.format_exc()}")
            raise ex

        # Capture installed OS version if this plugin discovered it
        discovered_os_version = ""
        try:
            discovered_os_version = Context.get_installed_os_version() or ""
        except Exception:
            discovered_os_version = ""

        # Build deltas to send back
        category = artifact_info.get("category", "")
        artifact_name = artifact_info.get("name", plugin_key)
        artifact_icon = artifact_info.get("artifact_icon", "")

        icons_delta: dict[str, dict[str, str]] = {}
        if data_list and category:
            icons_delta = {category: {artifact_name: artifact_icon}}

        lava_meta_delta: dict | None = None
        lava_only_delta: list[dict] = []

        if wants_lava and data_headers and data_list:
            # Derive table name + maps consistently with lava_create_sqlite_table()
            func_name = plugin_spec.name
            table_name, column_map, object_columns = lavafuncs.lava_create_sqlite_table(func_name, data_headers)

            module_filename = ""
            try:
                module_filename = os.path.basename(Context.get_module_file_path())
            except Exception:
                module_filename = f"{plugin_spec.module_name}.py"

            lava_meta_delta = lavafuncs.lava_build_artifact_meta_delta(
                category=category,
                module_name=plugin_spec.module_name,
                module_filename=module_filename,
                artifact_name=artifact_name,
                artifact_info=artifact_info,
                table_name=table_name,
                column_map=column_map,
                object_columns=object_columns,
                record_count=len(data_list) if data_list else 0,
                artifact_icon=artifact_icon,
                source_path=source_path,
                data_headers=data_headers,
                data_views=artifact_info.get("data_views"),
            )

            # If lava_only, record for the parent's lava-only log
            if check_output_types("lava_only", output_types):
                lava_only_delta.append({
                    "category": category,
                    "artifact_name": artifact_name,
                    "table_name": table_name,
                    "records": len(data_list) if data_list else 0,
                })

        result_queue.put({
            "ok": True,
            "plugin_key": plugin_key,
            "record_count": len(data_list) if data_list else 0,
            "icons_delta": icons_delta,
            "lava_meta_delta": lava_meta_delta,
            "lava_only_delta": lava_only_delta,
            "installed_os_version": discovered_os_version,
        })

    except Exception as ex:
        result_queue.put({
            "ok": False,
            "plugin_key": payload.get("plugin_key"),
            "error": str(ex),
            "traceback": traceback.format_exc(),
        })
    finally:
        # Ensure DB connection is closed in the child
        try:
            lavafuncs.lava_close_db()
        except Exception:
            pass


