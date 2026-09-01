__artifacts_v2__ = {
    "augustLocks": {
        "name": "August - Locks",
        "description": "Locks recorded in the August app's network cache, with the lock name, "
                       "serial number, MAC address, owning house, firmware, battery level and "
                       "the lock status the service last returned.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "August",
        "notes": "Read from the app's NSURLCache at Library/Caches/com.august.yale.app/nscache, which "
                 "holds the JSON the August service returned. Each request carries a unique "
                 "clientSerial query value, so the same endpoint appears once per fetch with its own "
                 "cache timestamp; this artifact reports one row per lock, built from the newest "
                 "cached body, and gives the number of cached observations and the first and last "
                 "cache timestamps that carried it. Cache timestamps are UTC: on the tested sample a "
                 "response's cache timestamp equalled the Updated value inside its own body, which the "
                 "service writes with an explicit Z, to the second. Body timestamps are ISO 8601 "
                 "carrying their own UTC offset and are not inferred. Lock Status and Type are "
                 "reported as stored. Battery Level is the fraction the service returned. This "
                 "artifact does NOT recover a door operation log: the app's own lock log endpoint is "
                 "present in the cache 25 times and every one of those responses is an acknowledgement "
                 "carrying no event payload, so the cache records no open, close, lock or unlock "
                 "events. The lock's remote operate secret, HomeKit setup payload and pub/sub channel "
                 "are deliberately not reported. Created and Updated held the same value on every lock "
                 "in the tested sample, which is what the service returned for both fields rather than "
                 "a derivation that did not run.",
        "paths": ('*/Library/Caches/com.august.yale.app/nscache/Cache.db*',
                  '*/Library/Caches/com.august.yale.app/nscache/fsCachedData/*'),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "lock",
        "sample_data": {
            "falken_ios26": "iOS 26.2.1 | 2 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows; app installed and its cache staged, holding only app configuration and telemetry responses",
        },
    },
    "augustLockUsers": {
        "name": "August - Lock Users",
        "description": "People the service listed as having access to each lock, with the name "
                       "and access type recorded for each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "August",
        "notes": "Read from the users object inside each cached lock body, one row per lock and "
                 "user. User Type is the role string the service returned and is reported as "
                 "stored. Identifiers is the joined list of contact identifiers the service "
                 "held for that user, which on the tested sample are prefixed strings naming "
                 "the identifier kind. Presence in this list means the account was recorded as "
                 "having access to the lock at the time of the cached response; it is not "
                 "evidence that the person operated the lock, and the cache carries no "
                 "operation log to establish that.",
        "paths": ('*/Library/Caches/com.august.yale.app/nscache/Cache.db*',
                  '*/Library/Caches/com.august.yale.app/nscache/fsCachedData/*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "users",
        "sample_data": {
            "falken_ios26": "iOS 26.2.1 | 2 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows; app installed and its cache staged, holding only app configuration and telemetry responses",
        },
    },
    "augustOfflineKeys": {
        "name": "August - Lock Offline Keys",
        "description": "Offline access keys provisioned on each lock, with the user, the key "
                       "slot, the group the key sits in and the created and loaded timestamps.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "August",
        "notes": "Read from the OfflineKeys object inside each cached lock body. That object groups "
                 "keys under created, loaded, deleted and loadedhk, and the group name is reported in "
                 "its own column as stored; on the tested sample keys appeared in the created, deleted "
                 "and loadedhk groups. A row records that a key occupying the named slot was "
                 "provisioned for that user identifier, and a row in the deleted group records a key "
                 "the service listed as removed. The key material itself is present in the cached body "
                 "and is deliberately NOT reported; only its presence, slot and timestamps are. "
                 "Timestamps are ISO 8601 carrying an explicit UTC offset. Provisioning a key is not "
                 "evidence that the lock was operated with it. House Name holds one value on every row "
                 "in the tested sample because that device had a single house, and it is kept so a "
                 "device with more than one house shows which house each key belongs to. A key that "
                 "the service had moved into the deleted group is reported with its group as stored "
                 "and with Key Material Present false, which is how a revoked credential appears.",
        "paths": ('*/Library/Caches/com.august.yale.app/nscache/Cache.db*',
                  '*/Library/Caches/com.august.yale.app/nscache/fsCachedData/*'),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "key",
        "sample_data": {
            "falken_ios26": "iOS 26.2.1 | 7 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows; app installed and its cache staged, holding only app configuration and telemetry responses",
        },
    },
    "augustHouses": {
        "name": "August - Houses",
        "description": "Houses recorded in the app's network cache, with the number of users "
                       "the service listed for each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "August",
        "notes": "Read from the cached users/houses/mine and houses responses. User Count is "
                 "the number of entries in the users object where the service returned one, and "
                 "is blank where the response carried no users object rather than zero. The "
                 "house image fields the service returns are not reported.",
        "paths": ('*/Library/Caches/com.august.yale.app/nscache/Cache.db*',
                  '*/Library/Caches/com.august.yale.app/nscache/fsCachedData/*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "home",
        "sample_data": {
            "falken_ios26": "iOS 26.2.1 | 1 row",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows; app installed and its cache staged, holding only app configuration and telemetry responses",
        },
    },
    "augustAccount": {
        "name": "August - Account",
        "description": "The August account signed in to the app, with the email address, name "
                       "and phone number the service returned.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "August",
        "notes": "Read from the cached users/me response. The authentication tokens the same response "
                 "carries are deliberately not reported. Where several cached responses describe the "
                 "account, the newest is used and the observation count and cache window are given. "
                 "Locale was empty on the account in the tested sample; the column is kept because the "
                 "service defines the field and another account may carry it.",
        "paths": ('*/Library/Caches/com.august.yale.app/nscache/Cache.db*',
                  '*/Library/Caches/com.august.yale.app/nscache/fsCachedData/*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user",
        "sample_data": {
            "falken_ios26": "iOS 26.2.1 | 1 row",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows; app installed and its cache staged, holding only app configuration and telemetry responses",
        },
    },
    "augustSubscriptions": {
        "name": "August - Subscriptions",
        "description": "Service subscriptions recorded in the cache, tying a plan to a device, "
                       "lock, house and user with its created, updated and expiry timestamps.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "August",
        "notes": "Read from the cached subscriptions response, one row per subscription identifier "
                 "from the newest body that carried it. Plan Code, Status and Type are reported as "
                 "stored. Timestamps are ISO 8601 carrying an explicit UTC offset. Created At and "
                 "Updated At held the same value on every row in the tested sample, and Device Name "
                 "equalled Lock Name on every row because the subscribed device was the lock itself. "
                 "Both pairs are kept because a subscription for a different device type would "
                 "separate them.",
        "paths": ('*/Library/Caches/com.august.yale.app/nscache/Cache.db*',
                  '*/Library/Caches/com.august.yale.app/nscache/fsCachedData/*'),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "receipt",
        "sample_data": {
            "falken_ios26": "iOS 26.2.1 | 2 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows; app installed and its cache staged, holding only app configuration and telemetry responses",
        },
    },
    "augustBattery": {
        "name": "August - Lock Battery",
        "description": "Battery state the service last returned for each lock, including the "
                       "date the batteries were recorded as last changed.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "August",
        "notes": "Read from the cached per-lock battery responses and from the batteryInfo "
                 "object inside the cached lock bodies, one row per lock from the newest body. "
                 "Last Change Date is the date the service recorded the batteries as last "
                 "changed, which is a physical interaction with the lock. Projected Death Date "
                 "is a forward-looking estimate the service returned, not an observed event, "
                 "and on the tested sample it fell three months after the last change date. "
                 "Warning State is reported as stored. Timestamps are ISO 8601 carrying an "
                 "explicit UTC offset.",
        "paths": ('*/Library/Caches/com.august.yale.app/nscache/Cache.db*',
                  '*/Library/Caches/com.august.yale.app/nscache/fsCachedData/*'),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "battery",
        "sample_data": {
            "falken_ios26": "iOS 26.2.1 | 2 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows; app installed and its cache staged, holding only app configuration and telemetry responses",
        },
    },
    "augustLinkedApps": {
        "name": "August - Linked Apps",
        "description": "Third-party services the cache records as linked to the August account.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "August",
        "notes": "Read from the cached apps/mine response. A row records that the service "
                 "listed the named integration for this account. The partners catalogue the app "
                 "also caches lists every integration the vendor offers rather than the ones "
                 "this account uses, so it is deliberately not reported here.",
        "paths": ('*/Library/Caches/com.august.yale.app/nscache/Cache.db*',
                  '*/Library/Caches/com.august.yale.app/nscache/fsCachedData/*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "plug",
        "sample_data": {
            "falken_ios26": "iOS 26.2.1 | 1 row",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows; app installed and its cache staged, holding only app configuration and telemetry responses",
        },
    },
}

import gzip
import json
import os
import re
from datetime import datetime, timezone

from scripts.ilapfuncs import (
    artifact_processor,
    get_sqlite_db_records,
    logfunc,
)

_API_HOST = 'api-production.august.com'
_LOCK_DETAIL = re.compile(r'/locks/[0-9A-Fa-f]{16,}(?:\?|$)')
_ISO_FRACTION = re.compile(r'\.(\d+)')


def _iso_to_utc(value):
    """Parse an ISO 8601 string that carries its own offset, or '' when unusable.

    The service writes a trailing Z and three fractional digits. Python 3.10, which the
    runtime contract still covers, rejects the Z spelling and accepts only three or six
    fractional digits, so both are normalised before parsing rather than relying on a
    newer interpreter being more lenient.
    """
    if not value or not isinstance(value, str):
        return ''
    text = value.strip()
    if text.endswith(('Z', 'z')):
        text = text[:-1] + '+00:00'

    def _pad(match):
        digits = match.group(1)
        return '.' + (digits + '000000')[:6]

    text = _ISO_FRACTION.sub(_pad, text, count=1)
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        logfunc(f'August: could not parse the timestamp {value!r}')
        return ''
    if parsed.tzinfo is None:
        return ''
    return parsed.astimezone(timezone.utc)


def _cache_stamp_to_utc(value):
    """The cache's own time_stamp column, recorded as UTC text."""
    if not value:
        return ''
    try:
        return datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return ''


def _external_body_path(db_path, file_name):
    """An externally stored body sits in the fsCachedData folder beside its Cache.db."""
    if not file_name or os.sep in file_name or '/' in file_name:
        return None
    candidate = os.path.join(os.path.dirname(db_path), 'fsCachedData', file_name)
    return candidate if os.path.isfile(candidate) else None


def _decode_body(db_path, blob, on_filesystem):
    """The JSON a cached response carried, inline or resolved from fsCachedData."""
    if blob is None:
        return None
    if on_filesystem:
        name = blob.decode('utf-8', 'replace') if isinstance(blob, (bytes, bytearray)) \
            else str(blob)
        path = _external_body_path(db_path, name)
        if path is None:
            logfunc(f'August: external cached body {name!r} was not present in the extraction')
            return None
        try:
            with open(path, 'rb') as handle:
                blob = handle.read()
        except OSError as error:
            logfunc(f'August: could not read the external cached body {name!r}: {error}')
            return None
    if isinstance(blob, str):
        blob = blob.encode('utf-8', 'replace')
    if blob[:2] == b'\x1f\x8b':
        try:
            blob = gzip.decompress(blob)
        except (OSError, EOFError, gzip.BadGzipFile):
            return None
    try:
        return json.loads(blob.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


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


def _cached_responses(database):
    """Yield (endpoint path, cache timestamp, decoded body) for every August API response."""
    query = '''
    SELECT r.request_key, r.time_stamp, d.isDataOnFS, d.receiver_data
    FROM cfurl_cache_response AS r
    LEFT JOIN cfurl_cache_receiver_data AS d ON d.entry_ID = r.entry_ID
    ORDER BY r.time_stamp
    '''
    for record in get_sqlite_db_records(database, query):
        key = record[0] or ''
        if _API_HOST not in key:
            continue
        body = _decode_body(database, record[3], record[2])
        if body is None:
            continue
        path = re.sub(r'^https?://[^/]+', '', key).split('?')[0]
        yield path, record[1], body


def _newest_by(database, matcher):
    """{identity: (body, first cache stamp, last cache stamp, observations)} for one endpoint.

    Responses arrive oldest first, so the last body seen for an identity is the newest.
    """
    collected = {}
    for path, stamp, body in _cached_responses(database):
        for identity, item in matcher(path, body):
            if identity in collected:
                previous = collected[identity]
                collected[identity] = (item, previous[1], stamp, previous[3] + 1)
            else:
                collected[identity] = (item, stamp, stamp, 1)
    return collected


def _text(value):
    """A displayable value; a list is joined, a dictionary is not rendered."""
    if value is None:
        return ''
    if isinstance(value, bool):
        return value
    if isinstance(value, list):
        return ', '.join(str(item) for item in value)
    if isinstance(value, dict):
        return ''
    return value


def _lock_bodies(path, body):
    """Lock detail responses, keyed by lock identifier."""
    if not _LOCK_DETAIL.search(path + '?') or not isinstance(body, dict):
        return
    lock_id = body.get('LockID')
    if lock_id:
        yield lock_id, body


@artifact_processor
def augustLocks(context):
    data_headers = (
        ('Created', 'datetime'),
        ('Updated', 'datetime'),
        ('First Seen In Cache', 'datetime'),
        ('Last Seen In Cache', 'datetime'),
        'Lock Name',
        'House Name',
        'Serial Number',
        'MAC Address',
        'Lock Status (as stored)',
        'Battery Level',
        'Firmware Version',
        'Time Zone',
        'Type (as stored)',
        'SKU Number',
        'Calibrated',
        'Supports Entry Codes',
        'Access Schedules Allowed',
        'HomeKit Enabled',
        'Host Lock Manufacturer',
        'Host Lock Serial Number',
        'Lock ID',
        'House ID',
        'Cached Observations',
        'Source File',
    )
    data_list = []
    source_files = []

    for database in _cache_databases(context.get_files_found()):
        rows = 0
        for lock_id, (body, first, last, count) in _newest_by(database, _lock_bodies).items():
            rows += 1
            status = body.get('LockStatus')
            firmware = body.get('currentFirmwareVersion')
            host = body.get('hostLockInfo')
            data_list.append((
                _iso_to_utc(body.get('Created')),
                _iso_to_utc(body.get('Updated')),
                _cache_stamp_to_utc(first),
                _cache_stamp_to_utc(last),
                _text(body.get('LockName')),
                _text(body.get('HouseName')),
                _text(body.get('SerialNumber')),
                _text(body.get('macAddress')),
                _text(status.get('status')) if isinstance(status, dict) else '',
                _text(body.get('battery')),
                ', '.join(sorted(firmware)) if isinstance(firmware, dict) else '',
                _text(body.get('timeZone')),
                _text(body.get('Type')),
                _text(body.get('skuNumber')),
                _text(body.get('Calibrated')),
                _text(body.get('supportsEntryCodes')),
                _text(body.get('accessSchedulesAllowed')),
                _text(body.get('homeKitEnabled')),
                _text(host.get('manufacturer')) if isinstance(host, dict) else '',
                _text(host.get('serialNumber')) if isinstance(host, dict) else '',
                lock_id,
                _text(body.get('HouseID')),
                count,
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)


def _lock_user_entries(path, body):
    """One identity per (lock, user), so a user removed later is still reported."""
    if not _LOCK_DETAIL.search(path + '?') or not isinstance(body, dict):
        return
    lock_id = body.get('LockID')
    users = body.get('users')
    if not lock_id or not isinstance(users, dict):
        return
    for user_id, user in users.items():
        if isinstance(user, dict):
            yield (lock_id, user_id), dict(user, _lock=body)


def _offline_key_entries(path, body):
    """One identity per provisioned key, so a key seen only in an older body survives.

    The service moves a key between the created, loaded, deleted and loadedhk groups as
    its state changes, so identity deliberately excludes the group and the reported group
    is the one from the most recent cached body that carried the key.
    """
    if not _LOCK_DETAIL.search(path + '?') or not isinstance(body, dict):
        return
    lock_id = body.get('LockID')
    groups = body.get('OfflineKeys')
    if not lock_id or not isinstance(groups, dict):
        return
    for group, entries in groups.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            identity = (lock_id, entry.get('slot'), entry.get('UserID'), entry.get('created'))
            yield identity, dict(entry, _group=group, _lock=body)


@artifact_processor
def augustLockUsers(context):
    data_headers = (
        ('First Seen In Cache', 'datetime'),
        ('Last Seen In Cache', 'datetime'),
        'Lock Name',
        'House Name',
        'First Name',
        'Last Name',
        'User Type (as stored)',
        'Identifiers',
        'User ID',
        'Lock ID',
        'Cached Observations',
        'Source File',
    )
    data_list = []
    source_files = []

    for database in _cache_databases(context.get_files_found()):
        rows = 0
        collected = _newest_by(database, _lock_user_entries)
        for (lock_id, user_id), (user, first, last, count) in collected.items():
            rows += 1
            lock = user.get('_lock') or {}
            data_list.append((
                _cache_stamp_to_utc(first),
                _cache_stamp_to_utc(last),
                _text(lock.get('LockName')),
                _text(lock.get('HouseName')),
                _text(user.get('FirstName')),
                _text(user.get('LastName')),
                _text(user.get('UserType')),
                _text(user.get('identifiers')),
                user_id,
                lock_id,
                count,
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def augustOfflineKeys(context):
    data_headers = (
        ('Created', 'datetime'),
        ('Loaded', 'datetime'),
        ('First Seen In Cache', 'datetime'),
        ('Last Seen In Cache', 'datetime'),
        'Group (as stored)',
        'Slot',
        'Lock Name',
        'House Name',
        'User ID',
        'Key Material Present',
        'Lock ID',
        'Cached Observations',
        'Source File',
    )
    data_list = []
    source_files = []

    for database in _cache_databases(context.get_files_found()):
        rows = 0
        collected = _newest_by(database, _offline_key_entries)
        for identity, (entry, first, last, count) in collected.items():
            rows += 1
            lock = entry.get('_lock') or {}
            data_list.append((
                _iso_to_utc(entry.get('created')),
                _iso_to_utc(entry.get('loaded')),
                _cache_stamp_to_utc(first),
                _cache_stamp_to_utc(last),
                entry.get('_group'),
                _text(entry.get('slot')),
                _text(lock.get('LockName')),
                _text(lock.get('HouseName')),
                _text(entry.get('UserID')),
                bool(entry.get('key')),
                identity[0],
                count,
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)


def _house_bodies(path, body):
    """House responses, from either the list or the single-house endpoint."""
    if path not in ('/users/houses/mine', '/houses'):
        return
    items = body if isinstance(body, list) else [body]
    for item in items:
        if isinstance(item, dict) and item.get('HouseID'):
            yield item['HouseID'], item


@artifact_processor
def augustHouses(context):
    data_headers = (
        ('First Seen In Cache', 'datetime'),
        ('Last Seen In Cache', 'datetime'),
        'House Name',
        'User Count',
        'Type (as stored)',
        'House ID',
        'Cached Observations',
        'Source File',
    )
    data_list = []
    source_files = []

    for database in _cache_databases(context.get_files_found()):
        rows = 0
        for house_id, (body, first, last, count) in _newest_by(database, _house_bodies).items():
            rows += 1
            users = body.get('users')
            data_list.append((
                _cache_stamp_to_utc(first),
                _cache_stamp_to_utc(last),
                _text(body.get('HouseName')),
                len(users) if isinstance(users, dict) else '',
                _text(body.get('type')),
                house_id,
                count,
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)


def _account_bodies(path, body):
    if path == '/users/me' and isinstance(body, dict) and body.get('UserID'):
        yield body['UserID'], body


@artifact_processor
def augustAccount(context):
    data_headers = (
        ('First Seen In Cache', 'datetime'),
        ('Last Seen In Cache', 'datetime'),
        'Email',
        'First Name',
        'Last Name',
        'Phone Number',
        'Locale',
        'User ID',
        'Cached Observations',
        'Source File',
    )
    data_list = []
    source_files = []

    for database in _cache_databases(context.get_files_found()):
        rows = 0
        for user_id, (body, first, last, count) in _newest_by(database,
                                                              _account_bodies).items():
            rows += 1
            data_list.append((
                _cache_stamp_to_utc(first),
                _cache_stamp_to_utc(last),
                _text(body.get('Email')),
                _text(body.get('FirstName')),
                _text(body.get('LastName')),
                _text(body.get('PhoneNo')),
                _text(body.get('locale')),
                user_id,
                count,
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)


def _subscription_bodies(path, body):
    if path != '/subscriptions':
        return
    items = body if isinstance(body, list) else [body]
    for item in items:
        if isinstance(item, dict) and item.get('subscriptionID'):
            yield item['subscriptionID'], item


@artifact_processor
def augustSubscriptions(context):
    data_headers = (
        ('Created At', 'datetime'),
        ('Updated At', 'datetime'),
        ('Expires At', 'datetime'),
        'Plan Code (as stored)',
        'Status (as stored)',
        'Type (as stored)',
        'Device Name',
        'Device Type (as stored)',
        'Lock Name',
        'House Name',
        'User ID',
        'Device ID',
        'Subscription ID',
        'Source File',
    )
    data_list = []
    source_files = []

    for database in _cache_databases(context.get_files_found()):
        rows = 0
        for sub_id, (body, _f, _l, _c) in _newest_by(database, _subscription_bodies).items():
            rows += 1
            data_list.append((
                _iso_to_utc(body.get('createdAt')),
                _iso_to_utc(body.get('updatedAt')),
                _iso_to_utc(body.get('expiresAt')),
                _text(body.get('planCode')),
                _text(body.get('status')),
                _text(body.get('type')),
                _text(body.get('deviceName')),
                _text(body.get('deviceType')),
                _text(body.get('lockName')),
                _text(body.get('houseName')),
                _text(body.get('userID')),
                _text(body.get('deviceID')),
                sub_id,
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)


_BATTERY_ENDPOINT = re.compile(r'/locks/([0-9A-Fa-f]{16,})/battery$')


def _battery_bodies(path, body):
    """Battery state, from the per-lock battery endpoint and from the lock body."""
    match = _BATTERY_ENDPOINT.search(path)
    if match and isinstance(body, dict):
        yield match.group(1), body
        return
    if _LOCK_DETAIL.search(path + '?') and isinstance(body, dict):
        info = body.get('batteryInfo')
        if isinstance(info, dict) and body.get('LockID'):
            yield body['LockID'], dict(info, LockName=body.get('LockName'))


@artifact_processor
def augustBattery(context):
    data_headers = (
        ('Last Change Date', 'datetime'),
        ('Info Updated Date', 'datetime'),
        ('Projected Death Date', 'datetime'),
        'Lock Name',
        'Level',
        'Last Change Voltage',
        'Warning State (as stored)',
        'Lock ID',
        'Cached Observations',
        'Source File',
    )
    data_list = []
    source_files = []

    for database in _cache_databases(context.get_files_found()):
        rows = 0
        for lock_id, (body, _f, _l, count) in _newest_by(database, _battery_bodies).items():
            rows += 1
            data_list.append((
                _iso_to_utc(body.get('lastChangeDate')),
                _iso_to_utc(body.get('infoUpdatedDate')),
                _iso_to_utc(body.get('deathDate')),
                _text(body.get('LockName')),
                _text(body.get('level')),
                _text(body.get('lastChangeVoltage')),
                _text(body.get('warningState')),
                lock_id,
                count,
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)


def _linked_app_bodies(path, body):
    if path != '/apps/mine':
        return
    items = body if isinstance(body, list) else [body]
    for item in items:
        if isinstance(item, dict) and item.get('id'):
            yield item['id'], item


@artifact_processor
def augustLinkedApps(context):
    data_headers = (
        ('First Seen In Cache', 'datetime'),
        ('Last Seen In Cache', 'datetime'),
        'Name',
        'Type (as stored)',
        'Description',
        'Partner ID',
        'App ID',
        'Source File',
    )
    data_list = []
    source_files = []

    for database in _cache_databases(context.get_files_found()):
        rows = 0
        for app_id, (body, first, last, _c) in _newest_by(database,
                                                          _linked_app_bodies).items():
            rows += 1
            data_list.append((
                _cache_stamp_to_utc(first),
                _cache_stamp_to_utc(last),
                _text(body.get('name')),
                _text(body.get('type')),
                _text(body.get('description')),
                _text(body.get('partnerID')),
                app_id,
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)
