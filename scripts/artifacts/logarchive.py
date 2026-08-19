__artifacts_v2__ = {
    "logarchive": {
        "name": "logarchive",
        "description": "Processes Apple Unified Logs, either from tracev3 data in the "
                       "extraction or from a json file exported with 'log show'",
        "author": "@AlexisBrignoni",
        "creation_date": "2025-05-06",
        "last_update_date": "2026-07-29",
        "requirements": "Reading tracev3 data natively requires the unifiedlog_iterator "
                        "binary; see scripts/unifiedlogs.py",
        "category": "Unified Logs",
        "notes": "",
        # The tracev3 globs are anchored at db/, not private/var/db/: Cellebrite UFED
        # zips (and the corpus CSVs in admin/data/filepath-lists) store the data
        # partition as filesystem2/db/diagnostics with no private/var prefix, and the
        # anchored form never matched them. fnmatch's '*' crosses path separators, so
        # these cover the Apple-native layout too.
        "paths": ('*/logarchive*.json',
                  '*/db/diagnostics/*',
                  '*/db/uuidtext/*',
                  '*.logarchive/*'),
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
        "description": "Identify time changes",
        "author": "@AlexisBrignoni",
        "creation_date": "2025-05-22",
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "2026-08-01: added the system 'Significant time change' broadcast "
                 "(observed on iOS 18.7) and the timed manual-time-setting entries "
                 "(TMSetManualTime / 'setting manual time'), which record a clock set by "
                 "hand on the device. Manual-time patterns documented at "
                 "https://www.ios-unifiedlogs.com/post/ios-unified-logs-don-t-trust-the-clock-timestamp.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "clock",
    },
    "logarchive_flashlight": {
        "name": "logarchive flashlight",
        "description": "Identify flashlight turn on or off",
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
        "description": "Track apps being executed",
        "author": "@AlexisBrignoni",
        "creation_date": "2025-05-26",
        "last_update_date": "2025-05-26",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "code",
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
        "description": "Lock Status",
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
                 "records when a network is picked by hand in Settings rather than "
                 "auto-joined "
                 "(https://www.ios-unifiedlogs.com/post/ios-unified-logs-parsing-all-my-sql-queries). "
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
        "description": "Navigation entries",
        "author": "@AlexisBrignoni",
        "creation_date": "2025-07-25",
        "last_update_date": "2025-07-25",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "map-pin",
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
                 "asked for the call UI (touch, Siri, or a Bluetooth accessory). Keypad tone "
                 "entries come from mediaserverd in the cited research and from audiomxd on "
                 "iOS 18.7, and only appear when keypad sounds are enabled. The number "
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
                 "where the value survived. ContactSearchManager: 752 entries on an iOS "
                 "18.7 image, 301 of them the 'Searching for' and 'Search cancelled for' "
                 "pairs, whose digit strings lengthen one step at a time up to a ten-digit "
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
                 "(subsystem UIKitCore there; com.apple.TextInput on iOS 18.7). Sound-request "
                 "actionID mapping documented at "
                 "https://www.ios-unifiedlogs.com/post/ios-unified-logs-typing-and-sending-a-message-in-whatsapp; "
                 "those entries require keyboard sounds to be enabled and name the client "
                 "app. Text content is not recorded. High volume: over 200k signpost rows "
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
                 "observed on iOS 18.7. Indicates the front sensor was obstructed (device "
                 "face-down or stowed) versus clear; the cited research reports bursts of "
                 "entries per obstruction period.",
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
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Documented at https://thesisfriday.com/thesis-friday-14-aul-touch-events/ "
                 "(iOS 18.5) and "
                 "https://www.ios-unifiedlogs.com/news/ios-unified-logs-touching-the-iphone-screen; "
                 "observed on iOS 18.7. Contact entries record finger presence on the "
                 "digitizer, not which control was touched. High volume, LAVA-only.",
        "paths": None,
        "output_types": "lava_only",
        "artifact_icon": "target",
    },
    "logarchive_usb_connections": {
        "name": "logarchive USB and power connections",
        "description": "Unified log entries recording external power and USB cable "
                       "attach/detach: powerexperienced plugin state changes, kernel "
                       "IOAccessoryUSBConnectShim cable-detect events, and the kernel "
                       "VBUS power and CON_DET physical-connection states",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-08-02",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Documented at "
                 "https://thesisfriday.com/thesis-friday-9-aul-connecting-a-usb-cable/ and "
                 "https://thesisfriday.com/thesis-friday-20-project-stark-forensic-reconstruction-of-the-carplay-handshake/; "
                 "observed on iOS 18.7, where the shim also emits an 'AppleUSBCableDetect 1' "
                 "form. The 'USB Power (VBUS) Present' pattern was added 2026-08-02 as "
                 "version insurance, not as a fix: the cited CarPlay research, revised for "
                 "iOS 26.6, quotes that line without the shim prefix and treats it as the "
                 "most consistent connection marker, with 'Present: 0' the reliable detach "
                 "signal while CON_DET can remain 1. On our images every VBUS line did "
                 "carry the shim prefix and was therefore already collected (30 records on "
                 "iOS 18.7, 40 on iOS 17.1, none without the prefix), so the pattern is "
                 "redundant on those versions and only earns its place if a release drops "
                 "the prefix. These entries record cable presence, not what was connected; "
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
        "description": "Unified log entries recording interaction with notifications: "
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
                 "validation image's log window. Notification content is not recorded.",
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
                 "foreground-interactive' indicates a launch from a fully closed state; the "
                 "iOS 16 form is 'Bootstrapping application<bundle>' and iOS 17+ is "
                 "'Bootstrapping app<bundle>'. An empty inFocus value indicates return to "
                 "the home screen. Complements the logarchive executed apps artifact.",
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
        "description": "Unified log entries recording lock/unlock session durations (apsd "
                       "'Was locked/unlocked for N seconds'), authentication requests with "
                       "type and outcome, chronod locked-state transitions, keybag/APFS "
                       "volume unlock, and locks from the side button",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-01",
        "last_update_date": "2026-08-01",
        "requirements": "logarchive module must be executed first",
        "category": "Unified Logs",
        "notes": "Patterns documented by Lionel Notari "
                 "(https://www.ios-unifiedlogs.com/post/ios-unified-logs-unlock) and "
                 "https://thesisfriday.com/thesis-friday-12-aul-first-glance-at-ios-26/; "
                 "observed on iOS 18.7. In 'Processed authentication request' entries the "
                 "cited research maps type 1 to passcode and type 2 to biometric, and "
                 "success=NO entries record failed attempts. Complements the logarchive "
                 "lock status artifact with durations and method.",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "unlock",
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
                 "observed on iOS 18.7. The CSAudioRecordTypeDictation entries distinguish "
                 "keyboard dictation from Siri requests. Dictated content is not recorded.",
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
                 "observed on iOS 18.7. These entries record deliberate interface "
                 "interaction between app launches.",
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
                 "shows nothing. The motion classification also fires on other transport. "
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
        "description": "Unified log entries from sosd recording SOS engine status "
                       "broadcasts and flow state, including the paired-device trigger "
                       "entry",
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
                 "and the same author's SQL queries post; all three entry families "
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
        "description": "Unified log entries from sharingd's AirDrop and share sheet "
                       "categories: the device's rotating AirDrop ID, discoverability "
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
                 "windows. AirDrop IDs rotate, so an ID ties activity together only "
                 "within a session.",
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
        "notes": "NOT YET VALIDATED IN-HOUSE. Every pattern here comes from Tim Korver's "
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
    }
}

