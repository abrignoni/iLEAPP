__artifacts_v2__ = {
    "get_biomeUserFocusDriving": {
        "name": "Biome - Focus Driving",
        "description": "Records from the UserFocus.DoNotDisturbWhileDriving biome stream: the "
                       "stored starting flag and reason of each record.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field names and numbers come from the class's protoFields in BiomeLibrary.framework, read on macOS 27.2.1 (26B131). That the iOS writer uses the same field numbers was checked only against the data: no written record in the tested files decoded to a field number outside that set. On dexter_ios18 written records that hold only zero bytes decode to no stream field and are skipped and logged (32 Inferred Mode and 2 Sleep Mode records; 12 more Inferred Mode records do not decode at all). Enum names come from the same framework, decoded per data version, and are shown with the stored number beside them. The version is read from an integer in the SEGB record header that the SEGB reader leaves unnamed (the last field of the header in SEGB v1, the second in SEGB v2); that it is the data version was checked only against the data: the values seen are the versions the framework decodes. The framework numbers Inferred Mode origin and mode type from 0 (None, Custom) in data version 1 and inserts 0 Unknown in version 2, and numbers Sleep Mode state from 0 (Off) in version 2 and inserts 0 Unknown in version 3. On the tested images the iOS 15 to iOS 17 Inferred Mode records are version 1 and the iOS 18 and iOS 26 ones version 2; read that way, the Is Start Yes rows hold the same pairs of mode type and origin under both tables (Driving with DNDWD, Home with CoreRoutine, Default with None). A number the version's table does not name, or a version with no table, shows the number only. On the tested iOS 15 and iOS 16 images the streams are named DoNotDisturbWhileDriving, InferredMode and SleepMode, which the framework lists as their legacy names, and are read too. Only records in the written state are reported. Files in the stream's tombstone folder are not read: on the tested images their written records have a layout that is not the stream's (bytes and three integers, plus bytes from iOS 16 and a fixed64 from iOS 18), and what they record is not established. Each tested image has one file in the "
                 "stream's local folder outside tombstone, so SEGB File held one value on every "
                 "row. SEGB Timestamp is the first timestamp of the SEGB record header (SEGB v1) or the creation time of the record's trailer entry (SEGB v2); what it marks was not checked against another record. Fields: 1 starting and 2 reason, named by "
                 "BMUserFocusDoNotDisturbWhileDrivingReasonAsString. Starting was Yes on 199 of "
                 "215 rows of hill_iphone15pro_ios26, 174 of 308 of wilkerson_iphone16_ios26 and "
                 "2,619 of 2,731 of iphone11_ios17, so the counts of Yes and No rows differ on all "
                 "three images. Reason held Vehicular (2) on all 215 rows of "
                 "hill_iphone15pro_ios26; on wilkerson_iphone16_ios26 it held Vehicular (2) or "
                 "CarPlay (3), CarPlay only on rows where Starting is No.",
        "paths": ('*/streams/*/UserFocus.DoNotDisturbWhileDriving/local/*', '*/streams/*/DoNotDisturbWhileDriving/local/*'),
        "output_types": "standard",
        "artifact_icon": "car",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 525 rows",
            "dexter_ios18": "iOS 18.3.2 | 524 rows",
            "felix23_ios16": "iOS 16.5 | 204 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 136 rows",
            "hill_iphone15pro_ios26": "iOS 26 | 215 rows",
            "iphone11_ios17": "iOS 17.3 | 2731 rows",
            "jess_ios15": "iOS 15.0.2 | 142 rows",
            "magnet_ios16": "iOS 16.1.1 | 241 rows",
            "otto_ios17": "iOS 17.5.1 | 36 rows",
            "wilkerson_iphone16_ios26": "iOS 26 | 308 rows",
        },
    },
    "get_biomeUserFocusInferredMode": {
        "name": "Biome - Focus Inferred Mode",
        "description": "Records from the UserFocus.InferredMode biome stream: the time, the "
                       "stored isStart flag, the mode type, the origin and the other fields each "
                       "record stores.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field names and numbers come from the class's protoFields in BiomeLibrary.framework, read on macOS 27.2.1 (26B131). That the iOS writer uses the same field numbers was checked only against the data: no written record in the tested files decoded to a field number outside that set. On dexter_ios18 written records that hold only zero bytes decode to no stream field and are skipped and logged (32 Inferred Mode and 2 Sleep Mode records; 12 more Inferred Mode records do not decode at all). Enum names come from the same framework, decoded per data version, and are shown with the stored number beside them. The version is read from an integer in the SEGB record header that the SEGB reader leaves unnamed (the last field of the header in SEGB v1, the second in SEGB v2); that it is the data version was checked only against the data: the values seen are the versions the framework decodes. The framework numbers Inferred Mode origin and mode type from 0 (None, Custom) in data version 1 and inserts 0 Unknown in version 2, and numbers Sleep Mode state from 0 (Off) in version 2 and inserts 0 Unknown in version 3. On the tested images the iOS 15 to iOS 17 Inferred Mode records are version 1 and the iOS 18 and iOS 26 ones version 2; read that way, the Is Start Yes rows hold the same pairs of mode type and origin under both tables (Driving with DNDWD, Home with CoreRoutine, Default with None). A number the version's table does not name, or a version with no table, shows the number only. On the tested iOS 15 and iOS 16 images the streams are named DoNotDisturbWhileDriving, InferredMode and SleepMode, which the framework lists as their legacy names, and are read too. Only records in the written state are reported. Files in the stream's tombstone folder are not read: on the tested images their written records have a layout that is not the stream's (bytes and three integers, plus bytes from iOS 16 and a fixed64 from iOS 18), and what they record is not established. hill_iphone15pro_ios26 and dexter_ios18 have two files in the local folder outside tombstone (55 and 25 rows on the first); the other tested images have one. Fields: 1 absoluteTimestamp, 2 "
                 "modeIdentifier, 3 origin, 4 originBundleID, 5 isAutomationEnabled, 6 isStart, 7 "
                 "uuid, 8 originAnchorType, 9 uiLocation, 10 confidenceScore, 11 "
                 "serializedTriggers, 12 modeType, 13 shouldSuggestTriggers and 14 userModeName. "
                 "The names are those of BMUserFocusInferredModeOriginAsString and BMUserFocusInferredModeTypeAsString, which take the version 2 numbers. Absolute Timestamp is absoluteTimestamp "
                 "read as seconds since 2001 UTC; read that way it equals the SEGB Timestamp to "
                 "the second on every row of hill_iphone15pro_ios26, wilkerson_iphone16_ios26 and iphone11_ios17 (80, 236 and 376); on abe_ios16 one row differs by under a second. On hill_iphone15pro_ios26 and wilkerson_iphone16_ios26 the Yes and No rows of Is Start are equal in number for each Mode "
                 "Type (40 and 40, 118 and 118); 39 and 117 UUIDs hold a Yes row then a No row "
                 "with the same Mode Type, and one Yes row and one No row on each image have no "
                 "partner by UUID. Origin is None (1) on every row of those images where Is Start "
                 "is No. Serialized Triggers (bytes) gives the length of the stored triggers, "
                 "which are not decoded. Origin Bundle ID and Origin Anchor Type are empty on "
                 "every row of hill_iphone15pro_ios26, wilkerson_iphone16_ios26 and iphone11_ios17, and Mode Identifier and User Mode Name are "
                 "empty on every row of the iOS 26 images. Confidence Score held 0.8, and "
                 "Automation Enabled and Should Suggest Triggers held No, on every row of the "
                 "same three images; UI Location held 1 on every row of hill_iphone15pro_ios26 and wilkerson_iphone16_ios26.",
        "paths": ('*/streams/*/UserFocus.InferredMode/local/*', '*/streams/*/InferredMode/local/*'),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 136 rows",
            "dexter_ios18": "iOS 18.3.2 | 318 rows",
            "felix23_ios16": "iOS 16.5 | 182 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 254 rows",
            "hill_iphone15pro_ios26": "iOS 26 | 80 rows",
            "iphone11_ios17": "iOS 17.3 | 376 rows",
            "jess_ios15": "iOS 15.0.2 | 104 rows",
            "magnet_ios16": "iOS 16.1.1 | 138 rows",
            "otto_ios17": "iOS 17.5.1 | 74 rows",
            "wilkerson_iphone16_ios26": "iOS 26 | 236 rows",
        },
    },
    "get_biomeUserFocusSleepMode": {
        "name": "Biome - Focus Sleep Mode",
        "description": "Records from the UserFocus.SleepMode biome stream: the sleep mode state, "
                       "the change reason and the expected end date each record stores.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field names and numbers come from the class's protoFields in BiomeLibrary.framework, read on macOS 27.2.1 (26B131). That the iOS writer uses the same field numbers was checked only against the data: no written record in the tested files decoded to a field number outside that set. On dexter_ios18 written records that hold only zero bytes decode to no stream field and are skipped and logged (32 Inferred Mode and 2 Sleep Mode records; 12 more Inferred Mode records do not decode at all). Enum names come from the same framework, decoded per data version, and are shown with the stored number beside them. The version is read from an integer in the SEGB record header that the SEGB reader leaves unnamed (the last field of the header in SEGB v1, the second in SEGB v2); that it is the data version was checked only against the data: the values seen are the versions the framework decodes. The framework numbers Inferred Mode origin and mode type from 0 (None, Custom) in data version 1 and inserts 0 Unknown in version 2, and numbers Sleep Mode state from 0 (Off) in version 2 and inserts 0 Unknown in version 3. On the tested images the iOS 15 to iOS 17 Inferred Mode records are version 1 and the iOS 18 and iOS 26 ones version 2; read that way, the Is Start Yes rows hold the same pairs of mode type and origin under both tables (Driving with DNDWD, Home with CoreRoutine, Default with None). A number the version's table does not name, or a version with no table, shows the number only. On the tested iOS 15 and iOS 16 images the streams are named DoNotDisturbWhileDriving, InferredMode and SleepMode, which the framework lists as their legacy names, and are read too. Only records in the written state are reported. Files in the stream's tombstone folder are not read: on the tested images their written records have a layout that is not the stream's (bytes and three integers, plus bytes from iOS 16 and a fixed64 from iOS 18), and what they record is not established. Each tested image has one file in the "
                 "stream's local folder outside tombstone, so SEGB File held one value on every "
                 "row. SEGB Timestamp is the first timestamp of the SEGB record header (SEGB v1) or the creation time of the record's trailer entry (SEGB v2); what it marks was not checked against another record. Fields: 1 state, 2 changeReason and 3 expectedEndDate. The state names are those of BMUserFocusSleepModeStateAsString, which takes the version 3 numbers; the change reason names are those of BMUserFocusSleepModeChangeReasonAsString. Expected End "
                 "Date is expectedEndDate read as seconds since 2001 UTC, which is how the framework returns it: on iphone11_ios17 it falls 7.7 to 8.5 hours after the "
                 "SEGB Timestamp on the 58 rows that hold it, which are the rows with State 1 or "
                 "2. Expected End Date is empty on every row of hill_iphone15pro_ios26 and wilkerson_iphone16_ios26, where State "
                 "held Off (1) and Change Reason held Other (7) on all 4 and 2 rows.",
        "paths": ('*/streams/*/UserFocus.SleepMode/local/*', '*/streams/*/SleepMode/local/*'),
        "output_types": "standard",
        "artifact_icon": "moon",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 95 rows",
            "dexter_ios18": "iOS 18.3.2 | 5 rows",
            "felix23_ios16": "iOS 16.5 | 4 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 6 rows",
            "hill_iphone15pro_ios26": "iOS 26 | 4 rows",
            "iphone11_ios17": "iOS 17.3 | 93 rows",
            "magnet_ios16": "iOS 16.1.1 | 6 rows",
            "otto_ios17": "iOS 17.5.1 | 88 rows",
            "wilkerson_iphone16_ios26": "iOS 26 | 2 rows",
        },
    },
}


