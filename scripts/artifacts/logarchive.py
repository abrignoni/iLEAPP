__artifacts_v2__ = {
    "logarchive": {
        "name": "logarchive",
        "description": "Processes a json file from a logarchive",
        "author": "@AlexisBrignoni",
        "creation_date": "2025-05-06",
        "last_update_date": "2025-05-06",
        "requirements": "none",
        "category": "Unified Logs",
        "notes": "",
        "paths": ('*/logarchive*.json',),
        "output_types": "lava_only",
        "artifact_icon": "database",
    },
    "logarchive_artifacts": {
        "name": "logarchive artifacts",
        "description": "Extract relevant entries from the logarchive table of LAVA db",
        "author": "@AlexisBrignoni, @JohannPLW",
        "creation_date": "2025-05-19",
        "last_update_date": "2025-05-21",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "",
        "paths": None,
        "output_types": "lava_only",
        "artifact_icon": "database",
    },
    "logarchive_time_change": {
        "name": "logarchive time change",
        "description": "Identify time changes",
        "author": "@AlexisBrignoni",
        "creation_date": "2025-05-22",
        "last_update_date": "2025-05-22",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "clock",
    },
    "logarchive_flashlight": {
        "name": "logarchive flashlight",
        "description": "Identify flashlight turn on or off",
        "author": "@AlexisBrignoni",
        "creation_date": "2025-05-25",
        "last_update_date": "2025-05-25",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "sun",
    },
    "logarchive_executed_apps": {
        "name": "logarchive executed apps",
        "description": "Track apps being executed",
        "author": "@AlexisBrignoni",
        "creation_date": "2025-05-26",
        "last_update_date": "2025-05-26",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "code",
    },
    "logarchive_tethering": {
        "name": "logarchive personal hotspot",
        "description": "Hotspot/Tethering state",
        "author": "@AlexisBrignoni",
        "creation_date": "2025-05-27",
        "last_update_date": "2025-05-27",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "wifi",
    },
    "logarchive_airplane_mode": {
        "name": "logarchive airplane mode",
        "description": "Airplane Mode",
        "author": "@AlexisBrignoni",
        "creation_date": "2025-05-27",
        "last_update_date": "2025-05-27",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "wifi-off",
    },
    "logarchive_lock_status": {
        "name": "logarchive lock status",
        "description": "Lock Status",
        "author": "@AlexisBrignoni",
        "creation_date": "2025-05-28",
        "last_update_date": "2025-05-28",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "lock",
    },
    "logarchive_wifi_status": {
        "name": "logarchive wifi status",
        "description": "WiFi Status",
        "author": "@AlexisBrignoni",
        "creation_date": "2025-05-28",
        "last_update_date": "2025-05-28",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "wifi",
    },
    "logarchive_bluetooth_status": {
        "name": "logarchive bluetooth status",
        "description": "Bluetooth Status",
        "author": "@AlexisBrignoni",
        "creation_date": "2025-05-28",
        "last_update_date": "2025-05-28",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "bluetooth",
    },
    "logarchive_audio_status": {
        "name": "logarchive audio status",
        "description": "Audio Status",
        "author": "@AlexisBrignoni",
        "creation_date": "2025-06-02",
        "last_update_date": "2025-06-02",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "headphones",
    },
    "logarchive_navigation": {
        "name": "logarchive navigation",
        "description": "Navigation entries",
        "author": "@AlexisBrignoni",
        "creation_date": "2025-07-25",
        "last_update_date": "2025-07-25",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "map-pin",
    }
}

import ijson
from datetime import datetime, timezone
from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, logfunc


def convert_to_utc(timestamp):
    # dt_local = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f%z")
    # dt_utc = dt_local.astimezone(timezone.utc)
    # return dt_utc.astimezone(timezone.utc)
    # NOTE:
    #   python 3.7-3.10 have datetime.fromisoformat() but it had a bug where it didn't
    #   parse timezones correctly -- so this is now 3.11 onwards:
    #   if you're on 3.10 and know your python-fun, uncomment the first 3 lines
    #   but it'll run much slower than 3.11+ with this new version
    
    return datetime.fromisoformat(timestamp).astimezone(timezone.utc)


