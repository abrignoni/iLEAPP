__artifacts_v2__ = {
'Ph034iCloudSharedLinkRecordswithNADPhDaPsql': {
'name': 'Ph034-iCloud Shared Link Records with NAD-PhDaPsql',
'description': 'Share and participant records from PhotoData/Photos.sqlite with stored ZSHARE.ZSCOPETYPE 2. A share with multiple participants appears on multiple rows; no asset data is parsed. Queries support iOS 14 through 25, with unsupported versions returning no rows. Enum fields report raw stored values. Registered real samples have returned no qualifying rows.',
'author': '@AlexisBrignoni, Codex',
'creation_date': '2026-05-28',
'last_update_date': '2026-10-10',
'version': '6.0',
'date': '2026-05-27',
'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
'category': 'Photos.sqlite',
'notes': 'Original parser and Photos.sqlite research: Scott Koenig, https://theforensicscooter.com/2024/05/18/ileapp-parsers-photos-sqlite-queries/. Raw enum projections preserve stored NULL and unknown values; per-value interpretations are not emitted.',
'paths': ('*/PhotoData/Photos.sqlite*',),
"output_types": ["standard", "tsv", "none"],
"artifact_icon": "link",
'sample_data': {
'ctf2020_ios12': 'iOS 12.4 | not queried, the code returns before reading the database on versions below iOS 14',
'dexter_ios18': 'iOS 18.3.2 | 0 rows',
'felix_ios17': 'iOS 17.6.1 | 0 rows',
'fsfull002_ios17': 'iOS 17.1 | 0 rows',
'hc_ios18_7': 'iOS 18.7.8 | 0 rows',
'iphone11_ios17': 'iOS 17.3 | 0 rows',
'iphone12_ios18': 'iOS 18.7 | 0 rows',
'iphone14plus_ios18': 'iOS 18.0 | 0 rows',
'otto_ios17': 'iOS 17.5.1 | 0 rows',
'abe_ios16': 'iOS 16.5 | 0 rows',
'felix23_ios16': 'iOS 16.5 | 0 rows',
'hickman_ios13': 'iOS 13.3.1 | not queried, the code returns before reading the database on versions below iOS 14',
'hickman_ios14': 'iOS 14.3 | 0 rows',
'jess_ios15': 'iOS 15.0.2 | 0 rows',
'magnet_ios16': 'iOS 16.1.1 | 0 rows',
}
}
}

import os
from packaging import version
from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, null_absent_columns, logfunc, iOS

