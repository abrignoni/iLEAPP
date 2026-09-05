__artifacts_v2__ = {
    "life360Locations": {
        "name": "Life360 - Locations",
        "description": "Location fixes Life360 sent to its servers, read from the X-UserContext header the app "
                       "logs with each upload, with the fix time, coordinates, altitude, speed, heading, "
                       "accuracy and the device activity and location mode at the time.",
        "author": "@KevinPagano3",
        "creation_date": "2024-01-15",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Life360",
        "notes": "Read from the X-UserContext header set lines of the com.life360.safetymap logs, whose value "
                 "is JSON with flags, device, geolocation and geolocation_meta objects. Timestamp is "
                 "geolocation.timestamp, Unix seconds, rendered in UTC; Latitude, Longitude, Altitude, "
                 "Speed, Heading, Accuracy, Vertical Accuracy and Age are the geolocation keys lat, lon, alt, "
                 "speed, heading, accuracy, vertical_accuracy and age as stored. The units in the Speed and "
                 "Accuracy headers were checked against the same logs: the app also prints Apple's own "
                 "CLLocation description of a fix (<lat,lon> +/- Nm (speed N mps / course N)), and on one "
                 "tested image the JSON speed equalled that description's mps value on 726 of 726 fixes at "
                 "the same coordinates, accuracy its metres value on 678 of 726 and heading its course on "
                 "691. Activity Type is device.userActivity as stored (vehicle, potentialFlyer, unknown, "
                 "os_walking, flying and walking across the eight tested images with fixes; an earlier "
                 "version of this artifact stripped os_ and capitalised the value, which merged os_walking "
                 "with walking), Location Mode is geolocation_meta.lmode as stored (drive, move, gh, push, "
                 "geo and fore) and Location Precision is flags.preciseLocation as stored (fullAccuracy on "
                 "every tested fix, 8,679 across the eight images). Life360 is closed "
                 "source, so the key names are the only labels; the per-second samples the app logs beside "
                 "these fixes are in the Location Samples artifact. A row records a fix the app prepared "
                 "for upload; it does not by itself say who carried the device.",
        "paths": ('*/com.life360.safetymap *.log',),
        "output_types": ["html", "tsv", "timeline", "lava", "kml"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Life360: Find Friends & Family 23.19.0 | 728 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "belkactf6": "0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | Life360: Stay Connected & Safe 25.37.0 | 628 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Life360: Find Family & Friends 24.34.0 | 324 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360: Find Friends & Family 23.15.0 | 811 rows",
            "hc_ios18_7": "iOS 18.7.8 | Life360: Family Safety & GPS 26.22.0 | 734 rows",
            "hc_ios26": "iOS 26.5.2 | 1407 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Life360: Find Friends & Family 24.28.0 | 1722 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | Life360: Find Friends & Family 24.31.0 | 2325 rows",
        },
    },
    "life360DeviceBattery": {
        "name": "Life360 - Device Battery",
        "description": "The battery level and charging state Life360 logged with each location upload, with "
                       "the time of the fix it accompanied.",
        "author": "@KevinPagano3",
        "creation_date": "2024-01-15",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Life360",
        "notes": "Read from the same X-UserContext header set lines as the Locations artifact: Timestamp is "
                 "geolocation.timestamp rendered in UTC, Device Battery is device.battery as stored and "
                 "Charging is Yes when device.charge is 1 and blank when it is 0 (the only two values on "
                 "the tested images; any other value is shown as stored). Life360 is closed source, so the "
                 "key names are the only labels.",
        "paths": ('*/com.life360.safetymap *.log',),
        "output_types": "standard",
        "artifact_icon": "battery",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Life360: Find Friends & Family 23.19.0 | 728 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "belkactf6": "0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | Life360: Stay Connected & Safe 25.37.0 | 628 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Life360: Find Family & Friends 24.34.0 | 324 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360: Find Friends & Family 23.15.0 | 811 rows",
            "hc_ios18_7": "iOS 18.7.8 | Life360: Family Safety & GPS 26.22.0 | 734 rows",
            "hc_ios26": "iOS 26.5.2 | 1407 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Life360: Find Friends & Family 24.28.0 | 1722 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | Life360: Find Friends & Family 24.31.0 | 2325 rows",
        },
    },
    "life360LocationSamples": {
        "name": "Life360 - Location Samples",
        "description": "The per-second location samples Life360 wrote to its own logs, with the sample time, "
                       "coordinates and accuracy, from the main app log and the location push extension log.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Life360",
        "notes": "Read from the lines of the com.life360.safetymap and com.life360.safetymap.sidecar-lpse "
                 "logs that end in four comma-separated values, a time of day, a number, a latitude and a "
                 "longitude, sometimes followed by a fifth word (Strategy). The app writes these under "
                 "its Sample Points listing and beside its Filtered, Filter out, Sending sample and "
                 "Transport success messages; Log Contexts joins the message prefixes a sample appeared "
                 "under and Occurrences counts the lines, because one fix is relogged as it moves "
                 "through the app's filters (on the twelve main logs of one tested image, 19,941 "
                 "distinct fixes across 37,949 lines). Life360 is closed source and the four fields "
                 "carry no labels in the log; the labels here were derived from the same files: the "
                 "third and fourth values are the lat and lon of the X-UserContext JSON fix the app "
                 "logged at the same second (3,322 such pairs on that image), and on 3,001 of those "
                 "pairs the second value equalled the JSON accuracy key and equalled no other key on "
                 "more than nine, so it is reported as Accuracy (as stored), in the unit the JSON key "
                 "carries (metres by the check described in the Locations notes). Sample Time is the "
                 "time of day read in the zone the log line itself carries, attached to the line's date, "
                 "rendered in UTC; a sample time later than its log line by more than an hour is taken "
                 "as the previous day, and no sample on the tested images was dated after the line that "
                 "logged it. First Logged is the time of the earliest line that carried the sample. "
                 "Strategy is the fifth word as stored: drive, bluetooth, movement, push and foreGround in "
                 "the main logs and heartbeat and smartRealTime in the push extension logs across the "
                 "tested images, blank on most sample lines. Log Kind is main or sidecar-lpse from the "
                 "file name. Sample lines were present on five of the eight tested images holding Life360 "
                 "logs, the ones running app versions 23.15.0 through 24.34.0, and absent on the three "
                 "newer ones (25.37.0, 26.22.0 and an iOS 26 image), so their absence on a device says "
                 "nothing about its movements. A row records "
                 "that the app held that fix for the device at Sample Time; it does not say who carried "
                 "the device.",
        "paths": ('*/com.life360.safetymap*.log',),
        "output_types": "all",
        "artifact_icon": "map",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 20421 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "belkactf6": "0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 8626 rows",
            "fsfull002_ios17": "iOS 17.1 | 9783 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 46678 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 33962 rows",
        },
    },
    "life360MotionActivity": {
        "name": "Life360 - Motion Activity",
        "description": "The CoreMotion activity states Life360 logged while deciding how to sample location, "
                       "with the start time of each state and its walking, driving, stationary and confidence flags.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Life360",
        "notes": "Read from the log lines that print a CMMotionActivity object (ActivityQueryProvider latest "
                 "activity), which Apple's CoreMotion framework describes with its own property names: "
                 "startDate, confidence, unknown, stationary, walking, running, automotive and cycling. "
                 "Reference: Apple, CoreMotion CMMotionActivity.h (macOS 26.5 SDK), which declares those "
                 "properties and the confidence enum CMMotionActivityConfidenceLow = 0, Medium = 1, "
                 "High = 2; Confidence Level applies that enum to the stored value. Apple's class "
                 "documentation says the motion properties are not mutually exclusive, so more than one "
                 "can be 1 at once. Start Date is the startDate value, which the log prints with a +0000 "
                 "offset, rendered in UTC. The app repeats the current activity on many lines, so one row "
                 "is reported per distinct start date and flag set, with Occurrences counting the lines "
                 "and First Logged the earliest one (4,344 lines became 4,024 rows on one tested image, so "
                 "most polls report a new state). These lines appeared on one of the eight tested images holding "
                 "Life360 logs, the one running app version 23.19.0, so the artifact is empty on the other "
                 "builds. A row records the motion state iOS reported to the app from Start "
                 "Date on; it does not by itself say who carried the device.",
        "paths": ('*/com.life360.safetymap*.log',),
        "output_types": "standard",
        "artifact_icon": "navigation",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 4024 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "belkactf6": "0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
        },
    },
    "life360ChatMessages": {
        "name": "Life360 - Chat Messages",
        "description": "Parses Life360 chat messages",
        "author": "@KevinPagano3",
        "creation_date": "2024-01-15",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Life360",
        "notes": "Sent-status value mapping observed in testing; unrecognized values reported as stored",
        "paths": ('*/Library/Application Support/Messaging.sqlite*',),
        "output_types": "all",
        "artifact_icon": "message-circle",
        "sample_data": {
            "felix_ios17": "iOS 17.6.1 | Life360: Find Family & Friends 24.34.0 | 8 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360: Find Friends & Family 23.15.0 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Life360: Find Friends & Family 24.28.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | Life360: Find Friends & Family 24.31.0 | 5 rows",
            "abe_ios16": "iOS 16.5 | Life360: Find Friends & Family 23.19.0 | 0 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Thread ID",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender First Name"
            }
        },
    },
    "life360Members": {
        "name": "Life360 - Members",
        "description": "Parses Life360 circle members",
        "author": "@KevinPagano3",
        "creation_date": "2024-01-15",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Life360",
        "notes": "",
        "paths": ('*/Library/Application Support/Messaging.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "felix_ios17": "iOS 17.6.1 | Life360: Find Family & Friends 24.34.0 | 10 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360: Find Friends & Family 23.15.0 | 1 row",
            "iphone11_ios17": "iOS 17.3 | Life360: Find Friends & Family 24.28.0 | 4 rows",
            "otto_ios17": "iOS 17.5.1 | Life360: Find Friends & Family 24.31.0 | 10 rows",
            "abe_ios16": "iOS 16.5 | Life360: Find Friends & Family 23.19.0 | 1 row",
        }
    }
}

