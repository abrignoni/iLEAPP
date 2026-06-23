__artifacts_v2__ = {
    "notificationsXII": {
        "name": "Notifications",
        "description": "iOS 12+ delivered notifications (DeliveredNotifications.plist)",
        "author": "",
        "version": "2.0",
        "date": "2026-06-23",
        "requirements": "none",
        "category": "Notifications",
        "notes": "",
        "paths": ('*/mobile/Library/UserNotifications*',),
        "output_types": "standard",
        "artifact_icon": "bell"
    }
}

import glob
import os
from datetime import datetime, timezone

import nska_deserialize as nd

from scripts.ilapfuncs import artifact_processor


def _bundle_info(plist_files):
    """Map bundle_id -> bundle_name from UserNotificationsServer/Library.plist (if present)."""
    for fp in plist_files:
        if fp.endswith('Library.plist') and os.path.dirname(fp).endswith('UserNotificationsServer'):
            try:
                with open(fp, 'rb') as f:
                    plist = nd.deserialize_plist(f)
                return {v: k for k, v in plist.items()}
            except (OSError, ValueError, nd.DeserializeError):
                return {}
    return {}


@artifact_processor
def notificationsXII(context):
    data_headers = (('Creation Time', 'datetime'), 'Bundle', 'Title[Subtitle]', 'Message',
                    'Other Details')
    data_list = []
    sources = []

    plist_files = []
    for fp in context.get_files_found():
        fp = str(fp)
        if os.path.isdir(fp):
            plist_files.extend(str(x) for x in glob.iglob(os.path.join(fp, '**'), recursive=True))
        else:
            plist_files.append(fp)

    bundle_info = _bundle_info(plist_files)

    for filepath in plist_files:
        if not (os.path.isfile(filepath) and filepath.endswith('DeliveredNotifications.plist')):
            continue
        try:
            with open(filepath, 'rb') as p:
                plist = nd.deserialize_plist(p)
        except (OSError, ValueError, nd.DeserializeError):
            continue
        if isinstance(plist, dict):
            continue  # empty plist is {'root': None}

        sources.append(context.get_relative_path(filepath))
        bundle_id = os.path.basename(os.path.dirname(filepath))
        bundle_name = bundle_info.get(bundle_id, bundle_id)

        for item in plist:
            creation_date = ''
            title = subtitle = message = ''
            other_dict = {}
            for k, v in item.items():
                if k == 'AppNotificationCreationDate':
                    creation_date = v.replace(tzinfo=timezone.utc) if isinstance(v, datetime) else v
                elif k == 'AppNotificationMessage':
                    message = v
                elif k == 'AppNotificationTitle':
                    title = v
                elif k == 'AppNotificationSubtitle':
                    subtitle = v
                else:
                    other_dict[k] = str(v)
            if subtitle:
                title = f'{title}[{subtitle}]'
            data_list.append((creation_date, bundle_name, title, message, str(other_dict)))

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
