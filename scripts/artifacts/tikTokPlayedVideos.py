"""TikTok played item ids from the friends feed store and played video ids from the follow feed store."""

__artifacts_v2__ = {
    "tiktok_friends_feed_played": {
        "name": "TikTok - Friends Feed Played Items",
        "description": "Rows of the playedItemIds_<account> tables in TikTok's "
                       "Library/Caches/com.friends.feed.deduplicate/record.db: the awemeId with its record and "
                       "latest played times.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-24",
        "last_update_date": "2026-11-24",
        "requirements": "none",
        "category": "TikTok",
        "notes": "Reads every table named playedItemIds_<account> in record.db, with its -wal, in TikTok's "
                 "Library/Caches/com.friends.feed.deduplicate folder, in a container owned by com.zhiliaoapp.musically"
                 " according to its own .com.apple.mobile_container_manager.metadata.plist; a store in a container "
                 "owned by another app, or whose owner cannot be established, is skipped and logged. No tested image "
                 "had such a store, so the skip was exercised on constructed test data only. "
                 "com.friends.feed.deduplicate is the app's folder name; that the rows describe a friends feed is not "
                 "established. playedItemIds is the app's table name; whether a row means the item was played on "
                 "screen is not established. One row per table row. Account UID is the table name after "
                 "playedItemIds_. On the 8 images with rows in sample_data it equalled an account folder name under "
                 "Library/Application Support/ChatFiles, and each image held one such table, so Account UID held one "
                 "value per image; it is kept because it is the only column naming the table a row came from. A store "
                 "with more than one table was read on constructed test data only. Aweme ID is awemeId as stored. "
                 "Latest Played Timestamp and Record Timestamp are latestPlayedTimeStamp and recordTimeStamp, REAL "
                 "values read as Unix seconds in UTC; the names are the table's own, and what each moment means is not"
                 " established beyond them. Latest Played Timestamp and Record Timestamp are identical on 230 of the "
                 "247 rows, including every row of iphone11_ios17, iphone12_ios18, iphone14plus_ios18_mvs2025 and "
                 "wilkerson_iphone16_ios26; they differ on 17 rows of the other four images. On abe_ios16, "
                 "iphone11_ios17 and otto_ios17, 81 of the 82 Aweme IDs equal the aid of a TikTok - Watch History row,"
                 " and on all 81 Latest Played Timestamp is within 60 seconds of that row's Timestamp. User ID is "
                 "userID as stored; whose id it is is not established, and it equalled the Account UID on 2 of the 159"
                 " rows that have one. The column is absent from the older table versions seen, so User ID has no "
                 "value on any row of abe_ios16, iphone11_ios17, iphone14plus_ios18_mvs2025 and otto_ios17. It is also"
                 " empty on 4 of the 108 rows of dexter_ios18. Not shown: scene, latestPlayedScene, pageType and "
                 "isStory, integers whose meaning is not established. The rows reported are the store's current state "
                 "with the -wal applied. On hill_iphone15pro_ios26, iphone12_ios18 and iphone14plus_ios18_mvs2025 the "
                 "4 KB main file held no rows without its -wal, and on abe_ios16 it held 8 of the 54, so the -wal has "
                 "to be in the extraction. On dexter_ios18, iphone11_ios17 and wilkerson_iphone16_ios26 the main file "
                 "read without its -wal held 44, 3 and 5 rows that are not in the current state and are not reported. "
                 "TikTok - Watch History returned no rows on dexter_ios18, hill_iphone15pro_ios26, iphone12_ios18, "
                 "iphone14plus_ios18_mvs2025 and wilkerson_iphone16_ios26, and those archives list no file under "
                 "Documents/WatchHistory.",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 54 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 108 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 51 rows",
            "iphone11_ios17": "iOS 17.3 | 3 rows",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 2 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 25 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 3 rows",
        },
        "paths": (
            '*/mobile/Containers/Data/Application/*/Library/Caches/com.friends.feed.deduplicate/record.db*',
            '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
        ),
        "output_types": "standard",
        "artifact_icon": "play",
    },
    "tiktok_follow_feed_played": {
        "name": "TikTok - Follow Feed Played Videos",
        "description": "Rows of the playedItemIds_<account> tables in TikTok's "
                       "Documents/follow_feed/played_videos_recorder.db: the gid with its createTime.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-24",
        "last_update_date": "2026-11-24",
        "requirements": "none",
        "category": "TikTok",
        "notes": "Reads every table named playedItemIds_<account> in played_videos_recorder.db, with its -wal, in "
                 "TikTok's Documents/follow_feed folder, in a container owned by com.zhiliaoapp.musically according to"
                 " its own .com.apple.mobile_container_manager.metadata.plist; a store in a container owned by another"
                 " app, or whose owner cannot be established, is skipped and logged. No tested image had such a store."
                 " follow_feed is the app's folder name; that the rows describe a following feed is not established. "
                 "One row per table row. GID is gid as stored, and Create Time is createTime, a REAL value read as "
                 "Unix seconds in UTC; what event it marks is not established. Account UID is the table name after "
                 "playedItemIds_. On the 4 images with rows in sample_data it equalled an account folder name under "
                 "Library/Application Support/ChatFiles, and each image held one such table, so Account UID held one "
                 "value per image; it is kept because it is the only column naming the table a row came from. No "
                 "tested store held more than one table. 148 of the 210 GIDs equal an awemeId in the same image's "
                 "com.friends.feed.deduplicate/record.db, and on 141 of those 148 Create Time is within 60 seconds of "
                 "that row's recordTimeStamp. The rows reported are the store's current state with the -wal applied. "
                 "On dexter_ios18, hill_iphone15pro_ios26 and iphone12_ios18 the 4 KB main file held no rows without "
                 "its -wal, so the -wal has to be in the extraction. On wilkerson_iphone16_ios26 the main file read "
                 "without its -wal held 7 rows that are not in the current state and are not reported. TikTok - Watch "
                 "History returned no rows on the 4 images with rows, and those archives list no file under "
                 "Documents/WatchHistory.",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 157 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 50 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 2 rows",
        },
        "paths": (
            '*/mobile/Containers/Data/Application/*/Documents/follow_feed/played_videos_recorder.db*',
            '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
        ),
        "output_types": "standard",
        "artifact_icon": "play",
    },
}

