"""Tests for scripts/sqlite_wal.py, the committed-state reader for write-ahead logs.

Every fixture is written here with known content: the rows inserted, deleted and
changed are known, so what the helper returns can be checked against them exactly.
The independent reading is SQLite's own: the helper's newest state must equal what
SQLite reads from an untouched copy of the full log, whatever shape the log is in.
"""
import hashlib
import os
import shutil
import sqlite3
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.sqlite_wal import (EARLIER_VERSION, KIND_COMMITTED, KIND_EARLIER,
                                KIND_UNCOMMITTED, NOT_IN_CURRENT, UNCOMMITTED_CHANGE, WalLog,
                                WalStates, _wal_checksum, rows_not_in_current)

QUERY = 'SELECT id, txt FROM t'


def _hashes(folder):
    return {name: hashlib.sha256(Path(folder, name).read_bytes()).hexdigest()
            for name in sorted(os.listdir(folder))}


class WalFixture:
    """A WAL-mode database whose log is captured while the writer is still open.

    Closing the last connection checkpoints the log and deletes it, so the files are
    copied out with the writer open and wal_autocheckpoint off.
    """

    def __init__(self, folder):
        self.folder = folder
        self.live = os.path.join(folder, 'live')
        self.evidence = os.path.join(folder, 'evidence')
        os.makedirs(self.live)
        os.makedirs(self.evidence)
        self.connection = sqlite3.connect(os.path.join(self.live, 't.db'),
                                          isolation_level=None)
        self.connection.execute('PRAGMA journal_mode=WAL')
        self.connection.execute('PRAGMA wal_autocheckpoint=0')

    def execute(self, sql, params=()):
        return self.connection.execute(sql, params)

    def capture(self):
        for name in ('t.db', 't.db-wal'):
            shutil.copyfile(os.path.join(self.live, name), os.path.join(self.evidence, name))
        self.connection.close()
        return os.path.join(self.evidence, 't.db')


def _sqlite_reading(db_path, query=QUERY):
    """What SQLite itself reads from a copy of the database and its full log."""
    work = tempfile.mkdtemp()
    try:
        for suffix in ('', '-wal'):
            if os.path.exists(db_path + suffix):
                shutil.copyfile(db_path + suffix, os.path.join(work, 't.db' + suffix))
        connection = sqlite3.connect(Path(work, 't.db').as_uri() + '?mode=ro', uri=True)
        rows = set(connection.execute(query).fetchall())
        connection.close()
        return rows
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _current_state(db_path, query=QUERY):
    with WalStates(db_path) as wal:
        for state in wal.states():
            return set(state.connection.execute(query).fetchall())
    return None


class SqliteWalTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.fixture = WalFixture(self.tmp)
        self.fixture.execute('CREATE TABLE t (id INTEGER PRIMARY KEY, txt TEXT)')
        self.fixture.execute('PRAGMA wal_checkpoint(TRUNCATE)')

    def tearDown(self):
        try:
            self.fixture.connection.close()
        except sqlite3.Error:
            pass
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _insert_delete(self, payload='row %d'):
        for i in range(1, 41):
            self.fixture.execute('INSERT INTO t VALUES (?, ?)', (i, payload % i))
        for i in range(5, 18):
            self.fixture.execute('DELETE FROM t WHERE id = ?', (i,))

    def test_deleted_rows_are_returned_exactly(self):
        self._insert_delete()
        db_path = self.fixture.capture()
        before = _hashes(self.fixture.evidence)
        columns, rows, wal = rows_not_in_current(db_path, QUERY, key_columns=[0])
        self.assertEqual(columns, ['id', 'txt'])
        self.assertEqual(sorted(row.values[0] for row in rows), list(range(5, 18)))
        self.assertTrue(all(row.status == NOT_IN_CURRENT for row in rows))
        self.assertEqual(len(wal.log.commits), 53)
        self.assertEqual(_hashes(self.fixture.evidence), before)

    def test_rows_spanning_many_pages(self):
        self._insert_delete('row %d ' + 'x' * 900)
        db_path = self.fixture.capture()
        _columns, rows, _wal = rows_not_in_current(db_path, QUERY)
        self.assertEqual(sorted(row.values[0] for row in rows), list(range(5, 18)))
        self.assertTrue(all(row.values[1].startswith(f'row {row.values[0]} ') for row in rows))

    def test_changed_row_is_an_earlier_version(self):
        self.fixture.execute("INSERT INTO t VALUES (1, 'first')")
        self.fixture.execute("UPDATE t SET txt = 'second' WHERE id = 1")
        self.fixture.execute("UPDATE t SET txt = 'third' WHERE id = 1")
        db_path = self.fixture.capture()
        _columns, rows, _wal = rows_not_in_current(db_path, QUERY, key_columns=[0])
        self.assertEqual([(row.values, row.status, row.first_state, row.last_state)
                          for row in rows],
                         [((1, 'first'), EARLIER_VERSION, 1, 1),
                          ((1, 'second'), EARLIER_VERSION, 2, 2)])

    def test_row_seen_across_states_keeps_its_range(self):
        self.fixture.execute("INSERT INTO t VALUES (1, 'kept a while')")
        self.fixture.execute("INSERT INTO t VALUES (2, 'other')")
        self.fixture.execute("INSERT INTO t VALUES (3, 'other')")
        self.fixture.execute('DELETE FROM t WHERE id = 1')
        db_path = self.fixture.capture()
        _columns, rows, _wal = rows_not_in_current(db_path, QUERY)
        self.assertEqual([(row.values, row.first_state, row.last_state) for row in rows],
                         [((1, 'kept a while'), 1, 3)])
        self.assertLess(rows[0].first_frame, rows[0].last_frame)

    def test_newest_state_matches_sqlite_on_the_full_log(self):
        self._insert_delete()
        db_path = self.fixture.capture()
        self.assertEqual(_current_state(db_path), _sqlite_reading(db_path))

    def test_bad_checksum_stops_where_sqlite_stops(self):
        self._insert_delete()
        db_path = self.fixture.capture()
        log = WalLog(db_path + '-wal')
        frame_size = 24 + log.page_size
        damaged = 30
        with open(db_path + '-wal', 'r+b') as handle:
            handle.seek(32 + (damaged - 1) * frame_size + 24 + 200)
            byte = handle.read(1)
            handle.seek(-1, os.SEEK_CUR)
            handle.write(bytes([byte[0] ^ 0xFF]))
        wal = WalStates(db_path)
        self.assertEqual(wal.log.valid_frames, damaged - 1)
        self.assertEqual(wal.log.other_frames, wal.log.total_frames - (damaged - 1))
        self.assertIn('failing their checksum not read', wal.summary())
        self.assertEqual(_current_state(db_path), _sqlite_reading(db_path))

    def test_uncommitted_tail_is_not_read(self):
        self._insert_delete()
        db_path = self.fixture.capture()
        log = WalLog(db_path + '-wal')
        frame_size = 24 + log.page_size
        with open(db_path + '-wal', 'r+b') as handle:
            data = bytearray(handle.read())
        # Re-seal the last frame as a non-commit frame with a valid checksum.
        last = 32 + (log.total_frames - 1) * frame_size
        data[last + 4:last + 8] = b'\x00\x00\x00\x00'
        big_endian = struct.unpack('>I', data[:4])[0] & 1
        state = _wal_checksum(bytes(data[:24]), big_endian)
        for index in range(log.total_frames):
            offset = 32 + index * frame_size
            state = _wal_checksum(bytes(data[offset:offset + 8] + data[offset + 24:offset + frame_size]),
                                  big_endian, state)
            data[offset + 16:offset + 24] = struct.pack('>2I', *state)
        Path(db_path + '-wal').write_bytes(bytes(data))
        wal = WalStates(db_path)
        self.assertEqual(wal.log.uncommitted_frames, 1)
        self.assertEqual(len(wal.log.commits), 52)
        self.assertEqual(_current_state(db_path), _sqlite_reading(db_path))
        self.assertEqual(sorted(row for row, in _current_state(db_path, 'SELECT id FROM t')),
                         [1, 2, 3, 4] + list(range(17, 41)))

    def test_zeroed_header_is_not_read(self):
        self._insert_delete()
        db_path = self.fixture.capture()
        with open(db_path + '-wal', 'r+b') as handle:
            handle.write(b'\x00' * 32)
        columns, rows, wal = rows_not_in_current(db_path, QUERY)
        self.assertEqual((columns, rows), ([], []))
        self.assertIn('not a WAL header', wal.summary())

    def test_no_log_returns_nothing(self):
        self.fixture.execute("INSERT INTO t VALUES (1, 'a')")
        db_path = self.fixture.capture()
        os.unlink(db_path + '-wal')
        columns, rows, wal = rows_not_in_current(db_path, QUERY)
        self.assertEqual((columns, rows), ([], []))
        self.assertIn('no write-ahead log', wal.summary())

    def test_table_created_inside_the_log(self):
        self.fixture.execute("INSERT INTO t VALUES (1, 'a')")
        self.fixture.execute('CREATE TABLE later (id INTEGER PRIMARY KEY, v TEXT)')
        self.fixture.execute("INSERT INTO later VALUES (1, 'gone')")
        self.fixture.execute("INSERT INTO later VALUES (2, 'stays')")
        self.fixture.execute('DELETE FROM later WHERE id = 1')
        db_path = self.fixture.capture()
        _columns, rows, _wal = rows_not_in_current(db_path, 'SELECT id, v FROM later')
        self.assertEqual([row.values for row in rows], [(1, 'gone')])

    def test_checkpointed_log_skips_states_it_cannot_rebuild(self):
        self._insert_delete('row %d ' + 'x' * 900)
        self.fixture.execute('PRAGMA wal_checkpoint(PASSIVE)')
        db_path = self.fixture.capture()
        wal = WalStates(db_path)
        self.assertEqual(wal.checkpointed_frame, wal.log.commits[-1][1])
        self.assertGreater(wal.skipped_mixed, 0)
        self.assertNotIn((0, 0), wal.readable)
        _columns, rows, _wal = rows_not_in_current(db_path, QUERY)
        recovered = {row.values[0] for row in rows}
        self.assertTrue(recovered <= set(range(5, 18)))
        for state_rows in self._every_state(db_path):
            self.assertTrue(state_rows <= {i for i in range(1, 41)})

    def test_checkpointed_single_page_table_is_fully_readable(self):
        self._insert_delete()
        self.fixture.execute('PRAGMA wal_checkpoint(PASSIVE)')
        db_path = self.fixture.capture()
        wal = WalStates(db_path)
        self.assertTrue(wal.checkpointed_frame)
        _columns, rows, _wal = rows_not_in_current(db_path, QUERY)
        self.assertEqual(sorted(row.values[0] for row in rows), list(range(5, 18)))

    def test_state_limit_keeps_the_newest(self):
        self._insert_delete()
        db_path = self.fixture.capture()
        wal = WalStates(db_path, max_states=5)
        self.assertEqual([number for number, _frame in wal.readable], [49, 50, 51, 52, 53])
        self.assertEqual(wal.skipped_limit, 54 - 5)
        _columns, rows, _wal = rows_not_in_current(db_path, QUERY, max_states=5)
        self.assertEqual(sorted(row.values[0] for row in rows), [14, 15, 16, 17])

    def test_scratch_copies_are_removed_after_an_early_stop(self):
        self._insert_delete()
        db_path = self.fixture.capture()
        with WalStates(db_path) as wal:
            for _state in wal.states():
                work = wal._work  # pylint: disable=protected-access
                break
        self.assertFalse(os.path.exists(work))

    @staticmethod
    def _every_state(db_path):
        with WalStates(db_path) as wal:
            for state in wal.states():
                yield {row[0] for row in state.connection.execute('SELECT id FROM t')}


