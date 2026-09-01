__artifacts_v2__ = {
    "cnnSearches": {
        "name": "CNN - Searches",
        "description": "Search terms sent to the CNN search service, recovered from the "
                       "request URLs the app's network cache retained, with how many cached "
                       "responses each term produced.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "CNN",
        "notes": "Read from the app's NSURLCache at Library/Caches/com.cnn.iphone. The search term is "
                 "carried in the q parameter of the cached request URL and is percent decoded for "
                 "display; the raw parameter is reported beside it so the decoding can be checked. One "
                 "row is reported per distinct term, because the app requests successive pages of the "
                 "same search and each page is cached as its own entry. Cached Responses counts those "
                 "entries and Deepest Result Offset is the largest from parameter seen for the term, "
                 "which records how far through the results the app requested rather than how far a "
                 "person read. First and Last Cached are the cache's own timestamps and are UTC: on "
                 "the tested samples a response's cache timestamp equalled the HTTP Date header stored "
                 "in the same row, which is written in GMT, to the second. A term is evidence that the "
                 "search was issued from this app; it does not establish who typed it. Result Types "
                 "Requested held one value on every row of one tested sample because the app asked for "
                 "the same result types each time; it is kept because the other sample shows the "
                 "parameter does vary. The app was present on 2 of the 26 registered iOS corpora swept "
                 "for it and both carry rows, so the counts recorded here come from two independent "
                 "extractions.",
        "paths": ('*/Library/Caches/com.cnn.iphone/Cache.db*',
                  '*/Library/Caches/com.cnn.iphone/fsCachedData/*'),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "search",
        "sample_data": {
            "falken_ios26": "iOS 26.2.1 | 2 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 3 rows",
        },
    },
    "cnnArticleRequests": {
        "name": "CNN - Article Requests",
        "description": "CNN article and video pages the app requested, recovered from the "
                       "request URLs its network cache retained.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "CNN",
        "notes": "Read from the app's NSURLCache at Library/Caches/com.cnn.iphone. Only paths under "
                 "the app's mobile content API that carry a year, month and day segment are reported, "
                 "which is the shape the app uses for an individual story; the home feed and video "
                 "feed endpoints it fetches on its own are excluded because they are requested without "
                 "a person choosing them. The date in the path is the story's own publication date and "
                 "is reported as the Published Date Segment as stored, which is not the same as when "
                 "it was requested. Requested is the cache timestamp and is UTC, corroborated against "
                 "the HTTP Date header stored in the same row. A cached request records that the app "
                 "fetched the page; the store keeps no dwell time or read state, so it does not "
                 "establish that the page was read. The app was present on 2 of the 26 registered iOS "
                 "corpora swept for it and both carry rows, so the counts recorded here come from two "
                 "independent extractions.",
        "paths": ('*/Library/Caches/com.cnn.iphone/Cache.db*',
                  '*/Library/Caches/com.cnn.iphone/fsCachedData/*'),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "news",
        "sample_data": {
            "falken_ios26": "iOS 26.2.1 | 6 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 2 rows",
        },
    },
}

import os
import re
from datetime import datetime, timezone
from urllib.parse import unquote_plus

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records

_SEARCH_PATH = '/search/mobile/'
_ARTICLE_PATH = re.compile(r'/mobile/v\d+/(\d{4}/\d{2}/\d{2})/(.+)$')


def _cache_stamp_to_utc(value):
    """The cache's own time_stamp column, recorded in UTC."""
    if not value:
        return ''
    try:
        return datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return ''


def _cache_databases(files_found):
    """The app's NSURLCache databases, sidecars and cached body files excluded."""
    databases = []
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        if os.path.basename(file_found) != 'Cache.db':
            continue
        if 'fsCachedData' in file_found:
            continue
        databases.append(file_found)
    return databases


def _requests(database):
    """Yield (request url, cache timestamp) for every cached response."""
    query = '''
    SELECT request_key, time_stamp
    FROM cfurl_cache_response
    ORDER BY time_stamp
    '''
    for record in get_sqlite_db_records(database, query):
        if record[0]:
            yield record[0], record[1]


def _query_parameter(url, name):
    """The raw value of a query parameter, or '' when it is absent."""
    match = re.search(rf'[?&]{name}=([^&]*)', url)
    return match.group(1) if match else ''


@artifact_processor
def cnnSearches(context):
    data_headers = (
        ('First Cached', 'datetime'),
        ('Last Cached', 'datetime'),
        'Search Term',
        'Search Term (as stored)',
        'Cached Responses',
        'Deepest Result Offset',
        'Result Types Requested',
        'Source File',
    )
    data_list = []
    source_files = []

    for database in _cache_databases(context.get_files_found()):
        collected = {}
        for url, stamp in _requests(database):
            if _SEARCH_PATH not in url:
                continue
            raw = _query_parameter(url, 'q')
            if not raw:
                continue
            offset = _query_parameter(url, 'from')
            types = _query_parameter(url, 'types')
            entry = collected.get(raw)
            if entry is None:
                collected[raw] = {'first': stamp, 'last': stamp, 'count': 1,
                                  'offset': offset, 'types': {unquote_plus(types)} if types
                                  else set()}
            else:
                entry['last'] = stamp
                entry['count'] += 1
                try:
                    if offset and int(offset) > int(entry['offset'] or 0):
                        entry['offset'] = offset
                except ValueError:
                    pass
                if types:
                    entry['types'].add(unquote_plus(types))
        for raw, entry in collected.items():
            data_list.append((
                _cache_stamp_to_utc(entry['first']),
                _cache_stamp_to_utc(entry['last']),
                unquote_plus(raw).strip(),
                raw,
                entry['count'],
                entry['offset'],
                ', '.join(sorted(entry['types'])),
                context.get_relative_path(database),
            ))
        if collected:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def cnnArticleRequests(context):
    data_headers = (
        ('Requested', 'datetime'),
        'Published Date Segment (as stored)',
        'Article Path',
        'Request URL',
        'Source File',
    )
    data_list = []
    source_files = []

    for database in _cache_databases(context.get_files_found()):
        seen = set()
        rows = 0
        for url, stamp in _requests(database):
            match = _ARTICLE_PATH.search(url.split('?')[0])
            if not match:
                continue
            path = match.group(0)
            if path in seen:
                continue
            seen.add(path)
            rows += 1
            data_list.append((
                _cache_stamp_to_utc(stamp),
                match.group(1),
                match.group(2),
                url.split('?')[0],
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)
