"""The newer Waze GPS quality layout's count lines are read by the right expression.

The duplicate count was looked for as dup_sample_count only; the layout the cited
research shows writes duplicate_sample_count. Both are read. The plain sample
count no longer matches inside the bad or duplicate count lines.
"""
import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts import waze  # pylint: disable=wrong-import-position


def read(expression, line):
    match = expression.search(line)
    return int(match.group(1)) if match else None


class GpsQualityCounts(unittest.TestCase):

    def test_each_count_line_feeds_only_its_own_column(self):
        cases = {
            '  sample_count: 7': (7, None, None),
            '  bad_sample_count: 2': (None, 2, None),
            '  dup_sample_count: 3': (None, None, 3),
            '  duplicate_sample_count: 4': (None, None, 4),
        }
        for line, expected in cases.items():
            with self.subTest(line=line):
                self.assertEqual(tuple(read(e, line) for e in (
                    waze.SWIFT_SAM_CNT_RE, waze.SWIFT_BAD_CNT_RE, waze.SWIFT_DUP_CNT_RE)), expected)


if __name__ == '__main__':
    unittest.main()
