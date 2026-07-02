__artifacts_v2__ = {
    "get_rctAsyncStorageManifest": {
        "name": "React Native Async Storage Manifest",
        "description": "Parses React Native AsyncStorage manifest files",
        "author": "@Gear-I",
        "creation_date": "",
        "last_updated": "2026-06-19",
        "requirements": "none",
        "category": "React Native",
        "notes": "Manifest files may belong to any React Native app. Use Source File to identify the app container.",
        "paths": (
            "*/mobile/Containers/Data/Application/*/Documents/RCTAsyncLocalStorage_V1/manifest.json",
            "*/mobile/Containers/Data/Application/*/Library/Application Support/RCTAsyncLocalStorage_V1/manifest.json",
        ),
        "output_types": "standard",
        "artifact_icon": "database",
    }
}

import json
import os

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_rctAsyncStorageManifest(context):
    data_list = []

    for file_found in context.get_files_found():
        file_found = str(file_found)

        if not os.path.isfile(file_found):
            continue

        try:
            with open(file_found, "r", encoding="utf-8") as f_in:
                json_data = json.load(f_in)
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            continue

        if not isinstance(json_data, dict):
            continue

        for key, value in json_data.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)

            data_list.append((
                key,
                value,
                context.get_relative_path(file_found),
            ))

    data_headers = (
        "Key Name",
        "Data Value",
        "Source File",
    )

    return data_headers, data_list, "see Source File for more"