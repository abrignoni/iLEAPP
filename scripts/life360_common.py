"""Life360 container validation and conversion of documented seconds-based timestamps."""
import os
import sqlite3
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import get_plist_file_content, get_sqlite_db_records, logfunc


def seconds_to_utc(value, epoch_year):
    """Known seconds must not be magnitude-scaled or truncated to whole seconds."""
    if value is None or value == '':
        return ''
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        logfunc('Life360 timestamp was not numeric seconds; rendered time left blank')
        return ''
    try:
        return datetime(epoch_year, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=value)
    except (OverflowError, ValueError):
        logfunc('Life360 numeric timestamp outside the supported date range; rendered time left blank')
        return ''


def columns_first(headers, rows, first):
    """Move the named columns to the front in the given order; the rest keep their order."""
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    order = [names.index(name) for name in first]
    order += [i for i in range(len(names)) if i not in order]
    return tuple(headers[i] for i in order), [tuple(row[i] for i in order) for row in rows]


def stored_dict(value, label):
    """Keep an optional object; report a present value with the wrong shape."""
    if isinstance(value, dict):
        return value
    if value is not None:
        logfunc(f'Life360 {label} was not an object; its fields were skipped')
    return {}


def stored_list(value, label):
    """Keep an optional array; report a present value with the wrong shape."""
    if isinstance(value, list):
        return value
    if value is not None:
        logfunc(f'Life360 {label} was not an array; its elements were skipped')
    return []


def read_life360_rows(path, query, label):
    """Keep a deferred SQLite read failure local to its source file; label is its extraction-relative path."""
    try:
        records = get_sqlite_db_records(path, query)
        try:
            yield from records
        finally:
            close = getattr(records, 'close', None)
            if close is not None:
                close()
    except sqlite3.Error as error:
        logfunc(f'Life360 SQLite read failed in {label!r} ({type(error).__name__}); '
                'remaining rows skipped, earlier rows retained')


def get_life360_files(context):
    """Validate relevant container markers and log every excluded matching file."""
    files = [str(path) for path in context.get_files_found()]
    marker_name = '.com.apple.mobile_container_manager.metadata.plist'
    markers = {}
    candidates = {}
    for path in files:
        physical = os.path.normcase(os.path.realpath(path))
        if os.path.basename(path) == marker_name:
            markers.setdefault(os.path.dirname(physical), path)
        else:
            candidates.setdefault(physical, path)
    identifiers = {}
    accepted = {}
    for physical, path in sorted(candidates.items()):
        # The nearest marker owns this file; a nested foreign container cannot inherit
        # an accepted ancestor. Walking parents also keeps Windows drives separate.
        root = os.path.dirname(physical)
        while root not in markers:
            parent = os.path.dirname(root)
            if parent == root:
                root = None
                break
            root = parent
        if root is None:
            reason = 'container marker missing'
        else:
            if root not in identifiers:
                metadata = get_plist_file_content(markers[root])
                identifiers[root] = metadata.get('MCMMetadataIdentifier') if isinstance(metadata, dict) else None
            identifier = identifiers[root]
            if identifier == 'com.life360.safetymap':
                accepted[physical] = path
                continue
            if not isinstance(identifier, str) or not identifier:
                reason = 'container marker unreadable or missing a valid MCMMetadataIdentifier'
            else:
                reason = f'unsupported MCMMetadataIdentifier {identifier!r}'
        relative = context.get_relative_path(path)
        logfunc(f'Life360 skipped matching file {relative!r}: {reason}')
    return sorted(accepted.values())
