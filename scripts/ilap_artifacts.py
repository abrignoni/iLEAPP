# To add a new artifact module, import it here as shown below:
#     from scripts.artifacts.fruitninja import get_fruitninja
# Also add the grep search for that module using the same name
# to the 'tosearch' data structure.

import traceback

from time import process_time, gmtime, strftime
from scripts.artifacts.accs import get_accs
from scripts.artifacts.addressBook import get_addressBook
from scripts.artifacts.alarms import get_alarms
from scripts.artifacts.AllTrails import get_AllTrails
from scripts.artifacts.appConduit import get_appConduit
from scripts.artifacts.appGrouplisting import get_appGrouplisting
from scripts.artifacts.appItunesmeta import get_appItunesmeta
from scripts.artifacts.appSnapshots import get_applicationSnapshots
from scripts.artifacts.appleMapsApplication import get_appleMapsApplication
from scripts.artifacts.appleMapsGroup import get_appleMapsGroup
from scripts.artifacts.appleMapsSearchHistory import get_appleMapsSearchHistory
from scripts.artifacts.applePodcasts import get_applePodcasts
from scripts.artifacts.appleWifiPlist import get_appleWifiPlist
from scripts.artifacts.appleWalletCards import get_appleWalletCards
from scripts.artifacts.appleWalletPasses import get_appleWalletPasses
from scripts.artifacts.appleWalletTransactions import get_appleWalletTransactions
from scripts.artifacts.applicationstate import get_applicationstate
from scripts.artifacts.airtags import get_airtags
from scripts.artifacts.bluetooth import get_bluetooth
from scripts.artifacts.bumble import get_bumble
from scripts.artifacts.cacheRoutesGmap import get_cacheRoutesGmap
from scripts.artifacts.calendar import get_calendar
from scripts.artifacts.callHistory import get_callHistory
from scripts.artifacts.cashApp import get_cashApp
from scripts.artifacts.celWireless import get_celWireless
from scripts.artifacts.cloudkitSharing import get_cloudkitSharing
from scripts.artifacts.conDev import get_conDev
from scripts.artifacts.confaccts import get_confaccts
from scripts.artifacts.ControlCenter import get_ControlCenter
from scripts.artifacts.deviceActivator import get_deviceActivator
from scripts.artifacts.dhcphp import get_dhcphp
from scripts.artifacts.dhcpl import get_dhcpl
from scripts.artifacts.discordAcct import get_discordAcct
from scripts.artifacts.discordJson import get_discordJson
from scripts.artifacts.discordManifest import get_discordManifest
from scripts.artifacts.FacebookMessenger import get_FacebookMessenger
from scripts.artifacts.filesAppsclient import get_filesAppsclient
from scripts.artifacts.filesAppsdb import get_filesAppsdb
from scripts.artifacts.filesAppsm import get_filesAppsm
from scripts.artifacts.geodApplications import get_geodApplications
from scripts.artifacts.geodMapTiles import get_geodMapTiles
from scripts.artifacts.geodPDPlaceCache import get_geodPDPlaceCache
from scripts.artifacts.Gmail import get_Gmail
from scripts.artifacts.googleDuo import get_googleDuo
from scripts.artifacts.icloudMeta import get_icloudMeta
from scripts.artifacts.icloudPhotoMeta import get_icloudPhotoMeta
from scripts.artifacts.quickLook import get_quickLook
from scripts.artifacts.iCloudWifi import get_iCloudWifi
from scripts.artifacts.icloudSharedalbums import get_icloudSharedalbums
from scripts.artifacts.iconsScreen import get_iconsScreen
from scripts.artifacts.imoHD_Chat import get_imoHD_Chat
from scripts.artifacts.instagramThreads import get_instagramThreads
from scripts.artifacts.interactionCcontacts import get_interactionCcontacts
from scripts.artifacts.keyboardAppUsage import get_keyboardAppUsage
from scripts.artifacts.keyboardLexicon import get_keyboardLexicon
from scripts.artifacts.kijijiConversations import get_kijijiConversations
from scripts.artifacts.kikGroupadmins import get_kikGroupadmins
from scripts.artifacts.kikLocaladmin import get_kikLocaladmin
from scripts.artifacts.kikMessages import get_kikMessages
from scripts.artifacts.kikBplistmeta import get_kikBplistmeta
from scripts.artifacts.kikPendingUploads import get_kikPendingUploads
from scripts.artifacts.kikUsersgroups import get_kikUsersgroups
from scripts.artifacts.locServicesconfig import get_locServicesconfig
#from scripts.artifacts.lastBuild import get_lastBuild, get_iTunesBackupInfo
from scripts.artifacts.mapsSync import get_mapsSync
from scripts.artifacts.mailprotect import get_mailprotect
from scripts.artifacts.mediaLibrary import get_mediaLibrary
from scripts.artifacts.medicalID import get_medicalID
from scripts.artifacts.mobileActivationLogs import get_mobileActivationLogs
from scripts.artifacts.mobileBackup import get_mobileBackup
from scripts.artifacts.mobileContainerManager import get_mobileContainerManager
from scripts.artifacts.mobileInstall import get_mobileInstall
from scripts.artifacts.notes import get_notes
from scripts.artifacts.notificationsDuet import get_notificationsDuet
from scripts.artifacts.notificationsXI import get_notificationsXI
from scripts.artifacts.notificationsXII import get_notificationsXII
from scripts.artifacts.ooklaSpeedtestData import get_ooklaSpeedtestData
from scripts.artifacts.photosMetadata import get_photosMetadata
from scripts.artifacts.protonMail import get_protonMail
from scripts.artifacts.recentApphistory import get_recentApphistory
from scripts.artifacts.reminders import get_reminders
from scripts.artifacts.restoreLog import get_restoreLog
from scripts.artifacts.queryPredictions import get_queryPredictions
from scripts.artifacts.safariBookmarks import get_safariBookmarks
from scripts.artifacts.safariFavicons import get_safariFavicons
from scripts.artifacts.safariRecentWebSearches import get_safariRecentWebSearches
from scripts.artifacts.safariTabs import get_safariTabs
from scripts.artifacts.safariWebsearch import get_safariWebsearch
from scripts.artifacts.slack import get_slack
from scripts.artifacts.tcc import get_tcc
from scripts.artifacts.teams import get_teams
from scripts.artifacts.teamsSegment import get_teamsSegment 
from scripts.artifacts.textinputTyping import get_textinputTyping
from scripts.artifacts.tikTok import get_tikTok
from scripts.artifacts.tileApp import get_tileApp
from scripts.artifacts.tileAppDb import get_tileAppDb
from scripts.artifacts.tileAppDisc import get_tileAppDisc
from scripts.artifacts.tileAppNetDb import get_tileAppNetDb
from scripts.artifacts.walStrings import get_walStrings
from scripts.artifacts.webClips import get_webClips
from scripts.artifacts.weatherAppLocations import get_weatherAppLocations
from scripts.artifacts.whatsappContacts import get_whatsappContacts
from scripts.artifacts.whatsappMessages import get_whatsappMessages
from scripts.artifacts.vipps import get_vipps
from scripts.artifacts.vippsContacts import get_vippsContacts
from scripts.artifacts.venmo import get_venmo
from scripts.artifacts.viber import get_viber
from scripts.artifacts.voicemail import get_voicemail
from scripts.artifacts.voiceTriggers import get_voiceTriggers
from scripts.artifacts.voiceRecordings import get_voiceRecordings