def truncate_after_last_bracket(file_path):
    with open(file_path, 'rb+') as f:
        # Start from the end of the file and scan backwards
        f.seek(0, 2)  # Move to end of file
        file_size = f.tell()

        for i in range(file_size - 1, -1, -1):
            f.seek(i)
            char = f.read(1)
            if char == b']':
                # Truncate the file just after this bracket
                f.truncate(i + 1)
                logfunc(f"Truncated file after position {i+1}")
                return
        print("No closing bracket `]` found.")

@artifact_processor
def logarchive(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, 'logarchive*.json')
    data_list = []

    incval = 0
    if source_path:
        truncate_after_last_bracket(source_path)
        with open(source_path, 'rb') as f:
            for record in ijson.items(f, 'item', multiple_values=True ): # if the json is a list
                if isinstance(record, dict):
                    incval = incval + 1
                    timestamp = record.get('timestamp', '')
                    timestamp = convert_to_utc(timestamp) if timestamp else ''
                    processid = record.get('processID', '')
                    process_image_path = record.get('processImagePath', '')
                    subsystem = record.get('subsystem', '')
                    category = record.get('category', '')
                    eventmessage = str(record.get('eventMessage', ''))
                    traceid = str(record.get('traceID', ''))
                    
                    t0 = ( timestamp, incval,  process_image_path,  processid,  subsystem,  category,  eventmessage,  traceid)
                    data_list.append(t0)

    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID',
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    return data_headers, data_list, source_path

