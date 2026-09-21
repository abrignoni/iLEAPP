# pylint: disable=W0718
__artifacts_v2__ = {
    "snapchatMessages": {
        "name": "Snapchat - Messages (arroyo.db)",
        "description": "Chat message records from the conversation_message table in arroyo.db, both the rows a "
                       "normal read returns and rows that are present only before the write-ahead log is "
                       "applied, distinguished by the Record Origin column. Sender UUIDs are resolved against "
                       "the snapchatter store in primary.docobjects, and message text is decoded from the "
                       "message_content protobuf on rows where content_type is 1. WAL frames are not parsed, "
                       "so absence of a message here is not evidence it did not exist. Cached media that "
                       "cache_controller.db links to a message is shown in the Media column when its format is "
                       "recognised.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16", "last_update_date": "2026-09-19",
        "requirements": "blackboxprotobuf, nska_deserialize", "category": "Snapchat",
        "notes": "iOS Snapchat keeps conversations in Documents/user_scoped/<account "
                 "hash>/arroyo/arroyo.db; the schema ships the developers' own column comments and they "
                 "are quoted where relied on.\n"
                 "Record Origin. Live rows come back from a normal read. Recovered rows do not: they sit "
                 "in the database file as of its last checkpoint and are gone once the write-ahead log "
                 "is applied. Recovery Method and Recovery Location are filled in only on Recovered "
                 "rows. The two sets cannot overlap. Why a Recovered row is absent is not established "
                 "here: removal by the app, a server re-sync, and deletion all produce the same result.\n"
                 "Method. The file is read twice through SQLite, immutable=1 to ignore the log and "
                 "mode=ro to apply it, then compared on the (client_conversation_id, client_message_id) "
                 "key rather than row count. The glob keeps the -wal and -shm sidecars: on "
                 "iphone11_ios17 this table reads 11 rows without its log and 17 with it applied.\n"
                 "Message text comes from the message_content protobuf at 4 > 4 > 2 > 1, derived from "
                 "observed structure rather than a published schema, and cross-checked against the same "
                 "row's SQL columns on iphone11_ios17: field 2 > 1 holds the 16 bytes of the sender_id "
                 "UUID on all 17 rows. On iphone11_ios17 only content_type 1 carried text (9 of 17 "
                 "rows); other values carried media metadata but no plaintext body. content_type is "
                 "reported as stored because no source for the enum was verified.\n"
                 "Media. A message's cached media is linked through records the app keeps, never by time "
                 "or size: a cache_controller.db entry whose EXTERNAL_KEY names the conversation and the "
                 "message's server_message_id, or a message whose own local_message_references MEDIA_ID "
                 "equals an entry's EXTERNAL_KEY. The file is shown when its bytes, read as stored, are "
                 "a recognised image, video or audio format; on the tested images 38 of the 39 non-empty "
                 "cached files were, with no decryption needed. Snapchat - Chat Media lists every entry, "
                 "including those with no file on disk.\n"
                 "Message Direction compares sender_id against the local account id from user_id in the "
                 "app's Documents/user.plist, else the single distinct sender of rows where "
                 "local_message_content_id is set (the schema comments describe that column as nullable "
                 "if the message was not created on this device). On iphone11_ios17 the user.plist value "
                 "resolved, matched the snapchatter row carrying the account's username, and appeared in "
                 "every resolved conversation's participant list; the fallback is unexercised because "
                 "local_message_content_id was NULL on every row of the 12 tested images holding "
                 "messages. Blank when neither resolves.\n"
                 "Older arroyo.db generations carry a strict subset of the current columns (iOS 12 and "
                 "13 era files lack sender_id and content_type, an iOS 14 era file lacks only "
                 "quoted_server_message_id, all as observed in tested images); absent columns are "
                 "substituted with NULL under the same name so the remaining columns still report, and "
                 "the affected fields are blank on those rows.\n"
                 "Limits. WAL frames are not parsed, so a message absent here is not evidence it did not "
                 "exist. Reactions and message_state history are not parsed. The run log reports the "
                 "image's WAL frame count.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/user_scoped/*/arroyo/arroyo.db*',
                  '*/mobile/Containers/Data/Application/*/Documents/user_scoped/*/DocObjects/primary.docobjects*',
                  '*/mobile/Containers/Data/Application/*/Documents/user.plist',
                  '*/mobile/Containers/Data/Application/*/Documents/global_scoped/cachecontroller/cache_controller.db*',
                  '*/mobile/Containers/Data/Application/*/Documents/com.snap.file_manager_*_SCContent_*/*'),
        "output_types": "standard", "artifact_icon": "message",
        "sample_data": {
                           "iphone11_ios17": "iOS 17.3 | 17 rows (all Live; 2 with media)",
                           "otto_ios17": "iOS 17.5.1 | 71 rows (59 Live, 12 Recovered; 4 with media)",
                           "dexter_ios18": "iOS 18.3.2 | 33 rows (31 Live, 2 Recovered; 5 with media)",
                           "iphone12_ios18": "iOS 18.7 | 22 rows (15 Live, 7 Recovered; 1 with media)",
                           "hc_ios18_7": "iOS 18.7.8 | 26 rows (all Live; 2 with media)",
                           "iphone14plus_ios18_mvs2025": "iOS 18.0 | 7 rows (all Live; 2 with media)",
                           "abe_ios16": "iOS 16.5 | 198 rows (all Live; 7 with media)",
                           "hexordia_ios1651": "iOS 16.5.1 | 65 rows (all Live; 2 with media)",
                           "magnet_ios16": "iOS 16.1.1 | 7 rows (all Live; none with media, its 6 conversation cache entries have no file)",
                           "felix23_ios16": "iOS 16.5 | 0 rows (conversation_message table empty)",
                           "hickman_ios15": "iOS 15.3.1 | 18 rows (all Live; 6 with media)",
                           "jess_ios15": "iOS 15.0.2 | 2 rows (all Live; 1 with media)",
                           "hickman_ios14": "iOS 14.3 | 22 rows (all Live; schema lacks quoted_server_message_id; none with media, cache_controller.db has no conversation entries)",
                           "hickman_ios13": "iOS 13.3.1 | 0 rows (conversation_message table empty)",
                           "ctf2020_ios12": "iOS 12.4 | 0 rows (conversation_message table empty)",
                           "iphone14plus_ios18": "iOS 18.0 | no Snapchat arroyo.db found",
                           "felix_ios17": "iOS 17.6.1 | no Snapchat arroyo.db found",
                           "fsfull002_ios17": "iOS 17.1 | no Snapchat arroyo.db found",
                           "hc_ios26": "iOS 26.5.2 | no Snapchat arroyo.db found",
                           "cookbook_ios1751": "iOS 17.5.1 | no Snapchat arroyo.db found",
                           "belkactf6": "no Snapchat files found",
                       },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation ID",
                "textColumn": "Message Text",
                "directionColumn": "Message Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Creation Timestamp",
                "senderColumn": "Sender Username",
                "mediaColumn": "Media",
                # Shows Live or Recovered under every bubble, so a recovered row cannot be
                # read as a live message.
                "extraColumns": ["Record Origin"],
            }
        },
    },
    "snapchatConversations": {
        "name": "Snapchat - Conversations (arroyo.db)",
        "description": "Conversation records from the conversation and feed_entry tables in "
                       "arroyo.db, both the rows a normal read returns and rows that are present "
                       "only before the write-ahead log is applied, distinguished by the Record "
                       "Origin column. Participant UUIDs are decoded from the "
                       "conversation_metadata protobuf and resolved against the snapchatter "
                       "store in primary.docobjects. WAL frames are not parsed, so absence of a "
                       "conversation here is not evidence it did not exist.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16", "last_update_date": "2026-08-16",
        "requirements": "blackboxprotobuf", "category": "Snapchat",
        "notes": "Record Origin. Live rows come back from a normal read. Recovered rows are "
                 "conversations whose client_conversation_id is present in conversation or "
                 "feed_entry as of the last checkpoint and in neither once the write-ahead log "
                 "is applied. Method and limits match Snapchat - Messages (arroyo.db); see its "
                 "notes, including that why a Recovered row is absent is not established.\n"
                 "Rows are the union of client_conversation_id across conversation and "
                 "feed_entry, so a conversation in only one of them is still reported. "
                 "Participant IDs come from the conversation_metadata protobuf at repeated "
                 "field 3, sub-path 1 > 1, as 16 raw bytes formatted as a UUID; on the tested "
                 "image every resolved conversation's participant list included the local "
                 "account id from user.plist. A participant missing from the snapchatter store "
                 "shows as a bare UUID, an unresolved identifier rather than a finding.\n"
                 "Conversation Type is reported as stored, since no source for the enum was "
                 "verified. Message Count counts conversation_message rows in the matching "
                 "view, not messages exchanged.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/user_scoped/*/arroyo/arroyo.db*',
                  '*/mobile/Containers/Data/Application/*/Documents/user_scoped/*/DocObjects/primary.docobjects*'),
        "output_types": "standard", "artifact_icon": "messages",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | 21 rows (all Live)",
            "otto_ios17": "iOS 17.5.1 | 140 rows (138 Live, 2 Recovered)",
            "dexter_ios18": "iOS 18.3.2 | 77 rows (76 Live, 1 Recovered)",
            "iphone12_ios18": "iOS 18.7 | 104 rows (all Live)",
            "hc_ios18_7": "iOS 18.7.8 | 14 rows (all Live)",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 18 rows (all Live)",
            "abe_ios16": "iOS 16.5 | 12 rows (all Live)",
            "hexordia_ios1651": "iOS 16.5.1 | 11 rows (all Live)",
            "magnet_ios16": "iOS 16.1.1 | 1 row",
            "felix23_ios16": "iOS 16.5 | 1 row",
            "hickman_ios15": "iOS 15.3.1 | 4 rows (all Live)",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "hickman_ios14": "iOS 14.3 | 2 rows (all Live)",
            "hickman_ios13": "iOS 13.3.1 | 2 rows (feed_entry lacks streak columns)",
            "ctf2020_ios12": "iOS 12.4 | 4 rows (feed_entry lacks streak columns)",
        },
    },
    "snapchatFriends": {
        "name": "Snapchat - Snapchatter Records",
        "description": "User records in the snapchatter table of primary.docobjects, with "
                       "usernames, user id and display name, and, where the app's own friends "
                       "list is found, whether it names the user. The table is not a friends list.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16", "last_update_date": "2026-09-21",
        "requirements": "none", "category": "Snapchat",
        "notes": "primary.docobjects (Documents/user_scoped/<account hash>/DocObjects/) is a "
                 "SQLite store whose snapchatter table keeps one FlatBuffers document per user "
                 "in column p, keyed by userId. The table is not a friends list. On the 12 "
                 "tested images that hold rows it included the account's own row and a row for "
                 "the teamsnapchat account, and on the 11 of them where the app's own friends "
                 "list was found, the table held 1,023 rows and the lists named 133 of them.\n"
                 "In Friends List says whether the app's own friends list for the account names "
                 "the user: YES, NO, or blank when no list for the account was found. The list "
                 "is read from the App Group container that holds "
                 "Library/Preferences/group.snapchat.picaboo.plist, in whichever of three "
                 "layouts is present: User/<user id>/app_group_plist_storage > "
                 "snapchatter_repository > FRIENDS (9 tested images), the group plist's user > "
                 "keyed_friends_array (hickman_ios14), or its share_user > SECTIONS > "
                 "DESTINATIONS whose CODED_SUBTYPE is SUBTYPE_FRIEND (jess_ios15). An account with "
                 "more than one layout is read from the first in that order; no tested image had "
                 "more than one. A list is tied "
                 "to the store it describes by the SHA-256 of the account's user id, which "
                 "equalled the account hash folder name on the 14 tested images whose App Group "
                 "names an account. Where a list was found, the account's own row read NO, and the "
                 "teamsnapchat row read NO in the first layout and YES in the two older ones. On "
                 "iphone12_ios18 the App Group held none of the three layouts, so In Friends List "
                 "is blank on its 220 rows; on magnet_ios16 the list was present and empty, so In "
                 "Friends List is NO on all 129 rows there. None of the users the lists named "
                 "lacked a snapchatter row. Mutual Friend (as stored) is IS_MUTUAL_FRIEND, which "
                 "only the first layout records: YES on 60 and NO on 70 of the 130 users it "
                 "listed, and blank on every other row.\n"
                 "789 of the 890 rows the lists did not name were named in the store's "
                 "snapchatters__displaysuggestion documents. What that table's page numbers mean "
                 "is not established, and on otto_ios17 its page 7 also named 100 of the 104 "
                 "users that image's list named, so a row named there is not reported as a "
                 "suggestion.\n"
                 "Username, Mutable Username and Legacy Username come from the store's own "
                 "index_snapchatter* tables, joined on rowid, not from the document blob. On the "
                 "11 tested images whose store has all three, Mutable Username was the same as "
                 "Username on all 1,157 rows, so what it adds is not established. Legacy Username "
                 "differed from Username on 77 of those rows, and on every row of jess_ios15 and "
                 "magnet_ios16 Legacy Username was the same as both Username and Mutable "
                 "Username.\n"
                 "Display Name is read from the document's third string field. No published "
                 "schema for the document was found, so the field position was established on "
                 "the tested image and is self-checked at parse time: the value is only "
                 "reported when the document's first field equals the row's userId column, and "
                 "on the tested image the document's username fields equalled the index tables "
                 "on all 120 rows. When the layout check fails the column is left blank.\n"
                 "Older store generations carry fewer index tables (an iOS 14 era file has "
                 "only the username index) and iOS 12 and 13 era files predate the "
                 "snapchatter table entirely; missing index tables leave Mutable Username and "
                 "Legacy Username blank, and pre-snapchatter stores report no rows, with a log "
                 "line saying so. The "
                 "display-name field position also held on the iOS 14 era store, where all "
                 "86 rows passed the layout self-check.\n"
                 "No timestamps are reported: none were identified in the SQL columns, and "
                 "none in the document were established. The lists' BEST_FRIENDS, RECENTS and "
                 "GROUPS entries are not parsed, and neither is any blocked state.\n"
                 "Reference: dfjsim, 'Snapchat_Auto, docs/related_ileapp.md', "
                 "https://github.com/dfjsim/Snapchat_Auto/blob/"
                 "93677d19a70caebb666d89dcb0f40d4693e2aacf/docs/related_ileapp.md#L114",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/user_scoped/*/DocObjects/primary.docobjects*',
                  '*/mobile/Containers/Shared/AppGroup/*/Library/Preferences/group.snapchat.picaboo.plist',
                  '*/mobile/Containers/Shared/AppGroup/*/User/*/app_group_plist_storage'),
        "output_types": "standard", "artifact_icon": "users",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | 120 rows (4 in the friends list)",
            "otto_ios17": "iOS 17.5.1 | 293 rows (104 in the friends list)",
            "dexter_ios18": "iOS 18.3.2 | 13 rows (10 in the friends list)",
            "iphone12_ios18": "iOS 18.7 | 220 rows (no friends list found)",
            "hc_ios18_7": "iOS 18.7.8 | 4 rows (2 in the friends list)",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 106 rows (1 in the friends list)",
            "abe_ios16": "iOS 16.5 | 115 rows (5 in the friends list)",
            "hexordia_ios1651": "iOS 16.5.1 | 3 rows (1 in the friends list)",
            "magnet_ios16": "iOS 16.1.1 | 129 rows (friends list empty)",
            "hickman_ios15": "iOS 15.3.1 | 121 rows (3 in the friends list)",
            "jess_ios15": "iOS 15.0.2 | 33 rows (1 in the friends list)",
            "hickman_ios14": "iOS 14.3 | 86 rows (2 in the friends list; store has only the username index table)",
            "felix23_ios16": "iOS 16.5 | 0 rows (snapchatter table empty)",
            "hickman_ios13": "iOS 13.3.1 | 0 rows (store predates the snapchatter table)",
            "ctf2020_ios12": "iOS 12.4 | 0 rows (store predates the snapchatter table)",
        },
    },
    "snapchatGallerySearch": {
        "name": "Snapchat - Memories Search Index",
        "description": "Per-snap rows from the app's gallery_search index: the app's own "
                       "time, location, visual and meta tags, caption text, and visual "
                       "concept labels with their stored confidence values.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16", "last_update_date": "2026-08-16",
        "requirements": "none", "category": "Snapchat",
        "notes": "search.sqlite3 (Documents/gallery_search/<n>/<account hash>/) is an index the "
                 "app keeps over Memories snaps. All "
                 "values are app-generated tags reported as stored, not observations about "
                 "the media itself: location tags are place-name strings (down to street "
                 "level on the tested image), visual tags and concepts are the app's "
                 "labels with their stored confidence, and the time tag is a date string.\n"
                 "Tag rows live in FTS content tables keyed by docid; docid was verified "
                 "equal to snap_id_table's rowid on the tested image by matching each "
                 "row's visual tags against snap_visual_tag_conf_table for the same snap "
                 "id. The snap id refers to a Memories entry; linking it to media files "
                 "is not done here.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/gallery_search/*/search.sqlite3*',),
        "output_types": "standard", "artifact_icon": "search",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | 13 rows",
            "hickman_ios15": "iOS 15.3.1 | 13 rows",
            "hickman_ios14": "iOS 14.3 | 9 rows",
            "hickman_ios13": "iOS 13.3.1 | 11 rows",
            "dexter_ios18": "iOS 18.3.2 | 2 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "abe_ios16": "iOS 16.5 | 1 row",
            "otto_ios17": "iOS 17.5.1 | 0 rows (index tables empty)",
            "iphone12_ios18": "iOS 18.7 | no gallery_search search.sqlite3 found",
        },
    },
    "snapchatAccount": {
        "name": "Snapchat - Account",
        "description": "Account values from the app's Documents/user.plist: username, user id, "
                       "laguna id, and client encryption values, reported as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16", "last_update_date": "2026-08-16",
        "requirements": "none", "category": "Snapchat",
        "notes": "user.plist is not a property list despite its name: it begins with the "
                 "magic TSAF and carries length-delimited strings. The format is otherwise "
                 "undocumented here, so values are read as the string that follows each named "
                 "key token, and user_id and laguna_id are additionally required to be "
                 "UUID-shaped before being reported. On the tested image user_id matched a "
                 "userId in the snapchatter store whose username matched this file's username "
                 "value.\n"
                 "The client_encryption identifier, encryption_key and initialization_vector "
                 "are reported as stored; what they encrypt is not established here. Files "
                 "that do not begin with the TSAF magic are skipped, since Documents/user.plist "
                 "is not a Snapchat-specific file name.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/user.plist',),
        "output_types": "standard", "artifact_icon": "user",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | 6 rows",
            "otto_ios17": "iOS 17.5.1 | 6 rows",
            "dexter_ios18": "iOS 18.3.2 | 6 rows",
            "iphone12_ios18": "iOS 18.7 | 6 rows",
            "hc_ios18_7": "iOS 18.7.8 | 6 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 6 rows",
            "abe_ios16": "iOS 16.5 | 6 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 6 rows",
            "magnet_ios16": "iOS 16.1.1 | 6 rows",
            "hickman_ios15": "iOS 15.3.1 | 6 rows",
            "jess_ios15": "iOS 15.0.2 | 5 rows",
            "hickman_ios14": "iOS 14.3 | 5 rows",
            "hickman_ios13": "iOS 13.3.1 | 5 rows",
            "ctf2020_ios12": "iOS 12.4 | 5 rows",
        },
    },
    "snapchatChatMedia": {
        "name": "Snapchat - Chat Media",
        "description": "Conversation media entries in the app's cache index (cache_controller.db), each tied "
                       "to its message by an id recorded in the entry or in the message, with the cached file "
                       "shown when it is a recognised media format.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-19", "last_update_date": "2026-09-19",
        "requirements": "nska_deserialize", "category": "Snapchat",
        "notes": "cache_controller.db (Documents/global_scoped/cachecontroller/) indexes the files the "
                 "app caches. This artifact reports the entries that name a conversation. On the tested "
                 "images their EXTERNAL_KEY had the form [<kind>~]1:<conversation id>:<message "
                 "number>:0:0 (77 entries on 11 images). Where the message's conversation_message row "
                 "was present (57 entries), the message number equalled its server_message_id; it "
                 "matched client_message_id only where the two ids were equal. Entry Kind is the text "
                 "before the tilde as stored (content, thumbnail, firstframe, profilethumbnail, or "
                 "none); what each kind means is not established. A second link comes from the message: "
                 "conversation_message.local_message_references held an NSKeyedArchiver property list "
                 "after 8 bytes on all 14 values seen, and its MEDIA_ID equalled an entry's EXTERNAL_KEY "
                 "for 9 entries.\n"
                 "The file is the entry's CACHE_KEY inside the "
                 "Documents/com.snap.file_manager_<n>_SCContent_ folder whose name ends with the entry's "
                 "USER_ID (one folder name ends with nothing, matching entries whose USER_ID is empty). "
                 "Files are read as stored: on the tested images 38 of the 39 non-empty files were JPEG, "
                 "PNG, WebP, MPEG-4 or QuickTime with no decryption needed and are shown, and one "
                 "78-byte file matched no media format and is reported as unrecognised. Files of the "
                 "content kind were empty (9 files). Format is read from the file's bytes, not its name, "
                 "and an MPEG-4 brand does not say whether the file holds video. Format and Size (bytes) "
                 "are blank when the entry's file is not on disk.\n"
                 "Cache Entry Deleted is DELETED_TIMESTAMP_MILLIS. On the tested images the 38 entries "
                 "carrying one had no file on disk and the 48 without one had a file. Message In "
                 "arroyo.db is No for 20 entries whose ids match no conversation_message row in a normal "
                 "read, and Message Created is blank on exactly those entries. Account (USER_ID as "
                 "stored) held one value on each tested image.\n"
                 "Limits. Only app containers that also hold arroyo.db are read, since "
                 "cache_controller.db alone does not show a container belongs to Snapchat. "
                 "local_message_references is read from the normal view of arroyo.db only. Media Context "
                 "Type is reported as stored; no source for its values was verified. The entry's "
                 "IS_AUTHORITATIVE, EXPIRATION_TIMESTAMP_MILLIS, CONTENT_CLAIM_METADATA and "
                 "CONTENT_ATTRIBUTION columns are not reported. Entries that name no conversation, such "
                 "as the lens and Memories entries, are not reported here; Memories entries are in "
                 "Snapchat - Memories Media. The cache_controller.db table of deleted files "
                 "(CACHE_FILE_SAMPLED_TOMBSTONE) is not parsed: it records no EXTERNAL_KEY, and on the "
                 "tested images none of its rows joined to a conversation entry.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/user_scoped/*/arroyo/arroyo.db*',
                  '*/mobile/Containers/Data/Application/*/Documents/global_scoped/cachecontroller/cache_controller.db*',
                  '*/mobile/Containers/Data/Application/*/Documents/com.snap.file_manager_*_SCContent_*/*'),
        "output_types": "standard", "artifact_icon": "paperclip",
        "sample_data": {
                           "abe_ios16": "iOS 16.5 | 7 rows (7 with media)",
                           "dexter_ios18": "iOS 18.3.2 | 14 rows (10 with media, 4 empty files)",
                           "hc_ios18_7": "iOS 18.7.8 | 3 rows (2 with media, 1 unrecognised file)",
                           "hexordia_ios1651": "iOS 16.5.1 | 13 rows (3 with media, 1 empty file, 9 not on disk)",
                           "hickman_ios15": "iOS 15.3.1 | 14 rows (6 with media, 3 empty files, 5 not on disk)",
                           "iphone11_ios17": "iOS 17.3 | 15 rows (2 with media, 1 empty file, 12 not on disk)",
                           "iphone12_ios18": "iOS 18.7 | 1 row (with media)",
                           "iphone14plus_ios18_mvs2025": "iOS 18.0 | 2 rows (2 with media)",
                           "jess_ios15": "iOS 15.0.2 | 1 row (with media)",
                           "magnet_ios16": "iOS 16.1.1 | 6 rows (none on disk)",
                           "otto_ios17": "iOS 17.5.1 | 10 rows (4 with media, 6 not on disk)",
                           "felix23_ios16": "iOS 16.5 | 0 rows (cache_controller.db has no conversation entries)",
                           "hickman_ios14": "iOS 14.3 | 0 rows (cache_controller.db has no conversation entries)",
                           "hickman_ios13": "iOS 13.3.1 | 0 rows (no cache_controller.db)",
                           "ctf2020_ios12": "iOS 12.4 | 0 rows (no cache_controller.db)",
                           "iphone14plus_ios18": "iOS 18.0 | 0 rows (no Snapchat arroyo.db found)",
                           "felix_ios17": "iOS 17.6.1 | 0 rows (no Snapchat arroyo.db found)",
                           "fsfull002_ios17": "iOS 17.1 | 0 rows (no Snapchat arroyo.db found)",
                           "hc_ios26": "iOS 26.5.2 | 0 rows (no Snapchat arroyo.db found)",
                           "cookbook_ios1751": "iOS 17.5.1 | 0 rows (no Snapchat arroyo.db found)",
                       },
    },
    "snapchatMemories": {
        "name": "Snapchat - Memories",
        "description": "Memories from the app's Memories database (scdb-27.sqlite3), and snap keys with no "
                       "Memory row, with location from gallery.encrypteddb and media decrypted from the app's "
                       "caches and stored thumbnails when the keys are available.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-19", "last_update_date": "2026-09-19",
        "requirements": "nska_deserialize, pycryptodome", "category": "Snapchat",
        "notes": "Sources. Documents/gallery_data_object/<n>/<profile>/scdb-27.sqlite3 is a Core Data "
                 "store with one ZGALLERYSNAP row per Memory. The profile folder name equalled the "
                 "SHA-256 of user_id in Documents/user.plist on 14 of the 15 tested images carrying this "
                 "store, and Account User ID is filled only when it does. "
                 "Documents/gallery_encrypted_db/<n>/<profile>/gallery.encrypteddb is SQLCipher with "
                 "SQLCipher 3 settings, keyed with the raw 32-byte keychain item "
                 "egocipher.key.avoidkeyderivation. It was decrypted on 7 tested images, and on the 6 of "
                 "them holding rows every row was in its write-ahead log, which is replayed. It holds "
                 "each snap's AES key and IV (snap_key_iv), coordinates (snap_location_table) and an "
                 "address title (snap_address_title). Supply the keychain with --keychain; a keychain "
                 "the extraction carries is used when none is supplied. The decrypted copy is made in a "
                 "temporary folder that is deleted once read. Snapchat's SQLCipher build names its "
                 "automatic indexes sqlcph_autoindex_*, which stock SQLite refuses as an orphan index, "
                 "so they are renamed to sqlite_autoindex_* in that copy; the names are the same length "
                 "and nothing else changes.\n"
                 "Times. Created is ZCREATETIMEUTC and Captured is ZCAPTURETIMEUTC, both Cocoa seconds. "
                 "Read that way, Created was within a minute of the creation time of the Memory's own "
                 "cache_controller.db entry (Unix milliseconds) on 7 of the 31 Live Memories with such "
                 "an entry, on 4 images; for the other 24 the entry was created 59 to 1,891 days after "
                 "Created. Captured is blank where ZCAPTURETIMEUTC is empty. Capture Time Zone is "
                 "ZTIMEZONENAME as stored.\n"
                 "Keys. On 2 of the 9 tested images holding Memories the key and IV are also stored in "
                 "ZGALLERYSNAP.ZENCRYPTION, an NSKeyedArchiver archive, so the media of those Memories "
                 "whose key is not wrapped decrypts without a keychain. A 48-byte key with a 32-byte IV "
                 "is wrapped: it is the real key and IV encrypted with AES-CBC and PKCS#7 padding under "
                 "the master key in the keychain item com.snapchat.keyservice.persistedkey, and it is "
                 "unwrapped only when that item is present. Key State says which applied. Private Entry "
                 "is ZGALLERYENTRY.ZISPRIVATE as stored; on the tested images each of the 16 Memories "
                 "whose entry was private and whose key could be read had a wrapped key, and no other "
                 "Memory did.\n"
                 "Media. The Media column shows the best recovered file for the Memory (its full media, "
                 "else a preview, else a thumbnail) and its overlay when one was recovered. Recovered "
                 "Media lists every file found, and Snapchat - Memories Media gives each one its own row "
                 "with its source. Files come from the SCContent cache, located through "
                 "cache_controller.db entries named snap-media-, snap-overlay- or snap-rendered-lowres- "
                 "plus the snap or media id (the reference also names g-media-, which is matched but did "
                 "not occur on the tested images); from the Library/Caches/caching-media .pack files, "
                 "linked by the key that opens them; and from ZGALLERYSNAPMINITHUMBNAIL, a small "
                 "thumbnail per snap kept in scdb-27.sqlite3 and encrypted with the snap's key. All "
                 "three decrypt with AES-256-CBC using the snap's key and IV. Every stored thumbnail "
                 "whose Memory had a usable key decrypted (51 on 3 images); the table was empty on the 2 "
                 "images whose keys are in ZENCRYPTION.\n"
                 "Location. Latitude and Longitude come from snap_location_table and need the keychain; "
                 "KML is written for located rows. Address Title comes from snap_address_title; when the "
                 "Memory's own snap id has none, a title stored for a snap id sharing the Memory's key "
                 "is used. On the tested images the 52 snap ids sharing a Memory's key all carried that "
                 "Memory's coordinates, and they are not reported as rows of their own.\n"
                 "Record Origin. Live rows come from a normal read of scdb-27.sqlite3. Recovered rows "
                 "are ZGALLERYSNAP rows present only before the write-ahead log is applied (Recovery "
                 "Method WAL diff, 4 rows on 2 images), or snap ids with key and location rows in "
                 "gallery.encrypteddb that have no Memory row in either read and share no key with one "
                 "(Recovery Method Key row with no Memory row, 5 rows on 2 images), whose times and "
                 "metadata are blank. Why a Memory row is absent is not established here.\n"
                 "As stored: Media Format (ZSERVLETMEDIAFORMAT), Width, Height, Duration (ZDURATION), "
                 "Front Camera (ZCAMERAFRONTFACING) and Camera Roll ID (ZCAMERAROLLID). Caption is the "
                 "text of each caption in the ZGALLERYSNAPDETAIL.ZOVERLAY archive, joined with ' | '. "
                 "Entry Title is ZGALLERYENTRY.ZTITLE. Duplicated From Snap ID is ZDUPLICATEDFROMSNAPID "
                 "(7 rows). Media ID equalled Entry ID on 18 of the 94 rows with a Media ID; both are "
                 "reported as stored. Recovery Method and Recovery Location are filled only on Recovered "
                 "rows.\n"
                 "Limits. Without the keychain, location, address titles and the media of Memories whose "
                 "keys are only in gallery.encrypteddb stay unreadable, and Key State says so. A wrapped "
                 "key with no persistedkey keeps that Memory's media locked. The gallery_search index is "
                 "reported separately (Snapchat - Memories Search Index).\n"
                 "Reference: dfjsim, 'Snapchat_Auto, a fork of DFIR-HBG and stark4n6's Snapchat_Auto: "
                 "snapchat_ios_memories_decryption.md', "
                 "https://github.com/dfjsim/Snapchat_Auto/blob/58954948faf6ba682e9b09f968eb1c2cdef9796b/docs/snapchat_ios_memories_decryption.md?plain=1#L165 "
                 "(gallery.encrypteddb and egocipher), #L282 (the wrapped key and persistedkey), #L204 "
                 "(the cache_controller.db entries).",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/gallery_data_object/*/scdb-27.sqlite3*',
                  '*/mobile/Containers/Data/Application/*/Documents/gallery_encrypted_db/*/gallery.encrypteddb*',
                  '*/mobile/Containers/Data/Application/*/Documents/global_scoped/cachecontroller/cache_controller.db*',
                  '*/mobile/Containers/Data/Application/*/Documents/com.snap.file_manager_*_SCContent_*/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/caching-media/*.pack',
                  '*/mobile/Containers/Data/Application/*/Documents/user.plist'),
        "output_types": "all", "artifact_icon": "photo",
        "sample_data": {
                           "iphone11_ios17": "iOS 17.3 | 28 rows (25 Live, 3 Recovered; 28 with media, 27 located)",
                           "hickman_ios15": "iOS 15.3.1 | 28 rows (all Live; 21 with media, 27 located; 7 keys stay wrapped)",
                           "hickman_ios14": "iOS 14.3 | 14 rows (all Live; no keychain, no media or location)",
                           "hickman_ios13": "iOS 13.3.1 | 11 rows (all Live; no keychain, no media or location)",
                           "dexter_ios18": "iOS 18.3.2 | 8 rows (4 Live, 4 Recovered; 7 with media, 4 located)",
                           "ctf2020_ios12": "iOS 12.4 | 3 rows (all Live; no keychain, no media or location)",
                           "hexordia_ios1651": "iOS 16.5.1 | 3 rows (all Live; no keychain, no media or location)",
                           "abe_ios16": "iOS 16.5 | 2 rows (1 Live, 1 Recovered; 2 with media, 2 located)",
                           "hc_ios18_7": "iOS 18.7.8 | 1 row (Live; with media, located; run with --keychain)",
                           "otto_ios17": "iOS 17.5.1 | 1 row (Recovered, key row only; with media, located)",
                           "felix23_ios16": "iOS 16.5 | 0 rows (Memories table empty)",
                           "iphone12_ios18": "iOS 18.7 | 0 rows (Memories table empty)",
                           "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows (Memories table empty)",
                           "jess_ios15": "iOS 15.0.2 | 0 rows (Memories table empty)",
                           "magnet_ios16": "iOS 16.1.1 | 0 rows (Memories table empty)",
                           "iphone14plus_ios18": "iOS 18.0 | 0 rows (no Snapchat Memories database found)",
                           "felix_ios17": "iOS 17.6.1 | 0 rows (no Snapchat Memories database found)",
                           "fsfull002_ios17": "iOS 17.1 | 0 rows (no Snapchat Memories database found)",
                           "hc_ios26": "iOS 26.5.2 | 0 rows (no Snapchat Memories database found)",
                           "cookbook_ios1751": "iOS 17.5.1 | 0 rows (no Snapchat Memories database found)",
                       },
    },
    "snapchatMemoriesMedia": {
        "name": "Snapchat - Memories Media",
        "description": "Memories media found through the app's cache index, caches and thumbnail table, "
                       "decrypted with its snap's key where one is available, with the file it came from and "
                       "how it was linked, plus cache files no available key opened.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-19", "last_update_date": "2026-09-19",
        "requirements": "nska_deserialize, pycryptodome", "category": "Snapchat",
        "notes": "One row per file. SCContent files are located through their cache_controller.db entry "
                 "(snap-media-, snap-overlay- or snap-rendered-lowres-, or g-media- as the reference "
                 "describes, plus a snap id or the Memory's ZMEDIAID) in the SCContent folder named for "
                 "the entry's USER_ID; a file named by several Memories is one row listing each of them. "
                 "Library/Caches/caching-media .pack files have opaque names, so the first block of each "
                 "file is decrypted with every usable key, and the key whose output starts with the pack "
                 "header (01 00 00 00 and a little-endian length) and a media signature links the file. "
                 "Every snap id holding that key and a Memory row is listed, and Snap IDs Sharing The "
                 "Key counts all snap ids with the key. ZGALLERYSNAPMINITHUMBNAIL rows are thumbnails "
                 "kept in scdb-27.sqlite3, encrypted with the snap's key. How the keys are found is "
                 "described in Snapchat - Memories.\n"
                 "On the tested images every .pack file an available key opened, whether its name ended "
                 "-0 or -1, began with its own pack header under a snap's key and held its full declared "
                 "length (66 files on 6 images), and where one item had both they were different images "
                 "of different lengths. Each file is therefore decrypted on its own. The reference cited "
                 "in Snapchat - Memories describes numbered files as pieces of one item to be joined; "
                 "that did not hold on the tested images.\n"
                 "File says whether the file is on disk and whether it opened. Not on disk rows are "
                 "entries whose file is absent; all 26 on the tested images carried a time in Cache "
                 "Entry Deleted. Encrypted rows with no usable key belong to Memories whose key could "
                 "not be read. Rows saying no available key opened the files summarise, per folder, "
                 ".pack files that no available key opens; Linked By, Snap IDs and Memory Created are "
                 "blank on them, and whether those files hold Memories media is not established. Memory "
                 "Created is also blank on files linked only to a key row with no Memory row (11 rows on "
                 "2 images), since such rows record no times. Complete compares the payload with the "
                 "length declared by the 8-byte header that .pack files, and on the tested images the "
                 "snap-rendered-lowres SCContent files, start with; it is blank for files without that "
                 "header. All 75 files with the header on the tested images were complete. Format is "
                 "read from the decrypted bytes. Role is the entry's prefix for SCContent files, "
                 "caching-media for .pack files and the table name for thumbnails; Kind groups roles "
                 "into media, overlay, preview and thumbnail, a grouping made here rather than by the "
                 "app.\n"
                 "Memory Created, Record Origin and Key Source come from the Memory a file belongs to, "
                 "so they repeat across that Memory's files. Recovered media is written to the report's "
                 "media folder decrypted, and Source File names the encrypted file in the extraction.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/gallery_data_object/*/scdb-27.sqlite3*',
                  '*/mobile/Containers/Data/Application/*/Documents/gallery_encrypted_db/*/gallery.encrypteddb*',
                  '*/mobile/Containers/Data/Application/*/Documents/global_scoped/cachecontroller/cache_controller.db*',
                  '*/mobile/Containers/Data/Application/*/Documents/com.snap.file_manager_*_SCContent_*/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/caching-media/*.pack',
                  '*/mobile/Containers/Data/Application/*/Documents/user.plist'),
        "output_types": "standard", "artifact_icon": "photo-search",
        "sample_data": {
                           "iphone11_ios17": "iOS 17.3 | 98 rows (69 recovered, 26 not on disk)",
                           "hickman_ios15": "iOS 15.3.1 | 31 rows (31 recovered)",
                           "hickman_ios14": "iOS 14.3 | 27 rows (encrypted, no keychain)",
                           "dexter_ios18": "iOS 18.3.2 | 25 rows (23 recovered)",
                           "abe_ios16": "iOS 16.5 | 13 rows (13 recovered)",
                           "hickman_ios13": "iOS 13.3.1 | 11 rows (encrypted, no keychain)",
                           "hexordia_ios1651": "iOS 16.5.1 | 7 rows (encrypted, no keychain)",
                           "hc_ios18_7": "iOS 18.7.8 | 5 rows (5 recovered, 1 of them MPEG-4; run with --keychain)",
                           "ctf2020_ios12": "iOS 12.4 | 3 rows (encrypted, no keychain)",
                           "otto_ios17": "iOS 17.5.1 | 2 rows (2 recovered)",
                           "felix23_ios16": "iOS 16.5 | 0 rows (Memories table empty)",
                           "iphone12_ios18": "iOS 18.7 | 0 rows (Memories table empty)",
                           "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows (Memories table empty)",
                           "jess_ios15": "iOS 15.0.2 | 0 rows (Memories table empty)",
                           "magnet_ios16": "iOS 16.1.1 | 0 rows (Memories table empty)",
                           "iphone14plus_ios18": "iOS 18.0 | 0 rows (no Snapchat Memories database found)",
                           "felix_ios17": "iOS 17.6.1 | 0 rows (no Snapchat Memories database found)",
                           "fsfull002_ios17": "iOS 17.1 | 0 rows (no Snapchat Memories database found)",
                           "hc_ios26": "iOS 26.5.2 | 0 rows (no Snapchat Memories database found)",
                           "cookbook_ios1751": "iOS 17.5.1 | 0 rows (no Snapchat Memories database found)",
                       },
    },
}

