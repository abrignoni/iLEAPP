__artifacts_v2__ = {
    "knowledgeC_BatteryPercentage": {
        "name": "knowledgeC - Battery Percentage",
        "description": "Battery Percentages extracted from knowledgeC database",
        "author": "@JohannPLW",
        "creation_date": "2023-11-05",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "The field meanings, value labels and time handling below were derived independently, using "
                 "the store's schema, measured data and Apple's code. The artifact's choice of stream and "
                 "columns predates that work. Reads the Event rows of the /device/batteryPercentage stream. "
                 "Apple's monitor code sets Start Time when it builds the event for that state and End Time "
                 "when it records the next one. End Time equalled the next row's Start Time on 10,638 of "
                 "10,653 row pairs. Apple's code was read on macOS 27.2.1 (26B131). The iOS code of the tested "
                 "images was not read, so for them it is a lead and the row data is the measurement. End Time "
                 "is blank for the distant-future value Apple's monitors give an event still open; no tested "
                 "row held it. Created is ZCREATIONDATE: the event's own creation date if it has one, "
                 "otherwise when it was copied to the store. Battery Percent is ZVALUEDOUBLE as stored; every "
                 "tested value was a whole number from 1 to 100 and equalled ZVALUEINTEGER. Fully Charged "
                 "shows Yes for a stored 1 and is blank when nothing is stored, and a blank does not mean No. "
                 "It held 1 on 129 of the 10,658 tested rows and nothing on the rest, and the ctf2020_ios12 "
                 "store has no such column. Event Zone UTC Offset At Write is ZSECONDSFROMGMT, the event "
                 "zone's UTC offset when the row was written, which can differ from its offset at the event "
                 "across a daylight saving change. Event Zone UTC Offset At Write held one value on every row "
                 "of 3 of the 5 images with rows and more than one on the other 2. Source Device ID is "
                 "ZSOURCE.ZDEVICEID, which Apple's sync code uses to identify a peer device, and is blank when "
                 "none is recorded. It was blank on all 10,658 tested rows. In tested data this knowledgeC "
                 "stream carries rows on the iOS 12.4-15.3.1 images and no rows on any iOS 16.1.1-26.5.2 image "
                 "checked (the registered corpora; a comparison by Mattia Epifani in 2026-08 across 21 "
                 "extractions of iOS 16.1.1 to 26.5.2 reported the same, and no publication of it is cited "
                 "here). An empty result on an image of those versions matches what the tested images showed; "
                 "it is not by itself evidence about the device. See the PowerLog - Battery Level and Biome - "
                 "Battery Percentage artifacts for those images.",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "battery",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1408 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 2796 rows",
            "hickman_ios14": "iOS 14.3 | 3487 rows",
            "jess_ios15": "iOS 15.0.2 | 622 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 2345 rows",
            "belkactf6_tar": "iOS 16.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 0 rows",
        }
    },
    "knowledgeC_DevicePluginStatus": {
        "name": "knowledgeC - Device Plugin Status",
        "description": "Is Device Plugged In events extracted from knowledgeC database",
        "author": "@JohannPLW",
        "creation_date": "2023-11-05",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "The field meanings, value labels and time handling below were derived independently, using "
                 "the store's schema, measured data and Apple's code. The artifact's choice of stream and "
                 "columns predates that work. Reads the Event rows of the /device/isPluggedIn stream. Plugged "
                 "In shows Yes for a stored 1 and No for 0, the two boolean category values Apple's monitor "
                 "writes; any other value is shown with the words not established. Apple's monitor code sets "
                 "Start Time when it builds the event for that state and End Time when it records the next "
                 "one. End Time equalled the next row's Start Time on 404 of 421 row pairs. Apple's code was "
                 "read on macOS 27.2.1 (26B131). The iOS code of the tested images was not read, so for them "
                 "it is a lead and the row data is the measurement. End Time is blank for the distant-future "
                 "value Apple's monitors give an event still open; no tested row held it. Created is "
                 "ZCREATIONDATE: the event's own creation date if it has one, otherwise when it was copied to "
                 "the store. Adapter Family Code is the power adapter's FamilyCode, shown as unsigned 32-bit "
                 "hexadecimal. It held a value on 195 of the 426 tested rows. Apple's IOKit header IOPM.h "
                 "(macOS SDK) names family codes as kIOPSFamilyCode values. This artifact shows the code and "
                 "does not label it. Adapter Wireless shows Yes for a stored 1 and No for 0 and is blank when "
                 "nothing is stored; it held a value on 155 of the 426 tested rows. All 155 held 0. Stores "
                 "without these columns show them blank. Adapter Family Code was blank on every row of 1 of "
                 "the 5 images with rows and Adapter Wireless on 2, because those stores lack the columns. "
                 "Event Zone UTC Offset At Write is ZSECONDSFROMGMT, the event zone's UTC offset when the row "
                 "was written, which can differ from its offset at the event across a daylight saving change. "
                 "Event Zone UTC Offset At Write held one value on every row of 3 of the 5 images with rows "
                 "and more than one on the other 2. Source Device ID is ZSOURCE.ZDEVICEID, which Apple's sync "
                 "code uses to identify a peer device, and is blank when none is recorded. It was blank on all "
                 "426 tested rows. In tested data this knowledgeC stream carries rows on the iOS 12.4-15.3.1 "
                 "images and no rows on any iOS 16.1.1-26.5.2 image checked (the registered corpora; a "
                 "comparison by Mattia Epifani in 2026-08 across 21 extractions of iOS 16.1.1 to 26.5.2 "
                 "reported the same, and no publication of it is cited here). An empty result on an image of "
                 "those versions matches what the tested images showed; it is not by itself evidence about the "
                 "device. See the Power Log and Biome cable-plug artifacts for those images.",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "battery-charging",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 53 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 81 rows",
            "hickman_ios14": "iOS 14.3 | 147 rows",
            "jess_ios15": "iOS 15.0.2 | 50 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 95 rows",
            "belkactf6_tar": "iOS 16.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 0 rows",
        }
    },
    "knowledgeC_MediaPlaying": {
        "name": "knowledgeC - Media Playing",
        "description": "Media playing events extracted from knowledgeC database",
        "author": "@JohannPLW",
        "creation_date": "2023-10-31",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "The field meanings, value labels and time handling below were derived independently, using "
                 "the store's schema, measured data and Apple's code. The artifact's choice of stream and "
                 "columns predates that work. The Output Device IDs decoder also predates it. Reads the Event "
                 "rows of the /media/nowPlaying stream. Playback State labels the stored value with the names "
                 "Apple's MediaRemote gives it: 0 Unknown, 1 Playing, 2 Paused, 3 Stopped, 4 Interrupted, 5 "
                 "Seeking. Values 0 to 4 occur in tested data and 5 does not. Any other value is shown with "
                 "the words not established. Apple's monitor code sets Start Time when it builds the event for "
                 "that state and End Time when it records the next one. End Time equalled the next row's Start "
                 "Time on 2,373 of 2,400 row pairs. Apple's code was read on macOS 27.2.1 (26B131). The iOS "
                 "code of the tested images was not read, so for them it is a lead and the row data is the "
                 "measurement. End Time is blank for the distant-future value Apple's monitors give an event "
                 "still open; no tested row held it. Created is ZCREATIONDATE: the event's own creation date "
                 "if it has one, otherwise when it was copied to the store. Duration Seconds is End Time minus "
                 "Start Time. Media Duration (as stored) is the stored duration value, and its unit is not "
                 "established. Bundle ID is ZVALUESTRING as stored. It held an empty string on 634 of the "
                 "2,421 tested rows; all 634 hold Playback State Unknown and no title, and they are reported "
                 "as stored. Media Type is reported as stored and what its values mean is not established. "
                 "Media Type was blank on every row of 11 of the 21 images with rows. AirPlay Video shows Yes "
                 "for a stored 1 and No for 0. AirPlay Video held 0 on all 2,421 rows. Output Device IDs lists "
                 "each distinct value held in the arrays of the stored archive, in the order they are reached "
                 "from the archive's top object, separated by commas. It is blank when no archive is stored "
                 "(77 tested rows) or it cannot be read (0 tested rows). A second decode that reads the "
                 "archive's object list directly gave the same values on all 2,344 rows that store an archive. "
                 "What the dictionary keys mean and whether a value is a device name or an address is not "
                 "established. Artist, Album, Title and Genre can each be blank on every row of an image: "
                 "Artist and Album on 13 of the 21 images with rows, Title on 12 and Genre on 15. Event Zone "
                 "UTC Offset At Write is ZSECONDSFROMGMT, the event zone's UTC offset when the row was "
                 "written, which can differ from its offset at the event across a daylight saving change. "
                 "Event Zone UTC Offset At Write held one value on every row of 15 of the 21 images with rows "
                 "and more than one on the other 6. Source Device ID is ZSOURCE.ZDEVICEID, which Apple's sync "
                 "code uses to identify a peer device, and is blank when none is recorded. It was blank on all "
                 "2,421 tested rows. Earlier versions of this artifact credited a post by Ian Whiffin "
                 "(doubleblak.com). No link to it is given here. The iTunes store and subscription identifier "
                 "columns hold values on some rows and are not reported.",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "music",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 27 rows",
            "dexter_ios18": "iOS 18.3.2 | 454 rows",
            "felix_ios17": "iOS 17.6.1 | 15 rows",
            "fsfull002_ios17": "iOS 17.1 | 1 rows",
            "hc_ios18_7": "iOS 18.7.8 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 74 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 14 rows",
            "abe_ios16": "iOS 16.5 | 207 rows",
            "felix23_ios16": "iOS 16.5 | 7 rows",
            "hickman_ios13": "iOS 13.3.1 | 254 rows",
            "hickman_ios14": "iOS 14.3 | 435 rows",
            "jess_ios15": "iOS 15.0.2 | 58 rows",
            "magnet_ios16": "iOS 16.1.1 | 10 rows",
            "hc_ios26": "iOS 26.5.2 | 31 rows",
            "hickman_ios15": "iOS 15.3.1 | 403 rows",
            "belkactf6_tar": "iOS 16.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 8 rows",
            "hc_ios17_2": "iOS 17.2.1 | 7 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 77 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 4 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 86 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 247 rows",
        }
    },
    "knowledgeC_DoNotDisturb": {
        "name": "knowledgeC - Do Not Disturb",
        "description": "Do Not Disturb Status from knowledgeC Database",
        "author": "Geraldine Blay",
        "creation_date": "2024-02-24",
        "last_update_date": "2024-02-24",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "Based on research by Geraldine Blay and Dan Ogden; no title or link for that "
                 "research is given here. The Do Not Disturb? column shows Yes for a stored value "
                 "of 1 and No for 0; any other value is shown as Not Specified. In tested data "
                 "rows are recorded only on the iOS 13.3.1 and 14.3 images; the iOS 12.4 and "
                 "15.0.2 images and every iOS 16.1.1-26.5.2 image checked (the registered "
                 "corpora; a comparison by Mattia Epifani in 2026-08 across 21 extractions of iOS "
                 "16.1.1 to 26.5.2 reported the same, and no publication of it is cited here) "
                 "yield no rows. An empty result on an image of those versions matches what the "
                 "tested images showed; it is not by itself evidence about the device.",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "moon",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 44 rows",
            "hickman_ios14": "iOS 14.3 | 57 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "knowledgeC_AppUsage": {
        "name": "knowledgeC - App Usage",
        "description": "parses /app/usage events from knowledgeC Database",
        "author": "mxkrt@lsjam.nl",
        "creation_date": "2025-09-13",
        "last_update_date": "2025-09-13",
        "requirements": "none",
        "category": "App Usage",
        "notes": "",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 691 rows",
            "dexter_ios18": "iOS 18.3.2 | 363 rows",
            "felix_ios17": "iOS 17.6.1 | 152 rows",
            "fsfull002_ios17": "iOS 17.1 | 65 rows",
            "hc_ios18_7": "iOS 18.7.8 | 184 rows",
            "iphone11_ios17": "iOS 17.3 | 435 rows",
            "iphone14plus_ios18": "iOS 18.0 | 143 rows",
            "otto_ios17": "iOS 17.5.1 | 676 rows",
            "abe_ios16": "iOS 16.5 | 1467 rows",
            "felix23_ios16": "iOS 16.5 | 116 rows",
            "hickman_ios13": "iOS 13.3.1 | 623 rows",
            "hickman_ios14": "iOS 14.3 | 611 rows",
            "jess_ios15": "iOS 15.0.2 | 162 rows",
            "magnet_ios16": "iOS 16.1.1 | 202 rows",
        }
    },
    "knowledgeC_AppUsage_EndTime": {
        "name": "knowledgeC - App Usage End",
        "description": "include End Time in timeline for /app/usage events from knowledgeC Database",
        "author": "mxkrt@lsjam.nl",
        "creation_date": "2025-09-13",
        "last_update_date": "2025-09-13",
        "requirements": "none",
        "category": "App Usage",
        "notes": "",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "timeline",
        "artifact_icon": "activity",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 691 rows",
            "dexter_ios18": "iOS 18.3.2 | 363 rows",
            "felix_ios17": "iOS 17.6.1 | 152 rows",
            "fsfull002_ios17": "iOS 17.1 | 65 rows",
            "hc_ios18_7": "iOS 18.7.8 | 184 rows",
            "iphone11_ios17": "iOS 17.3 | 435 rows",
            "iphone14plus_ios18": "iOS 18.0 | 143 rows",
            "otto_ios17": "iOS 17.5.1 | 676 rows",
            "abe_ios16": "iOS 16.5 | 1467 rows",
            "felix23_ios16": "iOS 16.5 | 116 rows",
            "hickman_ios13": "iOS 13.3.1 | 623 rows",
            "hickman_ios14": "iOS 14.3 | 611 rows",
            "jess_ios15": "iOS 15.0.2 | 162 rows",
            "magnet_ios16": "iOS 16.1.1 | 202 rows",
        }
    },
    "knowledgeC_isLocked": {
        "name": "knowledgeC - Device Lock Status",
        "description": "Rows of the /device/isLocked stream of knowledgeC.db, which Apple's stream definition "
                       "describes as whether the screen is locked.",
        "author": "mxkrt@lsjam.nl",
        "creation_date": "2025-09-13",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "Device Usage",
        "notes": "The field meanings, value labels and time handling below were derived independently, using "
                 "the store's schema, measured data and Apple's code. The artifact's choice of stream and "
                 "columns predates that work. Screen Locked shows Yes for a stored 1 and No for 0, the two "
                 "boolean category values Apple's monitor writes; any other value is shown with the words not "
                 "established. Apple's monitor code sets Start Time when it builds the event for that state "
                 "and End Time when it records the next one. End Time equalled the next row's Start Time on "
                 "3,109 of 3,253 row pairs. Apple's code was read on macOS 27.2.1 (26B131). The iOS code of "
                 "the tested images was not read, so for them it is a lead and the row data is the "
                 "measurement. End Time is blank for the distant-future value Apple's monitors give an event "
                 "still open; no tested row held it. Created is ZCREATIONDATE: the event's own creation date "
                 "if it has one, otherwise when it was copied to the store. Stored On This Device is "
                 "ZLOCALCREATIONDATE, the time of the copy to this store. Source Device ID is "
                 "ZSOURCE.ZDEVICEID, which Apple's sync code uses to identify a peer device, and is blank when "
                 "none is recorded. In tested data every row that holds one has a Stored On This Device time "
                 "later than Created. Such a row should not be assumed to describe this device. 78 of the "
                 "3,275 tested rows hold one, and those are the rows where Created and Stored On This Device "
                 "differ. In tested data, on an image whose rows hold no Source Device ID, Created and Stored "
                 "On This Device are identical on every row. Event Zone UTC Offset At Write is "
                 "ZSECONDSFROMGMT, the event zone's UTC offset when the row was written, which can differ from "
                 "its offset at the event across a daylight saving change. Event Zone UTC Offset At Write held "
                 "one value on every row of 11 of the 22 images with rows and more than one on the other 11. "
                 "In tested data the iOS 12.4 image holds no rows in this stream and every image from iOS "
                 "13.3.1 to 26.5.2 holds some.",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "device-mobile",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 287 rows",
            "felix_ios17": "iOS 17.6.1 | 136 rows",
            "fsfull002_ios17": "iOS 17.1 | 49 rows",
            "hc_ios18_7": "iOS 18.7.8 | 164 rows",
            "iphone11_ios17": "iOS 17.3 | 91 rows",
            "iphone14plus_ios18": "iOS 18.0 | 33 rows",
            "otto_ios17": "iOS 17.5.1 | 60 rows",
            "abe_ios16": "iOS 16.5 | 710 rows",
            "felix23_ios16": "iOS 16.5 | 97 rows",
            "hickman_ios13": "iOS 13.3.1 | 277 rows",
            "hickman_ios14": "iOS 14.3 | 137 rows",
            "jess_ios15": "iOS 15.0.2 | 64 rows",
            "magnet_ios16": "iOS 16.1.1 | 95 rows",
            "hc_ios26": "iOS 26.5.2 | 72 rows",
            "hickman_ios15": "iOS 15.3.1 | 201 rows",
            "belkactf6_tar": "iOS 16.3 | 5 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 67 rows",
            "hc_ios17_2": "iOS 17.2.1 | 56 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 171 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 154 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 56 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 293 rows",
        }
    },
    "knowledgeC_isBacklit": {
        "name": "knowledgeC - Device Screen Status",
        "description": "Rows of the /display/isBacklit stream of knowledgeC.db, which Apple's stream definition "
                       "describes as the backlight level.",
        "author": "mxkrt@lsjam.nl",
        "creation_date": "2025-09-13",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "Device Usage",
        "notes": "The field meanings, value labels and time handling below were derived independently, using "
                 "the store's schema, measured data and Apple's code. The artifact's choice of stream and "
                 "columns predates that work. Backlit shows Yes for a stored 1 and No for 0, the two boolean "
                 "category values Apple's monitor writes; any other value is shown with the words not "
                 "established. Apple's monitor code sets Start Time when it builds the event for that state "
                 "and End Time when it records the next one. End Time equalled the next row's Start Time on "
                 "22,953 of 23,363 row pairs. Apple's code was read on macOS 27.2.1 (26B131). The iOS code of "
                 "the tested images was not read, so for them it is a lead and the row data is the "
                 "measurement. End Time is blank for the distant-future value Apple's monitors give an event "
                 "still open; no tested row held it. Created is ZCREATIONDATE: the event's own creation date "
                 "if it has one, otherwise when it was copied to the store. Stored On This Device is "
                 "ZLOCALCREATIONDATE, the time of the copy to this store. Source Device ID is "
                 "ZSOURCE.ZDEVICEID, which Apple's sync code uses to identify a peer device, and is blank when "
                 "none is recorded. In tested data every row that holds one has a Stored On This Device time "
                 "later than Created. Such a row should not be assumed to describe this device. 289 of the "
                 "23,385 tested rows hold one, and those are the rows where Created and Stored On This Device "
                 "differ. In tested data, on an image whose rows hold no Source Device ID, Created and Stored "
                 "On This Device are identical on every row. Event Zone UTC Offset At Write is "
                 "ZSECONDSFROMGMT, the event zone's UTC offset when the row was written, which can differ from "
                 "its offset at the event across a daylight saving change. Event Zone UTC Offset At Write held "
                 "one value on every row of 11 of the 22 images with rows and more than one on the other 11.",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "device-mobile",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1331 rows",
            "dexter_ios18": "iOS 18.3.2 | 1767 rows",
            "felix_ios17": "iOS 17.6.1 | 383 rows",
            "fsfull002_ios17": "iOS 17.1 | 182 rows",
            "hc_ios18_7": "iOS 18.7.8 | 515 rows",
            "iphone11_ios17": "iOS 17.3 | 784 rows",
            "iphone14plus_ios18": "iOS 18.0 | 227 rows",
            "otto_ios17": "iOS 17.5.1 | 2237 rows",
            "abe_ios16": "iOS 16.5 | 5140 rows",
            "felix23_ios16": "iOS 16.5 | 274 rows",
            "hickman_ios13": "iOS 13.3.1 | 1494 rows",
            "hickman_ios14": "iOS 14.3 | 1189 rows",
            "jess_ios15": "iOS 15.0.2 | 398 rows",
            "magnet_ios16": "iOS 16.1.1 | 623 rows",
            "hc_ios26": "iOS 26.5.2 | 248 rows",
            "hickman_ios15": "iOS 15.3.1 | 1340 rows",
            "belkactf6_tar": "iOS 16.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 209 rows",
            "hc_ios17_2": "iOS 17.2.1 | 228 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 1052 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 1047 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 701 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 2016 rows",
        }
    },
    "knowledgeC_LocationActivity": {
        "name": "knowledgeC - Location Activity",
        "description": "Places recorded in the knowledgeC /app/locationActivity stream, with the other "
                       "coordinate pairs found in the same record's payload",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-30",
        "last_update_date": "2026-09-30",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "Reads each ZOBJECT row in the /app/locationActivity stream of knowledgeC.db with the "
                 "ZSTRUCTUREDMETADATA row it points to. Location Name, Display Name, Address, Place Latitude "
                 "and Place Longitude are that row's Z_DKLOCATIONAPPLICATIONACTIVITYMETADATAKEY__ LOCATIONNAME, "
                 "DISPLAYNAME, FULLYFORMATTEDADDRESS, LATITUDE and LONGITUDE, as stored. Activity UUID is "
                 "Z_DKAPPLICATIONACTIVITYMETADATAKEY__USERACTIVITYUUID and Bundle ID is ZOBJECT.ZVALUESTRING. "
                 "Start Time is ZSTARTDATE, which equalled the row's end date and fell on a whole minute on all "
                 "48 tested rows; Creation Time is ZCREATIONDATE. "
                 "The user activity's required string (Z_DKAPPLICATIONACTIVITYMETADATAKEY__"
                 "USERACTIVITYREQUIREDSTRING) can carry a compressed payload: base64 between the two $ signs after "
                 "'bs'=, four bytes, then bzip2 holding a protobuf. Reference: Sarah Edwards, 'Providing Context to "
                 "iOS App Usage with knowledgeC.db and APOLLO', "
                 "https://www.mac4n6.com/blog/2020/1/13/apollo-into-the-details-with-application-activities. "
                 "Compressed Payload says whether that payload was present and whether it decoded. Other Coordinate "
                 "Pairs in Payload lists each nested protobuf message whose fields 1 and 2 are doubles within "
                 "latitude and longitude range (0, 0 excluded), with its distance from Place Latitude and Place "
                 "Longitude, the first field path it was found at and how many more held it, leaving out pairs "
                 "within 1 m of the place coordinates. Farthest "
                 "Other Pair (m) is the largest of those distances. What each pair represents is not established. "
                 "They are listed so that a coordinate another tool reads from this record can be checked against "
                 "the place the record names. Neither the place coordinates nor any other pair is established as "
                 "the device's location. "
                 "Tested on 22 registered images from iOS 12.4 to 26.5.2. Of those, only hickman_ios13 (8 rows) and "
                 "hickman_ios15 (40 rows) hold rows in this stream, so an empty result means only that the database "
                 "held none. Bundle ID held com.apple.Maps on all 48 rows. Rows repeat: one Activity UUID "
                 "covered all 8 hickman_ios13 rows, on which Location Name, Address, Place Latitude and Place "
                 "Longitude each held one value, and on hickman_ios15 one Activity UUID covered 33 rows naming two "
                 "places (7 rows naming one place, then 26 whose Location Name is Dropped Pin) while another covered "
                 "the other 7. The payload was present on 28 rows and "
                 "decoded on all 28. On the 26 Dropped Pin rows the only pair more than 1 m from the pin was at "
                 "field 1.5: 29 m away on 17 rows and 3,659 m away on 4; on the other 5 no pair was more than 1 m "
                 "away. On hickman_ios13 the 2 rows with a payload "
                 "listed pairs up to 1,287 m and 1,240 m from the place. "
                 "The required string also carries a maps.apple.com link on 21 of the 48 rows; its ll value was "
                 "within 0.00001 degrees of Place Latitude and Place Longitude on all 21, so it is not reported "
                 "separately. The title in the required string equalled Display Name on all 48 rows. The city, "
                 "state, postal code, street, street number and country columns each appeared within Address on all "
                 "48 rows and are not reported separately; the phone numbers column is not reported. "
                 "Not parsed here: com.apple.Maps rows in the /app/intents stream (INIntent verbs such as "
                 "Show and PlaceCardTap, whose parameters name the place; on hickman_ios13 a pin there is titled "
                 "Marked Location) and the 96 com.apple.Maps rows in /app/activity on hickman_ios13, none of which "
                 "has these place columns filled.",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 8 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 40 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        }
    },
    "knowledgeC_appInFocus": {
        "name": "knowledgeC - Application In Focus",
        "description": "Parses /app/inFocus events from the knowledgeC database: the application bundle id, the "
                       "start and end of the event, its duration in seconds, the launch reason and extension fields "
                       "from the structured metadata, the event zone's UTC offset, the source device and the event "
                       "UUID.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-13",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "The field meanings, value labels and time handling below were derived independently, using "
                 "the store's schema, measured data and Apple's code. The artifact's choice of stream and "
                 "columns predates that work. Reads the Event rows of the /app/inFocus stream, which Apple's "
                 "stream definition describes as an app's transition to focal state. Apple's monitor code sets "
                 "Start Time when it builds the event for that state and End Time when it records the next "
                 "one. Measured, End Time equalled the next row's Start Time on 2,637 of 9,145 row pairs, with "
                 "5,477 gaps and 1,031 overlaps; why is not established. Apple's code was read on macOS 27.2.1 "
                 "(26B131). The iOS code of the tested images was not read, so for them it is a lead and the "
                 "row data is the measurement. End Time is blank for the distant-future value Apple's monitors "
                 "give an event still open; no tested row held it. Created is ZCREATIONDATE: the event's own "
                 "creation date if it has one, otherwise when it was copied to the store. Bundle ID is "
                 "ZVALUESTRING as stored and held an empty string on 4 of the 9,150 tested rows. Duration "
                 "Seconds is End Time minus Start Time. Launch Reason is reported as stored and what its "
                 "values mean is not established. Launch Reason, Extension Containing Bundle ID and Extension "
                 "Host ID are read from ZSTRUCTUREDMETADATA and are blank where no value is stored. Extension "
                 "Containing Bundle ID held no value on any row of 1 of the 5 images with rows. Event Zone UTC "
                 "Offset At Write is ZSECONDSFROMGMT, the event zone's UTC offset when the row was written, "
                 "which can differ from its offset at the event across a daylight saving change. Event Zone "
                 "UTC Offset At Write held one value on every row of 4 of the 5 images with rows and more than "
                 "one on the other. Source Device ID is ZSOURCE.ZDEVICEID, which Apple's sync code uses to "
                 "identify a peer device, and is blank when none is recorded. It was blank on all 9,150 tested "
                 "rows. In tested data this stream carried rows on the iOS 12.4-15.3.1 images and no rows on "
                 "the iOS 16.1.1-26.5.2 images checked; the Biome - In Focus and Biome - In Focus DKEvent "
                 "artifacts read the Biome App.InFocus streams, which carried rows on the later images those "
                 "artifacts were run against. An empty result on an iOS 16 or later image matches what the "
                 "tested images showed and is not by itself evidence about the device.",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "eye",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 2186 rows",
            "hickman_ios13": "iOS 13.3.1 | 3987 rows",
            "hickman_ios14": "iOS 14.3 | 719 rows",
            "jess_ios15": "iOS 15.0.2 | 320 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 1938 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "belkactf6_tar": "iOS 16.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 0 rows",
        },
    }
}

