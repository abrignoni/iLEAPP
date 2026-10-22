"""Synthetic regressions for Life360 payload preservation, provenance and container scoping."""
import base64
import collections
from datetime import datetime, timezone
import fnmatch
import inspect
import json
from pathlib import Path
import plistlib
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from admin.test.fixtures.life360 import make_synthetic_life360 as fixture
from scripts import ilapfuncs, life360_common
from scripts.artifacts import life360Awareness as awareness, life360Stores as stores
from scripts.life360_common import get_life360_files, seconds_to_utc


class _Context:
    def __init__(self, root, patterns):
        self.root = Path(root)
        self.files = [str(path) for path in self.root.rglob('*') if path.is_file()
                      and any(fnmatch.fnmatchcase(str(path), pattern) for pattern in patterns)]

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root)).replace('\\', '/')


def _container(root, bundle='com.life360.safetymap'):
    fixture.build_container(str(root))
    marker = Path(root) / '.com.apple.mobile_container_manager.metadata.plist'
    marker.write_bytes(plistlib.dumps({'MCMMetadataIdentifier': bundle}))


def _run(module, name, root, reverse=False, duplicate=False):
    context = _Context(root, module.__artifacts_v2__[name]['paths'])
    if reverse:
        context.files.reverse()
    if duplicate:
        context.files *= 2
    with patch.object(stores, 'device_info'):
        headers, rows, _ = inspect.unwrap(getattr(module, name))(context)
    labels = [header[0] if isinstance(header, tuple) else header for header in headers]
    return [dict(zip(labels, row)) for row in rows]


def _topic(root, suffix):
    return next(path for path in Path(root).rglob('*.sqlite') if path.stem.endswith(suffix))


def _documents(path):
    with sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True) as connection:
        return [(stamp, json.loads(data)) for stamp, data in connection.execute(
            'SELECT ZTIMESTAMP,ZDATA FROM ZENTRY ORDER BY ZTIMESTAMP')]


def _append(path, stamp, document):
    # Writes only to this test's generated database, never a corpus or committed case.
    data = json.dumps(document).encode() if isinstance(document, dict) else document
    with sqlite3.connect(path) as connection:
        connection.execute('INSERT INTO ZENTRY (ZTIMESTAMP,ZDATA) VALUES (?,?)', (stamp, data))


