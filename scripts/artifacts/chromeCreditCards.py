__artifacts_v2__ = {
    "get_chromeCreditCards": {
        "name": "Saved Credit Cards",
        "description": "Parses saved payment card records from Chromium based browsers",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Chromium",
        "notes": "Reads the masked_credit_cards table in Web Data, joined to server_card_metadata on "
                 "id, mirroring the LEFT OUTER JOIN the browser itself uses, so a card with no "
                 "metadata row is still reported with an empty Date Last Used and Use Count. These "
                 "records hold the last four digits only; the tables carry no full card number and "
                 "none is reported. Column sets differ widely between releases, so columns are read "
                 "by name and any the release does not have are left empty rather than failing the "
                 "query. Date Last Used is server_card_metadata.use_date, read as microseconds since "
                 "1601-01-01 UTC, the epoch the browser uses for that column. The local credit_cards "
                 "table uses a different epoch (Unix seconds) and is not read by this artifact; it "
                 "stores its number encrypted. Card Network is reported as stored. Card Issuer, "
                 "Virtual Card Enrollment State and Card Creation Source are integers decoded "
                 "through Chromium's own enum definitions, which state the numbering is persistent "
                 "in the database; a value outside the defined set is reported as the bare integer. "
                 "Validation boundary: the tables were present in all 11 tested iOS images and held "
                 "no rows in any of them, so no iOS image exercises this parse. The code path was "
                 "exercised instead against a composite, an Android database carrying one card "
                 "placed at the iOS Chrome and Edge paths, which returned both rows with the "
                 "columns aligned and the browser resolved from the path. The parse and the 1601 "
                 "epoch are confirmed against a real row in the ALEAPP module of the same name. An "
                 "iOS image holding a saved payment card would close this gap. Rows are driven from "
                 "masked_credit_cards, so a metadata row whose card has been removed is not "
                 "reported. A Web Data file left with a hot rollback journal cannot be recovered "
                 "through a read-only handle; such a file is logged and skipped so it does not end "
                 "the run before the other browsers on the device are read. Reference: Chromium, "
                 "'payments_autofill_table.cc', "
                 "https://github.com/chromium/chromium/blob/8f4baaae073181e7e0fea1807f8db6ad720dbcb7/components/autofill/core/browser/webdata/payments/payments_autofill_table.cc"
                 " and 'enum_types.mojom', "
                 "https://github.com/chromium/chromium/blob/8f4baaae073181e7e0fea1807f8db6ad720dbcb7/components/autofill/core/browser/data_model/payments/enum_types.mojom",
        "paths": ('*/Chrome/*/Web Data*', '*/Chromium/*/Web Data*', '*/Edge/*/Web Data*',
                  '*/Library/Application Support/Web Data*'),
        "output_types": "standard",
        "artifact_icon": "credit-card",
        "sample_data": {
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    }
}

import datetime
import os
import sqlite3

from scripts.ilapfuncs import logfunc, artifact_processor, open_sqlite_db_readonly
from scripts.artifacts.chrome import get_browser_name

# Integer codes decoded through Chromium's own enum definitions. The file states
# the numbering is persistent in the database and kept in sync with the sync
# proto, so the values are not expected to shift between releases the way a
# build-assigned entity code would.
# Reference: Chromium, 'enum_types.mojom',
# https://github.com/chromium/chromium/blob/8f4baaae073181e7e0fea1807f8db6ad720dbcb7/components/autofill/core/browser/data_model/payments/enum_types.mojom
CARD_ISSUER = {
    0: 'Unknown',
    1: 'Google',
    2: 'External issuer',
}

VIRTUAL_CARD_ENROLLMENT_STATE = {
    0: 'Unspecified',
    1: 'Unenrolled (deprecated value)',
    2: 'Enrolled',
    3: 'Unenrolled and not eligible',
    4: 'Unenrolled and eligible',
}

CARD_CREATION_SOURCE = {
    0: 'Unspecified',
    1: 'Added through Chrome',
    2: 'Added outside of Chrome',
}


def _decode(mapping, value):
    """Return the documented label, or the value as stored when undefined."""
    if value is None or value == '':
        return ''
    try:
        return mapping.get(int(value), str(value))
    except (TypeError, ValueError):
        return str(value)


def _windows_epoch_us_to_utc(value):
    """server_card_metadata.use_date is microseconds since 1601-01-01 UTC."""
    if value in (None, 0, ''):
        return ''
    try:
        return (datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)
                + datetime.timedelta(microseconds=int(value)))
    except (TypeError, ValueError, OverflowError):
        return ''


def _table_exists(cursor, table):
    cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cursor.fetchone() is not None


def _rows_as_dicts(cursor, table):
    """Read a whole table into dicts keyed by column name.

    Releases carry very different column sets here, so reading by name and
    letting absent columns come back empty keeps one query working across all
    of them without naming a column the release does not have.
    """
    cursor.execute(f'SELECT * FROM {table}')
    columns = [description[0] for description in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


@artifact_processor
def get_chromeCreditCards(context):
    all_data = []
    data_headers = [
        ('Date Last Used', 'datetime'), 'Name on Card', 'Card Network (as stored)',
        'Last Four Digits', 'Expiration Month', 'Expiration Year', 'Use Count',
        'Bank Name', 'Nickname', 'Product Description', 'Card Issuer ID', 'Card Issuer',
        'Virtual Card Enrollment State', 'Card Creation Source', 'Billing Address ID',
        'Instrument ID', 'Card Art URL', 'Server ID', 'Browser Name', 'Source File']
    report_file = 'Unknown'

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'Web Data':  # skip -journal and other files
            continue

        browser_name = get_browser_name(file_found)

        db = open_sqlite_db_readonly(file_found)
        if db is None:
            continue

        # One unreadable database must not end the artifact. A Web Data file
        # left with a hot rollback journal cannot be recovered through a
        # read-only handle.
        cards = []
        metadata = {}
        try:
            cursor = db.cursor()
            if not _table_exists(cursor, 'masked_credit_cards'):
                continue
            cards = _rows_as_dicts(cursor, 'masked_credit_cards')
            if _table_exists(cursor, 'server_card_metadata'):
                metadata = {row.get('id'): row
                            for row in _rows_as_dicts(cursor, 'server_card_metadata')}
        except sqlite3.Error as ex:
            logfunc(f'Unable to read {browser_name} card tables in {file_found}: {ex}')
            continue
        finally:
            db.close()

        if not cards:
            logfunc(f'No {browser_name} - Saved Credit Cards data available')
            continue

        report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found
        source = context.get_relative_path(file_found)

        for card in cards:
            meta = metadata.get(card.get('id'), {})
            all_data.append((
                _windows_epoch_us_to_utc(meta.get('use_date')),
                card.get('name_on_card', ''),
                card.get('network', ''),
                card.get('last_four', ''),
                card.get('exp_month', ''),
                card.get('exp_year', ''),
                meta.get('use_count', ''),
                card.get('bank_name', ''),
                card.get('nickname', ''),
                card.get('product_description', ''),
                card.get('card_issuer_id', ''),
                _decode(CARD_ISSUER, card.get('card_issuer')),
                _decode(VIRTUAL_CARD_ENROLLMENT_STATE, card.get('virtual_card_enrollment_state')),
                _decode(CARD_CREATION_SOURCE, card.get('card_creation_source')),
                meta.get('billing_address_id', ''),
                card.get('instrument_id', ''),
                card.get('card_art_url', ''),
                card.get('id', ''),
                browser_name,
                source,
            ))

    return data_headers, all_data, report_file
