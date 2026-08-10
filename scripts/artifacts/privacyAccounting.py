__artifacts_v2__ = {
    'privacyAccountingAccess': {
        'name': 'Privacy Accounting - Resource Accesses',
        'description': 'Resource-access records from the privacyaccountingd SEGB streams under '
                       'PrivacyAccounting/Biome (tcc, location, oop): the accessing bundle '
                       'identifier, the TCC service name where the stream carries one, an access '
                       'identifier shared by paired records, and the record kind.',
        'author': '@abrignoni, @mattiaepi (Mattia Epifani)',
        'creation_date': '2026-07-31',
        'last_update_date': '2026-07-31',
        'requirements': 'none',
        'category': 'App Permissions',
        'notes': ('Biome-format SEGB v2 streams stored under PrivacyAccounting/Biome rather than '
                  'the main Biome folder; location reported and sample data provided by Mattia '
                  'Epifani. Recording is gated by a setting: privacyaccountingd contains the log '
                  'string "Logging disabled, ignoring incoming access" and a '
                  'PASettingsLoggingEnabled key, and in every local test image the stream folders '
                  'exist with no records. This gating is consistent with the App Privacy Report '
                  'feature, which is off until enabled. Kind is an integer reported as stored: in '
                  'the sample data every access identifier appeared exactly twice, kind 2 then '
                  'kind 3, and privacyaccountingd\'s log strings describe accesses as begin/end '
                  'intervals, but the kind values themselves are not documented. Records in the '
                  'location stream carry no service name; in the sample data the tcc stream held '
                  'kTCCService* names and the oop stream held a numeric value there. Pruned '
                  'records remain in the live segments as deleted-state SEGB entries whose '
                  'payload bytes were zeroed in the sample data but whose timestamps survive: '
                  'they are reported with timestamp, state and stream only, and reached months '
                  'to years before the earliest written record, showing that access events '
                  'occurred at those times without identifying the client or service.'),
        'paths': ('*/mobile/Library/PrivacyAccounting/Biome/com.apple.privacy.accounting.stream*/local/*',),
        'output_types': 'standard',
        'artifact_icon': 'shield-lock',
        'sample_data': {
            'hc_ios18_7': 'iOS 18.7.8 | stream folders present, no records',
            'hc_ios26': 'iOS 26 | stream folders present, no records',
        },
    },
    'privacyAccountingTombstones': {
        'name': 'Privacy Accounting - Stream Tombstones',
        'description': 'Entries from the tombstone folders of the privacyaccountingd SEGB '
                       'streams. Each entry names a stream segment file and the recording '
                       'process; entry timestamps record when the entries were written.',
        'author': '@abrignoni, @mattiaepi (Mattia Epifani)',
        'creation_date': '2026-07-31',
        'last_update_date': '2026-07-31',
        'requirements': 'none',
        'category': 'App Permissions',
        'notes': ('Tombstone entries accompany pruning of the access streams: privacyaccountingd '
                  'holds a com.apple.PrivacyAccounting.prune activity and is the process named '
                  'in every sample entry. Referenced segment names decode as Apple absolute '
                  'timestamps in microseconds (the Referenced Segment Name Time column); in '
                  'unpruned segments observed, that time matched the earliest record. Referenced '
                  'segments may no longer exist or may have been rewritten since an entry was '
                  'made. Fields 2, 3, 4 and 6 are integers whose meaning is not documented and '
                  'are reported as stored. In the sample data, tombstone entries existed for '
                  'segments dating back well before the earliest surviving stream records, '
                  'documenting that older data existed and was removed.'),
        'paths': ('*/mobile/Library/PrivacyAccounting/Biome/com.apple.privacy.accounting.stream*/local/*',),
        'output_types': 'standard',
        'artifact_icon': 'trash',
        'sample_data': {
            'hc_ios18_7': 'iOS 18.7.8 | no tombstone files',
            'hc_ios26': 'iOS 26 | no tombstone files',
        },
    },
}


import os
from datetime import datetime, timedelta, timezone
from uuid import UUID
from scripts import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc

APPLE_EPOCH = datetime(2001, 1, 1, tzinfo=timezone.utc)

# Field 1.2 is a 16-byte identifier whose raw bytes can look like a nested
# protobuf message, so its decoding is forced instead of letting the decoder
# guess. Fields left out of a typedef keep their wiretype-inferred decoding;
# the streams are not uniform there (the service field is a string in the tcc
# stream but numeric in the oop stream, and tombstone field 6 switches between
# varint and fixed64 encodings across files).
ACCESS_TYPEDEF = {
    '1': {'type': 'message', 'message_typedef': {
        '1': {'type': 'message', 'message_typedef': {
            '1': {'type': 'int'},
            '2': {'type': 'bytes'}}},
        '2': {'type': 'bytes'},
        '3': {'type': 'int'}}},
}

