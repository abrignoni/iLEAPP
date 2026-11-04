"""Read each Chromium saved-address layout from constructed databases."""
# pylint: disable=protected-access
import pathlib
import sqlite3
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import chrome as parser  # pylint: disable=wrong-import-position


def token_db(meta, tokens, with_record_type):
    con = sqlite3.connect(':memory:')
    extra = ', record_type INTEGER' if with_record_type else ''
    con.execute(f'CREATE TABLE "{meta}" (guid VARCHAR PRIMARY KEY, use_count INTEGER, '
                f'use_date INTEGER, date_modified INTEGER, label VARCHAR{extra})')
    con.execute(f'CREATE TABLE "{tokens}" (guid VARCHAR, type INTEGER, value VARCHAR, '
                'PRIMARY KEY (guid, type))')
    return con


class TokenLayouts(unittest.TestCase):
    def test_contact_info_row_carries_its_table_record_type(self):
        con = token_db('contact_info', 'contact_info_type_tokens', False)
        con.execute("INSERT INTO contact_info VALUES ('g1', 2, 1700000000, 1700000001, '')")
        con.executemany('INSERT INTO contact_info_type_tokens VALUES (?, ?, ?)',
                        [('g1', 7, 'full'), ('g1', 3, 'first'), ('g1', 36, 'CC'),
                         ('g1', 109, 'second'), ('g1', 999, 'odd'), ('g1', 33, '')])
        rows = parser._chrome_token_profiles(con.cursor(), 'contact_info',
                                               'contact_info_type_tokens',
                                               'kAccount or kAccountHome or kAccountWork')
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(len(row), 19)
        self.assertEqual(row[1], 'g1')
        self.assertEqual(row[2], 'first')
        self.assertEqual(row[9], '')            # empty city stays blank
        self.assertEqual(row[14], 'full')       # Full Name
        self.assertEqual(row[15], 'CC')         # Country
        self.assertEqual(row[16], 'NAME_LAST_SECOND: second; type 999: odd')
        self.assertEqual(row[17], 'kAccount or kAccountHome or kAccountWork')
        self.assertEqual(row[18], 'contact_info')

    def test_addresses_record_type_is_named_from_the_column(self):
        con = token_db('addresses', 'address_type_tokens', True)
        con.execute("INSERT INTO addresses VALUES ('g1', 1, 0, 0, '', 4)")
        rows = parser._chrome_token_profiles(con.cursor(), 'addresses', 'address_type_tokens', None)
        self.assertEqual(rows[0][17], 'kAccountNameEmail (4)')
        self.assertEqual(rows[0][0], '')        # a zero time is blank

    def test_missing_token_table_reads_nothing(self):
        con = sqlite3.connect(':memory:')
        con.execute('CREATE TABLE local_addresses (guid VARCHAR PRIMARY KEY)')
        self.assertEqual(parser._chrome_token_profiles(
            con.cursor(), 'local_addresses', 'local_addresses_type_tokens', 'x'), [])


class LegacyLayout(unittest.TestCase):
    def test_old_schema_without_newer_columns_still_reads(self):
        con = sqlite3.connect(':memory:')
        con.execute('CREATE TABLE autofill_profiles (guid VARCHAR PRIMARY KEY, company_name VARCHAR, '
                    'street_address VARCHAR, city VARCHAR, state VARCHAR, zipcode VARCHAR, '
                    'country_code VARCHAR, date_modified INTEGER, use_count INTEGER, use_date INTEGER)')
        con.execute('CREATE TABLE autofill_profile_names (guid VARCHAR, first_name VARCHAR, '
                    'middle_name VARCHAR, last_name VARCHAR)')
        con.execute('CREATE TABLE autofill_profile_emails (guid VARCHAR, email VARCHAR)')
        con.execute("INSERT INTO autofill_profiles VALUES ('g1', 'co', 'st', 'ci', 'sa', 'zz', 'CC', 1, 3, 2)")
        con.execute("INSERT INTO autofill_profile_names VALUES ('g1', 'a', '', 'b')")
        con.executemany('INSERT INTO autofill_profile_emails VALUES (?, ?)', [('g1', 'e1'), ('g1', 'e2')])
        con.execute("INSERT INTO autofill_profiles (guid) VALUES ('g2')")
        rows = parser._chrome_legacy_profiles(con.cursor())
        self.assertEqual(len(rows), 2)
        row = rows[0]
        self.assertEqual(row[2:12], ('a', '', 'b', 'e1; e2', '', 'co', 'st', 'ci', 'sa', 'zz'))
        self.assertEqual(row[13], 3)
        self.assertEqual(row[14:], ('', 'CC', '', '', 'autofill_profiles'))
        self.assertEqual(rows[1][2:12], ('',) * 10)

    def test_blob_value_is_reported_by_length(self):
        self.assertEqual(parser._chrome_value(b'\x00\x01'), '[2 bytes, not decoded]')
        self.assertEqual(parser._chrome_value(b''), '')


if __name__ == '__main__':
    unittest.main()
