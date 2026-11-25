"""Google Maps for iOS recent searches from the LocalSuggestions archive in the app's container."""

__artifacts_v2__ = {
    "googleMapsRecentSearches": {
        "name": "Google Maps - Recent Searches",
        "description": "Entries of the kRecentSearches list in Google Maps' LocalSuggestions archive: the stored query and "
                       "timestamp, the secondaryInfo text and the placemark's single-line address, and the placemark's "
                       "coordinates.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-24",
        "last_update_date": "2026-11-24",
        "requirements": "none",
        "category": "Locations & Maps",
        "notes": "Reads the LocalSuggestions file in the Library/Application Support folder of a container whose own "
                 ".com.apple.mobile_container_manager.metadata.plist names com.google.Maps; a LocalSuggestions file in"
                 " any other container is not read. The file is an NSKeyedArchiver archive, and one row is reported "
                 "per AZClientSideSuggestionItem in the array stored under its kRecentSearches key, in stored order. "
                 "List Position counts the reported items in that order, 1 first. It is not the placemark's own "
                 "listPosition field, which held a different value on all 35 placemarks and is not shown. "
                 "kRecentSearches and AZClientSideSuggestionItem are the names the archive itself uses; the rows were "
                 "not compared with what the app shows. On the 12 tested images the array held 0 to 7 items (43 in "
                 "all, on 9 images), and every array member was an AZClientSideSuggestionItem. The files on hc_ios18_7"
                 " and hc_ios26 are byte-identical, so their one item is counted twice in these figures. On the 7 "
                 "images with more than one item the timestamps were in descending order, so List Position 1 held the "
                 "latest timestamp. Timestamp is the item's timestamp, a 13-digit integer read as Unix milliseconds in"
                 " UTC. No source for the unit was found. Read that way, the latest timestamp was earlier than the "
                 "archive file's modified time on all 9 images with items: by 8 to 171 seconds on abe_ios16, "
                 "dexter_ios18, hill_iphone15pro_ios26, otto_ios17 and wilkerson_iphone16_ios26, by about 25 minutes "
                 "on hc_ios17_2, by about 1.8 days on iphone11_ios17 and by about 3.4 days on hc_ios18_7 and hc_ios26."
                 " The modified time used is the UTC extended timestamp each extraction zip records for the file. What"
                 " event the timestamp marks is not established. Query is the item's query field; its title field held"
                 " the same text on all 43 items and is not shown. Secondary Info is secondaryInfo, and Address is the"
                 " singleLineAddress of the item's placemark. Secondary Info and Address are equal on all 24 rows "
                 "where both are set, and each is set on 2 rows where the other is empty, so both are kept. Latitude "
                 "and Longitude are the placemark's _coordinateLat and _coordinateLong. 35 of the 43 items have a "
                 "placemark, and the 8 without one have no Address, Latitude or Longitude. The coordinates are stored "
                 "with the item's placemark. Whether any of them is a position of the device is not established, so "
                 "they should not be read as device positions. Not read: the archive's kEnabledKey value, the item's "
                 "transitLine and transitStation values, the GPBData blobs of historyItemProto and of the placemark's "
                 "place identifiers, the placemark's other fields, and the PlacesheetVisits and FrequentTripsData "
                 "archives beside this file. On the 12 tested images PlacesheetVisits held, under a 21-digit string "
                 "key, 19 or 20 digit integer keys, each with a 13-digit lastVisited integer and an "
                 "entrypointDismissed flag (18 entries on 5 images). What the integer keys identify is not "
                 "established. They were not found in the LocalSuggestions file of the same image as decimal or "
                 "hexadecimal text or as 64-bit or varint bytes, so this module does not tie those entries to a place."
                 " FrequentTripsData held an empty dictionary on all 12 images.",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 7 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 4 rows",
            "hc_ios17_2": "iOS 17.2.1 | 2 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "hc_ios26": "iOS 26.5.2 | 1 row",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 7 rows",
            "iphone11_ios17": "iOS 17.3 | 7 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 7 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 7 rows",
        },
        "paths": (
            '*/mobile/Containers/Data/Application/*/Library/Application Support/LocalSuggestions',
            '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
        ),
        "output_types": "all",
        "artifact_icon": "search",
    },
}

import os
import plistlib

from scripts.artifacts.googleMaps import _container_app, _container_owners, _unix_ms_to_utc
from scripts.ilapfuncs import artifact_processor, logfunc

_BUNDLE = 'com.google.Maps'


def _res(objects, value):
    if isinstance(value, plistlib.UID) and value.data < len(objects):
        return objects[value.data]
    return value


def _class_name(objects, obj):
    cls = obj.get('$class') if isinstance(obj, dict) else None
    target = _res(objects, cls)
    return target.get('$classname') if isinstance(target, dict) else None


def _text(objects, value):
    value = _res(objects, value)
    if isinstance(value, dict):
        value = value.get('NS.string')
    return value if isinstance(value, str) and value != '$null' else ''


def _coordinate(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else ''


def _entries(path):
    """The kRecentSearches items in stored order, or None when the file is not that archive."""
    try:
        with open(path, 'rb') as handle:
            archive = plistlib.load(handle)
    except (plistlib.InvalidFileException, ValueError, OSError) as ex:
        logfunc(f'Google Maps - Recent Searches: could not read {os.path.basename(path)}: {ex}')
        return None
    if not isinstance(archive, dict) or not isinstance(archive.get('$objects'), list):
        return None
    objects = archive['$objects']
    top = archive.get('$top')
    root = _res(objects, top.get('kRecentSearches')) if isinstance(top, dict) else None
    if not isinstance(root, dict):
        return None
    members = root.get('NS.objects', [])
    if not isinstance(members, list):
        logfunc(f'Google Maps - Recent Searches: {os.path.basename(path)} holds no kRecentSearches list; skipped')
        return None
    items = []
    for ref in members:
        item = _res(objects, ref)
        if _class_name(objects, item) == 'AZClientSideSuggestionItem':
            items.append((objects, item))
    return items


@artifact_processor
def googleMapsRecentSearches(context):
    owners = _container_owners(context)
    data_list = []
    sources = []
    for path in context.get_files_found():
        path = str(path)
        if os.path.basename(path) != 'LocalSuggestions' or os.path.isdir(path):
            continue
        if _container_app(path, owners) != _BUNDLE:
            continue  # the folder name is not the app's; only a Google Maps container counts
        entries = _entries(path)
        if entries is None:
            continue
        sources.append(path)
        for position, (objects, item) in enumerate(entries, 1):
            placemark = _res(objects, item.get('placemark'))
            if not isinstance(placemark, dict):
                placemark = {}
            data_list.append((
                _unix_ms_to_utc(_res(objects, item.get('timestamp'))),
                _text(objects, item.get('query')),
                _text(objects, item.get('secondaryInfo')),
                _text(objects, placemark.get('singleLineAddress')),
                _coordinate(placemark.get('_coordinateLat')),
                _coordinate(placemark.get('_coordinateLong')),
                position,
            ))

    data_headers = (('Timestamp', 'datetime'), 'Query', 'Secondary Info', 'Address', ('Latitude', 'latitude'),
                    ('Longitude', 'longitude'), ('List Position', 'number'))
    return data_headers, data_list, '\n'.join(sources)
