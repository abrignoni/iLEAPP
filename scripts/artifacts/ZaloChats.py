__artifacts_v2__ = {
    "zalo_messages": {
        "name": "Zalo - Chats",
        "description": "'Extract chats and groupchats from Zalo",
        "author": "C_Peter",
        "version": "0.0.1",
        "creatin_date": "2026-06-01",
        "last_update_date": "2026-06-01",
        "requirements": "pillow",
        "category": "Zalo",
        "notes": "",
        "paths": (  
            '*/mobile/Containers/Data/Application/*/Documents/chat_dbs/*/*',
            '*/mobile/Containers/Data/Application/*/Documents/profile.sqlite',
            '*/mobile/Containers/Data/Application/*/Documents/chatgroup.sqlite',
            '*/mobile/Containers/Data/Application/*/Documents/Files/*/*',
            '*/mobile/Containers/Data/Application/*/Documents/Sticker/Snapshot/*/*/*',
            '*/mobile/Containers/Data/Application/*/Documents/[0-9]*[0-9]/[0-9]*[0-9]/*/*.*',
            '*/mobile/Containers/Data/Application/*/tmp/[0-9]*[0-9]/[0-9]*[0-9]/*/*.*'
        ),
        "output_types": "standard",
        'data_views': {
            'conversation': {
                'conversationDiscriminatorColumn': 'Chat Name',
                'conversationLabelColumn': 'Chat Name',
                'textColumn': 'Message',
                'directionColumn': 'Outgoing',
                'directionSentValue': 1,
                'timeColumn': 'Timestamp',
                'senderColumn': 'Sender',
                'mediaColumn': 'Attachment File'
                }
        },
        "artifact_icon": "message-square"
    },
    "zalo_users": {
        "name": "Zalo - Known Users",
        "description": "Extract known users from Zalo",
        "author": "C_Peter",
        "version": "0.0.1",
        "creatin_date": "2026-06-01",
        "last_update_date": "2026-06-01",
        "requirements": "none",
        "category": "Zalo",
        "notes": "",
        "paths": (  
            '*/mobile/Containers/Data/Application/*/Documents/profile.sqlite'
        ),
        "output_types": "standard",
        "artifact_icon": "users"
    }
}

import re
import json
from io import BytesIO
from pathlib import Path
from PIL import Image

from scripts.ilapfuncs import artifact_processor, \
    convert_unix_ts_to_utc, get_sqlite_db_records, \
    check_in_media, check_in_embedded_media, get_file_path

def extract_last_url(blob) -> str | None:
    """Searches the msg_blob for the last URL"""
    if blob is None:
        return None
    if isinstance(blob, bytes):
        pass
    else:
        blob = blob.tobytes()
    pattern = rb'https?://[^\x00\s"]+'
    matches = re.findall(pattern, blob)
    if not matches:
        return None
    return matches[-1].decode("utf-8", errors="ignore")

def build_gif(png_files, metadata_file):
    """Recreates Stickers from multiple PNG files"""
    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    duration_list = metadata.get("duration", [100])
    if len(duration_list) == 1:
        duration_list = duration_list * len(png_files)
    frames = [Image.open(p).convert("RGBA") for p in sorted(png_files)]
    output = BytesIO()
    frames[0].save(
        output,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=duration_list,
        loop=0,
        disposal=2,
        transparency=0
    )
    output.seek(0)
    return output

