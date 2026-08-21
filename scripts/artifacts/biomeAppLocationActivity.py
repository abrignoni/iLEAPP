__artifacts_v2__ = {
    "get_biomeAppLocationActivity": {
        "name": "Biome - App Location Activity",
        "description": "Parses NSUserActivity records that carry place details from the "
                       "App.LocationActivity biome stream: the donating app, the activity type "
                       "and payload, the web page or item involved, and the associated street "
                       "address, city and postal code. TIMESTAMP CAUTION: the place details in "
                       "this stream parse consistently, but the timestamps require caution. "
                       "Records are "
                       "written in batches, so the SEGB record time is a write time rather than "
                       "the moment of the activity, and the other timestamp on the record is an "
                       "expiry roughly 30 days ahead. Corroborate any time here against another "
                       "source before relying on it.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "Same NSUserActivity record shape as the App.Activity stream, extended with "
                 "place fields. In the sample data the SEGB write times were identical across "
                 "records and fell on an exact minute boundary, which is a further sign they "
                 "are batch write times and not activity times. The expiration timestamp sits "
                 "about 30 days after the SEGB write, matching the interval seen in "
                 "App.Activity. Payload strings are URL-decoded for display. Reference: Mattia "
                 "Epifani, '84 Streams Later, Part 2: Inside Apple Biome', "
                 "https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html",
        "paths": ('*/streams/*/App.LocationActivity/local/*',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "dexter_ios18": "402 rows",
            "hc_ios18_7": "19 rows",
            "iphone12_ios18": "44 rows",
        },
    }
}


import os
import struct
from datetime import datetime, timezone
from urllib.parse import unquote

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


@artifact_processor
def get_biomeAppLocationActivity(context):

    data_list = []
    source_dirs = set()
    for file_found in sorted(context.get_files_found()):
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in file_found:
                continue
        else:
            continue

        source_dirs.add(os.path.dirname(file_found))
        for record in read_segb_file(file_found):
            ts = record.timestamp1.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data)
                except _DECODE_ERRORS as ex:
                    logfunc(f'App Location Activity: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                address = _to_str(protostuff.get('29', b''))
                city = _to_str(protostuff.get('26', b''))
                postal = _to_str(protostuff.get('32', b''))

                data_list.append((ts, _unix_double(protostuff.get('5')), record.state.name,
                                  _to_str(protostuff.get('1', b'')),
                                  _to_str(protostuff.get('2', b'')),
                                  _to_str(protostuff.get('34', b'')),
                                  address, city, postal,
                                  _to_str(protostuff.get('9', b'')),
                                  _to_str(protostuff.get('35', b'')),
                                  unquote(_to_str(protostuff.get('14', b''))),
                                  _to_str(protostuff.get('19', b'')),
                                  _to_str(protostuff.get('15', b'')),
                                  _to_str(protostuff.get('16', b'')),
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, None,
                                  None, None, None, None, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Write Timestamp', 'datetime'), ('Expiration Timestamp', 'datetime'),
                    'SEGB State', 'Bundle ID', 'Activity Type', 'Title', 'Street Address',
                    'City', 'Postal Code', 'URL', 'Place URL', 'Payload', 'Donation Type',
                    'Activity UUID', 'Source', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
