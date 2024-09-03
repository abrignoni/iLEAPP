__artifacts_v2__ = {
    "Oops": {
        "name": "Oops: Make New Friends",
        "description": "Parses Oops Message Database",
        "author": "Heather Charpentier",
        "version": "0.0.1",
        "date": "2024-06-26",
        "requirements": "none",
        "category": "Oops",
        "notes": "",
        "paths": ('*private/var/mobile/Containers/Data/Application/*/Library/Application Support/RongCloud/*/storage*'),
        "function": "get_OopsMessages"
    }
}

import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, timeline, tsv, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_OopsMessages(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('storage'):
            db = open_sqlite_db_readonly(file_found)
            #SQL QUERY TIME!
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            datetime(send_time/1000, 'unixepoch') as 'Date Sent',
            datetime(receive_time/1000, 'unixepoch') as 'Date Received',
            clazz_name as 'Message Type',
            json_extract(RCT_MESSAGE.content, '$.user.name') as 'Sender Name',
            sender_id as 'Sender ID',
            CASE message_direction
                WHEN 1 THEN 'Incoming'
                WHEN 0 THEN 'Outgoing'
                ELSE 'Unknown'
            END as Direction,
            json_extract(RCT_Message.content, '$.content') as 'Message',
            json_extract(json_extract(RCT_Message.content, '$.extra'), '$.nickName') AS 'Nickname',
            json_extract(json_extract(RCT_Message.content, '$.extra'), '$.userId') AS 'User ID'
            FROM RCT_MESSAGE
            WHERE
            json_valid(json_extract(RCT_Message.content, '$.extra'))
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
               for row in all_rows:
               
                   data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
            db.close()
                    
        else:
            continue
        
    if data_list:
        description = 'Oops: Make New Friends'
        report = ArtifactHtmlReport('Oops Messages')
        report.start_artifact_report(report_folder, 'Oops Messages', description)
        report.add_script()
        data_headers = ('Date Sent','Date Received','Message Type','Sender Name','Sender ID','Direction','Message','Nickname','User ID')
        report.write_artifact_data_table(data_headers, data_list, file_found,html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'Oops Messages'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Oops Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
    
    else:
        logfunc('No Oops data available')

