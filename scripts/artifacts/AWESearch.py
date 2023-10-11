import os
import plistlib
from datetime import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import timeline, logfunc, logdevinfo, tsv, is_platform_windows

def get_AWESearch(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        
        with open(file_found, 'rb') as fp:
            pl= plistlib.load(fp)
        for x in pl:
            kword = (x['keyword'])
            cocoatime = (x['time'])
            unix_timestamp = cocoatime + 978307200
            converted = datetime.utcfromtimestamp(unix_timestamp)
            data_list.append((converted, kword))

    if len(data_list) > 0:
        report = ArtifactHtmlReport('TikTok Search')
        report.start_artifact_report(report_folder, 'TikTok Search')
        report.add_script()
        data_headers = ('Time','Keyword')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
            
        tsvname = 'TikTok Search'
        tsv(report_folder, data_headers, data_list, tsvname)
            
        tlactivity = f'TikTok - Search History'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No data on TikTok Search')

            
        
__artifacts__ = {
    "AWESearch": (
        "TikTok",
        ('*/Documents/search_history/history_words/AWESearchHistory*'),
        get_AWESearch)
}

