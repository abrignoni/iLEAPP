""" Messages #images app: HashtagImagesExtension preferences and plugin metadata cache """
__artifacts_v2__ = {
    "hashtagImagesRecentQueries": {
        "name": "Hashtag Images Recent Queries",
        "description": "One row per string in STSRecentQueries of the #images extension "
                       "preferences plist.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-10",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "Hashtag Images",
        "notes": "Position is the 1-based place of the string in STSRecentQueries, as stored; "
                 "whether the first string is the newest, and what puts a string in the list, is "
                 "not established. No value in the plist was a date on the 3 images that have "
                 "it. It was on 3 of the 23 sample_data images (adams_iphone12mini with 1 "
                 "string, falken_ios26 and hc_ios17_2 with 3 each). No test case is committed "
                 "because none of those three images is publicly available. Source File is the "
                 "plist a row came from, and each of the 3 images had one such plist. The plist "
                 "also holds LegalNoticeCount, an integer, and STSReportConcernResults, an empty "
                 "dictionary on all 3 images; neither is reported. The other 20 images have no "
                 "such plist under a PluginKitPlugin container. Suggested in issue #1876.",
        "paths": ('*/Containers/Data/PluginKitPlugin/*/Library/Preferences/'
                  'com.apple.siri.parsec.HashtagImagesApp.HashtagImagesExtension.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "hash",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 1 rows",
            "hc_ios17_2": "iOS 17.2.1 | 3 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 3 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
    "hashtagImagesRecentResults": {
        "name": "Hashtag Images Recent Results",
        "description": "One row per entry in STSRecentResults1 of the #images extension "
                       "preferences plist, with the provider and URLs stored for it.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-10",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "Hashtag Images",
        "notes": "Position is the 1-based place of the entry in STSRecentResults1, as stored. An "
                 "entry that is not a dictionary is logged and skipped, and its position is "
                 "still counted; all 8 entries seen were dictionaries. Whether the first entry "
                 "is the newest, what puts an entry in the list, and how entries relate to the "
                 "strings in STSRecentQueries are not established; adams_iphone12mini holds 1 "
                 "query and 2 results. Provider, Result Type, URL, Host Page URL, Thumbnail URL, "
                 "Store Identifier, ID and Description Provider are the entry's "
                 "app-provider-name, result-type, url, meta-hostpage-url, thumbnail-url, "
                 "store-identifier, id and desc-provider-name, as stored. On the 8 entries seen "
                 "on 3 sample_data images, Provider was GIPHY on 6 and GIF Keyboard on 2, Result "
                 "Type was image_search on all 8, and Description Provider was an empty string "
                 "on all 8. Other Keys lists any key without a column of its own as key=value "
                 "and had no value on these entries. No value in the 8 entries seen was a date. "
                 "The URLs are remote addresses stored in the file, shown as text; this artifact "
                 "does not fetch them. No test case is committed because none of the three "
                 "images is publicly available. Source File is the plist a row came from, and "
                 "each of the 3 images had one such plist. The other 20 images have no such "
                 "plist under a PluginKitPlugin container. Suggested in issue #1876.",
        "paths": ('*/Containers/Data/PluginKitPlugin/*/Library/Preferences/'
                  'com.apple.siri.parsec.HashtagImagesApp.HashtagImagesExtension.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "hash",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 2 rows",
            "hc_ios17_2": "iOS 17.2.1 | 3 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 3 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
    "hashtagImagesMetadataCacheKeys": {
        "name": "Hashtag Images Metadata Cache Keys",
        "description": "One row per key, other than localID, of the Messages plugin metadata "
                       "cache plist kept for the #images extension.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-10",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "Hashtag Images",
        "notes": "Every key of the plist other than localID, with the value stored under it; "
                 "Local ID is the file's localID and is the same on every row from one file. "
                 "Keys are shown as stored and are not validated. On the 3 sample_data images "
                 "that have the file (adams_iphone12mini with 2 keys, falken_ios26 with 10, "
                 "hc_ios17_2 with 7) every value and every localID was a UUID-format string, and "
                 "the 19 keys had these forms: a plus sign and digits (10), that form prefixed "
                 "with iMessage;-; (4), SMS;-; (3) or any;-; (1), and chat followed by digits "
                 "prefixed with SMS;+; (1). What the presence of a key records is not "
                 "established, and this artifact reports no message content. No value in the "
                 "file was a date on the 3 images. No test case is committed because none of the "
                 "three images is publicly available. Source File is the plist a row came from, "
                 "and each of the 3 images had one such plist. The file name holds two colons in "
                 "the extraction; Source File shows them as underscores, which is how the tool "
                 "stages the file. The other 20 images have no such plist under "
                 "Library/SMS/PluginMetaDataCache. The #images preferences plist was suggested "
                 "in issue #1876; this cache file carries the same extension name and was not "
                 "named there.",
        "paths": ('*/Library/SMS/PluginMetaDataCache/*/com.apple.messages.'
                  'MSMessageExtensionBalloonPlugin:*:'
                  'com.apple.siri.parsec.HashtagImagesApp.HashtagImagesExtension.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "hash",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 2 rows",
            "hc_ios17_2": "iOS 17.2.1 | 7 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 10 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
}

from scripts.ilapfuncs import artifact_processor, get_plist_file_content, logfunc

_PLIST_NAME = 'com.apple.siri.parsec.HashtagImagesApp.HashtagImagesExtension.plist'
_QUERIES_KEY = 'STSRecentQueries'
_RESULTS_KEY = 'STSRecentResults1'
# Keys of a result that get a column of their own, in column order.
_RESULT_COLUMNS = ('app-provider-name', 'result-type', 'url', 'meta-hostpage-url',
                   'thumbnail-url', 'store-identifier', 'id', 'desc-provider-name')


def _plists(context, folder):
    """ Each matched plist that sits under a path segment named folder, as (path, dictionary). """
    for file_found in sorted(str(path) for path in context.get_files_found()):
        segments = file_found.replace('\\', '/').split('/')
        if not segments[-1].endswith(_PLIST_NAME) or folder not in segments:
            continue
        plist = get_plist_file_content(file_found)
        if not isinstance(plist, dict):
            logfunc(f'{file_found} did not read as a plist dictionary')
            plist = {}
        yield file_found, plist


def _list(plist, key):
    value = plist.get(key)
    return value if isinstance(value, list) else []


@artifact_processor
def hashtagImagesRecentQueries(context):
    """ See artifact description """
    data_headers = ('Position', 'Query', 'Source File')
    data_list = []
    source_paths = []
    for file_found, plist in _plists(context, 'PluginKitPlugin'):
        source_paths.append(file_found)
        source_file = context.get_relative_path(file_found)
        for position, query in enumerate(_list(plist, _QUERIES_KEY), start=1):
            data_list.append((position, str(query), source_file))
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def hashtagImagesRecentResults(context):
    """ See artifact description """
    data_headers = ('Position', 'Provider', 'Result Type', 'URL', 'Host Page URL',
                    'Thumbnail URL', 'Store Identifier', 'ID', 'Description Provider',
                    'Other Keys', 'Source File')
    data_list = []
    source_paths = []
    for file_found, plist in _plists(context, 'PluginKitPlugin'):
        source_paths.append(file_found)
        source_file = context.get_relative_path(file_found)
        for position, result in enumerate(_list(plist, _RESULTS_KEY), start=1):
            if not isinstance(result, dict):
                logfunc(f'{file_found}: result {position} is not a dictionary and was not reported')
                continue
            other = '; '.join(f'{key}={result[key]}' for key in sorted(result, key=str)
                              if key not in _RESULT_COLUMNS)
            data_list.append((position,)
                             + tuple('' if result.get(key) is None else str(result[key])
                                     for key in _RESULT_COLUMNS)
                             + (other, source_file))
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def hashtagImagesMetadataCacheKeys(context):
    """ See artifact description """
    data_headers = ('Key', 'Value', 'Local ID', 'Source File')
    data_list = []
    source_paths = []
    for file_found, plist in _plists(context, 'PluginMetaDataCache'):
        source_paths.append(file_found)
        source_file = context.get_relative_path(file_found)
        local_id = plist.get('localID')
        local_id = '' if local_id is None else str(local_id)
        for key in sorted(plist, key=str):
            if key != 'localID':
                data_list.append((str(key), str(plist[key]), local_id, source_file))
    return data_headers, data_list, '\n'.join(source_paths)
