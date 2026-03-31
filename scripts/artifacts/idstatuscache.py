"""
iLEAPP Artifact Module for Identity Lookup Service.
Parses iCloud sync, Email, FaceTime, and other lookup services by identifying 
how Apple devices verify the availability of communication services for specific 
contacts (partners).
"""

__artifacts_v2__ = {
    "idstatuscache": {
        "name": "Identity Lookup Service",
        "description": "Extracts iCloud sync, Email, FaceTime, more.",
        "author": "@djangofaiola",
        "creation_date": "2024-07-16",
        "last_update_date": "2026-03-31",
        "requirements": "none",
        "category": "Identity Lookup Service",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": (
            "*/mobile/Library/Preferences/com.apple.identityservices.idstatuscache.plist",
            "*/mobile/Library/IdentityServices/idstatuscache.plist"
        ),
        "output_types": [ "standard" ],
        "artifact_icon": "user"
    }
}


from scripts.ilapfuncs import get_plist_file_content, convert_cocoa_core_data_ts_to_utc, \
    artifact_processor, logfunc


# Mapping to convert raw service prefixes into human-readable formats
SERVICE_TYPE_MAP = {
    # Standard Communications & Protocols
    'tel': 'Telephone',                   # Standard telephone number URI scheme
    'e164': 'Telephone (E.164)',          # Internationally formatted telephone number
                                          # (ITU standard)
    'mailto': 'Email',                    # Standard email address scheme
    'sip': 'SIP / VoIP',                  # Session Initiation Protocol, often used for
                                          # Wi-Fi calling
    'urn': 'URN',                         # Uniform Resource Name, a generic standard identifier
    # Apple Communications
    'sms': 'SMS',                         # Short Message Service routing (Standard carrier texts)
    'facetime': 'FaceTime',               # Standard FaceTime video call routing
    'facetime-audio': 'FaceTime Audio',   # FaceTime audio-only routing
    'imessage': 'iMessage',               # Apple's proprietary end-to-end encrypted messaging
    # Accounts & Identities
    'x-apple': 'Apple ID',                # Generic Apple ID associated service or identifier
    'x-apple-dsid': 'Apple ID (DSID)',    # Destination Sign-In ID
                                          # (Unique numeric iCloud account ID)
    'acct': 'Account Identifier',         # Generic internal system account identifier
    'pseudonym': 'Apple Pseudonym ID',    # Anonymized ID used for "Sign in with Apple" privacy
                                          # features
    'mailto-alias': 'Email Alias',        # Often used for Apple's "Hide My Email" generated aliases
    # System, Hardware & Pairing
    'token': 'Push Token',                # Apple Push Notification service (APNs) device token
    'uuid': 'Device UUID',                # Universally Unique Identifier for hardware or pairing
                                          # sessions
    'mac': 'MAC Address',                 # Media Access Control address for general network
                                          # interfaces
    'bt': 'Bluetooth MAC',                # Bluetooth-specific hardware address
    'icloud': 'iCloud Service',           # General iCloud syncing, background routing, or CloudKit
                                          # data
    'watch': 'Apple Watch',               # Identifiers used during Apple Watch pairing and sync
                                          # requests
    'companion': 'Companion Device',      # Linked companion devices (e.g., iPad or Mac via
                                          # Continuity)
    # Special Services & Features
    'gamecenter': 'Game Center',          # Apple Game Center matchmaking and friend routing
    'vvm': 'Visual Voicemail',            # Carrier-provided visual voicemail syncing service
    'urn:service:sos': 'Emergency SOS',   # Satellite or cellular emergency routing services
    'multiplex1': 'Multiplex Stream'      # Internal combined Audio/Video/Data stream
                                          # (often for AVConference)
}


