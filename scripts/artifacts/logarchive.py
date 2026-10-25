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
        "author": "@AlexisBrignoni, Codex, @JohannPLW",
        "creation_date": "2025-05-19",
        "last_update_date": "2026-10-09",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Filters imported logs in bounded row ranges and reports progress, "
                 "including ranges with no matching events. Selected rows stream into LAVA. "
                 "A compiled multi-pattern prefilter accelerates comparisons when available; "
                 "the original SQLite predicates determine which events are selected.",
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
        "notes": "The two tags are matched as message text in any process, with no process, "
                 "subsystem or category condition.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "sun",
    },
    "logarchive_executed_apps": {
        "name": "logarchive executed apps",
        "description": "Unified log entries containing 'Allowing tap for icon view' (matched without "
                       "regard to case, so 'Disallowing tap' entries are included), 'Launching "
                       "application' or 'transition source:', and entries of the "
                       "com.apple.UserNotifications subsystem containing 'Launch application'; what "
                       "each form records is not sourced here",
        "author": "@AlexisBrignoni, @Hexordia",
        "creation_date": "2025-05-26",
        "last_update_date": "2026-10-18",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "'Launch application' is matched only in the com.apple.UserNotifications subsystem. Those "
                 "entries were on six of the 14 images: 7 on ctf2020_ios12, 1 on hickman_ios14_sysdiag, 1 on "
                 "jess_ios15, 3 on abe_ios16, 8 on hc_ios26 and 40 on ai16_ios26_sysdiag, logged by "
                 "SpringBoard in the AppLaunching category. 14 of the 60 contain 'Launch application in "
                 "foreground for notification response action' and 46 contain 'Launch application in "
                 "background for notification response'; 23 hold <private> in place of the value that ends the "
                 "others (20 on ai16_ios26_sysdiag, 3 on hc_ios26). The clause adds no row that the three "
                 "older terms already matched. Process Image Path was SpringBoard on every row except 2 "
                 "nsurlsessiond rows on jess_ios15. Process ID held one value per image on 10 images, two on "
                 "felix23_ios16 and hc_ios26_sysdiag, and three on jess_ios15. The iOS 12.4 image held only "
                 "the UserNotifications entries, so Subsystem and Category each held one value there. Trace ID "
                 "held no value on any row of the tested images: rows read from tracev3 data leave it empty. "
                 "Application (as stored) and Icon Location (as stored), added 2026-10-18, are read from the "
                 "message. A SpringBoard 'Launching application <application> from icon <icon>, location: "
                 "<location>' entry gives both, and 'Allowing tap for icon view '<application>'' gives the "
                 "application. On both forms the application value reads <private> where the log redacted it; "
                 "no redacted location was seen on the 14 images. Other forms leave the two blank, among them "
                 "'Disallowing tap for icon view' entries (5, on felix23_ios16 and iphone12_ios18), which the "
                 "case-insensitive match admits but the column parser does not read, and nsurlsessiond "
                 "'Launching application ... since we could not restore session' entries (2 on jess_ios15), "
                 "which name no icon. On the 14 images every SpringBoard 'from icon' entry gave both values "
                 "and every entry the 'Allowing tap' pattern read gave an application value. Locations seen, "
                 "reported as written: SBIconLocationRoot, SBIconLocationDock, SBIconLocationFolder, "
                 "SBIconLocationAppLibraryCategoryPod and SBIconLocationAppLibraryCategoryPodExpanded.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "code",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 7 rows",
            "hickman_ios14_sysdiag": "iOS 14.3 | 243 rows",
            "jess_ios15": "iOS 15.0.2 | 52 rows",
            "abe_ios16": "iOS 16.5 | 1222 rows",
            "felix23_ios16": "iOS 16.5 | 301 rows",
            "fsfull002_ios17": "iOS 17.1 | 223 rows",
            "hc_ios17_2": "iOS 17.2.1 | 752 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 39 rows",
            "dexter_ios18": "iOS 18.3.2 | 95 rows",
            "iphone12_ios18": "iOS 18.7 | 1676 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 229 rows",
            "hc_ios26": "iOS 26.5.2 | 442 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 75 rows",
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
        "author": "@AlexisBrignoni, @stark4n6, Claude",
        "creation_date": "2025-05-28",
        "last_update_date": "2026-10-18",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "2026-10-14: added com.apple.SpringBoard entries whose message begins "
                 "'UILocked:', followed by a number (6 on hickman_ios14_sysdiag, 25 on "
                 "hc_ios17_2, 3 on rodeo_ios17_sysdiag, 7 on hc_ios26_sysdiag). What the number "
                 "means is not established. The match is anchored to the start of the message "
                 "because on iOS 14.3 SpringBoard also logs volume-control state that contains "
                 "'UILocked:' mid-message (20 entries on hickman_ios14_sysdiag); those are not "
                 "reported. The SpringBoard process also logs entries under subsystem "
                 "com.apple.UserNotificationsKit that contain 'UILocked:' mid-message; the "
                 "subsystem filter keeps those out. "
                 "The 'Device unlocked' pattern matches in any process and in any case. "
                 "softwareupdateservicesd wrote 19, 6, 13, 17 and 6 of those rows on iOS 12.4, 17.2.1, "
                 "18.3.2, 18.7 and 26.5.2, fewer than the kernel 'is now UN-locked' entries the unlock "
                 "sessions artifact reports on each (28, 54, 58, 18 and 26). sharingd, appstored, "
                 "locationd and other processes wrote the rest, up to 424 rows from sharingd on iOS "
                 "17.2.1, so these rows are not a count of unlocks.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "lock",
    },
    "logarchive_wifi_status": {
        "name": "logarchive wifi status",
        "description": "WiFi Status",
        "author": "@AlexisBrignoni, @Hexordia, @stark4n6, Claude",
        "creation_date": "2025-05-28",
        "last_update_date": "2026-10-14",
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
                 "(https://www.ios-unifiedlogs.com/post/ios-unified-logs-wifi-and-airplane-mode). "
                 "2026-10-13: added wifid entries containing 'Auto join association "
                 "succeeded', which carry the network name in the clear on the iOS 14.3, 17.2.1 "
                 "and 26.6 images. None was found in the parsed iOS 17.3 log.",
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
                       "originating process, Phone app tab changes, keypad tone "
                       "requests (actionID 1200-1209 map to keypad digits 0-9), and incoming call "
                       "entries in the ims log category",
        "author": "@AlexisBrignoni, @Hexordia",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-10-12",
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
                 "carries the number in the clear. Entries in category ims are matched on three "
                 "message texts, with no process or subsystem condition: 'Incoming call ... from "
                 "...', 'Alerting user of incoming call' and 'Sending Incoming Call notification'. "
                 "The search terms came from Hexordia research. On the 14 images in sample_data, iOS "
                 "12.4 to 26.6, read from tracev3 data, they gave 11 rows on 4 images (iOS 16.5, "
                 "17.2.1, 18.3.2 and 26.5.2): 5 'Incoming call ... from', 5 'Alerting user' and 1 "
                 "'Sending Incoming Call notification', all from CommCenter in subsystem "
                 "com.apple.ipTelephony. The 5 'Incoming call ... from' rows, on the iOS 16.5, "
                 "17.2.1 and 26.5.2 images, each hold a value beginning with '+' after 'from' that "
                 "is not redacted, so the redaction described above does not cover them. Across the "
                 "14 images the same category held 411 entries reading 'Carrier incoming call "
                 "validations is enabled/disabled for this registration', on 8 images; they are not "
                 "collected, because their text names a registration setting and no call. A 'log "
                 "show' JSON export was not tested.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 430 rows; 0 ims",
            "hickman_ios14_sysdiag": "iOS 14.3 | 199 rows; 0 ims",
            "jess_ios15": "iOS 15.0.2 | 14 rows; 0 ims",
            "abe_ios16": "iOS 16.5 | 836 rows; 4 ims",
            "felix23_ios16": "iOS 16.5 | 63 rows; 0 ims",
            "fsfull002_ios17": "iOS 17.1 | 42 rows; 0 ims",
            "hc_ios17_2": "iOS 17.2.1 | 242 rows; 4 ims",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 11 rows; 0 ims",
            "dexter_ios18": "iOS 18.3.2 | 24 rows; 1 ims",
            "iphone12_ios18": "iOS 18.7 | 570 rows; 0 ims",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows; 0 ims",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 154 rows; 0 ims",
            "hc_ios26": "iOS 26.5.2 | 108 rows; 2 ims",
            "hc_ios26_sysdiag": "iOS 26.6 | 22 rows; 0 ims",
        },
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
                       "(touchstats), touch attention events, and tap-to-wake ('received tapToWake', "
                       "'send tapToWake' and 'tapToWakeDidRecognize' entries, written by backboardd "
                       "and SpringBoard on the tested images)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-10-18",
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
                 "backboardd 'send tapToWake' and SpringBoard 'tapToWakeDidRecognize:' entries were added "
                 "2026-10-18. The send entries equalled the received entries on each image that had either "
                 "(2, 21, 21 and 4 on iOS 17.2.1, 18.3.2, 18.7 and 26.5.2), and tapToWakeDidRecognize gave "
                 "2, 6, 21 and 4 there. On iOS 12.4 tapToWakeDidRecognize gave all 27 rows. "
                 "Trace ID held no value on any row of the tested images: rows read from tracev3 data leave it empty, and only a 'log show' JSON export fills it.",
        "paths": None,
        "output_types": "lava_only",
        "artifact_icon": "target",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 27 rows",
            "hc_ios17_2": "iOS 17.2.1 | 8197 rows",
            "dexter_ios18": "iOS 18.3.2 | 4828 rows",
            "iphone12_ios18": "iOS 18.7 | 24020 rows",
            "hc_ios26": "iOS 26.5.2 | 6941 rows",
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
        "last_update_date": "2026-10-18",
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
                 "entries per unlock on iOS. "
                 "On iOS 17.2.1, 18.3.2, 18.7 and 26.5.2 each entry names one disk device. The 26 entries "
                 "on iOS 26.5.2 were 13 "
                 "pairs less than two seconds apart, one naming disk1s2 and one disk1s8. iOS 18.3.2 held "
                 "28 disk2s2 and 30 disk2s8 entries, iOS 18.7 8 disk1s2 and 10 disk1s8, and iOS 17.2.1 46 "
                 "disk1s2 and 8 disk1s8, while on iOS 12.4 each of the 28 entries reads 'apfs Data is now "
                 "UN-locked' in an 'apfs_device_locked' form and names no disk device. So two entries per unlock did not hold on every tested "
                 "build. "
                 "The address recorded for the cheatsheet, "
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
    "logarchive_charging_state": {
        "name": "logarchive charging state",
        "description": "Unified log entries in which powerd logged a charging state update, with the "
                       "state and the other values the entry names",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-18",
        "last_update_date": "2026-10-18",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Reads the table the logarchive artifacts filter builds, so the logarchive module must run in "
                 "the same session. Row Number is the entry's row number in the logarchive table. Selects "
                 "powerd entries beginning 'handleChargingStateUpdate '. State is the text after 'State:' as "
                 "written. VBUS, UISOC, CHNC and Type are the values after those labels as written. TLC is the "
                 "text after 'TLC:' with trailing whitespace removed, and is blank when the message has no "
                 "TLC. The meaning of these values is not established here. A message of another shape leaves "
                 "those columns blank, and Event Message keeps the whole message; no such message appeared in "
                 "the images tested. Tested on the 14 images in sample_data, iOS 12.4 to 26.6. The entries "
                 "appeared only on the three iOS 26 images, where every row parsed. States seen: Charging, "
                 "Charging Completed, Charging On Hold and Disconnected. On every row VBUS held 1 when State "
                 "began with Charging and 0 when it was Disconnected. UISOC held whole numbers from 2 to 100, "
                 "Type held 0, 1 or 2, and TLC held text shaped like a weekday, month, day, time and year, "
                 "with no time zone in it. The entries record what powerd logged, not what was connected; the "
                 "logarchive USB and power connections artifact reports the cable entries. Process Image Path "
                 "ended in /powerd on every row, which the selection requires, and held one value per image. "
                 "Process ID held one value on all 13 ai16_ios26_sysdiag rows.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "battery-charging",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios14_sysdiag": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 13 rows",
            "hc_ios26": "iOS 26.5.2 | 41 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 18 rows",
        },
    },
    "logarchive_battery_center_sources": {
        "name": "logarchive Battery Center power sources",
        "description": "Unified log entries in which Battery Center listed a power source, the "
                       "internal battery or a wireless accessory, with the name, type, transport, "
                       "charge values and identifiers it logged",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-09",
        "last_update_date": "2026-10-09",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Reads the table the logarchive artifacts filter builds, so the logarchive "
                 "module must run in the same session. Row Number is the entry's row number in "
                 "the logarchive table. Selects com.apple.BatteryCenter entries containing 'Found "
                 "power source: {', whose message is a dictionary of 'key = value;' lines. Each "
                 "column named for a key holds that key's value as logged, with the quotes and "
                 "backslash escapes of a quoted value removed. Every other key goes to Other "
                 "Values as 'key = value', a value that is itself a dictionary is kept there "
                 "as one value (Trusted Battery Data, AdapterDetails), and so is any line that is not a "
                 "key and value pair. The meaning and units of the values are not established "
                 "here. Howard Oakley describes these entries on macOS in 'How macOS keeps an eye "
                 "on UPS and wireless devices' "
                 "(https://eclecticlight.co/2024/06/21/how-macos-keeps-an-eye-on-ups-and-wireless-devices/) "
                 "and 'Check UPS, batteries and input devices using Unhidden' "
                 "(https://eclecticlight.co/2024/07/08/check-ups-batteries-and-input-devices-using-unhidden/). "
                 "His posts do not cover iOS, and the second reports the BatteryCenter framework "
                 "as added in macOS Sonoma; the iOS 12.4 image tested here, whose rows are dated "
                 "2020, already holds these entries. Tested on the 14 images in sample_data, iOS "
                 "12.4 to 26.6, read from tracev3 data; a 'log show' JSON export was not tested. "
                 "13 images gave 12,582 rows, 2,591 at most on one image. hc_ios18_7 held no "
                 "com.apple.BatteryCenter entry among its 726,120 log entries, which is not "
                 "evidence about its battery. Name held a value on every row. 12,251 rows "
                 "describe the internal battery: Name InternalBattery-0, Transport Type Internal, "
                 "Is Present 1. Max Capacity held 100 on all 12,582 rows. 331 rows, all on "
                 "ai16_ios26_sysdiag (iOS 26.5.2), describe one Bluetooth accessory: Type "
                 "'Accessory Source', Transport Type Bluetooth, Accessory Category Watch, Vendor "
                 "ID 76 and an Accessory Identifier in the 8-4-4-4-12 form of a UUID, with Low "
                 "Warn Level, Temperature and AdapterDetails in Other Values and no value for Is "
                 "Present, Raw External Connected, Show Charging UI, Play Charging Chime, Cycle "
                 "count or Is Finishing Charge. Accessory Identifier, Accessory Category and "
                 "Vendor ID had no value on any other row, and no tested image held an entry for "
                 "another kind of accessory, so only that form was exercised. Keys differ by "
                 "release. Cycle count had no value on the five images from iOS 12.4 to 16.5 and "
                 "a value on every internal battery row of the eight from iOS 17.1 up. Play "
                 "Charging Chime had no value on the iOS 12.4 image. Is Finishing Charge had a "
                 "value on exactly the 5,208 rows where Is Charging was 1, and Is Charged on "
                 "1,797 rows of 10 images. The log cut 371 internal battery entries off at 1,031 "
                 "bytes (all 331 on ai16_ios26_sysdiag and 40 of the 45 on dexter_ios18), before "
                 "or inside the Type line. Type has no value on those rows, what was logged "
                 "before the cut is still split, and on 71 of them the cut line is in Other "
                 "Values as 'Type = ' with part of the value. No other entry reached that length. "
                 "The same listing is logged by more than one process and by more than one "
                 "controller object, so rows are not one per battery reading: hc_ios17_2 gave "
                 "2,057 rows from 3 processes and 15 controller addresses. Rows came from "
                 "SpringBoard (11,758), WidgetRenderer_Default (760), "
                 "BatteriesAvocadoWidgetExtension (59) and BatteriesWidgetExtension (5). 5 rows "
                 "on fsfull002_ios17 are dated 1970, the time the logarchive table holds for "
                 "those entries. The other com.apple.BatteryCenter entries are not selected, and "
                 "the 'Found device' entries are reported by the Battery Center devices artifact. "
                 "The logarchive battery state artifact selects other entries: none of its 8,192 "
                 "rows on these images is a com.apple.BatteryCenter entry.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "battery",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 250 rows",
            "hickman_ios14_sysdiag": "iOS 14.3 | 831 rows",
            "jess_ios15": "iOS 15.0.2 | 1770 rows",
            "abe_ios16": "iOS 16.5 | 613 rows",
            "felix23_ios16": "iOS 16.5 | 1747 rows",
            "fsfull002_ios17": "iOS 17.1 | 1257 rows",
            "hc_ios17_2": "iOS 17.2.1 | 2057 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 128 rows",
            "dexter_ios18": "iOS 18.3.2 | 45 rows",
            "iphone12_ios18": "iOS 18.7 | 2591 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows; no com.apple.BatteryCenter entry in the log",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 662 rows",
            "hc_ios26": "iOS 26.5.2 | 449 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 182 rows",
        },
    },
    "logarchive_battery_center_devices": {
        "name": "logarchive Battery Center devices",
        "description": "Unified log entries in which Battery Center listed a device with a "
                       "battery: its name, vendor, charge percentage, charging and connection "
                       "values, transport and identifiers as logged",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-09",
        "last_update_date": "2026-10-09",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Reads the table the logarchive artifacts filter builds, so the logarchive "
                 "module must run in the same session. Row Number is the entry's row number in "
                 "the logarchive table. Selects com.apple.BatteryCenter entries containing 'Found "
                 "device: <BCBatteryDevice:', whose message is a list of 'key = value' pairs "
                 "separated by '; '. The message is split where '; ' is followed by a word and "
                 "'='. Columns hold the values as logged, '(null)' included: Name (name), Group "
                 "Name (groupName), Vendor (vendor), Model Number (modelNumber), Percent Charge "
                 "(percentCharge), Charging (charging), Connected (connected), Internal "
                 "(internal), Power Source State (the key is logged as poweredSoureState), "
                 "Transport Type (transportType), Accessory Identifier (accessoryIdentifier), "
                 "Accessory Category (accessoryCategory), Identifier (identifier) and Product "
                 "Identifier (productIdentifier). Every other pair goes to Other Values, and a "
                 "message of another shape is kept whole there. The meaning of the values is not "
                 "established here. Howard Oakley describes Battery Center's log entries on macOS "
                 "in 'How macOS keeps an eye on UPS and wireless devices' "
                 "(https://eclecticlight.co/2024/06/21/how-macos-keeps-an-eye-on-ups-and-wireless-devices/) "
                 "and 'Check UPS, batteries and input devices using Unhidden' "
                 "(https://eclecticlight.co/2024/07/08/check-ups-batteries-and-input-devices-using-unhidden/). "
                 "His posts do not cover iOS, and they show the power source dictionaries, "
                 "reported by the Battery Center power sources artifact, and not this entry. "
                 "Tested on the 14 images in sample_data, iOS 12.4 to 26.6, read from tracev3 "
                 "data; a 'log show' JSON export was not tested. 13 images gave 12,580 rows, "
                 "2,591 at most on one image. hc_ios18_7 held no com.apple.BatteryCenter entry "
                 "among its 726,120 log entries, which is not evidence about its battery. Name "
                 "held a value on every row, and no entry was cut short (the longest was 568 "
                 "bytes). 12,249 rows have Internal YES, Group Name InternalBattery-0, Accessory "
                 "Identifier (null) and Accessory Category Unknown. Their Name held one value per "
                 "image; whether that is the name set on the device was not checked. 331 rows, "
                 "all on ai16_ios26_sysdiag (iOS 26.5.2), have Internal NO, Transport Type "
                 "Bluetooth, Accessory Category Watch and Name equal to Group Name, with the name "
                 "and the UUID-form Accessory Identifier that the power sources artifact reports "
                 "on its accessory rows. No tested image held an entry for another kind of "
                 "accessory, so only that form was exercised. Vendor (Apple), Connected (YES) and "
                 "Product Identifier (0) held one value on all 12,580 rows. Model Number held "
                 "(null) on every row except the 250 of the iOS 12.4 image, whose entries have no "
                 "modelNumber. Transport Type on the internal rows was Internal, except on the "
                 "iOS 12.4 and 14.3 images, which logged 1 (1,081 rows). Identifier on every row "
                 "equalled a Power Source ID among the same image's power source rows. Other "
                 "Values held parts, matchIdentifier, lowBattery and powerSource on every row, "
                 "lowPowerModeActive on the 11 images from iOS 15.0.2 up, batterySaverModeActive "
                 "on the iOS 12.4 and 14.3 images, and paused on the three iOS 26 images. The "
                 "same listing is logged by more than one process and by more than one controller "
                 "object, so rows are not one per battery reading. hc_ios17_2 and hc_ios26 each "
                 "gave one row fewer than the power sources artifact. 5 rows on fsfull002_ios17 "
                 "are dated 1970, the time the logarchive table holds for those entries.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "battery",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 250 rows",
            "hickman_ios14_sysdiag": "iOS 14.3 | 831 rows",
            "jess_ios15": "iOS 15.0.2 | 1770 rows",
            "abe_ios16": "iOS 16.5 | 613 rows",
            "felix23_ios16": "iOS 16.5 | 1747 rows",
            "fsfull002_ios17": "iOS 17.1 | 1257 rows",
            "hc_ios17_2": "iOS 17.2.1 | 2056 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 128 rows",
            "dexter_ios18": "iOS 18.3.2 | 45 rows",
            "iphone12_ios18": "iOS 18.7 | 2591 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows; no com.apple.BatteryCenter entry in the log",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 662 rows",
            "hc_ios26": "iOS 26.5.2 | 448 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 182 rows",
        },
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
        "last_update_date": "2026-10-18",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Documented at "
                 "https://thesisfriday.com/thesis-friday-19-emergency-sos-decoding-the-cross-device-help-handshake/. "
                 "Status broadcasts and flow entries were observed on iOS 16.5 and 17.1 "
                 "on devices with no known SOS use, so their presence alone does not "
                 "show an SOS call; the payloads are redacted to <private>. The "
                 "sosTriggeredOnPairedDevice entry (documented from a paired Apple Watch "
                 "trigger) is collected as documented-only. Complements the SOS claw "
                 "gesture entries in the logarchive artifacts filter. "
                 "Those are SpringBoard 'SBSOSClawGestureObserver - button press noted' entries, each "
                 "naming a hardware button (lock, volumeUp or volumeDown). The logarchive artifacts table "
                 "held 76, 4, 172 and 64 of them on iOS 17.2.1, 18.3.2, 18.7 and 26.5.2 and none on iOS "
                 "12.4. On iOS 26.5.2 they were two per backboardd press of the named button (48, 10 and 6 "
                 "against 24 side button, 5 volume down and 3 volume up presses); on iOS 18.3.2 there were "
                 "4 against 15 side button presses. They record button presses and are not by themselves a "
                 "sign of an SOS call.",
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
                       "dumps, share sheet activation, transfer entries, discoverable mode changes, and "
                       "validation record hash entries",
        "author": "@AlexisBrignoni, @Hexordia",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-10-12",
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
                 "established here. Every term is matched as message text in any process, with no "
                 "process, subsystem or category condition. 'Scanning mode' and 'startSending' are "
                 "short strings, and whether components other than AirDrop and the share sheet log "
                 "them was not measured, so read Process Image Path, Subsystem and Category on each "
                 "row before attributing it. 'Discoverable mode changed from' and 'Hashes in validation "
                 "record:' come from Hexordia research and are matched at the start of the message. On "
                 "the 14 images in sample_data, iOS 12.4 to 26.6, read from tracev3 data, 'Discoverable "
                 "mode changed from' gave 84 rows on 11 images, all from /usr/libexec/sharingd in "
                 "subsystem com.apple.sharing, category AirDrop. The 76 rows on the eight images from "
                 "iOS 12.4 to 17.3 name the old and new mode ((null), Off, Contacts Only or Everyone); "
                 "the 8 rows on the iOS 18.3.2, 18.7 and 26.6 images read '<private> to <private>'. "
                 "'Hashes in validation record:' is collected as documented-only: no entry on any of "
                 "the 14 images contained that text, so what those entries hold was not measured here. "
                 "Partial SHA-256 hash values in the receiver's sysdiagnose logarchive are described by "
                 "Epstein, Klein and Feuerstein, 'Analysis of Sysdiagnose in iOS 15 to Identify the "
                 "Sending Phone Number of AirDrop Data', Journal of Forensic Sciences, January 2022, "
                 "as summarised in the 4n6 Ninja post "
                 "(https://gforce4n6.blogspot.com/2022/03/airdropping-some-knowledge-using-rleapp.html). "
                 "A 'log show' JSON export was not tested.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "share",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 94 rows; 5 discoverable mode, 0 validation record hashes",
            "hickman_ios14_sysdiag": "iOS 14.3 | 232 rows; 6 discoverable mode, 0 validation record hashes",
            "jess_ios15": "iOS 15.0.2 | 66 rows; 3 discoverable mode, 0 validation record hashes",
            "abe_ios16": "iOS 16.5 | 268 rows; 3 discoverable mode, 0 validation record hashes",
            "felix23_ios16": "iOS 16.5 | 30 rows; 4 discoverable mode, 0 validation record hashes",
            "fsfull002_ios17": "iOS 17.1 | 160 rows; 46 discoverable mode, 0 validation record hashes",
            "hc_ios17_2": "iOS 17.2.1 | 275 rows; 8 discoverable mode, 0 validation record hashes",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 90 rows; 1 discoverable mode, 0 validation record hashes",
            "dexter_ios18": "iOS 18.3.2 | 12 rows; 3 discoverable mode, 0 validation record hashes",
            "iphone12_ios18": "iOS 18.7 | 17 rows; 3 discoverable mode, 0 validation record hashes",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows; 0 discoverable mode, 0 validation record hashes",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 1 rows; 0 discoverable mode, 0 validation record hashes",
            "hc_ios26": "iOS 26.5.2 | 46 rows; 0 discoverable mode, 0 validation record hashes",
            "hc_ios26_sysdiag": "iOS 26.6 | 13 rows; 2 discoverable mode, 0 validation record hashes",
        },
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
        "notes": "NOT YET VALIDATED IN-HOUSE. 'CarPlay Connection Event' is a term this module's "
                 "general filter already carried; it is not in the cited research, no source for it "
                 "is cited here and what an entry holding it records is not established. Every "
                 "other pattern here comes from Tim Korver's "
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
                       "press counts and single press recognition, SpringBoard raw volume press "
                       "entries, and the SpringBoard button combination recognizer's press type",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-03",
        "last_update_date": "2026-10-18",
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
                 "examiner handling the device. "
                 "SpringBoard 'RECEIVED rawVolumeIncreasePress' and 'RECEIVED rawVolumeDecreasePress' "
                 "entries were added 2026-10-18. On the tested images each press gave a 'down:YES' entry followed by a 'down:NO' "
                 "entry. The iOS "
                 "18.7 image held 41 increase and 13 decrease pairs and the iOS 26.5.2 image 3 and 5, "
                 "equal on both to the backboardd 0xC/0xE9 and 0xC/0xEA presses; none appeared on iOS "
                 "12.4, 17.2.1 or 18.3.2. "
                 "Trace ID held no value on any row of the tested "
                 "images: rows read from tracev3 data leave it empty, and only a 'log show' JSON "
                 "export fills it.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 9 rows",
            "hc_ios17_2": "iOS 17.2.1 | 188 rows",
            "dexter_ios18": "iOS 18.3.2 | 40 rows",
            "iphone12_ios18": "iOS 18.7 | 514 rows",
            "hc_ios26": "iOS 26.5.2 | 191 rows",
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
                       "TransactionLog category, installd entries naming a container it 'Made "
                       "container live for', and CommCenter ct.server entries beginning 'App "
                       "state'; what each entry records about an app is reported as logged and is "
                       "not sourced here",
        "author": "@Hexordia",
        "creation_date": "2026-10-06",
        "last_update_date": "2026-10-21",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Search terms provided by Hexordia as part of private R&D work; what the entries "
                 "mean is not sourced here, so they are reported as logged. Three filters feed this "
                 "artifact. (1) Entries logged by /usr/libexec/installd in the TransactionLog "
                 "category of the com.apple.appinstallation subsystem. On the five tested images "
                 "each message ended with a phase and an action separated by ' : '. Phases seen: "
                 "'Start', 'Success (End)' and 'Fail (End)'. Actions seen on those five images: "
                 "'Install (New)', "
                 "'Install (Placeholder)', 'Install (Parallel Placeholder)', 'Install (Promote From "
                 "Placeholder)', 'Install (Patch Update)', 'Uninstall (Application)', 'Uninstall "
                 "(Parallel Placeholder)', 'Staged Update Placeholder' and 'Apply Staged Update'. "
                 "The message begins with an identifier followed by four numbers; on the iOS "
                 "17.2.1, 18.3.2, 18.7 and 26.5.2 images a slash and a second value follow the "
                 "identifier, and on the iOS 12.4 image they do not. What the numbers and the "
                 "second value are is not established. No installd message held <private> on a "
                 "tested image. The category held 1,992 to 21,210 entries from 19 to 53 processes "
                 "per tested image; 20 to 468 of those entries were from installd. Entries from "
                 "other processes are not reported here. (2) CommCenter entries in the ct.server category "
                 "that begin 'App state'. They read 'App state[...] is suspended' or 'App "
                 "state[...] is moving from <state> to <state>'. State names seen: kUnknown, "
                 "kInBackgroundUnknownRestriction, kInBackgroundRestricted, "
                 "kInForegroundUnknownRestriction, kInForegroundRestricted and kNoRestrictions. "
                 "What each state means is not established. On the iOS 12.4 image the bracketed "
                 "value was <private> on each of the 1,237 rows. On the other four images it was "
                 "not redacted, and it was a name followed by a number in parentheses on 514 of "
                 "515 rows; whether that name is a bundle or a process name, and what the number "
                 "is, is not established. (3) Entries logged by /usr/libexec/installd whose "
                 "message contains 'Made container live for', followed by an identifier and a "
                 "container path. The iOS 12.4, 17.2.1, 18.3.2, 18.7 and 26.5.2 images held 60, "
                 "5, 4, 44 and 0 of them; none held <private>, and Subsystem and Category were "
                 "empty on all 113. The path was under /private/var/containers/Bundle/Application "
                 "on all of them except six on the iOS 12.4 image: three under "
                 "/private/var/mobile/Containers/Data/Application and three under "
                 "/private/var/mobile/Containers/Data/PluginKitPlugin. Whether an entry marks an "
                 "install, an update or another container change is not established. Most were "
                 "logged after a TransactionLog Start entry for the same identifier and before a "
                 "later End entry for the same action, but none of the four on the iOS 18.3.2 "
                 "image was, nor five of the 60 on the iOS 12.4 image. Only the direct tracev3 "
                 "import was tested. A 'log show' JSON export was not, and both installd filters "
                 "rely on the Process Image Path "
                 "column holding the /usr/libexec/installd path. Trace ID held no value on any row "
                 "of the tested images: rows read from tracev3 data leave it empty.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1509 rows",
            "hc_ios17_2": "iOS 17.2.1 | 160 rows",
            "dexter_ios18": "iOS 18.3.2 | 137 rows",
            "iphone12_ios18": "iOS 18.7 | 379 rows",
            "hc_ios26": "iOS 26.5.2 | 590 rows",
        },
    },
    "logarchive_device_id": {
        "name": "Logarchive - Device Identifiers",
        "description": "Unified log entries that carry device identifying details: the model, OS "
                       "version and build that sharingd logs, and the name, device type, OS "
                       "build and serial number of each peer that securityd lists in its account "
                       "state, the examined device among them.",
        "author": "@Hexordia, @stark4n6",
        "creation_date": "2026-10-06",
        "last_update_date": "2026-10-09",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Rows are unified log entries selected by three filters and reported whole; no "
                 "value is parsed out of the message. Tested on seven images running iOS 12.4, "
                 "16.5, 17.2.1, 17.3, 18.3.2, 18.7 and 26.5.2; the row counts are in "
                 "sample_data. The sharingd filter (process /usr/libexec/sharingd, message "
                 "containing 'Device Information:') matched on all seven. The line has the shape "
                 "'Device Information: Production: <model name> (<model identifier>), iPhone OS "
                 "<version> (<build>), <n>% (charging)', or '(not charging)'. It does not hold "
                 "the device name: on the four images where securityd names the device's own "
                 "peer, no sharingd row contained that name. 399 of the 411 sharingd rows are "
                 "'SharingDaemon State' dumps that embed the line. A dump row carries no "
                 "subsystem and no category, so on the iOS 26.5.2 image, where every row is a "
                 "dump, Subsystem and Category held no value on any of the 46 rows. The line "
                 "that sharingd logs on its own was readable on iOS 12.4, 17.2.1 and 17.3 and "
                 "read 'Device Information: <private>' on every such row of iOS 18.3.2 and 18.7 "
                 "(2 and 3 rows); iOS 16.5 and 26.5.2 held no such row. The same model and OS "
                 "string repeats from row to row; only the iOS 26.5.2 image held two different "
                 "version strings. The securityd filter (process /usr/libexec/securityd, "
                 "category accountLogState, message containing 'name:') matched on iOS 12.4, "
                 "16.5, 17.2.1 and 17.3 (8, 12, 18 and 2 rows) and on none of iOS 18.3.2, 18.7 "
                 "and 26.5.2, where no entry in that category from any process contained "
                 "'name:'. Each row is one peer record ('PI:') from securityd's Secure Object "
                 "Sync account state: its fields include a name, a flag group, the device type, "
                 "an OS build and a serial number. The rows cover every peer listed, not only "
                 "the examined device: the iOS 16.5 image listed 6 peers, one of them a MacBook "
                 "Pro, and each of the four images listed one peer of type Unknown. All 40 rows "
                 "carried a serial value, and two peers can carry the same one: the four images "
                 "listed 13 peers with 8 distinct serial values, counted per image. The first "
                 "character of the flag group is 'M' on the examined device's own peer and 'm' "
                 "on any other (Reference: Apple, Security, SOSPeerInfo.m, boolToChars(isMe, "
                 "'M', 'm'), "
                 "https://github.com/apple-oss-distributions/Security/blob/db15acbe6a7f257a859ad9a3bb86097bfe0679d9/keychain/SecureObjectSync/SOSPeerInfo.m#L699 "
                 "; the same call is in that file at each of the 40 published tags read, "
                 "Security-58286.1.32 to Security-61439.140.12). Exactly one peer on each of the "
                 "four images carried 'M'. A peer can appear on more than one row: the iOS 12.4 "
                 "image held 2 peers on 8 rows. The terminusd filter (process "
                 "/usr/libexec/terminusd, subsystem com.apple.networkrelay, message containing "
                 "'Starting terminusd') matched no entry on any of the seven images, and no "
                 "entry from any process contained 'Starting terminusd', so what those entries "
                 "hold was not measured here. Only the iOS 17.3 image, a sysdiagnose, held "
                 "terminusd entries at all (133). The three search terms came from Hexordia "
                 "research. Process Image Path held one value, /usr/libexec/sharingd, on every "
                 "row of iOS 18.3.2, 18.7 and 26.5.2, which have sharingd rows only, and Process "
                 "ID held one value on all 11 rows of the iOS 18.3.2 image. Trace ID held no "
                 "value on any row of the tested images: rows read from tracev3 data leave it "
                 "empty, and only a 'log show' JSON export fills it.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 10 rows; 2 sharingd, 8 securityd, 0 terminusd",
            "abe_ios16": "iOS 16.5 | 13 rows; 1 sharingd, 12 securityd, 0 terminusd",
            "hc_ios17_2": "iOS 17.2.1 | 277 rows; 259 sharingd, 18 securityd, 0 terminusd",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 89 rows; 87 sharingd, 2 securityd, 0 terminusd",
            "dexter_ios18": "iOS 18.3.2 | 11 rows; 11 sharingd, 0 terminusd",
            "iphone12_ios18": "iOS 18.7 | 5 rows; 5 sharingd, 0 terminusd",
            "hc_ios26": "iOS 26.5.2 | 46 rows; 46 sharingd, 0 terminusd",
        },
    },
    "logarchive_wake_source": {
        "name": "logarchive wake source",
        "description": "Unified log entries from SpringBoard whose message begins 'wake source:' "
                       "followed by a source name such as Notification, LiftToWake, Touch, "
                       "ACPowerChange, LockButton or HomeButton",
        "author": "@Hexordia",
        "creation_date": "2026-10-09",
        "last_update_date": "2026-10-12",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Reads the table the logarchive artifacts filter builds, so the logarchive "
                 "module must run in the same session. Selects entries whose subsystem contains "
                 "com.apple.SpringBoard and whose message begins 'wake source:'. The search term "
                 "came from Hexordia research. The name after the colon is reported as logged; "
                 "what each name means, and whether an entry marks the screen turning on, is not "
                 "established here. Tested on the 14 images in sample_data, iOS 12.4 to 26.6, read "
                 "from tracev3 data; a 'log show' JSON export was not tested. 11 images gave 606 "
                 "rows: Notification 220 rows on 8 images, LiftToWake 188 on 11, Touch 69 on 9, "
                 "ACPowerChange 63 on 8, LockButton 58 on 9, HomeButton 7 on 2 (iOS 15.0.2 and "
                 "16.5) and BumpToWake 1 on 1 (iOS 18.7). No other name was logged on these "
                 "images, which does not show that none exists. The iOS 12.4 and 14.3 images held "
                 "com.apple.SpringBoard entries in category DashBoard (150 and 464) and none "
                 "beginning 'wake source:'; hc_ios18_7 held no entry in that category among its "
                 "726,120 log entries. A zero is not evidence that the screen did not wake. "
                 "Process Image Path (/System/Library/CoreServices/SpringBoard.app/SpringBoard), "
                 "Subsystem (com.apple.SpringBoard) and Category (DashBoard) each held one value "
                 "on all 606 rows. Process ID held one value on every row of nine images and two "
                 "values on felix23_ios16 and hc_ios26_sysdiag. Trace ID held no value on any row: "
                 "rows read from tracev3 data leave it empty.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "sunrise",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows; 150 com.apple.SpringBoard DashBoard entries, none beginning 'wake source:'",
            "hickman_ios14_sysdiag": "iOS 14.3 | 0 rows; 464 com.apple.SpringBoard DashBoard entries, none beginning 'wake source:'",
            "jess_ios15": "iOS 15.0.2 | 111 rows",
            "abe_ios16": "iOS 16.5 | 61 rows",
            "felix23_ios16": "iOS 16.5 | 37 rows",
            "fsfull002_ios17": "iOS 17.1 | 97 rows",
            "hc_ios17_2": "iOS 17.2.1 | 46 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 13 rows",
            "dexter_ios18": "iOS 18.3.2 | 39 rows",
            "iphone12_ios18": "iOS 18.7 | 76 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows; no com.apple.SpringBoard DashBoard entry in the log",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 18 rows",
            "hc_ios26": "iOS 26.5.2 | 85 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 23 rows",
        },
    },
    "logarchive_weather": {
        "name": "logarchive weather",
        "description": "Unified log entries under the com.apple.weather subsystem about weather "
                       "data fetches and forecast builds, each carrying a location value. They are "
                       "written by the Weather app, its widget and, on some images, other "
                       "processes. On the iOS 14.3 image the location is a place name with "
                       "coordinates; on the iOS 17 and 26 images it is an encoded value.",
        "author": "@Hexordia, @stark4n6, @AlexisBrignoni, Claude",
        "creation_date": "2026-10-13",
        "last_update_date": "2026-10-14",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Matches four kinds of entry by category and message text: category "
                 "WeatherService or ForecastWeatherWidget containing 'About to fetch'; category "
                 "ForecastWeatherWidget containing 'Data operation succeeded'; category "
                 "WeatherService containing 'Successfully built' or 'Got response for fetch of'; "
                 "and category WeatherWidget containing 'successfully built'. The query does not "
                 "filter on subsystem; every matched row on the four images below was "
                 "com.apple.weather (com.apple.Weather on iOS 14.3). On hickman_ios14_sysdiag all "
                 "9 rows were ForecastWeatherWidget 'Data operation succeeded' entries carrying a "
                 "place name, a time zone and latitude and longitude in plain text. On the iOS "
                 "17.2.1, 17.3 and 26.6 images no entry of that kind was found in the parsed log, "
                 "and every row "
                 "carried the location as a 24-character base64 value (16 bytes) instead of "
                 "coordinates; what that value encodes is not established. Those rows were "
                 "WeatherService entries (367 of 393 on hc_ios17_2, 3 of 3 on rodeo_ios17_sysdiag, "
                 "205 of 221 on hc_ios26_sysdiag) and WeatherWidget 'Timeline: successfully built' "
                 "entries (26 and 16). Besides the Weather app and WeatherWidget, the rows on "
                 "rodeo_ios17_sysdiag were written by SleepLockScreen and 40 rows on "
                 "hc_ios26_sysdiag by destinationd. Trace ID held no value on any row.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "cloud-pin",
        "sample_data": {
            "hickman_ios14_sysdiag": "iOS 14.3 | 9 rows",
            "hc_ios17_2": "iOS 17.2.1 | 393 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 3 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 221 rows",
        },
    },
    "logarchive_family_hotspot": {
        "name": "logarchive family hotspot",
        "description": "Unified log entries recording the Family Hotspot state. An entry holds "
                       "either a single state (Disabled was observed) or a list of quoted "
                       "strings, each followed by a value.",
        "author": "@Hexordia, @stark4n6, @AlexisBrignoni, Claude",
        "creation_date": "2026-10-13",
        "last_update_date": "2026-10-14",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Matches entries whose message contains 'Family Hotspot State'. The query does "
                 "not filter on subsystem; every matched row was logged by sharingd under "
                 "com.apple.sharing, category Daemon. On rodeo_ios17_sysdiag the single row "
                 "listed five quoted strings, each followed by '-> Ask'; 'Ask' was the only value "
                 "observed after a quoted string. What the strings and values mean is not "
                 "established here. On "
                 "hickman_ios14_sysdiag and hc_ios17_2 every row read 'Family Hotspot State: "
                 "Disabled'. On hc_ios26_sysdiag no 'Family Hotspot State' entry was found in the "
                 "parsed log. "
                 "sharingd also logs 'Family hotspot entries:' followed by a single number on "
                 "the iOS 14.3 and 17 images and by '<private>' on iOS 26.6 (value redacted by the "
                 "unified log); this artifact does not report those entries. Trace ID held no "
                 "value on any row.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "access-point",
        "sample_data": {
            "hickman_ios14_sysdiag": "iOS 14.3 | 3 rows",
            "hc_ios17_2": "iOS 17.2.1 | 3 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 1 row",
            "hc_ios26_sysdiag": "iOS 26.6 | 0 rows; no 'Family Hotspot State' entry in the parsed log",
        },
    },
    # ---- TCC authorization cache and location manager state dumps (begin) ----
    "logarchive_tcc_cache": {
        "name": "logarchive TCC authorization cache dumps",
        "description": "Statedump snapshots titled 'TCC Authorization Cache', one row per cached "
                       "authorization entry in each dump: the service, the auth right, the reason and "
                       "the version as logged, and the process that wrote the dump. A dump is the "
                       "process's state when it was written, not an event, and the same entry is "
                       "repeated by the later dumps that still hold it.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-19",
        "last_update_date": "2026-10-19",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Statedump records carry no subsystem or category, and the logarchive table does not "
                 "keep the record's event type, so they are found by the first line of the message, "
                 "'title: TCC Authorization Cache'. The body is a JSON object of service name to a "
                 "credential and an authorization record, each a text description. Each entry becomes a "
                 "row: Service is the JSON key, Credential Object Address and Authorization Object Address are the hexadecimal "
                 "addresses in the two descriptions, Auth Right, Reason and Version are the "
                 "words and number after those labels, Other Flags is any text after the version, and "
                 "Authorization Record is the description as logged. Values are copied as logged and "
                 "this artifact assigns no meaning to them. In the logs read the two descriptions held "
                 "object addresses and no client identifier, bundle id or process name, so a row does not "
                 "name the application the entry is about; the only attribution is Process Image Path and "
                 "Process ID, the process that wrote the dump, as stored. Whether the cache is that "
                 "process's own, what a Version of 1 or 2 denotes, what 'Has Prompted For Allow' denotes, "
                 "and how an entry relates to the TCC.db access table are not established here. An entry "
                 "is the cache's content at the dump time, which is the record's time as stored, shown in "
                 "UTC. It does not say when the permission was granted, changed or used, and a match is a "
                 "lead, not proof of consent. Repeated dumps repeat entries: some processes wrote many dumps (up to 252 on "
                 "ai16_ios26_sysdiag and 36 on hc_ios26_sysdiag, while about half wrote one), so the "
                 "same entry can appear in many rows; the summary artifact "
                 "collapses them and is a labelled view over these rows. Entries In Dump is the number of "
                 "entries the dump held, counted over all its services. A dump with no entries (an empty object, or a service whose credential object is "
                 "empty) is collected but gives no row, and a dump whose body cannot be read as JSON "
                 "gives one row with the body in Authorization Record and every other field blank. An "
                 "empty result is not evidence that no permission was cached: only processes that wrote "
                 "a dump inside the log's window appear. Message shapes were read on iOS 26.6 and iOS "
                 "27.0 sysdiagnose logs natively decoded with unifiedlog_iterator; the way these records "
                 "appear in a 'log show' export was not examined. Those images are not in the public "
                 "corpus and no fixture from them is committed. On ai16_ios26_sysdiag (iOS 26.5.2) and "
                 "hc_ios26_sysdiag (iOS 26.6), read from tracev3 data, 518 and 331 dumps were collected "
                 "and 481 and 254 of them gave 542 and 278 rows; the other dumps held no entries. No body "
                 "failed to read as JSON and every authorization description matched the shape above. "
                 "Auth Right read Allowed, Limited, Denied or Unknown, Reason Entitled, User Consent, "
                 "Service Policy or None, Version 1 or 2, and Other Flags was blank except for 'Has "
                 "Prompted For Allow' on 4 rows on ai16_ios26_sysdiag. Most rows were "
                 "kTCCServiceAddressBook entries with Reason Entitled (381 of 542 and 230 of 278), "
                 "most written by processes outside app bundles (341 of 381 and 195 of 230) and "
                 "nearly all of the rest by processes in system app bundles. Both sysdiagnoses also held "
                 "TCC.db, which the Application Permissions artifact reads; it names the client and "
                 "gives a last modified time, while these dumps give the writing process and the dump "
                 "time. The dumps held Reason Entitled AddressBook entries for 42 distinct process image paths on "
                 "ai16_ios26_sysdiag and 38 on hc_ios26_sysdiag; TCC.db held AddressBook rows for 7 "
                 "clients on each. How the two sources relate "
                 "entry by entry is not established here. The test fixture is synthetic, with invented "
                 "process paths, PIDs and addresses.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "shield",
        "sample_data": {
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 542 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 278 rows",
        },
    },
    "logarchive_tcc_cache_summary": {
        "name": "logarchive TCC authorization cache summary",
        "description": "A collapsed view of the TCC authorization cache dumps: each distinct entry "
                       "(process, process ID, service, auth right, reason, version, other flags) once, "
                       "with the first and last dump that held it and the number of dumps.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-19",
        "last_update_date": "2026-10-19",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "A view over the rows of the logarchive TCC authorization cache dumps artifact, not a "
                 "change log. Two rows for the same process and service with different auth right, reason "
                 "or version mean that dumps held different content, not that the permission changed "
                 "between them: the dumps in between, or the dumps' own cache, may differ for reasons not "
                 "established here. First Dump and Last Dump are the record times, as stored, of the "
                 "earliest and latest dump holding the entry; Dumps is the number of dumps (distinct "
                 "Row Number and time) holding it and Entries the number of entries counted, which can be "
                 "larger when one dump holds the same description under more than one credential. The "
                 "credential and authorization object addresses are left out of the key, so entries that "
                 "differ only in address are merged. A process that restarted has a new Process ID and so a "
                 "new row. Dumps with no entries add no row, and an unreadable dump adds a row with blank "
                 "fields. Which dumps exist depends on the log window; absence of a service here does not "
                 "show that it was not cached. The test fixture is synthetic.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "shield",
        "sample_data": {
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 103 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 99 rows",
        },
    },
    "logarchive_location_state": {
        "name": "logarchive location manager state dumps",
        "description": "Statedump snapshots titled 'CLLocationManagerStateTracker', one row per dump: "
                       "the location manager flags and settings the dump logged, and the process that "
                       "wrote it. A dump is the state when it was written, not an event.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-19",
        "last_update_date": "2026-10-19",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Statedump records carry no subsystem or category, so they are found by the first line "
                 "of the message, 'title: CLLocationManagerStateTracker'. After two 'Object Type' lines "
                 "the body is a brace-delimited list of \"key\":value lines. Each column named after a "
                 "logged key (updatingLocation as Updating Location, and so on) holds the text after that "
                 "key's colon, as logged: booleans as true or false, numbers as written. Keys that have no "
                 "column of their own, including any a later release adds, are kept in Other Fields as "
                 "key: value pairs in the order logged, and a key the dump does not hold leaves its column "
                 "blank. If no key line can be read, Other Fields holds the body lines or, with no body, "
                 "the message as logged. No meaning is assigned to any value: the numbers in "
                 "previousAuthorizationStatus, activityType, desiredAccuracy and distanceFilter are not "
                 "translated, and previousAuthorizationStatus is the field of that name, not the "
                 "authorization in force. The dump does not name the application or the location manager "
                 "it describes. The only attribution is Process Image Path and Process ID, the process "
                 "that wrote the dump, as stored, Whether a dump describes one location manager or the whole process is not "
                 "established here; on the two corpus images no two dumps shared a time, process and "
                 "Process ID. A row with "
                 "updatingLocation true shows that state in the dump at that time. It is a lead; it does "
                 "not show that a position was obtained, stored or used, and the dump records no event "
                 "between dumps. Repeated dumps repeat state: some processes wrote many dumps (up to 1,764 on "
                 "ai16_ios26_sysdiag and 174 on hc_ios26_sysdiag), most of them with content identical "
                 "to an earlier dump, and the summary artifact collapses them. "
                 "Timestamp is the record time as stored, in UTC. An empty result is not evidence that no "
                 "process used location: only processes that wrote a dump inside the log's window "
                 "appear. Message shapes were read on iOS 26.6 and iOS 27.0 sysdiagnose logs natively "
                 "decoded with unifiedlog_iterator; the way these records appear in a 'log show' export "
                 "was not examined. Those images are not in the public corpus and no fixture from them is "
                 "committed. On ai16_ios26_sysdiag (iOS 26.5.2) and hc_ios26_sysdiag (iOS 26.6), read "
                 "from tracev3 data, 2,174 and 514 dumps came from 55 and 44 distinct process image paths. Every dump on "
                 "both held the 16 keys with columns and the same 12 others, which fill Other Fields on "
                 "every row, and no line that was not a key and value. Updating Location read true on 62 "
                 "and 42 rows; 12 of the 62 on ai16_ios26_sysdiag were written by processes in app bundles under "
                 "the user-installed application container, and none of the 42 on hc_ios26_sysdiag. The test fixture is "
                 "synthetic, with invented process paths, PIDs and values.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 2174 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 514 rows",
        },
    },
    "logarchive_location_state_summary": {
        "name": "logarchive location manager state summary",
        "description": "A collapsed view of the location manager state dumps: each distinct content "
                       "(process, process ID and the logged keys and values) once, with the first and "
                       "last dump that held it and the number of dumps.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-19",
        "last_update_date": "2026-10-19",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "A view over the rows of the logarchive location manager state dumps artifact, not a "
                 "change log. Two rows for one process with different content mean that dumps held "
                 "different content, not when or why it changed. First Dump and Last Dump are the record "
                 "times, as stored, of the earliest and latest dump with exactly that content; Dumps is "
                 "the number of dumps (distinct Row Number and time) with it. The dump does not name which location manager it describes, so a row groups dumps by "
                 "content; if one process wrote dumps for more than one manager with equal content, "
                 "they are merged. A process that restarted has a new Process ID and so a new row. The value columns are the same as in the dumps artifact. An empty result is not evidence that no process used "
                 "location. The test fixture is synthetic.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 119 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 156 rows",
        },
    },
    # ---- TCC authorization cache and location manager state dumps (end) ----
    "logarchive_urlopens": {
        "name": "logarchive URL and link opens",
        "description": "Unified log lines matching three URL-open markers: UIOpenURLAction "
                       "actions, openURLContexts scene calls, and launchservices reporting no "
                       "registered handler for a URL scheme. Each row is one log line, not one open.",
        "author": "@danjethh, @AlexisBrignoni, Claude",
        "creation_date": "2026-09-29",
        "last_update_date": "2026-10-14",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Each row is one log line, not one open. On hc_ios26_sysdiag three lines logged "
                 "within 0.16 seconds appear to describe one Notes widget launch: a com.apple.chrono "
                 "widget launch request carrying a UIOpenURLAction, SpringBoard sending "
                 "UIOpenURLAction to the Notes scene, and MobileNotes receiving it. The Process "
                 "Image Path column is the process that wrote the line, not always the app the URL "
                 "was sent to: SpringBoard wrote 4 of the 5 rows on that image, and the receiving "
                 "app is named in the message (an app<bundle id> or a sceneID starting with the "
                 "bundle id); on the MobileNotes row it is also the writing process. "
                 "The URL is logged unevenly. The chrono widget launch line held a URL in clear, "
                 "with a non-http scheme; that message ended at 1,029 characters on a letter with "
                 "no closing bracket, and if the line was longer, the rest is not in the parsed "
                 "log. The other UIOpenURLAction lines held no URL. The openURLContexts lines "
                 "(hc_ios17_2, written by Preferences as 'scene:openURLContexts:]: opening url "
                 "context') and the launchservices line held <private> in place of the value. "
                 "The launchservices line ('There is no registered handler for URL scheme', "
                 "hickman_ios14_sysdiag, written by lsd) names neither the requesting process nor "
                 "whether the request was an open or a check. openURLContexts is a UIKit method "
                 "name and may match lines that are not opens on other images. -canOpenURL: lines "
                 "are not matched by these markers. rodeo_ios17_sysdiag had no matching line. "
                 "Trace ID held no value on any row.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "link",
        "sample_data": {
            "hickman_ios14_sysdiag": "iOS 14.3 | 1 row",
            "hc_ios17_2": "iOS 17.2.1 | 2 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 0 rows; no matching line in the parsed log",
            "hc_ios26_sysdiag": "iOS 26.6 | 5 rows",
        },
    },
    "logarchive_capture_sessions": {
        "name": "logarchive camera and microphone capture sessions",
        "description": "Unified log lines from the camera capture daemon (subsystem "
                       "com.apple.cameracapture) recording a capture session being created, a "
                       "client calling start or stop, the session status changing, and the "
                       "client's own startRunning and stopRunning calls. Each row is one log "
                       "line, not one session. A start line is a lead; it does not establish "
                       "that audio or video was recorded.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-19",
        "last_update_date": "2026-10-19",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Lines are read from the table logarchive_artifacts builds. Kept: "
                 "FigCaptureSessionCreate, captureSession_StartRunning and _StopRunning, "
                 "captureSession_transitionToSessionStatus lines that carry a transition, "
                 "captureSession_didStopRunning lines reporting the stop, "
                 "FigCaptureSessionDetachFromClient, and the client-side -[AVCaptureSession "
                 "startRunning] and -[AVCaptureSession stopRunning] lines, whose Process Image "
                 "Path is the client process itself. The state lines that carry ClientStartedSession "
                 "are kept only when ClientStartedSession is 1 or a micStolen or cameraStolen flag "
                 "is 1; the state lines with all three at 0 are collected but not listed. "
                 "Client App ID and Client PID are read from the tag the daemon writes before the "
                 "message, in the form <object address[pid][app id]>, and from the 'Creating session "
                 "for PID' line; in the logs read (iOS 26.6 and 27.0 privately, and ai16_ios26_sysdiag) the "
                 "two PIDs agreed. "
                 "Session Object is that address as logged: it groups the lines of one session, but an "
                 "address can be reused, so compare the times as well. Cam/Audio, Background, Mic Stolen, "
                 "Camera Stolen, Runtime Error, Interruption Error and Session Status are copied as "
                 "logged; this artifact assigns no meaning to the numbers. Runtime Error, Interruption "
                 "Error and Session Status are read from the iOS 27.0 state lines; the "
                 "captureSession_updateRunningCondition state line on iOS 26.5.2 (ai16_ios26_sysdiag) "
                 "and on the iOS 26.6 log read carried none of the three, so they stay blank there. "
                 "In the iOS 27.0 log read Background, Mic Stolen, Camera Stolen, Runtime Error and "
                 "Interruption Error were identical on every row that carried them, all 0, and every "
                 "listed state line had Client Started Session 1 and Cam/Audio 1/0, so those columns "
                 "were uniform there. They stay because a different value is what this artifact "
                 "exists to surface: Camera Stolen read 1 on ai16_ios26_sysdiag (below), and the "
                 "other flags have read 1 only in the synthetic test fixture. "
                 "Timestamp is the time of the log record as stored, shown in UTC; no time inside a "
                 "message is used. "
                 "What a row does not establish: a client start line is the daemon's record of the "
                 "client's request, not of frames being recorded, and nothing here says whether anything "
                 "was saved. A system component can start a session on its own account: in the iOS 27.0 "
                 "log read, every state line with ClientStartedSession at 1 carried the app id of an "
                 "Apple system daemon (com.apple.biometrickitd), while the Camera app's state lines all "
                 "read 0 although its sessions were created. An empty result is not evidence that nothing was captured: the log "
                 "has a limited window and this artifact reads one daemon's lines. "
                 "Not covered: microphone capture that does not go through this daemon (audio sessions, "
                 "calls, voice recording) is not collected, and in no log read did the audio "
                 "flag or Mic Stolen read 1, so those two have been exercised only by the synthetic "
                 "test fixture. On ai16_ios26_sysdiag (iOS 26.5.2, read from tracev3 data) Camera "
                 "Stolen read 1 on 6 rows, all captureSession_updateRunningCondition lines for "
                 "com.apple.biometrickitd. On that image every row that carried a Client App ID (78 "
                 "of 102) named com.apple.biometrickitd; the other 24 were 'Creating session for "
                 "PID' lines with the same PID and client-side lines written by biometrickitd. No "
                 "row there came from a third-party app or the Camera app, although the import held "
                 "com.apple.cameracapture lines tagged with the Camera app id and lines written by a "
                 "third-party app, in client state and device selection shapes this artifact does not "
                 "collect. On hc_ios26_sysdiag "
                 "(iOS 26.6) the import held 1,140 com.apple.cameracapture lines and none in the "
                 "session or power-log shapes above. The com.apple.isp subsystem, written by the "
                 "camera hardware daemon (appleh*camerad) and by cameracaptured, is not collected: the "
                 "lines inspected were connection, ISP command, flicker-detector and similar "
                 "bookkeeping with the client PID redacted. "
                 "In the iOS 27.0 log read, FigFlashlightLocal (torch) lines from the same daemon and "
                 "subsystem outnumbered the session lines by a wide margin; neither corpus image held "
                 "that shape. They are not collected here, so a count of lines from that daemon is not a count of camera use; the "
                 "device-vendor lines (ClientIsActive, device usage counts, close timers) are also left "
                 "out because what they count is not established. Message shapes were read on "
                 "iOS 26.6 and iOS 27.0 sysdiagnose logs; those images are not in the public corpus and "
                 "no fixture from them is committed. The test fixture is synthetic, with invented app "
                 "IDs, PIDs and dates.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "camera",
        "sample_data": {
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 102 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 0 rows",
        },
    },
    "logarchive_capture_streaming": {
        "name": "logarchive camera streaming power events",
        "description": "Unified log lines from the camera capture daemon's "
                       "FigCaptureLogCameraStreamingPowerEvent function with the PID, application ID, "
                       "device type, streaming flag and port type as logged. Each row is one log "
                       "line.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-19",
        "last_update_date": "2026-10-19",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Fields are copied as logged and no meaning is assigned to the numbers. In the logs "
                 "read the streaming flag was logged as 1 and 0 and the application ID as <private>, "
                 "so the client has to be taken from the PID, for example by matching it with Client PID "
                 "in the capture sessions artifact; that match was not validated against a known capture. "
                 "In the iOS 27.0 log read the lines came in 1/0 pairs for a single device type and port "
                 "type, written for an Apple system daemon's session. A line records the daemon's power "
                 "event, not a saved recording. The related cpls_logCameraStreamingPowerEvents lines, "
                 "which carry a time inside the message, are not collected. Timestamp is the log record "
                 "time as stored, in UTC. An empty result is not evidence that the camera was not "
                 "streaming. In the iOS 27.0 log read Application ID (as logged) read <private>, Device Type "
                 "(as logged) 20 and Port Type (as logged) PortTypeFrontInfrared on every row, and Process "
                 "Image Path and Process ID held one value each. On ai16_ios26_sysdiag (iOS 26.5.2) "
                 "the 12 rows had the same shape: 6 with Streaming 1 and 6 with 0, all <private>, "
                 "20 and PortTypeFrontInfrared, and their PID matched the Client PID of that "
                 "image's com.apple.biometrickitd session lines. The test fixture is synthetic.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "video",
        "sample_data": {
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 12 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 0 rows",
        },
    },
    "logarchive_recording_indicator": {
        "name": "logarchive recording indicator lines",
        "description": "SpringBoard '[Recording Indicator]' log lines: the camera/microphone "
                       "activity-changed line, secure indicator layer creation, and the live "
                       "rendering assertion line. Each row is one log line.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-19",
        "last_update_date": "2026-10-19",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "The whole message, prefix included, is in the Event Message column as logged. "
                 "In the logs read the activity-changed line carried an empty set, so a row does not "
                 "say which sensor was active; a set with entries was not seen, and the synthetic "
                 "fixture's entry is invented to exercise the pass-through. Whether the on-screen "
                 "indicator was visible at a time is not established by these lines. The same prefix is "
                 "used by lines about layer opacity and brightness updates, which are not collected, "
                 "and by 'Should force high level layer' lines, which are not collected either. Use "
                 "this artifact to place indicator-related events in time, next to the capture "
                 "sessions and streaming events, not as proof of recording. Timestamp is the log "
                 "record time as stored, in UTC. An empty result is not evidence that the indicator "
                 "was not shown. Process Image Path held one value (SpringBoard) on every row in the "
                 "logs read. On hc_ios26_sysdiag (iOS 26.6) the one row was an activity-changed "
                 "line with an empty set. On ai16_ios26_sysdiag (iOS 26.5.2) all 51 '[Recording "
                 "Indicator]' lines were opacity or 'Should force high level layer' lines, so the "
                 "artifact gave no row. The layer creation and rendering assertion shapes were seen "
                 "only in the synthetic fixture.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "eye",
        "sample_data": {
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 0 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 1 row",
        },
    },
    "logarchive_app_snapshots": {
        "name": "logarchive app snapshots",
        "description": "Unified log entries from SpringBoard's com.apple.SplashBoard subsystem "
                       "saying that snapshot data was written to a file. The message "
                       "carries a bracketed identifier and the path of the .ktx file written",
        "author": "@Hexordia",
        "creation_date": "2026-10-20",
        "last_update_date": "2026-10-21",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Matches entries in the com.apple.SplashBoard subsystem whose message contains "
                 "'Snapshot data for'. On every tested image, every entry containing that text "
                 "came from that subsystem and from "
                 "/System/Library/CoreServices/SpringBoard.app/SpringBoard (1,810 entries across "
                 "seven images). The category was FileManifest on the iOS 17.2.1 to 26.6 images "
                 "and Snapshot on the iOS 12.4 image, so the filter does not test the category. "
                 "On iOS 17.2.1 and later each message read '<...> [identifier] Snapshot data for "
                 "<XBApplicationSnapshot ...> [identifier] written to file: <path>'. On iOS 12.4 it "
                 "read '[identifier] Snapshot data for <XBApplicationSnapshot ...> written to file: "
                 "<path>'. Whether the identifier is a bundle identifier is not established here. "
                 "Every path ended in .ktx, and none held <private>. Some paths contain spaces: on "
                 "17, 83, 1 and 7 rows of the iOS 17.2.1, 18.7, 26.5.2 and 26.6 images a folder "
                 "was named '<identifier> - {DEFAULT GROUP}'. "
                 "Paths were under a data container path "
                 "(/private/var/mobile/Containers/Data/Application/<UUID>/Library/SplashBoard/"
                 "Snapshots, or Library/Caches/Snapshots on iOS 12.4) or under "
                 "/var/mobile/Library/SplashBoard/Snapshots (/var/mobile/Library/Caches/Snapshots "
                 "on iOS 12.4); some were in a 'downscaled' subfolder. A row records that a file "
                 "was written, not that it still exists. Matching each logged path from /var/mobile/ "
                 "on against the extraction, 19 of 233 on the iOS "
                 "26.5.2 image, 83 of 429 on the iOS 18.7 image and 67 of 187 on the iOS 17.2.1 "
                 "image were present in the extraction. The App Snapshots artifact "
                 "(applicationSnapshots) reads .ktx files under those folders; it leaves out files "
                 "under 2500 bytes and files that do not decode. The identifier and path are not split "
                 "into their own columns; read them from Event Message. Process Image Path and "
                 "Subsystem held one value on every row of every tested image, and Category held "
                 "one value per image. Process ID held one value on six images and three values "
                 "on the iOS 12.4 image. Trace ID held no value on any row: rows read from "
                 "tracev3 data leave it empty. Only the direct tracev3 import was tested.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "screenshot",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 900 rows",
            "hc_ios17_2": "iOS 17.2.1 | 187 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 6 rows",
            "dexter_ios18": "iOS 18.3.2 | 32 rows",
            "iphone12_ios18": "iOS 18.7 | 429 rows",
            "hc_ios26": "iOS 26.5.2 | 233 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 23 rows",
        },
    },
    "logarchive_data_usage": {
        "name": "logarchive data usage",
        "description": "Unified log entries from symptomsd in the analytics category giving WiFi "
                       "and Cell in/out values for a name on a numbered flow; the values are "
                       "reported as logged",
        "author": "@Hexordia",
        "creation_date": "2026-10-21",
        "last_update_date": "2026-10-21",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Matches entries in the analytics category whose message contains 'Data Usage "
                 "for'. On every tested image those entries came from /usr/libexec/symptomsd in "
                 "the com.apple.symptomsd subsystem. Each message read 'Data Usage for <name> on "
                 "flow <number> - WiFi in/out: <n>/<n>, WiFi delta_in/delta_out: <n>/<n>, Cell "
                 "in/out: <n>/<n>, Cell delta_in/delta_out: <n>/<n>, RNF: <n>, subscriber tag: "
                 "<n>', followed on the iOS 18.3.2 to 26.6 images by ', total duration: <n>'. On "
                 "those images the name was followed by '(delegation: <name>)' on 12,902, "
                 "15,504, 14,554 and 4,095 rows (iOS 18.3.2, 18.7, 26.5.2 and 26.6). Some names "
                 "ended in '(viaNEHelper)' and some read '(null)'. The name is either a dotted "
                 "reverse-DNS-shaped string or a single word; what either names is not established. "
                 "None held <private>. What the in/out, delta, RNF, subscriber tag and duration "
                 "values count, and in what unit, is not established: the message gives no unit. "
                 "A flow number appeared on more than one row (24,593 rows held 14,841 distinct "
                 "flow numbers on the iOS 17.2.1 image). No counter is labelled Bluetooth; "
                 "Bluetooth appears only in the name, on 4, 6 and 7 rows of the iOS 17.2.1, "
                 "18.3.2 and 26.6 images. The iOS 12.4 image and the iOS 17.3 sysdiagnose held no "
                 "entry containing the text. CommCenter entries reading 'Data usage for "
                 "tethering' (2 and 4 on the iOS 17.2.1 and 26.5.2 images) match the text but not "
                 "the category and are not reported here. Network usage recorded in DataUsage.sqlite "
                 "is reported by the Data Usage artifact (get_DataUsage). Process Image Path, "
                 "Subsystem and Category held one value on every row of every tested image. "
                 "Process ID held one value on the iOS 18.7 and 26.5.2 images and two to four "
                 "values on the others. Trace ID held no value on any row: rows read from tracev3 "
                 "data leave it empty. Only the direct tracev3 import was tested.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "chart-line",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 24593 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 23400 rows",
            "iphone12_ios18": "iOS 18.7 | 23480 rows",
            "hc_ios26": "iOS 26.5.2 | 22242 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 6501 rows",
        },
    },
    "logarchive_lockdown_mode": {
        "name": "logarchive Lockdown Mode flag in Photos",
        "description": "Unified log entries from the Photos app (com.apple.photos.backend) that print an "
                       "isLockdownMode value while deciding whether Shared Albums are enabled; the value "
                       "is reported as logged",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Matches entries whose message contains 'isLockdownMode:'. Each message read "
                 "'Determining if Shared Albums enabled: Found <private> with: isEnabledForSharedStreams: "
                 "<YES|NO> isProvisionedForDataclass: <YES|NO> isEDUMode: <YES|NO> isLockdownMode: "
                 "<YES|NO>', written by the Photos app in the PhotoSharing category. The value is the "
                 "state the Photos code printed when it evaluated Shared Albums, so a row exists only "
                 "when that check ran; a day without a row says nothing about Lockdown Mode, and "
                 "a NO row is not evidence that the feature was never on at another time. Other logged "
                 "mentions of lockdown mode (for example the callservicesd line 'lockdownModeEnabled:') "
                 "print <private> in place of the value and are not matched. The unrelated lockdownd "
                 "service is not matched. Observed on two sysdiagnose logs of different devices: iOS 26.6.2 (8 matching "
                 "lines) and iOS 26.6 (2), all isLockdownMode: NO. No log from a device with the mode "
                 "turned on was available, so the YES form of the line is unverified on real data. Trace ID held no value on any "
                 "row. A third log (a second iOS 26.6 sysdiagnose of the first iOS 26.6 device, taken a day earlier) held 1 line, also NO. "
                 "On the iOS 26.6.2 log Subsystem, Category and Event Message each held one value on every row, the message being the same line each time. "
                 "Only the direct tracev3 import was tested.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "lock",
        "sample_data": {
            "local_ios26_6_2_sysdiag": "iOS 26.6.2 sysdiagnose | 8 rows",
            "local_ios26_6_sysdiag": "iOS 26.6 sysdiagnose | 2 rows",
            "local_ios26_6_sysdiag_b": "iOS 26.6 sysdiagnose | 1 row",
        },
    },
    "logarchive_passkey_store": {
        "name": "logarchive Safari passkey record loads",
        "description": "Unified log entries in which Safari's saved account store reports how many passkey "
                       "keychain records it loaded, from the personal keychain or a keychain group",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Matches entries in the com.apple.mobilesafari subsystem, Keychain category, whose message "
                 "contains 'passkey keychain records from'. The messages read '-[WBSSavedAccountStore "
                 "_fetchAndFilterPasskeysData]: Loaded <n> passkey keychain records from personal "
                 "keychain', the same with '_block_invoke' and 'from group <uuid>', and the variant "
                 "'recently deleted passkey keychain records'. The number is a count the store printed "
                 "when it loaded records; it is not a list of passkeys, names no site or account, and "
                 "can differ between loads. Loads are written when Safari or the Settings app "
                 "reads the saved accounts, so a day without a row says nothing about passkeys. "
                 "Writing process varied (MobileSafari 12, webbookmarksd 12, Preferences 3 of 27 rows on the "
                 "iOS 26.6.2 log; webbookmarksd 4 and AuthenticationServicesAgent 4 of 8 on the iOS 26.6 log). "
                 "Observed on two sysdiagnose logs of different devices. Other iOS versions were not tested. "
                 "A second iOS 26.6 log of the first iOS 26.6 device held 4 lines. Subsystem and Category held one value on every row, "
                 "which the match fixes, and on that 4-line log Process Image Path and Process ID also held one value on every row. "
                 "Trace ID held no value on any row. Only the direct tracev3 import was tested.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "key",
        "sample_data": {
            "local_ios26_6_2_sysdiag": "iOS 26.6.2 sysdiagnose | 27 rows",
            "local_ios26_6_sysdiag": "iOS 26.6 sysdiagnose | 8 rows",
            "local_ios26_6_sysdiag_b": "iOS 26.6 sysdiagnose | 4 rows",
        },
    },
    "logarchive_shortcut_actions": {
        "name": "logarchive background shortcut actions",
        "description": "Unified log entries from the background shortcut runner (com.apple.shortcuts, "
                       "RunningLifecycle) whose telemetry line names an actionID",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Matches entries in the com.apple.shortcuts subsystem, RunningLifecycle category, whose "
                 "message contains 'actionID='. The messages are signpost lines written by "
                 "BackgroundShortcutRunner and read 'Signpost ID: <id> - Signpost Name: <name> "
                 "enableTelemetry=YES actionID=<identifier> (signpost.telemetry:string...)'. The "
                 "identifier is a reverse-DNS-shaped string that, in the tested log, began with an "
                 "app's bundle identifier followed by an intent name. The line says that the runner "
                 "wrote a telemetry signpost naming that action; what triggered the run (an automation, "
                 "a shortcut, an app or a widget), whether the action completed and what it did are "
                 "not in the line. The other signpost lines of the runner in the same category carry "
                 "no actionID (54 of 60 in the tested log) and are not matched. Observed on two "
                 "sysdiagnose logs of different devices: iOS 26.6.2 had 6 matching lines naming two actions, 5 "
                 "for one and 1 for another; iOS 26.6 had none. Shortcuts run in the foreground by the Shortcuts app were not "
                 "observed and are not covered. Other iOS versions were not tested. Trace ID held no "
                 "value on any row. On the iOS 26.6.2 log Subsystem, Category and Process Image Path each held one value on every row "
                 "(the runner). Only the direct tracev3 import was tested.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "bolt",
        "sample_data": {
            "local_ios26_6_2_sysdiag": "iOS 26.6.2 sysdiagnose | 6 rows",
            "local_ios26_6_sysdiag": "iOS 26.6 sysdiagnose | 0 rows",
            "local_ios26_6_sysdiag_b": "iOS 26.6 sysdiagnose | 0 rows",
        },
    },
    "logarchive_vpn_state": {
        "name": "logarchive VPN connectivity state",
        "description": "Unified log entries from the Network Extension framework that print the VPN "
                       "connectivity state, as logged",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Matches entries in the com.apple.networkextension subsystem whose message contains "
                 "'VPN connectivity state is now'. The messages read 'VPN connectivity state is now "
                 "NEVPNConnectivityState<state>, visibility state is now <n>, does not use policy-based "
                 "routing'. The state word is NEVPNConnectivityManager's own value as logged. The line "
                 "does not name a VPN configuration, provider or server, and the process that "
                 "wrote it (Preferences or CommCenter in the tested log) is the one whose network "
                 "extension manager observed the change, not necessarily the one that started a "
                 "tunnel. Observed on one iOS 26.6.2 sysdiagnose log from a device with no VPN "
                 "configuration in its Network Extension store: 17 matching lines, all "
                 "NEVPNConnectivityStateDisconnected, and 17 on an iOS 26.6 log of a second device, "
                 "also all Disconnected. A second iOS 26.6 log of that second device, taken a day "
                 "earlier, held 55 lines: Disconnected 36, Connecting 9 and Disconnecting 10. The "
                 "Connected form was not observed, so what a connected tunnel logs is unverified on real "
                 "data. Other iOS versions were not tested. Subsystem held one value on every row, "
                 "Category was empty on every row, and on the 17-line logs Event Message held one value "
                 "on every row. Trace ID held no value on any row. Only the direct "
                 "tracev3 import was tested.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "shield-lock",
        "sample_data": {
            "local_ios26_6_2_sysdiag": "iOS 26.6.2 sysdiagnose | 17 rows; all Disconnected",
            "local_ios26_6_sysdiag": "iOS 26.6 sysdiagnose | 17 rows; all Disconnected",
            "local_ios26_6_sysdiag_b": "iOS 26.6 sysdiagnose | 55 rows; Disconnected 36, Connecting 9, Disconnecting 10",
        },
    },
}

