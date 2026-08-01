__artifacts_v2__ = {
    "mailprotect": {
        "name": "Apple Email",
        "description": "Apple Mail messages from the Envelope Index and Protected Index databases (iOS 13+)",
        "author": "@abrignoni - @stark4n6",
        "creation_date": "2020-05-07",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Apple Mail",
        "notes": ("Supports iOS 13 and later. The recipients.type = 1 = To mapping was "
                  "established through testing; other type values are not decoded."),
        "paths": ('*/mobile/Library/Mail/* Index*',),
        "output_types": "standard",
        "artifact_icon": "mail",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 570 rows",
            "felix_ios17": "iOS 17.6.1 | 28 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 268 rows",
            "iphone11_ios17": "iOS 17.3 | 1231 rows",
            "iphone12_ios18": "iOS 18.7 | 64 rows",
            "iphone14plus_ios18": "iOS 18.0 | 62 rows",
            "otto_ios17": "iOS 17.5.1 | 916 rows",
            "abe_ios16": "iOS 16.5 | 572 rows",
            "felix23_ios16": "iOS 16.5 | 7 rows",
            "hickman_ios13": "iOS 13.3.1 | 176 rows",
            "hickman_ios14": "iOS 14.3 | 658 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 94 rows",
        }
    },
    "mailHeaders": {
        "name": "Apple Email - Message Headers",
        "description": "RFC 822 headers of Apple Mail messages, including CC and BCC, read from the .emlx files in MessageData",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Apple Mail",
        "notes": ("In the examined corpora no CC/BCC recipients appeared in the Envelope Index recipients table. "
                  "The CC/BCC columns are parsed per RFC 822 but no message in the available test "
                  "corpora carries either header, so those two columns are unexercised."),
        "paths": ('*/mobile/Library/Mail/MessageData/*/*.emlx',),
        "output_types": "standard",
        "artifact_icon": "mail-opened",
        "sample_data": {
            "josh_ios17_ffs": "iOS 17.3 | 2010 rows; From/To/Subject/Message-ID on all, 0 with CC or BCC",
        }
    }
}

import email
import email.header
import email.utils
import os
import re
import sqlite3

from scripts.ilapfuncs import (artifact_processor, attach_sqlite_db_readonly,
                               get_sqlite_db_records, logfunc,
                               convert_unix_ts_to_utc)

# Recipient rows are typed; only To recipients (type 1) are decoded here.
# In the examined corpora no CC/BCC recipients appeared in this table; they
# live in the .emlx headers instead — see the mailHeaders artifact.
_RECIPIENT_TYPE_TO = 1

# LEFT JOINs throughout on purpose. Joining subjects/addresses/summaries with
# inner joins silently drops every message that has no summary row, which on a
# real mailbox is the majority of them.
_QUERY = f'''
SELECT
    datetime(main.messages.date_sent, 'UNIXEPOCH'),
    datetime(main.messages.date_received, 'UNIXEPOCH'),
    PI.addresses.address,
    PI.addresses.comment,
    (SELECT GROUP_CONCAT(ra.address, ', ')
       FROM main.recipients r
       JOIN PI.addresses ra ON ra.ROWID = r.address
      WHERE r.message = main.messages.ROWID
        AND r.type = {_RECIPIENT_TYPE_TO}) AS to_addresses,
    PI.subjects.subject,
    PI.summaries.summary,
    main.messages.read,
    main.messages.flagged,
    main.messages.deleted,
    main.mailboxes.url,
    (SELECT GROUP_CONCAT(ma.name, ', ')
       FROM main.message_attachments ma
      WHERE ma.global_message_id = main.messages.global_message_id) AS attachment_names,
    (SELECT GROUP_CONCAT(att.size, ', ')
       FROM main.message_attachments ma
       JOIN main.attachments att ON att.ROWID = ma.attachment
      WHERE ma.global_message_id = main.messages.global_message_id) AS attachment_sizes,
    main.messages.global_message_id
FROM main.messages
LEFT JOIN main.mailboxes ON main.mailboxes.ROWID = main.messages.mailbox
LEFT JOIN PI.subjects ON PI.subjects.ROWID = main.messages.subject
LEFT JOIN PI.addresses ON PI.addresses.ROWID = main.messages.sender
LEFT JOIN PI.summaries ON PI.summaries.ROWID = main.messages.summary
ORDER BY main.messages.date_received
'''


