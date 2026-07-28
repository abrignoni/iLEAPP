__artifacts_v2__ = {
    "get_biomeLocationVisit": {
        "name": "Biome - Location Visit",
        "description": "Parses visited places from the Location.Visit biome stream: coordinates "
                       "with horizontal accuracy, arrival and departure times, and the matched "
                       "point of interest (name, address and category) when iOS identified one. "
                       "TIMESTAMP CAUTION: the coordinates in this stream are reliable but the "
                       "timestamps are not. Records are written to the stream in batches long "
                       "after the visit, so the SEGB record time is a write time, not a visit "
                       "time, and the detection timestamp does not consistently line up with "
                       "the arrival and departure pair. Treat every time in this artifact as "
                       "an indication that needs corroborating from another source before it "
                       "is relied on.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Biome",
        "notes": "Timestamp reliability, observed in the sample data: every record in a stream "
                 "file shared one identical SEGB write time while the visits themselves spanned "
                 "weeks, so the whole batch was flushed at once. The detection timestamp "
                 "(field 1) ran from hours to more than a day after the recorded departure and "
                 "up to 28 days before the SEGB write. Arrival and departure are internally "
                 "consistent (arrival always precedes departure, spans from about half an hour "
                 "to just over a day) and are the most usable pair, but they are still not "
                 "independently verified. The coordinates, accuracy and point of interest "
                 "details are reliable. Latitude, longitude, horizontal accuracy in metres and "
                 "confidence are stored as doubles; vertical accuracy of -1 means unavailable.",
        "paths": ('*/streams/*/Location.Visit/local/*',),
        "output_types": ["html", "tsv", "timeline", "lava", "kml"],
        "artifact_icon": "map-pin",
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


def _to_str(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', 'replace')
    if value is None or isinstance(value, (dict, list)):
        return ''
    return str(value)


def _double(value):
    """Doubles are carried as fixed64 and surface as unsigned ints."""
    if isinstance(value, float):
        return value
    if not isinstance(value, int):
        return None
    return struct.unpack('<d', struct.pack('<Q', value & 0xFFFFFFFFFFFFFFFF))[0]


def _timestamp(value):
    seconds = _double(value)
    if seconds is None or not seconds:
        return None
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None


def _rounded(value, digits):
    return round(value, digits) if isinstance(value, float) else ''


@artifact_processor
def get_biomeLocationVisit(context):

    data_list = []
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

        for record in read_segb_file(file_found):
            ts = record.timestamp1.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Location Visit: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                geo = protostuff.get('3', {})
                if not isinstance(geo, dict):
                    geo = {}
                latitude = _double(geo.get('1'))
                longitude = _double(geo.get('2'))
                horizontal = _double(geo.get('3'))
                altitude = _double(geo.get('4'))
                vertical = _double(geo.get('5'))

                place = protostuff.get('8', {})
                if not isinstance(place, dict):
                    place = {}
                detail = place.get('5', {})
                if not isinstance(detail, dict):
                    detail = {}

                data_list.append((
                    _timestamp(protostuff.get('4')), _timestamp(protostuff.get('5')),
                    _timestamp(protostuff.get('1')), ts, record.state.name,
                    _rounded(latitude, 6), _rounded(longitude, 6), _rounded(horizontal, 2),
                    _rounded(altitude, 2), _rounded(vertical, 2),
                    _rounded(_double(protostuff.get('6')), 3),
                    _to_str(detail.get('2', b'')), _to_str(detail.get('3', b'')),
                    _to_str(detail.get('4', b'')), _to_str(detail.get('1', b'')),
                    _to_str(place.get('1', b'')), filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((None, None, None, ts, record.state.name, None, None, None,
                                  None, None, None, None, None, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (
        ('Arrival Timestamp', 'datetime'), ('Departure Timestamp', 'datetime'),
        ('Detection Timestamp', 'datetime'), ('SEGB Write Timestamp', 'datetime'),
        'SEGB State', 'Latitude', 'Longitude', 'Horizontal Accuracy (m)', 'Altitude',
        'Vertical Accuracy', 'Confidence', 'Place Name', 'Place Address', 'Place Category',
        'Place ID', 'Visit ID', 'Filename', 'Offset')

    return data_headers, data_list, 'see Filename for more info'
