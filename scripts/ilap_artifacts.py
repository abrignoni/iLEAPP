# To add a new artifact module, import it here as shown below:
#     from scripts.artifacts.fruitninja import get_fruitninja
# Also add the grep search for that module using the same name
# to the 'tosearch' data structure.

import traceback

from time import process_time, gmtime, strftime
from scripts.artifacts.accs import get_accs
from scripts.artifacts.addressBook import get_addressBook
from scripts.artifacts.aggDict import get_aggDict
from scripts.artifacts.aggDictScalars import get_aggDictScalars
from scripts.artifacts.aggDictpasscode import get_aggDictpasscode
from scripts.artifacts.aggDictpasscodetype import get_aggDictpasscodetype
from scripts.artifacts.appConduit import get_appConduit
from scripts.artifacts.appGrouplisting import get_appGrouplisting
from scripts.artifacts.appItunesmeta import get_appItunesmeta
from scripts.artifacts.appSnapshots import get_applicationSnapshots
from scripts.artifacts.appleMapsApplication import get_appleMapsApplication
from scripts.artifacts.appleMapsGroup import get_appleMapsGroup
from scripts.artifacts.appleWifiPlist import get_appleWifiPlist
from scripts.artifacts.applewalletTransactions import get_applewalletTransactions
from scripts.artifacts.applicationstate import get_applicationstate
from scripts.artifacts.bluetoothOther import get_bluetoothOther
from scripts.artifacts.bluetoothPaired import get_bluetoothPaired
from scripts.artifacts.bluetoothPairedReg import get_bluetoothPairedReg
from scripts.artifacts.cacheRoutesGmap import get_cacheRoutesGmap
from scripts.artifacts.calendarAll import get_calendarAll
from scripts.artifacts.callHistory import get_callHistory
from scripts.artifacts.celWireless import get_celWireless
from scripts.artifacts.cloudkitNoteSharing import get_cloudkitNoteSharing
from scripts.artifacts.cloudkitParticipants import get_cloudkitParticipants
from scripts.artifacts.conDev import get_conDev
from scripts.artifacts.confaccts import get_confaccts
from scripts.artifacts.coreDuetAirplane import get_coreDuetAirplane
from scripts.artifacts.coreDuetLock import get_coreDuetLock
from scripts.artifacts.coreDuetPlugin import get_coreDuetPlugin
from scripts.artifacts.dataArk import get_dataArk
from scripts.artifacts.dataUsageA import get_dataUsageA
from scripts.artifacts.dataUsageB import get_dataUsageB
from scripts.artifacts.dataUsageProcessA import get_dataUsageProcessA
from scripts.artifacts.dataUsageProcessB import get_dataUsageProcessB
from scripts.artifacts.deviceActivator import get_deviceActivator
from scripts.artifacts.dhcphp import get_dhcphp
from scripts.artifacts.dhcpl import get_dhcpl
from scripts.artifacts.discordAcct import get_discordAcct
from scripts.artifacts.discordJson import get_discordJson
from scripts.artifacts.discordManifest import get_discordManifest
from scripts.artifacts.filesAppsclient import get_filesAppsclient
from scripts.artifacts.filesAppsdb import get_filesAppsdb
from scripts.artifacts.filesAppsm import get_filesAppsm
from scripts.artifacts.geodApplications import get_geodApplications
from scripts.artifacts.geodMapTiles import get_geodMapTiles
from scripts.artifacts.geodPDPlaceCache import get_geodPDPlaceCache
from scripts.artifacts.healthAll import get_healthAll
from scripts.artifacts.iCloudWifi import get_iCloudWifi
from scripts.artifacts.icloudSharedalbums import get_icloudSharedalbums
from scripts.artifacts.iconsScreen import get_iconsScreen
from scripts.artifacts.interactionCcontacts import get_interactionCcontacts
from scripts.artifacts.kikMessages import get_kikMessages
from scripts.artifacts.knowCall import get_knowCall
from scripts.artifacts.lastBuild import get_lastBuild, get_iTunesBackupInfo
from scripts.artifacts.locationDallB import get_locationDallB
from scripts.artifacts.locationDparked import get_locationDparked
from scripts.artifacts.locationDparkedhistorical import get_locationDparkedhistorical
from scripts.artifacts.locationDsteps import get_locationDsteps
from scripts.artifacts.mailprotect import get_mailprotect
from scripts.artifacts.mediaLibrary import get_mediaLibrary
from scripts.artifacts.mobileActivationLogs import get_mobileActivationLogs
from scripts.artifacts.mobileBackup import get_mobileBackup
from scripts.artifacts.mobileContainerManager import get_mobileContainerManager
from scripts.artifacts.mobileInstall import get_mobileInstall
from scripts.artifacts.notificationsXI import get_notificationsXI
from scripts.artifacts.notificationsXII import get_notificationsXII
from scripts.artifacts.ooklaSpeedtestData import get_ooklaSpeedtestData
from scripts.artifacts.photosMetadata import get_photosMetadata
from scripts.artifacts.powerlogAll import get_powerlogAll
from scripts.artifacts.powerlogGZ import get_powerlogGZ
from scripts.artifacts.queryPredictions import get_queryPredictions
from scripts.artifacts.routineDCloud import get_routineDCloud
from scripts.artifacts.routineDLocationsLocal import get_routineDLocationsLocal
from scripts.artifacts.routineDlocations import get_routineDlocations
from scripts.artifacts.safariBookmarks import get_safariBookmarks
from scripts.artifacts.safariHistory import get_safariHistory
from scripts.artifacts.safariTabs import get_safariTabs
from scripts.artifacts.safariWebsearch import get_safariWebsearch
from scripts.artifacts.screentimeAll import get_screentimeAll
from scripts.artifacts.sms import get_sms
from scripts.artifacts.tileApp import get_tileApp
from scripts.artifacts.tileAppDb import get_tileAppDb
from scripts.artifacts.tileAppDisc import get_tileAppDisc
from scripts.artifacts.discordJson import get_discordJson
from scripts.artifacts.discordAcct import get_discordAcct
from scripts.artifacts.discordManifest import get_discordManifest
from scripts.artifacts.filesAppsm import get_filesAppsm
from scripts.artifacts.filesAppsdb import get_filesAppsdb
from scripts.artifacts.filesAppsclient import get_filesAppsclient
from scripts.artifacts.icloudSharedalbums import get_icloudSharedalbums
from scripts.artifacts.appGrouplisting import get_appGrouplisting
from scripts.artifacts.deviceActivator import get_deviceActivator
from scripts.artifacts.kikMessages import get_kikMessages
from scripts.artifacts.appItunesmeta import get_appItunesmeta
from scripts.artifacts.cloudkitParticipants import get_cloudkitParticipants
from scripts.artifacts.cloudkitNoteSharing import get_cloudkitNoteSharing
from scripts.artifacts.applewalletTransactions import get_applewalletTransactions
from scripts.artifacts.walStrings import get_walStrings
from scripts.artifacts.webClips import get_webClips
from scripts.artifacts.tcc import get_tcc
from scripts.artifacts.tileAppNetDb import get_tileAppNetDb
from scripts.artifacts.walStrings import get_walStrings
from scripts.artifacts.webClips import get_webClips
from scripts.artifacts.reminders import get_reminders
from scripts.artifacts.voiceTriggers import get_voiceTriggers
from scripts.artifacts.voiceRecordings import get_voiceRecordings

