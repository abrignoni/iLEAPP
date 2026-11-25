"""Snapchat friending badges, named from the friending notification store and the snapchatter store."""

__artifacts_v2__ = {
    "snapchatFriendingBadges": {
        "name": "Snapchat - Friending Badges",
        "description": "Rows of friending_badge_data in Snapchat's Documents/friending_badge_data.db (the badge time, its "
                       "source and the user it names) and users of the friending notification store that have no badge, with"
                       " the names the app's friending notification and snapchatter stores hold for each user.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-25",
        "requirements": "none",
        "category": "Snapchat",
        "notes": "Reads friending_badge_data in Documents/friending_badge_data.db, with its -wal, in each app "
                 "container that holds one, and names each badge's user from two stores in the same container: "
                 "Documents/friending_notification_snapchatter.db and the snapchatter table of "
                 "Documents/user_scoped/<account hash>/DocObjects/primary.docobjects, read with the helpers of "
                 "Snapchat - Snapchatter Records. On the 5 tested images that hold the two friending stores, each main"
                 " file was one page with no table in it, and every table and row was read from the -wal. Names are "
                 "matched by user id within one container only. One row per friending_badge_data row, plus one row for"
                 " each friending_notification_snapchatter user with no badge, with Badge Timestamp and Badge Source "
                 "empty (1 row, on wilkerson_iphone16_ios26). The table's own CREATE TABLE comments describe timestamp"
                 " as when the badge was created, source as the source of the badge used mostly for logging, and "
                 "userID as the user the badge represents, which can be null for badges that need no Snapchatter. No "
                 "tested row had a null userID. Badge Timestamp is timestamp read as Unix seconds in UTC; the comments"
                 " do not give the unit. On hc_ios18_7 and iphone12_ios18 the newest Badge Timestamp equalled, to the "
                 "second, the UTC modified time the extraction zip records for the -wal (its extended timestamp field "
                 "on hc_ios18_7, its NTFS field on iphone12_ios18). hill_iphone15pro_ios26 and "
                 "wilkerson_iphone16_ios26 are Cellebrite CLBX zips, which record each file's modified time in "
                 "metadata.msgpack. On wilkerson_iphone16_ios26 that record puts the -wal's modified time about 6.9 "
                 "days after the newest Badge Timestamp. On hill_iphone15pro_ios26 it puts the -wal's modified time "
                 "about 30.5 hours before the one Badge Timestamp its 5 rows share, which this reading does not "
                 "explain. Badge Source is source as stored. The tested values were INCOMING_FRIEND_REQUEST (84 rows: "
                 "83 on iphone12_ios18 and 1 on hc_ios18_7), AVAILABLE_FRIEND_SUGGESTIONS (11), "
                 "UNVIEWED_FRIEND_SUGGESTIONS (5) and RECENTLY_JOINED_SUGGESTIONS (1); what each means beyond its name"
                 " is not established. On hill_iphone15pro_ios26 Badge Timestamp and Badge Source each held one value "
                 "on all 5 rows. Username (snapchatter store) and Display Name (snapchatter store) are the username "
                 "index value and the display name of that user's snapchatter row, as Snapchatter Records reads them; "
                 "they are set on 93 of the 102 rows. Display Name (friending notification), Mutable Name (friending "
                 "notification) and Suggest Reason (friending notification) are displayName, mutableName and "
                 "suggestReason of that user's friending_notification_snapchatter row. Display Name (friending "
                 "notification) and Mutable Name (friending notification) are set on 13 rows (11 on "
                 "wilkerson_iphone16_ios26, 2 on iphone12_ios18) and Suggest Reason (friending notification) on 2. On "
                 "the 4 rows that have names from both stores, Display Name (snapchatter store) equalled Display Name "
                 "(friending notification) and Username (snapchatter store) equalled Mutable Name (friending "
                 "notification). On hc_ios18_7 and hill_iphone15pro_ios26 the notification table was empty, so Display"
                 " Name (friending notification), Mutable Name (friending notification) and Suggest Reason (friending "
                 "notification) have no value on any row there. On the tested images every row had a name from at "
                 "least one store. Not shown from friending_notification_snapchatter: processingTimestamp, which held "
                 "-1.0 on all 13 rows, incomingFriendInfoAddedByFriendTs, which held 0 on all 13, "
                 "incomingFriendInfoSubtext, which was null on all 13, abbreviatedSuggestReason, and "
                 "incomingFriendInfoFriendType, notificationType, isFromMyContact and the bitmoji and token columns, "
                 "whose meanings are not established. On dexter_ios18 both friending stores were present and empty. On"
                 " abe_ios16, iphone11_ios17, iphone14plus_ios18_mvs2025, magnet_ios16 and otto_ios17 the extraction "
                 "zip held neither friending store.",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 5 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 85 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 11 rows",
        },
        "paths": (
            '*/mobile/Containers/Data/Application/*/Documents/friending_badge_data.db*',
            '*/mobile/Containers/Data/Application/*/Documents/friending_notification_snapchatter.db*',
            '*/mobile/Containers/Data/Application/*/Documents/user_scoped/*/DocObjects/primary.docobjects*',
        ),
        "output_types": "standard",
        "artifact_icon": "user-plus",
    },
}

