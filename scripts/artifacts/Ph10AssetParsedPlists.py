# Photos.sqlite
# Author:  Scott Koenig, assisted by past contributors
# Version: 1.0
#
#   Description:
#   Parses basic asset record data from Photos.sqlite for assets that have embedded plist records for a variety of data.
#   This parser should be used in conjunction with other parsers to review a complete record for analysis.
#   The results of this parser could produce multiple records for a single asset.
#   This parser is based on research and SQLite queries written by Scott Koenig
#   https://theforensicscooter.com/ and queries found at https://github.com/ScottKjr3347
#

import os
from datetime import datetime
import pytz
import json
import shutil
import base64
from PIL import Image
from pillow_heif import register_heif_opener
import glob
import sys
import stat
from pathlib import Path
import sqlite3
import plistlib
import nska_deserialize as nd
import scripts.artifacts.artGlobals
from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, media_to_html, open_sqlite_db_readonly


def get_ph10assetparsedplistsphdapsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            break
      
    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("10.3.4"):
        logfunc("Unsupported ios version for PhotosData-Photos.sqlite assets have embedded plist from iOS " + iosversion)
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
        zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',
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
                if row[6] is not None:
                    pathto = os.path.join(report_folder, 'zAddAssetAttr-Shifted Location Data' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[6])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)
                        for key, val in plist.items():
                            if key == "geoPlaceResult":
                                aaashiftedlocation_geoplaceresult = val

                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                if row[7] is not None:
                    pathto = os.path.join(report_folder, 'zAddAssetAttr-Reverse Location Data' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[7])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)
                        for key, val in plist.items():
                            if key == "geoPlaceResult":
                                aaareverselocation_geoplaceresult = val

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5],
                                  aaashiftedlocation_geoplaceresult,
                                  aaareverselocation_geoplaceresult,
                                  row[8], row[9], row[10], row[11]))

                counter += 1

            description = 'Parses basic asset record data from Photos.sqlite for assets that have embedded plist' \
                          ' records for a variety of data. This parser should be used in conjunction with other' \
                          ' parsers to review a complete record for analysis. The results of this parser could' \
                          ' produce multiple records for a single asset.'
            report = ArtifactHtmlReport('Photos.sqlite-Other_Artifacts')
            report.start_artifact_report(report_folder, 'Ph10.1-Assets have embedded plists-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Directory-Path-1',
                            'zAsset-Filename-2',
                            'zAddAssetAttr- Original Filename-3',
                            'zCldMast- Original Filename-4',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-5',
                            'zAddAssetAttr-Shifted Location Data-6',
                            'zAddAssetAttr-Reverse Location Data-7',
                            'zAsset-zPK-8',
                            'zAddAssetAttr-zPK-9',
                            'zAsset-UUID = store.cloudphotodb-10',
                            'zAddAssetAttr-Master Fingerprint-11')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph10.1-Assets have embedded plists-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph10.1-Assets have embedded plists-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite assets having embedded plists')

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
        zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',
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
                aaashiftedlocation_postal_address_subadminarea = ''
                aaashiftedlocation_postal_address_sublocality = ''
                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                aaareverselocation_postal_address = ''
                aaareverselocation_postal_address_subadminarea = ''
                aaareverselocation_postal_address_sublocality = ''
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
                if row[7] is not None:
                    pathto = os.path.join(report_folder, 'zAddAssetAttr-Shifted Location Data' + str(counter) + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[7])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaashiftedlocation_postal_address = deserialized_plist['postalAddress']['_formattedAddress']
                            aaashiftedlocation_postal_address_subadminarea = deserialized_plist['postalAddress']['_subAdministrativeArea']
                            aaashiftedlocation_postal_address_sublocality = deserialized_plist['postalAddress']['_subLocality']

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from Asset PK ' + row[2])

                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                if row[9] is not None:
                    pathto = os.path.join(report_folder, 'zAddAssetAttr-Reverse Location Data' + str(counter) + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[9])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaareverselocation_postal_address = deserialized_plist['postalAddress']['_formattedAddress']
                            aaareverselocation_postal_address_subadminarea = deserialized_plist['postalAddress']['_subAdministrativeArea']
                            aaareverselocation_postal_address_sublocality = deserialized_plist['postalAddress']['_subLocality']

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from Asset PK ' + row[2])

                # AAAzCldMastMedData.ZDATA-PLIST
                if row[12] is not None:
                    pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[12])

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
                if row[15] is not None:
                    pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[15])

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

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                aaashiftedlocation_postal_address,
                                aaashiftedlocation_postal_address_subadminarea,
                                aaashiftedlocation_postal_address_sublocality,
                                row[8],
                                aaareverselocation_postal_address,
                                aaareverselocation_postal_address_subadminarea,
                                aaareverselocation_postal_address_sublocality,
                                row[10], row[11],
                                aaazcldmastmeddata_plist_tiff,
                                aaazcldmastmeddata_plist_exif,
                                aaazcldmastmeddata_plist_gps,
                                aaazcldmastmeddata_plist_iptc,
                                row[13], row[14],
                                cmzcldmastmeddata_plist_tiff,
                                cmzcldmastmeddata_plist_exif,
                                cmzcldmastmeddata_plist_gps,
                                cmzcldmastmeddata_plist_iptc,
                                row[16], row[17], row[18], row[19]))

                counter += 1

            description = 'Parses basic asset record data from Photos.sqlite for assets that have embedded plist' \
                          ' records for a variety of data. This parser should be used in conjunction with other' \
                          ' parsers to review a complete record for analysis. The results of this parser could' \
                          ' produce multiple records for a single asset.'
            report = ArtifactHtmlReport('Photos.sqlite-Other_Artifacts')
            report.start_artifact_report(report_folder, 'Ph10.1-Assets have embedded plists-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Directory-Path-1',
                            'zAsset-Filename-2',
                            'zAddAssetAttr- Original Filename-3',
                            'zCldMast- Original Filename-4',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-5',
                            'zAddAssetAttr-Shifted Location Valid-6',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address-7',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address_subadminarea-7',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address_sublocality-7',
                            'zAddAssetAttr-Reverse Location Is Valid-8',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address-9',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address_subadminarea-9',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address_sublocality-9',
                            'AAAzCldMastMedData-zOPT-10',
                            'zAddAssetAttr-Media Metadata Type-11',
                            'AAAzCldMastMedData-Data_plist_TIFF-12',
                            'AAAzCldMastMedData-Data_plist_Exif-12',
                            'AAAzCldMastMedData-Data_plist_GPS-12',
                            'AAAzCldMastMedData-Data_plist_IPTC-12',
                            'CldMasterzCldMastMedData-zOPT-13',
                            'zCldMast-Media Metadata Type-14',
                            'CMzCldMastMedData-Data_plist_TIFF-15',
                            'CMzCldMastMedData-Data_plist_Exif-15',
                            'CMzCldMastMedData-Data_plist_GPS-15',
                            'CMzCldMastMedData-Data_plist_IPTC-15',
                            'zAsset-zPK-16',
                            'zAddAssetAttr-zPK-17',
                            'zAsset-UUID = store.cloudphotodb-18',
                            'zAddAssetAttr-Master Fingerprint-19')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph10.1-Assets have embedded plists-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph10.1-Assets have embedded plists-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite assets having embedded plists')

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
        zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',
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
        CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',
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
                aaashiftedlocation_postal_address_subadminarea = ''
                aaashiftedlocation_postal_address_sublocality = ''
                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                aaareverselocation_postal_address = ''
                aaareverselocation_postal_address_subadminarea = ''
                aaareverselocation_postal_address_sublocality = ''
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
                if row[7] is not None:
                    pathto = os.path.join(report_folder, 'zAddAssetAttr-Shifted Location Data' + str(counter) + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[7])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaashiftedlocation_postal_address = deserialized_plist['postalAddress']['_formattedAddress']
                            aaashiftedlocation_postal_address_subadminarea = deserialized_plist['postalAddress']['_subAdministrativeArea']
                            aaashiftedlocation_postal_address_sublocality = deserialized_plist['postalAddress']['_subLocality']

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from Asset PK ' + row[2])

                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                if row[9] is not None:
                    pathto = os.path.join(report_folder, 'zAddAssetAttr-Reverse Location Data' + str(counter) + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[9])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaareverselocation_postal_address = deserialized_plist['postalAddress']['_formattedAddress']
                            aaareverselocation_postal_address_subadminarea = deserialized_plist['postalAddress']['_subAdministrativeArea']
                            aaareverselocation_postal_address_sublocality = deserialized_plist['postalAddress']['_subLocality']

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[10])
                            else:
                                logfunc('Error reading exported bplist from Asset PK ' + row[10])

                # AAAzCldMastMedData.ZDATA-PLIST
                if row[12] is not None:
                    pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[12])

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
                if row[15] is not None:
                    pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[15])

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

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                  aaashiftedlocation_postal_address,
                                  aaashiftedlocation_postal_address_subadminarea,
                                  aaashiftedlocation_postal_address_sublocality,
                                  row[8],
                                  aaareverselocation_postal_address,
                                  aaareverselocation_postal_address_subadminarea,
                                  aaareverselocation_postal_address_sublocality,
                                  row[10], row[11],
                                  aaazcldmastmeddata_plist_tiff,
                                  aaazcldmastmeddata_plist_exif,
                                  aaazcldmastmeddata_plist_gps,
                                  aaazcldmastmeddata_plist_iptc,
                                  row[13], row[14],
                                  cmzcldmastmeddata_plist_tiff,
                                  cmzcldmastmeddata_plist_exif,
                                  cmzcldmastmeddata_plist_gps,
                                  cmzcldmastmeddata_plist_iptc,
                                  row[16], row[17], row[18], row[19]))

                counter += 1

            description = 'Parses basic asset record data from Photos.sqlite for assets that have embedded plist' \
                          ' records for a variety of data. This parser should be used in conjunction with other' \
                          ' parsers to review a complete record for analysis. The results of this parser could' \
                          ' produce multiple records for a single asset.'
            report = ArtifactHtmlReport('Photos.sqlite-Other_Artifacts')
            report.start_artifact_report(report_folder, 'Ph10.1-Assets have embedded plists-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Directory-Path-1',
                            'zAsset-Filename-2',
                            'zAddAssetAttr- Original Filename-3',
                            'zCldMast- Original Filename-4',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-5',
                            'zAddAssetAttr-Shifted Location Valid-6',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address-7',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address_subadminarea-7',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address_sublocality-7',
                            'zAddAssetAttr-Reverse Location Is Valid-8',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address-9',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address_subadminarea-9',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address_sublocality-9',
                            'AAAzCldMastMedData-zOPT-10',
                            'zAddAssetAttr-Media Metadata Type-11',
                            'AAAzCldMastMedData-Data_plist_TIFF-12',
                            'AAAzCldMastMedData-Data_plist_Exif-12',
                            'AAAzCldMastMedData-Data_plist_GPS-12',
                            'AAAzCldMastMedData-Data_plist_IPTC-12',
                            'CldMasterzCldMastMedData-zOPT-13',
                            'zCldMast-Media Metadata Type-14',
                            'CMzCldMastMedData-Data_plist_TIFF-15',
                            'CMzCldMastMedData-Data_plist_Exif-15',
                            'CMzCldMastMedData-Data_plist_GPS-15',
                            'CMzCldMastMedData-Data_plist_IPTC-15',
                            'zAsset-zPK-16',
                            'zAddAssetAttr-zPK-17',
                            'zAsset-UUID = store.cloudphotodb-18',
                            'zAddAssetAttr-Master Fingerprint-19')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph10.1-Assets have embedded plists-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph10.1-Assets have embedded plists-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite assets having embedded plists')

        db.close()
        return

    elif version.parse(iosversion) >= version.parse("15"):
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
        zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',
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
        CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',
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
                aaashiftedlocation_postal_address_subadminarea = ''
                aaashiftedlocation_postal_address_sublocality = ''
                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                aaareverselocation_postal_address = ''
                aaareverselocation_postal_address_subadminarea = ''
                aaareverselocation_postal_address_sublocality = ''
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
                    pathto = os.path.join(report_folder, 'zAddAssetAttr-Shifted Location Data' + str(counter) + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[8])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaashiftedlocation_postal_address = deserialized_plist['postalAddress']['_formattedAddress']
                            aaashiftedlocation_postal_address_subadminarea = deserialized_plist['postalAddress']['_subAdministrativeArea']
                            aaashiftedlocation_postal_address_sublocality = deserialized_plist['postalAddress']['_subLocality']

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from Asset PK ' + row[2])

                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                if row[10] is not None:
                    pathto = os.path.join(report_folder, 'zAddAssetAttr-Reverse Location Data' + str(counter) + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[10])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaareverselocation_postal_address = deserialized_plist['postalAddress']['_formattedAddress']
                            aaareverselocation_postal_address_subadminarea = deserialized_plist['postalAddress']['_subAdministrativeArea']
                            aaareverselocation_postal_address_sublocality = deserialized_plist['postalAddress']['_subLocality']

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from Asset PK ' + row[2])

                # AAAzCldMastMedData.ZDATA-PLIST
                if row[13] is not None:
                    pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[13])

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
                if row[16] is not None:
                    pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[16])

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
                                  aaashiftedlocation_postal_address_subadminarea,
                                  aaashiftedlocation_postal_address_sublocality,
                                  row[19],
                                  aaareverselocation_postal_address,
                                  aaareverselocation_postal_address_subadminarea,
                                  aaareverselocation_postal_address_sublocality,
                                  row[11], row[12],
                                  aaazcldmastmeddata_plist_tiff,
                                  aaazcldmastmeddata_plist_exif,
                                  aaazcldmastmeddata_plist_gps,
                                  aaazcldmastmeddata_plist_iptc,
                                  row[14], row[15],
                                  cmzcldmastmeddata_plist_tiff,
                                  cmzcldmastmeddata_plist_exif,
                                  cmzcldmastmeddata_plist_gps,
                                  cmzcldmastmeddata_plist_iptc,
                                  row[17], row[18], row[19], row[20]))

                counter += 1

            description = 'Parses basic asset record data from Photos.sqlite for assets that have embedded plist' \
                          ' records for a variety of data. This parser should be used in conjunction with other' \
                          ' parsers to review a complete record for analysis. The results of this parser could' \
                          ' produce multiple records for a single asset.'
            report = ArtifactHtmlReport('Photos.sqlite-Other_Artifacts')
            report.start_artifact_report(report_folder, 'Ph10.1-Assets have embedded plists-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Directory-Path-1',
                            'zAsset-Filename-2',
                            'zAddAssetAttr- Original Filename-3',
                            'zCldMast- Original Filename-4',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-5',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-6',
                            'zAddAssetAttr-Shifted Location Valid-7',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address-8',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address_subadminarea-8',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address_sublocality-8',
                            'zAddAssetAttr-Reverse Location Is Valid-9',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address-10',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address_subadminarea-10',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address_sublocality-10',
                            'AAAzCldMastMedData-zOPT-11',
                            'zAddAssetAttr-Media Metadata Type-12',
                            'AAAzCldMastMedData-Data_plist_TIFF-13',
                            'AAAzCldMastMedData-Data_plist_Exif-13',
                            'AAAzCldMastMedData-Data_plist_GPS-13',
                            'AAAzCldMastMedData-Data_plist_IPTC-13',
                            'CldMasterzCldMastMedData-zOPT-14',
                            'zCldMast-Media Metadata Type-15',
                            'CMzCldMastMedData-Data_plist_TIFF-16',
                            'CMzCldMastMedData-Data_plist_Exif-16',
                            'CMzCldMastMedData-Data_plist_GPS-16',
                            'CMzCldMastMedData-Data_plist_IPTC-16',
                            'zAsset-zPK-17',
                            'zAddAssetAttr-zPK-18',
                            'zAsset-UUID = store.cloudphotodb-19',
                            'zAddAssetAttr-Master Fingerprint-20')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph10.1-Assets have embedded plists-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph10.1-Assets have embedded plists-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite assets having embedded plists')

        db.close()
        return


