""" Music app search keys in com.apple.Music.plist """
__artifacts_v2__ = {
    "appleMusicRecentlySearched": {
        "name": "Apple Music Recently Searched",
        "description": "One row per entry under RecentlySearched in com.apple.Music.plist, with "
                       "its stored date number, kind and the identifiers archived for it.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-10",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "Apple Music",
        "notes": "Each key under RecentlySearched (Source) holds a JSON array, and each row is "
                 "one item of it, with Position its 1-based place in that array. Date Added "
                 "Number is the item's dateAdded as stored. Date Added is that number read as "
                 "seconds since 2001-01-01 UTC, shown to the second. The epoch is not sourced: "
                 "it is used because the 4 values on the sample_data images then fall in 2021 "
                 "(hickman_ios14) and 2025 (dexter_ios18), and read from 1970 they fall in 1990 "
                 "and 1994. Kind is the item's kind as stored; artists, albums and playlists "
                 "were seen. The item's identifiers value is a base64 NSKeyedArchiver archive of "
                 "an identifier set. Model Class is the modelClass under "
                 "MPIdentifierSetCodingKeyModelKind; other keys under it are not shown. Store "
                 "Adam ID, Global Playlist ID and Device Library Persistent ID are the "
                 "MPIdentifierSet keys of those names. Person ID and Database ID are "
                 "MPIdentifierSetCodingKeyPersonID and MPIdentifierSetCodingKeyDatabaseID. Other "
                 "Identifiers lists the remaining keys of the set as key=value, rendered as "
                 "text. A value of 0, False, empty text, an empty list or an empty dictionary is "
                 "treated as no value and is not shown. Person ID had a value on all 4 items, "
                 "Store Adam ID and Global Playlist ID on 2 each, and Device Library Persistent "
                 "ID and Database ID on 1 (dexter_ios18). Other Identifiers had a value on the 2 "
                 "dexter_ios18 items and no value on the 2 hickman_ios14 items. The 4 items seen "
                 "hold only dateAdded, identifiers and kind: no title and no search text. What "
                 "puts an item in this list is not established. The key was on 2 of the 23 "
                 "sample_data images: dexter_ios18 (Apple.Music with 2 items, and Library with "
                 "an empty array) and hickman_ios14 (Apple.Music with 2 items). Of the 21 images "
                 "recorded with 0 rows, 15 have the file without the key and 6 have no "
                 "com.apple.Music.plist under mobile/Library/Preferences. Suggested in issue "
                 "#1876.",
        "paths": ('*/mobile/Library/Preferences/com.apple.Music.plist',),
        "output_types": "standard",
        "artifact_icon": "music",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 2 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 2 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
    "appleMusicRecentSearchTerms": {
        "name": "Apple Music Recent Search Terms",
        "description": "One row per string in the recentSearchTerms list of "
                       "com.apple.Music.plist.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-10",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "Apple Music",
        "notes": "Position is the 1-based place of the string in the recentSearchTerms list, as "
                 "stored; whether the first string is the newest, and what puts a string in the "
                 "list, is not established. The list holds strings only, with no date beside "
                 "them (1 image seen). It was on 1 of the 23 sample_data images (hickman_ios13, "
                 "1 string). Of the 22 images recorded with 0 rows, 16 have the file without the "
                 "key and 6 have no com.apple.Music.plist under mobile/Library/Preferences. "
                 "Suggested in issue #1876.",
        "paths": ('*/mobile/Library/Preferences/com.apple.Music.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "music",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 1 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
}

import base64
import binascii
import json

from scripts.ilapfuncs import (artifact_processor, convert_cocoa_core_data_ts_to_utc,
                               get_file_path, get_plist_content, get_plist_file_content, logfunc)

_RECENTLY_SEARCHED_KEY = 'RecentlySearched'
_SEARCH_TERMS_KEY = 'recentSearchTerms'
_MODEL_KIND_KEY = 'MPIdentifierSetCodingKeyModelKind'
# Identifier keys that get a column of their own, in column order.
_IDENTIFIER_COLUMNS = ('MPIdentifierSetStoreAdamID', 'MPIdentifierSetGlobalPlaylistID',
                       'MPIdentifierSetDeviceLibraryPersistentID',
                       'MPIdentifierSetCodingKeyPersonID', 'MPIdentifierSetCodingKeyDatabaseID')


def _load(context):
    source_path = get_file_path(context.get_files_found(), 'com.apple.Music.plist')
    if not source_path:
        return '', {}
    plist = get_plist_file_content(source_path)
    if not isinstance(plist, dict):
        logfunc(f'{source_path} did not read as a plist dictionary')
        return source_path, {}
    return source_path, plist


def _has_value(value):
    """ False, 0, empty text and empty containers are treated as no value. """
    return value not in ('', None, 0, False) and value != [] and value != {}


def _identifier_set(entry, where):
    """ The archived identifier set of an entry as a dictionary, or {} when it does not decode. """
    encoded = entry.get('identifiers')
    if not isinstance(encoded, str):
        return {}
    try:
        archived = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError):
        logfunc(f'{where}: identifiers is not base64 and was not decoded')
        return {}
    decoded = get_plist_content(archived)
    if not isinstance(decoded, dict) or not decoded:
        logfunc(f'{where}: identifiers did not decode to a dictionary')
        return {}
    return decoded


def _entries(stored, where):
    if isinstance(stored, (bytes, str)):
        try:
            stored = json.loads(stored)
        except ValueError:
            logfunc(f'{where} is not JSON and was not reported')
            return []
    if not isinstance(stored, list):
        logfunc(f'{where} is not a list and was not reported')
        return []
    return stored


@artifact_processor
def appleMusicRecentlySearched(context):
    """ See artifact description """
    data_headers = (('Date Added', 'datetime'), 'Date Added Number', 'Source', 'Position', 'Kind',
                    'Model Class', 'Store Adam ID', 'Global Playlist ID',
                    'Device Library Persistent ID', 'Person ID', 'Database ID',
                    'Other Identifiers')
    data_list = []
    source_path, plist = _load(context)
    if not source_path:
        return data_headers, data_list, ''

    sources = plist.get(_RECENTLY_SEARCHED_KEY)
    if not isinstance(sources, dict):
        return data_headers, data_list, source_path

    for source in sorted(sources, key=str):
        where = f'{_RECENTLY_SEARCHED_KEY}/{source}'
        for position, entry in enumerate(_entries(sources[source], where), start=1):
            if not isinstance(entry, dict):
                logfunc(f'{where}: entry {position} is not a dictionary and was not reported')
                continue
            date_number = entry.get('dateAdded')
            date_added = ''
            if isinstance(date_number, (int, float)) and not isinstance(date_number, bool):
                date_added = convert_cocoa_core_data_ts_to_utc(date_number)
            identifiers = _identifier_set(entry, f'{where} entry {position}')
            model_kind = identifiers.get(_MODEL_KIND_KEY)
            model_class = model_kind.get('modelClass', '') if isinstance(model_kind, dict) else ''
            other = '; '.join(
                f'{key}={identifiers[key]}' for key in sorted(identifiers, key=str)
                if key not in _IDENTIFIER_COLUMNS and key != _MODEL_KIND_KEY
                and _has_value(identifiers[key]))
            data_list.append(
                (date_added, '' if date_number is None else str(date_number), str(source),
                 position, str(entry.get('kind', '')), str(model_class))
                + tuple(str(identifiers[key]) if _has_value(identifiers.get(key)) else ''
                        for key in _IDENTIFIER_COLUMNS)
                + (other,))
    return data_headers, data_list, source_path


@artifact_processor
def appleMusicRecentSearchTerms(context):
    """ See artifact description """
    data_headers = ('Position', 'Search Term')
    data_list = []
    source_path, plist = _load(context)
    if not source_path:
        return data_headers, data_list, ''

    terms = plist.get(_SEARCH_TERMS_KEY)
    if isinstance(terms, list):
        data_list = [(position, str(term)) for position, term in enumerate(terms, start=1)]
    return data_headers, data_list, source_path
