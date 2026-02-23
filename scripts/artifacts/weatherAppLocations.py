import plistlib
import time
import datetime

from scripts.ilapfuncs import logfunc, artifact_processor


@artifact_processor
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
                return (), [], ''

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
                return (), [], ''
              
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
        data_headers = ("Update Time", "Type", "Last Location Update", "Latitude", "Longitude", "City", "Country", "Seconds from GMT")
        return data_headers, data_list, file_found
    elif len(data_list_two_one) > 0:
        data_headers = ("Update Time", "Name", "Country", "TimeZone", "City Timezone Update Key", "Latitude", "Longitude")
        return data_headers, data_list_two_one, file_found
    return (), [], ''

__artifacts_v2__ = {
    "get_weatherAppLocations": {
        "name": "Weather App Locations",
        "description": "",
        "author": "",
        "version": "0.2",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Location",
        "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/Library/Preferences/group.com.apple.weather.plist'),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}