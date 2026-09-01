__artifacts_v2__ = {
    "easy4ipCameras": {
        "name": "Easy4ip - Cameras",
        "description": "Cameras registered in an Easy4ip platform app, with the device name, "
                       "model, firmware version, connection ports and the storage and online "
                       "state recorded for each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Easy4ip",
        "notes": "Easy4ip is the camera platform that several vendors ship under their own branding, "
                 "so this artifact is named for the platform rather than for one app; the tested "
                 "sample came from a Lorex-branded app, and another vendor's app built on the same "
                 "platform would produce the same store. The Source File column gives the container "
                 "the store was read from, which is what identifies the app it belongs to. Read from "
                 "easy4ip.sqlite under Library/Support, whose parent folder is an account identifier, "
                 "joining DHDeviceDetailList to DHChannelDetailList on the device identifier. Device "
                 "Status, Camera Status, SD Card Status and Access Type are reported as stored. The "
                 "device user name and password the store holds are NOT recovered and this artifact "
                 "does not attempt to: each decodes from base64 to exactly 16 bytes of non-text at "
                 "about 4 bits per byte of entropy, which is one encrypted block rather than a stored "
                 "credential, and a 32 byte salt sits beside them. They are therefore reported only as "
                 "present with their decoded length, and no meaning is asserted for their contents. "
                 "The store was present on 1 of the 26 registered iOS corpora swept for the Lorex- "
                 "branded app, holding a single camera, so no field has been seen to vary across "
                 "devices, vendors or app versions. An extraction carrying another Easy4ip app, or "
                 "more than one camera, would close that gap.",
        "paths": ('*/Library/Support/*/easy4ip.sqlite*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "device-cctv",
        "sample_data": {
            "falken_ios26": "iOS 26.2.1 | 1 row",
        },
    },
    "easy4ipAlarms": {
        "name": "Easy4ip - Camera Alarms",
        "description": "Alarm messages the camera platform recorded, with the alarm type, the "
                       "camera it came from and the time as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Easy4ip",
        "notes": "Read from the CHNMESSAGE table of easy4ip.sqlite. Alarm Time is stored as text with "
                 "no time zone recorded anywhere in the store, so it is reported exactly as stored in "
                 "a text column rather than being rendered as UTC, and an examiner should establish "
                 "the device's zone before relying on it. Alarm Type is reported as stored; the value "
                 "observed on the tested sample names a smart detection class rather than a plain "
                 "motion event. Unread Count is the platform's own count of unread alarms for that "
                 "camera and was higher than the number of stored message rows on the tested sample, "
                 "so this table is a local cache of alarms rather than the complete alarm history, and "
                 "absence of a row is not evidence that no alarm occurred. Thumbnail URL is the "
                 "address the platform recorded for the alarm image; the image itself is not stored "
                 "locally and is not retrieved. The store was present on 1 of the 26 registered iOS "
                 "corpora swept for the Lorex-branded app, holding a single camera, so no field has "
                 "been seen to vary across devices, vendors or app versions. An extraction carrying "
                 "another Easy4ip app, or more than one camera, would close that gap.",
        "paths": ('*/Library/Support/*/easy4ip.sqlite*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "bell",
        "sample_data": {
            "falken_ios26": "iOS 26.2.1 | 1 row",
        },
    },
}

import base64
import os
import sqlite3

from scripts.ilapfuncs import (
    artifact_processor,
    get_sqlite_db_records,
    logfunc,
    open_sqlite_db_readonly,
)


def _encrypted_length(value):
    """The byte length a base64 credential field decodes to, or '' when absent.

    The store keeps the device user name and password as base64 of a single encrypted
    block, so only the decoded length is reported and never the contents.
    """
    if not value:
        return ''
    try:
        return len(base64.b64decode(str(value), validate=True))
    except (ValueError, TypeError):
        return ''


def _has_table(database, table):
    """True when the store carries the named table, so a same-named file fails closed."""
    try:
        connection = open_sqlite_db_readonly(database)
    except sqlite3.Error:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        return cursor.fetchone() is not None
    except sqlite3.Error:
        return False
    finally:
        connection.close()


def _stores(files_found, marker_table):
    """The easy4ip databases, sidecars and same-named lookalikes excluded."""
    stores = []
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        if os.path.basename(file_found) != 'easy4ip.sqlite':
            continue
        if not _has_table(file_found, marker_table):
            logfunc(f'Easy4ip: easy4ip.sqlite carries no {marker_table} table, skipped')
            continue
        stores.append(file_found)
    return stores


@artifact_processor
def easy4ipCameras(context):
    data_headers = (
        'Device Name',
        'Channel Name',
        'Device Model',
        'Firmware Version',
        'Device Status (as stored)',
        'Camera Status (as stored)',
        'SD Card Status (as stored)',
        'Access Type (as stored)',
        'Port',
        'HTTP Port',
        'RTSP Port',
        'Encrypt Mode (as stored)',
        'Stored User Name Length (bytes, encrypted)',
        'Stored Password Length (bytes, encrypted)',
        'Channel Count',
        'Device ID',
        'Source File',
    )
    data_list = []
    source_files = []

    query = '''
    SELECT D.name, C.channelName, D.deviceModel, D.version, D.status, C.cameraStatus,
           D.sdcardStatus, D.accessType, D.port, D.httpPort, D.rtspPort, D.encryptMode,
           D.deviceUsername, D.devicePassword, D.channelNum, D.deviceId
    FROM DHDeviceDetailList AS D
    LEFT JOIN DHChannelDetailList AS C ON C.deviceId = D.deviceId
    ORDER BY D.name
    '''
    for database in _stores(context.get_files_found(), 'DHDeviceDetailList'):
        rows = 0
        for record in get_sqlite_db_records(database, query):
            rows += 1
            data_list.append((
                record[0], record[1], record[2], record[3], record[4], record[5],
                record[6], record[7], record[8], record[9], record[10], record[11],
                _encrypted_length(record[12]),
                _encrypted_length(record[13]),
                record[14], record[15],
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def easy4ipAlarms(context):
    data_headers = (
        'Alarm Time (as stored, no zone recorded)',
        'Alarm Type (as stored)',
        'Camera Name',
        'Unread Count',
        'Thumbnail URL',
        'Device ID',
        'Channel ID',
        'Source File',
    )
    data_list = []
    source_files = []

    query = '''
    SELECT TIME, ALARMTYPE, CHILDNAME, UNREADCOUNT, THUMBURL, DEVICEID, CHILDID
    FROM CHNMESSAGE
    ORDER BY TIME DESC
    '''
    for database in _stores(context.get_files_found(), 'CHNMESSAGE'):
        rows = 0
        for record in get_sqlite_db_records(database, query):
            rows += 1
            data_list.append((
                record[0], record[1], record[2], record[3], record[4], record[5], record[6],
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)
