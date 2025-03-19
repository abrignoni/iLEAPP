__artifacts_v2__ = {
    "trustedPeers": {
        "name": "Trusted Peers",
        "description": "Devices Associtated with iCloud Account",
        "author": "Heather Charpentier",
        "version": "0.1",
        "date": "2024-12-13",
        "requirements": "none",
        "category": "Trusted Peers",
        "notes": "",
        "paths": ('*/private/var/Keychains/com.apple.security.keychain-defaultContext.TrustedPeersHelper.db*',),
        "output_types": "standard",
        "function": "get_trustedPeers",
        "artifact_icon": "check-circle"
    }
}


import os
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, timeline, tsv, is_platform_windows, open_sqlite_db_readonly


def get_trustedPeers(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
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
    usageentries = len(all_rows)
    data_list = []  
    
    if usageentries > 0:
        for row in all_rows:
        
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))

        description = 'Trusted Peers'
        report = ArtifactHtmlReport('Trusted Peers')
        report.start_artifact_report(report_folder, 'Trusted Peers', description)
        report.add_script()
        data_headers = ('Timestamp', 'Model', 'Model Version', 'Device Name', 'Serial Number', 'Passcode Length')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Trusted Peers'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Trusted Peers'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Trusted Peers data available')
        
    db.close()