import datetime
import hashlib
import io
import os
import plistlib
import re
import sqlite3
import struct
import tempfile

import nska_deserialize
from Crypto.Cipher import AES

from scripts import blackboxprotobuf
from scripts.ilapfuncs import (artifact_processor, check_in_embedded_media, check_in_media,
                               get_sqlite_db_path, logfunc)
from scripts.ios_keychain import active_keychain_path, find_keychain_secrets
from scripts.sqlcipher_decrypt import decrypt_sqlcipher_db

# blackboxprotobuf raises these when a blob does not decode as protobuf.
_PB_ERRORS = (ValueError, TypeError, IndexError, KeyError, AttributeError)
# nska_deserialize raises its own error for a malformed archive, plistlib's for a file that
# is not a property list, and the rest for archives whose objects are not the shape expected.
_NSKA_ERRORS = (nska_deserialize.DeserializeError, plistlib.InvalidFileException, ValueError,
                TypeError, KeyError, IndexError, AttributeError, EOFError, OverflowError,
                struct.error)
_TSAF_MAGIC = b'TSAF'
_UUID_RE = re.compile(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-'
                      r'[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _app_container(path):
    '''The .../Data/Application/<UUID> prefix of a path, or '' when not under one.'''
    normalized = str(path).replace('\\', '/')
    marker = '/Data/Application/'
    # The last occurrence belongs to the evidence; an earlier one would be in the folder
    # the examiner chose for the report.
    index = normalized.rfind(marker)
    if index == -1:
        return ''
    end = normalized.find('/', index + len(marker))
    return normalized[:end] if end != -1 else normalized


def _find(files_found, *suffixes):
    for file_found in files_found:
        if str(file_found).endswith(suffixes):
            return str(file_found)
    return ''


def _find_sibling(files_found, anchor_path, *suffixes):
    '''The matching file from the same app container as anchor_path, else any match.'''
    container = _app_container(anchor_path)
    fallback = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith(suffixes):
            continue
        if container and _app_container(file_found) == container:
            return file_found
        if not fallback:
            fallback = file_found
    return fallback


def _rows(source_path, sql, params=()):
    if not source_path:
        return []
    try:
        db = sqlite3.connect(f'file:{get_sqlite_db_path(source_path)}?mode=ro', uri=True)
    except sqlite3.Error:
        return []
    cursor = db.cursor()
    try:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


def _rows_pre_wal(source_path, sql):
    '''Run sql against the database file as of its last checkpoint, ignoring the WAL.

    immutable=1 is strictly read-only. Unlike mode=ro it does not even create a -shm
    sidecar, so no evidence file is altered.
    '''
    if not source_path:
        return []
    try:
        db = sqlite3.connect(f'file:{get_sqlite_db_path(source_path)}?immutable=1', uri=True)
    except sqlite3.Error:
        return []
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


def _table_columns(source_path, table):
    return {row[1] for row in _rows(source_path, f'PRAGMA table_info({table})')}


def _tolerant_select(source_path, table, columns, tail=''):
    '''A SELECT that names every requested column, substituting NULL AS <name> for columns
    the file's schema generation does not have, so one absent column does not silently drop
    every row. Older arroyo.db generations carry strict subsets of the current columns; on
    the tested images nothing was renamed, only absent.
    '''
    present = _table_columns(source_path, table)
    select_list = ', '.join(
        column if column in present else f'NULL AS {column}' for column in columns)
    return f'SELECT {select_list} FROM {table} {tail}'


def _superseded(source_path, sql, key_indexes):
    '''Rows present at the last checkpoint and absent once the write-ahead log is applied.

    Both sides are consistent SQLite views of the same file, one ignoring the WAL and one
    applying it, compared on the columns at key_indexes rather than on row counts, since a
    table can hold the same number of rows in both views with different rows in it.
    Empty when the file has no WAL alongside it. Why a row did not survive into the
    committed state is not established here.
    '''
    def key(row):
        return tuple(row[index] for index in key_indexes)

    committed = {key(row) for row in _rows(source_path, sql)}
    return [row for row in _rows_pre_wal(source_path, sql) if key(row) not in committed]


# --- primary.docobjects (snapchatter store) -------------------------------------------------

def _fb_string_field(buf, slot):
    '''String value of a FlatBuffers root-table field slot, or '' when absent or not a string.

    Reads only the root table: root offset, its vtable, the slot's field offset, then the
    field as an offset to a length-prefixed UTF-8 string. Any structural mismatch returns ''.
    '''
    try:
        table_pos = struct.unpack_from('<I', buf, 0)[0]
        vtable_offset = struct.unpack_from('<i', buf, table_pos)[0]
        vtable_pos = table_pos - vtable_offset
        vtable_size = struct.unpack_from('<H', buf, vtable_pos)[0]
        if slot >= (vtable_size - 4) // 2:
            return ''
        field_offset = struct.unpack_from('<H', buf, vtable_pos + 4 + slot * 2)[0]
        if field_offset == 0:
            return ''
        field_pos = table_pos + field_offset
        string_pos = field_pos + struct.unpack_from('<I', buf, field_pos)[0]
        string_len = struct.unpack_from('<I', buf, string_pos)[0]
        if string_pos + 4 + string_len > len(buf):
            return ''
        return buf[string_pos + 4:string_pos + 4 + string_len].decode('utf-8')
    except (struct.error, IndexError, UnicodeDecodeError, TypeError):
        return ''


# Field slots in the snapchatter FlatBuffers document, established on the tested image:
# slot 0 equalled the row's userId SQL column on all 120 rows, slots 1, 14 and 15 equalled
# the store's own username index tables, and slot 2 held the display name string. Slot 2 is
# only trusted when the slot-0 check passes on that row.
_FB_SLOT_USER_ID = 0
_FB_SLOT_DISPLAY_NAME = 2


def _display_name(blob, user_id):
    if not isinstance(blob, (bytes, bytearray)):
        return ''
    buf = bytes(blob)
    if _fb_string_field(buf, _FB_SLOT_USER_ID) != user_id:
        return ''
    return _fb_string_field(buf, _FB_SLOT_DISPLAY_NAME)


def _store_tables(doc_store_path):
    return {row[0] for row in _rows(
        doc_store_path, "SELECT name FROM sqlite_master WHERE type = 'table'")}


def _snapchatter_sql(doc_store_path):
    '''SELECT for snapchatter rows with whichever index tables this store generation has.

    Older stores lack some or all of the index_snapchatter* tables (an iOS 14 era file has
    only index_snapchatterusername, and iOS 12 and 13 era files have no snapchatter table
    at all), and a join against a missing table would silently drop every row. Absent
    sources are substituted with NULL under the same name.
    '''
    tables = _store_tables(doc_store_path)
    if 'snapchatter' not in tables:
        return ''
    selects = ['snapchatter.userId', 'snapchatter.p']
    joins = []
    for table, column in (('index_snapchatterusername', 'username'),
                          ('index_snapchattermutableUsername', 'mutableUsername'),
                          ('index_snapchatterlegacyUsername', 'legacyUsername')):
        if table in tables:
            selects.append(f'{table}.{column}')
            joins.append(f'LEFT JOIN {table} ON {table}.rowid = snapchatter.rowid')
        else:
            selects.append(f'NULL AS {column}')
    return f"SELECT {', '.join(selects)} FROM snapchatter {' '.join(joins)}"


def _friend_records(doc_store_path):
    '''snapchatter rows as {userId: (username, display_name)}, usernames from index tables.'''
    friends = {}
    sql = _snapchatter_sql(doc_store_path)
    if not sql:
        return friends
    for user_id, blob, username, _mutable, _legacy in _rows(doc_store_path, sql):
        if user_id:
            friends[user_id] = (username or '', _display_name(blob, user_id))
    return friends


def _friend_name(friends, user_id, index=0):
    return friends.get(user_id, ('', ''))[index]


# --- the app's own friends list (App Group) -------------------------------------------------

_GROUP_PLIST_SUFFIX = '/Library/Preferences/group.snapchat.picaboo.plist'
_USER_LIST_RE = re.compile(r'/User/(?P<user>[^/]+)/app_group_plist_storage$')
_DOC_STORE_RE = re.compile(r'/Documents/user_scoped/(?P<account>[^/]+)/DocObjects/'
                           r'primary\.docobjects$')


def _plist_file(path):
    '''A property list file as a dict, or {} when it cannot be read as one.'''
    try:
        with open(path, 'rb') as handle:
            values = plistlib.load(handle)
    except (OSError,) + _NSKA_ERRORS:
        return {}
    return values if isinstance(values, dict) else {}


def _account_hash(user_id):
    '''SHA-256 of a user id, the name the app gives the account's user_scoped folder.'''
    return hashlib.sha256(user_id.encode('utf-8')).hexdigest() if isinstance(user_id, str) else ''


def _friends_lists(files_found):
    '''The app's own friends lists, as ({account hash: friends}, {account hash: source path}).

    friends maps each listed user id to its IS_MUTUAL_FRIEND value as YES or NO, or ''
    where the layout records none. Lists are read only from App Group containers that hold
    Library/Preferences/group.snapchat.picaboo.plist, in three layouts: User/<user
    id>/app_group_plist_storage -> snapchatter_repository -> FRIENDS, then the group plist's
    user -> keyed_friends_array, then its share_user -> SECTIONS -> DESTINATIONS marked
    SUBTYPE_FRIEND. When an account has more than one, the first of those is used.
    '''
    roots = {}
    for file_found in files_found:
        path = str(file_found)
        if _norm(path).endswith(_GROUP_PLIST_SUFFIX) and os.path.isfile(path):
            roots[_norm(path)[:-len(_GROUP_PLIST_SUFFIX)]] = path
    lists, sources, layouts = {}, {}, {}

    def add(user_id, friends, path, layout):
        account = _account_hash(user_id)
        if not account:
            return
        if account in lists:
            logfunc(f'Snapchat: an account has friends lists in more than one App Group layout; '
                    f'the {layouts[account]} list is used and the {layout} list is not.')
            return
        lists[account], sources[account], layouts[account] = friends, path, layout

    for file_found in files_found:
        path = str(file_found)
        match = _USER_LIST_RE.search(_norm(path))
        if not match or _norm(path)[:match.start()] not in roots or not os.path.isfile(path):
            continue
        repository = _archive(_plist_file(path).get('snapchatter_repository'))
        entries = repository.get('FRIENDS') if repository else None
        if isinstance(entries, list):
            friends = {}
            for entry in entries:
                if isinstance(entry, dict) and isinstance(entry.get('USER_ID'), str):
                    mutual = entry.get('IS_MUTUAL_FRIEND')
                    friends[entry['USER_ID']] = '' if mutual is None else _yes_no(mutual)
            add(match.group('user'), friends, path, 'snapchatter_repository')

    for group_plist in roots.values():
        values = _plist_file(group_plist)
        account = _archive(values.get('user'))
        if account and isinstance(account.get('keyed_friends_array'), list):
            friends = {}
            for section in account['keyed_friends_array']:
                for entry in (section.get('friends') if isinstance(section, dict) else None) or []:
                    if isinstance(entry, dict) and isinstance(entry.get('userId'), str):
                        friends[entry['userId']] = ''
            add(account.get('userId'), friends, group_plist, 'keyed_friends_array')
        shared = _archive(values.get('share_user'))
        if shared and isinstance(shared.get('SECTIONS'), list):
            friends = {}
            for section in shared['SECTIONS']:
                for entry in (section.get('DESTINATIONS') if isinstance(section, dict) else None) or []:
                    if not isinstance(entry, dict) or entry.get('CODED_SUBTYPE') != 'SUBTYPE_FRIEND':
                        continue
                    bitmoji = entry.get('FRIEND_BITMOJI_INFO')
                    user_id = bitmoji.get('USER_ID') if isinstance(bitmoji, dict) else None
                    if isinstance(user_id, str):
                        friends[user_id] = ''
            add(shared.get('USER_ID'), friends, group_plist, 'share_user')
    return lists, sources


# --- user.plist (TSAF) ----------------------------------------------------------------------

def _tsaf_tokens(path):
    '''The length-delimited strings of a TSAF file, in order; [] when not TSAF.'''
    if not path:
        return []
    try:
        with open(path, 'rb') as handle:
            data = handle.read()
    except OSError:
        return []
    if not data.startswith(_TSAF_MAGIC):
        return []
    return [token.decode('utf-8', 'replace')
            for token in re.findall(rb'\x08([^\x00]+)\x00', data)]


def _tsaf_value(tokens, key):
    '''The string following the key token, or ''.'''
    for position, token in enumerate(tokens):
        if token == key and position + 1 < len(tokens):
            return tokens[position + 1]
    return ''


def _local_user_id(user_plist_path, arroyo_path):
    '''The signed-in account's user id, or '' when it cannot be established.

    Preferred source is user_id in the app's Documents/user.plist. Failing that, the single
    distinct sender of rows where local_message_content_id is set, which the arroyo.db
    schema comments describe as nullable if the message was not created on this device.
    '''
    user_id = _tsaf_value(_tsaf_tokens(user_plist_path), 'user_id')
    if user_id and _UUID_RE.match(user_id):
        return user_id
    senders = {row[0] for row in _rows(
        arroyo_path,
        'SELECT DISTINCT sender_id FROM conversation_message '
        'WHERE local_message_content_id IS NOT NULL') if row[0]}
    return senders.pop() if len(senders) == 1 else ''


# --- arroyo.db protobuf helpers -------------------------------------------------------------

def _pb_get(node, key):
    '''Read one field out of a blackboxprotobuf dict.

    blackboxprotobuf splits a field whose repeats decode to different typedefs into
    'N-1', 'N-2' keys, so fall back to the first such variant when the plain key is absent.
    '''
    if not isinstance(node, dict):
        return None
    if key in node:
        return node[key]
    for name in sorted(node):
        if name.startswith(f'{key}-'):
            return node[name]
    return None


def _pb_walk(node, *path):
    '''Walk a blackboxprotobuf dict, taking the first element of any repeated field.'''
    current = node
    for key in path:
        if isinstance(current, list):
            current = current[0] if current else None
        current = _pb_get(current, key)
    if isinstance(current, list):
        current = current[0] if current else None
    return current


def _pb_text(node, *path):
    value = _pb_walk(node, *path)
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).decode('utf-8', 'replace')
    if isinstance(value, str):
        return value
    return ''


