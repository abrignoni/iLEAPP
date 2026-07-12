__artifacts_v2__ = {
    "tiktok_replied": {
        "name": "TikTok - Replied Messages",
        "description": (
            'Extracts "Replied" message remnants left in the TikTok database which '
            "may no longer exist in the native message table"
        ),
        "author": "John Hyla http://www.bluecrewforensics.com/",
        "creation_date": "2024-11-08",
        "last_update_date": "2026-06-18",
        "requirements": "none",
        "category": "TikTok",
        "notes": (
            "This artifact is extracted from TIMMessageKVORM or TIMMessageNewPropertyORM. "
            "It appears that a copy of the message being replied to is placed into these "
            "tables and may remain after the actual referenced message or reply is deleted."
        ),
        "paths": (
            "*/Application/*/Library/Application Support/ChatFiles/*/db.sqlite*",
            "*AwemeIM.db*",
        ),
        "output_types": "standard",
        "artifact_icon": "corner-up-left",
        "sample_data": {
            "josh_ios_15": "2 replied-message rows; TIMMessageKVORM and TIMMessageNewPropertyORM both present",
            "josh_ios_17": "No TikTok AwemeIM.db or ChatFiles db.sqlite found",
            "mvs_2026": "No TikTok AwemeIM.db or ChatFiles db.sqlite found",
            "ctf2020_ios12": "iOS 12.4 | com.zhiliaoapp.musically | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | TikTok - Videos, Shop & LIVE 41.8.0 | 3 rows",
            "fsfull002_ios17": "iOS 17.1 | TikTok 28.4.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | TikTok 35.1.0 | 4 rows",
            "iphone12_ios18": "iOS 18.7 | TikTok - Videos, Shop & LIVE 42.7.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | TikTok 35.6.0 | 0 rows",
            "abe_ios16": "iOS 16.5 | TikTok 30.0.0 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | TikTok - Make Your Day 15.4.0 | 0 rows",
            "hickman_ios14": "iOS 14.3 | TikTok 18.4.5 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | TikTok 27.0.1 | 0 rows",
        },
    }
}

from os.path import basename, dirname, normcase, normpath

from scripts.ilapfuncs import (
    artifact_processor,
    attach_sqlite_db_readonly,
    convert_unix_ts_to_utc,
    get_sqlite_db_records,
    logfunc,
)


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


def _table_exists(db_path, table_name):
    query = f"""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
            AND name = {_quote_literal(table_name)}
    """
    return bool(get_sqlite_db_records(db_path, query))


def _table_columns(db_path, table_name, attach_query):
    query = f"PRAGMA AwemeIM.table_info({_quote_literal(table_name)})"
    return {row[1].lower() for row in get_sqlite_db_records(db_path, query, attach_query)}


