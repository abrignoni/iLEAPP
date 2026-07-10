__artifacts_v2__ = {
    "safariRecentWebSearches": {
        "name": "Safari Browser - Recent Web Searches",
        "description": "Recent Safari web searches from com.apple.mobilesafari.plist",
        "author": "",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Safari Browser",
        "notes": "Search dates are stored as UTC in the plist.",
        "paths": ('**/Library/Preferences/com.apple.mobilesafari.plist',),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | com.apple.mobilesafari | 20 rows",
            "dexter_ios18": "iOS 18.3.2 | com.apple.mobilesafari | 2 rows",
            "felix_ios17": "iOS 17.6.1 | com.apple.mobilesafari | 2 rows",
            "fsfull002_ios17": "iOS 17.1 | com.apple.mobilesafari | 5 rows",
            "hc_ios18_7": "iOS 18.7.8 | com.apple.mobilesafari | 1 row",
            "iphone11_ios17": "iOS 17.3 | com.apple.mobilesafari | 1 row",
            "iphone12_ios18": "iOS 18.7 | com.apple.mobilesafari | 2 rows",
            "iphone14plus_ios18": "iOS 18.0 | com.apple.mobilesafari | 2 rows",
            "otto_ios17": "iOS 17.5.1 | com.apple.mobilesafari | 20 rows",
        }
    }
}

import plistlib
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, logfunc


@artifact_processor
def safariRecentWebSearches(context):
    data_headers = (('Date', 'datetime'), 'Search Term')
    data_list = []

    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('com.apple.mobilesafari.plist'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

    try:
        with open(source_path, 'rb') as fp:
            plist = plistlib.load(fp)
    except (plistlib.InvalidFileException, ValueError, OSError) as ex:
        logfunc(f'Failed to read plist {source_path}: {ex}')
        return data_headers, data_list, context.get_relative_path(source_path)

    for search in plist.get('RecentWebSearches', []):
        date = search.get('Date', '')
        if isinstance(date, datetime) and date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        data_list.append((date, search.get('SearchString', '')))

    return data_headers, data_list, context.get_relative_path(source_path)
