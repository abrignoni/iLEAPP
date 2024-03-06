__artifacts_v2__ = {
    "burnerCache": {
        "name": "Burner Cache",
        "description": "Parses and extract accounts, contacts, burner numbers and messages",
        "author": "Django Faiola (djangofaiola.blogspot.com @DjangoFaiola)",
        "version": "0.1.0",
        "date": "2024-03-05",
        "requirements": "none",
        "category": "Burner",
        "notes": "App version tested: 4.0.18, 4.3.3, 5.3.8",
        "paths": ('*/Library/Caches/com.adhoclabs.burner/Cache.db*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "function": "get_burner_cache"
    }
}

import os
import json
import re
import plistlib
import shutil
import sqlite3
import textwrap

from pathlib import Path
from base64 import b64encode
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, convert_ts_int_to_utc, convert_utc_human_to_timezone, media_to_html
from scripts.filetype import image_match

# format timestamp
def FormatTimestamp(utc, timezone_offset, divisor=1.0):
    if not bool(utc):
        return ''
    else:
        timestamp = convert_ts_int_to_utc(int(float(utc) / divisor))
        return convert_utc_human_to_timezone(timestamp, timezone_offset)


# blob image to html
def blob_image_to_html(data, max_width=96):
    mimetype = image_match(data)
    if bool(mimetype):
        base64 = b64encode(data).decode('utf-8')
        return f'<img src="data:{mimetype.MIME};base64,{base64}" width="{max_width}">'
    else:
        return ''
                  

REGEXP_MEDIA = r'WHERE cr.request_key like "https://s3.amazonaws.com/burner-%"'
REGEXP_ACCOUNTS = r'WHERE cr.request_key REGEXP "https://phoenix\.burnerapp\.com(/v\d)?(/register(/phone)?$|/user/[a-zA-Z0-9\-]{36}/token)"'
REGEXP_CONTACTS = r'WHERE cr.request_key REGEXP "https://phoenix\.burnerapp\.com(/v\d)?/user/[a-zA-Z0-9\-]{36}/contacts\?.+"'
REGEXP_MESSAGES = r'WHERE cr.request_key REGEXP "https://phoenix\.burnerapp\.com(/v\d)?/user/[a-zA-Z0-9\-]{36}/messages($|\?.*contactPhoneNumber=.+)"'
REGEXP_NUMBERS = r'WHERE cr.request_key REGEXP "https://phoenix\.burnerapp\.com(/v\d)?/user/[a-zA-Z0-9\-]{36}/burners(/[a-zA-Z0-9\-]{36})?$"'

# cache query
def cache_query(db, where=''):
    cursor = db.cursor()
    cursor.execute('''
    SELECT
        cr.entry_ID,
        crd.entry_ID,
        cr.request_key,
	    crd.isDataOnFS,
	    crd.receiver_data
    FROM cfurl_cache_response AS "cr"
    LEFT JOIN cfurl_cache_receiver_data AS "crd" ON (cr.entry_ID = crd.entry_ID)
    {0}                       
    '''.format(where)
    )
    return cursor.fetchall()

                       
# cache accounts
def get_cache_accounts(file_found, cache_files, report_folder, timezone_offset):
    # get account
    def get_account(account):
        # user
        user = account.get('user')
        if bool(user):
            # date created
            created = FormatTimestamp(user.get('dateCreated'), timezone_offset, divisor=1000)
            # phone number
            phone_number = user.get('phoneNumber', '')
            # country code
            country_code = user.get('countryCode')
            # carrier name
            carrier_name = user.get('carrierName')
            # total number burners
            total_number_burners = user.get('totalNumberBurners')
            # last updated date
            last_updated = FormatTimestamp(user.get('lastUpdatedDate'), timezone_offset, divisor=1000)
            # user id
            user_id = user.get('id')
        else:
            # date created
            created = FormatTimestamp(account.get('dateCreated'), timezone_offset, divisor=1000)
            # phone number
            phone_number = account.get('phoneNumber', '')
            # country code
            country_code = account.get('countryCode')
            # carrier name
            carrier_name = account.get('carrierName')
            # total number burners
            total_number_burners = account.get('totalNumberBurners')
            # last updated date
            last_updated = FormatTimestamp(account.get('lastUpdatedDate'), timezone_offset, divisor=1000)
            # user id
            user_id = account.get('id')

        if bool(user_id):
            out_map[user_id] = phone_number

        # out values
        return last_updated, created, phone_number, country_code, carrier_name, total_number_burners, user_id
    
    # {user_id: phone_number}
    out_map = {}

    # accounts
    db = open_sqlite_db_readonly(file_found)
    try:
        # regexp() user function
        db.create_function('regexp', 2, lambda x, y: 1 if re.search(x,y) else 0)

        all_rows = cache_query(db, where=REGEXP_ACCOUNTS)
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Burner Cache accounts')
            report.start_artifact_report(report_folder, 'Burner Cache accounts')
            report.add_script()
            data_headers = ('Last updated', 'Created', 'Phone number', 'Country code', 'Carrier name', 'Number of burners', 'User ID', 'Item') 
                       
            data_list = []
            json_data = None
            for row in all_rows:
                # from file?
                isDataOnFS = bool(row[3])
                if isDataOnFS:
                    json_file = os.path.dirname(file_found)
                    json_file = Path(json_file).joinpath('fsCachedData', row[4])
                    if os.path.isfile(json_file):
                        f = open(json_file, 'r', encoding='utf-8')
                        try:
                            json_data = json.load(f)
                        finally:
                            f.close()
                # from blob
                else:
                    json_data = json.loads(row[4])

                # accounts
                if type(json_data) in (list, tuple):
                    a_count = 0
                    for account in json_data:
                        # fsCachedData
                        if isDataOnFS:
                            location = f'{row[4]}[{a_count}]'
                        # cfurl_cache_receiver_data.receiver_data
                        else:
                            location = f'receiver_data[{a_count}]'

                        last_updated, created, phone_number, country_code, carrier_name, total_number_burners, user_id = get_account(account)
                        data_list.append((last_updated, created, phone_number, country_code, carrier_name, total_number_burners, user_id, location))                       
                        a_count += 1
                # account
                elif type(json_data) is dict:
                    # fsCachedData
                    if isDataOnFS:
                        location = f'{row[4]}[0]'
                    # cfurl_cache_receiver_data.receiver_data
                    else:
                        location = 'receiver_data[0]'

                    last_updated, created, phone_number, country_code, carrier_name, total_number_burners, user_id = get_account(json_data)
                    data_list.append((last_updated, created, phone_number, country_code, carrier_name, total_number_burners, user_id, location))
        
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()
                
            tsvname = f'Burner Cache accounts'
            tsv(report_folder, data_headers, data_list, tsvname)
                
            tlactivity = 'Burner Cache accounts'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Burner Cache accounts data available')

    except Exception as ex:
        logfunc('Exception while parsing Burner Cache accounts: ' + str(ex))

    finally:
        db.close()
        return out_map


# cache contacts
def get_cache_contacts(file_found, cache_files, report_folder, timezone_offset):
    # get contact
    def get_contact(contact):
        # date created
        created = FormatTimestamp(contact.get('dateCreated'), timezone_offset, divisor=1000)
        # display name
        display_name = contact.get('name', '')
        # phone number
        phone_number = contact.get('phoneNumber', '')
        # other phones ???
        # notes
        notes = contact.get('text', '')
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
        burner_ids = ', '.join(contact.get('burnerIds', []))       
        # contact id
        contact_id = contact.get('id')

        # out values
        return created, phone_number, display_name, notes, verified, blocked, muted, burner_ids, contact_id

    db = open_sqlite_db_readonly(file_found)
    try:
        # regexp() user function
        db.create_function('regexp', 2, lambda x, y: 1 if re.search(x,y) else 0)

        all_rows = cache_query(db, where=REGEXP_CONTACTS)
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Burner Cache contacts')
            report.start_artifact_report(report_folder, 'Burner Cache contacts')
            report.add_script()
            data_headers = ('Created', 'Phone number', 'Full name', 'Notes', 'Verified', 'Blocked', 'Muted', 'Burner IDs', 'Contact ID', 'Item') 

            data_list = []
            json_data = None
            for row in all_rows:
                # from file?
                isDataOnFS = bool(row[3])
                if isDataOnFS:
                    json_file = os.path.dirname(file_found)
                    json_file = Path(json_file).joinpath('fsCachedData', row[4])
                    if os.path.isfile(json_file):
                        f = open(json_file, 'r', encoding='utf-8')
                        try:
                            json_data = json.load(f)
                        finally:
                            f.close()
                # from blob
                else:
                    json_data = json.loads(row[4])

                # contacts
                if type(json_data) in (list, tuple):
                    c_count = 0
                    for contact in json_data:
                        # fsCachedData
                        if isDataOnFS:
                            location = f'{row[4]}[{c_count}]'
                        # cfurl_cache_receiver_data.receiver_data
                        else:
                            location = f'receiver_data[{c_count}]'

                        created, phone_number, display_name, notes, verified, blocked, muted, burner_ids, contact_id = get_contact(contact)
                        data_list.append((created, phone_number, display_name, notes, verified, blocked, muted, burner_ids, contact_id, location))
                        c_count += 1
                # contact
                elif type(json_data) is dict:
                    # fsCachedData
                    if isDataOnFS:
                        location = f'{row[4]}[0]'
                    # cfurl_cache_receiver_data.receiver_data
                    else:
                        location = 'receiver_data[0]'

                    created, phone_number, display_name, notes, verified, blocked, muted, burner_ids, contact_id = get_contact(json_data)
                    data_list.append((created, phone_number, display_name, notes, verified, blocked, muted, burner_ids, contact_id, location))
    
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()
                
            tsvname = f'Burner Cache contacts'
            tsv(report_folder, data_headers, data_list, tsvname)
                
            tlactivity = 'Burner Cache contacts'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Burner Cache contacts data available')

    except Exception as ex:
        logfunc('Exception while parsing Burner Cache contacts: ' + str(ex))

    finally:
        db.close()


# cache numbers
def get_cache_numbers(file_found, cache_files, report_folder, timezone_offset, users):
    # get number
    def get_number(number):
        # burner number
        burner_number = number.get('phoneNumber')
        if not bool(burner_number):
            burner_number = number.get('phoneNumberId')
        # user id
        user_id = number.get('userId', '')
        if not bool(user_id):
            # https://phoenix.burnerapp.com/v3/user/<user_id>/burners
            user_id = str(row[2]).split('/')[-2]
        # user phone number
        user_phone_number = users.get(user_id, '')
        # version
        version = number.get('version')
        # date created
        created = FormatTimestamp(number.get('dateCreated'), timezone_offset, divisor=1000)
        # subscription expires
        expires = FormatTimestamp(number.get('expirationDate'), timezone_offset, divisor=1000)
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

        # out values
        return burner_number, display_name, created, expires, version, notifications, inbound_caller_id,  \
            voip, auto_reply_enabled, auto_reply_text, rt_minutes, rt_texts, \
            user_phone_number, user_id, burner_id
    
    # numbers
    db = open_sqlite_db_readonly(file_found)
    try:
        # regexp() user function
        db.create_function('regexp', 2, lambda x, y: 1 if re.search(x,y) else 0)

        all_rows = cache_query(db, where=REGEXP_NUMBERS)       
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Burner Cache numbers')
            report.start_artifact_report(report_folder, 'Burner Cache numbers')
            report.add_script()
            data_headers = ('Burner number', 'Display name', 'Created', 'Subscription Expires', 'Version', 'Notifications', 'Inbound caller ID', 
                            'In-App calling (VoIP)', 'Auto-replay enabled', 'Auto-reply message', 'Remaining/Total minutes', 'Remaining/Total messages', 
                            'Phone number', 'User ID', 'Burner ID', 'Item') 
                        
            data_list = []
            json_data = None
            for row in all_rows:
                # from file?
                isDataOnFS = bool(row[3])
                if isDataOnFS:
                    json_file = os.path.dirname(file_found)
                    json_file = Path(json_file).joinpath('fsCachedData', row[4])
                    if os.path.isfile(json_file):
                        f = open(json_file, 'r', encoding='utf-8')
                        try:
                            json_data = json.load(f)
                        finally:
                            f.close()
                # from blob
                else:
                    json_data = json.loads(row[4])

                # numbers
                if type(json_data) in (list, tuple):
                    n_count = 0
                    for number in json_data:
                        # fsCachedData
                        if isDataOnFS:
                            location = f'{row[4]}[{n_count}]'
                        # cfurl_cache_receiver_data.receiver_data
                        else:
                            location = f'receiver_data[{n_count}]'

                        burner_number, display_name, created, expires, version, notifications, inbound_caller_id,  \
                        voip, auto_reply_enabled, auto_reply_text, rt_minutes, rt_texts, \
                        user_phone_number, user_id, burner_id = get_number(number)
                        data_list.append((burner_number, display_name, created, expires, version, notifications, inbound_caller_id,
                                          voip, auto_reply_enabled, auto_reply_text, rt_minutes, rt_texts, 
                                          user_phone_number, user_id, burner_id, location))
                        n_count += 1
                # number
                elif type(json_data) is dict:
                    # fsCachedData
                    if isDataOnFS:
                        location = f'{row[4]}[0]'
                    # cfurl_cache_receiver_data.receiver_data
                    else:
                        location = 'receiver_data[0]'

                    burner_number, display_name, created, expires, version, notifications, inbound_caller_id,  \
                    voip, auto_reply_enabled, auto_reply_text, rt_minutes, rt_texts, \
                    user_phone_number, user_id, burner_id = get_number(json_data)
                    data_list.append((burner_number, display_name, created, expires, version, notifications, inbound_caller_id,
                                      voip, auto_reply_enabled, auto_reply_text, rt_minutes, rt_texts, 
                                      user_phone_number, user_id, burner_id, location))
        
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()
                
            tsvname = f'Burner Cache numbers'
            tsv(report_folder, data_headers, data_list, tsvname)
                
            tlactivity = 'Burner Cache numbers'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Burner Cache numbers data available')

    except Exception as ex:
        logfunc('Exception while parsing Burner Cache numbers: ' + str(ex))

    finally:
        db.close()


# cache messages
def get_cache_messages(file_found, cache_files, report_folder, timezone_offset, users):
    # get message
    def get_message(message):
        # date created
        created = FormatTimestamp(message.get('dateCreated'), timezone_offset, divisor=1000)
        # read
        if bool(message.get('read')):
            read = 'Read'
        else:
            read = 'Not read'
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
        # user id
        user_id = message.get('userId', '')
        if not bool(user_id):
            # https://phoenix.burnerapp.com/user/<user_id>/messages
            user_id = str(row[2]).split('/')[-2]
        # user phone number
        user_phone_number = users.get(user_id, '')
        # sender, recipient
        if dir_val == 1:
            sender = message.get('contactPhoneNumber')
            recipient = user_phone_number
        else:
            sender = user_phone_number
            recipient = message.get('contactPhoneNumber')
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
        media = ''
        # asset url
        asset_url = message.get('assetUrl')
        if bool(asset_url):
            for row_media in all_media:
                if row_media[2] == asset_url:
                    # isDataOnFS
                    if row_media[3] == 1:
                        media = media_to_html(row_media[4], cache_files, report_folder)
                    else:
                        media = blob_image_to_html(row_media[4])
                    break
        # message type
        message_type = message.get('messageType')
        if  (message_type == 1) and (state in (3, 4)):
            message_type = 'Call'
        elif  (message_type == 1) and (state == 5):
            message_type = 'Voicemail'
        elif  (message_type == 2) and not bool(asset_url):
            message_type = 'Text'
        elif  (message_type == 2):
            message_type = 'Picture'
        # voice url
        voice_url = message.get('voiceUrl')
        if bool(voice_url):
            for row_media in all_media:
                if row_media[2] == voice_url:
                    # isDataOnFS
                    if row_media[3] == 1:
                        media += media_to_html(row_media[4], cache_files, report_folder)
                    else:
                        media += blob_image_to_html(row_media[4])
                    break
        # message id
        message_id = message.get('id')

        # out values
        return created, direction, read, sender, recipient, body, message_type, media, asset_url, voice_url, message_id


    # messages
    db = open_sqlite_db_readonly(file_found)
    try:
        # regexp() user function
        db.create_function('regexp', 2, lambda x, y: 1 if re.search(x,y) else 0)

        # media
        all_media = cache_query(db, where=REGEXP_MEDIA)

        all_rows = cache_query(db, where=REGEXP_MESSAGES)
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Burner Cache messages')
            report.start_artifact_report(report_folder, 'Burner Cache messages')
            report.add_script()
            data_headers = ('Sent', 'Direction', 'Read', 'Sender', 'Recipient', 'Message', 'Message type',
                            'Media', 'Media URL', 'Voicemail URL', 'Message ID', 'Item') 
                        
            data_list = []
            json_data = None
            for row in all_rows:
                # from file?
                isDataOnFS = bool(row[3])
                if isDataOnFS:
                    json_file = os.path.dirname(file_found)
                    json_file = Path(json_file).joinpath('fsCachedData', row[4])
                    if os.path.isfile(json_file):
                        f = open(json_file, 'r', encoding='utf-8')
                        try:
                            json_data = json.load(f)
                        finally:
                            f.close()
                # from blob
                else:
                    json_data = json.loads(row[4])

                # messages
                if type(json_data) in (list, tuple):
                    m_count = 0
                    for message in json_data:
                        # fsCachedData
                        if isDataOnFS:
                            location = f'{row[4]}[{m_count}]'
                        # cfurl_cache_receiver_data.receiver_data
                        else:
                            location = f'receiver_data[{m_count}]'

                        created, direction, read, sender, recipient, body, message_type, \
                        media, asset_url, voice_url, message_id = get_message(message)
                        data_list.append((created, direction, read, sender, recipient, body, message_type,
                                          media, asset_url, voice_url, message_id, location))
                        m_count += 1
                # message
                elif type(json_data) is dict:
                    # fsCachedData
                    if isDataOnFS:
                        location = f'{row[4]}[0]'
                    # cfurl_cache_receiver_data.receiver_data
                    else:
                        location = 'receiver_data[0]'

                    created, direction, read, sender, recipient, body, message_type, \
                    media, asset_url, voice_url, message_id = get_message(json_data)
                    data_list.append((created, direction, read, sender, recipient, body, message_type,
                                      media, asset_url, voice_url, message_id, location))
        
            report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=[ 'Media' ])
            report.end_artifact_report()
                
            tsvname = f'Burner Cache messages'
            tsv(report_folder, data_headers, data_list, tsvname)
                
            tlactivity = 'Burner Cache messages'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Burner Cache messages data available')

    except Exception as ex:
        logfunc('Exception while parsing Burner Cache messages: ' + str(ex))

    finally:
        db.close()


