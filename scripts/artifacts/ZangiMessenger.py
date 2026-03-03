# Tested with the following versions:
# App: 5.6.7

__artifacts_v2__ = {

    
    "zangi_messages": {
        "name": "Zangi Messenger - Messages",
        "description": "Zangi Messenger - Messages",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "creatin_date": "2026-03-03",
        "last_update_date": "2026-03-03",
        "requirements": "pathlib",
        "category": "Chats",
        "notes": "",
        "paths": (  
            '*/mobile/Containers/Shared/AppGroup/*/zangidb*.sqlite',
            '*/mobile/Containers/Shared/AppGroup/*/*/image/*/msgId*',
            '*/mobile/Containers/Shared/AppGroup/*/*/video/*/msgId*',
            '*/mobile/Containers/Shared/AppGroup/*/*/file/*/*',
            '*/mobile/Containers/Shared/AppGroup/*/*/voice/*/msgId*',
            '*/mobile/Containers/Shared/AppGroup/*/animations/*'
        ),
        "output_types": "standard",
        'data_views': {
            'conversation': {
                'conversationDiscriminatorColumn': 'Conversation ID',
                'conversationLabelColumn': 'Chat Name',
                'textColumn': 'Message Text',
                'directionColumn': 'Direction',
                'directionSentValue': 'Outgoing',
                'timeColumn': 'Message Timestamp',
                'senderColumn': 'Sender Name',
                'mediaColumn': 'Attachment File'
                }
        },
        "artifact_icon": "message-square"
    },
    "zangi_contacts": {
        "name": "Zangi Messenger - Contacts",
        "description": "Zangi Messenger - Contacts",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "creatin_date": "2026-03-01",
        "last_update_date": "2026-03-01",
        "requirements": "",
        "category": "Contacts",
        "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/zangidb*.sqlite'),
        "output_types": "standard",
        "artifact_icon": "users"
    },
    "zangi_accounts": {
        "name": "Zangi Messenger - Accounts",
        "description": "Zangi Messenger - Accounts",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "creatin_date": "2026-03-01",
        "last_update_date": "2026-03-01",
        "requirements": "",
        "category": "Accounts",
        "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/zangidb*.sqlite'),
        "output_types": "standard",
        "artifact_icon": "user"
    }
}

from pathlib import Path

from scripts.ilapfuncs import artifact_processor, \
    convert_unix_ts_to_utc, get_sqlite_db_records, \
    convert_cocoa_core_data_ts_to_utc, check_in_media

