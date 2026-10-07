"""Exercise actual product BLOB decoding and SQLite selection boundaries."""
import plistlib
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import home_depot


class HomeDepotProductFieldsTest(unittest.TestCase):
    def context(self, path):
        return SimpleNamespace(get_files_found=lambda: [str(path)],
                               get_relative_path=lambda value: Path(value).name)

    def test_xml_binary_values_and_occurrences(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'THDConsumer.sqlite'
            db = sqlite3.connect(path)
            db.execute('CREATE TABLE ZPRODUCTENTITY(ZPRODUCTID, ZPRODUCTSEARCHSKU)')
            products = [{}, {'specialPriceKey': 0}, {'specialPriceKey': False},
                        {'specialPriceKey': {'NS.string': 0}},
                        {'specialPriceKey': {'plain': [1, False]}}]
            for fmt in (getattr(plistlib, 'FMT_XML'), getattr(plistlib, 'FMT_BINARY')):
                for product in products:
                    db.execute('INSERT INTO ZPRODUCTENTITY VALUES(?, ?)',
                               ('id', plistlib.dumps(product, fmt=fmt)))
            db.commit()
            db.close()
            _, rows, source = home_depot.home_depot_products_viewed.__wrapped__(self.context(path))
            self.assertEqual([row[5] for row in rows], ['', 0, False, 0, {'plain': [1, False]}] * 2)
            self.assertIs(type(rows[1][5]), int)
            self.assertIs(type(rows[2][5]), bool)
            self.assertEqual(source, path.name)

    def test_json_scalar_and_nonmapping_skip(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'THDConsumer.sqlite'
            db = sqlite3.connect(path)
            db.execute('CREATE TABLE ZPRODUCTENTITY(ZPRODUCTID, ZPRODUCTSEARCHSKU)')
            for value in ('{"specialPriceKey":4}', None, plistlib.dumps([1, 2])):
                db.execute('INSERT INTO ZPRODUCTENTITY VALUES(?, ?)', ('id', value))
            db.commit()
            db.close()
            _, rows, _ = home_depot.home_depot_products_viewed.__wrapped__(self.context(path))
            self.assertEqual(rows, [])

    def test_decoded_presence_and_nonrecursive_string_key(self):
        cases = [({}, ''), ({'specialPriceKey': None}, None),
                 ({'specialPriceKey': {'NS.string': False}}, False),
                 ({'specialPriceKey': {'NS.string': {'NS.string': 4}}}, {'NS.string': 4})]
        for product, expected in cases:
            value = getattr(home_depot, '_product_field')(product, 'specialPriceKey')
            self.assertEqual(value, expected)
            self.assertIs(type(value), type(expected))

    def test_live_wal_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'THDConsumer.sqlite'
            db = sqlite3.connect(path)
            db.execute('CREATE TABLE ZPRODUCTENTITY(ZPRODUCTID, ZPRODUCTSEARCHSKU)')
            db.commit()
            db.execute('PRAGMA journal_mode=WAL')
            db.execute('PRAGMA wal_autocheckpoint=0')
            db.execute('INSERT INTO ZPRODUCTENTITY VALUES(?, ?)',
                       ('wal', plistlib.dumps({'specialPriceKey': 0})))
            db.commit()
            try:
                _, rows, _ = home_depot.home_depot_products_viewed.__wrapped__(self.context(path))
                self.assertEqual([row[0] for row in rows], ['wal'])
                self.assertIs(type(rows[0][5]), int)
            finally:
                db.close()


if __name__ == '__main__':
    unittest.main()
