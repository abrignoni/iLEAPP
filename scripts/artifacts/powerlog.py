__artifacts_v2__ = {
    "powerlogApplicationRuntime": {
        "name": "PowerLog - Application Runtime",
        "description": (
            "Per-Bundle ID time values for each PowerLog aggregation window "
            "(PLAppTimeService_Aggregate_AppRunTime table), with the window start and end"
        ),
        "author": '@AlexisBrignoni, Codex, Claude',
        "creation_date": "2026-07-28",
        "last_update_date": '2026-11-21',
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "The field meanings and method below were derived independently from the table's "
            "schema, measured data and Apple's code. Code statements were read in PowerlogCore "
            "and PowerlogHelperdOperators on iOS 18.7. Other builds were not read. On every other"
            " version the statements rest on the schema and measurements. Each row is one Bundle "
            "ID in one aggregation window. Window Start is the stored timestamp, which the writer"
            " sets to the start of the window, plus the clock offset. Window End adds Window "
            "Seconds, the stored timeInterval. Window is Hour for 3600 seconds and Day for 86400."
            " Any other length reads Other. None was seen in the images tested. Day rows appeared"
            " only on the iOS 17 and later images tested. Day rows repeat seconds already in Hour"
            " rows, so the two must not be totalled together. Values are seconds. A value can be "
            "a proportional share, because the writer splits a span across the windows it "
            "overlaps. The time columns must not be added to each other. A PluggedIn column holds"
            " time the writer also files in its base column. On a few rows (19 of 90,071 "
            "measured) the PluggedIn value is larger than its base, and the cause is not "
            "established. Whether the other columns overlap one another is not established. The "
            "writer files BackgroundLocation time from a status bar state, and that this state is"
            " location use in every case is not established. PowerOutAccessories in Bundle ID is "
            "a literal written by Apple's code and is not an app; what its time value means is "
            "not established. A column absent from an older schema is empty. The table stores "
            "PowerLog's monotonic clock, and the code converts it to system time by adding the "
            "system value of PLStorageOperator_EventForward_TimeOffset. Those offset rows are "
            "samples, so this artifact pools them from all databases and applies the row nearest "
            "in stored time. That choice is this artifact's and not Apple's. Time Offset and "
            "Offset Row Distance are reported on each row. The distance can be days or weeks (up "
            "to about 58 days in the images tested), so Window Start is not exact to the second. "
            "Where no database holds an offset row, the stored value is shown uncorrected, on "
            "PowerLog's own clock, and Time Offset is empty. No image tested was in that state. "
            "Gzipped rotated logs and the databases under logs/powerlogs in a packed sysdiagnose "
            "are read from temporary copies. Rows equal on every column this artifact reads, all "
            "but the row id, are collapsed across databases: Copies counts them and Source File "
            "lists them, with a sysdiagnose member shown as archive >> member. Row State is empty"
            " unless one row id, with the same window and Bundle ID, holds different values in "
            "different databases. That was seen on one image tested (12 row ids), where every "
            "changed value was larger in the later file, which fits one row captured at different"
            " times. It then reads Earlier capture, Latest capture or Order not determined. The "
            "order comes from the file name and the table's row sequence. Leave Earlier capture "
            "rows out of a total. Order not determined did not occur in the images tested. "
            "Separate row ids for one window and Bundle ID are kept, and whether they add "
            "together is not established. PowerLog holds many additional version-specific tables "
            "that require separate validation."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "battery",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 2546 rows",
            "hickman_ios13": "iOS 13.3.1 | 3057 rows",
            "hickman_ios14": "iOS 14.3 | 5014 rows",
            "jess_ios15": "iOS 15.0.2 | 852 rows",
            "hickman_ios15": "iOS 15.3.1 | 4086 rows",
            "magnet_ios16": "iOS 16.1.1 | 933 rows",
            "abe_ios16": "iOS 16.5 | 19216 rows",
            "felix23_ios16": "iOS 16.5 | 8048 rows",
            "fsfull002_ios17": "iOS 17.1 | 1717 rows",
            "iphone11_ios17": "iOS 17.3 | 14672 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 6266 rows",
            "otto_ios17": "iOS 17.5.1 | 1923 rows",
            "felix_ios17": "iOS 17.6.1 | 7810 rows",
            "iphone14plus_ios18": "iOS 18.0 | 4127 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 2716 rows",
            "hc_ios18_7": "iOS 18.7.8 | 5684 rows",
            "hc_ios26": "iOS 26.5.2 | 3550 rows",
            "hc_ios26_sysdiag": "iOS 26.6 sysdiagnose | 5650 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 18883 rows",
        },
    },
    "powerlogBatteryLevel": {
        "name": "PowerLog - Battery Level",
        "description": "Battery level and charging state samples recorded by PowerLog "
                       "(PLBatteryAgent_EventBackward_BatteryUI table)",
        "author": '@AlexisBrignoni, Codex',
        "creation_date": "2026-08-03",
        "last_update_date": '2026-10-04',
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Level is reported as stored without an asserted percentage unit. IsCharging holds 0/1, "
            "reported as No/Yes with other values passed through as stored. Timestamps "
            "are adjusted using PowerLog's time-offset table and the applied offset is "
            "reported per row; see the PowerLog - Application Runtime notes for the "
            "mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "battery-charging",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 12915 rows",
            "hickman_ios13": "iOS 13.3.1 | 7659 rows",
            "hickman_ios14": "iOS 14.3 | 8386 rows",
            "jess_ios15": "iOS 15.0.2 | 2560 rows",
            "hickman_ios15": "iOS 15 | 7220 rows",
            "magnet_ios16": "iOS 16.1.1 | 210 rows",
            "abe_ios16": "iOS 16.5 | 16342 rows",
            "felix23_ios16": "iOS 16.5 | 6818 rows",
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
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Event, State, and Reason are integer codes reported as stored; their "
            "meanings are not decoded here. Timestamps are adjusted using "
            "PowerLog's time-offset table and the applied offset is reported per row; "
            "see the PowerLog - Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "power",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 65114 rows",
            "hickman_ios13": "iOS 13.3.1 | 19005 rows",
            "hickman_ios14": "iOS 14.3 | 19991 rows",
            "jess_ios15": "iOS 15.0.2 | 2960 rows",
            "hickman_ios15": "iOS 15 | 18018 rows",
            "magnet_ios16": "iOS 16.1.1 | 1472 rows",
            "abe_ios16": "iOS 16.5 | 21426 rows",
            "felix23_ios16": "iOS 16.5 | 7527 rows",
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
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "State and Reason are integer codes reported as stored; their meanings are "
            "not decoded here. Timestamps are adjusted using PowerLog's time-offset "
            "table and the applied offset is reported per row; see the PowerLog - "
            "Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "activity",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 9493 rows",
            "hickman_ios13": "iOS 13.3.1 | 14878 rows",
            "hickman_ios14": "iOS 14.3 | 19186 rows",
            "jess_ios15": "iOS 15.0.2 | 701 rows",
            "hickman_ios15": "iOS 15 | 5708 rows",
            "magnet_ios16": "iOS 16.1.1 | 360 rows",
            "abe_ios16": "iOS 16.5 | 31702 rows",
            "felix23_ios16": "iOS 16.5 | 4052 rows",
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
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Locked holds 0/1, reported as No/Yes with other values passed through as "
            "stored. Timestamps are adjusted using PowerLog's time-offset table and the "
            "applied offset is reported per row; see the PowerLog - Application Runtime "
            "notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "lock",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 214 rows",
            "hickman_ios13": "iOS 13.3.1 | 83 rows",
            "hickman_ios14": "iOS 14.3 | 99 rows",
            "jess_ios15": "iOS 15.0.2 | 21 rows",
            "hickman_ios15": "iOS 15 | 77 rows",
            "magnet_ios16": "iOS 16.1.1 | 3 rows",
            "abe_ios16": "iOS 16.5 | 295 rows",
            "felix23_ios16": "iOS 16.5 | 83 rows",
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
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "AutoLockType is an integer code reported as stored; its meaning is not "
            "decoded here. Timestamps are adjusted using PowerLog's time-offset table "
            "and the applied offset is reported per row; see the PowerLog - Application "
            "Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "clock",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 71 rows",
            "hickman_ios13": "iOS 13.3.1 | 160 rows",
            "hickman_ios14": "iOS 14.3 | 163 rows",
            "jess_ios15": "iOS 15.0.2 | 30 rows",
            "hickman_ios15": "iOS 15 | 193 rows",
            "magnet_ios16": "iOS 16.1.1 | 11 rows",
            "abe_ios16": "iOS 16.5 | 1275 rows",
            "felix23_ios16": "iOS 16.5 | 88 rows",
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
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "BundleId and Level are reported as stored; on the tested rows (iOS 12.4-26) Level "
            "was 0 or 1. Rows are sparse: no test image held more than 23. Timestamps are "
            "adjusted using PowerLog's time-offset table and the applied offset is reported per "
            "row; see the PowerLog - Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "zap",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 11 rows",
            "hickman_ios13": "iOS 13.3.1 | 10 rows",
            "hickman_ios14": "iOS 14.3 | 7 rows",
            "jess_ios15": "iOS 15.0.2 | 6 rows",
            "hickman_ios15": "iOS 15 | 8 rows",
            "magnet_ios16": "iOS 16.1.1 | 2 rows",
            "abe_ios16": "iOS 16.5 | 23 rows",
            "felix23_ios16": "iOS 16.5 | 8 rows",
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
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Brightness, SliderValue, lux, and mNits are reported as stored with the "
            "column names the database uses; no unit conversion is applied. Timestamps "
            "are adjusted using PowerLog's time-offset table and the applied offset is "
            "reported per row; see the PowerLog - Application Runtime notes for the "
            "mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "sun",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1271 rows",
            "hickman_ios13": "iOS 13.3.1 | 1445 rows",
            "hickman_ios14": "iOS 14.3 | 2251 rows",
            "jess_ios15": "iOS 15.0.2 | 262 rows",
            "hickman_ios15": "iOS 15 | 4787 rows",
            "magnet_ios16": "iOS 16.1.1 | 45 rows",
            "abe_ios16": "iOS 16.5 | 4311 rows",
            "felix23_ios16": "iOS 16.5 | 254 rows",
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
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "ActiveRoute and OutputCategory are text values reported verbatim; observed "
            "in test images (iOS 12.4-26): routes Speaker, Receiver, HeadphonesBT, "
            "CarAudioOutput, INVALID and categories Alarm, Ringtone, PhoneCall, "
            "Audio/Video, FindMyPhone, VoiceCommand. Active holds 0/1. ActivePID and "
            "BTEndpointType are not present in every schema; where absent the columns are "
            "reported empty. Timestamps are adjusted using PowerLog's time-offset table and the "
            "applied offset is reported per row; see the PowerLog - Application Runtime notes "
            "for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "headphones",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 183 rows",
            "hickman_ios13": "iOS 13.3.1 | 176 rows",
            "hickman_ios14": "iOS 14.3 | 344 rows",
            "jess_ios15": "iOS 15.0.2 | 20 rows",
            "hickman_ios15": "iOS 15 | 66 rows",
            "magnet_ios16": "iOS 16.1.1 | 4 rows",
            "abe_ios16": "iOS 16.5 | 2116 rows",
            "felix23_ios16": "iOS 16.5 | 87 rows",
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
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Values are reported as stored with the column names the database uses; no "
            "units are asserted. In test images, nonzero SystemInputVoltage values "
            "clustered near 5000 and 9000; the charging state at those times was not "
            "cross-checked here. SystemInputVoltage and SystemInputCurrent are absent "
            "from some iOS 16 schemas; where absent the columns are reported empty. "
            "Timestamps are adjusted using PowerLog's time-offset table and the "
            "applied offset is reported per row; see the PowerLog - Application "
            "Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
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
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "CameraType and State are integer codes reported as stored; their meanings "
            "are not decoded here. The table's wider column set varies by iOS version; "
            "only the columns present in every tested schema are parsed. Timestamps "
            "are adjusted using PowerLog's time-offset table and the applied offset is "
            "reported per row; see the PowerLog - Application Runtime notes for the "
            "mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "camera",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 957 rows",
            "hickman_ios13": "iOS 13.3.1 | 223 rows",
            "hickman_ios14": "iOS 14.3 | 286 rows",
            "jess_ios15": "iOS 15.0.2 | 8 rows",
            "hickman_ios15": "iOS 15 | 100 rows",
            "magnet_ios16": "iOS 16.1.1 | 1 rows",
            "abe_ios16": "iOS 16.5 | 322 rows",
            "felix23_ios16": "iOS 16.5 | 37 rows",
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
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "In the recorded sample data rows were returned only on iOS 18 and iOS 26 "
            "images. csIdentity holds process or bundle identifiers as recorded; "
            "modelURL holds a model file path. cacheHit, isPrecompiled, modelSize, and "
            "modelLoadingTime are reported as stored; no units are asserted. "
            "Timestamps are adjusted using PowerLog's time-offset table and the "
            "applied offset is reported per row; see the PowerLog - Application "
            "Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
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
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "In the recorded sample data rows were returned only on iOS 18 and iOS 26 "
            "images. csIdentity holds process or bundle identifiers as recorded; "
            "modelURL holds a model file path. Timestamps are adjusted using PowerLog's "
            "time-offset table and the applied offset is reported per row; see the "
            "PowerLog - Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
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
        "author": '@AlexisBrignoni, Codex',
        "creation_date": "2026-08-03",
        "last_update_date": '2026-10-04',
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "bundleID holds app bundle identifiers as recorded. kind, exitReason, "
            "and isUrgent are integer codes reported as stored. In test data these "
            "tables held rows only on an Apple Intelligence capable device (iPhone 16, "
            "iOS 26.5.2 sysdiagnose). A zero row count elsewhere does not establish "
            "whether the table exists. Timestamps are adjusted using PowerLog's time-offset table and "
            "the applied offset is reported per row; end times preserve the recorded "
            "duration against the corrected start. See the PowerLog - Application "
            "Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
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
        "description": "Request records recorded by PowerLog in the "
                       "GenerativeFunctionMetrics_tgiExecuteRequest_1_2 table (token "
                       "counts and request type as stored)",
        "author": '@AlexisBrignoni, Codex',
        "creation_date": "2026-08-03",
        "last_update_date": '2026-10-04',
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Token counts, requestType, errorType and qos are reported as stored. No "
            "latency column is read here. The table carries additional "
            "columns whose names begin with sd_ that are not parsed here. "
            "In test data these tables held rows only on an Apple Intelligence "
            "capable device (iPhone 16, iOS 26.5.2 sysdiagnose). A zero row count elsewhere "
            "does not establish whether the table exists. Timestamps are adjusted using "
            "PowerLog's time-offset table and the applied offset is reported per "
            "row; end times preserve the recorded duration against the corrected "
            "start. See the PowerLog - Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
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
        "description": "Request records recorded by PowerLog in the "
                       "GenerativeFunctionMetrics_mmExecuteRequest_1_2 table (use case "
                       "and bundle identifiers as stored)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "useCaseIdentifier is a text value reported verbatim; observed values "
            "include summarization.summarizeMailMessage, "
            "classification.classifyMailMessage, memoryCreation.QueryUnderstanding, "
            "and textUnderstanding.TextEventExtraction. Bundle and provider "
            "identifiers are reported as recorded. "
            "In test data these tables held rows only on an Apple Intelligence "
            "capable device (iPhone 16, iOS 26.5.2 sysdiagnose). Timestamps are "
            "adjusted using PowerLog's time-offset table and the applied offset is "
            "reported per row; end times preserve the recorded duration against the "
            "corrected start. See the PowerLog - Application Runtime notes for the "
            "mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
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
        "author": '@AlexisBrignoni, Codex',
        "creation_date": "2026-08-03",
        "last_update_date": '2026-10-04',
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "catalogResourceIdentifier is reported verbatim; observed values "
            "include fm.language.instruct_3b variants and gm.safety_* resources; what "
            "each identifier refers to is not established here. loadType, reason, and "
            "result are integer codes reported as stored. In test data these tables "
            "held rows only on an Apple Intelligence capable device (iPhone 16, iOS "
            "26.5.2 sysdiagnose). A zero row count elsewhere does not establish "
            "whether the table exists. Timestamps are adjusted using PowerLog's time-offset table and the "
            "applied offset is reported per row; end times preserve the recorded "
            "duration against the corrected start. See the PowerLog - Application "
            "Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
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
        "author": '@AlexisBrignoni, Codex',
        "creation_date": "2026-08-03",
        "last_update_date": '2026-10-04',
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Enabled holds 0/1, reported as No/Yes with other values passed "
            "through as stored. On the device with data, raw timestamps for this "
            "table were decades off wall-clock time until corrected by the "
            "time-offset table, so the reported offset column is essential "
            "context. "
            "In test data these tables held rows only on an Apple Intelligence "
            "capable device (iPhone 16, iOS 26.5.2 sysdiagnose). A zero row count elsewhere "
            "does not establish whether the table exists. Timestamps are adjusted using "
            "PowerLog's time-offset table and the applied offset is reported per "
            "row. See the PowerLog - Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
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
        "author": '@AlexisBrignoni, Codex',
        "creation_date": "2026-08-03",
        "last_update_date": '2026-10-04',
        "requirements": "none",
        "category": "Power Telemetry",
        "notes": (
            "CycleCount, MaxCapacityPercent, NominalChargeCapacity, and "
            "ChargingVoltage are reported as stored under the database field names; no units "
            "are asserted from those names. MaxCapacityPercent is not present in every "
            "schema and is reported empty where absent. Raw timestamp values are adjusted "
            "using the time-offset table in this log (PPTStorageOperator_TimeOffset; its "
            "retention suffix varies by iOS version) and the applied offset is reported per "
            "row; see the PowerLog - Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/PerfPowerTelemetry/*/*.EPSQL*",
            "*/powerlogs/*.EPSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
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
            "felix23_ios16": "iOS 16.5 | 316 rows",
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
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Power Telemetry",
        "notes": (
            "ChargeLimit, ChargingState, CheckPoint, DecisionMaker, InflowState, "
            "and ModeOfOperation are integer codes reported as stored; their "
            "meanings are not decoded here. DecisionMaker is not present in every schema "
            "and is reported empty where absent. "
            "Raw timestamp values are adjusted using the time-offset table in "
            "this log (PPTStorageOperator_TimeOffset; its retention suffix "
            "varies by iOS version) and the applied offset is reported per row; "
            "see the PowerLog - Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/PerfPowerTelemetry/*/*.EPSQL*",
            "*/powerlogs/*.EPSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
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
            "felix23_ios16": "iOS 16.5 | 48 rows",
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
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Power Telemetry",
        "notes": (
            "DesignCapacity, ChemID, AlgoChemID, EEEE, YWW, and "
            "GasGaugeFirmwareVersion are reported as stored; no interpretation "
            "is applied. No image in the recorded sample data holds more than three "
            "rows. Rows are not deduplicated across copies of a log, so one record can "
            "appear once per copy. Raw timestamp values are adjusted using the "
            "time-offset table in this log (PPTStorageOperator_TimeOffset; its "
            "retention suffix varies by iOS version) and the applied offset is "
            "reported per row; see the PowerLog - Application Runtime notes for the "
            "mechanism."
        ),
        "paths": (
            "*/PerfPowerTelemetry/*/*.EPSQL*",
            "*/powerlogs/*.EPSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
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
            "felix23_ios16": "iOS 16.5 | 3 rows",
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
        "author": '@AlexisBrignoni, Codex',
        "creation_date": "2026-08-03",
        "last_update_date": '2026-10-04',
        "requirements": "none",
        "category": "Power Telemetry",
        "notes": (
            "TrustedCycleCount, TrustedMaximumCapacity, and TrustedLifeTimeMaxWRdc "
            "are reported as stored. TrustedDateOfFirstUse decodes as a standard "
            "Unix timestamp, unlike the offset-skewed timestamp column: on two "
            "validation devices it held one stable calendar date each, preceding "
            "every daily sample. In the recorded sample data rows were returned on two "
            "images, dexter_ios18 (42 rows) and ai16_ios26_sysdiag (364 rows); rows "
            "are not deduplicated across copies of a log, so a row count is not a "
            "count of distinct days. Raw timestamp values are adjusted using the "
            "time-offset table in this log (PPTStorageOperator_TimeOffset; its "
            "retention suffix varies by iOS version) and the applied offset is "
            "reported per row; see the PowerLog - Application Runtime notes for the "
            "mechanism."
        ),
        "paths": (
            "*/PerfPowerTelemetry/*/*.EPSQL*",
            "*/powerlogs/*.EPSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
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
        "author": '@AlexisBrignoni, Codex',
        "creation_date": "2026-08-03",
        "last_update_date": '2026-10-04',
        "requirements": "none",
        "category": "Power Telemetry",
        "notes": (
            "StartDate and EndDate hold standard Unix timestamps as stored; the "
            "row timestamp runs on the internal clock and is offset-corrected "
            "here. StartedOnBattery holds 0/1, reported as No/Yes. Observed only in "
            "iOS 26 test data; iOS 18 background processing logs exist without this "
            "table. Raw timestamp values are adjusted using the time-offset table in "
            "this log (BackgroundProcessing_TimeOffset) and the applied offset "
            "is reported per row; see the PowerLog - Application Runtime notes "
            "for the mechanism."
        ),
        "paths": (
            "*/PerfPowerTelemetry/*/*.BGSQL*",
            "*/powerlogs/*.BGSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
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
        "description": "Background task metadata rows from the PerfPowerTelemetry "
                       "background processing log (BackgroundProcessing_TaskMetadata table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-09-18",
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
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
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
    "powerlogInCallService": {
        "name": "PowerLog - In Call Service",
        "description": "Call service events recorded by PowerLog (PLXPCAgent_EventForward_InCallService table)",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-13",
        "last_update_date": "2026-11-13",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Bundle ID and Provider Identifier are the stored bundleID and providerIdentifier "
            "values; their meaning is not established here. Call Sub Type and Status are reported "
            "as stored. On the 593 rows read from the images in sample_data (iOS 12.4 to 18.7.8), "
            "Status held callStart, callStop, callForegrounded and callBackgrounded; Call Sub Type "
            "held kCallSubTypeVoLTE, kCallSubTypeTelephony or kCallSubTypeWifi, and was empty on "
            "286 rows. Video is an integer reported as stored; it held 0 or 1 on those rows. A row "
            "is one record read from one PowerLog file; rows are not deduplicated across files, so "
            "a record held in the current log and in a rotated archive appears once per file. A row "
            "does not establish the call's direction or that it connected. Timestamps are adjusted "
            "using PowerLog's time-offset table and the applied offset is reported in its own "
            "column; where a file holds no offset entries the column is empty and the timestamp is "
            "on the log's uncorrected clock (seen on 5 archives of hc_ios18_7). See the PowerLog - "
            "Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "phone-call",
        "sample_data": {
            'ctf2020_ios12': 'iOS 12.4 | 22 rows',
            'hickman_ios13': 'iOS 13.3.1 | 91 rows',
            'hickman_ios14': 'iOS 14.3 | 199 rows',
            'jess_ios15': 'iOS 15.0.2 | 6 rows',
            'magnet_ios16': 'iOS 16.1.1 | 0 rows',
            'abe_ios16': 'iOS 16.5 | 57 rows',
            'felix23_ios16': 'iOS 16.5 | 8 rows',
            'fsfull002_ios17': 'iOS 17.1 | 18 rows',
            'iphone11_ios17': 'iOS 17.3 | 87 rows',
            'otto_ios17': 'iOS 17.5.1 | 4 rows',
            'felix_ios17': 'iOS 17.6.1 | 0 rows',
            'iphone14plus_ios18': 'iOS 18.0 | 0 rows',
            'dexter_ios18': 'iOS 18.3.2 | 0 rows (only empty Quarantine .PLSQL files)',
            'iphone12_ios18': 'iOS 18.7 | 81 rows',
            'hc_ios18_7': 'iOS 18.7.8 | 20 rows',
        },
    },
    "powerlogLightningConnector": {
        "name": "PowerLog - Lightning Connector Status",
        "description": "Lightning connector status records logged by PowerLog (PLBatteryAgent_EventForward_LightningConnectorStatus table)",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-13",
        "last_update_date": "2026-11-13",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Accessory Power Mode is the stored IOAccessoryPowerMode integer, reported as stored; "
            "its values are not decoded here. On the 35,150 rows read from the images in "
            "sample_data it held 1 (17,647 rows), 3 (17,502 rows) or 4 (1 row), and held only 1 on "
            "iphone11_ios17. A row is one record read from one PowerLog file; consecutive rows can "
            "hold the same value, and rows are not deduplicated across files. Timestamps are "
            "adjusted using PowerLog's time-offset table and the applied offset is reported in its "
            "own column; where a file holds no offset entries the column is empty and the timestamp "
            "is on the log's uncorrected clock (seen on 5 archives of hc_ios18_7). See the PowerLog "
            "- Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "link",
        "sample_data": {
            'ctf2020_ios12': 'iOS 12.4 | 10298 rows',
            'hickman_ios13': 'iOS 13.3.1 | 2049 rows',
            'hickman_ios14': 'iOS 14.3 | 21 rows',
            'jess_ios15': 'iOS 15.0.2 | 22 rows',
            'magnet_ios16': 'iOS 16.1.1 | 2 rows',
            'abe_ios16': 'iOS 16.5 | 1699 rows',
            'felix23_ios16': 'iOS 16.5 | 14 rows',
            'fsfull002_ios17': 'iOS 17.1 | 510 rows',
            'iphone11_ios17': 'iOS 17.3 | 24 rows',
            'otto_ios17': 'iOS 17.5.1 | 1010 rows',
            'felix_ios17': 'iOS 17.6.1 | 15 rows',
            'iphone14plus_ios18': 'iOS 18.0 | 9 rows',
            'dexter_ios18': 'iOS 18.3.2 | 0 rows (only empty Quarantine .PLSQL files)',
            'iphone12_ios18': 'iOS 18.7 | 19452 rows',
            'hc_ios18_7': 'iOS 18.7.8 | 25 rows',
        },
    },
    "powerlogNetworkUsage": {
        "name": "PowerLog - Network Usage",
        "description": "Per-interface DownBytes and UpBytes counters recorded by PowerLog (PLNetworkAgent_EventBackward_CumulativeNetworkUsage table)",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-13",
        "last_update_date": "2026-11-13",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Interface is the stored Interface value; on the 22,101 rows read from the images in "
            "sample_data it held awdl0, en0 or pdp_ip0, one row each per timestamp. Down Bytes and "
            "Up Bytes are the stored DownBytes and UpBytes integers, reported as stored. The table "
            "name calls them cumulative; a counter was in some rows lower than the previous row for "
            "the same interface, so the values do not only increase. The table has no process or "
            "app column; the counters are per interface. A row is one record read from one PowerLog "
            "file and rows are not deduplicated across files. Timestamps are adjusted using "
            "PowerLog's time-offset table and the applied offset is reported in its own column; "
            "where a file holds no offset entries the column is empty and the timestamp is on the "
            "log's uncorrected clock. See the PowerLog - Application Runtime notes for the "
            "mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "activity",
        "sample_data": {
            'ctf2020_ios12': 'iOS 12.4 | 2664 rows',
            'hickman_ios13': 'iOS 13.3.1 | 2430 rows',
            'hickman_ios14': 'iOS 14.3 | 3120 rows',
            'jess_ios15': 'iOS 15.0.2 | 630 rows',
            'magnet_ios16': 'iOS 16.1.1 | 240 rows',
            'abe_ios16': 'iOS 16.5 | 2688 rows',
            'felix23_ios16': 'iOS 16.5 | 2262 rows',
            'fsfull002_ios17': 'iOS 17.1 | 693 rows',
            'iphone11_ios17': 'iOS 17.3 | 2748 rows',
            'otto_ios17': 'iOS 17.5.1 | 438 rows',
            'felix_ios17': 'iOS 17.6.1 | 2016 rows',
            'iphone14plus_ios18': 'iOS 18.0 | 693 rows',
            'dexter_ios18': 'iOS 18.3.2 | 0 rows (only empty Quarantine .PLSQL files)',
            'iphone12_ios18': 'iOS 18.7 | 723 rows',
            'hc_ios18_7': 'iOS 18.7.8 | 756 rows',
        },
    },
    "powerlogTimeZone": {
        "name": "PowerLog - Time Zone",
        "description": "Device time-zone records logged by PowerLog (PLLocaleAgent_EventForward_TimeZone table)",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-13",
        "last_update_date": "2026-11-13",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Time Zone Name is the stored TimeZoneName text; on the 223 rows read from the images "
            "in sample_data it had the Area/Location form of an IANA zone name. Seconds From GMT "
            "and Is In DST are reported as stored. Country Code, Locale ID and Trigger are reported "
            "as stored; Trigger held powerlog or kCFTimeZoneSystemTimeZoneDidChangeNotification. On "
            "iphone11_ios17 all 24 rows held one Time Zone Name, one Country Code, one Locale ID "
            "and the Trigger value powerlog. A row is one time-zone record read from one PowerLog "
            "file and rows are not deduplicated across files. Timestamps are adjusted using "
            "PowerLog's time-offset table and the applied offset is reported in its own column; "
            "where a file holds no offset entries the column is empty and the timestamp is on the "
            "log's uncorrected clock (seen on 5 archives of hc_ios18_7). See the PowerLog - "
            "Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
            "*/powerlogs/*.PLSQL*",
            "*/sysdiagnose_*.tar.gz", "*/*_sysdiagnose.tar.gz",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "clock",
        "sample_data": {
            'ctf2020_ios12': 'iOS 12.4 | 20 rows',
            'hickman_ios13': 'iOS 13.3.1 | 15 rows',
            'hickman_ios14': 'iOS 14.3 | 25 rows',
            'jess_ios15': 'iOS 15.0.2 | 16 rows',
            'magnet_ios16': 'iOS 16.1.1 | 3 rows',
            'abe_ios16': 'iOS 16.5 | 26 rows',
            'felix23_ios16': 'iOS 16.5 | 22 rows',
            'fsfull002_ios17': 'iOS 17.1 | 9 rows',
            'iphone11_ios17': 'iOS 17.3 | 24 rows',
            'otto_ios17': 'iOS 17.5.1 | 5 rows',
            'felix_ios17': 'iOS 17.6.1 | 22 rows',
            'iphone14plus_ios18': 'iOS 18.0 | 6 rows',
            'dexter_ios18': 'iOS 18.3.2 | 0 rows (only empty Quarantine .PLSQL files)',
            'iphone12_ios18': 'iOS 18.7 | 14 rows',
            'hc_ios18_7': 'iOS 18.7.8 | 16 rows',
        },
    },
}

import atexit
from contextlib import closing
import glob
import gzip
import os
import re
import shutil
import tarfile
import tempfile
import time
import zlib
from bisect import bisect_left, bisect_right
from collections import Counter
from datetime import timedelta

from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    does_column_exist_in_db,
    does_table_exist_in_db,
    get_sqlite_db_records,
    get_sysdiagnose_files,
    logfunc,
)

TIME_OFFSET_TABLE = "PLStorageOperator_EventForward_TimeOffset"

# Rotated archives are decompressed once per session and reused by every
# artifact in this module; maps original .PLSQL.gz path -> decompressed copy.
_GZ_CACHE = {}
# 'dir' -> session temp directory for the decompressed copies, first use only.
# The copies taken out of packed sysdiagnoses go in the same directory.
_GZ_TEMP = {}
_GZ_TEMP_PREFIX = "ileapp_powerlog_gz_"

# Packed sysdiagnoses are read once per session as well; maps archive path ->
# [(extracted copy, 'archive >> member')] for every telemetry db it holds under
# logs/powerlogs/.
_SYSDIAG_CACHE = {}
# A sysdiagnose keeps its telemetry dbs under logs/powerlogs/. The sysdiagnoses
# checked (iOS 13.3.1 to 26) held only the database files there, no -wal or -shm.
_SYSDIAG_TELEMETRY = re.compile(r"/logs/powerlogs/[^/]+\.(?:PLSQL|EPSQL|BGSQL)$")

# How long an abandoned directory must have gone untouched before another run reclaims it.
# Generous on purpose: the cost of waiting is disk space, the cost of being wrong is
# deleting decompressed databases out from under an iLEAPP that is still reading them.
_STALE_TEMP_AGE_SECONDS = 24 * 60 * 60


def _remove_gz_temp():
    """Delete this run's decompressed and extracted copies.

    The rotated archives expand to their full uncompressed size, so a run over an
    extraction with a long PowerLog history leaves hundreds of megabytes behind. Nothing
    used to remove them: 135 directories totalling 12 GB were found in the system temp
    directory of one machine, from two days of ordinary runs that all completed normally.
    """
    temp_dir = _GZ_TEMP.pop("dir", None)
    _GZ_CACHE.clear()
    _SYSDIAG_CACHE.clear()
    if temp_dir:
        shutil.rmtree(temp_dir, ignore_errors=True)


atexit.register(_remove_gz_temp)


def _remove_stale_gz_temps():
    """Reclaim directories left by a run that was killed before atexit could fire.

    Only directories untouched for _STALE_TEMP_AGE_SECONDS are removed, so a concurrent
    iLEAPP keeps its own. ignore_errors leaves anything held open by another process in
    place rather than half-deleting it.
    """
    pattern = os.path.join(tempfile.gettempdir(), f"{_GZ_TEMP_PREFIX}*")
    cutoff = time.time() - _STALE_TEMP_AGE_SECONDS
    for path in glob.glob(pattern):
        try:
            if os.path.isdir(path) and os.path.getmtime(path) < cutoff:
                shutil.rmtree(path, ignore_errors=True)
        except OSError:
            continue


def _session_temp_dir():
    """This run's temp dir for decompressed and extracted copies, made on first use."""
    temp_dir = _GZ_TEMP.get("dir")
    if not temp_dir:
        _remove_stale_gz_temps()
        temp_dir = tempfile.mkdtemp(prefix=_GZ_TEMP_PREFIX)
        _GZ_TEMP["dir"] = temp_dir
    return temp_dir


def _materialize_gz(gz_path):
    """Decompress a rotated PowerLog archive to a session temp dir, once.

    Returns the decompressed path, or None when the archive cannot be read.
    The original file is only ever opened for reading.
    """
    cached = _GZ_CACHE.get(gz_path)
    if gz_path in _GZ_CACHE and cached is None:
        return None
    if cached and os.path.exists(cached):
        return cached
    out_name = f"{len(_GZ_CACHE):04d}_{os.path.basename(gz_path)[:-3]}"
    out_path = os.path.join(_session_temp_dir(), out_name)
    try:
        with gzip.open(gz_path, "rb") as src, open(out_path, "wb") as dst:
            shutil.copyfileobj(src, dst)
    except (OSError, EOFError, gzip.BadGzipFile) as e:
        if isinstance(e, (EOFError, gzip.BadGzipFile)):
            # The archive itself is damaged, so another attempt reads the same bytes.
            _GZ_CACHE[gz_path] = None
        try:
            os.remove(out_path)
        except FileNotFoundError:
            pass
        logfunc(f"Could not decompress {gz_path}: {e}")
        return None
    _GZ_CACHE[gz_path] = out_path
    return out_path


def _materialize_sysdiagnose(archive_path):
    """Copy the telemetry dbs out of a packed sysdiagnose to the session temp dir, once.

    SQLite needs a file on disk and get_sysdiagnose_files() yields a stream, so each
    matching member is written out. Returns [(copy path, 'archive >> member')], empty
    when the archive holds none or is not a sysdiagnose the helper reads. A member
    that fails part way through is dropped rather than queried incomplete. The
    archive is only ever opened for reading.
    """
    cached = _SYSDIAG_CACHE.get(archive_path)
    if cached is not None:
        return cached
    copies = []
    target_dir = None
    partial = None
    members = get_sysdiagnose_files([archive_path], _SYSDIAG_TELEMETRY, text_mode=False)
    try:
        for stream, evidence_path in members:
            if target_dir is None:
                target_dir = os.path.join(_session_temp_dir(),
                                          f"sysdiagnose_{len(_SYSDIAG_CACHE):04d}")
                os.makedirs(target_dir, exist_ok=True)
            member_name = evidence_path.rsplit(" >> ", 1)[-1]
            out_path = os.path.join(
                target_dir, f"{len(copies):02d}_{os.path.basename(member_name)}")
            partial = out_path
            with open(out_path, "wb") as dst:
                shutil.copyfileobj(stream, dst)
            partial = None
            copies.append((out_path, evidence_path))
    except (OSError, EOFError, tarfile.TarError, zlib.error) as e:
        logfunc(f"Could not read the telemetry databases in {archive_path}: {e}")
        if partial and os.path.exists(partial):
            os.remove(partial)
    finally:
        members.close()
    _SYSDIAG_CACHE[archive_path] = copies
    return copies


def _powerlog_sources(context, extension=".PLSQL"):
    """(queryable path, evidence path) for every matching telemetry db found.

    Plain database files are used in place; .PLSQL.gz rotated archives are
    decompressed to a temp dir but keep their original path for reporting.
    The telemetry dbs under logs/powerlogs/ in a packed sysdiagnose_*.tar.gz or *_sysdiagnose.tar.gz
    are copied out to the same temp dir and reported as 'archive >> member'.
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
        elif ".tar" in os.path.basename(path):
            # get_sysdiagnose_files() decides which archives are sysdiagnoses and skips
            # IN_PROGRESS_ ones. Every family is copied on first use, so the .EPSQL and
            # .BGSQL artifacts read the same copies.
            sources.extend(pair for pair in _materialize_sysdiagnose(path)
                           if pair[0].endswith(extension))
    return sources


def _resolve_table(source_path, prefix):
    """Actual table name for a family whose retention suffix varies by iOS.

    Matches the exact name first, then prefix + '_' (skipping _Array_ side
    tables). Returns None when the db has no such table.
    """
    if does_table_exist_in_db(source_path, prefix):
        return prefix
    with closing(get_sqlite_db_records(source_path, '''
            SELECT name FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
        ''')) as records:
        for row in records:
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


def _parse_powerlog_table(context, headers, table, columns, row_builder, optional=(),
                          extension=".PLSQL", offset_prefix=TIME_OFFSET_TABLE):
    """Run one query shape over every matching telemetry db found.

    table may be an exact name or a family prefix whose retention suffix
    varies by iOS version. columns are selected as-is; names in optional are
    selected as NULL where a given file's schema lacks them, so row shape
    stays fixed across iOS versions.
    row_builder(corrected_ts, offset, row, evidence_path) -> tuple.

    Rows go to LAVA as they are read rather than being collected first. The
    largest of these tables runs to six figures on one device, and the core
    replays the rows from LAVA for the other outputs, so nothing here has to
    hold them. headers is needed up front because the row writer registers the
    table from them on the first row.
    """
    results = context.create_artifact_result(headers=headers)
    sources = _powerlog_sources(context, extension)
    # The files that rows were read from.
    source_paths = set()
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
                ORDER BY timestamp, rowid
            '''):
            ts, offset = _corrected_utc(row[0], stamps, offsets)
            results.add_row(row_builder(ts, offset, row, relative_path))
            source_paths.add(evidence_path)
    return results, '\n'.join(sorted(source_paths))


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


_APP_RUN_TIME_TABLE = "PLAppTimeService_Aggregate_AppRunTime"
_APP_RUN_TIME_STATES = (
    "ScreenOnTime", "ScreenOnPluggedInTime", "BackgroundTime", "BackgroundPluggedInTime",
    "BackgroundAudioPlayingTime", "BackgroundAudioPlayingTimePluggedIn",
    "BackgroundAudioNowPlayingTime", "BackgroundAudioNowPlayingPluggedInTime",
    "BackgroundLocationTime", "BackgroundLocationPluggedInTime",
    "BackgroundLocationAudioTime", "BackgroundLocationAudioPluggedInTime",
    "InCallScreenOnTime", "InCallBackgroundTime",
)
_APP_RUN_TIME_WINDOWS = {3600: "Hour", 86400: "Day"}


def _nearest_offset(stamps, offsets, raw_ts):
    """(offset, distance in seconds) of the pooled offset row nearest in stored time."""
    if not stamps or not isinstance(raw_ts, (int, float)):
        return None, None
    after = bisect_left(stamps, raw_ts)
    before = after - 1
    if before < 0:
        chosen = after
    elif after >= len(stamps):
        chosen = before
    else:
        chosen = before if raw_ts - stamps[before] <= stamps[after] - raw_ts else after
    return offsets[chosen], abs(raw_ts - stamps[chosen])


def _file_recency(db_path, evidence_path):
    """Sort key for a database: current log, then the date in its name, then row sequence."""
    name = os.path.basename(evidence_path.split(" >> ")[-1])
    dated = re.search(r"\d{4}-\d{2}-\d{2}", name)
    sequence = -1
    if does_table_exist_in_db(db_path, "sqlite_sequence"):
        for row in get_sqlite_db_records(db_path, f"""
                SELECT seq FROM sqlite_sequence WHERE name = '{_APP_RUN_TIME_TABLE}'
                """):
            sequence = row[0]
    return name.startswith("CurrentPowerlog"), dated.group(0) if dated else "", sequence


def _app_run_time_groups(context):
    """Rows of every database, equal rows collapsed, with the pooled offset rows."""
    groups = {}
    recency = {}
    pooled = set()
    for db_path, evidence_path in _powerlog_sources(context):
        stamps, offsets = _load_time_offsets(db_path)
        pooled.update(zip(stamps, offsets))
        table = _resolve_table(db_path, _APP_RUN_TIME_TABLE)
        if not table:
            continue
        recency[evidence_path] = _file_recency(db_path, evidence_path)
        wanted = ("timestamp", "timeInterval", "BundleID") + _APP_RUN_TIME_STATES
        select = ", ".join(f'"{col}"' if does_column_exist_in_db(db_path, table, col)
                           else f'NULL AS "{col}"' for col in wanted)
        seen = Counter()
        for row in get_sqlite_db_records(db_path, f'''
                SELECT rowid, {select} FROM "{table}" ORDER BY rowid
                '''):
            content = (row[1], row[2], row[3], tuple(row[4:]))
            # Equal rows in one file stay separate: the nth copy in one file can
            # only collapse onto the nth copy in another.
            occurrence = seen[content]
            seen[content] += 1
            groups.setdefault((content, occurrence), []).append((evidence_path, row[0]))
    return groups, recency, sorted(pooled)


def _app_run_time_states(groups, recency):
    """Whether each group is one capture of a row that changed between files."""
    lineage = {}
    for (content, _occurrence), sources in groups.items():
        for evidence_path, row_id in sources:
            versions = lineage.setdefault((row_id,) + content[:3], {})
            rank = recency[evidence_path]
            if content[3] not in versions or rank > versions[content[3]]:
                versions[content[3]] = rank

    def state(content, sources):
        found = set()
        for _evidence_path, row_id in sources:
            versions = lineage[(row_id,) + content[:3]]
            if len(versions) < 2:
                continue
            newest = max(versions.values())
            if versions[content[3]] < newest:
                found.add("Earlier capture")
            elif sum(rank == newest for rank in versions.values()) > 1:
                found.add("Order not determined")
            else:
                found.add("Latest capture")
        return ", ".join(sorted(found))
    return state


@artifact_processor
def powerlogApplicationRuntime(context):
    data_headers = (
        ("Window Start", "datetime"), ("Window End", "datetime"), "Window Seconds", "Window",
        "Bundle ID",
    ) + tuple(f"{column} (seconds)" for column in _APP_RUN_TIME_STATES) + (
        "Time Offset (seconds)", "Offset Row Distance (seconds)", "Row State", "Copies",
        "Source File",
    )
    results = context.create_artifact_result(headers=data_headers)
    groups, recency, pooled = _app_run_time_groups(context)
    stamps = [stamp for stamp, _offset in pooled]
    offsets = [offset for _stamp, offset in pooled]
    state_of = _app_run_time_states(groups, recency)
    relative = {path: context.get_relative_path(path) for path in recency}

    def order(item):
        (raw_ts, interval, bundle, stored), occurrence = item[0]
        return (raw_ts if isinstance(raw_ts, (int, float)) else float("inf"),
                interval if isinstance(interval, (int, float)) else float("inf"),
                bundle or "", repr(stored), occurrence)

    for (content, _occurrence), sources in sorted(groups.items(), key=order):
        raw_ts, interval, bundle, stored = content
        offset, distance = _nearest_offset(stamps, offsets, raw_ts)
        start = None
        if isinstance(raw_ts, (int, float)):
            start = convert_unix_ts_to_utc(raw_ts + (offset or 0))
        end = None
        if start is not None and isinstance(interval, (int, float)):
            end = start + timedelta(seconds=interval)
        window = _APP_RUN_TIME_WINDOWS.get(interval, "" if interval is None else "Other")
        files = "\n".join(sorted({relative[path] for path, _row_id in sources}))
        results.add_row((start, end, interval, window, bundle) + stored + (
            offset, distance, state_of(content, sources), len(sources), files))
    return data_headers, results, "\n".join(sorted(recency))


@artifact_processor
def powerlogBatteryLevel(context):
    data_headers = (
        ("Timestamp", "datetime"), "Level (as stored)", "Is Charging",
        "Time Offset (seconds)", "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "PLBatteryAgent_EventBackward_BatteryUI",
        ("timestamp", "Level", "IsCharging"),
        lambda ts, offset, row, rel: (ts, row[1], _yes_no(row[2]), offset, rel),
    )
    return data_headers, results, source


@artifact_processor
def powerlogDevicePowerState(context):
    data_headers = (
        ("Timestamp", "datetime"), "Event (as stored)", "State (as stored)",
        "Reason (as stored)", "UUID", "Time Offset (seconds)", "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "PLSleepWakeAgent_EventForward_PowerState",
        ("timestamp", "Event", "State", "Reason", "UUID"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], row[4], offset, rel),
    )
    return data_headers, results, source


@artifact_processor
def powerlogAppState(context):
    data_headers = (
        ("Timestamp", "datetime"), "Identifier", "PID", "State (as stored)",
        "Reason (as stored)", "Time Offset (seconds)", "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "PLApplicationAgent_EventForward_Application",
        ("timestamp", "Identifier", "pid", "State", "Reason"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], row[4], offset, rel),
    )
    return data_headers, results, source


@artifact_processor
def powerlogDeviceLock(context):
    data_headers = (
        ("Timestamp", "datetime"), "Locked", "Time Offset (seconds)",
        "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "PLSpringBoardAgent_EventForward_SBLock",
        ("timestamp", "Locked"),
        lambda ts, offset, row, rel: (ts, _yes_no(row[1]), offset, rel),
    )
    return data_headers, results, source


@artifact_processor
def powerlogAutolock(context):
    data_headers = (
        ("Timestamp", "datetime"), "AutoLockType (as stored)",
        "Time Offset (seconds)", "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "PLSpringBoardAgent_EventPoint_SBAutoLock",
        ("timestamp", "AutoLockType"),
        lambda ts, offset, row, rel: (ts, row[1], offset, rel),
    )
    return data_headers, results, source


@artifact_processor
def powerlogTorch(context):
    data_headers = (
        ("Timestamp", "datetime"), "Bundle ID", "Level (as stored)",
        "Time Offset (seconds)", "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "PLCameraAgent_EventForward_Torch",
        ("timestamp", "BundleId", "Level"),
        lambda ts, offset, row, rel: (ts, row[1], row[2], offset, rel),
    )
    return data_headers, results, source


@artifact_processor
def powerlogDisplayState(context):
    data_headers = (
        ("Timestamp", "datetime"), "Brightness", "SliderValue (as stored)",
        "lux (as stored)", "mNits (as stored)", "Time Offset (seconds)",
        "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "PLDisplayAgent_EventForward_Display",
        ("timestamp", "Brightness", "SliderValue", "lux", "mNits"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], row[4], offset, rel),
    )
    return data_headers, results, source


@artifact_processor
def powerlogAudioRouting(context):
    data_headers = (
        ("Timestamp", "datetime"), "Active", "Active Route", "Output Category",
        "Headphones Connected", "BT Endpoint Type", "Active PID",
        "Time Offset (seconds)", "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "PLAudioAgent_EventForward_Routing",
        ("timestamp", "Active", "ActiveRoute", "OutputCategory",
         "HeadphonesConnected", "BTEndpointType", "ActivePID"),
        lambda ts, offset, row, rel: (
            ts, _yes_no(row[1]), row[2], row[3], _yes_no(row[4]), row[5],
            row[6], offset, rel),
        optional=("BTEndpointType", "ActivePID"),
    )
    return data_headers, results, source


@artifact_processor
def powerlogAdapter(context):
    data_headers = (
        ("Timestamp", "datetime"), "SystemInputVoltage (as stored)",
        "SystemInputCurrent (as stored)", "SystemPowerIn (as stored)",
        "SystemLoad (as stored)", "AdapterEfficiencyLoss (as stored)",
        "Time Offset (seconds)", "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "PLBatteryAgent_EventBackward_Adapter",
        ("timestamp", "SystemInputVoltage", "SystemInputCurrent",
         "SystemPowerIn", "SystemLoad", "AdapterEfficiencyLoss"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], row[4], row[5], offset, rel),
        optional=("SystemInputVoltage", "SystemInputCurrent"),
    )
    return data_headers, results, source


@artifact_processor
def powerlogCameraState(context):
    data_headers = (
        ("Timestamp", "datetime"), "Bundle ID", "CameraType (as stored)",
        "State (as stored)", "Time Offset (seconds)", "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "PLCameraAgent_EventForward_Camera",
        ("timestamp", "BundleId", "CameraType", "State"),
        lambda ts, offset, row, rel: (ts, row[1], row[2], row[3], offset, rel),
    )
    return data_headers, results, source


@artifact_processor
def powerlogNeuralEngineModelLoad(context):
    data_headers = (
        ("Timestamp", "datetime"), "Identity", "Model URL",
        "Model Size (as stored)", "Loading Time (as stored)",
        "Cache Hit (as stored)", "Precompiled (as stored)",
        "Time Offset (seconds)", "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "ANE_modelLoad_1_2",
        ("timestamp", "csIdentity", "modelURL", "modelSize",
         "modelLoadingTime", "cacheHit", "isPrecompiled"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], row[4], row[5], row[6], offset, rel),
    )
    return data_headers, results, source


@artifact_processor
def powerlogNeuralEngineModelUnload(context):
    data_headers = (
        ("Timestamp", "datetime"), "Identity", "Model URL",
        "Time Offset (seconds)", "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "ANE_modelUnload_1_2",
        ("timestamp", "csIdentity", "modelURL"),
        lambda ts, offset, row, rel: (ts, row[1], row[2], offset, rel),
    )
    return data_headers, results, source
@artifact_processor
def powerlogGenerativeSummarization(context):
    data_headers = (
        ("Start Time", "datetime"), ("End Time", "datetime"), "Bundle ID",
        "kind (as stored)", "exitReason (as stored)", "isUrgent (as stored)",
        "Request Identifier", "Time Offset (seconds)", "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "GenerativeFunctionMetrics_Summarization_1_2",
        ("timestamp", "timestampEnd", "bundleID", "kind", "exitReason",
         "isUrgent", "requestIdentifier"),
        lambda ts, offset, row, rel: (
            ts, _end_utc(ts, row[0], row[1]), row[2], row[3], row[4], row[5],
            row[6], offset, rel),
    )
    return data_headers, results, source


@artifact_processor
def powerlogGenerativeTextRequests(context):
    data_headers = (
        ("Start Time", "datetime"), ("End Time", "datetime"),
        "requestType (as stored)", "errorType (as stored)",
        "Input Tokens (as stored)", "Output Tokens (as stored)",
        "qos (as stored)", "Request Identifier", "Time Offset (seconds)",
        "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "GenerativeFunctionMetrics_tgiExecuteRequest_1_2",
        ("timestamp", "timestampEnd", "requestType", "errorType",
         "inputTokensCount", "outputTokensCount", "qos", "requestIdentifier"),
        lambda ts, offset, row, rel: (
            ts, _end_utc(ts, row[0], row[1]), row[2], row[3], row[4], row[5],
            row[6], row[7], offset, rel),
    )
    return data_headers, results, source


@artifact_processor
def powerlogGenerativeInferenceRequests(context):
    data_headers = (
        ("Start Time", "datetime"), ("End Time", "datetime"), "Use Case",
        "Created By", "On Behalf Of", "Inference Provider",
        "error (as stored)", "requestType (as stored)", "Session Identifier",
        "Time Offset (seconds)", "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "GenerativeFunctionMetrics_mmExecuteRequest_1_2",
        ("timestamp", "timestampEnd", "useCaseIdentifier",
         "createdByBundleIdentifier", "onBehalfOfBundleIdentifier",
         "inferenceProviderIdentifier", "error", "requestType",
         "sessionIdentifier"),
        lambda ts, offset, row, rel: (
            ts, _end_utc(ts, row[0], row[1]), row[2], row[3], row[4], row[5],
            row[6], row[7], row[8], offset, rel),
    )
    return data_headers, results, source


@artifact_processor
def powerlogGenerativeAssetLoad(context):
    data_headers = (
        ("Start Time", "datetime"), ("End Time", "datetime"),
        "Catalog Resource", "loadType (as stored)", "reason (as stored)",
        "result (as stored)", "Session Identifier", "Time Offset (seconds)",
        "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "GenerativeFunctionMetrics_assetLoad_1_2",
        ("timestamp", "timestampEnd", "catalogResourceIdentifier", "loadType",
         "reason", "result", "sessionIdentifier"),
        lambda ts, offset, row, rel: (
            ts, _end_utc(ts, row[0], row[1]), row[2], row[3], row[4], row[5],
            row[6], offset, rel),
    )
    return data_headers, results, source


@artifact_processor
def powerlogGenerativeOptIn(context):
    data_headers = (
        ("Timestamp", "datetime"), "Enabled", "Time Offset (seconds)",
        "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "GenerativeFunctionMetrics_OptIn_1_2",
        ("timestamp", "Enabled"),
        lambda ts, offset, row, rel: (ts, _yes_no(row[1]), offset, rel),
    )
    return data_headers, results, source

EPSQL_OFFSET = "PPTStorageOperator_TimeOffset"
BGSQL_OFFSET = "BackgroundProcessing_TimeOffset"


@artifact_processor
def powerTelemetryBatteryDataDaily(context):
    data_headers = (
        ("Timestamp", "datetime"), "Cycle Count", "MaxCapacityPercent (as stored)",
        "Nominal Charge Capacity (as stored)", "Charging Voltage (as stored)",
        "Time Offset (seconds)", "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "BatteryDataCollection_BDC_Daily",
        ("timestamp", "CycleCount", "MaxCapacityPercent",
         "NominalChargeCapacity", "ChargingVoltage"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], row[4], offset, rel),
        optional=("MaxCapacityPercent",),
        extension=".EPSQL", offset_prefix=EPSQL_OFFSET,
    )
    return data_headers, results, source


@artifact_processor
def powerTelemetrySmartCharging(context):
    data_headers = (
        ("Timestamp", "datetime"), "ChargeLimit (as stored)",
        "ChargingState (as stored)", "CheckPoint (as stored)",
        "DecisionMaker (as stored)", "InflowState (as stored)",
        "ModeOfOperation (as stored)", "Time Offset (seconds)", "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "BatteryDataCollection_BDC_SmartCharging",
        ("timestamp", "ChargeLimit", "ChargingState", "CheckPoint",
         "DecisionMaker", "InflowState", "ModeOfOperation"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], row[4], row[5], row[6], offset, rel),
        optional=("DecisionMaker",),
        extension=".EPSQL", offset_prefix=EPSQL_OFFSET,
    )
    return data_headers, results, source


@artifact_processor
def powerTelemetryBatteryHardware(context):
    data_headers = (
        ("Timestamp", "datetime"), "Design Capacity (as stored)",
        "ChemID (as stored)", "AlgoChemID (as stored)", "EEEE (as stored)",
        "YWW (as stored)", "Gas Gauge Firmware (as stored)",
        "Time Offset (seconds)", "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "BatteryDataCollection_BDC_Once",
        ("timestamp", "DesignCapacity", "ChemID", "AlgoChemID", "EEEE", "YWW",
         "GasGaugeFirmwareVersion"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], row[4], row[5], row[6], offset, rel),
        optional=("GasGaugeFirmwareVersion",),
        extension=".EPSQL", offset_prefix=EPSQL_OFFSET,
    )
    return data_headers, results, source


@artifact_processor
def powerTelemetryBatteryTrustedDaily(context):
    data_headers = (
        ("Timestamp", "datetime"), ("Trusted Date Of First Use", "datetime"), "Trusted Cycle Count",
        "Trusted Maximum Capacity (as stored)",
        "Trusted LifeTime Max WRdc (as stored)",
        "Time Offset (seconds)", "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "BatteryTrustedData_Daily",
        ("timestamp", "TrustedCycleCount", "TrustedMaximumCapacity",
         "TrustedLifeTimeMaxWRdc", "TrustedDateOfFirstUse"),
        lambda ts, offset, row, rel: (
            ts, convert_unix_ts_to_utc(row[4]), row[1], row[2], row[3],
            offset, rel),
        extension=".EPSQL", offset_prefix=EPSQL_OFFSET,
    )
    return data_headers, results, source


@artifact_processor
def powerTelemetryBackgroundTaskInstances(context):
    data_headers = (
        ("Timestamp", "datetime"), ("Start Date", "datetime"), ("End Date", "datetime"),
        "Process Name", "PID",
        "Started On Battery", "Task ID", "Time Offset (seconds)",
        "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "BackgroundProcessing_TaskInstanceData",
        ("timestamp", "ProcessName", "PID", "StartDate", "EndDate",
         "StartedOnBattery", "TaskID"),
        lambda ts, offset, row, rel: (
            ts, convert_unix_ts_to_utc(row[3]), convert_unix_ts_to_utc(row[4]),
            row[1], row[2], _yes_no(row[5]), row[6], offset,
            rel),
        extension=".BGSQL", offset_prefix=BGSQL_OFFSET,
    )
    return data_headers, results, source


@artifact_processor
def powerTelemetryBackgroundTaskMetadata(context):
    data_headers = (
        ("Timestamp", "datetime"), "Bundle ID", "Name", "Service Name",
        "Group Name", "Launch Reason", "Task ID", "Time Offset (seconds)",
        "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "BackgroundProcessing_TaskMetadata",
        ("timestamp", "BundleID", "Name", "ServiceName", "GroupName",
         "LaunchReason", "TaskID"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], row[4], row[5], row[6], offset, rel),
        extension=".BGSQL", offset_prefix=BGSQL_OFFSET,
    )
    return data_headers, results, source


@artifact_processor
def powerlogInCallService(context):
    data_headers = (
        ("Timestamp", "datetime"), "Bundle ID", "Call Sub Type (as stored)",
        "Provider Identifier", "Status (as stored)", "Video (as stored)",
        "Time Offset (seconds)", "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "PLXPCAgent_EventForward_InCallService",
        ("timestamp", "bundleID", "kCallSubType", "providerIdentifier", "status", "video"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], row[4], row[5], offset, rel),
    )
    return data_headers, results, source


@artifact_processor
def powerlogLightningConnector(context):
    data_headers = (
        ("Timestamp", "datetime"), "Accessory Power Mode (as stored)",
        "Time Offset (seconds)", "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "PLBatteryAgent_EventForward_LightningConnectorStatus",
        ("timestamp", "IOAccessoryPowerMode"),
        lambda ts, offset, row, rel: (ts, row[1], offset, rel),
    )
    return data_headers, results, source


@artifact_processor
def powerlogNetworkUsage(context):
    data_headers = (
        ("Timestamp", "datetime"), "Interface", "Down Bytes (as stored)",
        "Up Bytes (as stored)", "Time Offset (seconds)", "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "PLNetworkAgent_EventBackward_CumulativeNetworkUsage",
        ("timestamp", "Interface", "DownBytes", "UpBytes"),
        lambda ts, offset, row, rel: (ts, row[1], row[2], row[3], offset, rel),
    )
    return data_headers, results, source


@artifact_processor
def powerlogTimeZone(context):
    data_headers = (
        ("Timestamp", "datetime"), "Time Zone Name", "Seconds From GMT (as stored)",
        "Is In DST (as stored)", "Country Code", "Locale ID", "Trigger",
        "Time Offset (seconds)", "Source File",
    )
    results, source = _parse_powerlog_table(
        context, data_headers, "PLLocaleAgent_EventForward_TimeZone",
        ("timestamp", "TimeZoneName", "SecondsFromGMT", "TimeZoneIsInDST",
         "CountryCode", "LocaleId", "Trigger"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], row[4], row[5], row[6], offset, rel),
    )
    return data_headers, results, source
