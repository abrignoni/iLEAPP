# Tested with the following versions:
# App: 5.6.7

__artifacts_v2__ = {

    
    "zangi_messages": {
        "name": "Zangi Messenger - Messages",
        "description": "Messages from the Zangi Messenger database, joined to its conversation, "
                       "group and contact tables, with direction, sender, chat name, text, "
                       "message type and the attachment file where one is found by name among the "
                       "image, video, file and voice folders of the app group folder that holds "
                       "the database (by message id, by the stored "
                       "media path, or for documents by the message text); only voice "
                       "note and image rows fill Attachment File, other types fill Attachment "
                       "Link. Reads two database layouts: the older ZZANGIMESSAGE table and the "
                       "newer ZZMESSAGE family, whichever a database carries.",
        "author": "Marco Neumann {kalinko@be-binary.de}, @AlexisBrignoni, Codex",
        "creatin_date": "2026-03-03",
        "creation_date": "2026-03-03",
        "last_update_date": "2026-10-09",
        "requirements": "pathlib",
        "category": "Chats",
        "notes": "Message type labels are a reading of rows from app version 5.6.7 and are not "
                 "vendor-documented. Which of the eleven mapped codes the tested data held is not "
                 "recorded here. On the newer layout the Message Type label for an unmapped code is "
                 "cast to text. On the older layout it is Other/Unknown. ZTYPE (as stored) "
                 "separately retains the native SQLite value on each joined row in both layouts; "
                 "it does not establish what the code means. The module reads two database layouts and produces "
                 "the same columns from each. A row is one joined row: a message that matches "
                 "more than one group, contact, sender or media row is listed once per match. The "
                 "layouts are the older single ZZANGIMESSAGE table, and the newer layout where "
                 "message data moved to a ZZMESSAGE table with per-message sender rows in "
                 "ZZMESSAGEUSER and attachments in ZZMESSAGEMEDIA. The layout is selected per "
                 "database from the table present. The newer layout, including its sender, "
                 "chat-name, media-path and timestamp mapping, was field mapped from a private "
                 "sample; no sample data is recorded for that sample. ZMESSAGETIME on the newer "
                 "layout is read as a Cocoa/Core Data timestamp, and Direction is derived from "
                 "ZISRECEIVED (0 outgoing, 1 incoming); neither reading is sourced, and what in "
                 "that sample supports them is not recorded here. The same two readings are "
                 "applied to the older layout. The attachment is matched by file name and is not "
                 "a link the store records; only files under the app group folder that holds "
                 "the database are considered, and where more than one file there carries the "
                 "same name the first in path order is used.",
        "paths": (  
            '*/mobile/Containers/Shared/AppGroup/*/zangidb*.sqlite*',
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
        "artifact_icon": "message",
        "sample_data": {
            "iphone14plus_ios18": "iOS 18.0 | Zangi Private Messenger 5.6.7 | 19 rows",
        }
    },
    "zangi_contacts": {
        "name": "Zangi Messenger - Contacts",
        "description": "Contacts from the Zangi Messenger database (ZCONTACT with its numbers), "
                       "with names, number, email, number type name, blocked and favourite flags "
                       "and modification and activity times. The modification time is read as "
                       "seconds from 2001 and the activity time as Unix time; neither reading "
                       "has been checked on data here, because the one image recorded in "
                       "sample_data returned no contact rows.",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "creatin_date": "2026-03-01",
        "creation_date": "2026-03-01",
        "last_update_date": "2026-10-04",
        "requirements": "",
        "category": "Contacts",
        "notes": "Number Type holds ZNAME of the ZCONTACTNUMBERTYPE row that the number's own "
                 "ZCONTACTNUMBER.ZTYPE column points at. The Core Data model shipped with the "
                 "app on iphone14plus_ios18 (zangidb 7.7, whose version hashes equal the "
                 "store's) defines that column as the to-one relationship named type from "
                 "ContactNumber to ContactNumberType, so the value belongs to the number on "
                 "the row and not to the contact. On that image the user's store held 2 "
                 "ZCONTACTNUMBER rows, both resolving to the 1 ZCONTACTNUMBERTYPE row, whose "
                 "ZNAME is empty, and no ZCONTACT row, so the artifact returned no rows and "
                 "the column was exercised only on a constructed copy of that store. What "
                 "the type names mean is not established. Where a database has no "
                 "ZCONTACTNUMBER.ZTYPE column the Number Type column is left blank.",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/zangidb*.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "iphone14plus_ios18": "iOS 18.0 | Zangi Private Messenger 5.6.7 | 0 rows",
        }
    },
    "zangi_accounts": {
        "name": "Zangi Messenger - Accounts",
        "description": "Account rows from the ZUSER table of the Zangi Messenger database, with "
                       "the number stored as ZNUMBER (shown as Account ID), names, email, status, "
                       "registration status, country, the passcode, password, PIN and hidden "
                       "conversation PIN (shown as Conversation Hiding Password) fields as "
                       "stored, and ZSTATUSLASTSYNCTIME read as Unix time (shown as Last Sync "
                       "Timestamp).",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "creatin_date": "2026-03-01",
        "creation_date": "2026-03-01",
        "last_update_date": "2026-09-22",
        "requirements": "",
        "category": "Accounts",
        "notes": "The ZUSER columns are selected per database from the columns present, so a "
                 "column absent on a given app version (ZSTATUS is missing on the layout seen in "
                 "a private sample) is reported blank rather than failing the query.",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/zangidb*.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "iphone14plus_ios18": "iOS 18.0 | Zangi Private Messenger 5.6.7 | 1 row",
        }
    }
}

