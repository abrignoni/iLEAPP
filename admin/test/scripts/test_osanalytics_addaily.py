"""OS Analytics addaily network usage on a synthetic plist (values invented for the test)."""
import datetime
import pathlib
import plistlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import osanalyticsAdDaily as parser  # noqa: E402

NAME = 'private/var/mobile/Library/Preferences/com.apple.osanalytics.addaily.plist'


class OsanalyticsAdDailyTest(unittest.TestCase):
    def test_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            good = pathlib.Path(directory) / 'a' / NAME
            good.parent.mkdir(parents=True)
            when = datetime.datetime(2024, 1, 2, 3, 4, 5)
            good.write_bytes(plistlib.dumps({'netUsageBaseline': {
                'com.example.app': [when, 10.0, 2.0, 30.0, 4.5], 'shortproc': [when, 1]}}))
            broken = pathlib.Path(directory) / 'b' / NAME
            broken.parent.mkdir(parents=True)
            broken.write_bytes(b'not a plist')
            paths = [str(good), str(broken)]
            headers, rows, source = parser.osanalytics_addaily_net_usage.__wrapped__(
                SimpleNamespace(get_files_found=lambda: paths))
        self.assertEqual(len(headers), 6)
        self.assertEqual(len(rows), 2)
        first = rows[0]
        self.assertEqual(first[0], when.replace(tzinfo=datetime.timezone.utc))
        self.assertEqual(first[1:], ('com.example.app', 10, 2, 30, 4.5))
        self.assertIsInstance(first[2], int)
        self.assertEqual(rows[1][1:], ('shortproc', 1, '', '', ''))
        self.assertEqual(len(source.splitlines()), 2)


if __name__ == '__main__':
    unittest.main()
