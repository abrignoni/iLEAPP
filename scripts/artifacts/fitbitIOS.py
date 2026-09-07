__artifacts_v2__ = {
    "fitbit_ios_locations": {
        "name": "Fitbit - Exercise Locations",
        "description": "Parses the GPS points the Fitbit iOS app recorded during exercise, "
                       "with the coordinates, altitude, speed and accuracy of each.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Fitbit",
        "notes": "One row per recorded point. Each point is joined to its session through the "
                 "location group the record names, so a point carries the name and start time of "
                 "the exercise it came from. The timestamp is stored as an eight byte value "
                 "holding a big endian double of seconds since the 2001 Apple epoch, which is "
                 "unusual enough to be worth stating: it is not a plain numeric column. That "
                 "reading is corroborated independently, because the heart rate table in the "
                 "same database stores its own times as ISO text written by a different code "
                 "path and its dates coincide with the span these points cover. All 9,419 points "
                 "on the iOS 17.3 image (iphone11_ios17) decoded to one five day window. "
                 "Interpolated (as stored) is the flag the record carries; its meaning is not "
                 "established here, so a flagged point is not read as an observed one. "
                 "Horizontal and vertical "
                 "accuracy are the values the record carries. Field mapping was done against "
                 "a private sample provided by Mattia; no sample data is recorded for it. Every copy of the database in the extraction is read rather than the first one found, so a device holding more than one app data container reports all of them.",
        "paths": ('*/Documents/fitbit.sqlite*',),
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | 9,419 rows",
            "hickman_ios15": "iOS 15.3.1 | 2,938 rows",
            "hickman_ios14": "iOS 14.3 | 2,642 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
        },
        "output_types": ["html", "tsv", "timeline", "lava", "kml"],
        "artifact_icon": "map-pin"
    },
    "fitbit_ios_activities": {
        "name": "Fitbit - Exercise Sessions",
        "description": "Parses the exercise sessions the Fitbit iOS app logged, with the "
                       "start time, duration, distance and the tracker that recorded them.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Fitbit",
        "notes": "One row per logged session. Start Time uses the same eight byte big endian "
                 "double of seconds since the 2001 Apple epoch as the location points. "
                 "Duration values are seconds. Has GPS is the flag the record carries and "
                 "tells an examiner whether to expect points in the locations artifact for "
                 "that session. Source Name and Source Type are reported as stored. Distance and "
                 "speed are reported as stored, because the record separately carries a unit "
                 "system code and nothing in the extraction maps that code to a unit, so the "
                 "figures are not converted or labelled with a unit here. A stored date far "
                 "outside any plausible range is left empty "
                 "rather than rendered as a first century date. Field mapping was done "
                 "against a private sample provided by Mattia; no sample data is recorded "
                 "for it. Source Name is a column older stores lack: the iOS 13.3.1, 14.3 and "
                 "15.3.1 images carry Source Type and Source ID but no ZSOURCENAME, so the "
                 "column is blank there and the query reads it as NULL rather than failing. "
                 "On the iOS 17.3 image 12 of 27 sessions have no Source Name stored either.",
        "paths": ('*/Documents/fitbit.sqlite*',),
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | 27 rows",
            "hickman_ios15": "iOS 15.3.1 | 21 rows",
            "hickman_ios14": "iOS 14.3 | 22 rows",
            "hickman_ios13": "iOS 13.3.1 | 5 rows",
        },
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "activity"
    },
    "fitbit_ios_heart_rate": {
        "name": "Fitbit - Heart Rate",
        "description": "Parses the heart rate samples the Fitbit iOS app stored, with the "
                       "time and value of each.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Fitbit",
        "notes": "One row per sample. Unlike the location and session times in the same "
                 "database, these are stored as ISO text and are reported as the time they "
                 "state; the text carries no zone, so no conversion is applied. Resolution "
                 "is the value the record carries and is reported as stored. A sample is a "
                 "tracker reading and not a phone location. On the iOS 17.3 image "
                 "(iphone11_ios17) the "
                 "samples were dense, 56,282 of them, so the artifact is large by nature. Field "
                 "mapping was done against a private sample provided by Mattia; no sample data "
                 "is recorded for it. Older stores have no ZMANAGEDHEARTRATE table: the iOS "
                 "13.3.1 and 14.3 images keep per day heart rate rows in ZFBHEARTRATESTAT and "
                 "the 15.3.1 image in ZHEARTRATESTAT, with intraday points archived in keyed "
                 "archive blobs, and this artifact reads none of those, so it reports no rows "
                 "on such stores and logs the skip.",
        "paths": ('*/Documents/fitbit.sqlite*',),
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | 56,282 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
        },
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "heart"
    },
    "fitbit_ios_daily_stats": {
        "name": "Fitbit - Daily Activity Stats",
        "description": "Parses the per day activity totals the Fitbit iOS app stored, "
                       "including steps, distance, floors and active minutes.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Fitbit",
        "notes": "One row per stored day. These are per day totals as stored; how they were "
                 "computed is not established here. Distance is reported as stored for the same "
                 "reason as the "
                 "sessions artifact: the database carries a unit system code that nothing in "
                 "the extraction maps to a unit. Field mapping was done against a private "
                 "sample provided by Mattia; no sample data is recorded for it.",
        "paths": ('*/Documents/fitbit.sqlite*',),
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | 68 rows",
            "hickman_ios15": "iOS 15.3.1 | 45 rows",
            "hickman_ios14": "iOS 14.3 | 54 rows",
            "hickman_ios13": "iOS 13.3.1 | 62 rows",
        },
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "bar-chart-2"
    },
}

