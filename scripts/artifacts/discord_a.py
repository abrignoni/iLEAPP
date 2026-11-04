__artifacts_v2__ = {
    "DiscordChatsA": {  # This should match the function name exactly
        "name": "Discord Chats (KV Storage)",
        "description": "Parses Discord chats from \"a\" database, including messages another state in its "
                       "write-ahead log holds and the current state does not",
        "author": "@stark4n6",
        "creation_date": "2025-03-31",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Discord",
        "notes": "Direction reads Outgoing when the message sender id equals the "
                 "account id in the kv-storage/@account.<id>/ path and Incoming when "
                 "it differs; it is blank when the path gives no account id or the "
                 "record has no sender id. Message Type shows Message, Call, User "
                 "Joined and Reply for type values 0, 3, 7 and 19, following the "
                 "message type table in the Discord Developer Documentation; any other "
                 "type value is shown as stored. Reference for the four type values: "
                 "Discord Developer Documentation, 'Message Resource', "
                 "https://docs.discord.com/developers/resources/message. "
                 "Conversation, Server Name, Server ID, Channel Name and DM Recipients come from "
                 "the channel and server records cached in the kv_cache0 table of the same "
                 "database, matched on Channel ID. For a server channel, Conversation is the "
                 "server name (or the server id when no server record is cached) and #channel name; for a channel with no guild_id it is the "
                 "channel name, or 'DM:' and the recipients from the record's rawRecipients "
                 "(username and user id). When rawRecipients is absent the ids in recipients are used. The DM label is given to any cached channel with no guild_id and no name; the channel type is not checked. In tested samples every such channel had type 1, which the Discord Developer Documentation lists as a direct message between users (https://docs.discord.com/developers/resources/channel). When the channel is not cached those columns are "
                 "blank and Conversation shows the Channel ID (not exercised on the tested images; every channel was cached). In tested samples every row "
                 "resolved: 76 of 76 on dexter_ios18 in server channels, 25 of 50 on "
                 "iphone11_ios17 in a server channel and 25 in a channel with no guild_id, and "
                 "all 8 on hc_ios18_7 and all 4 on iphone12_ios18 in a channel with no guild_id. "
                 "Channel Name was blank on every row in a channel with no guild_id. "
                 "Record Origin. Live rows come from a normal read of messages0. Recovered rows do not: their key, columns a to f of messages0, is held by another state in the database's write-ahead log and absent from the current one. messages0 declares no primary key; the unique index messages0_by_key on a to f is what makes a row one message, so a row whose key the current state still holds is not reported, whatever its older versions held. Recovery Method and Recovery Location are filled in only on Recovered rows. Why a Recovered row is absent is not established here. States are read by scripts/sqlite_wal.py: each earlier committed state of the log's current generation (state n is the database after the first n committed transactions, and state 0 the database file without its log), the previous generation's left-over frames where its checks pass, and frames after the last commit. A Recovered row is reported once, as the newest committed state holding its key stored it, else the previous generation's newest left-over commit, else the frames after the last commit. Recovery Location names the committed states the key was read in, with their first and last numbers, and the previous log generation with the first and last numbers of its left-over commits; for a key read only after the last commit it names the log's frames after the last commit. Recovery Method is WAL committed states, or WAL uncommitted frames for a key read only after the last commit. The previous-generation and uncommitted-frame paths were not exercised on these images or by the unit test. "
                 "On falken_ios26 one Recovered row was returned, read in committed states 0 to 3. "
                 "On dexter_ios18, hc_ios18_7, hc_ios26 and iphone11_ios17 no Recovered row was "
                 "returned, so Record Origin held Live on every row and Recovery Method and Recovery "
                 "Location were empty on every row; on dexter_ios18 none of the previous "
                 "generation's 15 commits could be read. iphone12_ios18 had an empty (0-byte) log "
                 "beside the database, which the reader treats as no log.",
        "paths": ('*/Library/Caches/kv-storage/@account*/a*'),
        "output_types": "standard",  # or ["html", "tsv", "timeline", "lava"]
        "artifact_icon": "message-circle",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | Discord - Talk, Play, Hang Out 298.0 | 76 rows",
            "falken_ios26": "iOS 26.2.1 | 34 rows (1 Recovered)",
            "hc_ios26": "iOS 26.5.2 | 8 rows",
            "hc_ios18_7": "iOS 18.7.8 | Discord - Talk, Play, Hang Out 324.0 | 8 rows",
            "iphone11_ios17": "iOS 17.3 | Discord - Talk, Play, Hang Out 238.0 | 50 rows",
            "iphone12_ios18": "iOS 18.7 | Discord - Talk, Play, Hang Out 306.1 | 4 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Channel ID",
                "conversationLabelColumn": "Conversation",
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

from scripts.artifacts.discordServers import (ORIGIN_LIVE, ORIGIN_RECOVERED, discord_channel_context,
                                              discord_kv_lookup, discord_removed_messages)
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records

_ACCOUNT_ID_RE = re.compile(r'@account\.(\d+)')


@artifact_processor
def DiscordChatsA(context):
    data_list = []
    source_paths = []

    query = '''select data from messages0'''

    data_headers = (
        ('Message Timestamp', 'datetime'),
        ('Edited Timestamp', 'datetime'),
        'Direction',
        'Sender Username',
        'Conversation',
        'Message',
        'Record Origin',
        'Sender Global Name',
        'Sender ID',
        'Attachment(s)',
        'Message Type',
        'Call Ended',
        'Message ID',
        'Channel ID',
        'Server Name',
        'Server ID',
        'Channel Name',
        'DM Recipients',
        'Account ID',
        'Recovery Method',
        'Recovery Location',
    )

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.basename(file_found) != 'a':
            continue
        source_paths.append(context.get_relative_path(file_found))

        # local account id is part of the kv-storage path
        account_match = _ACCOUNT_ID_RE.search(file_found)
        account_id = account_match.group(1) if account_match else ''
        lookup = discord_kv_lookup([file_found])

        db_records = [(record[0], ORIGIN_LIVE, '', '')
                      for record in get_sqlite_db_records(file_found, query)]
        db_records.extend((blob, ORIGIN_RECOVERED, method, location)
                          for blob, method, location in discord_removed_messages(file_found))

        for blob_data, origin, method, location in db_records:
            message_ts = edited_ts = auth_username = global_username = ''
            attach_name = message_type = call_end = sender_id = message = ''
            blob_id = channel_id = ''
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

            conversation, server_name, server_id, channel_name, recipients = \
                discord_channel_context(channel_id, *lookup)
            data_list.append((
                message_ts,
                edited_ts,
                direction,
                auth_username,
                conversation,
                message,
                origin,
                global_username,
                sender_id,
                attach_name,
                message_type,
                call_end,
                blob_id,
                channel_id,
                server_name,
                server_id,
                channel_name,
                recipients,
                account_id,
                method,
                location,
            ))

    return data_headers, data_list, '\n'.join(source_paths)
