__artifacts_v2__ = {
    'potatochat_chats': {
        'name': 'Potato Chat - Chats',
        'description': 'Extract chats from Potato Chat',
        'author': '@C_Peter',
        'creation_date': '2025-08-13',
        'last_update_date': '2025-08-13',
        'requirements': 'none',
        'category': 'Potato Chat',
        'notes': '',
        'paths': (
            '*/mobile/Containers/Shared/AppGroup/*/Documents/tgdata.db*',
            '*/mobile/Containers/Shared/AppGroup/*/Documents/files/*',
            '*/mobile/Containers/Shared/AppGroup/*/Documents/video/*',
        ),
        'output_types': 'standard',
        'artifact_icon': 'message-square',
    },
    'potatochat_users': {
        'name': 'Potato Chat - Known Users',
        'description': 'Extract known users from Potato Chat',
        'author': '@C_Peter',
        'creation_date': '2025-08-13',
        'last_update_date': '2025-08-13',
        'requirements': 'none',
        'category': 'Potato Chat',
        'notes': '',
        'paths': (
            '*/mobile/Containers/Shared/AppGroup/*/Documents/tgdata.db*',
        ),
        'output_types': 'standard',
        'artifact_icon': 'users',
    }
}

import datetime
import struct
import plistlib
from pathlib import Path
from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records, attach_sqlite_db_readonly, \
    check_in_media, get_plist_content

def extract_attachment_message(media_blob):
    if media_blob is None:
        return None
    else:
        pass

    marker = bytes.fromhex("44 00 00 a0 44")
    end_marker = b"\x00" * 6
    start_index = media_blob.rfind(marker)
    if start_index == -1:
        return None
    msg_start = start_index + len(marker) + 16
    end_index = media_blob.find(end_marker, msg_start)
    if end_index == -1:
        return None
    
    msg_bytes = media_blob[msg_start:end_index]
    try:
        return msg_bytes.decode("utf-8", errors="replace")
    except UnicodeDecodeError:
        return None

