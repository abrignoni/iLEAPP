"""The test-case harness turns datetimes into the same values on every host timezone.

test_module.convert_to_unix_time used datetime.timestamp(), which reads a naive datetime as
the host's local time. A module returning naive UTC datetimes, as a decoded NSDate is,
therefore recorded and compared a different snapshot on every host timezone, and
twitterX.twitterDirectMessages had to be excluded from the comparison for it. A date has no
timestamp() and stopped the run. Each subprocess here runs the serialiser under one TZ.
"""
import json
import os
import pathlib
import subprocess
import sys
import unittest

SCRIPTS = pathlib.Path(__file__).resolve().parent
PROBE = """
import json, sys
from datetime import date, datetime, timezone
sys.path.insert(0, sys.argv[1])
import test_module
print(json.dumps([
    test_module.convert_to_unix_time(datetime(2020, 1, 6, 10, 40)),
    test_module.convert_to_unix_time(datetime(2020, 1, 6, 10, 40, tzinfo=timezone.utc)),
    test_module.convert_to_unix_time(date(2020, 1, 6)),
    test_module.convert_to_unix_time('as stored'),
]))
"""


def serialised(tz):
    env = dict(os.environ, TZ=tz)
    out = subprocess.run([sys.executable, '-c', PROBE, str(SCRIPTS)], env=env, check=True,
                         capture_output=True, text=True, cwd=SCRIPTS.parents[2])
    return json.loads(out.stdout.strip().splitlines()[-1])


class HarnessDatetimeSerializationTest(unittest.TestCase):

    def test_values_do_not_depend_on_the_host_timezone(self):
        expected = [1578307200, 1578307200, '2020-01-06', 'as stored']
        for tz in ('UTC', 'America/New_York', 'Asia/Tokyo'):
            self.assertEqual(serialised(tz), expected, tz)


if __name__ == '__main__':
    unittest.main()
