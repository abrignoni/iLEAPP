__artifacts_v2__ = {
    'mastodonDirectMessages': {
        'name': 'Mastodon - Direct Messages',
        'description': 'Private (direct visibility) statuses cached by the Mastodon application',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-31',
        'requirements': 'none',
        'category': 'Mastodon',
        'notes': 'Mastodon models direct messages as statuses with a visibility of "direct".',
        'paths': ('*/mobile/Containers/Shared/AppGroup/*/Databases/shared.sqlite*',),
        'output_types': 'all',
        'artifact_icon': 'message',
        'sample_data': {
            'josh_ios17_ffs': 'iOS 17.3 | 40 rows',
            'magnet_ios16': 'iOS 14.7.1 | Mastodon present',
        },
        'data_views': {
            'conversation': {
                'conversationDiscriminatorColumn': 'Conversation Key',
                'conversationLabelColumn': 'Conversation',
                'textColumn': 'Message',
                'directionColumn': 'From Me',
                'directionSentValue': 1,
                'timeColumn': 'Timestamp',
                'senderColumn': 'Author',
            }
        }
    },
    'mastodonStatuses': {
        'name': 'Mastodon - Statuses',
        'description': 'Statuses (posts) cached by the Mastodon application, including boosts and replies',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-25',
        'requirements': 'none',
        'category': 'Mastodon',
        'notes': '',
        'paths': ('*/mobile/Containers/Shared/AppGroup/*/Databases/shared.sqlite*',),
        'output_types': 'standard',
        'artifact_icon': 'news',
        'sample_data': {
            'josh_ios17_ffs': 'iOS 17.3 | 114 rows (74 public, 40 direct)',
        },
    },
    'mastodonUsers': {
        'name': 'Mastodon - Users',
        'description': 'Mastodon accounts cached by the application, with follow relationships',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-25',
        'requirements': 'none',
        'category': 'Mastodon',
        'notes': '',
        'paths': ('*/mobile/Containers/Shared/AppGroup/*/Databases/shared.sqlite*',),
        'output_types': 'standard',
        'artifact_icon': 'users',
        'sample_data': {
            'josh_ios17_ffs': 'iOS 17.3 | 255 rows',
        },
    },
    'mastodonNotifications': {
        'name': 'Mastodon - Notifications',
        'description': 'Mentions, follows and other notifications received by the Mastodon account',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-25',
        'requirements': 'none',
        'category': 'Mastodon',
        'notes': '',
        'paths': ('*/mobile/Containers/Shared/AppGroup/*/Databases/shared.sqlite*',),
        'output_types': 'standard',
        'artifact_icon': 'bell',
        'sample_data': {
            'josh_ios17_ffs': 'iOS 17.3 | 18 rows (15 mention, 3 follow)',
        },
    },
    'mastodonAccount': {
        'name': 'Mastodon - Account Information',
        'description': 'The Mastodon account signed in on the device and its home instance',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-25',
        'requirements': 'none',
        'category': 'Mastodon',
        'notes': 'When the authentication table is empty the account holder is identified from the notification owner ID.',
        'paths': ('*/mobile/Containers/Shared/AppGroup/*/Databases/shared.sqlite*',),
        'output_types': 'standard',
        'artifact_icon': 'user',
        'sample_data': {
            'josh_ios17_ffs': 'iOS 17.3 | 1 row; ZMASTODONAUTHENTICATION empty, holder resolved from notifications',
        },
    },
}

import html
import json
import re

from scripts.ilapfuncs import artifact_processor, logfunc, \
    get_file_path, get_sqlite_db_records, does_table_exist_in_db, \
    convert_cocoa_core_data_ts_to_utc

HTML_TAG_RE = re.compile(r'<[^>]+>')

# Mastodon's Databases/shared.sqlite name is generic enough that another app
# could share it, so every artifact confirms this table before querying.
MASTODON_MARKER_TABLE = 'ZMASTODONUSER'

# Common projection of an author row onto a readable handle.
AUTHOR_LABEL_SQL = '''
    COALESCE(
        NULLIF(u.ZDISPLAYNAME, '') || ' (@' || u.ZACCT || ')',
        '@' || u.ZACCT,
        u.ZUSERNAME
    )
'''


def _html_to_text(content):
    """Flatten a Mastodon HTML status body to plain text."""
    if not content:
        return ''
    text = content.replace('</p><p>', '\n').replace('<br>', '\n').replace('<br/>', '\n')
    text = HTML_TAG_RE.sub('', text)
    return html.unescape(text).replace('\xa0', ' ').strip()


