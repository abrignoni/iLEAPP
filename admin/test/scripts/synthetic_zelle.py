#!/usr/bin/env python3
"""Builds a fully synthetic Zelle (com.zellepay.zelle) app container for the zelle module.

Every value is invented: the bundle id is the real one (the module is gated on it), the container ids are
fabricated, hosts use the reserved .test top-level domain, and all times are fixed. Nothing here comes from a
device or a person.

    python synthetic_zelle.py <output folder>          # writes the case zips under <output folder>/zelle
    python synthetic_zelle.py <output folder> --tree   # also leaves the unpacked container trees
"""
import argparse
import datetime
import fnmatch
import json
import os
import plistlib
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

BUNDLE = 'com.zellepay.zelle'
APP = 'private/var/mobile/Containers/Data/Application'
CONTAINER = 'AAAAAAAA-0000-4000-8000-000000000001'
OTHER_CONTAINER = 'BBBBBBBB-0000-4000-8000-000000000002'
UTC = datetime.timezone.utc
_BINARY = getattr(plistlib, 'FMT_BINARY')

# Epoch used by the fixture: 2026-03-02 14:00:00 UTC
FIRST_OPEN = datetime.datetime(2026, 3, 2, 14, 0, 0, tzinfo=UTC)


def _ts(dt):
    return dt.timestamp()


def sdk_log(include_noise=True):
    """A synthetic risk-SDK log in the same line layout as Documents/log1.txt."""
    out = ['', '']

    def entry(when, level, component, *message):
        out.append(f'+++ [{when.month}-{when.day}-{when.year} {when:%H:%M:%S}] [{level}] [{component}]')
        out.extend(message)
        out.append('')

    t = FIRST_OPEN
    host = 'risk-east.example.test'
    for session in range(3):
        t = FIRST_OPEN + datetime.timedelta(days=session * 3, minutes=session)
        entry(t, 'DEBUG', 'TwoChkCorePlugin', 'Two Core Plugin Start')
        entry(t, 'DEBUG', 'ManagerPlugin', 'Application  has started successfully')
        t += datetime.timedelta(seconds=1)
        entry(t, 'DEBUG', 'TwoChkCorePlugin', 'handle2ChkGuiRequest received: TwoChkGuiReqMsg: GET_APPLICATION_SECRETS')
        if include_noise:
            for sock in range(4):
                entry(t, 'DEBUG', 'HttpPlugin', f'HttpPlugin sending POST on (socket={sock + 3})')
                entry(t, 'DEBUG', 'HttpPlugin', 'Found Dlg in transaction map')
            entry(t, 'DEBUG', 'HttpPlugin', f'send connect request to {host}')
        t += datetime.timedelta(seconds=2)
        entry(t, 'DEBUG', 'HttpPlugin', f'handle post Rsp, connected to siteId:{host}')
        entry(t, 'DEBUG', 'TwoChkCorePlugin', 'Received msg of type GetSecrets, status code =success')
        entry(t, 'DEBUG', 'TwoChkCorePlugin', 'handle2ChkGuiRequest received: TwoChkGuiReqMsg: START_RISK_SESSION')
        entry(t, 'DEBUG', 'TwoChkCorePlugin', 'TCCP::handle2ChkRsp() msgDetails.msgContents.riskReason adddevice')
        entry(t, 'DEBUG', 'TwoChkCorePlugin', 'Received msg of type StartRiskSession, status code =success')
        entry(t, 'DEBUG', 'TwoChkCorePlugin', 'device state set to: DEV_STATE_READY')
        if include_noise:
            entry(t, 'DEBUG', 'TwoChkCorePlugin', 'TCCP Credential Enrolled (0) -> enrolled 256 ')
            entry(t, 'DEBUG', 'TwoChkCorePlugin', 'Router core get environment 1')
        t += datetime.timedelta(minutes=5)
        entry(t, 'DEBUG', 'TwoChkCorePlugin', 'handle2ChkGuiRequest received: TwoChkGuiReqMsg: QUERY_USER_STATE request....')
        entry(t, 'DEBUG', 'TwoChkCorePlugin', 'Received msg of type StateCheck, status code =success')
    t += datetime.timedelta(hours=1)
    entry(t, 'DEBUG', 'TwoChkCorePlugin', 'handle2ChkGuiRequest received: TwoChkGuiReqMsg: DEL_DEVICE request....')
    entry(t, 'DEBUG', 'TwoChkCorePlugin', 'Received msg of type RemoveDevice, status code =success')
    entry(t, 'DEBUG', 'TwoChkCorePlugin', 'device state set to: DEV_STATE_FRESH_INSTALL')
    entry(t, 'DEBUG', 'TwoChkCorePlugin', 'Cleared the credentials!')
    t += datetime.timedelta(seconds=30)
    entry(t, 'ERROR', 'TwoChkCorePlugin', 'No device key to sign anything with..')
    entry(t, 'ERROR', 'HttpPlugin', 'SSL Handshake failed with error & sslErr -9806:0, errno=0')
    entry(t, 'DEBUG', 'TwoChkCorePlugin', 'Received msg of type Connect, status code =MobileAuthStarted')
    return '\n'.join(out) + '\n'


