__artifacts_v2__ = {
    "pingertextfree": {
        "name": "Text Free - Pinger",
        "description": "Text free messages",
        "author": "@AlexisBrignoni",
        "version": "0.0.1",
        "date": "2020-11-18",
        "requirements": "none",
        "category": "Pinger",
        "notes": "",
        "paths": ('*/Messaging_*.sqlite*'),
        "function": "get_pingertextfree",
        "output_types": "standard"
    }
}


import os
import shutil
import sqlite3
#import scripts.artifacts.artGlobals

#from packaging import version
#from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import artifact_processor, logfunc, logdevinfo, timeline, tsv, is_platform_windows, open_sqlite_db_readonly, media_to_html

@artifact_processor
def get_pingertextfree(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            ZCONVERSATIONCD.Z_PK
            from ZCONVERSATIONCD 
            order by ZCONVERSATIONCD.Z_PK
            ''')
        
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            data_list = []  
            
            if usageentries > 0:
                for row in all_rows:
                    cursor.execute(f'''
                    SELECT
                    ZCONVERSATIONCD.Z_PK,
                    datetime(ZCOMMUNICATIONCD.ZTIMECREATED, 'unixepoch'),
                    ZCOMMUNICATIONCD.ZCONVERSATION,
                    ZCOMMUNICATIONCD.ZDIRECTION,
                    ZCONVERSATIONCD.ZDISPLAYNAME,
                    ZCOMMUNICATIONCD.ZMYSTATUS,
                    ZCOMMUNICATIONCD.ZTEXT,
                    ZCOMMUNICATIONCD.ZTYPE,
                    ZCOMMUNICATIONCD.ZTIMECREATED
                    FROM ZCONVERSATIONCD, ZCOMMUNICATIONCD
                    WHERE ZCONVERSATIONCD.Z_PK = {row[0]}  AND ZCOMMUNICATIONCD.ZCONVERSATION = {row[0]}
                    order by ZCOMMUNICATIONCD.ZTIMECREATED
                    ''')
                    
                    all_rowsb = cursor.fetchall()
                    usageentriesb = len(all_rowsb)
                
                    
                    if usageentriesb > 0:
                        for rowb in all_rowsb:
                            data_list.append((rowb[1], rowb[2], rowb[3], rowb[4], rowb[5], rowb[6], rowb[7]))
        
            
            data_headers = (
                'Timestamp', 
                'Conversation ID',
                'Directionality to from Other Party', 
                'Other Party',
                'Status',
                'Text', 
                'Type'
                )
            return data_headers, data_list, file_found
        
            '''
            description = 'Text Free Messages'
            report = ArtifactHtmlReport('Text Free Messages')
            report.start_artifact_report(report_folder, 'Text Free Messages', description)
            report.add_script()
            data_headers = ('Timestamp', 'Conversation ID', 'Directionality to/from Other Party', 'Other Party', 'Status', 'Text', 'Type')
            report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Attachment'])
            report.end_artifact_report()
            
            tsvname = 'Text Free Messages'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Text Free Messages'
            timeline(report_folder, tlactivity, data_list, data_headers)
        '''
        else:
            logfunc('No Text Free Messages  data available')
        