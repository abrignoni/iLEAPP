"""Exercise stored Wire join multiplicity with actual SQLite schemas."""
import datetime
import pathlib
import shutil
import sqlite3
import tempfile
import unittest

from scripts.artifacts import wire


class _Context:
    def __init__(self, files):
        self.files = files

    def __call__(self):
        return self

    def get_files_found(self):
        return self.files


def _create(path, locations=True, phone=True, affinity='', collation='BINARY'):
    connection = sqlite3.connect(path)
    user = ['Z_PK', f'ZHANDLE {affinity} COLLATE {collation}', 'ZNAME', 'ZEMAILADDRESS']
    client = ['ZUSER', 'ZACTIVATIONDATE']
    if phone:
        user.append('ZPHONENUMBER')
    if locations:
        client.extend(['ZACTIVATIONLOCATIONLATITUDE', 'ZACTIVATIONLOCATIONLONGITUDE'])
    connection.execute('CREATE TABLE ZUSER (' + ','.join(user) + ')')
    connection.execute('CREATE TABLE ZUSERCLIENT (' + ','.join(client) + ')')
    connection.execute('CREATE TABLE ZMESSAGE '
                       '(ZSERVERTIMESTAMP, ZNORMALIZEDTEXT, ZCACHEDCATEGORY, ZDURATION, ZSENDER)')
    connection.commit()
    return connection, len(user), len(client)


