__artifacts_v2__ = {
    "life360DeviceLocationSamples": {
        "name": "Life360 - Device Location Samples",
        "description": "Location samples Life360 stored in its DeviceLocationTopic event store, one row per "
                       "buffered sample, with the sample time, coordinates, altitude, speed, course and "
                       "accuracy values as stored.",
        "author": '@CyberMike81, Claude, OpenAI Codex',
        "creation_date": "2026-10-21",
        "last_update_date": "2026-10-22",
        "requirements": "none",
        "category": "Life360",
        "notes": 'Read from ZENTRY in com.life360.DeviceLocationTopic.sqlite. One row per element of the '
                 'bufferedSamples array of each entry, falling back to its location object when the array is '
                 'empty. Sample Time is the sample timestamp (Cocoa seconds); Logged Time is ZTIMESTAMP (Unix '
                 'seconds). Location values are as stored; the store records no units. Sample Origin is the key '
                 'of the stored sampleOrigin object. On the tested image Sample Origin held locationEngine, '
                 'Server Tag held undefined, and Simulated By Software and Produced By Accessory held No on '
                 'every row. The table held 109 entries covering 27 minutes on the tested image; whether the app '
                 'trims older entries is not established. A row shows the app stored the sample; it does not '
                 'show who carried the device. Other EventKit topics (transactiontopic, structuredLogTopic, '
                 'systemEventTopic, systemErrorTopic, systemRequestTopic, observabilityDataTopic, '
                 'PowerModeTopic, PowerTopic, SRTTopic, MemberWakeTopic, TakeoffTopic, FlightTopic) are not '
                 'parsed. Times render in UTC. Tested on Life360 26.34.0.5 (iOS 18.6); other versions may '
                 'differ. Reads only the main app container (container identifier com.life360.safetymap); '
                 'extension containers and iTunes backups are not read, and skipped files are named in the run '
                 'log. Only the live database with its WAL applied is read; older records left in the main '
                 'database file are not recovered.',
        "paths": ('*/Library/Application Support/com.eventkit/com.life360.DeviceLocationTopic/com.life360.DeviceLocationTopic.sqlite*',
                  '*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Life360 23.19.0 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Life360 24.34.0 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360 23.43.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Life360 24.28.0 | 0 rows",
        },
    },
    "life360FailedLocations": {
        "name": "Life360 - Failed Location Reports",
        "description": "Entries Life360 stored in its FailedLocationTopic event store, each carrying a location object "
                       "with the device battery level and state, Wi-Fi state, SSID, BSSID and drive detection status "
                       "recorded alongside it.",
        "author": '@CyberMike81, Claude, OpenAI Codex',
        "creation_date": "2026-10-21",
        "last_update_date": "2026-10-22",
        "requirements": "none",
        "category": "Life360",
        "notes": 'Read from ZENTRY in com.life360.AwarenessEngine.Topics.FailedLocationTopic.sqlite. What the '
                 'app means by a failed location is not established; the topic name is the only label. Location '
                 'Time is location.timestamp (Cocoa seconds); Logged Time is ZTIMESTAMP (Unix seconds). Values '
                 'are as stored. On the tested image Battery Level and Battery State held -100 and unknown, SSID '
                 'and BSSID were empty, Speed held 0, Wi-Fi Enabled held No and Drive Detection Status held OFF '
                 'on every row. Server Tag had no value on any row of felix_ios17 or iphone11_ios17 (Life360 '
                 '24.x). Times render in UTC. Tested on Life360 26.34.0.5 (iOS 18.6); other versions may differ. '
                 'Reads only the main app container (container identifier com.life360.safetymap); extension '
                 'containers and iTunes backups are not read, and skipped files are named in the run log. Only '
                 'the live database with its WAL applied is read; older records left in the main database file '
                 'are not recovered.',
        "paths": ('*/Library/Application Support/com.eventkit/com.life360.AwarenessEngine.Topics.FailedLocationTopic/com.life360.AwarenessEngine.Topics.FailedLocationTopic.sqlite*',
                  '*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "all",
        "artifact_icon": "map-pin-off",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Life360 23.19.0 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Life360 24.34.0 | 12 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360 23.43.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Life360 24.28.0 | 3 rows",
        },
    },
    "life360MovementEvents": {
        "name": "Life360 - Movement Events",
        "description": 'Drive and trip events Life360 stored in its topic stores and trip-start preferences dictionary, with '
                 'stored event labels, times, identifiers, coordinates, summary values and place fields.',
        "author": '@CyberMike81, Claude, OpenAI Codex',
        "creation_date": "2026-10-21",
        "last_update_date": "2026-10-22",
        "requirements": "none",
        "category": "Life360",
        "notes": 'Read from the drive_session, DriveEvent, trip_session, DriveCancellationTopic and '
                 'TripCancellationTopic stores and the DriveEventPublishingComponent.tripStartTimes dictionary '
                 'in com.life360.safetymap.plist. Kind is drive or trip, from the source store. Event Type is '
                 'the stored eventType (start, update and end seen); cancellation rows show cancel with the '
                 'stored reason in Reason. Event Time is drive.timestamp or the trip currentTimestamp (Cocoa '
                 'seconds), or the timestamp of a cancellation row or plist trip start (Unix seconds). Start '
                 'Time and End Time are Cocoa seconds. Plist rows carry only a trip ID and a start time; on the '
                 'tested image they reached back months before the event stores. drive_session and DriveEvent '
                 'held the same six trips on the tested image; both are shown. Distance, speed and score are as '
                 'stored, without units, and appeared only on end events in the tested image. Start Place and '
                 'End Place join the name and address fields of the first stored place entry. Waypoints and '
                 'incidents are in their own artifacts. Times render in UTC. Tested on Life360 26.34.0.5 (iOS '
                 '18.6); other versions may differ. Reads only the main app container (container identifier '
                 'com.life360.safetymap); extension containers and iTunes backups are not read, and skipped '
                 'files are named in the run log. Only the live database with its WAL applied is read; older '
                 'records left in the main database file are not recovered.',
        "paths": ('*/Library/Application Support/com.eventkit/com.life360.event_history_core.topics.drive_session/com.life360.event_history_core.topics.drive_session.sqlite*',
                  '*/Library/Application Support/com.eventkit/com.life360.L360Driving.Topics.DriveEvent/com.life360.L360Driving.Topics.DriveEvent.sqlite*',
                  '*/Library/Application Support/com.eventkit/com.life360.event_history_core.topics.trip_session/com.life360.event_history_core.topics.trip_session.sqlite*',
                  '*/Library/Application Support/com.eventkit/com.life360.AwarenessEngine.Topics.DriveCancellationTopic/com.life360.AwarenessEngine.Topics.DriveCancellationTopic.sqlite*',
                  '*/Library/Application Support/com.eventkit/com.life360.AwarenessEngine.Topics.TripCancellationTopic/com.life360.AwarenessEngine.Topics.TripCancellationTopic.sqlite*',
                  '*/Library/Preferences/com.life360.safetymap.plist',
                  '*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "all",
        "artifact_icon": "car",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Life360 23.19.0 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Life360 24.34.0 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360 23.43.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Life360 24.28.0 | 0 rows",
        },
    },
    "life360MovementWaypoints": {
        "name": "Life360 - Movement Waypoints",
        "description": 'Distinct decoded waypoint and route-point objects Life360 stored in drive and trip events, retaining '
                 'differing point attributes and the records that contributed each point.',
        "author": '@CyberMike81, Claude, OpenAI Codex',
        "creation_date": "2026-10-21",
        "last_update_date": "2026-10-22",
        "requirements": "none",
        "category": "Life360",
        "notes": 'Read from the drive waypoints in the drive_session and DriveEvent stores and the route points '
                 'in trip_session. Waypoint Time is Unix seconds for drive waypoints and Cocoa seconds for trip '
                 'route points. Values are as stored, without units. An identical point within one container and '
                 'trip or session is shown once; Occurrences, Stores, Source Files and Contributing Records show '
                 'where it appeared, and Point Data holds the point as stored. Source Files and Stores matched '
                 'one to one on the tested image; Source Files keeps containers apart. Times render in UTC. '
                 'Tested on Life360 26.34.0.5 (iOS 18.6); other versions may differ. Reads only the main app '
                 'container (container identifier com.life360.safetymap); extension containers and iTunes '
                 'backups are not read, and skipped files are named in the run log. Only the live database with '
                 'its WAL applied is read; older records left in the main database file are not recovered.',
        "paths": ('*/Library/Application Support/com.eventkit/com.life360.event_history_core.topics.drive_session/com.life360.event_history_core.topics.drive_session.sqlite*',
                  '*/Library/Application Support/com.eventkit/com.life360.L360Driving.Topics.DriveEvent/com.life360.L360Driving.Topics.DriveEvent.sqlite*',
                  '*/Library/Application Support/com.eventkit/com.life360.event_history_core.topics.trip_session/com.life360.event_history_core.topics.trip_session.sqlite*',
                  '*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "all",
        "artifact_icon": "route",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Life360 23.19.0 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Life360 24.34.0 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360 23.43.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Life360 24.28.0 | 0 rows",
        },
    },
    "life360DrivingIncidents": {
        "name": "Life360 - Driving Incidents",
        "description": "The drivingIncidents entries Life360 stored inside its drive session events, with the "
                       "incident time, type and coordinates as stored.",
        "author": '@CyberMike81, Claude, OpenAI Codex',
        "creation_date": "2026-10-21",
        "last_update_date": "2026-10-22",
        "requirements": "none",
        "category": "Life360",
        "notes": 'Read from drive.drivingIncidents in the drive_session and DriveEvent stores. Incident Time is '
                 'Unix seconds. Type is as stored (distractedDriving was the only value on the tested image); '
                 'what the driving SDK counts as an incident is not established. An identical incident within '
                 'one container and trip is shown once, and Event IDs lists every enclosing drive ID. On the '
                 'tested image Stores held the same pair of stores and Occurrences held 2 on every row. Incident '
                 'Data holds the incident as stored. Crash Count in Driver Reports comes from a different store. '
                 'Times render in UTC. Tested on Life360 26.34.0.5 (iOS 18.6); other versions may differ. Reads '
                 'only the main app container (container identifier com.life360.safetymap); extension containers '
                 'and iTunes backups are not read, and skipped files are named in the run log. Only the live '
                 'database with its WAL applied is read; older records left in the main database file are not '
                 'recovered.',
        "paths": ('*/Library/Application Support/com.eventkit/com.life360.event_history_core.topics.drive_session/com.life360.event_history_core.topics.drive_session.sqlite*',
                  '*/Library/Application Support/com.eventkit/com.life360.L360Driving.Topics.DriveEvent/com.life360.L360Driving.Topics.DriveEvent.sqlite*',
                  '*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "all",
        "artifact_icon": "alert-triangle",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Life360 23.19.0 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Life360 24.34.0 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360 23.43.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Life360 24.28.0 | 0 rows",
        },
    },
    "life360DwellEvents": {
        "name": "Life360 - Dwell Events",
        "description": 'Dwell-labelled event documents Life360 stored in its dwell topics, with stored state labels, time '
                 'windows, coordinates, place fields and contributing source records.',
        "author": '@CyberMike81, Claude, OpenAI Codex',
        "creation_date": "2026-10-21",
        "last_update_date": "2026-10-22",
        "requirements": "none",
        "category": "Life360",
        "notes": 'Read from the dwell_session and DwellTopic stores. Event Type (start, update and end seen) and '
                 'State (dwelling and moving seen) are as stored. Event Time is dwell.timestamp (Cocoa seconds); '
                 'Dwell Start and Dwell End are location.startTime and endTime (Unix seconds); Logged Time is '
                 'ZTIMESTAMP (Unix seconds). Only identical documents with the same Logged Time are merged. '
                 'Event Data holds the document as stored. On the tested image Displayable Place and Inferred '
                 'Place were identical, Algorithm held one value and Occurrences held 1 on every row. The labels '
                 'do not establish a stationary period. Times render in UTC. Tested on Life360 26.34.0.5 (iOS '
                 '18.6); other versions may differ. Reads only the main app container (container identifier '
                 'com.life360.safetymap); extension containers and iTunes backups are not read, and skipped '
                 'files are named in the run log. Only the live database with its WAL applied is read; older '
                 'records left in the main database file are not recovered.',
        "paths": ('*/Library/Application Support/com.eventkit/com.life360.event_history_core.topics.dwell_session/com.life360.event_history_core.topics.dwell_session.sqlite*',
                  '*/Library/Application Support/com.eventkit/com.life360.AwarenessEngine.Topics.DwellTopic/com.life360.AwarenessEngine.Topics.DwellTopic.sqlite*',
                  '*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "all",
        "artifact_icon": "home",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Life360 23.19.0 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Life360 24.34.0 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360 23.43.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Life360 24.28.0 | 0 rows",
        },
    },
    "life360GeofenceBreaches": {
        "name": "Life360 - Geofence Breaches",
        "description": 'BreachTopic documents Life360 stored, one row per stored place element with its direction, '
                 'fence-distance value and accompanying location object.',
        "author": '@CyberMike81, Claude, OpenAI Codex',
        "creation_date": "2026-10-21",
        "last_update_date": "2026-10-22",
        "requirements": "none",
        "category": "Life360",
        "notes": 'Read from ZENTRY in com.life360.AwarenessEngine.Topics.BreachTopic.sqlite. One row per stored '
                 'place; an entry with no places gives one row so its location is kept. Event Time is the entry '
                 'timestamp, or ZTIMESTAMP when the entry has none (Unix seconds); Location Time is '
                 'location.timestamp (Cocoa seconds). Direction and Algorithm are as stored (egress and CLPv1 '
                 'seen). How the app decides a breach is not established. On Life360 24.x a second BreachTopic '
                 'store sits in the com.life360.safetymap.sidecar-lpse extension container, which is not read; '
                 'it was empty on felix_ios17 and iphone11_ios17. Times render in UTC. Tested on Life360 '
                 '26.34.0.5 (iOS 18.6); other versions may differ. Reads only the main app container (container '
                 'identifier com.life360.safetymap); extension containers and iTunes backups are not read, and '
                 'skipped files are named in the run log. Only the live database with its WAL applied is read; '
                 'older records left in the main database file are not recovered.',
        "paths": ('*/Library/Application Support/com.eventkit/com.life360.AwarenessEngine.Topics.BreachTopic/com.life360.AwarenessEngine.Topics.BreachTopic.sqlite*',
                  '*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "all",
        "artifact_icon": "circle-dashed",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Life360 23.19.0 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Life360 24.34.0 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360 23.43.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Life360 24.28.0 | 0 rows",
        },
    },
    "life360ActivityModality": {
        "name": "Life360 - Activity Modality",
        "description": "Activity recognition events Life360 stored in its active_modality event store, with the "
                       "modality and confidence the app assigned and the location sample carried in the event.",
        "author": '@CyberMike81, Claude, OpenAI Codex',
        "creation_date": "2026-10-21",
        "last_update_date": "2026-10-22",
        "requirements": "none",
        "category": "Life360",
        "notes": 'Read from ZENTRY in com.life360.activity_recognition.topics.active_modality.sqlite. Modality, '
                 'Confidence and Raw Event Type are as stored (driving and unknown; low, medium and high; '
                 'modalityLocation and driveEvent seen). Event Time is rawEvent.timestamp, or the entry '
                 'timestamp when absent; Logged Time is ZTIMESTAMP; both are Unix seconds and were equal on the '
                 'tested image except on 14 of 562 entries, where they differed by under 0.004 seconds. Location '
                 'Time is Cocoa seconds, from rawEvent.location or, for driveEvent rows, rawEvent.drive. How the '
                 'app derives the modality is not established. Times render in UTC. Tested on Life360 26.34.0.5 '
                 '(iOS 18.6); other versions may differ. Reads only the main app container (container identifier '
                 'com.life360.safetymap); extension containers and iTunes backups are not read, and skipped '
                 'files are named in the run log. Only the live database with its WAL applied is read; older '
                 'records left in the main database file are not recovered.',
        "paths": ('*/Library/Application Support/com.eventkit/com.life360.activity_recognition.topics.active_modality/com.life360.activity_recognition.topics.active_modality.sqlite*',
                  '*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "all",
        "artifact_icon": "activity",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Life360 23.19.0 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Life360 24.34.0 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360 23.43.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Life360 24.28.0 | 0 rows",
        },
    },
}

