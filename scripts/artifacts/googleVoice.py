__artifacts_v2__ = {
    'googleVoiceMessages': {
        'name': 'Google Voice - Messages',
        'description': 'SMS/MMS messages exchanged through the Google Voice application',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-25',
        'requirements': 'none',
        'category': 'Google Voice',
        'notes': '',
        'paths': ('*/mobile/Containers/Shared/AppGroup/*/threadingStore.sqlite*',),
        'output_types': 'all',
        'artifact_icon': 'message',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | Josh Hickman image | 118 rows (60 in, 58 out)',
        },
        'data_views': {
            'conversation': {
                'conversationDiscriminatorColumn': 'Thread Key',
                'conversationLabelColumn': 'Conversation',
                'textColumn': 'Message',
                'directionColumn': 'From Me',
                'directionSentValue': 1,
                'timeColumn': 'Timestamp',
                'senderColumn': 'Sender',
            }
        }
    },
    'googleVoiceCalls': {
        'name': 'Google Voice - Calls',
        'description': 'Incoming, outgoing and missed calls handled by the Google Voice application',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-25',
        'requirements': 'none',
        'category': 'Google Voice',
        'notes': '',
        'paths': ('*/mobile/Containers/Shared/AppGroup/*/threadingStore.sqlite*',),
        'output_types': 'standard',
        'artifact_icon': 'phone',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | Josh Hickman image | 29 rows (3 incoming, 6 outgoing, 20 missed)',
        },
    },
    'googleVoiceVoicemails': {
        'name': 'Google Voice - Voicemails',
        'description': 'Voicemails left on the Google Voice number, including the machine transcription',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-25',
        'requirements': 'none',
        'category': 'Google Voice',
        'notes': '',
        'paths': ('*/mobile/Containers/Shared/AppGroup/*/threadingStore.sqlite*',),
        'output_types': 'standard',
        'artifact_icon': 'voicemail',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | Josh Hickman image | 5 rows, 4 with a transcript',
        },
    },
    'googleVoiceContacts': {
        'name': 'Google Voice - Contacts',
        'description': 'Phone numbers stored in the Google Voice threading database (participants)',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-31',
        'requirements': 'none',
        'category': 'Google Voice',
        'notes': '',
        'paths': ('*/mobile/Containers/Shared/AppGroup/*/threadingStore.sqlite*',),
        'output_types': 'standard',
        'artifact_icon': 'address-book',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | Josh Hickman image | 24 rows',
        },
    },
}

from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records, convert_unix_ts_to_utc

# ThreadItem.itemType values seen in the Google Voice threading store. The app
# stores direction in the item type itself rather than in a separate column.
OUTGOING_ITEM_TYPES = ('SmsOut', 'OutgoingCall')

CALL_DIRECTIONS = {
    'IncomingCall': 'Incoming',
    'OutgoingCall': 'Outgoing',
    'MissedCall': 'Missed',
}


# Names the conversation a thread belongs to. senderPhoneNumber is not usable
# here: on outgoing items it holds the local Google Voice number, so labelling
# from it splits a single conversation in two. Group threads carry a groupName;
# everything else is named after the thread's participants.
THREAD_LABEL_SQL = '''
    COALESCE(
        th.groupName,
        (SELECT GROUP_CONCAT(tp.phoneNumberE164, ', ')
           FROM ThreadParticipant tp
          WHERE tp.threadKey = ti.threadKey AND tp.threadType = ti.threadType),
        ti.threadKey
    ) AS conversation
'''


