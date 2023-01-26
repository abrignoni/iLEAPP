import datetime
import email
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, media_to_html

def get_offlinePages(files_found, report_folder, seeker, wrap_text):
    
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        modified_time = os.path.getmtime(file_found)
        utc_modified_date = datetime.datetime.utcfromtimestamp(modified_time)
        
        with open(file_found,'r', errors='replace') as fp:
            message = email.message_from_file(fp)
            sourced = (message['Snapshot-Content-Location'])
            subjectd = (message['Subject'])
            dated = (message['Date'])
            media = media_to_html(file_found, files_found, report_folder)

        data_list.append((utc_modified_date, media, sourced, subjectd, dated, file_found))
        
    if len(data_list) > 0:
        note = 'Source location in extraction found in the report for each item.'
        report = ArtifactHtmlReport('Offline Pages')
        report.start_artifact_report(report_folder, f'Offline Pages')
        report.add_script()
        data_headers = ('Timestamp Modified', 'File', 'Web Source', 'Subject', 'MIME Date', 'Source in Extraction')
        report.write_artifact_data_table(data_headers, data_list, note, html_no_escape=['File'])
        report.end_artifact_report()
        
        tsvname = f'Offline Pages'
        tsv(report_folder, data_headers, data_list, tsvname)

__artifacts__ = {
        "pages": (
                "Offline Pages",
                ('*/*.mhtml', '*/*.mht'),
                get_offlinePages)
}
            