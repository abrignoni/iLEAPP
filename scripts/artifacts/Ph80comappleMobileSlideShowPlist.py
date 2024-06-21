# Author:  Scott Koenig, assisted by past contributors
# Version: 1.0
#
#   Description:
#   Parses basic data from com.apple.mobileslideshow.plist which contains some important data related to the Apple
#   Photos Application. Additional information and explanation of some keys-fields might be found with
#   research and published blogs written by Scott Koenig https://theforensicscooter.com/

import datetime
import os
import plistlib
import nska_deserialize as nd
import scripts.artifacts.artGlobals
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows


def get_ph80comapplemobileslideshowplist(files_found, report_folder, seeker, wrap_text, time_offset):
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            if key == 'downloadAndKeepOriginals':
                data_list.append(('downloadAndKeepOriginals', val))
                logdevinfo(f"<b>comapplemobileslideshowplist-downloadAndKeepOriginals: </b>{val}")

            elif key == 'PhotosSharedLibrarySyncingIsActive':
                data_list.append(('PhotosSharedLibrarySyncingIsActive', val))
                logdevinfo(f"<b>comapplemobileslideshowplist-PhotosSharedLibrarySyncingIsActive: </b>{val}")

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
                data_list.append(('TipKitEligibleContents-com.apple.mobileslideshow.one-up-photo', val))

            else:
                data_list.append((key, val))

    if len(data_list) > 0:
        description = ('Parses data from com.apple.mobileslideshow.plist which contains some important data'
                       ' related to the Apple Photos Application. Additional information and explanation of some'
                       ' keys-fields might be found with research and published blogs written by'
                       ' Scott Koenig https://theforensicscooter.com/')
        report = ArtifactHtmlReport('Ph80-Com-Apple-MobileSlideshow-Plist')
        report.start_artifact_report(report_folder, 'Ph80-Com-Apple-MobileSlideshow-Plist', description)
        report.add_script()
        data_headers = ('Key', 'Values')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'Ph80-Com-Apple-MobileSlideshow-Plist'
        tsv(report_folder, data_headers, data_list, tsvname)


__artifacts_v2__ = {
    'Ph80-Com-Apple-MobileSlideshow-Plist': {
        'name': 'Photos App Settings Ph80 com.apple.mobileslideshow-plist',
        'description': 'Parses basic data from com.apple.mobileslideshow.plist which contains some important'
                       ' data related to the Apple Photos Application. Additional information and explanation of some'
                       ' keys-fields might be found with research and published blogs written by'
                       ' Scott Koenig https://theforensicscooter.com/',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.0',
        'date': '2024-06-8',
        'requirements': 'Acquisition that contains com.apple.mobileslideshow.plist',
        'category': 'Photos-Z-Settings',
        'notes': '',
        'paths': '*/Library/Preferences/com.apple.mobileslideshow.plist',
        'function': 'get_ph80comapplemobileslideshowplist'
    }
}
