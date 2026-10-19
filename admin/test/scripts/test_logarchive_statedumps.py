"""TCC authorization cache and location manager state dumps, through the real two-stage logarchive chain.

The four artifacts here read the table logarchive_artifacts builds, and that table holds only rows
its own marker list collected. A test that queries a dependent artifact on a hand-made table cannot
see a marker missing from the collection stage, so the main test runs the real ileapp.py on a
synthetic 'log show' export (synthetic_statedumps.py) and reads what each stage wrote. Everything in
the export is invented.
"""
import inspect
import json
import os
import pathlib
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import synthetic_statedumps as synthetic  # pylint: disable=wrong-import-position
from scripts.artifacts import logarchive  # pylint: disable=wrong-import-position

PROFILE = {'leapp': 'ileapp', 'format_version': 1,
           'plugins': ['logarchive', 'logarchive_artifacts', 'logarchive_tcc_cache',
                       'logarchive_tcc_cache_summary', 'logarchive_location_state',
                       'logarchive_location_state_summary']}
BASE_EPOCH = datetime(2026, 3, 14, 15, 0, 0, tzinfo=timezone.utc).timestamp()  # 10:00:00 at -0500
MAPS, CAM, DAEMON, TCC_DAEMON = synthetic.MAPS, synthetic.CAM, synthetic.DAEMON, synthetic.TCC_DAEMON


def _like_patterns(sql):
    return set(re.findall(r"LIKE '([^']*)'", sql))


def _row_at(sec, kind, nth=0):
    """Row Number of the nth line of a kind at a number of seconds after the base time."""
    hits = [index for index, line in enumerate(synthetic.build_lines(), start=1)
            if line[6] == kind and abs(line[0] - sec) < 1e-6]
    return hits[nth]


