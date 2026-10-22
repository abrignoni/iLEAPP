#!/usr/bin/env python3
"""Create wholly fabricated Life360 API-cache and multi-transaction WAL evidence."""
import json
from pathlib import Path
import plistlib
import sqlite3
import uuid

from admin.test.fixtures.life360 import make_synthetic_life360 as base


def _marker(root):
    root.mkdir(parents=True, exist_ok=True)
    (root / '.com.apple.mobile_container_manager.metadata.plist').write_bytes(
        plistlib.dumps({'MCMMetadataIdentifier': 'com.life360.safetymap'}))


def build_cache(root):
    root = Path(root)
    _marker(root)
    folder = root / 'Library/Caches/com.life360.safetymap'
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / 'Cache.db'
    connection = sqlite3.connect(path)
    connection.executescript('''
        CREATE TABLE cfurl_cache_response(entry_ID INTEGER PRIMARY KEY,request_key TEXT,
                                          time_stamp NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE cfurl_cache_receiver_data(entry_ID INTEGER PRIMARY KEY,isDataOnFS INTEGER,receiver_data BLOB);
        CREATE TABLE cfurl_cache_blob_data(entry_ID INTEGER PRIMARY KEY,response_object BLOB,request_object BLOB);
    ''')
    iso = '2026-01-15T07:00:00.125-05:00'
    stamp = '2026-01-15 13:00:00'
    location = {'deviceId': base.lid(200), 'latitude': 0.5, 'longitude': -150.5, 'accuracy': 5,
                'firstObserved': iso, 'lastObserved': iso, 'updated': iso, 'batteryLevel': 75,
                'batteryCharging': False, 'wifiConnected': True, 'speed': 0, 'inTransit': False,
                'owners': [{'userId': base.USER}], 'provider': 'synthetic', 'type': 'phone',
                'os': 'iOS', 'appVersion': '26.34.0.5', 'userActivity': 'unknown', 'unknownField': 'retained'}
    responses = [
        ('/v5/circles/devices/locations', {'data': {'items': [location]}}, 0),
        ('/v5/circles/devices', {'data': {'items': [{'id': base.lid(200), 'owners': [{'userId': base.USER}],
             'name': 'Synthetic Phone', 'modified': iso, 'provider': 'synthetic', 'type': 'phone',
             'typeData': {'hardwareModel': 'Synthetic', 'os': 'iOS', 'osVersion': '18.6', 'appVersion': '26.34.0.5'}}]}}, 0),
        ('/v5/circles/devices/issues', {'data': {'items': [{'deviceId': base.lid(200), 'userId': base.USER,
             'issues': [{'name': 'syntheticIssue', 'value': 'unknown', 'startTime': iso}]}]}}, 0),
        ('/v4/circles', {'circles': [{'id': base.CIRCLE1, 'name': 'Synthetic Circle', 'createdAt': str(base.T0)}]}, 1),
        ('/v5/users/me', {'id': base.USER, 'firstName': 'Sample', 'lastName': 'Person', 'loginEmail': 'sample@example.invalid',
             'loginPhone': '+15550100001', 'created': '2026-01-15 12:00:00', 'dob': '2000-01-01',
             'locale': 'en_US', 'language': 'en', 'extraProfileField': 'retained'}, 0),
        ('/v4/circles/' + base.CIRCLE1 + '/drives', 'missing-body', 1),
    ]
    for index, (endpoint, body, disk) in enumerate(responses, 1):
        encoded = json.dumps(body).encode()
        if disk:
            name = 'synthetic-' + str(index)
            if isinstance(body, dict):
                external = folder / 'fsCachedData'
                external.mkdir(exist_ok=True)
                (external / name).write_bytes(encoded)
            encoded = name
        connection.execute('insert into cfurl_cache_response values(?,?,?)',
                           (index, 'https://api-cloudfront.life360.com' + endpoint, stamp))
        connection.execute('insert into cfurl_cache_receiver_data values(?,?,?)', (index, disk, encoded))
    connection.commit()
    connection.close()
    return path


