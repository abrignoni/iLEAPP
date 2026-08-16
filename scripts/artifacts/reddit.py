__artifacts_v2__ = {
    "reddit_chat_users": {
        "name": "Reddit Chat Users",
        "description": "Chat participants cached in RoomsUsersService.db: display name, "
                       "Matrix user id and the store's own access and update dates.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Reddit",
        "notes": (
            "The store is a Core Data key-value cache under "
            "Library/Caches/MatrixChat/roomsAccount/<account>/MatrixUsers-*/. Each row is "
            "keyed by the Matrix user id (@t2_<reddit id>:reddit.com) and its value is "
            "JSON preceded by a single 0x01 byte, which is stripped before parsing. The "
            "display name, user id and updated date are read from the value's exists._0 "
            "object.\n"
            "Is Current App User is the value's own is_current flag; on the tested image "
            "exactly one of the four rows carried it. Updated Date is Unix milliseconds "
            "from the value, while Access Date and Update Date are the row's Core Data "
            "Apple absolute timestamps, which record when the app touched the cache "
            "rather than when the account changed.\n"
            "The reference documents this store at a redditAccount/RedditUsers-* path "
            "holding user identity JSON. On the tested image that path holds a different "
            "database (see Reddit Users) and this content sits under "
            "roomsAccount/MatrixUsers-*, so both locations are matched.\n"
            "Reference: Arun Kalackattu Hari, 'Forensic Analysis of Reddit App: iOS and "
            "Android', dfdive.com, 06 April 2026, https://dfdive.com/articles/"
        ),
        "paths": (
            '*/Library/Caches/MatrixChat/roomsAccount/*/MatrixUsers-*/RoomsUsersService.db*',
            '*/Library/Caches/MatrixChat/redditAccount/*/RedditUsers-*/RoomsusersService.db*',
        ),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | 4 rows (1 flagged as the current app user)",
            "otto_ios17": "iOS 17.5.1 | 0 rows (store present, no entries)",
            "hickman_ios15": "iOS 15.3.1 | no RoomsUsersService.db found",
            "hickman_ios14": "iOS 14.3 | no RoomsUsersService.db found",
            "hickman_ios13": "iOS 13.3.1 | no RoomsUsersService.db found",
            "ctf2020_ios12": "iOS 12.4 | no RoomsUsersService.db found",
        },
    },
    "reddit_users": {
        "name": "Reddit Users",
        "description": "Reddit accounts cached in RedditUsersStore.db: display name, "
                       "account id, karma totals and profile creation date as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Reddit",
        "notes": (
            "A Core Data key-value cache under "
            "Library/Caches/MatrixChat/redditAccount/<account>/RedditUsers-*/, keyed by "
            "the Reddit account id (t2_<id>). The value is JSON preceded by a single "
            "0x01 byte, which is stripped before parsing.\n"
            "Karma is reported in total and by source as the app cached it. Profile "
            "Created is the value's profile.createdAt. The verified, NSFW, blocked and "
            "accepting-chats flags are reported as stored; a cached row records what the "
            "app knew about the account, not a current state.\n"
            "Access Date and Update Date are the row's Core Data Apple absolute "
            "timestamps and record when the app wrote the cache entry.\n"
            "Reference: Arun Kalackattu Hari, 'Forensic Analysis of Reddit App: iOS and "
            "Android', dfdive.com, 06 April 2026, https://dfdive.com/articles/"
        ),
        "paths": ('*/Library/Caches/MatrixChat/redditAccount/*/RedditUsers-*/RedditUsersStore.db*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | 4 rows",
            "otto_ios17": "iOS 17.5.1 | 1 row",
            "hickman_ios15": "iOS 15.3.1 | no RedditUsersStore.db found",
            "hickman_ios14": "iOS 14.3 | no RedditUsersStore.db found",
            "hickman_ios13": "iOS 13.3.1 | no RedditUsersStore.db found",
            "ctf2020_ios12": "iOS 12.4 | no RedditUsersStore.db found",
        },
    },
    "reddit_subreddit_subscriptions": {
        "name": "Reddit Subreddit Subscriptions",
        "description": "Communities from the SubredditSubscriptions archive: name, title, "
                       "subscriber count, creation date and the app's subscribed, "
                       "favourite and muted flags as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Reddit",
        "notes": (
            "Documents/release02/accountData/<reddit id>/SubredditSubscriptions is an "
            "NSKeyedArchiver property list holding one entry per community, deserialised "
            "before reading. The account folder name is the Reddit id without its t2_ "
            "prefix and is reported as the Account column; an 'anonymous' folder is the "
            "logged-out store.\n"
            "Community ID is the t5_ identifier the reference documents as the value that "
            "links a community across the app's other stores. Subscribed, Favourite, Muted "
            "and NSFW come from the entry's own boolean fields. Subreddit Type is reported "
            "as stored because no source for the integer was verified.\n"
            "Subscriber and active counts are values the app cached from the server at "
            "some point before extraction, not measurements made here.\n"
            "Reference: Arun Kalackattu Hari, 'Forensic Analysis of Reddit App: iOS and "
            "Android', dfdive.com, 06 April 2026, https://dfdive.com/articles/"
        ),
        "paths": ('*/Documents/release02/accountData/*/SubredditSubscriptions',),
        "output_types": "standard",
        "artifact_icon": "users-group",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 151 rows",
            "otto_ios17": "iOS 17.5.1 | 16 rows",
            "iphone11_ios17": "iOS 17.3 | 12 rows",
            "hickman_ios15": "iOS 15.3.1 | 12 rows",
            "hickman_ios14": "iOS 14.3 | 12 rows",
            "hickman_ios13": "iOS 13.3.1 | 12 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 8 rows",
            "jess_ios15": "iOS 15.0.2 | 5 rows",
        },
    },
    "reddit_chats": {
        "name": "Reddit Chats",
        "description": "Parses chat messages from Reddit",
        "author": "@stark4n6",
        "creation_date": "2026-04-28",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Reddit",
        "notes": "An m.room.message event whose content carries no msgtype is reported as MESSAGE DELETED, matching the Matrix redaction algorithm, which strips the content keys of redacted m.room.message events. Reference: Matrix Specification v1.11, 'Room Version 11 - Redactions', https://spec.matrix.org/v1.11/rooms/v11/#redactions",
        "paths": (
            '*/Library/Caches/MatrixChat/roomsAccount/*/Account-*/Account.db*',
            '*/Library/Caches/MatrixChat/roomsAccount/*/Downloads-*/ContentService.db*',
            '*/Library/Caches/MatrixChat/roomsAccount/*/Downloads-*/Files/*'
        ),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | Reddit 2023.50.1 | 44 rows",
            "otto_ios17": "iOS 17.5.1 | Reddit 2024.33.0 | 0 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Room ID",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Server Timestamp",
                "senderColumn": "Sender Display Name",
                "mediaColumn": "Attachment"
            }
        },
    }
}