import json
import os
import re
import shutil
import ijson
from pathlib import Path
from datetime import datetime, timedelta, timezone
from contextlib import closing
from scripts import unifiedlogs
from scripts.ilapfuncs import artifact_processor, get_file_path, \
    get_sqlite_db_records, logfunc, get_sysdiagnose_files

DATA_HEADERS = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID',
                'Subsystem', 'Category', 'Event Message', 'Trace ID')


_JSON_OFFSET = re.compile(r'([+-]\d{2})(\d{2})$')


def convert_to_utc(timestamp):
    """Parse the 'log show --style json' timestamp, e.g. 2026-03-14 10:00:00.100000-0500.

    The offset has no colon. datetime.fromisoformat() accepts that only from 3.11, and on
    3.10 it also takes a fraction of exactly 3 or 6 digits, so normalize both here rather
    than depend on the interpreter version.
    """
    normalized = _JSON_OFFSET.sub(r'\1:\2', timestamp)
    if '.' in normalized:
        whole, rest = normalized.split('.', 1)
        digits = len(rest) - len(rest.lstrip('0123456789'))
        normalized = f'{whole}.{rest[:digits][:6].ljust(6, "0")}{rest[digits:]}'
    return datetime.fromisoformat(normalized).astimezone(timezone.utc)


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
    to accept either of those in 3.11, so normalize both here rather than depending on the
    interpreter version.
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
    results = context.create_artifact_result(headers=DATA_HEADERS, source_path=source_path)

    query = '''
    SELECT *
    FROM logarchive
    WHERE (event_message LIKE '%Take screenshot%'
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
        OR (subsystem LIKE 'com.apple.SpringBoard' AND event_message LIKE 'UILocked:%')
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
        OR event_message LIKE '%Auto join association succeeded%'
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
        OR event_message LIKE '%VolumeIncreasePress%'
        OR event_message LIKE '%VolumeDecreasePress%'
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
        OR event_message LIKE '%Tethering is now disabled with%'
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
        OR (category LIKE 'ims'
            AND (event_message LIKE '%Incoming call %from %'
                 OR event_message LIKE '%Alerting user of incoming call%'
                 OR event_message LIKE '%Sending Incoming Call notification%'))
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
        OR event_message LIKE '%send tapToWake%'
        OR event_message LIKE '%tapToWakeDidRecognize%'
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
        -- logarchive_battery_center_sources and logarchive_battery_center_devices
        OR (subsystem = 'com.apple.BatteryCenter'
            AND (event_message LIKE '%Found power source: {%'
                 OR event_message LIKE '%Found device: <BCBatteryDevice:%'))
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
        OR event_message LIKE 'Discoverable mode changed from%'
        OR event_message LIKE 'Hashes in validation record:%'
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
                 OR event_message LIKE 'RECEIVED rawVolume%Press%'
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
        OR (process_image_path LIKE '%/usr/libexec/installd%' AND event_message LIKE '%Made container live for%')
        -- logarchive_device_id
        OR (subsystem LIKE '%com.apple.networkrelay%' AND process_image_path LIKE '%/usr/libexec/terminusd%' AND event_message LIKE '%Starting terminusd%')
        OR (process_image_path LIKE '%/usr/libexec/sharingd%' AND event_message LIKE '%Device Information:%')
        OR (process_image_path LIKE '%/usr/libexec/securityd%' AND category LIKE '%accountLogState%' AND event_message LIKE '%name:%')
        -- logarchive_wake_source
        OR (subsystem LIKE '%com.apple.SpringBoard%' AND event_message LIKE 'wake source:%')
        -- logarchive_weather
        OR ((category = 'WeatherService' OR category = 'ForecastWeatherWidget') AND event_message LIKE '%About to fetch%')
        OR (category LIKE 'ForecastWeatherWidget' AND event_message LIKE '%Data operation succeeded%')
        OR (category LIKE 'WeatherService' AND (event_message LIKE '%Successfully built%' OR event_message LIKE '%Got response for fetch of%'))
        OR (category LIKE 'WeatherWidget' AND event_message LIKE '%successfully built%')
        -- logarchive_family_hotspot
        OR event_message LIKE '%Family Hotspot State%'
        -- logarchive_urlopens. Collected here as well as filtered in the dependent
        -- artifact, or the rows never reach the table it reads.
        OR event_message LIKE '%UIOpenURLAction%'
        OR event_message LIKE '%openURLContexts%'
        OR event_message LIKE '%no registered handler for URL scheme%'
        -- (statedump markers begin) logarchive_tcc_cache, logarchive_tcc_cache_summary,
        -- logarchive_location_state and logarchive_location_state_summary. A statedump
        -- record has no subsystem or category, and this table does not keep the event
        -- type, so the first line of the message ('title: ...') is the only handle. The
        -- patterns are anchored at the start of the message and must stay collected here
        -- as well as filtered in the dependent artifacts, or the rows never reach the table
        -- they read.
        OR event_message LIKE 'title: TCC Authorization Cache%'
        OR event_message LIKE 'title: CLLocationManagerStateTracker%'
        -- (statedump markers end)
        -- logarchive_charging_state
        OR (process_image_path LIKE '%/powerd' AND event_message LIKE 'handleChargingStateUpdate %')
        -- logarchive_capture_sessions and logarchive_capture_streaming. Collected here as
        -- well as filtered in the dependent artifacts, or the rows never reach the table
        -- they read. The subsystem condition keeps this to the capture daemon's session
        -- and power-log lines: in the iOS 27.0 log read, the same subsystem carried tens of
        -- thousands of torch (FigFlashlightLocal) and device-vendor lines that no marker below
        -- matches. The
        -- ClientStartedSession state lines are collected whole; the dependent artifact
        -- lists only those with a start or a stolen flag set.
        OR (subsystem = 'com.apple.cameracapture'
            AND (event_message LIKE '%FigCaptureSessionCreate:%'
                 OR event_message LIKE '%captureSession_StartRunning:%'
                 OR event_message LIKE '%captureSession_StopRunning:%'
                 OR event_message LIKE '%captureSession_transitionToSessionStatus:%'
                 OR event_message LIKE '%captureSession_didStopRunning:%'
                 OR event_message LIKE '%FigCaptureSessionDetachFromClient%'
                 OR event_message LIKE '%-[AVCaptureSession startRunning]%'
                 OR event_message LIKE '%-[AVCaptureSession stopRunning]%'
                 OR event_message LIKE '%ClientStartedSession:%'
                 OR event_message LIKE '%FigCaptureLogCameraStreamingPowerEvent:%'))
        -- logarchive_recording_indicator
        OR (subsystem = 'com.apple.SpringBoard'
            AND (event_message LIKE '%[Recording Indicator] Active camera/microphone activity changed%'
                 OR event_message LIKE '%[Recording Indicator] creating secure indicator layer%'
                 OR event_message LIKE '%[Recording Indicator] updating live rendering assertion%'))
        -- logarchive_app_snapshots
        OR (subsystem LIKE 'com.apple.SplashBoard' AND event_message LIKE '%Snapshot data for%')
        -- logarchive_data_usage
        OR (category LIKE 'analytics' AND event_message LIKE '%Data Usage for%')
        -- logarchive_lockdown_mode
        OR (subsystem LIKE 'com.apple.photos.backend' AND event_message LIKE '%isLockdownMode:%')
        -- logarchive_passkey_store
        OR (subsystem LIKE 'com.apple.mobilesafari' AND event_message LIKE '%passkey keychain records from%')
        -- logarchive_shortcut_actions
        OR (subsystem = 'com.apple.shortcuts' AND category = 'RunningLifecycle' AND event_message LIKE '%actionID=%')
        -- logarchive_vpn_state
        OR (subsystem = 'com.apple.networkextension' AND event_message LIKE '%VPN connectivity state is now%')
    )
    '''

    with closing(unifiedlogs.filtered_records(source_path, query)) as rows:
        results.extend(rows)
    return results

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
    
    data_list = _report_rows(get_sqlite_db_records(source_path, query))
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
    
    data_list = _report_rows(get_sqlite_db_records(source_path, query))
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    
    return data_headers, data_list, source_path

