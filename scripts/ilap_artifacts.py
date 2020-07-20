# To add a new artifact module, import it here as shown below:
#     from scripts.artifacts.fruitninja import get_fruitninja
# Also add the grep search for that module using the same name
# to the 'tosearch' data structure.

import traceback

from scripts.artifacts.applicationstate import get_applicationstate
from scripts.artifacts.journalStrings import get_journalStrings 
from scripts.artifacts.walStrings import get_walStrings
from scripts.artifacts.confaccts import get_confaccts
from scripts.artifacts.accs import get_accs
from scripts.artifacts.callHistory import get_callHistory
from scripts.artifacts.conDev import get_conDev
from scripts.artifacts.dataUsageA import get_dataUsageA
from scripts.artifacts.dataUsageProcessA import get_dataUsageProcessA
from scripts.artifacts.dataUsageB import get_dataUsageB
from scripts.artifacts.dataUsageProcessB import get_dataUsageProcessB
from scripts.artifacts.mobileInstall import get_mobileInstall
from scripts.artifacts.sms import get_sms
from scripts.artifacts.lastBuild import get_lastBuild
from scripts.artifacts.dataArk import get_dataArk
from scripts.artifacts.iconsScreen import get_iconsScreen
from scripts.artifacts.webClips import get_webClips
from scripts.artifacts.notificationsXII import get_notificationsXII
from scripts.artifacts.notificationsXI import get_notificationsXI
from scripts.artifacts.celWireless import get_celWireless
from scripts.artifacts.knowCincept import get_knowCincept
from scripts.artifacts.knowCusage import get_knowCusage
from scripts.artifacts.knowCact import get_knowCact
from scripts.artifacts.knowCinfocus import get_knowCinfocus
from scripts.artifacts.knowCbatlvl import get_knowCbatlvl
from scripts.artifacts.knowClocked import get_knowClocked
from scripts.artifacts.knowCplugged import get_knowCplugged
from scripts.artifacts.knowCsiri import get_knowCsiri
from scripts.artifacts.aggDict import get_aggDict
from scripts.artifacts.aggDictScalars import get_aggDictScalars
from scripts.artifacts.coreDuetAirplane import get_coreDuetAirplane
from scripts.artifacts.coreDuetLock import get_coreDuetLock
from scripts.artifacts.coreDuetPlugin import get_coreDuetPlugin
from scripts.artifacts.healthDistance import get_healthDistance
from scripts.artifacts.healthEcg import get_healthEcg
from scripts.artifacts.healthFlights import get_healthFlights
from scripts.artifacts.healthHr import get_healthHr
from scripts.artifacts.healthSteps import get_healthSteps
from scripts.artifacts.healthStandup import get_healthStandup
from scripts.artifacts.healthWeight import get_healthWeight
from scripts.artifacts.healthCadence import get_healthCadence
from scripts.artifacts.healthElevation import get_healthElevation
from scripts.artifacts.healthWorkoutGen import get_healthWorkoutGen
from scripts.artifacts.healthAll import get_healthAll
from scripts.artifacts.interactionCcontacts import get_interactionCcontacts
from scripts.artifacts.knowCnotes import get_knowCnotes
from scripts.artifacts.knowCactivitylvl import get_knowCactivitylvl
from scripts.artifacts.knowCappact import get_knowCappact
from scripts.artifacts.knowCappactcal import get_knowCappactcal
from scripts.artifacts.knowCappactsafari import get_knowCappactsafari
from scripts.artifacts.knowCinstall import get_knowCinstall
from scripts.artifacts.safariHistory import get_safariHistory
from scripts.artifacts.safariWebsearch import get_safariWebsearch
from scripts.artifacts.queryPredictions import get_queryPredictions
from scripts.artifacts.dhcpl import get_dhcpl
from scripts.artifacts.dhcphp import get_dhcphp
from scripts.artifacts.powerlogWifiprop import get_powerlogWifiprop
from scripts.artifacts.powerlogVolumePercentage import get_powerlogVolumePercentage
from scripts.artifacts.powerlogVideo import get_powerlogVideo
from scripts.artifacts.powerlogTorch import get_powerlogTorch
from scripts.artifacts.powerlogTimezone import get_powerlogTimezone
from scripts.artifacts.powerlogAggnotifications import get_powerlogAggnotifications
from scripts.artifacts.powerlogAggbulletins import get_powerlogAggbulletins
from scripts.artifacts.powerlogPushreceived import get_powerlogPushreceived
from scripts.artifacts.powerlogProcessdatausage import get_powerlogProcessdatausage
from scripts.artifacts.powerlogPaireddevconf import get_powerlogPaireddevconf
from scripts.artifacts.powerlogLocuseapp import get_powerlogLocuseapp
from scripts.artifacts.powerlogAirdrop import get_powerlogAirdrop
from scripts.artifacts.powerlogAudio import get_powerlogAudio
from scripts.artifacts.powerlogLightplug import get_powerlogLightplug
from scripts.artifacts.powerlogAppinfo import get_powerlogAppinfo
from scripts.artifacts.powerlogBackupinfo import get_powerlogBackupinfo
from scripts.artifacts.powerlogDeletedapps import get_powerlogDeletedapps
from scripts.artifacts.powerlogAll import get_powerlogAll
from scripts.artifacts.knowClocation import get_knowClocation
from scripts.artifacts.knowCappshortcut import get_knowCappshortcut
from scripts.artifacts.knowCwebusage import get_knowCwebusage
from scripts.artifacts.knowCbluetooth import get_knowCbluetooth
from scripts.artifacts.knowCmediaplaying import get_knowCmediaplaying
from scripts.artifacts.knowCcarplaycon import get_knowCcarplaycon
from scripts.artifacts.knowCinferredmotion import get_knowCinferredmotion
from scripts.artifacts.knowCbacklit import get_knowCbacklit
from scripts.artifacts.knowCorientation import get_knowCorientation
from scripts.artifacts.knowCwatchnear import get_knowCwatchnear
from scripts.artifacts.knowCdisksub import get_knowCdisksub
from scripts.artifacts.knowCsafari import get_knowCsafari
from scripts.artifacts.knowCdonotdisturb import get_knowCdonotdisturb
from scripts.artifacts.knowCuserwaking import get_knowCuserwaking
from scripts.artifacts.knowCwidget import get_knowCwidget
from scripts.artifacts.locationDparkedhistorical import get_locationDparkedhistorical
from scripts.artifacts.locationDparked import get_locationDparked
from scripts.artifacts.knowCall import get_knowCall
from scripts.artifacts.mailprotect import get_mailprotect
from scripts.artifacts.screentimeGenerichour import get_screentimeGenerichour
from scripts.artifacts.screentimeTimeditems import get_screentimeTimeditems
from scripts.artifacts.screentimeCounteditems import get_screentimeCounteditems
from scripts.artifacts.screentimeAll import get_screentimeAll
from scripts.artifacts.bluetoothPaired import get_bluetoothPaired
from scripts.artifacts.bluetoothOther import get_bluetoothOther
from scripts.artifacts.locationDcellloc import get_locationDcellloc
from scripts.artifacts.locationDappharvest import get_locationDappharvest
from scripts.artifacts.locationDcdmaloc1 import get_locationDcdmaloc1
from scripts.artifacts.locationDwifilocB import get_locationDwifilocB
from scripts.artifacts.locationDlteloc import get_locationDlteloc
from scripts.artifacts.locationDsteps import get_locationDsteps
from scripts.artifacts.locationDallB import get_locationDallB
from scripts.artifacts.calendarAll import get_calendarAll
from scripts.artifacts.photosMetadata import get_photosMetadata
from scripts.artifacts.aggDictpasscode import get_aggDictpasscode
from scripts.artifacts.aggDictpasscodetype import get_aggDictpasscodetype
from scripts.artifacts.ooklaSpeedtestData import get_ooklaSpeedtestData