def get_ph10assetparsedplistssyndpl(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("10.3.4"):
        logfunc("Unsupported ios version for Syndication.photoslibrary-database-Photos.sqlite assets have embedded plist from iOS " + iosversion)
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
        zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',
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
                if row[6] is not None:
                    pathto = os.path.join(report_folder, 'zAddAssetAttr-Shifted Location Data' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[6])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)
                        for key, val in plist.items():
                            if key == "geoPlaceResult":
                                aaashiftedlocation_geoplaceresult = val

                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                if row[7] is not None:
                    pathto = os.path.join(report_folder, 'zAddAssetAttr-Reverse Location Data' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[7])

                    with open(pathto, "rb") as fp:
                        plist = plistlib.load(fp)
                        for key, val in plist.items():
                            if key == "geoPlaceResult":
                                aaareverselocation_geoplaceresult = val

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5],
                                  aaashiftedlocation_geoplaceresult,
                                  aaareverselocation_geoplaceresult,
                                  row[8], row[9], row[10], row[11]))

                counter += 1

            description = 'Parses basic asset record data from Syndication.photoslibrary-Photos.sqlite' \
                          ' for assets that have embedded plist records for a variety of data. This parser' \
                          ' should be used in conjunction with other parsers to review a complete record' \
                          ' for analysis. The results of this parser could produce multiple records for a single asset.'
            report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
            report.start_artifact_report(report_folder, 'Ph10.2-Assets have embedded plists-SyndPL', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Directory-Path-1',
                            'zAsset-Filename-2',
                            'zAddAssetAttr- Original Filename-3',
                            'zCldMast- Original Filename-4',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-5',
                            'zAddAssetAttr-Shifted Location Data-6',
                            'zAddAssetAttr-Reverse Location Data-7',
                            'zAsset-zPK-8',
                            'zAddAssetAttr-zPK-9',
                            'zAsset-UUID = store.cloudphotodb-10',
                            'zAddAssetAttr-Master Fingerprint-11')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph10.2-Assets have embedded plists-SyndPL'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph10.2-Assets have embedded plists-SyndPL'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for Syndication.photoslibrary-Photos.sqlite assets having embedded plists')

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
        zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',
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
                aaashiftedlocation_postal_address_subadminarea = ''
                aaashiftedlocation_postal_address_sublocality = ''
                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                aaareverselocation_postal_address = ''
                aaareverselocation_postal_address_subadminarea = ''
                aaareverselocation_postal_address_sublocality = ''
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
                if row[7] is not None:
                    pathto = os.path.join(report_folder, 'zAddAssetAttr-Shifted Location Data' + str(counter) + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[7])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaashiftedlocation_postal_address = deserialized_plist['postalAddress']['_formattedAddress']
                            aaashiftedlocation_postal_address_subadminarea = deserialized_plist['postalAddress']['_subAdministrativeArea']
                            aaashiftedlocation_postal_address_sublocality = deserialized_plist['postalAddress']['_subLocality']

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from Asset PK ' + row[2])

                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                if row[9] is not None:
                    pathto = os.path.join(report_folder, 'zAddAssetAttr-Reverse Location Data' + str(counter) + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[9])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaareverselocation_postal_address = deserialized_plist['postalAddress']['_formattedAddress']
                            aaareverselocation_postal_address_subadminarea = deserialized_plist['postalAddress']['_subAdministrativeArea']
                            aaareverselocation_postal_address_sublocality = deserialized_plist['postalAddress']['_subLocality']

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from Asset PK ' + row[2])

                # AAAzCldMastMedData.ZDATA-PLIST
                if row[12] is not None:
                    pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[12])

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
                if row[15] is not None:
                    pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[15])

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

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                aaashiftedlocation_postal_address,
                                aaashiftedlocation_postal_address_subadminarea,
                                aaashiftedlocation_postal_address_sublocality,
                                row[8],
                                aaareverselocation_postal_address,
                                aaareverselocation_postal_address_subadminarea,
                                aaareverselocation_postal_address_sublocality,
                                row[10], row[11],
                                aaazcldmastmeddata_plist_tiff,
                                aaazcldmastmeddata_plist_exif,
                                aaazcldmastmeddata_plist_gps,
                                aaazcldmastmeddata_plist_iptc,
                                row[13], row[14],
                                cmzcldmastmeddata_plist_tiff,
                                cmzcldmastmeddata_plist_exif,
                                cmzcldmastmeddata_plist_gps,
                                cmzcldmastmeddata_plist_iptc,
                                row[16], row[17], row[18], row[19]))

                counter += 1

            description = 'Parses basic asset record data from Syndication.photoslibrary-Photos.sqlite' \
                          ' for assets that have embedded plist records for a variety of data. This parser' \
                          ' should be used in conjunction with other parsers to review a complete record' \
                          ' for analysis. The results of this parser could produce multiple records for a single asset.'
            report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
            report.start_artifact_report(report_folder, 'Ph10.2-Assets have embedded plists-SyndPL', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Directory-Path-1',
                            'zAsset-Filename-2',
                            'zAddAssetAttr- Original Filename-3',
                            'zCldMast- Original Filename-4',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-5',
                            'zAddAssetAttr-Shifted Location Valid-6',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address-7',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address_subadminarea-7',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address_sublocality-7',
                            'zAddAssetAttr-Reverse Location Is Valid-8',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address-9',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address_subadminarea-9',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address_sublocality-9',
                            'AAAzCldMastMedData-zOPT-10',
                            'zAddAssetAttr-Media Metadata Type-11',
                            'AAAzCldMastMedData-Data_plist_TIFF-12',
                            'AAAzCldMastMedData-Data_plist_Exif-12',
                            'AAAzCldMastMedData-Data_plist_GPS-12',
                            'AAAzCldMastMedData-Data_plist_IPTC-12',
                            'CldMasterzCldMastMedData-zOPT-13',
                            'zCldMast-Media Metadata Type-14',
                            'CMzCldMastMedData-Data_plist_TIFF-15',
                            'CMzCldMastMedData-Data_plist_Exif-15',
                            'CMzCldMastMedData-Data_plist_GPS-15',
                            'CMzCldMastMedData-Data_plist_IPTC-15',
                            'zAsset-zPK-16',
                            'zAddAssetAttr-zPK-17',
                            'zAsset-UUID = store.cloudphotodb-18',
                            'zAddAssetAttr-Master Fingerprint-19')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph10.2-Assets have embedded plists-SyndPL'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph10.2-Assets have embedded plists-SyndPL'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for Syndication.photoslibrary-Photos.sqlite assets having embedded plists')

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
        zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',
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
        CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',
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
                aaashiftedlocation_postal_address_subadminarea = ''
                aaashiftedlocation_postal_address_sublocality = ''
                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                aaareverselocation_postal_address = ''
                aaareverselocation_postal_address_subadminarea = ''
                aaareverselocation_postal_address_sublocality = ''
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
                if row[7] is not None:
                    pathto = os.path.join(report_folder, 'zAddAssetAttr-Shifted Location Data' + str(counter) + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[7])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaashiftedlocation_postal_address = deserialized_plist['postalAddress']['_formattedAddress']
                            aaashiftedlocation_postal_address_subadminarea = deserialized_plist['postalAddress']['_subAdministrativeArea']
                            aaashiftedlocation_postal_address_sublocality = deserialized_plist['postalAddress']['_subLocality']

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from Asset PK ' + row[2])

                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                if row[9] is not None:
                    pathto = os.path.join(report_folder, 'zAddAssetAttr-Reverse Location Data' + str(counter) + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[9])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaareverselocation_postal_address = deserialized_plist['postalAddress']['_formattedAddress']
                            aaareverselocation_postal_address_subadminarea = deserialized_plist['postalAddress']['_subAdministrativeArea']
                            aaareverselocation_postal_address_sublocality = deserialized_plist['postalAddress']['_subLocality']

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[10])
                            else:
                                logfunc('Error reading exported bplist from Asset PK ' + row[10])

                # AAAzCldMastMedData.ZDATA-PLIST
                if row[12] is not None:
                    pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[12])

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
                if row[15] is not None:
                    pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[15])

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

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                  aaashiftedlocation_postal_address,
                                  aaashiftedlocation_postal_address_subadminarea,
                                  aaashiftedlocation_postal_address_sublocality,
                                  row[8],
                                  aaareverselocation_postal_address,
                                  aaareverselocation_postal_address_subadminarea,
                                  aaareverselocation_postal_address_sublocality,
                                  row[10], row[11],
                                  aaazcldmastmeddata_plist_tiff,
                                  aaazcldmastmeddata_plist_exif,
                                  aaazcldmastmeddata_plist_gps,
                                  aaazcldmastmeddata_plist_iptc,
                                  row[13], row[14],
                                  cmzcldmastmeddata_plist_tiff,
                                  cmzcldmastmeddata_plist_exif,
                                  cmzcldmastmeddata_plist_gps,
                                  cmzcldmastmeddata_plist_iptc,
                                  row[16], row[17], row[18], row[19]))

                counter += 1

            description = 'Parses basic asset record data from Syndication.photoslibrary-Photos.sqlite' \
                          ' for assets that have embedded plist records for a variety of data. This parser' \
                          ' should be used in conjunction with other parsers to review a complete record' \
                          ' for analysis. The results of this parser could produce multiple records for a single asset.'
            report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
            report.start_artifact_report(report_folder, 'Ph10.2-Assets have embedded plists-SyndPL', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Directory-Path-1',
                            'zAsset-Filename-2',
                            'zAddAssetAttr- Original Filename-3',
                            'zCldMast- Original Filename-4',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-5',
                            'zAddAssetAttr-Shifted Location Valid-6',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address-7',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address_subadminarea-7',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address_sublocality-7',
                            'zAddAssetAttr-Reverse Location Is Valid-8',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address-9',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address_subadminarea-9',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address_sublocality-9',
                            'AAAzCldMastMedData-zOPT-10',
                            'zAddAssetAttr-Media Metadata Type-11',
                            'AAAzCldMastMedData-Data_plist_TIFF-12',
                            'AAAzCldMastMedData-Data_plist_Exif-12',
                            'AAAzCldMastMedData-Data_plist_GPS-12',
                            'AAAzCldMastMedData-Data_plist_IPTC-12',
                            'CldMasterzCldMastMedData-zOPT-13',
                            'zCldMast-Media Metadata Type-14',
                            'CMzCldMastMedData-Data_plist_TIFF-15',
                            'CMzCldMastMedData-Data_plist_Exif-15',
                            'CMzCldMastMedData-Data_plist_GPS-15',
                            'CMzCldMastMedData-Data_plist_IPTC-15',
                            'zAsset-zPK-16',
                            'zAddAssetAttr-zPK-17',
                            'zAsset-UUID = store.cloudphotodb-18',
                            'zAddAssetAttr-Master Fingerprint-19')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph10.2-Assets have embedded plists-SyndPL'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph10.2-Assets have embedded plists-SyndPL'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for Syndication.photoslibrary-Photos.sqlite assets having embedded plists')

        db.close()
        return

    elif version.parse(iosversion) >= version.parse("15"):
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
        zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',
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
        CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',
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
                aaashiftedlocation_postal_address_subadminarea = ''
                aaashiftedlocation_postal_address_sublocality = ''
                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                aaareverselocation_postal_address = ''
                aaareverselocation_postal_address_subadminarea = ''
                aaareverselocation_postal_address_sublocality = ''
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
                    pathto = os.path.join(report_folder, 'zAddAssetAttr-Shifted Location Data' + str(counter) + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[8])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaashiftedlocation_postal_address = deserialized_plist['postalAddress']['_formattedAddress']
                            aaashiftedlocation_postal_address_subadminarea = deserialized_plist['postalAddress']['_subAdministrativeArea']
                            aaashiftedlocation_postal_address_sublocality = deserialized_plist['postalAddress']['_subLocality']

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from Asset PK ' + row[2])

                # zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
                if row[10] is not None:
                    pathto = os.path.join(report_folder, 'zAddAssetAttr-Reverse Location Data' + str(counter) + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[10])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            aaareverselocation_postal_address = deserialized_plist['postalAddress']['_formattedAddress']
                            aaareverselocation_postal_address_subadminarea = deserialized_plist['postalAddress']['_subAdministrativeArea']
                            aaareverselocation_postal_address_sublocality = deserialized_plist['postalAddress']['_subLocality']

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[2])
                            else:
                                logfunc('Error reading exported bplist from Asset PK ' + row[2])

                # AAAzCldMastMedData.ZDATA-PLIST
                if row[13] is not None:
                    pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[13])

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
                if row[16] is not None:
                    pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[16])

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
                                  aaashiftedlocation_postal_address_subadminarea,
                                  aaashiftedlocation_postal_address_sublocality,
                                  row[19],
                                  aaareverselocation_postal_address,
                                  aaareverselocation_postal_address_subadminarea,
                                  aaareverselocation_postal_address_sublocality,
                                  row[11], row[12],
                                  aaazcldmastmeddata_plist_tiff,
                                  aaazcldmastmeddata_plist_exif,
                                  aaazcldmastmeddata_plist_gps,
                                  aaazcldmastmeddata_plist_iptc,
                                  row[14], row[15],
                                  cmzcldmastmeddata_plist_tiff,
                                  cmzcldmastmeddata_plist_exif,
                                  cmzcldmastmeddata_plist_gps,
                                  cmzcldmastmeddata_plist_iptc,
                                  row[17], row[18], row[19], row[20]))

                counter += 1

            description = 'Parses basic asset record data from Syndication.photoslibrary-Photos.sqlite' \
                          ' for assets that have embedded plist records for a variety of data. This parser' \
                          ' should be used in conjunction with other parsers to review a complete record' \
                          ' for analysis. The results of this parser could produce multiple records for a single asset.'
            report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
            report.start_artifact_report(report_folder, 'Ph10.2-Assets have embedded plists-SyndPL', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Directory-Path-1',
                            'zAsset-Filename-2',
                            'zAddAssetAttr- Original Filename-3',
                            'zCldMast- Original Filename-4',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-5',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-6',
                            'zAddAssetAttr-Shifted Location Valid-7',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address-8',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address_subadminarea-8',
                            'zAddAssetAttr-Shifted Location Data-bplist_postal_address_sublocality-8',
                            'zAddAssetAttr-Reverse Location Is Valid-9',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address-10',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address_subadminarea-10',
                            'zAddAssetAttr-Reverse Location Data-bplist_postal_address_sublocality-10',
                            'AAAzCldMastMedData-zOPT-11',
                            'zAddAssetAttr-Media Metadata Type-12',
                            'AAAzCldMastMedData-Data_plist_TIFF-13',
                            'AAAzCldMastMedData-Data_plist_Exif-13',
                            'AAAzCldMastMedData-Data_plist_GPS-13',
                            'AAAzCldMastMedData-Data_plist_IPTC-13',
                            'CldMasterzCldMastMedData-zOPT-14',
                            'zCldMast-Media Metadata Type-15',
                            'CMzCldMastMedData-Data_plist_TIFF-16',
                            'CMzCldMastMedData-Data_plist_Exif-16',
                            'CMzCldMastMedData-Data_plist_GPS-16',
                            'CMzCldMastMedData-Data_plist_IPTC-16',
                            'zAsset-zPK-17',
                            'zAddAssetAttr-zPK-18',
                            'zAsset-UUID = store.cloudphotodb-19',
                            'zAddAssetAttr-Master Fingerprint-20')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph10.2-Assets have embedded plists-SyndPL'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph10.2-Assets have embedded plists-SyndPL'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for Syndication.photoslibrary-Photos.sqlite assets having embedded plists')

        db.close()
        return


