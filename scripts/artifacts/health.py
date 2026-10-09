"""
This module contains artifacts for Apple Health data
See artifacts description for more details.
"""

__artifacts_v2__ = {
    "health_workouts": {
        "name": "Health - Workouts",
        "description": "Workouts from healthdb_secure.sqlite, with Duration and Total "
                       "Time Duration (end minus start) reported side by side. "
                       "Additional details published within 'Enriching "
                       "Investigations with Apple Watch Data Through the "
                       "healthdb_secure.sqlite Database' at "
                       "https://dfir.pubpub.org/pub/xqvcn3hj/release/1",
        "author": "@KevinPagano3 - @Johann-PLW - @SQLMcGee",
        "creation_date": "2022-08-15",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Health",
        "notes": "The Fahrenheit assumption for HKWeatherTemperature is inherited "
                 "from community queries and unverified.",
        "paths": ("*Health/healthdb_secure.sqlite*", "*Health/healthdb.sqlite*"),
        "output_types": "all",
        "artifact_icon": "activity",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 29 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 6 rows",
            "hickman_ios14": "iOS 14.3 | 12 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "health_provenances": {
        "name": "Health - Provenances",
        "description": "Provenance records (source app, device and operating system build) stored "
                       "for Health data. Queries are a derivative of research provided by Heather "
                       "Mahalik and Jared Barnhart as part of their SANS DFIR Summit 2022 talk as "
                       "well as research provided by Sarah Edwards as part of her APOLLO project. "
                       "https://for585.com/dfirsummit22 - "
                       "https://github.com/mac4n6/APOLLO/tree/"
                       "bd725461fbd22c8ceadd04f0c4ded49b66147439/modules",
        "author": "@KevinPagano3 - @Johann-PLW",
        "creation_date": "2022-08-15",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Health",
        "notes": "",
        "paths": ("*Health/healthdb_secure.sqlite*", "*Health/healthdb.sqlite*"),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "device-mobile",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 55 rows",
            "felix_ios17": "iOS 17.6.1 | 80 rows",
            "fsfull002_ios17": "iOS 17.1 | 17 rows",
            "hc_ios18_7": "iOS 18.7.8 | 8 rows",
            "iphone11_ios17": "iOS 17.3 | 100 rows",
            "iphone12_ios18": "iOS 18.7 | 9 rows",
            "iphone14plus_ios18": "iOS 18.0 | 3 rows",
            "otto_ios17": "iOS 17.5.1 | 144 rows",
            "abe_ios16": "iOS 16.5 | 79 rows",
            "felix23_ios16": "iOS 16.5 | 10 rows",
            "hickman_ios13": "iOS 13.3.1 | 31 rows",
            "hickman_ios14": "iOS 14.3 | 54 rows",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 5 rows",
        }
    },
    "health_headphone_audio_levels": {
        "name": "Health - Headphone Audio Levels",
        "description": "Headphone audio level samples (data type 173), one row per metadata value "
                       "stored for the sample other than the "
                       "_HKPrivateMetadataKeyHeadphoneAudioDataIsTransient key, and one row for a "
                       "sample with no metadata value. Queries are a derivative of research "
                       "provided by Heather Mahalik and Jared Barnhart as part of their SANS DFIR "
                       "Summit 2022 talk as well as research provided by Sarah Edwards as part of "
                       "her APOLLO project. https://for585.com/dfirsummit22 - "
                       "https://github.com/mac4n6/APOLLO/tree/"
                       "bd725461fbd22c8ceadd04f0c4ded49b66147439/modules",
        "author": "@KevinPagano3",
        "creation_date": "2022-08-24",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "Health",
        "notes": "Quantity (as stored) is quantity_samples.quantity for the sample, reported as "
                 "stored; earlier versions of this artifact headed the column Decibels, and the "
                 "unit of the stored number is not established here. A sample with no metadata "
                 "value is reported once with Bundle Name and Key blank. A sample whose only "
                 "metadata value has the key _HKPrivateMetadataKeyHeadphoneAudioDataIsTransient is "
                 "not reported. The sample_data counts were recorded before samples with no "
                 "metadata value were kept and were not remeasured for that change.",
        "paths": ("*Health/healthdb_secure.sqlite*", "*Health/healthdb.sqlite*"),
        "output_types": "standard",
        "artifact_icon": "headphones",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 183 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 27 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 23 rows",
            "abe_ios16": "iOS 16.5 | 17 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 8 rows",
            "hickman_ios14": "iOS 14.3 | 13 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "health_heart_rate": {
        "name": "Health - Heart Rate",
        "description": "Heart rate samples (data type 5). Queries are a derivative of research "
                       "provided by Heather Mahalik and Jared Barnhart as part of their SANS DFIR "
                       "Summit 2022 talk as well as research provided by Sarah Edwards as part of "
                       "her APOLLO project. https://for585.com/dfirsummit22 - "
                       "https://github.com/mac4n6/APOLLO/tree/"
                       "bd725461fbd22c8ceadd04f0c4ded49b66147439/modules",
        "author": "@KevinPagano3 - @Johann-PLW, @AlexisBrignoni, Codex",
        "creation_date": "2023-03-06",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Health",
        "notes": "One row per heart rate sample and distinct stored numeric context value (data type 5). On "
                 "iOS 15 and later a sample that holds a series is reported as one row per value "
                 "in the series and distinct context value. Repeated identical context pairs do not "
                 "add rows; differing values remain separate, without choosing one. "
                 "Rows whose objects.type is 2 are not reported. Heart Rate Context "
                 "is read only from the sample's metadata value whose key is "
                 "_HKPrivateHeartRateContext, as named in the store's metadata_keys table; it is "
                 "blank when the sample has none. On hickman_ios13, hickman_ios14, iphone11_ios17 "
                 "and cookbook_ios1751 no heart rate sample held more than one such value, and "
                 "that key was the only metadata key on these samples. A sample holding two such "
                 "distinct numeric values is reported for both. Heart Rate Context Value reports the "
                 "stored numerical_value separately from the existing label. The quantity-times-60 "
                 "BPM conversion is retained; its basis is not established here. "
                 "The Heart Rate Context labels are not in the "
                 "cited APOLLO health_heart_rate module and their source is not established here; "
                 "a value with no label is shown as stored. Device Name, Manufacturer and "
                 "Hardware are the source_devices name, manufacturer and hardware values of the "
                 "sample's provenance; Device Model is the name this tool maps the Hardware value "
                 "to.",
        "paths": ("*Health/healthdb_secure.sqlite*", "*Health/healthdb.sqlite*"),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 39140 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 3651 rows",
            "hickman_ios14": "iOS 14.3 | 21152 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "health_resting_heart_rate": {
        "name": "Health - Resting Heart Rate",
        "description": "Resting Heart Rate. "
                       "Queries are a derivative of research provided by Heather Mahalik "
                       "and Jared Barnhart as part of their SANS DFIR Summit 2022 talk "
                       "as well as research provided by Sarah Edwards as part of "
                       "her APOLLO project. https://for585.com/dfirsummit22 - "
                       "https://github.com/mac4n6/APOLLO/tree/"
                       "bd725461fbd22c8ceadd04f0c4ded49b66147439/modules",
        "author": "@KevinPagano3 - @Johann-PLW",
        "creation_date": "2023-03-06",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Health",
        "notes": "One row per resting heart rate sample (data type 118) that stores a quantity. "
                 "Hardware ID is the product type of the source record.",
        "paths": ("*Health/healthdb_secure.sqlite*", "*Health/healthdb.sqlite*"),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 107 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 14 rows",
            "hickman_ios14": "iOS 14.3 | 71 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "health_achievements": {
        "name": "Health - Achievements",
        "description": "Earned achievement records from the ACHAchievementsPlugin_earned_instances "
                       "table. Queries are a derivative of research provided by Heather Mahalik "
                       "and Jared Barnhart as part of their SANS DFIR Summit 2022 talk as well as "
                       "research provided by Sarah Edwards as part of her APOLLO project. "
                       "https://for585.com/dfirsummit22 - "
                       "https://github.com/mac4n6/APOLLO/tree/"
                       "bd725461fbd22c8ceadd04f0c4ded49b66147439/modules",
        "author": "@KevinPagano3",
        "creation_date": "2022-08-24",
        "last_update_date": "2026-08-04",
        "requirements": "none",
        "category": "Health",
        "notes": "",
        "paths": ("*Health/healthdb_secure.sqlite*",),
        "output_types": "standard",
        "artifact_icon": "star",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 38 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 22 rows",
            "abe_ios16": "iOS 16.5 | 19 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 8 rows",
            "hickman_ios14": "iOS 14.3 | 30 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "health_steps": {
        "name": "Health - Steps",
        "description": "Step count samples from the samples table of healthdb_secure.sqlite, with "
                       "start and end, steps, duration and the origin product type recorded in the "
                       "sample's provenance and the model it maps to.",
        "author": "@KevinPagano3",
        "creation_date": "2023-10-06",
        "last_update_date": "2025-10-13",
        "requirements": "none",
        "category": "Health",
        "notes": "",
        "paths": ("*Health/healthdb_secure.sqlite*",),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 1860 rows",
            "felix_ios17": "iOS 17.6.1 | 318 rows",
            "fsfull002_ios17": "iOS 17.1 | 1028 rows",
            "hc_ios18_7": "iOS 18.7.8 | 218 rows",
            "iphone11_ios17": "iOS 17.3 | 16996 rows",
            "iphone12_ios18": "iOS 18.7 | 369 rows",
            "iphone14plus_ios18": "iOS 18.0 | 49 rows",
            "otto_ios17": "iOS 17.5.1 | 3265 rows",
            "abe_ios16": "iOS 16.5 | 3337 rows",
            "felix23_ios16": "iOS 16.5 | 81 rows",
            "hickman_ios13": "iOS 13.3.1 | 5544 rows",
            "hickman_ios14": "iOS 14.3 | 14275 rows",
            "jess_ios15": "iOS 15.0.2 | 131 rows",
            "magnet_ios16": "iOS 16.1.1 | 183 rows",
        }
    },
    "health_distance_walking_running": {
        "name": "Health - Walking + Running Distance",
        "description": "Walking and running distance samples from the samples table of "
                       "healthdb_secure.sqlite, with start and end, distance in meters, "
                       "kilometers and miles, duration and the writing device's id and model.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-25",
        "last_update_date": "2026-09-25",
        "requirements": "none",
        "category": "Health",
        "notes": "Reads samples whose data_type is 8 and that have a row in quantity_samples "
                 "and a data_provenances record. "
                 "The Health database names this type itself: on 17 of the tested images, "
                 "the chart records in its shared_summaries table pair "
                 "HKQuantityTypeIdentifierDistanceWalkingRunning with data type 8 and "
                 "HKQuantityTypeIdentifierStepCount with data type 7. Sarah Edwards "
                 "(@iamevltwin, mac4n6.com) also documented data_type 8 as a distance in "
                 "meters in her APOLLO research "
                 "(https://github.com/mac4n6/APOLLO/blob/"
                 "bd725461fbd22c8ceadd04f0c4ded49b66147439/modules/health_distance.txt#L78-L91); "
                 "this query was written independently from "
                 "the live schema. The stored quantity is in meters: on 205 of the 226 chart "
                 "buckets those records store in meters, the type 8 samples in the bucket "
                 "add up to its total, and the 10 samples on each of hickman_ios13, "
                 "hickman_ios14 and iphone11_ios17 that recorded an original unit carried km "
                 "and stored exactly 1,000 times the original value. Distance (Kilometers) "
                 "and Distance (Miles) are computed from the meters value. "
                 "Samples with no quantity_samples row are not reported: 3,293 on "
                 "hickman_ios14 and 12 on hickman_ios13, none on the other tested images. "
                 "Health - Steps skips such samples the same way. Device ID is the origin "
                 "product type from data_provenances. Each writing device, such as an "
                 "iPhone and an Apple Watch, stores its own samples, and they can "
                 "cover the same time: on iphone11_ios17, 4,852 of 18,682 samples overlap "
                 "a sample with a different Device ID, so adding up rows across devices can "
                 "count the same period more than once. Device ID and Device Model held one "
                 "value on every row of 8 of the 20 tested images with rows, each of which "
                 "carried samples from one device. Other distance kinds Health can record, "
                 "such as cycling or swimming, are not read by this artifact; workout "
                 "distance is reported in Health - Workouts. On ctf2020_ios12, "
                 "healthdb_secure.sqlite is an 8-byte file that is not a database.",
        "paths": ("*Health/healthdb_secure.sqlite*",),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 1860 rows",
            "felix_ios17": "iOS 17.6.1 | 316 rows",
            "fsfull002_ios17": "iOS 17.1 | 1023 rows",
            "hc_ios18_7": "iOS 18.7.8 | 218 rows",
            "iphone11_ios17": "iOS 17.3 | 18682 rows",
            "iphone12_ios18": "iOS 18.7 | 370 rows",
            "iphone14plus_ios18": "iOS 18.0 | 49 rows",
            "otto_ios17": "iOS 17.5.1 | 3266 rows",
            "abe_ios16": "iOS 16.5 | 3339 rows",
            "felix23_ios16": "iOS 16.5 | 80 rows",
            "hickman_ios13": "iOS 13.3.1 | 5832 rows",
            "hickman_ios14": "iOS 14.3 | 12728 rows",
            "jess_ios15": "iOS 15.0.2 | 133 rows",
            "magnet_ios16": "iOS 16.1.1 | 183 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 107 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 101 rows",
            "hc_ios26": "iOS 26.5.2 | 263 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 252 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 120 rows",
            "falken_ios26": "iOS 26.2.1 | 92 rows",
        }
    },
    "health_height": {
        "name": "Health - Height Samples",
        "description": "Height samples recorded in Health. This artifact does not report whether "
                       "a sample was user-entered or written by an app or device; see Health - "
                       "Provenances for the sources the database records. Height is displayed "
                       "with the sample's start date "
                       "followed by height in "
                       "meters, centimeters, feet and inches.",
        "author": "@SQLMcGee",
        "creation_date": "2023-04-04",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Health",
        "notes": "",
        "paths": ("*Health/healthdb_secure.sqlite*",),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 1 row",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 1 row",
            "abe_ios16": "iOS 16.5 | 1 row",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 1 row",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "health_weight": {
        "name": "Health - Weight Samples",
        "description": "Weight samples recorded in Health. This artifact does not report whether "
                       "a sample was user-entered or written by an app or device; see Health - "
                       "Provenances for the sources the database records. Weight is displayed "
                       "with the sample's start date "
                       "followed by weight in "
                       "kilograms, stones, and pounds.",
        "author": "@SQLMcGee",
        "creation_date": "2023-04-04",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "Health",
        "notes": "Weight (in Kilograms) is quantity_samples.quantity as stored, with no rounding "
                 "or cutting of digits; earlier versions of this artifact showed its first five "
                 "characters. The kilogram unit is the one the original artifact assigned and is "
                 "not sourced here. Weight (Approximate in Pounds) is the stored quantity "
                 "multiplied by 2.20462262 and rounded to two decimal places; earlier versions "
                 "showed the first six characters of the product.",
        "paths": ("*Health/healthdb_secure.sqlite*",),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 1 row",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 1113 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 1 row",
            "abe_ios16": "iOS 16.5 | 2 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 1105 rows",
            "hickman_ios14": "iOS 14.3 | 1113 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "health_watch_worn_data": {
        "name": "Health - Device - Watch Worn Data",
        "description": "Parses Apple Watch Worn Data from the healthdb_secure.sqlite database"
                       ", grouping the data type 70 samples into periods. A period continues "
                       "while the gap between one sample's end and the next sample's start is "
                       "3,600 seconds or less. Hours Worn and the hours off before the next "
                       "period retain fractional hours. The reading of data type 70 as watch "
                       "worn, in one-hour samples, is the cited article's. "
                       "Additional details published within 'Apple Watch Worn Data Analysis' at "
                       "https://metadataperspective.com/2024/05/20/apple-watch-worn-data-analysis/",
        "author": "@SQLMcGee for Metadata Forensics, LLC, @AlexisBrignoni, Codex",
        "creation_date": "2024-05-20",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Health",
        "notes": "",
        "paths": ("*Health/healthdb_secure.sqlite*",),
        "output_types": "standard",
        "artifact_icon": "device-watch",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 52 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 15 rows",
            "hickman_ios14": "iOS 14.3 | 37 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    'health_all_watch_sleep_data': {
        'name': 'Health - Sleep - All Watch Sleep Data',
        'description': 'Parses Apple Health Sleep Data from the healthdb_secure.sqlite database',
        'author': '@SQLMcGee for Metadata Forensics, LLC',
        'creation_date': '2024-08-01',
        'last_update_date': '2026-10-09',
        'requirements': 'none',
        'category': 'Health',
        'notes': "One row per sleep sample (data type 63) whose provenance names a Watch and whose "
                 "category value is not 0 or 1. Values 2, 3, 4 and 5 are labelled AWAKE, CORE, "
                 "DEEP and REM, the names the cited article gives them; any other value is "
                 "shown in Sleep State as the stored number, with no label. Additional details "
                 "published within 'Sleepless in Cupertino: A Forensic Dive into Apple Watch Sleep "
                 "Tracking' at "
                 "https://metadataperspective.com/2024/08/01/"
                 "sleepless-in-cupertino-a-forensic-dive-into-apple-watch-sleep-tracking/",
        'paths': ('*Health/healthdb_secure.sqlite*',),
        'output_types': 'standard',
        'artifact_icon': 'moon',
        'sample_data': {
            'ctf2020_ios12': 'iOS 12.4 | 0 rows',
            'dexter_ios18': 'iOS 18.3.2 | 0 rows',
            'felix_ios17': 'iOS 17.6.1 | 0 rows',
            'fsfull002_ios17': 'iOS 17.1 | 0 rows',
            'hc_ios18_7': 'iOS 18.7.8 | 0 rows',
            'iphone11_ios17': 'iOS 17.3 | 93 rows',
            'iphone12_ios18': 'iOS 18.7 | 0 rows',
            'iphone14plus_ios18': 'iOS 18.0 | 0 rows',
            'otto_ios17': 'iOS 17.5.1 | 0 rows',
            'abe_ios16': 'iOS 16.5 | 0 rows',
            'felix23_ios16': 'iOS 16.5 | 0 rows',
            'hickman_ios13': 'iOS 13.3.1 | 0 rows',
            'hickman_ios14': 'iOS 14.3 | 0 rows',
            'jess_ios15': 'iOS 15.0.2 | 0 rows',
            'magnet_ios16': 'iOS 16.1.1 | 0 rows',
        }
    },
    "health_watch_by_sleep_period": {
        "name": "Health - Sleep - Watch By Sleep Period",
        "description": "Parses Apple Health Sleep Data from the healthdb_secure.sqlite database"
                       ". One row per run of Watch sleep stage samples with consecutive data_id "
                       "values, which this artifact treats as one sleep period. Time in Bed is the "
                       "span from the earliest start to the latest end of the period. "
                       "Additional details published within 'Sleepless in Cupertino: "
                       "A Forensic Dive into Apple Watch Sleep Tracking' at "
                       "https://metadataperspective.com/2024/08/01/sleepless-in-cupertino-a-"
                       "forensic-dive-into-apple-watch-sleep-tracking/",
        "author": "@SQLMcGee for Metadata Forensics, LLC, @AlexisBrignoni, Codex",
        "creation_date": "2024-08-01",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Health",
        "notes": "The samples read are sleep samples (data type 63) whose provenance names a Watch "
                 "and whose category value is not 0 or 1. Category values 2, 3, 4 and 5 are "
                 "counted as awake, core, deep and REM, the names the cited article gives them. A "
                 "sample with any other category value stays in its period: it counts toward the "
                 "period span and toward the total each percentage is divided by, and toward no "
                 "stage duration or stage percentage, so the four percentages of such a period "
                 "add up to less than 100. Whether a tested image holds such a sample was not "
                 "measured.",
        "paths": ("*Health/healthdb_secure.sqlite*",),
        "output_types": "standard",
        "artifact_icon": "moon",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 4 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "health_source_devices": {
        "name": "Health - Source Devices",
        "description": "Source device records selected from healthdb.sqlite, including the stored "
                       "model field beside the existing mapped Model value.",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2025-03-03",
        "last_update_date": "2026-10-07",
        "requirements": "none",
        "category": "Health",
        "notes": "The model (as stored) column retains source_devices.model without conversion "
                 "beside Model (existing mapping), which retains the existing Bluetooth PID "
                 "lookup and fallback. A mapped product name does not establish physical device "
                 "identity or ownership. Existing selection remains name NOT LIKE '__NONE__' AND"
                 " localIdentifier NOT LIKE '__NONE__': underscores are SQL LIKE wildcards and "
                 "NULL predicates exclude rows. Local ID retains the existing str() conversion "
                 "and terminal -tacl suffix removal. Optional Sync Provenance and Sync ID "
                 "columns retain their existing schema-dependent presence and values. Creation "
                 "Date conversion, first selected healthdb.sqlite, hardware-to-device lookup, "
                 "row order and all prior values are unchanged; this stage does not repair "
                 "selection, suffix trimming or source association. Original artifact "
                 "contribution/research attribution: @stark4n6; existing Bluetooth PID reference"
                 " retained in the source comment. Historical sample_data counts remain recorded"
                 " and are not assumed remeasured by this change.",
        "paths": ("*Health/healthdb.sqlite*",),
        "output_types": "standard",
        "artifact_icon": "device-mobile",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1 row",
            "dexter_ios18": "iOS 18.3.2 | 15 rows",
            "felix_ios17": "iOS 17.6.1 | 15 rows",
            "fsfull002_ios17": "iOS 17.1 | 9 rows",
            "hc_ios18_7": "iOS 18.7.8 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 25 rows",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "iphone14plus_ios18": "iOS 18.0 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 9 rows",
            "abe_ios16": "iOS 16.5 | 9 rows",
            "felix23_ios16": "iOS 16.5 | 4 rows",
            "hickman_ios13": "iOS 13.3.1 | 4 rows",
            "hickman_ios14": "iOS 14.3 | 13 rows",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 2 rows",
        }
    },
    "health_wrist_temperature": {
        "name": "Health - Wrist Temperature",
        "description": "Reads samples of data type 256 as Apple Health wrist temperature. None of "
                       "the 15 images in sample_data returned a row, so the data type, the unit "
                       "and the metadata keys are not validated against data. The Health app shows "
                       "this data at Health Application > Summary > Show All Health Data > Wrist "
                       "Temperature > Show All Data > All Recorded Data",
        "author": "@SQLMcGee for Metadata Forensics, LLC",
        "creation_date": "2025-06-20",
        "last_update_date": "2025-10-13",
        "requirements": "none",
        "category": "Health",
        "notes": "",
        "paths": ("*Health/healthdb_secure.sqlite*", "*Health/healthdb.sqlite*"),
        "output_types": "standard",
        "artifact_icon": "thermometer",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    }
}

