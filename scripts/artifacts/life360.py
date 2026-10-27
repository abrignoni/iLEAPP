__artifacts_v2__ = {
    "life360Locations": {
        "name": "Life360 - Locations",
        "description": "Location fixes Life360 wrote into the X-UserContext header value it "
                       "logged, with the fix time, coordinates, altitude, speed, "
                       "heading, "
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
                 "Accuracy headers were checked against the same logs (the metres unit in the "
                 "Vertical Accuracy header was not checked and follows the Accuracy column): the "
                 "app also prints Apple's own CLLocation description of a fix (<lat,lon> +/- Nm "
                 "(speed N mps / course N)), and on one tested image the JSON speed equalled that "
                 "description's mps value on 726 of 726 fixes at the same coordinates, accuracy "
                 "its metres value on 678 of 726 and heading its course on 691. Activity Type is "
                 "device.userActivity as stored (vehicle, potentialFlyer, unknown, os_walking, "
                 "flying and walking across the eight tested images with fixes; an earlier version "
                 "of this artifact stripped os_ and capitalised the value, which merged os_walking "
                 "with walking), Location Mode is geolocation_meta.lmode as stored (drive, move, "
                 "gh, push, geo and fore) and Location Precision is flags.preciseLocation as "
                 "stored (fullAccuracy was the value seen on the tested images). Life360 is closed "
                 "source, so the key names are the only labels; the location samples the app logs "
                 "beside these fixes are in the Location Samples artifact. A row records a fix the "
                 "app logged in an X-UserContext header value; whether that header was sent is not "
                 "established here, and a row does not by itself say who carried the device.",
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
            "fsfull002_ios17": "iOS 17.1 | Life360: Find Friends & Family 23.43.1 | 811 rows",
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
        "description": "The device.battery and device.charge values Life360 logged in each "
                       "X-UserContext header, with "
                       "the time of the fix it accompanied.",
        "author": '@AlexisBrignoni, Codex',
        "creation_date": "2024-01-15",
        "last_update_date": '2026-10-07',
        "requirements": "none",
        "category": "Life360",
        "notes": 'Read from the same X-UserContext header set lines as the Locations artifact: Timestamp is geolocation.timestamp rendered in UTC. device.battery (as stored) and device.charge (as stored) report the parsed JSON values without a percent unit or charging-state mapping. Missing battery or charge keys retain the existing empty-string default; this does not distinguish a missing key from a stored empty string. The key names alone do not establish units or device charging state. Original artifact contribution: @KevinPagano3.',
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
            "fsfull002_ios17": "iOS 17.1 | Life360: Find Friends & Family 23.43.1 | 811 rows",
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
        "description": "The location samples Life360 wrote to its own logs, with the sample time, "
                       "coordinates and accuracy, from the main app log and the sidecar and "
                       "sidecar-lpse logs.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Life360",
        "notes": "Read from the lines of the logs matching com.life360.safetymap*.log that end in "
                 "four comma-separated values, a time of day, a number, a latitude and a "
                 "longitude, sometimes followed by a fifth word (Strategy). The app writes these "
                 "under its Sample Points listing and beside its Filtered, Filter out, Sending "
                 "sample and Transport success messages; Log Contexts joins the message prefixes a "
                 "sample appeared under and Occurrences counts the lines within one log file (a "
                 "sample that appears in two files is reported once per file, and each prefix in "
                 "Log Contexts is cut to 60 characters), because the same sample values appear on "
                 "more than one line, under different message prefixes. Life360 is closed source "
                 "and the four fields carry no labels in the log; the labels here were derived "
                 "from the same files on one tested image: the third and fourth values were "
                 "compared with the lat and lon of the X-UserContext JSON fix the app logged at "
                 "the same second, and the second value with that fix's accuracy key, which is why "
                 "it is reported as Accuracy (as stored), in the unit the JSON key carries (metres "
                 "by the check described in the Locations notes). The counts from that comparison "
                 "are not recorded here. Sample Time is the time of day "
                 "read in the zone the log line itself carries, attached to the line's date, "
                 "rendered in UTC; a sample time later than its log line by more than an hour is "
                 "taken as the previous day. First Logged is the time of the earliest line that "
                 "carried the sample. Strategy is the fifth word as stored: drive, bluetooth, "
                 "movement, push and foreGround in the main logs and heartbeat and smartRealTime "
                 "in the sidecar-lpse logs across the tested images, blank on most sample lines. "
                 "Log Kind is main, sidecar or sidecar-lpse from the file name. Sample lines were "
                 "present on five of the eight tested images holding Life360 logs, the ones "
                 "running app versions 23.19.0 through 24.34.0, and absent on the three newer ones "
                 "(25.37.0, 26.22.0 and an iOS 26 image), so their absence on a device says "
                 "nothing about its movements. A row records that the app logged a sample carrying "
                 "that time and those coordinates; it does not say who carried "
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
        "description": "The CoreMotion activity states Life360 logged in its own log, with the "
                       "start time of each state and its stationary, walking, running, automotive, "
                       "cycling and unknown flags and its confidence value.",
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
                 "is reported per distinct start date, confidence value and flag set within one "
                 "log file, with Occurrences counting the lines and First Logged the earliest one "
                 "(4,344 lines became 4,024 rows on one tested image, so most of those lines "
                 "carried a start date and flag set not seen before). These lines appeared on one "
                 "of the eight tested images holding Life360 logs, the one running app version "
                 "23.19.0, and on none of the other seven, so an empty result on a device says "
                 "nothing about its motion. A row records the motion state iOS reported to the app "
                 "from Start "
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
        "description": "Parses Life360 chat messages, including messages another state in the "
                       "database's write-ahead log holds and the current state does not",
        "author": "@KevinPagano3",
        "creation_date": "2024-01-15",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Life360",
        "notes": "Direction is derived: Outgoing when the sender's member row has ZISLOGGEDINUSER "
                 "set to 1 and Incoming when it is set to 0. Direction is blank when ZSENDER "
                 "matches no ZCHATMEMBER row or that row holds neither value, so a blank does not "
                 "say who sent the message. All 13 Live messages on felix_ios17 and otto_ios17 and all "
                 "46 Recovered messages on felix_ios17, iphone11_ios17 and otto_ios17 matched a "
                 "member row holding 1 or 0; the blank case was exercised only with a constructed "
                 "database. Timestamp reads ZDATE as seconds since 2001 in UTC. Message "
                 "Seen, Message Deleted (Locally) and Message Liked show Yes for a stored 1 in "
                 "ZISREAD, ZISLOCALLYDELETED and ZISLIKED; what sets those flags is not "
                 "established. Sent Status maps ZSENTSTATUSASINTEGER 2 to Sent and 3 to Failed; "
                 "the mapping "
                 "is not sourced from Life360 and was assigned from tested data with no count "
                 "recorded here. Unrecognized values are reported as stored. "
                 "Record Origin. Live rows come from a normal read of the query. Recovered rows do "
                 "not: their message, the ZCHATMESSAGE primary key Z_PK, is held by another state in "
                 "the database's write-ahead log and absent from the current one. A row whose message "
                 "the current state still holds is not reported, whatever its older versions held. "
                 "The whole query is run in each state, so a Recovered row's sender and location "
                 "come from the same state as its message. Recovery Method and Recovery Location are "
                 "filled in only on Recovered rows. Why a Recovered row is absent is not established "
                 "here. Message Deleted (Locally) on a Recovered row shows the flag held by the state "
                 "the row was read from, mapped the same way as on Live rows. States are read by "
                 "scripts/sqlite_wal.py: each readable earlier committed state of the log's current "
                 "generation (state n is the database after the first n committed transactions, and "
                 "state 0 the database file without its log; a state a partial checkpoint has made "
                 "unreadable is skipped and counted in the run log), the previous generation's "
                 "left-over frames where its checks pass, and frames after the last commit where "
                 "SQLite's quick_check passes. A Recovered row is reported once per message and location row, as the "
                 "newest committed state holding it stored it, else the previous generation's newest "
                 "left-over commit, else the frames after the last commit. Recovery Location names "
                 "the committed states the message was read in, with their first and last numbers, "
                 "and the previous log generation with the first and last numbers of its left-over "
                 "commits; for a message read only after the last commit it names the log's frames "
                 "after the last commit. Recovery Method is WAL committed states, or WAL uncommitted "
                 "frames for a message read only after the last commit. The previous-generation and "
                 "uncommitted-frame paths were not exercised on these images or by the unit test. "
                 "Recovered rows were returned on felix_ios17 (3), iphone11_ios17 (32, where the "
                 "current state holds no message) and otto_ios17 (11), every one from committed "
                 "states of the current generation and with Message text; 7 on otto_ios17 were "
                 "read in the database file and the first two committed states. Message Deleted "
                 "(Locally) was Yes on 2 of the 32 on iphone11_ios17. abe_ios16 and fsfull002_ios17 "
                 "returned no rows; fsfull002_ios17 has no log beside the database. On "
                 "felix_ios17, iphone11_ios17 and otto_ios17 Message Liked was empty on every row; "
                 "Sent Status held Sent on every row on felix_ios17 and iphone11_ios17, and Message "
                 "Seen held Yes on every row on felix_ios17. On iphone11_ios17 Record Origin held "
                 "Recovered and Recovery Method held WAL committed states on every row.",
        "paths": ('*/Library/Application Support/Messaging.sqlite*',),
        "output_types": "all",
        "artifact_icon": "message-circle",
        "sample_data": {
            "felix_ios17": "iOS 17.6.1 | Life360: Find Family & Friends 24.34.0 | 11 rows (3 Recovered)",
            "fsfull002_ios17": "iOS 17.1 | Life360: Find Friends & Family 23.43.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Life360: Find Friends & Family 24.28.0 | 32 rows (32 Recovered)",
            "otto_ios17": "iOS 17.5.1 | Life360: Find Friends & Family 24.31.0 | 16 rows (11 Recovered)",
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
            "fsfull002_ios17": "iOS 17.1 | Life360: Find Friends & Family 23.43.1 | 1 row",
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
from scripts.sqlite_wal import (KIND_COMMITTED, KIND_EARLIER, KIND_UNCOMMITTED,
                                rows_not_in_current)

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
    data_headers = (('Timestamp', 'datetime'), 'device.battery (as stored)', 'device.charge (as stored)')
    data_list = []
    items, source_path = _iter_usercontext(context)
    for time_create, jl in items:
        device = jl.get('device', {})
        charge = device.get('charge', '')
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


# A chat message is one ZCHATMESSAGE row (Z_PK); the query's last two columns are that key and
# the joined ZCHATMESSAGELOCATION Z_PK, so a message with several location rows keeps each.
_MESSAGE_PK = -2
_WAL_KINDS = (KIND_COMMITTED, KIND_EARLIER, KIND_UNCOMMITTED)
_ORIGIN_LIVE = 'Live'
_ORIGIN_RECOVERED = 'Recovered'
_METHOD_WAL_STATES = 'WAL committed states'
_METHOD_WAL_UNCOMMITTED = 'WAL uncommitted frames'


def _recovery_location(name, spans):
    """(method, location) for a key read in the states spans names."""
    parts = []
    committed, earlier = spans['committed'], spans['earlier']
    if committed:
        first, last = committed
        if last == 0:
            parts.append(f'{name} without its log, state 0')
        elif first == 0:
            parts.append(f'{name} and {name}-wal, committed states 0 to {last}')
        else:
            states = f'state {first}' if first == last else f'states {first} to {last}'
            parts.append(f'{name}-wal, committed {states}')
    if earlier:
        first, last = earlier
        commits = f'commit {first}' if first == last else f'commits {first} to {last}'
        parts.append(f'{name}-wal, previous log generation, left-over {commits}')
    if not parts:
        return _METHOD_WAL_UNCOMMITTED, f'{name}-wal, frames after the last commit'
    return _METHOD_WAL_STATES, '; '.join(parts)


def _removed_messages(db_file, query, live_messages):
    """Rows of query whose message key another state in the write-ahead log holds and the
    current state does not, read through scripts/sqlite_wal.py, with each state's own joins.

    Returns [(row, method, location)], one per (message, location row): the row as the newest
    state holding it stored it (a committed state before the previous log generation before
    the frames after the last commit).
    """
    try:
        columns, found, wal = rows_not_in_current(str(db_file), query, include=_WAL_KINDS)
    except (sqlite3.Error, OSError) as ex:
        logfunc(f'Life360 - Chat Messages: write-ahead log not read: {ex}')
        return []
    if wal.log:
        logfunc(f'Life360 - Chat Messages: {wal.summary()}')
    width = len(columns)
    by_key = {}
    for item in found:
        if item.values[width + _MESSAGE_PK] in live_messages:
            continue
        key = item.values[width + _MESSAGE_PK:]
        rank = ((2, item.last_state) if item.first_state is not None else
                (1, item.earlier_generation[1]) if item.earlier_generation else (0, 0))
        entry = by_key.setdefault(key, {'row': item.values, 'rank': rank, 'committed': None,
                                        'earlier': None})
        if rank > entry['rank']:
            entry['row'], entry['rank'] = item.values, rank
        for slot, span in (('committed', (item.first_state, item.last_state)
                            if item.first_state is not None else None),
                           ('earlier', item.earlier_generation)):
            if span:
                old = entry[slot]
                entry[slot] = span if old is None else (min(old[0], span[0]), max(old[1], span[1]))
    name = os.path.basename(str(db_file))
    return [(entry['row'], *_recovery_location(name, entry)) for entry in by_key.values()]


@artifact_processor
def life360ChatMessages(context):
    data_headers = (('Timestamp', 'datetime'), 'Direction', 'Sender First Name', 'Message',
                    'Message ID', 'Sender Last Name', 'Sent Status', 'Message Seen',
                    'Message Deleted (Locally)', 'Message Liked', 'Action', 'Location Name',
                    'Latitude', 'Longitude', 'Thread ID', 'Record Origin', 'Recovery Method',
                    'Recovery Location')
    data_list = []
    source_path = _find_db(context)
    if not source_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        datetime(ZCHATMESSAGE.ZDATE + 978307200, 'unixepoch'),
        CASE ZCHATMEMBER.ZISLOGGEDINUSER WHEN 1 THEN 'Outgoing' WHEN 0 THEN 'Incoming'
            ELSE '' END,
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
        ZCHATMESSAGE.ZTHREAD,
        ZCHATMESSAGE.Z_PK,
        ZCHATMESSAGELOCATION.Z_PK
    FROM ZCHATMESSAGE
    LEFT JOIN ZCHATMEMBER ON ZCHATMEMBER.Z_PK = ZCHATMESSAGE.ZSENDER
    LEFT JOIN ZCHATMESSAGELOCATION ON ZCHATMESSAGELOCATION.ZMESSAGE = ZCHATMESSAGE.Z_PK
    '''
    try:
        rows = [tuple(row) for row in get_sqlite_db_records(source_path, query)]
    except sqlite3.Error as ex:
        logfunc(f'Error reading Life360 chat messages: {ex}')
        return data_headers, data_list, context.get_relative_path(source_path)

    records = [(row, _ORIGIN_LIVE, '', '') for row in rows]
    records.extend((row, _ORIGIN_RECOVERED, method, location) for row, method, location
                   in _removed_messages(source_path, query, {row[_MESSAGE_PK] for row in rows}))
    for row, origin, method, location in records:
        data_list.append((convert_ts_human_to_utc(row[0]),) + tuple(row[1:_MESSAGE_PK])
                         + (origin, method, location))

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