import base64
import json
import os

from scripts.ilapfuncs import artifact_processor, get_plist_file_content, logfunc
from scripts.life360_common import (get_life360_files, read_life360_rows, seconds_to_utc,
                                   stored_dict, stored_list)

_JSON_ERRORS = (json.JSONDecodeError, TypeError, ValueError, UnicodeDecodeError)
_TRIP_START_KEY = 'DriveEventPublishingComponent.tripStartTimes'


def _cocoa(value):
    return seconds_to_utc(value, 2001)


def _unix(value):
    return seconds_to_utc(value, 1970)


def _enum(value):
    """The single key of a {key: {}} object, or the string itself, as stored."""
    if isinstance(value, dict):
        if len(value) == 1:
            return next(iter(value))
        return json.dumps(value, sort_keys=True)
    if value is None:
        return ''
    return value


def _get(obj, *keys):
    for key in keys:
        if not isinstance(obj, dict):
            if obj is not None:
                logfunc(f'Life360 nested field {".".join(keys)} was not an object; value left blank')
            return None
        obj = obj.get(key)
    return obj


def _as_stored(value):
    return '' if value is None else value


def _bool(value):
    if value is True:
        return 'Yes'
    if value is False:
        return 'No'
    return _as_stored(value)


def _coords(loc):
    return _as_stored(_get(loc, 'coordinate', 'latitude')), _as_stored(_get(loc, 'coordinate', 'longitude'))


