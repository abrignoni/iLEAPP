__artifacts_v2__ = {
    "chrome_sync_sessions": {
        "name": "Chrome Sync - Synced Tabs",
        "description": "Pages in the tabs Chromium-based browsers synced, from this browser and from other sync clients on the account, with the address, title, navigation time and the name of the device the tab belongs to.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-30",
        "last_update_date": "2026-10-30",
        "requirements": "none",
        "category": "Chrome Sync",
        "notes": "Reads the Sync Data/LevelDB folder of each profile under an app container's Library/Application Support: Google/Chrome/<profile> (com.google.chrome.ios, whose profile folder is Default on the tested images except dexter_ios18, where it is named by a UUID), Microsoft/Edge/Default and Microsoft/Edge/Default-AAD (com.microsoft.msedge), Chromium/Default (com.brave.ios.browser) and, directly under Application Support, the Google app's (com.google.GoogleMobile). The pattern matches a Sync Data folder at any depth under Application Support, so another app's store would be read too. Bundle ID is the MCMMetadataIdentifier in the container's .com.apple.mobile_container_manager.metadata.plist, and is blank when that plist is not found; the folder names inside the container are not used to name the app. In an iTunes backup it is the container folder name, which the seeker names by bundle identifier; no iTunes backup was run for these artifacts, so that case is covered only by a unit test (admin/test/scripts/test_chrome_sync_data.py). On the tested images every store resolved to one of the four identifiers above. Source Folder names the store a row came from. Each folder is read once as its own store, so Edge's two profiles, or two stores of one account in different apps, are never merged, and a device listed by two stores is reported once per store. Read with the vendored ccl_leveldb through scripts/chromium_sync_data.py, ported from ALEAPP (https://github.com/abrignoni/ALEAPP/blob/09dd5c833e2110bf5b8f88a729b0018f2a67f2e7/scripts/chromium_sync_data.py), which ported it from DLEAPP. Chromium keeps each sync data type's records under the keys <type>-dt-<storage key>, with A- in front for account storage, and the type's sync state under <type>-GlobalMetadata (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/model/blocking_data_type_store_impl.cc#L26-L63 and https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/model/blocking_data_type_store_impl.cc#L172-L183); no tested store held an account storage data record, and 3 held an account storage sync state record, for reading_list. LevelDB numbers each write and orders the versions of a key by decreasing sequence number, the newest first (https://github.com/google/leveldb/blob/bb74ef739973a70ca9f0d90788a1da89b788c0ad/db/dbformat.cc#L47-L63). Only the newest version of each key is read, and a key whose newest version is a deletion is not reported; earlier versions are not reported by any artifact, and the run log counts them for each folder. Across the 21 stores on the tested images that left 616 of 8,994 records as the newest version of a key, 156 of them deletions. 11 of the 21 stores held one record and no sync data: _mts_schema_descriptor, the schema version record Chromium's data type store writes (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/model/data_type_store_backend.h#L103-L104, https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/model/data_type_store_backend.cc#L342-L351). They were the Brave stores on hc_ios18_7, hc_ios26, hickman_ios15 and iphone11_ios17, both Edge profiles on hickman_ios15, Edge's Default-AAD on iphone11_ios17, Chrome's on cookbook_ios1751 and the Google app's on hc_ios17_2, hc_ios26 and iphone12_ios18. Values are decoded with the field numbers and types of the messages Chromium publishes under components/sync/protocol at commit 5926523bcfedb77ba2533ace1dd93b477673f72a, transcribed into scripts/chromium_sync_data.py, not by guessing at field types; a record that does not decode is not reported and the run log names its store and data type; none failed to decode on the tested images. Not read: the -md- metadata records and the data types other than device_info and sessions. Of those, the tested stores held preferences, priority_preferences and user_consent data records. No tested store held a send_tab_to_self data record, so ALEAPP's Send Tab To Self artifact is not ported; a sample with one would close that gap. One row per navigation entry in each live sessions record that holds a SessionTab (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/session_specifics.proto#L69-L91), whose entries are TabNavigation messages (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/tab_navigation.proto#L19-L51); the 174 tested rows came from 71 tab records. URL is virtual_url, the URL as displayed to the user (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/tab_navigation.proto#L20-L24); Title and Referrer are title and referrer decoded as UTF-8 and HTTP Status is http_status_code as stored. HTTP Status held 0 on all 160 tested rows whose This Device is Yes and 200 on the 14 rows from another client. Transition is page_transition, the core transition type, named with sync_enums.proto (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/sync_enums.proto#L63-L74); From Address Bar is navigation_from_address_bar (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/tab_navigation.proto#L40-L41). Navigation Time is timestamp_msec, described as when the navigation last occurred, in client time, and as able to refresh when the user goes back or forward (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/tab_navigation.proto#L35-L37), written with TimeToProtoTime (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync_sessions/synced_session.cc#L136), milliseconds since 1970-01-01 UTC (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/base/time.cc#L14-L16); it was not compared with the browser's History on these images. Navigation Index is the entry's position in the tab and Current Entry is Yes on the entry at current_navigation_index (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/session_specifics.proto#L77-L79). Tab Last Active is last_active_time_unix_epoch_millis (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/session_specifics.proto#L89-L91), blank on 84 of the 174 tested rows, every row of abe_ios16, hickman_ios15, iphone11_ios17 and magnet_ios16. Pinned is pinned shown as Yes or No, and Pinned held No on all 174 tested rows; Tab ID and Window ID are tab_id and window_id as stored. Device Name is the client_name of the session header with the same session tag, or of the device with that Cache GUID when no header is stored; it held a value on every tested row. Session Tag is the record's session_tag, which the proto describes as sync's cache GUID since M89 (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/session_specifics.proto#L21-L24). This Device is Yes when the session tag equals the cache_guid in the sessions sync state, the GUID of the sync client that wrote the store (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/data_type_state.proto#L58-L64), No when it equals the Cache GUID of another device the store lists, and blank when the store records no cache_guid or the tag matches no listed GUID. On the tested rows it was Yes on 160 and No on 14 and never blank. A row whose This Device is No came from another sync client on the account; it is not a page opened in this app. The 14 No rows, all on magnet_ios16, came from a client whose device_info lists Device Type TYPE_WIN (1) and no OS Type. The 3 rows on iphone11_ios17 came from Edge; every other tested row came from Chrome.",
        "paths": ('*/Library/Application Support/*Sync Data/LevelDB/*',),
        "output_types": "standard",
        "artifact_icon": "cloud",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 45 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows (no Sync Data folder matched)",
            "belkactf6": "iOS 16.3 | 0 rows (no Sync Data folder matched)",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows (no live tab record in the Sync Data folders)",
            "ctf2020_ios12": "iOS 12.4 | 0 rows (no Sync Data folder matched)",
            "dexter_ios18": "iOS 18.3.2 | 68 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows (no Sync Data folder matched)",
            "felix23_ios16": "iOS 16.5 | 0 rows (no Sync Data folder matched)",
            "felix_ios17": "iOS 17.6.1 | 0 rows (no Sync Data folder matched)",
            "fsfull002_ios17": "iOS 17.1 | 0 rows (no Sync Data folder matched)",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows (no live tab record in the Sync Data folders)",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows (no live tab record in the Sync Data folders)",
            "hc_ios26": "iOS 26.5.2 | 0 rows (no live tab record in the Sync Data folders)",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows (no live tab record in the Sync Data folders)",
            "hickman_ios13": "iOS 13.3.1 | 0 rows (no Sync Data folder matched)",
            "hickman_ios14": "iOS 14.3 | 0 rows (no Sync Data folder matched)",
            "hickman_ios15": "iOS 15.3.1 | 4 rows",
            "iphone11_ios17": "iOS 17.3 | 3 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows (no live tab record in the Sync Data folders)",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows (no Sync Data folder matched)",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows (no Sync Data folder matched)",
            "jess_ios15": "iOS 15.0.2 | 0 rows (no Sync Data folder matched)",
            "magnet_ios16": "iOS 16.1.1 | 32 rows",
            "otto_ios17": "iOS 17.5.1 | 22 rows",
        },
    },
    "chrome_sync_devices": {
        "name": "Chrome Sync - Session Devices",
        "description": "The session header each device synced to Chromium-based browsers: the device name and form factor and how many windows and tabs it listed.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-30",
        "last_update_date": "2026-10-30",
        "requirements": "none",
        "category": "Chrome Sync",
        "notes": "Reads the Sync Data/LevelDB folder of each profile under an app container's Library/Application Support: Google/Chrome/<profile> (com.google.chrome.ios, whose profile folder is Default on the tested images except dexter_ios18, where it is named by a UUID), Microsoft/Edge/Default and Microsoft/Edge/Default-AAD (com.microsoft.msedge), Chromium/Default (com.brave.ios.browser) and, directly under Application Support, the Google app's (com.google.GoogleMobile). The pattern matches a Sync Data folder at any depth under Application Support, so another app's store would be read too. Bundle ID is the MCMMetadataIdentifier in the container's .com.apple.mobile_container_manager.metadata.plist, and is blank when that plist is not found; the folder names inside the container are not used to name the app. In an iTunes backup it is the container folder name, which the seeker names by bundle identifier; no iTunes backup was run for these artifacts, so that case is covered only by a unit test (admin/test/scripts/test_chrome_sync_data.py). On the tested images every store resolved to one of the four identifiers above. Source Folder names the store a row came from. Each folder is read once as its own store, so Edge's two profiles, or two stores of one account in different apps, are never merged, and a device listed by two stores is reported once per store. Read with the vendored ccl_leveldb through scripts/chromium_sync_data.py, ported from ALEAPP (https://github.com/abrignoni/ALEAPP/blob/09dd5c833e2110bf5b8f88a729b0018f2a67f2e7/scripts/chromium_sync_data.py), which ported it from DLEAPP. Chromium keeps each sync data type's records under the keys <type>-dt-<storage key>, with A- in front for account storage, and the type's sync state under <type>-GlobalMetadata (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/model/blocking_data_type_store_impl.cc#L26-L63 and https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/model/blocking_data_type_store_impl.cc#L172-L183); no tested store held an account storage data record, and 3 held an account storage sync state record, for reading_list. LevelDB numbers each write and orders the versions of a key by decreasing sequence number, the newest first (https://github.com/google/leveldb/blob/bb74ef739973a70ca9f0d90788a1da89b788c0ad/db/dbformat.cc#L47-L63). Only the newest version of each key is read, and a key whose newest version is a deletion is not reported; earlier versions are not reported by any artifact, and the run log counts them for each folder. Across the 21 stores on the tested images that left 616 of 8,994 records as the newest version of a key, 156 of them deletions. 11 of the 21 stores held one record and no sync data: _mts_schema_descriptor, the schema version record Chromium's data type store writes (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/model/data_type_store_backend.h#L103-L104, https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/model/data_type_store_backend.cc#L342-L351). They were the Brave stores on hc_ios18_7, hc_ios26, hickman_ios15 and iphone11_ios17, both Edge profiles on hickman_ios15, Edge's Default-AAD on iphone11_ios17, Chrome's on cookbook_ios1751 and the Google app's on hc_ios17_2, hc_ios26 and iphone12_ios18. Values are decoded with the field numbers and types of the messages Chromium publishes under components/sync/protocol at commit 5926523bcfedb77ba2533ace1dd93b477673f72a, transcribed into scripts/chromium_sync_data.py, not by guessing at field types; a record that does not decode is not reported and the run log names its store and data type; none failed to decode on the tested images. Not read: the -md- metadata records and the data types other than device_info and sessions. Of those, the tested stores held preferences, priority_preferences and user_consent data records. No tested store held a send_tab_to_self data record, so ALEAPP's Send Tab To Self artifact is not ported; a sample with one would close that gap. One row per live sessions record that holds a SessionHeader (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/session_specifics.proto#L21-L36 and https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/session_specifics.proto#L40-L56). Device Name is the header's client_name, Form Factor its device_form_factor and Device Type its deprecated device_type, named with sync_enums.proto (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/sync_enums.proto#L143-L177). Windows is the number of SessionWindow entries, Tabs Listed the number of tab ids they list, and Window Types the browser_type names of the windows (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/session_specifics.proto#L58-L66, https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/sync_enums.proto#L180-L186); every tested header listed at least one window. Session Start is session_start_time_unix_epoch_millis, which the proto says was introduced in M130 and is not populated for sessions started before it (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/session_specifics.proto#L41-L44); it was blank on 6 of the 7 tested rows, all but dexter_ios18's. Form Factor was blank on 3 of the 7, both magnet_ios16 headers and Edge's on iphone11_ios17. Session Tag is session_tag, sync's cache GUID since M89 (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/session_specifics.proto#L21-L24). This Device is Yes when the session tag equals the cache_guid in the sessions sync state (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/data_type_state.proto#L58-L64), No when it equals the Cache GUID of another device the store lists, and blank when the store records no cache_guid or the tag matches no listed GUID; on the tested rows it was Yes on 6 and No on 1, on magnet_ios16. The Google app's stores held no sessions record on the tested images. A device appears here because it synced a session to this account, not because it was used at the device this extraction came from.",
        "paths": ('*/Library/Application Support/*Sync Data/LevelDB/*',),
        "output_types": "standard",
        "artifact_icon": "monitor",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 1 row",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows (no Sync Data folder matched)",
            "belkactf6": "iOS 16.3 | 0 rows (no Sync Data folder matched)",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows (no live session header record in the Sync Data folders)",
            "ctf2020_ios12": "iOS 12.4 | 0 rows (no Sync Data folder matched)",
            "dexter_ios18": "iOS 18.3.2 | 1 row",
            "falken_ios26": "iOS 26.2.1 | 0 rows (no Sync Data folder matched)",
            "felix23_ios16": "iOS 16.5 | 0 rows (no Sync Data folder matched)",
            "felix_ios17": "iOS 17.6.1 | 0 rows (no Sync Data folder matched)",
            "fsfull002_ios17": "iOS 17.1 | 0 rows (no Sync Data folder matched)",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows (no live session header record in the Sync Data folders)",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows (no live session header record in the Sync Data folders)",
            "hc_ios26": "iOS 26.5.2 | 0 rows (no live session header record in the Sync Data folders)",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows (no live session header record in the Sync Data folders)",
            "hickman_ios13": "iOS 13.3.1 | 0 rows (no Sync Data folder matched)",
            "hickman_ios14": "iOS 14.3 | 0 rows (no Sync Data folder matched)",
            "hickman_ios15": "iOS 15.3.1 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 0 rows (no live session header record in the Sync Data folders)",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows (no Sync Data folder matched)",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows (no Sync Data folder matched)",
            "jess_ios15": "iOS 15.0.2 | 0 rows (no Sync Data folder matched)",
            "magnet_ios16": "iOS 16.1.1 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 1 row",
        },
    },
    "chrome_sync_device_info": {
        "name": "Chrome Sync - Device Info",
        "description": "Devices listed in the sync device information of Chromium-based browsers and the Google app, with the name, operating system, model, browser version and last update time each device recorded.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-30",
        "last_update_date": "2026-10-30",
        "requirements": "none",
        "category": "Chrome Sync",
        "notes": "Reads the Sync Data/LevelDB folder of each profile under an app container's Library/Application Support: Google/Chrome/<profile> (com.google.chrome.ios, whose profile folder is Default on the tested images except dexter_ios18, where it is named by a UUID), Microsoft/Edge/Default and Microsoft/Edge/Default-AAD (com.microsoft.msedge), Chromium/Default (com.brave.ios.browser) and, directly under Application Support, the Google app's (com.google.GoogleMobile). The pattern matches a Sync Data folder at any depth under Application Support, so another app's store would be read too. Bundle ID is the MCMMetadataIdentifier in the container's .com.apple.mobile_container_manager.metadata.plist, and is blank when that plist is not found; the folder names inside the container are not used to name the app. In an iTunes backup it is the container folder name, which the seeker names by bundle identifier; no iTunes backup was run for these artifacts, so that case is covered only by a unit test (admin/test/scripts/test_chrome_sync_data.py). On the tested images every store resolved to one of the four identifiers above. Source Folder names the store a row came from. Each folder is read once as its own store, so Edge's two profiles, or two stores of one account in different apps, are never merged, and a device listed by two stores is reported once per store. Read with the vendored ccl_leveldb through scripts/chromium_sync_data.py, ported from ALEAPP (https://github.com/abrignoni/ALEAPP/blob/09dd5c833e2110bf5b8f88a729b0018f2a67f2e7/scripts/chromium_sync_data.py), which ported it from DLEAPP. Chromium keeps each sync data type's records under the keys <type>-dt-<storage key>, with A- in front for account storage, and the type's sync state under <type>-GlobalMetadata (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/model/blocking_data_type_store_impl.cc#L26-L63 and https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/model/blocking_data_type_store_impl.cc#L172-L183); no tested store held an account storage data record, and 3 held an account storage sync state record, for reading_list. LevelDB numbers each write and orders the versions of a key by decreasing sequence number, the newest first (https://github.com/google/leveldb/blob/bb74ef739973a70ca9f0d90788a1da89b788c0ad/db/dbformat.cc#L47-L63). Only the newest version of each key is read, and a key whose newest version is a deletion is not reported; earlier versions are not reported by any artifact, and the run log counts them for each folder. Across the 21 stores on the tested images that left 616 of 8,994 records as the newest version of a key, 156 of them deletions. 11 of the 21 stores held one record and no sync data: _mts_schema_descriptor, the schema version record Chromium's data type store writes (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/model/data_type_store_backend.h#L103-L104, https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/model/data_type_store_backend.cc#L342-L351). They were the Brave stores on hc_ios18_7, hc_ios26, hickman_ios15 and iphone11_ios17, both Edge profiles on hickman_ios15, Edge's Default-AAD on iphone11_ios17, Chrome's on cookbook_ios1751 and the Google app's on hc_ios17_2, hc_ios26 and iphone12_ios18. Values are decoded with the field numbers and types of the messages Chromium publishes under components/sync/protocol at commit 5926523bcfedb77ba2533ace1dd93b477673f72a, transcribed into scripts/chromium_sync_data.py, not by guessing at field types; a record that does not decode is not reported and the run log names its store and data type; none failed to decode on the tested images. Not read: the -md- metadata records and the data types other than device_info and sessions. Of those, the tested stores held preferences, priority_preferences and user_consent data records. No tested store held a send_tab_to_self data record, so ALEAPP's Send Tab To Self artifact is not ported; a sample with one would close that gap. One row per live device_info record, a DeviceInfoSpecifics message (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L24-L110). The Google app's store is read here because, on the tested images, it held device_info records and no other sync data, and it lists devices the browsers' stores do not: on hexordia_ios1651 it is the only store with a device row, and on abe_ios16 it lists its own sync client, which Chrome's store does not. That client's own row, This Device Yes in the Google app's store, had a Sync User Agent without the word Chrome on all 3 images where it was present; on dexter_ios18 Chrome's store also lists that client, with This Device No, and the two stores there list the same 3 Cache GUIDs. Last Updated is last_updated_timestamp, which the proto describes as updated to the current time periodically and whenever another field changes (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L53-L57); the client sets it with TimeToProtoTime from its own clock (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync_device_info/device_info_sync_bridge.cc#L322-L325), milliseconds since 1970-01-01 UTC (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/base/time.cc#L14-L16). Device Name is client_name, a non-unique human readable name (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L28-L29); Cache GUID is cache_guid, which identifies a sync client (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L25-L26). This Device is Yes when the row's cache GUID equals the cache_guid in the type's sync state record, the GUID of the sync client that wrote the store (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/data_type_state.proto#L58-L64), No when it differs, and blank when the store records none; each of the 10 tested stores with device rows had one Yes row. OS Type, Form Factor and Device Type are os_type and device_form_factor (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L96-L100) and the deprecated device_type (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L31-L34), named with sync_enums.proto (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/sync_enums.proto#L143-L177); OS Type and Form Factor were blank on 3 of the 17 tested rows, both magnet_ios16 rows and the Google app's own row on abe_ios16. Chrome Version is chrome_version_info.version_number (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L91-L92, https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L263-L266), or the deprecated chrome_version when that is absent (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L40-L42). Manufacturer, Model, Sync User Agent and Signin Scoped Device ID are manufacturer, model, sync_user_agent and signin_scoped_device_id (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L67-L71, https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L36-L38, https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L49-L51); each held a value on every tested row. A row records that a device was listed in the app's sync data; it does not establish who used the device.",
        "paths": ('*/Library/Application Support/*Sync Data/LevelDB/*',),
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 3 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows (no Sync Data folder matched)",
            "belkactf6": "iOS 16.3 | 0 rows (no Sync Data folder matched)",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows (no live device_info record in the Sync Data folders)",
            "ctf2020_ios12": "iOS 12.4 | 0 rows (no Sync Data folder matched)",
            "dexter_ios18": "iOS 18.3.2 | 6 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows (no Sync Data folder matched)",
            "felix23_ios16": "iOS 16.5 | 0 rows (no Sync Data folder matched)",
            "felix_ios17": "iOS 17.6.1 | 0 rows (no Sync Data folder matched)",
            "fsfull002_ios17": "iOS 17.1 | 0 rows (no Sync Data folder matched)",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows (no live device_info record in the Sync Data folders)",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows (no live device_info record in the Sync Data folders)",
            "hc_ios26": "iOS 26.5.2 | 0 rows (no live device_info record in the Sync Data folders)",
            "hexordia_ios1651": "iOS 16.5.1 | 1 row",
            "hickman_ios13": "iOS 13.3.1 | 0 rows (no Sync Data folder matched)",
            "hickman_ios14": "iOS 14.3 | 0 rows (no Sync Data folder matched)",
            "hickman_ios15": "iOS 15.3.1 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows (no live device_info record in the Sync Data folders)",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows (no Sync Data folder matched)",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows (no Sync Data folder matched)",
            "jess_ios15": "iOS 15.0.2 | 0 rows (no Sync Data folder matched)",
            "magnet_ios16": "iOS 16.1.1 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 1 row",
        },
    },
}