from pathlib import Path

from scripts.ilapfuncs import artifact_processor, \
    convert_unix_ts_to_utc, get_sqlite_db_records, \
    convert_cocoa_core_data_ts_to_utc, check_in_media, \
    does_table_exist_in_db

@artifact_processor
def zangi_messages(context):
    files_found = [x for x in context.get_files_found() if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]
    data_list = []

    # Older layout: a single ZZANGIMESSAGE table with inline media columns. Kept so
    # extractions from earlier app versions keep parsing.
    query_legacy = '''
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
            zm.ZMESSAGEINFO [Message Info],
            zm.ZTYPE [ZTYPE (as stored)]
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

    # Newer layout: message data moved to ZZMESSAGE, with the sender in a per-message
    # ZZMESSAGEUSER row and the attachment in a per-message ZZMESSAGEMEDIA row. Returns
    # the same columns in the same order as the legacy query so the row handling below is
    # shared. Unmapped Message Type labels are cast to text; raw ZTYPE is separate.
    query_new = '''
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
                ELSE CAST(zm.ZTYPE AS TEXT)
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
                mu.ZFULLNUMBER
            ) [Sender Name],
            COALESCE(snd_cn.ZFULLNUMBER, mu.ZFULLNUMBER) [Sender Number],
            CASE
                WHEN zm.ZISRECEIVED = 0 THEN 'Outgoing'
                WHEN zm.ZISRECEIVED = 1 THEN 'Incoming'
                ELSE 'Unknown'
            END [Direction],
            COALESCE(
                NULLIF(mm.ZFILEREMOTEPATH, ''),
                NULLIF(mm.ZMEDIAASSETSLIBRARYURL, '')
            ) [Media Path],
            mm.ZFILEEXTENSION [Media Extension],
            zm.ZMESSAGEINFO [Message Info],
            zm.ZTYPE [ZTYPE (as stored)]
        FROM ZZMESSAGE zm
        LEFT JOIN ZCONVERSATION cnv         ON cnv.Z_PK = zm.ZCONVERSATION
        LEFT JOIN ZGROUP grp                ON grp.ZCONVERSATION = cnv.Z_PK
        LEFT JOIN ZGROUPPROFILE gpf         ON gpf.ZGROUP = grp.Z_PK
        LEFT JOIN ZZMESSAGEUSER mu          ON mu.ZMESSAGE = zm.Z_PK
        LEFT JOIN ZCONTACTNUMBER snd_cn     ON snd_cn.Z_PK = mu.ZCONTACTNUMBER
        LEFT JOIN Z_4CONTACTNUMBER snd_lnk  ON snd_lnk.Z_5CONTACTNUMBER = snd_cn.Z_PK
        LEFT JOIN ZCONTACT snd_ct           ON snd_ct.Z_PK = snd_lnk.Z_4CONTACT
        LEFT JOIN ZZMESSAGEMEDIA mm         ON mm.ZMESSAGE = zm.Z_PK
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

    all_media_files = sorted(media_files)

    def _index_media(group_dir):
        """Index the media files under the app group folder holding a database."""
        prefix = group_dir.replace('\\', '/').rstrip('/') + '/'
        group_media = [m for m in all_media_files
                       if m.replace('\\', '/').startswith(prefix)]
        by_msg_id = {}
        by_basename = {}
        by_name_lower = {}
        by_stem_lower = {}
        for media_file in group_media:
            basename = Path(media_file).name
            by_basename.setdefault(basename, media_file)
            by_name_lower.setdefault(basename.lower(), media_file)
            by_stem_lower.setdefault(Path(basename).stem.lower(), media_file)
            if basename.startswith('msgId'):
                by_msg_id.setdefault(basename, media_file)
        return group_media, by_msg_id, by_basename, by_name_lower, by_stem_lower

    def _find_media_file(index, message_id, media_path, message_type, message_text, media_extension):
        (media_files, media_by_msg_id, media_by_basename,
         media_by_name_lower, media_by_stem_lower) = index
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
        source_db = context.get_relative_path(main_db)
        if does_table_exist_in_db(main_db, 'ZZMESSAGE'):
            query = query_new
        elif does_table_exist_in_db(main_db, 'ZZANGIMESSAGE'):
            query = query_legacy
        else:
            continue
        db_records = get_sqlite_db_records(main_db, query)
        # Attachments are looked up only under the app group folder that holds
        # this database, so one group's file is not shown on another's message.
        media_index = _index_media(str(Path(main_db).parent))

        for row in db_records:
            message_type = row[3]
            message_id = row[4]
            message_text = row[1]
            media_path = row[10]
            media_extension = row[11]

            media_file_path = _find_media_file(
                media_index,
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
                row[9],
                row[7],
                row[6],
                row[1],
                attachment_file,
                row[2],
                row[3],
                row[13],
                row[4],
                row[5],
                row[8],
                row[10],
                row[11],
                attachment_link,
                source_db,
            ))

    data_headers = (
        ('Message Timestamp', 'datetime'),
        'Direction',
        'Sender Name',
        'Chat Name',
        'Message Text',
        ('Attachment File', 'media'),
        'Conversation Type',
        'Message Type',
        'ZTYPE (as stored)',
        'Message ID',
        'Conversation ID',
        'Sender Number',
        'Media Path',
        'Media Extension',
        ('Attachment Link', 'media'),
        'Source Database',
    )

    return data_headers, data_list, '\n'.join(sorted(set(db_files)))


