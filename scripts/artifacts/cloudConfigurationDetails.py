__artifacts_v2__ = {
    "cloud_configuration_details": {
        "name": "Cloud Configuration Details",
        "description": "Top-level keys and values of CloudConfigurationDetails.plist and "
                       "CloudConfigurationSetAsideDetails.plist in the configurationprofiles system group "
                       "container. Byte strings are shown by size and SHA-256.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Configuration Profiles",
        "notes": "One row per top-level key of CloudConfigurationDetails.plist and "
                 "CloudConfigurationSetAsideDetails.plist under Library/ConfigurationProfiles in the "
                 "systemgroup.com.apple.configurationprofiles Shared/SystemGroup container (iTunes backups"
                 " map SysSharedContainerDomain- to the same path, scripts/search_files.py; not exercised "
                 "on a backup here, and whether a backup includes these files is not established). "
                 "Booleans and integers are shown as text. A list of byte strings gives one row per item, "
                 "with the item's index in Key. Byte strings are shown by a label, size and SHA-256, not "
                 "their bytes; the label is 'bytes starting 30 82' when they start with those two bytes, "
                 "which is not a certificate parse. Other lists and dictionaries are shown as JSON. "
                 "Apple's device-management schemas (github.com/apple/device-management at commit 9e7fdbe,"
                 " searched 2026-11-16) name IsSupervised only as a key of the MDM DeviceInformation "
                 "query, and ConfigurationSource only as a string key of the Education profile payload. "
                 "They do not name the other keys seen here or either file. No key's meaning in this file "
                 "is established by that source, and none is interpreted. On the 22 images in sample_data "
                 "(iOS 12.4 to 26.5.2, 114 rows) every image held CloudConfigurationDetails.plist. "
                 "IsSupervised was False and ConfigurationSource 0 on all 20 that carry them, AllowPairing"
                 " True on 20, CloudConfigurationUIComplete True on 22, PostSetupProfileWasInstalled True "
                 "on 8 and False on 13, ConfigurationWasApplied True on 7, and SupervisorHostCertificates "
                 "held one item starting 30 82 on fsfull002_ios17 and on hc_ios17_2. No image in "
                 "sample_data held IsSupervised True; whether any of them was supervised or enrolled in "
                 "device management is not established. File held CloudConfigurationDetails.plist on every"
                 " row of 21 images; hc_ios18_7 also held CloudConfigurationSetAsideDetails.plist "
                 "(CloudConfigurationUIComplete and ConfigurationWasApplied, both False), which is why the"
                 " column is kept. Installed profiles are in Configuration Profiles.",
        "paths": (
            '*/systemgroup.com.apple.configurationprofiles/Library/ConfigurationProfiles/CloudConfigurationDetails.plist',
            '*/systemgroup.com.apple.configurationprofiles/Library/ConfigurationProfiles/CloudConfigurationSetAsideDetails.plist',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 5 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 5 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 5 rows",
            "ctf2020_ios12": "iOS 12.4 | 5 rows",
            "dexter_ios18": "iOS 18.3.2 | 5 rows",
            "felix23_ios16": "iOS 16.5 | 6 rows",
            "felix_ios17": "iOS 17.6.1 | 6 rows",
            "fsfull002_ios17": "iOS 17.1 | 4 rows",
            "hc_ios17_2": "iOS 17.2.1 | 7 rows",
            "hc_ios18_7": "iOS 18.7.8 | 3 rows",
            "hc_ios26": "iOS 26.5.2 | 5 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 5 rows",
            "hickman_ios13": "iOS 13.3.1 | 5 rows",
            "hickman_ios14": "iOS 14.3 | 5 rows",
            "hickman_ios15": "iOS 15.3.1 | 5 rows",
            "iphone11_ios17": "iOS 17.3 | 6 rows",
            "iphone12_ios18": "iOS 18.7 | 5 rows",
            "iphone14plus_ios18": "iOS 18.0 | 5 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 6 rows",
            "jess_ios15": "iOS 15.0.2 | 5 rows",
            "magnet_ios16": "iOS 16.1.1 | 6 rows",
            "otto_ios17": "iOS 17.5.1 | 5 rows",
        },
    },
}

import datetime
import hashlib
import json
import os
import plistlib
from xml.parsers.expat import ExpatError

from scripts.ilapfuncs import artifact_processor, logfunc

_PLIST_ERRORS = (plistlib.InvalidFileException, ExpatError, ValueError, TypeError, OverflowError, OSError)


def _bytes_text(value):
    kind = 'bytes starting 30 82' if value[:2] == b'\x30\x82' else 'bytes'
    return f'{kind}, {len(value)} bytes, SHA-256 {hashlib.sha256(value).hexdigest()}'


def _plain(value):
    if isinstance(value, bytes):
        return _bytes_text(value)
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_plain(v) for v in value]
    return value


def _value_rows(key, value):
    """One (key, value text) per value; a list of byte strings gives one row per item."""
    if isinstance(value, list) and value and all(isinstance(v, bytes) for v in value):
        return [(f'{key} [{index}]', _bytes_text(item)) for index, item in enumerate(value)]
    if isinstance(value, bytes):
        return [(key, _bytes_text(value))]
    if isinstance(value, (dict, list)):
        return [(key, json.dumps(_plain(value), sort_keys=True))]
    return [(key, str(value))]


@artifact_processor
def cloud_configuration_details(context):
    data_list = []
    source_paths = []
    for path in sorted(str(f) for f in context.get_files_found() if not os.path.isdir(str(f))):
        source_paths.append(path)
        try:
            with open(path, 'rb') as handle:
                plist = plistlib.load(handle)
        except _PLIST_ERRORS as error:
            logfunc(f'Cloud Configuration Details: could not read {os.path.basename(path)}: {error}')
            continue
        if not isinstance(plist, dict):
            continue
        name = os.path.basename(path)
        for key in sorted(plist):
            for shown_key, text in _value_rows(str(key), plist[key]):
                data_list.append((name, shown_key, text))

    data_headers = ('File', 'Key', 'Value')
    return data_headers, data_list, '\n'.join(source_paths)