def _parse_attachments(blob):
    """Return (urls, descriptions) from the JSON attachment blob on a status."""
    if not blob:
        return '', ''
    try:
        attachments = json.loads(blob)
    except (ValueError, TypeError):
        return '', ''
    if not isinstance(attachments, list):
        return '', ''
    urls = [a.get('url') or a.get('previewURL') or ''
            for a in attachments if isinstance(a, dict)]
    descriptions = [a.get('altDescription') or ''
                    for a in attachments if isinstance(a, dict)]
    return ', '.join(u for u in urls if u), ', '.join(d for d in descriptions if d)


def _parse_mentions(blob):
    """Return the handles mentioned in a status."""
    if not blob:
        return ''
    try:
        mentions = json.loads(blob)
    except (ValueError, TypeError):
        return ''
    if not isinstance(mentions, list):
        return ''
    return ', '.join('@' + m.get('acct', '') for m in mentions
                     if isinstance(m, dict) and m.get('acct'))


def _get_source(context):
    """Return the shared.sqlite path only if it is really a Mastodon database."""
    source_path = get_file_path(context.get_files_found(), 'shared.sqlite')
    if not source_path:
        return None
    if not does_table_exist_in_db(source_path, MASTODON_MARKER_TABLE):
        logfunc(f'{source_path} is not a Mastodon database; skipping.')
        return None
    return source_path


def _get_local_user_id(source_path):
    """Identify the signed-in account.

    ZMASTODONAUTHENTICATION is the intended home for this but is empty in some
    extractions, so fall back to the account ID that owns the notifications.
    """
    for query in (
        'SELECT ZUSERID FROM ZMASTODONAUTHENTICATION WHERE ZUSERID IS NOT NULL LIMIT 1',
        'SELECT ZUSERID FROM ZNOTIFICATION WHERE ZUSERID IS NOT NULL LIMIT 1',
    ):
        records = list(get_sqlite_db_records(source_path, query))
        if records and records[0]['ZUSERID']:
            return records[0]['ZUSERID']
    return None


STATUS_QUERY = f'''
SELECT
    s.ZCREATEDAT,
    s.ZEDITEDAT,
    s.ZDELETEDAT,
    s.ZID AS statusId,
    s.ZDOMAIN AS domain,
    s.ZCONTENT AS content,
    s.ZSPOILERTEXT AS spoilerText,
    s.ZVISIBILITYRAW AS visibility,
    s.ZLANGUAGE AS language,
    s.ZURL AS url,
    s.ZURI AS uri,
    s.ZSENSITIVE AS sensitive,
    s.ZFAVOURITESCOUNT AS favouritesCount,
    s.ZREBLOGSCOUNT AS reblogsCount,
    s.ZREPLIESCOUNT AS repliesCount,
    s.ZINREPLYTOID AS inReplyToId,
    s.ZINREPLYTOACCOUNTID AS inReplyToAccountId,
    s.ZATTACHMENTS AS attachments,
    s.ZMENTIONS AS mentions,
    u.ZID AS authorId,
    u.ZACCT AS authorAcct,
    {AUTHOR_LABEL_SQL} AS authorLabel,
    app.ZNAME AS applicationName
FROM ZSTATUS s
LEFT JOIN ZMASTODONUSER u ON u.Z_PK = s.ZAUTHOR
LEFT JOIN ZAPPLICATION app ON app.Z_PK = s.ZAPPLICATION
{{where}}
ORDER BY s.ZCREATEDAT
'''


@artifact_processor
def mastodonDirectMessages(context):
    source_path = _get_source(context)
    data_list = []
    data_headers = (
        ('Timestamp', 'datetime'), 'Conversation', 'Conversation Key', 'Author',
        'Author Handle', 'Message', 'Mentions', 'Attachment URLs',
        'Attachment Descriptions', 'Content Warning', 'Language',
        ('Edited', 'datetime'), 'In Reply To Status ID', 'Status ID', 'URL',
        'From Me')
    if not source_path:
        return data_headers, data_list, ''

    local_user_id = _get_local_user_id(source_path)
    query = STATUS_QUERY.format(where="WHERE s.ZVISIBILITYRAW = 'direct'")

    for record in get_sqlite_db_records(source_path, query):
        attachment_urls, attachment_descriptions = _parse_attachments(record['attachments'])
        mentions = _parse_mentions(record['mentions'])
        author_id = record['authorId']
        from_me = 1 if local_user_id and author_id == local_user_id else 0

        # A direct status has no thread ID of its own. The people mentioned in
        # it are what makes it one conversation, so key on that set.
        participants = sorted({p for p in mentions.split(', ') if p} |
                              ({'@' + record['authorAcct']} if record['authorAcct'] else set()))
        conversation_key = ', '.join(participants)

        data_list.append((
            convert_cocoa_core_data_ts_to_utc(record['ZCREATEDAT']),
            conversation_key,
            conversation_key,
            record['authorLabel'],
            record['authorAcct'],
            _html_to_text(record['content']),
            mentions,
            attachment_urls,
            attachment_descriptions,
            record['spoilerText'],
            record['language'],
            convert_cocoa_core_data_ts_to_utc(record['ZEDITEDAT']) if record['ZEDITEDAT'] else '',
            record['inReplyToId'],
            record['statusId'],
            record['url'],
            from_me,
        ))

    return data_headers, data_list, source_path


