from datetime import datetime
import plistlib

from scripts.ilapfuncs import logdevinfo, artifact_processor


@artifact_processor
def get_findMy(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():

            if key == 'addTime':
                addtime = datetime.utcfromtimestamp(val)
                data_list.append(('Find My iPhone Add Time', addtime))
                logdevinfo("<b>Find My iPhone: </b>Enabled")
                logdevinfo(f"<b>Find My iPhone Add Time: </b>{addtime}")

            else:
                data_list.append((key, val ))

    data_headers = ('Key', 'Values')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_findMy": {
        "name": "Identifiers",
        "description": "",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/mobile/Library/Preferences/com.apple.icloud.findmydeviced.FMIPAccounts.plist',),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
