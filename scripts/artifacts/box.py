"""
Box Artifact Module
Extracts account, file hierarchy, and offline metadata from Box on iOS, 
including shared links, collections, and cached media previews, 
along with recent activity, comments, and file annotations.
"""

__artifacts_v2__ = {
    "box_account": {
        "name": "Box - Account",
        "description": "Parses and extracts Box Account information",
        "author": "@djangofaiola",
        "creation_date": "2025-12-05",
        "last_update_date": "2026-03-30",
        "requirements": "none",
        "category": "Box",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Shared/AppGroup/*/Library/Preferences/"
                  "group.net.box.BoxNet.plist"),
        "output_types": [ "standard" ],
        "artifact_icon": "user"
    },
    "box_all_files": {
        "name": "Box - All Files",
        "description": "Parses and extracts Box All Files information",
        "author": "@djangofaiola",
        "creation_date": "2025-12-05",
        "last_update_date": "2026-03-30",
        "requirements": "none",
        "category": "Box",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Shared/AppGroup/*/Documents/db/Item.db*",
                  "*/mobile/Containers/Shared/AppGroup/*/Documents/offlinefilesinfo/"
                  "itemIDs.plist",
                  "*/mobile/Containers/Shared/AppGroup/*/Documents/offlinefilesinfo/"
                  "lastDownloadDates.plist"),
        "output_types": [ "standard" ],
        "html_columns": [ "URL" ],
        "artifact_icon": "cloud"
    },
    "box_previews": {
        "name": "Box - Previews",
        "description": "Parses and extracts all Previews and Original media files",
        "author": "@djangofaiola",
        "creation_date": "2025-12-05",
        "last_update_date": "2026-03-30",
        "requirements": "none",
        "category": "Box",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Shared/AppGroup/*/File Provider Storage/boxpreview/*/db/"
                  "PreviewItem.db*",
                  "*/mobile/Containers/Shared/AppGroup/*/File Provider Storage/boxpreview/*/cache/"
                  "files/*/*/*"),
        "output_types": [ "standard" ],
        "artifact_icon": "image"
    },
    "box_recents": {
        "name": "Box - Recents",
        "description": "Parses and extracts Recents",
        "author": "@djangofaiola",
        "creation_date": "2025-12-05",
        "last_update_date": "2026-03-30",
        "requirements": "none",
        "category": "Box",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Shared/AppGroup/*/Documents/db/Recents.db*",
                  "*/mobile/Containers/Shared/AppGroup/*/Documents/db/Item.db*"),
        "output_types": [ "standard" ],
        "artifact_icon": "search"
    },
    "box_comments": {
        "name": "Box - Comments and Annotations",
        "description": "Parses and extracts Comments and Annotations",
        "author": "@djangofaiola",
        "creation_date": "2025-12-05",
        "last_update_date": "2026-03-30",
        "requirements": "none",
        "category": "Box",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Shared/AppGroup/*/Documents/db/annotations.db*",
                  "*/mobile/Containers/Shared/AppGroup/*/Documents/db/Item.db*"),
        "output_types": [ "standard" ],
        "artifact_icon": "message-circle"
    },
}

import re
import html
import plistlib
import sqlite3
from datetime import timezone, datetime
from pathlib import Path
from urllib.parse import urlparse, urlunparse
from scripts.filetype import get_type
from scripts.ilapfuncs import artifact_processor, check_in_media, get_plist_file_content, \
    get_plist_content, attach_sqlite_db_readonly, get_sqlite_db_records, open_sqlite_db_readonly, \
    convert_unix_ts_to_utc, convert_bytes_to_unit, logfunc


# Pattern to normalize timezone offsets from +HHMM -> +HH:MM
ISO_OFFSET_FIX = re.compile(r'([+-]\d{2})(\d{2})$')

