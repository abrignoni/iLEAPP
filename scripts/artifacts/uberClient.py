__artifacts_v2__ = {
    "uber_account": {
        "name": "Uber - Account",
        "description": "Parses Uber user account information (Client, City, Status).",
        "author": "Django Faiola",
        "creation_date": "2024-05-30",
        "last_update_date": "2025-11-21",
        "requirements": "none",
        "category": "Uber",
        "notes": "",
        "paths": (
            '*/Library/Application Support/PersistentStorage/BootstrapStore/RealtimeRider.StreamModelKey/client',
        ),
        "output_types": "standard",
        "artifact_icon": "user"
    },
    "uber_vehicles": {
        "name": "Uber - Nearby Vehicles",
        "description": "Parses nearby vehicles data from Eyeball cache.",
        "author": "Django Faiola",
        "creation_date": "2024-05-30",
        "last_update_date": "2025-11-21",
        "requirements": "none",
        "category": "Uber",
        "notes": "",
        "paths": (
            '*/Library/Application Support/PersistentStorage/BootstrapStore/RealtimeRider.StreamModelKey/eyeball',
        ),
        "output_types": "standard",
        "artifact_icon": "truck"
    },
    "uber_user_address": {
        "name": "Uber - User Address",
        "description": "Parses user reverse geocode address from Eyeball cache.",
        "author": "Django Faiola",
        "creation_date": "2024-05-30",
        "last_update_date": "2025-11-21",
        "requirements": "none",
        "category": "Uber",
        "notes": "",
        "paths": (
            '*/Library/Application Support/PersistentStorage/BootstrapStore/RealtimeRider.StreamModelKey/eyeball',
        ),
        "output_types": "standard",
        "artifact_icon": "map-pin"
    },
    "uber_payment_profiles": {
        "name": "Uber - Payment Profiles",
        "description": "Parses Uber payment methods and profiles.",
        "author": "Django Faiola",
        "creation_date": "2024-05-30",
        "last_update_date": "2025-11-21",
        "requirements": "none",
        "category": "Uber",
        "notes": "",
        "paths": (
            '*/Library/Application Support/PersistentStorage/Store/PaymentFoundation.PaymentStreamModelKey/profiles',
        ),
        "output_types": "standard",
        "artifact_icon": "credit-card"
    },
    "uber_searched_rides": {
        "name": "Uber - Searched Rides",
        "description": "Parses searched rides history from database.db.",
        "author": "Django Faiola",
        "creation_date": "2024-05-30",
        "last_update_date": "2025-11-21",
        "requirements": "none",
        "category": "Uber",
        "notes": "",
        "paths": ('*/Documents/database.db*',),
        "output_types": "standard",
        "artifact_icon": "search"
    },
    "uber_cached_locations": {
        "name": "Uber - Cached Locations",
        "description": "Parses cached locations from database.db.",
        "author": "Django Faiola",
        "creation_date": "2024-05-30",
        "last_update_date": "2025-11-21",
        "requirements": "none",
        "category": "Uber",
        "notes": "",
        "paths": ('*/Documents/database.db*',),
        "output_types": "standard",
        "artifact_icon": "map"
    },
    "uber_ur_locations": {
        "name": "Uber - Unified Reporter Locations",
        "description": "Parses location data from ur_message.db.",
        "author": "Django Faiola",
        "creation_date": "2024-05-30",
        "last_update_date": "2025-11-21",
        "requirements": "none",
        "category": "Uber",
        "notes": "",
        "paths": ('*/Documents/ur_message.db*',),
        "output_types": "standard",
        "artifact_icon": "navigation"
    },
    "uber_metadata_leveldb": {
        "name": "Uber - Metadata LevelDB",
        "description": "Parses LevelDB metadata for locations.",
        "author": "Django Faiola",
        "creation_date": "2024-05-30",
        "last_update_date": "2025-11-21",
        "requirements": "none",
        "category": "Uber",
        "notes": "",
        "paths": ('*/Library/Application Support/com.ubercab.UberClient/__METADATA/*.ldb',),
        "output_types": "standard",
        "artifact_icon": "database"
    }
}

