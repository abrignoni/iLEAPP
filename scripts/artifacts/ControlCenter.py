__artifacts_v2__ = {
    "controlcenter": {
        "name": "Control Center Configuration",
        "description": "Parses controls/apps added to the Control Center",
        "author": "@KevinPagano3",
        "version": "0.0.1",
        "date": "2022-04-28",
        "requirements": "none",
        "category": "Control Center",
        "notes": "",
        "paths": ('*/mobile/Library/ControlCenter/ModuleConfiguration.plist',),
        "function": "get_ControlCenter"
    }
}


import plistlib
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 

def get_ControlCenter(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list_disabled = []
    data_list_modules = []
    data_list_userenabled = []
    count = 0
   
    for file_found in files_found:
        file_found = str(file_found)

        with open(file_found, 'rb') as f:
            pl = plistlib.load(f)
            
            check_var = pl.get('disabled-module-identifiers','notfound')
            
            if check_var == 'notfound':
                pass
            else:
                if len(pl['disabled-module-identifiers']) > 0:
                    for module1 in pl['disabled-module-identifiers']:
                        count += 1
                        data_list_disabled.append((count, module1))
                else: pass
            
            count = 0
            check_var = pl.get('module-identifiers','notfound')
            
            if check_var == 'notfound':
                pass
            else:
                if len(pl['module-identifiers']) > 0:
                    for module2 in pl['module-identifiers']:
                        count += 1
                        data_list_modules.append((count, module2))
                        
                else: pass
            
            count = 0
            check_var = pl.get('userenabled-fixed-module-identifiers','notfound')
            
            if check_var == 'notfound':
                pass
            else:
                if len(pl['userenabled-fixed-module-identifiers']) > 0:
                    for module3 in pl['userenabled-fixed-module-identifiers']:
                        count += 1
                        data_list_userenabled.append((count, module3))    
                else: pass
            
    if len(data_list_disabled) > 0:
        description = 'Controls disabled in the Control Center'
        report = ArtifactHtmlReport('Control Center - Disabled Controls')
        report.start_artifact_report(report_folder, 'Control Center - Disabled Controls')
        report.add_script()
        data_headers = ['Position','App Bundle']
        report.write_artifact_data_table(data_headers, data_list_disabled, file_found)
        report.end_artifact_report()
        
        tsvname = 'Control Center - Disabled Controls'
        tsv(report_folder, data_headers, data_list_disabled, tsvname)
        
    else:
        logfunc('No Control Center - Disabled Controls data available')
            
    if len(data_list_modules) > 0:
        description = 'Controls that are active and added to Control Center'
        report = ArtifactHtmlReport('Control Center - Active Controls')
        report.start_artifact_report(report_folder, 'Control Center - Active Controls')
        report.add_script()
        data_headers = ['Position','App Bundle']
        report.write_artifact_data_table(data_headers, data_list_modules, file_found)
        report.end_artifact_report()
        
        tsvname = 'Control Center - Active Controls'
        tsv(report_folder, data_headers, data_list_modules, tsvname)
    
    else:
        logfunc('No Control Center - Active Controls data available')
        
    if len(data_list_userenabled) > 0:
        description = 'Controls that have been added by the user via a hard toggle to the Control Center'
        report = ArtifactHtmlReport('Control Center - User Toggled Controls')
        report.start_artifact_report(report_folder, 'Control Center - User Toggled Controls')
        report.add_script()
        data_headers = ['Position','App Bundle']
        report.write_artifact_data_table(data_headers, data_list_userenabled, file_found)
        report.end_artifact_report()
        
        tsvname = 'Control Center - User Toggled Controls'
        tsv(report_folder, data_headers, data_list_userenabled, tsvname)
    
    else:
        logfunc('No Control Center - User Toggled Controls data available')

# __artifacts__ = {
#     "controlcenter": (
#         "Control Center",
#         ('*/mobile/Library/ControlCenter/ModuleConfiguration.plist'),
#         get_ControlCenter)
# }