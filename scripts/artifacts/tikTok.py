""" tikTok """
__artifacts_v2__ = {
    "tiktok_messages": {
        "name": "TikTok - Messages",
        "description": "Extracts TikTok message data from the ChatFiles databases",
        "author": "James Habben, John Hyla",
        "creation_date": "2024-11-08",
        "last_update_date": "2026-06-18",
        "requirements": "none",
        "category": "TikTok",
        "notes": (
            "Messages are extracted from TIMMessageORM. Contact details are joined from "
            "AwemeContacts tables when available."
        ),
        "paths": (
            "*/Application/*/Library/Application Support/ChatFiles/*/db.sqlite*",
            "*AwemeIM.db*",
        ),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "josh_ios_15": (
                "32 message rows; AwemeContactsV5, TIMMessageORM, TIMMessageKVORM, "
                "and TIMMessageNewPropertyORM present"
            ),
            "josh_ios_17": "No TikTok AwemeIM.db or ChatFiles db.sqlite found",
            "mvs_2026": "No TikTok AwemeIM.db or ChatFiles db.sqlite found",
        },
    },
    "tiktok_contacts": {
        "name": "TikTok - Contacts",
        "description": "Extracts TikTok contact data from AwemeIM.db",
        "author": "James Habben, John Hyla",
        "creation_date": "2024-11-08",
        "last_update_date": "2026-06-18",
        "requirements": "none",
        "category": "TikTok",
        "notes": "Timestamp corresponds to latest chat if available.",
        "paths": ("*AwemeIM.db*",),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "josh_ios_15": "4 contact rows from AwemeContactsV5",
            "josh_ios_17": "No TikTok AwemeIM.db found",
            "mvs_2026": "No TikTok AwemeIM.db found",
        },
    },
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
    aweme_dbs = _aweme_im_dbs(files_found)
    data_list = []

    if not aweme_dbs:
        logfunc("AwemeIM.db not found. TikTok messages cannot be parsed.")
        return (), [], ""

    for chat_db in _chat_databases(files_found):
        aweme_im_db = _aweme_for_chat_db(chat_db, aweme_dbs)
        account_id = basename(dirname(chat_db))
        attach_query = attach_sqlite_db_readonly(aweme_im_db, "AwemeIM")
        message_table = get_sqlite_db_records(
            chat_db,
            """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                    AND name = 'TIMMessageORM'
            """,
        )

        if not message_table:
            logfunc(f"Table TIMMessageORM not found in {chat_db}")
            continue

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
                source_table
            FROM TIMMessageORM
            LEFT JOIN DeduplicatedContacts ON DeduplicatedContacts.uid = sender
            ORDER BY localcreatedat
        """
        db_records = get_sqlite_db_records(chat_db, query, attach_query)
        source_file = _source_file_text(context, chat_db, aweme_im_db)

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
                _convert_tiktok_timestamp(record[8]),
                record[9],
                record[10],
                account_id,
                source_file,
            ))

    data_headers = (
        ("Timestamp", "datetime"),
        "Sender",
        "Custom ID",
        "Nickname",
        "Message",
        "Local Response",
        "Link GIF Name",
        "Link GIF URL",
        ("Server Created Timestamp", "datetime"),
        "Profile Pic URL",
        "Contact Table",
        "Account ID",
        "Source File",
    )

    return data_headers, data_list, "see Source File column"


@artifact_processor
def tiktok_contacts(context):
    """ see artifact description """
    files_found = context.get_files_found()
    aweme_dbs = _aweme_im_dbs(files_found)
    data_list = []

    if not aweme_dbs:
        logfunc("AwemeIM.db not found. TikTok contacts cannot be parsed.")
        return (), [], ""

    for aweme_im_db in aweme_dbs:
        contact_tables = _contact_tables(
            aweme_im_db,
            required_columns=("latestchattimestamp", "nickname", "uid", "customid", "url1"),
        )
        if not contact_tables:
            logfunc(f"No AwemeContacts tables found in {aweme_im_db}.")
            continue

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

    return data_headers, data_list, "see Source File column"
