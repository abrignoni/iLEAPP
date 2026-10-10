""" Photos app recent searches: PhotoData/Caches/search/RecentSearches.plist """
__artifacts_v2__ = {
    "photosRecentSearches": {
        "name": "Photos Recent Searches",
        "description": "One row per entry in the Photos RecentSearches.plist, with its search "
                       "text and the title and query token stored for each represented object.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-10",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "Photos",
        "notes": "Position is the 1-based position of the entry in the file's array, as stored; "
                 "whether the first entry is the newest is not established. Search Text is the "
                 "entry's SearchText. Represented Objects is the number of items in the entry's "
                 "RepresentedObjects list. Represented Object Titles holds their title values, "
                 "and Token Text, Token User Category and Token Match Type hold the text, "
                 "userCategory and matchType fields of the PSIQueryToken archived in each item's "
                 "queryRepresentedObject, as stored, joined with a semicolon when an entry holds "
                 "more than one item. What the category and match type numbers mean is not "
                 "established. The file was on 2 of the 23 sample_data images (abe_ios16 with 3 "
                 "entries, otto_ios17 with 1). 2 of the 4 entries held one represented object "
                 "each and 2 held none; in both objects the title equalled Token Text and "
                 "differed from Search Text. No value in the file is a date on those 2 images. "
                 "The other 21 images have the PhotoData/Caches/search folder without a "
                 "RecentSearches.plist. Suggested in issue #1876.",
        "paths": ('*/mobile/Media/PhotoData/Caches/search/RecentSearches.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "search",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 3 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 1 rows",
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

from scripts.ilapfuncs import (artifact_processor, get_file_path, get_plist_content,
                               get_plist_file_content, logfunc)


def _token_field(token, key):
    value = token.get(key) if isinstance(token, dict) else None
    return '' if value is None else str(value)


@artifact_processor
def photosRecentSearches(context):
    """ See artifact description """
    data_headers = ('Position', 'Search Text', 'Represented Objects', 'Represented Object Titles',
                    'Token Text', 'Token User Category', 'Token Match Type')
    data_list = []
    source_path = get_file_path(context.get_files_found(), 'RecentSearches.plist')
    if not source_path:
        return data_headers, data_list, ''

    entries = get_plist_file_content(source_path)
    if not isinstance(entries, list):
        logfunc(f'{source_path} did not read as a plist array')
        return data_headers, data_list, source_path

    for position, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            logfunc(f'{source_path}: entry {position} is not a dictionary and was not reported')
            continue
        objects = entry.get('RepresentedObjects')
        objects = objects if isinstance(objects, list) else []
        titles, texts, categories, match_types = [], [], [], []
        for represented in objects:
            if not isinstance(represented, dict):
                continue
            titles.append(str(represented.get('title', '')))
            archived = represented.get('queryRepresentedObject')
            token = get_plist_content(archived) if isinstance(archived, bytes) else {}
            if isinstance(archived, bytes) and not token:
                logfunc(f'{source_path}: entry {position} holds a query object that did not decode')
            texts.append(_token_field(token, 'text'))
            categories.append(_token_field(token, 'userCategory'))
            match_types.append(_token_field(token, 'matchType'))
        data_list.append((position, str(entry.get('SearchText', '')), len(objects),
                          '; '.join(titles), '; '.join(texts), '; '.join(categories),
                          '; '.join(match_types)))
    return data_headers, data_list, source_path
