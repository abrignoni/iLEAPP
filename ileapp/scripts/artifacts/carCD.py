__artifacts_v2__ = {
    "carCD": {
        "name": "Last Car Connection and UDID",
        "description": "",
        "author": "@AlexisBrignoni",
        "version": "0.0.2",
        "date": "2023-09-30",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/Library/Caches/locationd/cache.plist'),
        "output_types": "none",
    }
}


import plistlib
from ileapp.scripts.ilapfuncs import artifact_processor, webkit_timestampsconv, device_info

@artifact_processor
def carCD(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = str(files_found[0])
        
    with open(source_path, "rb") as fp:
        pl = plistlib.load(fp)
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
