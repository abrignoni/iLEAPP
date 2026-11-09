#!/usr/bin/env python3
"""Build SYNTHETIC PayPal (com.yourcompany.PPClient) containers (fabricated values, no data from any device).

File names, table names, column names and key names follow what the paypal artifacts read in the
Data container and the app-group container of PayPal 8.98 to 8.107 full file
systems. Every value below is invented: accounts are ``*.example.invalid``, ids start with ``SYNTH``,
phone numbers are 555-01xx style and every date derives from the fixed epoch below, so the output is
reproducible.

    python synthetic_paypal.py full out.tar.gz     # every store populated, plus a decoy app container
    python synthetic_paypal.py empty out.tar.gz    # stores present but empty, as in real installs
    python synthetic_paypal.py sparse out.tar.gz   # stores missing or without the expected tables

``write_archive(path, variant)`` packs the two containers (and, for ``full``, a decoy container of
another bundle id that holds a Thales log and an mParticle database which the
artifacts must not report) below ``private/var/mobile/Containers``.
"""

import datetime
import io
import json
import plistlib
import sqlite3
import sys
import tarfile
import tempfile
from pathlib import Path

BUNDLE = 'com.yourcompany.PPClient'
GROUP = 'group.com.yourcompany.PPClient'
DATA_UUID = '11111111-AAAA-4AAA-8AAA-000000000001'
GROUP_UUID = '22222222-BBBB-4BBB-8BBB-000000000002'
DECOY_UUID = '33333333-CCCC-4CCC-8CCC-000000000003'

EPOCH = datetime.datetime(2026, 5, 9, 12, 0, 0)         # naive UTC, as a plist date is
UNIX_EPOCH = int(EPOCH.replace(tzinfo=datetime.timezone.utc).timestamp())

DATA_ROOT = f'private/var/mobile/Containers/Data/Application/{DATA_UUID}'
GROUP_ROOT = f'private/var/mobile/Containers/Shared/AppGroup/{GROUP_UUID}'
DECOY_ROOT = f'private/var/mobile/Containers/Data/Application/{DECOY_UUID}'


def keyed_archive(mapping):
    """An NSKeyedArchiver plist holding one NSDictionary of simple values."""
    # objects: 0 $null, 1 the dictionary, 2 its class, then a key and a value per entry
    objects = ['$null', None, {'$classname': 'NSDictionary', '$classes': ['NSDictionary', 'NSObject']}]
    keys, values = [], []
    for key, value in mapping.items():
        objects.append(key)
        keys.append(plistlib.UID(len(objects) - 1))
        objects.append(value)
        values.append(plistlib.UID(len(objects) - 1))
    objects[1] = {'NS.keys': keys, 'NS.objects': values, '$class': plistlib.UID(2)}
    return plistlib.dumps({'$version': 100000, '$archiver': 'NSKeyedArchiver',
                           '$top': {'root': plistlib.UID(1)}, '$objects': objects}, fmt=plistlib.PlistFormat.FMT_BINARY)


def metadata_plist(identifier):
    return plistlib.dumps({'MCMMetadataIdentifier': identifier, 'MCMMetadataVersion': 1,
                           'MCMMetadataUUID': 'SYNTHETIC'}, fmt=plistlib.PlistFormat.FMT_BINARY)


def _sqlite(statements, rows=()):
    """Bytes of a SQLite database built from CREATE statements and (sql, params) rows."""
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / 'build.db'
        db = sqlite3.connect(path)
        for statement in statements:
            db.execute(statement)
        for sql, params in rows:
            db.execute(sql, params)
        db.commit()
        db.close()
        return path.read_bytes()


def app_prefs(variant):
    def stamp(hours):
        return EPOCH + datetime.timedelta(hours=hours)

    prefs = {
        'timestampAppInBGUserDefaultsKey': stamp(3),
        'remoteConfigLastUpdateTime': stamp(2),
        'rampConfigLastUpdateTime': stamp(2),
        'adj_skad_register_call_time': stamp(-48),
        'KronosStableTime': {'Timestamp': float(UNIX_EPOCH + 600), 'Offset': 0.004, 'Uptime': 90000.0},
        'OptInStatus': 'Declined',
        'gdprConsented': True,
        'gdprConsentedDate': stamp(-24),
        'home.appLocale': 'en_US',
        'is_app_reinstalled': False,
        'com.directdeposit.accountnumber': '',
        'com.directdeposit.accounttype': '',
        'com.directdeposit.routingnumber': '',
        'appLaunchedFirstTime:8.9.1': True,
        'appLaunchedFirstTime:8.98.0': True,
        'appLaunchedFirstTime:8.107.2': True,
        'isPasskeyLoginEnabled': True,                        # a server-supplied flag: must not be reported
        'RCSDefault-hubCaching': True,
    }
    if variant == 'full':
        prefs.update({
            'com.paypal.pushNotification.preference.SYNTHACCT0001A': {
                'SendMoney': 'true', 'ReceiveMoney': 'true', 'Purchase': 'false', 'GenericMarketing': 'false'},
            'socialTooltipViewedFirstTimeShown.SYNTHACCT0001A': True,
            'pat.example@example.invalid.hasUserSeenFXPopup': True,
        })
    return prefs