import os
import struct
from datetime import datetime, timedelta, timezone

from google.protobuf.message import DecodeError
from scripts import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError)
_EPOCH_2001 = datetime(2001, 1, 1, tzinfo=timezone.utc)
# Field names and numbers from the protoFields of BMUserFocusDoNotDisturbWhileDriving,
# BMUserFocusInferredMode and BMUserFocusSleepMode, read from BiomeLibrary.framework on macOS 27.2.1
# (26B131). Enum names are read the same way, per record data version: one-field records were
# decoded with eventWithData:dataVersion: and each name taken from the event's description. The
# data version is the second integer of the SEGB entry header. InferredMode version 1 numbers
# origin and mode type from 0 (None, Custom) and version 2 inserts 0 Unknown; SleepMode version 2
# numbers state from 0 (Off) and version 3 inserts 0 Unknown.
_DRIVING_REASON_V1 = {0: 'Unknown', 1: 'ManualControlCenter', 2: 'Vehicular', 3: 'CarPlay', 4:
                      'ManualExitFriction', 5: 'ManualBulletin', 6:
                      'ManualVanillaControlCenter'}
_ORIGIN_V1 = {0: 'None', 1: 'CoreMotion', 2: 'CarPlay', 3: 'DNDWD', 4: 'CoreRoutine', 5:
              'Sleep', 6: 'AppLaunch', 7: 'WatchWorkout', 8: 'WFHClassifier', 9: 'Calendar',
              10: 'AnchorModel', 11: 'AppLaunchModel', 12: 'ScreenShare', 13:
              'ScreenRecording', 14: 'GameControllerConnected', 15: 'POI', 16: 'BacklightData'}
