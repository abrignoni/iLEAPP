__artifacts_v2__ = {'life360CachedLocations': {'name': 'Life360 - Cached Device Locations',
                            'description': 'Device-location objects returned in cached Life360 API '
                                           'responses.',
                            'author': '@CyberMike81, OpenAI Codex',
                            'creation_date': '2026-10-22',
                            'last_update_date': '2026-10-22',
                            'requirements': 'none',
                            'category': 'Life360',
                            'notes': 'Location Time is lastObserved; First Observed and Updated are the '
                                     'separate response fields. These ISO times carry explicit offsets. '
                                     'Cached Time is the CFURL cache time, not a location fix. Numeric '
                                     'values are as stored; their units are not independently established; a '
                                     'cached location is not continuous tracking or proof of who carried the '
                                     'device. Each response item is retained with its complete JSON. Read '
                                     'from Library/Caches/com.life360.safetymap/Cache.db with the current '
                                     'WAL applied. Cached Time is SQLite CURRENT_TIMESTAMP text, read as '
                                     'UTC; invalid times are left blank and logged. Only the validated main '
                                     'app container is read. Tested on Life360 26.34.0.5 / iOS 18.6; other '
                                     'layouts may differ. Body Source File was empty in the tested '
                                     'extraction; inline responses have no external file. Cached Time, Cache '
                                     'Entry ID and Request Path are uniform within this tested '
                                     'single-response table.',
                            'paths': ('*/Library/Caches/com.life360.safetymap/Cache.db*',
                                      '*/Library/Caches/com.life360.safetymap/fsCachedData/*',
                                      '*/.com.apple.mobile_container_manager.metadata.plist'),
                            'output_types': 'all',
                            'artifact_icon': 'map-pin'},
 'life360CachedDevices': {'name': 'Life360 - Cached Devices',
                          'description': 'Device and owner objects returned in cached Life360 API responses.',
                          'author': '@CyberMike81, OpenAI Codex',
                          'creation_date': '2026-10-22',
                          'last_update_date': '2026-10-22',
                          'requirements': 'none',
                          'category': 'Life360',
                          'notes': 'Modified is the response modified field (ISO with an explicit offset). '
                                   'Owner IDs come only from the item owners array; no profile or location '
                                   'is joined by proximity. Device and owner fields are retained in Record '
                                   'JSON. Read from Library/Caches/com.life360.safetymap/Cache.db with the '
                                   'current WAL applied. Cached Time is SQLite CURRENT_TIMESTAMP text, read '
                                   'as UTC; invalid times are left blank and logged. Only the validated main '
                                   'app container is read. Tested on Life360 26.34.0.5 / iOS 18.6; other '
                                   'layouts may differ. Body Source File was empty in the tested extraction; '
                                   'inline responses have no external file. Cached Time, Cache Entry ID and '
                                   'Request Path are uniform within this tested single-response table.',
                          'paths': ('*/Library/Caches/com.life360.safetymap/Cache.db*',
                                    '*/Library/Caches/com.life360.safetymap/fsCachedData/*',
                                    '*/.com.apple.mobile_container_manager.metadata.plist'),
                          'output_types': 'standard',
                          'artifact_icon': 'devices'},
 'life360CachedDeviceIssues': {'name': 'Life360 - Cached Device Issues',
                               'description': 'Device issue objects returned in cached Life360 API '
                                              'responses.',
                               'author': '@CyberMike81, OpenAI Codex',
                               'creation_date': '2026-10-22',
                               'last_update_date': '2026-10-22',
                               'requirements': 'none',
                               'category': 'Life360',
                               'notes': 'Issue Start is the issue startTime field (ISO with an explicit '
                                        'offset). Names and values are as stored; an issue does not '
                                        'independently establish device capability or its duration. Record '
                                        'JSON retains the complete enclosing item and the selected issue '
                                        'as separate item and issue objects. Read from '
                                        'Library/Caches/com.life360.safetymap/Cache.db with the current WAL '
                                        'applied. Cached Time is SQLite CURRENT_TIMESTAMP text, read as UTC; '
                                        'invalid times are left blank and logged. Only the validated main '
                                        'app container is read. Tested on Life360 26.34.0.5 / iOS 18.6; '
                                        'other layouts may differ. Body Source File was empty in the tested '
                                        'extraction; inline responses have no external file. Cached Time, '
                                        'Cache Entry ID and Request Path are uniform within this tested '
                                        'single-response table.',
                               'paths': ('*/Library/Caches/com.life360.safetymap/Cache.db*',
                                         '*/Library/Caches/com.life360.safetymap/fsCachedData/*',
                                         '*/.com.apple.mobile_container_manager.metadata.plist'),
                               'output_types': 'standard',
                               'artifact_icon': 'alert-triangle'},
 'life360CachedCircles': {'name': 'Life360 - Cached Circles',
                          'description': 'Circle objects returned in cached Life360 API responses.',
                          'author': '@CyberMike81, OpenAI Codex',
                          'creation_date': '2026-10-22',
                          'last_update_date': '2026-10-22',
                          'requirements': 'none',
                          'category': 'Life360',
                          'notes': 'Created is createdAt from the circle object (Unix seconds). A cached '
                                   'circle list is not a history of membership. Record JSON retains the '
                                   'stored fields. Read from Library/Caches/com.life360.safetymap/Cache.db '
                                   'with the current WAL applied. Cached Time is SQLite CURRENT_TIMESTAMP '
                                   'text, read as UTC; invalid times are left blank and logged. Only the '
                                   'validated main app container is read. Tested on Life360 26.34.0.5 / iOS '
                                   '18.6; other layouts may differ. Body Source File was empty in the tested '
                                   'extraction because its response was inline. Cached Time, Cache Entry ID '
                                   'and Request Path are uniform within this tested single-response table.',
                          'paths': ('*/Library/Caches/com.life360.safetymap/Cache.db*',
                                    '*/Library/Caches/com.life360.safetymap/fsCachedData/*',
                                    '*/.com.apple.mobile_container_manager.metadata.plist'),
                          'output_types': 'standard',
                          'artifact_icon': 'users'},
 'life360CachedAccount': {'name': 'Life360 - Cached Account',
                          'description': 'The account profile returned in a cached Life360 API response.',
                          'author': '@CyberMike81, OpenAI Codex',
                          'creation_date': '2026-10-22',
                          'last_update_date': '2026-10-22',
                          'requirements': 'none',
                          'category': 'Life360',
                          'notes': 'Profile Created has no explicit zone in the tested response and remains '
                                   'as stored, without an assumed UTC time. Date of Birth also remains as '
                                   'stored. The profile describes the cached service response, not a '
                                   'verified identity. Settings and communications remain in Record JSON. '
                                   'Read from Library/Caches/com.life360.safetymap/Cache.db with the current '
                                   'WAL applied. Cached Time is SQLite CURRENT_TIMESTAMP text, read as UTC; '
                                   'invalid times are left blank and logged. Only the validated main app '
                                   'container is read. Tested on Life360 26.34.0.5 / iOS 18.6; other layouts '
                                   'may differ. Body Source File was empty because the tested profile '
                                   'response was inline.',
                          'paths': ('*/Library/Caches/com.life360.safetymap/Cache.db*',
                                    '*/Library/Caches/com.life360.safetymap/fsCachedData/*',
                                    '*/.com.apple.mobile_container_manager.metadata.plist'),
                          'output_types': 'standard',
                          'artifact_icon': 'user'},
 'life360CacheResponses': {'name': 'Life360 - Cached API Responses',
                           'description': 'An index of Life360 API responses and the availability of their '
                                          'cached bodies.',
                           'author': '@CyberMike81, OpenAI Codex',
                           'creation_date': '2026-10-22',
                           'last_update_date': '2026-10-22',
                           'requirements': 'none',
                           'category': 'Life360',
                           'notes': 'One row per first-party Life360 API cache entry, including '
                                    'missing/unreadable bodies. It indexes response availability, not user '
                                    'interaction. Request Path omits query strings, fragments and URL '
                                    'credentials. Third-party SDK, catalogue, image and configuration caches '
                                    'are not decoded into user activity. External bodies are resolved only '
                                    'by their recorded filename within this cache’s fsCachedData directory. '
                                    'Read from Library/Caches/com.life360.safetymap/Cache.db with the '
                                    'current WAL applied. Cached Time is SQLite CURRENT_TIMESTAMP text, read '
                                    'as UTC; invalid times are left blank and logged. Only the validated '
                                    'main app container is read. Tested on Life360 26.34.0.5 / iOS 18.6; '
                                    'other layouts may differ. Body Source File was empty throughout the '
                                    'tested extraction: its external references had no acquired bodies. The '
                                    'synthetic case includes a resolvable external body and a missing-body '
                                    'control, and Cached Time is uniform only in that fabricated case. '
                                    'Expanded bodies above 32 MiB are excluded with a diagnostic. Cached '
                                    'drive-feed, premium and experiments body references were missing in the '
                                    'tested extraction; their contents are not parsed. Circle-member '
                                    'profiles are not inferred from device-owner IDs.',
                           'paths': ('*/Library/Caches/com.life360.safetymap/Cache.db*',
                                     '*/Library/Caches/com.life360.safetymap/fsCachedData/*',
                                     '*/.com.apple.mobile_container_manager.metadata.plist'),
                           'output_types': 'standard',
                           'artifact_icon': 'database'}}
