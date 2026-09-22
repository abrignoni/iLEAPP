"""Odnoklassniki (OK) iOS app.

The app (bundle id ru.ok.iphone, internal prefix "ru.ok.tt") keeps its chat data
in a YapDatabase built on SQLite: a single table "database2" whose rows are
(collection, key, data BLOB, metadata BLOB). Each object's "data" blob is a
MessagePack-encoded map, not a custom format, so it is decoded here with a small
self-contained MessagePack reader rather than adding a dependency (iLEAPP already
ships one such hand-rolled reader in KeepSafe.py for the same reason).

Collections used:
  * messages           - one object per message
  * chats              - one object per chat (group chat or one-to-one dialog)
  * contacts           - one object per contact (user id, name parts, flags)
  * contacts_last_seen - a scalar Unix-seconds value keyed by contact user id

Timestamps: message and chat times are Unix milliseconds; the contacts_last_seen
value is a Unix-seconds float. Direction is taken from each message's "my" flag
(true for a message the account sent). Sender is the message "sender" user id and
is resolved to a contact name when that user id is a known contact. A chat's label
is the recorded group title, or for a one-to-one dialog the other participant's
contact name when that participant is a known contact.

The sticker, animoji and other catalogue collections in the same store, and the
separate onelogV2 telemetry database, are app-supplied catalogues/telemetry and
are not reported. Attachment media files are summarised by type only and are not
rendered.

Field mapping was done against a private sample; no sample data is recorded for it.
"""

import os
import sqlite3
import struct

from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    logfunc,
    open_sqlite_db_readonly,
)


