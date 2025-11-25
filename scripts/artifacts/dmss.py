__artifacts_v2__ = {
    "get_dmss_pin": {
        "name": "Dahua Technology (DMSS)",
        "description": "Extract PINs from Dahua Technology (DMSS) Application",
        "author": "@theAtropos4n6",
        "creation_date": "2023-11-21",
        "last_update_date": "2025-11-25",
        "requirements": "none",
        "category": "Dahua Technology (DMSS)",
        "notes": "",
        "paths": ('*/Library/Support/configFile1',),
        "output_types": "standard",
    },
    "get_dmss_channels": {
        "name": "Dahua Technology (DMSS)",
        "description": "Extract channels from Dahua Technology (DMSS) Application",
        "author": "@theAtropos4n6",
        "creation_date": "2023-11-21",
        "last_update_date": "2025-11-25",
        "requirements": "none",
        "category": "Dahua Technology (DMSS)",
        "notes": "",
        "paths": ('*/Library/Support/Devices.sqlite3*'),
        "output_types": "standard",
    },
    "get_dmss_info": {
        "name": "Dahua Technology (DMSS)",
        "description": "Extract info from Dahua Technology (DMSS) Application",
        "author": "@theAtropos4n6",
        "creation_date": "2023-11-21",
        "last_update_date": "2025-11-25",
        "requirements": "none",
        "category": "Dahua Technology (DMSS)",
        "notes": "",
        "paths": ('*/Library/Support/Devices.sqlite3*'),
        "output_types": "standard",
    },
    "get_dmss_registered_sensors": {
        "name": "Dahua Technology (DMSS)",
        "description": "Extract registered sensors from Dahua Technology (DMSS) Application",
        "author": "@theAtropos4n6",
        "creation_date": "2023-11-21",
        "last_update_date": "2025-11-25",
        "requirements": "none",
        "category": "Dahua Technology (DMSS)",
        "notes": "",
        "paths": ('*/Library/Support/*/DMSSCloud.sqlite*'),
        "output_types": "standard",
    },
    "get_dmss_registered_devices": {
        "name": "Dahua Technology (DMSS)",
        "description": "Extract registered devices from Dahua Technology (DMSS) Application",
        "author": "@theAtropos4n6",
        "creation_date": "2023-11-21",
        "last_update_date": "2025-11-25",
        "requirements": "none",
        "category": "Dahua Technology (DMSS)",
        "notes": "",
        "paths": ('*/Library/Support/*/DMSSCloud.sqlite*'),
        "output_types": "standard",
    },
    "get_dmss_notifications": {
        "name": "Dahua Technology (DMSS)",
        "description": "Extract notifications from Dahua Technology (DMSS) Application",
        "author": "@theAtropos4n6",
        "creation_date": "2023-11-21",
        "last_update_date": "2025-11-25",
        "requirements": "none",
        "category": "Dahua Technology (DMSS)",
        "notes": "",
        "paths": ('*/Library/Support/*/DMSSCloud.sqlite*'),
        "output_types": "standard",
    },
    "get_dmss_created_media": {
        "name": "Dahua Technology (DMSS)",
        "description": "Extract created media from Dahua Technology (DMSS) Application",
        "author": "@theAtropos4n6",
        "creation_date": "2023-11-21",
        "last_update_date": "2025-11-25",
        "requirements": "none",
        "category": "Dahua Technology (DMSS)",
        "notes": "",
        "paths": ('*/Documents/Captures/*','*/Documents/Videos/*'),
        "output_types": "standard",
    }
}


