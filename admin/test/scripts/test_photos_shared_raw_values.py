"""Raw values must retain NULL/unknown states and legitimate joined records."""
from contextlib import ExitStack
from pathlib import Path
import re
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from scripts.artifacts import Ph026SyndicationPLAssets as syndication
from scripts.artifacts import Ph023AlbumsSharedNAD as albums
from scripts.artifacts import Ph030iCloudShareMethodsNAD as shares


class Context:
    def __init__(self, path):
        self.path = path

    def get_files_found(self):
        return [self.path]

    def get_report_folder(self):
        return str(self.path.parent)


def invoke(module, key, path, reader):
    with ExitStack() as stack:
        stack.enter_context(patch.object(module.iOS, 'get_version', return_value='18.3.2'))
        stack.enter_context(patch.object(module, 'get_sqlite_db_records', side_effect=reader))
        stack.enter_context(patch.object(module, 'null_absent_columns', side_effect=lambda _, q: q))
        return getattr(module, key).__wrapped__(Context(path))


class TestPhotosSharedRawValues(unittest.TestCase):
    def run_fixture(self, module, key, records):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'Photos.sqlite'
            path.touch()
            captured = []
            invoke(module, key, path, lambda _, q: captured.append(q) or [])
            query = captured[0]
            aliases = dict((alias, table) for table, alias in
                           re.findall(r'(?:FROM|JOIN)\s+(\w+)\s+(\w+)', query))
            columns = {}
            for alias, column in re.findall(r'(\w+)\.(Z\w+)', query):
                columns.setdefault(aliases[alias], set()).add(column)
            connection = sqlite3.connect(path)
            for table, fields in columns.items():
                connection.execute(f'CREATE TABLE {table} ({",".join(sorted(fields))})')
            for table, values in records:
                names = list(values)
                connection.execute(f'INSERT INTO {table} ({",".join(names)}) '
                                   f'VALUES ({",".join("?" for _ in names)})', list(values.values()))
            connection.commit()
            headers, rows, _ = invoke(module, key, path,
                                     lambda _, q: connection.execute(q).fetchall())
            connection.close()
        names = [h[0] if isinstance(h, tuple) else h for h in headers]
        return [dict(zip(names, row)) for row in rows]

    def test_share_participants_preserve_unknown_and_null(self):
        rows = self.run_fixture(shares, 'Ph030iCloudSharedMethodswithNADPhDaPsql', [
            ('ZSHARE', {'Z_PK': 1, 'ZSCOPETYPE': 999, 'ZSTATUS': None}),
            ('ZSHAREPARTICIPANT', {'ZSHARE': 1, 'Z_PK': 10, 'ZROLE': 1}),
            ('ZSHAREPARTICIPANT', {'ZSHARE': 1, 'Z_PK': 11, 'ZROLE': -8}),
            ('ZSHARE', {'Z_PK': 2, 'ZSCOPETYPE': None, 'ZSTATUS': 4}),
        ])
        self.assertEqual(len(rows), 3)
        self.assertEqual([r['zShare-ZSCOPETYPE Raw Value-8'] for r in rows], [999, 999, None])
        self.assertCountEqual([r['zSharePartic-ZROLE Raw Value-34'] for r in rows], [1, -8, None])
        self.assertEqual([r['zShare-ZSTATUS Raw Value-7'] for r in rows], [None, None, 4])

    def test_album_invitations_keep_filter_and_multiplicity(self):
        rows = self.run_fixture(albums, 'Ph023SharedAlbumRecordsInviteswithNADPhDaPsql', [
            ('ZGENERICALBUM', {'Z_PK': 1, 'ZKIND': 1505}),
            ('ZGENERICALBUM', {'Z_PK': 2, 'ZKIND': 2}),
            ('ZCLOUDSHAREDALBUMINVITATIONRECORD', {'ZALBUM': 1, 'ZINVITATIONSTATE': 999}),
            ('ZCLOUDSHAREDALBUMINVITATIONRECORD', {'ZALBUM': 1, 'ZINVITATIONSTATE': None}),
        ])
        self.assertEqual(len(rows), 2)
        values = [next(v for k, v in row.items() if '-ZINVITATIONSTATE Raw Value-' in k)
                  for row in rows]
        self.assertCountEqual(values, [999, None])

    def test_syndication_null_unknown_and_excluded_asset(self):
        rows = self.run_fixture(syndication, 'Ph026_1SyndicationIDAssetsPhDaPsql', [
            ('ZADDITIONALASSETATTRIBUTES', {'Z_PK': 1, 'ZSYNDICATIONIDENTIFIER': 'a'}),
            ('ZADDITIONALASSETATTRIBUTES', {'Z_PK': 2, 'ZSYNDICATIONIDENTIFIER': None}),
            ('ZASSET', {'Z_PK': 1, 'ZADDITIONALATTRIBUTES': 1, 'ZSYNDICATIONSTATE': 999,
                        'ZSAVEDASSETTYPE': None}),
            ('ZASSET', {'Z_PK': 2, 'ZADDITIONALATTRIBUTES': 1, 'ZSYNDICATIONSTATE': None,
                        'ZSAVEDASSETTYPE': -9}),
            ('ZASSET', {'Z_PK': 3, 'ZADDITIONALATTRIBUTES': 2, 'ZSYNDICATIONSTATE': 8}),
        ])
        self.assertEqual(len(rows), 2)
        self.assertEqual([r['zAsset-ZSYNDICATIONSTATE Raw Value-13'] for r in rows], [999, None])
        self.assertEqual([r['zAsset-ZSAVEDASSETTYPE Raw Value-18'] for r in rows], [None, -9])


if __name__ == '__main__':
    unittest.main()