import base64
import binascii
import bz2
import math
import plistlib
import re
import struct
from datetime import datetime, timedelta, timezone
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, \
    convert_ts_human_to_utc, convert_cocoa_core_data_ts_to_utc, logfunc

_COCOA_EPOCH = datetime(2001, 1, 1, tzinfo=timezone.utc)
# [[NSDate distantFuture] timeIntervalSinceReferenceDate], the end a monitor gives an open event.
_DISTANT_FUTURE = 63113904000.0
_NOT_ESTABLISHED = 'not established'
_BOOL_LABELS = {0: 'No', 1: 'Yes'}
# MediaRemote MRMediaRemoteCopyPlaybackStateDescription
_PLAYBACK_STATES = {0: 'Unknown', 1: 'Playing', 2: 'Paused', 3: 'Stopped', 4: 'Interrupted', 5: 'Seeking'}
_NOW_PLAYING_KEY = 'Z_DKNOWPLAYINGMETADATAKEY__'
_APP_KEY = 'Z_DKAPPLICATIONMETADATAKEY__'
_PLUGGED_IN_KEY = 'Z_DKDEVICEISPLUGGEDINMETADATAKEY__'
_BATTERY_KEY = 'Z_DKDEVICEBATTERYPERCENTAGEMETADATAKEY__'