LAUNCHING_APPLICATION = re.compile(
    r'Launching application (?P<bundle>\S+) from icon \S+, location: (?P<location>\S+)')
ALLOWING_TAP = re.compile(r"Allowing tap for icon view '(?P<bundle>[^']*)'")


def _launch_fields(message):
    """The application and icon location a SpringBoard launch entry names, as written."""
    message = message or ''
    match = LAUNCHING_APPLICATION.search(message)
    if match:
        return match.group('bundle'), match.group('location')
    match = ALLOWING_TAP.search(message)
    if match:
        return match.group('bundle'), ''
    return '', ''


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
    
    for record in _report_rows(get_sqlite_db_records(source_path, query)):
        data_list.append((record[0],) + _launch_fields(record[6]) + tuple(record[1:]))
    data_headers = (('Timestamp', 'datetime'), 'Application (as stored)', 'Icon Location (as stored)', 'Row Number',
                    'Process Image Path', 'Process ID', 'Subsystem', 'Category', 'Event Message',
                    'Trace ID')

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
    
    data_list = _report_rows(get_sqlite_db_records(source_path, query))
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
        OR event_message LIKE '%Tethering is now disabled with%'
        OR event_message LIKE '%Received notification that wireless modem state changed%'
        OR event_message LIKE '%Previous tethering state was%'
    '''
    
    data_list = _report_rows(get_sqlite_db_records(source_path, query))
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
    
    data_list = _report_rows(get_sqlite_db_records(source_path, query))
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
        OR (subsystem LIKE 'com.apple.SpringBoard' AND event_message LIKE 'UILocked:%')
    '''
    
    data_list = _report_rows(get_sqlite_db_records(source_path, query))
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
        OR event_message LIKE '%Auto join association succeeded%'
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
    
    data_list = _report_rows(get_sqlite_db_records(source_path, query))
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
    
    data_list = _report_rows(get_sqlite_db_records(source_path, query))
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
        OR event_message LIKE '%VolumeIncreasePress%'
        OR event_message LIKE '%VolumeDecreasePress%'
        OR event_message LIKE '%Volume active%'
        OR event_message LIKE '%PlaybackQueueInvalidation%'
        OR event_message LIKE '%volumeValueDidChange%'
    '''
    
    data_list = _report_rows(get_sqlite_db_records(source_path, query))
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


_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def _report_time(value):
    """The table's epoch seconds as a UTC datetime; anything else as stored."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            return _EPOCH + timedelta(seconds=value)
        except (OverflowError, ValueError):
            return value
    return value


def _report_rows(records):
    """Table rows with the leading timestamp column as a datetime.

    The logarchive_artifacts table holds the timestamp as epoch seconds, which is what
    the HTML report, the TSV export and the timeline would print. Handed a datetime they
    print a date and time, and LAVA stores the same epoch seconds it did before.
    """
    return [(_report_time(record[0]),) + tuple(record[1:]) for record in records]


def _artifacts_table_records(context, where_clause, report_time=True):
    """Rows from the logarchive_artifacts table matching where_clause.

    Shared by the artifacts added in the 2026-08-01 predicate survey. Each one is a
    filter over the table the logarchive_artifacts artifact materializes, exactly like
    the older artifacts above; the WHERE fragment is the only thing that varies.

    report_time=False returns the rows as stored. The lava_only artifacts use it: they
    write no report, so the conversion would only be undone on the way into LAVA.
    """
    source_path = get_file_path(context.get_files_found(), '_lava_artifacts.db')
    query = f'SELECT * FROM logarchive_artifacts WHERE {where_clause}'
    records = get_sqlite_db_records(source_path, query)
    data_list = _report_rows(records) if report_time else list(records)
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
        OR (category LIKE 'ims'
            AND (event_message LIKE '%Incoming call %from %'
                 OR event_message LIKE '%Alerting user of incoming call%'
                 OR event_message LIKE '%Sending Incoming Call notification%'))
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
    ''', report_time=False)

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
    ''', report_time=False)

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
        OR event_message LIKE '%send tapToWake%'
        OR event_message LIKE '%tapToWakeDidRecognize%'
        OR event_message LIKE '%AttentionAwareness.Touch%'
        OR event_message LIKE '%Touch entered%'
    ''', report_time=False)

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


