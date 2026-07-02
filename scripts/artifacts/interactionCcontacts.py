__artifacts_v2__ = {
    "interactionCContacts": {
        "name": "InteractionC - Contacts",
        "description": "Contact interactions recorded in interactionC.db",
        "author": "",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "InteractionC",
        "notes": "",
        "paths": ('**/interactionC.db*',),
        "output_types": "standard",
        "artifact_icon": "users"
    },
    "interactionCAttachments": {
        "name": "InteractionC - Attachments",
        "description": "Attachment interactions recorded in interactionC.db",
        "author": "",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "InteractionC",
        "notes": "",
        "paths": ('**/interactionC.db*',),
        "output_types": "standard",
        "artifact_icon": "paperclip"
    }
}

import sqlite3

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, logfunc


def _find_db(context):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('.db'):
            return file_found
    return ''


@artifact_processor
def interactionCContacts(context):
    data_headers = (
        ('Start Date', 'datetime'), ('End Date', 'datetime'), 'Bundle ID', 'Display Name',
        'Identifier', 'Direction', 'Is Response', 'Recipient Count',
        ('Zinteractions Creation Date', 'datetime'), ('Zcontacts Creation Date', 'datetime'),
        'Content URL')
    data_list = []
    source_path = _find_db(context)
    if not source_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        datetime(zinteractions.zstartdate + 978307200, 'unixepoch'),
        datetime(zinteractions.zenddate + 978307200, 'unixepoch'),
        zinteractions.zbundleid,
        zcontacts.zdisplayname,
        zcontacts.zidentifier,
        zinteractions.zdirection,
        zinteractions.zisresponse,
        zinteractions.zrecipientcount,
        datetime(zinteractions.zcreationdate + 978307200, 'unixepoch'),
        datetime(zcontacts.zcreationdate + 978307200, 'unixepoch'),
        zinteractions.zcontenturl
    FROM zinteractions
    LEFT JOIN zcontacts ON zinteractions.zsender = zcontacts.z_pk
    '''
    try:
        rows = get_sqlite_db_records(source_path, query)
    except sqlite3.Error as ex:
        logfunc(f'Error reading InteractionC contacts: {ex}')
        return data_headers, data_list, context.get_relative_path(source_path)

    for row in rows:
        data_list.append(tuple(row))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def interactionCAttachments(context):
    data_headers = (
        ('Creation Date', 'datetime'), 'Bundle ID', 'Target Bundle ID', 'ZUUID',
        'Content Text', 'Uniform Type ID', 'Content URL')
    data_list = []
    source_path = _find_db(context)
    if not source_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        datetime(zinteractions.ZCREATIONDATE + 978307200, 'unixepoch'),
        ZINTERACTIONS.zbundleid,
        ZINTERACTIONS.ztargetbundleid,
        ZINTERACTIONS.zuuid,
        ZATTACHMENT.zcontenttext,
        ZATTACHMENT.zuti,
        ZATTACHMENT.zcontenturl
    FROM zinteractions
    INNER JOIN z_1interactions ON zinteractions.z_pk = z_1interactions.z_3interactions
    INNER JOIN zattachment ON z_1interactions.z_1attachments = zattachment.z_pk
    '''
    try:
        rows = get_sqlite_db_records(source_path, query)
    except sqlite3.Error as ex:
        logfunc(f'Error reading InteractionC attachments: {ex}')
        return data_headers, data_list, context.get_relative_path(source_path)

    for row in rows:
        data_list.append(tuple(row))

    return data_headers, data_list, context.get_relative_path(source_path)