import json

from os.path import basename, dirname

from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, attach_sqlite_db_readonly, check_in_media, get_plist_file_content, convert_unix_ts_to_utc, convert_cocoa_core_data_ts_to_utc


def _reddit_owner_id(source_path):
    """Own Matrix user id from the .m.rule.invite_for_me push rule (its
    state_key pattern is the account's own id, server-populated)."""
    rows = get_sqlite_db_records(
        source_path,
        "SELECT ZDATA FROM ZACCOUNTSTORAGEACCOUNTDATAITEM WHERE ZEVENTTYPEFIELD = 'm.push_rules'")
    for (blob,) in rows:
        try:
            rules = json.loads(blob.decode('utf-8', 'replace') if isinstance(blob, (bytes, bytearray)) else blob)
        except (json.JSONDecodeError, TypeError, ValueError):
            continue
        for section in ((rules.get('content') or {}).get('global') or {}).values():
            if not isinstance(section, list):
                continue
            for rule in section:
                if rule.get('rule_id') == '.m.rule.invite_for_me':
                    for cond in rule.get('conditions') or []:
                        if cond.get('key') == 'state_key' and cond.get('pattern'):
                            return cond['pattern']
    return ''

@artifact_processor
def reddit_chats(context):
    data_list = []
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "Account.db")
    attachDB = get_file_path(files_found, "ContentService.db")
    
    attach_query = attach_sqlite_db_readonly(attachDB, 'content')
    
    query = '''
    SELECT 
    datetime(m.ZORIGINSERVERDATE + 978307200,'unixepoch') AS 'Timestamp',
	substr(m.ZITEMIDFIELD, instr(m.ZITEMIDFIELD, '|') + 1) AS 'Event ID',
    (SELECT json_extract(u.ZDATA, '$.content.displayname') 
     FROM ZACCOUNTSTORAGETIMELINEITEM u 
     WHERE u.ZSTATEKEYFIELD = m.ZSENDERFIELD 
     AND u.ZEVENTTYPEFIELD = 'm.room.member'
     LIMIT 1) AS 'Sender',
	 m.ZSENDERFIELD,
    GROUP_CONCAT(
        DISTINCT json_extract(rec.ZDATA, '$.content.displayname')
    ) AS 'Recipient(s)',
	CASE 
		WHEN m.ZEVENTTYPEFIELD = 'm.room.message' THEN 'Message'
		WHEN m.ZEVENTTYPEFIELD = 'm.reaction' THEN 'Reaction'
		WHEN m.ZEVENTTYPEFIELD = 'm.room.redaction' THEN 'Deletion for Event ID: ' || json_extract(m.ZDATA, '$.redacts')
		ELSE m.ZEVENTTYPEFIELD
	END AS 'Event Type',
	CASE
		WHEN json_extract(m.ZDATA, '$.content.msgtype') IS NULL AND m.ZEVENTTYPEFIELD = 'm.room.message' THEN 'MESSAGE DELETED'
		WHEN json_extract(m.ZDATA, '$.content.msgtype') = 'm.text' THEN 'Text'
		WHEN json_extract(m.ZDATA, '$.content.msgtype') = 'm.image' THEN 'Image'
		ELSE json_extract(m.ZDATA, '$.content.msgtype')
	END AS 'Message Type',
	CASE
		WHEN m.ZEVENTTYPEFIELD = 'm.reaction' THEN json_extract(m.ZDATA, '$.content."m.relates_to".key')
		ELSE json_extract(m.ZDATA, '$.content.body')
	END AS 'Message',
    att.ZFILENAME AS 'Attachment File',
    substr(m.ZITEMIDFIELD, 1, instr(m.ZITEMIDFIELD, '|') - 1) AS 'Room ID',
	m.ZDATA
    FROM ZACCOUNTSTORAGETIMELINEITEM AS m
    LEFT JOIN content.ZKEYVALUESTORAGEBASEELEMENT AS att
        ON json_extract(m.ZDATA, '$.content.url') = att.ZKEY
    LEFT JOIN ZACCOUNTSTORAGETIMELINEITEM AS rec
        ON substr(rec.ZITEMIDFIELD, 1, instr(rec.ZITEMIDFIELD, '|') - 1) = substr(m.ZITEMIDFIELD, 1, instr(m.ZITEMIDFIELD, '|') - 1)
        AND rec.ZEVENTTYPEFIELD = 'm.room.member'
        AND rec.ZSTATEKEYFIELD != m.ZSENDERFIELD  -- Don't list the sender as a receiver
        AND json_extract(rec.ZDATA, '$.content.membership') = 'join'
    WHERE m.ZEVENTTYPEFIELD = 'm.room.message' OR m.ZEVENTTYPEFIELD = 'm.room.redaction' OR m.ZEVENTTYPEFIELD = 'm.reaction'
    GROUP BY m.ZORIGINSERVERDATE, m.ZITEMIDFIELD
    ORDER BY "Timestamp" ASC;
    '''

    data_headers = (('Server Timestamp', 'datetime'),'Event ID', 'Sender Display Name','Sender ID','Recipient(s)','Event Type','Message Type','Message','Attachment Cached Name',('Attachment','media'),'Room ID','Direction')

    owner_id = _reddit_owner_id(source_path)

    db_records = get_sqlite_db_records(source_path, query, attach_query)

    for record in db_records:
        attachment = ''
        for x in files_found:
            if str(record[8]) in x:
                attachment = check_in_media(x,str(record[8]))
        if owner_id and record[3]:
            direction = 'Outgoing' if record[3] == owner_id else 'Incoming'
        else:
            direction = ''
        data_list.append((record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7], record[8], attachment, record[9], direction))

    return data_headers, data_list, source_path

