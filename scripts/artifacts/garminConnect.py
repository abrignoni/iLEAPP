__artifacts_v2__ = {
    "garmin_ios_activities": {
        "name": "Garmin Connect - Activities",
        "description": "Activities held in the app's calendar cache, with the start and end of "
                       "the cached track where the app kept one.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": "One row per entry of the app's calendar cache that carries an activity name, "
                 "read from "
                 "Library/Caches/DataCache/GCMCacheManagerConnectCalendarCachePath/GCMCacheManagerConnectCalendarCacheFile, "
                 "an NSKeyedArchiver plist. That cache held 72 entries on the iOS 17.3 image and "
                 "67 on the iOS 15.3.1 image, of which 5 and 4 carry an activity name and are "
                 "reported here; the rest carry no activity and are reported by the Daily Metrics "
                 "artifact. Start Time (Device Local) is the app's own startTimestampLocal read "
                 "as a wall clock reading rather than as an instant, and it is carried as text so "
                 "nothing downstream can attach a zone to it. The app writes a GMT value beside "
                 "the local one on the per-day entries of the same cache, and on every one of the "
                 "11 and 5 entries of the two tested images that carry both, the local value was "
                 "4 hours behind the GMT value. Activity entries carry only the local value, so "
                 "no UTC instant is recorded for an activity and none is computed here. Latitude "
                 "and Longitude are the start of the track the app cached for that activity and "
                 "End Latitude and End Longitude its end, read from Library/Application "
                 "Support/DataCache/com.garmin.activity.common.polyline/ where each file is named "
                 "for the activity id. All 9 activity rows across the two images matched a cached "
                 "track on that id. Track Points Recorded is the point count the cache states for "
                 "the activity and Track Points Cached is the number of points the cached track "
                 "decodes to; the cached track was shorter than the recorded count on all 9 rows "
                 "(2,598 recorded against 1,062 cached on one image and 1,729 against 782 on the "
                 "other), so the cached track is a sample of the activity rather than the "
                 "recorded track. Lap Count held 4 on 4 of the 5 rows of the iOS 17.3 image and a "
                 "different value on the other, and one value on all 4 rows of the iOS 15.3.1 "
                 "image. Cache Record Written is the entry's own creationDate, a Cocoa absolute "
                 "time, so it records when the app wrote the entry and not when the activity "
                 "happened. Activity Type ID, Sport Type Key and Item Type are reported as "
                 "stored. Sport Type Key and Item Type held 0 on every row of both images. "
                 "Activity Type ID held 0 on 8 rows and 2 on 1 row of the 9 reported, and the row "
                 "holding 2 is the one whose activity name records walking while the rows holding "
                 "0 record running; nothing available defines either value and no mapping is "
                 "asserted from that. On the iOS 14.3 image the container held no calendar cache "
                 "and no track cache, and on the iOS 26.2.1 image the container held neither of "
                 "those either, keeping a Documents/connect_apollo_db directory instead whose "
                 "cached activity list documents were empty when read directly; this module does "
                 "not read that directory, so neither image produced a row here. A row records "
                 "what the app cached about an activity reported by a device on the account. It "
                 "does not establish who was wearing that device. The app container is identified "
                 "from its own .com.apple.mobile_container_manager.metadata.plist, and a file is "
                 "read only when it sits inside a container whose plist names "
                 "com.garmin.connect.mobile or group.com.garmin.connect, so a file matched in "
                 "another app's container is not read. That guard is exercised by the tested "
                 "images rather than only present: the image cache directory this module also "
                 "matches belongs to a third party library that other apps embed, and on the iOS "
                 "14.3 image 194 of its files were staged while the 5 inside the Garmin container "
                 "were the only ones reported. On the two tested images that do not carry Garmin "
                 "Connect, 79 and 147 such files were staged and every artifact in this module "
                 "reported nothing.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/DataCache/*',
                  '*/mobile/Containers/Data/Application/*/Library/Application Support/DataCache/*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "lava", "kml"],
        "artifact_icon": "activity",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | Garmin Connect 4.74.3 | 5 rows",
            "hickman_ios15": "iOS 15.3.1 | Garmin Connect 4.65 | 4 rows",
            "hickman_ios14": "iOS 14.3 | Garmin Connect 4.38 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | Garmin Connect 5.21.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | Garmin Connect not installed | 0 rows",
            "jess_ios15": "iOS 15.0.2 | Garmin Connect not installed | 0 rows",
        },
    },
    "garmin_ios_activity_tracks": {
        "name": "Garmin Connect - Activity Tracks",
        "description": "Points of the sampled track the app cached for an activity.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": "One row per point of the track the app cached for an activity, from "
                 "Library/Application Support/DataCache/com.garmin.activity.common.polyline/ "
                 "where each file is named for the activity id and holds a JSON document. The "
                 "coordinates come from the document's encodedSamples field, a Google encoded "
                 "polyline, decoded here. The decode was checked against the same document's own "
                 "recorded bounds: on all 9 tracks the minimum and maximum of the decoded "
                 "latitudes and longitudes equalled the document's minLat, maxLat, minLon and "
                 "maxLon to five decimal places, and the first decoded point equalled its "
                 "startLat and startLon to the same precision. The point count is smaller than "
                 "the count the activity cache records: 1,062 points decoded across 5 tracks on "
                 "the iOS 17.3 image against 2,598 recorded, and 782 across 4 tracks on the iOS "
                 "15.3.1 image against 1,729. The field is named for samples and the cached track "
                 "is a sample of the activity, so the points here are not the recorded track and "
                 "the line between two consecutive points is not a recorded path. No time is "
                 "stored per point, so Activity Name and Activity Start come from the calendar "
                 "cache entry with the same activity id and every point of one track carries the "
                 "same pair. The app container is identified from its own "
                 ".com.apple.mobile_container_manager.metadata.plist, and a file is read only "
                 "when it sits inside a container whose plist names com.garmin.connect.mobile or "
                 "group.com.garmin.connect, so a file matched in another app's container is not "
                 "read. That guard is exercised by the tested images rather than only present: "
                 "the image cache directory this module also matches belongs to a third party "
                 "library that other apps embed, and on the iOS 14.3 image 194 of its files were "
                 "staged while the 5 inside the Garmin container were the only ones reported. On "
                 "the two tested images that do not carry Garmin Connect, 79 and 147 such files "
                 "were staged and every artifact in this module reported nothing.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/DataCache/*',
                  '*/mobile/Containers/Data/Application/*/Library/Application Support/DataCache/*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "lava", "kml"],
        "artifact_icon": "map",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | Garmin Connect 4.74.3 | 1062 rows",
            "hickman_ios15": "iOS 15.3.1 | Garmin Connect 4.65 | 782 rows",
            "hickman_ios14": "iOS 14.3 | Garmin Connect 4.38 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | Garmin Connect 5.21.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | Garmin Connect not installed | 0 rows",
            "jess_ios15": "iOS 15.0.2 | Garmin Connect not installed | 0 rows",
        },
    },
    "garmin_ios_daily_metrics": {
        "name": "Garmin Connect - Daily Metrics",
        "description": "Per-day entries of the app's calendar cache that carry no activity, with "
                       "whichever of steps, sleep, stress, body battery and heart rate the entry "
                       "holds for that day.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": "One row per entry of the calendar cache that carries no activity name, from the "
                 "same file the Activities artifact reads. 67 of the 72 entries on the iOS 17.3 "
                 "image and 63 of 67 on the iOS 15.3.1 image are reported here. An entry carries "
                 "a subset of the columns and the subset differs by Item Type, so most columns "
                 "are blank on most rows: on the iOS 17.3 image Steps and Step Goal carried a "
                 "value on 14 rows, Sleep Duration on 9, and the stress, body battery and heart "
                 "rate columns on 11 each. Item Type is reported as stored. Nothing available "
                 "defines the values, and which columns an entry carries is the only thing here "
                 "that separates them. Start Time (UTC) is the entry's startTimestampGMT and is "
                 "present on 11 of the 67 rows on the iOS 17.3 image and 5 of 63 on the other; "
                 "the rest of the rows record a calendar day and no instant, so Calendar Date "
                 "leads the table. Start Time (Device Local) is the app's own startTimestampLocal "
                 "read as a wall clock reading rather than as an instant, and it is carried as "
                 "text so nothing downstream can attach a zone to it. The app writes a GMT value "
                 "beside the local one on the per-day entries of the same cache, and on every one "
                 "of the 11 and 5 entries of the two tested images that carry both, the local "
                 "value was 4 hours behind the GMT value. Cache Record Written is the entry's own "
                 "creationDate. The entry also carries a distance, which was 0 on every reported "
                 "row of both images, so it is not given a column of its own here. Moderate "
                 "Intensity Minutes and Vigorous Intensity Minutes held the same value as each "
                 "other on every reported row of both images, either 0 or -1, and both are kept "
                 "because the entry declares them separately. A row is what the app cached for "
                 "that day, so an absent day is not evidence that the device recorded nothing, "
                 "and the window the cache covers is not established. The app container is "
                 "identified from its own .com.apple.mobile_container_manager.metadata.plist, and "
                 "a file is read only when it sits inside a container whose plist names "
                 "com.garmin.connect.mobile or group.com.garmin.connect, so a file matched in "
                 "another app's container is not read. That guard is exercised by the tested "
                 "images rather than only present: the image cache directory this module also "
                 "matches belongs to a third party library that other apps embed, and on the iOS "
                 "14.3 image 194 of its files were staged while the 5 inside the Garmin container "
                 "were the only ones reported. On the two tested images that do not carry Garmin "
                 "Connect, 79 and 147 such files were staged and every artifact in this module "
                 "reported nothing.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/DataCache/*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "bar-chart-2",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | Garmin Connect 4.74.3 | 67 rows",
            "hickman_ios15": "iOS 15.3.1 | Garmin Connect 4.65 | 63 rows",
            "hickman_ios14": "iOS 14.3 | Garmin Connect 4.38 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | Garmin Connect 5.21.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | Garmin Connect not installed | 0 rows",
            "jess_ios15": "iOS 15.0.2 | Garmin Connect not installed | 0 rows",
        },
    },
    "garmin_ios_daily_heart_rate": {
        "name": "Garmin Connect - Daily Heart Rate",
        "description": "Per-day heart rate record the app cached in its Move IQ store.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": "One row per day in "
                 "Library/Caches/DataCache/GCMCacheManagerMoveIQCachePath/GCMCacheManagerMoveIQCacheFile "
                 "that carries a heart rate record or a heart rate zone record. 8 days were "
                 "reported on the iOS 17.3 image and 7 on the iOS 15.3.1 image. A day can carry "
                 "the zone record without the heart rate record: the zone floors were present on "
                 "all 8 and all 7 rows while Resting Heart Rate was present on 4 and 5. Minimum "
                 "Heart Rate and Maximum Heart Rate are in the same record as the resting value "
                 "and were blank on every row of the iOS 17.3 image and present on 5 rows of the "
                 "iOS 15.3.1 image, so an absent value there is the record not carrying one "
                 "rather than a reading of zero. Device ID is in that record too and was blank on "
                 "every row of both images; it is kept because the record declares it. Day Start "
                 "and Day End are present on 7 and 5 rows, the rows that carry the heart rate "
                 "record. Zone 1 Floor, Zone 2 Floor, Zone 3 Floor, Zone 4 Floor, Zone 5 Floor, "
                 "Resting Heart Rate Used and Maximum Heart Rate Used come from the day's "
                 "heartRateZoneData and are the thresholds the app held rather than measurements "
                 "of that day, so each of those seven held one value across every day of both "
                 "images. Training Method and Sport are reported as stored; both held 0 on every "
                 "row of both images. The User Profile ID on every row of both images equalled "
                 "the user profile id the Account artifact reports for the signed-in account. The "
                 "same day record also carries a heart rate series, a per-minute movement series "
                 "and a sleep event list, which the Heart Rate Samples, Movement Samples and "
                 "Sleep Events artifacts report. The record's own listOfEvents was empty on every "
                 "day of both images. On the iOS 14.3 image the file was present and held only a "
                 "cache bookkeeping key with no day, and on the iOS 26.2.1 image the app kept no "
                 "such file, so neither produced a row. The app container is identified from its "
                 "own .com.apple.mobile_container_manager.metadata.plist, and a file is read only "
                 "when it sits inside a container whose plist names com.garmin.connect.mobile or "
                 "group.com.garmin.connect, so a file matched in another app's container is not "
                 "read. That guard is exercised by the tested images rather than only present: "
                 "the image cache directory this module also matches belongs to a third party "
                 "library that other apps embed, and on the iOS 14.3 image 194 of its files were "
                 "staged while the 5 inside the Garmin container were the only ones reported. On "
                 "the two tested images that do not carry Garmin Connect, 79 and 147 such files "
                 "were staged and every artifact in this module reported nothing.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/DataCache/*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "heart",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | Garmin Connect 4.74.3 | 8 rows",
            "hickman_ios15": "iOS 15.3.1 | Garmin Connect 4.65 | 7 rows",
            "hickman_ios14": "iOS 14.3 | Garmin Connect 4.38 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | Garmin Connect 5.21.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | Garmin Connect not installed | 0 rows",
            "jess_ios15": "iOS 15.0.2 | Garmin Connect not installed | 0 rows",
        },
    },
    "garmin_ios_heart_rate_samples": {
        "name": "Garmin Connect - Heart Rate Samples",
        "description": "Heart rate readings the app cached through the day, from its Move IQ "
                       "store.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": "One row per entry of the heart rate series a day's record carries, from its "
                 "allDayHRData hrDetail heartRateArray. The store is "
                 "Library/Caches/DataCache/GCMCacheManagerMoveIQCachePath/GCMCacheManagerMoveIQCacheFile, "
                 "an NSKeyedArchiver plist holding one record per calendar day. The Daily Heart "
                 "Rate artifact reports the rest of that record. Sample Time is the entry's own "
                 "startGMT, a Cocoa absolute time, so it is an instant and not a wall clock "
                 "reading. Heart Rate is reported as stored and the store gives no unit; 2,940 "
                 "entries across 5 days were reported on the iOS 15.3.1 image and 6 of them "
                 "carried no value, which is the entry holding none rather than a reading of "
                 "zero. The gap between consecutive entries within a day was 120 seconds on 2,929 "
                 "of the 2,935 gaps and longer on the other 6, so the series has breaks where the "
                 "app cached no reading and a row is not evidence that the next reading is 120 "
                 "seconds later. The iOS 17.3 image kept day records whose heart rate series was "
                 "empty, so it reported nothing here while still reporting the day rows in Daily "
                 "Heart Rate, and the iOS 14.3 and 26.2.1 images hold no day record at all. A row "
                 "records what the app cached for that moment. It does not establish that a "
                 "particular person was wearing the device. User Profile ID is the id the record "
                 "itself carries and held the one value 89370933 across every reported row of "
                 "both images, which is the single account the app was signed in as; it is kept "
                 "so a row carries its own account rather than taking one from the artifact it "
                 "sits in. The app container is identified from its own "
                 ".com.apple.mobile_container_manager.metadata.plist, and a file is read only "
                 "when it sits inside a container whose plist names com.garmin.connect.mobile or "
                 "group.com.garmin.connect, so a file matched in another app's container is not "
                 "read.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/DataCache/*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "activity",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | Garmin Connect 4.74.3 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | Garmin Connect 4.65 | 2940 rows",
            "hickman_ios14": "iOS 14.3 | Garmin Connect 4.38 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | Garmin Connect 5.21.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | Garmin Connect not installed | 0 rows",
            "jess_ios15": "iOS 15.0.2 | Garmin Connect not installed | 0 rows",
        },
    },
    "garmin_ios_movement_samples": {
        "name": "Garmin Connect - Movement Samples",
        "description": "Per-minute movement readings the app cached through the day, from its "
                       "Move IQ store.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": "One row per entry of the movement series a day's record carries, from its "
                 "movementDetail movementArray. The store is "
                 "Library/Caches/DataCache/GCMCacheManagerMoveIQCachePath/GCMCacheManagerMoveIQCacheFile, "
                 "an NSKeyedArchiver plist holding one record per calendar day. The Daily Heart "
                 "Rate artifact reports the rest of that record. Sample Time is the entry's own "
                 "startGMT, a Cocoa absolute time. Movement Value is reported as stored: the "
                 "store gives no unit and nothing available defines the scale, so the column is "
                 "the number the app cached and not a distance, a step count or an intensity in "
                 "any named unit. 6,630 entries across 5 days were reported on the iOS 15.3.1 "
                 "image, 3,645 of them zero, and a zero entry is reported rather than dropped so "
                 "that the series is not read as continuous movement. The gap between consecutive "
                 "entries within a day was 60 seconds on every one of the 6,625 gaps, so a full "
                 "day is 1,440 entries and one of the 5 days is short at 870. The iOS 17.3 image "
                 "kept day records whose movement series was empty, so it reported nothing here, "
                 "and the iOS 14.3 and 26.2.1 images hold no day record at all. A row records "
                 "what the app cached for that minute. It does not establish that a particular "
                 "person was carrying or wearing the device. User Profile ID is the id the record "
                 "itself carries and held the one value 89370933 across every reported row of "
                 "both images, which is the single account the app was signed in as; it is kept "
                 "so a row carries its own account rather than taking one from the artifact it "
                 "sits in. The app container is identified from its own "
                 ".com.apple.mobile_container_manager.metadata.plist, and a file is read only "
                 "when it sits inside a container whose plist names com.garmin.connect.mobile or "
                 "group.com.garmin.connect, so a file matched in another app's container is not "
                 "read.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/DataCache/*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "trending-up",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | Garmin Connect 4.74.3 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | Garmin Connect 4.65 | 6630 rows",
            "hickman_ios14": "iOS 14.3 | Garmin Connect 4.38 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | Garmin Connect 5.21.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | Garmin Connect not installed | 0 rows",
            "jess_ios15": "iOS 15.0.2 | Garmin Connect not installed | 0 rows",
        },
    },
    "garmin_ios_sleep_events": {
        "name": "Garmin Connect - Sleep Events",
        "description": "Instants the app cached in the sleep event list of its Move IQ store, "
                       "with the type it recorded for each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": "One row per entry of the sleep event list a day's record carries, from its "
                 "allDayHRData sleepEventList. The store is "
                 "Library/Caches/DataCache/GCMCacheManagerMoveIQCachePath/GCMCacheManagerMoveIQCacheFile, "
                 "an NSKeyedArchiver plist holding one record per calendar day. The Daily Heart "
                 "Rate artifact reports the rest of that record. Event Time is the entry's own "
                 "timeStamp, a Cocoa absolute time. Event Type is reported as stored; the tested "
                 "images hold 0 and 1 and 2 and 3 and nothing available defines them, so no "
                 "meaning is given to the numbers here and none should be read into the "
                 "artifact's name beyond the list the app calls a sleep event list. What the data "
                 "does show, measured on both images: a day's record carries up to four entries, "
                 "and on all 15 pairs the entry typed 1 came before the entry typed 0 and the "
                 "entry typed 3 came before the entry typed 2, with the gap within a pair running "
                 "from 6.08 to 10.73 hours. The same instants repeat across neighbouring days "
                 "under a different type: the iOS 15.3.1 image reported 20 rows holding 14 "
                 "distinct instants, while the iOS 17.3 image reported 10 rows holding 10 "
                 "distinct instants because its day records are not consecutive. Every row is "
                 "reported because each is a stored entry, and Calendar Date Of The Record is the "
                 "day whose record held it rather than the day the instant falls on. The iOS 14.3 "
                 "and 26.2.1 images hold no day record, so neither produced a row. A row records "
                 "an instant the app cached. It does not establish that a particular person was "
                 "asleep or awake. User Profile ID is the id the record itself carries and held "
                 "the one value 89370933 across every reported row of both images, which is the "
                 "single account the app was signed in as; it is kept so a row carries its own "
                 "account rather than taking one from the artifact it sits in. The app container "
                 "is identified from its own .com.apple.mobile_container_manager.metadata.plist, "
                 "and a file is read only when it sits inside a container whose plist names "
                 "com.garmin.connect.mobile or group.com.garmin.connect, so a file matched in "
                 "another app's container is not read.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/DataCache/*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "moon",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | Garmin Connect 4.74.3 | 10 rows",
            "hickman_ios15": "iOS 15.3.1 | Garmin Connect 4.65 | 20 rows",
            "hickman_ios14": "iOS 14.3 | Garmin Connect 4.38 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | Garmin Connect 5.21.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | Garmin Connect not installed | 0 rows",
            "jess_ios15": "iOS 15.0.2 | Garmin Connect not installed | 0 rows",
        },
    },
    "garmin_ios_devices": {
        "name": "Garmin Connect - Devices",
        "description": "Device records the app kept in its device caches.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": "One row per device record in the app's device caches, with Cache File naming "
                 "the cache the row came from. Three caches are read and which of them a "
                 "container holds differs by app version: Library/Application "
                 "Support/DataCache/GCMGarmindevicesStore/GCMGarmindevicesStorePairedDevices and "
                 "Library/Application "
                 "Support/DataCache/Devices/RealRegisteredDevicesStoreCacheFile were both present "
                 "on the iOS 17.3, 15.3.1 and 26.2.1 images, and the iOS 14.3 image held neither "
                 "and kept "
                 "Library/Caches/DataCache/Devices/GCMCacheManagerRegisteredDevicesCacheFile "
                 "instead, whose keys are spelled differently and are resolved here. Each tested "
                 "image held one Garmin device, so the 2 rows on the iOS 17.3 image are one "
                 "device reported from two caches and they carry the same Unit ID; a row is a "
                 "cache record, not a device. The two caches carry different parts of the record. "
                 "Last Connected is a Cocoa absolute time and is held only by the paired store, "
                 "so it is blank on the registered store's rows. Part Number, Product SKU and "
                 "Application Key are held only by the registered store, and Bluetooth Low Energy "
                 "Identifier only by the paired store, which carried one on the iOS 17.3 and "
                 "26.2.1 images and none on the others. On the iOS 15.3.1 image the paired store "
                 "held the unit id and the connection time and nothing else, so Product Name, "
                 "Friendly Name and Product Number are blank on that row, and Product Number is "
                 "blank on the iOS 14.3 image, whose older cache does not carry it. Friendly Name "
                 "equalled Product Name on every row of every image that filled both. Firmware "
                 "Version is reported as stored and the two caches spell it differently for the "
                 "same device at the same moment: on the iOS 17.3 image they held 7.80 and 780 "
                 "and on the iOS 26.2.1 image 17.05 and 1705, the integer being the dotted "
                 "reading times a hundred in both cases. NFC Chip Type and Payment Cards Cached "
                 "come from Library/Caches/GarminPayWalletMetadataCache and "
                 "GarminPayWalletItemsCache, joined to the row on the unit id the wallet caches "
                 "record; the cached card list was empty on every image that held one, so Payment "
                 "Cards Cached was 0 throughout and no card is recorded here. The app's own "
                 "product catalogue cache is not read: it lists Garmin products the app ships "
                 "knowledge of rather than devices the account holds. The app container is "
                 "identified from its own .com.apple.mobile_container_manager.metadata.plist, and "
                 "a file is read only when it sits inside a container whose plist names "
                 "com.garmin.connect.mobile or group.com.garmin.connect, so a file matched in "
                 "another app's container is not read. That guard is exercised by the tested "
                 "images rather than only present: the image cache directory this module also "
                 "matches belongs to a third party library that other apps embed, and on the iOS "
                 "14.3 image 194 of its files were staged while the 5 inside the Garmin container "
                 "were the only ones reported. On the two tested images that do not carry Garmin "
                 "Connect, 79 and 147 such files were staged and every artifact in this module "
                 "reported nothing.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/DataCache/*',
                  '*/mobile/Containers/Data/Application/*/Library/Application Support/DataCache/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/GarminPay*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "watch",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | Garmin Connect 4.74.3 | 2 rows",
            "hickman_ios15": "iOS 15.3.1 | Garmin Connect 4.65 | 2 rows",
            "hickman_ios14": "iOS 14.3 | Garmin Connect 4.38 | 1 row",
            "falken_ios26": "iOS 26.2.1 | Garmin Connect 5.21.1 | 2 rows",
            "abe_ios16": "iOS 16.5 | Garmin Connect not installed | 0 rows",
            "jess_ios15": "iOS 15.0.2 | Garmin Connect not installed | 0 rows",
        },
    },
    "garmin_ios_account": {
        "name": "Garmin Connect - Account",
        "description": "Account directories the app kept, with the cached profile on the one it "
                       "recorded a user profile id for.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": "One row per account directory under Documents/users/ in the app's container. "
                 "The app names that directory for the signed-in account: it was the account's "
                 "email address on the iOS 17.3, 15.3.1 and 14.3 images and an identifier on the "
                 "iOS 26.2.1 image. It also keeps a directory named anonymous, which carried no "
                 "user profile id on any tested image, which is why 2 rows are reported for one "
                 "account on three of the images. The profile columns come from caches that sit "
                 "at container level rather than under an account directory, so they are filled "
                 "only on the row whose own directory records a user profile id, and the "
                 "anonymous row carries the directory name alone. Country Code and the user "
                 "profile id are read from that directory's GCMUserSettingsUserLocationKey and "
                 "the rest of the profile from "
                 "Library/Caches/DataCache/GCMCacheManagerPersonalInformationCachePath/GCMCacheManagerUserSettingsDataCacheFile. "
                 "Height is in centimetres and Weight in grams, as the cache stores them. Birth "
                 "Date is a Cocoa absolute time, reported as stored in UTC; on the iOS 17.3 image "
                 "it fell on midnight of its own day in the time zone the same cache records for "
                 "the profile, so the day it names in UTC can be a different day from the one the "
                 "profile holds. Profile Time Zone comes from the personal information cache and "
                 "carried a zone on the iOS 17.3, 15.3.1 and 26.2.1 images, while the iOS 14.3 "
                 "image's older cache does not hold one and leaves it blank. Wake Time and Sleep "
                 "Time are seconds after midnight, as stored. Gender (as stored), Handedness (as "
                 "stored), Time Format (as stored), Units Of Measure (as stored) and Activity "
                 "Level (as stored) are reported as stored and nothing available defines their "
                 "values. VO2 Max Cycling and Activity Level (as stored) both held -1 on the "
                 "profile row of all four tested images that carry the app, which is what the "
                 "cache carries for those two unrelated fields there rather than a relationship "
                 "between them. VO2 Max Running carried a reading on three of those four and -1 "
                 "on the fourth. Nothing available defines -1. Incident Detection Contact Name is "
                 "the name the app held for its incident detection feature and was present on the "
                 "iOS 14.3 image only. Last Logged In is the app's LastLoggedInDateFileName, a "
                 "Cocoa absolute time, and records a time the app wrote rather than a sign-in a "
                 "person performed. Country Code Verified Timestamp is text in the cache and is "
                 "reported as stored. Full Name, Display Name, Garmin GUID, Authentication "
                 "Domain, App Version and Profile Image come from "
                 "Library/Preferences/group.com.garmin.connect.plist in the shared app group "
                 "container, which holds a cached profile as JSON and the profile picture as "
                 "base64 inside it. Those six are attached only where the profile id that file "
                 "carries equals the user profile id the account directory records. The two "
                 "agreed on every tested image that carries the app, so the branch that refuses a "
                 "mismatch is present and was not exercised here. App Version is that file's "
                 "GCMAppVersion key and equalled the CFBundleShortVersionString of the installed "
                 "app bundle on all 4 tested images that carry the app. Profile Image is decoded "
                 "from the file's own imageData field and is the picture the app cached for the "
                 "account, not a file a person saved. The app container is identified from its "
                 "own .com.apple.mobile_container_manager.metadata.plist, and a file is read only "
                 "when it sits inside a container whose plist names com.garmin.connect.mobile or "
                 "group.com.garmin.connect, so a file matched in another app's container is not "
                 "read. That guard is exercised by the tested images rather than only present: "
                 "the image cache directory this module also matches belongs to a third party "
                 "library that other apps embed, and on the iOS 14.3 image 194 of its files were "
                 "staged while the 5 inside the Garmin container were the only ones reported. On "
                 "the two tested images that do not carry Garmin Connect, 79 and 147 such files "
                 "were staged and every artifact in this module reported nothing.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/DataCache/*',
                  '*/mobile/Containers/Data/Application/*/Library/Application Support/DataCache/*',
                  '*/mobile/Containers/Data/Application/*/Documents/users/*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
                  '*/mobile/Containers/Shared/AppGroup/*/Library/Preferences/group.com.garmin.connect.plist',
                  '*/mobile/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | Garmin Connect 4.74.3 | 2 rows",
            "hickman_ios15": "iOS 15.3.1 | Garmin Connect 4.65 | 2 rows",
            "hickman_ios14": "iOS 14.3 | Garmin Connect 4.38 | 2 rows",
            "falken_ios26": "iOS 26.2.1 | Garmin Connect 5.21.1 | 1 row",
            "abe_ios16": "iOS 16.5 | Garmin Connect not installed | 0 rows",
            "jess_ios15": "iOS 15.0.2 | Garmin Connect not installed | 0 rows",
        },
    },
    "garmin_ios_cached_images": {
        "name": "Garmin Connect - Cached Images",
        "description": "Images the app downloaded and kept in its image cache, with the address "
                       "each was fetched from.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": "One row per file in "
                 "Library/Caches/com.pinterest.PINDiskCache.PINRemoteImageManagerCache inside the "
                 "Garmin container whose bytes, or whose archived data object's bytes, carry a "
                 "JPEG, PNG, GIF or RIFF signature. The cache file name is the address the app "
                 "fetched the image from, percent encoded, and Address is that name decoded. On "
                 "the iOS 17.3 image the cache held 13 such files and on the iOS 15.3.1 image 23. "
                 "Image Kind is derived from the address: an address under /profile_images/ is a "
                 "profile image, one under /images/badges/ a badge, and one under /device-images/ "
                 "or /products/ a product image. Garmin User ID In Address is the number the "
                 "profile image address ends with. On both images that carry profile images one "
                 "of those numbers equalled the user profile id of the signed-in account, and the "
                 "iOS 15.3.1 image carried 5 distinct numbers in total, so the cache holds "
                 "profile images of Garmin accounts other than the signed-in one. An image here "
                 "was downloaded by the app. Its presence does not establish that a person viewed "
                 "it, and the numbers in the addresses are reported as stored without any "
                 "relationship to the account being asserted. One entry can be a transformed copy "
                 "of another: on 3 of the tested images an address ended in a marker the caching "
                 "library appends and named a profile image the cache also held under its own "
                 "address, and both are reported. A transformed copy is written as an archived "
                 "data object rather than as raw bytes and both forms are read. On the iOS 26.2.1 "
                 "image the app kept no such cache. The app container is identified from its own "
                 ".com.apple.mobile_container_manager.metadata.plist, and a file is read only "
                 "when it sits inside a container whose plist names com.garmin.connect.mobile or "
                 "group.com.garmin.connect, so a file matched in another app's container is not "
                 "read. That guard is exercised by the tested images rather than only present: "
                 "the image cache directory this module also matches belongs to a third party "
                 "library that other apps embed, and on the iOS 14.3 image 194 of its files were "
                 "staged while the 5 inside the Garmin container were the only ones reported. On "
                 "the two tested images that do not carry Garmin Connect, 79 and 147 such files "
                 "were staged and every artifact in this module reported nothing.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "image",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | Garmin Connect 4.74.3 | 13 rows",
            "hickman_ios15": "iOS 15.3.1 | Garmin Connect 4.65 | 23 rows",
            "hickman_ios14": "iOS 14.3 | Garmin Connect 4.38 | 5 rows",
            "falken_ios26": "iOS 26.2.1 | Garmin Connect 5.21.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | Garmin Connect not installed | 0 rows",
            "jess_ios15": "iOS 15.0.2 | Garmin Connect not installed | 0 rows",
        },
    },
}

