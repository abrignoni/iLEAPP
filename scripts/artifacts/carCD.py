__artifacts_v2__ = {
    "carCD": {
        "name": "Last Car Connection and UDID",
        "description": "Parses the last connected CarPlay vehicle and the device UDID from the locationd cache.plist.",
        "author": "@AlexisBrignoni",
        "creation_date": "2023-09-30",
        "last_update_date": "2025-11-12",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/Library/Caches/locationd/cache.plist'),
        "output_types": "none",
        "artifact_icon": "car",
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
        },
    }
}

from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv, device_info, get_plist_file_content

@artifact_processor
def carCD(context):
    files_found = context.get_files_found()
    source_path = str(files_found[0])
        
    pl = get_plist_file_content(source_path)
    for key, value in pl.items():
        if key == 'LastVehicleConnection':
            lastconn = value
            contype = lastconn[2]
            device_info("Vehicle", "Type", contype, source_path)
            connected = webkit_timestampsconv(lastconn[0])
            device_info("Vehicle", "Last Connected", connected, source_path)
            disconnected = webkit_timestampsconv(lastconn[1])
            device_info("Vehicle", "Last Disconnected", disconnected, source_path)
        elif key == 'LastVehicleConnectionV2':
            lastconnv2 = value
            contype = lastconnv2[2]
            device_info("Vehicle", "Type", contype, source_path)
            connected = webkit_timestampsconv(lastconnv2[0])
            device_info("Vehicle", "Last Connected", connected, source_path)
            disconnected = webkit_timestampsconv(lastconnv2[1])
            device_info("Vehicle", "Last Disconnected", disconnected, source_path)
        elif key == 'CalibrationUDID':
            uid = value
            device_info("Vehicle", "CalibrationUDID", uid, source_path)
        else:
            pass

    # Return empty data since this artifact only collects device info
    return (), [], source_path
