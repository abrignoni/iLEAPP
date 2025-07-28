__artifacts_v2__ = {
    "get_burner_accounts": {
        "name": "Burner Accounts",
        "description": "Parses and extract burner accounts",
        "author": "Django Faiola (https://djangofaiola.blogspot.com https://www.linkedin.com/in/djangofaiola/)",
        "version": "0.2.0",
        "date": "2024-03-05",
        "requirements": "none",
        "category": "Burner",
        "notes": "App version tested: 4.0.18, 4.3.3, 5.3.8, 5.4.11",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/Phoenix.sqlite*'),
        "output_types": ["lava", "tsv", "timeline"]
    },
    "get_burner_messages": {
        "name": "Burner Messages",
        "description": "Parses and extract burner messages",
        "author": "Django Faiola (https://djangofaiola.blogspot.com https://www.linkedin.com/in/djangofaiola/)",
        "version": "0.2.0",
        "date": "2024-03-05",
        "requirements": "none",
        "category": "Burner",
        "notes": "App version tested: 4.0.18, 4.3.3, 5.3.8, 5.4.11",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/Phoenix.sqlite*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["lava", "tsv"],
        "data_views": {
            "chat": {
                "directionSentValue": "Outgoing",
                "threadDiscriminatorColumn": "Thread",
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
        "version": "0.2.0",
        "date": "2024-03-05",
        "requirements": "none",
        "category": "Burner",
        "notes": "App version tested: 4.0.18, 4.3.3, 5.3.8, 5.4.11",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/Phoenix.sqlite*'),
        "output_types": ["lava", "tsv"]
    },
    "get_burner_numbers": {
        "name": "Burner Numbers",
        "description": "Parses and extract burner numbers",
        "author": "Django Faiola (https://djangofaiola.blogspot.com https://www.linkedin.com/in/djangofaiola/)",
        "version": "0.2.0",
        "date": "2024-03-05",
        "requirements": "none",
        "category": "Burner",
        "notes": "App version tested: 4.0.18, 4.3.3, 5.3.8, 5.4.11",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/Phoenix.sqlite*'),
        "output_types": ["lava", "tsv", "timeline"]

    }
}

import os
import plistlib
import shutil

from pathlib import Path
from base64 import b64encode
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import open_sqlite_db_readonly, does_column_exist_in_db, convert_ts_int_to_utc, convert_utc_human_to_timezone, artifact_processor
from scripts.filetype import image_match

# format timestamp
def FormatTimestamp(utc, timezone_offset, divisor=1.0):
    if not bool(utc):
        return ''
    else:
        timestamp = convert_ts_int_to_utc(int(float(utc) / divisor))
        return convert_utc_human_to_timezone(timestamp, timezone_offset)


# image file to html
def ImageFileToHtml(file_found, files_found, report_folder):
    media = str(file_found)
    attachment_name = os.path.normpath(media)
    for match in files_found:
        if attachment_name in match:
            # outgoingPhotos or thumbnails
            media_folder = (Path(media).parts[-2:-1])[0]
            locationfiles = os.path.join(report_folder, media_folder)
            Path(f'{locationfiles}').mkdir(parents=True, exist_ok=True)
            shutil.copy2(match, locationfiles)
            attachment_name = Path(report_folder).name + '/' + media_folder + '/' + Path(attachment_name).name
            if image_match(match):
                media = f'<a href="{attachment_name}" target="_blank"><img src="{attachment_name}" width="300"></img></a>'
            else:
                media = f'<a href="{attachment_name}" target="_blank"> Link to {Path(attachment_name).name} file</>'
            break
    return media


# blob image to html
def BlobImageToHtml(data, image_width=96):
    mimetype = image_match(data)
    if mimetype is not None:
        base64 = b64encode(data).decode('utf-8')
        return f'<img src="data:{mimetype.MIME};base64,{base64}" width="{image_width}">'
    else:
        return ""


# accounts
@artifact_processor
def get_burner_accounts(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = ['Created', 'Phone number', 'Country code', 'Number of burners', 'Burner numbers', 'Burner IDs',
                    'Do not distub', 'Voicemail URL', 'User ID']
    data_list = []
    report_file = 'Unknown'

    for file_found in files_found:
        file_found = str(file_found)

        # Phoenix.sqlite
        if file_found.endswith('Phoenix.sqlite'):
            report_file = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            if does_column_exist_in_db(file_found, 'ZBURNER', 'ZUSER'):
                cursor.execute('''
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
                ''')
            else:
                cursor.execute('''
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
                ''')

            all_rows = cursor.fetchall()
            if len(all_rows) > 0:
                report = ArtifactHtmlReport('Burner Accounts')
                report.start_artifact_report(report_folder, 'Burner Accounts')
                report.add_script()

                for row in all_rows:
                    # created
                    created = FormatTimestamp(row[2], timezone_offset)

                    # row
                    data_list.append((created, row[3], row[4], row[5], row[6], row[7],
                                      row[8], row[9], row[10]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()

            db.close()

    data_headers[0] = (data_headers[0], 'datetime')

    return data_headers, data_list, report_file


# contacts
@artifact_processor
def get_burner_contacts(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    data_list_html = []
    data_headers = ('Phone number', 'Full name', 'Other phones', 'Notes', 'Verified', 'Blocked', 'Muted',
                    'Image', 'Thumbnail', 'Image URL', 'Thumbnail URL', 'Contact ID')
    report_file = 'Unknown'

    for file_found in files_found:
        file_found = str(file_found)

        # Phoenix.sqlite
        if file_found.endswith('Phoenix.sqlite'):
            report_file = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
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
            ''')

            all_rows = cursor.fetchall()
            if len(all_rows) > 0:
                report = ArtifactHtmlReport('Burner Contacts')
                report.start_artifact_report(report_folder, 'Burner Contacts')
                report.add_script()
                for row in all_rows:
                    # image
                    if bool(row[10]):
                        image = BlobImageToHtml(row[10])
                    else:
                        image = ''

                    # thumbnail
                    if bool(row[11]):
                        thumb = BlobImageToHtml(row[11])
                    else:
                        thumb = ''

                    # row
                    data_list_html.append((row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                      image, thumb, row[12], row[13], row[14]))

                    # TODO: Update when media manager is ready
                    data_list.append((row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                      row[10], row[11], row[12], row[13], row[14]))

                report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=[ 'Image', 'Thumbnail' ])
                report.end_artifact_report()

            db.close()

    return data_headers, data_list, report_file


# numbers
@artifact_processor
def get_burner_numbers(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    data_list_html = []
    data_headers = ['Created', 'Profile picture', 'Burner number', 'Display name', 'Subscription Expires',
                    'Notifications', 'Inbound caller ID', 'In-App calling (VoIP)', 'Auto-replay enabled',
                    'Auto-reply message', 'Remaining/Total minutes', 'Remaining/Total messages',
                    'Phone number', 'User ID', 'Burner ID']
    report_file = 'Unknown'

    for file_found in files_found:
        file_found = str(file_found)

        # Phoenix.sqlite
        if file_found.endswith('Phoenix.sqlite'):
            report_file = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            if does_column_exist_in_db(file_found, 'ZBURNER', 'ZUSER'):
                cursor.execute('''
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
                ''')
            else:
                cursor.execute('''
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
                ''')

            all_rows = cursor.fetchall()

            #Handle HTML Manually due to embedded media
            if len(all_rows) > 0:
                report = ArtifactHtmlReport('Burner Numbers')
                report.start_artifact_report(report_folder, 'Burner Numbers')
                report.add_script()

                for row in all_rows:
                    # image
                    if bool(row[2]):
                        image = BlobImageToHtml(row[2])
                    else:
                        image = ''

                    # created
                    created = FormatTimestamp(row[5], timezone_offset)

                    # subscription expires
                    expires = FormatTimestamp(row[6], timezone_offset)

                    # row
                    data_list_html.append((created, image, row[3], row[4], expires, row[7], row[8], row[9], row[10],
                                           row[11], row[12], row[13], row[14], row[15], row[16]))
                    data_list.append((created, row[2], row[3], row[4], expires, row[7], row[8], row[9], row[10],
                                      row[11], row[12], row[13], row[14], row[15], row[16]))

                report.write_artifact_data_table(data_headers, data_list_html, file_found,
                                                 html_no_escape=['Profile picture'])
                report.end_artifact_report()

            db.close()

    data_headers[0] = (data_headers[0], 'datetime')

    return data_headers, data_list_html, report_file


# messages
@artifact_processor
def get_burner_messages(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_headers = ['Sent', 'Thread', 'Direction', 'Read', 'Sender', 'Recipient', 'Message', 'Message type',
                    'Image', 'Thumbnail', 'Media URL', 'Voicemail URL', 'Message ID', 'Burner ID', 'Thread ID']
    data_list = []
    data_list_html = []

    report_file = 'Unknown'

    mediafilepaths = []
    for file_foundm in files_found:
        if file_foundm.endswith('.com.apple.mobile_container_manager.metadata.plist'):
            report_file = file_foundm
            with open(file_foundm, 'rb') as f:
                pl = plistlib.load(f)
                if pl['MCMMetadataIdentifier'] == 'com.adhoclabs.burner':
                    fulldir = (os.path.dirname(file_foundm))
                    identifier = (os.path.basename(fulldir))

                    # outgoingPhotos
                    media_files = seeker.search(f'*/{identifier}/Library/Caches/outgoingPhotos/**')

                    # thumbnails
                    temp = seeker.search(f'*/{identifier}/Library/Caches/thumbnails/**')
                    if len(temp) > 0:
                        media_files.extend(temp)
                    mediafilepaths = media_files
                    break

                f.close()



    for file_found in files_found:
        file_found = str(file_found)

        # Phoenix.sqlite
        if file_found.endswith('Phoenix.sqlite'):
            report_file = file_found if (file_found == 'Unknown') else report_file + ', ' + file_found
            db = open_sqlite_db_readonly(file_found)
            # 5.4.11
            if does_column_exist_in_db(file_found, 'ZMESSAGE', 'ZCONVERSATIONID'):
                extra_join_thread = ' OR (M.ZMESSAGETHREAD IS NULL AND M.ZBURNERID = MT.ZBURNERID AND M.ZCONVERSATIONID = MT.ZCONVERSATIONID)'
            # 5.3.8
            elif does_column_exist_in_db(file_found, 'ZMESSAGE', 'M.ZCONTACTID'):
                extra_join_thread = ' OR (M.ZMESSAGETHREAD IS NULL AND M.ZBURNERID = MT.ZBURNERID AND coalesce(M.ZCONTACTID, M.ZCONTACTPHONENUMBER) = MT.ZCONTACTPHONENUMBER)'
            # 4.0.18, 4.3.3
            else:
                extra_join_thread = '' # OR (M.ZMESSAGETHREAD IS NULL AND M.ZBURNERID = MT.ZBURNERID AND M.ZCONTACTPHONENUMBER = MT.ZCONTACTPHONENUMBER)'

            # 5.3.8, 5.4.11
            if does_column_exist_in_db(file_found, 'ZMESSAGE', 'ZCONTACTID'):
                extra_join_contact = ' OR (MT.ZCONTACT IS NULL AND coalesce(M.ZCONTACTID, M.ZCONTACTPHONENUMBER) = C.ZPHONENUMBER)'
            # 4.0.18 e 4.3.3
            else:
                extra_join_contact = '' #' OR (MT.ZCONTACT IS NULL AND M.ZCONTACTPHONENUMBER = C.ZPHONENUMBER)'

            cursor = db.cursor()
            cursor.execute('''
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
            )

            all_rows = cursor.fetchall()

            # Handle HTML Manually
            if len(all_rows) > 0:
                report = ArtifactHtmlReport('Burner Messages')
                report.start_artifact_report(report_folder, 'Burner Messages')
                report.add_script()

                for row in all_rows:
                    # created
                    created = FormatTimestamp(row[5], timezone_offset)

                    # local asset url
                    if bool(row[12]):
                        image = ImageFileToHtml(row[12], mediafilepaths, report_folder)
                        #image = media_to_html(row[12], mediafilepaths, report_folder)
                    else:
                        image = ''

                    # local thumbnail url
                    if bool(row[13]):
                        thumb = ImageFileToHtml(row[13], mediafilepaths, report_folder)
                        #thumb = media_to_html(row[13], mediafilepaths, report_folder)
                    else:
                        thumb = ''

                    # row
                    data_list_html.append((created, row[4], row[6], row[7], row[8], row[9], row[10], row[11], image,
                                           thumb, row[14], row[15], row[16], row[17], row[18]))

                    # TODO: Update when media manager is ready
                    data_list.append((created, row[4], row[6], row[7], row[8], row[9], row[10], row[11], row[12],
                                      row[13], row[14], row[15], row[16], row[17], row[18]))

                report.write_artifact_data_table(data_headers, data_list_html, file_found,
                                                 html_no_escape=['Image', 'Thumbnail'])
                report.end_artifact_report()

    data_headers[0] = (data_headers[0], 'datetime')

    return data_headers, data_list, report_file