import base64
import json
import os
import plistlib
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote

from scripts.ilapfuncs import (artifact_processor, check_in_embedded_media, check_in_media,
                               get_plist_file_content, logfunc)

_METADATA_NAME = '.com.apple.mobile_container_manager.metadata.plist'
_APP_ID = 'com.garmin.connect.mobile'
_GROUP_ID = 'group.com.garmin.connect'
_COCOA_EPOCH_UTC = datetime(2001, 1, 1, tzinfo=timezone.utc)
_COCOA_EPOCH_NAIVE = datetime(2001, 1, 1)
_IMAGE_SIGNATURES = (b'\xff\xd8\xff', b'\x89PNG\r\n\x1a\n', b'GIF87a', b'GIF89a', b'RIFF')

# Leaf names of the caches this module reads, relative to the app's data container.
_CALENDAR = 'GCMCacheManagerConnectCalendarCacheFile'
_MOVE_IQ = 'GCMCacheManagerMoveIQCacheFile'
_PAIRED = 'GCMGarmindevicesStorePairedDevices'
_REGISTERED = ('RealRegisteredDevicesStoreCacheFile', 'GCMCacheManagerRegisteredDevicesCacheFile')
_USER_SETTINGS = 'GCMCacheManagerUserSettingsDataCacheFile'
_PERSONAL = 'GCMCacheManagerPersonalInformationCacheFile'
_LAST_LOGIN = 'LastLoggedInDateFileName'
_WALLET_METADATA = 'GarminPayWalletMetadataCache'
_WALLET_ITEMS = 'GarminPayWalletItemsCache'
_WALLET_USER = 'GarminPayUserWalletCache'
_POLYLINE_DIR = 'com.garmin.activity.common.polyline'
_IMAGE_CACHE_DIR = 'com.pinterest.PINDiskCache.PINRemoteImageManagerCache'
_GROUP_PREFS = 'group.com.garmin.connect.plist'
_PROFILE_KEY = 'com.garmin.ConnectProfileCache.UserProfile'
_CUSTOMER_KEY = 'com.garmin.ConnectProfileCache.CustomerInfo'
_DAY = re.compile(r'^\d{4}-\d{2}-\d{2}$')
_PROFILE_IMAGE_URL = re.compile(r'/profile_images/[0-9a-f-]+-(\d+)\.png', re.I)
_BADGE_URL = re.compile(r'/images/badges/', re.I)
_PRODUCT_IMAGE_URL = re.compile(r'/device-images/|/products/', re.I)


