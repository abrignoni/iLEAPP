__artifacts_v2__ = {
    "get_adId": {
        "name": "Advertising Identifier",
        "description": "Extracts Apple Advertising Identifier from the device",
        "author": "@AlexisBrignoni",
        "version": "0.2",
        "date": "2024-05-09",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/containers/Shared/SystemGroup/*/Library/Caches/com.apple.lsdidentifiers.plist',),
        "output_types": ["html", "tsv", "lava"]
    }
}

import plistlib
from scripts.ilapfuncs import artifact_processor, logfunc, logdevinfo 

@artifact_processor
def get_adId(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    data_headers = ()
    source_path = str(files_found[0])

    if not source_path:
        logfunc('com.apple.lsdidentifiers.plist not found')
        return data_headers, data_list, source_path

    with open(source_path, "rb") as fp:
        pl = plistlib.load(fp)
        if len(pl) > 0:
            for key, val in pl.items():
                if key == 'LSAdvertiserIdentifier':
                    data_list.append(('Apple Advertising Identifier', val))
                    logdevinfo(f"<b>Apple Advertising Identifier: </b>{val}")
        else:
            logfunc("No Apple advertising identifier found")

    data_headers = ('Key', 'Data')
    return data_headers, data_list, source_path
