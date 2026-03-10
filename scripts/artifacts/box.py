__artifacts_v2__ = {
    "box_account": {
        "name": "Box - Account",
        "description": "Parses and extracts Box Account information",
        "author": "@djangofaiola",
        "creation_date": "2025-12-05",
        "last_update_date": "2026-10-03",
        "requirements": "none",
        "category": "Box",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/Library/Preferences/group.net.box.BoxNet.plist',
                  '*/*group.net.box.BoxNet/Library/Preferences/group.net.box.BoxNet.plist'),
        "output_types": [ "lava", "html", "timeline" ],
        "artifact_icon": "user"
    },
    "box_all_files": {
        "name": "Box - All Files",
        "description": "Parses and extracts Box All Files information",
        "author": "@djangofaiola",
        "creation_date": "2025-12-05",
        "last_update_date": "2026-10-03",
        "requirements": "none",
        "category": "Box",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/Documents/db/Item.db*',
                  '*/mobile/Containers/Shared/AppGroup/*/Documents/offlinefilesinfo/itemIDs.plist',
                  '*/mobile/Containers/Shared/AppGroup/*/Documents/offlinefilesinfo/lastDownloadDates.plist',
                  '*/*group.net.box.BoxNet/Documents/db/Item.db*'),
        "output_types": [ "lava", "html", "timeline" ],
        "html_columns": [ "URL" ],
        "artifact_icon": "cloud"
    },
    "box_previews": {
        "name": "Box - Previews",
        "description": "Parses and extracts all Previews and Original media files",
        "author": "@djangofaiola",
        "creation_date": "2025-12-05",
        "last_update_date": "2026-10-03",
        "requirements": "none",
        "category": "Box",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/File Provider Storage/boxpreview/*/db/PreviewItem.db*',
                  '*/mobile/Containers/Shared/AppGroup/*/File Provider Storage/boxpreview/*/cache/files/*/*/*',
                  '*/*group.net.box.BoxNet/File Provider Storage/boxpreview/*/db/PreviewItem.db*'),
        "output_types": [ "lava", "html", "timeline" ],
        "html_columns": [ "URL" ],
        "artifact_icon": "image"
    },
    "box_recents": {
        "name": "Box - Recents",
        "description": "Parses and extracts Recents",
        "author": "@djangofaiola",
        "creation_date": "2025-12-05",
        "last_update_date": "2026-10-03",
        "requirements": "none",
        "category": "Box",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/Documents/db/Recents.db*',
                  '*/*group.net.box.BoxNet/Documents/db/Recents.db*',
                  '*/mobile/Containers/Shared/AppGroup/*/Documents/db/Item.db*',
                  '*/*group.net.box.BoxNet/Documents/db/Item.db*'),
        "output_types": [ "lava", "html", "timeline" ],
        "artifact_icon": "search"
    },
    "box_comments": {
        "name": "Box - Comments and Annotations",
        "description": "Parses and extracts Comments and Annotations",
        "author": "@djangofaiola",
        "creation_date": "2025-12-05",
        "last_update_date": "2026-10-03",
        "requirements": "none",
        "category": "Box",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/Documents/db/annotations.db*',
                  '*/*group.net.box.BoxNet/Documents/db/annotations.db*',
                  '*/mobile/Containers/Shared/AppGroup/*/Documents/db/Item.db*',
                  '*/*group.net.box.BoxNet/Documents/db/Item.db*'),
        "output_types": [ "lava", "html", "timeline" ],
        "artifact_icon": "message-circle"
    },
}

import re
from datetime import datetime, timezone
from pathlib import Path
import html
from urllib.parse import urlparse, urlunparse
from scripts.filetype import get_type
from scripts.ilapfuncs import artifact_processor, check_in_media, get_plist_file_content, get_plist_content, attach_sqlite_db_readonly, \
    get_sqlite_db_records, convert_unix_ts_to_utc, convert_bytes_to_unit, logfunc


# Pattern to normalize timezone offsets from +HHMM -> +HH:MM
ISO_OFFSET_FIX = re.compile(r'([+-]\d{2})(\d{2})$')

