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
from scripts.artifacts.dataUsage import get_dataUsage
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

from scripts.ilapfuncs import *

# GREP searches for each module
# Format is Key='modulename', Value=Tuple('Module Pretty Name', 'regex term')
# Here modulename must match the get_xxxxxx function name for that module. 
# For example: If modulename='profit', function name must be get_profit(..)
# Don't forget to import the module above!!!!

'''
tosearch = {'lastBuild':('IOS Build', '*LastBuildInfo.plist'),
            'dataArk':('IOS Build', '**/Library/Lockdown/data_ark.plist'),
            'applicationstate':('Installed Apps', '**/applicationState.db'),
            'accs':('Accounts', '**/Accounts3.sqlite'),
            'confaccts':('Accounts', '**/com.apple.accounts.exists.plist'),
            'callHistory':('Call logs', '**/CallHistory.storedata'),
            'conDev':('Connected to', '**/iTunes_Control/iTunes/iTunesPrefs'),
            'dataUsage':('Network data', '**/DataUsage.sqlite'),
            'mobileInstall':('Mobile Installation Logs', '**/mobile_installation.log.*'), 
            'journalStrings':('SQLite Journaling', '**/*-journal'),
            'sms':('SMS & iMessage', '**/sms.db'),
            'iconsScreen':('iOS Screens', '**/SpringBoard/IconState.plist'),
            'webClips':('iOS Screens', '*WebClips/*.webclip/*'),
            'notificationsXII':('Notifications', '*private/var/mobile/Library/UserNotifications*'),
            'celWireless':('Cellular Wireless', '*wireless/Library/Preferences/com.apple.*')
            }

# 'notificationsXI':('Notifications', '*PushStore*') //Need test iOS 11 image with notifications
'''
tosearch = {'lastBuild':('IOS Build', '*LastBuildInfo.plist'),
            'knowCincept':('KnowledgeC', '*/CoreDuet/Knowledge/knowledgeC.db'),
            }


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
