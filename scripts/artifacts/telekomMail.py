__artifacts_v2__ = {
    "telekomMailMessages": {
        "name": "Telekom Mail - Messages",
        "description": "Email messages held by the Telekom Mail iOS client",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-22",
        "last_update_date": "2026-09-22",
        "requirements": "none",
        "category": "Telekom Mail",
        "notes": "Read from the Messages-<address>.sqlite Core Data store the Telekom Mail client keeps "
                 "in Application Support, one store per signed in account. On the devices tested the "
                 "mail was in the clear. A row is a message header from ZMESSAGEHEADER joined to its "
                 "one line preview in ZCONTENTPREVIEW through the shared ZMESSAGE row. Received and "
                 "Sent are ZDATERECEIVED and ZDATESENT, Cocoa seconds from 2001. Sender is the "
                 "ZSENDER string as the client stored it, usually a display name and an address. "
                 "Recipients and CC are the email addresses found in the ZRECIPIENTS and "
                 "ZRECIPIENTSCC blobs, which the client stores as archived objects; the addresses are "
                 "extracted from the blob and joined with a comma, and an address that is not an email "
                 "in that blob is not shown. Folder is ZFOLDERPATH, which names the mailbox the "
                 "message sits in (the client's inbox, sent and other folders), and is the plain way "
                 "to tell an incoming message from a sent one without asserting a mapping for the "
                 "folder type integer. Preview is the client's own one line preview, not the full "
                 "body: the full body is an HTML or text part in ZMESSAGE.ZTEXTPART, which is not "
                 "reported here to keep the row readable, and is available in the store for an "
                 "examiner who needs it. Seen, Answered, Flagged and Has Attachments are the client's "
                 "own flags, reported as stored; on the devices tested every message was seen and none was "
                 "answered or flagged, so those three held one value, kept because a store with an "
                 "unread or flagged message would show it. Field mapping was done against two "
                 "private samples; no sample data is "
                 "recorded for them. A Messages-<address>.sqlite that does not carry this client's own "
                 "tables is skipped, so another app's file of a similar name is not reported as "
                 "Telekom Mail. Each account's store is a separate file, and every one in the "
                 "extraction is read.",
        "paths": ('*/Library/Application Support/Messages-*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "mail"
    },
    "telekomMailAttachments": {
        "name": "Telekom Mail - Attachments",
        "description": "Email attachments recorded by the Telekom Mail iOS client",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-22",
        "last_update_date": "2026-09-22",
        "requirements": "none",
        "category": "Telekom Mail",
        "notes": "Read from the ZATTACHMENT table of the Messages-<address>.sqlite store, joined to "
                 "its message's subject and date through the shared ZMESSAGE row. File Name, MIME "
                 "Type and Size are the client's own columns. Inline says whether the attachment is "
                 "an inline part of the message body rather than a separate file. The attachment bytes "
                 "are not rendered here: on the devices tested the ZDATA column was empty for the "
                 "listed attachments, so this artifact reports that an attachment existed, its name, "
                 "type and size, rather than the file itself. Inline was zero on every attachment of the "
                 "devices tested, kept because an inline image would set it, and Message Received "
                 "and Subject are blank where the attachment's message has no header row, which is "
                 "why the date leads the table only partly filled. Field mapping was done against two "
                 "private samples; no sample data is recorded for them.",
        "paths": ('*/Library/Application Support/Messages-*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "paperclip"
    },
}

import os
import re

from scripts.ilapfuncs import (artifact_processor, get_sqlite_db_records,
                               convert_cocoa_core_data_ts_to_utc)

EMAIL = re.compile(rb'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
# The store is generically named. It is this client's only when it carries these tables.
REQUIRED_TABLES = {'ZMESSAGEHEADER', 'ZMESSAGE', 'ZCONTENTPREVIEW'}


def _tables(db_path):
    return {row[0] for row in get_sqlite_db_records(
        db_path, "SELECT name FROM sqlite_master WHERE type='table'")}


def _emails(blob):
    if not blob:
        return ''
    seen = []
    for match in EMAIL.findall(bytes(blob)):
        address = match.decode('ascii', 'replace')
        if address not in seen:
            seen.append(address)
    return ', '.join(seen)


def _stores(context):
    """Every Telekom Mail Core Data store, confirmed by its own tables."""
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not os.path.basename(file_found.replace('\\', '/')).endswith('.sqlite'):
            continue
        if 'Messages-' not in os.path.basename(file_found.replace('\\', '/')):
            continue
        if REQUIRED_TABLES <= _tables(file_found):
            yield file_found


@artifact_processor
def telekomMailMessages(context):
    data_headers = (
        ('Received', 'datetime'),
        ('Sent', 'datetime'),
        'Folder',
        'Sender',
        'Recipients',
        'CC',
        'Subject',
        'Preview',
        'Seen',
        'Answered',
        'Flagged',
        'Has Attachments',
        'Message ID',
        'Source File',
    )
    data_list = []
    source_paths = []

    query = '''
        SELECT h.ZDATERECEIVED, h.ZDATESENT, h.ZFOLDERPATH, h.ZSENDER, h.ZRECIPIENTS,
               h.ZRECIPIENTSCC, h.ZSUBJECT, p.ZTEXT, h.ZISSEEN, h.ZISANSWERED, h.ZISFLAGGED,
               h.ZHASATTACHMENTS, h.ZMESSAGEID
        FROM ZMESSAGEHEADER h
        LEFT JOIN ZCONTENTPREVIEW p ON p.ZMESSAGE = h.ZMESSAGE
    '''
    for db_path in _stores(context):
        rows = 0
        for row in get_sqlite_db_records(db_path, query):
            data_list.append((
                convert_cocoa_core_data_ts_to_utc(row[0]) if row[0] else '',
                convert_cocoa_core_data_ts_to_utc(row[1]) if row[1] else '',
                row[2] or '',
                row[3] or '',
                _emails(row[4]),
                _emails(row[5]),
                row[6] or '',
                row[7] or '',
                row[8] if row[8] is not None else '',
                row[9] if row[9] is not None else '',
                row[10] if row[10] is not None else '',
                row[11] if row[11] is not None else '',
                row[12] or '',
                context.get_relative_path(db_path),
            ))
            rows += 1
        if rows:
            source_paths.append(db_path)

    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def telekomMailAttachments(context):
    data_headers = (
        ('Message Received', 'datetime'),
        'Message Subject',
        'File Name',
        'MIME Type',
        'Size (bytes)',
        'Inline',
        'Source File',
    )
    data_list = []
    source_paths = []

    query = '''
        SELECT h.ZDATERECEIVED, h.ZSUBJECT, a.ZFILENAME, a.ZTYPE, a.ZSIZE, a.ZISINLINEATTACHMENT
        FROM ZATTACHMENT a
        LEFT JOIN ZMESSAGEHEADER h ON h.ZMESSAGE = a.ZMESSAGE
    '''
    for db_path in _stores(context):
        if 'ZATTACHMENT' not in _tables(db_path):
            continue
        rows = 0
        for row in get_sqlite_db_records(db_path, query):
            data_list.append((
                convert_cocoa_core_data_ts_to_utc(row[0]) if row[0] else '',
                row[1] or '',
                row[2] or '',
                row[3] or '',
                row[4] if row[4] is not None else '',
                row[5] if row[5] is not None else '',
                context.get_relative_path(db_path),
            ))
            rows += 1
        if rows:
            source_paths.append(db_path)

    return data_headers, data_list, '\n'.join(source_paths)