# Battery Center writes each power source as an NSDictionary description ('key = value;' lines
# between braces) and each device as '<BCBatteryDevice: 0x...; key = value; ...>'. The columns
# are the keys seen on the tested iOS images; any other key goes to Other Values.

_BC_PAIR = re.compile(r'^\s*("(?:[^"\\]|\\.)*"|[^\s=;"]+)\s*=\s*("(?:[^"\\]|\\.)*"|[^;"]*);\s*$')
_BC_OPEN = re.compile(r'^("(?:[^"\\]|\\.)*"|[^\s=;"]+)\s*=\s*([{(])$')
_BC_ESCAPE = re.compile(r'\\(U[0-9a-fA-F]{4}|.)', re.DOTALL)
_BC_ESCAPED = {'n': '\n', 't': '\t', 'r': '\r'}
_BC_DEVICE = re.compile(r'Found device: <BCBatteryDevice: 0x[0-9a-fA-F]+; (.*?);?\s*>\s*$', re.DOTALL)
_BC_DEVICE_SPLIT = re.compile(r'; (?=\w+ ?=)')
_BC_DEVICE_PAIR = re.compile(r'^(\w+) ?= ?(.*)$', re.DOTALL)

_BC_SOURCE_KEYS = ('Name', 'Type', 'Transport Type', 'Power Source State', 'Current Capacity',
                   'Max Capacity', 'Is Charging', 'Is Charged', 'Is Finishing Charge',
                   'Is Present', 'Raw External Connected', 'Show Charging UI',
                   'Play Charging Chime', 'Cycle count', 'Accessory Identifier',
                   'Accessory Category', 'Vendor ID', 'Power Source ID')
