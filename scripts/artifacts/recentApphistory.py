import biplist
import datetime

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_recentApphistory(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    file_found = ''
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

    data_headers = ('Timestamp', 'Bundle ID')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_recentApphistory": {
        "name": "CarPlay",
        "description": "CarPlay recent app history.",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "CarPlay",
        "notes": "",
        "paths": ('*/com.apple.CarPlayApp.plist',),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
