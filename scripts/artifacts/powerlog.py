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
            "*/powerlogs/*.PLSQL*",
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
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 6266 rows",
            "otto_ios17": "iOS 17.5.1 | 2364 rows",
            "felix_ios17": "iOS 17.6.1 | 37932 rows",
            "iphone14plus_ios18": "iOS 18.0 | 10541 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 4884 rows",
            "hc_ios18_7": "iOS 18.7.8 | 23095 rows",
            "hc_ios26": "iOS 26 | 17659 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 5650 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 18883 rows",
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
            "*/powerlogs/*.PLSQL*",
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
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 1591 rows",
            "otto_ios17": "iOS 17.5.1 | 5229 rows",
            "felix_ios17": "iOS 17.6.1 | 49753 rows",
            "iphone14plus_ios18": "iOS 18.0 | 9098 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 5966 rows",
            "hc_ios18_7": "iOS 18.7.8 | 19008 rows",
            "hc_ios26": "iOS 26 | 3968 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 1746 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 7827 rows",
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
            "*/powerlogs/*.PLSQL*",
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
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 2670 rows",
            "otto_ios17": "iOS 17.5.1 | 5809 rows",
            "felix_ios17": "iOS 17.6.1 | 1207 rows",
            "iphone14plus_ios18": "iOS 18.0 | 2528 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 2646 rows",
            "hc_ios18_7": "iOS 18.7.8 | 3392 rows",
            "hc_ios26": "iOS 26 | 5275 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 1370 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 5963 rows",
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
            "*/powerlogs/*.PLSQL*",
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
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 5345 rows",
            "otto_ios17": "iOS 17.5.1 | 5404 rows",
            "felix_ios17": "iOS 17.6.1 | 5998 rows",
            "iphone14plus_ios18": "iOS 18.0 | 1591 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 10806 rows",
            "hc_ios18_7": "iOS 18.7.8 | 5933 rows",
            "hc_ios26": "iOS 26 | 5610 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 1065 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 8499 rows",
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
            "*/powerlogs/*.PLSQL*",
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
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 40 rows",
            "otto_ios17": "iOS 17.5.1 | 4 rows",
            "felix_ios17": "iOS 17.6.1 | 40 rows",
            "iphone14plus_ios18": "iOS 18.0 | 6 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 42 rows",
            "hc_ios18_7": "iOS 18.7.8 | 57 rows",
            "hc_ios26": "iOS 26 | 53 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 5 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 27 rows",
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
            "*/powerlogs/*.PLSQL*",
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
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 70 rows",
            "otto_ios17": "iOS 17.5.1 | 182 rows",
            "felix_ios17": "iOS 17.6.1 | 53 rows",
            "iphone14plus_ios18": "iOS 18.0 | 22 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 100 rows",
            "hc_ios18_7": "iOS 18.7.8 | 59 rows",
            "hc_ios26": "iOS 26 | 81 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 18 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 63 rows",
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
            "*/powerlogs/*.PLSQL*",
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
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 1 rows",
            "otto_ios17": "iOS 17.5.1 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | 2 rows",
            "iphone14plus_ios18": "iOS 18.0 | 3 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26 | 0 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 1 rows",
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
            "*/powerlogs/*.PLSQL*",
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
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 1009 rows",
            "otto_ios17": "iOS 17.5.1 | 519 rows",
            "felix_ios17": "iOS 17.6.1 | 670 rows",
            "iphone14plus_ios18": "iOS 18.0 | 710 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 8313 rows",
            "hc_ios18_7": "iOS 18.7.8 | 388 rows",
            "hc_ios26": "iOS 26 | 3091 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 163 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 1434 rows",
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
            "*/powerlogs/*.PLSQL*",
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
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 261 rows",
            "otto_ios17": "iOS 17.5.1 | 34 rows",
            "felix_ios17": "iOS 17.6.1 | 24 rows",
            "iphone14plus_ios18": "iOS 18.0 | 22 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 594 rows",
            "hc_ios18_7": "iOS 18.7.8 | 262 rows",
            "hc_ios26": "iOS 26 | 91 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 3 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 43 rows",
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
            "*/powerlogs/*.PLSQL*",
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
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 2764 rows",
            "otto_ios17": "iOS 17.5.1 | 2848 rows",
            "felix_ios17": "iOS 17.6.1 | 47807 rows",
            "iphone14plus_ios18": "iOS 18.0 | 1615 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 6036 rows",
            "hc_ios18_7": "iOS 18.7.8 | 2674 rows",
            "hc_ios26": "iOS 26 | 3110 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 367 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 3105 rows",
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
            "*/powerlogs/*.PLSQL*",
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
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 94 rows",
            "otto_ios17": "iOS 17.5.1 | 41 rows",
            "felix_ios17": "iOS 17.6.1 | 9 rows",
            "iphone14plus_ios18": "iOS 18.0 | 21 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 74 rows",
            "hc_ios18_7": "iOS 18.7.8 | 18 rows",
            "hc_ios26": "iOS 26 | 23 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 1 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 118 rows",
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
            "*/powerlogs/*.PLSQL*",
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
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 42 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 1562 rows",
            "hc_ios18_7": "iOS 18.7.8 | 36 rows",
            "hc_ios26": "iOS 26 | 88 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 7 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 216 rows",
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
            "*/powerlogs/*.PLSQL*",
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
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 43 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 1472 rows",
            "hc_ios18_7": "iOS 18.7.8 | 39 rows",
            "hc_ios26": "iOS 26 | 86 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 7 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 200 rows",
        },
    },
    "powerlogGenerativeSummarization": {
        "name": "PowerLog - Generative Function Summarization",
        "description": "Summarization request events recorded by PowerLog "
                       "(GenerativeFunctionMetrics_Summarization_1_2 table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "bundleID holds app bundle identifiers as recorded. kind, exitReason, "
            "and isUrgent are integer codes reported as stored; observed kind "
            "0/2/3 and exitReason 6/12/13. "
            "In test data these tables held rows only on an Apple Intelligence "
            "capable device (iPhone 16, iOS 26.5.2 sysdiagnose); on other iOS 18-26 "
            "test images they exist with zero rows. Timestamps are adjusted using "
            "PowerLog's time-offset table and the applied offset is reported per "
            "row; end times preserve the recorded duration against the corrected "
            "start. See the PowerLog - Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
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
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26 | 0 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 309 rows",
        },
    },
    "powerlogGenerativeTextRequests": {
        "name": "PowerLog - Generative Function Text Generation",
        "description": "Text generation inference request events recorded by PowerLog "
                       "(GenerativeFunctionMetrics_tgiExecuteRequest_1_2 table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Token counts, latencies, and type codes are reported as stored; no "
            "units are asserted for latency values. The table carries additional "
            "speculative-decoding counters (sd_*) that are not parsed here. "
            "In test data these tables held rows only on an Apple Intelligence "
            "capable device (iPhone 16, iOS 26.5.2 sysdiagnose); on other iOS 18-26 "
            "test images they exist with zero rows. Timestamps are adjusted using "
            "PowerLog's time-offset table and the applied offset is reported per "
            "row; end times preserve the recorded duration against the corrected "
            "start. See the PowerLog - Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
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
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26 | 0 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 46 rows",
        },
    },
    "powerlogGenerativeInferenceRequests": {
        "name": "PowerLog - Generative Function Inference Requests",
        "description": "Model inference request events recorded by PowerLog "
                       "(GenerativeFunctionMetrics_mmExecuteRequest_1_2 table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "useCaseIdentifier is a text value reported verbatim; observed values "
            "include summarization.summarizeMailMessage, "
            "classification.classifyMailMessage, memoryCreation.QueryUnderstanding, "
            "and textUnderstanding.TextEventExtraction. Bundle and provider "
            "identifiers are reported as recorded. "
            "In test data these tables held rows only on an Apple Intelligence "
            "capable device (iPhone 16, iOS 26.5.2 sysdiagnose); on other iOS 18-26 "
            "test images they exist with zero rows. Timestamps are adjusted using "
            "PowerLog's time-offset table and the applied offset is reported per "
            "row; end times preserve the recorded duration against the corrected "
            "start. See the PowerLog - Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
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
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26 | 0 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 255 rows",
        },
    },
    "powerlogGenerativeAssetLoad": {
        "name": "PowerLog - Generative Function Asset Loads",
        "description": "Model asset load events recorded by PowerLog "
                       "(GenerativeFunctionMetrics_assetLoad_1_2 table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "catalogResourceIdentifier is reported verbatim; observed values "
            "reference foundation language model assets (for example "
            "fm.language.instruct_3b variants and gm.safety_* resources). "
            "loadType, reason, and result are integer codes reported as stored. "
            "In test data these tables held rows only on an Apple Intelligence "
            "capable device (iPhone 16, iOS 26.5.2 sysdiagnose); on other iOS 18-26 "
            "test images they exist with zero rows. Timestamps are adjusted using "
            "PowerLog's time-offset table and the applied offset is reported per "
            "row; end times preserve the recorded duration against the corrected "
            "start. See the PowerLog - Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
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
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26 | 0 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 329 rows",
        },
    },
    "powerlogGenerativeOptIn": {
        "name": "PowerLog - Generative Function Opt-In",
        "description": "Opt-in state samples recorded by PowerLog "
                       "(GenerativeFunctionMetrics_OptIn_1_2 table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Enabled holds 0/1, reported as No/Yes with other values passed "
            "through as stored. On the device with data, raw timestamps for this "
            "table were decades off wall-clock time until corrected by the "
            "time-offset table, so the reported offset column is essential "
            "context. "
            "In test data these tables held rows only on an Apple Intelligence "
            "capable device (iPhone 16, iOS 26.5.2 sysdiagnose); on other iOS 18-26 "
            "test images they exist with zero rows. Timestamps are adjusted using "
            "PowerLog's time-offset table and the applied offset is reported per "
            "row; end times preserve the recorded duration against the corrected "
            "start. See the PowerLog - Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
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
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26 | 0 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 3 rows",
        },
    },
    "powerTelemetryBatteryDataDaily": {
        "name": "Power Telemetry - Battery Data Daily",
        "description": "Daily battery data samples recorded in the PerfPowerTelemetry "
                       "extended persistence log (BatteryDataCollection_BDC_Daily table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "Power Telemetry",
        "notes": (
            "CycleCount, MaxCapacityPercent, NominalChargeCapacity, and "
            "ChargingVoltage are reported as stored; no units are asserted. "
            "MaxCapacityPercent is absent from iOS 15/16 schemas and reported "
            "empty there. In test data rows spanned more than a year on one "
            "device. "
            "Raw timestamp values are adjusted using the time-offset table in "
            "this log (PPTStorageOperator_TimeOffset; its retention suffix "
            "varies by iOS version) and the applied offset is reported per row; "
            "see the PowerLog - Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/PerfPowerTelemetry/*/*.EPSQL*",
            "*/powerlogs/*.EPSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "battery",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 48 rows",
            "hickman_ios15": "iOS 15 | 77 rows",
            "magnet_ios16": "iOS 16.1.1 | 93 rows",
            "abe_ios16": "iOS 16.5 | 208 rows",
            "felix23_ios16": "iOS 16.5 | 245 rows",
            "fsfull002_ios17": "iOS 17.1 | 193 rows",
            "iphone11_ios17": "iOS 17.3 | 598 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 608 rows",
            "otto_ios17": "iOS 17.5.1 | 110 rows",
            "felix_ios17": "iOS 17.6.1 | 58 rows",
            "iphone14plus_ios18": "iOS 18.0 | 52 rows",
            "dexter_ios18": "iOS 18.3.2 | 82 rows",
            "iphone12_ios18": "iOS 18.7 | 46 rows",
            "hc_ios18_7": "iOS 18.7.8 | 225 rows",
            "hc_ios26": "iOS 26 | 15 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 26 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 1349 rows",
        },
    },
    "powerTelemetrySmartCharging": {
        "name": "Power Telemetry - Smart Charging",
        "description": "Smart charging state samples recorded in the PerfPowerTelemetry "
                       "extended persistence log (BatteryDataCollection_BDC_SmartCharging "
                       "table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "Power Telemetry",
        "notes": (
            "ChargeLimit, ChargingState, CheckPoint, DecisionMaker, InflowState, "
            "and ModeOfOperation are integer codes reported as stored; their "
            "meanings are not decoded here. DecisionMaker is absent from iOS 16 "
            "schemas and reported empty there. "
            "Raw timestamp values are adjusted using the time-offset table in "
            "this log (PPTStorageOperator_TimeOffset; its retention suffix "
            "varies by iOS version) and the applied offset is reported per row; "
            "see the PowerLog - Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/PerfPowerTelemetry/*/*.EPSQL*",
            "*/powerlogs/*.EPSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "battery-charging",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 5 rows",
            "abe_ios16": "iOS 16.5 | 160 rows",
            "felix23_ios16": "iOS 16.5 | 26 rows",
            "fsfull002_ios17": "iOS 17.1 | 49 rows",
            "iphone11_ios17": "iOS 17.3 | 241 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 247 rows",
            "otto_ios17": "iOS 17.5.1 | 442 rows",
            "felix_ios17": "iOS 17.6.1 | 38 rows",
            "iphone14plus_ios18": "iOS 18.0 | 12 rows",
            "dexter_ios18": "iOS 18.3.2 | 160 rows",
            "iphone12_ios18": "iOS 18.7 | 75 rows",
            "hc_ios18_7": "iOS 18.7.8 | 189 rows",
            "hc_ios26": "iOS 26 | 17 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 26 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 3525 rows",
        },
    },
    "powerTelemetryBatteryHardware": {
        "name": "Power Telemetry - Battery Hardware Data",
        "description": "Battery hardware data rows recorded in the PerfPowerTelemetry "
                       "extended persistence log (BatteryDataCollection_BDC_Once table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "Power Telemetry",
        "notes": (
            "DesignCapacity, ChemID, AlgoChemID, EEEE, YWW, and "
            "GasGaugeFirmwareVersion are reported as stored; no interpretation "
            "is applied. Test images held at most two rows each. "
            "Raw timestamp values are adjusted using the time-offset table in "
            "this log (PPTStorageOperator_TimeOffset; its retention suffix "
            "varies by iOS version) and the applied offset is reported per row; "
            "see the PowerLog - Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/PerfPowerTelemetry/*/*.EPSQL*",
            "*/powerlogs/*.EPSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "settings",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15 | 1 rows",
            "magnet_ios16": "iOS 16.1.1 | 1 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 1 rows",
            "fsfull002_ios17": "iOS 17.1 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 1 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 1 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26 | 0 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 2 rows",
        },
    },
    "powerTelemetryBatteryTrustedDaily": {
        "name": "Power Telemetry - Battery Trusted Data Daily",
        "description": "Daily trusted battery data samples recorded in the "
                       "PerfPowerTelemetry extended persistence log "
                       "(BatteryTrustedData_Daily table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "Power Telemetry",
        "notes": (
            "TrustedCycleCount, TrustedMaximumCapacity, and TrustedLifeTimeMaxWRdc "
            "are reported as stored. TrustedDateOfFirstUse decodes as a standard "
            "Unix timestamp, unlike the offset-skewed timestamp column: on two "
            "validation devices it held one stable calendar date each, preceding "
            "every daily sample. The table exists on iOS 18+ test images only; one "
            "validation device carried a full year of daily rows. "
            "Raw timestamp values are adjusted using the time-offset table in "
            "this log (PPTStorageOperator_TimeOffset; its retention suffix "
            "varies by iOS version) and the applied offset is reported per row; "
            "see the PowerLog - Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/PerfPowerTelemetry/*/*.EPSQL*",
            "*/powerlogs/*.EPSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "clock",
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
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 42 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26 | 0 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 364 rows",
        },
    },
    "powerTelemetryBackgroundTaskInstances": {
        "name": "Power Telemetry - Background Task Instances",
        "description": "Background task execution records from the PerfPowerTelemetry "
                       "background processing log (BackgroundProcessing_TaskInstanceData "
                       "table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "Power Telemetry",
        "notes": (
            "StartDate and EndDate hold standard Unix timestamps as stored; the "
            "row timestamp runs on the internal clock and is offset-corrected "
            "here, and on validation data the corrected value aligns with "
            "StartDate in the same rows. StartedOnBattery holds 0/1, reported "
            "as No/Yes. Observed only in iOS 26 test data; iOS 18 background "
            "processing logs exist without this table. "
            "Raw timestamp values are adjusted using the time-offset table in "
            "this log (BackgroundProcessing_TimeOffset) and the applied offset "
            "is reported per row; see the PowerLog - Application Runtime notes "
            "for the mechanism."
        ),
        "paths": (
            "*/PerfPowerTelemetry/*/*.BGSQL*",
            "*/powerlogs/*.BGSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "activity",
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
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26 | 15297 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 26912 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 109132 rows",
        },
    },
    "powerTelemetryBackgroundTaskMetadata": {
        "name": "Power Telemetry - Background Task Metadata",
        "description": "Background task registrations from the PerfPowerTelemetry "
                       "background processing log (BackgroundProcessing_TaskMetadata table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "Power Telemetry",
        "notes": (
            "BundleID, Name, ServiceName, GroupName, and LaunchReason are "
            "reported as recorded. Observed only in iOS 26 test data; iOS 18 "
            "background processing logs exist without this table. "
            "Raw timestamp values are adjusted using the time-offset table in "
            "this log (BackgroundProcessing_TimeOffset) and the applied offset "
            "is reported per row; see the PowerLog - Application Runtime notes "
            "for the mechanism."
        ),
        "paths": (
            "*/PerfPowerTelemetry/*/*.BGSQL*",
            "*/powerlogs/*.BGSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "package",
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
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26 | 2092 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 2591 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 1623 rows",
        },
    },
}

