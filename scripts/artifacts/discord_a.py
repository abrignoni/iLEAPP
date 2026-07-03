__artifacts_v2__ = {
    "DiscordChatsA": {  # This should match the function name exactly
        "name": "Discord Chats (KV Storage)",
        "description": "Parses Discord chats from \"a\" database",
        "author": "@stark4n6",
        "creation_date": "2025-03-31",
        "last_update_date": "2026-07-03",
        "requirements": "none",
        "category": "Discord",
        "notes": "Direction is derived by comparing the message sender id to the "
                 "account id in the kv-storage/@account.<id>/ path.",
        "paths": ('*/Library/Caches/kv-storage/@account*/a*'),
        "output_types": "standard",  # or ["html", "tsv", "timeline", "lava"]
        "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Channel ID",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Message Timestamp",
                "senderColumn": "Sender Username"
            }
        },
    }
}

import os
import re
import json

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records

_ACCOUNT_ID_RE = re.compile(r'@account\.(\d+)')


@artifact_processor
def DiscordChatsA(context):
    data_list = []
    source_paths = []

    query = '''select data from messages0'''

    data_headers = (('Message Timestamp', 'datetime'), ('Edited Timestamp', 'datetime'),
                    'Sender Username', 'Sender Global Name', 'Sender ID', 'Message',
                    'Attachment(s)', 'Message Type', 'Call Ended', 'Message ID', 'Channel ID',
                    'Account ID', 'Direction',)

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.basename(file_found) != 'a':
            continue
        source_paths.append(context.get_relative_path(file_found))

        # local account id is part of the kv-storage path
        account_match = _ACCOUNT_ID_RE.search(file_found)
        account_id = account_match.group(1) if account_match else ''

        db_records = get_sqlite_db_records(file_found, query)

        for record in db_records:
            message_ts = edited_ts = auth_username = global_username = ''
            attach_name = message_type = call_end = sender_id = message = ''
            blob_id = channel_id = ''
            blob_data = record[0]
            if len(blob_data) <= 1:
                continue
            try:
                json_load = json.loads(blob_data[1:])
            except (json.JSONDecodeError, TypeError, ValueError, UnicodeDecodeError):
                continue

            blob_id = json_load.get('id', '')
            channel_id = json_load.get('channelId', '')

            if 'message' in json_load:
                message_ts = str(json_load['message'].get('timestamp', '')).replace('T', ' ')
                edited_ts = str(json_load['message'].get('edited_timestamp', '')).replace('T', ' ')
                if edited_ts == 'None':
                    edited_ts = ''
                if json_load['message'].get('type', '') == 0:
                    message_type = 'Message'
                elif json_load['message'].get('type', '') == 3:
                    message_type = 'Call'
                    call_end = str(json_load['message']['call'].get('ended_timestamp', '')).replace('T', ' ')
                elif json_load['message'].get('type', '') == 7:
                    message_type = 'User Joined'
                elif json_load['message'].get('type', '') == 19:
                    message_type = 'Reply'
                else:
                    message_type = json_load['message'].get('type', '')
                message = json_load['message'].get('content', '')

                if 'author' in json_load['message']:
                    auth_username = json_load['message']['author'].get('username', '')
                    global_username = json_load['message']['author'].get('globalName', '')
                    sender_id = json_load['message']['author'].get('id', '')

                if 'attachments' in json_load['message'] and len(json_load['message']['attachments']) > 0:
                    attachment_list = []
                    for x in json_load['message']['attachments']:
                        attachment_name = x.get('filename', '')
                        attachment_url = x.get('url', '')

                        attachment_list.append(f"{attachment_name} ({attachment_url})")

                    attach_name = "<br>".join(attachment_list)

            if account_id and sender_id:
                direction = 'Outgoing' if str(sender_id) == account_id else 'Incoming'
            else:
                direction = ''

            data_list.append((message_ts, edited_ts, auth_username, global_username, sender_id,
                              message, attach_name, message_type, call_end, blob_id, channel_id,
                              account_id, direction))

    return data_headers, data_list, '\n'.join(source_paths)
