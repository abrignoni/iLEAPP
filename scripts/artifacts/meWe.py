__artifacts_v2__ = {
    'meWeMessages': {
        'name': 'MeWe - Chats',
        'description': 'Chat messages, attachments and shared locations from the MeWe application',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-31',
        'requirements': 'none',
        'category': 'MeWe',
        'notes': 'In examined data shared locations appeared as OpenStreetMap links; coordinates are parsed out of the message text.',
        'paths': ('*/mobile/Containers/Data/Application/*/Documents/sgrouplesdb.sqlite*',),
        'output_types': 'all',
        'artifact_icon': 'message',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 53 rows across 4 threads',
        },
        'data_views': {
            'conversation': {
                'conversationDiscriminatorColumn': 'Thread ID',
                'conversationLabelColumn': 'Conversation',
                'textColumn': 'Message',
                'directionColumn': 'From Me',
                'directionSentValue': 1,
                'timeColumn': 'Timestamp',
                'senderColumn': 'Sender',
            }
        }
    },
    'meWeContacts': {
        'name': 'MeWe - Contacts',
        'description': 'MeWe users known to the application, including contact relationships',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-25',
        'requirements': 'none',
        'category': 'MeWe',
        'notes': '',
        'paths': ('*/mobile/Containers/Data/Application/*/Documents/sgrouplesdb.sqlite*',),
        'output_types': 'standard',
        'artifact_icon': 'address-book',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 7 rows',
        },
    },
    'meWePosts': {
        'name': 'MeWe - Posts',
        'description': 'Status updates and group posts cached by the MeWe application',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-25',
        'requirements': 'none',
        'category': 'MeWe',
        'notes': '',
        'paths': ('*/mobile/Containers/Data/Application/*/Documents/sgrouplesdb.sqlite*',),
        'output_types': 'standard',
        'artifact_icon': 'news',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 33 rows',
        },
    },
    'meWeGroups': {
        'name': 'MeWe - Groups',
        'description': 'Social groups the MeWe account belongs to or has viewed',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-25',
        'requirements': 'none',
        'category': 'MeWe',
        'notes': '',
        'paths': ('*/mobile/Containers/Data/Application/*/Documents/sgrouplesdb.sqlite*',),
        'output_types': 'standard',
        'artifact_icon': 'users-group',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 1 row',
        },
    },
    'meWePolls': {
        'name': 'MeWe - Polls',
        'description': 'Polls cached by the MeWe application, with their options and vote counts',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-31',
        'requirements': 'none',
        'category': 'MeWe',
        'notes': '',
        'paths': ('*/mobile/Containers/Data/Application/*/Documents/sgrouplesdb.sqlite*',),
        'output_types': 'standard',
        'artifact_icon': 'chart-bar',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 10 rows',
        },
    },
    'meWeAccount': {
        'name': 'MeWe - Account Information',
        'description': 'Details of the MeWe account signed in on the device',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-25',
        'requirements': 'none',
        'category': 'MeWe',
        'notes': '',
        'paths': ('*/mobile/Containers/Data/Application/*/Documents/sgrouplesdb.sqlite*',),
        'output_types': 'standard',
        'artifact_icon': 'user',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 1 row',
        },
    },
}

import re

from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records, null_absent_columns, convert_cocoa_core_data_ts_to_utc

# MeWe sends a shared location as an OpenStreetMap link in the message body,
# e.g. https://www.openstreetmap.org/?mlat=35.66119068&mlon=-78.87362671
OSM_COORDS_RE = re.compile(r'mlat=(-?\d+\.?\d*)&(?:amp;)?mlon=(-?\d+\.?\d*)')

# Resolves a MeWe user ID to the best available display name.
USER_NAME_SQL = '''
    COALESCE(
        u.ZNAME,
        TRIM(COALESCE(u.ZFIRSTNAME, '') || ' ' || COALESCE(u.ZLASTNAME, '')),
        u.ZHANDLE
    )
'''


def _parse_shared_location(text):
    """Return (latitude, longitude) if the message body is a shared location."""
    if not text:
        return '', ''
    match = OSM_COORDS_RE.search(text)
    if not match:
        return '', ''
    return match.group(1), match.group(2)


def _column_exists(source_path, table, column):
    """Whether a column is present, so the account query survives MeWe schema versions
    that drop version-specific columns such as the DSNP (web3) fields."""
    rows = get_sqlite_db_records(
        source_path,
        f"SELECT 1 FROM pragma_table_info('{table}') WHERE name = '{column}'")
    return any(True for _ in rows)


