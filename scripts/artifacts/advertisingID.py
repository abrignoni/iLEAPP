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
        "output_types": "none",
        "artifact_icon": "settings"
    }
}

from scripts.ilapfuncs import artifact_processor, get_plist_content, device_info

@artifact_processor
def advertisingID(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = str(files_found[0])

    pl = get_plist_content(source_path)
    for key, val in pl.items():
        if key == 'LSAdvertiserIdentifier':
            device_info("Advertising Identifier", "Apple Advertising Identifier", val, source_path)
            break

    
    # Return empty data since this artifact only collects device info
    return (), [], source_path
