__artifacts_v2__ = {
    'safariCache': {
        'name': 'Safari Browser - Cache Records',
        'description': 'URL cache records held by Safari, with the HTTP response details and '
                       'the cached payload for each entry',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-29',
        'last_update_date': '2026-07-29',
        'requirements': 'none',
        'category': 'Safari Browser',
        'notes': ('An entry records that Safari fetched and cached a URL, not that the user '
                  'navigated to it: pages pull subresources, and Safari fetches configuration '
                  'files on its own. Payloads above a size threshold are written to the '
                  'sibling fsCachedData directory instead of the database, in which case '
                  'receiver_data holds the file name rather than the content.'),
        'paths': ('*/mobile/Containers/Data/Application/*/Library/Caches/com.apple.mobilesafari/Cache.db*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/com.apple.mobilesafari/fsCachedData/*'),
        'output_types': 'standard',
        'artifact_icon': 'browser',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 6 rows; all six live in the WAL, the database file '
                              'alone parses as empty',
            'magnet_ios16': 'iOS 16.1.1 | 1 row; payload on the filesystem',
            'hc_ios18_7': '6 rows; 2 payloads on the filesystem, 4 inline',
        },
    },
}

import os

from scripts.filetype import guess_mime
from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records, get_plist_content, check_in_media, \
    check_in_embedded_media, convert_human_ts_to_utc

# Tokens CFNetwork writes in place of a value it did not record.
NULL_TOKENS = ('__CFURLResponseNullTokenString__', '__CFURLRequestNullTokenString__')