import os

import ijson
from datetime import datetime, timezone
from scripts import unifiedlogs
from scripts.ilapfuncs import artifact_processor, artifact_processor_streaming, get_file_path, \
    get_sqlite_db_records, logfunc

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


@artifact_processor_streaming
def logarchive(context):
    """Import Apple Unified Logs into the LAVA database.

    Two sources, in order of preference:

      1. a 'logarchive*.json' export the examiner produced with 'log show' on a Mac, which
         stays the documented workflow and is what an examiner explicitly chose to provide;
      2. the tracev3 data in the extraction itself, read natively, which needs no Mac and no
         intermediate json file.

    Rows are streamed rather than accumulated: a full archive runs to tens of millions of
    records, which is more than fits in memory as Python tuples.
    """
    files_found = context.get_files_found()

    source_path = get_file_path(files_found, 'logarchive*.json')
    if source_path:
        return DATA_HEADERS, rows_from_json(source_path), source_path

    logarchive_dir, diagnostics_dir, uuidtext_dir = unifiedlogs.find_archive_roots(files_found)
    if not logarchive_dir and not diagnostics_dir:
        return DATA_HEADERS, iter(()), None

    binary = unifiedlogs.find_iterator()
    if not binary:
        logfunc('Unified Log tracev3 data was found but the unifiedlog_iterator binary is not '
                'available, so it cannot be read natively. Either install the binary (see '
                'scripts/unifiedlogs.py) or supply a logarchive*.json export.')
        return DATA_HEADERS, iter(()), None

    if logarchive_dir:
        archive_dir = logarchive_dir
        source_path = logarchive_dir
    else:
        if not uuidtext_dir:
            # Without uuidtext the parser cannot resolve format strings, so the messages
            # would come back as placeholders. Better to say why than to import junk.
            logfunc('Unified Log tracev3 data was found but the uuidtext directory was not, '
                    'so log messages cannot be resolved. Skipping.')
            return DATA_HEADERS, iter(()), None
        archive_dir = unifiedlogs.assemble_archive(
            diagnostics_dir, uuidtext_dir,
            os.path.join(context.get_data_folder(), '_logarchive_native'))
        source_path = f'{diagnostics_dir}\n{uuidtext_dir}'

    logfunc(f'Reading Apple Unified Logs natively with {os.path.basename(binary)}')
    return DATA_HEADERS, rows_from_tracev3(binary, archive_dir), source_path

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
        OR event_message LIKE '%Proceed to%'
        OR event_message LIKE '%Turn right%'
        OR event_message LIKE '%Turn left%'
        OR event_message LIKE '%roundabout%'
        OR event_message LIKE '%first exit%'
        OR event_message LIKE '%Stay in the%'
        OR event_message LIKE '%parking lot%'
        OR event_message LIKE '%of a mile%'
        OR event_message LIKE '%In about%'
        OR event_message LIKE '%Arrived%'
        OR event_message LIKE '%destination%'
        OR event_message LIKE '%At the light%'
        OR event_message LIKE '%Starting route to%'
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
    source_path = get_file_path(context.get_files_found(), '_lava_artifacts.db')
    data_list = []
    
    query = '''
    SELECT *
    FROM logarchive_artifacts
    WHERE event_message LIKE '%Starting route to%'
        OR event_message LIKE '%Proceed to the%'
        OR event_message LIKE '%Proceed to\\%'
        OR event_message LIKE '%Turn right%'
        OR event_message LIKE '%Turn left%'
        OR event_message LIKE '%roundabout%'
        OR event_message LIKE '%first exit%'
        OR event_message LIKE '%Stay in the%'
        OR event_message LIKE '%parking lot for%'
        OR event_message LIKE '%of a mile%'
        OR event_message LIKE '%In about%'
        OR event_message LIKE '%then arrive%'
        OR event_message LIKE '%your destination%'
        OR event_message LIKE '%At the light%'
        OR event_message LIKE '%Arrived\\%'
    '''
    
    data_list = list( get_sqlite_db_records(source_path, query) )
    data_headers = (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID', 
                    'Subsystem', 'Category', 'Event Message', 'Trace ID')
    
    return data_headers, data_list, source_path
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
        OR event_message LIKE '%lock button source%'
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