class ChainTest(unittest.TestCase):
    """ileapp.py on the fixture: producer, collection stage, then the dependent artifacts."""

    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.TemporaryDirectory()
        root = pathlib.Path(cls.folder.name)
        extraction = root / 'extraction'
        extraction.mkdir()
        (extraction / synthetic.FIXTURE_NAME).write_bytes(synthetic.to_bytes())
        profile = root / 'statedump.ilprofile'
        profile.write_text(json.dumps(PROFILE), encoding='utf-8')
        output = root / 'out'
        output.mkdir()
        environment = dict(os.environ, TZ='UTC')
        completed = subprocess.run(
            [sys.executable, str(REPO_ROOT / 'ileapp.py'), '-t', 'fs', '-i', str(extraction),
             '-o', str(output), '-m', str(profile)],
            capture_output=True, text=True, check=False, env=environment, cwd=REPO_ROOT, timeout=600)
        cls.log = completed.stdout + completed.stderr
        cls.returncode = completed.returncode
        reports = sorted(output.glob('iLEAPP_Output_*'))
        cls.report = reports[-1] if reports else None
        cls.db = None
        if cls.report is not None and (cls.report / '_lava_artifacts.db').exists():
            cls.db = sqlite3.connect(f'file:{cls.report / "_lava_artifacts.db"}?mode=ro', uri=True)

    @classmethod
    def tearDownClass(cls):
        if cls.db is not None:
            cls.db.close()
        cls.folder.cleanup()

    def numbers(self, table):
        # Row Number is stored as text, like every header that is not typed.
        return sorted(int(row[0]) for row in self.db.execute(f'SELECT row_number FROM {table}'))

    def rows(self, table, columns):
        return self.db.execute(f'SELECT {columns} FROM {table} ORDER BY timestamp, row_number, rowid').fetchall()

    def test_the_run_completed_and_produced_the_database(self):
        self.assertEqual(self.returncode, 0, self.log[-2000:])
        self.assertIsNotNone(self.db, self.log[-2000:])
        self.assertIn('Report generation Completed.', self.log)

    def test_stage_one_imports_every_record_and_stage_two_collects_the_markers(self):
        self.assertEqual(self.numbers('logarchive'), list(range(1, len(synthetic.build_lines()) + 1)))
        collected = self.numbers('logarchive_artifacts')
        expected = sorted(synthetic.lines_of('tcc') + synthetic.lines_of('tcc_empty')
                          + synthetic.lines_of('location'))
        self.assertEqual(collected, expected)
        for number in synthetic.lines_of('never'):
            self.assertNotIn(number, collected)

    def test_statedump_records_have_no_subsystem_or_category_in_the_table(self):
        # The premise of the first-line markers: nothing else identifies these records.
        rows = self.db.execute('SELECT DISTINCT subsystem, category FROM logarchive_artifacts').fetchall()
        self.assertEqual(rows, [('', '')])

    def test_tcc_rows_are_one_per_entry_and_empty_dumps_give_none(self):
        listed = self.numbers('logarchive_tcc_cache')
        self.assertEqual(sorted(set(listed)), [n for n in synthetic.lines_of('tcc')])
        self.assertNotIn(synthetic.lines_of('tcc_empty')[0], listed)
        self.assertEqual(len(listed), 19)

    def test_tcc_entry_fields(self):
        rows = self.rows(
            'logarchive_tcc_cache',
            'row_number, process_image_path, process_id, service_as_logged, credential_object_as_logged, '
            'authorization_object_as_logged, auth_right_as_logged, reason_as_logged, version_as_logged, '
            'other_flags_as_logged, entries_in_dump')
        by_row = {}
        for row in rows:
            by_row.setdefault(int(row[0]), []).append(row[1:])
        # Two services in one dump; the entry order is the order logged.
        first = by_row[_row_at(10.0, 'tcc')]
        self.assertEqual(first, [
            (MAPS, '4101', 'kTCCServicePhotos', '0x7f0b00001000', '0x7f0b00002000', 'Allowed', 'Entitled', '2', '', '2'),
            (MAPS, '4101', 'kTCCServiceMicrophone', '0x7f0b00001100', '0x7f0b00002100', 'Allowed', 'User Consent', '1',
             '', '2')])
        # Text after the version is kept, not interpreted.
        flagged = [row for row in by_row[_row_at(12.0, 'tcc')] if row[2] == 'kTCCServiceCamera']
        self.assertEqual(flagged, [(MAPS, '4101', 'kTCCServiceCamera', '0x7f0b00001200', '0x7f0b00002200',
                                    'Denied', 'User Consent', '1', 'Has Prompted For Allow', '3')])
        # The changed entry is listed as the dump held it.
        changed = [row for row in by_row[_row_at(13.0, 'tcc')] if row[2] == 'kTCCServiceMicrophone']
        self.assertEqual(changed[0][5:8], ('Denied', 'System Set', '1'))
        # The values that carry no grant are copied as logged.
        other = {row[2]: row[5:8] for row in by_row[_row_at(20.0, 'tcc')]}
        self.assertEqual(other, {'kTCCServiceCamera': ('Allowed', 'System Set', '1'),
                                 'kTCCServicePhotos': ('Limited', 'Service Policy', '2'),
                                 'kTCCServiceAddressBook': ('Unknown', 'None', '1')})
        # A restarted process is listed under its new PID.
        self.assertEqual(by_row[_row_at(30.0, 'tcc')][0][:2], (MAPS, '4103'))

    def test_tcc_fallbacks_keep_the_text_and_leave_fields_blank(self):
        records = {int(row[0]): row[1:] for row in self.db.execute(
            'SELECT row_number, service_as_logged, credential_object_as_logged, authorization_object_as_logged, '
            'auth_right_as_logged, reason_as_logged, version_as_logged, other_flags_as_logged, '
            'entries_in_dump, authorization_record_as_logged FROM logarchive_tcc_cache')}
        # An authorization description in another layout.
        row = records[_row_at(40.0, 'tcc')]
        self.assertEqual(row[:8], ('kTCCServiceCamera', '0x7f0b00007000', '', '', '', '', '', '1'))
        self.assertIn('something else entirely', row[8])
        # A service that maps to a string.
        row = records[_row_at(41.0, 'tcc')]
        self.assertEqual((row[0], row[1], row[8]), ('kTCCServiceCalendar', '', 'not an object'))
        # A body cut off mid-way: one row, body text as logged, nothing parsed.
        row = records[_row_at(42.0, 'tcc')]
        self.assertEqual(row[:8], ('', '', '', '', '', '', '', ''))
        self.assertTrue(row[8].startswith('{"kTCCServiceCamera":{"<Credential (0x7f0b00009000)'))
        # A message with no body: the whole message.
        self.assertEqual(records[_row_at(43.0, 'tcc')][8], 'title: TCC Authorization Cache')
        # No address on the credential; the key, not the description's service, is the Service.
        row = records[_row_at(44.0, 'tcc')]
        self.assertEqual(row[:7], ('kTCCServiceCamera', '', '0x7f0b0000a000', 'Allowed', 'Entitled', '2', ''))
        self.assertIn('Service: kTCCServiceMicrophone', row[8])

    def test_tcc_summary_collapses_identical_entries(self):
        rows = {(row[0], row[1], row[2], row[3], row[4], row[5]): row[6:] for row in self.db.execute(
            'SELECT process_image_path, process_id, service_as_logged, auth_right_as_logged, reason_as_logged, '
            'version_as_logged, other_flags_as_logged, first_dump, last_dump, dumps, entries '
            'FROM logarchive_tcc_cache_summary')}
        self.assertEqual(len(rows), 12)
        photos = rows[(MAPS, '4101', 'kTCCServicePhotos', 'Allowed', 'Entitled', '2')]
        self.assertEqual(photos, ('', BASE_EPOCH + 10, BASE_EPOCH + 13, '4', '4'))
        microphone = rows[(MAPS, '4101', 'kTCCServiceMicrophone', 'Allowed', 'User Consent', '1')]
        self.assertEqual(microphone[1:], (BASE_EPOCH + 10, BASE_EPOCH + 12, '3', '3'))
        denied = rows[(MAPS, '4101', 'kTCCServiceMicrophone', 'Denied', 'System Set', '1')]
        self.assertEqual(denied[1:], (BASE_EPOCH + 13, BASE_EPOCH + 13, '1', '1'))
        flagged = rows[(MAPS, '4101', 'kTCCServiceCamera', 'Denied', 'User Consent', '1')]
        self.assertEqual(flagged, ('Has Prompted For Allow', BASE_EPOCH + 12, BASE_EPOCH + 13, '2', '2'))
        # The restarted process is its own row; two unreadable dumps share one.
        self.assertEqual(rows[(MAPS, '4103', 'kTCCServicePhotos', 'Allowed', 'Entitled', '2')][3:], ('1', '1'))
        self.assertEqual(rows[(TCC_DAEMON, '90', '', '', '', '')][3:], ('2', '2'))

    def test_location_rows(self):
        self.assertEqual(self.numbers('logarchive_location_state'), synthetic.lines_of('location'))

    def test_location_fields(self):
        columns = ('updating_location_as_logged, requesting_location_as_logged, updating_heading_as_logged, '
                   'updating_ranging_as_logged, requesting_ranging_as_logged, '
                   'allows_background_location_updates_as_logged, shows_background_location_indicator_as_logged, '
                   'paused_as_logged, batching_location_as_logged, limits_precision_as_logged, '
                   'dynamic_accuracy_reduction_enabled_as_logged, previous_authorization_status_valid_as_logged, '
                   'previous_authorization_status_as_logged, desired_accuracy_as_logged, distance_filter_as_logged, '
                   'activity_type_as_logged, other_fields_as_logged')
        by_row = {int(row[0]): row[1:] for row in self.db.execute(
            f'SELECT row_number, process_image_path, process_id, {columns} FROM logarchive_location_state')}
        idle = by_row[_row_at(100.0, 'location')]
        self.assertEqual(idle[:2], (MAPS, '4101'))
        self.assertEqual(idle[2:], (
            'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false',
            'true', '2', '-1', '-1', '0',
            'headingFilter: 1; allowsLocationPrompts: true; allowsAlteredAccessoryLocations: false; '
            'pausesLocationUpdatesAutomatically: 5; allowsMapCorrection: true; updatingVehicleSpeed: false; '
            'updatingVehicleHeading: false; matchInfoEnabled: false; groundAltitudeEnabled: false; '
            'fusionInfoEnabled: false; courtesyPromptNeeded: false; isAuthorizedForWidgetUpdates: false'))
        updating = by_row[_row_at(110.0, 'location')]
        self.assertEqual((updating[2], updating[15], updating[16]), ('true', '100', '50'))
        limited = by_row[_row_at(130.0, 'location')]
        self.assertEqual((limited[11], limited[14]), ('true', '3'))
        background = by_row[_row_at(140.0, 'location')]
        self.assertEqual((background[2], background[7], background[17]), ('true', 'true', '3'))
        system = by_row[_row_at(150.0, 'location')]
        self.assertEqual((system[1], system[3], system[12], system[13], system[15], system[16]),
                         ('210', 'true', 'true', 'false', '2147483646', '500'))

    def test_location_fallbacks(self):
        other = {int(row[0]): row[1] for row in self.db.execute(
            'SELECT row_number, other_fields_as_logged FROM logarchive_location_state')}
        paused = {int(row[0]): row[1] for row in self.db.execute(
            'SELECT row_number, paused_as_logged FROM logarchive_location_state')}
        updating = {int(row[0]): row[1] for row in self.db.execute(
            'SELECT row_number, updating_location_as_logged FROM logarchive_location_state')}
        # A key with no column is kept in order of appearance, and a missing key leaves its column blank.
        unknown = _row_at(160.0, 'location')
        self.assertEqual(paused[unknown], '')
        self.assertIn('futureKey: "text value"', other[unknown])
        # A repeated key: the first value fills the column, the second is kept.
        repeated = _row_at(170.0, 'location')
        self.assertEqual(updating[repeated], 'false')
        self.assertIn('updatingLocation: true', other[repeated])
        # A line that is not a key and value is kept.
        self.assertIn('stray line', other[_row_at(180.0, 'location')])
        # No body: every column blank and the message in Other Fields.
        bodiless = _row_at(190.0, 'location')
        self.assertEqual(updating[bodiless], '')
        self.assertTrue(other[bodiless].startswith('title: CLLocationManagerStateTracker'))

    def test_location_summary_groups_by_content(self):
        rows = self.db.execute(
            'SELECT process_image_path, process_id, updating_location_as_logged, limits_precision_as_logged, '
            'first_dump, last_dump, dumps FROM logarchive_location_state_summary').fetchall()
        self.assertEqual(len(rows), 9)
        by_key = {row[:4]: row[4:] for row in rows}
        # Three dumps (two with the same record time and different rows) with equal content.
        self.assertEqual(by_key[(MAPS, '4101', 'true', 'false')], (BASE_EPOCH + 110, BASE_EPOCH + 120, '3'))
        self.assertEqual(by_key[(MAPS, '4101', 'false', 'false')], (BASE_EPOCH + 100, BASE_EPOCH + 100, '1'))
        self.assertEqual(by_key[(MAPS, '4101', 'false', 'true')], (BASE_EPOCH + 130, BASE_EPOCH + 130, '1'))

    def test_timestamps_are_utc_epoch_seconds_of_the_record(self):
        first = self.db.execute('SELECT timestamp FROM logarchive_tcc_cache ORDER BY row_number LIMIT 1').fetchone()[0]
        self.assertAlmostEqual(first, BASE_EPOCH + 10.0, places=3)
        first = self.db.execute('SELECT timestamp FROM logarchive_location_state ORDER BY row_number LIMIT 1'
                                ).fetchone()[0]
        self.assertAlmostEqual(first, BASE_EPOCH + 100.0, places=3)

    def test_every_output_format_was_written(self):
        names = ('logarchive TCC authorization cache dumps', 'logarchive TCC authorization cache summary',
                 'logarchive location manager state dumps', 'logarchive location manager state summary')
        for name in names:
            with self.subTest(name=name):
                self.assertTrue((self.report / '_TSV Exports' / f'{name}.tsv').exists())
                self.assertTrue(list((self.report / '_HTML').glob(f'{name.replace(" ", "_")}.html')))
        self.assertTrue((self.report / '_Timeline' / 'tl.db').exists())
        manifest = json.loads((self.report / '_lava_data.lava').read_text(encoding='utf-8'))
        tables = {artifact['tablename'] for group in manifest['artifacts'].values() for artifact in group}
        for table in ('logarchive_tcc_cache', 'logarchive_tcc_cache_summary', 'logarchive_location_state',
                      'logarchive_location_state_summary'):
            self.assertIn(table, tables)

    def test_no_duplicate_artifact_names_were_rejected(self):
        self.assertNotIn('duplicate', self.log.lower())


