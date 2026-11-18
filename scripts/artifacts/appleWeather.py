__artifacts_v2__ = {
    "weatherFetchHistory": {
        "name": "Weather - Fetch History",
        "description": "Rows of the lastFetch table in the Weather app's weather-data.db: the "
                       "time, the latitude and longitude and the data products of each fetch.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Weather",
        "notes": "No Apple documentation of the Weather app's stores was found, so the table and "
                 "key names are the only labels used here and values are reported as stored. One "
                 "row per row of lastFetch. Fetch Time is timestamp read as seconds since 1970 "
                 "UTC; read that way it falls between March or April and October 2026 on the two "
                 "iOS 26 images, and no source for the epoch was found. Latitude and Longitude are "
                 "stored with three decimal places (about 110 metres). Every row on "
                 "hill_iphone15pro_ios26 (156) and wilkerson_iphone16_ios26 (817) holds a "
                 "different coordinate pair, so the table is not a list of a few saved places; "
                 "whether each pair is the device's position when the fetch was made is not "
                 "established. Products lists the data sets fetched, as stored. iphone11_ios17 "
                 "(iOS 17.3) has weather-data.db without a lastFetch table. The other tables of "
                 "weather-data.db (forecasts, air quality, alerts, news and metadata, with their "
                 "own coordinates) are not read here.",
        "paths": ('*/mobile/Library/Weather/weather-data.db*',),
        "output_types": "all",
        "artifact_icon": "cloud",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 156 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 817 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows, no lastFetch table",
        },
    },
    "weatherCurrentLocation": {
        "name": "Weather - Current Location",
        "description": "The current location records in the Weather app's current-location.db: "
                       "the raw coordinate and its date, and the geocoded name, time zone and "
                       "refresh date.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Weather",
        "notes": "No Apple documentation of the Weather app's stores was found, so the table and "
                 "key names are the only labels used here and values are reported as stored. One "
                 "row per row of currentLocationRaw and of currentLocationGeocoded, named in "
                 "Table. Date is the date column read as seconds since 1970 UTC. Last Refresh Date "
                 "is the geocoded record's lastRefreshDate read as seconds since 2001 UTC: on "
                 "wilkerson_iphone16_ios26 that reading equals the row's Date to the second, and "
                 "read as seconds since 1970 it would fall in 1995. Each tested image holds one "
                 "row in each table.",
        "paths": ('*/mobile/Library/Weather/current-location.db*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 2 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
        },
    },
    "weatherReverseGeocodes": {
        "name": "Weather - Reverse Geocode Results",
        "description": "Rows of the reverseGeocodeResult table in the Weather app's "
                       "geocode_wk.db: the stored key, the place name, country code and time "
                       "zone, and the expiry time.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Weather",
        "notes": "No Apple documentation of the Weather app's stores was found, so the table and "
                 "key names are the only labels used here and values are reported as stored. One "
                 "row per row of reverseGeocodeResult. Key is the id column as stored, which holds "
                 "rounded coordinates and a locale on the tested images. Expires is expires read "
                 "as seconds since 1970 UTC; what expires is not established. Name, Country Code "
                 "and Time Zone come from the reverseGeocodeResult JSON. hill_iphone15pro_ios26 "
                 "holds 38 rows (9 names), wilkerson_iphone16_ios26 21 (7 names) and "
                 "iphone11_ios17 4. Country Code and Configured Country Code held US on every row "
                 "of wilkerson_iphone16_ios26 and iphone11_ios17, and Time Zone held one value on "
                 "every row of iphone11_ios17. geocode.db, which holds geocoded locations with a "
                 "time zone, and notifications.db are not read here.",
        "paths": ('*/mobile/Library/Weather/geocode_wk.db*',),
        "output_types": "standard",
        "artifact_icon": "map",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 38 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 21 rows",
            "iphone11_ios17": "iOS 17.3 | 4 rows",
        },
    },
}


import json
import os
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import (artifact_processor, does_table_exist_in_db, get_sqlite_db_records,
                               is_sqlite_sidecar, logfunc)

