__artifacts_v2__ = {
    "get_biomeNowplaying": {
        "name": "Biome - Now Playing",
        "description": "Parses Now Playing entries from biomes",
        "author": "@JohnHyla, @mattiaepi (Mattia Epifani)",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Records are read from both the local and remote subfolders; the Sync Origin "
                 "column reports which one a record came from, with the name of the folder under "
                 "remote. That this name identifies a device is not sourced here. The local and remote naming is the stream's own folder layout. That "
                 "a remote record is a copy synced from another device is not sourced here, so a "
                 "Remote row is not shown to be an event of this device. Files under a tombstone "
                 "folder are skipped. "
                 "The output device columns are the outputDevices field (field 14) of the "
                 "BMMediaNowPlaying class, a repeated BMMediaNowPlayingOutputDevice, read from "
                 "BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was "
                 "read. Output Device ID is outputDeviceID (field 14.3), reported before as Output. "
                 "Output Device Type is type (field 14.1: 0 Unknown, 1 AirPlay, 2 Bluetooth, "
                 "3 CarPlay, 4 BuiltIn, 5 Wired) and Output Device Sub Type is subType (field "
                 "14.2, 23 names from 0 Unknown to 22 HomeAccessory), each with its integer in a "
                 "(raw) column; both were not reported before. Several devices are joined with "
                 "' <-> '; on the tested images no written record held more than one. Output "
                 "Device ID held the same text as Output Device Sub Type on 527 of the 1,045 "
                 "written rows with a device, among them all 159 written rows of the legacy NowPlaying stream. That stream is read from its local folder only, so Sync Origin reads Local on its rows. Timestamp is absoluteTimestamp (field 2), which the class reads as seconds since 2001-01-01 UTC. Deleted rows carry no stored fields, so Output Device ID, "
                 "Output Device Type, Output Device Type (raw), Output Device Sub Type and Output "
                 "Device Sub Type (raw) are empty on them (all 31 rows on hc_ios17_2 were Deleted). "
                 "On the tested images 146 written rows had a Remote Sync Origin: the 96 on "
                 "falken_ios26 carried no output device, title or artist, and 50 on "
                 "wilkerson_iphone16_ios26 held an output device, 33 of them with a title.",
        "paths": (
            '*/Biome/streams/public/NowPlaying/local/*',
            '*/streams/*/Media.NowPlaying/local/*',
            '*/streams/*/Media.NowPlaying/remote/*',
        ),
        "output_types": "standard",
        "artifact_icon": "music",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 234 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 68 rows",
            "magnet_ios16": "iOS 16.1.1 | 22 rows",
            "hc_ios18_7": "iOS 18.7.8 | 14 rows",
            "iphone11_ios17": "iOS 17.3 | 242 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 22 rows (20 remote)",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 742 rows (108 remote)",
            "falken_ios26": "iOS 26.2.1 | 116 rows (102 remote)",
            "felix_ios17": "iOS 17.6.1 | 1986 rows (1976 remote)",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 6 rows",
            "iphone12_ios18": "iOS 18.7 | 25 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 126 rows",
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


# BMMediaNowPlayingOutputDevice type and subType names, read from BiomeLibrary.framework on
# macOS 27.2.1 (26B131), data version 1.
OUTPUT_DEVICE_TYPE = dict(enumerate(('Unknown', 'AirPlay', 'Bluetooth', 'CarPlay', 'BuiltIn',
                                     'Wired')))
OUTPUT_DEVICE_SUBTYPE = dict(enumerate((
    'Unknown', 'Standard', 'Speaker', 'Headphones', 'Headset', 'Receiver', 'LineOut', 'USB',
    'DisplayPort', 'HDMI', 'LowEnergy', 'SPDIF', 'TV', 'HomePod', 'AppleTV', 'Vehicle',
    'AirPlayCluster', 'SetTopBox', 'TVStick', 'Mac', 'IOS', 'Vision', 'HomeAccessory')))


def _output_devices(value):
    """outputDevices (field 14), a repeated BMMediaNowPlayingOutputDevice: returns the
    outputDeviceID, type and subType columns, each device joined with ' <-> '."""
    devices = value if isinstance(value, list) else [value] if isinstance(value, dict) else []
    ids, types, types_raw, subtypes, subtypes_raw = [], [], [], [], []
    for device in devices:
        if not isinstance(device, dict):
            continue
        device_type, subtype = device.get('1'), device.get('2')
        ids.append(str(device.get('3', '')))
        types.append(OUTPUT_DEVICE_TYPE.get(device_type, '') if type(device_type) is int else '')
        types_raw.append('' if device_type is None else str(device_type))
        subtypes.append(OUTPUT_DEVICE_SUBTYPE.get(subtype, '') if type(subtype) is int else '')
        subtypes_raw.append('' if subtype is None else str(subtype))
    return tuple(' <-> '.join(column) for column in
                 (ids, types, types_raw, subtypes, subtypes_raw))


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
def get_biomeNowplaying(context):

    typess = {
        '2': {'type': 'double', 'name': ''},
        '3': {'type': 'int', 'name': ''},
        '5': {'type': 'str', 'name': ''},
        '6': {'type': 'int', 'name': ''},
        '8': {'type': 'str', 'name': ''},
        '9': {'type': 'int', 'name': ''},
        '10': {'type': 'str', 'name': ''},
        '13': {'type': 'int', 'name': ''},
        '14': {
            'type': 'message',
            'message_typedef': {
                '1': {'type': 'int', 'name': ''},
                '2': {'type': 'int', 'name': ''},
                '3': {'type': 'str', 'name': ''}
            },
            'name': ''
        },
        '15': {'type': 'str', 'name': ''}
    }

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

        origin = _sync_origin(context.get_relative_path(file_found))
        source_dirs.add(os.path.dirname(file_found))
        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, typess)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Biome Now Playing: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue
                
                timestart = (webkit_timestampsconv(protostuff['2']))
                bundleid = (protostuff['15'])
                info = (protostuff.get('10',''))
                info2 = (protostuff.get('8',''))
                info3 = (protostuff.get('5',''))
                outputs = _output_devices(protostuff.get('14'))
                data_list.append((ts, timestart, record.state.name, bundleid, *outputs, info, info2,
                                  info3, origin, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, None,
                                  None, None, None, None, origin, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Timestamp', 'datetime'), 'SEGB State', 'Bundle ID',
                    'Output Device ID', 'Output Device Type', 'Output Device Type (raw)',
                    'Output Device Sub Type', 'Output Device Sub Type (raw)', 'Media Type', 'Title', 'Artist', 'Sync Origin', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
