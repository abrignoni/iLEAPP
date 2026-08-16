# pylint: disable=W0718
__artifacts_v2__ = {
    "snapchatMessages": {
        "name": "Snapchat - Messages (arroyo.db)",
        "description": "Chat message records from the conversation_message table in arroyo.db, "
                       "both the rows a normal read returns and rows that are present only before "
                       "the write-ahead log is applied, distinguished by the Record Origin column. "
                       "Sender UUIDs are resolved against the snapchatter store in "
                       "primary.docobjects, and message text is decoded from the message_content "
                       "protobuf on rows where content_type is 1. WAL frames are not parsed, so "
                       "absence of a message here is not evidence it did not exist.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16", "last_update_date": "2026-08-16",
        "requirements": "blackboxprotobuf", "category": "Snapchat",
        "notes": "iOS Snapchat keeps conversations in "
                 "Documents/user_scoped/<account hash>/arroyo/arroyo.db, the same store the "
                 "Android app uses; the schema ships the developers' own column comments and "
                 "they are quoted where relied on.\n"
                 "Record Origin. Live rows come back from a normal read. Recovered rows do not: "
                 "they sit in the database file as of its last checkpoint and are gone once the "
                 "write-ahead log is applied. Recovery Method and Recovery Location are filled "
                 "in only on Recovered rows. The two sets cannot overlap. Why a Recovered row "
                 "is absent is not established here: removal by the app, a server re-sync, and "
                 "deletion all produce the same result.\n"
                 "Method. The file is read twice through SQLite, immutable=1 to ignore the log "
                 "and mode=ro to apply it, then compared on the (client_conversation_id, "
                 "client_message_id) key rather than row count. The glob keeps the -wal and "
                 "-shm sidecars: on the tested image this table reads 11 rows without its log "
                 "and 17 with it applied.\n"
                 "Message text comes from the message_content protobuf at 4 > 4 > 2 > 1, "
                 "derived from observed structure rather than a published schema, and "
                 "cross-checked against the same row's SQL columns on the tested image: field "
                 "2 > 1 holds the 16 raw bytes of sender_id. Only content_type 1 carried text "
                 "(9 of 17 rows); other values carried media metadata but no plaintext body. "
                 "Media is not decrypted or linked to rows, and content_type is reported as "
                 "stored because no source for the enum was verified.\n"
                 "Message Direction compares sender_id against the local account id from "
                 "user_id in the app's Documents/user.plist, else the single distinct sender "
                 "of rows where local_message_content_id is set (the schema comments describe "
                 "that column as nullable if the message was not created on this device). On "
                 "the tested image the user.plist value resolved, matched the snapchatter row "
                 "carrying the account's username, and appeared in every resolved "
                 "conversation's participant list; the fallback is unexercised there because "
                 "local_message_content_id was NULL on every row. Blank when neither "
                 "resolves.\n"
                 "Older arroyo.db generations carry a strict subset of the current columns "
                 "(iOS 12 and 13 era files lack sender_id and content_type, an iOS 14 era "
                 "file lacks only quoted_server_message_id, all as observed in tested "
                 "images); absent columns are substituted with NULL under the same name so "
                 "the remaining columns still report, and the affected fields are blank on "
                 "those rows.\n"
                 "Limits. WAL frames are not parsed, so a message absent here is not evidence "
                 "it did not exist. Reactions and message_state history are not parsed. The "
                 "run log reports the image's WAL frame count.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/user_scoped/*/arroyo/arroyo.db*',
                  '*/mobile/Containers/Data/Application/*/Documents/user_scoped/*/DocObjects/primary.docobjects*',
                  '*/mobile/Containers/Data/Application/*/Documents/user.plist'),
        "output_types": "standard", "artifact_icon": "message",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | 17 rows (all Live)",
            "otto_ios17": "iOS 17.5.1 | 71 rows (59 Live, 12 Recovered)",
            "dexter_ios18": "iOS 18.3.2 | 33 rows (31 Live, 2 Recovered)",
            "iphone12_ios18": "iOS 18.7 | 22 rows (15 Live, 7 Recovered)",
            "hc_ios18_7": "iOS 18.7.8 | 26 rows (all Live)",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 7 rows (all Live)",
            "abe_ios16": "iOS 16.5 | 198 rows (all Live)",
            "hexordia_ios1651": "iOS 16.5.1 | 65 rows (all Live)",
            "magnet_ios16": "iOS 16.1.1 | 7 rows (all Live)",
            "felix23_ios16": "iOS 16.5 | 0 rows (conversation_message table empty)",
            "hickman_ios15": "iOS 15.3.1 | 18 rows (all Live)",
            "jess_ios15": "iOS 15.0.2 | 2 rows (all Live)",
            "hickman_ios14": "iOS 14.3 | 22 rows (all Live; schema lacks quoted_server_message_id)",
            "hickman_ios13": "iOS 13.3.1 | 0 rows (conversation_message table empty)",
            "ctf2020_ios12": "iOS 12.4 | 0 rows (conversation_message table empty)",
            "iphone14plus_ios18": "iOS 18.0 | no Snapchat arroyo.db found",
            "felix_ios17": "iOS 17.6.1 | no Snapchat arroyo.db found",
            "fsfull002_ios17": "iOS 17.1 | no Snapchat arroyo.db found",
            "hc_ios26": "iOS 26.5.2 | no Snapchat arroyo.db found",
            "cookbook_ios1751": "iOS 17.5.1 | no Snapchat arroyo.db found",
            "belkactf6": "no Snapchat files found",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation ID",
                "textColumn": "Message Text",
                "directionColumn": "Message Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Creation Timestamp",
                "senderColumn": "Sender Username",
                # Shows Live or Recovered under every bubble, so a recovered row cannot be
                # read as a live message.
                "extraColumns": ["Record Origin"],
            }
        },
    },
    "snapchatConversations": {
        "name": "Snapchat - Conversations (arroyo.db)",
        "description": "Conversation records from the conversation and feed_entry tables in "
                       "arroyo.db, both the rows a normal read returns and rows that are present "
                       "only before the write-ahead log is applied, distinguished by the Record "
                       "Origin column. Participant UUIDs are decoded from the "
                       "conversation_metadata protobuf and resolved against the snapchatter "
                       "store in primary.docobjects. WAL frames are not parsed, so absence of a "
                       "conversation here is not evidence it did not exist.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16", "last_update_date": "2026-08-16",
        "requirements": "blackboxprotobuf", "category": "Snapchat",
        "notes": "Record Origin. Live rows come back from a normal read. Recovered rows are "
                 "conversations whose client_conversation_id is present in conversation or "
                 "feed_entry as of the last checkpoint and in neither once the write-ahead log "
                 "is applied. Method and limits match Snapchat - Messages (arroyo.db); see its "
                 "notes, including that why a Recovered row is absent is not established.\n"
                 "Rows are the union of client_conversation_id across conversation and "
                 "feed_entry, so a conversation in only one of them is still reported. "
                 "Participant IDs come from the conversation_metadata protobuf at repeated "
                 "field 3, sub-path 1 > 1, as 16 raw bytes formatted as a UUID; on the tested "
                 "image every resolved conversation's participant list included the local "
                 "account id from user.plist. A participant missing from the snapchatter store "
                 "shows as a bare UUID, an unresolved identifier rather than a finding.\n"
                 "Conversation Type is reported as stored, since no source for the enum was "
                 "verified. Message Count counts conversation_message rows in the matching "
                 "view, not messages exchanged.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/user_scoped/*/arroyo/arroyo.db*',
                  '*/mobile/Containers/Data/Application/*/Documents/user_scoped/*/DocObjects/primary.docobjects*'),
        "output_types": "standard", "artifact_icon": "messages",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | 21 rows (all Live)",
            "otto_ios17": "iOS 17.5.1 | 140 rows (138 Live, 2 Recovered)",
            "dexter_ios18": "iOS 18.3.2 | 77 rows (76 Live, 1 Recovered)",
            "iphone12_ios18": "iOS 18.7 | 104 rows (all Live)",
            "hc_ios18_7": "iOS 18.7.8 | 14 rows (all Live)",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 18 rows (all Live)",
            "abe_ios16": "iOS 16.5 | 12 rows (all Live)",
            "hexordia_ios1651": "iOS 16.5.1 | 11 rows (all Live)",
            "magnet_ios16": "iOS 16.1.1 | 1 row",
            "felix23_ios16": "iOS 16.5 | 1 row",
            "hickman_ios15": "iOS 15.3.1 | 4 rows (all Live)",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "hickman_ios14": "iOS 14.3 | 2 rows (all Live)",
            "hickman_ios13": "iOS 13.3.1 | 2 rows (feed_entry lacks streak columns)",
            "ctf2020_ios12": "iOS 12.4 | 4 rows (feed_entry lacks streak columns)",
        },
    },
    "snapchatFriends": {
        "name": "Snapchat - Friends",
        "description": "Snapchatter records from the primary.docobjects store: usernames from "
                       "the store's own index tables, user id, and the display name string from "
                       "the record's serialized document.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16", "last_update_date": "2026-08-16",
        "requirements": "none", "category": "Snapchat",
        "notes": "primary.docobjects (Documents/user_scoped/<account hash>/DocObjects/) is a "
                 "SQLite store whose snapchatter table keeps one FlatBuffers document per user "
                 "in column p, keyed by userId. Username, Mutable Username and Legacy Username "
                 "come from the store's own index_snapchatter* tables, joined on rowid, not "
                 "from the document blob.\n"
                 "Display Name is read from the document's third string field. No published "
                 "schema for the document was found, so the field position was established on "
                 "the tested image and is self-checked at parse time: the value is only "
                 "reported when the document's first field equals the row's userId column, and "
                 "on the tested image the document's username fields equalled the index tables "
                 "on all 120 rows. When the layout check fails the column is left blank.\n"
                 "Older store generations carry fewer index tables (an iOS 14 era file has "
                 "only the username index) and iOS 12 and 13 era files predate the "
                 "snapchatter table entirely; missing index tables report as blank columns "
                 "and pre-snapchatter stores report no rows, with a log line saying so. The "
                 "display-name field position also held on the iOS 14 era store, where all "
                 "86 rows passed the layout self-check.\n"
                 "No timestamps are reported: none were identified in the SQL columns, and "
                 "none in the document were established. Friend-relationship state (added, "
                 "blocked, best-friend) is not parsed. The local account appears as a row.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/user_scoped/*/DocObjects/primary.docobjects*',),
        "output_types": "standard", "artifact_icon": "users",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | 120 rows",
            "otto_ios17": "iOS 17.5.1 | 293 rows",
            "dexter_ios18": "iOS 18.3.2 | 13 rows",
            "iphone12_ios18": "iOS 18.7 | 220 rows",
            "hc_ios18_7": "iOS 18.7.8 | 4 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 106 rows",
            "abe_ios16": "iOS 16.5 | 115 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 3 rows",
            "magnet_ios16": "iOS 16.1.1 | 129 rows",
            "hickman_ios15": "iOS 15.3.1 | 121 rows",
            "jess_ios15": "iOS 15.0.2 | 33 rows",
            "hickman_ios14": "iOS 14.3 | 86 rows (store has only the username index table)",
            "hickman_ios13": "iOS 13.3.1 | 0 rows (store predates the snapchatter table)",
            "ctf2020_ios12": "iOS 12.4 | 0 rows (store predates the snapchatter table)",
        },
    },
    "snapchatGallerySearch": {
        "name": "Snapchat - Memories Search Index",
        "description": "Per-snap rows from the app's gallery_search index: the app's own "
                       "time, location, visual and meta tags, caption text, and visual "
                       "concept labels with their stored confidence values.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16", "last_update_date": "2026-08-16",
        "requirements": "none", "category": "Snapchat",
        "notes": "search.sqlite3 (Documents/gallery_search/<n>/<account hash>/) is the "
                 "index the app builds over Memories snaps so they can be searched. All "
                 "values are app-generated tags reported as stored, not observations about "
                 "the media itself: location tags are place-name strings (down to street "
                 "level on the tested image), visual tags and concepts are the app's "
                 "labels with their stored confidence, and the time tag is a date string.\n"
                 "Tag rows live in FTS content tables keyed by docid; docid was verified "
                 "equal to snap_id_table's rowid on the tested image by matching each "
                 "row's visual tags against snap_visual_tag_conf_table for the same snap "
                 "id. The snap id refers to a Memories entry; linking it to media files "
                 "is not done here.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/gallery_search/*/search.sqlite3*',),
        "output_types": "standard", "artifact_icon": "search",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | 13 rows",
            "hickman_ios15": "iOS 15.3.1 | 13 rows",
            "hickman_ios14": "iOS 14.3 | 9 rows",
            "hickman_ios13": "iOS 13.3.1 | 11 rows",
            "dexter_ios18": "iOS 18.3.2 | 2 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "abe_ios16": "iOS 16.5 | 1 row",
            "otto_ios17": "iOS 17.5.1 | 0 rows (index tables empty)",
            "iphone12_ios18": "iOS 18.7 | no gallery_search search.sqlite3 found",
        },
    },
    "snapchatAccount": {
        "name": "Snapchat - Account",
        "description": "Account values from the app's Documents/user.plist: username, user id, "
                       "laguna id, and client encryption values, reported as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16", "last_update_date": "2026-08-16",
        "requirements": "none", "category": "Snapchat",
        "notes": "user.plist is not a property list despite its name: it begins with the "
                 "magic TSAF and carries length-delimited strings. The format is otherwise "
                 "undocumented here, so values are read as the string that follows each named "
                 "key token, and user_id and laguna_id are additionally required to be "
                 "UUID-shaped before being reported. On the tested image user_id matched a "
                 "userId in the snapchatter store whose username matched this file's username "
                 "value.\n"
                 "The client_encryption identifier, encryption_key and initialization_vector "
                 "are reported as stored; what they encrypt is not established here. Files "
                 "that do not begin with the TSAF magic are skipped, since Documents/user.plist "
                 "is not a Snapchat-specific file name.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/user.plist',),
        "output_types": "standard", "artifact_icon": "user",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | 6 rows",
            "otto_ios17": "iOS 17.5.1 | 6 rows",
            "dexter_ios18": "iOS 18.3.2 | 6 rows",
            "iphone12_ios18": "iOS 18.7 | 6 rows",
            "hc_ios18_7": "iOS 18.7.8 | 6 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 6 rows",
            "abe_ios16": "iOS 16.5 | 6 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 6 rows",
            "magnet_ios16": "iOS 16.1.1 | 6 rows",
            "hickman_ios15": "iOS 15.3.1 | 6 rows",
            "jess_ios15": "iOS 15.0.2 | 5 rows",
            "hickman_ios14": "iOS 14.3 | 5 rows",
            "hickman_ios13": "iOS 13.3.1 | 5 rows",
            "ctf2020_ios12": "iOS 12.4 | 5 rows",
        },
    },
}

