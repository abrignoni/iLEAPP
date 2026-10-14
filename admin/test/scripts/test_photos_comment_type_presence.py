"""Comment-type presence must preserve zero/negative/text states without numeric inference."""
import ast
from collections import Counter
from pathlib import Path
import re
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from scripts.artifacts import Ph011KwrdsCapsTitlesDescripsBasicAssetData as artifact

TYPES = (None, '', '0', '-1', '1', 'note: x', 0, -1, 1)


def create_fixture(root, affinity='VARCHAR'):
    path = Path(root) / 'CONSTRUCTED/private/var/mobile/Media/PhotoData/Photos.sqlite'
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    columns = {}
    for node in ast.walk(ast.parse(Path(artifact.__file__).read_text(encoding='utf-8'))):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        query = node.value
        if 'SELECT' not in query or 'FROM' not in query:
            continue
        aliases = {alias: table for table, alias in
                   re.findall(r'(?:FROM|JOIN)\s+(\w+)\s+(\w+)', query)}
        for alias, column in re.findall(r'(\w+)\.(Z\w+)', query):
            columns.setdefault(aliases[alias], set()).add(column)
    for table, fields in columns.items():
        definitions = [f'{field} {affinity}' if field == 'ZCOMMENTTYPE' else field
                       for field in sorted(fields)]
        connection.execute(f'CREATE TABLE {table} ({",".join(definitions)})')
    for asset_id, value in enumerate(TYPES, 1):
        connection.execute('INSERT INTO ZASSET (Z_PK) VALUES (?)', (asset_id,))
        connection.execute('INSERT INTO ZCLOUDSHAREDCOMMENT '
                           '(Z_PK,ZCOMMENTEDASSET,ZCOMMENTTYPE) VALUES (?,?,?)',
                           (asset_id, asset_id, value))
    connection.executemany('INSERT INTO ZASSET (Z_PK) VALUES (?)', [(10,), (11,), (12,)])
    connection.execute("INSERT INTO ZCLOUDSHAREDCOMMENT (Z_PK,ZCOMMENTEDASSET,ZCOMMENTTEXT) "
                       "VALUES (10,10,'text only, <present>')")
    connection.execute('INSERT INTO ZCLOUDSHAREDCOMMENT (Z_PK,ZLIKEDASSET,ZISLIKE) '
                       'VALUES (11,11,1)')
    connection.execute("INSERT INTO ZCLOUDSHAREDCOMMENT (Z_PK,ZCOMMENTEDASSET,ZCOMMENTTYPE) "
                       "VALUES (13,3,'0')")
    connection.execute("INSERT INTO ZCLOUDSHAREDCOMMENT (Z_PK,ZCOMMENTEDASSET,ZCOMMENTTYPE) "
                       "VALUES (14,999,'unmatched')")
    connection.commit()
    connection.close()
    return path


class Context:
    def __init__(self, path):
        self.path = path

    def get_files_found(self):
        return [self.path]

    def get_report_folder(self):
        return str(self.path.parent)


def parse(path, version, key):
    reader = artifact.get_sqlite_db_records

    def read_and_close(source, query):
        cursor = reader(source, query)
        try:
            return list(cursor)
        finally:
            if isinstance(cursor, sqlite3.Cursor):
                cursor.connection.close()

    with patch.object(artifact.iOS, 'get_version', return_value=version), \
         patch.object(artifact, 'get_sqlite_db_records', side_effect=read_and_close):
        headers, rows, _ = getattr(artifact, key).__wrapped__(Context(path))
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    return [dict(zip(names, row)) for row in rows]


class TestPhotosCommentTypePresence(unittest.TestCase):
    def test_all_queries_keep_type_only_boundaries_and_comment_rows(self):
        keys = list(artifact.__artifacts_v2__)
        with tempfile.TemporaryDirectory() as directory:
            path = create_fixture(directory)
            for key, versions in [(keys[0], ('14.3', '15.0.2', '16.5', '17.3', '18.3.2', '26.0')),
                                  (keys[1], ('18.3.2', '26.0'))]:
                for version in versions:
                    with self.subTest(key=key, version=version):
                        rows = parse(path, version, key)
                        ids = [next(v for k, v in row.items() if re.fullmatch(r'zAsset-zPK-\d+', k))
                               for row in rows]
                        self.assertEqual(Counter(ids), Counter([3, 3, 4, 5, 6, 7, 8, 9, 10, 11]))
                        types = [next(v for k, v in row.items()
                                      if re.fullmatch(r'zCldSharedComment-Type-\d+', k)) for row in rows]
                        self.assertCountEqual(types, ['0', '0', '-1', '1', 'note: x', '0', '-1', '1',
                                                     None, None])

    def test_typeless_numeric_storage_is_also_present(self):
        with tempfile.TemporaryDirectory() as directory:
            path = create_fixture(directory, affinity='')
            rows = parse(path, '18.3.2', next(iter(artifact.__artifacts_v2__)))
        types = [next(v for k, v in row.items() if re.fullmatch(r'zCldSharedComment-Type-\d+', k))
                 for row in rows]
        self.assertCountEqual(types, ['0', '0', '-1', '1', 'note: x', 0, -1, 1, None, None])


if __name__ == '__main__':
    unittest.main()
