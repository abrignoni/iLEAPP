__artifacts_v2__ = {
    "get_biomeBluetooth": {
        "name": "Biome - Bluetooth",
        "description": "Parses Bluetooth device entries from biomes",
        "author": "@JohnHyla, @AlexisBrignoni, Codex",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "Use caution when interpreting this artifact. Lists of Bluetooth devices have been "
                 "observed sharing a single SEGB timestamp, so the presence of a device in this "
                 "stream does not establish that the device was connected to the iOS device at "
                 "that time. Reference: Mattia Epifani, '84 Streams Later, Part 2: Inside Apple "
                 "Biome', https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html\n"
                 "Records are read from both the local and remote subfolders; the Sync Origin "
                 "column classifies the evidence-relative stream folder, not the staging path: "
                 "Local, Remote, or Remote (folder name). Unknown means the stream layout "
                 "was not recognized unambiguously. These labels do not establish a device "
                 "writer or account relationship. Records under the remote folder sit in a subfolder named by an "
                 "identifier. What device wrote them is not established here, so they should not "
                 "be read as events of this device. Files under a tombstone folder are skipped.\n"
                 "Starting is field 4 (starting, a boolean stored as 0 or 1) and Device Type is "
                 "field 5 (deviceType), with its integer in a (raw) column. Neither was reported "
                 "before. Field numbers and names are those of the BMDeviceBluetooth class, "
                 "read from BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was read. What Starting marks is not established. On the tested "
                 "images (6 of 21 images held written records, 118 written rows) Starting held 1 "
                 "on 46 rows and 0 on 72. Device Type held 7 values: Handsfree 56, Headset 31, "
                 "Headphones 18, Generic 6, VideoDisplay 4, CarStereo 2 and Keyboard 1. Field 10 "
                 "(userWearing) is not reported: it held 1 on each of the 118 rows, across the "
                 "device types, so it does not separate them. Deleted rows leave the new columns "
                 "empty.",
        "paths": ('*/Biome/streams/restricted/Device.Wireless.Bluetooth/local/*',
                  '*/Biome/streams/restricted/Device.Wireless.Bluetooth/remote/*'),
        "output_types": "standard",
        "artifact_icon": "bluetooth",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 12 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 724 rows (21 remote)",
            "hc_ios17_2": "iOS 17.2.1 | 20 rows",
            "dexter_ios18": "iOS 18.3.2 | 87 rows (14 remote)",
            "felix_ios17": "iOS 17.6.1 | 420 rows (420 remote)",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 4 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 22 rows",
            "abe_ios16": "iOS 16.5 | 84 rows",
            "felix23_ios16": "iOS 16.5 | 10 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
        }
    }
}


import os
import struct
from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from datetime import timezone
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)


# deviceType names, read from BiomeLibrary.framework BMDeviceBluetooth on macOS 27.2.1 (26B131).
DEVICE_TYPE = {
    0: 'Unknown', 1: 'Generic', 2: 'GenericComputer', 3: 'GenericPhone', 4: 'GenericAudioVideo',
    5: 'GenericPeripheral', 6: 'GenericImaging', 7: 'GenericToy', 8: 'DesktopComputer',
    9: 'LaptopComputer', 10: 'WearableComputer', 11: 'Server', 12: 'PDA', 13: 'MobilePhone',
    14: 'CordlessPhone', 15: 'Modem', 16: 'AccessPoint', 17: 'Headset', 18: 'Handsfree',
    19: 'Microphone', 20: 'Speaker', 21: 'Headphones', 22: 'PortableAudio', 23: 'CarStereo',
    24: 'HifiStereo', 25: 'Keyboard', 26: 'Mouse', 27: 'Gamepad', 28: 'RemoteControl',
    29: 'Sensor', 30: 'Tablet', 31: 'CardReader', 32: 'Printer', 33: 'Scanner', 34: 'Camera',
    35: 'VideoCamera', 36: 'Display', 37: 'VideoDisplay', 38: 'VideoConferencing', 39: 'SetTopBox',
    40: 'VCR', 41: 'GamingConsole', 42: 'ToyController', 43: 'Watch', 44: 'Pager', 45: 'Jacket',
    46: 'Helmet', 47: 'Glasses', 48: 'A2dp', 49: 'LePeripheral', 50: 'AppleTrackpad'
}


def _sync_origin(relative_path):
    """Classify the stored Bluetooth stream folder without inferring its writer."""
    if not isinstance(relative_path, str) or not relative_path:
        return 'Unknown'
    normalized = relative_path.replace('\\', '/')
    if normalized.startswith('/') or (
            len(normalized) >= 3 and normalized[0].isalpha()
            and normalized[1:3] == ':/'):
        return 'Unknown'
    parts = normalized.split('/')
    if any(part in ('.', '..') for part in parts):
        return 'Unknown'
    anchor = ['Biome', 'streams', 'restricted', 'Device.Wireless.Bluetooth']
    positions = [index for index in range(len(parts) - len(anchor) + 1)
                 if parts[index:index + len(anchor)] == anchor]
    if len(positions) != 1:
        return 'Unknown'
    tail = parts[positions[0] + len(anchor):]
    if len(tail) < 2 or any(not part for part in tail):
        return 'Unknown'
    if tail[0] == 'local':
        return 'Local'
    if tail[0] == 'remote':
        return f'Remote ({tail[1]})' if len(tail) > 2 else 'Remote'
    return 'Unknown'


@artifact_processor
def get_biomeBluetooth(context):

    # Only the added fields are pinned, so the decoding of the existing columns is unchanged.
    typess = {'4': {'type': 'int', 'name': ''}, '5': {'type': 'int', 'name': ''}}

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
                    logfunc(f'Biome Bluetooth: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue
                
                mac = protostuff['1'].decode()
                if isinstance(protostuff['2'], dict):
                    desc = protostuff['2']
                else:
                    desc = protostuff['2'].decode()
                device_type = protostuff.get('5')
                is_int = type(device_type) is int
                data_list.append((ts, record.state.name, mac, desc, origin, protostuff.get('4', ''),
                                  DEVICE_TYPE.get(device_type, '') if is_int else '',
                                  device_type if is_int else '', filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, None, origin, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'MAC', 'Name', 'Sync Origin',
                    'Starting', 'Device Type', 'Device Type (raw)', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
