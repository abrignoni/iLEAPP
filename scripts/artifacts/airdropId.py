__artifacts_v2__ = {
    "airdropId": {
        "name": "Airdrop ID",
        "description": "Extract Airdrop ID",
        "author": "@AlexisBrignoni",
        "creation_date": "2023-10-03",
        "last_update_date": "2025-10-08",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/mobile/Library/Preferences/com.apple.sharingd.plist'),
        "output_types": "none",
        "artifact_icon": "settings",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | files found",
            "dexter_ios18": "iOS 18.3.2 | files found",
            "felix_ios17": "iOS 17.6.1 | files found",
            "fsfull002_ios17": "iOS 17.1 | files found",
            "hc_ios18_7": "iOS 18.7.8 | files found",
            "iphone11_ios17": "iOS 17.3 | files found",
            "iphone12_ios18": "iOS 18.7 | files found",
            "iphone14plus_ios18": "iOS 18.0 | files found",
            "otto_ios17": "iOS 17.5.1 | files found",
            "abe_ios16": "iOS 16.5 | files found",
            "felix23_ios16": "iOS 16.5 | files found",
            "hickman_ios13": "iOS 13.3.1 | files found",
            "hickman_ios14": "iOS 14.3 | files found",
            "jess_ios15": "iOS 15.0.2 | files found",
            "magnet_ios16": "iOS 16.1.1 | files found",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content, device_info

@artifact_processor
def airdropId(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "com.apple.sharingd.plist")

    pl = get_plist_file_content(source_path)
    for key, val in pl.items():
        if key == 'AirDropID':
            device_info("AirDrop", "AirDrop ID", val, source_path)
                        
        elif key == 'DiscoverableMode':
            device_info("AirDrop", "Discoverable Mode", val, source_path)
            
    # Return empty data since this artifact only collects device info
    return (), [], source_path
