#!/usr/bin/env python3
"""Builds fully synthetic app containers that hold a Google Measurement (Firebase Analytics) store.

Every value is invented: the bundle ids use the reserved example domain, the container ids are fabricated,
and all times are fixed. Nothing here comes from a device or a person.

    python synthetic_google_measurement.py <output folder>          # writes the case zips under <output folder>
    python synthetic_google_measurement.py <output folder> --tree   # also leaves the unpacked container trees
"""
import argparse
import datetime
import fnmatch
import json
import os
import plistlib
import shutil
import sqlite3
import sys
import tempfile
import zipfile
from pathlib import Path

APP = 'private/var/mobile/Containers/Data/Application'
ALPHA = 'AAAAAAAA-0000-4000-8000-000000000001'
BETA = 'BBBBBBBB-0000-4000-8000-000000000002'
UNIDENTIFIED = 'CCCCCCCC-0000-4000-8000-000000000003'
NO_STORE = 'DDDDDDDD-0000-4000-8000-000000000004'
UTC = datetime.timezone.utc
_BINARY = getattr(plistlib, 'FMT_BINARY')

# Epoch used by the fixture: 2026-03-02 14:00:00 UTC
FIRST_OPEN = datetime.datetime(2026, 3, 2, 14, 0, 0, tzinfo=UTC)
MEASUREMENT = 'Library/Application Support/Google/Measurement'


def _ts(dt):
    return dt.timestamp()


def measurement_db(path, tables='both', offset_days=0):
    """A google-app-measurement.sql with the tables the module reads; returns the latest event time."""
    start = FIRST_OPEN + datetime.timedelta(days=offset_days)
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE events (name TEXT, lifetime_count INTEGER, current_bundle_count INTEGER, '
                'last_fire_timestamp REAL, last_sampled_complex_event_id INTEGER, last_bundled_timestamp REAL)')
    events = [('_f', 1, 0, _ts(start)),
              ('_s', 3, 0, _ts(start + datetime.timedelta(days=6))),
              ('_e', 9, 0, _ts(start + datetime.timedelta(days=6, minutes=7))),
              ('synthetic_screen_view', 5, 0, _ts(start + datetime.timedelta(days=6, minutes=3)))]
    con.executemany('INSERT INTO events VALUES (?,?,?,?,0,0)', events)
    if tables == 'both':
        con.execute('CREATE TABLE user_attributes (name TEXT, set_timestamp REAL, value, origin TEXT)')
        con.executemany('INSERT INTO user_attributes VALUES (?,?,?,?)', [
            ('_fot', _ts(start), int(start.timestamp() * 1000) + 3_600_000 - 1_000, 'auto'),
            ('_sno', _ts(start), 3, 'auto'),
            ('synthetic_tier', _ts(start + datetime.timedelta(days=1)), 'example', 'app'),
        ])
    con.commit()
    con.close()
    return max(e[3] for e in events)


def measurement_plist(last_event, offset_days=0):
    start = FIRST_OPEN + datetime.timedelta(days=offset_days)
    prefix = '/google/measurement/'
    return {
        prefix + 'first_open_timestamp_ms': int(start.timestamp() * 1000),
        prefix + 'last_uploaded_event_millis': int(last_event * 1000),
        prefix + 'last_engagement_end': last_event,
        prefix + 'last_successful_upload': last_event + 30,
        prefix + 'last_failed_upload': 0.0,
        prefix + 'session_number': 3,
        prefix + 'app_version': '9.9.9',
        prefix + 'os_version': '99.0',
        prefix + 'app_instance_id': 'synthetic-instance-id',
    }


def _metadata(bundle):
    return plistlib.dumps({'MCMMetadataIdentifier': bundle, 'MCMMetadataContentClass': 2,
                           'MCMMetadataVersion': 15}, fmt=_BINARY)


def _write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data if isinstance(data, bytes) else data.encode('utf-8'))


def build_container(root, folder, bundle=None, tables='both', with_plist=True, offset_days=0):
    """One data container; bundle=None leaves out the metadata plist (an unidentified container)."""
    base = Path(root) / APP / folder
    if bundle:
        _write(base / '.com.apple.mobile_container_manager.metadata.plist', _metadata(bundle))
    _write(base / 'Documents/readme.txt', 'synthetic')
    measurement = base / MEASUREMENT
    measurement.mkdir(parents=True, exist_ok=True)
    last_event = measurement_db(str(measurement / 'google-app-measurement.sql'), tables=tables,
                                offset_days=offset_days)
    if with_plist:
        _write(measurement / 'com.google.gmp.measurement.plist',
               plistlib.dumps(measurement_plist(last_event, offset_days), fmt=_BINARY))


def build_container_without_store(root, folder, bundle):
    base = Path(root) / APP / folder
    _write(base / '.com.apple.mobile_container_manager.metadata.plist', _metadata(bundle))
    _write(base / 'Documents/readme.txt', 'synthetic')


def _two_apps(root):
    build_container(root, ALPHA, bundle='com.example.alpha')
    # a second app: an older SDK layout with no user_attributes table
    build_container(root, BETA, bundle='com.example.beta', tables='events', offset_days=10)
    # a container with the store but no metadata plist: the app cannot be named
    build_container(root, UNIDENTIFIED, bundle=None, with_plist=False, offset_days=20)
    # an app with no Google Measurement folder at all
    build_container_without_store(root, NO_STORE, 'com.example.gamma')


CASES = {
    'synthetic': _two_apps,
    # Only what a trimmed extraction might hold: events table, no plist.
    'synthetic_minimal': lambda root: build_container(root, ALPHA, bundle='com.example.alpha', tables='events',
                                                      with_plist=False),
    # An iTunes backup names the container folder by the bundle id and has no metadata plist.
    'synthetic_backup': lambda root: build_container(root, 'com.example.alpha', bundle=None),
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
    parser.add_argument('--module', default=None, help='path to scripts/artifacts/googleMeasurement.py')
    args = parser.parse_args()
    repo = Path(args.module).resolve().parents[2] if args.module else Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(repo))
    from scripts.artifacts import googleMeasurement  # pylint: disable=import-outside-toplevel
    out = Path(args.out)
    for case, build in CASES.items():
        with tempfile.TemporaryDirectory() as tmp:
            build(tmp)
            if args.tree:
                shutil.copytree(tmp, out / 'trees' / case, dirs_exist_ok=True)
            for name, info in googleMeasurement.__artifacts_v2__.items():
                target = out / 'googleMeasurement' / f'testdata.googleMeasurement.{name}.{case}.zip'
                n = zip_case(tmp, info['paths'], target)
                print(f'{target.name}: {n} files')
    print(json.dumps(sorted(CASES)))


if __name__ == '__main__':
    os.environ.setdefault('PYTHONHASHSEED', '0')
    main()