@artifact_processor
def logarchive_artifacts(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, '_lava_artifacts.db')
    data_list = []

    query = '''
    SELECT *
    FROM logarchive
    WHERE event_message LIKE '%Take screenshot%'
        OR event_message LIKE '%Time change: Clock shifted by%'
        OR event_message LIKE '%BoutDetector (stepBout): Identified potential walking bout%'
        OR event_message LIKE '%Has contact name and phone number%'
        OR event_message LIKE '%charger connected state change%'
        OR event_message LIKE '%Motion State Transition:%'
        OR event_message LIKE '%CarPlay Connection Event:%'
        OR event_message LIKE '%CoreAnalytics event: com.apple.accessories.connection.added%'
        OR event_message LIKE '%CoreAnalytics event: com.apple.accessories.endpoint.accessroryInfoChanged%'
        OR event_message LIKE '%Start #SpeechRequest id%'
        OR event_message LIKE '%Received Orientation%'
        OR event_message LIKE '%Effective device orientation%'
        OR event_message LIKE '%Received: Match Started%'
        OR event_message LIKE '%Received: Face%'
        OR event_message LIKE '%Received: Authenticated%'
        OR event_message LIKE '%AppleAccount Authenticated:%'
        OR event_message LIKE '%=> Transitioning to state:%'
        OR event_message LIKE '%Received: Screen%'
        OR event_message LIKE '%Screen did lock%'
        OR event_message LIKE '%ScreenOn changed%'
        OR event_message LIKE '%Screen shut off%'
        OR event_message LIKE '%screen is locked%'
        OR event_message LIKE '%screen is unlocked%'
        OR event_message LIKE '%Device unlocked%'
        OR event_message LIKE '%Device lock status%'
        OR event_message LIKE '%Biometric match complete%'
        OR event_message LIKE '%SBIconView touches began with event:%'
        OR event_message LIKE '%Setting process visibility%'
        OR event_message LIKE '%WiFi state changed:%'
        OR event_message LIKE '%Toggled WiFi state%'
        OR event_message LIKE '%is WiFi associated?%'
        OR event_message LIKE '%link status changed%'
        OR event_message LIKE '%reachability changed%'
        OR event_message LIKE '%ISNetworkObserver%'
        OR event_message LIKE '%ForgetSSID%'
        OR event_message LIKE '%en0: SSID%'
        OR event_message LIKE '%Removing Lease SSID%'
        OR event_message LIKE '%SysMon: WiFi state changed:%'
        OR event_message LIKE '%WiFiManagerClientRemoveNetworkWithReason:%'
        OR event_message LIKE '%WiFiSecurityRemovePassword%'
        OR event_message LIKE '%AlwaysOnWifi:%'
        OR event_message LIKE '%WiFiDeviceManagerSetNetworks:%'
        OR event_message LIKE '%Scanning For Broadcast found:%'
        OR event_message LIKE '%Scanning Remaining Channels%'
        OR event_message LIKE '%WiFiSettlementObserver _handleScanResults%'
        OR event_message LIKE '%Attempting to join%'
        OR event_message LIKE '%WiFiLQAMgrSetCurrentNetwork: Joined SSID:%'
        OR event_message LIKE '%Preparing background scan request for %'
        OR event_message LIKE '%WiFiNetworkPrepareKnownBssList%'
        OR event_message LIKE '%to list of known networks%'
        OR event_message LIKE '%{AUTOJOIN, SCAN*} Scanning 2Ghz Channels found:%'
        OR event_message LIKE '%{AUTOJOIN, SCAN*} Scanning 5Ghz Channels found:%'
        OR event_message LIKE '%ATXModeDrivingFeaturizer: Driving mode%'
        OR event_message LIKE '%ATXModeCorrelatedAppsDataSource: user%'
        OR event_message LIKE '%VEHICULAR:vehicularStartTime%'
        OR event_message LIKE '%Handling com.apple.vehiclePolicy.DNDMode notification%'
        OR event_message LIKE '%Get mode configuration, identifier=com.apple.donotdisturb.mode.driving%'
        OR event_message LIKE '%Engaging Driving%'
        OR event_message LIKE '%ATXModeDrivingFeaturizer: received new DNDWD event%'
        OR event_message LIKE '%Airplane Mode is now 1%'
        OR event_message LIKE '%Airplane Mode is now On%'
        OR event_message LIKE '%Setting airplane mode to true%'
        OR event_message LIKE '%Airplane mode now active%'
        OR event_message LIKE '%Airplane mode now active%'
        OR event_message LIKE '%enabling airplanemode%'
        OR event_message LIKE '%Airplane mode changed%'
        OR event_message LIKE '%Airplane Mode is now 0%'
        OR event_message LIKE '%Airplane Mode is now Off%'
        OR event_message LIKE '%Airplane Mode is now On%'
        OR event_message LIKE '%Setting airplane mode to false%'
        OR event_message LIKE '%Airplane mode now inactive%'
        OR event_message LIKE '%Airplane mode Disabled%'
        OR event_message LIKE '%Bluetooth state changed%'
        OR event_message LIKE '%Sending new bluetooth state%'
        OR event_message LIKE '%Bluetooth state changed PoweredOn%'
        OR event_message LIKE '%ServiceManager disconnection result for%'
        OR event_message LIKE '%Device type is%'
        OR event_message LIKE '%is asking to connect device%'
        OR event_message LIKE '%Received connection result for%'
        OR event_message LIKE '%Received disconnection result for%'
        OR event_message LIKE '%Received handsfree disconnection%'
        OR event_message LIKE '%Sending ring notification for call%'
        OR event_message LIKE '%Accepting incoming audio connection%'
        OR event_message LIKE '%Received voice audio connected%'
        OR event_message LIKE '%Stopping A2DP audio streaming%'
        OR event_message LIKE '%Bluetooth A2DP device%'
        OR event_message LIKE '%Bluetooth Daemon: A2DP streaming%'
        OR event_message LIKE '%Starting Media connection to device%'
        OR event_message LIKE '%Received voice disconnection%'
        OR event_message LIKE '%Disconnecting audio from device%'
        OR event_message LIKE '%Audio was already disconnected%'
        OR event_message LIKE '%Toggled Bluetooth state from%'
        OR event_message LIKE '%CUBluetoothDevice%'
        OR event_message LIKE '%handsfree device disconnected%'
        OR event_message LIKE '%handsfree device connected%'
        OR event_message LIKE '%Bluetooth state updated%'
        OR event_message LIKE '%Bluetooth power is now off%'
        OR event_message LIKE '%Bluetooth state%'
        OR event_message LIKE '%Sending call state update%'
        OR event_message LIKE '%A2DP LinkQualityReport%'
        OR event_message LIKE '%AudioQueueIsPlaying%'
        OR event_message LIKE '%VolumeIncrement%'
        OR event_message LIKE '%rawVolumeIncreasePress%'
        OR event_message LIKE '%rawVolumeDecreasePress%'
        OR event_message LIKE '%Volume active%'
        OR event_message LIKE '%PlaybackQueueInvalidation%'
        OR event_message LIKE '%volumeValueDidChange%'
        OR event_message LIKE '%SBVolumeControl%'
        OR event_message LIKE '%SBSOSClawGestureObserver - button press noted%'
        OR event_message LIKE '%brightness change:%'
        OR event_message LIKE '%SBRingerControl activateRingerHUD%'
        OR event_message LIKE '%SBRingerHUDViewController setRingerSilent:%'
        OR event_message LIKE '%ringer state changed to:%'
        OR event_message LIKE '%Allowing tap for icon view%'
        OR event_message LIKE '%Launching application%'
        OR event_message LIKE '%transition source:%'
        OR event_message LIKE '%[Flashlight Controller]%'
        OR event_message LIKE '%<<<<AVFlashlight>>>>-%'
        OR event_message LIKE '%Tethering is now enabled with%'
        OR event_message LIKE '%Received notification that wireless modem state changed%'
        OR event_message LIKE '%Previous tethering state was%'
        OR event_message LIKE '%Proceed to%'
        OR event_message LIKE '%Turn right%'
        OR event_message LIKE '%Turn left%'
        OR event_message LIKE '%roundabout%'
        OR event_message LIKE '%first exit%'
        OR event_message LIKE '%Stay in the%'
        OR event_message LIKE '%parking lot%'
        OR event_message LIKE '%of a mile%'
        OR event_message LIKE '%In about%'
        OR event_message LIKE '%Arrived%'
        OR event_message LIKE '%destination%'
        OR event_message LIKE '%At the light%'
        OR event_message LIKE '%Starting route to%'
    '''

    data_list = get_sqlite_db_records(source_path, query)
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')

    return data_headers, data_list, source_path

