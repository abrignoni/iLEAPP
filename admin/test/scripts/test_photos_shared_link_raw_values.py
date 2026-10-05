"""Shared-link rows retain source states and missing/one-to-many relationships."""
import ast
from pathlib import Path
import re
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from scripts.artifacts import Ph034iCloudSharedLinksNAD as links
from scripts.artifacts import Ph035iCloudSharedLinkAssets as assets

MODULES = (links, assets)


class Context:
    def __init__(self, path):
        self.path = path

    def get_files_found(self):
        return [self.path]

    def get_report_folder(self):
        return str(self.path.parent)


def create_fixture(root):
    path = Path(root) / 'CONSTRUCTED/private/var/mobile/Media/PhotoData/Photos.sqlite'
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    columns = {}
    for module in MODULES:
        for node in ast.walk(ast.parse(Path(module.__file__).read_text(encoding='utf-8'))):
            if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
                continue
            query = node.value
            if 'SELECT' not in query or 'FROM' not in query:
                continue
            aliases = {alias: table for table, alias in
                       re.findall(r'(?:FROM|JOIN)\s+(\w+)\s+(\w+)', query)}
            for alias, field in re.findall(r'(\w+)\.(Z\w+)', query):
                columns.setdefault(aliases[alias], set()).add(field)
    for table, fields in columns.items():
        connection.execute(f'CREATE TABLE {table} ({",".join(sorted(fields))})')
    records = [
        ('ZSHARE', {'Z_PK': 1, 'ZSCOPETYPE': 2, 'ZSTATUS': 999, 'ZPUBLICPERMISSION': None}),
        ('ZSHARE', {'Z_PK': 2, 'ZSCOPETYPE': 2, 'ZSTATUS': None}),
        ('ZSHARE', {'Z_PK': 3, 'ZSCOPETYPE': 4, 'ZSTATUS': 1}),
        ('ZSHAREPARTICIPANT', {'Z_PK': 10, 'ZSHARE': 1, 'ZROLE': -8, 'ZISCURRENTUSER': None}),
        ('ZSHAREPARTICIPANT', {'Z_PK': 11, 'ZSHARE': 1, 'ZROLE': None, 'ZISCURRENTUSER': 1}),
        ('ZASSET', {'Z_PK': 100, 'ZSAVEDASSETTYPE': 8, 'ZMOMENTSHARE': 1,
                    'ZSYNDICATIONSTATE': 999}),
        ('ZASSET', {'Z_PK': 101, 'ZSAVEDASSETTYPE': 8, 'ZMOMENTSHARE': 2,
                    'ZSYNDICATIONSTATE': None}),
        ('ZASSET', {'Z_PK': 102, 'ZSAVEDASSETTYPE': 8, 'ZMOMENTSHARE': 999,
                    'ZSYNDICATIONSTATE': -9}),
        ('ZASSET', {'Z_PK': 103, 'ZSAVEDASSETTYPE': 9, 'ZMOMENTSHARE': 1}),
    ]
    for table, record in records:
        fields = list(record)
        connection.execute(f'INSERT INTO {table} ({",".join(fields)}) '
                           f'VALUES ({",".join("?" for _ in fields)})', list(record.values()))
    connection.commit()
    connection.close()
    return path


def parse(module, path, version):
    reader = module.get_sqlite_db_records

    def read_and_close(source, query):
        cursor = reader(source, query)
        try:
            return list(cursor)
        finally:
            if isinstance(cursor, sqlite3.Cursor):
                cursor.connection.close()

    with patch.object(module.iOS, 'get_version', return_value=version), \
         patch.object(module, 'logfunc'), \
         patch.object(module, 'get_sqlite_db_records', side_effect=read_and_close):
        key = next(iter(module.__artifacts_v2__))
        headers, rows, _ = getattr(module, key).__wrapped__(Context(path))
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    return [dict(zip(names, row)) for row in rows]


def field_values(rows, field):
    return [next(v for k, v in row.items() if f'-{field} Raw Value-' in k) for row in rows]


class TestPhotosSharedLinkRawValues(unittest.TestCase):
    def test_all_supported_branches_keep_raw_states_and_relationships(self):
        with tempfile.TemporaryDirectory() as directory:
            path = create_fixture(directory)
            for version in ('14.3', '15.0.2', '16.5', '17.3', '17.6.1', '18.3.2'):
                with self.subTest(version=version):
                    share_rows = parse(links, path, version)
                    asset_rows = parse(assets, path, version)
                    self.assertEqual(len(share_rows), 3)
                    self.assertEqual(len(asset_rows), 4)
                    self.assertCountEqual(field_values(share_rows, 'ZSTATUS'), [999, 999, None])
                    self.assertCountEqual(field_values(share_rows, 'ZROLE'), [-8, None, None])
                    self.assertCountEqual(field_values(asset_rows, 'ZISCURRENTUSER'),
                                          [None, 1, None, None])
                    self.assertCountEqual(field_values(asset_rows, 'ZSAVEDASSETTYPE'), [8]*4)
                    if version != '14.3':
                        self.assertCountEqual(field_values(asset_rows, 'ZSYNDICATIONSTATE'),
                                              [999, 999, None, -9])

    def test_unsupported_versions_do_not_read_database(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'Photos.sqlite'
            path.touch()
            for module in MODULES:
                with patch.object(module, 'get_sqlite_db_records') as reader:
                    for version in ('13.3.1', '26.0'):
                        self.assertEqual(parse(module, path, version), [])
                    reader.assert_not_called()


if __name__ == '__main__':
    unittest.main()