import gzip
import io
import json
import math
from pathlib import Path
import re
import sqlite3
import zlib
from datetime import datetime, timezone
from urllib.parse import urlsplit

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly
from scripts.life360_common import get_life360_files, life360_logger, seconds_to_utc

_MAX_BODY = 32 * 1024 * 1024
_HOSTS = {'api-cloudfront.life360.com', 'api.life360.com'}


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


def _text(value):
    if value is None:
        return ''
    if isinstance(value, (dict, list)):
        return _json(value)
    return value


def _time(value, label, cache=False, unix=False):
    if value is None or value == '':
        return ''
    try:
        if unix:
            if isinstance(value, bool) or not re.fullmatch(r'-?\d+(?:\.\d+)?', str(value)):
                raise ValueError
            number = float(value)
            if not math.isfinite(number):
                raise ValueError
            return seconds_to_utc(number, 1970)
        if not isinstance(value, str):
            raise ValueError
        if cache:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            raise ValueError
        return parsed.astimezone(timezone.utc)
    except (ValueError, TypeError, OverflowError):
        logfunc(f'Life360 cache invalid {label}; rendered time left blank')
        return ''


def _array(value, label):
    if value is None:
        return []
    if not isinstance(value, list):
        logfunc(f'Life360 cache {label} was not an array; raw response retained at its source')
        return []
    result = []
    for item in value:
        if isinstance(item, dict):
            result.append(item)
        else:
            logfunc(f'Life360 cache {label} contained a non-object item; item skipped')
    return result