_ORIGIN_V2 = {0: 'Unknown', 1: 'None', 2: 'CoreMotion', 3: 'CarPlay', 4: 'DNDWD', 5:
              'CoreRoutine', 6: 'Sleep', 7: 'AppLaunch', 8: 'WatchWorkout', 9: 'WFHClassifier',
              10: 'Calendar', 11: 'AnchorModel', 12: 'AppLaunchModel', 13: 'ScreenShare', 14:
              'ScreenRecording', 15: 'GameControllerConnected', 16: 'POI', 17: 'BacklightData',
              18: 'Perception'}
_MODE_TYPE_V1 = {0: 'Custom', 1: 'Default', 2: 'Home', 3: 'Working', 4: 'Exercising', 5:
                 'Driving', 6: 'Bedtime', 7: 'Gaming', 8: 'Reading', 9: 'Traveling', 10:
                 'Learning', 11: 'Streaming', 12: 'ScreenSharing', 13: 'ClassicDND', 14:
                 'ScreenRecording', 15: 'AirPlayMirroring', 16: 'Mindfulness'}
_MODE_TYPE_V2 = {0: 'Unknown', 1: 'Custom', 2: 'Default', 3: 'Home', 4: 'Working', 5:
                 'Exercising', 6: 'Driving', 7: 'Bedtime', 8: 'Gaming', 9: 'Reading', 10:
                 'Traveling', 11: 'Learning', 12: 'Streaming', 13: 'ScreenSharing', 14:
                 'ClassicDND', 15: 'ScreenRecording', 16: 'AirPlayMirroring', 17:
                 'Mindfulness', 18: 'ReduceInterruptions'}
