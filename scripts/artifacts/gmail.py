__artifacts_v2__ = {
    "gmailOfflineSearch": {
        "name": "Gmail - Offline Search",
        "description": "Parses Gmail offline search content",
        "author": "@KevinPagano3",
        "creation_date": "2024-10-15",
        "version": "0.0.2",
        "date": "2024-03-20",
        "last_update_date": "2026-08-24",
        "requirements": "none",
        "category": "Gmail",
        "notes": "Column meanings for the offline_search_content FTS shadow table were inferred from observed content; the FTS virtual-table declaration in the database can corroborate the mapping. An account directory under Library/Application Support/data/ can carry its own searchsqlitedb; every matched store is read, in sorted path order, and the Account column reports the name of the account directory the row's store sits under (email-address-shaped in tested images). Not every account directory holds one: in the tested two-account image only one account had an offline search store. A store that cannot be opened or queried is logged and skipped without dropping the other accounts' rows.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/data/*/searchsqlitedb*',),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "search",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | Gmail - Email by Google 6.0.250915 | 176 rows",
            "iphone11_ios17": "iOS 17.3 | Gmail - Email by Google 6.0.231127 | 321 rows",
            "iphone14plus_ios18": "iOS 18.0 | Gmail - Email by Google 6.0.251201 | 18 rows",
            "otto_ios17": "iOS 17.5.1 | Gmail - Email by Google 6.0.240729 | 305 rows",
            "abe_ios16": "iOS 16.5 | Gmail - Email by Google 6.0.230528 | 430 rows",
            "jess_ios15": "iOS 15.0.2 | Gmail - Email by Google 6.0.211226 | 81 rows",
            "magnet_ios16": "iOS 16.1.1 | Gmail - Email by Google 6.0.221127 | 21 rows",
        }
    },
    "gmailLabelDetails": {
        "name": "Gmail - Label Details",
        "description": "Parses Gmail label details",
        "author": "@KevinPagano3",
        "creation_date": "2024-10-15",
        "last_update_date": "2026-08-24",
        "version": "0.0.2",
        "date": "2024-03-20",
        "requirements": "none",
        "category": "Gmail",
        "notes": "One row per label per account store. Every account directory under Library/Application Support/data/ held its own sqlitedb in the tested images; every matched store is read, in sorted path order, and the Account column reports the name of the account directory the row's store sits under (email-address-shaped in tested images). A store that cannot be opened or queried is logged and skipped without dropping the other accounts' rows. In the tested two-account image one account's label rows lived entirely in the WAL sidecar, so the sidecars must travel with the evidence. Label values are reported as stored.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/data/*/sqlitedb*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "tag",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | com.google.Gmail | 30 rows",
            "dexter_ios18": "iOS 18.3.2 | Gmail - Email by Google 6.0.250915 | 35 rows",
            "iphone11_ios17": "iOS 17.3 | Gmail - Email by Google 6.0.231127 | 31 rows",
            "iphone14plus_ios18": "iOS 18.0 | Gmail - Email by Google 6.0.251201 | 33 rows",
            "otto_ios17": "iOS 17.5.1 | Gmail - Email by Google 6.0.240729 | 33 rows",
            "abe_ios16": "iOS 16.5 | Gmail - Email by Google 6.0.230528 | 31 rows",
            "jess_ios15": "iOS 15.0.2 | Gmail - Email by Google 6.0.211226 | 30 rows",
            "magnet_ios16": "iOS 16.1.1 | Gmail - Email by Google 6.0.221127 | 59 rows across 2 account stores",
        }
    }
}

import os
import sqlite3

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly, convert_ts_human_to_utc


def _read_account_stores(context, store_name, query, label):
    """Yields (account, store path, rows) for every matched Gmail store.

    The Gmail container keeps one store per account directory under
    Library/Application Support/data/, so files_found can hold several,
    plus their -wal/-shm sidecars. Stores are read in sorted path order so
    the output cannot depend on the platform's directory listing order, and
    each store is attributed to the account directory it sits under. A store
    that cannot be opened or queried is logged and skipped so it cannot cost
    the other accounts their rows.
    """
    stores = sorted(str(p) for p in context.get_files_found()
                    if os.path.basename(str(p)) == store_name)
    for store_path in stores:
        account = os.path.basename(os.path.dirname(store_path))
        db = open_sqlite_db_readonly(store_path)
        if db is None:
            logfunc(f'Unable to open Gmail {label} store for account {account}')
            continue
        try:
            cursor = db.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
        except sqlite3.Error as ex:
            logfunc(f'Unable to read Gmail {label} store for account {account}: {ex}')
            continue
        finally:
            db.close()
        yield account, store_path, rows


@artifact_processor
def gmailOfflineSearch(context):
    data_list = []
    source_paths = []

    query = '''
    SELECT
        datetime(c0/1000,'unixepoch'),
        c3 AS 'Sender',
        c4 AS 'Receiver',
        c5 AS 'CC',
        c6 AS 'BCC',
        c7 AS 'Subject',
        c8 AS 'Body',
        c1 AS 'Thread ID',
        c2 AS 'Message ID'
    FROM offline_search_content
    '''

    for account, store_path, rows in _read_account_stores(
            context, 'searchsqlitedb', query, 'offline search'):
        source_paths.append(store_path)
        for row in rows:
            timestamp = convert_ts_human_to_utc(row[0])

            sender = row[1]
            sender_split = [sender_split.strip() for sender_split in sender.split(',')]

            if len(sender_split) < 2:
                sender_title = sender_split[0]
                sender_email = ''
            else:
                sender_title = sender_split[0]
                sender_email = sender_split[1]

            data_list.append((timestamp, account, sender_title, sender_email, row[2],
                              row[3], row[4], row[5], row[6], row[7], row[8]))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Account',
        'Sender Name',
        'Sender Email',
        'Receiver',
        'CC',
        'BCC',
        'Subject',
        'Body',
        'Thread ID',
        'Message ID'
    )

    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def gmailLabelDetails(context):
    data_list = []
    source_paths = []

    query = '''
    SELECT
        label_server_perm_id,
        unread_count,
        total_count,
        unseen_count
    FROM label_counts
    ORDER BY label_server_perm_id
    '''

    for account, store_path, rows in _read_account_stores(
            context, 'sqlitedb', query, 'label'):
        source_paths.append(store_path)
        for row in rows:
            data_list.append((account, row[0], row[1], row[2], row[3]))

    data_headers = ('Account', 'Label', 'Unread Count', 'Total Count', 'Unseen Count')

    return data_headers, data_list, '\n'.join(source_paths)
