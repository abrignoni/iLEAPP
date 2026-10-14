"""Actual SQLite origin affinity, file-local context and committed WAL rows."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts.safariHistory import safariHistory, safariHistoryTags


def write_fixture(path, values, affinity='', wal=False, tags=True):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    if wal:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('PRAGMA wal_autocheckpoint=0')
    db.execute('CREATE TABLE history_items (id, url, visit_count)')
    db.execute('CREATE TABLE history_visits (id, history_item, visit_time, '
               'title, redirect_source, redirect_destination, origin ' + affinity + ')')
    if tags:
        db.execute('CREATE TABLE history_tags (id, title, identifier, '
                   'modification_timestamp, item_count, type, level)')
        db.execute('CREATE TABLE history_items_to_tags (history_item, tag_id, timestamp)')
    if wal:
        db.commit()
        db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    for i, value in enumerate(values, 1):
        db.execute('INSERT INTO history_items VALUES (?, ?, ?)',
                   (i, f'https://example.test/{i}', i))
        db.execute('INSERT INTO history_visits VALUES (?, ?, ?, ?, ?, ?, ?)',
                   (i, i, 700000000 + i, f'title{i}', i - 1 if i > 1 else None,
                    i + 1 if i < len(values) else None, value))
    if tags:
        db.executemany('INSERT INTO history_tags VALUES (?, ?, ?, ?, ?, ?, ?)',
                       [(1, 'Alpha', 'Q1', 700000000, 1, 1, 200),
                        (2, 'Beta', 'Q2', 700000000, 1, 1, 200),
                        (3, 'Orphan', 'Q3', 700000000, 0, 1, 200)])
        if values:
            db.executemany('INSERT INTO history_items_to_tags VALUES (?, ?, ?)',
                           [(1, 2, 700000002), (1, 1, 700000001)])
    db.commit()
    return db


def context(root, files):
    return SimpleNamespace(get_files_found=lambda: [str(p) for p in files],
                           get_relative_path=lambda p: str(Path(p).relative_to(root)))


class TestSafariHistoryRawOrigin(unittest.TestCase):
    def test_native_storage_classes_and_file_context(self):
        values = [None, 0, 1, 2, -1, 99, -(2**63), 2**63 - 1, 0.0, 1.0,
                  1.5, '0', '1', '', 'unknown', '雪', b'', b'\x00\xff', 1, 1]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for affinity in ['', 'INTEGER', 'TEXT']:
                path = root / (affinity or 'NONE') / 'Safari/History.db'
                write_fixture(path, values, affinity).close()
                with sqlite3.connect(path) as db:
                    expected = db.execute('SELECT origin FROM history_visits '
                                          'ORDER BY visit_time, id').fetchall()
                _, rows, source = safariHistory.__wrapped__(context(root, [path]))
                self.assertEqual(source, str(path.relative_to(root)))
                self.assertEqual(len(rows), len(values))
                for row, stored in zip(rows, expected):
                    self.assertEqual(len(row), 12)
                    self.assertIs(type(row[7]), type(stored[0]))
                    self.assertEqual(row[7], stored[0])
                self.assertEqual(rows[0][8:10], ('Alpha; Beta', 'Q1; Q2'))
                self.assertEqual(rows[1][4], 'https://example.test/1')
                self.assertEqual(rows[0][5], 'https://example.test/2')
                self.assertEqual(rows[0][10:], ('Default', ''))

    def test_profile_title_tie_and_duplicate_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / 'a/Safari/Profiles/profile/History.db'
            write_fixture(path, [2], tags=False).close()
            tabs = []
            for folder, title in [('x', 'First'), ('y', 'Second')]:
                p = root / folder / 'Safari/SafariTabs.db'
                p.parent.mkdir(parents=True)
                with sqlite3.connect(p) as db:
                    db.execute('CREATE TABLE bookmarks (title, server_id, external_uuid)')
                    db.execute('INSERT INTO bookmarks VALUES (?, ?, ?)', (title, 'profile', 'other'))
                tabs.append(p)
            ctx = context(root, tabs + [path, path])
            _, rows, _ = safariHistory.__wrapped__(ctx)
            self.assertEqual(len(rows), 2)
            self.assertEqual([r[10:] for r in rows], [('profile', 'First')] * 2)
            _, rows, _ = safariHistory.__wrapped__(context(root, tabs[::-1] + [path]))
            self.assertEqual(rows[0][11], 'Second')
            self.assertEqual(safariHistoryTags.__wrapped__(ctx)[1], [])

    def test_committed_wal_origin_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / 'Safari/History.db'
            writer = write_fixture(path, [2, None, b'\xff'], wal=True)
            try:
                self.assertGreater(Path(str(path) + '-wal').stat().st_size, 0)
                _, rows, _ = safariHistory.__wrapped__(context(root, [path]))
                self.assertEqual([r[7] for r in rows], [2, None, b'\xff'])
                self.assertEqual(len(safariHistoryTags.__wrapped__(context(root, [path]))[1]), 3)
            finally:
                writer.close()
