__artifacts_v2__ = {
    "uberClient": {
        "name": "Uber",
        "description": "account, payment profiles, nearby vehicles, user address location, searched rides, cached locations, sqlite locations data, locations",
        "author": "Django Faiola (djangofaiola.blogspot.com)",
        "version": "0.1.0",
        "date": "09/03/2024",
        "requirements": "none",
        "category": "Uber",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),          
        "function": "get_uber_client"
    }
}

import os
import json
import biplist
import plistlib
import nska_deserialize as nd
import sys
import re
import shutil
import sqlite3
import textwrap
from pathlib import Path
from scripts import ccl_leveldb
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, convert_ts_int_to_utc, convert_utc_human_to_timezone

# format timestamp
def FormatTimestamp(utc, timezone_offset, divisor=1.0):
    if not bool(utc):
        return ''
    else:
        timestamp = convert_ts_int_to_utc(int(float(utc) / divisor))
        return convert_utc_human_to_timezone(timestamp, timezone_offset)


# format location
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
    # locations
    return location + newLocation

# account
def get_account(file_found, report_folder, timezone_offset):
    data_list = []
    row = [ None ] * 17
    source_files = [ file_found ]

    # client
    f = open(file_found, 'r', encoding='utf-8')
    try:
        json_data = json.load(f)
        if bool(json_data):
            # first name
            row[0] = json_data.get('firstName')
            # last name
            row[1] = json_data.get('lastName')
            # phone number
            row[2] = json_data.get('mobileDigits')
            # email
            row[3] = json_data.get('email')
            # share code
            row[4] = json_data.get('referralCode')
            # picture url
            row[5] = json_data.get('pictureUrl')
            # profile type
            row[6] = json_data.get('profileType')
            # country code
            row[7] = json_data.get('mobileCountryIso2')
            # last payment profile id
            row[15] = json_data.get('lastSelectedPaymentProfileUUID')
            # user id
            row[16] = json_data.get('uuid')
    except Exception as ex:
        logfunc('Exception while parsing Uber App Account: ' + str(ex))
    finally:
        f.close()

    # city
    file_temp = os.path.dirname(file_found)
    file_temp = Path(file_temp).joinpath('city')
    if os.path.exists(file_temp):
        f = open(file_temp, 'r', encoding='utf-8')
        try:
            json_data = json.load(f)
            if bool(json_data):
                # city id
                row[8] = json_data.get('cityId')
                # city
                row[9] = json_data.get('cityName')
                # currency
                row[10] = json_data.get('currencyCode')
                # timezone
                row[11] = json_data.get('timezone')                
                
                # city file
                file_temp = str(file_temp)
                if file_temp.startswith('\\\\?\\'):
                    file_temp = file_temp[4:]
                source_files.append(file_temp)
        except Exception as ex:
            logfunc('Exception while parsing Uber App Account: ' + str(ex))
        finally:
            f.close()

    # clientStatus
    file_temp = os.path.dirname(file_found)
    file_temp = Path(file_temp).joinpath('clientStatus')
    if os.path.exists(file_temp):
        f = open(file_temp, 'r', encoding='utf-8')
        try:
            json_data = json.load(f)
            if bool(json_data):
                # meta
                meta = json_data.get('meta')
                if bool(meta):
                    row[12] = FormatTimestamp(meta.get('lastModifiedTimeMs'), timezone_offset, 1000.0)
                
                # clientStatus file
                file_temp = str(file_temp)
                if file_temp.startswith('\\\\?\\'):
                    file_temp = file_temp[4:]
                source_files.append(file_temp)
        except Exception as ex:
            logfunc('Exception while parsing Uber App Account: ' + str(ex))
        finally:
            f.close()

    # targetLocationSynced
    file_temp = os.path.dirname(file_found)
    file_temp = Path(file_temp).joinpath('targetLocationSynced')
    if os.path.exists(file_temp):
        f = open(file_temp, 'r', encoding='utf-8')
        try:
            json_data = json.load(f)
            if bool(json_data):
                # latitude
                row[13] = json_data.get('latitude')
                # longitude
                row[14] = json_data.get('longitude')

                # targetLocationSynced file
                file_temp = str(file_temp)
                if file_temp.startswith('\\\\?\\'):
                    file_temp = file_temp[4:]
                source_files.append(file_temp)
        except Exception as ex:
            logfunc('Exception while parsing Uber App Account: ' + str(ex))
        finally:
            f.close()

    # row
    if row.count(None) != len(row):
        report = ArtifactHtmlReport('Uber App Account')
        report.start_artifact_report(report_folder, 'Uber App Account')
        report.add_script()
        data_headers = ('First name', 'Last name', 'Mobile phone', 'Email', 'Share code', 'Profile picture url', 'Profile type',
                        'Country code', 'City ID', 'City', 'Currency code', 'Timezone', 'Last used', 'Latitude (startup)', 'Longitude (startup)', 
                        'Last payment profile ID', 'User ID') 

        data_list.append(row)

        report.write_artifact_data_table(data_headers, data_list, ', '.join(source_files), html_escape=False)
        report.end_artifact_report()
                
        tsvname = f'Uber App Account'
        tsv(report_folder, data_headers, data_list, tsvname)
                
        tlactivity = 'Uber App Account'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Uber App Account data available')