def _uuid_from_bytes(value):
    '''Format a 16-byte protobuf value as a canonical UUID string.'''
    if not isinstance(value, (bytes, bytearray)) or len(value) != 16:
        return ''
    digits = bytes(value).hex()
    return (f'{digits[0:8]}-{digits[8:12]}-{digits[12:16]}-'
            f'{digits[16:20]}-{digits[20:32]}')


def _decode(blob):
    if not blob:
        return None
    try:
        values, _typedef = blackboxprotobuf.decode_message(bytes(blob))
    except _PB_ERRORS:
        return None
    return values if isinstance(values, dict) else None


def _participants(arroyo_path, friends, reader=_rows):
    '''Map client_conversation_id to (participant ids, participant usernames).'''
    participants = {}
    for conversation_id, blob in reader(
            arroyo_path, 'SELECT client_conversation_id, conversation_metadata FROM conversation'):
        entries = _pb_get(_decode(blob), '3')
        if isinstance(entries, dict):
            entries = [entries]
        ids = []
        for entry in entries if isinstance(entries, list) else []:
            user_id = _uuid_from_bytes(_pb_walk(entry, '1', '1'))
            if user_id and user_id not in ids:
                ids.append(user_id)
        names = [_friend_name(friends, user_id) or user_id for user_id in ids]
        participants[conversation_id] = (', '.join(ids), ', '.join(names))
    return participants


