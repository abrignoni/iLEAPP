__artifacts_v2__ = {
    'get_vipps': {
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
    get_plist_content,
    logfunc
)


@artifact_processor
def get_vipps(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = get_file_path(files_found, 'Vipps.sqlite')

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

    for row in db_records:
        plist_data = row[4]
        if not plist_data:
            continue

        try:
            plist = get_plist_content(plist_data)
        except Exception as ex:
            logfunc(f'Failed to read plist for {row[0]}, error was: {ex}')
            continue

        for i, y in plist.items():
            try:
                jsonitems = json.loads(y)
            except json.JSONDecodeError:
                continue

            telephone = ''
            if row[0] and '-' in row[0]:
                telephone = row[0].split('-')[1]
            name = ''

            phone_col = 'ZPHONENUMBERS'
            if does_column_exist_in_db(source_path, 'ZCONTACTMODEL', 'ZRAWPHONENUMBERS'):
                phone_col = 'ZRAWPHONENUMBERS'

            query_contact = f'''
            SELECT ZNAME FROM ZCONTACTMODEL WHERE {phone_col} LIKE "%{telephone}%"
            '''

            contact_rows = get_sqlite_db_records(source_path, query_contact)
            if contact_rows:
                name = contact_rows[0][0]

            if jsonitems.get('model') == "CHAT":
                data_content = jsonitems.get('data', {})

                timestamp = convert_unix_ts_to_utc(int(data_content.get('messageTimeStamp', 0))/1000)
                message = data_content.get('message', '')
                amount = data_content.get('amount', '')
                status_text = data_content.get('statusText', '')
                status_category = data_content.get('statusCategory', '')
                direction = data_content.get('direction', '')
                transaction_id = data_content.get('transactionID', '')
                type_val = data_content.get('type', '')

                data_list.append((
                    timestamp,
                    telephone,
                    name,
                    message,
                    amount,
                    status_text,
                    status_category,
                    direction,
                    transaction_id,
                    type_val,
                    source_path
                ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Telephone',
        'Name',
        'Message',
        'Amount',
        'Status Text',
        'Status Category',
        'Direction',
        'Transaction ID',
        'Type',
        'File Name'
    )

    return data_headers, data_list, source_path
