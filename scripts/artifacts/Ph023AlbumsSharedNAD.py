__artifacts_v2__ = {
'Ph023SharedAlbumRecordsInviteswithNADPhDaPsql': {
'name': 'Ph023-Shared Album Records & Invites NAD-PhDaPsql',
'description': 'Album records with stored ZKIND 1505 in PhotoData/Photos.sqlite, including linked invitation records. Queries cover iOS 11 through 26; an album with several invitations can appear on several rows. No asset records are parsed. Enum fields report raw stored values. The iOS 26 join-table path has returned no rows in the two registered images with no kind 1505 album.',
'author': '@AlexisBrignoni, Codex',
'creation_date': '2026-05-28',
'last_update_date': '2026-10-05',
'version': '6.0',
'date': '2026-05-26',
'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
'category': 'Photos.sqlite',
'notes': 'Original parser and Photos.sqlite research: Scott Koenig, https://theforensicscooter.com/2024/05/18/ileapp-parsers-photos-sqlite-queries/. Raw enum projections preserve stored NULL and unknown values; per-value interpretations are not emitted.',
'paths': ('*/PhotoData/Photos.sqlite*',),
"output_types": ["standard", "tsv", "none"],
"artifact_icon": "cloud-upload",
'sample_data': {
'ctf2020_ios12': 'iOS 12.4 | 1 row',
'dexter_ios18': 'iOS 18.3.2 | 0 rows',
'felix_ios17': 'iOS 17.6.1 | 0 rows',
'fsfull002_ios17': 'iOS 17.1 | 0 rows',
'hc_ios18_7': 'iOS 18.7.8 | 0 rows',
'iphone11_ios17': 'iOS 17.3 | 8 rows',
'iphone12_ios18': 'iOS 18.7 | 0 rows',
'iphone14plus_ios18': 'iOS 18.0 | 0 rows',
'otto_ios17': 'iOS 17.5.1 | 0 rows',
'abe_ios16': 'iOS 16.5 | 1 row',
'felix23_ios16': 'iOS 16.5 | 0 rows',
'hickman_ios13': 'iOS 13.3.1 | 0 rows',
'hickman_ios14': 'iOS 14.3 | 1 row',
'jess_ios15': 'iOS 15.0.2 | 0 rows',
'magnet_ios16': 'iOS 16.1.1 | 0 rows',
}
}
}

import os
from packaging import version
from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, null_absent_columns, logfunc, iOS

