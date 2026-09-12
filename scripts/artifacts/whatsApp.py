__artifacts_v2__ = {
    'whatsAppCallHistory': {
        'name': 'WhatsApp - Call History',
        'description': 'Extract call history from WhatsApp',
        'author': '@Vinceckert',
        'creation_date': '2024-05-31',
        'last_update_date': '2026-09-11',
        'requirements': 'none',
        'category': 'WhatsApp',
        'notes': "The ZOUTCOME values 0, 1 and 4 are labelled Ended, Missed and Rejected; that "
                 "mapping has no vendor source and no recorded count, and unrecognized values are "
                 "reported as stored. Incoming (as stored), Video Call, Missed and Missed Reason "
                 "come from the ZWAAGGREGATECALLEVENT row this call belongs to, joined on the "
                 "call's own Z1CALLEVENTS, which the artifact also reports as Aggregate Event ID. "
                 "That row is per group of calls rather than per call: 2 aggregates across the "
                 "tested images covered more than one call, so where two rows share an Aggregate "
                 "Event ID those four columns describe the group and not the individual call. "
                 "Video Call and Missed are the ZVIDEO and ZMISSED booleans rendered Yes and No; "
                 "across the 20 rows of the 5 tested images that hold any, Video Call was Yes on "
                 "12 and Missed was Yes on 4. Missed Reason is reported as stored: the only value "
                 "held is 1, and nothing available defines it. Incoming (as stored) is the app's "
                 "own ZINCOMING flag and Direction beside it is derived from the group call "
                 "creator, so the two are independent readings of the same thing: they agreed on "
                 "all 16 rows where both are present and disagreed on none. On the iOS 14.3 image "
                 "Direction is blank on every row because that release has no group call creator "
                 "column, and the stored flag fills in there. Bytes Sent and Bytes Received are "
                 "the call's own byte counts. Call ID is the call's ZCALLIDSTRING and was present "
                 "on 14 of the 20 rows; the column is absent from the database on the iOS 17.1 "
                 "and 14.3 images. Group JID held no value on any row of any tested image, so no "
                 "group call is recorded among them, and the column is kept because the database "
                 "declares it. The file also holds ZWAJOINABLECALLEVENT, present and empty on "
                 "every tested image, and ZWAUPCOMINGCALLEVENT, present and empty on all but the "
                 "iOS 14.3 image, which does not have it; neither is read. Ending Timestamp is "
                 "the start plus the stored duration, so it equals Starting Timestamp on a call "
                 "of no duration: 7 of the 20 rows have a duration of 00:00:00 and those are "
                 "exactly the rows where the two timestamps are equal, and exactly the rows whose "
                 "Disconnected cause reads Missed. Contact Fullname and Phone Number come from "
                 "the separate address book database and were filled on 12 of the 20 rows, blank "
                 "where the participant has no entry there. Contact ID is the participant the "
                 "call was with and can legitimately repeat: it held a single value across every "
                 "row of the 2 rows of the iOS 17.1 image and the 4 rows of the iOS 14.3 image, "
                 "which is that many calls with the same party.",
        'paths': (
            '*/mobile/Containers/Shared/AppGroup/*/CallHistory.sqlite*',
            '*/mobile/Containers/Shared/AppGroup/*/ContactsV2.sqlite*',
        ),
        'output_types': 'standard',
        'artifact_icon': 'user',
        'sample_data': {
            'ctf2020_ios12': 'iOS 12.4 | net.whatsapp.WhatsApp | 0 rows',
            'dexter_ios18': 'iOS 18.3.2 | WhatsApp Messenger 25.26.72 | 1 row',
            'felix_ios17': 'iOS 17.6.1 | WhatsApp Messenger 24.17.78 | 0 rows',
            'fsfull002_ios17': 'iOS 17.1 | WhatsApp Messenger 23.8.78 | 2 rows',
            'hc_ios18_7': 'iOS 18.7.8 | WhatsApp Messenger 26.14.76 | 0 rows',
            'iphone11_ios17': 'iOS 17.3 | WhatsApp Messenger 24.15.1 | 8 rows',
            'otto_ios17': 'iOS 17.5.1 | WhatsApp Messenger 24.13.79 | 5 rows',
            'abe_ios16': 'iOS 16.5 | WhatsApp Messenger 23.11.80 | 0 rows',
            'felix23_ios16': 'iOS 16.5 | WhatsApp Messenger 23.12.76 | 0 rows',
            'hickman_ios13': 'iOS 13.3.1 | WhatsApp Messenger 2.20.31 | 0 rows',
            'hickman_ios14': 'iOS 14.3 | WhatsApp Messenger 2.21.20 | 4 rows',
            'magnet_ios16': 'iOS 16.1.1 | WhatsApp Messenger 22.23.77 | 0 rows',
        },
    },
    'whatsAppMessages': {
        'name': 'WhatsApp - Messages',
        'description': 'Extract WhatsApp messages',
        'author': '@AlexisBrignoni',
        'creation_date': '2021-03-26',
        'last_update_date': '2026-07-31',
        'requirements': '',
        'category': 'WhatsApp',
        'notes': "Metadata protobuf field meanings have no vendor source and no recorded "
                 "measurement here. Coordinates are emitted only for rows whose ZMESSAGETYPE is "
                 "5; the ZMESSAGETYPE value mapping is not sourced.",
        'paths': (
            '*/mobile/Containers/Shared/AppGroup/*/ChatStorage.sqlite*',
            '*/mobile/Containers/Shared/AppGroup/*/ContactsV2.sqlite*',
            '*/mobile/Containers/Shared/AppGroup/*/Message/Media/*/*/*/*'),
        'output_types': 'all',
        'artifact_icon': 'message',
        'sample_data': {
            'ctf2020_ios12': 'iOS 12.4 | net.whatsapp.WhatsApp | 0 rows',
            'dexter_ios18': 'iOS 18.3.2 | WhatsApp Messenger 25.26.72 | 77 rows',
            'felix_ios17': 'iOS 17.6.1 | WhatsApp Messenger 24.17.78 | 4 rows',
            'fsfull002_ios17': 'iOS 17.1 | WhatsApp Messenger 23.8.78 | 33 rows',
            'hc_ios18_7': 'iOS 18.7.8 | WhatsApp Messenger 26.14.76 | 15 rows',
            'iphone11_ios17': 'iOS 17.3 | WhatsApp Messenger 24.15.1 | 60 rows',
            'otto_ios17': 'iOS 17.5.1 | WhatsApp Messenger 24.13.79 | 1803 rows',
            'abe_ios16': 'iOS 16.5 | WhatsApp Messenger 23.11.80 | 63 rows',
            'felix23_ios16': 'iOS 16.5 | WhatsApp Messenger 23.12.76 | 10 rows',
            'hickman_ios13': 'iOS 13.3.1 | WhatsApp Messenger 2.20.31 | 12 rows',
            'hickman_ios14': 'iOS 14.3 | WhatsApp Messenger 2.21.20 | 17 rows',
            'magnet_ios16': 'iOS 16.1.1 | WhatsApp Messenger 22.23.77 | 0 rows',
        },
        'data_views': {
            'conversation': {
                'conversationDiscriminatorColumn': 'Chat ID',
                'conversationLabelColumn': 'Chat Name',
                'textColumn': 'Message',
                'directionColumn': 'Direction',
                'directionSentValue': 'Outgoing',
                'timeColumn': 'Timestamp',
                'senderColumn': 'Sender Name',
                'mediaColumn': 'Attachment File'
            }
        },
    },
    'whatsAppContacts': {
        'name': 'WhatsApp - Contacts',
        'description': 'Extract contacts registered in WhatsApp',
        'author': '@AlexisBrignoni',
        'creation_date': '2021-03-26',
        'last_update_date': '2025-04-08',
        'requirements': '',
        'category': 'WhatsApp',
        'notes': '',
        'paths': ('*/mobile/Containers/Shared/AppGroup/*/ContactsV2.sqlite*',),
        'output_types': 'standard',
        'artifact_icon': 'users',
        'sample_data': {
            'ctf2020_ios12': 'iOS 12.4 | net.whatsapp.WhatsApp | 21 rows',
            'dexter_ios18': 'iOS 18.3.2 | WhatsApp Messenger 25.26.72 | 10 rows',
            'felix_ios17': 'iOS 17.6.1 | WhatsApp Messenger 24.17.78 | 7 rows',
            'fsfull002_ios17': 'iOS 17.1 | WhatsApp Messenger 23.8.78 | 6 rows',
            'hc_ios18_7': 'iOS 18.7.8 | WhatsApp Messenger 26.14.76 | 2 rows',
            'iphone11_ios17': 'iOS 17.3 | WhatsApp Messenger 24.15.1 | 12 rows',
            'otto_ios17': 'iOS 17.5.1 | WhatsApp Messenger 24.13.79 | 1017 rows',
            'abe_ios16': 'iOS 16.5 | WhatsApp Messenger 23.11.80 | 582 rows',
            'felix23_ios16': 'iOS 16.5 | WhatsApp Messenger 23.12.76 | 6 rows',
            'hickman_ios13': 'iOS 13.3.1 | WhatsApp Messenger 2.20.31 | 3 rows',
            'hickman_ios14': 'iOS 14.3 | WhatsApp Messenger 2.21.20 | 5 rows',
            'magnet_ios16': 'iOS 16.1.1 | WhatsApp Messenger 22.23.77 | 0 rows',
        }
    }
}


