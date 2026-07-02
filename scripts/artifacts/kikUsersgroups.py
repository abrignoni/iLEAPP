__artifacts_v2__ = {
    "kikUsersgroups": {
        "name": "Kik Users in Groups",
        "description": "Kik users that are members of a group (kik.sqlite)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-06-22",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Kik",
        "notes": "",
        "paths": ('*/kik.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "users"
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def kikUsersgroups(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    data_headers = ('User ID', 'Display Name', 'Username', 'Profile Pic URL', 'Member Group ID',
                    'Group Tag', 'Group Name', 'Group ID', 'Group Pic URL', 'Blob',
                    'Additional Information')
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
        Z_9MEMBERS.Z_9MEMBERSINVERSE,
        ZKIKUSEREXTRA.ZENTITYUSERDATA,
        ZKIKUSEREXTRA.ZROSTERENTRYDATA
    FROM ZKIKUSER
        INNER JOIN Z_9MEMBERS ON ZKIKUSER.Z_PK = Z_9MEMBERS.Z_9MEMBERS
        LEFT JOIN ZKIKUSEREXTRA ON ZKIKUSER.Z_PK = ZKIKUSEREXTRA.ZUSER
    ORDER BY Z_9MEMBERSINVERSE
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
