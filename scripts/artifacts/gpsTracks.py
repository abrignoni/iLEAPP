__artifacts_v2__ = {
    "gps_tracks_ios_tracks": {
        "name": "GPS Tracks - Tracks",
        "description": "Tracks recorded in the GPS Tracks app, with the date, distance and duration "
                       "each one stores.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "GPS Tracks",
        "notes": "One row per row of ZTRACK and of ZCURRENTTRACK in Library/GPS_Tracks.sqlite, "
                 "told apart by the Source Table column. ZCURRENTTRACK is a separate table; on "
                 "the tested image its row carried a later date than any saved track and no "
                 "points of its own, and whether it records the recording the app had open is "
                 "not established. Date, Sync Date and the point times are Core Data seconds "
                 "since 2001 and are rendered in UTC. Distance, Time, Calories and Type are "
                 "reported as stored: the store carries no unit for the first three and nothing "
                 "available maps the type number to a meaning, so none is given here. Track ID "
                 "is the identifier the app assigns, and the same identifier names the per track "
                 "files under Library/Assets, so a track row can be tied to those files by name. "
                 "Saved and Recovered come from ZCURRENTTRACK only and are blank for a saved "
                 "track. Notes and Favorite (as stored) held no value on any row of the tested "
                 "image.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/GPS_Tracks.sqlite*',),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "map",
        "sample_data": {
            "otto_ios17": "iOS 17.5.1 | GPS Tracks | 4 rows",
        },
    },
    "gps_tracks_ios_points": {
        "name": "GPS Tracks - Track Points",
        "description": "Points recorded along GPS Tracks tracks, with coordinates, altitude, speed "
                       "and heading.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "GPS Tracks",
        "notes": "One row per row of ZCOURSEPOINT. Every one of the 170,418 points on the tested "
                 "image carried a latitude and a longitude, and they fell between 2024-05-12 and "
                 "2024-07-06. Track Name is joined from the track the point names, so a point "
                 "whose track row is gone still reports its coordinates with the name left blank. "
                 "Speed, Average Speed, Distance, Distance Elapsed, Course, True Heading, "
                 "Magnetic Heading and Glide Ratio are reported as stored, because the store "
                 "carries no unit for any of them. Heart Rate is a column of this table and held "
                 "no value on any row of the tested image; it is kept because the store defines "
                 "it. This table is large, 170,418 rows on the tested image, so the artifact is "
                 "correspondingly "
                 "large. A separate table, ZSPEEDALTITUDEPOINT, holds a second series of 253,819 "
                 "rows carrying only a date, a speed and an altitude with no coordinates; it is "
                 "not reported here because the points in this artifact already carry speed and "
                 "altitude and those rows cannot be placed on a map.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/GPS_Tracks.sqlite*',),
        "output_types": ["html", "tsv", "timeline", "lava", "kml"],
        "artifact_icon": "navigation",
        "sample_data": {
            "otto_ios17": "iOS 17.5.1 | GPS Tracks | 170,418 rows",
        },
    },
    "gps_tracks_ios_waypoints": {
        "name": "GPS Tracks - Waypoints",
        "description": "Waypoints held in the GPS Tracks app, with the name, note and address where "
                       "the row carries them.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "GPS Tracks",
        "notes": "One row per row of ZWAYPOINT and of ZTRACKPOINT, told apart by the Source Table "
                 "column. ZWAYPOINT rows stand on their own and ZTRACKPOINT rows name a track, so "
                 "the second kind marks a position along a recorded track. Both carry a name, a "
                 "note, an address and an alert radius in the same shape, and all twelve rows on "
                 "the tested image carried coordinates and eleven of them carried a name. Sync Date "
                 "held no value on any of the twelve. Address is the text the row holds and is "
                 "not resolved here; it was present on one row of the tested image and blank on "
                 "the rest, so a blank address is not evidence about where the point is. Alert "
                 "Radius, Position and Type are reported as stored. A waypoint records a place "
                 "the app held, which is not by itself evidence that the device was there; the "
                 "row does not record how the waypoint was created.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/GPS_Tracks.sqlite*',),
        "output_types": ["html", "tsv", "timeline", "lava", "kml"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "otto_ios17": "iOS 17.5.1 | GPS Tracks | 12 rows",
        },
    },
}