@artifact_processor
def zalo_users(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    """Extracts known Zalo Users"""
    data_list = []
    source_path = get_file_path(files_found, 'profile.sqlite')

    user_query = '''
        SELECT
            pe.userid,
            pe.displayname,
            be.mobile,
            ge.globalid
        FROM
            ProfileEntity pe
        LEFT JOIN BuddyEntity be
            ON pe.userid=be.zaloid
        LEFT JOIN GlobalIdEntity ge
            ON pe.userid=ge.rawid
        '''

    user_records = get_sqlite_db_records(source_path, user_query)
    for record in user_records:
        uid = record["userid"]
        uname = record["displayname"]
        umobile = record["mobile"]
        uglobal = record["globalid"]

        data_list.append([uid, uname, umobile, uglobal])

    data_headers = ("User-ID", "Username", "Mobile", "Global-ID")

    return data_headers, data_list, source_path


@artifact_processor
def zalo_messages(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    """Extracts Zalo Chats and Groupchats"""
    data_list = []
    chat_dbs = [x for x in files_found if "chat_dbs" in x and x.endswith('.db') and "_ext" not in x]
    chat_dbs = list(set(chat_dbs))
    first_db = chat_dbs[0]
    first_db_path = Path(first_db)
    idx = first_db_path.parts.index("chat_dbs")
    user_id = first_db_path.parts[idx + 1]
    #user_id = first_db.split("chat_dbs/")[1].split("/")[0]
    print(f"Found local user id: {user_id}")
    db_path_parts = Path(first_db).parts
    idx = db_path_parts.index("Documents")
    uuid = db_path_parts[idx - 1]
    files_found = [x for x in files_found if uuid in x]
    chat_info = get_file_path(files_found, 'profile.sqlite')
    group_info = get_file_path(files_found, 'chatgroup.sqlite')
    media_pattern = re.compile(rf"/(?:Documents|tmp)/{user_id}/\d+/")
    media_list = [x for x in files_found if media_pattern.search(x.replace("\\", "/"))]
    file_pattern = re.compile(r"^.*?/Documents/Files/(?P<hash>[a-fA-F0-9]{32})/(?P<filename>[^/]+)$")
    file_dicts = []
    for file in files_found:
        match = file_pattern.match(file.replace("\\", "/"))
        if match:
            file_dicts.append({
                "path": file,
                "hash": match.group("hash"),
                "filename": match.group("filename"),
            })

    user_query = '''
        SELECT
            userid,
            displayname
        FROM
            ProfileEntity
    '''
    group_query = '''
        SELECT
            groupid,
            name
        FROM
            GroupEntity
    '''
    content_query = '''
        SELECT
            SenderId,
            CliMsgId,
            MsgType,
            TimeStamp,
            MsgContent,
            BinNet,
            LocalPath
        FROM
            ChatContent
    '''

    user_dict = {}
    user_records = get_sqlite_db_records(chat_info, user_query)
    for record in user_records:
        uid = record["userid"]
        uname = record["displayname"]
        user_dict[uid] = uname

    group_dict = {}
    group_records = get_sqlite_db_records(group_info, group_query)
    for record in group_records:
        gid = record["groupid"]
        gname = record["name"]
        group_dict[gid] = gname

    for db_file in chat_dbs:
        source_file = db_file
        isgroup = False
        if "group_" in db_file:
            isgroup = True
            chat_id = db_file.split("group_")[1].split(".db")[0]
            chat_name = group_dict.get(chat_id, None)
        else:
            chat_id = Path(db_file).stem
            chat_name = user_dict.get(chat_id, f"Unknown ({chat_id})")
        db_records = get_sqlite_db_records(db_file, content_query)
        for record in db_records:
            sender_id = record["SenderID"]
            if str(sender_id) == str(user_id):
                outgoing = 1
            else:
                outgoing = 0
            sender_name = user_dict.get(str(sender_id), sender_id)
            timestamp = record["TimeStamp"]
            message_date = convert_unix_ts_to_utc(timestamp)
            msg_type = record["MsgType"]
            message = record["MsgContent"]
            msg_blob = record["BinNet"]
            local_path = record["LocalPath"]
            attach_file = None
            has_local_path = False
            if local_path not in [None, ""]:
                has_local_path = True
                full_path = Path(local_path)
                attach_file_name = full_path.name
                idx = len(full_path.parts) - 1 - full_path.parts[::-1].index("Documents")
                short_path = str(Path(*full_path.parts[idx + 1:]))
                #short_path = local_path.rsplit("/Documents/", 1)[-1]
                attach_file = check_in_media(short_path, attach_file_name)
            print_type = "Unknown"
            # Text Message
            if msg_type == 0:
                print_type = "Message"
            # Voice Note
            if msg_type == 6:
                print_type = "Voice Note" 
                if message in ["", None, " "]:
                    message = extract_last_url(msg_blob)
            # Sticker
            if msg_type == 10:
                print_type = "Sticker"
                try:
                    cateid, eid = message.strip("[]^").split(",")
                    sticker_files = [x for x in files_found if f"Sticker/Snapshot/{cateid}/{eid}/" in x.replace("\\", "/")]
                    if sticker_files != []:
                        png_files = [p for p in sticker_files if p.endswith(".png")]
                        metadata_file = next((p for p in sticker_files if "metadata" in p), None)
                        if len(png_files) == 1:
                            p = Path(png_files[0])
                            idx = len(p.parts) - 1 - p.parts[::-1].index("Documents")
                            short_path = str(Path(*p.parts[idx + 1:]))
                            attach_file_name = f"Sticker_{cateid},{eid}"
                            attach_file = check_in_media(short_path, attach_file_name)
                            message = f"Sticker: cateid={cateid} eid={eid}"
                        elif len(png_files) > 1 and metadata_file:
                            try:
                                sticker = build_gif(png_files, metadata_file).getvalue()
                                attach_file_name = f"Sticker_{cateid},{eid}"
                                attach_file = check_in_embedded_media(f"Sticker/Snapshot/{cateid}/{eid}/metadata", sticker, attach_file_name)
                                message = f"Sticker: cateid={cateid} eid={eid}"
                            except ValueError:
                                message = f"Failed to recreate Sticker: cateid={cateid} eid={eid}"
                        else:
                            message = f"Missing Sticker: cateid={cateid} eid={eid}"
                    else:
                        message = f"Missing Sticker: cateid={cateid} eid={eid}"
                except ValueError:
                    pass

            # Call / Link
            if msg_type == 12:
                type_call = "recommened.calltime"
                type_missed = "recommened.misscall"
                type_groupcall = "recommened.groupcall"
                type_link = "recommened.link"
                type_user = "recommened.user"
                if isinstance(msg_blob, bytes):
                    if type_call.encode() in msg_blob:
                        print_type = "Call"
                    elif type_missed.encode() in msg_blob:
                        print_type = "Missed Call"
                    elif type_groupcall.encode() in msg_blob:
                        print_type = "Groupcall"
                    elif type_link.encode() in msg_blob:
                        print_type = "Link"
                    elif type_user.encode() in msg_blob:
                        print_type = "User"
                    else:
                        print_type = "Unknown (12)"
                else:
                    if type_call in msg_blob:
                        print_type = "Call"
                    elif type_missed in msg_blob:
                        print_type = "Missed Call"
                    elif type_groupcall in msg_blob:
                        print_type = "Groupcall"
                    elif type_link in msg_blob:
                        print_type = "Link"
                    elif type_user in msg_blob:
                        print_type = "User"
                    else:
                        print_type = "Unknown) 12"
                if print_type == "Link":
                    if message in ["", None, " "]:
                        message = extract_last_url(msg_blob)
                if print_type == "User":
                    username = user_dict.get(message, None)
                    if username:
                        message = message + f" ({username})"
            # System Message
            if msg_type in [15,20,24,36]:
                print_type = "System Message"
            # Poll
            if msg_type == 26:
                print_type = "Poll"
            # Media File
            if msg_type in [1,2,3,4,19,23]:
                print_type = "Media"
                if not has_local_path:
                    candidates = []
                    for file in media_list:
                        if chat_id not in file:
                            continue
                        if file.lower().endswith(".zins"):
                            continue
                        full_path = Path(file)
                        if not full_path.is_file():
                            continue

                        stem = full_path.stem

                        if isinstance(msg_blob, bytes):
                            match = stem.encode() in msg_blob
                        else:
                            match = stem in msg_blob

                        if match:
                            candidates.append(file)

                    best_file = next(
                        (f for f in candidates if not f.lower().endswith((".jpg", ".jpeg"))),
                        None
                    )

                    if best_file is None and candidates:
                        best_file = candidates[0]

                    if best_file:
                        p = Path(best_file)
                        idx = len(p.parts) - 1 - p.parts[::-1].index("Documents")
                        short_path = str(Path(*p.parts[idx + 1:]))
                        #short_path = best_file.rsplit("/Documents/", 1)[-1]
                    if best_file is not None:
                        attach_file = check_in_media(short_path, Path(best_file).name)
                    else:
                        attach_file = None
                        if message in [None, "", " "]:
                            message = extract_last_url(msg_blob)
            # Other File
            if msg_type == 22:
                print_type = "File"
                if not has_local_path:
                    blob_path = None
                    for file in file_dicts:
                        full_path = Path(file["path"])
                        if not full_path.is_file():
                            continue
                        if isinstance(msg_blob, bytes):
                            if file["hash"].encode() in msg_blob and file["filename"].encode() in msg_blob:
                                blob_path = file["path"]
                        else:
                            if file["hash"] in msg_blob and file["filename"] in msg_blob:
                                blob_path = file["path"]
                    if blob_path is not None:
                        p = Path(blob_path)
                        idx = len(p.parts) - 1 - p.parts[::-1].index("Documents")
                        short_path = str(Path(*p.parts[idx + 1:]))
                        #short_path = blob_path.rsplit("/Documents/", 1)[-1]
                        attach_file = check_in_media(short_path, Path(blob_path).name)
                    else:
                        attach_file = None
            # Location
            latitude = None
            longitude = None
            if msg_type == 18:
                print_type = "Location"
                blobtext = msg_blob.decode("utf-8", errors="ignore")
                lat_match = re.search(r'"latitude":(-?\d+(?:\.\d+)?)', blobtext)
                lon_match = re.search(r'"longitude":(-?\d+(?:\.\d+)?)', blobtext)
                if lat_match and lon_match:
                    latitude = float(lat_match.group(1))
                    longitude = float(lon_match.group(1))
                    if message in [None, "", " "]:
                        message = f"geo:{latitude},{longitude}"

            data_list.append([message_date, chat_name, sender_id, sender_name, msg_type, print_type, message, attach_file, latitude, longitude, outgoing, isgroup, source_file])

    data_headers = (('Timestamp', 'datetime'), "Chat Name", "Sender-ID", "Sender", "Type ID", "Message Type", "Message", ('Attachment File', 'media'), "Latitude", "Longitude", "Outgoing", "Group Chat", "Source File")

    return data_headers, data_list, 'See Table for Source DB'
