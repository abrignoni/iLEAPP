__artifacts_v2__ = {
    "powerlogApplicationRuntime": {
        "name": "PowerLog - Application Runtime",
        "description": "Application foreground and background runtime recorded by PowerLog "
                       "(PLAppTimeService_Aggregate_AppRunTime table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-28",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Raw PowerLog 'timestamp' values run on the log's internal clock, which can "
            "diverge from wall-clock time. The PLStorageOperator_EventForward_TimeOffset "
            "table records the correction in effect across the span of the log ('system' "
            "column, in seconds). Each row here is adjusted by the offset entry at or "
            "before its raw timestamp (rows older than the oldest retained entry use that "
            "oldest entry) and the applied offset is reported in its own column. Checked "
            "against test images: raw values lagged an iOS 18.7 acquisition date by ~32 "
            "days and led an iOS 12.4 acquisition by 69 seconds; corrected values align "
            "with the acquisition dates. ScreenOnTime/BackgroundTime read as seconds are "
            "consistent with the sampling-window durations in test data. Gzipped rotated "
            "logs (*.PLSQL.gz) are decompressed to a temporary location and parsed; the "
            "Source File column carries the archive path. InCallScreenOnTime and "
            "InCallBackgroundTime exist on later iOS 18 schemas only; where absent the "
            "columns are reported empty. PowerLog holds many additional version-specific "
            "tables that require separate validation."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "battery",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 13524 rows",
            "hickman_ios13": "iOS 13.3.1 | 11047 rows",
            "hickman_ios14": "iOS 14.3 | 18474 rows",
            "jess_ios15": "iOS 15.0.2 | 3558 rows",
            "hickman_ios15": "iOS 15 | 16221 rows",
            "magnet_ios16": "iOS 16.1.1 | 933 rows",
            "abe_ios16": "iOS 16.5 | 84531 rows",
            "felix23_ios16": "iOS 16.5 | 11986 rows",
            "fsfull002_ios17": "iOS 17.1 | 8059 rows",
            "iphone11_ios17": "iOS 17.3 | 55157 rows",
            "otto_ios17": "iOS 17.5.1 | 2364 rows",
            "felix_ios17": "iOS 17.6.1 | 33829 rows",
            "iphone14plus_ios18": "iOS 18.0 | 10541 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 4884 rows",
            "hc_ios18_7": "iOS 18.7.8 | 23095 rows",
            "hc_ios26": "iOS 26 | 17659 rows",
        },
    },
    "powerlogBatteryLevel": {
        "name": "PowerLog - Battery Level",
        "description": "Battery level and charging state samples recorded by PowerLog "
                       "(PLBatteryAgent_EventBackward_BatteryUI table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Level values ranged 1-100 across test images (iOS 12.4-26), consistent "
            "with a percentage. IsCharging holds 0/1, reported as No/Yes with other "
            "values passed through as stored. Timestamps are adjusted using PowerLog's "
            "time-offset table and the applied offset is reported per row; see the "
            "PowerLog - Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "battery-charging",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 12915 rows",
            "hickman_ios13": "iOS 13.3.1 | 5967 rows",
            "hickman_ios14": "iOS 14.3 | 6704 rows",
            "jess_ios15": "iOS 15.0.2 | 2560 rows",
            "hickman_ios15": "iOS 15 | 7220 rows",
            "magnet_ios16": "iOS 16.1.1 | 210 rows",
            "abe_ios16": "iOS 16.5 | 16342 rows",
            "felix23_ios16": "iOS 16.5 | 4905 rows",
            "fsfull002_ios17": "iOS 17.1 | 2999 rows",
            "iphone11_ios17": "iOS 17.3 | 13704 rows",
            "otto_ios17": "iOS 17.5.1 | 5229 rows",
            "felix_ios17": "iOS 17.6.1 | 44171 rows",
            "iphone14plus_ios18": "iOS 18.0 | 9098 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 5966 rows",
            "hc_ios18_7": "iOS 18.7.8 | 19008 rows",
            "hc_ios26": "iOS 26 | 3968 rows",
        },
    },
    "powerlogDevicePowerState": {
        "name": "PowerLog - Device Power State",
        "description": "Device sleep and wake power state events recorded by PowerLog "
                       "(PLSleepWakeAgent_EventForward_PowerState table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Event, State, and Reason are integer codes reported as stored; their "
            "meanings are not decoded here. Observed in test images (iOS 12.4-26): "
            "State 0-2, Event 0-5, Reason 1 or null. Timestamps are adjusted using "
            "PowerLog's time-offset table and the applied offset is reported per row; "
            "see the PowerLog - Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "power",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 65114 rows",
            "hickman_ios13": "iOS 13.3.1 | 13208 rows",
            "hickman_ios14": "iOS 14.3 | 13357 rows",
            "jess_ios15": "iOS 15.0.2 | 2960 rows",
            "hickman_ios15": "iOS 15 | 18018 rows",
            "magnet_ios16": "iOS 16.1.1 | 1472 rows",
            "abe_ios16": "iOS 16.5 | 21426 rows",
            "felix23_ios16": "iOS 16.5 | 3173 rows",
            "fsfull002_ios17": "iOS 17.1 | 3150 rows",
            "iphone11_ios17": "iOS 17.3 | 22977 rows",
            "otto_ios17": "iOS 17.5.1 | 5809 rows",
            "felix_ios17": "iOS 17.6.1 | 1206 rows",
            "iphone14plus_ios18": "iOS 18.0 | 2528 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 2646 rows",
            "hc_ios18_7": "iOS 18.7.8 | 3392 rows",
            "hc_ios26": "iOS 26 | 5275 rows",
        },
    },
    "powerlogAppState": {
        "name": "PowerLog - Application State",
        "description": "Application state transition events recorded by PowerLog "
                       "(PLApplicationAgent_EventForward_Application table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "State and Reason are integer codes reported as stored; their meanings are "
            "not decoded here. Observed in test images (iOS 12.4-26): State 0, 1, 2, 4, "
            "8, 32; Reason 0 or 1. Timestamps are adjusted using PowerLog's time-offset "
            "table and the applied offset is reported per row; see the PowerLog - "
            "Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "activity",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 9493 rows",
            "hickman_ios13": "iOS 13.3.1 | 10596 rows",
            "hickman_ios14": "iOS 14.3 | 11695 rows",
            "jess_ios15": "iOS 15.0.2 | 701 rows",
            "hickman_ios15": "iOS 15 | 5708 rows",
            "magnet_ios16": "iOS 16.1.1 | 360 rows",
            "abe_ios16": "iOS 16.5 | 31702 rows",
            "felix23_ios16": "iOS 16.5 | 2268 rows",
            "fsfull002_ios17": "iOS 17.1 | 921 rows",
            "iphone11_ios17": "iOS 17.3 | 18444 rows",
            "otto_ios17": "iOS 17.5.1 | 5404 rows",
            "felix_ios17": "iOS 17.6.1 | 5630 rows",
            "iphone14plus_ios18": "iOS 18.0 | 1591 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 10806 rows",
            "hc_ios18_7": "iOS 18.7.8 | 5933 rows",
            "hc_ios26": "iOS 26 | 5610 rows",
        },
    },
    "powerlogDeviceLock": {
        "name": "PowerLog - Device Lock State",
        "description": "Device lock and unlock state changes recorded by PowerLog "
                       "(PLSpringBoardAgent_EventForward_SBLock table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Locked holds 0/1, reported as No/Yes with other values passed through as "
            "stored. Table schema was identical across test images (iOS 12.4-26). "
            "Timestamps are adjusted using PowerLog's time-offset table and the applied "
            "offset is reported per row; see the PowerLog - Application Runtime notes "
            "for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "lock",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 214 rows",
            "hickman_ios13": "iOS 13.3.1 | 62 rows",
            "hickman_ios14": "iOS 14.3 | 63 rows",
            "jess_ios15": "iOS 15.0.2 | 21 rows",
            "hickman_ios15": "iOS 15 | 77 rows",
            "magnet_ios16": "iOS 16.1.1 | 3 rows",
            "abe_ios16": "iOS 16.5 | 295 rows",
            "felix23_ios16": "iOS 16.5 | 34 rows",
            "fsfull002_ios17": "iOS 17.1 | 7 rows",
            "iphone11_ios17": "iOS 17.3 | 114 rows",
            "otto_ios17": "iOS 17.5.1 | 4 rows",
            "felix_ios17": "iOS 17.6.1 | 39 rows",
            "iphone14plus_ios18": "iOS 18.0 | 6 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 42 rows",
            "hc_ios18_7": "iOS 18.7.8 | 57 rows",
            "hc_ios26": "iOS 26 | 53 rows",
        },
    },
    "powerlogAutolock": {
        "name": "PowerLog - Autolock Events",
        "description": "Autolock events recorded by PowerLog "
                       "(PLSpringBoardAgent_EventPoint_SBAutoLock table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "AutoLockType is an integer code reported as stored; its meaning is not "
            "decoded here. Observed values in test images (iOS 12.4-26): 1 and 4. "
            "Timestamps are adjusted using PowerLog's time-offset table and the applied "
            "offset is reported per row; see the PowerLog - Application Runtime notes "
            "for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "clock",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 71 rows",
            "hickman_ios13": "iOS 13.3.1 | 120 rows",
            "hickman_ios14": "iOS 14.3 | 113 rows",
            "jess_ios15": "iOS 15.0.2 | 30 rows",
            "hickman_ios15": "iOS 15 | 193 rows",
            "magnet_ios16": "iOS 16.1.1 | 11 rows",
            "abe_ios16": "iOS 16.5 | 1275 rows",
            "felix23_ios16": "iOS 16.5 | 35 rows",
            "fsfull002_ios17": "iOS 17.1 | 20 rows",
            "iphone11_ios17": "iOS 17.3 | 201 rows",
            "otto_ios17": "iOS 17.5.1 | 182 rows",
            "felix_ios17": "iOS 17.6.1 | 52 rows",
            "iphone14plus_ios18": "iOS 18.0 | 22 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 100 rows",
            "hc_ios18_7": "iOS 18.7.8 | 59 rows",
            "hc_ios26": "iOS 26 | 81 rows",
        },
    },
    "powerlogTorch": {
        "name": "PowerLog - Torch",
        "description": "Torch (flashlight) events recorded by PowerLog "
                       "(PLCameraAgent_EventForward_Torch table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "BundleId and Level are reported as stored; Level was 0 in every "
            "test-image row (iOS 12.4-26), so other values are unobserved. Rows are "
            "sparse: the test images held at most a few entries each. Timestamps are "
            "adjusted using PowerLog's time-offset table and the applied offset is "
            "reported per row; see the PowerLog - Application Runtime notes for the "
            "mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "zap",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 11 rows",
            "hickman_ios13": "iOS 13.3.1 | 8 rows",
            "hickman_ios14": "iOS 14.3 | 6 rows",
            "jess_ios15": "iOS 15.0.2 | 6 rows",
            "hickman_ios15": "iOS 15 | 8 rows",
            "magnet_ios16": "iOS 16.1.1 | 2 rows",
            "abe_ios16": "iOS 16.5 | 23 rows",
            "felix23_ios16": "iOS 16.5 | 6 rows",
            "fsfull002_ios17": "iOS 17.1 | 6 rows",
            "iphone11_ios17": "iOS 17.3 | 11 rows",
            "otto_ios17": "iOS 17.5.1 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | 2 rows",
            "iphone14plus_ios18": "iOS 18.0 | 3 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26 | 0 rows",
        },
    },
    "powerlogDisplayState": {
        "name": "PowerLog - Display State",
        "description": "Display brightness and ambient light samples recorded by "
                       "PowerLog (PLDisplayAgent_EventForward_Display table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Brightness values observed 0-100 across test images (iOS 12.4-26). "
            "SliderValue, lux, and mNits are reported as stored with the column names "
            "the database uses; no unit conversion is applied. Timestamps are adjusted "
            "using PowerLog's time-offset table and the applied offset is reported per "
            "row; see the PowerLog - Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "sun",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1271 rows",
            "hickman_ios13": "iOS 13.3.1 | 945 rows",
            "hickman_ios14": "iOS 14.3 | 1365 rows",
            "jess_ios15": "iOS 15.0.2 | 262 rows",
            "hickman_ios15": "iOS 15 | 4787 rows",
            "magnet_ios16": "iOS 16.1.1 | 45 rows",
            "abe_ios16": "iOS 16.5 | 4311 rows",
            "felix23_ios16": "iOS 16.5 | 110 rows",
            "fsfull002_ios17": "iOS 17.1 | 131 rows",
            "iphone11_ios17": "iOS 17.3 | 5369 rows",
            "otto_ios17": "iOS 17.5.1 | 519 rows",
            "felix_ios17": "iOS 17.6.1 | 667 rows",
            "iphone14plus_ios18": "iOS 18.0 | 710 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 8313 rows",
            "hc_ios18_7": "iOS 18.7.8 | 388 rows",
            "hc_ios26": "iOS 26 | 3091 rows",
        },
    },
    "powerlogAudioRouting": {
        "name": "PowerLog - Audio Routing",
        "description": "Audio output routing events recorded by PowerLog "
                       "(PLAudioAgent_EventForward_Routing table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "ActiveRoute and OutputCategory are text values reported verbatim; observed "
            "in test images (iOS 12.4-26): routes Speaker, Receiver, HeadphonesBT, "
            "CarAudioOutput, INVALID and categories Alarm, Ringtone, PhoneCall, "
            "Audio/Video, FindMyPhone, VoiceCommand. Active holds 0/1. ActivePID is "
            "absent from iOS 18+ schemas and BTEndpointType is absent before iOS 17; "
            "where absent the columns are reported empty. Timestamps are adjusted using "
            "PowerLog's time-offset table and the applied offset is reported per row; "
            "see the PowerLog - Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "headphones",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 183 rows",
            "hickman_ios13": "iOS 13.3.1 | 105 rows",
            "hickman_ios14": "iOS 14.3 | 206 rows",
            "jess_ios15": "iOS 15.0.2 | 20 rows",
            "hickman_ios15": "iOS 15 | 66 rows",
            "magnet_ios16": "iOS 16.1.1 | 4 rows",
            "abe_ios16": "iOS 16.5 | 2116 rows",
            "felix23_ios16": "iOS 16.5 | 40 rows",
            "fsfull002_ios17": "iOS 17.1 | 13 rows",
            "iphone11_ios17": "iOS 17.3 | 2097 rows",
            "otto_ios17": "iOS 17.5.1 | 34 rows",
            "felix_ios17": "iOS 17.6.1 | 22 rows",
            "iphone14plus_ios18": "iOS 18.0 | 22 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 594 rows",
            "hc_ios18_7": "iOS 18.7.8 | 262 rows",
            "hc_ios26": "iOS 26 | 91 rows",
        },
    },
    "powerlogAdapter": {
        "name": "PowerLog - Power Adapter",
        "description": "Power adapter electrical telemetry samples recorded by "
                       "PowerLog (PLBatteryAgent_EventBackward_Adapter table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Values are reported as stored with the column names the database uses; no "
            "units are asserted. In test images, nonzero SystemInputVoltage values "
            "clustered near 5000 and 9000 while a charger was connected. "
            "SystemInputVoltage and SystemInputCurrent are absent from some iOS 16 "
            "schemas; where absent the columns are reported empty. Timestamps are "
            "adjusted using PowerLog's time-offset table and the applied offset is "
            "reported per row; see the PowerLog - Application Runtime notes for the "
            "mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "plug-connected",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 438 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 1085 rows",
            "iphone11_ios17": "iOS 17.3 | 17679 rows",
            "otto_ios17": "iOS 17.5.1 | 2848 rows",
            "felix_ios17": "iOS 17.6.1 | 43487 rows",
            "iphone14plus_ios18": "iOS 18.0 | 1615 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 6036 rows",
            "hc_ios18_7": "iOS 18.7.8 | 2674 rows",
            "hc_ios26": "iOS 26 | 3110 rows",
        },
    },
    "powerlogCameraState": {
        "name": "PowerLog - Camera State",
        "description": "Camera session events recorded by PowerLog "
                       "(PLCameraAgent_EventForward_Camera table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "CameraType and State are integer codes reported as stored; their meanings "
            "are not decoded here. Observed in test images (iOS 12.4-26): CameraType "
            "0-4, State 0/1. The table's wider column set varies by iOS version; only "
            "the columns present in every tested schema are parsed. Timestamps are "
            "adjusted using PowerLog's time-offset table and the applied offset is "
            "reported per row; see the PowerLog - Application Runtime notes for the "
            "mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "camera",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 957 rows",
            "hickman_ios13": "iOS 13.3.1 | 131 rows",
            "hickman_ios14": "iOS 14.3 | 160 rows",
            "jess_ios15": "iOS 15.0.2 | 8 rows",
            "hickman_ios15": "iOS 15 | 100 rows",
            "magnet_ios16": "iOS 16.1.1 | 1 rows",
            "abe_ios16": "iOS 16.5 | 322 rows",
            "felix23_ios16": "iOS 16.5 | 14 rows",
            "fsfull002_ios17": "iOS 17.1 | 27 rows",
            "iphone11_ios17": "iOS 17.3 | 245 rows",
            "otto_ios17": "iOS 17.5.1 | 41 rows",
            "felix_ios17": "iOS 17.6.1 | 8 rows",
            "iphone14plus_ios18": "iOS 18.0 | 21 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 74 rows",
            "hc_ios18_7": "iOS 18.7.8 | 18 rows",
            "hc_ios26": "iOS 26 | 23 rows",
        },
    },
    "powerlogNeuralEngineModelLoad": {
        "name": "PowerLog - Neural Engine Model Load",
        "description": "Apple Neural Engine model load events recorded by PowerLog "
                       "(ANE_modelLoad_1_2 table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Present in iOS 18 and iOS 26 test images only. csIdentity holds process "
            "or bundle identifiers as recorded; modelURL holds a model file path. "
            "cacheHit, isPrecompiled, modelSize, and modelLoadingTime are reported as "
            "stored; no units are asserted. Timestamps are adjusted using PowerLog's "
            "time-offset table and the applied offset is reported per row; see the "
            "PowerLog - Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "cpu",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 42 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 1562 rows",
            "hc_ios18_7": "iOS 18.7.8 | 36 rows",
            "hc_ios26": "iOS 26 | 88 rows",
        },
    },
    "powerlogNeuralEngineModelUnload": {
        "name": "PowerLog - Neural Engine Model Unload",
        "description": "Apple Neural Engine model unload events recorded by PowerLog "
                       "(ANE_modelUnload_1_2 table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Present in iOS 18 and iOS 26 test images only. csIdentity holds process "
            "or bundle identifiers as recorded; modelURL holds a model file path. "
            "Timestamps are adjusted using PowerLog's time-offset table and the applied "
            "offset is reported per row; see the PowerLog - Application Runtime notes "
            "for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "cpu",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 43 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 1472 rows",
            "hc_ios18_7": "iOS 18.7.8 | 39 rows",
            "hc_ios26": "iOS 26 | 86 rows",
        },
    },
}

