__artifacts_v2__ = {
    "advertisingID": {
        "name": "Advertising Identifier",
        "description": "Extract Apple advertising identifier",
        "author": "@AlexisBrignoni",
        "version": "0.2.1",
        "date": "2023-10-03",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/containers/Shared/SystemGroup/*/Library/Caches/com.apple.lsdidentifiers.plist',),
        "output_types": "lava"
    }
}

import plistlib
from scripts.ilapfuncs import artifact_processor, device_info

@artifact_processor
def advertisingID(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    data_headers = ()
    source_path = str(files_found[0])

    with open(source_path, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            if key == 'LSAdvertiserIdentifier':
                data_list.append(('Apple Advertising Identifier', val))
                device_info("Advertising Identifier", "Apple Advertising Identifier", val, source_path)

    
    data_headers = ('Identifier', 'Data Value')
    return data_headers, data_list, source_path
