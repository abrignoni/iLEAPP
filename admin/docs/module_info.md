# iLEAPP Artifacts

<!-- MODULE_INFO_START -->

## Summary

Total number of modules: 260  
Number of v1 artifacts: 164  
Number of v2 artifacts: 44  
Number of modules with errors or no recognized artifacts: 3  

## V2 Artifacts Table

| Module | Artifact | Name | Output Types | Description | Paths |
|--------|----------|------|--------------|-------------|-------|
| [ATXDatastore.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/ATXDatastore.py) | ATXDatastore | iOS ATXDatastore | all | Parses ATXDataStore and matches actions with Frequent locations, when available. | ``**DuetExpertCenter/_ATXDataStore.db*``, ``**routined/Local.sqlite*`` |
| [ControlCenter.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/ControlCenter.py) | controlcenter | Control Center Configuration |  | Parses controls/apps added to the Control Center | ``*/mobile/Library/ControlCenter/ModuleConfiguration.plist`` |
| [DataUsage.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/DataUsage.py) | datausage | Data Usage |  | Parses application network data usage | ``*/wireless/Library/Databases/DataUsage.sqlite*`` |
| [Gmail.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/Gmail.py) | gmail_offline_search | Gmail - Offline Search | all | Parses Gmail offline search content | ``*/mobile/Containers/Data/Application/*/Library/Application Support/data/*/searchsqlitedb*`` |
| [Gmail.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/Gmail.py) | gmail_label_details | Gmail - Label Details | all | Parses Gmail label details | ``*/mobile/Containers/Data/Application/*/Library/Application Support/data/*/sqlitedb*`` |
| [Splitwise.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/Splitwise.py) | splitwise | Splitwise |  | Parses users, accounts, and transaction information from Splitwise app | ``*/Library/Application Support/database.sqlite*`` |
| [WatchSleepData.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/WatchSleepData.py) | HealthSleepData | Apple Health Sleep Data |  | Parses Apple Health Sleep Data from the healthdb_secure.sqlite database | ``*Health/healthdb_secure.sqlite*`` |
| [WatchWornData.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/WatchWornData.py) | WatchWornData | Apple Watch Worn Data |  | Parses Apple Watch Worn Data from the healthdb_secure.sqlite database | ``*Health/healthdb_secure.sqlite*`` |
| [accs.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/accs.py) | accs | Account Data | all | Extract information about configured user accounts | ``*/mobile/Library/Accounts/Accounts3.sqlite*`` |
| [adId.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/adId.py) | adId |  |  |  | ``*/containers/Shared/SystemGroup/*/Library/Caches/com.apple.lsdidentifiers.plist`` |
| [addressBook.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/addressBook.py) | addressbook | Address Book |  | Extract information from the native contacts application | ``*/mobile/Library/AddressBook/AddressBook*.sqlitedb*`` |
| [applicationstate.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/applicationstate.py) | applicationstate | Application State |  | Extract information about bundle container path and data path for Applications | ``*/mobile/Library/FrontBoard/applicationState.db*`` |
| [blockedContacts.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/blockedContacts.py) | blockedContacts | Blocked Contacts |  |  | ``*/mobile/Library/Preferences/com.apple.cmfsyncagent.plist`` |
| [booking.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/booking.py) | booking | Booking.com |  | account, payment methods, wish lists, viewed, recently searched, recently booked, booked, stored destinations, notifications and flights searched | ``*/mobile/Containers/Data/Application/*/Library/Preferences/com.booking.BookingApp.plist`` |
| [burner.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/burner.py) | burnerPhoenix | Burner |  | Parses and extract accounts, contacts, burner numbers and messages | ``*/mobile/Containers/Shared/AppGroup/*/Phoenix.sqlite*``, ``*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist`` |
| [burnerCache.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/burnerCache.py) | burnerCache | Burner Cache |  | Parses and extract accounts, contacts, burner numbers and messages | ``*/Library/Caches/com.adhoclabs.burner/Cache.db*``, ``*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist`` |
| [cachev0.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/cachev0.py) | cachev0 | Image cacheV0 |  | Images cached in the SQLite database. | ``*/cacheV0.db*`` |
| [calendarAll.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/calendarAll.py) | calendar | Calendar |  | List of calendars, calendar events and bithdays | ``**/Calendar.sqlitedb`` |
| [callHistory.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/callHistory.py) | callhistory | Call History |  | Parses and extract Call History | ``**/CallHistory.storedata*``, ``**/call_history.db`` |
| [chatgpt.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/chatgpt.py) | chatgpt | ChatGPT |  | Get user's ChatGPT conversations, settings and media files. This parser is based on a research project. Parser is validated up to the app's 1.2024.178 | ``**/Containers/Data/Application/*/Library/Application Support/conversations-*/*.*``, ``**/Containers/Data/Application/*/Library/Application Support/drafts-*/*.*``, ``**/Containers/Data/Application/*/Library/Preferences/com.openai.chat.StatsigService.plist``, ``**/Containers/Data/Application/*/Library/Preferences/com.segment.storage.oai.plist``, ``**/Containers/Data/Application/*/Library/Preferences/com.openai.chat.plist``, ``**/Containers/Data/Application/*/tmp/recordings/*.*``, ``**/Containers/Data/Application/*/tmp/photo-*.*``, ``**/Containers/Data/Application/*/tmp/*/*.*`` |
| [cloudkitSharing.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/cloudkitSharing.py) | cloudkitsharing | Cloudkit Sharing |  | This module processes data related to CloudKit sharing, encompassing information on notes shared via CloudKit and the accounts participating in CloudK | ``*NoteStore.sqlite*`` |
| [dmss.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/dmss.py) | Dahua Technology (DMSS) | Dahua Technology (DMSS) |  | Extract data from Dahua Technology (DMSS) Application | ``*/Library/Support/Devices.sqlite3*``, ``*/Library/Support/configFile1``, ``*/Library/Support/*/DMSSCloud.sqlite*``, ``*/Documents/Captures/*``, ``*/Documents/Videos/*`` |
| [filesApps.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/filesApps.py) | filesapp | Files App |  | Items stored in iCloud Drive. | ``*/mobile/Library/Application Support/CloudDocs/session/db/client.db*``, ``*/mobile/Library/Application Support/CloudDocs/session/db/server.db*`` |
| [googleTranslate.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/googleTranslate.py) | googleTranslate | Google Translate |  | History, Favorite translations and Text-To-Speech | ``*/mobile/Containers/Data/Application/*/Documents/translate.db*`` |
| [iTunesBackupInfo.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/iTunesBackupInfo.py) | iTunesBackupInfo | iTunes Backup Information |  | Extract information from the Info.plist file of an iTunes backup | ``*Info.plist``, ``*info.plist`` |
| [knowledgeC.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/knowledgeC.py) | knowledgeC | knowledgeC |  | Extract Pattern of Life from knowledgeC database | ``*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*`` |
| [lastBuild.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/lastBuild.py) | lastbuild | iOS Information |  | Extract iOS information from the LastBuildInfo.plist file | ``*LastBuildInfo.plist`` |
| [life360.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/life360.py) | Life360 | Life360 |  | Parses Life360 app logs, chat messages, and more | ``*/com.life360.safetymap *.log``, ``*/Library/Application Support/Messaging.sqlite*`` |
| [line.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/line.py) | line | Line Artifacts |  | Get Line | ``**/Line.sqlite*`` |
| [mediaLibrary.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/mediaLibrary.py) | mediaLibrary | Media Library |  |  | ``**/Medialibrary.sqlitedb*`` |
| [serialNumber.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/serialNumber.py) | serialNumber | Serial Number |  | Serial Number | ``*/Library/Caches/locationd/consolidated.db*`` |
| [sysShutdown.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/sysShutdown.py) | sysShutdown | Sysdiagnose - Shutdown Log |  | Parses the shutdown.log file from Sysdiagnose logs, based off work by Kaspersky Lab https://github.com/KasperskyLab/iShutdown | ``*/shutdown.log`` |
| [tcc.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/tcc.py) | tcc | Application Permissions |  | Extract application permissions from TCC.db database | ``*/mobile/Library/TCC/TCC.db*`` |
| [telegramMesssages.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/telegramMesssages.py) | TelegramMessages | Telegram Messages |  |  | ``*/telegram-data/account-*/postbox/db/db_sqlite*``, ``*/telegram-data/account-*/postbox/media/**`` |
| [uberClient.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/uberClient.py) | uberClient | Uber |  | account, payment profiles, nearby vehicles, user address location, searched rides, cached locations, sqlite locations data, locations | ``*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist`` |
| [uberLeveldb.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/uberLeveldb.py) | uberLocations | Uber |  | Uber locations inside LevelDB | ``*/Data/Application/*/Library/Application Support/com.ubercab.UberClient/storagev2/*`` |
| [uberPlaces.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/uberPlaces.py) | uberPlaces | Uber - Places |  | Parses Uber Places Database | ``*/private/var/mobile/Containers/Data/Application/*/Documents/database.db*`` |
| [viber.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/viber.py) | viber | Viber Artifacts |  | Get Viber settings, contacts, recent calls and messages information. This script queries Settings.data and Contacts.data Viber dbs and creates a repor | ``**/com.viber/settings/Settings.data*``, ``**/com.viber/database/Contacts.data*``, ``**/Containers/Data/Application/*/Documents/Attachments/*.*``, ``**/com.viber/ViberIcons/*.*`` |
| [voicemail.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/voicemail.py) | voicemail | Voicemail |  | Parses and extract Voicemail | ``**/Voicemail/voicemail.db*``, ``**/Voicemail/*.amr`` |
| [waze.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/waze.py) | waze | Waze |  | Get account, session, searched locations, recent locations, favorite locations, share locations, text-to-speech navigation and track GPS quality. | ``*/mobile/Containers/Data/Application/*/Documents/user.db*``, ``*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist`` |
| [whatsappCallHistory.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/whatsappCallHistory.py) | whatsappCallHistory | WhatsappCallHistory |  |  | ``*/var/mobile/Containers/Shared/AppGroup/*/CallHistory.sqlite*``, ``*/var/mobile/Containers/Shared/AppGroup/*/ContactsV2.sqlite*`` |
| [whatsappContacts.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/whatsappContacts.py) | whatsappContacts | Whatsapp Contacts |  |  | ``*/var/mobile/Containers/Shared/AppGroup/*/ContactsV2.sqlite*`` |
| [whatsappMessages.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/whatsappMessages.py) | whatsappMessages | Whatsapp Messages |  |  | ``*/var/mobile/Containers/Shared/AppGroup/*/ChatStorage.sqlite*``, ``*/var/mobile/Containers/Shared/AppGroup/*/Message/Media/*/*/*/*.*`` |
| [wire.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/wire.py) | wire | Wire Artifacts |  | Get Wire | ``**/store.wiredatabase*`` |

