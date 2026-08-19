__artifacts_v2__ = {
    'groupMeMessages': {
        'name': 'GroupMe - Messages',
        'description': 'Direct and group messages, attachments and shared locations from GroupMe',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-08-18',
        'requirements': 'none',
        'category': 'GroupMe',
        'notes': 'Deletion Status Recorded, System Deleted and Deletion Actor (as stored) '
                 'come from ZGMMESSAGE.ZMESSAGEDELETIONSTATUS, an NSKeyedArchiver archive '
                 'of a GMMessageDeletionStatus object whose keys are isSystemDeleted and '
                 'deletionActor. In the tested images the column is populated only on '
                 'rows whose stored message text is the deleted-message placeholder, and '
                 'ZHIDDEN is 0 on every one of them, so the Hidden column does not '
                 'identify these rows. The value domain of deletionActor is not '
                 'documented, so it is reported as stored. The app binary types the '
                 'property as a signed integer and declares the enum '
                 'GroupMe.MessageDeletionStatus.DeletionActor with three cases and no '
                 'payloads, but its case names are absent from the reflection metadata of '
                 'the shipped binary, so the mapping is not recoverable from it '
                 '(GroupMe.app/GroupMe, com.groupme.iphone-app 6.102.4). The separate '
                 'three-case enum GroupMe.MessageDeletionMode (senderAndAdmin, admin, '
                 'nobody) is the deletion permission setting and is not this column. '
                 'Older stores lack the column and are read as NULL, observed on an iOS '
                 '14.3 image; on an iOS 15.3.1 image the archived object carries '
                 'isSystemDeleted with no deletionActor key.',
        'paths': (
            '*/mobile/Containers/Data/Application/*/Library/Application Support/GroupMe.sqlite*',
            '*/mobile/Containers/Data/Application/*/Documents/GroupMe.sqlite*',
            '*/mobile/Containers/Data/Application/*/Library/Preferences/com.groupme.iphone-app.plist',
        ),
        'output_types': 'all',
        'artifact_icon': 'message',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 146 rows across 3 conversations; 1 hidden message and 4 carrying a deletion status record (deletionActor 0, isSystemDeleted false)',
            'hickman_ios15': 'iOS 15.3.1 | 66 rows across 2 conversations; 3 carrying a deletion status record that archives isSystemDeleted with no deletionActor key',
            'hickman_ios14': 'iOS 14.3 | 14 rows in 1 conversation; ZMESSAGEDELETIONSTATUS absent from this store and read as NULL',
        },
        'data_views': {
            'conversation': {
                'conversationDiscriminatorColumn': 'Chat ID',
                'conversationLabelColumn': 'Conversation',
                'textColumn': 'Message',
                'directionColumn': 'From Me',
                'directionSentValue': 1,
                'timeColumn': 'Timestamp',
                'senderColumn': 'Sender',
            }
        }
    },
    'groupMeChats': {
        'name': 'GroupMe - Chats',
        'description': 'Direct message threads and groups known to the GroupMe application',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-08-18',
        'requirements': 'none',
        'category': 'GroupMe',
        'notes': '',
        'paths': (
            '*/mobile/Containers/Data/Application/*/Library/Application Support/GroupMe.sqlite*',
            '*/mobile/Containers/Data/Application/*/Documents/GroupMe.sqlite*',
        ),
        'output_types': 'standard',
        'artifact_icon': 'users-group',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 15 rows (13 direct message, 2 group)',
            'hickman_ios15': 'iOS 15.3.1 | 12 rows',
            'hickman_ios14': 'iOS 14.3 | 1 row',
        },
    },
    'groupMeGroupMembers': {
        'name': 'GroupMe - Group Members',
        'description': 'Members of the GroupMe groups the account belongs to',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-08-18',
        'requirements': 'none',
        'category': 'GroupMe',
        'notes': '',
        'paths': (
            '*/mobile/Containers/Data/Application/*/Library/Application Support/GroupMe.sqlite*',
            '*/mobile/Containers/Data/Application/*/Documents/GroupMe.sqlite*',
        ),
        'output_types': 'standard',
        'artifact_icon': 'users',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 5 rows',
            'hickman_ios15': 'iOS 15.3.1 | 2 rows',
            'hickman_ios14': 'iOS 14.3 | 2 rows',
        },
    },
    'groupMeContacts': {
        'name': 'GroupMe - Contacts',
        'description': 'Contacts and relationships stored by the GroupMe application',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-08-18',
        'requirements': 'none',
        'category': 'GroupMe',
        'notes': '',
        'paths': (
            '*/mobile/Containers/Data/Application/*/Library/Application Support/GroupMe.sqlite*',
            '*/mobile/Containers/Data/Application/*/Documents/GroupMe.sqlite*',
        ),
        'output_types': 'standard',
        'artifact_icon': 'address-book',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 14 rows',
            'hickman_ios15': 'iOS 15.3.1 | 2 rows',
            'hickman_ios14': 'iOS 14.3 | 1 row',
        },
    },
    'groupMeAccount': {
        'name': 'GroupMe - Account Information',
        'description': 'Local GroupMe account details from the application preferences',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-08-18',
        'requirements': 'none',
        'category': 'GroupMe',
        'notes': '',
        'paths': ('*/mobile/Containers/Data/Application/*/Library/Preferences/com.groupme.iphone-app.plist',),
        'output_types': 'standard',
        'artifact_icon': 'user',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 13 rows',
            'hickman_ios15': 'iOS 15.3.1 | 11 rows',
            'hickman_ios14': 'iOS 14.3 | 10 rows',
        },
    },
}

