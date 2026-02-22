__artifacts_v2__ = {
    "get_line": {
        "name": "Line Artifacts",
        "description": "Get Line",
        "author": "Elliot Glendye",
        "version": "0.0.1",
        "date": "2023-11-22",
        "requirements": "",
        "category": "Line",
        "notes": "No notes at present.",
        "paths": ('**/Line.sqlite*',),
        "output_types": "standard"
    }
}

from packaging import version
from scripts.ilapfuncs import logfunc, artifact_processor, open_sqlite_db_readonly, iOS


@artifact_processor
def get_line(files_found, report_folder, seeker, wrap_text, timezone_offset):
    file_found = str(files_found[0])
    for file_found in files_found:
        file_found = str(file_found)

        iOSversion = iOS.get_version()
        if version.parse(iOSversion) < version.parse('15'):
            logfunc('Line parsing has not been tested on iOS version ' + iOSversion)

        if file_found.endswith('Line.sqlite'):
            break

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    Select datetime(ZMESSAGE.ZTIMESTAMP / 1000, 'unixepoch') AS Timestamp,
    CASE
    WHEN ZMESSAGE.ZSENDER IS NULL THEN "Outgoing"
     ELSE "Incoming" END AS "Sent / Received",
    ZUSER.ZNAME AS "Username",
    ZMESSAGE.ZTEXT AS "Message Content"
    From ZMESSAGE
    LEFT Join ZUSER On ZMESSAGE.ZSENDER = ZUSER.Z_PK
    ORDER BY ZMESSAGE.ZTIMESTAMP Desc;
    ''')

    all_rows = cursor.fetchall()
    data_list = []

    for row in all_rows:
        data_list.append((row[0], row[1], row[2], row[3]))

    db.close()

    data_headers = ('Timestamp', 'Sent / Received', 'Username', 'Message')
    return data_headers, data_list, file_found
