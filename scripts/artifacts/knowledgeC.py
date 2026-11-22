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
        "description": "Place attributes an app donated with a user activity, from the knowledgeC /app/locationActivity "
                       "stream, with the dropped pin, search and directions fields of the Maps payload",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-30",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "The field meanings, payload decode and time handling below were derived independently, using the"
                 " store's schema, measured data and Apple's code (iOS 13 and iOS 15 binaries read statically, and"
                 " generated classes on macOS 27). The artifact's choice of stream and place columns and its "
                 "generic protobuf wire reader predate that work. Reads the Event rows of the "
                 "/app/locationActivity stream. A row records that an app donated a searchable user activity "
                 "carrying place attributes and that CoreDuet logged it. Place Latitude and Place Longitude are a "
                 "place attribute an app donated. Neither they nor any coordinate in the payload is shown to be a "
                 "device fix, and nothing in this stream shows the device was at that place. All 48 tested rows "
                 "are from Maps: Bundle ID held com.apple.Maps on every row. In the iOS 13.3.1 code the writer "
                 "tests the item's place attributes and not the app, so other apps are not excluded. No tested row"
                 " is from another app. Address is FULLYFORMATTEDADDRESS, Activity UUID is USERACTIVITYUUID and "
                 "Bundle ID is ZVALUESTRING. On the MapKit path in iOS 13.3.1, Apple's code fills Location Name, "
                 "Address, Place Latitude, Place Longitude and Phone Numbers from the map item the activity "
                 "carries. Display Name is not set there. It equalled the activity title on all 48 rows. Phone "
                 "Numbers is the stored archive's list of strings, filled on 22 rows. Start Time is ZSTARTDATE. "
                 "Apple's writer passes one date as both start and end, and the two were equal on all 48 rows, so "
                 "end is not reported. In the iOS 13.3.1 code, that date is taken from the clock when CoreDuet "
                 "builds the event. The stored value is rounded (see below). On iOS 15 there is one event per date"
                 " the user action was sent to the indexer. Start Time fell on a whole minute on all 48 rows (11 "
                 "distinct values in 48 rows). Where that rounding happens was not traced. Created is "
                 "ZCREATIONDATE. Which moment it records for this stream is not established. It was 4.9 to 199.7 "
                 "seconds after Start Time. Payload Status reports the bs value in the user info of the activity's"
                 " required string. The value is a 4-byte little-endian length, then a bzip2 stream of a protobuf."
                 " The length matched on all 28 values. Apple's Maps code names the message MapsActivity. It "
                 "decoded on all 28 rows that hold it and is Not present on the other 20. Field names come from "
                 "Apple's Maps writers and generated classes, and the classes were read on macOS 27 for payloads "
                 "written by iOS 13 and iOS 15. Dropped Pin Latitude, Dropped Pin Longitude and Dropped Pin Time "
                 "are the payload's droppedPin. Dropped Pin Time is read as seconds since 2001-01-01 UTC. On the "
                 "path traced in Apple's code, it is when Maps created the search result the pin came from. Pins "
                 "restored through other paths were not traced. Dropped Pin Time held one value per image (2 "
                 "values on 28 rows). It was at or before Created on all 28 rows. On 20 hickman_ios15 rows it was "
                 "about 38 seconds after Start Time, which is less than the one-minute step Start Time held. Maps "
                 "Search String is searchString (1 row). Presented Map Item is the first entity name of "
                 "presentedMapItem (1 row). Search Places in Payload counts searchPlaces and is blank without a "
                 "payload. Maps can drop trailing search places when it reduces the payload, so the count can be "
                 "lower than the app had and a missing place is not evidence it was absent. Directions Waypoints "
                 "lists the waypoints of the first stored route request: name, coordinate and the "
                 "is_current_location value where one is stored (1 row, 2 waypoints, 1 with the value). Whether "
                 "is_current_location marks the device's position is not established. Not reported: the map camera"
                 " values, whose meaning and units are not established; the mapType and userTrackingMode numbers, "
                 "whose labels are not established for iOS 13 or iOS 15; the times inside directions and place "
                 "data, whose epoch is not established; the MapsAction values, the item identifier and the "
                 "shortcut availability, whose meaning is not established; and the activity title, which equalled "
                 "Display Name on all 48 rows. Several rows can point to one metadata row: hickman_ios15 has 40 "
                 "rows on 9 metadata rows. On hickman_ios13, Location Name, Address, Phone Numbers, Place "
                 "Latitude, Place Longitude and Activity UUID each held one value on all 8 rows. On hickman_ios15,"
                 " Maps Search String, Presented Map Item and Directions Waypoints held no value on any of the 40 "
                 "rows. Only hickman_ios13 (8 rows) and hickman_ios15 (40 rows) hold rows in this stream among the"
                 " images listed in sample_data, so an empty result means only that the database held none.",
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
import bz2
import plistlib
import struct
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, \
    convert_ts_human_to_utc, logfunc

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


