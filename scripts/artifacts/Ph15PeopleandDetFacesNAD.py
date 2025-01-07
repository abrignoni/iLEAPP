__artifacts_v2__ = {
    'Ph15_1PeopleFacesNADPhDaPsql': {
        'name': 'Ph15.1-People & Faces NAD-PhDaPsql',
        'description': 'Parses data from PhotoData-Photos.sqlite for people - detected faces - face crop data.'
                       ' The results may contain multiple records per ZASSET table Z_PK value and supports iOS 14-18.',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-G-People_Faces_Data',
        'notes': '',
        'paths': ('*/PhotoData/Photos.sqlite*',),
        "output_types": ["standard", "tsv", "none"]
    },
    'Ph15_2PeopleFacesNADSyndPL': {
        'name': 'Ph15.2-People & Faces NAD-SyndPL',
        'description': 'Parses data from Syndication.photoslibrary-database-Photos.sqlite for'
                       ' people - detected faces - face crop data. The results may contain multiple records'
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
def Ph15_1PeopleFacesNADPhDaPsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
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
        zDetFace.ZASSET AS 'zDetFace-AssetForFace= zAsset-zPK',
        zFaceCrop.ZASSET AS 'zFaceCrop-Asset Key',
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
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID'      
        FROM ZDETECTEDFACE zDetFace
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSON
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP  
        ORDER BY zDetFace.Z_PK
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            personcontactmatchingdictionary = ''
            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            facecropresourcedata_blob = ''

            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            if row[3] is not None:
                pathto = os.path.join(report_folder, 'zPerson-ContactMatchingDict_' + row[89] + '.plist')
                with open(pathto, 'ab') as wf:
                    wf.write(row[3])

                with open(pathto, 'rb') as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        personcontactmatchingdictionary = deserialized_plist

                    except (KeyError, ValueError, TypeError) as ex:
                        if str(ex).find("does not contain an '$archiver' key") >= 0:
                            logfunc('plist was Not an NSKeyedArchive ' + row[89])
                        else:
                            logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[89])

            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            if row[10] is not None:
                pathto = os.path.join(report_folder, 'FaceCropFor_' + row[87] + '.jpg')
                with open(pathto, 'wb') as file:
                    file.write(row[10])
                facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

            data_list.append((row[0], row[1], row[2],
                            personcontactmatchingdictionary,
                            row[4], row[5], row[6], row[7], row[8], row[9],
                            facecropresourcedata_blob,
                            row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                            row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                            row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                            row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                            row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                            row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                            row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                            row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                            row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                            row[91]))

        data_headers = ('zDetFace-AssetForFace= zAsset-zPK-0',
                        'zFaceCrop-Asset Key-1',
                        'zDetFacePrint-Data-SeeRawDBData-2',
                        'zPerson-Contact Matching Dictionary-3',
                        'zPerson-Verified Type-4',
                        'zPerson-Display Name-5',
                        'zPerson-Full Name-6',
                        'zPerson-Cloud Verified Type-7',
                        'zFaceCrop-State-8',
                        'zFaceCrop-Type-9',
                        'zFaceCrop-Resource Data-10',
                        'zDetFace-Confirmed Face Crop Generation State-11',
                        'zDetFace-Manual-12',
                        'zDetFace-VIP Model Type-13',
                        'zDetFace-Name Source-14',
                        'zDetFace-Cloud Name Source-15',
                        'zPerson-Type-16',
                        'zPerson-Gender Type-17',
                        'zDetFace-Gender Type-18',
                        'zDetFace-Center X-19',
                        'zDetFace-Center Y-20',
                        'zPerson-Age Type Estimate-21',
                        'zDetFace-Age Type Estimate-22',
                        'zDetFace-Hair Color Type-23',
                        'zDetFace-Facial Hair Type-24',
                        'zDetFace-Has Smile-25',
                        'zDetFace-Smile Type-26',
                        'zDetFace-Lip Makeup Type-27',
                        'zDetFace-Eyes State-28',
                        'zDetFace-Is Left Eye Closed-29',
                        'zDetFace-Is Right Eye Closed-30',
                        'zDetFace-Eye Glasses Type-31',
                        'zDetFace-Eye Makeup Type-32',
                        'zDetFace-Cluster Sequence Number Key-33',
                        'zDetFace-Grouping ID-34',
                        'zDetFace-Master ID-35',
                        'zDetFace-Quality-36',
                        'zDetFace-Quality Measure-37',
                        'zDetFace-Source Height-38',
                        'zDetFace-Source Width-39',
                        'zDetFace-Asset Visible-40',
                        'zDetFace-Hidden/Asset Hidden-41',
                        'zDetFace-In Trash/Recently Deleted-42',
                        'zDetFace-Cloud Local State-43',
                        'zDetFace-Training Type-44',
                        'zDetFace.Pose Yaw-45',
                        'zDetFace-Roll-46',
                        'zDetFace-Size-47',
                        'zDetFace-Cluster Sequence Number-48',
                        'zDetFace-Blur Score-49',
                        'zDetFacePrint-Face Print Version-50',
                        'zDetFaceGroup-UUID-51',
                        'zDetFaceGroup-Person Builder State-52',
                        'zDetFaceGroup-UnNamed Face Count-53',
                        'zPerson-Face Count-54',
                        'zDetFace-Face Algorithm Version-55',
                        'zDetFace-Adjustment Version-56',
                        'zPerson-In Person Naming Model-57',
                        'zPerson-Key Face Pick Source Key-58',
                        'zPerson-Manual Order Key-59',
                        'zPerson-Question Type-60',
                        'zPerson-Suggested For Client Type-61',
                        'zPerson-Merge Target Person-62',
                        'zPerson-Cloud Local State-63',
                        'zFaceCrop-Cloud Local State-64',
                        'zFaceCrop-Cloud Type-65',
                        'zPerson-Cloud Delete State-66',
                        'zFaceCrop-Cloud Delete State-67',
                        'zDetFace-zPK-68',
                        'zDetFacePrint-Face Key-69',
                        'zPerson-KeyFace=zDetFace-zPK-70',
                        'zFaceCrop-Face Key-71',
                        'zPerson-zPK=zDetFace-Person-72',
                        'zDetFace-PersonForFace= zPerson-zPK-73',
                        'zDetFace-Person Being Key Face-74',
                        'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-75',
                        'zDetFace-Face Print-76',
                        'zDetFacePrint-zPK-77',
                        'zDetFace-Face Crop-78',
                        'zFaceCrop-zPK-79',
                        'zDetFaceGroup-KeyFace= zDetFace-zPK-80',
                        'zDetFaceGroup-AssocPerson= zPerson-zPK-81',
                        'zPerson-Assoc Face Group Key-82',
                        'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-83',
                        'zDetFace-FaceGroup= zDetFaceGroup-zPK-84',
                        'zDetFaceGroup-zPK-85',
                        'zDetFace-UUID-86',
                        'zFaceCrop-UUID-87',
                        'zFaceCrop-Invalid Merge Candidate Person UUID-88',
                        'zPerson-Person UUID-89',
                        'zPerson-Person URI-90',
                        'zDetFaceGroup-UUID-91')
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
        zDetFace.ZASSET AS 'zDetFace-AssetForFace= zAsset-zPK',
        zFaceCrop.ZASSET AS 'zFaceCrop-Asset Key',
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
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID'      
        FROM ZDETECTEDFACE zDetFace
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSON
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP  
        ORDER BY zDetFace.Z_PK
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            personcontactmatchingdictionary = ''
            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            facecropresourcedata_blob = ''

            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            if row[3] is not None:
                pathto = os.path.join(report_folder, 'zPerson-ContactMatchingDict_' + row[105] + '.plist')
                with open(pathto, 'ab') as wf:
                    wf.write(row[3])

                with open(pathto, 'rb') as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        personcontactmatchingdictionary = deserialized_plist

                    except (KeyError, ValueError, TypeError) as ex:
                        if str(ex).find("does not contain an '$archiver' key") >= 0:
                            logfunc('plist was Not an NSKeyedArchive ' + row[105])
                        else:
                            logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[105])

            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            if row[10] is not None:
                pathto = os.path.join(report_folder, 'FaceCropFor_' + row[103] + '.jpg')
                with open(pathto, 'wb') as file:
                    file.write(row[10])
                facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

            data_list.append((row[0], row[1], row[2],
                            personcontactmatchingdictionary,
                            row[4], row[5], row[6], row[7], row[8], row[9],
                            facecropresourcedata_blob,
                            row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                            row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                            row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                            row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                            row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                            row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                            row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                            row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                            row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                            row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                            row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107]))

        data_headers = ('zDetFace-AssetForFace= zAsset-zPK-0',
                        'zFaceCrop-Asset Key-1',
                        'zDetFacePrint-Data-SeeRawDBData-2',
                        'zPerson-Contact Matching Dictionary-3',
                        'zPerson-Verified Type-4',
                        'zPerson-Display Name-5',
                        'zPerson-Full Name-6',
                        'zPerson-Cloud Verified Type-7',
                        'zFaceCrop-State-8',
                        'zFaceCrop-Type-9',
                        'zFaceCrop-Resource Data-10',
                        'zDetFace-Confirmed Face Crop Generation State-11',
                        'zDetFace-Manual-12',
                        'zDetFace-Detection Type-13',
                        'zPerson-Detection Type-14',
                        'zDetFace-VIP Model Type-15',
                        'zDetFace-Name Source-16',
                        'zDetFace-Cloud Name Source-17',
                        'zPerson-Type-18',
                        'zPerson-Gender Type-19',
                        'zDetFace-Gender Type-20',
                        'zDetFace-Center X-21',
                        'zDetFace-Center Y-22',
                        'zPerson-Age Type Estimate-23',
                        'zDetFace-Age Type Estimate-24',
                        'zDetFace-Ethnicity Type-25',
                        'zDetFace-Skin Tone Type-26',
                        'zDetFace-Hair Type-27',
                        'zDetFace-Hair Color Type-28',
                        'zDetFace-Head Gear Type-29',
                        'zDetFace-Facial Hair Type-30',
                        'zDetFace-Has Face Mask-31',
                        'zDetFace-Pose Type-32',
                        'zDetFace-Face Expression Type-33',
                        'zDetFace-Has Smile-34',
                        'zDetFace-Smile Type-35',
                        'zDetFace-Lip Makeup Type-36',
                        'zDetFace-Eyes State-37',
                        'zDetFace-Is Left Eye Closed-38',
                        'zDetFace-Is Right Eye Closed-39',
                        'zDetFace-Gaze Center X-40',
                        'zDetFace-Gaze Center Y-41',
                        'zDetFace-Face Gaze Type-42',
                        'zDetFace-Eye Glasses Type-43',
                        'zDetFace-Eye Makeup Type-44',
                        'zDetFace-Cluster Squence Number Key-45',
                        'zDetFace-Grouping ID-46',
                        'zDetFace-Master ID-47',
                        'zDetFace-Quality-48',
                        'zDetFace-Quality Measure-49',
                        'zDetFace-Source Height-50',
                        'zDetFace-Source Width-51',
                        'zDetFace-Asset Visible-52',
                        'zDetFace-Hidden/Asset Hidden-53',
                        'zDetFace-In Trash/Recently Deleted-54',
                        'zDetFace-Cloud Local State-55',
                        'zDetFace-Training Type-56',
                        'zDetFace.Pose Yaw-57',
                        'zDetFace-Body Center X-58',
                        'zDetFace-Body Center Y-59',
                        'zDetFace-Body Height-60',
                        'zDetFace-Body Width-61',
                        'zDetFace-Roll-62',
                        'zDetFace-Size-63',
                        'zDetFace-Cluster Squence Number-64',
                        'zDetFace-Blur Score-65',
                        'zDetFacePrint-Face Print Version-66',
                        'zDetFaceGroup-UUID-67',
                        'zDetFaceGroup-Person Builder State-68',
                        'zDetFaceGroup-UnNamed Face Count-69',
                        'zPerson-Face Count-70',
                        'zDetFace-Face Algorithm Version-71',
                        'zDetFace-Adjustment Version-72',
                        'zPerson-In Person Naming Model-73',
                        'zPerson-Key Face Pick Source Key-74',
                        'zPerson-Manual Order Key-75',
                        'zPerson-Question Type-76',
                        'zPerson-Suggested For Client Type-77',
                        'zPerson-Merge Target Person-78',
                        'zPerson-Cloud Local State-79',
                        'zFaceCrop-Cloud Local State-80',
                        'zFaceCrop-Cloud Type-81',
                        'zPerson-Cloud Delete State-82',
                        'zFaceCrop-Cloud Delete State-83',
                        'zDetFace-zPK-84',
                        'zDetFacePrint-Face Key-85',
                        'zPerson-KeyFace=zDetFace-zPK-86',
                        'zFaceCrop-Face Key-87',
                        'zPerson-zPK=zDetFace-Person-88',
                        'zDetFace-PersonForFace= zPerson-zPK-89',
                        'zDetFace-Person Being Key Face-90',
                        'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-91',
                        'zDetFace-Face Print-92',
                        'zDetFacePrint-zPK-93',
                        'zDetFace-Face Crop-94',
                        'zFaceCrop-zPK-95',
                        'zDetFaceGroup-KeyFace= zDetFace-zPK-96',
                        'zDetFaceGroup-AssocPerson= zPerson-zPK-97',
                        'zPerson-Assoc Face Group Key-98',
                        'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-99',
                        'zDetFace-FaceGroup= zDetFaceGroup-zPK-100',
                        'zDetFaceGroup-zPK-101',
                        'zDetFace-UUID-102',
                        'zFaceCrop-UUID-103',
                        'zFaceCrop-Invalid Merge Canidate Person UUID-104',
                        'zPerson-Person UUID-105',
                        'zPerson-Person URI-106',
                        'zDetFaceGroup-UUID-107')
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
        zDetFace.ZASSET AS 'zDetFace-AssetForFace= zAsset-zPK',
        zFaceCrop.ZASSET AS 'zFaceCrop-Asset Key',
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
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID'      
        FROM ZDETECTEDFACE zDetFace
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSON
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP  
        ORDER BY zDetFace.Z_PK
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            personcontactmatchingdictionary = ''
            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            facecropresourcedata_blob = ''

            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            if row[3] is not None:
                pathto = os.path.join(report_folder, 'zPerson-ContactMatchingDict_' + row[107] + '.plist')
                with open(pathto, 'ab') as wf:
                    wf.write(row[3])

                with open(pathto, 'rb') as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        personcontactmatchingdictionary = deserialized_plist

                    except (KeyError, ValueError, TypeError) as ex:
                        if str(ex).find("does not contain an '$archiver' key") >= 0:
                            logfunc('plist was Not an NSKeyedArchive ' + row[107])
                        else:
                            logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[107])

            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            if row[10] is not None:
                pathto = os.path.join(report_folder, 'FaceCropFor_' + row[105] + '.jpg')
                with open(pathto, 'wb') as file:
                    file.write(row[10])
                facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

            data_list.append((row[0], row[1], row[2],
                            personcontactmatchingdictionary,
                            row[4], row[5], row[6], row[7], row[8], row[9],
                            facecropresourcedata_blob,
                            row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                            row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                            row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                            row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                            row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                            row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                            row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                            row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                            row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                            row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                            row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                            row[108], row[109]))

        data_headers = ('zDetFace-AssetForFace= zAsset-zPK-0',
                        'zFaceCrop-Asset Key-1',
                        'zDetFacePrint-Data-SeeRawDBData-2',
                        'zPerson-Contact Matching Dictionary-3',
                        'zPerson-Verified Type-4',
                        'zPerson-Display Name-5',
                        'zPerson-Full Name-6',
                        'zPerson-Cloud Verified Type-7',
                        'zFaceCrop-State-8',
                        'zFaceCrop-Type-9',
                        'zFaceCrop-Resource Data-10',
                        'zDetFace-Confirmed Face Crop Generation State-11',
                        'zDetFace-Manual-12',
                        'zDetFace-Detection Type-13',
                        'zPerson-Detection Type-14',
                        'zDetFace-VIP Model Type-15',
                        'zDetFace-Name Source-16',
                        'zDetFace-Cloud Name Source-17',
                        'zPerson-Merge Candidate Confidence-18',
                        'zPerson-Type-19',
                        'zPerson-Gender Type-20',
                        'zDetFace-Gender Type-21',
                        'zDetFace-Center X-22',
                        'zDetFace-Center Y-23',
                        'zPerson-Age Type Estimate-24',
                        'zDetFace-Age Type Estimate-25',
                        'zDetFace-Ethnicity Type-26',
                        'zDetFace-Skin Tone Type-27',
                        'zDetFace-Hair Type-28',
                        'zDetFace-Hair Color Type-29',
                        'zDetFace-Head Gear Type-30',
                        'zDetFace-Facial Hair Type-31',
                        'zDetFace-Has Face Mask-32',
                        'zDetFace-Pose Type-33',
                        'zDetFace-Face Expression Type-34',
                        'zDetFace-Has Smile-35',
                        'zDetFace-Smile Type-36',
                        'zDetFace-Lip Makeup Type-37',
                        'zDetFace-Eyes State-38',
                        'zDetFace-Is Left Eye Closed-39',
                        'zDetFace-Is Right Eye Closed-40',
                        'zDetFace-Gaze Center X-41',
                        'zDetFace-Gaze Center Y-42',
                        'zDetFace-Face Gaze Type-43',
                        'zDetFace-Eye Glasses Type-44',
                        'zDetFace-Eye Makeup Type-45',
                        'zDetFace-Cluster Squence Number Key-46',
                        'zDetFace-Grouping ID-47',
                        'zDetFace-Master ID-48',
                        'zDetFace-Quality-49',
                        'zDetFace-Quality Measure-50',
                        'zDetFace-Source Height-51',
                        'zDetFace-Source Width-52',
                        'zDetFace-Asset Visible-53',
                        'zDetFace-Hidden/Asset Hidden-54',
                        'zDetFace-In Trash/Recently Deleted-55',
                        'zDetFace-Cloud Local State-56',
                        'zDetFace-Training Type-57',
                        'zDetFace.Pose Yaw-58',
                        'zDetFace-Body Center X-59',
                        'zDetFace-Body Center Y-60',
                        'zDetFace-Body Height-61',
                        'zDetFace-Body Width-62',
                        'zDetFace-Roll-63',
                        'zDetFace-Size-64',
                        'zDetFace-Cluster Sequence Number-65',
                        'zDetFace-Blur Score-66',
                        'zDetFacePrint-Face Print Version-67',
                        'zDetFaceGroup-UUID-68',
                        'zDetFaceGroup-Person Builder State-69',
                        'zDetFaceGroup-UnNamed Face Count-70',
                        'zPerson-Face Count-71',
                        'zDetFace-Face Algorithm Version-72',
                        'zDetFace-Adjustment Version-73',
                        'zPerson-In Person Naming Model-74',
                        'zPerson-Key Face Pick Source Key-75',
                        'zPerson-Manual Order Key-76',
                        'zPerson-Question Type-77',
                        'zPerson-Suggested For Client Type-78',
                        'zPerson-Merge Target Person-79',
                        'zPerson-Cloud Local State-80',
                        'zFaceCrop-Cloud Local State-81',
                        'zFaceCrop-Cloud Type-82',
                        'zPerson-Cloud Delete State-83',
                        'zFaceCrop-Cloud Delete State-84',
                        'zDetFace-zPK-85',
                        'zDetFacePrint-Face Key-86',
                        'zPerson-KeyFace=zDetFace-zPK-87',
                        'zFaceCrop-Face Key-88',
                        'zPerson-zPK=zDetFace-Person-89',
                        'zDetFace-PersonForFace= zPerson-zPK-90',
                        'zDetFace-Person Being Key Face-91',
                        'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-92',
                        'zDetFace-Face Print-93',
                        'zDetFacePrint-zPK-94',
                        'zDetFace-Face Crop-95',
                        'zFaceCrop-zPK-96',
                        'zDetFaceGroup-KeyFace= zDetFace-zPK-97',
                        'zDetFaceGroup-AssocPerson= zPerson-zPK-98',
                        'zPerson-Assoc Face Group Key-99',
                        'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-100',
                        'zDetFace-FaceGroup= zDetFaceGroup-zPK-101',
                        'zDetFaceGroup-zPK-102',
                        'zPerson-Share Participant= zSharePartic-zPK-103',
                        'zDetFace-UUID-104',
                        'zFaceCrop-UUID-105',
                        'zFaceCrop-Invalid Merge Candidate Person UUID-106',
                        'zPerson-Person UUID-107',
                        'zPerson-Person URI-108',
                        'zDetFaceGroup-UUID-109')
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
        zDetFace.ZASSETFORFACE AS 'zDetFace-AssetForFace= zAsset-zPK',
        zDetFace.ZASSETFORTORSO AS 'zDetFace-AssetForTorso= zAsset-zPK',
        zFaceCrop.ZASSET AS 'zFaceCrop-Asset Key',        
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
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID'      
        FROM ZDETECTEDFACE zDetFace
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSONFORFACE
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP  
        ORDER BY zDetFace.Z_PK
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            personcontactmatchingdictionary = ''
            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            facecropresourcedata_blob = ''

            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            if row[5] is not None:
                pathto = os.path.join(report_folder, 'zPerson-ContactMatchingDict_' + row[111] + '.plist')
                with open(pathto, 'ab') as wf:
                    wf.write(row[5])

                with open(pathto, 'rb') as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        personcontactmatchingdictionary = deserialized_plist

                    except (KeyError, ValueError, TypeError) as ex:
                        if str(ex).find("does not contain an '$archiver' key") >= 0:
                            logfunc('plist was Not an NSKeyedArchive ' + row[111])
                        else:
                            logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[111])

            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            if row[12] is not None:
                pathto = os.path.join(report_folder, 'FaceCropFor_' + row[109] + '.jpg')
                with open(pathto, 'wb') as file:
                    file.write(row[12])
                facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

            data_list.append((row[0], row[1], row[2], row[3], row[4],
                            personcontactmatchingdictionary,
                            row[6], row[7], row[8], row[9], row[10], row[11],
                            facecropresourcedata_blob,
                            row[13], row[14], row[15], row[16], row[17], row[18],
                            row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                            row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                            row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                            row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                            row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                            row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                            row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                            row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                            row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                            row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                            row[108], row[109], row[110], row[111], row[112], row[113]))

        data_headers = ('zDetFace-AssetForFace= zAsset-zPK-0',
                        'zDetFace-AssetForTorso= zAsset-zPK-1',
                        'zFaceCrop-Asset Key-2',
                        'zDetFace-Asset For Temporal Detected Faces= zAsset-zPK-3',
                        'zDetFacePrint-Data-SeeRawDBData-4',
                        'zPerson-Contact Matching Dictionary-5',
                        'zPerson-Verified Type-6',
                        'zPerson-Display Name-7',
                        'zPerson-Full Name-8',
                        'zPerson-Cloud Verified Type-9',
                        'zFaceCrop-State-10',
                        'zFaceCrop-Type-11',
                        'zFaceCrop-Resource Data-12',
                        'zDetFace-Confirmed Face Crop Generation State-13',
                        'zDetFace-Manual-14',
                        'zDetFace-Detection Type-15',
                        'zPerson-Detection Type-16',
                        'zDetFace-VIP Model Type-17',
                        'zDetFace-Name Source-18',
                        'zDetFace-Cloud Name Source-19',
                        'zPerson-Merge Candidate Confidence-20',
                        'zPerson-Type-21',
                        'zPerson-Gender Type-22',
                        'zDetFace-Gender Type-23',
                        'zDetFace-Center X-24',
                        'zDetFace-Center Y-25',
                        'zPerson-Age Type Estimate-26',
                        'zDetFace-Age Type Estimate-27',
                        'zDetFace-Ethnicity Type-28',
                        'zDetFace-Skin Tone Type-29',
                        'zDetFace-Hair Type-30',
                        'zDetFace-Hair Color Type-31',
                        'zDetFace-Head Gear Type-32',
                        'zDetFace-Facial Hair Type-33',
                        'zDetFace-Has Face Mask-34',
                        'zDetFace-Pose Type-35',
                        'zDetFace-Face Expression Type-36',
                        'zDetFace-Has Smile-37',
                        'zDetFace-Smile Type-38',
                        'zDetFace-Lip Makeup Type-39',
                        'zDetFace-Eyes State-40',
                        'zDetFace-Is Left Eye Closed-41',
                        'zDetFace-Is Right Eye Closed-42',
                        'zDetFace-Gaze Center X-43',
                        'zDetFace-Gaze Center Y-44',
                        'zDetFace-Face Gaze Type-45',
                        'zDetFace-Eye Glasses Type-46',
                        'zDetFace-Eye Makeup Type-47',
                        'zDetFace-Cluster Sequence Number Key-48',
                        'zDetFace-Grouping ID-49',
                        'zDetFace-Master ID-50',
                        'zDetFace-Quality-51',
                        'zDetFace-Quality Measure-52',
                        'zDetFace-Source Height-53',
                        'zDetFace-Source Width-54',
                        'zDetFace-Asset Visible-55',
                        'zDetFace-Hidden/Asset Hidden-56',
                        'zDetFace-In Trash/Recently Deleted-57',
                        'zDetFace-Cloud Local State-58',
                        'zDetFace-Training Type-59',
                        'zDetFace.Pose Yaw-60',
                        'zDetFace-Body Center X-61',
                        'zDetFace-Body Center Y-62',
                        'zDetFace-Body Height-63',
                        'zDetFace-Body Width-64',
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
                        'zDetFace-Person for Temporal Detected Faces= zPerson-zPK-93',
                        'zDetFace-PersonForTorso= zPerson-zPK-94',
                        'zDetFace-Person Being Key Face-95',
                        'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-96',
                        'zDetFace-Face Print-97',
                        'zDetFacePrint-zPK-98',
                        'zDetFace-Face Crop-99',
                        'zFaceCrop-zPK-100',
                        'zDetFaceGroup-KeyFace= zDetFace-zPK-101',
                        'zDetFaceGroup-AssocPerson= zPerson-zPK-102',
                        'zPerson-Assoc Face Group Key-103',
                        'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-104',
                        'zDetFace-FaceGroup= zDetFaceGroup-zPK-105',
                        'zDetFaceGroup-zPK-106',
                        'zPerson-Share Participant= zSharePartic-zPK-107',
                        'zDetFace-UUID-108',
                        'zFaceCrop-UUID-109',
                        'zFaceCrop-Invalid Merge Candidate Person UUID-110',
                        'zPerson-Person UUID-111',
                        'zPerson-Person URI-112',
                        'zDetFaceGroup-UUID-113')
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
        zDetFace.ZASSETFORFACE AS 'zDetFace-AssetForFace= zAsset-zPK',
        zDetFace.ZASSETFORTORSO AS 'zDetFace-AssetForTorso= zAsset-zPK',
        zFaceCrop.ZASSET AS 'zFaceCrop-Asset Key',        
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
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID'      
        FROM ZDETECTEDFACE zDetFace
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSONFORFACE
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP  
        ORDER BY zDetFace.Z_PK
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            personcontactmatchingdictionary = ''
            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            facecropresourcedata_blob = ''

            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            if row[5] is not None:
                pathto = os.path.join(report_folder, 'zPerson-ContactMatchingDict_' + row[112] + '.plist')
                with open(pathto, 'ab') as wf:
                    wf.write(row[5])

                with open(pathto, 'rb') as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        personcontactmatchingdictionary = deserialized_plist

                    except (KeyError, ValueError, TypeError) as ex:
                        if str(ex).find("does not contain an '$archiver' key") >= 0:
                            logfunc('plist was Not an NSKeyedArchive ' + row[112])
                        else:
                            logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[112])

            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            if row[13] is not None:
                pathto = os.path.join(report_folder, 'FaceCropFor_' + row[110] + '.jpg')
                with open(pathto, 'wb') as file:
                    file.write(row[13])
                facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

            data_list.append((row[0], row[1], row[2], row[3], row[4],
                            personcontactmatchingdictionary,
                            row[6], row[7], row[8], row[9], row[10], row[11], row[12],
                            facecropresourcedata_blob,
                            row[14], row[15], row[16], row[17], row[18],
                            row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                            row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                            row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                            row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                            row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                            row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                            row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                            row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                            row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                            row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                            row[108], row[109], row[110], row[111], row[112], row[113], row[114]))

        data_headers = ('zDetFace-AssetForFace= zAsset-zPK-0',
                        'zDetFace-AssetForTorso= zAsset-zPK-1',
                        'zFaceCrop-Asset Key-2',
                        'zDetFace-Asset For Temporal Detected Faces= zAsset-zPK-3',
                        'zDetFacePrint-Data-SeeRawDBData-4',
                        'zPerson-Contact Matching Dictionary-5',
                        'zPerson-Verified Type-6',
                        'zPerson-Is_Me_Confidence-7',
                        'zPerson-Display Name-8',
                        'zPerson-Full Name-9',
                        'zPerson-Cloud Verified Type-10',
                        'zFaceCrop-State-11',
                        'zFaceCrop-Type-12',
                        'zFaceCrop-Resource Data-13',
                        'zDetFace-Confirmed Face Crop Generation State-14',
                        'zDetFace-Manual-15',
                        'zDetFace-Detection Type-16',
                        'zPerson-Detection Type-17',
                        'zDetFace-VIP Model Type-18',
                        'zDetFace-Name Source-19',
                        'zDetFace-Cloud Name Source-20',
                        'zPerson-Merge Candidate Confidence-21',
                        'zPerson-Type-22',
                        'zPerson-Gender Type-23',
                        'zDetFace-Gender Type-24',
                        'zDetFace-Center X-25',
                        'zDetFace-Center Y-26',
                        'zPerson-Age Type Estimate-27',
                        'zDetFace-Age Type Estimate-28',
                        'zDetFace-Ethnicity Type-29',
                        'zDetFace-Skin Tone Type-30',
                        'zDetFace-Hair Type-31',
                        'zDetFace-Hair Color Type-32',
                        'zDetFace-Head Gear Type-33',
                        'zDetFace-Facial Hair Type-34',
                        'zDetFace-Has Face Mask-35',
                        'zDetFace-Pose Type-36',
                        'zDetFace-Face Expression Type-37',
                        'zDetFace-Has Smile-38',
                        'zDetFace-Smile Type-39',
                        'zDetFace-Lip Makeup Type-40',
                        'zDetFace-Eyes State-41',
                        'zDetFace-Is Left Eye Closed-42',
                        'zDetFace-Is Right Eye Closed-43',
                        'zDetFace-Gaze Center X-44',
                        'zDetFace-Gaze Center Y-45',
                        'zDetFace-Face Gaze Type-46',
                        'zDetFace-Eye Glasses Type-47',
                        'zDetFace-Eye Makeup Type-48',
                        'zDetFace-Cluster Sequence Number Key-49',
                        'zDetFace-Grouping ID-50',
                        'zDetFace-Master ID-51',
                        'zDetFace-Quality-52',
                        'zDetFace-Quality Measure-53',
                        'zDetFace-Source Height-54',
                        'zDetFace-Source Width-55',
                        'zDetFace-Asset Visible-56',
                        'zDetFace-Hidden/Asset Hidden-57',
                        'zDetFace-In Trash/Recently Deleted-58',
                        'zDetFace-Cloud Local State-59',
                        'zDetFace-Training Type-60',
                        'zDetFace.Pose Yaw-61',
                        'zDetFace-Body Center X-62',
                        'zDetFace-Body Center Y-63',
                        'zDetFace-Body Height-64',
                        'zDetFace-Body Width-65',
                        'zDetFace-Roll-66',
                        'zDetFace-Size-67',
                        'zDetFace-Cluster Sequence Number-68',
                        'zDetFace-Blur Score-69',
                        'zDetFacePrint-Face Print Version-70',
                        'zDetFaceGroup-UUID-71',
                        'zDetFaceGroup-Person Builder State-72',
                        'zDetFaceGroup-UnNamed Face Count-73',
                        'zPerson-Face Count-74',
                        'zDetFace-Face Algorithm Version-75',
                        'zDetFace-Adjustment Version-76',
                        'zPerson-In Person Naming Model-77',
                        'zPerson-Key Face Pick Source Key-78',
                        'zPerson-Manual Order Key-79',
                        'zPerson-Question Type-80',
                        'zPerson-Suggested For Client Type-81',
                        'zPerson-Merge Target Person-82',
                        'zPerson-Cloud Local State-83',
                        'zFaceCrop-Cloud Local State-84',
                        'zFaceCrop-Cloud Type-85',
                        'zPerson-Cloud Delete State-86',
                        'zFaceCrop-Cloud Delete State-87',
                        'zDetFace-zPK-88',
                        'zDetFacePrint-Face Key-89',
                        'zPerson-KeyFace=zDetFace-zPK-90',
                        'zFaceCrop-Face Key-91',
                        'zPerson-zPK=zDetFace-Person-92',
                        'zDetFace-PersonForFace= zPerson-zPK-93',
                        'zDetFace-Person for Temporal Detected Faces= zPerson-zPK-94',
                        'zDetFace-PersonForTorso= zPerson-zPK-95',
                        'zDetFace-Person Being Key Face-96',
                        'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-97',
                        'zDetFace-Face Print-98',
                        'zDetFacePrint-zPK-99',
                        'zDetFace-Face Crop-100',
                        'zFaceCrop-zPK-101',
                        'zDetFaceGroup-KeyFace= zDetFace-zPK-102',
                        'zDetFaceGroup-AssocPerson= zPerson-zPK-103',
                        'zPerson-Assoc Face Group Key-104',
                        'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-105',
                        'zDetFace-FaceGroup= zDetFaceGroup-zPK-106',
                        'zDetFaceGroup-zPK-107',
                        'zPerson-Share Participant= zSharePartic-zPK-108',
                        'zDetFace-UUID-109',
                        'zFaceCrop-UUID-110',
                        'zFaceCrop-Invalid Merge Candidate Person UUID-111',
                        'zPerson-Person UUID-112',
                        'zPerson-Person URI-113',
                        'zDetFaceGroup-UUID-114')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