@artifact_processor
def Ph034iCloudSharedLinkRecordswithNADPhDaPsql(context):
    files_found = context.get_files_found()
    report_folder = context.get_report_folder()
    source_path = ''
    for source_path in files_found:
        source_path = str(source_path)

        if source_path.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = iOS.get_version()
    if not iosversion:
        logfunc("No iOS version had been read when this artifact ran, Photos.sqlite was not queried")
        return (), [], source_path
    if (version.parse(iosversion) < version.parse("14")) or (version.parse(iosversion) >= version.parse("26")):
        logfunc("Unsupported version for PhotoData-Photos.sqlite from iOS " + iosversion)
        return (), [], source_path
    if (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("16")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zShare.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Creation Date',
        DateTime(zShare.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Start Date',
        DateTime(zShare.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-End Date',
        DateTime(zShare.ZEXPIRYDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Expiry Date',
        zShare.ZUUID AS 'zShare-UUID',
        zShare.ZORIGINATINGSCOPEIDENTIFIER AS 'zShare-Originating Scope ID',
        zShare.ZSTATUS AS 'zShare-ZSTATUS Raw Value',
        zShare.ZSCOPETYPE AS 'zShare-ZSCOPETYPE Raw Value',
        zShare.ZASSETCOUNT AS 'zShare-Asset Count-CMM',
        zShare.ZFORCESYNCATTEMPTED AS 'zShare-Force Sync Attempted-CMM',  
        zShare.ZPHOTOSCOUNT AS 'zShare-Photos Count-CMM',
        zShare.ZUPLOADEDPHOTOSCOUNT AS 'zShare-Uploaded Photos Count-CMM',
        zShare.ZVIDEOSCOUNT AS 'zShare-Videos Count-CMM',
        zShare.ZUPLOADEDVIDEOSCOUNT AS 'zShare-Uploaded Videos Count-CMM',
        zShare.ZSCOPEIDENTIFIER AS 'zShare-Scope ID',
        zShare.ZTITLE AS 'zShare-Title-SPL',
        zShare.ZSHAREURL AS 'zShare-Share URL',
        zShare.ZLOCALPUBLISHSTATE AS 'zShare-ZLOCALPUBLISHSTATE Raw Value',
        zShare.ZPUBLICPERMISSION AS 'zShare-ZPUBLICPERMISSION Raw Value',
        zSharePartic.ZACCEPTANCESTATUS AS 'zSharePartic-ZACCEPTANCESTATUS Raw Value',
        zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
        zSharePartic.Z_PK AS 'zSharePartic-zPK',
        zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
        zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',
        zSharePartic.ZISCURRENTUSER AS 'zSharePartic-ZISCURRENTUSER Raw Value',
        zSharePartic.ZROLE AS 'zSharePartic-ZROLE Raw Value',
        zSharePartic.ZPERMISSION AS 'zSharePartic-ZPERMISSION Raw Value',
        zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION AS 'zShare-ZSHOULDNOTIFYONUPLOADCOMPLETION Raw Value',
        zShare.ZSHOULDIGNOREBUDGETS AS 'zShare-ZSHOULDIGNOREBUDGETS Raw Value',
        zShare.ZTRASHEDSTATE AS 'zShare-ZTRASHEDSTATE Raw Value',
        zShare.ZCLOUDDELETESTATE AS 'zShare-ZCLOUDDELETESTATE Raw Value',
        zShare.Z_ENT AS 'zShare-Z_ENT Raw Value'
        FROM ZSHARE zShare
            LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
        WHERE zShare.ZSCOPETYPE = 2
        ORDER BY zShare.ZCREATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
            row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
            row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
            row[28], row[29], row[30], row[31]))

        data_headers = (('zShare-Creation Date-0', 'datetime'),
        ('zShare-Start Date-1', 'datetime'),
        ('zShare-End Date-2', 'datetime'),
        ('zShare-Expiry Date-3', 'datetime'),
        'zShare-UUID-4',
        'zShare-Originating Scope ID-5',
        'zShare-ZSTATUS Raw Value-6',
        'zShare-ZSCOPETYPE Raw Value-7',
        'zShare-Asset Count-CMM-8',
        'zShare-Force Sync Attempted-CMM-9',
        'zShare-Photos Count-CMM-10',
        'zShare-Uploaded Photos Count-CMM-11',
        'zShare-Videos Count-CMM-12',
        'zShare-Uploaded Videos Count-CMM-13',
        'zShare-Scope ID-14',
        'zShare-Title-SPL-15',
        'zShare-Share URL-16',
        'zShare-ZLOCALPUBLISHSTATE Raw Value-17',
        'zShare-ZPUBLICPERMISSION Raw Value-18',
        'zSharePartic-ZACCEPTANCESTATUS Raw Value-19',
        'zSharePartic-User ID-20',
        'zSharePartic-zPK-21',
        'zSharePartic-Email Address-22',
        'zSharePartic-Phone Number-23',
        'zSharePartic-ZISCURRENTUSER Raw Value-24',
        'zSharePartic-ZROLE Raw Value-25',
        'zSharePartic-ZPERMISSION Raw Value-26',
        'zShare-ZSHOULDNOTIFYONUPLOADCOMPLETION Raw Value-27',
        'zShare-ZSHOULDIGNOREBUDGETS Raw Value-28',
        'zShare-ZTRASHEDSTATE Raw Value-29',
        'zShare-ZCLOUDDELETESTATE Raw Value-30',
        'zShare-Z_ENT Raw Value-31')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("17.6")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zShare.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Creation Date',
        DateTime(zShare.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Start Date',
        DateTime(zShare.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-End Date',
        DateTime(zShare.ZEXPIRYDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Expiry Date',  
        zShare.ZUUID AS 'zShare-UUID',
        zShare.ZORIGINATINGSCOPEIDENTIFIER AS 'zShare-Originating Scope ID',
        zSharePartic.Z54_SHARE AS 'zSharePartic-Z54_SHARE Raw Value',
        zShare.ZSTATUS AS 'zShare-ZSTATUS Raw Value',
        zShare.ZSCOPETYPE AS 'zShare-ZSCOPETYPE Raw Value',
        zShare.ZASSETCOUNT AS 'zShare-Asset Count-CMM',
        zShare.ZFORCESYNCATTEMPTED AS 'zShare-Force Sync Attempted-CMM',  
        zShare.ZPHOTOSCOUNT AS 'zShare-Photos Count-CMM',
        zShare.ZUPLOADEDPHOTOSCOUNT AS 'zShare-Uploaded Photos Count-CMM',
        zShare.ZVIDEOSCOUNT AS 'zShare-Videos Count-CMM',
        zShare.ZUPLOADEDVIDEOSCOUNT AS 'zShare-Uploaded Videos Count-CMM',  
        zShare.ZSCOPEIDENTIFIER AS 'zShare-Scope ID',
        zShare.ZTITLE AS 'zShare-Title-SPL',
        zShare.ZSHAREURL AS 'zShare-Share URL',
        zShare.ZLOCALPUBLISHSTATE AS 'zShare-ZLOCALPUBLISHSTATE Raw Value',
        zShare.ZPUBLICPERMISSION AS 'zShare-ZPUBLICPERMISSION Raw Value',
        zShare.ZCLOUDLOCALSTATE AS 'zShare-ZCLOUDLOCALSTATE Raw Value',
        zShare.ZSCOPESYNCINGSTATE AS 'zShare-ZSCOPESYNCINGSTATE Raw Value',
        zShare.ZAUTOSHAREPOLICY AS 'zShare-ZAUTOSHAREPOLICY Raw Value',
        zSharePartic.ZACCEPTANCESTATUS AS 'zSharePartic-ZACCEPTANCESTATUS Raw Value',
        zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
        zSharePartic.Z_PK AS 'zSharePartic-zPK',
        zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
        zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',
        zSharePartic.ZPARTICIPANTID AS 'zSharePartic-Participant ID',
        zSharePartic.ZUUID AS 'zSharePartic-UUID',  
        zSharePartic.ZISCURRENTUSER AS 'zSharePartic-ZISCURRENTUSER Raw Value',
        zSharePartic.ZROLE AS 'zSharePartic-ZROLE Raw Value',
        zSharePartic.ZPERMISSION AS 'zSharePartic-ZPERMISSION Raw Value',
        zShare.ZPARTICIPANTCLOUDUPDATESTATE AS 'zShare-ZPARTICIPANTCLOUDUPDATESTATE Raw Value',
        zSharePartic.ZEXITSTATE AS 'zSharePartic-ZEXITSTATE Raw Value',
        zShare.ZPREVIEWSTATE AS 'zShare-ZPREVIEWSTATE Raw Value',
        zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION AS 'zShare-ZSHOULDNOTIFYONUPLOADCOMPLETION Raw Value',
        zShare.ZSHOULDIGNOREBUDGETS AS 'zShare-ZSHOULDIGNOREBUDGETS Raw Value',
        zShare.ZEXITSOURCE AS 'zShare-ZEXITSOURCE Raw Value',
        zShare.ZEXITSTATE AS 'zShare-ZEXITSTATE Raw Value',
        zShare.ZEXITTYPE AS 'zShare-ZEXITTYPE Raw Value',
        zShare.ZTRASHEDSTATE AS 'zShare-ZTRASHEDSTATE Raw Value',
        zShare.ZCLOUDDELETESTATE AS 'zShare-ZCLOUDDELETESTATE Raw Value',
        DateTime(zShare.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Trashed Date',
        DateTime(zShare.ZLASTPARTICIPANTASSETTRASHNOTIFICATIONDATE + 978307200, 'UNIXEPOCH') AS
         'zShare-LastParticipant Asset Trash Notification Date',
        DateTime(zShare.ZLASTPARTICIPANTASSETTRASHNOTIFICATIONVIEWEDDATE + 978307200, 'UNIXEPOCH') AS
         'zShare-Last Participant Asset Trash Notification View Date',
        zShare.Z_ENT AS 'zShare-Z_ENT Raw Value'
        FROM ZSHARE zShare
            LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
        WHERE zShare.ZSCOPETYPE = 2
        ORDER BY zShare.ZCREATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
            row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16],
            row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25],
            row[26], row[27], row[28], row[29], row[30], row[31], row[32], row[33], row[34],
            row[35], row[36], row[37], row[38], row[39], row[40], row[41], row[42], row[43],
            row[44], row[45], row[46]))

        data_headers = (('zShare-Creation Date-0', 'datetime'),
        ('zShare-Start Date-1', 'datetime'),
        ('zShare-End Date-2', 'datetime'),
        ('zShare-Expiry Date-3', 'datetime'),
        'zShare-UUID-4',
        'zShare-Originating Scope ID-5',
        'zSharePartic-Z54_SHARE Raw Value-6',
        'zShare-ZSTATUS Raw Value-7',
        'zShare-ZSCOPETYPE Raw Value-8',
        'zShare-Asset Count-CMM-9',
        'zShare-Force Sync Attempted-CMM-10',
        'zShare-Photos Count-CMM-11',
        'zShare-Uploaded Photos Count-CMM-12',
        'zShare-Videos Count-CMM-13',
        'zShare-Uploaded Videos Count-CMM-14',
        'zShare-Scope ID-15',
        'zShare-Title-SPL-16',
        'zShare-Share URL-17',
        'zShare-ZLOCALPUBLISHSTATE Raw Value-18',
        'zShare-ZPUBLICPERMISSION Raw Value-19',
        'zShare-ZCLOUDLOCALSTATE Raw Value-20',
        'zShare-ZSCOPESYNCINGSTATE Raw Value-21',
        'zShare-ZAUTOSHAREPOLICY Raw Value-22',
        'zSharePartic-ZACCEPTANCESTATUS Raw Value-23',
        'zSharePartic-User ID-24',
        'zSharePartic-zPK-25',
        'zSharePartic-Email Address-26',
        'zSharePartic-Phone Number-27',
        'zSharePartic-Participant ID-28',
        'zSharePartic-UUID-29',
        'zSharePartic-ZISCURRENTUSER Raw Value-30',
        'zSharePartic-ZROLE Raw Value-31',
        'zSharePartic-ZPERMISSION Raw Value-32',
        'zShare-ZPARTICIPANTCLOUDUPDATESTATE Raw Value-33',
        'zSharePartic-ZEXITSTATE Raw Value-34',
        'zShare-ZPREVIEWSTATE Raw Value-35',
        'zShare-ZSHOULDNOTIFYONUPLOADCOMPLETION Raw Value-36',
        'zShare-ZSHOULDIGNOREBUDGETS Raw Value-37',
        'zShare-ZEXITSOURCE Raw Value-38',
        'zShare-ZEXITSTATE Raw Value-39',
        'zShare-ZEXITTYPE Raw Value-40',
        'zShare-ZTRASHEDSTATE Raw Value-41',
        'zShare-ZCLOUDDELETESTATE Raw Value-42',
        ('zShare-Trashed Date-43', 'datetime'),
        ('zShare-LastParticipant Asset Trash Notification Date-44', 'datetime'),
        ('zShare-Last Participant Asset Trash Notification View Date-45', 'datetime'),
        'zShare-Z_ENT Raw Value-46')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("17.6")) & (version.parse(iosversion) < version.parse("18")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zShare.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Creation Date',
        DateTime(zShare.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Start Date',
        DateTime(zShare.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-End Date',
        DateTime(zShare.ZEXPIRYDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Expiry Date',  
        zShare.ZUUID AS 'zShare-UUID',
        zShare.ZORIGINATINGSCOPEIDENTIFIER AS 'zShare-Originating Scope ID',
        zSharePartic.Z55_SHARE AS 'zSharePartic-Z55_SHARE Raw Value',
        zShare.ZSTATUS AS 'zShare-ZSTATUS Raw Value',
        zShare.ZSCOPETYPE AS 'zShare-ZSCOPETYPE Raw Value',
        zShare.ZASSETCOUNT AS 'zShare-Asset Count-CMM',
        zShare.ZFORCESYNCATTEMPTED AS 'zShare-Force Sync Attempted-CMM',  
        zShare.ZPHOTOSCOUNT AS 'zShare-Photos Count-CMM',
        zShare.ZUPLOADEDPHOTOSCOUNT AS 'zShare-Uploaded Photos Count-CMM',
        zShare.ZVIDEOSCOUNT AS 'zShare-Videos Count-CMM',
        zShare.ZUPLOADEDVIDEOSCOUNT AS 'zShare-Uploaded Videos Count-CMM',  
        zShare.ZSCOPEIDENTIFIER AS 'zShare-Scope ID',
        zShare.ZTITLE AS 'zShare-Title-SPL',
        zShare.ZSHAREURL AS 'zShare-Share URL',
        zShare.ZLOCALPUBLISHSTATE AS 'zShare-ZLOCALPUBLISHSTATE Raw Value',
        zShare.ZPUBLICPERMISSION AS 'zShare-ZPUBLICPERMISSION Raw Value',
        zShare.ZCLOUDLOCALSTATE AS 'zShare-ZCLOUDLOCALSTATE Raw Value',
        zShare.ZSCOPESYNCINGSTATE AS 'zShare-ZSCOPESYNCINGSTATE Raw Value',
        zShare.ZAUTOSHAREPOLICY AS 'zShare-ZAUTOSHAREPOLICY Raw Value',
        zSharePartic.ZACCEPTANCESTATUS AS 'zSharePartic-ZACCEPTANCESTATUS Raw Value',
        zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
        zSharePartic.Z_PK AS 'zSharePartic-zPK',
        zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
        zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',
        zSharePartic.ZPARTICIPANTID AS 'zSharePartic-Participant ID',
        zSharePartic.ZUUID AS 'zSharePartic-UUID',  
        zSharePartic.ZISCURRENTUSER AS 'zSharePartic-ZISCURRENTUSER Raw Value',
        zSharePartic.ZROLE AS 'zSharePartic-ZROLE Raw Value',
        zSharePartic.ZPERMISSION AS 'zSharePartic-ZPERMISSION Raw Value',
        zShare.ZPARTICIPANTCLOUDUPDATESTATE AS 'zShare-ZPARTICIPANTCLOUDUPDATESTATE Raw Value',
        zSharePartic.ZEXITSTATE AS 'zSharePartic-ZEXITSTATE Raw Value',
        zShare.ZPREVIEWSTATE AS 'zShare-ZPREVIEWSTATE Raw Value',
        zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION AS 'zShare-ZSHOULDNOTIFYONUPLOADCOMPLETION Raw Value',
        zShare.ZSHOULDIGNOREBUDGETS AS 'zShare-ZSHOULDIGNOREBUDGETS Raw Value',
        zShare.ZEXITSOURCE AS 'zShare-ZEXITSOURCE Raw Value',
        zShare.ZEXITSTATE AS 'zShare-ZEXITSTATE Raw Value',
        zShare.ZEXITTYPE AS 'zShare-ZEXITTYPE Raw Value',
        zShare.ZTRASHEDSTATE AS 'zShare-ZTRASHEDSTATE Raw Value',
        zShare.ZCLOUDDELETESTATE AS 'zShare-ZCLOUDDELETESTATE Raw Value',
        DateTime(zShare.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Trashed Date',
        DateTime(zShare.ZLASTPARTICIPANTASSETTRASHNOTIFICATIONDATE + 978307200, 'UNIXEPOCH') AS
         'zShare-LastParticipant Asset Trash Notification Date',
        DateTime(zShare.ZLASTPARTICIPANTASSETTRASHNOTIFICATIONVIEWEDDATE + 978307200, 'UNIXEPOCH') AS
         'zShare-Last Participant Asset Trash Notification View Date',
        zShare.Z_ENT AS 'zShare-Z_ENT Raw Value'
        FROM ZSHARE zShare
            LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
        WHERE zShare.ZSCOPETYPE = 2
        ORDER BY zShare.ZCREATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
            row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16],
            row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25],
            row[26], row[27], row[28], row[29], row[30], row[31], row[32], row[33], row[34],
            row[35], row[36], row[37], row[38], row[39], row[40], row[41], row[42], row[43],
            row[44], row[45], row[46]))

        data_headers = (('zShare-Creation Date-0', 'datetime'),
        ('zShare-Start Date-1', 'datetime'),
        ('zShare-End Date-2', 'datetime'),
        ('zShare-Expiry Date-3', 'datetime'),
        'zShare-UUID-4',
        'zShare-Originating Scope ID-5',
        'zSharePartic-Z55_SHARE Raw Value-6',
        'zShare-ZSTATUS Raw Value-7',
        'zShare-ZSCOPETYPE Raw Value-8',
        'zShare-Asset Count-CMM-9',
        'zShare-Force Sync Attempted-CMM-10',
        'zShare-Photos Count-CMM-11',
        'zShare-Uploaded Photos Count-CMM-12',
        'zShare-Videos Count-CMM-13',
        'zShare-Uploaded Videos Count-CMM-14',
        'zShare-Scope ID-15',
        'zShare-Title-SPL-16',
        'zShare-Share URL-17',
        'zShare-ZLOCALPUBLISHSTATE Raw Value-18',
        'zShare-ZPUBLICPERMISSION Raw Value-19',
        'zShare-ZCLOUDLOCALSTATE Raw Value-20',
        'zShare-ZSCOPESYNCINGSTATE Raw Value-21',
        'zShare-ZAUTOSHAREPOLICY Raw Value-22',
        'zSharePartic-ZACCEPTANCESTATUS Raw Value-23',
        'zSharePartic-User ID-24',
        'zSharePartic-zPK-25',
        'zSharePartic-Email Address-26',
        'zSharePartic-Phone Number-27',
        'zSharePartic-Participant ID-28',
        'zSharePartic-UUID-29',
        'zSharePartic-ZISCURRENTUSER Raw Value-30',
        'zSharePartic-ZROLE Raw Value-31',
        'zSharePartic-ZPERMISSION Raw Value-32',
        'zShare-ZPARTICIPANTCLOUDUPDATESTATE Raw Value-33',
        'zSharePartic-ZEXITSTATE Raw Value-34',
        'zShare-ZPREVIEWSTATE Raw Value-35',
        'zShare-ZSHOULDNOTIFYONUPLOADCOMPLETION Raw Value-36',
        'zShare-ZSHOULDIGNOREBUDGETS Raw Value-37',
        'zShare-ZEXITSOURCE Raw Value-38',
        'zShare-ZEXITSTATE Raw Value-39',
        'zShare-ZEXITTYPE Raw Value-40',
        'zShare-ZTRASHEDSTATE Raw Value-41',
        'zShare-ZCLOUDDELETESTATE Raw Value-42',
        ('zShare-Trashed Date-43', 'datetime'),
        ('zShare-LastParticipant Asset Trash Notification Date-44', 'datetime'),
        ('zShare-Last Participant Asset Trash Notification View Date-45', 'datetime'),
        'zShare-Z_ENT Raw Value-46')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("18")) & (version.parse(iosversion) < version.parse("26")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zShare.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Creation Date',
        DateTime(zShare.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Start Date',
        DateTime(zShare.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-End Date',
        DateTime(zShare.ZEXPIRYDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Expiry Date',  
        zShare.ZUUID AS 'zShare-UUID',
        zShare.ZORIGINATINGSCOPEIDENTIFIER AS 'zShare-Originating Scope ID',
        zSharePartic.Z61_SHARE AS 'zSharePartic-Z61_SHARE Raw Value',
        zShare.ZSTATUS AS 'zShare-ZSTATUS Raw Value',
        zShare.ZSCOPETYPE AS 'zShare-ZSCOPETYPE Raw Value',
        zShare.ZASSETCOUNT AS 'zShare-Asset Count-CMM',
        zShare.ZFORCESYNCATTEMPTED AS 'zShare-Force Sync Attempted-CMM',  
        zShare.ZPHOTOSCOUNT AS 'zShare-Photos Count-CMM',
        zShare.ZUPLOADEDPHOTOSCOUNT AS 'zShare-Uploaded Photos Count-CMM',
        zShare.ZVIDEOSCOUNT AS 'zShare-Videos Count-CMM',
        zShare.ZUPLOADEDVIDEOSCOUNT AS 'zShare-Uploaded Videos Count-CMM',  
        zShare.ZSCOPEIDENTIFIER AS 'zShare-Scope ID',
        zShare.ZTITLE AS 'zShare-Title-SPL',
        zShare.ZSHAREURL AS 'zShare-Share URL',
        zShare.ZLOCALPUBLISHSTATE AS 'zShare-ZLOCALPUBLISHSTATE Raw Value',
        zShare.ZPUBLICPERMISSION AS 'zShare-ZPUBLICPERMISSION Raw Value',
        zShare.ZCLOUDLOCALSTATE AS 'zShare-ZCLOUDLOCALSTATE Raw Value',
        zShare.ZSCOPESYNCINGSTATE AS 'zShare-ZSCOPESYNCINGSTATE Raw Value',
        zShare.ZAUTOSHAREPOLICY AS 'zShare-ZAUTOSHAREPOLICY Raw Value',
        zSharePartic.ZACCEPTANCESTATUS AS 'zSharePartic-ZACCEPTANCESTATUS Raw Value',
        zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
        zSharePartic.Z_PK AS 'zSharePartic-zPK',
        zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
        zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',
        zSharePartic.ZPARTICIPANTID AS 'zSharePartic-Participant ID',
        zSharePartic.ZUUID AS 'zSharePartic-UUID',  
        zSharePartic.ZISCURRENTUSER AS 'zSharePartic-ZISCURRENTUSER Raw Value',
        zSharePartic.ZROLE AS 'zSharePartic-ZROLE Raw Value',
        zSharePartic.ZPERMISSION AS 'zSharePartic-ZPERMISSION Raw Value',
        zShare.ZPARTICIPANTCLOUDUPDATESTATE AS 'zShare-ZPARTICIPANTCLOUDUPDATESTATE Raw Value',
        zSharePartic.ZEXITSTATE AS 'zSharePartic-ZEXITSTATE Raw Value',
        zShare.ZPREVIEWSTATE AS 'zShare-ZPREVIEWSTATE Raw Value',
        zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION AS 'zShare-ZSHOULDNOTIFYONUPLOADCOMPLETION Raw Value',
        zShare.ZSHOULDIGNOREBUDGETS AS 'zShare-ZSHOULDIGNOREBUDGETS Raw Value',
        zShare.ZEXITSOURCE AS 'zShare-ZEXITSOURCE Raw Value',
        zShare.ZEXITSTATE AS 'zShare-ZEXITSTATE Raw Value',
        zShare.ZEXITTYPE AS 'zShare-ZEXITTYPE Raw Value',
        zShare.ZTRASHEDSTATE AS 'zShare-ZTRASHEDSTATE Raw Value',
        zShare.ZCLOUDDELETESTATE AS 'zShare-ZCLOUDDELETESTATE Raw Value',
        DateTime(zShare.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Trashed Date',
        DateTime(zShare.ZLASTPARTICIPANTASSETTRASHNOTIFICATIONDATE + 978307200, 'UNIXEPOCH') AS
         'zShare-LastParticipant Asset Trash Notification Date',
        DateTime(zShare.ZLASTPARTICIPANTASSETTRASHNOTIFICATIONVIEWEDDATE + 978307200, 'UNIXEPOCH') AS
         'zShare-Last Participant Asset Trash Notification View Date',
        zShare.Z_ENT AS 'zShare-Z_ENT Raw Value'
        FROM ZSHARE zShare
            LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
        WHERE zShare.ZSCOPETYPE = 2
        ORDER BY zShare.ZCREATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
            row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16],
            row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25],
            row[26], row[27], row[28], row[29], row[30], row[31], row[32], row[33], row[34],
            row[35], row[36], row[37], row[38], row[39], row[40], row[41], row[42], row[43],
            row[44], row[45], row[46]))

        data_headers = (('zShare-Creation Date-0', 'datetime'),
        ('zShare-Start Date-1', 'datetime'),
        ('zShare-End Date-2', 'datetime'),
        ('zShare-Expiry Date-3', 'datetime'),
        'zShare-UUID-4',
        'zShare-Originating Scope ID-5',
        'zSharePartic-Z61_SHARE Raw Value-6',
        'zShare-ZSTATUS Raw Value-7',
        'zShare-ZSCOPETYPE Raw Value-8',
        'zShare-Asset Count-CMM-9',
        'zShare-Force Sync Attempted-CMM-10',
        'zShare-Photos Count-CMM-11',
        'zShare-Uploaded Photos Count-CMM-12',
        'zShare-Videos Count-CMM-13',
        'zShare-Uploaded Videos Count-CMM-14',
        'zShare-Scope ID-15',
        'zShare-Title-SPL-16',
        'zShare-Share URL-17',
        'zShare-ZLOCALPUBLISHSTATE Raw Value-18',
        'zShare-ZPUBLICPERMISSION Raw Value-19',
        'zShare-ZCLOUDLOCALSTATE Raw Value-20',
        'zShare-ZSCOPESYNCINGSTATE Raw Value-21',
        'zShare-ZAUTOSHAREPOLICY Raw Value-22',
        'zSharePartic-ZACCEPTANCESTATUS Raw Value-23',
        'zSharePartic-User ID-24',
        'zSharePartic-zPK-25',
        'zSharePartic-Email Address-26',
        'zSharePartic-Phone Number-27',
        'zSharePartic-Participant ID-28',
        'zSharePartic-UUID-29',
        'zSharePartic-ZISCURRENTUSER Raw Value-30',
        'zSharePartic-ZROLE Raw Value-31',
        'zSharePartic-ZPERMISSION Raw Value-32',
        'zShare-ZPARTICIPANTCLOUDUPDATESTATE Raw Value-33',
        'zSharePartic-ZEXITSTATE Raw Value-34',
        'zShare-ZPREVIEWSTATE Raw Value-35',
        'zShare-ZSHOULDNOTIFYONUPLOADCOMPLETION Raw Value-36',
        'zShare-ZSHOULDIGNOREBUDGETS Raw Value-37',
        'zShare-ZEXITSOURCE Raw Value-38',
        'zShare-ZEXITSTATE Raw Value-39',
        'zShare-ZEXITTYPE Raw Value-40',
        'zShare-ZTRASHEDSTATE Raw Value-41',
        'zShare-ZCLOUDDELETESTATE Raw Value-42',
        ('zShare-Trashed Date-43', 'datetime'),
        ('zShare-LastParticipant Asset Trash Notification Date-44', 'datetime'),
        ('zShare-Last Participant Asset Trash Notification View Date-45', 'datetime'),
        'zShare-Z_ENT Raw Value-46')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        return data_headers, data_list, source_path
