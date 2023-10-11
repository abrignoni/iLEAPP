# Kijiji Conversations
# Author:  Terry Chabot (Krypterry)
# Version: 1.0.0
# Kijiji iOS App Version Tested: v15.24.0 (2022-06)
# Requirements:  None
#
#   Description:
#   Obtains individual chat messages that were sent and received using the Kijiji application.
#
#   Additional Info:
#       Kijiji.ca is a Canadian online classified advertising website and part of eBay Classifieds Group, with over 16 million unique visitors per month.
#
#       Kijiji, May 2022 <https://help.kijiji.ca/helpdesk/basics/what-is-kijiji>
#       Wikipedia - The Free Encyclopedia, May 2022, <https://en.wikipedia.org/wiki/Kijiji>
import json
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv

LOCAL_USER = 'Local User'
UNIX_EPOCH = 978307200

def get_kijijiConversations(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list_conversation = []
    for file_found in files_found:
        file_found = str(file_found)
        logfunc(f'JSON file {file_found} is being deserialized...')
        with open(file_found, mode='r', encoding="UTF-8") as json_content:
            data_list_conversation = []
            data = json.load(json_content)

            for conversation in data['data']:
                counterPartyName = conversation['counterParty']['name']
                counterPartyId = conversation['counterParty']['identifier']
                conversationId = conversation['conversationId']
                advertTitle = conversation['ad']['displayTitle']
                advertId = conversation['ad']['identifier']
                messages = conversation['messages']
                #advertThumbnailUrl = conversation['ad']['thumbnailUrl']
                AppendMessageRowsToDataList(data_list_conversation,
                    conversationId,
                    advertId,
                    advertTitle,
                    counterPartyId,
                    counterPartyName,
                    messages)

            if len(data_list_conversation) > 0:
                report = ArtifactHtmlReport('Kijiji Conversations')
                report.start_artifact_report(report_folder, 'Kijiji Conversations')
                report.add_script()
                data_headers = ('Timestamp (Local Time)', 'Conversation ID', 'Ad ID', 'Ad Title', 'Message ID', 'Sender ID', 'Sender Name', 'Recipient ID', 'Recipient Name', 'State', 'Message')
                report.write_artifact_data_table(data_headers, data_list_conversation, file_found)
                report.end_artifact_report()
                
                tsvname = 'Kijiji Conversations'
                tsv(report_folder, data_headers, data_list_conversation, tsvname)                
            else:
                logfunc('No Kijiji Conversations data found.')

            return True

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

__artifacts__ = {
    "kijijiConversations": (
        "Kijiji Conversations",
        ('*/Library/Caches/conversation_cache'),
        get_kijijiConversations)
}