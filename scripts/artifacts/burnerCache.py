__artifacts_v2__ = {
    "burnerCache_preferences": {
        "name": "Preferences",
        "description": "Parses and extract Burner Cache Preferences",
        "author": "@djangofaiola",
        "version": "0.3",
        "creation_date": "2024-03-05",
        "last_update_date": "2025-05-02",
        "requirements": "none",
        "category": "Burner Cache",
        "notes": ("https://djangofaiola.blogspot.com",
                  "App version tested: 4.0.18, 4.3.3, 5.3.8, 5.4.11"),
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Preferences/com.adhoclabs.burner.plist'),
        "output_types": [ "none" ],
        "artifact_icon": "settings"
    },
    "burnerCache_accounts": {
        "name": "Accounts",
        "description": "Parses and extract Burner Cache Accounts",
        "author": "@djangofaiola",
        "version": "0.3",
        "creation_date": "2024-03-05",
        "last_update_date": "2025-05-02",
        "requirements": "none",
        "category": "Burner Cache",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/com.adhoclabs.burner/Cache.db*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Source file name", "Location" ],
        "artifact_icon": "user"
    },
    "burnerCache_contacts": {
        "name": "Contacts",
        "description": "Parses and extract Burner Cache Contacts",
        "author": "@djangofaiola",
        "version": "0.3",
        "creation_date": "2024-03-05",
        "last_update_date": "2025-05-02",
        "requirements": "none",
        "category": "Burner Cache",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/com.adhoclabs.burner/Cache.db*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Source file name", "Location" ],
        "artifact_icon": "users"
    },
    "burnerCache_numbers": {
        "name": "Numbers",
        "description": "Parses and extract Burner Cache Numbers",
        "author": "@djangofaiola",
        "version": "0.3",
        "creation_date": "2024-03-05",
        "last_update_date": "2025-05-02",
        "requirements": "none",
        "category": "Burner Cache",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/com.adhoclabs.burner/Cache.db*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Source file name", "Location" ],
        "artifact_icon": "phone"
    },
    "burnerCache_messages": {
        "name": "Messages",
        "description": "Parses and extract Burner Cache Messages",
        "author": "@djangofaiola",
        "version": "0.3",
        "creation_date": "2024-03-05",
        "last_update_date": "2025-05-02",
        "requirements": "none",
        "category": "Burner Cache",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/com.adhoclabs.burner/Cache.db*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Media URL", "Source file name", "Location" ],
        "artifact_icon": "message-circle",
        "data_views": {
            "chat": {
                "directionSentValue": "Outgoing",
                "threadDiscriminatorColumn": "Thread",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "timeColumn": "Sent",
                "senderColumn": "Sender",
                "mediaColumn": "Media"
            }
        }
    }
}

import inspect
from urllib.parse import urlparse, urlunparse
import json
import re
import sqlite3
from pathlib import Path
from scripts.ilapfuncs import get_file_path, get_plist_file_content, open_sqlite_db_readonly, lava_get_full_media_info, \
    convert_unix_ts_to_utc, check_in_media, check_in_embedded_media, artifact_processor, logfunc


# burner app id
burner_app_identifier = None
# <id, phone number (display name)>
burner_uid_map = {}
# constants
LINE_BREAK = '\n'
COMMA_SEP = ', '
HTML_LINE_BREAK = '<br>'
HTML_HORZ_RULE = '<hr>'
# Cache.db query
BURNER_CACHE_DB_QUERY = '''
    SELECT
        crd.entry_ID,
        cr.request_key,
        crd.isDataOnFS,
        crd.receiver_data
    FROM cfurl_cache_response AS "cr"
    LEFT JOIN cfurl_cache_receiver_data AS "crd" ON (cr.entry_ID = crd.entry_ID)
    WHERE cr.request_key REGEXP "{0}"
    '''


