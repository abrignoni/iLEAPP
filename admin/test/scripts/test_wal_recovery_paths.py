"""Write-ahead log recovery in artifacts must find the log beside a path with a space.

scripts/sqlite_wal.py takes a file system path and builds its own SQLite URI. A path that
has already been turned into a URI fragment (get_sqlite_db_path percent-encodes spaces) is
not a file name: the reader then sees no -wal and recovers nothing, without an error.
Every database here sits in a folder whose name has a space, as a case folder often does.
"""
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest


ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.artifacts import life360, snapchat  # pylint: disable=wrong-import-position
from scripts.artifacts import googlePhotos  # pylint: disable=wrong-import-position


def _capture(folder, name, statements):
    """Run statements in WAL mode and copy the database and its log out while the writer
    is still open, since closing it checkpoints the log away."""
    live = os.path.join(folder, 'live')
    evidence = os.path.join(folder, 'case folder with space')
    os.makedirs(live)
    os.makedirs(evidence)
    connection = sqlite3.connect(os.path.join(live, name), isolation_level=None)
    connection.execute('PRAGMA journal_mode=WAL')
    connection.execute('PRAGMA wal_autocheckpoint=0')
    for statement in statements:
        connection.execute(statement)
    for suffix in ('', '-wal'):
        shutil.copyfile(os.path.join(live, name + suffix), os.path.join(evidence, name + suffix))
    connection.close()
    return os.path.join(evidence, name)


class WalRecoveryPathTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_snapchat_messages_found_beside_a_path_with_a_space(self):
        path = _capture(self.tmp, 'arroyo.db', [
            'CREATE TABLE m (conv TEXT, id INTEGER, txt TEXT)',
            "INSERT INTO m VALUES ('c', 1, 'kept')",
            "INSERT INTO m VALUES ('c', 2, 'removed')",
            'DELETE FROM m WHERE id = 2'])
        removed = snapchat._removed_in_log(  # pylint: disable=protected-access
            path, 'SELECT conv, id, txt FROM m', (0, 1), {('c', 1)})
        self.assertEqual([row for row, _spans in removed], [('c', 2, 'removed')])

    def test_snapchat_conversations_found_beside_a_path_with_a_space(self):
        path = _capture(self.tmp, 'arroyo.db', [
            'CREATE TABLE conversation (client_conversation_id TEXT)',
            'CREATE TABLE feed_entry (client_conversation_id TEXT)',
            "INSERT INTO conversation VALUES ('kept')",
            "INSERT INTO conversation VALUES ('gone')",
            "DELETE FROM conversation WHERE client_conversation_id = 'gone'"])
        removed = snapchat._removed_conversation_ids(path)  # pylint: disable=protected-access
        self.assertEqual(set(removed), {'gone'})

    def test_snapchat_memories_found_beside_a_path_with_a_space(self):
        path = _capture(self.tmp, 'scdb-27.sqlite3', [
            'CREATE TABLE ZGALLERYSNAP (Z_PK INTEGER PRIMARY KEY, ZSNAPID TEXT, ZENTRY INTEGER)',
            "INSERT INTO ZGALLERYSNAP VALUES (1, 'kept', NULL)",
            "INSERT INTO ZGALLERYSNAP VALUES (2, 'gone', NULL)",
            'DELETE FROM ZGALLERYSNAP WHERE Z_PK = 2'])
        records = snapchat._memory_records_in_log(path, {'kept'})  # pylint: disable=protected-access
        self.assertEqual(set(records), {'gone'})

    def test_google_photos_rows_found_beside_a_path_with_a_space(self):
        path = _capture(self.tmp, 'photos-shared.db', [
            'CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT)',
            "INSERT INTO t VALUES (1, 'kept')",
            "INSERT INTO t VALUES (2, 'gone')",
            'DELETE FROM t WHERE id = 2'])
        found = googlePhotos._rows_in_log(path)  # pylint: disable=protected-access
        self.assertEqual([(table, row) for table, _c, _i, _d, row, _s, _cur in found],
                         [('t', (2, b'gone'))])

    def test_life360_chat_messages_found_beside_a_path_with_a_space(self):
        # A message is its ZCHATMESSAGE Z_PK: a row whose message is still current is not
        # reported again, a removed message is, with its sender joined from its own state.
        path = _capture(self.tmp, 'Messaging.sqlite', [
            'CREATE TABLE ZCHATMEMBER (Z_PK INTEGER PRIMARY KEY, ZFIRSTNAME TEXT)',
            'CREATE TABLE ZCHATMESSAGE (Z_PK INTEGER PRIMARY KEY, ZSENDER INTEGER, ZTEXT TEXT)',
            "INSERT INTO ZCHATMEMBER VALUES (1, 'a')",
            "INSERT INTO ZCHATMESSAGE VALUES (1, 1, 'kept')",
            "INSERT INTO ZCHATMESSAGE VALUES (2, 1, 'removed')",
            "UPDATE ZCHATMESSAGE SET ZTEXT = 'kept, edited' WHERE Z_PK = 1",
            'DELETE FROM ZCHATMESSAGE WHERE Z_PK = 2'])
        query = ('SELECT ZTEXT, ZFIRSTNAME, ZCHATMESSAGE.Z_PK, NULL FROM ZCHATMESSAGE '
                 'LEFT JOIN ZCHATMEMBER ON ZCHATMEMBER.Z_PK = ZSENDER')
        removed = life360._removed_messages(path, query, {1})  # pylint: disable=protected-access
        self.assertEqual([row for row, _method, _location in removed], [('removed', 'a', 2, None)])

if __name__ == '__main__':
    unittest.main()
