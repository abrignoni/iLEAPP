__artifacts_v2__ = {
    "get_uber_account": {
        "name": "Uber - Account",
        "description": "Parses Uber user account information (Client, City, Status).",
        "author": "Django Faiola",
        "creation_date": "2024-05-30",
        "last_update_date": "2025-11-21",
        "requirements": "none",
        "category": "Uber",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "standard",
        "artifact_icon": "user"
    },
    "get_uber_vehicles": {
        "name": "Uber - Nearby Vehicles",
        "description": "Parses nearby vehicles data from Eyeball cache.",
        "author": "Django Faiola",
        "creation_date": "2024-05-30",
        "last_update_date": "2025-11-21",
        "requirements": "none",
        "category": "Uber",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "standard",
        "artifact_icon": "truck"
    },
    "get_uber_user_address": {
        "name": "Uber - User Address",
        "description": "Parses user reverse geocode address from Eyeball cache.",
        "author": "Django Faiola",
        "creation_date": "2024-05-30",
        "last_update_date": "2025-11-21",
        "requirements": "none",
        "category": "Uber",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "standard",
        "artifact_icon": "map-pin"
    },
    "get_uber_payment_profiles": {
        "name": "Uber - Payment Profiles",
        "description": "Parses Uber payment methods and profiles.",
        "author": "Django Faiola",
        "creation_date": "2024-05-30",
        "last_update_date": "2025-11-21",
        "requirements": "none",
        "category": "Uber",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "standard",
        "artifact_icon": "credit-card"
    },
    "get_uber_searched_rides": {
        "name": "Uber - Searched Rides",
        "description": "Parses searched rides history from database.db.",
        "author": "Django Faiola",
        "creation_date": "2024-05-30",
        "last_update_date": "2025-11-21",
        "requirements": "none",
        "category": "Uber",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "standard",
        "artifact_icon": "search"
    },
    "get_uber_cached_locations": {
        "name": "Uber - Cached Locations",
        "description": "Parses cached locations from database.db.",
        "author": "Django Faiola",
        "creation_date": "2024-05-30",
        "last_update_date": "2025-11-21",
        "requirements": "none",
        "category": "Uber",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "standard",
        "artifact_icon": "map"
    },
    "get_uber_ur_locations": {
        "name": "Uber - Unified Reporter Locations",
        "description": "Parses location data from ur_message.db.",
        "author": "Django Faiola",
        "creation_date": "2024-05-30",
        "last_update_date": "2025-11-21",
        "requirements": "none",
        "category": "Uber",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "standard",
        "artifact_icon": "navigation"
    },
    "get_uber_metadata_leveldb": {
        "name": "Uber - Metadata LevelDB",
        "description": "Parses LevelDB metadata for locations.",
        "author": "Django Faiola",
        "creation_date": "2024-05-30",
        "last_update_date": "2025-11-21",
        "requirements": "none",
        "category": "Uber",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "standard",
        "artifact_icon": "database"
    }
}

import os
import json
import pathlib
import scripts.ccl_leveldb

from scripts.ilapfuncs import (
    logfunc,
    artifact_processor,
    get_file_path,
    get_sqlite_db_records,
    convert_unix_ts_to_utc,
    get_plist_content,
    convert_cocoa_core_data_ts_to_utc
)

# --- Helper Functions ---
def FormatLocation(location, values, item, key, 
                   sep_split : str = chr(29), sep_item = ' ', sep_key = ': ', sep_val = ', ', sep_items = '; ', 
                   group_kv = True, brackets = '()') -> str:
    newLocation = ''
    str_values = str(values)
    str_item = str(item)
    if bool(str_values):
        if str_item.startswith('\\\\?\\'):
            str_item = str_item[4:]
        str_values = str_values.split(sep_split)
        for elem in range(0, len(str_values)):
            if bool(str_values[elem]) and (str_values[elem].lower() != 'none'):
                if len(newLocation) > 0:
                    newLocation += sep_val
                if len(key) > 0 and group_kv:
                    newLocation += brackets[0] + key + sep_key + str_values[elem] + brackets[1]
                elif len(key) > 0:
                    newLocation += key + brackets[0] + str_values[elem] + brackets[1]
                else:
                    newLocation += brackets[0] + str_values[elem] + brackets[1]
    if len(newLocation) > 0:
        if bool(item) > 0:
            newLocation = str_item + sep_item + newLocation
        if len(location) > 0:
            newLocation = sep_items + newLocation
    return location + newLocation


