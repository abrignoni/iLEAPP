"""Life360 container validation and conversion of documented seconds-based timestamps."""
import os
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import get_plist_file_content, logfunc


def seconds_to_utc(value, epoch_year):
    """Known seconds must not be magnitude-scaled or truncated to whole seconds."""
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return ''
    try:
        return datetime(epoch_year, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=value)
    except (OverflowError, ValueError):
        logfunc('Life360 numeric timestamp outside the supported date range; rendered time left blank')
        return ''


def get_life360_files(context):
    """Return each physical file once, inside a positively identified Life360 container."""
    files = [str(path) for path in context.get_files_found()]
    roots = set()
    marker_name = '.com.apple.mobile_container_manager.metadata.plist'
    for path in files:
        if os.path.basename(path) != marker_name:
            continue
        metadata = get_plist_file_content(path)
        if isinstance(metadata, dict) and metadata.get('MCMMetadataIdentifier') == 'com.life360.safetymap':
            roots.add(os.path.normcase(os.path.realpath(os.path.dirname(path))))
    if not roots:
        if files:
            logfunc('Life360 app container marker not found; matching stores were skipped')
        return []
    accepted = {}
    for path in files:
        physical = os.path.normcase(os.path.realpath(path))
        for root in roots:
            try:
                belongs = os.path.commonpath((root, physical)) == root
            except ValueError:  # Different Windows drives cannot share a container.
                belongs = False
            if belongs:
                accepted.setdefault(physical, path)
                break
    return sorted(accepted.values())
