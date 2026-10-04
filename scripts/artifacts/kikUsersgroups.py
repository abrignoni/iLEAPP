__artifacts_v2__ = {
    "kikUsersgroups": {
        "name": "Kik Users in Groups",
        "description": "ZKIKUSER rows joined to the members join table of kik.sqlite, with the "
                       "group row each is linked to.",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-06-22",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Kik",
        "notes": "The join table is named Z_<n>MEMBERS, where <n> is the Core Data entity number "
                 "of the store's model, and the name is read from the store. It was Z_9MEMBERS on "
                 "the seven tested images, and the table held no rows on any of them, so the "
                 "query and the columns it fills were not exercised on real rows. A store with "
                 "no such table is logged and reports no rows. Blob and Additional Information "
                 "are the ZENTITYUSERDATA and ZROSTERENTRYDATA values as stored.",
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

import re

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


def _members_join_table(db):
    """Return (table, member column, group column) for the members join table, or None.

    Core Data names a many-to-many join table Z_<n><RELATIONSHIP>, where <n> is the entity
    number of the model in use, so the number is read from the store and not assumed.
    """
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    for (name,) in cursor.fetchall():
        match = re.fullmatch(r'Z_(\d+)MEMBERS', name)
        if not match:
            continue
        member_col = name
        group_col = f'Z_{match.group(1)}MEMBERSINVERSE'
        cursor.execute(f'PRAGMA table_info("{name}")')
        columns = {row[1] for row in cursor.fetchall()}
        if member_col in columns and group_col in columns:
            return name, member_col, group_col
    return None


@artifact_processor
def kikUsersgroups(context):
    data_headers = ('User ID', 'Display Name', 'Username', 'Profile Pic URL', 'Member Group ID',
                    'Group Tag', 'Group Name', 'Group ID', 'Group Pic URL', 'Blob',
                    'Additional Information')
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
    join_table = _members_join_table(db)
    if join_table is None:
        logfunc('Kik Users in Groups: kik.sqlite has no Z_<n>MEMBERS join table')
        db.close()
        return data_headers, data_list, source_path
    table, member_col, group_col = join_table
    cursor = db.cursor()
    cursor.execute(f'''
    SELECT ZKIKUSER.Z_PK,
        ZKIKUSER.ZDISPLAYNAME,
        ZKIKUSER.ZUSERNAME,
        ZKIKUSER.ZPPURL,
        {table}.{group_col},
        ZKIKUSEREXTRA.ZENTITYUSERDATA,
        ZKIKUSEREXTRA.ZROSTERENTRYDATA
    FROM ZKIKUSER
        INNER JOIN {table} ON ZKIKUSER.Z_PK = {table}.{member_col}
        LEFT JOIN ZKIKUSEREXTRA ON ZKIKUSER.Z_PK = ZKIKUSEREXTRA.ZUSER
    ORDER BY {table}.{group_col}
    ''')

    for row in cursor.fetchall():
        grouptag = groupdname = zjid = zpurl = ''
        cursor2 = db.cursor()
        cursor2.execute('SELECT ZGROUPTAG, ZDISPLAYNAME, ZJID, ZPPURL FROM ZKIKUSER WHERE Z_PK = ?',
                        (row[4],))
        for rows2 in cursor2.fetchall():
            grouptag, groupdname, zjid, zpurl = rows2[0], rows2[1], rows2[2], rows2[3]
        data_list.append((row[0], row[1], row[2], row[3], row[4], grouptag, groupdname, zjid, zpurl,
                          row[5], row[6]))
    db.close()

    return data_headers, data_list, source_path