def _kv_store_rows(source_path):
    """(key, decoded JSON value, access date, update date) from a Core Data key-value store.

    The stored value is JSON preceded by a single 0x01 byte, so the prefix is stripped
    before parsing. A row whose value does not parse is skipped.
    """
    records = get_sqlite_db_records(
        source_path,
        "SELECT ZKEY, ZVALUE, ZACCESSDATE, ZUPDATEDATE FROM ZKEYVALUESTORAGEBASEELEMENT")
    for key, value, access_date, update_date in records:
        if isinstance(value, (bytes, bytearray)):
            text = bytes(value).lstrip(b'\x01').decode('utf-8', 'replace')
        else:
            text = str(value or '')
        try:
            decoded = json.loads(text)
        except (json.JSONDecodeError, TypeError, ValueError):
            continue
        if isinstance(decoded, dict):
            yield key, decoded, access_date, update_date


def _apple_absolute(value):
    if value in (None, ''):
        return ''
    try:
        return convert_cocoa_core_data_ts_to_utc(float(value))
    except (TypeError, ValueError):
        return ''


def _yes_no(value):
    return 'YES' if value else 'NO'


@artifact_processor
def reddit_chat_users(context):
    """ see artifact description """
    data_list = []
    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.lower().endswith(('roomsusersservice.db',)):
            continue
        source_path = source_path or file_found
        source_file = context.get_relative_path(file_found)
        for key, decoded, access_date, update_date in _kv_store_rows(file_found):
            entry = (decoded.get('exists') or {}).get('_0') or {}
            data_list.append((
                convert_unix_ts_to_utc(entry.get('updated_date')) if entry.get('updated_date') else '',
                _apple_absolute(access_date),
                _apple_absolute(update_date),
                entry.get('display_name', ''),
                entry.get('user_id', '') or key,
                _yes_no(entry.get('is_current')),
                key,
                source_file,
            ))
    data_headers = (
        ('Updated Date', 'datetime'),
        ('Access Date', 'datetime'),
        ('Store Update Date', 'datetime'),
        'Display Name',
        'Matrix User ID',
        'Is Current App User',
        'Store Key',
        'Source File',
    )
    return data_headers, data_list, source_path