import os
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import (artifact_processor, does_table_exist_in_db, get_sqlite_db_records,
                               logfunc)

_STORE_NAME = 'GPS_Tracks.sqlite'
_CORE_DATA_EPOCH_UTC = datetime(2001, 1, 1, tzinfo=timezone.utc)


def _stores(files_found):
    '''Every GPS Tracks database among the matched files, directories skipped.'''
    seen = []
    for found in files_found:
        path = str(found)
        if os.path.isdir(path):
            continue
        if os.path.basename(path) == _STORE_NAME and path not in seen:
            seen.append(path)
    return seen


def _rows(path, table, columns):
    '''Rows of a table, or nothing when the store does not have it.'''
    if not does_table_exist_in_db(path, table):
        logfunc(f'GPS Tracks: {table} is not in this GPS_Tracks.sqlite')
        return []
    try:
        return list(get_sqlite_db_records(path, f'SELECT {columns} FROM {table}'))
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'GPS Tracks: could not read {table}: {error}')
        return []


def _text(value):
    '''A stored value as text, with a stored null read as absent.'''
    return '' if value is None else str(value)


def _core_data_to_utc(value):
    '''Core Data seconds since 2001-01-01 to an aware UTC datetime, or ''.'''
    if value in (None, ''):
        return ''
    try:
        return _CORE_DATA_EPOCH_UTC + timedelta(seconds=float(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _track_names(path):
    '''{ZTRACK row id: track name} so a point can report the track it belongs to.'''
    names = {}
    for row_id, name in _rows(path, 'ZTRACK', 'Z_PK, ZNAME'):
        names[row_id] = _text(name)
    return names


@artifact_processor
def gps_tracks_ios_tracks(context):
    data_list = []
    sources = _stores(context.get_files_found())

    for source_path in sources:
        for (row_id, date, sync_date, name, notes, distance, elapsed, calories, kind,
             unique_id, favorite) in _rows(
                source_path, 'ZTRACK',
                'Z_PK, ZDATE, ZSYNCDATE, ZNAME, ZNOTES, ZDISTANCE, ZTIME, ZCALORIES, ZTYPE, '
                'ZUNIQUEID, ZFAVORITE'):
            data_list.append((
                _core_data_to_utc(date), _text(name), _text(notes), _text(distance),
                _text(elapsed), _text(calories), _text(kind), _text(favorite), '', '',
                _core_data_to_utc(sync_date), _text(unique_id), 'ZTRACK', _text(row_id),
            ))
        for (row_id, date, sync_date, name, notes, distance, elapsed, calories, kind,
             unique_id, saved, recovered) in _rows(
                source_path, 'ZCURRENTTRACK',
                'Z_PK, ZDATE, ZSYNCDATE, ZNAME, ZNOTES, ZDISTANCE, ZTIME, ZCALORIES, ZTYPE, '
                'ZUNIQUEID, ZSAVED, ZRECOVERED'):
            data_list.append((
                _core_data_to_utc(date), _text(name), _text(notes), _text(distance),
                _text(elapsed), _text(calories), _text(kind), '', _text(saved),
                _text(recovered), _core_data_to_utc(sync_date), _text(unique_id),
                'ZCURRENTTRACK', _text(row_id),
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)

    data_headers = (
        ('Date', 'datetime'), 'Track Name', 'Notes', 'Distance (as stored)',
        'Time (as stored)', 'Calories (as stored)', 'Type (as stored)', 'Favorite (as stored)',
        'Saved (as stored)', 'Recovered (as stored)', ('Sync Date', 'datetime'), 'Track ID',
        'Source Table', 'Row ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def gps_tracks_ios_points(context):
    data_list = []
    sources = _stores(context.get_files_found())

    for source_path in sources:
        names = _track_names(source_path)
        for (row_id, date, latitude, longitude, altitude, speed, average_speed, course,
             distance, elapsed, true_heading, magnetic_heading, heading_accuracy,
             horizontal_accuracy, vertical_accuracy, glide_ratio, heart_rate, track) in _rows(
                source_path, 'ZCOURSEPOINT',
                'Z_PK, ZDATE, ZLATITUDE, ZLONGITUDE, ZALTITUDE, ZSPEED, ZAVERAGESPEED, ZCOURSE, '
                'ZDISTANCE, ZTIMEELAPSED, ZTRUEHEADING, ZMAGNETICHEADING, ZHEADINGACCURACY, '
                'ZHORIZONTALACCURACY, ZVERTICALACCURACY, ZGLIDERATIO, ZHEARTRATE, ZTRACK'):
            data_list.append((
                _core_data_to_utc(date), _text(latitude), _text(longitude),
                names.get(track, ''), _text(altitude), _text(speed), _text(average_speed),
                _text(course), _text(distance), _text(elapsed), _text(true_heading),
                _text(magnetic_heading), _text(heading_accuracy), _text(horizontal_accuracy),
                _text(vertical_accuracy), _text(glide_ratio), _text(heart_rate),
                _text(track), _text(row_id),
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)

    data_headers = (
        ('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Track Name', 'Altitude',
        'Speed (as stored)', 'Average Speed (as stored)', 'Course (as stored)',
        'Distance (as stored)', 'Distance Elapsed (as stored)', 'True Heading (as stored)',
        'Magnetic Heading (as stored)', 'Heading Accuracy', 'Horizontal Accuracy',
        'Vertical Accuracy', 'Glide Ratio (as stored)', 'Heart Rate (as stored)',
        'Track Row ID', 'Row ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def gps_tracks_ios_waypoints(context):
    data_list = []
    sources = _stores(context.get_files_found())

    for source_path in sources:
        names = _track_names(source_path)
        for (row_id, date, sync_date, latitude, longitude, altitude, name, notes, address,
             radius, position, kind, unique_id) in _rows(
                source_path, 'ZWAYPOINT',
                'Z_PK, ZDATE, ZSYNCDATE, ZLATITUDE, ZLONGITUDE, ZALTITUDE, ZNAME, ZNOTES, '
                'ZADDRESS, ZALERTRADIUS, ZPOSITION, ZTYPE, ZUNIQUEID'):
            data_list.append((
                _core_data_to_utc(date), _text(latitude), _text(longitude), _text(name),
                _text(notes), _text(address), '', _text(altitude), _text(radius),
                _text(position), _text(kind), _core_data_to_utc(sync_date), _text(unique_id),
                'ZWAYPOINT', _text(row_id),
            ))
        for (row_id, date, sync_date, latitude, longitude, altitude, name, notes, address,
             position, unique_id, track) in _rows(
                source_path, 'ZTRACKPOINT',
                'Z_PK, ZDATE, ZSYNCDATE, ZLATITUDE, ZLONGITUDE, ZALTITUDE, ZNAME, ZNOTES, '
                'ZADDRESS, ZPOSITION, ZUNIQUEID, ZTRACK'):
            data_list.append((
                _core_data_to_utc(date), _text(latitude), _text(longitude), _text(name),
                _text(notes), _text(address), names.get(track, ''), _text(altitude), '',
                _text(position), '', _core_data_to_utc(sync_date), _text(unique_id),
                'ZTRACKPOINT', _text(row_id),
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)

    data_headers = (
        ('Date', 'datetime'), 'Latitude', 'Longitude', 'Name', 'Notes', 'Address',
        'Track Name', 'Altitude', 'Alert Radius (as stored)', 'Position (as stored)',
        'Type (as stored)', ('Sync Date', 'datetime'), 'Waypoint ID', 'Source Table', 'Row ID',
    )
    return data_headers, data_list, '\n'.join(sources)