@artifact_processor
def logarchive_time_change(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, '_lava_artifacts.db')
    data_list = []
    
    query = '''
    SELECT *
    FROM logarchive_artifacts
    WHERE event_message LIKE '%Time change: Clock shifted by%'
    '''
    
    data_list = get_sqlite_db_records(source_path, query)
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    
    return data_headers, data_list, source_path

@artifact_processor
def logarchive_flashlight(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, '_lava_artifacts.db')
    data_list = []
    
    query = '''
    SELECT *
    FROM logarchive_artifacts
    WHERE event_message LIKE '%[Flashlight Controller]%' 
    OR event_message LIKE '%<<<<AVFlashlight>>>>-%'
    '''
    
    data_list = get_sqlite_db_records(source_path, query)
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    
    return data_headers, data_list, source_path

@artifact_processor
def logarchive_executed_apps(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, '_lava_artifacts.db')
    data_list = []
    
    query = '''
    SELECT *
    FROM logarchive_artifacts
    WHERE event_message LIKE '%Allowing tap for icon view%'
        OR event_message LIKE '%Launching application%'
        OR event_message LIKE '%transition source:%'
    '''
    
    data_list = get_sqlite_db_records(source_path, query)
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    
    return data_headers, data_list, source_path

@artifact_processor
def logarchive_tethering(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, '_lava_artifacts.db')
    data_list = []
    
    query = '''
    SELECT *
    FROM logarchive_artifacts
    WHERE event_message LIKE '%Tethering is now enabled with%'
        OR event_message LIKE '%Received notification that wireless modem state changed%'
        OR event_message LIKE '%Previous tethering state was%'
    '''
    
    data_list = get_sqlite_db_records(source_path, query)
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    
    return data_headers, data_list, source_path

