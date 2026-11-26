"""Synthetic checks for chromeFavicons: the join, the enums, the times and the History lookup."""
import os
import shutil
import sqlite3
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

from scripts.artifacts import chromeFavicons as module

PNG = b'\x89PNG\r\n\x1a\n' + b'\x00' * 24
# 2024-01-01 00:00:00 UTC as microseconds since 1601-01-01.
JAN_2024 = 13348540800 * 1_000_000


def favicons_db(path, page_url_type=True, last_requested=True):
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE icon_mapping (id INTEGER PRIMARY KEY, page_url TEXT, icon_id INTEGER'
               + (', page_url_type INTEGER' if page_url_type else '') + ')')
    db.execute('CREATE TABLE favicons (id INTEGER PRIMARY KEY, url TEXT, icon_type INTEGER)')
    db.execute('CREATE TABLE favicon_bitmaps (id INTEGER PRIMARY KEY, icon_id INTEGER, '
               'last_updated INTEGER, image_data BLOB, width INTEGER, height INTEGER'
               + (', last_requested INTEGER' if last_requested else '') + ')')
    db.execute('INSERT INTO favicons VALUES (1, ?, 1), (2, ?, 16)',
               ('https://a.test/favicon.ico', 'https://b.test/icon.png'))
    bitmaps = [(1, 1, JAN_2024, PNG, 16, 16), (2, 1, JAN_2024 + 1_000_000, PNG + b'x', 32, 32),
               (3, 2, 0, PNG + b'y', 16, 16)]
    for row in bitmaps:
        if last_requested:
            db.execute('INSERT INTO favicon_bitmaps VALUES (?, ?, ?, ?, ?, ?, ?)',
                       row + ((JAN_2024 if row[0] == 3 else 0),))
        else:
            db.execute('INSERT INTO favicon_bitmaps VALUES (?, ?, ?, ?, ?, ?)', row)
    mappings = [(1, 'https://a.test/', 1, 0), (2, 'https://b.test/page', 2, 1)]
    for row in mappings:
        db.execute(f'INSERT INTO icon_mapping VALUES ({", ".join("?" * (4 if page_url_type else 3))})',
                   row if page_url_type else row[:3])
    db.commit()
    db.close()


def history_db(path, urls):
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE urls (id INTEGER PRIMARY KEY, url TEXT)')
    db.executemany('INSERT INTO urls (url) VALUES (?)', [(u,) for u in urls])
    db.commit()
    db.close()


class TestChromeFavicons(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.profile = os.path.join(self.tmp, 'Chrome', 'Default')
        os.makedirs(self.profile)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_module(self, files):
        context = SimpleNamespace(get_files_found=lambda: files, get_relative_path=os.path.basename)
        with mock.patch.object(module, 'check_in_embedded_media', side_effect=lambda f, d: f'media-{len(d)}'), \
                mock.patch.object(module, 'get_browser_name', return_value='Chrome'), \
                mock.patch.object(module, 'logfunc'):
            return module.chromeFavicons.__wrapped__(context)

    def test_rows_join_enums_and_history(self):
        fav = os.path.join(self.profile, 'Favicons')
        hist = os.path.join(self.profile, 'History')
        favicons_db(fav)
        history_db(hist, ['https://a.test/'])
        _, rows, source = self.run_module([fav, hist])
        self.assertEqual(len(rows), 2)
        first, second = rows
        self.assertEqual(first[0].isoformat(), '2024-01-01T00:00:01+00:00')
        self.assertEqual(first[1], '')
        self.assertEqual(first[2:7], ('https://a.test/', 'Yes', 'https://a.test/favicon.ico',
                                      'kFavicon (1)', '16x16, 32x32'))
        self.assertEqual(first[7], f'media-{len(PNG) + 1}')
        self.assertEqual(first[8:], ('kRegular (0)', 'Chrome'))
        self.assertEqual(second[0], '')
        self.assertEqual(second[1].isoformat(), '2024-01-01T00:00:00+00:00')
        self.assertEqual(second[3], 'No')
        self.assertEqual(second[5], '16')
        self.assertEqual(second[8], 'kRedirect (1)')
        self.assertEqual(source.split('\n'), [fav, hist])

    def test_older_schema_and_no_history(self):
        fav = os.path.join(self.profile, 'Favicons')
        favicons_db(fav, page_url_type=False, last_requested=False)
        _, rows, source = self.run_module([fav])
        self.assertEqual(len(rows), 2)
        self.assertEqual([r[3] for r in rows], ['', ''])
        self.assertEqual([r[8] for r in rows], ['', ''])
        self.assertEqual([r[1] for r in rows], ['', ''])
        self.assertEqual(source, fav)

    def test_missing_table_gives_no_rows(self):
        fav = os.path.join(self.profile, 'Favicons')
        db = sqlite3.connect(fav)
        db.execute('CREATE TABLE meta (key TEXT, value TEXT)')
        db.commit()
        db.close()
        _, rows, source = self.run_module([fav])
        self.assertEqual((rows, source), ([], ''))


if __name__ == '__main__':
    unittest.main()
