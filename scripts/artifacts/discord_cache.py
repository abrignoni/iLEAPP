""" discord_cache.py """
__artifacts_v2__ = {
    "discord_cache": {
        "name": "Discord Cache",
        "description": "Parses Discord URL cache records and files from Cache.db and fsCachedData",
        "author": "@JamesHabben",
        "creation_date": "2026-05-29",
        "last_updated": "2026-05-29",
        "requirements": "none",
        "category": "Discord",
        "notes": "",
        "paths": (
            '*/Library/Caches/com.hammerandchisel.discord/Cache.db*',
            '*/Library/Caches/com.hammerandchisel.discord/fsCachedData/*'
        ),
        "output_types": "standard",
        "artifact_icon": "database"
    }
}

import os
import sqlite3
import json
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly, check_in_media,\
     check_in_embedded_media, get_plist_content
from scripts.filetype import guess_mime

def detect_payload_type(data, path=None):
    """
    Detects payload type using filetype library and fallbacks.
    """
    mime = None
    try:
        if path and os.path.exists(path):
            mime = guess_mime(path)
        elif data:
            mime = guess_mime(data)
    except (TypeError, OSError, AttributeError) as e:
        logfunc(f"Error in guess_mime: {e}")

    if mime:
        return mime

    if not data:
        return "Unknown"

    # Fallbacks
    try:
        # Check for JSON Array or Object
        # Find first non-whitespace byte
        first_byte = None
        for b in data:
            if b not in b' \n\r\t':
                first_byte = b
                break

        if first_byte == ord('['):
            return "application/json (Array)"
        if first_byte == ord('{'):
            return "application/json (Object)"
    except (AttributeError, TypeError, ValueError):
        pass

    if data.startswith(b'\x1f\x8b'):
        return "application/gzip"

    if data.startswith(b'SQLite format 3'):
        return "application/x-sqlite3"

    try:
        data.decode('utf-8')
        return "text/plain"
    except UnicodeDecodeError:
        pass

    return "application/octet-stream"

def get_payload_preview(data, p_type):
    """
    Generates a preview of the payload.
    """
    if not data:
        return ""

    p_type_lower = p_type.lower()
    if "json" in p_type_lower or "text" in p_type_lower:
        try:
            preview = data[:150].decode('utf-8', errors='replace')
            # Sanitize: replace newlines/tabs with spaces for better report display
            preview = preview.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            return preview
        except (UnicodeDecodeError, AttributeError):
            pass

    # Binary fallback: first 30 bytes in hex
    return ' '.join(f'{b:02X}' for b in data[:30])

