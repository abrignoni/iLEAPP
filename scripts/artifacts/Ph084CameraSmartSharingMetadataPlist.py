# pylint: disable=E0606,W0611,W0613
__artifacts_v2__ = {
    'Ph084CameraSmartSharingMetadataPlist': {
        'name': 'Ph084-Camera-Smart-Sharing-Metadata-Plist',
        'description': 'Parses basic data from */PhotoData/Caches/SmartSharing/camera_smart_sharing_metadata.plist'
                       ' which contains some important data related to iCloud Shared Photos Library'
                       ' Smart Camera Settings and auto sharing. Additional information and explanation of some'
                       ' keys-fields might be found with research and published blogs written by Scott Koenig'
                       ' https://theforensicscooter.com/2024/05/18/ileapp-parsers-photos-sqlite-queries/',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains camera_smart_sharing_metadata.plist',
        'category': 'Photos.sqlite-Y-Settings-Plist-Camera-Smart-Share',
        'notes': '',
        'paths': ('*/PhotoData/Caches/SmartSharing/camera_smart_sharing_metadata.plist',),
        "output_types": ["standard", "tsv", "none"],
        "artifact_icon": "camera",
        'sample_data': {
            'dexter_ios18': 'iOS 18.3.2 | 1 row',
        }
    }
}

import datetime
import os
import plistlib
import nska_deserialize as nd
from scripts.ilapfuncs import artifact_processor, logfunc, device_info, get_file_path

@artifact_processor
def Ph084CameraSmartSharingMetadataPlist(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    source_path = str(files_found[0])

    if source_path.endswith('camera_smart_sharing_metadata.plist'):
        with open(source_path, 'rb') as f:
            try:
                deserialized_plist = nd.deserialize_plist(f)
                plist = deserialized_plist
                for key, val in plist.items():
                    if key == 'creationDate':
                        creationdate = val
                    if key == 'homeLocations':
                        homelocations = val
                    if key == 'frequentLocations':
                        frequentlocations = val
                    if key == 'identities':
                        identities = val
                    if key == 'locationShiftingRequired':
                        locationshiftingrequired = val
                    if key == 'version':
                        version = val
                    if key == 'libraryScopeLocalIdentifier':
                        libraryscopelocalidentifier = val

            except (nd.DeserializeError,
                    nd.biplist.NotBinaryPlistException,
                    nd.biplist.InvalidPlistException,
                    plistlib.InvalidFileException,
                    nd.ccl_bplist.BplistError,
                    ValueError,
                    TypeError, OSError, OverflowError) as ex:
                logfunc('Had exception: ' + str(ex))

        data_list.append((creationdate, homelocations, frequentlocations, identities, locationshiftingrequired,
                          version, libraryscopelocalidentifier))

    data_headers = (
        ('creationdate', 'datetime'),
        'homelocations',
        'frequentlocations',
        'identities',
        'locationshiftingrequired',
        'version',
        'libraryscopelocalidentifier')
    return data_headers, data_list, source_path


