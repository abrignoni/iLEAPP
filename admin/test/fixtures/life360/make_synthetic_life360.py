#!/usr/bin/env python3
"""Build a synthetic Life360 iOS app container for iLEAPP test fixtures.

Every value here is invented: coordinates sit in the Pacific Ocean, identifiers are
fixed UUID-shaped strings, names are placeholders. The layout and key names follow
the schema the life360Awareness and life360Stores modules document.

Usage: make_synthetic_life360.py OUT_DIR [--containers N]
"""
import json
import os
import plistlib
# plistlib exports its format enum members dynamically; astroid does not see this member.
from plistlib import FMT_BINARY  # pylint: disable=no-name-in-module
from pathlib import Path
import sqlite3
import sys
import uuid
import zipfile
from datetime import datetime, timezone

COCOA = 978307200
# 2026-01-15 12:00:00 UTC
T0 = int(datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc).timestamp())


def uid(n):
    return str(uuid.UUID(int=n)).upper()


def lid(n):
    return str(uuid.UUID(int=0xA000 + n))


USER = lid(1)
MEMBER2 = lid(2)
CIRCLE1 = lid(10)
CIRCLE2 = lid(11)
PLACE_HOME = lid(20)
PLACE_WORK = lid(21)
TRIP1 = '20260115AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
TRIP2 = '20260115BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
SESSION1 = uid(0x501)
SESSION2 = uid(0x502)
LAT, LON = 0.5, -150.5  # open ocean


def loc(ts_unix, dlat=0.0, dlon=0.0, speed=1.5, course=90.0, tag='undefined', origin='locationEngine'):
    return {
        'timestamp': ts_unix - COCOA, 'coordinate': {'latitude': LAT + dlat, 'longitude': LON + dlon},
        'altitude': 10.5, 'horizontalAccuracy': 5.0, 'verticalAccuracy': 3.0, 'speed': speed,
        'course': course, 'speedAccuracy': -1, 'courseAccuracy': -1,
        'lmode': {'serverTag': {'_0': tag}}, 'sampleOrigin': {origin: {}},
        'sourceInformation': {'isSimulatedBySoftware': False, 'isProducedByAccessory': False},
    }


