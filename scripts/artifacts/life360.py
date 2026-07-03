__artifacts_v2__ = {
    "life360Locations": {
        "name": "Life360 - Locations",
        "description": "Parses Life360 location records from app logs",
        "author": "@KevinPagano3",
        "creation_date": "2024-01-15",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Life360",
        "notes": "",
        "paths": ('*/com.life360.safetymap *.log',),
        "output_types": ["html", "tsv", "timeline", "lava", "kml"],
        "artifact_icon": "map-pin"
    },
    "life360DeviceBattery": {
        "name": "Life360 - Device Battery",
        "description": "Parses Life360 device battery records from app logs",
        "author": "@KevinPagano3",
        "creation_date": "2024-01-15",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Life360",
        "notes": "",
        "paths": ('*/com.life360.safetymap *.log',),
        "output_types": "standard",
        "artifact_icon": "battery"
    },
    "life360ChatMessages": {
        "name": "Life360 - Chat Messages",
        "description": "Parses Life360 chat messages",
        "author": "@KevinPagano3",
        "creation_date": "2024-01-15",
        "last_update_date": "2026-07-03",
        "requirements": "none",
        "category": "Life360",
        "notes": "",
        "paths": ('*/Library/Application Support/Messaging.sqlite*',),
        "output_types": "all",
        "artifact_icon": "message-circle",
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
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Life360",
        "notes": "",
        "paths": ('*/Library/Application Support/Messaging.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "users"
    }
}

import json
import sqlite3
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, convert_ts_human_to_utc, get_sqlite_db_records, logfunc


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
    return items, ', '.join(dict.fromkeys(sources))


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
        activity = jl.get('device', {}).get('userActivity', '').replace('os_', '').title()
        lmode = jl.get('geolocation_meta', {}).get('lmode', '').title()
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
def life360ChatMessages(context):
    data_headers = (('Timestamp', 'datetime'), 'Message ID', 'Sender First Name', 'Sender Last Name',
                    'Message', 'Sent Status', 'Message Seen', 'Message Deleted', 'Message Liked',
                    'Action', 'Location Name', 'Latitude', 'Longitude', 'Direction', 'Thread ID')
    data_list = []
    source_path = _find_db(context)
    if not source_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        datetime(ZCHATMESSAGE.ZDATE + 978307200, 'unixepoch'),
        ZCHATMESSAGE.ZMESSAGEID,
        ZCHATMEMBER.ZFIRSTNAME,
        ZCHATMEMBER.ZLASTNAME,
        ZCHATMESSAGE.ZMESSAGETEXT,
        CASE ZCHATMESSAGE.ZSENTSTATUSASINTEGER WHEN 2 THEN 'Sent' WHEN 3 THEN 'Failed' END,
        CASE ZCHATMESSAGE.ZISREAD WHEN 0 THEN '' WHEN 1 THEN 'Yes' END,
        CASE ZCHATMESSAGE.ZISLOCALLYDELETED WHEN 0 THEN '' WHEN 1 THEN 'Yes' END,
        CASE ZCHATMESSAGE.ZISLIKED WHEN 0 THEN '' WHEN 1 THEN 'Yes' END,
        ZCHATMESSAGE.ZACTION,
        ZCHATMESSAGELOCATION.ZNAME,
        ZCHATMESSAGELOCATION.ZLATITUDE,
        ZCHATMESSAGELOCATION.ZLONGITUDE,
        CASE ZCHATMEMBER.ZISLOGGEDINUSER WHEN 1 THEN 'Outgoing' ELSE 'Incoming' END,
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