def _poi_text(poi_block):
    """Join the first poiDisplayable/poiInferred entry's fields, as stored."""
    pois = stored_list(_get(poi_block, 'pois'), 'POI candidates')
    if not pois:
        return ''
    if not isinstance(pois[0], dict):
        logfunc('Life360 first POI candidate was not an object; place text left blank')
        return ''
    poi = pois[0]
    parts = [poi.get(k) for k in ('locationName', 'streetAddress', 'city', 'region', 'countryCode')]
    return ', '.join(str(p) for p in parts if p)


def _container(path):
    """The app container a store sits in: the path up to its Library folder."""
    marker = f'{os.sep}Library{os.sep}'
    return path.rsplit(marker, 1)[0] if marker in path else os.path.dirname(path)


def _topic_name(path):
    base = os.path.basename(path)
    return base[:-len('.sqlite')] if base.endswith('.sqlite') else base


def _short_topic(path):
    return _topic_name(path).rsplit('.', 1)[-1]


def _topic_files(context, wanted=None):
    """The .sqlite paths among the files found (sidecars are found too, and are applied by SQLite)."""
    seen = []
    for file_found in get_life360_files(context):
        file_found = str(file_found)
        if not file_found.endswith('.sqlite') or os.path.isdir(file_found):
            continue
        if wanted and _short_topic(file_found) not in wanted:
            continue
        if file_found not in seen:
            seen.append(file_found)
    return seen