def _reject_constant(_):
    raise ValueError('nonfinite JSON')


def _finite_float(text):
    value = float(text)
    if not math.isfinite(value):
        raise ValueError('nonfinite JSON')
    return value


def _body(database, data, on_disk, files):
    source = ''
    if on_disk is None:
        raise ValueError('body missing')
    if on_disk == 1:
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        if not isinstance(data, str) or data in ('.', '..') or not re.fullmatch(r'[A-Za-z0-9._-]+', data):
            raise ValueError('unsafe external-body reference')
        expected = database.parent / 'fsCachedData' / data
        if expected.resolve().parent != database.parent.resolve() / 'fsCachedData':
            raise ValueError('external body outside this cache')
        # The accepted file list is container-scoped and must name this exact cache directory.
        source = files.get(str(expected.resolve()))
        if source is None:
            raise ValueError('external body missing')
        source = str(expected)
        with Path(source).open('rb') as stream:
            data = stream.read(_MAX_BODY + 1)
    elif on_disk != 0:
        raise ValueError('unsupported body-storage flag')
    if data is None:
        raise ValueError('body missing')
    if isinstance(data, str):
        data = data.encode('utf-8')
    if not isinstance(data, bytes) or len(data) > _MAX_BODY:
        raise ValueError('body size or type unsupported')
    if data.startswith(b'\x1f\x8b'):
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
            data = stream.read(_MAX_BODY + 1)
        if len(data) > _MAX_BODY:
            raise ValueError('expanded body exceeds limit')
    value = json.loads(data, parse_constant=_reject_constant, parse_float=_finite_float)
    if not isinstance(value, (dict, list)):
        raise ValueError('body is not a JSON object or array')
    return value, source, len(data)


def _cache_rows(path, query, label, logger):
    connection = None
    try:
        with Path(path).open('rb') as stream:
            if stream.read(16) != b'SQLite format 3\x00':
                logger(f'Life360 cache SQLite read failed in {label!r}: invalid database header')
                return
        connection = open_sqlite_db_readonly(path)
        if connection is None:
            logger(f'Life360 cache SQLite read failed in {label!r}: read-only open unavailable')
            return
        yield from connection.execute(query)
    except (OSError, sqlite3.Error) as error:
        logger(f'Life360 cache SQLite read failed in {label!r} ({type(error).__name__}); '
                'earlier rows retained and other files continue')
    finally:
        if connection is not None:
            connection.close()