def _containers(files_found):
    '''{container directory: bundle or group id} read from each container's own metadata plist.'''
    containers = {}
    for found in files_found:
        path = str(found)
        if os.path.basename(path) != _METADATA_NAME or os.path.isdir(path):
            continue
        try:
            with open(path, 'rb') as handle:
                plist = plistlib.load(handle)
        except (plistlib.InvalidFileException, OSError, ValueError) as error:
            logfunc(f'Garmin Connect: could not read a container metadata plist: {error}')
            continue
        identifier = plist.get('MCMMetadataIdentifier')
        if identifier in (_APP_ID, _GROUP_ID):
            containers[os.path.dirname(path).replace('\\', '/')] = identifier
    return containers


def _garmin_files(files_found, containers):
    '''Matched files that sit inside a container the metadata plist named as Garmin's.'''
    keep = []
    for found in files_found:
        path = str(found).replace('\\', '/')
        if os.path.isdir(path) or os.path.basename(path) == _METADATA_NAME:
            continue
        for container in containers:
            if path.startswith(container + '/'):
                keep.append((container, path))
                break
    return keep


def _plist_root(path):
    '''The root object of a plist, with an NSKeyedArchiver graph walked back into plain values.'''
    try:
        with open(path, 'rb') as handle:
            plist = plistlib.load(handle)
    except (plistlib.InvalidFileException, OSError, ValueError) as error:
        logfunc(f'Garmin Connect: could not read {os.path.basename(path)}: {error}')
        return None
    if not isinstance(plist, dict) or '$objects' not in plist:
        return plist
    objects = plist['$objects']

    def walk(node, depth=0):
        if depth > 24:
            return None
        if isinstance(node, plistlib.UID):
            return walk(objects[node.data], depth + 1)
        if isinstance(node, dict):
            if 'NS.keys' in node and 'NS.objects' in node:
                return {walk(k, depth + 1): walk(v, depth + 1)
                        for k, v in zip(node['NS.keys'], node['NS.objects'])}
            if 'NS.objects' in node:
                return [walk(v, depth + 1) for v in node['NS.objects']]
            if 'NS.time' in node:
                return {'NS.time': node['NS.time']}
            if 'NS.data' in node and not set(node) - {'NS.data', '$class'}:
                # An archived NSData, which is how the image cache stores a transformed copy.
                # A richer object that merely carries an NS.data field, such as an archived
                # time zone, keeps its other fields and is walked as a mapping.
                return node['NS.data']
            return {k: walk(v, depth + 1) for k, v in node.items() if k != '$class'}
        if isinstance(node, list):
            return [walk(v, depth + 1) for v in node]
        return node

    try:
        return walk(plist.get('$top', {}).get('root'))
    except (IndexError, KeyError, TypeError) as error:
        logfunc(f'Garmin Connect: could not walk {os.path.basename(path)}: {error}')
        return None