from scripts.ilapfuncs import *

# GREP searches for each module
# Format is Key='modulename', Value=Tuple('Module Pretty Name', 'regex term')
#   regex_term can be a string or a list/tuple of strings
# Here modulename must match the get_xxxxxx function name for that module. 
# For example: If modulename='profit', function name must be get_profit(..)
# Don't forget to import the module above!!!!


tosearch = {'lastBuild': ('IOS Build', '*LastBuildInfo.plist'),
            'accs': ('Accounts', '**/Accounts3.sqlite'),
            'addressBook': ('Address Book', '**/AddressBook.sqlitedb'),
            'aggDictpasscode': ('Aggregate Dictionary', '*/AggregateDictionary/ADDataStore.sqlitedb'),
            'aggDictpasscodetype': ('Aggregate Dictionary', '*/AggregateDictionary/ADDataStore.sqlitedb'),
            'appConduit': ('App Conduit', '**/AppConduit.log.*'),
            'appGrouplisting': ('Installed Apps', ('*/private/var/mobile/Containers/Shared/AppGroup/*/*.metadata.plist',
                                                   '**/PluginKitPlugin/*.metadata.plist')),
            'appItunesmeta': ('Installed Apps', ('**/iTunesMetadata.plist', '**/BundleMetadata.plist')),
            'appleMapsApplication': ('Locations', '**/Data/Application/*/Library/Preferences/com.apple.Maps.plist'),
            'appleMapsGroup': ('Locations', '**/Shared/AppGroup/*/Library/Preferences/group.com.apple.Maps.plist'),
            'appleWifiPlist': ('Wireless Networks', (
            '**/com.apple.wifi.plist', '**/com.apple.wifi-networks.plist.backup',
            '**/com.apple.wifi.known-networks.plist', '**/com.apple.wifi-private-mac-networks.plist')),
            'applewalletTransactions': ('Apple Wallet', '**/passes23.sqlite'),
            'applicationSnapshots': ('Installed Apps', ('**/Library/Caches/Snapshots/*', '**/SplashBoard/Snapshots/*')),
            'applicationstate': ('Installed Apps', '**/applicationState.db'),
            # 'appUpdates':('App Updates', '**/AppUpdates.sqlitedb'),
            'bluetoothOther': ('Bluetooth', '**/Library/Database/com.apple.MobileBluetooth.ledevices.other.db'),
            'bluetoothPaired': ('Bluetooth', '**/com.apple.MobileBluetooth.ledevices.paired.db'),
            'bluetoothPairedReg': ('Bluetooth', '**/com.apple.MobileBluetooth.devices.plist'),
            'cacheRoutesGmap': ('Locations', '**/Library/Application Support/CachedRoutes/*.plist'),
            'calendarAll': ('Calendar', '**/Calendar.sqlitedb'),
            'callHistory': ('Call logs', '**/CallHistory.storedata'),
            'celWireless': ('Cellular Wireless', '*wireless/Library/Preferences/com.apple.*'),
            'cloudkitNoteSharing': ('Cloudkit', '*NoteStore.sqlite*'),
            'cloudkitParticipants': ('Cloudkit', '*NoteStore.sqlite*'),
            'conDev': ('Connected to', '**/iTunes_Control/iTunes/iTunesPrefs'),
            'confaccts': ('Accounts', '**/com.apple.accounts.exists.plist'),
            'coreDuetAirplane': ('CoreDuet', '**/coreduetd.db'),
            'coreDuetLock': ('CoreDuet', '**/coreduetd.db'),
            'coreDuetPlugin': ('CoreDuet', '**/coreduetd.db'),
            'dataArk': ('IOS Build', '**/Library/Lockdown/data_ark.plist'),
            'dataUsageA': ('Data Usage', '**/DataUsage.sqlite'),
            'dataUsageB': ('Data Usage', '**/DataUsage-watch.sqlite'),
            'dataUsageProcessA': ('Data Usage', '**/DataUsage-watch.sqlite'),
            'dataUsageProcessB': ('Data Usage', '**/DataUsage.sqlite'),
            'deviceActivator': ('IOS Build', '*private/var/mobile/Library/Logs/mobileactivationd/ucrt_oob_request.txt'),
            'dhcphp': ('DHCP', '**/private/var/db/dhcpd_leases*'),
            'dhcpl': ('DHCP', '**/private/var/db/dhcpclient/leases/en*'),
            'discordAcct': ('Discord', '*/var/mobile/Containers/Data/Application/*/Documents/mmkv/mmkv.default'),
            'discordJson': ('Discord', '*/com.hammerandchisel.discord/fsCachedData/*'),
            'discordManifest': ('Discord',
                                '*/private/var/mobile/Containers/Data/Application/*/Documents/RCTAsyncLocalStorage_V1/manifest.json'),
            'filesAppsclient': (
            'Files App', '*private/var/mobile/Library/Application Support/CloudDocs/session/db/client.db*'),
            'filesAppsdb': (
            'Files App', '*private/var/mobile/Library/Application Support/CloudDocs/session/db/server.db*'),
            'filesAppsm': ('Files App', '*private/var/mobile/Containers/Shared/AppGroup/*/smartfolders.db*'),
            'geodApplications': ('Geolocation', '**/AP.db'),
            'geodMapTiles': ('Geolocation', '**/MapTiles.sqlitedb'),
            'geodPDPlaceCache': ('Geolocation', '**/PDPlaceCache.db'),
            'healthAll': ('Health Data', '**/healthdb_secure.sqlite'),
            'iCloudWifi': ('Wifi Connections', '**/com.apple.wifid.plist'),
            'icloudSharedalbums': (
            'iCloud Shared Albums', '*/private/var/mobile/Media/PhotoData/PhotoCloudSharingData/*'),
            'iconsScreen': ('iOS Screens', '**/SpringBoard/IconState.plist'),
            'interactionCcontacts': ('InteractionC', '**/interactionC.db'),
            'kikMessages': ('Kik', '**/kik.sqlite*'),
            'knowCall': ('KnowledgeC', '**/CoreDuet/Knowledge/knowledgeC.db'),
            'locationDallB': ('Locations', '**/cache_encryptedB.db'),
            'locationDparked': ('Locations', '**/Local.sqlite'),
            'locationDparkedhistorical': ('Locations', '**/Local.sqlite'),
            'mailprotect': ('iOS Mail', '**/private/var/mobile/Library/Mail/* Index*'),
            'mediaLibrary': ('Media Library', '**/Medialibrary.sqlitedb'),
            'mobileActivationLogs': ('Mobile Activation Logs', '**/mobileactivationd.log*'),
            'mobileBackup': ('Mobile Backup', '*/Preferences/com.apple.MobileBackup.plist'),
            'mobileContainerManager': ('Mobile Container Manager', '**/containermanagerd.log.*'),
            # 'appUpdates':('App Updates', '**/AppUpdates.sqlitedb'),
            'appConduit': ('App Conduit', '**/AppConduit.log.*'),
            'mediaLibrary': ('Media Library', '**/Medialibrary.sqlitedb'),
            'geodMapTiles': ('Geolocation', '**/MapTiles.sqlitedb'),
            'geodPDPlaceCache': ('Geolocation', '**/PDPlaceCache.db'),
            'geodApplications': ('Geolocation', '**/AP.db'),
            'tcc': ('App Permissions', '*TCC.db*'),
            'mobileInstall': ('Mobile Installation Logs', '**/mobile_installation.log.*'),
            'notificationsXI': ('Notifications', '*PushStore*'),
            'notificationsXII': ('Notifications', '*private/var/mobile/Library/UserNotifications*'),
            'ooklaSpeedtestData': ('Applications', '**/speedtest.sqlite*'),
            'photosMetadata': ('Photos', '**/Photos.sqlite'),
            'powerlogAll': ('Powerlog', '**/CurrentPowerlog.PLSQL'),
            'powerlogGZ': ('Powerlog Backups', '**/Library/BatteryLife/Archives/powerlog_*.PLSQL.gz'),
            'queryPredictions': ('SMS & iMessage', '**/query_predictions.db'),
            'routineDCloud': ('Locations', '**/Library/Caches/com.apple.routined/Cloud-V2.sqlite*'),
            'routineDLocationsLocal': (
            'Locations', '**/private/var/mobile/Library/Caches/com.apple.routined/Local.sqlite*'),
            'routineDlocations': ('Locations', '**/com.apple.routined/Cache.sqlite*'),
            'safariBookmarks': ('Safari Browser', '**/Safari/Bookmarks.db'),
            'safariHistory': ('Safari Browser', '**/Safari/History.db'),
            'safariTabs': ('Safari Browser', '**/Safari/BrowserState.db'),
            'safariWebsearch': ('Safari Browser', '**/Safari/History.db'),
            'screentimeAll': ('Screentime', '**/RMAdminStore-Local.sqlite'),
            'sms': ('SMS & iMessage', '**/sms.db'),
            # 'systemVersion':('Device Info', '**/SystemVersion.plist'),
            'tileApp': (
            'Locations', '*private/var/mobile/Containers/Data/Application/*/Library/log/com.thetileapp.tile*'),
            'tileAppDb': (
            'Locations', '*private/var/mobile/Containers/Shared/AppGroup/*/com.thetileapp.tile-TileNetworkDB.sqlite*'),
            'tileAppDisc': ('Accounts',
                            '*/private/var/mobile/Containers/Shared/AppGroup/*/com.thetileapp.tile-DiscoveredTileDB.sqlite*'),
            'tileAppNetDb': (
            'Accounts', '*/private/var/mobile/Containers/Shared/AppGroup/*/com.thetileapp.tile-TileNetworkDB.sqlite*'),
            'walStrings': ('SQLite Journaling', ('**/*-wal', '**/*-journal')),
            'webClips': ('iOS Screens', '*WebClips/*.webclip/*'),
            'reminders': ('Reminders', '**/Reminders/Container_v1/Stores/*.sqlite'),
            'voiceRecordings': (
            'Voice-Recordings', ('**/Recordings/*.composition/manifest.plist', '**/Recordings/*.m4a')),
            'voiceTriggers': ('Voice-Triggers', ('**/td/audio/*.json', '**/td/audio/*.wav')),
            }

