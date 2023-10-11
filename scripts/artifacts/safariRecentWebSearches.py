import biplist
import plistlib
import sys

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline

def get_safariRecentWebSearches(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
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
                
    if data_list:
        report = ArtifactHtmlReport('Safari Recent WebSearches')
        report.start_artifact_report(report_folder, 'Recent WebSearches')
        report.add_script()
        data_headers = ('Date','Search Term')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Recent WebSearches'
        tsv(report_folder, data_headers, data_list, tsvname)
        timeline(report_folder, tsvname, data_list, data_headers)
    else:
        logfunc('No data for recent web searches')

__artifacts__ = {
    "safariRecentWebSearches": (
        "Safari Browser",
        ('**/Library/Preferences/com.apple.mobilesafari.plist'),
        get_safariRecentWebSearches)
}