_BC_DEVICE_KEYS = ('name', 'groupName', 'vendor', 'modelNumber', 'percentCharge', 'charging',
                   'connected', 'internal', 'poweredSoureState', 'transportType',
                   'accessoryIdentifier', 'accessoryCategory', 'identifier', 'productIdentifier')


CHARGING_STATE_UPDATE = re.compile(
    r'handleChargingStateUpdate State:(?P<state>.+?) VBUS:(?P<vbus>\S*) UISOC:(?P<uisoc>\S*) '
    r'CHNC:(?P<chnc>\S*) Type:(?P<type>\S*)(?: TLC:(?P<tlc>.*?))?\s*$')


@artifact_processor
def logarchive_charging_state(context):
    _headers, records, source_path = _artifacts_table_records(context, """
        process_image_path LIKE '%/powerd' AND event_message LIKE 'handleChargingStateUpdate %'
    """, report_time=False)
    data_list = []
    for record in records:
        message = record['event_message'] or ''
        match = CHARGING_STATE_UPDATE.match(message)
        fields = (match.group('state'), match.group('vbus'), match.group('uisoc'),
                  match.group('chnc'), match.group('type'), match.group('tlc') or '') if match \
            else ('',) * 6
        data_list.append((_report_time(record['timestamp']),) + fields
                         + (message, record['process_image_path'], record['process_id'],
                            record['row_number']))
    data_headers = (('Timestamp', 'datetime'), 'State', 'VBUS (as stored)', 'UISOC (as stored)',
                    'CHNC (as stored)', 'Type (as stored)', 'TLC (as stored)', 'Event Message',
                    'Process Image Path', 'Process ID', 'Row Number')
    return data_headers, data_list, source_path


