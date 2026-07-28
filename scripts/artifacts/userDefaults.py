__artifacts_v2__ = {
    "user_defaults": {
        "name": "Application User Defaults",
        "description": "Extracts the user defaults plist file for each application",
        "author": "@jfhyla",
        "creation_date": "2024-12-16",
        "last_update_date": "2026-07-21",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "https://developer.apple.com/documentation/foundation/userdefaults",
        "paths": (
            "*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist",
            "*/Containers/Data/Application/*/Library/Preferences/*.plist",
        ),
        "output_types": ["html","lava","tsv"],
        "artifact_icon": "adjustments-alt",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 4280 rows",
            "dexter_ios18": "iOS 18.3.2 | 2572 rows",
            "felix_ios17": "iOS 17.6.1 | 1322 rows",
            "fsfull002_ios17": "iOS 17.1 | 1561 rows",
            "hc_ios18_7": "iOS 18.7.8 | 2582 rows",
            "iphone11_ios17": "iOS 17.3 | 3322 rows",
            "iphone12_ios18": "iOS 18.7 | 1740 rows",
            "iphone14plus_ios18": "iOS 18.0 | 831 rows",
            "otto_ios17": "iOS 17.5.1 | 2927 rows",
            "abe_ios16": "iOS 16.5 | 2829 rows",
            "felix23_ios16": "iOS 16.5 | 866 rows",
            "hickman_ios13": "iOS 13.3.1 | 2836 rows",
            "hickman_ios14": "iOS 14.3 | 2471 rows",
            "jess_ios15": "iOS 15.0.2 | 693 rows",
            "magnet_ios16": "iOS 16.1.1 | 1003 rows",
        },
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