from scripts.ilapfuncs import *

# GREP searches for each module
# Format is Key='modulename', Value=Tuple('Module Pretty Name', 'regex term')
#   regex_term can be a string or a list/tuple of strings
# Here modulename must match the get_xxxxxx function name for that module. 
# For example: If modulename='profit', function name must be get_profit(..)
# Don't forget to import the module above!!!!


tosearch = {
            
            'icloudSharedalbums': ('iCloud Shared Albums', '*/private/var/mobile/Media/PhotoData/PhotoCloudSharingData/*'),
            'iCloudWifi': ('Wifi Connections', '**/com.apple.wifid.plist'),
            'iconsScreen': ('iOS Screens', '**/SpringBoard/IconState.plist'),
            'imoHD_Chat': ('IMO HD Chat', ('**/IMODb2.sqlite*','private/var/mobile/Containers/Data/Application/*/Library/Caches/videos/*.webp')),
            'instagramThreads':('Instagram', '*/mobile/Containers/Data/Application/*/Library/Application Support/DirectSQLiteDatabase/*.db*'),
            'interactionCcontacts': ('InteractionC', '**/interactionC.db*'),
            'keyboardAppUsage': ('Keyboard', '*/private/var/mobile/Library/Keyboard/app_usage_database.plist'),
            'keyboardLexicon': ('Keyboard', '*/private/var/mobile/Library/Keyboard/*-dynamic.lm/dynamic-lexicon.dat'),
            'kijijiConversations':('Kijiji Conversations', ('*/Library/Caches/conversation_cache')),
            'kikMessages': ('Kik', ('**/kik.sqlite*','*/mobile/Containers/Shared/AppGroup/*/cores/private/*/content_manager/data_cache/*')),
            'kikBplistmeta': ('Kik', '*/mobile/Containers/Shared/AppGroup/*/cores/private/*/attachments/*'),
            'kikGroupadmins': ('Kik', ('*/kik.sqlite*')),
            'kikLocaladmin': ('Kik', ('*/kik.sqlite*')),
            'kikPendingUploads': ('Kik', ('*/mobile/Containers/Shared/AppGroup/*/cores/private/*/chunked_upload_storage/pending_uploads','*/mobile/Containers/Shared/AppGroup/*/cores/private/*/chunked_upload_storage/data_cache/*')),
            'kikUsersgroups':('Kik', ('*/kik.sqlite*')),            
            'locServicesconfig': ('Location Services Configurations', ('*/Library/Preferences/com.apple.locationd.plist','*/Library/Caches/locationd/clients.plist', '*/Library/Preferences/com.apple.routined.plist')),
            'mapsSync': ('Geolocation', '*/MapsSync_0.0.1*'),
            'mailprotect': ('iOS Mail', '**/private/var/mobile/Library/Mail/* Index*'),
            'mediaLibrary': ('Media Library', '**/Medialibrary.sqlitedb'),
            'medicalID': ('Medical ID', '*/private/var/mobile/Library/MedicalID/MedicalIDData.archive'),
            'mobileActivationLogs': ('Mobile Activation Logs', '**/mobileactivationd.log*'),
            'mobileBackup': ('Mobile Backup', '*/Preferences/com.apple.MobileBackup.plist'),
            'mobileContainerManager': ('Mobile Container Manager', '**/containermanagerd.log.*'),
            'mobileInstall': ('Mobile Installation Logs', '**/mobile_installation.log.*'),
            'notes': ('Notes', '*/NoteStore.sqlite*'),
            'notificationsDuet': ('Notifications', '*/DuetExpertCenter/streams/userNotificationEvents/local/*'),
            'notificationsXI': ('Notifications', '*PushStore*'),
            'notificationsXII': ('Notifications', '*private/var/mobile/Library/UserNotifications*'),
            'ooklaSpeedtestData': ('Applications', '**/speedtest.sqlite*'),
            'photosMetadata': ('Photos', '**/Photos.sqlite*'),
            'protonMail': ('Proton Mail', ('*/group.ch.protonmail.protonmail.plist','*/ProtonMail.sqlite*','*/Containers/Data/Application/*/tmp/*')),
            'queryPredictions': ('SMS & iMessage', '**/query_predictions.db'),
            'quickLook': ('iCloud Quick Look', '*/Quick Look/cloudthumbnails.db*'),
            'recentApphistory':('CarPlay', '*/com.apple.CarPlayApp.plist'),
            'restoreLog':('Mobile Software Update', '**/private/var/mobile/MobileSoftwareUpdate/restore.log'),
            'reminders': ('Reminders', '**/Reminders/Container_v1/Stores/*.sqlite*'),
            'safariBookmarks': ('Safari Browser', '**/Safari/Bookmarks.db*'),
            'safariRecentWebSearches': ('Safari Browser', '**/Library/Preferences/com.apple.mobilesafari.plist'),
            'safariTabs': ('Safari Browser', '**/Safari/BrowserState.db*'),
            'safariWebsearch': ('Safari Browser', '**/Safari/History.db*'),
            'safariFavicons': ('Safari Browser', '*/Containers/Data/Application/*/Library/Image Cache/Favicons/Favicons.db*'),
            'slack': ('Slack', '*/var/mobile/Containers/Data/Application/*/Library/Application Support/Slack/*/Database/main_db*'),
            'tcc': ('App Permissions', '*TCC.db*'),
            'teams': ('Microsoft Teams', ('*/var/mobile/Containers/Shared/AppGroup/*/SkypeSpacesDogfood/*/Skype*.sqlite*','*/var/mobile/Containers/Shared/AppGroup/*/SkypeSpacesDogfood/Downloads/*/Images/*')),
            'textinputTyping': ('Text Input Messages', '*/DES/Records/com.apple.TextInput.TypingDESPlugin/*.desdata'),
            'teamsSegment': ('Microsoft Teams - Logs', '*/var/mobile/Containers/Data/Application/*/Library/DriveIQ/segments/current/*.*'),
            'tikTok': ('TikTok', ('*/Application/*/Library/Application Support/ChatFiles/*/db.sqlite*', '*AwemeIM.db*')),
            'tileApp': ('Locations', '*private/var/mobile/Containers/Data/Application/*/Library/log/com.thetileapp.tile*'),
            'tileAppDb': ('Locations', '*private/var/mobile/Containers/Shared/AppGroup/*/com.thetileapp.tile-TileNetworkDB.sqlite*'),
            'tileAppDisc': ('Accounts','*/private/var/mobile/Containers/Shared/AppGroup/*/com.thetileapp.tile-DiscoveredTileDB.sqlite*'),
            'tileAppNetDb': ('Accounts', '*/private/var/mobile/Containers/Shared/AppGroup/*/com.thetileapp.tile-TileNetworkDB.sqlite*'),
            'voiceRecordings': ('Voice-Recordings', ('**/Recordings/*.composition/manifest.plist', '**/Recordings/*.m4a')),
            'voiceTriggers': ('Voice-Triggers', ('**/td/audio/*.json', '**/td/audio/*.wav')),
            'walStrings': ('SQLite Journaling', ('**/*-wal', '**/*-journal')),
            'whatsappMessages': ('Whatsapp', ('*/var/mobile/Containers/Shared/AppGroup/*/ChatStorage.sqlite*','*/var/mobile/Containers/Shared/AppGroup/*/Message/Media/*/*/*/*.*')),
            'whatsappContacts': ('Whatsapp', ('*/var/mobile/Containers/Shared/AppGroup/*/ContactsV2.sqlite*')),
            'weatherAppLocations': ('Locations', '*/private/var/mobile/Containers/Shared/AppGroup/*/Library/Preferences/group.com.apple.weather.plist'),
            'webClips': ('iOS Screens', '*WebClips/*.webclip/*'),
            'vipps':('Vipps', ('*/Vipps.sqlite*')),
            'vippsContacts':('Vipps', ('*/Vipps.sqlite*')),
            'venmo':('Venmo', ('*PrivateFeed', '*PublicFeed', '*FriendsFeed')),
            'voicemail': ('Voicemail', ('**/Voicemail/voicemail.db','**/Voicemail/*.amr')),
            'viber' : ('Viber', ('**/com.viber/settings/Settings.data','**/com.viber/database/Contacts.data','**/Containers/Data/Application/*/Documents/Attachments/*.*','**/com.viber/ViberIcons/*.*')),
            # 'appUpdates':('App Updates', '**/AppUpdates.sqlitedb'),
            # 'systemVersion':('Device Info', '**/SystemVersion.plist'),
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
        method(files_found, report_folder, seeker, wrap_text)
    except Exception as ex:
        logfunc('Reading {} artifact had errors!'.format(artifact_name))
        logfunc('Error was {}'.format(str(ex)))
        logfunc('Exception Traceback: {}'.format(traceback.format_exc()))
        return

    end_time = process_time()
    run_time_secs = end_time - start_time
    # run_time_HMS = strftime('%H:%M:%S', gmtime(run_time_secs))
    logfunc('{} [{}] artifact completed in time {} seconds'.format(artifact_name, artifact_func, run_time_secs))