# Field number -> (key, child message, wire type) for the MapsActivity fields this artifact reports.
_MAPS_FIELDS = {
    'MapsActivity': {3: ('searchString', None, 2), 4: ('searchPlaces', 'GEOMapItemStorage', 2),
                     7: ('directionsPlan', 'DirectionsPlan', 2), 8: ('droppedPin', 'MSPDroppedPin', 2),
                     11: ('presentedMapItem', 'GEOMapItemStorage', 2)},
    'DirectionsPlan': {1: ('routeRequestStorage', 'GEOStorageRouteRequestStorage', 2)},
    'GEOStorageRouteRequestStorage': {1: ('waypoints', 'GEOComposedWaypoint', 2)},
    'GEOComposedWaypoint': {1: ('waypoint', 'GEOWaypointTyped', 2), 2: ('mapItemStorage', 'GEOMapItemStorage', 2),
                            3: ('latLng', 'GEOLatLng', 2)},
    'GEOWaypointTyped': {5: ('is_current_location', None, 0)},
    'MSPDroppedPin': {1: ('latLng', 'GEOLatLng', 2), 3: ('timestamp', None, 1)},
    'GEOLatLng': {1: ('lat', None, 1), 2: ('lng', None, 1)},
    'GEOMapItemStorage': {1: ('placeData', 'GEOPDPlace', 2)},
    'GEOPDPlace': {4: ('component', 'GEOPDComponent', 2)},
    'GEOPDComponent': {8: ('value', 'GEOPDComponentValue', 2)},
    'GEOPDComponentValue': {1: ('entity', 'GEOPDEntity', 2)},
    'GEOPDEntity': {10: ('name', 'GEOLocalizedString', 2)},
    'GEOLocalizedString': {3: ('string_value', None, 2)},
}


def _maps_message(class_name, buf):
    """The reported fields of one message, as {key: [values]}. Raises on bytes that are not a message."""
    table = _MAPS_FIELDS[class_name]
    out = {}
    for field, wire, value in _pb_fields(buf):
        entry = table.get(field)
        if entry is None or entry[2] != wire:
            continue
        key, child, _ = entry
        if child:
            value = _maps_message(child, value)
        elif wire == 2:
            value = value.decode('utf-8', 'replace')
        out.setdefault(key, []).append(value)
    return out


def _maps_first(message, *keys):
    """The first value at a key path, looking through repeated fields in stored order."""
    if not keys:
        return message
    for value in message.get(keys[0], []):
        found = _maps_first(value, *keys[1:]) if len(keys) > 1 else value
        if found not in (None, ''):
            return found
    return None


class _ActivityString:
    """Value grammar of a user activity's required string: 'text', $base64$, ^url^...%%^,
    ^d...^, --, (array), {(set)}, {key=value,...} and bare numbers."""

    def __init__(self, text):
        self.text = text
        self.pos = 0

    def _at(self, token):
        return self.text.startswith(token, self.pos)

    def _until(self, token):
        end = self.text.index(token, self.pos)
        value = self.text[self.pos:end]
        self.pos = end + len(token)
        return value

    def value(self):
        for token, reader in (("'", lambda: unquote(self._until("'"))),
                              ('$', lambda: base64.b64decode(self._until('$'), validate=True)),
                              ('^url^', lambda: unquote(self._until('%%^'))),
                              ('^d', lambda: self._until('^')),
                              ('--', lambda: None),
                              ('{(', lambda: self._items(')}')),
                              ('(', lambda: self._items(')')),
                              ('{', self._mapping)):
            if self._at(token):
                self.pos += len(token)
                return reader()
        end = self.pos
        while end < len(self.text) and self.text[end] not in ',})&':
            end += 1
        value = self.text[self.pos:end]
        self.pos = end
        return value

    def _items(self, closer):
        items = []
        while not self._at(closer):
            before = self.pos
            items.append(self.value())
            if self._at(','):
                self.pos += 1
            if self.pos == before:
                raise ValueError('array does not advance')
        self.pos += len(closer)
        return items

    def _mapping(self):
        mapping = {}
        while not self._at('}'):
            key = self.value()
            if not self._at('='):
                raise ValueError('expected =')
            self.pos += 1
            mapping[key] = self.value()
            if self._at(','):
                self.pos += 1
        self.pos += 1
        return mapping

    def fields(self):
        """The name=value pairs after the version and activity type."""
        out = {}
        while self.pos < len(self.text):
            name = self._until('=')
            out[name] = self.value()
            if self._at('&'):
                self.pos += 1
            elif self.pos < len(self.text):
                raise ValueError('expected &')
        return out


