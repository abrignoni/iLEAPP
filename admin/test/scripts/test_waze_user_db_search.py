"""The Waze user.db search never hands a -wal or -shm sidecar to the SQLite readers."""
# pylint: disable=protected-access
import unittest
from types import SimpleNamespace

from scripts.artifacts import waze


def _context(result):
    calls = []

    def search(pattern, return_on_first_hit=False):
        calls.append(return_on_first_hit)
        return result
    seeker = SimpleNamespace(search=search)
    return SimpleNamespace(get_seeker=lambda: seeker), calls


class UserDbSearchTest(unittest.TestCase):
    def test_main_file_is_returned_whatever_the_order(self):
        for order in (['/x/user.db', '/x/user.db-wal', '/x/user.db-shm'],
                      ['/x/user.db-shm', '/x/user.db-wal', '/x/user.db']):
            context, _ = _context(order)
            self.assertEqual(waze._search_user_db(context, 'app'), '/x/user.db')

    def test_every_match_is_requested_so_the_wal_is_staged(self):
        context, calls = _context(['/x/user.db-shm', '/x/user.db'])
        waze._search_user_db(context, 'app')
        self.assertEqual(calls, [False])

    def test_sidecars_alone_give_nothing(self):
        context, _ = _context(['/x/user.db-shm', '/x/user.db-wal'])
        self.assertIsNone(waze._search_user_db(context, 'app'))

    def test_no_hit_stays_empty(self):
        for result in (None, []):
            context, _ = _context(result)
            self.assertIsNone(waze._search_user_db(context, 'app'))


if __name__ == '__main__':
    unittest.main()