@artifact_processor
def logarchive_airplane_mode(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, '_lava_artifacts.db')
    data_list = []
    
    query = '''
    SELECT *
    FROM logarchive_artifacts
    WHERE event_message LIKE '%Airplane Mode is now 1%'
        OR event_message LIKE '%Airplane Mode is now On%'
        OR event_message LIKE '%Setting airplane mode to true%'
        OR event_message LIKE '%Airplane mode now active%'
        OR event_message LIKE '%Airplane mode now active%'
        OR event_message LIKE '%enabling airplanemode%'
        OR event_message LIKE '%Airplane mode changed%'
        OR event_message LIKE '%Airplane Mode is now 0%'
        OR event_message LIKE '%Airplane Mode is now Off%'
        OR event_message LIKE '%Airplane Mode is now On%'
        OR event_message LIKE '%Setting airplane mode to false%'
        OR event_message LIKE '%Airplane mode now inactive%'
        OR event_message LIKE '%Airplane mode Disabled%'
    '''
    
    data_list = get_sqlite_db_records(source_path, query)
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    
    return data_headers, data_list, source_path

@artifact_processor
def logarchive_lock_status(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, '_lava_artifacts.db')
    data_list = []
    
    query = '''
    SELECT *
    FROM logarchive_artifacts
    WHERE event_message LIKE '%Screen did lock%'
        OR event_message LIKE '%ScreenOn changed%'
        OR event_message LIKE '%Screen shut off%'
        OR event_message LIKE '%screen is locked%'
        OR event_message LIKE '%screen is unlocked%'
        OR event_message LIKE '%Device unlocked%'
        OR event_message LIKE '%Device lock status%'
        OR event_message LIKE '%Biometric match complete%'

    '''
    
    data_list = get_sqlite_db_records(source_path, query)
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    
    return data_headers, data_list, source_path

@artifact_processor
def logarchive_wifi_status(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, '_lava_artifacts.db')
    data_list = []
    
    query = '''
    SELECT *
    FROM logarchive_artifacts
    WHERE event_message LIKE '%WiFi state changed:%'
        OR event_message LIKE '%Toggled WiFi state%'
        OR event_message LIKE '%is WiFi associated?%'
        OR event_message LIKE '%link status changed%'
        OR event_message LIKE '%reachability changed%'
        OR event_message LIKE '%ISNetworkObserver%'
        OR event_message LIKE '%ForgetSSID%'
        OR event_message LIKE '%en0: SSID%'
        OR event_message LIKE '%Removing Lease SSID%'
        OR event_message LIKE '%SysMon: WiFi state changed:%'
        OR event_message LIKE '%WiFiManagerClientRemoveNetworkWithReason:%'
        OR event_message LIKE '%WiFiSecurityRemovePassword%'
        OR event_message LIKE '%AlwaysOnWifi:%'
        OR event_message LIKE '%WiFiDeviceManagerSetNetworks:%'
        OR event_message LIKE '%Scanning For Broadcast found:%'
        OR event_message LIKE '%Scanning Remaining Channels%'
        OR event_message LIKE '%WiFiSettlementObserver _handleScanResults%'
        OR event_message LIKE '%Attempting to join%'
        OR event_message LIKE '%WiFiLQAMgrSetCurrentNetwork: Joined SSID:%'
        OR event_message LIKE '%Preparing background scan request for %'
        OR event_message LIKE '%WiFiNetworkPrepareKnownBssList%'
        OR event_message LIKE '%to list of known networks%'
        OR event_message LIKE '%{AUTOJOIN, SCAN*} Scanning 2Ghz Channels found:%'
        OR event_message LIKE '%{AUTOJOIN, SCAN*} Scanning 5Ghz Channels found:%'
    '''
    
    data_list = get_sqlite_db_records(source_path, query)
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    
    return data_headers, data_list, source_path