def convert_iso8601_to_utc(str_date: str | bytes | None) -> str | None:
    """
    Convert an ISO 8601 formatted date string to a canonical UTC string
    consistent with convert_unix_ts_to_utc.
    - Input is expected to be a string or bytes.
    - Decodes bytes using UTF-8 with errors ignored.
    - Normalizes trailing 'Z' and compact offsets (+HHMM -> +HH:MM).
    - Returns the canonical UTC string on success.
    - On failure, returns the trimmed original string and logs the parse failure.

    Args:
        str_date: ISO 8601 formatted string or bytes, or None.

    Returns:
        str | None: Canonical UTC string, trimmed original string if parsing fails,
                    or None if input is None or cannot be decoded.
    """

    # Explicitly preserve None input
    if str_date is None:
        return None

    # Decode bytes to string if necessary
    if isinstance(str_date, bytes):
        str_date = str_date.decode('utf-8', errors='ignore')

    # Ensure the input is a string
    if not isinstance(str_date, str):
        str_date = str(str_date)

    # Trim leading/trailing whitespace
    s = str_date.strip()

    # Return early for empty or "null"-like values
    if not s or s.lower() == 'null':
        return s

    # Replace comma with dot in fractional seconds
    s = s.replace(",", ".")

    # Normalize trailing 'Z' (UTC designator) to explicit offset
    if s.endswith('Z'):
        s = s[:-1] + '+00:00'

    # Normalize compact timezone offsets (+HHMM -> +HH:MM)
    s = ISO_OFFSET_FIX.sub(r"\1:\2", s)

    try:
        # Parse ISO 8601 string
        dt = datetime.fromisoformat(s)

        if dt.tzinfo is None:
            # Treat naive datetimes as UTC
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            # Convert aware datetimes to UTC
            dt = dt.astimezone(timezone.utc)

        # Convert to canonical UTC string using helper
        return convert_unix_ts_to_utc(dt.timestamp())

    except (ValueError, TypeError) as e:
        # Log parsing failure and return original trimmed string
        logfunc(f"Error - convert_iso8601_to_utc: parse failed for {s!r}: {e}")
        return s


def format_url(str_url : str | None, html_format : bool = False) -> str:
    """
    Normalize a raw URL and optionally format it as a safe HTML anchor.
    - Return an empty string if str_url is None, empty, or the literal 'null'.
    - Strip leading and trailing whitespace.
    - If the URL has no scheme, default to 'https'.
    - In case of unexpected errors, return the cleaned input (do not raise).
    - When html_format=True, escape values and add rel attributes to prevent tabnabbing.
    """

    # Treat None, empty strings, and the literal 'null' as missing input.
    if not str_url or str_url.strip().lower() == 'null':
        return ''

    s = str_url.strip()
    try:
        parsed = urlparse(s)

        # If no scheme is present, assume http
        if not parsed.scheme:
            parsed = urlparse(f"https://{s}")
        normalized = urlunparse(parsed)

    except (ValueError, TypeError, AttributeError) as e:
        # Log the error and return the cleaned input without raising
        logfunc(f"Error - format_url parse failed for {str_url!r}: {e}")
        return s

    if html_format:
        # Escape both the href and the visible text to prevent XSS
        safe_href = html.escape(normalized, quote=True)
        safe_text = html.escape(normalized, quote=False)
        # Add rel="noopener noreferrer" with target="_blank" to prevent tabnabbing
        return (
            f'<a href="{safe_href}" target="_blank" '
            f'rel="noopener noreferrer">{safe_text}</a>'
        )

    return normalized


