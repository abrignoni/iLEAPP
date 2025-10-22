""" See descriptions below """

__artifacts_v2__ = {
    'viber_settings': {
        'name': 'Viber - Settings',
        'description': "Parses settings db, extracts and reports on user's available "
                       "information regarding Viber settings.",
        'author': 'Evangelos Dragonas (@theAtropos4n6)',
        'creation_date': '2022-03-09',
        'last_update_date': '2025-10-10',
        'requirements': '',
        'category': 'Viber',
        'notes': '',
        'paths': ('*/com.viber/settings/Settings.data',),
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'settings'
    },
    'viber_contacts': {
        'name': 'Viber - Contacts',
        'description': "Parses contacts db, extracts and reports on user's contacts. "
                       "Be advised that a contact may not participate in a chat "
                       "(therefore a contact is not a chat 'member') and vice versa. "
                       "A chat 'member' may not be registered as a Viber contact.",
        'author': 'Evangelos Dragonas (@theAtropos4n6)',
        'creation_date': '2022-03-09',
        'last_update_date': '2025-10-11',
        'requirements': '',
        'category': 'Viber',
        'notes': '',
        'paths': ('**/com.viber/database/Contacts.data*',),
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'users'
    },
    'viber_call_remnants': {
        'name': 'Viber - Call Remnants',
        'description': "Parses contacts db, extracts and reports on user's "
                       "recent calls that have no corresponding message (ZVIBERMESSAGE) "
                       "entry, indicating these messages have been deleted.",
        'author': 'Evangelos Dragonas (@theAtropos4n6)',
        'creation_date': '2022-03-09',
        'last_update_date': '2025-10-11',
        'requirements': '',
        'category': 'Viber',
        'notes': '',
        'paths': ('**/com.viber/database/Contacts.data*',),
        'output_types': "standard",
        'artifact_icon': 'phone-call'
    },
    'viber_chats': {
        'name': 'Viber - Chats',
        'description': "Parses contacts db, extracts and reports on user's chats, "
                       "including extra columns with each chat's grouped participants "
                       "and phone numbers.",
        'author': 'Evangelos Dragonas (@theAtropos4n6)',
        'creation_date': '2022-03-09',
        'last_update_date': '2025-10-12',
        'requirements': '',
        'category': 'Viber',
        'notes': '',
        'paths': (
            '**/com.viber/database/Contacts.data*',
            '**/Containers/Data/Application/*/Documents/Attachments/*.*',
            '**/com.viber/ViberIcons/*.*'),
        'output_types': "all",
        'artifact_icon': 'message-square'
    }

}

import json
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, logfunc, \
    convert_unix_ts_to_utc, convert_cocoa_core_data_ts_to_utc, get_birthdate_from_unix_ts, \
    check_in_media, check_in_embedded_media