import plistlib

from scripts.ilapfuncs import artifact_processor, logfunc, \
    get_file_path, get_plist_content, get_plist_file_content, get_sqlite_db_records, \
    convert_cocoa_core_data_ts_to_utc, null_absent_columns

# Z_ENT values from Z_PRIMARYKEY. GroupMe keeps direct messages and group
# messages in the same ZGMMESSAGE table and tells them apart by entity.
ENTITY_DIRECT_MESSAGE = 15
ENTITY_GROUP_LINE = 16

# Account keys worth surfacing from the preferences plist. The plist also holds
# a large amount of SDK/telemetry noise which is deliberately left out.
ACCOUNT_KEYS = (
    ('userId', 'User ID'),
    ('GMAppVersion', 'App Version'),
    ('GMLastChatViewed', 'Last Chat Viewed'),
    ('GMTimeLastDidFullRefresh', 'Last Full Refresh'),
    ('kLastScannedAddressBook', 'Address Book Last Scanned'),
    ('lastFetchedRelationships', 'Relationships Last Fetched'),
    ('userProfileLastRefresh', 'Profile Last Refreshed'),
    ('syncContactsToServer', 'Sync Contacts To Server'),
    ('apnsId', 'APNS ID'),
)

# Resolves both direct messages (ZUSER) and group lines (ZGROUP) to ZGMCHAT.
CHAT_JOIN = 'LEFT JOIN ZGMCHAT c ON c.Z_PK = COALESCE(m.ZGROUP, m.ZUSER)'


def _get_local_user_id(files_found):
    """Read the signed-in GroupMe user ID from the application preferences.

    Message rows carry the sender's user ID but no direction flag, so the local
    user ID is what makes 'From Me' possible. Returns None when the preferences
    plist was not collected, in which case direction is left blank rather than
    guessed.
    """
    plist_path = get_file_path(files_found, 'com.groupme.iphone-app.plist')
    if not plist_path:
        return None
    try:
        plist = get_plist_file_content(plist_path)
    except (plistlib.InvalidFileException, OSError, ValueError) as ex:
        logfunc(f'Could not read GroupMe preferences plist: {ex}')
        return None
    user_id = plist.get('userId') if plist else None
    return str(user_id) if user_id is not None else None


