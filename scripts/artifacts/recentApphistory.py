import biplist
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows


def get_recentApphistory(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        with open(file_found, 'rb') as f:
            plist = biplist.readPlist(f)
            RecentAppHistory = plist.get('CARRecentAppHistory')
            
        if RecentAppHistory is not None:
            if len(RecentAppHistory) > 0:
                for bundleid, timestamp in RecentAppHistory.items():
                    timestamp = (datetime.datetime.utcfromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S'))
                    data_list.append((timestamp, bundleid))
        
    if len(data_list) > 0:
        description = 'CarPlay recent app history.'
        report = ArtifactHtmlReport('CarPlay Recent App History')
        report.start_artifact_report(report_folder, 'CarPlay Recent App History', description)
        report.add_script()
        data_headers = ('Timestamp','Bundle ID')     
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'CarPlay Recent App History'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'CarPlay Recent App History'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No data on CarPlay Recent App History')

__artifacts_v2__ = {
    "recentApphistory": {
        "name": "CarPlay",
        "description": "",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "CarPlay",
        "notes": "",
        "paths": ('*/com.apple.CarPlayApp.plist'),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
    