import datetime
import os
import re
import sqlite3
import struct

from scripts import blackboxprotobuf
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_path, logfunc

# blackboxprotobuf raises these when a blob does not decode as protobuf.
_PB_ERRORS = (ValueError, TypeError, IndexError, KeyError, AttributeError)
_TSAF_MAGIC = b'TSAF'
_UUID_RE = re.compile(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-'
                      r'[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _app_container(path):
    '''The .../Data/Application/<UUID> prefix of a path, or '' when not under one.'''
    normalized = str(path).replace('\\', '/')
    marker = '/Data/Application/'
    index = normalized.find(marker)
    if index == -1:
        return ''
    end = normalized.find('/', index + len(marker))
    return normalized[:end] if end != -1 else normalized


def _find(files_found, *suffixes):
    for file_found in files_found:
        if str(file_found).endswith(suffixes):
            return str(file_found)
    return ''


def _find_sibling(files_found, anchor_path, *suffixes):
    '''The matching file from the same app container as anchor_path, else any match.'''
    container = _app_container(anchor_path)
    fallback = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith(suffixes):
            continue
        if container and _app_container(file_found) == container:
            return file_found
        if not fallback:
            fallback = file_found
    return fallback


def _rows(source_path, sql, params=()):
    if not source_path:
        return []
    try:
        db = sqlite3.connect(f'file:{get_sqlite_db_path(source_path)}?mode=ro', uri=True)
    except sqlite3.Error:
        return []
    cursor = db.cursor()
    try:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


def _rows_pre_wal(source_path, sql):
    '''Run sql against the database file as of its last checkpoint, ignoring the WAL.

    immutable=1 is strictly read-only. Unlike mode=ro it does not even create a -shm
    sidecar, so no evidence file is altered.
    '''
    if not source_path:
        return []
    try:
        db = sqlite3.connect(f'file:{get_sqlite_db_path(source_path)}?immutable=1', uri=True)
    except sqlite3.Error:
        return []
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


def _table_columns(source_path, table):
    return {row[1] for row in _rows(source_path, f'PRAGMA table_info({table})')}


def _tolerant_select(source_path, table, columns, tail=''):
    '''A SELECT that names every requested column, substituting NULL AS <name> for columns
    the file's schema generation does not have, so one absent column does not silently drop
    every row. Older arroyo.db generations carry strict subsets of the current columns; on
    the tested images nothing was renamed, only absent.
    '''
    present = _table_columns(source_path, table)
    select_list = ', '.join(
        column if column in present else f'NULL AS {column}' for column in columns)
    return f'SELECT {select_list} FROM {table} {tail}'


def _superseded(source_path, sql, key_indexes):
    '''Rows present at the last checkpoint and absent once the write-ahead log is applied.

    Both sides are consistent SQLite views of the same file, one ignoring the WAL and one
    applying it, compared on the columns at key_indexes rather than on row counts, since a
    table can hold the same number of rows in both views with different rows in it.
    Empty when the file has no WAL alongside it. Why a row did not survive into the
    committed state is not established here.
    '''
    def key(row):
        return tuple(row[index] for index in key_indexes)

    committed = {key(row) for row in _rows(source_path, sql)}
    return [row for row in _rows_pre_wal(source_path, sql) if key(row) not in committed]


# --- primary.docobjects (snapchatter store) -------------------------------------------------

def _fb_string_field(buf, slot):
    '''String value of a FlatBuffers root-table field slot, or '' when absent or not a string.

    Reads only the root table: root offset, its vtable, the slot's field offset, then the
    field as an offset to a length-prefixed UTF-8 string. Any structural mismatch returns ''.
    '''
    try:
        table_pos = struct.unpack_from('<I', buf, 0)[0]
        vtable_offset = struct.unpack_from('<i', buf, table_pos)[0]
        vtable_pos = table_pos - vtable_offset
        vtable_size = struct.unpack_from('<H', buf, vtable_pos)[0]
        if slot >= (vtable_size - 4) // 2:
            return ''
        field_offset = struct.unpack_from('<H', buf, vtable_pos + 4 + slot * 2)[0]
        if field_offset == 0:
            return ''
        field_pos = table_pos + field_offset
        string_pos = field_pos + struct.unpack_from('<I', buf, field_pos)[0]
        string_len = struct.unpack_from('<I', buf, string_pos)[0]
        if string_pos + 4 + string_len > len(buf):
            return ''
        return buf[string_pos + 4:string_pos + 4 + string_len].decode('utf-8')
    except (struct.error, IndexError, UnicodeDecodeError, TypeError):
        return ''


# Field slots in the snapchatter FlatBuffers document, established on the tested image:
# slot 0 equalled the row's userId SQL column on all 120 rows, slots 1, 14 and 15 equalled
# the store's own username index tables, and slot 2 held the display name string. Slot 2 is
# only trusted when the slot-0 check passes on that row.
_FB_SLOT_USER_ID = 0
_FB_SLOT_DISPLAY_NAME = 2


def _display_name(blob, user_id):
    if not isinstance(blob, (bytes, bytearray)):
        return ''
    buf = bytes(blob)
    if _fb_string_field(buf, _FB_SLOT_USER_ID) != user_id:
        return ''
    return _fb_string_field(buf, _FB_SLOT_DISPLAY_NAME)


def _store_tables(doc_store_path):
    return {row[0] for row in _rows(
        doc_store_path, "SELECT name FROM sqlite_master WHERE type = 'table'")}


def _snapchatter_sql(doc_store_path):
    '''SELECT for snapchatter rows with whichever index tables this store generation has.

    Older stores lack some or all of the index_snapchatter* tables (an iOS 14 era file has
    only index_snapchatterusername, and iOS 12 and 13 era files have no snapchatter table
    at all), and a join against a missing table would silently drop every row. Absent
    sources are substituted with NULL under the same name.
    '''
    tables = _store_tables(doc_store_path)
    if 'snapchatter' not in tables:
        return ''
    selects = ['snapchatter.userId', 'snapchatter.p']
    joins = []
    for table, column in (('index_snapchatterusername', 'username'),
                          ('index_snapchattermutableUsername', 'mutableUsername'),
                          ('index_snapchatterlegacyUsername', 'legacyUsername')):
        if table in tables:
            selects.append(f'{table}.{column}')
            joins.append(f'LEFT JOIN {table} ON {table}.rowid = snapchatter.rowid')
        else:
            selects.append(f'NULL AS {column}')
    return f"SELECT {', '.join(selects)} FROM snapchatter {' '.join(joins)}"


def _friend_records(doc_store_path):
    '''snapchatter rows as {userId: (username, display_name)}, usernames from index tables.'''
    friends = {}
    sql = _snapchatter_sql(doc_store_path)
    if not sql:
        return friends
    for user_id, blob, username, _mutable, _legacy in _rows(doc_store_path, sql):
        if user_id:
            friends[user_id] = (username or '', _display_name(blob, user_id))
    return friends


def _friend_name(friends, user_id, index=0):
    return friends.get(user_id, ('', ''))[index]


# --- user.plist (TSAF) ----------------------------------------------------------------------

def _tsaf_tokens(path):
    '''The length-delimited strings of a TSAF file, in order; [] when not TSAF.'''
    if not path:
        return []
    try:
        with open(path, 'rb') as handle:
            data = handle.read()
    except OSError:
        return []
    if not data.startswith(_TSAF_MAGIC):
        return []
    return [token.decode('utf-8', 'replace')
            for token in re.findall(rb'\x08([^\x00]+)\x00', data)]


def _tsaf_value(tokens, key):
    '''The string following the key token, or ''.'''
    for position, token in enumerate(tokens):
        if token == key and position + 1 < len(tokens):
            return tokens[position + 1]
    return ''


def _local_user_id(user_plist_path, arroyo_path):
    '''The signed-in account's user id, or '' when it cannot be established.

    Preferred source is user_id in the app's Documents/user.plist. Failing that, the single
    distinct sender of rows where local_message_content_id is set, which the arroyo.db
    schema comments describe as nullable if the message was not created on this device.
    '''
    user_id = _tsaf_value(_tsaf_tokens(user_plist_path), 'user_id')
    if user_id and _UUID_RE.match(user_id):
        return user_id
    senders = {row[0] for row in _rows(
        arroyo_path,
        'SELECT DISTINCT sender_id FROM conversation_message '
        'WHERE local_message_content_id IS NOT NULL') if row[0]}
    return senders.pop() if len(senders) == 1 else ''


# --- arroyo.db protobuf helpers -------------------------------------------------------------

def _pb_get(node, key):
    '''Read one field out of a blackboxprotobuf dict.

    blackboxprotobuf splits a field whose repeats decode to different typedefs into
    'N-1', 'N-2' keys, so fall back to the first such variant when the plain key is absent.
    '''
    if not isinstance(node, dict):
        return None
    if key in node:
        return node[key]
    for name in sorted(node):
        if name.startswith(f'{key}-'):
            return node[name]
    return None


def _pb_walk(node, *path):
    '''Walk a blackboxprotobuf dict, taking the first element of any repeated field.'''
    current = node
    for key in path:
        if isinstance(current, list):
            current = current[0] if current else None
        current = _pb_get(current, key)
    if isinstance(current, list):
        current = current[0] if current else None
    return current


def _pb_text(node, *path):
    value = _pb_walk(node, *path)
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).decode('utf-8', 'replace')
    if isinstance(value, str):
        return value
    return ''