def _decode_deletion_status(blob):
    """Unpack a ZMESSAGEDELETIONSTATUS archive into its two stored values.

    The column holds an NSKeyedArchiver archive of a GMMessageDeletionStatus
    object. Returns (recorded, isSystemDeleted, deletionActor), where recorded
    says a status object was stored at all. Either key can be absent: an iOS 15
    store archives isSystemDeleted on its own, so a missing key is reported
    empty rather than as a value.
    """
    if not blob:
        return '', '', ''
    status = get_plist_content(blob)
    if not isinstance(status, dict):
        return '', '', ''
    system_deleted = status.get('isSystemDeleted')
    actor = status.get('deletionActor')
    return (
        'Yes',
        '' if system_deleted is None else ('Yes' if system_deleted else 'No'),
        '' if actor is None else actor,
    )


@artifact_processor
def groupMeMessages(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'GroupMe.sqlite')
    data_list = []

    local_user_id = _get_local_user_id(files_found)
    if local_user_id is None:
        logfunc('GroupMe preferences plist not found; message direction will be blank.')

    query = f'''
    SELECT
        m.ZCREATEDAT,
        m.Z_ENT,
        m.ZNAME AS senderName,
        m.ZUSERID AS senderId,
        m.ZMESSAGE AS message,
        m.ZSYSTEM AS isSystem,
        m.ZHIDDEN AS isHidden,
        m.ZFAVORITEDBY AS favoritedBy,
        m.ZMESSAGEDELETIONSTATUS AS deletionStatus,
        m.ZREPLYMESSAGEID AS replyMessageId,
        m.ZSOURCEGUID AS sourceGuid,
        COALESCE(m.ZDIRECTMESSAGEID, m.ZLINEID) AS messageId,
        c.Z_PK AS chatRowId,
        c.ZNAME AS chatName,
        c.ZCHATTYPE AS chatType,
        c.ZCHATID AS chatId,
        (SELECT GROUP_CONCAT(a.ZTYPE, ', ') FROM ZGMATTACHMENT a
          WHERE a.ZMESSAGE = m.Z_PK) AS attachmentType,
        (SELECT GROUP_CONCAT(COALESCE(a.ZURL, a.ZFILENAME), ', ') FROM ZGMATTACHMENT a
          WHERE a.ZMESSAGE = m.Z_PK AND COALESCE(a.ZURL, a.ZFILENAME) IS NOT NULL) AS attachmentUrl,
        (SELECT GROUP_CONCAT(a.ZLAT, ', ') FROM ZGMATTACHMENT a
          WHERE a.ZMESSAGE = m.Z_PK AND a.ZTYPE = 'location') AS latitude,
        (SELECT GROUP_CONCAT(a.ZLNG, ', ') FROM ZGMATTACHMENT a
          WHERE a.ZMESSAGE = m.Z_PK AND a.ZTYPE = 'location') AS longitude,
        (SELECT GROUP_CONCAT(a.ZVENUENAME, ', ') FROM ZGMATTACHMENT a
          WHERE a.ZMESSAGE = m.Z_PK AND a.ZTYPE = 'location') AS venueName
    FROM ZGMMESSAGE m
    {CHAT_JOIN}
    ORDER BY m.ZCREATEDAT
    '''

    for record in get_sqlite_db_records(source_path, null_absent_columns(source_path, query)):
        sender_id = record['senderId']
        if local_user_id is not None and not record['isSystem']:
            from_me = 1 if str(sender_id) == local_user_id else 0
        else:
            from_me = ''

        chat_type = record['chatType']
        conversation = record['chatName'] or record['chatId'] or ''

        # Only location attachments carry real coordinates; every other type
        # stores 0.0/0.0, which would litter the map output with null island.
        latitude = record['latitude'] if record['latitude'] is not None else ''
        longitude = record['longitude'] if record['longitude'] is not None else ''

        deletion_recorded, system_deleted, deletion_actor = \
            _decode_deletion_status(record['deletionStatus'])

        data_list.append((
            convert_cocoa_core_data_ts_to_utc(record['ZCREATEDAT']),
            from_me,
            record['senderName'],
            conversation,
            record['message'],
            record['chatId'],
            'Group' if chat_type == 'group' else 'Direct Message',
            sender_id,
            record['attachmentType'],
            record['attachmentUrl'],
            record['venueName'],
            latitude,
            longitude,
            'Yes' if record['isSystem'] else '',
            'Yes' if record['isHidden'] else '',
            deletion_recorded,
            system_deleted,
            deletion_actor,
            'Yes' if record['favoritedBy'] else '',
            record['replyMessageId'],
            record['messageId'],
            record['sourceGuid'],
        ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'From Me',
        'Sender',
        'Conversation',
        'Message',
        'Chat ID',
        'Chat Type',
        'Sender ID',
        'Attachment Type',
        'Attachment',
        'Venue Name',
        'Latitude',
        'Longitude',
        'System Message',
        'Hidden',
        'Deletion Status Recorded',
        'System Deleted',
        'Deletion Actor (as stored)',
        'Favorited By',
        'Reply To Message ID',
        'Message ID',
        'Source GUID',
    )

    return data_headers, data_list, source_path


@artifact_processor
def groupMeChats(context):
    source_path = get_file_path(context.get_files_found(), 'GroupMe.sqlite')
    data_list = []

    query = '''
    SELECT
        c.ZCREATEDAT,
        c.ZUPDATEDAT,
        c.ZLASTMESSAGEDATE,
        c.ZLASTVIEWED,
        c.ZNAME AS chatName,
        c.ZCHATID AS chatId,
        c.ZCHATTYPE AS chatType,
        c.ZGROUPTYPE AS groupType,
        c.ZGROUPDESCRIPTION AS groupDescription,
        c.ZUSERID AS otherUserId,
        c.ZCREATORID AS creatorId,
        c.ZUNREADCOUNT AS unreadCount,
        c.ZMUTED AS muted,
        c.ZHIDDEN AS hidden,
        c.ZSHAREURL AS shareUrl,
        c.ZAVATARURL AS avatarUrl,
        (SELECT COUNT(*) FROM ZGMMESSAGE m
          WHERE COALESCE(m.ZGROUP, m.ZUSER) = c.Z_PK) AS messageCount
    FROM ZGMCHAT c
    ORDER BY c.ZLASTMESSAGEDATE
    '''

    for record in get_sqlite_db_records(source_path, query):
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(record['ZCREATEDAT']) if record['ZCREATEDAT'] else '',
            convert_cocoa_core_data_ts_to_utc(record['ZLASTMESSAGEDATE']) if record['ZLASTMESSAGEDATE'] else '',
            convert_cocoa_core_data_ts_to_utc(record['ZLASTVIEWED']) if record['ZLASTVIEWED'] else '',
            record['chatName'],
            record['chatId'],
            'Group' if record['chatType'] == 'group' else 'Direct Message',
            record['groupType'],
            record['groupDescription'],
            record['otherUserId'],
            record['creatorId'],
            record['messageCount'],
            record['unreadCount'],
            'Yes' if record['muted'] else '',
            'Yes' if record['hidden'] else '',
            record['shareUrl'],
            record['avatarUrl'],
        ))

    data_headers = (
        ('Created', 'datetime'), ('Last Message', 'datetime'), ('Last Viewed', 'datetime'),
        'Chat Name', 'Chat ID', 'Chat Type', 'Group Type', 'Group Description',
        'Other Party User ID', 'Creator ID', 'Message Count', 'Unread Count',
        'Muted', 'Hidden', 'Share URL', 'Avatar URL')

    return data_headers, data_list, source_path


