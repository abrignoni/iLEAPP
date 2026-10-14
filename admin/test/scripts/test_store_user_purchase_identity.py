"""CD0835: account-event repetition must not multiply purchase records."""
import collections
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.artifacts.storeUser import storeUser_pha


class StoreUserPurchaseIdentity(unittest.TestCase):
    def parse(self, purchases, events):
        with tempfile.TemporaryDirectory() as temporary:
            source = pathlib.Path(temporary) / 'storeUser.db'
            con = sqlite3.connect(source)
            con.executescript('''
                CREATE TABLE purchase_history_apps (
                    date_purchased REAL, title TEXT, long_title TEXT, bundle_id TEXT,
                    developer_name TEXT, product_url TEXT, store_item_id INTEGER,
                    hidden_from_springboard INTEGER, genre_name TEXT,
                    required_capabilities BLOB, purchaser_dsid INTEGER, purchase_token TEXT);
                CREATE TABLE account_events (account_id INTEGER, apple_id TEXT,
                    event_type INTEGER, timestamp REAL);
            ''')
            con.executemany('INSERT INTO purchase_history_apps VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', purchases)
            con.executemany('INSERT INTO account_events VALUES (?,?,?,?)', events)
            con.commit()
            con.close()
            return storeUser_pha.__wrapped__(SimpleNamespace(get_files_found=lambda: [str(source)]))

    @staticmethod
    def purchase(account=10, token='purchase-one'):
        return (1, 'App', 'App Long', 'test.app', 'Developer', 'https://example.com',
                100, 0, 'Tools', b'["arm64", "metal"]', account, token)

    def test_repeated_events_keep_each_purchase_record(self):
        # Identical purchase rows are separate source records, including identical tokens.
        headers, rows, _ = self.parse([self.purchase(), self.purchase()],
                                      [(10, 'first@example.com', 1, 10),
                                       (10, 'first@example.com', 2, 20)])
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], rows[1])
        self.assertEqual(rows[0][10], 'first@example.com')
        self.assertEqual(rows[0][9], 'arm64;\nmetal')
        self.assertEqual(headers[0], ('Purchased Timestamp', 'datetime'))
        self.assertEqual(rows[0][0], '2001-01-01 00:00:01')

    def test_distinct_identities_null_empty_and_unmatched_survive(self):
        _, rows, _ = self.parse([self.purchase(), self.purchase(20, 'unmatched')],
                               [(10, 'first@example.com', 1, 10),
                                (10, 'first@example.com', 2, 20),
                                (10, 'second@example.com', 1, 30),
                                (10, None, 1, 40), (10, None, 2, 50),
                                (10, '', 1, 60), (30, 'unrelated@example.com', 1, 70)])
        matched = [row for row in rows if row[11] == 10]
        self.assertEqual(collections.Counter(row[10] for row in matched),
                         collections.Counter(['first@example.com', 'second@example.com', None, '']))
        unmatched = [row for row in rows if row[11] == 20]
        self.assertEqual(len(unmatched), 1)
        self.assertIsNone(unmatched[0][10])
        self.assertEqual(unmatched[0][12], 'unmatched')
        self.assertEqual(len(rows), 5)


if __name__ == '__main__':
    unittest.main()
