__artifacts_v2__ = {
    "kikGroupadmins": {
        "name": "Kik Group Administrators",
        "description": "ZKIKUSER rows joined to the administrators join table of kik.sqlite "
                       "(Z_9ADMINSINVERSE on the tested images), with the ZKIKUSER row each is "
                       "linked to. No tested image returned rows.",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-06-22",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Kik",
        "notes": "The Blob and Additional Info columns are decoded from the ZENTITYUSERDATA and "
                 "ZROSTERENTRYDATA protobufs by field position. The positions and the column "
                 "labels are not sourced from Kik, and what each field holds is not established. "
                 "On each of the seven tested images kik.sqlite holds a Z_9ADMINSINVERSE table "
                 "with columns Z_9ADMINS and Z_9ADMINSINVERSE and no rows, and Z_PRIMARYKEY "
                 "numbers the KikUser entity 9. The artifact therefore returned no rows on any of "
                 "them, and neither the join nor the decode has been exercised on real data. "
                 "Which of the two join columns holds the administrator and which the group is "
                 "not established: the query matches Z_<n>ADMINS to the reported user row and "
                 "looks up Z_<n>ADMINSINVERSE as the group row, and the Administrator Group ID "
                 "column is the Z_<n>ADMINSINVERSE value as stored. The number in the table name "
                 "is read from the store's own table list, not fixed in the query; that was "
                 "checked on a constructed copy of the iphone11_ios17 store with the table "
                 "renamed and one row added, not on a real store with another number. A store "
                 "with no such table is logged and reports no rows.",
        "paths": ('*/kik.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "felix_ios17": "iOS 17.6.1 | Kik Messaging & Chat App 17.0.0 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Kik Messaging & Chat App 16.9.3 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Kik Messaging & Chat App 17.11.3 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Kik Messaging & Chat App 16.16.1 | 0 rows",
            "felix23_ios16": "iOS 16.5 | Kik Messaging & Chat App 16.9.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | Kik 15.21.2 | 0 rows",
            "hickman_ios14": "iOS 14.3 | Kik 15.25.1 | 0 rows",
        }
    }
}

from scripts import blackboxprotobuf

import re

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


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
def kikGroupadmins(context):
    data_headers = ('User ID', 'Display Name', 'Username', 'Profile Pic URL', 'Administrator Group ID',
                    'Group Tag', 'Group Name', 'Group ID', 'Group Pic URL', 'Blob User',
                    'Blob Description', 'Blob Interests', 'Additional Info User A',
                    'Additional Info User B', 'Additional Info Display', 'Additional Info Value')
    data_list = []

    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('kik.sqlite'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()

    # Core Data names the join table after the KikUser entity's number, which is set by
    # the store's model. Take the table and its two columns from the store itself.
    join_table = admins_col = inverse_col = ''
    cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")
    for (table_name,) in cursor.fetchall():
        matched = re.fullmatch(r'Z_(\d+)ADMINSINVERSE', table_name or '')
        if not matched:
            continue
        columns = [info[1] for info in cursor.execute(f'PRAGMA table_info("{table_name}")')]
        wanted = (f'Z_{matched.group(1)}ADMINS', table_name)
        if all(column in columns for column in wanted):
            join_table, admins_col, inverse_col = table_name, wanted[0], wanted[1]
            break
    if not join_table:
        logfunc('Kik Group Administrators: no Z_<n>ADMINSINVERSE table in kik.sqlite')
        db.close()
        return data_headers, data_list, source_path

    cursor.execute(f'''
    SELECT ZKIKUSER.Z_PK,
        ZKIKUSER.ZDISPLAYNAME,
        ZKIKUSER.ZUSERNAME,
        ZKIKUSER.ZPPURL,
        {join_table}.{inverse_col},
        ZKIKUSEREXTRA.ZENTITYUSERDATA,
        ZKIKUSEREXTRA.ZROSTERENTRYDATA
    FROM ZKIKUSER
        INNER JOIN {join_table} ON ZKIKUSER.Z_PK = {join_table}.{admins_col}
        LEFT JOIN ZKIKUSEREXTRA ON ZKIKUSER.Z_PK = ZKIKUSEREXTRA.ZUSER
    ORDER BY {join_table}.{inverse_col}
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
