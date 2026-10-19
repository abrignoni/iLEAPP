#!/usr/bin/env python3
"""Build a SYNTHETIC Unified Log export for the TCC authorization cache and location state artifacts.

The output has the shape of ``log show --style json``: a JSON list of records with
``timestamp``, ``processImagePath``, ``processID``, ``subsystem``, ``category``,
``eventMessage`` and ``traceID`` (iLEAPP's logarchive artifact accepts any ``logarchive*.json``).

Every process path, PID and object address is invented (``FakeMaps``, ``FakeCam``, PIDs 4101 and
up, ``0x7f0b...``) and every timestamp is fixed, so the output is reproducible and carries nothing
from a real device. The message text of the two statedump kinds follows what unifiedlog_iterator
decoded on iOS 26.6 and iOS 27.0 sysdiagnose logs: a ``title:`` line, two ``Object Type:`` lines and
a body. A statedump record there has an empty subsystem and category. How such a record appears in a
real ``log show`` export was not examined, so putting it in this shape is itself INVENTED SHAPE; the
shapes the real logs did not contain are marked ``INVENTED SHAPE`` below, and they exist to exercise a
branch, not to describe a device.

    python synthetic_statedumps.py [output.json]

``build_lines()`` labels each line 'tcc' (a TCC cache dump that gives rows), 'tcc_empty' (collected, no
entries so no row), 'location' (a location manager dump) or 'never' (must not be collected);
``lines_of(kind)`` gives the Row Numbers the import assigns to them.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone

_ZONE = timezone(timedelta(hours=-5))
_BASE = datetime(2026, 3, 14, 10, 0, 0, tzinfo=_ZONE)

FIXTURE_NAME = 'logarchive_synthetic_statedump.json'

MAPS = ('/private/var/containers/Bundle/Application/FAKE0000-0000-0000-0000-000000000002/'
        'FakeMaps.app/FakeMaps')
CAM = ('/private/var/containers/Bundle/Application/FAKE0000-0000-0000-0000-000000000003/'
       'FakeCam.app/FakeCam')
DAEMON = '/usr/libexec/fakelocationclientd'
TCC_DAEMON = '/usr/libexec/faketccd'

TCC_TITLE = 'title: TCC Authorization Cache\nObject Type: \nObject Type: \n'
LOCATION_TITLE = ('title: CLLocationManagerStateTracker\nObject Type: location\n'
                  'Object Type: _CLLocationManagerStateTrackerState\n')

# The keys of a CLLocationManagerStateTracker dump in the order logged, with an idle default.
LOCATION_KEYS = (
    ('distanceFilter', '-1'), ('desiredAccuracy', '-1'), ('updatingLocation', 'false'),
    ('requestingLocation', 'false'), ('requestingRanging', 'false'), ('updatingRanging', 'false'),
    ('updatingHeading', 'false'), ('headingFilter', '1'), ('allowsLocationPrompts', 'true'),
    ('allowsAlteredAccessoryLocations', 'false'), ('dynamicAccuracyReductionEnabled', 'false'),
    ('previousAuthorizationStatusValid', 'true'), ('previousAuthorizationStatus', '2'),
    ('limitsPrecision', 'false'), ('activityType', '0'), ('pausesLocationUpdatesAutomatically', '5'),
    ('paused', 'false'), ('allowsBackgroundLocationUpdates', 'false'),
    ('showsBackgroundLocationIndicator', 'false'), ('allowsMapCorrection', 'true'),
    ('batchingLocation', 'false'), ('updatingVehicleSpeed', 'false'),
    ('updatingVehicleHeading', 'false'), ('matchInfoEnabled', 'false'),
    ('groundAltitudeEnabled', 'false'), ('fusionInfoEnabled', 'false'),
    ('courtesyPromptNeeded', 'false'), ('isAuthorizedForWidgetUpdates', 'false'))


def tcc_dump(entries):
    """A TCC Authorization Cache message. entries: (service, credential, record, right, reason, version, flags)."""
    cache = {}
    for service, credential, record, right, reason, version, flags in entries:
        tail = f' {flags},' if flags else ''
        cache.setdefault(service, {})[f'<Credential ({credential}) | Requestor>'] = (
            f'<Authorization Record ({record}) | Service: {service}, AuthRight: {right}, '
            f'Reason: {reason}, Version: {version},{tail} >')
    return TCC_TITLE + json.dumps(cache, separators=(',', ':'))


def location_dump(**changes):
    """A CLLocationManagerStateTracker message with the idle defaults and the given keys changed."""
    unknown = set(changes) - {key for key, _value in LOCATION_KEYS}
    assert not unknown, unknown
    lines = []
    for index, (key, default) in enumerate(LOCATION_KEYS):
        # The first two lines of the real body end with a comma and a space.
        lines.append(f'            "{key}":{changes.get(key, default)},' + (' ' if index < 2 else ''))
    return LOCATION_TITLE + '{\n' + '\n'.join(lines) + '\n        }'


def build_lines():
    """(seconds after the base time, process path, pid, subsystem, category, message, kind) in file order.

    The last element names the branch each line exercises: 'tcc' lines give rows in the TCC
    artifacts, 'tcc_empty' lines are collected but give none, 'location' lines give a row in the
    location artifacts, and 'never' lines are not collected at all.
    """
    lines = []

    def add(sec, process, pid, message, kind, subsystem='', category=''):
        lines.append((sec, process, pid, subsystem, category, message, kind))

    # A process dumps its cache several times. The first two hold the same two entries (the object
    # addresses differ, as they would for newly built objects), then an entry is added, then one
    # changes, then the cache is empty.
    photos = ('kTCCServicePhotos', '0x7f0b00001000', '0x7f0b00002000', 'Allowed', 'Entitled', '2', '')
    mic = ('kTCCServiceMicrophone', '0x7f0b00001100', '0x7f0b00002100', 'Allowed', 'User Consent', '1', '')
    add(10.000, MAPS, 4101, tcc_dump([photos, mic]), 'tcc')
    add(11.000, MAPS, 4101, tcc_dump([
        ('kTCCServicePhotos', '0x7f0b00003000', '0x7f0b00004000', 'Allowed', 'Entitled', '2', ''),
        ('kTCCServiceMicrophone', '0x7f0b00003100', '0x7f0b00004100', 'Allowed', 'User Consent', '1', '')]),
        'tcc')
    add(12.000, MAPS, 4101, tcc_dump([
        photos, mic,
        ('kTCCServiceCamera', '0x7f0b00001200', '0x7f0b00002200', 'Denied', 'User Consent', '1',
         'Has Prompted For Allow')]), 'tcc')
    add(13.000, MAPS, 4101, tcc_dump([
        photos, ('kTCCServiceMicrophone', '0x7f0b00001100', '0x7f0b00002100', 'Denied', 'System Set', '1', ''),
        ('kTCCServiceCamera', '0x7f0b00001200', '0x7f0b00002200', 'Denied', 'User Consent', '1',
         'Has Prompted For Allow')]), 'tcc')
    add(14.000, MAPS, 4101, TCC_TITLE + '{}', 'tcc_empty')

    # Another process; the other auth rights and reasons seen in the logs, one service per credential.
    add(20.000, CAM, 4102, tcc_dump([
        ('kTCCServiceCamera', '0x7f0b00005000', '0x7f0b00006000', 'Allowed', 'System Set', '1', ''),
        ('kTCCServicePhotos', '0x7f0b00005100', '0x7f0b00006100', 'Limited', 'Service Policy', '2', ''),
        ('kTCCServiceAddressBook', '0x7f0b00005200', '0x7f0b00006200', 'Unknown', 'None', '1', '')]), 'tcc')

    # The same process path again with a new PID (a restart): a separate summary row.
    add(30.000, MAPS, 4103, tcc_dump([photos]), 'tcc')

    # INVENTED SHAPE: the samples held only the layout above. These exercise the fall-backs.
    # An authorization description in another layout keeps its text and gives blank fields.
    add(40.000, TCC_DAEMON, 90, TCC_TITLE + '{"kTCCServiceCamera":{"<Credential (0x7f0b00007000) | Requestor>":'
                                              '"<Authorization Record (0x7f0b00008000) | something else entirely>"}}',
        'tcc')
    # A service key that maps to a string instead of credential and record pairs.
    add(41.000, TCC_DAEMON, 90, TCC_TITLE + '{"kTCCServiceCalendar":"not an object"}', 'tcc')
    # A body that is cut off, and a message with no body at all.
    add(42.000, TCC_DAEMON, 90, TCC_TITLE + '{"kTCCServiceCamera":{"<Credential (0x7f0b00009000) | Requestor>":',
        'tcc')
    add(43.000, TCC_DAEMON, 90, 'title: TCC Authorization Cache', 'tcc')
    # A credential without an address, and a record whose service differs from its key.
    add(44.000, TCC_DAEMON, 90, TCC_TITLE + '{"kTCCServiceCamera":{"<Credential | Requestor>":'
                                              '"<Authorization Record (0x7f0b0000a000) | Service: kTCCServiceMicrophone, '
                                              'AuthRight: Allowed, Reason: Entitled, Version: 2, >"}}', 'tcc')

    # Location manager dumps. Idle, then updating, repeated, then not updating and precision limited.
    add(100.000, MAPS, 4101, location_dump(), 'location')
    add(110.000, MAPS, 4101, location_dump(updatingLocation='true', desiredAccuracy='100', distanceFilter='50'),
        'location')
    add(120.000, MAPS, 4101, location_dump(updatingLocation='true', desiredAccuracy='100', distanceFilter='50'),
        'location')
    # Two dumps with the same record time from one process, with equal content (two managers, or one
    # dump written twice: the dump does not say).
    add(120.000, MAPS, 4101, location_dump(updatingLocation='true', desiredAccuracy='100', distanceFilter='50'),
        'location')
    add(130.000, MAPS, 4101, location_dump(limitsPrecision='true', previousAuthorizationStatus='3'), 'location')
    add(140.000, CAM, 4102, location_dump(allowsBackgroundLocationUpdates='true', activityType='3',
                                          updatingLocation='true'), 'location')
    add(150.000, DAEMON, 210, location_dump(requestingLocation='true', desiredAccuracy='2147483646',
                                            distanceFilter='500', dynamicAccuracyReductionEnabled='true',
                                            previousAuthorizationStatusValid='false'), 'location')

    # INVENTED SHAPE: the samples held the same 28 keys in the same order on every dump.
    # A key this artifact has no column for, and a key the dump does not hold (paused).
    unknown = location_dump().replace('            "paused":false,\n',
                                      '            "futureKey":"text value",\n')
    add(160.000, DAEMON, 210, unknown, 'location')
    # A repeated key: the first value fills the column and the second is kept in Other Fields.
    repeated = location_dump().replace('            "updatingLocation":false,\n',
                                       '            "updatingLocation":false,\n            "updatingLocation":true,\n')
    add(170.000, DAEMON, 210, repeated, 'location')
    # A body line that is not a key and value.
    odd = location_dump().replace('            "paused":false,\n', '            "paused":false,\n            stray line\n')
    add(180.000, DAEMON, 210, odd, 'location')
    # A message with no body.
    add(190.000, DAEMON, 210, LOCATION_TITLE.rstrip('\n'), 'location')

    # Decoys: other text that mentions the same names, and other statedumps.
    add(500.000, TCC_DAEMON, 90, 'TCC Authorization Cache refreshed for kTCCServiceCamera', 'never',
        subsystem='com.apple.TCC', category='access')
    add(501.000, TCC_DAEMON, 90, 'note: ' + tcc_dump([photos]), 'never')
    add(502.000, DAEMON, 210, 'CLLocationManagerStateTracker: updatingLocation changed', 'never',
        subsystem='com.apple.locationd', category='Client')
    add(503.000, DAEMON, 210, 'note: ' + location_dump(updatingLocation='true'), 'never')
    add(504.000, DAEMON, 210, 'title: CLRegionStateTracker\nObject Type: location\n{\n"updatingLocation":true,\n}',
        'never')
    add(505.000, TCC_DAEMON, 90, 'title: TCC Access Cache\nObject Type: \nObject Type: \n{}', 'never')
    return lines


def _stamp(seconds):
    return (_BASE + timedelta(seconds=seconds)).strftime('%Y-%m-%d %H:%M:%S.%f%z')


def build_records():
    """The JSON list in file order. traceID is a fixed, invented number per line."""
    records = []
    for index, (sec, process, pid, subsystem, category, message, _kind) in enumerate(build_lines()):
        records.append({
            'traceID': 2000 + index,
            'eventMessage': message,
            'eventType': 'logEvent',
            'source': None,
            'formatString': '%{public}s',
            'activityIdentifier': 0,
            'subsystem': subsystem,
            'category': category,
            'threadID': 5000 + index,
            'senderImageUUID': '00000000-0000-0000-0000-000000000000',
            'senderImagePath': process,
            'machTimestamp': 2000000 + index,
            'messageType': 'Default',
            'processImageUUID': '00000000-0000-0000-0000-000000000001',
            'processUniqueID': pid,
            'processID': pid,
            'processImagePath': process,
            'timestamp': _stamp(sec),
            'timezoneName': '',
            'creatorActivityID': 0,
            'parentActivityIdentifier': 0,
        })
    return records


def to_bytes(records=None):
    return (json.dumps(build_records() if records is None else records, indent=1) + '\n').encode('utf-8')


def lines_of(kind):
    """1-based file positions (the Row Number the import assigns) of the lines of one kind."""
    return [index for index, line in enumerate(build_lines(), start=1) if line[6] == kind]


if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else FIXTURE_NAME
    with open(target, 'wb') as handle:
        handle.write(to_bytes())
    print(f'wrote {target}: {len(build_lines())} records')