@artifact_processor
def discord_cache(context):
    """ see artifact info """
    files_found = context.get_files_found()
    seeker = context.get_seeker()
    data_list = []

    def get_rel_path(path):
        if path in seeker.file_infos:
            return seeker.file_infos[path].source_path
        return path

    # Track all fsCachedData files to find orphans
    fs_cached_files = {} # path -> seen_in_db (bool)
    cache_db_files = []

    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('Cache.db'):
            cache_db_files.append(file_found)
        elif 'fsCachedData' in file_found:
            if os.path.isfile(file_found):
                fs_cached_files[file_found] = False

    for cache_db in cache_db_files:
        db = open_sqlite_db_readonly(cache_db)
        if not db:
            logfunc(f"Could not open Discord Cache.db at {cache_db}")
            continue

        cursor = db.cursor()
        query = '''
        SELECT
            r.entry_ID,
            r.version,
            r.hash_value,
            r.storage_policy,
            r.request_key,
            r.time_stamp,
            r.partition,
            rd.isDataOnFS,
            rd.receiver_data,
            b.response_object,
            b.request_object,
            b.proto_props,
            b.user_info
        FROM cfurl_cache_response r
        LEFT JOIN cfurl_cache_receiver_data rd
            ON rd.entry_ID = r.entry_ID
        LEFT JOIN cfurl_cache_blob_data b
            ON b.entry_ID = r.entry_ID
        ORDER BY r.entry_ID;
        '''

        try:
            cursor.execute(query)
            rows = cursor.fetchall()
        except sqlite3.Error as e:
            logfunc(f"Error querying Discord Cache.db at {cache_db}: {e}")
            db.close()
            continue

        # Get the sibling fsCachedData directory
        cache_dir = os.path.dirname(cache_db)
        fs_cached_dir = os.path.join(cache_dir, 'fsCachedData')

        for row in rows:
            entry_id = row[0]
            request_key = row[4]
            timestamp = row[5]
            storage_policy = row[3]
            partition = row[6]
            is_data_on_fs = row[7]
            receiver_data = row[8]

            # BLOB data
            response_obj = row[9]
            request_obj = row[10]
            proto_props = row[11]
            user_info = row[12]

            def decode_blob(blob):
                if not blob:
                    return ""
                try:
                    content = get_plist_content(blob)
                    return json.dumps(content, indent=4, default=str)
                except (TypeError, ValueError, AttributeError, OSError) as e:
                    return f"Error decoding: {e}"

            response_obj_decoded = decode_blob(response_obj)
            request_obj_decoded = decode_blob(request_obj)
            proto_props_decoded = decode_blob(proto_props)
            user_info_decoded = decode_blob(user_info)

            payload_exists = False
            payload_path = ""
            payload_data = None
            cache_filename = ""
            media_preview = None
            payload_size = 0

            if is_data_on_fs == 1:
                # receiver_data is a filename
                try:
                    if receiver_data:
                        if isinstance(receiver_data, bytes):
                            cache_filename = receiver_data.decode('utf-8', errors='replace')
                        else:
                            cache_filename = str(receiver_data)

                        payload_path = os.path.join(fs_cached_dir, cache_filename)
                        if os.path.exists(payload_path):
                            payload_exists = True
                            # Mark as seen
                            if payload_path in fs_cached_files:
                                fs_cached_files[payload_path] = True

                            # Read small portion for type detection and preview
                            with open(payload_path, 'rb') as f:
                                payload_data = f.read(8192) # Read enough for detection

                            payload_size = os.path.getsize(payload_path)
                        else:
                            payload_size = 0
                    else:
                        cache_filename = ""
                        payload_size = 0
                except (OSError, UnicodeDecodeError, AttributeError) as e:
                    logfunc(f"Error processing on-disk payload for entry {entry_id}: {e}")
                    payload_size = 0
            else:
                # receiver_data is inline bytes
                payload_data = receiver_data
                payload_size = len(receiver_data) if receiver_data else 0
                payload_exists = True if payload_size > 0 else False

            p_type = detect_payload_type(payload_data, payload_path if is_data_on_fs == 1 else None)
            p_preview = get_payload_preview(payload_data, p_type)

            # Media handling
            if payload_exists:
                p_type_lower = p_type.lower()
                if any(x in p_type_lower for x in ['image', 'video', 'audio']):
                    if is_data_on_fs == 1:
                        media_preview = check_in_media(payload_path)
                    else:
                        media_preview = check_in_embedded_media(cache_db, receiver_data, name=f"entry_{entry_id}")

            data_list.append((
                entry_id, timestamp, media_preview, request_key,
                storage_policy, partition, is_data_on_fs, cache_filename, payload_exists,
                False, # Orphaned Payload
                get_rel_path(payload_path), payload_size, p_type, p_preview,
                response_obj_decoded, request_obj_decoded, proto_props_decoded, user_info_decoded,
                get_rel_path(cache_db)
            ))

        db.close()

    # Process Orphans
    for path, seen in fs_cached_files.items():
        if not seen:
            # Orphaned file
            payload_data = None
            payload_size = 0
            try:
                if os.path.exists(path):
                    with open(path, 'rb') as f:
                        payload_data = f.read(8192)
                    payload_size = os.path.getsize(path)
            except (OSError, AttributeError):
                pass

            p_type = detect_payload_type(payload_data, path)
            p_preview = get_payload_preview(payload_data, p_type)

            media_preview = None
            p_type_lower = p_type.lower()
            if any(x in p_type_lower for x in ['image', 'video', 'audio']):
                media_preview = check_in_media(path)

            data_list.append((
                "", # Cache Entry ID
                "", # Cache Timestamp
                media_preview,
                "", # Request URL
                "", # Storage Policy
                "", # Partition
                "", # Is Data On Filesystem
                os.path.basename(path), # Cache Filename
                True, # Payload Exists
                True, # Orphaned Payload
                get_rel_path(path), payload_size, p_type, p_preview,
                "", "", "", "", # BLOB data
                "" # Source DB
            ))

    data_headers = (
        'Cache Entry ID', ('Cache Timestamp', 'datetime'), ('Media Preview', 'media'),
        'Request URL', 'Storage Policy', 'Partition', 'Is Data On Filesystem', 'Cache Filename',
        'Payload Exists', 'Orphaned Payload', 'Payload Path', 'Payload Size', 'Payload Type',
        'Payload Preview', 'Response Object', 'Request Object', 'Proto Props', 'User Info',
        'Source DB'
    )

    return data_headers, data_list, 'See source file(s) below:'