import gzip
import os
import shutil
import tempfile
from bisect import bisect_right

from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    does_column_exist_in_db,
    does_table_exist_in_db,
    get_sqlite_db_records,
    logfunc,
)

TIME_OFFSET_TABLE = "PLStorageOperator_EventForward_TimeOffset"

# Rotated archives are decompressed once per session and reused by every
# artifact in this module; maps original .PLSQL.gz path -> decompressed copy.
_GZ_CACHE = {}
# 'dir' -> session temp directory for the decompressed copies, first use only.
_GZ_TEMP = {}


def _materialize_gz(gz_path):
    """Decompress a rotated PowerLog archive to a session temp dir, once.

    Returns the decompressed path, or None when the archive cannot be read.
    The original file is only ever opened for reading.
    """
    cached = _GZ_CACHE.get(gz_path)
    if cached and os.path.exists(cached):
        return cached
    temp_dir = _GZ_TEMP.get("dir")
    if not temp_dir:
        temp_dir = tempfile.mkdtemp(prefix="ileapp_powerlog_gz_")
        _GZ_TEMP["dir"] = temp_dir
    out_name = f"{len(_GZ_CACHE):04d}_{os.path.basename(gz_path)[:-3]}"
    out_path = os.path.join(temp_dir, out_name)
    try:
        with gzip.open(gz_path, "rb") as src, open(out_path, "wb") as dst:
            shutil.copyfileobj(src, dst)
    except (OSError, EOFError, gzip.BadGzipFile) as e:
        logfunc(f"Could not decompress {gz_path}: {e}")
        return None
    _GZ_CACHE[gz_path] = out_path
    return out_path


