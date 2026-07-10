""" trustedPeers """
__artifacts_v2__ = {
    "trusted_peers": {
        "name": "Trusted Peers",
        "description": "Devices Associated with iCloud Account",
        "author": "Heather Charpentier",
        "creation_date": "2024-12-13",
        "last_update_date": "2026-06-18",
        "requirements": "none",
        "category": "Trusted Peers",
        "notes": "",
        "paths": ('**/*TrustedPeersHelper.db*',),
        "output_types": "standard",
        "artifact_icon": "circle-check",
        "sample_data": {
            "josh_ios_15": "23 rows",
            "mvs_2026": "6 rows but ZPEERINFO is empty",
            "dexter_ios18": "iOS 18.3.2 | 5 rows",
            "felix_ios17": "iOS 17.6.1 | 13 rows",
            "fsfull002_ios17": "iOS 17.1 | 5 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 24 rows",
            "iphone12_ios18": "iOS 18.7 | 3 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 3 rows",
        }
    }
}

from scripts.ilapfuncs import (
    artifact_processor,
    convert_cocoa_core_data_ts_to_utc,
    does_column_exist_in_db,
    get_file_path,
    get_sqlite_db_records,
    logfunc,
)

PEER_INFO_KEYS = (
    'OSVersion',
    'ModelName',
    'ComputerName',
    'SerialNumber',
)


def _read_der_length(data, offset):
    if offset >= len(data):
        return None, offset

    length = data[offset]
    offset += 1
    if length < 0x80:
        return length, offset

    length_bytes = length & 0x7f
    if length_bytes == 0 or offset + length_bytes > len(data):
        return None, offset

    length = int.from_bytes(data[offset:offset + length_bytes], 'big')
    return length, offset + length_bytes


def _read_der_strings(data, start=0, end=None):
    end = len(data) if end is None else end
    offset = start
    strings = []

    while offset < end:
        if offset + 2 > end:
            break

        tag = data[offset]
        offset += 1
        length, offset = _read_der_length(data, offset)
        if length is None or offset + length > end:
            break

        value = data[offset:offset + length]
        if tag in (0x0c, 0x13, 0x16, 0x1a):
            strings.append(value.decode('utf-8', errors='ignore'))
        elif tag & 0x20:
            strings.extend(_read_der_strings(data, offset, offset + length))

        offset += length

    return strings


def _peer_info_values(peer_info):
    values = {key: '' for key in PEER_INFO_KEYS}
    if not peer_info:
        return values

    strings = _read_der_strings(bytes(peer_info))
    for index, item in enumerate(strings[:-1]):
        if item in values:
            values[item] = strings[index + 1]

    return values


@artifact_processor
def trusted_peers(context):
    """ see artifact description """
    files_found = context.get_files_found()
    data_list = []
    source_path = get_file_path(files_found, '*TrustedPeersHelper.db')
    if not source_path:
        logfunc('TrustedPeersHelper.db not found')
        return (), [], ''

    device_color = (
        'client.ZDEVICECOLOR'
        if does_column_exist_in_db(source_path, 'ZESCROWCLIENTMETADATA', 'ZDEVICECOLOR')
        else 'NULL'
    )
    device_enclosure_color = (
        'client.ZDEVICEENCLOSURECOLOR'
        if does_column_exist_in_db(source_path, 'ZESCROWCLIENTMETADATA', 'ZDEVICEENCLOSURECOLOR')
        else 'NULL'
    )
    peer_info = (
        'metadata.ZPEERINFO'
        if does_column_exist_in_db(source_path, 'ZESCROWMETADATA', 'ZPEERINFO')
        else 'NULL'
    )

    query = f'''
    SELECT DISTINCT
        client.ZSECUREBACKUPMETADATATIMESTAMP,
        client.ZDEVICEMODEL,
        client.ZDEVICEMODELVERSION,
        client.ZDEVICENAME,
        metadata.ZSERIAL,
        client.ZSECUREBACKUPNUMERICPASSPHRASELENGTH,
        {device_color} AS ZDEVICECOLOR,
        {device_enclosure_color} AS ZDEVICEENCLOSURECOLOR,
        {peer_info} AS ZPEERINFO
    FROM
        ZESCROWCLIENTMETADATA AS client
    LEFT JOIN
        ZESCROWMETADATA AS metadata
    ON
        client.ZESCROWMETADATA = metadata.Z_PK;
    '''

    db_records = get_sqlite_db_records(source_path, query)

    for row in db_records:
        timestamp = convert_cocoa_core_data_ts_to_utc(row[0])
        peer_values = _peer_info_values(row[8])

        data_list.append((
            timestamp,
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            row[7],
            peer_values['OSVersion'],
            peer_values['ModelName'],
            peer_values['ComputerName'],
            peer_values['SerialNumber'],
        ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Model',
        'Model Version',
        'Device Name',
        'Serial Number',
        'Passcode Length',
        'Device Color',
        'Device Enclosure Color',
        'Peer OS Version',
        'Peer Model Name',
        'Peer Computer Name',
        'Peer Serial Number',
    )

    return data_headers, data_list, context.get_relative_path(source_path)