def _location_activity_payload(required_string):
    """The MapsActivity held under the user-info key bs of a user activity's required string
    (v1.0/<type>/name=value&...). The value is a 4-byte little-endian uncompressed length, then a
    bzip2 stream of the protobuf. Returns (message as {key: [values]} or None, status)."""
    if not required_string:
        return None, 'Not present'
    try:
        if not required_string.startswith('v1.0/'):
            raise ValueError('unknown version')
        _, separator, body = required_string[5:].partition('/')
        if not separator:
            raise ValueError('no activity type')
        user_info = _ActivityString(body).fields().get('u')
    except (ValueError, IndexError, RecursionError):
        return None, 'Not decoded (activity string)'
    if not isinstance(user_info, dict) or 'bs' not in user_info:
        return None, 'Not present'
    data = user_info['bs']
    if not isinstance(data, bytes) or len(data) < 5:
        return None, 'Not decoded (bs value is not data)'
    try:
        expanded = bz2.decompress(data[4:])
    except (OSError, EOFError, ValueError):
        return None, 'Not decoded (bzip2)'
    if len(expanded) != struct.unpack('<I', data[:4])[0]:
        return None, 'Not decoded (length mismatch)'
    try:
        return _maps_message('MapsActivity', expanded), 'Decoded'
    except _PROTOBUF_ERRORS:
        return None, 'Not decoded (protobuf)'


def _keyed_archive_strings(blob):
    """The strings of an NSKeyedArchiver array, joined. Undecoded bytes are shown as hex."""
    if blob is None:
        return ''
    try:
        archive = plistlib.loads(bytes(blob), fmt=plistlib.FMT_BINARY)
        objects = archive['$objects']
        root = objects[archive['$top']['root'].data]
        return '; '.join(str(objects[item.data]) for item in root['NS.objects'])
    except (plistlib.InvalidFileException, KeyError, IndexError, TypeError, AttributeError, ValueError):
        return f'undecoded: {bytes(blob).hex()}'


def _waypoint_lines(payload):
    """One line per stored directions waypoint: name, coordinate and is_current_location as stored."""
    lines = []
    for plan in payload.get('directionsPlan', [])[:1]:
        for storage in plan.get('routeRequestStorage', [])[:1]:
            for waypoint in storage.get('waypoints', []):
                parts = []
                name = _maps_first(waypoint, 'mapItemStorage', 'placeData', 'component', 'value', 'entity',
                                   'name', 'string_value')
                if name:
                    parts.append(name)
                lat, lng = _maps_first(waypoint, 'latLng', 'lat'), _maps_first(waypoint, 'latLng', 'lng')
                if lat is not None and lng is not None:
                    parts.append(f'{lat}, {lng}')
                current = _maps_first(waypoint, 'waypoint', 'is_current_location')
                if current is not None:
                    parts.append(f'is_current_location={current}')
                lines.append(' | '.join(parts))
    return '\n'.join(lines)


@artifact_processor
def knowledgeC_LocationActivity(context):
    data_headers = (
        ('Start Time', 'datetime'), ('Created', 'datetime'), ('Dropped Pin Time', 'datetime'), 'Location Name',
        'Display Name', 'Address', 'Phone Numbers', 'Place Latitude', 'Place Longitude',
        'Dropped Pin Latitude', 'Dropped Pin Longitude', 'Maps Search String', 'Presented Map Item',
        'Search Places in Payload', 'Directions Waypoints', 'Payload Status', 'Activity UUID', 'Bundle ID')
    db_file = _knowledgec_db(context)
    columns = tuple(f'{_LOCATION_ACTIVITY_KEY}{name}' for name in (
        'LOCATIONNAME', 'DISPLAYNAME', 'FULLYFORMATTEDADDRESS', 'LATITUDE', 'LONGITUDE', 'PHONENUMBERS')) + (
        f'{_APP_ACTIVITY_KEY}USERACTIVITYREQUIREDSTRING', f'{_APP_ACTIVITY_KEY}USERACTIVITYUUID')
    name, display, address, lat, lon, phones, required, activity_uuid = columns
    data_list = []
    for row in _stream_rows(db_file, '/app/locationActivity', columns):
        payload, status = _location_activity_payload(row[required])
        if status.startswith('Not decoded'):
            logfunc(f'knowledgeC - Location Activity: payload {status}')
        message = payload or {}
        data_list.append((
            _event_time(row['start']), _event_time(row['created']),
            _event_time(_maps_first(message, 'droppedPin', 'timestamp')),
            row[name], row[display], row[address], _keyed_archive_strings(row[phones]), row[lat], row[lon],
            _maps_first(message, 'droppedPin', 'latLng', 'lat'), _maps_first(message, 'droppedPin', 'latLng', 'lng'),
            _maps_first(message, 'searchString') or '',
            _maps_first(message, 'presentedMapItem', 'placeData', 'component', 'value', 'entity', 'name',
                        'string_value') or '',
            len(message.get('searchPlaces', [])) if payload is not None else '',
            _waypoint_lines(message), status, row[activity_uuid], row['text']))
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
