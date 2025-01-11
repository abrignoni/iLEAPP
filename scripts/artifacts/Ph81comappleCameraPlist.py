__artifacts_v2__ = {
    'Ph81ComAppleCameraPlist': {
        'name': 'Ph81-Com-Apple-Camera-Plist',
        'description': 'Parses data from */mobile/Library/Preferences/com.apple.camera.plist which contains some'
                       ' important data related to the Apple Camera Application. Additional information and'
                       ' explanation of some keys-fields might be found with research and published blogs written by'
                       ' Scott Koenig https://theforensicscooter.com/',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains com.apple.camera.plist',
        'category': 'Photos-Z-Settings',
        'notes': '',
        'paths': ('*/mobile/Library/Preferences/com.apple.camera.plist',),
        "output_types": ["standard", "tsv", "none"]
    }
}

import datetime
import os
import plistlib
import nska_deserialize as nd
import scripts.artifacts.artGlobals
from scripts.builds_ids import OS_build
from scripts.ilapfuncs import artifact_processor, logfunc, device_info, get_file_path

@artifact_processor
def Ph81ComAppleCameraPlist(files_found, report_folder, seeker, wrap_text, time_offset):
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
