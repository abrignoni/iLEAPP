__artifacts_v2__ = {
    "get_cacheRoutesGmap": {
        "name": "Google Maps Cache Routes",
        "description": "",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-08-03",
        "last_update_date": "2025-11-12",
        "requirements": "none",
        "category": "Locations",
        "notes": "",
        "paths": ('*/Library/Application Support/CachedRoutes/*.plist',),
        "output_types": "standard",
    }
}

import os
from datetime import datetime, timezone
from scripts.ilapfuncs import artifact_processor, get_plist_file_content

@artifact_processor
def get_cacheRoutesGmap(context):
    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        noext = os.path.splitext(os.path.basename(file_found))[0]
        try:
            epoch_ms = int(noext)
        except ValueError:
            continue  # filename is not a numeric (ms epoch) timestamp
        datetime_time = datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc)

        deserialized = get_plist_file_content(file_found)
        if not isinstance(deserialized, dict):
            continue
        objects = deserialized.get('$objects')
        if not isinstance(objects, list):
            continue  # not an NSKeyedArchiver archive
        for entry in objects:
            try:
                lat = entry['_coordinateLat']
                lon = entry['_coordinateLong']  # lat/longs
                data_list.append((datetime_time, lat, lon, context.get_relative_path(file_found)))
            except (KeyError, TypeError):
                pass

    data_headers = (('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Source File')

    return data_headers, data_list, 'see Source File for more info'