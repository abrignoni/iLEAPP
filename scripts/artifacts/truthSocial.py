__artifacts_v2__ = {
    'truthSocialMessages': {
        'name': 'Truth Social - Chats',
        'description': 'Direct messages and chat events from the Truth Social application',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-25',
        'requirements': 'none',
        'category': 'Truth Social',
        'notes': 'Message bodies are stored as HTML fragments; the text is extracted alongside the raw content.',
        'paths': ('*/mobile/Containers/Shared/AppGroup/*/chat/v1/*/ChatModel.sqlite*',),
        'output_types': 'all',
        'artifact_icon': 'message',
        'sample_data': {
            'josh_ios17_ffs': 'iOS 17.3 | 13 message rows, 5 chat events',
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
    'truthSocialChats': {
        'name': 'Truth Social - Chats List',
        'description': 'Chat threads and channels known to the Truth Social application',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-25',
        'requirements': 'none',
        'category': 'Truth Social',
        'notes': '',
        'paths': ('*/mobile/Containers/Shared/AppGroup/*/chat/v1/*/ChatModel.sqlite*',),
        'output_types': 'standard',
        'artifact_icon': 'messages',
        'sample_data': {
            'josh_ios17_ffs': 'iOS 17.3 | 2 rows (1 direct chat, 1 channel)',
        },
    },
    'truthSocialAccounts': {
        'name': 'Truth Social - Accounts',
        'description': 'Truth Social accounts cached by the chat database, including the account holder',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-25',
        'requirements': 'none',
        'category': 'Truth Social',
        'notes': 'The signed-in account ID is taken from the chat ownership column and from the database path.',
        'paths': ('*/mobile/Containers/Shared/AppGroup/*/chat/v1/*/ChatModel.sqlite*',),
        'output_types': 'standard',
        'artifact_icon': 'user',
        'sample_data': {
            'josh_ios17_ffs': 'iOS 17.3 | 3 rows',
        },
    },
}

import html
import re

from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records, convert_cocoa_core_data_ts_to_utc

HTML_TAG_RE = re.compile(r'<[^>]+>')

# Resolves an account ID to a readable handle. Only accounts the app has cached
# appear in ZMANAGEDACCOUNT, so the raw ID is kept as a fallback.
ACCOUNT_LABEL_SQL = '''
    COALESCE(
        NULLIF(acct.ZDISPLAYNAME, '') || ' (@' || acct.ZACCT || ')',
        '@' || acct.ZACCT
    )
'''


def _html_to_text(content):
    """Flatten a Truth Social HTML message body to plain text."""
    if not content:
        return ''
    text = content.replace('</p><p>', '\n').replace('<br>', '\n').replace('<br/>', '\n')
    text = HTML_TAG_RE.sub('', text)
    return html.unescape(text).replace('\xa0', ' ').strip()


@artifact_processor
def truthSocialMessages(context):
    source_path = get_file_path(context.get_files_found(), 'ChatModel.sqlite')
    data_list = []

    query = f'''
    SELECT
        e.ZCREATEDAT,
        e.ZTYPE AS eventType,
        p.Z_NAME AS entityName,
        e.ZCHATID AS chatId,
        e.ZCONTENT AS content,
        e.ZTEXT AS eventText,
        e.ZMESSAGEID AS messageId,
        e.ZISUNREAD AS isUnread,
        e.ZISHIDDEN AS isHidden,
        e.ZFAILEDTOSEND AS failedToSend,
        e.ZMESSAGEEXPIRATION AS messageExpiration,
        e.ZURL AS url,
        e.ZACCOUNTID AS membershipAccountId,
        e.ZCHANGEDBYACCOUNTID AS changedByAccountId,
        e.ZINVITEDACCOUNTID AS invitedAccountId,
        e.ZINVITEDBYACCOUNTID AS invitedByAccountId,
        COALESCE(e.ZACCOUNTID1, e.ZACCOUNTID) AS senderAccountId,
        {ACCOUNT_LABEL_SQL} AS senderLabel,
        chat.ZOWNEDBYACCOUNTID AS ownerAccountId,
        chat.ZTYPE AS chatType,
        other.ZACCT AS otherAcct,
        other.ZDISPLAYNAME AS otherDisplayName,
        chat.ZOTHERACCOUNTID AS otherAccountId,
        (SELECT GROUP_CONCAT(a.ZTYPE, ', ') FROM ZMANAGEDATTACHMENT a
          WHERE a.ZMESSAGE = e.Z_PK) AS attachmentType,
        (SELECT GROUP_CONCAT(COALESCE(a.ZURL, a.ZREMOTEURL), ', ') FROM ZMANAGEDATTACHMENT a
          WHERE a.ZMESSAGE = e.Z_PK) AS attachmentUrl,
        (SELECT GROUP_CONCAT(r.ZNAME, ' ') FROM ZMANAGEDREACTION r
          WHERE r.ZMESSAGE = e.Z_PK) AS reactions
    FROM ZMANAGEDEVENTBASE e
    LEFT JOIN Z_PRIMARYKEY p ON p.Z_ENT = e.Z_ENT
    LEFT JOIN ZMANAGEDCHAT chat ON chat.ZSERVERID = e.ZCHATID
    LEFT JOIN ZMANAGEDACCOUNT acct
        ON acct.ZSERVERID = COALESCE(e.ZACCOUNTID1, e.ZACCOUNTID)
    LEFT JOIN ZMANAGEDACCOUNT other ON other.ZSERVERID = chat.ZOTHERACCOUNTID
    ORDER BY e.ZCREATEDAT
    '''

    for record in get_sqlite_db_records(source_path, query):
        sender_id = record['senderAccountId']
        owner_id = record['ownerAccountId']
        if sender_id and owner_id:
            from_me = 1 if sender_id == owner_id else 0
        else:
            from_me = ''

        conversation = record['otherDisplayName'] or record['otherAcct'] \
            or record['otherAccountId'] or record['chatId']

        data_list.append((
            convert_cocoa_core_data_ts_to_utc(record['ZCREATEDAT']),
            conversation,
            record['chatId'],
            'Channel' if record['chatType'] == 'channel' else 'Direct Message',
            record['eventType'],
            record['senderLabel'] or sender_id,
            sender_id,
            _html_to_text(record['content']) or record['eventText'],
            record['attachmentType'],
            record['attachmentUrl'],
            record['reactions'],
            'Yes' if record['isUnread'] else '',
            'Yes' if record['isHidden'] else '',
            'Yes' if record['failedToSend'] else '',
            record['messageExpiration'],
            record['url'],
            record['membershipAccountId'],
            record['changedByAccountId'],
            record['invitedAccountId'],
            record['invitedByAccountId'],
            record['content'],
            record['messageId'],
            from_me,
        ))

    data_headers = (
        ('Timestamp', 'datetime'), 'Conversation', 'Chat ID', 'Chat Type',
        'Event Type', 'Sender', 'Sender Account ID', 'Message',
        'Attachment Type', 'Attachment URL', 'Reactions', 'Unread', 'Hidden',
        'Failed To Send', 'Message Expiration (Seconds)', 'URL',
        'Membership Account ID', 'Changed By Account ID', 'Invited Account ID',
        'Invited By Account ID', 'Raw HTML Content', 'Message ID', 'From Me')

    return data_headers, data_list, source_path


@artifact_processor
def truthSocialChats(context):
    source_path = get_file_path(context.get_files_found(), 'ChatModel.sqlite')
    data_list = []

    query = '''
    SELECT
        c.ZCREATEDAT,
        c.ZLASTACTIVITYDATE,
        c.ZLASTREADAT,
        c.ZLASTSYNCDATE,
        c.ZSERVERID AS chatId,
        c.ZTYPE AS chatType,
        c.ZOTHERACCOUNTID AS otherAccountId,
        other.ZACCT AS otherAcct,
        other.ZDISPLAYNAME AS otherDisplayName,
        other.ZISVERIFIED AS otherVerified,
        c.ZOWNEDBYACCOUNTID AS ownerAccountId,
        c.ZCREATEDBYACCOUNT AS createdByAccountId,
        c.ZUNREADCOUNT AS unreadCount,
        c.ZMESSAGETTL AS messageTtl,
        c.ZISACCEPTED AS isAccepted,
        c.ZISBLOCKED AS isBlocked,
        c.ZISBLOCKING AS isBlocking,
        c.ZISHIDDEN AS isHidden,
        c.ZISSILENCED AS isSilenced,
        c.ZAVATARURL AS avatarUrl,
        (SELECT COUNT(*) FROM ZMANAGEDEVENTBASE e
          WHERE e.ZCHATID = c.ZSERVERID AND e.ZTYPE = 'message') AS messageCount
    FROM ZMANAGEDCHAT c
    LEFT JOIN ZMANAGEDACCOUNT other ON other.ZSERVERID = c.ZOTHERACCOUNTID
    ORDER BY c.ZCREATEDAT
    '''

    for record in get_sqlite_db_records(source_path, query):
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(record['ZCREATEDAT']) if record['ZCREATEDAT'] else '',
            convert_cocoa_core_data_ts_to_utc(record['ZLASTACTIVITYDATE']) if record['ZLASTACTIVITYDATE'] else '',
            convert_cocoa_core_data_ts_to_utc(record['ZLASTREADAT']) if record['ZLASTREADAT'] else '',
            record['chatId'],
            'Channel' if record['chatType'] == 'channel' else 'Direct Message',
            record['otherDisplayName'],
            record['otherAcct'],
            record['otherAccountId'],
            record['ownerAccountId'],
            record['createdByAccountId'],
            record['messageCount'],
            record['unreadCount'],
            record['messageTtl'],
            'Yes' if record['isAccepted'] else '',
            'Yes' if record['isBlocked'] else '',
            'Yes' if record['isBlocking'] else '',
            'Yes' if record['isHidden'] else '',
            'Yes' if record['isSilenced'] else '',
            'Yes' if record['otherVerified'] else '',
            record['avatarUrl'],
        ))

    data_headers = (
        ('Created', 'datetime'), ('Last Activity', 'datetime'), ('Last Read', 'datetime'),
        'Chat ID', 'Chat Type', 'Other Party Display Name', 'Other Party Handle',
        'Other Party Account ID', 'Owned By Account ID', 'Created By Account ID',
        'Message Count', 'Unread Count', 'Message TTL (Seconds)', 'Accepted',
        'Blocked', 'Blocking', 'Hidden', 'Silenced', 'Other Party Verified',
        'Avatar URL')

    return data_headers, data_list, source_path


