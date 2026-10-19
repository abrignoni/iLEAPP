"""Camera and microphone capture artifacts, through the real two-stage logarchive chain.

The three artifacts here read the table logarchive_artifacts builds, and that table holds only
rows its own marker list collected. A test that queries the dependent artifact on a hand-made
table cannot see a marker missing from the collection stage, so the main test runs the real
ileapp.py on a synthetic 'log show' export (synthetic_capture_sessions.py) and reads what each
stage wrote. Everything in the export is invented.
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

import synthetic_capture_sessions as synthetic  # pylint: disable=wrong-import-position
from scripts.artifacts import logarchive  # pylint: disable=wrong-import-position

PROFILE = {'leapp': 'ileapp', 'format_version': 1,
           'plugins': ['logarchive', 'logarchive_artifacts', 'logarchive_capture_sessions',
                       'logarchive_capture_streaming', 'logarchive_recording_indicator',
                       'logarchive_flashlight', 'logarchive_camera']}
BASE_EPOCH = datetime(2026, 3, 14, 15, 0, 0, tzinfo=timezone.utc).timestamp()  # 10:00:00 at -0500


def _like_patterns(sql):
    return set(re.findall(r"LIKE '([^']*)'", sql))


class ChainTest(unittest.TestCase):
    """ileapp.py on the fixture: producer, collection stage, then the dependent artifacts."""

    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.TemporaryDirectory()
        root = pathlib.Path(cls.folder.name)
        extraction = root / 'extraction'
        extraction.mkdir()
        (extraction / synthetic.FIXTURE_NAME).write_bytes(synthetic.to_bytes())
        profile = root / 'capture.ilprofile'
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

    def test_the_run_completed_and_produced_the_database(self):
        self.assertEqual(self.returncode, 0, self.log[-2000:])
        self.assertIsNotNone(self.db, self.log[-2000:])
        self.assertIn('Report generation Completed.', self.log)

    def test_stage_one_imports_every_record_and_stage_two_collects_the_markers(self):
        self.assertEqual(self.numbers('logarchive'), list(range(1, len(synthetic.build_lines()) + 1)))
        collected = self.numbers('logarchive_artifacts')
        expected = sorted(synthetic.lines_of('listed') + synthetic.lines_of('held')
                          + synthetic.lines_of('power') + synthetic.lines_of('indicator'))
        self.assertEqual(collected, expected)
        for number in synthetic.lines_of('never'):
            self.assertNotIn(number, collected)

    def test_sessions_list_the_lifecycle_lines_and_hold_back_idle_state(self):
        listed = self.numbers('logarchive_capture_sessions')
        self.assertEqual(listed, synthetic.lines_of('listed'))
        for number in synthetic.lines_of('held'):
            self.assertNotIn(number, listed)

    def test_streaming_and_indicator_rows(self):
        self.assertEqual(self.numbers('logarchive_capture_streaming'), synthetic.lines_of('power'))
        self.assertEqual(self.numbers('logarchive_recording_indicator'), synthetic.lines_of('indicator'))

    def test_torch_and_device_vendor_lines_reach_no_artifact(self):
        torch = [i for i, line in enumerate(synthetic.build_lines(), start=1)
                 if 'FigFlashlightLocal' in line[5] or 'ClientIsActive' in line[5]]
        self.assertTrue(torch)
        collected = set(self.numbers('logarchive_artifacts'))
        self.assertFalse(collected & set(torch))
        for table in ('logarchive_flashlight', 'logarchive_camera'):
            exists = self.db.execute("SELECT 1 FROM sqlite_master WHERE name = ?", (table,)).fetchone()
            self.assertIsNone(exists, f'{table} should have nothing to report for this export')

    def test_timestamps_are_utc_epoch_seconds_of_the_record(self):
        first = self.db.execute('SELECT timestamp FROM logarchive_capture_sessions '
                                'ORDER BY row_number LIMIT 1').fetchone()[0]
        self.assertAlmostEqual(first, BASE_EPOCH + 0.100, places=3)

    def test_session_fields_by_row(self):
        by_row = {int(row[0]): row for row in self.db.execute(
            'SELECT row_number, logged_function, client_app_id_as_logged, client_pid_as_logged, '
            'session_object_as_logged, client_started_session, camaudio, background, mic_stolen, '
            'camera_stolen, runtime_error, interruption_error, session_status, status_transition '
            'FROM logarchive_capture_sessions')}
        lines = synthetic.build_lines()

        def row_of(sec, fragment):
            return next(index for index, line in enumerate(lines, start=1)
                        if abs(line[0] - sec) < 1e-6 and fragment in line[5])

        # Create line with only a PID, then the tagged line.
        self.assertEqual(by_row[row_of(0.100, 'Creating session')][2:5], ('', '3101', ''))
        self.assertEqual(by_row[row_of(0.101, 'New session')][2:5], ('com.example.fakecam', '3101', '0x7f0a11c000'))
        # A start with the state fields of the iOS 27 shape.
        started = by_row[row_of(10.001, 'ClientStartRunning')]
        self.assertEqual(started[1], 'captureSession_StartRunning')
        self.assertEqual(started[5:], ('1', '1/0', '0', '0', '0', '0', '0', 'Idle', ''))
        # Running in the background, the camera lost, the microphone lost with the audio flag set.
        self.assertEqual(by_row[row_of(20.0, 'Update:1')][5:9], ('1', '1/0', '1', '0'))
        self.assertEqual(by_row[row_of(25.0, 'Update:1')][5:10], ('0', '1/0', '0', '0', '1'))
        self.assertEqual(by_row[row_of(30.0, 'Update:1')][5:10], ('1', '0/1', '0', '1', '0'))
        # A transition is copied whole; the timing line "Starting took" is not listed.
        self.assertEqual(by_row[row_of(10.002, 'Idle ->')][13], 'Idle -> Starting Running')
        self.assertNotIn(row_of(10.291, 'Starting took'), by_row)
        # A tag with no app id leaves it blank and keeps the PID.
        self.assertEqual(by_row[row_of(110.0, 'New session')][2:5], ('', '3105', '0x7f0a11f000'))
        # The iOS 26.6 shape has neither runtime error nor session status.
        legacy = by_row[row_of(210.001, 'active:0')]
        self.assertEqual(legacy[5:13], ('1', '1/0', '0', '0', '0', '', '', ''))
        # The lowercase spelling is listed with no state fields.
        lowered = by_row[row_of(210.002, 'clientRequested')]
        self.assertEqual(lowered[1], 'captureSession_updateSessionRunningCondition_block_invoke')
        self.assertEqual(lowered[5:], ('',) * 9)
        # Client-side calls: the writer is the client process, so no tag fields.
        client = by_row[row_of(300.0, 'startRunning')]
        self.assertEqual((client[1], client[2], client[3], client[4]), ('-[AVCaptureSession startRunning]', '', '', ''))

    def test_streaming_fields(self):
        rows = self.db.execute(
            'SELECT client_pid_as_logged, application_id_as_logged, device_type_as_logged, '
            'streaming_as_logged, port_type_as_logged FROM logarchive_capture_streaming '
            'ORDER BY row_number').fetchall()
        self.assertEqual(rows, [('3101', '<private>', '20', '1', 'PortTypeFrontInfrared'),
                                ('3101', '<private>', '20', '0', 'PortTypeFrontInfrared'),
                                ('3103', 'com.example.fakevideo', '2', '1', 'PortTypeBack'),
                                ('', '', '', '', '')])

    def test_every_output_format_was_written(self):
        names = ('logarchive camera and microphone capture sessions',
                 'logarchive camera streaming power events', 'logarchive recording indicator lines')
        for name in names:
            with self.subTest(name=name):
                self.assertTrue((self.report / '_TSV Exports' / f'{name}.tsv').exists())
                self.assertTrue(list((self.report / '_HTML').glob(f'{name.replace(" ", "_")}.html')))
        self.assertTrue((self.report / '_Timeline' / 'tl.db').exists())
        manifest = json.loads((self.report / '_lava_data.lava').read_text(encoding='utf-8'))
        tables = {artifact['tablename'] for group in manifest['artifacts'].values() for artifact in group}
        for table in ('logarchive_capture_sessions', 'logarchive_capture_streaming',
                      'logarchive_recording_indicator'):
            self.assertIn(table, tables)

    def test_no_duplicate_artifact_names_were_rejected(self):
        self.assertNotIn('duplicate', self.log.lower())


class MarkerTest(unittest.TestCase):
    """The dependent filters only find what the collection stage materialized."""

    def test_every_dependent_pattern_is_collected(self):
        collected = _like_patterns(inspect.getsource(logarchive.logarchive_artifacts.__wrapped__))
        for name in ('CAPTURE_SESSION_WHERE', 'CAPTURE_STREAMING_WHERE', 'RECORDING_INDICATOR_WHERE'):
            for pattern in _like_patterns(getattr(logarchive, name)):
                if pattern in ('% -> %', '%Stopped running%', '%ClientStartedSession:1%',
                               '%micStolen:1%', '%cameraStolen:1%'):
                    continue  # narrowing conditions on a row the collection stage already holds
                with self.subTest(name=name, pattern=pattern):
                    self.assertIn(pattern, collected)

    def test_subsystem_conditions_match(self):
        source = inspect.getsource(logarchive.logarchive_artifacts.__wrapped__)
        self.assertIn("subsystem = 'com.apple.cameracapture'", source)
        self.assertIn("subsystem = 'com.apple.SpringBoard'", source)
        for name in ('CAPTURE_SESSION_WHERE', 'CAPTURE_STREAMING_WHERE'):
            self.assertIn("subsystem = 'com.apple.cameracapture'", getattr(logarchive, name))
        self.assertIn("subsystem = 'com.apple.SpringBoard'", logarchive.RECORDING_INDICATOR_WHERE)

    def test_collection_predicate_is_accepted_by_the_compiled_prefilter(self):
        # The prefilter falls back to plain SQL for an expression it cannot read; the fallback is
        # correct but slow on a tens-of-millions-row import, so a change that trips it is worth knowing.
        from scripts import log_filter  # pylint: disable=import-outside-toplevel
        source = inspect.getsource(logarchive.logarchive_artifacts.__wrapped__)
        query = source.split("query = '''", 1)[1].split("'''", 1)[0]
        prefix = log_filter._SELECT.match(query)  # pylint: disable=protected-access
        self.assertIsNotNone(prefix)
        self.assertIsNotNone(log_filter._anchors(query[prefix.end():]))  # pylint: disable=protected-access


class ParserTest(unittest.TestCase):
    TAG = '<0x7f0a11c000[3101][com.example.fakecam]>'

    def fields(self, message):
        return logarchive._capture_session_fields(message)  # pylint: disable=protected-access

    def test_ios27_state_line(self):
        message = ('<<<< FigCaptureSession >>>> captureSession_StopRunning: ' + self.TAG
                   + ' ClientStartedSession:1 Cam/Audio:1/0 bg:1 prewarming:0 micStolen:1 multitasking:0 '
                   'pip:0 cameraStolen:1 pressured:0 interruptions:0 runtimeError:2 stopRequired:0 '
                   'shouldRun:1 interruptionError:3 sessionStatus:Running ClientStopRunning')
        fields = self.fields(message)
        self.assertEqual((fields['function'], fields['app_id'], fields['pid'], fields['session_object']),
                         ('captureSession_StopRunning', 'com.example.fakecam', '3101', '0x7f0a11c000'))
        self.assertEqual((fields['started'], fields['cam_audio'], fields['background']), ('1', '1/0', '1'))
        self.assertEqual((fields['mic_stolen'], fields['camera_stolen'], fields['runtime_error'],
                          fields['interruption_error'], fields['status']), ('1', '1', '2', '3', 'Running'))

    def test_a_flag_name_inside_another_word_is_not_read(self):
        message = ('<<<< FigCaptureSession >>>> captureSession_X: ' + self.TAG
                   + ' ClientStartedSession:1 Cam/Audio:1/0 bg:0 notmicStolen:1 cameraStolen:0')
        fields = self.fields(message)
        self.assertEqual((fields['mic_stolen'], fields['camera_stolen']), ('', '0'))

    def test_unrecognised_input_gives_blanks_not_a_guess(self):
        for message in ('', None, 'something else entirely', '<<<< FigCaptureSession >>>> '):
            with self.subTest(message=message):
                self.assertEqual(set(self.fields(message).values()), {''})

    def test_creating_session_line_gives_only_the_pid(self):
        fields = self.fields('<<<< FigCaptureSession >>>> FigCaptureSessionCreate: Creating session for PID 42')
        self.assertEqual((fields['function'], fields['pid'], fields['app_id']), ('FigCaptureSessionCreate', '42', ''))

    def test_transition_requires_an_arrow(self):
        timing = '<<<< FigCaptureSession >>>> captureSession_transitionToSessionStatus: ' + self.TAG + ' Starting took 1.0ms'
        self.assertEqual(self.fields(timing)['transition'], '')
        moved = '<<<< FigCaptureSession >>>> captureSession_transitionToSessionStatus: ' + self.TAG + ' Idle -> Starting Running'
        self.assertEqual(self.fields(moved)['transition'], 'Idle -> Starting Running')


class FixtureTest(unittest.TestCase):
    def test_fixture_is_reproducible_and_invented(self):
        self.assertEqual(synthetic.to_bytes(), synthetic.to_bytes())
        records = json.loads(synthetic.to_bytes())
        self.assertEqual(len(records), len(synthetic.build_lines()))
        text = synthetic.to_bytes().decode('utf-8')
        self.assertNotIn('biometrickitd', text)
        for record in records:
            stamp = datetime.strptime(record['timestamp'], '%Y-%m-%d %H:%M:%S.%f%z')
            self.assertEqual(stamp.utcoffset(), timedelta(hours=-5))
            self.assertEqual(stamp.year, 2026)


if __name__ == '__main__':
    unittest.main()
