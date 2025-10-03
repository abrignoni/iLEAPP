__artifacts_v2__ = {
    "user_defaults": {
        "name": "Application User Defaults",
        "description": "Extracts the user defaults Plist file for each application",
        "author": "@jfhyla",
        "version": "0.1",
        "date": "2025-07-28",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "https://developer.apple.com/documentation/foundation/userdefaults",
        "paths": ('*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
                  '*/mobile/Containers/Data/Application/*/Preferences/*.plist'),
        "output_types": ["html", "tsv", "lava"]
    }
}

import biplist
import pathlib
import plistlib
from plistlib import InvalidFileException
import sys
import datetime
from ileapp.scripts.ilapfuncs import artifact_processor

@artifact_processor
def user_defaults(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    apps = {}
    found_apps = []
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('mobile_container_manager.metadata.plist'):
            continue
        with open(file_found, "rb") as fp:
            if sys.version_info >= (3, 9):
                plist = plistlib.load(fp)
            else:
                plist = biplist.readPlist(fp)
            bundleid = plist['MCMMetadataIdentifier']
            p = pathlib.Path(file_found)
            appgroupid = p.parent.name
            apps[appgroupid] = bundleid

    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('mobile_container_manager.metadata.plist'):
            continue
        for guid, bundleid in apps.items():
            if f'{bundleid}.plist' in file_found and guid in file_found:
                found_apps.append(guid)
                with open(file_found, "rb") as fp:
                    if sys.version_info >= (3, 9):
                        try:
                            plist = plistlib.load(fp)
                        except InvalidFileException as e:
                            plist = 'INVALID FILE'
                    else:
                        plist = biplist.readPlist(fp)
                    for (key,item) in plist.items():

                        data_list.append((bundleid, guid, key, clean_data(item), file_found))

    if len(data_list) > 0:
        
        filelocdesc = 'Path column in the report'

        data_headers = ('Application BundleID', 'Application GUID', 'Key', 'Item', 'Path')
        return data_headers, data_list, filelocdesc


def clean_data(obj):
    if isinstance(obj, dict):
        return {key: clean_data(val) for key, val in obj.items()}
    elif isinstance(obj, list):
        return [clean_data(item) for item in obj]
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, bytes):
        return str(obj)
    else:
        return obj