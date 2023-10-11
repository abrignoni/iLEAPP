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
import plistlib
import os
import textwrap
import scripts.artifacts.artGlobals


from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly,media_to_html

def get_dmss(files_found, report_folder, seeker, wrap_text, timezone_offset):
    separator_1 = '/'
    separator_2 = "\\"
    dmss_db_file_list = []
    media_data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        file_name = os.path.basename(file_found)
        if file_name == 'configFile1':
            #-Dahua App's PIN
            pin_code = "No Pass"
            with open(file_found,'rb') as f:
                encoded_data = f.read()

            decoded_data = base64.b64decode(encoded_data)

            plist_data = plistlib.loads(decoded_data)

            for k,v in plist_data.items():
                if k == "$objects":
                    if "5" == str(v[3]) and "True" == str(v[4]):
                        pin_code = v[5] #v[5] value is where the PIN gets stored
            
            if pin_code == "No Pass":
                logfunc(f'No PIN was set for Dahua Application')
            else:
                report = ArtifactHtmlReport('Dahua App PIN')
                report.start_artifact_report(report_folder, 'Dahua App PIN')
                report.add_script()
                data_headers = ('PIN',)
                data_list = ((pin_code,),)
                #data_list.append(pin_code,)
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Dahua App PIN'
                tsv(report_folder,data_headers, data_list, tsvname)
 
        if file_name == 'Devices.sqlite3':
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            
            #Dahua CCTV - Channels
            cursor.execute('''
                select
                    DEVICES.name,
                    CHANNELID,
                    CHANNELS.NAME
                from CHANNELS
                JOIN DEVICES ON CHANNELS.DEVICEID = DEVICES.ID
                ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Dahua - CCTV Channels')
                report.start_artifact_report(report_folder, 'Dahua - CCTV Channels')
                report.add_script()
                data_headers = ('Device Name','Channel ID','Channel Name') 
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Dahua - CCTV Channels'
                tsv(report_folder, data_headers, data_list, tsvname)
            
            else:
                logfunc(f'No Dahua - CCTV Channels data available')
            
            #Dahua CCTV - Info
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
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Dahua CCTV - Info')
                report.start_artifact_report(report_folder, 'Dahua CCTV - Info')
                report.add_script()
                data_headers = ('Name','IP/SN/Domain','Port','User','Password (Enc.)','DDNS Enabled','DDNS Address','DDNS Domain','DDNS Server Port','DDNS Username','DDNS Password (Enc.)','DDNS Type','DDNS Alias') 
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Dahua CCTV - Info'
                tsv(report_folder, data_headers, data_list, tsvname)
                
            else:
                logfunc(f'No Dahua CCTV - Info data available')

            db.close()

        if file_name == 'DMSSCloud.sqlite':
            try:
                db = open_sqlite_db_readonly(file_found)
                cursor = db.cursor()
                
                #-Dahua IoT - Registered Sensors
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
                usageentries = len(all_rows)
                db_owner = "N/A"
                if usageentries > 0:
                    if separator_1 in file_found:
                        dmss_db_file_list = file_found.split(separator_1)
                    else:
                        dmss_db_file_list = file_found.split(separator_2)
                    db_owner = "(without DMSS account)" if str(dmss_db_file_list[-2]) == "0" else f'(Account- {str(dmss_db_file_list[-2])})'

                    report = ArtifactHtmlReport(f'Dahua IoT - Registered Sensors {db_owner}')
                    report.start_artifact_report(report_folder, f'Dahua IoT - Registered Sensors {db_owner}')
                    report.add_script()
                    data_headers = ('Device Name','Device Model','Device SN','Device Type','Alarm State','Battery Percent','Associated Hub SN','Online State','Door State Sensor','Full Day Alarm','Tamper Status') 
                    data_list = []
                    for row in all_rows:
                        data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]))

                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    
                    tsvname = f'Dahua IoT - Registered Sensors {db_owner}'
                    tsv(report_folder, data_headers, data_list, tsvname)

                else:
                    logfunc(f'No Dahua IoT - Registered Sensors {db_owner} data available')

                #-Dahua IoT - Registered Devices
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
                usageentries = len(all_rows)
                if usageentries > 0:
                    report = ArtifactHtmlReport(f'Dahua IoT - Registered Devices {db_owner}')
                    report.start_artifact_report(report_folder, f'Dahua IoT - Registered Devices {db_owner}')
                    report.add_script()
                    data_headers = ('Device Name','Device Model','Device SN','Device Type','Channels','Online','Receive Share From','Send Share To','Username','Device Capabilities','Sup. Capabilities','Channels Capabilities','Port','RTSP Port','Hardware ID') 
                    data_list = []
                    for row in all_rows:
                        data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14]))

                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    
                    tsvname = f'Dahua IoT - Registered Devices {db_owner}'
                    tsv(report_folder, data_headers, data_list, tsvname)
                
                else:
                    logfunc(f'No Dahua IoT - Registered Devices {db_owner} data available')

                #-Dahua IoT - Notifications
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
                usageentries = len(all_rows)
                if usageentries > 0:
                    report = ArtifactHtmlReport(f'Dahua IoT - Notifications {db_owner}')
                    report.start_artifact_report(report_folder, f'Dahua IoT - Registered Notifications {db_owner}')
                    report.add_script()
                    data_headers = ('Timestamp (Local)','Sensor/Area/Nick Name','Sensor SN','Area Name','Nickname','Associated Device Name','Associated Device SN','Associated Device Type','Alarm Message ID','Alarm Notification','Checked') 
                    data_list = []
                    for row in all_rows:
                        data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]))

                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    
                    tsvname = f'Dahua IoT - Notifications {db_owner}'
                    tsv(report_folder, data_headers, data_list, tsvname)
                    
                    tlactivity =f'Dahua IoT - Notifications {db_owner}'
                    timeline(report_folder, tlactivity, data_list, data_headers) 

                else:
                    logfunc(f'No Dahua IoT - Notifications {db_owner} data available')
                db.close()
            
            except sqlite3.OperationalError as e:
                logfunc(f'Error - {e}')

        #Dahua CCTV - User Created Media: - Collecting Files
        if file_name.endswith(".jpg") or file_name.endswith(".mp4") or file_name.endswith(".dav"):
            if file_name.endswith(".jpg") and "Videos" in file_found: #we intentionally left out thumbnails of snapshots and video files to reduce media
                pass
            else:
                temp_tuple = ()
                temp_tuple = (file_found,file_name,file_name)
                media_data_list.append(temp_tuple)
            
    #Dahua CCTV - User Created Media: - Reporting Files
    media_files =  len(media_data_list)
    if media_files > 0:
        report = ArtifactHtmlReport('Dahua CCTV - User Created Media')
        report.start_artifact_report(report_folder, 'Dahua CCTV - User Created Media')
        report.add_script()
        data_headers = ('File Path','File Name', 'File Content') 
        data_list = []
        for mfile in media_data_list:          
            if mfile[2] is not None:
                media = media_to_html(mfile[2], files_found, report_folder)
            data_list.append((mfile[0],mfile[1],media))
        media_files_dir = "/private/var/mobile/Containers/Data/Application/[Application-GUID]/Documents/Captures/* and /private/var/mobile/Containers/Data/Application/[Application-GUID]/Documents/Videos/*" #Generic path of the media files.
        report.write_artifact_data_table(data_headers, data_list, media_files_dir, html_escape = False)
        report.end_artifact_report()

        tsvname = f'Dahua CCTV - User Created Media'
        tsv(report_folder, data_headers, data_list, tsvname)
            
    else:
        logfunc(f'No Dahua CCTV - User Created Media data available')

__artifacts__ = {
        "Dahua Technology (DMSS)": (
                "Dahua Technology (DMSS)",
                ('*/Library/Support/Devices.sqlite3','*/Library/Support/configFile1','*/Library/Support/*/DMSSCloud.sqlite','*/Documents/Captures/*','*/Documents/Videos/*'),
                get_dmss)
}
