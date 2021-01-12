import biplist

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_safariRecentWebSearches(files_found, report_folder, seeker):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        with open(file_found, "rb") as fp:
            try:
                plist = biplist.readPlist(fp)
                searches = plist.get('RecentWebSearches', [])
                for search in searches:
                    term = search.get('SearchString', '')
                    date = search.get('Date', '')
                    data_list.append((date, term))
            except biplist.InvalidPlistException as ex:
                logfunc(f'Failed to read plist {file_found}' + str(ex))
    report = ArtifactHtmlReport('Safari Recent WebSearches')
    report.start_artifact_report(report_folder, 'Recent WebSearches')
    report.add_script()
    data_headers = ('Date','Search Term')
    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()
    
    tsvname = 'Recent WebSearches'
    tsv(report_folder, data_headers, data_list, tsvname)