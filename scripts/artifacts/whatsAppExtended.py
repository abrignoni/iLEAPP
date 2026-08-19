"""WhatsApp iOS add-on artifacts: message reactions, channel reaction tallies,
group events and group membership changes from ChatStorage.sqlite.

Reactions on iOS are not stored in their own table. They live inside the
ZWAMESSAGEINFO.ZRECEIPTINFO protobuf blob (one row per message, linked from
ZWAMESSAGE.ZMESSAGEINFO). Field meanings here were established by decoding
every populated blob across 13 test images (iOS 12.4 through iOS 26) and
cross-checking the decoded values against the columns beside them; see each
artifact's notes and sample_data.

This is the iOS counterpart of ALEAPP's whatsAppExtended.py (PR #1118). The
Android feature map came from WAInsight by Akhil Dara
(https://github.com/akhil-dara/WAInsight, MIT); WAInsight has no iOS support,
so the structures here were derived from the test images directly.
"""

__artifacts_v2__ = {
    "whatsAppReactions": {
        "name": "WhatsApp - Message Reactions",
        "description": "WhatsApp emoji reactions decoded from the ZRECEIPTINFO blob (ChatStorage.sqlite)",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "Reactions are stored inside ZWAMESSAGEINFO.ZRECEIPTINFO, a protobuf blob. "
                 "Two record shapes were observed under field 7 across the tested images. "
                 "Shape one (field 7.1) carries a message key id, the reactor's JID, the "
                 "emoji, and a millisecond timestamp; every decoded instance had a "
                 "well-formed JID and a plausible timestamp (12 of 12). Shape two (field "
                 "7.2) carries a key id, the emoji, and a millisecond timestamp but no JID "
                 "(26 of 26 decoded clean); it was observed on both incoming and outgoing "
                 "messages, so which party reacted is not established for that shape and "
                 "the Reactor JID column is empty there. The Record Shape column states "
                 "which shape each row came from. Decoded with the bundled "
                 "blackboxprotobuf; no external source documents this blob, so only "
                 "content verifiable in the data itself is reported.",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/ChatStorage.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "thumb-up",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | WhatsApp Messenger 23.11.80 | 3 rows",
            "ctf2020_ios12": "iOS 12.4 | net.whatsapp.WhatsApp | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | WhatsApp Messenger 25.26.72 | 9 rows",
            "felix23_ios16": "iOS 16.5 | WhatsApp Messenger 23.12.76 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | WhatsApp Messenger 24.17.78 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | WhatsApp Messenger 23.8.78 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | WhatsApp Messenger 26.14.76 | 1 row",
            "hc_ios26": "iOS 26.5.2 | 1 row",
            "hickman_ios13": "iOS 13.3.1 | WhatsApp Messenger 2.20.31 | 0 rows",
            "hickman_ios14": "iOS 14.3 | WhatsApp Messenger 2.21.20 | 0 rows",
            "hickman_ios15": "iOS 15 | 1 row",
            "iphone11_ios17": "iOS 17.3 | WhatsApp Messenger 24.15.1 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | WhatsApp Messenger 24.13.79 | 21 rows",
        },
    },
    "whatsAppChannelReactionTallies": {
        "name": "WhatsApp - Channel Reaction Tallies",
        "description": "Aggregate emoji reaction counts on channel messages, decoded from the ZRECEIPTINFO blob (ChatStorage.sqlite)",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "Field 7.3 of the ZWAMESSAGEINFO.ZRECEIPTINFO protobuf holds repeated "
                 "(emoji, count) pairs. In the tested images these appear on messages in "
                 "@newsletter (channel) chats and the counts reach the thousands, "
                 "consistent with channel-wide totals rather than per-contact reactions; "
                 "that reading is an observation from the tested data, not a documented "
                 "meaning. One row per emoji per message, count reported as stored.",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/ChatStorage.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "chart-bar",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | WhatsApp Messenger 23.11.80 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | net.whatsapp.WhatsApp | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | WhatsApp Messenger 25.26.72 | 0 rows",
            "felix23_ios16": "iOS 16.5 | WhatsApp Messenger 23.12.76 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | WhatsApp Messenger 24.17.78 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | WhatsApp Messenger 23.8.78 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | WhatsApp Messenger 26.14.76 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | WhatsApp Messenger 2.20.31 | 0 rows",
            "hickman_ios14": "iOS 14.3 | WhatsApp Messenger 2.21.20 | 0 rows",
            "hickman_ios15": "iOS 15 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | WhatsApp Messenger 24.15.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | WhatsApp Messenger 24.13.79 | 1324 rows",
        },
    },
    "whatsAppGroupEvents": {
        "name": "WhatsApp - Group Events",
        "description": "WhatsApp message rows carrying a group event type (ChatStorage.sqlite ZWAMESSAGE)",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "Rows in ZWAMESSAGE whose ZGROUPEVENTTYPE is set and non-zero. The value "
                 "is an integer with no lookup table in the database and is reported as "
                 "stored. ZTEXT on these rows is usually empty; where present it is "
                 "reported verbatim.",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/ChatStorage.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | WhatsApp Messenger 23.11.80 | 42 rows",
            "ctf2020_ios12": "iOS 12.4 | net.whatsapp.WhatsApp | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | WhatsApp Messenger 25.26.72 | 46 rows",
            "felix23_ios16": "iOS 16.5 | WhatsApp Messenger 23.12.76 | 6 rows",
            "felix_ios17": "iOS 17.6.1 | WhatsApp Messenger 24.17.78 | 3 rows",
            "fsfull002_ios17": "iOS 17.1 | WhatsApp Messenger 23.8.78 | 25 rows",
            "hc_ios18_7": "iOS 18.7.8 | WhatsApp Messenger 26.14.76 | 13 rows",
            "hc_ios26": "iOS 26.5.2 | 13 rows",
            "hickman_ios13": "iOS 13.3.1 | WhatsApp Messenger 2.20.31 | 5 rows",
            "hickman_ios14": "iOS 14.3 | WhatsApp Messenger 2.21.20 | 11 rows",
            "hickman_ios15": "iOS 15 | 21 rows",
            "iphone11_ios17": "iOS 17.3 | WhatsApp Messenger 24.15.1 | 33 rows",
            "otto_ios17": "iOS 17.5.1 | WhatsApp Messenger 24.13.79 | 1684 rows",
        },
    },
    "whatsAppGroupMembershipChanges": {
        "name": "WhatsApp - Group Membership Changes",
        "description": "WhatsApp group membership change log (ChatStorage.sqlite ZWAGROUPMEMBERSCHANGE)",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "One row per entry in ZWAGROUPMEMBERSCHANGE: change timestamp, an integer "
                 "change type (no lookup table in the database; reported as stored), the "
                 "group JID and the affected member JIDs as stored. In the tested images "
                 "only one image (iOS 17.5.1) had rows; the table exists empty on the "
                 "others that carry it.",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/ChatStorage.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | WhatsApp Messenger 23.11.80 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | net.whatsapp.WhatsApp | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | WhatsApp Messenger 25.26.72 | 0 rows",
            "felix23_ios16": "iOS 16.5 | WhatsApp Messenger 23.12.76 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | WhatsApp Messenger 24.17.78 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | WhatsApp Messenger 23.8.78 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | WhatsApp Messenger 26.14.76 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | WhatsApp Messenger 2.20.31 | 0 rows",
            "hickman_ios14": "iOS 14.3 | WhatsApp Messenger 2.21.20 | 0 rows",
            "hickman_ios15": "iOS 15 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | WhatsApp Messenger 24.15.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | WhatsApp Messenger 24.13.79 | 1856 rows",
        },
    },
}

