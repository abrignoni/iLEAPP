# iLEAPP Artifacts

<!-- MODULE_INFO_START -->

## Summary

Total number of modules: 260  
Number of v1 artifacts: 166  
Number of v2 artifacts: 71  
Number of modules with errors or no recognized artifacts: 3  

## V2 Artifacts Table

| Module | Artifact | Name | Description | Paths |
|--------|----------|------|-------------|-------|
| ControlCenter.py | controlcenter | Control Center Configuration | Parses controls/apps added to the Control Center | `*/mobile/Library/ControlCenter/ModuleConfiguration.plist` |
| DataUsage.py | datausage | Data Usage | Parses application network data usage | `*/wireless/Library/Databases/DataUsage.sqlite*` |
| Ph100UFEDdevcievaluesplist.py | Ph100-UFED-device-values-Plist | UFED Adv Log Acquisition Ph100 UFED Device Values Plist | Parses basic data from */device_values.plist which is a part of a UFED Advance Logical acquisitions | `*/device_values.plist` |
| Ph11KwrdsCapsTitlesDescripsBasicAssetData.py | Ph11-KwrdsCapsTitlesDescripsLikesBasicAsstData-PhDaPsql | PhDaPL Photos.sqlite Ph11 Keywords Captions Titles Descriptions Likes and Basic Asset Data | Parses basic asset record data from iOS18 *PhotoData-Photos.sqlite for assets that have Keywords, Ca | `*/PhotoData/Photos.sqlite*` |
| Ph21AlbumsNonSharedNAD.py | Ph21-Non-Shared Album Records with NAD-PhDaPsql | PhDaPL Photos.sqlite Ph21 Non-Shared Album Records with No Asset Data | Parses Non-Shared Album records found in the PhotoData-Photos.sqlite ZGENERICALBUM Table and support | `*/PhotoData/Photos.sqlite*` |
| Ph22AssetsInNonSharedAlbums.py | Ph22-Assets in Non-Shared Albums-PhDaPsql | PhDaPL Photos.sqlite Ph22 Assets in Non-Shared Albums | Parses Assets associated with Non-Shared Albums found in PhotoData-Photos.sqlite and supports iOS 11 | `*/PhotoData/Photos.sqlite*` |
| Ph23AlbumsSharedNAD.py | Ph23-Shared Album Records & Invites with NAD-PhDaPsql | PhDaPL Photos.sqlite 23 Shared Album Records with No Asset Data | Parses Shared Album records found in the PhotoData-Photos.sqlite ZGENERICALBUM Table and supports iO | `*/PhotoData/Photos.sqlite*` |
| Ph24AssetsInSharedAlbums.py | Ph24-Asset in Shared Albums & Invites-PhDaPsql | PhDaPL Photos.sqlite Ph24 Asset in Shared Albums with invites | Parses Assets in Shared Albums found in PhotoData-Photos.sqlite and supports iOS 18. Parses limited | `*/PhotoData/Photos.sqlite*` |
| Ph30iCloudShareMethodsNAD.py | Ph30-iCloud Shared Methods with NAD-PhDaPsql | PhDaPL Photos.sqlite Ph30 iCld Share Methods with No Asset Data | Parses records for different methods which media files have been shared via iCloud Share found in th | `*/PhotoData/Photos.sqlite*` |
| Ph31iCloudSharePhotoLibraryNAD.py | Ph31-iCloud SPL with Participants with NAD-PhDaPsql | PhDaPL Photos.sqlite Ph31 iCld Shared Photo Library with Partic with No Asset Data | Parses iCloud Shared Photo Library records and invites from the PhotoData-Photos.sqlite ZSHARE Table | `*/PhotoData/Photos.sqlite*` |
| Ph32AssetsIniCldSPLwContrib.py | Ph32-iCloud SPL Assets with Contributor-PhDaPsql | PhDaPL Photos.sqlite Ph32 iCld Shared Photo Library Assets with Contributor | Parses Assets in iCloud Shared Photo Library with contributor information from PhotoData-Photos.sqli | `*/PhotoData/Photos.sqlite*` |
| Ph33AssetsIniCldSPLfromOtherContrib.py | Ph33-iCld SPL Assets from other contrib-PhDaPsql | PhDaPL Photos.sqlite Ph33 iCld Shared Photo Library Assets from other Contributors | Parses Assets in iCloud Shared Photo Library from other contributors from PhotoData-Photos.sqlite ZS | `*/PhotoData/Photos.sqlite*` |
| Ph34iCloudSharedLinksNAD.py | Ph34-iCloud Shared Link Records with NAD-PhDaPsql | PhDaPL Photos.sqlite Ph34 iCld Shared Link Records with No Asset Data | Parses iCloud Shared Link records from the PhotoData-Photos.sqlite ZSHARE Table and supports iOS 14- | `*/PhotoData/Photos.sqlite*` |
| Ph35iCloudSharedLinkAssets.py | Ph35-iCloud Shared Link Assets-PhDaPsql | PhDaPL Photos.sqlite Ph35 iCld Shared Link Assets | Parses iCloud Shared Link records and related assets from the PhotoData-Photos.sqlite ZSHARE Table a | `*/PhotoData/Photos.sqlite*` |
| Ph4Hidden.py | Ph4-Hidden-PhDaPsql | PhDaPL Photos.sqlite 4 Hidden Assets | Parses basic asset record data from PhotoData-Photos.sqlite for hidden assets and supports iOS 11-18 | `*/PhotoData/Photos.sqlite*` |
| Ph51PossOptimizedAssetsIntResouData.py | Ph51-Possible_Optimized_Assets_IntResou-PhDaPsql | SyndPL Photos.sqlite Ph51 Possible Optimized Assets IntResource | Parses iOS 14-18 asset records from PhotoData-Photos.sqlite ZINTERNALRESOURCE and other tables. This | `*/PhotoData/Photos.sqlite*` |
| Ph6ViewedPlayData.py | Ph6-View and Play Data-PhDaPsql | PhDaPL Photos.sqlite Ph6 assets with viewed and played data | Parses basic asset record data from PhotoData-Photos.sqlite for assets with view and played data in | `*/PhotoData/Photos.sqlite*` |
| Ph7Favorite.py | Ph7-Favorite-PhDaPsql | PhDaPL Photos.sqlite Ph7 Favorite Assets | Parses basic asset record data from PhotoData-Photos.sqlite for favorite assets and supports iOS 11- | `*/PhotoData/Photos.sqlite*` |
| Ph80comappleMobileSlideShowPlist.py | Ph80-Com-Apple-MobileSlideshow-Plist | Photos App Settings Ph80 com.apple.mobileslideshow-plist | Parses basic data from com.apple.mobileslideshow.plist which contains some important data related to | `*/Library/Preferences/com.apple.mobileslideshow.plist` |
| Ph81comappleCameraPlist.py | Ph81-Com-Apple-Camera-Plist | Camera App Settings Ph81 Com-Apple-Camera-Plist | Parses data from */mobile/Library/Preferences/com.apple.camera.plist which contains some important d | `*/mobile/Library/Preferences/com.apple.camera.plist` |
| Ph82comappleMediaAnalysisDPlist.py | Ph82-Com-Apple-MediaAnalysisD-Plist | Photo Libraries and Media Analysis Completion Ph82 Com-Apple-MediaAnalysisD-Plist | Parses basic data from */mobile/Library/Preferences/com.apple.mediaanalysisd.plist which contains so | `*/mobile/Library/Preferences/com.apple.mediaanalysisd.plist` |
| Ph83comapplePurpleBuddyPlist.py | Ph83-Com-Apple-PurpleBuddy-Plist | Photos App Settings Ph83 com.apple.purplebuddy-plist | Parses basic data from com.apple.purplebuddy.plist which contains some important data related to dev | `*/Library/Preferences/com.apple.purplebuddy.plist` |
| Ph84CameraSmartSharingMetadataPlist.py | Ph84-Camera-Smart-Sharing-Metadata-Plist | Camera Smart Sharing Settings Ph84 Camera Smart Sharing Metadata Plist | Parses basic data from */PhotoData/Caches/SmartSharing/camera_smart_sharing_metadata.plist which con | `*/PhotoData/Caches/SmartSharing/camera_smart_sharing_metadata.plist` |
| Ph85acntsdcloudServiceEnableLogplist.py | Ph85-accountsd-cloud-Service-Enable-Log-Plist | Accountsd Ph85 cloud Services Enable Log Plist | Parses basic data from */PhotoData/private/com.apple.accountsd/cloudServiceEnableLog.plist which is | `*/com.apple.accountsd/cloudServiceEnableLog.plist` |
| Ph86astsdcloudServiceEnableLogplist.py | Ph86-assetsd-cloud-Service-Enable-Log-Plist | Assetsd Ph86 cloud Services Enable Log Plist | Parses basic data from */PhotoData/private/com.apple.accountsd/cloudServiceEnableLog.plist which is | `*/com.apple.assetsd/cloudServiceEnableLog.plist` |
| Ph8HasAdjustment.py | Ph8-Has Adjustment-PhDaPsql | PhDaPL Photos.sqlite Ph8 Adjusted Assets | Parses basic asset record data from PhotoData-Photos.sqlite for adjusted assets and supports iOS 11- | `*/PhotoData/Photos.sqlite*` |
| Ph99SystemVersionPlist.py | Ph99-System-Version-Plist | Ph99 System Version plist | Parses basic data from device acquisition */System/Library/CoreServices/SystemVersion.plist which co | `*/SystemVersion.plist` |
| Ph9BurstAvalanche.py | Ph9-Burst Avalanche-PhDaPsql | PhDaPL Photos.sqlite Ph9 Burst Avalanche Assets | Parses basic asset record data from PhotoData-Photos.sqlite for burst avalanche assets and supports | `*/PhotoData/Photos.sqlite*` |
| Splitwise.py | splitwise | Splitwise | Parses users, accounts, and transaction information from Splitwise app | `*/Library/Application Support/database.sqlite*` |
| WatchSleepData.py | HealthSleepData | Apple Health Sleep Data | Parses Apple Health Sleep Data from the healthdb_secure.sqlite database | `*Health/healthdb_secure.sqlite*` |
| WatchWornData.py | WatchWornData | Apple Watch Worn Data | Parses Apple Watch Worn Data from the healthdb_secure.sqlite database | `*Health/healthdb_secure.sqlite*` |
| ZangiChats.py | Zangi_Chats | Zangi Chats | Parses Zangi Chat database | `*/private/var/mobile/Containers/Shared/AppGroup/*/zangidb.sqlite*` |
| accs.py | accs | Account Data | Extract information about configured user accounts | `*/mobile/Library/Accounts/Accounts3.sqlite*` |
| adId.py | adId |  |  | `*/containers/Shared/SystemGroup/*/Library/Caches/com.apple.lsdidentifiers.plist` |
| addressBook.py | addressbook | Address Book | Extract information from the native contacts application | `*/mobile/Library/AddressBook/AddressBook*.sqlitedb*` |
| applicationstate.py | applicationstate | Application State | Extract information about bundle container path and data path for Applications | `*/mobile/Library/FrontBoard/applicationState.db*` |
| blockedContacts.py | blockedContacts | Blocked Contacts |  | `*/mobile/Library/Preferences/com.apple.cmfsyncagent.plist` |
| booking.py | booking | Booking.com | account, payment methods, wish lists, viewed, recently searched, recently booked, booked, stored des | `*/mobile/Containers/Data/Application/*/Library/Preferences/com.booking.BookingApp.plist` |
| burner.py | burnerPhoenix | Burner | Parses and extract accounts, contacts, burner numbers and messages | `*/mobile/Containers/Shared/AppGroup/*/Phoenix.sqlite*`, `*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist` |
| burnerCache.py | burnerCache | Burner Cache | Parses and extract accounts, contacts, burner numbers and messages | `*/Library/Caches/com.adhoclabs.burner/Cache.db*`, `*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist` |
| cachev0.py | cachev0 | Image cacheV0 | Images cached in the SQLite database. | `*/cacheV0.db*` |
| calendarAll.py | calendar | Calendar | List of calendars, calendar events and bithdays | `**/Calendar.sqlitedb` |
| callHistory.py | callhistory | Call History | Parses and extract Call History | `**/CallHistory.storedata*`, `**/call_history.db` |
| chatgpt.py | chatgpt | ChatGPT | Get user's ChatGPT conversations, settings and media files. This parser is based on a research proje | `**/Containers/Data/Application/*/Library/Application Support/conversations-*/*.*`, `**/Containers/Data/Application/*/Library/Application Support/drafts-*/*.*`, `**/Containers/Data/Application/*/Library/Preferences/com.openai.chat.StatsigService.plist`, `**/Containers/Data/Application/*/Library/Preferences/com.segment.storage.oai.plist`, `**/Containers/Data/Application/*/Library/Preferences/com.openai.chat.plist`, `**/Containers/Data/Application/*/tmp/recordings/*.*`, `**/Containers/Data/Application/*/tmp/photo-*.*`, `**/Containers/Data/Application/*/tmp/*/*.*` |
| cloudkitSharing.py | cloudkitsharing | Cloudkit Sharing | This module processes data related to CloudKit sharing, encompassing information on notes shared via | `*NoteStore.sqlite*` |
| dmss.py | Dahua Technology (DMSS) | Dahua Technology (DMSS) | Extract data from Dahua Technology (DMSS) Application | `*/Library/Support/Devices.sqlite3*`, `*/Library/Support/configFile1`, `*/Library/Support/*/DMSSCloud.sqlite*`, `*/Documents/Captures/*`, `*/Documents/Videos/*` |
| filesApps.py | filesapp | Files App | Items stored in iCloud Drive. | `*/mobile/Library/Application Support/CloudDocs/session/db/client.db*`, `*/mobile/Library/Application Support/CloudDocs/session/db/server.db*` |
| googleTranslate.py | googleTranslate | Google Translate | History, Favorite translations and Text-To-Speech | `*/mobile/Containers/Data/Application/*/Documents/translate.db*` |
| iTunesBackupInfo.py | iTunesBackupInfo | iTunes Backup Information | Extract information from the Info.plist file of an iTunes backup | `*Info.plist`, `*info.plist` |
| knowledgeC.py | knowledgeC | knowledgeC | Extract Pattern of Life from knowledgeC database | `*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*` |
| lastBuild.py | lastbuild | iOS Information | Extract iOS information from the LastBuildInfo.plist file | `*LastBuildInfo.plist` |
| life360.py | Life360 | Life360 | Parses Life360 app logs, chat messages, and more | `*/com.life360.safetymap *.log`, `*/Library/Application Support/Messaging.sqlite*` |
| line.py | line | Line Artifacts | Get Line | `**/Line.sqlite*` |
| mediaLibrary.py | mediaLibrary | Media Library |  | `**/Medialibrary.sqlitedb*` |
| mobileBackupplist.py | Mobile_Backup_plist | Mobile Backup Plist Settings com-apple-MobileBackup-plist | Parses basic data from */mobile/Library/Preferences/com.apple.MobileBackup.plist which contains some | `*/Library/Preferences/com.apple.MobileBackup.plist` |
| serialNumber.py | serialNumber | Serial Number | Serial Number | `*/Library/Caches/locationd/consolidated.db*` |
| sysShutdown.py | sysShutdown | Sysdiagnose - Shutdown Log | Parses the shutdown.log file from Sysdiagnose logs, based off work by Kaspersky Lab https://github.c | `*/shutdown.log` |
| tcc.py | tcc | Application Permissions | Extract application permissions from TCC.db database | `*/mobile/Library/TCC/TCC.db*` |
| telegramMesssages.py | TelegramMessages | Telegram Messages |  | `*/telegram-data/account-*/postbox/db/db_sqlite*`, `*/telegram-data/account-*/postbox/media/**` |
| tikTokReplied.py | tiktok_replied | TikTok - Replied Referenced Messages | Extracts "Replied" message remnants left in the TikTok database which may no longer exist in the nat | `*/Application/*/Library/Application Support/ChatFiles/*/db.sqlite*`, `*AwemeIM.db*` |
| twint.py | Twint | Twint Transaction Artifacts | Extract all the data available related to transactions made with the instant payment app Twint prepa | `*/var/mobile/Containers/Data/Application/*/Library/Application Support/Twint.sqlite*` |
| uberClient.py | uberClient | Uber | account, payment profiles, nearby vehicles, user address location, searched rides, cached locations, | `*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist` |
| uberLeveldb.py | uberLocations | Uber | Uber locations inside LevelDB | `*/Data/Application/*/Library/Application Support/com.ubercab.UberClient/storagev2/*` |
| uberPlaces.py | uberPlaces | Uber - Places | Parses Uber Places Database | `*/private/var/mobile/Containers/Data/Application/*/Documents/database.db*` |
| viber.py | viber | Viber Artifacts | Get Viber settings, contacts, recent calls and messages information. This script queries Settings.da | `**/com.viber/settings/Settings.data*`, `**/com.viber/database/Contacts.data*`, `**/Containers/Data/Application/*/Documents/Attachments/*.*`, `**/com.viber/ViberIcons/*.*` |
| voicemail.py | voicemail | Voicemail | Parses and extract Voicemail | `**/Voicemail/voicemail.db*`, `**/Voicemail/*.amr` |
| waze.py | waze | Waze | Get account, session, searched locations, recent locations, favorite locations, share locations, tex | `*/mobile/Containers/Data/Application/*/Documents/user.db*`, `*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist` |
| whatsappCallHistory.py | whatsappCallHistory | WhatsappCallHistory |  | `*/var/mobile/Containers/Shared/AppGroup/*/CallHistory.sqlite*`, `*/var/mobile/Containers/Shared/AppGroup/*/ContactsV2.sqlite*` |
| whatsappContacts.py | whatsappContacts | Whatsapp Contacts |  | `*/var/mobile/Containers/Shared/AppGroup/*/ContactsV2.sqlite*` |
| whatsappMessages.py | whatsappMessages | Whatsapp Messages |  | `*/var/mobile/Containers/Shared/AppGroup/*/ChatStorage.sqlite*`, `*/var/mobile/Containers/Shared/AppGroup/*/Message/Media/*/*/*/*.*` |
| wire.py | wire | Wire Artifacts | Get Wire | `**/store.wiredatabase*` |

