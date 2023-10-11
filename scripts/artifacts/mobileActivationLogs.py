import os
import re
import pathlib

from datetime import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 


def get_mobileActivationLogs(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    data_list_info = []

    source_files = []
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.startswith('\\\\?\\'):
            file_name = pathlib.Path(file_found[4:]).name
            source_files.append(file_found[4:])
        else:
            file_name = pathlib.Path(file_found).name
            source_files.append(file_found)

        with open(file_found, 'r') as fp:        
            data = fp.readlines()
            linecount = 0
            hitcount = 0
            activationcount = 0
            
            for line in data:
                linecount += 1
                date_filter = re.compile(r'(([A-Za-z]+[\s]+([a-zA-Z]+[\s]+[0-9]+)[\s]+([0-9]+\:[0-9]+\:[0-9]+)[\s]+([0-9]{4}))([\s]+[\[\d\]]+[\s]+[\<a-z\>]+[\s]+[\(\w\)]+[\s]+[A-Z]{2}\:[\s]+)([main\:\s]*.*)$)')
                line_match = re.match(date_filter, line)

                if line_match:
                    date_time = (line_match.group(3, 5, 4))
                    conv_time = ' '.join(date_time)
                    dtime_obj = datetime.strptime(conv_time, '%b %d %Y %H:%M:%S')
                    ma_datetime = str(dtime_obj)
                    values = line_match.group(7)

                    if 'perform_data_migration' in values:
                        hitcount += 1
                        upgrade_match = re.search((r'((.*)(Upgrade\s+from\s+[\w]+\s+to\s+[\w]+\s+detected\.$))'), values)
                        if upgrade_match:
                            upgrade = upgrade_match.group(3)            
                            data_list.append((ma_datetime, upgrade, file_name))
                    
                    if '____________________ Mobile Activation Startup _____________________' in values:
                        activationcount += 1
                        ma_startup_line = str(linecount)
                        ma_startup = (f'Mobile Activation Startup at line: {ma_startup_line}')
                        data_list.append((ma_datetime, ma_startup, file_name))

                upgrade_entries = (f'Found {hitcount} Upgrade entries in {file_name}')
                boot_entries = (f'Found {activationcount} Mobile Activation entries in {file_name}')
            data_list_info.append((boot_entries, upgrade_entries))
            
    report = ArtifactHtmlReport('Mobile Activation Logs')
    report.start_artifact_report(report_folder, 'Mobile Activation Logs')
    report.add_script()
    data_headers_info = ('Mobile Activation', 'Upgrade')
    data_headers = ('Datetime', 'Event', 'Log Name')

    source_files_found = ', '.join(source_files)
    
    report.write_artifact_data_table(data_headers_info, data_list_info, source_files_found, cols_repeated_at_bottom=False)
    report.write_artifact_data_table(data_headers, data_list, source_files_found, True, False)
    report.end_artifact_report()
    
    tsvname = 'Mobile Activation Logs'
    tsv(report_folder, data_headers, data_list, tsvname)
    tsv(report_folder, data_headers_info, data_list_info, tsvname)

__artifacts__ = {
    "mobileActivationLogs": (
        "Mobile Activation Logs",
        ('**/mobileactivationd.log*'),
        get_mobileActivationLogs)
}