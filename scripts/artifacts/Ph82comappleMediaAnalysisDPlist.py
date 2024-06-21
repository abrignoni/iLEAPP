# Author:  Scott Koenig, assisted by past contributors
# Version: 1.0
#
#   Description:
#   Parses basic data from */mobile/Library/Preferences/com.apple.mediaanalysisd.plist which contains
#   some important data related to Apple Photos Libraries storage locations and Media Analysis Completion.
#   Additional information and explanation of some keys-fields
#   might be found with research and published blogs written by Scott Koenig https://theforensicscooter.com/

import datetime
import os
import plistlib
import nska_deserialize as nd
import scripts.artifacts.artGlobals
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows


def get_82comapplemediaanalysisdplist(files_found, report_folder, seeker, wrap_text, time_offset):
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            data_list.append((key, val))

    if len(data_list) > 0:
        description = ('Parses basic data from */mobile/Library/Preferences/com.apple.mediaanalysisd.plist which'
                       ' contains some important data related to Apple Photos Libraries storage locations and'
                       ' Media Analysis Completion. Additional information and explanation of some keys-fields'
                       ' might be found with research and published blogs written by'
                       ' Scott Koenig https://theforensicscooter.com/')
        report = ArtifactHtmlReport('Ph82-Com-Apple-MediaAnalysisD-Plist')
        report.start_artifact_report(report_folder, 'Ph82-Com-Apple-MediaAnalysisD-Plist', description)
        report.add_script()
        data_headers = ('Key', 'Values')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'Ph82-Com-Apple-MediaAnalysisD-Plist'
        tsv(report_folder, data_headers, data_list, tsvname)


__artifacts_v2__ = {
    'Ph82-Com-Apple-MediaAnalysisD-Plist': {
        'name': 'Photo Libraries and Media Analysis Completion Ph82 Com-Apple-MediaAnalysisD-Plist',
        'description': 'Parses basic data from */mobile/Library/Preferences/com.apple.mediaanalysisd.plist which'
                       ' contains some important data related to Apple Photos Libraries storage locations and'
                       ' Media Analysis Completion. Additional information and explanation of some keys-fields'
                       ' might be found with research and published blogs written by'
                       ' Scott Koenig https://theforensicscooter.com/',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.0',
        'date': '2024-06-1',
        'requirements': 'Acquisition that contains com.apple.mediaanalysisd.plist',
        'category': 'Photos-Z-Settings',
        'notes': '',
        'paths': '*/mobile/Library/Preferences/com.apple.mediaanalysisd.plist',
        'function': 'get_82comapplemediaanalysisdplist'
    }
}
