__artifacts_v2__ = {
    "session": {
        "name": "Session Chats",
        "description": "Parses Session chats",
        "author": "@snoop168",
        "creation_date": "2025-06-18",
        "last_update_date": "2025-06-18",
        "requirements": "none",
        "category": "Session",
        "notes": "Place the GK Keychain in the same folder as the input file, or make sure the UFED keychain is in the Zip file",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/database/Session.sqlite*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/*-thumbnails/thumbnail-*.jpg',
                  '*/mobile/Containers/Shared/AppGroup/*/Attachments/*'),
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

    if not source_path:
        logfunc("Session.sqlite file not found")
        return None, None, None

    kc = iOS.get_keychain()
    found_key = False
    for item in kc.get('genp'):
        if item.get('acct') == b'GRDBDatabaseCipherKeySpec':
            key = str(item['v_Data'].hex())
            found_key = True
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
                interactionAttachment.attachmentId,
                attachment.contentType,
                attachment.sourceFilename
            FROM interaction
            LEFT JOIN profile ON interaction.authorId = profile.id
            LEFT JOIN interactionAttachment ON interactionAttachment.interactionId = interaction.id
            LEFT JOIN attachment on attachment.id = interactionAttachment.attachmentId
            '''

            data_headers = (('Message Timestamp', 'datetime'), 'Message', 'Author ID', 'Message Sent',
                            'Message Read', 'Thread ID', 'Message ID', 'Author', ('Attachments', 'media'))

            db_records = get_sqlite_cipher_db_records(source_path, query, key, 32)

            for record in db_records:
                artifact_info = inspect.stack()[0]
                message_timestamp = convert_unix_ts_to_timezone(record[0], timezone_offset)
                media_items = None
                attach = record[8]
                media_id = None
                if attach:
                    if record[10]:
                        #Find the media using the sourceFilename [10]
                        media_id = check_in_media(
                            artifact_info,
                            report_folder,
                            seeker,
                            files_found,
                            f'{attach}/{record[10]}',
                            name=attach
                        )
                    #if we havent found the media_id yet via the above method
                    if not media_id:
                        #first try to find the actual attachment
                        media_id = check_in_media(
                            artifact_info,
                            report_folder,
                            seeker,
                            files_found,
                            f'{attach}.mp4', #Be smarter here, we can figure out the actual ext testing for now
                            name=attach
                        )
                        if not media_id:
                            #Still didnt find it, so now lets fall back to the thumbnail
                            for resolution in [1334, 450, 200]:
                                media_id = check_in_media(
                                    artifact_info,
                                    report_folder,
                                    seeker,
                                    files_found,
                                    f'{attach}-thumbnails/thumbnail-{resolution}.jpg',
                                    name=attach
                                )
                                if media_id:
                                    break

                data_list.append(
                    (message_timestamp, record[1], record[2], record[3], record[4], record[5], record[6], record[7],
                     media_id))
    if not found_key:
        logfunc("Session Key wasn't found. Place the GK keychain file in the same folder as the input file or make sure the UFED keychain is located in the Zip file.")
    return data_headers, data_list, source_path
