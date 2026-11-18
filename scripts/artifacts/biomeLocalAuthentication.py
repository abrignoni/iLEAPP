__artifacts_v2__ = {
    "get_biomeLocalAuthenticationEvaluations": {
        "name": "Biome - Local Authentication Evaluations",
        "description": "Authentication evaluation records from the "
                       "LocalAuthentication.Interactive.Evaluations biome stream: the policy and "
                       "result, whether biometry and passcode were available, started and "
                       "succeeded, and the ratchet state each record stores.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "One row per written record of the LocalAuthentication.Interactive.Evaluations "
                 "stream. Field names and numbers come from BMLocalAuthenticationEvaluations and "
                 "BMLocalAuthenticationEvaluationsMechanism protoFields in BiomeLibrary.framework, "
                 "read on macOS 27.2.1 (26B131): 1 policy, 2 result, 3 biometry, 4 passcode, 5 "
                 "ratchetState and 7 ratchetArmingState, and within biometry and passcode 1 "
                 "available, 2 started, 3 success, 4 lockout and 5 generation. Ratchet State and "
                 "Ratchet Arming State names come from "
                 "BMLocalAuthenticationEvaluationsRatchetStateAsString and "
                 "BMLocalAuthenticationEvaluationsRatchetArmingStateAsString in the same "
                 "framework, with the stored number kept beside the name. That the iOS writer uses "
                 "the same schema was not checked beyond the data: every written record decoded to "
                 "those fields. Policy and Result are reported as stored, as the framework exports "
                 "no names for them: Policy held 0, 1, 2, 1007 and 1028 on hill_iphone15pro_ios26 "
                 "and 0, 2, 1004, 1026 and 1028 on wilkerson_iphone16_ios26, and Result held 0 or "
                 "-9 on every row. The record holds no name of the app that asked for the "
                 "evaluation. SEGB Timestamp is the SEGB record time; what it marks was not "
                 "checked against another record. On the tested images Biometry Available, "
                 "Passcode Available, Biometry Lockout and Passcode Lockout held one value on "
                 "every row (Yes, Yes, No and No), Biometry Generation and Passcode Generation "
                 "held one value on every row of each image, and Passcode Started and Passcode "
                 "Success are identical on every row. Ratchet State held DisabledByConfiguration "
                 "(7) on all 19 rows of hill_iphone15pro_ios26 and Enabled (1) on all 9 rows of "
                 "wilkerson_iphone16_ios26, and Ratchet Arming State held NotStarted (1) on every "
                 "row of hill_iphone15pro_ios26. What a ratchet state means for the device is not "
                 "established here. Each tested image has one file in the stream's local folder, "
                 "so SEGB File held one value on every row. Records the SEGB file marks deleted "
                 "are not listed and their payloads are not decoded: 39 on hill_iphone15pro_ios26 "
                 "and 152 on wilkerson_iphone16_ios26. The LocalAuthentication.Interactive.Dialogs "
                 "stream, which the framework defines with a bundle ID field, was not present on "
                 "the tested images and is not read.",
        "paths": ('*/streams/*/LocalAuthentication.Interactive.Evaluations/local/*',),
        "output_types": "standard",
        "artifact_icon": "shield-lock",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 19 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 9 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows, no stream file",
        },
    }
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
# Field names and numbers from BMLocalAuthenticationEvaluations and
# BMLocalAuthenticationEvaluationsMechanism protoFields, and state names from
# BMLocalAuthenticationEvaluationsRatchetStateAsString and
# BMLocalAuthenticationEvaluationsRatchetArmingStateAsString, read from BiomeLibrary.framework
# on macOS 27.2.1 (26B131).
_RATCHET = {0: 'Unknown', 1: 'Enabled', 2: 'EnabledStrictMode', 3: 'DisabledIneligibleDevice',
            4: 'DisabledNoBiometry', 5: 'DisabledNoPasscode', 6: 'DisabledRatchetCollapsed',
            7: 'DisabledByConfiguration', 8: 'DisabledForOtherReason'}
_ARMING = {0: 'Unknown', 1: 'NotStarted', 2: 'WaitingForCoolOff',
           3: 'WaitingForSecondAuthentication', 4: 'Ready', 5: 'Collapsed'}
_MECHANISM = (('1', 'Available'), ('2', 'Started'), ('3', 'Success'), ('4', 'Lockout'))


def _named(names, value):
    if not isinstance(value, int):
        return ''
    return f'{names[value]} ({value})' if value in names else f'Unknown value ({value})'


def _flag(value):
    if value is None:
        return ''
    return 'Yes' if value else 'No'


def _mechanism(message, number):
    mechanism = message.get(number)
    if not isinstance(mechanism, dict):
        return ('',) * (len(_MECHANISM) + 1)
    return tuple(_flag(mechanism.get(key)) for key, _ in _MECHANISM) + (
        '' if mechanism.get('5') is None else mechanism.get('5'),)


@artifact_processor
def get_biomeLocalAuthenticationEvaluations(context):
    data_list, source_dirs = [], set()
    for found in sorted(str(path) for path in context.get_files_found()):
        name = os.path.basename(found)
        if name.startswith('.') or not os.path.isfile(found):
            continue
        if '/tombstone/' in context.get_relative_path(found).replace('\\', '/'):
            continue
        source_dirs.add(os.path.dirname(found))
        for record in read_segb_file(found):
            if record.state != EntryState.Written:
                continue
            try:
                message, _ = blackboxprotobuf.decode_message(record.data)
            except _DECODE_ERRORS as error:
                logfunc(f'Local Authentication: could not decode record at offset '
                        f'{record.data_start_offset} in {name}: {error}')
                continue
            data_list.append((
                record.timestamp1.replace(tzinfo=timezone.utc),
                '' if message.get('1') is None else message.get('1'),
                '' if message.get('2') is None else message.get('2'),
                *_mechanism(message, '3'),
                *_mechanism(message, '4'),
                _named(_RATCHET, message.get('5')),
                _named(_ARMING, message.get('7')),
                name,
                record.data_start_offset,
            ))
    data_headers = (
        ('SEGB Timestamp', 'datetime'), 'Policy (as stored)', 'Result (as stored)',
        'Biometry Available', 'Biometry Started', 'Biometry Success', 'Biometry Lockout',
        'Biometry Generation (as stored)', 'Passcode Available', 'Passcode Started',
        'Passcode Success', 'Passcode Lockout', 'Passcode Generation (as stored)',
        'Ratchet State', 'Ratchet Arming State', 'SEGB File', 'Offset')
    return data_headers, data_list, '\n'.join(sorted(source_dirs))
