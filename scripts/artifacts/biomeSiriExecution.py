__artifacts_v2__ = {
    "get_biomeSiriExecution": {
        "name": "Biome - Siri Execution",
        "description": "Parses Siri execution events from the Siri.Execution biome stream "
                       "(BMPBSiriExecutionEvent). A written record can carry a task step, an "
                       "intent name, a status reason, a slot value, an app bundle id, a task "
                       "id, an interaction id, and an absolute timestamp. Field names were "
                       "taken from the BMPBSiriExecutionEvent class in BiomeStreams.framework "
                       "on macOS 27.2; the three written records on the tested otto_ios17 "
                       "(iOS 17.5.1) image parsed through that class and each field came back "
                       "under the name used here.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-13",
        "last_update_date": "2026-11-13",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field names and two task-step names (0 = Start, 6 = Completed) come from the "
                 "BMPBSiriExecutionEvent class in BiomeStreams.framework on macOS 27.2; that "
                 "class names other task steps, and this artifact maps only the two seen in the "
                 "tested records, leaving other Task Step integers blank with the stored value "
                 "in Task Step (raw). The names are source-verified against the macOS class; the "
                 "parse was run on the three written records from otto_ios17 (iOS 17.5.1), and "
                 "the iOS 17 and iOS 18 builds of the class were not read. On those records the "
                 "task id and interaction id were UUID-format strings. The Absolute Timestamp is "
                 "a Cocoa epoch (seconds since 2001-01-01 UTC); on the three tested records it "
                 "matched the SEGB record timestamp within about 14 ms (otto_ios17). Live "
                 "written records were present on only one tested image (otto_ios17, 3 written); "
                 "iphone11_ios17 and dexter_ios18 held this stream with deleted records only. "
                 "Eight other tested images produced no rows: three held Siri.Execution files "
                 "with no records (felix_ios17, hc_ios18_7, iphone14plus_ios18) and five held no "
                 "Siri.Execution files. This artifact does not decode the payload of deleted "
                 "records; a Deleted row has a timestamp, a state and a file location but no "
                 "fields. On the tested written records App Bundle ID held 'none' and Slot Value "
                 "held 'none' or 'not_applicable'; both are reported as stored. Filename is the "
                 "SEGB segment file name; on otto_ios17 all rows came from one segment file, so "
                 "Filename held one value there, and files under the tombstone folder are not "
                 "read. On the tested images the stream was under streams/restricted.",
        "paths": ('*/streams/*/Siri.Execution/local/*',),
        "output_types": "standard",
        "artifact_icon": "mic",
        "sample_data": {
            "otto_ios17": "iOS 17 | 49 rows (3 written, 46 deleted)",
            "iphone11_ios17": "iOS 17 | 11 rows (deleted only)",
            "dexter_ios18": "iOS 18 | 27 rows (deleted only)",
            "felix_ios17": "iOS 17 | 0 rows",
            "hc_ios18_7": "iOS 18.7 | 0 rows",
            "iphone12_ios18": "iOS 18 | 0 rows",
        },
    }
}


import os
import struct
from datetime import datetime, timedelta, timezone

from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)

# Task-step integers sourced from BMPBSiriExecutionEvent and confirmed by parsing
# sample records through the class. Only the observed values are mapped.
TASK_STEP = {0: 'Start', 6: 'Completed'}

# Cocoa / Core Data epoch is 2001-01-01 UTC.
_COCOA_EPOCH = datetime(2001, 1, 1, tzinfo=timezone.utc)

# Pin flat fields so the UUID and code strings are never eagerly decoded as nested
# protobuf, and so field 8 (a fixed64 holding a double) decodes as a float.
TYPESS = {
    '1': {'type': 'str', 'name': ''},     # taskId (UUID)
    '2': {'type': 'int', 'name': ''},     # taskStep
    '3': {'type': 'str', 'name': ''},     # statusReason
    '4': {'type': 'str', 'name': ''},     # slotValue
    '5': {'type': 'str', 'name': ''},     # intentName
    '6': {'type': 'str', 'name': ''},     # appBundleId
    '7': {'type': 'str', 'name': ''},     # interactionId (UUID)
    '8': {'type': 'double', 'name': ''},  # absoluteTimestamp (Cocoa epoch)
}


def _to_str(value):
    """Absent submessages decode as an empty dict, which is not a value."""
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', 'replace')
    if value is None or isinstance(value, (dict, list)):
        return ''
    return str(value)


def _cocoa_dt(value):
    """A Cocoa-epoch double (seconds since 2001-01-01 UTC) as a UTC datetime."""
    if not isinstance(value, (int, float)) or not value:
        return None
    try:
        return _COCOA_EPOCH + timedelta(seconds=value)
    except (OverflowError, OSError, ValueError):
        return None


@artifact_processor
def get_biomeSiriExecution(context):

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
            ts = record.timestamp1.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, TYPESS)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Siri Execution: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                raw_step = protostuff.get('2')
                abs_ts = _cocoa_dt(protostuff.get('8'))

                data_list.append((ts, abs_ts, record.state.name,
                                  TASK_STEP.get(raw_step, ''),
                                  _to_str(raw_step),
                                  _to_str(protostuff.get('5')),
                                  _to_str(protostuff.get('3')),
                                  _to_str(protostuff.get('4')),
                                  _to_str(protostuff.get('6')),
                                  _to_str(protostuff.get('1')),
                                  _to_str(protostuff.get('7')),
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, '', '', '', '', '', '',
                                  '', '', filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Absolute Timestamp', 'datetime'),
                    'SEGB State', 'Task Step', 'Task Step (raw)', 'Intent Name',
                    'Status Reason', 'Slot Value', 'App Bundle ID',
                    ('Task ID', 'hash'), ('Interaction ID', 'hash'), 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
