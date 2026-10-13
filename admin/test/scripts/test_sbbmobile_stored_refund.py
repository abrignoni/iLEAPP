"""Exercise stored refund values against actual SQLite queries and sidecars."""
import shutil
from contextlib import closing
from unittest.mock import patch
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import sbbmobile


class TestSbbStoredRefund(unittest.TestCase):
    HTML = ('<div class="ticketinformationen"><div class="item">'
            '<span class="value">first &amp; α</span></div>'
            '<div class="item"><span class="value">second</span></div></div>'
            '<p class="abgang">A</p><p class="bestimmung">B</p><p class="zonen">1</p>')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def database(self, name, affinity='', collation='BINARY', values=()):
        path = self.root / name / 'SbbMobile.db'
        path.parent.mkdir(parents=True)
        with closing(sqlite3.connect(path)) as db:
            db.execute('CREATE TABLE PurchasedTickets(traveler, validFrom, validUntil, '
                       f'refundState {affinity} COLLATE {collation}, paymentMethodType, '
                       'displayInfo_ticketType, screenTicket_contentHtml)')
            for value in values:
                db.execute('INSERT INTO PurchasedTickets VALUES(?,?,?,?,?,?,?)',
                           ('person', 0, None, value, 'card', 'ticket', self.HTML))
            db.commit()
        return path

    @staticmethod
    def run_parser(paths):
        context = SimpleNamespace(get_files_found=lambda: list(map(str, paths)))
        reader = sbbmobile.get_sqlite_db_records
        cursors = []

        def track_cursor(path, query):
            cursor = reader(path, query)
            cursors.append(cursor)
            return cursor

        with patch.object(sbbmobile, 'get_sqlite_db_records', track_cursor):
            try:
                return sbbmobile.sbb_purchased_tickets.__wrapped__(context)
            finally:
                for cursor in cursors:
                    if isinstance(cursor, sqlite3.Cursor):
                        cursor.connection.close()

    def test_actual_affinity_and_collation_raw_values_and_nine_cell_inverse(self):
        for affinity in ('', 'TEXT', 'INTEGER'):
            for collation in ('BINARY', 'NOCASE', 'RTRIM'):
                with self.subTest(affinity=affinity, collation=collation):
                    path = self.database((affinity or 'NONE') + collation,
                                         affinity, collation,
                                         [None, '', 'COMPLETE', 'complete', 'COMPLETE ',
                                          0, '0', -1, 1.25, 'unknown', 'COMPLETE'])
                    _, rows, source = self.run_parser([path])
                    with closing(sqlite3.connect(path)) as db:
                        raw = db.execute('SELECT traveler,validFrom,validUntil,refundState,'
                                         'paymentMethodType,displayInfo_ticketType '
                                         'FROM PurchasedTickets').fetchall()
                        legacy = db.execute("SELECT CASE WHEN refundState='COMPLETE' "
                                            "THEN 'Refunded' ELSE refundState END "
                                            'FROM PurchasedTickets').fetchall()
                    self.assertEqual(source, str(path))
                    self.assertEqual(len(rows), len(raw))
                    for row, stored, mapped in zip(rows, raw, legacy):
                        expected = (stored[1], stored[2], 'first & α', stored[0], stored[3],
                                    stored[4], stored[5], 'A', 'B', '1')
                        self.assertEqual(row, expected)
                        self.assertEqual([type(x) for x in row], [type(x) for x in expected])
                        inverse = tuple(row[i] for i in (3, 0, 1, 4, 5, 6, 2, 7, 8, 9))
                        original = stored[:3] + (mapped[0],) + stored[4:] + ('first & α', 'A', 'B', '1')
                        self.assertEqual(inverse[:3] + inverse[4:], original[:3] + original[4:])
                    if collation == 'NOCASE':
                        self.assertEqual(legacy[3], ('Refunded',))
                        self.assertEqual(rows[3][4], 'complete')
                    if collation == 'RTRIM':
                        self.assertEqual(legacy[4], ('Refunded',))
                        self.assertEqual(rows[4][4], 'COMPLETE ')
                    self.assertEqual(rows[2], rows[-1])

    def test_blob_after_only_raw_storage_classes(self):
        # No legacy CASE or legacy parser is executed on these values.
        path = self.database('blob', values=[b'COMPLETE', b'', b'\xff\x00', None])
        _, rows, _ = self.run_parser([path])
        with closing(sqlite3.connect(path)) as db:
            raw = db.execute('SELECT refundState,typeof(refundState) FROM PurchasedTickets').fetchall()
        self.assertEqual([row[4] for row in rows], [v for v, _ in raw])
        self.assertEqual([type(row[4]) for row in rows], [bytes, bytes, bytes, type(None)])

    def test_actual_wal_and_first_selected_main_order(self):
        first = self.database('first', values=['main'])
        writer = sqlite3.connect(first)
        self.addCleanup(writer.close)
        writer.execute('PRAGMA journal_mode=WAL')
        writer.execute('PRAGMA wal_autocheckpoint=0')
        writer.execute('INSERT INTO PurchasedTickets VALUES(?,?,?,?,?,?,?)',
                       ('wal', 5, 6, 'COMPLETE', 'card', 'wal ticket', self.HTML))
        writer.commit()
        snapshot = self.root / 'snapshot' / 'SbbMobile.db'
        snapshot.parent.mkdir()
        for suffix in ('', '-wal', '-shm'):
            shutil.copy2(str(first) + suffix, str(snapshot) + suffix)
        writer.close()
        second = self.database('second', values=['second'])
        _, rows, source = self.run_parser([snapshot, second, snapshot])
        self.assertEqual(source, str(snapshot))
        self.assertEqual([r[4] for r in rows], ['main', 'COMPLETE'])
        _, rows, source = self.run_parser([second, snapshot])
        self.assertEqual(source, str(second))
        self.assertEqual([r[4] for r in rows], ['second'])

    def test_html_first_value_and_absent_selectors_keep_legacy_projection(self):
        path = self.database('html', values=[0, None])
        reversed_html = self.HTML.replace('first &amp; α', 'TEMP').replace('second', 'first').replace('TEMP', 'second')
        with closing(sqlite3.connect(path)) as db:
            db.execute('UPDATE PurchasedTickets SET screenTicket_contentHtml=? WHERE rowid=1',
                       (reversed_html,))
            db.execute('UPDATE PurchasedTickets SET screenTicket_contentHtml=? WHERE rowid=2',
                       ('<p>safe missing selectors</p>',))
            db.commit()
        _, rows, _ = self.run_parser([path])
        self.assertEqual(rows[0][2], 'second')
        self.assertEqual((rows[1][2], *rows[1][7:]), ('', '', '', ''))
        self.assertEqual([r[4] for r in rows], [0, None])


if __name__ == '__main__':
    unittest.main()
