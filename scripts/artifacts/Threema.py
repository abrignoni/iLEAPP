__artifacts_v2__ = {
    'threema_chats': {
        'name': 'Threema - Chats',
        'description': 'Extract chats from Threema',
        'author': '@C_Peter',
        'creation_date': '2026-01-03',
        'last_update_date': '2022-01-03',
        'requirements': 'none',
        'category': 'Threema',
        'notes': '',
        'paths': (
            '*/mobile/Containers/Shared/AppGroup/*/ThreemaData.sqlite*',
            '*/mobile/Containers/Shared/AppGroup/*/.ThreemaData_SUPPORT/_EXTERNAL_DATA/*',
        ),
        'output_types': 'standard',
        'artifact_icon': 'message-square',
        'data_views': {
            'conversation': {
                'conversationDiscriminatorColumn': 'Chat-ID',
                'conversationLabelColumn': 'Chat',
                'textColumn': 'Message',
                'directionColumn': 'From Me',
                'directionSentValue': 1,
                'timeColumn': 'Timestamp',
                'senderColumn': 'Sender Name',
                'mediaColumn': 'Attachment File'
            }
        }
    },
    'threema_users': {
        'name': 'Threema - Known Users',
        'description': 'Extract known users from Threema',
        'author': '@C_Peter',
        'creation_date': '2026-01-03',
        'last_update_date': '2022-01-03',
        'requirements': 'none',
        'category': 'Threema',
        'notes': '',
        'paths': (
            '*/mobile/Containers/Shared/AppGroup/*/ThreemaData.sqlite*',
        ),
        'output_types': 'standard',
        'artifact_icon': 'users',
    }
}

import datetime
from pathlib import Path
from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records, \
    check_in_media, check_in_embedded_media

