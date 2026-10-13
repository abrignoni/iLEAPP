__artifacts_v2__ = {
    "zalo_messages": {
        "name": "Zalo - Chats",
        "description": "Messages from the ChatContent table of each Zalo chat database under Documents/chat_dbs, for one to one and group chats, with the attached file where one is found.",
        "author": "C_Peter",
        "creatin_date": "2026-06-01",
        "creation_date": "2026-06-01",
        "last_update_date": "2026-10-09",
        "requirements": "pillow",
        "category": "Zalo",
        "notes": "Message type mappings are not vendor-documented and no published source for "
                 "them is cited. They were derived from test data that is not recorded here, so "
                 "each label is a reading of the stored type code and not an established meaning. "
                 "Unrecognized types are reported as Unknown, or for type 12 rows with no "
                 "recognised marker as 'Unknown (12)', with the raw Type ID "
                 "column. Outgoing is not a stored flag: it is 1 when the row's SenderId equals "
                 "the account id taken from the chat_dbs folder name of the database the row was "
                 "read from. Sender and chat names, media files and attached files are looked up "
                 "in the app container that holds that database. Attachment File is the file "
                 "the row's LocalPath names where one is stored. Where it is not, media rows are "
                 "matched to a file in the account's media folders whose path holds the chat id "
                 "and whose name without its extension appears in the row's BinNet blob, and file "
                 "rows to a file under Documents/Files whose folder hash and name both appear in "
                 "the blob; these matches are made by the module and are not a link the store "
                 "records. Where several files match, a media row keeps the first match that is "
                 "not a JPEG, or the first match when all are, and a file row keeps the last "
                 "match. On voice note and link rows "
                 "whose MsgContent is empty, and on media rows with an empty MsgContent, no "
                 "LocalPath and no matched file, Message holds the last web address found in the "
                 "row's BinNet blob. On sticker rows whose MsgContent holds the two sticker "
                 "identifiers, Message is a string the module builds from them, and on location "
                 "rows with an empty MsgContent it is a geo string built from the coordinates in "
                 "the blob.",
        "paths": (  
            '*/mobile/Containers/Data/Application/*/Documents/chat_dbs/*/*',
            '*/mobile/Containers/Data/Application/*/Documents/profile.sqlite*',
            '*/mobile/Containers/Data/Application/*/Documents/chatgroup.sqlite*',
            '*/mobile/Containers/Data/Application/*/Documents/Files/*/*',
            '*/mobile/Containers/Data/Application/*/Documents/Sticker/Snapshot/*/*/*',
            '*/mobile/Containers/Data/Application/*/Documents/[0-9]*[0-9]/[0-9]*[0-9]/*/*.*',
            '*/mobile/Containers/Data/Application/*/tmp/[0-9]*[0-9]/[0-9]*[0-9]/*/*.*'
        ),
        "output_types": "all",
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
        "artifact_icon": "message"
    },
    "zalo_users": {
        "name": "Zalo - Stored Profile Entries",
        "description": "Stored ProfileEntity rows from the selected profile.sqlite, with mobile values joined from BuddyEntity and optional globalid values from GlobalIdEntity.",
        "author": "C_Peter, @AlexisBrignoni, Codex",
        "creatin_date": "2026-06-01",
        "creation_date": "2026-06-01",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Zalo",
        "notes": "Profile inclusion and relationship to a device user are not established. Rows are stored "
                 "profile/join observations, not verified contacts or known relationships. LEFT JOINs "
                 "retain missing joined values and may return multiple rows per profile when matching "
                 "join records repeat. Only the selected profile.sqlite is read; no app ownership or "
                 "interaction is inferred from a profile entry.",
        "paths": (  
            '*/mobile/Containers/Data/Application/*/Documents/profile.sqlite*'
        ),
        "output_types": "standard",
        "artifact_icon": "users"
    }
}

import os
import re
import json
from io import BytesIO
from pathlib import Path
from PIL import Image

