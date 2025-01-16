__artifacts_v2__ = {
    'Ph16_1PeopleFacesAssetDataPhDaPsql': {
        'name': 'Ph16.1-People & Faces Asset Data-PhDaPsql',
        'description': 'Parses basic asset record data from PhotoData-Photos.sqlite for basic asset'
                       ' people and faces data. The results may contain multiple records per ZASSET table Z_PK value'
                       ' and supports iOS 14-18.',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-G-People_Faces_Data',
        'notes': '',
        'paths': ('*/PhotoData/Photos.sqlite*',),
        "output_types": ["standard", "tsv", "none"]
    },
    'Ph16_2PeopleFacesAssetDataSyndPL': {
        'name': 'Ph16.2-People & Faces Asset Data-SyndPL',
        'description': 'Parses basic asset record data from Syndication.photoslibrary-database-Photos.sqlite'
                       ' for basic asset people and faces data. The results may contain multiple records'
                       ' per ZASSET table Z_PK value and supports iOS 14-18.',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains Syndication Photo Library Photos.sqlite',
        'category': 'Photos.sqlite-S-Syndication_PL_Artifacts',
        'notes': '',
        'paths': ('*/mobile/Library/Photos/Libraries/Syndication.photoslibrary/database/Photos.sqlite*',),
        "output_types": ["standard", "tsv", "none"]
    }
}

import os
import nska_deserialize as nd
import scripts.artifacts.artGlobals
from packaging import version
from scripts.builds_ids import OS_build
from scripts.ilapfuncs import media_to_html, artifact_processor, get_file_path, open_sqlite_db_readonly, get_sqlite_db_records, logfunc