__artifacts_v2__ = {
    "odnoklassniki_messages": {
        "name": "Odnoklassniki - Messages",
        "description": (
            "Messages from the Odnoklassniki (OK) iOS app's YapDatabase store, decoded "
            "from the MessagePack objects in the messages collection, with direction, "
            "sender and chat resolved where the store records the link."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-22",
        "last_update_date": "2026-09-22",
        "requirements": "none",
        "category": "Odnoklassniki",
        "notes": (
            "Source is the app's YapDatabase (Library/Application Support/ru.ok.tt/"
            "database_N.db/app.db), a SQLite database whose 'database2' table stores each "
            "object as a MessagePack-encoded blob; the blobs are decoded by a small "
            "self-contained MessagePack reader in this module. One row per object in the "
            "messages collection. Direction is taken from the message 'my' flag (Sent when "
            "true, Received otherwise). Message Timestamp is a Unix-milliseconds value from "
            "the object's 'time' field. Sender is the object's 'sender' user id, shown "
            "resolved to a contact name where that user id is a known contact and as the "
            "stored id otherwise. Chat is the group chat title, or for a one-to-one dialog "
            "the other participant's contact name where that participant is a known contact. "
            "Attachments are summarised by their recorded type (as stored, e.g. PHOTO, CALL, "
            "AUDIO, VIDEO) and count; the attachment media files are not rendered. Reactions "
            "are summarised from the recorded reaction counters. Message Type is reported as "
            "stored. This module does not render attachment media, does not decode the "
            "sticker/animoji catalogue collections, and does not parse the separate onelogV2 "
            "telemetry database. Field mapping was done against a private sample; no sample "
            "data is recorded for it."
        ),
        "paths": ("*/Library/Application Support/ru.ok.tt/*/app.db*",),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Chat ID",
                "conversationLabelColumn": "Chat",
                "timeColumn": "Message Timestamp",
                "directionColumn": "Direction",
                "directionSentValue": "Sent",
                "senderColumn": "Sender",
                "textColumn": "Message",
            }
        },
    },
    "odnoklassniki_chats": {
        "name": "Odnoklassniki - Chats",
        "description": (
            "Chats (group chats and one-to-one dialogs) from the Odnoklassniki (OK) iOS "
            "app's YapDatabase store, decoded from the MessagePack objects in the chats "
            "collection."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-22",
        "last_update_date": "2026-09-22",
        "requirements": "none",
        "category": "Odnoklassniki",
        "notes": (
            "One row per object in the chats collection of the app's YapDatabase "
            "(database2 table, MessagePack blobs). Last Activity is the recorded "
            "lastMessageTimestamp (Unix milliseconds), falling back to lastEventTime; "
            "Created is the recorded creation time (Unix milliseconds) and is blank when "
            "the stored value is a sentinel rather than a real time. Chat Type is reported "
            "as stored (e.g. GROUP_CHAT, DIALOG). Title is the recorded group title, or for "
            "a one-to-one dialog the other participant's contact name where that participant "
            "is a known contact. Participant IDs are the recorded participant user ids. "
            "Field mapping was done against a private sample; no sample data is recorded for it."
        ),
        "paths": ("*/Library/Application Support/ru.ok.tt/*/app.db*",),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "odnoklassniki_contacts": {
        "name": "Odnoklassniki - Contacts",
        "description": (
            "Contacts from the Odnoklassniki (OK) iOS app's YapDatabase store, decoded from "
            "the MessagePack objects in the contacts collection, with last-seen time joined "
            "from the contacts_last_seen collection by user id."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-22",
        "last_update_date": "2026-09-22",
        "requirements": "none",
        "category": "Odnoklassniki",
        "notes": (
            "One row per object in the contacts collection of the app's YapDatabase "
            "(database2 table, MessagePack blobs). Name is the recorded name parts joined "
            "with a space. Is Me marks the object whose recorded 'isMe' flag is set (the "
            "account owner). Last Seen is joined from the contacts_last_seen collection, "
            "whose value is a Unix-seconds time keyed by the contact user id. Last Updated "
            "is the recorded updateTime (Unix milliseconds) and is blank when the stored "
            "value is a sentinel. Contact Type and Gender are reported as stored integer "
            "codes. Field mapping was done against a private sample; no sample data is "
            "recorded for it."
        ),
        "paths": ("*/Library/Application Support/ru.ok.tt/*/app.db*",),
        "output_types": "standard",
        "artifact_icon": "address-book",
    },
}


# ---------------------------------------------------------------------------
# Minimal MessagePack decoder (nil/bool/int/float/str/bin/array/map; ext is
# consumed and returned as None because no reported field is an ext type).
# ---------------------------------------------------------------------------

class _OkMsgpackError(ValueError):
    pass


def _mp_decode(data):
    """Decode a single top-level MessagePack value from bytes."""
    pos = 0
    length = len(data)

    def read(count):
        nonlocal pos
        if pos + count > length:
            raise _OkMsgpackError(f"truncated msgpack data at offset {pos}")
        chunk = data[pos:pos + count]
        pos += count
        return chunk

    def unpack_value():
        nonlocal pos
        tag = read(1)[0]
        if tag <= 0x7F:
            return tag
        if tag >= 0xE0:
            return tag - 0x100
        if 0x80 <= tag <= 0x8F:
            return unpack_map(tag & 0x0F)
        if 0x90 <= tag <= 0x9F:
            return unpack_array(tag & 0x0F)
        if 0xA0 <= tag <= 0xBF:
            return read(tag & 0x1F).decode("utf-8", "replace")
        if tag == 0xC0:
            return None
        if tag == 0xC2:
            return False
        if tag == 0xC3:
            return True
        if tag == 0xC4:
            return read(read(1)[0])
        if tag == 0xC5:
            return read(struct.unpack(">H", read(2))[0])
        if tag == 0xC6:
            return read(struct.unpack(">I", read(4))[0])
        if tag == 0xC7:
            ext_len = read(1)[0]
            read(1)
            read(ext_len)
            return None
        if tag == 0xC8:
            ext_len = struct.unpack(">H", read(2))[0]
            read(1)
            read(ext_len)
            return None
        if tag == 0xC9:
            ext_len = struct.unpack(">I", read(4))[0]
            read(1)
            read(ext_len)
            return None
        if tag == 0xCA:
            return struct.unpack(">f", read(4))[0]
        if tag == 0xCB:
            return struct.unpack(">d", read(8))[0]
        if tag == 0xCC:
            return read(1)[0]
        if tag == 0xCD:
            return struct.unpack(">H", read(2))[0]
        if tag == 0xCE:
            return struct.unpack(">I", read(4))[0]
        if tag == 0xCF:
            return struct.unpack(">Q", read(8))[0]
        if tag == 0xD0:
            return struct.unpack(">b", read(1))[0]
        if tag == 0xD1:
            return struct.unpack(">h", read(2))[0]
        if tag == 0xD2:
            return struct.unpack(">i", read(4))[0]
        if tag == 0xD3:
            return struct.unpack(">q", read(8))[0]
        if tag in (0xD4, 0xD5, 0xD6, 0xD7, 0xD8):
            ext_len = 1 << (tag - 0xD4)
            read(1)
            read(ext_len)
            return None
        if tag == 0xD9:
            return read(read(1)[0]).decode("utf-8", "replace")
        if tag == 0xDA:
            return read(struct.unpack(">H", read(2))[0]).decode("utf-8", "replace")
        if tag == 0xDB:
            return read(struct.unpack(">I", read(4))[0]).decode("utf-8", "replace")
        if tag == 0xDC:
            return unpack_array(struct.unpack(">H", read(2))[0])
        if tag == 0xDD:
            return unpack_array(struct.unpack(">I", read(4))[0])
        if tag == 0xDE:
            return unpack_map(struct.unpack(">H", read(2))[0])
        if tag == 0xDF:
            return unpack_map(struct.unpack(">I", read(4))[0])
        raise _OkMsgpackError(f"unsupported msgpack tag 0x{tag:02x} at offset {pos - 1}")

    def unpack_array(count):
        return [unpack_value() for _ in range(count)]

    def unpack_map(count):
        result = {}
        for _ in range(count):
            key = unpack_value()
            result[key] = unpack_value()
        return result

    return unpack_value()


# ---------------------------------------------------------------------------
# Store access helpers.
# ---------------------------------------------------------------------------

def _find_db(files_found):
    """Return the app.db path from files_found (never a directory or -wal/-shm)."""
    for entry in files_found:
        path = str(entry)
        if os.path.isdir(path):
            continue
        if path.endswith("app.db"):
            return path
    return None


def _decode_collection(db, collection):
    """Yield (key, decoded_data) for each object in a collection. Rows whose blob
    cannot be decoded are logged and skipped."""
    try:
        cursor = db.execute(
            "SELECT key, data FROM database2 WHERE collection = ?", (collection,)
        )
        rows = cursor.fetchall()
    except sqlite3.Error as ex:
        # A store whose schema does not carry a database2 table (or the expected
        # columns) reads as "no rows here" rather than aborting the artifact.
        logfunc(f"Odnoklassniki: could not read collection {collection}: {ex}")
        return
    for key, data in rows:
        if not data:
            yield key, None
            continue
        try:
            yield key, _mp_decode(bytes(data))
        except _OkMsgpackError as ex:
            logfunc(f"Odnoklassniki: undecoded object in {collection}: {ex}")


def _ms_ts(value):
    """Convert a Unix-milliseconds value to UTC, blanking sentinels/absent values."""
    if isinstance(value, (int, float)) and value >= 1_000_000_000_000:
        return convert_unix_ts_to_utc(value)
    return ""


def _sec_ts(value):
    """Convert a Unix-seconds value to UTC, blanking sentinels/absent values."""
    if isinstance(value, (int, float)) and value >= 1_000_000_000:
        return convert_unix_ts_to_utc(value)
    return ""


def _contact_name(contact):
    """Join a contact object's recorded name parts."""
    parts = []
    names = contact.get("names") if isinstance(contact, dict) else None
    if isinstance(names, list):
        for part in names:
            if isinstance(part, dict):
                name = part.get("name")
                if isinstance(name, str) and name and name not in parts:
                    parts.append(name)
    return " ".join(parts)


def _load_indices(db):
    """Return (contacts_by_uid, my_uid, chats_by_key, last_seen_by_uid)."""
    contacts_by_uid = {}
    my_uid = None
    for _key, obj in _decode_collection(db, "contacts"):
        if not isinstance(obj, dict):
            continue
        uid = obj.get("id")
        if uid is None:
            continue
        contacts_by_uid[str(uid)] = obj
        if obj.get("isMe"):
            my_uid = str(uid)

    chats_by_key = {}
    for key, obj in _decode_collection(db, "chats"):
        if isinstance(obj, dict):
            chats_by_key[key] = obj

    last_seen_by_uid = {}
    for key, obj in _decode_collection(db, "contacts_last_seen"):
        if isinstance(obj, (int, float)):
            last_seen_by_uid[str(key)] = obj

    return contacts_by_uid, my_uid, chats_by_key, last_seen_by_uid


def _chat_title(chat, contacts_by_uid, my_uid):
    """Resolve a chat's display title: recorded group title, or for a one-to-one
    dialog the other participant's contact name when known."""
    for field in ("safeTitle", "title", "localTitle", "safeLocalTitle"):
        value = chat.get(field)
        if isinstance(value, str) and value:
            return value
    group_info = chat.get("groupChatInfo")
    if isinstance(group_info, dict):
        name = group_info.get("name")
        if isinstance(name, str) and name:
            return name
    participants = chat.get("participants")
    if isinstance(participants, dict) and my_uid:
        for uid in participants:
            if str(uid) != str(my_uid):
                contact = contacts_by_uid.get(str(uid))
                if contact:
                    name = _contact_name(contact)
                    if name:
                        return name
    return ""


def _attachments_summary(attaches):
    """Summarise attachments by their recorded type and count."""
    if not isinstance(attaches, list) or not attaches:
        return ""
    counts = {}
    for attach in attaches:
        if isinstance(attach, dict):
            atype = attach.get("_type") or "UNKNOWN"
            counts[atype] = counts.get(atype, 0) + 1
    return ", ".join(f"{atype} x{count}" for atype, count in sorted(counts.items()))


def _reactions_summary(reaction_info):
    """Summarise a message's recorded reaction counters."""
    if not isinstance(reaction_info, dict):
        return ""
    total = reaction_info.get("totalCount")
    if not total:
        return ""
    parts = []
    counters = reaction_info.get("counters")
    if isinstance(counters, list):
        for counter in counters:
            if isinstance(counter, dict):
                reaction = counter.get("reaction")
                count = counter.get("count")
                if reaction:
                    parts.append(f"{reaction} x{count}")
    return ", ".join(parts) if parts else f"{total} total"


# ---------------------------------------------------------------------------
# Artifacts.
# ---------------------------------------------------------------------------

@artifact_processor
def odnoklassniki_messages(context):
    files_found = [str(f) for f in context.get_files_found()]
    db_path = _find_db(files_found)
    data_list = []

    data_headers = (
        ("Message Timestamp", "datetime"),
        "Direction",
        "Sender",
        "Chat",
        "Message",
        "Sender ID (as stored)",
        "Chat ID",
        "Chat Type",
        "Message Type (as stored)",
        "Attachments",
        "Reactions",
        "Message ID (as stored)",
    )

    if not db_path:
        return data_headers, data_list, ""

    db = open_sqlite_db_readonly(db_path)
    if db is None:
        return data_headers, data_list, ""

    try:
        contacts_by_uid, my_uid, chats_by_key, _last_seen = _load_indices(db)

        for _key, msg in _decode_collection(db, "messages"):
            if not isinstance(msg, dict):
                continue

            timestamp = _ms_ts(msg.get("time"))
            direction = "Sent" if msg.get("my") else "Received"

            sender_id = msg.get("sender")
            sender_id_str = str(sender_id) if sender_id else ""
            sender_name = ""
            if sender_id is not None:
                contact = contacts_by_uid.get(str(sender_id))
                if contact:
                    sender_name = _contact_name(contact)
            if not sender_name:
                sender_name = sender_id_str

            chat_key = msg.get("chatPrimaryKey")
            chat = chats_by_key.get(chat_key)
            chat_title = _chat_title(chat, contacts_by_uid, my_uid) if isinstance(chat, dict) else ""
            chat_type = chat.get("type") if isinstance(chat, dict) else ""

            message_text = ""
            msg_text_obj = msg.get("messsageText")
            if isinstance(msg_text_obj, dict):
                text = msg_text_obj.get("text")
                if isinstance(text, str):
                    message_text = text

            message_id = msg.get("id")

            data_list.append((
                timestamp,
                direction,
                sender_name,
                chat_title,
                message_text,
                sender_id_str,
                chat_key if isinstance(chat_key, str) else "",
                chat_type if isinstance(chat_type, str) else "",
                msg.get("type") if isinstance(msg.get("type"), str) else "",
                _attachments_summary(msg.get("attaches")),
                _reactions_summary(msg.get("reactionInfo")),
                str(message_id) if message_id is not None else "",
            ))
    finally:
        db.close()

    return data_headers, data_list, db_path


@artifact_processor
def odnoklassniki_chats(context):
    files_found = [str(f) for f in context.get_files_found()]
    db_path = _find_db(files_found)
    data_list = []

    data_headers = (
        ("Last Activity", "datetime"),
        ("Created", "datetime"),
        "Chat ID",
        "Chat Type",
        "Title",
        "Participant Count",
        "Participant IDs",
        "Owner Is Me",
    )

    if not db_path:
        return data_headers, data_list, ""

    db = open_sqlite_db_readonly(db_path)
    if db is None:
        return data_headers, data_list, ""

    try:
        contacts_by_uid, my_uid, _chats, _last_seen = _load_indices(db)

        for key, chat in _decode_collection(db, "chats"):
            if not isinstance(chat, dict):
                continue

            last_activity = _ms_ts(chat.get("lastMessageTimestamp")) or _ms_ts(chat.get("lastEventTime"))
            created = _ms_ts(chat.get("created"))
            chat_type = chat.get("type") if isinstance(chat.get("type"), str) else ""
            title = _chat_title(chat, contacts_by_uid, my_uid)

            participants = chat.get("participants")
            if isinstance(participants, dict):
                participant_ids = ", ".join(sorted(str(uid) for uid in participants))
            else:
                participant_ids = ""
            participant_count = chat.get("participantsCount")

            data_list.append((
                last_activity,
                created,
                key if isinstance(key, str) else "",
                chat_type,
                title,
                participant_count if isinstance(participant_count, int) else "",
                participant_ids,
                "Yes" if chat.get("ownerIsMe") else "No",
            ))
    finally:
        db.close()

    return data_headers, data_list, db_path


@artifact_processor
def odnoklassniki_contacts(context):
    files_found = [str(f) for f in context.get_files_found()]
    db_path = _find_db(files_found)
    data_list = []

    data_headers = (
        ("Last Seen", "datetime"),
        ("Last Updated", "datetime"),
        "User ID",
        "Name",
        "Is Me",
        "Contact Type (as stored)",
        "Gender (as stored)",
        "Profile URL",
    )

    if not db_path:
        return data_headers, data_list, ""

    db = open_sqlite_db_readonly(db_path)
    if db is None:
        return data_headers, data_list, ""

    try:
        contacts_by_uid, _my_uid, _chats, last_seen_by_uid = _load_indices(db)

        for uid, contact in contacts_by_uid.items():
            profile_url = contact.get("profileUrl")
            contact_type = contact.get("contactType")
            gender = contact.get("gender")

            data_list.append((
                _sec_ts(last_seen_by_uid.get(uid)),
                _ms_ts(contact.get("updateTime")),
                uid,
                _contact_name(contact),
                "Yes" if contact.get("isMe") else "No",
                contact_type if isinstance(contact_type, int) else "",
                gender if isinstance(gender, int) else "",
                profile_url if isinstance(profile_url, str) else "",
            ))
    finally:
        db.close()

    return data_headers, data_list, db_path