HTTP_METHODS = ('GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'CONNECT', 'TRACE')

# Response headers worth their own column.
REPORTED_HEADERS = ('Content-Type', 'Content-Length', 'Date', 'Expires', 'Last-Modified',
                    'Cache-Control', 'Server')

# Header carrying the base64 archive of the original header casing. It duplicates
# what the sibling keys already hold and is long enough to swamp the report.
HEADER_ARCHIVE_KEY = '__hhaa__'


def _as_text(value):
    """Decode a receiver_data file name, which reads back as bytes or as text."""
    if not value:
        return ''
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    return str(value)


def _as_bytes(value):
    """Return payload content as bytes whichever type sqlite handed back."""
    if not value:
        return b''
    if isinstance(value, bytes):
        return value
    return str(value).encode('utf-8', 'replace')


def _archived_array(blob):
    """Return the value list of an archived CFURLResponse or CFURLRequest.

    Both blobs are binary plists holding a Version number and an Array whose
    positions are the archived fields. The positions move between iOS versions,
    so callers pick values out of the array by shape rather than by index.
    """
    if not blob:
        return []
    content = get_plist_content(bytes(blob))
    if not isinstance(content, dict):
        return []
    array = content.get('Array')
    return array if isinstance(array, list) else []


def _url(array):
    """The archived URL, held in a dict under _CFURLString."""
    for item in array:
        if isinstance(item, dict) and '_CFURLString' in item:
            return item['_CFURLString']
    return ''


def _status_code(array):
    """The HTTP status, the only integer in the array inside the status range."""
    for item in array:
        if isinstance(item, int) and not isinstance(item, bool) and 100 <= item <= 599:
            return item
    return ''


def _headers(array):
    """The header dictionary, the only dict of string keys that is not the URL."""
    for item in array:
        if isinstance(item, dict) and '_CFURLString' not in item:
            if all(isinstance(key, str) for key in item):
                return {key: value for key, value in item.items()
                        if key != HEADER_ARCHIVE_KEY}
    return {}


def _mime_type(array):
    """The MIME type: a bare type/subtype string, unlike the URL or the tokens."""
    for item in array:
        if not isinstance(item, str) or item in NULL_TOKENS:
            continue
        if item.count('/') == 1 and ' ' not in item and not item.startswith('http'):
            return item
    return ''


def _method(array):
    """The request method, an uppercase verb from the known set."""
    for item in array:
        if isinstance(item, str) and item in HTTP_METHODS:
            return item
    return ''


def _payload_type(data, path):
    """Best effort content type for a cached payload."""
    try:
        mime = guess_mime(path) if path else guess_mime(data)
    except (TypeError, OSError, AttributeError):
        mime = None
    if mime:
        return mime
    if not data:
        return ''
    stripped = data.lstrip()
    if stripped[:1] in (b'{', b'['):
        return 'application/json'
    if data.startswith(b'\x1f\x8b'):
        return 'application/gzip'
    if data.startswith(b'SQLite format 3'):
        return 'application/x-sqlite3'
    try:
        data.decode('utf-8')
        return 'text/plain'
    except UnicodeDecodeError:
        return 'application/octet-stream'


@artifact_processor
def safariCache(context):
    source_path = get_file_path(context.get_files_found(), 'Cache.db')
    data_list = []
    data_headers = (
        ('Timestamp', 'datetime'), 'Request URL', 'HTTP Status', 'Request Method',
        'MIME Type', ('Cached Payload', 'media'), 'Payload Location', 'Cache File Name',
        'Payload Size', 'Payload Type', 'Content Type', 'Content Length', 'Date', 'Expires',
        'Last Modified', 'Cache Control', 'Server', 'Partition', 'Storage Policy', 'Entry ID')
    if not source_path:
        return data_headers, data_list, ''

    fs_cached_dir = os.path.join(os.path.dirname(source_path), 'fsCachedData')

    query = '''
    SELECT response.entry_ID, response.request_key, response.time_stamp, response.partition,
           response.storage_policy, receiver.isDataOnFS, receiver.receiver_data,
           blob.response_object, blob.request_object
    FROM cfurl_cache_response AS response
    LEFT JOIN cfurl_cache_receiver_data AS receiver ON receiver.entry_ID = response.entry_ID
    LEFT JOIN cfurl_cache_blob_data AS blob ON blob.entry_ID = response.entry_ID
    ORDER BY response.time_stamp
    '''

    for record in get_sqlite_db_records(source_path, query):
        response_array = _archived_array(record['response_object'])
        request_array = _archived_array(record['request_object'])
        headers = _headers(response_array)

        payload = record['receiver_data']
        payload_path = ''
        cache_file_name = ''
        media = None

        if record['isDataOnFS']:
            # receiver_data holds the name of a file in the sibling directory.
            cache_file_name = _as_text(payload)
            location = 'File system'
            payload_path = os.path.join(fs_cached_dir, cache_file_name)
            if cache_file_name and os.path.isfile(payload_path):
                payload_size = os.path.getsize(payload_path)
                with open(payload_path, 'rb') as payload_file:
                    sample = payload_file.read(8192)
            else:
                # The record survived but the payload file did not come across.
                payload_size = ''
                sample = b''
                payload_path = ''
        else:
            location = 'Database' if payload else ''
            sample = _as_bytes(payload)
            payload_size = len(sample)

        payload_type = _payload_type(sample, payload_path)
        if payload_type.startswith(('image', 'video', 'audio')):
            if payload_path:
                media = check_in_media(payload_path)
            elif sample:
                media = check_in_embedded_media(
                    source_path, sample, name=f"entry_{record['entry_ID']}")

        data_list.append((
            convert_human_ts_to_utc(record['time_stamp']),
            record['request_key'] or _url(response_array),
            _status_code(response_array),
            _method(request_array),
            _mime_type(response_array),
            media,
            location,
            cache_file_name,
            payload_size,
            payload_type,
            headers.get('Content-Type', ''),
            headers.get('Content-Length', ''),
            headers.get('Date', ''),
            headers.get('Expires', ''),
            headers.get('Last-Modified', ''),
            headers.get('Cache-Control', ''),
            headers.get('Server', ''),
            record['partition'],
            record['storage_policy'],
            record['entry_ID'],
        ))

    return data_headers, data_list, source_path
