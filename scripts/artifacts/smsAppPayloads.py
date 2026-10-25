__artifacts_v2__ = {
    "smsLinkPreviews": {
        "name": "SMS & iMessage - Link Previews",
        "description": "Link preview metadata stored with a message (message.payload_data of a "
                       "rich link balloon in sms.db): the URL, original URL, title, summary and site name.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "SMS & iMessage",
        "notes": "One row per message whose payload_data is an NSKeyedArchiver archive holding rich link "
                 "metadata, under the key richLinkMetadata or metadata. In the tested databases these "
                 "rows have the balloon_bundle_id com.apple.messages.URLBalloonProvider, and some have "
                 "no balloon_bundle_id. URL, Original URL, Title, Summary, Site Name and Item Type are "
                 "the strings stored in the metadata, as stored: the title and summary come from the "
                 "linked page and were stored by Messages, they are not text typed by a person. "
                 "Original URL is the address before any redirect the page followed, as stored. "
                 "Image and Video say whether the metadata holds an image or video entry; the files "
                 "themselves are not reported here (the message's attachments may hold the preview image; this artifact does not match them). Placeholder is richLinkIsPlaceholder as stored. Message Text is "
                 "message.text, or the text decoded from attributedBody where text is empty. A "
                 "preview exists only when Messages built one, so a link sent without a preview "
                 "has no row here but appears in the SMS artifact. Whether the message was sent or "
                 "received is From Me, as stored. This artifact does not establish that the link was "
                 "opened. Observed on 9 databases from full-filesystem extractions (iOS 18.1.1 "
                 "and iOS 26.2.1 to 26.6.2): 5,413 link previews."
                 " On single databases of the nine Chat Name was empty on every row (no named group chat), Video was empty on every row, Placeholder (as stored) held one value (False) on every row, Destination Caller ID held one value on every row (one iMessage line), and Original URL and Message Text were identical on every row (the message body is the link). The artifact ran without error on the 22 of 32 corpus iOS images that hold an sms.db (iOS 12.4 to 26.5.2); the other 10 had no sms.db. sample_data lists six of the 22, iOS 14.3 to 26.5.2.",
        "paths": ('*/Library/SMS/sms.db*',),
        "output_types": "standard",
        "artifact_icon": "link",
        "sample_data": {
            "hickman_ios14": "iOS 14.3 | 2 rows",
            "hickman_ios15": "iOS 15.3.1 | 3 rows",
            "abe_ios16": "iOS 16.5 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 9 rows",
            "dexter_ios18": "iOS 18.3.2 | 4 rows",
            "hc_ios26": "iOS 26.5.2 | 8 rows",
        },
    },
    "smsAppMessages": {
        "name": "SMS & iMessage - iMessage App Messages",
        "description": "Messages sent by an iMessage app extension (balloon_bundle_id and payload_data in "
                       "sms.db), with the layout fields the app stored.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "SMS & iMessage",
        "notes": "One row per message that has a balloon_bundle_id other than the link preview balloon "
                 "and a payload_data value. App Bundle is balloon_bundle_id as stored: for an app "
                 "extension it has the form com.apple.messages.MSMessageExtensionBalloonPlugin:"
                 "<team id>:<extension bundle id>. App Name (an), Summary Text (ldtext), "
                 "Layout Class, Caption, Subcaption, "
                 "Image Title, Image Subtitle, Accessibility Label, Session Identifier and URL are the "
                 "values stored in the NSKeyedArchiver payload under those keys (the userInfo keys "
                 "are caption, subcaption, image-title and image-subtitle; the userInfo keys "
                 "secondary-subcaption and tertiary-subcaption held no value on any of the 447 rows "
                 "and are not reported), shown as stored; what each key means to an app is defined by the "
                 "app, so a value is what the extension stored for display and is not verified against "
                 "the app. The URL is the app's own URL for the message and can hold the app's data; "
                 "it is reported in full. Payload Format says Keyed archive when the payload decoded "
                 "and Not decoded otherwise (for example the Handwriting payload is not a property "
                 "list archive, and Digital Touch and similar payloads are not decoded here). "
                 "Other keys (for example ai, liveLayoutInfo, data, requiredCapabilities, appid) are not reported. The payloads of Apple "
                 "Cash, Photos, Find My, Business Chat and third-party apps share this layout in the "
                 "tested databases; the artifact does not interpret a payment, photo or location. A "
                 "message with a rich-link payload is in 'SMS & iMessage - Link Previews'. Messages "
                 "from RCS chatbots (balloon_bundle_id com.apple.messages.chatbot) carry no "
                 "payload_data in the tested databases and are not reported. Service and Destination Caller ID are the message row's values as stored and are "
                 "uniform on a device that used one service and one line. Observed on 7 of 9 databases from full-filesystem extractions "
                 "(iOS 18.1.1 and iOS 26.2.1 to 26.6.2): 447 app messages."
                 " On single databases of the nine Chat Name was empty on every row (no named group chat), Image Title, Image Subtitle, Accessibility Label and Session Identifier were empty on every row, Layout Class, Payload Format, App Bundle and App Name held one value on every row, and From Me, Sender, Chat Contact ID, Chat ID and Message Text held one value on every row (a few messages from one correspondent, the text being the object replacement character), with Sender and Chat Contact ID identical. The artifact ran without error on the 22 of 32 corpus iOS images that hold an sms.db (iOS 12.4 to 26.5.2); the other 10 had no sms.db. sample_data lists six of the 22, iOS 14.3 to 26.5.2.",
        "paths": ('*/Library/SMS/sms.db*',),
        "output_types": "standard",
        "artifact_icon": "apps",
        "sample_data": {
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
}

from urllib.parse import urljoin

from scripts.ilapfuncs import artifact_processor, get_file_path, open_sqlite_db_readonly
from scripts.sms_deep import time_first, cocoa_to_utc, keyed_archive, message_columns, message_text

LINK_BALLOON = 'com.apple.messages.URLBalloonProvider'

MESSAGE_SELECT = '''
    SELECT m.date, m.is_from_me, CASE WHEN m.is_from_me = 0 THEN h.id END, c.chat_identifier,
           c.display_name, m.text, m.attributedBody, m.balloon_bundle_id, m.payload_data,
           m.service, m.destination_caller_id, cmj.chat_id, m.ROWID, m.guid
    FROM message m
    LEFT JOIN handle h ON h.ROWID = m.handle_id
    LEFT JOIN chat_message_join cmj ON cmj.message_id = m.ROWID
    LEFT JOIN chat c ON c.ROWID = cmj.chat_id
    WHERE m.payload_data IS NOT NULL
    ORDER BY m.date, m.ROWID
'''


def url_text(value):
    """An archived NSURL ({NS.base, NS.relative}) or string as text."""
    if isinstance(value, dict):
        relative = value.get('NS.relative')
        base = value.get('NS.base')
        if isinstance(relative, str) and isinstance(base, str):
            return urljoin(base, relative)
        return relative if isinstance(relative, str) else ''
    return value if isinstance(value, str) else ''


def text_value(value):
    return value if isinstance(value, str) else ''


def payload_rows(source_path):
    db = open_sqlite_db_readonly(source_path)
    if db is None:
        return []
    try:
        columns = message_columns(db)
        if not {'payload_data', 'balloon_bundle_id'} <= columns:
            return []
        return db.execute(MESSAGE_SELECT).fetchall()
    finally:
        db.close()


def link_metadata(payload):
    """The rich link metadata dict of a payload, or None when it holds none."""
    if not isinstance(payload, dict):
        return None
    for key in ('richLinkMetadata', 'metadata'):
        if isinstance(payload.get(key), dict):
            return payload[key]
    return None


@artifact_processor
def smsLinkPreviews(context):
    """ see artifact description """
    source_path = get_file_path(context.get_files_found(), "sms.db")
    data_headers = (
        ('Message Timestamp', 'datetime'), 'From Me', 'Sender', 'Chat Contact ID', 'Chat Name',
        'URL', 'Original URL', 'Title', 'Summary', 'Site Name', 'Item Type (as stored)', 'Image',
        'Video', 'Placeholder (as stored)', 'Message Text', 'Service', 'Destination Caller ID',
        'Chat ID', 'Message Row ID', 'Message GUID')
    data_list = []
    for (date, from_me, sender, chat_identifier, chat_name, text, body, balloon, payload_blob,
         service, caller_id, chat_id, rowid, guid) in payload_rows(source_path):
        if balloon not in (None, LINK_BALLOON):
            continue
        payload = keyed_archive(payload_blob)
        meta = link_metadata(payload)
        if meta is None:
            continue
        has_image = any(meta.get(k) for k in ('image', 'images', 'imageMetadata', 'icon', 'icons'))
        has_video = any(meta.get(k) for k in ('video', 'videoMetadata'))
        placeholder = payload.get('richLinkIsPlaceholder')
        data_list.append((
            cocoa_to_utc(date), from_me, sender or '', chat_identifier or '', chat_name or '',
            url_text(meta.get('URL')), url_text(meta.get('originalURL')),
            text_value(meta.get('title')), text_value(meta.get('summary')),
            text_value(meta.get('siteName')), text_value(meta.get('itemType')),
            'Yes' if has_image else '', 'Yes' if has_video else '',
            '' if placeholder is None else str(placeholder), message_text(text, body) or '',
            service or '', caller_id or '', chat_id, rowid, guid))
    return time_first(data_headers, data_list) + (source_path,)


@artifact_processor
def smsAppMessages(context):
    """ see artifact description """
    source_path = get_file_path(context.get_files_found(), "sms.db")
    data_headers = (
        ('Message Timestamp', 'datetime'), 'From Me', 'Sender', 'Chat Contact ID', 'Chat Name',
        'App Bundle', 'App Name', 'Summary Text', 'Layout Class', 'Caption', 'Subcaption',
        'Image Title', 'Image Subtitle',
        'Accessibility Label', 'Session Identifier', 'URL', 'Payload Format', 'Message Text',
        'Service', 'Destination Caller ID', 'Chat ID', 'Message Row ID', 'Message GUID')
    data_list = []
    for (date, from_me, sender, chat_identifier, chat_name, text, body, balloon, payload_blob,
         service, caller_id, chat_id, rowid, guid) in payload_rows(source_path):
        if not balloon or balloon == LINK_BALLOON:
            continue
        payload = keyed_archive(payload_blob)
        if isinstance(payload, dict) and link_metadata(payload) is not None:
            continue
        if isinstance(payload, dict) and payload:
            info = payload.get('userInfo') if isinstance(payload.get('userInfo'), dict) else {}
            values = (
                text_value(payload.get('an')), text_value(payload.get('ldtext')),
                text_value(payload.get('layoutClass')), text_value(info.get('caption')),
                text_value(info.get('subcaption')), text_value(info.get('image-title')),
                text_value(info.get('image-subtitle')), text_value(payload.get('AccessibilityLabel')),
                text_value(payload.get('sessionIdentifier')), url_text(payload.get('URL')),
                'Keyed archive')
        else:
            values = ('',) * 10 + ('Not decoded',)
        data_list.append((
            cocoa_to_utc(date), from_me, sender or '', chat_identifier or '', chat_name or '',
            balloon) + values + (message_text(text, body) or '', service or '', caller_id or '',
                                 chat_id, rowid, guid))
    return time_first(data_headers, data_list) + (source_path,)
