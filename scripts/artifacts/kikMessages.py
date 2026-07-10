__artifacts_v2__ = {
    "kikMessages": {
        "name": "Kik Messages",
        "description": "Kik chat messages with attachments (kik.sqlite)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-06-22",
        "last_update_date": "2026-07-03",
        "requirements": "none",
        "category": "Kik",
        "notes": "",
        "paths": ('**/kik.sqlite*',
                  '*/mobile/Containers/Shared/AppGroup/*/cores/private/*/content_manager/data_cache/*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "felix_ios17": "iOS 17.6.1 | Kik Messaging & Chat App 17.0.0 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Kik Messaging & Chat App 16.9.3 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Kik Messaging & Chat App 17.11.3 | 3 rows",
            "iphone11_ios17": "iOS 17.3 | Kik Messaging & Chat App 16.16.1 | 32 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "User Name",
                "textColumn": "Message",
                "directionColumn": "Type",
                "directionSentValue": "Sent",
                "timeColumn": "Timestamp",
                "senderColumn": "Display Name",
                "sentMessageStaticLabel": "Local User",
                "mediaColumn": "Attachment"
            }
        },
    },
    "kikUsers": {
        "name": "Kik Users",
        "description": "Kik user accounts from kik.sqlite (ZKIKUSER)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-06-22",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Kik",
        "notes": "",
        "paths": ('**/kik.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "felix_ios17": "iOS 17.6.1 | Kik Messaging & Chat App 17.0.0 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Kik Messaging & Chat App 16.9.3 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Kik Messaging & Chat App 17.11.3 | 4 rows",
            "iphone11_ios17": "iOS 17.3 | Kik Messaging & Chat App 16.16.1 | 7 rows",
        }
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, check_in_media


def _str_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S').replace(
            tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError):
        return ''


def _find_db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('kik.sqlite'):
            return file_found
    return ''


@artifact_processor
def kikMessages(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    data_headers = (('Received Time', 'datetime'), ('Timestamp', 'datetime'), 'Message', 'Type',
                    'User', 'Display Name', 'User Name', 'Attachment Name', ('Attachment', 'media'))
    data_list = []
    source_path = _find_db(files_found)
    if not source_path:
        return data_headers, data_list, ''

    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
        datetime(ZKIKMESSAGE.ZRECEIVEDTIMESTAMP +978307200,'UNIXEPOCH'),
        datetime(ZKIKMESSAGE.ZTIMESTAMP +978307200,'UNIXEPOCH'),
        ZKIKMESSAGE.ZBODY,
        CASE ZKIKMESSAGE.ZTYPE
            WHEN 1 THEN 'Received' WHEN 2 THEN 'Sent' WHEN 3 THEN 'Group Admin'
            WHEN 4 THEN 'Group Message' ELSE 'Unknown' END,
        ZKIKMESSAGE.ZUSER,
        ZKIKUSER.ZDISPLAYNAME,
        ZKIKUSER.ZUSERNAME,
        ZKIKATTACHMENT.ZCONTENT
    FROM ZKIKMESSAGE
    LEFT JOIN ZKIKUSER ON ZKIKMESSAGE.ZUSER = ZKIKUSER.Z_PK
    LEFT JOIN ZKIKATTACHMENT ON ZKIKMESSAGE.Z_PK = ZKIKATTACHMENT.ZMESSAGE
    ''')

    for row in cursor.fetchall():
        media = ''
        if row[7]:
            media = check_in_media(str(row[7])) or ''
        data_list.append((_str_to_utc(row[0]), _str_to_utc(row[1]), row[2], row[3], row[4], row[5],
                          row[6], row[7], media))
    db.close()

    return data_headers, data_list, source_path


@artifact_processor
def kikUsers(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    data_headers = ('PK', 'Display Name', 'User Name', 'Email', 'JID', 'First Name', 'Last Name',
                    ('Profile Pic Timestamp', 'datetime'), 'Profile Pic URL')
    data_list = []
    source_path = _find_db(files_found)
    if not source_path:
        return data_headers, data_list, ''

    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
    SELECT Z_PK, ZDISPLAYNAME, ZUSERNAME, ZEMAIL, ZJID, ZFIRSTNAME, ZLASTNAME,
        datetime(ZPPTIMESTAMP/1000,'unixepoch'), ZPPURL
    FROM ZKIKUSER
    ''')

    for row in cursor.fetchall():
        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], _str_to_utc(row[7]),
                          row[8]))
    db.close()

    return data_headers, data_list, source_path