@artifact_processor
def Ph16_1PeopleFacesAssetDataPhDaPsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for source_path in files_found:
        source_path = str(source_path)

        if source_path.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("13.7"):
        logfunc("Unsupported version for PhotoData-Photos.sqlite iOS " + iosversion)
        return (), [], source_path
    if (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("15")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',  
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',    
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr-Creator Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',        
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE
            WHEN zAsset.ZFACEAREAPOINTS > 0 THEN 'Face Area Points Detected in zAsset'
            ELSE 'Face Area Points Not Detected in zAsset'
        END AS 'zFaceCrop-Face Area Points',
        zAsset.ZFACEADJUSTMENTVERSION AS 'zAsset-Face Adjustment Version',
        CASE
            WHEN zAddAssetAttr.ZFACEREGIONS > 0 THEN 'zAddAssetAttr-Face_Regions_has_Data'
            ELSE 'zAddAssetAttr-Face_Regions_has_NO-Data'
        END AS 'zAddAssetAttr-Face_Regions-SeeRawDBData',
        CASE
            WHEN zDetFacePrint.ZDATA > 0 THEN 'zDetFacePrint-Data_has_Data'
            ELSE 'zDetFacePrint-Data_NO-Data'
        END AS 'zDetFacePrint-Data-SeeRawDBData',
        zPerson.ZCONTACTMATCHINGDICTIONARY AS 'zPerson-Contact Matching Dictionary',
        CASE zPerson.ZVERIFIEDTYPE
            WHEN 0 THEN '0-Not-Verified'
            WHEN 1 THEN '1-Has_Contact Matching_Dictionary'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZVERIFIEDTYPE || ''
        END AS 'zPerson-Verified Type',
        zPerson.ZDISPLAYNAME AS 'zPerson-Display Name',
        zPerson.ZFULLNAME AS 'zPerson-Full Name',
        CASE zPerson.ZCLOUDVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDVERIFIEDTYPE || ''
        END AS 'zPerson-Cloud Verified Type',
        CASE zFaceCrop.ZSTATE
            WHEN 5 THEN 'Validated-5'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZSTATE || ''
        END AS 'zFaceCrop-State',
        CASE zFaceCrop.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-Active'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZTYPE || ''
        END AS 'zFaceCrop-Type',
        zFaceCrop.ZRESOURCEDATA AS 'zFaceCrop-Resource Data',	
        CASE zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE || ''
        END AS 'zDetFace-Confirmed Face Crop Generation State',
        CASE zDetFace.ZMANUAL
            WHEN 0 THEN 'zDetFace-Auto Detected-0'
            WHEN 1 THEN 'zDetFace-Manually Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZMANUAL || ''
        END AS 'zDetFace-Manual',
        CASE zDetFace.ZVIPMODELTYPE
            WHEN 0 THEN 'Not VIP-0'
            WHEN 1 THEN 'VIP-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZVIPMODELTYPE || ''
        END AS 'zDetFace-VIP Model Type',
        CASE zDetFace.ZNAMESOURCE
            WHEN 0 THEN 'No Name Listed-0'
            WHEN 1 THEN '1-Face Crop-1'
            WHEN 2 THEN '2-Verified/Has-Person-URI'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZNAMESOURCE || ''
        END AS 'zDetFace-Name Source',
        CASE zDetFace.ZCLOUDNAMESOURCE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN '1-User Added Via Face Crop-1'
            WHEN 5 THEN '5-Asset Shared has Name'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDNAMESOURCE || ''
        END AS 'zDetFace-Cloud Name Source',
        CASE zPerson.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZTYPE || ''
        END AS 'zPerson-Type',
        CASE zPerson.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZGENDERTYPE || ''
        END AS 'zPerson-Gender Type',
        CASE zDetFace.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGENDERTYPE || ''
        END AS 'zDetFace-Gender Type',
        zDetFace.ZCENTERX AS 'zDetFace-Center X',
        zDetFace.ZCENTERY AS 'zDetFace-Center Y',
        CASE zPerson.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZAGETYPE || ''
        END AS 'zPerson-Age Type Estimate',
        CASE zDetFace.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZAGETYPE || ''
        END AS 'zDetFace-Age Type Estimate',
        CASE zDetFace.ZHAIRCOLORTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/Brown Hair Color-1'
            WHEN 2 THEN 'Brown/Blonde Hair Color-2'
            WHEN 3 THEN 'Brown/Red Hair Color-3'
            WHEN 4 THEN 'Red/White Hair Color-4'
            WHEN 5 THEN 'StillTesting/Artifical-5'
            WHEN 6 THEN 'White/Bald Hair Color-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRCOLORTYPE || ''
        END AS 'zDetFace-Hair Color Type',
        CASE zDetFace.ZFACIALHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Clean Shaven Facial Hair Type-1'
            WHEN 2 THEN 'Beard Facial Hair Type-2'
            WHEN 3 THEN 'Goatee Facial Hair Type-3'
            WHEN 4 THEN 'Mustache Facial Hair Type-4'
            WHEN 5 THEN 'Stubble Facial Hair Type-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACIALHAIRTYPE || ''
        END AS 'zDetFace-Facial Hair Type',
        CASE zDetFace.ZHASSMILE
            WHEN 0 THEN 'zDetFace No Smile-0'
            WHEN 1 THEN 'zDetFace Smile-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASSMILE || ''
        END AS 'zDetFace-Has Smile',
        CASE zDetFace.ZSMILETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'zDetFace Smile No Teeth-1'
            WHEN 2 THEN 'zDetFace Smile has Teeth-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSMILETYPE || ''
        END AS 'zDetFace-Smile Type',
        CASE zDetFace.ZLIPMAKEUPTYPE
            WHEN 0 THEN 'zDetFace No Lip Makeup-0'
            WHEN 1 THEN 'zDetFace Lip Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZLIPMAKEUPTYPE || ''
        END AS 'zDetFace-Lip Makeup Type',
        CASE zDetFace.ZEYESSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eyes Closed-1'
            WHEN 2 THEN 'Eyes Open-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYESSTATE || ''
        END AS 'zDetFace-Eyes State',
        CASE zDetFace.ZISLEFTEYECLOSED
            WHEN 0 THEN 'Left Eye Open-0'
            WHEN 1 THEN 'Left Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISLEFTEYECLOSED || ''
        END AS 'zDetFace-Is Left Eye Closed',
        CASE zDetFace.ZISRIGHTEYECLOSED
            WHEN 0 THEN 'Right Eye Open-0'
            WHEN 1 THEN 'Right Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISRIGHTEYECLOSED || ''
        END AS 'zDetFace-Is Right Eye Closed',
        CASE zDetFace.ZGLASSESTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eye Glasses-1'
            WHEN 2 THEN 'Sun Glasses-2'
            WHEN 3 THEN 'No Glasses-3'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGLASSESTYPE || ''
        END AS 'zDetFace-Eye Glasses Type',
        CASE zDetFace.ZEYEMAKEUPTYPE
            WHEN 0 THEN 'No Eye Makeup-0'
            WHEN 1 THEN 'Eye Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYEMAKEUPTYPE || ''
        END AS 'zDetFace-Eye Makeup Type',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number Key',
        zDetFace.ZGROUPINGIDENTIFIER AS 'zDetFace-Grouping ID',
        zDetFace.ZMASTERIDENTIFIER AS 'zDetFace-Master ID',
        zDetFace.ZQUALITY AS 'zDetFace-Quality',
        zDetFace.ZQUALITYMEASURE AS 'zDetFace-Quality Measure',
        zDetFace.ZSOURCEHEIGHT AS 'zDetFace-Source Height',
        zDetFace.ZSOURCEWIDTH AS 'zDetFace-Source Width',
        CASE zDetFace.ZASSETVISIBLE
            WHEN 0 THEN '0-Unknown-StillTesitng-0'
            WHEN 1 THEN '1-Unknown-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZASSETVISIBLE || ''
        END AS 'zDetFace-Asset Visible',
        CASE zDetFace.ZHIDDEN
            WHEN 0 THEN 'Not Hidden-0'
            WHEN 1 THEN 'Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHIDDEN || ''
        END AS 'zDetFace-Hidden/Asset Hidden',
        CASE zDetFace.ZISINTRASH
            WHEN 0 THEN 'Not In Trash-0'
            WHEN 1 THEN 'In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISINTRASH || ''
        END AS 'zDetFace-In Trash/Recently Deleted',
        CASE zDetFace.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDLOCALSTATE || ''
        END AS 'zDetFace-Cloud Local State',
        CASE zDetFace.ZTRAININGTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZTRAININGTYPE
        END AS 'zDetFace-Training Type',
        zDetFace.ZPOSEYAW AS 'zDetFace.Pose Yaw',
        zDetFace.ZROLL AS 'zDetFace-Roll',
        zDetFace.ZSIZE AS 'zDetFace-Size',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number',
        zDetFace.ZBLURSCORE AS 'zDetFace-Blur Score',
        zDetFacePrint.ZFACEPRINTVERSION AS 'zDetFacePrint-Face Print Version',
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFaceGroup.ZPERSONBUILDERSTATE AS 'zDetFaceGroup-Person Builder State',
        zDetFaceGroup.ZUNNAMEDFACECOUNT AS 'zDetFaceGroup-UnNamed Face Count',
        zPerson.ZFACECOUNT AS 'zPerson-Face Count',       
        zDetFace.ZFACEALGORITHMVERSION AS 'zDetFace-Face Algorithm Version',
        zDetFace.ZADJUSTMENTVERSION AS 'zDetFace-Adjustment Version',       
        zPerson.ZINPERSONNAMINGMODEL AS 'zPerson-In Person Naming Model',
        zPerson.ZKEYFACEPICKSOURCE AS 'zPerson-Key Face Pick Source Key',
        zPerson.ZMANUALORDER AS 'zPerson-Manual Order Key',
        zPerson.ZQUESTIONTYPE AS 'zPerson-Question Type',
        zPerson.ZSUGGESTEDFORCLIENTTYPE AS 'zPerson-Suggested For Client Type',
        zPerson.ZMERGETARGETPERSON AS 'zPerson-Merge Target Person',
        CASE zPerson.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Person Not Synced with Cloud-0'
            WHEN 1 THEN 'Person Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDLOCALSTATE
        END AS 'zPerson-Cloud Local State',
        CASE zFaceCrop.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDLOCALSTATE || ''
        END AS 'zFaceCrop-Cloud Local State',
        CASE zFaceCrop.ZCLOUDTYPE
            WHEN 0 THEN 'Has Name-0'
            WHEN 5 THEN 'Has Face Key-5'
            WHEN 12 THEN '12-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDTYPE || ''
        END AS 'zFaceCrop-Cloud Type',
        CASE zPerson.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDDELETESTATE || ''
        END AS 'zPerson-Cloud Delete State',
        CASE zFaceCrop.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDDELETESTATE || ''
        END AS 'zFaceCrop-Cloud Delete State',
        zDetFace.Z_PK AS 'zDetFace-zPK',
        zDetFacePrint.ZFACE AS 'zDetFacePrint-Face Key',
        zPerson.ZKEYFACE AS 'zPerson-KeyFace=zDetFace-zPK',
        zFaceCrop.ZFACE AS 'zFaceCrop-Face Key',
        zPerson.Z_PK AS 'zPerson-zPK=zDetFace-Person',
        zDetFace.ZPERSON AS 'zDetFace-PersonForFace= zPerson-zPK',
        zDetFace.ZPERSONBEINGKEYFACE AS 'zDetFace-Person Being Key Face',         
        zFaceCrop.ZPERSON AS 'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key',	
        zDetFace.ZFACEPRINT AS 'zDetFace-Face Print',	
        zDetFacePrint.Z_PK AS 'zDetFacePrint-zPK',		
        zDetFace.ZFACECROP AS 'zDetFace-Face Crop',
        zFaceCrop.Z_PK AS 'zFaceCrop-zPK',           
        zDetFaceGroup.ZKEYFACE AS 'zDetFaceGroup-KeyFace= zDetFace-zPK',
        zDetFaceGroup.ZASSOCIATEDPERSON AS 'zDetFaceGroup-AssocPerson= zPerson-zPK',
        zPerson.ZASSOCIATEDFACEGROUP AS 'zPerson-Assoc Face Group Key',
        zDetFace.ZFACEGROUPBEINGKEYFACE AS 'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK',
        zDetFace.ZFACEGROUP AS 'zDetFace-FaceGroup= zDetFaceGroup-zPK',		
        zDetFaceGroup.Z_PK AS 'zDetFaceGroup-zPK',
        zDetFace.ZUUID AS 'zDetFace-UUID',		
        zFaceCrop.ZUUID AS 'zFaceCrop-UUID',		
        zFaceCrop.ZINVALIDMERGECANDIDATEPERSONUUID AS 'zFaceCrop-Invalid Merge Canidate Person UUID',		
        zPerson.ZPERSONUUID AS 'zPerson-Person UUID',
        zPerson.ZPERSONURI AS 'zPerson-Person URI',		
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFace.ZASSET AS 'zDetFace-AssetForFace= zAsset-zPK',
        zFaceCrop.ZASSET AS 'zFaceCrop-Asset Key',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
            LEFT JOIN ZDETECTEDFACE zDetFace ON zAsset.Z_PK = zDetFace.ZASSET
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSON
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP
        WHERE zDetFace.Z_PK > 0      
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            personcontactmatchingdictionary = ''
            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            facecropresourcedata_blob = ''

            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            if row[22] is not None:
                pathto = os.path.join(report_folder, 'zPerson-ContactMatchingDict_' + row[108] + '.plist')
                with open(pathto, 'ab') as wf:
                    wf.write(row[22])

                with open(pathto, 'rb') as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        personcontactmatchingdictionary = deserialized_plist

                    except (KeyError, ValueError, TypeError) as ex:
                        if str(ex).find("does not contain an '$archiver' key") >= 0:
                            logfunc('plist was Not an NSKeyedArchive ' + row[108])
                        else:
                            logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[108])

            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            if row[29] is not None:
                pathto = os.path.join(report_folder, 'FaceCropFor_' + row[106] + '.jpg')
                with open(pathto, 'wb') as file:
                    file.write(row[29])
                facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                            row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                            row[19], row[20], row[21],
                            personcontactmatchingdictionary,
                            row[23], row[24], row[25], row[26], row[27], row[28],
                            facecropresourcedata_blob,
                            row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                            row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                            row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                            row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                            row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                            row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                            row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                            row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                            row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                            row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
                            row[116]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        'zAsset-Directory-Path-7',
                        'zAsset-Filename-8',
                        'zAddAssetAttr- Original Filename-9',
                        'zCldMast- Original Filename-10',
                        ('zAsset-Trashed Date-11', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-12',
                        'zAddAssetAttr-Creator Bundle ID-13',
                        'zAddAssetAttr-Imported By Display Name-14',
                        'zCldMast-Imported by Bundle ID-15',
                        'zCldMast-Imported by Display Name-16',
                        'zAsset-Visibility State-17',
                        'zFaceCrop-Face Area Points-18',
                        'zAsset-Face Adjustment Version-19',
                        'zAddAssetAttr-Face_Regions-SeeRawDBData-20',
                        'zDetFacePrint-Data-SeeRawDBData-21',
                        'zPerson-Contact Matching Dictionary-22',
                        'zPerson-Verified Type-23',
                        'zPerson-Display Name-24',
                        'zPerson-Full Name-25',
                        'zPerson-Cloud Verified Type-26',
                        'zFaceCrop-State-27',
                        'zFaceCrop-Type-28',
                        'zFaceCrop-Resource Data-29',
                        'zDetFace-Confirmed Face Crop Generation State-30',
                        'zDetFace-Manual-31',
                        'zDetFace-VIP Model Type-32',
                        'zDetFace-Name Source-33',
                        'zDetFace-Cloud Name Source-34',
                        'zPerson-Type-35',
                        'zPerson-Gender Type-36',
                        'zDetFace-Gender Type-37',
                        'zDetFace-Center X-38',
                        'zDetFace-Center Y-39',
                        'zPerson-Age Type Estimate-40',
                        'zDetFace-Age Type Estimate-41',
                        'zDetFace-Hair Color Type-42',
                        'zDetFace-Facial Hair Type-43',
                        'zDetFace-Has Smile-44',
                        'zDetFace-Smile Type-45',
                        'zDetFace-Lip Makeup Type-46',
                        'zDetFace-Eyes State-47',
                        'zDetFace-Is Left Eye Closed-48',
                        'zDetFace-Is Right Eye Closed-49',
                        'zDetFace-Eye Glasses Type-50',
                        'zDetFace-Eye Makeup Type-51',
                        'zDetFace-Cluster Sequence Number Key-52',
                        'zDetFace-Grouping ID-53',
                        'zDetFace-Master ID-54',
                        'zDetFace-Quality-55',
                        'zDetFace-Quality Measure-56',
                        'zDetFace-Source Height-57',
                        'zDetFace-Source Width-58',
                        'zDetFace-Asset Visible-59',
                        'zDetFace-Hidden/Asset Hidden-60',
                        'zDetFace-In Trash/Recently Deleted-61',
                        'zDetFace-Cloud Local State-62',
                        'zDetFace-Training Type-63',
                        'zDetFace.Pose Yaw-64',
                        'zDetFace-Roll-65',
                        'zDetFace-Size-66',
                        'zDetFace-Cluster Sequence Number-67',
                        'zDetFace-Blur Score-68',
                        'zDetFacePrint-Face Print Version-69',
                        'zDetFaceGroup-UUID-70',
                        'zDetFaceGroup-Person Builder State-71',
                        'zDetFaceGroup-UnNamed Face Count-72',
                        'zPerson-Face Count-73',
                        'zDetFace-Face Algorithm Version-74',
                        'zDetFace-Adjustment Version-75',
                        'zPerson-In Person Naming Model-76',
                        'zPerson-Key Face Pick Source Key-77',
                        'zPerson-Manual Order Key-78',
                        'zPerson-Question Type-79',
                        'zPerson-Suggested For Client Type-80',
                        'zPerson-Merge Target Person-81',
                        'zPerson-Cloud Local State-82',
                        'zFaceCrop-Cloud Local State-83',
                        'zFaceCrop-Cloud Type-84',
                        'zPerson-Cloud Delete State-85',
                        'zFaceCrop-Cloud Delete State-86',
                        'zDetFace-zPK-87',
                        'zDetFacePrint-Face Key-88',
                        'zPerson-KeyFace=zDetFace-zPK-89',
                        'zFaceCrop-Face Key-90',
                        'zPerson-zPK=zDetFace-Person-91',
                        'zDetFace-PersonForFace= zPerson-zPK-92',
                        'zDetFace-Person Being Key Face-93',
                        'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-94',
                        'zDetFace-Face Print-95',
                        'zDetFacePrint-zPK-96',
                        'zDetFace-Face Crop-97',
                        'zFaceCrop-zPK-98',
                        'zDetFaceGroup-KeyFace= zDetFace-zPK-99',
                        'zDetFaceGroup-AssocPerson= zPerson-zPK-100',
                        'zPerson-Assoc Face Group Key-101',
                        'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-102',
                        'zDetFace-FaceGroup= zDetFaceGroup-zPK-103',
                        'zDetFaceGroup-zPK-104',
                        'zDetFace-UUID-105',
                        'zFaceCrop-UUID-106',
                        'zFaceCrop-Invalid Merge Candidate Person UUID-107',
                        'zPerson-Person UUID-108',
                        'zPerson-Person URI-109',
                        'zDetFaceGroup-UUID-110',
                        'zDetFace-AssetForFace= zAsset-zPK-111',
                        'zFaceCrop-Asset Key-112',
                        'zAsset-zPK-113',
                        'zAddAssetAttr-zPK-114',
                        'zAsset-UUID = store.cloudphotodb-115',
                        'zAddAssetAttr-Master Fingerprint-116')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',  
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE
            WHEN zAsset.ZFACEAREAPOINTS > 0 THEN 'Face Area Points Detected in zAsset'
            ELSE 'Face Area Points Not Detected in zAsset'
        END AS 'zFaceCrop-Face Area Points',
        zAsset.ZFACEADJUSTMENTVERSION AS 'zAsset-Face Adjustment Version',
        CASE
            WHEN zAddAssetAttr.ZFACEREGIONS > 0 THEN 'zAddAssetAttr-Face_Regions_has_Data'
            ELSE 'zAddAssetAttr-Face_Regions_has_NO-Data'
        END AS 'zAddAssetAttr-Face_Regions-SeeRawDBData',
        zAddAssetAttr.ZFACEANALYSISVERSION AS 'zAddAssetAttr-Face Analysis Version',
        CASE
            WHEN zDetFacePrint.ZDATA > 0 THEN 'zDetFacePrint-Data_has_Data'
            ELSE 'zDetFacePrint-Data_NO-Data'
        END AS 'zDetFacePrint-Data-SeeRawDBData',
        zPerson.ZCONTACTMATCHINGDICTIONARY AS 'zPerson-Contact Matching Dictionary',
        CASE zPerson.ZVERIFIEDTYPE
            WHEN 0 THEN '0-Not-Verified'
            WHEN 1 THEN '1-Has_Contact Matching_Dictionary'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZVERIFIEDTYPE || ''
        END AS 'zPerson-Verified Type',
        zPerson.ZDISPLAYNAME AS 'zPerson-Display Name',
        zPerson.ZFULLNAME AS 'zPerson-Full Name',
        CASE zPerson.ZCLOUDVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDVERIFIEDTYPE || ''
        END AS 'zPerson-Cloud Verified Type',
        CASE zFaceCrop.ZSTATE
            WHEN 5 THEN 'Validated-5'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZSTATE || ''
        END AS 'zFaceCrop-State',
        CASE zFaceCrop.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-Active'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZTYPE || ''
        END AS 'zFaceCrop-Type',
        zFaceCrop.ZRESOURCEDATA AS 'zFaceCrop-Resource Data',	
        CASE zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE || ''
        END AS 'zDetFace-Confirmed Face Crop Generation State',
        CASE zDetFace.ZMANUAL
            WHEN 0 THEN 'zDetFace-Auto Detected-0'
            WHEN 1 THEN 'zDetFace-Manually Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZMANUAL || ''
        END AS 'zDetFace-Manual',
        CASE zDetFace.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZDETECTIONTYPE || ''
        END AS 'zDetFace-Detection Type',
        CASE zPerson.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZDETECTIONTYPE || ''
        END AS 'zPerson-Detection Type',
        CASE zDetFace.ZVIPMODELTYPE
            WHEN 0 THEN 'Not VIP-0'
            WHEN 1 THEN 'VIP-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZVIPMODELTYPE || ''
        END AS 'zDetFace-VIP Model Type',
        CASE zDetFace.ZNAMESOURCE
            WHEN 0 THEN 'No Name Listed-0'
            WHEN 1 THEN '1-Face Crop-1'
            WHEN 2 THEN '2-Verified/Has-Person-URI'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZNAMESOURCE || ''
        END AS 'zDetFace-Name Source',
        CASE zDetFace.ZCLOUDNAMESOURCE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN '1-User Added Via Face Crop-1'
            WHEN 5 THEN '5-Asset Shared has Name'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDNAMESOURCE || ''
        END AS 'zDetFace-Cloud Name Source',
        CASE zPerson.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZTYPE || ''
        END AS 'zPerson-Type',
        CASE zPerson.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZGENDERTYPE || ''
        END AS 'zPerson-Gender Type',
        CASE zDetFace.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGENDERTYPE || ''
        END AS 'zDetFace-Gender Type',
        zDetFace.ZCENTERX AS 'zDetFace-Center X',
        zDetFace.ZCENTERY AS 'zDetFace-Center Y',
        CASE zPerson.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZAGETYPE || ''
        END AS 'zPerson-Age Type Estimate',
        CASE zDetFace.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZAGETYPE || ''
        END AS 'zDetFace-Age Type Estimate',
        CASE zDetFace.ZETHNICITYTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/African American-1'
            WHEN 2 THEN 'White-2'
            WHEN 3 THEN 'Hispanic/Latino-3'
            WHEN 4 THEN 'Asian-4'
            WHEN 5 THEN 'Native Hawaiian/Other Pacific Islander-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZETHNICITYTYPE || ''
        END AS 'zDetFace-Ethnicity Type',
        CASE zDetFace.ZSKINTONETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Light-Pale White Skin Tone-1'
            WHEN 2 THEN 'White-Fair Skin Tone-2'
            WHEN 3 THEN 'Medium-White to Olive Skin Tone-3'
            WHEN 4 THEN 'Olive-Moderate Brown Skin Tone-4'
            WHEN 5 THEN 'Brown-Dark Brown Skin Tone-5'
            WHEN 6 THEN 'Black-Very Dark Brown to Black Skin Tone-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSKINTONETYPE || ''
        END AS 'zDetFace-Skin Tone Type',
        CASE zDetFace.ZHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            WHEN 6 THEN '6-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRTYPE || ''
        END AS 'zDetFace-Hair Type',
        CASE zDetFace.ZHAIRCOLORTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/Brown Hair Color-1'
            WHEN 2 THEN 'Brown/Blonde Hair Color-2'
            WHEN 3 THEN 'Brown/Red Hair Color-3'
            WHEN 4 THEN 'Red/White Hair Color-4'
            WHEN 5 THEN 'StillTesting/Artifical-5'
            WHEN 6 THEN 'White/Bald Hair Color-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRCOLORTYPE || ''
        END AS 'zDetFace-Hair Color Type',
        CASE zDetFace.ZHEADGEARTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-No Headgear'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHEADGEARTYPE || ''
        END AS 'zDetFace-Head Gear Type',
        CASE zDetFace.ZFACIALHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Clean Shaven Facial Hair Type-1'
            WHEN 2 THEN 'Beard Facial Hair Type-2'
            WHEN 3 THEN 'Goatee Facial Hair Type-3'
            WHEN 4 THEN 'Mustache Facial Hair Type-4'
            WHEN 5 THEN 'Stubble Facial Hair Type-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACIALHAIRTYPE || ''
        END AS 'zDetFace-Facial Hair Type',
        CASE zDetFace.ZHASFACEMASK
            WHEN 0 THEN 'No Mask-0'
            WHEN 1 THEN 'Has Mask-1'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASFACEMASK || ''
        END AS 'zDetFace-Has Face Mask',
        CASE zDetFace.ZPOSETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Face Frontal Pose-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN 'Face Profile Pose-3'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZPOSETYPE || ''
        END AS 'zDetFace-Pose Type',
        CASE zDetFace.ZFACEEXPRESSIONTYPE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN 'Disgusted/Angry-1'
            WHEN 2 THEN 'Surprised/Fearful-2'
            WHEN 3 THEN 'Neutral-3'
            WHEN 4 THEN 'Confident/Smirk-4'
            WHEN 5 THEN 'Happiness-5'
            WHEN 6 THEN 'Sadness-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACEEXPRESSIONTYPE || ''
        END AS 'zDetFace-Face Expression Type',
        CASE zDetFace.ZHASSMILE
            WHEN 0 THEN 'zDetFace No Smile-0'
            WHEN 1 THEN 'zDetFace Smile-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASSMILE || ''
        END AS 'zDetFace-Has Smile',
        CASE zDetFace.ZSMILETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'zDetFace Smile No Teeth-1'
            WHEN 2 THEN 'zDetFace Smile has Teeth-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSMILETYPE || ''
        END AS 'zDetFace-Smile Type',
        CASE zDetFace.ZLIPMAKEUPTYPE
            WHEN 0 THEN 'zDetFace No Lip Makeup-0'
            WHEN 1 THEN 'zDetFace Lip Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZLIPMAKEUPTYPE || ''
        END AS 'zDetFace-Lip Makeup Type',
        CASE zDetFace.ZEYESSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eyes Closed-1'
            WHEN 2 THEN 'Eyes Open-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYESSTATE || ''
        END AS 'zDetFace-Eyes State',
        CASE zDetFace.ZISLEFTEYECLOSED
            WHEN 0 THEN 'Left Eye Open-0'
            WHEN 1 THEN 'Left Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISLEFTEYECLOSED || ''
        END AS 'zDetFace-Is Left Eye Closed',
        CASE zDetFace.ZISRIGHTEYECLOSED
            WHEN 0 THEN 'Right Eye Open-0'
            WHEN 1 THEN 'Right Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISRIGHTEYECLOSED || ''
        END AS 'zDetFace-Is Right Eye Closed',
        zDetFace.ZGAZECENTERX AS 'zDetFace-Gaze Center X',
        zDetFace.ZGAZECENTERY AS 'zDetFace-Gaze Center Y',
        CASE zDetFace.ZGAZETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGAZETYPE || ''
        END AS 'zDetFace-Face Gaze Type',
        CASE zDetFace.ZGLASSESTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eye Glasses-1'
            WHEN 2 THEN 'Sun Glasses-2'
            WHEN 3 THEN 'No Glasses-3'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGLASSESTYPE || ''
        END AS 'zDetFace-Eye Glasses Type',
        CASE zDetFace.ZEYEMAKEUPTYPE
            WHEN 0 THEN 'No Eye Makeup-0'
            WHEN 1 THEN 'Eye Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYEMAKEUPTYPE || ''
        END AS 'zDetFace-Eye Makeup Type',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Sequence Number Key',
        zDetFace.ZGROUPINGIDENTIFIER AS 'zDetFace-Grouping ID',
        zDetFace.ZMASTERIDENTIFIER AS 'zDetFace-Master ID',
        zDetFace.ZQUALITY AS 'zDetFace-Quality',
        zDetFace.ZQUALITYMEASURE AS 'zDetFace-Quality Measure',
        zDetFace.ZSOURCEHEIGHT AS 'zDetFace-Source Height',
        zDetFace.ZSOURCEWIDTH AS 'zDetFace-Source Width',
        CASE zDetFace.ZASSETVISIBLE
            WHEN 0 THEN '0-Unknown-StillTesitng-0'
            WHEN 1 THEN '1-Unknown-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZASSETVISIBLE || ''
        END AS 'zDetFace-Asset Visible',
        CASE zDetFace.ZHIDDEN
            WHEN 0 THEN 'Not Hidden-0'
            WHEN 1 THEN 'Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHIDDEN || ''
        END AS 'zDetFace-Hidden/Asset Hidden',
        CASE zDetFace.ZISINTRASH
            WHEN 0 THEN 'Not In Trash-0'
            WHEN 1 THEN 'In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISINTRASH || ''
        END AS 'zDetFace-In Trash/Recently Deleted',
        CASE zDetFace.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDLOCALSTATE || ''
        END AS 'zDetFace-Cloud Local State',
        CASE zDetFace.ZTRAININGTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZTRAININGTYPE
        END AS 'zDetFace-Training Type',
        zDetFace.ZPOSEYAW AS 'zDetFace.Pose Yaw',
        zDetFace.ZBODYCENTERX AS 'zDetFace-Body Center X',
        zDetFace.ZBODYCENTERY AS 'zDetFace-Body Center Y',
        zDetFace.ZBODYHEIGHT AS 'zDetFace-Body Height',
        zDetFace.ZBODYWIDTH AS 'zDetFace-Body Width',
        zDetFace.ZROLL AS 'zDetFace-Roll',
        zDetFace.ZSIZE AS 'zDetFace-Size',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number',
        zDetFace.ZBLURSCORE AS 'zDetFace-Blur Score',
        zDetFacePrint.ZFACEPRINTVERSION AS 'zDetFacePrint-Face Print Version',
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFaceGroup.ZPERSONBUILDERSTATE AS 'zDetFaceGroup-Person Builder State',
        zDetFaceGroup.ZUNNAMEDFACECOUNT AS 'zDetFaceGroup-UnNamed Face Count',
        zPerson.ZFACECOUNT AS 'zPerson-Face Count',       
        zDetFace.ZFACEALGORITHMVERSION AS 'zDetFace-Face Algorithm Version',
        zDetFace.ZADJUSTMENTVERSION AS 'zDetFace-Adjustment Version',       
        zPerson.ZINPERSONNAMINGMODEL AS 'zPerson-In Person Naming Model',
        zPerson.ZKEYFACEPICKSOURCE AS 'zPerson-Key Face Pick Source Key',
        zPerson.ZMANUALORDER AS 'zPerson-Manual Order Key',
        zPerson.ZQUESTIONTYPE AS 'zPerson-Question Type',
        zPerson.ZSUGGESTEDFORCLIENTTYPE AS 'zPerson-Suggested For Client Type',
        zPerson.ZMERGETARGETPERSON AS 'zPerson-Merge Target Person',
        CASE zPerson.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Person Not Synced with Cloud-0'
            WHEN 1 THEN 'Person Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDLOCALSTATE
        END AS 'zPerson-Cloud Local State',
        CASE zFaceCrop.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDLOCALSTATE || ''
        END AS 'zFaceCrop-Cloud Local State',
        CASE zFaceCrop.ZCLOUDTYPE
            WHEN 0 THEN 'Has Name-0'
            WHEN 5 THEN 'Has Face Key-5'
            WHEN 12 THEN '12-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDTYPE || ''
        END AS 'zFaceCrop-Cloud Type',
        CASE zPerson.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDDELETESTATE || ''
        END AS 'zPerson-Cloud Delete State',
        CASE zFaceCrop.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDDELETESTATE || ''
        END AS 'zFaceCrop-Cloud Delete State',
        zDetFace.Z_PK AS 'zDetFace-zPK',
        zDetFacePrint.ZFACE AS 'zDetFacePrint-Face Key',
        zPerson.ZKEYFACE AS 'zPerson-KeyFace=zDetFace-zPK',
        zFaceCrop.ZFACE AS 'zFaceCrop-Face Key',
        zPerson.Z_PK AS 'zPerson-zPK=zDetFace-Person',
        zDetFace.ZPERSON AS 'zDetFace-PersonForFace= zPerson-zPK',
        zDetFace.ZPERSONBEINGKEYFACE AS 'zDetFace-Person Being Key Face',         
        zFaceCrop.ZPERSON AS 'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key',	
        zDetFace.ZFACEPRINT AS 'zDetFace-Face Print',	
        zDetFacePrint.Z_PK AS 'zDetFacePrint-zPK',		
        zDetFace.ZFACECROP AS 'zDetFace-Face Crop',
        zFaceCrop.Z_PK AS 'zFaceCrop-zPK',           
        zDetFaceGroup.ZKEYFACE AS 'zDetFaceGroup-KeyFace= zDetFace-zPK',
        zDetFaceGroup.ZASSOCIATEDPERSON AS 'zDetFaceGroup-AssocPerson= zPerson-zPK',
        zPerson.ZASSOCIATEDFACEGROUP AS 'zPerson-Assoc Face Group Key',
        zDetFace.ZFACEGROUPBEINGKEYFACE AS 'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK',
        zDetFace.ZFACEGROUP AS 'zDetFace-FaceGroup= zDetFaceGroup-zPK',		
        zDetFaceGroup.Z_PK AS 'zDetFaceGroup-zPK',
        zDetFace.ZUUID AS 'zDetFace-UUID',		
        zFaceCrop.ZUUID AS 'zFaceCrop-UUID',		
        zFaceCrop.ZINVALIDMERGECANDIDATEPERSONUUID AS 'zFaceCrop-Invalid Merge Candidate Person UUID',		
        zPerson.ZPERSONUUID AS 'zPerson-Person UUID',
        zPerson.ZPERSONURI AS 'zPerson-Person URI',		
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFace.ZASSET AS 'zDetFace-AssetForFace= zAsset-zPK',
        zFaceCrop.ZASSET AS 'zFaceCrop-Asset Key',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
            LEFT JOIN ZDETECTEDFACE zDetFace ON zAsset.Z_PK = zDetFace.ZASSET
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSON
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP       
        WHERE zDetFace.Z_PK > 0  
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            personcontactmatchingdictionary = ''
            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            facecropresourcedata_blob = ''

            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            if row[25] is not None:
                pathto = os.path.join(report_folder, 'zPerson-ContactMatchingDict_' + row[127] + '.plist')
                with open(pathto, 'ab') as wf:
                    wf.write(row[25])

                with open(pathto, 'rb') as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        personcontactmatchingdictionary = deserialized_plist

                    except (KeyError, ValueError, TypeError) as ex:
                        if str(ex).find("does not contain an '$archiver' key") >= 0:
                            logfunc('plist was Not an NSKeyedArchive ' + row[127])
                        else:
                            logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[127])

            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            if row[32] is not None:
                pathto = os.path.join(report_folder, 'FaceCropFor_' + row[125] + '.jpg')
                with open(pathto, 'wb') as file:
                    file.write(row[32])
                facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                            row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                            row[19], row[20], row[21], row[22], row[23], row[24],
                            personcontactmatchingdictionary,
                            row[26], row[27],
                            row[28], row[29], row[30], row[31],
                            facecropresourcedata_blob,
                            row[33], row[34], row[35], row[36],
                            row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                            row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                            row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                            row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                            row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                            row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                            row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                            row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                            row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
                            row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
                            row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
                            row[132], row[133], row[134], row[135]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        'zAsset-Directory-Path-7',
                        'zAsset-Filename-8',
                        'zAddAssetAttr- Original Filename-9',
                        'zCldMast- Original Filename-10',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-11',
                        'zAsset- Conversation= zGenAlbum_zPK-12',
                        ('zAsset-Trashed Date-13', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-14',
                        'zAddAssetAttr-Imported by Bundle ID-15',
                        'zAddAssetAttr-Imported By Display Name-16',
                        'zCldMast-Imported by Bundle ID-17',
                        'zCldMast-Imported by Display Name-18',
                        'zAsset-Visibility State-19',
                        'zFaceCrop-Face Area Points-20',
                        'zAsset-Face Adjustment Version-21',
                        'zAddAssetAttr-Face_Regions-SeeRawDBData-22',
                        'zAddAssetAttr-Face Analysis Version-23',
                        'zDetFacePrint-Data-SeeRawDBData-24',
                        'zPerson-Contact Matching Dictionary-25',
                        'zPerson-Verified Type-26',
                        'zPerson-Display Name-27',
                        'zPerson-Full Name-28',
                        'zPerson-Cloud Verified Type-29',
                        'zFaceCrop-State-30',
                        'zFaceCrop-Type-31',
                        'zFaceCrop-Resource Data-32',
                        'zDetFace-Confirmed Face Crop Generation State-33',
                        'zDetFace-Manual-34',
                        'zDetFace-Detection Type-35',
                        'zPerson-Detection Type-36',
                        'zDetFace-VIP Model Type-37',
                        'zDetFace-Name Source-38',
                        'zDetFace-Cloud Name Source-39',
                        'zPerson-Type-40',
                        'zPerson-Gender Type-41',
                        'zDetFace-Gender Type-42',
                        'zDetFace-Center X-43',
                        'zDetFace-Center Y-44',
                        'zPerson-Age Type Estimate-45',
                        'zDetFace-Age Type Estimate-46',
                        'zDetFace-Ethnicity Type-47',
                        'zDetFace-Skin Tone Type-48',
                        'zDetFace-Hair Type-49',
                        'zDetFace-Hair Color Type-50',
                        'zDetFace-Head Gear Type-51',
                        'zDetFace-Facial Hair Type-52',
                        'zDetFace-Has Face Mask-53',
                        'zDetFace-Pose Type-54',
                        'zDetFace-Face Expression Type-55',
                        'zDetFace-Has Smile-56',
                        'zDetFace-Smile Type-57',
                        'zDetFace-Lip Makeup Type-58',
                        'zDetFace-Eyes State-59',
                        'zDetFace-Is Left Eye Closed-60',
                        'zDetFace-Is Right Eye Closed-61',
                        'zDetFace-Gaze Center X-62',
                        'zDetFace-Gaze Center Y-63',
                        'zDetFace-Face Gaze Type-64',
                        'zDetFace-Eye Glasses Type-65',
                        'zDetFace-Eye Makeup Type-66',
                        'zDetFace-Cluster Sequence Number Key-67',
                        'zDetFace-Grouping ID-68',
                        'zDetFace-Master ID-69',
                        'zDetFace-Quality-70',
                        'zDetFace-Quality Measure-71',
                        'zDetFace-Source Height-72',
                        'zDetFace-Source Width-73',
                        'zDetFace-Asset Visible-74',
                        'zDetFace-Hidden/Asset Hidden-75',
                        'zDetFace-In Trash/Recently Deleted-76',
                        'zDetFace-Cloud Local State-77',
                        'zDetFace-Training Type-78',
                        'zDetFace.Pose Yaw-79',
                        'zDetFace-Body Center X-80',
                        'zDetFace-Body Center Y-81',
                        'zDetFace-Body Height-82',
                        'zDetFace-Body Width-83',
                        'zDetFace-Roll-84',
                        'zDetFace-Size-85',
                        'zDetFace-Cluster Sequence Number-86',
                        'zDetFace-Blur Score-87',
                        'zDetFacePrint-Face Print Version-88',
                        'zDetFaceGroup-UUID-89',
                        'zDetFaceGroup-Person Builder State-90',
                        'zDetFaceGroup-UnNamed Face Count-91',
                        'zPerson-Face Count-92',
                        'zDetFace-Face Algorithm Version-93',
                        'zDetFace-Adjustment Version-94',
                        'zPerson-In Person Naming Model-95',
                        'zPerson-Key Face Pick Source Key-96',
                        'zPerson-Manual Order Key-97',
                        'zPerson-Question Type-98',
                        'zPerson-Suggested For Client Type-99',
                        'zPerson-Merge Target Person-100',
                        'zPerson-Cloud Local State-101',
                        'zFaceCrop-Cloud Local State-102',
                        'zFaceCrop-Cloud Type-103',
                        'zPerson-Cloud Delete State-104',
                        'zFaceCrop-Cloud Delete State-105',
                        'zDetFace-zPK-106',
                        'zDetFacePrint-Face Key-107',
                        'zPerson-KeyFace=zDetFace-zPK-108',
                        'zFaceCrop-Face Key-109',
                        'zPerson-zPK=zDetFace-Person-110',
                        'zDetFace-PersonForFace= zPerson-zPK-111',
                        'zDetFace-Person Being Key Face-112',
                        'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-113',
                        'zDetFace-Face Print-114',
                        'zDetFacePrint-zPK-115',
                        'zDetFace-Face Crop-116',
                        'zFaceCrop-zPK-117',
                        'zDetFaceGroup-KeyFace= zDetFace-zPK-118',
                        'zDetFaceGroup-AssocPerson= zPerson-zPK-119',
                        'zPerson-Assoc Face Group Key-120',
                        'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-121',
                        'zDetFace-FaceGroup= zDetFaceGroup-zPK-122',
                        'zDetFaceGroup-zPK-123',
                        'zDetFace-UUID-124',
                        'zFaceCrop-UUID-125',
                        'zFaceCrop-Invalid Merge Candidate Person UUID-126',
                        'zPerson-Person UUID-127',
                        'zPerson-Person URI-128',
                        'zDetFaceGroup-UUID-129',
                        'zDetFace-AssetForFace= zAsset-zPK-130',
                        'zFaceCrop-Asset Key-131',
                        'zAsset-zPK-132',
                        'zAddAssetAttr-zPK-133',
                        'zAsset-UUID = store.cloudphotodb-134',
                        'zAddAssetAttr-Master Fingerprint-135')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("17")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',  
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE
            WHEN zAsset.ZFACEAREAPOINTS > 0 THEN 'Face Area Points Detected in zAsset'
            ELSE 'Face Area Points Not Detected in zAsset'
        END AS 'zFaceCrop-Face Area Points',
        zAsset.ZFACEADJUSTMENTVERSION AS 'zAsset-Face Adjustment Version',
        CASE
            WHEN zAddAssetAttr.ZFACEREGIONS > 0 THEN 'zAddAssetAttr-Face_Regions_has_Data'
            ELSE 'zAddAssetAttr-Face_Regions_has_NO-Data'
        END AS 'zAddAssetAttr-Face_Regions-SeeRawDBData',
        zAddAssetAttr.ZFACEANALYSISVERSION AS 'zAddAssetAttr-Face Analysis Version',
        CASE
            WHEN zDetFacePrint.ZDATA > 0 THEN 'zDetFacePrint-Data_has_Data'
            ELSE 'zDetFacePrint-Data_NO-Data'
        END AS 'zDetFacePrint-Data-SeeRawDBData',
        zPerson.ZCONTACTMATCHINGDICTIONARY AS 'zPerson-Contact Matching Dictionary',
        CASE zPerson.ZVERIFIEDTYPE
            WHEN 0 THEN '0-Not-Verified'
            WHEN 1 THEN '1-Has_Contact Matching_Dictionary'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZVERIFIEDTYPE || ''
        END AS 'zPerson-Verified Type',
        zPerson.ZDISPLAYNAME AS 'zPerson-Display Name',
        zPerson.ZFULLNAME AS 'zPerson-Full Name',
        CASE zPerson.ZCLOUDVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDVERIFIEDTYPE || ''
        END AS 'zPerson-Cloud Verified Type',
        CASE zFaceCrop.ZSTATE
            WHEN 5 THEN 'Validated-5'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZSTATE || ''
        END AS 'zFaceCrop-State',
        CASE zFaceCrop.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-Active'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZTYPE || ''
        END AS 'zFaceCrop-Type',
        zFaceCrop.ZRESOURCEDATA AS 'zFaceCrop-Resource Data',	
        CASE zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE || ''
        END AS 'zDetFace-Confirmed Face Crop Generation State',
        CASE zDetFace.ZMANUAL
            WHEN 0 THEN 'zDetFace-Auto Detected-0'
            WHEN 1 THEN 'zDetFace-Manually Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZMANUAL || ''
        END AS 'zDetFace-Manual',
        CASE zDetFace.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZDETECTIONTYPE || ''
        END AS 'zDetFace-Detection Type',
        CASE zPerson.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZDETECTIONTYPE || ''
        END AS 'zPerson-Detection Type',
        CASE zDetFace.ZVIPMODELTYPE
            WHEN 0 THEN 'Not VIP-0'
            WHEN 1 THEN 'VIP-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZVIPMODELTYPE || ''
        END AS 'zDetFace-VIP Model Type',
        CASE zDetFace.ZNAMESOURCE
            WHEN 0 THEN 'No Name Listed-0'
            WHEN 1 THEN '1-Face Crop-1'
            WHEN 2 THEN '2-Verified/Has-Person-URI'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZNAMESOURCE || ''
        END AS 'zDetFace-Name Source',
        CASE zDetFace.ZCLOUDNAMESOURCE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN '1-User Added Via Face Crop-1'
            WHEN 5 THEN '5-Asset Shared has Name'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDNAMESOURCE || ''
        END AS 'zDetFace-Cloud Name Source',
        zPerson.ZMERGECANDIDATECONFIDENCE AS 'zPerson-Merge Candidate Confidence',
        CASE zPerson.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZTYPE || ''
        END AS 'zPerson-Type',
        CASE zPerson.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZGENDERTYPE || ''
        END AS 'zPerson-Gender Type',
        CASE zDetFace.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGENDERTYPE || ''
        END AS 'zDetFace-Gender Type',
        zDetFace.ZCENTERX AS 'zDetFace-Center X',
        zDetFace.ZCENTERY AS 'zDetFace-Center Y',
        CASE zPerson.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZAGETYPE || ''
        END AS 'zPerson-Age Type Estimate',
        CASE zDetFace.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZAGETYPE || ''
        END AS 'zDetFace-Age Type Estimate',
        CASE zDetFace.ZETHNICITYTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/African American-1'
            WHEN 2 THEN 'White-2'
            WHEN 3 THEN 'Hispanic/Latino-3'
            WHEN 4 THEN 'Asian-4'
            WHEN 5 THEN 'Native Hawaiian/Other Pacific Islander-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZETHNICITYTYPE || ''
        END AS 'zDetFace-Ethnicity Type',
        CASE zDetFace.ZSKINTONETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Light-Pale White Skin Tone-1'
            WHEN 2 THEN 'White-Fair Skin Tone-2'
            WHEN 3 THEN 'Medium-White to Olive Skin Tone-3'
            WHEN 4 THEN 'Olive-Moderate Brown Skin Tone-4'
            WHEN 5 THEN 'Brown-Dark Brown Skin Tone-5'
            WHEN 6 THEN 'Black-Very Dark Brown to Black Skin Tone-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSKINTONETYPE || ''
        END AS 'zDetFace-Skin Tone Type',
        CASE zDetFace.ZHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            WHEN 6 THEN '6-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRTYPE || ''
        END AS 'zDetFace-Hair Type',
        CASE zDetFace.ZHAIRCOLORTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/Brown Hair Color-1'
            WHEN 2 THEN 'Brown/Blonde Hair Color-2'
            WHEN 3 THEN 'Brown/Red Hair Color-3'
            WHEN 4 THEN 'Red/White Hair Color-4'
            WHEN 5 THEN 'StillTesting/Artifical-5'
            WHEN 6 THEN 'White/Bald Hair Color-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRCOLORTYPE || ''
        END AS 'zDetFace-Hair Color Type',
        CASE zDetFace.ZHEADGEARTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-No Headgear'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHEADGEARTYPE || ''
        END AS 'zDetFace-Head Gear Type',
        CASE zDetFace.ZFACIALHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Clean Shaven Facial Hair Type-1'
            WHEN 2 THEN 'Beard Facial Hair Type-2'
            WHEN 3 THEN 'Goatee Facial Hair Type-3'
            WHEN 4 THEN 'Mustache Facial Hair Type-4'
            WHEN 5 THEN 'Stubble Facial Hair Type-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACIALHAIRTYPE || ''
        END AS 'zDetFace-Facial Hair Type',
        CASE zDetFace.ZHASFACEMASK
            WHEN 0 THEN 'No Mask-0'
            WHEN 1 THEN 'Has Mask-1'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASFACEMASK || ''
        END AS 'zDetFace-Has Face Mask',
        CASE zDetFace.ZPOSETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Face Frontal Pose-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN 'Face Profile Pose-3'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZPOSETYPE || ''
        END AS 'zDetFace-Pose Type',
        CASE zDetFace.ZFACEEXPRESSIONTYPE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN 'Disgusted/Angry-1'
            WHEN 2 THEN 'Suprised/Fearful-2'
            WHEN 3 THEN 'Neutral-3'
            WHEN 4 THEN 'Confident/Smirk-4'
            WHEN 5 THEN 'Happiness-5'
            WHEN 6 THEN 'Sadness-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACEEXPRESSIONTYPE || ''
        END AS 'zDetFace-Face Expression Type',
        CASE zDetFace.ZHASSMILE
            WHEN 0 THEN 'zDetFace No Smile-0'
            WHEN 1 THEN 'zDetFace Smile-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASSMILE || ''
        END AS 'zDetFace-Has Smile',
        CASE zDetFace.ZSMILETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'zDetFace Smile No Teeth-1'
            WHEN 2 THEN 'zDetFace Smile has Teeth-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSMILETYPE || ''
        END AS 'zDetFace-Smile Type',
        CASE zDetFace.ZLIPMAKEUPTYPE
            WHEN 0 THEN 'zDetFace No Lip Makeup-0'
            WHEN 1 THEN 'zDetFace Lip Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZLIPMAKEUPTYPE || ''
        END AS 'zDetFace-Lip Makeup Type',
        CASE zDetFace.ZEYESSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eyes Closed-1'
            WHEN 2 THEN 'Eyes Open-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYESSTATE || ''
        END AS 'zDetFace-Eyes State',
        CASE zDetFace.ZISLEFTEYECLOSED
            WHEN 0 THEN 'Left Eye Open-0'
            WHEN 1 THEN 'Left Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISLEFTEYECLOSED || ''
        END AS 'zDetFace-Is Left Eye Closed',
        CASE zDetFace.ZISRIGHTEYECLOSED
            WHEN 0 THEN 'Right Eye Open-0'
            WHEN 1 THEN 'Right Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISRIGHTEYECLOSED || ''
        END AS 'zDetFace-Is Right Eye Closed',
        zDetFace.ZGAZECENTERX AS 'zDetFace-Gaze Center X',
        zDetFace.ZGAZECENTERY AS 'zDetFace-Gaze Center Y',
        CASE zDetFace.ZGAZETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGAZETYPE || ''
        END AS 'zDetFace-Face Gaze Type',
        CASE zDetFace.ZGLASSESTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eye Glasses-1'
            WHEN 2 THEN 'Sun Glasses-2'
            WHEN 3 THEN 'No Glasses-3'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGLASSESTYPE || ''
        END AS 'zDetFace-Eye Glasses Type',
        CASE zDetFace.ZEYEMAKEUPTYPE
            WHEN 0 THEN 'No Eye Makeup-0'
            WHEN 1 THEN 'Eye Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYEMAKEUPTYPE || ''
        END AS 'zDetFace-Eye Makeup Type',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Sequence Number Key',
        zDetFace.ZGROUPINGIDENTIFIER AS 'zDetFace-Grouping ID',
        zDetFace.ZMASTERIDENTIFIER AS 'zDetFace-Master ID',
        zDetFace.ZQUALITY AS 'zDetFace-Quality',
        zDetFace.ZQUALITYMEASURE AS 'zDetFace-Quality Measure',
        zDetFace.ZSOURCEHEIGHT AS 'zDetFace-Source Height',
        zDetFace.ZSOURCEWIDTH AS 'zDetFace-Source Width',
        CASE zDetFace.ZASSETVISIBLE
            WHEN 0 THEN '0-Unknown-StillTesitng-0'
            WHEN 1 THEN '1-Unknown-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZASSETVISIBLE || ''
        END AS 'zDetFace-Asset Visible',
        CASE zDetFace.ZHIDDEN
            WHEN 0 THEN 'Not Hidden-0'
            WHEN 1 THEN 'Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHIDDEN || ''
        END AS 'zDetFace-Hidden/Asset Hidden',
        CASE zDetFace.ZISINTRASH
            WHEN 0 THEN 'Not In Trash-0'
            WHEN 1 THEN 'In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISINTRASH || ''
        END AS 'zDetFace-In Trash/Recently Deleted',
        CASE zDetFace.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDLOCALSTATE || ''
        END AS 'zDetFace-Cloud Local State',
        CASE zDetFace.ZTRAININGTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZTRAININGTYPE
        END AS 'zDetFace-Training Type',
        zDetFace.ZPOSEYAW AS 'zDetFace.Pose Yaw',
        zDetFace.ZBODYCENTERX AS 'zDetFace-Body Center X',
        zDetFace.ZBODYCENTERY AS 'zDetFace-Body Center Y',
        zDetFace.ZBODYHEIGHT AS 'zDetFace-Body Height',
        zDetFace.ZBODYWIDTH AS 'zDetFace-Body Width',
        zDetFace.ZROLL AS 'zDetFace-Roll',
        zDetFace.ZSIZE AS 'zDetFace-Size',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Sequence Number',
        zDetFace.ZBLURSCORE AS 'zDetFace-Blur Score',
        zDetFacePrint.ZFACEPRINTVERSION AS 'zDetFacePrint-Face Print Version',
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFaceGroup.ZPERSONBUILDERSTATE AS 'zDetFaceGroup-Person Builder State',
        zDetFaceGroup.ZUNNAMEDFACECOUNT AS 'zDetFaceGroup-UnNamed Face Count',
        zPerson.ZFACECOUNT AS 'zPerson-Face Count',       
        zDetFace.ZFACEALGORITHMVERSION AS 'zDetFace-Face Algorithm Version',
        zDetFace.ZADJUSTMENTVERSION AS 'zDetFace-Adjustment Version',       
        zPerson.ZINPERSONNAMINGMODEL AS 'zPerson-In Person Naming Model',
        zPerson.ZKEYFACEPICKSOURCE AS 'zPerson-Key Face Pick Source Key',
        zPerson.ZMANUALORDER AS 'zPerson-Manual Order Key',
        zPerson.ZQUESTIONTYPE AS 'zPerson-Question Type',
        zPerson.ZSUGGESTEDFORCLIENTTYPE AS 'zPerson-Suggested For Client Type',
        zPerson.ZMERGETARGETPERSON AS 'zPerson-Merge Target Person',
        CASE zPerson.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Person Not Synced with Cloud-0'
            WHEN 1 THEN 'Person Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDLOCALSTATE
        END AS 'zPerson-Cloud Local State',
        CASE zFaceCrop.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDLOCALSTATE || ''
        END AS 'zFaceCrop-Cloud Local State',
        CASE zFaceCrop.ZCLOUDTYPE
            WHEN 0 THEN 'Has Name-0'
            WHEN 5 THEN 'Has Face Key-5'
            WHEN 12 THEN '12-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDTYPE || ''
        END AS 'zFaceCrop-Cloud Type',
        CASE zPerson.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDDELETESTATE || ''
        END AS 'zPerson-Cloud Delete State',
        CASE zFaceCrop.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDDELETESTATE || ''
        END AS 'zFaceCrop-Cloud Delete State',
        zDetFace.Z_PK AS 'zDetFace-zPK',
        zDetFacePrint.ZFACE AS 'zDetFacePrint-Face Key',
        zPerson.ZKEYFACE AS 'zPerson-KeyFace=zDetFace-zPK',
        zFaceCrop.ZFACE AS 'zFaceCrop-Face Key',
        zPerson.Z_PK AS 'zPerson-zPK=zDetFace-Person',
        zDetFace.ZPERSON AS 'zDetFace-PersonForFace= zPerson-zPK',
        zDetFace.ZPERSONBEINGKEYFACE AS 'zDetFace-Person Being Key Face',         
        zFaceCrop.ZPERSON AS 'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key',	
        zDetFace.ZFACEPRINT AS 'zDetFace-Face Print',	
        zDetFacePrint.Z_PK AS 'zDetFacePrint-zPK',		
        zDetFace.ZFACECROP AS 'zDetFace-Face Crop',
        zFaceCrop.Z_PK AS 'zFaceCrop-zPK',           
        zDetFaceGroup.ZKEYFACE AS 'zDetFaceGroup-KeyFace= zDetFace-zPK',
        zDetFaceGroup.ZASSOCIATEDPERSON AS 'zDetFaceGroup-AssocPerson= zPerson-zPK',
        zPerson.ZASSOCIATEDFACEGROUP AS 'zPerson-Assoc Face Group Key',
        zDetFace.ZFACEGROUPBEINGKEYFACE AS 'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK',
        zDetFace.ZFACEGROUP AS 'zDetFace-FaceGroup= zDetFaceGroup-zPK',		
        zDetFaceGroup.Z_PK AS 'zDetFaceGroup-zPK',
        zPerson.ZSHAREPARTICIPANT AS 'zPerson-Share Participant= zSharePartic-zPK',		
        zDetFace.ZUUID AS 'zDetFace-UUID',		
        zFaceCrop.ZUUID AS 'zFaceCrop-UUID',	
        zFaceCrop.ZINVALIDMERGECANDIDATEPERSONUUID AS 'zFaceCrop-Invalid Merge Candidate Person UUID',		
        zPerson.ZPERSONUUID AS 'zPerson-Person UUID',
        zPerson.ZPERSONURI AS 'zPerson-Person URI',		
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFace.ZASSET AS 'zDetFace-AssetForFace= zAsset-zPK',
        zFaceCrop.ZASSET AS 'zFaceCrop-Asset Key',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
            LEFT JOIN ZDETECTEDFACE zDetFace ON zAsset.Z_PK = zDetFace.ZASSET
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSON
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP
        WHERE zDetFace.Z_PK > 0  
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            personcontactmatchingdictionary = ''
            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            facecropresourcedata_blob = ''

            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            if row[26] is not None:
                pathto = os.path.join(report_folder, 'zPerson-ContactMatchingDict_' + row[130] + '.plist')
                with open(pathto, 'ab') as wf:
                    wf.write(row[26])

                with open(pathto, 'rb') as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        personcontactmatchingdictionary = deserialized_plist

                    except (KeyError, ValueError, TypeError) as ex:
                        if str(ex).find("does not contain an '$archiver' key") >= 0:
                            logfunc('plist was Not an NSKeyedArchive ' + row[130])
                        else:
                            logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[130])

            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            if row[33] is not None:
                pathto = os.path.join(report_folder, 'FaceCropFor_' + row[128] + '.jpg')
                with open(pathto, 'wb') as file:
                    file.write(row[33])
                facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                            row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                            row[19], row[20], row[21], row[22], row[23], row[24], row[25],
                            personcontactmatchingdictionary,
                            row[27], row[28], row[29], row[30], row[31], row[32],
                            facecropresourcedata_blob,
                            row[34], row[35], row[36],
                            row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                            row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                            row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                            row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                            row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                            row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                            row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                            row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                            row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
                            row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
                            row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
                            row[132], row[133], row[134], row[135], row[136], row[137], row[138]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        'zAsset-Directory-Path-7',
                        'zAsset-Filename-8',
                        'zAddAssetAttr- Original Filename-9',
                        'zCldMast- Original Filename-10',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-11',
                        'zAsset- Conversation= zGenAlbum_zPK-12',
                        ('zAsset-Trashed Date-13', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-14',
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-15',
                        'zAddAssetAttr-Imported by Bundle ID-16',
                        'zAddAssetAttr-Imported By Display Name-17',
                        'zCldMast-Imported by Bundle ID-18',
                        'zCldMast-Imported by Display Name-19',
                        'zAsset-Visibility State-20',
                        'zFaceCrop-Face Area Points-21',
                        'zAsset-Face Adjustment Version-22',
                        'zAddAssetAttr-Face_Regions-SeeRawDBData-23',
                        'zAddAssetAttr-Face Analysis Version-24',
                        'zDetFacePrint-Data-SeeRawDBData-25',
                        'zPerson-Contact Matching Dictionary-26',
                        'zPerson-Verified Type-27',
                        'zPerson-Display Name-28',
                        'zPerson-Full Name-29',
                        'zPerson-Cloud Verified Type-30',
                        'zFaceCrop-State-31',
                        'zFaceCrop-Type-32',
                        'zFaceCrop-Resource Data-33',
                        'zDetFace-Confirmed Face Crop Generation State-34',
                        'zDetFace-Manual-35',
                        'zDetFace-Detection Type-36',
                        'zPerson-Detection Type-37',
                        'zDetFace-VIP Model Type-38',
                        'zDetFace-Name Source-39',
                        'zDetFace-Cloud Name Source-40',
                        'zPerson-Merge Candidate Confidence-41',
                        'zPerson-Type-42',
                        'zPerson-Gender Type-43',
                        'zDetFace-Gender Type-44',
                        'zDetFace-Center X-45',
                        'zDetFace-Center Y-46',
                        'zPerson-Age Type Estimate-47',
                        'zDetFace-Age Type Estimate-48',
                        'zDetFace-Ethnicity Type-49',
                        'zDetFace-Skin Tone Type-50',
                        'zDetFace-Hair Type-51',
                        'zDetFace-Hair Color Type-52',
                        'zDetFace-Head Gear Type-53',
                        'zDetFace-Facial Hair Type-54',
                        'zDetFace-Has Face Mask-55',
                        'zDetFace-Pose Type-56',
                        'zDetFace-Face Expression Type-57',
                        'zDetFace-Has Smile-58',
                        'zDetFace-Smile Type-59',
                        'zDetFace-Lip Makeup Type-60',
                        'zDetFace-Eyes State-61',
                        'zDetFace-Is Left Eye Closed-62',
                        'zDetFace-Is Right Eye Closed-63',
                        'zDetFace-Gaze Center X-64',
                        'zDetFace-Gaze Center Y-65',
                        'zDetFace-Face Gaze Type-66',
                        'zDetFace-Eye Glasses Type-67',
                        'zDetFace-Eye Makeup Type-68',
                        'zDetFace-Cluster Sequence Number Key-69',
                        'zDetFace-Grouping ID-70',
                        'zDetFace-Master ID-71',
                        'zDetFace-Quality-72',
                        'zDetFace-Quality Measure-73',
                        'zDetFace-Source Height-74',
                        'zDetFace-Source Width-75',
                        'zDetFace-Asset Visible-76',
                        'zDetFace-Hidden/Asset Hidden-77',
                        'zDetFace-In Trash/Recently Deleted-78',
                        'zDetFace-Cloud Local State-79',
                        'zDetFace-Training Type-80',
                        'zDetFace.Pose Yaw-81',
                        'zDetFace-Body Center X-82',
                        'zDetFace-Body Center Y-83',
                        'zDetFace-Body Height-84',
                        'zDetFace-Body Width-85',
                        'zDetFace-Roll-86',
                        'zDetFace-Size-87',
                        'zDetFace-Cluster Sequence Number-88',
                        'zDetFace-Blur Score-89',
                        'zDetFacePrint-Face Print Version-90',
                        'zDetFaceGroup-UUID-91',
                        'zDetFaceGroup-Person Builder State-92',
                        'zDetFaceGroup-UnNamed Face Count-93',
                        'zPerson-Face Count-94',
                        'zDetFace-Face Algorithm Version-95',
                        'zDetFace-Adjustment Version-96',
                        'zPerson-In Person Naming Model-97',
                        'zPerson-Key Face Pick Source Key-98',
                        'zPerson-Manual Order Key-99',
                        'zPerson-Question Type-100',
                        'zPerson-Suggested For Client Type-101',
                        'zPerson-Merge Target Person-102',
                        'zPerson-Cloud Local State-103',
                        'zFaceCrop-Cloud Local State-104',
                        'zFaceCrop-Cloud Type-105',
                        'zPerson-Cloud Delete State-106',
                        'zFaceCrop-Cloud Delete State-107',
                        'zDetFace-zPK-108',
                        'zDetFacePrint-Face Key-109',
                        'zPerson-KeyFace=zDetFace-zPK-110',
                        'zFaceCrop-Face Key-111',
                        'zPerson-zPK=zDetFace-Person-112',
                        'zDetFace-PersonForFace= zPerson-zPK-113',
                        'zDetFace-Person Being Key Face-114',
                        'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-115',
                        'zDetFace-Face Print-116',
                        'zDetFacePrint-zPK-117',
                        'zDetFace-Face Crop-118',
                        'zFaceCrop-zPK-119',
                        'zDetFaceGroup-KeyFace= zDetFace-zPK-120',
                        'zDetFaceGroup-AssocPerson= zPerson-zPK-121',
                        'zPerson-Assoc Face Group Key-122',
                        'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-123',
                        'zDetFace-FaceGroup= zDetFaceGroup-zPK-124',
                        'zDetFaceGroup-zPK-125',
                        'zPerson-Share Participant= zSharePartic-zPK-126',
                        'zDetFace-UUID-127',
                        'zFaceCrop-UUID-128',
                        'zFaceCrop-Invalid Merge Candidate Person UUID-129',
                        'zPerson-Person UUID-130',
                        'zPerson-Person URI-131',
                        'zDetFaceGroup-UUID-132',
                        'zDetFace-AssetForFace= zAsset-zPK-133',
                        'zFaceCrop-Asset Key-134',
                        'zAsset-zPK-135',
                        'zAddAssetAttr-zPK-136',
                        'zAsset-UUID = store.cloudphotodb-137',
                        'zAddAssetAttr-Master Fingerprint-138')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("17")) & (version.parse(iosversion) < version.parse("18")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',  
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE
            WHEN zAsset.ZFACEAREAPOINTS > 0 THEN 'Face Area Points Detected in zAsset'
            ELSE 'Face Area Points Not Detected in zAsset'
        END AS 'zFaceCrop-Face Area Points',
        zAsset.ZFACEADJUSTMENTVERSION AS 'zAsset-Face Adjustment Version',
        CASE
            WHEN zAddAssetAttr.ZFACEREGIONS > 0 THEN 'zAddAssetAttr-Face_Regions_has_Data'
            ELSE 'zAddAssetAttr-Face_Regions_has_NO-Data'
        END AS 'zAddAssetAttr-Face_Regions-SeeRawDBData',
        zAddAssetAttr.ZFACEANALYSISVERSION AS 'zAddAssetAttr-Face Analysis Version',
        zDetFace.ZASSETFORTEMPORALDETECTEDFACES AS 'zDetFace-Asset For Temporal Detected Faces= zAsset-zPK',
        CASE
            WHEN zDetFacePrint.ZDATA > 0 THEN 'zDetFacePrint-Data_has_Data'
            ELSE 'zDetFacePrint-Data_NO-Data'
        END AS 'zDetFacePrint-Data-SeeRawDBData',
        zPerson.ZCONTACTMATCHINGDICTIONARY AS 'zPerson-Contact Matching Dictionary',
        CASE zPerson.ZVERIFIEDTYPE
            WHEN 0 THEN '0-Not-Verified'
            WHEN 1 THEN '1-Has_Contact Matching_Dictionary'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZVERIFIEDTYPE || ''
        END AS 'zPerson-Verified Type',
        zPerson.ZDISPLAYNAME AS 'zPerson-Display Name',
        zPerson.ZFULLNAME AS 'zPerson-Full Name',
        CASE zPerson.ZCLOUDVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDVERIFIEDTYPE || ''
        END AS 'zPerson-Cloud Verified Type',
        CASE zFaceCrop.ZSTATE
            WHEN 5 THEN 'Validated-5'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZSTATE || ''
        END AS 'zFaceCrop-State',
        CASE zFaceCrop.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-Active'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZTYPE || ''
        END AS 'zFaceCrop-Type',
        zFaceCrop.ZRESOURCEDATA AS 'zFaceCrop-Resource Data',	
        CASE zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE || ''
        END AS 'zDetFace-Confirmed Face Crop Generation State',
        CASE zDetFace.ZMANUAL
            WHEN 0 THEN 'zDetFace-Auto Detected-0'
            WHEN 1 THEN 'zDetFace-Manually Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZMANUAL || ''
        END AS 'zDetFace-Manual',
        CASE zDetFace.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZDETECTIONTYPE || ''
        END AS 'zDetFace-Detection Type',
        CASE zPerson.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZDETECTIONTYPE || ''
        END AS 'zPerson-Detection Type',
        CASE zDetFace.ZVIPMODELTYPE
            WHEN 0 THEN 'Not VIP-0'
            WHEN 1 THEN 'VIP-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZVIPMODELTYPE || ''
        END AS 'zDetFace-VIP Model Type',
        CASE zDetFace.ZNAMESOURCE
            WHEN 0 THEN 'No Name Listed-0'
            WHEN 1 THEN '1-Face Crop-1'
            WHEN 2 THEN '2-Verified/Has-Person-URI'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZNAMESOURCE || ''
        END AS 'zDetFace-Name Source',
        CASE zDetFace.ZCLOUDNAMESOURCE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN '1-User Added Via Face Crop-1'
            WHEN 5 THEN '5-Asset Shared has Name'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDNAMESOURCE || ''
        END AS 'zDetFace-Cloud Name Source',
        zPerson.ZMERGECANDIDATECONFIDENCE AS 'zPerson-Merge Candidate Confidence',
        CASE zPerson.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZTYPE || ''
        END AS 'zPerson-Type',
        CASE zPerson.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZGENDERTYPE || ''
        END AS 'zPerson-Gender Type',
        CASE zDetFace.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGENDERTYPE || ''
        END AS 'zDetFace-Gender Type',
        zDetFace.ZCENTERX AS 'zDetFace-Center X',
        zDetFace.ZCENTERY AS 'zDetFace-Center Y',
        CASE zPerson.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZAGETYPE || ''
        END AS 'zPerson-Age Type Estimate',
        CASE zDetFace.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZAGETYPE || ''
        END AS 'zDetFace-Age Type Estimate',
        CASE zDetFace.ZETHNICITYTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/African American-1'
            WHEN 2 THEN 'White-2'
            WHEN 3 THEN 'Hispanic/Latino-3'
            WHEN 4 THEN 'Asian-4'
            WHEN 5 THEN 'Native Hawaiian/Other Pacific Islander-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZETHNICITYTYPE || ''
        END AS 'zDetFace-Ethnicity Type',
        CASE zDetFace.ZSKINTONETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Light-Pale White Skin Tone-1'
            WHEN 2 THEN 'White-Fair Skin Tone-2'
            WHEN 3 THEN 'Medium-White to Olive Skin Tone-3'
            WHEN 4 THEN 'Olive-Moderate Brown Skin Tone-4'
            WHEN 5 THEN 'Brown-Dark Brown Skin Tone-5'
            WHEN 6 THEN 'Black-Very Dark Brown to Black Skin Tone-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSKINTONETYPE || ''
        END AS 'zDetFace-Skin Tone Type',
        CASE zDetFace.ZHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            WHEN 6 THEN '6-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRTYPE || ''
        END AS 'zDetFace-Hair Type',
        CASE zDetFace.ZHAIRCOLORTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/Brown Hair Color-1'
            WHEN 2 THEN 'Brown/Blonde Hair Color-2'
            WHEN 3 THEN 'Brown/Red Hair Color-3'
            WHEN 4 THEN 'Red/White Hair Color-4'
            WHEN 5 THEN 'StillTesting/Artifical-5'
            WHEN 6 THEN 'White/Bald Hair Color-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRCOLORTYPE || ''
        END AS 'zDetFace-Hair Color Type',
        CASE zDetFace.ZHEADGEARTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-No Headgear'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHEADGEARTYPE || ''
        END AS 'zDetFace-Head Gear Type',
        CASE zDetFace.ZFACIALHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Clean Shaven Facial Hair Type-1'
            WHEN 2 THEN 'Beard Facial Hair Type-2'
            WHEN 3 THEN 'Goatee Facial Hair Type-3'
            WHEN 4 THEN 'Mustache Facial Hair Type-4'
            WHEN 5 THEN 'Stubble Facial Hair Type-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACIALHAIRTYPE || ''
        END AS 'zDetFace-Facial Hair Type',
        CASE zDetFace.ZHASFACEMASK
            WHEN 0 THEN 'No Mask-0'
            WHEN 1 THEN 'Has Mask-1'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASFACEMASK || ''
        END AS 'zDetFace-Has Face Mask',
        CASE zDetFace.ZPOSETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Face Frontal Pose-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN 'Face Profile Pose-3'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZPOSETYPE || ''
        END AS 'zDetFace-Pose Type',
        CASE zDetFace.ZFACEEXPRESSIONTYPE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN 'Disgusted/Angry-1'
            WHEN 2 THEN 'Suprised/Fearful-2'
            WHEN 3 THEN 'Neutral-3'
            WHEN 4 THEN 'Confident/Smirk-4'
            WHEN 5 THEN 'Happiness-5'
            WHEN 6 THEN 'Sadness-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACEEXPRESSIONTYPE || ''
        END AS 'zDetFace-Face Expression Type',
        CASE zDetFace.ZHASSMILE
            WHEN 0 THEN 'zDetFace No Smile-0'
            WHEN 1 THEN 'zDetFace Smile-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASSMILE || ''
        END AS 'zDetFace-Has Smile',
        CASE zDetFace.ZSMILETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'zDetFace Smile No Teeth-1'
            WHEN 2 THEN 'zDetFace Smile has Teeth-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSMILETYPE || ''
        END AS 'zDetFace-Smile Type',
        CASE zDetFace.ZLIPMAKEUPTYPE
            WHEN 0 THEN 'zDetFace No Lip Makeup-0'
            WHEN 1 THEN 'zDetFace Lip Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZLIPMAKEUPTYPE || ''
        END AS 'zDetFace-Lip Makeup Type',
        CASE zDetFace.ZEYESSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eyes Closed-1'
            WHEN 2 THEN 'Eyes Open-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYESSTATE || ''
        END AS 'zDetFace-Eyes State',
        CASE zDetFace.ZISLEFTEYECLOSED
            WHEN 0 THEN 'Left Eye Open-0'
            WHEN 1 THEN 'Left Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISLEFTEYECLOSED || ''
        END AS 'zDetFace-Is Left Eye Closed',
        CASE zDetFace.ZISRIGHTEYECLOSED
            WHEN 0 THEN 'Right Eye Open-0'
            WHEN 1 THEN 'Right Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISRIGHTEYECLOSED || ''
        END AS 'zDetFace-Is Right Eye Closed',
        zDetFace.ZGAZECENTERX AS 'zDetFace-Gaze Center X',
        zDetFace.ZGAZECENTERY AS 'zDetFace-Gaze Center Y',
        CASE zDetFace.ZGAZETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGAZETYPE || ''
        END AS 'zDetFace-Face Gaze Type',
        CASE zDetFace.ZGLASSESTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eye Glasses-1'
            WHEN 2 THEN 'Sun Glasses-2'
            WHEN 3 THEN 'No Glasses-3'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGLASSESTYPE || ''
        END AS 'zDetFace-Eye Glasses Type',
        CASE zDetFace.ZEYEMAKEUPTYPE
            WHEN 0 THEN 'No Eye Makeup-0'
            WHEN 1 THEN 'Eye Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYEMAKEUPTYPE || ''
        END AS 'zDetFace-Eye Makeup Type',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number Key',
        zDetFace.ZGROUPINGIDENTIFIER AS 'zDetFace-Grouping ID',
        zDetFace.ZMASTERIDENTIFIER AS 'zDetFace-Master ID',
        zDetFace.ZQUALITY AS 'zDetFace-Quality',
        zDetFace.ZQUALITYMEASURE AS 'zDetFace-Quality Measure',
        zDetFace.ZSOURCEHEIGHT AS 'zDetFace-Source Height',
        zDetFace.ZSOURCEWIDTH AS 'zDetFace-Source Width',
        CASE zDetFace.ZASSETVISIBLE
            WHEN 0 THEN '0-Unknown-StillTesitng-0'
            WHEN 1 THEN '1-Unknown-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZASSETVISIBLE || ''
        END AS 'zDetFace-Asset Visible',
        CASE zDetFace.ZHIDDEN
            WHEN 0 THEN 'Not Hidden-0'
            WHEN 1 THEN 'Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHIDDEN || ''
        END AS 'zDetFace-Hidden/Asset Hidden',
        CASE zDetFace.ZISINTRASH
            WHEN 0 THEN 'Not In Trash-0'
            WHEN 1 THEN 'In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISINTRASH || ''
        END AS 'zDetFace-In Trash/Recently Deleted',
        CASE zDetFace.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDLOCALSTATE || ''
        END AS 'zDetFace-Cloud Local State',
        CASE zDetFace.ZTRAININGTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZTRAININGTYPE
        END AS 'zDetFace-Training Type',
        zDetFace.ZPOSEYAW AS 'zDetFace.Pose Yaw',
        zDetFace.ZBODYCENTERX AS 'zDetFace-Body Center X',
        zDetFace.ZBODYCENTERY AS 'zDetFace-Body Center Y',
        zDetFace.ZBODYHEIGHT AS 'zDetFace-Body Height',
        zDetFace.ZBODYWIDTH AS 'zDetFace-Body Width',
        zDetFace.ZROLL AS 'zDetFace-Roll',
        zDetFace.ZSIZE AS 'zDetFace-Size',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Sequence Number',
        zDetFace.ZBLURSCORE AS 'zDetFace-Blur Score',
        zDetFacePrint.ZFACEPRINTVERSION AS 'zDetFacePrint-Face Print Version',
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFaceGroup.ZPERSONBUILDERSTATE AS 'zDetFaceGroup-Person Builder State',
        zDetFaceGroup.ZUNNAMEDFACECOUNT AS 'zDetFaceGroup-UnNamed Face Count',
        zPerson.ZFACECOUNT AS 'zPerson-Face Count',       
        zDetFace.ZFACEALGORITHMVERSION AS 'zDetFace-Face Algorithm Version',
        zDetFace.ZADJUSTMENTVERSION AS 'zDetFace-Adjustment Version',       
        zPerson.ZINPERSONNAMINGMODEL AS 'zPerson-In Person Naming Model',
        zPerson.ZKEYFACEPICKSOURCE AS 'zPerson-Key Face Pick Source Key',
        zPerson.ZMANUALORDER AS 'zPerson-Manual Order Key',
        zPerson.ZQUESTIONTYPE AS 'zPerson-Question Type',
        zPerson.ZSUGGESTEDFORCLIENTTYPE AS 'zPerson-Suggested For Client Type',
        zPerson.ZMERGETARGETPERSON AS 'zPerson-Merge Target Person',
        CASE zPerson.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Person Not Synced with Cloud-0'
            WHEN 1 THEN 'Person Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDLOCALSTATE
        END AS 'zPerson-Cloud Local State',
        CASE zFaceCrop.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDLOCALSTATE || ''
        END AS 'zFaceCrop-Cloud Local State',
        CASE zFaceCrop.ZCLOUDTYPE
            WHEN 0 THEN 'Has Name-0'
            WHEN 5 THEN 'Has Face Key-5'
            WHEN 12 THEN '12-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDTYPE || ''
        END AS 'zFaceCrop-Cloud Type',
        CASE zPerson.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDDELETESTATE || ''
        END AS 'zPerson-Cloud Delete State',
        CASE zFaceCrop.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDDELETESTATE || ''
        END AS 'zFaceCrop-Cloud Delete State',
        zDetFace.Z_PK AS 'zDetFace-zPK',
        zDetFacePrint.ZFACE AS 'zDetFacePrint-Face Key',
        zPerson.ZKEYFACE AS 'zPerson-KeyFace=zDetFace-zPK',
        zFaceCrop.ZFACE AS 'zFaceCrop-Face Key',
        zPerson.Z_PK AS 'zPerson-zPK=zDetFace-Person',
        zDetFace.ZPERSONFORFACE AS 'zDetFace-PersonForFace= zPerson-zPK',
        zDetFace.ZPERSONFORTEMPORALDETECTEDFACES AS 'zDetFace-Person for Temporal Detected Faces= zPerson-zPK',
        zDetFace.ZPERSONFORTORSO AS 'zDetFace-PersonForTorso= zPerson-zPK',
        zDetFace.ZPERSONBEINGKEYFACE AS 'zDetFace-Person Being Key Face',         
        zFaceCrop.ZPERSON AS 'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key',	
        zDetFace.ZFACEPRINT AS 'zDetFace-Face Print',	
        zDetFacePrint.Z_PK AS 'zDetFacePrint-zPK',		
        zDetFace.ZFACECROP AS 'zDetFace-Face Crop',
        zFaceCrop.Z_PK AS 'zFaceCrop-zPK',           
        zDetFaceGroup.ZKEYFACE AS 'zDetFaceGroup-KeyFace= zDetFace-zPK',
        zDetFaceGroup.ZASSOCIATEDPERSON AS 'zDetFaceGroup-AssocPerson= zPerson-zPK',
        zPerson.ZASSOCIATEDFACEGROUP AS 'zPerson-Assoc Face Group Key',
        zDetFace.ZFACEGROUPBEINGKEYFACE AS 'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK',
        zDetFace.ZFACEGROUP AS 'zDetFace-FaceGroup= zDetFaceGroup-zPK',		
        zDetFaceGroup.Z_PK AS 'zDetFaceGroup-zPK',
        zPerson.ZSHAREPARTICIPANT AS 'zPerson-Share Participant= zSharePartic-zPK',		
        zDetFace.ZUUID AS 'zDetFace-UUID',
        zFaceCrop.ZUUID AS 'zFaceCrop-UUID',	
        zFaceCrop.ZINVALIDMERGECANDIDATEPERSONUUID AS 'zFaceCrop-Invalid Merge Candidate Person UUID',		
        zPerson.ZPERSONUUID AS 'zPerson-Person UUID',
        zPerson.ZPERSONURI AS 'zPerson-Person URI',		
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFace.ZASSETFORFACE AS 'zDetFace-AssetForFace= zAsset-zPK',
        zDetFace.ZASSETFORTORSO AS 'zDetFace-AssetForTorso= zAsset-zPK',
        zFaceCrop.ZASSET AS 'zFaceCrop-Asset Key',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
            LEFT JOIN ZDETECTEDFACE zDetFace ON zAsset.Z_PK = zDetFace.ZASSETFORFACE
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSONFORFACE
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP
        WHERE zDetFace.Z_PK > 0  
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            personcontactmatchingdictionary = ''
            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            facecropresourcedata_blob = ''

            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            if row[27] is not None:
                pathto = os.path.join(report_folder, 'zPerson-ContactMatchingDict_' + row[133] + '.plist')
                with open(pathto, 'ab') as wf:
                    wf.write(row[27])

                with open(pathto, 'rb') as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        personcontactmatchingdictionary = deserialized_plist

                    except (KeyError, ValueError, TypeError) as ex:
                        if str(ex).find("does not contain an '$archiver' key") >= 0:
                            logfunc('plist was Not an NSKeyedArchive ' + row[133])
                        else:
                            logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[133])

            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            if row[34] is not None:
                pathto = os.path.join(report_folder, 'FaceCropFor_' + row[131] + '.jpg')
                with open(pathto, 'wb') as file:
                    file.write(row[34])
                facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                            row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                            row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26],
                            personcontactmatchingdictionary,
                            row[28], row[29], row[30], row[31], row[32], row[33],
                            facecropresourcedata_blob,
                            row[35], row[36],
                            row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                            row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                            row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                            row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                            row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                            row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                            row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                            row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                            row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
                            row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
                            row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
                            row[132], row[133], row[134], row[135], row[136], row[137], row[138], row[139],
                            row[140], row[141], row[142]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        'zAsset-Directory-Path-7',
                        'zAsset-Filename-8',
                        'zAddAssetAttr- Original Filename-9',
                        'zCldMast- Original Filename-10',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-11',
                        'zAsset- Conversation= zGenAlbum_zPK-12',
                        ('zAsset-Trashed Date-13', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-14',
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-15',
                        'zAddAssetAttr-Imported by Bundle ID-16',
                        'zAddAssetAttr-Imported By Display Name-17',
                        'zCldMast-Imported by Bundle ID-18',
                        'zCldMast-Imported by Display Name-19',
                        'zAsset-Visibility State-20',
                        'zFaceCrop-Face Area Points-21',
                        'zAsset-Face Adjustment Version-22',
                        'zAddAssetAttr-Face_Regions-SeeRawDBData-23',
                        'zAddAssetAttr-Face Analysis Version-24',
                        'zDetFace-Asset For Temporal Detected Faces= zAsset-zPK-25',
                        'zDetFacePrint-Data-SeeRawDBData-26',
                        'zPerson-Contact Matching Dictionary-27',
                        'zPerson-Verified Type-28',
                        'zPerson-Display Name-29',
                        'zPerson-Full Name-30',
                        'zPerson-Cloud Verified Type-31',
                        'zFaceCrop-State-32',
                        'zFaceCrop-Type-33',
                        'zFaceCrop-Resource Data-34',
                        'zDetFace-Confirmed Face Crop Generation State-35',
                        'zDetFace-Manual-36',
                        'zDetFace-Detection Type-37',
                        'zPerson-Detection Type-38',
                        'zDetFace-VIP Model Type-39',
                        'zDetFace-Name Source-40',
                        'zDetFace-Cloud Name Source-41',
                        'zPerson-Merge Candidate Confidence-42',
                        'zPerson-Type-43',
                        'zPerson-Gender Type-44',
                        'zDetFace-Gender Type-45',
                        'zDetFace-Center X-46',
                        'zDetFace-Center Y-47',
                        'zPerson-Age Type Estimate-48',
                        'zDetFace-Age Type Estimate-49',
                        'zDetFace-Ethnicity Type-50',
                        'zDetFace-Skin Tone Type-51',
                        'zDetFace-Hair Type-52',
                        'zDetFace-Hair Color Type-53',
                        'zDetFace-Head Gear Type-54',
                        'zDetFace-Facial Hair Type-55',
                        'zDetFace-Has Face Mask-56',
                        'zDetFace-Pose Type-57',
                        'zDetFace-Face Expression Type-58',
                        'zDetFace-Has Smile-59',
                        'zDetFace-Smile Type-60',
                        'zDetFace-Lip Makeup Type-61',
                        'zDetFace-Eyes State-62',
                        'zDetFace-Is Left Eye Closed-63',
                        'zDetFace-Is Right Eye Closed-64',
                        'zDetFace-Gaze Center X-65',
                        'zDetFace-Gaze Center Y-66',
                        'zDetFace-Face Gaze Type-67',
                        'zDetFace-Eye Glasses Type-68',
                        'zDetFace-Eye Makeup Type-69',
                        'zDetFace-Cluster Squence Number Key-70',
                        'zDetFace-Grouping ID-71',
                        'zDetFace-Master ID-72',
                        'zDetFace-Quality-73',
                        'zDetFace-Quality Measure-74',
                        'zDetFace-Source Height-75',
                        'zDetFace-Source Width-76',
                        'zDetFace-Asset Visible-77',
                        'zDetFace-Hidden/Asset Hidden-78',
                        'zDetFace-In Trash/Recently Deleted-79',
                        'zDetFace-Cloud Local State-80',
                        'zDetFace-Training Type-81',
                        'zDetFace.Pose Yaw-82',
                        'zDetFace-Body Center X-83',
                        'zDetFace-Body Center Y-84',
                        'zDetFace-Body Height-85',
                        'zDetFace-Body Width-86',
                        'zDetFace-Roll-87',
                        'zDetFace-Size-88',
                        'zDetFace-Cluster Sequence Number-89',
                        'zDetFace-Blur Score-90',
                        'zDetFacePrint-Face Print Version-91',
                        'zDetFaceGroup-UUID-92',
                        'zDetFaceGroup-Person Builder State-93',
                        'zDetFaceGroup-UnNamed Face Count-94',
                        'zPerson-Face Count-95',
                        'zDetFace-Face Algorithm Version-96',
                        'zDetFace-Adjustment Version-97',
                        'zPerson-In Person Naming Model-98',
                        'zPerson-Key Face Pick Source Key-99',
                        'zPerson-Manual Order Key-100',
                        'zPerson-Question Type-101',
                        'zPerson-Suggested For Client Type-102',
                        'zPerson-Merge Target Person-103',
                        'zPerson-Cloud Local State-104',
                        'zFaceCrop-Cloud Local State-105',
                        'zFaceCrop-Cloud Type-106',
                        'zPerson-Cloud Delete State-107',
                        'zFaceCrop-Cloud Delete State-108',
                        'zDetFace-zPK-109',
                        'zDetFacePrint-Face Key-110',
                        'zPerson-KeyFace=zDetFace-zPK-111',
                        'zFaceCrop-Face Key-112',
                        'zPerson-zPK=zDetFace-Person-113',
                        'zDetFace-PersonForFace= zPerson-zPK-114',
                        'zDetFace-Person for Temporal Detected Faces= zPerson-zPK-115',
                        'zDetFace-PersonForTorso= zPerson-zPK-116',
                        'zDetFace-Person Being Key Face-117',
                        'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-118',
                        'zDetFace-Face Print-119',
                        'zDetFacePrint-zPK-120',
                        'zDetFace-Face Crop-121',
                        'zFaceCrop-zPK-122',
                        'zDetFaceGroup-KeyFace= zDetFace-zPK-123',
                        'zDetFaceGroup-AssocPerson= zPerson-zPK-124',
                        'zPerson-Assoc Face Group Key-125',
                        'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-126',
                        'zDetFace-FaceGroup= zDetFaceGroup-zPK-127',
                        'zDetFaceGroup-zPK-128',
                        'zPerson-Share Participant= zSharePartic-zPK-129',
                        'zDetFace-UUID-130',
                        'zFaceCrop-UUID-131',
                        'zFaceCrop-Invalid Merge Candidate Person UUID-132',
                        'zPerson-Person UUID-133',
                        'zPerson-Person URI-134',
                        'zDetFaceGroup-UUID-135',
                        'zDetFace-AssetForFace= zAsset-zPK-136',
                        'zDetFace-AssetForTorso= zAsset-zPK-137',
                        'zFaceCrop-Asset Key-138',
                        'zAsset-zPK-139',
                        'zAddAssetAttr-zPK-140',
                        'zAsset-UUID = store.cloudphotodb-141',
                        'zAddAssetAttr-Master Fingerprint-142')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif version.parse(iosversion) >= version.parse("18"):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',  
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE
            WHEN zAsset.ZFACEAREAPOINTS > 0 THEN 'Face Area Points Detected in zAsset'
            ELSE 'Face Area Points Not Detected in zAsset'
        END AS 'zFaceCrop-Face Area Points',
        zAsset.ZFACEADJUSTMENTVERSION AS 'zAsset-Face Adjustment Version',
        CASE
            WHEN zAddAssetAttr.ZFACEREGIONS > 0 THEN 'zAddAssetAttr-Face_Regions_has_Data'
            ELSE 'zAddAssetAttr-Face_Regions_has_NO-Data'
        END AS 'zAddAssetAttr-Face_Regions-SeeRawDBData',
        CASE zAddAssetAttr.ZHASPEOPLESCENEMIDORGREATERCONFIDENCE
            WHEN 0 THEN '0-Obs in iOS 18 still testing-0'
            WHEN 1 THEN '1-Obs in iOS 18 still testing-1'	
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZHASPEOPLESCENEMIDORGREATERCONFIDENCE || ''
        END AS 'zAddAssetAttr-Has_People_Scene Mid_Or_Greater_Confidence',
        zAddAssetAttr.ZFACEANALYSISVERSION AS 'zAddAssetAttr-Face Analysis Version',
        zDetFace.ZASSETFORTEMPORALDETECTEDFACES AS 'zDetFace-Asset For Temporal Detected Faces= zAsset-zPK',
        CASE
            WHEN zDetFacePrint.ZDATA > 0 THEN 'zDetFacePrint-Data_has_Data'
            ELSE 'zDetFacePrint-Data_NO-Data'
        END AS 'zDetFacePrint-Data-SeeRawDBData',
        zPerson.ZCONTACTMATCHINGDICTIONARY AS 'zPerson-Contact Matching Dictionary',
        CASE zPerson.ZVERIFIEDTYPE
            WHEN 0 THEN '0-Not-Verified'
            WHEN 1 THEN '1-Has_Contact Matching_Dictionary'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZVERIFIEDTYPE || ''
        END AS 'zPerson-Verified Type',
        zPerson.ZISMECONFIDENCE AS 'zPerson-Is_Me_Confidence',
        zPerson.ZDISPLAYNAME AS 'zPerson-Display Name',
        zPerson.ZFULLNAME AS 'zPerson-Full Name',
        CASE zPerson.ZCLOUDVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDVERIFIEDTYPE || ''
        END AS 'zPerson-Cloud Verified Type',
        CASE zFaceCrop.ZSTATE
            WHEN 5 THEN 'Validated-5'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZSTATE || ''
        END AS 'zFaceCrop-State',
        CASE zFaceCrop.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-Active'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZTYPE || ''
        END AS 'zFaceCrop-Type',
        zFaceCrop.ZRESOURCEDATA AS 'zFaceCrop-Resource Data',	
        CASE zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE || ''
        END AS 'zDetFace-Confirmed Face Crop Generation State',
        CASE zDetFace.ZMANUAL
            WHEN 0 THEN 'zDetFace-Auto Detected-0'
            WHEN 1 THEN 'zDetFace-Manually Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZMANUAL || ''
        END AS 'zDetFace-Manual',
        CASE zDetFace.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZDETECTIONTYPE || ''
        END AS 'zDetFace-Detection Type',
        CASE zPerson.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZDETECTIONTYPE || ''
        END AS 'zPerson-Detection Type',
        CASE zDetFace.ZVIPMODELTYPE
            WHEN 0 THEN 'Not VIP-0'
            WHEN 1 THEN 'VIP-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZVIPMODELTYPE || ''
        END AS 'zDetFace-VIP Model Type',
        CASE zDetFace.ZNAMESOURCE
            WHEN 0 THEN 'No Name Listed-0'
            WHEN 1 THEN '1-Face Crop-1'
            WHEN 2 THEN '2-Verified/Has-Person-URI'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZNAMESOURCE || ''
        END AS 'zDetFace-Name Source',
        CASE zDetFace.ZCLOUDNAMESOURCE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN '1-User Added Via Face Crop-1'
            WHEN 5 THEN '5-Asset Shared has Name'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDNAMESOURCE || ''
        END AS 'zDetFace-Cloud Name Source',
        zPerson.ZMERGECANDIDATECONFIDENCE AS 'zPerson-Merge Candidate Confidence',
        CASE zPerson.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZTYPE || ''
        END AS 'zPerson-Type',
        CASE zPerson.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZGENDERTYPE || ''
        END AS 'zPerson-Gender Type',
        CASE zDetFace.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGENDERTYPE || ''
        END AS 'zDetFace-Gender Type',
        zDetFace.ZCENTERX AS 'zDetFace-Center X',
        zDetFace.ZCENTERY AS 'zDetFace-Center Y',
        CASE zPerson.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZAGETYPE || ''
        END AS 'zPerson-Age Type Estimate',
        CASE zDetFace.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZAGETYPE || ''
        END AS 'zDetFace-Age Type Estimate',
        CASE zDetFace.ZETHNICITYTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/African American-1'
            WHEN 2 THEN 'White-2'
            WHEN 3 THEN 'Hispanic/Latino-3'
            WHEN 4 THEN 'Asian-4'
            WHEN 5 THEN 'Native Hawaiian/Other Pacific Islander-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZETHNICITYTYPE || ''
        END AS 'zDetFace-Ethnicity Type',
        CASE zDetFace.ZSKINTONETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Light-Pale White Skin Tone-1'
            WHEN 2 THEN 'White-Fair Skin Tone-2'
            WHEN 3 THEN 'Medium-White to Olive Skin Tone-3'
            WHEN 4 THEN 'Olive-Moderate Brown Skin Tone-4'
            WHEN 5 THEN 'Brown-Dark Brown Skin Tone-5'
            WHEN 6 THEN 'Black-Very Dark Brown to Black Skin Tone-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSKINTONETYPE || ''
        END AS 'zDetFace-Skin Tone Type',
        CASE zDetFace.ZHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            WHEN 6 THEN '6-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRTYPE || ''
        END AS 'zDetFace-Hair Type',
        CASE zDetFace.ZHAIRCOLORTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/Brown Hair Color-1'
            WHEN 2 THEN 'Brown/Blonde Hair Color-2'
            WHEN 3 THEN 'Brown/Red Hair Color-3'
            WHEN 4 THEN 'Red/White Hair Color-4'
            WHEN 5 THEN 'StillTesting/Artifical-5'
            WHEN 6 THEN 'White/Bald Hair Color-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRCOLORTYPE || ''
        END AS 'zDetFace-Hair Color Type',
        CASE zDetFace.ZHEADGEARTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-No Headgear'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHEADGEARTYPE || ''
        END AS 'zDetFace-Head Gear Type',
        CASE zDetFace.ZFACIALHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Clean Shaven Facial Hair Type-1'
            WHEN 2 THEN 'Beard Facial Hair Type-2'
            WHEN 3 THEN 'Goatee Facial Hair Type-3'
            WHEN 4 THEN 'Mustache Facial Hair Type-4'
            WHEN 5 THEN 'Stubble Facial Hair Type-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACIALHAIRTYPE || ''
        END AS 'zDetFace-Facial Hair Type',
        CASE zDetFace.ZHASFACEMASK
            WHEN 0 THEN 'No Mask-0'
            WHEN 1 THEN 'Has Mask-1'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASFACEMASK || ''
        END AS 'zDetFace-Has Face Mask',
        CASE zDetFace.ZPOSETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Face Frontal Pose-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN 'Face Profile Pose-3'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZPOSETYPE || ''
        END AS 'zDetFace-Pose Type',
        CASE zDetFace.ZFACEEXPRESSIONTYPE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN 'Disgusted/Angry-1'
            WHEN 2 THEN 'Suprised/Fearful-2'
            WHEN 3 THEN 'Neutral-3'
            WHEN 4 THEN 'Confident/Smirk-4'
            WHEN 5 THEN 'Happiness-5'
            WHEN 6 THEN 'Sadness-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACEEXPRESSIONTYPE || ''
        END AS 'zDetFace-Face Expression Type',
        CASE zDetFace.ZHASSMILE
            WHEN 0 THEN 'zDetFace No Smile-0'
            WHEN 1 THEN 'zDetFace Smile-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASSMILE || ''
        END AS 'zDetFace-Has Smile',
        CASE zDetFace.ZSMILETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'zDetFace Smile No Teeth-1'
            WHEN 2 THEN 'zDetFace Smile has Teeth-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSMILETYPE || ''
        END AS 'zDetFace-Smile Type',
        CASE zDetFace.ZLIPMAKEUPTYPE
            WHEN 0 THEN 'zDetFace No Lip Makeup-0'
            WHEN 1 THEN 'zDetFace Lip Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZLIPMAKEUPTYPE || ''
        END AS 'zDetFace-Lip Makeup Type',
        CASE zDetFace.ZEYESSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eyes Closed-1'
            WHEN 2 THEN 'Eyes Open-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYESSTATE || ''
        END AS 'zDetFace-Eyes State',
        CASE zDetFace.ZISLEFTEYECLOSED
            WHEN 0 THEN 'Left Eye Open-0'
            WHEN 1 THEN 'Left Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISLEFTEYECLOSED || ''
        END AS 'zDetFace-Is Left Eye Closed',
        CASE zDetFace.ZISRIGHTEYECLOSED
            WHEN 0 THEN 'Right Eye Open-0'
            WHEN 1 THEN 'Right Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISRIGHTEYECLOSED || ''
        END AS 'zDetFace-Is Right Eye Closed',
        zDetFace.ZGAZECENTERX AS 'zDetFace-Gaze Center X',
        zDetFace.ZGAZECENTERY AS 'zDetFace-Gaze Center Y',
        CASE zDetFace.ZGAZETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGAZETYPE || ''
        END AS 'zDetFace-Face Gaze Type',
        CASE zDetFace.ZGLASSESTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eye Glasses-1'
            WHEN 2 THEN 'Sun Glasses-2'
            WHEN 3 THEN 'No Glasses-3'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGLASSESTYPE || ''
        END AS 'zDetFace-Eye Glasses Type',
        CASE zDetFace.ZEYEMAKEUPTYPE
            WHEN 0 THEN 'No Eye Makeup-0'
            WHEN 1 THEN 'Eye Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYEMAKEUPTYPE || ''
        END AS 'zDetFace-Eye Makeup Type',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number Key',
        zDetFace.ZGROUPINGIDENTIFIER AS 'zDetFace-Grouping ID',
        zDetFace.ZMASTERIDENTIFIER AS 'zDetFace-Master ID',
        zDetFace.ZQUALITY AS 'zDetFace-Quality',
        zDetFace.ZQUALITYMEASURE AS 'zDetFace-Quality Measure',
        zDetFace.ZSOURCEHEIGHT AS 'zDetFace-Source Height',
        zDetFace.ZSOURCEWIDTH AS 'zDetFace-Source Width',
        CASE zDetFace.ZASSETVISIBLE
            WHEN 0 THEN '0-Unknown-StillTesitng-0'
            WHEN 1 THEN '1-Unknown-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZASSETVISIBLE || ''
        END AS 'zDetFace-Asset Visible',
        CASE zDetFace.ZHIDDEN
            WHEN 0 THEN 'Not Hidden-0'
            WHEN 1 THEN 'Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHIDDEN || ''
        END AS 'zDetFace-Hidden/Asset Hidden',
        CASE zDetFace.ZISINTRASH
            WHEN 0 THEN 'Not In Trash-0'
            WHEN 1 THEN 'In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISINTRASH || ''
        END AS 'zDetFace-In Trash/Recently Deleted',
        CASE zDetFace.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDLOCALSTATE || ''
        END AS 'zDetFace-Cloud Local State',
        CASE zDetFace.ZTRAININGTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZTRAININGTYPE
        END AS 'zDetFace-Training Type',
        zDetFace.ZPOSEYAW AS 'zDetFace.Pose Yaw',
        zDetFace.ZBODYCENTERX AS 'zDetFace-Body Center X',
        zDetFace.ZBODYCENTERY AS 'zDetFace-Body Center Y',
        zDetFace.ZBODYHEIGHT AS 'zDetFace-Body Height',
        zDetFace.ZBODYWIDTH AS 'zDetFace-Body Width',
        zDetFace.ZROLL AS 'zDetFace-Roll',
        zDetFace.ZSIZE AS 'zDetFace-Size',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Sequence Number',
        zDetFace.ZBLURSCORE AS 'zDetFace-Blur Score',
        zDetFacePrint.ZFACEPRINTVERSION AS 'zDetFacePrint-Face Print Version',
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFaceGroup.ZPERSONBUILDERSTATE AS 'zDetFaceGroup-Person Builder State',
        zDetFaceGroup.ZUNNAMEDFACECOUNT AS 'zDetFaceGroup-UnNamed Face Count',
        zPerson.ZFACECOUNT AS 'zPerson-Face Count',       
        zDetFace.ZFACEALGORITHMVERSION AS 'zDetFace-Face Algorithm Version',
        zDetFace.ZADJUSTMENTVERSION AS 'zDetFace-Adjustment Version',       
        zPerson.ZINPERSONNAMINGMODEL AS 'zPerson-In Person Naming Model',
        zPerson.ZKEYFACEPICKSOURCE AS 'zPerson-Key Face Pick Source Key',
        zPerson.ZMANUALORDER AS 'zPerson-Manual Order Key',
        zPerson.ZQUESTIONTYPE AS 'zPerson-Question Type',
        zPerson.ZSUGGESTEDFORCLIENTTYPE AS 'zPerson-Suggested For Client Type',
        zPerson.ZMERGETARGETPERSON AS 'zPerson-Merge Target Person',
        CASE zPerson.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Person Not Synced with Cloud-0'
            WHEN 1 THEN 'Person Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDLOCALSTATE
        END AS 'zPerson-Cloud Local State',
        CASE zFaceCrop.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDLOCALSTATE || ''
        END AS 'zFaceCrop-Cloud Local State',
        CASE zFaceCrop.ZCLOUDTYPE
            WHEN 0 THEN 'Has Name-0'
            WHEN 5 THEN 'Has Face Key-5'
            WHEN 12 THEN '12-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDTYPE || ''
        END AS 'zFaceCrop-Cloud Type',
        CASE zPerson.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDDELETESTATE || ''
        END AS 'zPerson-Cloud Delete State',
        CASE zFaceCrop.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDDELETESTATE || ''
        END AS 'zFaceCrop-Cloud Delete State',
        zDetFace.Z_PK AS 'zDetFace-zPK',
        zDetFacePrint.ZFACE AS 'zDetFacePrint-Face Key',
        zPerson.ZKEYFACE AS 'zPerson-KeyFace=zDetFace-zPK',
        zFaceCrop.ZFACE AS 'zFaceCrop-Face Key',
        zPerson.Z_PK AS 'zPerson-zPK=zDetFace-Person',
        zDetFace.ZPERSONFORFACE AS 'zDetFace-PersonForFace= zPerson-zPK',
        zDetFace.ZPERSONFORTEMPORALDETECTEDFACES AS 'zDetFace-Person for Temporal Detected Faces= zPerson-zPK',
        zDetFace.ZPERSONFORTORSO AS 'zDetFace-PersonForTorso= zPerson-zPK',
        zDetFace.ZPERSONBEINGKEYFACE AS 'zDetFace-Person Being Key Face',         
        zFaceCrop.ZPERSON AS 'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key',	
        zDetFace.ZFACEPRINT AS 'zDetFace-Face Print',	
        zDetFacePrint.Z_PK AS 'zDetFacePrint-zPK',		
        zDetFace.ZFACECROP AS 'zDetFace-Face Crop',
        zFaceCrop.Z_PK AS 'zFaceCrop-zPK',           
        zDetFaceGroup.ZKEYFACE AS 'zDetFaceGroup-KeyFace= zDetFace-zPK',
        zDetFaceGroup.ZASSOCIATEDPERSON AS 'zDetFaceGroup-AssocPerson= zPerson-zPK',
        zPerson.ZASSOCIATEDFACEGROUP AS 'zPerson-Assoc Face Group Key',
        zDetFace.ZFACEGROUPBEINGKEYFACE AS 'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK',
        zDetFace.ZFACEGROUP AS 'zDetFace-FaceGroup= zDetFaceGroup-zPK',		
        zDetFaceGroup.Z_PK AS 'zDetFaceGroup-zPK',
        zPerson.ZSHAREPARTICIPANT AS 'zPerson-Share Participant= zSharePartic-zPK',		
        zDetFace.ZUUID AS 'zDetFace-UUID',
        zFaceCrop.ZUUID AS 'zFaceCrop-UUID',	
        zFaceCrop.ZINVALIDMERGECANDIDATEPERSONUUID AS 'zFaceCrop-Invalid Merge Candidate Person UUID',		
        zPerson.ZPERSONUUID AS 'zPerson-Person UUID',
        zPerson.ZPERSONURI AS 'zPerson-Person URI',		
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFace.ZASSETFORFACE AS 'zDetFace-AssetForFace= zAsset-zPK',
        zDetFace.ZASSETFORTORSO AS 'zDetFace-AssetForTorso= zAsset-zPK',
        zFaceCrop.ZASSET AS 'zFaceCrop-Asset Key',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
            LEFT JOIN ZDETECTEDFACE zDetFace ON zAsset.Z_PK = zDetFace.ZASSETFORFACE
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSONFORFACE
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP
        WHERE zDetFace.Z_PK > 0  
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            personcontactmatchingdictionary = ''
            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            facecropresourcedata_blob = ''

            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            if row[28] is not None:
                pathto = os.path.join(report_folder, 'zPerson-ContactMatchingDict_' + row[135] + '.plist')
                with open(pathto, 'ab') as wf:
                    wf.write(row[28])

                with open(pathto, 'rb') as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        personcontactmatchingdictionary = deserialized_plist

                    except (KeyError, ValueError, TypeError) as ex:
                        if str(ex).find("does not contain an '$archiver' key") >= 0:
                            logfunc('plist was Not an NSKeyedArchive ' + row[135])
                        else:
                            logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[135])

            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            if row[36] is not None:
                pathto = os.path.join(report_folder, 'FaceCropFor_' + row[133] + '.jpg')
                with open(pathto, 'wb') as file:
                    file.write(row[36])
                facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                            row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                            row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                            personcontactmatchingdictionary,
                            row[29], row[30], row[31], row[32], row[33], row[34], row[35],
                            facecropresourcedata_blob,
                            row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                            row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                            row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                            row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                            row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                            row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                            row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                            row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                            row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
                            row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
                            row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
                            row[132], row[133], row[134], row[135], row[136], row[137], row[138], row[139],
                            row[140], row[141], row[142], row[143], row[144], row[145]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        'zAsset-Directory-Path-7',
                        'zAsset-Filename-8',
                        'zAddAssetAttr- Original Filename-9',
                        'zCldMast- Original Filename-10',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-11',
                        'zAsset- Conversation= zGenAlbum_zPK-12',
                        ('zAsset-Trashed Date-13', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-14',
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-15',
                        'zAddAssetAttr-Imported by Bundle ID-16',
                        'zAddAssetAttr-Imported By Display Name-17',
                        'zCldMast-Imported by Bundle ID-18',
                        'zCldMast-Imported by Display Name-19',
                        'zAsset-Visibility State-20',
                        'zFaceCrop-Face Area Points-21',
                        'zAddAssetAttr-Has_People_Scene Mid_Or_Greater_Confidence-22',
                        'zAsset-Face Adjustment Version-23',
                        'zAddAssetAttr-Face_Regions-SeeRawDBData-24',
                        'zAddAssetAttr-Face Analysis Version-25',
                        'zDetFace-Asset For Temporal Detected Faces= zAsset-zPK-26',
                        'zDetFacePrint-Data-SeeRawDBData-27',
                        'zPerson-Contact Matching Dictionary-28',
                        'zPerson-Verified Type-29',
                        'zPerson-Is_Me_Confidence-30',
                        'zPerson-Display Name-31',
                        'zPerson-Full Name-32',
                        'zPerson-Cloud Verified Type-33',
                        'zFaceCrop-State-34',
                        'zFaceCrop-Type-35',
                        'zFaceCrop-Resource Data-36',
                        'zDetFace-Confirmed Face Crop Generation State-37',
                        'zDetFace-Manual-38',
                        'zDetFace-Detection Type-39',
                        'zPerson-Detection Type-40',
                        'zDetFace-VIP Model Type-41',
                        'zDetFace-Name Source-42',
                        'zDetFace-Cloud Name Source-43',
                        'zPerson-Merge Candidate Confidence-44',
                        'zPerson-Type-45',
                        'zPerson-Gender Type-46',
                        'zDetFace-Gender Type-47',
                        'zDetFace-Center X-48',
                        'zDetFace-Center Y-49',
                        'zPerson-Age Type Estimate-50',
                        'zDetFace-Age Type Estimate-51',
                        'zDetFace-Ethnicity Type-52',
                        'zDetFace-Skin Tone Type-53',
                        'zDetFace-Hair Type-54',
                        'zDetFace-Hair Color Type-55',
                        'zDetFace-Head Gear Type-56',
                        'zDetFace-Facial Hair Type-57',
                        'zDetFace-Has Face Mask-58',
                        'zDetFace-Pose Type-59',
                        'zDetFace-Face Expression Type-60',
                        'zDetFace-Has Smile-61',
                        'zDetFace-Smile Type-62',
                        'zDetFace-Lip Makeup Type-63',
                        'zDetFace-Eyes State-64',
                        'zDetFace-Is Left Eye Closed-65',
                        'zDetFace-Is Right Eye Closed-66',
                        'zDetFace-Gaze Center X-67',
                        'zDetFace-Gaze Center Y-68',
                        'zDetFace-Face Gaze Type-69',
                        'zDetFace-Eye Glasses Type-70',
                        'zDetFace-Eye Makeup Type-71',
                        'zDetFace-Cluster Squence Number Key-72',
                        'zDetFace-Grouping ID-73',
                        'zDetFace-Master ID-74',
                        'zDetFace-Quality-75',
                        'zDetFace-Quality Measure-76',
                        'zDetFace-Source Height-77',
                        'zDetFace-Source Width-78',
                        'zDetFace-Asset Visible-79',
                        'zDetFace-Hidden/Asset Hidden-80',
                        'zDetFace-In Trash/Recently Deleted-81',
                        'zDetFace-Cloud Local State-82',
                        'zDetFace-Training Type-83',
                        'zDetFace.Pose Yaw-84',
                        'zDetFace-Body Center X-85',
                        'zDetFace-Body Center Y-86',
                        'zDetFace-Body Height-87',
                        'zDetFace-Body Width-88',
                        'zDetFace-Roll-89',
                        'zDetFace-Size-90',
                        'zDetFace-Cluster Sequence Number-91',
                        'zDetFace-Blur Score-92',
                        'zDetFacePrint-Face Print Version-93',
                        'zDetFaceGroup-UUID-94',
                        'zDetFaceGroup-Person Builder State-95',
                        'zDetFaceGroup-UnNamed Face Count-96',
                        'zPerson-Face Count-97',
                        'zDetFace-Face Algorithm Version-98',
                        'zDetFace-Adjustment Version-99',
                        'zPerson-In Person Naming Model-100',
                        'zPerson-Key Face Pick Source Key-101',
                        'zPerson-Manual Order Key-102',
                        'zPerson-Question Type-103',
                        'zPerson-Suggested For Client Type-104',
                        'zPerson-Merge Target Person-105',
                        'zPerson-Cloud Local State-106',
                        'zFaceCrop-Cloud Local State-107',
                        'zFaceCrop-Cloud Type-108',
                        'zPerson-Cloud Delete State-109',
                        'zFaceCrop-Cloud Delete State-110',
                        'zDetFace-zPK-111',
                        'zDetFacePrint-Face Key-112',
                        'zPerson-KeyFace=zDetFace-zPK-113',
                        'zFaceCrop-Face Key-114',
                        'zPerson-zPK=zDetFace-Person-115',
                        'zDetFace-PersonForFace= zPerson-zPK-116',
                        'zDetFace-Person for Temporal Detected Faces= zPerson-zPK-117',
                        'zDetFace-PersonForTorso= zPerson-zPK-118',
                        'zDetFace-Person Being Key Face-119',
                        'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-120',
                        'zDetFace-Face Print-121',
                        'zDetFacePrint-zPK-122',
                        'zDetFace-Face Crop-123',
                        'zFaceCrop-zPK-124',
                        'zDetFaceGroup-KeyFace= zDetFace-zPK-125',
                        'zDetFaceGroup-AssocPerson= zPerson-zPK-126',
                        'zPerson-Assoc Face Group Key-127',
                        'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-128',
                        'zDetFace-FaceGroup= zDetFaceGroup-zPK-129',
                        'zDetFaceGroup-zPK-130',
                        'zPerson-Share Participant= zSharePartic-zPK-131',
                        'zDetFace-UUID-132',
                        'zFaceCrop-UUID-133',
                        'zFaceCrop-Invalid Merge Candidate Person UUID-134',
                        'zPerson-Person UUID-135',
                        'zPerson-Person URI-136',
                        'zDetFaceGroup-UUID-137',
                        'zDetFace-AssetForFace= zAsset-zPK-138',
                        'zDetFace-AssetForTorso= zAsset-zPK-139',
                        'zFaceCrop-Asset Key-140',
                        'zAsset-zPK-141',
                        'zAddAssetAttr-zPK-142',
                        'zAsset-UUID = store.cloudphotodb-143',
                        'zAddAssetAttr-Original Stable Hash-144',
                        'zAddAssetAttr.Adjusted Stable Hash-145')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

