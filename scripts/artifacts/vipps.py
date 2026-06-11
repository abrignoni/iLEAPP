__artifacts_v2__ = {
    'vipps': {
        'name': 'Vipps - Messages',
        'description': 'Extracts messages and transaction details from Vipps.',
        'author': '@AlexisBrignoni',
        'creation_date': '2022-06-22',
        'last_update_date': '2025-11-28',
        'requirements': 'none',
        'category': 'Vipps',
        'notes': '',
        'paths': ('*/Vipps.sqlite*',),
        'output_types': 'standard',
        'artifact_icon': 'message-square'
    }
}

import json

from scripts.ilapfuncs import (
    artifact_processor,
    get_file_path,
    get_sqlite_db_records,
    does_column_exist_in_db,
    convert_unix_ts_to_utc,
    get_plist_content
)


def _get_contact_name(source_path, telephone, phone_columns):
    if not telephone:
        return ''

    escaped_telephone = telephone.replace("'", "''")
    for phone_column in phone_columns:
        query = f'''
        SELECT ZNAME
        FROM ZCONTACTMODEL
        WHERE {phone_column} LIKE '%{escaped_telephone}%'
        '''
        contact_rows = get_sqlite_db_records(source_path, query)
        if contact_rows:
            return contact_rows[0][0]
    return ''


def _convert_message_timestamp(timestamp_value):
    if timestamp_value in (None, ''):
        return ''

    try:
        return convert_unix_ts_to_utc(float(timestamp_value) / 1000)
    except (TypeError, ValueError, OverflowError, OSError):
        return timestamp_value


def _parse_chat_item(json_items, telephone, name, relative_source_path):
    if json_items.get('model') != 'CHAT':
        return None

    data_content = json_items.get('data', {})
    if not isinstance(data_content, dict):
        return None

    return (
        _convert_message_timestamp(data_content.get('messageTimeStamp')),
        telephone,
        name,
        data_content.get('message', ''),
        data_content.get('amount', ''),
        data_content.get('statusText', ''),
        data_content.get('statusCategory', ''),
        data_content.get('direction', ''),
        data_content.get('transactionID', ''),
        data_content.get('type', ''),
        relative_source_path
    )


@artifact_processor
def vipps(context):
    data_list = []
    source_path = get_file_path(context.get_files_found(), 'Vipps.sqlite')

    if not source_path:
        return (), [], ''

    query = '''
    SELECT
    ZFEEDMODELKEY,
    ZMODELTYPE,
    ZSTATUS,
    ZVIPPSTRANSACTIONID,
    ZBLOB
    FROM ZFEEDDETAILMODEL
    '''

    db_records = get_sqlite_db_records(source_path, query)
    phone_columns = []
    if does_column_exist_in_db(source_path, 'ZCONTACTMODEL', 'ZRAWPHONENUMBERS'):
        phone_columns.append('ZRAWPHONENUMBERS')
    if does_column_exist_in_db(source_path, 'ZCONTACTMODEL', 'ZPHONENUMBERS'):
        phone_columns.append('ZPHONENUMBERS')
    relative_source_path = context.get_relative_path(source_path)

    for row in db_records:
        if not row[4]:
            continue

        plist = get_plist_content(row[4])
        if not isinstance(plist, dict):
            continue

        for plist_value in plist.values():
            try:
                json_items = json.loads(plist_value)
            except (json.JSONDecodeError, TypeError):
                continue

            if not isinstance(json_items, dict):
                continue

            telephone = ''
            if row[0] and '-' in row[0]:
                telephone = row[0].split('-', 1)[1]
            name = _get_contact_name(source_path, telephone, phone_columns)
            chat_item = _parse_chat_item(
                json_items, telephone, name, relative_source_path
            )
            if chat_item:
                data_list.append(chat_item)

    data_headers = (
        ('Timestamp', 'datetime'),
        ('Telephone', 'phonenumber'),
        'Name',
        'Message',
        'Amount',
        'Status Text',
        'Status Category',
        'Direction',
        'Transaction ID',
        'Message Type',
        'Source File'
    )

    return data_headers, data_list, source_path
