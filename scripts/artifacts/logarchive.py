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
        "paths": ('*/logarchive.json',),
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
    }
}

import ijson
from datetime import datetime, timezone
from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, logfunc


def convert_to_utc(timestamp):
    dt_local = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f%z")
    dt_utc = dt_local.astimezone(timezone.utc)

    return dt_utc


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
    source_path = get_file_path(files_found, 'logarchive.json')
    data_list = []

    incval = 0
    if source_path:
        truncate_after_last_bracket(source_path)
        with open(source_path, 'rb') as f:
            for record in ijson.items(f, 'item', multiple_values=True ): # if the json is a list
                if isinstance(record, dict):
                    timestamp = processid = process_image_path = subsystem = ''
                    category = eventmessage = traceid = ''
                    incval = incval + 1

                    for key, value in record.items():
                        if key == 'timestamp':
                            value = convert_to_utc(value)
                            timestamp = value
                        elif key == 'processID':
                            processid = value
                        elif key == 'processImagePath':
                            process_image_path = value
                        elif key == 'subsystem':
                            subsystem = value
                        elif key == 'category':
                            category = value
                        elif key == 'eventMessage':
                            eventmessage = str(value)
                        elif key == 'traceID':
                            traceid = str(value)

                    
                    data_list.append((timestamp, incval, process_image_path, processid, subsystem,
                                      category, eventmessage, traceid))

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
        OR event_message LIKE '%ForgetSSID%'
        OR event_message LIKE '%en0: SSID%'
        OR event_message LIKE '%Removing Lease SSID%'
        OR event_message LIKE '%SysMon: WiFi state changed:%'
        OR event_message LIKE '%WiFiDeviceManagerSetNetworks:%'
        OR event_message LIKE '%Scanning For Broadcast found:%'
        OR event_message LIKE '%Scanning Remaining Channels%'
        OR event_message LIKE '%WiFiSettlementObserver _handleScanResults%'
        OR event_message LIKE '%Attempting to join%'
        OR event_message LIKE '%Preparing background scan request for %'
        OR event_message LIKE '%WiFiNetworkPrepareKnownBssList%'
        OR event_message LIKE '%to list of known networks%'
        OR event_message LIKE '%{AUTOJOIN, SCAN*} Scanning 2Ghz Channels found:%'
        OR event_message LIKE '%{AUTOJOIN, SCAN*} Scanning 5Ghz Channels found:%'
        OR event_message LIKE '%is asking to connect device%'
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

    