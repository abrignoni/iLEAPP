"""The Photos.sqlite entity renumbering resolves numbers by name from the store, from iOS 27 on."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.artifacts.Ph126iOS26REFforAssetAnalysis import renumber_photos_entities

QUERY = ('SELECT z33Assets.Z_33ALBUMS, Z_3MEMORIESBEINGCURATEDASSETS.Z_56MEMORIESBEINGCURATEDASSETS, '
         'zSharePartic.Z66_SHARE, zSharePartic.Z61_SHARE, Z_FOK_ALBUM, Z_32ALBUMLISTS.Z_FOK_32ALBUMS, '
         'Z_PK, Z_ENT FROM Z_33ASSETS z33Assets LEFT JOIN Z_32ALBUMLISTS ON Z_32ALBUMLISTS.Z_2ALBUMLISTS = 1')


class TestPhotosEntityRenumbering(unittest.TestCase):

    def _store(self, directory, entities):
        path = Path(directory) / 'Photos.sqlite'
        with sqlite3.connect(path) as db:
            db.execute('CREATE TABLE Z_PRIMARYKEY (Z_ENT INTEGER PRIMARY KEY, Z_NAME VARCHAR)')
            db.executemany('INSERT INTO Z_PRIMARYKEY VALUES (?, ?)', entities)
        return str(path)

    def test_before_ios_27_the_query_is_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self._store(directory, [(34, 'Album')])
            for ios in ('18.0', '26.5.2'):
                self.assertEqual(renumber_photos_entities(path, QUERY, ios), QUERY)

    def test_ios_27_numbers_come_from_the_store_by_name(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self._store(directory, [(2, 'AlbumList'), (3, 'Asset'), (33, 'GenericAlbum'),
                                           (34, 'Album'), (59, 'Memory'), (71, 'Share')])
            result = renumber_photos_entities(path, QUERY, '27.2')
        self.assertEqual(result, (
            'SELECT z33Assets.Z_34ALBUMS, Z_3MEMORIESBEINGCURATEDASSETS.Z_59MEMORIESBEINGCURATEDASSETS, '
            'zSharePartic.Z71_SHARE, zSharePartic.Z61_SHARE, Z_FOK_ALBUM, Z_33ALBUMLISTS.Z_FOK_33ALBUMS, '
            'Z_PK, Z_ENT FROM Z_34ASSETS z33Assets LEFT JOIN Z_33ALBUMLISTS ON Z_33ALBUMLISTS.Z_2ALBUMLISTS = 1'))

    def test_a_name_the_store_lacks_is_left_as_written(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self._store(directory, [(34, 'Album')])
            result = renumber_photos_entities(path, 'SELECT Z_33ALBUMS, Z_56MEMORIESBEINGCURATEDASSETS', '27.2')
        self.assertEqual(result, 'SELECT Z_34ALBUMS, Z_56MEMORIESBEINGCURATEDASSETS')

    def test_a_store_without_z_primarykey_returns_the_query(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'Photos.sqlite'
            with sqlite3.connect(path) as db:
                db.execute('CREATE TABLE unrelated (value)')
            self.assertEqual(renumber_photos_entities(str(path), QUERY, '27.2'), QUERY)


if __name__ == '__main__':
    unittest.main()