@artifact_processor
def groupMeGroupMembers(context):
    source_path = get_file_path(context.get_files_found(), 'GroupMe.sqlite')
    data_list = []

    query = '''
    SELECT
        mem.ZNAME AS nickname,
        mem.ZREALNAME AS realName,
        mem.ZGLOBALUSERID AS userId,
        mem.ZMEMBERID AS memberId,
        mem.ZSTATE AS state,
        mem.ZISAUTOKICKED AS autoKicked,
        mem.ZAVATARURL AS avatarUrl,
        c.ZNAME AS groupName,
        c.ZCHATID AS groupId
    FROM ZGMMEMBER mem
    LEFT JOIN ZGMCHAT c ON c.Z_PK = mem.ZGROUP
    ORDER BY c.ZNAME, mem.ZNAME
    '''

    for record in get_sqlite_db_records(source_path, query):
        data_list.append((
            record['groupName'],
            record['groupId'],
            record['nickname'],
            record['realName'],
            record['userId'],
            record['memberId'],
            record['state'],
            'Yes' if record['autoKicked'] else '',
            record['avatarUrl'],
        ))

    data_headers = (
        'Group Name', 'Group ID', 'Nickname', 'Real Name', 'User ID',
        'Member ID', 'State', 'Auto Kicked', 'Avatar URL')

    return data_headers, data_list, source_path