def _powerlog_sources(context):
    """(queryable path, evidence path) for every PowerLog db found.

    Plain .PLSQL files are used in place; .PLSQL.gz rotated archives are
    decompressed to a temp dir but keep their original path for reporting.
    -wal/-shm sidecars ride along on disk for SQLite and are not listed.
    A file matched by more than one glob is returned once.
    """
    sources = []
    for path in dict.fromkeys(str(p) for p in context.get_files_found()):
        if path.endswith(".PLSQL"):
            sources.append((path, path))
        elif path.endswith(".PLSQL.gz"):
            materialized = _materialize_gz(path)
            if materialized:
                sources.append((materialized, path))
    return sources


def _load_time_offsets(source_path):
    """Read the log's clock corrections as parallel timestamp-sorted lists.

    Returns ([raw timestamp], [offset seconds]); empty lists when the table
    is missing or holds no usable rows.
    """
    if not does_table_exist_in_db(source_path, TIME_OFFSET_TABLE):
        return [], []
    stamps = []
    offsets = []
    for row in get_sqlite_db_records(source_path, f'''
            SELECT timestamp, system
            FROM "{TIME_OFFSET_TABLE}"
            WHERE timestamp IS NOT NULL AND system IS NOT NULL
            ORDER BY timestamp
        '''):
        stamps.append(row[0])
        offsets.append(row[1])
    return stamps, offsets


