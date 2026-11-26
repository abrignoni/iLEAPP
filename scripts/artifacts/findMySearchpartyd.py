__artifacts_v2__ = {
    "findMyBeaconEstimatedLocations": {
        "name": "Find My Beacon Estimated Locations",
        "description": "Location records from the encrypted BeaconEstimatedLocation records of searchpartyd, "
                       "with the beacon's name",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-26",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Locations & Maps",
        "notes": "One row per BeaconEstimatedLocation record in com.apple.icloud.searchpartyd. Each .record file is a "
                 "binary plist list of a 16 byte nonce, a 16 byte tag and the AES-256-GCM ciphertext. It is decrypted "
                 "with the BeaconStore / BeaconStoreKey keychain item from the keychain carried by the extraction or "
                 "supplied with --keychain, and read only when the GCM tag verifies. The item's access group was "
                 "com.apple.icloud.searchpartyd on dexter_ios18, hill_iphone15pro_ios26 and wilkerson_iphone16_ios26 "
                 "and searchpartyd-baa-fmna-group on hickman_ios15, abe_ios16, felix23_ios16, adams_iphone12mini, "
                 "iphone11_ios17, felix_ios17 and otto_ios17. The key was the item's data on dexter_ios18, "
                 "felix_ios17, otto_ios17, hill_iphone15pro_ios26 and wilkerson_iphone16_ios26, and its gena attribute "
                 "on hickman_ios15, abe_ios16, felix23_ios16, adams_iphone12mini and iphone11_ios17, where the item "
                 "holds no data. The layout was published in denysvitali/searchparty-keys "
                 "(https://github.com/denysvitali/searchparty-keys/blob/b1b4b13c09c46d61b3cf22e66a2fb54e20e3c8c6/decrypt.go#L12-L33) "
                 "and joshuahickman1/Lost_Apples "
                 "(https://github.com/joshuahickman1/Lost_Apples/blob/9ec8597a4164bd63fa757fe2463597a393934e03/src/owned_beacons_parser.py#L99-L117). "
                 "A record file that cannot be opened is logged and skipped, and the others are still read. Without a "
                 "usable key a record is logged and gives no row, which is not evidence that nothing was recorded: "
                 "records were present and not read on cookbook_ios1751, hexordia_ios1651, iphone12_ios18, "
                 "iphone14plus_ios18, iphone14plus_ios18_mvs2025 and jess_ios15, where iLEAPP finds no keychain in the "
                 "extraction, and on falken_ios26, fsfull002_ios17 and hc_ios17_2, whose keychain-backup.plist entries "
                 "hold only encrypted data and a persistent reference. They carry no service, account or access group, "
                 "so no BeaconStore item could be identified. Records are joined only within one searchpartyd folder. "
                 "Timestamp and Scan Date are the record's timestamp and scanDate dates, in UTC; what each marks is "
                 "not established. Over the 190 rows of the nine images read they were equal on 145, Timestamp was "
                 "earlier on 30, and Scan Date held the text $null, shown as no value, on 15. locationSource (as "
                 "stored) held seven distinct integers (1, 2, 3, 4, 7, 8 and 15) and Horizontal Accuracy is "
                 "horizontalAccuracy as stored; the meaning of the first and the unit of the second are not "
                 "established. Beacon Record names the record type whose identifier equals the record's "
                 "associatedBeacon: OwnedBeacons on 171 rows and SharedBeacons on 19, all 19 on iphone11_ios17. Beacon "
                 "Name is the name in the BeaconNamingRecord whose associatedBeacon matches, else the name in the "
                 "BeaconAttributes table of the store's ItemSharingKeys.db whose beaconIdentifier matches, as "
                 "described in Find My Shared Beacons; those 19 rows have no naming record, and all 19 take their name "
                 "from BeaconAttributes. Where several naming records or several BeaconAttributes rows match, their "
                 "distinct names are joined with a comma; no image read had more than one. The record identifier and "
                 "cloudKitMetadata are not reported. SafeLocations records are not read; Find My Safe Locations Cache "
                 "reads the SafeLocations.data cache file. WildModeAssociationRecord records are read by Find My "
                 "Unwanted Tracker Alerts and Find My Unwanted Tracker Locations, and LeashRecords are counted by Find "
                 "My Owned Beacons. The remaining record types in the folder (among them KeySyncRecord, "
                 "KeyAlignmentRecords, OwnedDeviceKeyRecord and the SecureLocation records), its databases other than "
                 "Observations.db (read by Find My Observed Advertisements) and ItemSharingKeys.db (whose "
                 "BeaconAttributes names are joined here) and CachedUnifiedBeacons.data are not read.",
        "paths": (
            '*/mobile/Library/com.apple.icloud.searchpartyd/BeaconEstimatedLocation/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/BeaconNamingRecord/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/OwnedBeacons/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/SharedBeacons/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/ItemSharingKeys.db*',
        ),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 32 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 50 rows",
            "iphone11_ios17": "iOS 17.3 | 50 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 24 rows",
            "dexter_ios18": "iOS 18.3.2 | 18 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 1 row",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 15 rows",
        },
    },
    "findMyOwnedBeacons": {
        "name": "Find My Owned Beacons",
        "description": "Beacon records from the encrypted OwnedBeacons records of searchpartyd, with the name "
                       "from the matching BeaconNamingRecord",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-26",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Locations & Maps",
        "notes": "One row per OwnedBeacons record in com.apple.icloud.searchpartyd, decrypted as described in Find My "
                 "Beacon Estimated Locations, where the images whose records could not be read are listed. Model "
                 "(model as stored) held a string shaped like a device model identifier on 31 of the 37 rows read "
                 "(iPhone, iPad, Mac and Watch forms among them) and an empty string on 6. What the field identifies "
                 "is not established. Pairing Date is pairingDate in UTC; what it marks is not established. Name is "
                 "the name in the BeaconNamingRecord whose associatedBeacon equals the identifier, empty on the 6 of "
                 "37 rows with none. BeaconNamingRecord files for 6 beacons that match neither an OwnedBeacons nor a "
                 "SharedBeacons identifier (2 on abe_ios16, 4 on iphone11_ios17) are not reported. Latest Estimated "
                 "Location Timestamp is the latest Timestamp among the beacon's BeaconEstimatedLocation records and "
                 "Estimated Location Records is their count; 20 of 37 rows had none. Leash Records counts the "
                 "LeashRecords whose associatedBeacons list the identifier (1 on 23 rows, 0 on 14); what a leash "
                 "record represents is not established. batteryLevel (as stored) held 0 on 33 rows and 1 on 4, "
                 "productId (as stored) -1 on 31 and vendorId (as stored) -1 on 31; their meanings are not "
                 "established. Not reported: isZeus (False on all 37 records), cloudKitMetadata, groupIdentifier "
                 "(present on 2 records), the naming record's emoji (on 6 of 37) and roleId, and the key material "
                 "(privateKey, publicKey and sharedSecret on all 37, secureLocationsSharedSecret on 29, "
                 "secondarySharedSecret on 6).",
        "paths": (
            '*/mobile/Library/com.apple.icloud.searchpartyd/OwnedBeacons/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/BeaconNamingRecord/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/LeashRecords/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/BeaconEstimatedLocation/*.record',
        ),
        "output_types": "standard",
        "artifact_icon": "tag",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 4 rows",
            "felix23_ios16": "iOS 16.5 | 3 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 5 rows",
            "iphone11_ios17": "iOS 17.3 | 9 rows",
            "otto_ios17": "iOS 17.5.1 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | 7 rows",
            "dexter_ios18": "iOS 18.3.2 | 4 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 1 row",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 2 rows",
        },
    },
    "findMySharedBeacons": {
        "name": "Find My Shared Beacons",
        "description": "Beacon records from the encrypted SharedBeacons records of searchpartyd, with the "
                       "owner handle and share date",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-26",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Locations & Maps",
        "notes": "One row per SharedBeacons record in com.apple.icloud.searchpartyd, decrypted as described in Find My "
                 "Beacon Estimated Locations. Of the nine images in sample_data, only iphone11_ios17 held "
                 "SharedBeacons records, so every count here is from that image. Share Date is shareDate in UTC; what "
                 "it marks is not established. Owner Handle is the destination string of the ownerHandle dictionary, "
                 "present on all 14 rows; the dictionary's type integer (0 on all 14) is not reported. Owner Beacon "
                 "Identifier is ownerBeaconIdentifier from the record's name dictionary, present on 7 rows; on the "
                 "other 7 name held an empty string, and no record held a text name. Name and Emoji are the name and "
                 "emoji of the BeaconAttributes row in the store's ItemSharingKeys.db whose beaconIdentifier matches "
                 "the identifier, compared without regard to case, read in the database's current state. The table's "
                 "schema does not make beaconIdentifier unique; where several rows match, their distinct values are "
                 "joined with a comma, and no image read had more than one. Name was present on 7 of the 14 rows and "
                 "Emoji on 2, and ItemSharingKeys.db held BeaconAttributes rows on no other image. ItemSharingKeys.db "
                 "is a SQLite database encrypted as Observations.db is (see Find My Observed Advertisements), with the "
                 "KeyDatabase / searchparty keychain item; that item's data held the key on dexter_ios18, felix_ios17, "
                 "otto_ios17, hill_iphone15pro_ios26 and wilkerson_iphone16_ios26, and its gena attribute on "
                 "adams_iphone12mini and iphone11_ios17 (abe_ios16 and felix23_ios16 have no ItemSharingKeys.db). A "
                 "decrypted copy is written to the Decrypted searchpartyd folder in the report folder. Where "
                 "BeaconAttributes cannot be read, the failure is logged and the beacon rows are reported without its "
                 "names. The BeaconAttributes userIdentifier, roleIdentifier and systemVersion (each present on all 7 "
                 "rows) and serialNumber (null on all 7) are not reported. The table also has a delegationStatus "
                 "column on dexter_ios18, hill_iphone15pro_ios26 and wilkerson_iphone16_ios26, where it held no rows. "
                 "shareType (as stored) held 1 on 7 rows and 4 on 7; its meaning is not established. Model held an "
                 "empty string on 4 rows. Latest Estimated Location Timestamp and Estimated Location Records come from "
                 "the BeaconEstimatedLocation records whose associatedBeacon equals the identifier: 19 records for 3 "
                 "of the 14 beacons. Not reported: accepted (True on all 14), role (-1 on all 14), groupIdentifier "
                 "($null on all 14), correlationIdentifier, shareIdentifier, advertisedIndex, cloudKitMetadata and the "
                 "name dictionary's version.",
        "paths": (
            '*/mobile/Library/com.apple.icloud.searchpartyd/SharedBeacons/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/BeaconEstimatedLocation/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/ItemSharingKeys.db*',
        ),
        "output_types": "standard",
        "artifact_icon": "share-2",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 14 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
    "findMyUnwantedTrackerAlerts": {
        "name": "Find My Unwanted Tracker Alerts",
        "description": "The encrypted WildModeAssociationRecord records of searchpartyd, which Lost_Apples "
                       "describes as unwanted tracker alerts, with the span and count of their locations",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-26",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Locations & Maps",
        "notes": "One row per WildModeAssociationRecord record in com.apple.icloud.searchpartyd, decrypted as described "
                 "in Find My Beacon Estimated Locations, where the images whose records could not be read are listed. "
                 "Of the ten images run (the nine listed there and hickman_ios15), only iphone11_ios17 (4 records) and "
                 "hickman_ios15 (3) held WildModeAssociationRecord records, so every count here is from those 7 "
                 "records; the other eight images held none. "
                 "joshuahickman1/Lost_Apples describes these records as unwanted tracker alerts and their locations as "
                 "the phone's location when it detected the tracker "
                 "(https://github.com/joshuahickman1/Lost_Apples/blob/9ec8597a4164bd63fa757fe2463597a393934e03/README.md#L41); this module does not establish either. "
                 "Trigger Date is triggerDate in UTC; it fell between the earliest and latest location timestamps on 7 "
                 "of 7 records, and what it marks is not established. Date Published and Date Observation State "
                 "Changed are datePublished and dateObservationStateChanged in UTC, present on 2 of 7 records (both on "
                 "iphone11_ios17), each less than an hour after Trigger Date, and absent on the other 5, shown as no value; what they mark is not established. "
                 "Earliest Location Timestamp, Latest Location Timestamp and Locations come from the record's locations "
                 "list, which held 23 to 163 entries per record (702 in all); Locations counts entries, and on 2 records "
                 "two entries shared a timestamp. Find My Unwanted Tracker Locations has one row per entry. "
                 "observationState (as stored) held the text update on 2 rows and the key was absent on 5; a value "
                 "that is not text is shown as no value. observationType (as stored) held 0 on 2 rows and the key was "
                 "absent on 5. state (as stored) held 0 on all 7 rows and deviceType "
                 "(as stored) held 1 on all 7 rows. The meanings of these four values are not established. "
                 "Advertisement Key (hex) is the data of the record's advertisement key dictionary, 28 bytes on all 7; an advertisement in another layout gives no value. "
                 "Lost_Apples describes comparing beacon keys with the Wild Mode records of another device "
                 "(https://github.com/joshuahickman1/Lost_Apples/blob/9ec8597a4164bd63fa757fe2463597a393934e03/README.md#L145), keeps the 28 byte advertisement for that "
                 "comparison (https://github.com/joshuahickman1/Lost_Apples/blob/9ec8597a4164bd63fa757fe2463597a393934e03/src/wild_mode_parser.py#L228-L239), and derives a Bluetooth address from its first six bytes "
                 "(https://github.com/joshuahickman1/Lost_Apples/blob/9ec8597a4164bd63fa757fe2463597a393934e03/src/wild_mode_parser.py#L208-L226); neither is done here. Identifier is the "
                 "record's identifier, equal to its file name without the .record extension on 7 of 7. Lost_Apples also reads the keys address, "
                 "addresses, manufacturer, manufacturerName, model, modelName, productInfo, uuid and observationStates "
                 "(https://github.com/joshuahickman1/Lost_Apples/blob/9ec8597a4164bd63fa757fe2463597a393934e03/src/wild_mode_parser.py#L160-L304); none was present in the records read, "
                 "and they are not reported. Not reported either: recordBaseURL, present on the 3 hickman_ios15 "
                 "records, which held the record folder's own file URL. A record holding a key other than those named here is still reported, "
                 "and the key's name is logged.",
        "paths": (
            '*/mobile/Library/com.apple.icloud.searchpartyd/WildModeAssociationRecord/*.record',
        ),
        "output_types": "standard",
        "artifact_icon": "alert-triangle",
        "sample_data": {
            "hickman_ios15": "iOS 15.3.1 | 3 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 4 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
    "findMyUnwantedTrackerLocations": {
        "name": "Find My Unwanted Tracker Locations",
        "description": "The locations listed in the encrypted WildModeAssociationRecord records of searchpartyd, "
                       "one row per location",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-26",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Locations & Maps",
        "notes": "One row per entry in the locations list of a WildModeAssociationRecord record in "
                 "com.apple.icloud.searchpartyd, decrypted as described in Find My Beacon Estimated Locations. Every "
                 "count here is from iphone11_ios17 (460 entries in 4 records) and hickman_ios15 (242 in 3), the only "
                 "images run that held these records. Lost_Apples describes the locations as the phone's location when it detected the unwanted "
                 "tracker (https://github.com/joshuahickman1/Lost_Apples/blob/9ec8597a4164bd63fa757fe2463597a393934e03/README.md#L41); this module does not establish that. Timestamp is the "
                 "entry's timestamp in UTC; on 2 records two entries shared a timestamp, and both are reported. Horizontal Accuracy is horizontalAccuracy as stored; its unit is not established. Alert "
                 "Identifier is the record's identifier, the Identifier of its row in Find My Unwanted Tracker Alerts.",
        "paths": (
            '*/mobile/Library/com.apple.icloud.searchpartyd/WildModeAssociationRecord/*.record',
        ),
        "output_types": "all",
        "artifact_icon": "map",
        "sample_data": {
            "hickman_ios15": "iOS 15.3.1 | 242 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 460 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
    "findMyBeaconDailyAddresses": {
        "name": "Find My Beacon Daily Addresses",
        "description": "The daily MAC addresses and advertisement keys derived from the encrypted OwnedBeacons "
                       "records of searchpartyd, with the times this phone recorded each one",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-26",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Locations & Maps",
        "notes": "One row per day key derived for each OwnedBeacons record in com.apple.icloud.searchpartyd that holds "
                 "a secondarySharedSecret, decrypted as described in Find My Beacon Estimated Locations. The "
                 "derivation is the separated-state key chain of Apple's Find My Network Accessory Specification "
                 "(sections 6.3.4 and 5.1.3) as summarized in joshuahickman1/Lost_Apples "
                 "(https://github.com/joshuahickman1/Lost_Apples/blob/9ec8597a4164bd63fa757fe2463597a393934e03/src/key_schedule_generator.py#L19-L27): "
                 "each key's secret is the ANSI X9.63 KDF (SHA-256) of the one before it with \"update\", the KDF of "
                 "that with \"diversify\" gives two P-224 scalars u and v, and the key is the point u*P + v*G, computed "
                 "here as (d*u + v)*G from the record's private scalar d. Before any key is derived, the private "
                 "scalar is checked against the record's own public key; a record that fails, or has no pairing date, "
                 "is logged and gives no rows. Advertisement Key (hex) is the key's 28 byte x coordinate, and MAC "
                 "Address is its first 6 bytes with the top two bits of the first byte set. Both are derived values: "
                 "the record's private key and shared secrets are not reported. The derivation was checked against the "
                 "advertisements the same phone stored for its own beacons in Observations.db: on dexter_ios18, 3 of "
                 "the beacon's stored addresses equal a derived daily MAC Address exactly and their 28 byte "
                 "advertisementData equals the derived Advertisement Key exactly. On dexter_ios18, all 59 distinct "
                 "addresses the phone stored for its 2 beacons equaled a derived address of that beacon, 56 of them "
                 "from the 15 minute key chain this artifact does not list. Key Index counts days from the record's "
                 "secret. Estimated Date (UTC) is the pairing date plus Key Index days, in UTC; it is an estimate, "
                 "since Lost_Apples notes the secret can be replaced after pairing, and the specification starts each "
                 "key at 4 AM local time, which this artifact does not apply. Recorded First and Recorded Last are the "
                 "earliest and latest scanDate (UTC) at which this phone stored that MAC Address for the same beacon "
                 "in the current state of Observations.db, empty where it did not; a recorded row gives the key's real "
                 "time. Rows run from Key Index 1 to the number of whole days from pairing to the latest time the "
                 "store holds (the latest scanDate or BeaconEstimatedLocation timestamp), plus 2. The list is for "
                 "searching other data, such as another phone's Find My Observed Advertisements or Find My Unwanted "
                 "Tracker Alerts, or a Bluetooth detector export, for the MAC Address or Advertisement Key; matching "
                 "is left to the examiner, and a match or no match alone does not establish that the beacon was there. "
                 "The 15 minute keys a beacon uses near its owner are not listed, and neither are keys for beacons "
                 "with no secondarySharedSecret (31 of the 37 OwnedBeacons records on the nine images, counted in the "
                 "log); Lost_Apples derives both. Over the nine images, 6 records gave 1,203 rows: abe_ios16 23, "
                 "adams_iphone12mini 39 (2 beacons), dexter_ios18 217 (3 recorded) and iphone11_ios17 924 (2 beacons). "
                 "Beacon Name is the BeaconNamingRecord name, present on every row.",
        "paths": (
            '*/mobile/Library/com.apple.icloud.searchpartyd/OwnedBeacons/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/BeaconNamingRecord/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/BeaconEstimatedLocation/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/Observations.db*',
        ),
        "output_types": "standard",
        "artifact_icon": "radio",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 23 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 39 rows",
            "iphone11_ios17": "iOS 17.3 | 924 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 217 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
    "findMyObservedAdvertisementDays": {
        "name": "Find My Observed Advertisement Days",
        "description": "Advertisements in the encrypted Observations.db store of searchpartyd that have no "
                       "location, counted per beacon and UTC day",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-26",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Locations & Maps",
        "notes": "One row per searchpartyd folder, beacon and UTC day for the advertisements in Observations.db that "
                 "have no ObservedAdvertisementLocation row, read and decrypted as described in Find My Observed "
                 "Advertisements, which reports the advertisements that do have one; together the two account for "
                 "every advertisement read. These advertisements are counted per day and are not listed; their "
                 "macAddress, advertisementData and the other stored columns are not reported here. Where the store "
                 "was encrypted, the decrypted database and log in the report folder hold them, and a recovered one is "
                 "in an earlier state of the log, not in the database's current state. Day (UTC) is the first 10 "
                 "characters of scanDate, which is stored as text with no zone and read as UTC (see Find My Observed "
                 "Advertisements). First Scan Date and Last Scan Date are the earliest and latest scanDate of the "
                 "day's advertisements. Advertisements counts them, current and recovered, and Recovered "
                 "Advertisements counts those read only in another state of the write-ahead log. rssi Minimum and rssi "
                 "Maximum are the lowest and highest stored rssi; what rssi measures is not established. Beacon "
                 "Identifier, Beacon Record and Beacon Name are joined as in Find My Observed Advertisements; "
                 "advertisements that name no beacon are counted in a row with those columns empty, a path covered by "
                 "the unit test. Over the nine images, 1,842 advertisements had no location and made 9 rows: "
                 "felix_ios17 2 rows (1,833 advertisements), dexter_ios18 2 (4, 1 of them recovered), iphone11_ios17 2 "
                 "(2, one of them of a SharedBeacons beacon), and otto_ios17, hill_iphone15pro_ios26 and "
                 "wilkerson_iphone16_ios26 1 each. Every row named a beacon, and every row's beacon had a name. "
                 "Recovery Location is not reported per day; Find My Observed Advertisements gives it for each located "
                 "advertisement.",
        "paths": (
            '*/mobile/Library/com.apple.icloud.searchpartyd/Observations.db*',
            '*/mobile/Library/com.apple.icloud.searchpartyd/OwnedBeacons/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/SharedBeacons/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/BeaconNamingRecord/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/ItemSharingKeys.db*',
        ),
        "output_types": "standard",
        "artifact_icon": "calendar",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 1 row",
            "felix_ios17": "iOS 17.6.1 | 2 rows",
            "dexter_ios18": "iOS 18.3.2 | 2 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 1 row",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 1 row",
        },
    },
    "findMyObservedAdvertisements": {
        "name": "Find My Observed Advertisements",
        "description": "Advertisements in the encrypted Observations.db store of searchpartyd that have a location, "
                       "with the beacon identifier where the store names one, and the beacon name from the matching "
                       "BeaconNamingRecord, or from BeaconAttributes in ItemSharingKeys.db where there is none",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-26",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Locations & Maps",
        "notes": "One row per advertisement in the ObservedAdvertisement table of Observations.db in "
                 "com.apple.icloud.searchpartyd that has an ObservedAdvertisementLocation row, read in the current "
                 "state and in every other state of the database's write-ahead log that scripts/sqlite_wal.py could "
                 "read. Advertisements without a location row are counted per beacon and UTC day in Find My Observed "
                 "Advertisement Days, and together the two account for every advertisement read. The store is a SQLite "
                 "database encrypted page by page with AES-256-OFB, as published in joshuahickman1/Lost_Apples "
                 "(https://github.com/joshuahickman1/Lost_Apples/blob/9ec8597a4164bd63fa757fe2463597a393934e03/src/searchpartyd_db_decryptor.py#L15-L19): "
                 "page 1 bytes 16 to 23 and the last 12 bytes of each page are stored unencrypted, and a page's IV is "
                 "its page number (4 bytes, little-endian) followed by those 12 bytes. The key is the Observations / "
                 "searchparty keychain item from the keychain carried by the extraction or supplied with --keychain: "
                 "the item's data on dexter_ios18, felix_ios17, otto_ios17, hill_iphone15pro_ios26 and "
                 "wilkerson_iphone16_ios26, and its gena attribute on abe_ios16, felix23_ios16, adams_iphone12mini and "
                 "iphone11_ios17. A candidate is used only when it decrypts page 1 to a SQLite header. A store with "
                 "another page layout, or with no key that opens it, is logged and gives no rows; every store read had "
                 "4096 byte pages and 12 reserved bytes. On all nine images the stored checksums of the log's "
                 "current-generation frames verified over the encrypted frames and not over their plaintext (2 of the "
                 "7 frames on abe_ios16; its other 5 are from an older generation), so each frame is checked as stored "
                 "and only a frame that passes is given a checksum over its plaintext: a frame that fails its stored "
                 "checksum still fails after decryption. The decrypted database and log are written to the Decrypted "
                 "searchpartyd folder in this artifact's report folder, and that copy is what is queried. A store that "
                 "is already plain SQLite is read where it is. Bytes after the log's last whole frame are not copied "
                 "(3,896 bytes on abe_ios16). A log whose header is damaged is still decrypted, its frames taken at "
                 "the database's page size as scripts/sqlite_wal.py reads such a log; that path is covered by the unit "
                 "test, and no image read had a damaged header. Record Origin. Live rows come from the current state "
                 "of the decrypted store. Recovered rows are advertisements, keyed by advId (INTEGER PRIMARY KEY "
                 "AUTOINCREMENT in the store's schema on all nine images), that another state in the log holds and the "
                 "current state does not. States are read by scripts/sqlite_wal.py: each committed state of the log's "
                 "current generation that it can read exactly (state n is the database after the first n committed "
                 "transactions, and state 0 the database file without its log), the previous generation's left-over "
                 "frames where its checks pass, and frames after the last commit. Only advId is compared from state to "
                 "state; the full row of each advertisement the current state lacks is read from the newest state "
                 "holding it (a committed state, else the previous generation's left-over frames, else the frames "
                 "after the last commit), with that state's location and beacon rows, and is reported once. An "
                 "advertisement whose location row survives only in a state older than the one it is read from is "
                 "summarized per day without it and counted in the log; none did on the nine images. Recovery Location "
                 "names the committed states the advertisement was read in, with their first and last numbers. Why a "
                 "Recovered row is absent from the current state is not established. Recovered rows were returned on "
                 "adams_iphone12mini (66 of 70), dexter_ios18 (71 of 180), iphone11_ios17 (174 of 180), otto_ios17 "
                 "(838 of 840) and wilkerson_iphone16_ios26 (57 of 78), all from committed states, so Recovery Method "
                 "held WAL committed states on every Recovered row. That includes 22 wilkerson_iphone16_ios26 rows "
                 "read only in state 0, the database file without its log, as their Recovery Location says. On "
                 "felix_ios17 and hill_iphone15pro_ios26 every row is Live: Record Origin held Live and Recovery "
                 "Method and Recovery Location were empty on all their rows. The previous-generation and "
                 "uncommitted-frame paths were not exercised: no log held frames of the previous generation or frames "
                 "after its last commit. The abe_ios16 log holds 5 frames of an older generation, none a commit frame, "
                 "which are not read. On felix23_ios16 the database file already held the whole log, so 3 of its 4 "
                 "earlier states (0 to 2) could not be read. abe_ios16 and felix23_ios16 held no advertisements in the "
                 "states read. Scan Date is the advertisement's scanDate and Location Timestamp the timestamp of its "
                 "ObservedAdvertisementLocation row. Both are stored as text with no zone and are read as UTC. Read "
                 "that way, over the 2,072 advertisements of the nine images whose beacon has a "
                 "BeaconEstimatedLocation record (231 with a location row, 1,841 without), a scanDate equaled a time "
                 "in a record of the same beacon (a plist date) to the millisecond on 22 advertisements over six "
                 "images (19 with a location row, 3 without), and a location timestamp did on 19 of the 231; none "
                 "matched a whole number of hours away. What each time marks is not established. Latitude, Longitude "
                 "and Horizontal Accuracy come from the location row; 1,819 of the 3,661 advertisements read had one "
                 "(23 of 1,856 on felix_ios17). The schema requires horizontalAccuracy to be 0 or more; its unit is "
                 "not established. Beacon Identifier is the beaconIdentifier of the advertisement's "
                 "ObservedAdvertisementBeaconInfo row, present on 231 of the 1,819 rows, each equal to an OwnedBeacons "
                 "record identifier; Beacon Record names the record type matched (OwnedBeacons or SharedBeacons), and "
                 "Beacon Name is the name in the BeaconNamingRecord whose associatedBeacon matches, else the "
                 "BeaconAttributes name described in Find My Shared Beacons. All 231 had a naming record. The other "
                 "1,588 rows name no beacon, and what sent them is not established. Records are joined only within one "
                 "searchpartyd folder. macAddress (hex) is the stored macAddress, which the schema requires to be 6 "
                 "bytes. Advertisement Data (hex) is the stored advertisementData, 28 bytes on 1,689 rows and 6 bytes "
                 "on 130. rssi (as stored) was negative on 1,818 rows. What these three values identify or measure is "
                 "not established. Advertisement ID is advId. Not reported: source, status, multipart, hint, "
                 "extraKeyBits, isPosh and isPublished, and the sequence and index of ObservedAdvertisementBeaconInfo, "
                 "whose meanings are not established. The other tables of Observations.db are not read: DeviceEvent, "
                 "DeviceEventLocation and AttachmentInfo were absent or empty on all nine images; "
                 "KeyGenerationBeaconKeys and KeyGenerationHint have columns named privateKey and sharedSecret and "
                 "held no rows on any of the nine images; KeyGenerationBeaconInfo holds a beacon identifier and "
                 "pairDate per beacon, and read as UTC its pairDate equaled the OwnedBeacons pairingDate that Find My "
                 "Owned Beacons reports on all 31 joined rows; KeySyncMetadata holds integers (type, sequence, index, "
                 "isWild) and a time whose meanings are not established. FindMyServiceDevices held 5 rows, on the two "
                 "iOS 26 images only, and each had a record in the Devices.data cache that Find My Devices Cache "
                 "reports whose id equaled its deviceId, with the same name and rawDeviceModel; BatteryState, on "
                 "wilkerson_iphone16_ios26 only, held one batteryLevel value on all 66 distinct rows over the log's "
                 "states. Neither is read. The folder's other databases decrypted with their own keychain items on "
                 "these images: CloudStorage, LocalStorage and StandaloneBeacon held no rows on any of them and are "
                 "not read, CloudStorage_CKRecordCache held only CloudKit change tokens (one DatabaseChangeToken and "
                 "one ZoneChangeToken row) and is not read, and ItemSharingKeys held rows on iphone11_ios17 only (7 "
                 "BeaconAttributes rows and 47,600 NearOwnerKeys rows, each a 6 byte nearOwnerAdvertisement with "
                 "integers). Its BeaconAttributes names are joined into the beacon names here and in Find My Shared "
                 "Beacons; its other tables are not read.",
        "paths": (
            '*/mobile/Library/com.apple.icloud.searchpartyd/Observations.db*',
            '*/mobile/Library/com.apple.icloud.searchpartyd/OwnedBeacons/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/SharedBeacons/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/BeaconNamingRecord/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/ItemSharingKeys.db*',
        ),
        "output_types": "all",
        "artifact_icon": "bluetooth",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 70 rows",
            "iphone11_ios17": "iOS 17.3 | 180 rows",
            "otto_ios17": "iOS 17.5.1 | 840 rows",
            "felix_ios17": "iOS 17.6.1 | 23 rows",
            "dexter_ios18": "iOS 18.3.2 | 180 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 448 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 78 rows",
        },
    },
}

import hashlib
import os
import plistlib
import sqlite3
import struct
from datetime import datetime, timedelta, timezone
from pathlib import PurePath
from xml.parsers.expat import ExpatError

from Crypto.Cipher import AES
from Crypto.PublicKey import ECC

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, logfunc
from scripts.ios_keychain import active_keychain_path, load_keychain_entries
from scripts.sqlite_wal import KIND_COMMITTED, KIND_EARLIER, KIND_UNCOMMITTED, WalStates

STORE_DIR = 'com.apple.icloud.searchpartyd'
# The item's access group was com.apple.icloud.searchpartyd on the three iOS 18 and 26 images read
# and searchpartyd-baa-fmna-group on the seven iOS 15, 16 and 17 images read; the lookup matches a
# substring of both.
ACCESS_GROUP = 'searchpartyd'
KEY_SERVICE = 'BeaconStore'
KEY_ACCOUNT = 'BeaconStoreKey'
KEY_LENGTH = 32
NONCE_LENGTH = 16
TAG_LENGTH = 16
# Some keys hold this text in place of a value. It is read as no value.
NULL_TEXT = '$null'

_PLIST_ERRORS = (plistlib.InvalidFileException, ValueError, TypeError, IndexError, KeyError,
                 OverflowError, RecursionError, ExpatError)

_key_cache = {}


def _loads_plist(raw):
    try:
        return plistlib.loads(raw)
    except _PLIST_ERRORS:
        return None


def _field_text(entry, field):
    value = entry.get(field)
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).decode('utf-8', 'ignore').rstrip('\x00')
    return str(value) if value is not None else ''


def _keychain_keys(service, account):
    """Every 32 byte key candidate the keychain in use holds for a searchpartyd item, or None
    without a keychain.

    The key was the item's data (v_Data) on some images run. On others the item held no data
    and the key was its 32 byte gena attribute, so both are candidates; the caller's check (the
    GCM tag, or the SQLite header of a decrypted page) decides which, if either, is the key.
    """
    keychain = active_keychain_path()
    if not keychain:
        return None
    cache_key = (keychain, service, account)
    if cache_key not in _key_cache:
        keys = []
        for entry in load_keychain_entries(keychain):
            if (ACCESS_GROUP not in _field_text(entry, 'agrp').lower()
                    or _field_text(entry, 'svce') != service
                    or _field_text(entry, 'acct') != account):
                continue
            for field in ('v_Data', 'gena'):
                value = entry.get(field)
                if isinstance(value, (bytes, bytearray)) and len(value) == KEY_LENGTH \
                        and bytes(value) not in keys:
                    keys.append(bytes(value))
        _key_cache[cache_key] = keys
    return _key_cache[cache_key]


def _beacon_store_keys():
    """Every 32 byte BeaconStore / BeaconStoreKey key candidate, or None without a keychain."""
    return _keychain_keys(KEY_SERVICE, KEY_ACCOUNT)


def read_searchpartyd_record(file_found):
    """Open one searchpartyd .record file, or return None (logged) where it cannot be read.

    The file is a binary plist holding a list of three byte strings: a 16 byte nonce, a 16 byte
    tag and the AES-256-GCM ciphertext. The key is the BeaconStore / BeaconStoreKey keychain item.
    The plaintext is a binary plist dictionary.
    """
    try:
        with open(file_found, 'rb') as record_file:
            outer = _loads_plist(record_file.read())
    except OSError as error:
        logfunc(f'{file_found}: could not read record: {error}')
        return None
    if (not isinstance(outer, list) or len(outer) != 3 or not all(isinstance(x, bytes) for x in outer)
            or len(outer[0]) != NONCE_LENGTH or len(outer[1]) != TAG_LENGTH):
        logfunc(f'{file_found} is not a nonce, tag and ciphertext list; not read')
        return None
    keys = _beacon_store_keys()
    if keys is None:
        logfunc(f'{file_found} is encrypted and no keychain is available; not read. '
                'Supply the extraction\'s keychain with --keychain.')
        return None
    if not keys:
        logfunc(f'{file_found} is encrypted and no readable BeaconStore key was found in the keychain in use; not read')
        return None
    nonce, tag, ciphertext = outer
    for key in keys:
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        try:
            plain = cipher.decrypt_and_verify(ciphertext, tag)
        except ValueError:
            continue
        document = _loads_plist(plain)
        if not isinstance(document, dict):
            logfunc(f'{file_found}: decrypted content is not a plist dictionary; not read')
            return None
        return document
    logfunc(f'{file_found}: the authentication tag did not verify with the BeaconStore key; not read')
    return None


def _store_root(file_found):
    """The searchpartyd folder a record belongs to, so records join only within one store."""
    parts = PurePath(file_found).parts
    for index in range(len(parts) - 1, -1, -1):
        if parts[index] == STORE_DIR:
            return PurePath(*parts[:index + 1])
    return None


def _record_type(file_found, root):
    return PurePath(file_found).relative_to(root).parts[0]


def _read_store(files_found):
    """Decrypted records grouped by store folder and record type, with the files that opened."""
    stores = {}
    for file_found in sorted(str(path) for path in files_found):
        if not file_found.endswith('.record'):
            continue
        root = _store_root(file_found)
        if root is None:
            continue
        record = read_searchpartyd_record(file_found)
        if record is None:
            continue
        stores.setdefault(root, {}).setdefault(_record_type(file_found, root), []).append(
            (file_found, record))
    return stores


def _value(value):
    return '' if value is None or value == NULL_TEXT else value


def _date(value):
    if hasattr(value, 'replace') and hasattr(value, 'year'):
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
    return ''


def _text(value):
    return value if isinstance(value, str) and value != NULL_TEXT else ''


def _names(records):
    names = {}
    for _file_found, record in records.get('BeaconNamingRecord', []):
        beacon = _text(record.get('associatedBeacon')).upper()
        name = _text(record.get('name'))
        if beacon and name:
            names.setdefault(beacon, []).append(name)
    return {beacon: ', '.join(dict.fromkeys(found)) for beacon, found in names.items()}


def _identifiers(records, record_type):
    return {_text(record.get('identifier')).upper() for _file_found, record in records.get(record_type, [])}


def _estimates(records):
    """The timestamps of the BeaconEstimatedLocation records, keyed by beacon identifier."""
    estimated = {}
    for _file_found, record in records.get('BeaconEstimatedLocation', []):
        estimated.setdefault(_text(record.get('associatedBeacon')).upper(), []).append(
            _date(record.get('timestamp')))
    return estimated


def _estimate_columns(estimated, identifier):
    times = [time for time in estimated.get(identifier.upper(), []) if time]
    return (max(times) if times else ''), len(estimated.get(identifier.upper(), []))


@artifact_processor
def findMyBeaconEstimatedLocations(context):
    data_headers = (('Timestamp', 'datetime'), ('Scan Date', 'datetime'), ('Latitude', 'latitude'),
                    ('Longitude', 'longitude'), 'Horizontal Accuracy', 'locationSource (as stored)',
                    'Beacon Name', 'Beacon Record', 'Beacon Identifier')
    data_list = []
    sources = []
    attributes, attribute_sources = _beacon_attributes(context, context.get_files_found())
    for root, records in _read_store(context.get_files_found()).items():
        names = _beacon_names(records, attributes.get(root, {}))
        owned = _identifiers(records, 'OwnedBeacons')
        shared = _identifiers(records, 'SharedBeacons')
        for file_found, record in records.get('BeaconEstimatedLocation', []):
            beacon = _text(record.get('associatedBeacon'))
            kind = 'OwnedBeacons' if beacon.upper() in owned else \
                'SharedBeacons' if beacon.upper() in shared else ''
            sources.append(file_found)
            data_list.append((_date(record.get('timestamp')), _date(record.get('scanDate')),
                              _value(record.get('latitude')), _value(record.get('longitude')),
                              _value(record.get('horizontalAccuracy')), _value(record.get('locationSource')),
                              names.get(beacon.upper(), ''), kind, beacon))
    sources += [path for path in attribute_sources if _store_root(path) in
                {_store_root(source) for source in sources}]
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def findMyOwnedBeacons(context):
    data_headers = (('Pairing Date', 'datetime'), ('Latest Estimated Location Timestamp', 'datetime'), 'Name',
                    'Model', 'System Version', 'batteryLevel (as stored)', 'productId (as stored)',
                    'vendorId (as stored)', 'Estimated Location Records', 'Leash Records', 'Identifier',
                    'Stable Identifier')
    data_list = []
    sources = []
    for _root, records in _read_store(context.get_files_found()).items():
        names = _names(records)
        estimated = _estimates(records)
        leashes = {}
        for _file_found, record in records.get('LeashRecords', []):
            for beacon in record.get('associatedBeacons') or []:
                if isinstance(beacon, str):
                    leashes[beacon.upper()] = leashes.get(beacon.upper(), 0) + 1
        for file_found, record in records.get('OwnedBeacons', []):
            sources.append(file_found)
            identifier = _text(record.get('identifier'))
            newest, count = _estimate_columns(estimated, identifier)
            stable = record.get('stableIdentifier')
            stable = ', '.join(s for s in stable if isinstance(s, str)) if isinstance(stable, list) \
                else _text(stable)
            data_list.append((_date(record.get('pairingDate')), newest, names.get(identifier.upper(), ''),
                              _text(record.get('model')), _text(record.get('systemVersion')),
                              _value(record.get('batteryLevel')), _value(record.get('productId')),
                              _value(record.get('vendorId')), count, leashes.get(identifier.upper(), 0),
                              identifier, stable))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def findMySharedBeacons(context):
    data_headers = (('Share Date', 'datetime'), ('Latest Estimated Location Timestamp', 'datetime'), 'Name',
                    'Emoji', 'Owner Handle', 'Model', 'System Version', 'shareType (as stored)',
                    'productId (as stored)', 'vendorId (as stored)',
                    'Estimated Location Records', 'Identifier', 'Owner Beacon Identifier')
    data_list = []
    sources = []
    attributes, attribute_sources = _beacon_attributes(context, context.get_files_found())
    for root, records in _read_store(context.get_files_found()).items():
        estimated = _estimates(records)
        store_attributes = attributes.get(root, {})
        for file_found, record in records.get('SharedBeacons', []):
            sources.append(file_found)
            identifier = _text(record.get('identifier'))
            newest, count = _estimate_columns(estimated, identifier)
            handle = record.get('ownerHandle') if isinstance(record.get('ownerHandle'), dict) else {}
            name = record.get('name')
            owner_beacon = _text(name.get('ownerBeaconIdentifier')) if isinstance(name, dict) else ''
            name_text, emoji = store_attributes.get(identifier.upper(), ('', ''))
            data_list.append((_date(record.get('shareDate')), newest, name_text, emoji,
                              _text(handle.get('destination')), _text(record.get('model')),
                              _text(record.get('systemVersion')), _value(record.get('shareType')),
                              _value(record.get('productId')),
                              _value(record.get('vendorId')), count, identifier, owner_beacon))
    sources += [path for path in attribute_sources if _store_root(path) in
                {_store_root(source) for source in sources}]
    return data_headers, data_list, '\n'.join(sources)


# The top-level keys of the WildModeAssociationRecord records read. recordBaseURL held the record
# folder's own file URL and is not reported. A record holding any other key is still reported; the
# key's name is logged so a layout not seen here is visible.
WILD_MODE_KEYS = frozenset((
    'identifier', 'triggerDate', 'datePublished', 'dateObservationStateChanged', 'locations',
    'deviceType', 'state', 'observationState', 'observationType', 'advertisement', 'recordBaseURL'))


def _wild_mode_records(files_found):
    """The decrypted WildModeAssociationRecord records, with the file each came from."""
    found = []
    for records in _read_store(files_found).values():
        for file_found, record in records.get('WildModeAssociationRecord', []):
            unknown = sorted(str(key) for key in record if key not in WILD_MODE_KEYS)
            if unknown:
                logfunc(f'{file_found}: WildModeAssociationRecord keys not reported: {", ".join(unknown)}')
            found.append((file_found, record))
    return found


def _locations(record):
    locations = record.get('locations')
    return [entry for entry in locations if isinstance(entry, dict)] if isinstance(locations, list) else []


def _advertisement(record):
    """The advertisement key's data as hex, or '' where the record holds none."""
    advertisement = record.get('advertisement')
    key = advertisement.get('key') if isinstance(advertisement, dict) else None
    data = key.get('data') if isinstance(key, dict) else None
    return bytes(data).hex() if isinstance(data, (bytes, bytearray)) else ''


@artifact_processor
def findMyUnwantedTrackerAlerts(context):
    data_headers = (('Trigger Date', 'datetime'), ('Date Published', 'datetime'),
                    ('Date Observation State Changed', 'datetime'), ('Earliest Location Timestamp', 'datetime'),
                    ('Latest Location Timestamp', 'datetime'), 'Locations', 'observationState (as stored)',
                    'observationType (as stored)', 'state (as stored)', 'deviceType (as stored)',
                    'Advertisement Key (hex)', 'Identifier')
    data_list = []
    sources = []
    for file_found, record in _wild_mode_records(context.get_files_found()):
        sources.append(file_found)
        locations = _locations(record)
        times = [time for time in (_date(entry.get('timestamp')) for entry in locations) if time]
        data_list.append((_date(record.get('triggerDate')), _date(record.get('datePublished')),
                          _date(record.get('dateObservationStateChanged')), min(times) if times else '',
                          max(times) if times else '', len(locations), _text(record.get('observationState')),
                          _value(record.get('observationType')), _value(record.get('state')),
                          _value(record.get('deviceType')), _advertisement(record),
                          _text(record.get('identifier'))))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def findMyUnwantedTrackerLocations(context):
    data_headers = (('Timestamp', 'datetime'), ('Latitude', 'latitude'), ('Longitude', 'longitude'),
                    'Horizontal Accuracy', 'Alert Identifier')
    data_list = []
    sources = []
    for file_found, record in _wild_mode_records(context.get_files_found()):
        sources.append(file_found)
        identifier = _text(record.get('identifier'))
        for entry in _locations(record):
            data_list.append((_date(entry.get('timestamp')), _value(entry.get('latitude')),
                              _value(entry.get('longitude')), _value(entry.get('horizontalAccuracy')),
                              identifier))
    return data_headers, data_list, '\n'.join(sources)


# The searchpartyd .db stores are SQLite databases encrypted page by page (SQLite Encryption
# Extension, AES-256-OFB), as published in joshuahickman1/Lost_Apples (searchpartyd_db_decryptor.py
# lines 15-25 and 99-130 at 9ec8597a). Page 1 bytes 16 to 23 (page size, versions, reserved byte
# count) are stored unencrypted. The last RESERVED_BYTES of each page are stored unencrypted too,
# and the page's IV is its page number (4 bytes, little-endian) followed by them. The key is the
# keychain item named for the store (account searchparty).
SQLITE_MAGIC = b'SQLite format 3\x00'
SEE_RESERVED_BYTES = 12
STORE_ACCOUNT = 'searchparty'
OBSERVATIONS_SERVICE = 'Observations'
WAL_MAGICS = (0x377F0682, 0x377F0683)
WAL_HEADER = 32
WAL_FRAME_HEADER = 24
DECRYPTED_FOLDER = 'Decrypted searchpartyd'


def _page_geometry(header):
    """(page size, reserved bytes) from the unencrypted page 1 bytes 16 to 23, or None."""
    if len(header) < 24:
        return None
    size = int.from_bytes(header[16:18], 'big')
    size = 65536 if size == 1 else size
    if size < 512 or size & (size - 1):
        return None
    return size, header[20]


def _decrypt_page(key, page, page_number):
    """One page's plaintext. The reserved bytes are kept, so the page keeps its stored IV."""
    reserved = page[-SEE_RESERVED_BYTES:]
    iv = page_number.to_bytes(4, 'little') + reserved
    plain = AES.new(key, AES.MODE_OFB, iv=iv).decrypt(page[:-SEE_RESERVED_BYTES])
    if page_number == 1:
        plain = plain[:16] + page[16:24] + plain[24:]
    return plain + reserved


def _wal_checksum(data, big_endian, state):
    """SQLite's write-ahead log checksum over data, continuing from state."""
    words = struct.unpack(('>' if big_endian else '<') + f'{len(data) // 4}I', data)
    first, second = state
    for index in range(0, len(words), 2):
        first = (first + words[index] + second) & 0xFFFFFFFF
        second = (second + words[index + 1] + first) & 0xFFFFFFFF
    return first, second


def _usable_wal_header(raw):
    """(big_endian, page size) from a log header SQLite would accept, or None for a damaged one."""
    magic = int.from_bytes(raw[:4], 'big')
    size = int.from_bytes(raw[8:12], 'big')
    if magic not in WAL_MAGICS or size < 512 or size > 65536 or size & (size - 1):
        return None
    big_endian = bool(magic & 1)
    if _wal_checksum(raw[:24], big_endian, (0, 0)) != struct.unpack('>II', raw[24:32]):
        return None
    return big_endian, size


def _frame_chain_byte_order(raw, page_size):
    """With no usable header, the byte order under which frame 2's stored checksum follows from
    frame 1's, tried big-endian first as scripts/sqlite_wal.py does; big-endian when neither holds."""
    frame_size = WAL_FRAME_HEADER + page_size
    if len(raw) < WAL_HEADER + 2 * frame_size:
        return True
    first = raw[WAL_HEADER:WAL_HEADER + frame_size]
    second = raw[WAL_HEADER + frame_size:WAL_HEADER + 2 * frame_size]
    for big_endian in (True, False):
        state = _wal_checksum(second[:8], big_endian, struct.unpack('>II', first[16:24]))
        if _wal_checksum(second[WAL_FRAME_HEADER:], big_endian, state) == struct.unpack('>II', second[16:24]):
            return big_endian
    return True


def _decrypt_wal(raw, key, page_size):
    """The log with each frame's page decrypted, or None when it is not a log of this page size.

    SQLite SEE computes a frame's checksum over the frame as stored, that is over the encrypted
    page. Each frame is checked that way, against the frame before it as stored. A frame that
    passes gets a new checksum over its plaintext, chained from the new checksum of the frame
    before it; a frame that fails keeps its stored checksum, which does not match its plaintext.
    So SQLite, and scripts/sqlite_wal.py, read the decrypted log the way they would read the
    stored one: the same frames pass and fail, including a previous generation's left-over
    frames, whose chain starts from the first left-over frame's stored checksum. A log whose
    header is damaged is kept as scripts/sqlite_wal.py reads one: its frames are taken at the
    database's page size, in the byte order under which their chain holds, and the header is
    copied as stored.
    Returns (log, frames, bytes after the last whole frame, whether the header was usable).
    """
    if len(raw) < WAL_HEADER:
        return None
    header_fields = _usable_wal_header(raw)
    if header_fields is None:
        big_endian = _frame_chain_byte_order(raw, page_size)
    elif header_fields[1] != page_size:
        return None
    else:
        big_endian = header_fields[0]
    out = bytearray(raw[:WAL_HEADER])
    stored_before = out_before = struct.unpack('>II', raw[24:32])
    frame_size = WAL_FRAME_HEADER + page_size
    frames = (len(raw) - WAL_HEADER) // frame_size
    for index in range(frames):
        offset = WAL_HEADER + index * frame_size
        header = raw[offset:offset + WAL_FRAME_HEADER]
        page = raw[offset + WAL_FRAME_HEADER:offset + frame_size]
        page_number = int.from_bytes(header[:4], 'big')
        stored = struct.unpack('>II', header[16:24])
        passes = page_number and _wal_checksum(
            page, big_endian, _wal_checksum(header[:8], big_endian, stored_before)) == stored
        plain = _decrypt_page(key, page, page_number) if page_number else page
        new = _wal_checksum(plain, big_endian, _wal_checksum(header[:8], big_endian, out_before)) \
            if passes else stored
        out += header[:16] + struct.pack('>II', *new) + plain
        stored_before, out_before = stored, new
    return bytes(out), frames, len(raw) - WAL_HEADER - frames * frame_size, header_fields is not None


def decrypt_searchpartyd_db(db_path, service, output_dir):
    """Write a decrypted copy of one searchpartyd .db store, and of its -wal when there is one,
    into output_dir. Returns the copy's path, or None (logged) where the store cannot be read.
    The evidence files are only read.
    """
    try:
        with open(db_path, 'rb') as db_file:
            raw = db_file.read()
    except OSError as error:
        logfunc(f'{db_path}: could not read store: {error}')
        return None
    if raw[:16] == SQLITE_MAGIC:
        logfunc(f'{db_path} is not encrypted; read as it is')
        return db_path
    geometry = _page_geometry(raw)
    if geometry is None or geometry[1] != SEE_RESERVED_BYTES or len(raw) % geometry[0]:
        logfunc(f'{db_path}: page size, reserved bytes or file size is not the encrypted layout '
                f'read here ({SEE_RESERVED_BYTES} reserved bytes, a whole number of pages); not read')
        return None
    page_size = geometry[0]
    keys = _keychain_keys(service, STORE_ACCOUNT)
    if keys is None:
        logfunc(f'{db_path} is encrypted and no keychain is available; not read. '
                'Supply the extraction\'s keychain with --keychain.')
        return None
    key = next((k for k in keys if _decrypt_page(k, raw[:page_size], 1)[:16] == SQLITE_MAGIC), None)
    if key is None:
        logfunc(f'{db_path}: no {service} key in the keychain in use decrypts page 1 to a SQLite '
                f'header ({len(keys)} candidates tried); not read')
        return None
    os.makedirs(output_dir, exist_ok=True)
    copy_path = os.path.join(output_dir, os.path.basename(db_path))
    with open(copy_path, 'wb') as copy_file:
        for number in range(len(raw) // page_size):
            copy_file.write(_decrypt_page(key, raw[number * page_size:(number + 1) * page_size], number + 1))
    wal_path = db_path + '-wal'
    if os.path.isfile(wal_path):
        try:
            with open(wal_path, 'rb') as wal_file:
                wal = _decrypt_wal(wal_file.read(), key, page_size)
        except OSError as error:
            logfunc(f'{wal_path}: could not read log: {error}; the database file is read without it')
            wal = None
        if wal is None:
            logfunc(f'{wal_path} is shorter than a log header or names another page size; the database '
                    'file is read without it')
        else:
            log, frames, tail, header_usable = wal
            with open(copy_path + '-wal', 'wb') as copy_file:
                copy_file.write(log)
            if not header_usable:
                logfunc(f'{wal_path}: the log header is damaged; its {frames} frames are kept at the '
                        'database\'s page size for scripts/sqlite_wal.py to read')
            if tail:
                logfunc(f'{wal_path}: {tail} bytes after the last of its {frames} whole frames are not read')
    return copy_path


def _decrypted_output_dir(context, db_path):
    """A folder of its own for each searchpartyd folder, in this artifact's report folder."""
    digest = hashlib.sha1(str(_store_root(db_path)).encode('utf-8', 'surrogateescape')).hexdigest()[:12]
    return os.path.join(context.get_report_folder(), DECRYPTED_FOLDER, digest)


_decrypted_copies = {}


def _decrypted_copy(context, db_path, service):
    """The decrypted copy of one store, made once per report folder however many artifacts read it."""
    output_dir = _decrypted_output_dir(context, db_path)
    cache_key = (output_dir, os.path.basename(db_path))
    if cache_key not in _decrypted_copies:
        _decrypted_copies[cache_key] = decrypt_searchpartyd_db(db_path, service, output_dir)
    return _decrypted_copies[cache_key]


KEY_DATABASE_SERVICE = 'KeyDatabase'


def _beacon_attributes(context, files_found):
    """The name and emoji of each beacon in the BeaconAttributes table of each store's ItemSharingKeys.db,
    read in its current state, keyed by searchpartyd folder and then upper-case beacon identifier.
    Returns ({folder: {beacon: (name, emoji)}}, [the stores that held a name or an emoji])."""
    found = {}
    read = []
    for db_path in sorted(str(path) for path in files_found
                          if os.path.basename(str(path)) == 'ItemSharingKeys.db' and _store_root(str(path))):
        copy_path = _decrypted_copy(context, db_path, KEY_DATABASE_SERVICE)
        if copy_path is None:
            continue
        values = {}
        try:
            for row in get_sqlite_db_records(copy_path, 'SELECT beaconIdentifier, name, emoji FROM BeaconAttributes'):
                beacon, name, emoji = tuple(row)
                if not isinstance(beacon, str) or not beacon:
                    continue
                names, emojis = values.setdefault(beacon.upper(), ([], []))
                if isinstance(name, str) and name:
                    names.append(name)
                if isinstance(emoji, str) and emoji:
                    emojis.append(emoji)
        except sqlite3.Error as ex:
            # The beacon rows are still reported, without names from this store.
            logfunc(f'{db_path}: BeaconAttributes not read: {ex}; beacon names from it are left out')
            continue
        if any(names or emojis for names, emojis in values.values()):
            read.append(db_path)  # cited only where it supplied a name or an emoji
        found[_store_root(db_path)] = {beacon: (', '.join(dict.fromkeys(names)), ', '.join(dict.fromkeys(emojis)))
                                       for beacon, (names, emojis) in values.items()}
    return found, read


def _beacon_names(records, attributes):
    """A beacon's name: from its BeaconNamingRecord, else from BeaconAttributes in ItemSharingKeys.db."""
    names = {beacon: name for beacon, (name, _emoji) in attributes.items() if name}
    names.update(_names(records))
    return names


_WAL_KINDS = (KIND_COMMITTED, KIND_EARLIER, KIND_UNCOMMITTED)
_ORIGIN_LIVE = 'Live'
_ORIGIN_RECOVERED = 'Recovered'
_METHOD_WAL_STATES = 'WAL committed states'
_METHOD_WAL_UNCOMMITTED = 'WAL uncommitted frames'


def _recovery_location(name, spans):
    """(method, location) for a key read in the states spans names."""
    parts = []
    committed, earlier = spans['committed'], spans['earlier']
    if committed:
        first, last = committed
        if last == 0:
            parts.append(f'{name} without its log, state 0')
        elif first == 0:
            parts.append(f'{name} and {name}-wal, committed states 0 to {last}')
        else:
            states = f'state {first}' if first == last else f'states {first} to {last}'
            parts.append(f'{name}-wal, committed {states}')
    if earlier:
        first, last = earlier
        commits = f'commit {first}' if first == last else f'commits {first} to {last}'
        parts.append(f'{name}-wal, previous log generation, left-over {commits}')
    if not parts:
        return _METHOD_WAL_UNCOMMITTED, f'{name}-wal, frames after the last commit'
    return _METHOD_WAL_STATES, '; '.join(parts)


OBSERVATIONS_QUERY = '''
    SELECT ObservedAdvertisement.scanDate, ObservedAdvertisementLocation.timestamp,
           ObservedAdvertisementLocation.latitude, ObservedAdvertisementLocation.longitude,
           ObservedAdvertisementLocation.horizontalAccuracy,
           ObservedAdvertisementBeaconInfo.beaconIdentifier, ObservedAdvertisement.macAddress,
           ObservedAdvertisement.rssi, ObservedAdvertisement.advertisementData,
           ObservedAdvertisement.advId
    FROM ObservedAdvertisement
    LEFT JOIN ObservedAdvertisementLocation
        ON ObservedAdvertisementLocation.advId = ObservedAdvertisement.advId
    LEFT JOIN ObservedAdvertisementBeaconInfo
        ON ObservedAdvertisementBeaconInfo.advId = ObservedAdvertisement.advId
'''


def _stored_utc(value):
    """A stored text time (2024-01-31T12:34:56.789, no zone) as a UTC datetime, or ''."""
    if not isinstance(value, str):
        return ''
    try:
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f').replace(tzinfo=timezone.utc)
    except ValueError:
        try:
            return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
        except ValueError:
            logfunc(f'Find My Observed Advertisements: a time not in the stored layout is not read: '
                    f'{len(value)} characters')
            return ''


def _hex(value, separator=None):
    if not isinstance(value, (bytes, bytearray)) or not value:
        return ''
    return bytes(value).hex(separator) if separator else bytes(value).hex()


# Advertisement rows come in two shapes. One with an ObservedAdvertisementLocation row is reported
# as a row. The others are counted per searchpartyd folder, beacon (or none) and UTC day, since a
# store can hold far more of them than a report table can show; their stored columns other than the
# time, beacon and rssi are not reported.
LOCATED = ' WHERE ObservedAdvertisementLocation.advId IS NOT NULL'
BY_ID = ' WHERE ObservedAdvertisement.advId IN ({})'
DAY_QUERY = '''
    SELECT max(ObservedAdvertisementBeaconInfo.beaconIdentifier), substr(ObservedAdvertisement.scanDate, 1, 10),
           count(*), min(ObservedAdvertisement.scanDate), max(ObservedAdvertisement.scanDate),
           min(ObservedAdvertisement.rssi), max(ObservedAdvertisement.rssi)
    FROM ObservedAdvertisement
    LEFT JOIN ObservedAdvertisementLocation
        ON ObservedAdvertisementLocation.advId = ObservedAdvertisement.advId
    LEFT JOIN ObservedAdvertisementBeaconInfo
        ON ObservedAdvertisementBeaconInfo.advId = ObservedAdvertisement.advId
    WHERE ObservedAdvertisementLocation.advId IS NULL
    GROUP BY upper(coalesce(ObservedAdvertisementBeaconInfo.beaconIdentifier, '')),
             substr(ObservedAdvertisement.scanDate, 1, 10)
'''
_RANKS = {KIND_COMMITTED: 2, KIND_EARLIER: 1, KIND_UNCOMMITTED: 0}
_FETCH_CHUNK = 500
_observations_cache = {}


def _add_to_day(days, beacon, scan, rssi, count=1, last=None, rssi_max=None, recovered=0):
    """Fold advertisements into the (beacon, UTC day) summary."""
    beacon = _text(beacon)
    day = scan[:10] if isinstance(scan, str) else ''
    entry = days.setdefault((beacon.upper(), day), {'beacon': beacon, 'day': day, 'count': 0, 'recovered': 0,
                                                    'first': None, 'last': None, 'rssi': []})
    entry['count'] += count
    entry['recovered'] += recovered
    for value, keep in ((scan, min), (last if last is not None else scan, max)):
        if isinstance(value, str):
            slot = 'first' if keep is min else 'last'
            entry[slot] = value if entry[slot] is None else keep(entry[slot], value)
    entry['rssi'] += [value for value in (rssi, rssi_max) if isinstance(value, int)]


def _wal_recovered(copy_path, current_ids, label):
    """Advertisements another readable state of the log holds and the current state does not.

    Only advId is compared from state to state; the full row of each missing advertisement is then
    read from the newest state holding it (a committed state, else the previous generation's
    left-over frames, else the frames after the last commit), with that state's own joins.
    Returns ({advId: (row, method, location)}, location advIds seen in any state).
    """
    best = {}
    spans = {}
    located_any = set()
    try:
        with WalStates(str(copy_path), include=_WAL_KINDS) as wal:
            for position, state in enumerate(wal.states()):
                if position == 0:
                    continue  # the current state, read normally by the caller
                try:
                    ids = {row[0] for row in state.connection.execute('SELECT advId FROM ObservedAdvertisement')}
                    located_any.update(row[0] for row in state.connection.execute(
                        'SELECT advId FROM ObservedAdvertisementLocation'))
                except sqlite3.Error:
                    continue  # the tables do not exist yet in this state
                rank = _RANKS.get(state.kind, 0)
                missing = ids - current_ids
                for adv_id in missing:
                    span = spans.setdefault(adv_id, {'committed': None, 'earlier': None})
                    slot = 'committed' if state.kind == KIND_COMMITTED else \
                        'earlier' if state.kind == KIND_EARLIER else None
                    if slot:
                        old = span[slot]
                        span[slot] = (state.number, state.number) if old is None else \
                            (min(old[0], state.number), max(old[1], state.number))
                wanted = sorted(adv_id for adv_id in missing if adv_id not in best or best[adv_id][0] < rank)
                fetched = {}
                try:
                    for start in range(0, len(wanted), _FETCH_CHUNK):
                        chunk = wanted[start:start + _FETCH_CHUNK]
                        query = OBSERVATIONS_QUERY + BY_ID.format(', '.join('?' * len(chunk)))
                        for row in state.connection.execute(query, chunk):
                            fetched[row[-1]] = (rank, tuple(row))
                except sqlite3.Error as ex:
                    # Only this state is skipped; what earlier states gave is kept.
                    logfunc(f'{label}: advertisements not read from one state of the log: {ex}')
                    continue
                best.update(fetched)
            if wal.log:
                logfunc(f'{label}: {wal.summary()}')
    except (sqlite3.Error, OSError) as ex:
        logfunc(f'{label}: write-ahead log not read: {ex}')
        return {}, located_any
    name = os.path.basename(str(copy_path))
    return ({adv_id: (row, *_recovery_location(name, spans[adv_id])) for adv_id, (_rank, row) in best.items()},
            located_any)


def _read_observations(copy_path, label):
    """The located advertisement rows and the per-day summary of the rest, for one decrypted store,
    read once however many artifacts ask. Returns None where the store cannot be queried."""
    if copy_path in _observations_cache:
        return _observations_cache[copy_path]
    try:
        located = [(tuple(row), _ORIGIN_LIVE, '', '')
                   for row in get_sqlite_db_records(copy_path, OBSERVATIONS_QUERY + LOCATED)]
        days = {}
        for beacon, _day, count, first, last, rssi_min, rssi_max in get_sqlite_db_records(copy_path, DAY_QUERY):
            _add_to_day(days, beacon, first, rssi_min, count, last, rssi_max)
        current_ids = {row[0] for row in get_sqlite_db_records(copy_path, 'SELECT advId FROM ObservedAdvertisement')}
        head_located = {row[0] for row in get_sqlite_db_records(
            copy_path, 'SELECT advId FROM ObservedAdvertisementLocation')}
    except sqlite3.Error as ex:
        logfunc(f'{label}: error reading the decrypted store: {ex}')
        _observations_cache[copy_path] = None
        return None
    recovered, located_any = _wal_recovered(copy_path, current_ids, label)
    for adv_id, (row, method, location) in recovered.items():
        if row[1] is not None or row[2] is not None:
            located.append((row, _ORIGIN_RECOVERED, method, location))
        else:
            _add_to_day(days, row[5], row[0], row[7], recovered=1)
            if adv_id in located_any:
                head_located.discard(adv_id)
                current_ids.add(adv_id)  # counted with the current ones below
    earlier_only = len((current_ids - head_located) & located_any)
    if earlier_only:
        logfunc(f'{label}: {earlier_only} advertisements have a location row only in a state of the log older than '
                'the one they are read from; they are summarized per day without it')
    _observations_cache[copy_path] = (located, days)
    return _observations_cache[copy_path]


def _observation_stores(context):
    """(store folder, original path, decrypted reading, names, owned, shared) for each Observations.db
    that opens, and the ItemSharingKeys.db stores whose names were used."""
    files_found = [str(path) for path in context.get_files_found()]
    stores = _read_store(files_found)
    attributes, attribute_sources = _beacon_attributes(context, files_found)
    found = []
    for db_path in sorted(path for path in files_found
                          if os.path.basename(path) == 'Observations.db' and _store_root(path) is not None):
        copy_path = _decrypted_copy(context, db_path, OBSERVATIONS_SERVICE)
        reading = _read_observations(copy_path, f'{db_path}') if copy_path else None
        if reading is None:
            continue
        root = _store_root(db_path)
        records = stores.get(root, {})
        found.append((db_path, reading, _beacon_names(records, attributes.get(root, {})),
                      _identifiers(records, 'OwnedBeacons'), _identifiers(records, 'SharedBeacons')))
    roots = {_store_root(db_path) for db_path, *_rest in found}
    return found, [path for path in attribute_sources if _store_root(path) in roots]


def _beacon_kind(beacon, owned, shared):
    return 'OwnedBeacons' if beacon and beacon.upper() in owned else \
        'SharedBeacons' if beacon and beacon.upper() in shared else ''


@artifact_processor
def findMyObservedAdvertisements(context):
    data_headers = (('Scan Date', 'datetime'), ('Location Timestamp', 'datetime'), ('Latitude', 'latitude'),
                    ('Longitude', 'longitude'), 'Horizontal Accuracy', 'Beacon Name', 'Beacon Record',
                    'Beacon Identifier', 'macAddress (hex)', 'rssi (as stored)', 'Advertisement Data (hex)',
                    'Advertisement ID', 'Record Origin', 'Recovery Method', 'Recovery Location')
    data_list = []
    found, attribute_sources = _observation_stores(context)
    for _db_path, (located, _days), names, owned, shared in found:
        for row, origin, method, location in located:
            scan, located_at, latitude, longitude, accuracy, beacon, mac, rssi, advertisement, adv_id = row
            beacon = _text(beacon)
            data_list.append((_stored_utc(scan), _stored_utc(located_at), _value(latitude), _value(longitude),
                              _value(accuracy), names.get(beacon.upper(), '') if beacon else '',
                              _beacon_kind(beacon, owned, shared), beacon, _hex(mac, ':'), _value(rssi),
                              _hex(advertisement), adv_id, origin, method, location))
    sources = [db_path for db_path, *_rest in found] + attribute_sources
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def findMyObservedAdvertisementDays(context):
    data_headers = (('First Scan Date', 'datetime'), ('Last Scan Date', 'datetime'), 'Day (UTC)', 'Beacon Name',
                    'Beacon Record', 'Beacon Identifier', ('Advertisements', 'number'),
                    ('Recovered Advertisements', 'number'), ('rssi Minimum (as stored)', 'number'),
                    ('rssi Maximum (as stored)', 'number'))
    data_list = []
    found, attribute_sources = _observation_stores(context)
    for _db_path, (_located, days), names, owned, shared in found:
        for entry in days.values():
            beacon = entry['beacon']
            data_list.append((_stored_utc(entry['first']), _stored_utc(entry['last']), entry['day'],
                              names.get(beacon.upper(), '') if beacon else '', _beacon_kind(beacon, owned, shared),
                              beacon, entry['count'], entry['recovered'],
                              min(entry['rssi']) if entry['rssi'] else '', max(entry['rssi']) if entry['rssi'] else ''))
    data_list.sort(key=lambda row: (row[2], row[5]))
    sources = [db_path for db_path, *_rest in found] + attribute_sources
    return data_headers, data_list, '\n'.join(sources)


# Daily advertisement keys of an owned beacon. Apple's Find My Network Accessory Specification
# (sections 6.3.4 and 5.1.3) derives them from the beacon's secondary shared secret, as summarized in
# joshuahickman1/Lost_Apples (src/key_schedule_generator.py lines 19 to 27 at 9ec8597a): each day's
# secret is the ANSI X9.63 KDF (SHA-256) of the day before's with "update"; the KDF of that with
# "diversify" gives two 36 byte values u and v, each reduced to a P-224 scalar; the day's key is the
# point u*P + v*G, which equals (d*u + v)*G for the beacon's private scalar d. The 28 byte
# x coordinate is the advertisement key, and its first 6 bytes with the top two bits of the first set
# are the advertised MAC address.
P224_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFF16A2E0B8F03E13DD29455C5C2A3D
PRIVATE_KEY_LENGTH = 85  # 0x04, x (28 bytes), y (28 bytes), d (28 bytes)
PUBLIC_KEY_LENGTH = 57   # 0x04, x, y
DAY_MARGIN = 2


def _x963_kdf(secret, info, length):
    out, counter = b'', 1
    while len(out) < length:
        out += hashlib.sha256(secret + counter.to_bytes(4, 'big') + info).digest()
        counter += 1
    return out[:length]


def _daily_keys(secondary_secret, private_scalar, days):
    """(day index, 28 byte advertisement key) for days 1 to days."""
    secret = secondary_secret
    for index in range(1, days + 1):
        secret = _x963_kdf(secret, b'update', 32)
        derived = _x963_kdf(secret, b'diversify', 72)
        u = int.from_bytes(derived[:36], 'big') % (P224_ORDER - 1) + 1
        v = int.from_bytes(derived[36:], 'big') % (P224_ORDER - 1) + 1
        point = ECC.construct(curve='P-224', d=(private_scalar * u + v) % P224_ORDER).pointQ
        yield index, int(point.x).to_bytes(28, 'big')


def _key_data(record, field):
    value = record.get(field)
    value = value.get('key') if isinstance(value, dict) else None
    value = value.get('data') if isinstance(value, dict) else None
    return bytes(value) if isinstance(value, (bytes, bytearray)) else None


def _private_scalar(record):
    """The beacon's P-224 private scalar, checked against its own public key, or None."""
    private, public = _key_data(record, 'privateKey'), _key_data(record, 'publicKey')
    if not private or len(private) != PRIVATE_KEY_LENGTH or not public or len(public) != PUBLIC_KEY_LENGTH:
        return None
    scalar = int.from_bytes(private[-28:], 'big')
    try:
        point = ECC.construct(curve='P-224', d=scalar).pointQ
    except ValueError:
        return None
    return scalar if int(point.x).to_bytes(28, 'big') == public[1:29] else None


def _recorded_macs(context, files_found):
    """(first, last) scanDate of each (beacon, MAC address) in the current state of each store's
    Observations.db, keyed by store folder, and the latest scanDate in each store."""
    found, latest = {}, {}
    for db_path in sorted(path for path in files_found
                          if os.path.basename(path) == 'Observations.db' and _store_root(path) is not None):
        copy_path = _decrypted_copy(context, db_path, OBSERVATIONS_SERVICE)
        if copy_path is None:
            continue
        macs = {}
        for beacon, mac, first, last in get_sqlite_db_records(copy_path, '''
                SELECT upper(ObservedAdvertisementBeaconInfo.beaconIdentifier), ObservedAdvertisement.macAddress,
                       min(ObservedAdvertisement.scanDate), max(ObservedAdvertisement.scanDate)
                FROM ObservedAdvertisement
                JOIN ObservedAdvertisementBeaconInfo
                    ON ObservedAdvertisementBeaconInfo.advId = ObservedAdvertisement.advId
                GROUP BY 1, 2'''):
            if isinstance(mac, (bytes, bytearray)):
                macs[(beacon, bytes(mac))] = (first, last)
        root = _store_root(db_path)
        found[root] = macs
        times = [_stored_utc(last) for _first, last in macs.values()]
        latest[root] = max((t for t in times if t), default=None)
    return found, latest


@artifact_processor
def findMyBeaconDailyAddresses(context):
    data_headers = ('Estimated Date (UTC)', ('Recorded First', 'datetime'), ('Recorded Last', 'datetime'),
                    'Beacon Name', 'Beacon Identifier', 'Key Index', 'MAC Address', 'Advertisement Key (hex)')
    data_list = []
    sources = []
    files_found = [str(path) for path in context.get_files_found()]
    recorded, latest_scan = _recorded_macs(context, files_found)
    for root, records in _read_store(files_found).items():
        names = _names(records)
        estimated = _estimates(records)
        macs = recorded.get(root, {})
        ends = [latest_scan.get(root)] + [time for times in estimated.values() for time in times if time]
        end = max((time for time in ends if time), default=None)
        for file_found, record in records.get('OwnedBeacons', []):
            identifier = _text(record.get('identifier'))
            secondary = _key_data(record, 'secondarySharedSecret')
            pairing = _date(record.get('pairingDate'))
            if not secondary:
                continue  # no daily keys (counted in the log below)
            scalar = _private_scalar(record)
            if scalar is None or not pairing:
                logfunc(f'{file_found}: key material or pairing date not in the layout read here; '
                        'no daily addresses derived')
                continue
            days = max(((end or pairing) - pairing).days, 0) + DAY_MARGIN
            sources.append(file_found)
            for index, key in _daily_keys(secondary, scalar, days):
                mac = bytes([key[0] | 0xC0]) + key[1:6]
                first, last = macs.get((identifier.upper(), mac), (None, None))
                data_list.append(((pairing + timedelta(days=index)).date().isoformat(), _stored_utc(first),
                                  _stored_utc(last), names.get(identifier.upper(), ''), identifier, index,
                                  mac.hex(':'), key.hex()))
        without = sum(1 for _f, record in records.get('OwnedBeacons', [])
                      if not _key_data(record, 'secondarySharedSecret'))
        if without:
            logfunc(f'Find My Beacon Daily Addresses: {without} owned beacons hold no secondarySharedSecret and '
                    'have no daily addresses')
    sources += [path for path in files_found if os.path.basename(path) == 'Observations.db'
                and _store_root(path) in {_store_root(source) for source in sources}]
    return data_headers, data_list, '\n'.join(sources)