class WireJoinOccurrencesTests(unittest.TestCase):
    def test_optional_schemas_keep_equal_join_and_unmatched_rows(self):
        for locations in (False, True):
            for phone in (False, True):
                with self.subTest(locations=locations, phone=phone), tempfile.TemporaryDirectory() as tmp:
                    path = pathlib.Path(tmp) / 'store.wiredatabase'
                    connection, users, clients = _create(path, locations, phone)
                    for key, handle in [(1, 'same'), (2, 'same'), (3, 'unmatched'), (4, 'unmatched')]:
                        connection.execute('INSERT INTO ZUSER VALUES (' + ','.join('?' * users) + ')',
                                           (key, handle, 'name', 'mail') + (('123',) if phone else ()))
                    for key, stamp in [(1, 800000000), (1, 800000000),
                                       (2, 800000000), (2, 800000010), (999, 800000000)]:
                        connection.execute('INSERT INTO ZUSERCLIENT VALUES (' +
                                           ','.join('?' * clients) + ')',
                                           (key, stamp) + ((12.25, -45.5) if locations else ()))
                    connection.commit()
                    phone_sql = 'u.ZPHONENUMBER' if phone else 'NULL'
                    columns = (f'c.ZACTIVATIONDATE,NULL,NULL,u.ZHANDLE,u.ZNAME,{phone_sql},u.ZEMAILADDRESS,'
                               'NULL,NULL,NULL,NULL')
                    if locations:
                        columns += ',c.ZACTIVATIONLOCATIONLATITUDE,c.ZACTIVATIONLOCATIONLONGITUDE'
                    suffix = ' FROM ZUSER u LEFT JOIN ZUSERCLIENT c ON u.Z_PK=c.ZUSER'
                    raw = connection.execute('SELECT ' + columns + suffix).fetchall()
                    distinct = connection.execute('SELECT DISTINCT ' + columns + suffix).fetchall()
                    expected = [((datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc) +
                                  datetime.timedelta(seconds=row[0])) if row[0] else row[0],) + row[1:]
                                for row in raw]
                    connection.close()
                    headers, rows, source = wire.wireAccount.__wrapped__(_Context([str(path)]))
                    self.assertEqual(rows, expected)
                    self.assertEqual(len(rows), 6)
                    self.assertEqual(len(distinct), 3)
                    self.assertEqual(len(headers), 13 if locations else 11)
                    self.assertEqual(source, str(path))

    def test_sqlite_storage_classes_collations_and_nonunique_left_keys(self):
        for affinity, collation in [('', 'BINARY'), ('TEXT', 'NOCASE'), ('INTEGER', 'BINARY')]:
            with self.subTest(affinity=affinity), tempfile.TemporaryDirectory() as tmp:
                path = pathlib.Path(tmp) / 'store.wiredatabase'
                connection, _, _ = _create(path, False, False, affinity, collation)
                values = [None, 0, 1, 1.0, '1', 'Case', 'case', '', b'raw', b'', -1, 1]
                for index, value in enumerate(values):
                    connection.execute('INSERT INTO ZUSER VALUES (?,?,?,?)',
                                       (index, value, 'same', 'mail'))
                # Equal left keys and equal clients produce four physical pairs.
                connection.execute('INSERT INTO ZUSER VALUES (?,?,?,?)', (100, 'fanout', '', ''))
                connection.execute('INSERT INTO ZUSER VALUES (?,?,?,?)', (100, 'fanout', '', ''))
                connection.executemany('INSERT INTO ZUSERCLIENT VALUES (?,?)', [(100, 0), (100, 0)])
                connection.commit()
                query = ('SELECT c.ZACTIVATIONDATE,NULL,NULL,u.ZHANDLE,u.ZNAME,NULL,u.ZEMAILADDRESS,'
                         'NULL,NULL,NULL,NULL FROM ZUSER u LEFT JOIN ZUSERCLIENT c ON u.Z_PK=c.ZUSER')
                expected = connection.execute(query).fetchall()
                old = connection.execute(query.replace('SELECT ', 'SELECT DISTINCT ', 1)).fetchall()
                connection.close()
                _, rows, _ = wire.wireAccount.__wrapped__(_Context([str(path)]))
                self.assertEqual([(type(row[3]), row) for row in rows],
                                 [(type(row[3]), row) for row in expected])
                self.assertEqual(len(rows), 16)
                self.assertLess(len(old), len(rows))

    def test_join_key_affinity_and_collation_use_actual_sqlite_comparison(self):
        for affinity in ('', 'TEXT', 'INTEGER'):
            for collation in ('BINARY', 'NOCASE'):
                with self.subTest(affinity=affinity, collation=collation), tempfile.TemporaryDirectory() as tmp:
                    path = pathlib.Path(tmp) / 'store.wiredatabase'
                    connection = sqlite3.connect(path)
                    key = f'{affinity} COLLATE {collation}'
                    connection.execute(f'CREATE TABLE ZUSER (Z_PK {key}, ZHANDLE, ZNAME, ZEMAILADDRESS)')
                    connection.execute(f'CREATE TABLE ZUSERCLIENT (ZUSER {key}, ZACTIVATIONDATE)')
                    for value in (1, '1', 1.0, 'Case', 'case', None):
                        connection.execute('INSERT INTO ZUSER VALUES (?,?,?,?)',
                                           (value, 'same', 'name', 'mail'))
                    connection.executemany('INSERT INTO ZUSERCLIENT VALUES (?,0)',
                                           [(value,) for value in (1, '1', 1.0, 'CASE', None)])
                    connection.commit()
                    query = ('SELECT c.ZACTIVATIONDATE,NULL,NULL,u.ZHANDLE,u.ZNAME,NULL,u.ZEMAILADDRESS,'
                             'NULL,NULL,NULL,NULL FROM ZUSER u LEFT JOIN ZUSERCLIENT c ON u.Z_PK=c.ZUSER')
                    expected = connection.execute(query).fetchall()
                    distinct = connection.execute(query.replace('SELECT ', 'SELECT DISTINCT ', 1)).fetchall()
                    pairs = connection.execute('SELECT u.rowid,c.rowid FROM ZUSER u '
                                               'LEFT JOIN ZUSERCLIENT c ON u.Z_PK=c.ZUSER').fetchall()
                    connection.close()
                    _, rows, _ = wire.wireAccount.__wrapped__(_Context([str(path)]))
                    self.assertEqual(rows, expected)
                    self.assertEqual(len(rows), len(pairs))
                    self.assertGreater(len(rows), len(distinct))

    def test_client_columns_tell_apart_clients_with_no_activation_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / 'store.wiredatabase'
            connection = sqlite3.connect(path)
            connection.execute('CREATE TABLE ZUSER (Z_PK, ZHANDLE, ZNAME, ZEMAILADDRESS, ZPHONENUMBER)')
            connection.execute('CREATE TABLE ZUSERCLIENT (ZUSER, ZACTIVATIONDATE, ZDISCOVERYDATE, '
                               'ZLASTACTIVEDATE, ZREMOTEIDENTIFIER, ZDEVICECLASS, ZLABEL, ZMODEL, '
                               'ZACTIVATIONLOCATIONLATITUDE, ZACTIVATIONLOCATIONLONGITUDE)')
            connection.execute("INSERT INTO ZUSER VALUES (1, 'other', 'name', NULL, NULL)")
            connection.execute("INSERT INTO ZUSER VALUES (2, 'unmatched', 'name', NULL, NULL)")
            connection.executemany('INSERT INTO ZUSERCLIENT VALUES (1, NULL, ?, NULL, ?, ?, NULL, NULL, 0.0, 0.0)',
                                   [(600000000, 'aa', 'phone'), (600000010, 'bb', 'phone')])
            connection.commit()
            connection.close()
            headers, rows, _ = wire.wireAccount.__wrapped__(_Context([str(path)]))
            self.assertEqual([h[0] if isinstance(h, tuple) else h for h in headers][:2],
                             ['Activation Date', 'Discovery Date'])
            self.assertEqual(len(headers), 13)
            self.assertEqual(len(rows), 3)
            self.assertEqual(len(set(rows)), 3)
            epoch = datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc)
            self.assertEqual(sorted((row[7], row[1]) for row in rows if row[7]),
                             [('aa', epoch + datetime.timedelta(seconds=600000000)),
                              ('bb', epoch + datetime.timedelta(seconds=600000010))])
            self.assertEqual([row[3] for row in rows if row[7] is None], ['unmatched'])

    def test_own_wal_and_first_input_selection_and_message_sibling(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            writer = root / 'writer.db'
            connection, _, _ = _create(writer, False, False)
            connection.execute('PRAGMA journal_mode=WAL')
            connection.execute('PRAGMA wal_autocheckpoint=0')
            connection.execute('INSERT INTO ZUSER VALUES (1,?,?,?)', ('handle', 'name', 'mail'))
            connection.execute('INSERT INTO ZUSERCLIENT VALUES (1,0)')
            connection.execute('INSERT INTO ZUSERCLIENT VALUES (1,0)')
            connection.executemany('INSERT INTO ZMESSAGE VALUES (?,?,?,?,?)',
                                   [(0, 'included', None, 0, 1), (0, 'excluded', 1, 0, 1)])
            connection.commit()
            full = root / 'full' / 'store.wiredatabase'
            main = root / 'main' / 'store.wiredatabase'
            full.parent.mkdir()
            main.parent.mkdir()
            for suffix in ('', '-wal', '-shm'):
                shutil.copyfile(str(writer) + suffix, str(full) + suffix)
            shutil.copyfile(writer, main)
            connection.close()
            _, rows, source = wire.wireAccount.__wrapped__(_Context([str(full), str(main), str(full)]))
            self.assertEqual(len(rows), 2)
            self.assertEqual(source, str(full))
            _, empty, source = wire.wireAccount.__wrapped__(_Context([str(main), str(full)]))
            self.assertEqual(empty, [])
            self.assertEqual(source, str(main))
            headers, messages, _ = wire.wireMessages.__wrapped__(_Context([str(full)]))
            self.assertEqual(len(headers), 6)
            self.assertEqual(messages, [(0, 'handle', 'name', 'included', None, 0)])


if __name__ == '__main__':
    unittest.main()
