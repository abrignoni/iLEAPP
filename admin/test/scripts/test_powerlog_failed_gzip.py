"""Damaged telemetry archives must not poison good sources or be retried."""
import gzip
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import powerlog  # pylint: disable=wrong-import-position


class FailedGzipTests(unittest.TestCase):
    """A bad source must not affect subsequent good sources."""
    def test_truncated_archive_is_logged_once_and_partial_copy_removed(self):
        """Discard incomplete output and cache the failure for this session."""
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            output = root / 'output'
            output.mkdir()
            bad = root / 'bad.PLSQL.gz'
            good = root / 'good.PLSQL.gz'
            payload = b'SQLite format 3\x00' + b'synthetic' * 1000
            bad.write_bytes(gzip.compress(payload)[:-6])
            good.write_bytes(gzip.compress(payload))
            with mock.patch.object(powerlog, '_GZ_CACHE', {}), \
                 mock.patch.object(powerlog, '_session_temp_dir', return_value=str(output)), \
                 mock.patch.object(powerlog, 'logfunc') as log:
                for _ in range(17):
                    self.assertIsNone(powerlog._materialize_gz(str(bad)))  # pylint: disable=protected-access
                self.assertEqual(log.call_count, 1)
                self.assertEqual(list(output.iterdir()), [])
                materialized = powerlog._materialize_gz(str(good))  # pylint: disable=protected-access
                self.assertEqual(pathlib.Path(materialized).read_bytes(), payload)
                self.assertEqual(
                    powerlog._materialize_gz(str(good)),  # pylint: disable=protected-access
                    materialized)
                self.assertEqual(len(list(output.iterdir())), 1)


if __name__ == '__main__':
    unittest.main()
