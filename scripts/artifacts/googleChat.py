import sqlite3
import blackboxprotobuf
import re
from io import BytesIO

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, utf8_in_extended_ascii, media_to_html


def get_googleChat(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('dynamite.db'):
            result = re.findall(r"([0-9A-F]{8}-[0-9A-F]{4}-[4][0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}+)", file_found)
            guid = result[0]
            break
            
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime(topic_messages.create_time/1000000,'unixepoch') AS "Message Time",
    CASE
    WHEN group_type=1 THEN "Group Message"
    WHEN group_type=2 THEN "1-to-1 Message"
    ELSE group_type
    END AS "Group Type",
    Groups.name AS "Conversation Name",
    users.name AS "Message Author",
    topic_messages.text_body AS "Message",
    topic_messages.reactions AS "Message Reactions",
    topic_messages.annotation AS "Message Annotation (Possible Attachment Information)"
    FROM 
    topic_messages
    JOIN users ON users.user_id=topic_messages.creator_id
    JOIN Groups ON Groups.group_id=topic_messages.group_id
    ORDER BY "Message Time" ASC
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        
        for row in all_rows:
            thumb = ''
            protobufreactions = row[5]
            checkforempty = BytesIO(protobufreactions)
            check = checkforempty.read(3)
            
            if check == b'\xfe\xff\x00':
                reaction = ''
                reactionuser = ''
            else:
                protostuff, types = blackboxprotobuf.decode_message(protobufreactions)
                reaction = (protostuff['1']['1']['1']['1']).decode()
                reaction = (utf8_in_extended_ascii(reaction))[1]
                
                timestampofreaction = protostuff['1']['1']['4']
                reactionuser = protostuff['1'].get('2')
                if reactionuser is not None:
                    reactionuser = protostuff['1']['2']['1']
                    reactionuser = (reactionuser.decode())
                else:
                    reactionuser = ''
                    
            protobufmedia = row[6]
            checkforempty = BytesIO(protobufmedia)
            check = checkforempty.read(3)
            
            if check == b'\xfe\xff\x00':
                media = ''
                mediafilename = ''
            else:
                protostuff, types = blackboxprotobuf.decode_message(protobufmedia)
                checkkeyten = (protostuff['1'].get('10'))
                if checkkeyten is not None:
                    mediafilename = (protostuff['1']['10']['3'])
                    mediafilename = (mediafilename.decode())
                    attachment = seeker.search('*/'+guid+'/tmp/'+mediafilename, return_on_first_hit=True)
                    
                    if len(attachment) < 1:
                        thumb = ''
                    else:
                        thumb = media_to_html(attachment[0], (attachment[0],), report_folder)
                else:
                    mediafilename = ''
                    media = ''
            
            data_list.append((row[0],row[1],row[2],row[3],row[4],mediafilename,thumb,reaction,reactionuser))
            mediafilename = thumb = reaction = reactionuser = ''
            
        
        description = ''
        report = ArtifactHtmlReport('Google Chat')
        report.start_artifact_report(report_folder, 'Google Chat', description)
        report.add_script()
        data_headers = ('Timestamp','Group Type','Conversation Name','Message Author','Message','Filename','Media','Reaction','Reaction User' )     
        report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Media'])
        report.end_artifact_report()
        
        tsvname = 'Google Chat'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('No Google Chat data available')
    
    
__artifacts__ = {
    "googleChat": (
        "Google Chat",
        ('*/Documents/user_accounts/*/dynamite.db*'),
        get_googleChat)
}