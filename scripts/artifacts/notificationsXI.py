__artifacts_v2__ = {
    "notificationsXI": {
        "name": "Notifications (iOS 11 PushStore)",
        "description": "Delivered notifications parsed from iOS <= 11 SpringBoard PushStore files",
        "author": "",
        "version": "2.0",
        "date": "2026-06-23",
        "requirements": "none",
        "category": "Notifications",
        "notes": "Best-effort structured rewrite of the old HTML-triage version: pulls the "
                 "AppNotification* fields out of the PushStore NSKeyedArchiver into a flat table "
                 "matching the iOS 12 'Notifications' artifact. Field extraction should be validated "
                 "against an iOS 11 PushStore sample. Times assumed UTC.",
        "paths": ('*PushStore*',),
        "output_types": "standard",
        "artifact_icon": "bell"
    }
}

import glob
import os
from datetime import datetime, timezone

import nska_deserialize as nd

from scripts.ilapfuncs import artifact_processor

_FIELDS = ('AppNotificationCreationDate', 'AppNotificationTitle', 'AppNotificationSubtitle',
           'AppNotificationMessage')


def _walk_notifications(obj, seen=None):
    """Recursively yield dicts that look like a notification record (have an AppNotification* key)."""
    if seen is None:
        seen = set()
    if id(obj) in seen:
        return
    seen.add(id(obj))
    if isinstance(obj, dict):
        if any(isinstance(k, str) and k.startswith('AppNotification') for k in obj):
            yield obj
        for value in obj.values():
            yield from _walk_notifications(value, seen)
    elif isinstance(obj, (list, tuple)):
        for value in obj:
            yield from _walk_notifications(value, seen)


@artifact_processor
def notificationsXI(context):
    data_headers = (('Creation Time', 'datetime'), 'Bundle', 'Title[Subtitle]', 'Message',
                    'Other Details')
    data_list = []
    sources = []

    candidates = []
    for fp in context.get_files_found():
        fp = str(fp)
        if os.path.isdir(fp):
            candidates.extend(str(x) for x in glob.iglob(os.path.join(fp, '**'), recursive=True))
        else:
            candidates.append(fp)

    for filepath in candidates:
        if not (os.path.isfile(filepath) and filepath.endswith('pushstore')):
            continue
        try:
            with open(filepath, 'rb') as f:
                plist = nd.deserialize_plist(f)
        except (OSError, ValueError, nd.DeserializeError):
            continue

        bundle = os.path.splitext(os.path.basename(filepath))[0]
        matched = False
        for item in _walk_notifications(plist):
            matched = True
            creation_date = item.get('AppNotificationCreationDate', '')
            if isinstance(creation_date, datetime):
                creation_date = creation_date.replace(tzinfo=timezone.utc)
            title = item.get('AppNotificationTitle', '') or ''
            subtitle = item.get('AppNotificationSubtitle', '')
            message = item.get('AppNotificationMessage', '')
            other = {k: str(v) for k, v in item.items() if k not in _FIELDS}
            if subtitle:
                title = f'{title}[{subtitle}]'
            data_list.append((creation_date, bundle, title, message, str(other)))
        if matched:
            sources.append(context.get_relative_path(filepath))

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