def _corrected_utc(raw_ts, stamps, offsets):
    """Apply the clock correction in effect at raw_ts.

    Returns (aware datetime, applied offset in whole seconds). Rows older
    than the oldest retained offset entry use that oldest entry; a log with
    no offset entries gets the raw value back and no offset reported.
    """
    if raw_ts is None:
        return None, None
    if not stamps:
        return convert_unix_ts_to_utc(raw_ts), None
    idx = bisect_right(stamps, raw_ts) - 1
    if idx < 0:
        idx = 0
    offset = offsets[idx]
    return convert_unix_ts_to_utc(raw_ts + offset), int(round(offset))


def _parse_powerlog_table(context, table, columns, row_builder, optional=()):
    """Run one query shape over every PowerLog db found.

    columns are selected as-is; names in optional are selected as NULL where
    a given file's schema lacks them, so row shape stays fixed across iOS
    versions. row_builder(corrected_ts, offset, row, evidence_path) -> tuple.
    """
    data_list = []
    sources = _powerlog_sources(context)
    for db_path, evidence_path in sources:
        if not does_table_exist_in_db(db_path, table):
            continue
        select_parts = []
        for col in columns:
            if col in optional and not does_column_exist_in_db(db_path, table, col):
                select_parts.append(f'NULL AS "{col}"')
            else:
                select_parts.append(f'"{col}"')
        stamps, offsets = _load_time_offsets(db_path)
        relative_path = context.get_relative_path(evidence_path)
        for row in get_sqlite_db_records(db_path, f'''
                SELECT {", ".join(select_parts)}
                FROM "{table}"
                ORDER BY timestamp
            '''):
            ts, offset = _corrected_utc(row[0], stamps, offsets)
            data_list.append(row_builder(ts, offset, row, relative_path))
    source = "See source paths in data" if sources else ""
    return data_list, source