def group_prefs(variant):
    prefs = {
        'OptInStatus': 'Declined',
        'com.paypalAppleLocale': 'en_US',
        'com.paypalloginSkipCount': 2,
        'com.paypalPKPeerPaymentRecurringPaymentsLastUpdatedKey': EPOCH + datetime.timedelta(hours=1),
        'OptInData': {'pn_sync_time': '09-May-2026 08:00 AM', 'pn_user': 'SYNTHACCT0001A',
                      'pn_opt_in': 'Declined', 'pn_is_subscribed': False, 'pn_version': 1},
    }
    if variant != 'sparse':
        prefs['com.paypalRememberedUserV1'] = keyed_archive({
            'RememberedUserDisplayName': 'Pat Example',
            'RememberedUsername': 'pat.example@example.invalid',
            'RememberedUserPrimaryEmail': 'pat.example@example.invalid',
            'RememberedUserPrimaryPhone': '5550100',
            'RememberedAccountProfileId': 'SYNTHACCT0001A',
            'RememberedAccountType': 1,
            'RememberedUserCountryCode': 'US',
            'RememberedUserPhotoURL': 'https://img.example.invalid/synthetic/profile.png',
            'RememberedUserKMLISupportedForCountry': False,
        })
    return prefs


def thales_log(variant):
    header = 'TSH-48bbb8 PayPal 50   iOS 26.2 iPhone99,9\na50c3659fa 2.0.0 Unknown Unknown\n'
    body = []
    for minutes, tag, rest in ((0, 'SDKV', '6 7.2.3.rc01 (Release)'), (0, 'LPIS', '7 S.TSHP.CWVPC'),
                               (1, 'storage', '4 TPBS.IDTE'), (30, 'SDKV', '6 7.2.3.rc01 (Release)'),
                               (31, 'LPIC', '3 MGU.GWIDI.(null) [260]'), (240, 'SDKV', '6 7.2.3.rc01 (Release)')):
        moment = EPOCH + datetime.timedelta(minutes=minutes, milliseconds=871)
        body.append(f'{moment:%Y-%m-%dT%H:%M:%S}:{moment.microsecond // 1000:03d}Z {tag} {rest}')
        if tag == 'LPIS' and variant == 'full':
            body.append('    NSLocalizedDescription = "synthetic multi-line continuation";')
    if variant == 'sparse':
        body = ['not a log line']
    return (header + '\n'.join(body) + '\n').encode()


def url_cache(variant):
    tables = ['CREATE TABLE cfurl_cache_response(entry_ID INTEGER PRIMARY KEY, version INTEGER, hash_value INTEGER, '
              'storage_policy INTEGER, request_key TEXT UNIQUE, time_stamp DATETIME, partition TEXT)',
              'CREATE TABLE cfurl_cache_receiver_data(entry_ID INTEGER PRIMARY KEY, isDataOnFS INTEGER, receiver_data BLOB)',
              'CREATE TABLE cfurl_cache_blob_data(entry_ID INTEGER PRIMARY KEY, response_object BLOB, request_object BLOB, '
              'proto_props BLOB, user_info BLOB)']
    if variant == 'sparse':
        return _sqlite(['CREATE TABLE other(a)'])
    rows = []
    cached = EPOCH.replace(microsecond=0)
    entries = [
        (f'https://slc.stats.paypal.com/counter1.cgi?p=SYNTHPAGEID000000000000000000A1&i=192.0.2.10&t={UNIX_EPOCH}.250000&a=10', 0),
        (f'https://lvs.stats.paypal.com/counter2.cgi?p=SYNTHPAGEID000000000000000000A2&i=10.0.0.7&t={UNIX_EPOCH + 61}.500000&a=10', 61),
        ('https://analytics.adjust.com/session?app_token=SYNTHTOKEN', 90),
        ('https://www.paypalobjects.com/rdaAssets/magnes/synthetic.json', 120),
        ('https://api-m.paypal.com/v1/synthetic/path', 150),
    ]
    if variant == 'empty':
        entries = entries[:0]
    for number, (url, offset) in enumerate(entries, 1):
        stamp = (cached + datetime.timedelta(seconds=offset)).strftime('%Y-%m-%d %H:%M:%S')
        rows.append(('INSERT INTO cfurl_cache_response VALUES(?,?,?,?,?,?,?)', (number, 0, number, 0, url, stamp, None)))
    return _sqlite(tables, rows)


