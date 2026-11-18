"""Apple Intelligence biome streams.

The four AssetDeliveryLog streams share one event message (field 1: date, type, useCase,
resource and asset identifiers, errors, build and subscription fields) and add a stream-specific
state message in field 2. Safety Overrides is a flat message. Names read on macOS 27.2.1 (26B131) by decoding
synthetic records with each IntelligencePlatformLibrary event class that BiomeLibrary names.
"""
__artifacts_v2__ = {
    "get_biomeAppleIntelligenceAvailability": {
        "name": "Biome - Apple Intelligence Availability",
        "description": "Parses records from the AppleIntelligence.Availability biome "
                       "stream: the isDeviceEligible value of the Apple Intelligence and "
                       "diffusion use cases, the isAppleIntelligenceToggleEnabled value, and "
                       "the languages list. What sets these values is not established.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field names are those of the BMAppleIntelligenceAvailability class, read from "
                 "BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was "
                 "read. Apple Intelligence Is Device Eligible (field 1.1), Diffusion Is Device "
                 "Eligible (field 2.1) and Apple Intelligence Toggle Enabled (field 3) are true or "
                 "false values; they were reported before as State 1 (raw), State 2 (raw) and "
                 "State 3 (raw). Languages is a list, joined with semicolons; it was reported "
                 "before as Language, which was empty when a record held more than one. On the "
                 "tested images (6 images, 319 written rows) both Is Device Eligible columns held "
                 "True on 104 rows and False on 215, Apple Intelligence Toggle Enabled held True "
                 "on every written row, and 2 rows of iphone12_ios18 held two languages. The two Is Device "
                 "Eligible columns held the same value on every written row, and each image held "
                 "one value in them: True on hill_iphone15pro_ios26 (38 rows) and "
                 "wilkerson_iphone16_ios26 (66 rows), where all three columns are identical, and "
                 "False on the other four. Deleted rows are not decoded, so these columns are "
                 "empty on them.",
        "paths": ('*/streams/*/AppleIntelligence.Availability/local/*',),
        "output_types": "standard",
        "artifact_icon": "cpu",
        "sample_data": {
            "hc_ios18_7": "478 rows",
            "hc_ios26": "26.5.2 | 41 rows",
            "iphone12_ios18": "64 rows",
        },
    },
    "get_biomeAIAssetAvailability": {
        "name": "Biome - Apple Intelligence Asset Availability",
        "description": ("Parses records from the AppleIntelligence.Reporting.AssetDeliveryLog.Availability "
                       "biome stream: the event date and type, the use case and its parameters, asset "
                       "identifiers, build version and the availability status."),
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field and value names come from the stream's event class, an IntelligencePlatformLibrary EventWrapper type that BiomeLibrary.framework names for this stream, read on macOS 27.2.1 (26B131). No iOS copy was read. The stream's event class is a Swift type with no protoFields, so the "
                 "names were read by decoding synthetic records with the class's "
                 "eventWithData:dataVersion: and reading its json output. On the tested images every "
                 "written record decoded to field numbers that the class names. "
                 "Event Date is the event's date field, read as Unix seconds (reported before as Event Timestamp). The class does not state the epoch. On the tested images every written record's value, read this way, fell within one hour before its SEGB timestamp, and all but 6 within one second. Event Type is the event type (Unknown, Start, End or Impulse), reported before as Status (raw). Use Case ID, Use Case Parameters (name="
                 "value pairs), Locale and Country Code are the event's useCase fields; Use Case ID "
                 "was reported before as Feature or Client, and its parameter as Attribute and Attribute Value (empty before when a record held more than one; no tested record did). Resource Specifiers and Asset Set Identifiers are lists, joined "
                 "with commas; Asset Set Identifiers was reported before as Requesting Client. Errors joins each error's domain, errorCode and description (descriptionWithoutUnderlying when description is empty); the error's category, additionalUserInfo and underlying errors are not reported. The class also names useCase.mode, a number with no value names, which is not reported, and timeOfLastSoftwareUpdate, which no tested record held. Build Version, Subscription Name, "
                 "Subscriber Name and User Identifier were reported before as OS Build, Asset ID, "
                 "Asset Category and User ID. The stream's own state message (field 2) was printed "
                 "raw as Result (raw); it is now named: Status is availabilityChangeEventState.info.status (Unknown, Available, Restricted, Unavailable), with Reasons (raw) its reasons integer. The class prints it as a number, and what the values mean is not established. Deleted rows are not decoded. "
                 "On the tested images Resource Specifiers, Asset Set Identifiers, Errors and User "
                 "Identifier had no value on any of the 488 written rows; Event Type held "
                 "AppleIntelligenceReportingEventTypeImpulse (3) on all 488."),
        "paths": ('*/streams/*/AppleIntelligence.Reporting.AssetDeliveryLog.Availability/local/*',),
        "output_types": "standard",
        "artifact_icon": "cpu",
        "sample_data": {
            "falken_ios26": "iOS 26.2.1 | 183 rows (172 written)",
            "hc_ios26": "iOS 26.5.2 | 96 rows (96 written)",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 676 rows (84 written)",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 1253 rows (136 written)",
        },
    },
    "get_biomeAIModelCatalog": {
        "name": "Biome - Apple Intelligence Model Catalog",
        "description": ("Parses records from the AppleIntelligence.Reporting.AssetDeliveryLog.ModelCatalog "
                       "biome stream: the event date and type, the use case and its parameters, asset "
                       "identifiers, build version and the subscription trigger, action and batch."),
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field and value names come from the stream's event class, an IntelligencePlatformLibrary EventWrapper type that BiomeLibrary.framework names for this stream, read on macOS 27.2.1 (26B131). No iOS copy was read. The stream's event class is a Swift type with no protoFields, so the "
                 "names were read by decoding synthetic records with the class's "
                 "eventWithData:dataVersion: and reading its json output. On the tested images every "
                 "written record decoded to field numbers that the class names. "
                 "Event Date is the event's date field, read as Unix seconds (reported before as Event Timestamp). The class does not state the epoch. On the tested images every written record's value, read this way, fell within one hour before its SEGB timestamp, and all but 6 within one second. Event Type is the event type (Unknown, Start, End or Impulse), reported before as Status (raw). Use Case ID, Use Case Parameters (name="
                 "value pairs), Locale and Country Code are the event's useCase fields; Use Case ID "
                 "was reported before as Feature or Client, and its parameter as Attribute and Attribute Value (empty before when a record held more than one; no tested record did). Resource Specifiers and Asset Set Identifiers are lists, joined "
                 "with commas; Asset Set Identifiers was reported before as Requesting Client. Errors joins each error's domain, errorCode and description (descriptionWithoutUnderlying when description is empty); the error's category, additionalUserInfo and underlying errors are not reported. The class also names useCase.mode, a number with no value names, which is not reported, and timeOfLastSoftwareUpdate, which no tested record held. Build Version, Subscription Name, "
                 "Subscriber Name and User Identifier were reported before as OS Build, Asset ID, "
                 "Asset Category and User ID. The stream's own state message (field 2) was printed "
                 "raw as Result (raw); it is now named: Trigger, Subscription Action and Batch Identifier are modelCatalogSubscriptionEventState's trigger, action and batchIdentifier. Deleted rows are not decoded. "
                 "On the tested images Country Code and Errors had no value on any of the 12,482 "
                 "written rows; Event Type held AppleIntelligenceReportingEventTypeImpulse (3) on "
                 "all 12,482."),
        "paths": ('*/streams/*/AppleIntelligence.Reporting.AssetDeliveryLog.ModelCatalog/local/*',),
        "output_types": "standard",
        "artifact_icon": "cpu",
        "sample_data": {
            "falken_ios26": "iOS 26.2.1 | 93 rows (88 written)",
            "hc_ios26": "iOS 26.5.2 | 206 rows (206 written)",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 4248 rows (4182 written)",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 8278 rows (8006 written)",
        },
    },
    "get_biomeAISoftwareUpdate": {
        "name": "Biome - Apple Intelligence Software Update",
        "description": ("Parses records from the "
                       "AppleIntelligence.Reporting.AssetDeliveryLog.SoftwareUpdateController biome stream: "
                       "the event date and type, errors, build version and the software update operation and "
                       "update type."),
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field and value names come from the stream's event class, an IntelligencePlatformLibrary EventWrapper type that BiomeLibrary.framework names for this stream, read on macOS 27.2.1 (26B131). No iOS copy was read. The stream's event class is a Swift type with no protoFields, so the "
                 "names were read by decoding synthetic records with the class's "
                 "eventWithData:dataVersion: and reading its json output. On the tested images every "
                 "written record decoded to field numbers that the class names. "
                 "Event Date is the event's date field, read as Unix seconds (reported before as Event Timestamp). The class does not state the epoch. On the tested images every written record's value, read this way, fell within one hour before its SEGB timestamp, and all but 6 within one second. Event Type is the event type (Unknown, Start, End or Impulse), reported before as Status (raw). Use Case ID, Use Case Parameters (name="
                 "value pairs), Locale and Country Code are the event's useCase fields; Use Case ID "
                 "was reported before as Feature or Client, and its parameter as Attribute and Attribute Value (empty before when a record held more than one; no tested record did). Resource Specifiers and Asset Set Identifiers are lists, joined "
                 "with commas; Asset Set Identifiers was reported before as Requesting Client. Errors joins each error's domain, errorCode and description (descriptionWithoutUnderlying when description is empty); the error's category, additionalUserInfo and underlying errors are not reported. The class also names useCase.mode, a number with no value names, which is not reported, and timeOfLastSoftwareUpdate, which no tested record held. Build Version, Subscription Name, "
                 "Subscriber Name and User Identifier were reported before as OS Build, Asset ID, "
                 "Asset Category and User ID. The stream's own state message (field 2) was printed "
                 "raw as Result (raw); it is now named: Operation and Update Type are softwareUpdateControllerPSUSEvent's operation and update. Deleted rows are not decoded. "
                 "On the tested images Use Case ID, Use Case Parameters, Locale, Country Code, "
                 "Resource Specifiers, Asset Set Identifiers, Subscription Name, Subscriber Name "
                 "and User Identifier had no value on any of the 141 written rows; Update Type "
                 "held UpdateTypeIncremental (3) on all 141."),
        "paths": ('*/streams/*/AppleIntelligence.Reporting.AssetDeliveryLog.SoftwareUpdateController/local/*',),
        "output_types": "standard",
        "artifact_icon": "cpu",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | 9 rows (9 written)",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 224 rows (24 written)",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 422 rows (108 written)",
        },
    },
    "get_biomeAISafetyOverrides": {
        "name": "Biome - Apple Intelligence Safety Overrides",
        "description": ("Parses records from the AppleIntelligence.Reporting.SafetyOverrides biome stream: the "
                       "use case, system locale, region, asset version, action and instance type of each written record."),
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field and value names come from the stream's event class, an IntelligencePlatformLibrary EventWrapper type that BiomeLibrary.framework names for this stream, read on macOS 27.2.1 (26B131). No iOS copy was read. The stream's event class is a Swift type with no protoFields, so the "
                 "names were read by decoding synthetic records with the class's "
                 "eventWithData:dataVersion: and reading its json output. On the tested images every "
                 "written record decoded to field numbers that the class names. "
                 "The record holds fields 1 to 6 directly (useCaseIdentifier, systemLocale, region, "
                 "assetVersion, action, instanceType); before, it was read with the AssetDeliveryLog "
                 "layout, so its detail columns were empty, except Result (raw), which held field 2 (systemLocale) decoded as a nested message. On wilkerson_iphone16_ios26 "
                 "Action held ActionSafe (1) and Instance Type InstanceTypePrompt (1) on all 60 written "
                 "records; hill_iphone15pro_ios26 held deleted records only. Deleted rows are not "
                 "decoded."),
        "paths": ('*/streams/*/AppleIntelligence.Reporting.SafetyOverrides/local/*',),
        "output_types": "standard",
        "artifact_icon": "shield",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 265 rows (0 written)",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 248 rows (60 written)",
        },
    },
    "get_biomeAIUnifiedAsset": {
        "name": "Biome - Apple Intelligence Unified Asset",
        "description": ("Parses records from the "
                       "AppleIntelligence.Reporting.AssetDeliveryLog.UnifiedAssetFramework biome stream: the "
                       "event date and type, asset identifiers, build version, the subscriber and the "
                       "download and subscription status."),
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field and value names come from the stream's event class, an IntelligencePlatformLibrary EventWrapper type that BiomeLibrary.framework names for this stream, read on macOS 27.2.1 (26B131). No iOS copy was read. The stream's event class is a Swift type with no protoFields, so the "
                 "names were read by decoding synthetic records with the class's "
                 "eventWithData:dataVersion: and reading its json output. On the tested images every "
                 "written record decoded to field numbers that the class names. "
                 "Event Date is the event's date field, read as Unix seconds (reported before as Event Timestamp). The class does not state the epoch. On the tested images every written record's value, read this way, fell within one hour before its SEGB timestamp, and all but 6 within one second. Event Type is the event type (Unknown, Start, End or Impulse), reported before as Status (raw). Use Case ID, Use Case Parameters (name="
                 "value pairs), Locale and Country Code are the event's useCase fields; Use Case ID "
                 "was reported before as Feature or Client, and its parameter as Attribute and Attribute Value (empty before when a record held more than one; no tested record did). Resource Specifiers and Asset Set Identifiers are lists, joined "
                 "with commas; Asset Set Identifiers was reported before as Requesting Client. Errors joins each error's domain, errorCode and description (descriptionWithoutUnderlying when description is empty); the error's category, additionalUserInfo and underlying errors are not reported. The class also names useCase.mode, a number with no value names, which is not reported, and timeOfLastSoftwareUpdate, which no tested record held. Build Version, Subscription Name, "
                 "Subscriber Name and User Identifier were reported before as OS Build, Asset ID, "
                 "Asset Category and User ID. The stream's own state message (field 2) was printed "
                 "raw as Result (raw); it is now named: Download Status and Subscription Status are unifiedAssetFrameworkSubscriptionState's downloadStatus and subscriptionStatus. Deleted rows are not decoded. "
                 "On the tested images Use Case ID, Use Case Parameters, Locale, Country Code, "
                 "Resource Specifiers and Errors had no value on any of the 427 written rows; "
                 "Event Type held AppleIntelligenceReportingEventTypeImpulse (3) on all 427; "
                 "Download Status held UAFSubscriptionDownloadStatusComplete (4) on all 427; "
                 "Subscription Status held Subscribed (1) on all 427; User Identifier held one value on all 427."),
        "paths": ('*/streams/*/AppleIntelligence.Reporting.AssetDeliveryLog.UnifiedAssetFramework/local/*',),
        "output_types": "standard",
        "artifact_icon": "cpu",
        "sample_data": {
            "falken_ios26": "iOS 26.2.1 | 217 rows (190 written)",
            "hc_ios26": "iOS 26.5.2 | 14 rows (14 written)",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 1212 rows (103 written)",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 1542 rows (120 written)",
        },
    },
}


