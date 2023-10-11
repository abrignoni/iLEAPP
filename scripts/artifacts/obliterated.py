import datetime
import os
import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 

def get_obliterated(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    file_found = str(files_found[0])
    
    modified_time = os.path.getmtime(file_found)
    utc_modified_date = datetime.datetime.utcfromtimestamp(modified_time)
    
    logdevinfo(f'Obliterated Timestamp: {utc_modified_date}')
    
    data_list = []
    data_list.append((utc_modified_date,))
    
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Obliterated Time')
        report.start_artifact_report(report_folder, 'Obliterated Time')
        report.add_script()
        data_headers = ('Timestamp', )     
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Obliterated Time'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No Obliterated Time')
            



__artifacts__ = {
    "obliterated": (
        "Identifiers",
        ('*/root/.obliterated'),
        get_obliterated)
}
