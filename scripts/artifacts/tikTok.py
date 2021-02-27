from os.path import dirname, join
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_tikTok(files_found, report_folder, seeker):
    data_list = []
    data_list1 = []
    
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('_im.db'):
            maindb = file_found
        if file_found.endswith('db_im_xx'):
            attachdb = file_found

    db = open_sqlite_db_readonly(maindb)
    cursor = db.cursor()
    cursor.execute(f"ATTACH DATABASE '{attachdb}' as db_im_xx;")
    cursor.execute('''
        select
        datetime(created_time/1000, 'unixepoch', 'localtime') as created_time,
        UID,
        UNIQUE_ID,
        NICK_NAME,
        json_extract(content, '$.text') as message,
        json_extract(content,'$.display_name') as links_gifs_display_name,
        json_extract(content, '$.url.url_list[0]') as links_gifs_urls,
        read_status,
            case when read_status = 0 then 'Not read'
                when read_status = 1 then 'Read'
                else read_status
            end
        local_info
        from db_im_xx.SIMPLE_USER, msg
        where UID = sender order by created_time
        ''')

    all_rows = cursor.fetchall()
    
    if len(all_rows) > 0:
        for row in all_rows:

            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))

        report = ArtifactHtmlReport('TikTok Messages')
        report.start_artifact_report(report_folder, 'Messages')
        report.add_script()
        data_headers = ('Timestamp','UID','Unique ID','Nickname','Message','Link GIF Name','Link GIF URL','Read?','Local Info')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'Tiktok Messages'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'TikTok Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No TikTok messages available')

    cursor.execute('''
        select
        UID,
        NICK_NAME,
        UNIQUE_ID,
        INITIAL_LETTER,
        json_extract(AVATAR_THUMB, '$.url_list[0]') as avatarURL,
        FOLLOW_STATUS 
        from SIMPLE_USER
        ''')
    
    all_rows1 = cursor.fetchall()
    
    if len(all_rows) > 0:
        for row in all_rows1:
            
            data_list1.append((row[0], row[1], row[2], row[3], row[4], row[5]))
            
        report = ArtifactHtmlReport('TikTok Contacts')
        report.start_artifact_report(report_folder, 'Contacts')
        report.add_script()
        data_headers1 = ('UID','Nickname','Unique ID','Initial Letter','Avatar URL','Follow Status')
        report.write_artifact_data_table(data_headers1, data_list1, file_found)
        report.end_artifact_report()
        
        tsvname = 'TikTok Contacts'
        tsv(report_folder, data_headers1, data_list1, tsvname)
        
    else:
        logfunc('No TikTok Contacts available')
    
    db.close()
    