def _yes_no(value):
    return 'YES' if value else 'NO'


def _log_wal_extent(files_found):
    '''Log how much write-ahead log this artifact leaves unparsed, per image.

    Reads the WAL header and the 24-byte frame headers only; no page images are loaded.
    A frame whose salt pair does not match the WAL header belongs to a previous log
    generation that the current one has cycled past, so it holds older content still on
    disk. Reporting both counts gives the examiner the size of what is not covered here.
    '''
    wal_path = _find(files_found, 'arroyo.db-wal')
    if not wal_path:
        return
    try:
        with open(wal_path, 'rb') as handle:
            header = handle.read(32)
            if len(header) < 32:
                return
            magic = struct.unpack('>I', header[:4])[0]
            page_size = struct.unpack('>I', header[8:12])[0]
            if magic not in (0x377F0682, 0x377F0683) or page_size < 512:
                return
            salts = struct.unpack('>2I', header[16:24])
            frame_size = 24 + page_size
            total = max(0, (os.path.getsize(wal_path) - 32) // frame_size)
            current = 0
            for index in range(total):
                handle.seek(32 + index * frame_size)
                frame_header = handle.read(24)
                if len(frame_header) < 24:
                    total = index
                    break
                if struct.unpack('>2I', frame_header[8:16]) == salts:
                    current += 1
    except (OSError, struct.error, ValueError):
        return
    logfunc(f'Snapchat arroyo.db-wal holds {total} frames of {page_size} bytes '
            f'({current} in the current log generation, {total - current} from previous '
            f'generations). This artifact does not parse WAL frames, so records held only in '
            f'them are not reported and absence of a message from the Snapchat arroyo.db '
            f'artifacts is not evidence that it did not exist.')


_MESSAGE_COLUMNS = ('creation_timestamp', 'read_timestamp', 'sender_id', 'content_type',
                    'message_content', 'message_state_type', 'is_saved', 'is_viewed_by_user',
                    'remote_media_count', 'quoted_server_message_id',
                    'client_conversation_id', 'client_message_id', 'server_message_id')


def _message_sql(source_path):
    return _tolerant_select(source_path, 'conversation_message', _MESSAGE_COLUMNS,
                            'ORDER BY creation_timestamp')


# conversation_message key (client_conversation_id, client_message_id), as offsets into
# _MESSAGE_COLUMNS.
_MESSAGE_KEY = (10, 11)

_MESSAGE_HEADERS = (('Creation Timestamp', 'datetime'), ('Read Timestamp', 'datetime'),
                    'Message Direction', 'Sender Username', 'Message Text',
                    ('Media', 'media'), 'Record Origin',
                    'Sender Display Name', 'Sender ID',
                    'Conversation Participants', 'Content Type (as stored)',
                    'Message State Type', 'Is Saved', 'Is Viewed By User',
                    'Remote Media Count', 'Quoted Server Message ID',
                    'Conversation ID', 'Client Message ID', 'Server Message ID',
                    'Recovery Method', 'Recovery Location')

_CONVERSATION_HEADERS = (('Creation Timestamp', 'datetime'), ('Last Updated Timestamp', 'datetime'),
                         ('Display Timestamp', 'datetime'), ('Tombstoned At Timestamp', 'datetime'),
                         ('Streak Expiration Timestamp', 'datetime'),
                         'Record Origin',
                         'Conversation Title',
                         'Participants', 'Participant IDs', 'Message Count', 'Streak Count',
                         'Conversation Type (as stored)', 'Send State Type', 'Feed Item Creator',
                         'Feed Item Creator ID', 'Last Chat Sender', 'Last Chat Sender ID',
                         'Tombstoned', 'Conversation ID',
                         'Recovery Method', 'Recovery Location')

# Provenance vocabulary. Record Origin is a closed two-value set so a viewer can branch on
# it; Recovery Method names the technique and is empty on live rows; Recovery Location says
# where in the evidence the row came from. Keep these strings stable, they are read by
# people and may be read by LAVA.
_ORIGIN_LIVE = 'Live'
_ORIGIN_RECOVERED = 'Recovered'
_METHOD_WAL_DIFF = 'WAL diff'


def _provenance(source_path, origin):
    '''The three provenance values for a row, as (origin, method, location).'''
    if origin == _ORIGIN_LIVE:
        return (_ORIGIN_LIVE, '', '')
    name = os.path.basename(source_path) if source_path else 'database'
    return (_ORIGIN_RECOVERED, _METHOD_WAL_DIFF, f'{name} (pre-checkpoint)')


def _by_creation(row):
    '''Sort key on the first column, tolerating rows whose timestamp is blank.

    The blank flag comes first so a datetime is never compared against a string.
    '''
    return (row[0] == '', row[0])


def _message_rows(rows, friends, participants, local_user_id, provenance, media):
    '''Report rows for conversation_message rows; media(conversation, client id, server id)
    returns the media references linked to a message.'''
    origin, method, location = provenance
    data_list = []
    for row in rows:
        (created, read, sender_id, content_type, blob, state, saved, viewed,
         media_count, quoted_id, conversation_id, client_message_id, server_message_id) = row
        text = _pb_text(_decode(blob), '4', '4', '2', '1') if content_type == 1 else ''
        if not local_user_id or not sender_id:
            direction = ''
        else:
            direction = 'Outgoing' if sender_id == local_user_id else 'Incoming'
        references = media(conversation_id, client_message_id, server_message_id)
        data_list.append((
            _ms_to_utc(created), _ms_to_utc(read),
            direction, _friend_name(friends, sender_id), text, references or '', origin,
            _friend_name(friends, sender_id, 1), sender_id,
            participants.get(conversation_id, ('', ''))[1], content_type,
            state, _yes_no(saved), _yes_no(viewed), media_count, quoted_id,
            conversation_id, client_message_id, server_message_id, method, location))
    return data_list


def _conversation_rows(source_path, friends, reader, provenance, only_ids=None):
    participants = _participants(source_path, friends, reader)
    conversations = {row[0]: row[1:] for row in reader(source_path, '''
        SELECT client_conversation_id, creation_timestamp, tombstoned_at_timestamp,
               send_state_type
        FROM conversation
    ''')}
    feeds = {row[0]: row[1:] for row in reader(source_path, _tolerant_select(
        source_path, 'feed_entry',
        ('client_conversation_id', 'last_updated_timestamp', 'display_timestamp',
         'streak_expiration_timestamp_ms', 'conversation_title', 'conversation_type',
         'streak_count', 'feedItemCreator', 'last_chat_sender', 'tombstoned')))}
    counts = dict(reader(source_path, '''
        SELECT client_conversation_id, COUNT(*) FROM conversation_message
        GROUP BY client_conversation_id
    '''))

    origin, method, location = provenance
    wanted = set(conversations) | set(feeds)
    if only_ids is not None:
        wanted &= set(only_ids)

    data_list = []
    for conversation_id in sorted(wanted):
        created, tombstoned_at, send_state = conversations.get(conversation_id, (None, None, ''))
        (updated, displayed, streak_expiry, title, conversation_type, streak, creator,
         last_sender, tombstoned) = feeds.get(conversation_id, (None,) * 9)
        data_list.append((
            _ms_to_utc(created), _ms_to_utc(updated), _ms_to_utc(displayed),
            _ms_to_utc(tombstoned_at), _ms_to_utc(streak_expiry), origin, title,
            participants.get(conversation_id, ('', ''))[1],
            participants.get(conversation_id, ('', ''))[0],
            counts.get(conversation_id, 0), streak, conversation_type, send_state,
            _friend_name(friends, creator), creator,
            _friend_name(friends, last_sender), last_sender,
            _yes_no(tombstoned), conversation_id, method, location))
    return data_list


def _superseded_conversation_ids(source_path):
    '''client_conversation_id values that the WAL removes from conversation or feed_entry.'''
    pre, committed = set(), set()
    for sql in ('SELECT client_conversation_id FROM conversation',
                'SELECT client_conversation_id FROM feed_entry'):
        pre |= {row[0] for row in _rows_pre_wal(source_path, sql)}
        committed |= {row[0] for row in _rows(source_path, sql)}
    return pre - committed


@artifact_processor
def snapchatMessages(context):
    '''Live conversation_message rows, plus rows the write-ahead log removes.

    Both sets are in one table so the recovered rows sit in chronological context. They are
    disjoint by construction: _superseded only returns keys absent from the live read.
    '''
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    media_lookup = _chat_media_lookup(files_found)
    for arroyo_path in sorted({str(f) for f in files_found if str(f).endswith('arroyo.db')}):
        source_path = source_path or arroyo_path
        doc_store = _find_sibling(files_found, arroyo_path, 'primary.docobjects')
        user_plist = _find_sibling(files_found, arroyo_path, 'user.plist')
        friends = _friend_records(doc_store)
        local_user_id = _local_user_id(user_plist, arroyo_path)
        message_sql = _message_sql(arroyo_path)
        container = _app_container(arroyo_path)

        def media(conversation_id, client_id, server_id, container=container):
            conversation = str(conversation_id or '').lower()
            references = list(media_lookup.get(
                (container, conversation, 'server', str(server_id)), []))
            for reference in media_lookup.get(
                    (container, conversation, 'client', str(client_id)), []):
                if reference not in references:
                    references.append(reference)
            return references

        data_list += _message_rows(
            _rows(arroyo_path, message_sql), friends, _participants(arroyo_path, friends),
            local_user_id, _provenance(arroyo_path, _ORIGIN_LIVE), media)
        data_list += _message_rows(
            _superseded(arroyo_path, message_sql, _MESSAGE_KEY), friends,
            _participants(arroyo_path, friends, _rows_pre_wal), local_user_id,
            _provenance(arroyo_path, _ORIGIN_RECOVERED), media)
    _log_wal_extent(files_found)
    data_list.sort(key=_by_creation)
    return _MESSAGE_HEADERS, data_list, source_path


@artifact_processor
def snapchatConversations(context):
    '''Live conversation and feed_entry rows, plus rows the write-ahead log removes.'''
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for arroyo_path in sorted({str(f) for f in files_found if str(f).endswith('arroyo.db')}):
        source_path = source_path or arroyo_path
        doc_store = _find_sibling(files_found, arroyo_path, 'primary.docobjects')
        friends = _friend_records(doc_store)
        data_list += _conversation_rows(arroyo_path, friends, _rows,
                                        _provenance(arroyo_path, _ORIGIN_LIVE))
        data_list += _conversation_rows(arroyo_path, friends, _rows_pre_wal,
                                        _provenance(arroyo_path, _ORIGIN_RECOVERED),
                                        _superseded_conversation_ids(arroyo_path))
    data_list.sort(key=_by_creation)
    return _CONVERSATION_HEADERS, data_list, source_path


@artifact_processor
def snapchatFriends(context):
    files_found = context.get_files_found()
    data_list = []
    source_paths = set()
    lists, list_sources = _friends_lists(files_found)
    for doc_store in sorted({str(f) for f in files_found if _DOC_STORE_RE.search(_norm(f))}):
        source_paths.add(doc_store)
        sql = _snapchatter_sql(doc_store)
        if not sql:
            logfunc(f'No snapchatter table in {doc_store}; this store generation predates it.')
            continue
        account = _DOC_STORE_RE.search(_norm(doc_store)).group('account')
        friends = lists.get(account)
        if friends is None:
            logfunc('Snapchat: no friends list for this account was found in the Snapchat App '
                    'Group, so In Friends List is blank on its snapchatter rows.')
        else:
            source_paths.add(list_sources[account])
        for user_id, blob, username, mutable, legacy in _rows(doc_store, sql):
            if friends is None:
                in_list, mutual = '', ''
            else:
                in_list, mutual = _yes_no(user_id in friends), friends.get(user_id, '')
            data_list.append((username or '', _display_name(blob, user_id), in_list, mutual,
                              user_id, mutable or '', legacy or '',
                              context.get_relative_path(doc_store)))
    data_headers = ('Username', 'Display Name', 'In Friends List', 'Mutual Friend (as stored)',
                    'User ID', 'Mutable Username', 'Legacy Username', 'Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def snapchatGallerySearch(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for search_db in sorted({str(f) for f in files_found if str(f).endswith('search.sqlite3')}):
        source_path = source_path or search_db
        source_file = context.get_relative_path(search_db)
        concepts = {}
        for snap_id, concept, confidence in _rows(search_db, '''
                SELECT snap_id, concept, conf FROM snap_visual_tag_conf_table
                ORDER BY snap_id, conf DESC'''):
            if snap_id and concept:
                rounded = f'{confidence:.3f}' if isinstance(confidence, float) else confidence
                concepts.setdefault(snap_id, []).append(f'{concept} ({rounded})')
        for row in _rows(search_db, '''
                SELECT ids.snap_id, time_tags.time_tag, ids.language_id,
                       location_clusters.cluster_name, visual_clusters.cluster_name,
                       tags.c0time_tag, tags.c1location_tag, tags.c2visual_tag,
                       tags.c3meta_tag, captions.c0caption
                FROM snap_id_table AS ids
                LEFT JOIN snap_tag_table_content AS tags ON tags.docid = ids.rowid
                LEFT JOIN snap_description_table_content AS captions
                    ON captions.docid = ids.rowid
                LEFT JOIN snap_time_tag_table AS time_tags
                    ON time_tags.snap_id = ids.snap_id
                LEFT JOIN snap_location_tag_cluster_table AS location_clusters
                    ON location_clusters.snap_id = ids.snap_id
                LEFT JOIN snap_visual_tag_cluster_table AS visual_clusters
                    ON visual_clusters.snap_id = ids.snap_id'''):
            (snap_id, time_tag, language, location_cluster, visual_cluster,
             time_tags, location_tags, visual_tags, meta_tags, caption) = row
            data_list.append((
                time_tag, snap_id, location_tags, location_cluster, visual_tags,
                ', '.join(concepts.get(snap_id, [])), visual_cluster, meta_tags,
                time_tags, caption, language, source_file))
    data_headers = (('Time Tag', 'date'), 'Snap ID', 'Location Tags', 'Location Cluster',
                    'Visual Tags', 'Visual Concepts (confidence)', 'Visual Cluster',
                    'Meta Tags', 'Time Tags', 'Caption', 'Language', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def snapchatAccount(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for user_plist in sorted({str(f) for f in files_found if str(f).endswith('user.plist')}):
        tokens = _tsaf_tokens(user_plist)
        if not tokens:
            continue
        source_path = source_path or user_plist
        relative_path = context.get_relative_path(user_plist)
        for key in ('username', 'user_id', 'laguna_id'):
            value = _tsaf_value(tokens, key)
            if key in ('user_id', 'laguna_id') and value and not _UUID_RE.match(value):
                continue
            if value:
                data_list.append((key, value, relative_path))
        for key in ('identifier', 'encryption_key', 'initialization_vector'):
            value = _tsaf_value(tokens, key)
            if value:
                data_list.append((f'client_encryption {key}', value, relative_path))
    data_headers = ('Key', 'Value', 'Source File')
    return data_headers, data_list, source_path


# --- media sniffing and decryption ----------------------------------------------------------

# ISO base media brands that name audio or a still image. Every other brand is reported
# as MPEG-4 without claiming video, since brands such as isom and mp42 do not say whether
# a file holds a video track.
_ISO_AUDIO_BRANDS = ('M4A ', 'M4B ', 'M4P ')
_ISO_IMAGE_BRANDS = ('heic', 'heix', 'mif1', 'msf1', 'avif')
_PACK_HEADER = b'\x01\x00\x00\x00'


def _sniff(data):
    '''(format, extension) for the media formats this module renders, else None.'''
    if not data:
        return None
    if data[:3] == b'\xff\xd8\xff':
        return 'JPEG', 'jpg'
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return 'PNG', 'png'
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return 'WebP', 'webp'
    if data[:6] in (b'GIF87a', b'GIF89a'):
        return 'GIF', 'gif'
    if data[4:8] == b'ftyp':
        brand = data[8:12].decode('latin-1')
        if brand in _ISO_AUDIO_BRANDS:
            return f'MPEG-4 audio ({brand.strip()})', 'm4a'
        if brand in _ISO_IMAGE_BRANDS:
            return f'HEIF ({brand.strip()})', 'heic'
        if brand.startswith('qt'):
            return 'QuickTime', 'mov'
        return f'MPEG-4 ({brand.strip()})', 'mp4'
    return None


def _strip_pkcs7(data):
    '''data without its PKCS#7 padding, or unchanged when the tail is not valid padding.'''
    if data and 1 <= data[-1] <= 16 and data.endswith(bytes([data[-1]]) * data[-1]):
        return data[:-data[-1]]
    return data


def _unpad_exact(data, size):
    '''data with PKCS#7 padding removed when that leaves exactly size bytes, else b"".'''
    stripped = _strip_pkcs7(data)
    return stripped if len(stripped) == size and len(stripped) < len(data) else b''


def _aes_cbc(key, iv, data):
    '''AES-CBC decryption of the whole blocks of data, or b"" when that is not possible.'''
    usable = len(data) - len(data) % 16
    if not usable or len(key) != 32 or len(iv) != 16:
        return b''
    return AES.new(key, AES.MODE_CBC, iv).decrypt(data[:usable])


def _open_media(blob, key, iv):
    '''Decrypt one cached Memories blob with a snap's key.

    Returns (payload, declared length) when the plaintext is a recognised media format,
    else (b'', None). Two plaintext shapes occur: caching-media packs, and on the tested
    images the snap-rendered-lowres SCContent files, start with 01 00 00 00 and a
    little-endian payload length, so the payload is that many bytes after the 8-byte header;
    other SCContent files and the database thumbnails decrypt straight to the media followed
    by PKCS#7 padding, which is removed. A declared length larger than the bytes present
    means the item was only partly cached.
    '''
    plain = _aes_cbc(key, iv, blob)
    if plain[:4] == _PACK_HEADER:
        declared = int.from_bytes(plain[4:8], 'little')
        body = plain[8:8 + declared] if declared else plain[8:]
        if _sniff(body):
            return body, declared
    if _sniff(plain):
        return _strip_pkcs7(plain), None
    return b'', None


def _archive(blob):
    '''An NSKeyedArchiver property list as a dict, or None when it does not decode.'''
    if not isinstance(blob, (bytes, bytearray)) or not blob:
        return None
    try:
        values = nska_deserialize.deserialize_plist(io.BytesIO(bytes(blob)),
                                                    full_recurse_convert_nska=True,
                                                    format=dict)
    except _NSKA_ERRORS:
        return None
    return values if isinstance(values, dict) else None


def _read(path):
    with open(path, 'rb') as handle:
        return handle.read()


def _blank(value):
    return '' if value is None else value


# --- cache_controller.db and the SCContent cache folders ------------------------------------

_UUID_PATTERN = (r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-'
                 r'[0-9a-fA-F]{12}')
# A conversation media claim: an optional kind and a tilde, a number, the conversation id,
# the message's server_message_id, then further numbers (0:0 on every tested claim).
_CHAT_CLAIM_RE = re.compile(r'^(?:(?P<kind>[A-Za-z_]+)~)?\d+:(?P<conversation>'
                            + _UUID_PATTERN + r'):(?P<message>\d+)(?::\d+)*$')
_SCCONTENT_RE = re.compile(r'/Documents/com\.snap\.file_manager_[^/]*_SCContent_'
                           r'(?P<account>[^/]*)/(?P<name>[^/]+)$')
_PACK_RE = re.compile(r'/Library/Caches/caching-media/(?P<folder>[^/]+)/(?P<item>[^/]+)-'
                      r'(?P<number>\d+)\.pack$')
_SCDB_RE = re.compile(r'/Documents/gallery_data_object/[^/]+/(?P<profile>[^/]+)/'
                      r'scdb-27\.sqlite3$')
_GALLERY_RE = re.compile(r'/Documents/gallery_encrypted_db/[^/]+/(?P<profile>[^/]+)/'
                         r'gallery\.encrypteddb$')
_CLAIM_COLUMNS = ('USER_ID', 'CACHE_KEY', 'MEDIA_CONTEXT_TYPE', 'EXTERNAL_KEY',
                  'CREATION_TIMESTAMP_MILLIS', 'DELETED_TIMESTAMP_MILLIS')
_MEMORY_CLAIM_PREFIXES = ('snap-media-', 'snap-overlay-', 'snap-rendered-lowres-', 'g-media-')


def _norm(path):
    return str(path).replace('\\', '/')


def _sccontent_index(files_found):
    '''{(container, account, lower-case file name): path} for the SCContent cache folders.

    Each folder name ends with the account's user id (one folder ends with nothing), and a
    cache_controller.db claim carries the same value as USER_ID, so a claim resolves to its
    own account's folder in its own container.
    '''
    index = {}
    for file_found in files_found:
        path = str(file_found)
        match = _SCCONTENT_RE.search(_norm(path))
        if match and os.path.isfile(path):
            index[(_app_container(path), match.group('account'),
                   match.group('name').lower())] = path
    return index


def _claims(cache_db):
    '''CACHE_FILE_CLAIM rows as dicts, with None for columns an older schema lacks.'''
    return [dict(zip(_CLAIM_COLUMNS, row)) for row in _rows(
        cache_db, _tolerant_select(cache_db, 'CACHE_FILE_CLAIM', _CLAIM_COLUMNS))]


def _claim_file(index, container, claim):
    '''The staged SCContent file a claim names, or "" when it is not in the extraction.'''
    return index.get((container, claim['USER_ID'] or '', (claim['CACHE_KEY'] or '').lower()),
                     '')


def _file_state(path):
    '''(format, extension, size) of a staged file; format and extension are '' when unknown.'''
    size = os.path.getsize(path)
    with open(path, 'rb') as handle:
        sniffed = _sniff(handle.read(64))
    return (sniffed[0], sniffed[1], size) if sniffed else ('', '', size)


# --- conversation media ---------------------------------------------------------------------

_LINK_CLAIM = 'cache_controller.db EXTERNAL_KEY'
_LINK_LOCAL = 'local_message_references MEDIA_ID'


def _local_reference_media_id(blob):
    '''MEDIA_ID from a conversation_message.local_message_references value, or "".

    On every tested image the value was 8 bytes followed by an NSKeyedArchiver property
    list; the archive is located by its magic rather than by that offset.
    '''
    if not isinstance(blob, (bytes, bytearray)):
        return ''
    start = bytes(blob).find(b'bplist00')
    values = _archive(bytes(blob)[start:]) if start != -1 else None
    media_id = values.get('MEDIA_ID') if values else None
    return media_id if isinstance(media_id, str) else ''


def _chat_media_entries(files_found):
    '''Conversation media cache entries for the app containers that hold arroyo.db.

    Two recorded links tie a cache entry to a message: a claim whose EXTERNAL_KEY names the
    conversation and the message's server_message_id, and a message whose own
    local_message_references MEDIA_ID equals a claim's EXTERNAL_KEY. A container without
    arroyo.db is skipped, since cache_controller.db alone does not show the container
    belongs to Snapchat.
    '''
    index = _sccontent_index(files_found)
    arroyo_by_container = {}
    for file_found in files_found:
        if str(file_found).endswith('arroyo.db'):
            arroyo_by_container.setdefault(_app_container(file_found), []).append(
                str(file_found))
    entries = []
    for cache_db in sorted({str(f) for f in files_found
                            if str(f).endswith('cache_controller.db')}):
        container = _app_container(cache_db)
        arroyo_paths = arroyo_by_container.get(container)
        if not arroyo_paths:
            continue
        by_external_key = {}
        for claim in _claims(cache_db):
            by_external_key.setdefault(claim['EXTERNAL_KEY'], []).append(claim)
            match = _CHAT_CLAIM_RE.match(claim['EXTERNAL_KEY'] or '')
            if match:
                entries.append({
                    'container': container,
                    'conversation': match.group('conversation').lower(),
                    'server_id': match.group('message'), 'client_id': '',
                    'kind': match.group('kind') or '', 'link': _LINK_CLAIM, 'claim': claim,
                    'path': _claim_file(index, container, claim), 'cache_db': cache_db})
        for arroyo_path in arroyo_paths:
            if 'local_message_references' not in _table_columns(arroyo_path,
                                                                 'conversation_message'):
                continue
            for conversation_id, client_id, server_id, blob in _rows(arroyo_path, '''
                    SELECT client_conversation_id, client_message_id, server_message_id,
                           local_message_references
                    FROM conversation_message WHERE local_message_references IS NOT NULL'''):
                media_id = _local_reference_media_id(blob)
                for claim in by_external_key.get(media_id, []) if media_id else []:
                    entries.append({
                        'container': container,
                        'conversation': str(conversation_id or '').lower(),
                        'server_id': '' if server_id is None else str(server_id),
                        'client_id': '' if client_id is None else str(client_id),
                        'kind': '', 'link': _LINK_LOCAL, 'claim': claim,
                        'path': _claim_file(index, container, claim), 'cache_db': cache_db})
    return entries


def _check_in_chat_file(entry, checked_in):
    '''Media reference for an entry's file when it is a recognised media format, else None.'''
    path = entry['path']
    if not path:
        return None
    if path not in checked_in:
        media_format, extension, size = _file_state(path)
        checked_in[path] = check_in_media(
            path, name=f'{os.path.basename(path)}.{extension}',
            force_extension=extension) if media_format and size else None
    return checked_in[path]


def _chat_media_lookup(files_found):
    '''{(container, conversation, 'server' or 'client', id): [media refs]} for Messages.'''
    lookup = {}
    checked_in = {}
    for entry in _chat_media_entries(files_found):
        reference = _check_in_chat_file(entry, checked_in)
        if not reference:
            continue
        if entry['link'] == _LINK_LOCAL:
            key = (entry['container'], entry['conversation'], 'client', entry['client_id'])
        else:
            key = (entry['container'], entry['conversation'], 'server', entry['server_id'])
        references = lookup.setdefault(key, [])
        if reference not in references:
            references.append(reference)
    return lookup


# --- Memories -------------------------------------------------------------------------------

_COCOA_EPOCH_OFFSET = 978307200
_SNAPCHAT_ACCESS_GROUP = 'com.toyopagroup.picaboo'
_EGOCIPHER_ACCOUNT = 'egocipher.key.avoidkeyderivation'
_PERSISTED_KEY_ACCOUNT = 'com.snapchat.keyservice.persistedkey'
_SNAP_COLUMNS = ('Z_PK', 'ZSNAPID', 'ZMEDIAID', 'ZCREATETIMEUTC', 'ZCAPTURETIMEUTC',
                 'ZTIMEZONENAME', 'ZSERVLETMEDIAFORMAT', 'ZWIDTH', 'ZHEIGHT', 'ZDURATION',
                 'ZCAMERAFRONTFACING', 'ZCAMERAROLLID', 'ZDUPLICATEDFROMSNAPID', 'ZENTRY',
                 'ZENCRYPTION')
_SOURCE_SCCONTENT = 'SCContent cache'
_SOURCE_PACKS = 'caching-media cache'
_SOURCE_THUMBNAIL = 'Memories database'
_METHOD_KEY_ONLY = 'Key row with no Memory row'
# What a recovered file is, from the claim role or table that led to it. The Memories table
# shows the best of media, preview and thumbnail, with any overlay beside it.
_KIND_OF_ROLE = {'snap-media': 'media', 'g-media': 'media', 'snap-overlay': 'overlay',
                 'snap-rendered-lowres': 'preview', 'caching-media': 'preview',
                 'ZGALLERYSNAPMINITHUMBNAIL': 'thumbnail'}
_KIND_RANK = {'media': 0, 'preview': 1, 'thumbnail': 2}


def _cocoa_to_utc(value):
    if value in (None, ''):
        return ''
    try:
        return datetime.datetime.fromtimestamp(float(value) + _COCOA_EPOCH_OFFSET,
                                               datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _keychain_secrets(account):
    path = active_keychain_path()
    return find_keychain_secrets(path, _SNAPCHAT_ACCESS_GROUP, account) if path else []


def _egocipher():
    '''The 32-byte key of gallery.encrypteddb from the keychain, or None.'''
    secrets = [secret for secret in _keychain_secrets(_EGOCIPHER_ACCOUNT) if len(secret) == 32]
    return secrets[0] if secrets else None


def _persisted_master_keys():
    '''(key, iv) of every com.snapchat.keyservice.persistedkey item in the keychain.'''
    masters = []
    for secret in _keychain_secrets(_PERSISTED_KEY_ACCOUNT):
        values = _archive(secret)
        key = values.get('masterKey') if values else None
        iv = values.get('initializationVector') if values else None
        if isinstance(key, bytes) and isinstance(iv, bytes) and len(key) == 32 \
                and len(iv) == 16:
            masters.append((key, iv))
    return masters


def _unwrap(key, iv, masters):
    '''The usable key and IV behind a wrapped 48-byte key and 32-byte IV, or None.

    The wrapped values are a 32-byte key and a 16-byte IV encrypted with AES-CBC and
    PKCS#7 padding under a master key, so only the right master key leaves exactly one
    block of valid padding on both.
    '''
    for master_key, master_iv in masters:
        inner_key = _unpad_exact(_aes_cbc(master_key, master_iv, key), 32)
        inner_iv = _unpad_exact(_aes_cbc(master_key, master_iv, iv), 16)
        if inner_key and inner_iv:
            return inner_key, inner_iv
    return None


def _gallery_rows(gallery_path, egocipher):
    '''(keys, locations, addresses, status) from one gallery.encrypteddb.

    The database is SQLCipher keyed with the raw egocipher key, SQLCipher 3 settings
    (1,024-byte pages, HMAC-SHA1), and its rows live in the write-ahead log, which is
    replayed. The plaintext copy is written to a temporary directory that is removed
    before this returns.
    '''
    keys, locations, addresses = {}, {}, {}
    with tempfile.TemporaryDirectory(prefix='ileapp_snapchat_') as work:
        plain_path = os.path.join(work, 'gallery.sqlite')
        try:
            pages, verified = decrypt_sqlcipher_db(
                gallery_path, egocipher, plain_path, page_size=1024, raw_key=True,
                hmac_algorithm='sha1', kdf_algorithm='sha1', apply_wal=True)
        except (OSError, ValueError, KeyError) as error:
            return keys, locations, addresses, f'not decrypted ({error})'
        if not pages or not verified:
            return keys, locations, addresses, ('not decrypted (the keychain egocipher '
                                                'did not authenticate it)')
        # Snapchat's SQLCipher build names its automatic indexes sqlcph_autoindex_*. Stock
        # SQLite accepts only sqlite_autoindex_* for an index stored without SQL and
        # refuses the whole schema as an "orphan index". Both names are the same length,
        # so renaming them in the plaintext copy changes nothing else in the file.
        with open(plain_path, 'r+b') as handle:
            data = handle.read()
            handle.seek(0)
            handle.write(data.replace(b'sqlcph_autoindex_', b'sqlite_autoindex_'))
        for snap_id, key, iv, encrypted in _rows(
                plain_path, 'SELECT snap_id, key, iv, encrypted FROM snap_key_iv'):
            if snap_id and isinstance(key, bytes) and isinstance(iv, bytes):
                keys[snap_id] = (key, iv, encrypted)
        for snap_id, latitude, longitude in _rows(
                plain_path, 'SELECT snap_id, latitude, longitude FROM snap_location_table'):
            if snap_id:
                locations[snap_id] = (latitude, longitude)
        for snap_id, title in _rows(
                plain_path, 'SELECT snap_id, address_title FROM snap_address_title'):
            if snap_id and title:
                addresses[snap_id] = title
    status = 'decrypted' if verified == pages else (
        f'decrypted; {pages - verified} of {pages} pages failed authentication')
    return keys, locations, addresses, status


def _captions(blob):
    '''Caption text from a ZGALLERYSNAPDETAIL.ZOVERLAY archive, joined with " | ".'''
    values = _archive(blob)
    captions = values.get('captions') if values else None
    if not isinstance(captions, list):
        return ''
    return ' | '.join(caption['text'] for caption in captions
                      if isinstance(caption, dict) and isinstance(caption.get('text'), str)
                      and caption['text'])


def _memory_records(scdb_path, reader):
    '''{snap id: fields} for the ZGALLERYSNAP rows one view of scdb-27.sqlite3 returns.'''
    entries = {row[0]: row[1:] for row in reader(scdb_path, _tolerant_select(
        scdb_path, 'ZGALLERYENTRY', ('Z_PK', 'ZENTRYID', 'ZTITLE', 'ZISPRIVATE')))}
    captions = {row[0]: _captions(row[1]) for row in reader(scdb_path, _tolerant_select(
        scdb_path, 'ZGALLERYSNAPDETAIL', ('ZSNAP', 'ZOVERLAY')))}
    thumbnails = {row[0]: row[1] for row in reader(scdb_path, _tolerant_select(
        scdb_path, 'ZGALLERYSNAPMINITHUMBNAIL', ('ZSNAPID', 'ZTHUMBNAILDATA'))) if row[0]}
    records = {}
    for row in reader(scdb_path, _tolerant_select(scdb_path, 'ZGALLERYSNAP', _SNAP_COLUMNS)):
        fields = dict(zip(_SNAP_COLUMNS, row))
        snap_id = fields['ZSNAPID']
        if not snap_id:
            continue
        entry_id, title, private = entries.get(fields['ZENTRY'], (None, None, None))
        fields.update({'entry_id': entry_id or '', 'title': title or '',
                       'private': '' if private is None else ('Yes' if private else 'No'),
                       'caption': captions.get(fields['Z_PK'], ''),
                       'thumbnail': thumbnails.get(snap_id)})
        records[snap_id] = fields
    return records


def _snapchat_containers(files_found):
    '''{container: store paths} for app containers holding Snapchat's Memories store.'''
    containers = {}
    for file_found in files_found:
        path = str(file_found)
        normalized = _norm(path)
        match = _SCDB_RE.search(normalized) or _GALLERY_RE.search(normalized)
        if not match or not os.path.isfile(path):
            continue
        store = containers.setdefault(_app_container(path), {'profiles': {}, 'packs': {}})
        kind = 'scdb' if normalized.endswith('scdb-27.sqlite3') else 'gallery'
        store['profiles'].setdefault(match.group('profile'), {})[kind] = path
    for file_found in files_found:
        path = str(file_found)
        container = _app_container(path)
        if container not in containers or not os.path.isfile(path):
            continue
        normalized = _norm(path)
        if normalized.endswith('/Documents/global_scoped/cachecontroller/cache_controller.db'):
            containers[container]['cache_db'] = path
        elif normalized.endswith('/Documents/user.plist'):
            containers[container]['user_plist'] = path
        match = _PACK_RE.search(normalized)
        if match:
            containers[container]['packs'].setdefault(match.group('folder'), {}).setdefault(
                match.group('item'), {})[int(match.group('number'))] = path
    return containers


def _stored_pairs(encryption, gallery_key):
    '''Every raw (key, iv) pair stored for a snap: its ZENCRYPTION pair and its key row.'''
    pairs = []
    archive = _archive(encryption) if encryption else None
    if archive and isinstance(archive.get('KEY'), bytes) and isinstance(archive.get('IV'), bytes):
        pairs.append((archive['KEY'], archive['IV'], 'scdb-27 ZENCRYPTION'))
    if gallery_key:
        pairs.append((gallery_key[0], gallery_key[1], 'gallery.encrypteddb snap_key_iv'))
    return pairs


def _key_state(pairs, masters, gallery_status):
    '''(key, iv, key source) or (None, None, why there is no usable key).'''
    wrapped = False
    for key, iv, source in pairs:
        if len(key) == 32 and len(iv) == 16:
            return key, iv, source
        if len(key) == 48 and len(iv) == 32:
            wrapped = True
            unwrapped = _unwrap(key, iv, masters)
            if unwrapped:
                return (unwrapped[0], unwrapped[1],
                        f'{source}, unwrapped with the keychain persistedkey')
    if wrapped:
        return None, None, 'Wrapped key; no keychain persistedkey unwraps it'
    if gallery_status == 'decrypted':
        return None, None, 'No key: gallery.encrypteddb has no key row for this snap'
    return None, None, f'No key: gallery.encrypteddb {gallery_status}'


def _decrypted(blob, key, iv):
    '''(payload, declared length, plaintext file) for a cache blob, or (b"", None, False).'''
    if _sniff(blob):
        return blob, None, True
    if key:
        payload, declared = _open_media(blob, key, iv)
        return payload, declared, False
    return b'', None, False


def _media_record(snap_ids, source, linked_by, role, path, blob, key_info, cache_key,
                  shared=1, deleted=None):
    '''One Memories media file, recovered or not. key_info is (key, iv, key source).'''
    key, iv, key_source = key_info
    payload, declared, plaintext = _decrypted(blob, key, iv) if blob else (b'', None, False)
    sniffed = _sniff(payload) if payload else None
    if not path:
        state, complete = 'Not on disk', ''
    elif sniffed:
        state = 'On disk'
        # Only a .pack payload declares its length, so only a .pack file can be judged.
        complete = '' if declared is None else ('Yes' if len(payload) >= declared else (
            f'No: {len(payload):,} of {declared:,} bytes'))
    elif not key:
        state, complete = 'On disk, encrypted; no usable key', ''
    else:
        state, complete = 'On disk; did not decrypt to a recognised format', ''
    return {'snap_ids': list(snap_ids), 'source': source, 'linked_by': linked_by,
            'role': role, 'kind': _KIND_OF_ROLE.get(role, 'media'), 'path': path,
            'payload': payload if sniffed else b'', 'plaintext': plaintext,
            'format': sniffed[0] if sniffed else '', 'extension': sniffed[1] if sniffed else '',
            'size': len(payload) if sniffed else len(blob or b''), 'state': state,
            'complete': complete,
            'key_source': 'none needed (stored unencrypted)' if plaintext and sniffed else (
                key_source if sniffed else ''),
            'cache_key': cache_key, 'shared': shared, 'deleted': deleted}


def _memories_data(files_found):
    '''Memories rows and recovered media for every Snapchat container in files_found.

    Returns (memories, media, source_paths). A Memory is a ZGALLERYSNAP row from a normal
    read (Live) or present only before the write-ahead log is applied (Recovered), or a
    snap id holding a key row in gallery.encrypteddb with no Memory row in either read and
    no key shared with one (Recovered, key row only). Every snap is keyed by its profile
    folder as well as its id, so two accounts' stores in one container never merge.
    '''
    egocipher = _egocipher()
    masters = _persisted_master_keys()
    index = _sccontent_index(files_found)
    memories, media, source_paths = [], [], set()
    for container, store in sorted(_snapchat_containers(files_found).items()):
        user_id = _tsaf_value(_tsaf_tokens(store.get('user_plist')), 'user_id')
        snaps, usable, pair_of, addresses = {}, {}, {}, {}
        for profile, paths in sorted(store['profiles'].items()):
            gallery_keys, locations = {}, {}
            gallery_status = 'not in the extraction'
            if paths.get('gallery'):
                source_paths.add(paths['gallery'])
                if egocipher:
                    gallery_keys, locations, profile_addresses, gallery_status = \
                        _gallery_rows(paths['gallery'], egocipher)
                    addresses.update({(profile, snap_id): title
                                      for snap_id, title in profile_addresses.items()})
                elif active_keychain_path():
                    gallery_status = 'not decrypted (the keychain has no egocipher item)'
                else:
                    gallery_status = 'not decrypted (no keychain available)'
                logfunc(f'Snapchat Memories: gallery.encrypteddb {gallery_status}')
            live, recovered = {}, {}
            if paths.get('scdb'):
                source_paths.add(paths['scdb'])
                live = _memory_records(paths['scdb'], _rows)
                recovered = {snap_id: fields for snap_id, fields
                             in _memory_records(paths['scdb'], _rows_pre_wal).items()
                             if snap_id not in live}
            account = user_id if user_id and hashlib.sha256(
                user_id.encode('utf-8')).hexdigest() == profile else ''
            base = {'account': account, 'profile': profile, 'scdb': paths.get('scdb', ''),
                    'container': container}
            memory_pairs = set()
            for origin, records in ((_ORIGIN_LIVE, live), (_ORIGIN_RECOVERED, recovered)):
                for snap_id, fields in records.items():
                    snap_key = (profile, snap_id)
                    pairs = _stored_pairs(fields['ZENCRYPTION'], gallery_keys.get(snap_id))
                    memory_pairs.update((key, iv) for key, iv, _source in pairs)
                    pair_of[snap_key] = pairs[-1][:2] if pairs else None
                    key, iv, state = _key_state(pairs, masters, gallery_status)
                    if key:
                        usable[snap_key] = (key, iv, state)
                    snaps[snap_key] = dict(
                        base, snap_id=snap_id, origin=origin, fields=fields, key_state=state,
                        location=locations.get(snap_id, (None, None)),
                        method='' if origin == _ORIGIN_LIVE else _METHOD_WAL_DIFF,
                        recovery_location='' if origin == _ORIGIN_LIVE else
                        'scdb-27.sqlite3 (pre-checkpoint)')
            for snap_id, gallery_key in gallery_keys.items():
                snap_key = (profile, snap_id)
                if snap_key in snaps:
                    continue
                pairs = _stored_pairs(None, gallery_key)
                pair_of[snap_key] = pairs[0][:2]
                key, iv, state = _key_state(pairs, masters, gallery_status)
                if key:
                    usable[snap_key] = (key, iv, state)
                if pairs[0][:2] in memory_pairs:
                    # The same key as a Memory row: another id for that Memory's media.
                    continue
                snaps[snap_key] = dict(
                    base, snap_id=snap_id, origin=_ORIGIN_RECOVERED,
                    fields={'ZSNAPID': snap_id}, key_state=state,
                    location=locations.get(snap_id, (None, None)), method=_METHOD_KEY_ONLY,
                    recovery_location='gallery.encrypteddb')
        groups = {}
        for snap_key, pair in pair_of.items():
            if pair:
                groups.setdefault(pair, []).append(snap_key)
        container_media = _container_media(container, store, snaps, usable, pair_of, groups,
                                           index, source_paths)
        media.extend(container_media)
        for snap_key, snap in snaps.items():
            snap['key'] = snap_key
            snap['media'] = [record for record in container_media
                             if snap_key in record['snap_ids'] and record['payload']]
            # An address title can sit on a snap id that shares the Memory's key.
            snap['address'] = addresses.get(snap_key) or next(
                (addresses[other] for other in groups.get(pair_of.get(snap_key), [])
                 if addresses.get(other)), '')
            memories.append(snap)
    return memories, media, source_paths


def _container_media(container, store, snaps, usable, pair_of, groups, index, source_paths):
    '''Every Memories media file found for one container: SCContent, packs, thumbnails.'''
    records = []
    record_of_path = {}
    claims_by_id = {}
    if store.get('cache_db'):
        source_paths.add(store['cache_db'])
        for claim in _claims(store['cache_db']):
            external_key = claim['EXTERNAL_KEY'] or ''
            for prefix in _MEMORY_CLAIM_PREFIXES:
                if external_key.startswith(prefix):
                    claims_by_id.setdefault(external_key[len(prefix):], []).append(
                        (prefix.rstrip('-'), claim))

    def shared_with(snap_key):
        return len(groups.get(pair_of.get(snap_key), [snap_key]))

    for snap_key, snap in snaps.items():
        key_info = usable.get(snap_key, (None, None, ''))
        fields = snap['fields']
        references = [snap['snap_id']]
        if fields.get('ZMEDIAID') and fields['ZMEDIAID'] != snap['snap_id']:
            references.append(fields['ZMEDIAID'])
        for reference in references:
            for role, claim in claims_by_id.get(reference, []):
                path = _claim_file(index, container, claim)
                if path and path in record_of_path:
                    # Another Memory naming the same file, such as a duplicated Memory
                    # that keeps the original's media id.
                    if snap_key not in record_of_path[path]['snap_ids']:
                        record_of_path[path]['snap_ids'].append(snap_key)
                    continue
                if path:
                    source_paths.add(path)
                record = _media_record(
                    [snap_key], _SOURCE_SCCONTENT, f'cache_controller.db claim {role}-<id>',
                    role, path, _read(path) if path else b'', key_info,
                    claim['CACHE_KEY'] or '', shared_with(snap_key),
                    claim['DELETED_TIMESTAMP_MILLIS'])
                if path:
                    record_of_path[path] = record
                records.append(record)
        if fields.get('thumbnail') and key_info[0]:
            records.append(_media_record(
                [snap_key], _SOURCE_THUMBNAIL, 'ZGALLERYSNAPMINITHUMBNAIL row',
                'ZGALLERYSNAPMINITHUMBNAIL', snap['scdb'], bytes(fields['thumbnail']),
                key_info, snap['snap_id'], shared_with(snap_key)))
    records.extend(_pack_media(store, snaps, usable, pair_of, groups, source_paths))
    return records


def _pack_opener(path, pairs):
    '''(key, iv, key source, snap ids) of the key that opens one .pack file, or None.'''
    with open(path, 'rb') as handle:
        head = handle.read(32)
    for (key, iv), (key_source, snap_ids) in pairs.items():
        plain = _aes_cbc(key, iv, head)
        if plain[:4] == _PACK_HEADER and _sniff(plain[8:]):
            return key, iv, key_source, snap_ids
    return None


def _pack_media(store, snaps, usable, pair_of, groups, source_paths):
    '''Media from Library/Caches/caching-media, linked by the key that opens each file.

    File and folder names are opaque. Every .pack file is its own encrypted payload: on the
    tested images each one, whatever its numeric suffix, began with the pack header under a
    snap's key and held its full declared length. So the first block of each file is
    test-decrypted with every usable key, and the key whose output starts with the pack
    header and a media signature identifies the Memories media the file holds. Several snap
    ids can share one key, and every one that has a Memory row is listed.
    '''
    records = []
    pairs = {}
    for snap_id, (key, iv, key_source) in usable.items():
        pairs.setdefault((key, iv), (key_source, []))[1].append(snap_id)
    for folder, items in sorted(store.get('packs', {}).items()):
        unopened = []
        for item, files in sorted(items.items()):
            for number, path in sorted(files.items()):
                source_paths.add(path)
                opener = _pack_opener(path, pairs)
                if not opener:
                    unopened.append(path)
                    continue
                key, iv, key_source, snap_ids = opener
                listed = sorted(snap_key for snap_key in snap_ids if snap_key in snaps) or \
                    sorted(snap_ids)
                shared = len(groups.get(pair_of.get(listed[0]), listed))
                records.append(_media_record(
                    listed, _SOURCE_PACKS, 'key opened the file', 'caching-media', path,
                    _read(path), (key, iv, key_source), f'{folder}/{item}-{number}.pack',
                    shared))
        if unopened:
            record = _media_record([], _SOURCE_PACKS, '', 'caching-media', unopened[0], b'',
                                   (None, None, ''), folder)
            record['size'] = sum(os.path.getsize(path) for path in unopened)
            record['state'] = (f'On disk, encrypted; no available key opened '
                               f'{len(unopened)} file{"" if len(unopened) == 1 else "s"} '
                               f'in this folder')
            records.append(record)
    return records


def _media_reference(record, cache):
    '''Check one recovered Memories file in, once per artifact run; returns the media ref.'''
    identity = (record['path'], record['cache_key'], record['role'])
    if identity not in cache:
        name = f"{record['cache_key'].replace('/', '_') or 'memory'}.{record['extension']}"
        if record['plaintext']:
            cache[identity] = check_in_media(record['path'], name=name,
                                             force_extension=record['extension'])
        else:
            cache[identity] = check_in_embedded_media(record['path'], record['payload'],
                                                      name=name,
                                                      force_extension=record['extension'])
    return cache[identity]


def _summary(records):
    '''Short list of the media recovered for one Memory.'''
    parts = []
    for record in sorted(records, key=lambda r: (_KIND_RANK.get(r['kind'], 3), r['role'])):
        part = f"{record['kind']}: {record['role']} ({record['format']})"
        if record['complete'].startswith('No'):
            part += ', partly cached'
        parts.append(part)
    return '; '.join(parts)


_MEMORY_HEADERS = (('Created', 'datetime'), ('Captured', 'datetime'),
                   'Capture Time Zone (as stored)', ('Media', 'media'), 'Record Origin',
                   'Caption', 'Latitude', 'Longitude', 'Address Title',
                   'Private Entry (as stored)', 'Key State', 'Recovered Media',
                   'Media Format (as stored)', 'Width', 'Height', 'Duration (as stored)',
                   'Front Camera (as stored)', 'Camera Roll ID (as stored)', 'Entry Title',
                   'Duplicated From Snap ID', 'Snap ID', 'Media ID', 'Entry ID',
                   'Account User ID', 'Profile Folder', 'Recovery Method',
                   'Recovery Location')

_MEMORY_MEDIA_HEADERS = (('Memory Created', 'datetime'), ('Cache Entry Deleted', 'datetime'),
                         ('Media', 'media'), 'Snap IDs',
                         'Record Origin', 'Source', 'Linked By', 'Role',
                         'Kind', 'File', 'Format', 'Size (bytes)', 'Complete', 'Key Source',
                         'Snap IDs Sharing The Key', 'Cache Key', 'Source File')


@artifact_processor
def snapchatMemories(context):
    memories, _media, source_paths = _memories_data(context.get_files_found())
    cache = {}
    data_list = []
    for snap in memories:
        fields = snap['fields']
        shown = sorted((record for record in snap['media'] if record['kind'] != 'overlay'),
                       key=lambda record: (_KIND_RANK.get(record['kind'], 3), -record['size']))
        overlays = [record for record in snap['media'] if record['kind'] == 'overlay']
        references = [_media_reference(record, cache) for record in shown[:1] + overlays[:1]]
        latitude, longitude = snap['location']
        data_list.append((
            _cocoa_to_utc(fields.get('ZCREATETIMEUTC')),
            _cocoa_to_utc(fields.get('ZCAPTURETIMEUTC')), _blank(fields.get('ZTIMEZONENAME')),
            [reference for reference in references if reference] or '', snap['origin'],
            fields.get('caption', ''), _blank(latitude), _blank(longitude), snap['address'],
            fields.get('private', ''), snap['key_state'], _summary(snap['media']),
            _blank(fields.get('ZSERVLETMEDIAFORMAT')), _blank(fields.get('ZWIDTH')),
            _blank(fields.get('ZHEIGHT')), _blank(fields.get('ZDURATION')),
            _blank(fields.get('ZCAMERAFRONTFACING')), _blank(fields.get('ZCAMERAROLLID')),
            fields.get('title', ''), _blank(fields.get('ZDUPLICATEDFROMSNAPID')),
            snap['snap_id'], _blank(fields.get('ZMEDIAID')), fields.get('entry_id', ''),
            snap['account'], snap['profile'], snap['method'], snap['recovery_location']))
    data_list.sort(key=_by_creation)
    return _MEMORY_HEADERS, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def snapchatMemoriesMedia(context):
    memories, media, source_paths = _memories_data(context.get_files_found())
    by_key = {snap['key']: snap for snap in memories}
    cache = {}
    data_list = []
    for record in media:
        linked = [by_key[snap_key] for snap_key in record['snap_ids'] if snap_key in by_key]
        created = _cocoa_to_utc(linked[0]['fields'].get('ZCREATETIMEUTC')) if linked else ''
        reference = _media_reference(record, cache) if record['payload'] else None
        data_list.append((
            created, _ms_to_utc(record['deleted']), reference or '',
            ', '.join(snap_key[1] for snap_key in record['snap_ids']),
            ', '.join(sorted({snap['origin'] for snap in linked})), record['source'],
            record['linked_by'], record['role'], record['kind'], record['state'],
            record['format'], record['size'], record['complete'], record['key_source'],
            record['shared'] if record['snap_ids'] else '', record['cache_key'],
            context.get_relative_path(record['path']) if record['path'] else ''))
    data_list.sort(key=_by_creation)
    return _MEMORY_MEDIA_HEADERS, data_list, '\n'.join(sorted(source_paths))


_CHAT_MEDIA_HEADERS = (('Cache Entry Created', 'datetime'), ('Message Created', 'datetime'),
                       ('Cache Entry Deleted', 'datetime'), ('Media', 'media'),
                       'Conversation ID', 'Server Message ID', 'Message In arroyo.db',
                       'Link', 'Entry Kind (as stored)', 'File', 'Format', 'Size (bytes)',
                       'Media Context Type (as stored)', 'Cache Key', 'External Key',
                       'Account (USER_ID as stored)', 'Source File')


@artifact_processor
def snapchatChatMedia(context):
    '''One row per conversation media cache entry, with the file when it is on disk.'''
    files_found = context.get_files_found()
    messages = {}
    for arroyo_path in sorted({str(f) for f in files_found if str(f).endswith('arroyo.db')}):
        container = _app_container(arroyo_path)
        for conversation_id, server_id, created in _rows(arroyo_path, '''
                SELECT client_conversation_id, server_message_id, creation_timestamp
                FROM conversation_message'''):
            messages[(container, str(conversation_id or '').lower(), str(server_id))] = created
    checked_in = {}
    data_list = []
    source_paths = set()
    for entry in _chat_media_entries(files_found):
        claim = entry['claim']
        source_paths.add(entry['cache_db'])
        key = (entry['container'], entry['conversation'], entry['server_id'])
        path = entry['path']
        media_format, size, state = '', '', 'Not on disk'
        if path:
            source_paths.add(path)
            media_format, _extension, size = _file_state(path)
            state = 'On disk' if size else 'On disk, empty (0 bytes)'
            if size and not media_format:
                media_format = 'unrecognised'
        data_list.append((
            _ms_to_utc(claim['CREATION_TIMESTAMP_MILLIS']), _ms_to_utc(messages.get(key)),
            _ms_to_utc(claim['DELETED_TIMESTAMP_MILLIS']),
            _check_in_chat_file(entry, checked_in) or '', entry['conversation'],
            entry['server_id'], 'Yes' if key in messages else 'No', entry['link'],
            entry['kind'], state, media_format, size, _blank(claim['MEDIA_CONTEXT_TYPE']),
            claim['CACHE_KEY'] or '', claim['EXTERNAL_KEY'] or '', claim['USER_ID'] or '',
            context.get_relative_path(path or entry['cache_db'])))
    data_list.sort(key=_by_creation)
    return _CHAT_MEDIA_HEADERS, data_list, '\n'.join(sorted(source_paths))
