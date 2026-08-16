__artifacts_v2__ = {
    "get_chromePaymentsCustomerData": {
        "name": "Payments Customer Data",
        "description": "Parses the payments customer data record from Chromium based browsers",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Chromium",
        "notes": "Reads the payments_customer_data table in Web Data. The table is created with a "
                 "single VARCHAR column, customer_id, and the browser writes it by deleting every "
                 "row and then inserting at most one, so a profile stores at most one value here. "
                 "Chromium describes the struct backing this table as the Google Payments customer "
                 "data and describes customer_id as the identifier by which a Google Payments "
                 "account is identified; what account that is, and whose it is, is not recorded in "
                 "this table and is not asserted here. The value is reported as stored. Chromium "
                 "clears this table alongside the other server sourced payment tables in "
                 "ClearAllServerData, so it is grouped with server data rather than with locally "
                 "entered payment details. An empty table is reported as no rows; that is not "
                 "evidence about whether an account exists, only that no record was stored in this "
                 "file. Validation boundary: 11 of the 24 tested iOS images carry a Web Data file, "
                 "20 files in total; the table was present in all 20 and held no rows in any of "
                 "them, so no iOS image exercises this parse. The code path was exercised instead "
                 "against a composite, an Android database carrying one row placed at the iOS "
                 "Chrome and Edge paths, which returned both rows with the browser resolved from "
                 "the path. The parse is confirmed against real rows in the ALEAPP module of the "
                 "same name, where 3 of 17 images hold one. An iOS image holding a payments "
                 "customer data record would close this gap. The table is checked for rather than "
                 "assumed, because the Android side shows Web Data files that do not carry it. A "
                 "Web Data file "
                 "left with a hot rollback journal cannot be recovered through a read-only handle; "
                 "such a file is logged and skipped so it does not end the run before the other "
                 "browsers on the device are read. Reference: Chromium, "
                 "'payments_autofill_table.cc', "
                 "https://github.com/chromium/chromium/blob/8f4baaae073181e7e0fea1807f8db6ad720dbcb7/components/autofill/core/browser/webdata/payments/payments_autofill_table.cc"
                 " and 'payments_customer_data.h', "
                 "https://github.com/chromium/chromium/blob/8f4baaae073181e7e0fea1807f8db6ad720dbcb7/components/autofill/core/browser/payments/payments_customer_data.h",
        "paths": ('*/Chrome/*/Web Data*', '*/Chromium/*/Web Data*', '*/Edge/*/Web Data*',
                  '*/Library/Application Support/Web Data*'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "id",
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

import os
import sqlite3

from scripts.ilapfuncs import logfunc, artifact_processor, open_sqlite_db_readonly
from scripts.artifacts.chrome import get_browser_name


def _table_exists(cursor, table):
    cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cursor.fetchone() is not None


@artifact_processor
def get_chromePaymentsCustomerData(context):
    all_data = []
    data_headers = ['Customer ID', 'Browser Name', 'Source File']
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
        rows = []
        try:
            cursor = db.cursor()
            if not _table_exists(cursor, 'payments_customer_data'):
                continue
            cursor.execute('SELECT customer_id FROM payments_customer_data')
            rows = cursor.fetchall()
        except sqlite3.Error as ex:
            logfunc(f'Unable to read {browser_name} payments customer data in {file_found}: {ex}')
            continue
        finally:
            db.close()

        if not rows:
            continue

        report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found
        source = context.get_relative_path(file_found)

        for row in rows:
            all_data.append((row[0], browser_name, source))

    return data_headers, all_data, report_file