@artifact_processor
def potatochat_chats(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, 'tgdata.db')
    data_list = []
    #The table names aren't fix and change the trailing number from time to time
    messages_query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'messages_v__';"
    messages_nr = get_sqlite_db_records(source_path, messages_query)[0]['name']
    media_cache_query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'media_cache_v__';"
    media_cache_nr = get_sqlite_db_records(source_path, media_cache_query)[0]['name']
    users_query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'users_v__';"
    users_nr = get_sqlite_db_records(source_path, users_query)[0]['name']


    #The chat-ID is saved as little-endian blob in the media_cache table
    chat_query = f'''
        WITH mc_swapped AS (
            SELECT
                *,
                ("0x" || hex(substr(mids, 4,1)) || 
                         hex(substr(mids, 3,1)) || 
                         hex(substr(mids, 2,1)) || 
                         hex(substr(mids, 1,1)) 
                )->>'$' AS mid_hex
            FROM {media_cache_nr}
        )
        SELECT     
            m."date",
            CASE 
                WHEN cn.last_name IS NULL OR cn.last_name = '' THEN cn.first_name
                ELSE cn.first_name || ' ' || cn.last_name
            END AS chat,
            m.cid,
            m.mid,
            m.message,
            m.media,
            CASE 
                WHEN uf.last_name IS NULL OR uf.last_name = '' THEN uf.first_name
                ELSE uf.first_name || ' ' || uf.last_name
            END AS from_name,
            m.from_id,
            CASE 
                WHEN ut.last_name IS NULL OR ut.last_name = '' THEN ut.first_name
                ELSE ut.first_name || ' ' || ut.last_name
            END AS to_name,
            m.to_id,
            m.outgoing,
            mc.media_type,
            mc.media_id
        FROM {messages_nr} m
        LEFT JOIN mc_swapped mc
            ON m.mid = mid_hex
        LEFT JOIN {users_nr} uf 
            ON m.from_id = uf.uid
        LEFT JOIN {users_nr} ut 
            ON m.to_id = ut.uid
        LEFT JOIN {users_nr} cn 
            ON m.cid = cn.uid;
    '''
    db_records = get_sqlite_db_records(source_path, chat_query)
    for record in db_records:
        message_date = datetime.datetime.fromtimestamp(record['date'], tz=datetime.timezone.utc)
        chat_name = record['chat']
        chat_id = record['cid']
        message_id = record['mid']
        sender = 'Local User' if record['outgoing'] == 1 else record['from_name']
        sender_id = record['from_id']
        receiver = record['to_name'] if record['outgoing'] == 1 else 'Local User'
        receiver_id = record['to_id']
        message = record['message']
        reply = ''
        location = ''
        if message == "" or message == None:
            if record['media']:
                message = extract_attachment_message(record['media'])
                if b"foursquare" in record['media']:
                    try:
                        locblob = record['media']
                        start = locblob.find(b"bplist00")
                        plistb = locblob[start:]
                        location = get_plist_content(plistb)
                        message = f"Location: {location}"

                    except:
                        pass

        else:
            if record['media']:
                if b"replyMessage" in record['media']:
                    try:
                        reblob = record['media']
                        replystart = reblob.find(b"replyMessage")
                        pattern = b"\x01\x69\x02"
                        nr_start = reblob.find(pattern, replystart)
                        id_start = nr_start + len(pattern)
                        id_bytes = reblob[id_start:id_start+4]
                        reply = struct.unpack("<I", id_bytes)[0]
                    except:
                        pass

        attach_file = ''
        if record['media_id'] != None:
            if record['media'] != None:
                media_found = False
                media_str = record['media'].hex()
                hex_path = format(int(record['media_id']), 'x')
                # Check if the media_id is present in the media_blob - Message IDs can be given multiple times
                if str(record['media_id']).encode().hex() in media_str:
                    media_found = True
                elif bytes.fromhex(hex_path)[::-1].hex() in media_str:
                    media_found = True
                else:
                    if record['message'] == "" or record['message'] == None:
                        continue
                    else:
                        attach_file = ''
                if media_found:
                    if record['media_type'] == 2:
                        media_local_path = f'files/image-remote-{hex_path}/image.jpg'
                    elif record['media_type'] == 1:
                        media_local_path = f'video/remote{hex_path}.mov'
                    elif record['media_type'] == 3:
                        media_local_path = f'files/{hex_path}/file'
                    else: 
                        media_local_path = None
                    if media_local_path != None:
                        attach_file_name = Path(media_local_path).name
                        attach_file = check_in_media(media_local_path, attach_file_name)
                    else:
                        attach_file = ''
            else:
                pass
        data_list.append((message_date, chat_name, chat_id, message_id, sender, sender_id, receiver, receiver_id, message, attach_file, reply))
        


    data_headers = (
        ('Timestamp', 'datetime'), 'Chat', 'Chat-ID', 'Message-ID', 'Sender Name', 'From ID', 'Receiver', 'To ID',
        'Message', ('Attachment File', 'media'), 'Reply (Message-ID)')

    return data_headers, data_list, source_path

@artifact_processor
def potatochat_users(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, 'tgdata.db')
    data_list = []
    users_query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'users_v__';"
    users_nr = get_sqlite_db_records(source_path, users_query)[0]['name']
    list_query = f'''
        SELECT
            uid,
            first_name,
            last_name,
            access_hash,
            username,
            last_seen
        FROM {users_nr}
    '''
    db_records = get_sqlite_db_records(source_path, list_query)
    for record in db_records:
        user_id = record['uid']
        first_name = record['first_name']
        last_name = record['last_name']
        acc_hash = record['access_hash']
        username = record ['username']
        if int(record['last_seen']) > 1:
            last_seen = datetime.datetime.fromtimestamp(record['last_seen'], tz=datetime.timezone.utc)
        else:
            last_seen = ''
        data_list.append((user_id, first_name, last_name, acc_hash, username, last_seen))
    
    data_headers = (
        'User-ID', 'First Name', 'Last Name', 'Access Hash', 'Username', ('Last Seen', 'datetime'))

    return data_headers, data_list, source_path