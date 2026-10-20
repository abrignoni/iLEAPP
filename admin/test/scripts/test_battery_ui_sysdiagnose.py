"""batteryUISysdiagnose: sysdiagnose logs/BatteryUIPlist property lists, SYNTHETIC input only."""
import importlib.util
import plistlib
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import batteryUISysdiagnose as module

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('synthetic_battery_ui', HERE / 'synthetic_battery_ui.py')
SYNTH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNTH)

PREFIX = 'PLBatteryUIQueryRange'


def _context(files):
    return SimpleNamespace(get_files_found=lambda: [str(path) for path in files],
                           get_relative_path=lambda value: Path(value.split(' >> ')[0]).name)


def _run(function, files):
    return function.__wrapped__(_context(files))


def _write_tree(folder, files):
    base = Path(folder) / 'sysdiagnose_SYNTHETIC_iPhone-OS_iPhone_00A000' / 'logs' / 'BatteryUIPlist'
    out = []
    for name, data in files.items():
        path = base / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        out.append(path)
    return out


def independent_counts(files):
    """(buckets, app entries) counted straight from the property lists."""
    buckets = apps = 0
    for data in files.values():
        breakdown = plistlib.loads(data)['Breakdown']
        for key, value in breakdown.items():
            if not key.startswith(PREFIX):
                continue
            for bucket in value if isinstance(value, list) else [value]:
                buckets += 1
                apps += len([a for a in bucket['PLBatteryUIAppArrayKey'] if isinstance(a, dict)])
    return buckets, apps


def utc(value):
    return datetime.fromtimestamp(value, tz=timezone.utc)


