"""Native SQLite ZTYPE retention with both layouts and joined occurrences."""
import ast
import hashlib
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from scripts.artifacts import ZangiMessenger as artifact


class Context:
    def __init__(self, root, files):
        self.root, self.files = Path(root), list(map(str, files))

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


def query_for(module, name):
    """Read the exact parser SQL, without running the wrapper."""
    tree = ast.parse(Path(module.__file__).read_text(encoding='utf-8'))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == 'zangi_messages')
    return next(ast.literal_eval(n.value) for n in function.body
                if isinstance(n, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == name for t in n.targets))


def create_database(path, newer=False, wal=False):
    """Real affinityless typed values plus deliberate relationship fanout."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    if wal:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('PRAGMA wal_autocheckpoint=0')
    table = 'ZZMESSAGE' if newer else 'ZZANGIMESSAGE'
    db.executescript('''
    CREATE TABLE ZCONVERSATION(Z_PK,ZGROUPUID,ZUID,ZGROUPNAME,ZMEMBER);
    CREATE TABLE ZGROUP(Z_PK,ZCONVERSATION,ZUID);
    CREATE TABLE ZGROUPPROFILE(ZGROUP,ZNAME);
    CREATE TABLE ZCONTACTNUMBER(Z_PK,ZFULLNUMBER);
    CREATE TABLE Z_4CONTACTNUMBER(Z_5CONTACTNUMBER,Z_4CONTACT);
    CREATE TABLE ZCONTACT(Z_PK,ZDISPLAYNAME,ZFIRSTNAME,ZLASTNAME);
    CREATE TABLE ZZMESSAGEUSER(ZMESSAGE,ZCONTACTNUMBER,ZFULLNUMBER);
    CREATE TABLE ZZMESSAGEMEDIA(ZMESSAGE,ZFILEREMOTEPATH,ZMEDIAASSETSLIBRARYURL,ZFILEEXTENSION);
    INSERT INTO ZCONVERSATION VALUES(1,'group','chat','Chat',NULL);
    INSERT INTO ZGROUP VALUES(1,1,'group');
    INSERT INTO ZGROUPPROFILE VALUES(1,'First'),(1,'Second');
    ''')
    db.execute(f'''CREATE TABLE {table}(Z_PK,ZMESSAGETIME,ZMESSAGE,ZTYPE,
        ZMESSAGEID,ZCONVERSATION,ZFROM,ZISRECEIVED,ZFILEREMOTEPATH,
        ZMEDIAASSETSLIBRARYURL,ZENCRYPTFILEREMOTEPATH,ZFILEEXTENSION,ZMESSAGEINFO)''')
    values = [None, 0, 1, 5, 7, -7, 7.25, '7', 'unknown', '', b'7', 7]
    for index, value in enumerate(values, 1):
        db.execute(f'INSERT INTO {table} VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',
                   (index, 700000000 + index, 'document', value, 'msgId'+str(index),
                    1, None, index % 2, '', '', '', 'png', 'info'))
        if newer:
            db.execute('INSERT INTO ZZMESSAGEUSER VALUES(?,NULL,?)', (index, 'sender'))
            db.execute("INSERT INTO ZZMESSAGEMEDIA VALUES(?,'','','png')", (index,))
    if newer:
        db.execute("INSERT INTO ZZMESSAGEUSER VALUES(1,NULL,'second sender')")
        db.execute("INSERT INTO ZZMESSAGEMEDIA VALUES(1,'','','png')")
    db.commit()
    # A committed message exists only in live WAL, not the checkpointed main.
    if wal:
        db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
        db.execute(f"INSERT INTO {table} SELECT 99,700000099,ZMESSAGE,99,"
                   "'msgId99',ZCONVERSATION,ZFROM,ZISRECEIVED,ZFILEREMOTEPATH,"
                   'ZMEDIAASSETSLIBRARYURL,ZENCRYPTFILEREMOTEPATH,ZFILEEXTENSION,'
                   f'ZMESSAGEINFO FROM {table} WHERE Z_PK=2')
        if newer:
            db.execute("INSERT INTO ZZMESSAGEUSER VALUES(99,NULL,'wal sender')")
            db.execute("INSERT INTO ZZMESSAGEMEDIA VALUES(99,'','','png')")
        db.commit()
    return db


def media_reference(path, *_):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class TestZangiRawType(unittest.TestCase):
    def check_layout(self, newer, wal=False):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root)/'private/var/mobile/Containers/Shared/AppGroup/A/zangidb.sqlite'
            writer = create_database(path, newer, wal)
            try:
                query = query_for(artifact, 'query_new' if newer else 'query_legacy')
                oracle = writer.execute(query).fetchall()
                files = [path] + sorted(path.parent.glob('*.sqlite-*'))
                with patch.object(artifact, 'check_in_media', media_reference):
                    headers, rows, source = artifact.zangi_messages.__wrapped__(Context(root, files))
                self.assertEqual(len(headers), 16)
                self.assertEqual(headers[8], 'ZTYPE (as stored)')
                self.assertEqual(source, str(path))
                self.assertEqual(len(rows), len(oracle))
                self.assertEqual(len(rows), (30 if newer else 24) + (2 if wal else 0))
                for row, direct in zip(rows, oracle):
                    self.assertEqual(row[8], direct[13])
                    self.assertIs(type(row[8]), type(direct[13]))
                    self.assertEqual(row[7], direct[3])
                    self.assertEqual(row[9], direct[4])
                self.assertEqual({type(r[8]) for r in rows},
                                 {type(None), int, float, str, bytes})
                if wal:
                    self.assertEqual(sum(r[8] == 99 for r in rows), 2)
                if not newer:
                    unknown = [r[8] for r in rows if r[7] == 'Other/Unknown']
                    self.assertIn(None, unknown)
                    self.assertIn(-7, unknown)
                    self.assertIn(b'7', unknown)
            finally:
                writer.close()

    def test_legacy_native_types_and_label_collisions(self):
        self.check_layout(False)

    def test_new_native_types_and_fanout(self):
        self.check_layout(True)

    def test_multiple_sources_repeats_and_unchanged_media_preference(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            mains = [root / group / 'zangidb.sqlite' for group in ['A', 'B']]
            for main in mains:
                create_database(main).close()
            media = [root / group / 'image' / 'msgId3' for group in ['A', 'B']]
            for index, path in enumerate(media):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'\x89PNG\r\n\x1a\n' + bytes([index]))
            for order in [media, list(reversed(media))]:
                with patch.object(artifact, 'check_in_media', media_reference):
                    _, rows, source = artifact.zangi_messages.__wrapped__(
                        Context(root, mains + order))
                self.assertEqual(len(rows), 48)
                self.assertEqual(source.splitlines(), list(map(str, mains)))
                self.assertEqual([sum(r[15] == group + '/zangidb.sqlite'
                                      for r in rows) for group in ['A', 'B']], [24, 24])
                self.assertEqual({r[5] for r in rows if r[5]},
                                 {media_reference(order[0])})
                self.assertEqual(sum(r[9] == 'msgId3' for r in rows), 4)

    def test_legacy_live_wal(self):
        self.check_layout(False, True)

    def test_new_live_wal(self):
        self.check_layout(True, True)
