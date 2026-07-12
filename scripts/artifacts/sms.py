__artifacts_v2__ = {
    "sms": {
        "name": "SMS",
        "description": "Parses SMS and iMessage chats",
        "author": "@AlexisBrignoni, @XperyLab, @ydkhatri, @tobraha, @snoop168",
        "creation_date": "2020-04-30",
        "last_update_date": "2026-07-10",
        "requirements": "none",
        "category": "SMS & iMessage",
        "notes": "",
        "paths": ('*/Library/SMS/sms.db*',
                  '*/Library/SMS/Attachments/*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 107 rows",
            "dexter_ios18": "iOS 18.3.2 | 300 rows",
            "fsfull002_ios17": "iOS 17.1 | 253 rows",
            "hc_ios18_7": "iOS 18.7.8 | 126 rows",
            "iphone11_ios17": "iOS 17.3 | 99 rows",
            "iphone12_ios18": "iOS 18.7 | 27 rows",
            "iphone14plus_ios18": "iOS 18.0 | 13 rows",
            "otto_ios17": "iOS 17.5.1 | 223 rows",
            "felix_ios17": "iOS 17.6.1 | 69 rows",
            "abe_ios16": "iOS 16.5 | 211 rows",
            "felix23_ios16": "iOS 16.5 | 57 rows",
            "hickman_ios13": "iOS 13.3.1 | 42 rows",
            "hickman_ios14": "iOS 14.3 | 106 rows",
            "jess_ios15": "iOS 15.0.2 | 13 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Chat ID",
                "conversationLabelColumn": "Chat Contact ID",
                "textColumn": "Message",
                "directionColumn": "From Me",
                "directionSentValue": 1,
                "timeColumn": "Message Timestamp",
                "senderColumn": "Chat Contact ID",
                "sentMessageLabelColumn": "Account",
                "mediaColumn": "Attachment File"
            }
        }
    }
}

import os

import pandas as pd

from scripts.artifact_report import ArtifactHtmlReport
from scripts.chat_rendering import render_chat, chat_HTML
from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, \
    convert_cocoa_core_data_ts_to_utc, check_in_media, lava_get_full_media_info, logfunc

import typedstream


def parse_typedstream(buffer):
    """Parse NSAttributedString from typedstream format.
    
    Args:
        buffer: The attributedBody buffer from the database (bytes)
        
    Returns:
        str or None: The parsed text string, or None if parsing fails
    """
    try:
        root = typedstream.unarchive_from_data(buffer)
    except (ValueError, TypeError, OSError):
        return None

    # Handle GenericArchivedObject with contents list (NSMutableAttributedString)
    if hasattr(root, 'contents') and root.contents:
        # First item typically contains the string value (NSMutableString)
        first_item = root.contents[0]
        if hasattr(first_item, 'value') and hasattr(first_item.value, 'value'):
            return first_item.value.value

    return None