from scripts.ilapfuncs import *

# GREP searches for each module
# Format is Key='modulename', Value=Tuple('Module Pretty Name', 'regex term')
# Here modulename must match the get_xxxxxx function name for that module. 
# For example: If modulename='profit', function name must be get_profit(..)
# Don't forget to import the module above!!!!


tosearch = {'lastBuild':('IOS Build', '*LastBuildInfo.plist'),
            'aggDictpasscode':('Aggregate Dictionary', '*/AggregateDictionary/ADDataStore.sqlitedb'),
            'aggDictpasscodetype':('Aggregate Dictionary', '*/AggregateDictionary/ADDataStore.sqlitedb'),
            'dataArk':('IOS Build', '**/Library/Lockdown/data_ark.plist'),
            'applicationstate':('Installed Apps', '**/applicationState.db'),
            'accs':('Accounts', '**/Accounts3.sqlite'),
            'confaccts':('Accounts', '**/com.apple.accounts.exists.plist'),
            'callHistory':('Call logs', '**/CallHistory.storedata'),
            'conDev':('Connected to', '**/iTunes_Control/iTunes/iTunesPrefs'),
            'coreDuetAirplane':('CoreDuet', '**/coreduetd.db'),
            'coreDuetLock':('CoreDuet', '**/coreduetd.db'),
            'coreDuetPlugin':('CoreDuet', '**/coreduetd.db'),
            'safariHistory':('Safari Browser', '**/Safari/History.db'),
            'safariWebsearch':('Safari Browser', '**/Safari/History.db'),
            'queryPredictions':('SMS & iMessage', '**/query_predictions.db'),
            'dhcpl':('DHCP', '**/private/var/db/dhcpclient/leases/en*'),
            'dhcphp':('DHCP', '**/private/var/db/dhcpd_leases*'),
            'dataUsageA':('Data Usage', '**/DataUsage.sqlite'), 
            'dataUsageB':('Data Usage', '**/DataUsage-watch.sqlite'),
            'dataUsageProcessA':('Data Usage', '**/DataUsage-watch.sqlite'),
            'dataUsageProcessB':('Data Usage', '**/DataUsage.sqlite'),
            'mobileInstall':('Mobile Installation Logs', '**/mobile_installation.log.*'), 
            'sms':('SMS & iMessage', '**/sms.db'),
            'iconsScreen':('iOS Screens', '**/SpringBoard/IconState.plist'),
            'webClips':('iOS Screens', '*WebClips/*.webclip/*'),
            'notificationsXI':('Notifications', '*PushStore*'),
            'notificationsXII':('Notifications', '*private/var/mobile/Library/UserNotifications*'),
            'celWireless':('Cellular Wireless', '*wireless/Library/Preferences/com.apple.*'),
            'knowCall':('KnowledgeC', '**/CoreDuet/Knowledge/knowledgeC.db'),
            'powerlogAll':('Powerlog', '**/CurrentPowerlog.PLSQL'),
            'healthAll':('Health Data', '**/healthdb_secure.sqlite'),
            'locationDallB':('LocationD', '**/cache_encryptedB.db'),
            'screentimeAll':('Screentime', '**/RMAdminStore-Local.sqlite'),
            'mailprotect':('iOS Mail', '**/private/var/mobile/Library/Mail/* Index*'),
            'locationDparkedhistorical':('RoutineD', '**/Local.sqlite'),
            'locationDparked':('RoutineD', '**/Local.sqlite'),
            'bluetoothPaired':('Bluetooth', '**/Library/Database/com.apple.MobileBluetooth.ledevices.paired.db'),
            'bluetoothOther':('Bluetooth', '**/Library/Database/com.apple.MobileBluetooth.ledevices.other.db'),
            'calendarAll':('Calendar', '**/Calendar.sqlitedb'),
            'photosMetadata':('Photos', '**/Photos.sqlite'),
            'ooklaSpeedtestData':('Applications', '**/speedtest.sqlite*')
            }