from scripts import blackboxprotobuf

from pathlib import Path
from scripts.ilapfuncs import (
    artifact_processor,
    get_file_path,
    get_sqlite_db_records, null_absent_columns,
    attach_sqlite_db_readonly, does_column_exist_in_db, does_table_exist_in_db,
    check_in_media,
    convert_cocoa_core_data_ts_to_utc
)



def _stored(value):
    """A stored value as text, with an absent column and a stored null read the same way."""
    return '' if value is None else value


def _flag(value):
    """A stored boolean rendered Yes or No, blank where the column holds nothing."""
    if value is None:
        return ''
    return 'Yes' if value else 'No'

@artifact_processor
def whatsAppCallHistory(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'CallHistory.sqlite')
    contacts_db = get_file_path(files_found, 'ContactsV2.sqlite')

    data_list = []

    contact_info = '''
        ,base2.ZFULLNAME,
        base2.ZPHONENUMBER
    '''

    # LEFT JOIN on purpose: the address book is an enrichment, not a filter.
    # With INNER JOIN a call whose participant is not in ZWAADDRESSBOOKCONTACT
    # disappeared entirely (on the hickman_ios14 image all 4 calls were dropped
    # because the caller was not among the 5 stored contacts).
    tables_join = '''
    LEFT JOIN ContactsV2.ZWAADDRESSBOOKCONTACT base2 ON ZWACDCALLEVENTPARTICIPANT.ZJIDSTRING = base2.ZWHATSAPPID
    '''

    # Older releases have no group-call creator column. The query is built here
    # rather than passed through null_absent_columns because the contacts branch
    # attaches a second database, which the helper's connection does not have, so
    # it cannot compile the statement to find out what is missing.
    creator = 'ZWACDCALLEVENT.ZGROUPCALLCREATORUSERJIDSTRING'
    if not does_column_exist_in_db(source_path, 'ZWACDCALLEVENT',
                                   'ZGROUPCALLCREATORUSERJIDSTRING'):
        creator = 'NULL'

    # The same file keeps an aggregate row per group of calls and several per-call
    # columns that older releases do not have. Each is resolved the same way, for
    # the same reason: the contacts branch attaches a second database, so
    # null_absent_columns cannot compile the statement to find out what is missing.
    def column(table, name):
        return f'{table}.{name}' if does_column_exist_in_db(source_path, table, name) else 'NULL'

    aggregate = 'ZWAAGGREGATECALLEVENT'
    has_aggregate = does_table_exist_in_db(source_path, aggregate)
    aggregate_columns = ', '.join(
        column(aggregate, name) if has_aggregate else 'NULL'
        for name in ('ZINCOMING', 'ZVIDEO', 'ZMISSED', 'ZMISSEDREASON'))
    event_columns = ', '.join(
        column('ZWACDCALLEVENT', name)
        for name in ('ZBYTESSENT', 'ZBYTESRECEIVED', 'ZCALLIDSTRING', 'ZGROUPJIDSTRING'))
    aggregate_join = (f'LEFT JOIN {aggregate} ON '
                      f'ZWACDCALLEVENT.Z1CALLEVENTS = {aggregate}.Z_PK' if has_aggregate else '')

    query = f'''
    SELECT
        ZWACDCALLEVENT.ZDATE,
        ZWACDCALLEVENT.ZDATE + ZWACDCALLEVENT.ZDURATION AS 'Datetime_end',
        time(ZWACDCALLEVENT.ZDURATION, 'unixepoch') AS 'Duration',
        CASE
            WHEN {creator} = ZWACDCALLEVENTPARTICIPANT.ZJIDSTRING then 'Incoming'
            WHEN {creator} IS NOT NULL
                AND ZWACDCALLEVENTPARTICIPANT.ZJIDSTRING IS NOT NULL THEN 'Outgoing'
            ELSE {creator}
        END Direction,
        CASE ZWACDCALLEVENT.ZOUTCOME
            WHEN 0 THEN 'Ended'
            WHEN 1 THEN 'Missed'
            WHEN 4 THEN 'Rejected'
            ELSE ZWACDCALLEVENT.ZOUTCOME
        END Disconnected_cause,
        ZWACDCALLEVENTPARTICIPANT.ZJIDSTRING as 'Contact ID',
        {aggregate_columns},
        {event_columns},
        ZWACDCALLEVENT.Z1CALLEVENTS
        {contact_info if contacts_db else ''}
    FROM ZWACDCALLEVENT, ZWACDCALLEVENTPARTICIPANT
    {aggregate_join}
    {tables_join if contacts_db else ''}
    WHERE ZWACDCALLEVENT.Z1CALLEVENTS = ZWACDCALLEVENTPARTICIPANT.Z1PARTICIPANTS
    '''
    data_headers = [
        ('Starting Timestamp', 'datetime'),
        ('Ending Timestamp', 'datetime'),
        'Duration H:M:S',
        'Direction',
        'Disconnected cause',
        'Contact ID',
        'Incoming (as stored)',
        'Video Call',
        'Missed',
        'Missed Reason (as stored)',
        'Bytes Sent',
        'Bytes Received',
        'Call ID',
        'Group JID',
        'Aggregate Event ID']

    if contacts_db:
        attach_query = attach_sqlite_db_readonly(contacts_db, 'ContactsV2')
        db_records = get_sqlite_db_records(source_path, query, attach_query)
        data_headers.extend(
            ['Contact Fullname', ('Phone Number', 'phonenumber')])
    else:
        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

    for record in db_records:
        start_time = convert_cocoa_core_data_ts_to_utc(record[0])
        end_time = convert_cocoa_core_data_ts_to_utc(record[1])

        record_data = [
            start_time, end_time, record[2], record[3], record[4], record[5],
            _stored(record[6]), _flag(record[7]), _flag(record[8]), _stored(record[9]),
            _stored(record[10]), _stored(record[11]), _stored(record[12]), _stored(record[13]),
            _stored(record[14])]
        if contacts_db:
            record_data.extend([record[15], record[16]])
        data_list.append(
            tuple(record_data))

    data_headers = tuple(data_headers)
    return data_headers, data_list, source_path


