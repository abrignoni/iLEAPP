import blackboxprotobuf

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_kikGroupadmins(files_found, report_folder, seeker, wrap_text, timezone_offset):
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
        Z_9ADMINSINVERSE.Z_9ADMINSINVERSE,
        ZKIKUSEREXTRA.ZENTITYUSERDATA,
        ZKIKUSEREXTRA.ZROSTERENTRYDATA
    From ZKIKUSER
    Inner Join Z_9ADMINSINVERSE On ZKIKUSER.Z_PK = Z_9ADMINSINVERSE.Z_9ADMINS
    LEFT JOIN ZKIKUSEREXTRA On ZKIKUSER.Z_PK = ZKIKUSEREXTRA.ZUSER
    order by Z_9ADMINSINVERSE
    ''')

    all_rows = cursor.fetchall()
    data_list = []
    finalintlist = ''
    blobuser = ''
    blobdesc = ''
    addinfousera = ''
    addinfouserb = ''
    addinfodisp = ''
    addinfdesc = ''

    for row in all_rows:
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

        if row[6] is not None:
            addinfousera = ''
            addinfouserb = ''
            addinfodisp = ''
            addinfdesc = ''

            data, typess = blackboxprotobuf.decode_message(row[6])
            addinfousera = data['1']['1']
            if isinstance(addinfousera, dict):
                addinfousera = ''
            else:
                addinfousera = data['1']['1'].decode('utf-8')

            if data.get('2') is not None:
                addinfdesc = data.get('2')['1']['1']
                if isinstance(addinfdesc, dict):
                    addinfdesc = ''
                else:
                    addinfdesc = data.get('2')['1']['1'].decode('utf-8')

            addinfouserb = data['3']['1'].decode('utf-8')

            addinfodisp = data['4']['1']
            if isinstance(addinfodisp, dict):
                addinfodisp = ''
            else:
                addinfodisp = data['4']['1'].decode('utf-8')

        if row[5] is not None:
            finalintlist = ''
            blobuser = ''
            blobdesc = ''

            data, typess = blackboxprotobuf.decode_message(row[5])

            if (data['1'].get('5')) is not None:
                listofinterests = (data['1']['5']['1'])
                for x in listofinterests:
                    finalintlist = (x['2'].decode('utf-8')) + ', ' + finalintlist
                finalintlist = finalintlist[:-2]

            if isinstance(data['1'].get('1'), bytes):
                blobuser = (data['1'].get('1').decode('utf-8'))
            if isinstance(data['1'].get('1'), dict):
                if (data['1']['1'].get('1')) is not None:
                    blobdesc = (data['1']['1'].get('1').decode('utf-8'))

            if (data['1'].get('7')) is not None:
                if isinstance(data['1']['7'].get('1'), dict):
                    pass
                else:
                    blobname = ((data['1']['7'].get('1').decode('utf-8')))
            if (data.get('102')) is not None:
                blobpicfull = (data['102']['1']['2']['1'].decode('utf-8'))
                blobpicthu = (data['102']['1']['2']['2'].decode('utf-8'))
            if (data.get('104')) is not None:
                listofinterests = data['104']['1']
                for x in listofinterests:
                    finalintlist = (x['2'].decode('utf-8')) + ', ' + finalintlist
                finalintlist = finalintlist[:-2]

        data_list.append((row[0], row[1], row[2], row[3], row[4], grouptag, groupdname, zjid, zpurl,
                         blobuser, blobdesc, finalintlist, addinfousera, addinfouserb, addinfodisp, addinfdesc))

    db.close()

    data_headers = ('User ID', 'Display Name', 'Username', 'Profile Pic URL', 'Member Group ID',
                    'Group Tag', 'Group Name', 'Group ID', 'Group Pic URL', 'Blob User',
                    'Blob Description', 'Blob Interests', 'Additional Info User',
                    'Additional Info User', 'Additional Info Display', 'Additional Info Value')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_kikGroupadmins": {
        "name": "Kik Group Administrators",
        "description": "Kik users that are Administrators of a group.",
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
