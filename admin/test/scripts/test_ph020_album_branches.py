"""Exercise actual Photos album query branches without changing their labels."""
import ast
import re
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.artifacts import Ph020AlbumsNAD as parser

WRAPPERS = ('Ph020_1AlbumRecordswithNADPhDaPsql', 'Ph020_2AlbumRecordswithNADSyndPL',
            'Ph020_3AlbumRecordswithNADGenPlayPsql')
VERSIONS = ('11.0', '13.0', '14.0', '15.0', '17.0', '18.0', '26.0')


def queries():
    """Read actual query literals, in their source branch order."""
    tree = ast.parse(Path(parser.__file__).read_text(encoding='utf-8'))
    return {node.name: [n.value for n in ast.walk(node) if isinstance(n, ast.Constant)
                       and isinstance(n.value, str) and 'FROM ZGENERICALBUM' in n.value]
            for node in tree.body if isinstance(node, ast.FunctionDef)}


def query_for(name, version):
    """Version selection mirrors only the documented SQL branch ranges."""
    major = int(version.split('.')[0])
    index = 0 if name == WRAPPERS[2] or major < 14 else 1 if major < 15 else 2 if major < 18 else 3
    return queries()[name][index]


def write_fixture(path, missing=False, wal=False):
    """Create a real single-table album store with known, unknown and null kinds."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted(set(re.findall(r'zGenAlbum\.(Z[A-Z0-9_]+)',
                                  '\n'.join(q for qs in queries().values() for q in qs))))
    if missing:
        fields.remove('ZCLOUDGUID')
    db = sqlite3.connect(path)
    if wal:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('PRAGMA wal_autocheckpoint=0')
    db.execute('CREATE TABLE ZGENERICALBUM (' + ','.join(fields) + ')')
    db.commit()
    if wal:
        db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    for index, kind in enumerate([None, 2, 1505, 1509, 9999, -1, 2, '9999', 2.5]):
        record = {field: index for field in fields}
        record.update(ZKIND=kind, ZTITLE='' if index == 0 else 'album-' + str(index),
                      ZSTARTDATE=1000 + index // 2, ZENDDATE=2000 + index,
                      ZCREATIONDATE=3000 + index // 2, ZTRASHEDSTATE=index % 3,
                      ZTRASHEDDATE=None if index == 0 else 4000 + index,
                      ZUUID='uuid-' + str(index))
        if not missing:
            record['ZCLOUDGUID'] = None if index == 0 else 'cloud-' + str(index)
        db.execute('INSERT INTO ZGENERICALBUM VALUES (' + ','.join('?' for _ in fields)
                   + ')', [record[field] for field in fields])
    db.commit()
    return db


class TestAlbumQueryBranches(unittest.TestCase):
    """All native cells remain actual SQL results across supported schema ranges."""
    def test_all_query_branches(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'Photos.sqlite'
            db = write_fixture(path)
            try:
                for version in VERSIONS:
                    for name in WRAPPERS:
                        if name == WRAPPERS[2] and int(version.split('.')[0]) < 18:
                            continue
                        expected = db.execute(query_for(name, version)).fetchall()
                        context = SimpleNamespace(get_files_found=lambda: [str(path)],
                                                  get_report_folder=lambda: directory)
                        with patch.object(parser.iOS, 'get_version', return_value=version):
                            headers, rows, source = getattr(parser, name).__wrapped__(context)
                        self.assertEqual(rows, expected)
                        self.assertEqual(source, str(path))
                        self.assertEqual(len(headers), 12 if int(version.split('.')[0]) < 14 else 14)
                        self.assertEqual([type(v) for row in rows for v in row],
                                         [type(v) for row in expected for v in row])
            finally:
                db.close()

    def test_optional_column_and_live_wal(self):
        with tempfile.TemporaryDirectory() as directory:
            for missing, wal in [(True, False), (False, True)]:
                path = Path(directory) / str(missing) / 'Photos.sqlite'
                db = write_fixture(path, missing, wal)
                try:
                    query = query_for(WRAPPERS[0], '18.0')
                    if missing:
                        query = query.replace('zGenAlbum.ZCLOUDGUID', 'NULL')
                    expected = db.execute(query).fetchall()
                    context = SimpleNamespace(get_files_found=lambda path=path: [str(path)],
                                              get_report_folder=lambda: directory)
                    with patch.object(parser.iOS, 'get_version', return_value='18.0'):
                        _, rows, _ = getattr(parser, WRAPPERS[0]).__wrapped__(context)
                    self.assertEqual(rows, expected)
                    if wal:
                        self.assertGreater(Path(str(path) + '-wal').stat().st_size, 32)
                finally:
                    db.close()


if __name__ == '__main__':
    unittest.main()