# payment profiles
def get_payment_profiles(file_found, report_folder, timezone_offset):
    data_list = []

    # E9446EF1-C440-4D70-B66F-3A49D1D58406/Library/Application Support/PersistentStorage/Store/PaymentFoundation.PaymentStreamModelKey/profiles
    f = open(file_found, 'r', encoding='utf-8')
    try:
        json_data = json.load(f)
        # array
        if bool(json_data) and (isinstance(json_data, list) or isinstance(json_data, tuple)):
            i_count = 0
            for item in json_data:
                # card type
                card_type = item.get('cardType')
                # account name
                account_name = item.get('accountName')
                # bank identification number
                card_bin = item.get('cardBin')
                # card number
                card_number = item.get('cardNumber')
                # category
                card_category = item.get('cardCategory')
                # expires (ms)
                card_expiration = FormatTimestamp(item.get('cardExpirationEpoch'), timezone_offset, 1000.0)
                # status
                status = item.get('status')
                # using type
                using_type = item.get('useCase')
                # country code
                country_code = item.get('billingCountryIso2')
                # uuid
                uuid = item.get('uuid')
                # location
                location = f'[{i_count}]'

                data_list.append((card_type, account_name, card_bin, card_number, card_category, card_expiration, status, using_type, country_code, uuid, location))
                i_count += 1
    except Exception as ex:
        logfunc('Exception while parsing Uber App Payment Profiles: ' + str(ex))
    finally:
        f.close()

    # data list
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Uber App Payment Profiles')
        report.start_artifact_report(report_folder, 'Uber App Payment Profiles')
        report.add_script()
        data_headers = ('Card type', 'Account name', 'Card BIN', 'Number', 'Category', 'Expires', 'Status', 'Using type', 'Country code', 'ID', 'Location') 

        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()
                    
        tsvname = f'Uber App Payment Profiles'
        tsv(report_folder, data_headers, data_list, tsvname)
                    
        tlactivity = 'Uber App Payment Profiles'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Uber App Payment Profiles data available')


# eyeball
def get_eyeball(file_found, report_folder, timezone_offset):
    # eyeball
    f = open(file_found, 'r', encoding='utf-8')
    try:
        json_data = json.load(f)   
        try:
            data_list = []
            # nearbyVehicles (object)
            nearby_vehicles = json_data.get('nearbyVehicles')
            for v, vehicle in nearby_vehicles.items():
                # vehicle (object)
                if not isinstance(vehicle, dict):
                    continue

                # vehicle_paths (object)
                vehicle_paths = vehicle.get('vehiclePaths')
                for vp, vehicle_path in vehicle_paths.items():
                    # location
                    #location = f'[nearbyVehicles][{v}][vehiclePaths]'

                    # array
                    for j in range(0, len(vehicle_path)):
                        item = vehicle_path[j]
                        # epoch (ms)
                        timestamp = FormatTimestamp(item.get('epoch'), timezone_offset, 1000.0)
                        # latitude
                        latitude = item.get('latitude')
                        # longitude
                        longitude = item.get('longitude')
                        # course
                        course = item.get('course')
                        # location
                        location = f'[nearbyVehicles][{v}][vehiclePaths][{vp}][{j}]'

                        data_list.append((timestamp, latitude, longitude, course, location))

            if len(data_list) > 0:
                report = ArtifactHtmlReport('Uber App Nearby Vehicles')
                report.start_artifact_report(report_folder, 'Uber App Nearby Vehicles')
                report.add_script()
                data_headers = ('Timestamp', 'Latitude', 'Longitude', 'Course', 'Location') 

                report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                report.end_artifact_report()
                    
                tsvname = 'Uber App Nearby Vehicles'
                tsv(report_folder, data_headers, data_list, tsvname)
                    
                tlactivity = 'Uber App Nearby Vehicles'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Uber App Nearby Vehicles data available')
        except Exception as ex:
            logfunc('Exception while parsing Uber App Nearby Vehicles: ' + str(ex))


        try:
            data_list = []
            # reverseGeocode (object)
            reverse_geocode = json_data.get('reverseGeocode')
            if bool(reverse_geocode):
                # latitude
                latitude = reverse_geocode.get('latitude')
                # longitude
                longitude = reverse_geocode.get('longitude')
                # uuid
                uuid = reverse_geocode.get('uuid')
                # longAddress
                address = reverse_geocode.get('longAddress')
                # components (array)
                # location
                location = f'[reverseGeocode]'

                data_list.append((latitude, longitude, address, uuid, location))
                
            if len(data_list) > 0:
                report = ArtifactHtmlReport('Uber App User Address Location')
                report.start_artifact_report(report_folder, 'Uber App User Address Location')
                report.add_script()
                data_headers = ('Latitude', 'Longitude', 'Address', 'ID', 'Location') 

                report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                report.end_artifact_report()
                
                tsvname = 'Uber App User Address Location'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'Uber App User Address Location'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Uber App User Address Location data available')           
        except Exception as ex:
            logfunc('Exception while parsing Uber App User Address Location: ' + str(ex))
    finally:
        f.close()


