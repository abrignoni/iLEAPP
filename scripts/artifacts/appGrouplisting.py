import biplist
import pathlib
import plistlib
import sys

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows


def get_appGrouplisting(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []       
    for file_found in files_found:
        file_found = str(file_found)
        with open(file_found, "rb") as fp:
            if sys.version_info >= (3, 9):
                plist = plistlib.load(fp)
            else:
                plist = biplist.readPlist(fp)
            bundleid = plist['MCMMetadataIdentifier']
            
            p = pathlib.Path(file_found)
            appgroupid = p.parent.name
            fileloc = str(p.parents[1])
            typedir = str(p.parents[1].name)
            
            data_list.append((bundleid, typedir, appgroupid, fileloc))
        
    if len(data_list) > 0:
        filelocdesc = 'Path column in the report'
        description = 'List can included once installed but not present apps. Each file is named .com.apple.mobile_container_manager.metadata.plist'
        report = ArtifactHtmlReport('Bundle ID by AppGroup & PluginKit IDs')
        report.start_artifact_report(report_folder, 'Bundle ID by AppGroup & PluginKit IDs', description)
        report.add_script()
        data_headers = ('Bundle ID','Type','Directory GUID','Path')     
        report.write_artifact_data_table(data_headers, data_list, filelocdesc)
        report.end_artifact_report()
        
        tsvname = 'Bundle ID - AppGroup ID - PluginKit ID'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No data on Bundle ID - AppGroup ID - PluginKit ID')

__artifacts__ = {
    "appgrouplisting": (
        "Installed Apps",
        ('*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist', '**/PluginKitPlugin/*.metadata.plist'),
        get_appGrouplisting)
}