class MarkerTest(unittest.TestCase):
    """The dependent filters only find what the collection stage materialized."""

    def test_every_dependent_pattern_is_collected(self):
        collected = _like_patterns(inspect.getsource(logarchive.logarchive_artifacts.__wrapped__))
        for name in ('TCC_CACHE_WHERE', 'LOCATION_STATE_WHERE'):
            patterns = _like_patterns(getattr(logarchive, name))
            self.assertTrue(patterns, name)
            for pattern in patterns:
                with self.subTest(name=name, pattern=pattern):
                    self.assertIn(pattern, collected)

    def test_collection_predicate_is_accepted_by_the_compiled_prefilter(self):
        # The prefilter falls back to plain SQL for an expression it cannot read; the fallback is
        # correct but slow on a tens-of-millions-row import, so a change that trips it is worth knowing.
        from scripts import log_filter  # pylint: disable=import-outside-toplevel
        source = inspect.getsource(logarchive.logarchive_artifacts.__wrapped__)
        query = source.split("query = '''", 1)[1].split("'''", 1)[0]
        prefix = log_filter._SELECT.match(query)  # pylint: disable=protected-access
        self.assertIsNotNone(prefix)
        self.assertIsNotNone(log_filter._anchors(query[prefix.end():]))  # pylint: disable=protected-access

    def test_markers_are_anchored_at_the_start_of_the_message(self):
        # A statedump title is the first line; the same words inside another message must not match.
        for where, title in ((logarchive.TCC_CACHE_WHERE, 'title: TCC Authorization Cache'),
                             (logarchive.LOCATION_STATE_WHERE, 'title: CLLocationManagerStateTracker')):
            db = sqlite3.connect(':memory:')
            db.execute('CREATE TABLE t (event_message TEXT)')
            db.executemany('INSERT INTO t VALUES (?)', [(title + '\nbody',), ('x ' + title,), (title.upper(),)])
            hits = db.execute(f'SELECT event_message FROM t WHERE {where}').fetchall()
            db.close()
            # SQLite LIKE ignores ASCII case, so the upper-case title is collected; the parsers read it
            # the same way. A title in the middle of a message is not.
            self.assertEqual(sorted(hit[0] for hit in hits), sorted([title + '\nbody', title.upper()]))