def _uuid_from_bytes(value):
    '''Format a 16-byte protobuf value as a canonical UUID string.'''
    if not isinstance(value, (bytes, bytearray)) or len(value) != 16:
        return ''
    digits = bytes(value).hex()
    return (f'{digits[0:8]}-{digits[8:12]}-{digits[12:16]}-'
            f'{digits[16:20]}-{digits[20:32]}')


def _decode(blob):
    if not blob:
        return None
    try:
        values, _typedef = blackboxprotobuf.decode_message(bytes(blob))
    except _PB_ERRORS:
        return None
    return values if isinstance(values, dict) else None


def _participants(arroyo_path, friends, reader=_rows):
    '''Map client_conversation_id to (participant ids, participant usernames).'''
    participants = {}
    for conversation_id, blob in reader(
            arroyo_path, 'SELECT client_conversation_id, conversation_metadata FROM conversation'):
        entries = _pb_get(_decode(blob), '3')
        if isinstance(entries, dict):
            entries = [entries]
        ids = []
        for entry in entries if isinstance(entries, list) else []:
            user_id = _uuid_from_bytes(_pb_walk(entry, '1', '1'))
            if user_id and user_id not in ids:
                ids.append(user_id)
        names = [_friend_name(friends, user_id) or user_id for user_id in ids]
        participants[conversation_id] = (', '.join(ids), ', '.join(names))
    return participants


