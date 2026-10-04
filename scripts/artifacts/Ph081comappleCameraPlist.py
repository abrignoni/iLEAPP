__artifacts_v2__ = {
    "Ph081ComAppleCameraPlist": {
        "name": "Ph081-Com-Apple-Camera-Plist",
        "description": "Parses distinct files matched by */mobile/Library/Preferences/com.apple.camera.plist, which is the"
            " preferences file of the Camera app. Values are reported as stored; four keys that hold"
            " embedded plists (the three CAMUserPreferenceSharedLibrary location keys and"
            " CAMUserPreferenceExposureBiasByMode) are shown decoded when they can be read. Scott"
            " Koenig describes the CAMUserPreferenceTimerDuration key, as observed on iOS 14.7 and"
            " 15.1, at"
            " https://theforensicscooter.com/2022/05/02/photos-sqlite-query-documentation-notable-artifacts/"
            " . What the other keys mean is not established here.",
        "author": "Scott Koenig, @AlexisBrignoni, Codex",
        "creation_date": "2025-01-05",
        "last_update_date": "2026-10-04",
        "requirements": "Acquisition that contains com.apple.camera.plist",
        "category": "Photos.sqlite",
        "notes": "",
        "paths": ("*/mobile/Library/Preferences/com.apple.camera.plist",),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "settings",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 25 rows",
            "dexter_ios18": "iOS 18.3.2 | 68 rows",
            "felix_ios17": "iOS 17.6.1 | 41 rows",
            "fsfull002_ios17": "iOS 17.1 | 40 rows",
            "hc_ios18_7": "iOS 18.7.8 | 31 rows",
            "iphone11_ios17": "iOS 17.3 | 41 rows",
            "iphone12_ios18": "iOS 18.7 | 40 rows",
            "otto_ios17": "iOS 17.5.1 | 43 rows",
            "abe_ios16": "iOS 16.5 | 35 rows",
            "felix23_ios16": "iOS 16.5 | 26 rows",
            "hickman_ios13": "iOS 13.3.1 | 18 rows",
            "hickman_ios14": "iOS 14.3 | 19 rows",
            "jess_ios15": "iOS 15.0.2 | 23 rows",
            "magnet_ios16": "iOS 16.1.1 | 39 rows",
        }
    }
}

import os
import plistlib
import nska_deserialize as nd
from scripts.ilapfuncs import artifact_processor, logfunc

@artifact_processor
def Ph081ComAppleCameraPlist(context):
    files_found = list(dict.fromkeys(str(path) for path in context.get_files_found()))
    report_folder = context.get_report_folder()
    data_list = []

    for source_index, source_path in enumerate(files_found):
        export_suffix = f"-{source_index + 1}" if len(files_found) > 1 else ""
        with open(source_path, "rb") as fp:
            pl = plistlib.load(fp)
            for key, val in pl.items():

                if key == 'CAMUserPreferenceSharedLibraryLastDiscoveryLocation':
                    pathto = os.path.join(report_folder, 'CAMUserPreferenceSharedLibraryLastDiscoveryLocation' + export_suffix + '.bplist')
                    with open(pathto, "wb") as wf:
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
                    data_list.append(('CAMUserPreferenceSharedLibraryLastDiscoveryLocation', str(val), context.get_relative_path(source_path)))

                elif key == 'CAMUserPreferenceSharedLibraryLastLocation':
                    pathto = os.path.join(report_folder, 'CAMUserPreferenceSharedLibraryLastLocation' + export_suffix + '.bplist')
                    with open(pathto, "wb") as wf:
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
                    data_list.append(('CAMUserPreferenceSharedLibraryLastLocation', str(val), context.get_relative_path(source_path)))

                elif key == 'CAMUserPreferenceSharedLibraryLastUserActionLocation':
                    pathto = os.path.join(report_folder, 'CAMUserPreferenceSharedLibraryLastUserActionLocation' + export_suffix + '.bplist')
                    with open(pathto, "wb") as wf:
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
                    data_list.append(('CAMUserPreferenceSharedLibraryLastUserActionLocation', str(val), context.get_relative_path(source_path)))

                elif key == 'CAMUserPreferenceExposureBiasByMode':
                    pathto = os.path.join(report_folder, 'CAMUserPreferenceExposureBiasByMode' + export_suffix + '.bplist')
                    with open(pathto, "wb") as wf:
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
                    data_list.append(('CAMUserPreferenceExposureBiasByMode', str(val), context.get_relative_path(source_path)))

                else:
                    data_list.append((key, str(val), context.get_relative_path(source_path)))

    data_headers = ('Property', 'Property Value', 'Source File')
    return data_headers, data_list, '\n'.join(files_found)
