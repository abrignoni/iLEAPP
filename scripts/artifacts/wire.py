__artifacts_v2__ = {
    "wireAccountFiles": {
        "name": "Wire Secure Messenger Accounts",
        "description": "Wire accounts stored in the app group's Accounts folder, one row per account file, with "
                       "display name, handle, email address, team, login flags, the stored unread count, the "
                       "profile picture, and whether the account is the one the app has selected.",
        "author": "@kalink0",
        "creation_date": "2026-11-08",
        "last_update_date": "2026-11-11",
        "requirements": "",
        "category": "Wire Messenger",
        "notes": "Each file under AppGroup/<group>/Accounts named by a UUID is Wire's JSON encoding of its "
                 "Account class, written by AccountStore under the account's user identifier as an "
                 "uppercase uuidString "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/WireDomain/Sources/WireDomain/Account/AccountStore.swift#L96-L101, "
                 "https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/WireDomain/Sources/WireDomain/Account/AccountStore.swift#L166-L167). "
                 "The keys read are those of Account's CodingKeys: name, team, identifier, handle, "
                 "backendName, image, teamImage, unreadConversationCount, loginCredentials and "
                 "lastSSOIdentityProviderID "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/Account/Account.swift#L40-L51); "
                 "a key absent from a file leaves its column blank. A file is read only when it is a JSON "
                 "object carrying identifier and name. In the code read, a plain logout keeps the file "
                 "(logoutCurrentSession passes deleteAccount: false, "
                 "https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-sync-engine/Source/SessionManager/SessionManager.swift#L887-L889) "
                 "and deleting the account's data removes it "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-sync-engine/Source/SessionManager/SessionManager.swift#L1311, "
                 "https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/WireDomain/Sources/WireDomain/Account/AccountStore.swift#L119-L121), "
                 "so a row is an account the app holds, not evidence that it is logged in. Selected is "
                 "Yes when the AccountManagerSelectedAccountKey of the same app group's "
                 "group.com.wearezeta.zclient.ios.plist names the account, which is where AccountManager "
                 "keeps the selected account "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/WireDomain/Sources/WireDomain/Account/AccountManager.swift#L254-L266), "
                 "No when that plist names another account or none, and blank when no such plist was "
                 "found. Account ID is the identifier key; where it differs from the file name, both are "
                 "given. Uses Company Login is loginCredentials.usesCompanyLogin as stored. In the code "
                 "read, a user's credentials take it from the user's usesCompanyLogin, which is set when "
                 "the backend's user record carries an sso_id subject "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-sync-engine/Source/UserSession/PreLoginAuthenticationNotification.swift#L24-L29, "
                 "https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/User/ZMUser.m#L434-L437), "
                 "Other callers of the LoginCredentials initialiser were not read. "
                 "Has Password is loginCredentials.hasPassword as stored; the LoginCredentials read has no "
                 "such field and the older writer was not read. Unread Count (as stored) is "
                 "unreadConversationCount as of the last time the file was written, not of the extraction. "
                 "SessionManager writes it from the number of unread conversations and also from a count "
                 "its caller passes for the app icon badge, which was not read "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-sync-engine/Source/SessionManager/SessionManager.swift#L1827, "
                 "https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-sync-engine/Source/SessionManager/SessionManager.swift#L1837-L1841). "
                 "Profile Picture and Team Picture are the image and teamImage values decoded from "
                 "base64, with their type taken from the decoded bytes. On iphone11_ios17 the one account "
                 "file was named by the same UUID as the AccountData folder, was the selected account, "
                 "its image decoded as a PNG, and its identifier, name and email address matched the "
                 "ZUSER row that ZSESSION.ZSELFUSER names in that folder's store.wiredatabase (identifier "
                 "apart from letter case). On iphone11_ios17 Handle, Team, Backend, Last SSO Identity "
                 "Provider ID and Team Picture were blank, because that file had no handle, team, "
                 "backendName, lastSSOIdentityProviderID or teamImage key. The Wire code cited is at commit 851bba15 and was not "
                 "compared with the builds on the corpora below.",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/Accounts/????????-????-????-????-????????????',
                  '*/mobile/Containers/Shared/AppGroup/*/Library/Preferences/group.com.wearezeta.zclient.ios.plist'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | Wire • Secure Messenger 3.111.9 | 1 row",
        }
    },
    "wireAccount": {
        "name": "Wire Secure Messenger Users and Clients",
        "description": "Wire users joined to the clients recorded for them (ZUSER LEFT JOIN ZUSERCLIENT), one row "
                       "per user and client, with handle, display name, phone and email as stored, the user ID as a UUID, and each client's "
                       "ID, device class, label, model and activation, discovery and last active dates, and, where "
                       "the schema has them, the client's activation location as Latitude and Longitude. The query "
                       "is not limited to the account signed in on the device.",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2024-01-21",
        "last_update_date": "2026-11-11",
        "requirements": "",
        "category": "Wire Messenger",
        "notes": "Each result of ZUSER LEFT JOIN ZUSERCLIENT is reported without DISTINCT: a user with several "
                 "clients gives one row per client, and a user with no client gives one row with the client "
                 "columns blank. Clients with no matching ZUSER are not selected. Every "
                 "AccountData/<account>/store/store.wiredatabase found is read, and Account is that "
                 "folder's name, uppercased; Latitude and Longitude are blank for a database whose "
                 "schema lacks them. On iphone11_ios17 Account held one value on all 13 rows, the image's "
                 "only account; a tree holding that account twice, under two account folders, gave "
                 "exactly twice the rows, each account's from its own folder. No device with two Wire "
                 "accounts was available. Client ID is ZUSERCLIENT.ZREMOTEIDENTIFIER. Handle is "
                 "ZUSER.ZHANDLE, the handle attribute of Wire's User entity, which Wire's header describes as "
                 "the \"@name\" handle "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Public/ZMUser.h#L55-L56). "
                 "ZMUser.m writes it from the handle field of the backend's user record "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/User/ZMUser.m#L484-L487) and from search "
                 "results (https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/User/ZMUser.m#L562-L573), "
                 "and the app's settings let the account owner choose one, shown after an @ prefix and sent "
                 "to /self/handle "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios/Wire-iOS/Sources/UserInterface/Settings/ChangingDetails/ChangeHandleViewController.swift#L101, "
                 "https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios/Wire-iOS/Sources/UserInterface/Settings/ChangingDetails/ChangeHandleViewController.swift#L328-L329, "
                 "https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-sync-engine/Source/Synchronization/Strategies/UserProfileUpdateRequestStrategy.swift#L142-L145). "
                 "User ID is ZUSER.ZREMOTEIDENTIFIER_DATA, the remoteIdentifier_data attribute of the User entity "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/WireData/Sources/WireData/Schema/zmessaging.xcdatamodeld/zmessaging2.144.0.xcdatamodel/contents#L381). "
                 "Wire reads its 16 bytes as the uuid_t of an NSUUID and writes NSUUID.data, which is getUUIDBytes "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/ZMManagedObject.m#L178-L209, "
                 "https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-utilities/Source/NSUUID+Data.m#L23-L27), through the remoteIdentifier accessor in ZMUser.swift "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/User/ZMUser.swift#L343-L359) "
                 "and the _data key suffix (https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/ZMManagedObject.m#L27), "
                 "so the bytes are shown in stored order as a lowercase UUID; a value that is not 16 bytes is shown as "
                 "hex. "
                 "When ZMUser.m updates a user from the backend's user record, it sets the ID only if none is stored, "
                 "and an update carrying a different ID fails a RequireString check, which crashes rather than "
                 "replacing it (https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/User/ZMUser.m#L442-L472, "
                 "https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-system/Source/ZMSAsserts.h#L54-L58), "
                 "while the same update replaces the handle whenever it carries one "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/User/ZMUser.m#L484-L487) "
                 "and the account owner can send a new one to /self/handle "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios/Wire-iOS/Sources/UserInterface/Settings/ChangingDetails/ChangeHandleViewController.swift#L328-L329). "
                 "User ID was filled on every ZUSER row of hickman_ios13 (2 of 2) and iphone11_ios17 (4 of 4), both "
                 "for the user that ZSESSION.ZSELFUSER names "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/WireData/Sources/WireData/Schema/zmessaging.xcdatamodeld/zmessaging2.144.0.xcdatamodel/contents#L301-L302) "
                 "and for the others. On both, which hold the same account, the self user's User ID matches the "
                 "AccountData folder name apart from letter case; Wire builds that folder from the account's user "
                 "identifier as a Swift uuidString, which is uppercase "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/ManagedObjectContext/CoreDataStack.swift#L455-L458). "
                 "No second record of the other users' IDs was checked. "
                 "In the Wire code read, "
                 "Client ID, Device Class, Device Label, Device Model, Activation Date and Last Active Date are "
                 "written from the backend's record of the client (id, class, label, model, time and "
                 "last_active) (https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/UserClient/UserClient.swift#L358-L379, "
                 "https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/WireDomain/Sources/WireDomain/Repositories/UserClients/UserClientsLocalStore.swift#L124-L130). "
                 "The self client's label, model and device class are also set locally when that client is "
                 "created, with device class derived from the model name "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/UserClient/UserClient.swift#L140-L153). Discovery Date "
                 "is set to the current time when UserClient.swift creates a client record it did not already "
                 "have (https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/UserClient/UserClient.swift#L202-L209); "
                 "UserClientsLocalStore.swift also sets it from a date its caller supplies, and that caller was "
                 "not read (https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/WireDomain/Sources/WireDomain/Repositories/UserClients/UserClientsLocalStore.swift#L199-L204). "
                 "That code is newer than the Wire builds on the corpora below, and the older writer was not "
                 "read. Dates are Core Data timestamps converted to UTC. On every corpus below no row has both "
                 "Activation Date and Discovery Date, so Activation Date, which leads the table, is blank on the "
                 "rows that carry a Discovery Date (iphone11_ios17: filled on 5 of 13 rows). Discovery Date has "
                 "no value on any row of iphone12_ios18 and jess_ios15. Last Active Date is blank where the "
                 "schema has no ZLASTACTIVEDATE column (hickman_ios13, hickman_ios14, iphone11_ios17, "
                 "jess_ios15). Phone Number is blank where the schema has no ZPHONENUMBER column (hc_ios18_7, "
                 "iphone12_ios18) and held no value on any row of iphone11_ios17 and jess_ios15. On hickman_ios13 "
                 "the 12 rows are 12 clients of 2 users; on hickman_ios14 the 10 rows are 9 clients of 2 users "
                 "and 1 user with no client; no two rows are equal on any corpus below. Source ownership and "
                 "self-account identity are not established here. Original contribution credited to Elliot "
                 "Glendye.",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/AccountData/*/store/store.wiredatabase*'),
        "output_types": "all",
        "artifact_icon": "user",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | Wire • Secure Messenger 4.16.3 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | Wire • Secure Messenger 3.111.9 | 13 rows",
            "iphone12_ios18": "iOS 18.7 | Wire • Secure Messenger 4.10.0 | 2 rows",
            "hickman_ios13": "iOS 13.3.1 | Wire • Secure Messenger 3.54 | 12 rows",
            "hickman_ios14": "iOS 14.3 | Wire • Secure Messenger 3.73 | 10 rows",
            "jess_ios15": "iOS 15.0.2 | Wire • Secure Messenger 3.94 | 1 row",
        }
    },
    "wireMessages": {
        "name": "Wire Secure Messenger Messages",
        "description": "Wire messages with direction, sender handle, user ID and display name, conversation, "
                       "conversation type and message type, the cached media file where Wire's asset cache "
                       "holds one, and the stored duration of call records",
        "author": 'Elliot Glendye, @AlexisBrignoni, Codex, @kalink0',
        "creation_date": "2024-01-21",
        "last_update_date": '2026-11-11',
        "requirements": "",
        "category": "Wire Messenger",
        "notes": "Rows with category 1 (undefined per the Wire source) are excluded; rows with "
                 "no stored category are retained. Handle, User ID and Display Name come from the ZUSER row that "
                 "ZMESSAGE.ZSENDER points to (LEFT JOIN), so they are blank when no such row exists. Handle "
                 "is ZUSER.ZHANDLE, the handle attribute of Wire's User entity, which Wire's header describes "
                 "as the \"@name\" handle "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Public/ZMUser.h#L55-L56). "
                 "ZMUser.m writes it from the handle field of the backend's user record "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/User/ZMUser.m#L484-L487) and from search "
                 "results (https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/User/ZMUser.m#L562-L573). "
                 "User ID is ZUSER.ZREMOTEIDENTIFIER_DATA, the remoteIdentifier_data attribute of the User entity "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/WireData/Sources/WireData/Schema/zmessaging.xcdatamodeld/zmessaging2.144.0.xcdatamodel/contents#L381). "
                 "Wire reads its 16 bytes as the uuid_t of an NSUUID and writes NSUUID.data, which is getUUIDBytes "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/ZMManagedObject.m#L178-L209, "
                 "https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-utilities/Source/NSUUID+Data.m#L23-L27), through the remoteIdentifier accessor in ZMUser.swift "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/User/ZMUser.swift#L343-L359) "
                 "and the _data key suffix (https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/ZMManagedObject.m#L27), "
                 "so the bytes are shown in stored order as a lowercase UUID; a value that is not 16 bytes is shown as "
                 "hex. "
                 "When ZMUser.m updates a user from the backend's user record, it sets the ID only if none is stored, "
                 "and an update carrying a different ID fails a RequireString check, which crashes rather than "
                 "replacing it (https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/User/ZMUser.m#L442-L472, "
                 "https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-system/Source/ZMSAsserts.h#L54-L58), "
                 "while the same update replaces the handle whenever it carries one "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/User/ZMUser.m#L484-L487) "
                 "and the account owner can send a new one to /self/handle "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios/Wire-iOS/Sources/UserInterface/Settings/ChangingDetails/ChangeHandleViewController.swift#L328-L329, "
                 "https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-sync-engine/Source/Synchronization/Strategies/UserProfileUpdateRequestStrategy.swift#L142-L145). "
                 "User ID was filled on every ZUSER row of hickman_ios13 (2 of 2) and iphone11_ios17 (4 of 4), both "
                 "for the user that ZSESSION.ZSELFUSER names "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/WireData/Sources/WireData/Schema/zmessaging.xcdatamodeld/zmessaging2.144.0.xcdatamodel/contents#L301-L302) "
                 "and for the others. On both, which hold the same account, the self user's User ID matches the "
                 "AccountData folder name apart from letter case; Wire builds that folder from the account's user "
                 "identifier as a Swift uuidString, which is uppercase "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/ManagedObjectContext/CoreDataStack.swift#L455-L458). "
                 "No second record of the other users' IDs was checked. "
                 "That code is newer than the Wire "
                 "builds on the corpora below. "
                 "Message is the ZNORMALIZEDTEXT column as stored. "
                 "Message Type is Call where ZSYSTEMMESSAGETYPE is 18 and Missed Call where it is 7, "
                 "performedCall and missedCall of Wire's ZMSystemMessageType "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Public/ZMMessage.h#L74-L93), "
                 "and otherwise follows ZCACHEDCATEGORY. In the build read for calls (tag 3.111.7), the "
                 "Call row is written when the call ends, with the caller as sender, the current time as "
                 "its server timestamp and the seconds since the call was established as its duration, "
                 "or 0 for an outgoing call that was never established; an incoming call that was never "
                 "established is written as Missed Call instead "
                 "(https://github.com/wireapp/wire-ios/blob/7245c2abed9462dba9947045df35f2a5290947c0/wire-ios-sync-engine/Source/Calling/SystemMessageCallObserver.swift#L47-L72, "
                 "https://github.com/wireapp/wire-ios/blob/7245c2abed9462dba9947045df35f2a5290947c0/wire-ios-data-model/Source/Model/Conversation/Calling/ZMConversation%2BCalling.swift#L44-L64, "
                 "https://github.com/wireapp/wire-ios/blob/7245c2abed9462dba9947045df35f2a5290947c0/wire-ios-data-model/Source/Model/Conversation/ZMConversation%2BSecurityLevel.swift#L588-L608). "
                 "For a Call row, Date / Time is therefore when the call ended on the device's clock, "
                 "Direction says who placed the call, Call Duration (seconds) is ZDURATION and Call "
                 "Connected is Date / Time minus that duration, which is when the call was established, "
                 "not when it started ringing; Call Connected is blank where the duration is 0. "
                 "The newer code read marks performedCall as deprecated "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Public/ZMMessage.h#L93). "
                 "Whether it still writes the row was not read. "
                 "ZDURATION belongs to the SystemMessage entity only "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/WireData/Sources/WireData/Schema/zmessaging.xcdatamodeld/zmessaging2.144.0.xcdatamodel/contents#L309) "
                 "and is not reported for other system message types; on iphone11_ios17 it was filled on "
                 "the 10 Call rows and held 0.0 on the one other system message. On iphone11_ios17 the "
                 "Call rows for the incoming and the outgoing audio call of 5 January 2024 give Call "
                 "Connected times of 17:12:33 and 17:15:09 UTC, matching the 12:12 and 12:15 local times "
                 "in the image's documentation, and Direction Incoming and Outgoing as documented. "
                 "Call Connected, like Date / Time, is shown to the whole second. "
                 "Media is the file in Library/Caches/wire-account-<account> whose name is Wire's cache key "
                 "for the message, the hex SHA-256 of the message nonce, the sender's user ID and the "
                 "conversation ID, each as a lowercase UUID, and the format, joined with underscores "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/Message/FileAssetCache.swift#L827-L847, "
                 "https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-transport/Source/TransportEncoding/UUID%2BTransportCoding.swift#L23-L25); "
                 "the original is shown where it is cached, else the medium, else the preview, else the "
                 "file under the key with no format; an "
                 "encrypted copy is never shown here, so a message whose file is cached only encrypted "
                 "has a blank Media and its file appears in Wire Secure Messenger Media. The account "
                 "is the AccountData folder the database sits in. A message whose file is not in the cache "
                 "has a blank Media, which says nothing about whether it carried one. On iphone11_ios17 "
                 "the 4 Image Message rows each had a cached file; 2 of them fall on 5 January 2024 and "
                 "match the image received at 12:02 and sent at 12:07 local time in the image's "
                 "documentation, and the other 2 are from a later date. Wire Secure Messenger Media lists "
                 "every cached file, matched or not. "
                 "Unrecognized category values (including bitmask combinations) are "
                 "reported as stored. Reference: Wire open source, wire-ios-data-model "
                 "MessageCategory (OptionSet raw values), "
                 "https://github.com/wireapp/wire-ios/blob/1d90c3e2c54b223a61fb766802cce112ed5afa0f/wire-ios-data-model/Source/Model/Message/ZMMessage%2BCategorization.swift#L255-L273. "
                 "Direction is Outgoing when ZMESSAGE.ZSENDER is the user that ZSESSION.ZSELFUSER names, "
                 "Incoming when it is another user, and blank when the message has no sender or the "
                 "database does not hold exactly one ZSESSION row. Wire's isSelfUser makes the same "
                 "comparison against the self user it reads from the session "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/User/ZMUser.m#L177-L184, "
                 "https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/User/ZMUser.m#L678-L719), "
                 "and appending a message sets its sender to the self user "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/Conversation/ZMConversation%2BMessage.swift#L479). "
                 "Outgoing therefore names the account, not the device: a message the account sent from "
                 "another of its clients would also be Outgoing; Sender Client ID was not compared here. "
                 "Conversation is taken from ZVISIBLEINCONVERSATION and, where that is empty, from "
                 "ZHIDDENINCONVERSATION; Placement says which. Wire moves a message it removes from the "
                 "visible to the hidden relationship "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/Message/ZMMessage.m#L348-L351), "
                 "sets only the hidden one for messages appended as hidden "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/Conversation/ZMConversation%2BMessage.swift#L482-L483) "
                 "and for system messages added as children of another "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/Conversation/Calling/ZMConversation%2BCalling.swift#L65-L68), "
                 "so Hidden does not by itself say which of these happened. Every "
                 "AccountData/<account>/store/store.wiredatabase found is read, and Account is that "
                 "folder's name, uppercased. Conversation Key is Account and Conversation ID joined with "
                 "a slash; the conversation view groups by it, so a conversation two accounts on the "
                 "device both belong to shows as one thread per account. On iphone11_ios17 Account held "
                 "one value on all 50 rows, the image's only account; a tree holding that account twice, "
                 "under two account folders, gave exactly twice the rows, each account's media from its "
                 "own cache and one thread per account and conversation. No device with two Wire "
                 "accounts was available. Conversation ID is "
                 "ZCONVERSATION.ZREMOTEIDENTIFIER_DATA shown as a UUID like User ID. Conversation is a "
                 "label derived here, not a stored title. It is modelled on Wire's displayName "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/Conversation/ZMConversation%2BDisplayName.swift#L22-L73), "
                 "which for a one-on-one conversation ignores ZUSERDEFINEDNAME: Self gives the self "
                 "user's display name; One-on-one the display name of the first other user in "
                 "ZPARTICIPANTROLE by Z_PK, else of the connected user; Group ZUSERDEFINEDNAME, else "
                 "the other participants' display names sorted and joined with commas; Connection "
                 "request the connected user's display name, else ZUSERDEFINEDNAME; any other type "
                 "ZUSERDEFINEDNAME. Where that gives no name the Conversation ID is shown. The connected "
                 "user is ZCONVERSATION.ZONEONONEUSER, which connectedUser returns "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/Conversation/ZMConversation.m#L272-L284, "
                 "https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/WireData/Sources/WireData/Schema/zmessaging.xcdatamodeld/zmessaging2.144.0.xcdatamodel/contents#L121), "
                 "or, in schemas without that column, the ZTO user of the first ZCONNECTION row by Z_PK "
                 "whose ZCONVERSATION is the conversation (the to and conversation relationships of "
                 "Connection, "
                 "https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/WireData/Sources/WireData/Schema/zmessaging.xcdatamodeld/zmessaging2.110.0.xcdatamodel/contents#L47-L48); "
                 "the code that read that older link was not read. Without exactly one ZSESSION row no "
                 "participant can be excluded as self, so One-on-one and Group fall back to the "
                 "connected user and ZUSERDEFINEDNAME. On iphone11_ios17 one of the two one-on-one "
                 "conversations with messages holds the self user's own display name in "
                 "ZUSERDEFINEDNAME, which is why that column is not used for them. Conversation Type is "
                 "the stored type; Wire shows an unnamed team group with one other participant as "
                 "one-on-one "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/Conversation/ZMConversation.m#L453-L477), "
                 "and such a conversation is reported here as Group, labelled with that participant. "
                 "On iphone11_ios17 Conversation Type held One-on-one on all 50 rows and Placement held "
                 "Visible on all 50 rows: both conversations with messages are one-on-one, and no "
                 "message there has ZHIDDENINCONVERSATION set. On hc_ios18_7 Conversation Type held "
                 "Group, One-on-one and Self and on iphone12_ios18 One-on-one and Self, and every row "
                 "was labelled with a name. On iphone12_ios18 2 ZMESSAGE rows have ZHIDDENINCONVERSATION "
                 "set; both are category 1 with no sender and no text, so the category filter drops "
                 "them, and Placement is Visible on every reported row. A removed message of that shape "
                 "is therefore not reported. "
                 "Conversation Type maps ZCONVERSATIONTYPE with Wire's ZMConversationType "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Public/ZMConversation.h#L41-L47); "
                 "other values are reported as stored. Where a schema lacks ZUSER.ZREMOTEIDENTIFIER_DATA, "
                 "ZMESSAGE.ZVISIBLEINCONVERSATION, ZHIDDENINCONVERSATION, ZSYSTEMMESSAGETYPE, ZDURATION "
                 "or ZNONCE_DATA, the values drawn from it are left blank; ZMESSAGE.ZSERVERTIMESTAMP, "
                 "ZSENDER, ZNORMALIZEDTEXT and ZCACHEDCATEGORY and ZUSER.ZNAME and ZHANDLE are selected "
                 "unconditionally. "
                 "The Wire code cited for these columns is at commit 851bba15 and was not compared with "
                 "the builds on the corpora below.",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/AccountData/*/store/store.wiredatabase*',
                  '*/mobile/Containers/Shared/AppGroup/*/Library/Caches/wire-account-*/'
                  '????????????????????????????????????????????????????????????????'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation Key",
                "conversationLabelColumn": "Conversation",
                "textColumn": "Message",
                "senderColumn": "Display Name",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Date / Time",
                "mediaColumn": "Media",
            }
        },
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | Wire • Secure Messenger 4.16.3 | 19 rows",
            "iphone11_ios17": "iOS 17.3 | Wire • Secure Messenger 3.111.9 | 50 rows",
            "iphone12_ios18": "iOS 18.7 | Wire • Secure Messenger 4.10.0 | 38 rows",
            "hickman_ios13": "iOS 13.3.1 | Wire • Secure Messenger 3.54 | 12 rows",
            "hickman_ios14": "iOS 14.3 | Wire • Secure Messenger 3.73 | 18 rows",
            "jess_ios15": "iOS 15.0.2 | Wire • Secure Messenger 3.94 | 0 rows",
        }
    },
    "wireContacts": {
        "name": "Wire Secure Messenger Contacts",
        "description": "Wire users stored in the account's database, one row per ZUSER row, with display name, "
                       "handle, email address, phone number, user ID, whether the row is the account's own "
                       "user, the stored connection status, and the profile pictures found in the app's "
                       "user image caches.",
        "author": "@kalink0",
        "creation_date": "2026-11-08",
        "last_update_date": "2026-11-11",
        "requirements": "",
        "category": "Wire Messenger",
        "notes": "Every ZUSER row of every AccountData/<account>/store/store.wiredatabase found is "
                 "reported, the same rows as Wire Secure Messenger Users and Clients without the "
                 "per-client fan-out, with Account naming the account folder and pictures taken only from "
                 "that account's caches. On iphone11_ios17 Account held one value on all 4 rows, the "
                 "image's only account; a tree holding that account twice, under two account folders, "
                 "gave exactly twice the rows, each account's pictures from its own cache. No device with "
                 "two Wire accounts was available. A ZUSER row does not need a ZCONNECTION row (the self "
                 "user has none on iphone11_ios17, hc_ios18_7, iphone12_ios18 and jess_ios15), so a row is "
                 "not by itself a contact the account added. Self is Yes for "
                 "the user that ZSESSION.ZSELFUSER names and blank for the others, and blank on every row "
                 "when the database does not hold exactly one ZSESSION row. Connection Status maps "
                 "ZCONNECTION.ZSTATUS of the ZCONNECTION row whose ZTO is the user with Wire's "
                 "ZMConnectionStatus "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/Connection/ZMConnection.h#L24-L33); "
                 "other values are reported as stored, and it is blank where no ZCONNECTION row names the "
                 "user, which says nothing about whether the two users ever connected. Where several "
                 "ZCONNECTION rows name one user, the first by Z_PK is used. Profile Picture and Profile "
                 "Picture Preview are the images Wire's UserImageLocalCache keeps in the "
                 "com.pinterest.PINDiskCache.largeUserImages and smallUserImages caches under "
                 "Library/Caches/wire-account-<account>, keyed by the user ID as a lowercase UUID, a hyphen "
                 "and the user's ZCOMPLETEPROFILEASSETIDENTIFIER or ZPREVIEWPROFILEASSETIDENTIFIER "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Utilis/UserImageLocalCache.swift#L28-L40, "
                 "https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Utilis/UserImageLocalCache.swift#L77-L78). "
                 "Each cache file is a keyed archive whose image bytes are read from its object list. "
                 "UserImageLocalCache stores an image there in setUserImage "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Utilis/UserImageLocalCache.swift#L125-L141), "
                 "and the callers of setUserImage were not read; a blank picture does not mean the user "
                 "has none. Phone Number is blank where the "
                 "schema has no ZPHONENUMBER column; on iphone11_ios17 Phone Number was blank on all 4 "
                 "rows because ZPHONENUMBER held no value. On iphone11_ios17 all 4 users had "
                 "both pictures cached, and every cache file matched a user and asset identifier in ZUSER. "
                 "A cached picture was found for 1 of 2 users on hc_ios18_7, 0 of 2 on iphone12_ios18 "
                 "and 1 of 1 on jess_ios15. The Wire code cited is at commit 851bba15 and was not compared with the builds "
                 "on the corpora below.",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/AccountData/*/store/store.wiredatabase*',
                  '*/mobile/Containers/Shared/AppGroup/*/Library/Caches/wire-account-*/'
                  'com.pinterest.PINDiskCache.*UserImages/*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "address-book",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | Wire • Secure Messenger 3.111.9 | 4 rows",
        }
    },
    "wireMedia": {
        "name": "Wire Secure Messenger Media",
        "description": "Files in Wire's per-account asset cache, one row per file, with the message each one "
                       "belongs to where Wire's cache key identifies it, and the file itself.",
        "author": "@kalink0",
        "creation_date": "2026-11-08",
        "last_update_date": "2026-11-11",
        "requirements": "",
        "category": "Wire Messenger",
        "notes": "Every file directly under AppGroup/<group>/Library/Caches/wire-account-<account> whose name "
                 "is 64 hex digits is listed. A file is matched to a message of that account's "
                 "store.wiredatabase when its name is Wire's cache key for the message, the hex SHA-256 of "
                 "the message nonce, the sender's user ID and the conversation ID as lowercase UUIDs, and "
                 "the format, with \"_encrypted\" appended for the encrypted copy "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/Message/FileAssetCache.swift#L815-L847); "
                 "Format names the format whose key matched (original, medium, preview, or none for a key "
                 "without one), followed by \" (encrypted)\" for an encrypted copy, so it can also be, "
                 "for example, medium (encrypted) or none (encrypted). Message Date / Time, Direction, Sender, Conversation and Message Type are "
                 "those of Wire Secure Messenger Messages for the matched message, and are blank for a file "
                 "no key matched; such a file is still listed, with Format blank. The key is computed, "
                 "not read, so a file Wire cached under another key, such as one built by code that was "
                 "not read, is listed as unmatched. On iphone11_ios17 6 of the 8 files matched: the medium "
                 "copy of each of the 2 received images and the original and medium copies of each of the "
                 "2 sent images; the 2 unmatched files began with a multipart boundary line, so Message "
                 "Date / Time, Direction, Sender, Conversation, Format and Message Type were blank on "
                 "them. Account is the account named by the cache folder; on iphone11_ios17 Account "
                 "held one value on all 8 rows, the image's only account; a tree holding that account "
                 "twice, under two account folders, gave exactly twice the rows, with 6 of 8 matched in "
                 "each account. No device with two Wire accounts was available. A file is matched only against "
                 "the store.wiredatabase of its own account, so a cache folder without that account's "
                 "database is listed unmatched. Encrypted copies are listed as stored and are not "
                 "decrypted. All 5 cache files on hc_ios18_7 (Wire 4.16.3) and all 11 on iphone12_ios18 "
                 "(Wire 4.10.0) matched an encrypted format, and none did on iphone11_ios17 (Wire "
                 "3.111.9); such files are listed but not rendered. Wire's commit \"fix: assets are not encrypted at "
                 "rest\" of 22 March 2024 "
                 "(https://github.com/wireapp/wire-ios/commit/255a6951d568ff308ede1690ee8fff6417978aff) "
                 "changed FileAssetCache to keep assets encrypted; of the App Store release tags checked, "
                 "appstore/3.111.9 does not contain it and appstore/3.112.3 and every later tag up to "
                 "appstore/3.122.2 do. No tag exists for 3.112.0 to 3.112.2, and a tag's date is not the "
                 "date the release reached a device, so the version a device was running when its files "
                 "changed form is not established here. The Wire code cited is at commit 851bba15 and was not compared with "
                 "the builds on the corpora below.",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/AccountData/*/store/store.wiredatabase*',
                  '*/mobile/Containers/Shared/AppGroup/*/Library/Caches/wire-account-*/'
                  '????????????????????????????????????????????????????????????????'),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | Wire • Secure Messenger 3.111.9 | 8 rows",
        }
    }
}

