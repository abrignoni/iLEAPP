# pylint: disable=W0611,W0613
__artifacts_v2__ = {
    'Ph081ComAppleCameraPlist': {
        'name': 'Ph081-Com-Apple-Camera-Plist',
        'description': 'Parses data from */mobile/Library/Preferences/com.apple.camera.plist which contains some'
                       ' important data related to the Apple Camera Application. Additional information and'
                       ' explanation of some keys-fields might be found with research and published blogs by Scott Koenig'
                       ' https://theforensicscooter.com/2024/05/18/ileapp-parsers-photos-sqlite-queries/',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains com.apple.camera.plist',
        'category': 'Photos.sqlite-Y-Settings-Plist-Camera',
        'notes': '',
        'paths': ('*/mobile/Library/Preferences/com.apple.camera.plist',),
        "output_types": ["standard", "tsv", "none"],
        "artifact_icon": "settings",
        'sample_data': {
            'ctf2020_ios12': 'iOS 12.4 | 25 rows',
            'dexter_ios18': 'iOS 18.3.2 | 68 rows',
            'felix_ios17': 'iOS 17.6.1 | 41 rows',
            'fsfull002_ios17': 'iOS 17.1 | 40 rows',
            'hc_ios18_7': 'iOS 18.7.8 | 31 rows',
            'iphone11_ios17': 'iOS 17.3 | 41 rows',
            'iphone12_ios18': 'iOS 18.7 | 40 rows',
            'otto_ios17': 'iOS 17.5.1 | 43 rows',
            'abe_ios16': 'iOS 16.5 | 35 rows',
            'felix23_ios16': 'iOS 16.5 | 26 rows',
            'hickman_ios13': 'iOS 13.3.1 | 18 rows',
            'hickman_ios14': 'iOS 14.3 | 19 rows',
            'jess_ios15': 'iOS 15.0.2 | 23 rows',
            'magnet_ios16': 'iOS 16.1.1 | 39 rows',
        }
    }
}

import datetime
import os
import plistlib
import nska_deserialize as nd
from scripts.ilapfuncs import artifact_processor, logfunc, device_info, get_file_path

@artifact_processor
def Ph081ComAppleCameraPlist(files_found, report_folder, seeker, wrap_text, time_offset):
    data_list = []
    source_path = str(files_found[0])

    with open(source_path, "rb") as fp:
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
                data_list.append(('CAMUserPreferenceSharedLibraryLastDiscoveryLocation', str(val)))

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
                data_list.append(('CAMUserPreferenceSharedLibraryLastLocation', str(val)))

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
                data_list.append(('CAMUserPreferenceSharedLibraryLastUserActionLocation', str(val)))

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
                data_list.append(('CAMUserPreferenceExposureBiasByMode', str(val)))

            else:
                data_list.append((key, str(val)))

    data_headers = ('Property','Property Value')
    return data_headers, data_list, source_path
