# pylint: disable=W0611,W0613
__artifacts_v2__ = {
    'Ph80ComAppleMobileSlideshowPlist': {
        'name': 'Ph80-Com-Apple-MobileSlideshow-Plist',
        'description': 'Parses basic data from com.apple.mobileslideshow.plist which contains some important'
                       ' data related to the Apple Photos Application. Additional information and explanation of some'
                       ' keys-fields might be found with research and published blogs written by'
                       ' Scott Koenig https://theforensicscooter.com/',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains com.apple.mobileslideshow.plist',
        'category': 'Photos-Z-Settings',
        'notes': '',
        'paths': ('*/Library/Preferences/com.apple.mobileslideshow.plist',),
        "output_types": ["standard", "tsv", "none"],
        "artifact_icon": "settings",
        'sample_data': {
            'ctf2020_ios12': 'iOS 12.4 | 23 rows',
            'dexter_ios18': 'iOS 18.3.2 | 64 rows',
            'felix_ios17': 'iOS 17.6.1 | 26 rows',
            'fsfull002_ios17': 'iOS 17.1 | 8 rows',
            'hc_ios18_7': 'iOS 18.7.8 | 6 rows',
            'iphone11_ios17': 'iOS 17.3 | 19 rows',
            'iphone12_ios18': 'iOS 18.7 | 35 rows',
            'iphone14plus_ios18': 'iOS 18.0 | 5 rows',
            'otto_ios17': 'iOS 17.5.1 | 26 rows',
        }
    }
}

import datetime
import os
import plistlib
import nska_deserialize as nd
from scripts.ilapfuncs import artifact_processor, logfunc, device_info, get_file_path

@artifact_processor
def Ph80ComAppleMobileSlideshowPlist(files_found, report_folder, seeker, wrap_text, time_offset):
    data_list = []
    source_path = str(files_found[0])

    with open(source_path, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():

            if key == 'downloadAndKeepOriginals':
                logfunc(f"downloadAndKeepOriginals: {val}")
                device_info("com.apple.mobileslideshow.plist", "downloadAndKeepOriginals", str(val), source_path)

            elif key == 'PhotosSharedLibrarySyncingIsActive':
                logfunc(f"PhotosSharedLibrarySyncingIsActive: {val}")
                device_info("com.apple.mobileslideshow.plist", "PhotosSharedLibrarySyncingIsActive", str(val), source_path)

            elif key == 'TipKitEligibleContents-com.apple.mobileslideshow.one-up-photo':
                pathto = os.path.join(report_folder, 'TipKitEligibleContents-com.apple.mobileslideshow.one-up-photo' + '.bplist')
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
                data_list.append(('TipKitEligibleContents-com.apple.mobileslideshow.one-up-photo', str(val)))

            else:
                data_list.append((key, str(val)))

    data_headers = ('Property','Property Value')
    return data_headers, data_list, source_path