def _knowledgec_db(context):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('knowledgeC.db'):
            return file_found
    return ''


def _stream_rows(db_file, stream, metadata_columns=()):
    """Event rows of one stream, oldest first, as dictionaries of the stored values.

    Rows are ZOBJECT rows whose Z_ENT is the id Z_PRIMARYKEY gives the Event entity. Metadata
    and source columns a store does not have read as None."""
    if not db_file:
        return []
    db = open_sqlite_db_readonly(db_file)
    if db is None:
        return []
    try:
        cursor = db.cursor()
        entity = cursor.execute("SELECT Z_ENT FROM Z_PRIMARYKEY WHERE Z_NAME = 'Event'").fetchone()
        if not entity:
            logfunc(f'knowledgeC: no Event entity in Z_PRIMARYKEY, {stream} not read')
            return []
        metadata_present = {row[1] for row in cursor.execute('PRAGMA table_info(ZSTRUCTUREDMETADATA)')}
        source_present = {row[1] for row in cursor.execute('PRAGMA table_info(ZSOURCE)')}
        selected = [f'm."{name}"' if name in metadata_present else 'NULL' for name in metadata_columns]
        device_id = 's.ZDEVICEID' if 'ZDEVICEID' in source_present else 'NULL'
        query = f"""
        SELECT o.ZSTARTDATE, o.ZENDDATE, o.ZCREATIONDATE, o.ZLOCALCREATIONDATE, o.ZSECONDSFROMGMT,
               o.ZVALUESTRING, o.ZVALUEINTEGER, o.ZVALUEDOUBLE, o.ZUUID, {device_id}
               {''.join(', ' + column for column in selected)}
        FROM ZOBJECT o
        LEFT JOIN ZSOURCE s ON o.ZSOURCE = s.Z_PK
        LEFT JOIN ZSTRUCTUREDMETADATA m ON o.ZSTRUCTUREDMETADATA = m.Z_PK
        WHERE o.ZSTREAMNAME = ? AND o.Z_ENT = ?
        ORDER BY o.ZSTARTDATE, o.Z_PK"""
        names = ('start', 'end', 'created', 'stored', 'offset', 'text', 'integer', 'double', 'uuid',
                 'device') + tuple(metadata_columns)
        return [dict(zip(names, row)) for row in cursor.execute(query, (stream, entity[0]))]
    finally:
        db.close()


