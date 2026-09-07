__artifacts_v2__ = {
    "coverme_ios_numbers": {
        "name": "CoverMe - Numbers",
        "description": "Second phone numbers the CoverMe app holds, with the label and the other "
                       "values stored against each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "CoverMe",
        "notes": "One row per row of VirtualNumberTable in Documents/miliao.db. The app names "
                 "every column in this database fieldN, so a column's meaning is taken from the "
                 "values it holds rather than from its name, and any column whose meaning the "
                 "values did not settle is reported under the app's own column name and left as "
                 "stored. Number is field1, which held a single eleven digit number on the one "
                 "tested image and is the same number every call row carries in field5, so the "
                 "number table and the call rows name the same number. Label is field9. Two "
                 "fields hold Unix millisecond values and are reported both as stored and as UTC "
                 "times; read that way they fall in April 2020 and March 2021, which brackets the "
                 "period the image covers, but which of the two is an issue date and which an "
                 "expiry was not established, so neither is labelled. field2, field3 and field35 "
                 "are reported as stored. One of the 26 registered iOS corpora carries the store, "
                 "with one row.",
        "paths": ('*/Containers/Data/Application/*/Documents/miliao.db*',),
        "output_types": "standard",
        "artifact_icon": "hash",
        "sample_data": {
                           "hickman_ios14": "iOS 14.3 | CoverMe | 1 row",
                       },
    },
    "coverme_ios_calls": {
        "name": "CoverMe - Call History",
        "description": "Calls the CoverMe app recorded against a second number, with the other "
                       "number, a name and a duration.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "CoverMe",
        "notes": "One row per row of KVirtualNumberCallHistoryTable in Documents/miliao.db. The "
                 "app names every column in this database fieldN, so a column's meaning is taken "
                 "from the values it holds rather than from its name, and any column whose "
                 "meaning the values did not settle is reported under the app's own column name "
                 "and left as stored. Second Number is field5, which equals the one number in the "
                 "app's own number table; Other Number is field6; Name On The Row is field7, "
                 "which held a display name on both rows of the one tested image; Duration is "
                 "field11, which held a value of the form minutes and seconds. Timestamp is "
                 "field10, Unix seconds stored as text, reported in UTC, and both rows fall on "
                 "the same day inside the period the image covers. **Which end placed the call "
                 "was not established**, so no direction is reported and the flag columns are "
                 "left as stored. The image held two rows, both between the same pair of numbers, "
                 "of 1 minute 46 seconds and 1 minute 56 seconds.",
        "paths": ('*/Containers/Data/Application/*/Documents/miliao.db*',),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
                           "hickman_ios14": "iOS 14.3 | CoverMe | 2 rows",
                       },
    },
    "coverme_ios_messages": {
        "name": "CoverMe - Messages",
        "description": "Message records the CoverMe app holds, with the number on the row and any "
                       "attachment path it names.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "CoverMe",
        "notes": "One row per row of the sms table in Documents/miliao.db. The app names every "
                 "column in this database fieldN, so a column's meaning is taken from the values "
                 "it holds rather than from its name, and any column whose meaning the values did "
                 "not settle is reported under the app's own column name and left as stored. "
                 "**The message bodies are encrypted and are not decoded here.** field4 holds "
                 "base64 that differs on every row and is reported as stored so an examiner can "
                 "take it elsewhere; field3 holds base64 that is constant for each of the two "
                 "numbers, so it is keyed to the number rather than to the message. Number On The "
                 "Row is field2. It alternates between the number in the app's own number table "
                 "and one other number, 7 rows and 5 rows on the one tested image, and **which "
                 "end of the message that column names was not established**, so no direction is "
                 "reported and the flag columns are left as stored. Timestamp is field5, Unix "
                 "seconds, reported in UTC, and all twelve rows fall within about seventy minutes "
                 "of one day inside the period the image covers. Three rows name an attachment "
                 "path. Two of them sit under Documents/uploadMedia and both resolved to a file "
                 "in the same app container, so the byte sizes reported are of the files "
                 "themselves; the third names a folder under Documents whose name is a hash, "
                 "which this artifact does not gather, so it is reported by path alone. **No "
                 "picture is shown**: the attachment files that did resolve begin with the same "
                 "four bytes as each other and carry no signature of any image or video format, "
                 "so they are reported by path, presence and size and are not decoded. A third "
                 "file sits in the same upload folder under a longer name that no row names. Five "
                 "tables in this database are read by nothing here and are named so the omission "
                 "is visible. field6 (as stored) held the value 1 on all twelve rows, too few "
                 "values to say what it distinguishes. The five tables read by nothing here are: "
                 "the message table, whose rows carry button labels such as Learn More and are "
                 "the app's own screen content rather than a conversation; and the keychain, key, "
                 "password and successful login tables, which hold key material or ciphertext. "
                 "**No key material is reported.**",
        "paths": ('*/Containers/Data/Application/*/Documents/miliao.db*',
                  '*/Containers/Data/Application/*/Documents/uploadMedia/*'),
        "output_types": "standard",
        "artifact_icon": "message-square",
        "sample_data": {
                           "hickman_ios14": "iOS 14.3 | CoverMe | 12 rows",
                       },
    },
    "coverme_ios_login_days": {
        "name": "CoverMe - Login Days",
        "description": "Days the CoverMe app recorded a login on, one row per day it stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "CoverMe",
        "notes": "One row per row of loginTimesTable in Documents/miliao.db. The app names every "
                 "column in this database fieldN, so a column's meaning is taken from the values "
                 "it holds rather than from its name, and any column whose meaning the values did "
                 "not settle is reported under the app's own column name and left as stored. Day "
                 "is field2, which held a date written as text on all three rows of the one "
                 "tested image, so it is reported as the app stored it rather than converted. The "
                 "three days fall inside the period the image covers and two of them are more "
                 "than a fortnight before the day the messages and calls are on, so the table "
                 "reaches back further than the message table does. The row carries no time of "
                 "day and no count, so a row says the app recorded a login on that day and "
                 "nothing more, and a day that is absent is not evidence that no login happened "
                 "on it. field1 (as stored) held the value 1 on all three rows, too few values to "
                 "say what it distinguishes.",
        "paths": ('*/Containers/Data/Application/*/Documents/miliao.db*',),
        "output_types": "standard",
        "artifact_icon": "log-in",
        "sample_data": {
                           "hickman_ios14": "iOS 14.3 | CoverMe | 3 rows",
                       },
    },
}