import base64
import binascii
import hashlib
import json
import os
import plistlib
import urllib.parse
import uuid
from pathlib import Path

from scripts.ilapfuncs import (
    artifact_processor,
    check_in_embedded_media,
    check_in_media,
    logfunc,
    get_sqlite_db_records,
    does_column_exist_in_db,
    does_table_exist_in_db,
    convert_cocoa_core_data_ts_to_utc
    )

# ZMConversationType, wire-ios-data-model/Source/Public/ZMConversation.h (commit 851bba15)
_CONVERSATION_TYPES = {
    0: 'Invalid',
    1: 'Self',
    2: 'One-on-one',
    3: 'Group',
    4: 'Connection request',
}

# MessageCategory raw values, wire-ios-data-model ZMMessage+Categorization.swift (commit 1d90c3e2)
_MESSAGE_CATEGORIES = {
    0: 'None (uncategorized)',
    2: 'Text Message',
    8: 'Image Message',
    256: 'Location Message',
    2048: 'System Message',
}

# ZMSystemMessageType, wire-ios-data-model/Source/Public/ZMMessage.h (commit 851bba15)
_MISSED_CALL = 7
_PERFORMED_CALL = 18
_CALL_SYSTEM_TYPES = {_MISSED_CALL: 'Missed Call', _PERFORMED_CALL: 'Call'}

