__artifacts_v2__ = {
    "get_discordManifest": {  # This should match the function name exactly
        "name": "Discord - Manifest",
        "description": "Parses Discord manifest",
        "author": "",
        "creation_date": "",
        "last_updated": "2025-11-25",
        "requirements": "none",
        "category": "Discord",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/RCTAsyncLocalStorage_V1/manifest.json'),
        "output_types": "standard",  # or ["html", "tsv", "timeline", "lava"]
    }
}

import os
import json
from scripts.ilapfuncs import artifact_processor

@artifact_processor
def get_discordManifest(context):
    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)

        jsonfinal = None
        if os.path.isfile(file_found):
            with open(file_found, encoding='utf-8') as f_in:
                for jsondata in f_in:
                    jsonfinal = json.loads(jsondata)

        if jsonfinal:
            for key, value in jsonfinal.items():
                data_list.append((key, value, file_found))

    data_headers = ('Key Name', 'Data Value')   

    return data_headers, data_list, 'see Source File for more'