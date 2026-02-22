import biplist
import plistlib
import sys

from scripts.ilapfuncs import logfunc, artifact_processor


@artifact_processor
def get_safariRecentWebSearches(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    file_found = str(files_found[0])
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.db'):
            break

    with open(file_found, "rb") as fp:
        try:
            if sys.version_info >= (3, 9):
                plist = plistlib.load(fp)
            else:
                plist = biplist.readPlist(fp)
            searches = plist.get('RecentWebSearches', [])
            for search in searches:
                term = search.get('SearchString', '')
                date = search.get('Date', '')
                data_list.append((date, term))
        except (biplist.InvalidPlistException, plistlib.InvalidFileException) as ex:
            logfunc(f'Failed to read plist {file_found} ' + str(ex))

    data_headers = ('Date', 'Search Term')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_safariRecentWebSearches": {
        "name": "Safari Recent Web Searches",
        "description": "",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Safari Browser",
        "notes": "",
        "paths": ('**/Library/Preferences/com.apple.mobilesafari.plist',),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