def _json_root(path):
    '''Several of the caches archive a JSON document as bytes. Returns the decoded document.'''
    root = _plist_root(path)
    if isinstance(root, bytes):
        try:
            return json.loads(root.decode('utf8', 'replace'))
        except ValueError:
            return None
    if isinstance(root, (dict, list)):
        return root
    if isinstance(root, str):
        try:
            return json.loads(root)
        except ValueError:
            return root
    return None


def _raw_json(path):
    '''A cache written as plain JSON rather than as a plist.'''
    try:
        with open(path, 'rb') as handle:
            return json.loads(handle.read().decode('utf8', 'replace'))
    except (OSError, ValueError):
        return None


def _utc(value):
    '''A Cocoa absolute time to an aware UTC datetime.'''
    seconds = value.get('NS.time') if isinstance(value, dict) else value
    if not isinstance(seconds, (int, float)):
        return ''
    try:
        return _COCOA_EPOCH_UTC + timedelta(seconds=seconds)
    except (OverflowError, ValueError):
        return ''


def _local_text(value):
    '''A Cocoa value that carries a device-local wall clock, rendered as text.

    The app writes these alongside a GMT value that is the same moment, so reading one as
    though it were UTC prints the reading the device showed. No instant is asserted.
    '''
    seconds = value.get('NS.time') if isinstance(value, dict) else value
    if not isinstance(seconds, (int, float)):
        return ''
    try:
        return (_COCOA_EPOCH_NAIVE + timedelta(seconds=seconds)).strftime('%Y-%m-%d %H:%M:%S')
    except (OverflowError, ValueError):
        return ''