def _yes_no(value):
    return {0: "No", 1: "Yes"}.get(value, value)


@artifact_processor
def powerlogApplicationRuntime(context):
    data_headers = (
        ("Timestamp", "datetime"), "Bundle ID", "Background Time (seconds)",
        "Screen-on Time (seconds)", "In-Call Background Time (seconds)",
        "In-Call Screen-on Time (seconds)", "Time Offset (seconds)", "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "PLAppTimeService_Aggregate_AppRunTime",
        ("timestamp", "BundleID", "BackgroundTime", "ScreenOnTime",
         "InCallBackgroundTime", "InCallScreenOnTime"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], row[4], row[5], offset, rel),
        optional=("InCallBackgroundTime", "InCallScreenOnTime"),
    )
    return data_headers, data_list, source


@artifact_processor
def powerlogBatteryLevel(context):
    data_headers = (
        ("Timestamp", "datetime"), "Battery Level (%)", "Is Charging",
        "Time Offset (seconds)", "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "PLBatteryAgent_EventBackward_BatteryUI",
        ("timestamp", "Level", "IsCharging"),
        lambda ts, offset, row, rel: (ts, row[1], _yes_no(row[2]), offset, rel),
    )
    return data_headers, data_list, source


@artifact_processor
def powerlogDevicePowerState(context):
    data_headers = (
        ("Timestamp", "datetime"), "Event (as stored)", "State (as stored)",
        "Reason (as stored)", "UUID", "Time Offset (seconds)", "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "PLSleepWakeAgent_EventForward_PowerState",
        ("timestamp", "Event", "State", "Reason", "UUID"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], row[4], offset, rel),
    )
    return data_headers, data_list, source


