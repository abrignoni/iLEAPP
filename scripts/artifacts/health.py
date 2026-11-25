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
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": "The Fahrenheit assumption for HKWeatherTemperature is inherited "
                 "from community queries and unverified. Activity type labels are the "
                 "member names of the HKWorkoutActivityType enumeration and Location Type "
                 "labels (2 Indoor, 3 Outdoor) those of HKWorkoutSessionLocationType, read "
                 "from HKWorkoutActivityType.h and HKWorkoutConfiguration.h in Apple's "
                 "macOS 27.0 SDK; any other stored value is shown as stored. The Goal Type "
                 "labels (0 Open, 1 Distance in meters, 2 Time in seconds, 3 Kilocalories) "
                 "are not in those public headers and their source is not established "
                 "here.",
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
        "description": "Provenance records of Health data: the source, device and operating system build "
                       "recorded for samples in healthdb_secure.sqlite, with the number of sample rows that "
                       "reference each one.",
        "author": "@KevinPagano3 - @Johann-PLW, @AlexisBrignoni, Claude",
        "creation_date": "2022-08-15",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": "The field meanings (except the model and OS version names looked up from stored "
                 "product types and builds) and method below were derived independently, using the "
                 "store's schema, measured data and Apple's code. One row per data_provenances row, with"
                 " source_id and device_id resolved in healthdb.sqlite (sources, logical_sources, "
                 "source_devices). First Sample Start, Last Sample End and Sample Rows cover samples "
                 "whose objects.type is 1, Deleted Sample Rows counts type 2, and Other Rows any other "
                 "type. First Sample Start is blank for a provenance with no type 1 sample. First Sample Start and Last Sample End are read as Cocoa seconds (from 2001-01-01 UTC), which rests on their range, and are shown in UTC. Device and the other device columns are as stored, including the literal __NONE__. A binary value in Device Local Identifier, Device UDI, Device Bluetooth Identifier, sync_provenance, derived_flags, sync_identity or Source Deleted would be shown as a UUID or as hex. None occurred on the corpus keys run. Origin OS Version (as stored) is the stored major, minor and patch. Origin "
                 "and Local Product Model and OS Version are names looked up from the stored product "
                 "type and build. The meaning of sync_provenance, derived_flags, sync_identity and "
                 "Source Deleted is not established, so they are shown as stored. Owner Bundle ID, "
                 "Device Firmware, Device UDI, Device Bluetooth Identifier, Contributor Apple ID and "
                 "Contributor Caller ID held no value on any row of the corpus keys run. When "
                 "healthdb_secure.sqlite is not a readable database, as on ctf2020_ios12, which sources "
                 "wrote samples is unknown, not empty: the rows are then the sources and devices "
                 "healthdb.sqlite registers, with Record Kind registered source or registered device and"
                 " their time in Source Modified or Device Created. These two times are read as Cocoa "
                 "seconds, which rests on their range only. Sources in healthdb.sqlite with no "
                 "provenance row are not listed when the secure database is readable. See also: Heather "
                 "Mahalik and Jared Barnhart, SANS DFIR Summit 2022, https://for585.com/dfirsummit22",
        "paths": ("*Health/healthdb_secure.sqlite*", "*Health/healthdb.sqlite*"),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "device-mobile",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 79 rows",
            "belkactf6_tar": "iOS 16.3 | 1 row",
            "cookbook_ios1751": "iOS 17.5.1 | 10 rows",
            "ctf2020_ios12": "iOS 12.4 | 4 rows (registered sources and devices only: healthdb_secure.sqlite is not a database)",
            "dexter_ios18": "iOS 18.3.2 | 55 rows",
            "felix23_ios16": "iOS 16.5 | 10 rows",
            "felix_ios17": "iOS 17.6.1 | 80 rows",
            "fsfull002_ios17": "iOS 17.1 | 17 rows",
            "hc_ios17_2": "iOS 17.2.1 | 2 rows",
            "hc_ios18_7": "iOS 18.7.8 | 8 rows",
            "hc_ios26": "iOS 26.5.2 | 20 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 2 rows",
            "hickman_ios13": "iOS 13.3.1 | 31 rows",
            "hickman_ios14": "iOS 14.3 | 54 rows",
            "hickman_ios15": "iOS 15.3.1 | 61 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 18 rows",
            "iphone11_ios17": "iOS 17.3 | 100 rows",
            "iphone12_ios18": "iOS 18.7 | 9 rows",
            "iphone14plus_ios18": "iOS 18.0 | 3 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 5 rows",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 5 rows",
            "otto_ios17": "iOS 17.5.1 | 144 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 145 rows",
        }
    },
    "health_headphone_audio_levels": {
        "name": "Health - Headphone Audio Levels",
        "description": "Headphone audio exposure samples (HealthKit type code 173) from "
                       "healthdb_secure.sqlite, with each series parent followed by the points SQLite holds "
                       "for it.",
        "author": "@KevinPagano3, @AlexisBrignoni, Claude",
        "creation_date": "2022-08-24",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": "The field meanings and method below were derived independently, using the store's "
                 "schema, measured data and Apple's code. One row per sample of type 173, the code of "
                 "HKQuantityTypeIdentifierHeadphoneAudioExposure in the _HKDataTypeDefinitions tables of"
                 " the iOS 13.3, 14.3 and 18.7 HealthKit builds read, plus one row per series point. A "
                 "series point repeats its parent's Record Added or Deleted, metadata, device and Source columns. Record Kind is sample, series parent, series point or deleted sample record."
                 " Any other objects.type is shown as its stored number, marked not established. None "
                 "occurred on the corpus keys run. objects.type 2 is a deleted sample record: the iOS "
                 "14.3 and 18.7 HealthDaemon builds create the index objects_deleted on objects.type = "
                 "2, and HealthDaemon has a deleted-object insert (HDDeletedObjectEntity). The index is "
                 "not in the 12.4 and 13.3 builds read. Type 1 rows are reported as samples, and every "
                 "one held a quantity row on the corpus keys run. No deleted sample record of this type "
                 "was present on the corpus keys run. On the corpus keys run no deleted sample record of any type held a quantity row, so a deleted record carries no value. A deleted sample record shows that a sample of this type existed. Record Added or Deleted "
                 "is then objects.creation_date, which the deleted-object insert writes. That this value"
                 " is the deletion date rests on the order of that method's arguments. It can have no "
                 "Start or End. On a type 1 row, Record Added or Deleted is objects.creation_date, and "
                 "whether that is the insert on this device or a value carried in by sync is not "
                 "established. The dBASPL unit is source-verified only: Apple's HKTypeIdentifiers.h "
                 "gives it for this type, and the corpus keys run held no stored original unit to "
                 "measure it against. A series parent's level matched the equivalent continuous level of"
                 " its points, within a relative 0.0001, on every parent with points in SQLite, so it is"
                 " not another reading. Series Point Status gives the points a parent declares against "
                 "those in SQLite. On hickman_ios13, hickman_ios14 and hickman_ios15 the declared points"
                 " are not in SQLite. healthdb_secure.hfd is not read, so only the parent row is "
                 "reported there. The iOS 18.7 HealthDaemon build has a migration of series data from "
                 "that store to SQLite. What the file holds was not read. series_location is shown as stored. On the corpus keys run 2 went with points in SQLite and 1 with points not in SQLite (hickman_ios15). The meaning of the values is not established. The column is absent on hickman_ios13 and hickman_ios14. "
                 "_HKPrivateMediaSourceBundleIdentifier (as stored) is that metadata value, and its "
                 "meaning is not established beyond the key name. Other Metadata holds any other key as "
                 "stored, including _HKPrivateMetadataKeyHeadphoneAudioDataIsTransient, whose meaning is not established. A binary metadata value is shown as its byte length. The statistics archives in "
                 "hearing_headphone_audio_exposure_statistics (healthdb.sqlite) are not read. Original "
                 "Value (as stored) and Original Unit (as stored) held no value on any row of the corpus"
                 " keys run. Start, End and Record Added or Deleted are read as Cocoa seconds (from 2001-01-01 UTC), which rests on their range, and are shown in UTC. Provenance ROWID is the Row ID of Health - Provenances, which holds the bundle ID. See also: Heather Mahalik and Jared Barnhart, SANS DFIR Summit 2022, "
                 "https://for585.com/dfirsummit22",
        "paths": ("*Health/healthdb_secure.sqlite*", "*Health/healthdb.sqlite*"),
        "output_types": "standard",
        "artifact_icon": "headphones",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 595 rows",
            "belkactf6_tar": "iOS 16.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows (unknown, not empty: healthdb_secure.sqlite is not a database)",
            "dexter_ios18": "iOS 18.3.2 | 7256 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 8 rows",
            "hickman_ios14": "iOS 14.3 | 13 rows",
            "hickman_ios15": "iOS 15.3.1 | 20 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 930 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 643 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 4484 rows",
        }
    },
    "health_heart_rate": {
        "name": "Health - Heart Rate",
        "description": "Heart rate samples (HealthKit type code 5) from healthdb_secure.sqlite, with each "
                       "series parent followed by the points SQLite holds for it, and the stored heart rate "
                       "context.",
        "author": "@KevinPagano3 - @Johann-PLW, @AlexisBrignoni, Codex, Claude",
        "creation_date": "2023-03-06",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": "The field meanings (except the model names looked up from stored hardware identifiers)"
                 " and method below were derived independently, using the store's schema, measured data "
                 "and Apple's code. One row per sample of type 5, the code of "
                 "HKQuantityTypeIdentifierHeartRate in the _HKDataTypeDefinitions tables of the iOS 13.3, 14.3 and 18.7 HealthKit builds read, plus one row per series point. A series point "
                 "repeats its parent's Record Added or Deleted, context, device and source columns. "
                 "Record Kind is sample, series parent, series point or deleted sample record. Any other"
                 " objects.type is shown as its stored number, marked not established. None occurred on "
                 "the corpus keys run. objects.type 2 is a deleted sample record: the iOS 14.3 and 18.7 "
                 "HealthDaemon builds create the index objects_deleted on objects.type = 2, and "
                 "HealthDaemon has a deleted-object insert (HDDeletedObjectEntity). The index is not in "
                 "the 12.4 and 13.3 builds read. Type 1 rows are reported as samples, and every one held"
                 " a quantity row on the corpus keys run. No deleted sample record held a quantity row "
                 "on those keys, so no value survives. It shows that a sample of this type existed. "
                 "Record Added or Deleted is then objects.creation_date, which the deleted-object insert"
                 " writes. That this value is the deletion date rests on the order of that method's "
                 "arguments. It can have no Start or End. On a type 1 row, Record Added or Deleted is "
                 "objects.creation_date, and whether that is the insert on this device or a value "
                 "carried in by sync is not established. The stored value is in count/s: on every row "
                 "with a stored original unit, that unit is count/min and the stored value is the "
                 "original divided by 60, to 6 places. Heart Rate (BPM) is the stored value times 60, "
                 "rounded to 3 places. How a series parent's value relates to its points is not "
                 "established. Series Point Status gives the points a parent declares against those in "
                 "SQLite. On hickman_ios14 and hickman_ios15 the declared points are not in SQLite. "
                 "healthdb_secure.hfd is not read, so only the parent row is reported there. The iOS "
                 "18.7 HealthDaemon build has a migration of series data from that store to SQLite. What"
                 " the file holds was not read. series_location is shown as stored. On the corpus keys run 2 went with points in SQLite and 1 with points not in SQLite (hickman_ios15). The meaning of the values is not established. The column is absent on hickman_ios13 and hickman_ios14. Heart Rate Context Value is "
                 "the stored number of the _HKPrivateHeartRateContext metadata key. Heart Rate Context "
                 "is the string HealthKit's _NSStringFromPrivateHeartRateContext returns for codes 0 to "
                 "9, read statically from the iOS 12.4, 13.3, 14.3 and 18.7 builds, where all four "
                 "agree. That this function describes the stored metadata value rests on the shared "
                 "name. No watchOS build was read. The tables of iOS 15, 16, 17 and 26 were not read. "
                 "Code 10 is Scandium on 14.3 and Oxygen Saturation on 18.7, and code 11 is Sedentary "
                 "while Sleep Mode is enabled on 18.7 and absent from the older builds, so both show as "
                 "not established with the stored number kept. Device Name is as stored, including the "
                 "literal __NONE__. Model Name is looked up from Hardware. Other Metadata (as stored) "
                 "held no value on any row of the corpus keys run. Start, End and Record Added or Deleted are read as Cocoa seconds (from 2001-01-01 UTC), which rests on their range, and are shown in UTC. Provenance ROWID is the Row ID of Health - Provenances, which holds the bundle ID. See also: Heather Mahalik and Jared "
                 "Barnhart, SANS DFIR Summit 2022, https://for585.com/dfirsummit22",
        "paths": ("*Health/healthdb_secure.sqlite*", "*Health/healthdb.sqlite*"),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 0 rows",
            "belkactf6_tar": "iOS 16.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 155 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows (unknown, not empty: healthdb_secure.sqlite is not a database)",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 3651 rows",
            "hickman_ios14": "iOS 14.3 | 24999 rows",
            "hickman_ios15": "iOS 15.3.1 | 23485 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 39176 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 8816 rows",
        }
    },
    "health_resting_heart_rate": {
        "name": "Health - Resting Heart Rate",
        "description": "Resting heart rate samples (HealthKit type code 118) from healthdb_secure.sqlite, "
                       "including deleted sample records.",
        "author": "@KevinPagano3 - @Johann-PLW, @AlexisBrignoni, Claude",
        "creation_date": "2023-03-06",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": "The field meanings (except the model names looked up from stored product types) and "
                 "method below were derived independently, using the store's schema, measured data and "
                 "Apple's code. One row per sample of type 118, the code of "
                 "HKQuantityTypeIdentifierRestingHeartRate in the _HKDataTypeDefinitions tables of the iOS 13.3, 14.3 and 18.7 HealthKit builds read. Record Kind is sample or deleted sample "
                 "record on the corpus keys run. A series parent or series point would be labelled as "
                 "such, and any other objects.type is shown as its stored number, marked not "
                 "established. objects.type 2 is a deleted sample record: the iOS 14.3 and 18.7 "
                 "HealthDaemon builds create the index objects_deleted on objects.type = 2, and "
                 "HealthDaemon has a deleted-object insert (HDDeletedObjectEntity). The index is not in "
                 "the 12.4 and 13.3 builds read. Type 1 rows are reported as samples, and every one held"
                 " a quantity row on the corpus keys run. No deleted sample record held a quantity row "
                 "on those keys, so no value survives. It shows that a sample of this type existed. "
                 "Record Added or Deleted is then objects.creation_date, which the deleted-object insert"
                 " writes. That this value is the deletion date rests on the order of that method's "
                 "arguments. It can have no Start or End. On a type 1 row, Record Added or Deleted is "
                 "objects.creation_date, and whether that is the insert on this device or a value "
                 "carried in by sync is not established. The stored value is in count/min (beats per "
                 "minute): on every row with a stored original unit, that unit is count/s and the stored"
                 " value is the original times 60. Source Product Type is sources.product_type, and "
                 "Model Name is looked up from it. Device Name is as stored, and it held the literal __NONE__ on every row of the corpus keys run. Metadata is shown as stored, and the meaning of its keys is not established. A binary metadata value is shown as its byte length. Series Point Status held no value on any row of the corpus "
                 "keys run. Start, End and Record Added or Deleted are read as Cocoa seconds (from 2001-01-01 UTC), which rests on their range, and are shown in UTC. Provenance ROWID is the Row ID of Health - Provenances, which holds the bundle ID. See also: Heather Mahalik and Jared Barnhart, SANS DFIR Summit 2022, "
                 "https://for585.com/dfirsummit22",
        "paths": ("*Health/healthdb_secure.sqlite*", "*Health/healthdb.sqlite*"),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 0 rows",
            "belkactf6_tar": "iOS 16.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 2 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows (unknown, not empty: healthdb_secure.sqlite is not a database)",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 94 rows",
            "hickman_ios14": "iOS 14.3 | 449 rows",
            "hickman_ios15": "iOS 15.3.1 | 76 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 125 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 46 rows",
        }
    },
    "health_achievements": {
        "name": "Health - Achievements",
        "description": "Earned achievement records from ACHAchievementsPlugin_earned_instances in "
                       "healthdb_secure.sqlite, with the source name of the matching template.",
        "author": "@KevinPagano3, @AlexisBrignoni, Claude",
        "creation_date": "2022-08-24",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": "The field meanings and method below were derived independently, using the store's "
                 "schema, measured data and Apple's code. One row per earned instance, joined to "
                 "ACHAchievementsPlugin_templates on the template's unique name. Earned Date is a "
                 "calendar date stored as text and is not converted, because it is not an instant. "
                 "Created Timestamp is read as Cocoa seconds, which rests on its range. It is stored as a number, or as numeric text on "
                 "wilkerson_iphone16_ios26, the one key with rows whose schema declares the column TEXT."
                 " A value that is neither is left unconverted by this artifact. Value and Unit are "
                 "value_in_canonical_unit and value_canonical_unit as stored. Template In Store says "
                 "whether the template row exists. The meaning of Creator Device, sync_provenance and "
                 "sync_identity is not established, so they are shown as stored. A binary value in these three columns would be shown as a UUID or as hex. None occurred on the corpus keys run. The template catalog "
                 "and fitness_friend_achievements are not reported, and achievement badge files in app "
                 "containers are not read. See also: Heather Mahalik and Jared Barnhart, SANS DFIR "
                 "Summit 2022, https://for585.com/dfirsummit22",
        "paths": ("*Health/healthdb_secure.sqlite*",),
        "output_types": "standard",
        "artifact_icon": "star",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 19 rows",
            "belkactf6_tar": "iOS 16.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows (unknown, not empty: healthdb_secure.sqlite is not a database)",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 8 rows",
            "hickman_ios14": "iOS 14.3 | 30 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 38 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 22 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 5 rows",
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
        "category": "Health & Fitness",
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
    "health_flights_climbed": {
        "name": "Health - Flights Climbed",
        "description": "Flights climbed samples from the samples table of healthdb_secure.sqlite, "
                       "with start and end, flights climbed, duration and the origin product type "
                       "recorded in the sample's provenance and the model it maps to.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-13",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": "The type code, unit and joins were derived independently from the store's schema, "
                 "measured data and Apple's HealthKit and HealthDaemon code, and agree with this "
                 "query, which follows this module's Health - Steps query with data_type 12. Reads "
                 "samples whose data_type is 12 and that have a row in quantity_samples, an objects "
                 "row and a data_provenances record. HealthKit names code 12 "
                 "HKQuantityTypeIdentifierFlightsClimbed. The name was returned by HealthKit on macOS "
                 "27.2.1 (26B131) and read from the HealthKit type table of one build each of iOS 13, "
                 "14, 15 and 18. The canonical unit, count, was returned by HealthKit on macOS 27.2.1 "
                 "only. The table was not read for iOS 16, 17 or 26. On the 23 tested images with a "
                 "readable database, no type 12 sample stores an original unit (0 of 5,182 rows), so "
                 "the unit was not checked against stored data. On the 13 images in sample_data with a readable database (3,577 rows) the stored quantity ranged from "
                 "0.79364 to 56 and was never negative; 9 rows, all on iphone11_ios17, hold a "
                 "non-integer value. On the 11 tested images that have the shared_summaries table, "
                 "every summary whose name contains HKQuantityTypeIdentifierFlightsClimbed is linked "
                 "in shared_summary_object_types to object_type 12, and no other summary is; "
                 "hickman_ios13 and hickman_ios14 do not have these tables. Flights Climbed is "
                 "reported as stored. Device ID is the origin product type from data_provenances and "
                 "Device Model is the model it maps to; rows with different origin product types can "
                 "cover the same time, which occurs on hickman_ios13, hickman_ios14, magnet_ios16 "
                 "and iphone11_ios17. A sample needs a quantity_samples row, an objects row and a "
                 "data_provenances record to be reported: 7 samples on hickman_ios13 and 7 on "
                 "hickman_ios14 have no quantity_samples row and are not reported, none on the other "
                 "tested images. On ctf2020_ios12 healthdb_secure.sqlite is an 8-byte file that is "
                 "not a database.",
        "paths": ("*Health/healthdb_secure.sqlite*",),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 241 rows",
            "hickman_ios14": "iOS 14.3 | 824 rows",
            "jess_ios15": "iOS 15.0.2 | 20 rows",
            "magnet_ios16": "iOS 16.1.1 | 34 rows",
            "abe_ios16": "iOS 16.5 | 251 rows",
            "felix23_ios16": "iOS 16.5 | 9 rows",
            "otto_ios17": "iOS 17.5.1 | 226 rows",
            "felix_ios17": "iOS 17.6.1 | 46 rows",
            "fsfull002_ios17": "iOS 17.1 | 71 rows",
            "iphone11_ios17": "iOS 17.3 | 1610 rows",
            "dexter_ios18": "iOS 18.3.2 | 231 rows",
            "hc_ios18_7": "iOS 18.7.8 | 12 rows",
            "iphone14plus_ios18": "iOS 18.0 | 2 rows",
        }
    },
    "health_distance_walking_running": {
        "name": "Health - Walking + Running Distance",
        "description": "Walking and running distance samples from the samples table of "
                       "healthdb_secure.sqlite, with start and end, distance in meters, "
                       "kilometers and miles, duration and the writing device's id and model.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-25",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": "The type code, unit and joins were derived independently from the store's schema, "
                 "measured data and Apple's HealthKit and HealthDaemon code, and agree with this "
                 "query. Reads samples whose data_type is 8 and that have a row in quantity_samples "
                 "and a data_provenances record. HealthKit names code 8 "
                 "HKQuantityTypeIdentifierDistanceWalkingRunning. The name was returned by HealthKit "
                 "on macOS 27.2.1 (26B131) and read from the HealthKit type table of one build each "
                 "of iOS 13, 14, 15 and 18. The canonical unit, m, was returned by HealthKit on macOS "
                 "27.2.1 only. The table was not read for iOS 16, 17 or 26. "
                 "The Health database also names this type itself: on 17 of the tested images, "
                 "the chart records in its shared_summaries table pair "
                 "HKQuantityTypeIdentifierDistanceWalkingRunning with data type 8 and "
                 "HKQuantityTypeIdentifierStepCount with data type 7. The stored quantity is in meters: on 205 of the 226 chart "
                 "buckets those records store in meters, the type 8 samples in the bucket "
                 "add up to its total, and the 10 samples on each of hickman_ios13, "
                 "hickman_ios14 and iphone11_ios17 that recorded an original unit carried km "
                 "and stored exactly 1,000 times the original value. Distance (Kilometers) "
                 "and Distance (Miles) are computed from the meters value. "
                 "Samples with no quantity_samples row are not reported: 3,293 on "
                 "hickman_ios14, 12 on hickman_ios13 and 31 on wilkerson_iphone16_ios26, none on "
                 "the other 20 tested images with a readable database. "
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
        "category": "Health & Fitness",
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
        "category": "Health & Fitness",
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
        "category": "Health & Fitness",
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
        'category': 'Health & Fitness',
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
        "category": "Health & Fitness",
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
        "category": "Health & Fitness",
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
        "category": "Health & Fitness",
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

import math
import sqlite3
import uuid

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, \
    attach_sqlite_db_readonly, does_table_exist_in_db, convert_cocoa_core_data_ts_to_utc, \
    does_column_exist_in_db, logfunc, open_sqlite_db_readonly


def _record_value(record, index, default=None):
    return record[index] if index < len(record) else default


_HEALTH_SQLITE_MAGIC = b'SQLite format 3\x00'
_HEALTH_RECORD_KINDS = {1: 'sample', 2: 'deleted sample record'}
_HEART_RATE_CONTEXT_KEY = '_HKPrivateHeartRateContext'
_HEADPHONE_MEDIA_KEY = '_HKPrivateMediaSourceBundleIdentifier'
# The strings HealthKit's _NSStringFromPrivateHeartRateContext returns. Codes 0 to 9 are the
# same in the iOS 12.4, 13.3, 14.3 and 18.7 builds. Code 10 differs between them and code 11
# is only in 18.7, so neither is named here.
_HEART_RATE_CONTEXT_NAMES = {
    0: 'Not Set', 1: 'Background', 2: 'Streaming PPG', 3: 'Sedentary', 4: 'Walking',
    5: 'Breathe', 6: 'Workout', 7: 'Wheelchair Motion', 8: 'Background Tachogram',
    9: 'Streaming ECG'}
_HEALTH_PARENT_NOTES = {
    173: 'On the corpus keys run this level equalled the equivalent continuous level of its '
         'points.',
    5: 'As stored. How it relates to the points is not established.'}
_HEALTH_HFD_NOT_READ = 'healthdb_secure.hfd is not read by this artifact.'


def _health_is_sqlite(path):
    """True when the file starts with the SQLite header."""
    if not path:
        return False
    try:
        with open(path, 'rb') as handle:
            return handle.read(16) == _HEALTH_SQLITE_MAGIC
    except OSError:
        return False


def _health_open(data_source, healthdb):
    """Open healthdb_secure.sqlite read-only and attach healthdb.sqlite as h when it is readable."""
    if not _health_is_sqlite(data_source):
        return None, False
    con = open_sqlite_db_readonly(data_source)
    if con is None:
        return None, False
    attached = False
    if _health_is_sqlite(healthdb):
        try:
            con.execute(attach_sqlite_db_readonly(healthdb, 'h'))
            attached = True
        except sqlite3.Error as ex:
            logfunc(f'Could not attach healthdb.sqlite: {ex}')
    return con, attached


def _health_has_table(con, table, schema='main'):
    query = f'SELECT 1 FROM "{schema}".sqlite_master WHERE type = \'table\' AND name = ?'
    return con.execute(query, (table,)).fetchone() is not None


def _health_columns(con, table, schema='main'):
    return [row[1] for row in con.execute(f'PRAGMA "{schema}".table_info("{table}")')]


def _health_field(columns, name, alias):
    return f'{alias}."{name}"' if name in columns else 'NULL'


def _health_cell(value):
    """A value for a report cell: a 16-byte blob as a UUID, other blobs as hex."""
    if isinstance(value, (bytes, memoryview)):
        raw = bytes(value)
        return str(uuid.UUID(bytes=raw)) if len(raw) == 16 else raw.hex()
    return value


def _health_ts(value):
    """Cocoa seconds, as a number or numeric text, to UTC. Anything else is returned as stored."""
    if value is None or value == '':
        return value
    try:
        seconds = float(value)
        if not math.isfinite(seconds):
            return value
        return convert_cocoa_core_data_ts_to_utc(seconds)
    except (TypeError, ValueError, OverflowError, OSError):
        return value


def _health_stored_os(row):
    parts = [row.get(name) for name in (
        'origin_major_version', 'origin_minor_version', 'origin_patch_version')]
    return '.'.join(str(part) for part in parts) if all(p is not None for p in parts) else ''


def _health_os_version(context, build, product_type):
    """The OS version name for a build, blank when the product type is NULL."""
    if product_type is None:
        return ''
    return context.get_apple_os_version(build, product_type)


def _health_provenance(con, attached):
    """data_provenances rows by ROWID, with their sources and devices from healthdb.sqlite."""
    if not _health_has_table(con, 'data_provenances'):
        return {}
    columns = _health_columns(con, 'data_provenances')
    select = {name: _health_field(columns, name, 'p') for name in (
        'origin_product_type', 'origin_build', 'local_product_type', 'local_build', 'source_id',
        'device_id', 'contributor_id', 'source_version', 'tz_name', 'origin_major_version',
        'origin_minor_version', 'origin_patch_version', 'sync_provenance', 'sync_identity',
        'derived_flags')}
    joins = []
    if attached and _health_has_table(con, 'sources', 'h'):
        source_columns = _health_columns(con, 'sources', 'h')
        select['source_name'] = _health_field(source_columns, 'name', 's')
        select['source_product_type'] = _health_field(source_columns, 'product_type', 's')
        select['source_deleted'] = _health_field(source_columns, 'deleted', 's')
        joins.append('LEFT JOIN h.sources s ON s.ROWID = p.source_id')
        if 'bundle_id' in source_columns:
            select['bundle_id'] = 's."bundle_id"'
            select['owner_bundle_id'] = _health_field(source_columns, 'owner_bundle_id', 's')
        elif 'logical_source_id' in source_columns and _health_has_table(con, 'logical_sources', 'h'):
            logical_columns = _health_columns(con, 'logical_sources', 'h')
            select['bundle_id'] = _health_field(logical_columns, 'bundle_id', 'l')
            select['owner_bundle_id'] = _health_field(logical_columns, 'owner_bundle_id', 'l')
            joins.append('LEFT JOIN h.logical_sources l ON l.ROWID = s.logical_source_id')
    if attached and _health_has_table(con, 'source_devices', 'h'):
        device_columns = _health_columns(con, 'source_devices', 'h')
        for name, column in (
                ('device_name', 'name'), ('device_manufacturer', 'manufacturer'),
                ('device_model', 'model'), ('device_hardware', 'hardware'),
                ('device_firmware', 'firmware'), ('device_software', 'software'),
                ('device_local_identifier', 'localIdentifier'), ('device_udi', 'FDAUDI'),
                ('device_bluetooth_identifier', 'bluetooth_identifier')):
            select[name] = _health_field(device_columns, column, 'd')
        joins.append('LEFT JOIN h.source_devices d ON d.ROWID = p.device_id')
    if 'contributor_id' in columns and _health_has_table(con, 'contributors'):
        contributor_columns = _health_columns(con, 'contributors')
        select['contributor_apple_id'] = _health_field(contributor_columns, 'apple_id', 'c')
        select['contributor_caller_id'] = _health_field(contributor_columns, 'caller_id', 'c')
        joins.append('LEFT JOIN contributors c ON c.ROWID = p.contributor_id')
    names = list(select)
    fields = ', '.join(f'{select[name]} AS "{name}"' for name in names)
    query = f'SELECT p.ROWID, {fields} FROM data_provenances p {" ".join(joins)}'
    return {row[0]: dict(zip(names, row[1:])) for row in con.execute(query)}


def _health_provenance_counts(con):
    """Sample rows per provenance by objects.type, and the time span of the type 1 rows."""
    counts = {}
    if not (_health_has_table(con, 'samples') and _health_has_table(con, 'objects')):
        return counts
    query = '''
    SELECT o.provenance, o.type, COUNT(*), MIN(s.start_date), MAX(s.end_date)
    FROM samples s JOIN objects o ON o.data_id = s.data_id
    GROUP BY o.provenance, o.type
    '''
    for provenance, kind, number, first, last in con.execute(query):
        entry = counts.setdefault(provenance, {'sample': 0, 'deleted': 0, 'other': 0})
        entry['sample' if kind == 1 else 'deleted' if kind == 2 else 'other'] += number
        if kind == 1:
            entry['first'] = first
            entry['last'] = last
    return counts


def _health_registered_rows(healthdb, width):
    """Sources and devices healthdb.sqlite registers, for when the secure database is unreadable."""
    rows = []
    if not _health_is_sqlite(healthdb):
        return rows
    con = open_sqlite_db_readonly(healthdb)
    if con is None:
        return rows
    # Positions in the health_provenances headers.
    when, kind, name, bundle, owner, product = 2, 3, 4, 5, 6, 7
    device_first, deleted, source_at, device_at = 10, 36, 38, 39
    try:
        if _health_has_table(con, 'sources'):
            columns = _health_columns(con, 'sources')
            join = ''
            bundle_field = _health_field(columns, 'bundle_id', 's')
            owner_field = _health_field(columns, 'owner_bundle_id', 's')
            if 'bundle_id' not in columns and 'logical_source_id' in columns \
                    and _health_has_table(con, 'logical_sources'):
                logical = _health_columns(con, 'logical_sources')
                bundle_field = _health_field(logical, 'bundle_id', 'l')
                owner_field = _health_field(logical, 'owner_bundle_id', 'l')
                join = 'LEFT JOIN logical_sources l ON l.ROWID = s.logical_source_id'
            query = f'''
            SELECT {_health_field(columns, 'mod_date', 's')}, {_health_field(columns, 'name', 's')},
                {bundle_field}, {owner_field}, {_health_field(columns, 'product_type', 's')},
                {_health_field(columns, 'deleted', 's')}, s.ROWID
            FROM sources s {join} ORDER BY s.ROWID
            '''
            for mod, source, bid, obid, ptype, gone, rowid in con.execute(query):
                row = [''] * width
                row[when], row[kind], row[name] = _health_ts(mod), 'registered source', source
                row[bundle], row[owner], row[product] = bid, obid, ptype
                row[deleted], row[source_at] = _health_cell(gone), rowid
                rows.append(tuple(row))
        if _health_has_table(con, 'source_devices'):
            columns = _health_columns(con, 'source_devices')
            fields = ', '.join(_health_field(columns, column, 'd') for column in (
                'creation_date', 'name', 'manufacturer', 'model', 'hardware', 'firmware',
                'software', 'localIdentifier', 'FDAUDI', 'bluetooth_identifier'))
            for values in con.execute(f'SELECT {fields}, d.ROWID FROM source_devices d ORDER BY d.ROWID'):
                row = [''] * width
                row[when], row[kind] = _health_ts(values[0]), 'registered device'
                row[device_first - 1] = values[1]
                for offset, value in enumerate(values[2:10]):
                    row[device_first + offset] = _health_cell(value)
                row[device_at] = values[10]
                rows.append(tuple(row))
    except sqlite3.Error as ex:
        logfunc(f'Error reading healthdb.sqlite: {ex}')
    finally:
        con.close()
    return rows


def _health_metadata(con, data_type):
    """Metadata of one data type: {data_id: [(key, value shown, numerical_value)]}."""
    metadata = {}
    if not (_health_has_table(con, 'metadata_values') and _health_has_table(con, 'metadata_keys')):
        return metadata
    columns = _health_columns(con, 'metadata_values')
    query = f'''
    SELECT v.object_id, k.key, {_health_field(columns, 'string_value', 'v')},
        {_health_field(columns, 'numerical_value', 'v')},
        {_health_field(columns, 'date_value', 'v')}, {_health_field(columns, 'data_value', 'v')}
    FROM metadata_values v
    JOIN metadata_keys k ON k.ROWID = v.key_id
    JOIN samples s ON s.data_id = v.object_id
    WHERE s.data_type = ?
    ORDER BY v.object_id, k.key
    '''
    for object_id, key, text, number, date, blob in con.execute(query, (data_type,)):
        if text is not None:
            shown = text
        elif number is not None:
            shown = number
        elif date is not None:
            shown = date
        elif blob is not None:
            shown = f'<blob {len(bytes(blob))} bytes>'
        else:
            shown = ''
        metadata.setdefault(object_id, []).append((key, shown, number))
    return metadata


def _health_split_metadata(metadata, key):
    """Split metadata into the values of one key and the rest."""
    wanted = [item for item in metadata if item[0] == key]
    return wanted, [item for item in metadata if item[0] != key]


def _health_metadata_text(metadata):
    return '; '.join(f'{key}={shown}' for key, shown, _number in metadata)


def _health_context_cells(contexts):
    """Apple's name and the stored value of a sample's distinct heart rate context values."""
    values = []
    for _key, shown, number in contexts:
        value = number if number is not None else shown
        if value not in values:
            values.append(value)
    if not values:
        return '', ''
    names = []
    for value in values:
        code = int(value) if isinstance(value, (int, float)) and float(value).is_integer() else None
        names.append(_HEART_RATE_CONTEXT_NAMES.get(code, 'not established'))
    stored = values[0] if len(values) == 1 else '; '.join(str(value) for value in values)
    return '; '.join(names), stored


def _health_sample_records(con, data_type):
    """Every sample of a type, each series parent followed by the points SQLite holds for it."""
    if not (_health_has_table(con, 'samples') and _health_has_table(con, 'objects')):
        return
    metadata = _health_metadata(con, data_type)
    object_columns = _health_columns(con, 'objects')
    quantity_columns = _health_columns(con, 'quantity_samples') \
        if _health_has_table(con, 'quantity_samples') else []
    series_columns = _health_columns(con, 'quantity_sample_series') \
        if _health_has_table(con, 'quantity_sample_series') else []
    statistic_columns = _health_columns(con, 'quantity_sample_statistics') \
        if _health_has_table(con, 'quantity_sample_statistics') else []
    has_units = 'original_unit' in quantity_columns and _health_has_table(con, 'unit_strings')
    joins = ['LEFT JOIN objects o ON o.data_id = s.data_id']
    if quantity_columns:
        joins.append('LEFT JOIN quantity_samples q ON q.data_id = s.data_id')
    if has_units:
        joins.append('LEFT JOIN unit_strings u ON u.ROWID = q.original_unit')
    if statistic_columns:
        joins.append('LEFT JOIN quantity_sample_statistics st ON st.owner_id = s.data_id')
    if series_columns:
        joins.append('LEFT JOIN quantity_sample_series ser ON ser.data_id = s.data_id')
    query = f'''
    SELECT s.data_id, o.type, s.start_date, s.end_date,
        {_health_field(object_columns, 'creation_date', 'o')},
        {_health_field(object_columns, 'uuid', 'o')},
        {_health_field(object_columns, 'provenance', 'o')},
        {_health_field(quantity_columns, 'quantity', 'q')},
        {_health_field(quantity_columns, 'original_quantity', 'q')},
        {'u.unit_string' if has_units else 'NULL'},
        {_health_field(statistic_columns, 'min', 'st')},
        {_health_field(statistic_columns, 'max', 'st')},
        {_health_field(series_columns, 'count', 'ser')},
        {_health_field(series_columns, 'hfd_key', 'ser')},
        {_health_field(series_columns, 'series_location', 'ser')}
    FROM samples s {' '.join(joins)}
    WHERE s.data_type = ?
    ORDER BY s.start_date IS NULL, s.start_date, s.data_id
    '''
    point_columns = _health_columns(con, 'quantity_series_data') \
        if _health_has_table(con, 'quantity_series_data') else []
    point_query = f'''
    SELECT timestamp, value, {_health_field(point_columns, 'duration', 'p')}
    FROM quantity_series_data p WHERE series_identifier = ? ORDER BY timestamp
    '''
    point_cursor = con.cursor()
    for row in con.cursor().execute(query, (data_type,)):
        data_id, object_type, start, end, created, object_uuid, provenance, quantity, \
            original_quantity, original_unit, series_min, series_max, declared, series_key, \
            location = row
        kind = _HEALTH_RECORD_KINDS.get(object_type,
                                        f'objects.type {object_type} (meaning not established)')
        points, status, shown_declared, points_read = [], '', '', ''
        if series_key is not None:
            if object_type == 1:
                kind = 'series parent'
            if point_columns:
                points = point_cursor.execute(point_query, (series_key,)).fetchall()
            shown_declared, points_read = declared, len(points)
            missing = (declared or 0) - len(points)
            if not points and declared:
                status = f'{declared} points not in SQLite. {_HEALTH_HFD_NOT_READ}'
            elif missing:
                status = f'{len(points)} of {declared} declared points in SQLite. ' \
                         f'{_HEALTH_HFD_NOT_READ}'
            else:
                status = 'all declared points in SQLite'
        record = {
            'data_id': data_id, 'kind': kind, 'start': start, 'end': end, 'created': created,
            'uuid': object_uuid, 'provenance': provenance, 'quantity': quantity,
            'original_quantity': original_quantity, 'original_unit': original_unit,
            'series_min': series_min, 'series_max': series_max, 'declared': shown_declared,
            'points_read': points_read, 'status': status, 'series_location': location,
            'metadata': metadata.get(data_id, [])}
        yield record
        for timestamp, value, duration in points:
            point_end = timestamp + duration if isinstance(duration, (int, float)) else ''
            yield {**record, 'kind': 'series point', 'start': timestamp, 'end': point_end,
                   'quantity': value, 'original_quantity': None, 'original_unit': None,
                   'series_min': None, 'series_max': None, 'declared': '', 'points_read': '',
                   'status': '', 'series_location': None}


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
        WHEN 14 THEN "DANCE"
        WHEN 15 THEN "DANCE INSPIRED TRAINING"
        WHEN 16 THEN "ELLIPTICAL"
        WHEN 17 THEN "EQUESTRIAN SPORTS"
        WHEN 18 THEN "FENCING"
        WHEN 19 THEN "FISHING"
        WHEN 20 THEN "FUNCTIONAL STRENGTH TRAINING"
        WHEN 21 THEN "GOLF"
        WHEN 22 THEN "GYMNASTICS"
        WHEN 23 THEN "HANDBALL"
        WHEN 24 THEN "HIKING"
        WHEN 25 THEN "HOCKEY"
        WHEN 26 THEN "HUNTING"
        WHEN 27 THEN "LACROSSE"
        WHEN 28 THEN "MARTIAL ARTS"
        WHEN 29 THEN "MIND AND BODY"
        WHEN 30 THEN "MIXED METABOLIC CARDIO TRAINING"
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
        WHEN 44 THEN "STAIR CLIMBING"
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
        WHEN 77 THEN "CARDIO DANCE"
        WHEN 78 THEN "SOCIAL DANCE"
        WHEN 79 THEN "PICKLEBALL"
        WHEN 80 THEN "COOLDOWN"
        WHEN 82 THEN "SWIM BIKE RUN"
        WHEN 83 THEN "TRANSITION"
        WHEN 84 THEN "UNDERWATER DIVING"
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

    data_headers = (
        ('First Sample Start', 'datetime'), ('Last Sample End', 'datetime'),
        ('Source Modified or Device Created', 'datetime'), 'Record Kind', 'Source Name',
        'Bundle ID', 'Owner Bundle ID', 'Source Product Type', 'Source Version', 'Device',
        'Device Manufacturer', 'Device Model', 'Device Hardware', 'Device Firmware',
        'Device Software', 'Device Local Identifier', 'Device UDI',
        'Device Bluetooth Identifier', 'Origin Product Type', 'Origin Product Model',
        'Origin OS Build', 'Origin OS Version', 'Origin OS Version (as stored)',
        'Local Product Type', 'Local Product Model', 'Local OS Build', 'Local OS Version',
        'Timezone', 'Contributor Apple ID', 'Contributor Caller ID', 'Sample Rows',
        'Deleted Sample Rows', 'Other Rows', 'sync_provenance (as stored)',
        'derived_flags (as stored)', 'sync_identity (as stored)', 'Source Deleted (as stored)',
        'Row ID', 'Source ID', 'Device ID', 'Contributor ID')

    con, attached = _health_open(data_source, healthdb)
    if con is None:
        logfunc('healthdb_secure.sqlite is not a readable database, so which sources wrote '
                'samples is unknown, not empty. Listing what healthdb.sqlite registers.')
        return data_headers, _health_registered_rows(healthdb, len(data_headers)), \
            healthdb or data_source or ''

    data_list = []
    try:
        provenance = _health_provenance(con, attached)
        counts = _health_provenance_counts(con)
        def order(item):
            first = counts.get(item[0], {}).get('first')
            return (first is None, first or 0, item[0])
        for rowid, row in sorted(provenance.items(), key=order):
            count = counts.get(rowid, {})
            origin_type = row.get('origin_product_type')
            origin_build = row.get('origin_build')
            local_type = row.get('local_product_type')
            local_build = row.get('local_build')
            data_list.append((
                _health_ts(count.get('first')), _health_ts(count.get('last')), '', 'provenance',
                row.get('source_name'), row.get('bundle_id'), row.get('owner_bundle_id'),
                row.get('source_product_type'), row.get('source_version'), row.get('device_name'),
                row.get('device_manufacturer'), row.get('device_model'), row.get('device_hardware'),
                row.get('device_firmware'), row.get('device_software'),
                _health_cell(row.get('device_local_identifier')), _health_cell(row.get('device_udi')),
                _health_cell(row.get('device_bluetooth_identifier')), origin_type,
                context.lookup_metadata('apple_device_id_to_model', origin_type), origin_build,
                _health_os_version(context, origin_build, origin_type), _health_stored_os(row),
                local_type, context.lookup_metadata('apple_device_id_to_model', local_type),
                local_build, _health_os_version(context, local_build, local_type),
                row.get('tz_name'), row.get('contributor_apple_id'),
                row.get('contributor_caller_id'), count.get('sample', 0), count.get('deleted', 0),
                count.get('other', 0), _health_cell(row.get('sync_provenance')),
                _health_cell(row.get('derived_flags')), _health_cell(row.get('sync_identity')),
                _health_cell(row.get('source_deleted')), rowid, row.get('source_id'),
                row.get('device_id'), row.get('contributor_id')))
    except sqlite3.Error as ex:
        logfunc(f'Error reading Health provenances: {ex}')
    finally:
        con.close()

    return data_headers, data_list, data_source


@artifact_processor
def health_headphone_audio_levels(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    healthdb = context.get_source_file_path('healthdb.sqlite')

    data_headers = (
        ('Start', 'datetime'), ('End', 'datetime'), ('Record Added or Deleted', 'datetime'),
        'Record Kind', 'Level (dBASPL, as stored)', 'Original Value (as stored)',
        'Original Unit (as stored)', 'Series Min (as stored)', 'Series Max (as stored)',
        'Series Points Declared', 'Series Points Read', 'Series Point Status',
        'Series Parent Value Note', '_HKPrivateMediaSourceBundleIdentifier (as stored)', 'Device Name',
        'Device Manufacturer', 'Device Model', 'Local Identifier', 'Source',
        'Other Metadata (as stored)', 'series_location (as stored)', 'Object UUID', 'Data ID',
        'Provenance ROWID')

    con, attached = _health_open(data_source, healthdb)
    if con is None:
        logfunc('healthdb_secure.sqlite is not a readable database, so headphone audio '
                'samples are unknown, not empty.')
        return data_headers, [], data_source or ''

    data_list = []
    try:
        provenance = _health_provenance(con, attached)
        for rec in _health_sample_records(con, 173):
            row = provenance.get(rec['provenance'], {})
            media, other = _health_split_metadata(rec['metadata'], _HEADPHONE_MEDIA_KEY)
            data_list.append((
                _health_ts(rec['start']), _health_ts(rec['end']), _health_ts(rec['created']),
                rec['kind'], rec['quantity'], rec['original_quantity'], rec['original_unit'],
                rec['series_min'], rec['series_max'], rec['declared'], rec['points_read'],
                rec['status'],
                _HEALTH_PARENT_NOTES[173]
                if rec['kind'] == 'series parent' and rec['points_read'] else '',
                '; '.join(str(item[1]) for item in media), row.get('device_name'),
                row.get('device_manufacturer'), row.get('device_model'),
                _health_cell(row.get('device_local_identifier')), row.get('source_name'),
                _health_metadata_text(other), rec['series_location'],
                _health_cell(rec['uuid']), rec['data_id'], rec['provenance']))
    except sqlite3.Error as ex:
        logfunc(f'Error reading Health headphone audio samples: {ex}')
    finally:
        con.close()

    return data_headers, data_list, data_source


@artifact_processor
def health_heart_rate(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    healthdb = context.get_source_file_path('healthdb.sqlite')

    data_headers = (
        ('Start', 'datetime'), ('End', 'datetime'), ('Record Added or Deleted', 'datetime'),
        'Record Kind', 'Heart Rate (BPM)', 'Value (count/s, as stored)',
        'Original Value (as stored)', 'Original Unit (as stored)', 'Heart Rate Context',
        'Heart Rate Context Value', 'Series Min (as stored)', 'Series Max (as stored)',
        'Series Points Declared', 'Series Points Read', 'Series Point Status',
        'Series Parent Value Note', 'Device Name', 'Manufacturer', 'Hardware',
        'Model Name (from Hardware)', 'Source', 'Source Version', 'Timezone',
        'Other Metadata (as stored)', 'series_location (as stored)', 'Object UUID', 'Data ID',
        'Provenance ROWID')

    con, attached = _health_open(data_source, healthdb)
    if con is None:
        logfunc('healthdb_secure.sqlite is not a readable database, so heart rate samples '
                'are unknown, not empty.')
        return data_headers, [], data_source or ''

    data_list = []
    try:
        provenance = _health_provenance(con, attached)
        models = {}
        for rec in _health_sample_records(con, 5):
            row = provenance.get(rec['provenance'], {})
            hardware = row.get('device_hardware')
            if hardware not in models:
                models[hardware] = context.lookup_metadata('apple_device_id_to_model', hardware)
            contexts, other = _health_split_metadata(rec['metadata'], _HEART_RATE_CONTEXT_KEY)
            label, stored = _health_context_cells(contexts)
            quantity = rec['quantity']
            bpm = round(quantity * 60, 3) if isinstance(quantity, (int, float)) else ''
            data_list.append((
                _health_ts(rec['start']), _health_ts(rec['end']), _health_ts(rec['created']),
                rec['kind'], bpm, quantity, rec['original_quantity'], rec['original_unit'],
                label, stored, rec['series_min'], rec['series_max'], rec['declared'],
                rec['points_read'], rec['status'],
                _HEALTH_PARENT_NOTES[5] if rec['kind'] == 'series parent' else '',
                row.get('device_name'), row.get('device_manufacturer'), hardware, models[hardware],
                row.get('source_name'), row.get('source_version'),
                row.get('tz_name'), _health_metadata_text(other), rec['series_location'],
                _health_cell(rec['uuid']), rec['data_id'], rec['provenance']))
    except sqlite3.Error as ex:
        logfunc(f'Error reading Health heart rate samples: {ex}')
    finally:
        con.close()

    return data_headers, data_list, data_source


@artifact_processor
def health_resting_heart_rate(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    healthdb = context.get_source_file_path('healthdb.sqlite')

    data_headers = (
        ('Start', 'datetime'), ('End', 'datetime'), ('Record Added or Deleted', 'datetime'),
        'Record Kind', 'Resting Heart Rate (BPM, as stored)', 'Original Value (as stored)',
        'Original Unit (as stored)', 'Series Point Status', 'Source Product Type',
        'Model Name (from Source Product Type)', 'Source', 'Device Name', 'Source Version',
        'Timezone', 'Metadata (as stored)', 'Object UUID', 'Data ID', 'Provenance ROWID')

    con, attached = _health_open(data_source, healthdb)
    if con is None:
        logfunc('healthdb_secure.sqlite is not a readable database, so resting heart rate '
                'samples are unknown, not empty.')
        return data_headers, [], data_source or ''

    data_list = []
    try:
        provenance = _health_provenance(con, attached)
        models = {}
        for rec in _health_sample_records(con, 118):
            row = provenance.get(rec['provenance'], {})
            product = row.get('source_product_type')
            if product not in models:
                models[product] = context.lookup_metadata('apple_device_id_to_model', product)
            data_list.append((
                _health_ts(rec['start']), _health_ts(rec['end']), _health_ts(rec['created']),
                rec['kind'], rec['quantity'], rec['original_quantity'], rec['original_unit'],
                rec['status'], product, models[product], row.get('source_name'),
                row.get('device_name'), row.get('source_version'),
                row.get('tz_name'), _health_metadata_text(rec['metadata']),
                _health_cell(rec['uuid']), rec['data_id'], rec['provenance']))
    except sqlite3.Error as ex:
        logfunc(f'Error reading Health resting heart rate samples: {ex}')
    finally:
        con.close()

    return data_headers, data_list, data_source


@artifact_processor
def health_achievements(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')

    data_headers = (
        ('Earned Date', 'date'), ('Created Timestamp', 'datetime'), 'Achievement', 'Value', 'Unit',
        'Template Source Name', 'Template In Store', 'External Identifier',
        'Creator Device (as stored)', 'sync_provenance (as stored)', 'sync_identity (as stored)',
        'Row ID')

    con, _attached = _health_open(data_source, None)
    if con is None:
        logfunc('healthdb_secure.sqlite is not a readable database, so achievements are '
                'unknown, not empty.')
        return data_headers, [], data_source or ''

    data_list = []
    earned = 'ACHAchievementsPlugin_earned_instances'
    templates = 'ACHAchievementsPlugin_templates'
    try:
        if not _health_has_table(con, earned):
            logfunc(f'{earned} is not in this healthdb_secure.sqlite')
            return data_headers, data_list, data_source
        columns = _health_columns(con, earned)
        has_templates = _health_has_table(con, templates)
        template_source = 't.source_name' if has_templates else 'NULL'
        template_found = 't.unique_name IS NOT NULL' if has_templates else 'NULL'
        template_join = f'LEFT JOIN {templates} t ON t.unique_name = e.template_unique_name' \
            if has_templates else ''
        external = _health_field(columns, 'external_identifier', 'e')
        creator = _health_field(columns, 'creator_device', 'e')
        sync_provenance = _health_field(columns, 'sync_provenance', 'e')
        sync_identity = _health_field(columns, 'sync_identity', 'e')
        query = f'''
        SELECT e.earned_date, e.created_date, e.template_unique_name,
            e.value_in_canonical_unit, e.value_canonical_unit, {template_source},
            {template_found}, {external}, {creator}, {sync_provenance}, {sync_identity}, e.ROWID
        FROM {earned} e {template_join}
        ORDER BY e.earned_date, e.ROWID
        '''
        for row in con.execute(query):
            in_store = '' if row[6] is None else ('yes' if row[6] else 'no')
            data_list.append((row[0], _health_ts(row[1]), row[2], row[3], row[4], row[5],
                              in_store, _health_cell(row[7]), _health_cell(row[8]),
                              _health_cell(row[9]), _health_cell(row[10]), row[11]))
    except sqlite3.Error as ex:
        logfunc(f'Error reading Health achievements: {ex}')
    finally:
        con.close()

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


@artifact_processor
def health_flights_climbed(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    data_list = []

    query = '''
    SELECT
        samples.start_date AS "Start Date",
        samples.end_date AS "End Date",
        quantity_samples.quantity AS "Flights Climbed",
        (samples.end_date - samples.start_date) AS "Duration (Seconds)",
        data_provenances.origin_product_type AS "Device"
    FROM samples, quantity_samples, data_provenances, objects
    WHERE samples.data_type = 12
    AND samples.data_id = quantity_samples.data_id
    AND samples.data_id = objects.data_id
    AND objects.provenance = data_provenances.rowid
    '''

    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), 'Flights Climbed',
        'Duration (Seconds)', 'Device ID', 'Device Model')

    db_records = get_sqlite_db_records(data_source, query)

    for record in db_records:
        start_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        end_timestamp = convert_cocoa_core_data_ts_to_utc(record[1])
        hardware = context.lookup_metadata('apple_device_id_to_model', record[4])
        data_list.append((start_timestamp, end_timestamp, record[2], record[3],
                          record[4], hardware))

    return data_headers, data_list, data_source