import os
import re
from datetime import datetime, timezone

from scripts.ilapfuncs import (artifact_processor, does_table_exist_in_db,
                               get_sqlite_db_records, logfunc)

_CONTAINER = re.compile(r'(.*/Containers/Data/Application/[^/]+)/', re.I)


def _stores(files_found):
    '''Every miliao.db among the matches, directories and sidecars skipped.'''
    seen = []
    for found in files_found:
        path = str(found)
        if os.path.isdir(path) or path.endswith(('-wal', '-shm')):
            continue
        if os.path.basename(path) == 'miliao.db' and path not in seen:
            seen.append(path)
    return seen


def _container(path):
    '''The app data container a file sits in, or '' when it is not under one.'''
    match = _CONTAINER.match(str(path).replace('\\', '/'))
    return match.group(1) if match else ''


def _upload_files(files_found):
    '''{(container, file name): path} for every file staged from an upload folder.'''
    index = {}
    for found in files_found:
        path = str(found)
        if os.path.isdir(path):
            continue
        if '/Documents/uploadMedia/' in path.replace('\\', '/'):
            index.setdefault((_container(path), os.path.basename(path)), path)
    return index


def _rows(path, table, columns):
    '''Rows of a table, or nothing when the store does not have it.'''
    if not does_table_exist_in_db(path, table):
        return []
    try:
        return list(get_sqlite_db_records(path, f'SELECT {columns} FROM {table}'))
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'CoverMe: could not read {table}: {error}')
        return []


def _text(value):
    '''A stored value as text, with a stored null read as absent.'''
    return '' if value is None else str(value)