@artifact_processor
def meWeMessages(context):
    source_path = get_file_path(context.get_files_found(), 'sgrouplesdb.sqlite')
    data_list = []

    query = f'''
    SELECT
        m.ZDATE,
        m.ZEDITEDDATE,
        m.ZTEXT AS message,
        m.ZORIGINALTEXT AS originalText,
        m.ZSENDER AS senderId,
        {USER_NAME_SQL} AS senderName,
        m.ZTHREADID AS threadId,
        m.ZMESSAGEID AS messageId,
        m.ZREPLYMESSAGEID AS replyMessageId,
        m.ZDELETEDBYSENDER AS deletedBySender,
        m.ZDISAPPEARINGTYPE AS disappearingType,
        m.ZEVENTTYPE AS eventType,
        m.ZCALLDURATION AS callDuration,
        m.ZCALLHASVIDEO AS callHasVideo,
        m.ZTZDATESTR AS localTimeString,
        t.ZCHATTYPE AS chatType,
        t.ZSTARTEDBY AS startedBy,
        cur.ZUSERID AS currentUserId,
        (SELECT GROUP_CONCAT(a.ZATYPE, ', ') FROM ZCHATATTACHMENT a
          WHERE a.ZCHATMESSAGE = m.Z_PK) AS attachmentType,
        (SELECT GROUP_CONCAT(a.ZFILENAME, ', ') FROM ZCHATATTACHMENT a
          WHERE a.ZCHATMESSAGE = m.Z_PK AND a.ZFILENAME IS NOT NULL) AS attachmentName,
        (SELECT GROUP_CONCAT(a.ZURL, ', ') FROM ZCHATATTACHMENT a
          WHERE a.ZCHATMESSAGE = m.Z_PK AND a.ZURL IS NOT NULL) AS attachmentUrl,
        (SELECT GROUP_CONCAT(DISTINCT other.ZUSERID) FROM ZCHATMESSAGE om
           JOIN ZUSER other ON other.ZUSERID = om.ZSENDER
          WHERE om.ZTHREADID = m.ZTHREADID) AS threadParticipantIds
    FROM ZCHATMESSAGE m
    LEFT JOIN ZUSER u ON u.ZUSERID = m.ZSENDER
    LEFT JOIN ZCHATTHREAD t ON t.ZTHREADID = m.ZTHREADID
    LEFT JOIN ZUSER cur ON cur.ZCURRENTUSER = 1
    ORDER BY m.ZDATE
    '''

    # Name each thread after its participants other than the account holder, so
    # a one-to-one chat reads as the other person's name.
    thread_labels = {}
    records = list(get_sqlite_db_records(source_path, null_absent_columns(source_path, query)))
    for record in records:
        thread_id = record['threadId']
        if thread_id in thread_labels:
            continue
        others = [name for name in _thread_other_names(records, thread_id,
                                                       record['currentUserId'])]
        thread_labels[thread_id] = ', '.join(others) if others else thread_id

    for record in records:
        latitude, longitude = _parse_shared_location(record['message'])
        current_user_id = record['currentUserId']
        from_me = 1 if current_user_id and record['senderId'] == current_user_id else 0

        data_list.append((
            convert_cocoa_core_data_ts_to_utc(record['ZDATE']),
            convert_cocoa_core_data_ts_to_utc(record['ZEDITEDDATE']) if record['ZEDITEDDATE'] else '',
            from_me,
            record['senderName'],
            thread_labels.get(record['threadId'], record['threadId']),
            record['message'],
            record['threadId'],
            record['chatType'],
            record['senderId'],
            latitude,
            longitude,
            record['attachmentType'],
            record['attachmentName'],
            record['attachmentUrl'],
            record['originalText'],
            'Yes' if record['deletedBySender'] else '',
            record['disappearingType'],
            record['eventType'],
            record['callDuration'] or '',
            'Yes' if record['callHasVideo'] else '',
            record['messageId'],
            record['replyMessageId'],
        ))

    data_headers = (
        ('Timestamp', 'datetime'),
        ('Edited', 'datetime'),
        'From Me',
        'Sender',
        'Conversation',
        'Message',
        'Thread ID',
        'Chat Type',
        'Sender ID',
        'Latitude',
        'Longitude',
        'Attachment Type',
        'Attachment Name',
        'Attachment URL',
        'Original Text',
        'Deleted By Sender',
        'Disappearing Type',
        'Event Type',
        'Call Duration',
        'Call Has Video',
        'Message ID',
        'Reply To Message ID',
    )

    return data_headers, data_list, source_path