@artifact_processor
def viber_settings(context):
    """ See artifact description """
    data_source = context.get_source_file_path('Settings.data')
    data_list = []

    query = '''
    SELECT Data.key,value
    FROM Data
    WHERE Data.key IN
        (
        '_myUserName',
        '_currentEmail',
        '_myPhoneNumber',
        '_myCanonizedPhoneNumber',
        '_myFormattedPhoneNumber',
        '_myCountryPhoneCode',
        '_myCountryCode',
        '_myLanguageCode',
        '_wasabiLastKnownUserLocation',
        '_uid',
        '_appVersion',
        '_savedDeviceId',
        '_attemptsToDownloadBackupForRestore',
        '_backupAttemptsCount',
        '_hiddenChatsPINData',
        '_myPhotoLocalID',
        '_registrationDate',
        '_autoBackupLastRunTime',
        '_lastBackupStartDate',
        '_birthdate')
    ORDER BY value
    '''

    data_headers = ('Setting', 'Value')

    db_records = get_sqlite_db_records(data_source, query)

    for record in db_records:
        setting = ''
        value = record[1]
        if record[0] == '_appVersion':
            setting = 'Application Version'
        elif record[0] == '_lastBackupStartDate':
            setting = 'Last Backup Start Date - UTC'
        elif record[0] == '_myUserName':
            setting = 'User Name'
        elif record[0] == '_currentEmail':
            setting = 'Current Email'
        elif record[0] == '_birthdate':
            setting = "Birth Date - UTC (apply user's localtime offset)"
            value = get_birthdate_from_unix_ts(record[1])
        elif record[0] == '_registrationDate':
            setting = 'Registration Date - UTC'
            value = convert_unix_ts_to_utc(record[1])
        elif record[0] == '_uid':
            setting = 'User ID'
        elif record[0] == '_myPhoneNumber':
            setting = 'Phone Number'
        elif record[0] == '_myCanonizedPhoneNumber':
            setting = 'Canonized Phone Number'
        elif record[0] == '_myFormattedPhoneNumber':
            setting = 'Formatted Phone Number'
        elif record[0] == '_myCountryPhoneCode':
            setting = 'Country Phone Code'
        elif record[0] == '_myCountryCode':
            setting = 'Country Code'
        elif record[0] == '_myLanguageCode':
            setting = 'Language Code'
        elif record[0] == '_wasabiLastKnownUserLocation':
            setting = 'Last Known User Location'
        elif record[0] == '_savedDeviceId':
            setting = 'Device ID'
        elif record[0] == '_myPhotoLocalID':
            setting = 'Profile Picture'
            if record[1] is not None and isinstance(record[1], bytes):
                thumb = check_in_embedded_media(data_source, record[1], "Viber Profile Picture")
                value = thumb
        elif record[0] == '_attemptsToDownloadBackupForRestore':
            setting = 'Attempts To Download Backup For Restore'
            try:
                int.from_bytes(record[1], byteorder='big')  # needs further validation about the byteorder
            except TypeError as err:
                error_message = "Viber - Settings '_attemptsToDownloadBackupForRestore' could not be extracted. "
                error_message += f"The error was: {err}"
                logfunc(error_message)
        elif record[0] == '_backupAttemptsCount':
            setting = 'Backup Attempts Count'
            try:
                int.from_bytes(record[1], byteorder='big')  # needs further validation about the byteorder
            except TypeError as err:
                error_message = "Viber - Settings '_backupAttemptsCount' could not be extracted. "
                error_message += f"The error was: {err}"
                logfunc(error_message)
        elif record[0] == '_autoBackupLastRunTime':
            setting = 'Auto Backup Last Run Time - UTC'
            x = str(record[1])
            if x.startswith("-"):
                value = 'Not Applied'
            else:
                value = convert_unix_ts_to_utc(record[1])
        elif record[0] == '_lastBackupStartDate':
            x = str(record[1])
            if x.startswith("-"):
                value = 'Not Applied'
            else:
                value = convert_unix_ts_to_utc(record[1])
        elif record[0] == '_hiddenChatsPINData':
            setting = 'Hidden Chats PIN Data'
        data_list.append((setting, value))

    return data_headers, data_list, data_source


@artifact_processor
def viber_contacts(context):
    """ See artifact description """
    data_source = context.get_source_file_path('Contacts.data')
    data_list = []

    query = '''
    SELECT
        ZABCONTACT.ZMAINNAME AS 'Main Name',
        ZABCONTACT.ZPREFIXNAME AS 'Prefix Name',
        ZABCONTACT.ZSUFFIXNAME AS 'Suffix Name',
        ZABCONTACTNUMBER.ZPHONE AS 'Phone Number',
        ZABCONTACTNUMBER.ZCANONIZEDPHONENUM AS 'Canonized Phone Number',
        ZABCONTACT.ZCONTACTID AS 'Contact ID'
    FROM ZABCONTACT
    LEFT JOIN ZABCONTACTNUMBER ON ZABCONTACT.Z_PK = ZABCONTACTNUMBER.ZCONTACT
    UNION
    SELECT
        ZABCONTACT.ZMAINNAME AS 'Main Name',
        ZABCONTACT.ZPREFIXNAME AS 'Prefix Name',
        ZABCONTACT.ZSUFFIXNAME AS 'Suffix Name',
        ZABCONTACTNUMBER.ZPHONE AS 'Phone Number',
        ZABCONTACTNUMBER.ZCANONIZEDPHONENUM AS 'Canonized Phone Number',
        ZABCONTACT.ZCONTACTID AS 'Contact ID'
    FROM ZABCONTACTNUMBER
    LEFT JOIN ZABCONTACT ON ZABCONTACT.Z_PK = ZABCONTACTNUMBER.ZCONTACT
    ORDER BY ZMAINNAME
    '''

    data_headers = ('Main Name', 'Prefix Name', 'Suffix Name', 'Phone Number',
                    'Canonized Phone Number', 'Contact ID')

    db_records = get_sqlite_db_records(data_source, query)

    for record in db_records:
        data_list.append((record[0], record[1], record[2], record[3], record[4], record[5]))

    return data_headers, data_list, data_source


