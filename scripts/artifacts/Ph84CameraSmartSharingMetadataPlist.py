# Author:  Scott Koenig https://theforensicscooter.com/
# Version: 1.0
#
#   Description:
#   Parses basic data from */PhotoData/Caches/SmartSharing/camera_smart_sharing_metadata.plist
#   which contains some important data related to iCloud Shared Photos Library
#   Smart Camera Settings and auto sharing. Additional information and
#   explanation of some keys-fields might be found with research and published blogs written by
#   Scott Koenig https://theforensicscooter.com/

import os
import plistlib
import biplist
import nska_deserialize as nd
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 


def get_ph84camerasmartsharingmetadataplist(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    file_found = str(files_found[0])
    if file_found.endswith('camera_smart_sharing_metadata.plist'):
        with open(file_found, 'rb') as f:
            try:
                deserialized_plist = nd.deserialize_plist(f)
                plist = deserialized_plist
                for key, value in plist.items():
                    if key == 'homeLocations':
                        homelocations = value
                    if key == 'creationDate':
                        creationdate = value
                    if key == 'frequentLocations':
                        frequentlocations = value
                    if key == 'identities':
                        identities = value
                    if key == 'locationShiftingRequired':
                        locationshiftingrequired = value
                    if key == 'version':
                        version = value
                    if key == 'libraryScopeLocalIdentifier':
                        libraryscopelocalidentifier = value

            except (nd.DeserializeError,
                    nd.biplist.NotBinaryPlistException,
                    nd.biplist.InvalidPlistException,
                    plistlib.InvalidFileException,
                    nd.ccl_bplist.BplistError,
                    ValueError,
                    TypeError, OSError, OverflowError) as ex:
                logfunc('Had exception: ' + str(ex))

        data_list.append((homelocations, creationdate, frequentlocations, identities, locationshiftingrequired,
                          version, libraryscopelocalidentifier))

        description = ('Parses basic data from */PhotoData/Caches/SmartSharing/camera_smart_sharing_metadata.plist'
                       ' which contains some important data related to iCloud Shared Photos Library Smart'
                       ' Camera Settings and auto sharing.')
        report = ArtifactHtmlReport('Photos-Z-Settings')
        report.start_artifact_report(report_folder, 'Ph84-Camera-Smart-Sharing-Metadata-Plist', description)
        report.add_script()
        data_headers = ('homeLocations', 'creationDate', 'frequentLocations', 'identities', 'locationShiftingRequired',
                        'version', 'libraryScopeLocalIdentifier')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'Ph84-Camera-Smart-Sharing-Metadata-Plist'
        tsv(report_folder, data_headers, data_list, tsvname)


__artifacts_v2__ = {
    'Ph84-Camera-Smart-Sharing-Metadata-Plist': {
        'name': 'Camera Smart Sharing Settings Ph84 Camera Smart Sharing Metadata Plist',
        'description': 'Parses basic data from */PhotoData/Caches/SmartSharing/camera_smart_sharing_metadata.plist'
                       ' which contains some important data related to iCloud Shared Photos Library'
                       ' Smart Camera Settings and auto sharing. Additional information and'
                       ' explanation of some keys-fields might be found with research and published blogs written by'
                       ' Scott Koenig https://theforensicscooter.com/',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.0',
        'date': '2024-06-8',
        'requirements': 'Acquisition that contains camera_smart_sharing_metadata.plist',
        'category': 'Photos-Z-Settings',
        'notes': '',
        'paths': '*/PhotoData/Caches/SmartSharing/camera_smart_sharing_metadata.plist',
        'function': 'get_ph84camerasmartsharingmetadataplist'
    }
}
