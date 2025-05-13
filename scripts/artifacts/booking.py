__artifacts_v2__ = {
    "booking_preferences": {
        "name": "Preferences",
        "description": "Parses and extract Booking.com Preferences",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-05-28",
        "last_update_date": "2025-05-02",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Preferences/com.booking.BookingApp.plist'),
        "output_types": [ "none" ],
        "artifact_icon": "settings"
    },
    "booking_account": {
        "name": "Account",
        "description": "Parses and extract Booking.com Account",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-05-28",
        "last_update_date": "2025-05-02",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/KeyValueStorageAccountDomain*',
                  '*/mobile/Containers/Data/Application/*/Library/Application Support/AccountSettings*'),
        "output_types": [ "lava", "html", "tsv" ],
        "html_columns": [ "Profile picture URL", "Emails", "Facilities", "Source file name", "Location" ],
        "artifact_icon": "user"
    },
    "booking_payment_methods": {
        "name": "Payment Methods",
        "description": "Parses and extract Booking.com Payment Methods",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-05-28",
        "last_update_date": "2025-05-02",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/KeyValueStorageAccountDomain*',
                  '*/mobile/Containers/Data/Application/*/Library/Application Support/AccountSettings*'),
        "output_types": [ "lava", "html", "tsv" ],
        "html_columns": [ "Source file name", "Location" ],
        "artifact_icon": "credit-card"
    },
    "booking_wish_lists": {
        "name": "Wish Lists",
        "description": "Parses and extract Booking.com Wish Lists",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-05-28",
        "last_update_date": "2025-05-02",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/KeyValueStorageRecentsDomain*'),
        "output_types": [ "lava", "html", "tsv" ],
        "html_columns": [ "Source file name", "Location" ],
        "artifact_icon": "star"
    },
    "booking_viewed": {
        "name": "Viewed",
        "description": "Parses and extract Booking.com Viewed",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-05-28",
        "last_update_date": "2025-05-02",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/KeyValueStorageRecentsDomain*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Image URL", "Website", "Source file name", "Location" ],
        "artifact_icon": "eye"
    },
    "booking_recently_searched": {
        "name": "Recently Searched",
        "description": "Parses and extract Booking.com Recently Searched",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-05-28",
        "last_update_date": "2025-05-02",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/KeyValueStorageRecentsDomain*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Source file name", "Location" ],
        "artifact_icon": "search"
    },
    "booking_recently_booked": {
        "name": "Recently Booked",
        "description": "Parses and extract Booking.com Recently Booked",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-05-28",
        "last_update_date": "2025-05-02",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/KeyValueStorageRecentsDomain*'),
        "output_types": [ "lava", "html", "tsv" ],
        "html_columns": [ "Image URL", "Website", "Source file name", "Location" ],
        "artifact_icon": "shopping-bag"
    },
    "booking_booked": {
        "name": "Booked",
        "description": "Parses and extract Booking.com Booked",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-05-28",
        "last_update_date": "2025-05-13",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/BookingClouds*'),
        "output_types": [ "lava", "html", "tsv" ],
        "html_columns": [ "Check-in/out (Hotel time zone)", "Hotel contacts", "Confirmation number/Pin code", "Rooms", "Booker details", "Attachment",
                          "Source file name", "Location" ],
        "artifact_icon": "shopping-bag"
    },
    "booking_stored_destinations": {
        "name": "Stored Destinations",
        "description": "Parses and extract Booking.com Stored Destinations",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-05-28",
        "last_update_date": "2025-05-02",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/KeyValueStorageSharedDomain*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Image URL", "Source file name", "Location" ],
        "artifact_icon": "map"
    },
    "booking_notifications": {
        "name": "Notifications",
        "description": "Parses and extract Booking.com Notifications",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-05-28",
        "last_update_date": "2025-05-02",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/NotificationsModel.sqlite*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Image URL", "Action arguments", "Source file name", "Location" ],
        "artifact_icon": "bell"
    },
    "booking_flights_searched": {
        "name": "Flights Searched",
        "description": "Parses and extract Booking.com Flights Searched",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-05-28",
        "last_update_date": "2025-05-02",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/flight_rs_v2'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Source airports", "Destination airports", "Routes", "Travellers' details", "Source file name", "Location" ],
        "artifact_icon": "search"
    }
}

import inspect
from urllib.parse import urlparse, urlunparse
import json
import pytz
from datetime import datetime, date
from pathlib import Path
from scripts.ilapfuncs import get_file_path, get_sqlite_db_records, get_plist_content, get_plist_file_content, lava_get_full_media_info, \
    convert_plist_date_to_utc, convert_unix_ts_to_utc, convert_ts_int_to_utc, check_in_media, artifact_processor, logfunc


# booking app id
booking_app_identifier = None
# constants
LINE_BREAK = '\n'
COMMA_SEP = ', '
HTML_LINE_BREAK = '<br>'
HTML_HORZ_RULE = '<hr>'


# unordered list
def unordered_list(values, html_format=False):
    if not bool(values):
        return None

    return HTML_LINE_BREAK.join(values) if html_format else LINE_BREAK.join(values)


# generic url
def generic_url(value, html_format=False):
    # default
    result = None

    if bool(value) and (value != 'null'):
        u = urlparse(value)
        # 0=scheme, 2=path
        if not bool(u.scheme) and u.path.startswith('www'):
            u = u._replace(scheme='http')
        url = urlunparse(u)
        result =  f'<a href="{url}" target="_blank">{value}</a>' if html_format else url

    return result


# json file content
def get_json_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        logfunc(f"Error reading file {file_path}: {str(e)}")
        return None


# device path/local path
def get_device_file_path(file_path, seeker):
    device_path = file_path

    if bool(file_path):
        file_info = seeker.file_infos.get(file_path) if file_path else None
        # data folder: /path/to/report/data
        if file_info:
            source_path = file_info.source_path
        # extraction folder: /path/to/directory
        else:
            source_path = file_path
        source_path = Path(source_path).as_posix()

        index_private = source_path.find('/private/')
        if index_private > 0:
            device_path = source_path[index_private:]
    
    return device_path


