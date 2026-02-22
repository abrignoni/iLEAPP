import gzip
import re
import os

from scripts.ilapfuncs import artifact_processor, convert_ts_human_to_utc, convert_utc_human_to_timezone


@artifact_processor
def get_tileApp(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    file_found = ''
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('gz'):
            x = gzip.open
        elif file_found.endswith('log'):
            x = open
        else:
            continue

        with x(file_found, 'rt') as f:
            for counter, line in enumerate(f, 1):
                regexdate = r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}.\d{3}"
                datestamp = re.search(regexdate, line)
                if datestamp is not None:
                    datestamp = datestamp.group(0)
                    datestamp = convert_ts_human_to_utc(datestamp)
                    datestamp = convert_utc_human_to_timezone(datestamp, timezone_offset)
                    regexlatlong = r"<[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)>"
                    latlong = re.search(regexlatlong, line)
                    if latlong is not None:
                        latlong = latlong.group(0)
                        latlong = latlong.strip('<')
                        latlong = latlong.strip('>')
                        lat, longi = latlong.split(',')
                        head_tail = os.path.split(file_found)
                        source_path = head_tail[0]
                        data_list.append((datestamp, lat.lstrip(), longi.lstrip(), counter, head_tail[1]))

    data_headers = ('Timestamp', 'Latitude', 'Longitude', 'Row Number', 'Source File')
    return data_headers, data_list, source_path

__artifacts_v2__ = {
    "get_tileApp": {
        "name": "Tile App Geolocation",
        "description": "Tile app log recorded latitude and longitude coordinates.",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Locations",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/log/com.thetileapp.tile*',),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