# ZMConnectionStatus, wire-ios-data-model/Source/Model/Connection/ZMConnection.h (commit 851bba15)
_CONNECTION_STATUSES = {
    0: 'Invalid',
    1: 'Accepted',
    2: 'Pending',
    3: 'Ignored',
    4: 'Blocked',
    5: 'Sent',
    6: 'Cancelled',
    7: 'Blocked (missing legal hold consent)',
}

# ZMImageFormat stringValue, plus no identifier, as FileAssetCache.cacheKeyForAsset builds keys
_ASSET_FORMATS = (None, 'original', 'medium', 'preview')


def _uuid_text(value):
    """Wire's remoteIdentifier_data: 16 uuid_t bytes as a lowercase UUID; other values as stored."""
    if isinstance(value, bytes) and len(value) == 16:
        return str(uuid.UUID(bytes=value))
    if isinstance(value, bytes):
        return value.hex()
    return value


def _optional_column(source_path, table, column):
    """The qualified column when the table has it, else NULL, for columns some Wire schemas lack."""
    if does_column_exist_in_db(source_path, table, column):
        return f'{table}.{column}'
    return 'NULL'


def _self_user_pk(source_path):
    """ZSESSION.ZSELFUSER when the database holds exactly one session row, else None."""
    if not does_table_exist_in_db(source_path, 'ZSESSION'):
        return None
    rows = list(get_sqlite_db_records(source_path, 'SELECT ZSELFUSER FROM ZSESSION'))
    if len(rows) != 1:
        return None
    return rows[0][0]