def _event_time(value):
    """UTC datetime of a stored Cocoa time, blank when absent or the distant-future open end."""
    if value is None or value >= _DISTANT_FUTURE - 1:
        return ''
    try:
        return _COCOA_EPOCH + timedelta(seconds=float(value))
    except (OverflowError, ValueError, TypeError):
        logfunc('knowledgeC: a stored time could not be converted and is shown blank')
        return ''


def _duration(row):
    start, end = row['start'], row['end']
    if start is None or end is None or end >= _DISTANT_FUTURE - 1:
        return ''
    return round(end - start, 3)


def _utc_offset(seconds):
    if seconds is None:
        return ''
    seconds = int(seconds)
    sign = '+' if seconds >= 0 else '-'
    seconds = abs(seconds)
    return f'{sign}{seconds // 3600:02d}:{(seconds % 3600) // 60:02d}'


def _labelled(value, labels):
    if value is None:
        return ''
    return labels.get(value, f'{value} ({_NOT_ESTABLISHED})')


def _family_code(value):
    return '' if value is None else f'0x{int(value) & 0xFFFFFFFF:08X}'


@artifact_processor
def knowledgeC_BatteryPercentage(context):
    db_file = _knowledgec_db(context)
    fully_charged = f'{_BATTERY_KEY}FULLYCHARGED'
    data_list = [(_event_time(row['start']), _event_time(row['end']), _event_time(row['created']),
                  row['double'], _labelled(row[fully_charged], _BOOL_LABELS), _utc_offset(row['offset']),
                  row['device'])
                 for row in _stream_rows(db_file, '/device/batteryPercentage', (fully_charged,))]
    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), ('Created', 'datetime'), ('Battery Percent', 'number'),
        'Fully Charged', 'Event Zone UTC Offset At Write', 'Source Device ID')
    return data_headers, data_list, db_file

