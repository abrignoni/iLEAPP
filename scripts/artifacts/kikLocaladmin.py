__artifacts_v2__ = {
    "kikLocaladmin": {
        "name": "Kik Local Account",
        "description": "Kik local account users from kik.sqlite",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-06-22",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Kik",
        "notes": "",
        "paths": ('*/kik.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "felix_ios17": "iOS 17.6.1 | Kik Messaging & Chat App 17.0.0 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Kik Messaging & Chat App 16.9.3 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Kik Messaging & Chat App 17.11.3 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Kik Messaging & Chat App 16.16.1 | 1 row",
            "felix23_ios16": "iOS 16.5 | Kik Messaging & Chat App 16.9.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | Kik 15.21.2 | 1 row",
            "hickman_ios14": "iOS 14.3 | Kik 15.25.1 | 1 row",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def kikLocaladmin(context):
    data_headers = ('User ID', 'Display Name', 'Username', 'Profile Pic URL', 'Member Group ID',
                    'Administrator Group ID', 'Group Tag', 'Group Name', 'Group ID', 'Group Pic URL',
                    'Blob', 'Additional Information')
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
    cursor.execute('''
    SELECT ZKIKUSER.Z_PK,
        ZKIKUSER.ZDISPLAYNAME,
        ZKIKUSER.ZUSERNAME,
        ZKIKUSER.ZPPURL,
        Z_9MEMBERS.Z_9MEMBERSINVERSE,
        Z_9ADMINSINVERSE.Z_9ADMINSINVERSE,
        ZKIKUSEREXTRA.ZENTITYUSERDATA,
        ZKIKUSEREXTRA.ZROSTERENTRYDATA
    FROM ZKIKUSER
        LEFT JOIN Z_9MEMBERS ON ZKIKUSER.Z_PK = Z_9MEMBERS.Z_9MEMBERS
        LEFT JOIN Z_9ADMINSINVERSE ON ZKIKUSER.Z_PK = Z_9ADMINSINVERSE.Z_9ADMINS
        LEFT JOIN ZKIKUSEREXTRA ON ZKIKUSER.Z_PK = ZKIKUSEREXTRA.ZUSER
    WHERE ZKIKUSER.ZFIRSTNAME OR ZKIKUSER.ZLASTNAME <> ""
    ''')

    for row in cursor.fetchall():
        grouptag = groupdname = zjid = zpurl = ''
        if row[4] is not None:
            cursor2 = db.cursor()
            cursor2.execute('SELECT ZGROUPTAG, ZDISPLAYNAME, ZJID, ZPPURL FROM ZKIKUSER WHERE Z_PK = ?',
                            (row[4],))
            for rows2 in cursor2.fetchall():
                grouptag, groupdname, zjid, zpurl = rows2[0], rows2[1], rows2[2], rows2[3]
        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], grouptag, groupdname, zjid,
                          zpurl, row[6], row[7]))
    db.close()

    return data_headers, data_list, source_path