def _conversations(source_path, self_user_pk):
    """ZCONVERSATION.Z_PK -> (label, Conversation ID, stored type).

    The label is modelled on Wire's ZMConversation.displayName: self user's name for a self
    conversation, the other participant (else the connected user) for one-on-one, the
    user-defined name (else the other participants' names) for a group, and the connected
    user (else the user-defined name) for a connection request. The Conversation ID stands
    in where that gives no name.
    """
    if not does_table_exist_in_db(source_path, 'ZCONVERSATION'):
        return {}
    names = {pk: name for pk, name in get_sqlite_db_records(source_path, 'SELECT Z_PK, ZNAME FROM ZUSER')}

    participants = {}
    if (does_column_exist_in_db(source_path, 'ZPARTICIPANTROLE', 'ZCONVERSATION')
            and does_column_exist_in_db(source_path, 'ZPARTICIPANTROLE', 'ZUSER')):
        for conversation, user in get_sqlite_db_records(
                source_path, 'SELECT ZCONVERSATION, ZUSER FROM ZPARTICIPANTROLE ORDER BY Z_PK'):
            participants.setdefault(conversation, []).append(user)

    # Newer schemas name the connected user in ZCONVERSATION.ZONEONONEUSER; older ones only
    # through ZCONNECTION.ZCONVERSATION and ZTO.
    connected = {}
    if does_column_exist_in_db(source_path, 'ZCONVERSATION', 'ZONEONONEUSER'):
        connected = dict(get_sqlite_db_records(
            source_path, 'SELECT Z_PK, ZONEONONEUSER FROM ZCONVERSATION WHERE ZONEONONEUSER IS NOT NULL'))
    elif does_column_exist_in_db(source_path, 'ZCONNECTION', 'ZCONVERSATION'):
        for conversation, user in get_sqlite_db_records(
                source_path, 'SELECT ZCONVERSATION, ZTO FROM ZCONNECTION '
                             'WHERE ZCONVERSATION IS NOT NULL AND ZTO IS NOT NULL ORDER BY Z_PK'):
            connected.setdefault(conversation, user)

    columns = ', '.join(_optional_column(source_path, 'ZCONVERSATION', column) for column in
                        ('ZCONVERSATIONTYPE', 'ZUSERDEFINEDNAME', 'ZREMOTEIDENTIFIER_DATA'))
    result = {}
    for pk, conversation_type, user_defined, remote_id in get_sqlite_db_records(
            source_path, f'SELECT ZCONVERSATION.Z_PK, {columns} FROM ZCONVERSATION'):
        others = ([names.get(user) for user in participants.get(pk, []) if user != self_user_pk]
                  if self_user_pk is not None else [])
        others = [name for name in others if name]
        connected_name = names.get(connected.get(pk))
        if conversation_type == 1:
            label = names.get(self_user_pk)
        elif conversation_type == 2:
            label = (others[0] if others else None) or connected_name
        elif conversation_type == 3:
            label = user_defined or (', '.join(sorted(others)) if others else None)
        elif conversation_type == 4:
            label = connected_name or user_defined
        else:
            label = user_defined
        conversation_id = _uuid_text(remote_id)
        result[pk] = (label or conversation_id, conversation_id, conversation_type)
    return result


