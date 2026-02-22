# Kijiji Conversations
# Author:  Terry Chabot (Krypterry)
# Version: 1.0.0
# Kijiji iOS App Version Tested: v15.24.0 (2022-06)
# Requirements:  None
#
#   Description:
#   Obtains individual chat messages that were sent and received using the Kijiji application.

import json
import datetime

from scripts.ilapfuncs import artifact_processor

LOCAL_USER = 'Local User'
UNIX_EPOCH = 978307200


@artifact_processor
def get_kijijiConversations(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    file_found = str(files_found[0])

    for file_found in files_found:
        file_found = str(file_found)
        with open(file_found, mode='r', encoding="UTF-8") as json_content:
            data = json.load(json_content)

            for conversation in data['data']:
                counterPartyName = conversation['counterParty']['name']
                counterPartyId = conversation['counterParty']['identifier']
                conversationId = conversation['conversationId']
                advertTitle = conversation['ad']['displayTitle']
                advertId = conversation['ad']['identifier']
                messages = conversation['messages']
                AppendMessageRowsToDataList(data_list,
                    conversationId,
                    advertId,
                    advertTitle,
                    counterPartyId,
                    counterPartyName,
                    messages)

    data_headers = ('Timestamp (Local Time)', 'Conversation ID', 'Ad ID', 'Ad Title',
                    'Message ID', 'Sender ID', 'Sender Name', 'Recipient ID',
                    'Recipient Name', 'State', 'Message')
    return data_headers, data_list, file_found


# Appends a row for each message sent in a unique conversation thread.
def AppendMessageRowsToDataList(data_list,
    conversationId,
    advertId,
    advertTitle,
    conversationPartyId,
    conversationPartyName,
    messages):
    for message in messages:
        # Determine sender (local user or counter party)
        if message['sender'] == 0:
            senderId = ''
            senderName = LOCAL_USER
            recipientId = conversationPartyId
            recipientName = conversationPartyName
        else:
            senderId = conversationPartyId
            senderName = conversationPartyName
            recipientId = ''
            recipientName = LOCAL_USER

        messageTimestamp = (datetime.datetime.fromtimestamp(int(message['sentDate']) + UNIX_EPOCH).strftime('%Y-%m-%d %H:%M:%S'))

        data_list.append((messageTimestamp,
            conversationId,
            advertId,
            advertTitle,
            message['messageId'],
            senderId, senderName,
            recipientId,
            recipientName,
            message['messageStatus'],
            message['text']))

__artifacts_v2__ = {
    "get_kijijiConversations": {
        "name": "Kijiji Conversations",
        "description": "Chat messages sent and received using the Kijiji application.",
        "author": "Terry Chabot (Krypterry)",
        "version": "1.0.0",
        "date": "2022-06-01",
        "requirements": "none",
        "category": "Kijiji",
        "notes": "",
        "paths": ('*/Library/Caches/conversation_cache',),
        "output_types": "standard",
        "artifact_icon": "message-square"
    }
}