@artifact_processor
def sms(context):
    """ see artifact description """
    source_path = get_file_path(context.get_files_found(), "sms.db")
    data_list = []

    query = '''
    select
    message.date,
    message.date_read,
    message.text as "Message",
    message.service as "Service",
    case
        when message.is_from_me = 0
        then 'Incoming'
        when message.is_from_me = 1
        then 'Outgoing'
    end as "Message Direction",
    case 
        when message.is_sent = 0
        then ''
        when message.is_sent = 1
        then 'Yes'
    end as "Message Sent",
    case
        when message.is_delivered = 0
        then ''
        when message.is_delivered = 1
        then 'Yes'
    end as "Message Delivered",
    case
        when message.is_read = 0
        then ''
        when message.is_read = 1
        then 'Yes'
    end as "Message Read",
    message.account as "Account",
    chat.account_login as "Account Login",
    chat.chat_identifier as "Chat Contact ID",
    attachment.transfer_name as "Attachment Name",
    attachment.filename as "Attachment Path",
    attachment.created_date,
    attachment.mime_type as "Attachment Mimetype",
    attachment.total_bytes as "Attachment Size",
    message.rowid as "Message Row ID",
    chat_message_join.chat_id as "Chat ID",
    message.is_from_me as "From Me",
    message.attributedBody
    from message
    left join message_attachment_join on message.ROWID = message_attachment_join.message_id
    left join attachment on message_attachment_join.attachment_id = attachment.ROWID
    left join chat_message_join on message.ROWID = chat_message_join.message_id
    left join chat on chat_message_join.chat_id = chat.ROWID 
    '''

    data_headers = (('Message Timestamp', 'datetime'), ('Read Timestamp', 'datetime'), 'Message',
                    'Service', 'Message Direction', 'Message Sent', 'Message Delivered', 'Message Read',
                    'Account', 'Account Login', 'Chat Contact ID',
                    'Attachment Name', ('Attachment File', 'media'), ('Attachment Timestamp', 'datetime'),
                    'Attachment Mimetype', 'Attachment Size (Bytes)', 'Message Row ID', 'Chat ID', 'From Me')

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        def fix_cocoa_date(ts):
            if not ts or ts == '': return ''
            if ts > 1000000000000000: # Nanoseconds
                ts = ts / 1000000000
            return convert_cocoa_core_data_ts_to_utc(ts)

        message_timestamp = fix_cocoa_date(record[0])
        read_timestamp = fix_cocoa_date(record[1])
        attachment_timestamp = fix_cocoa_date(record[13])
        
        # Use message.text if available, otherwise try to parse from attributedBody
        message_text = record[2]
        if not message_text and record[19]:
            message_text = parse_typedstream(record[19])

        attachment_path = record[12]
        media_ref_id = None
        if attachment_path:
            clean_path = '*' + attachment_path.replace('~', '', 1)
            # Some attachments are directories (e.g. bundle-style payloads);
            # check_in_media can only ingest regular files.
            extraction_path = context.get_source_file_path(clean_path)
            if extraction_path and os.path.isdir(extraction_path):
                logfunc(f'Skipped media check-in for "{record[11]}": attachment is a directory')
            else:
                media_ref_id = check_in_media(clean_path, record[11])

        data_list.append((message_timestamp, read_timestamp, message_text, record[3], record[4], record[5],
                          record[6], record[7], record[8], record[9], record[10], record[11], media_ref_id,
                          attachment_timestamp, record[14], record[15], record[16], record[17], record[18]))

    def copy_attachments(rec):
        media_ref_id = rec["Attachment File"]
        if media_ref_id:
            media_item = lava_get_full_media_info(media_ref_id)
            if media_item:
                return media_item['extraction_path']
        return None

    # The threaded chat view is only rendered when there are messages;
    # an empty DataFrame breaks the pandas apply in render_chat.
    if data_list:
        sms_df = pd.DataFrame(data_list,
                              columns=['data-time', 'Read Timestamp', 'message', 'Service', 'Message Direction',
                                       'Message Sent', 'Message Delivered', 'Message Read', 'Account', 'Account Login',
                                       'data-name', 'Attachment Name', 'Attachment File', 'Attachment Timestamp',
                                       'content-type', 'Attachment Size (Bytes)', 'message-id', 'Chat ID', 'from_me'])

        sms_df["file-path"] = sms_df.apply(copy_attachments, axis=1)

        report = ArtifactHtmlReport('SMS & iMessage - Messages (Threaded)')
        report.start_artifact_report(context.get_report_folder(), 'SMS & iMessage - Messages (Threaded)')
        report.add_script()
        report.write_lead_text(f'SMS & iMessage Messages (Threaded) located at: {source_path}')
        report.write_raw_html(chat_HTML)
        report.add_script(render_chat(sms_df))
        report.end_artifact_report()

    return data_headers, data_list, source_path