@artifact_processor
def zangi_contacts(context):

    files_found = [x for x in context.get_files_found() if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]

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
                {number_type} [Number Type],
                zc.ZIDENTIFIRE [Contact ID],
                zc.ZISBLOCKED [Blocked?],
                zcn.ZISFAVORITE [Favorite?]
                FROM ZCONTACT zc
            LEFT JOIN Z_4CONTACTNUMBER z4cn ON zc.Z_PK = z4cn.Z_4CONTACT
            LEFT JOIN ZCONTACTNUMBER zcn ON zcn.Z_PK = z4cn.Z_5CONTACTNUMBER
            {type_join}
            '''

    source_files = set()
    data_headers = (    ('Last Modification Timestamp', 'datetime'),
                        ('Last Activity Timestamp', 'datetime'),
                        'Last Name',
                        'First Name', 
                        'Display Name',
                        'Contact Number',
                        'Contact Email',
                        'Number Type',
                        'Contact ID',
                        'Is Blocked?',
                        'Is Favorite?',
                        'Source Database'
                    )

    for file_found in files_found:
        main_db = str(file_found)
        source_files.add(main_db)
        source_db = context.get_relative_path(main_db)

        # The number type is linked from the number row (ZCONTACTNUMBER.ZTYPE holds the
        # ZCONTACTNUMBERTYPE row key). Without that column no type is reported.
        number_columns = {r['name'].upper()
                          for r in get_sqlite_db_records(
                              main_db, "PRAGMA table_info('ZCONTACTNUMBER')")}
        if 'ZTYPE' in number_columns and does_table_exist_in_db(main_db, 'ZCONTACTNUMBERTYPE'):
            db_query = query.format(
                number_type='zcnt.ZNAME',
                type_join='LEFT JOIN ZCONTACTNUMBERTYPE zcnt ON zcnt.Z_PK = zcn.ZTYPE')
        else:
            db_query = query.format(number_type='NULL', type_join='')

        db_records = get_sqlite_db_records(main_db, db_query)

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
                                source_db))

    return data_headers, data_list, '\n'.join(sorted(source_files))


@artifact_processor
def zangi_accounts(context):

    files_found = [x for x in context.get_files_found() if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]

    main_db = ''
    data_list = []

    # ZUSER columns in the order the data_headers below expect them. Selected per database
    # from the columns present, so a column absent on a given app version (ZSTATUS is
    # missing on an older layout) is returned as NULL instead of failing the whole query.
    account_columns = (
        'ZSTATUSLASTSYNCTIME',
        'ZNUMBER',
        'ZNICKNAME',
        'ZLASTNAME',
        'ZNAME',
        'ZNEWPASSCODE',
        'ZPASSWORD',
        'ZPINCODE',
        'ZSHAREDHIDECONVERSATIONPIN',
        'ZUSEREMAIL',
        'ZSTATUS',
        'ZUSERREGSTATUS',
        'ZCOUNTRY',
    )

    source_files = set()
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

    for file_found in files_found:
        main_db = str(file_found)
        source_files.add(main_db)
        source_db = context.get_relative_path(main_db)

        if not does_table_exist_in_db(main_db, 'ZUSER'):
            continue

        present_columns = {r['name'].upper()
                           for r in get_sqlite_db_records(
                               main_db, "PRAGMA table_info('ZUSER')")}
        select_columns = ', '.join(
            col if col in present_columns else 'NULL' for col in account_columns)
        query = f'SELECT {select_columns} FROM ZUSER'

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
                                source_db))

    return data_headers, data_list, '\n'.join(sorted(source_files))