@artifact_processor
def Ph15_2PeopleFacesNADSyndPL(files_found, report_folder, seeker, wrap_text, timezone_offset):
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
        zDetFace.ZASSET AS 'zDetFace-AssetForFace= zAsset-zPK',
        zFaceCrop.ZASSET AS 'zFaceCrop-Asset Key',
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
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID'      
        FROM ZDETECTEDFACE zDetFace
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSON
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP  
        ORDER BY zDetFace.Z_PK
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            personcontactmatchingdictionary = ''
            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            facecropresourcedata_blob = ''

            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            if row[3] is not None:
                pathto = os.path.join(report_folder, 'zPerson-ContactMatchingDict_' + row[89] + '.plist')
                with open(pathto, 'ab') as wf:
                    wf.write(row[3])

                with open(pathto, 'rb') as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        personcontactmatchingdictionary = deserialized_plist

                    except (KeyError, ValueError, TypeError) as ex:
                        if str(ex).find("does not contain an '$archiver' key") >= 0:
                            logfunc('plist was Not an NSKeyedArchive ' + row[89])
                        else:
                            logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[89])

            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            if row[10] is not None:
                pathto = os.path.join(report_folder, 'FaceCropFor_' + row[87] + '.jpg')
                with open(pathto, 'wb') as file:
                    file.write(row[10])
                facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

            data_list.append((row[0], row[1], row[2],
                              personcontactmatchingdictionary,
                              row[4], row[5], row[6], row[7], row[8], row[9],
                              facecropresourcedata_blob,
                              row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                              row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                              row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                              row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                              row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                              row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                              row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                              row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                              row[91]))

        data_headers = ('zDetFace-AssetForFace= zAsset-zPK-0',
                        'zFaceCrop-Asset Key-1',
                        'zDetFacePrint-Data-SeeRawDBData-2',
                        'zPerson-Contact Matching Dictionary-3',
                        'zPerson-Verified Type-4',
                        'zPerson-Display Name-5',
                        'zPerson-Full Name-6',
                        'zPerson-Cloud Verified Type-7',
                        'zFaceCrop-State-8',
                        'zFaceCrop-Type-9',
                        'zFaceCrop-Resource Data-10',
                        'zDetFace-Confirmed Face Crop Generation State-11',
                        'zDetFace-Manual-12',
                        'zDetFace-VIP Model Type-13',
                        'zDetFace-Name Source-14',
                        'zDetFace-Cloud Name Source-15',
                        'zPerson-Type-16',
                        'zPerson-Gender Type-17',
                        'zDetFace-Gender Type-18',
                        'zDetFace-Center X-19',
                        'zDetFace-Center Y-20',
                        'zPerson-Age Type Estimate-21',
                        'zDetFace-Age Type Estimate-22',
                        'zDetFace-Hair Color Type-23',
                        'zDetFace-Facial Hair Type-24',
                        'zDetFace-Has Smile-25',
                        'zDetFace-Smile Type-26',
                        'zDetFace-Lip Makeup Type-27',
                        'zDetFace-Eyes State-28',
                        'zDetFace-Is Left Eye Closed-29',
                        'zDetFace-Is Right Eye Closed-30',
                        'zDetFace-Eye Glasses Type-31',
                        'zDetFace-Eye Makeup Type-32',
                        'zDetFace-Cluster Sequence Number Key-33',
                        'zDetFace-Grouping ID-34',
                        'zDetFace-Master ID-35',
                        'zDetFace-Quality-36',
                        'zDetFace-Quality Measure-37',
                        'zDetFace-Source Height-38',
                        'zDetFace-Source Width-39',
                        'zDetFace-Asset Visible-40',
                        'zDetFace-Hidden/Asset Hidden-41',
                        'zDetFace-In Trash/Recently Deleted-42',
                        'zDetFace-Cloud Local State-43',
                        'zDetFace-Training Type-44',
                        'zDetFace.Pose Yaw-45',
                        'zDetFace-Roll-46',
                        'zDetFace-Size-47',
                        'zDetFace-Cluster Sequence Number-48',
                        'zDetFace-Blur Score-49',
                        'zDetFacePrint-Face Print Version-50',
                        'zDetFaceGroup-UUID-51',
                        'zDetFaceGroup-Person Builder State-52',
                        'zDetFaceGroup-UnNamed Face Count-53',
                        'zPerson-Face Count-54',
                        'zDetFace-Face Algorithm Version-55',
                        'zDetFace-Adjustment Version-56',
                        'zPerson-In Person Naming Model-57',
                        'zPerson-Key Face Pick Source Key-58',
                        'zPerson-Manual Order Key-59',
                        'zPerson-Question Type-60',
                        'zPerson-Suggested For Client Type-61',
                        'zPerson-Merge Target Person-62',
                        'zPerson-Cloud Local State-63',
                        'zFaceCrop-Cloud Local State-64',
                        'zFaceCrop-Cloud Type-65',
                        'zPerson-Cloud Delete State-66',
                        'zFaceCrop-Cloud Delete State-67',
                        'zDetFace-zPK-68',
                        'zDetFacePrint-Face Key-69',
                        'zPerson-KeyFace=zDetFace-zPK-70',
                        'zFaceCrop-Face Key-71',
                        'zPerson-zPK=zDetFace-Person-72',
                        'zDetFace-PersonForFace= zPerson-zPK-73',
                        'zDetFace-Person Being Key Face-74',
                        'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-75',
                        'zDetFace-Face Print-76',
                        'zDetFacePrint-zPK-77',
                        'zDetFace-Face Crop-78',
                        'zFaceCrop-zPK-79',
                        'zDetFaceGroup-KeyFace= zDetFace-zPK-80',
                        'zDetFaceGroup-AssocPerson= zPerson-zPK-81',
                        'zPerson-Assoc Face Group Key-82',
                        'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-83',
                        'zDetFace-FaceGroup= zDetFaceGroup-zPK-84',
                        'zDetFaceGroup-zPK-85',
                        'zDetFace-UUID-86',
                        'zFaceCrop-UUID-87',
                        'zFaceCrop-Invalid Merge Candidate Person UUID-88',
                        'zPerson-Person UUID-89',
                        'zPerson-Person URI-90',
                        'zDetFaceGroup-UUID-91')
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
        zDetFace.ZASSET AS 'zDetFace-AssetForFace= zAsset-zPK',
        zFaceCrop.ZASSET AS 'zFaceCrop-Asset Key',
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
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID'      
        FROM ZDETECTEDFACE zDetFace
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSON
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP  
        ORDER BY zDetFace.Z_PK
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            personcontactmatchingdictionary = ''
            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            facecropresourcedata_blob = ''

            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            if row[3] is not None:
                pathto = os.path.join(report_folder, 'zPerson-ContactMatchingDict_' + row[105] + '.plist')
                with open(pathto, 'ab') as wf:
                    wf.write(row[3])

                with open(pathto, 'rb') as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        personcontactmatchingdictionary = deserialized_plist

                    except (KeyError, ValueError, TypeError) as ex:
                        if str(ex).find("does not contain an '$archiver' key") >= 0:
                            logfunc('plist was Not an NSKeyedArchive ' + row[105])
                        else:
                            logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[105])

            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            if row[10] is not None:
                pathto = os.path.join(report_folder, 'FaceCropFor_' + row[103] + '.jpg')
                with open(pathto, 'wb') as file:
                    file.write(row[10])
                facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

            data_list.append((row[0], row[1], row[2],
                              personcontactmatchingdictionary,
                              row[4], row[5], row[6], row[7], row[8], row[9],
                              facecropresourcedata_blob,
                              row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                              row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                              row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                              row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                              row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                              row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                              row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                              row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                              row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                              row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107]))

        data_headers = ('zDetFace-AssetForFace= zAsset-zPK-0',
                        'zFaceCrop-Asset Key-1',
                        'zDetFacePrint-Data-SeeRawDBData-2',
                        'zPerson-Contact Matching Dictionary-3',
                        'zPerson-Verified Type-4',
                        'zPerson-Display Name-5',
                        'zPerson-Full Name-6',
                        'zPerson-Cloud Verified Type-7',
                        'zFaceCrop-State-8',
                        'zFaceCrop-Type-9',
                        'zFaceCrop-Resource Data-10',
                        'zDetFace-Confirmed Face Crop Generation State-11',
                        'zDetFace-Manual-12',
                        'zDetFace-Detection Type-13',
                        'zPerson-Detection Type-14',
                        'zDetFace-VIP Model Type-15',
                        'zDetFace-Name Source-16',
                        'zDetFace-Cloud Name Source-17',
                        'zPerson-Type-18',
                        'zPerson-Gender Type-19',
                        'zDetFace-Gender Type-20',
                        'zDetFace-Center X-21',
                        'zDetFace-Center Y-22',
                        'zPerson-Age Type Estimate-23',
                        'zDetFace-Age Type Estimate-24',
                        'zDetFace-Ethnicity Type-25',
                        'zDetFace-Skin Tone Type-26',
                        'zDetFace-Hair Type-27',
                        'zDetFace-Hair Color Type-28',
                        'zDetFace-Head Gear Type-29',
                        'zDetFace-Facial Hair Type-30',
                        'zDetFace-Has Face Mask-31',
                        'zDetFace-Pose Type-32',
                        'zDetFace-Face Expression Type-33',
                        'zDetFace-Has Smile-34',
                        'zDetFace-Smile Type-35',
                        'zDetFace-Lip Makeup Type-36',
                        'zDetFace-Eyes State-37',
                        'zDetFace-Is Left Eye Closed-38',
                        'zDetFace-Is Right Eye Closed-39',
                        'zDetFace-Gaze Center X-40',
                        'zDetFace-Gaze Center Y-41',
                        'zDetFace-Face Gaze Type-42',
                        'zDetFace-Eye Glasses Type-43',
                        'zDetFace-Eye Makeup Type-44',
                        'zDetFace-Cluster Squence Number Key-45',
                        'zDetFace-Grouping ID-46',
                        'zDetFace-Master ID-47',
                        'zDetFace-Quality-48',
                        'zDetFace-Quality Measure-49',
                        'zDetFace-Source Height-50',
                        'zDetFace-Source Width-51',
                        'zDetFace-Asset Visible-52',
                        'zDetFace-Hidden/Asset Hidden-53',
                        'zDetFace-In Trash/Recently Deleted-54',
                        'zDetFace-Cloud Local State-55',
                        'zDetFace-Training Type-56',
                        'zDetFace.Pose Yaw-57',
                        'zDetFace-Body Center X-58',
                        'zDetFace-Body Center Y-59',
                        'zDetFace-Body Height-60',
                        'zDetFace-Body Width-61',
                        'zDetFace-Roll-62',
                        'zDetFace-Size-63',
                        'zDetFace-Cluster Squence Number-64',
                        'zDetFace-Blur Score-65',
                        'zDetFacePrint-Face Print Version-66',
                        'zDetFaceGroup-UUID-67',
                        'zDetFaceGroup-Person Builder State-68',
                        'zDetFaceGroup-UnNamed Face Count-69',
                        'zPerson-Face Count-70',
                        'zDetFace-Face Algorithm Version-71',
                        'zDetFace-Adjustment Version-72',
                        'zPerson-In Person Naming Model-73',
                        'zPerson-Key Face Pick Source Key-74',
                        'zPerson-Manual Order Key-75',
                        'zPerson-Question Type-76',
                        'zPerson-Suggested For Client Type-77',
                        'zPerson-Merge Target Person-78',
                        'zPerson-Cloud Local State-79',
                        'zFaceCrop-Cloud Local State-80',
                        'zFaceCrop-Cloud Type-81',
                        'zPerson-Cloud Delete State-82',
                        'zFaceCrop-Cloud Delete State-83',
                        'zDetFace-zPK-84',
                        'zDetFacePrint-Face Key-85',
                        'zPerson-KeyFace=zDetFace-zPK-86',
                        'zFaceCrop-Face Key-87',
                        'zPerson-zPK=zDetFace-Person-88',
                        'zDetFace-PersonForFace= zPerson-zPK-89',
                        'zDetFace-Person Being Key Face-90',
                        'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-91',
                        'zDetFace-Face Print-92',
                        'zDetFacePrint-zPK-93',
                        'zDetFace-Face Crop-94',
                        'zFaceCrop-zPK-95',
                        'zDetFaceGroup-KeyFace= zDetFace-zPK-96',
                        'zDetFaceGroup-AssocPerson= zPerson-zPK-97',
                        'zPerson-Assoc Face Group Key-98',
                        'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-99',
                        'zDetFace-FaceGroup= zDetFaceGroup-zPK-100',
                        'zDetFaceGroup-zPK-101',
                        'zDetFace-UUID-102',
                        'zFaceCrop-UUID-103',
                        'zFaceCrop-Invalid Merge Canidate Person UUID-104',
                        'zPerson-Person UUID-105',
                        'zPerson-Person URI-106',
                        'zDetFaceGroup-UUID-107')
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
        zDetFace.ZASSET AS 'zDetFace-AssetForFace= zAsset-zPK',
        zFaceCrop.ZASSET AS 'zFaceCrop-Asset Key',
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
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID'      
        FROM ZDETECTEDFACE zDetFace
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSON
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP  
        ORDER BY zDetFace.Z_PK
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            personcontactmatchingdictionary = ''
            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            facecropresourcedata_blob = ''

            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            if row[3] is not None:
                pathto = os.path.join(report_folder, 'zPerson-ContactMatchingDict_' + row[107] + '.plist')
                with open(pathto, 'ab') as wf:
                    wf.write(row[3])

                with open(pathto, 'rb') as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        personcontactmatchingdictionary = deserialized_plist

                    except (KeyError, ValueError, TypeError) as ex:
                        if str(ex).find("does not contain an '$archiver' key") >= 0:
                            logfunc('plist was Not an NSKeyedArchive ' + row[107])
                        else:
                            logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[107])

            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            if row[10] is not None:
                pathto = os.path.join(report_folder, 'FaceCropFor_' + row[105] + '.jpg')
                with open(pathto, 'wb') as file:
                    file.write(row[10])
                facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

            data_list.append((row[0], row[1], row[2],
                              personcontactmatchingdictionary,
                              row[4], row[5], row[6], row[7], row[8], row[9],
                              facecropresourcedata_blob,
                              row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                              row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                              row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                              row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                              row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                              row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                              row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                              row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                              row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                              row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                              row[108], row[109]))

        data_headers = ('zDetFace-AssetForFace= zAsset-zPK-0',
                        'zFaceCrop-Asset Key-1',
                        'zDetFacePrint-Data-SeeRawDBData-2',
                        'zPerson-Contact Matching Dictionary-3',
                        'zPerson-Verified Type-4',
                        'zPerson-Display Name-5',
                        'zPerson-Full Name-6',
                        'zPerson-Cloud Verified Type-7',
                        'zFaceCrop-State-8',
                        'zFaceCrop-Type-9',
                        'zFaceCrop-Resource Data-10',
                        'zDetFace-Confirmed Face Crop Generation State-11',
                        'zDetFace-Manual-12',
                        'zDetFace-Detection Type-13',
                        'zPerson-Detection Type-14',
                        'zDetFace-VIP Model Type-15',
                        'zDetFace-Name Source-16',
                        'zDetFace-Cloud Name Source-17',
                        'zPerson-Merge Candidate Confidence-18',
                        'zPerson-Type-19',
                        'zPerson-Gender Type-20',
                        'zDetFace-Gender Type-21',
                        'zDetFace-Center X-22',
                        'zDetFace-Center Y-23',
                        'zPerson-Age Type Estimate-24',
                        'zDetFace-Age Type Estimate-25',
                        'zDetFace-Ethnicity Type-26',
                        'zDetFace-Skin Tone Type-27',
                        'zDetFace-Hair Type-28',
                        'zDetFace-Hair Color Type-29',
                        'zDetFace-Head Gear Type-30',
                        'zDetFace-Facial Hair Type-31',
                        'zDetFace-Has Face Mask-32',
                        'zDetFace-Pose Type-33',
                        'zDetFace-Face Expression Type-34',
                        'zDetFace-Has Smile-35',
                        'zDetFace-Smile Type-36',
                        'zDetFace-Lip Makeup Type-37',
                        'zDetFace-Eyes State-38',
                        'zDetFace-Is Left Eye Closed-39',
                        'zDetFace-Is Right Eye Closed-40',
                        'zDetFace-Gaze Center X-41',
                        'zDetFace-Gaze Center Y-42',
                        'zDetFace-Face Gaze Type-43',
                        'zDetFace-Eye Glasses Type-44',
                        'zDetFace-Eye Makeup Type-45',
                        'zDetFace-Cluster Squence Number Key-46',
                        'zDetFace-Grouping ID-47',
                        'zDetFace-Master ID-48',
                        'zDetFace-Quality-49',
                        'zDetFace-Quality Measure-50',
                        'zDetFace-Source Height-51',
                        'zDetFace-Source Width-52',
                        'zDetFace-Asset Visible-53',
                        'zDetFace-Hidden/Asset Hidden-54',
                        'zDetFace-In Trash/Recently Deleted-55',
                        'zDetFace-Cloud Local State-56',
                        'zDetFace-Training Type-57',
                        'zDetFace.Pose Yaw-58',
                        'zDetFace-Body Center X-59',
                        'zDetFace-Body Center Y-60',
                        'zDetFace-Body Height-61',
                        'zDetFace-Body Width-62',
                        'zDetFace-Roll-63',
                        'zDetFace-Size-64',
                        'zDetFace-Cluster Squence Number-65',
                        'zDetFace-Blur Score-66',
                        'zDetFacePrint-Face Print Version-67',
                        'zDetFaceGroup-UUID-68',
                        'zDetFaceGroup-Person Builder State-69',
                        'zDetFaceGroup-UnNamed Face Count-70',
                        'zPerson-Face Count-71',
                        'zDetFace-Face Algorithm Version-72',
                        'zDetFace-Adjustment Version-73',
                        'zPerson-In Person Naming Model-74',
                        'zPerson-Key Face Pick Source Key-75',
                        'zPerson-Manual Order Key-76',
                        'zPerson-Question Type-77',
                        'zPerson-Suggested For Client Type-78',
                        'zPerson-Merge Target Person-79',
                        'zPerson-Cloud Local State-80',
                        'zFaceCrop-Cloud Local State-81',
                        'zFaceCrop-Cloud Type-82',
                        'zPerson-Cloud Delete State-83',
                        'zFaceCrop-Cloud Delete State-84',
                        'zDetFace-zPK-85',
                        'zDetFacePrint-Face Key-86',
                        'zPerson-KeyFace=zDetFace-zPK-87',
                        'zFaceCrop-Face Key-88',
                        'zPerson-zPK=zDetFace-Person-89',
                        'zDetFace-PersonForFace= zPerson-zPK-90',
                        'zDetFace-Person Being Key Face-91',
                        'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-92',
                        'zDetFace-Face Print-93',
                        'zDetFacePrint-zPK-94',
                        'zDetFace-Face Crop-95',
                        'zFaceCrop-zPK-96',
                        'zDetFaceGroup-KeyFace= zDetFace-zPK-97',
                        'zDetFaceGroup-AssocPerson= zPerson-zPK-98',
                        'zPerson-Assoc Face Group Key-99',
                        'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-100',
                        'zDetFace-FaceGroup= zDetFaceGroup-zPK-101',
                        'zDetFaceGroup-zPK-102',
                        'zPerson-Share Participant= zSharePartic-zPK-103',
                        'zDetFace-UUID-104',
                        'zFaceCrop-UUID-105',
                        'zFaceCrop-Invalid Merge Canidate Person UUID-106',
                        'zPerson-Person UUID-107',
                        'zPerson-Person URI-108',
                        'zDetFaceGroup-UUID-109')
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
        zDetFace.ZASSETFORFACE AS 'zDetFace-AssetForFace= zAsset-zPK',
        zDetFace.ZASSETFORTORSO AS 'zDetFace-AssetForTorso= zAsset-zPK',
        zFaceCrop.ZASSET AS 'zFaceCrop-Asset Key',        
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
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID'      
        FROM ZDETECTEDFACE zDetFace
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSONFORFACE
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP  
        ORDER BY zDetFace.Z_PK
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            personcontactmatchingdictionary = ''
            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            facecropresourcedata_blob = ''

            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            if row[5] is not None:
                pathto = os.path.join(report_folder, 'zPerson-ContactMatchingDict_' + row[111] + '.plist')
                with open(pathto, 'ab') as wf:
                    wf.write(row[5])

                with open(pathto, 'rb') as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        personcontactmatchingdictionary = deserialized_plist

                    except (KeyError, ValueError, TypeError) as ex:
                        if str(ex).find("does not contain an '$archiver' key") >= 0:
                            logfunc('plist was Not an NSKeyedArchive ' + row[111])
                        else:
                            logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[111])

            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            if row[12] is not None:
                pathto = os.path.join(report_folder, 'FaceCropFor_' + row[109] + '.jpg')
                with open(pathto, 'wb') as file:
                    file.write(row[12])
                facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

            data_list.append((row[0], row[1], row[2], row[3], row[4],
                              personcontactmatchingdictionary,
                              row[6], row[7], row[8], row[9], row[10], row[11],
                              facecropresourcedata_blob,
                              row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                              row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                              row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                              row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                              row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                              row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                              row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                              row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                              row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                              row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                              row[108], row[109], row[110], row[111], row[112], row[113]))

        data_headers = ('zDetFace-AssetForFace= zAsset-zPK-0',
                        'zDetFace-AssetForTorso= zAsset-zPK-1',
                        'zFaceCrop-Asset Key-2',
                        'zDetFace-Asset For Temporal Detected Faces= zAsset-zPK-3',
                        'zDetFacePrint-Data-SeeRawDBData-4',
                        'zPerson-Contact Matching Dictionary-5',
                        'zPerson-Verified Type-6',
                        'zPerson-Display Name-7',
                        'zPerson-Full Name-8',
                        'zPerson-Cloud Verified Type-9',
                        'zFaceCrop-State-10',
                        'zFaceCrop-Type-11',
                        'zFaceCrop-Resource Data-12',
                        'zDetFace-Confirmed Face Crop Generation State-13',
                        'zDetFace-Manual-14',
                        'zDetFace-Detection Type-15',
                        'zPerson-Detection Type-16',
                        'zDetFace-VIP Model Type-17',
                        'zDetFace-Name Source-18',
                        'zDetFace-Cloud Name Source-19',
                        'zPerson-Merge Candidate Confidence-20',
                        'zPerson-Type-21',
                        'zPerson-Gender Type-22',
                        'zDetFace-Gender Type-23',
                        'zDetFace-Center X-24',
                        'zDetFace-Center Y-25',
                        'zPerson-Age Type Estimate-26',
                        'zDetFace-Age Type Estimate-27',
                        'zDetFace-Ethnicity Type-28',
                        'zDetFace-Skin Tone Type-29',
                        'zDetFace-Hair Type-30',
                        'zDetFace-Hair Color Type-31',
                        'zDetFace-Head Gear Type-32',
                        'zDetFace-Facial Hair Type-33',
                        'zDetFace-Has Face Mask-34',
                        'zDetFace-Pose Type-35',
                        'zDetFace-Face Expression Type-36',
                        'zDetFace-Has Smile-37',
                        'zDetFace-Smile Type-38',
                        'zDetFace-Lip Makeup Type-39',
                        'zDetFace-Eyes State-40',
                        'zDetFace-Is Left Eye Closed-41',
                        'zDetFace-Is Right Eye Closed-42',
                        'zDetFace-Gaze Center X-43',
                        'zDetFace-Gaze Center Y-44',
                        'zDetFace-Face Gaze Type-45',
                        'zDetFace-Eye Glasses Type-46',
                        'zDetFace-Eye Makeup Type-47',
                        'zDetFace-Cluster Squence Number Key-48',
                        'zDetFace-Grouping ID-49',
                        'zDetFace-Master ID-50',
                        'zDetFace-Quality-51',
                        'zDetFace-Quality Measure-52',
                        'zDetFace-Source Height-53',
                        'zDetFace-Source Width-54',
                        'zDetFace-Asset Visible-55',
                        'zDetFace-Hidden/Asset Hidden-56',
                        'zDetFace-In Trash/Recently Deleted-57',
                        'zDetFace-Cloud Local State-58',
                        'zDetFace-Training Type-59',
                        'zDetFace.Pose Yaw-60',
                        'zDetFace-Body Center X-61',
                        'zDetFace-Body Center Y-62',
                        'zDetFace-Body Height-63',
                        'zDetFace-Body Width-64',
                        'zDetFace-Roll-65',
                        'zDetFace-Size-66',
                        'zDetFace-Cluster Squence Number-67',
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
                        'zDetFace-Person for Temporal Detected Faces= zPerson-zPK-93',
                        'zDetFace-PersonForTorso= zPerson-zPK-94',
                        'zDetFace-Person Being Key Face-95',
                        'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-96',
                        'zDetFace-Face Print-97',
                        'zDetFacePrint-zPK-98',
                        'zDetFace-Face Crop-99',
                        'zFaceCrop-zPK-100',
                        'zDetFaceGroup-KeyFace= zDetFace-zPK-101',
                        'zDetFaceGroup-AssocPerson= zPerson-zPK-102',
                        'zPerson-Assoc Face Group Key-103',
                        'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-104',
                        'zDetFace-FaceGroup= zDetFaceGroup-zPK-105',
                        'zDetFaceGroup-zPK-106',
                        'zPerson-Share Participant= zSharePartic-zPK-107',
                        'zDetFace-UUID-108',
                        'zFaceCrop-UUID-109',
                        'zFaceCrop-Invalid Merge Canidate Person UUID-110',
                        'zPerson-Person UUID-111',
                        'zPerson-Person URI-112',
                        'zDetFaceGroup-UUID-113')
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
        zDetFace.ZASSETFORFACE AS 'zDetFace-AssetForFace= zAsset-zPK',
        zDetFace.ZASSETFORTORSO AS 'zDetFace-AssetForTorso= zAsset-zPK',
        zFaceCrop.ZASSET AS 'zFaceCrop-Asset Key',        
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
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID'      
        FROM ZDETECTEDFACE zDetFace
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSONFORFACE
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP  
        ORDER BY zDetFace.Z_PK
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            personcontactmatchingdictionary = ''
            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            facecropresourcedata_blob = ''

            # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
            if row[5] is not None:
                pathto = os.path.join(report_folder, 'zPerson-ContactMatchingDict_' + row[112] + '.plist')
                with open(pathto, 'ab') as wf:
                    wf.write(row[5])

                with open(pathto, 'rb') as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        personcontactmatchingdictionary = deserialized_plist

                    except (KeyError, ValueError, TypeError) as ex:
                        if str(ex).find("does not contain an '$archiver' key") >= 0:
                            logfunc('plist was Not an NSKeyedArchive ' + row[112])
                        else:
                            logfunc(
                                'Error reading exported plist from zPerson-Contact Matching Dictionary' + row[112])

            # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
            if row[13] is not None:
                pathto = os.path.join(report_folder, 'FaceCropFor_' + row[110] + '.jpg')
                with open(pathto, 'wb') as file:
                    file.write(row[13])
                facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

            data_list.append((row[0], row[1], row[2], row[3], row[4],
                              personcontactmatchingdictionary,
                              row[6], row[7], row[8], row[9], row[10], row[11], row[12],
                              facecropresourcedata_blob,
                              row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                              row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                              row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                              row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                              row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                              row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                              row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                              row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                              row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                              row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                              row[108], row[109], row[110], row[111], row[112], row[113], row[114]))

        data_headers = ('zDetFace-AssetForFace= zAsset-zPK-0',
                        'zDetFace-AssetForTorso= zAsset-zPK-1',
                        'zFaceCrop-Asset Key-2',
                        'zDetFace-Asset For Temporal Detected Faces= zAsset-zPK-3',
                        'zDetFacePrint-Data-SeeRawDBData-4',
                        'zPerson-Contact Matching Dictionary-5',
                        'zPerson-Verified Type-6',
                        'zPerson-Is_Me_Confidence-7',
                        'zPerson-Display Name-8',
                        'zPerson-Full Name-9',
                        'zPerson-Cloud Verified Type-10',
                        'zFaceCrop-State-11',
                        'zFaceCrop-Type-12',
                        'zFaceCrop-Resource Data-13',
                        'zDetFace-Confirmed Face Crop Generation State-14',
                        'zDetFace-Manual-15',
                        'zDetFace-Detection Type-16',
                        'zPerson-Detection Type-17',
                        'zDetFace-VIP Model Type-18',
                        'zDetFace-Name Source-19',
                        'zDetFace-Cloud Name Source-20',
                        'zPerson-Merge Candidate Confidence-21',
                        'zPerson-Type-22',
                        'zPerson-Gender Type-23',
                        'zDetFace-Gender Type-24',
                        'zDetFace-Center X-25',
                        'zDetFace-Center Y-26',
                        'zPerson-Age Type Estimate-27',
                        'zDetFace-Age Type Estimate-28',
                        'zDetFace-Ethnicity Type-29',
                        'zDetFace-Skin Tone Type-30',
                        'zDetFace-Hair Type-31',
                        'zDetFace-Hair Color Type-32',
                        'zDetFace-Head Gear Type-33',
                        'zDetFace-Facial Hair Type-34',
                        'zDetFace-Has Face Mask-35',
                        'zDetFace-Pose Type-36',
                        'zDetFace-Face Expression Type-37',
                        'zDetFace-Has Smile-38',
                        'zDetFace-Smile Type-39',
                        'zDetFace-Lip Makeup Type-40',
                        'zDetFace-Eyes State-41',
                        'zDetFace-Is Left Eye Closed-42',
                        'zDetFace-Is Right Eye Closed-43',
                        'zDetFace-Gaze Center X-44',
                        'zDetFace-Gaze Center Y-45',
                        'zDetFace-Face Gaze Type-46',
                        'zDetFace-Eye Glasses Type-47',
                        'zDetFace-Eye Makeup Type-48',
                        'zDetFace-Cluster Sequence Number Key-49',
                        'zDetFace-Grouping ID-50',
                        'zDetFace-Master ID-51',
                        'zDetFace-Quality-52',
                        'zDetFace-Quality Measure-53',
                        'zDetFace-Source Height-54',
                        'zDetFace-Source Width-55',
                        'zDetFace-Asset Visible-56',
                        'zDetFace-Hidden/Asset Hidden-57',
                        'zDetFace-In Trash/Recently Deleted-58',
                        'zDetFace-Cloud Local State-59',
                        'zDetFace-Training Type-60',
                        'zDetFace.Pose Yaw-61',
                        'zDetFace-Body Center X-62',
                        'zDetFace-Body Center Y-63',
                        'zDetFace-Body Height-64',
                        'zDetFace-Body Width-65',
                        'zDetFace-Roll-66',
                        'zDetFace-Size-67',
                        'zDetFace-Cluster Sequence Number-68',
                        'zDetFace-Blur Score-69',
                        'zDetFacePrint-Face Print Version-70',
                        'zDetFaceGroup-UUID-71',
                        'zDetFaceGroup-Person Builder State-72',
                        'zDetFaceGroup-UnNamed Face Count-73',
                        'zPerson-Face Count-74',
                        'zDetFace-Face Algorithm Version-75',
                        'zDetFace-Adjustment Version-76',
                        'zPerson-In Person Naming Model-77',
                        'zPerson-Key Face Pick Source Key-78',
                        'zPerson-Manual Order Key-79',
                        'zPerson-Question Type-80',
                        'zPerson-Suggested For Client Type-81',
                        'zPerson-Merge Target Person-82',
                        'zPerson-Cloud Local State-83',
                        'zFaceCrop-Cloud Local State-84',
                        'zFaceCrop-Cloud Type-85',
                        'zPerson-Cloud Delete State-86',
                        'zFaceCrop-Cloud Delete State-87',
                        'zDetFace-zPK-88',
                        'zDetFacePrint-Face Key-89',
                        'zPerson-KeyFace=zDetFace-zPK-90',
                        'zFaceCrop-Face Key-91',
                        'zPerson-zPK=zDetFace-Person-92',
                        'zDetFace-PersonForFace= zPerson-zPK-93',
                        'zDetFace-Person for Temporal Detected Faces= zPerson-zPK-94',
                        'zDetFace-PersonForTorso= zPerson-zPK-95',
                        'zDetFace-Person Being Key Face-96',
                        'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-97',
                        'zDetFace-Face Print-98',
                        'zDetFacePrint-zPK-99',
                        'zDetFace-Face Crop-100',
                        'zFaceCrop-zPK-101',
                        'zDetFaceGroup-KeyFace= zDetFace-zPK-102',
                        'zDetFaceGroup-AssocPerson= zPerson-zPK-103',
                        'zPerson-Assoc Face Group Key-104',
                        'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-105',
                        'zDetFace-FaceGroup= zDetFaceGroup-zPK-106',
                        'zDetFaceGroup-zPK-107',
                        'zPerson-Share Participant= zSharePartic-zPK-108',
                        'zDetFace-UUID-109',
                        'zFaceCrop-UUID-110',
                        'zFaceCrop-Invalid Merge Candidate Person UUID-111',
                        'zPerson-Person UUID-112',
                        'zPerson-Person URI-113',
                        'zDetFaceGroup-UUID-114')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path



