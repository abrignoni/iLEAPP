__artifacts_v2__ = {
    'mixpanel_events': {
        'name': 'Mixpanel - Events',
        'description': 'Queued analytics events and app-defined properties from iOS Mixpanel stores.',
        'author': '@CyberMike81, OpenAI Codex',
        'creation_date': '2026-10-22',
        'last_update_date': '2026-10-22',
        'requirements': 'none',
        'category': 'Mixpanel',
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'activity',
        'paths': ('*/Library/*_MPDB.sqlite*',
                  '*/.com.apple.mobile_container_manager.metadata.plist'),
        'notes': 'Event Time is properties.time; Time Divisor records the seconds/milliseconds '
                 'conversion. Zero dates are blank and Raw Event Time is retained. Bundle ID '
                 'uses consistent event/session IDs, otherwise container metadata; conflicts '
                 'remain visible. Session metrics are app-defined; Event JSON retains all '
                 'properties. Processed queue batches may be deleted, so this is not a complete '
                 'activity history.',
    },
}

import json
import math
import os
import plistlib
import re
import sqlite3
from datetime import datetime, timezone
from xml.parsers.expat import ExpatError

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


def _container(path):
    match = re.search(r'(.*/Containers/Data/Application/[^/]+)/', str(path).replace('\\', '/'))
    return match.group(1) if match else ''


def _container_bundles(context):
    bundles = {}
    for path in sorted({str(p) for p in context.get_files_found()}):
        if os.path.basename(path) != '.com.apple.mobile_container_manager.metadata.plist':
            continue
        container = _container(path)
        if not container or path.replace('\\', '/').rsplit('/', 1)[0] != container:
            continue
        try:
            with open(path, 'rb') as handle:
                metadata = plistlib.load(handle)
        except (OSError, ValueError, TypeError, OverflowError, plistlib.InvalidFileException, ExpatError):
            logfunc(f'Mixpanel: unreadable container metadata; file={context.get_relative_path(path)}')
            continue
        bundle = metadata.get('MCMMetadataIdentifier') if isinstance(metadata, dict) else None
        if isinstance(bundle, str) and bundle.strip():
            bundles[container] = bundle
    return bundles


def _seconds(value, divisor=1):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value == 0:
        return ''
    try:
        if isinstance(value, float) and not math.isfinite(value):
            return ''
        return datetime.fromtimestamp(value / divisor, timezone.utc)
    except (ValueError, OverflowError, OSError):
        return ''


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def _report_scalar(value):
    # Keep huge integers exact through SQLite's binder; the typed source stays in Event JSON.
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int) and not -(2**63) <= value < 2**63:
        return str(value)
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, (dict, list)):
        return _json(value)
    return value


def _event_time(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return '', None
    if isinstance(value, float) and not math.isfinite(value):
        return '', None
    # This exposed unit heuristic describes modern events; queue time is never a substitute.
    divisor = 1000 if abs(value) >= 100_000_000_000 else 1
    return _seconds(value, divisor), divisor


def _events(db, display_path):
    tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
              if re.fullmatch(r'mixpanel_[A-Za-z0-9_]+_events', r[0])]
    for table in tables:
        emitted = 0
        try:
            for row in db.execute('SELECT id,data,time FROM "' + table + '" ORDER BY id'):
                emitted += 1
                yield table, row
        except sqlite3.Error:
            logfunc(f'Mixpanel: unsupported or unreadable events table; table={table}; '
                    f'rows emitted={emitted}; file={display_path}')


def _bundle_identity(outer, inner, container):
    candidates = [v for v in (outer, inner) if isinstance(v, str) and v.strip()]
    invalid = any(v is not None and v != '' and not isinstance(v, str) for v in (outer, inner))
    if len(set(candidates)) > 1:
        return None, 'Conflicting event/session identifiers', 'Conflict: event and session bundle IDs differ'
    if candidates:
        bundle = candidates[0]
        origin = ('Event and session properties' if len(candidates) == 2 else
                  'Event properties' if isinstance(outer, str) and outer.strip() else 'Session properties')
        status = ('Conflict: event and container bundle IDs differ' if container and container != bundle else
                  'Container metadata matches' if container else 'Container metadata unavailable')
        if invalid:
            status += '; another event identifier has an unsupported type'
        return bundle, origin, status
    if container:
        return container, 'Container metadata', ('Event identifier has an unsupported type' if invalid else
                                                'No event/session bundle ID')
    return None, 'Unavailable', ('Event identifier has an unsupported type' if invalid else
                                 'No event/session or container bundle ID')


@artifact_processor
def mixpanel_events(context):
    rows = []
    source = ''
    containers = _container_bundles(context)
    for path in sorted({str(p) for p in context.get_files_found()}):
        if not path.endswith('_MPDB.sqlite') or not os.path.isfile(path):
            continue
        display_path = context.get_relative_path(path)
        db = open_sqlite_db_readonly(path)
        if db is None:
            logfunc(f'Mixpanel: could not open events database; file={display_path}')
            continue
        try:
            for table, (rowid, raw, queue_time) in _events(db, display_path):
                location = f'file={display_path}; table={table}; row={rowid}'
                try:
                    event = json.loads(raw)
                except (ValueError, TypeError, UnicodeError):
                    logfunc(f'Mixpanel: skipped malformed event JSON; {location}')
                    continue
                if not isinstance(event, dict) or not isinstance(event.get('properties'), dict):
                    logfunc(f'Mixpanel: unsupported event/properties shape; {location}')
                    continue
                props = event['properties']
                session = props.get('sessionParams')
                session = session if isinstance(session, dict) else {}
                outer, inner = props.get('bundleId'), session.get('bundleId')
                container = containers.get(_container(path))
                bundle, origin, status = _bundle_identity(outer, inner, container)
                stamp, divisor = _event_time(props.get('time'))
                if stamp == '' and props.get('time') not in (None, 0):
                    logfunc(f'Mixpanel: invalid event time; raw retained; {location}')
                spent = session.get('timeSpent')
                spent = spent if isinstance(spent, dict) else {}
                source = source or path
                rows.append(tuple(_report_scalar(value) for value in (
                    stamp, event.get('event'), bundle, origin, status, outer, inner, container,
                    rowid, props.get('time'), divisor, queue_time, props.get('$ae_session_length'),
                    session.get('itemsViewed'), session.get('albumsViewed'),
                    spent.get('thumbnails'), spent.get('gallery'),
                    props.get('$app_version_string', props.get('$app_version')), props.get('$os_version'),
                    props.get('mp_lib'), props.get('$lib_version'), table, _json(event), display_path)))
        except sqlite3.Error:
            logfunc(f'Mixpanel: unreadable events database; file={display_path}')
        finally:
            db.close()
    # SDK 5.0.8 removes processed batches after flush (including API-rejected items):
    # https://github.com/mixpanel/mixpanel-iphone/blob/v5.0.8/Sources/MPNetwork.m#L89-L115
    return (('Event Time', 'datetime'), 'Event', 'Bundle ID', 'Bundle ID Source', 'Bundle ID Status',
            'Event Bundle ID', 'Session Bundle ID', 'Container Bundle ID', 'Event Row ID',
            'Raw Event Time', 'Time Divisor', 'Raw Queue Time', 'Session Length',
            'Items Viewed', 'Albums Viewed', 'Thumbnail Time', 'Gallery Time',
            'App Version', 'OS Version', 'SDK Library', 'SDK Version', 'Source Table',
            'Event JSON', 'Source File'), rows, source