import gzip
import os
import shutil
import tempfile
from bisect import bisect_right
from datetime import timedelta

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


def _powerlog_sources(context, extension=".PLSQL"):
    """(queryable path, evidence path) for every matching telemetry db found.

    Plain database files are used in place; .PLSQL.gz rotated archives are
    decompressed to a temp dir but keep their original path for reporting.
    -wal/-shm sidecars ride along on disk for SQLite and are not listed.
    A file matched by more than one glob is returned once.
    """
    sources = []
    for path in dict.fromkeys(str(p) for p in context.get_files_found()):
        if os.path.basename(path).startswith('._'):
            # AppleDouble metadata written when an extraction is handled on macOS.
            # ._CurrentPowerlog.PLSQL sits beside the real database and matches the
            # same glob, and opening it raises "file is not a database".
            continue
        if path.endswith(extension):
            sources.append((path, path))
        elif extension == ".PLSQL" and path.endswith(".PLSQL.gz"):
            materialized = _materialize_gz(path)
            if materialized:
                sources.append((materialized, path))
    return sources


def _resolve_table(source_path, prefix):
    """Actual table name for a family whose retention suffix varies by iOS.

    Matches the exact name first, then prefix + '_' (skipping _Array_ side
    tables). Returns None when the db has no such table.
    """
    if does_table_exist_in_db(source_path, prefix):
        return prefix
    for row in get_sqlite_db_records(source_path, '''
            SELECT name FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
        '''):
        name = row[0]
        if name.startswith(prefix + "_") and "_Array_" not in name:
            return name
    return None