def _account_files(files_found):
    """Account JSON files and the app group plist, each keyed by the app group folder."""
    accounts, plists = [], {}
    for file_found in files_found:
        path = Path(file_found)
        if path.name == 'group.com.wearezeta.zclient.ios.plist':
            plists[path.parents[2]] = path
        elif path.parent.name == 'Accounts':
            try:
                uuid.UUID(path.name)
            except ValueError:
                continue
            accounts.append(path)
    return accounts, plists


def _selected_account(plist_path):
    """AccountManagerSelectedAccountKey uppercased, '' when the key is absent, None when unreadable."""
    try:
        with open(plist_path, 'rb') as plist_file:
            value = plistlib.load(plist_file).get('AccountManagerSelectedAccountKey')
    except (OSError, plistlib.InvalidFileException, ValueError, AttributeError):
        return None
    return str(value).upper() if value else ''


def _embedded_image(source_path, value, name):
    """A base64 image value checked in as embedded media, else ''."""
    if not isinstance(value, str) or not value:
        return ''
    try:
        data = base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError):
        return ''
    return check_in_embedded_media(source_path, data, name) or ''


@artifact_processor
def wireAccountFiles(context):
    accounts, plists = _account_files(context().get_files_found())
    data_list = []
    source_paths = []
    for path in sorted(accounts):
        try:
            with open(path, 'rb') as account_file:
                account = json.load(account_file)
        except (OSError, ValueError) as ex:
            logfunc(f'Wire account file {path} not read: {ex}')
            continue
        if not isinstance(account, dict) or 'identifier' not in account or 'name' not in account:
            continue
        source_paths.append(str(path))

        identifier = str(account.get('identifier') or '')
        account_id = identifier or path.name
        if identifier and identifier.upper() != path.name.upper():
            account_id = f'{identifier} (file name {path.name})'

        plist_path = plists.get(path.parents[1])
        selected_id = _selected_account(plist_path) if plist_path else None
        if selected_id is None:
            selected = ''
        else:
            selected = 'Yes' if selected_id in (identifier.upper(), path.name.upper()) else 'No'
            source_paths.append(str(plist_path))

        credentials = account.get('loginCredentials')
        if not isinstance(credentials, dict):
            credentials = {}
        data_list.append((
            account_id,
            selected,
            account.get('name'),
            account.get('handle'),
            credentials.get('emailAddress'),
            account.get('team'),
            account.get('backendName'),
            credentials.get('usesCompanyLogin'),
            credentials.get('hasPassword'),
            account.get('lastSSOIdentityProviderID'),
            account.get('unreadConversationCount'),
            _embedded_image(str(path), account.get('image'), 'profile picture'),
            _embedded_image(str(path), account.get('teamImage'), 'team picture'),
            ))

    data_headers = (
        'Account ID',
        'Selected',
        'Display Name',
        'Handle',
        'Email Address',
        'Team',
        'Backend',
        'Uses Company Login',
        'Has Password',
        'Last SSO Identity Provider ID',
        'Unread Count (as stored)',
        ('Profile Picture', 'media'),
        ('Team Picture', 'media'),
        )
    return data_headers, data_list, '\n'.join(dict.fromkeys(source_paths))