def convert_iso8601_to_utc(str_date : str) -> str:
    """
    Convert an ISO 8601 formatted date string to a canonical UTC string
    consistent with ilapfuncs.convert_unix_ts_to_utc.

    - Input is expected to be a string (framework convention).
    - Best-effort handles bytes by decoding UTF-8 (errors ignored).
    - On success returns the canonical UTC string from convert_unix_ts_to_utc.
    - On failure returns the trimmed original string and logs the parse failure.
    """
    # Preserve None explicitly
    if str_date is None:
        return None

    # Best-effort: decode bytes to str (framework functions normally accept str)
    if isinstance(str_date, bytes):
        try:
            str_date = str_date.decode('utf-8', errors='ignore')
        except Exception:
            try:
                return str(str_date)
            except Exception as e:
                logfunc(f"Box Error - convert_iso8601_to_utc: Error decoding bytes to string. Exception: {e}")
                return None

    # If not a string, preserve its string representation
    if not isinstance(str_date, str):
        try:
            return str(str_date)
        except Exception:
            return None

    s = str_date.strip()
    if not s or s.lower() == 'null':
        return s

    # Normalize trailing Z -> +00:00 (covers common API outputs)
    if s.endswith('Z'):
        s = s[:-1] + '+00:00'

    # Normalize compact offsets +HHMM -> +HH:MM
    s = ISO_OFFSET_FIX.sub(r'\1:\2', s)

    try:
        # datetime.fromisoformat on Python 3.10+ handles common ISO variants after normalization
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            # Policy: treat naive datetimes as UTC (document this choice)
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        # Return canonical project format used across iLEAPP
        return convert_unix_ts_to_utc(dt.timestamp())
    except (ValueError, TypeError) as e:
        # Forensic trace: preserve raw trimmed value and log the parse failure
        logfunc(f"Box Error - convert_iso8601_to_utc: parse failed for {s!r}: {e}")
        return s


def format_url(str_url : str, html_format : bool = False) -> str:
    """
    Normalize a raw URL and optionally format it as a safe HTML anchor.
    - If str_url is None, an empty string, or the literal 'null', return an empty string.
    - Strip surrounding whitespace.
    - If the URL has no scheme, assume 'http' as a fallback.
    - On parsing errors, return the cleaned input (do not raise).
    - When html_format=True, escape values and add rel attributes to mitigate tabnabbing.
    """
    # Treat None, empty string, and the literal 'null' as missing input; return ''.
    if str_url is None or str_url == '' or str_url == 'null':
        return ''

    s = str_url.strip()
    try:
        parsed = urlparse(s)
        # If no scheme is present, assume http (urlparse may place domain in path)
        if not parsed.scheme:
            parsed = parsed._replace(scheme='http')
        normalized = urlunparse(parsed)
    except Exception as e:
        # Forensic trace: preserve raw input and log the failure
        logfunc(f"Box Error - format_url parse failed for {str_url!r}: {e}")
        return s

    if html_format:
        # Escape href and visible text to prevent XSS
        safe_href = html.escape(normalized, quote=True)
        safe_text = html.escape(normalized, quote=False)
        # Use rel="noopener noreferrer" with target="_blank" to prevent tabnabbing
        return f'<a href="{safe_href}" target="_blank" rel="noopener noreferrer">{safe_text}</a>'

    return normalized


# Processes Box account data from the plist file
@artifact_processor
def box_account(context):

    data_headers = (
        ('Created At', 'datetime'),
        'Login',
        'Name',
        'Has custom avatar',
        'Is enterprise account',
        'User ID',
        'Timezone',
        'Language',
        'Total space',
        'Used space',
        'Max upload size'
    )
    
    data_list = []
    data_list_html = []

    source_path = context.get_source_file_path('group.net.box.BoxNet.plist')
    plist_data = get_plist_file_content(source_path)

    # Deserializing the embedded JSON string containing user metadata
    last_user_data = get_plist_content(plist_data.get('lastUserJSON'))

    if bool(last_user_data):
        try:
            # Profile and Localization metadata
            created_at = convert_iso8601_to_utc(last_user_data.get('created_at'))
            login = last_user_data.get('login')
            name = last_user_data.get('name')
            has_avatar = last_user_data.get('has_custom_avatar')
            is_enterprise = bool(last_user_data.get('enterprise'))
            user_id = last_user_data.get('id')
            timezone = last_user_data.get('timezone')
            language = last_user_data.get('language')

            # Storage metrics and quota formatting
            total_space = last_user_data.get('space_amount')
            total_space_html = convert_bytes_to_unit(total_space)
            
            used_space = last_user_data.get('space_used')
            used_space_html = convert_bytes_to_unit(used_space)
            
            max_upload_size = last_user_data.get('max_upload_size')
            max_upload_size_html = convert_bytes_to_unit(max_upload_size)

            data_list_html.append((created_at, login, name, has_avatar, is_enterprise, user_id, timezone, language, total_space_html, used_space_html, max_upload_size_html))
            data_list.append((created_at, login, name, has_avatar, is_enterprise, user_id, timezone, language, total_space, used_space, max_upload_size))

        except Exception as ex:
            logfunc(f"Box Error - Exception while parsing {context.get_artifact_name()} - {source_path}: {ex}")

    return data_headers, (data_list, data_list_html), source_path