def _thread_other_names(records, thread_id, current_user_id):
    """Distinct sender names in a thread, excluding the account holder."""
    seen = {}
    for record in records:
        if record['threadId'] != thread_id:
            continue
        if current_user_id and record['senderId'] == current_user_id:
            continue
        name = record['senderName'] or record['senderId']
        if name:
            seen[name] = None
    return list(seen)


@artifact_processor
def meWeContacts(context):
    source_path = get_file_path(context.get_files_found(), 'sgrouplesdb.sqlite')
    data_list = []

    query = f'''
    SELECT
        {USER_NAME_SQL} AS name,
        u.ZHANDLE AS handle,
        u.ZUSERID AS userId,
        u.ZFIRSTNAME AS firstName,
        u.ZLASTNAME AS lastName,
        u.ZISVERIFIED AS verified,
        u.ZISPREMIUM AS premium,
        u.ZISPUBLIC AS public,
        u.ZCURRENTUSER AS isCurrentUser,
        u.ZDSNPHANDLE AS dsnpHandle,
        c.ZCONTACTID AS contactId,
        c.ZCONTACTTYPE AS contactType,
        c.ZINVITATIONTYPE AS invitationType,
        c.ZCREATEDDATE AS contactCreated,
        p.followersCount,
        p.followingCount,
        p.isContact,
        p.isFollowing,
        p.isFollower,
        p.isMuted
    FROM ZUSER u
    LEFT JOIN ZCONTACT c ON c.ZUSER = u.Z_PK
    -- MeWe keeps several ZPROFILE rows per user (one per context the profile was
    -- loaded in), so collapse them to a single row before joining.
    LEFT JOIN (
        SELECT
            ZUSER,
            MAX(ZFOLLOWERSCOUNT) AS followersCount,
            MAX(ZFOLLOWINGCOUNT) AS followingCount,
            MAX(ZISCONTACT) AS isContact,
            MAX(ZISFOLLOWING) AS isFollowing,
            MAX(ZISFOLLOWER) AS isFollower,
            MAX(ZISMUTED) AS isMuted
        FROM ZPROFILE
        GROUP BY ZUSER
    ) p ON p.ZUSER = u.Z_PK
    ORDER BY name
    '''

    for record in get_sqlite_db_records(source_path, null_absent_columns(source_path, query)):
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(record['contactCreated']) if record['contactCreated'] else '',
            record['name'],
            record['handle'],
            record['userId'],
            record['firstName'],
            record['lastName'],
            'Yes' if record['isCurrentUser'] else '',
            record['contactType'],
            record['invitationType'],
            'Yes' if record['isContact'] else '',
            'Yes' if record['isFollowing'] else '',
            'Yes' if record['isFollower'] else '',
            'Yes' if record['isMuted'] else '',
            'Yes' if record['verified'] else '',
            'Yes' if record['premium'] else '',
            'Yes' if record['public'] else '',
            record['followersCount'],
            record['followingCount'],
            record['dsnpHandle'],
        ))

    data_headers = (
        ('Contact Created', 'datetime'), 'Name', 'Handle', 'User ID',
        'First Name', 'Last Name', 'Account Holder', 'Contact Type',
        'Invitation Type', 'Is Contact', 'Following', 'Follower', 'Muted',
        'Verified', 'Premium', 'Public', 'Followers Count', 'Following Count',
        'DSNP Handle')

    return data_headers, data_list, source_path