@artifact_processor
def box_account(context):
    """
    Extract Box account metadata from the main app plist, 
    deserializing embedded JSON user data.
    """

    data_headers = (
        ('Created At', 'datetime'),
        'Login',
        'Name',
        'Has Custom Avatar',
        'Is Enterprise Account',
        'User ID',
        'Timezone',
        'Language',
        'Total Space',
        'Used Space',
        'Max Upload Size'
    )

    data_list = []
    data_list_html = []

    source_path = context.get_source_file_path('group.net.box.BoxNet.plist')
    plist_data = get_plist_file_content(source_path)
    if not plist_data:
        return data_headers, (data_list, data_list_html), source_path

    try:
        # Deserializing the embedded JSON string containing user metadata
        last_user_data = get_plist_content(plist_data.get('lastUserJSON'))
        if not last_user_data:
            return data_headers, (data_list, data_list_html), source_path

        # Profile and Localization metadata
        created_at = convert_iso8601_to_utc(last_user_data.get('created_at'))
        login = last_user_data.get('login')
        name = last_user_data.get('name')
        has_avatar = last_user_data.get('has_custom_avatar')
        is_enterprise = bool(last_user_data.get('enterprise'))
        user_id = last_user_data.get('id')
        user_timezone = last_user_data.get('timezone')
        language = last_user_data.get('language')

        # Storage metrics and quota formatting
        total_space = last_user_data.get('space_amount', 0)
        total_space_html = convert_bytes_to_unit(total_space)
        used_space = last_user_data.get('space_used', 0)
        used_space_html = convert_bytes_to_unit(used_space)
        max_upload_size = last_user_data.get('max_upload_size', 0)
        max_upload_size_html = convert_bytes_to_unit(max_upload_size)

        # HTML row
        data_list_html.append((created_at, login, name, has_avatar, is_enterprise, user_id,
                                user_timezone, language, total_space_html, used_space_html,
                                max_upload_size_html))
        # LAVA row
        data_list.append((created_at, login, name, has_avatar, is_enterprise, user_id,
                            user_timezone, language, total_space, used_space,
                            max_upload_size))

    except (KeyError, TypeError, ValueError) as ex:
        logfunc(f"[{context.get_artifact_name()}] "
                f"Error - Malformed structure in {source_path}: {ex}")
    except OSError as ex:
        logfunc(f"[{context.get_artifact_name()}] "
                f"Error - Could not read {source_path}: {ex}")

    return data_headers, (data_list, data_list_html), source_path


