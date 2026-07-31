__artifacts_v2__ = {
    "logarchive": {
        "name": "logarchive",
        "description": "Processes Apple Unified Logs, either from tracev3 data in the "
                       "extraction or from a json file exported with 'log show'",
        "author": "@AlexisBrignoni",
        "creation_date": "2025-05-06",
        "last_update_date": "2026-07-29",
        "requirements": "Reading tracev3 data natively requires the unifiedlog_iterator "
                        "binary; see scripts/unifiedlogs.py",
        "category": "Unified Logs",
        "notes": "",
        # The tracev3 globs are anchored at db/, not private/var/db/: Cellebrite UFED
        # zips (and the corpus CSVs in admin/data/filepath-lists) store the data
        # partition as filesystem2/db/diagnostics with no private/var prefix, and the
        # anchored form never matched them. fnmatch's '*' crosses path separators, so
        # these cover the Apple-native layout too.
        "paths": ('*/logarchive*.json',
                  '*/db/diagnostics/*',
                  '*/db/uuidtext/*',
                  '*.logarchive/*'),
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
    "logarchive_motionstate": {
        "name": "logarchive motion state transitions",
        "description": "Motion state transition entries",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-04-30",
        "last_update_date": "2026-07-30",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "activity",
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

import os

import ijson
from datetime import datetime, timezone
from scripts import unifiedlogs
from scripts.ilapfuncs import artifact_processor, artifact_processor_streaming, get_file_path, \
    get_sqlite_db_records, logfunc

DATA_HEADERS = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID',
                'Subsystem', 'Category', 'Event Message', 'Trace ID')


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

def parse_iterator_timestamp(timestamp):
    """Parse the RFC 3339 timestamp unifiedlog_iterator emits, e.g. 2026-07-29T14:11:07.452774400Z.

    It carries nanosecond precision and a 'Z' suffix. datetime.fromisoformat() only learned
    to accept either of those in 3.11, and iLEAPP still supports 3.10, so normalize both
    here rather than depending on the interpreter version.
    """
    if not timestamp:
        return ''
    normalized = timestamp[:-1] if timestamp.endswith('Z') else timestamp
    if '.' in normalized:
        whole, fraction = normalized.split('.', 1)
        normalized = f'{whole}.{fraction[:6]}'
    try:
        return datetime.fromisoformat(normalized).replace(tzinfo=timezone.utc)
    except ValueError:
        return ''


def rows_from_json(source_path):
    """Yield rows from a 'log show --style json' export."""
    truncate_after_last_bracket(source_path)
    # Progress by file position: a log show export runs to tens of gigabytes and gave
    # no output at all while ijson chewed through it. f.tell() moves in reader buffer
    # strides, which is plenty accurate against a multi-gigabyte total.
    progress = unifiedlogs.ImportProgress(os.path.getsize(source_path))
    incval = 0
    with open(source_path, 'rb') as f:
        for record in ijson.items(f, 'item', multiple_values=True):  # if the json is a list
            if isinstance(record, dict):
                incval = incval + 1
                progress.add_record()
                if incval % unifiedlogs.ImportProgress.CHECK_EVERY == 0:
                    progress.set_bytes_done(f.tell())
                timestamp = record.get('timestamp', '')
                timestamp = convert_to_utc(timestamp) if timestamp else ''
                yield (timestamp,
                       incval,
                       record.get('processImagePath', ''),
                       record.get('processID', ''),
                       record.get('subsystem', ''),
                       record.get('category', ''),
                       str(record.get('eventMessage', '')),
                       str(record.get('traceID', '')))
    progress.finish()


def rows_from_tracev3(binary, archive_dir):
    """Yield rows parsed straight out of the tracev3 data.

    Column meanings are kept identical to the json import so the dependent artifacts, which
    all query this one table, work the same either way. Trace ID is the one exception:
    unifiedlog_iterator does not emit it, so it stays empty. No artifact queries it, and the
    parser supplies several fields Apple's json export does not (thread id, activity id,
    boot uuid, euid) that could be surfaced later.
    """
    incval = 0
    for record in unifiedlogs.stream_records(binary, archive_dir):
        incval = incval + 1
        yield (parse_iterator_timestamp(record.get('timestamp', '')),
               incval,
               record.get('process', ''),
               record.get('pid', ''),
               record.get('subsystem', ''),
               record.get('category', ''),
               str(record.get('message', '')),
               '')


@artifact_processor_streaming
def logarchive(context):
    """Import Apple Unified Logs into the LAVA database.

    Two sources, in order of preference:

      1. a 'logarchive*.json' export the examiner produced with 'log show' on a Mac, which
         stays the documented workflow and is what an examiner explicitly chose to provide;
      2. the tracev3 data in the extraction itself, read natively, which needs no Mac and no
         intermediate json file.

    Rows are streamed rather than accumulated: a full archive runs to tens of millions of
    records, which is more than fits in memory as Python tuples.
    """
    files_found = context.get_files_found()

    source_path = get_file_path(files_found, 'logarchive*.json')
    if source_path:
        return DATA_HEADERS, rows_from_json(source_path), source_path

    logarchive_dir, diagnostics_dir, uuidtext_dir = unifiedlogs.find_archive_roots(files_found)
    if not logarchive_dir and not diagnostics_dir:
        return DATA_HEADERS, iter(()), None

    binary = unifiedlogs.find_iterator()
    if not binary:
        logfunc('Unified Log tracev3 data was found but the unifiedlog_iterator binary is not '
                'available, so it cannot be read natively. Either install the binary (see '
                'scripts/unifiedlogs.py) or supply a logarchive*.json export.')
        return DATA_HEADERS, iter(()), None

    if logarchive_dir:
        archive_dir = logarchive_dir
        source_path = logarchive_dir
    else:
        if not uuidtext_dir:
            # Without uuidtext the parser cannot resolve format strings, so the messages
            # would come back as placeholders. Better to say why than to import junk.
            logfunc('Unified Log tracev3 data was found but the uuidtext directory was not, '
                    'so log messages cannot be resolved. Skipping.')
            return DATA_HEADERS, iter(()), None
        archive_dir = unifiedlogs.assemble_archive(
            diagnostics_dir, uuidtext_dir,
            os.path.join(context.get_data_folder(), '_logarchive_native'))
        source_path = f'{diagnostics_dir}\n{uuidtext_dir}'

    logfunc(f'Reading Apple Unified Logs natively with {os.path.basename(binary)}')
    return DATA_HEADERS, rows_from_tracev3(binary, archive_dir), source_path

@artifact_processor
def logarchive_artifacts(context):
    source_path = get_file_path(context.get_files_found(), '_lava_artifacts.db')
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
        -- AVFoundation's logging macro renders as '<<<< AVFlashlight >>>> -[AVFlashlight
        -- turnPowerOff]: ...' with spaces inside the brackets on iOS 17.1, which the
        -- unspaced predicate above misses entirely. Both forms are kept because the
        -- unspaced one was written from observed output on another release. The method
        -- prefix is not matched, so class methods ('+[') are picked up too.
        OR event_message LIKE '%<<<< AVFlashlight >>>>%'
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

    data_list = list( get_sqlite_db_records(source_path, query) )
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')

    return data_headers, data_list, source_path

@artifact_processor
def logarchive_time_change(context):
    source_path = get_file_path(context.get_files_found(), '_lava_artifacts.db')
    data_list = []
    
    query = '''
    SELECT *
    FROM logarchive_artifacts
    WHERE event_message LIKE '%Time change: Clock shifted by%'
    '''
    
    data_list = list( get_sqlite_db_records(source_path, query) )
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    
    return data_headers, data_list, source_path

@artifact_processor
def logarchive_flashlight(context):
    source_path = get_file_path(context.get_files_found(), '_lava_artifacts.db')
    data_list = []
    
    query = '''
    SELECT *
    FROM logarchive_artifacts
    WHERE event_message LIKE '%[Flashlight Controller]%'
    OR event_message LIKE '%<<<<AVFlashlight>>>>-%'
    -- Spaced variant; see the note in logarchive_artifacts. Both queries need it, since
    -- this artifact reads from the table that one builds.
    OR event_message LIKE '%<<<< AVFlashlight >>>>%'
    '''
    
    data_list = list( get_sqlite_db_records(source_path, query) )
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    
    return data_headers, data_list, source_path

@artifact_processor
def logarchive_executed_apps(context):
    source_path = get_file_path(context.get_files_found(), '_lava_artifacts.db')
    data_list = []
    
    query = '''
    SELECT *
    FROM logarchive_artifacts
    WHERE event_message LIKE '%Allowing tap for icon view%'
        OR event_message LIKE '%Launching application%'
        OR event_message LIKE '%transition source:%'
    '''
    
    data_list = list( get_sqlite_db_records(source_path, query) )
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    
    return data_headers, data_list, source_path

@artifact_processor
def logarchive_motionstate(context):
    source_path = get_file_path(context.get_files_found(), '_lava_artifacts.db')
    data_list = []
    
    query = '''
    SELECT *
    FROM logarchive_artifacts
    WHERE event_message LIKE '%Motion State Transition:%'
    '''
    
    data_list = list( get_sqlite_db_records(source_path, query) )
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    
    return data_headers, data_list, source_path

@artifact_processor
def logarchive_tethering(context):
    source_path = get_file_path(context.get_files_found(), '_lava_artifacts.db')
    data_list = []
    
    query = '''
    SELECT *
    FROM logarchive_artifacts
    WHERE event_message LIKE '%Tethering is now enabled with%'
        OR event_message LIKE '%Received notification that wireless modem state changed%'
        OR event_message LIKE '%Previous tethering state was%'
    '''
    
    data_list = list( get_sqlite_db_records(source_path, query) )
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    
    return data_headers, data_list, source_path

@artifact_processor
def logarchive_airplane_mode(context):
    source_path = get_file_path(context.get_files_found(), '_lava_artifacts.db')
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
    
    data_list = list( get_sqlite_db_records(source_path, query) )
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    
    return data_headers, data_list, source_path

@artifact_processor
def logarchive_lock_status(context):
    source_path = get_file_path(context.get_files_found(), '_lava_artifacts.db')
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
    
    data_list = list( get_sqlite_db_records(source_path, query) )
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    
    return data_headers, data_list, source_path

@artifact_processor
def logarchive_wifi_status(context):
    source_path = get_file_path(context.get_files_found(), '_lava_artifacts.db')
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
    
    data_list = list( get_sqlite_db_records(source_path, query) )
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    
    return data_headers, data_list, source_path

@artifact_processor
def logarchive_bluetooth_status(context):
    source_path = get_file_path(context.get_files_found(), '_lava_artifacts.db')
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
    
    data_list = list( get_sqlite_db_records(source_path, query) )
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    
    return data_headers, data_list, source_path

@artifact_processor
def logarchive_audio_status(context):
    source_path = get_file_path(context.get_files_found(), '_lava_artifacts.db')
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
    
    data_list = list( get_sqlite_db_records(source_path, query) )
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    
    #Info: https://thesisfriday.com/index.php/2025/05/30/thesis-friday-8-aul-physical-buttons-volume/
    
    return data_headers, data_list, source_path

@artifact_processor
def logarchive_navigation(context):
    source_path = get_file_path(context.get_files_found(), '_lava_artifacts.db')
    data_list = []
    
    query = '''
    SELECT *
    FROM logarchive_artifacts
    WHERE event_message LIKE '%Starting route to%'
        OR event_message LIKE '%Proceed to the%'
        OR event_message LIKE '%Proceed to\\%'
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
        OR event_message LIKE '%Arrived\\%'
    '''
    
    data_list = list( get_sqlite_db_records(source_path, query) )
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    
    return data_headers, data_list, source_path