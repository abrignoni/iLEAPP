__artifacts_v2__ = {
    "idstatuscache": {
        "name": "Identity Lookup Service",
        "description": "iCloud sync, Email, FaceTime, more",
        "author": "Django Faiola (djangofaiola.blogspot.com)",
        "version": "0.1.0",
        "date": "2024-07-16",
        "requirements": "none",
        "category": "Identity Lookup Service",
        "notes": "",            
        "paths": ("*/mobile/Library/Preferences/com.apple.identityservices.idstatuscache.plist",
                  "*/mobile/Library/IdentityServices/idstatuscache.plist"),
        "function": "get_idstatuscache"
    }
}

import plistlib
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, convert_ts_int_to_utc, convert_utc_human_to_timezone

# service type and partner
def get_service_type_and_partner(value : str):
    if bool(value):
        # type (e.g. tel:+390771XXXXX)
        parts = value.split(':', 1)
        service_type = parts[0] # tel
        partner = parts[1]      # +390771XXXXX

        # telephone
        if service_type == 'tel':
            return 'Telephone', partner
        # email
        elif service_type == 'mailto':
            return 'Email', partner
        # urn
        elif service_type == 'urn':
            return 'URN', partner
        # other
        else:
            return service_type, partner
    else:
        return '', ''


# map identifiers
def map_identifiers(seeker):
    map_ids = {}

    # default map
    map_ids['com.apple.madrid'] = 'iMessage'
    map_ids['com.apple.iMessage'] = 'iMessage'            # legacy
    map_ids['com.apple.ess'] = 'FaceTime'
    map_ids['com.apple.FaceTime'] = 'FaceTime'            # legacy
    map_ids['com.apple.private.ac'] = 'Calling'
    map_ids['com.apple.Calling'] = 'Calling'              # legacy
    map_ids['com.apple.private.alloy.accessibility.switchcontrol'] ='Accessibility SwitchControl'
    map_ids['com.apple.private.alloy.accountssync'] = 'AccountsSync'
    map_ids['com.apple.private.alloy.addressbooksync'] = 'AddressBookSync'
    map_ids['com.apple.private.alloy.airtraffic'] = 'AirTraffic'
    map_ids['com.apple.private.alloy.amsaccountsync'] = 'AMSAccountSync'
    map_ids['com.apple.private.alloy.anisette'] = 'AuthKitAnisette'
    map_ids['com.apple.private.alloy.appconduit'] = 'AppConduit'
    map_ids['com.apple.private.alloy.appconduit.v2'] = 'AppConduit'
    map_ids['com.apple.private.alloy.applepay'] = 'Apple Pay'
    map_ids['com.apple.private.alloy.apppredictionsync'] = 'AppPrediction Data Sync'
    map_ids['com.apple.private.alloy.appregistrysync'] = 'AppRegistrySync'
    map_ids['com.apple.private.alloy.appstore'] = 'AppStore'
    map_ids['com.apple.private.alloy.appsyncconduit'] = 'AppSyncConduit'
    map_ids['com.apple.private.alloy.appsyncconduit.v2'] = 'AppSyncConduit'
    map_ids['com.apple.private.alloy.audiocontrol.music'] = 'AudioControl'
    map_ids['com.apple.private.alloy.authkit'] = 'AuthKit'
    map_ids['com.apple.private.alloy.autobugcapture'] = 'iCloudPairing'
    map_ids['com.apple.private.alloy.avconference.avctester'] = 'AVConference AVCTester'
    map_ids['com.apple.private.alloy.avconference.icloud'] = 'AVConference iCloud'
    map_ids['com.apple.private.alloy.biz'] = 'BusinessMessage'
    map_ids['com.apple.private.alloy.bluetooth.audio'] = 'Bluetooth Audio'
    map_ids['com.apple.private.alloy.bluetoothregistry.cloud'] = 'NanoRegistryCloud'
    map_ids['com.apple.private.alloy.bluetoothregistry'] = 'NanoRegistry'
    map_ids['com.apple.private.alloy.bluetoothregistryclassa'] = 'NanoRegistryClassA'
    map_ids['com.apple.private.alloy.bluetoothregistryclassc'] = 'NanoRegistry'
    map_ids['com.apple.private.alloy.bulletinboard'] = 'SpringBoardNotificationSync'
    map_ids['com.apple.private.alloy.bulletindistributor'] = 'BulletinDistributor'
    map_ids['com.apple.private.alloy.bulletindistributor.settings'] = 'BulletinDistributorSettings'
    map_ids['com.apple.private.alloy.callhistorysync'] = 'CallHistory Sync'
    map_ids['com.apple.private.alloy.camera.proxy'] = 'CameraProxy'
    map_ids['com.apple.private.alloy.clockface.sync'] = 'ClockFace Sync'
    map_ids['com.apple.private.alloy.cmsession'] = 'CMSession'
    map_ids['com.apple.private.alloy.companionproxy'] = 'CompanionProxy'
    map_ids['com.apple.private.alloy.continuity.activity'] = 'Continuity Activity'
    map_ids['com.apple.private.alloy.continuity.auth.classa'] = 'Continuity Auth Class A'
    map_ids['com.apple.private.alloy.continuity.auth'] = 'Continuity Auth'
    map_ids['com.apple.private.alloy.continuity.encryption'] = 'Continuity Encryption'
    map_ids['com.apple.private.alloy.continuity.tethering'] = 'Continuity Tethering'
    map_ids['com.apple.private.alloy.continuity.unlock'] = 'Continuity Unlock'
    map_ids['com.apple.private.alloy.coreduet'] = 'CoreDuet'
    map_ids['com.apple.private.alloy.coreduet.sync'] = 'CoreDuet Sync'
    map_ids['com.apple.private.alloy.ct.baseband.p2p.notification'] = 'Baseband P2P Notifications'
    map_ids['com.apple.private.alloy.ct.commcenter.p2w.settings'] = 'Commcenter P2W Settings'
    map_ids['com.apple.private.alloy.ct.commcenter.sim.cloud'] = 'CommCenter SIM Cloud'
    map_ids['com.apple.private.alloy.ct.commcenter.sim'] = 'Commcenter SIM'
    map_ids['com.apple.private.alloy.ded'] = 'diagExtentionDaemon'
    map_ids['com.apple.private.alloy.ded.watch'] = 'Diagnostic Extension Watch'
    map_ids['com.apple.private.alloy.digitalhealth'] = 'DigitalHealth'
    map_ids['com.apple.private.alloy.donotdisturb'] = 'DoNotDisturb'
    map_ids['com.apple.private.alloy.electrictouch'] = 'ElectricTouch'
    map_ids['com.apple.private.alloy.eventkitmutation'] = 'EventKit Mutation'
    map_ids['com.apple.private.alloy.eventkitsync'] = 'EventKitSync'
    map_ids['com.apple.private.alloy.facetime.audio'] = 'FaceTime Audio'
    map_ids['com.apple.private.alloy.facetime.lp'] = 'FaceTime LP'
    map_ids['com.apple.private.alloy.facetime.multi'] = 'FaceTime Multi'
    map_ids['com.apple.private.alloy.facetime.mw'] = 'FaceTime MW'
    map_ids['com.apple.private.alloy.facetime.video'] = 'FaceTime Video'
    map_ids['com.apple.private.alloy.fetimesync'] = 'FeTimeSync'
    map_ids['com.apple.private.alloy.fignero'] = 'FigNero'
    map_ids['com.apple.private.alloy.findmydeviced.aoverc'] = 'Find My iPhone (A over C)'
    map_ids['com.apple.private.alloy.findmydeviced.watch'] = 'Find My iPhone'
    map_ids['com.apple.private.alloy.findmylocaldevice'] = 'Find My Local Device'
    map_ids['com.apple.private.alloy.fitnessfriends.icloud'] = 'FitnessFriends iCloud'
    map_ids['com.apple.private.alloy.fitnessfriends.imessage'] = 'FitnessFriends iMessage'
    map_ids['com.apple.private.alloy.fmd'] = 'Find My Friends'
    map_ids['com.apple.private.alloy.fmf'] = 'FindMyFriends'
    map_ids['com.apple.private.alloy.fmflocator'] = 'FMF Locator'
    map_ids['com.apple.private.alloy.gamecenter.imessage'] = 'Gamecenter iMessage'
    map_ids['com.apple.private.alloy.gamecenter'] = 'GameCenter'
    map_ids['com.apple.private.alloy.health.sync.classc'] = 'HealthSync (A over C)'
    map_ids['com.apple.private.alloy.icloudpairing'] = 'iCloudPairing'
    map_ids['com.apple.private.alloy.ids.cloudmessaging'] = 'IDS Cloud Messaging'
    map_ids['com.apple.private.alloy.idscredentials'] = 'IDSCredentials'
    map_ids['com.apple.private.alloy.idsremoteurlconnection'] = 'IDSRemoteURLConnection'
    map_ids['com.apple.private.alloy.idstransfers'] = 'IDS Transfers'
    map_ids['com.apple.private.alloy.iosdiagnostics.icloud'] = 'iosdiagnosticsicloud'
    map_ids['com.apple.private.alloy.iosdiagnostics'] = 'iOS Diagnostics'
    map_ids['com.apple.private.alloy.iratmanager'] = 'iRatManager'
    map_ids['com.apple.private.alloy.itesterd.transferService.icloud'] = 'iTesterTransferServiceiCloud'
    map_ids['com.apple.private.alloy.itunes'] = 'iTunes'
    map_ids['com.apple.private.alloy.livability'] = 'Livability'
    map_ids['com.apple.private.alloy.itunescloudd'] = 'itunescloudd'
    map_ids['com.apple.private.alloy.location.auth'] = 'LocationAuth'
    map_ids['com.apple.private.alloy.location.motion'] = 'LocationMotion'
    map_ids['com.apple.private.alloy.location.stream'] = 'LocationStream'
    map_ids['com.apple.private.alloy.location.usage'] = 'LocationUsage'
    map_ids['com.apple.private.alloy.location.wifitilesync'] = 'LocationWiFiTileSync'
    map_ids['com.apple.private.alloy.logcabin'] = 'logcabin'
    map_ids['com.apple.private.alloy.mail.fetches'] = 'MailFetches'
    map_ids['com.apple.private.alloy.mail.sync.accounts'] = 'MailAccounts'
    map_ids['com.apple.private.alloy.mail.sync.content'] = 'MailContent'
    map_ids['com.apple.private.alloy.mail.sync.messages'] = 'MailMessages'
    map_ids['com.apple.private.alloy.mail.sync.protected.content'] = 'MailClassAProtectedContent'
    map_ids['com.apple.private.alloy.mail.sync.protected'] = 'MailClassAProtected'
    map_ids['com.apple.private.alloy.maps.eta'] = 'SharedETA'
    map_ids['com.apple.private.alloy.maps'] = 'Maps'
    map_ids['com.apple.private.alloy.maps.proxy'] = 'MapsProxy'
    map_ids['com.apple.private.alloy.maps.sync'] = 'MapsSync'
    map_ids['com.apple.private.alloy.mediaremote'] = 'MediaRemote'
    map_ids['com.apple.private.alloy.messagenotification'] = 'Message Notification'
    map_ids['com.apple.private.alloy.messages'] = 'Messages'
    map_ids['com.apple.private.alloy.messagesquickswitch'] = 'MessagesQuickSwitch'
    map_ids['com.apple.private.alloy.mobiletimersync'] = 'MobileTimerSync'
    map_ids['com.apple.private.alloy.multiplex1'] = 'Multiplex 1'
    map_ids['com.apple.private.alloy.nanoappmonitor'] = 'NanoAppMonitor'
    map_ids['com.apple.private.alloy.nanobackup'] = 'NanoBackup'
    map_ids['com.apple.private.alloy.nearby'] = 'Nearby'
    map_ids['com.apple.private.alloy.news'] = 'Nano News'
    map_ids['com.apple.private.alloy.nsurlsessionproxy'] = 'NSURLSession Proxy'
    map_ids['com.apple.private.alloy.octagon'] = 'Octagon'
    map_ids['com.apple.private.alloy.otaupdate.cloud'] = 'OTAUpdate Cloud'
    map_ids['com.apple.private.alloy.otaupdate'] = 'OTAUpdate'
    map_ids['com.apple.private.alloy.pairedunlock'] = 'PairedUnlock'
    map_ids['com.apple.private.alloy.passbook.general'] = 'PassbookGeneral'
    map_ids['com.apple.private.alloy.passbook.maintenance'] = 'PassbookMaintenance'
    map_ids['com.apple.private.alloy.passbook.provisioning'] = 'PassbookProvisioning'
    map_ids['com.apple.private.alloy.passbook.relevancy'] = 'PassbookRelevancy'
    map_ids['com.apple.private.alloy.passbook.remoteadmin'] = 'PassbookRemoteAdmin'
    map_ids['com.apple.private.alloy.passbook.standalone.inapp'] = 'PassbookStandaloneInApp'
    map_ids['com.apple.private.alloy.passbook.standalone.provisioning'] = 'PassbookStandaloneProvisioning'
    map_ids['com.apple.private.alloy.pbbridge.connectivity'] = 'Bridge Connectivity'
    map_ids['com.apple.private.alloy.pbbridge'] = 'Setup Bridge'
    map_ids['com.apple.private.alloy.pcskey.sync'] = 'PCSKey Sync'
    map_ids['com.apple.private.alloy.phone.auth'] = 'PhoneAuth'
    map_ids['com.apple.private.alloy.phonecontinuity'] = 'Phone Continuity'
    map_ids['com.apple.private.alloy.photos.proxy'] = 'PhotosProxy'
    map_ids['com.apple.private.alloy.photostream'] = 'PhotoStream'
    map_ids['com.apple.private.alloy.preferencessync'] = 'PreferencesSync'
    map_ids['com.apple.private.alloy.proactiveeventtracker'] = 'proactiveeventtracker'
    map_ids['com.apple.private.alloy.proxiedcrashcopier.icloud'] = 'Proxied Crash Copier Cloud'
    map_ids['com.apple.private.alloy.proxiedcrashcopier'] = 'ProxiedCrashCopier'
    map_ids['com.apple.private.alloy.pushproxy'] = 'PushProxy'
    map_ids['com.apple.private.alloy.quickboard.classa'] = 'QuickboardClassA'
    map_ids['com.apple.private.alloy.remotemediaservices'] = 'RemoteMediaServices'
    map_ids['com.apple.private.alloy.resourcegrabber'] = 'ResourceGrabber'
    map_ids['com.apple.private.alloy.safeview'] = 'Safeview'
    map_ids['com.apple.private.alloy.screenshotter'] = 'Screenshotter'
    map_ids['com.apple.private.alloy.screentimelocal'] = 'screentimelocal'
    map_ids['com.apple.private.alloy.sensorkit'] = 'Sensor Kit'
    map_ids['com.apple.private.alloy.sensorkitkeys'] = 'SensorKitKeys'
    map_ids['com.apple.private.alloy.sharing.paireddevice'] = 'Sharing Paired Device Info'
    map_ids['com.apple.private.alloy.siri.device'] = 'SiriDevice'
    map_ids['com.apple.private.alloy.siri.icloud'] = 'Siri Cloud'
    map_ids['com.apple.private.alloy.siri.location'] = 'SiriLocation'
    map_ids['com.apple.private.alloy.siri.phrasespotter'] = 'SiriPhraseSpotter'
    map_ids['com.apple.private.alloy.siri.proxy'] = 'SiriProxy'
    map_ids['com.apple.private.alloy.siri.voiceshortcuts'] = 'Siri VoiceShortcuts'
    map_ids['com.apple.private.alloy.sms'] = 'SMSRelay'
    map_ids['com.apple.private.alloy.sms.watch'] = 'SMSWatch'
    map_ids['com.apple.private.alloy.sockpuppet.classd'] = 'SockPuppet Class D'
    map_ids['com.apple.private.alloy.sockpuppet'] = 'SockPuppet'
    map_ids['com.apple.private.alloy.sysdiagnose'] = 'Sysdiagnose'
    map_ids['com.apple.private.alloy.systemsettings'] = 'SystemSettings'
    map_ids['com.apple.private.alloy.tccd.msg'] = 'tccd messaging'
    map_ids['com.apple.private.alloy.tccd.sync'] = 'tccd sync'
    map_ids['com.apple.private.alloy.telephonyutilitiestemporary'] = 'TelephonyUtilities Temporary'
    map_ids['com.apple.private.alloy.terminus'] = 'NetworkRelay'
    map_ids['com.apple.private.alloy.thumper.keys'] = 'ThumperKeys'
    map_ids['com.apple.private.alloy.thumper.settings'] = 'ThumperSettings'
    map_ids['com.apple.private.alloy.timesync'] = 'TimeSync'
    map_ids['com.apple.private.alloy.timezonesync'] = 'TimeZoneSync'
    map_ids['com.apple.private.alloy.tincan.audio'] = 'Tincan Audio'
    map_ids['com.apple.private.alloy.tips'] = 'Tips'
    map_ids['com.apple.private.alloy.toolchestlite'] = 'Tool Chest Lite'
    map_ids['com.apple.private.alloy.voicemailsync'] = 'VoiceMail Sync'
    map_ids['com.apple.private.alloy.watchconnectivity.classd'] = 'Watch Connectivity Class D'
    map_ids['com.apple.private.alloy.watchconnectivity'] = 'Watch Connectivity'
    map_ids['com.apple.private.alloy.webkitnetworking'] = 'WebKit Networking'
    map_ids['com.apple.private.alloy.wifi.networksync'] = 'WiFiManager_WiFiNetworkSync_IDS'
    map_ids['com.apple.private.alloy.willow'] = 'Willow'
    map_ids['com.apple.private.alloy.willow.proxy'] = 'Willow Proxy'
    map_ids['com.apple.private.alloy.willow.stream'] = 'Willow Stream'
    
    # /System/Library/IdentityServices/ServiceDefinitions/
    source_files = seeker.search('*/System/Library/IdentityServices/ServiceDefinitions/*.plist')
    for file_found in source_files:
        f = open(file_found, "rb")
        try:
            plist = plistlib.load(f)
            if bool(plist):
                # current identifier
                identifier = plist.get('Identifier')
                # legacy identifier
                legacy_identifier = plist.get('LegacyIdentifier')
                # display name
                display_name = plist.get('DisplayName')
                # service name
                #service_name = plist.get('ServiceName')

                # current identifier
                if bool(identifier): map_ids[identifier] = display_name
                # legacy identifier
                if bool(legacy_identifier): map_ids[legacy_identifier] = display_name

        except Exception as ex:
            logfunc('Exception while parsing Identity Lookup Service: ' + str(ex))
            pass
        finally:
            f.close()

    return map_ids


