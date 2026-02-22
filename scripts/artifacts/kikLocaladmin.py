from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_kikLocaladmin(files_found, report_folder, seeker, wrap_text, timezone_offset):
    file_found = str(files_found[0])
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('kik.sqlite'):
            break

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    Select ZKIKUSER.Z_PK,
        ZKIKUSER.ZDISPLAYNAME,
        ZKIKUSER.ZUSERNAME,
        ZKIKUSER.ZPPURL,
        Z_9MEMBERS.Z_9MEMBERSINVERSE,
        Z_9ADMINSINVERSE.Z_9ADMINSINVERSE,
        ZKIKUSEREXTRA.ZENTITYUSERDATA,
        ZKIKUSEREXTRA.ZROSTERENTRYDATA
    From ZKIKUSER
        LEFT Join Z_9MEMBERS On ZKIKUSER.Z_PK = Z_9MEMBERS.Z_9MEMBERS
        Left Join Z_9ADMINSINVERSE On ZKIKUSER.Z_PK = Z_9ADMINSINVERSE.Z_9ADMINS
        LEFT JOIN ZKIKUSEREXTRA On ZKIKUSER.Z_PK = ZKIKUSEREXTRA.ZUSER
    WHERE ZKIKUSER.ZFIRSTNAME OR ZKIKUSER.ZLASTNAME <> ""
    ''')

    all_rows = cursor.fetchall()
    data_list = []

    for row in all_rows:
        if row[4] is None:
            grouptag = groupdname = zjid = zpurl = ''
        else:
            cursor2 = db.cursor()
            cursor2.execute('''
            SELECT ZGROUPTAG,
                ZDISPLAYNAME,
                ZJID,
                ZPPURL
            FROM ZKIKUSER
            WHERE Z_PK = ?
            ''', (row[4],))

            all_rows2 = cursor2.fetchall()
            grouptag = groupdname = zjid = zpurl = ''
            for rows2 in all_rows2:
                grouptag = rows2[0]
                groupdname = rows2[1]
                zjid = rows2[2]
                zpurl = rows2[3]

        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], grouptag, groupdname, zjid, zpurl, row[6], row[7]))

    db.close()

    data_headers = ('User ID', 'Display Name', 'Username', 'Profile Pic URL', 'Member Group ID',
                    'Administrator Group ID', 'Group Tag', 'Group Name', 'Group ID', 'Group Pic URL',
                    'Blob', 'Additional Information')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_kikLocaladmin": {
        "name": "Kik Local Account",
        "description": "Kik Local Account.",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Kik",
        "notes": "",
        "paths": ('*/kik.sqlite*',),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