@artifact_processor
def meWePosts(context):
    source_path = get_file_path(context.get_files_found(), 'sgrouplesdb.sqlite')
    data_list = []

    query = f'''
    SELECT
        p.ZCREATIONDATE,
        p.ZEDITEDDATE,
        p.ZUPDATEDDATE,
        p.ZTEXT AS text,
        p.ZPOSTID AS postId,
        p.ZUSERID AS userId,
        {USER_NAME_SQL} AS authorName,
        p.ZGROUPID AS groupId,
        g.ZNAME AS groupName,
        p.ZPAGEID AS pageId,
        p.ZALBUMNAME AS albumName,
        p.ZCOMMENTSCOUNT AS commentsCount,
        p.ZPHOTOSCOUNT AS photosCount,
        p.ZSHARESCOUNT AS sharesCount,
        p.ZISPUBLIC AS isPublic,
        p.ZISEVERYONE AS isEveryone,
        p.ZISFEATURED AS isFeatured,
        p.ZSOURCE AS source,
        p.ZPARENTPOSTID AS parentPostId,
        p.ZTHREADID AS threadId
    FROM ZPOST p
    LEFT JOIN ZUSER u ON u.ZUSERID = p.ZUSERID
    LEFT JOIN ZGROUP g ON g.ZGROUPID = p.ZGROUPID
    ORDER BY p.ZCREATIONDATE
    '''

    for record in get_sqlite_db_records(source_path, null_absent_columns(source_path, query)):
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(record['ZCREATIONDATE']) if record['ZCREATIONDATE'] else '',
            convert_cocoa_core_data_ts_to_utc(record['ZEDITEDDATE']) if record['ZEDITEDDATE'] else '',
            record['authorName'],
            record['userId'],
            record['text'],
            record['groupName'],
            record['groupId'],
            record['pageId'],
            record['albumName'],
            record['commentsCount'],
            record['photosCount'],
            record['sharesCount'],
            'Yes' if record['isPublic'] else '',
            'Yes' if record['isEveryone'] else '',
            'Yes' if record['isFeatured'] else '',
            record['source'],
            record['postId'],
            record['parentPostId'],
        ))

    data_headers = (
        ('Created', 'datetime'), ('Edited', 'datetime'), 'Author', 'Author User ID',
        'Text', 'Group Name', 'Group ID', 'Page ID', 'Album Name',
        'Comments Count', 'Photos Count', 'Shares Count', 'Public', 'Everyone',
        'Featured', 'Source', 'Post ID', 'Parent Post ID')

    return data_headers, data_list, source_path


@artifact_processor
def meWeGroups(context):
    source_path = get_file_path(context.get_files_found(), 'sgrouplesdb.sqlite')
    data_list = []

    query = '''
    SELECT
        g.ZNAME AS name,
        g.ZGROUPID AS groupId,
        g.ZDESCRIPTIONPLAIN AS description,
        g.ZOWNERID AS ownerId,
        g.ZROLE AS role,
        g.ZPUBLICROLE AS publicRole,
        g.ZCATEGORY AS category,
        g.ZMEMBERSCOUNT AS membersCount,
        g.ZISPUBLIC AS isPublic,
        g.ZISCONFIRMED AS isConfirmed,
        g.ZISMUTED AS isMuted,
        g.ZISOWNERORADMIN AS isOwnerOrAdmin,
        g.ZEMAIL AS email,
        g.ZPUBLICURLID AS publicUrlId,
        g.ZCHATMODE AS chatMode,
        g.ZUNSEENPOSTSCOUNT AS unseenPostsCount,
        (SELECT COUNT(*) FROM ZPOST p WHERE p.ZGROUPID = g.ZGROUPID) AS postCount
    FROM ZGROUP g
    ORDER BY g.ZNAME
    '''

    for record in get_sqlite_db_records(source_path, null_absent_columns(source_path, query)):
        data_list.append((
            record['name'],
            record['groupId'],
            record['description'],
            record['category'],
            record['ownerId'],
            record['role'],
            record['publicRole'],
            record['membersCount'],
            record['postCount'],
            record['unseenPostsCount'],
            'Yes' if record['isPublic'] else '',
            'Yes' if record['isConfirmed'] else '',
            'Yes' if record['isMuted'] else '',
            'Yes' if record['isOwnerOrAdmin'] else '',
            record['chatMode'],
            record['email'],
            record['publicUrlId'],
        ))

    data_headers = (
        'Group Name', 'Group ID', 'Description', 'Category', 'Owner ID', 'Role',
        'Public Role', 'Members Count', 'Cached Post Count', 'Unseen Posts',
        'Public', 'Confirmed', 'Muted', 'Owner Or Admin', 'Chat Mode', 'Email',
        'Public URL ID')

    return data_headers, data_list, source_path