def get_sqlite_db_records_regexpr(file_path, query, attach_query=None, regexpr=None):
    file_path = str(file_path)
    db = open_sqlite_db_readonly(file_path)
    if not bool(db):
        return None

    try:
        # regexp() user function
        if bool(regexpr):
            db.create_function('regexp', 2, lambda x, y: 1 if re.search(x,y) else 0)
    
        cursor = db.cursor()
        if bool(attach_query):
            cursor.execute(attach_query)
        cursor.execute(query)
        records = cursor.fetchall()
        return records

    except sqlite3.OperationalError as e:
        logfunc(f"Error with {file_path}:")
        logfunc(f" - {str(e)}")

    except sqlite3.ProgrammingError as e:
        logfunc(f"Error with {file_path}:")
        logfunc(f" - {str(e)}")


def get_json_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        logfunc(f"Error reading file {file_path}: {str(e)}")
        return None


def get_json_content(data):
    try:
        return json.loads(data)
    except Exception as e:
        logfunc(f"Unexpected error reading json data: {str(e)}")
        return {}


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


def get_cache_db_fs_path(data, file_found, seeker):
    if bool(data):
        # */<GUID>/Library/Caches/com.adhoclabs.burner/fsCachedData/<data>
        filter = Path('*').joinpath(*Path(file_found).parts[-5:-1], 'fsCachedData', data)
        json_file = seeker.search(filter, return_on_first_hit=True)
        return json_file
    else:
        return None


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


# preferences
@artifact_processor
def burnerCache_preferences(files_found, report_folder, seeker, wrap_text, timezone_offset):

    source_path = None
    global burner_app_identifier

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

            # Library/Preferences/com.adhoclabs.burner.plist
            burner_app_identifier = Path(file_found).parents[2].name

        except Exception as e:
            logfunc(f"Error: {str(e)}")
            pass

    # return empty
    return (), [], source_path