## V1 Artifacts Table

| Module | Artifacts |
|--------|----------|
| [AWESearch.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/AWESearch.py) | AWESearch |
| [AllTrails.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/AllTrails.py) | alltrails |
| [AshHistory.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/AshHistory.py) |  |
| [FacebookMessenger.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/FacebookMessenger.py) | facebookmessenger |
| [FitnessWorkoutsLocationData.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/FitnessWorkoutsLocationData.py) | Fitness |
| [Health.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/Health.py) | health |
| [SMSmissingROWIDs.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/SMSmissingROWIDs.py) |  |
| [SiriRemembers.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/SiriRemembers.py) |  |
| [airdropId.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/airdropId.py) | airdropId |
| [airtags.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/airtags.py) | airtags |
| [alarms.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/alarms.py) | alarms |
| [appConduit.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/appConduit.py) | appconduit |
| [appGrouplisting.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/appGrouplisting.py) | appgrouplisting |
| [appItunesmeta.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/appItunesmeta.py) | appitunesmeta |
| [appSnapshots.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/appSnapshots.py) | applicationsnapshots |
| [appleMapsApplication.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/appleMapsApplication.py) | applemapsapplication |
| [appleMapsGroup.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/appleMapsGroup.py) | applemapsgroup |
| [appleMapsSearchHistory.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/appleMapsSearchHistory.py) | applemapssearchhistory |
| [applePodcasts.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/applePodcasts.py) | applepodcasts |
| [appleWalletCards.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/appleWalletCards.py) | applewalletcards |
| [appleWalletPasses.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/appleWalletPasses.py) | applewalletpasses |
| [appleWalletTransactions.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/appleWalletTransactions.py) | applewallettransactions |
| [appleWifiPlist.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/appleWifiPlist.py) | applewifiplist |
| [applelocationd.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/applelocationd.py) | applelocationd |
| [audiTripdata.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/audiTripdata.py) | auditrip |
| [backupSettings.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/backupSettings.py) | backupSettings |
| [biomeAirpMode.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/biomeAirpMode.py) | biomeAirpMode |
| [biomeAppinstall.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/biomeAppinstall.py) | biomeAppinstall |
| [biomeBacklight.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/biomeBacklight.py) | biomeBacklight |
| [biomeBattperc.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/biomeBattperc.py) | biomeBattperc |
| [biomeBluetooth.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/biomeBluetooth.py) | biomeBluetooth |
| [biomeCarplayisconnected.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/biomeCarplayisconnected.py) | biomeCarplayisconnected |
| [biomeDevWifi.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/biomeDevWifi.py) | biomeDevWifi |
| [biomeDevplugin.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/biomeDevplugin.py) | biomeDevplugin |
| [biomeHardware.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/biomeHardware.py) | biomeHardware |
| [biomeInfocus.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/biomeInfocus.py) | biomeInFocus |
| [biomeIntents.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/biomeIntents.py) | Intents |
| [biomeLocationactivity.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/biomeLocationactivity.py) | biomeLocationactivity |
| [biomeNotes.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/biomeNotes.py) | biomeNotes |
| [biomeNotificationsPub.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/biomeNotificationsPub.py) | biomeNotificationsPub |
| [biomeNowplaying.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/biomeNowplaying.py) | biomeNowplaying |
| [biomeSafari.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/biomeSafari.py) | biomeSafari |
| [biomeSync.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/biomeSync.py) | biomeSync |
| [biomeTextinputses.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/biomeTextinputses.py) | biomeTextinputses |
| [biomeUseractmeta.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/biomeUseractmeta.py) | biomeUseractmeta |
| [biomeWifi.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/biomeWifi.py) | biomeWifi |
| [bluetooth.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/bluetooth.py) | bluetooth |
| [bumble.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/bumble.py) | bumble |
| [cacheRoutesGmap.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/cacheRoutesGmap.py) | cacheroutesgmap |
| [carCD.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/carCD.py) | carCD |
| [cashApp.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/cashApp.py) | cashapp |
| [celWireless.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/celWireless.py) | celwireless |
| [chrome.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/chrome.py) | Chrome |
| [chromeAutofill.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/chromeAutofill.py) | ChromeAutofill |
| [chromeBookmarks.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/chromeBookmarks.py) | ChromeBookmarks |
| [chromeCookies.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/chromeCookies.py) | ChromeCookies |
| [chromeLoginData.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/chromeLoginData.py) | ChromeLoginData |
| [chromeMediaHistory.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/chromeMediaHistory.py) | ChromeMediaHistory |
| [chromeNetworkActionPredictor.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/chromeNetworkActionPredictor.py) | ChromeNetworkActionPredictor |
| [chromeOfflinePages.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/chromeOfflinePages.py) | ChromeOfflinePages |
| [chromeTopSites.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/chromeTopSites.py) | ChromeTopSites |
| [cloudkitCache.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/cloudkitCache.py) | cloudkitcache |
| [cloudkitParticipants.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/cloudkitParticipants.py) | cloudkitparticipants |
| [conDev.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/conDev.py) | condev |
| [confaccts.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/confaccts.py) | confaccts |
| [coreAccessoriesAcc.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/coreAccessoriesAcc.py) | coreAccessories |
| [coreAccessoriesUserEvent.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/coreAccessoriesUserEvent.py) | coreAccessoriesUserEvent |
| [deviceActivator.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/deviceActivator.py) | deviceactivator |
| [deviceDatam.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/deviceDatam.py) | devicedata |
| [deviceName.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/deviceName.py) | deviceName |
| [dhcphp.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/dhcphp.py) | dhcphp |
| [dhcpl.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/dhcpl.py) | dhcpl |
| [discordAcct.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/discordAcct.py) | discordacct |
| [discordJson.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/discordJson.py) | discordjson |
| [discordManifest.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/discordManifest.py) | discordmanifest |
| [draftmessage.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/draftmessage.py) | draftmessage |
| [duetLocations.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/duetLocations.py) | duetlocations |
| [findMy.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/findMy.py) | findMy |
| [fsCachedData.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/fsCachedData.py) | fsChachedData |
| [geodApplications.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/geodApplications.py) | geodapplications |
| [geodMapTiles.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/geodMapTiles.py) | geodmaptiles |
| [geodPDPlaceCache.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/geodPDPlaceCache.py) | geodpdplacecache |
| [googleChat.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/googleChat.py) | googleChat |
| [googleDuo.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/googleDuo.py) | googleduo |
| [hikvision.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/hikvision.py) | hikvision |
| [iCloudWifi.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/iCloudWifi.py) | iCloudWifi |
| [icloudMeta.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/icloudMeta.py) | icloudmeta |
| [icloudPhotoMeta.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/icloudPhotoMeta.py) | aicloudphotometa |
| [icloudSharedalbums.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/icloudSharedalbums.py) | icloudSharedalbums |
| [iconsScreen.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/iconsScreen.py) | iconsScreen |
| [imeiImsi.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/imeiImsi.py) | imeiImsi |
| [imoHD_Chat.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/imoHD_Chat.py) | imoHD_Chat |
| [instagramThreads.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/instagramThreads.py) | instagramThreads |
| [interactionCcontacts.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/interactionCcontacts.py) | interactionCcontacts |
| [keyboard.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/keyboard.py) | keyboard |
| [kijijiConversations.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/kijijiConversations.py) | kijijiConversations |
| [kikBplistmeta.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/kikBplistmeta.py) | kikBplistmeta |
| [kikGroupadmins.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/kikGroupadmins.py) | kikGroupadmins |
| [kikLocaladmin.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/kikLocaladmin.py) | kikLocaladmin |
| [kikMessages.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/kikMessages.py) | kikMessages |
| [kikPendingUploads.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/kikPendingUploads.py) | kikPendingUploads |
| [kikUsersgroups.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/kikUsersgroups.py) | kikUsersgroups |
| [locServicesconfig.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/locServicesconfig.py) | locServicesconfig |
| [mailprotect.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/mailprotect.py) | mailprotect |
| [mapsSync.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/mapsSync.py) | mapsSync |
| [medicalID.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/medicalID.py) | medicalID |
| [messageRetention.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/messageRetention.py) | messageRetention |
| [metamask.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/metamask.py) | metamask |
| [mobileActivationLogs.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/mobileActivationLogs.py) | mobileActivationLogs |
| [mobileBackup.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/mobileBackup.py) | mobileBackup |
| [mobileContainerManager.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/mobileContainerManager.py) | mobileContainerManager |
| [mobileInstall.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/mobileInstall.py) | mobileInstall |
| [mobileInstallb.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/mobileInstallb.py) | mobileInstallb |
| [netusage.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/netusage.py) | netusage |
| [notes.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/notes.py) | notes |
| [notificationsDuet.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/notificationsDuet.py) | notificationsDuet |
| [notificationsXI.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/notificationsXI.py) | notificationsXI |
| [notificationsXII.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/notificationsXII.py) | notificationsXII |
| [obliterated.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/obliterated.py) | obliterated |
| [offlinePages.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/offlinePages.py) | pages |
| [ooklaSpeedtestData.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/ooklaSpeedtestData.py) | ooklaSpeedtestData |
| [photosDbexif.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/photosDbexif.py) | photosDbexif |
| [photosMetadata.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/photosMetadata.py) | photosMetadata |
| [photosMigration.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/photosMigration.py) | photosMigration |
| [preferencesPlist.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/preferencesPlist.py) | preferencesPlist |
| [protonMail.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/protonMail.py) | protonMail |
| [queryPredictions.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/queryPredictions.py) | queryPredictions |
| [quickLook.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/quickLook.py) | quickLook |
| [recentApphistory.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/recentApphistory.py) | recentApphistory |
| [reminders.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/reminders.py) | reminders |
| [restoreLog.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/restoreLog.py) | restoreLog |
| [safariBookmarks.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/safariBookmarks.py) | safariBookmarks |
| [safariFavicons.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/safariFavicons.py) | safariFavicons |
| [safariHistory.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/safariHistory.py) | safariHistory |
| [safariRecentWebSearches.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/safariRecentWebSearches.py) | safariRecentWebSearches |
| [safariTabs.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/safariTabs.py) | safariTabs |
| [safariWebsearch.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/safariWebsearch.py) | safariWebsearch |
| [secretCalculator.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/secretCalculator.py) | secretCalculatorPhotoAlbum |
| [simInfo.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/simInfo.py) | siminfo |
| [slack.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/slack.py) | slack |
| [sms.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/sms.py) | sms |
| [syncDev.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/syncDev.py) | syncDev |
| [teams.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/teams.py) | teams |
| [teamsSegment.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/teamsSegment.py) | teamsSegment |
| [teleguard.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/teleguard.py) | Teleguard |
| [textinputTyping.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/textinputTyping.py) | textinputTyping |
| [tikTok.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/tikTok.py) | tikTok |
| [tileApp.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/tileApp.py) | tileApp |
| [tileAppDb.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/tileAppDb.py) | tileAppDb |
| [tileAppDisc.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/tileAppDisc.py) | tileAppDisc |
| [tileAppNetDb.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/tileAppNetDb.py) | tileAppNetDb |
| [timezoneInfo.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/timezoneInfo.py) | timezoneInfo |
| [timezoneset.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/timezoneset.py) | timezoneset |
| [torrentData.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/torrentData.py) | TorrentData |
| [torrentResumeinfo.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/torrentResumeinfo.py) | torrentResumeinfo |
| [torrentinfo.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/torrentinfo.py) | torrentinfo |
| [venmo.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/venmo.py) | venmo |
| [vipps.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/vipps.py) | vipps |
| [vippsContacts.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/vippsContacts.py) | vippsContacts |
| [voiceRecordings.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/voiceRecordings.py) | voiceRecordings |
| [voiceTriggers.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/voiceTriggers.py) | voiceTriggers |
| [walStrings.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/walStrings.py) | walStrings |
| [weatherAppLocations.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/weatherAppLocations.py) | weatherAppLocations |
| [webClips.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/webClips.py) | webClips |
| [wiLoc.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/wiLoc.py) | wiloc |
| [wifiIdent.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/wifiIdent.py) | wifiIdent |
| [wifiNetworkStoreModel.py](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/wifiNetworkStoreModel.py) | wifiNetworkStoreModel |

## Modules with Errors or No Recognized Artifacts

| Module | Error/Issue |
|--------|-------------|
| NotificationParams.txt | No recognized artifacts found |
| artGlobals.py | No recognized artifacts found |
| script.txt | No recognized artifacts found |

<!-- MODULE_INFO_END -->