@artifact_processor
def box_all_files(context):
    """
    Reconstruct the full Box file hierarchy using a recursive CTE 
    and correlate with offline availability artifacts (plists).
    """

    data_headers = (
        ('Created At', 'datetime'),
        'Item ID',
        'Type',
        'Name',
        'Extension',
        'Path',
        'URL',
        'Description',
        'File/Folder Size',
        'Version ID',
        ('Content Created At', 'datetime'),
        ('Content Modified At', 'datetime'),
        ('Modified At', 'datetime'),
        ('Last Fetched At', 'datetime'),
        'Is Offline',
        ('Download At', 'datetime'),
        'Offline Source',
        'Favorites',
        'Collection Names',
        'Owner Login',
        'Owner Name',
        'Owner ID',
        'Creator Login',
        'Creator Name',
        'Creator ID',
        'Modifier Login',
        'Modifier Name',
        'Modifier ID',
        'SHA1'
    )

    data_list = []
    data_list_html = []

    # Offline status correlation: Primary (itemIDs) and Secondary (lastDownloadDates) sources
    ids_path = context.get_source_file_path('itemIDs.plist')
    last_dates_path = context.get_source_file_path('lastDownloadDates.plist')
    # Main database (Item.db)
    source_path = context.get_source_file_path('Item.db')
    source_paths = [ p for p in [ source_path, ids_path, last_dates_path ] if p ]

    offline_ids: dict[str, dict] = {}

    # Process itemIDs.plist
    if ids_path:
        try:
            with open(ids_path, 'rb') as f:
                ids_data = plistlib.load(f)
            if ids_data:
                offline_ids.update({
                    str(model_id): {
                        'offline': True,
                        'download_date': None,
                        'source': ids_path
                    } for model_id in ids_data
                })
        except (OSError, ValueError, TypeError) as ex:
            logfunc(f"[{context.get_artifact_name()}] Error - reading {ids_path}: {ex}")

    # Process lastDownloadDates.plist
    if last_dates_path:
        try:
            with open(last_dates_path, 'rb') as f:
                last_dates_data = plistlib.load(f)
            if last_dates_data:
                offline_ids.update({
                    str(model_id): {
                        'offline': True,
                        'download_date': date,
                        'source': last_dates_path
                    } for model_id, date in last_dates_data.items()
                })
        except (OSError, ValueError, TypeError) as ex:
            logfunc(f"[{context.get_artifact_name()}] Error - reading {last_dates_path}: {ex}")

    offline_artifacts_available = bool(offline_ids)


    db = open_sqlite_db_readonly(source_path)
    if not db:
        return data_headers, (data_list, data_list_html), source_path

    try:
        cursor = db.cursor()

        # Recursive CTE to reconstruct full directory hierarchy and extract JSON metadata
        query = '''
        WITH
        RECURSIVE cte_paths(id, name, path) AS (
            SELECT
                modelID AS id,
                name,
                '/' || name AS path
            FROM items
            WHERE COALESCE(parentID, 0) = 0
            UNION ALL
            SELECT
                i.modelID AS id,
                i.name,
                p.path || '/' || i.name AS path
            FROM items AS i
            JOIN cte_paths AS p ON (i.parentID = p.id)
        )

        SELECT
            p.id,
            i.type,
            p.name,
            json_extract(i.jsonData, '$.extension'),
            p.path,
            json_extract(i.jsonData, '$.shared_link.url'),
            json_extract(i.jsonData, '$.description'),
            json_extract(i.jsonData, '$.size'),
            json_extract(i.jsonData, '$.file_version.id'),
            json_extract(i.jsonData, '$.content_created_at'),
            json_extract(i.jsonData, '$.content_modified_at'),
            json_extract(i.jsonData, '$.created_at'),
            json_extract(i.jsonData, '$.modified_at'),
            i.lastNetworkFetchedTimestamp,
            CASE
                WHEN EXISTS (
                SELECT 1
                FROM json_each(i.jsonData, '$.collections')
                WHERE json_extract(json_each.value, '$.collection_type') = 'favorites'
                )
                THEN 'Yes'
                ELSE 'No'
            END AS "Favorites",
            (
                SELECT group_concat(json_extract(cn.value, '$.name'), ', ')
                FROM json_each(json_extract(i.jsonData, '$.collections')) AS cn
            ) AS "Collection Names",
            json_extract(i.jsonData, '$.owned_by.login'),
            json_extract(i.jsonData, '$.owned_by.name'),
            json_extract(i.jsonData, '$.owned_by.id'),
            json_extract(i.jsonData, '$.created_by.login'),
            json_extract(i.jsonData, '$.created_by.name'),
            json_extract(i.jsonData, '$.created_by.id'),
            json_extract(i.jsonData, '$.modified_by.login'),
            json_extract(i.jsonData, '$.modified_by.name'),
            json_extract(i.jsonData, '$.modified_by.id'),
            i.SHA1
        FROM cte_paths AS p
        LEFT JOIN items AS i ON (i.modelID = p.id)
        ORDER BY i.type DESC, p.path ASC;
        '''

        cursor.execute(query)

        for record in cursor:
            try:
                # Unpack record for clarity
                (
                    item_id, item_type, item_name, item_ext, full_path, url,
                    description, item_size, version_id, r_ccreated, r_cmodified,
                    r_created, r_modified, r_fetched, favorites, collections,
                    o_login, o_name, o_id, c_login, c_name, c_id,
                    m_login, m_name, m_id, sha1
                ) = record

                # Format URLs with safety checks
                url_html = format_url(url, html_format=True)

                # Convert bytes to human-readable format (e.g., MB, GB)
                item_size_html = convert_bytes_to_unit(item_size)

                # Parsing and normalization of timestamps (ISO8601 and Unix)
                ccreated_at = convert_iso8601_to_utc(r_ccreated)
                cmodified_at = convert_iso8601_to_utc(r_cmodified)
                created_at = convert_iso8601_to_utc(r_created)
                modified_at = convert_iso8601_to_utc(r_modified)
                last_fetched_at = convert_unix_ts_to_utc(r_fetched)

                # Offline status logic: cross-referencing DB with Plists and Seeker
                is_offline = 'Undetermined (no artifacts)'
                downloaded_at, offline_source = None, None
                item_id_str = str(item_id) if item_id is not None else ''

                if offline_artifacts_available:
                    is_offline = 'No'
                    # Strong offline evidence
                    if item_id_str in offline_ids:
                        is_offline = 'Yes'
                        downloaded_at = offline_ids[item_id_str]['download_date']
                        offline_source = Path(offline_ids[item_id_str]['source']).name
                    # Weak offline evidence via cache
                    elif bool(sha1) and context.get_seeker().search(sha1):
                        is_offline = 'Yes (cache only)'
                        offline_source = 'Filesystem cache'

                # Base row for both lists
                base_data = (
                    created_at, item_id, item_type, item_name, item_ext, full_path, url,
                    description, item_size, version_id, ccreated_at, cmodified_at,
                    modified_at, last_fetched_at, is_offline, downloaded_at, offline_source,
                    favorites, collections, o_login, o_name, o_id, c_login, c_name, c_id,
                    m_login, m_name, m_id, sha1
                )

                # LAVA row
                data_list.append(base_data)

                # HTML row
                html_list = list(base_data)
                html_list[6] = url_html
                html_list[8] = item_size_html
                data_list_html.append(tuple(html_list))

            except (IndexError, TypeError, ValueError) as ex:
                logfunc(f"[{context.get_artifact_name()}] "
                        f"Error - Failed parsing record items id {record[0]} in "
                        f"{source_path}: {ex}")
                continue

    except sqlite3.Error as db_ex:
        # Log fatal database errors (e.g., malformed DB or missing tables)
        logfunc(f"[{context.get_artifact_name()}] "
                f"Error - executing query on {source_path}: {db_ex}")
    finally:
        # Ensure the database connection is closed safely
        db.close()

    return data_headers, (data_list, data_list_html), '; '.join(source_paths)