def location_type_names(value):
    if (value == None):
        return ''

    # city
    elif value == 0: return 'City'
    # district
    elif value == 1: return 'District'
    # district
    elif value == 2: return 'Region'
    # country
    elif value == 3: return 'Country'
    # hotel
    elif value == 4: return 'Hotel'
    # airport
    elif value == 5: return 'Airport'
    # landmark
    elif value == 6: return 'Landmark'
    # google place
    elif value == 7: return 'Google Places'
    # unknown
    else: 
        return f"N/D: {value}"


def hotel_type_names(value):
    if (value == None):
        return ''

    # apartment
    elif value == 201: return 'Apartment'
    # guest accommodation
    elif value == 202: return 'Guest Accommodation'
    # hostel
    elif value == 203: return 'Hostel'
    # hotel
    elif value == 204: return 'Hotel'
    # motel
    elif value == 205: return 'Motel'
    # resort
    elif value == 206: return 'Resort'
    # residence
    elif value == 207: return 'Residence'
    # bed and breakfast
    elif value == 208: return 'Bed and Breakfast'
    # ryokan
    elif value == 209: return 'Ryokan'
    # farmstay
    elif value == 210: return 'Farmstay'
    # bungalow
    elif value == 211: return 'Bungalow'
    # resort village
    elif value == 212: return 'Resort Village'
    # villa
    elif value == 213: return 'Villa'
    # campground
    elif value == 214: return 'Campground'
    # boat
    elif value == 215: return 'Boat'
    # guesthouse
    elif value == 216: return 'Guesthouse'
    # inn
    elif value == 218: return 'Inn'
    # condo hotel
    elif value == 219: return 'Condo Hotel'
    # vacation home
    elif value == 220: return 'Vacation Home'
    # lodge
    elif value == 221: return 'Lodge'
    # homestay
    elif value == 222: return 'Homestay'
    # coutry house
    elif value == 223: return 'Country House'
    # luxury tent
    elif value == 224: return 'Luxury Tent'
    # capsule hotel
    elif value == 225: return 'Capsule Hotel'
    # love hotel
    elif value == 226: return 'Love Hotel'
    # riad
    elif value == 227: return 'Riad'
    # chalet
    elif value == 228: return 'Chalet'
    # condo
    elif value == 229: return 'Condo'
    # cottage
    elif value == 230: return 'Cottage'
    # economy hotel
    elif value == 231: return 'Economy Hotel'
    # gite
    elif value == 232: return 'Gite'
    # health resort
    elif value == 233: return 'Health Resort'
    # cruise
    elif value == 234: return 'Cruise'
    # student accommodation
    elif value == 235: return 'Student Accommodation'
    # unknown
    else: 
        return f"N/D: {value}"


# iso 8601 format to utc
def convert_iso8601_to_utc(str_date):
    if bool(str_date) and isinstance(str_date, str) and (str_date != 'null'):
        dt = datetime.fromisoformat(str_date).timestamp()
        return convert_ts_int_to_utc(dt)
    else:
        return str_date


def convert_utc_to_hotel_timezone(ts, timezone_offset):
    utc = pytz.timezone('UTC').localize(ts)
    return utc.astimezone(pytz.timezone(timezone_offset))


def format_check_in_out(ts_from, ts_until, tz=''):
    # check-in
    if bool(ts_from):
        # seconds
        if isinstance(ts_from, float):
            check_from = convert_unix_ts_to_utc(ts_from).strftime('%H:%M')            
        # '00:00'
        elif isinstance(ts_from, str):
            check_from = ts_from
        # timestamp to time zone
        elif len(tz) > 0:
            check_from = convert_utc_to_hotel_timezone(ts_from, tz).strftime('%H:%M')
        # timestamp
        else:
            check_from = ts_from.strftime('%H:%M')
    else:
        check_from = '00:00'

    # check-out
    if bool(ts_until):
        # seconds
        if isinstance(ts_until, float):
            check_until = convert_unix_ts_to_utc(ts_until).strftime('%H:%M')
        # '00:00'
        elif isinstance(ts_until, str):
            check_until = ts_until
        # timestamp to time zone
        elif len(tz) > 0:
            check_until = convert_utc_to_hotel_timezone(ts_until, tz).strftime('%H:%M')
        # timestamp
        else:
            check_until = ts_until.strftime('%H:%M')
    else:
        check_until = '00:00'

    return f"{check_from} - {check_until}"


def append_tag_value(target, tag, value):
    # "key: value"
    if value is None:
        return
    # dict, list, set, tuple
    elif isinstance(value, (dict, list, set, tuple)):
        if len(value) > 0:
            target.append(f"{tag}: {value}")
    else:
        target.append(f"{tag}: {value}")


# preferences
@artifact_processor
def booking_preferences(files_found, report_folder, seeker, wrap_text, timezone_offset):

    source_path = None
    global booking_app_identifier

    # all files
    for file_found in files_found:
        file_found = str(file_found)
        # prefs
        plist_data = get_plist_file_content(file_found)
        if not bool(plist_data):
            continue

        try:
            # source path
            source_path = file_found

            # Library/Preferences/com.booking.BookingApp.plist
            booking_app_identifier = Path(file_found).parents[2].name

        except Exception as e:
            logfunc(f"Error: {str(e)}")
            pass

    # return empty
    return (), [], source_path