def console_log():
    lines = [
        '2026-03-02 09:00:00.100 Zelle[500:1a0b] [Firebase/Crashlytics] Version 9.9.9',
        "2026-03-02 09:00:05.200 Zelle[500:1a0b] Can't find keyplane that supports type 5 for keyboard iPhone-PortraitTruffle-PhonePad; using 99999_PortraitTruffle_iPhone-Complex-Pad_Default",
        '2026-03-02 09:00:06.300 Zelle[500:1a0b] STEP 1 --- Initializing InAuth Sdk.....',
        '2026-03-02 09:00:06.400 Zelle[500:1a0b] keys: {',
        '    "encryptionPubKey": "SYNTHETIC-NOT-A-KEY",',
        '    "signatureType": "RSA-PSS-SHA1"',
        '}',
        '2026-03-02 09:00:07.000 Zelle[500:1a0b] InAuth Sig files versions: (null)',
        '2026-03-02 09:00:07.500 Zelle[500:1a0b] STEP 2 --- Generate Registration Payload.....',
        '2026-03-02 09:00:08.000 Zelle[500:1a0b] EwsMrdExtension.onGenerateLogs Generating device logs for sessionId: 00000000-0000-4000-8000-0000000000aa',
        '2026-03-02 09:00:08.100 Zelle[500:1a0b] running root detection...',
        '2026-03-02 09:00:08.200 Zelle[500:1a0b] EwsMrdExtension.getRootStatus:: root status is: NotRooted',
        '2026-03-02 09:00:08.300 Zelle[500:1a0b] running malware detection...',
        '2026-03-02 09:00:08.400 Zelle[500:1a0b] EwsMrdExtension.getMalwareStatus:: malware status is: NoMalwareDetected',
        '2026-03-02 09:00:08.500 Zelle[500:1a0b] Root scan list not found',
        '2026-03-04 18:30:00.000 Zelle[777:2c0d] <Google/Utilities/Network/ERROR> Encounter network error. Code, error: -1009',
        '2026-03-04 18:30:00.500 Zelle[777:2c0d] InAuth Sig files versions: 1.2',
    ]
    return '\n'.join(lines) + '\n'


def _archive(obj):
    """NSKeyedArchiver encoding of a flat {str: scalar} NSDictionary."""
    objects = ['$null']
    keys, values = [], []
    objects.append(None)  # index 1 is the dictionary, filled below
    for key, value in obj.items():
        keys.append(plistlib.UID(len(objects)))
        objects.append(key)
    for value in obj.values():
        values.append(plistlib.UID(len(objects)))
        objects.append(value)
    class_index = len(objects)
    objects.append({'$classname': 'NSDictionary', '$classes': ['NSDictionary', 'NSObject']})
    objects[1] = {'NS.keys': keys, 'NS.objects': values, '$class': plistlib.UID(class_index)}
    return plistlib.dumps({'$archiver': 'NSKeyedArchiver', '$version': 100000,
                           '$top': {'root': plistlib.UID(1)}, '$objects': objects}, fmt=_BINARY)