@artifact_processor
def Ph023SharedAlbumRecordsInviteswithNADPhDaPsql(context):
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
    if (version.parse(iosversion) <= version.parse("10.3.4")) or (version.parse(iosversion) >= version.parse("27")):
        logfunc("Unsupported version for PhotoData-Photos.sqlite iOS " + iosversion)
        return (), [], source_path
    if (version.parse(iosversion) >= version.parse("11")) & (version.parse(iosversion) < version.parse("12")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',             
        DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',    
        zGenAlbum.ZCLOUDMETADATA AS 'zGenAlbum-Cloud Metadata-HEX NSKeyed Plist',        
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        zGenAlbum.ZPENDINGITEMSTYPE AS 'zGenAlbum-ZPENDINGITEMSTYPE Raw Value',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        zGenAlbum.ZHASUNSEENCONTENT AS 'zGenAlbum-ZHASUNSEENCONTENT Raw Value',
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        zGenAlbum.Z_ENT AS 'zGenAlbum-Z_ENT Raw Value',
        zGenAlbum.ZKIND AS 'zGenAlbum-ZKIND Raw Value',
        zGenAlbum.ZCLOUDLOCALSTATE AS 'zGenAlbum-ZCLOUDLOCALSTATE Raw Value',
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        zGenAlbum.ZISOWNED AS 'zGenAlbum-ZISOWNED Raw Value',
        zGenAlbum.ZCLOUDRELATIONSHIPSTATE AS 'zGenAlbum-ZCLOUDRELATIONSHIPSTATE Raw Value',
        zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL AS 'zGenAlbum-ZCLOUDRELATIONSHIPSTATELOCAL Raw Value',
        zGenAlbum.ZCLOUDOWNEREMAILKEY AS 'zGenAlbum-Cloud Owner Mail Key',        
        zGenAlbum.ZCLOUDOWNERFIRSTNAME AS 'zGenAlbum-Cloud Owner Frist Name',        
        zGenAlbum.ZCLOUDOWNERLASTNAME AS 'zGenAlbum-Cloud Owner Last Name',        
        zGenAlbum.ZCLOUDOWNERFULLNAME AS 'zGenAlbum-Cloud Owner Full Name',
        zGenAlbum.ZCLOUDPERSONID AS 'zGenAlbum-Cloud Person ID',
        zGenAlbum.ZCLOUDOWNERHASHEDPERSONID AS 'zGenAlbum-Cloud Owner Hashed Person ID',
        zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL AS 'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL Raw Value',
        zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED AS 'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLED Raw Value',
        zGenAlbum.ZCLOUDALBUMSUBTYPE AS 'zGenAlbum-ZCLOUDALBUMSUBTYPE Raw Value',
        DateTime(zGenAlbum.ZCLOUDLASTCONTRIBUTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Contribution Date',        
        DateTime(zGenAlbum.ZCLOUDLASTINTERESTINGCHANGEDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Last Interesting Change Date',        
        zGenAlbum.ZCLOUDNOTIFICATIONSENABLED AS 'zGenAlbum-ZCLOUDNOTIFICATIONSENABLED Raw Value',
        zGenAlbum.ZISPINNED AS 'zGenAlbum-ZISPINNED Raw Value',
        zGenAlbum.ZCUSTOMSORTKEY AS 'zGenAlbum-ZCUSTOMSORTKEY Raw Value',
        zGenAlbum.ZCUSTOMSORTASCENDING AS 'zGenAlbum-ZCUSTOMSORTASCENDING Raw Value',
        zGenAlbum.ZCUSTOMQUERYTYPE AS 'zGenAlbum-ZCUSTOMQUERYTYPE Raw Value',
        zGenAlbum.ZTRASHEDSTATE AS 'zGenAlbum-ZTRASHEDSTATE Raw Value',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',
        zGenAlbum.ZCLOUDOWNERISWHITELISTED AS 'zGenAlbum-ZCLOUDOWNERISWHITELISTED Raw Value',
        zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL AS 'zGenAlbum-ZCLOUDPUBLICURLENABLEDLOCAL Raw Value',
        zGenAlbum.ZCLOUDPUBLICURLENABLED AS 'zGenAlbum-ZCLOUDPUBLICURLENABLED Raw Value',
        zGenAlbum.ZPUBLICURL AS 'zGenAlbum-Public URL',        
        zGenAlbum.ZKEYASSETFACETHUMBNAILINDEX AS 'zGenAlbum-Key Asset Face Thumb Index',        
        zGenAlbum.ZCUSTOMQUERYPARAMETERS AS 'zGenAlbum-Custom Query Parameters',
        zCldShareAlbumInvRec.ZISMINE AS 'zCldShareAlbumInvRec-ZISMINE Raw Value',
        zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL AS 'zCldShareAlbumInvRec-ZINVITATIONSTATELOCAL Raw Value',
        zCldShareAlbumInvRec.ZINVITATIONSTATE AS 'zCldShareAlbumInvRec-ZINVITATIONSTATE Raw Value',
        DateTime(zCldShareAlbumInvRec.ZINVITEESUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zCldShareAlbumInvRec-Subscription Date',
        zCldShareAlbumInvRec.ZINVITEEFIRSTNAME AS 'zCldShareAlbumInvRec-Invitee First Name',
        zCldShareAlbumInvRec.ZINVITEELASTNAME AS 'zCldShareAlbumInvRec-Invitee Last Name',
        zCldShareAlbumInvRec.ZINVITEEFULLNAME AS 'zCldShareAlbumInvRec-Invitee Full Name',
        zCldShareAlbumInvRec.ZINVITEEHASHEDPERSONID AS 'zCldShareAlbumInvRec-Invitee Hashed Person ID',
        zCldShareAlbumInvRec.ZINVITEEEMAILKEY AS 'zCldShareAlbumInvRec-Invitee Email Key',    
        zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID',
        zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID',  
        zAlbumList.ZNEEDSREORDERINGNUMBER AS 'zAlbumList-ZNEEDSREORDERINGNUMBER Raw Value'
        FROM ZGENERICALBUM zGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN Z_19ALBUMLISTS z19AlbumLists ON z19AlbumLists.Z_19ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z19AlbumLists.Z_3ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
        ORDER BY zGenAlbum.ZSTARTDATE
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
            row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
            row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
            row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
            row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
            row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
            row[55], row[56], row[57]))

        data_headers = (('zGenAlbum-Cloud Creation Date-0', 'datetime'),
        ('zGenAlbum-Start Date-1', 'datetime'),
        ('zGenAlbum-End Date-2', 'datetime'),
        ('zGenAlbum-Cloud Subscription Date-3', 'datetime'),
        'zGenAlbum- Title-User&System Applied-4',
        'zGenAlbum-UUID-5',
        'zGenAlbum-Cloud GUID-6',
        'zGenAlbum-Cloud Metadata-HEX NSKeyed Plist-7',
        'zGenAlbum-Pending Items Count-8',
        'zGenAlbum-ZPENDINGITEMSTYPE Raw Value-9',
        'zGenAlbum- Cached Photos Count-10',
        'zGenAlbum- Cached Videos Count-11',
        'zGenAlbum- Cached Count-12',
        'zGenAlbum-ZHASUNSEENCONTENT Raw Value-13',
        'zGenAlbum-Unseen Asset Count-14',
        'zGenAlbum-Z_ENT Raw Value-15',
        'zGenAlbum-ZKIND Raw Value-16',
        'zGenAlbum-ZCLOUDLOCALSTATE Raw Value-17',
        'zGenAlbum-Sync Event Order Key-18',
        'zGenAlbum-ZISOWNED Raw Value-19',
        'zGenAlbum-ZCLOUDRELATIONSHIPSTATE Raw Value-20',
        'zGenAlbum-ZCLOUDRELATIONSHIPSTATELOCAL Raw Value-21',
        'zGenAlbum-Cloud Owner Mail Key-22',
        'zGenAlbum-Cloud Owner Frist Name-23',
        'zGenAlbum-Cloud Owner Last Name-24',
        'zGenAlbum-Cloud Owner Full Name-25',
        'zGenAlbum-Cloud Person ID-26',
        'zGenAlbum-Cloud Owner Hashed Person ID-27',
        'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL Raw Value-28',
        'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLED Raw Value-29',
        'zGenAlbum-ZCLOUDALBUMSUBTYPE Raw Value-30',
        ('zGenAlbum-Cloud Contribution Date-31', 'datetime'),
        ('zGenAlbum-Cloud Last Interesting Change Date-32', 'datetime'),
        'zGenAlbum-ZCLOUDNOTIFICATIONSENABLED Raw Value-33',
        'zGenAlbum-ZISPINNED Raw Value-34',
        'zGenAlbum-ZCUSTOMSORTKEY Raw Value-35',
        'zGenAlbum-ZCUSTOMSORTASCENDING Raw Value-36',
        'zGenAlbum-ZCUSTOMQUERYTYPE Raw Value-37',
        'zGenAlbum-ZTRASHEDSTATE Raw Value-38',
        ('zGenAlbum-Trash Date-39', 'datetime'),
        'zGenAlbum-ZCLOUDOWNERISWHITELISTED Raw Value-40',
        'zGenAlbum-ZCLOUDPUBLICURLENABLEDLOCAL Raw Value-41',
        'zGenAlbum-ZCLOUDPUBLICURLENABLED Raw Value-42',
        'zGenAlbum-Public URL-43',
        'zGenAlbum-Key Asset Face Thumb Index-44',
        'zGenAlbum-Custom Query Parameters-45',
        'zCldShareAlbumInvRec-ZISMINE Raw Value-46',
        'zCldShareAlbumInvRec-ZINVITATIONSTATELOCAL Raw Value-47',
        'zCldShareAlbumInvRec-ZINVITATIONSTATE Raw Value-48',
        ('zCldShareAlbumInvRec-Subscription Date-49', 'datetime'),
        'zCldShareAlbumInvRec-Invitee First Name-50',
        'zCldShareAlbumInvRec-Invitee Last Name-51',
        'zCldShareAlbumInvRec-Invitee Full Name-52',
        'zCldShareAlbumInvRec-Invitee Hashed Person ID-53',
        'zCldShareAlbumInvRec-Invitee Email Key-54',
        'zCldShareAlbumInvRec-Album GUID-55',
        'zCldShareAlbumInvRec-Cloud GUID-56',
        'zAlbumList-ZNEEDSREORDERINGNUMBER Raw Value-57')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("12")) & (version.parse(iosversion) < version.parse("13")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Creation Date',  
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',              
        DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',      
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        zGenAlbum.ZPENDINGITEMSTYPE AS 'zGenAlbum-ZPENDINGITEMSTYPE Raw Value',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        zGenAlbum.ZHASUNSEENCONTENT AS 'zGenAlbum-ZHASUNSEENCONTENT Raw Value',
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        zGenAlbum.Z_ENT AS 'zGenAlbum-Z_ENT Raw Value',
        zGenAlbum.ZKIND AS 'zGenAlbum-ZKIND Raw Value',
        zGenAlbum.ZCLOUDLOCALSTATE AS 'zGenAlbum-ZCLOUDLOCALSTATE Raw Value',
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        zGenAlbum.ZISOWNED AS 'zGenAlbum-ZISOWNED Raw Value',
        zGenAlbum.ZCLOUDRELATIONSHIPSTATE AS 'zGenAlbum-ZCLOUDRELATIONSHIPSTATE Raw Value',
        zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL AS 'zGenAlbum-ZCLOUDRELATIONSHIPSTATELOCAL Raw Value',
        zGenAlbum.ZCLOUDOWNEREMAILKEY AS 'zGenAlbum-Cloud Owner Mail Key',        
        zGenAlbum.ZCLOUDOWNERFIRSTNAME AS 'zGenAlbum-Cloud Owner Frist Name',        
        zGenAlbum.ZCLOUDOWNERLASTNAME AS 'zGenAlbum-Cloud Owner Last Name',        
        zGenAlbum.ZCLOUDOWNERFULLNAME AS 'zGenAlbum-Cloud Owner Full Name',
        zGenAlbum.ZCLOUDPERSONID AS 'zGenAlbum-Cloud Person ID',        
        zGenAlbum.ZCLOUDOWNERHASHEDPERSONID AS 'zGenAlbum-Cloud Owner Hashed Person ID',        
        zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL AS 'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL Raw Value',
        zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED AS 'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLED Raw Value',
        zGenAlbum.ZCLOUDALBUMSUBTYPE AS 'zGenAlbum-ZCLOUDALBUMSUBTYPE Raw Value',
        DateTime(zGenAlbum.ZCLOUDLASTCONTRIBUTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Contribution Date',        
        DateTime(zGenAlbum.ZCLOUDLASTINTERESTINGCHANGEDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Last Interesting Change Date',        
        zGenAlbum.ZCLOUDNOTIFICATIONSENABLED AS 'zGenAlbum-ZCLOUDNOTIFICATIONSENABLED Raw Value',
        zGenAlbum.ZISPINNED AS 'zGenAlbum-ZISPINNED Raw Value',
        zGenAlbum.ZCUSTOMSORTKEY AS 'zGenAlbum-ZCUSTOMSORTKEY Raw Value',
        zGenAlbum.ZCUSTOMSORTASCENDING AS 'zGenAlbum-ZCUSTOMSORTASCENDING Raw Value',
        zGenAlbum.ZCUSTOMQUERYTYPE AS 'zGenAlbum-ZCUSTOMQUERYTYPE Raw Value',
        zGenAlbum.ZTRASHEDSTATE AS 'zGenAlbum-ZTRASHEDSTATE Raw Value',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        zGenAlbum.ZCLOUDDELETESTATE AS 'zGenAlbum-ZCLOUDDELETESTATE Raw Value',
        zGenAlbum.ZCLOUDOWNERISWHITELISTED AS 'zGenAlbum-ZCLOUDOWNERISWHITELISTED Raw Value',
        zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL AS 'zGenAlbum-ZCLOUDPUBLICURLENABLEDLOCAL Raw Value',
        zGenAlbum.ZCLOUDPUBLICURLENABLED AS 'zGenAlbum-ZCLOUDPUBLICURLENABLED Raw Value',
        zGenAlbum.ZPUBLICURL AS 'zGenAlbum-Public URL',        
        zGenAlbum.ZKEYASSETFACETHUMBNAILINDEX AS 'zGenAlbum-Key Asset Face Thumb Index',        
        zGenAlbum.ZCUSTOMQUERYPARAMETERS AS 'zGenAlbum-Custom Query Parameters',
        zCldShareAlbumInvRec.ZISMINE AS 'zCldShareAlbumInvRec-ZISMINE Raw Value',
        zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL AS 'zCldShareAlbumInvRec-ZINVITATIONSTATELOCAL Raw Value',
        zCldShareAlbumInvRec.ZINVITATIONSTATE AS 'zCldShareAlbumInvRec-ZINVITATIONSTATE Raw Value',
        DateTime(zCldShareAlbumInvRec.ZINVITEESUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zCldShareAlbumInvRec-Subscription Date',
        zCldShareAlbumInvRec.ZINVITEEFIRSTNAME AS 'zCldShareAlbumInvRec-Invitee First Name',
        zCldShareAlbumInvRec.ZINVITEELASTNAME AS 'zCldShareAlbumInvRec-Invitee Last Name',
        zCldShareAlbumInvRec.ZINVITEEFULLNAME AS 'zCldShareAlbumInvRec-Invitee Full Name',
        zCldShareAlbumInvRec.ZINVITEEHASHEDPERSONID AS 'zCldShareAlbumInvRec-Invitee Hashed Person ID',
        zCldShareAlbumInvRec.ZINVITEEEMAILKEY AS 'zCldShareAlbumInvRec-Invitee Email Key',    
        zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID',
        zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID',  
        zAlbumList.ZNEEDSREORDERINGNUMBER AS 'zAlbumList-ZNEEDSREORDERINGNUMBER Raw Value'
        FROM ZGENERICALBUM zGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN Z_22ALBUMLISTS z22AlbumLists ON z22AlbumLists.Z_22ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z22AlbumLists.Z_3ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
        ORDER BY zGenAlbum.ZSTARTDATE
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
            row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
            row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
            row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
            row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
            row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
            row[55], row[56], row[57]))

        data_headers = (('zGenAlbum-Cloud Creation Date-0', 'datetime'),
        ('zGenAlbum-Start Date-1', 'datetime'),
        ('zGenAlbum-End Date-2', 'datetime'),
        ('zGenAlbum-Cloud Subscription Date-3', 'datetime'),
        'zGenAlbum- Title-User&System Applied-4',
        'zGenAlbum-UUID-5',
        'zGenAlbum-Cloud GUID-6',
        'zGenAlbum-Pending Items Count-7',
        'zGenAlbum-ZPENDINGITEMSTYPE Raw Value-8',
        'zGenAlbum- Cached Photos Count-9',
        'zGenAlbum- Cached Videos Count-10',
        'zGenAlbum- Cached Count-11',
        'zGenAlbum-ZHASUNSEENCONTENT Raw Value-12',
        'zGenAlbum-Unseen Asset Count-13',
        'zGenAlbum-Z_ENT Raw Value-14',
        'zGenAlbum-ZKIND Raw Value-15',
        'zGenAlbum-ZCLOUDLOCALSTATE Raw Value-16',
        'zGenAlbum-Sync Event Order Key-17',
        'zGenAlbum-ZISOWNED Raw Value-18',
        'zGenAlbum-ZCLOUDRELATIONSHIPSTATE Raw Value-19',
        'zGenAlbum-ZCLOUDRELATIONSHIPSTATELOCAL Raw Value-20',
        'zGenAlbum-Cloud Owner Mail Key-21',
        'zGenAlbum-Cloud Owner First Name-22',
        'zGenAlbum-Cloud Owner Last Name-23',
        'zGenAlbum-Cloud Owner Full Name-24',
        'zGenAlbum-Cloud Person ID-25',
        'zGenAlbum-Cloud Owner Hashed Person ID-26',
        'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL Raw Value-27',
        'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLED Raw Value-28',
        'zGenAlbum-ZCLOUDALBUMSUBTYPE Raw Value-29',
        ('zGenAlbum-Cloud Contribution Date-30', 'datetime'),
        ('zGenAlbum-Cloud Last Interesting Change Date-31', 'datetime'),
        'zGenAlbum-ZCLOUDNOTIFICATIONSENABLED Raw Value-32',
        'zGenAlbum-ZISPINNED Raw Value-33',
        'zGenAlbum-ZCUSTOMSORTKEY Raw Value-34',
        'zGenAlbum-ZCUSTOMSORTASCENDING Raw Value-35',
        'zGenAlbum-ZCUSTOMQUERYTYPE Raw Value-36',
        'zGenAlbum-ZTRASHEDSTATE Raw Value-37',
        ('zGenAlbum-Trash Date-38', 'datetime'),
        'zGenAlbum-ZCLOUDDELETESTATE Raw Value-39',
        'zGenAlbum-ZCLOUDOWNERISWHITELISTED Raw Value-40',
        'zGenAlbum-ZCLOUDPUBLICURLENABLEDLOCAL Raw Value-41',
        'zGenAlbum-ZCLOUDPUBLICURLENABLED Raw Value-42',
        'zGenAlbum-Public URL-43',
        'zGenAlbum-Key Asset Face Thumb Index-44',
        'zGenAlbum-Custom Query Parameters-45',
        'zCldShareAlbumInvRec-ZISMINE Raw Value-46',
        'zCldShareAlbumInvRec-ZINVITATIONSTATELOCAL Raw Value-47',
        'zCldShareAlbumInvRec-ZINVITATIONSTATE Raw Value-48',
        ('zCldShareAlbumInvRec-Subscription Date-49', 'datetime'),
        'zCldShareAlbumInvRec-Invitee First Name-50',
        'zCldShareAlbumInvRec-Invitee Last Name-51',
        'zCldShareAlbumInvRec-Invitee Full Name-52',
        'zCldShareAlbumInvRec-Invitee Hashed Person ID-53',
        'zCldShareAlbumInvRec-Invitee Email Key-54',
        'zCldShareAlbumInvRec-Album GUID-55',
        'zCldShareAlbumInvRec-Cloud GUID-56',
        'zAlbumList-ZNEEDSREORDERINGNUMBER Raw Value-57')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("13")) & (version.parse(iosversion) < version.parse("14")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Creation Date',   
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',             
        DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',        
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        zGenAlbum.ZPENDINGITEMSTYPE AS 'zGenAlbum-ZPENDINGITEMSTYPE Raw Value',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        zGenAlbum.ZHASUNSEENCONTENT AS 'zGenAlbum-ZHASUNSEENCONTENT Raw Value',
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        zGenAlbum.Z_ENT AS 'zGenAlbum-Z_ENT Raw Value',
        zGenAlbum.ZKIND AS 'zGenAlbum-ZKIND Raw Value',
        zGenAlbum.ZCLOUDLOCALSTATE AS 'zGenAlbum-ZCLOUDLOCALSTATE Raw Value',
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        zGenAlbum.ZISOWNED AS 'zGenAlbum-ZISOWNED Raw Value',
        zGenAlbum.ZCLOUDRELATIONSHIPSTATE AS 'zGenAlbum-ZCLOUDRELATIONSHIPSTATE Raw Value',
        zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL AS 'zGenAlbum-ZCLOUDRELATIONSHIPSTATELOCAL Raw Value',
        zGenAlbum.ZCLOUDOWNEREMAILKEY AS 'zGenAlbum-Cloud Owner Mail Key',        
        zGenAlbum.ZCLOUDOWNERFIRSTNAME AS 'zGenAlbum-Cloud Owner Frist Name',        
        zGenAlbum.ZCLOUDOWNERLASTNAME AS 'zGenAlbum-Cloud Owner Last Name',        
        zGenAlbum.ZCLOUDOWNERFULLNAME AS 'zGenAlbum-Cloud Owner Full Name',
        zGenAlbum.ZCLOUDPERSONID AS 'zGenAlbum-Cloud Person ID',        
        zGenAlbum.ZCLOUDOWNERHASHEDPERSONID AS 'zGenAlbum-Cloud Owner Hashed Person ID',        
        zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL AS 'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL Raw Value',
        zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED AS 'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLED Raw Value',
        zGenAlbum.ZCLOUDALBUMSUBTYPE AS 'zGenAlbum-ZCLOUDALBUMSUBTYPE Raw Value',
        DateTime(zGenAlbum.ZCLOUDLASTCONTRIBUTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Contribution Date',        
        DateTime(zGenAlbum.ZCLOUDLASTINTERESTINGCHANGEDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Last Interesting Change Date',        
        zGenAlbum.ZCLOUDNOTIFICATIONSENABLED AS 'zGenAlbum-ZCLOUDNOTIFICATIONSENABLED Raw Value',
        zGenAlbum.ZISPINNED AS 'zGenAlbum-ZISPINNED Raw Value',
        zGenAlbum.ZCUSTOMSORTKEY AS 'zGenAlbum-ZCUSTOMSORTKEY Raw Value',
        zGenAlbum.ZCUSTOMSORTASCENDING AS 'zGenAlbum-ZCUSTOMSORTASCENDING Raw Value',
        zGenAlbum.ZPROJECTDOCUMENTTYPE AS 'zGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value',
        zGenAlbum.ZCUSTOMQUERYTYPE AS 'zGenAlbum-ZCUSTOMQUERYTYPE Raw Value',
        zGenAlbum.ZTRASHEDSTATE AS 'zGenAlbum-ZTRASHEDSTATE Raw Value',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        zGenAlbum.ZCLOUDDELETESTATE AS 'zGenAlbum-ZCLOUDDELETESTATE Raw Value',
        zGenAlbum.ZCLOUDOWNERISWHITELISTED AS 'zGenAlbum-ZCLOUDOWNERISWHITELISTED Raw Value',
        zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL AS 'zGenAlbum-ZCLOUDPUBLICURLENABLEDLOCAL Raw Value',
        zGenAlbum.ZCLOUDPUBLICURLENABLED AS 'zGenAlbum-ZCLOUDPUBLICURLENABLED Raw Value',
        zGenAlbum.ZPUBLICURL AS 'zGenAlbum-Public URL',        
        zGenAlbum.ZKEYASSETFACETHUMBNAILINDEX AS 'zGenAlbum-Key Asset Face Thumb Index',        
        zGenAlbum.ZPROJECTEXTENSIONIDENTIFIER AS 'zGenAlbum-Project Text Extension ID',        
        zGenAlbum.ZUSERQUERYDATA AS 'zGenAlbum-User Query Data',        
        zGenAlbum.ZCUSTOMQUERYPARAMETERS AS 'zGenAlbum-Custom Query Parameters',        
        zGenAlbum.ZPROJECTDATA AS 'zGenAlbum-Project Data',
        zCldShareAlbumInvRec.ZISMINE AS 'zCldShareAlbumInvRec-ZISMINE Raw Value',
        zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL AS 'zCldShareAlbumInvRec-ZINVITATIONSTATELOCAL Raw Value',
        zCldShareAlbumInvRec.ZINVITATIONSTATE AS 'zCldShareAlbumInvRec-ZINVITATIONSTATE Raw Value',
        DateTime(zCldShareAlbumInvRec.ZINVITEESUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zCldShareAlbumInvRec-Subscription Date',
        zCldShareAlbumInvRec.ZINVITEEFIRSTNAME AS 'zCldShareAlbumInvRec-Invitee First Name',
        zCldShareAlbumInvRec.ZINVITEELASTNAME AS 'zCldShareAlbumInvRec-Invitee Last Name',
        zCldShareAlbumInvRec.ZINVITEEFULLNAME AS 'zCldShareAlbumInvRec-Invitee Full Name',
        zCldShareAlbumInvRec.ZINVITEEHASHEDPERSONID AS 'zCldShareAlbumInvRec-Invitee Hashed Person ID',
        zCldShareAlbumInvRec.ZINVITEEEMAILKEY AS 'zCldShareAlbumInvRec-Invitee Email Key',    
        zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID',
        zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID',
        zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID',        
        zAlbumList.ZNEEDSREORDERINGNUMBER AS 'zAlbumList-ZNEEDSREORDERINGNUMBER Raw Value'
        FROM ZGENERICALBUM zGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN Z_25ALBUMLISTS z25AlbumLists ON z25AlbumLists.Z_25ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z25AlbumLists.Z_3ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
        ORDER BY zGenAlbum.ZCREATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
            row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
            row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
            row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
            row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
            row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
            row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63]))

        data_headers = (('zGenAlbum-Cloud Creation Date-0', 'datetime'),
        ('zGenAlbum-Creation Date-1', 'datetime'),
        ('zGenAlbum-Start Date-2', 'datetime'),
        ('zGenAlbum-End Date-3', 'datetime'),
        ('zGenAlbum-Cloud Subscription Date-4', 'datetime'),
        'zGenAlbum- Title-User&System Applied-5',
        'zGenAlbum-UUID-6',
        'zGenAlbum-Cloud GUID-7',
        'zGenAlbum-Pending Items Count-8',
        'zGenAlbum-ZPENDINGITEMSTYPE Raw Value-9',
        'zGenAlbum- Cached Photos Count-10',
        'zGenAlbum- Cached Videos Count-11',
        'zGenAlbum- Cached Count-12',
        'zGenAlbum-ZHASUNSEENCONTENT Raw Value-13',
        'zGenAlbum-Unseen Asset Count-14',
        'zGenAlbum-Z_ENT Raw Value-15',
        'zGenAlbum-ZKIND Raw Value-16',
        'zGenAlbum-ZCLOUDLOCALSTATE Raw Value-17',
        'zGenAlbum-Sync Event Order Key-18',
        'zGenAlbum-ZISOWNED Raw Value-19',
        'zGenAlbum-ZCLOUDRELATIONSHIPSTATE Raw Value-20',
        'zGenAlbum-ZCLOUDRELATIONSHIPSTATELOCAL Raw Value-21',
        'zGenAlbum-Cloud Owner Mail Key-22',
        'zGenAlbum-Cloud Owner Frist Name-23',
        'zGenAlbum-Cloud Owner Last Name-24',
        'zGenAlbum-Cloud Owner Full Name-25',
        'zGenAlbum-Cloud Person ID-26',
        'zGenAlbum-Cloud Owner Hashed Person ID-27',
        'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL Raw Value-28',
        'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLED Raw Value-29',
        'zGenAlbum-ZCLOUDALBUMSUBTYPE Raw Value-30',
        ('zGenAlbum-Cloud Contribution Date-31', 'datetime'),
        ('zGenAlbum-Cloud Last Interesting Change Date-32', 'datetime'),
        'zGenAlbum-ZCLOUDNOTIFICATIONSENABLED Raw Value-33',
        'zGenAlbum-ZISPINNED Raw Value-34',
        'zGenAlbum-ZCUSTOMSORTKEY Raw Value-35',
        'zGenAlbum-ZCUSTOMSORTASCENDING Raw Value-36',
        'zGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value-37',
        'zGenAlbum-ZCUSTOMQUERYTYPE Raw Value-38',
        'zGenAlbum-ZTRASHEDSTATE Raw Value-39',
        ('zGenAlbum-Trash Date-40', 'datetime'),
        'zGenAlbum-ZCLOUDDELETESTATE Raw Value-41',
        'zGenAlbum-ZCLOUDOWNERISWHITELISTED Raw Value-42',
        'zGenAlbum-ZCLOUDPUBLICURLENABLEDLOCAL Raw Value-43',
        'zGenAlbum-ZCLOUDPUBLICURLENABLED Raw Value-44',
        'zGenAlbum-Public URL-45',
        'zGenAlbum-Key Asset Face Thumb Index-46',
        'zGenAlbum-Project Text Extension ID-47',
        'zGenAlbum-User Query Data-48',
        'zGenAlbum-Custom Query Parameters-49',
        'zGenAlbum-Project Data-50',
        'zCldShareAlbumInvRec-ZISMINE Raw Value-51',
        'zCldShareAlbumInvRec-ZINVITATIONSTATELOCAL Raw Value-52',
        'zCldShareAlbumInvRec-ZINVITATIONSTATE Raw Value-53',
        ('zCldShareAlbumInvRec-Subscription Date-54', 'datetime'),
        'zCldShareAlbumInvRec-Invitee First Name-55',
        'zCldShareAlbumInvRec-Invitee Last Name-56',
        'zCldShareAlbumInvRec-Invitee Full Name-57',
        'zCldShareAlbumInvRec-Invitee Hashed Person ID-58',
        'zCldShareAlbumInvRec-Invitee Email Key-59',
        'zCldShareAlbumInvRec-Album GUID-60',
        'zCldShareAlbumInvRec-Cloud GUID-61',
        'zGenAlbum-Project Render UUID-62',
        'zAlbumList-ZNEEDSREORDERINGNUMBER Raw Value-63')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("15")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Creation Date',
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',              
        DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',    
        zGenAlbum.ZCREATORBUNDLEID AS 'zGenAlbum-Creator Bundle ID',     
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        zGenAlbum.ZPENDINGITEMSTYPE AS 'zGenAlbum-ZPENDINGITEMSTYPE Raw Value',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        zGenAlbum.ZHASUNSEENCONTENT AS 'zGenAlbum-ZHASUNSEENCONTENT Raw Value',
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        zGenAlbum.Z_ENT AS 'zGenAlbum-Z_ENT Raw Value',
        zGenAlbum.ZKIND AS 'zGenAlbum-ZKIND Raw Value',
        zGenAlbum.ZCLOUDLOCALSTATE AS 'zGenAlbum-ZCLOUDLOCALSTATE Raw Value',
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        zGenAlbum.ZISOWNED AS 'zGenAlbum-ZISOWNED Raw Value',
        zGenAlbum.ZCLOUDRELATIONSHIPSTATE AS 'zGenAlbum-ZCLOUDRELATIONSHIPSTATE Raw Value',
        zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL AS 'zGenAlbum-ZCLOUDRELATIONSHIPSTATELOCAL Raw Value',
        zGenAlbum.ZCLOUDOWNEREMAILKEY AS 'zGenAlbum-Cloud Owner Mail Key',        
        zGenAlbum.ZCLOUDOWNERFIRSTNAME AS 'zGenAlbum-Cloud Owner Frist Name',        
        zGenAlbum.ZCLOUDOWNERLASTNAME AS 'zGenAlbum-Cloud Owner Last Name',        
        zGenAlbum.ZCLOUDOWNERFULLNAME AS 'zGenAlbum-Cloud Owner Full Name',
        zGenAlbum.ZCLOUDPERSONID AS 'zGenAlbum-Cloud Person ID',        
        zGenAlbum.ZCLOUDOWNERHASHEDPERSONID AS 'zGenAlbum-Cloud Owner Hashed Person ID',        
        zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL AS 'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL Raw Value',
        zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED AS 'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLED Raw Value',
        zGenAlbum.ZCLOUDALBUMSUBTYPE AS 'zGenAlbum-ZCLOUDALBUMSUBTYPE Raw Value',
        DateTime(zGenAlbum.ZCLOUDLASTCONTRIBUTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Contribution Date',        
        DateTime(zGenAlbum.ZCLOUDLASTINTERESTINGCHANGEDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Last Interesting Change Date',        
        zGenAlbum.ZCLOUDNOTIFICATIONSENABLED AS 'zGenAlbum-ZCLOUDNOTIFICATIONSENABLED Raw Value',
        zGenAlbum.ZISPINNED AS 'zGenAlbum-ZISPINNED Raw Value',
        zGenAlbum.ZCUSTOMSORTKEY AS 'zGenAlbum-ZCUSTOMSORTKEY Raw Value',
        zGenAlbum.ZCUSTOMSORTASCENDING AS 'zGenAlbum-ZCUSTOMSORTASCENDING Raw Value',
        zGenAlbum.ZISPROTOTYPE AS 'zGenAlbum-ZISPROTOTYPE Raw Value',
        zGenAlbum.ZPROJECTDOCUMENTTYPE AS 'zGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value',
        zGenAlbum.ZCUSTOMQUERYTYPE AS 'zGenAlbum-ZCUSTOMQUERYTYPE Raw Value',
        zGenAlbum.ZTRASHEDSTATE AS 'zGenAlbum-ZTRASHEDSTATE Raw Value',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        zGenAlbum.ZCLOUDDELETESTATE AS 'zGenAlbum-ZCLOUDDELETESTATE Raw Value',
        zGenAlbum.ZCLOUDOWNERISWHITELISTED AS 'zGenAlbum-ZCLOUDOWNERISWHITELISTED Raw Value',
        zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL AS 'zGenAlbum-ZCLOUDPUBLICURLENABLEDLOCAL Raw Value',
        zGenAlbum.ZCLOUDPUBLICURLENABLED AS 'zGenAlbum-ZCLOUDPUBLICURLENABLED Raw Value',
        zGenAlbum.ZPUBLICURL AS 'zGenAlbum-Public URL',        
        zGenAlbum.ZKEYASSETFACETHUMBNAILINDEX AS 'zGenAlbum-Key Asset Face Thumb Index',        
        zGenAlbum.ZPROJECTEXTENSIONIDENTIFIER AS 'zGenAlbum-Project Text Extension ID',        
        zGenAlbum.ZUSERQUERYDATA AS 'zGenAlbum-User Query Data',        
        zGenAlbum.ZCUSTOMQUERYPARAMETERS AS 'zGenAlbum-Custom Query Parameters',        
        zGenAlbum.ZPROJECTDATA AS 'zGenAlbum-Project Data',
        zCldShareAlbumInvRec.ZISMINE AS 'zCldShareAlbumInvRec-ZISMINE Raw Value',
        zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL AS 'zCldShareAlbumInvRec-ZINVITATIONSTATELOCAL Raw Value',
        zCldShareAlbumInvRec.ZINVITATIONSTATE AS 'zCldShareAlbumInvRec-ZINVITATIONSTATE Raw Value',
        DateTime(zCldShareAlbumInvRec.ZINVITEESUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zCldShareAlbumInvRec-Subscription Date',
        zCldShareAlbumInvRec.ZINVITEEFIRSTNAME AS 'zCldShareAlbumInvRec-Invitee First Name',
        zCldShareAlbumInvRec.ZINVITEELASTNAME AS 'zCldShareAlbumInvRec-Invitee Last Name',
        zCldShareAlbumInvRec.ZINVITEEFULLNAME AS 'zCldShareAlbumInvRec-Invitee Full Name',
        zCldShareAlbumInvRec.ZINVITEEHASHEDPERSONID AS 'zCldShareAlbumInvRec-Invitee Hashed Person ID',
        zCldShareAlbumInvRec.ZINVITEEEMAILKEY AS 'zCldShareAlbumInvRec-Invitee Email Key',    
        zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID',
        zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID',
        zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID',        
        zAlbumList.ZNEEDSREORDERINGNUMBER AS 'zAlbumList-ZNEEDSREORDERINGNUMBER Raw Value'
        FROM ZGENERICALBUM zGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN Z_25ALBUMLISTS z25AlbumLists ON z25AlbumLists.Z_25ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z25AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
        ORDER BY zGenAlbum.ZCREATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
            row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
            row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
            row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
            row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
            row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
            row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
            row[64], row[65]))

        data_headers = (('zGenAlbum-Cloud Creation Date-0', 'datetime'),
        ('zGenAlbum-Creation Date-1', 'datetime'),
        ('zGenAlbum-Start Date-2', 'datetime'),
        ('zGenAlbum-End Date-3', 'datetime'),
        ('zGenAlbum-Cloud Subscription Date-4', 'datetime'),
        'zGenAlbum- Title-User&System Applied-5',
        'zGenAlbum-UUID-6',
        'zGenAlbum-Cloud GUID-7',
        'zGenAlbum-Creator Bundle ID-8',
        'zGenAlbum-Pending Items Count-9',
        'zGenAlbum-ZPENDINGITEMSTYPE Raw Value-10',
        'zGenAlbum- Cached Photos Count-11',
        'zGenAlbum- Cached Videos Count-12',
        'zGenAlbum- Cached Count-13',
        'zGenAlbum-ZHASUNSEENCONTENT Raw Value-14',
        'zGenAlbum-Unseen Asset Count-15',
        'zGenAlbum-Z_ENT Raw Value-16',
        'zGenAlbum-ZKIND Raw Value-17',
        'zGenAlbum-ZCLOUDLOCALSTATE Raw Value-18',
        'zGenAlbum-Sync Event Order Key-19',
        'zGenAlbum-ZISOWNED Raw Value-20',
        'zGenAlbum-ZCLOUDRELATIONSHIPSTATE Raw Value-21',
        'zGenAlbum-ZCLOUDRELATIONSHIPSTATELOCAL Raw Value-22',
        'zGenAlbum-Cloud Owner Mail Key-23',
        'zGenAlbum-Cloud Owner Frist Name-24',
        'zGenAlbum-Cloud Owner Last Name-25',
        'zGenAlbum-Cloud Owner Full Name-26',
        'zGenAlbum-Cloud Person ID-27',
        'zGenAlbum-Cloud Owner Hashed Person ID-28',
        'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL Raw Value-29',
        'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLED Raw Value-30',
        'zGenAlbum-ZCLOUDALBUMSUBTYPE Raw Value-31',
        ('zGenAlbum-Cloud Contribution Date-32', 'datetime'),
        ('zGenAlbum-Cloud Last Interesting Change Date-33', 'datetime'),
        'zGenAlbum-ZCLOUDNOTIFICATIONSENABLED Raw Value-34',
        'zGenAlbum-ZISPINNED Raw Value-35',
        'zGenAlbum-ZCUSTOMSORTKEY Raw Value-36',
        'zGenAlbum-ZCUSTOMSORTASCENDING Raw Value-37',
        'zGenAlbum-ZISPROTOTYPE Raw Value-38',
        'zGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value-39',
        'zGenAlbum-ZCUSTOMQUERYTYPE Raw Value-40',
        'zGenAlbum-ZTRASHEDSTATE Raw Value-41',
        ('zGenAlbum-Trash Date-42', 'datetime'),
        'zGenAlbum-ZCLOUDDELETESTATE Raw Value-43',
        'zGenAlbum-ZCLOUDOWNERISWHITELISTED Raw Value-44',
        'zGenAlbum-ZCLOUDPUBLICURLENABLEDLOCAL Raw Value-45',
        'zGenAlbum-ZCLOUDPUBLICURLENABLED Raw Value-46',
        'zGenAlbum-Public URL-47',
        'zGenAlbum-Key Asset Face Thumb Index-48',
        'zGenAlbum-Project Text Extension ID-49',
        'zGenAlbum-User Query Data-50',
        'zGenAlbum-Custom Query Parameters-51',
        'zGenAlbum-Project Data-52',
        'zCldShareAlbumInvRec-ZISMINE Raw Value-53',
        'zCldShareAlbumInvRec-ZINVITATIONSTATELOCAL Raw Value-54',
        'zCldShareAlbumInvRec-ZINVITATIONSTATE Raw Value-55',
        ('zCldShareAlbumInvRec-Subscription Date-56', 'datetime'),
        'zCldShareAlbumInvRec-Invitee First Name-57',
        'zCldShareAlbumInvRec-Invitee Last Name-58',
        'zCldShareAlbumInvRec-Invitee Full Name-59',
        'zCldShareAlbumInvRec-Invitee Hashed Person ID-60',
        'zCldShareAlbumInvRec-Invitee Email Key-61',
        'zCldShareAlbumInvRec-Album GUID-62',
        'zCldShareAlbumInvRec-Cloud GUID-63',
        'zGenAlbum-Project Render UUID-64',
        'zAlbumList-ZNEEDSREORDERINGNUMBER Raw Value-65')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Creation Date',
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',            
        DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',    
        zGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zGenAlbum-Imported by Bundle Identifier',               
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        zGenAlbum.ZPENDINGITEMSTYPE AS 'zGenAlbum-ZPENDINGITEMSTYPE Raw Value',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        zGenAlbum.ZHASUNSEENCONTENT AS 'zGenAlbum-ZHASUNSEENCONTENT Raw Value',
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        zGenAlbum.Z_ENT AS 'zGenAlbum-Z_ENT Raw Value',
        zGenAlbum.ZKIND AS 'zGenAlbum-ZKIND Raw Value',
        zGenAlbum.ZCLOUDLOCALSTATE AS 'zGenAlbum-ZCLOUDLOCALSTATE Raw Value',
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        zGenAlbum.ZISOWNED AS 'zGenAlbum-ZISOWNED Raw Value',
        zGenAlbum.ZCLOUDRELATIONSHIPSTATE AS 'zGenAlbum-ZCLOUDRELATIONSHIPSTATE Raw Value',
        zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL AS 'zGenAlbum-ZCLOUDRELATIONSHIPSTATELOCAL Raw Value',
        zGenAlbum.ZCLOUDOWNEREMAILKEY AS 'zGenAlbum-Cloud Owner Mail Key',        
        zGenAlbum.ZCLOUDOWNERFIRSTNAME AS 'zGenAlbum-Cloud Owner Frist Name',        
        zGenAlbum.ZCLOUDOWNERLASTNAME AS 'zGenAlbum-Cloud Owner Last Name',        
        zGenAlbum.ZCLOUDOWNERFULLNAME AS 'zGenAlbum-Cloud Owner Full Name',
        zGenAlbum.ZCLOUDPERSONID AS 'zGenAlbum-Cloud Person ID',        
        zGenAlbum.ZCLOUDOWNERHASHEDPERSONID AS 'zGenAlbum-Cloud Owner Hashed Person ID',        
        zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL AS 'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL Raw Value',
        zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED AS 'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLED Raw Value',
        zGenAlbum.ZCLOUDALBUMSUBTYPE AS 'zGenAlbum-ZCLOUDALBUMSUBTYPE Raw Value',
        DateTime(zGenAlbum.ZCLOUDLASTCONTRIBUTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Contribution Date',        
        DateTime(zGenAlbum.ZCLOUDLASTINTERESTINGCHANGEDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Last Interesting Change Date',        
        zGenAlbum.ZCLOUDNOTIFICATIONSENABLED AS 'zGenAlbum-ZCLOUDNOTIFICATIONSENABLED Raw Value',
        zGenAlbum.ZISPINNED AS 'zGenAlbum-ZISPINNED Raw Value',
        zGenAlbum.ZCUSTOMSORTKEY AS 'zGenAlbum-ZCUSTOMSORTKEY Raw Value',
        zGenAlbum.ZCUSTOMSORTASCENDING AS 'zGenAlbum-ZCUSTOMSORTASCENDING Raw Value',
        zGenAlbum.ZISPROTOTYPE AS 'zGenAlbum-ZISPROTOTYPE Raw Value',
        zGenAlbum.ZPROJECTDOCUMENTTYPE AS 'zGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value',
        zGenAlbum.ZCUSTOMQUERYTYPE AS 'zGenAlbum-ZCUSTOMQUERYTYPE Raw Value',
        zGenAlbum.ZTRASHEDSTATE AS 'zGenAlbum-ZTRASHEDSTATE Raw Value',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        zGenAlbum.ZCLOUDDELETESTATE AS 'zGenAlbum-ZCLOUDDELETESTATE Raw Value',
        zGenAlbum.ZCLOUDOWNERISWHITELISTED AS 'zGenAlbum-ZCLOUDOWNERISWHITELISTED Raw Value',
        zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL AS 'zGenAlbum-ZCLOUDPUBLICURLENABLEDLOCAL Raw Value',
        zGenAlbum.ZCLOUDPUBLICURLENABLED AS 'zGenAlbum-ZCLOUDPUBLICURLENABLED Raw Value',
        zGenAlbum.ZPUBLICURL AS 'zGenAlbum-Public URL',        
        zGenAlbum.ZKEYASSETFACETHUMBNAILINDEX AS 'zGenAlbum-Key Asset Face Thumb Index',        
        zGenAlbum.ZPROJECTEXTENSIONIDENTIFIER AS 'zGenAlbum-Project Text Extension ID',        
        zGenAlbum.ZUSERQUERYDATA AS 'zGenAlbum-User Query Data',        
        zGenAlbum.ZCUSTOMQUERYPARAMETERS AS 'zGenAlbum-Custom Query Parameters',        
        zGenAlbum.ZPROJECTDATA AS 'zGenAlbum-Project Data',
        zCldShareAlbumInvRec.ZISMINE AS 'zCldShareAlbumInvRec-ZISMINE Raw Value',
        zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL AS 'zCldShareAlbumInvRec-ZINVITATIONSTATELOCAL Raw Value',
        zCldShareAlbumInvRec.ZINVITATIONSTATE AS 'zCldShareAlbumInvRec-ZINVITATIONSTATE Raw Value',
        DateTime(zCldShareAlbumInvRec.ZINVITEESUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zCldShareAlbumInvRec-Subscription Date',
        zCldShareAlbumInvRec.ZINVITEEFIRSTNAME AS 'zCldShareAlbumInvRec-Invitee First Name',
        zCldShareAlbumInvRec.ZINVITEELASTNAME AS 'zCldShareAlbumInvRec-Invitee Last Name',
        zCldShareAlbumInvRec.ZINVITEEFULLNAME AS 'zCldShareAlbumInvRec-Invitee Full Name',
        zCldShareAlbumInvRec.ZINVITEEHASHEDPERSONID AS 'zCldShareAlbumInvRec-Invitee Hashed Person ID',
        zCldShareAlbumInvRec.ZINVITEEEMAILKEY AS 'zCldShareAlbumInvRec-Invitee Email Key',    
        zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID',
        zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID',
        zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID',        
        zAlbumList.ZNEEDSREORDERINGNUMBER AS 'zAlbumList-ZNEEDSREORDERINGNUMBER Raw Value'
        FROM ZGENERICALBUM zGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN Z_26ALBUMLISTS z26AlbumLists ON z26AlbumLists.Z_26ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z26AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
        ORDER BY zGenAlbum.ZCREATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
            row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
            row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
            row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
            row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
            row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
            row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
            row[64], row[65]))

        data_headers = (('zGenAlbum-Cloud Creation Date-0', 'datetime'),
        ('zGenAlbum-Creation Date-1', 'datetime'),
        ('zGenAlbum-Start Date-2', 'datetime'),
        ('zGenAlbum-End Date-3', 'datetime'),
        ('zGenAlbum-Cloud Subscription Date-4', 'datetime'),
        'zGenAlbum- Title-User&System Applied-5',
        'zGenAlbum-UUID-6',
        'zGenAlbum-Cloud GUID-7',
        'zGenAlbum-Imported by Bundle Identifier-8',
        'zGenAlbum-Pending Items Count-9',
        'zGenAlbum-ZPENDINGITEMSTYPE Raw Value-10',
        'zGenAlbum- Cached Photos Count-11',
        'zGenAlbum- Cached Videos Count-12',
        'zGenAlbum- Cached Count-13',
        'zGenAlbum-ZHASUNSEENCONTENT Raw Value-14',
        'zGenAlbum-Unseen Asset Count-15',
        'zGenAlbum-Z_ENT Raw Value-16',
        'zGenAlbum-ZKIND Raw Value-17',
        'zGenAlbum-ZCLOUDLOCALSTATE Raw Value-18',
        'zGenAlbum-Sync Event Order Key-19',
        'zGenAlbum-ZISOWNED Raw Value-20',
        'zGenAlbum-ZCLOUDRELATIONSHIPSTATE Raw Value-21',
        'zGenAlbum-ZCLOUDRELATIONSHIPSTATELOCAL Raw Value-22',
        'zGenAlbum-Cloud Owner Mail Key-23',
        'zGenAlbum-Cloud Owner Frist Name-24',
        'zGenAlbum-Cloud Owner Last Name-25',
        'zGenAlbum-Cloud Owner Full Name-26',
        'zGenAlbum-Cloud Person ID-27',
        'zGenAlbum-Cloud Owner Hashed Person ID-28',
        'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL Raw Value-29',
        'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLED Raw Value-30',
        'zGenAlbum-ZCLOUDALBUMSUBTYPE Raw Value-31',
        ('zGenAlbum-Cloud Contribution Date-32', 'datetime'),
        ('zGenAlbum-Cloud Last Interesting Change Date-33', 'datetime'),
        'zGenAlbum-ZCLOUDNOTIFICATIONSENABLED Raw Value-34',
        'zGenAlbum-ZISPINNED Raw Value-35',
        'zGenAlbum-ZCUSTOMSORTKEY Raw Value-36',
        'zGenAlbum-ZCUSTOMSORTASCENDING Raw Value-37',
        'zGenAlbum-ZISPROTOTYPE Raw Value-38',
        'zGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value-39',
        'zGenAlbum-ZCUSTOMQUERYTYPE Raw Value-40',
        'zGenAlbum-ZTRASHEDSTATE Raw Value-41',
        ('zGenAlbum-Trash Date-42', 'datetime'),
        'zGenAlbum-ZCLOUDDELETESTATE Raw Value-43',
        'zGenAlbum-ZCLOUDOWNERISWHITELISTED Raw Value-44',
        'zGenAlbum-ZCLOUDPUBLICURLENABLEDLOCAL Raw Value-45',
        'zGenAlbum-ZCLOUDPUBLICURLENABLED Raw Value-46',
        'zGenAlbum-Public URL-47',
        'zGenAlbum-Key Asset Face Thumb Index-48',
        'zGenAlbum-Project Text Extension ID-49',
        'zGenAlbum-User Query Data-50',
        'zGenAlbum-Custom Query Parameters-51',
        'zGenAlbum-Project Data-52',
        'zCldShareAlbumInvRec-ZISMINE Raw Value-53',
        'zCldShareAlbumInvRec-ZINVITATIONSTATELOCAL Raw Value-54',
        'zCldShareAlbumInvRec-ZINVITATIONSTATE Raw Value-55',
        ('zCldShareAlbumInvRec-Subscription Date-56', 'datetime'),
        'zCldShareAlbumInvRec-Invitee First Name-57',
        'zCldShareAlbumInvRec-Invitee Last Name-58',
        'zCldShareAlbumInvRec-Invitee Full Name-59',
        'zCldShareAlbumInvRec-Invitee Hashed Person ID-60',
        'zCldShareAlbumInvRec-Invitee Email Key-61',
        'zCldShareAlbumInvRec-Album GUID-62',
        'zCldShareAlbumInvRec-Cloud GUID-63',
        'zGenAlbum-Project Render UUID-64',
        'zAlbumList-ZNEEDSREORDERINGNUMBER Raw Value-65')
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
        DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Creation Date',
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',             
        DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',    
        zGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zGenAlbum-Imported by Bundle Identifier',             
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        zGenAlbum.ZPENDINGITEMSTYPE AS 'zGenAlbum-ZPENDINGITEMSTYPE Raw Value',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        zGenAlbum.ZHASUNSEENCONTENT AS 'zGenAlbum-ZHASUNSEENCONTENT Raw Value',
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        zGenAlbum.Z_ENT AS 'zGenAlbum-Z_ENT Raw Value',
        zGenAlbum.ZKIND AS 'zGenAlbum-ZKIND Raw Value',
        zGenAlbum.ZCLOUDLOCALSTATE AS 'zGenAlbum-ZCLOUDLOCALSTATE Raw Value',
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        zGenAlbum.ZISOWNED AS 'zGenAlbum-ZISOWNED Raw Value',
        zGenAlbum.ZCLOUDRELATIONSHIPSTATE AS 'zGenAlbum-ZCLOUDRELATIONSHIPSTATE Raw Value',
        zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL AS 'zGenAlbum-ZCLOUDRELATIONSHIPSTATELOCAL Raw Value',
        zGenAlbum.ZCLOUDOWNEREMAILKEY AS 'zGenAlbum-Cloud Owner Mail Key',        
        zGenAlbum.ZCLOUDOWNERFIRSTNAME AS 'zGenAlbum-Cloud Owner Frist Name',        
        zGenAlbum.ZCLOUDOWNERLASTNAME AS 'zGenAlbum-Cloud Owner Last Name',        
        zGenAlbum.ZCLOUDOWNERFULLNAME AS 'zGenAlbum-Cloud Owner Full Name',
        zGenAlbum.ZCLOUDPERSONID AS 'zGenAlbum-Cloud Person ID',        
        zGenAlbum.ZCLOUDOWNERHASHEDPERSONID AS 'zGenAlbum-Cloud Owner Hashed Person ID',        
        zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL AS 'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL Raw Value',
        zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED AS 'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLED Raw Value',
        zGenAlbum.ZCLOUDALBUMSUBTYPE AS 'zGenAlbum-ZCLOUDALBUMSUBTYPE Raw Value',
        DateTime(zGenAlbum.ZCLOUDLASTCONTRIBUTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Contribution Date',        
        DateTime(zGenAlbum.ZCLOUDLASTINTERESTINGCHANGEDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Last Interesting Change Date',        
        zGenAlbum.ZCLOUDNOTIFICATIONSENABLED AS 'zGenAlbum-ZCLOUDNOTIFICATIONSENABLED Raw Value',
        zGenAlbum.ZISPINNED AS 'zGenAlbum-ZISPINNED Raw Value',
        zGenAlbum.ZCUSTOMSORTKEY AS 'zGenAlbum-ZCUSTOMSORTKEY Raw Value',
        zGenAlbum.ZCUSTOMSORTASCENDING AS 'zGenAlbum-ZCUSTOMSORTASCENDING Raw Value',
        zGenAlbum.ZISPROTOTYPE AS 'zGenAlbum-ZISPROTOTYPE Raw Value',
        zGenAlbum.ZPROJECTDOCUMENTTYPE AS 'zGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value',
        zGenAlbum.ZCUSTOMQUERYTYPE AS 'zGenAlbum-ZCUSTOMQUERYTYPE Raw Value',
        zGenAlbum.ZTRASHEDSTATE AS 'zGenAlbum-ZTRASHEDSTATE Raw Value',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        zGenAlbum.ZCLOUDDELETESTATE AS 'zGenAlbum-ZCLOUDDELETESTATE Raw Value',
        zGenAlbum.ZCLOUDOWNERISWHITELISTED AS 'zGenAlbum-ZCLOUDOWNERISWHITELISTED Raw Value',
        zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL AS 'zGenAlbum-ZCLOUDPUBLICURLENABLEDLOCAL Raw Value',
        zGenAlbum.ZCLOUDPUBLICURLENABLED AS 'zGenAlbum-ZCLOUDPUBLICURLENABLED Raw Value',
        zGenAlbum.ZPUBLICURL AS 'zGenAlbum-Public URL',        
        zGenAlbum.ZKEYASSETFACETHUMBNAILINDEX AS 'zGenAlbum-Key Asset Face Thumb Index',        
        zGenAlbum.ZPROJECTEXTENSIONIDENTIFIER AS 'zGenAlbum-Project Text Extension ID',        
        zGenAlbum.ZUSERQUERYDATA AS 'zGenAlbum-User Query Data',        
        zGenAlbum.ZCUSTOMQUERYPARAMETERS AS 'zGenAlbum-Custom Query Parameters',        
        zGenAlbum.ZPROJECTDATA AS 'zGenAlbum-Project Data',        
        zGenAlbum.ZSEARCHINDEXREBUILDSTATE AS 'zGenAlbum-ZSEARCHINDEXREBUILDSTATE Raw Value',
        zGenAlbum.ZDUPLICATETYPE AS 'zGenAlbum-ZDUPLICATETYPE Raw Value',
        zGenAlbum.ZPRIVACYSTATE AS 'zGenAlbum-ZPRIVACYSTATE Raw Value',
        zCldShareAlbumInvRec.ZUUID AS 'zCldShareAlbumInvRec-zUUID',
        zCldShareAlbumInvRec.ZISMINE AS 'zCldShareAlbumInvRec-ZISMINE Raw Value',
        zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL AS 'zCldShareAlbumInvRec-ZINVITATIONSTATELOCAL Raw Value',
        zCldShareAlbumInvRec.ZINVITATIONSTATE AS 'zCldShareAlbumInvRec-ZINVITATIONSTATE Raw Value',
        DateTime(zCldShareAlbumInvRec.ZINVITEESUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zCldShareAlbumInvRec-Subscription Date',
        zCldShareAlbumInvRec.ZINVITEEFIRSTNAME AS 'zCldShareAlbumInvRec-Invitee First Name',
        zCldShareAlbumInvRec.ZINVITEELASTNAME AS 'zCldShareAlbumInvRec-Invitee Last Name',
        zCldShareAlbumInvRec.ZINVITEEFULLNAME AS 'zCldShareAlbumInvRec-Invitee Full Name',
        zCldShareAlbumInvRec.ZINVITEEHASHEDPERSONID AS 'zCldShareAlbumInvRec-Invitee Hashed Person ID',
        zCldShareAlbumInvRec.ZINVITEEEMAILKEY AS 'zCldShareAlbumInvRec-Invitee Email Key',    
        zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID',
        zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID',
        zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID',        
        zAlbumList.ZNEEDSREORDERINGNUMBER AS 'zAlbumList-ZNEEDSREORDERINGNUMBER Raw Value'
        FROM ZGENERICALBUM zGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN Z_27ALBUMLISTS z27AlbumLists ON z27AlbumLists.Z_27ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z27AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
        ORDER BY zGenAlbum.ZCREATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
            row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
            row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
            row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
            row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
            row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
            row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
            row[64], row[65], row[66], row[67], row[68], row[69]))

        data_headers = (('zGenAlbum-Cloud Creation Date-0', 'datetime'),
        ('zGenAlbum-Creation Date-1', 'datetime'),
        ('zGenAlbum-Start Date-2', 'datetime'),
        ('zGenAlbum-End Date-3', 'datetime'),
        ('zGenAlbum-Cloud Subscription Date-4', 'datetime'),
        'zGenAlbum- Title-User&System Applied-5',
        'zGenAlbum-UUID-6',
        'zGenAlbum-Cloud GUID-7',
        'zGenAlbum-Imported by Bundle Identifier-8',
        'zGenAlbum-Pending Items Count-9',
        'zGenAlbum-ZPENDINGITEMSTYPE Raw Value-10',
        'zGenAlbum- Cached Photos Count-11',
        'zGenAlbum- Cached Videos Count-12',
        'zGenAlbum- Cached Count-13',
        'zGenAlbum-ZHASUNSEENCONTENT Raw Value-14',
        'zGenAlbum-Unseen Asset Count-15',
        'zGenAlbum-Z_ENT Raw Value-16',
        'zGenAlbum-ZKIND Raw Value-17',
        'zGenAlbum-ZCLOUDLOCALSTATE Raw Value-18',
        'zGenAlbum-Sync Event Order Key-19',
        'zGenAlbum-ZISOWNED Raw Value-20',
        'zGenAlbum-ZCLOUDRELATIONSHIPSTATE Raw Value-21',
        'zGenAlbum-ZCLOUDRELATIONSHIPSTATELOCAL Raw Value-22',
        'zGenAlbum-Cloud Owner Mail Key-23',
        'zGenAlbum-Cloud Owner First Name-24',
        'zGenAlbum-Cloud Owner Last Name-25',
        'zGenAlbum-Cloud Owner Full Name-26',
        'zGenAlbum-Cloud Person ID-27',
        'zGenAlbum-Cloud Owner Hashed Person ID-28',
        'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL Raw Value-29',
        'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLED Raw Value-30',
        'zGenAlbum-ZCLOUDALBUMSUBTYPE Raw Value-31',
        ('zGenAlbum-Cloud Contribution Date-32', 'datetime'),
        ('zGenAlbum-Cloud Last Interesting Change Date-33', 'datetime'),
        'zGenAlbum-ZCLOUDNOTIFICATIONSENABLED Raw Value-34',
        'zGenAlbum-ZISPINNED Raw Value-35',
        'zGenAlbum-ZCUSTOMSORTKEY Raw Value-36',
        'zGenAlbum-ZCUSTOMSORTASCENDING Raw Value-37',
        'zGenAlbum-ZISPROTOTYPE Raw Value-38',
        'zGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value-39',
        'zGenAlbum-ZCUSTOMQUERYTYPE Raw Value-40',
        'zGenAlbum-ZTRASHEDSTATE Raw Value-41',
        ('zGenAlbum-Trash Date-42', 'datetime'),
        'zGenAlbum-ZCLOUDDELETESTATE Raw Value-43',
        'zGenAlbum-ZCLOUDOWNERISWHITELISTED Raw Value-44',
        'zGenAlbum-ZCLOUDPUBLICURLENABLEDLOCAL Raw Value-45',
        'zGenAlbum-ZCLOUDPUBLICURLENABLED Raw Value-46',
        'zGenAlbum-Public URL-47',
        'zGenAlbum-Key Asset Face Thumb Index-48',
        'zGenAlbum-Project Text Extension ID-49',
        'zGenAlbum-User Query Data-50',
        'zGenAlbum-Custom Query Parameters-51',
        'zGenAlbum-Project Data-52',
        'zGenAlbum-ZSEARCHINDEXREBUILDSTATE Raw Value-53',
        'zGenAlbum-ZDUPLICATETYPE Raw Value-54',
        'zGenAlbum-ZPRIVACYSTATE Raw Value-55',
        'zCldShareAlbumInvRec-zUUID-56',
        'zCldShareAlbumInvRec-ZISMINE Raw Value-57',
        'zCldShareAlbumInvRec-ZINVITATIONSTATELOCAL Raw Value-58',
        'zCldShareAlbumInvRec-ZINVITATIONSTATE Raw Value-59',
        ('zCldShareAlbumInvRec-Subscription Date-60', 'datetime'),
        'zCldShareAlbumInvRec-Invitee First Name-61',
        'zCldShareAlbumInvRec-Invitee Last Name-62',
        'zCldShareAlbumInvRec-Invitee Full Name-63',
        'zCldShareAlbumInvRec-Invitee Hashed Person ID-64',
        'zCldShareAlbumInvRec-Invitee Email Key-65',
        'zCldShareAlbumInvRec-Album GUID-66',
        'zCldShareAlbumInvRec-Cloud GUID-67',
        'zGenAlbum-Project Render UUID-68',
        'zAlbumList-ZNEEDSREORDERINGNUMBER Raw Value-69')
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
        DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Creation Date',
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',             
        DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',    
        zGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zGenAlbum-Imported by Bundle Identifier',             
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        zGenAlbum.ZPENDINGITEMSTYPE AS 'zGenAlbum-ZPENDINGITEMSTYPE Raw Value',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        zGenAlbum.ZHASUNSEENCONTENT AS 'zGenAlbum-ZHASUNSEENCONTENT Raw Value',
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        zGenAlbum.Z_ENT AS 'zGenAlbum-Z_ENT Raw Value',
        zGenAlbum.ZKIND AS 'zGenAlbum-ZKIND Raw Value',
        zGenAlbum.ZCLOUDLOCALSTATE AS 'zGenAlbum-ZCLOUDLOCALSTATE Raw Value',
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        zGenAlbum.ZISOWNED AS 'zGenAlbum-ZISOWNED Raw Value',
        zGenAlbum.ZCLOUDRELATIONSHIPSTATE AS 'zGenAlbum-ZCLOUDRELATIONSHIPSTATE Raw Value',
        zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL AS 'zGenAlbum-ZCLOUDRELATIONSHIPSTATELOCAL Raw Value',
        zGenAlbum.ZCLOUDOWNEREMAILKEY AS 'zGenAlbum-Cloud Owner Mail Key',        
        zGenAlbum.ZCLOUDOWNERFIRSTNAME AS 'zGenAlbum-Cloud Owner Frist Name',        
        zGenAlbum.ZCLOUDOWNERLASTNAME AS 'zGenAlbum-Cloud Owner Last Name',        
        zGenAlbum.ZCLOUDOWNERFULLNAME AS 'zGenAlbum-Cloud Owner Full Name',
        zGenAlbum.ZCLOUDPERSONID AS 'zGenAlbum-Cloud Person ID',        
        zGenAlbum.ZCLOUDOWNERHASHEDPERSONID AS 'zGenAlbum-Cloud Owner Hashed Person ID',        
        zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL AS 'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL Raw Value',
        zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED AS 'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLED Raw Value',
        zGenAlbum.ZCLOUDALBUMSUBTYPE AS 'zGenAlbum-ZCLOUDALBUMSUBTYPE Raw Value',
        DateTime(zGenAlbum.ZCLOUDLASTCONTRIBUTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Contribution Date',        
        DateTime(zGenAlbum.ZCLOUDLASTINTERESTINGCHANGEDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Last Interesting Change Date',        
        zGenAlbum.ZCLOUDNOTIFICATIONSENABLED AS 'zGenAlbum-ZCLOUDNOTIFICATIONSENABLED Raw Value',
        zGenAlbum.ZISPINNED AS 'zGenAlbum-ZISPINNED Raw Value',
        zGenAlbum.ZCUSTOMSORTKEY AS 'zGenAlbum-ZCUSTOMSORTKEY Raw Value',
        zGenAlbum.ZCUSTOMSORTASCENDING AS 'zGenAlbum-ZCUSTOMSORTASCENDING Raw Value',
        zGenAlbum.ZISPROTOTYPE AS 'zGenAlbum-ZISPROTOTYPE Raw Value',
        zGenAlbum.ZPROJECTDOCUMENTTYPE AS 'zGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value',
        zGenAlbum.ZCUSTOMQUERYTYPE AS 'zGenAlbum-ZCUSTOMQUERYTYPE Raw Value',
        zGenAlbum.ZTRASHEDSTATE AS 'zGenAlbum-ZTRASHEDSTATE Raw Value',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        zGenAlbum.ZCLOUDDELETESTATE AS 'zGenAlbum-ZCLOUDDELETESTATE Raw Value',
        zGenAlbum.ZCLOUDOWNERISWHITELISTED AS 'zGenAlbum-ZCLOUDOWNERISWHITELISTED Raw Value',
        zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL AS 'zGenAlbum-ZCLOUDPUBLICURLENABLEDLOCAL Raw Value',
        zGenAlbum.ZCLOUDPUBLICURLENABLED AS 'zGenAlbum-ZCLOUDPUBLICURLENABLED Raw Value',
        zGenAlbum.ZPUBLICURL AS 'zGenAlbum-Public URL',        
        zGenAlbum.ZKEYASSETFACETHUMBNAILINDEX AS 'zGenAlbum-Key Asset Face Thumb Index',        
        zGenAlbum.ZPROJECTEXTENSIONIDENTIFIER AS 'zGenAlbum-Project Text Extension ID',        
        zGenAlbum.ZUSERQUERYDATA AS 'zGenAlbum-User Query Data',        
        zGenAlbum.ZCUSTOMQUERYPARAMETERS AS 'zGenAlbum-Custom Query Parameters',        
        zGenAlbum.ZPROJECTDATA AS 'zGenAlbum-Project Data',        
        zGenAlbum.ZSEARCHINDEXREBUILDSTATE AS 'zGenAlbum-ZSEARCHINDEXREBUILDSTATE Raw Value',
        zGenAlbum.ZDUPLICATETYPE AS 'zGenAlbum-ZDUPLICATETYPE Raw Value',
        zGenAlbum.ZPRIVACYSTATE AS 'zGenAlbum-ZPRIVACYSTATE Raw Value',
        zCldShareAlbumInvRec.ZUUID AS 'zCldShareAlbumInvRec-zUUID',
        zCldShareAlbumInvRec.ZISMINE AS 'zCldShareAlbumInvRec-ZISMINE Raw Value',
        zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL AS 'zCldShareAlbumInvRec-ZINVITATIONSTATELOCAL Raw Value',
        zCldShareAlbumInvRec.ZINVITATIONSTATE AS 'zCldShareAlbumInvRec-ZINVITATIONSTATE Raw Value',
        DateTime(zCldShareAlbumInvRec.ZINVITEESUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zCldShareAlbumInvRec-Subscription Date',
        zCldShareAlbumInvRec.ZINVITEEFIRSTNAME AS 'zCldShareAlbumInvRec-Invitee First Name',
        zCldShareAlbumInvRec.ZINVITEELASTNAME AS 'zCldShareAlbumInvRec-Invitee Last Name',
        zCldShareAlbumInvRec.ZINVITEEFULLNAME AS 'zCldShareAlbumInvRec-Invitee Full Name',
        zCldShareAlbumInvRec.ZINVITEEHASHEDPERSONID AS 'zCldShareAlbumInvRec-Invitee Hashed Person ID',
        zCldShareAlbumInvRec.ZINVITEEEMAILKEY AS 'zCldShareAlbumInvRec-Invitee Email Key',    
        zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID',
        zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID',
        zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID',        
        zAlbumList.ZNEEDSREORDERINGNUMBER AS 'zAlbumList-ZNEEDSREORDERINGNUMBER Raw Value'
        FROM ZGENERICALBUM zGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN Z_28ALBUMLISTS z28AlbumLists ON z28AlbumLists.Z_28ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z28AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
        ORDER BY zGenAlbum.ZCREATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
            row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
            row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
            row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
            row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
            row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
            row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
            row[64], row[65], row[66], row[67], row[68], row[69]))

        data_headers = (('zGenAlbum-Cloud Creation Date-0', 'datetime'),
        ('zGenAlbum-Creation Date-1', 'datetime'),
        ('zGenAlbum-Start Date-2', 'datetime'),
        ('zGenAlbum-End Date-3', 'datetime'),
        ('zGenAlbum-Cloud Subscription Date-4', 'datetime'),
        'zGenAlbum- Title-User&System Applied-5',
        'zGenAlbum-UUID-6',
        'zGenAlbum-Cloud GUID-7',
        'zGenAlbum-Imported by Bundle Identifier-8',
        'zGenAlbum-Pending Items Count-9',
        'zGenAlbum-ZPENDINGITEMSTYPE Raw Value-10',
        'zGenAlbum- Cached Photos Count-11',
        'zGenAlbum- Cached Videos Count-12',
        'zGenAlbum- Cached Count-13',
        'zGenAlbum-ZHASUNSEENCONTENT Raw Value-14',
        'zGenAlbum-Unseen Asset Count-15',
        'zGenAlbum-Z_ENT Raw Value-16',
        'zGenAlbum-ZKIND Raw Value-17',
        'zGenAlbum-ZCLOUDLOCALSTATE Raw Value-18',
        'zGenAlbum-Sync Event Order Key-19',
        'zGenAlbum-ZISOWNED Raw Value-20',
        'zGenAlbum-ZCLOUDRELATIONSHIPSTATE Raw Value-21',
        'zGenAlbum-ZCLOUDRELATIONSHIPSTATELOCAL Raw Value-22',
        'zGenAlbum-Cloud Owner Mail Key-23',
        'zGenAlbum-Cloud Owner First Name-24',
        'zGenAlbum-Cloud Owner Last Name-25',
        'zGenAlbum-Cloud Owner Full Name-26',
        'zGenAlbum-Cloud Person ID-27',
        'zGenAlbum-Cloud Owner Hashed Person ID-28',
        'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL Raw Value-29',
        'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLED Raw Value-30',
        'zGenAlbum-ZCLOUDALBUMSUBTYPE Raw Value-31',
        ('zGenAlbum-Cloud Contribution Date-32', 'datetime'),
        ('zGenAlbum-Cloud Last Interesting Change Date-33', 'datetime'),
        'zGenAlbum-ZCLOUDNOTIFICATIONSENABLED Raw Value-34',
        'zGenAlbum-ZISPINNED Raw Value-35',
        'zGenAlbum-ZCUSTOMSORTKEY Raw Value-36',
        'zGenAlbum-ZCUSTOMSORTASCENDING Raw Value-37',
        'zGenAlbum-ZISPROTOTYPE Raw Value-38',
        'zGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value-39',
        'zGenAlbum-ZCUSTOMQUERYTYPE Raw Value-40',
        'zGenAlbum-ZTRASHEDSTATE Raw Value-41',
        ('zGenAlbum-Trash Date-42', 'datetime'),
        'zGenAlbum-ZCLOUDDELETESTATE Raw Value-43',
        'zGenAlbum-ZCLOUDOWNERISWHITELISTED Raw Value-44',
        'zGenAlbum-ZCLOUDPUBLICURLENABLEDLOCAL Raw Value-45',
        'zGenAlbum-ZCLOUDPUBLICURLENABLED Raw Value-46',
        'zGenAlbum-Public URL-47',
        'zGenAlbum-Key Asset Face Thumb Index-48',
        'zGenAlbum-Project Text Extension ID-49',
        'zGenAlbum-User Query Data-50',
        'zGenAlbum-Custom Query Parameters-51',
        'zGenAlbum-Project Data-52',
        'zGenAlbum-ZSEARCHINDEXREBUILDSTATE Raw Value-53',
        'zGenAlbum-ZDUPLICATETYPE Raw Value-54',
        'zGenAlbum-ZPRIVACYSTATE Raw Value-55',
        'zCldShareAlbumInvRec-zUUID-56',
        'zCldShareAlbumInvRec-ZISMINE Raw Value-57',
        'zCldShareAlbumInvRec-ZINVITATIONSTATELOCAL Raw Value-58',
        'zCldShareAlbumInvRec-ZINVITATIONSTATE Raw Value-59',
        ('zCldShareAlbumInvRec-Subscription Date-60', 'datetime'),
        'zCldShareAlbumInvRec-Invitee First Name-61',
        'zCldShareAlbumInvRec-Invitee Last Name-62',
        'zCldShareAlbumInvRec-Invitee Full Name-63',
        'zCldShareAlbumInvRec-Invitee Hashed Person ID-64',
        'zCldShareAlbumInvRec-Invitee Email Key-65',
        'zCldShareAlbumInvRec-Album GUID-66',
        'zCldShareAlbumInvRec-Cloud GUID-67',
        'zGenAlbum-Project Render UUID-68',
        'zAlbumList-ZNEEDSREORDERINGNUMBER Raw Value-69')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("18")) & (version.parse(iosversion) < version.parse("27")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Creation Date',
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',             
        DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',    
        zGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zGenAlbum-Imported by Bundle Identifier',             
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        zGenAlbum.ZPENDINGITEMSTYPE AS 'zGenAlbum-ZPENDINGITEMSTYPE Raw Value',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        zGenAlbum.ZHASUNSEENCONTENT AS 'zGenAlbum-ZHASUNSEENCONTENT Raw Value',
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        zGenAlbum.Z_ENT AS 'zGenAlbum-Z_ENT Raw Value',
        zGenAlbum.ZKIND AS 'zGenAlbum-ZKIND Raw Value',
        zGenAlbum.ZCLOUDLOCALSTATE AS 'zGenAlbum-ZCLOUDLOCALSTATE Raw Value',
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        zGenAlbum.ZISOWNED AS 'zGenAlbum-ZISOWNED Raw Value',
        zGenAlbum.ZCLOUDRELATIONSHIPSTATE AS 'zGenAlbum-ZCLOUDRELATIONSHIPSTATE Raw Value',
        zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL AS 'zGenAlbum-ZCLOUDRELATIONSHIPSTATELOCAL Raw Value',
        zGenAlbum.ZCLOUDOWNEREMAILKEY AS 'zGenAlbum-Cloud Owner Mail Key',        
        zGenAlbum.ZCLOUDOWNERFIRSTNAME AS 'zGenAlbum-Cloud Owner Frist Name',        
        zGenAlbum.ZCLOUDOWNERLASTNAME AS 'zGenAlbum-Cloud Owner Last Name',        
        zGenAlbum.ZCLOUDOWNERFULLNAME AS 'zGenAlbum-Cloud Owner Full Name',
        zGenAlbum.ZCLOUDPERSONID AS 'zGenAlbum-Cloud Person ID',        
        zGenAlbum.ZCLOUDOWNERHASHEDPERSONID AS 'zGenAlbum-Cloud Owner Hashed Person ID',        
        zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL AS 'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL Raw Value',
        zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED AS 'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLED Raw Value',
        zGenAlbum.ZCLOUDALBUMSUBTYPE AS 'zGenAlbum-ZCLOUDALBUMSUBTYPE Raw Value',
        DateTime(zGenAlbum.ZCLOUDLASTCONTRIBUTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Contribution Date',        
        DateTime(zGenAlbum.ZCLOUDLASTINTERESTINGCHANGEDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Last Interesting Change Date',        
        zGenAlbum.ZCLOUDNOTIFICATIONSENABLED AS 'zGenAlbum-ZCLOUDNOTIFICATIONSENABLED Raw Value',
        zGenAlbum.ZISPINNED AS 'zGenAlbum-ZISPINNED Raw Value',
        zGenAlbum.ZCUSTOMSORTKEY AS 'zGenAlbum-ZCUSTOMSORTKEY Raw Value',
        zGenAlbum.ZCUSTOMSORTASCENDING AS 'zGenAlbum-ZCUSTOMSORTASCENDING Raw Value',
        zGenAlbum.ZISPROTOTYPE AS 'zGenAlbum-ZISPROTOTYPE Raw Value',
        zGenAlbum.ZPROJECTDOCUMENTTYPE AS 'zGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value',
        zGenAlbum.ZCUSTOMQUERYTYPE AS 'zGenAlbum-ZCUSTOMQUERYTYPE Raw Value',
        zGenAlbum.ZTRASHEDSTATE AS 'zGenAlbum-ZTRASHEDSTATE Raw Value',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        zGenAlbum.ZCLOUDDELETESTATE AS 'zGenAlbum-ZCLOUDDELETESTATE Raw Value',
        zGenAlbum.ZCLOUDOWNERISWHITELISTED AS 'zGenAlbum-ZCLOUDOWNERISWHITELISTED Raw Value',
        zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL AS 'zGenAlbum-ZCLOUDPUBLICURLENABLEDLOCAL Raw Value',
        zGenAlbum.ZCLOUDPUBLICURLENABLED AS 'zGenAlbum-ZCLOUDPUBLICURLENABLED Raw Value',
        zGenAlbum.ZPUBLICURL AS 'zGenAlbum-Public URL',        
        zGenAlbum.ZKEYASSETFACETHUMBNAILINDEX AS 'zGenAlbum-Key Asset Face Thumb Index',        
        zGenAlbum.ZPROJECTEXTENSIONIDENTIFIER AS 'zGenAlbum-Project Text Extension ID',        
        zGenAlbum.ZUSERQUERYDATA AS 'zGenAlbum-User Query Data',        
        zGenAlbum.ZCUSTOMQUERYPARAMETERS AS 'zGenAlbum-Custom Query Parameters',        
        zGenAlbum.ZPROJECTDATA AS 'zGenAlbum-Project Data',        
        zGenAlbum.ZSEARCHINDEXREBUILDSTATE AS 'zGenAlbum-ZSEARCHINDEXREBUILDSTATE Raw Value',
        zGenAlbum.ZDUPLICATETYPE AS 'zGenAlbum-ZDUPLICATETYPE Raw Value',
        zGenAlbum.ZPRIVACYSTATE AS 'zGenAlbum-ZPRIVACYSTATE Raw Value',
        zCldShareAlbumInvRec.ZUUID AS 'zCldShareAlbumInvRec-zUUID',
        zCldShareAlbumInvRec.ZISMINE AS 'zCldShareAlbumInvRec-ZISMINE Raw Value',
        zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL AS 'zCldShareAlbumInvRec-ZINVITATIONSTATELOCAL Raw Value',
        zCldShareAlbumInvRec.ZINVITATIONSTATE AS 'zCldShareAlbumInvRec-ZINVITATIONSTATE Raw Value',
        DateTime(zCldShareAlbumInvRec.ZINVITEESUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zCldShareAlbumInvRec-Subscription Date',
        zCldShareAlbumInvRec.ZINVITEEFIRSTNAME AS 'zCldShareAlbumInvRec-Invitee First Name',
        zCldShareAlbumInvRec.ZINVITEELASTNAME AS 'zCldShareAlbumInvRec-Invitee Last Name',
        zCldShareAlbumInvRec.ZINVITEEFULLNAME AS 'zCldShareAlbumInvRec-Invitee Full Name',
        zCldShareAlbumInvRec.ZINVITEEHASHEDPERSONID AS 'zCldShareAlbumInvRec-Invitee Hashed Person ID',
        zCldShareAlbumInvRec.ZINVITEEEMAILKEY AS 'zCldShareAlbumInvRec-Invitee Email Key',    
        zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID',
        zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID',
        zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID',        
        zAlbumList.ZNEEDSREORDERINGNUMBER AS 'zAlbumList-ZNEEDSREORDERINGNUMBER Raw Value'
        FROM ZGENERICALBUM zGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN Z_29ALBUMLISTS z29AlbumLists ON z29AlbumLists.Z_29ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z29AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
        ORDER BY zGenAlbum.ZCREATIONDATE
        '''

        if version.parse(iosversion) >= version.parse("26"):
            # On iOS 26 the album to album list join table is Z_32ALBUMLISTS (Z_32ALBUMS).
            query = query.replace('Z_29ALBUMLISTS', 'Z_32ALBUMLISTS').replace('Z_29ALBUMS', 'Z_32ALBUMS')

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
            row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
            row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
            row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
            row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
            row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
            row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
            row[64], row[65], row[66], row[67], row[68], row[69]))

        data_headers = (('zGenAlbum-Cloud Creation Date-0', 'datetime'),
        ('zGenAlbum-Creation Date-1', 'datetime'),
        ('zGenAlbum-Start Date-2', 'datetime'),
        ('zGenAlbum-End Date-3', 'datetime'),
        ('zGenAlbum-Cloud Subscription Date-4', 'datetime'),
        'zGenAlbum- Title-User&System Applied-5',
        'zGenAlbum-UUID-6',
        'zGenAlbum-Cloud GUID-7',
        'zGenAlbum-Imported by Bundle Identifier-8',
        'zGenAlbum-Pending Items Count-9',
        'zGenAlbum-ZPENDINGITEMSTYPE Raw Value-10',
        'zGenAlbum- Cached Photos Count-11',
        'zGenAlbum- Cached Videos Count-12',
        'zGenAlbum- Cached Count-13',
        'zGenAlbum-ZHASUNSEENCONTENT Raw Value-14',
        'zGenAlbum-Unseen Asset Count-15',
        'zGenAlbum-Z_ENT Raw Value-16',
        'zGenAlbum-ZKIND Raw Value-17',
        'zGenAlbum-ZCLOUDLOCALSTATE Raw Value-18',
        'zGenAlbum-Sync Event Order Key-19',
        'zGenAlbum-ZISOWNED Raw Value-20',
        'zGenAlbum-ZCLOUDRELATIONSHIPSTATE Raw Value-21',
        'zGenAlbum-ZCLOUDRELATIONSHIPSTATELOCAL Raw Value-22',
        'zGenAlbum-Cloud Owner Mail Key-23',
        'zGenAlbum-Cloud Owner First Name-24',
        'zGenAlbum-Cloud Owner Last Name-25',
        'zGenAlbum-Cloud Owner Full Name-26',
        'zGenAlbum-Cloud Person ID-27',
        'zGenAlbum-Cloud Owner Hashed Person ID-28',
        'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL Raw Value-29',
        'zGenAlbum-ZCLOUDMULTIPLECONTRIBUTORSENABLED Raw Value-30',
        'zGenAlbum-ZCLOUDALBUMSUBTYPE Raw Value-31',
        ('zGenAlbum-Cloud Contribution Date-32', 'datetime'),
        ('zGenAlbum-Cloud Last Interesting Change Date-33', 'datetime'),
        'zGenAlbum-ZCLOUDNOTIFICATIONSENABLED Raw Value-34',
        'zGenAlbum-ZISPINNED Raw Value-35',
        'zGenAlbum-ZCUSTOMSORTKEY Raw Value-36',
        'zGenAlbum-ZCUSTOMSORTASCENDING Raw Value-37',
        'zGenAlbum-ZISPROTOTYPE Raw Value-38',
        'zGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value-39',
        'zGenAlbum-ZCUSTOMQUERYTYPE Raw Value-40',
        'zGenAlbum-ZTRASHEDSTATE Raw Value-41',
        ('zGenAlbum-Trash Date-42', 'datetime'),
        'zGenAlbum-ZCLOUDDELETESTATE Raw Value-43',
        'zGenAlbum-ZCLOUDOWNERISWHITELISTED Raw Value-44',
        'zGenAlbum-ZCLOUDPUBLICURLENABLEDLOCAL Raw Value-45',
        'zGenAlbum-ZCLOUDPUBLICURLENABLED Raw Value-46',
        'zGenAlbum-Public URL-47',
        'zGenAlbum-Key Asset Face Thumb Index-48',
        'zGenAlbum-Project Text Extension ID-49',
        'zGenAlbum-User Query Data-50',
        'zGenAlbum-Custom Query Parameters-51',
        'zGenAlbum-Project Data-52',
        'zGenAlbum-ZSEARCHINDEXREBUILDSTATE Raw Value-53',
        'zGenAlbum-ZDUPLICATETYPE Raw Value-54',
        'zGenAlbum-ZPRIVACYSTATE Raw Value-55',
        'zCldShareAlbumInvRec-zUUID-56',
        'zCldShareAlbumInvRec-ZISMINE Raw Value-57',
        'zCldShareAlbumInvRec-ZINVITATIONSTATELOCAL Raw Value-58',
        'zCldShareAlbumInvRec-ZINVITATIONSTATE Raw Value-59',
        ('zCldShareAlbumInvRec-Subscription Date-60', 'datetime'),
        'zCldShareAlbumInvRec-Invitee First Name-61',
        'zCldShareAlbumInvRec-Invitee Last Name-62',
        'zCldShareAlbumInvRec-Invitee Full Name-63',
        'zCldShareAlbumInvRec-Invitee Hashed Person ID-64',
        'zCldShareAlbumInvRec-Invitee Email Key-65',
        'zCldShareAlbumInvRec-Album GUID-66',
        'zCldShareAlbumInvRec-Cloud GUID-67',
        'zGenAlbum-Project Render UUID-68',
        'zAlbumList-ZNEEDSREORDERINGNUMBER Raw Value-69')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        return data_headers, data_list, source_path

