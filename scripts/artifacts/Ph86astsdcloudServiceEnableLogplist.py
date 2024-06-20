# Author:  Scott Koenig https://theforensicscooter.com/
# Version: 1.0
#
#   Description:
#   Parses basic data from */PhotoData/private/com.apple.assetsd/cloudServiceEnableLog.plist which is a plist that
#   tracks when Cloud Photos Library (CPL) has been enabled.
#   Based on research and published blogs written by Scott Koenig https://theforensicscooter.com/

import os
import plistlib
import biplist
import nska_deserialize as nd
import scripts.artifacts.artGlobals
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 


def get_ph86assetsdcldservenalogplist(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
    if len(pl) > 0:
        for key in pl:
            if 'timestamp' in key:
                timestamputc = key['timestamp']
            else:
                timestamputc = ''
            if 'type' in key:
                servicetype = key['type']
            else:
                servicetype = ''
            if 'enabled' in key:
                enabledstate = key['enabled']
            else:
                enabledstate = ''

            data_list.append((timestamputc, servicetype, enabledstate))

    description = ('Parses basic data from */PhotoData/private/com.apple.assetsd/cloudServiceEnableLog.plist'
                   ' which is a plist that tracks when Cloud Photos Library (CPL) has been enabled.'
                   ' Based on research and published blogs written by Scott Koenig https://theforensicscooter.com/')
    report = ArtifactHtmlReport('Photos-Z-Settings')
    report.start_artifact_report(report_folder, 'Ph86-assetsd-cloud-Service-Enable-Log-Plist', description)
    report.add_script()
    data_headers = ('TimestampUTC', 'Service-Type', 'Enabled-State')
    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()

    tsvname = 'Ph86-assetsd-cloud-Service-Enable-Log-Plist'
    tsv(report_folder, data_headers, data_list, tsvname)


__artifacts_v2__ = {
    'Ph86-assetsd-cloud-Service-Enable-Log-Plist': {
        'name': 'Assetsd Ph86 cloud Services Enable Log Plist',
        'description': 'Parses basic data from */PhotoData/private/com.apple.accountsd/cloudServiceEnableLog.plist'
                       ' which is a plist that tracks when Cloud Photos Library (CPL) has been enabled.'
                       ' Based on research and published blogs written by Scott Koenig https://theforensicscooter.com/',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.0',
        'date': '2024-06-20',
        'requirements': 'Acquisition that contains assetsd cloudServiceEnableLog.plist',
        'category': 'Photos-Z-Settings',
        'notes': '',
        'paths': '*/com.apple.assetsd/cloudServiceEnableLog.plist',
        'function': 'get_ph86assetsdcldservenalogplist'
    }
}
