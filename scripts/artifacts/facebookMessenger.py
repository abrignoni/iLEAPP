__artifacts_v2__ = {
    "facebookMessengerCalls": {
        "name": "Facebook Messenger - Calls",
        "description": "Call events from the Facebook Messenger msys mailbox, with the recorded time, the "
        "caller's name and id and the call type and duration text as stored.",
        "author": "@stark4n6",
        "creation_date": "2021-03-03",
        "last_update_date": "2026-09-17",
        "requirements": "none",
        "category": "Facebook Messenger",
        "notes": "Read from both containers that hold Messenger's msys mailbox: "
        "lightspeed-userDatabases in the shared app group group.com.facebook.Messenger, and "
        "cask/<account id>/FBMessagingMailboxCaskStore/<n>/fb-msys-<account id>.db in the "
        "shared app group group.com.facebook.Facebook. Both group identifiers were read from "
        "those groups' own container metadata on the tested images. Records identical in "
        "every reported value are merged into one row whose Source File cell lists each file "
        "they were found in; records differing in any value are reported separately, so one "
        "held in both copies can still appear twice when a volatile value differs between "
        "them, which on the tested images is the profile picture URL because it carries a "
        "per-fetch token. Of the 25 registered corpora run, 4 carry the Facebook app's copy "
        "and no lightspeed copy, and 2 of those 4 (hexordia_ios1651, iphone12_ios18) have no "
        "Messenger app bundle on the image at all.",
        "paths": (
            "*/lightspeed-userDatabases/*.db*",
            "*/FBMessagingMailboxCaskStore/*/fb-msys-*.db*",
        ),
        "output_types": "standard",
        "artifact_icon": "phone-call",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Messenger 414.0 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | Messenger 526.0.0 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Messenger 408.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Messenger 557.0.0 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | Messenger 570.0.0 | 0 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | Messenger 405.0 | 4 rows",
            "iphone11_ios17": "iOS 17.3 | Messenger 468.1.0 | 20 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | Messenger 471.0.0 | 0 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 0 rows",
        },
    },
    "facebookMessengerChats": {
        "name": "Facebook Messenger - Chats",
        "description": "Messages from the thread_messages view of the Facebook Messenger msys mailbox, with "
        "direction, sender, text, attachment name and size and the thread id.",
        "author": "@stark4n6",
        "creation_date": "2021-03-03",
        "last_update_date": "2026-09-17",
        "requirements": "none",
        "category": "Facebook Messenger",
        "notes": "Read from both containers that hold Messenger's msys mailbox: "
        "lightspeed-userDatabases in the shared app group group.com.facebook.Messenger, and "
        "cask/<account id>/FBMessagingMailboxCaskStore/<n>/fb-msys-<account id>.db in the "
        "shared app group group.com.facebook.Facebook. Both group identifiers were read from "
        "those groups' own container metadata on the tested images. Records identical in "
        "every reported value are merged into one row whose Source File cell lists each file "
        "they were found in; records differing in any value are reported separately, so one "
        "held in both copies can still appear twice when a volatile value differs between "
        "them, which on the tested images is the profile picture URL because it carries a "
        "per-fetch token. Of the 25 registered corpora run, 4 carry the Facebook app's copy "
        "and no lightspeed copy, and 2 of those 4 (hexordia_ios1651, iphone12_ios18) have no "
        "Messenger app bundle on the image at all.",
        "paths": (
            "*/lightspeed-userDatabases/*.db*",
            "*/FBMessagingMailboxCaskStore/*/fb-msys-*.db*",
        ),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Messenger 414.0 | 25 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | Messenger 526.0.0 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Messenger 408.1 | 13 rows",
            "hc_ios18_7": "iOS 18.7.8 | Messenger 557.0.0 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | Messenger 570.0.0 | 0 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 17 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | Messenger 405.0 | 10 rows",
            "iphone11_ios17": "iOS 17.3 | Messenger 468.1.0 | 90 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | Messenger 471.0.0 | 0 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 0 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Thread ID",
                "textColumn": "Message",
                "directionColumn": "Message Direction",
                "directionSentValue": "Sent",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender Name",
            },
        },
    },
    "facebook_messenger_client_chats": {
        "name": "Facebook Messenger - Client Messages",
        "description": "Messages from the client_messages table of the Facebook Messenger msys mailbox, with "
        "direction, sender, the message text and the attachment image where its persisted "
        "file is present in the media bank.",
        "author": "Sukochev",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-09-17",
        "requirements": "none",
        "category": "Facebook Messenger",
        "notes": "All 114 client_messages rows across the 9 msys stores measured sit on a thread whose "
        "client_threads.transport_key is AdvancedCrypto, and all 18 of those threads carry "
        "Messenger's own end-to-end encryption notice as a message; where a row carries text, that "
        "text is held in this table unencrypted. Read from both containers that hold Messenger's msys "
        "mailbox: lightspeed-userDatabases in the shared app group group.com.facebook.Messenger, and "
        "cask/<account id>/FBMessagingMailboxCaskStore/<n>/fb-msys-<account id>.db in the shared app "
        "group group.com.facebook.Facebook. Both group identifiers were read from those groups' own "
        "container metadata on the tested images. Records identical in every reported value are "
        "merged into one row whose Source File cell lists each file they were found in; records "
        "differing in any value are reported separately, so one held in both copies can still appear "
        "twice when a volatile value differs between them, which on the tested images is the profile "
        "picture URL because it carries a per-fetch token. Of the 25 registered corpora run, 4 carry "
        "the Facebook app's copy and no lightspeed copy, and 2 of those 4 (hexordia_ios1651, "
        "iphone12_ios18) have no Messenger app bundle on the image at all. Message Direction, Sender "
        "Name and Sender ID are resolved through fb_transport_contacts. All 9 msys stores carrying "
        "client_messages declare sender_contact_pk a foreign key to client_contacts (pk), so it holds "
        "a client contact key, while contacts.id and _user_info.facebook_user_id hold Facebook user "
        "ids; fb_transport_contacts maps between the two. This is the store's own resolution path: "
        "its armadillo_participants view reaches a client participant's contact row through "
        "fb_unified_contacts, which on 8 of the 9 stores is contacts INNER JOIN fb_transport_contacts "
        "ON contacts.id = fb_transport_contacts.server_contact_id, and on the ninth (hickman_ios15, "
        "Messenger 405.0) joins that same table through an intermediate fb_client_contacts view. All "
        "9 carry a UNIQUE index on fb_transport_contacts.client_contact_pk, so the join cannot "
        "multiply rows. On 5 of the 9 the mapping is an identity map, every client contact key equal "
        "to the Facebook user id it maps to, so a client contact key on those stores reads like a "
        "Facebook user id; on the other 4 the two are unrelated. Measured on the 6 registered corpora "
        "that report rows (dexter_ios18, hc_ios18_7, hc_ios26, hickman_ios15, iphone11_ios17, "
        "otto_ios17), 114 rows in all: a sender name and a sender id are reported on 114 of 114 rows, "
        "and 76 of 114 are Sent. The mapping was cross-checked against the store's own server-side "
        "records: for each of the 9 client threads that mi_act_mapping_table maps to a server thread, "
        "the Facebook user ids fb_transport_contacts gives that thread's client_participants equal "
        "the contact ids the participants table holds for the mapped thread, 9 of 9 with no "
        "disagreement. Where a store carries no fb_transport_contacts table, or no mapping row for a "
        "sender, the raw sender_contact_pk is used as the Facebook user id; neither branch is "
        "exercised by these corpora, where all 9 stores carry the table and 0 of the 114 rows lack a "
        "mapping row.",
        "paths": (
            "*/lightspeed-userDatabases/*.db*",
            "*/FBMessagingMailboxCaskStore/*/fb-msys-*.db*",
            "*/lightspeed-TAMStorage/media_bank/AdvancedCrypto/*/persistent/*.jpg",
        ),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Messenger 414.0 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | Messenger 526.0.0 | 17 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Messenger 408.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Messenger 557.0.0 | 17 rows",
            "hc_ios26": "iOS 26.5.2 | Messenger 570.0.0 | 2 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | Messenger 405.0 | 12 rows",
            "iphone11_ios17": "iOS 17.3 | Messenger 468.1.0 | 44 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | Messenger 471.0.0 | 22 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 0 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Thread ID",
                "textColumn": "Message",
                "directionColumn": "Message Direction",
                "directionSentValue": "Sent",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender Name",
                "mediaColumn": "Image",
            },
        },
    },
    "facebookMessengerSecretConversations": {
        "name": "Facebook Messenger - Secret Conversations",
        "description": "Rows from the secure_messages table of the Facebook Messenger msys mailbox. The "
        "message and attachment values are stored encrypted and are reported as stored.",
        "author": "@stark4n6",
        "creation_date": "2021-03-03",
        "last_update_date": "2026-09-17",
        "requirements": "none",
        "category": "Facebook Messenger",
        "notes": "Read from both containers that hold Messenger's msys mailbox: "
        "lightspeed-userDatabases in the shared app group group.com.facebook.Messenger, and "
        "cask/<account id>/FBMessagingMailboxCaskStore/<n>/fb-msys-<account id>.db in the "
        "shared app group group.com.facebook.Facebook. Both group identifiers were read from "
        "those groups' own container metadata on the tested images. Records identical in "
        "every reported value are merged into one row whose Source File cell lists each file "
        "they were found in; records differing in any value are reported separately, so one "
        "held in both copies can still appear twice when a volatile value differs between "
        "them, which on the tested images is the profile picture URL because it carries a "
        "per-fetch token. Of the 25 registered corpora run, 4 carry the Facebook app's copy "
        "and no lightspeed copy, and 2 of those 4 (hexordia_ios1651, iphone12_ios18) have no "
        "Messenger app bundle on the image at all.",
        "paths": (
            "*/lightspeed-userDatabases/*.db*",
            "*/FBMessagingMailboxCaskStore/*/fb-msys-*.db*",
        ),
        "output_types": "standard",
        "artifact_icon": "lock",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Messenger 414.0 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | Messenger 526.0.0 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Messenger 408.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Messenger 557.0.0 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | Messenger 570.0.0 | 0 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | Messenger 405.0 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Messenger 468.1.0 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | Messenger 471.0.0 | 0 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 0 rows",
        },
    },
    "facebookMessengerConversationGroups": {
        "name": "Facebook Messenger - Conversation Groups",
        "description": "Conversation threads from the thread_participant_detail view of the Facebook "
        "Messenger msys mailbox, with the thread key, the participants and the last activity "
        "time.",
        "author": "@stark4n6",
        "creation_date": "2021-03-03",
        "last_update_date": "2026-09-17",
        "requirements": "none",
        "category": "Facebook Messenger",
        "notes": "Read from both containers that hold Messenger's msys mailbox: "
        "lightspeed-userDatabases in the shared app group group.com.facebook.Messenger, and "
        "cask/<account id>/FBMessagingMailboxCaskStore/<n>/fb-msys-<account id>.db in the "
        "shared app group group.com.facebook.Facebook. Both group identifiers were read from "
        "those groups' own container metadata on the tested images. Records identical in "
        "every reported value are merged into one row whose Source File cell lists each file "
        "they were found in; records differing in any value are reported separately, so one "
        "held in both copies can still appear twice when a volatile value differs between "
        "them, which on the tested images is the profile picture URL because it carries a "
        "per-fetch token. Of the 25 registered corpora run, 4 carry the Facebook app's copy "
        "and no lightspeed copy, and 2 of those 4 (hexordia_ios1651, iphone12_ios18) have no "
        "Messenger app bundle on the image at all.",
        "paths": (
            "*/lightspeed-userDatabases/*.db*",
            "*/FBMessagingMailboxCaskStore/*/fb-msys-*.db*",
        ),
        "output_types": "standard",
        "artifact_icon": "brand-facebook",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Messenger 414.0 | 6 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | Messenger 526.0.0 | 2 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Messenger 408.1 | 2 rows",
            "hc_ios18_7": "iOS 18.7.8 | Messenger 557.0.0 | 2 rows",
            "hc_ios26": "iOS 26.5.2 | Messenger 570.0.0 | 1 row",
            "hc_ios26_sysdiag": "iOS 26.6 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 1 row",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | Messenger 405.0 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | Messenger 468.1.0 | 4 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | Messenger 471.0.0 | 3 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 0 rows",
        },
    },
    "facebookMessengerContacts": {
        "name": "Facebook Messenger - Contacts",
        "description": "Contacts from the contacts table of the Facebook Messenger msys mailbox, with the "
        "Facebook id, names and profile picture link as stored.",
        "author": "@stark4n6",
        "creation_date": "2021-03-03",
        "last_update_date": "2026-09-17",
        "requirements": "none",
        "category": "Facebook Messenger",
        "notes": "Read from both containers that hold Messenger's msys mailbox: "
        "lightspeed-userDatabases in the shared app group group.com.facebook.Messenger, and "
        "cask/<account id>/FBMessagingMailboxCaskStore/<n>/fb-msys-<account id>.db in the "
        "shared app group group.com.facebook.Facebook. Both group identifiers were read from "
        "those groups' own container metadata on the tested images. Records identical in "
        "every reported value are merged into one row whose Source File cell lists each file "
        "they were found in; records differing in any value are reported separately, so one "
        "held in both copies can still appear twice when a volatile value differs between "
        "them, which on the tested images is the profile picture URL because it carries a "
        "per-fetch token. Of the 25 registered corpora run, 4 carry the Facebook app's copy "
        "and no lightspeed copy, and 2 of those 4 (hexordia_ios1651, iphone12_ios18) have no "
        "Messenger app bundle on the image at all.",
        "paths": (
            "*/lightspeed-userDatabases/*.db*",
            "*/FBMessagingMailboxCaskStore/*/fb-msys-*.db*",
        ),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Messenger 414.0 | 14 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | Messenger 526.0.0 | 8 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Messenger 408.1 | 5 rows",
            "hc_ios18_7": "iOS 18.7.8 | Messenger 557.0.0 | 5 rows",
            "hc_ios26": "iOS 26.5.2 | Messenger 570.0.0 | 2 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 2 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | Messenger 405.0 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | Messenger 468.1.0 | 3 rows",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | Messenger 471.0.0 | 13 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 0 rows",
        },
    },
}


