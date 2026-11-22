__artifacts_v2__ = {
    "get_biomeAppWebUsage": {
        "name": "Biome - App Web Usage",
        "description": "Parses App Web Usage entries from Biome",
        "author": "r.schramp@nfi.nl",
        "creation_date": "2026-05-29",
        "last_update_date": "2026-11-18",
        "version": "0.0.1",
        "date": "2026-05-29",
        "requirements": "none",
        "category": "Biome",
        "notes": "The Usage State and Is Usage Trusted field names and the Usage State "
                 "value names are those of the BMAppWebUsage class, read from BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class "
                 "was read. The class reads only data version 1 (the unnamed integer the SEGB reader "
                 "returns with each entry); a record of another version, or a value outside the class's "
                 "list, keeps its integer in Usage State (raw) with the name blank. Usage State "
                 "was reported before as pb_int_3 and Is Usage Trusted as pb_int_8. Is Usage "
                 "Trusted reads True for 1, False for 0 and is blank otherwise. On the 718 written "
                 "records on the tested images Usage State was 1 (NotInUse) on 370 and 3 "
                 "(InFocus) on 348, and Is Usage Trusted was True on all 718.",
        "paths": ('*/Biome/streams/restricted/App.WebUsage/local/*'),
        "output_types": "standard",
        "artifact_icon": "world",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 29 rows",
            "felix_ios17": "iOS 17.6.1 | 30 rows",
            "fsfull002_ios17": "iOS 17.1 | 12 rows",
            "hc_ios18_7": "iOS 18.7.8 | 26 rows",
            "iphone11_ios17": "iOS 17.3 | 3 rows",
            "iphone12_ios18": "iOS 18.7 | 110 rows",
            "iphone14plus_ios18": "iOS 18.0 | 46 rows",
            "otto_ios17": "iOS 17.5.1 | 371 rows",
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

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)


# usageState names, read from BiomeLibrary.framework BMAppWebUsage on macOS 27.2.1 (26B131).
# The class reads only data version 1 (the unnamed int the SEGB reader returns per entry); other
# versions get no name, and so do values the class renders only as its fallback.
USAGE_STATE_BY_VERSION = {
    1: dict(enumerate(('Unknown', 'NotInUse', 'InUse', 'InFocus'))),
}


def _bool_text(value):
    if value == 1 and not isinstance(value, bool):
        return 'True'
    if value == 0 and not isinstance(value, bool):
        return 'False'
    return ''


@artifact_processor
def get_biomeAppWebUsage(context):

    # Field mapping (BMAppWebUsage field names in brackets):
    #   1  -> GUID / UUID string (uniqueID)
    #   2  -> Timestamp (webkit/double, e.g. 7.858817e8) (absoluteTimestamp)
    #   3  -> Usage State enum (usageState)
    #   4  -> Full URL string (webpageURL)
    #   5  -> Domain / host string (webDomain)
    #   6  -> Bundle ID string (e.g. com.apple.mobilesafari) (applicationID)
    #   8  -> Is Usage Trusted bool (isUsageTrusted)

    typess = {
        '1': {'type': 'str',    'name': 'guid'},
        '2': {'type': 'double', 'name': 'timestamp'},
        '3': {'type': 'int',    'name': 'usage_state'},
        '4': {'type': 'str',    'name': 'url'},
        '5': {'type': 'str',    'name': 'domain'},
        '6': {'type': 'str',    'name': 'bundle_id'},
        '8': {'type': 'int',    'name': 'is_usage_trusted'},
    }

    data_list = []
    report_file = ''

    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found)

        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in context.get_relative_path(file_found):
                continue
            else:
                report_file = os.path.dirname(file_found)
        else:
            continue

        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _types = blackboxprotobuf.decode_message(record.data, typess)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Biome App Web Usage: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                guid               = protostuff.get('guid', '')
                raw_timestamp      = protostuff.get('timestamp')
                # an NSDate sentinel converts to '', kept as None like the other absent values
                timestamp          = ((webkit_timestampsconv(raw_timestamp) or None)
                                      if isinstance(raw_timestamp, (int, float)) else None)
                usage_state        = protostuff.get('usage_state', None)
                url                = protostuff.get('url', '')
                domain             = protostuff.get('domain', '')
                bundle_id          = protostuff.get('bundle_id', '')
                is_usage_trusted   = _bool_text(protostuff.get('is_usage_trusted'))
                version            = getattr(record, '_unknown_value', None)
                usage_state_name   = USAGE_STATE_BY_VERSION.get(version, {}).get(usage_state, '')

                data_list.append((
                    ts,
                    timestamp,
                    record.state.name,
                    url,
                    domain,
                    bundle_id,
                    guid,
                    usage_state_name,
                    usage_state,
                    is_usage_trusted,
                    filename,
                    record.data_start_offset
                ))

            elif record.state == EntryState.Deleted:
                data_list.append((
                    ts,
                    None,               # timestart
                    record.state.name,
                    None,               # url
                    None,               # domain
                    None,               # bundle_id
                    None,               # guid
                    None,               # usage state
                    None,               # usage state (raw)
                    None,               # is usage trusted
                    filename,
                    record.data_start_offset
                ))

    data_headers = (
        ('SEGB Timestamp', 'datetime'),
        ('Timestamp',      'datetime'),
        'SEGB State',
        'URL',
        'Domain',
        'Bundle ID',
        'GUID',
        'Usage State',
        'Usage State (raw)',
        'Is Usage Trusted',
        'Filename',
        'Offset'
    )

    return data_headers, data_list, report_file