@artifact_processor
def whatsAppContacts(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'ContactsV2.sqlite')
    data_list = []

    query = '''
    SELECT
        ZFULLNAME,
        ZABOUTTEXT,
        ZABOUTTIMESTAMP,
        ZPHONENUMBER,
        ZPHONENUMBERLABEL,
        ZWHATSAPPID,
        ZIDENTIFIER
    FROM ZWAADDRESSBOOKCONTACT
    '''

    data_headers = (
        'Fullname',
        'About Text',
        ('About Text Timestamp', 'datetime'),
        ('Phone Number', 'phonenumber'),
        'Phone Number Label',
        'Whatsapp ID',
        'Identifier')

    db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

    for record in db_records:

        about_timestamp = convert_cocoa_core_data_ts_to_utc(
            record['ZABOUTTIMESTAMP'])
        phone_number_label = record['ZPHONENUMBERLABEL']
        cleaned_label = phone_number_label.replace('_$!<', '').replace(
            '>!$_', '') if phone_number_label else ''

        data_list.append(
            (record[0], record[1], about_timestamp, record[3],
             cleaned_label, record[5], record[6]))

    return data_headers, data_list, source_path


@artifact_processor
def whatsAppMessages(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'ChatStorage.sqlite')
    contacts_db = get_file_path(files_found, 'ContactsV2.sqlite')
    data_list = []

    query = '''
    SELECT
        ZMESSAGEDATE,
        ZISFROMME,
        ZPARTNERNAME,
        ZFROMJID,
        ZTOJID,
        ZWAMESSAGE.ZMEDIAITEM,
        ZTEXT,
        ZSTARRED,
        ZMESSAGETYPE,
        ZLONGITUDE,
        ZLATITUDE,
        ZMEDIALOCALPATH,
        ZXMPPTHUMBPATH,
        ZMETADATA,
        ZWACHATSESSION.ZCONTACTJID
    FROM ZWAMESSAGE
    LEFT JOIN ZWAMEDIAITEM ON ZWAMESSAGE.Z_PK = ZWAMEDIAITEM.ZMESSAGE
    LEFT JOIN ZWACHATSESSION ON ZWACHATSESSION.Z_PK = ZWAMESSAGE.ZCHATSESSION
    '''

    data_headers = (
        ('Timestamp', 'datetime'),
        'Direction',
        'Sender Name',
        'Chat Name',
        'Message',
        ('Attachment File', 'media'),
        'From ID',
        'Receiver',
        'To ID',
        ('Thumb', 'media'),
        'Starred?',
        'Metadata Field 17 (forward count, observed)',
        'Metadata Field 21 (forwarder, observed)',
        'Latitude',
        'Longitude',
        'Chat ID',
        )

    db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

    for record in db_records:
        message_date = convert_cocoa_core_data_ts_to_utc(
            record['ZMESSAGEDATE'])

        sender = 'Local User' if record['ZISFROMME'] == 1 else record['ZPARTNERNAME']
        receiver = record['ZPARTNERNAME'] if record['ZISFROMME'] == 1 else 'Local User'

        attach_file = ''
        media_local_path = record['ZMEDIALOCALPATH']
        if media_local_path:
            attach_file_name = Path(media_local_path).name
            attach_file = check_in_media(media_local_path, attach_file_name)

        thumb = ''
        thumb_path = record['ZXMPPTHUMBPATH']
        if thumb_path:
            thumb_name = Path(thumb_path).name
            thumb = check_in_media(thumb_path, thumb_name)

        metadata = record['ZMETADATA']
        number_forward = ''
        from_forward = ''
        if metadata:
            try:
                decoded_data, _ = blackboxprotobuf.decode_message(metadata)
                number_forward = f'{decoded_data.get("17", "")}'
                forward_id = decoded_data.get("21")
                from_forward = forward_id.decode("utf-8") if isinstance(forward_id, bytes) else ''
                if contacts_db and from_forward:
                    attach_query = attach_sqlite_db_readonly(contacts_db, 'ContactsV2')
                    query_contact = f"""
                                SELECT
                                    ZWHATSAPPID,
                                    ZFULLNAME,
                                    ZPHONENUMBER
                                FROM ContactsV2.ZWAADDRESSBOOKCONTACT
                                WHERE ZWHATSAPPID = '{from_forward}'
                            """
                    contact_records = list( get_sqlite_db_records(source_path, query_contact, attach_query) )
                    if contact_records:
                        forwardedwhatsappid, fullname, phone = contact_records[0]
                        from_forward = f"{fullname} ({phone}) - ({forwardedwhatsappid})"

            except (TypeError, ValueError, KeyError):
                pass

        lon = record['ZLONGITUDE'] if record['ZMESSAGETYPE'] == 5 else ''
        lat = record['ZLATITUDE'] if record['ZMESSAGETYPE'] == 5 else ''

        direction = 'Outgoing' if record['ZISFROMME'] == 1 else 'Incoming'
        data_list.append((
            message_date,
            direction,
            sender,
            record['ZPARTNERNAME'],
            record['ZTEXT'],
            attach_file,
            record['ZFROMJID'],
            receiver,
            record['ZTOJID'],
            thumb,
            record['ZSTARRED'],
            number_forward,
            from_forward,
            lat,
            lon,
            record['ZCONTACTJID'],
        ))

    return data_headers, data_list, source_path