def _contact_tables(db_path, attach_query, required_columns=None):
    query = """
        SELECT name
        FROM AwemeIM.sqlite_master
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


def _deduplicated_contacts_cte(contact_tables):
    subqueries = []
    for table in contact_tables:
        table_name = _quote_literal(table)
        table_identifier = f"AwemeIM.{_quote_identifier(table)}"
        subqueries.append(
            "SELECT uid, customid, nickname, url1, "
            f"{table_name} AS source_table FROM {table_identifier}"
        )

    if subqueries:
        contacts_subquery = " UNION ALL ".join(subqueries)
    else:
        contacts_subquery = (
            "SELECT NULL AS uid, NULL AS customid, NULL AS nickname, "
            "NULL AS url1, NULL AS source_table WHERE 0"
        )

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


def _kvorm_query(contacts_cte):
    return f"""
        {contacts_cte}
        SELECT
            TIMMessageORM.servercreatedat,
            TIMMessageKVORM.rowid,
            TIMMessageKVORM.belongingMessageID,
            json_extract(TIMMessageKVORM.value, '$.ref_msg_type') AS ref_msg_type,
            json_extract(TIMMessageKVORM.value, '$.ref_msg_id') AS ref_msg_id,
            CASE
                WHEN json_valid(json_extract(TIMMessageKVORM.value, '$.hint'))
                    AND json_valid(json_extract(json_extract(TIMMessageKVORM.value, '$.hint'), '$.content'))
                    THEN json_extract(
                        json_extract(json_extract(TIMMessageKVORM.value, '$.hint'), '$.content'),
                        '$.text'
                    )
            END AS referenced_text,
            CASE
                WHEN json_valid(json_extract(TIMMessageKVORM.value, '$.hint'))
                    THEN json_extract(json_extract(TIMMessageKVORM.value, '$.hint'), '$.refmsg_uid')
            END AS referenced_message_sender,
            ref_message_sender.customID AS referenced_message_sender_customid,
            ref_message_sender.nickname AS referenced_message_sender_nickname,
            CASE
                WHEN json_valid(TIMMessageORM.content) THEN json_extract(TIMMessageORM.content, '$.text')
            END AS reply_text,
            CASE
                WHEN TIMMessageORM.deleted = 0 THEN 'False'
                WHEN TIMMessageORM.deleted = 1 THEN 'True'
                ELSE 'Unknown'
            END AS deleted,
            TIMMessageORM.belongingConversationIdentifier,
            TIMMessageORM.sender AS reply_sender,
            reply_sender.customID AS reply_sender_customid,
            reply_sender.nickname AS reply_sender_nickname,
            ref_message_sender.source_table AS ref_message_contact_table,
            reply_sender.source_table AS reply_sender_contact_table,
            'TIMMessageKVORM' AS parser_table
        FROM TIMMessageKVORM
        LEFT JOIN TIMMessageORM
            ON TIMMessageKVORM.belongingMessageID = TIMMessageORM.identifier
        LEFT JOIN DeduplicatedContacts AS ref_message_sender
            ON referenced_message_sender = ref_message_sender.uid
        LEFT JOIN DeduplicatedContacts AS reply_sender
            ON TIMMessageORM.sender = reply_sender.uid
    """


def _new_property_query(contacts_cte):
    return f"""
        {contacts_cte}
        SELECT
            createdTime,
            rowid,
            belongingMessageID,
            json_extract(value, '$.ref_msg_type') AS ref_msg_type,
            json_extract(value, '$.ref_msg_id') AS ref_msg_id,
            CASE
                WHEN json_valid(json_extract(value, '$.hint'))
                    AND json_valid(json_extract(json_extract(value, '$.hint'), '$.content'))
                    THEN json_extract(json_extract(json_extract(value, '$.hint'), '$.content'), '$.text')
            END AS referenced_text,
            CASE
                WHEN json_valid(json_extract(value, '$.hint'))
                    THEN json_extract(json_extract(value, '$.hint'), '$.refmsg_uid')
            END AS referenced_message_sender,
            ref_message_sender.customID AS referenced_message_sender_customid,
            ref_message_sender.nickname AS referenced_message_sender_nickname,
            NULL AS reply_text,
            NULL AS deleted,
            belongingConversationID AS belongingConversationIdentifier,
            sender AS reply_sender,
            reply_sender.customID AS reply_sender_customid,
            reply_sender.nickname AS reply_sender_nickname,
            ref_message_sender.source_table AS ref_message_contact_table,
            reply_sender.source_table AS reply_sender_contact_table,
            'TIMMessageNewPropertyORM' AS parser_table
        FROM TIMMessageNewPropertyORM
        LEFT JOIN DeduplicatedContacts AS ref_message_sender
            ON json_extract(value, '$.hint.refmsg_uid') = ref_message_sender.uid
        LEFT JOIN DeduplicatedContacts AS reply_sender
            ON sender = reply_sender.uid
    """


@artifact_processor
def tiktok_replied(context):
    files_found = context.get_files_found()
    aweme_dbs = _aweme_im_dbs(files_found)
    data_list = []

    if not aweme_dbs:
        logfunc("AwemeIM.db not found. TikTok replied messages cannot be parsed.")
        return (), [], ""

    for chat_db in _chat_databases(files_found):
        aweme_im_db = _aweme_for_chat_db(chat_db, aweme_dbs)
        attach_query = attach_sqlite_db_readonly(aweme_im_db, "AwemeIM")
        contact_tables = _contact_tables(
            chat_db,
            attach_query,
            required_columns=("uid", "customid", "nickname", "url1"),
        )
        contacts_cte = _deduplicated_contacts_cte(contact_tables)

        if _table_exists(chat_db, "TIMMessageKVORM") and _table_exists(chat_db, "TIMMessageORM"):
            query = _kvorm_query(contacts_cte)
        elif _table_exists(chat_db, "TIMMessageNewPropertyORM"):
            query = _new_property_query(contacts_cte)
        else:
            logfunc(
                "TIMMessageKVORM/TIMMessageORM and TIMMessageNewPropertyORM were "
                f"not found in {chat_db}"
            )
            continue

        db_records = get_sqlite_db_records(chat_db, query, attach_query)
        source_file = _source_file_text(context, chat_db, aweme_im_db)
        account_id = basename(dirname(chat_db))

        for record in db_records:
            data_list.append((
                _convert_tiktok_timestamp(record[0]),
                record[1],
                record[2],
                record[3],
                record[4],
                record[5],
                record[6],
                record[7],
                record[8],
                record[9],
                record[10],
                record[11],
                record[12],
                record[13],
                record[14],
                record[15],
                record[16],
                record[17],
                account_id,
                context.get_relative_path(source_file),
            ))

    data_headers = (
        ("Reply Server Created Date", "datetime"),
        "RowID",
        "BelongingMessageID",
        "ref_msg_type",
        "ref_msg_id",
        "Referenced Text",
        "Ref Msg Sender UID",
        "Ref Msg Sender CustomID",
        "Ref Msg Sender Nickname",
        "Reply Text",
        "Deleted",
        "Belonging Conversation ID",
        "Reply Sender UID",
        "Reply Sender CustomID",
        "Reply Sender Nickname",
        "Ref Msg Sender Contact Table",
        "Reply Sender Contact Table",
        "Parser Table",
        "Account ID",
        "Source File",
    )

    return data_headers, data_list, "see Source File column"
