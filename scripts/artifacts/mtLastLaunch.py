__artifacts_v2__ = {
    "mtLastLaunch": {
        "name": "mt.lastLaunch App Dates",
        "description": "The per-app dates in com.apple.mt.lastLaunch.plist and the apps listed in "
                       "com.apple.mt.killed.plist",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-01",
        "last_update_date": "2026-11-01",
        "requirements": "none",
        "category": "App Usage",
        "notes": ('Read from com.apple.mt.lastLaunch.plist (its launches dictionary, bundle ID to date) and '
                  'com.apple.mt.killed.plist (its killed array of bundle IDs) in Library/Preferences. One row per '
                  'bundle ID in either file; In Last Launch List and In Killed List say which. Date is the launches '
                  'value, a plist date shown in UTC, blank for the 108 rows from the killed list alone. What the '
                  'date marks was established only for iOS 12. Source-verified on iOS 12 only (dasd on '
                  'ctf2020_ios12): the writer is _DASBARScheduler, the Background App Refresh scheduler, which sets '
                  'a date only for apps in its background-fetch set, with the current date when the app comes to '
                  'the foreground and from its background-fetch scheduling path; on uninstall the same call runs '
                  'with no date, read as removing the entry. On that image the 25 dated apps that had KnowledgeC '
                  'app-in-focus records were all dated at or after their latest focus start, 13 within 5 seconds of '
                  'one. In the same code the killed list holds apps whose BackBoard exit reason was 1 (no name for '
                  'that reason was found), and an app leaves it when it comes to the foreground; it stores no time. '
                  'iOS 13 to 15 were not examined. On iOS 16 and later the writer was not located: dasd there is '
                  'about 70 KB (650 KB on iOS 12), and a string search of the iOS 18.7 shared cache '
                  "(iphone12_ios18) found none of the scheduler's strings. Against Biome App.InFocus on 8 images "
                  'with iOS 16 or later, 32 dated apps had a foreground record for the same app: 19 fell within 5 '
                  "seconds of a foreground event and 10 were earlier than the app's latest foreground, so on those "
                  "versions do not read the date as the app's last use or last launch. The background-fetch set "
                  'could not be checked on those images. An app with no date is not evidence it was never opened: '
                  'on iOS 12 only apps in the background-fetch set get one. hexordia_ios1651 held an empty launches '
                  'dictionary. The tested iTunes backup gave the same 25 bundle IDs and flags as the full file '
                  'system of the same device; one date differed between the two captures.'),
        "paths": ('*/Library/Preferences/com.apple.mt.lastLaunch.plist',
                  '*/Library/Preferences/com.apple.mt.killed.plist'),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 36 rows",
            "hickman_ios14": "iOS 14.3 | 25 rows",
            "hickman_ios14_itunes_backup_decrypted": "iOS 14.3 | 25 rows",
            "dexter_ios18": "iOS 18.3.2 | 24 rows",
            "hickman_ios13": "iOS 13.3.1 | 22 rows",
            "hc_ios26": "iOS 26.5.2 | 21 rows",
            "hickman_ios15": "iOS 15.3.1 | 19 rows",
            "iphone11_ios17": "iOS 17.3 | 19 rows",
            "hc_ios17_2": "iOS 17.2.1 | 18 rows",
            "magnet_ios16": "iOS 16.1.1 | 18 rows",
            "abe_ios16": "iOS 16.5 | 17 rows",
            "otto_ios17": "iOS 17.5.1 | 15 rows",
            "iphone12_ios18": "iOS 18.7 | 13 rows",
            "belkactf6_tar": "iOS 16.3 | 11 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 11 rows",
            "hc_ios18_7": "iOS 18.7.8 | 10 rows",
            "felix_ios17": "iOS 17.6.1 | 8 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 2 rows",
        },
    }
}

import os
import plistlib
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, logfunc

LAUNCHES = 'com.apple.mt.lastLaunch.plist'
KILLED = 'com.apple.mt.killed.plist'


def _load(path):
    try:
        with open(path, 'rb') as fp:
            return plistlib.load(fp)
    except (OSError, plistlib.InvalidFileException, ValueError) as error:
        logfunc(f'mt.lastLaunch App Dates: could not read {os.path.basename(path)}: {error}')
        return None


@artifact_processor
def mtLastLaunch(context):
    data_headers = (('Date', 'datetime'), 'Bundle ID', 'In Last Launch List',
                    'In Killed List')
    # Preferences folder -> {file name: path}, so two extraction roots in one input never merge
    folders = {}
    for file_found in sorted(str(f) for f in context.get_files_found()):
        name = os.path.basename(file_found)
        if name in (LAUNCHES, KILLED) and os.path.isfile(file_found):
            folders.setdefault(os.path.dirname(file_found), {})[name] = file_found

    data_list = []
    sources = []
    for _, files in sorted(folders.items()):
        launches_store = None
        if LAUNCHES in files:
            launches_store = _load(files[LAUNCHES])
            sources.append(files[LAUNCHES])
        killed = set()
        if KILLED in files:
            killed_store = _load(files[KILLED])
            sources.append(files[KILLED])
            if isinstance(killed_store, dict) and isinstance(killed_store.get('killed'), list):
                killed = {str(b) for b in killed_store['killed']}
        launches = launches_store.get('launches') if isinstance(launches_store, dict) else None
        if not isinstance(launches, dict):
            launches = {}
        launches = {str(k): v for k, v in launches.items()}
        # dated apps first, then the killed list's apps that carry no date
        for bundle_id in sorted(launches) + sorted(killed - set(launches)):
            date = launches.get(bundle_id)
            timestamp = date.replace(tzinfo=timezone.utc) if isinstance(date, datetime) else ''
            data_list.append((timestamp, bundle_id, 'Yes' if bundle_id in launches else 'No',
                              'Yes' if bundle_id in killed else 'No'))

    return data_headers, data_list, '\n'.join(sources)