@artifact_processor
def logarchive_bluetooth_status(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, '_lava_artifacts.db')
    data_list = []
    
    query = '''
    SELECT *
    FROM logarchive_artifacts
    WHERE event_message LIKE '%Bluetooth state changed%'
        OR event_message LIKE '%Sending new bluetooth state%'
        OR event_message LIKE '%Bluetooth state changed PoweredOn%'
        OR event_message LIKE '%ServiceManager disconnection result for%'
        OR event_message LIKE '%Device type is%'
        OR event_message LIKE '%is asking to connect device%'
        OR event_message LIKE '%Received connection result for%'
        OR event_message LIKE '%Received disconnection result for%'
        OR event_message LIKE '%Received handsfree disconnection%'
        OR event_message LIKE '%Sending ring notification for call%'
        OR event_message LIKE '%Accepting incoming audio connection%'
        OR event_message LIKE '%Received voice audio connected%'
        OR event_message LIKE '%Stopping A2DP audio streaming%'
        OR event_message LIKE '%Bluetooth A2DP device%'
        OR event_message LIKE '%Bluetooth Daemon: A2DP streaming%'
        OR event_message LIKE '%Starting Media connection to device%'
        OR event_message LIKE '%Received voice disconnection%'
        OR event_message LIKE '%Disconnecting audio from device%'
        OR event_message LIKE '%Audio was already disconnected%'
        OR event_message LIKE '%Toggled Bluetooth state from%'
        OR event_message LIKE '%CUBluetoothDevice%'
        OR event_message LIKE '%handsfree device disconnected%'
        OR event_message LIKE '%handsfree device connected%'
        OR event_message LIKE '%Bluetooth state updated%'
        OR event_message LIKE '%Bluetooth power is now off%'
        OR event_message LIKE '%Bluetooth state%'
        OR event_message LIKE '%Sending call state update%'
        OR event_message LIKE '%A2DP LinkQualityReport%'

    '''
    
    data_list = get_sqlite_db_records(source_path, query)
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    
    return data_headers, data_list, source_path

@artifact_processor
def logarchive_audio_status(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, '_lava_artifacts.db')
    data_list = []
    
    query = '''
    SELECT *
    FROM logarchive_artifacts
    WHERE event_message LIKE '%AudioQueueIsPlaying%'
        OR event_message LIKE '%VolumeIncrement%'
        OR event_message LIKE '%rawVolumeIncreasePress%'
        OR event_message LIKE '%rawVolumeDecreasePress%'
        OR event_message LIKE '%Volume active%'
        OR event_message LIKE '%PlaybackQueueInvalidation%'
        OR event_message LIKE '%volumeValueDidChange%'
    '''
    
    data_list = get_sqlite_db_records(source_path, query)
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    
    #Info: https://thesisfriday.com/index.php/2025/05/30/thesis-friday-8-aul-physical-buttons-volume/
    
    return data_headers, data_list, source_path

@artifact_processor
def logarchive_navigation(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, '_lava_artifacts.db')
    data_list = []
    
    query = '''
    SELECT *
    FROM logarchive_artifacts
    WHERE event_message LIKE '%Starting route to%'
        OR event_message LIKE '%Proceed to the%'
        OR event_message LIKE '%Proceed to\%'
        OR event_message LIKE '%Turn right%'
        OR event_message LIKE '%Turn left%'
        OR event_message LIKE '%roundabout%'
        OR event_message LIKE '%first exit%'
        OR event_message LIKE '%Stay in the%'
        OR event_message LIKE '%parking lot for%'
        OR event_message LIKE '%of a mile%'
        OR event_message LIKE '%In about%'
        OR event_message LIKE '%then arrive%'
        OR event_message LIKE '%your destination%'
        OR event_message LIKE '%At the light%'
        OR event_message LIKE '%Arrived\%'
    '''
    
    data_list = get_sqlite_db_records(source_path, query)
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    
    return data_headers, data_list, source_path