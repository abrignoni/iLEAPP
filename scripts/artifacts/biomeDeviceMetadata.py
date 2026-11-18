__artifacts_v2__ = {
    "get_biomeDeviceMetadata": {
        "name": "Biome - Device Metadata",
        "description": "Parses OS build records from the Device.Metadata biome stream. The 46 written records on the tested images each carried an OS build string.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Builds with prefixes 19 through 23 were on the tested images (e.g. 20B110, "
                 "21D50, 22H31). The Supplemental Build and Platform field names and the Platform "
                 "value names are those of the BMDeviceMetadata class, read from BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of "
                 "the class was read. Supplemental Build was reported before as OS Build (Field 4) "
                 "and Platform as Type (raw). "
                 "Platform names depend on the integer shown in Data Version. The SEGB reader returns "
                 "it unnamed with each entry: it is the second integer of the entry header in SEGB "
                 "version 2 files and the last field of the record header in SEGB version 1 files. "
                 "It is read here as the Biome data version. BMDeviceMetadata reads "
                 "data version 0 with 0 = iPad, 1 = iPhone, 2 = MacDesktop, 3 = MacPortable, 4 = TV, "
                 "5 = Watch, 6 = HomePod, 8 = Vision, and data version 1 with 0 = Unknown, "
                 "1 = iPad, 2 = iPhone, 3 = MacDesktop, 4 = MacPortable, 5 = TV, 6 = Watch, "
                 "7 = HomePod, 8 = Vision, 9 = HomeAccessory. A value or version outside those "
                 "lists keeps its integer in Platform (raw) with the name blank. On the 46 written records on the tested images, the 18 data version 0 records hold 1 and the 28 data version 1 records hold 2, so all 46 read iPhone. Supplemental Build was the same as OS Build on 41 of the 46, different on 3 and empty on 2."
                 " "
                 "On 5 tested images (jess_ios15 on iOS 15; abe_ios16, felix23_ios16, hexordia_ios1651 and magnet_ios16 on iOS 16) the stream is stored under DeviceMetadata, which BiomeLibrary.framework on macOS 27.2.1 (26B131) lists as its legacy name, and is read too. Its 10 written records are data version 0. Fields 2 and 3 were on all 10 and field 4 on 9; the iOS 15 record held no field 4. Its remote folders are not read."),
        "paths": ('*/streams/*/Device.Metadata/local/*', '*/streams/*/DeviceMetadata/local/*'),
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 5 rows",
            "hc_ios18_7": "iOS 18.7.8 | 3 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
        },
    }
}


import os
import struct
from datetime import timezone

from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)

# Pin flat fields so build strings are never eagerly decoded as nested protobuf.
TYPESS = {
    '2': {'type': 'str', 'name': ''},
    '3': {'type': 'int', 'name': ''},
    '4': {'type': 'str', 'name': ''},
}

# platform names by record data version (the unnamed int the SEGB reader returns per entry), read
# from BiomeLibrary.framework BMDeviceMetadata on macOS 27.2.1 (26B131). Data version 1
# adds 0 = Unknown and 9 = HomeAccessory. Values the class renders only as its fallback
# (version 0: 7, 9 and up; version 1: 10 and up) get no name.
PLATFORM_BY_VERSION = {
    0: {0: 'iPad', 1: 'iPhone', 2: 'MacDesktop', 3: 'MacPortable', 4: 'TV', 5: 'Watch',
        6: 'HomePod', 8: 'Vision'},
    1: dict(enumerate(('Unknown', 'iPad', 'iPhone', 'MacDesktop', 'MacPortable', 'TV',
                       'Watch', 'HomePod', 'Vision', 'HomeAccessory'))),
}


def _to_str(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', 'replace')
    if value is None:
        return ''
    return str(value)


@artifact_processor
def get_biomeDeviceMetadata(context):

    data_list = []
    source_dirs = set()
    for file_found in sorted(context.get_files_found()):
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in context.get_relative_path(file_found):
                continue
        else:
            continue

        source_dirs.add(os.path.dirname(file_found))
        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, TYPESS)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Device Metadata: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                os_build = _to_str(protostuff.get('2', b''))
                supplemental_build = _to_str(protostuff.get('4', b''))
                platform = protostuff.get('3', '')
                version = getattr(record, '_unknown_value', None)

                data_list.append((ts, record.state.name, os_build, supplemental_build,
                                  PLATFORM_BY_VERSION.get(version, {}).get(platform, ''),
                                  platform, _to_str(version), filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, None, None, None, None,
                                  filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'OS Build',
                    'Supplemental Build', 'Platform', 'Platform (raw)', 'Data Version',
                    'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
