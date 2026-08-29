""" tikTok """
__artifacts_v2__ = {
    "tiktok_messages": {
        "name": "TikTok - Messages",
        "description": "Extracts TikTok message data from the ChatFiles databases",
        "author": "James Habben, John Hyla",
        "creation_date": "2024-11-08",
        "last_update_date": "2026-08-29",
        "requirements": "none",
        "category": "TikTok",
        "notes": (
            "Messages are extracted from TIMMessageORM. Contact details are joined from "
            "AwemeContacts tables when available. The Account ID column is the ChatFiles "
            "folder name (the local account uid, which also appears in AwemeIM.db); messages "
            "whose sender matches the Account ID are marked Outgoing. An iOS app container "
            "is a GUID directory, so the database names alone do not identify the owning "
            "app. Each matched database is attributed to the app named by its container's "
            "own .com.apple.mobile_container_manager.metadata.plist (a path reconstructed "
            "from an iTunes backup names the container by its AppDomain bundle id), and "
            "only containers owned by com.zhiliaoapp.musically are parsed. Databases in "
            "containers owned by any other app, or whose owning app cannot be established, "
            "are skipped and logged. "
            "On the tested images every matched database is in a TikTok-owned container; "
            "the exclusion of foreign and unattributable containers is proven with "
            "constructed test data. "
            "Reference: G. Horsman & L. Shou, 'Case Study: Forensic Analysis of TikTok on iOS', "
            "DFIR Review 2022, https://dfir.pubpub.org/pub/h6vyh33u"
        ),
        "paths": (
            "*/Application/*/Library/Application Support/ChatFiles/*/db.sqlite*",
            "*AwemeIM.db*",
            "*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist",
        ),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation ID",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Nickname"
            }
        },
        "sample_data": {
            "hickman_ios15": "32 message rows; AwemeContactsV5, TIMMessageORM, TIMMessageKVORM, and TIMMessageNewPropertyORM present",
            "iphone14plus_ios18": "No TikTok AwemeIM.db or ChatFiles db.sqlite found",
            "ctf2020_ios12": "iOS 12.4 | com.zhiliaoapp.musically | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | TikTok - Videos, Shop & LIVE 41.8.0 | 63 rows",
            "fsfull002_ios17": "iOS 17.1 | TikTok 28.4.1 | 15 rows",
            "iphone11_ios17": "iOS 17.3 | TikTok 35.1.0 | 50 rows",
            "iphone12_ios18": "iOS 18.7 | TikTok - Videos, Shop & LIVE 42.7.0 | 5 rows",
            "otto_ios17": "iOS 17.5.1 | TikTok 35.6.0 | 44 rows",
            "abe_ios16": "iOS 16.5 | TikTok 30.0.0 | 6 rows",
            "hickman_ios13": "iOS 13.3.1 | TikTok - Make Your Day 15.4.0 | 9 rows",
            "hickman_ios14": "iOS 14.3 | TikTok 18.4.5 | 12 rows",
            "magnet_ios16": "iOS 16.1.1 | TikTok 27.0.1 | 0 rows",
        },
    },
    "tiktok_contacts": {
        "name": "TikTok - Contacts",
        "description": "Extracts TikTok contact data from AwemeIM.db",
        "author": "James Habben, John Hyla",
        "creation_date": "2024-11-08",
        "last_update_date": "2026-08-29",
        "requirements": "none",
        "category": "TikTok",
        "notes": (
            "Timestamp corresponds to latest chat if available. An iOS app container is a "
            "GUID directory, so the AwemeIM.db name alone does not identify the owning app. "
            "Each matched database is attributed to the app named by its container's own "
            ".com.apple.mobile_container_manager.metadata.plist (a path reconstructed from "
            "an iTunes backup names the container by its AppDomain bundle id), and only "
            "containers owned by com.zhiliaoapp.musically are parsed. Databases in "
            "containers owned by any other app, or whose owning app cannot be established, "
            "are skipped and logged. On the tested images every matched database is in a "
            "TikTok-owned container; the exclusion of foreign and unattributable "
            "containers is proven with constructed test data."
        ),
        "paths": (
            "*AwemeIM.db*",
            "*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist",
        ),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "hickman_ios15": "4 contact rows from AwemeContactsV5",
            "iphone14plus_ios18": "No TikTok AwemeIM.db found",
            "ctf2020_ios12": "iOS 12.4 | com.zhiliaoapp.musically | 1 row",
            "dexter_ios18": "iOS 18.3.2 | TikTok - Videos, Shop & LIVE 41.8.0 | 44 rows",
            "fsfull002_ios17": "iOS 17.1 | TikTok 28.4.1 | 5 rows",
            "iphone11_ios17": "iOS 17.3 | TikTok 35.1.0 | 15 rows",
            "iphone12_ios18": "iOS 18.7 | TikTok - Videos, Shop & LIVE 42.7.0 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | TikTok 35.6.0 | 88 rows",
            "abe_ios16": "iOS 16.5 | TikTok 30.0.0 | 54 rows",
            "hickman_ios13": "iOS 13.3.1 | TikTok - Make Your Day 15.4.0 | 3 rows",
            "hickman_ios14": "iOS 14.3 | TikTok 18.4.5 | 4 rows",
            "magnet_ios16": "iOS 16.1.1 | TikTok 27.0.1 | 0 rows",
        },
    },
    "tiktok_account": {
        "name": "TikTok - Account",
        "description": "Account values from the com.toutiao.account.userdefault.user record "
                       "in the app's preferences plist, reported as stored under the app's "
                       "own key names.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "TikTok",
        "notes": (
            "The record is an NSKeyedArchiver payload inside "
            "Library/Preferences/com.zhiliaoapp.musically.plist; its string, number and "
            "boolean fields are reported one per row and empty values are skipped. On the "
            "tested image it carried the account's user id, screen name, sec user id, "
            "avatar URL, session key, and the phone number and email as the app stores "
            "them, which is partially masked. The sibling "
            "com.toutiao.account.userdefault.user.* scalar keys (login status, dticket, "
            "session ids) are included as rows. Other account caches in the same plist "
            "(NHAccountManager*, AWEUserStorageCacheUserKey, kDYA*) duplicate server "
            "profile responses and are not parsed."
        ),
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Preferences/com.zhiliaoapp.musically.plist",),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | TikTok 35.1.0 | 33 rows",
            "otto_ios17": "iOS 17.5.1 | TikTok 35.6.0 | 24 rows",
            "dexter_ios18": "iOS 18.3.2 | 23 rows",
            "iphone12_ios18": "iOS 18.7 | 30 rows",
            "abe_ios16": "iOS 16.5 | TikTok 30.0.0 | 32 rows",
            "hickman_ios15": "iOS 15.3.1 | 32 rows",
            "hickman_ios14": "iOS 14.3 | 22 rows",
        },
    },
    "tiktok_published_videos": {
        "name": "TikTok - Published Videos",
        "description": "Video files from the app's kAWEPublishLocalVideoStorageFolder, "
                       "rendered from disk, with the aid from each file name and the video "
                       "id the companion plist maps it to.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "TikTok",
        "notes": (
            "Files are named publish_video_local_<aid>.mp4. "
            "kAWEPublishLocalVideoCacheFile.plist in the same Documents folder maps each "
            "aid to a video id and both are reported. Hu and Karabiyik describe this "
            "folder as holding the videos uploaded by the user; on the tested image both "
            "files' aids also appear in the account's watch history. File Modified is the "
            "file system timestamp preserved in the extraction. "
            "Reference: Xiao Hu and Umit Karabiyik, 'Shopping while Watching: An Updated "
            "Forensic Analysis of TikTok on Android and iOS', ISNCC 2024, "
            "https://doi.org/10.1109/ISNCC62547.2024.10759027"
        ),
        "paths": ("*/mobile/Containers/Data/Application/*/Documents/kAWEPublishLocalVideoStorageFolder/*",
                  "*/mobile/Containers/Data/Application/*/Documents/kAWEPublishLocalVideoCacheFile.plist"),
        "output_types": "standard",
        "artifact_icon": "video",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | TikTok 35.1.0 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | TikTok 35.6.0 | 2 rows",
            "dexter_ios18": "iOS 18.3.2 | 3 rows",
            "abe_ios16": "iOS 16.5 | TikTok 30.0.0 | 1 row",
            "hickman_ios15": "iOS 15.3.1 | 1 row",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "hickman_ios13": "iOS 13.3.1 | 1 row (no companion plist, Video ID blank)",
        },
    },
    "tiktok_app_sessions": {
        "name": "TikTok - App Sessions",
        "description": "enter_app and leave_app rows from the FEInternalAppSessionTable in "
                       "the app's Pitaya feature_engineering databases, with session id, "
                       "launch flag and duration as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-29",
        "requirements": "none",
        "category": "TikTok",
        "notes": (
            "The databases live at Library/Pitaya/FE/<module id>/DB/"
            "feature_engineering.db and not every one carries the session table; files "
            "without it are skipped. Event Name holds the store's own enter_app and "
            "leave_app strings. Duration is reported as stored; on the tested image "
            "leave_app rows carried the milliseconds since that row's enter timestamp. "
            "Hu and Karabiyik describe the feature_engineering.db of an earlier app "
            "generation as recording user interaction events with millisecond "
            "timestamps; the event table they document is absent from the tested build, "
            "which carries this session table instead. An iOS app container is a GUID "
            "directory, so the database path alone does not identify the owning app. "
            "Each matched database is attributed to the app named by its container's "
            "own .com.apple.mobile_container_manager.metadata.plist (a path "
            "reconstructed from an iTunes backup names the container by its AppDomain "
            "bundle id), and only containers owned by com.zhiliaoapp.musically are "
            "parsed. Databases in containers owned by any other app, or whose owning "
            "app cannot be established, are skipped and logged. On the tested images "
            "every matched database is in a TikTok-owned container; the exclusion of "
            "foreign and unattributable containers is proven with constructed test "
            "data. "
            "Reference: Xiao Hu and Umit Karabiyik, 'Shopping while Watching: An Updated "
            "Forensic Analysis of TikTok on Android and iOS', ISNCC 2024, "
            "https://doi.org/10.1109/ISNCC62547.2024.10759027"
        ),
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Pitaya/FE/*/DB/feature_engineering.db*",
                  "*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist"),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 53 rows",
            "iphone11_ios17": "iOS 17.3 | TikTok 35.1.0 | 46 rows",
            "otto_ios17": "iOS 17.5.1 | TikTok 35.6.0 | 38 rows",
            "iphone12_ios18": "iOS 18.7 | 23 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 6 rows",
            "abe_ios16": "iOS 16.5 | TikTok 30.0.0 | 0 rows (FE database lacks the session table)",
            "hickman_ios15": "iOS 15.3.1 | 0 rows (FE database lacks the session table)",
            "hickman_ios13": "iOS 13.3.1 | no Pitaya feature_engineering.db found",
        },
    },
    "tiktok_watch_history": {
        "name": "TikTok - Watch History",
        "description": "Entries from the app's WatchHistory store: one row per aid with a "
                       "timestamp, reported as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-29",
        "requirements": "none",
        "category": "TikTok",
        "notes": (
            "The store is Documents/WatchHistory/<account id>_history_WCDB.sqlite inside the "
            "TikTok app container; WatchHistory is the app's own directory name. Its single "
            "table holds an aid text column and a Unix-epoch timestamp. An aid identifies a "
            "video: on the tested image two of the twelve aids equalled the numeric ids in "
            "the account's own published video file names "
            "(Documents/kAWEPublishLocalVideoStorageFolder/publish_video_local_<aid>.mp4) "
            "and in kAWEPublishLocalVideoCacheFile.plist, which maps each aid to a video "
            "id. Whether an entry means the video was viewed or prefetched is not "
            "established here. The Account ID column is the file name's numeric prefix, "
            "which on the tested image matches the ChatFiles account folder name (the "
            "local account uid). An iOS app container is a GUID directory, so the store's "
            "path alone does not identify the owning app. Each matched database is "
            "attributed to the app named by its container's own "
            ".com.apple.mobile_container_manager.metadata.plist (a path reconstructed "
            "from an iTunes backup names the container by its AppDomain bundle id), and "
            "only containers owned by com.zhiliaoapp.musically are parsed. Databases in "
            "containers owned by any other app, or whose owning app cannot be "
            "established, are skipped and logged. On the tested images every matched "
            "database is in a TikTok-owned container; the exclusion of foreign and "
            "unattributable containers is proven with constructed test data."
        ),
        "paths": ("*/mobile/Containers/Data/Application/*/Documents/WatchHistory/*_history_WCDB.sqlite*",
                  "*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist"),
        "output_types": "standard",
        "artifact_icon": "eye",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | TikTok 35.1.0 | 12 rows",
            "otto_ios17": "iOS 17.5.1 | TikTok 35.6.0 | 1044 rows",
            "abe_ios16": "iOS 16.5 | TikTok 30.0.0 | 1562 rows",
            "hickman_ios15": "iOS 15.3.1 | 8 rows",
            "dexter_ios18": "iOS 18.3.2 | no WatchHistory store found",
            "iphone12_ios18": "iOS 18.7 | no WatchHistory store found",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | no WatchHistory store found",
            "hickman_ios13": "iOS 13.3.1 | no WatchHistory store found",
        },
    },
}

import re
from datetime import datetime, timezone
from os.path import basename, dirname, getmtime, getsize, isfile, normcase, normpath

from scripts.ilapfuncs import (
    artifact_processor,
    attach_sqlite_db_readonly,
    convert_unix_ts_to_utc,
    check_in_media,
    get_plist_content,
    get_plist_file_content,
    get_sqlite_db_records,
    logfunc,
)

_TIKTOK_ACCOUNT_KEY = "com.toutiao.account.userdefault.user"

# An iOS app container is a GUID directory, so a matched file's path does not
# name the owning app. Stores matched by name (IM databases, Pitaya
# feature_engineering.db, WatchHistory) are only parsed when the app that owns
# their container is TikTok.
_TIKTOK_BUNDLE_IDS = ("com.zhiliaoapp.musically",)
_CONTAINER_METADATA_SUFFIX = ".com.apple.mobile_container_manager.metadata.plist"
_CONTAINER_SEGMENT_RE = re.compile(r"/Containers/Data/Application/([^/]+)/", re.I)


def _container_owners(files_found):
    """Container directory name mapped to the bundle id its own metadata plist
    records. The plists are declared in the artifact's paths so they are staged
    with the databases regardless of the order artifacts run in."""
    owners = {}
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith(_CONTAINER_METADATA_SUFFIX):
            continue
        parsed = get_plist_file_content(file_found)
        if not isinstance(parsed, dict):
            continue
        identifier = parsed.get("MCMMetadataIdentifier")
        if identifier:
            owners[basename(dirname(file_found))] = identifier
    return owners


def _container_owner(path, owners):
    """Bundle id of the app owning the container the file sits in, or '' when
    it cannot be established. The backup seeker reconstructs an AppDomain path
    with the bundle id itself as the container segment, so a dotted segment
    with no metadata plist is that recorded bundle id."""
    match = _CONTAINER_SEGMENT_RE.search(str(path).replace("\\", "/"))
    if not match:
        return ""
    segment = match.group(1)
    if segment in owners:
        return owners[segment]
    if "." in segment:
        return segment
    return ""


def _tiktok_owned(paths, owners):
    """The subset of paths whose containers TikTok owns; every exclusion is
    logged with the reason."""
    kept = []
    for path in paths:
        owner = _container_owner(path, owners)
        if owner in _TIKTOK_BUNDLE_IDS:
            kept.append(path)
        elif owner:
            logfunc(f"Skipping {path}; its container's metadata records the owning "
                    f"app {owner}, which is not a TikTok bundle id")
        else:
            logfunc(f"Skipping {path}; the app owning its container could not be established")
    return kept


def _quote_identifier(identifier):
    escaped_identifier = identifier.replace('"', '""')
    return f'"{escaped_identifier}"'


def _quote_literal(value):
    escaped_value = value.replace("'", "''")
    return f"'{escaped_value}'"


def _convert_tiktok_timestamp(timestamp):
    try:
        if timestamp and float(timestamp) > 1:
            return convert_unix_ts_to_utc(timestamp)
    except (TypeError, ValueError):
        pass
    return timestamp


def _application_container(path):
    parts = normpath(path).replace("/", "\\").split("\\")
    if "Application" not in parts:
        return ""
    app_index = len(parts) - 1 - parts[::-1].index("Application")
    if app_index + 1 >= len(parts):
        return ""
    return normcase("\\".join(parts[:app_index + 2]))


def _aweme_im_dbs(files_found):
    aweme_dbs = []
    for file_found in files_found:
        if str(file_found).endswith("AwemeIM.db"):
            aweme_dbs.append(str(file_found))
    return aweme_dbs


def _aweme_for_chat_db(chat_db, aweme_dbs):
    chat_container = _application_container(chat_db)
    for aweme_db in aweme_dbs:
        if _application_container(aweme_db) == chat_container:
            return aweme_db
    return aweme_dbs[0] if aweme_dbs else ""


def _chat_databases(files_found):
    return [str(file_found) for file_found in files_found if str(file_found).endswith("db.sqlite")]


def _table_columns(db_path, table_name, attach_query=None):
    db_name = "AwemeIM." if attach_query else ""
    query = f"PRAGMA {db_name}table_info({_quote_literal(table_name)})"
    return {row[1].lower() for row in get_sqlite_db_records(db_path, query, attach_query)}


def _contact_tables(db_path, attach_query=None, required_columns=None):
    query = """
        SELECT name
        FROM AwemeIM.sqlite_master
        WHERE type = 'table'
            AND name LIKE 'AwemeContacts%'
        ORDER BY name
    """
    if not attach_query:
        query = """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
                AND name LIKE 'AwemeContacts%'
            ORDER BY name
        """

    contact_tables = [row[0] for row in get_sqlite_db_records(db_path, query, attach_query)]
    if not required_columns:
        return contact_tables

    required_columns = {column.lower() for column in required_columns}
    matching_tables = []
    for table in contact_tables:
        table_columns = _table_columns(db_path, table, attach_query)
        if required_columns.issubset(table_columns):
            matching_tables.append(table)
        else:
            logfunc(f"Skipping TikTok contact table {table}; expected columns were not found")

    return matching_tables


def _contact_subquery(contact_tables, attached=True, include_source_table=False):
    source_prefix = "AwemeIM." if attached else ""
    source_table_column = ""
    if include_source_table:
        source_table_column = ", {table_name} AS source_table"

    subqueries = []
    for table in contact_tables:
        table_name = _quote_literal(table)
        table_identifier = f"{source_prefix}{_quote_identifier(table)}"
        subqueries.append(
            "SELECT uid, customid, nickname, url1"
            f"{source_table_column.format(table_name=table_name)} "
            f"FROM {table_identifier}"
        )

    if subqueries:
        return " UNION ALL ".join(subqueries)

    if include_source_table:
        return (
            "SELECT NULL AS uid, NULL AS customid, NULL AS nickname, "
            "NULL AS url1, NULL AS source_table WHERE 0"
        )

    return "SELECT NULL AS uid, NULL AS customid, NULL AS nickname, NULL AS url1 WHERE 0"


def _deduplicated_contacts_cte(contact_tables):
    contacts_subquery = _contact_subquery(contact_tables, include_source_table=True)
    return f"""
        WITH UniqueContacts AS (
            SELECT
                uid,
                customid,
                nickname,
                url1,
                source_table,
                ROW_NUMBER() OVER (PARTITION BY uid ORDER BY source_table) AS rn
            FROM ({contacts_subquery}) AS CombinedContacts
        ),
        DeduplicatedContacts AS (
            SELECT uid, customid, nickname, url1, source_table
            FROM UniqueContacts
            WHERE rn = 1
        )
    """


def _source_file_text(context, *paths):
    return "; ".join(context.get_relative_path(path) for path in paths if path)


@artifact_processor
def tiktok_messages(context):
    """ see artifact description """
    files_found = context.get_files_found()
    owners = _container_owners(files_found)
    aweme_dbs = _tiktok_owned(_aweme_im_dbs(files_found), owners)
    data_list = []
    source_paths = set()

    if not aweme_dbs:
        logfunc("No TikTok-owned AwemeIM.db found. TikTok messages cannot be parsed.")
        return (), [], ""

    for chat_db in _tiktok_owned(_chat_databases(files_found), owners):
        aweme_im_db = _aweme_for_chat_db(chat_db, aweme_dbs)
        account_id = basename(dirname(chat_db))
        attach_query = attach_sqlite_db_readonly(aweme_im_db, "AwemeIM")
        message_table = list( get_sqlite_db_records(
            chat_db,
            """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                    AND name = 'TIMMessageORM'
            """,
        ) )

        if not message_table:
            logfunc(f"Table TIMMessageORM not found in {chat_db}")
            continue

        source_paths.add(chat_db)
        if aweme_im_db:
            source_paths.add(aweme_im_db)
        contact_tables = _contact_tables(
            chat_db,
            attach_query,
            required_columns=("uid", "customid", "nickname", "url1"),
        )
        contacts_cte = _deduplicated_contacts_cte(contact_tables)
        query = f"""
            {contacts_cte}
            SELECT
                localcreatedat,
                sender,
                customid,
                nickname,
                CASE
                    WHEN json_valid(content) THEN json_extract(content, '$.text')
                END AS message,
                CASE
                    WHEN json_valid(content) THEN json_extract(content, '$.tips')
                END AS localresponse,
                CASE
                    WHEN json_valid(content) THEN json_extract(content, '$.display_name')
                END AS links_display_name,
                CASE
                    WHEN json_valid(content) THEN json_extract(content, '$.url.url_list[0]')
                END AS links_gifs_urls,
                servercreatedat,
                url1,
                source_table,
                belongingConversationIdentifier
            FROM TIMMessageORM
            LEFT JOIN DeduplicatedContacts ON DeduplicatedContacts.uid = sender
            ORDER BY localcreatedat
        """
        db_records = get_sqlite_db_records(chat_db, query, attach_query)
        source_file = _source_file_text(context, chat_db, aweme_im_db)

        for record in db_records:
            data_list.append((
                _convert_tiktok_timestamp(record[0]),
                _convert_tiktok_timestamp(record[8]),
                'Outgoing' if str(record[1]) == str(account_id) else 'Incoming',
                record[3],
                record[4],
                record[1],
                record[2],
                record[5],
                record[6],
                record[7],
                record[9],
                record[10],
                account_id,
                source_file,
                record[11],
            ))

    data_headers = (
        ("Timestamp", "datetime"),
        ("Server Created Timestamp", "datetime"),
        "Direction",
        "Nickname",
        "Message",
        "Sender",
        "Custom ID",
        "Local Response",
        "Content Display Name",
        "Content URL",
        "Profile Pic URL",
        "Contact Table",
        "Account ID",
        "Source File",
        "Conversation ID",
    )

    return data_headers, data_list, "\n".join(sorted(source_paths))


@artifact_processor
def tiktok_contacts(context):
    """ see artifact description """
    files_found = context.get_files_found()
    aweme_dbs = _tiktok_owned(_aweme_im_dbs(files_found), _container_owners(files_found))
    data_list = []
    source_paths = set()

    if not aweme_dbs:
        logfunc("No TikTok-owned AwemeIM.db found. TikTok contacts cannot be parsed.")
        return (), [], ""

    for aweme_im_db in aweme_dbs:
        contact_tables = _contact_tables(
            aweme_im_db,
            required_columns=("latestchattimestamp", "nickname", "uid", "customid", "url1"),
        )
        if not contact_tables:
            logfunc(f"No AwemeContacts tables found in {aweme_im_db}.")
            continue

        source_paths.add(aweme_im_db)
        contacts_query = []
        for table in contact_tables:
            table_name = _quote_literal(table)
            table_identifier = _quote_identifier(table)
            contacts_query.append(f"""
                SELECT
                    latestchattimestamp,
                    nickname,
                    uid,
                    customID,
                    url1,
                    {table_name}
                FROM {table_identifier}
            """)

        db_records = get_sqlite_db_records(aweme_im_db, " UNION ALL ".join(contacts_query))

        source_file = context.get_relative_path(aweme_im_db)
        for record in db_records:
            data_list.append((
                _convert_tiktok_timestamp(record[0]),
                record[1],
                record[2],
                record[3],
                record[4],
                record[5],
                source_file,
            ))

    data_headers = (
        ("Timestamp", "datetime"),
        "Nickname",
        "Unique ID",
        "Custom ID",
        "URL",
        "Source Table",
        "Source File",
    )

    return data_headers, data_list, "\n".join(sorted(source_paths))


@artifact_processor
def tiktok_account(context):
    """ see artifact description """
    files_found = context.get_files_found()
    data_list = []
    source_path = ""

    for file_found in files_found:
        file_found = str(file_found)
        plist_content = get_plist_file_content(file_found)
        if not isinstance(plist_content, dict) or _TIKTOK_ACCOUNT_KEY not in plist_content:
            continue
        source_path = source_path or file_found
        source_file = context.get_relative_path(file_found)

        account_blob = plist_content.get(_TIKTOK_ACCOUNT_KEY)
        account = get_plist_content(account_blob) if isinstance(account_blob, bytes) else {}
        if isinstance(account, dict):
            for key in sorted(account):
                value = account[key]
                if isinstance(value, (str, int, float, bool)) and value != "":
                    data_list.append((f"{_TIKTOK_ACCOUNT_KEY}: {key}", str(value), source_file))

        for key in sorted(plist_content):
            if not key.startswith(f"{_TIKTOK_ACCOUNT_KEY}."):
                continue
            value = plist_content[key]
            if isinstance(value, (str, int, float, bool)) and value != "":
                data_list.append((key, str(value), source_file))

    data_headers = ("Key", "Value", "Source File")
    return data_headers, data_list, source_path


@artifact_processor
def tiktok_watch_history(context):
    """ see artifact description """
    files_found = context.get_files_found()
    history_dbs = [str(file_found) for file_found in files_found
                   if str(file_found).endswith("_history_WCDB.sqlite")]
    data_list = []
    source_path = ""

    for file_found in _tiktok_owned(history_dbs, _container_owners(files_found)):
        source_path = source_path or file_found
        account_id = basename(file_found).split("_", 1)[0]
        source_file = context.get_relative_path(file_found)
        for aid, timestamp in get_sqlite_db_records(
                file_found,
                "SELECT aid, timestamp FROM kTableName_history ORDER BY timestamp"):
            data_list.append((
                _convert_tiktok_timestamp(timestamp),
                aid,
                account_id,
                source_file,
            ))

    data_headers = (
        ("Timestamp", "datetime"),
        "aid (as stored)",
        "Account ID",
        "Source File",
    )

    return data_headers, data_list, source_path


@artifact_processor
def tiktok_published_videos(context):
    """ see artifact description """
    files_found = context.get_files_found()
    data_list = []
    source_path = ""

    video_ids = {}
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith("kAWEPublishLocalVideoCacheFile.plist"):
            mapping = get_plist_file_content(file_found)
            if isinstance(mapping, dict):
                video_ids.update({str(k): str(v) for k, v in mapping.items()})

    for file_found in files_found:
        file_found = str(file_found)
        name = basename(file_found)
        if not (name.startswith("publish_video_local_") and isfile(file_found)):
            continue
        source_path = source_path or file_found
        aid = name.replace("publish_video_local_", "").rsplit(".", 1)[0]
        media_ref = check_in_media(file_found, name)
        modified = datetime.fromtimestamp(getmtime(file_found), timezone.utc)
        data_list.append((
            modified, media_ref or "", aid, video_ids.get(aid, ""),
            getsize(file_found), context.get_relative_path(file_found),
        ))

    data_headers = (
        ("File Modified", "datetime"),
        ("Media", "media"),
        "aid (as stored)",
        "Video ID",
        "File Size (bytes)",
        "Source File",
    )
    return data_headers, data_list, source_path


@artifact_processor
def tiktok_app_sessions(context):
    """ see artifact description """
    files_found = context.get_files_found()
    session_dbs = [str(file_found) for file_found in files_found
                   if str(file_found).endswith("feature_engineering.db")]
    data_list = []
    source_path = ""

    for file_found in _tiktok_owned(session_dbs, _container_owners(files_found)):
        has_table = list(get_sqlite_db_records(
            file_found,
            "SELECT name FROM sqlite_master WHERE type = 'table' "
            "AND name = 'FEInternalAppSessionTable'"))
        if not has_table:
            continue
        source_path = source_path or file_found
        source_file = context.get_relative_path(file_found)
        for (timestamp_ms, event_name, is_launch, session, enter_ms,
             duration) in get_sqlite_db_records(file_found, """
                SELECT timestamp_ms, event_name, is_launch, session,
                       enter_timestamp_ms, duration
                FROM FEInternalAppSessionTable ORDER BY timestamp_ms"""):
            data_list.append((
                _convert_tiktok_timestamp(timestamp_ms), event_name,
                "YES" if is_launch else "NO", session,
                _convert_tiktok_timestamp(enter_ms), duration, source_file,
            ))

    data_headers = (
        ("Timestamp", "datetime"),
        "Event Name",
        "Is Launch",
        "Session",
        ("Enter Timestamp", "datetime"),
        "Duration (ms, as stored)",
        "Source File",
    )
    return data_headers, data_list, source_path