import datetime
import os
import plistlib
import re

from scripts.chromium_sync_data import (BROWSER_TYPES, DEVICE_TYPES, FORM_FACTORS, OS_TYPES,
                                        PAGE_TRANSITIONS, ProtoError, SyncStore, decode,
                                        enum_label)
from scripts.context import Context
from scripts.ilapfuncs import artifact_processor, logfunc

# A store is the Sync Data/LevelDB folder of a profile, at Application Support/Sync Data
# (the Google app), Application Support/Chromium/<profile> (Brave),
# Application Support/Google/Chrome/<profile> or Application Support/Microsoft/Edge/<profile>.
_STORE = re.compile(r'(?:^|/)Library/Application Support/(?:[^/]+/)*Sync Data/LevelDB$')
_CONTAINER = re.compile(r'(?:^|/)Containers/Data/Application/([^/]+)(?=/)')
_UUID = re.compile(r'^[0-9A-Fa-f]{8}(?:-[0-9A-Fa-f]{4}){3}-[0-9A-Fa-f]{12}$')
_METADATA_NAME = '.com.apple.mobile_container_manager.metadata.plist'
_bundle_ids = {}


def _ms_time(value):
    """Milliseconds since 1970-01-01 UTC as a datetime; '' for missing, zero or out of range."""
    try:
        milliseconds = int(value)
    except (TypeError, ValueError):
        return ''
    if milliseconds <= 0:
        return ''
    try:
        return datetime.datetime.fromtimestamp(milliseconds / 1000, tz=datetime.timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _yes_no(value):
    if value is None:
        return ''
    return 'Yes' if value else 'No'


def _bundle_id(relative):
    """The bundle identifier of the app container holding a store, or ''.

    In an iTunes backup the seeker names the container folder by bundle identifier
    (search_files.get_root_path_from_domain), so the folder name is the identifier.
    In a full file system the folder is a UUID and the identifier is the
    MCMMetadataIdentifier of the container's metadata plist, found through the seeker
    once per container. Nothing is taken from the folder names inside the container.
    """
    container = _CONTAINER.search(relative)
    if not container:
        return ''
    name = container.group(1)
    if not _UUID.match(name):
        return name
    root = relative[:container.end()]
    key = (Context.get_data_folder(), root)
    if key not in _bundle_ids:
        identifier = ''
        try:
            found = Context.get_seeker().search(
                f'*/Containers/Data/Application/{name}/{_METADATA_NAME}')
        except ValueError:  # no seeker outside a run
            found = []
        for path in found:
            if Context.get_relative_path(str(path)).replace('\\', '/') != f'{root}/{_METADATA_NAME}':
                continue
            try:
                with open(path, 'rb') as handle:
                    value = plistlib.load(handle)
            except (OSError, plistlib.InvalidFileException, ValueError):
                continue
            if isinstance(value, dict) and isinstance(value.get('MCMMetadataIdentifier'), str):
                identifier = value['MCMMetadataIdentifier']
        _bundle_ids[key] = identifier
    return _bundle_ids[key]


def _folders(context):
    """(staged folder, evidence relative folder) for each Sync Data/LevelDB store.

    Files are grouped by the folder that holds them, so a store is read once however
    many of its files matched.
    """
    folders = {}
    for found in context.get_files_found():
        path = str(found)
        if not os.path.isfile(path):
            continue
        folder = os.path.dirname(path)
        relative = str(context.get_relative_path(folder)).replace('\\', '/')
        if _STORE.search(relative):
            folders.setdefault(folder, relative)
    return sorted(folders.items(), key=lambda item: item[1])


def _stores(context, label):
    """(folder, relative folder, bundle id, SyncStore) for each store that could be read."""
    out = []
    for folder, relative in _folders(context):
        try:
            sync = SyncStore(folder)
        except (OSError, ValueError, EOFError) as ex:
            logfunc(f'{label}: could not read {relative}: {ex}')
            continue
        logfunc(f'{label}: {relative}: {sync.records} records, {sync.superseded} older '
                f'versions of a key not read, {sync.deleted} keys whose newest version is a '
                f'deletion')
        out.append((folder, relative, _bundle_id(relative), sync))
    return out


def _decoded(sync, root_tag, message, label, relative):
    """(storage key, decoded message) for each live data record of one type that decodes."""
    out = []
    for _account, storage_key, value in sync.records_of(root_tag):
        try:
            out.append((storage_key, decode(value, message)))
        except ProtoError as ex:
            logfunc(f'{label}: {relative}: a {root_tag} record did not decode as '
                    f'{message} and is not reported: {ex}')
    return out


def _devices(sync, label, relative):
    """{cache GUID: DeviceInfoSpecifics} from the live device_info records."""
    devices = {}
    for _key, device in _decoded(sync, 'device_info', 'DeviceInfoSpecifics', label, relative):
        devices.setdefault(device.get('cache_guid', ''), device)
    return devices


def _local_guid(sync, root_tag, label, relative):
    try:
        return sync.local_cache_guid(root_tag)
    except ProtoError as ex:
        logfunc(f'{label}: {relative}: the {root_tag} sync state did not decode, so '
                f'This Device is blank: {ex}')
        return ''


def _this_device(guid, local_guid):
    if not local_guid:
        return ''
    return 'Yes' if guid == local_guid else 'No'


def _session_this_device(tag, local_guid, devices):
    """Yes when a session tag is this client's cache GUID, No when it is the cache GUID of
    another device the store lists, blank otherwise. A session tag has been the cache GUID
    only since M89, so a tag that matches no listed GUID establishes nothing about whose
    session it is."""
    if not local_guid or not tag:
        return ''
    if tag == local_guid:
        return 'Yes'
    return 'No' if tag in devices else ''


def _sessions(sync, label, relative):
    """(headers {session tag: SessionHeader}, tabs [(session tag, SessionTab)])."""
    headers, tabs = {}, []
    for _key, session in _decoded(sync, 'sessions', 'SessionSpecifics', label, relative):
        tag = session.get('session_tag', '')
        if 'header' in session:
            headers[tag] = session['header']
        elif 'tab' in session:
            tabs.append((tag, session['tab']))
    return headers, tabs


def _device_name(tag, headers, devices):
    name = headers.get(tag, {}).get('client_name')
    if name is None:
        name = devices.get(tag, {}).get('client_name', '')
    return name


@artifact_processor
def chrome_sync_sessions(context):
    label = 'Chrome Sync - Synced Tabs'
    data_list = []
    sources = []
    for folder, relative, bundle_id, sync in _stores(context, label):
        local_guid = _local_guid(sync, 'sessions', label, relative)
        devices = _devices(sync, label, relative)
        headers, tabs = _sessions(sync, label, relative)
        rows = 0
        for tag, tab in sorted(tabs, key=lambda item: (item[0], item[1].get('window_id', 0),
                                                        item[1].get('tab_id', 0))):
            current = tab.get('current_navigation_index')
            for index, navigation in enumerate(tab.get('navigation', [])):
                data_list.append((
                    _ms_time(navigation.get('timestamp_msec')),
                    _ms_time(tab.get('last_active_time_unix_epoch_millis')),
                    _device_name(tag, headers, devices),
                    _session_this_device(tag, local_guid, devices),
                    navigation.get('virtual_url', ''),
                    navigation.get('title', ''),
                    navigation.get('referrer', ''),
                    navigation.get('http_status_code', ''),
                    enum_label(PAGE_TRANSITIONS, navigation.get('page_transition')),
                    _yes_no(navigation.get('navigation_from_address_bar')),
                    index,
                    '' if current is None else ('Yes' if index == current else 'No'),
                    _yes_no(tab.get('pinned')),
                    tab.get('tab_id', ''),
                    tab.get('window_id', ''),
                    tag,
                    bundle_id,
                    relative,
                ))
                rows += 1
        if rows:
            sources.append(folder)
    data_headers = (('Navigation Time', 'datetime'), ('Tab Last Active', 'datetime'),
                    'Device Name', 'This Device', 'URL', 'Title', 'Referrer', 'HTTP Status',
                    'Transition', 'From Address Bar', 'Navigation Index', 'Current Entry',
                    'Pinned', 'Tab ID', 'Window ID', 'Session Tag', 'Bundle ID', 'Source Folder')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def chrome_sync_devices(context):
    label = 'Chrome Sync - Session Devices'
    data_list = []
    sources = []
    for folder, relative, bundle_id, sync in _stores(context, label):
        local_guid = _local_guid(sync, 'sessions', label, relative)
        devices = _devices(sync, label, relative)
        headers, _tabs = _sessions(sync, label, relative)
        rows = 0
        for tag, header in sorted(headers.items()):
            windows = header.get('window', [])
            browser_types = sorted({enum_label(BROWSER_TYPES, window.get('browser_type'))
                                    for window in windows if 'browser_type' in window})
            data_list.append((
                _ms_time(header.get('session_start_time_unix_epoch_millis')),
                header.get('client_name', ''),
                _session_this_device(tag, local_guid, devices),
                enum_label(FORM_FACTORS, header.get('device_form_factor')),
                enum_label(DEVICE_TYPES, header.get('device_type')),
                len(windows),
                sum(len(window.get('tab', [])) for window in windows),
                ', '.join(browser_types),
                tag,
                bundle_id,
                relative,
            ))
            rows += 1
        if rows:
            sources.append(folder)
    data_headers = (('Session Start', 'datetime'), 'Device Name', 'This Device', 'Form Factor',
                    'Device Type', 'Windows', 'Tabs Listed', 'Window Types', 'Session Tag',
                    'Bundle ID', 'Source Folder')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def chrome_sync_device_info(context):
    label = 'Chrome Sync - Device Info'
    data_list = []
    sources = []
    for folder, relative, bundle_id, sync in _stores(context, label):
        local_guid = _local_guid(sync, 'device_info', label, relative)
        rows = 0
        for _key, device in _decoded(sync, 'device_info', 'DeviceInfoSpecifics', label,
                                     relative):
            guid = device.get('cache_guid', '')
            version = (device.get('chrome_version_info') or {}).get('version_number')
            if version is None:
                version = device.get('chrome_version', '')
            data_list.append((
                _ms_time(device.get('last_updated_timestamp')),
                device.get('client_name', ''),
                _this_device(guid, local_guid),
                device.get('manufacturer', ''),
                device.get('model', ''),
                enum_label(OS_TYPES, device.get('os_type')),
                enum_label(FORM_FACTORS, device.get('device_form_factor')),
                enum_label(DEVICE_TYPES, device.get('device_type')),
                version,
                device.get('sync_user_agent', ''),
                guid,
                device.get('signin_scoped_device_id', ''),
                bundle_id,
                relative,
            ))
            rows += 1
        if rows:
            sources.append(folder)
    data_headers = (('Last Updated', 'datetime'), 'Device Name', 'This Device', 'Manufacturer',
                    'Model', 'OS Type', 'Form Factor', 'Device Type', 'Chrome Version',
                    'Sync User Agent', 'Cache GUID', 'Signin Scoped Device ID', 'Bundle ID',
                    'Source Folder')
    return data_headers, data_list, '\n'.join(sources)
