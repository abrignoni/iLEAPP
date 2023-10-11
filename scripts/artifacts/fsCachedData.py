import os
import magic
import datetime
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, tsv, is_platform_windows, open_sqlite_db_readonly, media_to_html


def get_fsCachedData(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []  
    
    for file_found in files_found:
        file_found = str(file_found)
        
        filename = os.path.basename(file_found)
        
        modified_time = os.path.getmtime(file_found)
        utc_modified_date = datetime.datetime.utcfromtimestamp(modified_time)

        #ext = (mime.split('/')[1])
            
        if os.path.isfile(file_found):
            mime = magic.from_file(file_found, mime=True)
            media = media_to_html(file_found, files_found, report_folder)
            data_list.append((utc_modified_date, media, mime, filename, file_found))
        
    
    if len(data_list) > 0:
        note = 'Source location in extraction found in the report for each item.'
        description = 'Media files'
        report = ArtifactHtmlReport('fsChachedData')
        report.start_artifact_report(report_folder, 'fsChachedData', description)
        report.add_script()
        data_headers = ('Timestamp Modified', 'Media', 'Mime Type', 'Filename', 'Path')
        report.write_artifact_data_table(data_headers, data_list, note, html_no_escape=['Media'])
        report.end_artifact_report()
        
        tsvname = 'fsChachedData'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'fsChachedData'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No fsChachedData data available')
        

__artifacts__ = {
    "fsChachedData": (
        "Cache Data",
        ('*/fsCachedData/**'),
        get_fsCachedData)
}