def _unix_to_utc(value):
    '''Unix seconds, stored as a number or as text, to an aware UTC datetime, or ''.'''
    if value in (None, '', 0, '0'):
        return ''
    try:
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _unix_ms_to_utc(value):
    '''Unix milliseconds to an aware UTC datetime, or ''.'''
    if value in (None, '', 0, '0'):
        return ''
    try:
        return datetime.fromtimestamp(float(value) / 1000, tz=timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


@artifact_processor
def coverme_ios_numbers(context):
    data_list = []
    sources = []
    for source_path in _stores(context.get_files_found()):
        sources.append(source_path)
        for (number, area, label, first_time, second_time, plan, state) in _rows(
                source_path, 'VirtualNumberTable',
                'VirtualNumber_field1, VirtualNumber_field2, VirtualNumber_field9, '
                'VirtualNumber_field6, VirtualNumber_field8, VirtualNumber_field35, '
                'VirtualNumber_field3'):
            data_list.append((
                _unix_ms_to_utc(first_time), _unix_ms_to_utc(second_time),
                _text(number), _text(label), _text(area), _text(plan), _text(state),
                _text(first_time), _text(second_time),
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)
    data_headers = (
        ('field6 as a Unix millisecond time', 'datetime'),
        ('field8 as a Unix millisecond time', 'datetime'),
        'Number', 'Label (field9)', 'field2 (as stored)', 'field35 (as stored)',
        'field3 (as stored)', 'field6 (as stored)', 'field8 (as stored)',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def coverme_ios_calls(context):
    data_list = []
    sources = []
    for source_path in _stores(context.get_files_found()):
        sources.append(source_path)
        for (stamp, own, other, name, duration, row_id, flag2, flag8,
             flag12, ident) in _rows(
                source_path, 'KVirtualNumberCallHistoryTable',
                'VirtualNumberHistory_field10, VirtualNumberHistory_field5, '
                'VirtualNumberHistory_field6, VirtualNumberHistory_field7, '
                'VirtualNumberHistory_field11, VirtualNumberHistory_field1, '
                'VirtualNumberHistory_field2, VirtualNumberHistory_field8, '
                'CallHistory_field12, CallHistory_field13'):
            data_list.append((
                _unix_to_utc(stamp), _text(own), _text(other), _text(name), _text(duration),
                _text(row_id), _text(flag2), _text(flag8), _text(flag12), _text(ident),
                _text(stamp),
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)
    data_headers = (
        ('Timestamp', 'datetime'), ('Second Number', 'phonenumber'),
        ('Other Number', 'phonenumber'), 'Name On The Row', 'Duration',
        'field1 (as stored)', 'field2 (as stored)', 'field8 (as stored)',
        'field12 (as stored)', 'field13 (as stored)', 'Timestamp (as stored)',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def coverme_ios_messages(context):
    data_list = []
    sources = []
    files_found = context.get_files_found()
    on_disk = _upload_files(files_found)
    for source_path in _stores(files_found):
        sources.append(source_path)
        container = _container(source_path)
        for (stamp, number, body, token, attachment, second_path, row_id, flag6, flag7,
             flag8, flag22, size) in _rows(
                source_path, 'sms',
                'SMS_field5, SMS_field2, SMS_field4, SMS_field3, SMS_field10, SMS_field20, '
                'SMS_field1, SMS_field6, SMS_field7, SMS_field8, SMS_field22, SMS_field23'):
            name = os.path.basename(_text(attachment).rstrip('/')) if attachment else ''
            path = on_disk.get((container, name)) if name else None
            present, on_disk_size = ('', '')
            if name:
                present = 'Yes' if path else 'No'
                if path:
                    try:
                        on_disk_size = str(os.path.getsize(path))
                    except OSError:
                        on_disk_size = ''
            data_list.append((
                _unix_to_utc(stamp), _text(number), _text(attachment), present, on_disk_size,
                _text(second_path), _text(body), _text(token), _text(row_id), _text(flag6),
                _text(flag7), _text(flag8), _text(flag22), _text(size), _text(stamp),
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)
    data_headers = (
        ('Timestamp', 'datetime'), ('Number On The Row', 'phonenumber'), 'Attachment Path',
        'Attachment Present', 'Attachment Bytes', 'Second Attachment Path',
        'Message Body (encrypted, as stored)', 'Number Token (encrypted, as stored)',
        'field1 (as stored)', 'field6 (as stored)', 'field7 (as stored)',
        'field8 (as stored)', 'field22 (as stored)', 'field23 (as stored)',
        'Timestamp (as stored)',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def coverme_ios_login_days(context):
    data_list = []
    sources = []
    for source_path in _stores(context.get_files_found()):
        sources.append(source_path)
        for (day, first) in _rows(
                source_path, 'loginTimesTable',
                'LoginTimesData_field2, LoginTimesData_field1'):
            data_list.append((_text(day), _text(first)))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)
    data_headers = (('Day', 'date'), 'field1 (as stored)')
    return data_headers, data_list, '\n'.join(sources)
