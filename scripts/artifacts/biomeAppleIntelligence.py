"""Apple Intelligence biome streams.

The four AssetDeliveryLog streams share one wrapper: field 1 carries the event
timestamp, a status code, a context submessage naming the feature or client and
one key/value attribute, the OS build, and the asset identifiers; field 2 carries
the delivery result.
"""
__artifacts_v2__ = {
    "get_biomeAppleIntelligenceAvailability": {
        "name": "Biome - Apple Intelligence Availability",
        "description": "Parses Apple Intelligence availability state changes from the "
                       "AppleIntelligence.Availability biome stream, including the language "
                       "the feature was evaluated for.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "The three state fields are reported raw; the sample does not establish which "
                 "availability condition each denotes.",
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
        "description": "Parses Apple Intelligence asset availability reporting from the "
                       "AppleIntelligence.Reporting.AssetDeliveryLog.Availability biome "
                       "stream: the requesting client, the attribute it was evaluated against "
                       "and the OS build at the time.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/streams/*/AppleIntelligence.Reporting.AssetDeliveryLog.Availability/local/*',),
        "output_types": "standard",
        "artifact_icon": "cpu",
        "sample_data": {
            "hc_ios26": "26.5.2 | 96 rows",
        },
    },
    "get_biomeAIModelCatalog": {
        "name": "Biome - Apple Intelligence Model Catalog",
        "description": "Parses Apple Intelligence model catalog activity from the "
                       "AppleIntelligence.Reporting.AssetDeliveryLog.ModelCatalog biome "
                       "stream. Each record names the Apple Intelligence feature whose model "
                       "was requested, for example a text composition or summarisation "
                       "feature, and the language it was requested for, showing which "
                       "features' models were requested on the device and when; user exercise "
                       "of the feature is not established.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "In test data, this is the highest volume stream of the Apple Intelligence family.",
        "paths": ('*/streams/*/AppleIntelligence.Reporting.AssetDeliveryLog.ModelCatalog/local/*',),
        "output_types": "standard",
        "artifact_icon": "cpu",
        "sample_data": {
            "hc_ios26": "26.5.2 | 206 rows",
        },
    },
    "get_biomeAISoftwareUpdate": {
        "name": "Biome - Apple Intelligence Software Update",
        "description": "Parses Apple Intelligence software update controller reporting from "
                       "the AppleIntelligence.Reporting.AssetDeliveryLog."
                       "SoftwareUpdateController biome stream.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/streams/*/AppleIntelligence.Reporting.AssetDeliveryLog.SoftwareUpdateController/local/*',),
        "output_types": "standard",
        "artifact_icon": "cpu",
        "sample_data": {
            "hc_ios26": "26.5.2 | 9 rows",
        },
    },
    "get_biomeAISafetyOverrides": {
        "name": "Biome - Apple Intelligence Safety Overrides",
        "description": "Parses Apple Intelligence safety override reporting from the "
                       "AppleIntelligence.Reporting.SafetyOverrides biome stream. Records mark "
                       "the times safety override reporting occurred, which is worth noting "
                       "even where the payload itself no longer survives.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "The sample for this stream held only deleted records, so the written record "
                 "layout is not confirmed. It is read with the shared AssetDeliveryLog parser "
                 "because the partially recoverable deleted payloads carry the same field 1 "
                 "event and field 3 context structure as the rest of that family; if a future "
                 "sample shows a different layout the detail columns will be empty while the "
                 "timestamps stay correct. Deleted payloads in the sample were largely "
                 "overwritten and did not decode, but their SEGB timestamps are intact and "
                 "consistent with reporting having occurred at those times.",
        "paths": ('*/streams/*/AppleIntelligence.Reporting.SafetyOverrides/local/*',),
        "output_types": "standard",
        "artifact_icon": "shield",
    },
    "get_biomeAIUnifiedAsset": {
        "name": "Biome - Apple Intelligence Unified Asset",
        "description": "Parses Apple Intelligence unified asset framework reporting from the "
                       "AppleIntelligence.Reporting.AssetDeliveryLog.UnifiedAssetFramework "
                       "biome stream: the asset requested, the client that requested it and "
                       "the user id it was requested under.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/streams/*/AppleIntelligence.Reporting.AssetDeliveryLog.UnifiedAssetFramework/local/*',),
        "output_types": "standard",
        "artifact_icon": "cpu",
        "sample_data": {
            "hc_ios26": "26.5.2 | 14 rows",
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
        if not os.path.isfile(file_found) or 'tombstone' in file_found:
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


def _delivery_log(context, label):
    """Shared parser for the four AssetDeliveryLog streams."""
    data_headers = (('SEGB Timestamp', 'datetime'), ('Event Timestamp', 'datetime'),
                    'SEGB State', 'Feature or Client', 'Attribute', 'Attribute Value',
                    'Requesting Client', 'Asset ID', 'Asset Category', 'OS Build',
                    'User ID', 'Status (raw)', 'Result (raw)', 'Filename', 'Offset')
    data_list = []
    for ts, record, protostuff, filename in _iter_records(context, label):
        if protostuff is None:
            data_list.append((ts, None, record.state.name, None, None, None, None, None, None,
                              None, None, None, None, filename, record.data_start_offset))
            continue

        event = protostuff.get('1', {})
        if not isinstance(event, dict):
            event = {}
        context_msg = event.get('3', {})
        if not isinstance(context_msg, dict):
            context_msg = {}
        attribute = context_msg.get('2', {})
        if not isinstance(attribute, dict):
            attribute = {}
        result = protostuff.get('2', {})

        data_list.append((ts, _unix_double(event.get('1')), record.state.name,
                          _to_str(context_msg.get('1')), _to_str(attribute.get('1')),
                          _to_str(attribute.get('2')), _to_str(event.get('5')),
                          _to_str(event.get('8')), _to_str(event.get('9')),
                          _to_str(event.get('7')), event.get('10', ''),
                          event.get('2', ''), str(result) if result else '',
                          filename, record.data_start_offset))
    return data_headers, data_list, _source_path(context)


@artifact_processor
def get_biomeAppleIntelligenceAvailability(context):
    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Language',
                    'State 1 (raw)', 'State 2 (raw)', 'State 3 (raw)', 'Filename', 'Offset')
    data_list = []
    for ts, record, protostuff, filename in _iter_records(context,
                                                          'Apple Intelligence Availability'):
        if protostuff is None:
            data_list.append((ts, record.state.name, None, None, None, None, filename,
                              record.data_start_offset))
            continue
        first = protostuff.get('1', {})
        second = protostuff.get('2', {})
        data_list.append((ts, record.state.name, _to_str(protostuff.get('6')),
                          first.get('1', '') if isinstance(first, dict) else first,
                          second.get('1', '') if isinstance(second, dict) else second,
                          protostuff.get('3', ''), filename, record.data_start_offset))
    return data_headers, data_list, _source_path(context)


@artifact_processor
def get_biomeAIAssetAvailability(context):
    return _delivery_log(context, 'Apple Intelligence Asset Availability')


@artifact_processor
def get_biomeAIModelCatalog(context):
    return _delivery_log(context, 'Apple Intelligence Model Catalog')


@artifact_processor
def get_biomeAISoftwareUpdate(context):
    return _delivery_log(context, 'Apple Intelligence Software Update')


@artifact_processor
def get_biomeAIUnifiedAsset(context):
    return _delivery_log(context, 'Apple Intelligence Unified Asset')


@artifact_processor
def get_biomeAISafetyOverrides(context):
    return _delivery_log(context, 'Apple Intelligence Safety Overrides')
