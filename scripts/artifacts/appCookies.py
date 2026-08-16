__artifacts_v2__ = {
    'appCookies': {
        'name': 'Cookies - Binary Cookies',
        'description': 'HTTP cookies stored by Safari and by individual applications in Cookies.binarycookies files',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-08-15',
        'requirements': 'none',
        'category': 'Cookies',
        'notes': ('Apple binarycookies format. Each application container keeps its own file, so the '
                  'container path identifies which application the cookie belongs to. '
                  "Reference: Satish B., 'BinaryCookieReader', "
                  'https://github.com/as0ler/BinaryCookieReader/blob/'
                  'd77e0f9eda49b9422211356027dca744363082a5/BinaryCookieReader.py'),
        'paths': (
            '*/mobile/Library/Cookies/Cookies.binarycookies',
            '*/mobile/Containers/Data/Application/*/Library/Cookies/Cookies.binarycookies',
            '*/mobile/Containers/Data/PluginKitPlugin/*/Library/Cookies/Cookies.binarycookies',
            '*/SystemData/com.apple.SafariViewService/Library/Cookies/Cookies.binarycookies',
        ),
        'output_types': 'standard',
        'artifact_icon': 'cookie',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 409 cookies across 33 container files',
        },
    },
}

import struct

from scripts.ilapfuncs import artifact_processor, logfunc, convert_cocoa_core_data_ts_to_utc

FILE_MAGIC = b'cook'
PAGE_MAGIC = b'\x00\x00\x01\x00'

# Offsets inside a single cookie record, relative to the record start.
_OFF_FLAGS = 8
_OFF_URL = 16
_OFF_NAME = 20
_OFF_PATH = 24
_OFF_VALUE = 28
# Bytes 32-39 are the "end of cookie" marker; the two dates follow it.
_OFF_DATES = 40

# Cookie flag bits.
COOKIE_FLAGS = ((1, 'Secure'), (4, 'HTTP Only'))


def _read_cstring(buffer, offset):
    """Read a NUL-terminated UTF-8 string starting at offset."""
    if offset <= 0 or offset >= len(buffer):
        return ''
    end = buffer.find(b'\x00', offset)
    if end == -1:
        end = len(buffer)
    return buffer[offset:end].decode('utf-8', 'replace')


def _decode_flags(flags):
    """Render the cookie flag bitfield as readable text."""
    names = [name for bit, name in COOKIE_FLAGS if flags & bit]
    return ', '.join(names)


def _parse_binarycookies(data):
    """Yield cookie dicts from the contents of a Cookies.binarycookies file."""
    if len(data) < 8 or data[:4] != FILE_MAGIC:
        return

    page_count = struct.unpack('>i', data[4:8])[0]
    if page_count <= 0:
        return

    header_end = 8 + 4 * page_count
    page_sizes = struct.unpack(f'>{page_count}i', data[8:header_end])

    offset = header_end
    for page_size in page_sizes:
        page = data[offset:offset + page_size]
        offset += page_size
        if len(page) < 8 or page[:4] != PAGE_MAGIC:
            continue

        cookie_count = struct.unpack('<i', page[4:8])[0]
        if cookie_count <= 0:
            continue
        cookie_offsets = struct.unpack(f'<{cookie_count}i', page[8:8 + 4 * cookie_count])

        for cookie_offset in cookie_offsets:
            record = page[cookie_offset:]
            if len(record) < _OFF_DATES + 16:
                continue
            flags = struct.unpack('<i', record[_OFF_FLAGS:_OFF_FLAGS + 4])[0]
            url_off, name_off, path_off, value_off = struct.unpack(
                '<4i', record[_OFF_URL:_OFF_VALUE + 4])
            expiry, creation = struct.unpack('<2d', record[_OFF_DATES:_OFF_DATES + 16])

            yield {
                'host': _read_cstring(record, url_off),
                'name': _read_cstring(record, name_off),
                'path': _read_cstring(record, path_off),
                'value': _read_cstring(record, value_off),
                'flags': flags,
                'expiry': expiry,
                'creation': creation,
            }


def _safe_cocoa(value):
    """Convert a Cocoa timestamp, tolerating the out-of-range values cookies carry."""
    if not value:
        return ''
    try:
        return convert_cocoa_core_data_ts_to_utc(value)
    except (ValueError, OverflowError, OSError):
        return ''


@artifact_processor
def appCookies(context):
    data_list = []
    data_headers = (
        ('Created', 'datetime'), ('Expires', 'datetime'), 'Host', 'Cookie Name',
        'Path', 'Value', 'Flags', 'Source File')

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('Cookies.binarycookies'):
            continue
        try:
            with open(file_found, 'rb') as handle:
                data = handle.read()
        except OSError as ex:
            logfunc(f'Could not read {file_found}: {ex}')
            continue

        relative_path = context.get_relative_path(file_found)
        try:
            cookies = list(_parse_binarycookies(data))
        except (struct.error, IndexError, ValueError) as ex:
            logfunc(f'Malformed binarycookies file {relative_path}: {ex}')
            continue

        for cookie in cookies:
            data_list.append((
                _safe_cocoa(cookie['creation']),
                _safe_cocoa(cookie['expiry']),
                cookie['host'],
                cookie['name'],
                cookie['path'],
                cookie['value'],
                _decode_flags(cookie['flags']),
                relative_path,
            ))

    return data_headers, data_list, ''