# Default mapping for system applications and internal daemons.
DEFAULT_MAP_IDS = {
    'com.apple.Calling': 'Calling',     # legacy
    'com.apple.ess': 'FaceTime',
    'com.apple.FaceTime': 'FaceTime',   # legacy
    'com.apple.iMessage': 'iMessage',   # legacy
    'com.apple.madrid': 'iMessage',
    'com.apple.private.ac': 'Calling',
    'com.apple.private.alloy.accessibility.switchcontrol': 'Accessibility SwitchControl',
    'com.apple.private.alloy.accessibility.vision': 'Accessibility Vision Context',
    'com.apple.private.alloy.accountssync': 'AccountsSync',
    'com.apple.private.alloy.addressbooksync': 'AddressBookSync',
    'com.apple.private.alloy.ai.agent': 'Siri Intelligent Agent',
    'com.apple.private.alloy.airdrop': 'AirDrop',
    'com.apple.private.alloy.airtraffic': 'AirTraffic',
    'com.apple.private.alloy.ambient': 'StandBy Mode Sync',
    'com.apple.private.alloy.amsaccountsync': 'AMSAccountSync',
    'com.apple.private.alloy.anisette': 'AuthKitAnisette',
    'com.apple.private.alloy.appconduit': 'AppConduit',
    'com.apple.private.alloy.appconduit.v2': 'AppConduit',
    'com.apple.private.alloy.applepay': 'Apple Pay',
    'com.apple.private.alloy.applepay.peer-to-peer': 'Apple Cash / P2P',
    'com.apple.private.alloy.applepay.v2': 'Apple Pay v2',
    'com.apple.private.alloy.apppredictionsync': 'AppPrediction Data Sync',
    'com.apple.private.alloy.appregistrysync': 'AppRegistrySync',
    'com.apple.private.alloy.appstore': 'AppStore',
    'com.apple.private.alloy.appsyncconduit': 'AppSyncConduit',
    'com.apple.private.alloy.appsyncconduit.v2': 'AppSyncConduit',
    'com.apple.private.alloy.audiocontrol.music': 'AudioControl',
    'com.apple.private.alloy.authkit': 'AuthKit',
    'com.apple.private.alloy.autobugcapture': 'iCloudPairing',
    'com.apple.private.alloy.avconference.avctester': 'AVConference AVCTester',
    'com.apple.private.alloy.avconference.icloud': 'AVConference iCloud',
    'com.apple.private.alloy.biz': 'BusinessMessage',
    'com.apple.private.alloy.bluetooth.audio': 'Bluetooth Audio',
    'com.apple.private.alloy.bluetoothregistry': 'NanoRegistry',
    'com.apple.private.alloy.bluetoothregistry.cloud': 'NanoRegistryCloud',
    'com.apple.private.alloy.bluetoothregistryclassa': 'NanoRegistryClassA',
    'com.apple.private.alloy.bluetoothregistryclassc': 'NanoRegistry',
    'com.apple.private.alloy.bulletinboard': 'SpringBoardNotificationSync',
    'com.apple.private.alloy.bulletindistributor': 'BulletinDistributor',
    'com.apple.private.alloy.bulletindistributor.settings': 'BulletinDistributorSettings',
    'com.apple.private.alloy.callhistorysync': 'CallHistory Sync',
    'com.apple.private.alloy.camera.proxy': 'CameraProxy',
    'com.apple.private.alloy.carplay.spatial': 'Next-Gen CarPlay Spatial',
    'com.apple.private.alloy.chronod': 'Widget Data Sync',
    'com.apple.private.alloy.clockface.sync': 'ClockFace Sync',
    'com.apple.private.alloy.cmsession': 'CMSession',
    'com.apple.private.alloy.companionproxy': 'CompanionProxy',
    'com.apple.private.alloy.continuity.activity': 'Continuity Activity',
    'com.apple.private.alloy.continuity.activity.public': 'Continuity Public Activity',
    'com.apple.private.alloy.continuity.auth': 'Continuity Auth',
    'com.apple.private.alloy.continuity.auth.classa': 'Continuity Auth Class A',
    'com.apple.private.alloy.continuity.auth.classc': 'Continuity Auth Class C',
    'com.apple.private.alloy.continuity.encryption': 'Continuity Encryption',
    'com.apple.private.alloy.continuity.markup': 'Continuity Markup',
    'com.apple.private.alloy.continuity.sketch': 'Continuity Sketch',
    'com.apple.private.alloy.continuity.tethering': 'Continuity Tethering',
    'com.apple.private.alloy.continuity.unlock': 'Continuity Unlock',
    'com.apple.private.alloy.coreduet': 'CoreDuet',
    'com.apple.private.alloy.coreduet.sync': 'CoreDuet Sync',
    'com.apple.private.alloy.ct.baseband.p2p.notification': 'Baseband P2P Notifications',
    'com.apple.private.alloy.ct.commcenter.p2w.settings': 'Commcenter P2W Settings',
    'com.apple.private.alloy.ct.commcenter.sim': 'Commcenter SIM',
    'com.apple.private.alloy.ct.commcenter.sim.cloud': 'CommCenter SIM Cloud',
    'com.apple.private.alloy.ded': 'diagExtentionDaemon',
    'com.apple.private.alloy.ded.watch': 'Diagnostic Extension Watch',
    'com.apple.private.alloy.digitalhealth': 'DigitalHealth',
    'com.apple.private.alloy.donotdisturb': 'DoNotDisturb',
    'com.apple.private.alloy.electrictouch': 'ElectricTouch',
    'com.apple.private.alloy.eventkitmutation': 'EventKit Mutation',
    'com.apple.private.alloy.eventkitsync': 'EventKitSync',
    'com.apple.private.alloy.facetime.audio': 'FaceTime Audio',
    'com.apple.private.alloy.facetime.group': 'FaceTime Group Calls',
    'com.apple.private.alloy.facetime.lp': 'FaceTime LP',
    'com.apple.private.alloy.facetime.multi': 'FaceTime Multi',
    'com.apple.private.alloy.facetime.mw': 'FaceTime MW',
    'com.apple.private.alloy.facetime.video': 'FaceTime Video',
    'com.apple.private.alloy.family.activity': 'Family Activity Sharing',
    'com.apple.private.alloy.family.purchasesharing': 'Family Purchase Sharing',
    'com.apple.private.alloy.fetimesync': 'FeTimeSync',
    'com.apple.private.alloy.fignero': 'FigNero',
    'com.apple.private.alloy.findmydeviced.aoverc': 'Find My iPhone (A over C)',
    'com.apple.private.alloy.findmydeviced.watch': 'Find My iPhone',
    'com.apple.private.alloy.findmylocaldevice': 'Find My Local Device',
    'com.apple.private.alloy.fitness.sync': 'Activity Rings Sync',
    'com.apple.private.alloy.fitnessfriends.icloud': 'FitnessFriends iCloud',
    'com.apple.private.alloy.fitnessfriends.imessage': 'FitnessFriends iMessage',
    'com.apple.private.alloy.fmd': 'Find My Friends',
    'com.apple.private.alloy.fmf': 'FindMyFriends',
    'com.apple.private.alloy.fmflocator': 'FMF Locator',
    'com.apple.private.alloy.focus.sync': 'Focus Mode Sync',
    'com.apple.private.alloy.game.mode': 'Game Mode Sync',
    'com.apple.private.alloy.gamecenter': 'GameCenter',
    'com.apple.private.alloy.gamecenter.imessage': 'Gamecenter iMessage',
    'com.apple.private.alloy.gelato': 'Gelato',
    'com.apple.private.alloy.generative.media': 'Generative Media Sync',
    'com.apple.private.alloy.handover': 'Handoff',
    'com.apple.private.alloy.health.mental': 'Mental Health Sync',
    'com.apple.private.alloy.health.sharing.notifications': 'Health Sharing Notifications',
    'com.apple.private.alloy.health.sync.classa': 'HealthSync (Class A)',
    'com.apple.private.alloy.health.sync.classc': 'HealthSync (A over C)',
    'com.apple.private.alloy.health.sync.cloud': 'Health Cloud Sync',
    'com.apple.private.alloy.health.sync.device': 'Health Device-to-Device Sync',
    'com.apple.private.alloy.health.sync.notification': 'Health Sync Notification',
    'com.apple.private.alloy.health.sync.secure.backup': 'Health Secure Backup Sync',
    'com.apple.private.alloy.health.sync.sharing': 'Health Sharing Sync',
    'com.apple.private.alloy.health.sync.summary': 'Health Summary Sync',
    'com.apple.private.alloy.health.sync.urgent': 'Health Urgent Sync',
    'com.apple.private.alloy.home': 'HomeKit',
    'com.apple.private.alloy.icloudpairing': 'iCloudPairing',
    'com.apple.private.alloy.ids.cloudmessaging': 'IDS Cloud Messaging',
    'com.apple.private.alloy.idscentral': 'IDS Central Dispatch',
    'com.apple.private.alloy.idscredentials': 'IDSCredentials',
    'com.apple.private.alloy.idsremoteurlconnection': 'IDSRemoteURLConnection',
    'com.apple.private.alloy.idstransfers': 'IDS Transfers',
    'com.apple.private.alloy.intelligence.sync': 'Apple Intelligence Context',
    'com.apple.private.alloy.iosdiagnostics': 'iOS Diagnostics',
    'com.apple.private.alloy.iosdiagnostics.icloud': 'iosdiagnosticsicloud',
    'com.apple.private.alloy.iratmanager': 'iRatManager',
    'com.apple.private.alloy.itesterd.transferService.icloud': 'iTesterTransferServiceiCloud',
    'com.apple.private.alloy.itunes': 'iTunes',
    'com.apple.private.alloy.itunescloudd': 'itunescloudd',
    'com.apple.private.alloy.journal': 'Journal Sync',
    'com.apple.private.alloy.keychainsync': 'Keychain Sync',
    'com.apple.private.alloy.livability': 'Livability',
    'com.apple.private.alloy.live.activities': 'Live Activities Sync',
    'com.apple.private.alloy.location.auth': 'LocationAuth',
    'com.apple.private.alloy.location.motion': 'LocationMotion',
    'com.apple.private.alloy.location.stream': 'LocationStream',
    'com.apple.private.alloy.location.usage': 'LocationUsage',
    'com.apple.private.alloy.location.wifitilesync': 'LocationWiFiTileSync',
    'com.apple.private.alloy.logcabin': 'logcabin',
    'com.apple.private.alloy.mail.fetches': 'MailFetches',
    'com.apple.private.alloy.mail.sync.accounts': 'MailAccounts',
    'com.apple.private.alloy.mail.sync.content': 'MailContent',
    'com.apple.private.alloy.mail.sync.messages': 'MailMessages',
    'com.apple.private.alloy.mail.sync.protected': 'MailClassAProtected',
    'com.apple.private.alloy.mail.sync.protected.content': 'MailClassAProtectedContent',
    'com.apple.private.alloy.maps': 'Maps',
    'com.apple.private.alloy.maps.eta': 'SharedETA',
    'com.apple.private.alloy.maps.proxy': 'MapsProxy',
    'com.apple.private.alloy.maps.sync': 'MapsSync',
    'com.apple.private.alloy.mediaremote': 'MediaRemote',
    'com.apple.private.alloy.messagenotification': 'Message Notification',
    'com.apple.private.alloy.messages': 'Messages',
    'com.apple.private.alloy.messages.group': 'iMessage Group Management',
    'com.apple.private.alloy.messages.high-priority': 'High Priority Messages',
    'com.apple.private.alloy.messagesquickswitch': 'MessagesQuickSwitch',
    'com.apple.private.alloy.mobiletimersync': 'MobileTimerSync',
    'com.apple.private.alloy.multiplex1': 'Multiplex 1',
    'com.apple.private.alloy.music.playground': 'Playlist Playground',
    'com.apple.private.alloy.namedrop': 'NameDrop',
    'com.apple.private.alloy.nanoappmonitor': 'NanoAppMonitor',
    'com.apple.private.alloy.nanobackup': 'NanoBackup',
    'com.apple.private.alloy.nearby': 'Nearby',
    'com.apple.private.alloy.news': 'Nano News',
    'com.apple.private.alloy.notes': 'Notes Real-time Collab',
    'com.apple.private.alloy.nsurlsessionproxy': 'NSURLSession Proxy',
    'com.apple.private.alloy.octagon': 'Octagon',
    'com.apple.private.alloy.otaupdate': 'OTAUpdate',
    'com.apple.private.alloy.otaupdate.cloud': 'OTAUpdate Cloud',
    'com.apple.private.alloy.p2p.proximity': 'Proximity Handshake',
    'com.apple.private.alloy.pairedunlock': 'PairedUnlock',
    'com.apple.private.alloy.passbook.general': 'PassbookGeneral',
    'com.apple.private.alloy.passbook.maintenance': 'PassbookMaintenance',
    'com.apple.private.alloy.passbook.provisioning': 'PassbookProvisioning',
    'com.apple.private.alloy.passbook.relevancy': 'PassbookRelevancy',
    'com.apple.private.alloy.passbook.remoteadmin': 'PassbookRemoteAdmin',
    'com.apple.private.alloy.passbook.standalone.inapp': 'PassbookStandaloneInApp',
    'com.apple.private.alloy.passbook.standalone.provisioning': 'PassbookStandaloneProvisioning',
    'com.apple.private.alloy.passwords.sync': 'Passwords App Sync',
    'com.apple.private.alloy.pbbridge': 'Setup Bridge',
    'com.apple.private.alloy.pbbridge.connectivity': 'Bridge Connectivity',
    'com.apple.private.alloy.pcskey.sync': 'PCSKey Sync',
    'com.apple.private.alloy.phone.auth': 'PhoneAuth',
    'com.apple.private.alloy.phonecontinuity': 'Phone Continuity',
    'com.apple.private.alloy.photos.proxy': 'PhotosProxy',
    'com.apple.private.alloy.photostream': 'PhotoStream',
    'com.apple.private.alloy.podcasts': 'Podcasts',
    'com.apple.private.alloy.preferencessync': 'PreferencesSync',
    'com.apple.private.alloy.proactiveeventtracker': 'proactiveeventtracker',
    'com.apple.private.alloy.proxiedcrashcopier': 'ProxiedCrashCopier',
    'com.apple.private.alloy.proxiedcrashcopier.icloud': 'Proxied Crash Copier Cloud',
    'com.apple.private.alloy.pushproxy': 'PushProxy',
    'com.apple.private.alloy.quickboard.classa': 'QuickboardClassA',
    'com.apple.private.alloy.reality.sharing': 'Spatial Object Sharing',
    'com.apple.private.alloy.reminders': 'Reminders Sync',
    'com.apple.private.alloy.remotemediaservices': 'RemoteMediaServices',
    'com.apple.private.alloy.resourcegrabber': 'ResourceGrabber',
    'com.apple.private.alloy.safety.checkin': 'Check In (Safety)',
    'com.apple.private.alloy.safetymonitor.ownaccount': 'SafetyMonitor',
    'com.apple.private.alloy.safeview': 'Safeview',
    'com.apple.private.alloy.satellite.messaging': 'Satellite Messaging',
    'com.apple.private.alloy.screensharing': 'ScreenSharing',
    'com.apple.private.alloy.screensharing.v2': 'ScreenSharing v2 (SharePlay)',
    'com.apple.private.alloy.screenshotter': 'Screenshotter',
    'com.apple.private.alloy.screentimelocal': 'screentimelocal',
    'com.apple.private.alloy.sensorkit': 'Sensor Kit',
    'com.apple.private.alloy.sensorkitkeys': 'SensorKitKeys',
    'com.apple.private.alloy.sharing.handoff': 'Handoff / Universal Clipboard',
    'com.apple.private.alloy.sharing.paireddevice': 'Sharing Paired Device Info',
    'com.apple.private.alloy.sharing.v2': 'Sharing Service v2',
    'com.apple.private.alloy.sidecar': 'Sidecar / Universal Control',
    'com.apple.private.alloy.siri.device': 'SiriDevice',
    'com.apple.private.alloy.siri.icloud': 'Siri Cloud',
    'com.apple.private.alloy.siri.location': 'SiriLocation',
    'com.apple.private.alloy.siri.phrasespotter': 'SiriPhraseSpotter',
    'com.apple.private.alloy.siri.proxy': 'SiriProxy',
    'com.apple.private.alloy.siri.suggestions': 'Siri Intelligent Suggestions',
    'com.apple.private.alloy.siri.voiceshortcuts': 'Siri VoiceShortcuts',
    'com.apple.private.alloy.sms': 'SMSRelay',
    'com.apple.private.alloy.sms.watch': 'SMSWatch',
    'com.apple.private.alloy.sockpuppet': 'SockPuppet',
    'com.apple.private.alloy.sockpuppet.classd': 'SockPuppet Class D',
    'com.apple.private.alloy.status.keysharing': 'KeySharing',
    'com.apple.private.alloy.status.shareplay': 'SharePlay Status',
    'com.apple.private.alloy.sysdiagnose': 'Sysdiagnose',
    'com.apple.private.alloy.systemsettings': 'SystemSettings',
    'com.apple.private.alloy.tccd.msg': 'tccd messaging',
    'com.apple.private.alloy.tccd.sync': 'tccd sync',
    'com.apple.private.alloy.telephonyutilitiestemporary': 'TelephonyUtilities Temporary',
    'com.apple.private.alloy.terminus': 'NetworkRelay',
    'com.apple.private.alloy.thumper.keys': 'ThumperKeys',
    'com.apple.private.alloy.thumper.settings': 'ThumperSettings',
    'com.apple.private.alloy.timesync': 'TimeSync',
    'com.apple.private.alloy.timezonesync': 'TimeZoneSync',
    'com.apple.private.alloy.tincan.audio': 'Tincan Audio',
    'com.apple.private.alloy.tips': 'Tips',
    'com.apple.private.alloy.toolchestlite': 'Tool Chest Lite',
    'com.apple.private.alloy.vision.handover': 'Vision Pro Continuity',
    'com.apple.private.alloy.voicemailsync': 'VoiceMail Sync',
    'com.apple.private.alloy.wallet.passes': 'Wallet Passes Sync',
    'com.apple.private.alloy.wallet.provisioning': 'Wallet Provisioning',
    'com.apple.private.alloy.wallet.sharing': 'Wallet Card Sharing',
    'com.apple.private.alloy.wallet.transactions': 'Wallet Transactions Sync',
    'com.apple.private.alloy.watchconnectivity': 'Watch Connectivity',
    'com.apple.private.alloy.watchconnectivity.classd': 'Watch Connectivity Class D',
    'com.apple.private.alloy.watchconnectivity.v4': 'Watch Connectivity v4',
    'com.apple.private.alloy.webkitnetworking': 'WebKit Networking',
    'com.apple.private.alloy.wifi.networksync': 'WiFiManager_WiFiNetworkSync_IDS',
    'com.apple.private.alloy.willow': 'Willow',
    'com.apple.private.alloy.willow.proxy': 'Willow Proxy',
    'com.apple.private.alloy.willow.stream': 'Willow Stream',
    'com.apple.private.alloy.workout.sync': 'Workout Sync'
}


