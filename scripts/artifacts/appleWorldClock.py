__artifacts_v2__ = {
    "worldclock": {
        "name": "WorldClock",
        "description": "Extraction of different World Clock entries",
        "author": "Mohammad Natiq Khan",
        "creation_date": "2025-02-23",
        "last_update_date": "2025-10-09",
        "requirements": "none",
        "category": "Clock",
        "notes": "",
        "paths": ('*/mobile/Library/Preferences/com.apple.mobiletimer.plist',),
        "output_types": "all",
        "artifact_icon": "clock",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 2 rows",
            "dexter_ios18": "iOS 18.3.2 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 3 rows",
            "iphone11_ios17": "iOS 17.3 | 4 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 2 rows",
            "abe_ios16": "iOS 16.5 | 2 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 2 rows",
            "hickman_ios14": "iOS 14.3 | 2 rows",
            "jess_ios15": "iOS 15.0.2 | 2 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content

@artifact_processor
def worldclock(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "com.apple.mobiletimer.plist")
    data_list = []

    pl = get_plist_file_content(source_path)
    if not pl or not isinstance(pl, dict):
        return (), [], ''
    
    if 'cities' in pl:
        for city in pl['cities']:
            country_dict = city.get('city')

            country_code = country_dict.get('identifier', '')
            country_name = country_dict.get('unlocalizedCountryName', '')
            country_localeCode = country_dict.get('localeCode', '')
            country_localName = country_dict.get('unlocalizedName', '')
            country_timezone = country_dict.get('timeZone', '')
            country_longitude = country_dict.get('longitude', '')
            country_latitude = country_dict.get('latitude', '')
            country_yahooCode = country_dict.get('yahooCode', '')

            data_list.append(( 
                country_code,
                country_name, 
                country_localeCode,
                country_localName,
                country_timezone,
                country_latitude,
                country_longitude,
                country_yahooCode
                ))

    data_headers = (
            'ISO Code',
            'Country Name', 
            'Country Code', 
            'City', 
            'Timezone', 
            'Latitude', 
            'Longitude',
            'Yahoo Code'
            )

    return data_headers, data_list, source_path
