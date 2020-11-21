import glob
import os
import sqlite3
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, kmlgen, tsv, is_platform_windows, open_sqlite_db_readonly


def get_routineDCloud(files_found, report_folder, seeker):
    iOSversion = scripts.artifacts.artGlobals.versionf
    for file_found in files_found:
      file_found = str(file_found)
      
      if file_found.endswith('Cloud-V2.sqlite'):
        break
        
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    if version.parse(iOSversion) >= version.parse("12"):
        cursor.execute('''
        select 
        datetime(zrtaddressmo.zcreationdate + 978307200, 'unixepoch'),
        datetime(zrtaddressmo.zexpirationdate + 978307200, 'unixepoch'),
        zrtaddressmo.zcountry,
        zrtaddressmo.zcountrycode,
        zrtaddressmo.zpostalcode,
        zrtaddressmo.zlocality,
        zrtaddressmo.zsublocality,
        zrtaddressmo.zthoroughfare,
        zrtaddressmo.zsubthoroughfare,
        zrtaddressmo.zsubadministrativearea,  
        zrtaddressmo.zareasofinterest
        from zrtaddressmo
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []    
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))
            
            description = 'Address'
            report = ArtifactHtmlReport('Locations')
            report.start_artifact_report(report_folder, 'RoutineD Cloud Addresses', description)
            report.add_script()
            data_headers = ('Address Creation Date','Address Expiration Date','Country','Country Code','Postal Code', 'Locality','Sublocality','Throroughfare','Subthroroughfare','Subadministrative Area','Area of Interest' )     
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'RoutineD Cloud Addresses'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'RoutineD Cloud Addresses'
            timeline(report_folder, tlactivity, data_list, data_headers)
            

        else:
            logfunc('No RoutineD Cloud Addresses data available')
            
    if version.parse(iOSversion) >= version.parse("12"):
      cursor.execute('''
      select
      datetime(zrtmapitemmo.zcreationdate + 978307200, 'unixepoch'),
      datetime(zrtmapitemmo.zexpirationdate + 978307200, 'unixepoch'),
      zrtmapitemmo.zname,
      zrtaddressmo.zcountry,
      zrtaddressmo.zcountrycode,
      zrtaddressmo.zpostalcode,
      zrtaddressmo.zlocality,
      zrtaddressmo.zsublocality,
      zrtaddressmo.zthoroughfare,
      zrtaddressmo.zsubthoroughfare,
      zrtaddressmo.zsubadministrativearea,  
      zrtaddressmo.zareasofinterest,
      zrtmapitemmo.zlatitude,
      zrtmapitemmo.zlongitude,
      zrtmapitemmo.zuncertainty
      from zrtmapitemmo, zrtaddressmo 
      where  zrtmapitemmo.z_pk == zrtaddressmo.zmapitem
      ''')
      all_rows = cursor.fetchall()
      usageentries = len(all_rows)
      data_list = []  
      if usageentries > 0:
          for row in all_rows:
              data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14]))
          
          description = 'RoutineD Cloud Map Items'
          report = ArtifactHtmlReport('Locations')
          report.start_artifact_report(report_folder, 'RoutineD Cloud Map Items', description)
          report.add_script()
          data_headers = ('Timestamp','Map Item Expiration Date','Map Item Name','Country','Country Code','Postal Code', 'Locality','Sublocality','Throroughfare','Subthroroughfare','Subadministrative Area','Area of Interest', 'Latitude','Longitude','Uncertainty' )    
          report.write_artifact_data_table(data_headers, data_list, file_found)
          report.end_artifact_report()
          
          tsvname = 'RoutineD Cloud Map Items'
          tsv(report_folder, data_headers, data_list, tsvname)
          
          tlactivity = 'RoutineD Cloud Map Items'
          timeline(report_folder, tlactivity, data_list, data_headers)
          
          kmlactivity = 'RoutineD Cloud Map Items'
          kmlgen(report_folder, kmlactivity, data_list, data_headers)

      else:
          logfunc('No RoutineD Map Items Cloud-V2.sqlite data available')
    
        
    if (version.parse(iOSversion) >= version.parse("13")):
      cursor.execute('''
      select
      datetime(zrtlearnedvisitmo.zentrydate + 978307200, 'unixepoch'),
      datetime(zrtlearnedvisitmo.zexitdate + 978307200, 'unixepoch'),
      (zexitdate-zentrydate)/60.00,
      zrtlearnedvisitmo.zplace,
      zrtlearnedvisitmo.zdatapointcount,
      zrtaddressmo.zcountry,
      zrtaddressmo.zcountrycode,
      zrtaddressmo.zpostalcode,
      zrtaddressmo.zlocality,
      zrtaddressmo.zsublocality,
      zrtaddressmo.zthoroughfare,
      zrtaddressmo.zsubthoroughfare,
      zrtaddressmo.zsubadministrativearea,  
      zrtaddressmo.zareasofinterest,
      zrtlearnedvisitmo.zlocationuncertainty,
      zrtlearnedvisitmo.zconfidence,
      datetime(zrtlearnedvisitmo.zcreationdate + 978307200, 'unixepoch'),
      datetime(zrtlearnedvisitmo.zexpirationdate + 978307200, 'unixepoch'),
      zrtdevicemo.zdeviceclass,
      zrtdevicemo.zdevicemodel,
      zrtdevicemo.zdevicename,
      datetime(zrtlearnedplacemo.zcreationdate + 978307200, 'unixepoch'),
      datetime(zrtlearnedplacemo.zexpirationdate + 978307200, 'unixepoch'),
      datetime(zrtaddressmo.zcreationdate + 978307200, 'unixepoch'),   
      zrtlearnedvisitmo.zlocationlatitude,
      zrtlearnedvisitmo.zlocationlongitude,
      datetime(zrtmapitemmo.zcreationdate + 978307200, 'unixepoch'),
      datetime(zrtmapitemmo.zexpirationdate + 978307200, 'unixepoch'),
      zrtmapitemmo.zlatitude,
      zrtmapitemmo.zlongitude,
      zrtmapitemmo.zuncertainty,
      zrtmapitemmo.zdisplaylanguage,
      zrtmapitemmo.zname 
      from
      zrtlearnedvisitmo, zrtdevicemo, zrtlearnedplacemo,  zrtaddressmo, zrtmapitemmo
      where zrtlearnedvisitmo.zdevice = zrtdevicemo.z_pk 
      and zrtlearnedplacemo.z_pk = zrtlearnedvisitmo.zplace
      and zrtaddressmo.zmapitem = zrtlearnedplacemo.zmapitem
      and zrtmapitemmo.z_pk = zrtlearnedplacemo.zmapitem
            
      ''')

      all_rows = cursor.fetchall()
      usageentries = len(all_rows)
      data_list = []    
      if usageentries > 0:
          for row in all_rows:
              data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27], row[28], row[29], row[30], row[31], row[32]))
          
          description = 'Significant Locations - Vist Entry & Exit (Historical)'
          report = ArtifactHtmlReport('Locations')
          report.start_artifact_report(report_folder, 'RoutineD Cloud Visit Entry Exit', description)
          report.add_script()
          data_headers = ('Timestamp','Visit Exit','Visit Time (Minutes)','Place ID','Data Point Count','Country','Country Code','Postal Code', 'Locality','Sublocality','Throroughfare','Subthroroughfare','Subadministrative Area','Area of Interest', 'Location Uncertainty', 'Confidence','Visit Creation','Visit Expiration','Device Class','Device Model','Device Name','Learned Placed Creation', 'Learned Place Expiration','Address Creation', 'Latitude','Longitude','Map Item Creation Date','Map Item Expiration Date','Map Item Latitude','Map Item Longitude','Uncertainty','Map Item Language','Map Item Name' )     
          report.write_artifact_data_table(data_headers, data_list, file_found)
          report.end_artifact_report()
          
          tsvname = 'RoutineD Cloud Visit Entry Exit'
          tsv(report_folder, data_headers, data_list, tsvname)
          
          tlactivity = 'RoutineD Cloud Visit Entry Exit'
          timeline(report_folder, tlactivity, data_list, data_headers)
          
          kmlactivity = 'RoutineD Cloud Visit Entry Exit'
          kmlgen(report_folder, kmlactivity, data_list, data_headers)

      else:
          logfunc('No RoutineD Significant Locations - Vist Entry & Exit (Historical)')
          
          