from pathlib import Path

from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    convert_unix_ts_to_utc,
    does_table_exist_in_db,
    does_view_exist_in_db,
    get_sqlite_db_records,
)

CLIENT_MESSAGES = "client_messages"
FB_TRANSPORT_CONTACTS = "fb_transport_contacts"
CONTACTS = "contacts"
THREAD_MESSAGES = "thread_messages"
THREAD_PARTICIPANT_DETAIL = "thread_participant_detail"
SECURE_MESSAGES = "secure_messages"


def _database_files_with_view(context, view):
    db_list = []
    for file_found in context.get_files_found():
        if str(file_found).endswith(".db") and does_view_exist_in_db(file_found, view):
            db_list.append(file_found)
        else:
            continue
    return db_list


def _database_files_with_table(context, table):
    db_list = []
    for file_found in context.get_files_found():
        if str(file_found).endswith(".db") and does_table_exist_in_db(
            file_found, table
        ):
            db_list.append(file_found)
        else:
            continue
    return db_list


def _media_files(context):
    return [
        str(file_found)
        for file_found in context.get_files_found()
        if str(file_found).endswith(".jpg")
    ]



def _merge_duplicate_records(data_list):
    """Collapse records read twice because the device carries two mailbox copies.

    Messenger keeps the same msys mailbox under lightspeed-userDatabases and under
    FBMessagingMailboxCaskStore. A record present in both is one record, so it is
    reported once with every file it was found in listed in its Source File cell.
    Records that differ in any reported value are left alone.
    """
    sources_by_record = {}
    order = []
    for record in data_list:
        values, source = record[:-1], record[-1]
        if values not in sources_by_record:
            sources_by_record[values] = []
            order.append(values)
        if source not in sources_by_record[values]:
            sources_by_record[values].append(source)
    return [values + ("; ".join(sources_by_record[values]),) for values in order]

