__artifacts_v2__ = {
    "tileApp": {
        "name": "Tile App Geolocation Logs",
        "description": "Latitude/longitude coordinates recorded in Tile app logs",
        "author": "",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Locations",
        "notes": "Log timestamps stored as UTC.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/log/com.thetileapp.tile*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Tile - Find lost keys & phone 2.115.0 | 0 rows",
        }
    }
}

import gzip
import os
import re

from scripts.ilapfuncs import artifact_processor, convert_ts_human_to_utc

_REGEX_DATE = r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}.\d{3}"
_REGEX_LATLONG = (r"<[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*"
                  r"[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)>")


@artifact_processor
def tileApp(context):
    data_headers = (('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Row Number', 'Source File')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('gz'):
            opener = gzip.open
        elif file_found.endswith('log'):
            opener = open
        else:
            continue

        counter = 0
        had_data = False
        with opener(file_found, 'rt') as f:
            for line in f:
                counter += 1
                datestamp = re.search(_REGEX_DATE, line)
                if datestamp is None:
                    continue
                latlong = re.search(_REGEX_LATLONG, line)
                if latlong is None:
                    continue
                lat, longi = latlong.group(0).strip('<').strip('>').split(',')
                data_list.append((convert_ts_human_to_utc(datestamp.group(0)),
                                  lat.lstrip(), longi.lstrip(), counter, os.path.basename(file_found)))
                had_data = True
        if had_data:
            sources.append(context.get_relative_path(file_found))

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
