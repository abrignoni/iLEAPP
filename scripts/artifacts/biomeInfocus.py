__artifacts_v2__ = {
    "get_biomeInfocus": {
        "name": "Biome - In Focus",
        "description": "Parses InFocus Events from biomes",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names are those of the BMAppInFocus class, read from "
                 "BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was "
                 "read. Starting is field 3, a true or false value. It was reported before as "
                 "Action, with Foreground for 1 and Background for 0; the framework names the "
                 "field starting and gives no names to its values. On the tested images (21 images, 30,365 written rows) Starting held True on 15,241 rows and False on 15,124. Records are "
                 "read from both the local and remote subfolders. The Sync Origin column reports "
                 "which one a record came from, with the name of the folder under remote. That "
                 "this name identifies a device is not sourced here. Files under a tombstone folder are "
                 "skipped."
                 " "
                 "On 5 tested images (jess_ios15 on iOS 15; abe_ios16, felix23_ios16, hexordia_ios1651 and magnet_ios16 on iOS 16) the stream is stored under AppLaunch, which BiomeLibrary.framework on macOS 27.2.1 (26B131) lists as its legacy name, and is read too. Fields 3, 4 and 6, which this artifact reports, were present on all 4,053 written records there. Those records also carry field 5 (duration), which is not reported. Launch Reason (field 1, launchReason), Short Version (field 9, shortVersionString), Exact Version (field 10, exactVersionString) and Display Type (field 13, displayType) come from the BMAppInFocus class in BiomeLibrary.framework, macOS 27.2.1 (26B131); no iOS copy was read. None was reported before. On the 21 iOS images tested (21 held written records of this stream, 30,365 written rows), Launch Reason was set on 7,083 rows (152 distinct values, shown as stored; their meaning is not decoded here. By shape: 4,833 values start with com.apple.SpringBoard or com.apple.springboard, 2,015 start with a name prefixed SB, CS, BLS or _SB and hold no UUID, 132 hold a UUID and 103 are other), Short Version on 27,766 (20 images) and Exact Version on 27,826 (20 images). Display Type was set on 6,674 rows on 8 images: Unknown (0) on 3,569 and MainDisplay (1) on 3,105. The class also names 4 as Continuity, which did not occur. The per-record integer that the SEGB reader leaves unnamed was 10 on the 30,365 written records. The BMAppInFocus class declares 10 as its latest data version. Field 5 (duration) is not reported: it was zero on the 4,054 rows that held it."),
        "paths": ('*/[Bb]iome/streams/restricted/App.InFocus/local/*',
                  '*/[Bb]iome/streams/restricted/App.InFocus/remote/*',
                  '*/[Bb]iome/streams/*/AppLaunch/local/*',
                  '*/[Bb]iome/streams/*/AppLaunch/remote/*'),
        "output_types": "standard",
        "artifact_icon": "focus-2",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 3895 rows (1456 remote)",
            "felix_ios17": "iOS 17.6.1 | 20368 rows (19852 remote)",
            "fsfull002_ios17": "iOS 17.1 | 680 rows (121 remote)",
            "hc_ios18_7": "iOS 18.7.8 | 4031 rows",
            "iphone11_ios17": "iOS 17.3 | 4943 rows",
            "iphone12_ios18": "iOS 18.7 | 2073 rows (205 remote)",
            "iphone14plus_ios18": "iOS 18.0 | 909 rows (647 remote)",
            "otto_ios17": "iOS 17.5.1 | 1139 rows (314 remote)",
            "abe_ios16": "iOS 16.5 | 5967 rows (115 remote)",
            "felix23_ios16": "iOS 16.5 | 1446 rows",
            "magnet_ios16": "iOS 16.1.1 | 660 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 2357 rows (1490 remote)",
            "cookbook_ios1751": "iOS 17.5.1 | 947 rows (240 remote)",
            "falken_ios26": "iOS 26.2.1 | 2374 rows (730 remote)",
            "hc_ios26": "iOS 26.5.2 | 545 rows (230 remote)",
        }
    }
}


import os
import struct
from datetime import timezone
from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)


# displayType names, read from BiomeLibrary.framework BMAppInFocus on macOS 27.2.1 (26B131).
DISPLAY_TYPE = {0: 'Unknown', 1: 'MainDisplay', 4: 'Continuity'}


def _text(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    return '' if value is None or isinstance(value, (dict, list)) else str(value)


def _sync_origin(file_found):
    """Local for a file under local/, Remote (<folder>) for a file under remote/, where <folder>
    is the name of the folder under remote/. What that name identifies is not sourced here."""
    normalized = file_found.replace('\\', '/')
    if '/remote/' in normalized:
        trailer = normalized.split('/remote/', 1)[1]
        if '/' in trailer:
            return f"Remote ({trailer.split('/', 1)[0]})"
        return 'Remote'
    return 'Local'


@artifact_processor
def get_biomeInfocus(context):

    typess = {'1': {'name': '', 'type': 'bytes'}, '10': {'name': '', 'type': 'bytes'},
              '13': {'name': '', 'type': 'int'}, '2': {'name': '', 'type': 'int'}, '3': {'name': '', 'type': 'int'},
              '4': {'name': '', 'type': 'double'}, '6': {'name': '', 'type': 'str'},
              '9': {'name': '', 'type': 'bytes'}}

    data_list = []
    source_dirs = set()
    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in context.get_relative_path(file_found):
                continue
        else:
            continue

        origin = _sync_origin(file_found)
        source_dirs.add(os.path.dirname(file_found))
        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, typess)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Biome In Focus: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                bundleid = (protostuff['6'])
                # an NSDate sentinel converts to ''; kept as None, as in the Deleted rows
                timestart = (webkit_timestampsconv(protostuff['4']) or None)
                state = protostuff['3']
                starting = {1: 'True', 0: 'False'}.get(state, '')

                display_type = protostuff.get('13') if type(protostuff.get('13')) is int else ''

                data_list.append((ts, timestart, record.state.name, bundleid, starting,
                                  _text(protostuff.get('1')), _text(protostuff.get('9')),
                                  _text(protostuff.get('10')), DISPLAY_TYPE.get(display_type, ''), display_type,
                                  origin, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, None, None, None, origin, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Absolute Timestamp', 'datetime'), 'SEGB State', 'Bundle ID', 'Starting',
                    'Launch Reason', 'Short Version', 'Exact Version', 'Display Type', 'Display Type (raw)', 'Sync Origin', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))

