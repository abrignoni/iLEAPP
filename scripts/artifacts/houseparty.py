__artifacts_v2__ = {
    "housepartyMessages": {
        "name": "Houseparty - Direct Messages",
        "description": "Direct messages held in the Houseparty app's Realm store, with the time each was sent, "
                       "the account that sent it, the account it was addressed to, the message text, and the "
                       "thumbnail and video of a facemail where the store and the container hold them.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-04",
        "last_update_date": "2026-09-04",
        "requirements": "none",
        "category": "Houseparty",
        "notes": "Read from class_RealmNote in Documents/houseparty.rocky.realm with the vendored "
                 "realm_parser. Houseparty was a group video chat app; its publisher removed it "
                 "from the app stores on 9 September 2021 and shut it down in October 2021, so a "
                 "store found now is a residue of earlier use. Reference: Sarah Perez, 'Epic "
                 "Games to shut down Houseparty in October, including the video chat Fortnite "
                 "Mode feature', TechCrunch, "
                 "https://techcrunch.com/2021/09/09/epic-games-to-shut-down-houseparty-in-october-including-the-video-chat-fortnite-mode-feature/ "
                 "The store's file name is the app's own, so the pattern is anchored on it even "
                 "though an iOS data container is named by an identifier; a store without "
                 "class_RealmUser and class_RealmGlobals is skipped and logged. Direction is "
                 "derived by comparing each message's senderId against the currentUserId "
                 "class_RealmGlobals records, which is the identity the store itself holds, and "
                 "is left empty when that row is absent. Sender and Recipient are resolved to the "
                 "username class_RealmPublicUser records for that id, falling back to the id as "
                 "stored. Sent At is built from the row's own sentAtSeconds and sentAtNanos, "
                 "which agreed with its sentAt text on every message of the tested images, and "
                 "the newest value matched lastNoteSentAt in the app's Houseparty.plist to the "
                 "millisecond. A facemail is the app's video message: the row's facemail link "
                 "resolves to class_RealmFacemail, whose thumbnail column holds a base64 PNG that "
                 "is rendered in Facemail Thumbnail, and whose mediaID names the video. The video "
                 "itself is rendered in Facemail Video when Library/Application "
                 "Support/Prefetched-Facemails/<mediaID>.mp4 exists in the same container; on the "
                 "tested images that file was present for the one facemail received and absent "
                 "for the two sent, so Facemail Video is blank on a sent facemail. A facemail row "
                 "carries an empty Message. Facemail Watched is the store's watched flag as "
                 "stored. Unread is the row's isUnread flag and was False on every message of the "
                 "tested images. Note ID is the noteId the service assigned; the row's local id "
                 "differs from it on sent messages and is not reported. Conversation names the "
                 "other account in the exchange, so it holds one value wherever the store records "
                 "messages with a single correspondent, as it did on both tested images. "
                 "class_RealmConversation holds one summary row per correspondent that repeats "
                 "the newest message's time and is not reported. class_RealmHouseMessage and "
                 "every other class_RealmHouse* table (group chats the app called houses) held no "
                 "rows on the tested images, so no group message was recovered.",
        "paths": ('*/Documents/houseparty.rocky.realm',
                  '*/Library/Application Support/Prefetched-Facemails/*.mp4'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 0 rows",
            "belkactf6": "iOS 16.3 | 0 rows (run against the decrypted filesystem copy)",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | com.herzick.houseparty 1.34.6 | 5 rows",
            "hickman_ios14": "iOS 14.3 | com.herzick.houseparty 1.56.0 | 6 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 0 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation",
                "conversationLabelColumn": "Conversation",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Sent At",
                "senderColumn": "Sender",
                "mediaColumn": "Facemail Thumbnail",
            },
        },
    },
    "housepartyRooms": {
        "name": "Houseparty - Video Rooms",
        "description": "Video rooms the app recorded, with the time each was created, whether it was locked, "
                       "who the app had invited to it and the media server session it was carried on.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-04",
        "last_update_date": "2026-09-04",
        "requirements": "none",
        "category": "Houseparty",
        "notes": "Read from class_RealmRoom in the app's Realm store, with the session joined from "
                 "class_RealmRoomSession through the row's own latestSession link and the server host joined "
                 "from class_RealmMediaServerEndpoint through the session's mediaServer link. A room row records "
                 "that the app held a room, not that a call took place or who was in it. Invited Users lists "
                 "the accounts named in the row's invitedUsers link list, resolved to usernames; it was empty "
                 "on every room of the tested images, and the parser reads link lists elsewhere in the same "
                 "file, so that is an absence in the data rather than a decoding limit. Locked, Locking User, "
                 "Video Tech and Secret Version are reported as stored; no room on the tested images was "
                 "locked, so Locking User is empty on all of them. Media Server is the host the session's "
                 "endpoint row names and is the server the app was told to use, not an address the device is "
                 "shown to have reached; on the iOS 13 image two of the three sessions named hosts under "
                 "rtcp.on.epicgames.com and the third a host under ms.thehousepartyapp.com, and on the iOS 14 "
                 "image all four named ms.thehousepartyapp.com hosts. The session's latestTicketString is a "
                 "credential and is not reported.",
        "paths": ('*/Documents/houseparty.rocky.realm',),
        "output_types": "standard",
        "artifact_icon": "video",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 0 rows",
            "belkactf6": "iOS 16.3 | 0 rows (run against the decrypted filesystem copy)",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | com.herzick.houseparty 1.34.6 | 3 rows",
            "hickman_ios14": "iOS 14.3 | com.herzick.houseparty 1.56.0 | 4 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 0 rows",
        },
    },
    "housepartyAccount": {
        "name": "Houseparty - Account",
        "description": "The signed-in Houseparty account, with the username, full name, email address, "
                       "telephone number and birthday the account held, the privacy settings stored alongside "
                       "it, and the sign-in and last-use times the app kept in its preferences.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-04",
        "last_update_date": "2026-09-04",
        "requirements": "none",
        "category": "Houseparty",
        "notes": "Read from class_RealmUser in the app's Realm store, with the public profile "
                 "joined from class_RealmPublicUser through the row's own publicUser link, the "
                 "settings from class_RealmUserSettings through its settings link, and the "
                 "session dates from class_RealmToken matched on the account id. These are values "
                 "the account held in the app, which the app received from its service; they are "
                 "not verified identifiers. Signed In At, Last Backgrounded At and Activity Last "
                 "Seen At come from the SignedInAt, lastBackgroundedAt and activityLastSeenAt "
                 "keys of Library/Preferences/Houseparty.plist in the same container and are "
                 "blank when that file is absent; on the tested images Signed In At agreed with "
                 "Session Created to the second. Birthday fell on midnight UTC on both tested "
                 "images and is reported as a date rather than a datetime for that reason. "
                 "Session Invalidated is blank where class_RealmToken holds the Unix epoch, which "
                 "is the store's not-invalidated sentinel, as it did on both tested images. The "
                 "token string, the authentication record and the push and VoIP tokens in the "
                 "same stores are not reported. Linked Accounts lists the display names of linked "
                 "Epic accounts where the store carries any; on the tested images the list was "
                 "empty on the iOS 14 image and the column absent from the iOS 13 schema. "
                 "Facebook ID is reported as stored and was empty on both. Phone is the number "
                 "the account record holds as stored; it was empty on the iOS 13 image and "
                 "populated on the iOS 14 image, where the app's own traits file recorded the "
                 "phone as verified. The Fortnite notification settings the iOS 14 schema adds to "
                 "class_RealmUserSettings are not reported. class_RealmClientPreferencesData "
                 "holds a protobuf of per-feature timestamps whose meaning is not recorded in the "
                 "store and is not reported.",
        "paths": ('*/Documents/houseparty.rocky.realm',
                  '*/Library/Preferences/Houseparty.plist'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 0 rows",
            "belkactf6": "iOS 16.3 | 0 rows (run against the decrypted filesystem copy)",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | com.herzick.houseparty 1.34.6 | 1 row",
            "hickman_ios14": "iOS 14.3 | com.herzick.houseparty 1.56.0 | 1 row",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 0 rows",
        },
    },
    "housepartyContacts": {
        "name": "Houseparty - Contacts",
        "description": "Other Houseparty accounts the app held, with the username and full name each carried, "
                       "when each was last seen, the address book name the app matched it to, and the "
                       "relationship, interaction and time-together values the app recorded for them.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-04",
        "last_update_date": "2026-09-04",
        "requirements": "none",
        "category": "Houseparty",
        "notes": "Read from class_RealmPublicUser in the app's Realm store, with presence joined "
                 "from class_RealmUserPresence, the relationship from "
                 "class_RealmRelationshipInfo, the address book name from "
                 "class_RealmUserRelevance, the last interaction from class_RealmUserInteraction "
                 "and the time-together counters from class_RealmWithSomeoneData and "
                 "class_RealmLocalWithSomeoneData, each through the row's own links or matched on "
                 "the account id. The signed-in account appears here as well as in the Account "
                 "artifact, because the store keeps a public record for it too. Last Seen and "
                 "Room Created At are values the service supplied about that account and are not "
                 "evidence of activity on this device. Address Book Name is the name the app "
                 "matched the account to in this device's contacts, as stored, and is blank where "
                 "no relevance row exists. Last Interaction At and Last Interaction Type come "
                 "from the interaction row the relationship links to; the type is an integer the "
                 "store does not explain and is reported as stored. Presence Type, Relationship "
                 "Status, Relevance Reason, On Phone, Notifications Enabled and Ghosting are "
                 "reported as stored; On Phone and Ghosting were False on every row of the tested "
                 "images, and Presence Type was offline on every row. Active With Someone Minutes "
                 "and Local Minutes are the app's own counters as stored, and Last With Someone "
                 "At and Local Last With Someone At are the timestamps beside them; the two rows "
                 "can differ. Room Colour is the color value the presence row carries, a hex RGB "
                 "string as stored. The iOS 14 schema adds an isSuspect flag, which is not "
                 "reported because the store does not record what sets it.",
        "paths": ('*/Documents/houseparty.rocky.realm',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 0 rows",
            "belkactf6": "iOS 16.3 | 0 rows (run against the decrypted filesystem copy)",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | com.herzick.houseparty 1.34.6 | 2 rows",
            "hickman_ios14": "iOS 14.3 | com.herzick.houseparty 1.56.0 | 2 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 0 rows",
        },
    },
    "housepartyPhoneContacts": {
        "name": "Houseparty - Phone Contacts",
        "description": "Entries from this device's address book that the Houseparty app read, with the "
                       "name and number as stored and the Houseparty account each was matched to.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-04",
        "last_update_date": "2026-09-04",
        "requirements": "none",
        "category": "Houseparty",
        "notes": "Read from class_RealmContact in the app's Realm store, one row per phone number, with the "
                 "matched account joined from class_RealmPublicUser through the row's own user link and the "
                 "contact record joined from class_RealmLocalContact through its contacts link list. Name In "
                 "Phone is the name as the app read it from the address book, and Phone is the number in E.164 "
                 "form as stored; Phone (as formatted) is the formatted spelling the app keeps for the same "
                 "number in Documents/houseparty.rocky.phonenumbers where that store is present. Score, Invite "
                 "Sent, Ignored and Suggested are reported as stored. A row means the app read that address "
                 "book entry; it does not establish that the entry was uploaded or that the person uses "
                 "Houseparty unless Matched Username is populated. On the iOS 13 image the app's traits "
                 "recorded the contacts permission as allowed and this table held two numbers of one contact, "
                 "one of them matched to a Houseparty account; on the iOS 14 image the permission was recorded "
                 "as denied, the table held no rows and the phone-number store was absent. The iOS 14 schema "
                 "keeps the contact name only on class_RealmLocalContact, and the artifact reads it from there "
                 "when the row itself carries none. There is no timestamp in these rows.",
        "paths": ('*/Documents/houseparty.rocky.realm',
                  '*/Documents/houseparty.rocky.phonenumbers'),
        "output_types": "standard",
        "artifact_icon": "book",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 0 rows",
            "belkactf6": "iOS 16.3 | 0 rows (run against the decrypted filesystem copy)",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | com.herzick.houseparty 1.34.6 | 2 rows",
            "hickman_ios14": "iOS 14.3 | com.herzick.houseparty 1.56.0 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 0 rows",
        },
    },
}

