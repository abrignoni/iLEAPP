"""Life360 container validation and conversion of documented seconds-based timestamps."""
import os
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import get_plist_file_content, logfunc


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
