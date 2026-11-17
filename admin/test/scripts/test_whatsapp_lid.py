"""WhatsApp LID artifacts on synthetic databases (values invented for the test)."""
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import whatsAppLID as parser  # noqa: E402

GROUP = 'private/var/mobile/Containers/Shared/AppGroup/{}'


def _db(path, statements):
    db = sqlite3.connect(path)
    for statement, *params in statements:
        db.execute(statement, *params)
    db.commit()
    db.close()


def _container(folder, with_account):
    folder.mkdir(parents=True)
    lid = [('CREATE TABLE ZWAPHONENUMBERLIDPAIR (Z_PK INTEGER PRIMARY KEY, ZTIMESTAMP TIMESTAMP, ZLID VARCHAR, '
            'ZPHONENUMBER VARCHAR)',),
           ('INSERT INTO ZWAPHONENUMBERLIDPAIR VALUES (1, 100, ?, ?)', ('111', '5550001')),
           ('CREATE TABLE ZWALIDPROPERTIES (Z_PK INTEGER PRIMARY KEY, ZLID VARCHAR, ZDISPLAYNAME VARCHAR)',),
           ('INSERT INTO ZWALIDPROPERTIES VALUES (1, ?, ?)', ('111@lid', 'Name A')),
           ('INSERT INTO ZWALIDPROPERTIES VALUES (2, ?, ?)', ('333@lid', 'Name C'))]
    if with_account:
        lid += [('CREATE TABLE ZWAZACCOUNT (Z_PK INTEGER PRIMARY KEY, ZIDENTIFIER VARCHAR, ZPHONENUMBER VARCHAR, '
                 'ZCREATEDAT TIMESTAMP)',),
                ('INSERT INTO ZWAZACCOUNT VALUES (1, ?, ?, 200)', ('222@lid', '5550002'))]
    _db(folder / 'LID.sqlite', lid)
    _db(folder / 'ContactsV2.sqlite', [
        ('CREATE TABLE ZWAADDRESSBOOKCONTACT (Z_PK INTEGER PRIMARY KEY, ZLID VARCHAR, ZWHATSAPPID VARCHAR, '
         'ZFULLNAME VARCHAR)',),
        ('INSERT INTO ZWAADDRESSBOOKCONTACT VALUES (1, ?, ?, ?)', ('111@lid', '5550001@s.whatsapp.net', 'Book A')),
        ('INSERT INTO ZWAADDRESSBOOKCONTACT VALUES (2, NULL, ?, ?)', ('5550009@s.whatsapp.net', 'Book Z'))])
    _db(folder / 'ChatStorage.sqlite', [
        ('CREATE TABLE ZWACHATSESSION (Z_PK INTEGER PRIMARY KEY, ZPARTNERNAME VARCHAR, ZCONTACTJID VARCHAR)',),
        ('INSERT INTO ZWACHATSESSION VALUES (1, ?, ?)', ('Group One', '1-2@g.us')),
        ('INSERT INTO ZWACHATSESSION VALUES (2, NULL, ?)', ('status@broadcast',)),
        ('CREATE TABLE ZWAGROUPMEMBER (Z_PK INTEGER PRIMARY KEY, ZCHATSESSION INTEGER, ZMEMBERJID VARCHAR, '
         'ZISADMIN INTEGER, ZISACTIVE INTEGER)',),
        ('INSERT INTO ZWAGROUPMEMBER VALUES (1, 1, ?, 1, 1)', ('111@lid',)),
        ('INSERT INTO ZWAGROUPMEMBER VALUES (2, 1, ?, 0, 1)', ('5550009@s.whatsapp.net',)),
        ('INSERT INTO ZWAGROUPMEMBER VALUES (3, 1, ?, 0, 0)', ('333@lid',)),
        ('INSERT INTO ZWAGROUPMEMBER VALUES (4, 2, ?, 0, 1)', ('222@lid',))])


class WhatsAppLidTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        root = pathlib.Path(self.directory.name)
        self.first = root / GROUP.format('A')
        self.second = root / GROUP.format('B')
        _container(self.first, with_account=True)
        _container(self.second, with_account=False)
        files = [str(folder / name) for folder in (self.first, self.second)
                 for name in ('LID.sqlite', 'ChatStorage.sqlite', 'ContactsV2.sqlite', 'ContactsV2.sqlite-wal')]
        self.context = SimpleNamespace(get_files_found=lambda: files)

    def tearDown(self):
        self.directory.cleanup()

    def test_lid_phone_numbers(self):
        headers, rows, source = parser.whatsapp_lid_phone_numbers.__wrapped__(self.context)
        self.assertEqual(len(headers), len(rows[0]))
        by_key = {(r[2], r[6]) for r in rows}
        self.assertEqual(by_key, {('111', 'ZWAPHONENUMBERLIDPAIR'), ('222', 'ZWAZACCOUNT')})
        self.assertEqual(len(rows), 3)
        pair = next(r for r in rows if r[2] == '111')
        self.assertEqual(pair[3:6], ('5550001', 'Name A', 'Book A'))
        self.assertEqual(pair[1], '')
        self.assertEqual(len(source.splitlines()), 2)

    def test_group_members(self):
        headers, rows, _ = parser.whatsapp_group_members.__wrapped__(self.context)
        self.assertEqual(len(headers), len(rows[0]))
        first = [r for r in rows if r[0] in ('Group One', '')][:4]
        by_member = {r[2]: r for r in first}
        self.assertEqual(by_member['111@lid'][3:7], ('5550001', 'ZWAPHONENUMBERLIDPAIR', 'Name A', 'Book A'))
        self.assertEqual(by_member['5550009@s.whatsapp.net'][3:7], ('5550009', 'Member JID', '', 'Book Z'))
        self.assertEqual(by_member['333@lid'][3:6], ('', '', 'Name C'))
        self.assertEqual(by_member['222@lid'][:2], ('', 'status@broadcast'))
        self.assertEqual(by_member['222@lid'][3:5], ('5550002', 'ZWAZACCOUNT'))
        # the second container has no ZWAZACCOUNT, so its 222@lid member stays unresolved
        second = [r for r in rows if r[2] == '222@lid']
        self.assertEqual(sorted(r[3] for r in second), ['', '5550002'])
        self.assertEqual(len(rows), 8)


if __name__ == '__main__':
    unittest.main()