@artifact_processor
def truthSocialAccounts(context):
    source_path = get_file_path(context.get_files_found(), 'ChatModel.sqlite')
    data_list = []

    query = '''
    SELECT
        a.ZSERVERID AS accountId,
        a.ZACCT AS handle,
        a.ZDISPLAYNAME AS displayName,
        a.ZISVERIFIED AS verified,
        a.ZAVATARSTATIC AS avatarUrl,
        (SELECT COUNT(*) FROM ZMANAGEDEVENTBASE e
          WHERE COALESCE(e.ZACCOUNTID1, e.ZACCOUNTID) = a.ZSERVERID) AS eventCount
    FROM ZMANAGEDACCOUNT a
    ORDER BY a.ZACCT
    '''

    for record in get_sqlite_db_records(source_path, query):
        data_list.append((
            record['accountId'],
            record['handle'],
            record['displayName'],
            'Yes' if record['verified'] else '',
            '',
            record['eventCount'],
            record['avatarUrl'],
        ))

    # The signed-in account is not stored in ZMANAGEDACCOUNT; it only appears as
    # the owner of each chat thread, so surface it from there.
    owner_query = '''
    SELECT DISTINCT
        c.ZOWNEDBYACCOUNTID AS accountId,
        (SELECT COUNT(*) FROM ZMANAGEDEVENTBASE e
          WHERE COALESCE(e.ZACCOUNTID1, e.ZACCOUNTID) = c.ZOWNEDBYACCOUNTID) AS eventCount
    FROM ZMANAGEDCHAT c
    WHERE c.ZOWNEDBYACCOUNTID IS NOT NULL
      AND c.ZOWNEDBYACCOUNTID NOT IN (SELECT ZSERVERID FROM ZMANAGEDACCOUNT)
    '''

    for record in get_sqlite_db_records(source_path, owner_query):
        data_list.append((
            record['accountId'],
            '',
            '',
            '',
            'Yes',
            record['eventCount'],
            '',
        ))

    data_headers = (
        'Account ID', 'Handle', 'Display Name', 'Verified', 'Account Holder',
        'Event Count', 'Avatar URL')

    return data_headers, data_list, source_path
