__artifacts_v2__ = {
    "get_airdropId": {
        "name": "Airdrop ID",
        "description": "Extracts Airdrop ID from the device",
        "author": "@AlexisBrignoni",
        "version": "0.2",
        "date": "2024-05-09",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/mobile/Library/Preferences/com.apple.sharingd.plist'),
        "output_types": "all"
    }
}

import plistlib
from scripts.ilapfuncs import artifact_processor, logfunc, logdevinfo

@artifact_processor
def get_airdropId(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    source_path = str(files_found[0])

    with open(source_path, "rb") as fp:
        pl = plistlib.load(fp)
        if len(pl) > 0:
            for key, val in pl.items():
                if key == 'LSAdvertiserIdentifier':
                    data_list.append('Airdrop ID', val)
                    logdevinfo(f"<b>Airdrop ID: </b>{val}")
        else:
            logfunc("No Airdrop ID available")

    data_headers = ('Key', 'Data')
    return data_headers, data_list, source_path