# account
@artifact_processor
def booking_account(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        'First name',
        'Last name',
        'Nickname',
        'Profile picture URL',
        'Gender',
        ('Birth date', 'date'),
        'Street',
        'City',
        'Zip code',
        'Country',
        ('Phone number', 'phonenumber'),
        'Emails',
        "Genius membership",
        "Facilities",
        "Unique ID",
        'Authentication token',
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    artifact_info_name = __artifacts_v2__['booking_account']['name']

    # all files
    for file_found in files_found:
        file_rel_path = Path(Path(file_found).parent.name, Path(file_found).name).as_posix()
        device_file_path = get_device_file_path(file_found, seeker)

        # KeyValueStorageAccountDomain[.plist]
        if file_rel_path.endswith('KeyValueStorageAccountDomain') or file_rel_path.endswith('KeyValueStorageAccountDomain.plist'):
            try:
                device_file_paths = [ device_file_path ]

                # plist data
                plist_data = get_plist_file_content(file_found)
                if not bool(plist_data):
                    continue

                # authentication token
                auth_token = plist_data.get('auth_token')
                # user profile
                user_profile = plist_data.get('user_profile', {})
                # first name
                first_name = user_profile.get('first_name')
                # last name
                last_name = user_profile.get('last_name')
                # nickname
                nickname = user_profile.get('nickname')
                # profile picture url
                pp_urls = user_profile.get('avatar_details', {}).get('urls',{})
                pp_url = next(iter(pp_urls.items()))[1] if bool(pp_urls) else None
                pp_url_html = generic_url(pp_url, html_format=True)
                # gender
                gender = user_profile.get('gender')
                # date of birth (yyyy/mm/dd)
                birth_date = user_profile.get('date_of_birth')
                birth_date = birth_date.date() if bool(birth_date) else None
                # street
                street = user_profile.get('street')
                # city
                city = user_profile.get('city')
                # zip code
                zip_code = user_profile.get('zipcode')
                # country
                country = user_profile.get('country')
                # phone number
                phone_number = user_profile.get('telephone')
                # email address
                email_address = user_profile.get('email_address', [])
                emails = unordered_list(email_address)
                emails_html = unordered_list(email_address, html_format=True)
                # email data
                # genius membership
                is_genius = user_profile.get('is_genius')
                # preferred.facility
                facility = user_profile.get('preferred', {}).get('facility', [])
                prefs = []
                for x in facility:
                    if bool(x.get('is_selected')): prefs.append(x.get('name'))
                facilities = unordered_list(prefs)
                facilities_html = unordered_list(prefs, html_format=True)
                # uid
                uid = user_profile.get('uid')

                # source file name
                device_file_paths = dict.fromkeys(device_file_paths)
                source_file_name = unordered_list(device_file_paths)
                source_file_name_html = unordered_list(device_file_paths, html_format=True)
                # location
                location = f""

                # html row
                data_list_html.append((first_name, last_name, nickname, pp_url_html, gender, birth_date, street, city, zip_code,country, phone_number,
                                       emails_html, is_genius, facilities_html, uid, auth_token, source_file_name_html, source_file_name, location))
                # lava row
                data_list.append((first_name, last_name, nickname, pp_url, gender, birth_date, street, city, zip_code,country, phone_number,
                                  emails, is_genius, facilities, uid, auth_token, source_file_name_html, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

        # AccountSettings[.plist]
        elif file_rel_path.endswith('AccountSettings') or file_rel_path.endswith('AccountSettings.plist'):
            try:
                device_file_paths = [ device_file_path ]

                # plist data
                plist_data = get_plist_file_content(file_found)
                if not bool(plist_data):
                    continue

                # personal details
                personal_details = plist_data.get('userDetailsResponse', {}).get('userDetails', {}).get('personalDetails', {})
                # contact details
                contact_details = plist_data.get('userDetailsResponse', {}).get('userDetails', {}).get('contactDetails', {})

                # authentication token
                auth_token = None
                # first name
                first_name = personal_details.get('name', {}).get('first')
                # last name
                last_name = personal_details.get('name', {}).get('last')
                # nickname
                nickname = personal_details.get('displayName')
                # profile picture url
                pp_urls = personal_details.get('avatar', {}).get('urls', {})
                pp_url = next(iter(pp_urls.items()))[1] if bool(pp_urls) else None
                pp_url_html = generic_url(pp_url, html_format=True)
                # gender
                gender = personal_details.get('gender')
                # date of birth (yyyy/mm/dd)
                birth_date = personal_details.get('dateOfBirth', {})                   
                birth_date = date(birth_date.get('year'), birth_date.get('month'), birth_date.get('day')) if bool(birth_date) else None
                # street
                street = contact_details.get('address', {}).get('street')
                # city
                city = contact_details.get('address', {}).get('cityName')
                # zip code
                zip_code = contact_details.get('address', {}).get('zip')
                # country
                country = contact_details.get('address', {}).get('countryCode')
                # phone number
                phone_number = contact_details.get('primaryPhone', {}).get('fullNumber')
                # email address
                emails =  contact_details.get('primaryEmail', {}).get('address')
                emails_html = emails
                # email data
                # genius membership
                is_genius = None
                # preferred.facility
                facilities = None
                facilities_html = None
                # uid
                uid = None

                # source file name
                device_file_paths = dict.fromkeys(device_file_paths)
                source_file_name = unordered_list(device_file_paths)
                source_file_name_html = unordered_list(device_file_paths, html_format=True)
                # location
                location = f"[userDetailsResponse][userDetails]"

                # html row
                data_list_html.append((first_name, last_name, nickname, pp_url_html, gender, birth_date, street, city, zip_code,country, phone_number,
                                       emails_html, is_genius, facilities_html, uid, auth_token, source_file_name_html, source_file_name, location))
                # lava row
                data_list.append((first_name, last_name, nickname, pp_url, gender, birth_date, street, city, zip_code,country, phone_number,
                                  emails, is_genius, facilities, uid, auth_token, source_file_name_html, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

    return data_headers, (data_list, data_list_html), ' '


# payment methods
@artifact_processor
def booking_payment_methods(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        'Unique ID',
        'Type',
        'Status',
        'Valid thru',
        'Cardholder name',
        'Last four digits',
        'Business',        
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    artifact_info_name = __artifacts_v2__['booking_payment_methods']['name']

    # all files
    for file_found in files_found:
        file_rel_path = Path(Path(file_found).parent.name, Path(file_found).name).as_posix()
        device_file_path = get_device_file_path(file_found, seeker)

        # KeyValueStorageAccountDomain[.plist]
        if file_rel_path.endswith('KeyValueStorageAccountDomain') or file_rel_path.endswith('KeyValueStorageAccountDomain.plist'):
            try:
                device_file_paths = [ device_file_path ]

                # plist data
                plist_data = get_plist_file_content(file_found)
                if not bool(plist_data):
                    continue

                # credit card details
                cc_details = plist_data.get('user_profile', {}).get('cc_details')

                # array
                for i in range(0, len(cc_details)):
                    cc = cc_details[i]
                    
                    # id
                    id = cc.get('cc_id')
                    # type
                    type_ = cc.get('cc_type')
                    # status
                    status = cc.get('cc_status')
                    # valid thru (mm-yyyy)
                    valid_thru = f"{cc.get('cc_expire_month'):02}-{cc.get('cc_expire_year')}"
                    # cardholder name
                    cardholder_name = cc.get('cc_name')
                    # last digits
                    last_digits = cc.get('last_digits')
                    # is business
                    is_business = cc.get('cc_is_business')

                    # source file name
                    device_file_paths = dict.fromkeys(device_file_paths)
                    source_file_name = unordered_list(device_file_paths)
                    # location
                    location = f"[user_profile][cc_details][{i}]"

                    # html row
                    data_list_html.append((id, type_, status, valid_thru, cardholder_name, last_digits, is_business, source_file_name, location))
                    # lava row
                    data_list.append((id, type_, status, valid_thru, cardholder_name, last_digits, is_business, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

        # AccountSettings[.plist]
        elif file_rel_path.endswith('AccountSettings') or file_rel_path.endswith('AccountSettings.plist'):
            try:
                device_file_paths = [ device_file_path ]

                # plist data
                plist_data = get_plist_file_content(file_found)
                if not bool(plist_data):
                    continue

                # credit card details
                cc_details = plist_data.get('cardsResponse', {}).get('values')

                # array
                for i in range(0, len(cc_details)):
                    cc = cc_details[i]
                    
                    # id
                    id = cc.get('id')
                    # type
                    type_ = cc.get('name')
                    # status
                    status = cc.get('status')
                    # valid thru (mm-yyyy)
                    valid_thru = cc.get('expirationDateFormatted')
                    # card holder name
                    cardholder_name = None
                    # last digits
                    last_digits = cc.get('lastDigits')
                    # is business
                    is_business = cc.get('cc_is_business')

                    # source file name
                    device_file_paths = dict.fromkeys(device_file_paths)
                    source_file_name = unordered_list(device_file_paths)
                    # location
                    location = f"[cardsResponse][values][{i}]"

                    # html row
                    data_list_html.append((id, type_, status, valid_thru, cardholder_name, last_digits, is_business, source_file_name, location))
                    # lava row
                    data_list.append((id, type_, status, valid_thru, cardholder_name, last_digits, is_business, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

    return data_headers, (data_list, data_list_html), ' '


# stored destinations
@artifact_processor
def booking_stored_destinations(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Created', 'datetime'),
        'Location type',
        'Unique ID',
        'Destination name',
        'Address/Description',
        'City',
        'Region',
        'Country',
        'Latitude',
        'Longitude',
        'Time zone',
        'Image URL',
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    artifact_info_name = __artifacts_v2__['booking_stored_destinations']['name']

    # all files
    for file_found in files_found:
        file_rel_path = Path(Path(file_found).parent.name, Path(file_found).name).as_posix()
        device_file_path = get_device_file_path(file_found, seeker)

        # KeyValueStorageSharedDomain[.plist]
        if file_rel_path.endswith('KeyValueStorageSharedDomain') or file_rel_path.endswith('KeyValueStorageSharedDomain.plist'):
            try:
                device_file_paths = [ device_file_path ]

                # plist data
                plist_data = get_plist_file_content(file_found)
                if not bool(plist_data):
                    continue

                # stored destinations
                stored_destinations = plist_data.get('stored_destinations')
                # array
                for i in range(0, len(stored_destinations)):
                    dest = stored_destinations[i]

                    # created/last updated
                    created = convert_plist_date_to_utc(dest.get('created'))
                    # location
                    loc = dest.get('loc', {})
                    # type
                    type_ = location_type_names(loc.get('locationType_'))
                    # id
                    id = loc.get('id_')
                    # destination name
                    dest_name = loc.get('string_')
                    # description (place name)
                    description = loc.get('substring_')
                    if not bool(description): description = loc.get('address')      # (locationType_=7)
                    # city_
                    city = loc.get('city_')
                    if bool(city):
                        # city name
                        city_name = city.get('string_')
                        # region name
                        region_name = city.get('region_name')
                    # no city_
                    else:
                        # city name
                        city_name = loc.get('cityName_')
                        # region name
                        region_name = loc.get('region_name')
                    # country name
                    country_name = loc.get('countryName_')
                    if not bool(country_name): country_name = loc.get('country')    # (locationType_=7)
                    # location (locationType_=7)
                    location_dict = loc.get('location')
                    if bool(location_dict):
                        # latitude
                        latitude = location_dict.get('latitude')
                        # longitude
                        longitude = location_dict.get('longitude')
                    # no location
                    else:
                        # latitude
                        latitude = loc.get('latitude_')
                        # longitude
                        longitude = loc.get('longitude_')
                    # time zone
                    timezone = loc.get('timezone')
                    # image url
                    image_url = loc.get('image_url')
                    image_url_html = generic_url(image_url, html_format=True)

                    # source file name
                    device_file_paths = dict.fromkeys(device_file_paths)
                    source_file_name = unordered_list(device_file_paths)
                    # location
                    location = f"[stored_destinations][{i}]"

                    # html row
                    data_list_html.append((created, type_, id, dest_name, description, city_name, region_name, country_name, latitude, longitude,
                                      timezone, image_url_html, source_file_name, location))
                    # lava row
                    data_list.append((created, type_, id, dest_name, description, city_name, region_name, country_name, latitude, longitude,
                                      timezone, image_url, source_file_name, location))

            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

    return data_headers, (data_list, data_list_html), ' '


# recently searched
@artifact_processor
def booking_recently_searched(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Searched', 'datetime'),
        'Location type',
        'Unique ID',
        'Destination name',
        'Description',
        'City',
        'Region',
        'Country',
        'Latitude',
        'Longitude',
        'Time zone',
        'Check-in',
        'Check-out',
        'Number of rooms',
        'Guests',
        'Number of nights',
        'Source',
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    artifact_info_name = __artifacts_v2__['booking_recently_searched']['name']

    # all files
    for file_found in files_found:
        file_rel_path = Path(Path(file_found).parent.name, Path(file_found).name).as_posix()
        device_file_path = get_device_file_path(file_found, seeker)

        # KeyValueStorageRecentsDomain[.plist]
        if file_rel_path.endswith('KeyValueStorageRecentsDomain') or file_rel_path.endswith('KeyValueStorageRecentsDomain.plist'):
            try:
                device_file_paths = [ device_file_path ]

                # plist data
                plist_data = get_plist_file_content(file_found)
                if not bool(plist_data):
                    continue

                # stored searches
                stored_searches = plist_data.get('stored_searches')
                # array
                for i in range(0, len(stored_searches)):
                    ss = stored_searches[i]

                    # searched
                    searched = convert_plist_date_to_utc(ss.get('created'))
                    # destination
                    dest = ss.get('destination')
                    # location type
                    type_ = location_type_names(dest.get('locationType_'))
                    # id
                    id = dest.get('id_')
                    # destination name
                    dest_name = dest.get('string_')
                    # description (place name)
                    description = dest.get('substring_')
                    if not bool(description): description = dest.get('address')     # (locationType_=7)
                    # city_
                    city = dest.get('city_')
                    if bool(city):
                        # city name
                        city_name = city.get('string_')
                        # region name
                        region_name = city.get('region_name')
                    # no city_
                    else:
                        # city name
                        city_name = dest.get('cityName_')
                        # region name
                        region_name = dest.get('region_name')
                    # country name
                    country_name = dest.get('countryName_')
                    if not bool(country_name): country_name = dest.get('country')   # (locationType_=7)
                    # location (locationType_=7)
                    location_dict = dest.get('location')
                    if bool(location_dict):
                        # latitude
                        latitude = location_dict.get('latitude')
                        # longitude
                        longitude = location_dict.get('longitude')
                    # no location
                    else:
                        # latitude
                        latitude = dest.get('latitude_')
                        # longitude
                        longitude = dest.get('longitude_')
                    # time zone
                    timezone = dest.get('timezone')
                    # check-in
                    check_in = ss.get('checkin')
                    # check-out
                    check_out = ss.get('checkout')
                    # number of rooms
                    number_of_rooms = ss.get('number_of_rooms')
                    # guests per room
                    guests_per_room = ss.get('guests_per_room')
                    # number of nights
                    number_of_nights = ss.get('number_of_nights')
                    # source
                    source = ss.get('source')

                    # source file name
                    device_file_paths = dict.fromkeys(device_file_paths)
                    source_file_name = unordered_list(device_file_paths)
                    # location
                    location = f"[stored_searches][{i}]"

                    # html row
                    data_list_html.append((searched, type_, id, dest_name, description, city_name, region_name, country_name, latitude, longitude,
                                      timezone, check_in, check_out, number_of_rooms, guests_per_room, number_of_nights, source, source_file_name, location))
                    # lava row
                    data_list.append((searched, type_, id, dest_name, description, city_name, region_name, country_name, latitude, longitude,
                                      timezone, check_in, check_out, number_of_rooms, guests_per_room, number_of_nights, source, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

    return data_headers, (data_list, data_list_html), ' '


# recently booked
@artifact_processor
def booking_recently_booked(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        'Hotel type',
        'Hotel Id',
        'Hotel name',
        'Address',
        'City',
        'Region',
        'Zip code',
        'Latitude',
        'Longitude',
        'Check-in (Hotel time zone)',
        'Check-out (Hotel time zone)',
        'Image URL',
        'Website',
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    artifact_info_name = __artifacts_v2__['booking_recently_booked']['name']

    # all files
    for file_found in files_found:
        file_rel_path = Path(Path(file_found).parent.name, Path(file_found).name).as_posix()
        device_file_path = get_device_file_path(file_found, seeker)

        # KeyValueStorageRecentsDomain[.plist]
        if file_rel_path.endswith('KeyValueStorageRecentsDomain') or file_rel_path.endswith('KeyValueStorageRecentsDomain.plist'):
            try:
                device_file_paths = [ device_file_path ]

                # plist data
                plist_data = get_plist_file_content(file_found)
                if not bool(plist_data):
                    continue

                # booked
                booked = plist_data.get('booked', {})
                # dict
                for key, value in booked.items():
                    # hotel
                    hotel = value.get('hotel')

                    # hotel type
                    type_ = hotel_type_names(hotel.get('hotel_type'))
                    # hotel id = key
                    id = hotel.get('hotel_id')
                    # hotel name
                    hotel_name = hotel.get('name')
                    # address
                    address = hotel.get('address')
                    # city
                    city = hotel.get('city')
                    if bool(city):
                        # city name
                        city_name = city.get('string_')
                        # region name
                        region_name = city.get('region_name')
                    # no city
                    else:
                        # city name
                        city_name = hotel.get('cityName')
                        # region name
                        region_name = hotel.get('region_name')
                        # zip code
                        zip_code = hotel.get('zip')
                        # latitude
                        latitude = hotel.get('latitude')
                        # longitude
                        longitude = hotel.get('longitude')
                        # check-in
                        check_in = format_check_in_out(hotel.get('checkInFrom'), hotel.get('checkInUntil'))
                        # check-out
                        check_out = format_check_in_out(hotel.get('checkOutFrom'), hotel.get('checkOutUntil'))
                        # picture url
                        p_url = hotel.get('pictureURL')
                        p_url_html = generic_url(p_url, html_format=True)
                        # website
                        website = hotel.get('hotelURL')
                        website_html = generic_url(website, html_format=True)

                        # source file name
                        device_file_paths = dict.fromkeys(device_file_paths)
                        source_file_name = unordered_list(device_file_paths)
                        # location
                        location = f"[booked][{key}]"

                        # html row
                        data_list_html.append((type_, id, hotel_name, address, city_name, region_name, zip_code, latitude, longitude,
                                               check_in, check_out, p_url_html, website_html, source_file_name, location))
                        # lava row
                        data_list.append((type_, id, hotel_name, address, city_name, region_name, zip_code, latitude, longitude,
                                               check_in, check_out, p_url, website, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

    return data_headers, (data_list, data_list_html), ' '


# booked
@artifact_processor
def booking_booked(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Created', 'datetime'),
        'Hotel Id',
        'Hotel name',
        'Full address',
        'Time zone',
        'Check-in/out (Hotel time zone)',
        'Hotel contacts',
        'Confirmation number/Pin code',
        'Total price',
        'Number of rooms',
        'Rooms',
        'Booker details',
        'Source',
        ('Attachment', 'media'),
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    artifact_info = inspect.stack()[0]
    artifact_info_name = __artifacts_v2__['booking_booked']['name']

    # rooms
    def get_rooms(rooms, html_format=False):
        result = ''
        if not bool(rooms) or not isinstance(rooms, list):
            return None

        for r in range(len(rooms)):
            room = rooms[r]
            if not bool(room):
                continue
            room_meta = []

            room_meta.append(f"Room {r} - {room.get('name', 'N/A')}")                           
            # guest name
            append_tag_value(room_meta, 'Guest name', room.get('guest_name'))
            # number of guests
            append_tag_value(room_meta, 'Number of guests', room.get('nr_guests'))
            # is cancelled
            append_tag_value(room_meta, 'Cancelled', room.get('is_cancelled'))
            # cancel date
            cancel_date = convert_plist_date_to_utc(room.get('cancel_date'))
            append_tag_value(room_meta, 'Cancel date', cancel_date)
            # room id
            append_tag_value(room_meta, 'Identifier', room.get('room_id'))
            # room photo (string)
            append_tag_value(room_meta, 'URL photo', room.get('room_photo'))
            # room photos (array)
            room_photos = room.get('room_photos', [])
            for j in range(len(room_photos)):
                # url_original
                append_tag_value(room_meta, f"URL photo #{j}", room_photos[j].get('url_original'))

            # result
            result += unordered_list(room_meta, html_format=html_format)

            # room separator
            if r < len(rooms) - 1:
                result += HTML_HORZ_RULE if html_format else LINE_BREAK + LINE_BREAK

        return result


    # Documents
    documents = seeker.search(f"*/{booking_app_identifier}/Documents/Booking #*", return_on_first_hit=False)

    # all files
    for file_found in files_found:
        file_rel_path = Path(Path(file_found).parent.name, Path(file_found).name).as_posix()
        device_file_path = get_device_file_path(file_found, seeker)

        # BookingClouds[.plist]
        if file_rel_path.endswith('BookingClouds') or file_rel_path.endswith('BookingClouds.plist'):
            try:
                device_file_paths = [ device_file_path ]

                # plist data
                plist_data = get_plist_file_content(file_found)
                if not bool(plist_data):
                    continue

                for key_root, value_root in plist_data.items():
                    if not isinstance(value_root, dict):
                        continue
                  
                # booked
                if (key_root == 'DeviceBookings') or (key_root == 'AccountBookings'):
                    # array
                    for key, value in value_root.items():
                        # created
                        created = convert_plist_date_to_utc(value.get('created_epoch'))
                        # name
                        hotel_id = value.get('hotel_id')
                        # name
                        hotel_name = value.get('hotel_name')
                        # full address + country
                        full_address = value.get('hotel_full_address')
                        # country name
                        country_name = value.get('hotel_country_name')
                        full_address = COMMA_SEP.join([full_address, country_name])
                        # time zone
                        hotel_timezone = value.get('hotel_timezone')
                        # check-in - check out
                        check_io = []
                        # check-in
                        check_in = value.get('checkin')
                        if bool(check_in):
                            tmp = f"Check-in: {check_in.strftime('%Y-%m-%d')}"
                            tmp += ' ' + format_check_in_out(value.get('checkin_from_epoch'), value.get('checkin_until_epoch'), tz=hotel_timezone)
                            check_io.append(tmp)
                        # check-out
                        check_out = value.get('checkout')
                        if bool(check_out):
                            tmp = f"Check-out: {check_out.strftime('%Y-%m-%d')}"
                            tmp += ' ' + format_check_in_out(value.get('checkout_from_epoch'), value.get('checkout_until_epoch'), tz=hotel_timezone)
                            check_io.append(tmp)
                        registration = unordered_list(check_io)
                        registration_html = unordered_list(check_io, html_format=True)
                        # hotel contacts
                        contacts = []
                        # telephone
                        append_tag_value(contacts, 'Telephone', value.get('hotel_telephone'))
                        # email
                        append_tag_value(contacts, 'Email', value.get('hotel_email'))
                        hotel_contacts = unordered_list(contacts)
                        hotel_contacts_html = unordered_list(contacts, html_format=True)
                        # confirmation number
                        conf_info = []
                        append_tag_value(conf_info, 'Confirmation number', value.get('id'))
                        # pin code
                        append_tag_value(conf_info, 'Pin code', value.get('pincode'))
                        confirm_info = unordered_list(conf_info)
                        confirm_info_html = unordered_list(conf_info, html_format=True)
                        # currency code + total price
                        total_price = f"{value.get('user_selected_currency_code')} {value.get('totalprice', '0'):.4f}"
                        # rooms (array)
                        rooms = ''
                        rooms_html = ''
                        rooms_list = value.get('room', [])
                        # number of rooms
                        number_of_rooms = len(rooms_list)
                        # rooms details
                        rooms = get_rooms(rooms_list)
                        rooms_html = get_rooms(rooms_list, html_format=True)
                        # booker details
                        booker_dets = []
                        # first name
                        append_tag_value(booker_dets, 'First name', value.get('booker_firstname'))
                        # last name
                        append_tag_value(booker_dets, 'Last name', value.get('booker_lastname'))
                        # country code                        
                        append_tag_value(booker_dets, 'Country code', value.get('booker_cc1'))
                        # email
                        append_tag_value(booker_dets, 'Email', value.get('booker_email'))
                        # credit card last digits
                        append_tag_value(booker_dets, 'Credit card last four digits', value.get('cc_number_last_digits'))
                        booker_details = unordered_list(booker_dets)
                        booker_details_html = unordered_list(booker_dets, html_format=True)           
                        # source (ios-app, web, etc.)
                        source = value.get('source')
                        # attachment (key=id)Booking
                        if bool(documents):
                            # url encode "#"???
                            att_media_ref_id = check_in_media(artifact_info, report_folder, seeker, documents, 
                                                              f"Booking #{key}.pdf")
                            att_media_item = lava_get_full_media_info(att_media_ref_id)
                            if att_media_item: device_file_paths.append(get_device_file_path(att_media_item[6], seeker))

                        # source file name
                        device_file_paths = dict.fromkeys(device_file_paths)
                        source_file_name = unordered_list(device_file_paths)
                        # location
                        location = f"[{key_root}][{key}]"

                        # html row
                        data_list_html.append((created, hotel_id, hotel_name, full_address, hotel_timezone, registration_html, hotel_contacts_html,
                                               confirm_info_html, total_price, number_of_rooms, rooms_html, booker_details_html, source, att_media_ref_id,
                                               source_file_name, location))
                        # lava row
                        data_list.append((created, hotel_id, hotel_name, full_address, hotel_timezone, registration, hotel_contacts,
                                          confirm_info, total_price, number_of_rooms, rooms, booker_details, source, att_media_ref_id,
                                          source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

    return data_headers, (data_list, data_list_html), ' '


# wish lists
@artifact_processor
def booking_wish_lists(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Added', 'datetime'),
        'Title',
        'Hotel ID',
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    artifact_info_name = __artifacts_v2__['booking_wish_lists']['name']

    # all files
    for file_found in files_found:
        file_rel_path = Path(Path(file_found).parent.name, Path(file_found).name).as_posix()
        device_file_path = get_device_file_path(file_found, seeker)

        # KeyValueStorageRecentsDomain[.plist]
        if file_rel_path.endswith('KeyValueStorageRecentsDomain') or file_rel_path.endswith('KeyValueStorageRecentsDomain.plist'):
            try:
                device_file_paths = [ device_file_path ]

                # plist data
                plist_data = get_plist_file_content(file_found)
                if not bool(plist_data):
                    continue

                # wish lists
                wish_lists = plist_data.get('wishlists')
                # array
                for i in range(0, len(wish_lists)):
                    wish = wish_lists[i]

                    # list name
                    list_name = wish.get('name')
                    # hotels
                    hotels = wish.get('hotels')
                    for j in range(0, len(hotels)):
                        hotel = hotels[j]

                        # added
                        added = convert_plist_date_to_utc(hotel.get('date'))
                        # id
                        id = hotel['id']

                        # source file name
                        device_file_paths = dict.fromkeys(device_file_paths)
                        source_file_name = unordered_list(device_file_paths)
                        # location
                        location = [ f"[wishlists][{i}]" ]
                        location.append(f"[wishlists][{i}][hotels][{j}]")
                        location = COMMA_SEP.join(location)

                        # html row
                        data_list_html.append((added, list_name, id, source_file_name, location))
                        # lava row
                        data_list.append((added, list_name, id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

    return data_headers, (data_list, data_list_html), ' '


# viewed
@artifact_processor
def booking_viewed(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Last viewed', 'datetime'),
        'Hotel type',
        'Hotel Id',
        'Hotel name',
        'Address',
        'City',
        'Region',
        'Zip code',
        'Latitude',
        'Longitude',
        'Image URL',
        'Website',
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    artifact_info_name = __artifacts_v2__['booking_viewed']['name']

    # all files
    for file_found in files_found:
        file_rel_path = Path(Path(file_found).parent.name, Path(file_found).name).as_posix()
        device_file_path = get_device_file_path(file_found, seeker)

        # KeyValueStorageRecentsDomain[.plist]
        if file_rel_path.endswith('KeyValueStorageRecentsDomain') or file_rel_path.endswith('KeyValueStorageRecentsDomain.plist'):
            try:
                device_file_paths = [ device_file_path ]

                # plist data
                plist_data = get_plist_file_content(file_found)
                if not bool(plist_data):
                    continue

                # viewed
                viewed = plist_data.get('viewed', {})
                # dict
                for key, value in viewed.items():
                    # hotel
                    hotel = value.get('hotel')

                    # last viewed
                    last_viewed = convert_plist_date_to_utc(hotel.get('lastViewed'))
                    # hotel type
                    type_ = hotel_type_names(hotel.get('hotel_type'))
                    # key=hotel id
                    id = hotel.get('hotel_id')
                    # hotel name
                    hotel_name = hotel.get('name')
                    # address
                    address = hotel.get('address')
                    # city
                    city = hotel.get('city')
                    if bool(city):
                        # city name
                        city_name = city.get('string_')
                        # region
                        region_name = city.get('region_name')
                    # no city
                    else:
                        # city name
                        city_name = hotel.get('cityName')
                        # region name
                        region_name = hotel.get('region_name')
                    # zip code
                    zip_code = hotel.get('zip')
                    # latitude
                    latitude = hotel.get('latitude')
                    # longitude
                    longitude = hotel.get('longitude')
                    # picture url
                    p_url = hotel.get('pictureURL')
                    p_url_html = generic_url(p_url, html_format=True)
                    # website
                    website = hotel.get('hotelURL')
                    website_html = generic_url(website, html_format=True)

                    # source file name
                    device_file_paths = dict.fromkeys(device_file_paths)
                    source_file_name = unordered_list(device_file_paths)
                    # location
                    location = f"[viewed][{key}]"

                    # html row
                    data_list_html.append((last_viewed, type_, id, hotel_name, address, city_name, region_name, zip_code, latitude, longitude,
                                           p_url_html, website_html, source_file_name, location))
                    # lava row
                    data_list.append((last_viewed, type_, id, hotel_name, address, city_name, region_name, zip_code, latitude, longitude,
                                      p_url, website, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

    return data_headers, (data_list, data_list_html), ' '


# notifications
@artifact_processor
def booking_notifications(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Timestamp', 'datetime'),
        'Identifier',
        'Title',
        'Message',
        'Viewed',
        'Deleted',
        'Action ID',
        'Action arguments',
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    file_found = get_file_path(files_found, "NotificationsModel.sqlite")
    device_file_path = get_device_file_path(file_found, seeker)

    query = '''
    SELECT
        ROWID,
        (ZDATE + 978307200) AS "timestamp",
        ZIDENTIFIER,
        ZTITLE,
        ZBODY,
        ZVIEWED,
        ZLOCALLYDELETED,
        ZACTIONIDENTIFIER,
        ZACTIONARGUMENTS
    FROM ZNOTIFICATION
    '''

    db_records = get_sqlite_db_records(file_found, query)
    for record in db_records:
        device_file_paths = [ device_file_path ]

        # timestamp
        timestamp = convert_unix_ts_to_utc(record[1])
        # identifier
        identifier = record[2]
        # title
        title = record[3]
        # body
        body = record[4]
        # is_viewed
        is_viewed = bool(record[5])
        # is_deleted
        is_deleted = bool(record[6])
        # action identifier
        action_identifier = record[7]
        # arguments
        arguments = get_plist_content(record[8])

        # location
        location = f""

        # source file name
        device_file_paths = dict.fromkeys(device_file_paths)
        source_file_name = unordered_list(device_file_paths)
        source_file_name_html = unordered_list(device_file_paths, html_format=True)
        # location
        location = f"ZNOTIFICATION (ROWID: {record[0]})"

        # html row
        data_list_html.append((timestamp, identifier, title, body, is_viewed, is_deleted, action_identifier, arguments, source_file_name_html, location))
        # lava row
        data_list.append((timestamp, identifier, title, body, is_viewed, is_deleted, action_identifier, arguments, source_file_name, location))

    return data_headers, (data_list, data_list_html), ' '


# flights searched
@artifact_processor
def booking_flights_searched(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Last updated', 'datetime'),
        'Start date',
        'Return date',
        'Direct flight',
        'Search type',
        'Cabin class',
        'Source airports',
        'Destination airports',
        'Routes',
        "Travellers' details",
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    artifact_info_name = __artifacts_v2__['booking_flights_searched']['name']


    # traveller details
    def get_traveller_details(traveller_details, html_format=False):
        if not bool(traveller_details) or not isinstance(traveller_details, dict):
            return None
        travellers_meta = []

        travellers_details = params.get('travellersDetails', {})
        # adults count
        append_tag_value(travellers_meta, 'Adults count', travellers_details.get('adultsCount'))
        # children count
        append_tag_value(travellers_meta, 'Children count', travellers_details.get('childrenCount'))
        # children ages (array of int)
        children_ages = travellers_details.get('childrenAges', {})
        append_tag_value(travellers_meta, 'Children ages', COMMA_SEP.join([str(x) for x in children_ages]))

        return unordered_list(travellers_meta, html_format=html_format)


    # airports details
    def get_airports(airports, section_name='Airport', html_format=False):
        result = ''
        if not bool(airports) or not isinstance(airports, list):
            return None
        
        for a in range(len(airports)):
            airport = airports[a]
            if not bool(airport):
                continue
            airport_meta = []

            airport_meta.append(f"{section_name} {a} - {airport.get('name', 'N/A')}")
            # city name
            append_tag_value(airport_meta, 'City', airport.get('cityName'))
            # region name
            append_tag_value(airport_meta, 'Region', airport.get('regionName'))
            # country name
            append_tag_value(airport_meta, 'Country', airport.get('coutryName'))
            # type
            append_tag_value(airport_meta, 'Type', airport.get('type'))
            # code
            append_tag_value(airport_meta, 'Code', airport.get('code'))
            # selected
            append_tag_value(airport_meta, 'Selected', airport.get('selected'))
                                
            # result
            result += unordered_list(airport_meta, html_format=html_format)

            # airport separator
            if a < len(airports) - 1:
                result += HTML_HORZ_RULE if html_format else LINE_BREAK + LINE_BREAK

        return result


    # routes
    def get_routes(routes, html_format=False):
        result = ''
        if not bool(routes) or not isinstance(routes, list):
            return None

        for r in range(len(routes)):
            route = routes[r]
            if not bool(route):
                continue
            routes_meta = []
            
            # start date
            start_date = None
            try: start_date = date(route.get('startYear'), route.get('startMonth'), route.get('startDay'))
            except: pass
            if not bool(start_date):
                continue

            routes_meta.append(f"Route {r} - {start_date}")
            # sources airports
            routes_meta.append(get_airports(route.get('sourceAirports'), section_name='Source airport'))
            # destinations airports
            routes_meta.append(get_airports(route.get('destinationAirports'), section_name='Destination airport'))

            # result
            result += unordered_list(routes_meta, html_format=html_format)

            # routes separator
            if r < len(routes) - 1:
                result += HTML_HORZ_RULE if html_format else LINE_BREAK + LINE_BREAK

        return result


    # all files
    for file_found in files_found:
        file_rel_path = Path(Path(file_found).parent.name, Path(file_found).name).as_posix()
        device_file_path = get_device_file_path(file_found, seeker)

        # flight_rs_v2
        if file_rel_path.endswith('flight_rs_v2'):
            try:
                device_file_paths = [ device_file_path ]

                # json data
                json_data = get_json_file_content(file_found)
                if not bool(json_data):
                    continue

                # flights (array)
                flights = json_data.get('value')
                if not bool(flights):
                    continue

                # array
                for i in range(0, len(flights)):
                    # flight
                    flight = flights[i]

                    # last updated
                    last_updated = convert_iso8601_to_utc(flight.get('lastUpdated'))
                    # parameters
                    params = flight.get('parameters', {}).get('searchOptionModel', {})
                    # start date
                    try: start_date = date(params.get('startYear'), params.get('startMonth'), params.get('startDay'))
                    except: pass
                    # return date (returnType=ONEWAY-> returnYear, returnMonth, returnDay are Null)
                    try: return_date = date(params.get('returnYear'), params.get('returnMonth'), params.get('returnDay'))
                    except: pass
                    # direct flight
                    direct_flight = params.get('direct')
                    # search type
                    search_type = params.get('searchType')
                    # cabin class
                    cabin_class = params.get('cabin')
                    # source airports
                    source_airports = get_airports(params.get('sourceAirports'))
                    source_airports_html = get_airports(params.get('sourceAirports'), html_format=True)
                    # destination airports
                    destination_airports = get_airports(params.get('destinationAirports'))
                    destination_airports_html = get_airports(params.get('destinationAirports'), html_format=True)
                    # routes
                    routes = get_routes(params.get('routes'))
                    routes_html = get_routes(params.get('routes'), html_format=True)
                    # travellers' details
                    travellers_details = get_traveller_details(params.get('travellersDetails'))
                    travellers_details_html = get_traveller_details(params.get('travellersDetails'), html_format=True)

                    # source file name
                    device_file_paths = dict.fromkeys(device_file_paths)
                    source_file_name = unordered_list(device_file_paths)
                    source_file_name_html = unordered_list(device_file_paths, html_format=True)
                    # location
                    location = f"[value][{i}]"

                    # html row
                    data_list_html.append((last_updated, start_date, return_date, direct_flight, search_type, cabin_class, source_airports_html,
                                           destination_airports_html, routes_html, travellers_details_html, source_file_name_html, source_file_name, location))
                    # lava row
                    data_list.append((last_updated, start_date, return_date, direct_flight, search_type, cabin_class, source_airports,
                                      destination_airports, routes, travellers_details, source_file_name_html, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

    return data_headers, (data_list, data_list_html), ' '