def analytics_db(variant):
    schema = ['CREATE TABLE events(event_id varchar(100), event_session varchar(100), event_payload varchar(4000), '
              'event_ts REAL, api_version varchar(10), original_event varchar(4000), dispatch_status INT, '
              'network_dispatch_try_count INT)']
    if variant == 'sparse':
        return _sqlite(['CREATE TABLE other(a)'])
    rows = []
    if variant == 'full':
        events = [
            (0, {'event_name': 'appTransition:didFinishLaunching', 'page': 'mobile:consapp:apptransition::didfinishlaunching',
                 'pgrp': 'mobile:consapp:apptransition', 'evnt_type': 'ac', 'channel': 'Mobile', 'network_type': 'wifi',
                 'wifi': True, 'ui_mode': 'light', 'device_orientation': 'portrait', 'is_device_locked': 'NO',
                 'sessn_id': 'SYNTH-SESSION-1', 'cust_id': 'SYNTHCUST0001', 'visitor_id': 'SYNTHVISITOR01'}),
            (45, {'eventName': 'authentication_queued_im', 'page': 'mobile:consapp:authentication::queued',
                  'login_method': 'passkey', 'auth_state': 'Unknown', 'flow': 'triggerProactiveLogin',
                  'api_response': 'synthetic', 'wifi': False}),
            (90, 'this is not json'),
        ]
        for number, (offset, payload) in enumerate(events, 1):
            if isinstance(payload, dict):
                body, original = json.dumps(payload), json.dumps({k: v for k, v in payload.items() if k != 'channel'})
            else:
                body, original = payload, payload
            rows.append(('INSERT INTO events VALUES(?,?,?,?,?,?,?,?)',
                         (f'SYNTH-EVENT-{number}', 'SYNTH-SESSION-1', body, UNIX_EPOCH + offset + 0.5, 'v1', original, -1, 0)))
    return _sqlite(schema, rows)


def mparticle_db(variant):
    if variant != 'full':
        return None
    schema = ['CREATE TABLE sessions(_id INTEGER PRIMARY KEY AUTOINCREMENT, uuid TEXT, start_time REAL, end_time REAL, '
              'background_time REAL, attributes_data BLOB, session_number INTEGER, number_interruptions INTEGER, '
              'event_count INTEGER, suspend_time REAL, length REAL, mpid INTEGER, session_user_ids TEXT)']
    rows = [('INSERT INTO sessions(uuid,start_time,end_time,session_number,number_interruptions,event_count,length) '
             'VALUES(?,?,?,?,?,?,?)', (f'SYNTH-{n}', UNIX_EPOCH - 86400 * n, UNIX_EPOCH - 86400 * n + 87.25, 0, 1, n, 87.25))
            for n in (3, 2, 1)]
    return _sqlite(schema, rows)



def build_members(variant):
    """{archive path: bytes} for one variant."""
    members = {
        f'{DATA_ROOT}/.com.apple.mobile_container_manager.metadata.plist': metadata_plist(BUNDLE),
        f'{GROUP_ROOT}/.com.apple.mobile_container_manager.metadata.plist': metadata_plist(GROUP),
        f'{DATA_ROOT}/Library/Preferences/{BUNDLE}.plist': plistlib.dumps(app_prefs(variant), fmt=plistlib.PlistFormat.FMT_BINARY),
        f'{GROUP_ROOT}/Library/Preferences/{GROUP}.plist': plistlib.dumps(group_prefs(variant), fmt=plistlib.PlistFormat.FMT_BINARY),
        f'{DATA_ROOT}/Library/Application Support/Thales-v2/slog-TSH-48bbb8-01.log': thales_log(variant),
        f'{DATA_ROOT}/Library/Caches/{BUNDLE}/Cache.db': url_cache(variant),
        f'{DATA_ROOT}/Library/Caches/com.paypal.lighthouseanalytics/lighthouseanalytics.db': analytics_db(variant),
    }
    mparticle = mparticle_db(variant)
    if mparticle:
        members[f'{DATA_ROOT}/Documents/mParticle28.db'] = mparticle
    if variant == 'full':
        # A container of another app that reuses the third-party file names; nothing in it may be reported.
        members[f'{DECOY_ROOT}/.com.apple.mobile_container_manager.metadata.plist'] = metadata_plist('com.example.other')
        members[f'{DECOY_ROOT}/Library/Application Support/Thales-v2/slog-TSH-aaaaaa-01.log'] = thales_log('full')
        members[f'{DECOY_ROOT}/Documents/mParticle28.db'] = mparticle_db('full')
    return members


def write_archive(path, variant):
    path = Path(path)
    mode = 'w:gz' if path.name.endswith(('.gz', '.tgz')) else 'w'
    with tarfile.open(path, mode) as archive:
        for name, data in sorted(build_members(variant).items()):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mtime = UNIX_EPOCH
            archive.addfile(info, io.BytesIO(data))


def write_tree(folder, variant):
    """The same members as plain files below folder."""
    for name, data in build_members(variant).items():
        target = Path(folder) / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] not in ('full', 'empty', 'sparse'):
        sys.exit(__doc__)
    write_archive(sys.argv[2], sys.argv[1])
