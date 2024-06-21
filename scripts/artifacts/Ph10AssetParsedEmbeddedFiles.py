# Photos.sqlite
# Author:  Scott Koenig, assisted by past contributors
# Version: 2.0
#
#   Description:
#   Parses basic asset record data from Photos.sqlite for assets that have embedded files.
#   This parser should be used in conjunction with other parsers to review a complete record for analysis.
#   The results of this parser could produce multiple records for a single asset.
#   This parser is based on research and SQLite queries written by Scott Koenig
#   https://theforensicscooter.com/ and queries found at https://github.com/ScottKjr3347
#

import os
import plistlib
import nska_deserialize as nd
import scripts.artifacts.artGlobals
from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, media_to_html, open_sqlite_db_readonly


def get_ph10assetparsedembeddedfilesphdapsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            break
      
    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("10.3.4"):
        logfunc("Unsupported ios version for PhotosData-Photos.sqlite assets have embedded files from iOS " + iosversion)
    if (version.parse(iosversion) >= version.parse("11")) & (version.parse(iosversion) < version.parse("13")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data-HasDataIndicator',
        zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data-HasDataIndicator',
        zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',      
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZGENERICASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                aaashiftedlocation_geoplaceresult = ''
                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                aaareverselocation_geoplaceresult = ''

                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                if row[8] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[8])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)
                        for key, val in plist.items():
                            if key == "geoPlaceResult":
                                aaashiftedlocation_geoplaceresult = val

                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                if row[11] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[11])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)
                        for key, val in plist.items():
                            if key == "geoPlaceResult":
                                aaareverselocation_geoplaceresult = val

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                  aaashiftedlocation_geoplaceresult,
                                  row[9], row[10],
                                  aaareverselocation_geoplaceresult,
                                  row[12], row[13], row[14], row[15]))

                counter += 1

            description = 'Parses basic asset record data from Photos.sqlite for assets that have embedded files' \
                          ' records for a variety of data. This parser should be used in conjunction with other' \
                          ' parsers to review a complete record for analysis. The results of this parser could' \
                          ' produce multiple records for a single asset.'
            report = ArtifactHtmlReport('Ph10.1-Assets have embedded files-PhDaPsql')
            report.start_artifact_report(report_folder, 'Ph10.1-Assets have embedded files-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Directory-Path-1',
                            'zAsset-Filename-2',
                            'zAddAssetAttr- Original Filename-3',
                            'zCldMast- Original Filename-4',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-5',
                            'zAddAssetAttr-Shifted Location Valid-6',
                            'zAddAssetAttr-Shifted Location Data-HasDataIndicator-7',
                            'zAddAssetAttr-Shifted Location Data-geoPlaceResult-8',
                            'zAddAssetAttr-Reverse Location Is Valid-9',
                            'zAddAssetAttr-Reverse Location Data-HasDataIndicator-10',
                            'zAddAssetAttr-Reverse Location Data-geoPlaceResult-11',
                            'zAsset-zPK-12',
                            'zAddAssetAttr-zPK-13',
                            'zAsset-UUID = store.cloudphotodb-14',
                            'zAddAssetAttr-Master Fingerprint-15')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph10.1-Assets have embedded files-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph10.1-Assets have embedded files-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite assets having embedded files')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("13")) & (version.parse(iosversion) < version.parse("14")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',        
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data-HasDataIndicator',
        zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data-HasDataIndicator',
        zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',		
        zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
        AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
        AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
        zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
        CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data-HasDataIndicator',		
        CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZGENERICASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                aaashiftedlocation_postal_address = ''
                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                aaareverselocation_postal_address = ''
                # AAAzCldMastMedData.ZDATA-PLIST
                aaazcldmastmeddata_plist_tiff = ''
                aaazcldmastmeddata_plist_exif = ''
                aaazcldmastmeddata_plist_gps = ''
                aaazcldmastmeddata_plist_iptc = ''
                # CMzCldMastMedData.ZDATA-PLIST
                cmzcldmastmeddata_plist_tiff = ''
                cmzcldmastmeddata_plist_exif = ''
                cmzcldmastmeddata_plist_gps = ''
                cmzcldmastmeddata_plist_iptc = ''

                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                if row[8] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[8])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaashiftedlocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename' + row[2])

                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                if row[11] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[11])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaareverselocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename' + row[2])

                # AAAzCldMastMedData.ZDATA-PLIST
                if row[17] is not None:
                    pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[17])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                aaazcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                aaazcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                aaazcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                aaazcldmastmeddata_plist_iptc = val

                # CMzCldMastMedData.ZDATA-PLIST
                if row[23] is not None:
                    pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[23])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                cmzcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                cmzcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                cmzcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                cmzcldmastmeddata_plist_iptc = val

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                aaashiftedlocation_postal_address,
                                row[9], row[10],
                                aaareverselocation_postal_address,
                                row[12], row[13], row[14], row[15], row[16],
                                aaazcldmastmeddata_plist_tiff,
                                aaazcldmastmeddata_plist_exif,
                                aaazcldmastmeddata_plist_gps,
                                aaazcldmastmeddata_plist_iptc,
                                row[18], row[19], row[20], row[21], row[22],
                                cmzcldmastmeddata_plist_tiff,
                                cmzcldmastmeddata_plist_exif,
                                cmzcldmastmeddata_plist_gps,
                                cmzcldmastmeddata_plist_iptc,
                                row[24], row[25], row[26], row[27]))

                counter += 1

            description = 'Parses basic asset record data from Photos.sqlite for assets that have embedded files' \
                          ' records for a variety of data. This parser should be used in conjunction with other' \
                          ' parsers to review a complete record for analysis. The results of this parser could' \
                          ' produce multiple records for a single asset.'
            report = ArtifactHtmlReport('Ph10.1-Assets have embedded files-PhDaPsql')
            report.start_artifact_report(report_folder, 'Ph10.1-Assets have embedded files-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Directory-Path-1',
                            'zAsset-Filename-2',
                            'zAddAssetAttr- Original Filename-3',
                            'zCldMast- Original Filename-4',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-5',
                            'zAddAssetAttr-Shifted Location Valid-6',
                            'zAddAssetAttr-Shifted Location Data-HasDataIndicator7-',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address-8',
                            'zAddAssetAttr-Reverse Location Is Valid-9',
                            'zAddAssetAttr-Reverse Location Data-HasDataIndicator-10',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address-11',
                            'AAAzCldMastMedData-zOPT-12',
                            'zAddAssetAttr-Media Metadata Type-13',
                            'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-14',
                            'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast- MediaMetaData-15',
                            'AAAzCldMastMedData-Data-HasDataIndicator-16',
                            'AAAzCldMastMedData-Data_plist_TIFF-17',
                            'AAAzCldMastMedData-Data_plist_Exif-17',
                            'AAAzCldMastMedData-Data_plist_GPS-17',
                            'AAAzCldMastMedData-Data_plist_IPTC-17',
                            'CldMasterzCldMastMedData-zOPT-18',
                            'zCldMast-Media Metadata Type-19',
                            'zCldMast-Media Metadata Key= zCldMastMedData-zPK-20',
                            'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast- MediaMetaData Key-21',
                            'CMzCldMastMedData-Data-HasDataIndicator-22',
                            'CMzCldMastMedData-Data_plist_TIFF-23',
                            'CMzCldMastMedData-Data_plist_Exif-23',
                            'CMzCldMastMedData-Data_plist_GPS-23',
                            'CMzCldMastMedData-Data_plist_IPTC-23',
                            'zAsset-zPK-24',
                            'zAddAssetAttr-zPK-25',
                            'zAsset-UUID = store.cloudphotodb-26',
                            'zAddAssetAttr-Master Fingerprint-27')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph10.1-Assets have embedded files-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph10.1-Assets have embedded files-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite assets having embedded files')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("15")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT 
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data-HasDataIndicator',
        zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data-HasDataIndicator',
        zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',		
        zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
        AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
        AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
        zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
        CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data-HasDataIndicator',		
        CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',
        CASE zSharePartic.ZACCEPTANCESTATUS
            WHEN 1 THEN '1-Invite-Pending_or_Declined-1'
            WHEN 2 THEN '2-Invite-Accepted-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZACCEPTANCESTATUS || ''
        END AS 'zSharePartic-Acceptance Status',
        zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
        zSharePartic.Z_PK AS 'zSharePartic-zPK',
        zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
        zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',
        CASE
            WHEN zSharePartic.ZNAMECOMPONENTS > 0 THEN 'zSharePartic-Name_Components_has_Plist'
            ELSE 'zSharePartic-Name_Components_Empty-NULL'
        END AS 'zSharePartic-Name_Components-HasDataIndicator',
        zSharePartic.ZNAMECOMPONENTS AS 'zSharePartic-Name_Components',        
        CASE zSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_CurrentUser-0'
            WHEN 1 THEN '1-Participant-Is_CurrentUser-1'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZISCURRENTUSER || ''
        END AS 'zSharePartic-Is Current User',
        CASE zSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZROLE || ''
        END AS 'zSharePartic-Role',
        CASE
            WHEN zShare.ZPREVIEWDATA > 0 THEN 'zShare-Preview_Data_has_BLOB'
            ELSE 'zShare-Preview_Data_Empty-NULL'
        END AS 'zShare-Preview_Data-DataIndicator',
        zShare.ZPREVIEWDATA AS 'zShare-Preview_Data',
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
            LEFT JOIN ZSHARE zShare ON zShare.Z_PK = zAsset.ZMOMENTSHARE
            LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                aaashiftedlocation_postal_address = ''
                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                aaareverselocation_postal_address = ''
                # AAAzCldMastMedData.ZDATA-PLIST
                aaazcldmastmeddata_plist_tiff = ''
                aaazcldmastmeddata_plist_exif = ''
                aaazcldmastmeddata_plist_gps = ''
                aaazcldmastmeddata_plist_iptc = ''
                # CMzCldMastMedData.ZDATA-PLIST
                cmzcldmastmeddata_plist_tiff = ''
                cmzcldmastmeddata_plist_exif = ''
                cmzcldmastmeddata_plist_gps = ''
                cmzcldmastmeddata_plist_iptc = ''
                # zSharePartic_ZNAMECOMPONENTS_PLIST
                zsharepartic_namecomponents = ''
                # zShare.ZPREVIEWDATA-BLOB_JPG
                zshare_previewdata_blob = ''

                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                if row[8] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[8])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaashiftedlocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename' + row[2])

                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                if row[11] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[11])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaareverselocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename' + row[2])

                # AAAzCldMastMedData.ZDATA-PLIST
                if row[17] is not None:
                    pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[17])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                aaazcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                aaazcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                aaazcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                aaazcldmastmeddata_plist_iptc = val

                # CMzCldMastMedData.ZDATA-PLIST
                if row[23] is not None:
                    pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[23])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                cmzcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                cmzcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                cmzcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                cmzcldmastmeddata_plist_iptc = val

                # zSharePartic_ZNAMECOMPONENTS_PLIST
                if row[30] is not None:
                    pathto = os.path.join(report_folder, 'zSP_Name_Components_' + row[2] + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[30])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            zsharepartic_namecomponents = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from Asset PK ' + row[2])

                # zShare.ZPREVIEWDATA-BLOB_JPG
                if row[34] is not None:
                    pathto = os.path.join(report_folder, 'zShare_PreviewData_' + row[2] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[34])
                    zshare_previewdata_blob = media_to_html(pathto, files_found, report_folder)

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                aaashiftedlocation_postal_address,
                                row[9], row[10],
                                aaareverselocation_postal_address,
                                row[12], row[13], row[14], row[15], row[16],
                                aaazcldmastmeddata_plist_tiff,
                                aaazcldmastmeddata_plist_exif,
                                aaazcldmastmeddata_plist_gps,
                                aaazcldmastmeddata_plist_iptc,
                                row[18], row[19], row[20], row[21], row[22],
                                cmzcldmastmeddata_plist_tiff,
                                cmzcldmastmeddata_plist_exif,
                                cmzcldmastmeddata_plist_gps,
                                cmzcldmastmeddata_plist_iptc,
                                row[24], row[25], row[26], row[27], row[28], row[29],
                                zsharepartic_namecomponents,
                                row[31], row[32], row[33],
                                zshare_previewdata_blob,
                                row[35], row[36], row[37], row[38]))

                counter += 1

            description = 'Parses basic asset record data from Photos.sqlite for assets that have embedded files' \
                          ' records for a variety of data. This parser should be used in conjunction with other' \
                          ' parsers to review a complete record for analysis. The results of this parser could' \
                          ' produce multiple records for a single asset.'
            report = ArtifactHtmlReport('Ph10.1-Assets have embedded files-PhDaPsql')
            report.start_artifact_report(report_folder, 'Ph10.1-Assets have embedded files-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Directory-Path-1',
                            'zAsset-Filename-2',
                            'zAddAssetAttr- Original Filename-3',
                            'zCldMast- Original Filename-4',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-5',
                            'zAddAssetAttr-Shifted Location Valid-6',
                            'zAddAssetAttr-Shifted Location Data-HasDataIndicator-7',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address-8',
                            'zAddAssetAttr-Reverse Location Is Valid-9',
                            'zAddAssetAttr-Reverse Location Data-HasDataIndicator-10',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address-11',
                            'AAAzCldMastMedData-zOPT-12',
                            'zAddAssetAttr-Media Metadata Type-13',
                            'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-14',
                            'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-15',
                            'AAAzCldMastMedData-Data-HasDataIndicator-16',
                            'AAAzCldMastMedData-Data_plist_TIFF-17',
                            'AAAzCldMastMedData-Data_plist_Exif-17',
                            'AAAzCldMastMedData-Data_plist_GPS-17',
                            'AAAzCldMastMedData-Data_plist_IPTC-17',
                            'CldMasterzCldMastMedData-zOPT-18',
                            'zCldMast-Media Metadata Type-19',
                            'zCldMast-Media Metadata Key= zCldMastMedData.zPK-20',
                            'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-21',
                            'CMzCldMastMedData-Data-HasDataIndicator-22',
                            'CMzCldMastMedData-Data_plist_TIFF-23',
                            'CMzCldMastMedData-Data_plist_Exif-23',
                            'CMzCldMastMedData-Data_plist_GPS-23',
                            'CMzCldMastMedData-Data_plist_IPTC-23',
                            'zSharePartic-Acceptance Status-24',
                            'zSharePartic-User ID-25',
                            'zSharePartic-zPK-26',
                            'zSharePartic-Email Address-27',
                            'zSharePartic-Phone Number-28',
                            'zSharePartic-Name_Components-HasDataIndicator-29',
                            'zSharePartic-Name_Components_Plist-30',
                            'zSharePartic-Is Current User-31',
                            'zSharePartic-Role-32',
                            'zShare-Preview_Data-DataIndicator-33',
                            'zShare-Preview_Data-BLOB_JPG-34',
                            'zAsset-zPK-35',
                            'zAddAssetAttr-zPK-36',
                            'zAsset-UUID = store.cloudphotodb-37',
                            'zAddAssetAttr-Master Fingerprint-38')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph10.1-Assets have embedded files-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph10.1-Assets have embedded files-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite assets having embedded files')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data-HasDataIndicator',
        zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data-HasDataIndicator',
        zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',		
        zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
        AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
        AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
        zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
        CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data-HasDataIndicator',
        CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',
        CASE zSharePartic.ZACCEPTANCESTATUS
            WHEN 1 THEN '1-Invite-Pending_or_Declined-1'
            WHEN 2 THEN '2-Invite-Accepted-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZACCEPTANCESTATUS || ''
        END AS 'zSharePartic-Acceptance Status',
        zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
        zSharePartic.Z_PK AS 'zSharePartic-zPK',
        zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
        zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',
        CASE
            WHEN zSharePartic.ZNAMECOMPONENTS > 0 THEN 'zSharePartic-Name_Components_has_Plist'
            ELSE 'zSharePartic-Name_Components_Empty-NULL'
        END AS 'zSharePartic-Name_Components-HasDataIndicator',
        zSharePartic.ZNAMECOMPONENTS AS 'zSharePartic-Name_Components',        
        CASE zSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_CurrentUser-0'
            WHEN 1 THEN '1-Participant-Is_CurrentUser-1'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZISCURRENTUSER || ''
        END AS 'zSharePartic-Is Current User',
        CASE zSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZROLE || ''
        END AS 'zSharePartic-Role',
        CASE
            WHEN zShare.ZPREVIEWDATA > 0 THEN 'zShare-Preview_Data_has_BLOB'
            ELSE 'zShare-Preview_Data_Empty-NULL'
        END AS 'zShare-Preview_Data-DataIndicator',
        zShare.ZPREVIEWDATA AS 'zShare-Preview_Data',        
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
            LEFT JOIN ZSHARE zShare ON zShare.Z_PK = zAsset.ZMOMENTSHARE
            LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                aaashiftedlocation_postal_address = ''
                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                aaareverselocation_postal_address = ''
                # AAAzCldMastMedData.ZDATA-PLIST
                aaazcldmastmeddata_plist_tiff = ''
                aaazcldmastmeddata_plist_exif = ''
                aaazcldmastmeddata_plist_gps = ''
                aaazcldmastmeddata_plist_iptc = ''
                # CMzCldMastMedData.ZDATA-PLIST
                cmzcldmastmeddata_plist_tiff = ''
                cmzcldmastmeddata_plist_exif = ''
                cmzcldmastmeddata_plist_gps = ''
                cmzcldmastmeddata_plist_iptc = ''
                # zSharePartic_ZNAMECOMPONENTS_PLIST
                zsharepartic_namecomponents = ''
                # zShare.ZPREVIEWDATA-BLOB_JPG
                zshare_previewdata_blob = ''

                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                if row[9] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[9])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaashiftedlocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename' + row[2])

                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                if row[12] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[12])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaareverselocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename' + row[2])

                # AAAzCldMastMedData.ZDATA-PLIST
                if row[18] is not None:
                    pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[18])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                aaazcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                aaazcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                aaazcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                aaazcldmastmeddata_plist_iptc = val

                # CMzCldMastMedData.ZDATA-PLIST
                if row[24] is not None:
                    pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[24])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                cmzcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                cmzcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                cmzcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                cmzcldmastmeddata_plist_iptc = val

                # zSharePartic_ZNAMECOMPONENTS_PLIST
                if row[31] is not None:
                    pathto = os.path.join(report_folder, 'zSP_Name_Components_' + row[2] + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[31])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            zsharepartic_namecomponents = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from zAsset-Filename' + row[2])

                # zShare.ZPREVIEWDATA-BLOB_JPG
                if row[35] is not None:
                    pathto = os.path.join(report_folder, 'zShare_PreviewData_' + row[2] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[35])
                    zshare_previewdata_blob = media_to_html(pathto, files_found, report_folder)

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8],
                                  aaashiftedlocation_postal_address,
                                  row[10], row[11],
                                  aaareverselocation_postal_address,
                                  row[13], row[14], row[15], row[16], row[17],
                                  aaazcldmastmeddata_plist_tiff,
                                  aaazcldmastmeddata_plist_exif,
                                  aaazcldmastmeddata_plist_gps,
                                  aaazcldmastmeddata_plist_iptc,
                                  row[19], row[20], row[21], row[22], row[23],
                                  cmzcldmastmeddata_plist_tiff,
                                  cmzcldmastmeddata_plist_exif,
                                  cmzcldmastmeddata_plist_gps,
                                  cmzcldmastmeddata_plist_iptc,
                                  row[25], row[26], row[27], row[28], row[29], row[30],
                                  zsharepartic_namecomponents,
                                  row[32], row[33], row[34],
                                  zshare_previewdata_blob,
                                  row[36], row[37], row[38], row[39]))

                counter += 1

            description = 'Parses basic asset record data from Photos.sqlite for assets that have embedded files' \
                          ' records for a variety of data. This parser should be used in conjunction with other' \
                          ' parsers to review a complete record for analysis. The results of this parser could' \
                          ' produce multiple records for a single asset.'
            report = ArtifactHtmlReport('Ph10.1-Assets have embedded files-PhDaPsql')
            report.start_artifact_report(report_folder, 'Ph10.1-Assets have embedded files-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Directory-Path-1',
                            'zAsset-Filename-2',
                            'zAddAssetAttr- Original Filename-3',
                            'zCldMast- Original Filename-4',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-5',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-6',
                            'zAddAssetAttr-Shifted Location Valid-7',
                            'zAddAssetAttr-Shifted Location Data-HasDataIndicator-8',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address-9',
                            'zAddAssetAttr-Reverse Location Is Valid-10',
                            'zAddAssetAttr-Reverse Location Data-HasDataIndicator-11',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address-12',
                            'AAAzCldMastMedData-zOPT-13',
                            'zAddAssetAttr-Media Metadata Type-14',
                            'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-15',
                            'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-16',
                            'AAAzCldMastMedData-Data-HasDataIndicator-17',
                            'AAAzCldMastMedData-Data_plist_TIFF-18',
                            'AAAzCldMastMedData-Data_plist_Exif-18',
                            'AAAzCldMastMedData-Data_plist_GPS-18',
                            'AAAzCldMastMedData-Data_plist_IPTC-18',
                            'CldMasterzCldMastMedData-zOPT-19',
                            'zCldMast-Media Metadata Type-20',
                            'zCldMast-Media Metadata Key= zCldMastMedData.zPK-21',
                            'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-22',
                            'CMzCldMastMedData-Data-HasDataIndicator-23',
                            'CMzCldMastMedData-Data_plist_TIFF-24',
                            'CMzCldMastMedData-Data_plist_Exif-24',
                            'CMzCldMastMedData-Data_plist_GPS-24',
                            'CMzCldMastMedData-Data_plist_IPTC-24',
                            'zSharePartic-Acceptance Status-25',
                            'zSharePartic-User ID-26',
                            'zSharePartic-zPK-27',
                            'zSharePartic-Email Address-28',
                            'zSharePartic-Phone Number-29',
                            'zSharePartic-Name_Components-HasDataIndicator-30',
                            'zSharePartic-Name_Components_Plist-31',
                            'zSharePartic-Is Current User-32',
                            'zSharePartic-Role-33',
                            'zShare-Preview_Data-DataIndicator-34',
                            'zShare-Preview_Data-BLOB_JPG-35',
                            'zAsset-zPK-36',
                            'zAddAssetAttr-zPK-37',
                            'zAsset-UUID = store.cloudphotodb-38',
                            'zAddAssetAttr-Master Fingerprint-39')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph10.1-Assets have embedded files-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph10.1-Assets have embedded files-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite assets having embedded files')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("17")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data-HasDataIndicator',
        zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data-HasDataIndicator',
        zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',		
        zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
        AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
        AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
        zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
        CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data-HasDataIndicator',
        CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',
        CASE zSharePartic.ZACCEPTANCESTATUS
            WHEN 1 THEN '1-Invite-Pending_or_Declined-1'
            WHEN 2 THEN '2-Invite-Accepted-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZACCEPTANCESTATUS || ''
        END AS 'zSharePartic-Acceptance Status',
        zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
        zSharePartic.Z_PK AS 'zSharePartic-zPK',
        zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
        zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',
        CASE
            WHEN zSharePartic.ZNAMECOMPONENTS > 0 THEN 'zSharePartic-Name_Components_has_Plist'
            ELSE 'zSharePartic-Name_Components_Empty-NULL'
        END AS 'zSharePartic-Name_Components-HasDataIndicator',
        zSharePartic.ZNAMECOMPONENTS AS 'zSharePartic-Name_Components',        
        CASE zSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_CurrentUser-0'
            WHEN 1 THEN '1-Participant-Is_CurrentUser-1'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZISCURRENTUSER || ''
        END AS 'zSharePartic-Is Current User',
        CASE zSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZROLE || ''
        END AS 'zSharePartic-Role',
        CASE
            WHEN zShare.ZPREVIEWDATA > 0 THEN 'zShare-Preview_Data_has_BLOB'
            ELSE 'zShare-Preview_Data_Empty-NULL'
        END AS 'zShare-Preview_Data-DataIndicator',
        zShare.ZPREVIEWDATA AS 'zShare-Preview_Data',
        CASE SPLzSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_CurrentUser-0'
            WHEN 1 THEN '1-Participant-Is_CurrentUser-1'
            ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZISCURRENTUSER || ''
        END AS 'SPLzSharePartic-Is Current User',
        CASE SPLzSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZROLE || ''
        END AS 'SPLzSharePartic-Role',
        zAssetContrib.ZPARTICIPANT AS 'zAsstContrib-Participant= zSharePartic-zPK',
        SPLzSharePartic.ZEMAILADDRESS AS 'SPLzSharePartic-Email Address',
        SPLzSharePartic.ZPHONENUMBER AS 'SPLzSharePartic-Phone Number',
        CASE
            WHEN SPLzSharePartic.ZNAMECOMPONENTS > 0 THEN 'SPLzSharePartic-Name_Components_has_Plist'
            ELSE 'SPLzSharePartic-Name_Components_Empty-NULL'
        END AS 'SPLzSharePartic-Name_Components-HasDataIndicator',
        SPLzSharePartic.ZNAMECOMPONENTS AS 'SPLzSharePartic-Name_Components',
        CASE
            WHEN SPLzShare.ZPREVIEWDATA > 0 THEN 'SPLzShare-Preview_Data_has_BLOB'
            ELSE 'SPLzShare-Preview_Data_Empty-NULL'
        END AS 'SPLzShare-Preview_Data-DataIndicator',
        SPLzShare.ZPREVIEWDATA AS 'SPLzShare-Preview_Data',
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
            LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
            LEFT JOIN ZSHARE zShare ON zShare.Z_PK = zAsset.ZMOMENTSHARE
            LEFT JOIN ZASSETCONTRIBUTOR zAssetContrib ON zAssetContrib.Z3LIBRARYSCOPEASSETCONTRIBUTORS = zAsset.Z_PK
            LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
            LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.Z_PK = zAssetContrib.ZPARTICIPANT
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                aaashiftedlocation_postal_address = ''
                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                aaareverselocation_postal_address = ''
                # AAAzCldMastMedData.ZDATA-PLIST
                aaazcldmastmeddata_plist_tiff = ''
                aaazcldmastmeddata_plist_exif = ''
                aaazcldmastmeddata_plist_gps = ''
                aaazcldmastmeddata_plist_iptc = ''
                # CMzCldMastMedData.ZDATA-PLIST
                cmzcldmastmeddata_plist_tiff = ''
                cmzcldmastmeddata_plist_exif = ''
                cmzcldmastmeddata_plist_gps = ''
                cmzcldmastmeddata_plist_iptc = ''
                # zSharePartic_ZNAMECOMPONENTS_PLIST
                zsharepartic_namecomponents = ''
                # SPLzSharePartic_ZNAMECOMPONENTS_PLIST
                splzsharepartic_namecomponents = ''
                # zShare.ZPREVIEWDATA-BLOB_JPG
                zshare_previewdata_blob = ''
                # SPLzShare.ZPREVIEWDATA-BLOB_JPG
                splzshare_previewdata_blob = ''

                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                if row[9] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[9])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaashiftedlocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename' + row[2])

                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                if row[12] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[12])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaareverselocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename ' + row[2])

                # AAAzCldMastMedData.ZDATA-PLIST
                if row[18] is not None:
                    pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[18])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                aaazcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                aaazcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                aaazcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                aaazcldmastmeddata_plist_iptc = val

                # CMzCldMastMedData.ZDATA-PLIST
                if row[24] is not None:
                    pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[24])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                cmzcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                cmzcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                cmzcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                cmzcldmastmeddata_plist_iptc = val

                # zSharePartic_ZNAMECOMPONENTS_PLIST
                if row[31] is not None:
                    pathto = os.path.join(report_folder, 'zSP_Name_Components_' + row[2] + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[31])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            zsharepartic_namecomponents = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from zAsset-Filename' + row[2])

                # SPLzSharePartic_ZNAMECOMPONENTS_PLIST
                if row[42] is not None:
                    pathto = os.path.join(report_folder, 'SPLzSharePartic-Name_Components_' + row[2] + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[42])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            splzsharepartic_namecomponents = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from zAsset-Filename' + row[2])

                # zShare.ZPREVIEWDATA-BLOB_JPG
                if row[35] is not None:
                    pathto = os.path.join(report_folder, 'zShare_PreviewData_' + row[2] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[35])
                    zshare_previewdata_blob = media_to_html(pathto, files_found, report_folder)

                # SPLzShare.ZPREVIEWDATA-BLOB_JPG
                if row[44] is not None:
                    pathto = os.path.join(report_folder, 'SPLzShare_PreviewData_' + row[2] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[44])
                    splzshare_previewdata_blob = media_to_html(pathto, files_found, report_folder)

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8],
                                  aaashiftedlocation_postal_address,
                                  row[10], row[11],
                                  aaareverselocation_postal_address,
                                  row[13], row[14], row[15], row[16], row[17],
                                  aaazcldmastmeddata_plist_tiff,
                                  aaazcldmastmeddata_plist_exif,
                                  aaazcldmastmeddata_plist_gps,
                                  aaazcldmastmeddata_plist_iptc,
                                  row[19], row[20], row[21], row[22], row[23],
                                  cmzcldmastmeddata_plist_tiff,
                                  cmzcldmastmeddata_plist_exif,
                                  cmzcldmastmeddata_plist_gps,
                                  cmzcldmastmeddata_plist_iptc,
                                  row[25], row[26], row[27], row[28], row[29], row[30],
                                  zsharepartic_namecomponents,
                                  row[32], row[33], row[34],
                                  zshare_previewdata_blob,
                                  row[36], row[37],
                                  row[38], row[39], row[40], row[41],
                                  splzsharepartic_namecomponents,
                                  row[43],
                                  splzshare_previewdata_blob,
                                  row[45], row[46], row[47], row[48]))

                counter += 1

            description = 'Parses basic asset record data from Photos.sqlite for assets that have embedded files' \
                          ' records for a variety of data. This parser should be used in conjunction with other' \
                          ' parsers to review a complete record for analysis. The results of this parser could' \
                          ' produce multiple records for a single asset.'
            report = ArtifactHtmlReport('Ph10.1-Assets have embedded files-PhDaPsql')
            report.start_artifact_report(report_folder, 'Ph10.1-Assets have embedded files-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Directory-Path-1',
                            'zAsset-Filename-2',
                            'zAddAssetAttr- Original Filename-3',
                            'zCldMast- Original Filename-4',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-5',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-6',
                            'zAddAssetAttr-Shifted Location Valid-7',
                            'zAddAssetAttr-Shifted Location Data-HasDataIndicator-8',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address-9',
                            'zAddAssetAttr-Reverse Location Is Valid-10',
                            'zAddAssetAttr-Reverse Location Data-HasDataIndicator-11',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address-12',
                            'AAAzCldMastMedData-zOPT-13',
                            'zAddAssetAttr-Media Metadata Type-14',
                            'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-15',
                            'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-16',
                            'AAAzCldMastMedData-Data-HasDataIndicator-17',
                            'AAAzCldMastMedData-Data_plist_TIFF-18',
                            'AAAzCldMastMedData-Data_plist_Exif-18',
                            'AAAzCldMastMedData-Data_plist_GPS-18',
                            'AAAzCldMastMedData-Data_plist_IPTC-18',
                            'CldMasterzCldMastMedData-zOPT-19',
                            'zCldMast-Media Metadata Type-20',
                            'zCldMast-Media Metadata Key= zCldMastMedData.zPK-21',
                            'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-22',
                            'CMzCldMastMedData-Data-HasDataIndicator-23',
                            'CMzCldMastMedData-Data_plist_TIFF-24',
                            'CMzCldMastMedData-Data_plist_Exif-24',
                            'CMzCldMastMedData-Data_plist_GPS-24',
                            'CMzCldMastMedData-Data_plist_IPTC-24',
                            'zSharePartic-Acceptance Status-25',
                            'zSharePartic-User ID-26',
                            'zSharePartic-zPK-27',
                            'zSharePartic-Email Address-28',
                            'zSharePartic-Phone Number-29',
                            'zSharePartic-Name_Components-HasDataIndicator-30',
                            'zSharePartic-Name_Components_Plist-31',
                            'zSharePartic-Is Current User-32',
                            'zSharePartic-Role-33',
                            'zShare-Preview_Data-DataIndicator-34',
                            'zShare-Preview_Data-BLOB_JPG-35',
                            'SPLzSharePartic-Is Current User-36',
                            'SPLzSharePartic-Role-37',
                            'zAsstContrib-Participant= zSharePartic-zPK-38',
                            'SPLzSharePartic-Email Address-39',
                            'SPLzSharePartic-Phone Number-40',
                            'SPLzSharePartic-Name_Components-HasDataIndicator-41',
                            'SPLzSharePartic-Name_Components_Plist-42',
                            'zShare-Preview_Data-DataIndicator-43',
                            'zShare-Preview_Data-BLOB_JPG-44',
                            'zAsset-zPK-45',
                            'zAddAssetAttr-zPK-46',
                            'zAsset-UUID = store.cloudphotodb-47',
                            'zAddAssetAttr-Master Fingerprint-48')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph10.1-Assets have embedded files-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph10.1-Assets have embedded files-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite assets having embedded files')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("17")) & (version.parse(iosversion) < version.parse("18")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data-HasDataIndicator',
        zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data-HasDataIndicator',
        zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',		
        zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
        AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
        AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
        zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
        CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data-HasDataIndicator',
        CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',
        CASE zSharePartic.ZACCEPTANCESTATUS
            WHEN 1 THEN '1-Invite-Pending_or_Declined-1'
            WHEN 2 THEN '2-Invite-Accepted-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZACCEPTANCESTATUS || ''
        END AS 'zSharePartic-Acceptance Status',
        zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
        zSharePartic.Z_PK AS 'zSharePartic-zPK',
        zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
        zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',
        CASE
            WHEN zSharePartic.ZNAMECOMPONENTS > 0 THEN 'zSharePartic-Name_Components_has_Plist'
            ELSE 'zSharePartic-Name_Components_Empty-NULL'
        END AS 'zSharePartic-Name_Components-HasDataIndicator',
        zSharePartic.ZNAMECOMPONENTS AS 'zSharePartic-Name_Components',        
        CASE zSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_CurrentUser-0'
            WHEN 1 THEN '1-Participant-Is_CurrentUser-1'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZISCURRENTUSER || ''
        END AS 'zSharePartic-Is Current User',
        CASE zSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZROLE || ''
        END AS 'zSharePartic-Role',
        CASE
            WHEN zShare.ZPREVIEWDATA > 0 THEN 'zShare-Preview_Data_has_BLOB'
            ELSE 'zShare-Preview_Data_Empty-NULL'
        END AS 'zShare-Preview_Data-DataIndicator',
        zShare.ZPREVIEWDATA AS 'zShare-Preview_Data',
        CASE SPLzSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_CurrentUser-0'
            WHEN 1 THEN '1-Participant-Is_CurrentUser-1'
            ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZISCURRENTUSER || ''
        END AS 'SPLzSharePartic-Is Current User',
        CASE SPLzSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZROLE || ''
        END AS 'SPLzSharePartic-Role',
        zAssetContrib.ZPARTICIPANT AS 'zAsstContrib-Participant= zSharePartic-zPK',
        SPLzSharePartic.ZEMAILADDRESS AS 'SPLzSharePartic-Email Address',
        SPLzSharePartic.ZPHONENUMBER AS 'SPLzSharePartic-Phone Number',
        CASE
            WHEN SPLzSharePartic.ZNAMECOMPONENTS > 0 THEN 'SPLzSharePartic-Name_Components_has_Plist'
            ELSE 'SPLzSharePartic-Name_Components_Empty-NULL'
        END AS 'SPLzSharePartic-Name_Components-HasDataIndicator',
        SPLzSharePartic.ZNAMECOMPONENTS AS 'SPLzSharePartic-Name_Components',
        CASE
            WHEN SPLzShare.ZPREVIEWDATA > 0 THEN 'SPLzShare-Preview_Data_has_BLOB'
            ELSE 'SPLzShare-Preview_Data_Empty-NULL'
        END AS 'SPLzShare-Preview_Data-DataIndicator',
        SPLzShare.ZPREVIEWDATA AS 'SPLzShare-Preview_Data',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
        zAddAssetAttr.ZADJUSTEDFINGERPRINT AS 'zAddAssetAttr.Adjusted Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
            LEFT JOIN ZSHARE zShare ON zShare.Z_PK = zAsset.ZMOMENTSHARE
            LEFT JOIN ZASSETCONTRIBUTOR zAssetContrib ON zAssetContrib.Z3LIBRARYSCOPEASSETCONTRIBUTORS = zAsset.Z_PK
            LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
            LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.Z_PK = zAssetContrib.ZPARTICIPANT
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                aaashiftedlocation_postal_address = ''
                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                aaareverselocation_postal_address = ''
                # AAAzCldMastMedData.ZDATA-PLIST
                aaazcldmastmeddata_plist_tiff = ''
                aaazcldmastmeddata_plist_exif = ''
                aaazcldmastmeddata_plist_gps = ''
                aaazcldmastmeddata_plist_iptc = ''
                # CMzCldMastMedData.ZDATA-PLIST
                cmzcldmastmeddata_plist_tiff = ''
                cmzcldmastmeddata_plist_exif = ''
                cmzcldmastmeddata_plist_gps = ''
                cmzcldmastmeddata_plist_iptc = ''
                # zSharePartic_ZNAMECOMPONENTS_PLIST
                zsharepartic_namecomponents = ''
                # SPLzSharePartic_ZNAMECOMPONENTS_PLIST
                splzsharepartic_namecomponents = ''
                # zShare.ZPREVIEWDATA-BLOB_JPG
                zshare_previewdata_blob = ''
                # SPLzShare.ZPREVIEWDATA-BLOB_JPG
                splzshare_previewdata_blob = ''

                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                if row[9] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[9])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaashiftedlocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename' + row[2])

                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                if row[12] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[12])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaareverselocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename ' + row[2])

                # AAAzCldMastMedData.ZDATA-PLIST
                if row[18] is not None:
                    pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[18])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                aaazcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                aaazcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                aaazcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                aaazcldmastmeddata_plist_iptc = val

                # CMzCldMastMedData.ZDATA-PLIST
                if row[24] is not None:
                    pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[24])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                cmzcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                cmzcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                cmzcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                cmzcldmastmeddata_plist_iptc = val

                # zSharePartic_ZNAMECOMPONENTS_PLIST
                if row[31] is not None:
                    pathto = os.path.join(report_folder, 'zSP_Name_Components_' + row[2] + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[31])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            zsharepartic_namecomponents = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from zAsset-Filename' + row[2])

                # SPLzSharePartic_ZNAMECOMPONENTS_PLIST
                if row[42] is not None:
                    pathto = os.path.join(report_folder, 'SPLzSharePartic-Name_Components_' + row[2] + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[42])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            splzsharepartic_namecomponents = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from zAsset-Filename' + row[2])

                # zShare.ZPREVIEWDATA-BLOB_JPG
                if row[35] is not None:
                    pathto = os.path.join(report_folder, 'zShare_PreviewData_' + row[2] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[35])
                    zshare_previewdata_blob = media_to_html(pathto, files_found, report_folder)

                # SPLzShare.ZPREVIEWDATA-BLOB_JPG
                if row[44] is not None:
                    pathto = os.path.join(report_folder, 'SPLzShare_PreviewData_' + row[2] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[44])
                    splzshare_previewdata_blob = media_to_html(pathto, files_found, report_folder)

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8],
                                  aaashiftedlocation_postal_address,
                                  row[10], row[11],
                                  aaareverselocation_postal_address,
                                  row[13], row[14], row[15], row[16], row[17],
                                  aaazcldmastmeddata_plist_tiff,
                                  aaazcldmastmeddata_plist_exif,
                                  aaazcldmastmeddata_plist_gps,
                                  aaazcldmastmeddata_plist_iptc,
                                  row[19], row[20], row[21], row[22], row[23],
                                  cmzcldmastmeddata_plist_tiff,
                                  cmzcldmastmeddata_plist_exif,
                                  cmzcldmastmeddata_plist_gps,
                                  cmzcldmastmeddata_plist_iptc,
                                  row[25], row[26], row[27], row[28], row[29], row[30],
                                  zsharepartic_namecomponents,
                                  row[32], row[33], row[34],
                                  zshare_previewdata_blob,
                                  row[36], row[37],
                                  row[38], row[39], row[40], row[41],
                                  splzsharepartic_namecomponents,
                                  row[43],
                                  splzshare_previewdata_blob,
                                  row[45], row[46], row[47], row[48], row[49]))

                counter += 1

            description = 'Parses basic asset record data from Photos.sqlite for assets that have embedded files' \
                          ' records for a variety of data. This parser should be used in conjunction with other' \
                          ' parsers to review a complete record for analysis. The results of this parser could' \
                          ' produce multiple records for a single asset.'
            report = ArtifactHtmlReport('Ph10.1-Assets have embedded files-PhDaPsql')
            report.start_artifact_report(report_folder, 'Ph10.1-Assets have embedded files-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Directory-Path-1',
                            'zAsset-Filename-2',
                            'zAddAssetAttr- Original Filename-3',
                            'zCldMast- Original Filename-4',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-5',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-6',
                            'zAddAssetAttr-Shifted Location Valid-7',
                            'zAddAssetAttr-Shifted Location Data-HasDataIndicator-8',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address-9',
                            'zAddAssetAttr-Reverse Location Is Valid-10',
                            'zAddAssetAttr-Reverse Location Data-HasDataIndicator-11',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address-12',
                            'AAAzCldMastMedData-zOPT-13',
                            'zAddAssetAttr-Media Metadata Type-14',
                            'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-15',
                            'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-16',
                            'AAAzCldMastMedData-Data-HasDataIndicator-17',
                            'AAAzCldMastMedData-Data_plist_TIFF-18',
                            'AAAzCldMastMedData-Data_plist_Exif-18',
                            'AAAzCldMastMedData-Data_plist_GPS-18',
                            'AAAzCldMastMedData-Data_plist_IPTC-18',
                            'CldMasterzCldMastMedData-zOPT-19',
                            'zCldMast-Media Metadata Type-20',
                            'zCldMast-Media Metadata Key= zCldMastMedData.zPK-21',
                            'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-22',
                            'CMzCldMastMedData-Data-HasDataIndicator-23',
                            'CMzCldMastMedData-Data_plist_TIFF-24',
                            'CMzCldMastMedData-Data_plist_Exif-24',
                            'CMzCldMastMedData-Data_plist_GPS-24',
                            'CMzCldMastMedData-Data_plist_IPTC-24',
                            'zSharePartic-Acceptance Status-25',
                            'zSharePartic-User ID-26',
                            'zSharePartic-zPK-27',
                            'zSharePartic-Email Address-28',
                            'zSharePartic-Phone Number-29',
                            'zSharePartic-Name_Components-HasDataIndicator-30',
                            'zSharePartic-Name_Components_Plist-31',
                            'zSharePartic-Is Current User-32',
                            'zSharePartic-Role-33',
                            'zShare-Preview_Data-DataIndicator-34',
                            'zShare-Preview_Data-BLOB_JPG-35',
                            'SPLzSharePartic-Is Current User-36',
                            'SPLzSharePartic-Role-37',
                            'zAsstContrib-Participant= zSharePartic-zPK-38',
                            'SPLzSharePartic-Email Address-39',
                            'SPLzSharePartic-Phone Number-40',
                            'SPLzSharePartic-Name_Components-HasDataIndicator-41',
                            'SPLzSharePartic-Name_Components_Plist-42',
                            'zShare-Preview_Data-DataIndicator-43',
                            'zShare-Preview_Data-BLOB_JPG-44',
                            'zAsset-zPK-45',
                            'zAddAssetAttr-zPK-46',
                            'zAsset-UUID = store.cloudphotodb-47',
                            'zAddAssetAttr-Master Fingerprint-48',
                            'zAddAssetAttr.Adjusted Fingerprint-49')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph10.1-Assets have embedded files-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph10.1-Assets have embedded files-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite assets having embedded files')

        db.close()
        return

    elif version.parse(iosversion) >= version.parse("18"):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data-HasDataIndicator',
        zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data-HasDataIndicator',
        zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',		
        zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
        AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
        AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
        zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
        CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data-HasDataIndicator',
        CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',
        CASE zSharePartic.ZACCEPTANCESTATUS
            WHEN 1 THEN '1-Invite-Pending_or_Declined-1'
            WHEN 2 THEN '2-Invite-Accepted-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZACCEPTANCESTATUS || ''
        END AS 'zSharePartic-Acceptance Status',
        zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
        zSharePartic.Z_PK AS 'zSharePartic-zPK',
        zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
        zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',
        CASE
            WHEN zSharePartic.ZNAMECOMPONENTS > 0 THEN 'zSharePartic-Name_Components_has_Plist'
            ELSE 'zSharePartic-Name_Components_Empty-NULL'
        END AS 'zSharePartic-Name_Components-HasDataIndicator',
        zSharePartic.ZNAMECOMPONENTS AS 'zSharePartic-Name_Components',        
        CASE zSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_CurrentUser-0'
            WHEN 1 THEN '1-Participant-Is_CurrentUser-1'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZISCURRENTUSER || ''
        END AS 'zSharePartic-Is Current User',
        CASE zSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZROLE || ''
        END AS 'zSharePartic-Role',
        CASE
            WHEN zShare.ZPREVIEWDATA > 0 THEN 'zShare-Preview_Data_has_BLOB'
            ELSE 'zShare-Preview_Data_Empty-NULL'
        END AS 'zShare-Preview_Data-DataIndicator',
        zShare.ZPREVIEWDATA AS 'zShare-Preview_Data',
        CASE SPLzSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_CurrentUser-0'
            WHEN 1 THEN '1-Participant-Is_CurrentUser-1'
            ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZISCURRENTUSER || ''
        END AS 'SPLzSharePartic-Is Current User',
        CASE SPLzSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZROLE || ''
        END AS 'SPLzSharePartic-Role',
        zAssetContrib.ZPARTICIPANT AS 'zAsstContrib-Participant= zSharePartic-zPK',
        SPLzSharePartic.ZEMAILADDRESS AS 'SPLzSharePartic-Email Address',
        SPLzSharePartic.ZPHONENUMBER AS 'SPLzSharePartic-Phone Number',
        CASE
            WHEN SPLzSharePartic.ZNAMECOMPONENTS > 0 THEN 'SPLzSharePartic-Name_Components_has_Plist'
            ELSE 'SPLzSharePartic-Name_Components_Empty-NULL'
        END AS 'SPLzSharePartic-Name_Components-HasDataIndicator',
        SPLzSharePartic.ZNAMECOMPONENTS AS 'SPLzSharePartic-Name_Components',
        CASE
            WHEN SPLzShare.ZPREVIEWDATA > 0 THEN 'SPLzShare-Preview_Data_has_BLOB'
            ELSE 'SPLzShare-Preview_Data_Empty-NULL'
        END AS 'SPLzShare-Preview_Data-DataIndicator',
        SPLzShare.ZPREVIEWDATA AS 'SPLzShare-Preview_Data',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash-iOS18',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash-iOS18'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
            LEFT JOIN ZSHARE zShare ON zShare.Z_PK = zAsset.ZMOMENTSHARE
            LEFT JOIN ZASSETCONTRIBUTOR zAssetContrib ON zAssetContrib.Z3LIBRARYSCOPEASSETCONTRIBUTORS = zAsset.Z_PK
            LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
            LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.Z_PK = zAssetContrib.ZPARTICIPANT
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                aaashiftedlocation_postal_address = ''
                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                aaareverselocation_postal_address = ''
                # AAAzCldMastMedData.ZDATA-PLIST
                aaazcldmastmeddata_plist_tiff = ''
                aaazcldmastmeddata_plist_exif = ''
                aaazcldmastmeddata_plist_gps = ''
                aaazcldmastmeddata_plist_iptc = ''
                # CMzCldMastMedData.ZDATA-PLIST
                cmzcldmastmeddata_plist_tiff = ''
                cmzcldmastmeddata_plist_exif = ''
                cmzcldmastmeddata_plist_gps = ''
                cmzcldmastmeddata_plist_iptc = ''
                # zSharePartic_ZNAMECOMPONENTS_PLIST
                zsharepartic_namecomponents = ''
                # SPLzSharePartic_ZNAMECOMPONENTS_PLIST
                splzsharepartic_namecomponents = ''
                # zShare.ZPREVIEWDATA-BLOB_JPG
                zshare_previewdata_blob = ''
                # SPLzShare.ZPREVIEWDATA-BLOB_JPG
                splzshare_previewdata_blob = ''

                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                if row[9] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[9])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaashiftedlocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename' + row[2])

                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                if row[12] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[12])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaareverselocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename ' + row[2])

                # AAAzCldMastMedData.ZDATA-PLIST
                if row[18] is not None:
                    pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[18])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                aaazcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                aaazcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                aaazcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                aaazcldmastmeddata_plist_iptc = val

                # CMzCldMastMedData.ZDATA-PLIST
                if row[24] is not None:
                    pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[24])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                cmzcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                cmzcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                cmzcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                cmzcldmastmeddata_plist_iptc = val

                # zSharePartic_ZNAMECOMPONENTS_PLIST
                if row[31] is not None:
                    pathto = os.path.join(report_folder, 'zSP_Name_Components_' + row[2] + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[31])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            zsharepartic_namecomponents = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from zAsset-Filename' + row[2])

                # SPLzSharePartic_ZNAMECOMPONENTS_PLIST
                if row[42] is not None:
                    pathto = os.path.join(report_folder, 'SPLzSharePartic-Name_Components_' + row[2] + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[42])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            splzsharepartic_namecomponents = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from zAsset-Filename' + row[2])

                # zShare.ZPREVIEWDATA-BLOB_JPG
                if row[35] is not None:
                    pathto = os.path.join(report_folder, 'zShare_PreviewData_' + row[2] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[35])
                    zshare_previewdata_blob = media_to_html(pathto, files_found, report_folder)

                # SPLzShare.ZPREVIEWDATA-BLOB_JPG
                if row[44] is not None:
                    pathto = os.path.join(report_folder, 'SPLzShare_PreviewData_' + row[2] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[44])
                    splzshare_previewdata_blob = media_to_html(pathto, files_found, report_folder)

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8],
                                  aaashiftedlocation_postal_address,
                                  row[10], row[11],
                                  aaareverselocation_postal_address,
                                  row[13], row[14], row[15], row[16], row[17],
                                  aaazcldmastmeddata_plist_tiff,
                                  aaazcldmastmeddata_plist_exif,
                                  aaazcldmastmeddata_plist_gps,
                                  aaazcldmastmeddata_plist_iptc,
                                  row[19], row[20], row[21], row[22], row[23],
                                  cmzcldmastmeddata_plist_tiff,
                                  cmzcldmastmeddata_plist_exif,
                                  cmzcldmastmeddata_plist_gps,
                                  cmzcldmastmeddata_plist_iptc,
                                  row[25], row[26], row[27], row[28], row[29], row[30],
                                  zsharepartic_namecomponents,
                                  row[32], row[33], row[34],
                                  zshare_previewdata_blob,
                                  row[36], row[37],
                                  row[38], row[39], row[40], row[41],
                                  splzsharepartic_namecomponents,
                                  row[43],
                                  splzshare_previewdata_blob,
                                  row[45], row[46], row[47], row[48], row[49]))

                counter += 1

            description = 'Parses basic asset record data from Photos.sqlite for assets that have embedded files' \
                          ' records for a variety of data. This parser should be used in conjunction with other' \
                          ' parsers to review a complete record for analysis. The results of this parser could' \
                          ' produce multiple records for a single asset.'
            report = ArtifactHtmlReport('Ph10.1-Assets have embedded files-PhDaPsql')
            report.start_artifact_report(report_folder, 'Ph10.1-Assets have embedded files-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Directory-Path-1',
                            'zAsset-Filename-2',
                            'zAddAssetAttr- Original Filename-3',
                            'zCldMast- Original Filename-4',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-5',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-6',
                            'zAddAssetAttr-Shifted Location Valid-7',
                            'zAddAssetAttr-Shifted Location Data-HasDataIndicator-8',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address-9',
                            'zAddAssetAttr-Reverse Location Is Valid-10',
                            'zAddAssetAttr-Reverse Location Data-HasDataIndicator-11',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address-12',
                            'AAAzCldMastMedData-zOPT-13',
                            'zAddAssetAttr-Media Metadata Type-14',
                            'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-15',
                            'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-16',
                            'AAAzCldMastMedData-Data-HasDataIndicator-17',
                            'AAAzCldMastMedData-Data_plist_TIFF-18',
                            'AAAzCldMastMedData-Data_plist_Exif-18',
                            'AAAzCldMastMedData-Data_plist_GPS-18',
                            'AAAzCldMastMedData-Data_plist_IPTC-18',
                            'CldMasterzCldMastMedData-zOPT-19',
                            'zCldMast-Media Metadata Type-20',
                            'zCldMast-Media Metadata Key= zCldMastMedData.zPK-21',
                            'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-22',
                            'CMzCldMastMedData-Data-HasDataIndicator-23',
                            'CMzCldMastMedData-Data_plist_TIFF-24',
                            'CMzCldMastMedData-Data_plist_Exif-24',
                            'CMzCldMastMedData-Data_plist_GPS-24',
                            'CMzCldMastMedData-Data_plist_IPTC-24',
                            'zSharePartic-Acceptance Status-25',
                            'zSharePartic-User ID-26',
                            'zSharePartic-zPK-27',
                            'zSharePartic-Email Address-28',
                            'zSharePartic-Phone Number-29',
                            'zSharePartic-Name_Components-HasDataIndicator-30',
                            'zSharePartic-Name_Components_Plist-31',
                            'zSharePartic-Is Current User-32',
                            'zSharePartic-Role-33',
                            'zShare-Preview_Data-DataIndicator-34',
                            'zShare-Preview_Data-BLOB_JPG-35',
                            'SPLzSharePartic-Is Current User-36',
                            'SPLzSharePartic-Role-37',
                            'zAsstContrib-Participant= zSharePartic-zPK-38',
                            'SPLzSharePartic-Email Address-39',
                            'SPLzSharePartic-Phone Number-40',
                            'SPLzSharePartic-Name_Components-HasDataIndicator-41',
                            'SPLzSharePartic-Name_Components_Plist-42',
                            'zShare-Preview_Data-DataIndicator-43',
                            'zShare-Preview_Data-BLOB_JPG-44',
                            'zAsset-zPK-45',
                            'zAddAssetAttr-zPK-46',
                            'zAsset-UUID = store.cloudphotodb-47',
                            'zAddAssetAttr-Original Stable Hash-iOS18-48',
                            'zAddAssetAttr.Adjusted Stable Hash-iOS18-49')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph10.1-Assets have embedded files-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph10.1-Assets have embedded files-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite assets having embedded files')

        db.close()
        return