class Life360StoreTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / 'app'
        _container(self.root)

    def test_known_second_epochs_keep_zero_negative_and_fractional_times(self):
        for epoch in (1970, 2001):
            with self.subTest(epoch=epoch):
                self.assertEqual(seconds_to_utc(0, epoch), datetime(epoch, 1, 1, tzinfo=timezone.utc))
                self.assertEqual(seconds_to_utc(-1, epoch).year, epoch - 1)
                self.assertEqual(seconds_to_utc(0.125, epoch).microsecond, 125000)
        with patch('scripts.life360_common.logfunc') as log:
            self.assertEqual(seconds_to_utc(float('inf'), 1970), '')
            self.assertEqual(seconds_to_utc(float('nan'), 2001), '')
        self.assertEqual(log.call_count, 2)
        with patch('scripts.life360_common.logfunc') as log:
            for value in ('synthetic-not-seconds', True):
                self.assertEqual(seconds_to_utc(value, 1970), '')
            self.assertEqual(log.call_count, 2)
            log.reset_mock()
            for value in (None, ''):
                self.assertEqual(seconds_to_utc(value, 1970), '')
            log.assert_not_called()

    def test_converted_artifact_columns_preserve_epochs_and_subseconds(self):
        entry = fixture.uid(0x9030)
        document = {'id': entry, 'bufferedSamples': [fixture.loc(fixture.T0 + 1200.125)]}
        _append(_topic(self.root, 'DeviceLocationTopic'), fixture.T0 + 1200.375, document)
        rows = _run(awareness, 'life360DeviceLocationSamples', self.root)
        sample = next(row for row in rows if row['Entry ID'] == entry)
        self.assertEqual(sample['Sample Time'], datetime.fromtimestamp(fixture.T0 + 1200.125, timezone.utc))
        self.assertEqual(sample['Logged Time'], datetime.fromtimestamp(fixture.T0 + 1200.375, timezone.utc))
        self.assertEqual((sample['Logged Time'] - sample['Sample Time']).total_seconds(), 0.25)
        drives = _run(stores, 'life360CircleDrives', self.root)
        self.assertEqual(len(drives), 3)
        self.assertTrue(all(row['Last Retrieved'].microsecond == 500000 for row in drives))

    def test_equal_position_and_time_keep_both_point_sources(self):
        rows = _run(awareness, 'life360MovementWaypoints', self.root)
        self.assertEqual(len(rows), 6)
        self.assertEqual(sum(row['Occurrences'] for row in rows), 6)
        groups = collections.defaultdict(set)
        for row in rows:
            groups[(row['Waypoint Time'], row['Latitude'], row['Longitude'])].add(
                row['Point Source (as stored)'])
        self.assertTrue(any(values == {'drive_engine', 'location_engine'} for values in groups.values()))

    def test_unreported_point_key_is_retained_and_prevents_dedup(self):
        path = _topic(self.root, 'drive_session')
        stamp, document = _documents(path)[1]
        point = document['drive']['waypoints'][0]
        variant = dict(point, syntheticQuality='different')
        document['drive']['waypoints'] = [point, variant]
        _append(path, stamp + 1, document)
        rows = _run(awareness, 'life360MovementWaypoints', self.root)
        self.assertEqual(len(rows), 7)
        self.assertEqual(sum(row['Occurrences'] for row in rows), 8)
        self.assertEqual(sum('syntheticQuality' in json.loads(row['Point Data (as stored)'])
                             for row in rows), 1)

    def test_incident_event_ids_are_associated_with_sources_and_order_independent(self):
        rows = _run(awareness, 'life360DrivingIncidents', self.root)
        self.assertEqual(rows, _run(awareness, 'life360DrivingIncidents', self.root, reverse=True))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        appearances = json.loads(row['Contributing Records'])
        self.assertEqual(len(appearances), 3)
        self.assertEqual(row['Occurrences'], 3)
        self.assertEqual(set(row['Event IDs'].split(', ')), {value['eventID'] for value in appearances})
        for value in appearances:
            self.assertFalse(Path(value['sourceFile']).is_absolute())
            documents = _documents(self.root / value['sourceFile'])
            self.assertTrue(any(document.get('id') == value['entryID']
                                and document['drive']['id'] == value['eventID']
                                and stamp == value['loggedTimeUnix'] for stamp, document in documents))

    def test_dwell_conflicts_and_logged_times_survive_without_field_merging(self):
        path = _topic(self.root, 'DwellTopic')
        stamp, document = _documents(path)[1]
        document['dwell']['location']['latitude'] = 0.6
        document['dwell']['state'] = {'moving': {}}
        _append(path, stamp, document)
        _append(path, stamp, document)
        rows = _run(awareness, 'life360DwellEvents', self.root)
        self.assertEqual(len(rows), 5)
        self.assertEqual(sum(row['Occurrences'] for row in rows), 6)
        variant = [row for row in rows if row['Latitude'] == 0.6]
        self.assertEqual(len(variant), 1)
        self.assertEqual(variant[0]['State (as stored)'], 'moving')
        self.assertEqual(variant[0]['Occurrences'], 2)
        self.assertEqual(variant[0]['Session ID'], '')
        self.assertEqual(rows, _run(awareness, 'life360DwellEvents', self.root, reverse=True))

    def test_all_aggregates_keep_relative_sources_and_stable_point_order(self):
        for name in ('life360MovementWaypoints', 'life360DrivingIncidents', 'life360DwellEvents'):
            with self.subTest(artifact=name):
                rows = _run(awareness, name, self.root)
                self.assertEqual(rows, _run(awareness, name, self.root, reverse=True))
                for row in rows:
                    sources = row['Source Files'].splitlines()
                    self.assertTrue(sources)
                    self.assertTrue(all(not Path(source).is_absolute() for source in sources))
                    self.assertEqual(set(sources), {entry['sourceFile'] for entry in
                                                   json.loads(row['Contributing Records'])})

    def test_load_bearing_wal_is_applied(self):
        path = _topic(self.root, 'DeviceLocationTopic')
        self.assertTrue(Path(str(path) + '-wal').is_file())
        with sqlite3.connect(path.resolve().as_uri() + '?immutable=1', uri=True) as connection:
            self.assertEqual(connection.execute('SELECT count(*) FROM ZENTRY').fetchone()[0], 0)
        rows = _run(awareness, 'life360DeviceLocationSamples', self.root)
        self.assertEqual(len(rows), 3)

    def test_empty_or_missing_buffer_uses_headline(self):
        path = _topic(self.root, 'DeviceLocationTopic')
        document = {'id': fixture.uid(0x9010), 'location': fixture.loc(fixture.T0 + 200)}
        for index, buffered in enumerate((None, [])):
            if buffered is not None:
                document['bufferedSamples'] = buffered
            _append(path, fixture.T0 + 201 + index, document)
        rows = _run(awareness, 'life360DeviceLocationSamples', self.root)
        self.assertEqual(len(rows), 5)
        self.assertEqual(sum(row['Sample Count'] == 1 for row in rows), 3)

    def test_bad_entry_json_is_logged_and_other_rows_survive(self):
        path = _topic(self.root, 'DeviceLocationTopic')
        for data in (b'{', b'[]', b'\xff'):
            _append(path, fixture.T0 + 500, data)
        with patch.object(awareness, 'logfunc') as log:
            rows = _run(awareness, 'life360DeviceLocationSamples', self.root)
        self.assertEqual(len(rows), 3)
        self.assertTrue(any('3 ZENTRY row(s)' in str(call) for call in log.call_args_list))

    def test_deferred_sqlite_read_failure_preserves_good_files(self):
        tree = self.root.parent
        artifacts = [(module, name) for module in (awareness, stores)
                     for name, metadata in module.__artifacts_v2__.items()
                     if any('.sqlite' in pattern for pattern in metadata['paths'])]
        expected = {(module, name): _run(module, name, tree) for module, name in artifacts}
        bad = tree / '0_bad'
        _container(bad)
        (bad / 'Library/Preferences/com.life360.safetymap.plist').unlink()
        original = ilapfuncs.get_sqlite_db_records
        closed = []

        def records(path, query):
            found = original(path, query)
            if bad not in Path(path).parents:
                return found

            def fail_late():
                try:
                    yield next(iter(found))
                    raise sqlite3.DatabaseError('synthetic-private-payload')
                finally:
                    found.close()
                    closed.append(path)

            return fail_late()

        for module, name in artifacts:
            with self.subTest(artifact=name), \
                    patch.object(life360_common, 'get_sqlite_db_records', side_effect=records), \
                    patch.object(life360_common, 'logfunc') as log:
                closed.clear()
                rows = _run(module, name, tree)
                before = collections.Counter(json.dumps(row, sort_keys=True, default=str)
                                             for row in expected[module, name])
                after = collections.Counter(json.dumps(row, sort_keys=True, default=str) for row in rows)
                self.assertFalse(before - after)
                self.assertTrue(closed)
                messages = [call.args[0] for call in log.call_args_list]
                self.assertTrue(any('0_bad' in message and 'SQLite read failed' in message
                                    and 'earlier rows retained' in message for message in messages))
                self.assertTrue(all('synthetic-private-payload' not in message for message in messages))

    def test_unrecognised_location_entry_is_logged_beside_good_rows(self):
        path = _topic(self.root, 'DeviceLocationTopic')
        _append(path, fixture.T0 + 1500, {'unsupported_layout': True})
        with patch.object(awareness, 'logfunc') as log:
            rows = _run(awareness, 'life360DeviceLocationSamples', self.root)
        self.assertEqual(len(rows), 3)
        self.assertTrue(any('DeviceLocationTopic.sqlite' in call.args[0]
                            and 'neither buffered samples nor a headline location' in call.args[0]
                            for call in log.call_args_list))

    def test_corrupt_and_unrecognised_sqlite_stores_are_logged_beside_good_files(self):
        tree = self.root.parent
        artifacts = [(module, name) for module in (awareness, stores)
                     for name, metadata in module.__artifacts_v2__.items()
                     if any('.sqlite' in pattern for pattern in metadata['paths'])]
        expected = {(module, name): _run(module, name, tree) for module, name in artifacts}
        for mode in ('corrupt', 'unrecognised_schema'):
            bad = tree / mode
            _container(bad)
            (bad / 'Library/Preferences/com.life360.safetymap.plist').unlink()
            for path in bad.rglob('*'):
                if path.name.endswith(('-wal', '-shm')):
                    path.unlink()
            for path in bad.rglob('*.sqlite'):
                path.unlink()
                if mode == 'corrupt':
                    path.write_bytes(b'not a SQLite database')
                else:
                    with sqlite3.connect(path) as connection:
                        connection.execute('CREATE TABLE unsupported_layout (value TEXT)')
        for module, name in artifacts:
            with self.subTest(artifact=name), patch.object(ilapfuncs, 'logfunc') as log:
                rows = _run(module, name, tree)
                self.assertCountEqual(rows, expected[module, name])
                messages = [call.args[0] for call in log.call_args_list]
                for mode in ('corrupt', 'unrecognised_schema'):
                    self.assertTrue(any(mode in message and '.sqlite' in message for message in messages))

    def test_malformed_embedded_xml_plist_is_logged_and_good_file_survives(self):
        tree = self.root.parent
        expected = _run(stores, 'life360PopDwells', tree)
        bad = tree / '0_bad'
        _container(bad)
        path = bad / 'Library/Preferences/com.life360.safetymap.plist'
        preferences = plistlib.loads(path.read_bytes())
        preferences['pop-dwell_seen'] = b'<?xml version="1.0"?><plist><array><dict><key>date</key>'
        path.write_bytes(plistlib.dumps(preferences))
        with patch.object(stores, 'logfunc') as log:
            rows = _run(stores, 'life360PopDwells', tree)
        self.assertEqual(rows, expected)
        self.assertTrue(any('0_bad/Library/Preferences/com.life360.safetymap.plist' in call.args[0]
                            and 'did not parse as a plist' in call.args[0] for call in log.call_args_list))

    def test_raw_event_forms_and_bad_base64_preserve_outer_entry(self):
        path = _topic(self.root, 'active_modality')
        raw = {'timestamp': fixture.T0 + 1200, 'location': fixture.loc(fixture.T0 + 1199)}
        drive = {'timestamp': fixture.T0 + 1199 - fixture.COCOA,
                 'coordinate': {'latitude': fixture.LAT, 'longitude': fixture.LON},
                 'tripID': 'synthetic-fallback-trip'}
        variants = (raw, '!!notbase64', base64.b64encode(b'not JSON').decode(), None,
                    base64.b64encode(b'[]').decode(), 7,
                    dict(raw, location=None, drive=drive), dict(raw, location=7, drive=drive))
        for index, value in enumerate(variants):
            document = {'id': fixture.uid(0x9100 + index), 'timestamp': fixture.T0 + 1300 + index,
                        'rawEvent': value, 'rawEventType': 'synthetic'}
            _append(path, fixture.T0 + 1400 + index, document)
        with patch.object(awareness, 'logfunc') as log, patch('scripts.life360_common.logfunc') as shape_log:
            rows = _run(awareness, 'life360ActivityModality', self.root)
        self.assertEqual(len(rows), 10)
        self.assertEqual(sum(row['Location Time'] == '' for row in rows), 5)
        self.assertEqual(log.call_count, 4)
        self.assertTrue(all('outer entry retained' in call.args[0] for call in log.call_args_list))
        self.assertTrue(any('rawEvent location' in call.args[0] for call in shape_log.call_args_list))
        fallback = [row for row in rows if row['Trip ID'] == 'synthetic-fallback-trip']
        self.assertEqual(len(fallback), 2)
        self.assertTrue(all(row['Location Time'] != '' and row['Latitude'] == fixture.LAT for row in fallback))
        self.assertTrue(any(row['Event Time'] != row['Logged Time'] for row in rows))

    def test_account_health_dictionary_json_bytes_and_string(self):
        path = self.root / 'Library/Preferences/com.life360.safetymap.plist'
        preferences = plistlib.loads(path.read_bytes())
        health = {'synthetic': {'name': 'example', 'total': 2, 'time': float(fixture.T0)}}
        for value in (health, json.dumps(health), json.dumps(health).encode()):
            with self.subTest(type=type(value).__name__):
                preferences['L360LocationHealthStorage'] = value
                path.write_bytes(plistlib.dumps(preferences))
                rows = _run(stores, 'life360Account', self.root)
                self.assertEqual(sum(row['Section'] == 'L360LocationHealthStorage' for row in rows), 3)

    def test_code_only_circle_keeps_invite_without_fabricating_name(self):
        rows = _run(stores, 'life360Circles', self.root)
        self.assertEqual(len(rows), 2)
        orphan = next(row for row in rows if row['Circle ID'] == fixture.CIRCLE2)
        self.assertEqual(orphan['Circle Name'], '')
        self.assertEqual(orphan['Created At'], '')
        self.assertEqual(orphan['Invite Code'], 'XYZ-789')

    def test_circle_roles_decode_dictionaries_json_text_and_bytes(self):
        path = self.root / 'Library/Preferences/com.life360.safetymap.plist'
        preferences = plistlib.loads(path.read_bytes())
        roles = {fixture.CIRCLE1: 1, fixture.CIRCLE2: 0}
        for raw in (roles, json.dumps(roles), json.dumps(roles).encode()):
            with self.subTest(type=type(raw).__name__):
                preferences['memberRoles'] = raw
                path.write_bytes(plistlib.dumps(preferences))
                with patch.object(stores, 'logfunc') as log, patch('scripts.life360_common.logfunc') as shape_log:
                    rows = _run(stores, 'life360Circles', self.root)
                self.assertEqual({row['Circle ID']: row['Role (as stored)'] for row in rows}, roles)
                log.assert_not_called()
                shape_log.assert_not_called()
        for raw in (b'{', b'[]', 7):
            with self.subTest(invalid=type(raw).__name__):
                preferences['memberRoles'] = raw
                path.write_bytes(plistlib.dumps(preferences))
                with patch.object(stores, 'logfunc') as log:
                    rows = _run(stores, 'life360Circles', self.root)
                self.assertEqual(len(rows), 2)
                self.assertTrue(all(row['Role (as stored)'] == '' for row in rows))
                self.assertTrue(any('memberRoles' in call.args[0] for call in log.call_args_list))
        preferences.pop('memberRoles')
        path.write_bytes(plistlib.dumps(preferences))
        with patch.object(stores, 'logfunc') as log:
            rows = _run(stores, 'life360Circles', self.root)
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row['Role (as stored)'] == '' for row in rows))
        log.assert_not_called()

    def test_malformed_preference_sections_are_logged_and_isolated(self):
        path = self.root / 'Library/Preferences/com.life360.safetymap.plist'
        preferences = plistlib.loads(path.read_bytes())
        preferences.update({'com.life360.datakit.CurrentUser.Type': b'[null]',
                            'com.life360.datakit.Circle.Type': b'{',
                            'L360LocationHealthStorage': b'{',
                            'AwarenessEngineGate.BreachRule.breachStateCache': b'{',
                            'pop-dwell_seen': b'not a plist'})
        path.write_bytes(plistlib.dumps(preferences))
        with patch.object(stores, 'logfunc') as log:
            self.assertTrue(_run(stores, 'life360Account', self.root))
            self.assertEqual(len(_run(stores, 'life360Circles', self.root)), 2)
            self.assertEqual(_run(stores, 'life360GeofenceStates', self.root), [])
            self.assertEqual(_run(stores, 'life360PopDwells', self.root), [])
        self.assertGreaterEqual(log.call_count, 5)

    def test_breach_without_places_keeps_location(self):
        path = _topic(self.root, 'BreachTopic')
        document = {'id': fixture.uid(0x9200), 'timestamp': fixture.T0 + 1500,
                    'location': fixture.loc(fixture.T0 + 1499), 'places': []}
        _append(path, fixture.T0 + 1500, document)
        rows = _run(awareness, 'life360GeofenceBreaches', self.root)
        self.assertEqual(len(rows), 2)
        self.assertEqual(sum(row['Place Name'] == '' and row['Latitude'] == fixture.LAT for row in rows), 1)

    @unittest.skipIf(sqlite3.sqlite_version_info < (3, 35, 0), 'DROP COLUMN needs SQLite 3.35')
    def test_places_without_category_column_keeps_rows(self):
        # The Life360 24.x ZPLACEMODEL has no ZCATEGORY column.
        expected = _run(stores, 'life360Places', self.root)
        path = self.root / 'Library/Application Support/L360CoreDataStore.sqlite'
        with sqlite3.connect(path) as connection:
            connection.execute('ALTER TABLE ZPLACEMODEL DROP COLUMN ZCATEGORY')
        rows = _run(stores, 'life360Places', self.root)
        self.assertEqual(len(rows), len(expected))
        self.assertEqual({row['Name'] for row in rows}, {row['Name'] for row in expected})
        self.assertTrue(all(row['Category'] == '' for row in rows))

    def test_preference_shape_and_setting_decode_failures_are_logged(self):
        path = self.root / 'Library/Preferences/com.life360.safetymap.plist'
        preferences = plistlib.loads(path.read_bytes())
        preferences['com.life360.datakit.CurrentUser.Type'] = 7
        preferences['com.life360.datakit.Circle.Type'] = '[null, {}]'
        preferences['L360LocationHealthStorage'] = b'null'
        key = 'com.life360.datakit.MemberCircleSettings.Type'
        blocks = json.loads(preferences[key])
        blocks[0]['store'].extend(['synthetic-raw-key', '!!synthetic-secret', 'synthetic-unpaired-key'])
        preferences[key] = json.dumps(blocks).encode()
        path.write_bytes(plistlib.dumps(preferences))
        with patch.object(stores, 'logfunc') as log:
            self.assertTrue(_run(stores, 'life360Account', self.root))
            self.assertTrue(_run(stores, 'life360Circles', self.root))
            rows = _run(stores, 'life360MemberSettings', self.root)
        messages = [call.args[0] for call in log.call_args_list]
        for reason in ('neither an array nor an object', 'array element 0 was not an object',
                       'did not hold a dictionary', 'unpaired trailing key', 'raw value retained'):
            self.assertTrue(any(reason in message for message in messages), reason)
        self.assertTrue(any(row['Value'] == '!!synthetic-secret' for row in rows))
        self.assertTrue(all('synthetic-secret' not in message for message in messages))
        path.write_bytes(plistlib.dumps([]))
        with patch.object(stores, 'logfunc') as log:
            for name in ('life360Account', 'life360Circles', 'life360MemberSettings',
                         'life360GeofenceStates', 'life360PopDwells'):
                self.assertEqual(_run(stores, name, self.root), [])
        self.assertEqual(log.call_count, 5)

    def test_two_tenants_duplicate_views_and_foreign_decoy(self):
        # An examiner's ancestor folder named Library must not become the container key.
        tree = self.root.parent / 'Library' / 'multi'
        _container(tree / 'first')
        _container(tree / 'second')
        _container(tree / 'foreign', 'invalid.example.foreign-app')
        delta = {'id': fixture.uid(0xA500), 'location': fixture.loc(fixture.T0 + 2000)}
        _append(_topic(tree / 'second', 'DeviceLocationTopic'), fixture.T0 + 2001, delta)
        for module in (awareness, stores):
            for name in module.__artifacts_v2__:
                with self.subTest(artifact=name):
                    single = _run(module, name, self.root)
                    with patch('scripts.life360_common.logfunc'):
                        multiple = _run(module, name, tree, duplicate=True)
                    expected = 2 * len(single) + (name == 'life360DeviceLocationSamples')
                    self.assertEqual(len(multiple), expected)
                    for row in multiple:
                        source = row.get('Source File', row.get('Source Files', ''))
                        self.assertNotIn('foreign/', source)
                        self.assertTrue(source.startswith(('first/', 'second/')))

    def test_missing_marker_fails_closed_and_physical_alias_collapses(self):
        marker = self.root / '.com.apple.mobile_container_manager.metadata.plist'
        marker.unlink()
        with patch('scripts.life360_common.logfunc'):
            self.assertEqual(_run(awareness, 'life360MovementWaypoints', self.root), [])
            self.assertEqual(_run(stores, 'life360Places', self.root), [])
        marker.write_bytes(plistlib.dumps({'MCMMetadataIdentifier': 'com.life360.safetymap'}))
        alias = self.root.parent / 'alias'
        try:
            alias.symlink_to(self.root, target_is_directory=True)
        except OSError:
            return  # Some Windows test environments do not grant symlink privileges.
        context = _Context(self.root, awareness.__artifacts_v2__['life360MovementWaypoints']['paths'])
        context.files += [str(alias / Path(path).relative_to(self.root)) for path in list(context.files)]
        headers, rows, _ = awareness.life360MovementWaypoints.__wrapped__(context)
        self.assertEqual(len(rows), 6)
        self.assertTrue(all(len(row) == len(headers) for row in rows))

    def test_excluded_stores_are_logged_when_the_main_container_is_present(self):
        tree = self.root.parent
        _container(tree / 'PluginKitPlugin' / 'extension', 'com.life360.safetymap.SidecarLPSE')
        _container(tree / 'foreign', 'invalid.example.foreign-app')
        _container(tree / 'missing')
        (tree / 'missing' / '.com.apple.mobile_container_manager.metadata.plist').unlink()
        _container(tree / 'invalid')
        (tree / 'invalid' / '.com.apple.mobile_container_manager.metadata.plist').write_bytes(
            plistlib.dumps([]))
        _container(tree / 'corrupt')
        (tree / 'corrupt' / '.com.apple.mobile_container_manager.metadata.plist').write_bytes(b'not a plist')
        for module in (awareness, stores):
            for name in module.__artifacts_v2__:
                with self.subTest(artifact=name), patch('scripts.life360_common.logfunc') as log, \
                        patch('scripts.ilapfuncs.logfunc') as plist_log:
                    single = _run(module, name, self.root)
                    multiple = _run(module, name, tree, duplicate=True)
                    self.assertEqual(len(multiple), len(single))
                    messages = [call.args[0] for call in log.call_args_list]
                    self.assertTrue(any('com.life360.safetymap.SidecarLPSE' in m for m in messages))
                    self.assertTrue(any('invalid.example.foreign-app' in m for m in messages))
                    self.assertTrue(any('missing/' in m and 'marker missing' in m for m in messages))
                    self.assertTrue(any('invalid/' in m and 'marker unreadable' in m for m in messages))
                    self.assertTrue(any('corrupt/' in m and 'marker unreadable' in m for m in messages))
                    plist_log.assert_called()
                    self.assertTrue(all(str(tree) not in m for m in messages))
                    log.reset_mock()
                    self.assertEqual(_run(module, name, tree), multiple)
                    self.assertEqual([call.args[0] for call in log.call_args_list], messages)

    def test_unrelated_markers_are_not_parsed(self):
        context = _Context(self.root, awareness.__artifacts_v2__['life360GeofenceBreaches']['paths'])
        unrelated = [self.root.parent / 'other-apps' / str(n) /
                     '.com.apple.mobile_container_manager.metadata.plist' for n in range(1352)]
        context.files.extend(str(path) for path in unrelated)
        with patch('scripts.life360_common.get_plist_file_content', wraps=stores.get_plist_file_content) as read:
            self.assertTrue(get_life360_files(context))
        self.assertEqual(read.call_count, 1)

    def test_nested_foreign_marker_does_not_inherit_an_accepted_parent(self):
        nested = self.root / 'nested'
        _container(nested, 'invalid.example.foreign-app')
        with patch('scripts.life360_common.logfunc') as log:
            rows = _run(awareness, 'life360GeofenceBreaches', self.root)
        self.assertEqual(len(rows), 1)
        self.assertTrue(all('nested/' not in row['Source File'] for row in rows))
        self.assertTrue(any('invalid.example.foreign-app' in call.args[0] for call in log.call_args_list))


if __name__ == '__main__':
    unittest.main()