@artifact_processor
def zangi_messages(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    data_list = []

    query = '''
        SELECT
            zm.ZMESSAGETIME [Message Timestamp],
            zm.ZMESSAGE [Message Text],
            CASE
                WHEN grp.Z_PK IS NOT NULL THEN 'Group'
                ELSE 'Direct'
            END [Conversation Type],
            CASE zm.ZTYPE
                WHEN 0   THEN 'Text'
                WHEN 1   THEN 'Image/Media'
                WHEN 2   THEN 'Video'
                WHEN 3   THEN 'Location'
                WHEN 4   THEN 'Voice note'
                WHEN 8   THEN 'Link/Share'
                WHEN 9   THEN 'File/Document'
                WHEN 101 THEN 'System message'
                WHEN 115 THEN 'Group event'
                WHEN 160 THEN 'Call start'
                WHEN 175 THEN 'Call end'
                ELSE 'Other/Unknown'
            END [Message Type],
            zm.ZMESSAGEID [Message ID],
            COALESCE(
                NULLIF(grp.ZUID, ''),
                NULLIF(cnv.ZGROUPUID, ''),
                CAST(cnv.ZUID AS TEXT)
            ) [Conversation ID],
            COALESCE(
                NULLIF(TRIM(gpf.ZNAME), ''),
                NULLIF(TRIM(cnv.ZGROUPNAME), ''),
                NULLIF(TRIM(chat_ct.ZDISPLAYNAME), ''),
                NULLIF(TRIM(COALESCE(chat_ct.ZFIRSTNAME, '') || ' ' || COALESCE(chat_ct.ZLASTNAME, '')), ''),
                chat_cn.ZFULLNUMBER,
                CAST(cnv.ZUID AS TEXT)
            ) [Chat Name],
            COALESCE(
                NULLIF(TRIM(snd_ct.ZDISPLAYNAME), ''),
                NULLIF(TRIM(COALESCE(snd_ct.ZFIRSTNAME, '') || ' ' || COALESCE(snd_ct.ZLASTNAME, '')), ''),
                snd_cn.ZFULLNUMBER,
                CAST(zm.ZFROM AS TEXT)
            ) [Sender Name],
            snd_cn.ZFULLNUMBER [Sender Number],
            CASE
                WHEN zm.ZISRECEIVED = 0 THEN 'Outgoing'
                WHEN zm.ZISRECEIVED = 1 THEN 'Incoming'
                ELSE 'Unknown'
            END [Direction],
            COALESCE(
                NULLIF(zm.ZFILEREMOTEPATH, ''),
                NULLIF(zm.ZMEDIAASSETSLIBRARYURL, ''),
                NULLIF(zm.ZENCRYPTFILEREMOTEPATH, '')
            ) [Media Path],
            zm.ZFILEEXTENSION [Media Extension],
            zm.ZMESSAGEINFO [Message Info]
        FROM ZZANGIMESSAGE zm
        LEFT JOIN ZCONVERSATION cnv         ON cnv.Z_PK = zm.ZCONVERSATION
        LEFT JOIN ZGROUP grp                ON grp.ZCONVERSATION = cnv.Z_PK
        LEFT JOIN ZGROUPPROFILE gpf         ON gpf.ZGROUP = grp.Z_PK
        LEFT JOIN ZCONTACTNUMBER snd_cn     ON snd_cn.Z_PK = zm.ZFROM
        LEFT JOIN Z_4CONTACTNUMBER snd_lnk  ON snd_lnk.Z_5CONTACTNUMBER = snd_cn.Z_PK
        LEFT JOIN ZCONTACT snd_ct           ON snd_ct.Z_PK = snd_lnk.Z_4CONTACT
        LEFT JOIN ZCONTACTNUMBER chat_cn    ON chat_cn.Z_PK = cnv.ZMEMBER
        LEFT JOIN Z_4CONTACTNUMBER chat_lnk ON chat_lnk.Z_5CONTACTNUMBER = chat_cn.Z_PK
        LEFT JOIN ZCONTACT chat_ct          ON chat_ct.Z_PK = chat_lnk.Z_4CONTACT;
    '''

    db_files = []
    media_files = []
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('.sqlite'):
            db_files.append(file_found)
        elif '/image/' in file_found or '/video/' in file_found or '/file/' in file_found or '/voice/' in file_found:
            media_files.append(file_found)

    media_by_msg_id = {}
    media_by_basename = {}
    media_by_name_lower = {}
    media_by_stem_lower = {}
    for media_file in media_files:
        basename = Path(media_file).name
        media_by_basename.setdefault(basename, media_file)
        media_by_name_lower.setdefault(basename.lower(), media_file)
        media_by_stem_lower.setdefault(Path(basename).stem.lower(), media_file)
        if basename.startswith('msgId'):
            media_by_msg_id.setdefault(basename, media_file)

    def _find_media_file(message_id, media_path, message_type, message_text, media_extension):
        media_path_str = (media_path or '').strip()
        found_path = ''
        # First try: find by message_id (file name)
        if message_id:
            found_path = media_by_msg_id.get(message_id, '')

        # Second try: resolve from media path
        if not found_path and media_path_str:
            rel_path = media_path_str.strip('/')
            if rel_path:
                rel_basename = Path(rel_path).name
                if rel_basename and rel_basename.startswith('msgId'):
                    found_path = media_by_basename.get(rel_basename, '')
                if not found_path and 'msgId' in rel_path:
                    for media_file in media_files:
                        if rel_path in media_file:
                            found_path = media_file
                            break

        # File/document fallback: files are often stored by document name, not msgId.
        if not found_path and message_type == 'File/Document':
            clean_text = (message_text or '').strip()
            clean_ext = (media_extension or '').strip().lstrip('.').lower()
            if clean_text:
                if clean_ext:
                    expected_name = f'{clean_text}.{clean_ext}'.lower()
                    found_path = media_by_name_lower.get(expected_name, '')
                if not found_path:
                    found_path = media_by_stem_lower.get(clean_text.lower(), '')

        return found_path

    for main_db in db_files:
        db_records = get_sqlite_db_records(main_db, query)

        for row in db_records:
            message_type = row[3]
            message_id = row[4]
            message_text = row[1]
            media_path = row[10]
            media_extension = row[11]

            media_file_path = _find_media_file(
                message_id,
                media_path,
                message_type,
                message_text,
                media_extension
            )
            attachment_file = ''
            attachment_link = ''
            if media_file_path:
                media_ref = check_in_media(media_file_path, Path(media_file_path).name)
                if message_type in {'Voice note', 'Image/Media'}:
                    attachment_file = media_ref
                else:
                    attachment_link = media_ref

            data_list.append((
                convert_cocoa_core_data_ts_to_utc(row[0]),
                row[1],   # Message ID
                row[2],   # Message Text
                row[3],   # Conversation Type
                row[4],   # Message Type
                row[5],   # Conversation ID
                row[6],   # Chat Name
                row[7],   # Sender Name
                row[8],   # Sender Number
                row[9],   # Direction
                row[10],  # Media Path
                row[11],  # Media Extension
                attachment_file,
                attachment_link,
                main_db
            ))

    data_headers = (
        ('Message Timestamp', 'datetime'),
        'Message Text',
        'Conversation Type',
        'Message Type',
        'Message ID',
        'Conversation ID',
        'Chat Name',
        'Sender Name',
        'Sender Number',
        'Direction',
        'Media Path',
        'Media Extension',
        ('Attachment File', 'media'),
        ('Attachment Link', 'media'),
        'Source Database'
    )

    return data_headers, data_list, 'See Table for Source DB'


@artifact_processor
def zangi_contacts(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):

    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]

    main_db = ''
    data_list = []

    query = '''
            SELECT
                zc.ZMODIFICATIONDATE [Last Modification Timestamp],
                zcn.ZLASTACTIVITY [Last Activity Timestamp],
                zc.ZLASTNAME [Last Name],
                zc.ZFIRSTNAME [First Name],
                zc.ZDISPLAYNAME [Display Name],
                zcn.ZFULLNUMBER [Contact Number],
                zcn.ZEMAIL [Contact Mail],
                zcnt.ZNAME [Registration Number Type],
                zc.ZIDENTIFIRE [Contact ID],
                zc.ZISBLOCKED [Blocked?],
                zcn.ZISFAVORITE [Favorite?]
                FROM ZCONTACT zc
            LEFT JOIN Z_4CONTACTNUMBER z4cn ON zc.Z_PK = z4cn.Z_4CONTACT
            LEFT JOIN ZCONTACTNUMBER zcn ON zcn.Z_PK = z4cn.Z_5CONTACTNUMBER
            LEFT JOIN ZCONTACTNUMBERTYPE zcnt ON zcnt.Z_PK = zc.Z_PK
            '''

    for file_found in files_found:
        main_db = str(file_found)

        db_records = get_sqlite_db_records(main_db, query)

        for row in db_records:
            mod_timestamp = convert_cocoa_core_data_ts_to_utc(row[0])
            last_act_timestmap = convert_unix_ts_to_utc(row[1])
            last_name = row[2]
            first_name = row[3]
            display_name = row[4]
            contact_number = row[5]
            contact_email = row[6]
            reg_type = row[7]
            contact_id = row[8]
            is_blocked = row[9]
            is_favorite = row[10]



            data_list.append((  mod_timestamp,
                                last_act_timestmap,
                                last_name,
                                first_name,
                                display_name,
                                contact_number,
                                contact_email,
                                reg_type,
                                contact_id,
                                is_blocked,
                                is_favorite,
                                main_db))

        data_headers = (    ('Last Modification Timestamp', 'datetime'),
                            ('Last Activity Timestamp', 'datetime'),
                            'Last Name',
                            'First Name', 
                            'Display Name',
                            'Contact Number',
                            'Contact Email',
                            'Registration Type',
                            'Contact ID',
                            'Is Blocked?',
                            'Is Favorite?',
                            'Source Database'
                        )

    return data_headers, data_list, 'See Table for Source DB'