import json
import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import artifact_processor, convert_ts_human_to_utc, get_sqlite_db_records, logfunc

_LINE = re.compile(r'^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}\.\d{3})([+-])(\d{2})(\d{2}) ')
# 'Life360[pid:tid] I | NGL | ', 'Life360[pid:tid] I LOCATION | ', 'Sidecar-LPSE[pid:tid] I Sidecar-LPSE | '
_HEADER = re.compile(r'^[\w.-]+\[[^\]]*\] \w+ (?:\| )?(?:[\w-]+ \| )?')
# a time of day, a number, a latitude and a longitude, then an optional word, ending the line
_SAMPLE = re.compile(r'(\d{2}:\d{2}:\d{2}\.\d+),\s*(-?\d+\.\d+),\s*(-?\d{1,3}\.\d+),\s*(-?\d{1,3}\.\d+)(?:,\s*([A-Za-z_-]+))?\s*$')
_MOTION = re.compile(r'CMMotionActivity @ [\d.]+,<startDate,(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) ([+-]\d{4}),'
                     r'confidence,(\d+),unknown,(\d+),stationary,(\d+),walking,(\d+),running,(\d+),automotive,(\d+)'
                     r'(?:,cycling,(\d+))?>')
# CoreMotion CMMotionActivity.h: CMMotionActivityConfidenceLow = 0, Medium, High
_CONFIDENCE = {'0': 'Low', '1': 'Medium', '2': 'High'}