def _entries(path, rel):
    """Yield (ZTIMESTAMP, parsed JSON) for each ZENTRY row, logging rows that do not parse."""
    rows = read_life360_rows(path, 'SELECT ZTIMESTAMP, ZDATA FROM ZENTRY ORDER BY ZTIMESTAMP', rel)
    bad = 0
    for row in rows:
        data = row[1]
        try:
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            document = json.loads(data)
        except _JSON_ERRORS:
            bad += 1
            continue
        if not isinstance(document, dict):
            bad += 1
            continue
        yield row[0], document
    if bad:
        logfunc(f'{bad} ZENTRY row(s) in {rel!r} did not hold a JSON object and were skipped')


def _sources(paths, context):
    return '\n'.join(context.get_relative_path(p) for p in paths)


def _json_text(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def _appearance(doc, logged, topic, source, event_id=''):
    """Keep the association between each event, source and logged time."""
    return {'entryID': doc.get('id'), 'eventID': event_id, 'store': topic,
            'sourceFile': source, 'loggedTimeUnix': logged}


def _aggregate(values):
    return {'values': values, 'events': set(), 'stores': set(), 'files': set(),
            'appearances': set(), 'n': 0}


def _add_occurrence(entry, doc, logged, topic, source, event_id=''):
    entry['n'] += 1
    entry['stores'].add(topic)
    entry['files'].add(source)
    entry['appearances'].add(_json_text(_appearance(doc, logged, topic, source, event_id)))


def _provenance(entry):
    return (', '.join(sorted(entry['stores'])), entry['n'], '\n'.join(sorted(entry['files'])),
            '[' + ', '.join(sorted(entry['appearances'])) + ']')


def _location_columns(loc):
    lat, lon = _coords(loc)
    return (lat, lon, _as_stored(_get(loc, 'altitude')), _as_stored(_get(loc, 'speed')),
            _as_stored(_get(loc, 'course')), _as_stored(_get(loc, 'horizontalAccuracy')),
            _as_stored(_get(loc, 'verticalAccuracy')))


@artifact_processor
def life360DeviceLocationSamples(context):
    data_headers = (
        ('Sample Time', 'datetime'), ('Logged Time', 'datetime'), 'Latitude', 'Longitude', 'Altitude',
        'Speed', 'Course', 'Horizontal Accuracy', 'Vertical Accuracy', 'Sample Origin (as stored)',
        'Server Tag (as stored)', 'Simulated By Software', 'Produced By Accessory', 'Sample Index',
        'Sample Count', 'Entry ID', 'Source File',
    )
    data_list = []
    paths = _topic_files(context)
    for path in paths:
        rel = context.get_relative_path(path)
        for logged, doc in _entries(path, rel):
            samples = doc.get('bufferedSamples')
            samples = stored_list(samples, 'bufferedSamples')
            if not samples:
                location = stored_dict(doc.get('location'), 'headline location')
                samples = [location] if isinstance(doc.get('location'), dict) else []
            if not samples:
                logfunc(f'Life360 location entry in {rel!r} had neither buffered samples nor a headline '
                        'location and was skipped')
            for index, sample in enumerate(samples, 1):
                if not isinstance(sample, dict):
                    logfunc('Life360 bufferedSamples element was not an object and was skipped')
                    continue
                data_list.append((
                    _cocoa(sample.get('timestamp')), _unix(logged)) + _location_columns(sample) + (
                    _enum(sample.get('sampleOrigin')), _as_stored(_get(sample, 'lmode', 'serverTag', '_0')),
                    _bool(_get(sample, 'sourceInformation', 'isSimulatedBySoftware')),
                    _bool(_get(sample, 'sourceInformation', 'isProducedByAccessory')),
                    index, len(samples), _as_stored(doc.get('id')), rel,
                ))
    return data_headers, data_list, _sources(paths, context)


@artifact_processor
def life360FailedLocations(context):
    data_headers = (
        ('Location Time', 'datetime'), ('Logged Time', 'datetime'), 'Latitude', 'Longitude', 'Altitude',
        'Speed', 'Course', 'Horizontal Accuracy', 'Vertical Accuracy', 'Server Tag (as stored)',
        'Battery Level (as stored)', 'Battery State (as stored)', 'Wi-Fi Enabled', 'SSID', 'BSSID',
        'Drive Detection Status (as stored)', 'Entry ID', 'Source File',
    )
    data_list = []
    paths = _topic_files(context)
    for path in paths:
        rel = context.get_relative_path(path)
        for logged, doc in _entries(path, rel):
            loc = stored_dict(doc.get('location'), 'failed location')
            data_list.append((_cocoa(loc.get('timestamp')), _unix(logged)) + _location_columns(loc) + (
                _as_stored(_get(loc, 'lmode', 'serverTag', '_0')),
                _as_stored(_get(doc, 'batteryState', 'level')), _as_stored(_get(doc, 'batteryState', 'state')),
                _bool(doc.get('wifiEnabled')), _as_stored(doc.get('ssid')), _as_stored(doc.get('bssid')),
                _as_stored(doc.get('driveDetectionStatus')), _as_stored(doc.get('id')), rel,
            ))
    return data_headers, data_list, _sources(paths, context)


def _drive_event_row(doc, logged, kind_store, rel):
    drive = stored_dict(doc.get('drive'), 'movement drive')
    lat, lon = _coords(drive)
    incidents = drive.get('drivingIncidents')
    waypoints = drive.get('waypoints')
    stored_list(incidents, 'movement drivingIncidents')
    stored_list(waypoints, 'movement waypoints')
    poi = doc.get('movementPOIData')
    return (
        _cocoa(drive.get('timestamp')), 'drive', _enum(drive.get('eventType')),
        _cocoa(doc.get('startTime')), '', lat, lon,
        _as_stored(drive.get('distance')), _as_stored(drive.get('averageSpeed')),
        _as_stored(drive.get('topSpeed')), _as_stored(drive.get('score')), '', '',
        _as_stored(drive.get('completionState')),
        _poi_text(_get(poi, 'startPoiDisplayable')), _poi_text(_get(poi, 'endPoiDisplayable')),
        len(incidents) if isinstance(incidents, list) else '',
        len(waypoints) if isinstance(waypoints, list) else '', '',
        _as_stored(drive.get('tripID')), _as_stored(doc.get('sessionID')), _as_stored(drive.get('id')),
        _as_stored(drive.get('sdkVendor')), _as_stored(drive.get('sdkVersion')),
        _as_stored(doc.get('sequenceNumber')), _as_stored(doc.get('userId')), _unix(logged), kind_store, rel,
    )


def _trip_event_row(doc, logged, kind_store, rel):
    route = doc.get('route')
    stored_list(route, 'movement route')
    poi = doc.get('movementPOIData')
    return (
        _cocoa(doc.get('currentTimestamp')), 'trip', _enum(doc.get('eventType')),
        _cocoa(doc.get('startTime')), _cocoa(doc.get('endTime')), '', '',
        _as_stored(doc.get('distance')), '', '', '', _as_stored(doc.get('modality')),
        _as_stored(doc.get('confidence')), '',
        _poi_text(_get(poi, 'startPoiDisplayable')), _poi_text(_get(poi, 'endPoiDisplayable')),
        '', len(route) if isinstance(route, list) else '', '',
        '', _as_stored(doc.get('sessionId')), _as_stored(doc.get('id')), '', '',
        _as_stored(doc.get('sequenceNumber')), _as_stored(doc.get('userId')), _unix(logged), kind_store, rel,
    )


def _cancel_row(doc, logged, kind, kind_store, rel):
    session = doc.get('driveSessionId') if kind == 'drive' else doc.get('tripSessionId')
    return (
        _unix(doc.get('timestamp')), kind, 'cancel', '', '', '', '', '', '', '', '', '', '', '', '', '',
        '', '', _as_stored(doc.get('reason')), '', _as_stored(session), _as_stored(doc.get('id')), '', '',
        '', '', _unix(logged), kind_store, rel,
    )


@artifact_processor
def life360MovementEvents(context):
    data_headers = (
        ('Event Time', 'datetime'), 'Kind', 'Event Type (as stored)', ('Start Time', 'datetime'),
        ('End Time', 'datetime'), 'Latitude', 'Longitude', 'Distance (as stored)',
        'Average Speed (as stored)', 'Top Speed (as stored)', 'Score (as stored)', 'Modality (as stored)',
        'Confidence (as stored)', 'Completion State (as stored)', 'Start Place',
        'End Place', 'Incident Count', 'Waypoint Count', 'Reason (as stored)', 'Trip ID',
        'Session ID', 'Event ID', 'SDK Vendor', 'SDK Version', 'Sequence Number', 'User ID',
        ('Logged Time', 'datetime'), 'Store', 'Source File',
    )
    data_list = []
    sources = []
    for path in _topic_files(context):
        topic = _short_topic(path)
        rel = context.get_relative_path(path)
        sources.append(path)
        for logged, doc in _entries(path, rel):
            if topic in ('drive_session', 'DriveEvent'):
                data_list.append(_drive_event_row(doc, logged, topic, rel))
            elif topic == 'trip_session':
                data_list.append(_trip_event_row(doc, logged, topic, rel))
            elif topic == 'DriveCancellationTopic':
                data_list.append(_cancel_row(doc, logged, 'drive', topic, rel))
            elif topic == 'TripCancellationTopic':
                data_list.append(_cancel_row(doc, logged, 'trip', topic, rel))
    for file_found in get_life360_files(context):
        file_found = str(file_found)
        if not file_found.endswith('com.life360.safetymap.plist'):
            continue
        plist = stored_dict(get_plist_file_content(file_found), 'preferences root')
        starts = plist.get(_TRIP_START_KEY)
        stored_dict(starts, 'trip start times')
        if not isinstance(starts, dict):
            continue
        sources.append(file_found)
        rel = context.get_relative_path(file_found)
        for trip_id, started in starts.items():
            data_list.append((
                _unix(started), 'drive', 'start', _unix(started), '', '', '', '', '', '', '', '', '', '', '',
                '', '', '', '', _as_stored(trip_id), '', '', '', '', '', '', '', _TRIP_START_KEY, rel,
            ))
    data_list.sort(key=lambda row: (str(row[0]), row[27]))
    return data_headers, data_list, _sources(sources, context)


def _point_row(point, kind, session, event_type, store, container):
    if not isinstance(point, dict):
        logfunc('Life360 waypoint element was not an object and was skipped')
        return None
    # drive waypoints carry Unix seconds, trip route points seconds since 2001 (see the notes)
    when = _unix(point.get('timestamp')) if kind == 'drive' else _cocoa(point.get('timestamp'))
    if 'coordinate' in point:
        lat, lon = _coords(point)
    else:
        lat, lon = _as_stored(point.get('latitude')), _as_stored(point.get('longitude'))
    # The entire object matters: equal coordinates/time can carry different sources or quality.
    key = (container, kind, session, _json_text(point))
    values = (
        when, lat, lon, _as_stored(point.get('speed')),
        _as_stored(point.get('course')), _as_stored(point.get('horizontalAccuracy')),
        _as_stored(point.get('verticalAccuracy')), _as_stored(point.get('source')),
        _as_stored(point.get('modality')), _as_stored(point.get('confidence')), kind, session,
    )
    return key, values, event_type, store


@artifact_processor
def life360MovementWaypoints(context):
    data_headers = (
        ('Waypoint Time', 'datetime'), 'Latitude', 'Longitude', 'Speed', 'Course', 'Horizontal Accuracy',
        'Vertical Accuracy', 'Point Source (as stored)', 'Modality (as stored)', 'Confidence (as stored)',
        'Kind', 'Trip ID or Session ID', 'Event Types', 'Stores', 'Occurrences', 'Source Files',
        'Contributing Records', 'Point Data (as stored)',
    )
    points = {}
    paths = _topic_files(context)
    for path in paths:
        topic = _short_topic(path)
        rel = context.get_relative_path(path)
        for logged, doc in _entries(path, rel):
            if topic == 'trip_session':
                items = doc.get('route')
                kind, session, event_type = 'trip', doc.get('sessionId'), _enum(doc.get('eventType'))
            else:
                drive = stored_dict(doc.get('drive'), 'waypoint drive')
                items = drive.get('waypoints')
                kind, session, event_type = 'drive', drive.get('tripID'), _enum(drive.get('eventType'))
            items = stored_list(items, 'waypoints or route')
            for point in items:
                made = _point_row(point, kind, _as_stored(session), event_type, topic, _container(path))
                if made is None:
                    continue
                key, values, event_type_seen, store = made
                entry = points.setdefault(key, _aggregate(values))
                entry['events'].add(str(event_type_seen))
                drive = doc.get('drive') if isinstance(doc.get('drive'), dict) else {}
                _add_occurrence(entry, doc, logged, store, rel, drive.get('id', doc.get('id')))
    data_list = []
    for key, entry in points.items():
        data_list.append(entry['values'] + (', '.join(sorted(entry['events'])),) +
                         _provenance(entry) + (key[-1],))
    data_list.sort(key=lambda row: tuple(str(value) for value in row))
    return data_headers, data_list, _sources(paths, context)


@artifact_processor
def life360DrivingIncidents(context):
    data_headers = (
        ('Incident Time', 'datetime'), 'Type (as stored)', 'Latitude', 'Longitude', 'Trip ID', 'Event IDs',
        'Stores', 'Occurrences', 'Source Files', 'Contributing Records', 'Incident Data (as stored)',
    )
    incidents = {}
    paths = _topic_files(context)
    for path in paths:
        topic = _short_topic(path)
        rel = context.get_relative_path(path)
        for logged, doc in _entries(path, rel):
            drive = stored_dict(doc.get('drive'), 'incident drive')
            items = stored_list(drive.get('drivingIncidents'), 'drivingIncidents')
            for item in items:
                if not isinstance(item, dict):
                    logfunc('Life360 drivingIncidents element was not an object and was skipped')
                    continue
                lat, lon = _coords(item)
                key = (_container(path), _as_stored(drive.get('tripID')), _json_text(item))
                values = (_unix(item.get('timestamp')), _as_stored(item.get('type')), lat, lon,
                          _as_stored(drive.get('tripID')))
                entry = incidents.setdefault(key, _aggregate(values))
                event_id = _as_stored(drive.get('id'))
                if event_id != '':
                    entry['events'].add(str(event_id))
                _add_occurrence(entry, doc, logged, topic, rel, event_id)
    data_list = []
    for key, entry in incidents.items():
        data_list.append(entry['values'] + (', '.join(sorted(entry['events'])),) +
                         _provenance(entry) + (key[-1],))
    data_list.sort(key=lambda row: tuple(str(value) for value in row))
    return data_headers, data_list, _sources(paths, context)


@artifact_processor
def life360DwellEvents(context):
    data_headers = (
        ('Event Time', 'datetime'), 'Event Type (as stored)', 'State (as stored)', ('Dwell Start', 'datetime'),
        ('Dwell End', 'datetime'), 'Latitude', 'Longitude', 'Horizontal Accuracy',
        'Displayable Place', 'Inferred Place', 'Algorithm (as stored)',
        'Dwell ID', 'Session ID', 'Sequence Number', 'User ID', ('Logged Time', 'datetime'), 'Stores',
        'Occurrences', 'Source Files', 'Contributing Records', 'Event Data (as stored)',
    )
    dwells = {}
    paths = _topic_files(context)
    for path in paths:
        topic = _short_topic(path)
        rel = context.get_relative_path(path)
        for logged, doc in _entries(path, rel):
            dwell = stored_dict(doc.get('dwell'), 'dwell')
            loc = stored_dict(dwell.get('location'), 'dwell location')
            event_type = _enum(dwell.get('eventType'))
            # Do not merge engine and session payloads into a record that neither store wrote.
            key = (_container(path), _json_text(doc), logged)
            values = (
                _cocoa(dwell.get('timestamp')), event_type, _enum(dwell.get('state')),
                _unix(loc.get('startTime')), _unix(loc.get('endTime')),
                _as_stored(loc.get('latitude')), _as_stored(loc.get('longitude')),
                _as_stored(loc.get('horizontalAccuracy')),
                _poi_text(_get(dwell, 'poiData', 'poiDisplayable')),
                _poi_text(_get(dwell, 'poiData', 'poiInferred')), _as_stored(dwell.get('algorithm')),
                _as_stored(dwell.get('id')), _as_stored(doc.get('sessionID')),
                _as_stored(doc.get('sequenceNumber')), _as_stored(doc.get('userId')), _unix(logged),
            )
            entry = dwells.setdefault(key, _aggregate(values))
            _add_occurrence(entry, doc, logged, topic, rel, dwell.get('id'))
    data_list = [entry['values'] + _provenance(entry) + (key[1],) for key, entry in dwells.items()]
    data_list.sort(key=lambda row: tuple(str(value) for value in row))
    return data_headers, data_list, _sources(paths, context)


@artifact_processor
def life360GeofenceBreaches(context):
    data_headers = (
        ('Event Time', 'datetime'), ('Location Time', 'datetime'), 'Place Name', 'Direction (as stored)',
        'Distance To Fence', 'Unit', 'Algorithm (as stored)', 'Place ID', 'Circle ID', 'Latitude', 'Longitude',
        'Altitude', 'Speed', 'Course', 'Horizontal Accuracy', 'Vertical Accuracy', 'Wi-Fi Enabled',
        'Entry ID', 'Source File',
    )
    data_list = []
    paths = _topic_files(context)
    for path in paths:
        rel = context.get_relative_path(path)
        for logged, doc in _entries(path, rel):
            loc = stored_dict(doc.get('location'), 'breach location')
            places = stored_list(doc.get('places'), 'breach places')
            if not places:
                places = [{}]
            for place in places:
                if not isinstance(place, dict):
                    logfunc('Life360 breach place element was not an object and was skipped')
                    continue
                data_list.append((
                    _unix(doc.get('timestamp', logged)), _cocoa(loc.get('timestamp')),
                    _as_stored(place.get('name')), _as_stored(place.get('direction')),
                    _as_stored(_get(place, 'distanceToFence', 'value')),
                    _as_stored(_get(place, 'distanceToFence', 'unit', 'symbol')),
                    _as_stored(place.get('algorithm')), _as_stored(place.get('id')),
                    _as_stored(place.get('circleId'))) + _location_columns(loc) + (
                    _bool(_get(doc, 'wifi', 'enabled')), _as_stored(doc.get('id')), rel,
                ))
    return data_headers, data_list, _sources(paths, context)


def _decode_raw_event(raw):
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str):
        if raw is not None:
            logfunc('Life360 rawEvent was neither an object nor base64 text; outer entry retained')
        return {}
    try:
        decoded = json.loads(base64.b64decode(raw, validate=True).decode('utf-8'))
    except _JSON_ERRORS:
        logfunc('Life360 rawEvent could not be decoded as base64 JSON; outer entry retained')
        return {}
    if not isinstance(decoded, dict):
        logfunc('Life360 rawEvent decoded to a non-object; outer entry retained')
    return decoded if isinstance(decoded, dict) else {}