'''
tosearch = {'lastBuild':('IOS Build', '*LastBuildInfo.plist'),
            'knowCinstall':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db')
            }

# Individual artifacts. Slow parsing when extracting the same data multiple times for each artifact.
tosearch = {'lastBuild':('IOS Build', '*LastBuildInfo.plist'),
    'aggDictpasscode':('Aggregate Dictionary', '*/AggregateDictionary/ADDataStore.sqlitedb'),
    'aggDictpasscodetype':('Aggregate Dictionary', '*/AggregateDictionary/ADDataStore.sqlitedb'),
    'knowCincept':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCusage':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCact':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCinfocus':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCbatlvl':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowClocked':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCplugged':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCsiri':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCnotes':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCactivitylvl':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCappact':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCappactcal':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCappactsafari':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCinstall':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowClocation':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCappshortcut':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCwebusage':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCbluetooth':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCmediaplaying':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCcarplaycon':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCinferredmotion':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCbacklit':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCorientation':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCwatchnear':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCdisksub':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCsafari':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCdonotdisturb':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCuserwaking':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'knowCwidget':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
    'powerlogWifiprop':('Powerlog', '**/CurrentPowerlog.PLSQL'),
    'powerlogVolumePercentage':('Powerlog', '**/CurrentPowerlog.PLSQL'),
    'powerlogTorch':('Powerlog', '**/CurrentPowerlog.PLSQL'),
    'powerlogVideo':('Powerlog', '**/CurrentPowerlog.PLSQL'),
    'powerlogTimezone':('Powerlog', '**/CurrentPowerlog.PLSQL'),
    'powerlogAggnotifications':('Powerlog', '**/CurrentPowerlog.PLSQL'),
    'powerlogAggbulletins':('Powerlog', '**/CurrentPowerlog.PLSQL'),
    'powerlogPushreceived':('Powerlog', '**/CurrentPowerlog.PLSQL'),
    'powerlogProcessdatausage':('Powerlog', '**/CurrentPowerlog.PLSQL'),
    'powerlogPaireddevconf':('Powerlog', '**/CurrentPowerlog.PLSQL'),
    'powerlogLocuseapp':('Powerlog', '**/CurrentPowerlog.PLSQL'),
    'powerlogAirdrop':('Powerlog', '**/CurrentPowerlog.PLSQL'),
    'powerlogAudio':('Powerlog', '**/CurrentPowerlog.PLSQL'),
    'powerlogDeletedapps':('Powerlog', '**/CurrentPowerlog.PLSQL'),
    'powerlogAppinfo':('Powerlog', '**/CurrentPowerlog.PLSQL'),
    'powerlogBackupinfo':('Powerlog', '**/CurrentPowerlog.PLSQL'),
    'powerlogLightplug':('Powerlog', '**/CurrentPowerlog.PLSQL'),
    'healthDistance':('Health Data', '**/healthdb_secure.sqlite'),
    'healthEcg':('Health Data', '**/healthdb_secure.sqlite'),
    'healthFlights':('Health Data', '**/healthdb_secure.sqlite'),
    'healthHr':('Health Data', '**/healthdb_secure.sqlite'),
    'healthStandup':('Health Data', '**/healthdb_secure.sqlite'),
    'healthWeight':('Health Data', '**/healthdb_secure.sqlite'),
    'healthCadence':('Health Data', '**/healthdb_secure.sqlite'),
    'healthElevation':('Health Data', '**/healthdb_secure.sqlite'),
    'healthWorkoutGen':('Health Data', '**/healthdb_secure.sqlite'),
    'dataArk':('IOS Build', '**/Library/Lockdown/data_ark.plist'),
    'applicationstate':('Installed Apps', '**/applicationState.db'),
    'accs':('Accounts', '**/Accounts3.sqlite'),
    'confaccts':('Accounts', '**/com.apple.accounts.exists.plist'),
    'callHistory':('Call logs', '**/CallHistory.storedata'),
    'conDev':('Connected to', '**/iTunes_Control/iTunes/iTunesPrefs'),
    'coreDuetAirplane':('CoreDuet', '*/coreduetd.db'),
    'coreDuetLock':('CoreDuet', '*/coreduetd.db'),
    'coreDuetPlugin':('CoreDuet', '*/coreduetd.db'),
    'safariHistory':('Safari Browser', '*/History.db'),
    'safariWebsearch':('Safari Browser', '**/Safari/History.db'),
    'queryPredictions':('SMS & iMessage', '**/query_predictions.db'),
    'dhcpl':('DHCP', '**private/var/db/dhcpclient/leases/en*'),
    'dhcphp':('DHCP', '**private/var/db/dhcpd_leases*'),
    'dataUsageA':('Data Usage', '**/DataUsage.sqlite'), 
    'dataUsageB':('Data Usage', '**/DataUsage-watch.sqlite'),
    'dataUsageProcessA':('Data Usage', '**/DataUsage-watch.sqlite'),
    'dataUsageProcessB':('Data Usage', '**/DataUsage.sqlite'),
    'mobileInstall':('Mobile Installation Logs', '**/mobile_installation.log.*'), 
    'sms':('SMS & iMessage', '**/sms.db'),
    'iconsScreen':('iOS Screens', '**/SpringBoard/IconState.plist'),
    'webClips':('iOS Screens', '*WebClips/*.webclip/*'),
    'notificationsXI':('Notifications', '*PushStore*'),
    'notificationsXII':('Notifications', '*private/var/mobile/Library/UserNotifications*'),
    'celWireless':('Cellular Wireless', '*wireless/Library/Preferences/com.apple.*'),
    'mailprotect':('iOS Mail', '**private/var/mobile/Library/Mail/* Index*'),
    'locationDparkedhistorical':('RoutineD', '**/Local.sqlite'),
    'locationDparked':('RoutineD', '**/Local.sqlite'),
    'screentimeGenerichour':('Screentime', '**/RMAdminStore-Local.sqlite'),
    'screentimeTimeditems':('Screentime', '**/RMAdminStore-Local.sqlite'),
    'screentimeCounteditems':('Screentime', '**/RMAdminStore-Local.sqlite'),
    'bluetoothPaired':('Bluetooth', '**/Library/Database/com.apple.MobileBluetooth.ledevices.paired.db'),
    'bluetoothOther':('Bluetooth', '**/Library/Database/com.apple.MobileBluetooth.ledevices.other.db'),
    'locationDcellloc':('LocationD', '**/cache_encryptedB.db'),
    'locationDappharvest':('LocationD', '**/cache_encryptedB.db'),
    'locationDwifilocB':('LocationD', '**/cache_encryptedB.db'),
    'locationDlteloc':('LocationD', '**/cache_encryptedB.db'),
    'locationDsteps':('LocationD', '**/cache_encryptedC.db'),
    'locationDcdmaloc1':('LocationD', '**/cache_encryptedB.db'),
    'calendarAll':('Calendar', '**/Calendar.sqlitedb'),
    'photosMetadata':('Photos', '**/Photos.sqlite')
    }
    
#    Artifacts take long to run. Useful in specific situations only.
#    'aggDict':('Aggregate Dictionary', '*/AggregateDictionary/ADDataStore.sqlitedb')
#    'aggDictScalars':('Aggregate Dictionary', '*/AggregateDictionary/ADDataStore.sqlitedb')
#    'journalStrings':('SQLite Journaling', '**/*-journal')
#    'walStrings':('SQLite Journaling - Strings', '**/*-wal')
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
    
    logfunc('{} artifact executing'.format(artifact_name))
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

    logfunc('{} artifact completed'.format(artifact_name))
