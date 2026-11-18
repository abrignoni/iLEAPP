__artifacts_v2__ = {
    "get_biomeLocationVisit": {
        "name": "Biome - Location Visit",
        "description": "Parses visited places from the Location.Visit biome stream: coordinates "
                       "with horizontal accuracy, arrival and departure times, and a place "
                       "name, address and category where the record carries them. "
                       "TIMESTAMP CAUTION: on the tested images coordinates and both accuracy "
                       "values were present on each of the 156 written rows; the timestamps "
                       "require caution. On the tested images the SEGB record time ran from "
                       "minutes to weeks after the recorded departure. It is a write time, not "
                       "a visit time. On the tested images the Detection Date column ran from "
                       "minutes to 24 days after the recorded departure. Treat every time in "
                       "this artifact as an indication that needs corroborating from another "
                       "source before it is relied on.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani), @AlexisBrignoni, Codex",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "On the tested images the records of a stream file did not share a SEGB write "
                 "time. Arrival, departure and detection date are stored as doubles and read "
                 "here as Unix epoch seconds. Detection Date (field 1, reported before as Field "
                 "1 Timestamp) carries the framework field name detectionDate; what it marks in "
                 "this stream is not established. On the tested images it ran from minutes to "
                 "24 days after the recorded departure, and from under a second to 20 days "
                 "before the SEGB write. It was within a minute of the SEGB time on 62 of 156 "
                 "written rows. On the tested images arrival preceded departure on all 156 "
                 "written rows, with spans from 2 minutes to 7 days. Neither was compared with "
                 "an independent record. On the tested images coordinates and both accuracy "
                 "values were present on all 156 written rows. Latitude, longitude, horizontal "
                 "accuracy and confidence are stored as doubles and reported rounded (6, 6, 2 "
                 "and 3 decimal places). The unit of the accuracy values was not read from a "
                 "source. Vertical accuracy is reported rounded to two decimal places; what a "
                 "value of -1 means in this stream is not established. Field names and the User "
                 "Specific Place Type names are those of the BMLocationVisit class and its "
                 "BMPlaceInference class, read from BiomeLibrary.framework on macOS 27.2.1 "
                 "(26B131); no iOS copy of the class was read. Arrival and departure are the "
                 "fields the framework names entryDate and exitDate, and Horizontal Accuracy "
                 "and Vertical Accuracy are horizontalUncertainty and verticalUncertainty. Place "
                 "Inference Identifier, reported before as Visit ID, is the identifier of the "
                 "place inference, not of the visit. User Specific Place Type is new, with its "
                 "integer in the (raw) column; on the tested images it was Home on 38 and "
                 "Unknown on 118 of the 156 written rows. Reference: Mattia Epifani, '84 Streams "
                 "Later, Part 2: Inside Apple Biome', "
                 "https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html",
        "paths": ('*/streams/*/Location.Visit/local/*',),
        "output_types": ["html", "tsv", "timeline", "lava", "kml"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "dexter_ios18": "378 rows",
            "hc_ios18_7": "43 rows",
            "hc_ios26": "26.5.2 | 35 rows",
            "iphone14plus_ios18": "3 rows",
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


# userSpecificPlaceType names, read from BiomeLibrary.framework BMPlaceInference on macOS 27.2.1 (26B131).
USER_SPECIFIC_PLACE_TYPE = {0: 'Unknown', 1: 'Home', 2: 'Work', 3: 'School', 4: 'Gym'}


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
                    _to_str(detail.get('4', b'')),
                    USER_SPECIFIC_PLACE_TYPE.get(place.get('3'), '')
                    if isinstance(place.get('3'), int) else '',
                    place.get('3', ''), _to_str(detail.get('1', b'')),
                    _to_str(place.get('1', b'')), filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((None, None, None, ts, record.state.name, None, None, None,
                                  None, None, None, None, None, None, None, None, None, None,
                                  filename,
                                  record.data_start_offset))

    data_headers = (
        ('Arrival Timestamp', 'datetime'), ('Departure Timestamp', 'datetime'),
        ('Detection Date', 'datetime'), ('SEGB Write Timestamp', 'datetime'),
        'SEGB State', ('Latitude', 'latitude'), ('Longitude', 'longitude'), 'Horizontal Accuracy', 'Altitude',
        'Vertical Accuracy', 'Confidence', 'Place Name', 'Place Address', 'Place Category',
        'User Specific Place Type', 'User Specific Place Type (raw)', 'Place ID',
        'Place Inference Identifier', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