def _load_time_offsets(source_path, offset_prefix=TIME_OFFSET_TABLE):
    """Read the log's clock corrections as parallel timestamp-sorted lists.

    Returns ([raw timestamp], [offset seconds]); empty lists when the table
    is missing or holds no usable rows.
    """
    offset_table = _resolve_table(source_path, offset_prefix)
    if not offset_table:
        return [], []
    stamps = []
    offsets = []
    for row in get_sqlite_db_records(source_path, f'''
            SELECT timestamp, system
            FROM "{offset_table}"
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


def _parse_powerlog_table(context, table, columns, row_builder, optional=(),
                          extension=".PLSQL", offset_prefix=TIME_OFFSET_TABLE):
    """Run one query shape over every matching telemetry db found.

    table may be an exact name or a family prefix whose retention suffix
    varies by iOS version. columns are selected as-is; names in optional are
    selected as NULL where a given file's schema lacks them, so row shape
    stays fixed across iOS versions.
    row_builder(corrected_ts, offset, row, evidence_path) -> tuple.
    """
    data_list = []
    sources = _powerlog_sources(context, extension)
    for db_path, evidence_path in sources:
        actual_table = _resolve_table(db_path, table)
        if not actual_table:
            continue
        select_parts = []
        for col in columns:
            if col in optional and not does_column_exist_in_db(
                    db_path, actual_table, col):
                select_parts.append(f'NULL AS "{col}"')
            else:
                select_parts.append(f'"{col}"')
        stamps, offsets = _load_time_offsets(db_path, offset_prefix)
        relative_path = context.get_relative_path(evidence_path)
        for row in get_sqlite_db_records(db_path, f'''
                SELECT {", ".join(select_parts)}
                FROM "{actual_table}"
                ORDER BY timestamp
            '''):
            ts, offset = _corrected_utc(row[0], stamps, offsets)
            data_list.append(row_builder(ts, offset, row, relative_path))
    source = "See source paths in data" if sources else ""
    return data_list, source


def _end_utc(start_dt, raw_start, raw_end):
    """Corrected end time: the corrected start plus the recorded raw duration.

    Both raw values run on the same internal clock, so the difference is
    offset-invariant; this avoids a second offset lookup that could straddle
    an offset boundary inside one short request.
    """
    if start_dt is None or raw_start is None or raw_end is None:
        return None
    return start_dt + timedelta(seconds=raw_end - raw_start)


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
@artifact_processor
def powerlogGenerativeSummarization(context):
    data_headers = (
        ("Start Time", "datetime"), ("End Time", "datetime"), "Bundle ID",
        "kind (as stored)", "exitReason (as stored)", "isUrgent (as stored)",
        "Request Identifier", "Time Offset (seconds)", "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "GenerativeFunctionMetrics_Summarization_1_2",
        ("timestamp", "timestampEnd", "bundleID", "kind", "exitReason",
         "isUrgent", "requestIdentifier"),
        lambda ts, offset, row, rel: (
            ts, _end_utc(ts, row[0], row[1]), row[2], row[3], row[4], row[5],
            row[6], offset, rel),
    )
    return data_headers, data_list, source


@artifact_processor
def powerlogGenerativeTextRequests(context):
    data_headers = (
        ("Start Time", "datetime"), ("End Time", "datetime"),
        "requestType (as stored)", "errorType (as stored)",
        "Input Tokens (as stored)", "Output Tokens (as stored)",
        "qos (as stored)", "Request Identifier", "Time Offset (seconds)",
        "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "GenerativeFunctionMetrics_tgiExecuteRequest_1_2",
        ("timestamp", "timestampEnd", "requestType", "errorType",
         "inputTokensCount", "outputTokensCount", "qos", "requestIdentifier"),
        lambda ts, offset, row, rel: (
            ts, _end_utc(ts, row[0], row[1]), row[2], row[3], row[4], row[5],
            row[6], row[7], offset, rel),
    )
    return data_headers, data_list, source


@artifact_processor
def powerlogGenerativeInferenceRequests(context):
    data_headers = (
        ("Start Time", "datetime"), ("End Time", "datetime"), "Use Case",
        "Created By", "On Behalf Of", "Inference Provider",
        "error (as stored)", "requestType (as stored)", "Session Identifier",
        "Time Offset (seconds)", "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "GenerativeFunctionMetrics_mmExecuteRequest_1_2",
        ("timestamp", "timestampEnd", "useCaseIdentifier",
         "createdByBundleIdentifier", "onBehalfOfBundleIdentifier",
         "inferenceProviderIdentifier", "error", "requestType",
         "sessionIdentifier"),
        lambda ts, offset, row, rel: (
            ts, _end_utc(ts, row[0], row[1]), row[2], row[3], row[4], row[5],
            row[6], row[7], row[8], offset, rel),
    )
    return data_headers, data_list, source


@artifact_processor
def powerlogGenerativeAssetLoad(context):
    data_headers = (
        ("Start Time", "datetime"), ("End Time", "datetime"),
        "Catalog Resource", "loadType (as stored)", "reason (as stored)",
        "result (as stored)", "Session Identifier", "Time Offset (seconds)",
        "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "GenerativeFunctionMetrics_assetLoad_1_2",
        ("timestamp", "timestampEnd", "catalogResourceIdentifier", "loadType",
         "reason", "result", "sessionIdentifier"),
        lambda ts, offset, row, rel: (
            ts, _end_utc(ts, row[0], row[1]), row[2], row[3], row[4], row[5],
            row[6], offset, rel),
    )
    return data_headers, data_list, source


@artifact_processor
def powerlogGenerativeOptIn(context):
    data_headers = (
        ("Timestamp", "datetime"), "Enabled", "Time Offset (seconds)",
        "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "GenerativeFunctionMetrics_OptIn_1_2",
        ("timestamp", "Enabled"),
        lambda ts, offset, row, rel: (ts, _yes_no(row[1]), offset, rel),
    )
    return data_headers, data_list, source

EPSQL_OFFSET = "PPTStorageOperator_TimeOffset"
BGSQL_OFFSET = "BackgroundProcessing_TimeOffset"


@artifact_processor
def powerTelemetryBatteryDataDaily(context):
    data_headers = (
        ("Timestamp", "datetime"), "Cycle Count", "Max Capacity (%)",
        "Nominal Charge Capacity (as stored)", "Charging Voltage (as stored)",
        "Time Offset (seconds)", "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "BatteryDataCollection_BDC_Daily",
        ("timestamp", "CycleCount", "MaxCapacityPercent",
         "NominalChargeCapacity", "ChargingVoltage"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], row[4], offset, rel),
        optional=("MaxCapacityPercent",),
        extension=".EPSQL", offset_prefix=EPSQL_OFFSET,
    )
    return data_headers, data_list, source


@artifact_processor
def powerTelemetrySmartCharging(context):
    data_headers = (
        ("Timestamp", "datetime"), "ChargeLimit (as stored)",
        "ChargingState (as stored)", "CheckPoint (as stored)",
        "DecisionMaker (as stored)", "InflowState (as stored)",
        "ModeOfOperation (as stored)", "Time Offset (seconds)", "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "BatteryDataCollection_BDC_SmartCharging",
        ("timestamp", "ChargeLimit", "ChargingState", "CheckPoint",
         "DecisionMaker", "InflowState", "ModeOfOperation"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], row[4], row[5], row[6], offset, rel),
        optional=("DecisionMaker",),
        extension=".EPSQL", offset_prefix=EPSQL_OFFSET,
    )
    return data_headers, data_list, source


@artifact_processor
def powerTelemetryBatteryHardware(context):
    data_headers = (
        ("Timestamp", "datetime"), "Design Capacity (as stored)",
        "ChemID (as stored)", "AlgoChemID (as stored)", "EEEE (as stored)",
        "YWW (as stored)", "Gas Gauge Firmware (as stored)",
        "Time Offset (seconds)", "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "BatteryDataCollection_BDC_Once",
        ("timestamp", "DesignCapacity", "ChemID", "AlgoChemID", "EEEE", "YWW",
         "GasGaugeFirmwareVersion"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], row[4], row[5], row[6], offset, rel),
        optional=("GasGaugeFirmwareVersion",),
        extension=".EPSQL", offset_prefix=EPSQL_OFFSET,
    )
    return data_headers, data_list, source


@artifact_processor
def powerTelemetryBatteryTrustedDaily(context):
    data_headers = (
        ("Timestamp", "datetime"), "Trusted Cycle Count",
        "Trusted Maximum Capacity (as stored)",
        "Trusted LifeTime Max WRdc (as stored)",
        ("Trusted Date Of First Use", "datetime"),
        "Time Offset (seconds)", "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "BatteryTrustedData_Daily",
        ("timestamp", "TrustedCycleCount", "TrustedMaximumCapacity",
         "TrustedLifeTimeMaxWRdc", "TrustedDateOfFirstUse"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], convert_unix_ts_to_utc(row[4]),
            offset, rel),
        extension=".EPSQL", offset_prefix=EPSQL_OFFSET,
    )
    return data_headers, data_list, source


@artifact_processor
def powerTelemetryBackgroundTaskInstances(context):
    data_headers = (
        ("Timestamp", "datetime"), "Process Name", "PID",
        ("Start Date", "datetime"), ("End Date", "datetime"),
        "Started On Battery", "Task ID", "Time Offset (seconds)",
        "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "BackgroundProcessing_TaskInstanceData",
        ("timestamp", "ProcessName", "PID", "StartDate", "EndDate",
         "StartedOnBattery", "TaskID"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], convert_unix_ts_to_utc(row[3]),
            convert_unix_ts_to_utc(row[4]), _yes_no(row[5]), row[6], offset,
            rel),
        extension=".BGSQL", offset_prefix=BGSQL_OFFSET,
    )
    return data_headers, data_list, source


@artifact_processor
def powerTelemetryBackgroundTaskMetadata(context):
    data_headers = (
        ("Timestamp", "datetime"), "Bundle ID", "Name", "Service Name",
        "Group Name", "Launch Reason", "Task ID", "Time Offset (seconds)",
        "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "BackgroundProcessing_TaskMetadata",
        ("timestamp", "BundleID", "Name", "ServiceName", "GroupName",
         "LaunchReason", "TaskID"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], row[4], row[5], row[6], offset, rel),
        extension=".BGSQL", offset_prefix=BGSQL_OFFSET,
    )
    return data_headers, data_list, source
