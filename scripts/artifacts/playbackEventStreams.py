__artifacts_v2__ = {
    "playbackEventStreams": {
        "name": "Media Playback Event Streams",
        "description": "Events in the MediaPlaybackCore playback event stream databases found in "
                       "app data containers: the time, the client name, the event type and the "
                       "item or container title an event names.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Music, Video & News",
        "notes": "One row per row of the events table in each Database file inside a .sqlpkg "
                 "folder under com.apple.MediaPlaybackCore.PlaybackEventStreams "
                 "(Library/Application Support of an app's data container) or "
                 "Documents/PlaybackEventStreams; a Database is read only when it has an events "
                 "table. MPCPlaybackEngineEvent and MPCPlaybackEngineEventStream are classes of "
                 "MediaPlaybackCore on macOS 27.2, and the event's initialiser fields match the "
                 "table's columns, but no documentation of this store was found, so the column and "
                 "payload key names are the only labels used here. Client is the .sqlpkg folder "
                 "name without its suffix after the last hyphen. It reads as an app name or bundle "
                 "ID; what it identifies, and which process wrote the file, is not established. "
                 "One container on wilkerson_iphone16_ios26 holds stores for three client names. "
                 "Event Time is userNS read as nanoseconds since 2001 UTC. On macOS 27.2 the "
                 "framework's event date is seconds since 2001; that userNS is that value in "
                 "nanoseconds is not sourced. In all nine tested stores it is within 14 seconds of "
                 "the store's own monotonic clock columns read as Unix time, and read that way the "
                 "last Music event falls on the date in the extraction folder name on all three "
                 "tested images. Event Type is the type column as stored. Item Title, Container "
                 "Title, Item Duration, Item Start Position, Item End Position, Rate Change "
                 "Reason, Queue Description, Application Bundle ID and Session ID are the payload "
                 "JSON keys item-metadata/item-title, container-metadata/container-title, "
                 "item-metadata/item-duration, item-start-position, item-end-position, "
                 "item-rate-change-reason, queue-description, "
                 "queue-reporting-metadata/application-bundle-id and session-id, shown as the "
                 "stored text, numbers included, and empty when the event lacks the key or the "
                 "value is not a single text, number or true/false value; the units of the "
                 "duration and positions are not established. Payload is the whole JSON as stored, "
                 "so every key is kept. On the tested images each store spans from under a second "
                 "to about a week, so a store holds a short window and should not be read as a "
                 "full play history; how long events are kept is not established. "
                 "hill_iphone15pro_ios26 holds 44 rows (Music 23, Podcasts 21), "
                 "wilkerson_iphone16_ios26 153 (Music 18, Podcasts 19, com.apple.mobiletimer 90 "
                 "and two com.apple.AdaptiveMusicApp stores with 13 each) and iphone11_ios17 71 "
                 "(Music 16, com.apple.mobileslideshow 55, both under "
                 "Documents/PlaybackEventStreams). Container Title, Rate Change Reason and "
                 "Application Bundle ID are empty on every row of hill_iphone15pro_ios26. The "
                 "write-ahead log is read with the database: without it, three of the "
                 "wilkerson_iphone16_ios26 stores hold 3, 3 and 72 rows instead of 13, 13 and 90.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/'
                  'com.apple.MediaPlaybackCore.PlaybackEventStreams/*.sqlpkg/Database*',
                  '*/mobile/Containers/Data/Application/*/Documents/PlaybackEventStreams/'
                  '*.sqlpkg/Database*'),
        "output_types": "standard",
        "artifact_icon": "music",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 44 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 153 rows",
            "iphone11_ios17": "iOS 17.3 | 71 rows",
        },
    }
}


import json
import os
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import (artifact_processor, does_table_exist_in_db, get_sqlite_db_records,
                               is_sqlite_sidecar, logfunc)

_EPOCH_2001 = datetime(2001, 1, 1, tzinfo=timezone.utc)


def _time(value):
    '''Nanoseconds since 2001 as UTC; a missing or non-positive value stays blank.'''
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        return ''
    try:
        return _EPOCH_2001 + timedelta(microseconds=value / 1000)
    except OverflowError:
        return ''


def _client(found):
    '''The package folder name without its random suffix: Music-ab12.sqlpkg gives Music.'''
    package = os.path.basename(os.path.dirname(found))
    stem = package[:-len('.sqlpkg')] if package.endswith('.sqlpkg') else package
    return stem.rsplit('-', 1)[0] if '-' in stem else stem


def _get(payload, *keys):
    value = payload
    for key in keys:
        if not isinstance(value, dict):
            return ''
        value = value.get(key)
    if value is None or isinstance(value, (dict, list)):
        return ''
    return value


@artifact_processor
def playbackEventStreams(context):
    data_list, sources = [], []
    for found in sorted(str(path) for path in context.get_files_found()):
        if os.path.basename(found) != 'Database' or is_sqlite_sidecar(found):
            continue
        if not does_table_exist_in_db(found, 'events'):
            continue
        sources.append(found)
        client = _client(found)
        for row in get_sqlite_db_records(
                found, 'SELECT userNS, type, payload FROM events ORDER BY userNS, rowid'):
            payload = {}
            if row[2] is not None:
                try:
                    payload = json.loads(row[2], parse_float=str, parse_int=str)
                except (ValueError, TypeError) as error:
                    logfunc(f'Media Playback Event Streams: could not read a payload in '
                            f'{client}: {error}')
                payload = payload if isinstance(payload, dict) else {}
            data_list.append((
                _time(row[0]), client, '' if row[1] is None else row[1],
                _get(payload, 'item-metadata', 'item-title'),
                _get(payload, 'container-metadata', 'container-title'),
                _get(payload, 'item-metadata', 'item-duration'),
                _get(payload, 'item-start-position'),
                _get(payload, 'item-end-position'),
                _get(payload, 'item-rate-change-reason'),
                _get(payload, 'queue-description'),
                _get(payload, 'queue-reporting-metadata', 'application-bundle-id'),
                _get(payload, 'session-id'),
                '' if row[2] is None else row[2],
            ))
    data_headers = (
        ('Event Time', 'datetime'), 'Client', 'Event Type', 'Item Title', 'Container Title',
        'Item Duration', 'Item Start Position', 'Item End Position', 'Rate Change Reason', 'Queue Description',
        'Application Bundle ID', 'Session ID', 'Payload (as stored)')
    return data_headers, data_list, '\n'.join(sources)