def _stores(files_found):
    """Every main store.wiredatabase, one per AccountData/<account> folder, in path order."""
    return sorted(dict.fromkeys(str(f) for f in files_found if Path(f).name == 'store.wiredatabase'))


@artifact_processor
def wireAccount(context):
    files_found = context().get_files_found()
    stores = _stores(files_found)
    data_list = []

    has_location_data = any(
        does_column_exist_in_db(source_path, 'ZUSERCLIENT', 'ZACTIVATIONLOCATIONLATITUDE')
        for source_path in stores)

    data_headers = [
        ('Activation Date', 'datetime'),
        ('Discovery Date', 'datetime'),
        ('Last Active Date', 'datetime'),
        'Handle',
        'User ID',
        'Display Name',
        ('Phone Number', 'phonenumber'),
        'Email Address',
        'Client ID',
        'Device Class',
        'Device Label',
        'Device Model',
        ]
    if has_location_data:
        data_headers.extend(['Latitude', 'Longitude'])
    data_headers.append('Account')

    for source_path in stores:
        # Newer Wire versions drop ZUSER.ZPHONENUMBER, so it is selected only when present.
        # The client columns are selected the same way, so a schema without one still
        # reports the rest, and a database without the location columns leaves them blank.
        columns = [
            'ZUSERCLIENT.ZACTIVATIONDATE',
            _optional_column(source_path, 'ZUSERCLIENT', 'ZDISCOVERYDATE'),
            _optional_column(source_path, 'ZUSERCLIENT', 'ZLASTACTIVEDATE'),
            'ZUSER.ZHANDLE',
            _optional_column(source_path, 'ZUSER', 'ZREMOTEIDENTIFIER_DATA'),
            'ZUSER.ZNAME',
            _optional_column(source_path, 'ZUSER', 'ZPHONENUMBER'),
            'ZUSER.ZEMAILADDRESS',
            _optional_column(source_path, 'ZUSERCLIENT', 'ZREMOTEIDENTIFIER'),
            _optional_column(source_path, 'ZUSERCLIENT', 'ZDEVICECLASS'),
            _optional_column(source_path, 'ZUSERCLIENT', 'ZLABEL'),
            _optional_column(source_path, 'ZUSERCLIENT', 'ZMODEL'),
            ]
        if has_location_data:
            columns.extend([
                _optional_column(source_path, 'ZUSERCLIENT', 'ZACTIVATIONLOCATIONLATITUDE'),
                _optional_column(source_path, 'ZUSERCLIENT', 'ZACTIVATIONLOCATIONLONGITUDE'),
                ])

        query = f'''
        SELECT
            {', '.join(columns)}
        FROM ZUSER
        LEFT JOIN ZUSERCLIENT ON ZUSER.Z_PK = ZUSERCLIENT.ZUSER;
        '''

        account = _store_account(source_path)
        for record in get_sqlite_db_records(source_path, query):
            data_list.append((
                convert_cocoa_core_data_ts_to_utc(record[0]),
                convert_cocoa_core_data_ts_to_utc(record[1]),
                convert_cocoa_core_data_ts_to_utc(record[2]),
                record[3],
                _uuid_text(record[4]),
                *tuple(record)[5:],
                account,
                ))
    return tuple(data_headers), data_list, '\n'.join(stores)