_CLIENT_MESSAGES_QUERY = """
    SELECT
        client_messages.display_ts_ms,
        client_messages.thread_pk,
        CASE
            WHEN {sender_id} = _user_info.facebook_user_id
                THEN contacts.name || ' (Local User)'
            ELSE contacts.name
        END,
        contacts.id,
        CASE
            WHEN {sender_id} = _user_info.facebook_user_id THEN 'Sent'
            ELSE 'Received'
        END AS "Message Direction",
        client_messages.text,
        CASE client_messages.message_content_type
            WHEN 2 THEN 'Yes'
            ELSE ''
        END AS "Attachment-Image",
        client_attachments.filename,
        client_attachments.filesize,
        client_attachment_store_keys.persisted_path
    FROM client_messages
    {transport_join}
    LEFT JOIN contacts
        ON contacts.id = {sender_id}
    LEFT JOIN client_attachments
        ON client_messages.pk = client_attachments.message_pk
    LEFT JOIN client_attachment_store_keys
        ON client_attachments.content_token = client_attachment_store_keys.content_token
    LEFT JOIN _user_info
    ORDER BY client_messages.display_ts_ms ASC
    """

_TRANSPORT_JOIN = """LEFT JOIN fb_transport_contacts
        ON fb_transport_contacts.client_contact_pk = client_messages.sender_contact_pk"""

