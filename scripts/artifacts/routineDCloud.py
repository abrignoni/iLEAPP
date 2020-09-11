import glob
import os
import sqlite3
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, tsv, is_platform_windows 


def get_routineDCloud(files_found, report_folder, seeker):
    iOSversion = scripts.artifacts.artGlobals.versionf
    for file_found in files_found:
      file_found = str(file_found)
      
      if file_found.endswith('Cloud-V2.sqlite'):
        break
        
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    if version.parse(iOSversion) >= version.parse("12"):
        cursor.execute('''
        SELECT 
            DATETIME(ZRTADDRESSMO.ZCREATIONDATE + 978307200, 'unixepoch') AS "ADDRESS CREATION DATE",
            DATETIME(ZRTADDRESSMO.ZEXPIRATIONDATE + 978307200, 'unixepoch') AS "ADDRESS EXPIRATION DATE",
            ZRTADDRESSMO.ZCOUNTRY AS "COUNTRY",
            ZRTADDRESSMO.ZCOUNTRYCODE AS "COUNTRY CODE",
            ZRTADDRESSMO.ZPOSTALCODE AS "POSTAL CODE",
            ZRTADDRESSMO.ZLOCALITY AS "LOCALITY",
            ZRTADDRESSMO.ZSUBLOCALITY AS "SUBLOCALITY",
            ZRTADDRESSMO.ZTHOROUGHFARE AS "THROROUGHFARE",
            ZRTADDRESSMO.ZSUBTHOROUGHFARE AS "SUBTHOROUGHFARE",
            ZRTADDRESSMO.ZSUBADMINISTRATIVEAREA AS "SUBADMINISTRATIVE AREA",  
            ZRTADDRESSMO.ZAREASOFINTEREST AS "AREA OF INTEREST",
            ZRTADDRESSMO.ZOCEAN AS "OCEAN",
            ZRTADDRESSMO.ZINLANDWATER AS "INLAND WATER",
            ZRTADDRESSMO.ZISLAND AS "ISLAND",
            ZRTADDRESSMO.Z_PK  AS "ZRTADDRESSMO TABLE ID" 
        FROM ZRTADDRESSMO
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []    
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14]))
            
            description = 'Address'
            report = ArtifactHtmlReport('Locations')
            report.start_artifact_report(report_folder, 'RoutineD Cloud Addresses', description)
            report.add_script()
            data_headers = ('Address Creation Date','Address Expiration Date','Country','Country Code','Postal Code', 'Locality','Sublocality','Throroughfare','Subthroroughfare','Subadministrative Area','Area of Interest','Ocean', 'Inland Water', 'Island', 'Table ID' )     
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'RoutineD Cloud Addresses'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'RoutineD Cloud Addresses'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No RoutineD Cloud Addresses data available')
            
    if version.parse(iOSversion) >= version.parse("13"):
      cursor.execute('''
      SELECT
        DATETIME(ZRTMAPITEMMO.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS "MAP ITEM CREATION DATE",
        DATETIME(ZRTMAPITEMMO.ZEXPIRATIONDATE + 978307200, 'UNIXEPOCH') AS "MAP ITEM EXPIRATION DATE", 
        ZRTMAPITEMMO.ZLATITUDE || ", " || ZRTMAPITEMMO.ZLONGITUDE AS "MAP ITEM COORDINATES",
        ZRTMAPITEMMO.ZNAME AS "MAP ITEM NAME",
        ZRTADDRESSMO.ZCOUNTRY AS "COUNTRY",
        ZRTADDRESSMO.ZCOUNTRYCODE AS "COUNTRY CODE",
        ZRTADDRESSMO.ZPOSTALCODE AS "POSTAL CODE",
        ZRTADDRESSMO.ZLOCALITY AS "LOCALITY",
        ZRTADDRESSMO.ZSUBLOCALITY AS "SUBLOCALITY",
        ZRTADDRESSMO.ZTHOROUGHFARE AS "THROROUGHFARE",
        ZRTADDRESSMO.ZSUBTHOROUGHFARE AS "SUBTHOROUGHFARE",
        ZRTADDRESSMO.ZSUBADMINISTRATIVEAREA AS "SUBADMINISTRATIVE AREA",  
        ZRTADDRESSMO.ZAREASOFINTEREST AS "AREA OF INTEREST",
        ZRTADDRESSMO.ZOCEAN AS "OCEAN",
        ZRTADDRESSMO.ZINLANDWATER AS "INLAND WATER",
        ZRTADDRESSMO.ZISLAND AS "ISLAND",
        ZRTMAPITEMMO.ZLATITUDE AS "LATITUTE",
        ZRTMAPITEMMO.ZLONGITUDE AS "LONGITUDE",
        ZRTMAPITEMMO.ZUNCERTAINTY AS "UNCERTAINTY",
        ZRTMAPITEMMO.ZDISPLAYLANGUAGE AS "MAP ITEM LANGUAGE",
        ZRTMAPITEMMO.Z_PK  AS "ZRTMAPITEMMO TABLE ID" 
          FROM ZRTMAPITEMMO
          LEFT JOIN ZRTADDRESSMO ON  ZRTMAPITEMMO.Z_PK == ZRTADDRESSMO.ZMAPITEM
      ''')
      all_rows = cursor.fetchall()
      usageentries = len(all_rows)
      data_list = []  
      if usageentries > 0:
          for row in all_rows:
              data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20]))
          
          description = 'RoutineD Cloud Map Items'
          report = ArtifactHtmlReport('Locations')
          report.start_artifact_report(report_folder, 'RoutineD Cloud Map Items', description)
          report.add_script()
          data_headers = ('Map Item Creation Date','Map Item Expiration Date','Map Item Coordinates','Map Item Name','Country','Country Code','Postal Code', 'Locality','Sublocality','Throroughfare','Subthroroughfare','Subadministrative Area','Area of Interest','Ocean', 'Inland Water', 'Island', 'Latitude','Longitude','Uncertainty','Map Item Language','Table ID' )    
          report.write_artifact_data_table(data_headers, data_list, file_found)
          report.end_artifact_report()
          
          tsvname = 'RoutineD Cloud Map Items'
          tsv(report_folder, data_headers, data_list, tsvname)
          
          tlactivity = 'RoutineD Cloud Map Items'
          timeline(report_folder, tlactivity, data_list, data_headers)

      else:
          logfunc('No RoutineD Map Items Cloud-V2.sqlite data available')
    
    if (version.parse(iOSversion) >= version.parse("12")) and (version.parse(iOSversion) < version.parse("13")):
      cursor.execute('''
      SELECT 
        DATETIME(ZRTMAPITEMMO.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS "MAP ITEM CREATION DATE",
        DATETIME(ZRTMAPITEMMO.ZEXPIRATIONDATE + 978307200, 'UNIXEPOCH') AS "MAP ITEM EXPIRATION DATE",
        ZRTMAPITEMMO.ZLATITUDE || ", " || ZRTMAPITEMMO.ZLONGITUDE AS "MAP ITEM COORDINATES",
        ZRTMAPITEMMO.ZNAME AS "MAP ITEM NAME",
        ZRTADDRESSMO.ZCOUNTRY AS "COUNTRY",
        ZRTADDRESSMO.ZCOUNTRYCODE AS "COUNTRY CODE",
        ZRTADDRESSMO.ZPOSTALCODE AS "POSTAL CODE",
        ZRTADDRESSMO.ZLOCALITY AS "LOCALITY",
        ZRTADDRESSMO.ZSUBLOCALITY AS "SUBLOCALITY",
        ZRTADDRESSMO.ZTHOROUGHFARE AS "THROROUGHFARE",
        ZRTADDRESSMO.ZSUBTHOROUGHFARE AS "SUBTHOROUGHFARE",
        ZRTADDRESSMO.ZSUBADMINISTRATIVEAREA AS "SUBADMINISTRATIVE AREA",  
        ZRTADDRESSMO.ZAREASOFINTEREST AS "AREA OF INTEREST",
        ZRTADDRESSMO.ZOCEAN AS "OCEAN",
        ZRTADDRESSMO.ZINLANDWATER AS "INLAND WATER",
        ZRTADDRESSMO.ZISLAND AS "ISLAND",
        ZRTMAPITEMMO.ZLATITUDE AS "LATITUTE",
        ZRTMAPITEMMO.ZLONGITUDE AS "LONGITUDE",
        ZRTMAPITEMMO.ZUNCERTAINTY AS "UNCERTAINTY",
        ZRTMAPITEMMO.Z_PK  AS "ZRTMAPITEMMO TABLE ID" 
          FROM ZRTMAPITEMMO
          LEFT JOIN ZRTADDRESSMO ON  ZRTMAPITEMMO.Z_PK == ZRTADDRESSMO.ZMAPITEM      
      ''')

      all_rows = cursor.fetchall()
      usageentries = len(all_rows)
      data_list = []    
      if usageentries > 0:
          for row in all_rows:
              data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[14], row[15], row[16], row[17], row[18], row[19]))
          
          description = 'RoutineD Cloud Map Items'
          report = ArtifactHtmlReport('Locations')
          report.start_artifact_report(report_folder, 'RoutineD Cloud Map Items', description)
          report.add_script()
          data_headers = ('Map Item Creation Date','Map Item Expiration Date','Map Item Coordinates','Map Item Name','Country','Country Code','Postal Code', 'Locality','Sublocality','Throroughfare','Subthroroughfare','Subadministrative Area','Area of Interest','Ocean', 'Inland Water', 'Island', 'Latitude','Longitude','Uncertainty','Table ID')        
          report.write_artifact_data_table(data_headers, data_list, file_found)
          report.end_artifact_report()
          
          tsvname = 'RoutineD Cloud Map Items'
          tsv(report_folder, data_headers, data_list, tsvname)
          
          tlactivity = 'RoutineD Cloud Map Items'
          timeline(report_folder, tlactivity, data_list, data_headers)

      else:
          logfunc('No RoutineD Cloud Map Items data available')
    
    if (version.parse(iOSversion) >= version.parse("13")):
      cursor.execute('''
      SELECT
          DATETIME(ZRTLEARNEDVISITMO.ZENTRYDATE + 978307200, 'UNIXEPOCH') AS "VISIT ENTRY",
          DATETIME(ZRTLEARNEDVISITMO.ZEXITDATE + 978307200, 'UNIXEPOCH') AS "VISIT EXIT",
          (ZEXITDATE-ZENTRYDATE)/60.00 AS "VISIT TIME (MINUTES)",
          ZRTLEARNEDVISITMO.ZLOCATIONLATITUDE || ", " || ZRTLEARNEDVISITMO.ZLOCATIONLONGITUDE AS "COORDINATES",
          ZRTLEARNEDVISITMO.ZPLACE AS "PLACE ID",
          ZRTLEARNEDVISITMO.ZDATAPOINTCOUNT AS "DATA POINT COUNT",
          ZRTADDRESSMO.ZCOUNTRY AS "COUNTRY",
          ZRTADDRESSMO.ZCOUNTRYCODE AS "COUNTRY CODE",
          ZRTADDRESSMO.ZPOSTALCODE AS "POSTAL CODE",
          ZRTADDRESSMO.ZLOCALITY AS "LOCALITY",
          ZRTADDRESSMO.ZSUBLOCALITY AS "SUBLOCALITY",
          ZRTADDRESSMO.ZTHOROUGHFARE AS "THROROUGHFARE",
          ZRTADDRESSMO.ZSUBTHOROUGHFARE AS "SUBTHOROUGHFARE",
          ZRTADDRESSMO.ZSUBADMINISTRATIVEAREA AS "SUBADMINISTRATIVE AREA",  
          ZRTADDRESSMO.ZAREASOFINTEREST AS "AREA OF INTEREST",
          ZRTADDRESSMO.ZOCEAN AS "OCEAN",
          ZRTADDRESSMO.ZINLANDWATER AS "INLAND WATER",
          ZRTADDRESSMO.ZISLAND AS "ISLAND",
          ZRTLEARNEDVISITMO.ZLOCATIONUNCERTAINTY AS "LOCATION UNCERTAINTY",
          ZRTLEARNEDVISITMO.ZCONFIDENCE AS "CONFIDENCE",
          DATETIME(ZRTLEARNEDVISITMO.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS "VISIT CREATION",
          DATETIME(ZRTLEARNEDVISITMO.ZEXPIRATIONDATE + 978307200, 'UNIXEPOCH') AS "VISIT EXPIRATION",
          ZRTDEVICEMO.ZDEVICECLASS AS "DEVICE CLASS",
          ZRTDEVICEMO.ZDEVICEMODEL AS "DEVICE MODEL",
          ZRTDEVICEMO.ZDEVICENAME AS "DEVICE NAME",
          DATETIME(ZRTLEARNEDPLACEMO.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS "LEARNED PLACE CREATION",
          DATETIME(ZRTLEARNEDPLACEMO.ZEXPIRATIONDATE + 978307200, 'UNIXEPOCH') AS "LEARNED PLACE EXPIRATION",
          DATETIME(ZRTADDRESSMO.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS "ADDRESS CREATION",   
          ZRTLEARNEDVISITMO.ZLOCATIONLATITUDE AS "LATITUDE",
          ZRTLEARNEDVISITMO.ZLOCATIONLONGITUDE AS "LONGITUDE",
          ZRTMAPITEMMO.ZLATITUDE || ", " || ZRTMAPITEMMO.ZLONGITUDE AS "MAP ITEM COORDINATES",
          DATETIME(ZRTMAPITEMMO.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS "MAP ITEM CREATION DATE",
          DATETIME(ZRTMAPITEMMO.ZEXPIRATIONDATE + 978307200, 'UNIXEPOCH') AS "MAP ITEM EXPIRATION DATE",
          ZRTMAPITEMMO.ZLATITUDE AS "MAP ITEM LATITUTE",
          ZRTMAPITEMMO.ZLONGITUDE AS "MAP ITEM LONGITUDE",
          ZRTMAPITEMMO.ZUNCERTAINTY AS "UNCERTAINTY",
          ZRTMAPITEMMO.ZDISPLAYLANGUAGE AS "MAP ITEM LANGUAGE",
          ZRTMAPITEMMO.ZNAME AS "MAP ITEM NAME",
          ZRTLEARNEDVISITMO.Z_PK AS "ZRTLEARNEDVISITMO TABLE ID" 
        FROM
          ZRTLEARNEDVISITMO 
          LEFT JOIN
            ZRTDEVICEMO ON ZRTLEARNEDVISITMO.ZDEVICE = ZRTDEVICEMO.Z_PK 
          LEFT JOIN
            ZRTLEARNEDPLACEMO ON ZRTLEARNEDPLACEMO.Z_PK = ZRTLEARNEDVISITMO.ZPLACE
          LEFT JOIN
            ZRTADDRESSMO ON ZRTADDRESSMO.ZMAPITEM = ZRTLEARNEDPLACEMO.ZMAPITEM
          LEFT JOIN
            ZRTMAPITEMMO ON ZRTMAPITEMMO.Z_PK = ZRTLEARNEDPLACEMO.ZMAPITEM
            
      ''')

      all_rows = cursor.fetchall()
      usageentries = len(all_rows)
      data_list = []    
      if usageentries > 0:
          for row in all_rows:
              data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27], row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36], row[37], row[38]))
          
          description = 'Significant Locations - Vist Entry & Exit (Historical)'
          report = ArtifactHtmlReport('Locations')
          report.start_artifact_report(report_folder, 'RoutineD Cloud Visit Entry Exit', description)
          report.add_script()
          data_headers = ('Visit Entry','Visit Exit','Visit Time (Minutes)','Coordinates','Place ID','Data Point Count','Country','Country Code','Postal Code', 'Locality','Sublocality','Throroughfare','Subthroroughfare','Subadministrative Area','Area of Interest','Ocean', 'Inland Water', 'Island', 'Location Uncertainty', 'Confidence','Visit Creation','Visit Expiration','Device Class','Device Model','Device Name','Learned Placed Creation', 'Learned Place Expiration','Address Creation', 'Latitude','Longitude','Map Item Coordinates','Map Item Creation Date','Map Item Expiration Date','Map Item Latitude','Map Item Longitude','Uncertainty','Map Item Language','Map Item Name','Table ID' )     
          report.write_artifact_data_table(data_headers, data_list, file_found)
          report.end_artifact_report()
          
          tsvname = 'RoutineD Cloud Visit Entry Exit'
          tsv(report_folder, data_headers, data_list, tsvname)
          
          tlactivity = 'RoutineD Cloud Visit Entry Exit'
          timeline(report_folder, tlactivity, data_list, data_headers)

      else:
          logfunc('No RoutineD Significant Locations - Vist Entry & Exit (Historical)')
          
          
        

      '''
      data_headers = ('Inbound Start Date','Inbound Stop Date','Inbound Time (Minutes)','Coordinates','Place ID','Data Point Count','Country','Country Code','Postal Code', 'Locality','Sublocality','Throroughfare','Subthroroughfare','Subadministrative Area','Area of Interest','Ocean', 'Inland Water', 'Island', 'Location Uncertainty', 'Confidence','Visit Entry','Visit Exit','Visit Creation','Visit Expiration','Device Class','Device Model','Device Name','Learned Placed Creation', 'Learned Place Expiration','Address Creation', 'Latitude','Longitude','Map Item Coordinates','Map Item Creation Date','Map Item Expiration Date','Map Item Latitude','Map Item Longitude','Uncertainty','Map Item Language','Map Item Name','Map Item Geomapitem (Hex Protobuf)','Table ID' )     
        '''