def _message_type(category, system_type):
    """Call and Missed Call from ZSYSTEMMESSAGETYPE, else the ZCACHEDCATEGORY name or the stored value."""
    if system_type in _CALL_SYSTEM_TYPES:
        return _CALL_SYSTEM_TYPES[system_type]
    return _MESSAGE_CATEGORIES.get(category, category)


def _messages(source_path):
    """The reported ZMESSAGE rows of one database as dicts, in query order."""
    self_user_pk = _self_user_pk(source_path)
    conversations = _conversations(source_path, self_user_pk)

    user_id_column = _optional_column(source_path, 'ZUSER', 'ZREMOTEIDENTIFIER_DATA')
    visible_column = _optional_column(source_path, 'ZMESSAGE', 'ZVISIBLEINCONVERSATION')
    hidden_column = _optional_column(source_path, 'ZMESSAGE', 'ZHIDDENINCONVERSATION')
    query = f'''
    SELECT
        ZMESSAGE.ZSERVERTIMESTAMP,
        ZMESSAGE.ZSENDER,
        ZUSER.ZNAME,
        COALESCE({visible_column}, {hidden_column}),
        ZMESSAGE.ZNORMALIZEDTEXT,
        ZUSER.ZHANDLE,
        {user_id_column},
        CASE
            WHEN {visible_column} IS NOT NULL THEN 'Visible'
            WHEN {hidden_column} IS NOT NULL THEN 'Hidden'
        END,
        ZMESSAGE.ZCACHEDCATEGORY,
        {_optional_column(source_path, 'ZMESSAGE', 'ZSYSTEMMESSAGETYPE')},
        {_optional_column(source_path, 'ZMESSAGE', 'ZDURATION')},
        {_optional_column(source_path, 'ZMESSAGE', 'ZNONCE_DATA')}
    FROM ZMESSAGE
    LEFT JOIN ZUSER ON ZUSER.Z_PK = ZMESSAGE.ZSENDER
    WHERE ZMESSAGE.ZCACHEDCATEGORY != 1 OR ZMESSAGE.ZCACHEDCATEGORY IS NULL;
    '''
    messages = []
    for record in get_sqlite_db_records(source_path, query):
        sender_pk = record[1]
        if sender_pk is None or self_user_pk is None:
            direction = ''
        elif sender_pk == self_user_pk:
            direction = 'Outgoing'
        else:
            direction = 'Incoming'
        label, conversation_id, conversation_type = conversations.get(record[3], (None, None, None))
        system_type = record[9]
        call_duration = record[10] if system_type == _PERFORMED_CALL else None
        messages.append({
            'timestamp': record[0],
            'direction': direction,
            'sender': record[2],
            'conversation': label,
            'text': record[4],
            'handle': record[5],
            'user_id': _uuid_text(record[6]),
            'conversation_id': conversation_id,
            'conversation_type': _CONVERSATION_TYPES.get(conversation_type, conversation_type),
            'placement': record[7],
            'message_type': _message_type(record[8], system_type),
            'call_duration': call_duration,
            'nonce': _uuid_text(record[11]),
            })
    return messages


def _call_connected(message):
    """Server timestamp minus a positive call duration, as UTC; None otherwise."""
    timestamp, duration = message['timestamp'], message['call_duration']
    if not isinstance(timestamp, (int, float)) or not isinstance(duration, (int, float)) or duration <= 0:
        return None
    return convert_cocoa_core_data_ts_to_utc(timestamp - duration)


def _store_account(source_path):
    """The AccountData/<account> folder name of a store.wiredatabase path, uppercased."""
    return Path(source_path).parents[1].name.upper() if source_path else ''


def _cache_account(path):
    """The account of a file under Library/Caches/wire-account-<account>, uppercased, else None."""
    for parent in Path(path).parents:
        if parent.name.lower().startswith('wire-account-'):
            return parent.name[len('wire-account-'):].upper()
    return None


def _asset_cache_files(files_found):
    """Asset cache files: 64 hex digit names directly under a wire-account-<account> folder."""
    files = []
    for file_found in files_found:
        path = Path(file_found)
        if (path.parent.name.lower().startswith('wire-account-')
                and len(path.name) == 64 and all(ch in '0123456789abcdef' for ch in path.name.lower())):
            files.append(path)
    return sorted(files)


def _asset_keys(message):
    """(format, cache key) pairs FileAssetCache.cacheKeyForAsset gives for a message."""
    if not (message['nonce'] and message['user_id'] and message['conversation_id']):
        return []
    keys = []
    for identifier in _ASSET_FORMATS:
        for encrypted in (False, True):
            parts = [message['nonce'], message['user_id'], message['conversation_id'], identifier,
                     'encrypted' if encrypted else None]
            key = hashlib.sha256('_'.join(p for p in parts if p).encode('utf-8')).hexdigest()
            label = (identifier or 'none') + (' (encrypted)' if encrypted else '')
            keys.append((label, key))
    return keys


