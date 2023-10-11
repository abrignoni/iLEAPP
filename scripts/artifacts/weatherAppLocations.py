import plistlib
import time
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, kmlgen, timeline, is_platform_windows


def get_weatherAppLocations(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    data_list_two_one = []
    for file_found in files_found:
        file_found = str(file_found)
        with open(file_found, "rb") as plist_file:
            plist_content = plistlib.load(plist_file)
            
          
            if plist_content.get('PrefsVersion') == '2.1':
              lastupdated = (plist_content['LastUpdated'])
              
              if plist_content.get('Cities', '0') == '0':
                logfunc('No cities available')
                return

              for x in plist_content['Cities']:
                lon = x.get('Lon','')
                lat = x.get('Lat','')
                name = x.get('Name','')
                country = x.get('Country','')
                timezone = x.get('TimeZone','')
                cityupdate = x.get('CityTimeZoneUpdateDateKey','')
                
                data_list_two_one.append((lastupdated, name, country, timezone, cityupdate, lat, lon))
            else:
              if plist_content.get('Cities', '0') == '0':
                logfunc('No cities available')
                return
              
              for city in plist_content['Cities']:
                  update_time = city.get('UpateTime','')
                  update_time_formatted = update_time.strftime('%Y-%m-%d %H:%M:%S')
  
                  data_list.append((update_time_formatted, 'Added from User', '', city['Lat'],
                                    city['Lon'], city['Name'], city['Country'], city['SecondsFromGMT']))
  
              local_weather = plist_content['LocalWeather']
              local_update_time = local_weather['UpateTime']
              local_update_time_formatted = local_update_time.strftime('%Y-%m-%d %H:%M:%S')
              last_location_update = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(plist_content.get('LastLocationUpdateTime')))
  
              data_list.append((local_update_time_formatted, 'Local', last_location_update, local_weather['Lat'],
                                local_weather['Lon'], local_weather['Name'], local_weather['Country'], local_weather['SecondsFromGMT']))

    if len(data_list) > 0:
        report = ArtifactHtmlReport('Weather App Locations')
        report.start_artifact_report(report_folder, 'Weather App Locations')
        report.add_script()
        data_headers = ("Update Time", "Type", "Last Location Update", "Latitude", "Longitude", "City", "Country", "Seconds from GMT")
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'Weather App Locations'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Weather App Locations'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
        kmlactivity = 'Weather App Locations'
        kmlgen(report_folder, kmlactivity, data_list, data_headers)

    elif len(data_list_two_one) > 0:
        report = ArtifactHtmlReport('Weather App Locations')
        report.start_artifact_report(report_folder, 'Weather App Locations')
        report.add_script()
        data_headers = ("Update Time", "Name", "Country", "TimeZone", "City Timezone Update Key","Latitude", "Longitude")
        report.write_artifact_data_table(data_headers, data_list_two_one, file_found)
        report.end_artifact_report()
      
        tsvname = 'Weather App Locations'
        tsv(report_folder, data_headers, data_list_two_one, tsvname)
      
        tlactivity = 'Weather App Locations'
        timeline(report_folder, tlactivity, data_list_two_one, data_headers)
      
        kmlactivity = 'Weather App Locations'
        kmlgen(report_folder, kmlactivity, data_list_two_one, data_headers)
    else:
        logfunc('No data available for Weather App Locations')

__artifacts__ = {
    "weatherAppLocations": (
        "Locations",
        ('*/mobile/Containers/Shared/AppGroup/*/Library/Preferences/group.com.apple.weather.plist'),
        get_weatherAppLocations)
}