@artifact_processor
def meWePolls(context):
    source_path = get_file_path(context.get_files_found(), 'sgrouplesdb.sqlite')
    data_list = []

    query = '''
    SELECT
        p.Z_PK AS pollRowId,
        p.ZQUESTION AS question,
        p.ZISCLOSED AS isClosed,
        p.ZENDDATE AS endDate,
        (SELECT GROUP_CONCAT(o.ZTEXT, ' | ') FROM ZPOLLOPTION o
          WHERE o.Z29OPTIONS = p.Z_PK) AS options,
        (SELECT GROUP_CONCAT(o.ZVOTES, ' | ') FROM ZPOLLOPTION o
          WHERE o.Z29OPTIONS = p.Z_PK) AS optionVotes,
        (SELECT COUNT(*) FROM ZPOLLOPTION o WHERE o.Z29OPTIONS = p.Z_PK) AS optionCount,
        (SELECT GROUP_CONCAT(o.ZTEXT, ' | ') FROM ZPOLLOPTION o
          WHERE o.Z29OPTIONS = p.Z_PK AND o.ZISSELECTED = 1) AS selectedOptions,
        (SELECT post.ZPOSTID FROM ZPOST post WHERE post.ZPOLL = p.Z_PK) AS postId,
        (SELECT post.ZUSERID FROM ZPOST post WHERE post.ZPOLL = p.Z_PK) AS postUserId,
        (SELECT post.ZCREATIONDATE FROM ZPOST post WHERE post.ZPOLL = p.Z_PK) AS postCreated
    FROM ZPOLL p
    ORDER BY p.Z_PK
    '''

    for record in get_sqlite_db_records(source_path, null_absent_columns(source_path, query)):
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(record['postCreated']) if record['postCreated'] else '',
            convert_cocoa_core_data_ts_to_utc(record['endDate']) if record['endDate'] else '',
            record['question'],
            record['options'],
            record['optionVotes'],
            record['selectedOptions'],
            record['optionCount'],
            'Yes' if record['isClosed'] else '',
            record['postUserId'],
            record['postId'],
        ))

    data_headers = (
        ('Post Created', 'datetime'), ('End Date', 'datetime'), 'Question',
        'Options', 'Option Votes', 'Selected Option (client state)', 'Option Count', 'Closed',
        'Posted By User ID', 'Post ID')

    return data_headers, data_list, source_path


@artifact_processor
def meWeAccount(context):
    source_path = get_file_path(context.get_files_found(), 'sgrouplesdb.sqlite')
    data_list = []

    # The DSNP (web3) columns are not present in every MeWe version, so they are
    # selected only when the schema still carries them.
    dsnp_registered = ('cu.ZISDSNPREGISTERED'
                       if _column_exists(source_path, 'ZCURRENTUSER', 'ZISDSNPREGISTERED')
                       else 'NULL')
    dsnp_handle = ('u.ZDSNPHANDLE'
                   if _column_exists(source_path, 'ZUSER', 'ZDSNPHANDLE') else 'NULL')

    query = f'''
    SELECT
        {USER_NAME_SQL} AS name,
        u.ZHANDLE AS handle,
        u.ZUSERID AS userId,
        u.ZFIRSTNAME AS firstName,
        u.ZLASTNAME AS lastName,
        u.ZFINGERPRINT AS fingerprint,
        {dsnp_handle} AS dsnpHandle,
        cu.ZPRIMARYEMAIL AS primaryEmail,
        cu.ZPRIMARYPHONE AS primaryPhone,
        cu.ZCONTACTINVITEID AS contactInviteId,
        cu.ZREGISTERED AS registered,
        {dsnp_registered} AS dsnpRegistered,
        cu.ZJAILSENTENCE AS jailSentence,
        cu.ZJAILDATE AS jailDate
    FROM ZCURRENTUSER cu
    LEFT JOIN ZUSER u ON u.Z_PK = cu.ZUSER
    '''

    for record in get_sqlite_db_records(source_path, null_absent_columns(source_path, query)):
        data_list.append((
            record['name'],
            record['handle'],
            record['userId'],
            record['firstName'],
            record['lastName'],
            record['primaryEmail'],
            record['primaryPhone'],
            record['contactInviteId'],
            record['registered'],
            'Yes' if record['dsnpRegistered'] else '',
            record['dsnpHandle'],
            record['fingerprint'],
            convert_cocoa_core_data_ts_to_utc(record['jailDate']) if record['jailDate'] else '',
        ))

    data_headers = (
        'Name', 'Handle', 'User ID', 'First Name', 'Last Name', 'Primary Email',
        ('Primary Phone', 'phonenumber'), 'Contact Invite ID', 'Registered',
        'DSNP Registered', 'DSNP Handle', 'Fingerprint', ('Jail Date', 'datetime'))

    return data_headers, data_list, source_path
