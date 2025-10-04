__artifacts_v2__ = {
    "airdropId": {
        "name": "Airdrop ID",
        "description": "Extract Airdrop ID",
        "author": "@AlexisBrignoni",
        "creation_date": "2023-10-03",
        "last_update_date": "2025-01-28",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/mobile/Library/Preferences/com.apple.sharingd.plist'),
        "output_types": "none",
        "artifact_icon": "settings"
    }
}

from ileapp.scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content, device_info

@artifact_processor
def airdropId(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "com.apple.sharingd.plist")

    pl = get_plist_file_content(source_path)
    for key, val in pl.items():
        if key == 'AirDropID':
            device_info("AirDrop", "AirDrop ID", val, source_path)
                        
        elif key == 'DiscoverableMode':
            device_info("AirDrop", "Discoverable Mode", val, source_path)
            
    # Return empty data since this artifact only collects device info
    return (), [], source_path