@artifact_processor
def Ph16_2PeopleFacesAssetDataSyndPL(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for source_path in files_found:
        source_path = str(source_path)

        if source_path.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("13.7"):
        logfunc("Unsupported version for Syndication.photoslibrary iOS " + iosversion)
        return (), [], source_path
    if (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("15")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',  
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',    
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr-Creator Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',        
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE
            WHEN zAsset.ZFACEAREAPOINTS > 0 THEN 'Face Area Points Detected in zAsset'
            ELSE 'Face Area Points Not Detected in zAsset'
        END AS 'zFaceCrop-Face Area Points',
        zAsset.ZFACEADJUSTMENTVERSION AS 'zAsset-Face Adjustment Version',
        CASE
            WHEN zAddAssetAttr.ZFACEREGIONS > 0 THEN 'zAddAssetAttr-Face_Regions_has_Data'
            ELSE 'zAddAssetAttr-Face_Regions_has_NO-Data'
        END AS 'zAddAssetAttr-Face_Regions-SeeRawDBData',
        CASE
            WHEN zDetFacePrint.ZDATA > 0 THEN 'zDetFacePrint-Data_has_Data'
            ELSE 'zDetFacePrint-Data_NO-Data'
        END AS 'zDetFacePrint-Data-SeeRawDBData',
        zPerson.ZCONTACTMATCHINGDICTIONARY AS 'zPerson-Contact Matching Dictionary',
        CASE zPerson.ZVERIFIEDTYPE
            WHEN 0 THEN '0-Not-Verified'
            WHEN 1 THEN '1-Has_Contact Matching_Dictionary'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZVERIFIEDTYPE || ''
        END AS 'zPerson-Verified Type',
        zPerson.ZDISPLAYNAME AS 'zPerson-Display Name',
        zPerson.ZFULLNAME AS 'zPerson-Full Name',
        CASE zPerson.ZCLOUDVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDVERIFIEDTYPE || ''
        END AS 'zPerson-Cloud Verified Type',
        CASE zFaceCrop.ZSTATE
            WHEN 5 THEN 'Validated-5'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZSTATE || ''
        END AS 'zFaceCrop-State',
        CASE zFaceCrop.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-Active'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZTYPE || ''
        END AS 'zFaceCrop-Type',
        zFaceCrop.ZRESOURCEDATA AS 'zFaceCrop-Resource Data',	
        CASE zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE || ''
        END AS 'zDetFace-Confirmed Face Crop Generation State',
        CASE zDetFace.ZMANUAL
            WHEN 0 THEN 'zDetFace-Auto Detected-0'
            WHEN 1 THEN 'zDetFace-Manually Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZMANUAL || ''
        END AS 'zDetFace-Manual',
        CASE zDetFace.ZVIPMODELTYPE
            WHEN 0 THEN 'Not VIP-0'
            WHEN 1 THEN 'VIP-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZVIPMODELTYPE || ''
        END AS 'zDetFace-VIP Model Type',
        CASE zDetFace.ZNAMESOURCE
            WHEN 0 THEN 'No Name Listed-0'
            WHEN 1 THEN '1-Face Crop-1'
            WHEN 2 THEN '2-Verified/Has-Person-URI'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZNAMESOURCE || ''
        END AS 'zDetFace-Name Source',
        CASE zDetFace.ZCLOUDNAMESOURCE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN '1-User Added Via Face Crop-1'
            WHEN 5 THEN '5-Asset Shared has Name'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDNAMESOURCE || ''
        END AS 'zDetFace-Cloud Name Source',
        CASE zPerson.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZTYPE || ''
        END AS 'zPerson-Type',
        CASE zPerson.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZGENDERTYPE || ''
        END AS 'zPerson-Gender Type',
        CASE zDetFace.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGENDERTYPE || ''
        END AS 'zDetFace-Gender Type',
        zDetFace.ZCENTERX AS 'zDetFace-Center X',
        zDetFace.ZCENTERY AS 'zDetFace-Center Y',
        CASE zPerson.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZAGETYPE || ''
        END AS 'zPerson-Age Type Estimate',
        CASE zDetFace.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZAGETYPE || ''
        END AS 'zDetFace-Age Type Estimate',
        CASE zDetFace.ZHAIRCOLORTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/Brown Hair Color-1'
            WHEN 2 THEN 'Brown/Blonde Hair Color-2'
            WHEN 3 THEN 'Brown/Red Hair Color-3'
            WHEN 4 THEN 'Red/White Hair Color-4'
            WHEN 5 THEN 'StillTesting/Artifical-5'
            WHEN 6 THEN 'White/Bald Hair Color-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRCOLORTYPE || ''
        END AS 'zDetFace-Hair Color Type',
        CASE zDetFace.ZFACIALHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Clean Shaven Facial Hair Type-1'
            WHEN 2 THEN 'Beard Facial Hair Type-2'
            WHEN 3 THEN 'Goatee Facial Hair Type-3'
            WHEN 4 THEN 'Mustache Facial Hair Type-4'
            WHEN 5 THEN 'Stubble Facial Hair Type-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACIALHAIRTYPE || ''
        END AS 'zDetFace-Facial Hair Type',
        CASE zDetFace.ZHASSMILE
            WHEN 0 THEN 'zDetFace No Smile-0'
            WHEN 1 THEN 'zDetFace Smile-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASSMILE || ''
        END AS 'zDetFace-Has Smile',
        CASE zDetFace.ZSMILETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'zDetFace Smile No Teeth-1'
            WHEN 2 THEN 'zDetFace Smile has Teeth-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSMILETYPE || ''
        END AS 'zDetFace-Smile Type',
        CASE zDetFace.ZLIPMAKEUPTYPE
            WHEN 0 THEN 'zDetFace No Lip Makeup-0'
            WHEN 1 THEN 'zDetFace Lip Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZLIPMAKEUPTYPE || ''
        END AS 'zDetFace-Lip Makeup Type',
        CASE zDetFace.ZEYESSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eyes Closed-1'
            WHEN 2 THEN 'Eyes Open-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYESSTATE || ''
        END AS 'zDetFace-Eyes State',
        CASE zDetFace.ZISLEFTEYECLOSED
            WHEN 0 THEN 'Left Eye Open-0'
            WHEN 1 THEN 'Left Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISLEFTEYECLOSED || ''
        END AS 'zDetFace-Is Left Eye Closed',
        CASE zDetFace.ZISRIGHTEYECLOSED
            WHEN 0 THEN 'Right Eye Open-0'
            WHEN 1 THEN 'Right Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISRIGHTEYECLOSED || ''
        END AS 'zDetFace-Is Right Eye Closed',
        CASE zDetFace.ZGLASSESTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eye Glasses-1'
            WHEN 2 THEN 'Sun Glasses-2'
            WHEN 3 THEN 'No Glasses-3'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGLASSESTYPE || ''
        END AS 'zDetFace-Eye Glasses Type',
        CASE zDetFace.ZEYEMAKEUPTYPE
            WHEN 0 THEN 'No Eye Makeup-0'
            WHEN 1 THEN 'Eye Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYEMAKEUPTYPE || ''
        END AS 'zDetFace-Eye Makeup Type',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number Key',
        zDetFace.ZGROUPINGIDENTIFIER AS 'zDetFace-Grouping ID',
        zDetFace.ZMASTERIDENTIFIER AS 'zDetFace-Master ID',
        zDetFace.ZQUALITY AS 'zDetFace-Quality',
        zDetFace.ZQUALITYMEASURE AS 'zDetFace-Quality Measure',
        zDetFace.ZSOURCEHEIGHT AS 'zDetFace-Source Height',
        zDetFace.ZSOURCEWIDTH AS 'zDetFace-Source Width',
        CASE zDetFace.ZASSETVISIBLE
            WHEN 0 THEN '0-Unknown-StillTesitng-0'
            WHEN 1 THEN '1-Unknown-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZASSETVISIBLE || ''
        END AS 'zDetFace-Asset Visible',
        CASE zDetFace.ZHIDDEN
            WHEN 0 THEN 'Not Hidden-0'
            WHEN 1 THEN 'Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHIDDEN || ''
        END AS 'zDetFace-Hidden/Asset Hidden',
        CASE zDetFace.ZISINTRASH
            WHEN 0 THEN 'Not In Trash-0'
            WHEN 1 THEN 'In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISINTRASH || ''
        END AS 'zDetFace-In Trash/Recently Deleted',
        CASE zDetFace.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDLOCALSTATE || ''
        END AS 'zDetFace-Cloud Local State',
        CASE zDetFace.ZTRAININGTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZTRAININGTYPE
        END AS 'zDetFace-Training Type',
        zDetFace.ZPOSEYAW AS 'zDetFace.Pose Yaw',
        zDetFace.ZROLL AS 'zDetFace-Roll',
        zDetFace.ZSIZE AS 'zDetFace-Size',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number',
        zDetFace.ZBLURSCORE AS 'zDetFace-Blur Score',
        zDetFacePrint.ZFACEPRINTVERSION AS 'zDetFacePrint-Face Print Version',
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFaceGroup.ZPERSONBUILDERSTATE AS 'zDetFaceGroup-Person Builder State',
        zDetFaceGroup.ZUNNAMEDFACECOUNT AS 'zDetFaceGroup-UnNamed Face Count',
        zPerson.ZFACECOUNT AS 'zPerson-Face Count',       
        zDetFace.ZFACEALGORITHMVERSION AS 'zDetFace-Face Algorithm Version',
        zDetFace.ZADJUSTMENTVERSION AS 'zDetFace-Adjustment Version',       
        zPerson.ZINPERSONNAMINGMODEL AS 'zPerson-In Person Naming Model',
        zPerson.ZKEYFACEPICKSOURCE AS 'zPerson-Key Face Pick Source Key',
        zPerson.ZMANUALORDER AS 'zPerson-Manual Order Key',
        zPerson.ZQUESTIONTYPE AS 'zPerson-Question Type',
        zPerson.ZSUGGESTEDFORCLIENTTYPE AS 'zPerson-Suggested For Client Type',
        zPerson.ZMERGETARGETPERSON AS 'zPerson-Merge Target Person',
        CASE zPerson.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Person Not Synced with Cloud-0'
            WHEN 1 THEN 'Person Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDLOCALSTATE
        END AS 'zPerson-Cloud Local State',
        CASE zFaceCrop.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDLOCALSTATE || ''
        END AS 'zFaceCrop-Cloud Local State',
        CASE zFaceCrop.ZCLOUDTYPE
            WHEN 0 THEN 'Has Name-0'
            WHEN 5 THEN 'Has Face Key-5'
            WHEN 12 THEN '12-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDTYPE || ''
        END AS 'zFaceCrop-Cloud Type',
        CASE zPerson.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDDELETESTATE || ''
        END AS 'zPerson-Cloud Delete State',
        CASE zFaceCrop.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDDELETESTATE || ''
        END AS 'zFaceCrop-Cloud Delete State',
        zDetFace.Z_PK AS 'zDetFace-zPK',
        zDetFacePrint.ZFACE AS 'zDetFacePrint-Face Key',
        zPerson.ZKEYFACE AS 'zPerson-KeyFace=zDetFace-zPK',
        zFaceCrop.ZFACE AS 'zFaceCrop-Face Key',
        zPerson.Z_PK AS 'zPerson-zPK=zDetFace-Person',
        zDetFace.ZPERSON AS 'zDetFace-PersonForFace= zPerson-zPK',
        zDetFace.ZPERSONBEINGKEYFACE AS 'zDetFace-Person Being Key Face',         
        zFaceCrop.ZPERSON AS 'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key',	
        zDetFace.ZFACEPRINT AS 'zDetFace-Face Print',	
        zDetFacePrint.Z_PK AS 'zDetFacePrint-zPK',		
        zDetFace.ZFACECROP AS 'zDetFace-Face Crop',
        zFaceCrop.Z_PK AS 'zFaceCrop-zPK',           
        zDetFaceGroup.ZKEYFACE AS 'zDetFaceGroup-KeyFace= zDetFace-zPK',
        zDetFaceGroup.ZASSOCIATEDPERSON AS 'zDetFaceGroup-AssocPerson= zPerson-zPK',
        zPerson.ZASSOCIATEDFACEGROUP AS 'zPerson-Assoc Face Group Key',
        zDetFace.ZFACEGROUPBEINGKEYFACE AS 'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK',
        zDetFace.ZFACEGROUP AS 'zDetFace-FaceGroup= zDetFaceGroup-zPK',		
        zDetFaceGroup.Z_PK AS 'zDetFaceGroup-zPK',
        zDetFace.ZUUID AS 'zDetFace-UUID',		
        zFaceCrop.ZUUID AS 'zFaceCrop-UUID',		
        zFaceCrop.ZINVALIDMERGECANDIDATEPERSONUUID AS 'zFaceCrop-Invalid Merge Canidate Person UUID',		
        zPerson.ZPERSONUUID AS 'zPerson-Person UUID',
        zPerson.ZPERSONURI AS 'zPerson-Person URI',		
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFace.ZASSET AS 'zDetFace-AssetForFace= zAsset-zPK',
        zFaceCrop.ZASSET AS 'zFaceCrop-Asset Key',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
            LEFT JOIN ZDETECTEDFACE zDetFace ON zAsset.Z_PK = zDetFace.ZASSET
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSON
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP
        WHERE zDetFace.Z_PK > 0      
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            personcontactmatchingdictionary = ''
            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            facecropresourcedata_blob = ''

            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            if row[22] is not None:
                pathto = os.path.join(report_folder, 'zPerson-ContactMatchingDict_' + row[108] + '.plist')
                with open(pathto, 'ab') as wf:
                    wf.write(row[22])

                with open(pathto, 'rb') as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        personcontactmatchingdictionary = deserialized_plist

                    except (KeyError, ValueError, TypeError) as ex:
                        if str(ex).find("does not contain an '$archiver' key") >= 0:
                            logfunc('plist was Not an NSKeyedArchive ' + row[108])
                        else:
                            logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[108])

            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            if row[29] is not None:
                pathto = os.path.join(report_folder, 'FaceCropFor_' + row[106] + '.jpg')
                with open(pathto, 'wb') as file:
                    file.write(row[29])
                facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21],
                              personcontactmatchingdictionary,
                              row[23], row[24], row[25], row[26], row[27], row[28],
                              facecropresourcedata_blob,
                              row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                              row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                              row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                              row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                              row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                              row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                              row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                              row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                              row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                              row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
                              row[116]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        'zAsset-Directory-Path-7',
                        'zAsset-Filename-8',
                        'zAddAssetAttr- Original Filename-9',
                        'zCldMast- Original Filename-10',
                        ('zAsset-Trashed Date-11', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-12',
                        'zAddAssetAttr-Creator Bundle ID-13',
                        'zAddAssetAttr-Imported By Display Name-14',
                        'zCldMast-Imported by Bundle ID-15',
                        'zCldMast-Imported by Display Name-16',
                        'zAsset-Visibility State-17',
                        'zFaceCrop-Face Area Points-18',
                        'zAsset-Face Adjustment Version-19',
                        'zAddAssetAttr-Face_Regions-SeeRawDBData-20',
                        'zDetFacePrint-Data-SeeRawDBData-21',
                        'zPerson-Contact Matching Dictionary-22',
                        'zPerson-Verified Type-23',
                        'zPerson-Display Name-24',
                        'zPerson-Full Name-25',
                        'zPerson-Cloud Verified Type-26',
                        'zFaceCrop-State-27',
                        'zFaceCrop-Type-28',
                        'zFaceCrop-Resource Data-29',
                        'zDetFace-Confirmed Face Crop Generation State-30',
                        'zDetFace-Manual-31',
                        'zDetFace-VIP Model Type-32',
                        'zDetFace-Name Source-33',
                        'zDetFace-Cloud Name Source-34',
                        'zPerson-Type-35',
                        'zPerson-Gender Type-36',
                        'zDetFace-Gender Type-37',
                        'zDetFace-Center X-38',
                        'zDetFace-Center Y-39',
                        'zPerson-Age Type Estimate-40',
                        'zDetFace-Age Type Estimate-41',
                        'zDetFace-Hair Color Type-42',
                        'zDetFace-Facial Hair Type-43',
                        'zDetFace-Has Smile-44',
                        'zDetFace-Smile Type-45',
                        'zDetFace-Lip Makeup Type-46',
                        'zDetFace-Eyes State-47',
                        'zDetFace-Is Left Eye Closed-48',
                        'zDetFace-Is Right Eye Closed-49',
                        'zDetFace-Eye Glasses Type-50',
                        'zDetFace-Eye Makeup Type-51',
                        'zDetFace-Cluster Sequence Number Key-52',
                        'zDetFace-Grouping ID-53',
                        'zDetFace-Master ID-54',
                        'zDetFace-Quality-55',
                        'zDetFace-Quality Measure-56',
                        'zDetFace-Source Height-57',
                        'zDetFace-Source Width-58',
                        'zDetFace-Asset Visible-59',
                        'zDetFace-Hidden/Asset Hidden-60',
                        'zDetFace-In Trash/Recently Deleted-61',
                        'zDetFace-Cloud Local State-62',
                        'zDetFace-Training Type-63',
                        'zDetFace.Pose Yaw-64',
                        'zDetFace-Roll-65',
                        'zDetFace-Size-66',
                        'zDetFace-Cluster Sequence Number-67',
                        'zDetFace-Blur Score-68',
                        'zDetFacePrint-Face Print Version-69',
                        'zDetFaceGroup-UUID-70',
                        'zDetFaceGroup-Person Builder State-71',
                        'zDetFaceGroup-UnNamed Face Count-72',
                        'zPerson-Face Count-73',
                        'zDetFace-Face Algorithm Version-74',
                        'zDetFace-Adjustment Version-75',
                        'zPerson-In Person Naming Model-76',
                        'zPerson-Key Face Pick Source Key-77',
                        'zPerson-Manual Order Key-78',
                        'zPerson-Question Type-79',
                        'zPerson-Suggested For Client Type-80',
                        'zPerson-Merge Target Person-81',
                        'zPerson-Cloud Local State-82',
                        'zFaceCrop-Cloud Local State-83',
                        'zFaceCrop-Cloud Type-84',
                        'zPerson-Cloud Delete State-85',
                        'zFaceCrop-Cloud Delete State-86',
                        'zDetFace-zPK-87',
                        'zDetFacePrint-Face Key-88',
                        'zPerson-KeyFace=zDetFace-zPK-89',
                        'zFaceCrop-Face Key-90',
                        'zPerson-zPK=zDetFace-Person-91',
                        'zDetFace-PersonForFace= zPerson-zPK-92',
                        'zDetFace-Person Being Key Face-93',
                        'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-94',
                        'zDetFace-Face Print-95',
                        'zDetFacePrint-zPK-96',
                        'zDetFace-Face Crop-97',
                        'zFaceCrop-zPK-98',
                        'zDetFaceGroup-KeyFace= zDetFace-zPK-99',
                        'zDetFaceGroup-AssocPerson= zPerson-zPK-100',
                        'zPerson-Assoc Face Group Key-101',
                        'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-102',
                        'zDetFace-FaceGroup= zDetFaceGroup-zPK-103',
                        'zDetFaceGroup-zPK-104',
                        'zDetFace-UUID-105',
                        'zFaceCrop-UUID-106',
                        'zFaceCrop-Invalid Merge Candidate Person UUID-107',
                        'zPerson-Person UUID-108',
                        'zPerson-Person URI-109',
                        'zDetFaceGroup-UUID-110',
                        'zDetFace-AssetForFace= zAsset-zPK-111',
                        'zFaceCrop-Asset Key-112',
                        'zAsset-zPK-113',
                        'zAddAssetAttr-zPK-114',
                        'zAsset-UUID = store.cloudphotodb-115',
                        'zAddAssetAttr-Master Fingerprint-116')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',  
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE
            WHEN zAsset.ZFACEAREAPOINTS > 0 THEN 'Face Area Points Detected in zAsset'
            ELSE 'Face Area Points Not Detected in zAsset'
        END AS 'zFaceCrop-Face Area Points',
        zAsset.ZFACEADJUSTMENTVERSION AS 'zAsset-Face Adjustment Version',
        CASE
            WHEN zAddAssetAttr.ZFACEREGIONS > 0 THEN 'zAddAssetAttr-Face_Regions_has_Data'
            ELSE 'zAddAssetAttr-Face_Regions_has_NO-Data'
        END AS 'zAddAssetAttr-Face_Regions-SeeRawDBData',
        zAddAssetAttr.ZFACEANALYSISVERSION AS 'zAddAssetAttr-Face Analysis Version',
        CASE
            WHEN zDetFacePrint.ZDATA > 0 THEN 'zDetFacePrint-Data_has_Data'
            ELSE 'zDetFacePrint-Data_NO-Data'
        END AS 'zDetFacePrint-Data-SeeRawDBData',
        zPerson.ZCONTACTMATCHINGDICTIONARY AS 'zPerson-Contact Matching Dictionary',
        CASE zPerson.ZVERIFIEDTYPE
            WHEN 0 THEN '0-Not-Verified'
            WHEN 1 THEN '1-Has_Contact Matching_Dictionary'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZVERIFIEDTYPE || ''
        END AS 'zPerson-Verified Type',
        zPerson.ZDISPLAYNAME AS 'zPerson-Display Name',
        zPerson.ZFULLNAME AS 'zPerson-Full Name',
        CASE zPerson.ZCLOUDVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDVERIFIEDTYPE || ''
        END AS 'zPerson-Cloud Verified Type',
        CASE zFaceCrop.ZSTATE
            WHEN 5 THEN 'Validated-5'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZSTATE || ''
        END AS 'zFaceCrop-State',
        CASE zFaceCrop.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-Active'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZTYPE || ''
        END AS 'zFaceCrop-Type',
        zFaceCrop.ZRESOURCEDATA AS 'zFaceCrop-Resource Data',	
        CASE zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE || ''
        END AS 'zDetFace-Confirmed Face Crop Generation State',
        CASE zDetFace.ZMANUAL
            WHEN 0 THEN 'zDetFace-Auto Detected-0'
            WHEN 1 THEN 'zDetFace-Manually Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZMANUAL || ''
        END AS 'zDetFace-Manual',
        CASE zDetFace.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZDETECTIONTYPE || ''
        END AS 'zDetFace-Detection Type',
        CASE zPerson.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZDETECTIONTYPE || ''
        END AS 'zPerson-Detection Type',
        CASE zDetFace.ZVIPMODELTYPE
            WHEN 0 THEN 'Not VIP-0'
            WHEN 1 THEN 'VIP-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZVIPMODELTYPE || ''
        END AS 'zDetFace-VIP Model Type',
        CASE zDetFace.ZNAMESOURCE
            WHEN 0 THEN 'No Name Listed-0'
            WHEN 1 THEN '1-Face Crop-1'
            WHEN 2 THEN '2-Verified/Has-Person-URI'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZNAMESOURCE || ''
        END AS 'zDetFace-Name Source',
        CASE zDetFace.ZCLOUDNAMESOURCE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN '1-User Added Via Face Crop-1'
            WHEN 5 THEN '5-Asset Shared has Name'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDNAMESOURCE || ''
        END AS 'zDetFace-Cloud Name Source',
        CASE zPerson.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZTYPE || ''
        END AS 'zPerson-Type',
        CASE zPerson.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZGENDERTYPE || ''
        END AS 'zPerson-Gender Type',
        CASE zDetFace.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGENDERTYPE || ''
        END AS 'zDetFace-Gender Type',
        zDetFace.ZCENTERX AS 'zDetFace-Center X',
        zDetFace.ZCENTERY AS 'zDetFace-Center Y',
        CASE zPerson.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZAGETYPE || ''
        END AS 'zPerson-Age Type Estimate',
        CASE zDetFace.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZAGETYPE || ''
        END AS 'zDetFace-Age Type Estimate',
        CASE zDetFace.ZETHNICITYTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/African American-1'
            WHEN 2 THEN 'White-2'
            WHEN 3 THEN 'Hispanic/Latino-3'
            WHEN 4 THEN 'Asian-4'
            WHEN 5 THEN 'Native Hawaiian/Other Pacific Islander-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZETHNICITYTYPE || ''
        END AS 'zDetFace-Ethnicity Type',
        CASE zDetFace.ZSKINTONETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Light-Pale White Skin Tone-1'
            WHEN 2 THEN 'White-Fair Skin Tone-2'
            WHEN 3 THEN 'Medium-White to Olive Skin Tone-3'
            WHEN 4 THEN 'Olive-Moderate Brown Skin Tone-4'
            WHEN 5 THEN 'Brown-Dark Brown Skin Tone-5'
            WHEN 6 THEN 'Black-Very Dark Brown to Black Skin Tone-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSKINTONETYPE || ''
        END AS 'zDetFace-Skin Tone Type',
        CASE zDetFace.ZHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            WHEN 6 THEN '6-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRTYPE || ''
        END AS 'zDetFace-Hair Type',
        CASE zDetFace.ZHAIRCOLORTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/Brown Hair Color-1'
            WHEN 2 THEN 'Brown/Blonde Hair Color-2'
            WHEN 3 THEN 'Brown/Red Hair Color-3'
            WHEN 4 THEN 'Red/White Hair Color-4'
            WHEN 5 THEN 'StillTesting/Artifical-5'
            WHEN 6 THEN 'White/Bald Hair Color-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRCOLORTYPE || ''
        END AS 'zDetFace-Hair Color Type',
        CASE zDetFace.ZHEADGEARTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-No Headgear'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHEADGEARTYPE || ''
        END AS 'zDetFace-Head Gear Type',
        CASE zDetFace.ZFACIALHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Clean Shaven Facial Hair Type-1'
            WHEN 2 THEN 'Beard Facial Hair Type-2'
            WHEN 3 THEN 'Goatee Facial Hair Type-3'
            WHEN 4 THEN 'Mustache Facial Hair Type-4'
            WHEN 5 THEN 'Stubble Facial Hair Type-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACIALHAIRTYPE || ''
        END AS 'zDetFace-Facial Hair Type',
        CASE zDetFace.ZHASFACEMASK
            WHEN 0 THEN 'No Mask-0'
            WHEN 1 THEN 'Has Mask-1'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASFACEMASK || ''
        END AS 'zDetFace-Has Face Mask',
        CASE zDetFace.ZPOSETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Face Frontal Pose-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN 'Face Profile Pose-3'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZPOSETYPE || ''
        END AS 'zDetFace-Pose Type',
        CASE zDetFace.ZFACEEXPRESSIONTYPE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN 'Disgusted/Angry-1'
            WHEN 2 THEN 'Surprised/Fearful-2'
            WHEN 3 THEN 'Neutral-3'
            WHEN 4 THEN 'Confident/Smirk-4'
            WHEN 5 THEN 'Happiness-5'
            WHEN 6 THEN 'Sadness-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACEEXPRESSIONTYPE || ''
        END AS 'zDetFace-Face Expression Type',
        CASE zDetFace.ZHASSMILE
            WHEN 0 THEN 'zDetFace No Smile-0'
            WHEN 1 THEN 'zDetFace Smile-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASSMILE || ''
        END AS 'zDetFace-Has Smile',
        CASE zDetFace.ZSMILETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'zDetFace Smile No Teeth-1'
            WHEN 2 THEN 'zDetFace Smile has Teeth-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSMILETYPE || ''
        END AS 'zDetFace-Smile Type',
        CASE zDetFace.ZLIPMAKEUPTYPE
            WHEN 0 THEN 'zDetFace No Lip Makeup-0'
            WHEN 1 THEN 'zDetFace Lip Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZLIPMAKEUPTYPE || ''
        END AS 'zDetFace-Lip Makeup Type',
        CASE zDetFace.ZEYESSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eyes Closed-1'
            WHEN 2 THEN 'Eyes Open-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYESSTATE || ''
        END AS 'zDetFace-Eyes State',
        CASE zDetFace.ZISLEFTEYECLOSED
            WHEN 0 THEN 'Left Eye Open-0'
            WHEN 1 THEN 'Left Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISLEFTEYECLOSED || ''
        END AS 'zDetFace-Is Left Eye Closed',
        CASE zDetFace.ZISRIGHTEYECLOSED
            WHEN 0 THEN 'Right Eye Open-0'
            WHEN 1 THEN 'Right Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISRIGHTEYECLOSED || ''
        END AS 'zDetFace-Is Right Eye Closed',
        zDetFace.ZGAZECENTERX AS 'zDetFace-Gaze Center X',
        zDetFace.ZGAZECENTERY AS 'zDetFace-Gaze Center Y',
        CASE zDetFace.ZGAZETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGAZETYPE || ''
        END AS 'zDetFace-Face Gaze Type',
        CASE zDetFace.ZGLASSESTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eye Glasses-1'
            WHEN 2 THEN 'Sun Glasses-2'
            WHEN 3 THEN 'No Glasses-3'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGLASSESTYPE || ''
        END AS 'zDetFace-Eye Glasses Type',
        CASE zDetFace.ZEYEMAKEUPTYPE
            WHEN 0 THEN 'No Eye Makeup-0'
            WHEN 1 THEN 'Eye Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYEMAKEUPTYPE || ''
        END AS 'zDetFace-Eye Makeup Type',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Sequence Number Key',
        zDetFace.ZGROUPINGIDENTIFIER AS 'zDetFace-Grouping ID',
        zDetFace.ZMASTERIDENTIFIER AS 'zDetFace-Master ID',
        zDetFace.ZQUALITY AS 'zDetFace-Quality',
        zDetFace.ZQUALITYMEASURE AS 'zDetFace-Quality Measure',
        zDetFace.ZSOURCEHEIGHT AS 'zDetFace-Source Height',
        zDetFace.ZSOURCEWIDTH AS 'zDetFace-Source Width',
        CASE zDetFace.ZASSETVISIBLE
            WHEN 0 THEN '0-Unknown-StillTesitng-0'
            WHEN 1 THEN '1-Unknown-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZASSETVISIBLE || ''
        END AS 'zDetFace-Asset Visible',
        CASE zDetFace.ZHIDDEN
            WHEN 0 THEN 'Not Hidden-0'
            WHEN 1 THEN 'Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHIDDEN || ''
        END AS 'zDetFace-Hidden/Asset Hidden',
        CASE zDetFace.ZISINTRASH
            WHEN 0 THEN 'Not In Trash-0'
            WHEN 1 THEN 'In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISINTRASH || ''
        END AS 'zDetFace-In Trash/Recently Deleted',
        CASE zDetFace.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDLOCALSTATE || ''
        END AS 'zDetFace-Cloud Local State',
        CASE zDetFace.ZTRAININGTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZTRAININGTYPE
        END AS 'zDetFace-Training Type',
        zDetFace.ZPOSEYAW AS 'zDetFace.Pose Yaw',
        zDetFace.ZBODYCENTERX AS 'zDetFace-Body Center X',
        zDetFace.ZBODYCENTERY AS 'zDetFace-Body Center Y',
        zDetFace.ZBODYHEIGHT AS 'zDetFace-Body Height',
        zDetFace.ZBODYWIDTH AS 'zDetFace-Body Width',
        zDetFace.ZROLL AS 'zDetFace-Roll',
        zDetFace.ZSIZE AS 'zDetFace-Size',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number',
        zDetFace.ZBLURSCORE AS 'zDetFace-Blur Score',
        zDetFacePrint.ZFACEPRINTVERSION AS 'zDetFacePrint-Face Print Version',
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFaceGroup.ZPERSONBUILDERSTATE AS 'zDetFaceGroup-Person Builder State',
        zDetFaceGroup.ZUNNAMEDFACECOUNT AS 'zDetFaceGroup-UnNamed Face Count',
        zPerson.ZFACECOUNT AS 'zPerson-Face Count',       
        zDetFace.ZFACEALGORITHMVERSION AS 'zDetFace-Face Algorithm Version',
        zDetFace.ZADJUSTMENTVERSION AS 'zDetFace-Adjustment Version',       
        zPerson.ZINPERSONNAMINGMODEL AS 'zPerson-In Person Naming Model',
        zPerson.ZKEYFACEPICKSOURCE AS 'zPerson-Key Face Pick Source Key',
        zPerson.ZMANUALORDER AS 'zPerson-Manual Order Key',
        zPerson.ZQUESTIONTYPE AS 'zPerson-Question Type',
        zPerson.ZSUGGESTEDFORCLIENTTYPE AS 'zPerson-Suggested For Client Type',
        zPerson.ZMERGETARGETPERSON AS 'zPerson-Merge Target Person',
        CASE zPerson.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Person Not Synced with Cloud-0'
            WHEN 1 THEN 'Person Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDLOCALSTATE
        END AS 'zPerson-Cloud Local State',
        CASE zFaceCrop.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDLOCALSTATE || ''
        END AS 'zFaceCrop-Cloud Local State',
        CASE zFaceCrop.ZCLOUDTYPE
            WHEN 0 THEN 'Has Name-0'
            WHEN 5 THEN 'Has Face Key-5'
            WHEN 12 THEN '12-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDTYPE || ''
        END AS 'zFaceCrop-Cloud Type',
        CASE zPerson.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDDELETESTATE || ''
        END AS 'zPerson-Cloud Delete State',
        CASE zFaceCrop.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDDELETESTATE || ''
        END AS 'zFaceCrop-Cloud Delete State',
        zDetFace.Z_PK AS 'zDetFace-zPK',
        zDetFacePrint.ZFACE AS 'zDetFacePrint-Face Key',
        zPerson.ZKEYFACE AS 'zPerson-KeyFace=zDetFace-zPK',
        zFaceCrop.ZFACE AS 'zFaceCrop-Face Key',
        zPerson.Z_PK AS 'zPerson-zPK=zDetFace-Person',
        zDetFace.ZPERSON AS 'zDetFace-PersonForFace= zPerson-zPK',
        zDetFace.ZPERSONBEINGKEYFACE AS 'zDetFace-Person Being Key Face',         
        zFaceCrop.ZPERSON AS 'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key',	
        zDetFace.ZFACEPRINT AS 'zDetFace-Face Print',	
        zDetFacePrint.Z_PK AS 'zDetFacePrint-zPK',		
        zDetFace.ZFACECROP AS 'zDetFace-Face Crop',
        zFaceCrop.Z_PK AS 'zFaceCrop-zPK',           
        zDetFaceGroup.ZKEYFACE AS 'zDetFaceGroup-KeyFace= zDetFace-zPK',
        zDetFaceGroup.ZASSOCIATEDPERSON AS 'zDetFaceGroup-AssocPerson= zPerson-zPK',
        zPerson.ZASSOCIATEDFACEGROUP AS 'zPerson-Assoc Face Group Key',
        zDetFace.ZFACEGROUPBEINGKEYFACE AS 'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK',
        zDetFace.ZFACEGROUP AS 'zDetFace-FaceGroup= zDetFaceGroup-zPK',		
        zDetFaceGroup.Z_PK AS 'zDetFaceGroup-zPK',
        zDetFace.ZUUID AS 'zDetFace-UUID',		
        zFaceCrop.ZUUID AS 'zFaceCrop-UUID',		
        zFaceCrop.ZINVALIDMERGECANDIDATEPERSONUUID AS 'zFaceCrop-Invalid Merge Candidate Person UUID',		
        zPerson.ZPERSONUUID AS 'zPerson-Person UUID',
        zPerson.ZPERSONURI AS 'zPerson-Person URI',		
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFace.ZASSET AS 'zDetFace-AssetForFace= zAsset-zPK',
        zFaceCrop.ZASSET AS 'zFaceCrop-Asset Key',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
            LEFT JOIN ZDETECTEDFACE zDetFace ON zAsset.Z_PK = zDetFace.ZASSET
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSON
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP       
        WHERE zDetFace.Z_PK > 0  
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            personcontactmatchingdictionary = ''
            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            facecropresourcedata_blob = ''

            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            if row[25] is not None:
                pathto = os.path.join(report_folder, 'zPerson-ContactMatchingDict_' + row[127] + '.plist')
                with open(pathto, 'ab') as wf:
                    wf.write(row[25])

                with open(pathto, 'rb') as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        personcontactmatchingdictionary = deserialized_plist

                    except (KeyError, ValueError, TypeError) as ex:
                        if str(ex).find("does not contain an '$archiver' key") >= 0:
                            logfunc('plist was Not an NSKeyedArchive ' + row[127])
                        else:
                            logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[127])

            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            if row[32] is not None:
                pathto = os.path.join(report_folder, 'FaceCropFor_' + row[125] + '.jpg')
                with open(pathto, 'wb') as file:
                    file.write(row[32])
                facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21], row[22], row[23], row[24],
                              personcontactmatchingdictionary,
                              row[26], row[27],
                              row[28], row[29], row[30], row[31],
                              facecropresourcedata_blob,
                              row[33], row[34], row[35], row[36],
                              row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                              row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                              row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                              row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                              row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                              row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                              row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                              row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                              row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
                              row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
                              row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
                              row[132], row[133], row[134], row[135]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        'zAsset-Directory-Path-7',
                        'zAsset-Filename-8',
                        'zAddAssetAttr- Original Filename-9',
                        'zCldMast- Original Filename-10',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-11',
                        'zAsset- Conversation= zGenAlbum_zPK-12',
                        ('zAsset-Trashed Date-13', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-14',
                        'zAddAssetAttr-Imported by Bundle ID-15',
                        'zAddAssetAttr-Imported By Display Name-16',
                        'zCldMast-Imported by Bundle ID-17',
                        'zCldMast-Imported by Display Name-18',
                        'zAsset-Visibility State-19',
                        'zFaceCrop-Face Area Points-20',
                        'zAsset-Face Adjustment Version-21',
                        'zAddAssetAttr-Face_Regions-SeeRawDBData-22',
                        'zAddAssetAttr-Face Analysis Version-23',
                        'zDetFacePrint-Data-SeeRawDBData-24',
                        'zPerson-Contact Matching Dictionary-25',
                        'zPerson-Verified Type-26',
                        'zPerson-Display Name-27',
                        'zPerson-Full Name-28',
                        'zPerson-Cloud Verified Type-29',
                        'zFaceCrop-State-30',
                        'zFaceCrop-Type-31',
                        'zFaceCrop-Resource Data-32',
                        'zDetFace-Confirmed Face Crop Generation State-33',
                        'zDetFace-Manual-34',
                        'zDetFace-Detection Type-35',
                        'zPerson-Detection Type-36',
                        'zDetFace-VIP Model Type-37',
                        'zDetFace-Name Source-38',
                        'zDetFace-Cloud Name Source-39',
                        'zPerson-Type-40',
                        'zPerson-Gender Type-41',
                        'zDetFace-Gender Type-42',
                        'zDetFace-Center X-43',
                        'zDetFace-Center Y-44',
                        'zPerson-Age Type Estimate-45',
                        'zDetFace-Age Type Estimate-46',
                        'zDetFace-Ethnicity Type-47',
                        'zDetFace-Skin Tone Type-48',
                        'zDetFace-Hair Type-49',
                        'zDetFace-Hair Color Type-50',
                        'zDetFace-Head Gear Type-51',
                        'zDetFace-Facial Hair Type-52',
                        'zDetFace-Has Face Mask-53',
                        'zDetFace-Pose Type-54',
                        'zDetFace-Face Expression Type-55',
                        'zDetFace-Has Smile-56',
                        'zDetFace-Smile Type-57',
                        'zDetFace-Lip Makeup Type-58',
                        'zDetFace-Eyes State-59',
                        'zDetFace-Is Left Eye Closed-60',
                        'zDetFace-Is Right Eye Closed-61',
                        'zDetFace-Gaze Center X-62',
                        'zDetFace-Gaze Center Y-63',
                        'zDetFace-Face Gaze Type-64',
                        'zDetFace-Eye Glasses Type-65',
                        'zDetFace-Eye Makeup Type-66',
                        'zDetFace-Cluster Sequence Number Key-67',
                        'zDetFace-Grouping ID-68',
                        'zDetFace-Master ID-69',
                        'zDetFace-Quality-70',
                        'zDetFace-Quality Measure-71',
                        'zDetFace-Source Height-72',
                        'zDetFace-Source Width-73',
                        'zDetFace-Asset Visible-74',
                        'zDetFace-Hidden/Asset Hidden-75',
                        'zDetFace-In Trash/Recently Deleted-76',
                        'zDetFace-Cloud Local State-77',
                        'zDetFace-Training Type-78',
                        'zDetFace.Pose Yaw-79',
                        'zDetFace-Body Center X-80',
                        'zDetFace-Body Center Y-81',
                        'zDetFace-Body Height-82',
                        'zDetFace-Body Width-83',
                        'zDetFace-Roll-84',
                        'zDetFace-Size-85',
                        'zDetFace-Cluster Squence Number-86',
                        'zDetFace-Blur Score-87',
                        'zDetFacePrint-Face Print Version-88',
                        'zDetFaceGroup-UUID-89',
                        'zDetFaceGroup-Person Builder State-90',
                        'zDetFaceGroup-UnNamed Face Count-91',
                        'zPerson-Face Count-92',
                        'zDetFace-Face Algorithm Version-93',
                        'zDetFace-Adjustment Version-94',
                        'zPerson-In Person Naming Model-95',
                        'zPerson-Key Face Pick Source Key-96',
                        'zPerson-Manual Order Key-97',
                        'zPerson-Question Type-98',
                        'zPerson-Suggested For Client Type-99',
                        'zPerson-Merge Target Person-100',
                        'zPerson-Cloud Local State-101',
                        'zFaceCrop-Cloud Local State-102',
                        'zFaceCrop-Cloud Type-103',
                        'zPerson-Cloud Delete State-104',
                        'zFaceCrop-Cloud Delete State-105',
                        'zDetFace-zPK-106',
                        'zDetFacePrint-Face Key-107',
                        'zPerson-KeyFace=zDetFace-zPK-108',
                        'zFaceCrop-Face Key-109',
                        'zPerson-zPK=zDetFace-Person-110',
                        'zDetFace-PersonForFace= zPerson-zPK-111',
                        'zDetFace-Person Being Key Face-112',
                        'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-113',
                        'zDetFace-Face Print-114',
                        'zDetFacePrint-zPK-115',
                        'zDetFace-Face Crop-116',
                        'zFaceCrop-zPK-117',
                        'zDetFaceGroup-KeyFace= zDetFace-zPK-118',
                        'zDetFaceGroup-AssocPerson= zPerson-zPK-119',
                        'zPerson-Assoc Face Group Key-120',
                        'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-121',
                        'zDetFace-FaceGroup= zDetFaceGroup-zPK-122',
                        'zDetFaceGroup-zPK-123',
                        'zDetFace-UUID-124',
                        'zFaceCrop-UUID-125',
                        'zFaceCrop-Invalid Merge Candidate Person UUID-126',
                        'zPerson-Person UUID-127',
                        'zPerson-Person URI-128',
                        'zDetFaceGroup-UUID-129',
                        'zDetFace-AssetForFace= zAsset-zPK-130',
                        'zFaceCrop-Asset Key-131',
                        'zAsset-zPK-132',
                        'zAddAssetAttr-zPK-133',
                        'zAsset-UUID = store.cloudphotodb-134',
                        'zAddAssetAttr-Master Fingerprint-135')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("17")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',  
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE
            WHEN zAsset.ZFACEAREAPOINTS > 0 THEN 'Face Area Points Detected in zAsset'
            ELSE 'Face Area Points Not Detected in zAsset'
        END AS 'zFaceCrop-Face Area Points',
        zAsset.ZFACEADJUSTMENTVERSION AS 'zAsset-Face Adjustment Version',
        CASE
            WHEN zAddAssetAttr.ZFACEREGIONS > 0 THEN 'zAddAssetAttr-Face_Regions_has_Data'
            ELSE 'zAddAssetAttr-Face_Regions_has_NO-Data'
        END AS 'zAddAssetAttr-Face_Regions-SeeRawDBData',
        zAddAssetAttr.ZFACEANALYSISVERSION AS 'zAddAssetAttr-Face Analysis Version',
        CASE
            WHEN zDetFacePrint.ZDATA > 0 THEN 'zDetFacePrint-Data_has_Data'
            ELSE 'zDetFacePrint-Data_NO-Data'
        END AS 'zDetFacePrint-Data-SeeRawDBData',
        zPerson.ZCONTACTMATCHINGDICTIONARY AS 'zPerson-Contact Matching Dictionary',
        CASE zPerson.ZVERIFIEDTYPE
            WHEN 0 THEN '0-Not-Verified'
            WHEN 1 THEN '1-Has_Contact Matching_Dictionary'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZVERIFIEDTYPE || ''
        END AS 'zPerson-Verified Type',
        zPerson.ZDISPLAYNAME AS 'zPerson-Display Name',
        zPerson.ZFULLNAME AS 'zPerson-Full Name',
        CASE zPerson.ZCLOUDVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDVERIFIEDTYPE || ''
        END AS 'zPerson-Cloud Verified Type',
        CASE zFaceCrop.ZSTATE
            WHEN 5 THEN 'Validated-5'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZSTATE || ''
        END AS 'zFaceCrop-State',
        CASE zFaceCrop.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-Active'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZTYPE || ''
        END AS 'zFaceCrop-Type',
        zFaceCrop.ZRESOURCEDATA AS 'zFaceCrop-Resource Data',	
        CASE zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE || ''
        END AS 'zDetFace-Confirmed Face Crop Generation State',
        CASE zDetFace.ZMANUAL
            WHEN 0 THEN 'zDetFace-Auto Detected-0'
            WHEN 1 THEN 'zDetFace-Manually Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZMANUAL || ''
        END AS 'zDetFace-Manual',
        CASE zDetFace.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZDETECTIONTYPE || ''
        END AS 'zDetFace-Detection Type',
        CASE zPerson.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZDETECTIONTYPE || ''
        END AS 'zPerson-Detection Type',
        CASE zDetFace.ZVIPMODELTYPE
            WHEN 0 THEN 'Not VIP-0'
            WHEN 1 THEN 'VIP-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZVIPMODELTYPE || ''
        END AS 'zDetFace-VIP Model Type',
        CASE zDetFace.ZNAMESOURCE
            WHEN 0 THEN 'No Name Listed-0'
            WHEN 1 THEN '1-Face Crop-1'
            WHEN 2 THEN '2-Verified/Has-Person-URI'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZNAMESOURCE || ''
        END AS 'zDetFace-Name Source',
        CASE zDetFace.ZCLOUDNAMESOURCE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN '1-User Added Via Face Crop-1'
            WHEN 5 THEN '5-Asset Shared has Name'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDNAMESOURCE || ''
        END AS 'zDetFace-Cloud Name Source',
        zPerson.ZMERGECANDIDATECONFIDENCE AS 'zPerson-Merge Candidate Confidence',
        CASE zPerson.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZTYPE || ''
        END AS 'zPerson-Type',
        CASE zPerson.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZGENDERTYPE || ''
        END AS 'zPerson-Gender Type',
        CASE zDetFace.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGENDERTYPE || ''
        END AS 'zDetFace-Gender Type',
        zDetFace.ZCENTERX AS 'zDetFace-Center X',
        zDetFace.ZCENTERY AS 'zDetFace-Center Y',
        CASE zPerson.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZAGETYPE || ''
        END AS 'zPerson-Age Type Estimate',
        CASE zDetFace.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZAGETYPE || ''
        END AS 'zDetFace-Age Type Estimate',
        CASE zDetFace.ZETHNICITYTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/African American-1'
            WHEN 2 THEN 'White-2'
            WHEN 3 THEN 'Hispanic/Latino-3'
            WHEN 4 THEN 'Asian-4'
            WHEN 5 THEN 'Native Hawaiian/Other Pacific Islander-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZETHNICITYTYPE || ''
        END AS 'zDetFace-Ethnicity Type',
        CASE zDetFace.ZSKINTONETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Light-Pale White Skin Tone-1'
            WHEN 2 THEN 'White-Fair Skin Tone-2'
            WHEN 3 THEN 'Medium-White to Olive Skin Tone-3'
            WHEN 4 THEN 'Olive-Moderate Brown Skin Tone-4'
            WHEN 5 THEN 'Brown-Dark Brown Skin Tone-5'
            WHEN 6 THEN 'Black-Very Dark Brown to Black Skin Tone-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSKINTONETYPE || ''
        END AS 'zDetFace-Skin Tone Type',
        CASE zDetFace.ZHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            WHEN 6 THEN '6-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRTYPE || ''
        END AS 'zDetFace-Hair Type',
        CASE zDetFace.ZHAIRCOLORTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/Brown Hair Color-1'
            WHEN 2 THEN 'Brown/Blonde Hair Color-2'
            WHEN 3 THEN 'Brown/Red Hair Color-3'
            WHEN 4 THEN 'Red/White Hair Color-4'
            WHEN 5 THEN 'StillTesting/Artifical-5'
            WHEN 6 THEN 'White/Bald Hair Color-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRCOLORTYPE || ''
        END AS 'zDetFace-Hair Color Type',
        CASE zDetFace.ZHEADGEARTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-No Headgear'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHEADGEARTYPE || ''
        END AS 'zDetFace-Head Gear Type',
        CASE zDetFace.ZFACIALHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Clean Shaven Facial Hair Type-1'
            WHEN 2 THEN 'Beard Facial Hair Type-2'
            WHEN 3 THEN 'Goatee Facial Hair Type-3'
            WHEN 4 THEN 'Mustache Facial Hair Type-4'
            WHEN 5 THEN 'Stubble Facial Hair Type-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACIALHAIRTYPE || ''
        END AS 'zDetFace-Facial Hair Type',
        CASE zDetFace.ZHASFACEMASK
            WHEN 0 THEN 'No Mask-0'
            WHEN 1 THEN 'Has Mask-1'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASFACEMASK || ''
        END AS 'zDetFace-Has Face Mask',
        CASE zDetFace.ZPOSETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Face Frontal Pose-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN 'Face Profile Pose-3'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZPOSETYPE || ''
        END AS 'zDetFace-Pose Type',
        CASE zDetFace.ZFACEEXPRESSIONTYPE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN 'Disgusted/Angry-1'
            WHEN 2 THEN 'Suprised/Fearful-2'
            WHEN 3 THEN 'Neutral-3'
            WHEN 4 THEN 'Confident/Smirk-4'
            WHEN 5 THEN 'Happiness-5'
            WHEN 6 THEN 'Sadness-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACEEXPRESSIONTYPE || ''
        END AS 'zDetFace-Face Expression Type',
        CASE zDetFace.ZHASSMILE
            WHEN 0 THEN 'zDetFace No Smile-0'
            WHEN 1 THEN 'zDetFace Smile-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASSMILE || ''
        END AS 'zDetFace-Has Smile',
        CASE zDetFace.ZSMILETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'zDetFace Smile No Teeth-1'
            WHEN 2 THEN 'zDetFace Smile has Teeth-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSMILETYPE || ''
        END AS 'zDetFace-Smile Type',
        CASE zDetFace.ZLIPMAKEUPTYPE
            WHEN 0 THEN 'zDetFace No Lip Makeup-0'
            WHEN 1 THEN 'zDetFace Lip Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZLIPMAKEUPTYPE || ''
        END AS 'zDetFace-Lip Makeup Type',
        CASE zDetFace.ZEYESSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eyes Closed-1'
            WHEN 2 THEN 'Eyes Open-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYESSTATE || ''
        END AS 'zDetFace-Eyes State',
        CASE zDetFace.ZISLEFTEYECLOSED
            WHEN 0 THEN 'Left Eye Open-0'
            WHEN 1 THEN 'Left Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISLEFTEYECLOSED || ''
        END AS 'zDetFace-Is Left Eye Closed',
        CASE zDetFace.ZISRIGHTEYECLOSED
            WHEN 0 THEN 'Right Eye Open-0'
            WHEN 1 THEN 'Right Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISRIGHTEYECLOSED || ''
        END AS 'zDetFace-Is Right Eye Closed',
        zDetFace.ZGAZECENTERX AS 'zDetFace-Gaze Center X',
        zDetFace.ZGAZECENTERY AS 'zDetFace-Gaze Center Y',
        CASE zDetFace.ZGAZETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGAZETYPE || ''
        END AS 'zDetFace-Face Gaze Type',
        CASE zDetFace.ZGLASSESTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eye Glasses-1'
            WHEN 2 THEN 'Sun Glasses-2'
            WHEN 3 THEN 'No Glasses-3'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGLASSESTYPE || ''
        END AS 'zDetFace-Eye Glasses Type',
        CASE zDetFace.ZEYEMAKEUPTYPE
            WHEN 0 THEN 'No Eye Makeup-0'
            WHEN 1 THEN 'Eye Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYEMAKEUPTYPE || ''
        END AS 'zDetFace-Eye Makeup Type',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Sequence Number Key',
        zDetFace.ZGROUPINGIDENTIFIER AS 'zDetFace-Grouping ID',
        zDetFace.ZMASTERIDENTIFIER AS 'zDetFace-Master ID',
        zDetFace.ZQUALITY AS 'zDetFace-Quality',
        zDetFace.ZQUALITYMEASURE AS 'zDetFace-Quality Measure',
        zDetFace.ZSOURCEHEIGHT AS 'zDetFace-Source Height',
        zDetFace.ZSOURCEWIDTH AS 'zDetFace-Source Width',
        CASE zDetFace.ZASSETVISIBLE
            WHEN 0 THEN '0-Unknown-StillTesitng-0'
            WHEN 1 THEN '1-Unknown-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZASSETVISIBLE || ''
        END AS 'zDetFace-Asset Visible',
        CASE zDetFace.ZHIDDEN
            WHEN 0 THEN 'Not Hidden-0'
            WHEN 1 THEN 'Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHIDDEN || ''
        END AS 'zDetFace-Hidden/Asset Hidden',
        CASE zDetFace.ZISINTRASH
            WHEN 0 THEN 'Not In Trash-0'
            WHEN 1 THEN 'In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISINTRASH || ''
        END AS 'zDetFace-In Trash/Recently Deleted',
        CASE zDetFace.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDLOCALSTATE || ''
        END AS 'zDetFace-Cloud Local State',
        CASE zDetFace.ZTRAININGTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZTRAININGTYPE
        END AS 'zDetFace-Training Type',
        zDetFace.ZPOSEYAW AS 'zDetFace.Pose Yaw',
        zDetFace.ZBODYCENTERX AS 'zDetFace-Body Center X',
        zDetFace.ZBODYCENTERY AS 'zDetFace-Body Center Y',
        zDetFace.ZBODYHEIGHT AS 'zDetFace-Body Height',
        zDetFace.ZBODYWIDTH AS 'zDetFace-Body Width',
        zDetFace.ZROLL AS 'zDetFace-Roll',
        zDetFace.ZSIZE AS 'zDetFace-Size',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Sequence Number',
        zDetFace.ZBLURSCORE AS 'zDetFace-Blur Score',
        zDetFacePrint.ZFACEPRINTVERSION AS 'zDetFacePrint-Face Print Version',
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFaceGroup.ZPERSONBUILDERSTATE AS 'zDetFaceGroup-Person Builder State',
        zDetFaceGroup.ZUNNAMEDFACECOUNT AS 'zDetFaceGroup-UnNamed Face Count',
        zPerson.ZFACECOUNT AS 'zPerson-Face Count',       
        zDetFace.ZFACEALGORITHMVERSION AS 'zDetFace-Face Algorithm Version',
        zDetFace.ZADJUSTMENTVERSION AS 'zDetFace-Adjustment Version',       
        zPerson.ZINPERSONNAMINGMODEL AS 'zPerson-In Person Naming Model',
        zPerson.ZKEYFACEPICKSOURCE AS 'zPerson-Key Face Pick Source Key',
        zPerson.ZMANUALORDER AS 'zPerson-Manual Order Key',
        zPerson.ZQUESTIONTYPE AS 'zPerson-Question Type',
        zPerson.ZSUGGESTEDFORCLIENTTYPE AS 'zPerson-Suggested For Client Type',
        zPerson.ZMERGETARGETPERSON AS 'zPerson-Merge Target Person',
        CASE zPerson.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Person Not Synced with Cloud-0'
            WHEN 1 THEN 'Person Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDLOCALSTATE
        END AS 'zPerson-Cloud Local State',
        CASE zFaceCrop.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDLOCALSTATE || ''
        END AS 'zFaceCrop-Cloud Local State',
        CASE zFaceCrop.ZCLOUDTYPE
            WHEN 0 THEN 'Has Name-0'
            WHEN 5 THEN 'Has Face Key-5'
            WHEN 12 THEN '12-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDTYPE || ''
        END AS 'zFaceCrop-Cloud Type',
        CASE zPerson.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDDELETESTATE || ''
        END AS 'zPerson-Cloud Delete State',
        CASE zFaceCrop.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDDELETESTATE || ''
        END AS 'zFaceCrop-Cloud Delete State',
        zDetFace.Z_PK AS 'zDetFace-zPK',
        zDetFacePrint.ZFACE AS 'zDetFacePrint-Face Key',
        zPerson.ZKEYFACE AS 'zPerson-KeyFace=zDetFace-zPK',
        zFaceCrop.ZFACE AS 'zFaceCrop-Face Key',
        zPerson.Z_PK AS 'zPerson-zPK=zDetFace-Person',
        zDetFace.ZPERSON AS 'zDetFace-PersonForFace= zPerson-zPK',
        zDetFace.ZPERSONBEINGKEYFACE AS 'zDetFace-Person Being Key Face',         
        zFaceCrop.ZPERSON AS 'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key',	
        zDetFace.ZFACEPRINT AS 'zDetFace-Face Print',	
        zDetFacePrint.Z_PK AS 'zDetFacePrint-zPK',		
        zDetFace.ZFACECROP AS 'zDetFace-Face Crop',
        zFaceCrop.Z_PK AS 'zFaceCrop-zPK',           
        zDetFaceGroup.ZKEYFACE AS 'zDetFaceGroup-KeyFace= zDetFace-zPK',
        zDetFaceGroup.ZASSOCIATEDPERSON AS 'zDetFaceGroup-AssocPerson= zPerson-zPK',
        zPerson.ZASSOCIATEDFACEGROUP AS 'zPerson-Assoc Face Group Key',
        zDetFace.ZFACEGROUPBEINGKEYFACE AS 'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK',
        zDetFace.ZFACEGROUP AS 'zDetFace-FaceGroup= zDetFaceGroup-zPK',		
        zDetFaceGroup.Z_PK AS 'zDetFaceGroup-zPK',
        zPerson.ZSHAREPARTICIPANT AS 'zPerson-Share Participant= zSharePartic-zPK',		
        zDetFace.ZUUID AS 'zDetFace-UUID',		
        zFaceCrop.ZUUID AS 'zFaceCrop-UUID',	
        zFaceCrop.ZINVALIDMERGECANDIDATEPERSONUUID AS 'zFaceCrop-Invalid Merge Candidate Person UUID',		
        zPerson.ZPERSONUUID AS 'zPerson-Person UUID',
        zPerson.ZPERSONURI AS 'zPerson-Person URI',		
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFace.ZASSET AS 'zDetFace-AssetForFace= zAsset-zPK',
        zFaceCrop.ZASSET AS 'zFaceCrop-Asset Key',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
            LEFT JOIN ZDETECTEDFACE zDetFace ON zAsset.Z_PK = zDetFace.ZASSET
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSON
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP
        WHERE zDetFace.Z_PK > 0  
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            personcontactmatchingdictionary = ''
            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            facecropresourcedata_blob = ''

            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            if row[26] is not None:
                pathto = os.path.join(report_folder, 'zPerson-ContactMatchingDict_' + row[130] + '.plist')
                with open(pathto, 'ab') as wf:
                    wf.write(row[26])

                with open(pathto, 'rb') as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        personcontactmatchingdictionary = deserialized_plist

                    except (KeyError, ValueError, TypeError) as ex:
                        if str(ex).find("does not contain an '$archiver' key") >= 0:
                            logfunc('plist was Not an NSKeyedArchive ' + row[130])
                        else:
                            logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[130])

            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            if row[33] is not None:
                pathto = os.path.join(report_folder, 'FaceCropFor_' + row[128] + '.jpg')
                with open(pathto, 'wb') as file:
                    file.write(row[33])
                facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21], row[22], row[23], row[24], row[25],
                              personcontactmatchingdictionary,
                              row[27], row[28], row[29], row[30], row[31], row[32],
                              facecropresourcedata_blob,
                              row[34], row[35], row[36],
                              row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                              row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                              row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                              row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                              row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                              row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                              row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                              row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                              row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
                              row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
                              row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
                              row[132], row[133], row[134], row[135], row[136], row[137], row[138]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        'zAsset-Directory-Path-7',
                        'zAsset-Filename-8',
                        'zAddAssetAttr- Original Filename-9',
                        'zCldMast- Original Filename-10',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-11',
                        'zAsset- Conversation= zGenAlbum_zPK-12',
                        ('zAsset-Trashed Date-13', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-14',
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-15',
                        'zAddAssetAttr-Imported by Bundle ID-16',
                        'zAddAssetAttr-Imported By Display Name-17',
                        'zCldMast-Imported by Bundle ID-18',
                        'zCldMast-Imported by Display Name-19',
                        'zAsset-Visibility State-20',
                        'zFaceCrop-Face Area Points-21',
                        'zAsset-Face Adjustment Version-22',
                        'zAddAssetAttr-Face_Regions-SeeRawDBData-23',
                        'zAddAssetAttr-Face Analysis Version-24',
                        'zDetFacePrint-Data-SeeRawDBData-25',
                        'zPerson-Contact Matching Dictionary-26',
                        'zPerson-Verified Type-27',
                        'zPerson-Display Name-28',
                        'zPerson-Full Name-29',
                        'zPerson-Cloud Verified Type-30',
                        'zFaceCrop-State-31',
                        'zFaceCrop-Type-32',
                        'zFaceCrop-Resource Data-33',
                        'zDetFace-Confirmed Face Crop Generation State-34',
                        'zDetFace-Manual-35',
                        'zDetFace-Detection Type-36',
                        'zPerson-Detection Type-37',
                        'zDetFace-VIP Model Type-38',
                        'zDetFace-Name Source-39',
                        'zDetFace-Cloud Name Source-40',
                        'zPerson-Merge Candidate Confidence-41',
                        'zPerson-Type-42',
                        'zPerson-Gender Type-43',
                        'zDetFace-Gender Type-44',
                        'zDetFace-Center X-45',
                        'zDetFace-Center Y-46',
                        'zPerson-Age Type Estimate-47',
                        'zDetFace-Age Type Estimate-48',
                        'zDetFace-Ethnicity Type-49',
                        'zDetFace-Skin Tone Type-50',
                        'zDetFace-Hair Type-51',
                        'zDetFace-Hair Color Type-52',
                        'zDetFace-Head Gear Type-53',
                        'zDetFace-Facial Hair Type-54',
                        'zDetFace-Has Face Mask-55',
                        'zDetFace-Pose Type-56',
                        'zDetFace-Face Expression Type-57',
                        'zDetFace-Has Smile-58',
                        'zDetFace-Smile Type-59',
                        'zDetFace-Lip Makeup Type-60',
                        'zDetFace-Eyes State-61',
                        'zDetFace-Is Left Eye Closed-62',
                        'zDetFace-Is Right Eye Closed-63',
                        'zDetFace-Gaze Center X-64',
                        'zDetFace-Gaze Center Y-65',
                        'zDetFace-Face Gaze Type-66',
                        'zDetFace-Eye Glasses Type-67',
                        'zDetFace-Eye Makeup Type-68',
                        'zDetFace-Cluster Sequence Number Key-69',
                        'zDetFace-Grouping ID-70',
                        'zDetFace-Master ID-71',
                        'zDetFace-Quality-72',
                        'zDetFace-Quality Measure-73',
                        'zDetFace-Source Height-74',
                        'zDetFace-Source Width-75',
                        'zDetFace-Asset Visible-76',
                        'zDetFace-Hidden/Asset Hidden-77',
                        'zDetFace-In Trash/Recently Deleted-78',
                        'zDetFace-Cloud Local State-79',
                        'zDetFace-Training Type-80',
                        'zDetFace.Pose Yaw-81',
                        'zDetFace-Body Center X-82',
                        'zDetFace-Body Center Y-83',
                        'zDetFace-Body Height-84',
                        'zDetFace-Body Width-85',
                        'zDetFace-Roll-86',
                        'zDetFace-Size-87',
                        'zDetFace-Cluster Sequence Number-88',
                        'zDetFace-Blur Score-89',
                        'zDetFacePrint-Face Print Version-90',
                        'zDetFaceGroup-UUID-91',
                        'zDetFaceGroup-Person Builder State-92',
                        'zDetFaceGroup-UnNamed Face Count-93',
                        'zPerson-Face Count-94',
                        'zDetFace-Face Algorithm Version-95',
                        'zDetFace-Adjustment Version-96',
                        'zPerson-In Person Naming Model-97',
                        'zPerson-Key Face Pick Source Key-98',
                        'zPerson-Manual Order Key-99',
                        'zPerson-Question Type-100',
                        'zPerson-Suggested For Client Type-101',
                        'zPerson-Merge Target Person-102',
                        'zPerson-Cloud Local State-103',
                        'zFaceCrop-Cloud Local State-104',
                        'zFaceCrop-Cloud Type-105',
                        'zPerson-Cloud Delete State-106',
                        'zFaceCrop-Cloud Delete State-107',
                        'zDetFace-zPK-108',
                        'zDetFacePrint-Face Key-109',
                        'zPerson-KeyFace=zDetFace-zPK-110',
                        'zFaceCrop-Face Key-111',
                        'zPerson-zPK=zDetFace-Person-112',
                        'zDetFace-PersonForFace= zPerson-zPK-113',
                        'zDetFace-Person Being Key Face-114',
                        'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-115',
                        'zDetFace-Face Print-116',
                        'zDetFacePrint-zPK-117',
                        'zDetFace-Face Crop-118',
                        'zFaceCrop-zPK-119',
                        'zDetFaceGroup-KeyFace= zDetFace-zPK-120',
                        'zDetFaceGroup-AssocPerson= zPerson-zPK-121',
                        'zPerson-Assoc Face Group Key-122',
                        'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-123',
                        'zDetFace-FaceGroup= zDetFaceGroup-zPK-124',
                        'zDetFaceGroup-zPK-125',
                        'zPerson-Share Participant= zSharePartic-zPK-126',
                        'zDetFace-UUID-127',
                        'zFaceCrop-UUID-128',
                        'zFaceCrop-Invalid Merge Candidate Person UUID-129',
                        'zPerson-Person UUID-130',
                        'zPerson-Person URI-131',
                        'zDetFaceGroup-UUID-132',
                        'zDetFace-AssetForFace= zAsset-zPK-133',
                        'zFaceCrop-Asset Key-134',
                        'zAsset-zPK-135',
                        'zAddAssetAttr-zPK-136',
                        'zAsset-UUID = store.cloudphotodb-137',
                        'zAddAssetAttr-Master Fingerprint-138')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("17")) & (version.parse(iosversion) < version.parse("18")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',  
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE
            WHEN zAsset.ZFACEAREAPOINTS > 0 THEN 'Face Area Points Detected in zAsset'
            ELSE 'Face Area Points Not Detected in zAsset'
        END AS 'zFaceCrop-Face Area Points',
        zAsset.ZFACEADJUSTMENTVERSION AS 'zAsset-Face Adjustment Version',
        CASE
            WHEN zAddAssetAttr.ZFACEREGIONS > 0 THEN 'zAddAssetAttr-Face_Regions_has_Data'
            ELSE 'zAddAssetAttr-Face_Regions_has_NO-Data'
        END AS 'zAddAssetAttr-Face_Regions-SeeRawDBData',
        zAddAssetAttr.ZFACEANALYSISVERSION AS 'zAddAssetAttr-Face Analysis Version',
        zDetFace.ZASSETFORTEMPORALDETECTEDFACES AS 'zDetFace-Asset For Temporal Detected Faces= zAsset-zPK',
        CASE
            WHEN zDetFacePrint.ZDATA > 0 THEN 'zDetFacePrint-Data_has_Data'
            ELSE 'zDetFacePrint-Data_NO-Data'
        END AS 'zDetFacePrint-Data-SeeRawDBData',
        zPerson.ZCONTACTMATCHINGDICTIONARY AS 'zPerson-Contact Matching Dictionary',
        CASE zPerson.ZVERIFIEDTYPE
            WHEN 0 THEN '0-Not-Verified'
            WHEN 1 THEN '1-Has_Contact Matching_Dictionary'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZVERIFIEDTYPE || ''
        END AS 'zPerson-Verified Type',
        zPerson.ZDISPLAYNAME AS 'zPerson-Display Name',
        zPerson.ZFULLNAME AS 'zPerson-Full Name',
        CASE zPerson.ZCLOUDVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDVERIFIEDTYPE || ''
        END AS 'zPerson-Cloud Verified Type',
        CASE zFaceCrop.ZSTATE
            WHEN 5 THEN 'Validated-5'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZSTATE || ''
        END AS 'zFaceCrop-State',
        CASE zFaceCrop.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-Active'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZTYPE || ''
        END AS 'zFaceCrop-Type',
        zFaceCrop.ZRESOURCEDATA AS 'zFaceCrop-Resource Data',	
        CASE zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE || ''
        END AS 'zDetFace-Confirmed Face Crop Generation State',
        CASE zDetFace.ZMANUAL
            WHEN 0 THEN 'zDetFace-Auto Detected-0'
            WHEN 1 THEN 'zDetFace-Manually Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZMANUAL || ''
        END AS 'zDetFace-Manual',
        CASE zDetFace.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZDETECTIONTYPE || ''
        END AS 'zDetFace-Detection Type',
        CASE zPerson.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZDETECTIONTYPE || ''
        END AS 'zPerson-Detection Type',
        CASE zDetFace.ZVIPMODELTYPE
            WHEN 0 THEN 'Not VIP-0'
            WHEN 1 THEN 'VIP-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZVIPMODELTYPE || ''
        END AS 'zDetFace-VIP Model Type',
        CASE zDetFace.ZNAMESOURCE
            WHEN 0 THEN 'No Name Listed-0'
            WHEN 1 THEN '1-Face Crop-1'
            WHEN 2 THEN '2-Verified/Has-Person-URI'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZNAMESOURCE || ''
        END AS 'zDetFace-Name Source',
        CASE zDetFace.ZCLOUDNAMESOURCE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN '1-User Added Via Face Crop-1'
            WHEN 5 THEN '5-Asset Shared has Name'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDNAMESOURCE || ''
        END AS 'zDetFace-Cloud Name Source',
        zPerson.ZMERGECANDIDATECONFIDENCE AS 'zPerson-Merge Candidate Confidence',
        CASE zPerson.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZTYPE || ''
        END AS 'zPerson-Type',
        CASE zPerson.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZGENDERTYPE || ''
        END AS 'zPerson-Gender Type',
        CASE zDetFace.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGENDERTYPE || ''
        END AS 'zDetFace-Gender Type',
        zDetFace.ZCENTERX AS 'zDetFace-Center X',
        zDetFace.ZCENTERY AS 'zDetFace-Center Y',
        CASE zPerson.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZAGETYPE || ''
        END AS 'zPerson-Age Type Estimate',
        CASE zDetFace.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZAGETYPE || ''
        END AS 'zDetFace-Age Type Estimate',
        CASE zDetFace.ZETHNICITYTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/African American-1'
            WHEN 2 THEN 'White-2'
            WHEN 3 THEN 'Hispanic/Latino-3'
            WHEN 4 THEN 'Asian-4'
            WHEN 5 THEN 'Native Hawaiian/Other Pacific Islander-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZETHNICITYTYPE || ''
        END AS 'zDetFace-Ethnicity Type',
        CASE zDetFace.ZSKINTONETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Light-Pale White Skin Tone-1'
            WHEN 2 THEN 'White-Fair Skin Tone-2'
            WHEN 3 THEN 'Medium-White to Olive Skin Tone-3'
            WHEN 4 THEN 'Olive-Moderate Brown Skin Tone-4'
            WHEN 5 THEN 'Brown-Dark Brown Skin Tone-5'
            WHEN 6 THEN 'Black-Very Dark Brown to Black Skin Tone-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSKINTONETYPE || ''
        END AS 'zDetFace-Skin Tone Type',
        CASE zDetFace.ZHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            WHEN 6 THEN '6-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRTYPE || ''
        END AS 'zDetFace-Hair Type',
        CASE zDetFace.ZHAIRCOLORTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/Brown Hair Color-1'
            WHEN 2 THEN 'Brown/Blonde Hair Color-2'
            WHEN 3 THEN 'Brown/Red Hair Color-3'
            WHEN 4 THEN 'Red/White Hair Color-4'
            WHEN 5 THEN 'StillTesting/Artifical-5'
            WHEN 6 THEN 'White/Bald Hair Color-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRCOLORTYPE || ''
        END AS 'zDetFace-Hair Color Type',
        CASE zDetFace.ZHEADGEARTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-No Headgear'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHEADGEARTYPE || ''
        END AS 'zDetFace-Head Gear Type',
        CASE zDetFace.ZFACIALHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Clean Shaven Facial Hair Type-1'
            WHEN 2 THEN 'Beard Facial Hair Type-2'
            WHEN 3 THEN 'Goatee Facial Hair Type-3'
            WHEN 4 THEN 'Mustache Facial Hair Type-4'
            WHEN 5 THEN 'Stubble Facial Hair Type-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACIALHAIRTYPE || ''
        END AS 'zDetFace-Facial Hair Type',
        CASE zDetFace.ZHASFACEMASK
            WHEN 0 THEN 'No Mask-0'
            WHEN 1 THEN 'Has Mask-1'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASFACEMASK || ''
        END AS 'zDetFace-Has Face Mask',
        CASE zDetFace.ZPOSETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Face Frontal Pose-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN 'Face Profile Pose-3'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZPOSETYPE || ''
        END AS 'zDetFace-Pose Type',
        CASE zDetFace.ZFACEEXPRESSIONTYPE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN 'Disgusted/Angry-1'
            WHEN 2 THEN 'Suprised/Fearful-2'
            WHEN 3 THEN 'Neutral-3'
            WHEN 4 THEN 'Confident/Smirk-4'
            WHEN 5 THEN 'Happiness-5'
            WHEN 6 THEN 'Sadness-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACEEXPRESSIONTYPE || ''
        END AS 'zDetFace-Face Expression Type',
        CASE zDetFace.ZHASSMILE
            WHEN 0 THEN 'zDetFace No Smile-0'
            WHEN 1 THEN 'zDetFace Smile-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASSMILE || ''
        END AS 'zDetFace-Has Smile',
        CASE zDetFace.ZSMILETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'zDetFace Smile No Teeth-1'
            WHEN 2 THEN 'zDetFace Smile has Teeth-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSMILETYPE || ''
        END AS 'zDetFace-Smile Type',
        CASE zDetFace.ZLIPMAKEUPTYPE
            WHEN 0 THEN 'zDetFace No Lip Makeup-0'
            WHEN 1 THEN 'zDetFace Lip Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZLIPMAKEUPTYPE || ''
        END AS 'zDetFace-Lip Makeup Type',
        CASE zDetFace.ZEYESSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eyes Closed-1'
            WHEN 2 THEN 'Eyes Open-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYESSTATE || ''
        END AS 'zDetFace-Eyes State',
        CASE zDetFace.ZISLEFTEYECLOSED
            WHEN 0 THEN 'Left Eye Open-0'
            WHEN 1 THEN 'Left Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISLEFTEYECLOSED || ''
        END AS 'zDetFace-Is Left Eye Closed',
        CASE zDetFace.ZISRIGHTEYECLOSED
            WHEN 0 THEN 'Right Eye Open-0'
            WHEN 1 THEN 'Right Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISRIGHTEYECLOSED || ''
        END AS 'zDetFace-Is Right Eye Closed',
        zDetFace.ZGAZECENTERX AS 'zDetFace-Gaze Center X',
        zDetFace.ZGAZECENTERY AS 'zDetFace-Gaze Center Y',
        CASE zDetFace.ZGAZETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGAZETYPE || ''
        END AS 'zDetFace-Face Gaze Type',
        CASE zDetFace.ZGLASSESTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eye Glasses-1'
            WHEN 2 THEN 'Sun Glasses-2'
            WHEN 3 THEN 'No Glasses-3'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGLASSESTYPE || ''
        END AS 'zDetFace-Eye Glasses Type',
        CASE zDetFace.ZEYEMAKEUPTYPE
            WHEN 0 THEN 'No Eye Makeup-0'
            WHEN 1 THEN 'Eye Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYEMAKEUPTYPE || ''
        END AS 'zDetFace-Eye Makeup Type',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number Key',
        zDetFace.ZGROUPINGIDENTIFIER AS 'zDetFace-Grouping ID',
        zDetFace.ZMASTERIDENTIFIER AS 'zDetFace-Master ID',
        zDetFace.ZQUALITY AS 'zDetFace-Quality',
        zDetFace.ZQUALITYMEASURE AS 'zDetFace-Quality Measure',
        zDetFace.ZSOURCEHEIGHT AS 'zDetFace-Source Height',
        zDetFace.ZSOURCEWIDTH AS 'zDetFace-Source Width',
        CASE zDetFace.ZASSETVISIBLE
            WHEN 0 THEN '0-Unknown-StillTesitng-0'
            WHEN 1 THEN '1-Unknown-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZASSETVISIBLE || ''
        END AS 'zDetFace-Asset Visible',
        CASE zDetFace.ZHIDDEN
            WHEN 0 THEN 'Not Hidden-0'
            WHEN 1 THEN 'Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHIDDEN || ''
        END AS 'zDetFace-Hidden/Asset Hidden',
        CASE zDetFace.ZISINTRASH
            WHEN 0 THEN 'Not In Trash-0'
            WHEN 1 THEN 'In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISINTRASH || ''
        END AS 'zDetFace-In Trash/Recently Deleted',
        CASE zDetFace.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDLOCALSTATE || ''
        END AS 'zDetFace-Cloud Local State',
        CASE zDetFace.ZTRAININGTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZTRAININGTYPE
        END AS 'zDetFace-Training Type',
        zDetFace.ZPOSEYAW AS 'zDetFace.Pose Yaw',
        zDetFace.ZBODYCENTERX AS 'zDetFace-Body Center X',
        zDetFace.ZBODYCENTERY AS 'zDetFace-Body Center Y',
        zDetFace.ZBODYHEIGHT AS 'zDetFace-Body Height',
        zDetFace.ZBODYWIDTH AS 'zDetFace-Body Width',
        zDetFace.ZROLL AS 'zDetFace-Roll',
        zDetFace.ZSIZE AS 'zDetFace-Size',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Sequence Number',
        zDetFace.ZBLURSCORE AS 'zDetFace-Blur Score',
        zDetFacePrint.ZFACEPRINTVERSION AS 'zDetFacePrint-Face Print Version',
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFaceGroup.ZPERSONBUILDERSTATE AS 'zDetFaceGroup-Person Builder State',
        zDetFaceGroup.ZUNNAMEDFACECOUNT AS 'zDetFaceGroup-UnNamed Face Count',
        zPerson.ZFACECOUNT AS 'zPerson-Face Count',       
        zDetFace.ZFACEALGORITHMVERSION AS 'zDetFace-Face Algorithm Version',
        zDetFace.ZADJUSTMENTVERSION AS 'zDetFace-Adjustment Version',       
        zPerson.ZINPERSONNAMINGMODEL AS 'zPerson-In Person Naming Model',
        zPerson.ZKEYFACEPICKSOURCE AS 'zPerson-Key Face Pick Source Key',
        zPerson.ZMANUALORDER AS 'zPerson-Manual Order Key',
        zPerson.ZQUESTIONTYPE AS 'zPerson-Question Type',
        zPerson.ZSUGGESTEDFORCLIENTTYPE AS 'zPerson-Suggested For Client Type',
        zPerson.ZMERGETARGETPERSON AS 'zPerson-Merge Target Person',
        CASE zPerson.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Person Not Synced with Cloud-0'
            WHEN 1 THEN 'Person Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDLOCALSTATE
        END AS 'zPerson-Cloud Local State',
        CASE zFaceCrop.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDLOCALSTATE || ''
        END AS 'zFaceCrop-Cloud Local State',
        CASE zFaceCrop.ZCLOUDTYPE
            WHEN 0 THEN 'Has Name-0'
            WHEN 5 THEN 'Has Face Key-5'
            WHEN 12 THEN '12-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDTYPE || ''
        END AS 'zFaceCrop-Cloud Type',
        CASE zPerson.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDDELETESTATE || ''
        END AS 'zPerson-Cloud Delete State',
        CASE zFaceCrop.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDDELETESTATE || ''
        END AS 'zFaceCrop-Cloud Delete State',
        zDetFace.Z_PK AS 'zDetFace-zPK',
        zDetFacePrint.ZFACE AS 'zDetFacePrint-Face Key',
        zPerson.ZKEYFACE AS 'zPerson-KeyFace=zDetFace-zPK',
        zFaceCrop.ZFACE AS 'zFaceCrop-Face Key',
        zPerson.Z_PK AS 'zPerson-zPK=zDetFace-Person',
        zDetFace.ZPERSONFORFACE AS 'zDetFace-PersonForFace= zPerson-zPK',
        zDetFace.ZPERSONFORTEMPORALDETECTEDFACES AS 'zDetFace-Person for Temporal Detected Faces= zPerson-zPK',
        zDetFace.ZPERSONFORTORSO AS 'zDetFace-PersonForTorso= zPerson-zPK',
        zDetFace.ZPERSONBEINGKEYFACE AS 'zDetFace-Person Being Key Face',         
        zFaceCrop.ZPERSON AS 'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key',	
        zDetFace.ZFACEPRINT AS 'zDetFace-Face Print',	
        zDetFacePrint.Z_PK AS 'zDetFacePrint-zPK',		
        zDetFace.ZFACECROP AS 'zDetFace-Face Crop',
        zFaceCrop.Z_PK AS 'zFaceCrop-zPK',           
        zDetFaceGroup.ZKEYFACE AS 'zDetFaceGroup-KeyFace= zDetFace-zPK',
        zDetFaceGroup.ZASSOCIATEDPERSON AS 'zDetFaceGroup-AssocPerson= zPerson-zPK',
        zPerson.ZASSOCIATEDFACEGROUP AS 'zPerson-Assoc Face Group Key',
        zDetFace.ZFACEGROUPBEINGKEYFACE AS 'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK',
        zDetFace.ZFACEGROUP AS 'zDetFace-FaceGroup= zDetFaceGroup-zPK',		
        zDetFaceGroup.Z_PK AS 'zDetFaceGroup-zPK',
        zPerson.ZSHAREPARTICIPANT AS 'zPerson-Share Participant= zSharePartic-zPK',		
        zDetFace.ZUUID AS 'zDetFace-UUID',
        zFaceCrop.ZUUID AS 'zFaceCrop-UUID',	
        zFaceCrop.ZINVALIDMERGECANDIDATEPERSONUUID AS 'zFaceCrop-Invalid Merge Candidate Person UUID',		
        zPerson.ZPERSONUUID AS 'zPerson-Person UUID',
        zPerson.ZPERSONURI AS 'zPerson-Person URI',		
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFace.ZASSETFORFACE AS 'zDetFace-AssetForFace= zAsset-zPK',
        zDetFace.ZASSETFORTORSO AS 'zDetFace-AssetForTorso= zAsset-zPK',
        zFaceCrop.ZASSET AS 'zFaceCrop-Asset Key',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
            LEFT JOIN ZDETECTEDFACE zDetFace ON zAsset.Z_PK = zDetFace.ZASSETFORFACE
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSONFORFACE
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP
        WHERE zDetFace.Z_PK > 0  
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            personcontactmatchingdictionary = ''
            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            facecropresourcedata_blob = ''

            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            if row[27] is not None:
                pathto = os.path.join(report_folder, 'zPerson-ContactMatchingDict_' + row[133] + '.plist')
                with open(pathto, 'ab') as wf:
                    wf.write(row[27])

                with open(pathto, 'rb') as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        personcontactmatchingdictionary = deserialized_plist

                    except (KeyError, ValueError, TypeError) as ex:
                        if str(ex).find("does not contain an '$archiver' key") >= 0:
                            logfunc('plist was Not an NSKeyedArchive ' + row[133])
                        else:
                            logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[133])

            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            if row[34] is not None:
                pathto = os.path.join(report_folder, 'FaceCropFor_' + row[131] + '.jpg')
                with open(pathto, 'wb') as file:
                    file.write(row[34])
                facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26],
                              personcontactmatchingdictionary,
                              row[28], row[29], row[30], row[31], row[32], row[33],
                              facecropresourcedata_blob,
                              row[35], row[36],
                              row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                              row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                              row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                              row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                              row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                              row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                              row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                              row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                              row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
                              row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
                              row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
                              row[132], row[133], row[134], row[135], row[136], row[137], row[138], row[139],
                              row[140], row[141], row[142]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        'zAsset-Directory-Path-7',
                        'zAsset-Filename-8',
                        'zAddAssetAttr- Original Filename-9',
                        'zCldMast- Original Filename-10',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-11',
                        'zAsset- Conversation= zGenAlbum_zPK-12',
                        ('zAsset-Trashed Date-13', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-14',
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-15',
                        'zAddAssetAttr-Imported by Bundle ID-16',
                        'zAddAssetAttr-Imported By Display Name-17',
                        'zCldMast-Imported by Bundle ID-18',
                        'zCldMast-Imported by Display Name-19',
                        'zAsset-Visibility State-20',
                        'zFaceCrop-Face Area Points-21',
                        'zAsset-Face Adjustment Version-22',
                        'zAddAssetAttr-Face_Regions-SeeRawDBData-23',
                        'zAddAssetAttr-Face Analysis Version-24',
                        'zDetFace-Asset For Temporal Detected Faces= zAsset-zPK-25',
                        'zDetFacePrint-Data-SeeRawDBData-26',
                        'zPerson-Contact Matching Dictionary-27',
                        'zPerson-Verified Type-28',
                        'zPerson-Display Name-29',
                        'zPerson-Full Name-30',
                        'zPerson-Cloud Verified Type-31',
                        'zFaceCrop-State-32',
                        'zFaceCrop-Type-33',
                        'zFaceCrop-Resource Data-34',
                        'zDetFace-Confirmed Face Crop Generation State-35',
                        'zDetFace-Manual-36',
                        'zDetFace-Detection Type-37',
                        'zPerson-Detection Type-38',
                        'zDetFace-VIP Model Type-39',
                        'zDetFace-Name Source-40',
                        'zDetFace-Cloud Name Source-41',
                        'zPerson-Merge Candidate Confidence-42',
                        'zPerson-Type-43',
                        'zPerson-Gender Type-44',
                        'zDetFace-Gender Type-45',
                        'zDetFace-Center X-46',
                        'zDetFace-Center Y-47',
                        'zPerson-Age Type Estimate-48',
                        'zDetFace-Age Type Estimate-49',
                        'zDetFace-Ethnicity Type-50',
                        'zDetFace-Skin Tone Type-51',
                        'zDetFace-Hair Type-52',
                        'zDetFace-Hair Color Type-53',
                        'zDetFace-Head Gear Type-54',
                        'zDetFace-Facial Hair Type-55',
                        'zDetFace-Has Face Mask-56',
                        'zDetFace-Pose Type-57',
                        'zDetFace-Face Expression Type-58',
                        'zDetFace-Has Smile-59',
                        'zDetFace-Smile Type-60',
                        'zDetFace-Lip Makeup Type-61',
                        'zDetFace-Eyes State-62',
                        'zDetFace-Is Left Eye Closed-63',
                        'zDetFace-Is Right Eye Closed-64',
                        'zDetFace-Gaze Center X-65',
                        'zDetFace-Gaze Center Y-66',
                        'zDetFace-Face Gaze Type-67',
                        'zDetFace-Eye Glasses Type-68',
                        'zDetFace-Eye Makeup Type-69',
                        'zDetFace-Cluster Squence Number Key-70',
                        'zDetFace-Grouping ID-71',
                        'zDetFace-Master ID-72',
                        'zDetFace-Quality-73',
                        'zDetFace-Quality Measure-74',
                        'zDetFace-Source Height-75',
                        'zDetFace-Source Width-76',
                        'zDetFace-Asset Visible-77',
                        'zDetFace-Hidden/Asset Hidden-78',
                        'zDetFace-In Trash/Recently Deleted-79',
                        'zDetFace-Cloud Local State-80',
                        'zDetFace-Training Type-81',
                        'zDetFace.Pose Yaw-82',
                        'zDetFace-Body Center X-83',
                        'zDetFace-Body Center Y-84',
                        'zDetFace-Body Height-85',
                        'zDetFace-Body Width-86',
                        'zDetFace-Roll-87',
                        'zDetFace-Size-88',
                        'zDetFace-Cluster Sequence Number-89',
                        'zDetFace-Blur Score-90',
                        'zDetFacePrint-Face Print Version-91',
                        'zDetFaceGroup-UUID-92',
                        'zDetFaceGroup-Person Builder State-93',
                        'zDetFaceGroup-UnNamed Face Count-94',
                        'zPerson-Face Count-95',
                        'zDetFace-Face Algorithm Version-96',
                        'zDetFace-Adjustment Version-97',
                        'zPerson-In Person Naming Model-98',
                        'zPerson-Key Face Pick Source Key-99',
                        'zPerson-Manual Order Key-100',
                        'zPerson-Question Type-101',
                        'zPerson-Suggested For Client Type-102',
                        'zPerson-Merge Target Person-103',
                        'zPerson-Cloud Local State-104',
                        'zFaceCrop-Cloud Local State-105',
                        'zFaceCrop-Cloud Type-106',
                        'zPerson-Cloud Delete State-107',
                        'zFaceCrop-Cloud Delete State-108',
                        'zDetFace-zPK-109',
                        'zDetFacePrint-Face Key-110',
                        'zPerson-KeyFace=zDetFace-zPK-111',
                        'zFaceCrop-Face Key-112',
                        'zPerson-zPK=zDetFace-Person-113',
                        'zDetFace-PersonForFace= zPerson-zPK-114',
                        'zDetFace-Person for Temporal Detected Faces= zPerson-zPK-115',
                        'zDetFace-PersonForTorso= zPerson-zPK-116',
                        'zDetFace-Person Being Key Face-117',
                        'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-118',
                        'zDetFace-Face Print-119',
                        'zDetFacePrint-zPK-120',
                        'zDetFace-Face Crop-121',
                        'zFaceCrop-zPK-122',
                        'zDetFaceGroup-KeyFace= zDetFace-zPK-123',
                        'zDetFaceGroup-AssocPerson= zPerson-zPK-124',
                        'zPerson-Assoc Face Group Key-125',
                        'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-126',
                        'zDetFace-FaceGroup= zDetFaceGroup-zPK-127',
                        'zDetFaceGroup-zPK-128',
                        'zPerson-Share Participant= zSharePartic-zPK-129',
                        'zDetFace-UUID-130',
                        'zFaceCrop-UUID-131',
                        'zFaceCrop-Invalid Merge Candidate Person UUID-132',
                        'zPerson-Person UUID-133',
                        'zPerson-Person URI-134',
                        'zDetFaceGroup-UUID-135',
                        'zDetFace-AssetForFace= zAsset-zPK-136',
                        'zDetFace-AssetForTorso= zAsset-zPK-137',
                        'zFaceCrop-Asset Key-138',
                        'zAsset-zPK-139',
                        'zAddAssetAttr-zPK-140',
                        'zAsset-UUID = store.cloudphotodb-141',
                        'zAddAssetAttr-Master Fingerprint-142')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif version.parse(iosversion) >= version.parse("18"):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',  
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE
            WHEN zAsset.ZFACEAREAPOINTS > 0 THEN 'Face Area Points Detected in zAsset'
            ELSE 'Face Area Points Not Detected in zAsset'
        END AS 'zFaceCrop-Face Area Points',
        zAsset.ZFACEADJUSTMENTVERSION AS 'zAsset-Face Adjustment Version',
        CASE
            WHEN zAddAssetAttr.ZFACEREGIONS > 0 THEN 'zAddAssetAttr-Face_Regions_has_Data'
            ELSE 'zAddAssetAttr-Face_Regions_has_NO-Data'
        END AS 'zAddAssetAttr-Face_Regions-SeeRawDBData',
        CASE zAddAssetAttr.ZHASPEOPLESCENEMIDORGREATERCONFIDENCE
            WHEN 0 THEN '0-Obs in iOS 18 still testing-0'
            WHEN 1 THEN '1-Obs in iOS 18 still testing-1'	
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZHASPEOPLESCENEMIDORGREATERCONFIDENCE || ''
        END AS 'zAddAssetAttr-Has_People_Scene Mid_Or_Greater_Confidence',
        zAddAssetAttr.ZFACEANALYSISVERSION AS 'zAddAssetAttr-Face Analysis Version',
        zDetFace.ZASSETFORTEMPORALDETECTEDFACES AS 'zDetFace-Asset For Temporal Detected Faces= zAsset-zPK',
        CASE
            WHEN zDetFacePrint.ZDATA > 0 THEN 'zDetFacePrint-Data_has_Data'
            ELSE 'zDetFacePrint-Data_NO-Data'
        END AS 'zDetFacePrint-Data-SeeRawDBData',
        zPerson.ZCONTACTMATCHINGDICTIONARY AS 'zPerson-Contact Matching Dictionary',
        CASE zPerson.ZVERIFIEDTYPE
            WHEN 0 THEN '0-Not-Verified'
            WHEN 1 THEN '1-Has_Contact Matching_Dictionary'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZVERIFIEDTYPE || ''
        END AS 'zPerson-Verified Type',
        zPerson.ZISMECONFIDENCE AS 'zPerson-Is_Me_Confidence',
        zPerson.ZDISPLAYNAME AS 'zPerson-Display Name',
        zPerson.ZFULLNAME AS 'zPerson-Full Name',
        CASE zPerson.ZCLOUDVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDVERIFIEDTYPE || ''
        END AS 'zPerson-Cloud Verified Type',
        CASE zFaceCrop.ZSTATE
            WHEN 5 THEN 'Validated-5'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZSTATE || ''
        END AS 'zFaceCrop-State',
        CASE zFaceCrop.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-Active'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZTYPE || ''
        END AS 'zFaceCrop-Type',
        zFaceCrop.ZRESOURCEDATA AS 'zFaceCrop-Resource Data',	
        CASE zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE || ''
        END AS 'zDetFace-Confirmed Face Crop Generation State',
        CASE zDetFace.ZMANUAL
            WHEN 0 THEN 'zDetFace-Auto Detected-0'
            WHEN 1 THEN 'zDetFace-Manually Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZMANUAL || ''
        END AS 'zDetFace-Manual',
        CASE zDetFace.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZDETECTIONTYPE || ''
        END AS 'zDetFace-Detection Type',
        CASE zPerson.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZDETECTIONTYPE || ''
        END AS 'zPerson-Detection Type',
        CASE zDetFace.ZVIPMODELTYPE
            WHEN 0 THEN 'Not VIP-0'
            WHEN 1 THEN 'VIP-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZVIPMODELTYPE || ''
        END AS 'zDetFace-VIP Model Type',
        CASE zDetFace.ZNAMESOURCE
            WHEN 0 THEN 'No Name Listed-0'
            WHEN 1 THEN '1-Face Crop-1'
            WHEN 2 THEN '2-Verified/Has-Person-URI'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZNAMESOURCE || ''
        END AS 'zDetFace-Name Source',
        CASE zDetFace.ZCLOUDNAMESOURCE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN '1-User Added Via Face Crop-1'
            WHEN 5 THEN '5-Asset Shared has Name'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDNAMESOURCE || ''
        END AS 'zDetFace-Cloud Name Source',
        zPerson.ZMERGECANDIDATECONFIDENCE AS 'zPerson-Merge Candidate Confidence',
        CASE zPerson.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZTYPE || ''
        END AS 'zPerson-Type',
        CASE zPerson.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZGENDERTYPE || ''
        END AS 'zPerson-Gender Type',
        CASE zDetFace.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGENDERTYPE || ''
        END AS 'zDetFace-Gender Type',
        zDetFace.ZCENTERX AS 'zDetFace-Center X',
        zDetFace.ZCENTERY AS 'zDetFace-Center Y',
        CASE zPerson.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZAGETYPE || ''
        END AS 'zPerson-Age Type Estimate',
        CASE zDetFace.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZAGETYPE || ''
        END AS 'zDetFace-Age Type Estimate',
        CASE zDetFace.ZETHNICITYTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/African American-1'
            WHEN 2 THEN 'White-2'
            WHEN 3 THEN 'Hispanic/Latino-3'
            WHEN 4 THEN 'Asian-4'
            WHEN 5 THEN 'Native Hawaiian/Other Pacific Islander-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZETHNICITYTYPE || ''
        END AS 'zDetFace-Ethnicity Type',
        CASE zDetFace.ZSKINTONETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Light-Pale White Skin Tone-1'
            WHEN 2 THEN 'White-Fair Skin Tone-2'
            WHEN 3 THEN 'Medium-White to Olive Skin Tone-3'
            WHEN 4 THEN 'Olive-Moderate Brown Skin Tone-4'
            WHEN 5 THEN 'Brown-Dark Brown Skin Tone-5'
            WHEN 6 THEN 'Black-Very Dark Brown to Black Skin Tone-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSKINTONETYPE || ''
        END AS 'zDetFace-Skin Tone Type',
        CASE zDetFace.ZHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            WHEN 6 THEN '6-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRTYPE || ''
        END AS 'zDetFace-Hair Type',
        CASE zDetFace.ZHAIRCOLORTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/Brown Hair Color-1'
            WHEN 2 THEN 'Brown/Blonde Hair Color-2'
            WHEN 3 THEN 'Brown/Red Hair Color-3'
            WHEN 4 THEN 'Red/White Hair Color-4'
            WHEN 5 THEN 'StillTesting/Artifical-5'
            WHEN 6 THEN 'White/Bald Hair Color-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRCOLORTYPE || ''
        END AS 'zDetFace-Hair Color Type',
        CASE zDetFace.ZHEADGEARTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-No Headgear'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHEADGEARTYPE || ''
        END AS 'zDetFace-Head Gear Type',
        CASE zDetFace.ZFACIALHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Clean Shaven Facial Hair Type-1'
            WHEN 2 THEN 'Beard Facial Hair Type-2'
            WHEN 3 THEN 'Goatee Facial Hair Type-3'
            WHEN 4 THEN 'Mustache Facial Hair Type-4'
            WHEN 5 THEN 'Stubble Facial Hair Type-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACIALHAIRTYPE || ''
        END AS 'zDetFace-Facial Hair Type',
        CASE zDetFace.ZHASFACEMASK
            WHEN 0 THEN 'No Mask-0'
            WHEN 1 THEN 'Has Mask-1'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASFACEMASK || ''
        END AS 'zDetFace-Has Face Mask',
        CASE zDetFace.ZPOSETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Face Frontal Pose-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN 'Face Profile Pose-3'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZPOSETYPE || ''
        END AS 'zDetFace-Pose Type',
        CASE zDetFace.ZFACEEXPRESSIONTYPE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN 'Disgusted/Angry-1'
            WHEN 2 THEN 'Suprised/Fearful-2'
            WHEN 3 THEN 'Neutral-3'
            WHEN 4 THEN 'Confident/Smirk-4'
            WHEN 5 THEN 'Happiness-5'
            WHEN 6 THEN 'Sadness-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACEEXPRESSIONTYPE || ''
        END AS 'zDetFace-Face Expression Type',
        CASE zDetFace.ZHASSMILE
            WHEN 0 THEN 'zDetFace No Smile-0'
            WHEN 1 THEN 'zDetFace Smile-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASSMILE || ''
        END AS 'zDetFace-Has Smile',
        CASE zDetFace.ZSMILETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'zDetFace Smile No Teeth-1'
            WHEN 2 THEN 'zDetFace Smile has Teeth-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSMILETYPE || ''
        END AS 'zDetFace-Smile Type',
        CASE zDetFace.ZLIPMAKEUPTYPE
            WHEN 0 THEN 'zDetFace No Lip Makeup-0'
            WHEN 1 THEN 'zDetFace Lip Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZLIPMAKEUPTYPE || ''
        END AS 'zDetFace-Lip Makeup Type',
        CASE zDetFace.ZEYESSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eyes Closed-1'
            WHEN 2 THEN 'Eyes Open-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYESSTATE || ''
        END AS 'zDetFace-Eyes State',
        CASE zDetFace.ZISLEFTEYECLOSED
            WHEN 0 THEN 'Left Eye Open-0'
            WHEN 1 THEN 'Left Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISLEFTEYECLOSED || ''
        END AS 'zDetFace-Is Left Eye Closed',
        CASE zDetFace.ZISRIGHTEYECLOSED
            WHEN 0 THEN 'Right Eye Open-0'
            WHEN 1 THEN 'Right Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISRIGHTEYECLOSED || ''
        END AS 'zDetFace-Is Right Eye Closed',
        zDetFace.ZGAZECENTERX AS 'zDetFace-Gaze Center X',
        zDetFace.ZGAZECENTERY AS 'zDetFace-Gaze Center Y',
        CASE zDetFace.ZGAZETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGAZETYPE || ''
        END AS 'zDetFace-Face Gaze Type',
        CASE zDetFace.ZGLASSESTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eye Glasses-1'
            WHEN 2 THEN 'Sun Glasses-2'
            WHEN 3 THEN 'No Glasses-3'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGLASSESTYPE || ''
        END AS 'zDetFace-Eye Glasses Type',
        CASE zDetFace.ZEYEMAKEUPTYPE
            WHEN 0 THEN 'No Eye Makeup-0'
            WHEN 1 THEN 'Eye Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYEMAKEUPTYPE || ''
        END AS 'zDetFace-Eye Makeup Type',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number Key',
        zDetFace.ZGROUPINGIDENTIFIER AS 'zDetFace-Grouping ID',
        zDetFace.ZMASTERIDENTIFIER AS 'zDetFace-Master ID',
        zDetFace.ZQUALITY AS 'zDetFace-Quality',
        zDetFace.ZQUALITYMEASURE AS 'zDetFace-Quality Measure',
        zDetFace.ZSOURCEHEIGHT AS 'zDetFace-Source Height',
        zDetFace.ZSOURCEWIDTH AS 'zDetFace-Source Width',
        CASE zDetFace.ZASSETVISIBLE
            WHEN 0 THEN '0-Unknown-StillTesitng-0'
            WHEN 1 THEN '1-Unknown-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZASSETVISIBLE || ''
        END AS 'zDetFace-Asset Visible',
        CASE zDetFace.ZHIDDEN
            WHEN 0 THEN 'Not Hidden-0'
            WHEN 1 THEN 'Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHIDDEN || ''
        END AS 'zDetFace-Hidden/Asset Hidden',
        CASE zDetFace.ZISINTRASH
            WHEN 0 THEN 'Not In Trash-0'
            WHEN 1 THEN 'In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISINTRASH || ''
        END AS 'zDetFace-In Trash/Recently Deleted',
        CASE zDetFace.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDLOCALSTATE || ''
        END AS 'zDetFace-Cloud Local State',
        CASE zDetFace.ZTRAININGTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZTRAININGTYPE
        END AS 'zDetFace-Training Type',
        zDetFace.ZPOSEYAW AS 'zDetFace.Pose Yaw',
        zDetFace.ZBODYCENTERX AS 'zDetFace-Body Center X',
        zDetFace.ZBODYCENTERY AS 'zDetFace-Body Center Y',
        zDetFace.ZBODYHEIGHT AS 'zDetFace-Body Height',
        zDetFace.ZBODYWIDTH AS 'zDetFace-Body Width',
        zDetFace.ZROLL AS 'zDetFace-Roll',
        zDetFace.ZSIZE AS 'zDetFace-Size',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Sequence Number',
        zDetFace.ZBLURSCORE AS 'zDetFace-Blur Score',
        zDetFacePrint.ZFACEPRINTVERSION AS 'zDetFacePrint-Face Print Version',
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFaceGroup.ZPERSONBUILDERSTATE AS 'zDetFaceGroup-Person Builder State',
        zDetFaceGroup.ZUNNAMEDFACECOUNT AS 'zDetFaceGroup-UnNamed Face Count',
        zPerson.ZFACECOUNT AS 'zPerson-Face Count',       
        zDetFace.ZFACEALGORITHMVERSION AS 'zDetFace-Face Algorithm Version',
        zDetFace.ZADJUSTMENTVERSION AS 'zDetFace-Adjustment Version',       
        zPerson.ZINPERSONNAMINGMODEL AS 'zPerson-In Person Naming Model',
        zPerson.ZKEYFACEPICKSOURCE AS 'zPerson-Key Face Pick Source Key',
        zPerson.ZMANUALORDER AS 'zPerson-Manual Order Key',
        zPerson.ZQUESTIONTYPE AS 'zPerson-Question Type',
        zPerson.ZSUGGESTEDFORCLIENTTYPE AS 'zPerson-Suggested For Client Type',
        zPerson.ZMERGETARGETPERSON AS 'zPerson-Merge Target Person',
        CASE zPerson.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Person Not Synced with Cloud-0'
            WHEN 1 THEN 'Person Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDLOCALSTATE
        END AS 'zPerson-Cloud Local State',
        CASE zFaceCrop.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDLOCALSTATE || ''
        END AS 'zFaceCrop-Cloud Local State',
        CASE zFaceCrop.ZCLOUDTYPE
            WHEN 0 THEN 'Has Name-0'
            WHEN 5 THEN 'Has Face Key-5'
            WHEN 12 THEN '12-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDTYPE || ''
        END AS 'zFaceCrop-Cloud Type',
        CASE zPerson.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDDELETESTATE || ''
        END AS 'zPerson-Cloud Delete State',
        CASE zFaceCrop.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDDELETESTATE || ''
        END AS 'zFaceCrop-Cloud Delete State',
        zDetFace.Z_PK AS 'zDetFace-zPK',
        zDetFacePrint.ZFACE AS 'zDetFacePrint-Face Key',
        zPerson.ZKEYFACE AS 'zPerson-KeyFace=zDetFace-zPK',
        zFaceCrop.ZFACE AS 'zFaceCrop-Face Key',
        zPerson.Z_PK AS 'zPerson-zPK=zDetFace-Person',
        zDetFace.ZPERSONFORFACE AS 'zDetFace-PersonForFace= zPerson-zPK',
        zDetFace.ZPERSONFORTEMPORALDETECTEDFACES AS 'zDetFace-Person for Temporal Detected Faces= zPerson-zPK',
        zDetFace.ZPERSONFORTORSO AS 'zDetFace-PersonForTorso= zPerson-zPK',
        zDetFace.ZPERSONBEINGKEYFACE AS 'zDetFace-Person Being Key Face',         
        zFaceCrop.ZPERSON AS 'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key',	
        zDetFace.ZFACEPRINT AS 'zDetFace-Face Print',	
        zDetFacePrint.Z_PK AS 'zDetFacePrint-zPK',		
        zDetFace.ZFACECROP AS 'zDetFace-Face Crop',
        zFaceCrop.Z_PK AS 'zFaceCrop-zPK',           
        zDetFaceGroup.ZKEYFACE AS 'zDetFaceGroup-KeyFace= zDetFace-zPK',
        zDetFaceGroup.ZASSOCIATEDPERSON AS 'zDetFaceGroup-AssocPerson= zPerson-zPK',
        zPerson.ZASSOCIATEDFACEGROUP AS 'zPerson-Assoc Face Group Key',
        zDetFace.ZFACEGROUPBEINGKEYFACE AS 'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK',
        zDetFace.ZFACEGROUP AS 'zDetFace-FaceGroup= zDetFaceGroup-zPK',		
        zDetFaceGroup.Z_PK AS 'zDetFaceGroup-zPK',
        zPerson.ZSHAREPARTICIPANT AS 'zPerson-Share Participant= zSharePartic-zPK',		
        zDetFace.ZUUID AS 'zDetFace-UUID',
        zFaceCrop.ZUUID AS 'zFaceCrop-UUID',	
        zFaceCrop.ZINVALIDMERGECANDIDATEPERSONUUID AS 'zFaceCrop-Invalid Merge Candidate Person UUID',		
        zPerson.ZPERSONUUID AS 'zPerson-Person UUID',
        zPerson.ZPERSONURI AS 'zPerson-Person URI',		
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFace.ZASSETFORFACE AS 'zDetFace-AssetForFace= zAsset-zPK',
        zDetFace.ZASSETFORTORSO AS 'zDetFace-AssetForTorso= zAsset-zPK',
        zFaceCrop.ZASSET AS 'zFaceCrop-Asset Key',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
            LEFT JOIN ZDETECTEDFACE zDetFace ON zAsset.Z_PK = zDetFace.ZASSETFORFACE
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSONFORFACE
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP
        WHERE zDetFace.Z_PK > 0  
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            personcontactmatchingdictionary = ''
            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            facecropresourcedata_blob = ''

            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            if row[28] is not None:
                pathto = os.path.join(report_folder, 'zPerson-ContactMatchingDict_' + row[135] + '.plist')
                with open(pathto, 'ab') as wf:
                    wf.write(row[28])

                with open(pathto, 'rb') as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        personcontactmatchingdictionary = deserialized_plist

                    except (KeyError, ValueError, TypeError) as ex:
                        if str(ex).find("does not contain an '$archiver' key") >= 0:
                            logfunc('plist was Not an NSKeyedArchive ' + row[135])
                        else:
                            logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[135])

            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            if row[36] is not None:
                pathto = os.path.join(report_folder, 'FaceCropFor_' + row[133] + '.jpg')
                with open(pathto, 'wb') as file:
                    file.write(row[36])
                facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                            row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                            row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                            personcontactmatchingdictionary,
                            row[29], row[30], row[31], row[32], row[33], row[34], row[35],
                            facecropresourcedata_blob,
                            row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                            row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                            row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                            row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                            row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                            row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                            row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                            row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                            row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
                            row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
                            row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
                            row[132], row[133], row[134], row[135], row[136], row[137], row[138], row[139],
                            row[140], row[141], row[142], row[143], row[144], row[145]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        'zAsset-Directory-Path-7',
                        'zAsset-Filename-8',
                        'zAddAssetAttr- Original Filename-9',
                        'zCldMast- Original Filename-10',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-11',
                        'zAsset- Conversation= zGenAlbum_zPK-12',
                        ('zAsset-Trashed Date-13', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-14',
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-15',
                        'zAddAssetAttr-Imported by Bundle ID-16',
                        'zAddAssetAttr-Imported By Display Name-17',
                        'zCldMast-Imported by Bundle ID-18',
                        'zCldMast-Imported by Display Name-19',
                        'zAsset-Visibility State-20',
                        'zFaceCrop-Face Area Points-21',
                        'zAddAssetAttr-Has_People_Scene Mid_Or_Greater_Confidence-22',
                        'zAsset-Face Adjustment Version-23',
                        'zAddAssetAttr-Face_Regions-SeeRawDBData-24',
                        'zAddAssetAttr-Face Analysis Version-25',
                        'zDetFace-Asset For Temporal Detected Faces= zAsset-zPK-26',
                        'zDetFacePrint-Data-SeeRawDBData-27',
                        'zPerson-Contact Matching Dictionary-28',
                        'zPerson-Verified Type-29',
                        'zPerson-Is_Me_Confidence-30',
                        'zPerson-Display Name-31',
                        'zPerson-Full Name-32',
                        'zPerson-Cloud Verified Type-33',
                        'zFaceCrop-State-34',
                        'zFaceCrop-Type-35',
                        'zFaceCrop-Resource Data-36',
                        'zDetFace-Confirmed Face Crop Generation State-37',
                        'zDetFace-Manual-38',
                        'zDetFace-Detection Type-39',
                        'zPerson-Detection Type-40',
                        'zDetFace-VIP Model Type-41',
                        'zDetFace-Name Source-42',
                        'zDetFace-Cloud Name Source-43',
                        'zPerson-Merge Candidate Confidence-44',
                        'zPerson-Type-45',
                        'zPerson-Gender Type-46',
                        'zDetFace-Gender Type-47',
                        'zDetFace-Center X-48',
                        'zDetFace-Center Y-49',
                        'zPerson-Age Type Estimate-50',
                        'zDetFace-Age Type Estimate-51',
                        'zDetFace-Ethnicity Type-52',
                        'zDetFace-Skin Tone Type-53',
                        'zDetFace-Hair Type-54',
                        'zDetFace-Hair Color Type-55',
                        'zDetFace-Head Gear Type-56',
                        'zDetFace-Facial Hair Type-57',
                        'zDetFace-Has Face Mask-58',
                        'zDetFace-Pose Type-59',
                        'zDetFace-Face Expression Type-60',
                        'zDetFace-Has Smile-61',
                        'zDetFace-Smile Type-62',
                        'zDetFace-Lip Makeup Type-63',
                        'zDetFace-Eyes State-64',
                        'zDetFace-Is Left Eye Closed-65',
                        'zDetFace-Is Right Eye Closed-66',
                        'zDetFace-Gaze Center X-67',
                        'zDetFace-Gaze Center Y-68',
                        'zDetFace-Face Gaze Type-69',
                        'zDetFace-Eye Glasses Type-70',
                        'zDetFace-Eye Makeup Type-71',
                        'zDetFace-Cluster Squence Number Key-72',
                        'zDetFace-Grouping ID-73',
                        'zDetFace-Master ID-74',
                        'zDetFace-Quality-75',
                        'zDetFace-Quality Measure-76',
                        'zDetFace-Source Height-77',
                        'zDetFace-Source Width-78',
                        'zDetFace-Asset Visible-79',
                        'zDetFace-Hidden/Asset Hidden-80',
                        'zDetFace-In Trash/Recently Deleted-81',
                        'zDetFace-Cloud Local State-82',
                        'zDetFace-Training Type-83',
                        'zDetFace.Pose Yaw-84',
                        'zDetFace-Body Center X-85',
                        'zDetFace-Body Center Y-86',
                        'zDetFace-Body Height-87',
                        'zDetFace-Body Width-88',
                        'zDetFace-Roll-89',
                        'zDetFace-Size-90',
                        'zDetFace-Cluster Sequence Number-91',
                        'zDetFace-Blur Score-92',
                        'zDetFacePrint-Face Print Version-93',
                        'zDetFaceGroup-UUID-94',
                        'zDetFaceGroup-Person Builder State-95',
                        'zDetFaceGroup-UnNamed Face Count-96',
                        'zPerson-Face Count-97',
                        'zDetFace-Face Algorithm Version-98',
                        'zDetFace-Adjustment Version-99',
                        'zPerson-In Person Naming Model-100',
                        'zPerson-Key Face Pick Source Key-101',
                        'zPerson-Manual Order Key-102',
                        'zPerson-Question Type-103',
                        'zPerson-Suggested For Client Type-104',
                        'zPerson-Merge Target Person-105',
                        'zPerson-Cloud Local State-106',
                        'zFaceCrop-Cloud Local State-107',
                        'zFaceCrop-Cloud Type-108',
                        'zPerson-Cloud Delete State-109',
                        'zFaceCrop-Cloud Delete State-110',
                        'zDetFace-zPK-111',
                        'zDetFacePrint-Face Key-112',
                        'zPerson-KeyFace=zDetFace-zPK-113',
                        'zFaceCrop-Face Key-114',
                        'zPerson-zPK=zDetFace-Person-115',
                        'zDetFace-PersonForFace= zPerson-zPK-116',
                        'zDetFace-Person for Temporal Detected Faces= zPerson-zPK-117',
                        'zDetFace-PersonForTorso= zPerson-zPK-118',
                        'zDetFace-Person Being Key Face-119',
                        'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-120',
                        'zDetFace-Face Print-121',
                        'zDetFacePrint-zPK-122',
                        'zDetFace-Face Crop-123',
                        'zFaceCrop-zPK-124',
                        'zDetFaceGroup-KeyFace= zDetFace-zPK-125',
                        'zDetFaceGroup-AssocPerson= zPerson-zPK-126',
                        'zPerson-Assoc Face Group Key-127',
                        'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-128',
                        'zDetFace-FaceGroup= zDetFaceGroup-zPK-129',
                        'zDetFaceGroup-zPK-130',
                        'zPerson-Share Participant= zSharePartic-zPK-131',
                        'zDetFace-UUID-132',
                        'zFaceCrop-UUID-133',
                        'zFaceCrop-Invalid Merge Candidate Person UUID-134',
                        'zPerson-Person UUID-135',
                        'zPerson-Person URI-136',
                        'zDetFaceGroup-UUID-137',
                        'zDetFace-AssetForFace= zAsset-zPK-138',
                        'zDetFace-AssetForTorso= zAsset-zPK-139',
                        'zFaceCrop-Asset Key-140',
                        'zAsset-zPK-141',
                        'zAddAssetAttr-zPK-142',
                        'zAsset-UUID = store.cloudphotodb-143',
                        'zAddAssetAttr-Original Stable Hash-144',
                        'zAddAssetAttr.Adjusted Stable Hash-145')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path
