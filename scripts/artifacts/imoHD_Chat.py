import io
import os
import plistlib
import shutil
import sys
import nska_deserialize as nd
try:
    import biplist
except ImportError:
    biplist = None

from scripts.ilapfuncs import logfunc, artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_imoHD_Chat_messages(files_found, report_folder, seeker, wrap_text, timezone_offset):

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.sqlite'):
            break

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select
    case ZIMOCHATMSG.ZTS
        when 0 then ''
        else datetime(ZTS/1000000000,'unixepoch')
    end  as "Timestamp",
    ZIMOCONTACT.ZDISPLAY as "Sender Display Name",
    ZIMOCHATMSG.ZALIAS as "Sender Alias",
    ZIMOCONTACT.ZDIGIT_PHONE,
    ZIMOCHATMSG.ZTEXT as "Message",
    case ZIMOCHATMSG.ZISSENT
        when 0 then 'Received'
        when 1 then 'Sent'
    end as "Message Status",
    ZIMOCHATMSG.ZIMDATA
    from ZIMOCHATMSG
    left join ZIMOCONTACT ON ZIMOCONTACT.ZBUID = ZIMOCHATMSG.ZA_UID
    ''')

    all_rows = cursor.fetchall()
    data_list = []

    for row in all_rows:

        plist = ''
        timestamp = row[0]
        senderName = row[1]
        senderAlias = row[2]
        senderPhone = row[3]
        message = row[4]
        messageStatus = row[5]
        itemAction = ''
        attachmentURL = ''
        thumb = ''

        plist_file_object = io.BytesIO(row[6])
        if row[6] is None:
            pass
        else:
            if row[6].find(b'NSKeyedArchiver') == -1:
                if sys.version_info >= (3, 9):
                    plist = plistlib.load(plist_file_object)
                else:
                    plist = biplist.readPlist(plist_file_object)
            else:
                try:
                    plist = nd.deserialize_plist(plist_file_object)
                except (nd.DeserializeError, nd.biplist.NotBinaryPlistException, nd.biplist.InvalidPlistException,
                    nd.plistlib.InvalidFileException, nd.ccl_bplist.BplistError, ValueError, TypeError, OSError, OverflowError) as ex:
                    logfunc(f'Failed to read plist for {row[0]}, error was:' + str(ex))

            itemAction = plist['type']

            #Check for Attachments
            if plist.get('objects') is not None:
                attachmentName = plist['objects'][0]['object_id']
                attachmentURL = "https://cdn.imoim.us/s/object/" + attachmentName + "/"

                for match in files_found:
                    if attachmentName in match:
                        shutil.copy2(match, report_folder)
                        data_file_name = os.path.basename(match)
                        thumb = f'<img src="{report_folder}/{data_file_name}"  width="300"></img>'

            else:
                attachmentURL = ''

        data_list.append((timestamp, senderName, senderAlias, senderPhone, message, messageStatus, itemAction, attachmentURL, thumb))

    db.close()
    data_headers = (
        'Timestamp', 'Sender Name', 'Sender Alias', 'Sender Phone', 'Message', 'Message Status', 'Item Action',
        'Attachment URL', 'Attachment')
    return data_headers, data_list, file_found


@artifact_processor
def get_imoHD_Chat_contacts(files_found, report_folder, seeker, wrap_text, timezone_offset):

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.sqlite'):
            break

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select
    ZPH_NAME,
    ZALIAS,
    ZPHONE,
    "https://cdn.imoim.us/s/object/" || ZICON_ID || "/" as "Profile Pic",
    ZBUID
    from ZIMOCONTACT
    ''')

    all_rows = cursor.fetchall()
    data_list = []

    for row in all_rows:
        data_list.append((row[0],row[1],row[2],row[3],row[4]))

    db.close()
    data_headers = ('Contact Name','Contact Alias','Contact Phone','Profile Pic URL','User ID')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_imoHD_Chat_messages": {
        "name": "IMO HD Chat - Messages",
        "description": "",
        "author": "",
        "version": "0.2",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "IMO HD Chat",
        "notes": "",
        "paths": ('*/IMODb2.sqlite*','*/mobile/Containers/Data/Application/*/Library/Caches/videos/*.webp'),
        "output_types": "all",
        "artifact_icon": "alert-triangle",
        "html_columns": ["Attachment"]
    },
    "get_imoHD_Chat_contacts": {
        "name": "IMO HD Chat - Contacts",
        "description": "",
        "author": "",
        "version": "0.2",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "IMO HD Chat",
        "notes": "",
        "paths": ('*/IMODb2.sqlite*'),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
