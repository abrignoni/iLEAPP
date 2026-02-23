from packaging import version

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone, iOS


@artifact_processor
def get_interactionC_contacts(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.db'):
            break

    db = open_sqlite_db_readonly(file_found)

    iOSversion = iOS.get_version()
    if version.parse(iOSversion) < version.parse("10"):
        db.close()
        return (), [], file_found

    cursor = db.cursor()
    cursor.execute('''
    select
    datetime(zinteractions.zstartdate + 978307200, 'unixepoch'),
    datetime(zinteractions.zenddate + 978307200, 'unixepoch'),
    zinteractions.zbundleid,
    zcontacts.zdisplayname,
    zcontacts.zidentifier,
    zinteractions.zdirection,
    zinteractions.zisresponse,
    zinteractions.zrecipientcount,
    datetime(zinteractions.zcreationdate + 978307200, 'unixepoch'),
    datetime(zcontacts.zcreationdate + 978307200, 'unixepoch'),
    zinteractions.zcontenturl
    from
    zinteractions
    left join
    zcontacts
    on zinteractions.zsender = zcontacts.z_pk
    ''')

    all_rows = cursor.fetchall()
    data_list = []

    for row in all_rows:
        starttime = convert_ts_human_to_utc(row[0])
        starttime = convert_utc_human_to_timezone(starttime,timezone_offset)

        endtime = convert_ts_human_to_utc(row[1])
        endtime = convert_utc_human_to_timezone(endtime,timezone_offset)

        zinteractcreated = convert_ts_human_to_utc(row[8])
        zinteractcreated = convert_utc_human_to_timezone(zinteractcreated,timezone_offset)

        zcontactscreated = row[9]
        if zcontactscreated is None:
            zcontactscreated = ''
        else:
            zcontactscreated = convert_ts_human_to_utc(zcontactscreated)
            zcontactscreated = convert_utc_human_to_timezone(zcontactscreated,timezone_offset)

        data_list.append((starttime,endtime,row[2],row[3],row[4],row[5],row[6],row[7],zinteractcreated,zcontactscreated,row[10]))

    db.close()
    data_headers = ('Start Date','End Date','Bundle ID','Display Name','Identifier','Direction','Is Response','Recipient Count','Zinteractions Creation Date','Zcontacts Creation Date','Content URL')
    return data_headers, data_list, file_found


@artifact_processor
def get_interactionC_attachments(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.db'):
            break

    db = open_sqlite_db_readonly(file_found)

    iOSversion = iOS.get_version()
    if version.parse(iOSversion) < version.parse("10"):
        db.close()
        return (), [], file_found

    cursor = db.cursor()
    cursor.execute('''
    select
        datetime(zinteractions.ZCREATIONDATE + 978307200, 'unixepoch'),
        ZINTERACTIONS.zbundleid,
        ZINTERACTIONS.ztargetbundleid,
        ZINTERACTIONS.zuuid,
        ZATTACHMENT.zcontenttext,
        ZATTACHMENT.zuti,
        ZATTACHMENT.zcontenturl
        from zinteractions
        inner join z_1interactions
        on zinteractions.z_pk = z_1interactions.z_3interactions
        inner join zattachment on z_1interactions.z_1attachments = zattachment.z_pk
    ''')

    all_rows = cursor.fetchall()
    data_list = []

    for row in all_rows:
        creationdate = convert_ts_human_to_utc(row[0])
        creationdate = convert_utc_human_to_timezone(creationdate,timezone_offset)

        data_list.append((creationdate,row[1],row[2],row[3],row[4],row[5],row[6]))

    db.close()
    data_headers = ('Creation Date', 'Bundle ID', 'Target Bundle ID', 'ZUUID', 'Content Text', 'Uniform Type ID', 'Content URL')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_interactionC_contacts": {
        "name": "InteractionC - Contacts",
        "description": "",
        "author": "",
        "version": "0.2",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "InteractionC",
        "notes": "",
        "paths": ('**/interactionC.db*'),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    },
    "get_interactionC_attachments": {
        "name": "InteractionC - Attachments",
        "description": "",
        "author": "",
        "version": "0.2",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "InteractionC",
        "notes": "",
        "paths": ('**/interactionC.db*'),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