## V1 Artifacts Table

| Module | Artifacts |
|--------|----------|
| ATXDatastore.py | ATXDatastore |
| AWESearch.py | AWESearch |
| AllTrails.py | alltrails |
| AshHistory.py |  |
| FacebookMessenger.py | facebookmessenger |
| FitnessWorkoutsLocationData.py | Fitness |
| Gmail.py | gmail |
| Health.py | health |
| SMSmissingROWIDs.py |  |
| SiriRemembers.py |  |
| airdropId.py | airdropId |
| airtags.py | airtags |
| alarms.py | alarms |
| appConduit.py | appconduit |
| appGrouplisting.py | appgrouplisting |
| appItunesmeta.py | appitunesmeta |
| appSnapshots.py | applicationsnapshots |
| appleMapsApplication.py | applemapsapplication |
| appleMapsGroup.py | applemapsgroup |
| appleMapsSearchHistory.py | applemapssearchhistory |
| applePodcasts.py | applepodcasts |
| appleWalletCards.py | applewalletcards |
| appleWalletPasses.py | applewalletpasses |
| appleWalletTransactions.py | applewallettransactions |
| appleWifiPlist.py | applewifiplist |
| applelocationd.py | applelocationd |
| audiTripdata.py | auditrip |
| backupSettings.py | backupSettings |
| biomeAirpMode.py | biomeAirpMode |
| biomeAppinstall.py | biomeAppinstall |
| biomeBacklight.py | biomeBacklight |
| biomeBattperc.py | biomeBattperc |
| biomeBluetooth.py | biomeBluetooth |
| biomeCarplayisconnected.py | biomeCarplayisconnected |
| biomeDevWifi.py | biomeDevWifi |
| biomeDevplugin.py | biomeDevplugin |
| biomeHardware.py | biomeHardware |
| biomeInfocus.py | biomeInFocus |
| biomeIntents.py | Intents |
| biomeLocationactivity.py | biomeLocationactivity |
| biomeNotes.py | biomeNotes |
| biomeNotificationsPub.py | biomeNotificationsPub |
| biomeNowplaying.py | biomeNowplaying |
| biomeSafari.py | biomeSafari |
| biomeSync.py | biomeSync |
| biomeTextinputses.py | biomeTextinputses |
| biomeUseractmeta.py | biomeUseractmeta |
| biomeWifi.py | biomeWifi |
| bluetooth.py | bluetooth |
| bumble.py | bumble |
| cacheRoutesGmap.py | cacheroutesgmap |
| carCD.py | carCD |
| cashApp.py | cashapp |
| celWireless.py | celwireless |
| chrome.py | Chrome |
| chromeAutofill.py | ChromeAutofill |
| chromeBookmarks.py | ChromeBookmarks |
| chromeCookies.py | ChromeCookies |
| chromeLoginData.py | ChromeLoginData |
| chromeMediaHistory.py | ChromeMediaHistory |
| chromeNetworkActionPredictor.py | ChromeNetworkActionPredictor |
| chromeOfflinePages.py | ChromeOfflinePages |
| chromeTopSites.py | ChromeTopSites |
| cloudkitCache.py | cloudkitcache |
| cloudkitParticipants.py | cloudkitparticipants |
| conDev.py | condev |
| confaccts.py | confaccts |
| coreAccessoriesAcc.py | coreAccessories |
| coreAccessoriesUserEvent.py | coreAccessoriesUserEvent |
| deviceActivator.py | deviceactivator |
| deviceDatam.py | devicedata |
| deviceName.py | deviceName |
| dhcphp.py | dhcphp |
| dhcpl.py | dhcpl |
| discordAcct.py | discordacct |
| discordJson.py | discordjson |
| discordManifest.py | discordmanifest |
| draftmessage.py | draftmessage |
| duetLocations.py | duetlocations |
| findMy.py | findMy |
| fsCachedData.py | fsChachedData |
| geodApplications.py | geodapplications |
| geodMapTiles.py | geodmaptiles |
| geodPDPlaceCache.py | geodpdplacecache |
| googleChat.py | googleChat |
| googleDuo.py | googleduo |
| hikvision.py | hikvision |
| iCloudWifi.py | iCloudWifi |
| icloudMeta.py | icloudmeta |
| icloudPhotoMeta.py | aicloudphotometa |
| icloudSharedalbums.py | icloudSharedalbums |
| iconsScreen.py | iconsScreen |
| imeiImsi.py | imeiImsi |
| imoHD_Chat.py | imoHD_Chat |
| instagramThreads.py | instagramThreads |
| interactionCcontacts.py | interactionCcontacts |
| keyboard.py | keyboard |
| kijijiConversations.py | kijijiConversations |
| kikBplistmeta.py | kikBplistmeta |
| kikGroupadmins.py | kikGroupadmins |
| kikLocaladmin.py | kikLocaladmin |
| kikMessages.py | kikMessages |
| kikPendingUploads.py | kikPendingUploads |
| kikUsersgroups.py | kikUsersgroups |
| locServicesconfig.py | locServicesconfig |
| mailprotect.py | mailprotect |
| mapsSync.py | mapsSync |
| medicalID.py | medicalID |
| messageRetention.py | messageRetention |
| metamask.py | metamask |
| mobileActivationLogs.py | mobileActivationLogs |
| mobileBackup.py | mobileBackup |
| mobileContainerManager.py | mobileContainerManager |
| mobileInstall.py | mobileInstall |
| mobileInstallb.py | mobileInstallb |
| netusage.py | netusage |
| notes.py | notes |
| notificationsDuet.py | notificationsDuet |
| notificationsXI.py | notificationsXI |
| notificationsXII.py | notificationsXII |
| obliterated.py | obliterated |
| offlinePages.py | pages |
| ooklaSpeedtestData.py | ooklaSpeedtestData |
| photosDbexif.py | photosDbexif |
| photosMetadata.py | photosMetadata |
| photosMigration.py | photosMigration |
| preferencesPlist.py | preferencesPlist |
| protonMail.py | protonMail |
| queryPredictions.py | queryPredictions |
| quickLook.py | quickLook |
| recentApphistory.py | recentApphistory |
| reminders.py | reminders |
| restoreLog.py | restoreLog |
| safariBookmarks.py | safariBookmarks |
| safariFavicons.py | safariFavicons |
| safariHistory.py | safariHistory |
| safariRecentWebSearches.py | safariRecentWebSearches |
| safariTabs.py | safariTabs |
| safariWebsearch.py | safariWebsearch |
| secretCalculator.py | secretCalculatorPhotoAlbum |
| simInfo.py | siminfo |
| slack.py | slack |
| sms.py | sms |
| syncDev.py | syncDev |
| teams.py | teams |
| teamsSegment.py | teamsSegment |
| teleguard.py | Teleguard |
| textinputTyping.py | textinputTyping |
| tikTok.py | tikTok |
| tileApp.py | tileApp |
| tileAppDb.py | tileAppDb |
| tileAppDisc.py | tileAppDisc |
| tileAppNetDb.py | tileAppNetDb |
| timezoneInfo.py | timezoneInfo |
| timezoneset.py | timezoneset |
| torrentData.py | TorrentData |
| torrentResumeinfo.py | torrentResumeinfo |
| torrentinfo.py | torrentinfo |
| venmo.py | venmo |
| vipps.py | vipps |
| vippsContacts.py | vippsContacts |
| voiceRecordings.py | voiceRecordings |
| voiceTriggers.py | voiceTriggers |
| walStrings.py | walStrings |
| weatherAppLocations.py | weatherAppLocations |
| webClips.py | webClips |
| wiLoc.py | wiloc |
| wifiIdent.py | wifiIdent |
| wifiNetworkStoreModel.py | wifiNetworkStoreModel |

## Modules with Errors or No Recognized Artifacts

| Module | Error/Issue |
|--------|-------------|
| NotificationParams.txt | No recognized artifacts found |
| artGlobals.py | No recognized artifacts found |
| script.txt | No recognized artifacts found |

<!-- MODULE_INFO_END -->