__artifacts_v2__ = {
    "session": {
        "name": "Session Chats",
        "description": "Parses Session chats",
        "author": "@snoop168",
        "creation_date": "2025-06-18",
        "last_update_date": "2025-06-18",
        "requirements": "none",
        "category": "Session",
        "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/database/Session.sqlite*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/*-thumbnails/thumbnail-*.jpg'),
        "output_types": "standard",  # or ["html", "tsv", "timeline", "lava"]
        "artifact_icon": "message-square",
        "data_views": {
            "chat": {
                "threadDiscriminatorColumn": "Thread ID",
                "threadLabelColumn": "Thread ID",
                "textColumn": "Message",
                "directionColumn": "Message Sent",
                "directionSentValue": 1,
                "timeColumn": "Message Timestamp",
                "senderColumn": "Author",
                "sentMessageLabelColumn": "Author",
                "mediaColumn": "Attachments"
            }
        }
    }
}

import inspect
from scripts.ilapfuncs import convert_unix_ts_to_timezone, iOS
from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_cipher_db_records, logfunc, check_in_media

@artifact_processor
def session(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "Session.sqlite")
    data_list = []

    kc = iOS.get_keychain()
    for item in kc['genp']:
        if item.get('acct') == b'GRDBDatabaseCipherKeySpec':
            key = str(item['v_Data'].hex())
            query = '''
            SELECT
                interaction.timestampMs,
                interaction.body,
                interaction.authorId, 
                interaction.variant,
                interaction.wasRead,
                interaction.threadId,
                interaction.id,
                profile.name,
                GROUP_CONCAT(interactionAttachment.attachmentId) AS attachmentIds
            FROM interaction
            LEFT JOIN profile ON interaction.authorId = profile.id
            LEFT JOIN interactionAttachment ON interactionAttachment.interactionId = interaction.id
            GROUP BY interaction.id
            '''

            data_headers = (('Message Timestamp', 'datetime'), 'Message', 'Author ID', 'Message Sent',
                            'Message Read', 'Thread ID', 'Message ID', 'Author', ('Attachments', 'media'))

            db_records = get_sqlite_cipher_db_records(source_path, query, key, 32)

            for record in db_records:
                artifact_info = inspect.stack()[0]
                message_timestamp = convert_unix_ts_to_timezone(record[0], timezone_offset)
                media_items = None
                if record[8]:
                    media_items = []
                    for attach in record[8].split(','):
                        media_items.append(check_in_media(
                            artifact_info,
                            report_folder,
                            seeker,
                            files_found,
                            f'{attach}-thumbnails/thumbnail-450.jpg',
                            name=attach
                        ))
                if media_items:
                    data_list.append(
                        (message_timestamp, record[1], record[2], record[3], record[4], record[5], record[6], record[7],
                         media_items[0]))
                else:
                    data_list.append(
                        (message_timestamp, record[1], record[2], record[3], record[4], record[5], record[6], record[7],
                         None))

    return data_headers, data_list, source_path
