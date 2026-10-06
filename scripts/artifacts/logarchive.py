__artifacts_v2__ = {
    "logarchive": {
        "name": "logarchive",
        "description": "Processes Apple Unified Logs, either from tracev3 data in the "
                       "extraction, from a json file exported with 'log show', or from "
                       "an embedded sysdiagnose tarball",
        "author": "@AlexisBrignoni, @stark4n6",
        "creation_date": "2025-05-06",
        "last_update_date": "2026-10-05",
        "requirements": "Reading tracev3 data natively requires the unifiedlog_iterator "
                        "binary; see scripts/unifiedlogs.py",
        "category": "Unified Logs",
        "notes": "Sources are processed in priority order: 1) logarchive*.json, "
                 "2) extracted native db/diagnostics, 3) embedded sysdiagnose tar.gz files. "
                 "If native logs are present, sysdiagnose tarballs are ignored and the run log "
                 "says so. If several sysdiagnoses are present, each is extracted to its own "
                 "temporary folder in the report directory and read in turn, and the temporary "
                 "folders are deleted afterwards. Rows are not marked with the sysdiagnose they "
                 "came from, and Row Number starts again for each one. Whether the logs of two "
                 "sysdiagnoses from one device overlap was not measured, so the same entry can "
                 "appear more than once; the run log states how many entries were read from each.",
        # The tracev3 globs are anchored at db/, not private/var/db/: Cellebrite UFED
        # zips (and the corpus CSVs in admin/data/filepath-lists) store the data
        # partition as filesystem2/db/diagnostics with no private/var prefix, and the
        # anchored form never matched them. fnmatch's '*' crosses path separators, so
        # these cover the Apple-native layout too.
        "paths": ('*/logarchive*.json',
                  '*/db/diagnostics/*',
                  '*/db/uuidtext/*',
                  '*.logarchive/*',
                  '*/sysdiagnose_*.tar.gz'),
        "output_types": "lava_only",
        "artifact_icon": "database",
        "sample_data": {
            "abe_ios16": "31206006 rows",
            "ctf2020_ios12": "17985646 rows",
            "dexter_ios18": "16823810 rows",
            "felix23_ios16": "19419414 rows",
            "fsfull002_ios17": "30362747 rows",
            "hc_ios18_7": "726120 rows",
            "hc_ios26": "26.5.2 | 15146256 rows",
            "iphone12_ios18": "20491691 rows",
            "jess_ios15": "16558937 rows",
            "rodeo_ios17_sysdiag": "17.3 | 3647611 rows",
            "hickman_ios14_sysdiag": "14.3 | 6033460 rows",
        },
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
        "description": "Unified log entries containing 'Time change: Clock shifted by', "
                       "'Significant time change', TMSetManualTime or 'setting manual time'",
        "author": "@AlexisBrignoni",
        "creation_date": "2025-05-22",
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "2026-08-01: added entries containing 'Significant time change' (observed on iOS "
                 "18.7; what triggers them is not established here, and Apple documents a "
                 "notification of that name, UIApplication.significantTimeChangeNotification, as "
                 "also posted at midnight and on daylight saving changes, so a row is not by "
                 "itself a clock change) and the timed manual-time-setting entries "
                 "(TMSetManualTime / 'setting manual time'), which record a clock set by "
                 "hand on the device. Manual-time patterns documented at "
                 "https://www.ios-unifiedlogs.com/post/ios-unified-logs-don-t-trust-the-clock-timestamp.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "clock",
    },
    "logarchive_flashlight": {
        "name": "logarchive flashlight",
        "description": "Unified log entries tagged '[Flashlight Controller]' or AVFlashlight. "
                       "Which of these messages record the light turning on or off has not been "
                       "measured for this artifact",
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
        "description": "Unified log entries containing 'Allowing tap for icon view', 'Launching "
                       "application' or 'transition source:', and entries of the "
                       "com.apple.UserNotifications subsystem containing 'Launch application'; what "
                       "each form records is not sourced here",
        "author": "@AlexisBrignoni, @Hexordia",
        "creation_date": "2025-05-26",
        "last_update_date": "2026-10-06",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "'Launch application' is matched only in the com.apple.UserNotifications subsystem. "
                 "Those entries were on two of the five tested images: 7 rows on the iOS 12.4 image "
                 "and 8 on the iOS 26.5.2 image, logged by SpringBoard in the AppLaunching category. "
                 "9 of the 15 contain 'Launch application in foreground for notification response "
                 "action' and 6 contain 'Launch application in background for notification "
                 "response'; 3 of the iOS 26.5.2 rows hold <private> in place of the value that ends "
                 "the others. The other three images held no such entry, and the clause adds no row "
                 "that the three older terms already matched. Process Image Path was SpringBoard and "
                 "Process ID held one value on the rows of each tested image. The iOS 12.4 image "
                 "held only the UserNotifications entries, so Subsystem and Category each held "
                 "one value there. Trace ID held no value on any row of the tested images: rows "
                 "read from tracev3 data leave it empty.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "code",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 7 rows",
            "hc_ios17_2": "iOS 17.2.1 | 752 rows",
            "dexter_ios18": "iOS 18.3.2 | 95 rows",
            "iphone12_ios18": "iOS 18.7 | 1676 rows",
            "hc_ios26": "iOS 26.5.2 | 442 rows",
        },
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
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "2026-08-01: added the SpringBoard 'Toggle AirPlane Mode state' and the "
                 "Preferences/assistant 'Setting airplane mode enabled' forms, both "
                 "observed on iOS 18.7; the logging process distinguishes a Control "
                 "Center toggle from Settings or Siri "
                 "(https://www.ios-unifiedlogs.com/post/ios-unified-logs-wifi-and-airplane-mode). "
                 "The CoreTelephony 'isAirplaneMode' state reads described at "
                 "https://thesisfriday.com/thesis-friday-13-aul-detecting-airplane-mode-activation-in-ios-26-beta/ "
                 "are deliberately not collected: they are frequent state polls, not "
                 "toggle events.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "wifi-off",
    },
    "logarchive_lock_status": {
        "name": "logarchive lock status",
        "description": "Unified log entries about screen lock and unlock, screen power (ScreenOn "
                       "changed, Screen shut off) and the 'Biometric match' completion entries",
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
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "2026-08-01: added wifid WFMacRandomisation entries (per-network MAC "
                 "randomisation records, observed on iOS 18.7 and usable against router "
                 "logs) and 'manual association' entries, which the cited research "
                 "shows as wifid '__associate Manual Association Requestion from user' when a "
                 "network is joined from Settings "
                 "(https://www.ios-unifiedlogs.com/post/ios-unified-logs-wifi-and-airplane-mode). "
                 "Also added, observed on iOS 16.5/17.1: keychain password retrieval "
                 "(WiFiNetworkCopyPasswordWithTimeout), '{AUTOJOIN, ASSOC*} Attempting "
                 "auto join association of <SSID>' with the network name in the clear, "
                 "'Link went down', and per-network 'Total connection time' entries "
                 "(https://www.ios-unifiedlogs.com/post/ios-unified-logs-wifi-and-airplane-mode).",
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
        "description": "Unified log records whose subsystem begins with com.apple.Navigation, "
                       "compared without regard to case, so com.apple.navigation.VirtualGarage is "
                       "included",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2025-07-25",
        "last_update_date": "2026-08-25",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Rows logged under a subsystem beginning with com.apple.Navigation, collected by "
                 "subsystem rather than by message text. Across the six tested images the emitting "
                 "processes are the Maps widget extension GeneralMapsWidget (955 rows on four "
                 "images), navd (755 on five) and Maps.app (609 on two), with single-figure counts "
                 "from assistantd, routined and destinationd on one image each. Categories "
                 "observed on the iOS 16.5 through 18.7 images, with the number of images carrying "
                 "each: MNNavigationXPC, MNNavigationService, MNNavigationStateManager and "
                 "MNRouteStorage on four; MNLocationProvider on three; MNVoiceLanguageUtil, "
                 "MNUserOptionsEngine and Navd on two; MNRouteEditor, MNSuggestedNavigationMode, "
                 "MNRouteAttributes, MNSequence, MNCarPlayConnectionMonitor, "
                 "MNRingerSwitchObserver, ProcessHandling and the three VirtualGarage categories "
                 "on one each. The iOS 26.5.2 image shares only MNLocationProvider with those and "
                 "otherwise logs two categories seen nowhere else, "
                 "FamiliarRouteAuthorizationChecker and GEONavigationListener, which is why the "
                 "subsystem prefix is matched instead of a list of categories. Until 2026-08-25 "
                 "this artifact instead matched event_message against fifteen English spoken "
                 "guidance phrases such as 'Starting route to' and 'your destination'. None of "
                 "those phrases occurs in any of the 117,678,121 records across the six images "
                 "listed in sample_data, every one of them an en-US device, so it reported nothing "
                 "on all six. The rows are whatever was logged under that subsystem prefix; on the "
                 "tested images that is the categories listed above. What each category records is "
                 "not established here. It is not a record of a route being followed: on every "
                 "tested image that logs a navigation state, the only values seen are "
                 "MNNavigationStateTypeNoDestination, MNNavigationStateTypeNone and Stopped, so "
                 "none of them holds an active turn by turn session. Whether spoken guidance text "
                 "reaches the unified log at all is untested here, and 19.1 percent of messages on "
                 "the iOS 18.7 image are redacted to <private>. An image captured during live "
                 "navigation would settle it. Trace ID held no value on any row of the tested "
                 "images: rows read from tracev3 data leave it empty, and only a 'log show' JSON "
                 "export fills it.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 131 rows",
            "fsfull002_ios17": "iOS 17.1 | 924 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 0 rows; no com.apple.Navigation records in the sysdiagnose window",
            "dexter_ios18": "iOS 18.3.2 | 229 rows",
            "iphone12_ios18": "iOS 18.7 | 912 rows; the only tested image with MNRouteEditor, MNSuggestedNavigationMode or MNRouteAttributes",
            "hc_ios26": "iOS 26.5.2 | 128 rows; FamiliarRouteAuthorizationChecker and GEONavigationListener only",
        },
    },
    # The artifacts below come from the 2026-08-01 unified log predicate survey.
    # Every message pattern is either documented in a cited publication, observed
    # in an iOS 18.7 (22H20) full file system image, or both; the per-artifact
    # notes say which. Dynamic payloads in these messages are usually redacted to
    # <private> on production devices, so the static message text is the signal.
    "logarchive_calls": {
        "name": "logarchive call events",
        "description": "Unified log entries recording telephony activity: call tracking "
                       "start and end from callservicesd, Phone app open requests with the "
                       "originating process, Phone app tab changes, and keypad tone "
                       "requests (actionID 1200-1209 map to keypad digits 0-9)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Patterns documented by Lionel Notari "
                 "(https://www.ios-unifiedlogs.com/post/ios-unified-logs-making-a-call and "
                 "https://www.ios-unifiedlogs.com/post/watchos-unified-logs-introduction-and-calls) "
                 "and observed on iOS 18.7. The open-request entries name the process that "
                 "asked for the call UI (the Phone app or assistantd for Siri in the cited "
                 "research). Keypad tone "
                 "entries come from mediaserverd in the cited research and from audiomxd on "
                 "iOS 18.7. The number "
                 "payloads in these particular entries are redacted to <private>; the "
                 "dialed numbers artifact collects the CommCenter call.provider block that "
                 "carries the number in the clear.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "phone",
    },
    "logarchive_dialed_numbers": {
        "name": "logarchive dialed numbers",
        "description": "Unified log entries from CommCenter and the Phone app: the "
                       "call.provider setup block whose kPhoneNumber field holds a dialed "
                       "number, the teardown block carrying the same kUuid, the "
                       "Call(StatusUpdate) state chain, and MobilePhone "
                       "ContactSearchManager entries whose message text holds the contents "
                       "of the Phone app dial field",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Patterns documented by Tim Korver, 'Recovering a dialed number from the "
                 "Unified Log' "
                 "(https://thesisfriday.com/thesis-friday-24-recovering-a-dialed-number-from-the-unified-log/), "
                 "from six recordings on one iPhone 14 running iOS 26.6. Both families were "
                 "observed here, on different images. kPhoneNumber: on an iOS 26.5.2 full "
                 "file system image, three kActionType 0 blocks each carried a phone number "
                 "in the clear in E.164 form, and each was followed by a kActionType 2 "
                 "block with the same kUuid, matching the cited structure; kActionType "
                 "values 1 and 7 also appeared there and are reported as stored, since no "
                 "source read for this artifact defines them. Other call.provider entries "
                 "on that image render caller id as <private>, so the kPhoneNumber block is "
                 "where the value survived. ContactSearchManager: the entries on an iOS 18.7 image "
                 "include 'Searching for' and 'Search cancelled for' pairs whose digit strings "
                 "lengthen one step at a time up to a ten-digit "
                 "value, as the cited research describes. Four images were swept for both "
                 "families (iOS 16.5, 17.1, 18.7 and 26.5.2). Only the 26.5.2 one carried "
                 "any kActionType block and only the 18.7 one carried ContactSearchManager, "
                 "although call.provider activity was present on all four. That is a set of "
                 "single-image observations, not an established version range, and no "
                 "absence here is evidence the family is unavailable on that release. The "
                 "cited research reports a setup block with no matching "
                 "teardown as a dialed attempt, which does not establish that a call "
                 "connected, and reports ContactSearchManager firing for digits entered on "
                 "the device keypad but not for entry on a CarPlay screen; contact, Recents "
                 "and Siri dialing were not tested there. A bare 'Searching for' predicate "
                 "is deliberately not used: that text alone matched 808 unrelated records "
                 "on the iOS 26.5.2 image, so the category is matched instead.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "phone-outgoing",
    },
    "logarchive_typing": {
        "name": "logarchive keyboard activity",
        "description": "Unified log entries recording on-screen keyboard activity: "
                       "keyboard touch signposts logged per app (category "
                       "KeyboardSignposts) and keyboard sound requests for character "
                       "(actionID 1104), delete (1155) and modifier (1156) keys",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Signpost entries documented at "
                 "https://thesisfriday.com/thesis-friday-17-touch-events-on-the-ios-on-screen-keyboard/ "
                 "(the cited post labels the subsystem UIKitCore; the log lines it quotes show the "
                 "UIKitCore library writing under subsystem com.apple.TextInput, category "
                 "KeyboardSignposts, the same subsystem and category seen on iOS 18.7). "
                 "Sound-request actionID mapping documented at "
                 "https://www.ios-unifiedlogs.com/post/ios-unified-logs-typing-and-sending-a-message-in-whatsapp; "
                 "those entries name the client app. No typed text was seen in these entries on "
                 "the tested iOS 18.7 image. High volume: over 200k signpost rows "
                 "were observed in a single iOS 18.7 image, so this artifact is LAVA-only.",
        "paths": None,
        "output_types": "lava_only",
        "artifact_icon": "type",
    },
    "logarchive_faceid_presence": {
        "name": "logarchive biometric sensor events",
        "description": "Unified log entries from biometric sensor stacks: Face ID camera "
                       "frames with face-detected, attention and glasses flags "
                       "(PearlCamFrameReceived), face-to-device distance readings "
                       "(getFaceDetectInfo), SpringBoard face-in-view notices, and Touch ID "
                       "finger-on/finger-off events on home button devices",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Face ID entries documented at "
                 "https://thesisfriday.com/thesis-friday-1-aul-faceid/ and "
                 "https://thesisfriday.com/thesis-friday-12-aul-first-glance-at-ios-26/ "
                 "(iOS 18.2.1 and iOS 26 beta); both entry families were also observed on "
                 "iOS 18.7. Touch ID kAppleBiometricFingerOn/OffEvent kernel entries "
                 "documented at "
                 "https://thesisfriday.com/thesis-friday-10-artefacts-on-a-iphone-6-ios-12-5-7/ "
                 "(iOS 12.5.7) and observed on an iPhone 8 Plus running iOS 16.5; the "
                 "same source's home button press entries were not observed there and are "
                 "collected as documented-only. Sensor-level entries record what the "
                 "sensor saw, not an unlock decision; pair with the lock status "
                 "artifacts. High volume, LAVA-only.",
        "paths": None,
        "output_types": "lava_only",
        "artifact_icon": "eye",
    },
    "logarchive_pocket_state": {
        "name": "logarchive pocket state",
        "description": "Unified log entries recording front infrared sensor pocket-state "
                       "detection (Doppler in pocket state detected/cleared) and "
                       "SpringBoard PocketState changes",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Documented by Ian Whiffin (https://doubleblak.com/blogPost.php?k=doppler) "
                 "and Lionel Notari "
                 "(https://www.ios-unifiedlogs.com/post/ios-unified-logs-parsing-all-my-sql-queries); "
                 "observed on iOS 18.7. The entries record the pocket state the sensor reported, "
                 "detected or cleared; in Ian Whiffin's cited test the entries came in groups of "
                 "150 to 406, each lined up with a period when the screen lit while the front "
                 "infrared camera was covered.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "moon",
    },
    "logarchive_touch": {
        "name": "logarchive touchscreen events",
        "description": "Unified log entries recording physical screen contact: digitizer "
                       "contact presence transitions, per-app touch statistics windows "
                       "(touchstats), touch attention events, and tap-to-wake",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-10-03",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Documented at https://thesisfriday.com/thesis-friday-14-aul-touch-events/ "
                 "(iOS 18.5) and "
                 "https://www.ios-unifiedlogs.com/news/ios-unified-logs-touching-the-iphone-screen; "
                 "observed on iOS 18.7. Contact entries record finger presence on the "
                 "digitizer, not which control was touched. High volume, LAVA-only. "
                 "'Touch entered' (backboardd) was added 2026-10-03 from Tim Korver's 'Apple "
                 "Unified Log search term and process cheatsheet', which is cited as noting that "
                 "the rectangle in it is the screen size, not the finger's position. The address "
                 "recorded for the cheatsheet, thesisfriday.com/alr, did not serve it when fetched "
                 "on 2026-10-03, so that statement could not be checked. The entry was observed on "
                 "the iOS 26.5.2 image. "
                 "Trace ID held no value on any row of the tested images: rows read from tracev3 data leave it empty, and only a 'log show' JSON export fills it.",
        "paths": None,
        "output_types": "lava_only",
        "artifact_icon": "target",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 8193 rows",
            "dexter_ios18": "iOS 18.3.2 | 4801 rows",
            "iphone12_ios18": "iOS 18.7 | 23978 rows",
            "hc_ios26": "iOS 26.5.2 | 6933 rows",
        },
    },
    "logarchive_usb_connections": {
        "name": "logarchive USB and power connections",
        "description": "Unified log entries recording external power and USB cable "
                       "attach/detach: powerexperienced plugin state changes, kernel "
                       "IOAccessoryUSBConnectShim cable-detect events, and the kernel "
                       "VBUS power and CON_DET physical-connection states",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-08-29",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Documented at "
                 "https://thesisfriday.com/thesis-friday-9-aul-connecting-a-usb-cable/ and "
                 "https://thesisfriday.com/thesis-friday-20-project-stark-forensic-reconstruction-of-the-carplay-handshake/; "
                 "observed on iOS 18.7, where the shim also emits an 'AppleUSBCableDetect 1' "
                 "form. The 'USB Power (VBUS) Present' pattern was added 2026-08-02 as "
                 "a precaution, not as a fix: the cited CarPlay research, revised for iOS 26.6, "
                 "quotes that line without the shim prefix and treats it as the most consistent "
                 "connection marker, with 'Present: 0' treated as the detach signal while CON_DET "
                 "can remain 1. On the iOS 18.7 and iOS 17.1 images checked when the pattern was "
                 "added, the VBUS lines carried the shim prefix and were already collected, so the "
                 "pattern added no rows on those versions; it is kept for a release that drops the "
                 "prefix. The counts from that check are not recorded in sample_data. These "
                 "entries record cable presence, not what was connected; "
                 "examiner acquisition also produces them.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "zap",
    },
    "logarchive_camera": {
        "name": "logarchive camera capture",
        "description": "Unified log entries from the Camera app and photo pipeline "
                       "recording capture mode changes, moment capture begin/commit, "
                       "still image capture, and assets being added to the photo library",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Patterns documented by Lionel Notari "
                 "(https://www.ios-unifiedlogs.com/post/ios-unified-logs-parsing-all-my-sql-queries); "
                 "the full chain (mode change, capture, asset added) was observed on "
                 "iOS 18.7. Asset filenames (IMG_ names) appear in assetsd entries when "
                 "not redacted.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "camera",
    },
    "logarchive_notifications": {
        "name": "logarchive notification interactions",
        "description": "Unified log entries about notifications: "
                       "removal of notification requests, group expansion, cell default "
                       "actions (tap-through), long-look presentation, and reply actions",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Patterns documented by Lionel Notari "
                 "(https://www.ios-unifiedlogs.com/post/ios-unified-logs-parsing-all-my-sql-queries). "
                 "Removal entries were observed on iOS 18.7; the tap-through, expansion and "
                 "reply patterns are from the cited research and did not occur in the "
                 "validation image's log window. No notification text was seen in the removal "
                 "entries on the tested iOS 18.7 image; the other forms were not observed.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "bell",
    },
    "logarchive_app_focus": {
        "name": "logarchive app focus and lifecycle",
        "description": "Unified log entries recording which app held focus and lifecycle "
                       "transitions: contextstored inFocus values, SpringBoard app "
                       "bootstrap with launch intent, scene lifecycle changes, icon taps, "
                       "and terminations from the app switcher",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Patterns documented by Lionel Notari "
                 "(https://www.ios-unifiedlogs.com/post/ios-unified-logs-unlock and "
                 "https://www.ios-unifiedlogs.com/post/ios-unified-logs-parsing-all-my-sql-queries); "
                 "observed on iOS 18.7. 'Bootstrapping ... with intent "
                 "foreground-interactive' entries are collected in both the 'Bootstrapping "
                 "application<bundle>' and 'Bootstrapping app<bundle>' forms. An empty inFocus "
                 "value is reported as stored. Complements the logarchive executed apps artifact.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "layers",
    },
    "logarchive_media_playback": {
        "name": "logarchive media playback",
        "description": "Unified log entries in the MediaRemote category recording "
                       "now-playing state: originating app bundle id, playback state "
                       "changes, and route information",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Category documented by Sarah Edwards "
                 "(https://www.mac4n6.com/blog/2020/5/22/analysis-of-apple-unified-logs-quarantine-edition-entry-9-we-all-know-youre-binging-netflix-now-playing-on-your-apple-devices); "
                 "observed on iOS 18.7. The cited research reports media duration, elapsed "
                 "time, playback rate and AirPlay target names in these entries.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "play-circle",
    },
    "logarchive_sim_cellular": {
        "name": "logarchive SIM and cellular state",
        "description": "Unified log entries recording SIM slot status "
                       "(kCTSIMSupportSIMStatus values), cellular data network type "
                       "changes, and itunestored network type observations",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Patterns documented by Lionel Notari "
                 "(https://www.ios-unifiedlogs.com/post/ios-unified-logs-wifi-and-airplane-mode); "
                 "observed on iOS 18.7, including kCTSIMSupportSIMStatusNotInserted from "
                 "the Preferences SIMCache. SIM status entries record slot state at "
                 "logging time, not the moment a card was inserted or removed.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "radio",
    },
    "logarchive_unlock_auth": {
        "name": "logarchive unlock sessions and method",
        "description": "Unified log entries recording lock/unlock session durations (apsd 'Was locked/unlocked "
                       "for N seconds'), authentication requests with type and outcome, keybag state "
                       "transitions, the kernel's APFS volume unlock entries and volume lock and unlock "
                       "notifications, and locks from the side button",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-10-03",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Patterns documented by Lionel Notari "
                 "(https://www.ios-unifiedlogs.com/post/ios-unified-logs-unlock) and "
                 "https://thesisfriday.com/thesis-friday-12-aul-first-glance-at-ios-26/; observed on iOS "
                 "18.7. In 'Processed authentication request' entries the cited research maps type 1 to "
                 "passcode and type 2 to biometric. The same research shows success=YES with type 1 also "
                 "recorded when a wrong passcode was entered, and gives the following 'Unlock attempt "
                 "succeeded: yes' or 'no' entry as the outcome. That entry did not appear on the iOS "
                 "12.4, 17.2.1, 18.3.2, 18.7 or 26.5.2 images, so on them the success flag alone does "
                 "not establish that an unlock succeeded. Every 'Transition:' entry of the "
                 "com.apple.chrono keybag category is selected, with any other entry containing "
                 "'Transition: locked ->' (remindd writes one). Several processes write one transition "
                 "(chronod, duetexpertd, SpringBoard and WidgetRenderer_Default on the iOS 18.3.2 "
                 "image), so the rows are not a count of unlocks; the cited research reads the target "
                 "state inBioUnlock as a biometric unlock. Tim Korver's 'Backward reasoning from a "
                 "provable endpoint' "
                 "(https://thesisfriday.com/thesis-friday-27-backward-reasoning-from-a-provable-endpoint/, "
                 "measured on macOS 26.6.2) reports that two processes writing the same transition are "
                 "one message relayed and not two observations, and that a session unlocked "
                 "biometrically stays in the biometric state until it locks. Transition entries by "
                 "image: none on iOS 12.4; 52 on iOS 17.2.1 in 10 forms; 314 on iOS 18.3.2 in 10 forms; "
                 "252 on iOS 18.7 in 9 forms; 183 on iOS 26.5.2 in 7 forms. A form naming inBioUnlock "
                 "appeared on the iOS 17.2.1 and iOS 18.3.2 images only. The kernel 'is now UN-locked' "
                 "entry, named as the unlock endpoint in Tim Korver's 'Apple Unified Log search term and "
                 "process cheatsheet', was added 2026-10-03: it appeared on all five tested images "
                 "(28, 54, 58, 18 and 26 entries), including iOS 12.4 and 17.2.1, where 'apfs is "
                 "being UN-locked' did not appear. The cheatsheet is cited as reporting two such "
                 "entries per unlock on iOS. The address recorded for the cheatsheet, "
                 "thesisfriday.com/alr, did not serve it when fetched on 2026-10-03, so the "
                 "statements attributed to it in these notes could not be checked. The kernel "
                 "'Sending notification for volume' entry carries "
                 "the state as written (unlocked, locked or cx expired; the last is reported as stored). "
                 "Tim Korver's 'What a busy phone forgets' "
                 "(https://thesisfriday.com/thesis-friday-28-what-a-busy-phone-forgets/, measured on iOS "
                 "26.6.2) counts it with the kernel lines of an unlock. By image: none on iOS 12.4; 71 "
                 "on iOS 17.2.1 (54 unlocked, 15 locked, 2 cx expired); 122 on iOS 18.3.2 (58 unlocked, "
                 "56 locked, 8 cx expired); 36 on iOS 18.7 (18 unlocked, 16 locked, 2 cx expired); 56 on "
                 "iOS 26.5.2 (26 unlocked, 24 locked, 6 cx expired). Its unlocked count equalled the 'is "
                 "now UN-locked' count on each of the four images that had it (54, 58, 18, 26). An "
                 "absent entry is not evidence that no unlock happened: that post measured the kernel "
                 "lines of an unlock gone from a phone in daily use within 13.2 hours, and retention was "
                 "not measured on the tested images. An acquisition can add to these entries: 'The stop "
                 "rule' (https://thesisfriday.com/the-stop-rule/) counted 158 kernel keybag unlock lines "
                 "and 370 keybag transition lines in a 67-minute period in which the phone was being "
                 "acquired and he had not unlocked it as part of his reference session. Complements the "
                 "logarchive lock status artifact with durations and method. Trace ID held no value on "
                 "any row of the tested images: rows read from tracev3 data leave it empty, and only a "
                 "'log show' JSON export fills it.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "unlock",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 111 rows",
            "hc_ios17_2": "iOS 17.2.1 | 217 rows",
            "dexter_ios18": "iOS 18.3.2 | 589 rows",
            "iphone12_ios18": "iOS 18.7 | 384 rows",
            "hc_ios26": "iOS 26.5.2 | 357 rows",
        },
    },
    "logarchive_dictation": {
        "name": "logarchive dictation",
        "description": "Unified log entries recording keyboard dictation sessions: "
                       "dictation start with language code, begin/end feedback events, "
                       "and assistantd dictation-type audio record preparation",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Documented at "
                 "https://www.ios-unifiedlogs.com/post/ios-unified-logs-the-use-of-the-dictaphone; "
                 "observed on iOS 18.7. The CSAudioRecordTypeDictation entries are the "
                 "assistantd audio record preparations carrying the dictation record type. "
                 "Whether dictated text appears in these entries was not measured for this "
                 "artifact.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "mic",
    },
    "logarchive_audio_routes": {
        "name": "logarchive audio routes",
        "description": "Unified log entries from the audio server recording output route "
                       "configuration and changes (receiver, speaker, or a Bluetooth "
                       "device) for calls and other audio sessions",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Documented at "
                 "https://www.ios-unifiedlogs.com/news/ios-unified-logs-calls-and-audio-output; "
                 "observed on iOS 18.7 from audiomxd. The cited research shows Bluetooth "
                 "routes carrying the accessory MAC address in the route state.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "volume-2",
    },
    "logarchive_battery_state": {
        "name": "logarchive battery state",
        "description": "Unified log entries recording battery charge level changes posted "
                       "by powerd and battery info updates from PowerUIAgent",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Patterns documented by Lionel Notari "
                 "(https://www.ios-unifiedlogs.com/post/ios-unified-logs-parsing-all-my-sql-queries); "
                 "observed on iOS 18.7. Complements the charger-connected entries in the "
                 "logarchive artifacts filter with a charge-level timeline.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "battery-charging",
    },
    "logarchive_ui_navigation": {
        "name": "logarchive interface navigation",
        "description": "Unified log entries recording interface navigation between apps: "
                       "Control Center launch and visibility, Today view overlay "
                       "appearance, widget visibility changes, and home screen page "
                       "scrolling",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Patterns documented by Lionel Notari "
                 "(https://www.ios-unifiedlogs.com/post/ios-unified-logs-parsing-all-my-sql-queries); "
                 "observed on iOS 18.7. These entries record interface transitions between app "
                 "launches.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "grid",
    },
    # The artifacts below extend the 2026-08-01 survey with patterns that did not
    # occur on the first validation image and were confirmed against two more:
    # an iPhone 8 Plus on iOS 16.5 (CTF device with staged usage) and an
    # iPhone 11 Pro on iOS 17.1.
    "logarchive_driving": {
        "name": "logarchive driving state",
        "description": "Unified log entries recording vehicular motion classification: "
                       "wifid CMMotionActivity driving start/stop, locationd vehicular "
                       "episode markers, Driving Focus engagement, and the "
                       "pedestrian-after-driving motion alarm",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Documented at https://www.ios-unifiedlogs.com/post/ios-unified-logs-driving; "
                 "observed on iOS 16.5 and 17.1. The cited research cautions that these "
                 "entries do not distinguish driver from passenger and that their absence "
                 "shows nothing. "
                 "Complements the motion state transitions artifact.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "truck",
    },
    "logarchive_bluetooth_pairing": {
        "name": "logarchive bluetooth pairing",
        "description": "Unified log entries recording device discovery and pairing: "
                       "bluetoothd CBDevice discovery records carrying accessory name, "
                       "Bluetooth address and product identifiers, plus pairing session "
                       "lifecycle entries",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Pairing sequence documented at "
                 "https://www.ios-unifiedlogs.com/news/bluetooth-pairing. 'Device found: "
                 "CBDevice' records (with accessory names and addresses in the clear) and "
                 "rapportd 'Pairing completed' entries were observed on iOS 16.5/17.1; the "
                 "cited bluetoothd forms for pairing start, numeric comparison and SDP are "
                 "collected as documented-only since no new pairing occurred in the "
                 "validation images' log windows. Complements the bluetooth status "
                 "artifact, which covers connect/disconnect of known devices.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "bluetooth",
    },
    "logarchive_emergency_sos": {
        "name": "logarchive emergency SOS engine",
        "description": "Unified log entries containing 'broadcasting SOSStatus', "
                       "'flowStartedOnEitherDevice' or 'sosTriggeredOnPairedDevice', matched in "
                       "any process",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Documented at "
                 "https://thesisfriday.com/thesis-friday-19-emergency-sos-decoding-the-cross-device-help-handshake/. "
                 "Status broadcasts and flow entries were observed on iOS 16.5 and 17.1 "
                 "on devices with no known SOS use, so their presence alone does not "
                 "show an SOS call; the payloads are redacted to <private>. The "
                 "sosTriggeredOnPairedDevice entry (documented from a paired Apple Watch "
                 "trigger) is collected as documented-only. Complements the SOS claw "
                 "gesture entries in the logarchive artifacts filter.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "alert-triangle",
    },
    "logarchive_power_events": {
        "name": "logarchive power events",
        "description": "Unified log entries marking device boot and shutdown: the kernel "
                       "iBoot version line logged at startup, the SpringBoard "
                       "orientation-deferral shutdown notice, and locationd shutting down",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Documented at https://www.ios-unifiedlogs.com/post/ios-unified-logs-unlock "
                 "and "
                 "https://www.ios-unifiedlogs.com/post/ios-unified-logs-parsing-all-my-sql-queries. "
                 "The SQL queries post scopes the iBoot line to the kernel process, the shutdown "
                 "notice to SpringBoard and the 'locationd shutting down' line to locationd; this "
                 "artifact matches the text in any process. All three entry families were "
                 "observed on iOS 16.5 and 17.1. The iBoot line marks a boot; the "
                 "SpringBoard and locationd lines mark orderly shutdowns. Pair with the "
                 "Sysdiagnose shutdown.log artifacts, which record reboot times and the "
                 "processes delaying them.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "power",
    },
    "logarchive_airdrop": {
        "name": "logarchive AirDrop",
        "description": "Unified log entries matching AirDrop and share sheet message text: the "
                       "device's AirDrop ID, discoverability "
                       "scanning mode (Everyone/Contacts Only/Off), SharingDaemon state "
                       "dumps, share sheet activation, and transfer entries",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Documented by Sarah Edwards "
                 "(https://www.mac4n6.com/blog/2020/6/5/analysis-of-apple-unified-logs-quarantine-edition-entry-11-airdropping-some-knowledge). "
                 "'Current AirDrop ID is ...' (identifier in the clear), 'Scanning mode "
                 "Contacts Only' and SharingDaemon state dumps were observed on iOS 17.1, "
                 "and share sheet activation with 'startSending' on iOS 18.7. The "
                 "incoming-transfer and accept/decline entries are collected as "
                 "documented-only; no transfer occurred in the validation images' log "
                 "windows. The cited research reports that the AirDrop ID is not constant for the "
                 "life of the device and changes often; how long one ID stays in use is not "
                 "established here.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "share",
    },
    "logarchive_carplay_session": {
        "name": "logarchive CarPlay session",
        "description": "Unified log entries recording the CarPlay connection sequence: "
                       "the airplayd USB DirectLink notice that marks a wired session, "
                       "CarKit session authentication and activation states, CarPlayApp "
                       "vehicle identifier entries, and the wifid CarPlay session vehicle "
                       "record carrying the reported model and manufacturer",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-02",
        "last_update_date": "2026-08-02",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "NOT YET VALIDATED IN-HOUSE. Every pattern here except 'CarPlay Connection Event' "
                 "comes from Tim Korver's "
                 "CarPlay handshake research "
                 "(https://thesisfriday.com/thesis-friday-20-project-stark-forensic-reconstruction-of-the-carplay-handshake/), "
                 "which documents the sequence on iOS 26.6 (build 23G71, iPhone 14) after "
                 "an earlier iOS 18 revision. None of it has been observed in our own test "
                 "images, because none of them contain a CarPlay session. Sweeping the full "
                 "marker set across complete iOS 17.1 and 18.7 extractions on 2026-08-02 "
                 "returned zero for every pattern here, as did an earlier DirectLink and "
                 "vehicle identifier sweep of an iOS 16.5 extraction; matches on "
                 "'com.apple.carkit' and 'CarPlayApp' in those images are subsystem and "
                 "process mentions in unrelated entries, not session markers. Treat output "
                 "as unconfirmed until seen on a device known to have used CarPlay. Caveats "
                 "from the source: the vehicle identifier is "
                 "assigned by the device rather than read from the car, so it needs the "
                 "surrounding session to attribute it to a vehicle; the CarKit session "
                 "entries appear roughly a thousand times per session and carry their "
                 "meaning in the isAuthenticated and isActivated values rather than the "
                 "message; the FrontBoard bootstrap line appeared in only one of three "
                 "runs and its absence shows nothing; the research covered one vehicle over "
                 "wired USB, with first-time pairing and wireless sessions untested. The "
                 "'Stark' subsystem the feature was built on no longer exists as of iOS "
                 "26.6. Pair with the USB and power connections artifact, whose VBUS "
                 "entries bracket a wired session.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "truck",
    },
    "logarchive_biometric_match": {
        "name": "logarchive biometric match results",
        "description": "Unified log entries recording the result of a Face ID or Touch ID match: the "
                       "kernel matchResultHandler entries, coreauthd no-match entries, and the "
                       "documented SpringBoard biometric unlock events",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-03",
        "last_update_date": "2026-10-03",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Search terms from Tim Korver, 'Apple Unified Log search term and process "
                 "cheatsheet', recorded as measured on iOS 12.5.7, 18.2.1, 26.0 and 26.6.1. The "
                 "address recorded for it, thesisfriday.com/alr, did not serve the cheatsheet when "
                 "fetched on 2026-10-03, so the statements attributed to it in these notes could "
                 "not be checked. It is cited as describing the matchResultHandler entry as "
                 "carrying the user ID and enrollment UUID and 'MATCH -1' as firing on a wrong "
                 "passcode and on a failed Face ID, with the surrounding entries deciding which. "
                 "Other MATCH values were not tested against known data here and are reported as "
                 "stored. Kernel matchResultHandler entries were present on the iOS 12.4 (43), iOS "
                 "17.2.1 (11) and iOS 18.3.2 (50) images and "
                 "absent on the iOS 18.7 and iOS 26.5.2 images. coreauthd 'has received no-match' "
                 "appeared once, on iOS 17.2.1. 'Base unlock behavior received biometric event' is "
                 "documented by Lionel Notari "
                 "(https://www.ios-unifiedlogs.com/post/ios-unified-logs-unlock) and "
                 "'matchResult:timestamp:' is the macOS form named in the cheatsheet; neither "
                 "appeared in the tested iOS images. An entry records a match attempt by the "
                 "sensor stack, not who was in front of it. "
                 "A match entry is not an unlock: Tim Korver's 'Backward reasoning from a provable "
                 "endpoint' "
                 "(https://thesisfriday.com/thesis-friday-27-backward-reasoning-from-a-provable-endpoint/, "
                 "measured on macOS 26.6.2) recorded successful Touch ID matches with the machine "
                 "already unlocked and no change of state; that was not tested on iOS here. An entry "
                 "absent from an image is not established to be a property of its iOS version: Tim "
                 "Korver's 'What a busy phone forgets' "
                 "(https://thesisfriday.com/thesis-friday-28-what-a-busy-phone-forgets/) measured the "
                 "kernel lines of an unlock gone from a phone in daily use within 13.2 hours, and "
                 "retention was not measured on the tested images. "
                 "Trace ID held no value on any row of the tested images: rows read from tracev3 data leave it empty, and only a 'log show' JSON export fills it.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "user-check",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 43 rows",
            "hc_ios17_2": "iOS 17.2.1 | 12 rows",
            "dexter_ios18": "iOS 18.3.2 | 50 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
    "logarchive_passcode_field": {
        "name": "logarchive passcode field input",
        "description": "Unified log entries recording the passcode text field (SBUIPasscodeTextField) "
                       "becoming and ceasing to be the keyboard input target, with the process that "
                       "showed it",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-03",
        "last_update_date": "2026-10-03",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Search term from Tim Korver, 'Apple Unified Log search term and process "
                 "cheatsheet', recorded as measured on iOS 12.5.7, 18.2.1, 26.0 and 26.6.1. The "
                 "address recorded for it, thesisfriday.com/alr, did not serve the cheatsheet when "
                 "fetched on 2026-10-03, so the statements attributed to it in these notes could "
                 "not be checked. It is cited as describing these entries as showing that the "
                 "passcode field was on screen; they do not "
                 "record the digits or whether the code was correct. The process column separates the "
                 "lock screen (SpringBoard) from passcode prompts shown for another authentication "
                 "(CoreAuthUI on iOS 17.2.1 and 18.7, LocalAuthenticationUIService on iOS 26.5.2). Rows "
                 "by image: iOS 17.2.1 44 (24 CoreAuthUI), iOS 18.3.2 6, iOS 18.7 450 (424 CoreAuthUI), "
                 "iOS 26.5.2 34 (8 LocalAuthenticationUIService); none on iOS 12.4. "
                 "'forSetDelegate:<SBUIPasscodeTextField' is written when the field becomes the input "
                 "target and '_teardownExistingDelegate:<SBUIPasscodeTextField' when it stops being one; "
                 "the two forms appeared in equal numbers on every tested image that had either. An "
                 "entry absent from an image is not established to be a property of its iOS version: Tim "
                 "Korver's 'What a busy phone forgets' "
                 "(https://thesisfriday.com/thesis-friday-28-what-a-busy-phone-forgets/) measured the "
                 "kernel lines of an unlock gone from a phone in daily use within 13.2 hours, and "
                 "retention was not measured on the tested images. Trace ID held no value on any row of "
                 "the tested images: rows read from tracev3 data leave it empty, and only a 'log show' "
                 "JSON export fills it.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "lock",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 44 rows",
            "dexter_ios18": "iOS 18.3.2 | 6 rows",
            "iphone12_ios18": "iOS 18.7 | 450 rows",
            "hc_ios26": "iOS 26.5.2 | 34 rows",
        },
    },
    "logarchive_hardware_buttons": {
        "name": "logarchive hardware button presses",
        "description": "Unified log entries recording physical button presses: backboardd button events "
                       "with the button's HID usage and how long it was held, SpringBoard side button "
                       "press counts and single press recognition, and the SpringBoard button "
                       "combination recognizer's press type",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-03",
        "last_update_date": "2026-10-03",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Search terms from Tim Korver, 'Apple Unified Log search term and process "
                 "cheatsheet', recorded as measured on iOS 12.5.7, 18.2.1, 26.0 and 26.6.1. The "
                 "address recorded for it, thesisfriday.com/alr, did not serve the cheatsheet when "
                 "fetched on 2026-10-03, so the statements attributed to it in these notes could "
                 "not be checked. backboardd writes one 'began:' and one 'finished:' entry per "
                 "press; the cheatsheet reads the time since firstDown in the 'finished:' entry as "
                 "how long the button was held. The usage pair at the start of the entry is a USB "
                 "HID Consumer Page usage: 0xC/0x30 Power, 0xC/0xE9 Volume Increment, 0xC/0xEA "
                 "Volume Decrement (USB-IF HID Usage Tables 1.5, section 15). The cheatsheet maps "
                 "the combination recognizer's press type 102 to volume up, 103 to volume down and "
                 "104 to the side button; on the iOS 18.7 image the three press types appeared 80, "
                 "26 and 66 times against 41, 13 and 33 presses of the matching backboardd usage. "
                 "'press count:' is the side "
                 "button's press count per the cheatsheet (1 single, 2 a second press shortly "
                 "after), and it matched the 0xC/0x30 press count on the iOS 17.2.1 (22), 18.7 "
                 "(33) and 26.5.2 (24) images but not on iOS 18.3.2 (2 against 15). The iOS 12.4 "
                 "image held only 'Lock button single press recognized' (9). Volume presses are "
                 "also reported by the audio status artifact; button presses can come from an "
                 "examiner handling the device. Trace ID held no value on any row of the tested "
                 "images: rows read from tracev3 data leave it empty, and only a 'log show' JSON "
                 "export fills it.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 9 rows",
            "hc_ios17_2": "iOS 17.2.1 | 188 rows",
            "dexter_ios18": "iOS 18.3.2 | 40 rows",
            "iphone12_ios18": "iOS 18.7 | 406 rows",
            "hc_ios26": "iOS 26.5.2 | 175 rows",
        },
    },
    "logarchive_orientation": {
        "name": "logarchive device orientation and pick-up",
        "description": "Unified log entries recording device orientation changes (Received orientation), "
                       "wake gesture notifications such as a pick-up (Gesture notification) and the "
                       "kernel's [TTW] orientation changes",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-03",
        "last_update_date": "2026-10-03",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Search terms from Tim Korver, 'Apple Unified Log search term and process "
                 "cheatsheet', recorded as measured on iOS 12.5.7, 18.2.1, 26.0 and 26.6.1. The "
                 "address recorded for it, thesisfriday.com/alr, did not serve the cheatsheet when "
                 "fetched on 2026-10-03, so the statements attributed to it in these notes could "
                 "not be checked. Orientation entries are documented at "
                 "https://thesisfriday.com/thesis-friday-2-aul-device-orientation/. The cheatsheet "
                 "notes that several processes write the same orientation and gesture entry for "
                 "one event, so a count of rows is not a count of events, and that the end state "
                 "is reliable while the start state is not. On the tested images gesture "
                 "notifications came from SpringBoard, biometrickitd and audiomxd (assistantd in "
                 "place of audiomxd on iOS 12.4), and orientation entries from backboardd and "
                 "biometrickitd with others such as audiomxd and callservicesd; on iOS 26.5.2 app "
                 "processes including Camera and MobileSMS also logged them. Gesture notification "
                 "values seen in the tested images: 1(Detected), "
                 "2(Dismissed), 4(PreDetection) and, on iOS 18.3.2, 7(Suppressed); the cheatsheet "
                 "reads 'Gesture notification: 1(Detected)' as the device being picked up. The "
                 "[TTW] kernel entries carry only a code and a microsecond counter and appeared on "
                 "iOS 17.2.1, 18.7 and 26.5.2. High volume, LAVA-only. "
                 "Trace ID held no value on any row of the tested images: rows read from tracev3 data leave it empty, and only a 'log show' JSON export fills it.",
        "paths": None,
        "output_types": "lava_only",
        "artifact_icon": "rotate-cw",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1236 rows",
            "hc_ios17_2": "iOS 17.2.1 | 3740 rows",
            "dexter_ios18": "iOS 18.3.2 | 827 rows",
            "iphone12_ios18": "iOS 18.7 | 5414 rows",
            "hc_ios26": "iOS 26.5.2 | 1034 rows",
        },
    },
    "logarchive_system_gestures": {
        "name": "logarchive system edge gestures",
        "description": "Unified log entries recording touches taken over by a system gesture "
                       "(backboardd) and SpringBoard edge gesture recognizers for the app switcher, "
                       "Control Center and the Cover Sheet",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-03",
        "last_update_date": "2026-10-03",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Search terms from Tim Korver, 'Apple Unified Log search term and process "
                 "cheatsheet', recorded as measured on iOS 12.5.7, 18.2.1, 26.0 and 26.6.1. The "
                 "address recorded for it, thesisfriday.com/alr, did not serve the cheatsheet when "
                 "fetched on 2026-10-03, so the statements attributed to it in these notes could "
                 "not be checked. It is cited as noting that a single 'system gesture stealing the "
                 "touches' entry is an edge touch while a real swipe writes nine to twenty-three. "
                 "The SpringBoard entries name the recognizer: DeckGrabberTongue (app switcher), "
                 "ControlCenterGrabberTongue, CoverSheetGrabberTongue and "
                 "SBCoverSheetSystemGesturesDelegate. The entries record that a gesture recognizer "
                 "began, not that the "
                 "gesture completed. "
                 "Trace ID held no value on any row of the tested images: rows read from tracev3 data leave it empty, and only a 'log show' JSON export fills it.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "move",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 269 rows",
            "hc_ios17_2": "iOS 17.2.1 | 431 rows",
            "dexter_ios18": "iOS 18.3.2 | 90 rows",
            "iphone12_ios18": "iOS 18.7 | 1195 rows",
            "hc_ios26": "iOS 26.5.2 | 312 rows",
        },
    },
    "logarchive_usb_host": {
        "name": "logarchive USB host connections",
        "description": "Unified log entries about the USB connection type: the kernel "
                       "AppleUSBCableType, UserEventAgent connectType changes, and "
                       "lockdownd host session entries",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-03",
        "last_update_date": "2026-10-03",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Search terms from Tim Korver, 'Apple Unified Log search term and process "
                 "cheatsheet', recorded as measured on iOS 12.5.7, 18.2.1, 26.0 and 26.6.1. The "
                 "address recorded for it, thesisfriday.com/alr, did not serve the cheatsheet when "
                 "fetched on 2026-10-03, so the statements attributed to it in these notes could "
                 "not be checked. It is cited as reading AppleUSBCableType USBHost as a cable to a "
                 "computer (absent with a power source), connectType 1 as a power source and 2 as "
                 "a computer, and the lockdownd usb_host_connected and bump_connection_count "
                 "entries as the host session rather than the cable. connectType 5, seen on the "
                 "iOS 18.3.2 image, is not among the values attributed to the cheatsheet and is "
                 "reported as stored. The lockdownd entries "
                 "appeared on iOS 12.4 and 17.2.1 only, and none of the families appeared on the "
                 "iOS 26.5.2 image. A computer connection is also what an examiner's acquisition "
                 "produces. Pair with the USB and power connections artifact for cable attach and "
                 "detach. "
                 "An entry absent from an image is not established to be a property of its iOS version: "
                 "Tim Korver's 'What a busy phone forgets' "
                 "(https://thesisfriday.com/thesis-friday-28-what-a-busy-phone-forgets/) measured the "
                 "kernel lines of an unlock gone from a phone in daily use within 13.2 hours, and "
                 "retention was not measured on the tested images. "
                 "Trace ID held no value on any row of the tested images: rows read from tracev3 data leave it empty, and only a 'log show' JSON export fills it.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "link",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 38 rows",
            "hc_ios17_2": "iOS 17.2.1 | 124 rows",
            "dexter_ios18": "iOS 18.3.2 | 2 rows",
            "iphone12_ios18": "iOS 18.7 | 187 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
    "logarchive_app_state": {
        "name": "logarchive app install and state",
        "description": "Unified log entries from installd in the com.apple.appinstallation "
                       "TransactionLog category, and CommCenter ct.server entries beginning 'App "
                       "state'; what each entry records about an app is reported as logged and is "
                       "not sourced here",
        "author": "@Hexordia",
        "creation_date": "2026-10-06",
        "last_update_date": "2026-10-06",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Search terms provided by Hexordia as part of private R&D work; what the entries "
                 "mean is not sourced here, so they are reported as logged. Two filters feed this "
                 "artifact. (1) Entries logged by /usr/libexec/installd in the TransactionLog "
                 "category of the com.apple.appinstallation subsystem. On the five tested images "
                 "each message ended with a phase and an action separated by ' : '. Phases seen: "
                 "'Start', 'Success (End)' and 'Fail (End)'. Actions seen: 'Install (New)', "
                 "'Install (Placeholder)', 'Install (Parallel Placeholder)', 'Install (Promote From "
                 "Placeholder)', 'Install (Patch Update)', 'Uninstall (Application)', 'Uninstall "
                 "(Parallel Placeholder)', 'Staged Update Placeholder' and 'Apply Staged Update'. "
                 "The message begins with an identifier followed by four numbers; on the iOS "
                 "17.2.1, 18.3.2, 18.7 and 26.5.2 images a slash and a second value follow the "
                 "identifier, and on the iOS 12.4 image they do not. What the numbers and the "
                 "second value are is not established. No installd message held <private> on a "
                 "tested image. Other processes log in the same category (19 to 53 processes per "
                 "tested image, 1,992 to 21,210 entries against 20 to 468 from installd); their "
                 "entries are not reported here. (2) CommCenter entries in the ct.server category "
                 "that begin 'App state'. They read 'App state[...] is suspended' or 'App "
                 "state[...] is moving from <state> to <state>'. State names seen: kUnknown, "
                 "kInBackgroundUnknownRestriction, kInBackgroundRestricted, "
                 "kInForegroundUnknownRestriction, kInForegroundRestricted and kNoRestrictions. "
                 "What each state means is not established. On the iOS 12.4 image the bracketed "
                 "value was <private> on each of the 1,237 rows. On the other four images it was "
                 "not redacted, and it was a name followed by a number in parentheses on 514 of "
                 "515 rows; whether that name is a bundle or a process name, and what the number "
                 "is, is not established. Only the direct tracev3 import was tested. A 'log show' "
                 "JSON export was not, and the installd filter relies on the Process Image Path "
                 "column holding the /usr/libexec/installd path. Trace ID held no value on any row "
                 "of the tested images: rows read from tracev3 data leave it empty.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1449 rows",
            "hc_ios17_2": "iOS 17.2.1 | 155 rows",
            "dexter_ios18": "iOS 18.3.2 | 133 rows",
            "iphone12_ios18": "iOS 18.7 | 335 rows",
            "hc_ios26": "iOS 26.5.2 | 590 rows",
        },
    },
}