import datetime

from scripts import blackboxprotobuf
from scripts.ilapfuncs import (artifact_processor,
                               convert_cocoa_core_data_ts_to_utc,
                               get_file_path, get_sqlite_db_records)


def _entries(value):
    """A repeated protobuf field decodes as a list only when it has more than
    one entry; normalize to a list."""
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _text(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    return '' if value is None else str(value)


def _ts_ms(value):
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000,
                                               tz=datetime.timezone.utc)
    except (TypeError, ValueError, OSError, OverflowError):
        return ''


_INFO_QUERY = '''
SELECT i.Z_PK, i.ZRECEIPTINFO, m.ZISFROMME, m.ZTEXT, m.ZFROMJID, m.ZTOJID,
       m.ZMESSAGEDATE, cs.ZCONTACTJID, cs.ZPARTNERNAME
FROM ZWAMESSAGEINFO i
LEFT JOIN ZWAMESSAGE m ON m.ZMESSAGEINFO = i.Z_PK
LEFT JOIN ZWACHATSESSION cs ON cs.Z_PK = m.ZCHATSESSION
'''


def _iter_field7(source_path):
    """Yield (subrecord dict, parent-row record) for every field-7 entry in
    every populated ZRECEIPTINFO blob."""
    for record in get_sqlite_db_records(source_path, _INFO_QUERY):
        blob = record['ZRECEIPTINFO']
        if not blob:
            continue
        try:
            decoded, _ = blackboxprotobuf.decode_message(blob)
        except Exception:  # pylint: disable=broad-exception-caught
            # blackboxprotobuf raises library-internal types; an undecodable
            # blob is reported by absence, never by crashing the artifact
            continue
        for sub in _entries(decoded.get('7')):
            if isinstance(sub, dict):
                yield sub, record