class BatteryUISysdiagnoseTest(unittest.TestCase):
    def test_row_counts_match_an_independent_count_in_both_shapes(self):
        for variant in ('hourly', 'stretched'):
            files = SYNTH.build_files(variant)
            expected_buckets, expected_apps = independent_counts(files)
            with tempfile.TemporaryDirectory() as folder:
                paths = _write_tree(folder, files)
                a_headers, apps, _ = _run(module.batteryUISysdiagnoseApps, paths)
                b_headers, buckets, _ = _run(module.batteryUISysdiagnoseBuckets, paths)
                s_headers, snapshots, _ = _run(module.batteryUISysdiagnoseSnapshots, paths)
            self.assertEqual((len(buckets), len(apps)), (expected_buckets, expected_apps), variant)
            self.assertEqual(len(snapshots), len(files))
            for headers, rows in ((a_headers, apps), (b_headers, buckets), (s_headers, snapshots)):
                self.assertTrue(rows)
                self.assertTrue(all(len(row) == len(headers) for row in rows))

    def test_bucket_times_are_utc_datetimes_and_seconds_are_end_minus_start(self):
        with tempfile.TemporaryDirectory() as folder:
            headers, rows, _ = _run(module.batteryUISysdiagnoseApps, _write_tree(folder, SYNTH.build_files('hourly', False)))
        self.assertEqual(headers[0], ('Bucket Start (UTC)', 'datetime'))
        self.assertEqual(headers[1], ('Bucket End (UTC)', 'datetime'))
        self.assertTrue(all(row[0].tzinfo is not None and row[1].tzinfo is not None for row in rows))
        self.assertTrue(all((row[1] - row[0]).total_seconds() == row[2] for row in rows))
        hourly = {row[2] for row in rows if row[3] == 'DayTapKey'}
        self.assertEqual(hourly, {3600.0})
        self.assertEqual({row[2] for row in rows if row[3] == 'WeekKey'}, {864000.0})

    def test_the_stretched_shape_keeps_the_stored_bucket_width(self):
        with tempfile.TemporaryDirectory() as folder:
            _, rows, _ = _run(module.batteryUISysdiagnoseApps, _write_tree(folder, SYNTH.build_files('stretched', False)))
        self.assertEqual({row[2] for row in rows if row[3] == 'DayTapKey'}, {86400.0})
        self.assertEqual({row[2] for row in rows if row[3] == 'WeekKey'}, {86400.0})

    def test_runtime_columns_are_the_stored_values_and_stay_within_a_tap_bucket(self):
        with tempfile.TemporaryDirectory() as folder:
            headers, rows, _ = _run(module.batteryUISysdiagnoseApps, _write_tree(folder, SYNTH.build_files('hourly', False)))
        fg, bg = headers.index('Foreground Runtime (s)'), headers.index('Background Runtime (s)')
        for row in rows:
            if row[3] in ('DayTapKey', 'WeekTapKey'):
                self.assertLessEqual(row[fg], row[2])
                self.assertLessEqual(row[bg], row[2])
        beta = next(r for r in rows if r[3] == 'DayKey' and r[5] == 'com.example.beta')
        self.assertEqual(beta[fg], round(86400.0 * 0.05 * 2 / 4, 3))
        self.assertEqual(beta[headers.index('Qualifiers (as stored)')], '2, 7')

    def test_missing_keys_stay_blank_and_components_are_listed(self):
        with tempfile.TemporaryDirectory() as folder:
            headers, rows, _ = _run(module.batteryUISysdiagnoseApps, _write_tree(folder, SYNTH.build_files('hourly', False)))
        flash = next(r for r in rows if r[5] == 'Flashlight')
        for name in ('Foreground Plugged-In Runtime (as stored)', 'Background Plugged-In Runtime (as stored)',
                     'Call Off-Screen Time (as stored)'):
            self.assertIsNone(flash[headers.index(name)])
        self.assertEqual(flash[headers.index('App Type (as stored)')], 1)
        gamma = next(r for r in rows if r[5] == 'com.example.gamma')
        self.assertEqual(gamma[headers.index('Energy Components (as stored)')],
                         'SynthCPU=12.75; SynthDRAM=4.5; SynthWidgetCounts={"a": 1, "b": 2}')

    def test_bucket_totals_equal_the_sum_of_the_app_values_and_empty_buckets_are_listed(self):
        with tempfile.TemporaryDirectory() as folder:
            paths = _write_tree(folder, SYNTH.build_files('hourly', False))
            _, apps, _ = _run(module.batteryUISysdiagnoseApps, paths)
            _, buckets, _ = _run(module.batteryUISysdiagnoseBuckets, paths)
        for bucket in buckets:
            members = [a for a in apps if a[:5] == bucket[:5]]
            self.assertEqual(bucket[12], len(members))
            self.assertAlmostEqual(bucket[5], sum(a[8] for a in members), places=3)
        empty = [b for b in buckets if b[12] == 0]
        self.assertTrue(empty)
        self.assertEqual({b[11] for b in empty}, {1})
        self.assertEqual({b[11] for b in buckets if b[12]}, {0})

    def test_upgrade_file_gives_the_builds_from_its_name_and_a_marker_row(self):
        with tempfile.TemporaryDirectory() as folder:
            paths = _write_tree(folder, SYNTH.build_files('stretched'))
            _, rows, source = _run(module.batteryUISysdiagnoseSnapshots, paths)
            _, buckets, _ = _run(module.batteryUISysdiagnoseBuckets, paths)
        self.assertEqual(len(rows), 2)
        by_kind = {row[1]: row for row in rows}
        upgrade, main = by_kind['Upgrade file'], by_kind['Main file']
        self.assertEqual((upgrade[2], upgrade[3]), ('00A001', '00B002'))
        self.assertEqual((main[2], main[3]), ('', ''))
        self.assertEqual(main[0], utc(SYNTH.QUERY_TIME))
        self.assertEqual(main[4], utc(SYNTH.QUERY_TIME - 33000.5))
        self.assertEqual(main[5:10], (77, 601, 87, 1036800.0, 1.0))
        self.assertEqual(main[10], 'DayKey, DayTapKey, WeekKey, WeekTapKey')
        self.assertIn('BatteryUIUpgrade_00A001_00B002.plist', source)
        upgrade_buckets = [b for b in buckets if b[13] == 'Upgrade file']
        self.assertTrue(upgrade_buckets)
        self.assertTrue(all(b[10] == 29285029.5 for b in upgrade_buckets if b[3] in ('DayKey', 'DayTapKey', 'WeekKey')))

    def test_damaged_values_become_blanks_and_do_not_stop_the_file(self):
        files = {'BatteryUISysdiagnose.plist': plistlib.dumps(SYNTH.edge_main())}
        with tempfile.TemporaryDirectory() as folder:
            paths = _write_tree(folder, files)
            headers, apps, _ = _run(module.batteryUISysdiagnoseApps, paths)
            _, buckets, _ = _run(module.batteryUISysdiagnoseBuckets, paths)
        expected_buckets, expected_apps = independent_counts(files)
        self.assertEqual((len(buckets), len(apps)), (expected_buckets, expected_apps))
        alpha = next(r for r in apps if r[3] == 'DayKey' and r[5] == 'com.example.alpha')
        self.assertIsNone(alpha[headers.index('Foreground Runtime (s)')])
        beta = next(r for r in apps if r[3] == 'DayKey' and r[5] == 'com.example.beta')
        self.assertIsNone(beta[headers.index('Energy Used (as stored)')])
        first_tap = next(b for b in buckets if b[3] == 'DayTapKey' and b[4] == 1)
        self.assertEqual((first_tap[0], first_tap[2]), (None, None))

    def test_unreadable_file_gives_a_snapshot_row_with_a_note_and_no_other_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            paths = _write_tree(folder, {'BatteryUISysdiagnose.plist': b'not a property list'})
            _, apps, _ = _run(module.batteryUISysdiagnoseApps, paths)
            _, buckets, _ = _run(module.batteryUISysdiagnoseBuckets, paths)
            headers, snapshots, _ = _run(module.batteryUISysdiagnoseSnapshots, paths)
        self.assertEqual((apps, buckets), ([], []))
        self.assertEqual(len(snapshots), 1)
        self.assertEqual(snapshots[0][headers.index('Notes')], 'The file could not be read as a property list.')

    def test_sysdiagnose_archive_and_extracted_folder_give_the_same_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            archive = Path(folder) / 'sysdiagnose_2026.09.29_19-00-00-0400_iPhone-OS_iPhone_24A437.tar.gz'
            SYNTH.write_archive(archive, 'stretched')
            paths = _write_tree(Path(folder) / 'tree', SYNTH.build_files('stretched'))
            for function in (module.batteryUISysdiagnoseApps, module.batteryUISysdiagnoseBuckets,
                             module.batteryUISysdiagnoseSnapshots):
                _, from_archive, source = _run(function, [archive])
                _, from_folder, _ = _run(function, paths)
                self.assertEqual(sorted(repr(r[:-1]) for r in from_archive), sorted(repr(r[:-1]) for r in from_folder))
                self.assertIn(' >> sysdiagnose_SYNTHETIC_iPhone-OS_iPhone_24A437/logs/BatteryUIPlist/', source)
                self.assertNotIn('other/', source)

    def test_empty_input_gives_no_rows(self):
        for function in (module.batteryUISysdiagnoseApps, module.batteryUISysdiagnoseBuckets,
                         module.batteryUISysdiagnoseSnapshots):
            headers, rows, source = _run(function, [])
            self.assertEqual((rows, source), ([], ''))
            self.assertTrue(headers)


if __name__ == '__main__':
    unittest.main()