import base64
import os
import re
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import (artifact_processor, check_in_embedded_media, check_in_media,
                               get_plist_file_content, logfunc)
from scripts.realm_parser import parse_realm_file

# A store is this app's only when it holds both; anything else matching the pattern is
# skipped and logged rather than reported under Houseparty's name.
_MARKER_CLASSES = ('class_RealmUser', 'class_RealmGlobals')
_REALM = 'houseparty.rocky.realm'
_PHONES = 'houseparty.rocky.phonenumbers'
_PLIST = 'Houseparty.plist'
_CONTAINER = re.compile(r'^(.*?/Containers/Data/Application/[^/]+)/', re.I)
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

_parsed = {}


def _utc(value):
    """A 'YYYY-MM-DD HH:MM:SS UTC' value as an aware datetime, or '' when unusable."""
    text = str(value or '').strip()
    if not text.endswith(' UTC'):
        return ''
    try:
        return datetime.strptime(text[:-4], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    except ValueError:
        return ''


def _utc_from_parts(seconds, nanos, fallback):
    """A datetime from Unix seconds plus nanoseconds, or the fallback text when absent."""
    if isinstance(seconds, bool) or not isinstance(seconds, int):
        return _utc(fallback)
    micros = int(nanos) // 1000 if isinstance(nanos, int) and not isinstance(nanos, bool) else 0
    return _EPOCH + timedelta(seconds=seconds, microseconds=micros)


def _date_only(value):
    """The date part of a UTC-marked value, for a value stored at midnight."""
    stamp = _utc(value)
    return stamp.strftime('%Y-%m-%d') if stamp else ''


def _plist_dt(value):
    """A plist datetime as an aware UTC datetime, or ''."""
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    return ''


def _text(value):
    """A displayable scalar. A list is rendered as its members, not its length."""
    if value is None:
        return ''
    if isinstance(value, bool):
        return value
    if isinstance(value, list):
        return ', '.join(str(item) for item in value)
    return value


def _parse(path):
    if path not in _parsed:
        _parsed[path] = parse_realm_file(path)
    return _parsed[path]


def _containers(context):
    """{container root: {'realm': path, 'phones': path, 'plist': path, 'mp4': {mediaID: path}}}."""
    found = {}
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        match = _CONTAINER.match(file_found.replace('\\', '/'))
        root = match.group(1) if match else os.path.dirname(os.path.dirname(file_found))
        entry = found.setdefault(root, {'mp4': {}})
        name = os.path.basename(file_found)
        if name == _REALM:
            entry['realm'] = file_found
        elif name == _PHONES:
            entry['phones'] = file_found
        elif name == _PLIST:
            entry['plist'] = file_found
        elif name.lower().endswith('.mp4') and 'Prefetched-Facemails' in file_found:
            entry['mp4'][name[:-4].lower()] = file_found
    return found


def _stores(context):
    """Each container whose Realm store carries this app's marker classes, as (entry, tables)."""
    out = []
    for root in sorted(_containers(context)):
        entry = _containers(context)[root]
        store = entry.get('realm')
        if not store:
            continue
        try:
            parsed = _parse(store)
        except Exception as error:  # pylint: disable=broad-exception-caught
            logfunc(f'Houseparty: {os.path.basename(store)} did not parse: {error}')
            continue
        tables = parsed.get('active') or {}
        if not all(name in tables for name in _MARKER_CLASSES):
            logfunc(f'Houseparty: {os.path.basename(store)} holds no {" and ".join(_MARKER_CLASSES)}, skipped')
            continue
        if parsed.get('reason'):
            logfunc(f'Houseparty: {os.path.basename(store)}: {parsed["reason"]}')
        out.append((entry, tables))
    return out


def _rows(tables, class_name):
    """Every row of ``class_name`` as a {column_name: value} dict."""
    table = tables.get(class_name)
    if not table:
        return []
    names = table['column_names']
    columns = table['columns']
    out = []
    for i in range(table['row_count']):
        row = {}
        for j, name in enumerate(names):
            values = columns.get(j)
            row[name] = values[i] if values is not None and i < len(values) else None
        out.append(row)
    return out


def _linked(rows, index):
    """The row a link column points at, or None. Links are positional row indexes."""
    if index is None or isinstance(index, bool):
        return None
    try:
        position = int(index)
    except (TypeError, ValueError):
        return None
    return rows[position] if 0 <= position < len(rows) else None


def _linked_all(rows, indexes):
    """The rows a link list points at."""
    if not isinstance(indexes, list):
        return []
    return [row for row in (_linked(rows, i) for i in indexes) if row is not None]


def _name_map(tables):
    """account id -> the username class_RealmPublicUser records for it."""
    out = {}
    for row in _rows(tables, 'class_RealmPublicUser'):
        if row.get('id'):
            out[str(row['id'])] = row.get('username') or row.get('fullName') or ''
    return out


def _who(account_id, names):
    """A username for an account id, falling back to the id as stored."""
    key = str(account_id or '')
    if not key:
        return ''
    return names.get(key) or key


def _current_user(tables):
    globals_rows = _rows(tables, 'class_RealmGlobals')
    if globals_rows and globals_rows[0].get('currentUserId'):
        return str(globals_rows[0]['currentUserId'])
    users = _rows(tables, 'class_RealmUser')
    return str(users[0]['id']) if users and users[0].get('id') else ''


@artifact_processor
def housepartyMessages(context):
    data_headers = (
        ('Sent At', 'datetime'),
        'Direction',
        'Sender',
        'Conversation',
        'Message',
        ('Facemail Thumbnail', 'media'),
        ('Facemail Video', 'media'),
        'Facemail Watched',
        'Facemail Media ID',
        'Recipient',
        'Unread',
        'Note ID',
    )
    data_list = []
    sources = []
    for entry, tables in _stores(context):
        store = entry['realm']
        names = _name_map(tables)
        account_id = _current_user(tables)
        facemails = _rows(tables, 'class_RealmFacemail')
        used_video = set()
        read_any = False
        for row in _rows(tables, 'class_RealmNote'):
            sender_id = str(row.get('senderId') or '')
            recipient_id = str(row.get('recipientId') or '')
            if account_id and sender_id:
                direction = 'Outgoing' if sender_id == account_id else 'Incoming'
            else:
                direction = ''
            other = recipient_id if direction == 'Outgoing' else sender_id
            facemail = _linked(facemails, row.get('facemail'))
            thumbnail = video = ''
            media_id = watched = ''
            if facemail:
                media_id = str(facemail.get('mediaID') or '')
                watched = _text(facemail.get('watched'))
                try:
                    png = base64.b64decode(str(facemail.get('thumbnail') or ''))
                except ValueError:
                    png = b''
                if png:
                    thumbnail = check_in_embedded_media(store, png, f'facemail-{media_id}-thumbnail.png') or ''
                mp4 = entry['mp4'].get(media_id.lower())
                if mp4:
                    video = check_in_media(mp4, f'{media_id}.mp4') or ''
                    used_video.add(mp4)
            data_list.append((
                _utc_from_parts(row.get('sentAtSeconds'), row.get('sentAtNanos'), row.get('sentAt')),
                direction,
                _who(sender_id, names),
                _who(other, names),
                _text(row.get('content')),
                thumbnail,
                video,
                watched,
                media_id,
                _who(recipient_id, names),
                _text(row.get('isUnread')),
                _text(row.get('noteId')),
            ))
            read_any = True
        if read_any:
            sources.append(store)
            sources.extend(sorted(used_video))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def housepartyRooms(context):
    data_headers = (
        ('Created At', 'datetime'),
        'Room ID',
        'Locked',
        'Locking User',
        'Invited Users',
        'Media Server',
        'Session ID',
        'Video Tech (as stored)',
        'Secret Version (as stored)',
    )
    data_list = []
    sources = []
    for entry, tables in _stores(context):
        store = entry['realm']
        names = _name_map(tables)
        public = _rows(tables, 'class_RealmPublicUser')
        sessions = _rows(tables, 'class_RealmRoomSession')
        endpoints = _rows(tables, 'class_RealmMediaServerEndpoint')
        read_any = False
        for row in _rows(tables, 'class_RealmRoom'):
            session = _linked(sessions, row.get('latestSession'))
            endpoint = _linked(endpoints, session.get('mediaServer')) if session else None
            invited = [_who(user.get('id'), names) for user in _linked_all(public, row.get('invitedUsers'))]
            data_list.append((
                _utc(row.get('createdAt')),
                _text(row.get('id')),
                _text(row.get('isLocked')),
                _who(row.get('lockingUserId'), names),
                ', '.join(invited),
                _text(endpoint.get('host')) if endpoint else '',
                _text(session.get('id')) if session else '',
                _text(session.get('videoTech')) if session else '',
                _text(session.get('secretVersion')) if session else '',
            ))
            read_any = True
        if read_any:
            sources.append(store)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def housepartyAccount(context):
    data_headers = (
        ('Account Created', 'datetime'),
        ('Signed In At', 'datetime'),
        ('Session Created', 'datetime'),
        ('Session Invalidated', 'datetime'),
        ('Last Backgrounded At', 'datetime'),
        ('Activity Last Seen At', 'datetime'),
        ('Birthday', 'date'),
        'Username',
        'Full Name',
        'Email',
        'Phone',
        'Facebook ID',
        'Account ID',
        'Private Mode',
        'Auto Ghost',
        'Auto Mute',
        'Auto Sneak In',
        'Linked Accounts',
    )
    data_list = []
    sources = []
    for entry, tables in _stores(context):
        store = entry['realm']
        public = _rows(tables, 'class_RealmPublicUser')
        settings_rows = _rows(tables, 'class_RealmUserSettings')
        tokens = _rows(tables, 'class_RealmToken')
        linked_accounts = _rows(tables, 'class_RealmLinkedAccount')
        epic_accounts = _rows(tables, 'class_RealmEpicAccount')
        prefs = {}
        plist = entry.get('plist')
        if plist:
            try:
                prefs = get_plist_file_content(plist) or {}
            except Exception as error:  # pylint: disable=broad-exception-caught
                logfunc(f'Houseparty: {os.path.basename(plist)} did not parse: {error}')
        read_any = False
        for row in _rows(tables, 'class_RealmUser'):
            profile = _linked(public, row.get('publicUser')) or {}
            settings = _linked(settings_rows, row.get('settings')) or {}
            account_id = str(row.get('id') or '')
            token = next((t for t in tokens if str(t.get('userId') or '') == account_id), {})
            invalidated = _utc(token.get('invalidatedAt'))
            # The store writes the Unix epoch to mean "not invalidated".
            if invalidated and invalidated == _EPOCH:
                invalidated = ''
            linked = []
            for link in _linked_all(linked_accounts, row.get('linkedAccounts')):
                epic = _linked(epic_accounts, link.get('epicAccount'))
                if epic:
                    linked.append(str(epic.get('displayName') or epic.get('id') or ''))
            data_list.append((
                _utc(profile.get('createdAt')),
                _plist_dt(prefs.get('SignedInAt')),
                _utc(token.get('createdAt')),
                invalidated,
                _plist_dt(prefs.get('lastBackgroundedAt')),
                _plist_dt(prefs.get('activityLastSeenAt')),
                _date_only(row.get('birthday')),
                _text(profile.get('username')),
                _text(profile.get('fullName')),
                _text(row.get('email')),
                _text(row.get('phone')),
                _text(row.get('facebookId')),
                account_id,
                _text(settings.get('privateMode')),
                _text(settings.get('autoGhost')),
                _text(settings.get('autoMute')),
                _text(settings.get('autoSneakIn')),
                ', '.join(linked),
            ))
            read_any = True
        if read_any:
            sources.append(store)
            if plist and prefs:
                sources.append(plist)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def housepartyContacts(context):
    data_headers = (
        ('Last Seen', 'datetime'),
        ('Latest Interaction At', 'datetime'),
        ('Last Interaction At', 'datetime'),
        ('Last With Someone At', 'datetime'),
        ('Local Last With Someone At', 'datetime'),
        ('Room Created At', 'datetime'),
        ('Created At', 'datetime'),
        'Username',
        'Full Name',
        'Account ID',
        'Address Book Name',
        'Relationship Status (as stored)',
        'Last Interaction Type (as stored)',
        'Presence Type (as stored)',
        'On Phone',
        'Room ID',
        'Room Colour',
        'Notifications Enabled',
        'Ghosting',
        'Active With Someone Minutes',
        'Local Minutes',
        'Relevance Reason (as stored)',
    )
    data_list = []
    sources = []
    for entry, tables in _stores(context):
        store = entry['realm']
        presences = _rows(tables, 'class_RealmUserPresence')
        relationships = _rows(tables, 'class_RealmRelationshipInfo')
        relevances = _rows(tables, 'class_RealmUserRelevance')
        interactions = _rows(tables, 'class_RealmUserInteraction')
        together_rows = _rows(tables, 'class_RealmWithSomeoneData')
        local_rows = _rows(tables, 'class_RealmLocalWithSomeoneData')
        read_any = False
        for row in _rows(tables, 'class_RealmPublicUser'):
            account_id = str(row.get('id') or '')
            presence = _linked(presences, row.get('presence')) or {}
            relationship = _linked(relationships, row.get('relationship'))
            if relationship is None:
                relationship = next((r for r in relationships if str(r.get('userId') or '') == account_id), {})
            relevance = _linked(relevances, row.get('relevance'))
            if relevance is None:
                relevance = next((r for r in relevances if str(r.get('id') or '') == account_id), {})
            interaction = _linked(interactions, relationship.get('lastInteraction')) or {}
            together = _linked(together_rows, relationship.get('withSomeoneData')) or {}
            local = _linked(local_rows, relationship.get('localWithSomeoneData')) or {}
            data_list.append((
                _utc(presence.get('lastSeen')),
                _utc(relationship.get('latestInteractionAt')),
                _utc(interaction.get('happenedAt')),
                _utc(together.get('lastWithSomeoneAt')),
                _utc(local.get('lastWithSomeoneAt')),
                _utc(presence.get('roomCreatedAt')),
                _utc(row.get('createdAt')),
                _text(row.get('username')),
                _text(row.get('fullName')),
                account_id,
                _text(relevance.get('addressBookName')),
                _text(relationship.get('status')),
                _text(interaction.get('interactionType')),
                _text(presence.get('type')),
                _text(presence.get('isOnPhone')),
                _text(presence.get('roomID')),
                _text(presence.get('roomColor')),
                _text(relationship.get('notificationsEnabled')),
                _text(relationship.get('isGhosting')),
                _text(together.get('activeWithSomeoneMinutes')),
                _text(local.get('localMinutes')),
                _text(relevance.get('reason')),
            ))
            read_any = True
        if read_any:
            sources.append(store)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def housepartyPhoneContacts(context):
    data_headers = (
        'Name In Phone',
        'Phone',
        'Phone (as formatted)',
        'Matched Username',
        'Matched Account ID',
        'Score',
        'Invite Sent',
        'Ignored',
        'Suggested',
        'Local Contact ID',
    )
    data_list = []
    sources = []
    for entry, tables in _stores(context):
        store = entry['realm']
        public = _rows(tables, 'class_RealmPublicUser')
        contacts = _rows(tables, 'class_RealmContact')
        locals_ = _rows(tables, 'class_RealmLocalContact')
        # The local contact record lists its numbers by row position, so invert that.
        owner = {}
        for local in locals_:
            for position in (local.get('contacts') or []) if isinstance(local.get('contacts'), list) else []:
                if isinstance(position, int) and not isinstance(position, bool):
                    owner[position] = local
        formatted = {}
        phones = entry.get('phones')
        if phones:
            try:
                for row in _rows(_parse(phones).get('active') or {}, 'class_RealmPhoneNumber'):
                    if row.get('e164'):
                        formatted[str(row['e164'])] = str(row.get('id') or '')
            except Exception as error:  # pylint: disable=broad-exception-caught
                logfunc(f'Houseparty: {os.path.basename(phones)} did not parse: {error}')
                phones = None
        read_any = False
        for position, row in enumerate(contacts):
            local = owner.get(position, {})
            user = _linked(public, row.get('user')) or {}
            number = str(row.get('phone') or '')
            data_list.append((
                _text(row.get('nameInPhone')) or _text(local.get('nameInPhone')),
                number,
                formatted.get(number, ''),
                _text(user.get('username')),
                _text(user.get('id')),
                _text(row.get('score')),
                _text(row.get('inviteSent')),
                _text(row.get('ignored')),
                _text(row.get('suggested')),
                _text(local.get('id')),
            ))
            read_any = True
        if read_any:
            sources.append(store)
            if phones and formatted:
                sources.append(phones)
    return data_headers, data_list, '\n'.join(sources)
