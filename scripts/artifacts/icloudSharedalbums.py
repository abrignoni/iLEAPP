__artifacts_v2__ = {
    "icloudSharedOwnerInfo": {
        "name": "iCloud Shared Albums - Owner Info",
        "description": "iCloud shared album owner info (Info.plist)",
        "author": "@abrignoni", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "iCloud Shared Albums", "notes": "",
        "paths": ('*/mobile/Media/PhotoData/PhotoCloudSharingData/*',),
        "output_types": "standard", "artifact_icon": "users",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1 row",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 5 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 1 row",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "icloudSharedAlbumData": {
        "name": "iCloud Shared Albums - Album Data",
        "description": "iCloud shared album DCIM counters (DCIM_CLOUD.plist)",
        "author": "@abrignoni", "creation_date": "2026-06-23", "last_update_date": "2026-07-31", "requirements": "none",
        "category": "iCloud Shared Albums", "notes": "",
        "paths": ('*/mobile/Media/PhotoData/PhotoCloudSharingData/*',),
        "output_types": "standard", "artifact_icon": "photo",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 4 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 1 row",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "icloudSharedPersonInfo": {
        "name": "iCloud Shared Albums - Person Info",
        "description": "Person records held in cloudSharedPersonInfos.plist of the iCloud shared album data (first email address display and stored email fields)",
        "author": "@abrignoni, @AlexisBrignoni, Codex", "creation_date": "2026-06-23", "last_update_date": "2026-10-06", "requirements": "none",
        "category": "iCloud Shared Albums", "notes": "Email keeps the existing first-entry display: a truthy emails field supplies its "
                 "first indexed value; otherwise the scalar email field is used. Emails Field "
                 "and Email Field contain compact typed JSON of the corresponding plistlib-decoded "
                 "fields, including key presence, value types, array order and repeated values. "
                 "Integer and UID values use decimal text; real values use their parsed binary64 "
                 "bits in big-endian hexadecimal; data uses base64; dates keep decoded components "
                 "without assigning a timezone. Dictionaries use ordered typed key/value pairs. "
                 "These fields preserve supported decoded values, not original plist bytes, XML "
                 "spelling, binary object identities or duplicate dictionary keys already collapsed "
                 "by decoding. Original source files remain the byte evidence. Existing malformed "
                 "shape handling and first-entry selection are unchanged. Multiple files can "
                 "contribute rows; the source union does not associate each row with its file. "
                 "Stored addresses do not establish ownership or current validity. On ctf2020_ios12, "
                 "Email, First Name and Last Name are empty on its one row because the "
                 "corresponding keys are absent. On iphone11_ios17, 14 records have a "
                 "one-string emails array and seven have only scalar email; none has both "
                 "keys. Multiple-address arrays and other native types were exercised only "
                 "on constructed XML or binary plists.",
        "paths": ('*/mobile/Media/PhotoData/PhotoCloudSharingData/*',),
        "output_types": "standard", "artifact_icon": "user",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1 row",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 21 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 1 row",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 4 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "icloudSharedEmails": {
        "name": "iCloud Shared Albums - Emails",
        "description": "iCloud shared album emails (cloudSharedEmails.plist)",
        "author": "@abrignoni", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "iCloud Shared Albums", "notes": "",
        "paths": ('*/mobile/Media/PhotoData/PhotoCloudSharingData/*',),
        "output_types": "standard", "artifact_icon": "mail",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 3 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    }
}

import base64
from datetime import datetime
import json
import os
import plistlib
import struct

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
    data_headers = ('Album ID', 'DCIM Last Directory Number', 'DCIM Last File Number',
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


def _person_value_node(value):
    """Encode a supported plistlib-decoded value without tag collisions."""
    if value is None:
        kind, encoded = 'null', None
    elif isinstance(value, bool):
        kind, encoded = 'bool', value
    elif isinstance(value, str):
        kind, encoded = 'string', value
    elif isinstance(value, int):
        kind, encoded = 'integer', str(value)
    elif isinstance(value, float):
        kind, encoded = 'real', struct.pack('>d', value).hex()
    elif isinstance(value, bytes):
        kind, encoded = 'data', base64.b64encode(value).decode('ascii')
    elif isinstance(value, datetime):
        kind, encoded = 'date', value.isoformat()
    elif isinstance(value, plistlib.UID):
        kind, encoded = 'uid', str(value.data)
    elif isinstance(value, list):
        kind, encoded = 'array', [_person_value_node(item) for item in value]
    elif isinstance(value, dict):
        kind = 'dictionary'
        encoded = [[_person_value_node(key), _person_value_node(item)]
                   for key, item in value.items()]
    else:
        raise TypeError(f'Unsupported person field value type: {type(value).__name__}')
    return {'type': kind, 'value': encoded}


def _person_field_json(info, key):
    """Keep missing keys distinct from present null or empty decoded values."""
    envelope = {'present': key in info}
    if key in info:
        envelope['value'] = _person_value_node(info[key])
    return json.dumps(envelope, ensure_ascii=True, separators=(',', ':'), allow_nan=False)


@artifact_processor
def icloudSharedPersonInfo(context):
    data_headers = ('Email', 'First Name', 'Last Name', 'Full Name', 'Identification',
                    'Emails Field (Typed JSON)', 'Email Field (Typed JSON)')
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
                              info.get('fullName', ''), identifier,
                              _person_field_json(info, 'emails'), _person_field_json(info, 'email')))
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
