"""WhatsApp - Messages group sender columns on a synthetic ChatStorage (values invented for the test)."""
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import whatsApp as parser  # noqa: E402  # pylint: disable=wrong-import-position

GROUP = 'private/var/mobile/Containers/Shared/AppGroup/A'


def _build(folder):
    folder.mkdir(parents=True)
    chat = sqlite3.connect(folder / 'ChatStorage.sqlite')
    chat.executescript('''
        CREATE TABLE ZWACHATSESSION (Z_PK INTEGER PRIMARY KEY, ZPARTNERNAME VARCHAR, ZCONTACTJID VARCHAR);
        CREATE TABLE ZWAMEDIAITEM (Z_PK INTEGER PRIMARY KEY, ZMESSAGE INTEGER, ZMEDIALOCALPATH VARCHAR,
            ZXMPPTHUMBPATH VARCHAR, ZMETADATA BLOB, ZLATITUDE FLOAT, ZLONGITUDE FLOAT);
        CREATE TABLE ZWAGROUPMEMBER (Z_PK INTEGER PRIMARY KEY, ZCHATSESSION INTEGER, ZMEMBERJID VARCHAR);
        CREATE TABLE ZWAPROFILEPUSHNAME (Z_PK INTEGER PRIMARY KEY, ZJID VARCHAR, ZPUSHNAME VARCHAR);
        CREATE TABLE ZWAMESSAGE (Z_PK INTEGER PRIMARY KEY, ZMESSAGEDATE TIMESTAMP, ZISFROMME INTEGER,
            ZFROMJID VARCHAR, ZTOJID VARCHAR, ZMEDIAITEM INTEGER, ZTEXT VARCHAR, ZSTARRED INTEGER,
            ZMESSAGETYPE INTEGER, ZCHATSESSION INTEGER, ZGROUPMEMBER INTEGER);
        INSERT INTO ZWACHATSESSION VALUES (1, 'Group One', '1-2@g.us');
        INSERT INTO ZWACHATSESSION VALUES (2, 'Person', '5550002@s.whatsapp.net');
        INSERT INTO ZWAGROUPMEMBER VALUES (1, 1, '5550001@s.whatsapp.net');
        INSERT INTO ZWAPROFILEPUSHNAME VALUES (1, '5550001@s.whatsapp.net', 'Push A');
        INSERT INTO ZWAMESSAGE VALUES (1, 100, 0, '1-2@g.us', NULL, NULL, 'linked', 0, 0, 1, 1);
        INSERT INTO ZWAMESSAGE VALUES (2, 200, 0, '1-2@g.us', NULL, NULL, 'unlinked', 0, 0, 1, NULL);
        INSERT INTO ZWAMESSAGE VALUES (3, 300, 0, '5550002@s.whatsapp.net', NULL, NULL, 'direct', 0, 0, 2, NULL);
    ''')
    chat.commit()
    chat.close()
    book = sqlite3.connect(folder / 'ContactsV2.sqlite')
    book.executescript('''
        CREATE TABLE ZWAADDRESSBOOKCONTACT (Z_PK INTEGER PRIMARY KEY, ZWHATSAPPID VARCHAR, ZFULLNAME VARCHAR,
            ZPHONENUMBER VARCHAR);
        INSERT INTO ZWAADDRESSBOOKCONTACT VALUES (1, '5550001@s.whatsapp.net', 'Book A', '5550001');
    ''')
    book.commit()
    book.close()


class WhatsAppGroupSenderTest(unittest.TestCase):
    def test_sender_columns(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = pathlib.Path(directory) / GROUP
            _build(folder)
            files = [str(folder / 'ChatStorage.sqlite'), str(folder / 'ContactsV2.sqlite')]
            headers, rows, _ = parser.whatsAppMessages.__wrapped__(SimpleNamespace(get_files_found=lambda: files))
        names = [h[0] if isinstance(h, tuple) else h for h in headers]
        self.assertEqual(len(names), len(rows[0]))
        by_text = {row[names.index('Message')]: dict(zip(names, row)) for row in rows}
        linked = by_text['linked']
        self.assertEqual(linked['Sender ID'], '5550001@s.whatsapp.net')
        self.assertEqual(linked['From ID'], '1-2@g.us')
        self.assertEqual(linked['Group Sender Push Name'], 'Push A')
        self.assertEqual(linked['Group Sender Address Book Name'], 'Book A')
        unlinked = by_text['unlinked']
        self.assertEqual(unlinked['Sender ID'], '1-2@g.us')
        self.assertEqual((unlinked['Group Sender Push Name'], unlinked['Group Sender Address Book Name']), ('', ''))
        self.assertEqual(by_text['direct']['Sender ID'], '5550002@s.whatsapp.net')


if __name__ == '__main__':
    unittest.main()
