__artifacts_v2__ = {
    "get_biomeSiriExecution": {
        "name": "Biome - Siri Execution",
        "description": "Parses Siri execution events from the Siri.Execution biome stream, and the "
                       "SiriExecution stream of the same records on iOS 16. A written record can "
                       "carry a task step, an intent name, a status reason, a slot value, an app "
                       "bundle id, a task id, an interaction id, a root interaction id and an "
                       "absolute timestamp. Task Step names follow the record's data version (see "
                       "notes).",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-13",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field names come from the BMPBSiriExecutionEvent class in BiomeStreams.framework "
                 "and the BMSiriExecution class in BiomeLibrary.framework, read on macOS 27.2.1 "
                 "(26B131); BMSiriExecution names the SiriExecution stream as a legacy name of "
                 "Siri.Execution. Task Step names depend on the integer shown in Data Version. In "
                 "SEGB v2 files it is the second integer of the entry header; the SEGB reader does "
                 "not name it. It is read here as the Biome data version because the values seen "
                 "(2 and 3) are the versions BMSiriExecution accepts. BMSiriExecution reads data "
                 "version 2 with 0 = Start, 1 = Authentication, 6 = Completed (the same list as "
                 "BMPBSiriExecutionEvent), and data version 3 with 0 = Unknown, 1 = Start, "
                 "6 = Failed, 7 = Completed: every version 2 step moves up by one. The iOS builds "
                 "of these classes were not read. The written records on otto_ios17 (iOS 17.5.1) "
                 "are version 2. The written records on hill_iphone15pro_ios26 and "
                 "wilkerson_iphone16_ios26 are version 3. A record of any other version keeps its "
                 "integer in Task Step (raw) with Task Step blank. No written SEGB v1 record was "
                 "tested. On the tested written records the task id was a UUID-format string. The "
                 "interaction id was a UUID-format string on the three otto_ios17 records, empty "
                 "on all 17 hill_iphone15pro_ios26 records and empty on 36 of the 41 "
                 "wilkerson_iphone16_ios26 records. Root Interaction ID is field 9 "
                 "(rootInteractionID); it held a value on 2 of the 41 wilkerson_iphone16_ios26 "
                 "written records and on none of the others. The abe_ios16 SiriExecution "
                 "records are version 2. The Absolute Timestamp is a Cocoa "
                 "epoch (seconds since 2001-01-01 UTC); on the three otto_ios17 written records it "
                 "matched the SEGB record timestamp within about 14 ms. This artifact does not "
                 "decode the payload of deleted records; a Deleted row has a timestamp, a state "
                 "and a file location but no fields. On the otto_ios17 written records App Bundle "
                 "ID held 'none' and Slot Value held 'none' or 'not_applicable'; both are reported "
                 "as stored. On the 17 hill_iphone15pro_ios26 written records Status Reason, Slot "
                 "Value, App Bundle ID and Interaction ID were empty strings. Filename is the SEGB "
                 "segment file name, and files under the tombstone folder are not read. On the "
                 "tested iOS 17 and iOS 26 images the stream was under streams/restricted; on "
                 "abe_ios16 and felix23_ios16 the SiriExecution stream was under streams/public.",
        "paths": ('*/streams/*/Siri.Execution/local/*', '*/streams/*/SiriExecution/local/*'),
        "output_types": "standard",
        "artifact_icon": "mic",
        "sample_data": {
            "otto_ios17": "iOS 17 | 49 rows (3 written, 46 deleted)",
            "hill_iphone15pro_ios26": "iOS 26 | 74 rows (17 written, 57 deleted)",
            "abe_ios16": "iOS 16.5 | 67 rows (15 written, 52 deleted)",
            "felix23_ios16": "iOS 16.5 | 35 rows (deleted only)",
            "falken_ios26": "iOS 26 | 2 rows (deleted only)",
            "wilkerson_iphone16_ios26": "iOS 26 | 163 rows (41 written, 122 deleted)",
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

# Task-step names by record data version (the second int of the SEGB entry header).
# Read from BiomeLibrary.framework BMSiriExecution on macOS 27.2.1 (26B131): data
# version 2 numbers the steps from 0 = Start (the same list as BiomeStreams'
# BMPBSiriExecutionEvent), and data version 3 inserts 0 = Unknown, so every later
# step moves up by one. Other versions get no name.
_TASK_STEPS_V2 = (
    'Start', 'Authentication', 'Wait', 'Resume', 'Canceled', 'Failed', 'Completed', 'None',
    'HandoffToCompanion', 'SiriExecutionTaskStepTypeSaved', 'UserAuthenticated',
    'ResolveConfirmStart', 'ResolveConfirmFinish', 'HandleIntentStart',
    'HandleIntentFinish', 'Disambiguation', 'PromptForData', 'Confirmation',
    'TapToEditCorrection', 'FetchData', 'ResolveApp', 'SuggestApp', 'DisambiguateApp',
    'ConfirmApp', 'SearchCompleted', 'Generic', 'PromptUnlock', 'ShowInterstitial',
    'ContactResolution', 'DeviceSearch', 'IntentAutoConfirm', 'CheckUnsetRelationship',
    'ConfirmIntent', 'ModifySlotValue', 'ReadingStart', 'RememberUnsetRelationship',
    'ResolveSlotAuthenticationRequired', 'ResolveSlotConfirm', 'ConfirmationAccepted',
    'ConfirmationRejected', 'ResolveSlotDisambiguate', 'DisambiguationResponseReceived',
    'DisambiguationManualOverride', 'ResolveSlotNeedsValue', 'ResolveSlotNotRequired',
    'ResolveSlotSuccess', 'ResolveSlotUnsupported', 'SetUnsetRelationship',
    'SubtaskCompleted', 'TermConditionCheck', 'DirectExecution',
    'SearchKnowledgeFromSports', 'SearchLocalEventsFromSports', 'SearchWebFromSports',
    'IntentReformation', 'DialogCompleted', 'DialogFailed', 'SportsProbeStarted',
    'SportsProbeNoResultsOrUnsupported', 'SportsProbeFailed', 'SportsProbeSuccessful',
    'Preprocess', 'Render', 'FlowReplan', 'SendViaSnippet', 'ContentChangedViaSnippet',
    'GateKeeperNewCall', 'GateKeeperNewMessage', 'GateKeeperReadMessage', 'Skip', 'Stop',
    'Reply', 'AudioReply', 'ReadAgain', 'ModifyMessage', 'ReplyWithCall', 'TCCAccepted',
    'TCCDeclined', 'GetCallBackgroundState', 'SearchFailed', 'Fallback', 'PartialFailure',
    'Correction', 'AutoSend', 'AutoSendStarted', 'CheckSharingPolicy',
    'PostNotificationToCompanion', 'ExecuteOnRemote', 'NeedsServerExecution',
    'CheckPersonalDomainSetting', 'CheckPersonalDomainSettingResponse', 'RequestIdentity',
    'ConfirmIdentity', 'CheckCompanionCompatibility',
)
TASK_STEP_BY_VERSION = {
    2: dict(enumerate(_TASK_STEPS_V2)),
    3: dict(enumerate(('Unknown',) + _TASK_STEPS_V2)),
}

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
    '9': {'type': 'str', 'name': ''},     # rootInteractionID
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
                version = getattr(record, '_unknown_value', None)
                step_name = TASK_STEP_BY_VERSION.get(version, {}).get(raw_step, '')
                abs_ts = _cocoa_dt(protostuff.get('8'))

                data_list.append((ts, abs_ts, record.state.name,
                                  step_name,
                                  _to_str(raw_step),
                                  _to_str(version),
                                  _to_str(protostuff.get('5')),
                                  _to_str(protostuff.get('3')),
                                  _to_str(protostuff.get('4')),
                                  _to_str(protostuff.get('6')),
                                  _to_str(protostuff.get('1')),
                                  _to_str(protostuff.get('7')),
                                  _to_str(protostuff.get('9')),
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, '', '', '', '', '', '', '',
                                  '', '', '', filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Absolute Timestamp', 'datetime'),
                    'SEGB State', 'Task Step', 'Task Step (raw)', 'Data Version', 'Intent Name',
                    'Status Reason', 'Slot Value', 'App Bundle ID',
                    ('Task ID', 'hash'), ('Interaction ID', 'hash'), ('Root Interaction ID', 'hash'),
                    'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