from scripts.ilapfuncs import artifact_processor, \
    convert_unix_ts_to_utc, get_sqlite_db_records, does_column_exist_in_db, \
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
def zalo_users(context):
    """Extracts known Zalo Users"""
    files_found = context.get_files_found()
    data_list = []
    source_path = get_file_path(files_found, 'profile.sqlite')

    rawid = does_column_exist_in_db(source_path, 'GlobalIdEntity', 'rawid')

    if rawid:
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
    else:
        user_query = '''
            SELECT
                pe.userid,
                pe.displayname,
                be.mobile
            FROM
                ProfileEntity pe
            LEFT JOIN BuddyEntity be
                ON pe.userid=be.zaloid
            '''

    user_records = get_sqlite_db_records(source_path, user_query)
    for record in user_records:
        uid = record["userid"]
        uname = record["displayname"]
        umobile = record["mobile"]
        if rawid:
            uglobal = record["globalid"]
        else:
            uglobal = None

        data_list.append([uid, uname, umobile, uglobal])

    data_headers = ("User-ID", "Username", ('Phone Number', 'phonenumber'), "Global-ID")

    return data_headers, data_list, source_path


@artifact_processor
def zalo_messages(context):
    """Extracts Zalo Chats and Groupchats"""
    files_found = context.get_files_found()
    data_list = []
    all_files = files_found
    chat_dbs = [x for x in all_files if "chat_dbs" in x and x.endswith('.db') and "_ext" not in x]
    chat_dbs = sorted(set(chat_dbs))
    file_pattern = re.compile(r"^.*?/Documents/Files/(?P<hash>[a-fA-F0-9]{32})/(?P<filename>[^/]+)$")
    container_cache = {}
    media_cache = {}

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

    source_dirs = set()

    def _container(uuid):
        """Files and name lookups of one app container, read once."""
        if uuid not in container_cache:
            container_files = [x for x in all_files if uuid in Path(x).parts]
            names = {}
            chat_info = get_file_path(container_files, 'profile.sqlite')
            if chat_info:
                for record in get_sqlite_db_records(chat_info, user_query):
                    names[record["userid"]] = record["displayname"]
            groups = {}
            group_info = get_file_path(container_files, 'chatgroup.sqlite')
            if group_info:
                for record in get_sqlite_db_records(group_info, group_query):
                    groups[record["groupid"]] = record["name"]
            attached = []
            for file in container_files:
                match = file_pattern.match(file.replace("\\", "/"))
                if match:
                    attached.append({
                        "path": file,
                        "hash": match.group("hash"),
                        "filename": match.group("filename"),
                    })
            container_cache[uuid] = (container_files, names, groups, attached)
        return container_cache[uuid]

    for db_file in chat_dbs:
        source_file = db_file
        source_dirs.add(os.path.dirname(db_file))
        # The account id and the app container are taken from this database's
        # own path, so a second account or container keeps its own values.
        db_path_parts = Path(db_file).parts
        user_id = db_path_parts[db_path_parts.index("chat_dbs") + 1]
        uuid = db_path_parts[db_path_parts.index("Documents") - 1]
        files_found, user_dict, group_dict, file_dicts = _container(uuid)
        if (uuid, user_id) not in media_cache:
            media_pattern = re.compile(rf"/(?:Documents|tmp)/{re.escape(user_id)}/\d+/")
            media_cache[(uuid, user_id)] = [
                x for x in files_found if media_pattern.search(x.replace("\\", "/"))]
        media_list = media_cache[(uuid, user_id)]
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
                if msg_blob is None:
                    blob_text = ""
                elif isinstance(msg_blob, bytes):
                    blob_text = msg_blob.decode("latin-1")
                else:
                    blob_text = msg_blob
                if type_call in blob_text:
                    print_type = "Call"
                elif type_missed in blob_text:
                    print_type = "Missed Call"
                elif type_groupcall in blob_text:
                    print_type = "Groupcall"
                elif type_link in blob_text:
                    print_type = "Link"
                elif type_user in blob_text:
                    print_type = "User"
                else:
                    print_type = "Unknown (12)"
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

            data_list.append([message_date, outgoing, sender_name, chat_name, message, attach_file, sender_id, msg_type, print_type, latitude, longitude, isgroup, context.get_relative_path(source_file)])

    data_headers = (('Timestamp', 'datetime'), "Outgoing", "Sender", "Chat Name", "Message", ('Attachment File', 'media'), "Sender-ID", "Type ID", "Message Type", "Latitude", "Longitude", "Group Chat", "Source File")

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
