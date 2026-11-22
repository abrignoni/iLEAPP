__artifacts_v2__ = {
    "get_biomeSafariWebPagePerformance": {
        "name": "Biome - Safari Web Page Performance",
        "description": "Parses records from the Safari.WebPagePerformance biome "
                       "stream. What a record "
                       "represents is not established; the domain, a timestamp on a "
                       "30 minute boundary, a platform, a performance event and a "
                       "privacy proxy flag are reported.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "The Domain, Platform, Performance Event and Privacy Proxy field names and the "
                 "Platform and Performance Event value names are those of the "
                 "BMSafariWebPagePerformance class, read from BiomeLibrary.framework on macOS "
                 "27.2.1 (26B131); no iOS copy of the class was read. The class reads only data "
                 "version 0 (the unnamed integer the SEGB reader returns with each entry); a "
                 "record of another version, or a value outside the class's lists, keeps its integer in the (raw) "
                 "column with the name blank. Domain was reported before as Detail (raw), Platform "
                 "as Field 3 (raw), Performance Event as "
                 "Field 4 (raw) and Privacy Proxy as Field 5 (raw). Privacy Proxy reads True for 1, "
                 "False for 0 and is blank otherwise. Rounded Timestamp (30 min) is field 2, "
                 "which the class reads as a date on the Unix epoch. On the "
                 "tested images it fell on a 30 "
                 "minute boundary after the SEGB timestamp, as in Safari.Navigations. On the 23 "
                 "written records on the tested images Platform was 2 (IOS) on all 23, Performance "
                 "Event was 3 (EnergyDrain) on 15 and 1 (Crash) on 8, and Privacy Proxy was False "
                 "on 22 and True on 1. Domain is read as a string; before, one of those 23 records "
                 "(on iphone11_ios17) showed a decoded structure in place of its domain.",
        "paths": ('*/streams/*/Safari.WebPagePerformance/local/*',),
        "output_types": "standard",
        "artifact_icon": "compass",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 1 row",
        },
    }
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

# Pin domain as a string so it is never eagerly decoded as a nested protobuf.
TYPESS = {
    '1': {'type': 'str', 'name': ''},
}

# platform and performanceEvent names, read from BiomeLibrary.framework
# BMSafariWebPagePerformance on macOS 27.2.1 (26B131). The class reads only data version 0
# (the unnamed int the SEGB reader returns per entry); other versions get no name, and so do values
# the class renders only as its fallback.
PLATFORM_BY_VERSION = {
    0: dict(enumerate(('Unknown', 'MacOS', 'IOS', 'IPadOS'))),
}
PERFORMANCE_EVENT_BY_VERSION = {
    0: dict(enumerate(('Unknown', 'Crash', 'Jetsam', 'EnergyDrain'))),
}


def _to_str(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', 'replace')
    if value is None:
        return ''
    return str(value)


def _bool_text(value):
    if value == 1 and not isinstance(value, bool):
        return 'True'
    if value == 0 and not isinstance(value, bool):
        return 'False'
    return ''


def _unix_double(value):
    if isinstance(value, int) and value > 10 ** 15:
        value = struct.unpack('<d', struct.pack('<q', value))[0]
    if not isinstance(value, (int, float)) or not value:
        return None
    try:
        return datetime.fromtimestamp(value, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None


@artifact_processor
def get_biomeSafariWebPagePerformance(context):

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
                    logfunc(f'Safari Web Page Performance: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                version = getattr(record, '_unknown_value', None)
                platform = protostuff.get('3', '')
                performance_event = protostuff.get('4', '')

                data_list.append((ts, _unix_double(protostuff.get('2')), record.state.name,
                                  _to_str(protostuff.get('1', b'')),
                                  PLATFORM_BY_VERSION.get(version, {}).get(platform, ''),
                                  platform,
                                  PERFORMANCE_EVENT_BY_VERSION.get(version, {}).get(
                                      performance_event, ''),
                                  performance_event, _bool_text(protostuff.get('5')),
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, None,
                                  None, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Rounded Timestamp (30 min)', 'datetime'),
                    'SEGB State', 'Domain', 'Platform', 'Platform (raw)', 'Performance Event',
                    'Performance Event (raw)', 'Privacy Proxy', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
