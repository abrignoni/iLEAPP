__artifacts_v2__ = {
    "get_cacheRoutesGmap": {
        "name": "Google Maps Cache Routes",
        "description": "Parses coordinates and a file name time from NSKeyedArchiver plists in an app's Library/Application Support/CachedRoutes folder. On the tested extractions the folder belonged to Google Maps.",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-08-03",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Locations",
        "notes": "One row per object in the archive that carries a _coordinateLat and "
                 "_coordinateLong pair. The time on every row of a file is the file name read as "
                 "Unix milliseconds, which is an interpretation based on the values seen on the "
                 "tested extractions; what event that time marks is not established. A file whose "
                 "name is not a whole number is skipped. The coordinates are points stored in a "
                 "cached route. They are not shown to be positions of the device, and the file does "
                 "not establish that the route was travelled. App attribution rests on the tested "
                 "extractions.",
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
    source_dirs = set()
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
        source_dirs.add(os.path.dirname(file_found))
        for entry in objects:
            try:
                lat = entry['_coordinateLat']
                lon = entry['_coordinateLong']  # lat/longs
                data_list.append((datetime_time, lat, lon, context.get_relative_path(file_found)))
            except (KeyError, TypeError):
                pass

    data_headers = (('Timestamp (from filename)', 'datetime'), 'Latitude', 'Longitude', 'Source File')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))