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
from scripts.artifacts.interactionCcontacts import get_interactionCcontacts
from scripts.artifacts.knowCnotes import get_knowCnotes
from scripts.artifacts.knowCactivitylvl import get_knowCactivitylvl
from scripts.artifacts.knowCappact import get_knowCappact
from scripts.artifacts.knowCappactcal import get_knowCappactcal
from scripts.artifacts.knowCappactsafari import get_knowCappactsafari
from scripts.artifacts.knowCinstall import get_knowCinstall
from scripts.artifacts.safariHistory import get_safariHistory
from scripts.artifacts.safariWebsearch import get_safariWebsearch

from scripts.ilapfuncs import *

# GREP searches for each module
# Format is Key='modulename', Value=Tuple('Module Pretty Name', 'regex term')
# Here modulename must match the get_xxxxxx function name for that module. 
# For example: If modulename='profit', function name must be get_profit(..)
# Don't forget to import the module above!!!!


tosearch = {'lastBuild':('IOS Build', '*LastBuildInfo.plist'),
            'dataArk':('IOS Build', '**/Library/Lockdown/data_ark.plist'),
            'applicationstate':('Installed Apps', '**/applicationState.db'),
            'accs':('Accounts', '**/Accounts3.sqlite'),
            'confaccts':('Accounts', '**/com.apple.accounts.exists.plist'),
            'callHistory':('Call logs', '**/CallHistory.storedata'),
            'conDev':('Connected to', '**/iTunes_Control/iTunes/iTunesPrefs'),
            'dataUsageA':('Data Usage', '**/DataUsage.sqlite'), 
            'dataUsageB':('Data Usage', '**/DataUsage-watch.sqlite'),
            'dataUsageProcessA':('Data Usage', '**/DataUsage-watch.sqlite'),
            'dataUsageProcessB':('Data Usage', '**/DataUsage.sqlite'),
            'mobileInstall':('Mobile Installation Logs', '**/mobile_installation.log.*'), 
            'journalStrings':('SQLite Journaling', '**/*-journal'),
            'sms':('SMS & iMessage', '**/sms.db'),
            'iconsScreen':('iOS Screens', '**/SpringBoard/IconState.plist'),
            'webClips':('iOS Screens', '*WebClips/*.webclip/*'),
            'notificationsXI':('Notifications', '*PushStore*'),
            'notificationsXII':('Notifications', '*private/var/mobile/Library/UserNotifications*'),
            'celWireless':('Cellular Wireless', '*wireless/Library/Preferences/com.apple.*'),
            'knowCincept':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
            'knowCusage':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
            'knowCact':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
            'knowCinfocus':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
            'knowCbatlvl':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
            'knowCappsinstal':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
            'knowClocked':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
            'knowCplugged':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
            'knowCsiri':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
            'knowCnotes':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
            'knowCactivitylvl':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
            'knowCappact':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
            'knowCappactcal':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
            'knowCappactsafari':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
            'knowCinstall':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
            'aggDict':('Aggregate Dictionary', '*/AggregateDictionary/ADDataStore.sqlitedb'),
            'aggDictScalars':('Aggregate Dictionary', '*/AggregateDictionary/ADDataStore.sqlitedb'),
            'coreDuetAirplane':('CoreDuet', '*/coreduetd.db'),
            'coreDuetLock':('CoreDuet', '*/coreduetd.db'),
            'coreDuetPlugin':('CoreDuet', '*/coreduetd.db'),
            'healthDistance':('Health Data', '**/healthdb_secure.sqlite'),
            'healthEcg':('Health Data', '**/healthdb_secure.sqlite'),
            'healthFlights':('Health Data', '**/healthdb_secure.sqlite'),
            'healthHr':('Health Data', '**/healthdb_secure.sqlite'),
            'healthStandup':('Health Data', '**/healthdb_secure.sqlite'),
            'healthWeight':('Health Data', '**/healthdb_secure.sqlite'),
            'healthCadence':('Health Data', '**/healthdb_secure.sqlite'),
            'healthElevation':('Health Data', '**/healthdb_secure.sqlite'),
            'healthWorkoutGen':('Health Data', '**/healthdb_secure.sqlite'),
            'safariHistory':('Safari Browser', '*/History.db'),
            'safariWebsearch':('Safari Browser', '**/Safari/History.db')
            
            
            }


#'lastBuild':('IOS Build', '*LastBuildInfo.plist'),
'''
tosearch = {'safariHistory':('Safari Browser', '*/History.db'),
            'safariWebsearch':('Safari Browser', '**/Safari/History.db')
            }
'''

#'walStrings':('SQLite Journaling - Strings', '**/*-wal') takes a long time to run... Maybe a check mark to make it run?


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
