__artifacts_v2__ = {
    "get_biomeDKInfocus": {
        "name": "Biome - In Focus DKEvent",
        "description": "Parses app in focus records from the _DKEvent.App.InFocus biome stream: the "
                       "bundle id, start and end times, and the launch reason and app version "
                       "metadata stored with the record.",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names come from CoreDuet's _DKPREvent class on macOS 27.2.1 (26B131); no "
                 "iOS copy of the class was read. Activity is the stream name (field 1.1) and Bundle "
                 "ID is the event's value string (field 4.3). The metadata columns are picked by each "
                 "entry's integer index, named from CoreDuet's own conversion of synthetic "
                 "records: Launch Reason 6002 (launchReason), Short Version 6007 "
                 "(shortVersionString), Exact Bundle Version 6008 (exactBundleVersion), Extension "
                 "Host ID 6003 (extensionHostIdentifier) and Extension Containing Bundle ID 6004 "
                 "(extensionContainingBundleIdentifier). Before, a Transition column took the first "
                 "metadata entry whatever its key. On 20 corpus images it held the launch reason on "
                 "5,195 written rows, a version string or extension id on 744, and was empty on 544. "
                 "Time Write is field 8, which the class names creationDate. Written records that "
                 "do not decode are skipped and logged (21, all on dexter_ios18, of 6,504 written "
                 "records on 20 corpus images)."),
        "paths": ('*/[Bb]iome/streams/restricted/_DKEvent.App.InFocus/local/*',),
        "output_types": "standard",
        "artifact_icon": "focus-2",
        "sample_data": {
            "felix_ios17": "iOS 17.6.1 | 261 rows",
            "fsfull002_ios17": "iOS 17.1 | 290 rows",
            "hc_ios18_7": "iOS 18.7.8 | 2024 rows",
            "iphone11_ios17": "iOS 17.3 | 2476 rows",
            "iphone12_ios18": "iOS 18.7 | 936 rows",
            "iphone14plus_ios18": "iOS 18.0 | 132 rows",
            "otto_ios17": "iOS 17.5.1 | 1758 rows",
            "dexter_ios18": "iOS 18.3.2 | 3838 rows",
            "abe_ios16": "iOS 16.5 | 2938 rows",
            "felix23_ios16": "iOS 16.5 | 753 rows",
            "magnet_ios16": "iOS 16.1.1 | 333 rows",
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


def _text(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    if value is None or isinstance(value, (dict, list)):
        return ''
    return str(value)


def _metadata_by_index(entries):
    """Metadata entries keyed by their integer index (field 7.N.3), with the string value.

    Index names, read from CoreDuet.framework on macOS 27.2.1 (26B131) through
    _DKEvent fromPBCodable: on synthetic records: 6002 launchReason, 6003
    extensionHostIdentifier, 6004 extensionContainingBundleIdentifier, 6007
    shortVersionString, 6008 exactBundleVersion (all _DKApplicationMetadataKey).
    """
    if isinstance(entries, dict):
        entries = [entries]
    found = {}
    for entry in entries or []:
        if not isinstance(entry, dict) or not isinstance(entry.get('3'), int):
            continue
        value = entry.get('2')
        found[entry['3']] = _text(value.get('3')) if isinstance(value, dict) else ''
    return found


@artifact_processor
def get_biomeDKInfocus(context):
    
    typess = {
        '1': {'type': 'message', 'message_typedef': {
            '1': {'type': 'str', 'name': ''},
            '2': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': ''},
                '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''},
        '2': {'type': 'double', 'name': ''},
        '3': {'type': 'double', 'name': ''},
        '4': {'type': 'message', 'message_typedef': {
            '1': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': ''},
                '2': {'type': 'int', 'name': ''}}, 'name': ''},
            '3': {'type': 'str', 'name': ''}}, 'name': ''},
        '5': {'type': 'str', 'name': ''},
        '7': {'type': 'message', 'message_typedef': {
            '1': {'type': 'bytes', 'name': ''},
            '2': {'type': 'message', 'message_typedef': {
                '1': {'type': 'message', 'message_typedef': {
                    '1': {'type': 'int', 'name': ''},
                    '2': {'type': 'int', 'name': ''}}, 'name': ''},
                '3': {'type': 'str', 'name': ''}}, 'name': ''},
            '3': {'type': 'int', 'name': ''}}, 'name': ''},
        '8': {'type': 'double', 'name': ''},
        '10': {'type': 'int', 'name': ''}}

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

        source_dirs.add(os.path.dirname(file_found))
        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, typess)

                    activity = (protostuff['1']['1'])
                    timestart = (webkit_timestampsconv(protostuff['2']))
                    timeend = (webkit_timestampsconv(protostuff['3']))
                    timewrite = (webkit_timestampsconv(protostuff['8']))

                    actionguid = (protostuff['5'])
                    bundleid = (protostuff['4']['3'])
                    meta = _metadata_by_index(protostuff.get('7'))
                except (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError) as ex:
                    logfunc(f"Skipping biomeDKInfocus record due to protobuf decode error: {ex} | "
                            f"File: {context.get_relative_path(file_found)} | "
                            f"Offset: {record.data_start_offset}")
                    continue

                data_list.append((ts, timestart, timeend, timewrite, record.state.name, activity, bundleid,
                                  meta.get(6002, ''), meta.get(6007, ''), meta.get(6008, ''),
                                  meta.get(6003, ''), meta.get(6004, ''),
                                  actionguid, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, None, None, record.state.name) + (None,) * 8 +
                                 (filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Time Start', 'datetime'), ('Time End', 'datetime'),
                    ('Time Write', 'datetime'), 'SEGB State', 'Activity', 'Bundle ID', 'Launch Reason', 'Short Version',
                    'Exact Bundle Version', 'Extension Host ID', 'Extension Containing Bundle ID', 'Action GUID',
                    'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