def _responses(context):
    logger = life360_logger(context, logfunc)
    paths = get_life360_files(context, logger)
    files = {str(Path(p).resolve()): p for p in paths}
    for name in paths:
        database = Path(name)
        if database.name != 'Cache.db':
            continue
        rel = context.get_relative_path(name)
        if database.parent.name != 'com.life360.safetymap' or database.parent.parent.name != 'Caches':
            logger(f'Life360 cache skipped matching database {rel!r}: not the main application API cache')
            continue
        query = '''SELECT r.entry_ID,r.request_key,r.time_stamp,d.isDataOnFS,d.receiver_data
                   FROM cfurl_cache_response r LEFT JOIN cfurl_cache_receiver_data d
                   ON d.entry_ID=r.entry_ID ORDER BY r.entry_ID'''
        for entry, key, stamp, on_disk, data in _cache_rows(name, query, rel, logger):
            try:
                if not isinstance(key, str):
                    raise TypeError
                url = urlsplit(key)
                if url.scheme not in ('https', 'http') or url.hostname not in _HOSTS:
                    continue
            except (ValueError, TypeError):
                logger(f'Life360 cache invalid request URL in {rel!r}, entry {entry}; entry skipped')
                continue
            response = {'entry': entry, 'path': url.path, 'request': url.hostname + url.path,
                        'cached': _time(stamp, 'Cached Time', cache=True), 'file': rel,
                        'body_file': '', 'body': None, 'status': '', 'bytes': ''}
            try:
                body, body_file, length = _body(database, data, on_disk, files)
                response.update(body=body, body_file=context.get_relative_path(body_file) if body_file else '',
                                status='JSON decoded', bytes=length)
            except (OSError, EOFError, ValueError, TypeError, UnicodeError, RecursionError, zlib.error) as error:
                # Error text is ours, not the JSON parser's payload-bearing message.
                reason = str(error) if type(error) is ValueError else type(error).__name__
                response['status'] = 'Body unavailable or invalid'
                logger(f'Life360 cache body unavailable/invalid in {rel!r}, entry {entry} '
                       f'({reason if reason in ("unsafe external-body reference", "external body outside this cache", "external body missing", "body missing", "unsupported body-storage flag", "body size or type unsupported", "expanded body exceeds limit", "body is not a JSON object or array", "nonfinite JSON") else type(error).__name__})')
            yield response


def _selected(context, endpoint):
    for response in _responses(context):
        if response['path'] != endpoint or response['body'] is None:
            continue
        if not isinstance(response['body'], dict):
            logfunc(f'Life360 cache expected an object in {response["file"]!r}, entry {response["entry"]}; response skipped')
            continue
        yield response, response['body']


def _items(body, response):
    data = body.get('data')
    if not isinstance(data, dict) or 'items' not in data:
        logfunc(f'Life360 cache missing data.items in {response["file"]!r}, entry {response["entry"]}; response skipped')
        return []
    return _array(data['items'], 'data.items')


def _coordinate(value, limit):
    if value is None or value == '':
        return ''
    try:
        number = float(value)
        if isinstance(value, bool) or not math.isfinite(number) or abs(number) > limit:
            raise ValueError
        return value
    except (TypeError, ValueError, OverflowError):
        logfunc('Life360 coordinate was invalid; coordinate left blank and source JSON retained')
        return ''


def _coordinates(item):
    return _coordinate(item.get('latitude'), 90), _coordinate(item.get('longitude'), 180)


def _provenance(response, record):
    return (response['request'], _json(record), response['file'], response['body_file'])


def _sources(context):
    files = get_life360_files(context, life360_logger(context, logfunc))
    caches = {Path(p).parent for p in files if Path(p).name == 'Cache.db'
              and Path(p).parent.name == 'com.life360.safetymap'
              and Path(p).parent.parent.name == 'Caches'}
    selected = [p for p in files if any(
        (Path(p).parent == cache and Path(p).name in ('Cache.db', 'Cache.db-wal'))
        or Path(p).parent == cache / 'fsCachedData' for cache in caches)]
    return '\n'.join(selected)


@artifact_processor
def life360CachedLocations(context):
    headers = (('Location Time', 'datetime'), ('First Observed', 'datetime'), ('Updated', 'datetime'),
               ('Cached Time', 'datetime'), 'Cache Entry ID', 'Device ID', 'Owner IDs', 'Latitude', 'Longitude',
               'Accuracy (as stored)', 'Speed (as stored)', 'Battery Level (as stored)', 'Battery Charging',
               'Wi-Fi Connected', 'In Transit', 'User Activity (as stored)', 'Provider', 'Device Type',
               'OS', 'App Version', 'Request Path', 'Record JSON', 'Source File', 'Body Source File')
    rows = []
    for response, body in _selected(context, '/v5/circles/devices/locations'):
        for item in _items(body, response):
            owners = _array(item.get('owners'), 'owners')
            rows.append(tuple(_time(item.get(k), k) for k in ('lastObserved', 'firstObserved', 'updated')) +
                        (response['cached'], response['entry'], _text(item.get('deviceId')),
                         _json([o.get('userId') for o in owners])) +
                        _coordinates(item) +
                        tuple(_text(item.get(k)) for k in ('accuracy', 'speed',
                            'batteryLevel', 'batteryCharging', 'wifiConnected', 'inTransit', 'userActivity',
                            'provider', 'type', 'os', 'appVersion')) + _provenance(response, item))
    return headers, rows, _sources(context)