ALL_KINDS = (KIND_COMMITTED, KIND_EARLIER, KIND_UNCOMMITTED)

# Run in a child process so it can stop without committing: the open transaction's
# spilled pages stay in the log as frames after the last commit.
UNCOMMITTED_WRITER = """
import os, sqlite3, sys
c = sqlite3.connect(sys.argv[1], isolation_level=None)
c.execute('PRAGMA journal_mode=WAL')
c.execute('PRAGMA wal_autocheckpoint=0')
c.execute('CREATE TABLE t (id INTEGER PRIMARY KEY, txt TEXT)')
c.execute('BEGIN')
for i in range(1, 301):
    c.execute('INSERT INTO t VALUES (?, ?)', (i, 'committed %d ' % i + 'y' * 200))
c.execute('COMMIT')
c.execute('PRAGMA cache_size=5')
c.execute('BEGIN')
if sys.argv[2] == 'update':
    c.execute("UPDATE t SET txt = 'pending ' || id || ' ' || substr(txt, 20)")
else:
    for i in range(1000, 1300):
        c.execute('INSERT INTO t VALUES (?, ?)', (i, 'pending %d ' % i + 'x' * 500))
os._exit(0)
"""


class EarlierGenerationTest(unittest.TestCase):
    """The previous log generation's left-over frames, read as earlier states."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.fixture = WalFixture(self.tmp)
        self.fixture.execute('CREATE TABLE t (id INTEGER PRIMARY KEY, txt TEXT)')
        self.fixture.execute('PRAGMA wal_checkpoint(TRUNCATE)')

    def tearDown(self):
        try:
            self.fixture.connection.close()
        except sqlite3.Error:
            pass
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _generation_a(self):
        for i in range(1, 41):
            self.fixture.execute('INSERT INTO t VALUES (?, ?)', (i, 'gen A row %d' % i))
        for i in range(5, 18):
            self.fixture.execute('DELETE FROM t WHERE id = ?', (i,))
        self.fixture.execute('PRAGMA wal_checkpoint(FULL)')

    def _short_generation(self, first, count):
        # A write after a full checkpoint resets the log to frame 1 with salt-1 + 1.
        for i in range(first, first + count):
            self.fixture.execute('INSERT INTO t VALUES (?, ?)', (i, 'later row %d' % i))

    def test_rows_deleted_in_the_previous_generation(self):
        self._generation_a()
        self._short_generation(200, 3)
        db_path = self.fixture.capture()
        before = _hashes(self.fixture.evidence)
        header = struct.unpack('>8I', Path(db_path + '-wal').read_bytes()[:32])
        log = WalLog(db_path + '-wal')
        self.assertEqual(log.earlier.salts[0], (header[4] - 1) & 0xFFFFFFFF)
        self.assertEqual(log.older_frames, 0)
        _columns, rows, wal = rows_not_in_current(db_path, QUERY, key_columns=[0],
                                                  include=ALL_KINDS)
        self.assertEqual(sorted(row.values[0] for row in rows), list(range(5, 18)))
        self.assertTrue(all(row.first_state is None and row.earlier_generation
                            and row.status == NOT_IN_CURRENT for row in rows))
        self.assertIn('frames left by the previous generation', wal.summary())
        self.assertEqual(_hashes(self.fixture.evidence), before)

    def test_default_include_does_not_read_the_previous_generation(self):
        self._generation_a()
        self._short_generation(200, 3)
        db_path = self.fixture.capture()
        _columns, rows, wal = rows_not_in_current(db_path, QUERY)
        self.assertEqual(rows, [])
        self.assertEqual(wal.earlier_readable, [])

    def test_only_the_previous_generation_is_read_after_two_resets(self):
        self._generation_a()
        self._short_generation(100, 20)
        self.fixture.execute('DELETE FROM t WHERE id = 105')
        self.fixture.execute('PRAGMA wal_checkpoint(FULL)')
        self._short_generation(200, 3)
        db_path = self.fixture.capture()
        _columns, rows, wal = rows_not_in_current(db_path, QUERY, include=ALL_KINDS)
        self.assertEqual([row.values[0] for row in rows], [105])
        self.assertGreater(wal.log.older_frames, 0)
        self.assertIn('from older generations', wal.summary())

    def test_checkpointed_current_generation_blocks_the_previous_one(self):
        self._generation_a()
        self._short_generation(200, 3)
        self.fixture.execute('PRAGMA wal_checkpoint(PASSIVE)')
        db_path = self.fixture.capture()
        _columns, rows, wal = rows_not_in_current(db_path, QUERY, include=ALL_KINDS)
        self.assertEqual(rows, [])
        self.assertEqual(wal.earlier_readable, [])
        self.assertIn('already holds', wal.summary())

    def test_zeroed_header_reads_the_generation_from_frame_one(self):
        self._generation_a()
        db_path = self.fixture.capture()
        with open(db_path + '-wal', 'r+b') as handle:
            handle.write(b'\x00' * 32)
        self.assertEqual(_current_state(db_path), None)
        _columns, rows, wal = rows_not_in_current(db_path, QUERY, include=ALL_KINDS)
        self.assertEqual(sorted(row.values[0] for row in rows), list(range(5, 18)))
        self.assertIn('unusable header', wal.summary())
        with WalStates(db_path, include=ALL_KINDS) as states:
            newest = next(states.states())
            rows_now = set(newest.connection.execute(QUERY).fetchall())
        self.assertEqual(rows_now, _sqlite_reading(db_path))

    def test_pages_allocated_later_do_not_block_earlier_states(self):
        # 60 large rows grow the file after the first commits. Pages past an earlier
        # state's size were not part of it, so they must not stop it being read; when
        # they did, only 3 of these states were readable.
        for i in range(1, 30):
            self.fixture.execute('INSERT INTO t VALUES (?, ?)', (i, 'early %d' % i))
        for i in range(3, 9):
            self.fixture.execute('DELETE FROM t WHERE id = ?', (i,))
        for i in range(100, 160):
            self.fixture.execute('INSERT INTO t VALUES (?, ?)', (i, 'late %d ' % i + 'z' * 900))
        self.fixture.execute('PRAGMA wal_checkpoint(FULL)')
        self._short_generation(500, 3)
        db_path = self.fixture.capture()
        _columns, rows, wal = rows_not_in_current(db_path, QUERY, include=ALL_KINDS)
        self.assertGreater(len(wal.earlier_readable), 40)
        self.assertEqual(wal.earlier_failed_check, 0)
        known = {(i, 'early %d' % i) for i in range(1, 30)}
        known |= {(i, 'late %d ' % i + 'z' * 900) for i in range(100, 160)}
        self.assertTrue({row.values for row in rows} <= known)

    def test_a_rebuilt_state_failing_quick_check_is_skipped(self):
        self._generation_a()
        self._short_generation(200, 3)
        db_path = self.fixture.capture()
        log = WalLog(db_path + '-wal')
        frame_size = 24 + log.page_size
        data = bytearray(Path(db_path + '-wal').read_bytes())
        # Damage the cell pointer area of one early left-over frame, then re-seal the
        # checksum chain from it so only the content is wrong.
        target = log.earlier.frames[5][0] - 1
        image = 32 + target * frame_size + 24
        data[image + 8:image + 24] = b'\xff' * 16
        state = struct.unpack('>2I', data[32 + (target - 1) * frame_size + 16:
                                          32 + (target - 1) * frame_size + 24])
        for index in range(target, log.total_frames):
            offset = 32 + index * frame_size
            state = _wal_checksum(bytes(data[offset:offset + 8] +
                                        data[offset + 24:offset + frame_size]),
                                  log.big_endian, state)
            data[offset + 16:offset + 24] = struct.pack('>2I', *state)
        Path(db_path + '-wal').write_bytes(bytes(data))
        _columns, rows, wal = rows_not_in_current(db_path, QUERY, include=ALL_KINDS)
        self.assertGreater(wal.earlier_failed_check, 0)
        self.assertIn('failed quick_check', wal.summary())
        self.assertTrue({row.values[0] for row in rows} <= set(range(5, 18)))


class UncommittedTest(unittest.TestCase):
    """Frames after the last commit, from a writer stopped mid-transaction."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _stopped_writer(self, mode):
        db_path = os.path.join(self.tmp, 't.db')
        subprocess.run([sys.executable, '-c', UNCOMMITTED_WRITER, db_path, mode],
                       check=True, stdin=subprocess.DEVNULL)
        return db_path

    def test_uncommitted_updates_to_existing_pages(self):
        db_path = self._stopped_writer('update')
        query = 'SELECT id, substr(txt, 1, 8) FROM t'
        self.assertGreater(WalLog(db_path + '-wal').uncommitted_frames, 0)
        _columns, rows, wal = rows_not_in_current(db_path, query, key_columns=[0],
                                                  include=ALL_KINDS)
        self.assertTrue(rows)
        self.assertTrue(all(row.status == UNCOMMITTED_CHANGE and row.uncommitted
                            and row.values[1] == 'pending ' for row in rows))
        self.assertIn('read as an uncommitted state', wal.summary())
        _columns, rows, _wal = rows_not_in_current(db_path, query, key_columns=[0])
        self.assertEqual(rows, [])

    def test_uncommitted_inserts_the_tree_does_not_reach(self):
        # Most new rows sit on pages no spilled interior page points to yet, so SQLite
        # cannot reach them; only the few on a reachable page come back.
        db_path = self._stopped_writer('insert')
        self.assertGreater(WalLog(db_path + '-wal').uncommitted_frames, 0)
        _columns, rows, _wal = rows_not_in_current(db_path, QUERY, include=ALL_KINDS)
        self.assertLess(len(rows), 300)
        self.assertTrue(all(row.status == UNCOMMITTED_CHANGE and row.values[0] >= 1000
                            for row in rows))


if __name__ == '__main__':
    unittest.main()