def _yes_no(value):
    return 'YES' if value else 'NO'


def _log_wal_extent(files_found):
    '''Log how much write-ahead log this artifact leaves unparsed, per image.

    Reads the WAL header and the 24-byte frame headers only; no page images are loaded.
    A frame whose salt pair does not match the WAL header belongs to a previous log
    generation that the current one has cycled past, so it holds older content still on
    disk. Reporting both counts gives the examiner the size of what is not covered here.
    '''
    wal_path = _find(files_found, 'arroyo.db-wal')
    if not wal_path:
        return
    try:
        with open(wal_path, 'rb') as handle:
            header = handle.read(32)
            if len(header) < 32:
                return
            magic = struct.unpack('>I', header[:4])[0]
            page_size = struct.unpack('>I', header[8:12])[0]
            if magic not in (0x377F0682, 0x377F0683) or page_size < 512:
                return
            salts = struct.unpack('>2I', header[16:24])
            frame_size = 24 + page_size
            total = max(0, (os.path.getsize(wal_path) - 32) // frame_size)
            current = 0
            for index in range(total):
                handle.seek(32 + index * frame_size)
                frame_header = handle.read(24)
                if len(frame_header) < 24:
                    total = index
                    break
                if struct.unpack('>2I', frame_header[8:16]) == salts:
                    current += 1
    except (OSError, struct.error, ValueError):
        return
    logfunc(f'Snapchat arroyo.db-wal holds {total} frames of {page_size} bytes '
            f'({current} in the current log generation, {total - current} from previous '
            f'generations). This artifact does not parse WAL frames, so records held only in '
            f'them are not reported and absence of a message from the Snapchat arroyo.db '
            f'artifacts is not evidence that it did not exist.')


_MESSAGE_COLUMNS = ('creation_timestamp', 'read_timestamp', 'sender_id', 'content_type',
                    'message_content', 'message_state_type', 'is_saved', 'is_viewed_by_user',
                    'remote_media_count', 'quoted_server_message_id',
                    'client_conversation_id', 'client_message_id', 'server_message_id')


def _message_sql(source_path):
    return _tolerant_select(source_path, 'conversation_message', _MESSAGE_COLUMNS,
                            'ORDER BY creation_timestamp')


# conversation_message key (client_conversation_id, client_message_id), as offsets into
# _MESSAGE_COLUMNS.
_MESSAGE_KEY = (10, 11)

_MESSAGE_HEADERS = (('Creation Timestamp', 'datetime'), ('Read Timestamp', 'datetime'),
                    'Record Origin',
                    'Sender Username', 'Sender Display Name', 'Sender ID', 'Message Direction',
                    'Conversation Participants', 'Message Text', 'Content Type (as stored)',
                    'Message State Type', 'Is Saved', 'Is Viewed By User',
                    'Remote Media Count', 'Quoted Server Message ID',
                    'Conversation ID', 'Client Message ID', 'Server Message ID',
                    'Recovery Method', 'Recovery Location')

_CONVERSATION_HEADERS = (('Creation Timestamp', 'datetime'), ('Last Updated Timestamp', 'datetime'),
                         ('Display Timestamp', 'datetime'), ('Tombstoned At Timestamp', 'datetime'),
                         ('Streak Expiration Timestamp', 'datetime'),
                         'Record Origin',
                         'Conversation Title',
                         'Participants', 'Participant IDs', 'Message Count', 'Streak Count',
                         'Conversation Type (as stored)', 'Send State Type', 'Feed Item Creator',
                         'Feed Item Creator ID', 'Last Chat Sender', 'Last Chat Sender ID',
                         'Tombstoned', 'Conversation ID',
                         'Recovery Method', 'Recovery Location')

# Provenance vocabulary. Record Origin is a closed two-value set so a viewer can branch on
# it; Recovery Method names the technique and is empty on live rows; Recovery Location says
# where in the evidence the row came from. Keep these strings stable, they are read by
# people and may be read by LAVA.
_ORIGIN_LIVE = 'Live'
_ORIGIN_RECOVERED = 'Recovered'
_METHOD_WAL_DIFF = 'WAL diff'


def _provenance(source_path, origin):
    '''The three provenance values for a row, as (origin, method, location).'''
    if origin == _ORIGIN_LIVE:
        return (_ORIGIN_LIVE, '', '')
    name = os.path.basename(source_path) if source_path else 'database'
    return (_ORIGIN_RECOVERED, _METHOD_WAL_DIFF, f'{name} (pre-checkpoint)')


def _by_creation(row):
    '''Sort key on the first column, tolerating rows whose timestamp is blank.

    The blank flag comes first so a datetime is never compared against a string.
    '''
    return (row[0] == '', row[0])


def _message_rows(rows, friends, participants, local_user_id, provenance):
    origin, method, location = provenance
    data_list = []
    for row in rows:
        (created, read, sender_id, content_type, blob, state, saved, viewed,
         media_count, quoted_id, conversation_id, client_message_id, server_message_id) = row
        text = _pb_text(_decode(blob), '4', '4', '2', '1') if content_type == 1 else ''
        if not local_user_id or not sender_id:
            direction = ''
        else:
            direction = 'Outgoing' if sender_id == local_user_id else 'Incoming'
        data_list.append((
            _ms_to_utc(created), _ms_to_utc(read), origin,
            _friend_name(friends, sender_id), _friend_name(friends, sender_id, 1), sender_id,
            direction, participants.get(conversation_id, ('', ''))[1], text, content_type,
            state, _yes_no(saved), _yes_no(viewed), media_count, quoted_id,
            conversation_id, client_message_id, server_message_id, method, location))
    return data_list


def _conversation_rows(source_path, friends, reader, provenance, only_ids=None):
    participants = _participants(source_path, friends, reader)
    conversations = {row[0]: row[1:] for row in reader(source_path, '''
        SELECT client_conversation_id, creation_timestamp, tombstoned_at_timestamp,
               send_state_type
        FROM conversation
    ''')}
    feeds = {row[0]: row[1:] for row in reader(source_path, _tolerant_select(
        source_path, 'feed_entry',
        ('client_conversation_id', 'last_updated_timestamp', 'display_timestamp',
         'streak_expiration_timestamp_ms', 'conversation_title', 'conversation_type',
         'streak_count', 'feedItemCreator', 'last_chat_sender', 'tombstoned')))}
    counts = dict(reader(source_path, '''
        SELECT client_conversation_id, COUNT(*) FROM conversation_message
        GROUP BY client_conversation_id
    '''))

    origin, method, location = provenance
    wanted = set(conversations) | set(feeds)
    if only_ids is not None:
        wanted &= set(only_ids)

    data_list = []
    for conversation_id in sorted(wanted):
        created, tombstoned_at, send_state = conversations.get(conversation_id, (None, None, ''))
        (updated, displayed, streak_expiry, title, conversation_type, streak, creator,
         last_sender, tombstoned) = feeds.get(conversation_id, (None,) * 9)
        data_list.append((
            _ms_to_utc(created), _ms_to_utc(updated), _ms_to_utc(displayed),
            _ms_to_utc(tombstoned_at), _ms_to_utc(streak_expiry), origin, title,
            participants.get(conversation_id, ('', ''))[1],
            participants.get(conversation_id, ('', ''))[0],
            counts.get(conversation_id, 0), streak, conversation_type, send_state,
            _friend_name(friends, creator), creator,
            _friend_name(friends, last_sender), last_sender,
            _yes_no(tombstoned), conversation_id, method, location))
    return data_list


def _superseded_conversation_ids(source_path):
    '''client_conversation_id values that the WAL removes from conversation or feed_entry.'''
    pre, committed = set(), set()
    for sql in ('SELECT client_conversation_id FROM conversation',
                'SELECT client_conversation_id FROM feed_entry'):
        pre |= {row[0] for row in _rows_pre_wal(source_path, sql)}
        committed |= {row[0] for row in _rows(source_path, sql)}
    return pre - committed


@artifact_processor
def snapchatMessages(context):
    '''Live conversation_message rows, plus rows the write-ahead log removes.

    Both sets are in one table so the recovered rows sit in chronological context. They are
    disjoint by construction: _superseded only returns keys absent from the live read.
    '''
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for arroyo_path in sorted({str(f) for f in files_found if str(f).endswith('arroyo.db')}):
        source_path = source_path or arroyo_path
        doc_store = _find_sibling(files_found, arroyo_path, 'primary.docobjects')
        user_plist = _find_sibling(files_found, arroyo_path, 'user.plist')
        friends = _friend_records(doc_store)
        local_user_id = _local_user_id(user_plist, arroyo_path)
        message_sql = _message_sql(arroyo_path)
        data_list += _message_rows(
            _rows(arroyo_path, message_sql), friends, _participants(arroyo_path, friends),
            local_user_id, _provenance(arroyo_path, _ORIGIN_LIVE))
        data_list += _message_rows(
            _superseded(arroyo_path, message_sql, _MESSAGE_KEY), friends,
            _participants(arroyo_path, friends, _rows_pre_wal), local_user_id,
            _provenance(arroyo_path, _ORIGIN_RECOVERED))
    _log_wal_extent(files_found)
    data_list.sort(key=_by_creation)
    return _MESSAGE_HEADERS, data_list, source_path


@artifact_processor
def snapchatConversations(context):
    '''Live conversation and feed_entry rows, plus rows the write-ahead log removes.'''
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for arroyo_path in sorted({str(f) for f in files_found if str(f).endswith('arroyo.db')}):
        source_path = source_path or arroyo_path
        doc_store = _find_sibling(files_found, arroyo_path, 'primary.docobjects')
        friends = _friend_records(doc_store)
        data_list += _conversation_rows(arroyo_path, friends, _rows,
                                        _provenance(arroyo_path, _ORIGIN_LIVE))
        data_list += _conversation_rows(arroyo_path, friends, _rows_pre_wal,
                                        _provenance(arroyo_path, _ORIGIN_RECOVERED),
                                        _superseded_conversation_ids(arroyo_path))
    data_list.sort(key=_by_creation)
    return _CONVERSATION_HEADERS, data_list, source_path


@artifact_processor
def snapchatFriends(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for doc_store in sorted({str(f) for f in files_found
                             if str(f).endswith('primary.docobjects')}):
        source_path = source_path or doc_store
        sql = _snapchatter_sql(doc_store)
        if not sql:
            logfunc(f'No snapchatter table in {doc_store}; this store generation predates it.')
            continue
        for user_id, blob, username, mutable, legacy in _rows(doc_store, sql):
            data_list.append((username or '', _display_name(blob, user_id), user_id,
                              mutable or '', legacy or '',
                              context.get_relative_path(doc_store)))
    data_headers = ('Username', 'Display Name', 'User ID', 'Mutable Username',
                    'Legacy Username', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def snapchatGallerySearch(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for search_db in sorted({str(f) for f in files_found if str(f).endswith('search.sqlite3')}):
        source_path = source_path or search_db
        source_file = context.get_relative_path(search_db)
        concepts = {}
        for snap_id, concept, confidence in _rows(search_db, '''
                SELECT snap_id, concept, conf FROM snap_visual_tag_conf_table
                ORDER BY snap_id, conf DESC'''):
            if snap_id and concept:
                rounded = f'{confidence:.3f}' if isinstance(confidence, float) else confidence
                concepts.setdefault(snap_id, []).append(f'{concept} ({rounded})')
        for row in _rows(search_db, '''
                SELECT ids.snap_id, time_tags.time_tag, ids.language_id,
                       location_clusters.cluster_name, visual_clusters.cluster_name,
                       tags.c0time_tag, tags.c1location_tag, tags.c2visual_tag,
                       tags.c3meta_tag, captions.c0caption
                FROM snap_id_table AS ids
                LEFT JOIN snap_tag_table_content AS tags ON tags.docid = ids.rowid
                LEFT JOIN snap_description_table_content AS captions
                    ON captions.docid = ids.rowid
                LEFT JOIN snap_time_tag_table AS time_tags
                    ON time_tags.snap_id = ids.snap_id
                LEFT JOIN snap_location_tag_cluster_table AS location_clusters
                    ON location_clusters.snap_id = ids.snap_id
                LEFT JOIN snap_visual_tag_cluster_table AS visual_clusters
                    ON visual_clusters.snap_id = ids.snap_id'''):
            (snap_id, time_tag, language, location_cluster, visual_cluster,
             time_tags, location_tags, visual_tags, meta_tags, caption) = row
            data_list.append((
                time_tag, snap_id, location_tags, location_cluster, visual_tags,
                ', '.join(concepts.get(snap_id, [])), visual_cluster, meta_tags,
                time_tags, caption, language, source_file))
    data_headers = (('Time Tag', 'date'), 'Snap ID', 'Location Tags', 'Location Cluster',
                    'Visual Tags', 'Visual Concepts (confidence)', 'Visual Cluster',
                    'Meta Tags', 'Time Tags', 'Caption', 'Language', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def snapchatAccount(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for user_plist in sorted({str(f) for f in files_found if str(f).endswith('user.plist')}):
        tokens = _tsaf_tokens(user_plist)
        if not tokens:
            continue
        source_path = source_path or user_plist
        relative_path = context.get_relative_path(user_plist)
        for key in ('username', 'user_id', 'laguna_id'):
            value = _tsaf_value(tokens, key)
            if key in ('user_id', 'laguna_id') and value and not _UUID_RE.match(value):
                continue
            if value:
                data_list.append((key, value, relative_path))
        for key in ('identifier', 'encryption_key', 'initialization_vector'):
            value = _tsaf_value(tokens, key)
            if value:
                data_list.append((f'client_encryption {key}', value, relative_path))
    data_headers = ('Key', 'Value', 'Source File')
    return data_headers, data_list, source_path