def _zone(sign, hours, minutes):
    delta = timedelta(hours=int(hours), minutes=int(minutes))
    return timezone(-delta if sign == '-' else delta)


def _log_kind(path):
    base = os.path.basename(path)
    return 'sidecar-lpse' if '.sidecar-lpse ' in base else 'sidecar' if '.sidecar ' in base else 'main'


def _log_lines(context):
    """(path, date, line time as aware datetime, message) for every timestamped line of every log found."""
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.isdir(file_found) or not file_found.endswith('.log'):
            continue
        try:
            with open(file_found, encoding='utf-8', errors='replace') as fh:
                lines = fh.readlines()
        except OSError as ex:
            logfunc(f'Failed to read Life360 log {file_found}: {ex}')
            continue
        for line in lines:
            m = _LINE.match(line)
            if not m:
                continue
            zone = _zone(m.group(3), m.group(4), m.group(5))
            try:
                when = datetime.strptime(f'{m.group(1)} {m.group(2)}', '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=zone)
            except ValueError:
                continue
            message = _HEADER.sub('', line[m.end():].rstrip(), count=1)
            yield file_found, m.group(1), when, message


def _iter_usercontext(context):
    """Yield (location-timestamp UTC, parsed JSON) for each X-UserContext log line."""
    items = []
    sources = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('.log'):
            continue
        try:
            with open(file_found, encoding='utf-8', mode='r') as fh:
                lines = fh.readlines()
        except OSError as ex:
            logfunc(f'Failed to read Life360 log {file_found}: {ex}')
            continue
        for line in lines:
            if 'X-UserContext header set: ' not in line:
                continue
            try:
                json_load = json.loads(line.split('X-UserContext header set: ')[1].strip())
            except (json.JSONDecodeError, IndexError):
                continue
            ts = json_load.get('geolocation', {}).get('timestamp')
            try:
                time_create = datetime.fromtimestamp(float(ts), tz=timezone.utc) if ts else ''
            except (ValueError, TypeError, OSError, OverflowError):
                time_create = ''
            items.append((time_create, json_load))
        sources.append(context.get_relative_path(file_found))
    return items, '\n'.join(dict.fromkeys(sources))


def _find_db(context):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('Messaging.sqlite'):
            return file_found
    return ''


@artifact_processor
def life360Locations(context):
    data_headers = ('Timestamp', 'Latitude', 'Longitude', 'Altitude', 'Speed (mps)', 'Heading',
                    'Activity Type', 'Location Mode', 'Location Precision', 'Accuracy (+/- m)',
                    'Vertical Accuracy (+/- m)', 'Age')
    data_headers = (('Timestamp', 'datetime'),) + data_headers[1:]
    data_list = []
    items, source_path = _iter_usercontext(context)
    for time_create, jl in items:
        geo = jl.get('geolocation', {})
        activity = jl.get('device', {}).get('userActivity', '')
        lmode = jl.get('geolocation_meta', {}).get('lmode', '')
        precise = jl.get('flags', {}).get('preciseLocation', '')
        data_list.append((time_create, geo.get('lat', ''), geo.get('lon', ''), geo.get('alt', ''),
                          geo.get('speed', ''), geo.get('heading', ''), activity, lmode, precise,
                          geo.get('accuracy', ''), geo.get('vertical_accuracy', ''), geo.get('age', '')))
    return data_headers, data_list, source_path


@artifact_processor
def life360DeviceBattery(context):
    data_headers = (('Timestamp', 'datetime'), 'Device Battery (%)', 'Charging')
    data_list = []
    items, source_path = _iter_usercontext(context)
    for time_create, jl in items:
        device = jl.get('device', {})
        charge = device.get('charge', '')
        charge = 'Yes' if charge == '1' else ('' if charge == '0' else charge)
        data_list.append((time_create, device.get('battery', ''), charge))
    return data_headers, data_list, source_path


@artifact_processor
def life360LocationSamples(context):
    data_headers = (
        ('Sample Time', 'datetime'),
        'Latitude',
        'Longitude',
        'Accuracy (as stored)',
        'Strategy (as stored)',
        'Log Contexts (as stored)',
        'Occurrences',
        ('First Logged', 'datetime'),
        'Log Kind',
        'Source File',
    )
    fixes = {}
    sources = []
    listing = None
    for path, day, when, message in _log_lines(context):
        m = _SAMPLE.search(message)
        if not m:
            # the bare samples that follow a 'Sample Points ----' header belong to that listing
            listing = path if message.startswith('Sample Points') else None
            continue
        try:
            sample = datetime.strptime(f'{day} {m.group(1)[:12]}', '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=when.tzinfo)
        except ValueError:
            continue
        if sample - when > timedelta(hours=1):
            sample -= timedelta(days=1)
        sample = sample.astimezone(timezone.utc)
        prefix = message[:m.start()].strip(' |')
        if not prefix and listing == path:
            prefix = 'Sample Points'
        key = (sample, m.group(3), m.group(4), m.group(2), path)
        entry = fixes.setdefault(key, {'strategy': set(), 'contexts': set(), 'count': 0, 'first': when.astimezone(timezone.utc)})
        entry['count'] += 1
        entry['first'] = min(entry['first'], when.astimezone(timezone.utc))
        if m.group(5):
            entry['strategy'].add(m.group(5))
        if prefix:
            entry['contexts'].add(prefix[:60])
        if path not in sources:
            sources.append(path)
    data_list = []
    for (sample, lat, lon, accuracy, path), entry in sorted(fixes.items(), key=lambda item: (item[0][0], item[0][4])):
        data_list.append((
            sample, lat, lon, accuracy, ', '.join(sorted(entry['strategy'])), '; '.join(sorted(entry['contexts'])),
            entry['count'], entry['first'], _log_kind(path), context.get_relative_path(path),
        ))
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in sources)


@artifact_processor
def life360MotionActivity(context):
    data_headers = (
        ('Start Date', 'datetime'),
        'Confidence (as stored)',
        'Confidence Level',
        'Stationary',
        'Walking',
        'Running',
        'Automotive',
        'Cycling',
        'Unknown',
        'Occurrences',
        ('First Logged', 'datetime'),
        'Log Kind',
        'Source File',
    )
    states = {}
    sources = []
    for path, _day, when, message in _log_lines(context):
        m = _MOTION.search(message)
        if not m:
            continue
        sign, hours, minutes = m.group(2)[0], m.group(2)[1:3], m.group(2)[3:5]
        try:
            start = datetime.strptime(m.group(1), '%Y-%m-%d %H:%M:%S').replace(tzinfo=_zone(sign, hours, minutes)).astimezone(timezone.utc)
        except ValueError:
            continue
        key = (start,) + m.groups()[2:] + (path,)
        entry = states.setdefault(key, {'count': 0, 'first': when.astimezone(timezone.utc)})
        entry['count'] += 1
        entry['first'] = min(entry['first'], when.astimezone(timezone.utc))
        if path not in sources:
            sources.append(path)
    data_list = []
    for key, entry in sorted(states.items(), key=lambda item: (item[0][0], item[0][-1])):
        start, confidence, unknown, stationary, walking, running, automotive, cycling, path = key
        data_list.append((
            start, confidence, _CONFIDENCE.get(confidence, ''), stationary, walking, running, automotive,
            cycling if cycling is not None else '', unknown, entry['count'], entry['first'], _log_kind(path),
            context.get_relative_path(path),
        ))
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in sources)