@artifact_processor
def mailprotect(context):
    data_headers = (
        ('Date Sent', 'datetime'), ('Date Received', 'datetime'), 'Address', 'Comment',
        'To Recipients', 'Subject', 'Summary', 'Read?', 'Flagged?', 'Deleted', 'Mailbox',
        'Attachment Names', 'Attachment Sizes (Bytes)', 'Global Message ID')
    data_list = []

    envelope_db = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('Envelope Index'):
            envelope_db = file_found
            break
    if not envelope_db:
        return data_headers, data_list, ''

    head = os.path.split(envelope_db)[0]
    attach_query = attach_sqlite_db_readonly(os.path.join(head, 'Protected Index'), 'PI')
    try:
        rows = get_sqlite_db_records(envelope_db, _QUERY, attach_query=attach_query)
    except sqlite3.Error as ex:
        logfunc(f'Error reading Apple Mail (iOS 13+ schema expected): {ex}')
        return data_headers, data_list, context.get_relative_path(head)

    for row in rows:
        data_list.append(tuple(row))

    return data_headers, data_list, context.get_relative_path(head)


# An .emlx file is a byte-count line, then the RFC 822 message, then an Apple
# plist trailer. Only the message part is of interest here.
_EMLX_LEADING_COUNT_RE = re.compile(rb'^\s*\d+\s*\n')

# Headers surfaced as their own columns; everything else stays in Raw Headers.
_NAMED_HEADERS = (
    ('From', 'From'),
    ('To', 'To'),
    ('Cc', 'CC'),
    ('Bcc', 'BCC'),
    ('Reply-To', 'Reply To'),
    ('Subject', 'Subject'),
    ('Date', 'Date'),
    ('Message-ID', 'Message ID'),
    ('Return-Path', 'Return Path'),
    ('List-Unsubscribe', 'List Unsubscribe'),
)


def _decode_header(value):
    """Decode an RFC 2047 header and unfold its continuation lines."""
    if value is None:
        return ''
    try:
        decoded = str(email.header.make_header(email.header.decode_header(value)))
    except (UnicodeDecodeError, ValueError, LookupError):
        decoded = str(value)
    # Folded headers carry embedded newlines; collapse them so the value fits a cell.
    return ' '.join(decoded.split())


@artifact_processor
def mailHeaders(context):
    data_headers = (
        ('Date (from message Date header, UTC)', 'datetime'), 'From Address', 'To Address', 'CC', 'BCC', 'Reply To',
        'Subject', 'Date', 'Message ID', 'Return Path', 'List Unsubscribe',
        'Attachment Filenames', 'Global Message ID', 'Raw Headers', 'Source File')
    data_list = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('.emlx') or os.path.isdir(file_found):
            continue
        try:
            with open(file_found, 'rb') as handle:
                raw = handle.read()
        except OSError as ex:
            logfunc(f'Could not read {file_found}: {ex}')
            continue

        message = email.message_from_bytes(_EMLX_LEADING_COUNT_RE.sub(b'', raw, count=1))

        values = {label: _decode_header(message.get(header))
                  for header, label in _NAMED_HEADERS}

        filenames = ', '.join(
            _decode_header(part.get_filename())
            for part in message.walk() if part.get_filename())

        # MessageData/<global_message_id>/<name>.emlx ties the file back to the
        # Envelope Index row.
        parent = os.path.basename(os.path.dirname(file_found))
        global_message_id = parent if parent.isdigit() else ''

        raw_headers = '\n'.join(f'{k}: {_decode_header(v)}' for k, v in message.items())

        received = ''
        try:
            parsed = email.utils.parsedate_to_datetime(message.get('Date')) \
                if message.get('Date') else None
            if parsed is not None:
                received = convert_unix_ts_to_utc(parsed.timestamp())
        except (TypeError, ValueError, OverflowError):
            received = ''

        data_list.append((
            received,
            values['From'], values['To'], values['CC'], values['BCC'],
            values['Reply To'], values['Subject'], values['Date'],
            values['Message ID'], values['Return Path'], values['List Unsubscribe'],
            filenames, global_message_id, raw_headers,
            context.get_relative_path(file_found),
        ))

    return data_headers, data_list, ''
