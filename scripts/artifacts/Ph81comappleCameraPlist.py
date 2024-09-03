# Author:  Scott Koenig, assisted by past contributors
# Version: 1.0
#
#   Description:
#   Parses basic data from */mobile/Library/Preferences/com.apple.camera.plist which contains some important data
#   related to the Apple Camera Application. Additional information and explanation of some keys-fields
#   might be found with research and published blogs written by Scott Koenig https://theforensicscooter.com/

import datetime
import os
import plistlib
import nska_deserialize as nd
import scripts.artifacts.artGlobals
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows


def get_81comapplecameraplist(files_found, report_folder, seeker, wrap_text, time_offset):
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            if key == 'CAMUserPreferenceSharedLibraryLastDiscoveryLocation':
                pathto = os.path.join(report_folder, 'CAMUserPreferenceSharedLibraryLastDiscoveryLocation' + '.bplist')
                with open(pathto, "ab") as wf:
                    wf.write(val)

                with open(pathto, "rb") as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        val = deserialized_plist

                    except (nd.DeserializeError,
                            nd.biplist.NotBinaryPlistException,
                            nd.biplist.InvalidPlistException,
                            plistlib.InvalidFileException,
                            nd.ccl_bplist.BplistError,
                            ValueError,
                            TypeError, OSError, OverflowError) as ex:
                        logfunc('Had exception: ' + str(ex))
                data_list.append(('CAMUserPreferenceSharedLibraryLastDiscoveryLocation', val))

            elif key == 'CAMUserPreferenceSharedLibraryLastLocation':
                pathto = os.path.join(report_folder, 'CAMUserPreferenceSharedLibraryLastLocation' + '.bplist')
                with open(pathto, "ab") as wf:
                    wf.write(val)

                with open(pathto, "rb") as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        val = deserialized_plist

                    except (nd.DeserializeError,
                            nd.biplist.NotBinaryPlistException,
                            nd.biplist.InvalidPlistException,
                            plistlib.InvalidFileException,
                            nd.ccl_bplist.BplistError,
                            ValueError,
                            TypeError, OSError, OverflowError) as ex:
                        logfunc('Had exception: ' + str(ex))
                data_list.append(('CAMUserPreferenceSharedLibraryLastLocation', val))

            elif key == 'CAMUserPreferenceSharedLibraryLastUserActionLocation':
                pathto = os.path.join(report_folder, 'CAMUserPreferenceSharedLibraryLastUserActionLocation' + '.bplist')
                with open(pathto, "ab") as wf:
                    wf.write(val)

                with open(pathto, "rb") as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        val = deserialized_plist

                    except (nd.DeserializeError,
                            nd.biplist.NotBinaryPlistException,
                            nd.biplist.InvalidPlistException,
                            plistlib.InvalidFileException,
                            nd.ccl_bplist.BplistError,
                            ValueError,
                            TypeError, OSError, OverflowError) as ex:
                        logfunc('Had exception: ' + str(ex))
                data_list.append(('CAMUserPreferenceSharedLibraryLastUserActionLocation', val))

            elif key == 'CAMUserPreferenceExposureBiasByMode':
                pathto = os.path.join(report_folder, 'CAMUserPreferenceExposureBiasByMode' + '.bplist')
                with open(pathto, "ab") as wf:
                    wf.write(val)

                with open(pathto, "rb") as f:
                    try:
                        deserialized_plist = nd.deserialize_plist(f)
                        val = deserialized_plist

                    except (nd.DeserializeError,
                            nd.biplist.NotBinaryPlistException,
                            nd.biplist.InvalidPlistException,
                            plistlib.InvalidFileException,
                            nd.ccl_bplist.BplistError,
                            ValueError,
                            TypeError, OSError, OverflowError) as ex:
                        logfunc('Had exception: ' + str(ex))
                data_list.append(('CAMUserPreferenceExposureBiasByMode', val))

            else:
                data_list.append((key, val))

    if len(data_list) > 0:
        description = ('Parses data from */mobile/Library/Preferences/com.apple.camera.plist which contains some'
                       ' important data related to the Apple Camera Application. Additional information and'
                       ' explanation of some keys-fields might be found with research and published blogs written by'
                       ' Scott Koenig https://theforensicscooter.com/')
        report = ArtifactHtmlReport('Ph81-Com-Apple-Camera-Plist')
        report.start_artifact_report(report_folder, 'Ph81-Com-Apple-Camera-Plist', description)
        report.add_script()
        data_headers = ('Key', 'Values')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'Ph81-Com-Apple-Camera-Plist'
        tsv(report_folder, data_headers, data_list, tsvname)


__artifacts_v2__ = {
    'Ph81-Com-Apple-Camera-Plist': {
        'name': 'Camera App Settings Ph81 Com-Apple-Camera-Plist',
        'description': 'Parses data from */mobile/Library/Preferences/com.apple.camera.plist which contains some'
                       ' important data related to the Apple Camera Application. Additional information and'
                       ' explanation of some keys-fields might be found with research and published blogs written by'
                       ' Scott Koenig https://theforensicscooter.com/',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.0',
        'date': '2024-06-1',
        'requirements': 'Acquisition that contains com.apple.camera.plist',
        'category': 'Photos-Z-Settings',
        'notes': '',
        'paths': '*/mobile/Library/Preferences/com.apple.camera.plist',
        'function': 'get_81comapplecameraplist'
    }
}