@artifact_processor
def life360ChatMessages(context):
    data_headers = (('Timestamp', 'datetime'), 'Direction', 'Sender First Name', 'Message',
                    'Message ID', 'Sender Last Name', 'Sent Status', 'Message Seen',
                    'Message Deleted (Locally)', 'Message Liked', 'Action', 'Location Name',
                    'Latitude', 'Longitude', 'Thread ID')
    data_list = []
    source_path = _find_db(context)
    if not source_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        datetime(ZCHATMESSAGE.ZDATE + 978307200, 'unixepoch'),
        CASE ZCHATMEMBER.ZISLOGGEDINUSER WHEN 1 THEN 'Outgoing' ELSE 'Incoming' END,
        ZCHATMEMBER.ZFIRSTNAME,
        ZCHATMESSAGE.ZMESSAGETEXT,
        ZCHATMESSAGE.ZMESSAGEID,
        ZCHATMEMBER.ZLASTNAME,
        CASE ZCHATMESSAGE.ZSENTSTATUSASINTEGER WHEN 2 THEN 'Sent' WHEN 3 THEN 'Failed'
            ELSE ZCHATMESSAGE.ZSENTSTATUSASINTEGER END,
        CASE ZCHATMESSAGE.ZISREAD WHEN 0 THEN '' WHEN 1 THEN 'Yes' END,
        CASE ZCHATMESSAGE.ZISLOCALLYDELETED WHEN 0 THEN '' WHEN 1 THEN 'Yes' END,
        CASE ZCHATMESSAGE.ZISLIKED WHEN 0 THEN '' WHEN 1 THEN 'Yes' END,
        ZCHATMESSAGE.ZACTION,
        ZCHATMESSAGELOCATION.ZNAME,
        ZCHATMESSAGELOCATION.ZLATITUDE,
        ZCHATMESSAGELOCATION.ZLONGITUDE,
        ZCHATMESSAGE.ZTHREAD
    FROM ZCHATMESSAGE
    LEFT JOIN ZCHATMEMBER ON ZCHATMEMBER.Z_PK = ZCHATMESSAGE.ZSENDER
    LEFT JOIN ZCHATMESSAGELOCATION ON ZCHATMESSAGELOCATION.ZMESSAGE = ZCHATMESSAGE.Z_PK
    '''
    try:
        rows = get_sqlite_db_records(source_path, query)
    except sqlite3.Error as ex:
        logfunc(f'Error reading Life360 chat messages: {ex}')
        return data_headers, data_list, context.get_relative_path(source_path)

    for row in rows:
        data_list.append((convert_ts_human_to_utc(row[0]),) + tuple(row[1:]))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def life360Members(context):
    data_headers = ('First Name', 'Last Name', 'Email', ('Phone', 'phonenumber'), 'Member ID',
                    'Avatar URL', 'Local User', 'Admin', 'Circle Name')
    data_list = []
    source_path = _find_db(context)
    if not source_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        ZCHATMEMBER.ZFIRSTNAME,
        ZCHATMEMBER.ZLASTNAME,
        ZCHATMEMBER.ZEMAIL,
        ZCHATMEMBER.ZPHONE,
        ZCHATMEMBER.ZMEMBERID,
        ZCHATMEMBER.ZAVATARURL,
        CASE ZCHATMEMBER.ZISLOGGEDINUSER WHEN 0 THEN '' WHEN 1 THEN 'Yes' END,
        CASE ZCHATMEMBER.ZISADMIN WHEN 0 THEN '' WHEN 1 THEN 'Yes' END,
        ZCHATCIRCLE.ZNAME
    FROM ZCHATMEMBER
    LEFT JOIN ZCHATCIRCLE ON ZCHATCIRCLE.Z_PK = ZCHATMEMBER.ZCIRCLE
    '''
    try:
        rows = get_sqlite_db_records(source_path, query)
    except sqlite3.Error as ex:
        logfunc(f'Error reading Life360 members: {ex}')
        return data_headers, data_list, context.get_relative_path(source_path)

    for row in rows:
        data_list.append(tuple(row))

    return data_headers, data_list, context.get_relative_path(source_path)