def load_plist_from_string(data):
    if not bool(data):
        return None
    
    if isinstance(data, (bytes, bytearray)):
        isNska = data.find(b'NSKeyedArchiver') != -1
    else:
        isNska = data.find('NSKeyedArchiver') != -1

    if not isNska:
        if sys.version_info >= (3, 9):
            plist = plistlib.loads(data)
        else:
            plist = biplist.readPlistFromString(data)
    else:
        try:
            plist = nd.deserialize_plist_from_string(data)
        except (nd.DeserializeError, nd.biplist.NotBinaryPlistException, nd.biplist.InvalidPlistException,
                nd.plistlib.InvalidFileException, nd.ccl_bplist.BplistError, ValueError, TypeError, OSError, OverflowError) as ex:
            logfunc(f'Failed to read plist for {data}, error was:' + str(ex))
    return plist


# searched rides
def get_searched_rides(file_found, report_folder, database, timezone_offset):
    try:
        cursor = database.cursor()
        cursor.execute('''
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
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Uber App searched rides')
            report.start_artifact_report(report_folder, 'Uber App searched rides')
            report.add_script()
            data_headers = ('Timestamp', 'Tag', 'Title', 'Address', 'Latitude', 'Longitude', 'Location') 
            data_list = []
            for row in all_rows:
                # timestamp
                timestamp = FormatTimestamp(row[2], timezone_offset)

                # location
                location = FormatLocation('', row[0], 'hits', '_id')
                location = FormatLocation(location, row[1], 'place', '_id')

                # row
                data_list.append((timestamp, row[3], row[4], row[5], row[6], row[7], location))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
                
            tsvname = f'Uber App Searched Rides'
            tsv(report_folder, data_headers, data_list, tsvname)
                
            tlactivity = f'Uber App Searched Rides'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Uber App Searched Rides data available')
    except Exception as ex:
        logfunc('Exception while parsing Uber App Searched Rides: ' + str(ex))


# cached locations
def get_cached_locations(file_found, report_folder, database, timezone_offset):
    try:
        cursor = database.cursor()
        cursor.execute('''
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
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Uber App Cached Locations')
            report.start_artifact_report(report_folder, 'Uber App Cached Locations')
            report.add_script()
            data_headers = ('Last hit', 'Type', 'Tag', 'Name', 'Address', 'Latitude', 'Longitude', 'Categories', 'Uber ID', 'Location') 
            data_list = []
            for row in all_rows:
                # timestamp
                timestamp = FormatTimestamp(row[1], timezone_offset)

                # location
                location = FormatLocation('', row[0], 'place', '_id')

                # row
                data_list.append((timestamp, row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], location))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
                
            tsvname = f'Uber App Cached Locations'
            tsv(report_folder, data_headers, data_list, tsvname)
                
            tlactivity = f'Uber App Cached Locations'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Uber App Cached Locations data available')
    except Exception as ex:
        logfunc('Exception while parsing Uber App Cached Locations: ' + str(ex))


