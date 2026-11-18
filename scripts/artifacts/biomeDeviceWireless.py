__artifacts_v2__ = {
    "get_biomeDeviceNFCTag": {
        "name": "Biome - NFC Tag",
        "description": "Records from the Device.Wireless.NFCTag biome stream, with the tag ID "
                       "each stores.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field names and numbers come from the class's protoFields in "
                 "BiomeLibrary.framework, read on macOS 27.2.1 (26B131). That the iOS writer uses "
                 "the same schema was checked only against the data: every written record decoded "
                 "to those fields. SEGB Timestamp is the SEGB record time; what it marks was not "
                 "checked against another record. Records the SEGB file marks deleted, and the "
                 "stream's tombstone folder, are not read. Each tested image that holds the stream "
                 "has one file in its local folder, so SEGB File held one value on every row. "
                 "Field: 1 tagID, shown as hex with its length. On hill_iphone15pro_ios26 the 126 "
                 "rows hold 109 tag IDs of 16 bytes (2 distinct), 16 of 8 bytes (16 distinct) and "
                 "1 of 24 bytes; on iphone11_ios17 the 209 rows hold 190 of 8 bytes (190 "
                 "distinct), 11 of 24, 6 of 16 and 2 of 14. An 8-byte value differed on every row, "
                 "so whether it identifies a tag or a single read is not established. "
                 "wilkerson_iphone16_ios26 holds no written record.",
        "paths": ('*/streams/*/Device.Wireless.NFCTag/local/*',),
        "output_types": "standard",
        "artifact_icon": "nfc",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 126 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 0 rows, no written record",
            "iphone11_ios17": "iOS 17.3 | 209 rows",
        },
    },
    "get_biomeDeviceDefaultPairedNearby": {
        "name": "Biome - Default Paired Device Nearby",
        "description": "Records from the Device.Wireless.DefaultPairedNearby biome stream, with "
                       "the starting flag each stores.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field names and numbers come from the class's protoFields in "
                 "BiomeLibrary.framework, read on macOS 27.2.1 (26B131). That the iOS writer uses "
                 "the same schema was checked only against the data: every written record decoded "
                 "to those fields. SEGB Timestamp is the SEGB record time; what it marks was not "
                 "checked against another record. Records the SEGB file marks deleted, and the "
                 "stream's tombstone folder, are not read. Each tested image that holds the stream "
                 "has one file in its local folder, so SEGB File held one value on every row. "
                 "Field: 1 starting. Which device is the default paired device is not stored. "
                 "Starting held No on all 8 rows of hill_iphone15pro_ios26 and was Yes on 506 of "
                 "1,264 rows of wilkerson_iphone16_ios26. iphone11_ios17 holds no stream file.",
        "paths": ('*/streams/*/Device.Wireless.DefaultPairedNearby/local/*',),
        "output_types": "standard",
        "artifact_icon": "bluetooth",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 8 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 1264 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows, no stream file",
        },
    },
    "get_biomeDeviceBluetoothNearbyDevice": {
        "name": "Biome - Bluetooth Nearby Device",
        "description": "Records from the Device.Wireless.BluetoothNearbyDevice biome stream: the "
                       "initiator and starting flags, the local identifier and the use case each "
                       "stores.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field names and numbers come from the class's protoFields in "
                 "BiomeLibrary.framework, read on macOS 27.2.1 (26B131). That the iOS writer uses "
                 "the same schema was checked only against the data: every written record decoded "
                 "to those fields. SEGB Timestamp is the SEGB record time; what it marks was not "
                 "checked against another record. Records the SEGB file marks deleted, and the "
                 "stream's tombstone folder, are not read. Each tested image that holds the stream "
                 "has one file in its local folder, so SEGB File held one value on every row. "
                 "Fields: 1 initiator, 2 localIdentifier, 3 starting and 4 useCase. No names for "
                 "useCase were found in the framework, so Use Case is reported as stored. "
                 "Initiator held Yes on every row of the tested images. On "
                 "wilkerson_iphone16_ios26 the 660 rows carry one Local Identifier and Use Case "
                 "held 11 on every row, half with Starting Yes. On iphone11_ios17 Use Case held 11 "
                 "on 301 of 307 rows. Local Identifier is reported as stored, and which device it "
                 "names is not resolved here. hill_iphone15pro_ios26 holds no written record.",
        "paths": ('*/streams/*/Device.Wireless.BluetoothNearbyDevice/local/*',),
        "output_types": "standard",
        "artifact_icon": "bluetooth",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows, no written record",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 660 rows",
            "iphone11_ios17": "iOS 17.3 | 307 rows",
        },
    },
}