# client_messages declares sender_contact_pk a foreign key to client_contacts (pk), so it is a
# client contact key, while contacts.id and _user_info.facebook_user_id hold Facebook user ids.
# fb_transport_contacts maps between the two, and it is the store's own resolution path: the
# app's armadillo_participants view reaches a client participant's contact row through
# fb_unified_contacts, which joins fb_transport_contacts on its server_contact_id directly on
# the newer stores and through an intermediate fb_client_contacts view on the older ones.
# Falling back to the raw key covers a store that does not carry the mapping table.
_SENDER_ID_VIA_TRANSPORT = (
    "COALESCE(fb_transport_contacts.server_contact_id, client_messages.sender_contact_pk)"
)
_SENDER_ID_DIRECT = "client_messages.sender_contact_pk"


def _client_messages_query(has_transport_contacts):
    if has_transport_contacts:
        return _CLIENT_MESSAGES_QUERY.format(
            sender_id=_SENDER_ID_VIA_TRANSPORT, transport_join=_TRANSPORT_JOIN
        )
    return _CLIENT_MESSAGES_QUERY.format(
        sender_id=_SENDER_ID_DIRECT, transport_join=""
    )


def _source_path(context, files_found):
    if not files_found:
        return ""
    return "\n".join(
        context.get_relative_path(file_found) for file_found in files_found
    )