class ParserTest(unittest.TestCase):
    def entries(self, message):
        return logarchive._tcc_cache_entries(message)  # pylint: disable=protected-access

    def location(self, message):
        return logarchive._location_state_fields(message)  # pylint: disable=protected-access

    def test_statedump_body_starts_at_the_first_brace_line(self):
        body = logarchive._statedump_body  # pylint: disable=protected-access
        self.assertEqual(body('title: x\nObject Type: \n{"a":1}'), '{"a":1}')
        self.assertEqual(body('title: x\n   {\n  "a":1,\n}'), '   {\n  "a":1,\n}')
        for message in ('title: x', '', None):
            self.assertEqual(body(message), '')

    def test_tcc_entries_in_logged_order(self):
        message = synthetic.tcc_dump([
            ('kTCCServiceB', '0x1', '0x2', 'Allowed', 'Entitled', '2', ''),
            ('kTCCServiceA', '0x3', '0x4', 'Denied', 'User Consent', '1', 'Has Prompted For Allow')])
        entries = self.entries(message)
        self.assertEqual([entry['service'] for entry in entries], ['kTCCServiceB', 'kTCCServiceA'])
        self.assertEqual(entries[1]['flags'], 'Has Prompted For Allow')
        self.assertEqual((entries[0]['credential'], entries[0]['authorization']), ('0x1', '0x2'))

    def test_tcc_unreadable_input_is_none_and_an_empty_cache_is_an_empty_list(self):
        self.assertEqual(self.entries(synthetic.TCC_TITLE + '{}'), [])
        for message in ('', None, 'title: TCC Authorization Cache', synthetic.TCC_TITLE + '{"a":',
                        synthetic.TCC_TITLE + '[1, 2]', synthetic.TCC_TITLE + '"text"'):
            with self.subTest(message=message):
                self.assertIsNone(self.entries(message))

    def test_tcc_deeply_nested_body_is_unreadable_not_an_error(self):
        self.assertIsNone(self.entries(synthetic.TCC_TITLE + '[' * 100000))

    def test_tcc_record_text_is_not_interpreted(self):
        message = synthetic.TCC_TITLE + json.dumps({'kTCCServiceX': {'<Credential (0xA) | Requestor>': (
            '<Authorization Record (0xB) | Service: kTCCServiceX, AuthRight: Odd Value, Reason: Other, '
            'Version: 9, flag one, flag two, >')}})
        entry = self.entries(message)[0]
        self.assertEqual((entry['right'], entry['reason'], entry['version'], entry['flags']),
                         ('Odd Value', 'Other', '9', 'flag one, flag two'))

    def test_location_values_are_copied_as_logged(self):
        values, other = self.location(synthetic.location_dump(distanceFilter='-1', desiredAccuracy='6380000'))
        columns = [key for key, _header in logarchive.LOCATION_COLUMNS]
        self.assertEqual(values[columns.index('desiredAccuracy')], '6380000')
        self.assertEqual(values[columns.index('distanceFilter')], '-1')
        self.assertTrue(other.startswith('headingFilter: 1;'))

    def test_location_without_a_body_keeps_the_message(self):
        values, other = self.location('title: CLLocationManagerStateTracker')
        self.assertEqual(set(values), {''})
        self.assertEqual(other, 'title: CLLocationManagerStateTracker')
        values, other = self.location(None)
        self.assertEqual((set(values), other), ({''}, ''))

    def test_location_keys_inside_other_words_are_not_read(self):
        message = synthetic.LOCATION_TITLE + '{\n  "notupdatingLocation":true,\n  "updatingLocation":false,\n}'
        values, other = self.location(message)
        columns = [key for key, _header in logarchive.LOCATION_COLUMNS]
        self.assertEqual(values[columns.index('updatingLocation')], 'false')
        self.assertEqual(other, 'notupdatingLocation: true')

    def test_range_ignores_a_time_that_is_not_a_number(self):
        group = {'first': None, 'last': None}
        for value in (None, '', True, 5.0, 3, 9.5, 'x'):
            logarchive._widen_range(group, value)  # pylint: disable=protected-access
        self.assertEqual((group['first'], group['last']), (3, 9.5))

    def test_headers_match_the_row_width(self):
        self.assertEqual(len(logarchive.LOCATION_STATE_HEADERS), 4 + len(logarchive.LOCATION_COLUMNS) + 1)
        self.assertEqual(len(logarchive.LOCATION_STATE_SUMMARY_HEADERS), 3 + 2 + len(logarchive.LOCATION_COLUMNS) + 1)
        self.assertEqual(len(logarchive.TCC_CACHE_HEADERS), 13)
        self.assertEqual(len(logarchive.TCC_CACHE_SUMMARY_HEADERS), 11)


class FixtureTest(unittest.TestCase):
    def test_fixture_is_reproducible_and_invented(self):
        self.assertEqual(synthetic.to_bytes(), synthetic.to_bytes())
        records = json.loads(synthetic.to_bytes())
        self.assertEqual(len(records), len(synthetic.build_lines()))
        for record in records:
            stamp = datetime.strptime(record['timestamp'], '%Y-%m-%d %H:%M:%S.%f%z')
            self.assertEqual(stamp.utcoffset(), timedelta(hours=-5))
            self.assertEqual(stamp.year, 2026)
            self.assertTrue(record['processImagePath'].startswith(('/usr/libexec/fake', synthetic.MAPS[:50])))
        # Object addresses are all in the invented 0x7f0b range.
        addresses = set(re.findall(r'0x[0-9a-fA-F]+', synthetic.to_bytes().decode('utf-8')))
        self.assertTrue(addresses)
        self.assertTrue(all(address.startswith('0x7f0b') for address in addresses))


if __name__ == '__main__':
    unittest.main()
