from os.path import dirname, join
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_tikTok(files_found, report_folder, seeker):
    data_list = []
    data_list1 = []
    
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('db.sqlite'):
            maindb = file_found
        if file_found.endswith('AwemeIM.db'):
            attachdb = file_found

    db = open_sqlite_db_readonly(maindb)
    cursor = db.cursor()
    cursor.execute(f"ATTACH DATABASE '{attachdb}' as AwemeIM;")
    cursor.execute("SELECT name FROM AwemeIM.sqlite_master WHERE type='table' LIMIT 1;") 
    tablename = cursor.fetchall()
    for rown in tablename:
        tname = rown[0]
    
    cursor.execute(f'''
        select
            datetime(localcreatedat, 'unixepoch') as Local_Create_Time,
            sender,
            customid,
            nickname,
            json_extract(content, '$.text') as message,
            json_extract(content, '$.tips') as localresponse,
            json_extract(content,'$.display_name') as links_display_name,
            json_extract(content, '$.url.url_list[0]') as links_gifs_urls,
            case 
                when servercreatedat > 1 then datetime(servercreatedat, 'unixepoch')
                else servercreatedat
                end
            servercreatedat,
            url1 as profilepicURL
        from TIMMessageORM, {tname}
        where uid = sender
        order by Local_Create_Time
        ''')

    all_rows = cursor.fetchall()
    
    if len(all_rows) > 0:
        for row in all_rows:

            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6],row[7], row[8], row[9]))

        report = ArtifactHtmlReport('TikTok Messages')
        report.start_artifact_report(report_folder, 'TikTok Messages')
        report.add_script()
        data_headers = ('Timestamp','Sender','Custom ID','Nickname','Message', 'Local Response','Link GIF Name','Link GIF URL','Server Create Timestamps','Profile Pic URL')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'Tiktok Messages'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'TikTok Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No TikTok messages available')

    cursor.execute(f'''
        select 
            case 
                when latestchattimestamp > 1 then datetime(latestchattimestamp, 'unixepoch')
                else latestchattimestamp
            end
        latestchattimestamp,
        nickname,
        uid,
        customID,
        url1
        from {tname}
        ''')
    
    all_rows1 = cursor.fetchall()
    
    if len(all_rows) > 0:
        description = 'Timestamp corresponds to latest chat if available'
        for row in all_rows1:
            
            data_list1.append((row[0], row[1], row[2], row[3], row[4]))
            
        report = ArtifactHtmlReport('TikTok Contacts')
        report.start_artifact_report(report_folder, 'TikTok Contacts', description)
        report.add_script()
        data_headers1 = ('Timestamp','Nickname','Unique ID','Custom ID','URL')
        report.write_artifact_data_table(data_headers1, data_list1, file_found)
        report.end_artifact_report()
        
        tsvname = 'TikTok Contacts'
        tsv(report_folder, data_headers1, data_list1, tsvname)
        
        tlactivity = 'TikTok Last Contact'
        timeline(report_folder, tlactivity, data_list1, data_headers1)
        
    else:
        logfunc('No TikTok Contacts available')
    
    db.close()
    