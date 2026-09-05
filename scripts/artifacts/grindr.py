__artifacts_v2__ = {
    "grindr_messages": {
        "name": "Grindr - Messages",
        "description": "Parses the chat messages the Grindr iOS app stored, with the "
                       "direction of each, the other party and the message text.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Grindr",
        "notes": "One row per message. The app stores its data in a Realm database named "
                 "PersistenceStore.bin, read here with the reader in scripts/realm_parser.py; "
                 "the file carries Realm's own T-DB header rather than a realm extension, so "
                 "it is matched by path rather than by name. An iOS data container is "
                 "named with a UUID, so the declared path carries no app name and a store "
                 "is accepted only when the Realm declares one of this app's own classes; "
                 "a Realm that declares none is logged and skipped rather than reported, so "
                 "another app using the same directory layout cannot be reported as this "
                 "one. The account the store belongs to "
                 "is the name of the directory holding it, which is how Account is filled and "
                 "how Direction is decided: a message whose source is that account is "
                 "outgoing and one whose target is that account is incoming. On the tested "
                 "device those two accounted for every message, 60 outgoing and 69 incoming "
                 "of 129, so no message was left undecided. Timestamps are rendered by the "
                 "Realm reader from the stored date. Type, Subtype, State, Source Type and "
                 "Found You Via are reported as stored, because the extraction carries no app "
                 "binary and nothing in it maps those integers to a meaning. Media Hash is "
                 "the reference the message carries and 23 of the 129 carried one, but the "
                 "bytes are not in the extraction: the app's media table marked 3,704 of its "
                 "3,705 entries as not local, no file in the container is named after a hash, "
                 "and that table also holds marketing image addresses, so no media column is "
                 "offered and nothing is rendered. Field mapping was done against a private "
                 "sample provided by Mattia; no sample data is recorded for it.",
        "paths": ('*/Documents/DataContainer/Data/*/PersistenceStore.bin',),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "data_views": {
            "conversation": {
                "directionSentValue": "Outgoing",
                "conversationDiscriminatorColumn": "Other Party ID",
                "conversationLabelColumn": "Other Party ID",
                "directionColumn": "Direction",
                "senderColumn": "Sender ID",
                "textColumn": "Message",
                "timeColumn": "Timestamp",
            }
        },
        "artifact_icon": "message-circle"
    },
    "grindr_conversations": {
        "name": "Grindr - Conversations",
        "description": "Parses the Grindr iOS conversation records, with the other party, "
                       "the unread count and any unsent draft message.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Grindr",
        "notes": "One row per conversation record in the app's Realm database. This record holds no message text; the messages themselves are reported by the messages artifact and a conversation links to them. Messages Linked, Tap Messages Linked and Members Linked are the lengths of those link lists, which is what lets a conversation be sized without opening it. On the tested device they totalled 118 message links across 17 conversations and 9 tap links across 9, against 129 rows in the messages artifact, so the two do not reconcile exactly and a message can be present without a conversation linking it. Draft Message is unsent draft text, and Name is a conversation name; both were empty on every row of the tested device and are carried because either one is significant wherever it is populated. Pinned, Muted and Unread Count are the values the record carries. Type is reported as stored. Some conversation records are created by the app's marketing framework rather than by a person: their identifiers carry that framework's name, and the Marketing column marks them so they are not read as conversations with another user. Field mapping was done against a private sample provided by Mattia; no sample data is recorded for it.",
        "paths": ('*/Documents/DataContainer/Data/*/PersistenceStore.bin',),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "users"
    },
    "grindr_profiles": {
        "name": "Grindr - Cached Profiles",
        "description": "Parses the profiles of other people that the Grindr iOS app cached, "
                       "including the attributes each profile recorded.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Grindr",
        "notes": "One row per cached profile. **These are profiles the app received, not "
                 "profiles the account holder chose to look at.** The app's own session "
                 "preferences keep a list it calls a cascade cache, which is the grid of "
                 "nearby profiles the service delivers, and on the tested device the store "
                 "held 2,178 profiles against 23 conversations, so the presence of a profile "
                 "is not evidence of contact. Columns that do record an interaction are "
                 "reported separately: Favourite was set on 1 profile and Last Viewed Me on "
                 "1,634. Last Chat Date is the value the profile record carries and was "
                 "populated on 1,869 profiles, far more than the account had conversations "
                 "with, so it is reported as stored and must not be read as a chat with this "
                 "account. Distance is the value the record carries, populated on 382 "
                 "profiles, and describes where the profile was relative to the device when "
                 "the app received it. Ethnicity, Body Type, Relationship Status, Sexual "
                 "Position, HIV Status and the tribe, meeting and looking-for sets are "
                 "integer codes or code sets and are reported as stored: the extraction "
                 "carries no app binary and nothing in it maps them to a meaning. Field "
                 "mapping was done against a private sample provided by Mattia; no sample "
                 "data is recorded for it.",
        "paths": ('*/Documents/DataContainer/Data/*/PersistenceStore.bin',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user"
    },
    "grindr_account": {
        "name": "Grindr - Account and Settings",
        "description": "Parses the Grindr iOS account identifier and the app's own session "
                       "and device settings, including the consent list it records.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Grindr",
        "notes": "One row per account. The identifier is read from the name of the "
                 "preference file the app writes per account and from the directory holding "
                 "that account's database, which agreed on the tested device. Consents is the "
                 "list the app records against the account, as stored. The remaining values "
                 "are settings the app keeps for itself and are reported as stored. A second "
                 "account directory named entirely with zeros is present on the tested "
                 "device and holds no messages, conversations or profiles; it is reported "
                 "when found because its presence is a fact about the device, and its empty "
                 "counts say what it holds. Field mapping was done against a private sample "
                 "provided by Mattia; no sample data is recorded for it.",
        "paths": (
            '*/Documents/DataContainer/Data/*/PersistenceStore.bin',
            '*/Library/Application Support/Preferences/com.grindrguy.grindrx.*.plist',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user-check"
    },
}

import os
import plistlib

from scripts.realm_parser import parse_realm_file, realm_rows
from scripts.ilapfuncs import artifact_processor, logfunc

_STORE = 'PersistenceStore.bin'
_MARKETING = 'braze'


def _account_of(path):
    '''The account identifier the store belongs to, from its parent directory name.

    The app keeps one database per signed in account under a directory named with that
    account's identifier, so the directory is recorded identity rather than a value this
    module infers.
    '''
    return os.path.basename(os.path.dirname(str(path)))


def _container_of(path):
    '''A key for the app data container a matched file belongs to.

    Two accounts live in one container as sibling directories, and one device can hold more
    than one container, so every index below is keyed on the container together with the
    account rather than on the account alone.
    '''
    parts = str(path).replace('\\', '/').split('/')
    # The database sits under Documents and the preferences under Library, so the container
    # is the directory holding both. Cutting at the first of those names resolves a store
    # and a preference file in one container to the same key, which keying on either
    # subtree alone does not.
    for position, part in enumerate(parts):
        if part in ('Documents', 'Library'):
            return '/'.join(parts[:position])
    return os.path.dirname(os.path.dirname(str(path)))


# Classes only this app defines. The declared path carries no app name, because an iOS
# data container is named with a UUID, so a store is accepted only when it declares one of
# these. A store that does not is skipped rather than reported, which fails closed: another
# app using the same directory layout cannot be reported as this one.
_OWN_CLASSES = ('class_GRChatMessage', 'class_GRConversation', 'class_GRProfile')


def _is_own_store(path):
    '''Whether a Realm database declares this app's own classes.'''
    try:
        parsed = parse_realm_file(path)
    except Exception as ex:                      # pylint: disable=broad-except
        logfunc(f'Grindr: could not read {os.path.basename(path)} as a Realm database: {ex}')
        return False
    for section in ('active', 'inactive'):
        tables = parsed.get(section) or {}
        if any(name in tables for name in _OWN_CLASSES):
            return True
    logfunc(f'Grindr: {os.path.basename(path)} is a Realm database but declares none of this '
            "app's classes, so it was skipped")
    return False


def _stores(files_found):
    '''Every Grindr Realm database among the matched files.'''
    return [str(f) for f in files_found
            if os.path.basename(str(f)) == _STORE and _is_own_store(str(f))]


def _rows(path, table):
    '''The rows of one Realm table, or nothing when it is absent.

    A table missing from an older or newer release is logged and yields nothing, so a
    schema change costs the artifact that table rather than every row it would return.
    '''
    try:
        return list(realm_rows(path, table))
    except Exception as ex:                      # pylint: disable=broad-except
        logfunc(f'Grindr: could not read {table} from {os.path.basename(path)}: {ex}')
        return []


def _text(value):
    '''A stored value as text, with a stored null read as absent.'''
    return '' if value is None else str(value)


def _links(value):
    '''The number of entries in a Realm link list, or '' when the column is absent.

    The list holds the store's own row references rather than values, so only its length
    is reported: the count is a fact about the record, while resolving the references to
    rows is not something this artifact does.
    '''
    if isinstance(value, list):
        return len(value)
    return ''


def _is_marketing(value):
    '''Whether an identifier was created by the app's marketing framework.'''
    return _MARKETING in str(value or '').lower()


@artifact_processor
def grindr_messages(context):
    data_list = []
    source_files = []

    for path in _stores(context.get_files_found()):
        account = _account_of(path)
        relative = context.get_relative_path(path)
        rows = _rows(path, 'class_GRChatMessage')
        if not rows:
            continue
        source_files.append(relative)
        for row in rows:
            source = _text(row.get('sourceID'))
            target = _text(row.get('targetID'))
            if source == account:
                direction, other = 'Outgoing', target
            elif target == account:
                direction, other = 'Incoming', source
            else:
                direction, other = '', target or source
            data_list.append((
                _text(row.get('timestamp')),
                _text(row.get('sendTimestamp')),
                direction,
                source,
                other,
                _text(row.get('text')),
                _text(row.get('translation')),
                _text(row.get('read')),
                _text(row.get('mediaHash')),
                _text(row.get('type')),
                _text(row.get('subType')),
                _text(row.get('state')),
                _text(row.get('sourceType')),
                _text(row.get('foundYouVia')),
                _text(row.get('tapSubType')),
                _text(row.get('replyMessage')),
                _text(row.get('albumId')),
                _text(row.get('countryCode')),
                _text(row.get('groupID')),
                _text(row.get('ID')),
                account,
                relative,
            ))

    data_list.sort(key=lambda r: (str(r[0]), str(r[19])), reverse=True)

    data_headers = (
        ('Timestamp', 'datetime'),
        ('Send Timestamp', 'datetime'),
        'Direction',
        'Sender ID',
        'Other Party ID',
        'Message',
        'Translation',
        'Read (as stored)',
        'Media Hash',
        'Type (as stored)',
        'Subtype (as stored)',
        'State (as stored)',
        'Source Type (as stored)',
        'Found You Via (as stored)',
        'Tap Subtype (as stored)',
        'Reply To',
        'Album ID',
        'Country Code',
        'Group ID',
        'Message ID',
        'Account',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def grindr_conversations(context):
    data_list = []
    source_files = []

    for path in _stores(context.get_files_found()):
        account = _account_of(path)
        relative = context.get_relative_path(path)
        rows = _rows(path, 'class_GRConversation')
        if not rows:
            continue
        source_files.append(relative)
        for row in rows:
            identifier = _text(row.get('ID'))
            data_list.append((
                _text(row.get('timestamp')),
                _text(row.get('createTimestamp')),
                _text(row.get('tapTimestamp')),
                _text(row.get('pinTimestamp')),
                _text(row.get('oppositeProfileID')),
                _text(row.get('name')),
                _text(row.get('draftMessage')),
                _text(row.get('unreadCount')),
                _links(row.get('messages')),
                _links(row.get('tapMessages')),
                _links(row.get('members')),
                _text(row.get('hasMessages')),
                _text(row.get('hasTapMessages')),
                _text(row.get('pinned')),
                _text(row.get('muteNotifications')),
                _text(row.get('stickyOnTop')),
                _text(row.get('type')),
                'Yes' if _is_marketing(identifier) else '',
                _text(row.get('lastMessageID')),
                _text(row.get('serverID')),
                identifier,
                account,
                relative,
            ))

    data_list.sort(key=lambda r: (str(r[0]), str(r[20])), reverse=True)

    data_headers = (
        ('Last Activity', 'datetime'),
        ('Created', 'datetime'),
        ('Tap Timestamp', 'datetime'),
        ('Pinned Timestamp', 'datetime'),
        'Other Profile ID',
        'Name',
        'Draft Message',
        'Unread Count',
        'Messages Linked',
        'Tap Messages Linked',
        'Members Linked',
        'Has Messages',
        'Has Tap Messages',
        'Pinned',
        'Muted',
        'Sticky On Top',
        'Type (as stored)',
        'Marketing Record',
        'Last Message ID',
        'Server ID',
        'Conversation ID',
        'Account',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def grindr_profiles(context):
    data_list = []
    source_files = []

    for path in _stores(context.get_files_found()):
        account = _account_of(path)
        relative = context.get_relative_path(path)
        rows = _rows(path, 'class_GRProfile')
        if not rows:
            continue
        source_files.append(relative)
        for row in rows:
            data_list.append((
                _text(row.get('lastSeen')),
                _text(row.get('lastViewedMe')),
                _text(row.get('lastChatDate')),
                _text(row.get('lastServerUpdatedDate')),
                _text(row.get('ID')),
                _text(row.get('name')),
                _text(row.get('age')),
                _text(row.get('aboutMe')),
                _text(row.get('distance')),
                _text(row.get('heightInCm')),
                _text(row.get('weightInGrams')),
                _text(row.get('ethnicity')),
                _text(row.get('bodyType')),
                _text(row.get('relationshipStatus')),
                _text(row.get('sexualPosition')),
                _text(row.get('HIVStatus')),
                _text(row.get('genderDetails')),
                _text(row.get('preferredPronoun')),
                _text(row.get('lookingForSet')),
                _text(row.get('meetAtSet')),
                _text(row.get('tribesSet')),
                _text(row.get('acceptNSFWPics')),
                _text(row.get('hashtagKeys')),
                _text(row.get('socialNetworks')),
                _text(row.get('__favorite')),
                _text(row.get('isNew')),
                _text(row.get('mediaHash')),
                account,
                relative,
            ))

    data_list.sort(key=lambda r: (str(r[0]), str(r[4])), reverse=True)

    data_headers = (
        ('Last Seen', 'datetime'),
        ('Last Viewed Me', 'datetime'),
        ('Last Chat Date (as stored)', 'datetime'),
        ('Last Server Update', 'datetime'),
        'Profile ID',
        'Name',
        'Age',
        'About Me',
        'Distance (as stored)',
        'Height cm',
        'Weight g',
        'Ethnicity (as stored)',
        'Body Type (as stored)',
        'Relationship Status (as stored)',
        'Sexual Position (as stored)',
        'HIV Status (as stored)',
        'Gender Details (as stored)',
        'Preferred Pronoun (as stored)',
        'Looking For (as stored)',
        'Meet At (as stored)',
        'Tribes (as stored)',
        'Accept NSFW Pics (as stored)',
        'Hashtag Keys (as stored)',
        'Social Networks (as stored)',
        'Favourite',
        'Is New',
        'Media Hash',
        'Account',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def grindr_account(context):
    data_list = []
    source_files = []

    files = [str(f) for f in context.get_files_found()]
    # Preferences are indexed per container, so one container's settings cannot be
    # reported against another container's account.
    settings = {}
    for path in files:
        name = os.path.basename(path)
        if not name.startswith('com.grindrguy.grindrx.') or not name.endswith('.plist'):
            continue
        try:
            with open(path, 'rb') as handle:
                settings.setdefault(_container_of(path), {})[name] = plistlib.load(handle)
        except (OSError, plistlib.InvalidFileException) as ex:
            logfunc(f'Grindr: could not read {name}: {ex}')

    for path in _stores(files):
        account = _account_of(path)
        container = _container_of(path)
        relative = context.get_relative_path(path)
        per_container = settings.get(container, {})
        session = per_container.get('com.grindrguy.grindrx.session.plist', {})
        device = per_container.get('com.grindrguy.grindrx.device.plist', {})
        profile = per_container.get(f'com.grindrguy.grindrx.profile.{account}.plist', {})

        agreement = session.get('agreement') if isinstance(session.get('agreement'), dict) else {}
        chat = session.get('chat') if isinstance(session.get('chat'), dict) else {}
        app = session.get('app') if isinstance(session.get('app'), dict) else {}
        device_app = device.get('app') if isinstance(device.get('app'), dict) else {}

        source_files.append(relative)
        data_list.append((
            account,
            'Yes' if profile else '',
            len(_rows(path, 'class_GRChatMessage')),
            len(_rows(path, 'class_GRConversation')),
            len(_rows(path, 'class_GRProfile')),
            '; '.join(str(v) for v in (agreement.get('userConsentList') or [])),
            _text(app.get('lastAcceptedPrivacyPolicy')),
            _text(chat.get('hasSentAMessage')),
            _text(device_app.get('disableAppearingInRemoteSearch')),
            relative,
        ))

    data_headers = (
        'Account',
        'Has Per Account Preferences',
        'Messages',
        'Conversations',
        'Cached Profiles',
        'Consents (as stored)',
        'Last Accepted Privacy Policy (as stored)',
        'Has Sent A Message (as stored)',
        'Disable Appearing In Remote Search (as stored)',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))
