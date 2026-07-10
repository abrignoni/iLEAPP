__artifacts_v2__ = {
    "discordChats": {
        "name": "Discord - Chats",
        "description": "Parses Discord chat messages from fsCachedData and the local KV storage database",
        "author": "Original Unknown, John Hyla & @stark4n6",
        "creation_date": "",
        "last_update_date": "2026-06-18",
        "requirements": "none",
        "category": "Discord",
        "notes": "",
        "paths": (
            "*/activation_record.plist",
            "*/com.hammerandchisel.discord/fsCachedData/*",
            "*/Library/Caches/kv-storage/@account*/a*",
            "*/Library/Caches/com.hackemist.SDImageCache/default/*",
        ),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Channel ID",
                "conversationLabelColumn": "Channel ID",
                "textColumn": "Content",
                "directionColumn": "Direction",
                "directionSentValue": "Sent",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender",
                "mediaColumn": "Attachment",
            }
        },
        "sample_data": {
            "josh_ios_15": "204 rows from fsCachedData and KV storage; 30 attachment rows; 11 cached media matches",
            "ctf2020_ios12": "iOS 12.4 | com.disney.MyDisneyExperience, com.nordstrom.shopping, com.plainvanillacorp.quizup | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 127 rows",
            "felix_ios17": "iOS 17.6.1 | AppLock - photo lock 1.2.6 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 22 rows",
            "iphone11_ios17": "iOS 17.3 | 334 rows",
            "iphone12_ios18": "iOS 18.7 | Discord - Talk, Play, Hang Out 306.1 | 4 rows",
            "iphone14plus_ios18": "iOS 18.0 | Depop - Buy & Sell Clothes 2.375 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | Life360: Find Friends & Family 24.31.0 | 0 rows",
        },
    }
}

import hashlib
import json
import math
import re
from datetime import datetime
from os.path import basename, isfile, normcase, normpath

import biplist

from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    get_resolution_for_model_id,
    get_sqlite_db_records,
    logfunc,
)


MESSAGE_TYPES = {
    0: "Message",
    3: "Call",
    7: "User Joined",
    19: "Reply",
}


def _discord_timestamp(timestamp):
    if not timestamp or timestamp == "None":
        return ""
    try:
        return datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
    except ValueError:
        return str(timestamp).replace("T", " ")


def _reduced_size(width, height, max_width, max_height):
    if width > height:
        if width <= max_width:
            return width, height
        ratio = width / max_width
        return max_width, math.ceil(height / ratio)

    if height <= max_height:
        return width, height

    ratio = height / max_height
    return math.ceil(width / ratio), max_height


def _source_type(file_path):
    if "fsCachedData" in file_path:
        return "fsCachedData"
    if basename(file_path) == "a":
        return "KV Storage"
    return ""


def _source_path(context, file_path):
    return context.get_relative_path(file_path)


def _application_container(path):
    parts = normpath(path).replace("/", "\\").split("\\")
    if "Application" not in parts:
        return ""
    app_index = len(parts) - 1 - parts[::-1].index("Application")
    if app_index + 1 >= len(parts):
        return ""
    return normcase("\\".join(parts[:app_index + 2]))


def _account_id_from_path(path):
    match = re.search(r"[/\\]@account\.([^/\\]+)", path)
    return match.group(1) if match else ""


def _account_ids_by_container(files_found):
    account_ids = {}
    for file_found in files_found:
        file_found = str(file_found)
        account_id = _account_id_from_path(file_found)
        if account_id:
            account_ids[_application_container(file_found)] = account_id
    return account_ids


def _account_id_for_file(file_path, account_ids):
    return account_ids.get(_application_container(file_path), "")


def _direction(author_id, account_id):
    if account_id and str(author_id) == str(account_id):
        return "Sent"
    return "Received"


def _message_type(message_type):
    if message_type in MESSAGE_TYPES:
        return MESSAGE_TYPES[message_type]
    return message_type if message_type is not None else ""


def _activation_resolution(files_found):
    for file_found in files_found:
        if not str(file_found).endswith("activation_record.plist"):
            continue

        plist = biplist.readPlist(str(file_found))
        account_token = plist["AccountToken"].decode("utf-8")
        matches = re.findall(r'"(.*?)" = "(.*?)";', account_token, re.DOTALL)
        model_id = {key: value for key, value in matches}.get("ProductType")
        if not model_id:
            logfunc("Cannot detect model ID. Cannot link Discord attachments")
            return None

        return get_resolution_for_model_id(model_id)

    logfunc("activation_record.plist not found. Unable to determine model/resolution for attachment linking")
    return None


def _attachment_extension(proxy_url):
    match = re.search(r"attachments.+(\.[^?=]{1,4})\??", proxy_url)
    return match.group(1) if match else ""


def _resized_proxy_url(proxy_url, width, height, resolution):
    if not width or not height or not resolution:
        return proxy_url

    new_width, new_height = _reduced_size(width, height, resolution["Width"], int(resolution["Height"] / 2))
    if new_height == height and new_width == width:
        if _attachment_extension(proxy_url) == ".gif":
            return proxy_url
        return f"{proxy_url}="

    if proxy_url.endswith("&"):
        return f"{proxy_url}=&width={new_width}&height={new_height}"
    return f"{proxy_url}?width={new_width}&height={new_height}"