def topic_db(path, entries, wal=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    con = sqlite3.connect(path)
    if wal:
        con.execute('PRAGMA journal_mode=WAL')
    con.executescript('''
        CREATE TABLE ZENTRY (Z_PK INTEGER PRIMARY KEY, Z_ENT INTEGER, Z_OPT INTEGER, ZTIMESTAMP FLOAT,
                             ZID BLOB, ZDATA BLOB);
        CREATE TABLE ZSUBSCRIPTION (Z_PK INTEGER PRIMARY KEY, Z_ENT INTEGER, Z_OPT INTEGER,
                                    ZLASTSENTTIMESTAMP FLOAT, ZIDENTIFIER VARCHAR);
    ''')
    if wal:
        con.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    for i, (ts, doc) in enumerate(entries, 1):
        doc.setdefault('id', uid(0x9000 + i))
        doc.setdefault('timestamp', ts)
        con.execute('INSERT INTO ZENTRY VALUES (?,1,1,?,?,?)',
                    (i, float(ts), uuid.UUID(doc['id']).bytes, json.dumps(doc).encode()))
    con.commit()
    # Preserve a load-bearing WAL in the fabricated evidence, not a fully checkpointed database.
    snapshot = {suffix: Path(path + suffix).read_bytes() for suffix in ('', '-wal', '-shm')} if wal else {}
    con.close()
    for suffix, data in snapshot.items():
        Path(path + suffix).write_bytes(data)


def drive_doc(ts, event, waypoints, incidents, summary, session):
    drive = {'id': uid(0x700 + int(ts) % 1000), 'tripID': TRIP1, 'timestamp': ts - COCOA,
             'eventType': {event: {}}, 'coordinate': {'latitude': LAT, 'longitude': LON + 0.01},
             'waypoints': waypoints, 'drivingIncidents': incidents}
    if summary:
        drive.update({'distance': 1234.5, 'averageSpeed': 12.5, 'topSpeed': 22.0, 'score': 80,
                      'completionState': 'complete', 'driveType': 2, 'sdkVendor': 'synthetic', 'sdkVersion': '1.0'})
    return {'version': 4, 'payloadVersion': 1, 'sequenceNumber': 1, 'userId': USER, 'sessionID': session,
            'thirdPartyID': TRIP1, 'startTime': T0 + 100 - COCOA, 'drive': drive,
            'movementPOIData': {'startPoiDisplayable': {'scoring': 'distanceSigmoid', 'pois': [
                {'source': 'rgc', 'streetAddress': '1 Example Way', 'city': 'Nowhere', 'region': 'ZZ',
                 'countryCode': 'XX'}]}} if summary else {}}


def wp(ts, i, source='location_engine'):
    point = {'timestamp': ts, 'coordinate': {'latitude': LAT + i * 0.001, 'longitude': LON + i * 0.001},
             'speed': 10.0 + i, 'horizontalAccuracy': 4.0, 'source': source}
    if source == 'location_engine':
        point.update({'course': 45.0, 'courseAccuracy': -1, 'speedAccuracy': -1, 'verticalAccuracy': 2.0,
                      'modality': 'driving', 'confidence': '90'})
    return point


def build_container(root):
    ek = os.path.join(root, 'Library', 'Application Support', 'com.eventkit')
    t = lambda name: os.path.join(ek, name, name + '.sqlite')

    topic_db(t('com.life360.DeviceLocationTopic'), [
        (T0 + 10, {'version': 4, 'location': loc(T0 + 9), 'bufferedSamples': [loc(T0 + 5), loc(T0 + 9, 0.0005)]}),
        (T0 + 70, {'version': 4, 'location': loc(T0 + 69, 0.001), 'bufferedSamples': [loc(T0 + 69, 0.001)]}),
    ], wal=True)
    topic_db(t('com.life360.AwarenessEngine.Topics.FailedLocationTopic'), [
        (T0 + 20, {'version': 2, 'location': loc(T0 + 19, tag='drive'), 'batteryState': {'state': 'unknown', 'level': -100},
                   'ssid': '', 'bssid': '', 'wifiEnabled': False, 'driveDetectionStatus': 'OFF'}),
    ])
    incidents = [{'type': 'distractedDriving', 'timestamp': T0 + 150, 'coordinate': {'latitude': LAT + 0.002, 'longitude': LON}}]
    topic_db(t('com.life360.event_history_core.topics.drive_session'), [
        (T0 + 100, drive_doc(T0 + 100, 'start', [], [], False, SESSION1)),
        (T0 + 160, drive_doc(T0 + 160, 'update', [wp(T0 + 120, 1), wp(T0 + 140, 2)], incidents, False, SESSION1)),
        (T0 + 300, drive_doc(T0 + 300, 'end', [wp(T0 + 280, 3)], incidents, True, SESSION1)),
    ])
    topic_db(t('com.life360.L360Driving.Topics.DriveEvent'), [
        (T0 + 100, {'version': 3, 'startTime': T0 + 100 - COCOA, 'drive': drive_doc(T0 + 100, 'start', [], [], False, '')['drive']}),
        (T0 + 300, {'version': 3, 'startTime': T0 + 100 - COCOA,
                    'drive': drive_doc(T0 + 300, 'end', [wp(T0 + 140, 2, 'drive_engine'), wp(T0 + 200, 4, 'drive_engine')],
                                       incidents, True, '')['drive']}),
    ])
    route = [{'timestamp': T0 + 400 - COCOA, 'latitude': LAT, 'longitude': LON, 'horizontalAccuracy': 20.0,
              'confidence': '67', 'modality': 'unknown', 'source': 'location_engine'}]
    topic_db(t('com.life360.event_history_core.topics.trip_session'), [
        (T0 + 400, {'version': 1, 'payloadVersion': 1, 'sequenceNumber': 2, 'userId': USER, 'sessionId': SESSION2,
                    'algorithm': 'TRIPv2', 'modality': 'unknown', 'confidence': 'low', 'eventType': {'start': {}},
                    'startTime': T0 + 390 - COCOA, 'currentTimestamp': T0 + 399 - COCOA,
                    'emissionTimestamp': T0 + 400 - COCOA, 'distance': 0.0, 'route': route}),
    ])
    topic_db(t('com.life360.AwarenessEngine.Topics.DriveCancellationTopic'), [
        (T0 + 500, {'version': 1, 'driveSessionId': SESSION1, 'reason': 'arity_termination'}),
    ])
    topic_db(t('com.life360.AwarenessEngine.Topics.TripCancellationTopic'), [
        (T0 + 510, {'version': 1, 'tripSessionId': SESSION2, 'reason': 'replaced_by_drive'}),
    ])
    dwell = lambda ts, ev, state: {'version': 2, 'dwell': {
        'id': uid(0x800), 'algorithm': 'CLPv1', 'timestamp': ts - COCOA, 'eventType': {ev: {}}, 'state': {state: {}},
        'location': {'startTime': T0 + 600, 'endTime': ts, 'latitude': LAT, 'longitude': LON, 'horizontalAccuracy': 30.0}}}
    topic_db(t('com.life360.AwarenessEngine.Topics.DwellTopic'), [
        (T0 + 700, dwell(T0 + 700, 'start', 'dwelling')), (T0 + 800, dwell(T0 + 800, 'update', 'dwelling'))])
    session_dwell = dwell(T0 + 900, 'end', 'moving')
    session_dwell.update({'sequenceNumber': 3, 'userId': USER, 'sessionID': uid(0x503)})
    session_dwell['dwell']['poiData'] = {'poiDisplayable': {'scoring': 'distanceSigmoid', 'pois': [
        {'source': 'rgc', 'streetAddress': '2 Example Way', 'city': 'Nowhere', 'region': 'ZZ', 'countryCode': 'XX'}]}}
    topic_db(t('com.life360.event_history_core.topics.dwell_session'), [
        (T0 + 800, dict(dwell(T0 + 800, 'update', 'dwelling'), sequenceNumber=2, userId=USER, sessionID=uid(0x503))),
        (T0 + 900, session_dwell)])
    topic_db(t('com.life360.AwarenessEngine.Topics.BreachTopic'), [
        (T0 + 1000, {'version': 1, 'location': loc(T0 + 999, origin='other'), 'wifi': {'algorithm': 'CLPv1', 'enabled': False},
                     'places': [{'id': PLACE_HOME, 'name': 'Home', 'circleId': CIRCLE1, 'direction': 'egress',
                                 'algorithm': 'CLPv1', 'distanceToFence': {'value': 42.0, 'unit': {'symbol': 'm',
                                 'converter': {'coefficient': 1, 'constant': 0}}}}]}),
    ])
    import base64
    raw_loc = {'timestamp': T0 + 1100, 'confidence': 'high', 'location': loc(T0 + 1099)}
    raw_drive = {'version': 3, 'timestamp': T0 + 300, 'startTime': T0 + 100 - COCOA,
                 'drive': drive_doc(T0 + 300, 'end', [], incidents, True, '')['drive']}
    topic_db(t('com.life360.activity_recognition.topics.active_modality'), [
        (T0 + 1100, {'version': 1, 'modality': 'driving', 'rawEventType': 'modalityLocation',
                     'rawEvent': base64.b64encode(json.dumps(raw_loc).encode()).decode()}),
        (T0 + 1101, {'version': 1, 'modality': 'unknown', 'rawEventType': 'driveEvent',
                     'rawEvent': base64.b64encode(json.dumps(raw_drive).encode()).decode()}),
    ])

    # Core Data stores
    app = os.path.join(root, 'Library', 'Application Support')
    con = sqlite3.connect(os.path.join(app, 'DriveModelStore.sqlite'))
    con.executescript('''
        CREATE TABLE ZDRIVEMODEL (Z_PK INTEGER PRIMARY KEY, Z_ENT INTEGER, Z_OPT INTEGER, ZDISTRACTEDCOUNT INTEGER,
          ZDRIVETYPE INTEGER, ZHARDBRAKINGCOUNT INTEGER, ZRAPIDACCELERATIONCOUNT INTEGER, ZSCORE INTEGER,
          ZSPEEDINGCOUNT INTEGER, ZUSERMODE INTEGER, ZUSERTAG INTEGER, ZAVERAGESPEED FLOAT, ZCREATEDAT TIMESTAMP,
          ZDISTANCE FLOAT, ZDURATION FLOAT, ZENDTIME TIMESTAMP, ZLASTRETRIEVED TIMESTAMP, ZSTARTTIME TIMESTAMP,
          ZTOPSPEED FLOAT, ZUPDATEDAT TIMESTAMP, ZID VARCHAR, ZUSERID VARCHAR, ZRIDESHAREVENDOR VARCHAR);
        CREATE TABLE ZCIRCLEDRIVEMODEL (Z_PK INTEGER PRIMARY KEY, Z_ENT INTEGER, Z_OPT INTEGER, ZDRIVE INTEGER,
          ZCIRCLEID VARCHAR, ZID VARCHAR);
    ''')
    for i, (user, start) in enumerate([(USER, T0), (MEMBER2, T0 + 3600), (USER, T0 + 7200)], 1):
        c = start - COCOA
        con.execute('INSERT INTO ZDRIVEMODEL VALUES (?,1,1,?,2,0,1,80,2,0,-1,11.5,?,2500.0,600.0,?,?,?,20.0,?,?,?,NULL)',
                    (i, i, c + 700, c + 600, c + 800.5, c, c + 700, lid(30 + i), user))
        con.execute('INSERT INTO ZCIRCLEDRIVEMODEL VALUES (?,2,1,?,?,?)', (i, i, CIRCLE1, lid(40 + i)))
    con.execute('INSERT INTO ZCIRCLEDRIVEMODEL VALUES (4,2,1,1,?,?)', (CIRCLE2, lid(44)))
    con.commit()
    con.close()

    con = sqlite3.connect(os.path.join(app, 'L360CoreDataStore.sqlite'))
    con.executescript('''
        CREATE TABLE ZPLACEMODEL (Z_PK INTEGER PRIMARY KEY, Z_ENT INTEGER, Z_OPT INTEGER, ZHASALERTS INTEGER, ZTYPE INTEGER,
          ZLASTRETRIEVED TIMESTAMP, ZLATITUDE FLOAT, ZLONGITUDE FLOAT, ZRADIUS FLOAT, ZADDRESS VARCHAR, ZCIRCLEID VARCHAR,
          ZID VARCHAR, ZNAME VARCHAR, ZOWNERID VARCHAR, ZSELECTIONTYPE VARCHAR, ZSOURCE VARCHAR, ZSOURCEID VARCHAR, ZCATEGORY VARCHAR);
        CREATE TABLE ZPLACEALERTMODEL (Z_PK INTEGER PRIMARY KEY, Z_ENT INTEGER, Z_OPT INTEGER, ZRECEIVESARRIVALALERTS INTEGER,
          ZRECEIVESDEPARTUREALERTS INTEGER, ZLASTRETRIEVED TIMESTAMP, ZCIRCLEID VARCHAR, ZID VARCHAR, ZMEMBERID VARCHAR, ZPLACEID VARCHAR);
        CREATE TABLE ZDRIVERREPORTMODEL (Z_PK INTEGER PRIMARY KEY, Z_ENT INTEGER, Z_OPT INTEGER, ZREPORTTYPE INTEGER, ZWEEKOFFSET INTEGER,
          ZWEEK INTEGER, ZCOVERAGEENDDATE TIMESTAMP, ZCOVERAGESTARTDATE TIMESTAMP, ZLASTRETRIEVED TIMESTAMP, ZCIRCLEID VARCHAR,
          ZID VARCHAR, ZMEMBERID VARCHAR, ZTIMEZONE VARCHAR);
        CREATE TABLE ZDRIVERREPORTITEMMODEL (Z_PK INTEGER PRIMARY KEY, Z_ENT INTEGER, Z_OPT INTEGER, ZCRASHCOUNT INTEGER,
          ZDISTRACTEDCOUNT INTEGER, ZHARDBRAKINGCOUNT INTEGER, ZRAPIDACCELERATIONCOUNT INTEGER, ZSPEEDINGCOUNT INTEGER, ZTRIPS INTEGER,
          ZDRIVERREPORTDAILY INTEGER, ZDRIVERREPORTWEEK INTEGER, ZDISTANCE FLOAT, ZDURATION FLOAT, ZENDDAY TIMESTAMP,
          ZLASTRETRIEVED TIMESTAMP, ZSCORE FLOAT, ZSTARTDAY TIMESTAMP, ZTOPSPEED FLOAT, ZID VARCHAR);
    ''')
    c = T0 - COCOA
    con.execute("INSERT INTO ZPLACEMODEL VALUES (1,1,1,1,0,?,?,?,150.0,NULL,?,?,'Home',?,'','u',NULL,NULL)", (c, LAT, LON, CIRCLE1, PLACE_HOME, USER))
    con.execute("INSERT INTO ZPLACEMODEL VALUES (2,1,1,0,0,?,?,?,250.0,'3 Example Way',?,?,'Work',?,'','l',?,NULL)",
                (c, LAT + 0.1, LON + 0.1, CIRCLE1, PLACE_WORK, USER, lid(50)))
    con.execute("INSERT INTO ZPLACEALERTMODEL VALUES (1,2,1,1,1,?,?,?,?,?)", (c, CIRCLE1, lid(60), USER, PLACE_HOME))
    con.execute("INSERT INTO ZPLACEALERTMODEL VALUES (2,2,1,0,1,?,?,?,?,?)", (c, CIRCLE1, lid(61), MEMBER2, PLACE_HOME))
    con.execute("INSERT INTO ZDRIVERREPORTMODEL VALUES (1,3,1,1,0,2603,?,?,?,?,?,?,'Etc/UTC')",
                (c + 7 * 86400, c, c + 8 * 86400, CIRCLE1, lid(70), USER))
    con.execute("INSERT INTO ZDRIVERREPORTMODEL VALUES (2,3,1,2,0,2603,?,?,?,NULL,?,?,'Etc/UTC')",
                (c + 7 * 86400, c, c + 8 * 86400, lid(71), USER))
    con.execute("INSERT INTO ZDRIVERREPORTITEMMODEL VALUES (1,4,1,0,3,1,0,2,4,1,NULL,12000.0,1800.0,?,?,NULL,?,25.0,?)",
                (c + 86400, c + 8 * 86400, c, lid(80)))
    con.execute("INSERT INTO ZDRIVERREPORTITEMMODEL VALUES (2,4,1,0,9,2,1,5,11,NULL,2,50000.0,7200.0,?,?,0.0,?,30.0,?)",
                (c + 7 * 86400, c + 8 * 86400, c, lid(81)))
    con.commit()
    con.close()

    # Preferences plist
    prefs = {
        'com.life360.datakit.CurrentUser.Type': json.dumps([{
            'id': USER, 'firstName': 'Pat', 'lastName': 'Example', 'loginEmail': 'pat@example.invalid',
            'loginPhone': '+15555550100', 'created': T0 - 86400 * 400 - COCOA, 'dob': T0 - 86400 * 365 * 30 - COCOA,
            'avatar': 'https://example.invalid/avatar.jpeg', 'locale': 'en_US', 'multiDevice': False,
            'settings': {'timeZone': {'identifier': 'Etc/UTC'}, 'unitOfMeasure': 'i', 'dateFormat': 'd'},
            'lastRetrieved': T0 - COCOA, 'managedUsers': []}]).encode(),
        'com.life360.datakit.Circle.Type': json.dumps([{'id': CIRCLE1, 'name': 'Family', 'type': 'basic',
                                                        'createdAt': T0 - 86400 * 300 - COCOA, 'lastRetrieved': T0 - COCOA}]).encode(),
        'com.life360.datakit.CircleCode.Type': json.dumps([{'circleID': CIRCLE1, 'code': 'ABC-123',
                                                            'deeplink': 'https://example.invalid/join', 'message': 'Join',
                                                            'expiration': T0 + 86400 * 3 - COCOA, 'lastRetrieved': T0 - COCOA},
                                                          {'circleID': CIRCLE2, 'code': 'XYZ-789',
                                                           'deeplink': 'https://example.invalid/other-circle',
                                                           'expiration': T0 + 86400 - COCOA,
                                                           'lastRetrieved': T0 - COCOA}]).encode(),
        'com.life360.datakit.MemberCircleSettings.Type': json.dumps([{
            'memberID': USER, 'circleID': CIRCLE1, 'lastRetrieved': T0 - COCOA,
            'store': ['driveDetectionStatus', 'Ik9OIg==', 'driveAlertsEnabled', 'dHJ1ZQ==']}]).encode(),
        'com.life360.datakit.CircleSettings.Type': json.dumps([{
            'circleID': CIRCLE1, 'lastRetrieved': T0 - COCOA, 'store': ['crashDetectionLimitationStatus', 'bm90LWFjY2VwdGVk']}]).encode(),
        'com.life360.datakit.UserSettings.Type': json.dumps([{
            'lastRetrieved': T0 - COCOA, 'store': ['contactsSettings', 'eyJ2aXNpYmlsaXR5IjoxfQ==', 'broken', '!!notbase64']}]).encode(),
        'deviceRegistrationInfo': {'appVersion': '26.34.0.5', 'deviceName': 'iPhone', 'deviceType': 'iphone',
                                   'deviceVersion': '18.6', 'deviceUdid': uid(0x1234), 'appId': 'safetymap',
                                   'carrier': 'Example Mobile', 'deviceToken': 'ff' * 8, 'deviceModel': 'iPhone15,2'},
        'lpseRegistrationInfo': {'appVersion': '26.34.0.5', 'appID': 'safetymap_lpse', 'deviceID': uid(0x1234)},
        'kL360UserDefaultsStoreloggedInUserData': {'dateOfBirth': float(T0 - 86400 * 365 * 30), 'initialAppRole': 'owner',
                                                   'premiumDispatchEnabled': False, 'createdAt': float(T0 - 86400 * 400)},
        'L360LocationHealthStorage': json.dumps({'device_app_logged_in': {
            'name': 'synthetic', 'total': 1, 'time': float(T0)}}).encode(),
        'kL360UserDefaultsStoreuserEmail': 'pat@example.invalid', 'kL360UserDefaultsStoreuserPhone': '+15555550100',
        'kL360UserDefaultsStoreuserFirstName': 'Pat', 'kL360UserDefaultsStoreuserLastName': 'Example',
        'kL360UserDefaultsStoreselectedCircleID': CIRCLE1, 'firstCircleID': CIRCLE1, 'memberDeviceID': uid(0x1234),
        'deviceUUID': uid(0x1234), 'FirstLaunch': False, 'CURRENTTRIPID': TRIP1, 'TripCompletionFlag': True,
        'queryLocationPermissionAccess': 'always', 'preciseLocationPermissionsAccess': True,
        'memberRoles': {CIRCLE1: 1},
        'AwarenessEngineGate.BreachRule.breachStateCache': json.dumps({'stateDictionary': {
            PLACE_HOME: {'id': PLACE_HOME, 'name': 'Home', 'circleId': CIRCLE1, 'direction': 'egress', 'latitude': LAT,
                         'longitude': LON, 'radius': {'value': 150.0, 'unit': {'symbol': 'm', 'converter': {'coefficient': 1, 'constant': 0}}}},
            PLACE_WORK: {'id': PLACE_WORK, 'name': 'Work', 'circleId': CIRCLE1, 'direction': 'ingress', 'latitude': LAT + 0.1,
                         'longitude': LON + 0.1, 'radius': {'value': 250.0, 'unit': {'symbol': 'm', 'converter': {'coefficient': 1, 'constant': 0}}}},
        }}).encode(),
        'pop-dwell_seen': plistlib.dumps([{'recurrenceId': 'r1', 'circleId': CIRCLE1, 'latitude': LAT + 0.2, 'longitude': LON + 0.2,
                                           'date': datetime(2026, 1, 10, 8, 0, 0)}], fmt=FMT_BINARY),
        'DriveEventPublishingComponent.tripStartTimes': {TRIP1: float(T0 + 100), TRIP2: float(T0 - 86400 * 30)},
    }
    os.makedirs(os.path.join(root, 'Library', 'Preferences'), exist_ok=True)
    with open(os.path.join(root, 'Library', 'Preferences', 'com.life360.safetymap.plist'), 'wb') as fh:
        plistlib.dump(prefs, fh, fmt=FMT_BINARY)
    build_location_state(root)


def build_location_state(root):
    """An NSKeyedArchiver location_state.data: two samples in location and one unsentFilteredSample."""
    objects = ['$null']

    def add(obj):
        objects.append(obj)
        return plistlib.UID(len(objects) - 1)

    date_class = add({'$classname': 'NSDate', '$classes': ['NSDate', 'NSObject']})
    sample_class = add({'$classname': 'L360CLLocation', '$classes': ['L360CLLocation', 'NSObject']})
    array_class = add({'$classname': 'NSMutableArray', '$classes': ['NSMutableArray', 'NSArray', 'NSObject']})
    state_class = add({'$classname': 'L360LocationPersistentState', '$classes': ['L360LocationPersistentState',
                                                                                 'NSObject']})

    def sample(stamp, offset, bssid):
        return add({'$class': sample_class, 'latitude': LAT + offset, 'longitude': LON, 'altitude': 3.0,
                    'speed': 1.5, 'course': 90.0, 'horizontalaccuracy': 10.0, 'verticalaccuracy': 4.0,
                    'locationmode': 2, 'wifi_enabled': True, 'mutated_sample': False,
                    'json_violation_string': add(''), 'wifi_bssid': add(bssid),
                    'timestamp': add({'$class': date_class, 'NS.time': float(stamp - COCOA)}),
                    'sampleTimestamp': add({'$class': date_class, 'NS.time': float(stamp + 0.25 - COCOA)})})

    samples = [sample(T0 + 500, 0.0, '2:0:5e:0:53:1'), sample(T0 + 560, 0.0005, '')]
    unsent = sample(T0 + 620, 0.001, '')
    array = add({'$class': array_class, 'NS.objects': samples})
    root_uid = add({'$class': state_class, 'location': array, 'unsentFilteredSample': unsent})
    archive = {'$version': 100000, '$archiver': 'NSKeyedArchiver', '$top': {'root': root_uid}, '$objects': objects}
    os.makedirs(os.path.join(root, 'Library', 'Application Support'), exist_ok=True)
    with open(os.path.join(root, 'Library', 'Application Support', 'location_state.data'), 'wb') as fh:
        plistlib.dump(archive, fh, fmt=FMT_BINARY)


def main():
    out = sys.argv[1]
    containers = int(sys.argv[sys.argv.index('--containers') + 1]) if '--containers' in sys.argv else 1
    for n in range(containers):
        root = os.path.join(out, 'private', 'var', 'mobile', 'Containers', 'Data', 'Application', uid(0xC0 + n))
        build_container(root)
        with open(os.path.join(root, '.com.apple.mobile_container_manager.metadata.plist'), 'wb') as fh:
            plistlib.dump({'MCMMetadataIdentifier': 'com.life360.safetymap'}, fh)
    zpath = out.rstrip('/') + '.zip'
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as zf:
        for dp, _dn, fn in os.walk(out):
            for f in fn:
                full = os.path.join(dp, f)
                zf.write(full, os.path.relpath(full, out))
    print(zpath)


if __name__ == '__main__':
    main()
