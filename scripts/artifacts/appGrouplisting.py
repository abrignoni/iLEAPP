import biplist
import pathlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows


def get_appGrouplisting(files_found, report_folder, seeker):
    data_list = []       
    for file_found in files_found:
        file_found = str(file_found)

        plist = biplist.readPlist(file_found)
        bundleid = plist['MCMMetadataIdentifier']
        
        p = pathlib.Path(file_found)
        appgroupid = p.parent.name
        
        data_list.append((bundleid, appgroupid))
        fileloc = str(p.parents[1])

    if len(data_list) > 0:
        
        description = 'List can included once installed but not present apps. Each file is named .com.apple.mobile_container_manager.metadata.plist'
        report = ArtifactHtmlReport('Bundle ID - AppGroup ID')
        report.start_artifact_report(report_folder, 'Bundle ID - AppGroup ID', description)
        report.add_script()
        data_headers = ('Bundle ID','AppGroup')     
        report.write_artifact_data_table(data_headers, data_list, fileloc)
        report.end_artifact_report()
        
        tsvname = 'Bundle ID - AppGroup ID'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('Bundle ID - AppGroup ID')

    