@artifact_processor
def groupMeContacts(context):
    source_path = get_file_path(context.get_files_found(), 'GroupMe.sqlite')
    data_list = []

    query = '''
    SELECT
        r.ZCREATEDAT,
        r.ZUPDATEDAT,
        r.ZNAME AS name,
        r.ZPHONENUMBER AS phoneNumber,
        r.ZUSERID AS userId,
        r.ZRELATIONSHIPID AS relationshipId,
        r.ZBLOCKED AS blocked,
        r.ZHIDDEN AS hidden,
        r.ZISAPPUSER AS isAppUser,
        r.ZAVATARURL AS avatarUrl,
        ab.ZFULLNAME AS addressBookName,
        ab.ZCONTACTSID AS addressBookId
    FROM ZGMRELATIONSHIP r
    LEFT JOIN ZGMABCONTACT ab ON ab.ZRELATIONSHIP = r.Z_PK
    ORDER BY r.ZNAME
    '''

    for record in get_sqlite_db_records(source_path, query):
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(record['ZCREATEDAT']) if record['ZCREATEDAT'] else '',
            convert_cocoa_core_data_ts_to_utc(record['ZUPDATEDAT']) if record['ZUPDATEDAT'] else '',
            record['name'],
            record['addressBookName'],
            record['phoneNumber'],
            record['userId'],
            record['relationshipId'],
            'Yes' if record['blocked'] else '',
            'Yes' if record['hidden'] else '',
            'Yes' if record['isAppUser'] else '',
            record['addressBookId'],
            record['avatarUrl'],
        ))

    data_headers = (
        ('Created', 'datetime'), ('Updated', 'datetime'), 'Name',
        'Address Book Name', ('Phone Number', 'phonenumber'), 'User ID',
        'Relationship ID', 'Blocked', 'Hidden', 'GroupMe User',
        'Address Book ID', 'Avatar URL')

    return data_headers, data_list, source_path


@artifact_processor
def groupMeAccount(context):
    source_path = get_file_path(context.get_files_found(), 'com.groupme.iphone-app.plist')
    data_list = []

    plist = get_plist_file_content(source_path)
    if plist:
        for key, label in ACCOUNT_KEYS:
            if key in plist:
                data_list.append((label, str(plist[key])))

        # The 'user' key holds the account profile dictionary.
        user = plist.get('user')
        if isinstance(user, dict):
            for key in ('name', 'email', 'phone_number', 'created_at', 'user_id'):
                if key in user:
                    data_list.append((f'Profile {key.replace("_", " ").title()}', str(user[key])))

    data_headers = ('Key', 'Value')

    return data_headers, data_list, source_path