@artifact_processor
def reddit_users(context):
    """ see artifact description """
    data_list = []
    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.lower().endswith('redditusersstore.db'):
            continue
        source_path = source_path or file_found
        source_file = context.get_relative_path(file_found)
        for key, decoded, access_date, update_date in _kv_store_rows(file_found):
            karma = decoded.get('karma') or {}
            profile = decoded.get('profile') or {}
            created = profile.get('createdAt')
            data_list.append((
                convert_unix_ts_to_utc(created) if created else '',
                _apple_absolute(access_date),
                _apple_absolute(update_date),
                decoded.get('displayName', ''),
                decoded.get('id', '') or key,
                karma.get('total'),
                karma.get('fromPosts'),
                karma.get('fromComments'),
                _yes_no(decoded.get('isVerified')),
                _yes_no(profile.get('isNsfw')),
                _yes_no(decoded.get('isBlocked')),
                _yes_no(decoded.get('isAcceptingChats')),
                _yes_no(decoded.get('isAcceptingPMs')),
                source_file,
            ))
    data_headers = (
        ('Profile Created', 'datetime'),
        ('Access Date', 'datetime'),
        ('Store Update Date', 'datetime'),
        'Display Name',
        'Reddit ID',
        'Total Karma',
        'Karma From Posts',
        'Karma From Comments',
        'Is Verified',
        'Profile Is NSFW',
        'Is Blocked',
        'Is Accepting Chats',
        'Is Accepting PMs',
        'Source File',
    )
    return data_headers, data_list, source_path


@artifact_processor
def reddit_subreddit_subscriptions(context):
    """ see artifact description """
    data_list = []
    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('SubredditSubscriptions'):
            continue
        source_path = source_path or file_found
        source_file = context.get_relative_path(file_found)
        account = basename(dirname(file_found))
        entries = get_plist_file_content(file_found)
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            data_list.append((
                entry.get('kCreatedDateKey', ''),
                entry.get('displayName', ''),
                entry.get('title', ''),
                entry.get('PrimaryKey', ''),
                account,
                _yes_no(entry.get('subscirbedBoolean')),
                _yes_no(entry.get('favoritedBoolean')),
                _yes_no(entry.get('mutedBoolean')),
                _yes_no(entry.get('nsfwBoolean')),
                entry.get('subscribedCount'),
                entry.get('activeCount'),
                entry.get('kSubredditType'),
                entry.get('public_description', ''),
                entry.get('kURLKey', ''),
                source_file,
            ))
    data_headers = (
        ('Community Created', 'datetime'),
        'Community',
        'Title',
        'Community ID',
        'Account',
        'Subscribed',
        'Favourite',
        'Muted',
        'NSFW',
        'Subscriber Count',
        'Active Count',
        'Subreddit Type (as stored)',
        'Public Description',
        'URL',
        'Source File',
    )
    return data_headers, data_list, source_path
