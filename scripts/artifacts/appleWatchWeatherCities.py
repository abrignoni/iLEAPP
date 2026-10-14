""" Apple Watch weather cities: com.apple.nanoweatherprefs.plist """
__artifacts_v2__ = {
    "appleWatchWeatherCities": {
        "name": "Apple Watch Weather Cities",
        "description": "One row per entry in the Cities list of com.apple.nanoweatherprefs.plist, "
                       "with its name, country abbreviation and stored coordinates.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-10",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "Apple Watch",
        "notes": "Position is the 1-based place of the city in the Cities list, as stored. Name, "
                 "Country Abbreviation, Latitude, Longitude, Time Zone and UUID are the city's "
                 "Name, CountryAbbreviation, Lat, Lon, TimeZone and UUID, as stored; on the 13 "
                 "cities seen the UUID was text of the form number,number and not a UUID. File "
                 "Last Updated is the file's LastUpdated and is the same on every row from one "
                 "file. Time Zone Last Updated is the city's TimeZoneLastUpdated. Both dates are "
                 "shown to the second, in UTC. On iphone11_ios17 all 4 cities hold a "
                 "TimeZoneLastUpdated at the year 1 boundary, which Python cannot represent; the "
                 "plist reader drops those values, the column is empty for them and the log says "
                 "how many were dropped. Time Zone Last Updated is shown on 7 of the 13 cities; "
                 "the key is stored on 11, and the other 4 are the dropped year 1 values. Time "
                 "Zone had a value on 11. Other Keys lists any key without a column of its own "
                 "as key=value and had no value on these cities. What adds a city to the list is "
                 "not established, and the file does not say the device was at those "
                 "coordinates. The file was on 4 of the 23 sample_data images (cookbook_ios1751 "
                 "with 2 cities, hickman_ios13 with 3, hickman_ios14 and iphone11_ios17 with 4 "
                 "each). The other 19 have no com.apple.nanoweatherprefs.plist under "
                 "mobile/Library/Preferences. Suggested in issue #1876.",
        "paths": ('*/mobile/Library/Preferences/com.apple.nanoweatherprefs.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cloud",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 3 rows",
            "hickman_ios14": "iOS 14.3 | 4 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 4 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
}

from datetime import datetime

from scripts.ilapfuncs import (artifact_processor, convert_plist_date_to_utc, get_file_path,
                               get_plist_file_content, logfunc)

# Keys of a city that get a column of their own.
_CITY_COLUMNS = ('Name', 'CountryAbbreviation', 'Lat', 'Lon', 'TimeZone', 'UUID')


def _date(value):
    return convert_plist_date_to_utc(value) if isinstance(value, datetime) else ''


def _text(value):
    return '' if value is None else str(value)


@artifact_processor
def appleWatchWeatherCities(context):
    """ See artifact description """
    data_headers = (('File Last Updated', 'datetime'), ('Time Zone Last Updated', 'datetime'),
                    'Position', 'Name', 'Country Abbreviation', 'Latitude', 'Longitude',
                    'Time Zone', 'UUID', 'Other Keys')
    data_list = []
    source_path = get_file_path(context.get_files_found(), 'com.apple.nanoweatherprefs.plist')
    if not source_path:
        return data_headers, data_list, ''

    plist = get_plist_file_content(source_path)
    if not isinstance(plist, dict):
        logfunc(f'{source_path} did not read as a plist dictionary')
        return data_headers, data_list, source_path
    cities = plist.get('Cities')
    if not isinstance(cities, list):
        logfunc(f'{source_path} holds no Cities list')
        return data_headers, data_list, source_path

    last_updated = _date(plist.get('LastUpdated'))
    for position, city in enumerate(cities, start=1):
        if not isinstance(city, dict):
            logfunc(f'{source_path}: city {position} is not a dictionary and was not reported')
            continue
        shown = set(_CITY_COLUMNS)
        zone_updated = city.get('TimeZoneLastUpdated')
        if zone_updated is None or isinstance(zone_updated, datetime):
            shown.add('TimeZoneLastUpdated')
        other = '; '.join(f'{key}={city[key]}' for key in sorted(city, key=str)
                          if key not in shown)
        data_list.append((last_updated, _date(zone_updated), position)
                         + tuple(_text(city.get(key)) for key in _CITY_COLUMNS) + (other,))
    return data_headers, data_list, source_path