@artifact_processor
def knowledgeC_DevicePluginStatus(context):
    db_file = _knowledgec_db(context)
    family, wireless = f'{_PLUGGED_IN_KEY}ADAPTERTYPE', f'{_PLUGGED_IN_KEY}ADAPTERISWIRELESS'
    data_list = [(_event_time(row['start']), _event_time(row['end']), _event_time(row['created']),
                  _labelled(row['integer'], _BOOL_LABELS), _family_code(row[family]),
                  _labelled(row[wireless], _BOOL_LABELS), _utc_offset(row['offset']), row['device'])
                 for row in _stream_rows(db_file, '/device/isPluggedIn', (family, wireless))]
    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), ('Created', 'datetime'), 'Plugged In',
        'Adapter Family Code', 'Adapter Wireless', 'Event Zone UTC Offset At Write', 'Source Device ID')
    return data_headers, data_list, db_file

@artifact_processor
def knowledgeC_MediaPlaying(context):
    db_file = _knowledgec_db(context)
    columns = tuple(f'{_NOW_PLAYING_KEY}{name}' for name in (
        'PLAYING', 'ARTIST', 'ALBUM', 'TITLE', 'GENRE', 'DURATION', 'MEDIATYPE', 'ISAIRPLAYVIDEO',
        'OUTPUTDEVICEIDS'))
    playing, artist, album, title, genre, length, media_type, airplay, outputs = columns
    data_list = [(_event_time(row['start']), _event_time(row['end']), _event_time(row['created']),
                  _labelled(row[playing], _PLAYBACK_STATES), _duration(row), row['text'], row[artist],
                  row[album], row[title], row[genre], row[length], row[media_type],
                  _labelled(row[airplay], _BOOL_LABELS), _output_device_ids(row[outputs]),
                  _utc_offset(row['offset']), row['device'])
                 for row in _stream_rows(db_file, '/media/nowPlaying', columns)]
    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), ('Created', 'datetime'), 'Playback State',
        ('Duration Seconds', 'number'), 'Bundle ID', 'Artist', 'Album', 'Title', 'Genre',
        'Media Duration (as stored)',
        'Media Type (as stored)', 'AirPlay Video', 'Output Device IDs', 'Event Zone UTC Offset At Write',
        'Source Device ID')
    return data_headers, data_list, db_file

