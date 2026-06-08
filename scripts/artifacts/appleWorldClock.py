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
        "output_types": "standard",
        "artifact_icon": "clock"
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
