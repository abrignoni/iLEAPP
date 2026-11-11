"""Synthetic tests for the Google Measurement module; the fixture is built by synthetic_google_measurement.py."""
import datetime
import fnmatch
import inspect
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import synthetic_google_measurement as fx  # noqa: E402  pylint: disable=wrong-import-position
from scripts.artifacts import googleMeasurement as module  # noqa: E402  pylint: disable=wrong-import-position

UTC = datetime.timezone.utc
NAME = 'google_measurement_store'


class Context:
    def __init__(self, root):
        self.root = Path(root).resolve()
        patterns = module.__artifacts_v2__[NAME]['paths']
        self.files = [str(p) for p in self.root.rglob('*') if p.is_file()
                      and any(fnmatch.fnmatchcase('root/' + p.relative_to(self.root).as_posix(), pat)
                              for pat in patterns)]

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return Path(path).relative_to(self.root).as_posix()


def run(root):
    headers, rows, source = inspect.unwrap(module.google_measurement_store)(Context(root))
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    assert all(len(row) == len(names) for row in rows)
    return [dict(zip(names, row)) for row in rows], source


def build(case):
    tmp = tempfile.TemporaryDirectory()
    fx.CASES[case](tmp.name)
    return tmp


class GoogleMeasurementTests(unittest.TestCase):
    def test_each_app_is_named_and_rows_stay_with_their_app(self):
        with build('synthetic') as root:
            rows, _ = run(root)
        apps = {r['App Bundle ID'] for r in rows}
        self.assertEqual(apps, {'com.example.alpha', 'com.example.beta', ''})
        alpha = [r for r in rows if r['App Bundle ID'] == 'com.example.alpha']
        beta = [r for r in rows if r['App Bundle ID'] == 'com.example.beta']
        self.assertEqual({r['Record Type'] for r in alpha}, {'Event', 'User Property', 'Measurement plist'})
        # the older layout has no user_attributes table
        self.assertEqual({r['Record Type'] for r in beta}, {'Event', 'Measurement plist'})
        # the first_open time of each app is its own
        first = {a: next(r['Time'] for r in rows if r['App Bundle ID'] == a and r['Name'] == '_f')
                 for a in ('com.example.alpha', 'com.example.beta')}
        self.assertEqual(first['com.example.alpha'], fx.FIRST_OPEN)
        self.assertEqual(first['com.example.beta'], fx.FIRST_OPEN + datetime.timedelta(days=10))

    def test_container_without_identifier_has_a_blank_app_and_one_without_a_store_adds_nothing(self):
        with build('synthetic') as root:
            rows, source = run(root)
        blank = [r for r in rows if r['App Bundle ID'] == '']
        self.assertTrue(blank)
        self.assertEqual({r['Record Type'] for r in blank}, {'Event', 'User Property'})
        self.assertNotIn('com.example.gamma', {r['App Bundle ID'] for r in rows})
        self.assertNotIn(fx.NO_STORE, source)

    def test_source_path_lists_every_file_read_once_per_line(self):
        with build('synthetic') as root:
            _, source = run(root)
        lines = source.split('\n')
        self.assertEqual(len(lines), len(set(lines)))
        self.assertEqual(len(lines), 5)   # alpha db and plist, beta db and plist, unidentified db
        for container in (fx.ALPHA, fx.BETA, fx.UNIDENTIFIED):
            self.assertTrue(any(container in line for line in lines))

    def test_times_are_utc_and_measurement_milliseconds_are_read_as_milliseconds(self):
        with build('synthetic_minimal') as root:
            rows, _ = run(root)
        events = {r['Name']: r for r in rows if r['Record Type'] == 'Event'}
        self.assertEqual(events['_f']['Time'], fx.FIRST_OPEN)
        self.assertEqual(events['_f']['Time'].tzinfo, UTC)
        self.assertEqual(events['_s']['Count'], 3)
        with build('synthetic') as root:
            rows, _ = run(root)
        plist = {r['Name']: r for r in rows
                 if r['App Bundle ID'] == 'com.example.alpha' and r['Record Type'] == 'Measurement plist'}
        self.assertEqual(plist['first_open_timestamp_ms']['Time'], fx.FIRST_OPEN)
        self.assertEqual(plist['last_engagement_end']['Time'], events['_e']['Time'] + datetime.timedelta(seconds=60))
        self.assertEqual(plist['last_failed_upload']['Time'], '')
        self.assertEqual(plist['last_failed_upload']['Value'], 0.0)

    def test_epoch_reads_large_values_as_milliseconds(self):
        self.assertEqual(module._epoch(1772460000.0), fx.FIRST_OPEN)  # pylint: disable=protected-access
        self.assertEqual(module._epoch(1772460000000), fx.FIRST_OPEN)  # pylint: disable=protected-access
        self.assertEqual(module._epoch(0), '')  # pylint: disable=protected-access
        self.assertEqual(module._epoch('text'), '')  # pylint: disable=protected-access

    def test_minimal_container_has_events_only_and_does_not_fail(self):
        with build('synthetic_minimal') as root:
            rows, _ = run(root)
        self.assertEqual({r['Record Type'] for r in rows}, {'Event'})
        self.assertEqual({r['App Bundle ID'] for r in rows}, {'com.example.alpha'})

    def test_backup_layout_names_the_app_from_the_folder(self):
        with build('synthetic_backup') as root:
            rows, _ = run(root)
        self.assertEqual({r['App Bundle ID'] for r in rows}, {'com.example.alpha'})
        self.assertEqual({r['Record Type'] for r in rows}, {'Event', 'User Property', 'Measurement plist'})

    def test_unreadable_files_are_skipped_without_raising(self):
        with build('synthetic') as root:
            for path in Path(root).rglob('*'):
                if path.is_file() and path.name in ('google-app-measurement.sql', 'com.google.gmp.measurement.plist'):
                    path.write_bytes(b'not a database or a plist')
            rows, _ = run(root)
        self.assertEqual(rows, [])


if __name__ == '__main__':
    unittest.main()
