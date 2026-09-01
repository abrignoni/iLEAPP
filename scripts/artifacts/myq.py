__artifacts_v2__ = {
    "myqDeviceHistory": {
        "name": "myQ - Device History",
        "description": "Garage door and opener events the myQ service returned, with the "
                       "event, the device it happened on and the account the service "
                       "attributed it to.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "myQ",
        "notes": "Read from the app's NSURLCache at Library/Caches/com.myliftmaster.myq, from the "
                 "cached accounthistory.myq-cloud.com deviceHistory response. Event timestamps are ISO "
                 "8601 carrying an explicit UTC offset. Device Event and Event Type are the strings "
                 "the service returned and are reported as stored. Attributed To Name and Attributed "
                 "To Source come from the event_by object the service returns, and both were absent on "
                 "some events in the tested sample, so an empty value means the service attributed the "
                 "event to nobody rather than that it was unattributed by the device. An event records "
                 "that the service logged a door state change; it does not establish who was "
                 "physically present. The local database the app keeps beside this cache has an "
                 "ApiEvent table, but it was empty on the tested sample and the events are recovered "
                 "from the cached response instead. The app's data container was present on 1 of the "
                 "26 registered iOS corpora swept for it, so every count recorded here comes from that "
                 "one extraction.",
        "paths": ('*/Library/Caches/com.myliftmaster.myq/Cache.db*',
                  '*/Library/Caches/com.myliftmaster.myq/fsCachedData/*'),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "door",
        "sample_data": {
            "falken_ios26": "iOS 26.2.1 | 27 rows",
        },
    },
    "myqDevices": {
        "name": "myQ - Devices",
        "description": "Door openers and gateways registered to the account, with the serial "
                       "number, model, current door state and the cycle counts recorded for "
                       "each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "myQ",
        "notes": "Read from the cached devices.myq-cloud.com Devices response, which returns both door "
                 "openers and gateways, so a column belonging to one device family is empty on rows of "
                 "the other; Door State and the cycle counts apply to openers and Firmware Version and "
                 "the Wi-Fi signal fields apply to gateways. Created Date is returned without a zone "
                 "by this endpoint and with an explicit +00:00 offset by the gateways endpoint for the "
                 "same device, and the two agreed to the millisecond on the tested sample, so the "
                 "value is read as UTC on that evidence rather than by assumption. The remaining "
                 "timestamps carry an explicit offset. Absolute Cycle Count is the lifetime count the "
                 "service holds for the opener; it was zero on the tested sample. Door State is the "
                 "state at the time of the cached response, not a history. Device Type and Device "
                 "Model held the same value on every row in the tested sample, and Absolute Cycle "
                 "Count equalled Service Cycle Count because both were zero on the opener and absent "
                 "on the gateway. Both pairs are kept because the service defines them separately and "
                 "a device with cycles recorded would separate them. The app's data container was "
                 "present on 1 of the 26 registered iOS corpora swept for it, so every count recorded "
                 "here comes from that one extraction.",
        "paths": ('*/Library/Caches/com.myliftmaster.myq/Cache.db*',
                  '*/Library/Caches/com.myliftmaster.myq/fsCachedData/*'),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "garage",
        "sample_data": {
            "falken_ios26": "iOS 26.2.1 | 2 rows",
        },
    },
    "myqAccountUsers": {
        "name": "myQ - Account Users",
        "description": "People the service listed as having access to the myQ account, with "
                       "the role and the date the access was created.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "myQ",
        "notes": "Read from the cached guestaccess.myq-cloud.com account users response. Role is "
                 "reported as stored. A row records that the service listed the account as having "
                 "access when the response was cached; it is not evidence that the person operated a "
                 "door, which the Device History artifact reports separately. Created Date carries an "
                 "explicit UTC offset. The app's data container was present on 1 of the 26 registered "
                 "iOS corpora swept for it, so every count recorded here comes from that one "
                 "extraction.",
        "paths": ('*/Library/Caches/com.myliftmaster.myq/Cache.db*',
                  '*/Library/Caches/com.myliftmaster.myq/fsCachedData/*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "users",
        "sample_data": {
            "falken_ios26": "iOS 26.2.1 | 1 row",
        },
    },
    "myqProfile": {
        "name": "myQ - Account Profile",
        "description": "The myQ account signed in to the app, with the email address and the "
                       "postal address fields the service returned.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "myQ",
        "notes": "Read from the cached profiles.myq-cloud.com profile response. The service returns a "
                 "postal code and country rather than a street address, and only those are reported. "
                 "Linked external identity providers are reported by name and count only. The app's "
                 "data container was present on 1 of the 26 registered iOS corpora swept for it, so "
                 "every count recorded here comes from that one extraction.",
        "paths": ('*/Library/Caches/com.myliftmaster.myq/Cache.db*',
                  '*/Library/Caches/com.myliftmaster.myq/fsCachedData/*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user",
        "sample_data": {
            "falken_ios26": "iOS 26.2.1 | 1 row",
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

_ISO_FRACTION = re.compile(r'\.(\d+)')


def _iso_to_utc(value, assume_utc=False):
    """Parse an ISO 8601 string, or '' when unusable.

    The service writes a trailing Z, an explicit offset, or, from the Devices endpoint,
    no zone at all. Python 3.10 is still in the runtime contract and rejects the Z spelling
    and any fraction that is not three or six digits, so both are normalised rather than
    relying on a newer interpreter. A value with no zone is only accepted when the caller
    passes assume_utc, which is set on the one endpoint where the same instant was observed
    with an explicit +00:00 offset from a sibling endpoint.
    """
    if not value or not isinstance(value, str):
        return ''
    text = value.strip()
    if text.endswith(('Z', 'z')):
        text = text[:-1] + '+00:00'

    def _pad(match):
        return '.' + (match.group(1) + '000000')[:6]

    text = _ISO_FRACTION.sub(_pad, text, count=1)
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        logfunc(f'myQ: could not parse the timestamp {value!r}')
        return ''
    if parsed.tzinfo is None:
        if not assume_utc:
            return ''
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


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
            logfunc(f'myQ: external cached body {name!r} was not present in the extraction')
            return None
        try:
            with open(path, 'rb') as handle:
                blob = handle.read()
        except OSError as error:
            logfunc(f'myQ: could not read the external cached body {name!r}: {error}')
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
    """The app's own NSURLCache databases, sidecars and cached body files excluded."""
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


def _cached_bodies(database, host_fragment, path_fragment):
    """Yield the newest decoded body for each cached response matching host and path."""
    query = '''
    SELECT r.request_key, r.time_stamp, d.isDataOnFS, d.receiver_data
    FROM cfurl_cache_response AS r
    LEFT JOIN cfurl_cache_receiver_data AS d ON d.entry_ID = r.entry_ID
    ORDER BY r.time_stamp
    '''
    for record in get_sqlite_db_records(database, query):
        key = record[0] or ''
        if host_fragment not in key or path_fragment not in key:
            continue
        body = _decode_body(database, record[3], record[2])
        if body is not None:
            yield body


def _newest(database, host_fragment, path_fragment):
    """The last, and so newest, body matching the endpoint, or None."""
    latest = None
    for body in _cached_bodies(database, host_fragment, path_fragment):
        latest = body
    return latest


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


@artifact_processor
def myqDeviceHistory(context):
    data_headers = (
        ('Event Timestamp', 'datetime'),
        'Device Event (as stored)',
        'Device Name',
        'Device Type (as stored)',
        'Event Type (as stored)',
        'Attributed To Name',
        'Attributed To Source (as stored)',
        'Device Serial Number',
        'Attributed To User ID',
        'Event ID',
        'Source File',
    )
    data_list = []
    source_files = []

    for database in _cache_databases(context.get_files_found()):
        rows = 0
        seen = set()
        for body in _cached_bodies(database, 'accounthistory.myq-cloud.com', 'deviceHistory'):
            events = body.get('device_history') if isinstance(body, dict) else None
            if not isinstance(events, list):
                continue
            for event in events:
                if not isinstance(event, dict):
                    continue
                identity = event.get('id')
                if identity in seen:
                    continue
                seen.add(identity)
                rows += 1
                detail = event.get('event') if isinstance(event.get('event'), dict) else {}
                actor = event.get('event_by') if isinstance(event.get('event_by'), dict) else {}
                data_list.append((
                    _iso_to_utc(event.get('event_timestamp')),
                    _text(detail.get('device_event')),
                    _text(detail.get('device_name')),
                    _text(detail.get('device_type')),
                    _text(event.get('event_type')),
                    _text(actor.get('name')),
                    _text(actor.get('source')),
                    _text(detail.get('device_serial_number')),
                    _text(actor.get('user_id')),
                    _text(identity),
                    context.get_relative_path(database),
                ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def myqDevices(context):
    data_headers = (
        ('Created Date', 'datetime'),
        ('Last Update', 'datetime'),
        ('Last Status', 'datetime'),
        'Device Name',
        'Device Family (as stored)',
        'Device Type (as stored)',
        'Device Model (as stored)',
        'Serial Number',
        'Door State (as stored)',
        'Absolute Cycle Count',
        'Service Cycle Count',
        'Online',
        'Firmware Version',
        'HomeKit Enabled',
        'Wi-Fi Signal Strength',
        'Platform (as stored)',
        'Parent Device ID',
        'Source File',
    )
    data_list = []
    source_files = []

    for database in _cache_databases(context.get_files_found()):
        rows = 0
        body = _newest(database, 'devices.myq-cloud.com', '/Devices')
        items = body.get('items') if isinstance(body, dict) else None
        for item in items or []:
            if not isinstance(item, dict):
                continue
            rows += 1
            state = item.get('state') if isinstance(item.get('state'), dict) else {}
            data_list.append((
                # This endpoint returns the created date with no zone, and the gateways
                # endpoint returns the same instant for the same device with +00:00.
                _iso_to_utc(item.get('created_date'), assume_utc=True),
                _iso_to_utc(state.get('last_update')),
                _iso_to_utc(state.get('last_status')),
                _text(item.get('name')),
                _text(item.get('device_family')),
                _text(item.get('device_type')),
                _text(item.get('device_model')),
                _text(item.get('serial_number')),
                _text(state.get('door_state')),
                _text(state.get('absolute_cycle_count')),
                _text(state.get('service_cycle_count')),
                _text(state.get('online')),
                _text(state.get('firmware_version')),
                _text(state.get('homekit_enabled')),
                _text(state.get('wifi_signal_strength')),
                _text(item.get('device_platform')),
                _text(item.get('parent_device_id')),
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def myqAccountUsers(context):
    data_headers = (
        ('Created Date', 'datetime'),
        'First Name',
        'Last Name',
        'Email',
        'Role (as stored)',
        'User ID',
        'Source File',
    )
    data_list = []
    source_files = []

    for database in _cache_databases(context.get_files_found()):
        rows = 0
        body = _newest(database, 'guestaccess.myq-cloud.com', '/users')
        users = body.get('account_users') if isinstance(body, dict) else None
        for user in users or []:
            if not isinstance(user, dict):
                continue
            rows += 1
            data_list.append((
                _iso_to_utc(user.get('created_date')),
                _text(user.get('first_name')),
                _text(user.get('last_name')),
                _text(user.get('email')),
                _text(user.get('role')),
                _text(user.get('user_id')),
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def myqProfile(context):
    data_headers = (
        'Email',
        'Postal Code',
        'Country',
        'Culture Code',
        'Diagnostics Opt In',
        'External Identity Providers',
        'Analytics ID',
        'Source File',
    )
    data_list = []
    source_files = []

    for database in _cache_databases(context.get_files_found()):
        rows = 0
        body = _newest(database, 'profiles.myq-cloud.com', '/my/profile')
        if isinstance(body, dict):
            rows += 1
            address = body.get('address') if isinstance(body.get('address'), dict) else {}
            country = address.get('country') if isinstance(address.get('country'), dict) else {}
            providers = body.get('external_identities')
            names = []
            if isinstance(providers, list):
                for provider in providers:
                    if isinstance(provider, dict) and provider.get('provider'):
                        names.append(str(provider['provider']))
            data_list.append((
                _text(body.get('email')),
                _text(address.get('postal_code')),
                _text(country.get('name')),
                _text(body.get('culture_code')),
                _text(body.get('diagnostics_opt_in')),
                ', '.join(names),
                _text(body.get('analytics_id')),
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)
