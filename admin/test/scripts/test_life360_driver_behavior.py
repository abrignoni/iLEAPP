"""Synthetic regression controls for diagnostic records, time bases and provenance."""
from datetime import datetime, timezone
import fnmatch
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from admin.test.fixtures.life360.make_synthetic_driver_behavior import build_logs
from scripts.artifacts import life360DriverBehavior as diagnostics


class _Context:
    def __init__(self, root):
        self.root = Path(root)
        self.files = [str(path) for path in self.root.rglob('*') if path.is_file()
                      and fnmatch.fnmatchcase(str(path), '*/com.life360.safetymap*.log')]

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root)).replace('\\', '/')


def _run(context):
    headers, rows, sources = diagnostics.life360CrashDetection.__wrapped__(context)
    names = [header[0] if isinstance(header, tuple) else header for header in headers]
    if any(len(row) != len(headers) for row in rows):
        raise AssertionError('Output row width differs from headers')
    return [dict(zip(names, row)) for row in rows], sources


class DriverBehaviorTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.main, self.sidecar = build_logs(self.root / 'one')

    def test_record_families_and_mixed_explicit_time_zones(self):
        rows, _ = _run(_Context(self.root))
        self.assertEqual(len(rows), 9)
        crash = next(row for row in rows if row['Trip ID'] == 'synthetic-trip-a')
        self.assertEqual(crash['Logged Time'], datetime(2026, 1, 15, 7, 0, 30, 625000, timezone.utc))
        self.assertEqual(crash['Event Time'], datetime(2026, 1, 15, 7, 0, 30, tzinfo=timezone.utc))
        self.assertEqual(crash['Speed (as stored)'], '11.176')
        self.assertEqual(crash['Accuracy (as stored)'], '45.0')
        self.assertIn('UnmappedSetting: keep-me', crash['Raw Log Record'])
        details = next(row for row in rows if row['Record Kind'] == 'Detector details')
        self.assertEqual(details['Confidence (as stored)'], '0.8125')
        self.assertEqual(details['Detector Start'], datetime(2026, 1, 15, 7, 0, tzinfo=timezone.utc))
        self.assertEqual(details['Detector End'], datetime(2026, 1, 15, 7, 0, 30, tzinfo=timezone.utc))
        self.assertEqual(details['Trip ID'], '')
        self.assertEqual(crash['Confidence (as stored)'], '')

    def test_warning_and_later_detection_remain_separate_with_exact_source_lines(self):
        rows, _ = _run(_Context(self.root))
        warning = next(row for row in rows if row['Record Kind'] == 'Accelerometer anomaly warning')
        self.assertEqual(warning['Source Line End'] - warning['Source Line'], 2)
        self.assertIn('collision capability will be deactivated', warning['Raw Log Record'])
        self.assertIn('\n', warning['Raw Log Record'])
        crash = next(row for row in rows if row['Trip ID'] == 'synthetic-trip-a')
        self.assertLess(warning['Logged Time'], crash['Logged Time'])
        self.assertEqual(warning['Event ID'], '')
        self.assertEqual(warning['Confidence (as stored)'], '')
        for row in rows:
            path = self.root / row['Source File']
            lines = path.read_text().splitlines(keepends=True)
            observed = ''.join(lines[row['Source Line'] - 1:row['Source Line End']]).rstrip('\r\n')
            self.assertEqual(row['Raw Log Record'], observed)

    def test_unknown_diagnostic_is_retained_and_unrelated_component_is_not_reported(self):
        with patch.object(diagnostics, 'logfunc') as log:
            rows, _ = _run(_Context(self.root))
        unknown = [row for row in rows if row['Record Kind'] == 'Other crash/collision diagnostic']
        self.assertEqual(len(unknown), 1)
        self.assertIn('syntheticQuality=unknown', unknown[0]['Raw Log Record'])
        self.assertTrue(any('unrecognised' in call.args[0] for call in log.call_args_list))
        self.assertTrue(all('unrelated component' not in row['Raw Log Record'] for row in rows))

    def test_explicit_zero_values_and_subsecond_event_time_are_preserved(self):
        rows, _ = _run(_Context(self.root))
        crash = next(row for row in rows if row['Trip ID'] == 'synthetic-trip-b')
        self.assertEqual(crash['Speed (as stored)'], '0')
        self.assertEqual(crash['Accuracy (as stored)'], '0')
        self.assertEqual(crash['Event Time'].microsecond, 125000)

    def test_prefix_date_rollover_does_not_replace_embedded_event_date(self):
        text = self.main.read_text().replace('2026-01-15T12:30:30.625+0530',
                                            '2026-01-16T00:10:00.625+0530')
        self.main.write_text(text)
        rows, _ = _run(_Context(self.root))
        crash = next(row for row in rows if row['Trip ID'] == 'synthetic-trip-a')
        self.assertEqual(crash['Logged Time'], datetime(2026, 1, 15, 18, 40, 0, 625000, timezone.utc))
        self.assertEqual(crash['Event Time'], datetime(2026, 1, 15, 7, 0, 30, tzinfo=timezone.utc))

    def test_identical_records_in_one_file_keep_distinct_line_numbers(self):
        text = self.main.read_text()
        repeated = next(line for line in text.splitlines() if 'Crash detected: TripID:' in line)
        self.main.write_text(text + repeated + '\n')
        rows, _ = _run(_Context(self.root))
        self.assertEqual(len(rows), 10)
        copies = [row for row in rows if row['Trip ID'] == 'synthetic-trip-a']
        self.assertEqual(len(copies), 2)
        self.assertEqual(copies[0]['Raw Log Record'], copies[1]['Raw Log Record'])
        self.assertNotEqual(copies[0]['Source Line'], copies[1]['Source Line'])

    def test_invalid_timestamps_keep_raw_records_and_log_without_failed_values(self):
        cases = (
            ('2026-01-15T12:30:30.625+0530', '2026-99-15T12:30:30.625+0530'),
            ('2026-01-15T12:30:30.625+0530', '2026-01-15T12:30:30.625'),
            ('2026-01-15T12:30:30.625+0530', '2026-01-15T12:30:30.6251234+0530'),
            ('Timestamp: 2026-01-15 07:00:30 +0000', 'Timestamp: synthetic-private-time'),
            ('Timestamp: 2026-01-15 07:00:30 +0000', 'Timestamp: 2026-01-15 07:00:30 +2500'),
        )
        original = self.main.read_text()
        for before, after in cases:
            with self.subTest(shape=after.split(':', 1)[0]):
                self.main.write_text(original.replace(before, after))
                with patch.object(diagnostics, 'logfunc') as log:
                    rows, _ = _run(_Context(self.root))
                self.assertEqual(len(rows), 9)
                crash = next(row for row in rows if row['Trip ID'] == 'synthetic-trip-a')
                self.assertEqual(crash['Logged Time'] if before.startswith('2026') else crash['Event Time'], '')
                self.assertTrue(any('could not be converted' in call.args[0] for call in log.call_args_list))
                self.assertTrue(all('synthetic-private-time' not in call.args[0] for call in log.call_args_list))

    def test_invalid_location_retains_record_and_other_fields(self):
        original = self.main.read_text()
        self.main.write_text(original.replace('Location: <0.5, -150.5>', 'Location: <not-a-coordinate>'))
        with patch.object(diagnostics, 'logfunc') as log:
            rows, _ = _run(_Context(self.root))
        crash = next(row for row in rows if row['Trip ID'] == 'synthetic-trip-a')
        self.assertEqual((crash['Latitude'], crash['Longitude']), ('', ''))
        self.assertEqual(crash['Speed (as stored)'], '11.176')
        self.assertTrue(any('location could not be decoded' in call.args[0] for call in log.call_args_list))

    def test_copies_and_distinct_containers_survive_duplicate_views_collapse(self):
        initial, _ = _run(_Context(self.root))
        build_logs(self.root / 'two')
        context = _Context(self.root)
        context.files = list(reversed(context.files)) * 2
        rows, sources = _run(context)
        self.assertEqual(len(rows), 2 * len(initial))
        context.files.reverse()
        self.assertEqual(_run(context), (rows, sources))
        copy = self.main.with_name('com.life360.safetymap copied.log')
        copy.write_bytes(self.main.read_bytes())
        rows, _ = _run(_Context(self.root))
        self.assertEqual(len(rows), 26)

    def test_physical_alias_is_read_once(self):
        context = _Context(self.root)
        original, _ = _run(context)
        alias = self.root / 'alias'
        try:
            alias.symlink_to(self.main.parent, target_is_directory=True)
        except OSError:
            self.skipTest('Creating a symlink is unavailable on this platform')
        context.files += [str(alias / self.main.name), str(alias / self.sidecar.name)]
        rows, _ = _run(context)
        self.assertEqual(len(rows), len(original))

    def test_bad_utf8_and_file_read_failure_are_visible_and_good_files_survive(self):
        bad = self.main.with_name('com.life360.safetymap invalid.log')
        bad.write_bytes(b'2026-01-15T08:00:00.000+0000 Life360[1:2] I | [DriverBehavior] - '
                        b'Collision future diagnostic: \xff\n')
        context = _Context(self.root)
        missing = self.main.with_name('com.life360.safetymap missing.log')
        context.files.append(str(missing))
        with patch.object(diagnostics, 'logfunc') as log:
            rows, _ = _run(context)
        self.assertEqual(len(rows), 10)
        self.assertTrue(any('\ufffd' in row['Raw Log Record'] for row in rows))
        messages = [call.args[0] for call in log.call_args_list]
        self.assertTrue(any('decode failed' in message for message in messages))
        self.assertTrue(any('missing.log' in message and 'read failed' in message for message in messages))

    def test_input_bytes_and_relative_source_paths_are_preserved(self):
        before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in (self.main, self.sidecar)}
        rows, sources = _run(_Context(self.root))
        self.assertEqual(before, {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in before})
        self.assertTrue(all(not Path(row['Source File']).is_absolute() for row in rows))
        self.assertNotIn(str(self.root), sources)


if __name__ == '__main__':
    unittest.main()