import os
import re
import shutil
import ijson
from pathlib import Path
from datetime import datetime, timezone
from scripts import unifiedlogs
from scripts.ilapfuncs import artifact_processor, get_file_path, \
    get_sqlite_db_records, logfunc, get_sysdiagnose_files

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


def _is_sysdiagnose_tarball(path):
    """True for a finished sysdiagnose tar.gz (an IN_PROGRESS_ one is not)."""
    name = os.path.basename(str(path))
    return name.startswith('sysdiagnose_') and name.endswith('.tar.gz') and 'IN_PROGRESS_' not in name


@artifact_processor
def logarchive(context):
    """Import Apple Unified Logs into the LAVA database.

    Two sources, in order of preference:

      1. a 'logarchive*.json' export the examiner produced with 'log show' on a Mac, which
         stays the documented workflow and is what an examiner explicitly chose to provide;
      2. the tracev3 data in the extraction itself, read natively, which needs no Mac and no
         intermediate json file.

    Rows are streamed rather than accumulated: a full archive runs to tens of millions of
    records, which is more than fits in memory as Python tuples. Each row goes to SQLite as
    it arrives, so peak memory stays flat at one batch however many records the archive holds.
    The artifact is declared lava_only, so nothing replays the rows for a second output.
    """
    files_found = context.get_files_found()
    results = context.create_artifact_result(headers=DATA_HEADERS)

    source_path = get_file_path(files_found, 'logarchive*.json')
    if source_path:
        results.set_source_path(source_path)
        return results.extend(rows_from_json(source_path))

    logarchive_dir, diagnostics_dir, uuidtext_dir = unifiedlogs.find_archive_roots(files_found)
    native = bool(logarchive_dir or diagnostics_dir)
    has_sysdiag = any(_is_sysdiagnose_tarball(f) for f in files_found)
    if not native and not has_sysdiag:
        return results

    binary = unifiedlogs.find_iterator()
    if not binary:
        logfunc('Unified Log tracev3 data, or a sysdiagnose archive that may hold it, was found but '
                'the unifiedlog_iterator binary is not available, so it cannot be read natively. '
                'Either install the binary (see scripts/unifiedlogs.py) or supply a '
                'logarchive*.json export.')
        return results

    if native:
        if has_sysdiag:
            logfunc('logarchive: native logarchive or diagnostics data was found, so the '
                    'sysdiagnose archives are not read.')
        if logarchive_dir:
            archive_dir = logarchive_dir
            source_path = logarchive_dir
        else:
            if not uuidtext_dir:
                # Without uuidtext the parser cannot resolve format strings, so the messages
                # would come back as placeholders. Better to say why than to import junk.
                logfunc('Unified Log tracev3 data was found but the uuidtext directory was not, '
                        'so log messages cannot be resolved. Skipping.')
                return results
            archive_dir = unifiedlogs.assemble_archive(
                diagnostics_dir, uuidtext_dir,
                os.path.join(context.get_data_folder(), '_logarchive_native'))
            source_path = f'{diagnostics_dir}\n{uuidtext_dir}'

        parser = unifiedlogs.iterator_version(binary) or os.path.basename(binary)
        logfunc(f'Reading Apple Unified Logs natively with {parser}')
        results.set_source_path(source_path)
        return results.extend(rows_from_tracev3(binary, archive_dir))

    # Only sysdiagnose archives: stage the unified log folders out of each into its own
    # temporary folder, then read them one after another.
    pattern = re.compile(r".*(?:system_logs\.logarchive|db/diagnostics|db/uuidtext)/.*", re.IGNORECASE)
    sysdiag_extractions = {}
    try:
        for file_obj, virt_path in get_sysdiagnose_files(files_found, pattern, text_mode=False):
            if 'PaxHeader' in virt_path:
                continue

            current_sysdiag = virt_path.split(' >> ')[0] if ' >> ' in virt_path else virt_path
            if current_sysdiag not in sysdiag_extractions:
                safe_name = os.path.basename(current_sysdiag).replace('.tar.gz', '')
                unique_index = len(sysdiag_extractions)
                temp_dir = os.path.join(context.get_data_folder(), f'_logarchive_{safe_name}_{unique_index}')
                sysdiag_extractions[current_sysdiag] = {'temp_dir': temp_dir, 'extracted_files': []}

            temp_log_dir = sysdiag_extractions[current_sysdiag]['temp_dir']

            # Reconstruct the inner directory paths
            inner_path = virt_path.split(' >> ')[-1].lstrip('/\\')
            if 'system_logs.logarchive' in inner_path:
                inner_path = inner_path[inner_path.find('system_logs.logarchive'):]
            elif 'db/diagnostics' in inner_path:
                inner_path = inner_path[inner_path.find('db/diagnostics'):]
            elif 'db/uuidtext' in inner_path:
                inner_path = inner_path[inner_path.find('db/uuidtext'):]

            inner_path = os.path.normpath(inner_path.replace('/', os.sep))
            out_path = os.path.join(temp_log_dir, inner_path)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)

            try:
                with open(out_path, 'wb') as f_out:
                    shutil.copyfileobj(file_obj, f_out)
                sysdiag_extractions[current_sysdiag]['extracted_files'].append(Path(out_path))
            except OSError as e:
                logfunc(f"logarchive: OS Error extracting {virt_path}: {e}")
    except OSError as e:
        logfunc(f"logarchive: OS Error during sysdiagnose extraction: {e}")

    def remove_staged():
        for data in sysdiag_extractions.values():
            shutil.rmtree(data['temp_dir'], ignore_errors=True)

    # Work out, before anything is read, which sysdiagnoses hold usable unified log data, so
    # the source path names only those.
    plans = []
    for sysdiag_name, data in sysdiag_extractions.items():
        label = os.path.basename(sysdiag_name)
        if not data['extracted_files']:
            continue
        la_dir, diag_dir, uuid_dir = unifiedlogs.find_archive_roots(data['extracted_files'])
        if not la_dir and not diag_dir:
            logfunc(f'logarchive: no unified log data found in {label}.')
            continue
        if not la_dir and not uuid_dir:
            logfunc(f'logarchive: skipping {label}: uuidtext missing.')
            continue
        plans.append((sysdiag_name, label, data['temp_dir'], la_dir, diag_dir, uuid_dir))

    if not plans:
        remove_staged()
        return results

    results.set_source_path('\n'.join(plan[0] for plan in plans))
    parser = unifiedlogs.iterator_version(binary) or os.path.basename(binary)

    def process_all_sysdiagnoses():
        try:
            for _name, label, temp_dir, la_dir, diag_dir, uuid_dir in plans:
                archive_dir = la_dir or unifiedlogs.assemble_archive(
                    diag_dir, uuid_dir, os.path.join(temp_dir, '_native'))
                logfunc(f'Reading Apple Unified Logs natively from {label} with {parser}')
                count = 0
                for row in rows_from_tracev3(binary, archive_dir):
                    count += 1
                    yield row
                logfunc(f'logarchive: {count} entries read from {label}.')
        finally:
            remove_staged()

    return results.extend(process_all_sysdiagnoses())

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
        -- The observed locationd form is 'VEHICULAR: vehicularStartTime' with a
        -- space after the colon, which the original unspaced pattern missed; the
        -- bare token matches both.
        OR event_message LIKE '%vehicularStartTime%'
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
        OR (event_message LIKE '%Launch application%' AND subsystem LIKE '%com.apple.UserNotifications%')
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
        -- logarchive_navigation. Collected by subsystem rather than by spoken
        -- guidance text. The MapsNavigation framework logs under com.apple.Navigation
        -- out of navd; the categories beneath it differ completely between iOS 16-18
        -- (MNNavigationStateManager, MNNavigationXPC) and iOS 26
        -- (FamiliarRouteAuthorizationChecker, GEONavigationListener), so the subsystem
        -- prefix is matched rather than a category list. Keep this as LIKE: the
        -- com.apple.navigation.VirtualGarage subsystem has a lowercase n and is only
        -- matched because SQLite LIKE is case-insensitive for ASCII.
        OR subsystem LIKE 'com.apple.Navigation%'
        -- Patterns below were added by the 2026-08-01 unified log predicate survey.
        -- Each is documented in the source cited by the artifact that consumes it
        -- (see __artifacts_v2__ notes) and, unless noted there, was observed in an
        -- iOS 18.7 image. Grouped by consuming artifact.
        -- logarchive_calls
        OR event_message LIKE '%Started tracking call%'
        OR event_message LIKE '%Dialed call%'
        OR event_message LIKE '%Call started outgoing%'
        OR event_message LIKE '%All calls ended%'
        OR event_message LIKE '%Received trusted open application request%'
        OR event_message LIKE '%Resuming to tab type%'
        OR event_message LIKE '%tab bar tab changed%'
        -- logarchive_dialed_numbers. The whole call.provider category is collected
        -- rather than a message pattern: the teardown block carries only kActionType
        -- and kUuid, with no distinctive text to anchor on. On the iOS 26.5.2 image
        -- the category held 328 records across three calls, and 1,482 records on the
        -- iOS 18.7 image, so the volume is small either way. The sibling 'call'
        -- category, 199 records on that image, carries the Call(StatusUpdate) state
        -- chain the artifact reads plus the surrounding CommCenter call bookkeeping.
        -- ContactSearchManager is matched by category for the same reason its message
        -- text is not: 'Searching for' on its own matched 808 unrelated records on
        -- the iOS 26.5.2 image.
        OR category = 'call.provider'
        OR category = 'call'
        OR category = 'ContactSearchManager'
        -- logarchive_calls (keypad tones) and logarchive_typing (key sounds); the
        -- actionID space also carries other UI sounds, which stay in this table
        -- for context without a dedicated artifact
        OR event_message LIKE '%Incoming Request : actionID%'
        -- logarchive_typing
        OR category = 'KeyboardSignposts'
        -- logarchive_faceid_presence
        OR event_message LIKE '%PearlCamFrameReceived%'
        OR event_message LIKE '%getFaceDetectInfo%'
        OR event_message LIKE '%[User Presence Monitor]%'
        -- logarchive_pocket_state
        OR event_message LIKE '%Doppler in pocket state%'
        OR event_message LIKE '%PocketState changed%'
        -- logarchive_touch
        OR event_message LIKE '%contact _ presence:%'
        OR event_message LIKE '%touchstats%'
        OR event_message LIKE '%received tapToWake%'
        OR event_message LIKE '%AttentionAwareness.Touch%'
        -- logarchive_usb_connections
        OR event_message LIKE '%plugin state changed to%'
        OR event_message LIKE '%IOAccessoryUSBConnectShim%'
        -- logarchive_camera
        OR event_message LIKE '%will change to: Photo%'
        OR event_message LIKE '%MomentCapture%'
        OR event_message LIKE '%Still image capture type%'
        OR event_message LIKE '%IrisWillBeginCapture%'
        OR event_message LIKE '%added photo to library%'
        OR event_message LIKE '%added video to library%'
        OR event_message LIKE '%Created asset IMG%'
        -- logarchive_notifications
        OR event_message LIKE '%removing notification request%'
        OR event_message LIKE '%expanding notification group%'
        OR event_message LIKE '%notification cell executing default action%'
        OR event_message LIKE '%will present long look%'
        OR event_message LIKE '%action reply for notification%'
        -- logarchive_app_focus
        OR event_message LIKE '%/device/app/inFocus%'
        OR event_message LIKE '%Bootstrapping app<%'
        OR event_message LIKE '%Bootstrapping application<%'
        OR event_message LIKE '%killed from app switcher%'
        OR event_message LIKE '%elementWithFocusBundleID changed%'
        OR event_message LIKE '%Icon tapped%'
        OR event_message LIKE '%Initiating launch from icon view%'
        OR event_message LIKE '%Scene lifecycle state did change%'
        -- logarchive_media_playback
        OR category = 'MediaRemote'
        -- logarchive_sim_cellular
        OR event_message LIKE '%kCTSIMSupportSIMStatus%'
        OR event_message LIKE '%dataNetwork changed to%'
        OR event_message LIKE '%disabling dataNetwork%'
        -- logarchive_unlock_auth
        OR event_message LIKE '%Screen did unlock%'
        OR event_message LIKE '%Processed authentication request%'
        OR event_message LIKE '%Transition: locked ->%'
        OR event_message LIKE '%apfs is being UN-locked%'
        OR event_message LIKE '%lock button source%'
        -- logarchive_dictation
        OR event_message LIKE '%DictationConnection startDictation%'
        OR event_message LIKE '%Dictation did begin%'
        OR event_message LIKE '%Dictation did end%'
        OR event_message LIKE '%CSAudioRecordTypeDictation%'
        -- logarchive_audio_routes
        OR event_message LIKE '%vaemConfigurePVMSettings%'
        OR event_message LIKE '%vaemVADRouteChangeListener%'
        OR event_message LIKE '%cmsmActivateEndpointFromRouteDescription%'
        OR event_message LIKE '%currently activating endpoint%'
        -- logarchive_battery_state
        OR event_message LIKE '%Battery capacity change posted%'
        OR event_message LIKE '%battery info changed to%'
        -- logarchive_ui_navigation
        OR event_message LIKE '%Control Center launched%'
        OR event_message LIKE '%Control Center Visible%'
        OR event_message LIKE '%Setting visibility of widget%'
        OR event_message LIKE '%Today view overlay%'
        OR event_message LIKE '%user-initiated scroll%'
        -- logarchive_airplane_mode additions (Control Center and Settings/Siri
        -- toggle forms; https://www.ios-unifiedlogs.com/post/ios-unified-logs-wifi-and-airplane-mode)
        OR event_message LIKE '%Toggle AirPlane Mode state%'
        OR event_message LIKE '%Setting airplane mode enabled%'
        -- logarchive_wifi_status additions (per-network MAC randomisation records
        -- and hand-picked network joins; Notari SQL queries post)
        OR event_message LIKE '%WFMacRandomisation%'
        OR event_message LIKE '%manual association%'
        -- logarchive_time_change additions (system time-shift broadcast and
        -- on-device manual clock setting; Notari clock-trust post)
        OR event_message LIKE '%Significant time change%'
        OR event_message LIKE '%TMSetManualTime%'
        OR event_message LIKE '%setting manual time%'
        -- Patterns below were confirmed against iOS 16.5 and 17.1 images where
        -- the corresponding events occurred; grouped by consuming artifact.
        -- logarchive_driving (Engaging Driving, DND driving mode and
        -- ATXModeDrivingFeaturizer are already collected above)
        OR event_message LIKE '%MotionState: Driving%'
        OR event_message LIKE '%PedestrianAfterDriving%'
        -- logarchive_bluetooth_pairing
        OR event_message LIKE '%Device found: CBDevice%'
        OR event_message LIKE '%pairing complete%'
        OR event_message LIKE '%pairing started%'
        OR event_message LIKE '%numeric comparison%'
        OR event_message LIKE '%Running SDP%'
        -- logarchive_emergency_sos
        OR event_message LIKE '%broadcasting SOSStatus%'
        OR event_message LIKE '%flowStartedOnEitherDevice%'
        OR event_message LIKE '%sosTriggeredOnPairedDevice%'
        -- logarchive_power_events
        OR event_message LIKE '%iBoot version%'
        OR event_message LIKE '%Deferring device orientation updates for reason: shutdown%'
        OR event_message LIKE '%locationd shutting down%'
        -- logarchive_airdrop
        OR event_message LIKE '%AirDrop ID%'
        OR event_message LIKE '%SharingDaemon State%'
        OR event_message LIKE '%Scanning mode%'
        OR event_message LIKE '%startSending%'
        OR event_message LIKE '%New incoming transfer%'
        OR event_message LIKE '%alertLog: idx:%'
        OR event_message LIKE '%Activating com.apple.sharing.sharesheet%'
        -- logarchive_wifi_status additions (password retrieval, auto-join with
        -- SSID in the clear, link loss, session duration)
        OR event_message LIKE '%Copy password for Network%'
        OR event_message LIKE '%Attempting auto join association%'
        OR event_message LIKE '%Link went down%'
        OR event_message LIKE '%Total connection time%'
        -- logarchive_faceid_presence additions (Touch ID sensor events on home
        -- button devices; home button press form is documented-only)
        OR event_message LIKE '%kAppleBiometricFinger%'
        OR event_message LIKE '%Home Button Was Pressed%'
        -- logarchive_usb_connections addition: the kernel VBUS/CON_DET line the
        -- CarPlay research calls the most consistent connect marker, and whose
        -- 'VBUS) Present: 0' form is the reliable detach signal
        OR event_message LIKE '%USB Power (VBUS) Present%'
        -- logarchive_carplay_session. Documented-only, from the cited CarPlay
        -- handshake research; not observed in any of our validation images, none
        -- of which contain a CarPlay session. See the artifact notes.
        OR event_message LIKE '%Found USB DirectLink%'
        OR event_message LIKE '%session isAuthenticated%'
        OR event_message LIKE '%vehicle ID%'
        OR event_message LIKE '%Persisting widget state%'
        OR event_message LIKE '%WiFiDeviceManagerSetCarPlaySessionState%'
        OR event_message LIKE '%CarPlay session vehicle inform%'
        -- Patterns below were added 2026-10-03 from the cheatsheet cited in the
        -- consuming artifacts' notes, grouped by consuming artifact.
        -- logarchive_unlock_auth: the kernel keybag endpoint. iOS 12.4 writes
        -- 'apfs Data is now UN-locked', later releases 'apfs is now UN-locked'.
        OR event_message LIKE '%is now UN-locked%'
        OR event_message LIKE '%Unlock attempt succeeded%'
        -- logarchive_unlock_auth: every keybag state transition, not only those
        -- leaving 'locked', and the kernel's volume lock and unlock notification.
        OR (subsystem = 'com.apple.chrono' AND category = 'keybag'
            AND event_message LIKE 'Transition:%')
        OR event_message LIKE '%Sending notification for volume%'
        -- logarchive_biometric_match
        OR event_message LIKE '%matchResultHandler: MATCH%'
        OR event_message LIKE '%matchResult:timestamp:%'
        OR event_message LIKE '%has received no-match%'
        OR event_message LIKE '%Base unlock behavior received biometric event%'
        -- logarchive_passcode_field
        OR event_message LIKE '%forSetDelegate:<SBUIPasscodeTextField%'
        OR event_message LIKE '%_teardownExistingDelegate:<SBUIPasscodeTextField%'
        -- logarchive_hardware_buttons
        OR (category = 'Button' AND event_message LIKE '%firstDown:%')
        OR (subsystem = 'com.apple.SpringBoard.buttons'
            AND (event_message LIKE 'press count:%'
                 OR event_message LIKE 'Lock button single press recognized%'
                 OR event_message LIKE 'SOS button gesture: press type=%'))
        -- logarchive_orientation ('Received orientation' is already collected by
        -- the case-insensitive 'Received Orientation' pattern above)
        OR event_message LIKE '%Gesture notification:%'
        OR event_message LIKE '%[TTW] Orientation changed%'
        -- logarchive_system_gestures
        OR event_message LIKE '%system gesture stealing the touches%'
        OR (category LIKE 'SystemGesture%' AND event_message LIKE '%gestureRecognizerShouldBegin%')
        -- logarchive_usb_host
        OR event_message LIKE '%AppleUSBCableType%'
        OR event_message LIKE '%launching clients due to connectType%'
        OR event_message LIKE '%usb_host_connected%'
        OR event_message LIKE '%bump_connection_count%'
        -- logarchive_touch addition (iOS 26)
        OR event_message LIKE '%Touch entered%'
        -- logarchive_app_state
        OR (category LIKE 'TransactionLog%' AND subsystem LIKE '%com.apple.appinstallation%' AND process_image_path LIKE '%/usr/libexec/installd%')
        OR (subsystem LIKE '%com.apple.CommCenter%' AND category LIKE '%ct.server%' AND event_message LIKE 'App state%')
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
        OR event_message LIKE '%Significant time change%'
        -- Manual clock setting on the device; see the artifact notes for sourcing.
        OR event_message LIKE '%TMSetManualTime%'
        OR event_message LIKE '%setting manual time%'
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
        OR (event_message LIKE '%Launch application%' AND subsystem LIKE '%com.apple.UserNotifications%')
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
        -- Toggle forms observed on iOS 18.7; see the artifact notes for sourcing.
        OR event_message LIKE '%Toggle AirPlane Mode state%'
        OR event_message LIKE '%Setting airplane mode enabled%'
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
        -- Per-network MAC randomisation records and hand-picked joins; see the
        -- artifact notes for sourcing.
        OR event_message LIKE '%WFMacRandomisation%'
        OR event_message LIKE '%manual association%'
        -- Keychain password retrieval, auto-join with SSID in the clear, link
        -- loss and per-network session duration; see the artifact notes.
        OR event_message LIKE '%Copy password for Network%'
        OR event_message LIKE '%Attempting auto join association%'
        OR event_message LIKE '%Link went down%'
        OR event_message LIKE '%Total connection time%'
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
    # The MapsNavigation framework logs under the com.apple.Navigation subsystem, from
    # navd. Matching the subsystem rather than message text keeps this working across
    # releases and on devices in any language: the categories beneath the subsystem are
    # entirely different on iOS 26 (FamiliarRouteAuthorizationChecker,
    # GEONavigationListener) from iOS 16 through 18 (MNNavigationStateManager,
    # MNNavigationXPC, MNRouteEditor), so a category list would need editing per release.
    #
    # LIKE is case-insensitive for ASCII in SQLite, and one subsystem in this family is
    # spelled with a lowercase n: com.apple.navigation.VirtualGarage. It is inside this
    # pattern only because of that case-insensitivity. Rewriting the comparison as GLOB,
    # or adding a COLLATE BINARY, drops those rows silently, 42 of them on the iOS 18.7
    # image, with no error and no change to any other count.
    return _artifacts_table_records(context, """
        subsystem LIKE 'com.apple.Navigation%'
    """)


def _artifacts_table_records(context, where_clause):
    """Rows from the logarchive_artifacts table matching where_clause.

    Shared by the artifacts added in the 2026-08-01 predicate survey. Each one is a
    filter over the table the logarchive_artifacts artifact materializes, exactly like
    the older artifacts above; the WHERE fragment is the only thing that varies.
    """
    source_path = get_file_path(context.get_files_found(), '_lava_artifacts.db')
    query = f'SELECT * FROM logarchive_artifacts WHERE {where_clause}'
    data_list = list(get_sqlite_db_records(source_path, query))
    return DATA_HEADERS, data_list, source_path

@artifact_processor
def logarchive_calls(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%Started tracking call%'
        OR event_message LIKE '%Dialed call%'
        OR event_message LIKE '%Call started outgoing%'
        OR event_message LIKE '%All calls ended%'
        OR event_message LIKE '%Received trusted open application request%'
        OR event_message LIKE '%Resuming to tab type%'
        OR event_message LIKE '%tab bar tab changed%'
        -- Keypad tones: actionID 1200-1209 map to keypad digits 0-9
        OR event_message LIKE '%Incoming Request : actionID 120%'
    ''')

@artifact_processor
def logarchive_dialed_numbers(context):
    # kActionType selects the setup and teardown blocks out of the call.provider
    # narrative; Call(StatusUpdate) carries the state chain the cited research uses to
    # separate a connected call from a dialed attempt. The rest of the category stays in
    # the collection table for context.
    #
    # Every clause is scoped to the category on purpose. A bare '%kPhoneNumber%' also
    # matches locationd's 'kPhoneNumberStatusNotification' under category Emergency,
    # which carries no number: 7 such records on the iOS 16.5 image and 44 on the
    # iOS 17.1 one, against 3 real setup blocks on the iOS 26.5.2 image.
    return _artifacts_table_records(context, '''
        (category = 'call.provider' AND event_message LIKE '%kPhoneNumber%')
        OR (category = 'call.provider' AND event_message LIKE '%kActionType%')
        OR (category = 'call' AND event_message LIKE '%Call(StatusUpdate)%')
        OR category = 'ContactSearchManager'
    ''')

@artifact_processor
def logarchive_typing(context):
    return _artifacts_table_records(context, '''
        category = 'KeyboardSignposts'
        -- Keyboard sounds: 1104 character, 1155 delete, 1156 modifier
        OR event_message LIKE '%Incoming Request : actionID 1104%'
        OR event_message LIKE '%Incoming Request : actionID 1155%'
        OR event_message LIKE '%Incoming Request : actionID 1156%'
    ''')

@artifact_processor
def logarchive_faceid_presence(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%PearlCamFrameReceived%'
        OR event_message LIKE '%getFaceDetectInfo%'
        OR event_message LIKE '%[User Presence Monitor]%'
        -- Touch ID sensor events on home button devices; the home button press
        -- form is documented-only (see artifact notes)
        OR event_message LIKE '%kAppleBiometricFinger%'
        OR event_message LIKE '%Home Button Was Pressed%'
    ''')

@artifact_processor
def logarchive_pocket_state(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%Doppler in pocket state%'
        OR event_message LIKE '%PocketState changed%'
    ''')

@artifact_processor
def logarchive_touch(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%contact _ presence:%'
        OR event_message LIKE '%touchstats%'
        OR event_message LIKE '%received tapToWake%'
        OR event_message LIKE '%AttentionAwareness.Touch%'
        OR event_message LIKE '%Touch entered%'
    ''')

@artifact_processor
def logarchive_usb_connections(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%plugin state changed to%'
        OR event_message LIKE '%IOAccessoryUSBConnectShim%'
        -- Matches both the attach ('Present: 1') and detach ('Present: 0') forms
        OR event_message LIKE '%USB Power (VBUS) Present%'
    ''')

@artifact_processor
def logarchive_camera(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%will change to: Photo%'
        OR event_message LIKE '%MomentCapture%'
        OR event_message LIKE '%Still image capture type%'
        OR event_message LIKE '%IrisWillBeginCapture%'
        OR event_message LIKE '%added photo to library%'
        OR event_message LIKE '%added video to library%'
        OR event_message LIKE '%Created asset IMG%'
    ''')

@artifact_processor
def logarchive_notifications(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%removing notification request%'
        OR event_message LIKE '%expanding notification group%'
        OR event_message LIKE '%notification cell executing default action%'
        OR event_message LIKE '%will present long look%'
        OR event_message LIKE '%action reply for notification%'
    ''')

@artifact_processor
def logarchive_app_focus(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%/device/app/inFocus%'
        -- iOS 17+ and iOS 16 bootstrap forms respectively
        OR event_message LIKE '%Bootstrapping app<%'
        OR event_message LIKE '%Bootstrapping application<%'
        OR event_message LIKE '%killed from app switcher%'
        OR event_message LIKE '%elementWithFocusBundleID changed%'
        OR event_message LIKE '%Icon tapped%'
        OR event_message LIKE '%Initiating launch from icon view%'
        OR event_message LIKE '%Scene lifecycle state did change%'
    ''')

@artifact_processor
def logarchive_media_playback(context):
    return _artifacts_table_records(context, '''
        category = 'MediaRemote'
    ''')

@artifact_processor
def logarchive_sim_cellular(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%kCTSIMSupportSIMStatus%'
        OR event_message LIKE '%dataNetwork changed to%'
        OR event_message LIKE '%disabling dataNetwork%'
        OR event_message LIKE '%ISNetworkObserver: Set network type%'
    ''')

@artifact_processor
def logarchive_unlock_auth(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%Screen did unlock (Was locked for%'
        OR event_message LIKE '%Screen did lock (Was unlocked for%'
        OR event_message LIKE '%Processed authentication request%'
        OR event_message LIKE '%Transition: locked ->%'
        OR event_message LIKE '%apfs is being UN-locked%'
        OR event_message LIKE '%is now UN-locked%'
        OR event_message LIKE '%Unlock attempt succeeded%'
        OR event_message LIKE '%lock button source%'
        OR (subsystem = 'com.apple.chrono' AND category = 'keybag'
            AND event_message LIKE 'Transition:%')
        OR event_message LIKE '%Sending notification for volume%'
    ''')

@artifact_processor
def logarchive_dictation(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%DictationConnection startDictation%'
        OR event_message LIKE '%Dictation did begin%'
        OR event_message LIKE '%Dictation did end%'
        OR event_message LIKE '%CSAudioRecordTypeDictation%'
    ''')

@artifact_processor
def logarchive_audio_routes(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%vaemConfigurePVMSettings%'
        OR event_message LIKE '%vaemVADRouteChangeListener%'
        OR event_message LIKE '%cmsmActivateEndpointFromRouteDescription%'
        OR event_message LIKE '%currently activating endpoint%'
    ''')

@artifact_processor
def logarchive_battery_state(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%Battery capacity change posted%'
        OR event_message LIKE '%battery info changed to%'
    ''')

@artifact_processor
def logarchive_ui_navigation(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%Control Center launched%'
        OR event_message LIKE '%Control Center Visible%'
        OR event_message LIKE '%Setting visibility of widget%'
        OR event_message LIKE '%Today view overlay%'
        OR event_message LIKE '%user-initiated scroll%'
    ''')

@artifact_processor
def logarchive_driving(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%MotionState: Driving%'
        OR event_message LIKE '%vehicularStartTime%'
        OR event_message LIKE '%PedestrianAfterDriving%'
        OR event_message LIKE '%Engaging Driving%'
        OR event_message LIKE '%com.apple.donotdisturb.mode.driving%'
        OR event_message LIKE '%ATXModeDrivingFeaturizer%'
    ''')

@artifact_processor
def logarchive_bluetooth_pairing(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%Device found: CBDevice%'
        -- Matches rapportd 'Pairing completed' and the documented bluetoothd
        -- 'pairing complete' event form
        OR event_message LIKE '%pairing complete%'
        -- Documented-only below; no new pairing occurred in the validation images
        OR event_message LIKE '%pairing started%'
        OR event_message LIKE '%numeric comparison%'
        OR event_message LIKE '%Running SDP%'
    ''')

@artifact_processor
def logarchive_emergency_sos(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%broadcasting SOSStatus%'
        OR event_message LIKE '%flowStartedOnEitherDevice%'
        OR event_message LIKE '%sosTriggeredOnPairedDevice%'
    ''')

@artifact_processor
def logarchive_power_events(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%iBoot version%'
        OR event_message LIKE '%Deferring device orientation updates for reason: shutdown%'
        OR event_message LIKE '%locationd shutting down%'
    ''')

@artifact_processor
def logarchive_airdrop(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%AirDrop ID%'
        OR event_message LIKE '%SharingDaemon State%'
        OR event_message LIKE '%Scanning mode%'
        OR event_message LIKE '%startSending%'
        OR event_message LIKE '%New incoming transfer%'
        OR event_message LIKE '%alertLog: idx:%'
        OR event_message LIKE '%Activating com.apple.sharing.sharesheet%'
    ''')

@artifact_processor
def logarchive_carplay_session(context):
    # Documented-only patterns; see the artifact notes for sourcing and caveats.
    return _artifacts_table_records(context, '''
        event_message LIKE '%Found USB DirectLink%'
        OR event_message LIKE '%session isAuthenticated%'
        OR event_message LIKE '%vehicle ID%'
        OR event_message LIKE '%Persisting widget state%'
        OR event_message LIKE '%WiFiDeviceManagerSetCarPlaySessionState%'
        OR event_message LIKE '%CarPlay session vehicle inform%'
        OR event_message LIKE '%CarPlay Connection Event%'
    ''')


@artifact_processor
def logarchive_biometric_match(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%matchResultHandler: MATCH%'
        OR event_message LIKE '%matchResult:timestamp:%'
        OR event_message LIKE '%has received no-match%'
        OR event_message LIKE '%Base unlock behavior received biometric event%'
    ''')

@artifact_processor
def logarchive_passcode_field(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%forSetDelegate:<SBUIPasscodeTextField%'
        OR event_message LIKE '%_teardownExistingDelegate:<SBUIPasscodeTextField%'
    ''')

@artifact_processor
def logarchive_hardware_buttons(context):
    return _artifacts_table_records(context, '''
        (category = 'Button' AND event_message LIKE '%firstDown:%')
        OR (subsystem = 'com.apple.SpringBoard.buttons'
            AND (event_message LIKE 'press count:%'
                 OR event_message LIKE 'Lock button single press recognized%'
                 OR event_message LIKE 'SOS button gesture: press type=%'))
    ''')

@artifact_processor
def logarchive_orientation(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%Received orientation%'
        OR event_message LIKE '%Gesture notification:%'
        OR event_message LIKE '%[TTW] Orientation changed%'
    ''')

@artifact_processor
def logarchive_system_gestures(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%system gesture stealing the touches%'
        OR (category LIKE 'SystemGesture%' AND event_message LIKE '%gestureRecognizerShouldBegin%')
    ''')

@artifact_processor
def logarchive_usb_host(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%AppleUSBCableType%'
        OR event_message LIKE '%launching clients due to connectType%'
        OR event_message LIKE '%usb_host_connected%'
        OR event_message LIKE '%bump_connection_count%'
    ''')

@artifact_processor
def logarchive_app_state(context):
    return _artifacts_table_records(context, '''
        (category LIKE 'TransactionLog%' AND subsystem LIKE '%com.apple.appinstallation%' AND process_image_path LIKE '%/usr/libexec/installd%')
        OR (subsystem LIKE '%com.apple.CommCenter%' AND category LIKE '%ct.server%' AND event_message LIKE 'App state%')
    ''')