import os
import re
import struct
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import (artifact_processor, does_table_exist_in_db, get_sqlite_db_records,
                               logfunc, null_absent_columns)

_COCOA = datetime(2001, 1, 1, tzinfo=timezone.utc)
_FRACTION = re.compile(r'^(.*\.)(\d+)(.*)$')


def _cocoa_blob(value):
    '''An eight byte big endian double of Apple epoch seconds as a UTC datetime, or ''.

    The app stores these dates as a BLOB rather than as a numeric column, so they cannot
    be read with the usual numeric conversion. A value far outside any plausible range is
    the app's own absent marker and yields nothing rather than a first century date.
    '''
    if not isinstance(value, (bytes, bytearray)) or len(value) != 8:
        return _cocoa_number(value)
    try:
        seconds = struct.unpack('>d', bytes(value))[0]
    except (struct.error, ValueError):
        return ''
    return _from_cocoa(seconds)


def _cocoa_number(value):
    '''A numeric Apple epoch value as a UTC datetime, or ''.'''
    try:
        return _from_cocoa(float(value))
    except (TypeError, ValueError):
        return ''


def _from_cocoa(seconds):
    '''Apple epoch seconds as a UTC datetime, bounded to a plausible range.'''
    if not seconds:
        return ''
    # Roughly 1990 to 2100. Outside that the value is a sentinel, not a date.
    if seconds < -347155200 or seconds > 3124137600:
        return ''
    try:
        return _COCOA + timedelta(seconds=seconds)
    except (OverflowError, ValueError):
        return ''


def _iso(value):
    '''An ISO text timestamp as a datetime, or '' when it does not parse.

    The fraction is trimmed to six digits before parsing, because releases before 3.11
    accept only three or six.
    '''
    if not value or not isinstance(value, str):
        return ''
    text = value.strip().replace('Z', '+00:00')
    match = _FRACTION.match(text)
    if match:
        text = f'{match.group(1)}{match.group(2)[:6]:0<6}{match.group(3)}'
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return ''


def _text(value):
    '''A stored value as text, with a stored null read as absent.'''
    return '' if value is None else str(value)


def _databases(files_found):
    '''Every copy of the app's database among the matched files.

    Returned as a list rather than as one path, because a device can hold more than one
    app data container and taking the first match silently drops the rest.
    '''
    seen = []
    for found in files_found:
        path = str(found)
        if os.path.basename(path) == 'fitbit.sqlite' and path not in seen:
            seen.append(path)
    return seen


def _rows(path, statement):
    '''The rows a statement returns, or nothing when the table is absent.

    Columns the store lacks are read as NULL, because older releases of the app wrote
    fewer columns and a query naming one of them would otherwise return nothing at all.
    '''
    try:
        return list(get_sqlite_db_records(path, null_absent_columns(path, statement)))
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'Fitbit: could not read from fitbit.sqlite: {error}')
        return []


def _sessions(path):
    '''{activity log key: (name, start time)} for the logged exercise sessions.'''
    index = {}
    for key, name, start in _rows(path, 'SELECT Z_PK, ZNAME, ZSTARTTIME FROM ZFBACTIVITYLOG'):
        index[key] = (_text(name), _cocoa_blob(start))
    return index


