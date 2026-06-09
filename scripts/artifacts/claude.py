__artifacts_v2__ = {
    "get_claude": {
        "name": "Claude",
        "description": "Parses Claude iOS app artifacts",
        "author": "Dielle De Noon",
        "creation_date": "2026-06-08",
        "last_updated": "2026-06-08",
        "requirements": "none",
        "category": "Claude",
        "notes": "",
        "paths": (
            "*/mobile/Containers/Data/Application/*/Documents/*",
            "*/mobile/Containers/Shared/AppGroup/*/*claude*",
            "*/mobile/Containers/Shared/AppGroup/*/*anthropic*",
        ),
        "output_types": "standard",
    }
}

import os
import json
import plistlib
from scripts.ilapfuncs import artifact_processor

@artifact_processor
def get_claude(context):
    data_list = []

    for file_found in context.get_files_found():
        file_found = str(file_found)

        if not os.path.isfile(file_found):
            continue

        lower = file_found.lower()
        if "claude" not in lower and "anthropic" not in lower:
            continue

        data_list.append((os.path.basename(file_found), file_found))

    data_headers = ("File Name", "Source File")
    return data_headers, data_list, "Claude iOS app related files"