@artifact_processor
def facebookMessengerCalls(context):
    data_list = []

    database_files_found = _database_files_with_view(context, THREAD_MESSAGES)
    source_path = _source_path(context, database_files_found)

    data_headers = (
        ("Timestamp", "datetime"),
        "Sender Name",
        "Sender ID",
        "Call Type",
        "Call Duration/Subtitle",
        "Source File",
    )

    query = """
    SELECT
        thread_messages.timestamp_ms,
        contacts.name,
        thread_messages.sender_id,
        attachments.title_text,
        attachments.subtitle_text
    FROM thread_messages
    LEFT JOIN contacts
        ON thread_messages.sender_id = contacts.id
    LEFT JOIN attachments
        ON thread_messages.message_id = attachments.message_id
    WHERE attachments.title_text like '%call%'
    """

    if database_files_found:
        for file_found in database_files_found:
            db_records = get_sqlite_db_records(file_found, query)
            for record in db_records:
                timestamp = ""
                sender_name = ""
                sender_id = ""
                call_type = ""
                call_duration = ""

                if record[0] > 0:
                    timestamp = convert_unix_ts_to_utc(record[0])
                else:
                    timestamp = record[0]

                sender_name = record[1]
                sender_id = record[2]
                call_type = record[3]
                call_duration = record[4]
                # NOTE: this pattern is repeated on this file and it can be
                #   replaced by unpacking the record over the variables
                #   we don't even need to initialize the varibles beforehand

                data_list.append(
                    (
                        timestamp,
                        sender_name,
                        sender_id,
                        call_type,
                        call_duration,
                        context.get_relative_path(file_found),
                    )
                )

        return data_headers, _merge_duplicate_records(data_list), source_path
    else:
        return data_headers, _merge_duplicate_records(data_list), source_path


