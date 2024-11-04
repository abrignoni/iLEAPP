__artifacts_v2__ = {
    "get_airdropId": {
        "name": "Airdrop ID",
        "description": "Extract Airdrop ID",
        "author": "@AlexisBrignoni",
        "version": "0.2.1",
        "date": "2023-10-03",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/mobile/Library/Preferences/com.apple.sharingd.plist'),
        "output_types": "lava"
    }
}

import plistlib
from scripts.ilapfuncs import artifact_processor, device_info

@artifact_processor
def get_airdropId(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    id_values = []
    data_headers = ()
    source_path = str(files_found[0])

    with open(source_path, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            if key == 'LSAdvertiserIdentifier':
                data_list.append('Airdrop ID', val)
                device_info("Airdrop", "Airdrop ID", val)

    data_headers = ('Identifer', 'Data Value')
    
    return data_headers, data_list, source_path