@artifact_processor
def wireMessages(context):
    files_found = context().get_files_found()
    stores = _stores(files_found)
    cache_files = _asset_cache_files(files_found)
    data_list = []
    media_sources = []

    data_headers = (
        ('Date / Time', 'datetime'),
        ('Call Connected', 'datetime'),
        'Direction',
        'Display Name',
        'Conversation',
        'Message',
        ('Media', 'media'),
        'Handle',
        'User ID',
        'Conversation ID',
        'Conversation Type',
        'Placement',
        'Message Type',
        ('Call Duration (seconds)', 'number'),
        'Account',
        'Conversation Key')

    for source_path in stores:
        account = _store_account(source_path)
        cache = {path.name.lower(): path for path in cache_files if _cache_account(path) == account}
        for message in _messages(source_path):
            media = ''
            if cache:
                found = dict((label, cache[key]) for label, key in _asset_keys(message) if key in cache)
                for label in ('original', 'medium', 'preview', 'none'):
                    if label in found:
                        media = check_in_media(str(found[label])) or ''
                        media_sources.append(str(found[label]))
                        break
            data_list.append((
                convert_cocoa_core_data_ts_to_utc(message['timestamp']),
                _call_connected(message),
                message['direction'],
                message['sender'],
                message['conversation'],
                message['text'],
                media,
                message['handle'],
                message['user_id'],
                message['conversation_id'],
                message['conversation_type'],
                message['placement'],
                message['message_type'],
                message['call_duration'],
                account,
                f"{account}/{message['conversation_id']}" if message['conversation_id'] else None,
                ))

    return data_headers, data_list, '\n'.join(stores + media_sources)


@artifact_processor
def wireMedia(context):
    files_found = context().get_files_found()
    stores = _stores(files_found)
    cache_files = _asset_cache_files(files_found)
    data_list = []

    # (account, cache key) -> (message, format), each account matched only against its own store.
    matches = {}
    matched_stores = []
    cached_accounts = {_cache_account(path) for path in cache_files}
    for source_path in stores:
        account = _store_account(source_path)
        if account not in cached_accounts:
            continue
        matched_stores.append(source_path)
        for message in _messages(source_path):
            for label, key in _asset_keys(message):
                matches.setdefault((account, key), (message, label))

    data_headers = (
        ('Message Date / Time', 'datetime'),
        'Direction',
        'Sender',
        'Conversation',
        ('Media', 'media'),
        'Format',
        'Message Type',
        'Account',
        'Cache File Name',
        ('Size (bytes)', 'number'))

    for path in cache_files:
        matched = matches.get((_cache_account(path), path.name.lower()))
        message, label = matched if matched else ({}, None)
        try:
            size = os.path.getsize(path)
        except OSError:
            size = None
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(message['timestamp']) if message else None,
            message.get('direction'),
            message.get('sender'),
            message.get('conversation'),
            check_in_media(str(path)) or '',
            label,
            message.get('message_type'),
            _cache_account(path),
            path.name,
            size,
            ))

    return data_headers, data_list, '\n'.join(matched_stores + [str(path) for path in cache_files])


def _user_image_files(files_found):
    """{(cache name, lowercase key): path} for files in the PINDiskCache user image caches."""
    images = {}
    for file_found in files_found:
        path = Path(file_found)
        cache_name = path.parent.name
        if cache_name in ('com.pinterest.PINDiskCache.largeUserImages',
                          'com.pinterest.PINDiskCache.smallUserImages'):
            images[(cache_name, urllib.parse.unquote(path.name).lower(), _cache_account(path))] = path
    return images


def _archived_image(path):
    """The first bytes object in a keyed archive's $objects, which is how PINDiskCache keeps NSData."""
    try:
        with open(path, 'rb') as archive_file:
            archive = plistlib.load(archive_file)
    except (OSError, plistlib.InvalidFileException, ValueError):
        return None
    objects = archive.get('$objects') if isinstance(archive, dict) else None
    for item in objects or []:
        if isinstance(item, bytes) and item:
            return item
    return None


def _contacts(source_path, images, image_sources):
    """The wireContacts rows of one database, pictures taken from that account's caches."""
    rows = []
    self_user_pk = _self_user_pk(source_path)
    account = _store_account(source_path)

    connections = {}
    if (does_column_exist_in_db(source_path, 'ZCONNECTION', 'ZTO')
            and does_column_exist_in_db(source_path, 'ZCONNECTION', 'ZSTATUS')):
        for user, status in get_sqlite_db_records(
                source_path, 'SELECT ZTO, ZSTATUS FROM ZCONNECTION WHERE ZTO IS NOT NULL ORDER BY Z_PK'):
            connections.setdefault(user, status)

    query = f'''
    SELECT
        Z_PK,
        ZNAME,
        ZHANDLE,
        ZEMAILADDRESS,
        {_optional_column(source_path, 'ZUSER', 'ZPHONENUMBER')},
        {_optional_column(source_path, 'ZUSER', 'ZREMOTEIDENTIFIER_DATA')},
        {_optional_column(source_path, 'ZUSER', 'ZCOMPLETEPROFILEASSETIDENTIFIER')},
        {_optional_column(source_path, 'ZUSER', 'ZPREVIEWPROFILEASSETIDENTIFIER')}
    FROM ZUSER
    ORDER BY Z_PK;
    '''
    for record in get_sqlite_db_records(source_path, query):
        user_id = _uuid_text(record[5])
        pictures = []
        for cache_name, asset_id in (('com.pinterest.PINDiskCache.largeUserImages', record[6]),
                                     ('com.pinterest.PINDiskCache.smallUserImages', record[7])):
            path = images.get((cache_name, f'{user_id}-{asset_id}'.lower(), account)) \
                if isinstance(user_id, str) and asset_id else None
            data = _archived_image(path) if path else None
            if data:
                image_sources.append(str(path))
                pictures.append(check_in_embedded_media(str(path), data, 'profile picture') or '')
            else:
                pictures.append('')
        status = connections.get(record[0])
        if self_user_pk is None:
            is_self = ''
        else:
            is_self = 'Yes' if record[0] == self_user_pk else ''
        rows.append((
            record[1],
            record[2],
            record[3],
            record[4],
            user_id,
            is_self,
            _CONNECTION_STATUSES.get(status, status),
            pictures[0],
            pictures[1],
            account,
            ))
    return rows


@artifact_processor
def wireContacts(context):
    files_found = context().get_files_found()
    stores = _stores(files_found)
    images = _user_image_files(files_found)
    image_sources = []
    data_list = []
    for source_path in stores:
        data_list.extend(_contacts(source_path, images, image_sources))

    data_headers = (
        'Display Name',
        'Handle',
        'Email Address',
        ('Phone Number', 'phonenumber'),
        'User ID',
        'Self',
        'Connection Status',
        ('Profile Picture', 'media'),
        ('Profile Picture Preview', 'media'),
        'Account',
        )
    return data_headers, data_list, '\n'.join(stores + image_sources)