# burner
def get_burner_cache(files_found, report_folder, seeker, wrap_text, timezone_offset):
    cache_files = []
    for file_foundm in files_found:
        if file_foundm.endswith('.com.apple.mobile_container_manager.metadata.plist'):
            with open(file_foundm, 'rb') as f:
                pl = plistlib.load(f)
                if pl['MCMMetadataIdentifier'] == 'com.adhoclabs.burner':
                    fulldir = (os.path.dirname(file_foundm))
                    identifier = (os.path.basename(fulldir))
                    
                    # fsCachedData
                    cache_files = seeker.search(f'*/{identifier}/Library/Caches/com.adhoclabs.burner/fsCachedData/**')
                f.close()

    for file_found in files_found:
        file_found = str(file_found)

        # Cache.db
        if file_found.endswith('Cache.db'):
            db = open_sqlite_db_readonly(file_found)
            try:
                # accounts
                users = get_cache_accounts(file_found, cache_files, report_folder, timezone_offset)
                # contacts
                get_cache_contacts(file_found, cache_files, report_folder, timezone_offset)
                # numbers
                get_cache_numbers(file_found, cache_files, report_folder, timezone_offset, users)
                # messages
                get_cache_messages(file_found, cache_files, report_folder, timezone_offset, users)

            finally:
                db.close()
