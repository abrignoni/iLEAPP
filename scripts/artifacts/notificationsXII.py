__artifacts_v2__ = {
    "notificationsXII": {
        "name": "Notifications",
        "description": "iOS 12+ delivered notifications (DeliveredNotifications.plist)",
        "author": "",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-07-26",
        "requirements": "none",
        "category": "Notifications",
        "notes": "Notification attachments (images stored under the Attachments folder) are checked in as media and linked to the notification that referenced them.",
        "paths": ('*/mobile/Library/UserNotifications*',),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 258 rows",
            "dexter_ios18": "iOS 18.3.2 | 153 rows",
            "felix_ios17": "iOS 17.6.1 | 45 rows",
            "fsfull002_ios17": "iOS 17.1 | 12 rows",
            "hc_ios18_7": "iOS 18.7.8 | 72 rows",
            "iphone11_ios17": "iOS 17.3 | 894 rows",
            "iphone12_ios18": "iOS 18.7 | 60 rows",
            "iphone14plus_ios18": "iOS 18.0 | 30 rows",
            "otto_ios17": "iOS 17.5.1 | 1137 rows",
            "abe_ios16": "iOS 16.5 | 426 rows",
            "felix23_ios16": "iOS 16.5 | 9 rows",
            "hickman_ios13": "iOS 13.3.1 | 249 rows",
            "hickman_ios14": "iOS 14.3 | 12 rows",
            "jess_ios15": "iOS 15.0.2 | 126 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    }
}

import glob
import os
from datetime import datetime, timezone

import nska_deserialize as nd

from scripts.ilapfuncs import artifact_processor, check_in_media, logfunc


def _attachment_index(plist_files):
    """Map each notification attachment file name to its path on disk.

    Attachments are stored beside the notification plists under an Attachments
    folder, named by a hash rather than by anything meaningful, so an index by
    file name is enough to resolve them later.
    """
    index = {}
    for filepath in plist_files:
        if os.path.isfile(filepath) and f'{os.sep}Attachments{os.sep}' in filepath:
            index.setdefault(os.path.basename(filepath), filepath)
    return index


def _notification_media(item, attachment_index, seen):
    """Check in the attachments of one notification, returning media references.

    The plist records both an AttachmentIdentifier, which is the logical name
    the app chose, and an AttachmentURL pointing at the stored copy. Only the
    URL matches what is on disk, so resolve by that and keep the identifier as
    the display name. The identifier is not trustworthy as a file name though:
    apps hand out things like "image.gif" for what is really a JPEG, so the
    extension comes from the stored file instead of from the identifier.
    """
    references = []
    for attachment in item.get('AppNotificationAttachments') or []:
        if not isinstance(attachment, dict):
            continue
        url = attachment.get('AttachmentURL')
        relative = url.get('NS.relative', '') if isinstance(url, dict) else str(url or '')
        stored_name = relative.rsplit('/', 1)[-1]
        path = attachment_index.get(stored_name)
        if not path:
            continue
        extension = os.path.splitext(stored_name)[1]
        try:
            reference = check_in_media(path,
                                       name=attachment.get('AttachmentIdentifier') or stored_name,
                                       force_extension=extension or None)
        except Exception as error:  # pylint: disable=broad-except
            logfunc(f'Notifications: could not check in {stored_name}: {error}')
            continue
        if reference:
            references.append(reference)
            seen.add(path)
    return references


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
                    ('Attachments', 'media'), 'Attachment Count', 'Other Details')
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
    attachment_index = _attachment_index(plist_files)
    checked_in = 0
    seen_attachments = set()

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
                elif k != 'AppNotificationAttachments':
                    other_dict[k] = str(v)
            if subtitle:
                title = f'{title}[{subtitle}]'
            # A notification can carry several attachments, so the media cell takes a list
            media = _notification_media(item, attachment_index, seen_attachments)
            checked_in += len(media)
            data_list.append((creation_date, bundle_name, title, message, media or '',
                              len(media), str(other_dict)))

    if checked_in:
        # Apps reuse one stored file across many notifications, so the two counts differ
        logfunc(f'Notifications: linked {checked_in} attachment reference(s) to '
                f'{len(seen_attachments)} stored file(s)')

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
