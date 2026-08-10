__artifacts_v2__ = {
    'appleAccountDeviceList': {
        'name': 'Apple Account - Device List',
        'description': 'Devices cached by the Apple authentication daemon (akd) for the '
                       'Apple Accounts signed in on this device',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-29',
        'last_update_date': '2026-07-29',
        'requirements': 'none',
        'category': 'Accounts',
        'notes': ('The list is a cache maintained by akd, so it reflects the last successful '
                  'refresh rather than the account state at extraction time. Columns dc, clcg, '
                  'clbg, clhs and dec are reported with their database names because their '
                  'meaning is not documented.'),
        'paths': ('*/mobile/Library/Application Support/com.apple.akd/devicelist.db*',),
        'output_types': 'standard',
        'artifact_icon': 'devices',
        'sample_data': {
            'hc_ios18_7': 'iOS 18.7.8 | 1 row (the device itself); additional_info held an IMEI',
        },
    },
    'appleAccountDeletedDeviceList': {
        'name': 'Apple Account - Deleted Device List',
        'description': 'Devices removed from the Apple Accounts signed in on this device, as '
                       'recorded by the Apple authentication daemon (akd)',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-29',
        'last_update_date': '2026-07-29',
        'requirements': 'none',
        'category': 'Accounts',
        'notes': ('The reason column is an integer code whose values are not documented, so it '
                  'is reported as stored.'),
        'paths': ('*/mobile/Library/Application Support/com.apple.akd/devicelist.db*',),
        'output_types': 'standard',
        'artifact_icon': 'device-mobile-off',
        'sample_data': {
            'hc_ios18_7': 'iOS 18.7.8 | 0 rows (table present but empty)',
        },
    },
}

import json

from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records, does_table_exist_in_db, convert_unix_ts_to_utc


def _decode_additional_info(blob):
    """Return (imei list, raw text) for the additional_info column.

    On the tested image the blob is UTF-8 JSON of the form
    {"phones": [{"imei": "...", "slotID": 1}]}. Anything that does not decode
    as JSON is passed through as text so nothing is silently dropped.
    """
    if not blob:
        return '', ''
    if isinstance(blob, bytes):
        text = blob.decode('utf-8', 'replace')
    else:
        text = str(blob)
    try:
        parsed = json.loads(text)
    except (ValueError, TypeError):
        return '', text
    imeis = []
    if isinstance(parsed, dict):
        for phone in parsed.get('phones') or []:
            if isinstance(phone, dict) and phone.get('imei'):
                imeis.append(str(phone['imei']))
    return ', '.join(imeis), text


def _yes_no(value):
    """Render the 0/1 flag columns, leaving anything unexpected as stored."""
    if value == 1:
        return 'Yes'
    if value == 0:
        return 'No'
    return value


@artifact_processor
def appleAccountDeviceList(context):
    source_path = get_file_path(context.get_files_found(), 'devicelist.db')
    data_list = []
    data_headers = (
        ('Last Updated', 'datetime'), ('Last Cache Updated', 'datetime'), 'Device Name',
        'Model', 'OS', 'OS Version', 'Build Number', 'Serial Number', 'IMEI', 'Trusted',
        'Circle Status', 'Services', 'Machine ID (mid)', 'altDSID', 'dc', 'clcg', 'clbg',
        'clhs', 'dec', 'Additional Info')
    if not source_path:
        return data_headers, data_list, ''

    query = '''
    SELECT last_updated_date, last_cache_updated_date, name, model, os, os_version,
           build_number, serial_number, additional_info, trusted, circle_status, services,
           mid, altDSID, dc, clcg, clbg, clhs, dec
    FROM device_list
    ORDER BY last_updated_date
    '''

    for record in get_sqlite_db_records(source_path, query):
        imei, additional_info = _decode_additional_info(record['additional_info'])
        data_list.append((
            convert_unix_ts_to_utc(record['last_updated_date']),
            convert_unix_ts_to_utc(record['last_cache_updated_date']),
            record['name'],
            record['model'],
            record['os'],
            record['os_version'],
            record['build_number'],
            record['serial_number'],
            imei,
            _yes_no(record['trusted']),
            record['circle_status'],
            record['services'],
            record['mid'],
            record['altDSID'],
            record['dc'],
            record['clcg'],
            record['clbg'],
            record['clhs'],
            record['dec'],
            additional_info,
        ))

    return data_headers, data_list, source_path


@artifact_processor
def appleAccountDeletedDeviceList(context):
    source_path = get_file_path(context.get_files_found(), 'devicelist.db')
    data_list = []
    data_headers = (
        ('Deleted', 'datetime'), ('Last Updated', 'datetime'), 'Reason Code',
        'Machine ID (mid)', 'altDSID')
    if not source_path or not does_table_exist_in_db(source_path, 'deleted_device_list'):
        return data_headers, data_list, ''

    query = '''
    SELECT deleted_date, last_updated_date, reason, mid, altDSID
    FROM deleted_device_list
    ORDER BY deleted_date
    '''

    for record in get_sqlite_db_records(source_path, query):
        data_list.append((
            convert_unix_ts_to_utc(record['deleted_date']),
            convert_unix_ts_to_utc(record['last_updated_date']),
            record['reason'],
            record['mid'],
            record['altDSID'],
        ))

    return data_headers, data_list, source_path