@artifact_processor
def powerlogAppState(context):
    data_headers = (
        ("Timestamp", "datetime"), "Identifier", "PID", "State (as stored)",
        "Reason (as stored)", "Time Offset (seconds)", "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "PLApplicationAgent_EventForward_Application",
        ("timestamp", "Identifier", "pid", "State", "Reason"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], row[4], offset, rel),
    )
    return data_headers, data_list, source


@artifact_processor
def powerlogDeviceLock(context):
    data_headers = (
        ("Timestamp", "datetime"), "Locked", "Time Offset (seconds)",
        "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "PLSpringBoardAgent_EventForward_SBLock",
        ("timestamp", "Locked"),
        lambda ts, offset, row, rel: (ts, _yes_no(row[1]), offset, rel),
    )
    return data_headers, data_list, source


@artifact_processor
def powerlogAutolock(context):
    data_headers = (
        ("Timestamp", "datetime"), "AutoLockType (as stored)",
        "Time Offset (seconds)", "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "PLSpringBoardAgent_EventPoint_SBAutoLock",
        ("timestamp", "AutoLockType"),
        lambda ts, offset, row, rel: (ts, row[1], offset, rel),
    )
    return data_headers, data_list, source


@artifact_processor
def powerlogTorch(context):
    data_headers = (
        ("Timestamp", "datetime"), "Bundle ID", "Level (as stored)",
        "Time Offset (seconds)", "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "PLCameraAgent_EventForward_Torch",
        ("timestamp", "BundleId", "Level"),
        lambda ts, offset, row, rel: (ts, row[1], row[2], offset, rel),
    )
    return data_headers, data_list, source