# com.apple.identityservices.idstatuscache.plist
# idstatuscache.plist
def get_identity_services(file_found, identifiers, report_folder, timezone_offset):
    data_list = []

    f = open(file_found, "rb")
    try:
        plist = plistlib.load(f)
        if bool(plist):
            for key, value in plist.items():
                if not isinstance(value, dict): 
                    continue

                # reset values
                row = [ None ] * 6

                for cat_key, cat_value in value.items():                   
                    # type, partner (e.g. mailto:account@me.com, tel:+1234567890)
                    row[0], row[1] = get_service_type_and_partner(cat_key)
                    # lookup date (timestamp)
                    lookup_date = cat_value.get('LookupDate')
                    if lookup_date != None:
                        lookup_date = convert_ts_int_to_utc(int(lookup_date + 978307200))
                        row[2] = convert_utc_human_to_timezone(lookup_date, timezone_offset)
                    # status id
                    status_id = cat_value.get('IDStatus')
                    if status_id != None:
                        if status_id == 1: row[3] = 'iDevice'
                        elif status_id == 2: row[3] = 'Not iDevice'
                        else: row[3] = status_id
                    # display name
                    row[4] = identifiers.get(key, 'N/D')                     
                    # identifier
                    row[5] = key

                    # location
                    location = f'[{key}][{cat_key}]'

                    # row
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], location))

    except Exception as ex:
        logfunc('Exception while parsing Identity Lookup Service: ' + str(ex))
    finally:
        f.close()

    # row
    if row.count(None) != len(row):
        report = ArtifactHtmlReport('Identity Lookup Service')
        report.start_artifact_report(report_folder, 'Identity Lookup Service')
        report.add_script()
        data_headers = ('Service type', 'Partner', 'Recently searched', 'Device type', 'Application', 'Identifier', 'Location')

        #data_list.append(row)

        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()
                
        tsvname = f'Identity Lookup Service'
        tsv(report_folder, data_headers, data_list, tsvname)
                
        tlactivity = 'Identity Lookup Service'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Identity Lookup Service data available')


# idstatuscache
def get_idstatuscache(files_found, report_folder, seeker, wrap_text, timezone_offset):
    identifiers = {}

    # map service definitions
    if len(files_found) > 0:
        identifiers = map_identifiers(seeker)
        
    for file_found in files_found:
        # com.apple.identityservices.idstatuscache.plist (until iOS 14.6.0)
        # idstatuscache.plist (from iOS 14.7.0)           
        if file_found.endswith('com.apple.identityservices.idstatuscache.plist') or file_found.endswith('idstatuscache.plist'):
            get_identity_services(file_found, identifiers, report_folder, timezone_offset)
            break