@artifact_processor
def life360ActivityModality(context):
    data_headers = (
        ('Event Time', 'datetime'), ('Logged Time', 'datetime'), ('Location Time', 'datetime'),
        'Modality (as stored)', 'Confidence (as stored)', 'Raw Event Type (as stored)',
        'Latitude', 'Longitude', 'Altitude', 'Speed', 'Course',
        'Horizontal Accuracy', 'Vertical Accuracy', 'Server Tag (as stored)', 'Trip ID', 'Entry ID',
        'Source File',
    )
    data_list = []
    paths = _topic_files(context)
    for path in paths:
        rel = context.get_relative_path(path)
        for logged, doc in _entries(path, rel):
            raw = _decode_raw_event(doc.get('rawEvent'))
            loc = stored_dict(raw.get('location'), 'rawEvent location')
            trip_id = ''
            if not isinstance(raw.get('location'), dict):
                drive = stored_dict(raw.get('drive'), 'rawEvent drive')
                loc = {'coordinate': drive.get('coordinate'), 'timestamp': drive.get('timestamp')}
                trip_id = _as_stored(drive.get('tripID'))
            data_list.append((
                _unix(raw.get('timestamp', doc.get('timestamp'))), _unix(logged),
                _cocoa(loc.get('timestamp')), _as_stored(doc.get('modality')),
                _as_stored(raw.get('confidence')), _as_stored(doc.get('rawEventType')),
                ) + _location_columns(loc) + (
                _as_stored(_get(loc, 'lmode', 'serverTag', '_0')), trip_id, _as_stored(doc.get('id')), rel,
            ))
    return data_headers, data_list, _sources(paths, context)
