"""Pairing rules of the logarchive app interaction deletes artifact. All log lines are invented."""
# pylint: disable=protected-access
import pathlib
import re
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts import logarchive  # pylint: disable=wrong-import-position

BUNDLE = 'com.example.chat'
OTHER = 'com.example.other'


def record(when, row, process, message):
    return (when, row, f'/private/var/containers/Bundle/{process}', 100, 'subsystem', 'category', message, '')


def request(when, row, process='Chat', prefix='(null)', identifiers=1):
    return record(when, row, process, f'({prefix}) deleteInteractionsWithGroupIdentifiers, '
                                      f'protectionClass:(null), identifiers number:{identifiers}')


def daemon(when, row, bundle=BUNDLE):
    return record(when, row, 'searchd', f'({bundle}) deleteInteractionsWithGroupIdentifiers, '
                                        'protectionClass:NSFileProtectionCompleteUntilFirstUserAuthentication, '
                                        'identifiers number:1')


def count(when, row, number, bundle=BUNDLE):
    return record(when, row, 'coreduetd', f'Deleted {number} interactions with reason '
                                          f'deleteInteractionsWithBundleId:{bundle} domainIdentifiers:(redacted)')


class PairingTest(unittest.TestCase):
    def test_bundle_from_searchd_and_count_from_coreduetd(self):
        rows = logarchive._interaction_delete_rows([request(10.0, 1), daemon(10.01, 2), count(10.02, 3, 4)])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][2:7], ('Chat', 100, BUNDLE, 1, 4))

    def test_bundle_named_on_the_request(self):
        rows = logarchive._interaction_delete_rows(
            [request(10.0, 1, 'imagent', BUNDLE), daemon(10.01, 2), count(10.02, 3, 2)])
        self.assertEqual(rows[0][4:7], (BUNDLE, 1, 2))

    def test_redacted_bundle_stays_blank(self):
        rows = logarchive._interaction_delete_rows(
            [request(10.0, 1), daemon(10.01, 2, '<private>'), count(10.02, 3, 4)])
        self.assertEqual(rows[0][4], '')
        self.assertIsNone(rows[0][6])

    def test_count_for_another_bundle_is_not_used(self):
        rows = logarchive._interaction_delete_rows(
            [request(10.0, 1), daemon(10.01, 2), count(10.02, 3, 9, OTHER)])
        self.assertEqual(rows[0][4], BUNDLE)
        self.assertIsNone(rows[0][6])

    def test_count_outside_the_window_is_not_used(self):
        rows = logarchive._interaction_delete_rows([request(10.0, 1), daemon(10.01, 2), count(11.5, 3, 4)])
        self.assertIsNone(rows[0][6])

    def test_two_requests_do_not_share_a_count(self):
        rows = logarchive._interaction_delete_rows([
            request(10.0, 1), daemon(10.01, 2), count(10.02, 3, 4),
            request(10.1, 4), daemon(10.11, 5), count(10.12, 6, 7)])
        self.assertEqual([row[6] for row in rows], [4, 7])

    def test_bundle_stays_blank_when_two_processes_request_together(self):
        rows = logarchive._interaction_delete_rows([
            request(10.0, 1, 'Chat'), request(10.2, 2, 'Other'),
            daemon(10.01, 3), daemon(10.21, 4, OTHER), count(10.02, 5, 4), count(10.22, 6, 7, OTHER)])
        self.assertEqual([row[4] for row in rows], ['', ''])
        self.assertEqual([row[6] for row in rows], [None, None])

    def test_daemon_lines_alone_make_no_row(self):
        rows = logarchive._interaction_delete_rows([daemon(10.01, 2), count(10.02, 3, 4)])
        self.assertEqual(rows, [])

    def test_where_patterns_are_collected(self):
        source = (REPO_ROOT / 'scripts' / 'artifacts' / 'logarchive.py').read_text(encoding='utf-8')
        start = source.index('def logarchive_artifacts(context):')
        end = source.index('def logarchive_time_change(context):')
        collected = source[start:end]
        patterns = re.findall(r"LIKE '([^']*)'", logarchive.INTERACTION_DELETE_WHERE)
        self.assertEqual(len(patterns), 2)
        for pattern in patterns:
            self.assertIn(f"LIKE '{pattern}'", collected)


if __name__ == '__main__':
    unittest.main()
