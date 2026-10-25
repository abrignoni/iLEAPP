"""The Waze user.db search never hands a -wal or -shm sidecar to the SQLite readers."""
# pylint: disable=protected-access
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import waze


def _context(result):
    seeker = SimpleNamespace(search=lambda pattern, return_on_first_hit=False: result)
    return SimpleNamespace(get_seeker=lambda: seeker)


class UserDbSearchTest(unittest.TestCase):
    def test_main_file_is_returned_as_found(self):
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / 'user.db')
            Path(path).write_bytes(b'x')
            self.assertEqual(waze._search_user_db(_context(path), 'app'), path)

    def test_sidecar_hit_resolves_to_the_main_file_when_present(self):
        with tempfile.TemporaryDirectory() as folder:
            main = Path(folder) / 'user.db'
            main.write_bytes(b'x')
            for suffix in ('-shm', '-wal'):
                sidecar = str(main) + suffix
                Path(sidecar).write_bytes(b'')
                self.assertEqual(waze._search_user_db(_context(sidecar), 'app'), str(main))

    def test_sidecars_alone_give_nothing(self):
        with tempfile.TemporaryDirectory() as folder:
            sidecar = Path(folder) / 'user.db-shm'
            sidecar.write_bytes(b'x')
            self.assertIsNone(waze._search_user_db(_context(str(sidecar)), 'app'))

    def test_no_hit_stays_empty(self):
        self.assertFalse(waze._search_user_db(_context(None), 'app'))
        self.assertFalse(waze._search_user_db(_context(''), 'app'))


if __name__ == '__main__':
    unittest.main()
