__artifacts_v2__ = {
    'potatochat_chats': {
        'name': 'Potato Chat - Chats',
        'description': 'Extract chats from Potato Chat',
        'author': '@C_Peter',
        'creation_date': '2025-08-17',
        'last_update_date': '2025-08-17',
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
    'potatochat_group_chats': {
        'name': 'Potato Chat - Group Chats',
        'description': 'Extract group chats from Potato Chat',
        'author': '@C_Peter',
        'creation_date': '2025-08-17',
        'last_update_date': '2025-08-17',
        'requirements': 'none',
        'category': 'Potato Chat',
        'notes': '',
        'paths': (
            '*/mobile/Containers/Shared/AppGroup/*/Documents/tgdata.db*',
            '*/mobile/Containers/Shared/AppGroup/*/Documents/shareDialogList.db*',
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
        'creation_date': '2025-08-17',
        'last_update_date': '2025-08-17',
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
import json
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

def decode_varint(source_data, offset): # Taken from https://github.com/Whee30/AppParsers/blob/main/Potato/decode_BLOB.py
    value = 0
    shift = 0
    while True:
        byte = source_data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        shift += 7 
        if (byte & 0x80) == 0:
            break
    return value, offset

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
    conversations_query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'convesations_v__' OR 'conversations_v__';"
    conversations_nr = get_sqlite_db_records(source_path, conversations_query)[0]['name']

    media_query = f'''
        SELECT
            media_type,
            media_id
        FROM
            {media_cache_nr}
    '''

    conv_query = f'''
        SELECT
            cid,
            participants
        FROM
            {conversations_nr}
    '''

    #The chat-ID is saved as little-endian blob in the media_cache table
    chat_query = f'''
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
            m.outgoing
        FROM {messages_nr} m
        LEFT JOIN {users_nr} uf 
            ON m.from_id = uf.uid
        LEFT JOIN {users_nr} ut 
            ON m.to_id = ut.uid
        LEFT JOIN {users_nr} cn 
            ON m.cid = cn.uid;
    '''
    user_cid_query = f'''
        SELECT
            uid,
            first_name,
            last_name
        FROM {users_nr}
    '''
        
    media_records = get_sqlite_db_records(source_path, media_query)
    db_records = get_sqlite_db_records(source_path, chat_query)
    conv_records = get_sqlite_db_records(source_path, conv_query)
    u_cid_records = get_sqlite_db_records(source_path, user_cid_query)


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
        if chat_name == None:
            for c_record in conv_records:
                if c_record['cid'] == chat_id and c_record['participants'] != None:
                    p_blob = c_record['participants'][:16]
                    length = p_blob[4]
                    le_cid = p_blob[-length:]
                    sc_cid = int.from_bytes(le_cid, byteorder="little")
                    c_cid = next((rec for rec in u_cid_records if rec["uid"] == sc_cid), None)
                    if c_cid:
                        if c_cid['last_name'] != None:
                            new_name = f"{c_cid['first_name']} {c_cid['last_name']}"
                        else:
                            new_name = f"{c_cid['first_name']}"
                        chat_name = f"{new_name} (Secret Chat)"
                        if sender == None: 
                            sender = new_name
                        if receiver == None:
                            receiver = new_name  
                    else:
                        chat_name = 'Unknown/Secret Chat'

        reply = ''
        location = ''
        lon = ""
        lat = ""
        if message == "" or message == None:
            if record['media']:
                blob = record['media']
                contact = bytes.fromhex("63 56 0a b9")
                call = bytes.fromhex("8b e2 67 11 18")
                location = bytes.fromhex("6e d0 9e 0c")
                message = extract_attachment_message(blob)
                try:
                    if blob[4:4 + len(location)] == location:
                        message = "Location"
                        lon_b = blob[20:28]
                        lat_b = blob[12:20]
                        lon = struct.unpack('<d', lon_b)[0]
                        lat = struct.unpack('<d', lat_b)[0]
                except:
                    lon = None
                    lat = None

                if b"foursquare" in blob:
                    try:
                        start = blob.find(b"bplist00")
                        plistb = blob[start:]
                        location = get_plist_content(plistb)
                        message = f"Location: {location}"
                    except:
                        pass
                try:
                    if blob[4:4 + len(contact)] == contact:
                        uid_b = blob[12:16]
                        c_uid = int.from_bytes(uid_b, byteorder="little")
                        c_cid = next((rec for rec in u_cid_records if rec["uid"] == c_uid), None)
                        if c_cid:
                            message = f"Contact: User-ID: {c_uid}, First Name: {c_cid['first_name']}, Last Name: {c_cid['last_name']}"
                        else:
                            message = "Contact (not found in database)"
                except:
                    pass
                try:
                    if blob[4:4 + len(call)] == call:
                        dur_b = blob[32:35]
                        dur_sec = int.from_bytes(dur_b, byteorder="little")
                        if blob[16] in (0x01, 0x23):
                            type = "Voice "
                        elif blob[16] in (0x05, 0x27):
                            type = "Video "
                        else:
                            type = ""
                        c_cid = next((rec for rec in u_cid_records if rec["uid"] == c_uid), None)
                        message = f"{type}Call - Duration: {dur_sec} Seconds"
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
        if record['media'] != None:
            for m_record in media_records:
                media_str = record['media'].hex()
                hex_path = format(abs(m_record['media_id']), 'x')
                if str(m_record['media_id']).startswith("-"):
                    unsigned = m_record['media_id'] & 0xFFFFFFFFFFFFFFFF
                    hex_path = format(int(unsigned), 'x')
                if bytes.fromhex(hex_path)[::-1].hex() in media_str:
                    if m_record['media_type'] == 2:
                        media_local_path = f'files/image-remote-{hex_path}/image.jpg'
                    elif m_record['media_type'] == 1:
                        media_local_path = f'video/remote{hex_path}.mov'
                    elif m_record['media_type'] == 3:
                        media_local_path = f'files/{hex_path}/file'
                        if str(m_record['media_id']).startswith("-"):
                            media_local_path = f'files/local{hex_path}/file'
                    else: 
                        media_local_path = None
                    if media_local_path != None:
                        attach_file_name = Path(media_local_path).name
                        attach_file = check_in_media(media_local_path, attach_file_name)
                    else:
                        attach_file = ''
                    break
        data_list.append((message_date, chat_name, chat_id, message_id, sender, sender_id, receiver, receiver_id, message, attach_file, reply, lat, lon))
        


    data_headers = (
        ('Timestamp', 'datetime'), 'Chat', 'Chat-ID', 'Message-ID', 'Sender Name', 'From ID', 'Receiver', 'To ID',
        'Message', ('Attachment File', 'media'), 'Reply (Message-ID)', 'Latitude', 'Longitude')

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

@artifact_processor
def potatochat_group_chats(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, 'tgdata.db')
    share_dialog = get_file_path(files_found, 'shareDialogList.db')
    data_list = []
    media_cache_query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'media_cache_v__';"
    media_cache_nr = get_sqlite_db_records(source_path, media_cache_query)[0]['name']
    users_query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'users_v__';"
    users_nr = get_sqlite_db_records(source_path, users_query)[0]['name']
    group_query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'share_dialog_list_users_v__';"
    group_nr = get_sqlite_db_records(share_dialog, group_query)[0]['name']
    channels_query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'channel_messages_v__';"
    channels_nr = get_sqlite_db_records(source_path, channels_query)[0]['name']
    group_query = f"SELECT userInfosJson FROM {group_nr} WHERE typeId=2"
    try:
        group_json = get_sqlite_db_records(share_dialog, group_query)[0]['userInfosJson'] 
        groups = json.loads(group_json)
    except: 
        group_json = None
        groups = []


    chat_query = f'''
        SELECT     
            mid,
            data
        FROM
            {channels_nr}
    '''
    user_cid_query = f'''
        SELECT
            uid,
            first_name,
            last_name
        FROM {users_nr}
    '''
    media_query = f'''
        SELECT
            media_type,
            media_id
        FROM
            {media_cache_nr}
    '''

    media_records = get_sqlite_db_records(source_path, media_query)
    u_cid_records = get_sqlite_db_records(source_path, user_cid_query)
    db_records = get_sqlite_db_records(source_path, chat_query)
    for record in db_records:
        message_id = record['mid']
        blob_data = record['data']
        blob_length = len(blob_data)
        working_length = 1
        working_offset = 0
        data_type = 0
        data_length = 0
        title_length = 1
        while working_offset < blob_length:
            title_length = int.from_bytes(blob_data[working_offset:working_offset + working_length])
            working_offset += working_length
            ASCII_title = blob_data[working_offset:working_offset + title_length].decode('utf-8', errors='replace')
            working_offset += title_length
            data_type = int.from_bytes(blob_data[working_offset:working_offset + 1])
            working_offset += 1
            if data_type == 1: 
                d_t = "Str"
                x = working_offset
                d = blob_data
                value, offset = decode_varint(d, x)
                working_offset = offset
                data_length = value
            elif data_type == 2:
                d_t = "Int"
                data_length = 4
            elif data_type == 3:
                d_t = "Int"
                data_length = 8
            elif data_type == 6: 
                d_t = "Varint"
                x = working_offset
                d = blob_data
                value, offset = decode_varint(d, x)
                working_offset = offset
                data_length = value
            else:
                break
            payload_data = blob_data[working_offset:working_offset + data_length]
            working_offset += data_length
            formatted_bytes = ' '.join(f'{byte:02X}' for byte in payload_data)
            if d_t == "Str" and ASCII_title == "t":
                message = payload_data.decode('utf-8', errors='replace')
            elif d_t == "Int" and ASCII_title == 'd':
                timestamp = int.from_bytes(payload_data, byteorder='little')
                message_date = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
            elif ASCII_title == "ti" or ASCII_title == "ci": 
                group_ID = abs(int.from_bytes(payload_data[0:4], byteorder="little", signed=True))
                try:
                    group = next((rec for rec in groups if rec.get("groupId") == group_ID), None)
                    group_name = group["title"]
                except:
                    group_name = None
            elif ASCII_title == "fi":
                user_ID = int.from_bytes(payload_data, byteorder='little')
                c_uid = next((rec for rec in u_cid_records if rec["uid"] == user_ID), None)
                if c_uid:
                    if c_uid['last_name'] != None:
                        user_name = f"{c_uid['first_name']} {c_uid['last_name']}"
                    else:
                        user_name = f"{c_uid['first_name']}"
                else:
                    user_name = None
            elif ASCII_title == 'i':
                mid = int.from_bytes(payload_data, byteorder='little')
            elif ASCII_title == 'out':
                outgoing = int.from_bytes(payload_data, byteorder='little')
            attach_file = ''
            for m_record in media_records:
                media_str = blob_data.hex()
                hex_path = format(abs(m_record['media_id']), 'x')
                if str(m_record['media_id']).startswith("-"):
                    unsigned = m_record['media_id'] & 0xFFFFFFFFFFFFFFFF
                    hex_path = format(int(unsigned), 'x')
                if bytes.fromhex(hex_path)[::-1].hex() in media_str:
                    if m_record['media_type'] == 2:
                        media_local_path = f'files/image-remote-{hex_path}/image.jpg'
                    elif m_record['media_type'] == 1:
                        media_local_path = f'video/remote{hex_path}.mov'
                    elif m_record['media_type'] == 3:
                        media_local_path = f'files/{hex_path}/file'
                        if str(m_record['media_id']).startswith("-"):
                            media_local_path = f'files/local{hex_path}/file'
                    else: 
                        media_local_path = None
                    if media_local_path != None:
                        attach_file_name = Path(media_local_path).name
                        attach_file = check_in_media(media_local_path, attach_file_name)
                    else:
                        attach_file = ''
                    break
        data_list.append((message_date, group_name, group_ID, message_id, user_name, user_ID, message, attach_file))

    data_headers = (
        ('Timestamp', 'datetime'), 'Group Name', 'Group-ID', 'Message-ID', 'Sender Name', 'From ID',
        'Message', ('Attachment File', 'media'))

    return data_headers, data_list, source_path