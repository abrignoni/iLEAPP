"""The test harness hands an artifact its files in the order a real zip run does.

A real run extends files_found pattern by pattern, in the artifact's declared
order, so an artifact that takes the first match (get_file_path) reads the file
of its first pattern. The harness used to pass os.walk order, which depends on
the file system: on the GitHub runner image of 2026-10-18 it put an empty
Documents/GroupMe.sqlite before the populated one under Library/Application
Support, and four GroupMe cases returned 0 rows. These tests feed the files in
the order that broke and check the harness puts them back in pattern order.
"""
import os
import sys
import unittest

sys.path.append(os.path.dirname(__file__))

import test_module as tm  # noqa: E402  pylint: disable=wrong-import-position
from scripts.search_files import FileInfo  # noqa: E402  pylint: disable=wrong-import-position

APP = 'fs/private/var/mobile/Containers/Data/Application/UUID'
DOCS_DB = f'{APP}/Documents/GroupMe.sqlite'
SUPPORT_DB = f'{APP}/Library/Application Support/GroupMe.sqlite'
PATHS = (
    '*/mobile/Containers/Data/Application/*/Library/Application Support/GroupMe.sqlite*',
    '*/mobile/Containers/Data/Application/*/Documents/GroupMe.sqlite*',
)


def staged(member):
    return os.path.join('temp', member)


class FilesFoundOrderTest(unittest.TestCase):
    def setUp(self):
        # file_infos is filled in archive order; this archive lists Documents first.
        self.file_infos = {staged(m): FileInfo(m, None, None) for m in (
            DOCS_DB, DOCS_DB + '-wal', SUPPORT_DB, SUPPORT_DB + '-wal', f'{APP}/other.plist')}

    def test_first_pattern_wins_whatever_the_walk_order(self):
        walk = list(self.file_infos)
        for staged_files in (walk, list(reversed(walk))):
            ordered = tm.order_like_seeker(staged_files, self.file_infos, PATHS)
            self.assertEqual(ordered[:2], [staged(SUPPORT_DB), staged(SUPPORT_DB + '-wal')])
            self.assertEqual(ordered[2:4], [staged(DOCS_DB), staged(DOCS_DB + '-wal')])

    def test_unmatched_files_follow_sorted_and_none_are_lost(self):
        extra = os.path.join('temp', 'mock_reports', 'x')
        staged_files = [extra] + list(reversed(list(self.file_infos)))
        ordered = tm.order_like_seeker(staged_files, self.file_infos, PATHS)
        self.assertEqual(sorted(ordered), sorted(staged_files))
        self.assertEqual(ordered[4:], sorted([staged(f'{APP}/other.plist'), extra]))

    def test_a_single_string_pattern_and_no_pattern(self):
        ordered = tm.order_like_seeker(list(self.file_infos), self.file_infos, PATHS[1])
        self.assertEqual(ordered[0], staged(DOCS_DB))
        self.assertEqual(tm.order_like_seeker(['b', 'a'], {}, None), ['a', 'b'])


if __name__ == '__main__':
    unittest.main()