@artifact_processor
def whatsAppReactions(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'ChatStorage.sqlite')
    data_list = []
    if source_path:
        for sub, record in _iter_field7(source_path):
            direction = 'Outgoing' if record['ZISFROMME'] == 1 else 'Incoming'
            common = (record['ZCONTACTJID'], record['ZPARTNERNAME'], direction,
                      convert_cocoa_core_data_ts_to_utc(record['ZMESSAGEDATE']),
                      record['ZTEXT'])
            for entry in _entries(sub.get('1')):
                if not isinstance(entry, dict):
                    continue
                data_list.append((_ts_ms(entry.get('4')), _text(entry.get('3')),
                                  _text(entry.get('2')), 'field 7.1',
                                  *common, _text(entry.get('1'))))
            for entry in _entries(sub.get('2')):
                if not isinstance(entry, dict):
                    continue
                data_list.append((_ts_ms(entry.get('3')), _text(entry.get('2')),
                                  '', 'field 7.2',
                                  *common, _text(entry.get('1'))))

    data_headers = (('Reaction Timestamp', 'datetime'), 'Reaction', 'Reactor JID',
                    'Record Shape', 'Chat JID', 'Chat Name',
                    'Message Direction', ('Message Timestamp', 'datetime'),
                    'Message', 'Message Key ID')
    return data_headers, data_list, source_path


@artifact_processor
def whatsAppChannelReactionTallies(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'ChatStorage.sqlite')
    data_list = []
    if source_path:
        for sub, record in _iter_field7(source_path):
            for group in _entries(sub.get('3')):
                if not isinstance(group, dict):
                    continue
                for entry in _entries(group.get('1')):
                    if not isinstance(entry, dict):
                        continue
                    data_list.append((
                        convert_cocoa_core_data_ts_to_utc(record['ZMESSAGEDATE']),
                        _text(entry.get('1')), entry.get('2'),
                        record['ZCONTACTJID'], record['ZPARTNERNAME'],
                        record['ZTEXT']))

    data_headers = (('Message Timestamp', 'datetime'), 'Reaction',
                    'Count (as stored)', 'Chat JID', 'Chat Name', 'Message')
    return data_headers, data_list, source_path


@artifact_processor
def whatsAppGroupEvents(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'ChatStorage.sqlite')
    data_list = []
    if source_path:
        query = '''
        SELECT m.ZMESSAGEDATE, m.ZGROUPEVENTTYPE, m.ZMESSAGETYPE, m.ZTEXT,
               m.ZFROMJID, cs.ZCONTACTJID, cs.ZPARTNERNAME
        FROM ZWAMESSAGE m
        LEFT JOIN ZWACHATSESSION cs ON cs.Z_PK = m.ZCHATSESSION
        WHERE m.ZGROUPEVENTTYPE IS NOT NULL AND m.ZGROUPEVENTTYPE != 0
        ORDER BY m.ZMESSAGEDATE
        '''
        for record in get_sqlite_db_records(source_path, query):
            data_list.append((
                convert_cocoa_core_data_ts_to_utc(record['ZMESSAGEDATE']),
                record['ZGROUPEVENTTYPE'], record['ZMESSAGETYPE'],
                record['ZTEXT'], record['ZFROMJID'],
                record['ZCONTACTJID'], record['ZPARTNERNAME']))

    data_headers = (('Event Timestamp', 'datetime'),
                    'Group Event Type (as stored)', 'Message Type (as stored)',
                    'Text', 'From JID', 'Chat JID', 'Chat Name')
    return data_headers, data_list, source_path


@artifact_processor
def whatsAppGroupMembershipChanges(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'ChatStorage.sqlite')
    data_list = []
    if source_path:
        query = '''
        SELECT ZCHANGEDATE, ZCHANGETYPE, ZGROUPJID, ZMEMBERJIDS
        FROM ZWAGROUPMEMBERSCHANGE
        ORDER BY ZCHANGEDATE
        '''
        for record in get_sqlite_db_records(source_path, query):
            data_list.append((
                convert_cocoa_core_data_ts_to_utc(record['ZCHANGEDATE']),
                record['ZCHANGETYPE'], record['ZGROUPJID'],
                record['ZMEMBERJIDS']))

    data_headers = (('Change Timestamp', 'datetime'),
                    'Change Type (as stored)', 'Group JID', 'Member JIDs')
    return data_headers, data_list, source_path
