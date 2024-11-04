__artifacts_v2__ = {
    "teamsMessages": {
        "name": "Teams Messages",
        "description": "Microsoft Teams messages and shared media",
        "author": "",
        "version": "1.0",
        "category": "Microsoft Teams",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/SkypeSpacesDogfood/*/Skype*.sqlite*',
                 '*/mobile/Containers/Shared/AppGroup/*/SkypeSpacesDogfood/Downloads/*/Images/*'),
        "output_types": "standard",
        "chatParams": {
            "threadDiscriminatorColumn": "Display Name",
            "textColumn": "Message",
            "timeColumn": "Timestamp",
            "senderColumn": "From",
            "mediaColumn": "Shared Media"
        }
    },
    "teamsContacts": {
        "name": "Teams Contacts",
        "description": "Microsoft Teams contact list",
        "author": "",
        "version": "1.0",
        "category": "Microsoft Teams",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/SkypeSpacesDogfood/*/Skype*.sqlite*',),
        "output_types": "standard"
    },
    "teamsUser": {
        "name": "Teams User Information",
        "description": "Microsoft Teams user profile and sync data",
        "author": "",
        "version": "1.0",
        "category": "Microsoft Teams",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/SkypeSpacesDogfood/*/Skype*.sqlite*',),
        "output_types": "standard"
    },
    "teamsCalls": {
        "name": "Teams Call Logs",
        "description": "Microsoft Teams call history",
        "author": "",
        "version": "1.0",
        "category": "Microsoft Teams",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/SkypeSpacesDogfood/*/Skype*.sqlite*',),
        "output_types": "standard"
    },
    "teamsLocations": {
        "name": "Teams Shared Locations",
        "description": "Microsoft Teams shared location data",
        "author": "",
        "version": "1.0",
        "category": "Microsoft Teams",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/SkypeSpacesDogfood/*/Skype*.sqlite*',),
        "output_types": "all"
    }
}

import sqlite3
import io
import json
import os
import re
import shutil
import datetime
from scripts.ilapfuncs import logfunc, convert_ts_human_to_timezone_offset, artifact_processor, open_sqlite_db_readonly
import nska_deserialize as nd

@artifact_processor
def teamsMessages(files_found, report_folder, seeker, wrap_text, timezone_offset):
    if not files_found:
        return
    
    data_list = []
    cache_file = None
    db_file = None
    
    # Find required files
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('.sqlite'):
            db_file = file_found
        elif file_found.endswith('CacheFile'):
            cache_file = file_found
    
    if not db_file:
        logfunc('No Teams database found')
        return
    
    # Initialize cache dictionary
    nsplist = {}
    if cache_file:
        try:
            with open(cache_file, 'rb') as nsfile:
                nsplist = nd.deserialize_plist(nsfile)
        except Exception as e:
            logfunc(f'Error parsing CacheFile: {str(e)}')
            nsplist = {}
    
    db = open_sqlite_db_readonly(db_file)
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT
            datetime('2001-01-01', "ZARRIVALTIME" || ' seconds') as timestamp,
            ZIMDISPLAYNAME,
            ZCONTENT,
            ZFROM
        FROM ZSMESSAGE
        ORDER BY timestamp
    ''')

    for row in cursor.fetchall():
        timestamp = convert_ts_human_to_timezone_offset(row[0], timezone_offset)
        display_name = row[1] if row[1] else ''
        content = row[2] if row[2] else ''
        sender = row[3] if row[3] else ''
        thumb = ''
        
        # Process media content
        if content and '<div><img src=' in content:
            try:
                matches = re.search('"([^"]+)"', content)
                if matches:
                    image_url = matches[0].strip('\"')
                    if image_url in nsplist:
                        data_file_real_path = nsplist[image_url]
                        for match in files_found:
                            if data_file_real_path in match:
                                try:
                                    shutil.copy2(match, report_folder)
                                    data_file_name = os.path.basename(match)
                                    thumb = f'<img src="{report_folder}/{data_file_name}"></img>'
                                except Exception as e:
                                    logfunc(f'Error copying media file: {str(e)}')
            except Exception as e:
                logfunc(f'Error processing image for message at {timestamp}: {str(e)}')
        
        data_list.append((timestamp, display_name, sender, content, thumb))
    
    db.close()
    
    data_headers = (
        ('Timestamp', 'datetime'),
        'Display Name',
        'From',
        'Message',
        'Shared Media'
    )
    
    return data_headers, data_list, db_file

@artifact_processor
def teamsContacts(files_found, report_folder, seeker, wrap_text, timezone_offset):
    if not files_found:
        return
    
    data_list = []
    db_file = None
    
    for file_found in files_found:
        if file_found.endswith('.sqlite'):
            db_file = file_found
            break
    
    if not db_file:
        logfunc('No Teams database found')
        return
    
    db = open_sqlite_db_readonly(db_file)
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT
            ZDISPLAYNAME,
            ZEMAIL,
            ZPHONENUMBER
        FROM ZDEVICECONTACTHASH
    ''')
    
    for row in cursor.fetchall():
        display_name = row[0] if row[0] else ''
        email = row[1] if row[1] else ''
        
        # Clean phone number
        phone = row[2] if row[2] else ''
        if phone:
            # Remove common formatting characters
            phone = phone.replace('(', '').replace(')', '').replace('-', '')
            phone = phone.replace(' ', '').replace('.', '').replace('+', '')
    
        data_list.append((display_name, email, phone))
    
    db.close()
    
    data_headers = (
        'Display Name',
        ('Email', 'phonenumber'),
        ('Phone Number', 'phonenumber')
    )
    
    return data_headers, data_list, db_file

@artifact_processor
def teamsUser(files_found, report_folder, seeker, wrap_text, timezone_offset):
    if not files_found:
        return
    
    data_list = []
    db_file = None
    
    for file_found in files_found:
        if file_found.endswith('.sqlite'):
            db_file = file_found
            break
    
    if not db_file:
        logfunc('No Teams database found')
        return
    
    db = open_sqlite_db_readonly(db_file)
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT
            datetime('2001-01-01', "ZTS_LASTSYNCEDAT" || ' seconds'),
            ZDISPLAYNAME,
            ZTELEPHONENUMBER
        FROM ZUSER
    ''')
    
    for row in cursor.fetchall():
        timestamp = convert_ts_human_to_timezone_offset(row[0], timezone_offset)
        display_name = row[1] if row[1] else ''
        phone = row[2] if row[2] else ''
        data_list.append((timestamp, display_name, phone))
    
    db.close()
    
    data_headers = (
        ('Timestamp Last Sync', 'datetime'),
        'Display Name',
        ('Phone Number', 'phonenumber')
    )
    
    return data_headers, data_list, db_file

@artifact_processor
def teamsCalls(files_found, report_folder, seeker, wrap_text, timezone_offset):
    if not files_found:
        return
    
    data_list = []
    db_file = None
    
    for file_found in files_found:
        if file_found.endswith('.sqlite'):
            db_file = file_found
            break
    
    if not db_file:
        logfunc('No Teams database found')
        return
    
    db = open_sqlite_db_readonly(db_file)
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT
            ZCOMPOSETIME,
            ZFROM,
            ZIMDISPLAYNAME,
            ZCONTENT,
            ZPROPERTIES
        FROM ZSMESSAGE
        JOIN ZMESSAGEPROPERTIES ON ZSMESSAGE.ZTSID = ZMESSAGEPROPERTIES.ZTSID
        WHERE ZPROPERTIES IS NOT NULL
        ORDER BY ZCOMPOSETIME
    ''')
    
    for row in cursor.fetchall():
        try:
            compose_time = convert_ts_human_to_timezone_offset(row[0].replace('T', ' '), timezone_offset)
            plist_file_object = io.BytesIO(row[4])
            
            try:
                plist = nd.deserialize_plist(plist_file_object)
            except Exception as e:
                logfunc(f'Failed to read plist: {str(e)}')
                continue
            
            if 'call-log' in plist:
                try:
                    if isinstance(plist['call-log'], dict):
                        datacalls = plist['call-log']
                    else:
                        datacalls = json.loads(plist['call-log'])
                    
                    call_start = convert_ts_human_to_timezone_offset(
                        datacalls.get('startTime', '').replace('T', ' '), 
                        timezone_offset
                    ) if datacalls.get('startTime') else ''
                    
                    call_connect = convert_ts_human_to_timezone_offset(
                        datacalls.get('connectTime', '').replace('T', ' '), 
                        timezone_offset
                    ) if datacalls.get('connectTime') else ''
                    
                    call_end = convert_ts_human_to_timezone_offset(
                        datacalls.get('endTime', '').replace('T', ' '), 
                        timezone_offset
                    ) if datacalls.get('endTime') else ''
                    
                    data_list.append((
                        compose_time,
                        row[1] if row[1] else '',  # from
                        row[2] if row[2] else '',  # display_name
                        row[3] if row[3] else '',  # content
                        call_start,
                        call_connect,
                        call_end,
                        datacalls.get('callDirection', ''),
                        datacalls.get('callType', ''),
                        datacalls.get('callState', ''),
                        datacalls.get('originator', ''),
                        datacalls.get('target', ''),
                        datacalls.get('originatorParticipant', {}).get('displayName', ''),
                        datacalls.get('targetParticipant', {}).get('displayName', '')
                    ))
                except Exception as e:
                    logfunc(f'Error processing call log data: {str(e)} - Data: {plist["call-log"]}')
                    
        except Exception as e:
            logfunc(f'Error processing row: {str(e)}')
    
    db.close()
    
    data_headers = (
        ('Compose Timestamp', 'datetime'),
        'From',
        'Display Name',
        'Content',
        ('Call Start', 'datetime'),
        ('Call Connect', 'datetime'),
        ('Call End', 'datetime'),
        'Call Direction',
        'Call Type',
        'Call State',
        'Call Originator',
        'Call Target',
        'Call Originator Name',
        'Call Participant Name'
    )
    
    return data_headers, data_list, db_file

@artifact_processor
def teamsLocations(files_found, report_folder, seeker, wrap_text, timezone_offset):
    if not files_found:
        return
    
    data_list = []
    db_file = None
    
    for file_found in files_found:
        if file_found.endswith('.sqlite'):
            db_file = file_found
            break
    
    if not db_file:
        logfunc('No Teams database found')
        return
    
    db = open_sqlite_db_readonly(db_file)
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT
            ZCOMPOSETIME,
            ZFROM,
            ZIMDISPLAYNAME,
            ZCONTENT,
            ZPROPERTIES
        FROM ZSMESSAGE
        JOIN ZMESSAGEPROPERTIES ON ZSMESSAGE.ZTSID = ZMESSAGEPROPERTIES.ZTSID
        WHERE ZPROPERTIES IS NOT NULL
        ORDER BY ZCOMPOSETIME
    ''')
    
    for row in cursor.fetchall():
        try:
            compose_time = convert_ts_human_to_timezone_offset(row[0].replace('T', ' '), timezone_offset)
            plist_file_object = io.BytesIO(row[4])
            
            try:
                plist = nd.deserialize_plist(plist_file_object)
            except Exception as e:
                logfunc(f'Failed to read plist: {str(e)}')
                continue
            
            if 'cards' in plist:
                try:
                    cards = json.loads(plist['cards'])
                    card = cards[0]['content']['body'][0]
                    
                    card_url = card.get('selectAction', {}).get('url', '')
                    card_title = card.get('selectAction', {}).get('title', '')
                    card_text = cards[0]['content']['body'][1].get('text', '')
                    card_url2 = card.get('url', '')
                    
                    card_lat = None
                    card_long = None
                    card_expires = None
                    card_devid = None
                    
                    if card.get('id'):
                        try:
                            id_content = json.loads(card['id'])
                            card_lat = id_content.get('latitude')
                            card_long = id_content.get('longitude')
                            expires_ms = id_content.get('expiresAt')
                            if expires_ms:
                                card_expires = convert_ts_human_to_timezone_offset(
                                    datetime.datetime.fromtimestamp(expires_ms / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                                    timezone_offset
                                )
                            card_devid = id_content.get('deviceId')
                        except Exception as e:
                            logfunc(f'Error processing card ID data: {str(e)}')
                    
                    data_list.append((
                        compose_time,
                        row[1] if row[1] else '',  # from
                        row[2] if row[2] else '',  # display_name
                        row[3] if row[3] else '',  # content
                        card_url,
                        card_title,
                        card_text,
                        card_url2,
                        card_lat,
                        card_long,
                        card_expires,
                        card_devid
                    ))
                except Exception as e:
                    logfunc(f'Error processing card data: {str(e)}')
                    
        except Exception as e:
            logfunc(f'Error processing row: {str(e)}')
    
    db.close()
    
    data_headers = (
        ('Timestamp', 'datetime'),
        'From',
        'Display Name',
        'Content',
        'Card URL',
        'Card Title',
        'Card Text',
        'Card URL2',
        'Latitude',
        'Longitude',
        ('Card Expires', 'datetime'),
        'Device ID'
    )
    
    return data_headers, data_list, db_file
    