def get_ph10assetparsedembeddedfilessyndpl(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("10.3.4"):
        logfunc("Unsupported ios version for Syndication.photoslibrary-database-Photos.sqlite assets have embedded files from iOS " + iosversion)
    if (version.parse(iosversion) >= version.parse("11")) & (version.parse(iosversion) < version.parse("13")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data-HasDataIndicator',
        zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data-HasDataIndicator',
        zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',      
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZGENERICASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                aaashiftedlocation_geoplaceresult = ''
                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                aaareverselocation_geoplaceresult = ''

                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                if row[8] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[8])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)
                        for key, val in plist.items():
                            if key == "geoPlaceResult":
                                aaashiftedlocation_geoplaceresult = val

                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                if row[11] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[11])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)
                        for key, val in plist.items():
                            if key == "geoPlaceResult":
                                aaareverselocation_geoplaceresult = val

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                  aaashiftedlocation_geoplaceresult,
                                  row[9], row[10],
                                  aaareverselocation_geoplaceresult,
                                  row[12], row[13], row[14], row[15]))

                counter += 1

            description = 'Parses basic asset record data from Syndication.photoslibrary-Photos.sqlite' \
                          ' for assets that have embedded files records for a variety of data. This parser' \
                          ' should be used in conjunction with other parsers to review a complete record' \
                          ' for analysis. The results of this parser could produce multiple records for a single asset.'
            report = ArtifactHtmlReport('Ph10.2-Assets have embedded files-SyndPL')
            report.start_artifact_report(report_folder, 'Ph10.2-Assets have embedded files-SyndPL', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Directory-Path-1',
                            'zAsset-Filename-2',
                            'zAddAssetAttr- Original Filename-3',
                            'zCldMast- Original Filename-4',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-5',
                            'zAddAssetAttr-Shifted Location Valid-6',
                            'zAddAssetAttr-Shifted Location Data-HasDataIndicator-7',
                            'zAddAssetAttr-Shifted Location Data-geoPlaceResult-8',
                            'zAddAssetAttr-Reverse Location Is Valid-9',
                            'zAddAssetAttr-Reverse Location Data-HasDataIndicator-10',
                            'zAddAssetAttr-Reverse Location Data-geoPlaceResult-11',
                            'zAsset-zPK-12',
                            'zAddAssetAttr-zPK-13',
                            'zAsset-UUID = store.cloudphotodb-14',
                            'zAddAssetAttr-Master Fingerprint-15')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph10.2-Assets have embedded files-SyndPL'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph10.2-Assets have embedded files-SyndPL'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for Syndication.photoslibrary-Photos.sqlite assets having embedded files')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("13")) & (version.parse(iosversion) < version.parse("14")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',        
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data-HasDataIndicator',
        zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data-HasDataIndicator',
        zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',		
        zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
        AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
        AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
        zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
        CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data-HasDataIndicator',		
        CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZGENERICASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                aaashiftedlocation_postal_address = ''
                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                aaareverselocation_postal_address = ''
                # AAAzCldMastMedData.ZDATA-PLIST
                aaazcldmastmeddata_plist_tiff = ''
                aaazcldmastmeddata_plist_exif = ''
                aaazcldmastmeddata_plist_gps = ''
                aaazcldmastmeddata_plist_iptc = ''
                # CMzCldMastMedData.ZDATA-PLIST
                cmzcldmastmeddata_plist_tiff = ''
                cmzcldmastmeddata_plist_exif = ''
                cmzcldmastmeddata_plist_gps = ''
                cmzcldmastmeddata_plist_iptc = ''

                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                if row[8] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[8])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaashiftedlocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename' + row[2])

                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                if row[11] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[11])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaareverselocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename' + row[2])

                # AAAzCldMastMedData.ZDATA-PLIST
                if row[17] is not None:
                    pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[17])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                aaazcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                aaazcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                aaazcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                aaazcldmastmeddata_plist_iptc = val

                # CMzCldMastMedData.ZDATA-PLIST
                if row[23] is not None:
                    pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[23])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                cmzcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                cmzcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                cmzcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                cmzcldmastmeddata_plist_iptc = val

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                aaashiftedlocation_postal_address,
                                row[9], row[10],
                                aaareverselocation_postal_address,
                                row[12], row[13], row[14], row[15], row[16],
                                aaazcldmastmeddata_plist_tiff,
                                aaazcldmastmeddata_plist_exif,
                                aaazcldmastmeddata_plist_gps,
                                aaazcldmastmeddata_plist_iptc,
                                row[18], row[19], row[20], row[21], row[22],
                                cmzcldmastmeddata_plist_tiff,
                                cmzcldmastmeddata_plist_exif,
                                cmzcldmastmeddata_plist_gps,
                                cmzcldmastmeddata_plist_iptc,
                                row[24], row[25], row[26], row[27]))

                counter += 1

            description = 'Parses basic asset record data from Syndication.photoslibrary-Photos.sqlite' \
                          ' for assets that have embedded files records for a variety of data. This parser' \
                          ' should be used in conjunction with other parsers to review a complete record' \
                          ' for analysis. The results of this parser could produce multiple records for a single asset.'
            report = ArtifactHtmlReport('Ph10.2-Assets have embedded files-SyndPL')
            report.start_artifact_report(report_folder, 'Ph10.2-Assets have embedded files-SyndPL', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Directory-Path-1',
                            'zAsset-Filename-2',
                            'zAddAssetAttr- Original Filename-3',
                            'zCldMast- Original Filename-4',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-5',
                            'zAddAssetAttr-Shifted Location Valid-6',
                            'zAddAssetAttr-Shifted Location Data-HasDataIndicator-7',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address-8',
                            'zAddAssetAttr-Reverse Location Is Valid-9',
                            'zAddAssetAttr-Reverse Location Data-HasDataIndicator-10',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address-11',
                            'AAAzCldMastMedData-zOPT-12',
                            'zAddAssetAttr-Media Metadata Type-13',
                            'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-14',
                            'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast- MediaMetaData-15',
                            'AAAzCldMastMedData-Data-HasDataIndicator-16',
                            'AAAzCldMastMedData-Data_plist_TIFF-17',
                            'AAAzCldMastMedData-Data_plist_Exif-17',
                            'AAAzCldMastMedData-Data_plist_GPS-17',
                            'AAAzCldMastMedData-Data_plist_IPTC-17',
                            'CldMasterzCldMastMedData-zOPT-18',
                            'zCldMast-Media Metadata Type-19',
                            'zCldMast-Media Metadata Key= zCldMastMedData-zPK-20',
                            'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast- MediaMetaData Key-21',
                            'CMzCldMastMedData-Data-HasDataIndicator-22',
                            'CMzCldMastMedData-Data_plist_TIFF-23',
                            'CMzCldMastMedData-Data_plist_Exif-23',
                            'CMzCldMastMedData-Data_plist_GPS-23',
                            'CMzCldMastMedData-Data_plist_IPTC-23',
                            'zAsset-zPK-24',
                            'zAddAssetAttr-zPK-25',
                            'zAsset-UUID = store.cloudphotodb-26',
                            'zAddAssetAttr-Master Fingerprint-27')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph10.2-Assets have embedded files-SyndPL'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph10.2-Assets have embedded files-SyndPL'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for Syndication.photoslibrary-Photos.sqlite assets having embedded files')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("15")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT 
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data-HasDataIndicator',
        zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data-HasDataIndicator',
        zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',		
        zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
        AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
        AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
        zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
        CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data-HasDataIndicator',		
        CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',
        CASE zSharePartic.ZACCEPTANCESTATUS
            WHEN 1 THEN '1-Invite-Pending_or_Declined-1'
            WHEN 2 THEN '2-Invite-Accepted-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZACCEPTANCESTATUS || ''
        END AS 'zSharePartic-Acceptance Status',
        zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
        zSharePartic.Z_PK AS 'zSharePartic-zPK',
        zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
        zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',
        CASE
            WHEN zSharePartic.ZNAMECOMPONENTS > 0 THEN 'zSharePartic-Name_Components_has_Plist'
            ELSE 'zSharePartic-Name_Components_Empty-NULL'
        END AS 'zSharePartic-Name_Components-HasDataIndicator',
        zSharePartic.ZNAMECOMPONENTS AS 'zSharePartic-Name_Components',        
        CASE zSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_CurrentUser-0'
            WHEN 1 THEN '1-Participant-Is_CurrentUser-1'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZISCURRENTUSER || ''
        END AS 'zSharePartic-Is Current User',
        CASE zSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZROLE || ''
        END AS 'zSharePartic-Role',
        CASE
            WHEN zShare.ZPREVIEWDATA > 0 THEN 'zShare-Preview_Data_has_BLOB'
            ELSE 'zShare-Preview_Data_Empty-NULL'
        END AS 'zShare-Preview_Data-DataIndicator',
        zShare.ZPREVIEWDATA AS 'zShare-Preview_Data',
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
            LEFT JOIN ZSHARE zShare ON zShare.Z_PK = zAsset.ZMOMENTSHARE
            LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                aaashiftedlocation_postal_address = ''
                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                aaareverselocation_postal_address = ''
                # AAAzCldMastMedData.ZDATA-PLIST
                aaazcldmastmeddata_plist_tiff = ''
                aaazcldmastmeddata_plist_exif = ''
                aaazcldmastmeddata_plist_gps = ''
                aaazcldmastmeddata_plist_iptc = ''
                # CMzCldMastMedData.ZDATA-PLIST
                cmzcldmastmeddata_plist_tiff = ''
                cmzcldmastmeddata_plist_exif = ''
                cmzcldmastmeddata_plist_gps = ''
                cmzcldmastmeddata_plist_iptc = ''
                # zSharePartic_ZNAMECOMPONENTS_PLIST
                zsharepartic_namecomponents = ''
                # zShare.ZPREVIEWDATA-BLOB_JPG
                zshare_previewdata_blob = ''

                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                if row[8] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[8])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaashiftedlocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename' + row[2])

                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                if row[11] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[11])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaareverselocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename ' + row[2])

                # AAAzCldMastMedData.ZDATA-PLIST
                if row[17] is not None:
                    pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[17])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                aaazcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                aaazcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                aaazcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                aaazcldmastmeddata_plist_iptc = val

                # CMzCldMastMedData.ZDATA-PLIST
                if row[23] is not None:
                    pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[23])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                cmzcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                cmzcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                cmzcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                cmzcldmastmeddata_plist_iptc = val

                # zSharePartic_ZNAMECOMPONENTS_PLIST
                if row[30] is not None:
                    pathto = os.path.join(report_folder, 'zSP_Name_Components_' + row[2] + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[30])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            zsharepartic_namecomponents = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from Asset PK ' + row[2])

                # zShare.ZPREVIEWDATA-BLOB_JPG
                if row[34] is not None:
                    pathto = os.path.join(report_folder, 'zShare_PreviewData_' + row[2] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[34])
                    zshare_previewdata_blob = media_to_html(pathto, files_found, report_folder)

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                  aaashiftedlocation_postal_address,
                                  row[9], row[10],
                                  aaareverselocation_postal_address,
                                  row[12], row[13], row[14], row[15], row[16],
                                  aaazcldmastmeddata_plist_tiff,
                                  aaazcldmastmeddata_plist_exif,
                                  aaazcldmastmeddata_plist_gps,
                                  aaazcldmastmeddata_plist_iptc,
                                  row[18], row[19], row[20], row[21], row[22],
                                  cmzcldmastmeddata_plist_tiff,
                                  cmzcldmastmeddata_plist_exif,
                                  cmzcldmastmeddata_plist_gps,
                                  cmzcldmastmeddata_plist_iptc,
                                  row[24], row[25], row[26], row[27], row[28], row[29],
                                  zsharepartic_namecomponents,
                                  row[31], row[32], row[33],
                                  zshare_previewdata_blob,
                                  row[35], row[36], row[37], row[38]))

                counter += 1

            description = 'Parses basic asset record data from Syndication.photoslibrary-Photos.sqlite' \
                          ' for assets that have embedded files records for a variety of data. This parser' \
                          ' should be used in conjunction with other parsers to review a complete record' \
                          ' for analysis. The results of this parser could produce multiple records for a single asset.'
            report = ArtifactHtmlReport('Ph10.2-Assets have embedded files-SyndPL')
            report.start_artifact_report(report_folder, 'Ph10.2-Assets have embedded files-SyndPL', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Directory-Path-1',
                            'zAsset-Filename-2',
                            'zAddAssetAttr- Original Filename-3',
                            'zCldMast- Original Filename-4',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-5',
                            'zAddAssetAttr-Shifted Location Valid-6',
                            'zAddAssetAttr-Shifted Location Data-HasDataIndicator-7',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address-8',
                            'zAddAssetAttr-Reverse Location Is Valid-9',
                            'zAddAssetAttr-Reverse Location Data-HasDataIndicator-10',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address-11',
                            'AAAzCldMastMedData-zOPT-12',
                            'zAddAssetAttr-Media Metadata Type-13',
                            'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-14',
                            'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-15',
                            'AAAzCldMastMedData-Data-HasDataIndicator-16',
                            'AAAzCldMastMedData-Data_plist_TIFF-17',
                            'AAAzCldMastMedData-Data_plist_Exif-17',
                            'AAAzCldMastMedData-Data_plist_GPS-17',
                            'AAAzCldMastMedData-Data_plist_IPTC-17',
                            'CldMasterzCldMastMedData-zOPT-18',
                            'zCldMast-Media Metadata Type-19',
                            'zCldMast-Media Metadata Key= zCldMastMedData.zPK-20',
                            'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-21',
                            'CMzCldMastMedData-Data-HasDataIndicator-22',
                            'CMzCldMastMedData-Data_plist_TIFF-23',
                            'CMzCldMastMedData-Data_plist_Exif-23',
                            'CMzCldMastMedData-Data_plist_GPS-23',
                            'CMzCldMastMedData-Data_plist_IPTC-23',
                            'zSharePartic-Acceptance Status-24',
                            'zSharePartic-User ID-25',
                            'zSharePartic-zPK-26',
                            'zSharePartic-Email Address-27',
                            'zSharePartic-Phone Number-28',
                            'zSharePartic-Name_Components-HasDataIndicator-29',
                            'zSharePartic-Name_Components_Plist-30',
                            'zSharePartic-Is Current User-31',
                            'zSharePartic-Role-32',
                            'zShare-Preview_Data-DataIndicator-33',
                            'zShare-Preview_Data-BLOB_JPG-34',
                            'zAsset-zPK-35',
                            'zAddAssetAttr-zPK-36',
                            'zAsset-UUID = store.cloudphotodb-37',
                            'zAddAssetAttr-Master Fingerprint-38')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph10.2-Assets have embedded files-SyndPL'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph10.2-Assets have embedded files-SyndPL'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for Syndication.photoslibrary-Photos.sqlite assets having embedded files')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data-HasDataIndicator',
        zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data-HasDataIndicator',
        zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',		
        zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
        AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
        AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
        zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
        CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data-HasDataIndicator',
        CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',
        CASE zSharePartic.ZACCEPTANCESTATUS
            WHEN 1 THEN '1-Invite-Pending_or_Declined-1'
            WHEN 2 THEN '2-Invite-Accepted-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZACCEPTANCESTATUS || ''
        END AS 'zSharePartic-Acceptance Status',
        zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
        zSharePartic.Z_PK AS 'zSharePartic-zPK',
        zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
        zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',
        CASE
            WHEN zSharePartic.ZNAMECOMPONENTS > 0 THEN 'zSharePartic-Name_Components_has_Plist'
            ELSE 'zSharePartic-Name_Components_Empty-NULL'
        END AS 'zSharePartic-Name_Components-HasDataIndicator',
        zSharePartic.ZNAMECOMPONENTS AS 'zSharePartic-Name_Components',        
        CASE zSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_CurrentUser-0'
            WHEN 1 THEN '1-Participant-Is_CurrentUser-1'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZISCURRENTUSER || ''
        END AS 'zSharePartic-Is Current User',
        CASE zSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZROLE || ''
        END AS 'zSharePartic-Role',
        CASE
            WHEN zShare.ZPREVIEWDATA > 0 THEN 'zShare-Preview_Data_has_BLOB'
            ELSE 'zShare-Preview_Data_Empty-NULL'
        END AS 'zShare-Preview_Data-DataIndicator',
        zShare.ZPREVIEWDATA AS 'zShare-Preview_Data',        
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
            LEFT JOIN ZSHARE zShare ON zShare.Z_PK = zAsset.ZMOMENTSHARE
            LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                aaashiftedlocation_postal_address = ''
                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                aaareverselocation_postal_address = ''
                # AAAzCldMastMedData.ZDATA-PLIST
                aaazcldmastmeddata_plist_tiff = ''
                aaazcldmastmeddata_plist_exif = ''
                aaazcldmastmeddata_plist_gps = ''
                aaazcldmastmeddata_plist_iptc = ''
                # CMzCldMastMedData.ZDATA-PLIST
                cmzcldmastmeddata_plist_tiff = ''
                cmzcldmastmeddata_plist_exif = ''
                cmzcldmastmeddata_plist_gps = ''
                cmzcldmastmeddata_plist_iptc = ''
                # zSharePartic_ZNAMECOMPONENTS_PLIST
                zsharepartic_namecomponents = ''
                # zShare.ZPREVIEWDATA-BLOB_JPG
                zshare_previewdata_blob = ''

                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                if row[9] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[9])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaashiftedlocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename' + row[2])

                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                if row[12] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[12])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaareverselocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename' + row[2])

                # AAAzCldMastMedData.ZDATA-PLIST
                if row[18] is not None:
                    pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[18])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                aaazcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                aaazcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                aaazcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                aaazcldmastmeddata_plist_iptc = val

                # CMzCldMastMedData.ZDATA-PLIST
                if row[24] is not None:
                    pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[24])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                cmzcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                cmzcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                cmzcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                cmzcldmastmeddata_plist_iptc = val

                # zSharePartic_ZNAMECOMPONENTS_PLIST
                if row[31] is not None:
                    pathto = os.path.join(report_folder, 'zSP_Name_Components_' + row[2] + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[31])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            zsharepartic_namecomponents = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from zAsset-Filename ' + row[2])

                # zShare.ZPREVIEWDATA-BLOB_JPG
                if row[35] is not None:
                    pathto = os.path.join(report_folder, 'zShare_PreviewData_' + row[2] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[35])
                    zshare_previewdata_blob = media_to_html(pathto, files_found, report_folder)

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8],
                                  aaashiftedlocation_postal_address,
                                  row[10], row[11],
                                  aaareverselocation_postal_address,
                                  row[13], row[14], row[15], row[16], row[17],
                                  aaazcldmastmeddata_plist_tiff,
                                  aaazcldmastmeddata_plist_exif,
                                  aaazcldmastmeddata_plist_gps,
                                  aaazcldmastmeddata_plist_iptc,
                                  row[19], row[20], row[21], row[22], row[23],
                                  cmzcldmastmeddata_plist_tiff,
                                  cmzcldmastmeddata_plist_exif,
                                  cmzcldmastmeddata_plist_gps,
                                  cmzcldmastmeddata_plist_iptc,
                                  row[25], row[26], row[27], row[28], row[29], row[30],
                                  zsharepartic_namecomponents,
                                  row[32], row[33], row[34],
                                  zshare_previewdata_blob,
                                  row[36], row[37], row[38], row[39]))

                counter += 1

            description = 'Parses basic asset record data from Syndication.photoslibrary-Photos.sqlite' \
                          ' for assets that have embedded files records for a variety of data. This parser' \
                          ' should be used in conjunction with other parsers to review a complete record' \
                          ' for analysis. The results of this parser could produce multiple records for a single asset.'
            report = ArtifactHtmlReport('Ph10.2-Assets have embedded files-SyndPL')
            report.start_artifact_report(report_folder, 'Ph10.2-Assets have embedded files-SyndPL', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Directory-Path-1',
                            'zAsset-Filename-2',
                            'zAddAssetAttr- Original Filename-3',
                            'zCldMast- Original Filename-4',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-5',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-6',
                            'zAddAssetAttr-Shifted Location Valid-7',
                            'zAddAssetAttr-Shifted Location Data-HasDataIndicator-8',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address-9',
                            'zAddAssetAttr-Reverse Location Is Valid-10',
                            'zAddAssetAttr-Reverse Location Data-HasDataIndicator-11',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address-12',
                            'AAAzCldMastMedData-zOPT-13',
                            'zAddAssetAttr-Media Metadata Type-14',
                            'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-15',
                            'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-16',
                            'AAAzCldMastMedData-Data-HasDataIndicator-17',
                            'AAAzCldMastMedData-Data_plist_TIFF-18',
                            'AAAzCldMastMedData-Data_plist_Exif-18',
                            'AAAzCldMastMedData-Data_plist_GPS-18',
                            'AAAzCldMastMedData-Data_plist_IPTC-18',
                            'CldMasterzCldMastMedData-zOPT-19',
                            'zCldMast-Media Metadata Type-20',
                            'zCldMast-Media Metadata Key= zCldMastMedData.zPK-21',
                            'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-22',
                            'CMzCldMastMedData-Data-HasDataIndicator-23',
                            'CMzCldMastMedData-Data_plist_TIFF-24',
                            'CMzCldMastMedData-Data_plist_Exif-24',
                            'CMzCldMastMedData-Data_plist_GPS-24',
                            'CMzCldMastMedData-Data_plist_IPTC-24',
                            'zSharePartic-Acceptance Status-25',
                            'zSharePartic-User ID-26',
                            'zSharePartic-zPK-27',
                            'zSharePartic-Email Address-28',
                            'zSharePartic-Phone Number-29',
                            'zSharePartic-Name_Components-HasDataIndicator-30',
                            'zSharePartic-Name_Components_Plist-31',
                            'zSharePartic-Is Current User-32',
                            'zSharePartic-Role-33',
                            'zShare-Preview_Data-DataIndicator-34',
                            'zShare-Preview_Data-BLOB_JPG-35',
                            'zAsset-zPK-36',
                            'zAddAssetAttr-zPK-37',
                            'zAsset-UUID = store.cloudphotodb-38',
                            'zAddAssetAttr-Master Fingerprint-39')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph10.2-Assets have embedded files-SyndPL'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph10.2-Assets have embedded files-SyndPL'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for Syndication.photoslibrary-Photos.sqlite assets having embedded files')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("17")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data-HasDataIndicator',
        zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data-HasDataIndicator',
        zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',		
        zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
        AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
        AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
        zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
        CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data-HasDataIndicator',
        CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',
        CASE zSharePartic.ZACCEPTANCESTATUS
            WHEN 1 THEN '1-Invite-Pending_or_Declined-1'
            WHEN 2 THEN '2-Invite-Accepted-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZACCEPTANCESTATUS || ''
        END AS 'zSharePartic-Acceptance Status',
        zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
        zSharePartic.Z_PK AS 'zSharePartic-zPK',
        zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
        zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',
        CASE
            WHEN zSharePartic.ZNAMECOMPONENTS > 0 THEN 'zSharePartic-Name_Components_has_Plist'
            ELSE 'zSharePartic-Name_Components_Empty-NULL'
        END AS 'zSharePartic-Name_Components-HasDataIndicator',
        zSharePartic.ZNAMECOMPONENTS AS 'zSharePartic-Name_Components',        
        CASE zSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_CurrentUser-0'
            WHEN 1 THEN '1-Participant-Is_CurrentUser-1'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZISCURRENTUSER || ''
        END AS 'zSharePartic-Is Current User',
        CASE zSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZROLE || ''
        END AS 'zSharePartic-Role',
        CASE
            WHEN zShare.ZPREVIEWDATA > 0 THEN 'zShare-Preview_Data_has_BLOB'
            ELSE 'zShare-Preview_Data_Empty-NULL'
        END AS 'zShare-Preview_Data-DataIndicator',
        zShare.ZPREVIEWDATA AS 'zShare-Preview_Data',
        CASE SPLzSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_CurrentUser-0'
            WHEN 1 THEN '1-Participant-Is_CurrentUser-1'
            ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZISCURRENTUSER || ''
        END AS 'SPLzSharePartic-Is Current User',
        CASE SPLzSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZROLE || ''
        END AS 'SPLzSharePartic-Role',
        zAssetContrib.ZPARTICIPANT AS 'zAsstContrib-Participant= zSharePartic-zPK',
        SPLzSharePartic.ZEMAILADDRESS AS 'SPLzSharePartic-Email Address',
        SPLzSharePartic.ZPHONENUMBER AS 'SPLzSharePartic-Phone Number',
        CASE
            WHEN SPLzSharePartic.ZNAMECOMPONENTS > 0 THEN 'SPLzSharePartic-Name_Components_has_Plist'
            ELSE 'SPLzSharePartic-Name_Components_Empty-NULL'
        END AS 'SPLzSharePartic-Name_Components-HasDataIndicator',
        SPLzSharePartic.ZNAMECOMPONENTS AS 'SPLzSharePartic-Name_Components',
        CASE
            WHEN SPLzShare.ZPREVIEWDATA > 0 THEN 'SPLzShare-Preview_Data_has_BLOB'
            ELSE 'SPLzShare-Preview_Data_Empty-NULL'
        END AS 'SPLzShare-Preview_Data-DataIndicator',
        SPLzShare.ZPREVIEWDATA AS 'SPLzShare-Preview_Data',
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
            LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
            LEFT JOIN ZSHARE zShare ON zShare.Z_PK = zAsset.ZMOMENTSHARE
            LEFT JOIN ZASSETCONTRIBUTOR zAssetContrib ON zAssetContrib.Z3LIBRARYSCOPEASSETCONTRIBUTORS = zAsset.Z_PK
            LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
            LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.Z_PK = zAssetContrib.ZPARTICIPANT
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                aaashiftedlocation_postal_address = ''
                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                aaareverselocation_postal_address = ''
                # AAAzCldMastMedData.ZDATA-PLIST
                aaazcldmastmeddata_plist_tiff = ''
                aaazcldmastmeddata_plist_exif = ''
                aaazcldmastmeddata_plist_gps = ''
                aaazcldmastmeddata_plist_iptc = ''
                # CMzCldMastMedData.ZDATA-PLIST
                cmzcldmastmeddata_plist_tiff = ''
                cmzcldmastmeddata_plist_exif = ''
                cmzcldmastmeddata_plist_gps = ''
                cmzcldmastmeddata_plist_iptc = ''
                # zSharePartic_ZNAMECOMPONENTS_PLIST
                zsharepartic_namecomponents = ''
                # SPLzSharePartic_ZNAMECOMPONENTS_PLIST
                splzsharepartic_namecomponents = ''
                # zShare.ZPREVIEWDATA-BLOB_JPG
                zshare_previewdata_blob = ''
                # SPLzShare.ZPREVIEWDATA-BLOB_JPG
                splzshare_previewdata_blob = ''

                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                if row[9] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[9])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaashiftedlocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename ' + row[2])

                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                if row[12] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[12])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaareverselocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename ' + row[2])

                # AAAzCldMastMedData.ZDATA-PLIST
                if row[18] is not None:
                    pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[18])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                aaazcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                aaazcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                aaazcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                aaazcldmastmeddata_plist_iptc = val

                # CMzCldMastMedData.ZDATA-PLIST
                if row[24] is not None:
                    pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[24])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                cmzcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                cmzcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                cmzcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                cmzcldmastmeddata_plist_iptc = val

                # zSharePartic_ZNAMECOMPONENTS_PLIST
                if row[31] is not None:
                    pathto = os.path.join(report_folder, 'zSP_Name_Components_' + row[2] + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[31])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            zsharepartic_namecomponents = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from zAsset-Filename' + row[2])

                # SPLzSharePartic_ZNAMECOMPONENTS_PLIST
                if row[42] is not None:
                    pathto = os.path.join(report_folder, 'SPLzSharePartic-Name_Components_' + row[2] + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[42])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            splzsharepartic_namecomponents = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from zAsset-Filename ' + row[2])

                # zShare.ZPREVIEWDATA-BLOB_JPG
                if row[35] is not None:
                    pathto = os.path.join(report_folder, 'zShare_PreviewData_' + row[2] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[35])
                    zshare_previewdata_blob = media_to_html(pathto, files_found, report_folder)

                # SPLzShare.ZPREVIEWDATA-BLOB_JPG
                if row[44] is not None:
                    pathto = os.path.join(report_folder, 'SPLzShare_PreviewData_' + row[2] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[44])
                    splzshare_previewdata_blob = media_to_html(pathto, files_found, report_folder)

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8],
                                  aaashiftedlocation_postal_address,
                                  row[10], row[11],
                                  aaareverselocation_postal_address,
                                  row[13], row[14], row[15], row[16], row[17],
                                  aaazcldmastmeddata_plist_tiff,
                                  aaazcldmastmeddata_plist_exif,
                                  aaazcldmastmeddata_plist_gps,
                                  aaazcldmastmeddata_plist_iptc,
                                  row[19], row[20], row[21], row[22], row[23],
                                  cmzcldmastmeddata_plist_tiff,
                                  cmzcldmastmeddata_plist_exif,
                                  cmzcldmastmeddata_plist_gps,
                                  cmzcldmastmeddata_plist_iptc,
                                  row[25], row[26], row[27], row[28], row[29], row[30],
                                  zsharepartic_namecomponents,
                                  row[32], row[33], row[34],
                                  zshare_previewdata_blob,
                                  row[36], row[37],
                                  row[38], row[39], row[40], row[41],
                                  splzsharepartic_namecomponents,
                                  row[43],
                                  splzshare_previewdata_blob,
                                  row[45], row[46], row[47], row[48]))

                counter += 1

            description = 'Parses basic asset record data from Syndication.photoslibrary-Photos.sqlite' \
                          ' for assets that have embedded files records for a variety of data. This parser' \
                          ' should be used in conjunction with other parsers to review a complete record' \
                          ' for analysis. The results of this parser could produce multiple records for a single asset.'
            report = ArtifactHtmlReport('Ph10.2-Assets have embedded files-SyndPL')
            report.start_artifact_report(report_folder, 'Ph10.2-Assets have embedded files-SyndPL', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Directory-Path-1',
                            'zAsset-Filename-2',
                            'zAddAssetAttr- Original Filename-3',
                            'zCldMast- Original Filename-4',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-5',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-6',
                            'zAddAssetAttr-Shifted Location Valid-7',
                            'zAddAssetAttr-Shifted Location Data-HasDataIndicator-8',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address-9',
                            'zAddAssetAttr-Reverse Location Is Valid-10',
                            'zAddAssetAttr-Reverse Location Data-HasDataIndicator-11',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address-12',
                            'AAAzCldMastMedData-zOPT-13',
                            'zAddAssetAttr-Media Metadata Type-14',
                            'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-15',
                            'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-16',
                            'AAAzCldMastMedData-Data-HasDataIndicator-17',
                            'AAAzCldMastMedData-Data_plist_TIFF-18',
                            'AAAzCldMastMedData-Data_plist_Exif-18',
                            'AAAzCldMastMedData-Data_plist_GPS-18',
                            'AAAzCldMastMedData-Data_plist_IPTC-18',
                            'CldMasterzCldMastMedData-zOPT-19',
                            'zCldMast-Media Metadata Type-20',
                            'zCldMast-Media Metadata Key= zCldMastMedData.zPK-21',
                            'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-22',
                            'CMzCldMastMedData-Data-HasDataIndicator-23',
                            'CMzCldMastMedData-Data_plist_TIFF-24',
                            'CMzCldMastMedData-Data_plist_Exif-24',
                            'CMzCldMastMedData-Data_plist_GPS-24',
                            'CMzCldMastMedData-Data_plist_IPTC-24',
                            'zSharePartic-Acceptance Status-25',
                            'zSharePartic-User ID-26',
                            'zSharePartic-zPK-27',
                            'zSharePartic-Email Address-28',
                            'zSharePartic-Phone Number-29',
                            'zSharePartic-Name_Components-HasDataIndicator-30',
                            'zSharePartic-Name_Components_Plist-31',
                            'zSharePartic-Is Current User-32',
                            'zSharePartic-Role-33',
                            'zShare-Preview_Data-DataIndicator-34',
                            'zShare-Preview_Data-BLOB_JPG-35',
                            'SPLzSharePartic-Is Current User-36',
                            'SPLzSharePartic-Role-37',
                            'zAsstContrib-Participant= zSharePartic-zPK-38',
                            'SPLzSharePartic-Email Address-39',
                            'SPLzSharePartic-Phone Number-40',
                            'SPLzSharePartic-Name_Components-HasDataIndicator-41',
                            'SPLzSharePartic-Name_Components_Plist-42',
                            'zShare-Preview_Data-DataIndicator-43',
                            'zShare-Preview_Data-BLOB_JPG-44',
                            'zAsset-zPK-45',
                            'zAddAssetAttr-zPK-46',
                            'zAsset-UUID = store.cloudphotodb-47',
                            'zAddAssetAttr-Master Fingerprint-48')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph10.2-Assets have embedded files-SyndPL'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph10.2-Assets have embedded files-SyndPL'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite assets having embedded files')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("17")) & (version.parse(iosversion) < version.parse("18")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data-HasDataIndicator',
        zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data-HasDataIndicator',
        zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',		
        zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
        AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
        AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
        zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
        CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data-HasDataIndicator',
        CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',
        CASE zSharePartic.ZACCEPTANCESTATUS
            WHEN 1 THEN '1-Invite-Pending_or_Declined-1'
            WHEN 2 THEN '2-Invite-Accepted-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZACCEPTANCESTATUS || ''
        END AS 'zSharePartic-Acceptance Status',
        zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
        zSharePartic.Z_PK AS 'zSharePartic-zPK',
        zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
        zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',
        CASE
            WHEN zSharePartic.ZNAMECOMPONENTS > 0 THEN 'zSharePartic-Name_Components_has_Plist'
            ELSE 'zSharePartic-Name_Components_Empty-NULL'
        END AS 'zSharePartic-Name_Components-HasDataIndicator',
        zSharePartic.ZNAMECOMPONENTS AS 'zSharePartic-Name_Components',        
        CASE zSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_CurrentUser-0'
            WHEN 1 THEN '1-Participant-Is_CurrentUser-1'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZISCURRENTUSER || ''
        END AS 'zSharePartic-Is Current User',
        CASE zSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZROLE || ''
        END AS 'zSharePartic-Role',
        CASE
            WHEN zShare.ZPREVIEWDATA > 0 THEN 'zShare-Preview_Data_has_BLOB'
            ELSE 'zShare-Preview_Data_Empty-NULL'
        END AS 'zShare-Preview_Data-DataIndicator',
        zShare.ZPREVIEWDATA AS 'zShare-Preview_Data',
        CASE SPLzSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_CurrentUser-0'
            WHEN 1 THEN '1-Participant-Is_CurrentUser-1'
            ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZISCURRENTUSER || ''
        END AS 'SPLzSharePartic-Is Current User',
        CASE SPLzSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZROLE || ''
        END AS 'SPLzSharePartic-Role',
        zAssetContrib.ZPARTICIPANT AS 'zAsstContrib-Participant= zSharePartic-zPK',
        SPLzSharePartic.ZEMAILADDRESS AS 'SPLzSharePartic-Email Address',
        SPLzSharePartic.ZPHONENUMBER AS 'SPLzSharePartic-Phone Number',
        CASE
            WHEN SPLzSharePartic.ZNAMECOMPONENTS > 0 THEN 'SPLzSharePartic-Name_Components_has_Plist'
            ELSE 'SPLzSharePartic-Name_Components_Empty-NULL'
        END AS 'SPLzSharePartic-Name_Components-HasDataIndicator',
        SPLzSharePartic.ZNAMECOMPONENTS AS 'SPLzSharePartic-Name_Components',
        CASE
            WHEN SPLzShare.ZPREVIEWDATA > 0 THEN 'SPLzShare-Preview_Data_has_BLOB'
            ELSE 'SPLzShare-Preview_Data_Empty-NULL'
        END AS 'SPLzShare-Preview_Data-DataIndicator',
        SPLzShare.ZPREVIEWDATA AS 'SPLzShare-Preview_Data',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
        zAddAssetAttr.ZADJUSTEDFINGERPRINT AS 'zAddAssetAttr.Adjusted Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
            LEFT JOIN ZSHARE zShare ON zShare.Z_PK = zAsset.ZMOMENTSHARE
            LEFT JOIN ZASSETCONTRIBUTOR zAssetContrib ON zAssetContrib.Z3LIBRARYSCOPEASSETCONTRIBUTORS = zAsset.Z_PK
            LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
            LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.Z_PK = zAssetContrib.ZPARTICIPANT
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                aaashiftedlocation_postal_address = ''
                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                aaareverselocation_postal_address = ''
                # AAAzCldMastMedData.ZDATA-PLIST
                aaazcldmastmeddata_plist_tiff = ''
                aaazcldmastmeddata_plist_exif = ''
                aaazcldmastmeddata_plist_gps = ''
                aaazcldmastmeddata_plist_iptc = ''
                # CMzCldMastMedData.ZDATA-PLIST
                cmzcldmastmeddata_plist_tiff = ''
                cmzcldmastmeddata_plist_exif = ''
                cmzcldmastmeddata_plist_gps = ''
                cmzcldmastmeddata_plist_iptc = ''
                # zSharePartic_ZNAMECOMPONENTS_PLIST
                zsharepartic_namecomponents = ''
                # SPLzSharePartic_ZNAMECOMPONENTS_PLIST
                splzsharepartic_namecomponents = ''
                # zShare.ZPREVIEWDATA-BLOB_JPG
                zshare_previewdata_blob = ''
                # SPLzShare.ZPREVIEWDATA-BLOB_JPG
                splzshare_previewdata_blob = ''

                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                if row[9] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[9])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaashiftedlocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename ' + row[2])

                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                if row[12] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[12])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaareverselocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename ' + row[2])

                # AAAzCldMastMedData.ZDATA-PLIST
                if row[18] is not None:
                    pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[18])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                aaazcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                aaazcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                aaazcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                aaazcldmastmeddata_plist_iptc = val

                # CMzCldMastMedData.ZDATA-PLIST
                if row[24] is not None:
                    pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[24])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                cmzcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                cmzcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                cmzcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                cmzcldmastmeddata_plist_iptc = val

                # zSharePartic_ZNAMECOMPONENTS_PLIST
                if row[31] is not None:
                    pathto = os.path.join(report_folder, 'zSP_Name_Components_' + row[2] + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[31])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            zsharepartic_namecomponents = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from zAsset-Filename' + row[2])

                # SPLzSharePartic_ZNAMECOMPONENTS_PLIST
                if row[42] is not None:
                    pathto = os.path.join(report_folder, 'SPLzSharePartic-Name_Components_' + row[2] + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[42])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            splzsharepartic_namecomponents = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from zAsset-Filename ' + row[2])

                # zShare.ZPREVIEWDATA-BLOB_JPG
                if row[35] is not None:
                    pathto = os.path.join(report_folder, 'zShare_PreviewData_' + row[2] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[35])
                    zshare_previewdata_blob = media_to_html(pathto, files_found, report_folder)

                # SPLzShare.ZPREVIEWDATA-BLOB_JPG
                if row[44] is not None:
                    pathto = os.path.join(report_folder, 'SPLzShare_PreviewData_' + row[2] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[44])
                    splzshare_previewdata_blob = media_to_html(pathto, files_found, report_folder)

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8],
                                  aaashiftedlocation_postal_address,
                                  row[10], row[11],
                                  aaareverselocation_postal_address,
                                  row[13], row[14], row[15], row[16], row[17],
                                  aaazcldmastmeddata_plist_tiff,
                                  aaazcldmastmeddata_plist_exif,
                                  aaazcldmastmeddata_plist_gps,
                                  aaazcldmastmeddata_plist_iptc,
                                  row[19], row[20], row[21], row[22], row[23],
                                  cmzcldmastmeddata_plist_tiff,
                                  cmzcldmastmeddata_plist_exif,
                                  cmzcldmastmeddata_plist_gps,
                                  cmzcldmastmeddata_plist_iptc,
                                  row[25], row[26], row[27], row[28], row[29], row[30],
                                  zsharepartic_namecomponents,
                                  row[32], row[33], row[34],
                                  zshare_previewdata_blob,
                                  row[36], row[37],
                                  row[38], row[39], row[40], row[41],
                                  splzsharepartic_namecomponents,
                                  row[43],
                                  splzshare_previewdata_blob,
                                  row[45], row[46], row[47], row[48], row[49]))

                counter += 1

            description = 'Parses basic asset record data from Syndication.photoslibrary-Photos.sqlite' \
                          ' for assets that have embedded files records for a variety of data. This parser' \
                          ' should be used in conjunction with other parsers to review a complete record' \
                          ' for analysis. The results of this parser could produce multiple records for a single asset.'
            report = ArtifactHtmlReport('Ph10.2-Assets have embedded files-SyndPL')
            report.start_artifact_report(report_folder, 'Ph10.2-Assets have embedded files-SyndPL', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Directory-Path-1',
                            'zAsset-Filename-2',
                            'zAddAssetAttr- Original Filename-3',
                            'zCldMast- Original Filename-4',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-5',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-6',
                            'zAddAssetAttr-Shifted Location Valid-7',
                            'zAddAssetAttr-Shifted Location Data-HasDataIndicator-8',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address-9',
                            'zAddAssetAttr-Reverse Location Is Valid-10',
                            'zAddAssetAttr-Reverse Location Data-HasDataIndicator-11',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address-12',
                            'AAAzCldMastMedData-zOPT-13',
                            'zAddAssetAttr-Media Metadata Type-14',
                            'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-15',
                            'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-16',
                            'AAAzCldMastMedData-Data-HasDataIndicator-17',
                            'AAAzCldMastMedData-Data_plist_TIFF-18',
                            'AAAzCldMastMedData-Data_plist_Exif-18',
                            'AAAzCldMastMedData-Data_plist_GPS-18',
                            'AAAzCldMastMedData-Data_plist_IPTC-18',
                            'CldMasterzCldMastMedData-zOPT-19',
                            'zCldMast-Media Metadata Type-20',
                            'zCldMast-Media Metadata Key= zCldMastMedData.zPK-21',
                            'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-22',
                            'CMzCldMastMedData-Data-HasDataIndicator-23',
                            'CMzCldMastMedData-Data_plist_TIFF-24',
                            'CMzCldMastMedData-Data_plist_Exif-24',
                            'CMzCldMastMedData-Data_plist_GPS-24',
                            'CMzCldMastMedData-Data_plist_IPTC-24',
                            'zSharePartic-Acceptance Status-25',
                            'zSharePartic-User ID-26',
                            'zSharePartic-zPK-27',
                            'zSharePartic-Email Address-28',
                            'zSharePartic-Phone Number-29',
                            'zSharePartic-Name_Components-HasDataIndicator-30',
                            'zSharePartic-Name_Components_Plist-31',
                            'zSharePartic-Is Current User-32',
                            'zSharePartic-Role-33',
                            'zShare-Preview_Data-DataIndicator-34',
                            'zShare-Preview_Data-BLOB_JPG-35',
                            'SPLzSharePartic-Is Current User-36',
                            'SPLzSharePartic-Role-37',
                            'zAsstContrib-Participant= zSharePartic-zPK-38',
                            'SPLzSharePartic-Email Address-39',
                            'SPLzSharePartic-Phone Number-40',
                            'SPLzSharePartic-Name_Components-HasDataIndicator-41',
                            'SPLzSharePartic-Name_Components_Plist-42',
                            'zShare-Preview_Data-DataIndicator-43',
                            'zShare-Preview_Data-BLOB_JPG-44',
                            'zAsset-zPK-45',
                            'zAddAssetAttr-zPK-46',
                            'zAsset-UUID = store.cloudphotodb-47',
                            'zAddAssetAttr-Master Fingerprint-48',
                            'zAddAssetAttr.Adjusted Fingerprint-49')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph10.2-Assets have embedded files-SyndPL'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph10.2-Assets have embedded files-SyndPL'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite assets having embedded files')

        db.close()
        return

    elif version.parse(iosversion) >= version.parse("18"):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data-HasDataIndicator',
        zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data-HasDataIndicator',
        zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',		
        zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
        AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
        AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
        zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
        CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data-HasDataIndicator',
        CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',
        CASE zSharePartic.ZACCEPTANCESTATUS
            WHEN 1 THEN '1-Invite-Pending_or_Declined-1'
            WHEN 2 THEN '2-Invite-Accepted-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZACCEPTANCESTATUS || ''
        END AS 'zSharePartic-Acceptance Status',
        zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
        zSharePartic.Z_PK AS 'zSharePartic-zPK',
        zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
        zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',
        CASE
            WHEN zSharePartic.ZNAMECOMPONENTS > 0 THEN 'zSharePartic-Name_Components_has_Plist'
            ELSE 'zSharePartic-Name_Components_Empty-NULL'
        END AS 'zSharePartic-Name_Components-HasDataIndicator',
        zSharePartic.ZNAMECOMPONENTS AS 'zSharePartic-Name_Components',        
        CASE zSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_CurrentUser-0'
            WHEN 1 THEN '1-Participant-Is_CurrentUser-1'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZISCURRENTUSER || ''
        END AS 'zSharePartic-Is Current User',
        CASE zSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZROLE || ''
        END AS 'zSharePartic-Role',
        CASE
            WHEN zShare.ZPREVIEWDATA > 0 THEN 'zShare-Preview_Data_has_BLOB'
            ELSE 'zShare-Preview_Data_Empty-NULL'
        END AS 'zShare-Preview_Data-DataIndicator',
        zShare.ZPREVIEWDATA AS 'zShare-Preview_Data',
        CASE SPLzSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_CurrentUser-0'
            WHEN 1 THEN '1-Participant-Is_CurrentUser-1'
            ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZISCURRENTUSER || ''
        END AS 'SPLzSharePartic-Is Current User',
        CASE SPLzSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZROLE || ''
        END AS 'SPLzSharePartic-Role',
        zAssetContrib.ZPARTICIPANT AS 'zAsstContrib-Participant= zSharePartic-zPK',
        SPLzSharePartic.ZEMAILADDRESS AS 'SPLzSharePartic-Email Address',
        SPLzSharePartic.ZPHONENUMBER AS 'SPLzSharePartic-Phone Number',
        CASE
            WHEN SPLzSharePartic.ZNAMECOMPONENTS > 0 THEN 'SPLzSharePartic-Name_Components_has_Plist'
            ELSE 'SPLzSharePartic-Name_Components_Empty-NULL'
        END AS 'SPLzSharePartic-Name_Components-HasDataIndicator',
        SPLzSharePartic.ZNAMECOMPONENTS AS 'SPLzSharePartic-Name_Components',
        CASE
            WHEN SPLzShare.ZPREVIEWDATA > 0 THEN 'SPLzShare-Preview_Data_has_BLOB'
            ELSE 'SPLzShare-Preview_Data_Empty-NULL'
        END AS 'SPLzShare-Preview_Data-DataIndicator',
        SPLzShare.ZPREVIEWDATA AS 'SPLzShare-Preview_Data',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash-iOS18',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash-iOS18'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
            LEFT JOIN ZSHARE zShare ON zShare.Z_PK = zAsset.ZMOMENTSHARE
            LEFT JOIN ZASSETCONTRIBUTOR zAssetContrib ON zAssetContrib.Z3LIBRARYSCOPEASSETCONTRIBUTORS = zAsset.Z_PK
            LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
            LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.Z_PK = zAssetContrib.ZPARTICIPANT
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                aaashiftedlocation_postal_address = ''
                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                aaareverselocation_postal_address = ''
                # AAAzCldMastMedData.ZDATA-PLIST
                aaazcldmastmeddata_plist_tiff = ''
                aaazcldmastmeddata_plist_exif = ''
                aaazcldmastmeddata_plist_gps = ''
                aaazcldmastmeddata_plist_iptc = ''
                # CMzCldMastMedData.ZDATA-PLIST
                cmzcldmastmeddata_plist_tiff = ''
                cmzcldmastmeddata_plist_exif = ''
                cmzcldmastmeddata_plist_gps = ''
                cmzcldmastmeddata_plist_iptc = ''
                # zSharePartic_ZNAMECOMPONENTS_PLIST
                zsharepartic_namecomponents = ''
                # SPLzSharePartic_ZNAMECOMPONENTS_PLIST
                splzsharepartic_namecomponents = ''
                # zShare.ZPREVIEWDATA-BLOB_JPG
                zshare_previewdata_blob = ''
                # SPLzShare.ZPREVIEWDATA-BLOB_JPG
                splzshare_previewdata_blob = ''

                # zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
                if row[9] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[9])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaashiftedlocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename ' + row[2])

                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                if row[12] is not None:
                    pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[12])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaareverselocation_postal_address = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported plist from zAsset-Filename ' + row[2])

                # AAAzCldMastMedData.ZDATA-PLIST
                if row[18] is not None:
                    pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[18])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                aaazcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                aaazcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                aaazcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                aaazcldmastmeddata_plist_iptc = val

                # CMzCldMastMedData.ZDATA-PLIST
                if row[24] is not None:
                    pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[2] + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[24])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)

                        for key, val in plist.items():
                            if key == '{TIFF}':
                                cmzcldmastmeddata_plist_tiff = val
                            elif key == '{Exif}':
                                cmzcldmastmeddata_plist_exif = val
                            elif key == '{GPS}':
                                cmzcldmastmeddata_plist_gps = val
                            elif key == '{IPTC}':
                                cmzcldmastmeddata_plist_iptc = val

                # zSharePartic_ZNAMECOMPONENTS_PLIST
                if row[31] is not None:
                    pathto = os.path.join(report_folder, 'zSP_Name_Components_' + row[2] + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[31])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            zsharepartic_namecomponents = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from zAsset-Filename' + row[2])

                # SPLzSharePartic_ZNAMECOMPONENTS_PLIST
                if row[42] is not None:
                    pathto = os.path.join(report_folder, 'SPLzSharePartic-Name_Components_' + row[2] + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[42])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            splzsharepartic_namecomponents = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from zAsset-Filename ' + row[2])

                # zShare.ZPREVIEWDATA-BLOB_JPG
                if row[35] is not None:
                    pathto = os.path.join(report_folder, 'zShare_PreviewData_' + row[2] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[35])
                    zshare_previewdata_blob = media_to_html(pathto, files_found, report_folder)

                # SPLzShare.ZPREVIEWDATA-BLOB_JPG
                if row[44] is not None:
                    pathto = os.path.join(report_folder, 'SPLzShare_PreviewData_' + row[2] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[44])
                    splzshare_previewdata_blob = media_to_html(pathto, files_found, report_folder)

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8],
                                  aaashiftedlocation_postal_address,
                                  row[10], row[11],
                                  aaareverselocation_postal_address,
                                  row[13], row[14], row[15], row[16], row[17],
                                  aaazcldmastmeddata_plist_tiff,
                                  aaazcldmastmeddata_plist_exif,
                                  aaazcldmastmeddata_plist_gps,
                                  aaazcldmastmeddata_plist_iptc,
                                  row[19], row[20], row[21], row[22], row[23],
                                  cmzcldmastmeddata_plist_tiff,
                                  cmzcldmastmeddata_plist_exif,
                                  cmzcldmastmeddata_plist_gps,
                                  cmzcldmastmeddata_plist_iptc,
                                  row[25], row[26], row[27], row[28], row[29], row[30],
                                  zsharepartic_namecomponents,
                                  row[32], row[33], row[34],
                                  zshare_previewdata_blob,
                                  row[36], row[37],
                                  row[38], row[39], row[40], row[41],
                                  splzsharepartic_namecomponents,
                                  row[43],
                                  splzshare_previewdata_blob,
                                  row[45], row[46], row[47], row[48], row[49]))

                counter += 1

            description = 'Parses basic asset record data from Syndication.photoslibrary-Photos.sqlite' \
                          ' for assets that have embedded files records for a variety of data. This parser' \
                          ' should be used in conjunction with other parsers to review a complete record' \
                          ' for analysis. The results of this parser could produce multiple records for a single asset.'
            report = ArtifactHtmlReport('Ph10.2-Assets have embedded files-SyndPL')
            report.start_artifact_report(report_folder, 'Ph10.2-Assets have embedded files-SyndPL', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Directory-Path-1',
                            'zAsset-Filename-2',
                            'zAddAssetAttr- Original Filename-3',
                            'zCldMast- Original Filename-4',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-5',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-6',
                            'zAddAssetAttr-Shifted Location Valid-7',
                            'zAddAssetAttr-Shifted Location Data-HasDataIndicator-8',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address-9',
                            'zAddAssetAttr-Reverse Location Is Valid-10',
                            'zAddAssetAttr-Reverse Location Data-HasDataIndicator-11',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address-12',
                            'AAAzCldMastMedData-zOPT-13',
                            'zAddAssetAttr-Media Metadata Type-14',
                            'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-15',
                            'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-16',
                            'AAAzCldMastMedData-Data-HasDataIndicator-17',
                            'AAAzCldMastMedData-Data_plist_TIFF-18',
                            'AAAzCldMastMedData-Data_plist_Exif-18',
                            'AAAzCldMastMedData-Data_plist_GPS-18',
                            'AAAzCldMastMedData-Data_plist_IPTC-18',
                            'CldMasterzCldMastMedData-zOPT-19',
                            'zCldMast-Media Metadata Type-20',
                            'zCldMast-Media Metadata Key= zCldMastMedData.zPK-21',
                            'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-22',
                            'CMzCldMastMedData-Data-HasDataIndicator-23',
                            'CMzCldMastMedData-Data_plist_TIFF-24',
                            'CMzCldMastMedData-Data_plist_Exif-24',
                            'CMzCldMastMedData-Data_plist_GPS-24',
                            'CMzCldMastMedData-Data_plist_IPTC-24',
                            'zSharePartic-Acceptance Status-25',
                            'zSharePartic-User ID-26',
                            'zSharePartic-zPK-27',
                            'zSharePartic-Email Address-28',
                            'zSharePartic-Phone Number-29',
                            'zSharePartic-Name_Components-HasDataIndicator-30',
                            'zSharePartic-Name_Components_Plist-31',
                            'zSharePartic-Is Current User-32',
                            'zSharePartic-Role-33',
                            'zShare-Preview_Data-DataIndicator-34',
                            'zShare-Preview_Data-BLOB_JPG-35',
                            'SPLzSharePartic-Is Current User-36',
                            'SPLzSharePartic-Role-37',
                            'zAsstContrib-Participant= zSharePartic-zPK-38',
                            'SPLzSharePartic-Email Address-39',
                            'SPLzSharePartic-Phone Number-40',
                            'SPLzSharePartic-Name_Components-HasDataIndicator-41',
                            'SPLzSharePartic-Name_Components_Plist-42',
                            'zShare-Preview_Data-DataIndicator-43',
                            'zShare-Preview_Data-BLOB_JPG-44',
                            'zAsset-zPK-45',
                            'zAddAssetAttr-zPK-46',
                            'zAsset-UUID = store.cloudphotodb-47',
                            'zAddAssetAttr-Original Stable Hash-iOS18-48',
                            'zAddAssetAttr.Adjusted Stable Hash-iOS18-49')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph10.2-Assets have embedded files-SyndPL'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph10.2-Assets have embedded files-SyndPL'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite assets having embedded files')

        db.close()
        return


