__artifacts_v2__ = {
    'appStoreSearches': {
        'name': 'App Store - Searches',
        'description': 'Search terms submitted in the App Store, recovered from the cached search API requests',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-25',
        'requirements': 'none',
        'category': 'App Store',
        'notes': ('Suggestion rows are typeahead lookups fired per keystroke, so a single search '
                  'usually appears as a run of lengthening prefixes ending in the submitted term.'),
        'paths': ('*/mobile/Containers/Data/Application/*/Library/Caches/com.apple.AppStore/Cache.db*',),
        'output_types': 'standard',
        'artifact_icon': 'search',
        'sample_data': {
            'josh_ios17_ffs': 'iOS 17.3 | 27 rows (24 suggestion, 3 submitted)',
        },
    },
    'appStoreCachedRequests': {
        'name': 'App Store - Cached Requests',
        'description': 'All App Store API requests held in the application URL cache',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-25',
        'requirements': 'none',
        'category': 'App Store',
        'notes': '',
        'paths': ('*/mobile/Containers/Data/Application/*/Library/Caches/com.apple.AppStore/Cache.db*',),
        'output_types': 'standard',
        'artifact_icon': 'brand-appstore',
        'sample_data': {
            'josh_ios17_ffs': 'iOS 17.3 | 977 rows',
        },
    },
}

import urllib.parse

from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records, convert_human_ts_to_utc

# Path fragments that identify a search request, mapped to how the request was
# made. The suggestions endpoint is hit while the user types; the plain search
# endpoint is hit when a term is actually submitted.
SEARCH_ENDPOINTS = (
    ('/search/suggestions', 'Suggestion (typed)'),
    ('/search', 'Search (submitted)'),
)

# Query parameters that have held the search text across App Store versions.
TERM_PARAMETERS = ('term', 'q')


def _classify(path):
    """Return the request kind for an App Store API path, or None."""
    for fragment, label in SEARCH_ENDPOINTS:
        if fragment in path:
            return label
    return None


def _storefront(path):
    """Pull the storefront code out of a catalog path such as /v1/catalog/us/search."""
    parts = [p for p in path.split('/') if p]
    for index, part in enumerate(parts):
        if part in ('catalog', 'engagement') and index + 1 < len(parts):
            return parts[index + 1]
    return ''


@artifact_processor
def appStoreSearches(context):
    source_path = get_file_path(context.get_files_found(), 'Cache.db')
    data_list = []
    data_headers = (
        ('Timestamp', 'datetime'), 'Search Term', 'Request Kind', 'Storefront',
        'Platform', 'Language', 'Request URL', 'Entry ID')
    if not source_path:
        return data_headers, data_list, ''

    query = '''
    SELECT entry_ID, request_key, time_stamp
    FROM cfurl_cache_response
    WHERE request_key LIKE '%/search%'
    ORDER BY time_stamp
    '''

    for record in get_sqlite_db_records(source_path, query):
        request_url = record['request_key'] or ''
        parsed = urllib.parse.urlparse(request_url)
        kind = _classify(parsed.path)
        if not kind:
            continue

        params = urllib.parse.parse_qs(parsed.query)
        term = next((params[key][0] for key in TERM_PARAMETERS if key in params), None)
        if term is None:
            continue

        data_list.append((
            convert_human_ts_to_utc(record['time_stamp']),
            term,
            kind,
            _storefront(parsed.path),
            params.get('platform', [''])[0],
            params.get('l', [''])[0],
            request_url,
            record['entry_ID'],
        ))

    return data_headers, data_list, source_path


@artifact_processor
def appStoreCachedRequests(context):
    source_path = get_file_path(context.get_files_found(), 'Cache.db')
    data_list = []
    data_headers = (
        ('Timestamp', 'datetime'), 'Host', 'Path', 'Request URL', 'Entry ID')
    if not source_path:
        return data_headers, data_list, ''

    query = '''
    SELECT entry_ID, request_key, time_stamp
    FROM cfurl_cache_response
    ORDER BY time_stamp
    '''

    for record in get_sqlite_db_records(source_path, query):
        request_url = record['request_key'] or ''
        parsed = urllib.parse.urlparse(request_url)
        data_list.append((
            convert_human_ts_to_utc(record['time_stamp']),
            parsed.netloc,
            parsed.path,
            request_url,
            record['entry_ID'],
        ))

    return data_headers, data_list, source_path
