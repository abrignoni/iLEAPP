__artifacts_v2__ = {
    "get_applePodcasts": {
        "function": "get_applePodcasts",
        "name": "Apple Podcasts",
        "description": "Extract Apple podcasts shows and episodes.",
        "author": "@stark4n6",
        "version": "0.1",
        "date": "2021-07-21",
        "requirements": "none",
        "category": "Apple Podcasts",
        "notes": "",
        "paths": ('*/MTLibrary.sqlite*'),
        "output_types": "none"
    }
}

import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lavafuncs import lava_process_artifact, lava_insert_sqlite_data
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_applePodcasts(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('.sqlite'):
            continue # Skip all other files
    
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(ZADDEDDATE + 978307200, 'unixepoch'),
        datetime(ZLASTDATEPLAYED + 978307200, 'unixepoch'),
        datetime(ZUPDATEDDATE + 978307200, 'unixepoch'),
        datetime(ZDOWNLOADEDDATE + 978307200, 'unixepoch'),
        ZAUTHOR,
        ZTITLE,
        ZFEEDURL,
        ZITEMDESCRIPTION,
        ZWEBPAGEURL
        from ZMTPODCAST
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            
            
            data_list1 = []
            for row in all_rows:
                
                if (row[0] == '') or (row[0]== None):
                    timestampadded = ''
                else:
                    timestampadded = convert_ts_human_to_utc(row[0])
                    timestampadded = convert_utc_human_to_timezone(timestampadded,timezone_offset)
                
                if (row[1] == '') or (row[1]== None):
                    timestampdateplayed = ''
                else:
                    timestampdateplayed = convert_ts_human_to_utc(row[1])
                    timestampdateplayed  = convert_utc_human_to_timezone(timestampdateplayed,timezone_offset)
                
                if (row[2] == '') or (row[2]== None):
                    timestampdupdate = ''
                else:
                    timestampdupdate = convert_ts_human_to_utc(row[2])
                    timestampdupdate = convert_utc_human_to_timezone(timestampdupdate,timezone_offset)
                
                if (row[3] == '') or (row[3]== None):
                    timestampdowndate = ''
                else:
                    timestampdowndate = convert_ts_human_to_utc(row[3])
                    timestampdowndate  = convert_utc_human_to_timezone(timestampdowndate,timezone_offset)
                
                data_list1.append((timestampadded,timestampdateplayed,timestampdupdate,timestampdupdate,row[4],row[5],row[6],row[7],row[8]))
            
            data_headers1 = [
                'Date Added',
                'Date Last Played',
                'Date Last Updated',
                'Date Downloaded',
                'Author','Title',
                'Feed URL',
                'Description',
                'Web Page URL']
            
            report1 = ArtifactHtmlReport('Apple Podcasts - Shows')
            report1.start_artifact_report(report_folder, 'Apple Podcasts - Shows')
            report1.add_script()
            report1.write_artifact_data_table(data_headers1, data_list1, file_found)
            report1.end_artifact_report()
            
            tsv(report_folder, data_headers1, data_list1, 'Apple Podcasts - Shows')
                
        else:
            logfunc('No Apple Podcasts - Shows data available')
        
        cursor.execute('''
        SELECT
        datetime(ZIMPORTDATE + 978307200, 'unixepoch'),
        CASE ZMETADATATIMESTAMP
            WHEN 0 THEN ''
            ELSE datetime(ZMETADATATIMESTAMP + 978307200, 'unixepoch')
        END,
        datetime(ZLASTDATEPLAYED + 978307200, 'unixepoch'),
        datetime(ZPLAYSTATELASTMODIFIEDDATE + 978307200, 'unixepoch'),
        datetime(ZDOWNLOADDATE + 978307200, 'unixepoch'),
        ZPLAYCOUNT,
        ZAUTHOR,
        ZTITLE,
        ZITUNESSUBTITLE,
        ZASSETURL,
        ZWEBPAGEURL,
        ZDURATION,
        ZBYTESIZE,
        ZPLAYSTATE
        FROM ZMTEPISODE
        ORDER by ZMETADATATIMESTAMP
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        
        if usageentries > 0:
            data_list2 = []
            for row in all_rows:
                
                timestampimport = convert_ts_human_to_utc(row[0])
                timestampimport = convert_utc_human_to_timezone(timestampimport ,timezone_offset)
                
                if (row[1] == '') or (row[1]== None):
                    timestampmeta = ''
                else:
                    timestampdameta = convert_ts_human_to_utc(row[1])
                    timestampdameta = convert_utc_human_to_timezone(timestampdameta,timezone_offset)
                
                if (row[2] == '') or (row[2]== None):
                    timestamplastplay = ''
                else:
                    timestamplastplay = convert_ts_human_to_utc(row[2])
                    timestamplastplay = convert_utc_human_to_timezone(timestamplastplay,timezone_offset)
                
                if (row[3] == '') or (row[3]== None):
                    timestamplastmod = ''
                else:
                    timestamplastmod = convert_ts_human_to_utc(row[3])
                    timestamplastmod = convert_utc_human_to_timezone(timestamplastmod,timezone_offset)
                
                if (row[4] == '') or (row[4]== None):
                    timestampdowndate = ''
                else:
                    timestampdowndate = convert_ts_human_to_utc(row[4])
                    timestampdowndate = convert_utc_human_to_timezone(timestampdupdate,timezone_offset)

            data_list2.append((timestampimport,timestampmeta,timestamplastplay,timestamplastmod,timestampdowndate,row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13]))
            
            data_headers2 = [
                'Import Date',
                'Metadata Timestamp',
                'Date Last Played',
                'Play State Last Modified',
                'Download Date',
                'Play Count',
                'Author',
                'Title',
                'Subtitle',
                'Asset URL',
                'Web Page URL',
                'Duration',
                'Size',
                'Play State'] 
            
            report2 = ArtifactHtmlReport('Apple Podcasts - Episodes')
            report2.start_artifact_report(report_folder, 'Apple Podcasts - Episodes')
            report2.add_script()
            report2.write_artifact_data_table(data_headers2, data_list2, file_found)
            report2.end_artifact_report()
            
            tsv(report_folder, data_headers2, data_list2, 'Apple Podcasts - Episodes')
            

        else:
            logfunc('No Apple Podcasts - Episodes data available')
    
    category = "Apple Podcasts"
    module_name = "get_applePodcasts"
    
    if data_list1:

        data_headers1[0] = (data_headers1[0], 'datetime')
        data_headers1[1] = (data_headers1[1], 'datetime')
        data_headers1[2] = (data_headers1[2], 'datetime')
        data_headers1[3] = (data_headers1[3], 'datetime')
        
        table_name1, object_columns1, column_map1 = lava_process_artifact(category, module_name, 'Apple Podcasts - Shows', data_headers1, len(data_list1))
        lava_insert_sqlite_data(table_name1, data_list1, object_columns1, data_headers1, column_map1)
    
    if data_list2:
        data_headers2[0] = (data_headers2[0], 'datetime')
        data_headers2[1] = (data_headers2[1], 'datetime')
        data_headers2[2] = (data_headers2[2], 'datetime')
        data_headers2[3] = (data_headers2[3], 'datetime')
        data_headers2[4] = (data_headers2[4], 'datetime')
        
        table_name2, object_columns2, column_map2 = lava_process_artifact(category, module_name, 'Apple Podcasts - Episodes', data_headers2, len(data_list2))
        lava_insert_sqlite_data(table_name2, data_list2, object_columns2, data_headers2, column_map2)    
        

        