def _attachment_rows(message, files_found, resolution):
    attachments = message.get("attachments") or []
    attachment_rows = []

    for attachment in attachments:
        filename = attachment.get("filename", "")
        proxy_url = attachment.get("proxy_url") or attachment.get("url", "")
        if not proxy_url:
            attachment_rows.append((None, filename, ""))
            continue
        if not resolution:
            attachment_rows.append((None, filename, proxy_url))
            continue

        width = attachment.get("width")
        height = attachment.get("height")
        resized_url = _resized_proxy_url(proxy_url, width, height, resolution)
        extension = _attachment_extension(proxy_url)
        cached_filename = hashlib.md5(resized_url.encode("utf-8")).hexdigest() + extension

        if any(cached_filename in str(file_found) for file_found in files_found):
            attachment_rows.append((check_in_media(cached_filename), filename, cached_filename))
        else:
            attachment_rows.append((None, filename, f"{proxy_url} ({cached_filename})"))

    return attachment_rows or [(None, "", "")]


def _embed_values(message):
    embed_author = author_url = author_icon_url = embedded_url = embedded_description = ""
    footer_text = footer_icon_url = ""

    for embed in message.get("embeds") or []:
        embedded_url = embed.get("url", "")
        embedded_description = embed.get("description", "")

        author = embed.get("author") or {}
        embed_author = author.get("name", "")
        author_url = author.get("url", "")
        author_icon_url = author.get("icon_url", "")

        footer = embed.get("footer") or {}
        footer_text = footer.get("text", "")
        footer_icon_url = footer.get("icon_url", "")

    return embed_author, author_url, author_icon_url, embedded_url, embedded_description, footer_text, footer_icon_url


def _message_rows(message, files_found, resolution, source_type, source_file, context, account_id):
    timestamp = _discord_timestamp(message.get("timestamp"))
    if not timestamp:
        return []

    author = message.get("author") or {}
    sender = author.get("global_name") or author.get("globalName") or author.get("display_name")
    sender = sender or author.get("username", "")
    author_id = author.get("id", "")
    edited_timestamp = _discord_timestamp(message.get("edited_timestamp"))
    call_ended = _discord_timestamp((message.get("call") or {}).get("ended_timestamp"))
    embed_values = _embed_values(message)

    rows = []
    for media_ref, attachment_filename, attachment_link in _attachment_rows(message, files_found, resolution):
        rows.append((
            timestamp,
            edited_timestamp,
            author.get("username", ""),
            author.get("global_name") or author.get("globalName") or author.get("display_name") or "",
            sender,
            author.get("bot", ""),
            message.get("content", ""),
            media_ref,
            attachment_filename,
            attachment_link,
            author_id,
            account_id,
            _direction(author_id, account_id),
            message.get("channel_id", ""),
            _message_type(message.get("type")),
            call_ended,
            message.get("id", ""),
            *embed_values,
            source_type,
            _source_path(context, source_file),
        ))

    return rows


def _fs_cache_messages(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if "fsCachedData" not in file_found or not isfile(file_found):
            continue

        try:
            with open(file_found, "r", encoding="utf-8") as json_file:
                for line in json_file:
                    json_record = json.loads(line)
                    if isinstance(json_record, list):
                        for message in json_record:
                            yield file_found, message
                    elif isinstance(json_record, dict):
                        yield file_found, json_record
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as ex:
            logfunc(f"Skipping Discord cache file {file_found}: {ex}")


def _kv_storage_dbs(files_found):
    return [
        str(file_found)
        for file_found in files_found
        if basename(str(file_found)) == "a" and "kv-storage" in str(file_found)
    ]


def _kv_storage_messages(db_file):
    query = "SELECT data FROM messages0"
    for record in get_sqlite_db_records(db_file, query):
        blob_data = record[0]
        if len(blob_data) <= 1:
            continue

        try:
            json_load = json.loads(blob_data[1:])
        except (TypeError, UnicodeDecodeError, json.JSONDecodeError) as ex:
            logfunc(f"Skipping Discord KV storage record in {db_file}: {ex}")
            continue

        message = json_load.get("message")
        if message:
            yield db_file, message


@artifact_processor
def discordChats(context):
    files_found = context.get_files_found()
    resolution = _activation_resolution(files_found)
    if not resolution:
        logfunc("Cannot link Discord attachments due to missing resolution")

    account_ids = _account_ids_by_container(files_found)
    data_list = []
    for source_file, message in _fs_cache_messages(files_found):
        account_id = _account_id_for_file(source_file, account_ids)
        data_list.extend(
            _message_rows(
                message,
                files_found,
                resolution,
                _source_type(source_file),
                source_file,
                context,
                account_id,
            )
        )

    for db_file in _kv_storage_dbs(files_found):
        for source_file, message in _kv_storage_messages(db_file):
            account_id = _account_id_for_file(source_file, account_ids)
            data_list.extend(
                _message_rows(
                    message,
                    files_found,
                    resolution,
                    _source_type(source_file),
                    source_file,
                    context,
                    account_id,
                )
            )

    data_headers = (
        ("Timestamp", "datetime"),
        ("Edited Timestamp", "datetime"),
        "Username",
        "Global Name",
        "Sender",
        "Bot?",
        "Content",
        ("Attachment", "media"),
        "Attachment Filename",
        "Attachment Link",
        "User ID",
        "Account ID",
        "Direction",
        "Channel ID",
        "Message Type",
        ("Call Ended", "datetime"),
        "Message ID",
        "Embedded Author",
        "Author URL",
        "Author Icon URL",
        "Embedded URL",
        "Embedded Description",
        "Footer Text",
        "Footer Icon URL",
        "Source Type",
        "Source File",
    )

    return data_headers, data_list, "see Source File column"
