__artifacts_v2__ = {
    "textnow_ios_messages": {
        "name": "TextNow - Messages",
        "description": "Messages held in the TextNow account store, with the picture "
                       "each picture message points at where the app cached it.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-07",
        "last_update_date": "2026-09-07",
        "requirements": "none",
        "category": "TextNow",
        "notes": "One row per row of ZTMOINTERACTION that carries no call identifier, "
                 "in the Core Data store the app keeps at Documents/<account "
                 "id><username>. The store is named for the account it belongs to, so "
                 "it cannot be matched on its name: the glob accepts any file whose "
                 "name starts with ten digits and the module then reads only the ones "
                 "that are SQLite and carry the app's own ZTMOACCOUNTINFO table. That "
                 "guard was measured rather than reasoned about. On one tested image "
                 "another app's store matched the same glob, was staged, and produced "
                 "no rows. The data lives in the write-ahead log. Of the eleven tables "
                 "that hold rows on the two tested images, the eight that hold app data "
                 "return zero rows when the database is read without its log, "
                 "ZTMOINTERACTION, ZTMOCONVERSATION, ZTMOCONTACTVALUE, ZTMOABCONTACT "
                 "and ZTMOSERVERCONTACT among them, and only the three Core Data "
                 "bookkeeping tables survive in the database itself. The sidecar is "
                 "therefore not optional and the glob picks it up. Message Time is "
                 "ZLOCALTIMESTAMP and Remote Time is ZREMOTETIMESTAMP, both Core Data "
                 "times, seconds since 2001, reported in UTC. They are not the same "
                 "reading: on the iOS 14.3 image four rows carry a remote time from "
                 "October 2020 against a local time in February 2021. Direction reads "
                 "the app's stored ZDIRECTION, 2 as outgoing and 1 as incoming, and "
                 "that reading is supported by the store rather than assumed: across "
                 "the 64 messages, none of the 9 outgoing rows carries an author name "
                 "while 50 of the 55 incoming rows do, and the same two values appear "
                 "on the call rows where the app's separate call history names one as "
                 "dialled. Sender takes the stored author name, and on an outgoing row "
                 "it takes the address the store marks as the account's own, since the "
                 "app records no author for its own messages. It is blank on 5 rows, "
                 "which are incoming rows the app left without an author. Picture is "
                 "filled from the app's own image cache. A picture message stores the "
                 "address the picture was fetched from as its text, and the cache file "
                 "is named for the MD5 of that address, which is the naming SDWebImage "
                 "uses (SDDiskCacheFileNameForKey in SDWebImage/Core/SDDiskCache.m at "
                 "8a1be70a). That is a link the app recorded, not a match on size or "
                 "time, and it resolved on 4 of the 4 rows that carry thumbnail "
                 "dimensions. The bytes are checked before anything is rendered and "
                 "only a file carrying an image signature is attached; all four were "
                 "JPEG. The pairing is confirmed a second way: the message row records "
                 "the width and height of the picture it points at, and on all 4 of "
                 "them those two numbers equal the pixel dimensions of the file the "
                 "address resolved to, which the store and the file record "
                 "independently. The cache is accounted for rather than sampled. It "
                 "holds 11 entries across the two images, all JPEG, of which 4 are "
                 "named by a message. Of the 7 that are not, 2 carry the same pixel "
                 "dimensions as a picture a message already names, so they are a second "
                 "cached copy of that photograph under another address, and the "
                 "remaining 5 are 320 pixels square or smaller, the size the app uses "
                 "for avatars and its own artwork. No picture in the cache is a "
                 "photograph that no message accounts for. That cache folder is named "
                 "for the image library rather than for the app, so an entry is only "
                 "used for a store in the same container. Conversation is the name or "
                 "address the conversation is with, and it is blank on 30 rows because "
                 "the store left them with no conversation link; all 30 are on the iOS "
                 "13.3.1 image and are the app's own inbox and marketing messages, "
                 "which carry a numeric author identifier and, on eleven of them, a "
                 "local path to an image a marketing library had cached rather than "
                 "message text. Two further rows carry such a path and do have a "
                 "conversation link, so thirteen rows in all hold one. Deleted State is "
                 "reported as stored and is 0 on 60 rows and 2 on 4; the four rows "
                 "marked 2 still hold their full text. Read State, Send Status and "
                 "Image Type are reported as stored and are not translated. Image Type "
                 "is blank on 47 rows. Thumbnail Width and Height are filled only on "
                 "the 4 picture rows. The store also holds ZTMOSIPDATA, "
                 "ZTMOBLOCKEDCONTACT, ZTMOCALLERIDENTRY, ZTMOPURCHASETRANSACTION, "
                 "ZTMOQOSTESTPROFILE and ZTMOQOSTESTSERVER, all empty on both tested "
                 "images, and Documents/ILDRates.sqlite, which is a downloaded table of "
                 "international dialling rates and is read by nothing here.",
        "paths": ('*/Containers/Data/Application/*/Documents/[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]*',
                  '*/Containers/Data/Application/*/Documents/com.hackemist.SDWebImageCache.default/*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
                         "sample_data": {
                                            "hickman_ios13": "iOS 13.3.1 | TextNow 20.10.0 | 49 rows",
                                            "hickman_ios14": "iOS 14.3 | TextNow 21.3.0 | 15 rows",
                                        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Message Time",
                "senderColumn": "Sender",
                "mediaColumn": "Picture",
            }
        },
    },
    "textnow_ios_calls": {
        "name": "TextNow - Calls",
        "description": "Calls held in the TextNow account store, with the matching row "
                       "from the calling library's own call history beside each one.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-07",
        "last_update_date": "2026-09-07",
        "requirements": "none",
        "category": "TextNow",
        "notes": "One row per row of ZTMOINTERACTION that carries a call identifier. "
                 "Call Start comes out of that identifier, which the app writes as the "
                 "other number and the call's own Core Data time joined by a hyphen, "
                 "and Recorded At is the row's ZLOCALTIMESTAMP. They are not the same "
                 "instant: across the 4 calls the row time follows the start by between "
                 "0.1 and 4.2 seconds. The columns whose names begin with Call History "
                 "come from eventHistory.db, a separate database in the same container "
                 "that belongs to the calling library the app embeds rather than to the "
                 "app. The two are joined on the time inside the call identifier, which "
                 "is that database's own Events.timestamp, so the link is recorded "
                 "rather than inferred, and it matched on 4 of 4 calls. Each database "
                 "holds exactly two calls per image and none was left unmatched. "
                 "Because eventHistory.db is the library's and not the app's, an entry "
                 "is only used for a store found in the same container. Duration and "
                 "Call History Duration are two separate recordings of the same call "
                 "and they disagree slightly, the app's own row being shorter by less "
                 "than a tenth of a second on all four, so both are reported rather "
                 "than one being chosen. Direction reads ZDIRECTION the same way the "
                 "messages do, and here the second database corroborates it: the 2 rows "
                 "read as outgoing are the ones it records with a dial action and no "
                 "sender, and the 2 read as incoming are the ones whose sender is the "
                 "other number. Call History Dial Action is therefore blank on 2 rows "
                 "by the same token. Call History Result holds the library's own codes "
                 "and is reported as stored, without translation, because no source for "
                 "their meaning was found; on the tested images it reads 16 on the two "
                 "outgoing calls and 1 on the two incoming ones. Status is the app's "
                 "own value and reads 4 on all 4 rows. Call ID and Call History Call ID "
                 "are the two stores' separate identifiers for the same call and they "
                 "do not match each other. A call recorded in eventHistory.db with no "
                 "matching row in the account store would not be reported here; on the "
                 "tested images there were none.",
        "paths": ('*/Containers/Data/Application/*/Documents/[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]*',
                  '*/Containers/Data/Application/*/Library/Application Support/eventHistory.db*'),
        "output_types": "standard",
        "artifact_icon": "phone-call",
                         "sample_data": {
                                            "hickman_ios13": "iOS 13.3.1 | TextNow 20.10.0 | 2 rows",
                                            "hickman_ios14": "iOS 14.3 | TextNow 21.3.0 | 2 rows",
                                        },
    },
    "textnow_ios_contacts": {
        "name": "TextNow - Contacts",
        "description": "Addresses and names the TextNow account store holds, for the "
                       "account itself, for the correspondents it has conversations "
                       "with and for the service's own addresses.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-07",
        "last_update_date": "2026-09-07",
        "requirements": "none",
        "category": "TextNow",
        "notes": "One row per row of ZTMOCONTACTVALUE. Contact Value is the address as "
                 "stored, which is a telephone number on some rows and an email address "
                 "or a service address on others. Account Own Address reads Yes on the "
                 "2 rows the store marks with ZCONTACTISSELF, one per image, and those "
                 "rows hold the account's own TextNow address. Address Book Name comes "
                 "from ZTMOABCONTACT through the join table Core Data keeps between the "
                 "two. That table and its two columns are named for the numbers Core "
                 "Data gave the entities, and those numbers move between releases, so "
                 "the table is found by shape rather than by a name written into this "
                 "module. Two address book rows point at one address on the iOS 14.3 "
                 "image, so two rows there list that name twice over. The column is "
                 "blank on 8 of 16 rows. Contact Name is the name the app itself holds "
                 "and is blank on 13 rows. Service Contact Name and Service Contact "
                 "Picture Key come from ZTMOSERVERCONTACT and mark the rows that are "
                 "the service's own addresses rather than a person's. In Network is "
                 "reported as stored and is blank on 7 rows. Conversation names the "
                 "conversation the address is attached to and is blank on 9 rows, which "
                 "are addresses the store holds without one. Rows are addresses the app "
                 "knows about, not a list of the device's contacts: the device address "
                 "book itself is not read here.",
        "paths": ('*/Containers/Data/Application/*/Documents/[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "user",
                         "sample_data": {
                                            "hickman_ios13": "iOS 13.3.1 | TextNow 20.10.0 | 8 rows",
                                            "hickman_ios14": "iOS 14.3 | TextNow 21.3.0 | 8 rows",
                                        },
    },
    "textnow_ios_account": {
        "name": "TextNow - Account",
        "description": "The TextNow account the store belongs to, with the number "
                       "assigned to it and its service settings.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-07",
        "last_update_date": "2026-09-07",
        "requirements": "none",
        "category": "TextNow",
        "notes": "One row per ZTMOACCOUNTINFO row, which held a single row on each of "
                 "the 2 tested images that carry the store. TextNow Number is the "
                 "number the service had assigned to the account when the store was "
                 "written, and it differs between the two images, so it is not a fixed "
                 "property of the account. Username, Email and Name are the account's "
                 "own registration values, and User ID and User ID (Hex) are the "
                 "service's identifiers for it; both images carry the same account. "
                 "Record Updated, Server Record Time, Wallet Updated and Ad Removal "
                 "Expiry are Core Data times, seconds since 2001, reported in UTC. Ad "
                 "Removal Expiry falls on midnight UTC on both rows, so it is a date "
                 "the service set rather than a moment. SIP Username, SIP Host and SIP "
                 "Client IP are the calling settings the service issued. SIP Client IP "
                 "is filled on one of the 2 rows and is an address the service recorded "
                 "for the client, not one read from the device. The store also holds "
                 "the account's SIP password. It is not printed here: SIP Password "
                 "Stored says only whether a value is present, which it was on both "
                 "rows. Account Status, Email Verified, Credits, TextNow Credit, "
                 "Currency, Unlimited and Show Ads are reported as stored. Account "
                 "Status reads ENABLED, Email Verified Yes, Credits 5 and TextNow "
                 "Credit 10 on both rows, and Unlimited reads 1 on both, so none of "
                 "those columns varies across the tested images. Show Ads differs "
                 "between them. A release of the app that does not carry a column is "
                 "read as an empty column of that name rather than costing the query "
                 "every row: the iOS 13.3.1 store has no SIP Client IP column and still "
                 "reports its account.",
        "paths": ('*/Containers/Data/Application/*/Documents/[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "user-check",
                         "sample_data": {
                                            "hickman_ios13": "iOS 13.3.1 | TextNow 20.10.0 | 1 row",
                                            "hickman_ios14": "iOS 14.3 | TextNow 21.3.0 | 1 row",
                                        },
    },
}

import hashlib
import os
import re
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import (artifact_processor, check_in_media, does_table_exist_in_db,
                               get_sqlite_db_records, logfunc)

_CONTAINER = re.compile(r'(.*?/Containers/Data/Application/[0-9A-Fa-f-]{36})/', re.I)
_IMAGE_CACHE = 'com.hackemist.SDWebImageCache.default'
_CORE_DATA_EPOCH_UTC = datetime(2001, 1, 1, tzinfo=timezone.utc)
_IMAGE_SIGNATURES = (b'\xff\xd8\xff', b'\x89PNG\r\n\x1a\n', b'GIF87a', b'GIF89a', b'RIFF')
_CALL_ID = re.compile(r'^(.*)-(\d+(?:\.\d+)?)$')


def _container(path):
    '''The app data container a file sits in, or '' when it is not under one.'''
    match = _CONTAINER.match(str(path).replace('\\', '/'))
    return match.group(1) if match else ''


def _core_data_to_utc(value):
    '''Core Data seconds since 2001 to an aware UTC datetime, or ''.'''
    if value in (None, '', 0):
        return ''
    try:
        return _CORE_DATA_EPOCH_UTC + timedelta(seconds=float(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _text(value):
    '''A stored value as text, with a stored null read as absent.'''
    if value is None:
        return ''
    return str(value)


def _name(first, last):
    '''A first and last name as one, with the padding the store keeps around them dropped.'''
    return ' '.join(part for part in (_text(first).strip(), _text(last).strip()) if part)

def _number(value):
    '''A stored number as text, without a trailing .0 on a whole value.'''
    if value in (None, ''):
        return ''
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    return str(int(number)) if number == int(number) else f'{number:.6f}'


def _stores(files_found):
    '''[(container, path)] for every TextNow account store among the matches.

    The store is named for the account it belongs to, so it cannot be matched by name alone.
    A match is only used when it is a database carrying the app's own entity tables, which
    means a file from another app that happens to sit at the same shape of path is refused.
    '''
    stores = []
    for found in files_found:
        path = str(found)
        if os.path.isdir(path) or path.endswith(('-wal', '-shm', '-journal')):
            continue
        try:
            with open(path, 'rb') as handle:
                if handle.read(16) != b'SQLite format 3\x00':
                    continue
        except OSError as error:
            logfunc(f'TextNow: could not read {path}: {error}')
            continue
        if not does_table_exist_in_db(path, 'ZTMOACCOUNTINFO'):
            continue
        stores.append((_container(path), path))
    return stores


def _call_histories(files_found):
    '''{container: path} for the call history database the app's calling library keeps.

    That database is the calling library's rather than the app's, so an entry is only used
    for a store found in the same container.
    '''
    histories = {}
    for found in files_found:
        path = str(found)
        if os.path.isdir(path) or os.path.basename(path) != 'eventHistory.db':
            continue
        histories[_container(path)] = path
    return histories


def _cached_images(files_found):
    '''{(container, cache file name): path} for the app's own image cache.

    The cache folder is named for the image library rather than for the app, so every entry
    is kept with the container it was found in.
    '''
    entries = {}
    for found in files_found:
        path = str(found)
        if os.path.isdir(path) or f'/{_IMAGE_CACHE}/' not in path.replace('\\', '/'):
            continue
        entries[(_container(path), os.path.basename(path))] = path
    return entries


def _columns(path, table):
    '''The set of column names a table has, or an empty set when it cannot be read.'''
    try:
        return {str(row[1]) for row in get_sqlite_db_records(path, f'PRAGMA table_info({table})')}
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'TextNow: could not read the columns of {table}: {error}')
        return set()


def _rows(path, table, columns, where=''):
    '''Rows of a table, or nothing when the store does not have it.

    Releases of the app differ in which columns the store carries, so a column the store
    does not have is selected as an empty one under its own name rather than costing the
    query every row it would have returned.
    '''
    if not does_table_exist_in_db(path, table):
        return []
    wanted = [name.strip() for name in columns.split(',')]
    present = _columns(path, table)
    if not present:
        return []
    selected = ', '.join(name if name in present else f'NULL AS {name}' for name in wanted)
    try:
        return list(get_sqlite_db_records(path, f'SELECT {selected} FROM {table} {where}'))
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'TextNow: could not read {table}: {error}')
        return []


def _address_book_join(store):
    '''{contact value row id: [address book row ids]} from the join table between them.

    The join table and its two columns are named for the numbers Core Data gave the two
    entities, and those numbers move between releases, so the table is looked up by shape
    rather than by a name typed here.
    '''
    query = ("SELECT name FROM sqlite_master WHERE type='table' "
             "AND name LIKE 'Z!_%CONTACTVALUES' ESCAPE '!'")
    try:
        tables = [str(row[0]) for row in get_sqlite_db_records(store, query)]
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'TextNow: could not list the join tables: {error}')
        return {}
    links = {}
    for table in tables:
        columns = sorted(_columns(store, table))
        contact = next((name for name in columns if 'ADDRESSBOOK' in name.upper()), '')
        value = next((name for name in columns if name != contact), '')
        if not contact or not value:
            continue
        for row in _rows(store, table, f'{contact}, {value}'):
            links.setdefault(row[1], []).append(row[0])
    return links


def _picture(images, container, url):
    '''The cached copy of a picture a message points at, as a media reference, or ''.

    The cache names each file for the address it was fetched from, so the link is one the
    app recorded rather than a match on size or time. The bytes are sniffed before they are
    rendered and anything that is not an image is left alone.
    '''
    if not url:
        return ''
    path = images.get((container, hashlib.md5(url.encode('utf8')).hexdigest()))
    if not path:
        return ''
    try:
        with open(path, 'rb') as handle:
            head = handle.read(16)
    except OSError as error:
        logfunc(f'TextNow: could not read {path}: {error}')
        return ''
    if not head.startswith(_IMAGE_SIGNATURES):
        logfunc(f'TextNow: cached file for a message is not an image: {path}')
        return ''
    return check_in_media(path, os.path.basename(path))


def _self_address(store):
    '''The address the store marks as the account's own, or ''.'''
    for row in _rows(store, 'ZTMOCONTACTVALUE', 'ZCONTACTVALUE', 'WHERE ZCONTACTISSELF = 1'):
        if row[0]:
            return str(row[0])
    return ''


def _conversation_labels(store):
    '''{conversation row id: the name or address the conversation is with}.'''
    values = {row[0]: (_text(row[2]) or _text(row[1]))
              for row in _rows(store, 'ZTMOCONTACTVALUE', 'Z_PK, ZCONTACTVALUE, ZCONTACTNAME')}
    return {row[0]: values.get(row[1], '')
            for row in _rows(store, 'ZTMOCONVERSATION', 'Z_PK, ZCONTACTVALUE')}


def _direction(value):
    '''The app's stored direction as a word, or the value as stored.'''
    return {1: 'Incoming', 2: 'Outgoing'}.get(value, _text(value))


@artifact_processor
def textnow_ios_messages(context):
    '''Messages and their pictures from the TextNow account store.'''
    files_found = context.get_files_found()
    images = _cached_images(files_found)
    data_list, sources = [], []

    for container, store in _stores(files_found):
        sources.append(store)
        labels = _conversation_labels(store)
        own = _self_address(store)
        for row in _rows(store, 'ZTMOINTERACTION',
                         'ZLOCALTIMESTAMP, ZREMOTETIMESTAMP, ZDIRECTION, ZAUTHORNAME, '
                         'ZCONVERSATION, ZCONTENT, ZREAD, ZDELETEDSTATE, ZSTATUS1, '
                         'ZIMAGETYPE, ZTHUMBNAILWIDTH, ZTHUMBNAILHEIGHT, ZMESSAGEID, '
                         'ZORDERINGID, ZCALLID, Z_PK',
                         'WHERE ZCALLID IS NULL'):
            (local, remote, direction, author, conversation, content, read, deleted, status,
             image_type, width, height, message_id, ordering, _, row_id) = row
            message = _text(content)
            sender = _text(author)
            if not sender and direction == 2:
                sender = own
            data_list.append((
                _core_data_to_utc(local),
                _core_data_to_utc(remote),
                _direction(direction),
                sender,
                message,
                _picture(images, container, message if message.startswith('http') else ''),
                labels.get(conversation, ''),
                _text(read),
                _text(deleted),
                _text(status),
                _text(image_type),
                _number(width),
                _number(height),
                _text(message_id),
                _text(ordering),
                _text(row_id),
            ))

    data_headers = (
        ('Message Time', 'datetime'), ('Remote Time', 'datetime'), 'Direction', 'Sender',
        'Message', ('Picture', 'media'), 'Conversation', 'Read State (as stored)',
        'Deleted State (as stored)', 'Send Status (as stored)', 'Image Type (as stored)',
        'Thumbnail Width', 'Thumbnail Height', 'Message ID', 'Ordering ID', 'Row ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def textnow_ios_calls(context):
    '''Calls from the TextNow account store, with the calling library's own record beside them.'''
    files_found = context.get_files_found()
    histories = _call_histories(files_found)
    data_list, sources = [], []

    for container, store in _stores(files_found):
        sources.append(store)
        labels = _conversation_labels(store)
        history_path = histories.get(container, '')
        history = {}
        if history_path:
            sources.append(history_path)
            attributes = {}
            for event_id, key, value in _rows(history_path, 'EventAttributes',
                                              'eventId, key, value'):
                attributes.setdefault(event_id, {})[key] = value
            parties = {row[0]: row[1] for row in _rows(history_path, 'RemoteUsers',
                                                       'eventId, transportUri')}
            for event_id, stamp, direction, sender in _rows(
                    history_path, 'Events', 'eventId, timestamp, direction, sender'):
                history[f'{float(stamp):.6f}'] = {
                    'direction': direction, 'sender': sender,
                    'party': parties.get(event_id, ''), **attributes.get(event_id, {})}

        for row in _rows(store, 'ZTMOINTERACTION',
                         'ZLOCALTIMESTAMP, ZDIRECTION, ZLENGTH, ZCALLID, ZCONVERSATION, '
                         'ZSTATUS, Z_PK',
                         'WHERE ZCALLID IS NOT NULL'):
            local, direction, length, call_id, conversation, status, row_id = row
            match = _CALL_ID.match(_text(call_id))
            number, start = (match.group(1), match.group(2)) if match else ('', '')
            record = history.get(f'{float(start):.6f}', {}) if start else {}
            data_list.append((
                _core_data_to_utc(start) if start else '',
                _core_data_to_utc(local),
                _direction(direction),
                number,
                labels.get(conversation, ''),
                _number(length),
                _number(record.get('callDuration')),
                _text(record.get('callResult')),
                _text(record.get('dialAction')),
                _text(record.get('party')),
                _text(call_id),
                _text(record.get('callId')),
                _text(status),
                _text(row_id),
            ))

    data_headers = (
        ('Call Start', 'datetime'), ('Recorded At', 'datetime'), 'Direction',
        ('Number', 'phonenumber'), 'Conversation', 'Duration (Seconds)',
        'Call History Duration (Seconds)', 'Call History Result (as stored)',
        'Call History Dial Action', ('Call History Party', 'phonenumber'), 'Call ID',
        'Call History Call ID', 'Status (as stored)', 'Row ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def textnow_ios_contacts(context):
    '''Contacts and addresses held in the TextNow account store.'''
    files_found = context.get_files_found()
    data_list, sources = [], []

    for _, store in _stores(files_found):
        sources.append(store)
        labels = _conversation_labels(store)
        servers = {row[0]: (_text(row[1]), _text(row[2]))
                   for row in _rows(store, 'ZTMOSERVERCONTACT', 'Z_PK, ZNAME, ZPICTUREIMAGEKEY')}
        book = {row[0]: (_name(row[1], row[2]), _text(row[3]))
                for row in _rows(store, 'ZTMOABCONTACT',
                                 'Z_PK, ZFIRSTNAME, ZLASTNAME, ZCONTACTID')}
        linked = {value: [book.get(contact, ('', ''))[0] for contact in contacts]
                  for value, contacts in _address_book_join(store).items()}

        for row in _rows(store, 'ZTMOCONTACTVALUE',
                         'Z_PK, ZCONTACTVALUE, ZCONTACTNAME, ZCONTACTLABEL, ZCONTACTISSELF, '
                         'ZINNETWORK, ZSERVERCONTACT, ZCONVERSATION'):
            (row_id, value, name, label, is_self, in_network, server, conversation) = row
            server_name, server_picture = servers.get(server, ('', ''))
            data_list.append((
                _text(value),
                _text(name),
                ', '.join(n for n in linked.get(row_id, []) if n),
                _text(label),
                'Yes' if is_self == 1 else 'No',
                _text(in_network),
                server_name,
                server_picture,
                labels.get(conversation, ''),
                _text(row_id),
            ))

    data_headers = (
        'Contact Value', 'Contact Name', 'Address Book Name', 'Label', 'Account Own Address',
        'In Network (as stored)', 'Service Contact Name', 'Service Contact Picture Key',
        'Conversation', 'Row ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def textnow_ios_account(context):
    '''The account the TextNow store belongs to.'''
    files_found = context.get_files_found()
    data_list, sources = [], []

    for _, store in _stores(files_found):
        sources.append(store)
        for row in _rows(store, 'ZTMOACCOUNTINFO',
                         'ZUSERNAME, ZPHONENUMBER, ZEMAIL, ZFIRSTNAME, ZLASTNAME, '
                         'ZACCOUNTSTATUS, ZEMAILVERIFIED, ZUSERID, ZUSERIDHEX, ZSIPUSERNAME, '
                         'ZSIPHOST, ZSIPCLIENTIP, ZCREDITS, ZTEXTNOWCREDIT, ZCURRENCY, '
                         'ZISUNLIMITED, ZSHOWADS, ZLOCALTIMESTAMP, ZREMOTETIMESTAMP, '
                         'ZLASTWALLETUPDATETIMESTAMP, ZADREMOVALEXPIRYDATE, ZSIPPASSWORD'):
            (username, number, email, first, last, status, verified, user_id, user_id_hex,
             sip_user, sip_host, sip_ip, credit_count, textnow_credit, currency, unlimited,
             show_ads, local, remote, wallet, ad_expiry, sip_password) = row
            data_list.append((
                _core_data_to_utc(local),
                _core_data_to_utc(remote),
                _core_data_to_utc(wallet),
                _core_data_to_utc(ad_expiry),
                _text(username),
                _text(number),
                _text(email),
                _name(first, last),
                _text(status),
                'Yes' if verified == 1 else 'No',
                _text(user_id),
                _text(user_id_hex),
                _text(sip_user),
                _text(sip_host),
                _text(sip_ip),
                'Yes' if sip_password else 'No',
                _text(credit_count),
                _text(textnow_credit),
                _text(currency),
                _text(unlimited),
                _text(show_ads),
            ))

    data_headers = (
        ('Record Updated', 'datetime'), ('Server Record Time', 'datetime'),
        ('Wallet Updated', 'datetime'), ('Ad Removal Expiry', 'datetime'), 'Username',
        ('TextNow Number', 'phonenumber'), 'Email', 'Name', 'Account Status',
        'Email Verified', 'User ID', 'User ID (Hex)', 'SIP Username', 'SIP Host',
        'SIP Client IP', 'SIP Password Stored', 'Credits', 'TextNow Credit', 'Currency',
        'Unlimited (as stored)', 'Show Ads (as stored)')
    return data_headers, data_list, '\n'.join(sources)