@artifact_processor
def powerlogDisplayState(context):
    data_headers = (
        ("Timestamp", "datetime"), "Brightness", "SliderValue (as stored)",
        "lux (as stored)", "mNits (as stored)", "Time Offset (seconds)",
        "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "PLDisplayAgent_EventForward_Display",
        ("timestamp", "Brightness", "SliderValue", "lux", "mNits"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], row[4], offset, rel),
    )
    return data_headers, data_list, source


@artifact_processor
def powerlogAudioRouting(context):
    data_headers = (
        ("Timestamp", "datetime"), "Active", "Active Route", "Output Category",
        "Headphones Connected", "BT Endpoint Type", "Active PID",
        "Time Offset (seconds)", "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "PLAudioAgent_EventForward_Routing",
        ("timestamp", "Active", "ActiveRoute", "OutputCategory",
         "HeadphonesConnected", "BTEndpointType", "ActivePID"),
        lambda ts, offset, row, rel: (
            ts, _yes_no(row[1]), row[2], row[3], _yes_no(row[4]), row[5],
            row[6], offset, rel),
        optional=("BTEndpointType", "ActivePID"),
    )
    return data_headers, data_list, source


@artifact_processor
def powerlogAdapter(context):
    data_headers = (
        ("Timestamp", "datetime"), "SystemInputVoltage (as stored)",
        "SystemInputCurrent (as stored)", "SystemPowerIn (as stored)",
        "SystemLoad (as stored)", "AdapterEfficiencyLoss (as stored)",
        "Time Offset (seconds)", "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "PLBatteryAgent_EventBackward_Adapter",
        ("timestamp", "SystemInputVoltage", "SystemInputCurrent",
         "SystemPowerIn", "SystemLoad", "AdapterEfficiencyLoss"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], row[4], row[5], offset, rel),
        optional=("SystemInputVoltage", "SystemInputCurrent"),
    )
    return data_headers, data_list, source