import datetime
import os
import sqlite3

from scripts.artifacts.tikTok import _container_owners, _tiktok_owned
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

_UNIX = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
_PREFIX = 'playedItemIds_'


def _seconds(value):
    """Unix seconds stored as REAL, or '' when empty or unusable."""
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not value:
        return ''
    try:
        return _UNIX + datetime.timedelta(seconds=float(value))
    except (OverflowError, ValueError):
        return ''


def _stores(context, name, parent):
    found = []
    for path in context.get_files_found():
        path = str(path)
        if os.path.basename(path) == name and os.path.basename(os.path.dirname(path)) == parent \
                and not os.path.isdir(path):
            found.append(path)
    return _tiktok_owned(sorted(set(found)), _container_owners(context.get_files_found()))


def _tables(path, label):
    """[(account, [row dicts])] for each playedItemIds_<account> table, or None when unreadable."""
    db = open_sqlite_db_readonly(path)
    if db is None:
        return None
    try:
        db.row_factory = sqlite3.Row
        out = []
        names = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
        for name in sorted(n for n in names if n.startswith(_PREFIX)):
            quoted = name.replace('"', '""')
            out.append((name[len(_PREFIX):], [dict(r) for r in db.execute(f'SELECT * FROM "{quoted}"')]))
        return out
    except sqlite3.Error as error:
        logfunc(f'{label}: could not read {os.path.basename(path)}: {error}')
        return None
    finally:
        db.close()


@artifact_processor
def tiktok_friends_feed_played(context):
    data_list = []
    sources = []
    for path in _stores(context, 'record.db', 'com.friends.feed.deduplicate'):
        tables = _tables(path, 'TikTok - Friends Feed Played Items')
        if tables is None:
            continue
        sources.append(path)
        for account, rows in tables:
            for row in rows:
                data_list.append((_seconds(row.get('latestPlayedTimeStamp')), _seconds(row.get('recordTimeStamp')),
                                  row.get('awemeId'), row.get('userID', '') or '', account))
    data_list.sort(key=lambda r: (r[0] == '', r[0] or _UNIX), reverse=False)
    data_headers = (('Latest Played Timestamp', 'datetime'), ('Record Timestamp', 'datetime'), 'Aweme ID',
                    'User ID (as stored)', 'Account UID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def tiktok_follow_feed_played(context):
    data_list = []
    sources = []
    for path in _stores(context, 'played_videos_recorder.db', 'follow_feed'):
        tables = _tables(path, 'TikTok - Follow Feed Played Videos')
        if tables is None:
            continue
        sources.append(path)
        for account, rows in tables:
            for row in rows:
                data_list.append((_seconds(row.get('createTime')), row.get('gid'), account))
    data_list.sort(key=lambda r: (r[0] == '', r[0] or _UNIX))
    data_headers = (('Create Time', 'datetime'), 'GID', 'Account UID')
    return data_headers, data_list, '\n'.join(sources)
