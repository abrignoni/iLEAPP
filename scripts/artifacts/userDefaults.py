__artifacts_v2__ = {
    "user_defaults": {
        "name": "Application User Defaults",
        "description": "Extracts the user defaults Plist file for each application",
        "author": "@jfhyla",
        "creation_date": "2024-12-16",
        "last_update_date": "2025-11-28",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "https://developer.apple.com/documentation/foundation/userdefaults",
        "paths": ('*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
                  '*/mobile/Containers/Data/Application/*/Preferences/*.plist'),
        "output_types": "standard",
        "artifact_icon": "sliders"
    }
}

import pathlib
import datetime
from scripts.ilapfuncs import (
    artifact_processor,
    get_plist_file_content,
)


def clean_data(obj):
    """Helper to clean nested plist data for display"""
    if isinstance(obj, dict):
        return {key: clean_data(val) for key, val in obj.items()}
    elif isinstance(obj, list):
        return [clean_data(item) for item in obj]
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, bytes):
        return str(obj)
    else:
        return obj


@artifact_processor
def user_defaults(context):
    files_found = context.get_files_found()
    data_list = []
    apps = {}

    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('mobile_container_manager.metadata.plist'):
            plist = get_plist_file_content(file_found)

            if plist and 'MCMMetadataIdentifier' in plist:
                bundleid = plist['MCMMetadataIdentifier']
                appgroupid = pathlib.Path(file_found).parent.name
                apps[appgroupid] = bundleid

    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('mobile_container_manager.metadata.plist'):
            continue

        for guid, bundleid in apps.items():
            if guid in file_found and f'{bundleid}.plist' in file_found:
                plist = get_plist_file_content(file_found)

                if plist:
                    for key, item in plist.items():
                        cleaned_item = clean_data(item)
                        data_list.append((
                            bundleid,
                            guid,
                            key,
                            str(cleaned_item),
                            file_found
                            ))

    data_headers = (
        'Application BundleID',
        'Application GUID',
        'Key',
        'Item',
        'Path'
        )

    return data_headers, data_list, ''