_SLEEP_STATE_V2 = {0: 'Off', 1: 'WindDown', 2: 'Bedtime'}
_SLEEP_STATE_V3 = {0: 'Unknown', 1: 'Off', 2: 'WindDown', 3: 'Bedtime'}
_SLEEP_REASON_V2 = {0: 'Unknown', 1: 'UserRequested', 2: 'Expected', 3: 'CloudSynced', 4:
                    'CloudSyncedUserRequested', 5: 'NanoSynced', 6: 'TurnedOffDND', 7: 'Other',
                    8: 'Automation', 9: 'CloudSyncedAutomation'}
_SLEEP_REASON_V3 = {0: 'Unknown', 1: 'UserRequested', 2: 'Expected', 3: 'CloudSynced', 4:
                    'CloudSyncedUserRequested', 5: 'NanoSynced', 6: 'TurnedOffDND', 7: 'Other',
                    8: 'Automation', 9: 'CloudSyncedAutomation'}

_DRIVING_REASON = {1: _DRIVING_REASON_V1}
_ORIGIN = {1: _ORIGIN_V1, 2: _ORIGIN_V2}
_MODE_TYPE = {1: _MODE_TYPE_V1, 2: _MODE_TYPE_V2}
_SLEEP_STATE = {2: _SLEEP_STATE_V2, 3: _SLEEP_STATE_V3}
_SLEEP_REASON = {2: _SLEEP_REASON_V2, 3: _SLEEP_REASON_V3}


def _named(names_by_version, value, version):
    '''Name and stored number, from the name table of the record's data version.

    A version with no table, or a number its table does not name, shows the number only.
    '''
    if not isinstance(value, int):
        return ''
    names = names_by_version.get(version, {})
    return f'{names[value]} ({value})' if value in names else str(value)


def _flag(value):
    if value is None:
        return ''
    return 'Yes' if value else 'No'


