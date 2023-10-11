import os
import plistlib
import datetime
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def convertcocoa(timevalue):
  if timevalue == '':
    return ''
  else:
    unix = datetime.datetime(1970, 1, 1)  # UTC
    cocoa = datetime.datetime(2001, 1, 1)
    delta = cocoa - unix  # timedelta instance 
    timestamp = datetime.datetime.fromtimestamp(timevalue) + delta 
    return (timestamp.strftime('%Y-%m-%d %H:%M:%S'))

def get_locServicesconfig(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    data_list_clientsplist = []
    data_list_routinedplist= []
    data_list_locationdplist = []
    
    for file_found in files_found:
      if file_found.endswith('clients.plist'):
        with open(file_found,'rb') as f :
          clientsplist = plistlib.load(f)
          
      if file_found.endswith('com.apple.locationd.plist'):
        with open(file_found,'rb') as f :
          locationdplist = plistlib.load(f)
          
      if file_found.endswith('com.apple.routined.plist'):
        with open(file_found,'rb') as f :
          routinedplist = plistlib.load(f)
          
          
    for key, value in clientsplist.items():
      if key == 'com.apple.locationd.bundle-/System/Library/LocationBundles/Routine.bundle':
        fencetimestarted = convertcocoa(value.get('FenceTimeStarted', ''))
        comsumptionperiod = convertcocoa(value.get('ConsumptionPeriodBegin', ''))
        receivinglocationinformationtimestopped = convertcocoa(value.get('ReceivingLocationInformationTimeStopped', ''))
        authorization = value.get('Authorization', '')
        locationtimestopped = convertcocoa(value.get('LocationTimeStopped', ''))
        
    data_list_clientsplist.append((fencetimestarted, 'FenceTimeStarted'))
    data_list_clientsplist.append((comsumptionperiod, 'ConsumptionPeriodBegin'))
    data_list_clientsplist.append((receivinglocationinformationtimestopped, 'ReceivingLocationInformationTimeStopped'))
    data_list_clientsplist.append((authorization, 'Authorization'))
    data_list_clientsplist.append((locationtimestopped, 'LocationTimeStopped'))
      
        
    for key, value in locationdplist.items():
      data_list_locationdplist.append((key, value))
      
    for key, value in routinedplist.items():
      if key != 'CloudKitAccountInfoCache':
        data_list_routinedplist.append((value, key))
      
    if len(data_list_routinedplist) > 0:
      report = ArtifactHtmlReport('LSC - com.apple.routined.plist')
      report.start_artifact_report(report_folder, 'LSC - com.apple.routined.plist')
      report.add_script()
      data_headers = ('Value', 'Key')
      report.write_artifact_data_table(data_headers, data_list_routinedplist, file_found)
      report.end_artifact_report()

      tsvname = 'LSC - com.apple.routined.plist'
      tsv(report_folder, data_headers, data_list_routinedplist, tsvname)
  
      tlactivity = 'LSC - com.apple.routined.plist'
      timeline(report_folder, tlactivity, data_list_routinedplist, data_headers)

    else:
      logfunc('No LSC - com.apple.routined.plist')

    if len(data_list_locationdplist) > 0:
      report = ArtifactHtmlReport('LSC - com.apple.locationd.plist')
      report.start_artifact_report(report_folder, 'LSC - com.apple.locationd.plist')
      report.add_script()
      data_headers = ('Value', 'Key')
      report.write_artifact_data_table(data_headers, data_list_locationdplist, file_found)
      report.end_artifact_report()
      
      tsvname = 'LSC - com.apple.locationd.plist'
      tsv(report_folder, data_headers, data_list_locationdplist, tsvname)
      
      tlactivity = 'LSC - com.apple.locationd.plist'
      timeline(report_folder, tlactivity, data_list_locationdplist, data_headers)
      
    else:
      logfunc('No LSC - com.apple.locationd.plist')
    
    if len(data_list_clientsplist) > 0:
      report = ArtifactHtmlReport('LSC - clients.plist')
      report.start_artifact_report(report_folder, 'LSC - clients.plist')
      report.add_script()
      data_headers = ('Value', 'Key')
      report.write_artifact_data_table(data_headers, data_list_clientsplist, file_found)
      report.end_artifact_report()
      
      tsvname = 'LSC - clients.plist'
      tsv(report_folder, data_headers, data_list_clientsplist, tsvname)
      
      tlactivity = 'LSC - clients.plist'
      timeline(report_folder, tlactivity, data_list_clientsplist, data_headers)
      
    else:
      logfunc('No LSC - clients.plist')

__artifacts__ = {
    "locServicesconfig": (
        "Location Services Configurations",
        ('*/Library/Preferences/com.apple.locationd.plist','*/Library/Caches/locationd/clients.plist','*/Library/Preferences/com.apple.routined.plist'),
        get_locServicesconfig)
}