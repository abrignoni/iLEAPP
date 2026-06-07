__artifacts_v2__ = {
    "trustedPeers": {
        "name": "Trusted Peers",
        "description": "Devices Associated with iCloud Account",
        "author": "Heather Charpentier",
        "version": "0.2",
        "date": "2024-12-13",
        "last_updated": "2026-03-30",
        "requirements": "none",
        "category": "Trusted Peers",
        "notes": " - updated by @ghmihkel. Add device colors and extract SerialNumber from ZESCROWMETADATA.ZPEERINFO DER data",
        "paths": ('*/Keychains/com.apple.security.keychain-defaultContext.TrustedPeersHelper.db*',),
        "output_types": "standard",
        "function": "get_trustedPeers",
        "artifact_icon": "check-circle"
    }
}

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, timeline, tsv, open_sqlite_db_readonly

PEER_KEYS = ("OSVersion", "ModelName", "ComputerName", "SerialNumber")


def _read_der_strings(data: bytes) -> dict:
    """Scan raw DER bytes for known key/value string pairs."""
    result = {k: "" for k in PEER_KEYS}
    i = 0
    while i < len(data) - 2:
        if data[i] == 0x0C:
            length = data[i + 1]
            text = data[i + 2:i + 2 + length].decode("utf-8", errors="ignore")
            if text in PEER_KEYS:
                j = i + 2 + length
                if j < len(data) - 1 and data[j] == 0x0C:
                    vlen = data[j + 1]
                    result[text] = data[j + 2:j + 2 + vlen].decode("utf-8", errors="ignore")
        i += 1
    return result


def get_trustedPeers(files_found, report_folder, seeker, wrap_text, timezone_offset):
    file_found = next(f for f in files_found if str(f).endswith('TrustedPeersHelper.db'))

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
        SELECT
            datetime(c.ZSECUREBACKUPMETADATATIMESTAMP + 978307200, 'unixepoch'),
            c.ZDEVICEMODEL, c.ZDEVICEMODELVERSION, c.ZDEVICENAME,
            m.ZSERIAL, c.ZSECUREBACKUPNUMERICPASSPHRASELENGTH,
            c.ZDEVICECOLOR, c.ZDEVICEENCLOSURECOLOR,
            m.ZPEERINFO
        FROM ZESCROWCLIENTMETADATA c
        LEFT JOIN ZESCROWMETADATA m ON c.ZESCROWMETADATA = m.Z_PK
    ''')
    rows = cursor.fetchall()
    db.close()

    if not rows:
        logfunc('No Trusted Peers data available')
        return

    headers = ('Timestamp', 'Model', 'Model Version', 'Device Name',
               'Serial Number', 'Passcode Length',
               'Bezel Color', 'Back Color',
               'OS Version', 'Serial (PeerInfo)')

    data_set = set()
    for row in rows:
        peer = _read_der_strings(bytes(row[8])) if row[8] else {}
        data_set.add((
            row[0], row[1], row[2], row[3], row[4], row[5],
            row[6], row[7],
            peer.get("OSVersion", ""),  peer.get("SerialNumber", ""),
        ))

    report = ArtifactHtmlReport('Trusted Peers')
    report.start_artifact_report(report_folder, 'Trusted Peers', 'Trusted Peers')
    report.add_script()
    report.write_artifact_data_table(headers, data_set, file_found)
    report.end_artifact_report()

    tsv(report_folder, headers, data_set, 'Trusted Peers')
    timeline(report_folder, 'Trusted Peers', data_set, headers)