'''
#    Artifacts take long to run. Useful in specific situations only.
#    'aggDict':('Aggregate Dictionary', '*/AggregateDictionary/ADDataStore.sqlitedb')
#    'aggDictScalars':('Aggregate Dictionary', '*/AggregateDictionary/ADDataStore.sqlitedb')
'''

slash = '\\' if is_platform_windows() else '/'


def process_artifact(files_found, artifact_func, artifact_name, seeker, report_folder_base):
    ''' Perform the common setup for each artifact, ie, 
        1. Create the report folder for it
        2. Fetch the method (function) and call it
        3. Wrap processing function in a try..except block

        Args:
            files_found: list of files that matched regex

            artifact_func: method to call

            artifact_name: Pretty name of artifact

            seeker: FileSeeker object to pass to method
    '''
    start_time = process_time()
    logfunc('{} [{}] artifact executing'.format(artifact_name, artifact_func))
    report_folder = os.path.join(report_folder_base, artifact_name) + slash
    try:
        if os.path.isdir(report_folder):
            pass
        else:
            os.makedirs(report_folder)
    except Exception as ex:
        logfunc('Error creating {} report directory at path {}'.format(artifact_name, report_folder))
        logfunc('Reading {} artifact failed!'.format(artifact_name))
        logfunc('Error was {}'.format(str(ex)))
        return
    try:
        method = globals()['get_' + artifact_func]
        method(files_found, report_folder, seeker)
    except Exception as ex:
        logfunc('Reading {} artifact had errors!'.format(artifact_name))
        logfunc('Error was {}'.format(str(ex)))
        logfunc('Exception Traceback: {}'.format(traceback.format_exc()))
        return

    end_time = process_time()
    run_time_secs = end_time - start_time
    # run_time_HMS = strftime('%H:%M:%S', gmtime(run_time_secs))
    logfunc('{} [{}] artifact completed in time {} seconds'.format(artifact_name, artifact_func, run_time_secs))
