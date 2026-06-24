__artifacts_v2__ = {
    "icloudSharedOwnerInfo": {
        "name": "iCloud Shared Albums - Owner Info",
        "description": "iCloud shared album owner info (Info.plist)",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "iCloud Shared Albums", "notes": "",
        "paths": ('*/mobile/Media/PhotoData/PhotoCloudSharingData/*',),
        "output_types": "standard", "artifact_icon": "users"
    },
    "icloudSharedAlbumData": {
        "name": "iCloud Shared Albums - Album Data",
        "description": "iCloud shared album DCIM counters (DCIM_CLOUD.plist)",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "iCloud Shared Albums", "notes": "",
        "paths": ('*/mobile/Media/PhotoData/PhotoCloudSharingData/*',),
        "output_types": "standard", "artifact_icon": "image"
    },
    "icloudSharedPersonInfo": {
        "name": "iCloud Shared Albums - Person Info",
        "description": "iCloud shared album participants (cloudSharedPersonInfos.plist)",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "iCloud Shared Albums", "notes": "",
        "paths": ('*/mobile/Media/PhotoData/PhotoCloudSharingData/*',),
        "output_types": "standard", "artifact_icon": "user"
    },
    "icloudSharedEmails": {
        "name": "iCloud Shared Albums - Emails",
        "description": "iCloud shared album emails (cloudSharedEmails.plist)",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "iCloud Shared Albums", "notes": "",
        "paths": ('*/mobile/Media/PhotoData/PhotoCloudSharingData/*',),
        "output_types": "standard", "artifact_icon": "mail"
    }
}

import os
import plistlib

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def icloudSharedOwnerInfo(context):
    data_headers = ('Album Title', 'Album ID', 'Cloud Owner Email', 'Cloud Owner First Name',
                    'Cloud Owner Last Name', 'Cloud Public URL Enabled?',
                    ('Cloud Subscription Date', 'datetime'), 'Cloud Relationship State',
                    'Cloud Owner Hashed Person ID', 'File Location')
    data_list = []
    sources = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not os.path.isfile(file_found) or os.path.basename(file_found) != 'Info.plist':
            continue
        album_id = os.path.basename(os.path.dirname(file_found))
        with open(file_found, 'rb') as fp:
            pl = plistlib.load(fp)
        rel = context.get_relative_path(file_found)
        data_list.append((pl.get('title', ''), album_id, pl.get('cloudOwnerEmail', ''),
                          pl.get('cloudOwnerFirstName', ''), pl.get('cloudOwnerLastName', ''),
                          pl.get('cloudPublicURLEnabled', ''), pl.get('cloudSubscriptionDate', ''),
                          pl.get('cloudRelationshipState', ''),
                          pl.get('cloudOwnerHashedPersonID', ''), rel))
        sources.append(rel)
    return data_headers, data_list, ', '.join(dict.fromkeys(sources))


@artifact_processor
def icloudSharedAlbumData(context):
    data_headers = ('Album Name', 'DCIM Last Directory Number', 'DCIM Last File Number',
                    'File Location')
    data_list = []
    sources = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not os.path.isfile(file_found) or os.path.basename(file_found) != 'DCIM_CLOUD.plist':
            continue
        album_id = os.path.basename(os.path.dirname(file_found))
        with open(file_found, 'rb') as fp:
            pl = plistlib.load(fp)
        rel = context.get_relative_path(file_found)
        data_list.append((album_id, pl.get('DCIMLastDirectoryNumber', ''),
                          pl.get('DCIMLastFileNumber', ''), rel))
        sources.append(rel)
    return data_headers, data_list, ', '.join(dict.fromkeys(sources))


@artifact_processor
def icloudSharedPersonInfo(context):
    data_headers = ('Email', 'First Name', 'Last Name', 'Full Name', 'Identification')
    data_list = []
    sources = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not os.path.isfile(file_found) or os.path.basename(file_found) != 'cloudSharedPersonInfos.plist':
            continue
        with open(file_found, 'rb') as fp:
            pl = plistlib.load(fp)
        for identifier, info in pl.items():
            if not isinstance(info, dict):
                continue
            email = info.get('email', '')
            if info.get('emails'):
                email = info['emails'][0]
            data_list.append((email, info.get('firstName', ''), info.get('lastName', ''),
                              info.get('fullName', ''), identifier))
        sources.append(context.get_relative_path(file_found))
    return data_headers, data_list, ', '.join(dict.fromkeys(sources))


@artifact_processor
def icloudSharedEmails(context):
    data_headers = ('Key', 'Value')
    data_list = []
    sources = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not os.path.isfile(file_found) or os.path.basename(file_found) != 'cloudSharedEmails.plist':
            continue
        with open(file_found, 'rb') as fp:
            pl = plistlib.load(fp)
        for key, value in pl.items():
            data_list.append((key, value))
        sources.append(context.get_relative_path(file_found))
    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