""""
Developed by Evangelos Dragonas (@theAtropos4n6)

Research for this artifact was conducted by Evangelos Dragonas, Costas Lambrinoudakis and Michael Kotsis. 
For more information read their research paper here: Link_to_be_uploaded

Updated:18-04-2023

Dahua Technology (DMSS) is a well-known app that is used to both remotely access/operate CCTV systems and control IoT security systems. Currently the following information can be interpreted:

-Dahua App PIN: The PIN the user chose for protecting the application's usage

-Dahua CCTV - Channels: retrieves info for any available CCTV record channels 
-Dahua CCTV - Info: Information about the CCTV system
-Dahua CCTV - User Created Media: The media files the user created while viewing footage from the CCTV

-Dahua IoT - Registered Sensors (without DMSS account): List of IoT Registered Sensors that are connected with app ('.db' gets populated when the application is used without a DMSS account).
-Dahua IoT - Registered Devices (without DMSS account): List of IoT Registered Devices that are connected with app ('.db' gets populated when the application is used without a DMSS account).
-Dahua IoT - Notifications (without DMSS account): Cached notifications of the IoT smart home ('.db' gets populated when the application is used without a DMSS account).

-Dahua IoT - Registered Sensors (-x- DMSS account): List of IoT Registered Sensors that are connected with app ('x-account.db' gets populated when the application is used with the -x- DMSS account).
-Dahua IoT - Registered Devices (-x- DMSS account): List of IoT Registered Devices that are connected with app ('x-account.db' gets populated when the application is used with the -x- DMSS account).
-Dahua IoT - Notifications (-x- DMSS account): Cached notifications of the IoT smart home ('x-account.db' gets populated when the application is used with the -x- DMSS account).

"""

import sqlite3
import base64
import os
from scripts.ilapfuncs import logfunc, open_sqlite_db_readonly, check_in_media, \
    artifact_processor, get_plist_content

@artifact_processor
def get_dmss_pin(context):
    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        #-Dahua App's PIN
        pin_code = "No Pass"
        with open(file_found,'rb') as f:
            encoded_data = f.read()
            decoded_data = base64.b64decode(encoded_data)
            plist_data = get_plist_content(decoded_data)

            for k,v in plist_data.items():
                if k == "$objects":
                    if "5" == str(v[3]) and "True" == str(v[4]):
                        pin_code = v[5] #v[5] value is where the PIN gets stored
                        
            data_list.append((pin_code, file_found))
        
    data_headers = ('PIN', 'Source File')
    return data_headers, data_list, 'see Source File for more info'

@artifact_processor
def get_dmss_channels(context):
    data_headers = ('Device Name','Channel ID','Channel Name', 'Source file') 
    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        
        cursor.execute('''
            select
                DEVICES.name,
                CHANNELID,
                CHANNELS.NAME
            from CHANNELS
            JOIN DEVICES ON CHANNELS.DEVICEID = DEVICES.ID
            ''')

        all_rows = cursor.fetchall()
        for row in all_rows:
            data_list.append((row[0],row[1],row[2], file_found))
        db.close()
        
    return data_headers, data_list, 'see Source File for more info'

