"""Proton Mail iOS 'Inbox' local cache.

Proton Mail 7.x for iOS (the 'Inbox' rewrite, app version 7.9.2 in the tested
image) keeps a local SQLite cache under the group.me.proton.mail app group,
separate from the older ch.protonmail.protonmail / ProtonMail.sqlite store that
scripts/artifacts/protonMail.py parses. In the tested image the message
subjects, bodies, sender and recipient addresses, contacts and account details
sit in this cache in clear text, and attachments are written to disk decrypted,
so no keychain or PGP key is needed to read them.

Two databases are read, dispatched by the tables they carry:
  - support/account.db          -> core_accounts / users -> account artifact
  - support/<base64 id>.db      -> messages, contacts, attachments, labels

Timestamps are Unix seconds. Folder names come from the app's own labels table
(label_type 4), resolved per database. Address columns hold JSON, decoded here to
'Name <address>' strings.
"""
__artifacts_v2__ = {
    "protonMailInboxMessages": {
        "name": "Proton Mail - Inbox Messages",
        "description": "Messages cached by the Proton Mail iOS Inbox app, including decrypted subject, body, sender and recipients",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "Proton Mail",
        "notes": "Reads the group.me.proton.mail cache used by Proton Mail 7.x (Inbox). In the tested "
                 "image the cached subject, body, sender and recipient values are stored in clear "
                 "text; the body is the HTML the app rendered. Folder is resolved from the app's own "
                 "labels table. From Me is derived by comparing the message sender to the account's "
                 "own addresses. The Attachment column shows the first cached attachment file for the "
                 "message when it is present in the extraction; the Inbox Attachments artifact lists "
                 "every attachment. A cached row reflects what the app had synced and decrypted "
                 "locally, not necessarily the full mailbox.",
        "paths": ('*/Shared/AppGroup/*/support/*.db*',
                  '*/Shared/AppGroup/*/cache/mail-cache/attachments/*'),
        "output_types": "standard",
        "artifact_icon": "mail",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation ID",
                "conversationLabelColumn": "Conversation Subject",
                "textColumn": "Body",
                "senderColumn": "From",
                "directionColumn": "From Me",
                "directionSentValue": "Yes",
                "timeColumn": "Time",
                "mediaColumn": "Attachment"
            }
        },
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | Proton Mail 7.9.2 | 2 rows",
            "hc_ios26": "iOS 26.5.2 | Proton Mail 7.x (installed, no mail cache) | 0 rows",
        }
    },
    "protonMailInboxAttachments": {
        "name": "Proton Mail - Inbox Attachments",
        "description": "Attachments cached on disk by the Proton Mail iOS Inbox app",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "Proton Mail",
        "notes": "Attachment metadata from the Inbox cache joined to the files the app wrote under "
                 "cache/mail-cache/attachments/. In the tested image those files are decrypted "
                 "images. The media column shows a file only when it is present in the extraction.",
        "paths": ('*/Shared/AppGroup/*/support/*.db*',
                  '*/Shared/AppGroup/*/cache/mail-cache/attachments/*'),
        "output_types": "standard",
        "artifact_icon": "paperclip",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | Proton Mail 7.9.2 | 4 rows",
        }
    },
    "protonMailInboxContacts": {
        "name": "Proton Mail - Inbox Contacts",
        "description": "Contact email addresses cached by the Proton Mail iOS Inbox app",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "Proton Mail",
        "notes": "Contact email rows from the Inbox cache. A proton-autosave uid marks a contact the "
                 "app created automatically from a sent or received message rather than one the user "
                 "saved.",
        "paths": ('*/Shared/AppGroup/*/support/*.db*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | Proton Mail 7.9.2 | 1 row",
        }
    },
    "protonMailInboxAccount": {
        "name": "Proton Mail - Inbox Account",
        "description": "Signed-in Proton account details cached by the Proton Mail iOS Inbox app",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "Proton Mail",
        "notes": "Account and user rows from support/account.db and the mail cache. Used and maximum "
                 "space are bytes as stored.",
        "paths": ('*/Shared/AppGroup/*/support/*.db*',),
        "output_types": "standard",
        "artifact_icon": "user-check",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | Proton Mail 7.9.2 | 2 rows (one from the mail cache users table, one from account.db core_accounts)",
        }
    }
}

import json
import re