from packaging import version
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, \
    attach_sqlite_db_readonly, does_table_exist_in_db, convert_cocoa_core_data_ts_to_utc, \
    does_column_exist_in_db


def _record_value(record, index, default=None):
    return record[index] if index < len(record) else default


@artifact_processor
def health_workouts(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    healthdb = context.get_source_file_path('healthdb.sqlite')

    data_list = []

    activity_types = '''
        WHEN 1 THEN "AMERICAN FOOTBALL"
        WHEN 2 THEN "ARCHERY"
        WHEN 3 THEN "AUSTRALIAN FOOTBALL"
        WHEN 4 THEN "BADMINTON"
        WHEN 5 THEN "BASEBALL"
        WHEN 6 THEN "BASKETBALL"
        WHEN 7 THEN "BOWLING"
        WHEN 8 THEN "BOXING"
        WHEN 9 THEN "CLIMBING"
        WHEN 10 THEN "CRICKET"
        WHEN 11 THEN "CROSS TRAINING"
        WHEN 12 THEN "CURLING"
        WHEN 13 THEN "CYCLING"
        WHEN 16 THEN "ELLIPTICAL"
        WHEN 17 THEN "EQUESTRIAN SPORTS"
        WHEN 18 THEN "FENCING"
        WHEN 19 THEN "FISHING"
        WHEN 20 THEN "FUNCTION STRENGTH TRAINING"
        WHEN 21 THEN "GOLF"
        WHEN 22 THEN "GYMNASTICS"
        WHEN 23 THEN "HANDBALL"
        WHEN 24 THEN "HIKING"
        WHEN 25 THEN "HOCKEY"
        WHEN 26 THEN "HUNTING"
        WHEN 27 THEN "LACROSS"
        WHEN 28 THEN "MARTIAL ARTS"
        WHEN 29 THEN "MIND AND BODY"
        WHEN 31 THEN "PADDLE SPORTS"
        WHEN 32 THEN "PLAY"
        WHEN 33 THEN "PREPARATION AND RECOVERY"
        WHEN 34 THEN "RACQUETBALL"
        WHEN 35 THEN "ROWING"
        WHEN 36 THEN "RUGBY"
        WHEN 37 THEN "RUNNING"
        WHEN 38 THEN "SAILING"
        WHEN 39 THEN "SKATING SPORTS"
        WHEN 40 THEN "SNOW SPORTS"
        WHEN 41 THEN "SOCCER"
        WHEN 42 THEN "SOFTBALL"
        WHEN 43 THEN "SQUASH"
        WHEN 44 THEN "STAIRSTEPPER"
        WHEN 45 THEN "SURFING SPORTS"
        WHEN 46 THEN "SWIMMING"
        WHEN 47 THEN "TABLE TENNIS"
        WHEN 48 THEN "TENNIS"
        WHEN 49 THEN "TRACK AND FIELD"
        WHEN 50 THEN "TRADITIONAL STRENGTH TRAINING"
        WHEN 51 THEN "VOLLEYBALL"
        WHEN 52 THEN "WALKING"
        WHEN 53 THEN "WATER FITNESS"
        WHEN 54 THEN "WATER POLO"
        WHEN 55 THEN "WATER SPORTS"
        WHEN 56 THEN "WRESTLING"
        WHEN 57 THEN "YOGA"
        WHEN 58 THEN "BARRE"
        WHEN 59 THEN "CORE TRAINING"
        WHEN 60 THEN "CROSS COUNTRY SKIING"
        WHEN 61 THEN "DOWNHILL SKIING"
        WHEN 62 THEN "FLEXIBILITY"
        WHEN 63 THEN "HIGH INTENSITY INTERVAL TRAINING (HIIT)"
        WHEN 64 THEN "JUMP ROPE"
        WHEN 65 THEN "KICKBOXING"
        WHEN 66 THEN "PILATES"
        WHEN 67 THEN "SNOWBOARDING"
        WHEN 68 THEN "STAIRS"
        WHEN 69 THEN "STEP TRAINING"
        WHEN 70 THEN "WHEELCHAIR WALK PACE"
        WHEN 71 THEN "WHEELCHAIR RUN PACE"
        WHEN 72 THEN "TAI CHI"
        WHEN 73 THEN "MIXED CARDIO"
        WHEN 74 THEN "HAND CYCLING"
        WHEN 75 THEN "DISC SPORTS"
        WHEN 76 THEN "FITNESS GAMING"
        WHEN 77 THEN "DANCE"
        WHEN 78 THEN "SOCIAL DANCE"
        WHEN 79 THEN "PICKLEBALL"
        WHEN 80 THEN "COOLDOWN"
        WHEN 3000 THEN "OTHER"
    '''

    goal_types = '''
        WHEN 0 THEN "Open"
        WHEN 1 THEN "Distance in meters"
        WHEN 2 THEN "Time in seconds"
        WHEN 3 THEN "Kilocalories"
        ELSE "Unknown" || "-" || workouts.goal_type
    '''

    distance_and_goals = '''
        round(workouts.total_distance, 2) AS 'Distance (in Km)',
        round(workouts.total_distance * 0.621371, 2) AS 'Distance (in Miles)',
        CASE workouts.goal_type''' + goal_types + '''
        END AS 'Goal Type',
        CAST(workouts.goal AS INT) AS 'Goal',
    '''

    metadata = '''
        MAX(
            CASE
                WHEN "metadata_keys"."key" = 'HKAverageMETs'
                THEN round(metadata_values.numerical_value, 1)
                ELSE NULL
            END)
        AS 'Average METs',
        MAX(
            CASE
                WHEN "metadata_keys"."key" = '_HKPrivateWorkoutMinHeartRate'
                THEN CAST(round(metadata_values.numerical_value * 60) AS INT)
                ELSE NULL
            END)
        AS 'Min. Heart Rate (BPM)',
        MAX(
            CASE
                WHEN "metadata_keys"."key" = '_HKPrivateWorkoutMaxHeartRate'
                THEN CAST(round(metadata_values.numerical_value * 60) AS INT)
                ELSE NULL
            END)
        AS 'Max. Heart Rate (BPM)',
        MAX(
            CASE
                WHEN "metadata_keys"."key" = '_HKPrivateWorkoutAverageHeartRate'
                THEN CAST(round(metadata_values.numerical_value * 60) AS INT)
                ELSE NULL
            END)
        AS 'Average Heart Rate (BPM)',
        MAX(
            CASE
                WHEN "metadata_keys"."key" = 'HKWeatherTemperature'
                THEN round(metadata_values.numerical_value, 2)
                ELSE NULL
            END)
        AS 'Weather Temperature (assumed °F)',
        MAX(
            CASE
                WHEN "metadata_keys"."key" = 'HKWeatherHumidity'
                THEN CAST(metadata_values.numerical_value AS INT)
                ELSE NULL
            END)
        AS 'Humidity (%)',
        MAX(
            CASE
                WHEN "metadata_keys"."key" = '_HKPrivateWorkoutWeatherLocationCoordinatesLatitude'
                THEN metadata_values.numerical_value
                ELSE NULL
            END)
        AS 'Latitude',
        MAX(
            CASE
                WHEN "metadata_keys"."key" = '_HKPrivateWorkoutWeatherLocationCoordinatesLongitude'
                THEN metadata_values.numerical_value
                ELSE NULL
            END)
        AS 'Longitude',
        MAX(
            CASE
                WHEN "metadata_keys"."key" = '_HKPrivateWorkoutMinGroundElevation'
                THEN round(metadata_values.numerical_value, 2)
                ELSE NULL
            END)
        AS 'Min. ground elevation (in Meters)',
        MAX(
            CASE
                WHEN "metadata_keys"."key" = '_HKPrivateWorkoutMaxGroundElevation'
                THEN round(metadata_values.numerical_value, 2)
                ELSE NULL
            END)
        AS 'Max ground elevation (in Meters)',
    '''

    source = '''
        healthdb.source_devices.hardware AS 'Hardware',
        healthdb.sources.name AS 'Source',
        data_provenances.source_version AS 'Software Version',
        data_provenances.tz_name AS 'Timezone',
        objects.creation_date
    '''

    attach_query = attach_sqlite_db_readonly(healthdb, 'healthdb')

    workout_activities_exists = does_table_exist_in_db(data_source, 'workout_activities')

    if workout_activities_exists:
        query = '''
        SELECT
            workout_activities.start_date,
            workout_activities.end_date,
            CASE workout_activities.activity_type''' + activity_types + '''
                ELSE "Unknown" || "-" || workout_activities.activity_type
            END AS 'Type',
            CASE workout_activities.location_type
                WHEN 2 THEN 'Indoor'
                WHEN 3 THEN 'Outdoor'
                ELSE workout_activities.location_type
            END AS 'Location Type',
            strftime('%H:%M:%S', samples.end_date - samples.start_date, 'unixepoch') AS 'Total Time Duration',
            strftime('%H:%M:%S', workout_activities.duration, 'unixepoch') AS 'Duration',
            ''' + distance_and_goals + '''
            MAX(
                CASE
                    WHEN workout_statistics.data_type = 10 THEN round(workout_statistics.quantity, 2)
                    ELSE NULL
                END)
            AS 'Total Active Energy (kcal)',
            MAX(
                CASE
                    WHEN workout_statistics.data_type = 9 THEN round(workout_statistics.quantity, 2)
                    ELSE NULL
                END)
            AS 'Total Resting Energy (kcal)',
            ''' + metadata + source + '''
        FROM workout_activities
        LEFT OUTER JOIN workouts ON workouts.data_id = workout_activities.owner_id
        LEFT OUTER JOIN workout_statistics ON workout_statistics.workout_activity_id = workout_activities.ROWID
        LEFT OUTER JOIN metadata_values ON metadata_values.object_id = workout_activities.owner_id
        LEFT OUTER JOIN metadata_keys ON metadata_keys.ROWID = metadata_values.key_id
        LEFT OUTER JOIN objects ON objects.data_id = workout_activities.owner_id
        LEFT OUTER JOIN data_provenances ON data_provenances.ROWID = objects.provenance
        LEFT OUTER JOIN healthdb.source_devices ON healthdb.source_devices.ROWID = data_provenances.device_id
        LEFT OUTER JOIN healthdb.sources ON healthdb.sources.ROWID = data_provenances.source_id
        LEFT OUTER JOIN samples ON samples.data_id = workouts.data_id
        GROUP BY workout_activities.ROWID
        ORDER BY workout_activities.start_date
        '''
    else:
        query = '''
        SELECT
            samples.start_date,
            samples.end_date,
            CASE workouts.activity_type''' + activity_types + '''
                ELSE "Unknown" || "-" || workouts.activity_type
            END AS 'Type',
            NULL AS 'Location Type',
            strftime('%H:%M:%S', samples.end_date - samples.start_date, 'unixepoch') AS 'Total Time Duration',
            strftime('%H:%M:%S', workouts.duration, 'unixepoch') AS 'Duration',
            ''' + distance_and_goals + '''
            round(workouts.total_energy_burned, 2) AS 'Total Active Energy (kcal)',
            round(workouts.total_basal_energy_burned, 2) AS 'Total Resting Energy (kcal)',
            ''' + metadata + source + '''
        FROM workouts
        LEFT OUTER JOIN samples ON samples.data_id = workouts.data_id
        LEFT OUTER JOIN metadata_values ON metadata_values.object_id = workouts.data_id
        LEFT OUTER JOIN metadata_keys ON metadata_keys.ROWID = metadata_values.key_id
        LEFT OUTER JOIN objects ON objects.data_id = workouts.data_id
        LEFT OUTER JOIN data_provenances ON data_provenances.ROWID = objects.provenance
        LEFT OUTER JOIN healthdb.source_devices ON healthdb.source_devices.ROWID = data_provenances.device_id
        LEFT OUTER JOIN healthdb.sources ON healthdb.sources.ROWID = data_provenances.source_id
        GROUP BY workouts.data_id
        ORDER BY samples.start_date
        '''

    data_headers = (
        ('Start Timestamp', 'datetime'), ('End Timestamp', 'datetime'),
        'Activity Type', 'Location Type', 'Total Time Duration', 'Duration',
        'Distance (in KM)', 'Distance (in Miles)', 'Goal Type', 'Goal',
        'Total Active Energy (kcal)', 'Total Resting Energy (kcal)', 'Average METs',
        'Min. Heart Rate (BPM)', 'Max. Heart Rate (BPM)', 'Average Heart Rate (BPM)',
        'Weather Temperature (assumed °F, converted to °C)',
        'Weather Temperature (assumed °F)', 'Humidity (%)', 'Latitude', 'Longitude',
        'Min. ground elevation (in Meters)', 'Max. ground elevation (in Meters)',
        'Device ID', 'Device Model', 'Source', 'Software Version', 'Timezone',
        ('Timestamp added to Health', 'datetime'))

    db_records = get_sqlite_db_records(data_source, query, attach_query)

    for record in db_records:
        def value(index, default=None):
            return _record_value(record, index, default)

        celcius_temp = None
        start_timestamp = convert_cocoa_core_data_ts_to_utc(value(0))
        end_timestamp = convert_cocoa_core_data_ts_to_utc(value(1))
        added_timestamp = convert_cocoa_core_data_ts_to_utc(value(26))
        device_id = value(22)
        device_model = context.lookup_metadata('apple_device_id_to_model', device_id)

        fahrenheit_temp = value(16)
        if fahrenheit_temp:
            celcius_temp = round(((fahrenheit_temp - 32) * (5 / 9)), 2)

        data_list.append(
            (start_timestamp, end_timestamp, str(value(2)).title(), value(3),
             value(4), value(5), value(6), value(7), value(8), value(9),
             value(10), value(11), value(12), value(13), value(14), value(15),
             celcius_temp, fahrenheit_temp, value(17), value(18), value(19),
             value(20), value(21), device_id, device_model, value(23),
             value(24), value(25), added_timestamp)
            )

    return data_headers, data_list, data_source


@artifact_processor
def health_provenances(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    healthdb = context.get_source_file_path('healthdb.sqlite')

    data_list = []

    attach_query = attach_sqlite_db_readonly(healthdb, 'healthdb')

    query = '''
    SELECT
        data_provenances.ROWID AS 'Row ID',
        data_provenances.origin_product_type AS 'Origin Product Type',
        data_provenances.origin_build AS 'Origin OS Build',
        data_provenances.local_product_type AS 'Local Product Type',
        data_provenances.local_build AS 'Local OS Build',
        data_provenances.source_id AS 'Source ID',
        healthdb.sources.name AS ' Source Name',
        data_provenances.source_version AS 'Source Version',
        data_provenances.device_id AS 'Device ID',
        CASE
            WHEN healthdb.source_devices.name = '__NONE__' THEN ''
            ELSE healthdb.source_devices.name
        END AS 'Device',
        data_provenances.tz_name AS 'Timezone'
    FROM data_provenances
    LEFT OUTER JOIN healthdb.sources ON healthdb.sources.ROWID = data_provenances.source_id
    LEFT OUTER JOIN healthdb.source_devices ON healthdb.source_devices.ROWID = data_provenances.device_id
    ORDER BY data_provenances.ROWID
    '''

    data_headers = (
        'Row ID', 'Origin Product Type', 'Origin Product Model', 'Origin OS Build',
        'Origin OS Version', 'Local Product Type', 'Local Product Model',
        'Local OS Build', 'Local OS Version', 'Source ID', 'Source Name',
        'Source Version', 'Device ID', 'Device', 'Timezone')

    db_records = get_sqlite_db_records(data_source, query, attach_query)

    for record in db_records:
        origin_device_model = context.lookup_metadata('apple_device_id_to_model', record[1])
        origin_os_version = context.get_apple_os_version(record[2], record[1])
        local_device_model = context.lookup_metadata('apple_device_id_to_model', record[3])
        local_os_version = context.get_apple_os_version(record[4], record[3])

        data_list.append(
            (record[0], record[1], origin_device_model, record[2], origin_os_version,
             record[3], local_device_model, record[4], local_os_version, record[5],
             record[6], record[7], record[8], record[9], record[10])
            )

    return data_headers, data_list, data_source


@artifact_processor
def health_headphone_audio_levels(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    healthdb = context.get_source_file_path('healthdb.sqlite')

    data_list = []

    attach_query = attach_sqlite_db_readonly(healthdb, 'healthdb')

    query = '''
    SELECT
        samples.start_date,
        samples.end_date,
        quantity_samples.quantity,
        metadata_values.string_value,
        healthdb.source_devices.name,
        healthdb.source_devices.manufacturer,
        healthdb.source_devices.model,
        healthdb.source_devices.localIdentifier,
        metadata_keys.key,
        samples.data_id
    FROM samples
    LEFT OUTER JOIN quantity_samples ON samples.data_id = quantity_samples.data_id
    LEFT OUTER JOIN metadata_values ON metadata_values.object_id = samples.data_id
    LEFT OUTER JOIN metadata_keys ON metadata_keys.ROWID = metadata_values.key_id
    LEFT OUTER JOIN objects ON samples.data_id = objects.data_id
    LEFT OUTER JOIN data_provenances ON objects.provenance = data_provenances.ROWID
    LEFT OUTER JOIN healthdb.source_devices ON healthdb.source_devices.ROWID = data_provenances.device_id
    WHERE samples.data_type = 173
        AND (metadata_values.object_id IS NULL
             OR metadata_keys.key != '_HKPrivateMetadataKeyHeadphoneAudioDataIsTransient')
    '''

    data_headers = (
        ('Start Timestamp', 'datetime'), ('End Timestamp', 'datetime'), 'Quantity (as stored)',
        'Bundle Name', 'Device Name', 'Device Manufacturer', 'Device Model',
        'Local Identifier', 'Key', 'Data ID')

    db_records = get_sqlite_db_records(data_source, query, attach_query)

    for record in db_records:
        start_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        end_timestamp = convert_cocoa_core_data_ts_to_utc(record[1])
        data_list.append(
            (start_timestamp, end_timestamp, record[2], record[3], record[4],
             record[5], record[6], record[7], record[8], record[9]))

    return data_headers, data_list, data_source


@artifact_processor
def health_heart_rate(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    healthdb = context.get_source_file_path('healthdb.sqlite')

    data_list = []
    os_version = context.get_installed_os_version()

    attach_query = attach_sqlite_db_readonly(healthdb, 'healthdb')

    query = '''
    SELECT
        samples.start_date,
        samples.end_date,
        CAST(round(quantity_samples.quantity * 60) AS INT),
        CASE metadata_values.numerical_value
            WHEN 1.0 THEN 'Background'
            WHEN 2.0 THEN 'Streaming'
            WHEN 3.0 THEN 'Sedentary'
            WHEN 4.0 THEN 'Walking'
            WHEN 5.0 THEN 'Breathe'
            WHEN 6.0 THEN 'Workout'
            WHEN 8.0 THEN 'Background'
            WHEN 9.0 THEN 'ECG'
            WHEN 10.0 THEN 'Blood Oxygen Saturation'
            ELSE metadata_values.numerical_value
        END,
        objects.creation_date,
        CASE healthdb.source_devices.name
            WHEN '__NONE__' THEN ''
            ELSE healthdb.source_devices.name
        END,
        healthdb.source_devices.manufacturer,
        healthdb.source_devices.hardware,
        healthdb.sources.name,
        data_provenances.source_version,
        data_provenances.tz_name,
        quantity_sample_series.hfd_key,
        quantity_sample_series.count,
        healthdb.sources.source_options,
        metadata_values.numerical_value
    FROM samples
    LEFT JOIN quantity_samples on samples.data_id = quantity_samples.data_id
    LEFT JOIN (
        SELECT DISTINCT metadata_values.object_id, metadata_values.numerical_value
        FROM metadata_values
        JOIN metadata_keys ON metadata_values.key_id = metadata_keys.ROWID
        WHERE metadata_keys.key = '_HKPrivateHeartRateContext'
    ) AS metadata_values ON samples.data_id = metadata_values.object_id
    LEFT JOIN objects ON samples.data_id = objects.data_id
    LEFT JOIN data_provenances ON objects.provenance = data_provenances.ROWID
    LEFT JOIN healthdb.sources ON data_provenances.source_id = healthdb.sources.ROWID
    LEFT JOIN healthdb.source_devices ON data_provenances.device_id = healthdb.source_devices.ROWID
    LEFT JOIN quantity_sample_series ON samples.data_id = quantity_sample_series.data_id
    WHERE samples.data_type = 5 AND objects.type != 2
    ORDER BY samples.start_date DESC
    '''

    db_records = get_sqlite_db_records(data_source, query, attach_query)

    for record in db_records:
        start_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        end_timestamp = convert_cocoa_core_data_ts_to_utc(record[1])
        added_timestamp = convert_cocoa_core_data_ts_to_utc(record[4])
        device_model = context.lookup_metadata('apple_device_id_to_model', record[7])
        if version.parse(os_version) >= version.parse("15"):
            if record[11] and record[12] > 0:
                quantity_series_data_query = '''
                SELECT
                    quantity_series_data.timestamp,
                    CAST(round(quantity_series_data.value *60) AS INT)
                FROM quantity_series_data
                WHERE quantity_series_data.series_identifier = ''' + str(record[11]) + '''
                ORDER BY quantity_series_data.timestamp DESC
                '''
                quantity_series_data_records = get_sqlite_db_records(data_source, quantity_series_data_query)
                for qsd_record in quantity_series_data_records:
                    series_data_date = convert_cocoa_core_data_ts_to_utc(qsd_record[0])
                    data_list.append(
                        (series_data_date, added_timestamp, qsd_record[1], record[3],
                         record[5], record[6], record[7], device_model, record[8],
                         record[9], record[10], record[14]))
            else:
                data_list.append(
                    (start_timestamp, added_timestamp, record[2], record[3], record[5],
                     record[6], record[7], device_model, record[8], record[9], record[10], record[14]))
        else:
            data_list.append(
                (start_timestamp, end_timestamp, added_timestamp, record[2], record[3],
                 record[5], record[6], record[7], device_model, record[8], record[9], record[10], record[14]))

    if version.parse(os_version) >= version.parse("15"):
        data_headers = (
            ('Date', 'datetime'), ('Date added to Health', 'datetime'),
            'Heart Rate (BPM)', 'Heart Rate Context', 'Device Name', 'Manufacturer',
            'Hardware', 'Device Model', 'Source', 'Software Version', 'Timezone', 'Heart Rate Context Value')
    else:
        data_headers = (
            ('Start Date', 'datetime'), ('End Date', 'datetime'),
            ('Date added to Health', 'datetime'), 'Heart Rate (BPM)', 'Heart Rate Context',
            'Device Name', 'Manufacturer', 'Hardware', 'Device Model', 'Source',
            'Software Version', 'Timezone', 'Heart Rate Context Value')

    return data_headers, data_list, data_source


@artifact_processor
def health_resting_heart_rate(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    healthdb = context.get_source_file_path('healthdb.sqlite')

    data_list = []

    attach_query = attach_sqlite_db_readonly(healthdb, 'healthdb')

    query = '''
    SELECT
        samples.start_date,
        samples.end_date,
        CAST(quantity_samples.quantity AS INT),
        objects.creation_date,
        healthdb.sources.product_type,
        healthdb.sources.name
    FROM samples
    LEFT JOIN quantity_samples ON samples.data_id = quantity_samples.data_id
    LEFT JOIN objects ON samples.data_id = objects.data_id
    LEFT JOIN data_provenances ON objects.provenance = data_provenances.ROWID
    LEFT JOIN healthdb.sources ON data_provenances.source_id = healthdb.sources.ROWID
    WHERE samples.data_type = 118 AND quantity_samples.quantity NOT NULL
    ORDER BY samples.start_date DESC
    '''

    data_headers = (
        ('Start Date', 'datetime'), ('End Date', 'datetime'), 'Resting Heart Rate (BPM)',
        ('Date added to Health', 'datetime'), 'Hardware ID',
        'Device Model', 'Source')

    db_records = get_sqlite_db_records(data_source, query, attach_query)

    for record in db_records:
        start_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        end_timestamp = convert_cocoa_core_data_ts_to_utc(record[1])
        added_timestamp = convert_cocoa_core_data_ts_to_utc(record[3])
        device_model = context.lookup_metadata('apple_device_id_to_model', record[4])
        data_list.append(
            (start_timestamp, end_timestamp, record[2], added_timestamp, record[4],
             device_model, record[5]))

    return data_headers, data_list, data_source


@artifact_processor
def health_achievements(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    data_list = []

    query = '''
    SELECT
        created_date,
        earned_date,
        template_unique_name,
        value_in_canonical_unit,
        value_canonical_unit,
        creator_device
    FROM ACHAchievementsPlugin_earned_instances
    '''

    data_headers = (
        ('Created Timestamp', 'datetime'), ('Earned Date', 'date'), 'Achievement',
        'Value', 'Unit', 'Creator Device')

    db_records = get_sqlite_db_records(data_source, query)

    for record in db_records:
        # created_date is REAL (Core Data seconds) in older schemas but TEXT in
        # newer ones (seen on iOS 26); a str value made the converter's
        # arithmetic raise and abort the artifact. Convert numeric values
        # (including numeric strings) and pass other text through as-is.
        created_date = record[0]
        try:
            created_timestamp = convert_cocoa_core_data_ts_to_utc(float(created_date))
        except (TypeError, ValueError):
            created_timestamp = created_date
        data_list.append((created_timestamp, record[1], record[2], record[3],
                          record[4], record[5]))

    return data_headers, data_list, data_source


@artifact_processor
def health_steps(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    data_list = []

    query = '''
    SELECT
        samples.start_date AS "Start Date",
        samples.end_date AS "End Date",
        quantity_samples.quantity AS "Steps",
        (samples.end_date - samples.start_date) AS "Duration (Seconds)",
        data_provenances.origin_product_type AS "Device"
    FROM samples, quantity_samples, data_provenances, objects
    WHERE samples.data_type = 7
    AND samples.data_id = quantity_samples.data_id
    AND samples.data_id = objects.data_id
    AND objects.provenance = data_provenances.rowid
    '''

    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), 'Steps',
        'Duration (Seconds)', 'Device ID', 'Device Model')

    db_records = get_sqlite_db_records(data_source, query)

    for record in db_records:
        start_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        end_timestamp = convert_cocoa_core_data_ts_to_utc(record[1])
        hardware = context.lookup_metadata('apple_device_id_to_model', record[4])
        data_list.append((start_timestamp, end_timestamp, record[2], record[3],
                          record[4], hardware))

    return data_headers, data_list, data_source


@artifact_processor
def health_distance_walking_running(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    data_list = []

    query = '''
    SELECT
        samples.start_date,
        samples.end_date,
        quantity_samples.quantity,
        samples.end_date - samples.start_date,
        data_provenances.origin_product_type
    FROM samples
    JOIN quantity_samples ON quantity_samples.data_id = samples.data_id
    JOIN objects ON objects.data_id = samples.data_id
    JOIN data_provenances ON data_provenances.ROWID = objects.provenance
    WHERE samples.data_type = 8
    ORDER BY samples.start_date, samples.data_id
    '''

    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), 'Distance (Meters)',
        'Distance (Kilometers)', 'Distance (Miles)', 'Duration (Seconds)',
        'Device ID', 'Device Model')

    db_records = get_sqlite_db_records(data_source, query)

    for record in db_records:
        start_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        end_timestamp = convert_cocoa_core_data_ts_to_utc(record[1])
        meters = record[2]
        kilometers = round(meters / 1000, 3) if meters is not None else None
        miles = round(meters / 1609.344, 3) if meters is not None else None
        hardware = context.lookup_metadata('apple_device_id_to_model', record[4])
        data_list.append((start_timestamp, end_timestamp, meters, kilometers, miles,
                          record[3], record[4], hardware))

    return data_headers, data_list, data_source


@artifact_processor
def health_height(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    data_list = []

    query = '''
    SELECT
        samples.start_date AS "Height Value Timestamp",
        quantity_samples.quantity AS "Height (in Meters)",
        CAST((quantity_samples.quantity * 100) AS INT) AS "Height (in Centimeters)",
        replace(quantity_samples.quantity * '3.281', substr(
            (quantity_samples.quantity * '3.281'),2,8),"'" ||
        rtrim((substr((substr((quantity_samples.quantity * '3.281'),2,8) * '12'),1,2)), '.')
          || '"') AS "Height (Feet and Inches)"
    FROM samples
    LEFT OUTER JOIN quantity_samples ON samples.data_id = quantity_samples.data_id
    WHERE samples.data_type = '2'
    ORDER BY samples.start_date DESC
    '''

    data_headers = (
        ('Height Value Timestamp', 'datetime'), 'Height (in Meters)',
        'Height (in Centimeters)', 'Height (Feet and Inches)')

    db_records = get_sqlite_db_records(data_source, query)

    for record in db_records:
        height_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        data_list.append((height_timestamp, record[1], record[2], record[3]))

    return data_headers, data_list, data_source


@artifact_processor
def health_weight(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    data_list = []

    query = '''
    SELECT
        samples.start_date AS "Weight Value Timestamp",
        quantity_samples.quantity AS "Weight (in Kilograms)",
        CASE
            WHEN SUBSTR(CAST(ROUND(((quantity_samples.quantity / 6.35029317) -
                CAST(quantity_samples.quantity / 6.35029317 AS INT)) * 14) AS VARCHAR),
                1, INSTR(CAST(ROUND(((quantity_samples.quantity / 6.35029317) -
                CAST(quantity_samples.quantity / 6.35029317 AS INT)) * 14) AS VARCHAR),
                '.') - 1) = '14'
            THEN ((CAST(quantity_samples.quantity / 6.35029317 AS INT) + 1) || ' Stone 0 Pounds')
            ELSE ((CAST(quantity_samples.quantity / 6.35029317 AS INT) || ' Stone ' ||
                SUBSTR(CAST(ROUND(((quantity_samples.quantity / 6.35029317) -
                CAST(quantity_samples.quantity / 6.35029317 AS INT)) * 14) AS VARCHAR),
                1, INSTR(CAST(ROUND(((quantity_samples.quantity / 6.35029317) -
                CAST(quantity_samples.quantity / 6.35029317 AS INT)) * 14) AS VARCHAR), '.')
                - 1) || ' Pounds'))
            END AS "Weight (in Stones and Pounds)",
        ROUND(quantity_samples.quantity * 2.20462262, 2) AS "Weight (Approximate in Pounds)"
    FROM samples
    LEFT OUTER JOIN quantity_samples ON samples.data_id = quantity_samples.data_id
    WHERE samples.data_type = '3'
    ORDER BY samples.start_date DESC
    '''

    data_headers = (
        ('Weight Value Timestamp', 'datetime'), 'Weight (in Kilograms)',
        'Weight (in Stone)', 'Weight (Approximate in Pounds)')

    db_records = get_sqlite_db_records(data_source, query)

    for record in db_records:
        weight_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        data_list.append((weight_timestamp, record[1], record[2], record[3]))

    return data_headers, data_list, data_source


@artifact_processor
def health_watch_worn_data(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    data_list = []

    query = '''
    WITH TimeData AS (
        SELECT
            start_date AS "Start Time",
            end_date AS "End Time",
            LAG(start_date) OVER (ORDER BY start_date) AS "Prev Start Time",
            LAG(end_date) OVER (ORDER BY start_date) AS "Prev End Time"
        FROM samples
        WHERE data_type = "70"
    ),
    PeriodData AS (
        SELECT
            *,
            "Start Time" - "Prev End Time" AS "Gap in Seconds",
            CASE
                WHEN "Start Time" - "Prev End Time" > 3600 THEN 1
                ELSE 0
            END AS "New Period"
        FROM TimeData
    ),
    PeriodGroup AS (
        SELECT
            *,
            SUM("New Period") OVER
                (ORDER BY "Start Time" ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS "Period ID"
        FROM PeriodData
    ),
    Summary AS (
        SELECT
            "Period ID",
            MIN("Start Time") AS "Watch Worn Start Time",
            MAX("End Time") AS "Last Watch Worn Hour Time",
            (MAX("End Time") - MIN("Start Time")) / 3600.0 AS "Hours Worn"
        FROM PeriodGroup
        GROUP BY "Period ID"
    )
    SELECT
        s1."Watch Worn Start Time",
        s1."Hours Worn",
        s1."Last Watch Worn Hour Time",
        (s2."Watch Worn Start Time" - s1."Last Watch Worn Hour Time") / 3600.0
            AS "Hours Off Before Next Worn"
    FROM
        Summary s1
    LEFT JOIN
        Summary s2 ON s1."Period ID" + 1 = s2."Period ID"
    ORDER BY s1."Period ID";
    '''

    data_headers = (
        ('Watch Worn Start Time', 'datetime'), ('Last Watch Worn Hour Time', 'datetime'),
        'Hours Worn', 'Hours Off Before Next Worn Start')

    db_records = get_sqlite_db_records(data_source, query)

    for record in db_records:
        start_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        last_hour_time = convert_cocoa_core_data_ts_to_utc(record[2])
        data_list.append((start_timestamp, last_hour_time, record[1], record[3]))

    return data_headers, data_list, data_source


@artifact_processor
def health_all_watch_sleep_data(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    data_list = []

    query = '''
    SELECT
        SAMPLES.START_DATE,
        CASE
            WHEN category_samples.value IS 2 THEN "AWAKE"
            WHEN category_samples.value IS 3 THEN "CORE"
            WHEN category_samples.value IS 4 THEN "DEEP"
            WHEN category_samples.value IS 5 THEN "REM"
            ELSE CAST(category_samples.value AS TEXT)
        END,
        SAMPLES.END_DATE,
        STRFTIME('%H:%M:%S', (samples.end_date - samples.start_date), 'unixepoch')
    FROM samples
    LEFT OUTER JOIN category_samples ON samples.data_id = category_samples.data_id
    LEFT OUTER JOIN objects on samples.data_id = objects.data_id
    LEFT OUTER JOIN data_provenances on objects.provenance = data_provenances.ROWID
    WHERE samples.data_type IS 63 AND category_samples.value != 0 AND\
        category_samples.value != 1 AND data_provenances.origin_product_type like "%Watch%"
    ORDER BY category_samples.data_id;
    '''

    data_headers = (
        ('Sleep Start Time', 'datetime'), 'Sleep State',
        ('Sleep End Time', 'datetime'), 'Sleep State (HH:MM:SS)')

    db_records = get_sqlite_db_records(data_source, query)

    for record in db_records:
        start_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        end_timestamp = convert_cocoa_core_data_ts_to_utc(record[2])
        data_list.append((start_timestamp, record[1], end_timestamp, record[3]))

    return data_headers, data_list, data_source


@artifact_processor
def health_watch_by_sleep_period(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    data_list = []

    query = '''
    WITH lagged_samples AS (
        SELECT
            samples.start_date,
            samples.end_date,
            samples.data_id,
            samples.start_date AS start_time,
            samples.end_date AS end_time,
            (samples.end_date - samples.start_date) / 60 AS duration_minutes,
            samples.data_type,
            category_samples.value,
            LAG(samples.data_id) OVER (ORDER BY samples.data_id) AS prev_data_id,
            CASE
                WHEN category_samples.value = 2 THEN "AWAKE"
                WHEN category_samples.value = 3 THEN "CORE"
                WHEN category_samples.value = 4 THEN "DEEP"
                WHEN category_samples.value = 5 THEN "REM"
            END AS sleep_value
        FROM samples
        LEFT OUTER JOIN category_samples ON samples.data_id = category_samples.data_id
        LEFT OUTER JOIN objects on samples.data_id = objects.data_id
        LEFT OUTER JOIN data_provenances on objects.provenance = data_provenances.ROWID
        WHERE samples.data_type IS 63 AND category_samples.value != 0\
            AND category_samples.value != 1 AND data_provenances.origin_product_type like "%Watch%"
        ORDER BY category_samples.data_id
    ),
    grouped_samples AS (
        SELECT
            start_time,
            start_date,
            sleep_value,
            end_time,
            end_date,
            duration_minutes,
            data_type,
            value,
            CASE
                WHEN data_id - prev_data_id > 1 OR prev_data_id IS NULL THEN 1
                ELSE 0
            END AS is_new_group,
            SUM(CASE
                    WHEN data_id - prev_data_id > 1 OR prev_data_id IS NULL THEN 1
                    ELSE 0
                END) OVER (ORDER BY data_id) AS group_number
        FROM lagged_samples
    )
    SELECT
        MIN(start_time),
        MAX(end_time),
        MAX(end_time) - MIN(start_time),
        STRFTIME('%H:%M:%S',
            SUM(CASE WHEN sleep_value IN ('REM', 'CORE', 'DEEP')
            THEN duration_minutes * 60 ELSE 0 END), 'unixepoch'),
        STRFTIME('%H:%M:%S',
            SUM(CASE WHEN sleep_value = 'AWAKE' THEN duration_minutes * 60 ELSE 0 END), 'unixepoch'),
        STRFTIME('%H:%M:%S',
            SUM(CASE WHEN sleep_value = 'REM' THEN duration_minutes * 60 ELSE 0 END), 'unixepoch'),
        STRFTIME('%H:%M:%S',
            SUM(CASE WHEN sleep_value = 'CORE' THEN duration_minutes * 60 ELSE 0 END), 'unixepoch'),
        STRFTIME('%H:%M:%S',
            SUM(CASE WHEN sleep_value = 'DEEP' THEN duration_minutes * 60 ELSE 0 END), 'unixepoch'),
        ROUND(SUM(CASE WHEN sleep_value = 'AWAKE'
            THEN duration_minutes ELSE 0 END) * 100.0 / SUM(duration_minutes), 2),
        ROUND(SUM(CASE WHEN sleep_value = 'REM'
            THEN duration_minutes ELSE 0 END) * 100.0 / SUM(duration_minutes), 2),
        ROUND(SUM(CASE WHEN sleep_value = 'CORE'
            THEN duration_minutes ELSE 0 END) * 100.0 / SUM(duration_minutes), 2),
        ROUND(SUM(CASE WHEN sleep_value = 'DEEP'
            THEN duration_minutes ELSE 0 END) * 100.0 / SUM(duration_minutes), 2)
    FROM grouped_samples
    GROUP BY group_number;
    '''

    data_headers = (
        ('Sleep Start Time', 'datetime'), ('Sleep End Time', 'datetime'),
        'Time in Bed (seconds, period span)', 'Time Asleep (HH:MM:SS)', 'Awake Duration (HH:MM:SS)',
        'REM Duration (HH:MM:SS)', 'Core Duration (HH:MM:SS)',
        'Deep Duration (HH:MM:SS)', 'Awake %', 'REM %', 'Core %', 'Deep %')

    db_records = get_sqlite_db_records(data_source, query)

    for record in db_records:
        start_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        end_timestamp = convert_cocoa_core_data_ts_to_utc(record[1])
        data_list.append(
            (start_timestamp, end_timestamp, record[2], record[3], record[4], record[5],
             record[6], record[7], record[8], record[9], record[10], record[11]))

    return data_headers, data_list, data_source


@artifact_processor
def health_source_devices(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb.sqlite')
    data_list = []

    # https://theapplewiki.com/wiki/Bluetooth_PIDs
    bluetooth_pid = {
        "0x0034": "Apple Watch Series 5",
        "0x003b": "Apple Watch Series 9",
        "0x0040": "iPhone10,4",
        "0x0267": "Magic Keyboard (1st generation)",
        "0x2002": "AirPods (1st generation)",
        "0x200A": "AirPods Max",
        "0x200E": "AirPods Pro (1st generation)",
        "0x2013": "AirPods (3rd generation)",
        "0x2014": "AirPods Pro (2nd generation) (Lightning)",
        "0x2016": "Beats Studio Buds +",
        "0x201b": "AirPods 4 (ANC)",
        "0x2024": "AirPods Pro (2nd generation) (USB-C)",
    }

    sync_provenance_exists = does_column_exist_in_db(data_source, 'source_devices', 'sync_provenance')
    sync_identity_exists = does_column_exist_in_db(data_source, 'source_devices', 'sync_identity')

    select_columns = [
        'creation_date',
        'name',
        'manufacturer',
        'model',
        'hardware',
        'firmware',
        'software',
        'localIdentifier'
    ]

    if sync_provenance_exists:
        select_columns.append('sync_provenance')
    if sync_identity_exists:
        select_columns.append('sync_identity')

    query = f'''
    SELECT
        {', '.join(select_columns)}
    FROM source_devices
    WHERE name NOT LIKE '__NONE__' AND localIdentifier NOT LIKE '__NONE__'
    '''

    data_headers = [
        ('Creation Date', 'datetime'), 'Device Name', 'Manufacturer', 'Model (existing mapping)', 'model (as stored)',
        'Device ID', 'Device Model', 'Firmware', 'Software', 'Local ID'
    ]
    if sync_provenance_exists:
        data_headers.append('Sync Provenance')
    if sync_identity_exists:
        data_headers.append('Sync ID')

    column_positions = {col: idx for idx, col in enumerate(select_columns)}

    db_records = get_sqlite_db_records(data_source, query)

    for record in db_records:
        creation_date = convert_cocoa_core_data_ts_to_utc(record[column_positions['creation_date']])
        model_value = record[column_positions['model']]
        model = bluetooth_pid.get(model_value, model_value)
        hardware_value = record[column_positions['hardware']]
        device_model = context.lookup_metadata('apple_device_id_to_model', hardware_value)
        local_id = ''
        local_identifier = str(record[column_positions['localIdentifier']])
        if local_identifier.endswith('-tacl'):
            local_id = local_identifier[:-5]
        else:
            local_id = local_identifier

        row = [
            creation_date,
            record[column_positions['name']],
            record[column_positions['manufacturer']],
            model,
            model_value,
            hardware_value,
            device_model,
            record[column_positions['firmware']],
            record[column_positions['software']],
            local_id,
        ]

        if sync_provenance_exists:
            row.append(record[column_positions['sync_provenance']])
        if sync_identity_exists:
            row.append(record[column_positions['sync_identity']])

        data_list.append(tuple(row))

    return tuple(data_headers), data_list, data_source


@artifact_processor
def health_wrist_temperature(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    healthdb = context.get_source_file_path('healthdb.sqlite')

    data_list = []

    attach_query = attach_sqlite_db_readonly(healthdb, 'healthdb')

    query = '''
    WITH surface_temp AS (
        SELECT
            metadata_values.object_id,
            metadata_values.numerical_value
        FROM metadata_values
        JOIN metadata_keys ON metadata_values.key_id = metadata_keys.ROWID
        WHERE metadata_keys.key = '_HKPrivateMetadataKeySkinSurfaceTemperature'
    ),
    algorithm_version AS (
        SELECT
            metadata_values.object_id,
            metadata_values.numerical_value
        FROM metadata_values
        JOIN metadata_keys ON metadata_values.key_id = metadata_keys.ROWID
        WHERE metadata_keys.key = 'HKAlgorithmVersion'
    )
    SELECT
        samples.start_date AS "Start Time",
        samples.end_date AS "End Time",
        objects.creation_date AS "Date Added to Health",
        quantity_samples.quantity AS "Wrist Temperature (°C)",
        ((quantity_samples.quantity * 1.8) + 32) AS "Wrist Temperature (°F)",
        healthdb.sources.name AS "Source",
        algorithm_version.numerical_value AS "Algorithm Version",
        surface_temp.numerical_value AS "Surface Temperature (°C)",
        ((surface_temp.numerical_value * 1.8) + 32) AS "Surface Temperature (°F)",
        healthdb.source_devices.name AS "Name",
        healthdb.source_devices.manufacturer AS "Manufacturer",
        healthdb.source_devices.model AS "Model",
        healthdb.source_devices.hardware AS "Hardware Version",
        healthdb.source_devices.software AS "Software Version"
    FROM samples
    LEFT OUTER JOIN quantity_samples ON quantity_samples.data_id = samples.data_id
    LEFT OUTER JOIN objects ON samples.data_id = objects.data_id
    LEFT OUTER JOIN data_provenances ON objects.provenance = data_provenances.ROWID
    LEFT OUTER JOIN surface_temp ON surface_temp.object_id = samples.data_id
    LEFT OUTER JOIN algorithm_version ON algorithm_version.object_id = samples.data_id
    LEFT OUTER JOIN healthdb.sources ON healthdb.sources.ROWID = data_provenances.source_id
    LEFT OUTER JOIN healthdb.source_devices ON healthdb.source_devices.ROWID = data_provenances.device_id
    WHERE samples.data_type = 256
    '''

    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'),
        ('Date Added to Health', 'datetime'), 'Wrist Temperature (°C)',
        'Wrist Temperature (°F)', 'Source', 'Algorithm Version',
        'Surface Temperature (°C)', 'Surface Temperature (°F)', 'Name',
        'Manufacturer', 'Model', 'Hardware Version', 'Software Version')

    db_records = get_sqlite_db_records(data_source, query, attach_query)

    for record in db_records:
        start_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        end_timestamp = convert_cocoa_core_data_ts_to_utc(record[1])
        added_timestamp = convert_cocoa_core_data_ts_to_utc(record[2])
        data_list.append(
            (start_timestamp, end_timestamp, added_timestamp, record[3], record[4],
             record[5], record[6], record[7], record[8], record[9], record[10],
             record[11], record[12], record[13]))

    return data_headers, data_list, data_source