def extract_user_id_safe(path: str, context) -> str | None:
    """
    Safely extract the Box user ID from the file system structure.
    Expected structure: .../<user_id>/db/PreviewItem.db
    - Input is expected to be a string representing the file path.
    - Validates that the target file is 'PreviewItem.db' within a 'db' directory.
    - On success, returns the parent directory name (the User ID).
    - On failure or unexpected structure, logs the event via logfunc and returns None.
    """
    try:
        p = Path(path)

        # Validation: check if the file is the expected PreviewItem database
        if p.name.lower() != 'previewitem.db':
            return None

        # Forensic mapping: navigate up to the parent directory 'db'
        db_dir = p.parent
        if db_dir.name.lower() != 'db':
            # This is a soft failure, might be a different DB version
            return None

        # The user ID is the name of the directory containing 'db'
        user_dir = db_dir.parent
        user_id = user_dir.name

        # Validate that user_id is not empty and not just the root
        if not user_id or user_id in ('.', '..', '/'):
            logfunc(f"[{context.get_artifact_name()}] Error - User ID could "
                    f"not be determined from path: {path}")
            return None

        return user_id

    except (TypeError, AttributeError, ValueError) as ex:
        logfunc(f"[{context.get_artifact_name()}] Error - User ID extraction "
                f"failed for {path}: {ex}")
        return None


@artifact_processor
def box_previews(context):
    """
    Process Box preview and thumbnail information from PreviewItem.db, 
    linking cached images to their respective file IDs and versions.
    """

    data_headers = (
        ('Last Accessed At', 'datetime'),
        ('Preview Thumbnail', 'media', 'height: 96px; border-radius: 5%;'),
        'Item ID',
        'File Name',
        'Preview Extension',
        'Preview Resolution',
        ('Original', 'media', 'height: 96px; border-radius: 5%;'),
        'Version ID',
        'Original SHA1',
        'User ID'
    )

    data_list = []
    source_paths = []

    source_path = context.get_source_file_path('PreviewItem.db')
    if not source_path:
        return data_headers, data_list, source_path
    source_paths.append(source_path)

    # Safely retrieve User ID from path; defaults to empty string if extraction fails
    user_id = extract_user_id_safe(source_path, context) or ''

    # SQL query utilizing JSON functions to extract representation metadata
    query = '''
    SELECT
        p.fileID AS "File ID",
        p.name AS "Preview Name",
        LOWER(json_extract(e.value, '$.representation')),
        json_extract(e.value, '$.properties.dimensions') AS "dimensions",
        TRIM(
            SUBSTR(
                json_extract(e.value, '$.info.url'),
                INSTR(json_extract(e.value, '$.info.url'), 'versions/') + 9,
                INSTR(SUBSTR(json_extract(e.value, '$.info.url'), INSTR(json_extract(e.value, '$.info.url'), 'versions/') + 9), '/') - 1
            )
        ) AS "File Version",
        p.lastAccessedDate,
        p.sha1
    FROM previewItems AS p
    JOIN json_each(p.representations, '$.entries') AS e
    ORDER BY p.lastAccessedDate DESC, p.fileID, LENGTH(dimensions) DESC, dimensions DESC
    '''

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        try:
            # Unpack record for clarity
            f_id, f_name, f_ext, dim, v_id, r_accessed, sha1 = record

            # Parsing and normalization of timestamps (ISO8601 and Unix)
            last_accessed_at = convert_unix_ts_to_utc(r_accessed)

            if not all([ f_id, f_name, f_ext, dim, sha1 ]):
                continue

            # Preview thumbnail path
            base_p = f"File Provider Storage/boxpreview/{user_id}/cache/files/{f_id}"
            preview_path = f"{base_p}/{f_ext}_{dim}/{f_name}"
            preview_ref_id = None
            if context.get_source_file_path(preview_path):
                preview_ref_id = check_in_media(preview_path, f_name)

            # Original file path
            original_path = f"{base_p}/original/{f_name}"
            original_ref_id = None
            if context.get_source_file_path(original_path):
                matcher = get_type(mime=None, ext=Path(f_name).suffix.strip('.'))
                mime = matcher.mime if matcher else matcher
                original_ref_id = check_in_media(original_path, f_name, force_type=mime)

            # LAVA row
            data_list.append((
                last_accessed_at, preview_ref_id, f_id, f_name,
                f_ext, dim, original_ref_id, v_id, sha1, user_id
            ))

        except (IndexError, TypeError, ValueError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Failed parsing record previewItems fileID {record[0]} in "
                    f"{source_path}: {ex}")
            continue

    return data_headers, data_list, '; '.join(source_paths)