from scripts.ilapfuncs import (artifact_processor, get_sqlite_db_records,
                               does_table_exist_in_db, convert_unix_ts_to_utc,
                               check_in_media)

_ATTACHMENT_ID_RE = re.compile(r'/mail-cache/attachments/(\d+)/')


def _is_mail_cache(file_found):
    return does_table_exist_in_db(file_found, 'messages') and \
        does_table_exist_in_db(file_found, 'labels')


def _first_address(raw):
    """The first address in a Proton address JSON value, lowercased, or ''."""
    if not raw:
        return ''
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return ''
    if isinstance(data, dict):
        data = [data]
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get('address'):
                return item['address'].lower()
    return ''


def _is_account_db(file_found):
    return does_table_exist_in_db(file_found, 'core_accounts')


def _format_addresses(raw):
    """Decode a Proton address JSON value to a 'Name <address>' string.

    Accepts a single object or a list of them. Anything that does not decode is
    returned unchanged so a format change surfaces rather than being dropped.
    """
    if not raw:
        return ''
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return str(raw)
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return str(raw)
    parts = []
    for item in data:
        if not isinstance(item, dict):
            continue
        address = item.get('address', '')
        name = item.get('name', '')
        parts.append(f'{name} <{address}>'.strip() if name else address)
    return '; '.join(p for p in parts if p)


def _labels_by_message(file_found):
    """message local_id -> sorted folder names, from labels + message_labels."""
    names = {row[0]: row[1] for row in
             get_sqlite_db_records(file_found, 'SELECT local_id, name FROM labels')}
    out = {}
    for message_id, label_id in get_sqlite_db_records(
            file_found, 'SELECT local_message_id, local_label_id FROM message_labels'):
        name = names.get(label_id)
        if name:
            out.setdefault(message_id, set()).add(name)
    return {mid: ', '.join(sorted(labels)) for mid, labels in out.items()}


@artifact_processor
def protonMailInboxMessages(context):
    data_headers = (
        ('Time', 'datetime'),
        'From Me',
        'From',
        'Conversation Subject',
        'Body',
        ('Attachment', 'media'),
        'Folder',
        'Conversation ID',
        'Subject',
        'To',
        'CC',
        'BCC',
        'Read',
        'Replied',
        'Forwarded',
        'Attachments',
        'Size',
        'Deleted',
        'Source File',
    )
    data_list = []
    sources = []

    query = '''
        SELECT m.local_id, m.time, m.subject, m.sender, m.to_list, m.cc_list, m.bcc_list,
               b.body, m.unread, m.is_replied, m.is_forwarded, m.num_attachments, m.size,
               m.deleted, m.remote_conversation_id, c.subject
        FROM messages m
        LEFT JOIN message_body b ON b.message_id = m.local_id
        LEFT JOIN conversations c ON c.local_id = m.local_conversation_id
    '''

    # attachment files matched by the id embedded in their cache path
    found_by_id = {}
    for file_found in context.get_files_found():
        file_found = str(file_found)
        match = _ATTACHMENT_ID_RE.search(file_found.replace('\\', '/'))
        if match:
            found_by_id[int(match.group(1))] = file_found

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('.db') or not _is_mail_cache(file_found):
            continue
        rel_path = context.get_relative_path(file_found)
        folders = _labels_by_message(file_found)

        owner_addresses = {row[0].lower() for row in
                           get_sqlite_db_records(file_found, 'SELECT email FROM addresses')
                           if row[0]}

        # first cached attachment file per message, for inline display
        first_attachment = {}
        if does_table_exist_in_db(file_found, 'attachments'):
            for att_id, message_id, filename in get_sqlite_db_records(
                    file_found,
                    'SELECT local_id, local_message_id, filename FROM attachments ORDER BY local_id'):
                if message_id not in first_attachment and att_id in found_by_id:
                    first_attachment[message_id] = (found_by_id[att_id], filename)

        rows_seen = False
        for row in get_sqlite_db_records(file_found, query):
            sender_address = _first_address(row[3])
            from_me = 'Yes' if sender_address and sender_address in owner_addresses else 'No'
            media_ref = ''
            attachment = first_attachment.get(row[0])
            if attachment:
                media_ref = check_in_media(attachment[0], attachment[1]) or ''
            data_list.append((
                convert_unix_ts_to_utc(row[1]),
                from_me,
                _format_addresses(row[3]),
                row[15],
                row[7],
                media_ref,
                folders.get(row[0], ''),
                row[14],
                row[2],
                _format_addresses(row[4]),
                _format_addresses(row[5]),
                _format_addresses(row[6]),
                'No' if row[8] else 'Yes',
                'Yes' if row[9] else 'No',
                'Yes' if row[10] else 'No',
                row[11],
                row[12],
                'Yes' if row[13] else 'No',
                rel_path,
            ))
            rows_seen = True
        if rows_seen:
            sources.append(rel_path)

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))