import os
import struct
from datetime import datetime, timezone

from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)


def _to_str(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', 'replace')
    if value is None or isinstance(value, (dict, list)):
        return ''
    return str(value)


def _bool(value):
    """BMAppleIntelligenceAvailability bool fields: 1 True, 0 False, anything else blank."""
    return {1: 'True', 0: 'False'}.get(value, '') if isinstance(value, int) else ''


def _unix_double(value):
    if not isinstance(value, int) or value == 0:
        return None
    seconds = struct.unpack('<d', struct.pack('<Q', value & 0xFFFFFFFFFFFFFFFF))[0]
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None


def _stream_files(context):
    """Non-hidden, non-tombstone stream files from the artifact's matched paths."""
    for file_found in sorted(map(str, context.get_files_found())):
        if os.path.basename(file_found).startswith('.'):
            continue
        if not os.path.isfile(file_found) or 'tombstone' in context.get_relative_path(file_found):
            continue
        yield file_found


def _source_path(context):
    return '\n'.join(sorted({os.path.dirname(f) for f in _stream_files(context)}))


def _iter_records(context, label):
    for file_found in _stream_files(context):
        filename = os.path.basename(file_found)

        for record in read_segb_file(file_found):
            ts = record.timestamp1.replace(tzinfo=timezone.utc)
            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data)
                except _DECODE_ERRORS as ex:
                    logfunc(f'{label}: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue
                yield ts, record, protostuff, filename
            elif record.state == EntryState.Deleted:
                yield ts, record, None, filename


# Field and enum names of the AppleIntelligence.Reporting streams, read on macOS 27.2.1 (26B131)
# from the event classes BiomeLibrary.framework names for them. These streams' event classes are Swift (IntelligencePlatformLibrary
# EventWrapper) with no protoFields; the names were read by decoding synthetic records with the
# class's eventWithData:dataVersion: and reading its json output.
_EVENT_TYPE = {0: 'AppleIntelligenceReportingEventTypeUnknown', 1:
    'AppleIntelligenceReportingEventTypeStart', 2: 'AppleIntelligenceReportingEventTypeEnd', 3:
    'AppleIntelligenceReportingEventTypeImpulse'}
_AVAIL_STATUS = {0: 'StatusUnknown', 1: 'StatusAvailable', 2: 'StatusRestricted', 3:
    'StatusUnavailable'}
_MC_TRIGGER = {0: 'TriggerUnknown', 1: 'TriggerAvailabilityChange', 2: 'TriggerInternalTool',
    3: 'TriggerScheduled'}
_MC_ACTION = {0: 'SubscriptionActionUnknown', 1: 'SubscriptionActionSubscribe', 2:
    'SubscriptionActionUnsubscribe'}
_SU_OPERATION = {0: 'OperationTypeUnknown', 1: 'OperationTypeOther', 2:
    'OperationTypePSUSDetermine', 3: 'OperationTypePSUSDownload'}
_SU_UPDATE = {0: 'UpdateTypeUnknown', 1: 'UpdateTypeOther', 2: 'UpdateTypeNotSpecified', 3:
    'UpdateTypeIncremental', 4: 'UpdateTypeFull', 5: 'UpdateTypeEmergency', 6:
    'UpdateTypeCritical', 7: 'UpdateTypeCriticalCellular'}
_UAF_DOWNLOAD = {0: 'DownloadStatusUnknown', 1: 'UAFSubscriptionDownloadStatusNotDownloading',
    2: 'UAFSubscriptionDownloadStatusDownloading', 3:
    'UAFSubscriptionDownloadStatusDownloadStalled', 4: 'UAFSubscriptionDownloadStatusComplete',
    5: 'UAFSubscriptionDownloadStatusOutOfSpace', 6: 'UAFSubscriptionDownloadStatusError', 7:
    'UAFSubscriptionDownloadStatusNetworkError', 8:
    'UAFSubscriptionDownloadStatusDowngradeError'}
_UAF_SUBSCRIPTION = {0: 'SubscriptionStatusUnknown', 1: 'Subscribed', 2: 'Unsubscribed'}
_SO_ACTION = {0: 'ActionUnknown', 1: 'ActionSafe', 2: 'ActionReject', 3: 'ActionRemove', 4:
    'ActionReplace'}
_SO_INSTANCE = {0: 'InstanceTypeUnknown', 1: 'InstanceTypePrompt', 2: 'InstanceTypeResponse'}

_S = {'type': 'bytes', 'name': ''}
_I = {'type': 'int', 'name': ''}
_KV = {'type': 'message', 'name': '', 'message_typedef': {'1': _S, '2': _S}}
_DELIVERY_TYPEDEF = {
    '1': {'type': 'message', 'name': '', 'message_typedef': {        # event
        '1': {'type': 'fixed64', 'name': ''},                        # date (Unix seconds)
        '2': _I,                                                     # type
        '3': {'type': 'message', 'name': '', 'message_typedef': {    # useCase
            '1': _S, '2': _KV, '3': _I, '4': _S, '5': _S}},
        '4': _S, '5': _S,                                            # resourceSpecifiers, assetSetIdentifiers
        '6': {'type': 'message', 'name': '', 'message_typedef': {    # errors
            '1': _S, '2': _I, '3': _S, '4': _S, '6': _S}},
        '7': _S, '8': _S, '9': _S, '10': _I}},                       # buildVersion ... userIdentifier
}
_SAFETY_TYPEDEF = {'1': _S, '2': _S, '3': _S, '4': _S, '5': _I, '6': _I}


def _list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _joined(value):
    return ', '.join(t for t in (_to_str(v) for v in _list(value)) if t)


def _named(names, value):
    if not isinstance(value, int):
        return ''
    return f'{names[value]} ({value})' if value in names else str(value)


def _get(message, *path):
    for key in path:
        if not isinstance(message, dict):
            return None
        message = message.get(key)
    return message


def _parameters(use_case):
    parts = []
    for entry in _list(_get(use_case, '2')):
        if isinstance(entry, dict):
            name, value = _to_str(entry.get('1')), _to_str(entry.get('2'))
            if name or value:
                parts.append(f'{name}={value}')
    return '; '.join(parts)


def _errors(event):
    parts = []
    for error in _list(_get(event, '6')):
        if not isinstance(error, dict):
            continue
        code = error.get('2')
        text = ' '.join(t for t in (_to_str(error.get('1')),
                                     str(code) if isinstance(code, int) else '',
                                     _to_str(error.get('4')) or _to_str(error.get('3'))) if t)
        if text:
            parts.append(text)
    return '; '.join(parts)


def _iter_typed(context, label, typedef):
    for file_found in _stream_files(context):
        filename = os.path.basename(file_found)
        for record in read_segb_file(file_found):
            ts = record.timestamp1.replace(tzinfo=timezone.utc)
            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, typedef)
                except _DECODE_ERRORS as ex:
                    logfunc(f'{label}: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue
                yield ts, record, protostuff, filename
            elif record.state == EntryState.Deleted:
                yield ts, record, None, filename


def _delivery_log(context, label, state_headers, state_values):
    """Shared parser for the four AssetDeliveryLog streams.

    Field 1 is the event and field 2 the stream's own state message; state_values turns
    field 2 into the columns named in state_headers.
    """
    data_headers = ((('SEGB Timestamp', 'datetime'), ('Event Date', 'datetime'), 'SEGB State',
                     'Event Type', 'Event Type (raw)') + tuple(state_headers) +
                    ('Use Case ID', 'Use Case Parameters', 'Locale', 'Country Code',
                     'Resource Specifiers', 'Asset Set Identifiers', 'Errors', 'Build Version',
                     'Subscription Name', 'Subscriber Name', 'User Identifier', 'Filename',
                     'Offset'))
    blank = len(data_headers) - 5
    data_list = []
    for ts, record, protostuff, filename in _iter_typed(context, label, _DELIVERY_TYPEDEF):
        if protostuff is None:
            data_list.append((ts, None, record.state.name) + (None,) * blank +
                             (filename, record.data_start_offset))
            continue
        event = _get(protostuff, '1')
        event = event if isinstance(event, dict) else {}
        use_case = event.get('3') if isinstance(event.get('3'), dict) else {}
        event_type = event.get('2')
        user = event.get('10')
        data_list.append((ts, _unix_double(event.get('1')), record.state.name,
                          _named(_EVENT_TYPE, event_type),
                          event_type if isinstance(event_type, int) else '') +
                         tuple(state_values(protostuff.get('2'))) +
                         (_to_str(use_case.get('1')), _parameters(use_case),
                          _to_str(use_case.get('4')), _to_str(use_case.get('5')),
                          _joined(event.get('4')), _joined(event.get('5')), _errors(event),
                          _to_str(event.get('7')), _to_str(event.get('8')),
                          _to_str(event.get('9')), user if isinstance(user, int) else '',
                          filename, record.data_start_offset))
    return data_headers, data_list, _source_path(context)


@artifact_processor
def get_biomeAppleIntelligenceAvailability(context):
    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Languages',
                    'Apple Intelligence Is Device Eligible', 'Diffusion Is Device Eligible',
                    'Apple Intelligence Toggle Enabled', 'Filename', 'Offset')
    data_list = []
    for ts, record, protostuff, filename in _iter_records(context,
                                                          'Apple Intelligence Availability'):
        if protostuff is None:
            data_list.append((ts, record.state.name, None, None, None, None, filename,
                              record.data_start_offset))
            continue
        first = protostuff.get('1', {})
        second = protostuff.get('2', {})
        languages = protostuff.get('6')
        if not isinstance(languages, list):
            languages = [languages]
        data_list.append((ts, record.state.name,
                          '; '.join(t for t in (_to_str(v) for v in languages) if t),
                          _bool(first.get('1') if isinstance(first, dict) else first),
                          _bool(second.get('1') if isinstance(second, dict) else second),
                          _bool(protostuff.get('3')), filename, record.data_start_offset))
    return data_headers, data_list, _source_path(context)


