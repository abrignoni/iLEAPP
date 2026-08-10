__artifacts_v2__ = {
    "dubox_messages": {
        "name": "Dubox - Messages",
        "description": "Messages from the Dubox (Terabox) in-app chat, with the direction, the "
                       "conversation partner, the message text and any file that was sent",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Dubox",
        "notes": "Read from mbox_main.sqlite. Direction is taken from the is_receive column (0 sent, "
                 "1 received) and the partner is resolved from mbox_friendlist through the message's "
                 "msguk. contentType is reported as the stored integer; message text, and for file "
                 "messages the file name, path and md5, are shown where present.",
        "paths": ('*/mbox_main.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | Dubox | 12 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Partner",
                "textColumn": "Content",
                "directionColumn": "Direction",
                "directionSentValue": "Sent",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender",
            }
        },
    },
    "dubox_conversations": {
        "name": "Dubox - Conversations",
        "description": "Conversation threads in the Dubox in-app chat, with the session name, the "
                       "last message and the unread count",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Dubox",
        "notes": "Read from mbox_conversations in mbox_main.sqlite.",
        "paths": ('*/mbox_main.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "list",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | Dubox | 4 rows",
        },
    },
    "dubox_contacts": {
        "name": "Dubox - Contacts",
        "description": "Contacts in the Dubox in-app chat friend list, with the user name, nickname "
                       "and any secure mobile number or email stored against them",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Dubox",
        "notes": "Read from mbox_friendlist in mbox_main.sqlite.",
        "paths": ('*/mbox_main.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | Dubox | 2 rows",
        },
    },
    "dubox_cloud_files": {
        "name": "Dubox - Cloud Files",
        "description": "Files cached from the Dubox cloud storage listing, with the server path, "
                       "size, md5 and the favourite and shared flags",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Dubox",
        "notes": "Read from the cachefilelist table of netdisk.sqlite; this is the cloud file "
                 "listing the app had cached, not necessarily the full account contents.",
        "paths": ('*/netdisk.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "cloud",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | Dubox | 45 rows",
        },
    },
    "dubox_photos": {
        "name": "Dubox - Photos",
        "description": "Photos and videos in the Dubox media listing, with the file name, the date "
                       "taken and, where the source recorded it, the location",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Dubox",
        "notes": "Read from the image_filelist table of imageDB.sqlite. The location columns are "
                 "populated only for items whose source carried location metadata; they are blank "
                 "otherwise.",
        "paths": ('*/imageDB.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | Dubox | 39 rows",
        },
    },
}

from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records