# ---- Statedump artifacts: TCC authorization cache and location manager state (begin) ----
# A statedump is the state a process wrote at one instant. The record has no subsystem or category
# and the logarchive table does not keep its event type, so each dump is found by the first line of
# its message. The WHERE fragments below must stay within the markers logarchive_artifacts collects
# (a test checks every pattern appears there), because these artifacts only read the table that
# query builds.
TCC_CACHE_WHERE = "event_message LIKE 'title: TCC Authorization Cache%'"
LOCATION_STATE_WHERE = "event_message LIKE 'title: CLLocationManagerStateTracker%'"

# The credential and the authorization record are text descriptions: '<Credential (0x...) | Requestor>'
# and '<Authorization Record (0x...) | Service: S, AuthRight: A, Reason: R, Version: V, [flags,] >'.
TCC_ADDRESS = re.compile(r'\((0x[0-9A-Fa-f]+)\)')
TCC_AUTH_RECORD = re.compile(
    r'^<Authorization Record \((?P<address>0x[0-9A-Fa-f]+)\) \| Service: (?P<service>[^,]*), '
    r'AuthRight: (?P<right>[^,]*), Reason: (?P<reason>[^,]*), Version: (?P<version>[^,]*),'
    r'(?P<rest>.*)>$', re.DOTALL)