# accounts
@artifact_processor
def burnerCache_accounts(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Last updated', 'datetime'),
        ('Created', 'datetime'),
        ('Phone number', 'phonenumber'),
        'Country code',
        'Carrier name',
        'Number of burners',
        'User ID',
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    artifact_info_name = __artifacts_v2__['burnerCache_accounts']['name']
    file_found = get_file_path(files_found, "Cache.db")
    device_file_path = get_device_file_path(file_found, seeker)

    # get account
    def get_account(account):
        acc_ref = account.get('user')
        if not bool(acc_ref):
            acc_ref = account

        # last updated date
        last_updated = convert_unix_ts_to_utc(acc_ref.get('lastUpdatedDate'))
        # date created
        created = convert_unix_ts_to_utc(acc_ref.get('dateCreated'))
        # phone number
        phone_number = acc_ref.get('phoneNumber', '')
        # country code
        country_code = acc_ref.get('countryCode')
        # carrier name
        carrier_name = acc_ref.get('carrierName')
        # total number burners
        total_number_burners = acc_ref.get('totalNumberBurners')
        # user id
        user_id = acc_ref.get('id')
        if bool(user_id):
            burner_uid_map[user_id] = phone_number

        # out values
        return last_updated, created, phone_number, country_code, carrier_name, total_number_burners, user_id


    query = BURNER_CACHE_DB_QUERY.format(r'https:\/\/phoenix\.burnerapp\.com(\/v\d)?(\/register(\/phone)?$|\/user\/[a-fA-F\d-]{36}\/token)')
    db_records = get_sqlite_db_records_regexpr(file_found, query, regexpr=True)
    for record in db_records:
        db_device_file_paths = [ device_file_path ]

        # from file?
        isDataOnFS = bool(record[2])
        # from FS
        if isDataOnFS:
            fs_cached_data_path = get_cache_db_fs_path(record[3], file_found, seeker)
            json_data = get_json_file_content(fs_cached_data_path)
            if bool(fs_cached_data_path): db_device_file_paths.append(get_device_file_path(fs_cached_data_path, seeker))
        # from BLOB
        else:
            json_data = get_json_content(record[3])

        device_file_paths = db_device_file_paths

        # accounts
        if isinstance(json_data, (list, tuple)):
            for i in range(0, len(json_data)):
                device_file_paths = db_device_file_paths

                account = json_data[i]
                if not bool(account):
                    continue

                # account
                last_updated, created, phone_number, country_code, carrier_name, total_number_burners, user_id = get_account(account)
        
                # source file name
                device_file_paths = dict.fromkeys(device_file_paths)
                source_file_name = unordered_list(device_file_paths)
                source_file_name_html = unordered_list(device_file_paths, html_format=True)
                # location
                location = [ f"cfurl_cache_receiver_data (entry_ID: {record[0]})" ]
                location.append(f"{record[3]}[{i}]" if isDataOnFS else f"receiver_data[{i}]")
                location = COMMA_SEP.join(location)

                # html row
                data_list_html.append((last_updated, created, phone_number, country_code, carrier_name, total_number_burners, user_id, source_file_name_html, location))
                # lava row
                data_list.append((last_updated, created, phone_number, country_code, carrier_name, total_number_burners, user_id, source_file_name, location))
        # account
        elif isinstance(json_data, dict):
            # account
            last_updated, created, phone_number, country_code, carrier_name, total_number_burners, user_id = get_account(json_data)
            
            # source file name
            device_file_paths = dict.fromkeys(device_file_paths)
            source_file_name = unordered_list(device_file_paths)
            source_file_name_html = unordered_list(device_file_paths, html_format=True)
            # location
            location = [ f"cfurl_cache_receiver_data (entry_ID: {record[0]})" ]
            location.append(f"{record[3]}" if isDataOnFS else f"receiver_data")
            location = COMMA_SEP.join(location)

            # html row
            data_list_html.append((last_updated, created, phone_number, country_code, carrier_name, total_number_burners, user_id, source_file_name_html, location))
            # lava row
            data_list.append((last_updated, created, phone_number, country_code, carrier_name, total_number_burners, user_id, source_file_name, location))

    return data_headers, (data_list, data_list_html), ' '


# contacts
@artifact_processor
def burnerCache_contacts(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Created', 'datetime'),
        ('Phone number', 'phonenumber'),
        'Full name',
        'Notes',
        'Verified',
        'Blocked',
        'Muted',
        'Burner IDs',
        'Contact ID',
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    artifact_info_name = __artifacts_v2__['burnerCache_contacts']['name']
    file_found = get_file_path(files_found, "Cache.db")
    device_file_path = get_device_file_path(file_found, seeker)

    # get contact
    def get_contact(contact):
        # date created
        created = convert_unix_ts_to_utc(contact.get('dateCreated'))
        # display name
        display_name = contact.get('name')
        # phone number
        phone_number = contact.get('phoneNumber')
        if bool(phone_number):
            burner_uid_map[phone_number] = f"{phone_number} ({display_name})" if bool(display_name) else phone_number            
        # other phones ???
        # notes
        notes = contact.get('text')
        # verified
        verified = 'Yes' if bool(contact.get('verified')) else 'No'
        # blocked
        blocked = 'Yes' if bool(contact.get('blocked')) else 'No'
        # muted
        muted = 'Yes' if bool(contact.get('muted')) else 'No'
        # images ???
        images = contact.get('images')
        if bool(images):
            # image = images.get('full', '')
            image = ''
            image_url = ''
            #thumbnail = images.get('thumbnail', '')
            thumbnail = ''
            thumbnail_url = ''
        else:
            image = ''
            image_url = ''
            thumbnail = ''
            thumbnail_url = ''
        # burner ids
        burner_ids = COMMA_SEP.join(contact.get('burnerIds', []))       
        # contact id
        contact_id = contact.get('id')
        if bool(contact_id):
            burner_uid_map[contact_id] = f"{phone_number} ({display_name})" if bool(display_name) else phone_number

        # out values
        return created, phone_number, display_name, notes, verified, blocked, muted, burner_ids, contact_id


    query = BURNER_CACHE_DB_QUERY.format(r'https:\/\/phoenix\.burnerapp\.com(\/v\d)?\/user\/[a-fA-F\d-]{36}\/contacts\?.+')
    db_records = get_sqlite_db_records_regexpr(file_found, query, regexpr=True)
    for record in db_records:
        db_device_file_paths = [ device_file_path ]

        # from file?
        isDataOnFS = bool(record[2])
        # from FS
        if isDataOnFS:
            fs_cached_data_path = get_cache_db_fs_path(record[3], file_found, seeker)
            json_data = get_json_file_content(fs_cached_data_path)
            if bool(fs_cached_data_path): db_device_file_paths.append(get_device_file_path(fs_cached_data_path, seeker))
        # from BLOB
        else:
            json_data = get_json_content(record[3])

        device_file_paths = db_device_file_paths

        # contacts
        if isinstance(json_data, (list, tuple)):
            for i in range(0, len(json_data)):
                device_file_paths = db_device_file_paths

                contact = json_data[i]
                if not bool(contact):
                    continue

                # contact
                created, phone_number, display_name, notes, verified, blocked, muted, burner_ids, contact_id = get_contact(contact)

                # source file name
                device_file_paths = dict.fromkeys(device_file_paths)
                source_file_name = unordered_list(device_file_paths)
                source_file_name_html = unordered_list(device_file_paths, html_format=True)
                # location
                location = [ f"cfurl_cache_receiver_data (entry_ID: {record[0]})" ]
                location.append(f"{record[3]}[{i}]" if isDataOnFS else f"receiver_data[{i}]")
                location = COMMA_SEP.join(location)

                # html row
                data_list_html.append((created, phone_number, display_name, notes, verified, blocked, muted, burner_ids, contact_id, source_file_name_html, location))
                # lava row
                data_list.append((created, phone_number, display_name, notes, verified, blocked, muted, burner_ids, contact_id, source_file_name, location))

        # contact
        elif isinstance(json_data, dict):
            created, phone_number, display_name, notes, verified, blocked, muted, burner_ids, contact_id = get_contact(json_data)
            
            # source file name
            device_file_paths = dict.fromkeys(device_file_paths)
            source_file_name = unordered_list(device_file_paths)
            source_file_name_html = unordered_list(device_file_paths, html_format=True)
            # location
            location = [ f"cfurl_cache_receiver_data (entry_ID: {record[0]})" ]
            location.append(f"{record[3]}" if isDataOnFS else f"receiver_data")
            location = COMMA_SEP.join(location)

            # html row
            data_list_html.append((created, phone_number, display_name, notes, verified, blocked, muted, burner_ids, contact_id, source_file_name_html, location))
            # lava row
            data_list.append((created, phone_number, display_name, notes, verified, blocked, muted, burner_ids, contact_id, source_file_name, location))

    return data_headers, (data_list, data_list_html), ' '


# numbers
@artifact_processor
def burnerCache_numbers(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Created', 'datetime'),
        'Burner number',
        'Display name',
        'Subscription Expires',
        'Version',
        'Notifications',
        'Inbound caller ID',
        'In-App calling (VoIP)',
        'Auto-replay enabled',
        'Auto-reply message',
        'Remaining/Total minutes',
        'Remaining/Total messages',
        ('Phone number', 'phonenumber'),
        'User ID',
        'Burner ID',
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    artifact_info_name = __artifacts_v2__['burnerCache_numbers']['name']
    file_found = get_file_path(files_found, "Cache.db")
    device_file_path = get_device_file_path(file_found, seeker)


    # get number
    def get_number(number):
        # burner number
        burner_number = number.get('phoneNumber')
        if not bool(burner_number):
            burner_number = number.get('phoneNumberId')
        # user id
        user_id = number.get('userId')
        if not bool(user_id):
            # https://phoenix.burnerapp.com/v3/user/<user_id>/burners
            user_id = str(record[1]).split('/')[-2]
        user_phone_number = burner_uid_map.get(user_id)
        # version
        version = number.get('version')
        # date created
        created = convert_unix_ts_to_utc(number.get('dateCreated'))
        # subscription expires
        expires = convert_unix_ts_to_utc(number.get('expirationDate'))
        # entitlements
        entitlements = number.get('entitlements')
        if bool(entitlements):
            # remaining minutes/total minutes
            rt_minutes = f"{entitlements.get('remainingMinutes', 0)}/{entitlements.get('totalMinutes', 0)}"
            # remaining messages/total messages
            rt_texts = f"{entitlements.get('remainingTexts', 0)}/{entitlements.get('totalTexts', 0)}"
        else:
            # remaining minutes/total minutes
            rt_minutes = f"{number.get('remainingMinutes', 0)}/{number.get('totalMinutes', 0)}"
            # remaining messages/total messages
            rt_texts = f"{number.get('remainingTexts', 0)}/{number.get('totalTexts', 0)}"
        # settings
        settings = number.get('settings')
        if bool(settings):
            # display name
            display_name = settings.get('name')
            # notifications
            notifications = 'On' if settings.get('notificationsEnabled') == True else 'Off'
            # inbound caller id
            inbound_caller_id = 'Burner Number' if settings.get('incomingCallNumberDisplay', 'BurnerNumber') == 'BurnerNumber' else 'Caller Number'
            # voip
            voip = 'VoIP' if settings.get('voipEnabled') == True else 'Standard Voice'
            # auto-reply message
            auto_reply_message = settings.get('autoReplyMessage')
            if bool(auto_reply_message):
                # auto-reply enabled
                auto_reply_enabled = 'Yes' if auto_reply_message.get('active') == True else 'No'
                # auto-reply message
                auto_reply_text = auto_reply_message.get('text')
        else:
            # display name
            display_name = number.get('name')
            # notifications
            notifications = 'On' if number.get('notifications') == True else 'Off'
            # inbound caller id
            inbound_caller_id = 'Caller Number' if number.get('callerIdEnabled') == True else 'Burner Number'
            # voip
            voip = 'VoIP' if number.get('useSip') == True else 'Standard Voice'
            # auto-reply enabled
            auto_reply_enabled = 'Yes' if number.get('autoReplyActive') == True else 'No'
            # auto-reply message
            auto_reply_text = number.get('autoReplyText')
        # burned id
        burner_id = number.get('id')
        if bool(burner_id):
            burner_uid_map[burner_id] = f"{burner_number} ({display_name})" if bool(display_name) else burner_number

        # out values
        return created, burner_number, display_name, expires, version, notifications, inbound_caller_id, voip, \
            auto_reply_enabled, auto_reply_text, rt_minutes, rt_texts, user_phone_number, user_id, burner_id


    query = BURNER_CACHE_DB_QUERY.format(r'https:\/\/phoenix\.burnerapp\.com(\/v\d)?\/user\/[a-fA-F\d-]{36}\/burners(\/[a-fA-F\d-]{36})?$')
    db_records = get_sqlite_db_records_regexpr(file_found, query, regexpr=True)
    for record in db_records:
        db_device_file_paths = [ device_file_path ]

        # from file?
        isDataOnFS = bool(record[2])
        # from FS
        if isDataOnFS:
            fs_cached_data_path = get_cache_db_fs_path(record[3], file_found, seeker)
            json_data = get_json_file_content(fs_cached_data_path)
            if bool(fs_cached_data_path): db_device_file_paths.append(get_device_file_path(fs_cached_data_path, seeker))
        # from BLOB
        else:
            json_data = get_json_content(record[3])

        device_file_paths = db_device_file_paths

        # numbers
        if isinstance(json_data, (list, tuple)):
            for i in range(0, len(json_data)):
                device_file_paths = db_device_file_paths

                number = json_data[i]
                if not bool(number):
                    continue

                # number
                created, burner_number, display_name, expires, version, notifications, inbound_caller_id, voip, auto_reply_enabled, auto_reply_text, \
                rt_minutes, rt_texts, user_phone_number, user_id, burner_id = get_number(number)

                # source file name
                device_file_paths = dict.fromkeys(device_file_paths)
                source_file_name = unordered_list(device_file_paths)
                source_file_name_html = unordered_list(device_file_paths, html_format=True)
                # location
                location = [ f"cfurl_cache_receiver_data (entry_ID: {record[0]})" ]
                location.append(f"{record[3]}[{i}]" if isDataOnFS else f"receiver_data[{i}]")
                location = COMMA_SEP.join(location)

                # html row
                data_list_html.append((created, burner_number, display_name, expires, version, notifications, inbound_caller_id, voip, auto_reply_enabled, auto_reply_text,
                                       rt_minutes, rt_texts, user_phone_number, user_id, burner_id, source_file_name_html, location))
                # lava row
                data_list.append((created, burner_number, display_name, expires, version, notifications, inbound_caller_id, voip, auto_reply_enabled, auto_reply_text,
                                  rt_minutes, rt_texts, user_phone_number, user_id, burner_id, source_file_name, location))

        # number
        elif isinstance(json_data, dict):
            created, burner_number, display_name, expires, version, notifications, inbound_caller_id, voip, auto_reply_enabled, auto_reply_text, \
            rt_minutes, rt_texts, user_phone_number, user_id, burner_id = get_number(json_data)
            
            # source file name
            device_file_paths = dict.fromkeys(device_file_paths)
            source_file_name = unordered_list(device_file_paths)
            source_file_name_html = unordered_list(device_file_paths, html_format=True)
            # location
            location = [ f"cfurl_cache_receiver_data (entry_ID: {record[0]})" ]
            location.append(f"{record[3]}" if isDataOnFS else f"receiver_data")
            location = COMMA_SEP.join(location)

            # html row
            data_list_html.append((created, burner_number, display_name, expires, version, notifications, inbound_caller_id, voip, auto_reply_enabled, auto_reply_text,
                                   rt_minutes, rt_texts, user_phone_number, user_id, burner_id, source_file_name_html, location))
            # lava row
            data_list.append((created, burner_number, display_name, expires, version, notifications, inbound_caller_id, voip, auto_reply_enabled, auto_reply_text,
                              rt_minutes, rt_texts, user_phone_number, user_id, burner_id, source_file_name, location))

    return data_headers, (data_list, data_list_html), ' '


# messages
@artifact_processor
def burnerCache_messages(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        'Thread',
        ('Sent', 'datetime'),
        'Direction',
        'Read',
        'Sender',
        'Recipient',
        'Message',
        'Message type',
        ('Media', 'media', 'height: 96px; border-radius: 5%;'),
        'Media URL',
        'Message ID',
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    artifact_info = inspect.stack()[0]
    artifact_info_name = __artifacts_v2__['burnerCache_messages']['name']
    file_found = get_file_path(files_found, "Cache.db")
    device_file_path = get_device_file_path(file_found, seeker)

    # get message
    def get_message(message):
        # date created
        created = convert_unix_ts_to_utc(message.get('dateCreated'))
        # read
        read = 'Read' if bool(message.get('read')) else 'Not read'
        # state
        state = message.get('state')
        # direction
        dir_val = message.get('direction')
        if dir_val == 1:
            direction = 'Incoming'
        elif dir_val == 2:
            direction = 'Outgoing'
        else:
            direction = dir_val
        # burner id
        burner_id = message.get('burnerId', '')
        # burner number
        burner_number = burner_uid_map.get(burner_id)
        # contact id
        contact_id = message.get('contactId', '')
        contact_temp = burner_uid_map.get(contact_id)
        contact_phone_number = contact_temp if bool(contact_temp) else message.get('contactPhoneNumber')       
        # sender, recipient
        if dir_val == 1:
            sender = contact_phone_number
            recipient = burner_number
        else:
            sender = burner_number
            recipient = contact_phone_number
        # body
        if (dir_val == 1) and (state == 3):
            body = 'Completed incoming call'
        elif (dir_val == 2) and (state == 3):
            body = 'Completed outgoing call'
        elif (dir_val == 1) and (state == 4):
            body = 'Missed incoming call'
        elif (dir_val == 2) and (state == 4):
            body = 'Missed outgoing call'
        elif (dir_val == 1) and (state == 5):
            body = 'Missed incoming call with voicemail'
        elif (dir_val == 2) and (state == 5):
            body = 'Missed outgoing call with voicemail'
        else:
            body = message.get('message')
        # asset url
        media_ref_id = None
        media_url = message.get('assetUrl')
        voice_url = message.get('voiceUrl')
        ref_url = media_url if bool(media_url) else voice_url
        if bool(ref_url):
            for m_record in media_records:
                if m_record[1] != ref_url:
                    continue
                # isDataOnFS
                if bool(m_record[2]):
                    media_ref_id = check_in_media(seeker, m_record[3], artifact_info, already_extracted=media_files)
                else:
                    media_ref_id = check_in_embedded_media(seeker, file_found, m_record[3], artifact_info)
                media_item = lava_get_full_media_info(media_ref_id)
                if media_item: device_file_paths.append(get_device_file_path(media_item[5], seeker))
                break
        # message type
        message_type = message.get('messageType')
        if  (message_type == 1) and (state in (3, 4)):
            message_type = 'Call'
        elif  (message_type == 1) and (state == 5):
            message_type = 'Voicemail'
        elif  (message_type == 2) and not bool(media_url):
            message_type = 'Text'
        elif  (message_type == 2):
            message_type = 'Picture'
        # message id
        message_id = message.get('id')

        # out values
        return contact_phone_number, created, direction, read, sender, recipient, body, message_type, media_ref_id, ref_url, message_id


    # get conversation
    def get_conversation(conversation):
        # date created
        created = convert_unix_ts_to_utc(conversation.get('dateCreated'))
        # read
        read = 'Read' if bool(conversation.get('read')) else 'Not read'
        # state
        state = conversation.get('state')
        # direction
        dir_val = conversation.get('direction')
        if dir_val == 'Inbound':
            direction = 'Incoming'
        elif dir_val == 'Outbound':
            direction = 'Outgoing'
        else:
            direction = dir_val
        # burner id
        burner_id = conversation.get('burnerId', '')
        # burner number
        burner_number = burner_uid_map.get(burner_id)
        # contact phone number
        contact_phone_number = conversation.get('conversation', {}).get('conversationId')
        contact_temp = burner_uid_map.get(contact_phone_number)
        if bool(contact_temp): contact_phone_number = contact_temp
        # sender, recipient
        if dir_val == 'Inbound':
            sender = contact_phone_number
            recipient = burner_number
        else:
            sender = burner_number
            recipient = contact_phone_number
        # body
        if (dir_val == 'Inbound') and (state == 'CallCompleted'):
            body = 'Completed incoming call'
        elif (dir_val == 'Outbound') and (state == 'CallCompleted'):
            body = 'Completed outgoing call'
        elif (dir_val == 'Inbound') and (state == 'CallMissed'):
            body = 'Missed incoming call'
        elif (dir_val == 'Outbound') and (state == 'CallMissed'):
            body = 'Missed outgoing call'
        elif (dir_val == 'Inbound') and (state == 'Voicemail'):
            body = 'Missed incoming call with voicemail'
        elif (dir_val == 'Outbound') and (state == 'Voicemail'):
            body = 'Missed outgoing call with voicemail'
        else:
            body = conversation.get('text')
        # media url
        media_ref_id = None
        media_url = conversation.get('mediaUrl')
        voice_url = conversation.get('voicemail', {}).get('audioUrl')
        ref_url = media_url if bool(media_url) else voice_url
        if bool(ref_url):
            for m_record in media_records:
                if m_record[1] != ref_url:
                    continue
                # isDataOnFS
                if bool(m_record[2]):
                    media_ref_id = check_in_media(seeker, m_record[3], artifact_info, already_extracted=media_files)
                else:
                    media_ref_id = check_in_embedded_media(seeker, file_found, m_record[3], artifact_info)
                media_item = lava_get_full_media_info(media_ref_id)
                if media_item: device_file_paths.append(get_device_file_path(media_item[5], seeker))
                break
        # message type
        message_type = conversation.get('messageType')
        if  message_type == 'Voice':
            message_type = 'Voicemail' if state == 'Voicemail' else 'Call'
        elif  (message_type == 'Text') and not bool(media_url):
            message_type = 'Text'
        elif  (message_type == 'Text'):
            message_type = 'Picture'
        # message id
        message_id = conversation.get('id')

        # out values
        return contact_phone_number, created, direction, read, sender, recipient, body, message_type, media_ref_id, ref_url, message_id


    # fsCachedData
    media_files = seeker.search(f"*/{burner_app_identifier}/Library/Caches/com.adhoclabs.burner/fsCachedData/*")

    # media
    query = BURNER_CACHE_DB_QUERY.format(r'https:\/\/s3\.amazonaws\.com\/burner-*')
    media_records = get_sqlite_db_records_regexpr(file_found, query, regexpr=True)

    # cache
    query = BURNER_CACHE_DB_QUERY.format(r'https:\/\/phoenix\.burnerapp\.com(\/v\d)?\/user\/[a-fA-F\d-]{36}(\/messages($|\?.*contactPhoneNumber=.+)|(\/burners\/[a-fA-F\d-]{36}\/conversations\/.+\/messages($|\?.*pageSize=.+)))')
    db_records = get_sqlite_db_records_regexpr(file_found, query, regexpr=True)
    for record in db_records:
        db_device_file_paths = [ device_file_path ]

        # from file?
        isDataOnFS = bool(record[2])
        # from FS
        if isDataOnFS:
            fs_cached_data_path = get_cache_db_fs_path(record[3], file_found, seeker)
            json_data = get_json_file_content(fs_cached_data_path)
            if bool(fs_cached_data_path): db_device_file_paths.append(get_device_file_path(fs_cached_data_path, seeker))
        # from BLOB
        else:
            json_data = get_json_content(record[3])

        device_file_paths = db_device_file_paths

        # messages
        if isinstance(json_data, (list, tuple)):
            for i in range(0, len(json_data)):
                device_file_paths = db_device_file_paths

                message = json_data[i]
                if not bool(message):
                    continue

                # message
                if not bool(message.get('conversation')):
                    thread, created, direction, read, sender, recipient, body, message_type, \
                    media_ref_id, media_url, message_id = get_message(message)
                # conversation
                else:
                    thread, created, direction, read, sender, recipient, body, message_type, \
                    media_ref_id, media_url, message_id = get_conversation(message)

                media_url_html = generic_url(media_url, html_format=True)

                # source file name
                device_file_paths = dict.fromkeys(device_file_paths)
                source_file_name = unordered_list(device_file_paths)
                source_file_name_html = unordered_list(device_file_paths, html_format=True)
                # location
                location = [ f"cfurl_cache_receiver_data (entry_ID: {record[0]})" ]
                location.append(f"{record[3]}[{i}]" if isDataOnFS else f"receiver_data[{i}]")
                location = COMMA_SEP.join(location)

                # html row
                data_list_html.append((thread, created, direction, read, sender, recipient, body, message_type, media_ref_id, media_url_html,
                                       message_id, source_file_name_html, location))
                # lava row
                data_list.append((thread, created, direction, read, sender, recipient, body, message_type, media_ref_id, media_url,
                                  message_id, source_file_name, location))

        # message
        elif isinstance(json_data, dict):
            # message
            if not bool(json_data.get('conversation')):
                thread, created, direction, read, sender, recipient, body, message_type, \
                media_ref_id, media_url, message_id = get_message(json_data)
            # conversation
            else:
                thread, created, direction, read, sender, recipient, body, message_type, \
                media_ref_id, media_url, message_id = get_conversation(json_data)

            media_url_html = generic_url(media_url, html_format=True)

            # source file name
            device_file_paths = dict.fromkeys(device_file_paths)
            source_file_name = unordered_list(device_file_paths)
            source_file_name_html = unordered_list(device_file_paths, html_format=True)
            # location
            location = [ f"cfurl_cache_receiver_data (entry_ID: {record[0]})" ]
            location.append(f"{record[3]}" if isDataOnFS else f"receiver_data")
            location = COMMA_SEP.join(location)

            # html row
            data_list_html.append((thread, created, direction, read, sender, recipient, body, message_type, media_ref_id, media_url_html,
                                   message_id, source_file_name_html, location))
            # lava row
            data_list.append((thread, created, direction, read, sender, recipient, body, message_type, media_ref_id, media_url,
                              message_id, source_file_name, location))

    return data_headers, (data_list, data_list_html), ' '