@artifact_processor
def fitbit_ios_locations(context):
    data_list = []
    sources = _databases(context.get_files_found())
    if not sources:
        return (), [], ''

    for source_path in sources:
        sessions = _sessions(source_path)
        groups = dict(_rows(source_path, 'SELECT Z_PK, ZACTIVITYLOG FROM ZFBLOCATIONGROUP'))
        for row in _rows(source_path, """
                SELECT ZTIMESTAMP, ZLATITUDE, ZLONGITUDE, ZALTITUDE, ZSPEED, ZPACE, ZCOURSE,
                       ZHORIZONTALACCURACY, ZVERTICALACCURACY, ZINTERPOLATED, ZACTIVE,
                       ZCUMULATIVEACTIVEDISTANCE, ZCUMULATIVEACTIVEDURATION,
                       ZCUMULATIVEACTIVECALORIES, ZLOCATIONGROUP
                FROM ZFBLOCATION"""):
            (stamp, latitude, longitude, altitude, speed, pace, course, horizontal,
             vertical, interpolated, active, distance, duration, calories, group_key) = row
            name, start = sessions.get(groups.get(group_key), ('', ''))
            data_list.append((
                _cocoa_blob(stamp), _text(latitude), _text(longitude), name, start,
                _text(altitude), _text(speed), _text(pace), _text(course),
                _text(horizontal), _text(vertical), _text(interpolated), _text(active),
                _text(distance), _text(duration), _text(calories), _text(group_key),
            ))

    data_list.sort(key=lambda r: str(r[0]))

    data_headers = (
        ('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Exercise',
        ('Exercise Start', 'datetime'), 'Altitude', 'Speed (as stored)',
        'Pace (as stored)', 'Course (as stored)', 'Horizontal Accuracy',
        'Vertical Accuracy', 'Interpolated (as stored)', 'Active (as stored)',
        'Cumulative Distance (as stored)', 'Cumulative Duration (as stored)',
        'Cumulative Calories (as stored)', 'Location Group',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def fitbit_ios_activities(context):
    data_list = []
    sources = _databases(context.get_files_found())
    if not sources:
        return (), [], ''

    for source_path in sources:
        for row in _rows(source_path, """
                SELECT ZSTARTTIME, ZNAME, ZDURATIONACTIVE, ZDURATIONOVERALL, ZDISTANCE,
                       ZSTEPS, ZCALORIES, ZAVERAGEHEARTRATE, ZELEVATIONGAIN, ZSPEED,
                       ZACTIVEMINUTES, ZAZMTOTALMINUTES, ZHASGPS, ZINPROGRESS, ZSOURCENAME,
                       ZSOURCETYPE, ZSOURCEID, ZLOGTYPE, ZLASTMODIFIED, ZLOGID
                FROM ZFBACTIVITYLOG"""):
            (start, name, active, overall, distance, steps, calories, heart_rate,
             elevation, speed, active_minutes, zone_minutes, has_gps, in_progress,
             source_name, source_type, source_id, log_type, modified, log_id) = row
            data_list.append((
                _cocoa_blob(start), _text(name), _text(overall), _text(active),
                _text(distance), _text(steps), _text(calories), _text(heart_rate),
                _text(elevation), _text(speed), _text(active_minutes), _text(zone_minutes),
                _text(has_gps), _text(in_progress), _text(source_name), _text(source_type),
                _text(source_id), _text(log_type), _cocoa_number(modified), _text(log_id),
            ))

    data_list.sort(key=lambda r: str(r[0]), reverse=True)

    data_headers = (
        ('Start Time', 'datetime'), 'Exercise', 'Duration Overall (seconds)',
        'Duration Active (seconds)', 'Distance (as stored)', 'Steps', 'Calories',
        'Average Heart Rate', 'Elevation Gain (as stored)', 'Speed (as stored)',
        'Active Minutes', 'Active Zone Minutes', 'Has GPS (as stored)',
        'In Progress (as stored)', 'Source Name', 'Source Type (as stored)', 'Source ID',
        'Log Type (as stored)', ('Last Modified', 'datetime'), 'Log ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def fitbit_ios_heart_rate(context):
    data_list = []
    sources = _databases(context.get_files_found())
    if not sources:
        return (), [], ''

    for source_path in sources:
        if not does_table_exist_in_db(source_path, 'ZMANAGEDHEARTRATE'):
            logfunc('Fitbit: no ZMANAGEDHEARTRATE table in fitbit.sqlite; older stores keep heart '
                    'rate in per day stat tables, which this artifact does not read')
            continue
        for stamp, value, resolution, identifier in _rows(
                source_path,
                'SELECT ZDATETIME, ZVALUE, ZRESOLUTION, ZID FROM ZMANAGEDHEARTRATE'):
            data_list.append((_iso(stamp) or _text(stamp), _text(value),
                              _text(resolution), _text(identifier)))

    data_list.sort(key=lambda r: str(r[0]), reverse=True)

    data_headers = (
        ('Timestamp', 'datetime'), 'Heart Rate', 'Resolution (as stored)', 'Record ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def fitbit_ios_daily_stats(context):
    data_list = []
    sources = _databases(context.get_files_found())
    if not sources:
        return (), [], ''

    for source_path in sources:
        for row in _rows(source_path, """
                SELECT ZDAY, ZSTEPS, ZDISTANCE, ZFLOORS, ZCALORIES, ZMINUTESVERYACTIVE,
                       ZMINUTESFAIRLYACTIVE, ZISDEFLATED
                FROM ZFBACTIVITYSTAT2"""):
            day, steps, distance, floors, calories, very, fairly, deflated = row
            data_list.append((
                _cocoa_blob(day) or _cocoa_number(day), _text(steps), _text(distance),
                _text(floors), _text(calories), _text(very), _text(fairly), _text(deflated),
            ))

    data_list.sort(key=lambda r: str(r[0]), reverse=True)

    data_headers = (
        ('Day', 'datetime'), 'Steps', 'Distance (as stored)', 'Floors', 'Calories',
        'Minutes Very Active', 'Minutes Fairly Active', 'Deflated (as stored)',
    )
    return data_headers, data_list, '\n'.join(sources)
