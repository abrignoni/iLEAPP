""" Apple Watch mail sync registry: DeviceRegistry/<id>/NanoMail/registry.sqlite """
__artifacts_v2__ = {
    "appleWatchMailSyncedMessages": {
        "name": "Apple Watch Mail Synced Messages",
        "description": "One row per row of SYNCED_MESSAGE in the NanoMail registry under "
                       "DeviceRegistry, with its received date, message identifier and "
                       "mailbox.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-10",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "Apple Watch",
        "notes": "Date Received is DATE_RECEIVED read as Unix seconds, shown in UTC in the HTML "
                 "and TSV reports. The shared converter would rescale a value of ten billion or "
                 "more as a sub-second unit; none of the 153 values was. The epoch is not "
                 "sourced: the 153 values on the sample_data images are integers that, read this "
                 "way, fall in 2020, 2021 and 2024, and read from 2001 fall in 2051 to 2055. "
                 "Message ID is the ID column as stored; all 153 had the form "
                 "x-apple-mail://message/ followed by a number and a uuid parameter, and what "
                 "the number refers to is not established. The row holds no sender, subject or "
                 "body. Mailbox ID is MAILBOX_ID, and Mailbox Name is the CUSTOM_NAME of the "
                 "MAILBOX row with that ID in the same file; all 153 rows matched one. "
                 "Conversation ID, Status, Content Synced and Used Protected Channel are "
                 "CONVERSATION_ID, STATUS, CONTENT_SYNCED and USED_PROTECTED_CHANNEL as stored. "
                 "Status was 33 on 83 rows, 32 on 68, 48 on 1 and 49 on 1; Content Synced was 0 "
                 "on 114 and 1 on 39; Used Protected Channel was 1 on 106 and 0 on 47. What "
                 "those values mean is not established. Device Registry ID is the name of the "
                 "folder under DeviceRegistry that holds the file, and each of the 4 images had "
                 "one such folder. The other columns of the table are not reported. SANITIZED_ID "
                 "held a distinct value on every row, in the same form as ID with its separators "
                 "changed. STATUS_VERSION, CONTENT_REQUESTED_BY_USER, "
                 "USED_NOTIFICATION_PRIORITY, RESEND_REQUESTED, RESEND_INTERVAL, "
                 "CONTENT_RESEND_INTERVAL, CONTENT_SYNCED_BECAUSE_USER_REQUESTED, "
                 "CONTENT_SYNCED_NOTIFICATION_PRIORITY, THREAD_SPECIFIC and "
                 "SPECIAL_MAILBOX_SPECIFIC were 0 on all 153 rows. The database is opened "
                 "read-only together with its write-ahead log; on cookbook_ios1751 every synced "
                 "message row is in the write-ahead log and the main file alone holds none. The "
                 "store was on 4 of the 23 sample_data images (cookbook_ios1751 with 21 rows, "
                 "hickman_ios13 and hickman_ios14 with 40 each, iphone11_ios17 with 52). The "
                 "other 19 have no NanoMail/registry.sqlite under mobile/Library/DeviceRegistry. "
                 "That this store belongs to a paired Apple Watch rests on issue #1876, which "
                 "describes DeviceRegistry as Apple Watch sync data; it is not sourced from "
                 "Apple documentation.",
        "paths": ('*/mobile/Library/DeviceRegistry/*/NanoMail/registry.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "mail",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 40 rows",
            "hickman_ios14": "iOS 14.3 | 40 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 52 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 21 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
    "appleWatchMailAccounts": {
        "name": "Apple Watch Mail Accounts",
        "description": "One row per row of SYNCED_ACCOUNT in the NanoMail registry under "
                       "DeviceRegistry.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-10",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "Apple Watch",
        "notes": "Display Name, Email Addresses, Username, Account ID, Local ID, Type "
                 "Identifier, Source Type and Should Archive are DISPLAY_NAME, EMAIL_ADDRESSES, "
                 "USERNAME, ID, LOCAL_ID, TYPE_IDENTIFIER, SOURCE_TYPE and SHOULD_ARCHIVE as "
                 "stored; a column the file's table does not have is left empty. Of the 4 "
                 "sample_data images that hold the store, 3 had one row each and "
                 "cookbook_ios1751 had none, while holding 1 mailbox and 21 synced messages. "
                 "Type Identifier had a value on 1 of the 3 rows (iphone11_ios17); the table has "
                 "no TYPE_IDENTIFIER column on hickman_ios13 and hickman_ios14. Source Type was "
                 "0 and Should Archive was 1 on all 3 rows, and what those values mean is not "
                 "established. DEFAULT_ADDRESS, EMAIL_ADDRESS_TOKEN and PCC_EMAIL_ADDRESS exist "
                 "only in the cookbook_ios1751 and iphone11_ios17 tables and were empty on the "
                 "one row there; they are not reported, nor are the resend columns. Device "
                 "Registry ID is the name of the folder under DeviceRegistry that holds the "
                 "file. The database is opened read-only together with its write-ahead log. The "
                 "other 19 images have no NanoMail/registry.sqlite under "
                 "mobile/Library/DeviceRegistry. That this store belongs to a paired Apple Watch "
                 "rests on issue #1876, which describes DeviceRegistry as Apple Watch sync data; "
                 "it is not sourced from Apple documentation.",
        "paths": ('*/mobile/Library/DeviceRegistry/*/NanoMail/registry.sqlite*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "mail",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 1 rows",
            "hickman_ios14": "iOS 14.3 | 1 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 1 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
    "appleWatchMailMailboxes": {
        "name": "Apple Watch Mail Mailboxes",
        "description": "One row per row of MAILBOX in the NanoMail registry under "
                       "DeviceRegistry.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-10",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "Apple Watch",
        "notes": "Custom Name, URL, Type, Filter Type, Sync Active, Sync Enabled, Mailbox ID and "
                 "Account ID are CUSTOM_NAME, URL, TYPE, FILTER_TYPE, SYNC_ACTIVE, SYNC_ENABLED, "
                 "ID and ACCOUNT_ID as stored. The 4 sample_data images that hold the store gave "
                 "21 rows (cookbook_ios1751 1, hickman_ios13 4, hickman_ios14 8, iphone11_ios17 "
                 "8). Type values seen were 0, 1, 2, 3, 4, 5 and 9, and Filter Type values were "
                 "0 and 15; what they mean is not established. Sync Active and Sync Enabled were "
                 "equal on all 21 rows: 1 on 4 rows and 0 on 17. URL was equal to Mailbox ID on "
                 "9 of the 21 rows. Account ID matched the ID of a SYNCED_ACCOUNT row in the "
                 "same file on 20 rows; the one that did not is on cookbook_ios1751, which has "
                 "no account row. SYNC_REQUESTED was 0 on all 21 rows and is not reported, nor "
                 "are ACCOUNT_LOCAL_ID and SYNC_REQUESTED_DATE. Device Registry ID is the name "
                 "of the folder under DeviceRegistry that holds the file. The database is opened "
                 "read-only together with its write-ahead log. The other 19 images have no "
                 "NanoMail/registry.sqlite under mobile/Library/DeviceRegistry. That this store "
                 "belongs to a paired Apple Watch rests on issue #1876, which describes "
                 "DeviceRegistry as Apple Watch sync data; it is not sourced from Apple "
                 "documentation.",
        "paths": ('*/mobile/Library/DeviceRegistry/*/NanoMail/registry.sqlite*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "mail",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 4 rows",
            "hickman_ios14": "iOS 14.3 | 8 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 8 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 1 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
}

import sqlite3

from scripts.ilapfuncs import (artifact_processor, convert_unix_ts_to_utc, logfunc,
                               open_sqlite_db_readonly)

_DB_NAME = 'registry.sqlite'


def _registries(context):
    """ Each matched registry.sqlite as (path, the folder name under DeviceRegistry). """
    for file_found in sorted(str(path) for path in context.get_files_found()):
        segments = file_found.replace('\\', '/').split('/')
        # The folder is read by position from the file, so a DeviceRegistry segment in the
        # examiner's own output path cannot be taken for it.
        if segments[-1] != _DB_NAME or segments[-4:-1:2] != ['DeviceRegistry', 'NanoMail']:
            continue
        yield file_found, segments[-3]


def _rows(file_found, table):
    """ Every row of table as a dictionary keyed by column name; [] when it cannot be read. """
    db = open_sqlite_db_readonly(file_found)
    if db is None:
        return []
    try:
        db.row_factory = sqlite3.Row
        return [dict(row) for row in db.execute(f'SELECT * FROM "{table}" ORDER BY rowid')]
    except sqlite3.Error as error:
        logfunc(f'{file_found}: {table} was not read: {error}')
        return []
    finally:
        db.close()


def _text(row, column):
    value = row.get(column)
    return '' if value is None else str(value)


def _table(context, table, columns):
    """ Rows of one table across every registry, as tuples of the named columns as text. """
    data_list = []
    source_paths = []
    for file_found, registry_id in _registries(context):
        source_paths.append(file_found)
        for row in _rows(file_found, table):
            data_list.append(tuple(_text(row, column) for column in columns) + (registry_id,))
    return data_list, '\n'.join(source_paths)


@artifact_processor
def appleWatchMailSyncedMessages(context):
    """ See artifact description """
    data_headers = (('Date Received', 'datetime'), 'Message ID', 'Mailbox ID', 'Mailbox Name',
                    'Conversation ID', 'Status', 'Content Synced', 'Used Protected Channel',
                    'Device Registry ID')
    data_list = []
    source_paths = []
    for file_found, registry_id in _registries(context):
        source_paths.append(file_found)
        names = {row.get('ID'): _text(row, 'CUSTOM_NAME') for row in _rows(file_found, 'MAILBOX')}
        for row in _rows(file_found, 'SYNCED_MESSAGE'):
            received = row.get('DATE_RECEIVED')
            is_number = isinstance(received, (int, float)) and not isinstance(received, bool)
            data_list.append((
                convert_unix_ts_to_utc(received) if is_number and received else '',
                _text(row, 'ID'), _text(row, 'MAILBOX_ID'), names.get(row.get('MAILBOX_ID'), ''),
                _text(row, 'CONVERSATION_ID'), _text(row, 'STATUS'), _text(row, 'CONTENT_SYNCED'),
                _text(row, 'USED_PROTECTED_CHANNEL'), registry_id))
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def appleWatchMailAccounts(context):
    """ See artifact description """
    data_headers = ('Display Name', 'Email Addresses', 'Username', 'Account ID', 'Local ID',
                    'Type Identifier', 'Source Type', 'Should Archive', 'Device Registry ID')
    data_list, source_path = _table(context, 'SYNCED_ACCOUNT', (
        'DISPLAY_NAME', 'EMAIL_ADDRESSES', 'USERNAME', 'ID', 'LOCAL_ID', 'TYPE_IDENTIFIER',
        'SOURCE_TYPE', 'SHOULD_ARCHIVE'))
    return data_headers, data_list, source_path


@artifact_processor
def appleWatchMailMailboxes(context):
    """ See artifact description """
    data_headers = ('Custom Name', 'URL', 'Type', 'Filter Type', 'Sync Active', 'Sync Enabled',
                    'Mailbox ID', 'Account ID', 'Device Registry ID')
    data_list, source_path = _table(context, 'MAILBOX', (
        'CUSTOM_NAME', 'URL', 'TYPE', 'FILTER_TYPE', 'SYNC_ACTIVE', 'SYNC_ENABLED', 'ID',
        'ACCOUNT_ID'))
    return data_headers, data_list, source_path