@artifact_processor
def life360CachedDevices(context):
    headers = (('Modified', 'datetime'), ('Cached Time', 'datetime'), 'Cache Entry ID', 'Device ID',
               'Owner IDs', 'Name', 'Provider', 'Device Type', 'Hardware Model', 'OS', 'OS Version',
               'App Version', 'Request Path', 'Record JSON', 'Source File', 'Body Source File')
    rows = []
    for response, body in _selected(context, '/v5/circles/devices'):
        for item in _items(body, response):
            owners = _array(item.get('owners'), 'owners')
            details = item.get('typeData')
            if not isinstance(details, dict):
                if details is not None:
                    logfunc('Life360 cache typeData was not an object; fields left blank')
                details = {}
            rows.append((_time(item.get('modified'), 'modified'), response['cached'], response['entry'],
                         _text(item.get('id')), _json([o.get('userId') for o in owners])) +
                        tuple(_text(item.get(k)) for k in ('name', 'provider', 'type')) +
                        tuple(_text(details.get(k)) for k in ('hardwareModel', 'os', 'osVersion', 'appVersion')) +
                        _provenance(response, item))
    return headers, rows, _sources(context)


@artifact_processor
def life360CachedDeviceIssues(context):
    headers = (('Issue Start', 'datetime'), ('Cached Time', 'datetime'), 'Cache Entry ID', 'Device ID',
               'User ID', 'Issue Name (as stored)', 'Issue Value (as stored)', 'Request Path',
               'Record JSON', 'Source File', 'Body Source File')
    rows = []
    for response, body in _selected(context, '/v5/circles/devices/issues'):
        for item in _items(body, response):
            for issue in _array(item.get('issues'), 'issues'):
                rows.append((_time(issue.get('startTime'), 'startTime'), response['cached'], response['entry'],
                             _text(item.get('deviceId')), _text(item.get('userId')),
                             _text(issue.get('name')), _text(issue.get('value'))) +
                            _provenance(response, {'item': item, 'issue': issue}))
    return headers, rows, _sources(context)


@artifact_processor
def life360CachedCircles(context):
    headers = (('Created', 'datetime'), ('Cached Time', 'datetime'), 'Cache Entry ID', 'Circle ID', 'Name',
               'Request Path', 'Record JSON', 'Source File', 'Body Source File')
    rows = []
    for response, body in _selected(context, '/v4/circles'):
        if 'circles' not in body:
            logfunc('Life360 cache circles response lacked its circles array')
        for item in _array(body.get('circles'), 'circles'):
            rows.append((_time(item.get('createdAt'), 'createdAt', unix=True), response['cached'],
                         response['entry'], _text(item.get('id')), _text(item.get('name'))) +
                        _provenance(response, item))
    return headers, rows, _sources(context)


@artifact_processor
def life360CachedAccount(context):
    headers = (('Cached Time', 'datetime'), 'Cache Entry ID', 'User ID', 'Profile Created (as stored)',
               'First Name', 'Last Name', 'Email', 'Phone', 'Date of Birth (as stored)', 'Locale',
               'Language', 'Request Path', 'Record JSON', 'Source File', 'Body Source File')
    rows = []
    for response, body in _selected(context, '/v5/users/me'):
        rows.append((response['cached'], response['entry'], _text(body.get('id')), _text(body.get('created'))) +
                    tuple(_text(body.get(k)) for k in ('firstName', 'lastName', 'loginEmail',
                                                     'loginPhone', 'dob', 'locale', 'language')) +
                    _provenance(response, body))
    return headers, rows, _sources(context)


@artifact_processor
def life360CacheResponses(context):
    headers = (('Cached Time', 'datetime'), 'Cache Entry ID', 'Request Path', 'Body Status', 'Body Bytes',
               'Source File', 'Body Source File')
    rows = [(r['cached'], r['entry'], r['request'], r['status'], r['bytes'], r['file'], r['body_file'])
            for r in _responses(context)]
    return headers, rows, _sources(context)
