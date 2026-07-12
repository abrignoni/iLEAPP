__artifacts_v2__ = {
    "get_cacheRoutesGmap": {
        "name": "Google Maps Cache Routes",
        "description": "Parses cached Google Maps route data and timestamps from the app CachedRoutes plists.",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-08-03",
        "last_update_date": "2025-11-12",
        "requirements": "none",
        "category": "Locations",
        "notes": "",
        "paths": ('*/Library/Application Support/CachedRoutes/*.plist',),
        "output_types": "all",
        "artifact_icon": "route",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | Google Maps 26.24.1 | 77 rows",
            "iphone11_ios17": "iOS 17.3 | Google Maps 6.125.1 | 35 rows",
            "otto_ios17": "iOS 17.5.1 | Google Maps 6.127.2 | 433 rows",
            "abe_ios16": "iOS 16.5 | Google Maps 6.51.0 | 249 rows",
        },
    }
}

import os
import plistlib
from datetime import datetime, timezone
from scripts.ilapfuncs import artifact_processor

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

        # Read the raw archive and walk $objects ourselves. Do NOT route this
        # through get_plist_file_content / nska_deserialize: these CachedRoutes
        # archives contain unhashable NSDictionary keys, which makes the
        # deserializer emit noisy "unhashable" warnings, and it strips the
        # $objects array this artifact actually needs.
        try:
            with open(file_found, 'rb') as f:
                deserialized = plistlib.load(f)
        except (plistlib.InvalidFileException, ValueError, OSError):
            continue
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