_EPOCH_2001 = datetime(2001, 1, 1, tzinfo=timezone.utc)


def _unix(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        return ''
    try:
        return datetime.fromtimestamp(value, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _cocoa(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        return ''
    try:
        return _EPOCH_2001 + timedelta(seconds=value)
    except OverflowError:
        return ''


def _json(value, label):
    if value is None:
        return {}
    try:
        parsed = json.loads(value)
    except (ValueError, TypeError, UnicodeDecodeError) as error:
        logfunc(f'Weather: could not read a {label} value: {error}')
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _store(context, name, table):
    for found in sorted(str(path) for path in context.get_files_found()):
        if os.path.basename(found) == name and not is_sqlite_sidecar(found):
            if does_table_exist_in_db(found, table):
                yield found


def _text(value):
    return '' if value is None else str(value)


@artifact_processor
def weatherFetchHistory(context):
    data_list, sources = [], []
    for found in _store(context, 'weather-data.db', 'lastFetch'):
        sources.append(found)
        for row in get_sqlite_db_records(
                found, 'SELECT timestamp, latitude, longitude, products, id FROM lastFetch '
                       'ORDER BY timestamp'):
            data_list.append((_unix(row[0]), row[1], row[2], _text(row[3]), _text(row[4])))
    headers = (('Fetch Time', 'datetime'), ('Latitude', 'latitude'), ('Longitude', 'longitude'),
               'Products', 'ID')
    return headers, data_list, '\n'.join(sources)


@artifact_processor
def weatherCurrentLocation(context):
    data_list, sources = [], []
    for found in _store(context, 'current-location.db', 'currentLocationRaw'):
        sources.append(found)
        for row in get_sqlite_db_records(found, 'SELECT id, coordinate, date FROM currentLocationRaw'):
            coordinate = _json(row[1], 'coordinate')
            data_list.append((_unix(row[2]), '', 'currentLocationRaw', coordinate.get('latitude', ''),
                              coordinate.get('longitude', ''), '', '', '', _text(row[0])))
        if does_table_exist_in_db(found, 'currentLocationGeocoded'):
            for row in get_sqlite_db_records(
                    found, 'SELECT id, location, date FROM currentLocationGeocoded'):
                location = _json(row[1], 'location')
                coordinate = location.get('coordinate') if isinstance(location.get('coordinate'), dict) else {}
                zone = location.get('timeZone') if isinstance(location.get('timeZone'), dict) else {}
                data_list.append((_unix(row[2]), _cocoa(location.get('lastRefreshDate')),
                                  'currentLocationGeocoded', coordinate.get('latitude', ''),
                                  coordinate.get('longitude', ''), _text(location.get('name')),
                                  _text(location.get('preciseName')), _text(zone.get('identifier')),
                                  _text(row[0])))
    headers = (('Date', 'datetime'), ('Last Refresh Date', 'datetime'), 'Table',
               ('Latitude', 'latitude'), ('Longitude', 'longitude'), 'Name', 'Precise Name',
               'Time Zone', 'ID')
    return headers, data_list, '\n'.join(sources)


@artifact_processor
def weatherReverseGeocodes(context):
    data_list, sources = [], []
    for found in _store(context, 'geocode_wk.db', 'reverseGeocodeResult'):
        sources.append(found)
        for row in get_sqlite_db_records(
                found, 'SELECT id, expires, reverseGeocodeResult, configuredCountryCode '
                       'FROM reverseGeocodeResult ORDER BY expires'):
            result = _json(row[2], 'reverse geocode')
            zone = result.get('timeZone') if isinstance(result.get('timeZone'), dict) else {}
            data_list.append((_unix(row[1]), _text(row[0]), _text(result.get('name')),
                              _text(result.get('countryCode')), _text(zone.get('identifier')),
                              _text(row[3])))
    headers = (('Expires', 'datetime'), 'Key (as stored)', 'Name', 'Country Code', 'Time Zone',
               'Configured Country Code')
    return headers, data_list, '\n'.join(sources)
