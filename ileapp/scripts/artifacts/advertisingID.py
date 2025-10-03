__artifacts_v2__ = {
    "advertisingID": {
        "name": "Advertising Identifier",
        "description": "Extract Apple advertising identifier",
        "author": "@AlexisBrignoni",
        "creation_date": "2023-10-03",
        "last_update_date": "2024-12-17",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/containers/Shared/SystemGroup/*/Library/Caches/com.apple.lsdidentifiers.plist',),
        "output_types": "none",
        "artifact_icon": "settings"
    }
}

from ileapp.scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content, device_info

@artifact_processor
def advertisingID(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "com.apple.lsdidentifiers.plist")

    pl = get_plist_file_content(source_path)
    for key, val in pl.items():
        if key == 'LSAdvertiserIdentifier':
            device_info("Advertising Identifier", "Apple Advertising Identifier", val, source_path)
            break

    
    # Return empty data since this artifact only collects device info
    return (), [], source_path