def _date_text(value):
    '''The calendar day of a Cocoa value that carries a device-local wall clock.'''
    text = _local_text(value)
    return text[:10] if text else ''


def _stored(value):
    '''A stored value as text, with the archiver's null and absent read the same way.'''
    if value in (None, '$null'):
        return ''
    return value


def _decode_polyline(encoded):
    '''Google encoded polyline to a list of (latitude, longitude).'''
    points = []
    latitude = longitude = index = 0
    while index < len(encoded):
        for axis in range(2):
            shift = result = 0
            while index < len(encoded):
                byte = ord(encoded[index]) - 63
                index += 1
                result |= (byte & 0x1f) << shift
                shift += 5
                if byte < 0x20:
                    break
            delta = ~(result >> 1) if result & 1 else result >> 1
            if axis == 0:
                latitude += delta
            else:
                longitude += delta
        points.append((latitude / 1e5, longitude / 1e5))
    return points


def _named(garmin_files, names):
    '''Matched files whose basename is one of <names>, as (container, path).'''
    if isinstance(names, str):
        names = (names,)
    return [(container, path) for container, path in garmin_files
            if os.path.basename(path) in names]


def _in_directory(garmin_files, directory):
    '''Matched files sitting directly inside a directory of the given name.'''
    return [(container, path) for container, path in garmin_files
            if os.path.basename(os.path.dirname(path)) == directory]