# Processes Box file information from the Item.db SQLite database
@artifact_processor
def box_all_files(context):

    data_headers = (
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
        ('Created At', 'datetime'),
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
        'SHA1',
        'Permissions'
    )
    
    data_list = []
    data_list_html = []

    # Offline status correlation: Primary (itemIDs) and Secondary (lastDownloadDates) sources
    ids_path = context.get_source_file_path('itemIDs.plist')
    ids_data = get_plist_file_content(ids_path) if ids_path else None

    last_dates_path = context.get_source_file_path('lastDownloadDates.plist')
    last_dates_data = get_plist_file_content(last_dates_path) if last_dates_path else None

    offline_ids = dict()   
    if ids_data:
        for model_id in ids_data:
            offline_ids[str(model_id)] = { 'offline' : True, 'download_date' : None, 'source' : ids_path }

    if last_dates_data:
        for model_id, date in last_dates_data.items():
            offline_ids[str(model_id)] = { 'offline' : True, 'download_date' : date, 'source' : last_dates_path }
    offline_artifacts_available = bool(ids_data or last_dates_data)

    source_path = context.get_source_file_path('Item.db')
    source_paths = [ p for p in [ source_path, ids_path, last_dates_path ] if p ]

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
        i.SHA1,
        (
            SELECT group_concat(p.key || '=' || p.value, ', ')
            FROM json_each(json_extract(i.jsonData, '$.permissions')) AS p
        ) AS "Permissions"
    FROM cte_paths AS p
    LEFT JOIN items AS i ON (i.modelID = p.id)
    ORDER BY i.type DESC, p.path ASC;
    '''

    db_records = get_sqlite_db_records(source_path, query)
    for record in db_records:
        try:
            # Resource identifiers and basic metadata
            item_id = record[0]
            item_type = record[1]
            item_name = record[2]
            item_ext = record[3]
            full_path = record[4]
            url = record[5]
            url_html = format_url(url, html_format=True)
            description = record[6]
            item_size = record[7]
            item_size_html = convert_bytes_to_unit(item_size)
            version_id = record[8]

            # Parsing and normalization of timestamps (ISO8601 and Unix)
            content_created_at = convert_iso8601_to_utc(record[9])
            content_modified_at = convert_iso8601_to_utc(record[10])
            created_at = convert_iso8601_to_utc(record[11])
            modified_at = convert_iso8601_to_utc(record[12])
            last_fetched_at = convert_unix_ts_to_utc(record[13])

            # Ownership and tracking properties
            favorites = record[14]
            collection_names = record[15]
            owner_login = record[16]
            owner_name = record[17]
            owner_id = record[18]
            creator_login = record[19]
            creator_name = record[20]
            creator_id = record[21]
            modifier_login = record[22]
            modifier_name = record[23]
            modifier_id = record[24]

            # Integrity and access control
            sha1 = record[25]
            permissions = record[26]

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

            data_list_html.append((item_id, item_type, item_name, item_ext, full_path, url_html, description, item_size_html, version_id, \
                                   content_created_at, content_modified_at, created_at, modified_at, last_fetched_at, \
                                   is_offline, downloaded_at, offline_source, favorites, collection_names, \
                                   owner_login, owner_name, owner_id, creator_login, creator_name, creator_id, modifier_login, modifier_name, modifier_id, \
                                   sha1, permissions))

            data_list.append((item_id, item_type, item_name, item_ext, full_path, url, description, item_size, version_id, \
                              content_created_at, content_modified_at, created_at, modified_at, last_fetched_at, \
                              is_offline, downloaded_at, offline_source, favorites, collection_names, \
                              owner_login, owner_name, owner_id, creator_login, creator_name, creator_id, modifier_login, modifier_name, modifier_id, \
                              sha1, permissions))

        except Exception as ex:
            logfunc(f"Box Error - itemID {record[0]} while parsing {context.get_artifact_name()} - {source_path}: {ex}")
            continue

    return data_headers, (data_list, data_list_html), '; '.join(source_paths)


def extract_user_id_safe(path: str) -> str:
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
            return None
            
        # The user ID is the name of the directory containing 'db'
        user_dir = db_dir.parent
        user_id = user_dir.name if user_dir and user_dir.name else None
        
        if not user_id:
            logfunc(f"Box Error - User ID could not be determined from path: {path}")
            return None
            
        return user_id

    except Exception as ex:
        logfunc(f"Box Error - User ID extraction failed for {path}: {ex}")
        return None


# Processes Box preview images and thumbnails from PreviewItem.db SQLite database
@artifact_processor
def box_previews(context):
    data_headers = (
        ('Preview Thumbnail', 'media', 'height: 96px; border-radius: 5%;'),
        'Item ID',
        'File Name',
        'Preview Extension',
        'Preview Resolution',
        ('Original', 'media', 'height: 96px; border-radius: 5%;'),
        'Version ID',
        ('Last Accessed At', 'datetime'),
        'Original SHA1',
        'User ID'
    )
    
    data_list = []
    source_paths = []

    for file_found in context.get_files_found():
        source_path = str(file_found)
   
        if not file_found.endswith('PreviewItem.db'):
            continue

        source_paths.append(source_path)

        # Safely retrieve User ID from path; defaults to empty string if extraction fails
        user_id = extract_user_id_safe(source_path) or ''

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
                file_id = str(record[0] or '')
                file_name = str(record[1] or '')
                file_ext = (record[2] or '')
                dimensions = (record[3] or '')
                version_id = record[4]
                last_accessed_at = convert_unix_ts_to_utc(record[5])
                sha1 = (record[6] or '')

                if not all([ file_id, file_name, file_ext, dimensions, sha1 ]):
                    continue

                # Preview thumbnail path: "File Provider Storage/boxpreview/<userID>/cache/files/<fileID>/<extension>_<dimensions>/<preview_name>"
                preview_path = f'File Provider Storage/boxpreview/{user_id}/cache/files/{file_id}/{file_ext}_{dimensions}/{file_name}'

                preview_ref_id = None
                if context.get_source_file_path(preview_path):
                    matcher = get_type(mime=None, ext=file_ext)
                    mime = matcher.mime if matcher else matcher
                    preview_ref_id = check_in_media(preview_path, file_name, force_type=mime)


                # Original file path: "File Provider Storage/boxpreview/<userID>/cache/files/<fileID>/original/<file_name>"
                original_path = f'File Provider Storage/boxpreview/{user_id}/cache/files/{file_id}/original/{file_name}'

                original_ref_id = None
                if context.get_source_file_path(original_path):
                    matcher = get_type(mime=None, ext=Path(file_name).suffix.strip('.'))
                    mime = matcher.mime if matcher else matcher
                    original_ref_id = check_in_media(original_path, file_name, force_type=mime)

                data_list.append((preview_ref_id, file_id, file_name, file_ext, dimensions, original_ref_id, version_id, last_accessed_at, sha1, user_id))

            except Exception as ex:
                logfunc(f"Box Error - fileID {record[0]} preview '{record[1]}' in {context.get_artifact_name()} ({source_path}): {ex}")
                continue

    return data_headers, data_list, '; '.join(source_paths)


# Processes Box Recents information from the Recents.db SQLite database
@artifact_processor
def box_recents(context):

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
            interaction_ts = convert_unix_ts_to_utc(record[0])
            interaction_type = record[1]
            item_id = record[2]
            item_type = record[3]
            item_name = record[4]
            item_ext = record[5]
            item_size = record[6]
            item_size_html = convert_bytes_to_unit(item_size)

            data_list_html.append((interaction_ts, interaction_type, item_id, item_type, item_name, item_ext, item_size_html))
            data_list.append((interaction_ts, interaction_type, item_id, item_type, item_name, item_ext, item_size))

        except Exception as ex:
            logfunc(f"Box Error - itemID {record[2]} parsing {context.get_artifact_name()} - {source_path}: {ex}")
            continue

    return data_headers, (data_list, data_list_html), source_path


# Processes Box Comments and Annotations from the annotations.db SQLite database
@artifact_processor
def box_comments(context):

    data_headers = (
        'ID',
        'Type',
        ('Created At', 'datetime'),
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
            resource_id = record[0]
            resource_type = record[1]
            created_at = convert_unix_ts_to_utc(record[2])

            # Differential timestamp parsing: comments use ISO8601, annotations use Unix
            if resource_type == 'comment':
                modified_at = convert_iso8601_to_utc(record[3])
            elif resource_type == 'annotation':
                modified_at = convert_unix_ts_to_utc(record[3])
            else:
                modified_at = None

            file_id = record[4]
            file_name = record[5]
            message = record[6]
            tagged_message = record[7]

            # Reply flag logic (specific to comments)
            val = int(record[8]) if record[8] is not None else None
            if resource_type == 'comment':
                is_reply = 'Yes' if val == 1 else ('No' if val == 0 else None)
            else:
                is_reply = None                

            creator_login = record[9]
            creator_name = record[10]
            creator_id = record[11]
            modifier_login = record[12]
            modifier_name = record[13]
            modifier_id = record[14]
            fetched_at = convert_unix_ts_to_utc(record[15])

            data_list.append((resource_id, resource_type, created_at, modified_at, file_id, file_name, message, tagged_message, is_reply, creator_login, \
                              creator_name, creator_id, modifier_login, modifier_name, modifier_id, fetched_at))

        except Exception as ex:
            logfunc(f"Box Error - record {record[0]} ({record[1]}) while parsing {context.get_artifact_name()} - {source_path}: {ex}")
            continue

    return data_headers, data_list, source_path