def _double(value):
    if isinstance(value, float):
        return value
    if not isinstance(value, int):
        return None
    return struct.unpack('<d', struct.pack('<Q', value & 0xFFFFFFFFFFFFFFFF))[0]


def _cocoa(value):
    seconds = _double(value)
    if not seconds:
        return ''
    try:
        return _EPOCH_2001 + timedelta(seconds=seconds)
    except OverflowError:
        return ''


def _text(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    return '' if value is None or isinstance(value, (dict, list)) else str(value)


def _records(context, label, read):
    '''(record, decoded message, file name) for every written record of the matched files.

    Every file read is added to the set read, so the source list names only those.
    '''
    for found in sorted(str(path) for path in context.get_files_found()):
        name = os.path.basename(found)
        if name.startswith('.') or not os.path.isfile(found):
            continue
        if '/tombstone/' in context.get_relative_path(found).replace('\\', '/'):
            continue
        read.add(found)
        for record in read_segb_file(found):
            if record.state != EntryState.Written:
                continue
            try:
                message, _ = blackboxprotobuf.decode_message(record.data)
            except _DECODE_ERRORS as error:
                logfunc(f'{label}: could not decode record at offset {record.data_start_offset} '
                        f'in {name}: {error}')
                continue
            if not any(key != '0' for key in message):
                # An all-zero payload decodes to field 0 only, which no stream defines.
                logfunc(f'{label}: skipped record at offset {record.data_start_offset} in {name}: '
                        'no stream field')
                continue
            yield found, record, message, name


def _version(record):
    return getattr(record, '_unknown_value', None)


def _sources(read):
    return '\n'.join(sorted(read))


@artifact_processor
def get_biomeUserFocusDriving(context):
    data_list, read = [], set()
    for _, record, message, name in _records(context, 'Focus Driving', read):
        data_list.append((record.timestamp1.replace(tzinfo=timezone.utc), _flag(message.get('1')),
                          _named(_DRIVING_REASON, message.get('2'), _version(record)), name,
                          record.data_start_offset))
    headers = (('SEGB Timestamp', 'datetime'), 'Starting', 'Reason', 'SEGB File', 'Offset')
    return headers, data_list, _sources(read)


@artifact_processor
def get_biomeUserFocusInferredMode(context):
    data_list, read = [], set()
    for _, record, message, name in _records(context, 'Focus Inferred Mode', read):
        triggers = message.get('11')
        confidence = _double(message.get('10'))
        data_list.append((
            _cocoa(message.get('1')),
            record.timestamp1.replace(tzinfo=timezone.utc),
            _flag(message.get('6')),
            _named(_MODE_TYPE, message.get('12'), _version(record)),
            _named(_ORIGIN, message.get('3'), _version(record)),
            _text(message.get('4')),
            _text(message.get('2')),
            _text(message.get('14')),
            '' if confidence is None else confidence,
            _flag(message.get('5')),
            '' if message.get('9') is None else message.get('9'),
            _flag(message.get('13')),
            _text(message.get('8')),
            len(triggers) if isinstance(triggers, bytes) else '',
            _text(message.get('7')),
            name,
            record.data_start_offset,
        ))
    headers = (('Absolute Timestamp', 'datetime'), ('SEGB Timestamp', 'datetime'), 'Is Start',
               'Mode Type', 'Origin', 'Origin Bundle ID', 'Mode Identifier', 'User Mode Name',
               'Confidence Score', 'Automation Enabled', 'UI Location (as stored)',
               'Should Suggest Triggers', 'Origin Anchor Type', 'Serialized Triggers (bytes)',
               'UUID', 'SEGB File', 'Offset')
    return headers, data_list, _sources(read)


@artifact_processor
def get_biomeUserFocusSleepMode(context):
    data_list, read = [], set()
    for _, record, message, name in _records(context, 'Focus Sleep Mode', read):
        data_list.append((record.timestamp1.replace(tzinfo=timezone.utc),
                          _cocoa(message.get('3')), _named(_SLEEP_STATE, message.get('1'), _version(record)),
                          _named(_SLEEP_REASON, message.get('2'), _version(record)), name,
                          record.data_start_offset))
    headers = (('SEGB Timestamp', 'datetime'), ('Expected End Date', 'datetime'), 'State',
               'Change Reason', 'SEGB File', 'Offset')
    return headers, data_list, _sources(read)
