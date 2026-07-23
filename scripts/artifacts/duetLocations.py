__artifacts_v2__ = {
    "duetlocations": {
        "name": "Duet Locations",
        "description": "Location records from the DuetExpertCenter location stream (SEGB)",
        "author": "",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Geolocation",
        "notes": "",
        "paths": ('*/DuetExpertCenter/streams/location/local/*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 58 rows",
            "felix23_ios16": "iOS 16.5 | 21 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    }
}

import os
import struct
from io import BytesIO

import nska_deserialize as nd

from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv

_PLIST_ERRORS = (nd.DeserializeError, nd.biplist.NotBinaryPlistException,
                 nd.biplist.InvalidPlistException, nd.plistlib.InvalidFileException,
                 nd.ccl_bplist.BplistError, ValueError, TypeError, OSError, OverflowError)


@artifact_processor
def duetlocations(context):
    data_headers = (('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Horizontal Accuracy',
                    'Altitude', 'Speed')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.') or not os.path.isfile(file_found) or 'tombstone' in file_found:
            continue
        with open(file_found, 'rb') as f:
            data = f.read()
        try:
            headerloc = data.index(b'SEGB')
        except ValueError:
            continue

        ab = BytesIO(data)
        ab.seek(headerloc)
        ab.read(4)  # main header
        found_any = False
        while True:
            size_hex = ab.read(4)
            try:
                size = struct.unpack_from("<i", size_hex)[0]
            except struct.error:
                break
            if size == 0:
                break
            ab.read(4)   # allocation
            ab.read(8)   # date1 (SEGB time, not surfaced — record uses the plist timestamp)
            ab.read(8)   # date2
            ab.read(8)   # ignore
            datos = ab.read(size)

            if datos[:1] != b'\x00':
                try:
                    plist = nd.deserialize_plist_from_string(datos)
                except _PLIST_ERRORS:
                    plist = None
                if isinstance(plist, dict) and plist:
                    lat = plist.get('kCLLocationCodingKeyCoordinateLatitude', '')
                    lon = plist.get('kCLLocationCodingKeyCoordinateLongitude', '')
                    if lat != '' and lon != '':
                        ts = plist.get('kCLLocationCodingKeyTimestamp')
                        data_list.append((webkit_timestampsconv(ts) if ts is not None else '', lat, lon,
                                          plist.get('kCLLocationCodingKeyHorizontalAccuracy', ''),
                                          plist.get('kCLLocationCodingKeyAltitude', ''),
                                          plist.get('kCLLocationCodingKeySpeed', '')))
                        found_any = True

            mod = size % 8
            if mod != 0:
                ab.read(8 - mod)

        if found_any:
            sources.append(context.get_relative_path(file_found))

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