@artifact_processor
def zangi_accounts(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):

    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]

    main_db = ''
    data_list = []

    query = '''
            SELECT
                ZSTATUSLASTSYNCTIME [Last Sync Time],
                ZNUMBER [Account ID],
                ZNICKNAME [Account Name],
                ZLASTNAME [Last Name],
                ZNAME [First Name],ZNICKNAME [Account Name],
                ZNEWPASSCODE [Passcode],
                ZPASSWORD [Password],
                ZPINCODE [PIN Code],
                ZSHAREDHIDECONVERSATIONPIN [HIDE CONVERSATION PIN],
                ZUSEREMAIL [Account Mail],
                ZSTATUS [Account Status],
                ZUSERREGSTATUS [Registration Status],
                ZCOUNTRY [Country]
            FROM ZUSER
            '''

    for file_found in files_found:
        main_db = str(file_found)

        db_records = get_sqlite_db_records(main_db, query)

        for row in db_records:
            timestamp = convert_unix_ts_to_utc(row[0])
            account_id = row[1]
            nickname = row[2]
            lastname = row[3]
            firstname = row[4]
            passcode = row[5]
            password = row[6]
            pincode = row[7]
            hiding_pw = row[8]
            email = row[9]
            status = row[10]
            reg_status = row[11]
            country = row[12]

            data_list.append((  timestamp,
                                account_id,
                                nickname,
                                lastname,
                                firstname,
                                passcode,
                                password,
                                pincode,
                                hiding_pw,
                                email,
                                status,
                                reg_status,
                                country,
                                main_db))

        data_headers = (    ('Last Sync Timestamp', 'datetime'),
                            'Account ID',
                            'Nickname',
                            'Last Name',
                            'First Name',
                            'Passcode',
                            'Password',
                            'PIN Code',
                            'Conversation Hiding Password',
                            'E-Mail',
                            'Status',
                            'Registration Status',
                            'Country',
                            'Source Database'
                        )

    return data_headers, data_list, 'See Table for Source DB'