@artifact_processor
def mastodonStatuses(context):
    source_path = _get_source(context)
    data_list = []
    data_headers = (
        ('Created', 'datetime'), ('Edited', 'datetime'), ('Deleted', 'datetime'),
        'Author', 'Author Handle', 'Author ID', 'Visibility', 'Content',
        'Content Warning', 'Mentions', 'Attachment URLs',
        'Attachment Descriptions', 'Sensitive', 'Language', 'Favourites',
        'Boosts', 'Replies', 'In Reply To Status ID', 'In Reply To Account ID',
        'Posted With', 'Domain', 'Status ID', 'URL')
    if not source_path:
        return data_headers, data_list, ''

    for record in get_sqlite_db_records(source_path, STATUS_QUERY.format(where='')):
        attachment_urls, attachment_descriptions = _parse_attachments(record['attachments'])

        data_list.append((
            convert_cocoa_core_data_ts_to_utc(record['ZCREATEDAT']) if record['ZCREATEDAT'] else '',
            convert_cocoa_core_data_ts_to_utc(record['ZEDITEDAT']) if record['ZEDITEDAT'] else '',
            convert_cocoa_core_data_ts_to_utc(record['ZDELETEDAT']) if record['ZDELETEDAT'] else '',
            record['authorLabel'],
            record['authorAcct'],
            record['authorId'],
            record['visibility'],
            _html_to_text(record['content']),
            record['spoilerText'],
            _parse_mentions(record['mentions']),
            attachment_urls,
            attachment_descriptions,
            'Yes' if record['sensitive'] else '',
            record['language'],
            record['favouritesCount'],
            record['reblogsCount'],
            record['repliesCount'],
            record['inReplyToId'],
            record['inReplyToAccountId'],
            record['applicationName'],
            record['domain'],
            record['statusId'],
            record['url'],
        ))

    return data_headers, data_list, source_path


@artifact_processor
def mastodonUsers(context):
    source_path = _get_source(context)
    data_list = []
    data_headers = (
        ('Created', 'datetime'), ('Updated', 'datetime'), 'Display Name',
        'Handle', 'Username', 'Domain', 'User ID', 'Account Holder',
        'Followed By Account Holder', 'Follows Account Holder', 'Bio',
        'Followers Count', 'Following Count', 'Statuses Count', 'Bot', 'Locked',
        'Suspended', 'Profile URL', 'Avatar URL')
    if not source_path:
        return data_headers, data_list, ''

    local_user_id = _get_local_user_id(source_path)

    query = '''
    SELECT
        u.ZCREATEDAT,
        u.ZUPDATEDAT,
        u.ZDISPLAYNAME AS displayName,
        u.ZACCT AS acct,
        u.ZUSERNAME AS username,
        u.ZDOMAIN AS domain,
        u.ZID AS userId,
        u.ZNOTE AS note,
        u.ZFOLLOWERSCOUNT AS followersCount,
        u.ZFOLLOWINGCOUNT AS followingCount,
        u.ZSTATUSESCOUNT AS statusesCount,
        u.ZBOT AS bot,
        u.ZLOCKED AS locked,
        u.ZSUSPENDED AS suspended,
        u.ZURL AS url,
        u.ZAVATARSTATIC AS avatarUrl,
        EXISTS(SELECT 1 FROM Z_8FOLLOWING f
                JOIN ZMASTODONUSER me ON me.Z_PK = f.Z_8FOLLOWINGBY
               WHERE f.Z_8FOLLOWING = u.Z_PK AND me.ZID = :localUserId) AS followedByHolder,
        EXISTS(SELECT 1 FROM Z_8FOLLOWING f
                JOIN ZMASTODONUSER me ON me.Z_PK = f.Z_8FOLLOWING
               WHERE f.Z_8FOLLOWINGBY = u.Z_PK AND me.ZID = :localUserId) AS followsHolder
    FROM ZMASTODONUSER u
    ORDER BY u.ZACCT
    '''

    for record in get_sqlite_db_records(source_path, query.replace(':localUserId',
                                                                  f"'{local_user_id}'" if local_user_id else 'NULL')):
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(record['ZCREATEDAT']) if record['ZCREATEDAT'] else '',
            convert_cocoa_core_data_ts_to_utc(record['ZUPDATEDAT']) if record['ZUPDATEDAT'] else '',
            record['displayName'],
            record['acct'],
            record['username'],
            record['domain'],
            record['userId'],
            'Yes' if local_user_id and record['userId'] == local_user_id else '',
            'Yes' if record['followedByHolder'] else '',
            'Yes' if record['followsHolder'] else '',
            _html_to_text(record['note']),
            record['followersCount'],
            record['followingCount'],
            record['statusesCount'],
            'Yes' if record['bot'] else '',
            'Yes' if record['locked'] else '',
            'Yes' if record['suspended'] else '',
            record['url'],
            record['avatarUrl'],
        ))

    return data_headers, data_list, source_path