TCC_CACHE_HEADERS = (
    ('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID',
    'Service (as logged)', 'Credential Object Address', 'Authorization Object Address',
    'Auth Right (as logged)', 'Reason (as logged)', 'Version (as logged)',
    'Other Flags (as logged)', 'Entries In Dump', 'Authorization Record (as logged)')

TCC_CACHE_SUMMARY_HEADERS = (
    ('First Dump', 'datetime'), ('Last Dump', 'datetime'), 'Dumps', 'Entries',
    'Process Image Path', 'Process ID', 'Service (as logged)', 'Auth Right (as logged)',
    'Reason (as logged)', 'Version (as logged)', 'Other Flags (as logged)')

# '"key": value' lines of a CLLocationManagerStateTracker dump. The body is not valid JSON (the last
# value is followed by a comma), so it is read line by line.
LOCATION_KEY_VALUE = re.compile(r'^\s*"([^"]+)"\s*:\s*(.*?)\s*,?\s*$')
# (logged key, column header) in column order. A key not listed goes to Other Fields.
LOCATION_COLUMNS = (
    ('updatingLocation', 'Updating Location (as logged)'),
    ('requestingLocation', 'Requesting Location (as logged)'),
    ('updatingHeading', 'Updating Heading (as logged)'),
    ('updatingRanging', 'Updating Ranging (as logged)'),
    ('requestingRanging', 'Requesting Ranging (as logged)'),
    ('allowsBackgroundLocationUpdates', 'Allows Background Location Updates (as logged)'),
    ('showsBackgroundLocationIndicator', 'Shows Background Location Indicator (as logged)'),
    ('paused', 'Paused (as logged)'),
    ('batchingLocation', 'Batching Location (as logged)'),
    ('limitsPrecision', 'Limits Precision (as logged)'),
    ('dynamicAccuracyReductionEnabled', 'Dynamic Accuracy Reduction Enabled (as logged)'),
    ('previousAuthorizationStatusValid', 'Previous Authorization Status Valid (as logged)'),
    ('previousAuthorizationStatus', 'Previous Authorization Status (as logged)'),
    ('desiredAccuracy', 'Desired Accuracy (as logged)'),
    ('distanceFilter', 'Distance Filter (as logged)'),
    ('activityType', 'Activity Type (as logged)'),
)
LOCATION_STATE_HEADERS = (
    ('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID',
    *(header for _key, header in LOCATION_COLUMNS), 'Other Fields (as logged)')
LOCATION_STATE_SUMMARY_HEADERS = (
    ('First Dump', 'datetime'), ('Last Dump', 'datetime'), 'Dumps', 'Process Image Path',
    'Process ID', *(header for _key, header in LOCATION_COLUMNS), 'Other Fields (as logged)')


def _statedump_body(message):
    """The text of a statedump message from its first line that begins with a brace.

    Statedump messages are a title line, two 'Object Type:' lines and then the body. Returns ''
    when no line begins with a brace, so the caller can keep the whole message instead.
    """
    lines = str(message or '').split('\n')
    for index, line in enumerate(lines):
        if line.lstrip().startswith('{'):
            return '\n'.join(lines[index:])
    return ''


def _logged_text(value):
    return value if isinstance(value, str) else json.dumps(value)


def _tcc_cache_entries(message):
    """The authorization entries of a TCC Authorization Cache dump, or None when unreadable.

    None means the body is missing or is not a JSON object; the caller then keeps the text as
    logged. An empty list is a dump that holds no entries. Each entry is a dict of the service
    (the JSON key), the two object addresses, the auth right, reason, version and any text after
    the version, and the authorization description; a description of another shape leaves its
    fields blank and is kept whole.
    """
    try:
        cache = json.loads(_statedump_body(message))
    except (ValueError, RecursionError):
        return None
    if not isinstance(cache, dict):
        return None
    entries = []
    for service, credentials in cache.items():
        if not isinstance(credentials, dict):
            credentials = {'': credentials}
        for credential, record in credentials.items():
            entry = dict.fromkeys(('credential', 'authorization', 'right', 'reason', 'version', 'flags'), '')
            entry['service'] = service
            entry['record'] = _logged_text(record)
            address = TCC_ADDRESS.search(str(credential))
            entry['credential'] = address.group(1) if address else ''
            parsed = TCC_AUTH_RECORD.match(entry['record'])
            if parsed:
                entry['authorization'] = parsed.group('address')
                entry['right'] = parsed.group('right').strip()
                entry['reason'] = parsed.group('reason').strip()
                entry['version'] = parsed.group('version').strip()
                entry['flags'] = parsed.group('rest').strip().strip(',').strip()
            entries.append(entry)
    return entries


def _location_state_fields(message):
    """The fields of a CLLocationManagerStateTracker dump: (column values, other fields).

    Column values are in LOCATION_COLUMNS order, '' for a key the dump does not hold. Other
    Fields lists the remaining keys as 'key: value' in the order logged, then any body line that
    is not a key and value, joined with '; '. A message with no body is kept whole there.
    """
    body = _statedump_body(message)
    pairs = []
    leftover = []
    for line in body.split('\n'):
        match = LOCATION_KEY_VALUE.match(line)
        if match:
            pairs.append((match.group(1), match.group(2)))
        elif line.strip() not in ('', '{', '}'):
            leftover.append(line.strip())
    known = {key for key, _header in LOCATION_COLUMNS}
    values = {}
    other = []
    for key, value in pairs:
        if key in known and key not in values:
            values[key] = value
        else:
            other.append(f'{key}: {value}')
    other.extend(leftover)
    if not body:
        other = [str(message or '').strip()]
    return tuple(values.get(key, '') for key, _header in LOCATION_COLUMNS), '; '.join(other)


def _widen_range(group, timestamp):
    """Move a group's first and last record time outwards; a time that is not a number is ignored."""
    if isinstance(timestamp, (int, float)) and not isinstance(timestamp, bool):
        group['first'] = timestamp if group['first'] is None else min(group['first'], timestamp)
        group['last'] = timestamp if group['last'] is None else max(group['last'], timestamp)


@artifact_processor
def logarchive_tcc_cache(context):
    source_path = get_file_path(context.get_files_found(), '_lava_artifacts.db')
    query = f'SELECT * FROM logarchive_artifacts WHERE {TCC_CACHE_WHERE}'
    data_list = []
    for record in get_sqlite_db_records(source_path, query):
        message = record['event_message']
        entries = _tcc_cache_entries(message)
        if entries is None:
            body = _statedump_body(message)
            data_list.append((_report_time(record['timestamp']), record['row_number'],
                              record['process_image_path'], record['process_id'],
                              '', '', '', '', '', '', '', '', body or str(message or '')))
            continue
        for entry in entries:
            data_list.append((
                _report_time(record['timestamp']), record['row_number'], record['process_image_path'],
                record['process_id'], entry['service'], entry['credential'], entry['authorization'],
                entry['right'], entry['reason'], entry['version'], entry['flags'], len(entries),
                entry['record']))
    return TCC_CACHE_HEADERS, data_list, source_path


@artifact_processor
def logarchive_tcc_cache_summary(context):
    source_path = get_file_path(context.get_files_found(), '_lava_artifacts.db')
    query = f'SELECT * FROM logarchive_artifacts WHERE {TCC_CACHE_WHERE}'
    groups = {}
    for record in get_sqlite_db_records(source_path, query):
        entries = _tcc_cache_entries(record['event_message'])
        if entries is None:
            entries = [dict.fromkeys(('service', 'right', 'reason', 'version', 'flags'), '')]
        dump = (record['row_number'], record['timestamp'])
        for entry in entries:
            key = (record['process_image_path'], record['process_id'], entry['service'],
                   entry['right'], entry['reason'], entry['version'], entry['flags'])
            group = groups.setdefault(key, {'first': None, 'last': None, 'dumps': set(), 'entries': 0})
            _widen_range(group, record['timestamp'])
            group['dumps'].add(dump)
            group['entries'] += 1
    data_list = [(_report_time(group['first']), _report_time(group['last']), len(group['dumps']),
                  group['entries'], key[0], key[1], key[2], key[3], key[4], key[5], key[6])
                 for key, group in groups.items()]
    return TCC_CACHE_SUMMARY_HEADERS, data_list, source_path


@artifact_processor
def logarchive_location_state(context):
    source_path = get_file_path(context.get_files_found(), '_lava_artifacts.db')
    query = f'SELECT * FROM logarchive_artifacts WHERE {LOCATION_STATE_WHERE}'
    data_list = []
    for record in get_sqlite_db_records(source_path, query):
        values, other = _location_state_fields(record['event_message'])
        data_list.append((_report_time(record['timestamp']), record['row_number'],
                          record['process_image_path'], record['process_id']) + values + (other,))
    return LOCATION_STATE_HEADERS, data_list, source_path


@artifact_processor
def logarchive_location_state_summary(context):
    source_path = get_file_path(context.get_files_found(), '_lava_artifacts.db')
    query = f'SELECT * FROM logarchive_artifacts WHERE {LOCATION_STATE_WHERE}'
    groups = {}
    for record in get_sqlite_db_records(source_path, query):
        values, other = _location_state_fields(record['event_message'])
        key = (record['process_image_path'], record['process_id'], values, other)
        group = groups.setdefault(key, {'first': None, 'last': None, 'dumps': set()})
        _widen_range(group, record['timestamp'])
        group['dumps'].add((record['row_number'], record['timestamp']))
    data_list = [(_report_time(group['first']), _report_time(group['last']), len(group['dumps']),
                  key[0], key[1]) + key[2] + (key[3],)
                 for key, group in groups.items()]
    return LOCATION_STATE_SUMMARY_HEADERS, data_list, source_path
# ---- Statedump artifacts: TCC authorization cache and location manager state (end) ----


def _bc_unquote(text):
    """A value or key of an NSDictionary description without its quotes and escapes."""
    text = text.strip()
    if len(text) < 2 or text[0] != '"' or text[-1] != '"':
        return text

    def unescape(match):
        token = match.group(1)
        if token[0] == 'U' and len(token) == 5:
            return chr(int(token[1:], 16))
        return _BC_ESCAPED.get(token, token)
    return _BC_ESCAPE.sub(unescape, text[1:-1])


def _bc_source_pairs(message):
    """(pairs, leftover) of a 'Found power source: {...}' entry; leftover is what did not parse.

    A value that is itself a dictionary or a list spans several lines. It is kept as one
    value, its lines as logged, so a key inside it is never read as a key of the power
    source. The log cuts a long entry short, so the closing brace is not required: what was
    logged before the cut is still split, and a line cut in half goes to leftover.
    """
    start = message.find('{')
    if start < 0:
        return [], message.strip()
    pairs = []
    leftover = []
    key = None      # the key of the nested value being read, if any
    opener = ''
    depth = 0
    lines = []
    for line in message[start + 1:].splitlines():
        text = line.strip()
        if not text:
            continue
        if key is not None:
            if text[-1] in '{(':
                depth += 1
            elif text.rstrip(';') in ('}', ')'):
                if depth == 0:
                    pairs.append((key, opener + ' '.join(lines) + text.rstrip(';')))
                    key = None
                    continue
                depth -= 1
            lines.append(text)
            continue
        if text == '}':
            break
        match = _BC_OPEN.match(text)
        if match:
            key, opener, depth, lines = _bc_unquote(match.group(1)), match.group(2), 0, []
            continue
        match = _BC_PAIR.match(line)
        if match:
            pairs.append((_bc_unquote(match.group(1)), _bc_unquote(match.group(2))))
        else:
            leftover.append(text)
    if key is not None:
        pairs.append((key, opener + ' '.join(lines)))
    return pairs, ' '.join(leftover)


def _bc_device_pairs(message):
    """(pairs, leftover) of a 'Found device: <BCBatteryDevice: ...>' entry."""
    match = _BC_DEVICE.search(message)
    if not match:
        return [], message.strip()
    pairs = []
    leftover = []
    for piece in _BC_DEVICE_SPLIT.split(match.group(1)):
        pair = _BC_DEVICE_PAIR.match(piece)
        if pair:
            pairs.append((pair.group(1), pair.group(2).strip()))
        else:
            leftover.append(piece.strip())
    return pairs, '; '.join(leftover)


def _bc_row(pairs, leftover, shown_keys):
    """The shown keys' values in order, then every pair not shown and anything unparsed."""
    shown = {}
    other = []
    for key, value in pairs:
        if key in shown_keys and key not in shown:
            shown[key] = value
        else:
            other.append(f'{key} = {value}')
    if leftover:
        other.append(leftover)
    return tuple(shown.get(key, '') for key in shown_keys) + ('; '.join(other),)


def _bc_entries(context, where_clause, pairs_of, shown_keys):
    # As stored, so the rows can still be read by column name; the time is converted below.
    _headers, records, source_path = _artifacts_table_records(context, where_clause,
                                                              report_time=False)
    data_list = []
    for record in records:
        pairs, leftover = pairs_of(record['event_message'] or '')
        data_list.append((_report_time(record['timestamp']),) + _bc_row(pairs, leftover, shown_keys)
                         + (record['process_image_path'], record['process_id'],
                            record['row_number']))
    return data_list, source_path


@artifact_processor
def logarchive_battery_center_sources(context):
    data_list, source_path = _bc_entries(context, """
        subsystem = 'com.apple.BatteryCenter' AND event_message LIKE '%Found power source: {%'
    """, _bc_source_pairs, _BC_SOURCE_KEYS)
    data_headers = (('Timestamp', 'datetime'),) + _BC_SOURCE_KEYS + (
        'Other Values', 'Process Image Path', 'Process ID', 'Row Number')
    return data_headers, data_list, source_path


@artifact_processor
def logarchive_battery_center_devices(context):
    data_list, source_path = _bc_entries(context, """
        subsystem = 'com.apple.BatteryCenter'
        AND event_message LIKE '%Found device: <BCBatteryDevice:%'
    """, _bc_device_pairs, _BC_DEVICE_KEYS)
    data_headers = (('Timestamp', 'datetime'), 'Name', 'Group Name', 'Vendor', 'Model Number',
                    'Percent Charge', 'Charging', 'Connected', 'Internal', 'Power Source State',
                    'Transport Type', 'Accessory Identifier', 'Accessory Category', 'Identifier',
                    'Product Identifier', 'Other Values', 'Process Image Path', 'Process ID',
                    'Row Number')
    return data_headers, data_list, source_path

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
        OR event_message LIKE 'Discoverable mode changed from%'
        OR event_message LIKE 'Hashes in validation record:%'
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
                 OR event_message LIKE 'RECEIVED rawVolume%Press%'
                 OR event_message LIKE 'SOS button gesture: press type=%'))
    ''')

@artifact_processor
def logarchive_orientation(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%Received orientation%'
        OR event_message LIKE '%Gesture notification:%'
        OR event_message LIKE '%[TTW] Orientation changed%'
    ''', report_time=False)

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
        OR (process_image_path LIKE '%/usr/libexec/installd%' AND event_message LIKE '%Made container live for%')
    ''')

@artifact_processor
def logarchive_device_id(context):
    return _artifacts_table_records(context, '''
        (subsystem LIKE '%com.apple.networkrelay%' AND process_image_path LIKE '%/usr/libexec/terminusd%' AND event_message LIKE '%Starting terminusd%')
        OR (process_image_path LIKE '%/usr/libexec/sharingd%' AND event_message LIKE '%Device Information:%')
        OR (process_image_path LIKE '%/usr/libexec/securityd%' AND category LIKE '%accountLogState%' AND event_message LIKE '%name:%')
    ''')


@artifact_processor
def logarchive_wake_source(context):
    return _artifacts_table_records(context, '''
        (subsystem LIKE '%com.apple.SpringBoard%' AND event_message LIKE 'wake source:%')
    ''')

@artifact_processor
def logarchive_weather(context):
    return _artifacts_table_records(context, '''
        ((category = 'WeatherService' OR category = 'ForecastWeatherWidget') AND event_message LIKE '%About to fetch%')
        OR (category LIKE 'ForecastWeatherWidget' AND event_message LIKE '%Data operation succeeded%')
        OR (category LIKE 'WeatherService' AND (event_message LIKE '%Successfully built%' OR event_message LIKE '%Got response for fetch of%'))
        OR (category LIKE 'WeatherWidget' AND event_message LIKE '%successfully built%')
    ''')
    
@artifact_processor
def logarchive_family_hotspot(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%Family Hotspot State%'
    ''')


