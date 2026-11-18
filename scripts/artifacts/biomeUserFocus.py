__artifacts_v2__ = {
    "get_biomeUserFocusDriving": {
        "name": "Biome - Focus Driving",
        "description": "Records from the UserFocus.DoNotDisturbWhileDriving biome stream: "
                       "whether each one starts or ends the Driving focus, and the reason it stores.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field names and numbers come from the class's protoFields in "
                 "BiomeLibrary.framework, read on macOS 27.2.1 (26B131), and enum names from the "
                 "matching AsString functions there, with the stored number kept beside each name. "
                 "That the iOS writer uses the same schema was checked only against the data: "
                 "every written record decoded to those fields. Records the SEGB file marks "
                 "deleted, and the stream's tombstone folder, are not read. Each tested image has "
                 "one file in the stream's local folder outside tombstone, so SEGB File held one "
                 "value on every row. Fields: 1 starting and 2 reason, named by "
                 "BMUserFocusDoNotDisturbWhileDrivingReasonAsString. SEGB Timestamp is the SEGB "
                 "record time; what it marks was not checked against another record. Starting was "
                 "Yes on 199 of 215 rows of hill_iphone15pro_ios26, 174 of 308 of "
                 "wilkerson_iphone16_ios26 and 2,619 of 2,731 of iphone11_ios17, so starts and "
                 "ends do not pair one to one. Reason held Vehicular (2) on all 215 rows of "
                 "hill_iphone15pro_ios26; on the other two images it held Vehicular (2) or CarPlay "
                 "(3), CarPlay only on rows where Starting is No.",
        "paths": ('*/streams/*/UserFocus.DoNotDisturbWhileDriving/local/*',),
        "output_types": "standard",
        "artifact_icon": "car",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 215 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 308 rows",
            "iphone11_ios17": "iOS 17.3 | 2731 rows",
        },
    },
    "get_biomeUserFocusInferredMode": {
        "name": "Biome - Focus Inferred Mode",
        "description": "Records from the UserFocus.InferredMode biome stream: the time, whether "
                       "each one starts or ends a mode, the mode type, the origin and the other "
                       "fields each record stores.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field names and numbers come from the class's protoFields in "
                 "BiomeLibrary.framework, read on macOS 27.2.1 (26B131), and enum names from the "
                 "matching AsString functions there, with the stored number kept beside each name. "
                 "That the iOS writer uses the same schema was checked only against the data: "
                 "every written record decoded to those fields. Records the SEGB file marks "
                 "deleted, and the stream's tombstone folder, are not read. Each tested image has "
                 "one file in the stream's local folder outside tombstone, so SEGB File held one "
                 "value on every row. Fields: 1 absoluteTimestamp, 2 modeIdentifier, 3 origin, 4 "
                 "originBundleID, 5 isAutomationEnabled, 6 isStart, 7 uuid, 8 originAnchorType, 9 "
                 "uiLocation, 10 confidenceScore, 11 serializedTriggers, 12 modeType, 13 "
                 "shouldSuggestTriggers and 14 userModeName. Origin is named by "
                 "BMUserFocusInferredModeOriginAsString and Mode Type by "
                 "BMUserFocusInferredModeTypeAsString. Absolute Timestamp is absoluteTimestamp "
                 "read as seconds since 2001 UTC; read that way it equals the SEGB Timestamp to "
                 "the second on every row of the three tested images (80, 236 and 376). On the two "
                 "iOS 26 images every start row has an end row with the same Mode Type, and the "
                 "end row's Origin is None (1). On iphone11_ios17 (iOS 17.3) the Origin values "
                 "pair with Mode Types in ways that do not fit their names (Exercising with "
                 "CarPlay, Working with GameControllerConnected), so the origin numbering on iOS "
                 "17 may differ from the macOS 27 framework; that was not established. Serialized "
                 "Triggers (bytes) gives the length of the stored triggers, which are not decoded. "
                 "Origin Bundle ID and Origin Anchor Type are empty on every row of the three "
                 "tested images, and Mode Identifier and User Mode Name are empty on every row of "
                 "the two iOS 26 images. Confidence Score held 0.8, and Automation Enabled and "
                 "Should Suggest Triggers held No, on every row of the three tested images; UI "
                 "Location held 1 on every row of the two iOS 26 images.",
        "paths": ('*/streams/*/UserFocus.InferredMode/local/*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 80 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 236 rows",
            "iphone11_ios17": "iOS 17.3 | 376 rows",
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
        "notes": "Field names and numbers come from the class's protoFields in "
                 "BiomeLibrary.framework, read on macOS 27.2.1 (26B131), and enum names from the "
                 "matching AsString functions there, with the stored number kept beside each name. "
                 "That the iOS writer uses the same schema was checked only against the data: "
                 "every written record decoded to those fields. Records the SEGB file marks "
                 "deleted, and the stream's tombstone folder, are not read. Each tested image has "
                 "one file in the stream's local folder outside tombstone, so SEGB File held one "
                 "value on every row. Fields: 1 state, named by BMUserFocusSleepModeStateAsString, "
                 "2 changeReason, named by BMUserFocusSleepModeChangeReasonAsString, and 3 "
                 "expectedEndDate. Expected End Date is expectedEndDate read as seconds since 2001 "
                 "UTC; that reading was checked only against the data: on iphone11_ios17 it falls "
                 "7.7 to 8.5 hours after the SEGB Timestamp on the 58 rows that hold it. Expected "
                 "End Date is empty on every row of the two iOS 26 images, where State held Off "
                 "(1) and Change Reason held Other (7) on all 4 and 2 rows.",
        "paths": ('*/streams/*/UserFocus.SleepMode/local/*',),
        "output_types": "standard",
        "artifact_icon": "moon",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 4 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 93 rows",
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
# BMUserFocusInferredMode and BMUserFocusSleepMode, and enum names from
# BMUserFocusDoNotDisturbWhileDrivingReasonAsString, BMUserFocusInferredModeOriginAsString,
# BMUserFocusInferredModeTypeAsString, BMUserFocusSleepModeStateAsString and
# BMUserFocusSleepModeChangeReasonAsString, read from BiomeLibrary.framework on macOS 27.2.1
# (26B131).
_DRIVING_REASON = {0: 'Unknown', 1: 'ManualControlCenter', 2: 'Vehicular', 3: 'CarPlay',
                   4: 'ManualExitFriction', 5: 'ManualBulletin', 6: 'ManualVanillaControlCenter'}
_ORIGIN = {0: 'Unknown', 1: 'None', 2: 'CoreMotion', 3: 'CarPlay', 4: 'DNDWD', 5: 'CoreRoutine',
           6: 'Sleep', 7: 'AppLaunch', 8: 'WatchWorkout', 9: 'WFHClassifier', 10: 'Calendar',
           11: 'AnchorModel', 12: 'AppLaunchModel', 13: 'ScreenShare', 14: 'ScreenRecording',
           15: 'GameControllerConnected', 16: 'POI', 17: 'BacklightData', 18: 'Perception'}
_MODE_TYPE = {0: 'Unknown', 1: 'Custom', 2: 'Default', 3: 'Home', 4: 'Working', 5: 'Exercising',
              6: 'Driving', 7: 'Bedtime', 8: 'Gaming', 9: 'Reading', 10: 'Traveling',
              11: 'Learning', 12: 'Streaming', 13: 'ScreenSharing', 14: 'ClassicDND',
              15: 'ScreenRecording', 16: 'AirPlayMirroring', 17: 'Mindfulness',
              18: 'ReduceInterruptions'}
_SLEEP_STATE = {0: 'Unknown', 1: 'Off', 2: 'WindDown', 3: 'Bedtime'}
_SLEEP_REASON = {0: 'Unknown', 1: 'UserRequested', 2: 'Expected', 3: 'CloudSynced',
                 4: 'CloudSyncedUserRequested', 5: 'NanoSynced', 6: 'TurnedOffDND', 7: 'Other',
                 8: 'Automation', 9: 'CloudSyncedAutomation'}


def _named(names, value):
    if not isinstance(value, int):
        return ''
    return f'{names[value]} ({value})' if value in names else f'Unknown value ({value})'


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


def _records(context, label):
    '''(record, decoded message, file name) for every written record of the matched files.'''
    for found in sorted(str(path) for path in context.get_files_found()):
        name = os.path.basename(found)
        if name.startswith('.') or not os.path.isfile(found):
            continue
        if '/tombstone/' in context.get_relative_path(found).replace('\\', '/'):
            continue
        for record in read_segb_file(found):
            if record.state != EntryState.Written:
                continue
            try:
                message, _ = blackboxprotobuf.decode_message(record.data)
            except _DECODE_ERRORS as error:
                logfunc(f'{label}: could not decode record at offset {record.data_start_offset} '
                        f'in {name}: {error}')
                continue
            yield found, record, message, name


def _sources(context):
    return '\n'.join(sorted({os.path.dirname(str(path)) for path in context.get_files_found()
                             if os.path.isfile(str(path))}))


@artifact_processor
def get_biomeUserFocusDriving(context):
    data_list = []
    for _, record, message, name in _records(context, 'Focus Driving'):
        data_list.append((record.timestamp1.replace(tzinfo=timezone.utc), _flag(message.get('1')),
                          _named(_DRIVING_REASON, message.get('2')), name,
                          record.data_start_offset))
    headers = (('SEGB Timestamp', 'datetime'), 'Starting', 'Reason', 'SEGB File', 'Offset')
    return headers, data_list, _sources(context)


@artifact_processor
def get_biomeUserFocusInferredMode(context):
    data_list = []
    for _, record, message, name in _records(context, 'Focus Inferred Mode'):
        triggers = message.get('11')
        confidence = _double(message.get('10'))
        data_list.append((
            _cocoa(message.get('1')),
            record.timestamp1.replace(tzinfo=timezone.utc),
            _flag(message.get('6')),
            _named(_MODE_TYPE, message.get('12')),
            _named(_ORIGIN, message.get('3')),
            _text(message.get('4')),
            _text(message.get('2')),
            _text(message.get('14')),
            '' if confidence is None else confidence,
            _flag(message.get('5')),
            '' if message.get('9') is None else message.get('9'),
            _flag(message.get('13')),
            _text(message.get('8')),
            len(triggers) if isinstance(triggers, (bytes, dict)) else '',
            _text(message.get('7')),
            name,
            record.data_start_offset,
        ))
    headers = (('Absolute Timestamp', 'datetime'), ('SEGB Timestamp', 'datetime'), 'Is Start',
               'Mode Type', 'Origin', 'Origin Bundle ID', 'Mode Identifier', 'User Mode Name',
               'Confidence Score', 'Automation Enabled', 'UI Location (as stored)',
               'Should Suggest Triggers', 'Origin Anchor Type', 'Serialized Triggers (bytes)',
               'UUID', 'SEGB File', 'Offset')
    return headers, data_list, _sources(context)


@artifact_processor
def get_biomeUserFocusSleepMode(context):
    data_list = []
    for _, record, message, name in _records(context, 'Focus Sleep Mode'):
        data_list.append((record.timestamp1.replace(tzinfo=timezone.utc),
                          _cocoa(message.get('3')), _named(_SLEEP_STATE, message.get('1')),
                          _named(_SLEEP_REASON, message.get('2')), name,
                          record.data_start_offset))
    headers = (('SEGB Timestamp', 'datetime'), ('Expected End Date', 'datetime'), 'State',
               'Change Reason', 'SEGB File', 'Offset')
    return headers, data_list, _sources(context)