@artifact_processor
def box_recents(context):
    """
    Process Box recent activity by joining Recents.db with the 
    attached Item.db to retrieve full metadata for each item.
    """

    data_headers = (
        ('Interaction Timestamp', 'datetime'),
        'Interaction Type',
        'Item ID',
        'Type',
        'Name',
        'Extension',
        'File/Folder Size'
    )

    data_list = []
    data_list_html = []

    source_path = context.get_source_file_path('Recents.db')
    if not source_path:
        return data_headers, (data_list, data_list_html), source_path
    item_db = context.get_source_file_path('Item.db')

    # Attach the Item.db database to the current query in a read-only mode
    attach_query = attach_sqlite_db_readonly(item_db, 'Item')

    # Cross-database query to fetch recents metadata from attached Item database
    query = '''
    SELECT
        r.interactionTimeStamp,
        r.interactionType,
        r.itemID,
        r.itemType,
        i.name,
        json_extract(i.jsonData, '$.extension') AS "ext",
        json_extract(i.jsonData, '$.size') AS "size"
    FROM recents AS r
    LEFT JOIN items AS i ON (r.itemID = i.modelID)
    '''

    db_records = get_sqlite_db_records(source_path, query, attach_query)

    for record in db_records:
        try:
            # Unpack for clarity
            r_int_ts, int_type, i_id, i_type, i_name, i_ext, i_size = record

            # Parsing and normalization of timestamps (ISO8601 and Unix)
            interaction_ts = convert_unix_ts_to_utc(r_int_ts)

            # Convert bytes to human-readable format (e.g., MB, GB)
            item_size_html = convert_bytes_to_unit(i_size)

            # Base row for both lists
            base_data = (
                interaction_ts, int_type, i_id, i_type, i_name, i_ext, i_size
            )

            # LAVA row
            data_list.append(base_data)

            # HTML row
            data_list_html.append(base_data[:-1] + (item_size_html,))

        except (IndexError, TypeError, ValueError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Failed parsing record recents itemID {record[2]} in "
                    f"{source_path}: {ex}")

    return data_headers, (data_list, data_list_html), source_path