@artifact_processor
def get_biomeAIAssetAvailability(context):
    def state(value):
        info = _get(value, '1')
        status, reasons = _get(info, '1'), _get(info, '2')
        return (_named(_AVAIL_STATUS, status), status if isinstance(status, int) else '',
                reasons if isinstance(reasons, int) else '')
    return _delivery_log(context, 'Apple Intelligence Asset Availability',
                         ('Status', 'Status (raw)', 'Reasons (raw)'), state)


@artifact_processor
def get_biomeAIModelCatalog(context):
    def state(value):
        trigger, action = _get(value, '1'), _get(value, '2')
        return (_named(_MC_TRIGGER, trigger), _named(_MC_ACTION, action),
                _to_str(_get(value, '3')))
    return _delivery_log(context, 'Apple Intelligence Model Catalog',
                         ('Trigger', 'Subscription Action', 'Batch Identifier'), state)


@artifact_processor
def get_biomeAISoftwareUpdate(context):
    def state(value):
        return (_named(_SU_OPERATION, _get(value, '1')), _named(_SU_UPDATE, _get(value, '2')))
    return _delivery_log(context, 'Apple Intelligence Software Update',
                         ('Operation', 'Update Type'), state)


@artifact_processor
def get_biomeAIUnifiedAsset(context):
    def state(value):
        return (_named(_UAF_DOWNLOAD, _get(value, '1')),
                _named(_UAF_SUBSCRIPTION, _get(value, '2')))
    return _delivery_log(context, 'Apple Intelligence Unified Asset',
                         ('Download Status', 'Subscription Status'), state)


@artifact_processor
def get_biomeAISafetyOverrides(context):
    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Use Case ID', 'System Locale',
                    'Region', 'Asset Version', 'Action', 'Instance Type', 'Filename', 'Offset')
    data_list = []
    for ts, record, protostuff, filename in _iter_typed(
            context, 'Apple Intelligence Safety Overrides', _SAFETY_TYPEDEF):
        if protostuff is None:
            data_list.append((ts, record.state.name) + (None,) * 6 +
                             (filename, record.data_start_offset))
            continue
        data_list.append((ts, record.state.name, _to_str(protostuff.get('1')),
                          _to_str(protostuff.get('2')), _to_str(protostuff.get('3')),
                          _to_str(protostuff.get('4')), _named(_SO_ACTION, protostuff.get('5')),
                          _named(_SO_INSTANCE, protostuff.get('6')), filename,
                          record.data_start_offset))
    return data_headers, data_list, _source_path(context)