@artifact_processor
def logarchive_urlopens(context):
    return _artifacts_table_records(context, '''
        event_message LIKE '%UIOpenURLAction%'
        OR event_message LIKE '%openURLContexts%'
        OR event_message LIKE '%no registered handler for URL scheme%'
    ''')


@artifact_processor
def logarchive_app_snapshots(context):
    return _artifacts_table_records(context, '''
        (subsystem LIKE 'com.apple.SplashBoard' AND event_message LIKE '%Snapshot data for%')
    ''')


@artifact_processor
def logarchive_data_usage(context):
    return _artifacts_table_records(context, '''
        (category LIKE 'analytics' AND event_message LIKE '%Data Usage for%')
    ''')


@artifact_processor
def logarchive_lockdown_mode(context):
    return _artifacts_table_records(context, '''
        (subsystem LIKE 'com.apple.photos.backend' AND event_message LIKE '%isLockdownMode:%')
    ''')


@artifact_processor
def logarchive_passkey_store(context):
    return _artifacts_table_records(context, '''
        (subsystem LIKE 'com.apple.mobilesafari' AND event_message LIKE '%passkey keychain records from%')
    ''')


@artifact_processor
def logarchive_shortcut_actions(context):
    return _artifacts_table_records(context, '''
        (subsystem = 'com.apple.shortcuts' AND category = 'RunningLifecycle' AND event_message LIKE '%actionID=%')
    ''')


@artifact_processor
def logarchive_vpn_state(context):
    return _artifacts_table_records(context, '''
        (subsystem = 'com.apple.networkextension' AND event_message LIKE '%VPN connectivity state is now%')
    ''')


# Camera and microphone capture. The WHERE fragments below must stay within the markers
# logarchive_artifacts collects (a test checks every pattern appears there), because these
# artifacts only read the table that query builds.
CAPTURE_SESSION_WHERE = """
    subsystem = 'com.apple.cameracapture'
    AND (event_message LIKE '%FigCaptureSessionCreate:%'
         OR event_message LIKE '%captureSession_StartRunning:%'
         OR event_message LIKE '%captureSession_StopRunning:%'
         OR (event_message LIKE '%captureSession_transitionToSessionStatus:%'
             AND event_message LIKE '% -> %')
         OR (event_message LIKE '%captureSession_didStopRunning:%'
             AND event_message LIKE '%Stopped running%')
         OR event_message LIKE '%FigCaptureSessionDetachFromClient%'
         OR event_message LIKE '%-[AVCaptureSession startRunning]%'
         OR event_message LIKE '%-[AVCaptureSession stopRunning]%'
         OR (event_message LIKE '%ClientStartedSession:%'
             AND (event_message LIKE '%ClientStartedSession:1%'
                  OR event_message LIKE '%micStolen:1%'
                  OR event_message LIKE '%cameraStolen:1%')))
"""

CAPTURE_STREAMING_WHERE = """
    subsystem = 'com.apple.cameracapture'
    AND event_message LIKE '%FigCaptureLogCameraStreamingPowerEvent:%'
"""

RECORDING_INDICATOR_WHERE = """
    subsystem = 'com.apple.SpringBoard'
    AND (event_message LIKE '%[Recording Indicator] Active camera/microphone activity changed%'
         OR event_message LIKE '%[Recording Indicator] creating secure indicator layer%'
         OR event_message LIKE '%[Recording Indicator] updating live rendering assertion%')
"""

# The tag the capture daemon writes in front of a session message: <object address[pid][app id]>.
# The app id part is absent on some lines and is left blank then.
CAPTURE_TAG = re.compile(r'<(0x[0-9A-Fa-f]+)\[(\d+)\](?:\[([^\]]*)\])?>')
CAPTURE_FUNCTION = re.compile(r'FigCaptureSession >>>> (\w+):|AVCaptureSession >>>> (-\[AVCaptureSession \w+\])')
CAPTURE_CREATE_PID = re.compile(r'Creating session for PID (\d+)')
CAPTURE_TRANSITION = re.compile(r'captureSession_transitionToSessionStatus: (?:<[^>]*> )?(\S.* -> .*\S)')
CAPTURE_STATE = re.compile(r'ClientStartedSession:(\d+) Cam/Audio:(\d+)/(\d+) bg:(\d+)')
CAPTURE_FLAG_NAMES = (('mic_stolen', 'micStolen'), ('camera_stolen', 'cameraStolen'),
                      ('runtime_error', 'runtimeError'), ('interruption_error', 'interruptionError'))
CAPTURE_STATUS = re.compile(r'sessionStatus:(\w+)')
CAPTURE_STREAMING = re.compile(
    r'FigCaptureLogCameraStreamingPowerEvent: PID: (\d+), applicationID: (.*?), '
    r'deviceType: (\d+), streaming: (\d+), portType: (\w+)')

CAPTURE_SESSION_HEADERS = (
    ('Timestamp', 'datetime'), 'Row Number', 'Logged Function',
    'Client App ID (as logged)', 'Client PID (as logged)', 'Session Object (as logged)',
    'Client Started Session', 'Cam/Audio', 'Background', 'Mic Stolen', 'Camera Stolen',
    'Runtime Error', 'Interruption Error', 'Session Status', 'Status Transition',
    'Process Image Path', 'Process ID', 'Event Message')

RECORDING_INDICATOR_HEADERS = (
    ('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 'Event Message')

CAPTURE_STREAMING_HEADERS = (
    ('Timestamp', 'datetime'), 'Row Number', 'Client PID (as logged)',
    'Application ID (as logged)', 'Device Type (as logged)', 'Streaming (as logged)',
    'Port Type (as logged)', 'Process Image Path', 'Process ID', 'Event Message')


def _capture_session_fields(message):
    """The fields of one capture-daemon line, as logged; '' for any the line does not carry.

    Nothing is interpreted: the numbers are copied, and a line in another shape yields blanks
    rather than a guess, so the row still shows the full message.
    """
    message = str(message or '')
    fields = dict.fromkeys(
        ('function', 'app_id', 'pid', 'session_object', 'started', 'cam_audio', 'background',
         'mic_stolen', 'camera_stolen', 'runtime_error', 'interruption_error', 'status',
         'transition'), '')
    function = CAPTURE_FUNCTION.search(message)
    if function:
        fields['function'] = function.group(1) or function.group(2)
    tag = CAPTURE_TAG.search(message)
    if tag:
        fields['session_object'], fields['pid'], fields['app_id'] = (
            tag.group(1), tag.group(2), tag.group(3) or '')
    else:
        created = CAPTURE_CREATE_PID.search(message)
        if created:
            fields['pid'] = created.group(1)
    transition = CAPTURE_TRANSITION.search(message)
    if transition:
        fields['transition'] = transition.group(1)
    state = CAPTURE_STATE.search(message)
    if state:
        fields['started'] = state.group(1)
        fields['cam_audio'] = f'{state.group(2)}/{state.group(3)}'
        fields['background'] = state.group(4)
        for key, logged in CAPTURE_FLAG_NAMES:
            flag = re.search(rf'\b{logged}:(\d+)', message)
            if flag:
                fields[key] = flag.group(1)
        status = CAPTURE_STATUS.search(message)
        if status:
            fields['status'] = status.group(1)
    return fields


@artifact_processor
def logarchive_capture_sessions(context):
    source_path = get_file_path(context.get_files_found(), '_lava_artifacts.db')
    query = f'SELECT * FROM logarchive_artifacts WHERE {CAPTURE_SESSION_WHERE}'
    data_list = []
    for record in get_sqlite_db_records(source_path, query):
        fields = _capture_session_fields(record[6])
        data_list.append((
            _report_time(record[0]), record[1], fields['function'], fields['app_id'],
            fields['pid'], fields['session_object'], fields['started'], fields['cam_audio'],
            fields['background'], fields['mic_stolen'], fields['camera_stolen'],
            fields['runtime_error'], fields['interruption_error'], fields['status'],
            fields['transition'], record[2], record[3], record[6]))
    return CAPTURE_SESSION_HEADERS, data_list, source_path


@artifact_processor
def logarchive_capture_streaming(context):
    source_path = get_file_path(context.get_files_found(), '_lava_artifacts.db')
    query = f'SELECT * FROM logarchive_artifacts WHERE {CAPTURE_STREAMING_WHERE}'
    data_list = []
    for record in get_sqlite_db_records(source_path, query):
        logged = CAPTURE_STREAMING.search(str(record[6] or ''))
        pid, application, device, streaming, port = logged.groups() if logged else ('',) * 5
        data_list.append((_report_time(record[0]), record[1], pid, application, device,
                          streaming, port, record[2], record[3], record[6]))
    return CAPTURE_STREAMING_HEADERS, data_list, source_path


@artifact_processor
def logarchive_recording_indicator(context):
    # Subsystem and category are fixed by the WHERE clause and Trace ID is empty on the native
    # import, so none of the three is repeated here.
    source_path = get_file_path(context.get_files_found(), '_lava_artifacts.db')
    query = f'SELECT * FROM logarchive_artifacts WHERE {RECORDING_INDICATOR_WHERE}'
    data_list = [(_report_time(record[0]), record[1], record[2], record[3], record[6])
                 for record in get_sqlite_db_records(source_path, query)]
    return RECORDING_INDICATOR_HEADERS, data_list, source_path