def preferences(full=True):
    prefs = {
        'AccountAssociatedWithUserKey': True,
        'AppAlreadyLaunchedKey': True,
        'PreferencesTouchIDKey': False,
        'PushIDKey': bytes(range(32)),
        'RecipientNameAlertWhitelist': [],
        'SafeUserAlertWhitelist': [],
        'MixpanelRecordEventType': 'DONT_RECORD',
        'qrCodeSeen': True,
    }
    if full:
        prefs['SKPurchaseIntentUpdatesLastChecked'] = 123456789.5
    mix = {
        'mixpanel-AppStore-MPUserId': 'synthetic-user-1',
        'mixpanel-AppStore-MPDistinctID': 'synthetic-distinct-1',
        'mixpanel-AppStore-MPAnonymousId': 'synthetic-anon-1',
        'MPAppVersion': '9.9.9',
        'mixpanel-AppStore-timedEvents': _archive({
            'login': _ts(FIRST_OPEN + datetime.timedelta(days=1)),
            'Enable Touch ID': _ts(FIRST_OPEN + datetime.timedelta(days=2)),
            'Add Profile Photo': _ts(FIRST_OPEN + datetime.timedelta(days=2, hours=1)),
        }),
        'mixpanel-AppStore-superProperties': _archive({
            'Current App Screen': 'synthetic_home',
            'Last App Screen': 'synthetic_login',
            'Enabled Push': True,
            'Returning User?': True,
        }),
    }
    crash = {'com.crashlytics.install.iid': 'synthetic-install-id', 'com.crashlytics.iuuid': 'synthetic-uuid'}
    return prefs, mix, crash


def _metadata(bundle):
    return plistlib.dumps({'MCMMetadataIdentifier': bundle, 'MCMMetadataContentClass': 2,
                           'MCMMetadataVersion': 15}, fmt=_BINARY)


def _write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data if isinstance(data, bytes) else data.encode('utf-8'))


def build_container(root, folder, bundle=BUNDLE, minimal=False, with_metadata=True, decoy=False):
    base = Path(root) / APP / folder
    if with_metadata:
        _write(base / '.com.apple.mobile_container_manager.metadata.plist', _metadata(bundle))
    _write(base / 'Documents/log1.txt', sdk_log(include_noise=not minimal))
    if decoy:
        return
    _write(base / 'Library/Caches/file.log', console_log())
    prefs, mix, crash = preferences(full=not minimal)
    for rel, data in (('Library/Preferences/com.zellepay.zelle.plist', prefs),
                      ('Library/Preferences/Mixpanel.plist', mix),
                      ('Library/Application Support/com.crashlytics/CLSUserDefaults.plist', crash)):
        _write(base / rel, plistlib.dumps(data, fmt=_BINARY))


CASES = {
    # Full container, plus a second container of another app holding a file with the same name (must be ignored).
    'synthetic': lambda root: (build_container(root, CONTAINER),
                               build_container(root, OTHER_CONTAINER, bundle='com.example.other', decoy=True)),
    # Only what an older app version or a trimmed extraction might hold: no noise lines, no user_attributes table,
    # no SKPurchaseIntentUpdatesLastChecked key.
    'synthetic_minimal': lambda root: build_container(root, CONTAINER, minimal=True),
    # An iTunes backup names the container folder by the bundle id and has no metadata plist.
    'synthetic_backup': lambda root: build_container(root, BUNDLE, with_metadata=False),
}


def zip_case(tree, patterns, target):
    tree = Path(tree)
    target.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
        for path in sorted(p for p in tree.rglob('*') if p.is_file()):
            rel = path.relative_to(tree).as_posix()
            if any(fnmatch.fnmatchcase('root/' + rel, pat) or fnmatch.fnmatchcase(rel, pat) for pat in patterns):
                info = zipfile.ZipInfo(rel, (2000, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, path.read_bytes())
                count += 1
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('out')
    parser.add_argument('--tree', action='store_true', help='keep the unpacked container trees')
    parser.add_argument('--module', default=None, help='path to scripts/artifacts/zelle.py (default: repo copy)')
    args = parser.parse_args()
    repo = Path(args.module).resolve().parents[2] if args.module else Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(repo))
    from scripts.artifacts import zelle  # pylint: disable=import-outside-toplevel
    out = Path(args.out)
    for case, build in CASES.items():
        with tempfile.TemporaryDirectory() as tmp:
            build(tmp)
            if args.tree:
                shutil.copytree(tmp, out / 'trees' / case, dirs_exist_ok=True)
            for name, info in zelle.__artifacts_v2__.items():
                target = out / 'zelle' / f'testdata.zelle.{name}.{case}.zip'
                n = zip_case(tmp, info['paths'], target)
                print(f'{target.name}: {n} files')
    print(json.dumps(sorted(CASES)))


if __name__ == '__main__':
    os.environ.setdefault('PYTHONHASHSEED', '0')
    main()