import datetime
import os
import sqlite3

from scripts.artifacts.snapchat import _app_container, _friend_records
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

_UNIX = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
_BADGES = 'friending_badge_data.db'
_NOTIFICATIONS = 'friending_notification_snapchatter.db'
_DOC_STORE = 'primary.docobjects'


def _seconds(value):
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        return ''
    try:
        return _UNIX + datetime.timedelta(seconds=value)
    except OverflowError:
        return ''


def _fetch(path, sql):
    db = open_sqlite_db_readonly(path)
    if db is None:
        return None
    try:
        db.row_factory = sqlite3.Row
        return [dict(r) for r in db.execute(sql)]
    except sqlite3.Error as error:
        logfunc(f'Snapchat - Friending Badges: could not read {os.path.basename(path)}: {error}')
        return None
    finally:
        db.close()


def _by_container(context):
    """{app container: {store name: [paths]}} for the three stores, sidecars and folders left out."""
    found = {}
    for path in context.get_files_found():
        path = str(path)
        name = os.path.basename(path)
        if name not in (_BADGES, _NOTIFICATIONS, _DOC_STORE) or os.path.isdir(path):
            continue
        if name == _DOC_STORE and os.path.basename(os.path.dirname(path)) != 'DocObjects':
            continue
        container = _app_container(path)
        if container:
            found.setdefault(container, {}).setdefault(name, []).append(path)
    return found


@artifact_processor
def snapchatFriendingBadges(context):
    data_list = []
    sources = []
    for _container, stores in sorted(_by_container(context).items()):
        badge_paths = sorted(set(stores.get(_BADGES, [])))
        notification_paths = sorted(set(stores.get(_NOTIFICATIONS, [])))
        if not badge_paths and not notification_paths:
            continue
        snapchatters = {}
        named_from = []
        for path in sorted(set(stores.get(_DOC_STORE, []))):
            records = _friend_records(path)
            if records:
                snapchatters.update(records)
                named_from.append(path)
        notified = {}
        for path in notification_paths:
            rows = _fetch(path, 'SELECT userId, displayName, mutableName, suggestReason '
                                'FROM friending_notification_snapchatter ORDER BY id')
            if rows is None:
                continue
            sources.append(path)
            for row in rows:
                notified.setdefault(row['userId'], row)
        badged = set()
        for path in badge_paths:
            rows = _fetch(path, 'SELECT id, userID, timestamp, source FROM friending_badge_data ORDER BY id')
            if rows is None:
                continue
            sources.append(path)
            for row in rows:
                user = row['userID'] or ''
                badged.add(user)
                data_list.append(_row(_seconds(row['timestamp']), row['source'], user, snapchatters, notified))
        for user in notified:
            if user not in badged:
                data_list.append(_row('', '', user, snapchatters, notified))
        sources.extend(named_from)

    data_headers = (('Badge Timestamp', 'datetime'), 'Badge Source (as stored)', 'User ID',
                    'Username (snapchatter store)', 'Display Name (snapchatter store)',
                    'Display Name (friending notification)', 'Mutable Name (friending notification)',
                    'Suggest Reason (friending notification)')
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


def _row(created, source, user, snapchatters, notified):
    username, display = snapchatters.get(user, ('', ''))
    note = notified.get(user) or {}
    return (created, source or '', user, username, display, note.get('displayName') or '',
            note.get('mutableName') or '', note.get('suggestReason') or '')