__artifacts_v2__ = {
    'Ph10-1-Assets have embedded files-PhDaPsql': {
        'name': 'PhDaPL Photos.sqlite Ph10.1 assets have embedded files',
        'description': 'Parses basic asset record data from Photos.sqlite for assets that have embedded files'
                       ' records for a variety of data. This parser should be used in conjunction with other'
                       ' parsers to review a complete record for analysis. The results of this parser could'
                       ' produce multiple records for a single asset.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '2.0',
        'date': '2024-06-12',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-C-Other_Artifacts',
        'notes': '',
        'paths': '*/PhotoData/Photos.sqlite*',
        'function': 'get_ph10assetparsedembeddedfilesphdapsql'
    },
    'Ph10-2-Assets have embedded files-SyndPL': {
        'name': 'SyndPL Photos.sqlite Ph10.2 assets have embedded files',
        'description': 'Parses basic asset record data from Syndication.photoslibrary-Photos.sqlite'
                       ' for assets that have embedded files records for a variety of data. This parser'
                       ' should be used in conjunction with other parsers to review a complete record for analysis.'
                       ' The results of this parser could produce multiple records for a single asset.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '2.0',
        'date': '2024-06-12',
        'requirements': 'Acquisition that contains Syndication Photo Library Photos.sqlite',
        'category': 'Photos.sqlite-S-Syndication_PL_Artifacts',
        'notes': '',
        'paths': '*/mobile/Library/Photos/Libraries/Syndication.photoslibrary/database/Photos.sqlite*',
        'function': 'get_ph10assetparsedembeddedfilessyndpl'
    }
}
