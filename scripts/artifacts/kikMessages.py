from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, media_to_html


@artifact_processor
def get_kikMessages(files_found, report_folder, seeker, wrap_text, timezone_offset):

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.sqlite'):
            break

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime(ZKIKMESSAGE.ZRECEIVEDTIMESTAMP +978307200,'UNIXEPOCH') AS RECEIVEDTIME,
    datetime(ZKIKMESSAGE.ZTIMESTAMP +978307200,'UNIXEPOCH') as TIMESTAMP,
    ZKIKMESSAGE.ZBODY,
    case ZKIKMESSAGE.ZTYPE
        when 1 then 'Received'
        when 2 then 'Sent'
        when 3 then 'Group Admin'
        when 4 then 'Group Message'
        else 'Unknown' end as 'Type',
    ZKIKMESSAGE.ZUSER,
    ZKIKUSER.ZDISPLAYNAME,
    ZKIKUSER.ZUSERNAME,
    ZKIKATTACHMENT.ZCONTENT
    from ZKIKMESSAGE
    left join ZKIKUSER on ZKIKMESSAGE.ZUSER = ZKIKUSER.Z_PK
    left join ZKIKATTACHMENT on ZKIKMESSAGE.Z_PK = ZKIKATTACHMENT.ZMESSAGE
    ''')

    all_rows = cursor.fetchall()
    data_list = []

    for row in all_rows:
        attachmentName = str(row[7])
        thumb = media_to_html(attachmentName, files_found, report_folder)
        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], thumb))

    db.close()
    data_headers = ('Received Time', 'Timestamp', 'Message', 'Type', 'User', 'Display Name', 'User Name','Attachment Name','Attachment')
    return data_headers, data_list, file_found


@artifact_processor
def get_kikUsers(files_found, report_folder, seeker, wrap_text, timezone_offset):

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.sqlite'):
            break

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    Z_PK,
    ZDISPLAYNAME,
    ZUSERNAME,
    ZEMAIL,
    ZJID,
    ZFIRSTNAME,
    ZLASTNAME,
    datetime(ZPPTIMESTAMP/1000,'unixepoch'),
    ZPPURL
    FROM ZKIKUSER
    ''')

    all_rows = cursor.fetchall()
    data_list = []

    for row in all_rows:
        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))

    db.close()
    data_headers = ('PK','Display Name','User Name','Email','JID','First Name','Last Name','Profile Pic Timestamp','Profile Pic URL')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_kikMessages": {
        "name": "Kik Messages",
        "description": "",
        "author": "",
        "version": "0.2",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Kik",
        "notes": "",
        "paths": ('**/kik.sqlite*','*/mobile/Containers/Shared/AppGroup/*/cores/private/*/content_manager/data_cache/*'),
        "output_types": "all",
        "artifact_icon": "alert-triangle",
        "html_columns": ["Attachment"]
    },
    "get_kikUsers": {
        "name": "Kik Users",
        "description": "",
        "author": "",
        "version": "0.2",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Kik",
        "notes": "",
        "paths": ('**/kik.sqlite*'),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