@artifact_processor
def mastodonNotifications(context):
    source_path = _get_source(context)
    data_list = []
    data_headers = (
        ('Timestamp', 'datetime'), 'Type', 'From User', 'From Handle',
        'Related Status', 'Domain', 'Notification ID', 'Recipient User ID')
    if not source_path:
        return data_headers, data_list, ''

    query = f'''
    SELECT
        n.ZCREATEAT,
        n.ZTYPERAW AS notificationType,
        n.ZID AS notificationId,
        n.ZDOMAIN AS domain,
        n.ZUSERID AS recipientUserId,
        u.ZACCT AS fromAcct,
        {AUTHOR_LABEL_SQL} AS fromLabel,
        s.ZCONTENT AS statusContent
    FROM ZNOTIFICATION n
    LEFT JOIN ZMASTODONUSER u ON u.Z_PK = n.ZACCOUNT
    LEFT JOIN ZSTATUS s ON s.Z_PK = n.ZSTATUS
    ORDER BY n.ZCREATEAT
    '''

    for record in get_sqlite_db_records(source_path, query):
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(record['ZCREATEAT']) if record['ZCREATEAT'] else '',
            record['notificationType'],
            record['fromLabel'],
            record['fromAcct'],
            _html_to_text(record['statusContent']),
            record['domain'],
            record['notificationId'],
            record['recipientUserId'],
        ))

    return data_headers, data_list, source_path


@artifact_processor
def mastodonAccount(context):
    source_path = _get_source(context)
    data_list = []
    data_headers = (
        'Display Name', 'Handle', 'Username', 'User ID', 'Instance Domain',
        'Instance Version', 'Bio', 'Followers Count', 'Following Count',
        'Statuses Count', 'Profile URL', 'Avatar URL', 'Identified From')
    if not source_path:
        return data_headers, data_list, ''

    local_user_id = _get_local_user_id(source_path)
    if not local_user_id:
        return data_headers, data_list, source_path

    auth_records = list(get_sqlite_db_records(
        source_path,
        'SELECT ZUSERID FROM ZMASTODONAUTHENTICATION WHERE ZUSERID IS NOT NULL LIMIT 1'))
    identified_from = 'ZMASTODONAUTHENTICATION' if auth_records else 'ZNOTIFICATION owner ID'

    query = f'''
    SELECT
        u.ZDISPLAYNAME AS displayName,
        u.ZACCT AS acct,
        u.ZUSERNAME AS username,
        u.ZID AS userId,
        u.ZNOTE AS note,
        u.ZFOLLOWERSCOUNT AS followersCount,
        u.ZFOLLOWINGCOUNT AS followingCount,
        u.ZSTATUSESCOUNT AS statusesCount,
        u.ZURL AS url,
        u.ZAVATARSTATIC AS avatarUrl,
        i.ZDOMAIN AS instanceDomain,
        i.ZVERSION AS instanceVersion
    FROM ZMASTODONUSER u
    LEFT JOIN ZINSTANCE i ON i.ZDOMAIN = u.ZDOMAIN
    WHERE u.ZID = '{local_user_id}'
    '''

    for record in get_sqlite_db_records(source_path, query):
        data_list.append((
            record['displayName'],
            record['acct'],
            record['username'],
            record['userId'],
            record['instanceDomain'],
            record['instanceVersion'],
            _html_to_text(record['note']),
            record['followersCount'],
            record['followingCount'],
            record['statusesCount'],
            record['url'],
            record['avatarUrl'],
            identified_from,
        ))

    return data_headers, data_list, source_path
