__artifacts_v2__ = {
    "get_trustedPeers": {
        "name": "Trusted Peers",
        "description": "Devices Associated with iCloud Account",
        "author": "Heather Charpentier",
        "version": "0.1",
        "date": "2024-12-13",
        "requirements": "none",
        "category": "Trusted Peers",
        "notes": "",
        "paths": ('*/Keychains/com.apple.security.keychain-defaultContext.TrustedPeersHelper.db*',),
        "output_types": "standard",
        "artifact_icon": "check-circle"
    }
}


from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_trustedPeers(files_found, report_folder, seeker, wrap_text, timezone_offset):
    file_found = str(files_found[0])
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('TrustedPeersHelper.db'):
            break

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    DISTINCT datetime(client.ZSECUREBACKUPMETADATATIMESTAMP + 978307200, 'unixepoch') AS "Timestamp",
	client.ZDEVICEMODEL AS "Model",
    client.ZDEVICEMODELVERSION AS "Model Version",
    client.ZDEVICENAME AS "Device Name",
    metadata.ZSERIAL AS "Serial Number",
	client.ZSECUREBACKUPNUMERICPASSPHRASELENGTH AS "Passcode Length"
    FROM
        ZESCROWCLIENTMETADATA AS client
    LEFT JOIN
        ZESCROWMETADATA AS metadata
    ON
        client.ZESCROWMETADATA = metadata.Z_PK;
    ''')

    all_rows = cursor.fetchall()
    data_list = []

    for row in all_rows:
        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))

    db.close()

    data_headers = ('Timestamp', 'Model', 'Model Version', 'Device Name', 'Serial Number', 'Passcode Length')
    return data_headers, data_list, file_found