def _calendar_items(garmin_files):
    '''(container, source path, item) for every entry of the calendar cache.'''
    items = []
    for container, path in _named(garmin_files, _CALENDAR):
        root = _plist_root(path)
        if not isinstance(root, dict):
            continue
        for group in root.values():
            if not isinstance(group, dict):
                continue
            for item in group.get('calendarItems') or []:
                if isinstance(item, dict):
                    items.append((container, path, item))
    return items


def _tracks(garmin_files):
    '''{(container, activity id): decoded track document} from the polyline cache.'''
    tracks = {}
    for container, path in _in_directory(garmin_files, _POLYLINE_DIR):
        document = _json_root(path)
        if not isinstance(document, dict):
            continue
        activity = document.get('activityId')
        if activity is None:
            activity = os.path.basename(path)
        tracks[(container, str(activity))] = (path, document)
    return tracks


@artifact_processor
def garmin_ios_activities(context):
    files_found = context.get_files_found()
    containers = _containers(files_found)
    garmin_files = _garmin_files(files_found, containers)
    tracks = _tracks(garmin_files)
    data_list = []
    sources = []

    for container, path, item in _calendar_items(garmin_files):
        title = _stored(item.get('title'))
        if not title:
            continue
        activity = item.get('itemId')
        source, document = tracks.get((container, str(activity)), ('', {}))
        points = _decode_polyline(document.get('encodedSamples') or '') if document else []
        if path not in sources:
            sources.append(path)
        if source and source not in sources:
            sources.append(source)
        data_list.append((
            _local_text(item.get('startTimestampLocal')),
            _date_text(item.get('date')),
            title,
            document.get('startLat', '') if document else '',
            document.get('startLon', '') if document else '',
            document.get('endLat', '') if document else '',
            document.get('endLon', '') if document else '',
            _stored(item.get('duration')),
            _stored(item.get('distance')),
            _stored(item.get('calories')),
            _stored(item.get('averageHR')),
            _stored(item.get('maxSpeed')),
            _stored(item.get('lapCount')),
            _stored(item.get('activityTypeId')),
            _stored(item.get('sportTypeKey')),
            _stored(item.get('itemType')),
            _stored(activity),
            document.get('numberOfPoints', '') if document else '',
            len(points),
            _utc(item.get('creationDate')),
        ))

    data_headers = (
        'Start Time (Device Local)',
        'Calendar Date',
        'Activity Name',
        'Latitude',
        'Longitude',
        'End Latitude',
        'End Longitude',
        'Duration (Seconds)',
        'Distance (Meters)',
        'Calories',
        'Average Heart Rate',
        'Max Speed (Meters Per Second)',
        'Lap Count',
        'Activity Type ID (as stored)',
        'Sport Type Key (as stored)',
        'Item Type (as stored)',
        'Activity ID',
        'Track Points Recorded',
        'Track Points Cached',
        ('Cache Record Written', 'datetime'),
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def garmin_ios_activity_tracks(context):
    files_found = context.get_files_found()
    containers = _containers(files_found)
    garmin_files = _garmin_files(files_found, containers)
    tracks = _tracks(garmin_files)
    names = {}
    for container, _path, item in _calendar_items(garmin_files):
        title = _stored(item.get('title'))
        if title:
            names[(container, str(item.get('itemId')))] = (
                title, _local_text(item.get('startTimestampLocal')))
    data_list = []
    sources = []

    for (container, activity), (path, document) in sorted(tracks.items()):
        title, started = names.get((container, activity), ('', ''))
        points = _decode_polyline(document.get('encodedSamples') or '')
        if points and path not in sources:
            sources.append(path)
        for number, (latitude, longitude) in enumerate(points, start=1):
            data_list.append((activity, title, started, number, latitude, longitude))

    data_headers = (
        'Activity ID',
        'Activity Name',
        'Activity Start (Device Local)',
        'Point Number',
        'Latitude',
        'Longitude',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def garmin_ios_daily_metrics(context):
    files_found = context.get_files_found()
    containers = _containers(files_found)
    garmin_files = _garmin_files(files_found, containers)
    data_list = []
    sources = []

    for _container, path, item in _calendar_items(garmin_files):
        if _stored(item.get('title')):
            continue
        if path not in sources:
            sources.append(path)
        data_list.append((
            _date_text(item.get('date')),
            _utc(item.get('startTimestampGMT')),
            _local_text(item.get('startTimestampLocal')),
            _utc(item.get('endTimestampGMT')),
            _local_text(item.get('endTimestampLocal')),
            _stored(item.get('step')),
            _stored(item.get('stepGoal')),
            _stored(item.get('sleepDuration')),
            _stored(item.get('minHeartRate')),
            _stored(item.get('maxHeartRate')),
            _stored(item.get('averageStressLevel')),
            _stored(item.get('maxStressLevel')),
            _stored(item.get('bodyBatteryCharged')),
            _stored(item.get('bodyBatteryDrained')),
            _stored(item.get('duration')),
            _stored(item.get('moderateIntensityMinutes')),
            _stored(item.get('vigorousIntensityMinutes')),
            _stored(item.get('deviceId')),
            _stored(item.get('itemType')),
            _utc(item.get('creationDate')),
        ))

    data_headers = (
        'Calendar Date',
        ('Start Time (UTC)', 'datetime'),
        'Start Time (Device Local)',
        ('End Time (UTC)', 'datetime'),
        'End Time (Device Local)',
        'Steps',
        'Step Goal',
        'Sleep Duration (Seconds)',
        'Minimum Heart Rate',
        'Maximum Heart Rate',
        'Average Stress Level',
        'Maximum Stress Level',
        'Body Battery Charged',
        'Body Battery Drained',
        'Duration (Seconds)',
        'Moderate Intensity Minutes',
        'Vigorous Intensity Minutes',
        'Device ID',
        'Item Type (as stored)',
        ('Cache Record Written', 'datetime'),
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def garmin_ios_daily_heart_rate(context):
    files_found = context.get_files_found()
    containers = _containers(files_found)
    garmin_files = _garmin_files(files_found, containers)
    data_list = []
    sources = []

    for _container, path in _named(garmin_files, _MOVE_IQ):
        root = _plist_root(path)
        if not isinstance(root, dict):
            continue
        for day, record in sorted(root.items()):
            if not isinstance(record, dict):
                continue
            detail = ((record.get('allDayHRData') or {}) if isinstance(record.get('allDayHRData'), dict) else {})
            detail = detail.get('hrDetail') if isinstance(detail.get('hrDetail'), dict) else {}
            zones = record.get('heartRateZoneData') if isinstance(record.get('heartRateZoneData'), dict) else {}
            if not detail and not zones:
                continue
            if path not in sources:
                sources.append(path)
            data_list.append((
                _utc(detail.get('startTimestampGMT')),
                day,
                _local_text(detail.get('startTimestampLocal')),
                _utc(detail.get('endTimestampGMT')),
                _stored(detail.get('restingHeartRate')),
                _stored(detail.get('minHeartRate')),
                _stored(detail.get('maxHeartRate')),
                _stored(zones.get('restingHeartRateUsed')),
                _stored(zones.get('maxHeartRateUsed')),
                _stored(zones.get('zone1Floor')),
                _stored(zones.get('zone2Floor')),
                _stored(zones.get('zone3Floor')),
                _stored(zones.get('zone4Floor')),
                _stored(zones.get('zone5Floor')),
                _stored(zones.get('trainingMethod')),
                _stored(zones.get('sport')),
                _stored(detail.get('userProfileId')),
                _stored(detail.get('deviceID')),
            ))

    data_headers = (
        ('Day Start (UTC)', 'datetime'),
        'Calendar Date',
        'Day Start (Device Local)',
        ('Day End (UTC)', 'datetime'),
        'Resting Heart Rate',
        'Minimum Heart Rate',
        'Maximum Heart Rate',
        'Resting Heart Rate Used',
        'Maximum Heart Rate Used',
        'Zone 1 Floor',
        'Zone 2 Floor',
        'Zone 3 Floor',
        'Zone 4 Floor',
        'Zone 5 Floor',
        'Training Method (as stored)',
        'Sport (as stored)',
        'User Profile ID',
        'Device ID',
    )
    return data_headers, data_list, '\n'.join(sources)


def _move_iq_days(garmin_files):
    '''(source path, calendar day, day record) for every day in the Move IQ store.'''
    days = []
    for _container, path in _named(garmin_files, _MOVE_IQ):
        root = _plist_root(path)
        if not isinstance(root, dict):
            continue
        for day, record in sorted(root.items()):
            if isinstance(record, dict) and _DAY.match(str(day)):
                days.append((path, str(day), record))
    return days


@artifact_processor
def garmin_ios_heart_rate_samples(context):
    files_found = context.get_files_found()
    containers = _containers(files_found)
    garmin_files = _garmin_files(files_found, containers)
    data_list = []
    sources = []

    for path, day, record in _move_iq_days(garmin_files):
        heart = record.get('allDayHRData') if isinstance(record.get('allDayHRData'), dict) else {}
        detail = heart.get('hrDetail') if isinstance(heart.get('hrDetail'), dict) else {}
        for sample in detail.get('heartRateArray') or []:
            if not isinstance(sample, dict):
                continue
            if path not in sources:
                sources.append(path)
            data_list.append((
                _utc(sample.get('startGMT')),
                day,
                _stored(sample.get('value')),
                _stored(detail.get('userProfileId')),
            ))

    data_headers = (
        ('Sample Time (UTC)', 'datetime'),
        'Calendar Date',
        'Heart Rate (as stored)',
        'User Profile ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def garmin_ios_movement_samples(context):
    files_found = context.get_files_found()
    containers = _containers(files_found)
    garmin_files = _garmin_files(files_found, containers)
    data_list = []
    sources = []

    for path, day, record in _move_iq_days(garmin_files):
        detail = record.get('movementDetail') if isinstance(record.get('movementDetail'), dict) else {}
        for sample in detail.get('movementArray') or []:
            if not isinstance(sample, dict):
                continue
            if path not in sources:
                sources.append(path)
            data_list.append((
                _utc(sample.get('startGMT')),
                day,
                _stored(sample.get('value')),
                _stored(detail.get('userProfileId')),
            ))

    data_headers = (
        ('Sample Time (UTC)', 'datetime'),
        'Calendar Date',
        'Movement Value (as stored)',
        'User Profile ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def garmin_ios_sleep_events(context):
    files_found = context.get_files_found()
    containers = _containers(files_found)
    garmin_files = _garmin_files(files_found, containers)
    data_list = []
    sources = []

    for path, day, record in _move_iq_days(garmin_files):
        heart = record.get('allDayHRData') if isinstance(record.get('allDayHRData'), dict) else {}
        detail = heart.get('hrDetail') if isinstance(heart.get('hrDetail'), dict) else {}
        for event in heart.get('sleepEventList') or []:
            if not isinstance(event, dict):
                continue
            if path not in sources:
                sources.append(path)
            data_list.append((
                _utc(event.get('timeStamp')),
                day,
                _stored(event.get('type')),
                _stored(detail.get('userProfileId')),
            ))

    data_headers = (
        ('Event Time (UTC)', 'datetime'),
        'Calendar Date Of The Record',
        'Event Type (as stored)',
        'User Profile ID',
    )
    return data_headers, data_list, '\n'.join(sources)



def _device_records(garmin_files):
    '''(container, source path, record) for every device record across the device caches.'''
    records = []
    for container, path in _named(garmin_files, (_PAIRED,) + _REGISTERED):
        document = _json_root(path)
        if isinstance(document, list):
            # The paired store is written as a flat [id, record, id, record, ...] list.
            if document and isinstance(document[0], int):
                for index in range(1, len(document), 2):
                    if isinstance(document[index], dict):
                        records.append((container, path, document[index]))
            else:
                for entry in document:
                    if isinstance(entry, dict):
                        records.append((container, path, entry))
        elif isinstance(document, dict):
            records.append((container, path, document))
    return records


def _first(record, *keys):
    '''The first key a record holds, across the spellings the app has used.'''
    for key in keys:
        if isinstance(record, dict) and record.get(key) not in (None, '$null', ''):
            return record[key]
    return ''


@artifact_processor
def garmin_ios_devices(context):
    files_found = context.get_files_found()
    containers = _containers(files_found)
    garmin_files = _garmin_files(files_found, containers)
    data_list = []
    sources = []

    wallets = {}
    for container, path in _named(garmin_files, _WALLET_METADATA):
        document = _raw_json(path) or _json_root(path)
        if isinstance(document, list) and len(document) >= 2 and isinstance(document[1], dict):
            wallets[(container, str(document[0]))] = (path, document[1])
    cards = {}
    for container, path in _named(garmin_files, _WALLET_ITEMS):
        document = _raw_json(path) or _json_root(path)
        if isinstance(document, list) and len(document) >= 2 and isinstance(document[1], list):
            cards[(container, str(document[0]))] = (path, document[1])

    for container, path, record in _device_records(garmin_files):
        data = record.get('deviceData') if isinstance(record.get('deviceData'), dict) else record
        unit = _first(data, 'unitID', 'device_id', 'deviceId', 'unitId')
        if unit == '':
            unit = _first(record, 'unitID', 'device_id', 'deviceId', 'unitId')
        wallet_path, wallet = wallets.get((container, str(unit)), ('', {}))
        card_path, card_list = cards.get((container, str(unit)), ('', None))
        if path not in sources:
            sources.append(path)
        for extra in (wallet_path, card_path):
            if extra and extra not in sources:
                sources.append(extra)
        chip = wallet.get('nfcInfo', {}).get('nfcChipType', '') if isinstance(wallet.get('nfcInfo'), dict) else ''
        data_list.append((
            _utc(record.get('lastConnected')),
            _stored(unit),
            _first(data, 'productName', 'displayName', 'display_name', 'friendlyName',
                   'productDisplayName', 'full_product_display_name'),
            _first(data, 'friendlyName'),
            _stored(_first(data, 'softwareVersion', 'firmwareVersion', 'firmware_version')),
            _stored(_first(data, 'productNumber', 'product_number')),
            _stored(_first(data, 'partNumber', 'part_number')),
            _stored(_first(data, 'productSku', 'product_Sku')),
            _stored(_first(data, 'bluetoothLowEnergyIdentifier')),
            _stored(_first(data, 'applicationKey', 'application_key')),
            _stored(chip),
            '' if card_list is None else len(card_list),
            os.path.basename(path),
        ))

    data_headers = (
        ('Last Connected', 'datetime'),
        'Unit ID',
        'Product Name',
        'Friendly Name',
        'Firmware Version (as stored)',
        'Product Number',
        'Part Number',
        'Product SKU',
        'Bluetooth Low Energy Identifier',
        'Application Key',
        'NFC Chip Type (as stored)',
        'Payment Cards Cached',
        'Cache File',
    )
    return data_headers, data_list, '\n'.join(sources)


def _group_profile(garmin_files):
    '''The account the app group preferences carry, with the file it came from.'''
    for _container, path in _named(garmin_files, _GROUP_PREFS):
        plist = get_plist_file_content(path)
        if not isinstance(plist, dict):
            continue
        profile = {}
        for key in (_PROFILE_KEY, _CUSTOMER_KEY):
            value = plist.get(key)
            if isinstance(value, bytes):
                try:
                    value = json.loads(value.decode('utf8', 'replace'))
                except ValueError:
                    value = None
            if isinstance(value, dict):
                for name, item in value.items():
                    profile.setdefault(name, item)
        profile['GCMAppVersion'] = plist.get('GCMAppVersion', '')
        profile['AuthenticationDomain'] = plist.get(
            'com.garmin.MobileAuthentication.AuthenticationDomain', '')
        return path, profile
    return '', {}


@artifact_processor
def garmin_ios_account(context):
    files_found = context.get_files_found()
    containers = _containers(files_found)
    garmin_files = _garmin_files(files_found, containers)
    data_list = []
    sources = []
    group_path, group = _group_profile(garmin_files)

    for container in sorted(set(c for c, _ in garmin_files)):
        inside = [(c, p) for c, p in garmin_files if c == container]
        accounts = {}
        for _c, path in inside:
            parts = path.split('/Documents/users/')
            if len(parts) == 2 and '/' in parts[1]:
                accounts.setdefault(parts[1].split('/')[0], {})[os.path.basename(path)] = path
        settings = {}
        personal = {}
        last_login = ''
        for _c, path in inside:
            name = os.path.basename(path)
            if name == _USER_SETTINGS:
                root = _plist_root(path)
                if isinstance(root, dict):
                    settings = root
                    if path not in sources:
                        sources.append(path)
            elif name == _PERSONAL:
                root = _plist_root(path)
                if isinstance(root, dict):
                    personal = root
                    if path not in sources:
                        sources.append(path)
            elif name == _LAST_LOGIN:
                last_login = _utc(_plist_root(path))
                if path not in sources:
                    sources.append(path)
        zone = personal.get('timeZone')
        zone_name = zone.get('NS.name', '') if isinstance(zone, dict) else ''
        if not accounts and not settings and not personal and not last_login:
            # The shared app group container carries no account of its own.
            continue
        if not accounts:
            accounts = {'': {}}
        for account, files in sorted(accounts.items()):
            location = {}
            incident = ''
            for name, path in sorted(files.items()):
                if name == 'GCMUserSettingsUserLocationKey':
                    document = _json_root(path)
                    if isinstance(document, dict):
                        location = document
                        if path not in sources:
                            sources.append(path)
                elif name == 'incident_detection_name':
                    value = _plist_root(path)
                    incident = _stored(value) if isinstance(value, str) else ''
                    if path not in sources:
                        sources.append(path)
            # The profile caches sit at container level rather than under an account
            # directory, so they are reported only on the account the app recorded a
            # user profile id for. The app also keeps a directory named anonymous,
            # which carries no user profile id.
            signed_in = bool(location)
            profile = settings if signed_in else {}
            # The group preferences sit in a different container, so they are attached only
            # when the profile id they carry is the one this account directory records.
            same = signed_in and str(group.get('profileId', '')) == str(
                location.get('userProfileId', ''))
            held = group if same else {}
            if same and group_path and group_path not in sources:
                sources.append(group_path)
            picture = ''
            if same and isinstance(group.get('imageData'), str):
                try:
                    raw = base64.b64decode(group['imageData'], validate=True)
                except (ValueError, TypeError):
                    raw = b''
                if raw.startswith(_IMAGE_SIGNATURES):
                    picture = check_in_embedded_media(group_path, raw, 'garmin_profile_image')
            data_list.append((
                account,
                _stored(location.get('userProfileId')) or (
                    _stored(settings.get('userId')) if signed_in else ''),
                _stored(location.get('countryCode')),
                _stored(location.get('countryCodeVerified')),
                _stored(location.get('countryCodeVerifiedTimestamp')),
                last_login if signed_in else '',
                incident,
                _utc(profile.get('birthDate')),
                _stored(profile.get('height')),
                _stored(profile.get('weight')),
                _stored(profile.get('gender')) or (
                    _stored(personal.get('gender')) if signed_in else ''),
                _stored(profile.get('handedness')),
                _stored(profile.get('vo2MaxRunning')),
                _stored(profile.get('vo2MaxCycling')),
                _stored(profile.get('wakeTime')),
                _stored(profile.get('sleepTime')),
                _stored(profile.get('timeFormat')),
                _stored(profile.get('unitsMeasure')),
                _stored(profile.get('activityLevel')),
                zone_name if signed_in else '',
                _stored(held.get('fullName')),
                _stored(held.get('displayName')),
                _stored(held.get('garminGUID')),
                _stored(held.get('AuthenticationDomain')),
                _stored(held.get('GCMAppVersion')),
                picture,
            ))

    data_headers = (
        'Account',
        'User Profile ID',
        'Country Code',
        'Country Code Verified',
        'Country Code Verified Timestamp (as stored)',
        ('Last Logged In', 'datetime'),
        'Incident Detection Contact Name',
        ('Birth Date (UTC, as stored)', 'datetime'),
        'Height (Centimeters)',
        'Weight (Grams)',
        'Gender (as stored)',
        'Handedness (as stored)',
        'VO2 Max Running',
        'VO2 Max Cycling',
        'Wake Time (Seconds After Midnight)',
        'Sleep Time (Seconds After Midnight)',
        'Time Format (as stored)',
        'Units Of Measure (as stored)',
        'Activity Level (as stored)',
        'Profile Time Zone',
        'Full Name',
        'Display Name',
        'Garmin GUID',
        'Authentication Domain',
        'App Version',
        ('Profile Image', 'media'),
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def garmin_ios_cached_images(context):
    files_found = context.get_files_found()
    containers = _containers(files_found)
    garmin_files = _garmin_files(files_found, containers)
    data_list = []
    sources = []

    for _container, path in _in_directory(garmin_files, _IMAGE_CACHE_DIR):
        name = os.path.basename(path)
        url = unquote(name)
        data = None
        try:
            with open(path, 'rb') as handle:
                head = handle.read(8)
        except OSError as error:
            logfunc(f'Garmin Connect: could not read a cached image: {error}')
            continue
        rendered = ''
        if head.startswith(_IMAGE_SIGNATURES):
            rendered = check_in_media(path, name)
        else:
            root = _plist_root(path)
            data = root if isinstance(root, bytes) else None
            if data and data.startswith(_IMAGE_SIGNATURES):
                rendered = check_in_embedded_media(path, data, name)
        if not rendered:
            continue
        if path not in sources:
            sources.append(path)
        match = _PROFILE_IMAGE_URL.search(url)
        if match:
            kind = 'Profile image'
        elif _BADGE_URL.search(url):
            kind = 'Badge image'
        elif _PRODUCT_IMAGE_URL.search(url):
            kind = 'Product image'
        else:
            kind = 'Other'
        data_list.append((
            rendered,
            kind,
            match.group(1) if match else '',
            url,
            os.path.getsize(path),
        ))

    data_headers = (
        ('Image', 'media'),
        'Image Kind',
        'Garmin User ID In Address',
        'Address',
        'Cache File Size (Bytes)',
    )
    return data_headers, data_list, '\n'.join(sources)
