"""Actual SQLite boundaries for the existing Truth Social account projections."""
from pathlib import Path
import shutil
import sqlite3
import tempfile
from types import SimpleNamespace
import unittest

from scripts.artifacts import truthSocial


def create(path, accounts, owners=(), events=()):
    connection = sqlite3.connect(path)
    connection.executescript('''
        CREATE TABLE ZMANAGEDACCOUNT(ZSERVERID, ZACCT, ZDISPLAYNAME, ZISVERIFIED, ZAVATARSTATIC);
        CREATE TABLE ZMANAGEDCHAT(ZOWNEDBYACCOUNTID);
        CREATE TABLE ZMANAGEDEVENTBASE(ZACCOUNTID1, ZACCOUNTID);
    ''')
    connection.executemany('INSERT INTO ZMANAGEDACCOUNT VALUES(?,?,?,?,?)', accounts)
    connection.executemany('INSERT INTO ZMANAGEDCHAT VALUES(?)', [(owner,) for owner in owners])
    connection.executemany('INSERT INTO ZMANAGEDEVENTBASE VALUES(?,?)', events)
    connection.commit()
    return connection


def parse(paths):
    context = SimpleNamespace(get_files_found=lambda: [str(path) for path in paths])
    return truthSocial.truthSocialAccounts.__wrapped__(context)


class AccountQueryMarkerTests(unittest.TestCase):
    def test_owner_query_distinct_and_coalesce_count_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'ChatModel.sqlite'
            create(path, [('managed', 'handle', 'display', 0, '')],
                   ['owner', 'owner', 'managed', None],
                   [('owner', 'managed'), (None, 'owner'), ('managed', 'owner')]).close()
            headers, rows, source = parse([path])
            self.assertEqual(headers[4], 'Owner-only Query Row')
            self.assertEqual(rows, [('managed', 'handle', 'display', '', '', 1, ''),
                                    ('owner', '', '', '', 'Yes', 2, '')])
            self.assertEqual(source, str(path))

    def test_null_managed_id_retains_existing_not_in_suppression(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'ChatModel.sqlite'
            create(path, [(None, 'handle', None, None, None)], ['owner']).close()
            _, rows, _ = parse([path])
            self.assertEqual(rows, [(None, 'handle', None, '', '', 0, None)])

    def test_native_id_storage_classes_and_current_verified_projection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'ChatModel.sqlite'
            identifiers = [0, 0.0, '0', b'raw', None]
            create(path, [(value, str(index), '', '0', '')
                          for index, value in enumerate(identifiers)]).close()
            _, rows, _ = parse([path])
            self.assertEqual([type(row[0]) for row in rows],
                             [int, float, str, bytes, type(None)])
            self.assertEqual([row[0] for row in rows], identifiers)
            self.assertTrue(all(row[3] == 'Yes' and row[4] == '' for row in rows))

    def test_first_matching_main_selection_stays_in_encounter_order(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = []
            for label in ['one', 'two']:
                path = Path(directory) / label / 'ChatModel.sqlite'
                path.parent.mkdir()
                create(path, [(label, label, '', 0, '')]).close()
                paths.append(path)
            self.assertEqual(parse(paths)[1][0][0], 'one')
            self.assertEqual(parse(list(reversed(paths)))[1][0][0], 'two')

    def test_committed_wal_owner_row_is_read_from_separate_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            writer = Path(directory) / 'writer.sqlite'
            connection = create(writer, [])
            connection.execute('PRAGMA journal_mode=WAL')
            connection.execute('PRAGMA wal_autocheckpoint=0')
            connection.execute("INSERT INTO ZMANAGEDCHAT VALUES('wal-owner')")
            connection.commit()
            snapshot = Path(directory) / 'ChatModel.sqlite'
            for suffix in ['', '-wal', '-shm']:
                source = Path(str(writer) + suffix)
                if source.exists():
                    shutil.copy2(source, Path(str(snapshot) + suffix))
            connection.close()
            _, rows, _ = parse([snapshot])
            self.assertEqual(rows, [('wal-owner', '', '', '', 'Yes', 0, '')])


    def test_optional_column_retains_existing_null_substitution(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'ChatModel.sqlite'
            connection = create(path, [('managed', 'handle', '', 0, '')])
            connection.execute('ALTER TABLE ZMANAGEDACCOUNT DROP COLUMN ZAVATARSTATIC')
            connection.commit()
            connection.close()
            _, rows, _ = parse([path])
            self.assertEqual(rows, [('managed', 'handle', '', '', '', 0, None)])

    def test_schema_column_and_row_committed_in_wal_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            writer = Path(directory) / 'writer.sqlite'
            connection = create(writer, [])
            connection.execute('ALTER TABLE ZMANAGEDACCOUNT DROP COLUMN ZISVERIFIED')
            connection.commit()
            connection.execute('PRAGMA journal_mode=WAL')
            connection.execute('PRAGMA wal_autocheckpoint=0')
            connection.execute('ALTER TABLE ZMANAGEDACCOUNT ADD COLUMN ZISVERIFIED')
            connection.execute("INSERT INTO ZMANAGEDACCOUNT "
                               "(ZSERVERID,ZACCT,ZDISPLAYNAME,ZAVATARSTATIC,ZISVERIFIED) "
                               "VALUES('managed','handle','','',1)")
            connection.commit()
            snapshot = Path(directory) / 'ChatModel.sqlite'
            for suffix in ['', '-wal', '-shm']:
                source = Path(str(writer) + suffix)
                if source.exists():
                    shutil.copy2(source, Path(str(snapshot) + suffix))
            connection.close()
            _, rows, _ = parse([snapshot])
            self.assertEqual(rows, [('managed', 'handle', '', 'Yes', '', 0, '')])


    def test_declared_nocase_collation_keeps_existing_query_comparison(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'ChatModel.sqlite'
            connection = create(path, [])
            connection.executescript("""
                DROP TABLE ZMANAGEDACCOUNT;
                DROP TABLE ZMANAGEDCHAT;
                CREATE TABLE ZMANAGEDACCOUNT(
                    ZSERVERID TEXT COLLATE NOCASE, ZACCT, ZDISPLAYNAME,
                    ZISVERIFIED, ZAVATARSTATIC);
                CREATE TABLE ZMANAGEDCHAT(ZOWNEDBYACCOUNTID TEXT COLLATE NOCASE);
                INSERT INTO ZMANAGEDACCOUNT VALUES('A','handle','',0,'');
                INSERT INTO ZMANAGEDCHAT VALUES('a');
                INSERT INTO ZMANAGEDEVENTBASE VALUES(NULL,'a');
            """)
            connection.commit()
            connection.close()
            _, rows, _ = parse([path])
            self.assertEqual(rows, [('A', 'handle', '', '', '', 1, '')])


if __name__ == '__main__':
    unittest.main()