def _output_device_ids(blob):
    """Values held in the arrays of an OUTPUTDEVICEIDS NSKeyedArchiver blob, joined by commas.

    The archive is followed from $top through each object's NS.objects references, so the
    result does not depend on where a value sits in the $objects list. Dictionary keys
    (NS.keys) are not followed. Returns '' when the blob is not a readable archive.
    """
    if not isinstance(blob, bytes):
        return ''
    try:
        archive = plistlib.loads(blob)
    except (plistlib.InvalidFileException, ValueError, TypeError, OverflowError):
        return ''
    if not isinstance(archive, dict):
        return ''
    objects = archive.get('$objects')
    top = archive.get('$top')
    if not isinstance(objects, list) or not isinstance(top, dict):
        return ''

    found = []

    def walk(node, active):
        if isinstance(node, plistlib.UID):
            index = node.data
            if index in active or not 0 <= index < len(objects):
                return
            walk(objects[index], active | {index})
        elif isinstance(node, dict):
            members = node.get('NS.objects')
            if isinstance(members, list):
                for member in members:
                    walk(member, active)
        elif isinstance(node, list):
            for member in node:
                walk(member, active)
        elif node is not None and node != '$null':
            text = str(node)
            if text not in found:
                found.append(text)

    for value in top.values():
        walk(value, frozenset())
    return ', '.join(found)


