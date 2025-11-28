__artifacts_v2__ = {
    "get_weatherAppLocations": {
        "name": "Weather App - Location",
        "description": "",
        "author": "@Anna-Mariya Mateyna",
        "creation_date": "2021-01-29",
        "last_update_date": "2025-11-20",
        "requirements": "none",
        "category": "Location",
        "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/Library/Preferences/group.com.apple.weather.plist',),
        "output_types": "standard",
        "artifact_icon": "sun"
    }
}
from scripts.ilapfuncs import (
    logfunc,
    artifact_processor,
    get_plist_file_content,
    get_file_path,
    convert_unix_ts_to_utc,
    convert_plist_date_to_utc
    )


@artifact_processor
def get_weatherAppLocations(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = get_file_path(files_found, 'group.com.apple.weather.plist')
    if not source_path:
        logfunc('No weather app location plist found')
        return (), [], ''
    plist_content = get_plist_file_content(source_path)
    if plist_content.get('PrefsVersion') == '2.1':
        data_headers = (
                    ('Update Time', 'datetime'),
                    'Name',
                    'Country',
                    'TimeZone',
                    ('City Timezone Update Key', 'datetime'),
                    'Latitude',
                    'Longitude',
                )

        lastupdated = convert_plist_date_to_utc(plist_content.get('LastUpdated'))
        if plist_content.get('Cities', '0') == '0':
            logfunc('No cities available')
            return

        for x in plist_content['Cities']:
            lon = x.get('Lon', '')
            lat = x.get('Lat', '')
            name = x.get('Name', '')
            country = x.get('Country', '')
            timezone = x.get('TimeZone', '')
            cityupdate = convert_unix_ts_to_utc(x.get('CityTimeZoneUpdateDateKey', ''))
            data_list.append((
                lastupdated,
                name,
                country,
                timezone,
                cityupdate,
                lat,
                lon
                ))
    else:
        data_headers = (
            ('Update Time', 'datetime'),
            'Type',
            ('Last Location Update', 'datetime'),
            'Latitude',
            'Longitude',
            'City',
            'Country',
            'Seconds from GMT',
            )
        if plist_content.get('Cities', '0') == '0':
            logfunc('No cities available')
            return
        for city in plist_content['Cities']:
            update_time = convert_plist_date_to_utc(city.get('UpateTime', ''))
            data_list.append((
                update_time,
                'Added from User',
                '',
                city['Lat'],
                city['Lon'],
                city['Name'],
                city['Country'],
                city['SecondsFromGMT'],
                source_path
                ))
        local_weather = plist_content.get('LocalWeather', {})
        local_update_time = convert_plist_date_to_utc(local_weather.get('UpateTime', ''))
        last_location_update = convert_unix_ts_to_utc(plist_content.get('LastLocationUpdateTime'))
        data_list.append((
            local_update_time,
            'Local',
            last_location_update,
            local_weather['Lat'],
            local_weather['Lon'],
            local_weather['Name'],
            local_weather['Country'],
            local_weather['SecondsFromGMT'],
            ))

    if not data_list:
        logfunc('No weather app location data available')
        return (), [], source_path
    return data_headers, data_list, source_path