@artifact_processor
def get_dmss_info(context):
    data_headers = ('Name', 'IP/SN/Domain', 'Port', 'User', 'Password (Enc.)', 'DDNS Enabled', 'DDNS Address', 'DDNS Domain',
                    'DDNS Server Port', 'DDNS Username', 'DDNS Password (Enc.)', 'DDNS Type', 'DDNS Alias', 'Source File') 
    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        
        cursor.execute('''
            select
                DEVICES.NAME,
                DEVICES.IP,
                DEVICES.PORT,
                DEVICES.USER,
                DEVICES.PASSWORD,
                CASE
                    when DDNSCONFIG.DDNSENABLE='0' THEN 'False'
                    when DDNSCONFIG.DDNSENABLE='1' THEN 'True'
                END DDNSENABLE,
                DDNSCONFIG.DDNSADDRESS,
                DDNSCONFIG.DDNSDOMAIN,
                DDNSCONFIG.DDNSSERVERPORT,
                DDNSCONFIG.DDNSUSERNAME,
                DDNSCONFIG.DDNSPASSWORD,
                DDNSCONFIG.DDNSTYPE,
                DDNSCONFIG.DDNSALIAS
            from DEVICES
            JOIN DDNSCONFIG ON DEVICES.IP = DDNSCONFIG.DEVICEID
        ''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10],
                                row[11], row[12], file_found))
        db.close()
        
    return data_headers, data_list, 'see Source File for more info'

@artifact_processor
def get_dmss_registered_sensors(context):
    separator_1 = '/'
    separator_2 = "\\"
    dmss_db_file_list = []
    
    data_headers = ('Device Name', 'Device Model', 'Device SN', 'Device Type', 'Alarm State', 'Battery Percent',
                    'Associated Hub SN', 'Online State', 'Door State Sensor', 'Full Day Alarm', 'Tamper Status', 'Owner', 'Source File') 
    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        try:
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            
            cursor.execute('''
                select
                    partName,
                    partModel,
                    partSN,
                    paasType,
                    CASE
                        when alarmState='0' then 'off'
                        when alarmState='1' then 'on'
                    end alarmState,
                    batteryPercent,
                    boxSN,--Hub
                    CASE
                        when onLineState='0' then 'off'
                        when onLineState='1' then 'on'
                    end onLineState,
                    doorState,
                    CASE
                        when fullDayAlarm='0' then 'off'
                        when fullDayAlarm='1' then 'on'
                    end fullDayAlarm,
                    tamper
                from GatewayPartTable
                ''')

            all_rows = cursor.fetchall()
            db_owner = "N/A"
            if separator_1 in file_found:
                dmss_db_file_list = file_found.split(separator_1)
            else:
                dmss_db_file_list = file_found.split(separator_2)
            db_owner = "(without DMSS account)" if str(dmss_db_file_list[-2]) == "0" else f'(Account- {str(dmss_db_file_list[-2])})'

            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], db_owner, file_found))
        
            db.close()
        except sqlite3.OperationalError as e:
            logfunc(f'Error - {e}')
        
    return data_headers, data_list, 'see Source File for more info'

@artifact_processor
def get_dmss_registered_devices(context):
    separator_1 = '/'
    separator_2 = "\\"
    dmss_db_file_list = []
    data_headers = ('Device Name', 'Device Model', 'Device SN', 'Device Type', 'Channels', 'Online', 'Receive Share From',
                    'Send Share To', 'Username', 'Device Capabilities', 'Sup. Capabilities', 'Channels Capabilities', 'Port',
                    'RTSP Port', 'Hardware ID', 'Owner', 'Source File') 
    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        try:
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            
            cursor.execute('''
                select
                    name,
                    serial,
                    sn,
                    devType,
                    channelCount,
                    deviceIsOnline,
                    ReceiveShare,
                    SendShareStr,
                    userName,
                    DeviceCS,
                    SupCaps,
                    ChannelCS,
                    mPort,
                    mRtspPort,
                    hwId
                from DEVICES
                ''')
            
            all_rows = cursor.fetchall()
            
            if separator_1 in file_found:
                dmss_db_file_list = file_found.split(separator_1)
            else:
                dmss_db_file_list = file_found.split(separator_2)
            db_owner = "(without DMSS account)" if str(dmss_db_file_list[-2]) == "0" else f'(Account- {str(dmss_db_file_list[-2])})'
            
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14], db_owner, file_found))
        
            db.close()
        except sqlite3.OperationalError as e:
            logfunc(f'Error - {e}')
    
    return data_headers, data_list, 'see Source File for more info'

@artifact_processor
def get_dmss_notifications(context):
    separator_1 = '/'
    separator_2 = "\\"
    dmss_db_file_list = []
    data_headers = (('Timestamp (Local)', 'datetime'), 'Sensor/Area/Nick Name', 'Sensor SN', 'Area Name', 'Nickname',
                    'Associated Device Name', 'Associated Device SN', 'Associated Device Type', 'Alarm Message ID',
                    'Alarm Notification', 'Checked', 'Owner', 'Source File') 
    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        try:
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            
            cursor.execute('''
                select
                    CHNALARMMESSAGE.TIME,
                    SensorName,
                    SensorSN,
                    AreaName,
                    NickName,
                    DEVICES.name,
                    DEVICEID,--SN
                    DEVICES.devType,
                    ALARMID,
                    case
                        when CHNALARMMESSAGE.TYPE = 'gwMsg_ATSFault_Start' then 'ATS fault. Check network connection'
                        when CHNALARMMESSAGE.TYPE = 'gwMsg_ATSFault_Stop' then 'ATS restored'
                        when CHNALARMMESSAGE.TYPE = 'gwMsg_AreaAlarm_AddArea' then '"area name", added by "nickname"'
                        when CHNALARMMESSAGE.TYPE = 'gwMsg_AreaAlarm_AreaDelete' then '"area name", removed by "nickname"'
                        when CHNALARMMESSAGE.TYPE = 'gwMsg_AreaArmModeChange_Remote_DisArm' then '"area name", disarmed by "nickname"'
                        when CHNALARMMESSAGE.TYPE = 'gwMsg_AreaArmModeChange_Remote_Arm_p1' then '"area name", Home mode activated by "nickname"'
                        when CHNALARMMESSAGE.TYPE = 'gwMsg_ArmingFailure' then 'Unsuccessful arming "area name" attempt by "nickname"'
                        when CHNALARMMESSAGE.TYPE = 'gwMsg_AlarmLocal_PassiveInfrared' then 'Motion detected, "device name" in "area name"'
                        when CHNALARMMESSAGE.TYPE = 'gwMsg_AlarmLocal_DoorMagnetism_Start' then 'Opening detected, "device name" in "area name"'
                        when CHNALARMMESSAGE.TYPE = 'gwMsg_AlarmLocal_DoorMagnetism_Stop' then 'Closing detected, "device name" in "area name"'
                        else CHNALARMMESSAGE.TYPE 
                    end TYPE,
                    case
                        when ISCHECKED = '1' then 'Yes'
                        when ISCHECKED = '0' then 'No'
                    end ISCHECKED
                    from CHNALARMMESSAGE
                JOIN DEVICES ON DEVICES.sn = CHNALARMMESSAGE.DEVICEID
                ''')
            
            all_rows = cursor.fetchall()
            
            if separator_1 in file_found:
                dmss_db_file_list = file_found.split(separator_1)
            else:
                dmss_db_file_list = file_found.split(separator_2)
            db_owner = "(without DMSS account)" if str(dmss_db_file_list[-2]) == "0" else f'(Account- {str(dmss_db_file_list[-2])})'

            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], db_owner, file_found))
            
            db.close()
        
        except sqlite3.OperationalError as e:
            logfunc(f'Error - {e}')

    return data_headers, data_list, 'see Source File for more info'

@artifact_processor
def get_dmss_created_media(context):
    files_found = context.get_files_found()
    report_folder = context.get_report_folder()
    
    media_data_list = []
    data_headers = ('File Name', ('File Content', 'media'), 'Source File') 
    for file_found in files_found:
        file_found = str(file_found)
        file_name = os.path.basename(file_found)
        #Dahua CCTV - User Created Media: - Collecting Files
        if file_name.endswith(".jpg") or file_name.endswith(".mp4") or file_name.endswith(".dav"):
            if file_name.endswith(".jpg") and "Videos" in file_found: #we intentionally left out thumbnails of snapshots and video files to reduce media
                pass
            else:
                temp_tuple = ()
                temp_tuple = (file_name,file_name,file_found)
                media_data_list.append(temp_tuple)
            
    data_list = []
    for mfile in media_data_list:          
        if mfile[1] is not None:
            media = check_in_media(mfile[2], mfile[0])
            data_list.append((mfile[0],media, mfile[2]))
 
    return data_headers, data_headers, 'see Source File for more info'