@artifact_processor
def facebookMessengerChats(context):
    data_list = []

    database_files_found = _database_files_with_view(context, THREAD_MESSAGES)
    source_path = _source_path(context, database_files_found)

    data_headers = (
        ("Timestamp", "datetime"),
        "Message Direction",
        "Sender Name",
        "Message",
        "Sender ID",
        "Attachment",
        "Attachment Name",
        "Attachment Size",
        "Title Text",
        "Subtitle Text",
        "Thread ID",
        "Source File",
    )

    query = """
    SELECT
	thread_messages.timestamp_ms,
	CASE 
        WHEN (SELECT CASE
		WHEN _user_info.facebook_user_id IS NOT NULL THEN 'Sent'
		ELSE 'Received'
	END) = 'Sent' THEN COALESCE(contacts.name, '') || ' (Local User)'
        ELSE contacts.name
    END,
	contacts.id,
	CASE
		WHEN _user_info.facebook_user_id IS NOT NULL THEN 'Sent'
		ELSE 'Received'
	END AS "Message Direction",
	thread_messages.text,
	CASE thread_messages.has_attachment
		WHEN NULL THEN ''
		WHEN 1 THEN 'Yes'
	END AS Attachment,
	attachments.filename,
	attachments.filesize,
	attachment_items.title_text,
    attachment_items.subtitle_text,
    thread_messages.thread_key
    FROM thread_messages
    LEFT JOIN contacts
        ON thread_messages.sender_id = contacts.id
    LEFT JOIN attachments
        ON thread_messages.message_id = attachments.message_id
    LEFT JOIN attachment_items
        ON thread_messages.message_id = attachment_items.message_id
    LEFT JOIN _user_info
        ON thread_messages.sender_id = _user_info.facebook_user_id
    WHERE attachment_items.title_text IS NULL or attachment_items.title_text NOT LIKE '%call%'
    ORDER BY thread_messages.timestamp_ms ASC
    """

    if database_files_found:
        for file_found in database_files_found:
            db_records = get_sqlite_db_records(file_found, query)
            for record in db_records:
                timestamp = ""
                sender_name = ""
                sender_id = ""
                message_direction = ""
                message = ""
                attachment = ""
                attachment_name = ""
                attachment_size = ""
                title_text = ""
                subtitle_text = ""
                thread_id = ""

                if record[0] > 0:
                    timestamp = convert_unix_ts_to_utc(record[0])
                else:
                    timestamp = record[0]

                sender_name = record[1]
                sender_id = record[2]
                message_direction = record[3]
                message = record[4]
                attachment = record[5]
                attachment_name = record[6]
                attachment_size = record[7]
                title_text = record[8]
                subtitle_text = record[9]
                thread_id = record[10]

                data_list.append(
                    (
                        timestamp,
                        message_direction,
                        sender_name,
                        message,
                        sender_id,
                        attachment,
                        attachment_name,
                        attachment_size,
                        title_text,
                        subtitle_text,
                        thread_id,
                        context.get_relative_path(file_found),
                    )
                )

        return data_headers, _merge_duplicate_records(data_list), source_path
    else:
        return data_headers, _merge_duplicate_records(data_list), source_path


@artifact_processor
def facebook_messenger_client_chats(context):
    data_list = []

    database_files_found = _database_files_with_table(context, CLIENT_MESSAGES)
    source_path = _source_path(context, database_files_found)

    media_files_found = _media_files(context)

    data_headers = (
        ("Timestamp", "datetime"),
        "Message Direction",
        "Sender Name",
        "Message",
        ("Image", "media"),
        "Thread ID",
        "Sender ID",
        "Attachment-Image",
        "Attachment Name",
        "Attachment Size",
        "Attachment Persisted Path",
        "Source File",
    )

    if database_files_found:
        for file_found in database_files_found:
            query = _client_messages_query(
                does_table_exist_in_db(file_found, FB_TRANSPORT_CONTACTS)
            )
            db_records = get_sqlite_db_records(file_found, query)
            for record in db_records:
                timestamp = ""
                thread_id = ""
                sender_name = ""
                sender_id = ""
                message_direction = ""
                message = ""
                is_attachment_image = ""
                attachment_name = ""
                attachment_size = ""
                attachment_persisted_path = ""
                media_file_found = ""

                if record[0] > 0:
                    timestamp = convert_unix_ts_to_utc(record[0])
                else:
                    timestamp = record[0]

                thread_id = record[1]
                sender_name = record[2]
                sender_id = record[3]
                message_direction = record[4]
                message = record[5]
                is_attachment_image = record[6]
                attachment_name = record[7]
                attachment_size = record[8]
                attachment_persisted_path = record[9]

                if media_files_found and attachment_persisted_path:
                    attachment_persisted_path_formatted = Path(attachment_persisted_path)
                    attachment_name_formatted = attachment_persisted_path_formatted.name
                    for image in media_files_found:
                        if image.endswith(str(attachment_name_formatted)):
                            media_file = image
                            media_path = Path(media_file)
                            media_filename = media_path.name
                            media_file_found = check_in_media(
                                media_file, media_filename
                            )

                data_list.append(
                    (
                        timestamp,
                        message_direction,
                        sender_name,
                        message,
                        media_file_found,
                        thread_id,
                        sender_id,
                        is_attachment_image,
                        attachment_name,
                        attachment_size,
                        attachment_persisted_path,
                        context.get_relative_path(file_found),
                    )
                )

        return data_headers, _merge_duplicate_records(data_list), source_path
    else:
        return data_headers, _merge_duplicate_records(data_list), source_path


