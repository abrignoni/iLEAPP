__artifacts_v2__ = {
    "suggestionsUrls": {
        "name": "Suggestions Store - URLs",
        "description": "Rows of the urls table in mobile/Library/Suggestions/entities.db: each URL with its "
                       "time, the app bundle ID and the received-from handle, and, for Messages rows, whether "
                       "the document ID is a message guid in sms.db.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-30",
        "last_update_date": "2026-10-30",
        "requirements": "none",
        "category": "Suggestions",
        "notes": "Reads the urls table of mobile/Library/Suggestions/entities.db, with its -wal, one row "
                 "per table row; the table was absent from the iOS 12 image ctf2020_ios12. Time is "
                 "seconds_from_1970 and Document Time is document_seconds_from_1970, both read as Unix "
                 "seconds; every tested value was ten digits, the shape the shared converter reads as "
                 "seconds. On the tested images every row came from com.apple.MobileSMS (117 rows) or "
                 "com.apple.mobilemail (105) in App (bundle ID). For the Messages rows, Document ID (as "
                 "stored) is compared with the guid column of the message table in "
                 "mobile/Library/SMS/sms.db: Message In sms.db is Yes when a message with that guid is "
                 "present and No when none is. It matched on 105 of the 117 tested Messages rows, and on "
                 "all 105 Time was within 60 seconds of that message's date (within 6 seconds on 98). No "
                 "does not establish that a message was deleted; it means no message with that guid is in "
                 "the sms.db that was read. On the 12 tested No rows the document ID had a prefix before "
                 "a UUID, unlike the 105 matched rows. The column is blank for other apps and when no "
                 "sms.db was read. What Document Time records is not established: it was within 60 "
                 "seconds of Time on 120 of the 222 tested rows. Received From (as stored) is "
                 "received_from_handle and Group ID (as stored) is group_id; on the Messages rows the "
                 "group ID began with SMS, iMessage, RCS, any or attachmentDomain, and on the Mail rows "
                 "it was a UUID followed by a dot and a number. Document ID (as stored) for Mail rows is "
                 "not resolved. Flags (as stored) held 16, 0, 17 or 1, whose meanings are not "
                 "established. The other tables of entities.db (contact details, entities, email metadata "
                 "and others) and snippets.db are not read here.",
        "paths": ('*/mobile/Library/Suggestions/entities.db*',
                  '*/mobile/Library/SMS/sms.db*'),
        "output_types": "standard",
        "artifact_icon": "link",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 6 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 31 rows",
            "belkactf6_tar": "iOS 16.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 2 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 11 rows",
            "falken_ios26": "iOS 26.2.1 | 49 rows",
            "felix23_ios16": "iOS 16.5 | 5 rows",
            "felix_ios17": "iOS 17.6.1 | 9 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 2 rows",
            "hc_ios18_7": "iOS 18.7.8 | 3 rows",
            "hc_ios26": "iOS 26.5.2 | 1 row",
            "hexordia_ios1651": "iOS 16.5.1 | 4 rows",
            "hickman_ios13": "iOS 13.3.1 | 28 rows",
            "hickman_ios14": "iOS 14.3 | 7 rows",
            "hickman_ios15": "iOS 15.3.1 | 10 rows",
            "iphone11_ios17": "iOS 17.3 | 9 rows",
            "iphone12_ios18": "iOS 18.7 | 4 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 14 rows",
            "jess_ios15": "iOS 15.0.2 | 7 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 20 rows",
        },
    }
}

import os

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, does_table_exist_in_db, \
    get_sqlite_db_records

_MESSAGES = 'com.apple.MobileSMS'


def _named(context, name):
    return sorted({str(p) for p in context.get_files_found() if os.path.basename(str(p)) == name})


def _time(value):
    """Unix seconds as a UTC datetime; blank for no value or 0."""
    if not value or isinstance(value, bool) or not isinstance(value, (int, float)):
        return ''
    return convert_unix_ts_to_utc(value)


def _text(value):
    return '' if value is None else value


@artifact_processor
def suggestionsUrls(context):
    data_headers = (
        ('Time', 'datetime'), ('Document Time', 'datetime'), 'URL', 'Received From (as stored)', 'App (bundle ID)',
        'Group ID (as stored)', 'Document ID (as stored)', 'Message In sms.db', 'Title', 'Document Title',
        'Flags (as stored)')
    guids, sms_read = None, []
    for path in _named(context, 'sms.db'):
        if does_table_exist_in_db(path, 'message'):
            guids = (guids or set()) | {row['guid'] for row in get_sqlite_db_records(path, 'SELECT guid FROM message')}
            sms_read.append(path)
    data_list, read = [], []
    for path in _named(context, 'entities.db'):
        if not does_table_exist_in_db(path, 'urls'):
            continue
        read.append(path)
        rows = get_sqlite_db_records(
            path, 'SELECT seconds_from_1970, document_seconds_from_1970, url, received_from_handle, bundle_id, '
                  'group_id, doc_id, title, document_title, flags FROM urls ORDER BY seconds_from_1970, id')
        for row in rows:
            in_sms = ''
            if row['bundle_id'] == _MESSAGES and guids is not None:
                in_sms = 'Yes' if row['doc_id'] in guids else 'No'
            data_list.append((
                _time(row['seconds_from_1970']), _time(row['document_seconds_from_1970']), _text(row['url']),
                _text(row['received_from_handle']), _text(row['bundle_id']), _text(row['group_id']),
                _text(row['doc_id']), in_sms, _text(row['title']), _text(row['document_title']),
                _text(row['flags'])))
    if data_list:
        read.extend(sms_read)
    return data_headers, data_list, '\n'.join(read)
