__artifacts_v2__ = {
    "kijijiConversations": {
        "name": "Kijiji Conversations",
        "description": "Chat messages sent and received using the Kijiji application",
        "author": "Terry Chabot (Krypterry)",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Kijiji Conversations",
        "notes": "Kijiji.ca is a Canadian online classified advertising site. Message timestamps are "
                 "Cocoa/Mac absolute time (seconds since 2001-01-01 UTC), converted to UTC.",
        "paths": ('*/Library/Caches/conversation_cache',),
        "output_types": "standard",
        "artifact_icon": "message-circle"
    }
}

import json

from scripts.ilapfuncs import artifact_processor, convert_cocoa_core_data_ts_to_utc, logfunc

_LOCAL_USER = 'Local User'


def _message_rows(conversation):
    """Yield one output row per message in a single Kijiji conversation thread."""
    counter_party_name = conversation['counterParty']['name']
    counter_party_id = conversation['counterParty']['identifier']
    conversation_id = conversation['conversationId']
    advert_title = conversation['ad']['displayTitle']
    advert_id = conversation['ad']['identifier']
    for message in conversation['messages']:
        if message['sender'] == 0:
            sender_id, sender_name = '', _LOCAL_USER
            recipient_id, recipient_name = counter_party_id, counter_party_name
        else:
            sender_id, sender_name = counter_party_id, counter_party_name
            recipient_id, recipient_name = '', _LOCAL_USER
        yield (convert_cocoa_core_data_ts_to_utc(int(message['sentDate'])), conversation_id,
               advert_id, advert_title, message['messageId'], sender_id, sender_name,
               recipient_id, recipient_name, message['messageStatus'], message['text'])


@artifact_processor
def kijijiConversations(context):
    data_headers = (('Timestamp', 'datetime'), 'Conversation ID', 'Ad ID', 'Ad Title', 'Message ID',
                    'Sender ID', 'Sender Name', 'Recipient ID', 'Recipient Name', 'State', 'Message')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        try:
            with open(file_found, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as ex:
            logfunc(f'Kijiji: could not parse {file_found}: {ex}')
            continue

        had_data = False
        for conversation in data.get('data', []):
            try:
                rows = list(_message_rows(conversation))
            except (KeyError, TypeError, ValueError) as ex:
                logfunc(f'Kijiji: skipping malformed conversation: {ex}')
                continue
            data_list.extend(rows)
            had_data = had_data or bool(rows)
        if had_data:
            sources.append(context.get_relative_path(file_found))

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
