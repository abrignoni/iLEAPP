__artifacts_v2__ = {
    "user_defaults": {
        "name": "Application User Defaults",
        "description": "Extracts the user defaults plist file for each application",
        "author": "@jfhyla",
        "creation_date": "2024-12-16",
        "last_update_date": "2026-06-08",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "https://developer.apple.com/documentation/foundation/userdefaults",
        "paths": (
            "*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist",
            "*/Containers/Data/Application/*/Library/Preferences/*.plist",
        ),
        "output_types": "standard",
        "artifact_icon": "sliders",
    }
}

import datetime
import pathlib

from scripts.ilapfuncs import artifact_processor, get_plist_file_content


def clean_data(obj):
    """Convert plist-only value types into report-friendly values."""
    if isinstance(obj, dict):
        return {key: clean_data(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [clean_data(item) for item in obj]
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, bytes):
        return str(obj)
    return obj


@artifact_processor
def user_defaults(context):
    files_found = context.get_files_found()
    applications = {}
    data_list = []

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith("mobile_container_manager.metadata.plist"):
            continue

        plist = get_plist_file_content(file_found)
        if not isinstance(plist, dict):
            continue

        bundle_id = plist.get("MCMMetadataIdentifier")
        if bundle_id:
            container_id = pathlib.Path(file_found).parent.name
            applications[container_id] = bundle_id

    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith("mobile_container_manager.metadata.plist"):
            continue

        for container_id, bundle_id in applications.items():
            if container_id not in file_found or f"{bundle_id}.plist" not in file_found:
                continue

            plist = get_plist_file_content(file_found)
            if not isinstance(plist, dict):
                continue

            source_file = context.get_relative_path(file_found)
            for key, item in plist.items():
                data_list.append((
                    bundle_id,
                    container_id,
                    key,
                    str(clean_data(item)),
                    source_file,
                ))

    data_headers = (
        "Application Bundle ID",
        "Application Container ID",
        "Key Name",
        "Item",
        "Source File",
    )

    return data_headers, data_list, "Source files listed in report"
