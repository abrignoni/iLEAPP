# Author:  Scott Koenig, assisted by past contributors
# Version: 1.0
#
#   Description:
#   Parses basic data from com.apple.purplebuddy.plist which contains some important data related to device restore.

import datetime
import os
import plistlib
import nska_deserialize as nd
import scripts.artifacts.artGlobals
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows


def get_ph83comapplepurplebuddyplist(files_found, report_folder, seeker, wrap_text, time_offset):
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            if key == 'SetupState':
                data_list.append(('SetupState', val))
                logdevinfo(f"<b>comapplepurplebuddyplist-SetupState: </b>{val}")

            else:
                data_list.append((key, val))

    if len(data_list) > 0:
        description = ('Parses basic data from com.apple.purplebuddy.plist which contains some important data'
                       ' related to device restore.')
        report = ArtifactHtmlReport('Photos-Z-Settings')
        report.start_artifact_report(report_folder, 'Ph83-Com-Apple-PurpleBuddy-Plist', description)
        report.add_script()
        data_headers = ('Key', 'Values')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'Ph83-Com-Apple-PurpleBuddy-Plist'
        tsv(report_folder, data_headers, data_list, tsvname)


__artifacts_v2__ = {
    'Ph83-Com-Apple-PurpleBuddy-Plist': {
        'name': 'Photos App Settings Ph83 com.apple.purplebuddy-plist',
        'description': 'Parses basic data from com.apple.purplebuddy.plist which contains some important data'
                       ' related to device restore.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.0',
        'date': '2024-06-8',
        'requirements': 'Acquisition that contains com.apple.purplebuddy.plist',
        'category': 'Photos-Z-Settings',
        'notes': '',
        'paths': '*/Library/Preferences/com.apple.purplebuddy.plist',
        'function': 'get_ph83comapplepurplebuddyplist'
    }
}