TOMBSTONE_TYPEDEF = {
    '1': {'type': 'bytes'},
    '5': {'type': 'bytes'},
}


def _stream_name(file_found):
    for part in file_found.replace('\\', '/').split('/'):
        if part.startswith('com.apple.privacy.accounting.stream'):
            return part
    return ''


def _text(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    return '' if value is None else str(value)


def _access_id(value):
    if isinstance(value, bytes) and len(value) == 16:
        return str(UUID(bytes=value)).upper()
    if isinstance(value, bytes):
        return value.hex()
    return ''


def _segment_name_time(name):
    try:
        return APPLE_EPOCH + timedelta(microseconds=int(name))
    except (TypeError, ValueError):
        return ''


def _stream_files(context, tombstones):
    for file_found in map(str, context.get_files_found()):
        if os.path.basename(file_found).startswith('.'):
            continue
        if not os.path.isfile(file_found):
            continue
        is_tombstone = 'tombstone' in file_found.replace('\\', '/').split('/')
        if is_tombstone == tombstones:
            yield file_found


@artifact_processor
def privacyAccountingAccess(context):

    data_list = []
    for file_found in _stream_files(context, tombstones=False):
        stream = _stream_name(file_found)
        filename = os.path.basename(file_found)
        for record in read_segb_file(file_found):
            if record.state not in (EntryState.Written, EntryState.Deleted):
                continue
            ts = record.timestamp1.replace(tzinfo=timezone.utc)

            # Deleted-state entries retain their timestamps; observed payloads
            # were zeroed, but decoding is still attempted in case other
            # devices retain them. Rows whose payload does not decode to the
            # expected shape keep their timestamp, state and stream.
            message = None
            if record.data:
                try:
                    message, _ = blackboxprotobuf.decode_message(record.data, ACCESS_TYPEDEF)
                except Exception as ex:  # pylint: disable=broad-exception-caught
                    if record.state == EntryState.Written:
                        logfunc(f'Privacy Accounting: undecoded record in {filename} at offset '
                                f'{record.data_start_offset}: {ex}')

            event = message.get('1') if isinstance(message, dict) else None
            if isinstance(event, dict):
                client = event.get('1') if isinstance(event.get('1'), dict) else {}
                data_list.append((ts, record.state.name, stream,
                                  _text(client.get('2')), client.get('1'),
                                  _text(message.get('2')), event.get('3'),
                                  _access_id(event.get('2')),
                                  filename, record.data_start_offset))
            else:
                data_list.append((ts, record.state.name, stream, None, None, None, None, None,
                                  filename, record.data_start_offset))

    data_list.sort(key=lambda row: row[0])

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Stream', 'Client',
                    'Client ID Type (as stored)', 'Service (as stored)', 'Kind (as stored)',
                    'Access ID', 'Filename', 'Offset')

    return data_headers, data_list, 'see Filename for more info'


@artifact_processor
def privacyAccountingTombstones(context):

    data_list = []
    for file_found in _stream_files(context, tombstones=True):
        stream = _stream_name(file_found)
        filename = os.path.basename(file_found)
        for record in read_segb_file(file_found):
            ts = record.timestamp1.replace(tzinfo=timezone.utc)

            if record.state not in (EntryState.Written, EntryState.Deleted):
                continue

            message = None
            if record.data:
                try:
                    message, _ = blackboxprotobuf.decode_message(record.data, TOMBSTONE_TYPEDEF)
                except Exception as ex:  # pylint: disable=broad-exception-caught
                    if record.state == EntryState.Written:
                        logfunc(f'Privacy Accounting: undecoded tombstone in {filename} at '
                                f'offset {record.data_start_offset}: {ex}')

            if isinstance(message, dict) and message.get('1') is not None:
                segment = _text(message.get('1'))
                data_list.append((ts, record.state.name, stream, segment,
                                  _segment_name_time(segment),
                                  message.get('2'), message.get('3'), message.get('4'),
                                  _text(message.get('5')), message.get('6'),
                                  filename, record.data_start_offset))
            else:
                data_list.append((ts, record.state.name, stream, None, None, None, None, None,
                                  None, None, filename, record.data_start_offset))

    data_list.sort(key=lambda row: row[0])

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Stream',
                    'Referenced Segment', ('Referenced Segment Name Time', 'datetime'),
                    'Field 2 (as stored)', 'Field 3 (as stored)', 'Field 4 (as stored)',
                    'Process', 'Field 6 (as stored)', 'Filename', 'Offset')

    return data_headers, data_list, 'see Filename for more info'