@artifact_processor
def viber_call_remnants(context):
    """ See artifact description """
    data_source = context.get_source_file_path('Contacts.data')
    data_list = []

    query = '''
    SELECT
        ZRECENT.ZDATE AS 'Timestamp - UTC',
        ZRECENT.ZRECENTSLINE AS 'EMPTY DUMMY COLUMN',
        CASE
            WHEN ZRECENT.ZCALLTYPE = 'missed' THEN 'Missed Audio Call'
            WHEN ZRECENT.ZCALLTYPE = 'missed_with_video' THEN 'Missed Video Call'
            WHEN ZRECENT.ZCALLTYPE = 'outgoing_viber' THEN 'Outgoing Audio Call'
            WHEN ZRECENT.ZCALLTYPE = 'outgoing_viber_with_video' THEN 'Outgoing Video Call'
            WHEN ZRECENT.ZCALLTYPE = 'incoming_with_video' THEN 'Incoming Video Call'
            WHEN ZRECENT.ZCALLTYPE = 'incoming' THEN 'Incoming Audio Call'
            ELSE ZRECENT.ZCALLTYPE
        end AS 'Call Type',
        ZRECENT.ZDURATION AS 'Duration'
    FROM ZRECENT
    WHERE ZRECENT.ZCALLLOGMESSAGE IS NULL AND ZRECENT.ZRECENTSLINE IS NULL
    '''

    data_headers = (
        ('Timestamp - UTC', 'datetime'), 'Caller', 'Call Type', 'Duration')

    db_records = get_sqlite_db_records(data_source, query)

    my_user_name = ''
    my_phone_number = ''

    if db_records:
        user_query = '''
        SELECT Data.key, value
        FROM Data
        WHERE Data.key IN ('_myUserName', '_myPhoneNumber')'''
        user_db_records = get_sqlite_db_records(data_source, user_query)
        for user_record in user_db_records:
            if user_record[0] == '_myUserName':
                my_user_name = user_record[1]
            elif user_record[0] == '_myPhoneNumber':
                my_phone_number = user_record[1]

    for record in db_records:
        timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        if 'Outgoing' in record[2]:
            record[1] = f"{my_user_name}, {my_phone_number}"
        data_list.append((timestamp, record[1], record[2], record[3]))

    return data_headers, data_list, data_source