@artifact_processor
def facebookMessengerSecretConversations(context):
    data_list = []

    database_files_found = _database_files_with_table(context, SECURE_MESSAGES)
    source_path = _source_path(context, database_files_found)

    data_headers = (
        ("Timestamp", "datetime"),
        "Thread Key",
        "Sender Name",
        "Message (Encrypted)",
        "Attachment (Encrypted)",
        "Source File",
    )

    query = """
    SELECT
        secure_messages.timestamp_ms,
        secure_messages.thread_key,
        contacts.name,
        secure_messages.text,
        secure_messages.secure_message_attachments_encrypted
    FROM secure_messages
    LEFT JOIN contacts
        ON secure_messages.sender_id = contacts.id
    """

    if database_files_found:
        for file_found in database_files_found:
            db_records = get_sqlite_db_records(file_found, query)
            for record in db_records:
                timestamp = ""
                thread_key = ""
                sender_name = ""
                message = ""
                attachment = ""

                if record[0] > 0:
                    timestamp = convert_unix_ts_to_utc(record[0])
                else:
                    timestamp = record[0]

                thread_key = record[1]
                sender_name = record[2]
                message = record[3]
                attachment = record[4]

                data_list.append(
                    (
                        timestamp,
                        thread_key,
                        sender_name,
                        message,
                        attachment,
                        context.get_relative_path(file_found),
                    )
                )

        return data_headers, _merge_duplicate_records(data_list), source_path
    else:
        return data_headers, _merge_duplicate_records(data_list), source_path


@artifact_processor
def facebookMessengerConversationGroups(context):
    data_list = []

    database_files_found = _database_files_with_view(context, THREAD_PARTICIPANT_DETAIL)
    source_path = _source_path(context, database_files_found)

    data_headers = (
        ("Timestamp (Last Activity)", "datetime"),
        "Thread Key",
        "Thread Participants",
        "Source File",
    )

    query = """
    SELECT
        threads.last_activity_timestamp_ms,
        thread_participant_detail.thread_key,
        group_concat(thread_participant_detail.name, ';') 
    FROM thread_participant_detail
    JOIN threads
        ON threads.thread_key = thread_participant_detail.thread_key
    GROUP BY thread_participant_detail.thread_key
    """

    if database_files_found:
        for file_found in database_files_found:
            db_records = get_sqlite_db_records(file_found, query)
            for record in db_records:
                timestamp = ""
                thread_key = ""
                thread_participants = ""

                if record[0] > 0:
                    timestamp = convert_unix_ts_to_utc(record[0])
                else:
                    timestamp = record[0]

                thread_key = record[1]
                thread_participants = record[2]

                data_list.append(
                    (
                        timestamp,
                        thread_key,
                        thread_participants,
                        context.get_relative_path(file_found),
                    )
                )

        return data_headers, _merge_duplicate_records(data_list), source_path
    else:
        return data_headers, _merge_duplicate_records(data_list), source_path


@artifact_processor
def facebookMessengerContacts(context):
    data_list = []

    database_files_found = _database_files_with_table(context, CONTACTS)
    source_path = _source_path(context, database_files_found)

    data_headers = (
        "User ID",
        "Username",
        "Normalized Username",
        "Profile Pic URL",
        "Is App User",
        "Source File",
    )

    query = """
    SELECT
        id,
        name,
        normalized_name_for_search,
        profile_picture_url,
        CASE is_messenger_user
            WHEN 0 THEN ''
            WHEN 1 THEN 'Yes'
        END AS is_messenger_user
    FROM contacts
    """

    if database_files_found:
        for file_found in database_files_found:
            db_records = get_sqlite_db_records(file_found, query)
            for record in db_records:
                user_id = ""
                contact_name = ""
                normalized_contact_name = ""
                profile_picture_url = ""
                is_app_user = ""

                user_id = record[0]
                contact_name = record[1]
                normalized_contact_name = record[2]
                profile_picture_url = record[3]
                is_app_user = record[4]

                data_list.append(
                    (
                        user_id,
                        contact_name,
                        normalized_contact_name,
                        profile_picture_url,
                        is_app_user,
                        context.get_relative_path(file_found),
                    )
                )

        return data_headers, _merge_duplicate_records(data_list), source_path
    else:
        return data_headers, _merge_duplicate_records(data_list), source_path