@artifact_processor
def googleVoiceMessages(context):
    source_path = get_file_path(context.get_files_found(), 'threadingStore.sqlite')
    data_list = []

    query = f'''
    SELECT
        ti.timestamp,
        ti.itemType,
        ti.messageText,
        ti.senderPhoneNumber,
        ti.isUnread,
        ti.isDeleted,
        ti.isSystemMessage,
        ti.threadKey,
        {THREAD_LABEL_SQL},
        (SELECT COUNT(*) FROM MMSAttachmentInfo ma
          WHERE ma.threadItemKey = ti.threadItemKey
            AND ma.threadItemType = ti.threadItemType) AS attachmentCount
    FROM ThreadItem ti
    LEFT JOIN Thread th
        ON th.threadKey = ti.threadKey AND th.threadType = ti.threadType
    WHERE ti.itemType IN ('SmsIn', 'SmsOut')
    ORDER BY ti.sortID
    '''

    for record in get_sqlite_db_records(source_path, query):
        from_me = 1 if record['itemType'] in OUTGOING_ITEM_TYPES else 0
        data_list.append((
            convert_unix_ts_to_utc(record['timestamp']),
            from_me,
            record['senderPhoneNumber'],
            record['conversation'],
            record['messageText'],
            record['threadKey'],
            'Outgoing' if from_me else 'Incoming',
            record['attachmentCount'],
            record['isUnread'],
            record['isDeleted'],
            record['isSystemMessage'],
        ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'From Me',
        ('Sender', 'phonenumber'),
        'Conversation',
        'Message',
        'Thread Key',
        'Direction',
        'Attachment Count',
        'Unread',
        'Deleted',
        'System Message',
    )

    return data_headers, data_list, source_path


@artifact_processor
def googleVoiceCalls(context):
    source_path = get_file_path(context.get_files_found(), 'threadingStore.sqlite')
    data_list = []

    query = '''
    SELECT
        ti.timestamp,
        ti.itemType,
        ti.senderPhoneNumber,
        ti.duration,
        ti.ringGroupName,
        ti.ringGroupPhoneNumber,
        ti.transferredFromE164,
        ti.transferredToE164,
        ti.isDeleted,
        ti.threadKey
    FROM ThreadItem ti
    WHERE ti.itemType IN ('IncomingCall', 'OutgoingCall', 'MissedCall')
    ORDER BY ti.sortID
    '''

    for record in get_sqlite_db_records(source_path, query):
        data_list.append((
            convert_unix_ts_to_utc(record['timestamp']),
            CALL_DIRECTIONS.get(record['itemType'], record['itemType']),
            record['senderPhoneNumber'],
            record['duration'],
            record['ringGroupName'],
            record['ringGroupPhoneNumber'],
            record['transferredFromE164'],
            record['transferredToE164'],
            record['isDeleted'],
            record['threadKey'],
        ))

    data_headers = (
        ('Timestamp', 'datetime'), 'Direction', ('Other Party', 'phonenumber'),
        'Duration (Seconds)', 'Ring Group Name', 'Ring Group Number',
        'Transferred From', 'Transferred To', 'Deleted', 'Thread Key')

    return data_headers, data_list, source_path


@artifact_processor
def googleVoiceVoicemails(context):
    source_path = get_file_path(context.get_files_found(), 'threadingStore.sqlite')
    data_list = []

    query = '''
    SELECT
        ti.timestamp,
        ti.senderPhoneNumber,
        ti.duration,
        ti.isUnread,
        ti.isDeleted,
        ti.threadKey,
        tr.text AS transcript,
        tr.confidence
    FROM ThreadItem ti
    LEFT JOIN Transcript tr
        ON tr.threadItemKey = ti.threadItemKey
       AND tr.threadItemType = ti.threadItemType
    WHERE ti.itemType = 'Voicemail'
    ORDER BY ti.sortID
    '''

    for record in get_sqlite_db_records(source_path, query):
        data_list.append((
            convert_unix_ts_to_utc(record['timestamp']),
            record['senderPhoneNumber'],
            record['duration'],
            record['transcript'],
            record['confidence'],
            record['isUnread'],
            record['isDeleted'],
            record['threadKey'],
        ))

    data_headers = (
        ('Timestamp', 'datetime'), ('Caller', 'phonenumber'), 'Duration (Seconds)',
        'Transcript', 'Transcript Confidence', 'Unread', 'Deleted', 'Thread Key')

    return data_headers, data_list, source_path


@artifact_processor
def googleVoiceContacts(context):
    source_path = get_file_path(context.get_files_found(), 'threadingStore.sqlite')
    data_list = []

    query = '''
    SELECT
        p.phoneNumberE164,
        p.isBlocked,
        COUNT(DISTINCT tp.threadKey) AS threadCount,
        (SELECT COUNT(*) FROM ThreadItem ti
          WHERE ti.senderPhoneNumber = p.phoneNumberE164) AS itemCount,
        (SELECT MAX(ti.timestamp) FROM ThreadItem ti
          WHERE ti.senderPhoneNumber = p.phoneNumberE164) AS lastSeen
    FROM Participant p
    LEFT JOIN ThreadParticipant tp
        ON tp.phoneNumberE164 = p.phoneNumberE164
    GROUP BY p.phoneNumberE164
    ORDER BY p.phoneNumberE164
    '''

    for record in get_sqlite_db_records(source_path, query):
        last_seen = record['lastSeen']
        data_list.append((
            convert_unix_ts_to_utc(last_seen) if last_seen else '',
            record['phoneNumberE164'],
            record['isBlocked'],
            record['threadCount'],
            record['itemCount'],
        ))

    data_headers = (
        ('Last Activity', 'datetime'), ('Phone Number', 'phonenumber'), 'Blocked',
        'Thread Count', 'Item Count')

    return data_headers, data_list, source_path