__artifacts_v2__ = {
    'Ph10-1-Assets have embedded plists-PhDaPsql': {
        'name': 'PhDaPL Photos.sqlite 10.1 assets have embedded plists',
        'description': 'Parses basic asset record data from Photos.sqlite for assets that have embedded plist'
                       ' records for a variety of data. This parser should be used in conjunction with other'
                       ' parsers to review a complete record for analysis. The results of this parser could'
                       ' produce multiple records for a single asset.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.0',
        'date': '2024-04-28',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-Other_Artifacts',
        'notes': '',
        'paths': '*/mobile/Media/PhotoData/Photos.sqlite*',
        'function': 'get_ph10assetparsedplistsphdapsql'
    },
    'Ph10-2-Assets have embedded plists-SyndPL': {
        'name': 'SyndPL Photos.sqlite 10.2 assets have embedded plists',
        'description': 'Parses basic asset record data from Syndication.photoslibrary-Photos.sqlite'
                       ' for assets that have embedded plist records for a variety of data. This parser'
                       ' should be used in conjunction with other parsers to review a complete record for analysis.'
                       ' The results of this parser could produce multiple records for a single asset.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.0',
        'date': '2024-04-28',
        'requirements': 'Acquisition that contains Syndication Photo Library Photos.sqlite',
        'category': 'Photos.sqlite-Syndication_PL_Artifacts',
        'notes': '',
        'paths': '*/mobile/Library/Photos/Libraries/Syndication.photoslibrary/database/Photos.sqlite*',
        'function': 'get_ph10assetparsedplistssyndpl'
    }
}
