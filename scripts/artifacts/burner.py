__artifacts_v2__ = {
    "get_burner_accounts": {
        "name": "Burner Accounts",
        "description": "Parses and extract burner accounts",
        "author": "Django Faiola (https://djangofaiola.blogspot.com https://www.linkedin.com/in/djangofaiola/)",
        "creation_date": "2024-03-05",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Burner",
        "notes": "App version tested: 4.0.18, 4.3.3, 5.3.8, 5.4.11",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/Phoenix.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | group.adhoclabs.Burners | 1 row",
            "hickman_ios13": "iOS 13.3.1 | group.adhoclabs.Burners | 1 row",
            "hickman_ios14": "iOS 14.3 | group.adhoclabs.Burners | 1 row",
        }
    },
    "get_burner_messages": {
        "name": "Burner Messages",
        "description": "Parses and extract burner messages",
        "author": "Django Faiola (https://djangofaiola.blogspot.com https://www.linkedin.com/in/djangofaiola/)",
        "creation_date": "2024-03-05",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Burner",
        "notes": "App version tested: 4.0.18, 4.3.3, 5.3.8, 5.4.11",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/Phoenix.sqlite*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/outgoingPhotos/**',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/thumbnails/**'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 32 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 8 rows",
            "hickman_ios14": "iOS 14.3 | 17 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        },
        "data_views": {
            "conversation": {
                "directionSentValue": "Outgoing",
                "conversationDiscriminatorColumn": "Thread",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "timeColumn": "Sent",
                "senderColumn": "Sender",
                "mediaColumn": "Image"
            }
        }
    },
    "get_burner_contacts": {
        "name": "Burner Contacts",
        "description": "Parses and extract burner contacts",
        "author": "Django Faiola (https://djangofaiola.blogspot.com https://www.linkedin.com/in/djangofaiola/)",
        "creation_date": "2024-03-05",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Burner",
        "notes": "App version tested: 4.0.18, 4.3.3, 5.3.8, 5.4.11",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/Phoenix.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | group.adhoclabs.Burners | 3 rows",
            "hickman_ios13": "iOS 13.3.1 | group.adhoclabs.Burners | 3 rows",
            "hickman_ios14": "iOS 14.3 | group.adhoclabs.Burners | 5 rows",
        }
    },
    "get_burner_numbers": {
        "name": "Burner Numbers",
        "description": "Parses and extract burner numbers",
        "author": "Django Faiola (https://djangofaiola.blogspot.com https://www.linkedin.com/in/djangofaiola/)",
        "creation_date": "2024-03-05",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Burner",
        "notes": "App version tested: 4.0.18, 4.3.3, 5.3.8, 5.4.11",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/Phoenix.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "hash",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | group.adhoclabs.Burners | 1 row",
            "hickman_ios13": "iOS 13.3.1 | group.adhoclabs.Burners | 1 row",
            "hickman_ios14": "iOS 14.3 | group.adhoclabs.Burners | 1 row",
        }
    }
}

import os
import plistlib

from scripts.ilapfuncs import (artifact_processor, check_in_embedded_media, convert_ts_int_to_utc,
                               does_column_exist_in_db, get_sqlite_db_records, logfunc)


def _to_utc(value, divisor=1.0):
    """Cocoa+epoch integer timestamp to aware UTC; empty/zero passes through."""
    if not value:
        return ''
    return convert_ts_int_to_utc(int(float(value) / divisor))


def _find_phoenix(context):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('Phoenix.sqlite'):
            return file_found
    return ''


def _checkin_asset(asset_url, media_paths, source_file):
    """Locate a message asset among the seeker-found media files and check it in as embedded media."""
    if not asset_url:
        return None
    target = os.path.normpath(str(asset_url))
    for match in media_paths:
        if target in str(match):
            try:
                with open(match, 'rb') as f:
                    return check_in_embedded_media(source_file, f.read(), os.path.basename(str(match)))
            except OSError as ex:
                logfunc(f'Burner: failed to read asset {match}: {ex}')
                return None
    return None


@artifact_processor
def get_burner_accounts(context):
    data_headers = (('Created', 'datetime'), ('Phone number', 'phonenumber'), 'Country code', 'Number of burners',
                    'Burner numbers', 'Burner IDs', 'Do not distub', 'Voicemail URL', 'User ID')
    data_list = []
    source_path = _find_phoenix(context)
    if not source_path:
        return data_headers, data_list, ''

    if does_column_exist_in_db(source_path, 'ZBURNER', 'ZUSER'):
        query = '''
        SELECT
            U.Z_PK,
            B.B_PK,
            (U.ZDATECREATED + 978307200) AS "created",
            U.ZPHONENUMBER AS "phoneNumber",
            U.ZCOUNTRYCODE AS "countryCode",
            (coalesce(B.nBurners, "0") || "/" || U.ZTOTALNUMBERBURNERS) AS "nBurners",
            B.burnerNames,
            B.burnerIds,
            CASE U.ZDNDENABLED WHEN 1 THEN "On" ELSE "Off" END AS "dndEnabled",
            U.ZVOICEMAILURL AS "voicemailUrl",
            U.ZUSERID AS "userId"
        FROM ZUSER AS "U"
        LEFT JOIN (
            SELECT
                BU.ZUSER,
                group_concat(BU.Z_PK, char(29)) AS "B_PK",
                count(BU.ZUSER) AS "nBurners",
                group_concat(IIF(BU.ZNAME NOT NULL, BU.ZPHONENUMBER || " (" || BU.ZNAME || ")", BU.ZPHONENUMBER), char(10)) AS "burnerNames",
                group_concat(BU.ZBURNERID, char(10)) AS "burnerIds"
            FROM ZBURNER AS "BU"
            GROUP BY BU.ZUSER
        ) AS "B" ON (U.Z_PK = B.ZUSER)
        '''
    else:
        query = '''
        SELECT
            U.Z_PK,
            NULL AS B_PK,
            (U.ZDATECREATED + 978307200) AS "created",
            U.ZPHONENUMBER AS "phoneNumber",
            U.ZCOUNTRYCODE AS "countryCode",
            ("0" || "/" || U.ZTOTALNUMBERBURNERS) AS "nBurners",
            NULL AS burnerNames,
            NULL burnerIds,
            CASE U.ZDNDENABLED WHEN 1 THEN "On" ELSE "Off" END AS "dndEnabled",
            U.ZVOICEMAILURL AS "voicemailUrl",
            U.ZUSERID AS "userId"
        FROM ZUSER AS "U"
        '''

    for row in get_sqlite_db_records(source_path, query):
        data_list.append((_to_utc(row[2]), row[3], row[4], row[5], row[6], row[7],
                          row[8], row[9], row[10]))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def get_burner_contacts(context):
    data_headers = (('Phone number', 'phonenumber'), 'Full name', 'Other phones', 'Notes', 'Verified', 'Blocked',
                    'Muted', ('Image', 'media'), ('Thumbnail', 'media'), 'Image URL',
                    'Thumbnail URL', 'Contact ID')
    data_list = []
    source_path = _find_phoenix(context)
    if not source_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        C.Z_PK AS "C_PK",
        CPN.CPN_PK,
        CN.CN_PK,
        C.ZPHONENUMBER AS "phoneNumber",
        C.ZNAME AS "name",
        CPN.otherPhones,
        CN.notes,
        CASE C.ZVERIFIED WHEN 1 then 'Yes' ELSE 'No' END AS "verified",
        CASE C.ZBLOCKED WHEN 1 then 'Yes' ELSE 'No' END AS "blocked",
        CASE C.ZMUTED WHEN 1 then 'Yes' ELSE 'No' END AS "muted",
        substr(C.ZIMAGE, 2, length(C.ZIMAGE) - 2) AS "image",
        substr(C.ZTHUMBNAIL, 2, length(C.ZTHUMBNAIL) - 2) AS "thumbnail",
        C.ZIMAGEURL AS "imageUrl",
        C.ZTHUMBNAILURL AS "thumbnailUrl",
        C.ZCONTACTID AS "contactId"
    FROM ZCONTACT AS "C"
    LEFT JOIN (
        SELECT
            PN.ZCONTACT,
            group_concat(coalesce(PN.Z_PK, ""), char(29)) AS "CPN_PK",
            group_concat(IIF(length(PN.ZPHONENUMBERLABEL) > 0, "(" || PN.ZPHONENUMBERLABEL || ") " || PN.ZPHONENUMBER, PN.ZPHONENUMBER), char(10)) AS "otherPhones"
        FROM ZCONTACTPHONENUMBER AS "PN"
        GROUP BY PN.ZCONTACT
    ) AS "CPN" ON (C.Z_PK = CPN.ZCONTACT)
    LEFT JOIN (
        SELECT
            N.ZCONTACT,
            group_concat(coalesce(N.Z_PK, ""), char(29)) AS "CN_PK",
            group_concat(coalesce(N.ZNOTEVALUE, ""), char(10)) AS "notes"
        FROM ZCONTACTNOTE AS "N"
        GROUP BY N.ZCONTACT
    ) AS "CN" ON (C.Z_PK = CN.ZCONTACT)
    '''

    for row in get_sqlite_db_records(source_path, query):
        image_ref = check_in_embedded_media(source_path, row[10], f'burner_contact_{row[0]}_image') if row[10] else None
        thumb_ref = check_in_embedded_media(source_path, row[11], f'burner_contact_{row[0]}_thumb') if row[11] else None
        data_list.append((row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                          image_ref, thumb_ref, row[12], row[13], row[14]))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def get_burner_numbers(context):
    data_headers = (('Created', 'datetime'), ('Profile picture', 'media'), ('Burner number', 'phonenumber'),
                    'Display name', ('Subscription Expires', 'datetime'), 'Notifications',
                    'Inbound caller ID', 'In-App calling (VoIP)', 'Auto-replay enabled',
                    'Auto-reply message', 'Remaining/Total minutes', 'Remaining/Total messages',
                    ('Phone number', 'phonenumber'), 'User ID', 'Burner ID')
    data_list = []
    source_path = _find_phoenix(context)
    if not source_path:
        return data_headers, data_list, ''

    if does_column_exist_in_db(source_path, 'ZBURNER', 'ZUSER'):
        query = '''
        SELECT
            B.Z_PK,
            U.Z_PK,
            substr(B.ZIMAGE, 2, length(B.ZIMAGE) - 2) AS "image",
            B.ZPHONENUMBER AS "burnerNumber",
            B.ZNAME AS "displayName",
            (B.ZDATECREATED + 978307200) AS "created",
            (B.ZEXPIRATIONDATE + 978307200) AS "expires",
            CASE B.ZNOTIFICATIONS WHEN 0 THEN "Off" ELSE "On" END AS "notifications",
            CASE B.ZCALLERIDENABLED WHEN 0 THEN "Burner Number" ELSE "Caller Number" END AS "inboundCallerID",
            CASE B.ZUSESIP WHEN 0 THEN "Standard Voice" ELSE "VoIP" END AS "VoIPinAppCalling",
            CASE B.ZAUTOREPLYACTIVE WHEN 0 THEN "No" ELSE "Yes" END AS "autoReplyActive",
            B.ZAUTOREPLYTEXT AS "autoReplyText",
            coalesce(B.ZREMAININGMINUTES, "0") || "/" || coalesce(B.ZTOTALMINUTES, "0") AS "minutes",
            coalesce(B.ZREMAININGTEXTS, "0") || "/" || coalesce(B.ZTOTALTEXTS, "0") AS "texts",
            U.ZPHONENUMBER AS "mobilePhone",
            U.ZUSERID AS "userId",
            B.ZBURNERID AS "burnerId"
        FROM ZBURNER AS "B"
        LEFT JOIN ZUSER AS "U" ON (B.ZUSER = U.Z_PK)
        '''
    else:
        query = '''
        SELECT
            B.Z_PK,
            NULL AS U_PK,
            substr(B.ZIMAGE, 2, length(B.ZIMAGE) - 2) AS "image",
            B.ZPHONENUMBER AS "burnerNumber",
            B.ZNAME AS "displayName",
            (B.ZDATECREATED + 978307200) AS "created",
            (B.ZEXPIRATIONDATE + 978307200) AS "expires",
            CASE B.ZNOTIFICATIONS WHEN 0 THEN "Off" ELSE "On" END AS "notifications",
            CASE B.ZCALLERIDENABLED WHEN 0 THEN "Burner Number" ELSE "Caller Number" END AS "inboundCallerID",
            CASE B.ZUSESIP WHEN 0 THEN "Standard Voice" ELSE "VoIP" END AS "VoIPinAppCalling",
            CASE B.ZAUTOREPLYACTIVE WHEN 0 THEN "No" ELSE "Yes" END AS "autoReplyActive",
            B.ZAUTOREPLYTEXT AS "autoReplyText",
            coalesce(B.ZREMAININGMINUTES, "0") || "/" || coalesce(B.ZTOTALMINUTES, "0") AS "minutes",
            coalesce(B.ZREMAININGTEXTS, "0") || "/" || coalesce(B.ZTOTALTEXTS, "0") AS "texts",
            NULL AS "mobilePhone",
            NULL AS "userId",
            B.ZBURNERID AS "burnerId"
        FROM ZBURNER AS "B"
        '''

    for row in get_sqlite_db_records(source_path, query):
        image_ref = check_in_embedded_media(source_path, row[2], f'burner_{row[16]}_image') if row[2] else None
        data_list.append((_to_utc(row[5]), image_ref, row[3], row[4], _to_utc(row[6]), row[7],
                          row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16]))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def get_burner_messages(context):
    data_headers = (('Sent', 'datetime'), 'Thread', 'Direction', 'Read', 'Sender', 'Recipient',
                    'Message', 'Message type', ('Image', 'media'), ('Thumbnail', 'media'),
                    'Media URL', 'Voicemail URL', 'Message ID', 'Burner ID', 'Thread ID')
    data_list = []

    media_paths = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('.com.apple.mobile_container_manager.metadata.plist'):
            try:
                with open(file_found, 'rb') as f:
                    pl = plistlib.load(f)
            except (plistlib.InvalidFileException, ValueError, OSError):
                continue
            if pl.get('MCMMetadataIdentifier') == 'com.adhoclabs.burner':
                identifier = os.path.basename(os.path.dirname(file_found))
                seeker = context.get_seeker()
                media_paths = seeker.search(f'*/{identifier}/Library/Caches/outgoingPhotos/**')
                media_paths.extend(seeker.search(f'*/{identifier}/Library/Caches/thumbnails/**'))
                break

    source_path = _find_phoenix(context)
    if not source_path:
        return data_headers, data_list, ''

    if does_column_exist_in_db(source_path, 'ZMESSAGE', 'ZCONVERSATIONID'):
        extra_join_thread = ' OR (M.ZMESSAGETHREAD IS NULL AND M.ZBURNERID = MT.ZBURNERID AND M.ZCONVERSATIONID = MT.ZCONVERSATIONID)'
    elif does_column_exist_in_db(source_path, 'ZMESSAGE', 'ZCONTACTID'):
        extra_join_thread = ' OR (M.ZMESSAGETHREAD IS NULL AND M.ZBURNERID = MT.ZBURNERID AND coalesce(M.ZCONTACTID, M.ZCONTACTPHONENUMBER) = MT.ZCONTACTPHONENUMBER)'
    else:
        extra_join_thread = ''

    if does_column_exist_in_db(source_path, 'ZMESSAGE', 'ZCONTACTID'):
        extra_join_contact = ' OR (MT.ZCONTACT IS NULL AND coalesce(M.ZCONTACTID, M.ZCONTACTPHONENUMBER) = C.ZPHONENUMBER)'
    else:
        extra_join_contact = ''

    query = '''
    SELECT
        MT.Z_PK AS "MT_PK",
        C.Z_PK AS "C_PK",
        M.Z_PK AS "M_PK",
        B.Z_PK AS "B_PK",
        IIF(C.ZNAME IS NOT NULL, C.ZPHONENUMBER || " (" || C.ZNAME || ")", C.ZPHONENUMBER) AS "thread",
        (M.ZDATECREATED + 978307200) AS "dateCreated",
        IIF(M.ZDIRECTION = 1, "Incoming", "Outgoing") AS "direction",
        IIF(M.ZREAD = 1, "Read", "Not read") AS "read",
        IIF (M.ZDIRECTION = 1,
            IIF(C.ZNAME IS NOT NULL, C.ZPHONENUMBER || " (" || C.ZNAME || ")", C.ZPHONENUMBER),
            IIF(B.ZNAME IS NOT NULL, B.ZPHONENUMBER || " (" || B.ZNAME || ")", B.ZPHONENUMBER)
        ) AS "sender",
        IIF (M.ZDIRECTION = 2,
            IIF(C.ZNAME IS NOT NULL, C.ZPHONENUMBER || " (" || C.ZNAME || ")", C.ZPHONENUMBER),
            IIF(B.ZNAME IS NOT NULL, B.ZPHONENUMBER || " (" || B.ZNAME || ")", B.ZPHONENUMBER)
        ) AS "recipient",
        CASE
            WHEN (M.ZDIRECTION = 1) AND (M.ZSTATE = 3) THEN "Completed incoming call"
            WHEN (M.ZDIRECTION = 2) AND (M.ZSTATE = 3) THEN "Completed outgoing call"
            WHEN (M.ZDIRECTION = 1) AND (M.ZSTATE = 4) THEN "Missed incoming call"
            WHEN (M.ZDIRECTION = 2) AND (M.ZSTATE = 4) THEN "Missed outgoing call"
            WHEN (M.ZDIRECTION = 1) AND (M.ZSTATE = 5) THEN "Missed incoming call with voicemail"
            WHEN (M.ZDIRECTION = 2) AND (M.ZSTATE = 5) THEN "Missed outgoing call with voicemail"
            ELSE M.ZBODY
        END AS "message",
        CASE
            WHEN (M.ZTYPE = 1) AND (M.ZSTATE in (3, 4)) THEN "Call"
            WHEN (M.ZTYPE = 1) AND (M.ZSTATE = 5) THEN "Voicemail"
            WHEN (M.ZTYPE = 2) AND (M.ZASSETURL IS NULL) THEN "Text"
            WHEN (M.ZTYPE = 2) THEN "Picture"
            ELSE M.ZTYPE
        END AS "mType",
        M.ZLOCALASSETURL AS "localAsset",
        M.ZLOCALTHUMBNAILURL AS "localThumbnail",
        M.ZASSETURL AS "mediaUrl",
        M.ZVOICEMAILURL AS "voiceUrl",
        M.ZMESSAGEID AS "messageId",
        M.ZBURNERID AS "burnerId",
        MT.ZMESSAGETHREADID AS "threadId"
    FROM ZMESSAGE AS "M"
    LEFT JOIN ZBURNER AS "B" ON (M.ZBURNERID = B.ZBURNERID)
    LEFT JOIN ZMESSAGETHREAD AS "MT" ON (M.ZMESSAGETHREAD = MT.Z_PK){0}
    LEFT JOIN ZCONTACT AS "C" ON (MT.ZCONTACT = C.Z_PK){1}
    '''.format(extra_join_thread, extra_join_contact)

    for row in get_sqlite_db_records(source_path, query):
        image_ref = _checkin_asset(row[12], media_paths, source_path)
        thumb_ref = _checkin_asset(row[13], media_paths, source_path)
        data_list.append((_to_utc(row[5]), row[4], row[6], row[7], row[8], row[9], row[10],
                          row[11], image_ref, thumb_ref, row[14], row[15], row[16], row[17], row[18]))

    return data_headers, data_list, context.get_relative_path(source_path)
