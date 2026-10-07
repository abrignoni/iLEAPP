"""Exercise stored generative-type values without assigning enum meanings."""
import ast
import re
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.artifacts import Ph017GenAIDetected as parser

WRAPPERS = (
    'Ph017_1GenAIDetectedPhDaPsql',
    'Ph017_2GenAIDetectedSyndPL',
    'Ph017_3GenAIDetectedGenPlayPsql',
)
VALUES = (None, 0, -3, 1, 2, 19, 1.5, '', '1', 'unknown', b'\x00\xff', 1)
TABLES = {'zAsset': 'ZASSET', 'zAddAssetAttr': 'ZADDITIONALASSETATTRIBUTES',
          'zExtAttr': 'ZEXTENDEDATTRIBUTES', 'zCldMast': 'ZCLOUDMASTER'}


def query_text(name=WRAPPERS[0]):
    """Read immutable SQL syntax without importing another artifact."""
    tree = ast.parse(Path(parser.__file__).read_text(encoding='utf-8'))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return next(n.value for n in ast.walk(function) if isinstance(n, ast.Constant)
                and isinstance(n.value, str) and 'FROM ZASSET' in n.value)


def write_fixture(path, affinity='', wal=False, values=VALUES):
    """Actual four-table schema; caller snapshots WAL before closing writer."""
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    if wal:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('PRAGMA wal_autocheckpoint=0')
    query = query_text()
    fields = {}
    for alias, table in TABLES.items():
        fields[alias] = sorted(set(re.findall(r'\b' + alias + r'\.(Z[A-Z0-9_]+)', query)))
        declarations = [field + (' ' + affinity if field == 'ZGENERATIVEAITYPE' else '')
                        for field in fields[alias]]
        db.execute('CREATE TABLE ' + table + ' (' + ','.join(declarations) + ')')
    db.commit()
    if wal:
        db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    for index, value in enumerate(values, 1):
        for alias, table in TABLES.items():
            record = {field: 0 for field in fields[alias]}
            record['Z_PK'] = index
            if alias == 'zAsset':
                record.update(ZADDITIONALATTRIBUTES=index, ZEXTENDEDATTRIBUTES=index,
                              ZMASTER=index, ZDATECREATED=1000 + index,
                              ZUUID='uuid-' + str(index), ZFILENAME='asset-' + str(index))
            if alias == 'zExtAttr':
                record.update(ZGENERATIVEAITYPE=value, ZCREDIT='credit-' + str(index))
            db.execute('INSERT INTO ' + table + ' VALUES (' + ','.join('?' for _ in record)
                       + ')', [record[field] for field in fields[alias]])
    # Deliberately duplicate a joined resource key to demonstrate retained fanout.
    db.execute('INSERT INTO ZEXTENDEDATTRIBUTES SELECT * FROM ZEXTENDEDATTRIBUTES WHERE Z_PK=4')
    db.commit()
    return db


class TestRawGenerativeType(unittest.TestCase):
    """Filter admission is decided by actual SQLite, not Python truthiness."""
    def test_native_storage_affinity_and_fanout(self):
        for affinity in ['', 'INTEGER']:
            with self.subTest(affinity=affinity), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'Photos.sqlite'
                db = write_fixture(path, affinity)
                expected = db.execute(query_text()).fetchall()
                expected_by_wrapper = {name: db.execute(query_text(name)).fetchall()
                                       for name in WRAPPERS}
                kinds = {r[0] for r in db.execute(
                    'SELECT typeof(ZGENERATIVEAITYPE) FROM ZEXTENDEDATTRIBUTES')}
                self.assertEqual(kinds, {'null', 'integer', 'real', 'text', 'blob'})
                self.assertEqual(sum(row[24] == 4 for row in expected), 2)
                db.close()
                for name in WRAPPERS:
                    with patch.object(parser.iOS, 'get_version', return_value='18.3.2'):
                        headers, rows, source = getattr(parser, name).__wrapped__(
                            SimpleNamespace(get_files_found=lambda path=path: [str(path)],
                                            get_report_folder=lambda directory=directory: directory))
                    self.assertEqual(len(headers), 31)
                    self.assertEqual(headers[29], 'zExtAttr-Generative_AI_Type (as stored)-29')
                    self.assertEqual(source, str(path))
                    self.assertEqual(rows, expected_by_wrapper[name])
                    self.assertEqual([type(row[29]) for row in rows],
                                     [type(row[29]) for row in expected])

    def test_wal_and_unsupported_version(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'Photos.sqlite'
            db = write_fixture(path, wal=True)
            try:
                self.assertGreater(Path(str(path) + '-wal').stat().st_size, 32)
                expected_by_wrapper = {name: db.execute(query_text(name)).fetchall()
                                       for name in WRAPPERS}
                for name in WRAPPERS:
                    context = SimpleNamespace(get_files_found=lambda path=path: [str(path)],
                                              get_report_folder=lambda directory=directory: directory)
                    with patch.object(parser.iOS, 'get_version', return_value='26.0'):
                        _, rows, _ = getattr(parser, name).__wrapped__(context)
                        self.assertEqual(rows, expected_by_wrapper[name])
                    with patch.object(parser.iOS, 'get_version', return_value='17.0'), \
                            patch.object(parser, 'get_sqlite_db_records') as reader:
                        self.assertEqual(getattr(parser, name).__wrapped__(context),
                                         ((), [], str(path)))
                        reader.assert_not_called()
            finally:
                db.close()


if __name__ == '__main__':
    unittest.main()