@artifact_processor
def protonMailInboxAttachments(context):
    data_headers = (
        'Filename',
        ('Attachment', 'media'),
        'Size',
        'MIME Type',
        'Cached Path',
        'Remote Message ID',
        'Source File')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('.db') or not _is_mail_cache(file_found):
            continue
        if not does_table_exist_in_db(file_found, 'attachments'):
            continue
        rel_path = context.get_relative_path(file_found)

        cache_paths = {}
        if does_table_exist_in_db(file_found, 'attachment_cache'):
            cache_paths = {row[0]: row[1] for row in get_sqlite_db_records(
                file_found, 'SELECT attachment_id, path FROM attachment_cache')}

        rows_seen = False
        for row in get_sqlite_db_records(
                file_found,
                'SELECT local_id, filename, size, mime_type, remote_message_id FROM attachments'):
            local_id, filename, size, mime_type, remote_message_id = row
            cached_path = cache_paths.get(local_id, '')
            media_ref = ''
            if cached_path:
                media_ref = check_in_media(cached_path, filename) or ''
            data_list.append((filename, media_ref, size, mime_type, cached_path,
                              remote_message_id, rel_path))
            rows_seen = True
        if rows_seen:
            sources.append(rel_path)

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))


@artifact_processor
def protonMailInboxContacts(context):
    data_headers = (
        'Name',
        'Email',
        ('Last Used', 'datetime'),
        'Is Proton',
        'Contact UID',
        'Source File')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('.db') or not _is_mail_cache(file_found):
            continue
        if not does_table_exist_in_db(file_found, 'contact_emails'):
            continue
        rel_path = context.get_relative_path(file_found)

        uids = {}
        if does_table_exist_in_db(file_found, 'contacts'):
            uids = {row[0]: row[1] for row in get_sqlite_db_records(
                file_found, 'SELECT local_id, uid FROM contacts')}

        rows_seen = False
        for row in get_sqlite_db_records(
                file_found,
                'SELECT name, email, last_used_time, is_proton, local_contact_id FROM contact_emails'):
            name, email, last_used, is_proton, local_contact_id = row
            data_list.append((name, email, convert_unix_ts_to_utc(last_used),
                              'Yes' if is_proton else 'No',
                              uids.get(local_contact_id, ''), rel_path))
            rows_seen = True
        if rows_seen:
            sources.append(rel_path)

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))


@artifact_processor
def protonMailInboxAccount(context):
    data_headers = (
        'Username',
        'Display Name',
        'Email',
        ('Create Time', 'datetime'),
        'Used Space',
        'Max Space',
        'Ready',
        'Source File')
    data_list = []
    sources = []

    # users table (mail cache) carries the richer record; account.db core_accounts
    # carries the login state. Read whichever the file has.
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('.db'):
            continue
        rel_path = context.get_relative_path(file_found)

        if _is_mail_cache(file_found) and does_table_exist_in_db(file_found, 'users'):
            for row in get_sqlite_db_records(
                    file_found,
                    'SELECT name, display_name, email, create_time, used_space, max_space FROM users'):
                name, display_name, email, create_time, used_space, max_space = row
                data_list.append((name, display_name, email,
                                  convert_unix_ts_to_utc(create_time),
                                  used_space, max_space, '', rel_path))
            if data_list:
                sources.append(rel_path)
        elif _is_account_db(file_found):
            for row in get_sqlite_db_records(
                    file_found,
                    'SELECT username, name_or_addr, is_ready FROM core_accounts'):
                username, name_or_addr, is_ready = row
                data_list.append((username, '', name_or_addr, '', '', '',
                                  'Yes' if is_ready else 'No', rel_path))
            if data_list:
                sources.append(rel_path)

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