def _uts(value):
    """Dubox stores Unix epoch seconds (sometimes fractional); return UTC datetime."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    try:
        return datetime.fromtimestamp(value, tz=timezone.utc)
    except (OSError, OverflowError, ValueError):
        return ''


@artifact_processor
def dubox_messages(context):
    source_path = get_file_path(context.get_files_found(), 'mbox_main.sqlite')
    data_list = []

    query = '''
    SELECT m.time, m.is_receive, f.uname, m.username, m.content, m.contentType,
           m.path, m.md5, m.size, m.link, m.msguk
    FROM mbox_msg m
    LEFT JOIN mbox_friendlist f ON m.msguk = f.uk
    ORDER BY m.time
    '''
    for record in get_sqlite_db_records(source_path, query):
        sent = record[1] == 0
        partner = record[2] or record[10]
        data_list.append((
            _uts(record[0]),
            'Sent' if sent else 'Received',
            record[3] if record[3] else ('' if sent else partner),
            partner,
            record[4],
            record[5],
            record[6],
            record[8],
            record[7],
            record[9],
        ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Direction',
        'Sender',
        'Partner',
        'Content',
        'Content Type Value',
        'File Path',
        'File Size',
        'File MD5',
        'Link',
    )
    return data_headers, data_list, source_path


@artifact_processor
def dubox_conversations(context):
    source_path = get_file_path(context.get_files_found(), 'mbox_main.sqlite')
    data_list = []

    query = '''
    SELECT mtime, time, sessionName, username, content, unreadcount, conversationType,
           is_official, draft_content, msguk
    FROM mbox_conversations
    ORDER BY mtime
    '''
    for record in get_sqlite_db_records(source_path, query):
        data_list.append((
            _uts(record[0]),
            _uts(record[1]),
            record[2] or record[3],
            record[4],
            record[5],
            record[6],
            'Yes' if record[7] else 'No',
            record[8],
            record[9],
        ))

    data_headers = (
        ('Last Message Time', 'datetime'),
        ('Created', 'datetime'),
        'Session Name',
        'Last Message',
        'Unread Count',
        'Conversation Type Value',
        'Official Account',
        'Draft Content',
        'Conversation Key',
    )
    return data_headers, data_list, source_path


@artifact_processor
def dubox_contacts(context):
    source_path = get_file_path(context.get_files_found(), 'mbox_main.sqlite')
    data_list = []

    query = '''
    SELECT uk, uname, nickname, displayname, remark, securemobil, secureemail, intro,
           viptype, isFriend
    FROM mbox_friendlist
    ORDER BY uname
    '''
    for record in get_sqlite_db_records(source_path, query):
        data_list.append((
            record[1], record[2], record[3], record[4], record[5], record[6], record[7],
            record[8], record[9], record[0],
        ))

    data_headers = (
        'User Name',
        'Nickname',
        'Display Name',
        'Remark',
        'Secure Mobile',
        'Secure Email',
        'Intro',
        'VIP Type Value',
        'Is Friend Value',
        'User Key',
    )
    return data_headers, data_list, source_path


@artifact_processor
def dubox_cloud_files(context):
    source_path = get_file_path(context.get_files_found(), 'netdisk.sqlite')
    data_list = []

    query = '''
    SELECT ctime, mtime, server_full_path, file_name, file_size, file_md5, isdir,
           file_category, is_favorite, is_shared, is_collected, fid
    FROM cachefilelist
    ORDER BY mtime
    '''
    for record in get_sqlite_db_records(source_path, query):
        data_list.append((
            _uts(record[0]),
            _uts(record[1]),
            record[3],
            record[2],
            record[4],
            record[5],
            'Yes' if record[6] else 'No',
            record[7],
            'Yes' if record[8] else 'No',
            'Yes' if record[9] else 'No',
            'Yes' if record[10] else 'No',
            record[11],
        ))

    data_headers = (
        ('Created', 'datetime'),
        ('Modified', 'datetime'),
        'File Name',
        'Server Path',
        'File Size',
        'File MD5',
        'Is Directory',
        'File Category Value',
        'Favourite',
        'Shared',
        'Collected',
        'File ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def dubox_photos(context):
    source_path = get_file_path(context.get_files_found(), 'imageDB.sqlite')
    data_list = []

    query = '''
    SELECT date_taken, ctime, mtime, file_name, server_full_path, file_size, file_md5,
           latitude, longitude, full_addr, city, street, resolution, duration, fid
    FROM image_filelist
    ORDER BY date_taken
    '''
    for record in get_sqlite_db_records(source_path, query):
        data_list.append((
            _uts(record[0]),
            _uts(record[1]),
            _uts(record[2]),
            record[3],
            record[4],
            record[5],
            record[6],
            record[7] if record[7] else '',
            record[8] if record[8] else '',
            record[9],
            record[10],
            record[11],
            record[12],
            record[13],
            record[14],
        ))

    data_headers = (
        ('Date Taken', 'datetime'),
        ('Created', 'datetime'),
        ('Modified', 'datetime'),
        'File Name',
        'Server Path',
        'File Size',
        'File MD5',
        'Latitude',
        'Longitude',
        'Full Address',
        'City',
        'Street',
        'Resolution',
        'Duration',
        'File ID',
    )
    return data_headers, data_list, source_path
