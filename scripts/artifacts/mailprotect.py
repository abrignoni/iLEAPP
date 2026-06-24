__artifacts_v2__ = {
    "mailprotect": {
        "name": "Apple Email",
        "description": "Apple Mail messages from the Envelope Index and Protected Index databases (iOS 13+)",
        "author": "@abrignoni - @stark4n6",
        "creation_date": "2020-05-07",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Apple Mail",
        "notes": "Supports iOS 13 and later.",
        "paths": ('*/mobile/Library/Mail/* Index*',),
        "output_types": "standard",
        "artifact_icon": "mail"
    }
}

import os
import sqlite3

from scripts.ilapfuncs import (artifact_processor, attach_sqlite_db_readonly,
                               get_sqlite_db_records, logfunc)

_QUERY = '''
SELECT
    datetime(main.messages.date_sent, 'UNIXEPOCH'),
    datetime(main.messages.date_received, 'UNIXEPOCH'),
    PI.addresses.address,
    PI.addresses.comment,
    PI.subjects.subject,
    PI.summaries.summary,
    main.messages.read,
    main.messages.flagged,
    main.messages.deleted,
    main.mailboxes.url
FROM main.mailboxes, main.messages, PI.subjects, PI.addresses, PI.summaries
WHERE main.messages.subject = PI.subjects.ROWID
AND main.messages.sender = PI.addresses.ROWID
AND main.messages.summary = PI.summaries.ROWID
AND main.mailboxes.ROWID = main.messages.mailbox
'''


@artifact_processor
def mailprotect(context):
    data_headers = (
        ('Date Sent', 'datetime'), ('Date Received', 'datetime'), 'Address', 'Comment', 'Subject',
        'Summary', 'Read?', 'Flagged?', 'Deleted', 'Mailbox')
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
