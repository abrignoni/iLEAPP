__artifacts_v2__ = {
    "notificationsXII": {
        "name": "Notifications",
        "description": "iOS 12+ delivered notifications (DeliveredNotifications.plist)",
        "author": "@abrignoni",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-07-26",
        "requirements": "none",
        "category": "Notifications",
        "notes": "Attachments are checked in as media, both the images stored under the Attachments folder and the ones carried inline in the payload. Sender, thread, category, trigger type and deep link are lifted out of the payload into their own columns; keys still holding their corpus-wide default value are dropped from Other Details.",
        "paths": ('*/mobile/Library/UserNotifications*',),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 86 rows",
            "dexter_ios18": "iOS 18.3.2 | 51 rows",
            "felix_ios17": "iOS 17.6.1 | 15 rows",
            "fsfull002_ios17": "iOS 17.1 | 4 rows",
            "hc_ios18_7": "iOS 18.7.8 | 24 rows",
            "iphone11_ios17": "iOS 17.3 | 298 rows",
            "iphone12_ios18": "iOS 18.7 | 20 rows",
            "iphone14plus_ios18": "iOS 18.0 | 10 rows",
            "otto_ios17": "iOS 17.5.1 | 379 rows",
            "abe_ios16": "iOS 16.5 | 142 rows",
            "felix23_ios16": "iOS 16.5 | 3 rows",
            "hickman_ios13": "iOS 13.3.1 | 83 rows",
            "hickman_ios14": "iOS 14.3 | 4 rows",
            "jess_ios15": "iOS 15.0.2 | 42 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    }
}

import glob
import os
from datetime import datetime, timezone

import nska_deserialize as nd

from scripts.ilapfuncs import (artifact_processor, check_in_embedded_media, check_in_media,
                               logfunc)

# Signatures of the image formats a notification payload is likely to carry
IMAGE_SIGNATURES = ((b'\xff\xd8\xff', 'jpg'), (b'\x89PNG\r\n\x1a\n', 'png'), (b'GIF8', 'gif'))
HEIF_BRANDS = (b'heic', b'heix', b'hevc', b'mif1', b'msf1')
# Anything shorter than this is a stray blob that happens to start like an image
MIN_EMBEDDED_IMAGE = 512

# Payload fields worth a column of their own, so notifications can be sorted and
# filtered by who they came from rather than only by the app that raised them
PROMOTED_FIELDS = (
    ('Sender', 'CommunicationContextDisplayName'),
    ('Thread', 'SBSPushStoreNotificationThreadKey'),
    ('Category', 'SBSPushStoreNotificationCategoryKey'),
    ('Trigger', 'UNNotificationTriggerType'),
    ('Deep Link', 'DefaultActionURL'),
)
PROMOTED_COLUMN_BY_KEY = {key: column for column, key in PROMOTED_FIELDS}

# Values these keys held on every row of all 15 test corpus devices, each key
# seen on at least 8 of them. They are dropped from Other Details only while
# they still hold that value, so a device that sets one differently still shows
# it. Keys constant on only one or two devices are deliberately not listed:
# a single observation is not enough to call a value a default.
DEFAULT_VALUES = {
    'BadgeApplicationIcon': 'True',
    'CommunicationContextBusinessCorrespondence': 'False',
    'CommunicationContextCapabilities': '0',
    'CommunicationContextMentionsCurrentUser': 'False',
    'CommunicationContextNotifyRecipientAnyway': 'False',
    'CommunicationContextReplyToCurrentUser': 'False',
    'CommunicationContextSystemImage': 'False',
    'Footer': '',
    'IconShouldSuppressMask': 'False',
    'ScreenCaptureProhibited': 'False',
    'ShouldHideTime': 'False',
    'ShouldIgnoreAccessibilityDisabledVibrationSetting': 'False',
    'ShouldPresentAlert': 'True',
    'ShouldSuppressSyncDismissalWhenRemoved': 'False',
    'SoundShouldIgnoreRingerSwitch': 'False',
    'SoundShouldRepeat': 'False',
    'ToneMediaLibraryItemIdentifier': '0',
    'TriggerRepeatInterval': '0',
    'TriggerRepeats': 'False',
    'UNNotificationRelevanceScore': '0.0',
}


def _image_extension(data):
    """Return the file extension when the bytes carry a known image signature."""
    for signature, extension in IMAGE_SIGNATURES:
        if data.startswith(signature):
            return extension
    if len(data) > 12 and data[4:8] == b'ftyp' and data[8:12] in HEIF_BRANDS:
        return 'heic'
    return None


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


def _extract_embedded_images(value, source_file, references, label='image'):
    """Pull inline images out of a notification payload, leaving a note behind.

    Not every notification image reaches the Attachments folder. Photos memories,
    for one, carry the thumbnail inside UNNotificationUserInfo as raw bytes.
    Stringified into the details column that is a six figure run of escaped
    bytes that swamps the row and cannot be viewed, so check the image in as
    media and put a short placeholder in its place. The payload is walked rather
    than read at a fixed key because apps nest it wherever they please.
    """
    if isinstance(value, dict):
        return {key: _extract_embedded_images(item, source_file, references, key)
                for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_extract_embedded_images(item, source_file, references, label) for item in value]
    if isinstance(value, (bytes, bytearray)) and len(value) >= MIN_EMBEDDED_IMAGE:
        data = bytes(value)
        extension = _image_extension(data)
        if not extension:
            return value
        try:
            reference = check_in_embedded_media(source_file, data, name=f'{label}.{extension}')
        except Exception as error:  # pylint: disable=broad-except
            logfunc(f'Notifications: could not check in embedded {label}: {error}')
            return value
        if not reference:
            return value
        references.append(reference)
        return f'<{len(data)} byte {extension} checked in as media>'
    return value


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
    data_headers = (('Creation Time', 'datetime'), 'Bundle', 'Sender', 'Title[Subtitle]',
                    'Message', ('Attachments', 'media'), 'Attachment Count', 'Thread',
                    'Category', 'Trigger', 'Deep Link', 'Other Details')
    data_list = []
    sources = []

    # The path glob matches the UserNotifications folder, each per-bundle folder
    # inside it and the files themselves, so walking every matched directory
    # reaches the same plist once per ancestor plus once directly. Without the
    # dedupe every notification is reported three times over.
    seen_paths = {}
    for fp in context.get_files_found():
        fp = str(fp)
        if os.path.isdir(fp):
            for found in glob.iglob(os.path.join(fp, '**'), recursive=True):
                seen_paths.setdefault(os.path.realpath(found), str(found))
        else:
            seen_paths.setdefault(os.path.realpath(fp), fp)
    plist_files = list(seen_paths.values())

    bundle_info = _bundle_info(plist_files)
    attachment_index = _attachment_index(plist_files)
    checked_in = 0
    embedded = 0
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
            promoted = dict.fromkeys(PROMOTED_COLUMN_BY_KEY.values(), '')
            # A notification can carry several attachments, so the media cell takes a list
            media = _notification_media(item, attachment_index, seen_attachments)
            checked_in += len(media)
            inline = []
            for k, v in item.items():
                if k == 'AppNotificationCreationDate':
                    creation_date = v.replace(tzinfo=timezone.utc) if isinstance(v, datetime) else v
                elif k == 'AppNotificationMessage':
                    message = v
                elif k == 'AppNotificationTitle':
                    title = v
                elif k == 'AppNotificationSubtitle':
                    subtitle = v
                elif k in PROMOTED_COLUMN_BY_KEY:
                    promoted[PROMOTED_COLUMN_BY_KEY[k]] = str(v)
                elif k == 'AppNotificationAttachments' or DEFAULT_VALUES.get(k, object()) == str(v):
                    continue  # handled by its own column, or holding its default value
                else:
                    other_dict[k] = str(_extract_embedded_images(v, filepath, inline, k))
            if subtitle:
                title = f'{title}[{subtitle}]'
            media.extend(inline)
            embedded += len(inline)
            data_list.append((creation_date, bundle_name, promoted['Sender'], title, message,
                              media or '', len(media), promoted['Thread'], promoted['Category'],
                              promoted['Trigger'], promoted['Deep Link'], str(other_dict)))

    if checked_in:
        # Apps reuse one stored file across many notifications, so the two counts differ
        logfunc(f'Notifications: linked {checked_in} attachment reference(s) to '
                f'{len(seen_attachments)} stored file(s)')
    if embedded:
        logfunc(f'Notifications: recovered {embedded} image(s) embedded in notification payloads')

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
