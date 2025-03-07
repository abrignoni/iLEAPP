__artifacts_v2__ = {
    "whatsappMessages": {
        "name": "Whatsapp Messages",
        "description": "",
        "author": "",
        "version": "",
        "date": "",
        "requirements": "",
        "category": "Whatsapp",
        "notes": "",
        "paths": (
            '*/var/mobile/Containers/Shared/AppGroup/*/ChatStorage.sqlite*',
            '*/var/mobile/Containers/Shared/AppGroup/*/ContactsV2.sqlite*',
            '*/var/mobile/Containers/Shared/AppGroup/*/Message/Media/*/*/*/*.*'
        ),
        "function": "get_whatsappMessages"
    }
}


import sqlite3
import io
import json
import os
import shutil
import nska_deserialize as nd
import scripts.artifacts.artGlobals
import blackboxprotobuf

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, kmlgen, tsv, is_platform_windows, open_sqlite_db_readonly


def get_whatsappMessages(files_found, report_folder, seeker, wrap_text, timezone_offset):

    found_source_file = []
    whatsapp_wa_db = None
    whatsapp_msgstore_db = None
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('ChatStorage.sqlite'):
            whatsapp_msgstore_db = str(file_found)
            found_source_file.append(file_found)
        if file_found.endswith('ContactsV2.sqlite'):
            whatsapp_wa_db = str(file_found)
            found_source_file.append(file_found)

    data_list =[]
    db = open_sqlite_db_readonly(whatsapp_msgstore_db)
    cursor = db.cursor()
    if(whatsapp_wa_db):
        cursor.execute('''attach database "''' + whatsapp_wa_db + '''" as wadb ''')
    cursor.execute('''
    select
    datetime(ZMESSAGEDATE+978307200, 'UNIXEPOCH'),
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
    ZVCARDSTRING
    FROM ZWAMESSAGE
    left JOIN ZWAMEDIAITEM
    on ZWAMESSAGE.Z_PK = ZWAMEDIAITEM.ZMESSAGE 
    left JOIN ZWACHATSESSION
    on ZWACHATSESSION.Z_PK = ZWAMESSAGE.ZCHATSESSION
    ''')
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    thumb = ''

    if usageentries > 0:
        for row in all_rows:

            if row[1] == 1:
                sender = 'Local User'
                receiver = row[2]
            else:
                sender = row[2]
                receiver = 'Local User'

            if row[8] == 5:
                lon = row[9]
                lat = row[10]
            else:
                lat = ''
                lon = ''

            attfile = row[11]
            attachment = row[12]
            localpath = row[11]

            metadata = row[13]
            attfiletype = row[14]

            if metadata is not None:
                number_forward = ''
                from_forward = ''
                decoded_data, _ = blackboxprotobuf.decode_message(row[13])

                number_forwardings = decoded_data.get("17")
                from_forwaded = decoded_data.get("21")
                if number_forwardings is not None:
                    number_forward = f'{number_forwardings}'
                if from_forwaded is not None:
                    from_forward = f'{from_forwaded.decode('utf-8')}'
                    if(whatsapp_wa_db):
                        subcursor = db.cursor()
                        subcursor.execute('''
                            SELECT ZFULLNAME || ' (' || ZPHONENUMBER || ')' 
                            FROM wadb.ZWAADDRESSBOOKCONTACT 
                            WHERE ZWHATSAPPID = ? 
                            LIMIT 1
                        ''', (from_forward,))

                        suball_rows = subcursor.fetchall()
                        if suball_rows:
                            from_forward += f"<br/>{suball_rows[0][0]}"

                        subcursor.close()
            else:
                number_forward = ''
                from_forward = ''

            if attachment is not None:
                attachment = os.path.normpath(attachment)
                for match in files_found:
                    if attachment in match:
                        shutil.copy2(match, report_folder)
                        data_file_name = os.path.basename(match)
                        rel_path = os.path.basename(report_folder)
                        thumb = f'<img src="./{rel_path}/{data_file_name}"></img>'
            else:
                thumb = ''

            if attfile is not None:
                attfile = os.path.normpath(attfile)
                for matchf in files_found:
                    if attfile in matchf:
                        shutil.copy2(matchf, report_folder)
                        data_file_namef = os.path.basename(matchf)
                        rel_path = os.path.basename(report_folder)
                        if(attfiletype.split("/")[0] == "video" ):
                            attfile = f'<video controls style="max-width:300px;"><source src="./{rel_path}/{data_file_namef}" type="{attfiletype}">'
                            if(len(thumb) > 0):
                                previewthumb = thumb
                            if(len(thumb) == 0):
                                previewthumb = 'videofile'
                            attfile += f'<a href="./{rel_path}/{data_file_namef}" target="_blank" title="open {attfiletype.split("/")[0]} file in a new tab">{previewthumb}</a>'
                            attfile += f'</video>'
                        if(attfiletype.split("/")[0] == "image"):
                            attfile = f'<a href="./{rel_path}/{data_file_namef}" target="_blank" title="open {attfiletype.split("/")[0]} file in a new tab"><img src="./{rel_path}/{data_file_namef}" style="max-width:300px"></img></a>'
                        if(attfiletype.split("/")[0] == "audio"):
                            attfile = f'<audio controls  style="max-width:300px;""><source src="./{rel_path}/{data_file_namef}" type="{attfiletype}">'
                            attfile += f'<a href="./{rel_path}/{data_file_namef}" target="_blank" title="open {attfiletype.split("/")[0]} file in a new tab">{attfiletype.split("/")[0]}</a>'
                            attfile += f'</audio>'
            else:
                attfile = ''

            data_list.append((row[0], sender, row[3], receiver, row[4], row[6], attfile, thumb, localpath, row[7], number_forward, from_forward, lat, lon,))


        description = 'Whatsapp - Messages'
        report = ArtifactHtmlReport('Whatsapp - Messages')
        report.start_artifact_report(report_folder, 'Whatsapp - Messages')
        report.add_script()
        data_headers = (
            'Timestamp', 'Sender Name', 'From ID', 'Receiver', 'To ID', 'Message',
            'Attachment File', 'Thumb','Attachment Local Path','Starred?', 'Number of Forwardings', 'Forwarded from',  'Latitude', 'Longitude',)  # Don't remove the comma, that is required to make this a tuple as there is only 1 element

        report.write_artifact_data_table(data_headers, data_list, found_source_file, html_escape=False)
        report.end_artifact_report()

        tsvname = f'Whatsapp - Messages'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Whatsapp - Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)

        kmlactivity = 'Whatsapp - Messages'
        kmlgen(report_folder, kmlactivity, data_list, data_headers)

    else:
        logfunc('Whatsapp - Messages data available')