# unified-reporter
def get_ur_locations(file_found, report_folder, database, timezone_offset):
    try:
        cursor = database.cursor()
        cursor.execute('''
        SELECT
	        m.auto_row_id,
	        (json_extract(m.content, '$.jsonConformingObject.meta.time_ms') / 1000) AS "timestamp",
	        m.message_type AS "messageType",
	        (json_extract(m.content, '$.jsonConformingObject.meta.location.gps_time_ms') / 1000) AS "gpsTime",
	        json_extract(m.content, '$.jsonConformingObject.meta.location.city') AS "city",
	        json_extract(m.content, '$.jsonConformingObject.meta.location.latitude') AS "lat",
	        json_extract(m.content, '$.jsonConformingObject.meta.location.longitude') AS "lng",
	        json_extract(m.content, '$.jsonConformingObject.meta.location.horizontal_accuracy') AS "accuracy",
	        json_extract(m.content, '$.jsonConformingObject.meta.location.speed') AS "speed",
	        --json_extract(m.content, '$.jsonConformingObject.meta.session.app_lifecycle_state') AS "appState",
	        json_extract(m.content, '$.jsonConformingObject.data.name') AS "name",
	        (json_extract(m.content, '$.jsonConformingObject.data.ui_state.timestamp_ms') / 1000) AS "uiTimestamp",
	        json_extract(m.content, '$.jsonConformingObject.data.ui_state.metadata') AS "uiMetadata",
	        json_extract(m.content, '$.jsonConformingObject.data.ui_state.scene') AS "uiScene",
	        json_extract(m.content, '$.jsonConformingObject.data.app_type_value_map') AS "appTypeValueMap",
	        json_extract(m.content, '$.jsonConformingObject.data.active_trips') AS "actTrips"
        FROM message AS "m"        
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Uber App SQLite Locations Data')
            report.start_artifact_report(report_folder, 'Uber App SQLite Locations Data')
            report.add_script()
            data_headers = ('Timestamp', 'Type', 'GPS timestamp', 'City', 'Latitude', 'Longitude', 'Horizontal acc.', 'Speed', 'Object name',
                            'UI Timestamp', 'Metadata', 'Scene', 'App type value map','Active trips', 'Location') 
            data_list = []
            for row in all_rows:
                # timestamp
                timestamp = FormatTimestamp(row[1], timezone_offset)

                # ui timestamp
                ui_timestamp = FormatTimestamp(row[10], timezone_offset)

                # location
                location = FormatLocation('', row[0], 'message', 'auto_row_id')

                # row
                data_list.append((timestamp, row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], 
                                  ui_timestamp, row[11], row[12], row[13], row[14], location))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
                
            tsvname = f'Uber App SQLite Locations Data'
            tsv(report_folder, data_headers, data_list, tsvname)
                
            tlactivity = f'Uber App SQLite Locations Data'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Uber App SQLite Locations Data available')
    except Exception as ex:
        logfunc('Exception while parsing Uber App SQLite Locations Data: ' + str(ex))


# locations
def get_locations(ldb_path, report_folder, timezone_offset):
    data_list = []

    leveldb_records = ccl_leveldb.RawLevelDb(ldb_path)
    for record in leveldb_records.iterate_records_raw():
        # key "UBLocationNode.__DEFAULT_INDEX"
        if record.user_key.decode() == 'UBLocationNode.__DEFAULT_INDEX':
            # location
            try:
                plist = load_plist_from_string(record.value)
            except Exception:
                pass
            else:
                if bool(plist.get('_sample')):
                    sample_location = plist['_sample']['_location']
                    if bool(sample_location):                        
                        # timestamp
                        timestamp_real = sample_location['kCLLocationCodingKeyTimestamp'] + 978307200.0
                        timestamp = FormatTimestamp(timestamp_real, timezone_offset)
                        # latitude
                        latitude = sample_location['kCLLocationCodingKeyCoordinateLatitude']
                        # longitude
                        longitude = sample_location['kCLLocationCodingKeyCoordinateLongitude']
                        # horizontal accuracy
                        horz_accuracy = sample_location['kCLLocationCodingKeyHorizontalAccuracy']
                        # altitude
                        altitude = sample_location['kCLLocationCodingKeyAltitude']
                        # vertical accuracy
                        vert_accuracy = sample_location['kCLLocationCodingKeyVerticalAccuracy']
                        # course
                        course = sample_location['kCLLocationCodingKeyCourse']
                        # speed
                        speed = sample_location['kCLLocationCodingKeySpeed']
                        # location
                        location = f'{str(Path(record.origin_file).name)} (seq no: {hex(record.seq)})'

                        data_list.append((timestamp, latitude, longitude, horz_accuracy, altitude, vert_accuracy, course, speed, record.state.name, location))

    # locations
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Uber App Locations')
        report.start_artifact_report(report_folder, 'Uber App Locations')
        report.add_script()
        data_headers = ('Timestamp', 'Latitude', 'Longitude', 'Horizontal acc.', 'Altitude', 'Vertical acc.', 'Course', 'Speed', 'State', 'Location') 

        report.write_artifact_data_table(data_headers, data_list, ldb_path, html_escape=False)
        report.end_artifact_report()
                
        tsvname = 'Uber App Locations'
        tsv(report_folder, data_headers, data_list, tsvname)
                
        tlactivity = 'Uber App Locations'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Uber App Locations data available')


# leveldb
def parse_leveldb(manifest_path, report_folder, timezone_offset):
    # com.ubercab.UberClient
    base_path = os.path.dirname(manifest_path)

    leveldb_records = ccl_leveldb.RawLevelDb(manifest_path)
    for record in leveldb_records.iterate_records_raw():
        key = record.user_key.decode()

        # plist
        plist = load_plist_from_string(record.value)

        # name
        name = plist.get('_name')
        # uuid (leveldb folder name)
        uuid = plist.get('_uuid')

        if not bool(name) or not bool(uuid):
            continue

        # uuid path
        ldb_path = os.path.join(base_path, uuid)
        
        # locations
        if key == 'UBPersistenceMetadata.com.uber.location.UBDeviceLocationSource':
            get_locations(ldb_path, report_folder, timezone_offset)


# uber client
def get_uber_client(files_found, report_folder, seeker, wrap_text, timezone_offset):
    identifier = ''

    for file_found in files_found:
        if file_found.endswith('.com.apple.mobile_container_manager.metadata.plist'):
            with open(file_found, 'rb') as f:
                pl = plistlib.load(f)
                if pl['MCMMetadataIdentifier'] == 'com.ubercab.UberClient':
                    fulldir = (os.path.dirname(file_found))
                    identifier = (os.path.basename(fulldir))
                    break
                f.close()

    if bool(identifier):
        # */Library/Application Support/PersistentStorage/BootstrapStore/RealtimeRider.StreamModelKey/**
        source_files = seeker.search(f'*/{identifier}/Library/Application Support/PersistentStorage/BootstrapStore/RealtimeRider.StreamModelKey/**')
        if bool(source_files) and len(source_files) > 0:
            for source_file in source_files:
                file_path = Path(source_file)
                # client
                if file_path.name == 'client':
                    get_account(source_file, report_folder, timezone_offset)
                # nearby vehicles, user address location
                elif file_path.name == 'eyeball':
                    get_eyeball(source_file, report_folder, timezone_offset)

        # */Library/Application Support/PersistentStorage/Store/PaymentFoundation.PaymentStreamModelKey/profiles
        source_files = seeker.search(f'*/{identifier}/Library/Application Support/PersistentStorage/Store/PaymentFoundation.PaymentStreamModelKey/profiles',
                                     return_on_first_hit=True)
        if bool(source_files) and len(source_files) > 0:
            get_payment_profiles(source_files, report_folder, timezone_offset)

        # */Documents/database.db or */Documents/ur_message.db
        source_files = seeker.search(f'*/{identifier}/Documents/*.db', return_on_first_hit=False)
        if bool(source_files) and len(source_files) > 0:
            for source_file in source_files:
                source_file = str(source_file)

                # database.db
                if source_file.endswith('database.db'):
                    db = open_sqlite_db_readonly(source_file)
                    try:
                        # searched rides
                        get_searched_rides(source_file, report_folder, db, timezone_offset)

                        # cached locations
                        get_cached_locations(source_file, report_folder, db, timezone_offset)
                        
                    finally:
                        db.close()

                # ur_message.db
                elif source_file.endswith('ur_message.db'):
                    db = open_sqlite_db_readonly(source_file)
                    try:
                        # unified-reporter locations
                        get_ur_locations(source_file, report_folder, db, timezone_offset)

                    finally:
                        db.close()
                        
        # */Library/Application Support/com.ubercab.UberClient/__METADATA/**
        source_files = seeker.search(f'*/{identifier}/Library/Application Support/com.ubercab.UberClient/__METADATA/*.ldb', 
                                     return_on_first_hit=True)
        if bool(source_files) and len(source_files) > 0:
            parse_leveldb(os.path.dirname(source_files), report_folder, timezone_offset)
