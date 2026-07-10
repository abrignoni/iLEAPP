__artifacts_v2__ = {
    "kikGroupadmins": {
        "name": "Kik Group Administrators",
        "description": "Kik users that are administrators of a group (kik.sqlite)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-06-22",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Kik",
        "notes": "",
        "paths": ('*/kik.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "felix_ios17": "iOS 17.6.1 | Kik Messaging & Chat App 17.0.0 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Kik Messaging & Chat App 16.9.3 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Kik Messaging & Chat App 17.11.3 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Kik Messaging & Chat App 16.16.1 | 0 rows",
        }
    }
}

import blackboxprotobuf

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _decode_additional_info(blob):
    """Decode the ZROSTERENTRYDATA protobuf; return (user_a, user_b, display, value)."""
    user_a = user_b = display = value = ''
    if blob is None:
        return user_a, user_b, display, value
    try:
        data, _ = blackboxprotobuf.decode_message(blob)
        raw = data['1']['1']
        user_a = '' if isinstance(raw, dict) else raw.decode('utf-8')
        if data.get('2') is not None:
            raw = data['2']['1']['1']
            value = '' if isinstance(raw, dict) else raw.decode('utf-8')
        user_b = data['3']['1'].decode('utf-8')
        raw = data['4']['1']
        display = '' if isinstance(raw, dict) else raw.decode('utf-8')
    except Exception:  # pylint: disable=broad-exception-caught
        pass  # blob layout varies / may be absent; keep whatever was decoded
    return user_a, user_b, display, value


def _decode_entity_blob(blob):
    """Decode the ZENTITYUSERDATA protobuf; return (username, description, interests)."""
    username = description = interests = ''
    if blob is None:
        return username, description, interests
    try:
        data, _ = blackboxprotobuf.decode_message(blob)
        if data['1'].get('5') is not None:
            for item in data['1']['5']['1']:
                interests = item['2'].decode('utf-8') + ', ' + interests
            interests = interests[:-2]
        if isinstance(data['1'].get('1'), bytes):
            username = data['1']['1'].decode('utf-8')
        elif isinstance(data['1'].get('1'), dict) and data['1']['1'].get('1') is not None:
            description = data['1']['1']['1'].decode('utf-8')
        if data.get('104') is not None:
            for item in data['104']['1']:
                interests = item['2'].decode('utf-8') + ', ' + interests
            interests = interests[:-2]
    except Exception:  # pylint: disable=broad-exception-caught
        pass  # blob layout varies / may be absent; keep whatever was decoded
    return username, description, interests


@artifact_processor
def kikGroupadmins(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    data_headers = ('User ID', 'Display Name', 'Username', 'Profile Pic URL', 'Member Group ID',
                    'Group Tag', 'Group Name', 'Group ID', 'Group Pic URL', 'Blob User',
                    'Blob Description', 'Blob Interests', 'Additional Info User A',
                    'Additional Info User B', 'Additional Info Display', 'Additional Info Value')
    data_list = []

    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('kik.sqlite'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
    SELECT ZKIKUSER.Z_PK,
        ZKIKUSER.ZDISPLAYNAME,
        ZKIKUSER.ZUSERNAME,
        ZKIKUSER.ZPPURL,
        Z_9ADMINSINVERSE.Z_9ADMINSINVERSE,
        ZKIKUSEREXTRA.ZENTITYUSERDATA,
        ZKIKUSEREXTRA.ZROSTERENTRYDATA
    FROM ZKIKUSER
        INNER JOIN Z_9ADMINSINVERSE ON ZKIKUSER.Z_PK = Z_9ADMINSINVERSE.Z_9ADMINS
        LEFT JOIN ZKIKUSEREXTRA ON ZKIKUSER.Z_PK = ZKIKUSEREXTRA.ZUSER
    ORDER BY Z_9ADMINSINVERSE
    ''')

    for row in cursor.fetchall():
        grouptag = groupdname = zjid = zpurl = ''
        cursor2 = db.cursor()
        cursor2.execute('SELECT ZGROUPTAG, ZDISPLAYNAME, ZJID, ZPPURL FROM ZKIKUSER WHERE Z_PK = ?',
                        (row[4],))
        for rows2 in cursor2.fetchall():
            grouptag, groupdname, zjid, zpurl = rows2[0], rows2[1], rows2[2], rows2[3]

        username, description, interests = _decode_entity_blob(row[5])
        info_a, info_b, info_display, info_value = _decode_additional_info(row[6])

        data_list.append((row[0], row[1], row[2], row[3], row[4], grouptag, groupdname, zjid, zpurl,
                          username, description, interests, info_a, info_b, info_display, info_value))
    db.close()

    return data_headers, data_list, source_path