@artifact_processor
def knowledgeC_DoNotDisturb(context):
    data_list = []
    db_file = ''

    for file_found in context.get_files_found():
        if file_found.endswith('knowledgeC.db'):
            db_file = file_found
            break

    with open_sqlite_db_readonly(db_file) as db:
        cursor = db.cursor()

        cursor.execute('''
        SELECT
        datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') AS 'Start Time',
        datetime(ZOBJECT.ZENDDATE + 978307200, 'unixepoch') AS 'End Time',
        CASE
            ZOBJECT.ZVALUEINTEGER
            WHEN '0' THEN 'No'
            WHEN '1' THEN 'Yes'
            ELSE 'Not Specified'
        END AS 'Is Do Not Disturb On?',
        datetime(ZOBJECT.ZCREATIONDATE + 978307200, 'unixepoch') AS 'Date Added'
        FROM ZOBJECT
        WHERE ZOBJECT.ZSTREAMNAME = '/settings/doNotDisturb'
        ORDER BY ZOBJECT.ZSTARTDATE
        ''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            start_time = convert_ts_human_to_utc(row[0])
            end_time = convert_ts_human_to_utc(row[1])
            added_time = convert_ts_human_to_utc(row[3])
            data_list.append((start_time, end_time, row[2], added_time))

    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), 'Do Not Disturb?', ('Time Added', 'datetime'))
    return data_headers, data_list, db_file


@artifact_processor
def knowledgeC_AppUsage(context):
    ''' parse /app/usage entries from knowledgeC.db '''

    db_file = ''

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('knowledgeC.db'):
            db_file = file_found
            break

    data_list = []

    with open_sqlite_db_readonly(db_file) as db:
        cursor = db.cursor()

        cursor.execute('''
            SELECT datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') AS 'Start Time',
                   datetime(ZOBJECT.ZENDDATE + 978307200, 'unixepoch') AS 'End Time',
                   datetime(ZOBJECT.ZCREATIONDATE + 978307200, 'unixepoch') AS 'Date Added',
                   ZVALUESTRING
            FROM ZOBJECT
            WHERE ZSTREAMNAME = '/app/usage'
            ORDER BY ZOBJECT.ZSTARTDATE, ZOBJECT.Z_PK''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            start_time = convert_ts_human_to_utc(row[0])
            end_time = convert_ts_human_to_utc(row[1])
            added_time = convert_ts_human_to_utc(row[2])
            data_list.append((start_time, end_time, added_time, row[3]))

    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), ('Time Added', 'datetime'), 'Application')

    return data_headers, data_list, db_file


