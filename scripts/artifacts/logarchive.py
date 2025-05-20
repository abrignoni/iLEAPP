__artifacts_v2__ = {
    "logarchive": {
        "name": "logarchive",
        "description": "Processes a json file from a logarchive",
        "author": "@AlexisBrignoni",
        "creation_date": "2025-05-06",
        "last_update_date": "2025-05-06",
        "requirements": "none",
        "category": "Logs",
        "notes": "",
        "paths": ('*/logarchive.json',),
        "output_types": "none",
        "artifact_icon": "database",
        "function": "logarchive"
    }
}

import ijson
from datetime import datetime, timezone
from scripts.lavafuncs import lava_process_artifact, lava_insert_sqlite_data
from scripts.ilapfuncs import get_file_path, get_plist_file_content, logfunc

def convert_to_utc(timestamp):
    dt_local = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f%z")
    dt_utc = dt_local.astimezone(timezone.utc)
    
    return(dt_utc)


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

def logarchive(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    data_list = []
    data_list_artifacts = []
    
    for file_found in files_found:
        file_found = str(file_found)
    
    incval = 0
    if file_found.endswith('logarchive.json'):
        truncate_after_last_bracket(file_found)
        with open(file_found, 'rb') as f:
            for record in ijson.items(f, 'item', multiple_values=True ): # if the json is a list
                if isinstance(record, dict):
                    timestamp = processid = subsystem = category = eventmessage = traceid = ''
                    incval = incval + 1
                    
                    for key, value in record.items():
                        if key == 'timestamp':
                            value = convert_to_utc(value)
                            timestamp = value
                        elif key == 'processID':
                            processid = value
                        elif key == 'processImagePath':
                            processImagePath = value
                        elif key == 'subsystem':
                            subsystem = value
                        elif key == 'category':
                            category = value
                        elif key == 'eventMessage':
                            eventmessage = str(value)
                        elif key == 'traceID':
                            traceid = str(value)

                    #print(timestamp, processid, subsystem, category, eventmessage, traceid)
                    
                    data_list.append((timestamp, incval, processImagePath, processid, subsystem, category, eventmessage, traceid))

                    #Identification and aggregation of relevant artifacts
                    if ('Take screenshot' in eventmessage or
                        'charger connected state change' in eventmessage or
                        'Motion State Transition:' in eventmessage or
                        'CarPlay Connection Event:' in eventmessage or
                        'CoreAnalytics event: com.apple.accessories.connection.added' in eventmessage or
                        'Start #SpeechRequest id' in eventmessage or
                        'Received Orientation' in eventmessage or
                        'Effective device orientation' in eventmessage or
                        'Received: Face' in eventmessage or
                        'AppleAccount Authenticated:' in eventmessage or
                        '=> Transitioning to state:' in eventmessage or
                        'Received: Screen' in eventmessage or
                        'Screen did lock' in eventmessage or
                        'ScreenOn changed' in eventmessage or
                        'Screen shut off' in eventmessage or
                        'screen is locked' in eventmessage or
                        'screen is unlocked' in eventmessage or
                        'Device unlocked' in eventmessage or
                        'Device lock status' in eventmessage or
                        'Biometric match complete' in eventmessage or
                        'SBIconView touches began with event:' in eventmessage or
                        'Setting process visibility' in eventmessage or
                        'WiFi state changed:' in eventmessage or
                        'Toggled WiFi state' in eventmessage or
                        'is WiFi associated?' in eventmessage or
                        'ForgetSSID' in eventmessage or
                        'en0: SSID' in eventmessage or
                        'Removing Lease SSID' in eventmessage or
                        'SysMon: WiFi state changed:' in eventmessage or
                        'WiFiDeviceManagerSetNetworks:' in eventmessage or 
                        'Scanning For Broadcast found:' in eventmessage or
                        'Scanning Remaining Channels' in eventmessage or
                        'WiFiSettlementObserver _handleScanResults' in eventmessage or
                        'Attempting to join' in eventmessage or
                        'Preparing background scan request for ' in eventmessage or
                        'WiFiNetworkPrepareKnownBssList' in eventmessage or
                        'to list of known networks' in eventmessage or
                        '{AUTOJOIN, SCAN*} Scanning 2Ghz Channels found:' in eventmessage or
                        '{AUTOJOIN, SCAN*} Scanning 5Ghz Channels found:' in eventmessage or
                        'is asking to connect device' in eventmessage or
                        'ATXModeDrivingFeaturizer: Driving mode' in eventmessage or
                        'ATXModeCorrelatedAppsDataSource: user' in eventmessage):
                        data_list_artifacts.append((timestamp, incval, processImagePath, processid, subsystem, category, eventmessage, traceid))
                
    #Create LAVA tables
    category = "Logs"
    module_name = "logarchive"
        
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 'Subsystem', 'Category', 'Event Message', 'Trace ID')
    table_name1, object_columns1, column_map1 = lava_process_artifact(category, module_name, 'Log Archive', data_headers, len(data_list))
    lava_insert_sqlite_data(table_name1, data_list, object_columns1, data_headers, column_map1)
    
    
    data_headers_artifacts = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 'Subsystem', 'Category', 'Event Message', 'Trace ID')
    table_name2, object_columns2, column_map2 = lava_process_artifact(category, module_name, 'Log Archive Artifacts', data_headers_artifacts, len(data_list_artifacts))
    lava_insert_sqlite_data(table_name2, data_list_artifacts, object_columns2, data_headers_artifacts, column_map2)

    