@artifact_processor
def viber_chats(context):
    """ See artifact description """
    data_source = context.get_source_file_path('Contacts.data')
    data_list = []

    query = '''
    SELECT
        CHAT_MEMBER.ZDISPLAYFULLNAME AS 'Sender (Display Full Name)',
        CHAT_MEMBER.ZDISPLAYSHORTNAME AS 'Sender (Display Short Name)',
        CHAT_MEMBER.ZPHONE AS 'Sender (Phone)',
        CHATS.Chat_Name AS 'Chat Name',
        CHATS.CHAT_MEMBERS AS 'Chat Participant(s)',
        CHATS.CHAT_PHONES 'Chat Phone(s)',
        ZVIBERMESSAGE.ZSTATEDATE AS 'Message Creation Date - UTC',
        ZVIBERMESSAGE.ZDATE AS 'Message Change State Date - UTC',
        RECENT.ZRECENTDATE AS 'Call Date - UTC',
        CASE
            WHEN ZCALLTYPE = 'missed' THEN 'Missed Audio Call'
            WHEN ZCALLTYPE = 'missed_with_video' THEN 'Missed Video Call'
            WHEN ZCALLTYPE = 'outgoing_viber' THEN 'Outgoing Audio Call'
            WHEN ZCALLTYPE = 'outgoing_viber_with_video' THEN 'Outgoing Video Call'
            WHEN ZCALLTYPE = 'incoming_with_video' THEN 'Incoming Video Call'
            WHEN ZCALLTYPE = 'incoming' THEN 'Incoming Audio Call'
            ELSE ZCALLTYPE
        END AS 'Call Type',
        CASE
            WHEN ZVIBERMESSAGE.ZSTATE IN ('send','delivered') THEN 'Outgoing'
            WHEN ZVIBERMESSAGE.ZSTATE = 'received' THEN 'Incoming'
            ELSE ZVIBERMESSAGE.ZSTATE
        END AS 'State',
        RECENT.ZDURATION AS 'Duration',
        ZVIBERMESSAGE.ZSYSTEMTYPE 'System Type Description',
        ZVIBERMESSAGE.ZMETADATA AS 'Message Metadata',
        ZVIBERMESSAGE.ZTEXT AS 'Message Content',
        ZATTACHMENT.ZNAME AS 'Attachment Name',
        ZATTACHMENT.ZTYPE AS 'Attachment Type',
        ZATTACHMENT.ZFILESIZE AS 'Attachment Size',
        ZVIBERLOCATION.ZLATITUDE AS 'Latitude',
        ZVIBERLOCATION.ZLONGITUDE AS 'Longitude',
        CASE
            WHEN CHATS.Chat_Deleted = 1 THEN 'True'
            WHEN CHATS.Chat_Deleted = 0 THEN 'False'
            ELSE CHATS.Chat_Deleted
        END AS 'Conversation Deleted',
        CASE
            WHEN ZVIBERMESSAGE.ZBEINGDELETED = 1 THEN 'True'
            WHEN ZVIBERMESSAGE.ZBEINGDELETED = 0 THEN 'False'
            ELSE ZVIBERMESSAGE.ZBEINGDELETED
        END AS 'Message Deleted',
        CHATS.ZTIMEBOMBDURATION AS 'Conversation Time Bomb Duration',
        ZVIBERMESSAGE.ZTIMEBOMBDURATION AS 'Message Time Bomb Duration',
        ZVIBERMESSAGE.ZTIMEBOMBTIMESTAMP AS 'Message Time Bomb Timestamp',
        CASE
            WHEN CHATS.Chat_Favorite= 1 THEN 'True'
            WHEN CHATS.Chat_Favorite = 0 THEN 'False'
            ELSE CHATS.Chat_Favorite
        END AS 'Conversation Marked Favorite',
        ZVIBERMESSAGE.ZLIKESCOUNT AS 'Likes Count'
    FROM ZVIBERMESSAGE
    LEFT JOIN
    (SELECT
        ZVIBERMESSAGE.ZCONVERSATION,
        ZCONVERSATION.ZNAME AS 'Chat_Name',
        ZCONVERSATION.ZBEINGDELETED AS 'Chat_Deleted',
        ZCONVERSATION.ZFAVORITE AS 'Chat_Favorite',
        ZCONVERSATION.ZTIMEBOMBDURATION,
        coalesce(ZVIBERMESSAGE.ZPHONENUMINDEX,ZCONVERSATION.ZINTERLOCUTOR) AS 'MEMBER_ID',
        MEMBER.ZDISPLAYFULLNAME,
        MEMBER.ZDISPLAYSHORTNAME,
        MEMBER.ZNAME AS 'Participant_Name',
        MEMBER.ZCANONIZEDPHONENUM,
        MEMBER.ZPHONE,
        group_concat(DISTINCT(MEMBER.ZDISPLAYFULLNAME)) AS 'CHAT_MEMBERS',
        group_concat(DISTINCT(MEMBER.ZPHONE)) AS 'CHAT_PHONES',
        group_concat(DISTINCT(MEMBER.ZCANONIZEDPHONENUM)) AS 'CHAT_CANONIZED_PHONES'
    FROM ZVIBERMESSAGE,ZCONVERSATION
    LEFT JOIN
    (SELECT
        ZMEMBER.ZDISPLAYFULLNAME,
        ZMEMBER.ZDISPLAYSHORTNAME,
        ZMEMBER.ZNAME,
        ZPHONENUMBER.ZCANONIZEDPHONENUM,
        ZPHONENUMBER.ZPHONE,
        ZMEMBER.Z_PK
    FROM ZMEMBER
    LEFT JOIN ZPHONENUMBER ON ZMEMBER.Z_PK = ZPHONENUMBER.ZMEMBER
    UNION
    SELECT
        ZMEMBER.ZDISPLAYFULLNAME,
        ZMEMBER.ZDISPLAYSHORTNAME,
        ZMEMBER.ZNAME,
        ZPHONENUMBER.ZCANONIZEDPHONENUM,
        ZPHONENUMBER.ZPHONE,
        ZMEMBER.Z_PK
    FROM ZPHONENUMBER
    LEFT JOIN ZMEMBER ON ZPHONENUMBER.ZMEMBER  = ZMEMBER.Z_PK
    ) AS MEMBER ON MEMBER.Z_PK = MEMBER_ID
    LEFT JOIN ZPHONENUMBER ON MEMBER_ID = ZPHONENUMBER.ZMEMBER
    WHERE ZVIBERMESSAGE.ZCONVERSATION = ZCONVERSATION.Z_PK
    GROUP BY ZVIBERMESSAGE.ZCONVERSATION
    ) CHATS ON ZVIBERMESSAGE.ZCONVERSATION = CHATS.ZCONVERSATION
    LEFT JOIN
    (SELECT
        ZMEMBER.ZDISPLAYFULLNAME,
        ZMEMBER.ZDISPLAYSHORTNAME,
        ZMEMBER.ZNAME,
        ZPHONENUMBER.ZCANONIZEDPHONENUM,
        ZPHONENUMBER.ZPHONE,
        ZMEMBER.Z_PK
    FROM ZMEMBER
    LEFT JOIN ZPHONENUMBER ON ZMEMBER.Z_PK = ZPHONENUMBER.ZMEMBER
    UNION
    SELECT
        ZMEMBER.ZDISPLAYFULLNAME,
        ZMEMBER.ZDISPLAYSHORTNAME,
        ZMEMBER.ZNAME,
        ZPHONENUMBER.ZCANONIZEDPHONENUM,
        ZPHONENUMBER.ZPHONE,
        ZMEMBER.Z_PK
    FROM ZPHONENUMBER
    LEFT JOIN ZMEMBER ON ZPHONENUMBER.ZMEMBER  = ZMEMBER.Z_PK
    ) AS CHAT_MEMBER ON ZVIBERMESSAGE.ZPHONENUMINDEX = CHAT_MEMBER.Z_PK
    LEFT JOIN
    (SELECT
        ZRECENT.ZDURATION,
        ZRECENT.ZCALLLOGMESSAGE,
        ZRECENT.ZDATE AS 'ZRECENTDATE',
        ZRECENTSLINE.ZDATE AS 'ZRECENTSLINEDATE',
        ZRECENT.ZCALLTYPE AS 'CALL TYPE',
        ZRECENTSLINE.ZCALLTYPE AS 'CALL TYPE',
        ZRECENTSLINE.ZPHONENUMBER AS 'PHONE NUMBER'
    FROM ZRECENT
    LEFT JOIN ZRECENTSLINE ON ZRECENT.ZRECENTSLINE = ZRECENTSLINE.Z_PK
    ) AS RECENT ON ZVIBERMESSAGE.Z_PK = RECENT.ZCALLLOGMESSAGE
    LEFT JOIN ZVIBERLOCATION ON ZVIBERMESSAGE.ZLOCATION = ZVIBERLOCATION.Z_PK
    LEFT JOIN ZATTACHMENT ON ZVIBERMESSAGE.ZATTACHMENT = ZATTACHMENT.Z_PK
    ORDER BY ZVIBERMESSAGE.Z_PK
    '''

    data_headers = (
        ('Timestamp', 'datetime'), 'Sender (Display Full Name)', 'Sender (Display Short Name)',
        'Sender (Phone)', 'Chat Name', 'Chat Participant(s)', 'Chat Phone(s)',
        'Message Creation Date - UTC', 'Message Change State Date - UTC',
        'Message Content', 'Attachment Name', ('Attachment', 'media'), 'Call Date - UTC',
        'Call Type', 'State', 'Duration (Seconds)', 'System Type Description',
        'Attachment Type', 'Attachment Size', 'Latitude', 'Longitude', 'Conversation Deleted',
        'Message Deleted', 'Conversation Time Bomb Duration', 'Message Time Bomb Duration',
        'Message Time Bomb Timestamp - UTC', 'Conversation Marked Favorite', 'Likes Count',
        'Message Metadata Fragments')

    db_records = get_sqlite_db_records(data_source, query)

    my_user_name = ''
    my_phone_number = ''

    if db_records:
        user_query = '''
        SELECT Data.key, value
        FROM Data
        WHERE Data.key IN ('_myUserName', '_myPhoneNumber')'''
        user_db_records = get_sqlite_db_records(data_source, user_query)
        for user_record in user_db_records:
            if user_record[0] == '_myUserName':
                my_user_name = user_record[1]
            elif user_record[0] == '_myPhoneNumber':
                my_phone_number = user_record[1]

    for record in db_records:
        temp_list = list(record)
        temp_chats_names = str(temp_list[4])
        temp_list[4] = f"{temp_chats_names}, {my_user_name}"
        temp_chats_phones = str(temp_list[5])
        temp_list[5] = f"{temp_chats_phones}, {my_phone_number}"
        if temp_list[13]:
            # the key that stores geolocation data is
            # ['pa_message_data']['rich_media']['Buttons'][2]['Map']
            # if the 'Map' key is identified successfully it will assign
            # lat,lon to the corresponding columns, otherwise it will continue
            # on (passing any key,index errors)
            y = json.loads(temp_list[13], strict=False)
            temp_list[13] = ''
            # What this ugly long list of dict keys simply does is that it extracts
            # only specific fields identified as important from the whole dictionary.
            # The reason why we extract only specific fields is because the report
            # is much prettier. In order to have a complete picture you will have
            # to go through the whole dictionary while inspecting the .db itself.
            # Therefore this column is named as 'Message Metadata Fragments'
            try:
                temp_list[18] = y['pa_message_data']['rich_media']['Buttons'][2]['Map']['Latitude']
                temp_list[19] = y['pa_message_data']['rich_media']['Buttons'][2]['Map']['Longitude']
            except (KeyError, IndexError):
                pass

            # general values
            if "Text" in y:
                try:
                    temp_list[13] += "Text: " + str(y['Text']) + ","
                except KeyError:
                    pass
            if "Title" in y:
                try:
                    temp_list[13] += "Title: " + str(y['Title']) + ","
                except KeyError:
                    pass
            if "URL" in y:
                try:
                    temp_list[13] += "URL: " + str(y['URL']) + ","
                except KeyError:
                    pass
            if "ThumbnailURL" in y:
                try:
                    temp_list[13] += "ThumbnailURL: " + str(y['ThumbnailURL']) + ","
                except KeyError:
                    pass
            if "Type" in y:
                try:
                    temp_list[13] += "Type: " + str(y['Type']) + ","
                except KeyError:
                    pass

            if "generalFwdInfo" in y:
                try:
                    temp_list[13] += "Original Chat ID: " + \
                        str(y['generalFwdInfo']['orig_chat_id']) + ","
                except KeyError:
                    pass

            if "audio_ptt" in y:
                try:
                    temp_list[13] += "Audio Duration: " + \
                        str(y['audio_ptt']['duration']) + ","
                except KeyError:
                    pass

            # fileInfo values
            if "fileInfo" in y:
                try:
                    temp_list[13] += "File Info - Content Type: " + \
                        str(y['fileInfo']['ContentType']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "File Info - Type: " + \
                        str(y['fileInfo']['Type']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "File Info - Hash: " + \
                        str(y['fileInfo']['FileHash']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "File Info - Name: " + \
                        str(y['fileInfo']['FileName']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "File Info - Extension: " + \
                        str(y['fileInfo']['FileExt']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "File Info - Duration: " + \
                        str(y['fileInfo']['Duration']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "File Info - Size: " + \
                        str(y['fileInfo']['FileSize']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "File Info - Original Size: " + \
                        str(y['fileInfo']['OrigSize']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "File|Media Info - iOS Origin: " + \
                        str(y['fileInfo']['mediaInfo']['ios_origin']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "File|Media Info - Width: " + \
                        str(y['fileInfo']['mediaInfo']['Width']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "File|Media Info - Height: " + \
                        str(y['fileInfo']['mediaInfo']['Height']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "File|Media Info - Media Type: " + \
                        str(y['fileInfo']['mediaInfo']['MediaType']) + ","
                except KeyError:
                    pass

            # custom_sticker_info values
            if "custom_sticker_info" in y:
                try:
                    temp_list[13] += "Custom Sticker Info - Package ID: " + \
                        str(y['custom_sticker_info']['package_id']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "Custom Sticker Info - Sticker ID: " + \
                        str(y['custom_sticker_info']['sticker_id'])+","
                except KeyError:
                    pass

            # groupReferralInfo values
            if "groupReferralInfo" in y:
                try:
                    temp_list[13] += "Group ID: " + str(y['groupReferralInfo']['groupID']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "Group Name: " + str(y['groupReferralInfo']['groupName']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "Invite Link: " + str(y['groupReferralInfo']['inviteLink']) + ","
                except KeyError:
                    pass

            # pa_message_data values
            if "pa_message_data" in y:
                try:
                    temp_list[13] += "Message Data - Text: " + \
                        str(y['pa_message_data']['text']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "Message Data - Sender Name: " + \
                        str(y['pa_message_data']['sender']['name']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "Message Data - Alt Text: " + \
                        str(y['pa_message_data']['alt_text']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "Message Data - Favorites Metadata - URL: " + \
                        str(y['pa_message_data']['rich_media']['FavoritesMetadata']['url']) + ","
                except KeyError:
                    pass

            # pin values
            if "pin" in y:
                try:
                    temp_list[13] += "Pin - Action: " + str(y['pin']['action']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "Pin - Text: " + str(y['pin']['text']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "Pin - Description: " + \
                        str(y['pin']['extended']['descr']) + ","
                except KeyError:
                    pass

            # poll values
            if "poll" in y:
                try:
                    temp_list[13] += "Poll - Group ID: " + str(y['poll']['groupID']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "Poll - Type: " + str(y['poll']['type']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "Poll - Sender ID: " + str(y['poll']['senderID']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "Poll - Multiple: " + str(y['poll']['multiple']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "Poll - Quiz Text: " + str(y['poll']['quiz_text']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "Poll - Description: " + \
                        str(y['poll']['extended']['descr']) + ","
                except KeyError:
                    pass
                try:
                    if y['poll']['options']:
                        z = ''
                        for x in y['poll']['options']:
                            try:
                                z = x['count']
                                temp_list[13] += "Poll - Options - Count: " + str(z) + ","
                            except (KeyError, IndexError):
                                pass
                            try:
                                z = x['name']
                                temp_list[13] += "Poll - Options - Name: " + str(z) + ","
                            except (KeyError, IndexError):
                                pass
                            try:
                                z = x['isLiked']
                                temp_list[13] += "Poll - Options - Is Liked: " + str(z) + ","
                            except (KeyError, IndexError):
                                pass
                except (KeyError, IndexError):
                    pass

            # quote values
            if "quote" in y:
                try:
                    temp_list[13] += "Quote - Text: " + str(y['quote']['text']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "Quote - Name: " + str(y['quote']['name']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "Quote - Attachment Name: " + \
                        str(y['quote']['attachmentName']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "Quote - Attachment UID: " + \
                        str(y['quote']['attachmentUID']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "Quote - Attachment Preview Path: " + \
                        str(y['quote']['attachmentPreviewPath']) + ","
                except KeyError:
                    pass
                try:
                    temp_list[13] += "Quote - Text Meta Info - Data: " + \
                        y['quote']['textMetaInfo_v2'][0]['data'] + ","
                except (KeyError, IndexError):
                    pass

        if temp_list[10] == 'Outgoing':
            temp_list[0] = my_user_name
            temp_list[1] = ''
            temp_list[2] = my_phone_number

        if record[15] is not None:
            thumb = check_in_media(record[15], record[15])
        else:
            thumb = ''

        creation_ts = convert_cocoa_core_data_ts_to_utc(record[6])
        change_ts = convert_cocoa_core_data_ts_to_utc(record[7])
        call_ts = convert_cocoa_core_data_ts_to_utc(record[8])
        msg_time_bomb_ts = convert_unix_ts_to_utc(record[24])
        record = tuple(temp_list)
        data_list.append((creation_ts, record[0], record[1], record[2], record[3],
                          record[4], record[5], creation_ts, change_ts, record[14],
                          record[15], thumb, call_ts, record[9], record[10],
                          record[11], record[12], record[16], record[17], record[18],
                          record[19], record[20], record[21], record[22], record[23],
                          msg_time_bomb_ts, record[25], record[26], record[13]))

    return data_headers, data_list, data_source