@artifact_processor
def powerlogCameraState(context):
    data_headers = (
        ("Timestamp", "datetime"), "Bundle ID", "CameraType (as stored)",
        "State (as stored)", "Time Offset (seconds)", "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "PLCameraAgent_EventForward_Camera",
        ("timestamp", "BundleId", "CameraType", "State"),
        lambda ts, offset, row, rel: (ts, row[1], row[2], row[3], offset, rel),
    )
    return data_headers, data_list, source


@artifact_processor
def powerlogNeuralEngineModelLoad(context):
    data_headers = (
        ("Timestamp", "datetime"), "Identity", "Model URL",
        "Model Size (as stored)", "Loading Time (as stored)",
        "Cache Hit (as stored)", "Precompiled (as stored)",
        "Time Offset (seconds)", "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "ANE_modelLoad_1_2",
        ("timestamp", "csIdentity", "modelURL", "modelSize",
         "modelLoadingTime", "cacheHit", "isPrecompiled"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], row[4], row[5], row[6], offset, rel),
    )
    return data_headers, data_list, source


@artifact_processor
def powerlogNeuralEngineModelUnload(context):
    data_headers = (
        ("Timestamp", "datetime"), "Identity", "Model URL",
        "Time Offset (seconds)", "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "ANE_modelUnload_1_2",
        ("timestamp", "csIdentity", "modelURL"),
        lambda ts, offset, row, rel: (ts, row[1], row[2], offset, rel),
    )
    return data_headers, data_list, source