import os
import json
import scripts.ccl_leveldb
from scripts.ilapfuncs import (
    logfunc,
    artifact_processor,
    get_file_path,
    get_sqlite_db_records,
    get_txt_file_content,
    convert_unix_ts_to_utc,
    get_plist_content,
    convert_cocoa_core_data_ts_to_utc,
    open_sqlite_db_readonly
)


def _load_json_file(file_path):
    try:
        file_content = get_txt_file_content(file_path)
        if not file_content:
            return None
        return json.loads(''.join(file_content))
    except json.JSONDecodeError as ex:
        logfunc(f'Error reading Uber JSON file {file_path}: {ex}')
        return None


def _first_sqlite_db_with_table(context, table_name):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('database.db'):
            continue

        db = open_sqlite_db_readonly(file_found)
        if not db:
            continue

        try:
            cursor = db.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            if cursor.fetchone():
                return file_found
        finally:
            db.close()

    return ''


# --- Helper Functions ---
def format_location(location, values, item, key,
                    sep_split: str = chr(29), sep_item=' ', sep_key=': ', sep_val=', ', sep_items='; ',
                    group_kv=True, brackets='()') -> str:
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
def uber_account(context):
    source_path = get_file_path(context.get_files_found(), '*client')

    if not source_path:
        return (), [], ''

    data_list = []
    row = [None] * 17

    json_data = _load_json_file(source_path)
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

    # 2. Process sibling files 'city', 'clientStatus', 'targetLocationSynced'
    base_dir = os.path.dirname(source_path)

    json_data = _load_json_file(os.path.join(base_dir, 'city'))
    if json_data:
        row[8] = json_data.get('cityId')
        row[9] = json_data.get('cityName')
        row[10] = json_data.get('currencyCode')
        row[11] = json_data.get('timezone')

    json_data = _load_json_file(os.path.join(base_dir, 'clientStatus'))
    if json_data:
        meta = json_data.get('meta')
        if meta:
            ts_ms = meta.get('lastModifiedTimeMs')
            if ts_ms:
                row[12] = convert_unix_ts_to_utc(ts_ms)

    json_data = _load_json_file(os.path.join(base_dir, 'targetLocationSynced'))
    if json_data:
        row[13] = json_data.get('latitude')
        row[14] = json_data.get('longitude')

    if any(row):
        data_list.append(tuple(row))

    data_headers = (
        'First name', 'Last name',
        ('Mobile phone', 'phonenumber'),
        'Email', 'Share code',
        'Profile picture url', 'Profile type',
        'Country code', 'City ID', 'City',
        'Currency code', 'Timezone',
        ('Last used', 'datetime'),
        'Latitude (startup)', 'Longitude (startup)',
        'Last payment profile ID', 'User ID'
    )

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def uber_vehicles(context):
    source_path = get_file_path(context.get_files_found(), '*eyeball')

    if not source_path:
        return (), [], ''

    data_list = []
    json_data = _load_json_file(source_path)
    if json_data:
        nearby_vehicles = json_data.get('nearbyVehicles', {})

        for v, vehicle in nearby_vehicles.items():
            if not isinstance(vehicle, dict):
                continue

            vehicle_paths = vehicle.get('vehiclePaths', {})
            for vp, vehicle_path in vehicle_paths.items():
                for j, item in enumerate(vehicle_path):
                    ts_ms = item.get('epoch')
                    timestamp = convert_unix_ts_to_utc(ts_ms) if ts_ms else ''

                    location = f'[nearbyVehicles][{v}][vehiclePaths][{vp}][{j}]'

                    data_list.append((
                        timestamp,
                        item.get('latitude'),
                        item.get('longitude'),
                        item.get('course'),
                        location
                    ))

    data_headers = (('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Course', 'Location')
    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def uber_user_address(context):
    source_path = get_file_path(context.get_files_found(), '*eyeball')

    if not source_path:
        return (), [], ''

    data_list = []
    json_data = _load_json_file(source_path)
    if json_data:
        reverse_geocode = json_data.get('reverseGeocode')
        if reverse_geocode:
            location = '[reverseGeocode]'
            data_list.append((
                reverse_geocode.get('latitude'),
                reverse_geocode.get('longitude'),
                reverse_geocode.get('longAddress'),
                reverse_geocode.get('uuid'),
                location
            ))

    data_headers = ('Latitude', 'Longitude', 'Address', 'ID', 'Location')
    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def uber_payment_profiles(context):
    source_path = get_file_path(context.get_files_found(), '*profiles')

    if not source_path:
        return (), [], ''

    data_list = []
    json_data = _load_json_file(source_path)
    if isinstance(json_data, list):
        for i, item in enumerate(json_data):
            exp_epoch = item.get('cardExpirationEpoch')
            expires = convert_unix_ts_to_utc(exp_epoch) if exp_epoch else ''

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

    data_headers = ('Card type', 'Account name', 'Card BIN', 'Number', 'Category', ('Expires', 'datetime'), 'Status', 'Using type', 'Country code', 'ID', 'Location')
    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def uber_searched_rides(context):
    source_path = _first_sqlite_db_with_table(context, 'hits')

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

        location = format_location('', row[0], 'hits', '_id')
        location = format_location(location, row[1], 'place', '_id')

        data_list.append((ts, row[3], row[4], row[5], row[6], row[7], location))

    data_headers = (('Timestamp', 'datetime'), 'Tag', 'Title', 'Address', 'Latitude', 'Longitude', 'Location')
    return data_headers, data_list, context.get_relative_path(source_path)

# --- Artefacto 6: Cached Locations ---
@artifact_processor
def uber_cached_locations(context):
    source_path = _first_sqlite_db_with_table(context, 'place')

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
        location = format_location('', row[0], 'place', '_id')

        data_list.append((ts, row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], location))

    data_headers = (('Last hit', 'datetime'), 'Type', 'Tag', 'Name', 'Address', 'Latitude', 'Longitude', 'Categories', 'Uber ID', 'Location')
    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def uber_ur_locations(context):
    source_path = get_file_path(context.get_files_found(), '*ur_message.db')

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
        location = format_location('', row[0], 'message', 'auto_row_id')

        data_list.append((
            timestamp, row[2], gps_timestamp, row[4], row[5], row[6], row[7], row[8], row[9],
            ui_timestamp, row[11], row[12], row[13], row[14], location
        ))

    data_headers = (
        ('Timestamp', 'datetime'), 'Type',
        ('GPS timestamp', 'datetime'), 'City', 'Latitude', 'Longitude',
        'Horizontal acc.', 'Speed', 'Object name',
        ('UI Timestamp', 'datetime'), 'Metadata', 'Scene',
        'App type value map','Active trips', 'Location'
    )
    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def uber_metadata_leveldb(context):
    files_found = context.get_files_found()
    data_list = []

    ldb_dirs = set()
    for f in files_found:
        if '__METADATA' in str(f):
            ldb_dirs.add(os.path.dirname(str(f)))

    for ldb_path in ldb_dirs:
        try:
            leveldb_records = scripts.ccl_leveldb.RawLevelDb(ldb_path)
            for record in leveldb_records.iterate_records_raw():
                if record.user_key.decode() != 'UBLocationNode.__DEFAULT_INDEX':
                    continue

                plist = get_plist_content(record.value)

                sample = plist.get('_sample', {})
                loc = sample.get('_location', {})

                if loc:
                    ts = loc.get('kCLLocationCodingKeyTimestamp')
                    timestamp = convert_cocoa_core_data_ts_to_utc(ts) if ts else ''

                    origin = f'{os.path.basename(str(record.origin_file))} (seq: {record.seq})'
                    source_file = context.get_relative_path(str(record.origin_file))

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
                        origin,
                        source_file
                    ))
        except (OSError, ValueError, UnicodeDecodeError) as ex:
            logfunc(f"Error reading LevelDB at {ldb_path}: {ex}")

    data_headers = (
        ('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Horizontal acc.',
        'Altitude', 'Vertical acc.', 'Course', 'Speed', 'State', 'Location',
        'Source File'
    )

    return data_headers, data_list, 'see Source File column'
