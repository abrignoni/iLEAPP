__artifacts_v2__ = {
    "cachev0": {
        "name": "Image cacheV0",
        "description": "Images cached in the SQLite database.",
        "author": "@AlexisBrignoni",
        "version": "0.1",
        "date": "2024-02-06",
        "requirements": "none",
        "category": "Image cacheV0",
        "notes": "",
        "paths": ('*/cacheV0.db*',),
        "function": "get_cachev0"
    }
}

from pathlib import Path
import uuid
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone, media_to_html


def get_cachev0(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('cacheV0.db'):
            
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            id,
            data 
            FROM cache
            ''')
        
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            
            for row in all_rows:
                images_list = []
                uuidvalue = uuid.uuid4().hex
                dest = Path(report_folder, uuidvalue)
                
                with open(f'{dest}', 'wb') as file:
                    file.write(row[1])
                
                images_list.append(str(dest))
                thumb = media_to_html(uuidvalue, images_list, report_folder)
                data_list.append((row[0],thumb,file_found))
            
    if len(data_list) > 0:
        
        description = 'Image media cache. Image source located in the Source DB field.'
        report = ArtifactHtmlReport('Image cacheV0')
        report.start_artifact_report(report_folder, 'Image cacheV0', description)
        report.add_script()
        data_headers = ('ID','Media','Source DB' )
        report.write_artifact_data_table(data_headers, data_list, '', html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'Image cacheV0'
        tsv(report_folder, data_headers, data_list, tsvname)

    else:
        logfunc('No Image cacheV0 data available')
    
    
        