@artifact_processor
def knowledgeC_AppUsage_EndTime(context):
    ''' Parse /app/usage entries from knowledgeC.db with End Time as first column'''

    # NOTE: there is no need to add this to html and lava output, the only
    # purpose of this additional parsing is to add the End Time as separate
    # event in the tl.db

    db_file = ''

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('knowledgeC.db'):
            db_file = file_found
            break

    data_list = []

    with open_sqlite_db_readonly(db_file) as db:
        cursor = db.cursor()

        cursor.execute('''
            SELECT datetime(ZOBJECT.ZENDDATE + 978307200, 'unixepoch') AS 'End Time',
                   datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') AS 'Start Time',
                   datetime(ZOBJECT.ZCREATIONDATE + 978307200, 'unixepoch') AS 'Date Added',
                   ZVALUESTRING
            FROM ZOBJECT
            WHERE ZSTREAMNAME = '/app/usage'
            ORDER BY ZOBJECT.ZENDDATE, ZOBJECT.rowid''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            end_time = convert_ts_human_to_utc(row[0])
            start_time = convert_ts_human_to_utc(row[1])
            added_time = convert_ts_human_to_utc(row[2])
            data_list.append((end_time, start_time, added_time, row[3]))

    data_headers = (
        ('End Time', 'datetime'), ('Start Time', 'datetime'), ('Time Added', 'datetime'), 'Application')
    return data_headers, data_list, db_file


@artifact_processor
def knowledgeC_isLocked(context):
    ''' parse /device/isLocked entries from knowledgeC.db '''
    db_file = _knowledgec_db(context)
    data_list = [(_event_time(row['start']), _event_time(row['end']), _event_time(row['created']),
                  _event_time(row['stored']), _labelled(row['integer'], _BOOL_LABELS),
                  _utc_offset(row['offset']), row['device'])
                 for row in _stream_rows(db_file, '/device/isLocked')]
    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), ('Created', 'datetime'),
        ('Stored On This Device', 'datetime'), 'Screen Locked', 'Event Zone UTC Offset At Write',
        'Source Device ID')
    return data_headers, data_list, db_file


@artifact_processor
def knowledgeC_isBacklit(context):
    ''' parse /display/isBacklit entries from knowledgeC.db '''
    db_file = _knowledgec_db(context)
    data_list = [(_event_time(row['start']), _event_time(row['end']), _event_time(row['created']),
                  _event_time(row['stored']), _labelled(row['integer'], _BOOL_LABELS),
                  _utc_offset(row['offset']), row['device'])
                 for row in _stream_rows(db_file, '/display/isBacklit')]
    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), ('Created', 'datetime'),
        ('Stored On This Device', 'datetime'), 'Backlit', 'Event Zone UTC Offset At Write',
        'Source Device ID')
    return data_headers, data_list, db_file


_LOCATION_ACTIVITY_KEY = 'Z_DKLOCATIONAPPLICATIONACTIVITYMETADATAKEY__'
_APP_ACTIVITY_KEY = 'Z_DKAPPLICATIONACTIVITYMETADATAKEY__'
_PROTOBUF_ERRORS = (ValueError, IndexError, struct.error)


def _pb_varint(buf, pos):
    result = shift = 0
    while True:
        byte = buf[pos]
        pos += 1
        result |= (byte & 0x7F) << shift
        shift += 7
        if byte < 0x80:
            return result, pos
        if shift > 63:
            raise ValueError('varint longer than 10 bytes')


def _pb_fields(buf):
    """Read one protobuf message as (field, wire type, value) triples. Raises ValueError
    when the bytes are not a complete message, so a string is never read as one."""
    fields = []
    pos = 0
    while pos < len(buf):
        key, pos = _pb_varint(buf, pos)
        field, wire = key >> 3, key & 7
        if field == 0:
            raise ValueError('field number 0')
        if wire == 0:
            value, pos = _pb_varint(buf, pos)
        elif wire == 1:
            if pos + 8 > len(buf):
                raise ValueError('truncated fixed64')
            value = struct.unpack('<d', buf[pos:pos + 8])[0]
            pos += 8
        elif wire == 2:
            length, pos = _pb_varint(buf, pos)
            if pos + length > len(buf):
                raise ValueError('truncated length-delimited field')
            value = buf[pos:pos + length]
            pos += length
        elif wire == 5:
            if pos + 4 > len(buf):
                raise ValueError('truncated fixed32')
            value = None
            pos += 4
        else:
            raise ValueError(f'wire type {wire}')
        fields.append((field, wire, value))
    return fields


def _pb_coordinate_pairs(buf, path='', depth=0, found=None):
    """Every nested message whose field 1 and field 2 are doubles within latitude and
    longitude range, with the dotted field path to that message."""
    if found is None:
        found = []
    try:
        fields = _pb_fields(buf)
    except _PROTOBUF_ERRORS:
        return found
    doubles = {field: value for field, wire, value in fields if wire == 1}
    lat, lon = doubles.get(1), doubles.get(2)
    if (path and lat is not None and lon is not None and -90 <= lat <= 90 and -180 <= lon <= 180
            and (lat, lon) != (0.0, 0.0)):
        found.append((path, lat, lon))
    if depth < 16:
        for field, wire, value in fields:
            if wire == 2 and value:
                _pb_coordinate_pairs(value, f'{path}.{field}' if path else str(field), depth + 1, found)
    return found


def _location_activity_payload(required_string):
    """The compressed payload in a user activity's required string: base64 between the
    two $ signs after 'bs'=, four bytes, then a bzip2 stream holding a protobuf (Sarah
    Edwards, mac4n6.com, 2020-01-14). Returns (payload bytes or None, status)."""
    match = re.search(r"'bs'=\$([A-Za-z0-9+/=]+)\$", required_string or '')
    if not match:
        return None, 'Not present'
    try:
        raw = base64.b64decode(match.group(1), validate=True)
    except (binascii.Error, ValueError) as ex:
        return None, f'Not decoded (base64: {ex})'
    if raw[4:7] != b'BZh':
        return None, 'Not decoded (no bzip2 header after the first 4 bytes)'
    try:
        return bz2.decompress(raw[4:]), 'Decoded'
    except (OSError, EOFError, ValueError) as ex:
        return None, f'Not decoded (bzip2: {ex})'


def _metres_between(lat1, lon1, lat2, lon2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi, d_lambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    h = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * 6371008.8 * math.asin(math.sqrt(h))


@artifact_processor
def knowledgeC_LocationActivity(context):
    data_headers = (
        ('Start Time', 'datetime'), ('Creation Time', 'datetime'), 'Location Name', 'Display Name',
        'Address', 'Place Latitude', 'Place Longitude', 'Other Coordinate Pairs in Payload',
        'Farthest Other Pair (m)', 'Compressed Payload', 'Activity UUID', 'Bundle ID')
    data_list = []
    db_file = ''

    for file_found in context.get_files_found():
        if file_found.endswith('knowledgeC.db'):
            db_file = file_found
            break
    if not db_file:
        return data_headers, data_list, db_file

    wanted = (f'{_LOCATION_ACTIVITY_KEY}LOCATIONNAME', f'{_LOCATION_ACTIVITY_KEY}DISPLAYNAME',
              f'{_LOCATION_ACTIVITY_KEY}FULLYFORMATTEDADDRESS', f'{_LOCATION_ACTIVITY_KEY}LATITUDE',
              f'{_LOCATION_ACTIVITY_KEY}LONGITUDE', f'{_APP_ACTIVITY_KEY}USERACTIVITYREQUIREDSTRING',
              f'{_APP_ACTIVITY_KEY}USERACTIVITYUUID')
    with open_sqlite_db_readonly(db_file) as db:
        cursor = db.cursor()
        present = {row[1] for row in cursor.execute('PRAGMA table_info(ZSTRUCTUREDMETADATA)')}
        columns = ', '.join(f'ZSTRUCTUREDMETADATA.{name}' if name in present else 'NULL'
                            for name in wanted)
        cursor.execute(f'''
        SELECT ZOBJECT.ZSTARTDATE, ZOBJECT.ZCREATIONDATE, ZOBJECT.ZVALUESTRING, {columns}
        FROM ZOBJECT
        LEFT OUTER JOIN ZSTRUCTUREDMETADATA ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK
        WHERE ZOBJECT.ZSTREAMNAME = '/app/locationActivity'
        ORDER BY ZOBJECT.ZSTARTDATE, ZOBJECT.ZCREATIONDATE, ZOBJECT.Z_PK
        ''')
        all_rows = cursor.fetchall()

    for (start, created, bundle, location_name, display_name, address, lat, lon,
         required_string, activity_uuid) in all_rows:
        payload, status = _location_activity_payload(required_string)
        if status.startswith('Not decoded'):
            logfunc(f'knowledgeC - Location Activity: payload {status}')
        others = {}
        for path, p_lat, p_lon in (_pb_coordinate_pairs(payload) if payload else []):
            key = (round(p_lat, 6), round(p_lon, 6))
            others.setdefault(key, []).append(path)
        described, farthest = [], None
        for (p_lat, p_lon), paths in others.items():
            paths = list(dict.fromkeys(paths))
            where = paths[0] + (f' and {len(paths) - 1} more' if len(paths) > 1 else '')
            if lat is None or lon is None:
                described.append(f'{p_lat:.6f}, {p_lon:.6f} (field {where})')
                continue
            metres = _metres_between(lat, lon, p_lat, p_lon)
            if metres < 1:
                continue
            farthest = max(farthest or 0, round(metres))
            described.append(f'{p_lat:.6f}, {p_lon:.6f} ({round(metres):,} m from the place coordinates; '
                             f'field {where})')
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(start), convert_cocoa_core_data_ts_to_utc(created),
            location_name, display_name, address, lat, lon, '\n'.join(described),
            farthest if farthest is not None else '', status, activity_uuid, bundle))

    return data_headers, data_list, db_file


@artifact_processor
def knowledgeC_appInFocus(context):
    ''' parse /app/inFocus entries from knowledgeC.db '''
    db_file = _knowledgec_db(context)
    columns = tuple(f'{_APP_KEY}{name}' for name in (
        'LAUNCHREASON', 'EXTENSIONCONTAININGBUNDLEIDENTIFIER', 'EXTENSIONHOSTIDENTIFIER'))
    reason, containing, host = columns
    data_list = [(_event_time(row['start']), _event_time(row['end']), _event_time(row['created']),
                  row['text'], _duration(row), row[reason], row[containing], row[host],
                  _utc_offset(row['offset']), row['device'], row['uuid'])
                 for row in _stream_rows(db_file, '/app/inFocus', columns)]
    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), ('Created', 'datetime'), 'Bundle ID',
        ('Duration Seconds', 'number'), 'Launch Reason (as stored)', 'Extension Containing Bundle ID',
        'Extension Host ID', 'Event Zone UTC Offset At Write', 'Source Device ID', 'Event UUID')
    return data_headers, data_list, db_file