# Map to resolve IDStatus into human-readable device types
DEVICE_TYPE_MAP = {
    1: 'iDevice',
    2: 'Not iDevice'
}


def get_service_type_and_partner(value: str) -> tuple[str, str]:
    """
    Extracts the service type and partner from a complex string.
    Resolves known service labels to human-readable formats.
    """

    if value and ':' in value:
        # Split the string into service type and partner based on the first colon
        # e.g. tel:+390771XXXXX
        service_type, partner = value.split(':', 1)

        # Resolves the formatted service label or falls back to the original name
        return SERVICE_TYPE_MAP.get(service_type, service_type), partner

    return '', ''


def map_identifiers(context)-> dict[str, str]:
    """
    Maps identifiers by retrieving them from ServiceDefinitions files in the system root.
    """

    # Copy default map to avoid mutating the original constant
    map_ids = DEFAULT_MAP_IDS.copy()

    # /System/Library/IdentityServices/ServiceDefinitions/
    source_files = context.get_seeker().search(
        "*/System/Library/IdentityServices/ServiceDefinitions/*.plist"
    )

    for file_found in source_files:
        file_found = str(file_found)

        try:
            # Get the parsed plist content
            plist_data = get_plist_file_content(file_found)
            if not plist_data:
                continue

            # Extract attributes
            identifier = plist_data.get('Identifier')
            legacy_identifier = plist_data.get('LegacyIdentifier')
            display_name = plist_data.get('DisplayName')
            #service_name = plist_data.get('ServiceName')

            # Map current identifier if both exist
            if identifier and display_name:
                map_ids[identifier] = display_name

            # Map legacy identifier if both exist
            if legacy_identifier and display_name:
                map_ids[legacy_identifier] = display_name


        except (KeyError, TypeError, IndexError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Malformed structure in {file_found}: {ex}")
        except OSError as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Could not read {file_found}: {ex}")

    return map_ids


def _parse_identity_services(file_found, identifiers, context) -> list:
    """
    Parses the Identity Services status cache property list to extract lookup records.
    Supports both legacy and modern plist formats.
    """

    data_list = []

    try:
        # Get the parsed plist content
        plist_data = get_plist_file_content(file_found)
        if not plist_data:
            return data_list

        for key, value in plist_data.items():
            # Ensure the root element is a dictionary before iterating
            if not isinstance(value, dict):
                continue

            for cat_key, cat_value in value.items():
                try:
                    # Extract service type and partner (e.g., mailto:account@me.com)
                    service_type, partner = get_service_type_and_partner(cat_key)

                    # Convert timestamps to UTC
                    lookup_date = cat_value.get('LookupDate')
                    if lookup_date:
                        recently_searched = convert_cocoa_core_data_ts_to_utc(lookup_date)
                    else:
                        recently_searched = None

                    # Extract IDStatus and safely map it to a device type
                    status_id = cat_value.get('IDStatus')
                    if status_id is not None:
                        device_type = DEVICE_TYPE_MAP.get(status_id, f"N/D: {status_id}")
                    else:
                        device_type = None

                    # Resolve application display name
                    application = identifiers.get(key, key)

                    # Precise location within the plist structure for validation
                    location = f"[{key}][{cat_key}]"

                    # LAVA row
                    data_list.append((
                        recently_searched,
                        service_type, partner,
                        device_type,
                        application,
                        key,    # identifier
                        location
                    ))

                except (KeyError, TypeError, IndexError) as ex:
                    logfunc(f"[{context.get_artifact_name()}] "
                            f"Error - Processing record '{cat_key}' in {file_found}: {ex}")
                    continue

    except OSError as ex:
        logfunc(f"[{context.get_artifact_name()}] "
                f"Error - Could not read {file_found}: {ex}")
    except Exception as ex: # pylint: disable=broad-except
        logfunc(f"[{context.get_artifact_name()}] "
                f"Unexpected structural error in {file_found}: {ex}")

    return data_list


@artifact_processor
def idstatuscache(context):
    """
    Main entry point for the Identity Lookup Service artifact.
    """

    data_headers = (
        ('Recently searched', 'datetime'),
        'Service Type',
        'Partner',
        'Device Type',
        'Application',
        'Identifier',
        'Location'
    )

    data_list = []
    source_paths = []
    identifiers = {}

    files_found = context.get_files_found()
    if not files_found:
        return data_headers, data_list, ''

    # Map service definitions to enrich application names
    identifiers = map_identifiers(context)

    for file_found in files_found:
        file_found = str(file_found)

        # We attempt to parse any file found by the seeker
        current_list = _parse_identity_services(file_found, identifiers, context)

        if current_list:
            data_list.extend(current_list)
            source_paths.append(file_found)
        else:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Info - File {file_found} yielded no records "
                    "(it might be empty, corrupted, or a legacy residue).")

    return data_headers, data_list, "; ".join(source_paths)