@artifact_processor
def threema_chats(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    source_path = get_file_path(files_found, 'ThreemaData.sqlite')
    data_list = []

    chat_query = '''
        SELECT
            m.Z_PK AS MID,
            m.ZDATE as COCOA,
            conv.Z_PK as C_ID,
            m.ZISOWN as OUT,
            CASE
                WHEN conv.ZGROUPNAME IS NOT NULL
                    THEN conv.ZGROUPNAME
                WHEN cont.ZFIRSTNAME IS NOT NULL AND cont.ZLASTNAME IS NULL
                    THEN cont.ZFIRSTNAME
                WHEN cont.ZFIRSTNAME IS NOT NULL AND cont.ZLASTNAME IS NOT NULL
                    THEN cont.ZFIRSTNAME || ' ' || cont.ZLASTNAME
                WHEN cont.ZFIRSTNAME IS NULL AND cont.ZLASTNAME IS NOT NULL
                    THEN cont.ZLASTNAME
                ELSE cont.ZPUBLICNICKNAME
            END AS CHAT,

            CASE
                WHEN m.ZISOWN = 1 THEN
                    'local user'

                WHEN m.ZSENDER IS NOT NULL THEN
                    CASE
                        WHEN sd.ZFIRSTNAME IS NOT NULL AND sd.ZLASTNAME IS NULL
                            THEN sd.ZFIRSTNAME
                        WHEN sd.ZFIRSTNAME IS NOT NULL AND sd.ZLASTNAME IS NOT NULL
                            THEN sd.ZFIRSTNAME || ' ' || sd.ZLASTNAME
                        WHEN sd.ZFIRSTNAME IS NULL AND sd.ZLASTNAME IS NOT NULL
                            THEN sd.ZLASTNAME
                        ELSE sd.ZPUBLICNICKNAME
                    END

                ELSE
                    CASE
                        WHEN conv.ZGROUPNAME IS NOT NULL
                            THEN conv.ZGROUPNAME
                        WHEN cont.ZFIRSTNAME IS NOT NULL AND cont.ZLASTNAME IS NULL
                            THEN cont.ZFIRSTNAME
                        WHEN cont.ZFIRSTNAME IS NOT NULL AND cont.ZLASTNAME IS NOT NULL
                            THEN cont.ZFIRSTNAME || ' ' || cont.ZLASTNAME
                        WHEN cont.ZFIRSTNAME IS NULL AND cont.ZLASTNAME IS NOT NULL
                            THEN cont.ZLASTNAME
                        ELSE cont.ZPUBLICNICKNAME
                    END
            END AS SENDER,
            CASE
                WHEN m.ZISOWN = 0 THEN
                    'local user'
                ELSE
                    CASE
                        WHEN conv.ZGROUPNAME IS NOT NULL
                            THEN conv.ZGROUPNAME
                        WHEN cont.ZFIRSTNAME IS NOT NULL AND cont.ZLASTNAME IS NULL
                            THEN cont.ZFIRSTNAME
                        WHEN cont.ZFIRSTNAME IS NOT NULL AND cont.ZLASTNAME IS NOT NULL
                            THEN cont.ZFIRSTNAME || ' ' || cont.ZLASTNAME
                        WHEN cont.ZFIRSTNAME IS NULL AND cont.ZLASTNAME IS NOT NULL
                            THEN cont.ZLASTNAME
                        ELSE cont.ZPUBLICNICKNAME
                    END 
                END AS RECEIVER,		
            m.ZREAD as "READ",
            p.Z_NAME as "MTYPE",
            CASE 
                WHEN m.ZTEXT IS NOT NULL THEN m.ZTEXT
                WHEN m.ZCAPTION IS NOT NULL THEN m.ZCAPTION
                ELSE NULL
            END AS MESSAGE,
            CASE
                WHEN ad.ZDATA IS NOT NULL THEN ad.ZDATA
                WHEN vd.ZDATA IS NOT NULL THEN vd.ZDATA
                WHEN id.ZDATA IS NOT NULL THEN id.ZDATA
                WHEN fd.ZDATA IS NOT NULL THEN fd.ZDATA
                ELSE NULL
            END AS MEDIA,
            CASE
                WHEN tn.ZDATA IS NOT NULL THEN tn.ZDATA
                ELSE NULL
            END AS THUMBNAIL,
            m.ZFILENAME AS FILENAME,
            m.ZMIMETYPE AS MIMETYPE,
            m.ZLATITUDE AS LATITUDE,
            m.ZLONGITUDE AS LONGITUDE,
            m.ZACCURACY AS ACCURACY
        FROM
            ZMESSAGE m
        JOIN
            Z_PRIMARYKEY p
            ON m.Z_ENT = p.Z_ENT
        LEFT JOIN ZAUDIODATA ad ON ad.Z_PK = m.ZAUDIO
        LEFT JOIN ZVIDEODATA vd ON vd.Z_PK = m.ZVIDEO
        LEFT JOIN ZIMAGEDATA id ON id.Z_PK = m.ZIMAGE
        LEFT JOIN ZFILEDATA fd ON fd.ZMESSAGE = m.Z_PK
        LEFT JOIN ZIMAGEDATA tn ON tn.Z_PK = m.ZTHUMBNAIL
        LEFT JOIN ZCONTACT sd ON sd.Z_PK = m.ZSENDER
        LEFT JOIN
            ZCONVERSATION conv
                ON m.ZCONVERSATION = conv.Z_PK
        LEFT JOIN
            ZCONTACT cont
                ON conv.ZCONTACT = cont.Z_PK;
        '''

    db_records = get_sqlite_db_records(source_path, chat_query)

    for record in db_records:
        m_type = record['MTYPE']
        #Date is in cocoa time
        message_date = datetime.datetime.fromtimestamp(record['COCOA'] + \
                       978307200, tz=datetime.timezone.utc)
        chat_id = record['C_ID']
        chat_name = record['CHAT']
        message_id = record['MID']
        sender = record['SENDER']
        receiver = record['RECEIVER']
        outgoing = record['OUT']
        message = record['MESSAGE']
        longitude = record['LONGITUDE']
        latitude = record['LATITUDE']
        accuracy = record['ACCURACY']
        attachment = record['MEDIA']
        filename = record['FILENAME']
        mimetype = record['MIMETYPE']
        mime = None
        if "image" in m_type.lower():
            mime = "image/jpeg"
        elif "video" in m_type.lower():
            mime = "video/mp4"
        elif "audio" in m_type.lower():
            mime = "audio/m4a"
        elif "file" in m_type.lower():
            if mimetype is not None:
                mime = mimetype
        attach_file = ''
        if attachment:
            if attachment[0] == 0x01:
                attach_blob = attachment[1:]
                attach_file_name = "embedded_file"
                attach_file = check_in_embedded_media("ThreemaData.sqlite", attach_blob, attach_file_name)
            if attachment[0] == 0x02 and attachment[-1] == 0x00:
                try:
                    attach_uuid = str(attachment[1:-1].decode("ascii"))
                except UnicodeDecodeError:
                    attach_uuid = None
                if attach_uuid is not None:
                    media_local_path = f'.ThreemaData_SUPPORT/_EXTERNAL_DATA/{attach_uuid}'
                    if filename is not None:
                        attach_file_name = filename
                    else:
                        attach_file_name = Path(media_local_path).name
                    if mime is not None:
                        attach_file = check_in_media(media_local_path, attach_file_name, force_type=mime)
                    else:
                        attach_file = check_in_media(media_local_path, attach_file_name)
            else:
                attach_file = ''

        if m_type == "SystemMessage":
            continue

        data_list.append((message_date, chat_name, chat_id, message_id, sender, receiver, m_type, message, attach_file, latitude, longitude, accuracy, outgoing))

    data_headers = (
        ('Timestamp', 'datetime'), 'Chat', 'Chat-ID', 'Message-ID', 'Sender Name', 'Receiver', 'Message Type',
        'Message', ('Attachment File', 'media'), 'Latitude', 'Longitude', 'Accuracy', 'From Me')

    return data_headers, data_list, source_path

@artifact_processor
def threema_users(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    source_path = get_file_path(files_found, 'ThreemaData.sqlite')
    data_list = []

    user_query = '''
        SELECT
            ZCNCONTACTID AS CID,
            ZIDENTITY AS IDENTITY,
            ZFIRSTNAME AS FIRSTNAME,
            ZLASTNAME AS LASTNAME,
            ZPUBLICNICKNAME AS NICKNAME
        FROM
            ZCONTACT;
    '''

    db_records = get_sqlite_db_records(source_path, user_query)
    for record in db_records:
        c_id = record['CID']
        identity = record['IDENTITY']
        first_name = record['FIRSTNAME']
        last_name = record['LASTNAME']
        nickname = record['NICKNAME']

        data_list.append((identity, first_name, last_name, nickname, c_id))

    data_headers = (
        'Identity', 'First Name', 'Last Name', 'Nickname', 'Contact ID')

    return data_headers, data_list, source_path