@artifact_processor
def get_uber_account(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, '*client')

    if not source_path:
        return (), [], ''

    data_list = []
    row = [None] * 17

    # 1. Process 'client' file
    try:
        with open(source_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            if json_data:
                row[0] = json_data.get('firstName')
                row[1] = json_data.get('lastName')
                row[2] = json_data.get('mobileDigits')
                row[3] = json_data.get('email')
                row[4] = json_data.get('referralCode')
                row[5] = json_data.get('pictureUrl')
                row[6] = json_data.get('profileType')
                row[7] = json_data.get('mobileCountryIso2')
                row[15] = json_data.get('lastSelectedPaymentProfileUUID')
                row[16] = json_data.get('uuid')
    except Exception as e:
        logfunc(f'Error reading Uber client file: {e}')

    # 2. Process sibling files 'city', 'clientStatus', 'targetLocationSynced'
    base_dir = os.path.dirname(source_path)

    # City
    try:
        with open(os.path.join(base_dir, '*city'), 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            if json_data:
                row[8] = json_data.get('cityId')
                row[9] = json_data.get('cityName')
                row[10] = json_data.get('currencyCode')
                row[11] = json_data.get('timezone')
    except: pass # Ignore errors if file doesn't exist

    # ClientStatus (Timestamp)
    try:
        with open(os.path.join(base_dir, 'clientStatus'), 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            meta = json_data.get('meta')
            if meta:
                ts_ms = meta.get('lastModifiedTimeMs')
                if ts_ms:
                    row[12] = convert_unix_ts_to_utc(int(ts_ms))
    except: pass

    # TargetLocationSynced
    try:
        with open(os.path.join(base_dir, '*targetLocationSynced'), 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            if json_data:
                row[13] = json_data.get('latitude')
                row[14] = json_data.get('longitude')
    except: pass

    if any(row):
        data_list.append(tuple(row))

    data_headers = (
        'First name', 'Last name', 'Mobile phone', 'Email', 'Share code', 'Profile picture url', 'Profile type',
        'Country code', 'City ID', 'City', 'Currency code', 'Timezone', ('Last used', 'datetime'),
        'Latitude (startup)', 'Longitude (startup)', 'Last payment profile ID', 'User ID'
    )

    return data_headers, data_list, source_path


@artifact_processor
def get_uber_vehicles(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, '*eyeball')

    if not source_path:
        return (), [], ''

    data_list = []
    try:
        with open(source_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            nearby_vehicles = json_data.get('nearbyVehicles', {})

            for v, vehicle in nearby_vehicles.items():
                if not isinstance(vehicle, dict): continue

                vehicle_paths = vehicle.get('vehiclePaths', {})
                for vp, vehicle_path in vehicle_paths.items():
                    for j, item in enumerate(vehicle_path):
                        ts_ms = item.get('epoch')
                        timestamp = convert_unix_ts_to_utc(int(ts_ms)) if ts_ms else ''

                        location = f'[nearbyVehicles][{v}][vehiclePaths][{vp}][{j}]'

                        data_list.append((
                            timestamp, 
                            item.get('latitude'),
                            item.get('longitude'),
                            item.get('course'),
                            location
                        ))
    except Exception as e:
        logfunc(f'Error parsing Uber vehicles: {e}')

    data_headers = (('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Course', 'Location')
    return data_headers, data_list, source_path


@artifact_processor
def get_uber_user_address(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, '*eyeball')

    if not source_path:
        return (), [], ''

    data_list = []
    try:
        with open(source_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            reverse_geocode = json_data.get('reverseGeocode')
            if reverse_geocode:
                location = f'[reverseGeocode]'
                data_list.append((
                    reverse_geocode.get('latitude'),
                    reverse_geocode.get('longitude'),
                    reverse_geocode.get('longAddress'),
                    reverse_geocode.get('uuid'),
                    location
                ))
    except Exception as e:
        logfunc(f'Error parsing Uber user address: {e}')

    data_headers = ('Latitude', 'Longitude', 'Address', 'ID', 'Location')
    return data_headers, data_list, source_path


@artifact_processor
def get_uber_payment_profiles(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, '*profiles')

    if not source_path:
        return (), [], ''

    data_list = []
    try:
        with open(source_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            if isinstance(json_data, list):
                for i, item in enumerate(json_data):
                    exp_epoch = item.get('cardExpirationEpoch')
                    expires = convert_unix_ts_to_utc(int(exp_epoch)) if exp_epoch else ''

                    location = f'[{i}]'
                    data_list.append((
                        item.get('cardType'),
                        item.get('accountName'),
                        item.get('cardBin'),
                        item.get('cardNumber'),
                        item.get('cardCategory'),
                        expires,
                        item.get('status'),
                        item.get('useCase'),
                        item.get('billingCountryIso2'),
                        item.get('uuid'),
                        location
                    ))
    except Exception as e:
        logfunc(f'Error parsing Uber payment profiles: {e}')

    data_headers = ('Card type', 'Account name', 'Card BIN', 'Number', 'Category', ('Expires', 'datetime'), 'Status', 'Using type', 'Country code', 'ID', 'Location')
    return data_headers, data_list, source_path


@artifact_processor
def get_uber_searched_rides(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, '*database.db')

    if not source_path:
        return (), [], ''

    query = '''
        SELECT
            h._id AS "h_id",
            p._id AS "p_id",
            h.timestamp_ms AS "timestamp",
            p.tag,
            p.title_segment AS "destTitle",
            p.subtitle_segment AS "destAddr",
            coalesce(p.latitude, p.latitude_v2, "") AS "destLat",
            coalesce(p.longitude, p.longitude_v2, "") AS "destLng"
        FROM hits AS "h"
        LEFT JOIN place AS "p" ON (h.fk_place_row_id = p._id)
    '''

    db_records = get_sqlite_db_records(source_path, query)
    data_list = []
    for row in db_records:
        ts = convert_unix_ts_to_utc(int(row[2]) / 1000) if row[2] else ''

        location = FormatLocation('', row[0], 'hits', '_id')
        location = FormatLocation(location, row[1], 'place', '_id')

        data_list.append((ts, row[3], row[4], row[5], row[6], row[7], location))

    data_headers = (('Timestamp', 'datetime'), 'Tag', 'Title', 'Address', 'Latitude', 'Longitude', 'Location')
    return data_headers, data_list, source_path

# --- Artefacto 6: Cached Locations ---
@artifact_processor
def get_uber_cached_locations(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, '*database.db')

    if not source_path:
        return (), [], ''

    query = '''
        SELECT
            p._id AS "p_id",
            p.timestamp_ms AS "lastHit",
            json_extract(p.place_result, '$.payload.personalPayload.labelType') AS "type",
            p.tag,
            json_extract(p.place_result, '$.location.addressLine1') AS "name",
            json_extract(p.place_result, '$.location.fullAddress') AS "address",
            coalesce(p.latitude, p.latitude_v2, "") AS "lat",
            coalesce(p.longitude, p.longitude_v2, "") AS "lng",
            (SELECT group_concat(json_each.value, ', ') FROM json_each(json_extract(p.place_result, '$.location.categories'))) AS "categories",
            p.uber_id
        FROM place AS "p"
    '''

    db_records = get_sqlite_db_records(source_path, query)
    data_list = []

    for row in db_records:
        ts = convert_unix_ts_to_utc(int(row[1]) / 1000) if row[1] else ''
        location = FormatLocation('', row[0], 'place', '_id')

        data_list.append((ts, row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], location))

    data_headers = (('Last hit', 'datetime'), 'Type', 'Tag', 'Name', 'Address', 'Latitude', 'Longitude', 'Categories', 'Uber ID', 'Location') 
    return data_headers, data_list, source_path


@artifact_processor
def get_uber_ur_locations(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, '*ur_message.db')

    if not source_path:
        return (), [], ''

    query = '''
        SELECT
            m.auto_row_id,
            (json_extract(m.content, '$.jsonConformingObject.meta.time_ms')) AS "timestamp",
            m.message_type AS "messageType",
            (json_extract(m.content, '$.jsonConformingObject.meta.location.gps_time_ms') ) AS "gpsTime",
            json_extract(m.content, '$.jsonConformingObject.meta.location.city') AS "city",
            json_extract(m.content, '$.jsonConformingObject.meta.location.latitude') AS "lat",
            json_extract(m.content, '$.jsonConformingObject.meta.location.longitude') AS "lng",
            json_extract(m.content, '$.jsonConformingObject.meta.location.horizontal_accuracy') AS "accuracy",
            json_extract(m.content, '$.jsonConformingObject.meta.location.speed') AS "speed",
            json_extract(m.content, '$.jsonConformingObject.data.name') AS "name",
            (json_extract(m.content, '$.jsonConformingObject.data.ui_state.timestamp_ms')) AS "uiTimestamp",
            json_extract(m.content, '$.jsonConformingObject.data.ui_state.metadata') AS "uiMetadata",
            json_extract(m.content, '$.jsonConformingObject.data.ui_state.scene') AS "uiScene",
            json_extract(m.content, '$.jsonConformingObject.data.app_type_value_map') AS "appTypeValueMap",
            json_extract(m.content, '$.jsonConformingObject.data.active_trips') AS "actTrips"
        FROM message AS "m"        
    '''

    db_records = get_sqlite_db_records(source_path, query)
    data_list = []

    for row in db_records:

        timestamp = convert_unix_ts_to_utc(row[1])
        gps_timestamp = convert_unix_ts_to_utc(row[3])
        ui_timestamp = convert_unix_ts_to_utc(row[10])
        location = FormatLocation('', row[0], 'message', 'auto_row_id')

        data_list.append((
            timestamp, row[2], gps_timestamp, row[4], row[5], row[6], row[7], row[8], row[9],
            ui_timestamp, row[11], row[12], row[13], row[14], location
        ))

    data_headers = (
        ('Timestamp', 'datetime'), 'Type', ('GPS timestamp', 'datetime'), 'City', 'Latitude', 'Longitude', 'Horizontal acc.', 'Speed', 'Object name',
        ('UI Timestamp', 'datetime'), 'Metadata', 'Scene', 'App type value map','Active trips', 'Location'
    )
    return data_headers, data_list, source_path


@artifact_processor
def get_uber_metadata_leveldb(context):
    files_found = context.get_files_found()
    data_list = []

    ldb_dirs = set()
    for f in files_found:
        if '__METADATA' in str(f):
            ldb_dirs.add(os.path.dirname(str(f)))

    source_path = ', '.join(list(ldb_dirs))

    for ldb_path in ldb_dirs:
        try:
            leveldb_records = scripts.ccl_leveldb.RawLevelDb(ldb_path)
            for record in leveldb_records.iterate_records_raw():
                if record.user_key.decode() == 'UBLocationNode.__DEFAULT_INDEX':
                    try:
                        plist = get_plist_content(record.value)

                        sample = plist.get('_sample', {})
                        loc = sample.get('_location', {})

                        if loc:
                            ts = loc.get('kCLLocationCodingKeyTimestamp')
                            timestamp = convert_cocoa_core_data_ts_to_utc(ts) if ts else ''

                            origin = f'{os.path.basename(str(record.origin_file))} (seq: {record.seq})'

                            data_list.append((
                                timestamp,
                                loc.get('kCLLocationCodingKeyCoordinateLatitude'),
                                loc.get('kCLLocationCodingKeyCoordinateLongitude'),
                                loc.get('kCLLocationCodingKeyHorizontalAccuracy'),
                                loc.get('kCLLocationCodingKeyAltitude'),
                                loc.get('kCLLocationCodingKeyVerticalAccuracy'),
                                loc.get('kCLLocationCodingKeyCourse'),
                                loc.get('kCLLocationCodingKeySpeed'),
                                record.state.name,
                                origin
                            ))
                    except Exception:
                        pass
        except Exception as e:
            logfunc(f"Error reading LevelDB at {ldb_path}: {e}")

    data_headers = (
        ('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Horizontal acc.',
        'Altitude', 'Vertical acc.', 'Course', 'Speed', 'State', 'Location'
    )

    return data_headers, data_list, source_path