@artifact_processor
def box_comments(context):
    """
    Process Box comments and annotations by correlating activity 
    between annotations.db and Item.db.
    """

    data_headers = (
        ('Created At', 'datetime'),
        'ID',
        'Type',
        ('Modified At', 'datetime'),
        'Item ID',
        'Name',
        'Message',
        'Tagged Message',
        'Is Reply',
        'Creator Login',
        'Creator Name',
        'Creator ID',
        'Modifier Login',
        'Modifier Name',
        'Modifier ID',
        ('Fetched At', 'datetime')
    )

    data_list = []

    source_path = context.get_source_file_path('annotations.db')
    if not source_path:
        return data_headers, data_list, source_path
    item_db = context.get_source_file_path('Item.db')

    # Attach Item.db to correlate activity with file names
    attach_query = attach_sqlite_db_readonly(item_db, 'Item')

    # Query fetching union of comments and annotations with conditional JSON extraction
    query = '''
    SELECT
        fa.id,
        fa.type,
        fa.createdAt,
        CASE
            WHEN fa.type = 'comment' THEN json_extract(c.jsonData, '$.modified_at')
            WHEN fa.type = 'annotation' THEN a.modifiedAt
            ELSE NULL
        END AS "modified_at",
        fa.fileID,
        i.name,
        CASE
            WHEN fa.type = 'comment' THEN json_extract(c.jsonData, '$.message')
            WHEN fa.type = 'annotation' THEN json_extract(a.descriptionJSONData, '$.message')
            ELSE NULL
        END AS "message",
        CASE
            WHEN fa.type = 'comment' THEN json_extract(c.jsonData, '$.tagged_message')
            ELSE ''
        END AS "tagged_message",
        CASE
            WHEN fa.type = 'comment' THEN c.isReply
            ELSE NULL
        END AS "isReply",
        CASE
            WHEN fa.type = 'comment' THEN json_extract(c.jsonData, '$.created_by.login')
            WHEN fa.type = 'annotation' THEN json_extract(a.createdByJSONData, '$.login')
            ELSE NULL
        END AS "created_by_login",
        CASE
            WHEN fa.type = 'comment' THEN json_extract(c.jsonData, '$.created_by.name')
            WHEN fa.type = 'annotation' THEN json_extract(a.createdByJSONData, '$.name')
            ELSE NULL
        END AS "created_by_name",
        CASE
            WHEN fa.type = 'comment' THEN json_extract(c.jsonData, '$.created_by.id')
            WHEN fa.type = 'annotation' THEN json_extract(a.createdByJSONData, '$.id')
            ELSE NULL
        END AS "created_by_id",
        CASE
            WHEN fa.type = 'comment' THEN json_extract(c.jsonData, '$.modified_by.login')
            WHEN fa.type = 'annotation' THEN json_extract(a.modifiedByJSONData, '$.login')
            ELSE NULL
        END AS "modified_by_login",
        CASE
            WHEN fa.type = 'comment' THEN json_extract(c.jsonData, '$.modified_by.name')
            WHEN fa.type = 'annotation' THEN json_extract(a.modifiedByJSONData, '$.name')
            ELSE NULL
        END AS "modified_by_name",
        CASE
            WHEN fa.type = 'comment' THEN json_extract(c.jsonData, '$.modified_by.id')
            WHEN fa.type = 'annotation' THEN json_extract(a.modifiedByJSONData, '$.id')
            ELSE NULL
        END AS "modified_by_id",
        fa.networkFetchedAt
    FROM fileActivity AS fa
    LEFT JOIN comments AS c ON (fa.id = c.id)
    LEFT JOIN annotations AS a ON (fa.id = a.id)
    LEFT JOIN items AS i ON (fa.fileID = i.modelID)
    ORDER BY i.name, fa.createdAt
    '''

    db_records = get_sqlite_db_records(source_path, query, attach_query)
    for record in db_records:
        try:
            (
                r_id, r_type, r_created, r_modified, f_id, f_name, msg, t_msg,
                reply_val, c_login, c_name, c_id, m_login, m_name, m_id, r_fetched
            ) = record


            # Parsing and normalization of timestamps (ISO8601 and Unix)
            created_at = convert_unix_ts_to_utc(r_created)
            fetched_at = convert_unix_ts_to_utc(r_fetched)

            # Differential timestamp parsing: comments use ISO8601, annotations use Unix
            if r_type == 'comment':
                modified_at = convert_iso8601_to_utc(r_modified)
            elif r_type == 'annotation':
                modified_at = convert_unix_ts_to_utc(r_modified)
            else:
                modified_at = None

            # Reply flag logic (specific to comments)
            val = int(reply_val) if reply_val is not None else None
            is_reply = 'Yes' if (r_type == 'comment' and val == 1) else \
                       ('No' if (r_type == 'comment' and val == 0) else None)

            # LAVA row
            data_list.append((
                created_at, r_id, r_type, modified_at, f_id, f_name, msg,
                t_msg, is_reply, c_login, c_name, c_id, m_login, m_name,
                m_id, fetched_at
            ))

        except (IndexError, TypeError, ValueError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Failed parsing record fileActivity id {record[0]} in "
                    f"{source_path}: {ex}")
            continue

    return data_headers, data_list, source_path