def _history(path, documents):
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.execute('PRAGMA page_size=1024')
    connection.execute('PRAGMA journal_mode=WAL')
    connection.execute('PRAGMA wal_autocheckpoint=0')
    connection.executescript('''CREATE TABLE ZENTRY(Z_PK INTEGER PRIMARY KEY,Z_ENT INTEGER,Z_OPT INTEGER,
        ZTIMESTAMP FLOAT,ZID BLOB,ZDATA BLOB);
        CREATE TABLE ZSUBSCRIPTION(Z_PK INTEGER PRIMARY KEY,Z_ENT INTEGER,Z_OPT INTEGER,
                                  ZLASTSENTTIMESTAMP FLOAT,ZIDENTIFIER VARCHAR);''')
    def put(index, doc):
        connection.execute('insert or replace into ZENTRY values(?,1,1,?,?,?)',
                           (index, float(base.T0 + index), uuid.UUID(doc['id']).bytes, json.dumps(doc).encode()))
    put(1, documents[0])
    connection.commit()
    connection.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    put(2, documents[1])
    connection.commit()
    put(3, documents[2])
    connection.commit()
    connection.execute('delete from ZENTRY where Z_PK in (1,2)')
    connection.commit()
    snapshot = {suffix: Path(str(path) + suffix).read_bytes() for suffix in ('', '-wal', '-shm')}
    connection.close()
    for suffix, data in snapshot.items():
        Path(str(path) + suffix).write_bytes(data)


def build_recovery(root):
    root = Path(root)
    _marker(root)
    docs = []
    for index in range(3):
        point = {'timestamp': base.T0 + index * 60, 'coordinate': {'latitude': 0.5 + index / 100, 'longitude': -150.5},
                 'speed': 0, 'course': 90, 'horizontalAccuracy': 5, 'unknownPoint': 'retained'}
        incident = {'timestamp': base.T0 + index * 60 + 1, 'type': 'synthetic',
                    'coordinate': point['coordinate'], 'unknownIncident': 'retained'}
        doc = base.drive_doc(base.T0 + index * 60, 'stop', [point], [incident], True, base.SESSION1)
        doc.update(id=base.uid(0xD000 + index), padding='overflow-control-' * 200 if index == 1 else '')
        docs.append(doc)
    stem = 'com.life360.event_history_core.topics.drive_session'
    path = root / 'Library/Application Support/com.eventkit' / stem / (stem + '.sqlite')
    _history(path, docs)
    failed = []
    for index in range(3):
        failed.append({'id': base.uid(0xE000 + index), 'location': base.loc(base.T0 + index * 60),
                       'batteryState': {'level': 75, 'state': 'unknown'}})
    stem = 'com.life360.AwarenessEngine.Topics.FailedLocationTopic'
    other = root / 'Library/Application Support/com.eventkit' / stem / (stem + '.sqlite')
    _history(other, failed)
    # Same Core Data schema as the earlier synthetic fixture; one non-live drive in its main-file view.
    temp = root / 'temporary-native-source'
    base.build_container(str(temp))
    source = temp / 'Library/Application Support/DriveModelStore.sqlite'
    destination = root / 'Library/Application Support/DriveModelStore.sqlite'
    destination.write_bytes(source.read_bytes())
    connection = sqlite3.connect(destination)
    connection.execute('PRAGMA journal_mode=WAL')
    connection.execute('PRAGMA wal_autocheckpoint=0')
    connection.execute('delete from ZDRIVEMODEL where Z_PK=1')
    connection.commit()
    snapshot = {suffix: Path(str(destination) + suffix).read_bytes() for suffix in ('', '-wal', '-shm')}
    connection.close()
    for suffix, data in snapshot.items():
        Path(str(destination) + suffix).write_bytes(data)
    for topic_index, suffix in enumerate(('BreachTopic', 'DwellTopic')):
        original = next(temp.rglob('*.' + suffix + '.sqlite'))
        with sqlite3.connect(original) as reader:
            data = reader.execute('select ZDATA from ZENTRY limit 1').fetchone()[0]
        examples = []
        for index in range(3):
            doc = json.loads(data)
            doc['id'] = base.uid(0xF000 + topic_index * 4 + index)
            examples.append(doc)
        stem = original.stem
        destination = root / 'Library/Application Support/com.eventkit' / stem / original.name
        _history(destination, examples)
    # Remove only this generator's temporary synthetic source tree.
    import shutil  # pylint: disable=import-outside-toplevel
    shutil.rmtree(temp)
    return path, other, destination


def build_container(root):
    build_cache(root)
    return build_recovery(root)


if __name__ == '__main__':
    import sys
    build_container(Path(sys.argv[1]))
