__artifacts_v2__ = {
    'clubhouseAccount': {
        'name': 'Clubhouse - Account Information',
        'description': 'Details of the Clubhouse account signed in on the device',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-31',
        'requirements': 'none',
        'category': 'Clubhouse',
        'notes': '',
        'paths': ('*/mobile/Containers/Data/Application/*/Library/Preferences/co.alphaexploration.clubhouse.plist',),
        'output_types': 'standard',
        'artifact_icon': 'user',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 1 row',
        },
    },
    'clubhouseContacts': {
        'name': 'Clubhouse - Suggested Invites',
        'description': 'Contacts staged in the Clubhouse contact-upload store and offered as suggested invites',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-31',
        'requirements': 'none',
        'category': 'Clubhouse',
        'notes': 'Sourced from the contact-upload-store-suggested-invites key, which holds contacts staged in the app contact-upload store (drawn from the device address book per the cnContactIdentifier keys).',
        'paths': ('*/mobile/Containers/Data/Application/*/Library/Preferences/co.alphaexploration.clubhouse.plist',),
        'output_types': 'standard',
        'artifact_icon': 'address-book',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 7 rows',
        },
    },
    'clubhouseConversations': {
        'name': 'Clubhouse - Conversations',
        'description': 'Recent Clubhouse conversations cached for the home screen widget',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-31',
        'requirements': 'none',
        'category': 'Clubhouse',
        'notes': 'Only participant names/IDs were present in the examined widget cache; message bodies were not observed in this store.',
        'paths': ('*/mobile/Containers/Shared/AppGroup/*/Library/Preferences/group.alphaexploration.clubhouse.plist',),
        'output_types': 'standard',
        'artifact_icon': 'messages',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 1 row',
        },
    },
    'clubhouseNotifications': {
        'name': 'Clubhouse - Received Notifications',
        'description': 'Identifiers and timestamps of push notifications received by Clubhouse',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-25',
        'requirements': 'none',
        'category': 'Clubhouse',
        'notes': '',
        'paths': ('*/mobile/Containers/Shared/AppGroup/*/Library/Preferences/group.alphaexploration.clubhouse.plist',),
        'output_types': 'standard',
        'artifact_icon': 'bell',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 1 row',
        },
    },
}

import json

from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_plist_file_content, convert_unix_ts_to_utc, \
    convert_cocoa_core_data_ts_to_utc

# Account fields worth reporting from the application preferences, in the order
# they should appear in the output.
ACCOUNT_FIELDS = (
    ('kStorageKeyMyName', 'Name'),
    ('kStorageKeyMyUsername', 'Username'),
    ('kStorageKeyUserServerId', 'User Server ID'),
    ('kStorageKeyPhoneNumber', 'Phone Number'),
    ('kStorageKeyMyPhotoUrl', 'Photo URL'),
    ('kStorageKeyDeviceId', 'Device ID'),
    ('kStorageKeyMyIsAdmin', 'Is Admin'),
    ('kStorageKeyNumInvites', 'Num Invites'),
    ('kNumCofollows', 'Co-follows'),
    ('kIsBlindInviteUser', 'Blind Invite User'),
    ('kStorageKeyIsUpgradedFromV1', 'Upgraded From V1'),
    ('kStorageKeyUserHasSeenOnboarding', 'Has Seen Onboarding'),
)


@artifact_processor
def clubhouseAccount(context):
    source_path = get_file_path(context.get_files_found(), 'co.alphaexploration.clubhouse.plist')
    data_list = []
    data_headers = (
        'Name', 'Username', 'User Server ID', ('Phone Number', 'phonenumber'),
        'Photo URL', 'Device ID', 'Is Admin', 'Num Invites', 'Co-follows',
        'Blind Invite User', 'Upgraded From V1', 'Has Seen Onboarding',
        ('Last Sync', 'datetime'), 'Following User IDs', 'Blocked User IDs')
    if not source_path:
        return data_headers, data_list, ''

    plist = get_plist_file_content(source_path) or {}

    following = plist.get('kCachedFollowing') or []
    blocked = plist.get('kCachedBlocked') or {}
    last_sync = plist.get('kLastSyncDate')

    row = [plist.get(key, '') for key, _ in ACCOUNT_FIELDS]
    row.append(last_sync.isoformat(sep=' ') if hasattr(last_sync, 'isoformat') else '')
    row.append(', '.join(str(i) for i in following))
    row.append(', '.join(str(i) for i in blocked))

    data_list.append(tuple(row))

    return data_headers, data_list, source_path


@artifact_processor
def clubhouseContacts(context):
    source_path = get_file_path(context.get_files_found(), 'co.alphaexploration.clubhouse.plist')
    data_list = []
    data_headers = (
        ('Store Last Updated', 'datetime'), 'Name', ('Phone Number', 'phonenumber'),
        'In App', 'pop (score)', 'Address Book Identifier',
        'Contact Hash', 'Image Path')
    if not source_path:
        return data_headers, data_list, ''

    plist = get_plist_file_content(source_path) or {}
    raw = plist.get('contact-upload-store-suggested-invites')
    if not raw:
        return data_headers, data_list, source_path

    try:
        store = json.loads(raw)
    except (ValueError, TypeError):
        return data_headers, data_list, source_path

    # lastUpdated is a Core Data (Cocoa) reference timestamp, not Unix epoch.
    last_updated = store.get('lastUpdated')
    uploaded = convert_cocoa_core_data_ts_to_utc(last_updated) if last_updated else ''

    for invite in store.get('suggestedInvites', []):
        if not isinstance(invite, dict):
            continue
        data_list.append((
            uploaded,
            invite.get('name'),
            invite.get('phoneNumber'),
            'Yes' if invite.get('inApp') else '',
            invite.get('pop'),
            invite.get('cnContactIdentifier'),
            invite.get('hash'),
            invite.get('imagePath'),
        ))

    return data_headers, data_list, source_path


@artifact_processor
def clubhouseConversations(context):
    source_path = get_file_path(context.get_files_found(), 'group.alphaexploration.clubhouse.plist')
    data_list = []
    data_headers = ('Participant Name', 'Conversation ID', 'Image URL')
    if not source_path:
        return data_headers, data_list, ''

    plist = get_plist_file_content(source_path) or {}
    raw = plist.get('widgetConversations')
    if not raw:
        return data_headers, data_list, source_path

    try:
        conversations = json.loads(raw)
    except (ValueError, TypeError):
        return data_headers, data_list, source_path

    for conversation in conversations:
        if not isinstance(conversation, dict):
            continue
        data_list.append((
            conversation.get('name'),
            conversation.get('id'),
            conversation.get('imageUrl'),
        ))

    return data_headers, data_list, source_path


@artifact_processor
def clubhouseNotifications(context):
    source_path = get_file_path(context.get_files_found(), 'group.alphaexploration.clubhouse.plist')
    data_list = []
    data_headers = (('Timestamp', 'datetime'), 'Notification ID')
    if not source_path:
        return data_headers, data_list, ''

    plist = get_plist_file_content(source_path) or {}
    ids = plist.get('notification_received_ids') or []
    timestamps = plist.get('notification_received_timestamps') or []

    # The two arrays are positional; pair them up and tolerate a length mismatch.
    for index, notification_id in enumerate(ids):
        timestamp = timestamps[index] if index < len(timestamps) else None
        data_list.append((
            convert_unix_ts_to_utc(float(timestamp)) if timestamp else '',
            notification_id,
        ))

    return data_headers, data_list, source_path
