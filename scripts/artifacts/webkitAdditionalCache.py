"""Additional WebKit stores outside the original NetworkCache artifact paths."""

import hashlib
import io
import json
import os
import re
import struct
from pathlib import Path
from urllib.parse import urlsplit

from scripts.ilapfuncs import (
    artifact_processor, check_in_embedded_media, check_in_media, logfunc,
)
from scripts.webkit_helpers import (
    OWNER_HEADERS, WebKitOwnerResolver, evidence_path, unix_timestamp,
)


__artifacts_v2__ = {
    'webkit_additional_cache_records': {
        'name': 'WebKit - Additional Cache Records',
        'description': 'Resource URLs and HTTP response metadata from additional WebKit '
                       'NetworkCache stores, including SafariViewService.',
        'author': '@ForensikITGmbH',
        'creation_date': '2026-10-12', 'last_update_date': '2026-10-12',
        'requirements': 'none', 'category': 'Browser',
        'notes': 'Complements the original webkit.py artifact without changing it. Records '
                 'under Library/Caches/WebKit/NetworkCache are left to that artifact. '
                 'Builds on NetworkCache research by @JamesHabben. '
                 'The resource decoder reads storage versions 16 and 17. Version 17 was '
                 'decoded with the version 16 layout on two iOS 18 images. The header '
                 'hash matched on all 11,866 records and Parse Status read Decoded '
                 'fields on every record. The WebKit commit that raised the version changed how the '
                 'key hash is computed and how certificate information is encoded; the '
                 'positions of the decoded fields were the same in the tested data. '
                 'Other versions, including version 18 set in WebKit '
                 'source on 2026-08-28, are listed with an unsupported-version status '
                 'and no decoded fields; no version 18 sample was tested. '
                 'A cache entry is evidence '
                 'of a cached resource, not a user navigation or link click. Timestamp '
                 'is the stored cache-entry time in Unix seconds. Raw time, byte range '
                 'and partial-decoding status are retained. Byte Range held no value on '
                 'any of the 12,158 rows in the four tested images with data. '
                 'Header hashes are checked '
                 'when the corresponding store salt is acquired; persistence checksums '
                 'are not verified. Research mode exposes additional encoded fields. '
                 'Sources, WebKit at a storage version 17 commit: '
                 'https://github.com/WebKit/WebKit/blob/'
                 'cffd5ed032c478c1dee5311a89b91e64909e8b90/Source/WebKit/'
                 'NetworkProcess/cache/NetworkCacheStorage.cpp#L739 ; '
                 'https://github.com/WebKit/WebKit/blob/'
                 'cffd5ed032c478c1dee5311a89b91e64909e8b90/Source/WebKit/'
                 'NetworkProcess/cache/NetworkCacheEntry.cpp#L87 ; version 17 change: '
                 'https://github.com/WebKit/WebKit/commit/'
                 '484500b2c078b29f80e12b8130c3f95ca698e2d3',
        'paths': (
            '*/NetworkCache/Version*/salt',
            '*/NetworkCache/Version*/Records/*/Resource/*',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/Containers/Data/PluginKitPlugin/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/[Cc]ontainers/Bundle/Application/*/*.app/Info.plist',
            '*/[Cc]ontainers/Bundle/Application/*/iTunesMetadata.plist',
        ),
        'output_types': 'standard', 'research_mode': False, 'artifact_icon': 'archive',
        'sample_data': {
            'ctf2020_ios12': 'iOS 12.4 | 0 rows',
            'magnet_ios16': 'iOS 16.1.1 | 20 rows | storage version 16',
            'iphone11_ios17': 'iOS 17.3 | 272 rows | storage version 16',
            'dexter_ios18': 'iOS 18.3.2 | 11862 rows | storage version 17',
            'hc_ios18_7': 'iOS 18.7.8 | 4 rows | storage version 17',
        },
    },
}

_VERSION_ROOT = re.compile(r'^(.*[/\\]NetworkCache[/\\]Version[^/\\]+)(?:[/\\]|$)')
_SUPPORTED_VERSIONS = (16, 17)
_MAX_STRING_BYTES = 16 * 1024 * 1024
_MAX_IMAGE_BYTES = 64 * 1024 * 1024

RESEARCH_HEADERS = (
    ('Timestamp', 'datetime'), 'Raw Timestamp',
    'Application GUID', 'Records GUID', 'File', 'Salt', 'Header', 'Partition',
    'Partition Flag', 'Type', 'Type Flag', 'URI', 'URI Flag',
    'Filename', 'Foldername', 'Meta SHA1', 'Meta Size',
    'Body SHA1', 'Body Size', 'Is Body Inline', 'Metadata Checksum', 'Start of Meta',
    'Meta URI', 'Meta URI Flag', 'Content Type',
    'Content Type Flag', 'Expected Content Length', 'Encoding Type', 'Encoding Type Flag',
    'HTTP Status Text', 'HTTP Status Text Flag', 'HTTP Version', 'HTTP Version Flag',
    'HTTP Header Count', 'HTTP Headers', 'Has Cookie', 'Response Code', 'Other Trailing Data',
    'Full File Path', ('Thumbnail', 'media'),
)

_EXTRA_HEADERS = (
    'Byte Range', 'Header Hash Status', 'Parse Status', 'Cached Body File',
) + OWNER_HEADERS


class CacheDecodeError(ValueError):
    """A truncated or unsupported encoded field."""


class _Reader:
    def __init__(self, handle, end):
        self.handle, self.end = handle, end

    def read(self, size):
        if size < 0 or size > self.end - self.handle.tell():
            raise CacheDecodeError('Truncated field')
        data = self.handle.read(size)
        if len(data) != size:
            raise CacheDecodeError('Truncated field')
        return data

    def unpack(self, format_string):
        return struct.unpack(format_string, self.read(struct.calcsize(format_string)))[0]

    def string(self):
        length = self.unpack('<I')
        if length == 0xffffffff:
            return '', ''
        flag = self.read(1)
        if flag not in (b'\x00', b'\x01'):
            raise CacheDecodeError('Invalid string encoding flag')
        byte_length = length * (2 if flag == b'\x00' else 1)
        if byte_length > _MAX_STRING_BYTES:
            raise CacheDecodeError('String exceeds decoding limit')
        data = self.read(byte_length)
        encoding = 'utf-16-le' if flag == b'\x00' else 'latin-1'
        try:
            return data.decode(encoding), flag.hex()
        except UnicodeDecodeError as error:
            raise CacheDecodeError('Invalid UTF-16 string') from error


def read_vf(handle):
    """Read a persisted WebKit string without reading beyond the file."""
    position = handle.tell()
    handle.seek(0, os.SEEK_END)
    end = handle.tell()
    handle.seek(position)
    try:
        return _Reader(handle, end).string()
    except CacheDecodeError:
        return None, None


def cache_record_timestamp(timestamp):
    return unix_timestamp(timestamp)


def extract_path_info(file_path):
    parts = str(file_path).replace('\\', '/').split('/')
    app_guid = records_guid = ''
    for index, part in enumerate(parts[:-1]):
        if part in ('Application', 'PluginKitPlugin', 'AppGroup'):
            app_guid = parts[index + 1]
        elif part == 'Records':
            records_guid = parts[index + 1]
    return app_guid, records_guid


def _store_root(path):
    match = _VERSION_ROOT.match(str(path))
    return os.path.normcase(os.path.normpath(match[1])) if match else ''


def _response_fields(metadata, values):
    reader = _Reader(io.BytesIO(metadata), len(metadata))
    values['Start of Meta'] = reader.read(1).hex()
    for name in ('Meta URI', 'Content Type'):
        values[name], values[name + ' Flag'] = reader.string()
    values['Expected Content Length'] = reader.unpack('<q')
    for name in ('Encoding Type', 'HTTP Status Text', 'HTTP Version'):
        values[name], values[name + ' Flag'] = reader.string()
    count = reader.unpack('<Q')
    values['HTTP Header Count'] = count
    if count > 10000 or count * 10 > len(metadata) - reader.handle.tell():
        raise CacheDecodeError('Invalid HTTP header count')
    headers = {}
    for _ in range(count):
        key, _ = reader.string()
        value, _ = reader.string()
        headers[key] = value
    values['HTTP Headers'] = json.dumps(headers, ensure_ascii=False, sort_keys=True)
    values['Has Cookie'] = 'Yes' if any('cookie' in key.lower() for key in headers) else 'No'
    code = reader.unpack('<H')
    if not 100 <= code <= 599:
        raise CacheDecodeError('Invalid HTTP response status')
    values['Response Code'] = code
    values['Other Trailing Data'] = metadata[reader.handle.tell():].hex()


def _parse_record(path, salt):
    values = {'Parse Status': 'Decoded fields; persistence checksums not verified',
              'Header Hash Status': 'Not checked'}
    body_offset = None
    try:
        with open(path, 'rb') as handle:
            size = os.fstat(handle.fileno()).st_size
            reader = _Reader(handle, size)
            version = reader.unpack('<I')
            values['Header'] = version
            if version not in _SUPPORTED_VERSIONS:
                values['Parse Status'] = f'Unsupported cache version {version}'
                return values, None
            for name in ('Partition', 'Type', 'URI', 'Byte Range'):
                values[name], flag = reader.string()
                values[name + ' Flag'] = flag
            if values['Type'] != 'Resource':
                raise CacheDecodeError('Record type is not Resource')
            values['Filename'] = reader.read(20).hex()
            values['Foldername'] = reader.read(20).hex()
            raw_timestamp = reader.unpack('<d')
            values['Raw Timestamp'] = str(raw_timestamp)
            values['Timestamp'] = cache_record_timestamp(raw_timestamp)
            values['Meta SHA1'] = reader.read(20).hex()
            metadata_size = reader.unpack('<Q')
            values['Meta Size'] = metadata_size
            values['Body SHA1'] = reader.read(20).hex()
            values['Body Size'] = reader.unpack('<Q')
            inline = reader.unpack('<B')
            if inline not in (0, 1):
                raise CacheDecodeError('Invalid inline-body flag')
            values['Is Body Inline'] = 'Yes' if inline else 'No'
            values['Metadata Checksum'] = reader.read(20).hex()
            if metadata_size > _MAX_STRING_BYTES:
                raise CacheDecodeError('Response metadata exceeds decoding limit')
            metadata = reader.read(metadata_size)
            body_offset = handle.tell()
            if salt:
                digest = hashlib.sha1(salt + metadata).hexdigest()
                values['Header Hash Status'] = 'Verified' if digest == values['Meta SHA1'] else 'Mismatch'
            else:
                values['Header Hash Status'] = 'Salt not acquired'
            _response_fields(metadata, values)
            if inline and values['Body Size'] > size - body_offset:
                raise CacheDecodeError('Truncated inline body')
    except (OSError, CacheDecodeError, struct.error) as error:
        values['Parse Status'] = f'Partial: {error}'
    return values, body_offset


def _thumbnail(path, values, body_offset, context):
    external = str(path) + '-blob'
    if values.get('Is Body Inline') == 'No' and os.path.isfile(external):
        values['Cached Body File'] = evidence_path(context, external)
    content_type = values.get('Content Type', '')
    if not content_type.startswith('image/'):
        return None
    try:
        name = Path(urlsplit(values.get('URI', '')).path).name or Path(path).name
    except ValueError:
        name = Path(path).name
    try:
        if values.get('Is Body Inline') == 'Yes' and body_offset is not None:
            length = values.get('Body Size', 0)
            if 0 < length <= _MAX_IMAGE_BYTES and os.path.getsize(path) - body_offset >= length:
                with open(path, 'rb') as handle:
                    handle.seek(body_offset)
                    body = handle.read(length)
                return check_in_embedded_media(path, body, name=name, force_type=content_type)
        elif os.path.isfile(external) and os.path.getsize(external) <= _MAX_IMAGE_BYTES:
            return check_in_media(external, name=name, force_type=content_type)
    except (OSError, ValueError) as error:
        logfunc(f'Could not register WebKit image {evidence_path(context, path)}: {error}')
    return None


@artifact_processor
def webkit_additional_cache_records(context):
    files = tuple(dict.fromkeys(map(str, context.get_files_found())))
    resolver = WebKitOwnerResolver(context, files)
    research = context.get_artifact_info().get('research_mode', False)
    headers = RESEARCH_HEADERS if research else (
        ('Timestamp', 'datetime'), 'Raw Timestamp',
        'Application GUID', 'Records GUID', 'File', 'Salt', 'URI',
        'Content Type', 'Body Size', 'Is Body Inline', 'HTTP Headers', 'Response Code',
        'Full File Path', ('Thumbnail', 'media'),
    )
    headers += _EXTRA_HEADERS
    result = context.create_artifact_result(headers=headers)
    salts, sources = {}, set()
    for path in files:
        if Path(path).name == 'salt' and _store_root(path):
            try:
                with open(path, 'rb') as handle:
                    salts[_store_root(path)] = handle.read(1024)
            except OSError as error:
                logfunc(f'Could not read WebKit salt {evidence_path(context, path)}: {error}')
    for path in sorted(files):
        normalized = path.replace('\\', '/')
        if '/Library/Caches/WebKit/NetworkCache/' in normalized:
            continue
        if not re.search(r'/NetworkCache/Version[^/]+/Records/[^/]+/Resource/[^/]+$', normalized):
            continue
        if path.endswith('-blob'):
            continue
        relative = evidence_path(context, path)
        sources.add(evidence_path(context, os.path.dirname(path)))
        salt = salts.get(_store_root(path), b'')
        values, body_offset = _parse_record(path, salt)
        app_guid, record_guid = extract_path_info(path)
        values.update({'Application GUID': app_guid, 'Records GUID': record_guid,
                       'File': Path(path).name, 'Salt': salt.hex(), 'Full File Path': relative})
        values['Thumbnail'] = _thumbnail(path, values, body_offset, context)
        values.update(zip(OWNER_HEADERS, resolver.resolve(path)))
        result.add_row(tuple(values.get(header[0] if isinstance(header, tuple) else header, '')
                             for header in headers))
    result.set_source_path('\n'.join(sorted(sources)))
    return result
