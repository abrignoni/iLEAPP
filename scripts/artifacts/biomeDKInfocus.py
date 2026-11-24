__artifacts_v2__ = {
    "get_biomeDKInfocus": {
        "name": "Biome - In Focus DKEvent",
        "description": "Parses app in focus records from the _DKEvent.App.InFocus biome stream: the "
                       "bundle id, start and end times, and the launch reason and app version "
                       "metadata stored with the record.",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-11-24",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names come from CoreDuet's _DKPREvent class on macOS 27.2.1 (26B131); no "
                 "iOS copy of the class was read. Start Date, End Date and Identifier are fields 2, 3 and 5 (startDate, endDate and identifier) and were reported before as Time Start, Time End and Action GUID. Stream Name is field 1.1 (the name of the record's stream), reported before as Activity, and Bundle "
                 "ID is the event's value string (field 4.3). The metadata columns are picked by each "
                 "entry's integer index, named from CoreDuet's own conversion of synthetic "
                 "records: Launch Reason 6002 (launchReason), Short Version 6007 "
                 "(shortVersionString), Exact Bundle Version 6008 (exactBundleVersion), Extension "
                 "Host ID 6003 (extensionHostIdentifier) and Extension Containing Bundle ID 6004 "
                 "(extensionContainingBundleIdentifier). Before, a Transition column took the first "
                 "metadata entry whatever its key. On 20 corpus images it held the launch reason on "
                 "5,195 written rows, a version string or extension id on 744, and was empty on 544. "
                 "Creation Date is field 8 (creationDate), reported before as Time Write. Written records that "
                 "do not decode are skipped and logged (21, all on dexter_ios18, of 6,504 written "
                 "records on 20 corpus images). Time Zone Offset (seconds) is field 10 (timeZone), which CoreDuet's own conversion of synthetic records reads as seconds from GMT; it was not reported before. On the 21 iOS images tested (20 held written records of this stream), it was set on each of the 6,483 written rows, with 9 distinct values, each a whole number of quarter hours within 14 hours of GMT. A Start Date, End Date or Creation Date whose stored value is not a number, is NaN or infinite, or is too large for a date is left empty, and the record keeps its row. The log names the file name and the record offset. The NSDate distantPast and distantFuture values, and a value within two days after distantPast, are also left empty, and the log does not name the file or offset for those. A synthetic test (admin/test/scripts/test_biome_dkevent_bad_dates.py) checks the first case with NaN, infinity and an out-of-range number in Start Date and with NaN in End Date and Creation Date. No record on the 4 corpus images run for this change (hill_iphone15pro_ios26, wilkerson_iphone16_ios26, dexter_ios18, iphone11_ios17) held such a value."),
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
from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.biome_stream_records import cocoa_date


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
                    # an NSDate sentinel converts to ''; kept as None, as in the Deleted rows
                    timestart = (cocoa_date(protostuff['2'], 'Biome App In Focus DKEvent', filename, record.data_start_offset) or None)
                    timeend = (cocoa_date(protostuff['3'], 'Biome App In Focus DKEvent', filename, record.data_start_offset) or None)
                    timewrite = (cocoa_date(protostuff['8'], 'Biome App In Focus DKEvent', filename, record.data_start_offset) or None)

                    actionguid = (protostuff['5'])
                    bundleid = (protostuff['4']['3'])
                    meta = _metadata_by_index(protostuff.get('7'))
                    tz_offset = protostuff.get('10') if type(protostuff.get('10')) is int else ''
                except (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError) as ex:
                    logfunc(f"Skipping biomeDKInfocus record due to protobuf decode error: {ex} | "
                            f"File: {context.get_relative_path(file_found)} | "
                            f"Offset: {record.data_start_offset}")
                    continue

                data_list.append((ts, timestart, timeend, timewrite, tz_offset, record.state.name, activity, bundleid,
                                  meta.get(6002, ''), meta.get(6007, ''), meta.get(6008, ''),
                                  meta.get(6003, ''), meta.get(6004, ''),
                                  actionguid, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, None, None, None, record.state.name) + (None,) * 8 +
                                 (filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Start Date', 'datetime'), ('End Date', 'datetime'),
                    ('Creation Date', 'datetime'), 'Time Zone Offset (seconds)', 'SEGB State', 'Stream Name', 'Bundle ID', 'Launch Reason', 'Short Version',
                    'Exact Bundle Version', 'Extension Host ID', 'Extension Containing Bundle ID', 'Identifier',
                    'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
