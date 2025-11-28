__artifacts_v2__ = {
    "get_trustedPeers": {
        "name": "Trusted Peers",
        "description": "Devices Associated with iCloud Account",
        "author": "Heather Charpentier",
        "creation_date": "2024-12-13",
        "last_update_date": "2025-04-14",
        "requirements": "none",
        "category": "Trusted Peers",
        "notes": "",
        "paths": ('**/*TrustedPeersHelper.db*',),
        "output_types": "standard",
        "artifact_icon": "check-circle"
    }
}

from scripts.ilapfuncs import (
    artifact_processor,
    logfunc,
    get_file_path,
    get_sqlite_db_records,
    convert_cocoa_core_data_ts_to_utc
)


@artifact_processor
def get_trustedPeers(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = get_file_path(files_found, '*TrustedPeersHelper.db')
    if not source_path:
        logfunc('TrustedPeersHelper.db not found')
        return (), [], ''

    query = '''
    SELECT DISTINCT
        client.ZSECUREBACKUPMETADATATIMESTAMP,
        client.ZDEVICEMODEL,
        client.ZDEVICEMODELVERSION,
        client.ZDEVICENAME,
        metadata.ZSERIAL,
        client.ZSECUREBACKUPNUMERICPASSPHRASELENGTH
    FROM
        ZESCROWCLIENTMETADATA AS client
    LEFT JOIN
        ZESCROWMETADATA AS metadata
    ON
        client.ZESCROWMETADATA = metadata.Z_PK;
    '''

    db_records = get_sqlite_db_records(source_path, query)

    if db_records:
        for row in db_records:
            timestamp = convert_cocoa_core_data_ts_to_utc(row[0])

            data_list.append((
                timestamp,
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
            ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Model',
        'Model Version',
        'Device Name',
        'Serial Number',
        'Passcode Length',
    )

    return data_headers, data_list, source_path