import os
import struct
from datetime import timezone

from google.protobuf.message import DecodeError
from scripts import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError)
# Field names and numbers from the protoFields of BMDeviceNFCTag (1 tagID),
# BMDeviceDefaultPairedNearby (1 starting) and BMDeviceBluetoothNearbyDevice (1 initiator,
# 2 localIdentifier, 3 starting, 4 useCase), read from BiomeLibrary.framework on macOS 27.2.1
# (26B131).
_BYTES = {'2': {'type': 'bytes'}}


def _flag(value):
    if value is None:
        return ''
    return 'Yes' if value else 'No'


def _text(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    return '' if value is None or isinstance(value, (dict, list)) else str(value)


def _records(context, label, types=None):
    sources = set()
    rows = []
    for found in sorted(str(path) for path in context.get_files_found()):
        name = os.path.basename(found)
        if name.startswith('.') or not os.path.isfile(found):
            continue
        if '/tombstone/' in context.get_relative_path(found).replace('\\', '/'):
            continue
        sources.add(os.path.dirname(found))
        for record in read_segb_file(found):
            if record.state != EntryState.Written:
                continue
            try:
                message, _ = blackboxprotobuf.decode_message(record.data, types or {})
            except _DECODE_ERRORS as error:
                logfunc(f'{label}: could not decode record at offset {record.data_start_offset} '
                        f'in {name}: {error}')
                continue
            rows.append((record, message, name))
    return rows, '\n'.join(sorted(sources))


@artifact_processor
def get_biomeDeviceNFCTag(context):
    rows, sources = _records(context, 'NFC Tag', {'1': {'type': 'bytes'}})
    data_list = []
    for record, message, name in rows:
        tag = message.get('1')
        data_list.append((record.timestamp1.replace(tzinfo=timezone.utc),
                          tag.hex() if isinstance(tag, bytes) else _text(tag),
                          len(tag) if isinstance(tag, bytes) else '', name,
                          record.data_start_offset))
    headers = (('SEGB Timestamp', 'datetime'), 'Tag ID (hex)', 'Tag ID Length (bytes)',
               'SEGB File', 'Offset')
    return headers, data_list, sources


@artifact_processor
def get_biomeDeviceDefaultPairedNearby(context):
    rows, sources = _records(context, 'Default Paired Nearby')
    data_list = [(record.timestamp1.replace(tzinfo=timezone.utc), _flag(message.get('1')), name,
                  record.data_start_offset) for record, message, name in rows]
    headers = (('SEGB Timestamp', 'datetime'), 'Starting', 'SEGB File', 'Offset')
    return headers, data_list, sources


@artifact_processor
def get_biomeDeviceBluetoothNearbyDevice(context):
    rows, sources = _records(context, 'Bluetooth Nearby Device', _BYTES)
    data_list = []
    for record, message, name in rows:
        data_list.append((record.timestamp1.replace(tzinfo=timezone.utc), _flag(message.get('3')),
                          _flag(message.get('1')), _text(message.get('2')),
                          '' if message.get('4') is None else message.get('4'), name,
                          record.data_start_offset))
    headers = (('SEGB Timestamp', 'datetime'), 'Starting', 'Initiator', 'Local Identifier',
               'Use Case (as stored)', 'SEGB File', 'Offset')
    return headers, data_list, sources
