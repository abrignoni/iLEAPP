__artifacts_v2__ = {
    "chrome_ios_open_tabs": {
        "name": "Chromium Open Tabs (iOS) - Tabs",
        "description": "Tabs a Chromium-based iOS browser (Chrome, Edge, Brave) kept in its session storage, "
                       "with the window kind (normal, inactive or Incognito), the tab's creation and last "
                       "active times, the page it was on and the tab's snapshot image.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-01",
        "last_update_date": "2026-11-01",
        "requirements": "none",
        "category": "Chromium Sessions",
        "notes": (
            'Two storage formats are read. (1) SessionStorage/<session>/session_metadata.pb, the tab list '
            '(WebStateListStorage), and <tab>/data.pb for each tab (WebStateStorage), file names from '
            'https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/chrome/browser/sessions/model/session_constants.mm#L7-L17.'
            " They are decoded with the vendored blackboxprotobuf using the field numbers of Chromium's own "
            'protos at commit 1c1ecc6d '
            '(https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/chrome/browser/sessions/model/proto/storage.proto#L28-L42,'
            ' '
            'https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/web/public/session/proto/storage.proto#L18-L24,'
            ' '
            'https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/web/public/session/proto/metadata.proto#L27-L32,'
            ' '
            'https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/web/public/session/proto/navigation.proto#L52-L72).'
            ' Every commit to those files since they were created in 2023 was read: fields were only added, and '
            'no field number was reused. Each time is a Timestamp in microseconds that TimeFromProto reads as '
            'time since 1601-01-01 UTC '
            '(https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/web/public/session/proto/proto_util.cc#L16-L19).'
            " The tab's state.pb, the web view's own session state "
            '(https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/chrome/browser/sessions/model/session_restoration_service_impl.mm#L856-L863),'
            ' is not read. (2) The older Sessions/<session>/session.plist, an NSKeyedArchiver archive read with '
            "the core's plist helper: a list of windows (sessionWindows) or one window, each with its tabs "
            '(sessions) and selectedIndex '
            '(https://github.com/chromium/chromium/blob/d221f35c9153cee8627a3c982e3c967531248ea2/ios/chrome/browser/sessions/session_ios.mm#L15,'
            ' '
            'https://github.com/chromium/chromium/blob/d221f35c9153cee8627a3c982e3c967531248ea2/ios/chrome/browser/sessions/session_window_ios.mm#L18-L19);'
            ' per tab entries, lastCommittedItemIndex, stableIdentifier, lastActiveTime and creationTime '
            '(https://github.com/chromium/chromium/blob/e1f6ff24e62718c3879f6314659c3a32be0cf76f/ios/web/session/crw_session_storage.mm#L26-L34),'
            ' the two times read as microseconds since 1601 '
            '(https://github.com/chromium/chromium/blob/e1f6ff24e62718c3879f6314659c3a32be0cf76f/ios/web/session/crw_session_storage.mm#L155-L162);'
            ' per entry urlString, virtualUrlString, referrerUrlString, timestamp and title '
            '(https://github.com/chromium/chromium/blob/d221f35c9153cee8627a3c982e3c967531248ea2/ios/web/crw_navigation_item_storage.mm#L20-L26),'
            ' the timestamp a base::Time internal value '
            '(https://github.com/chromium/chromium/blob/d221f35c9153cee8627a3c982e3c967531248ea2/ios/web/crw_navigation_item_storage.mm#L109-L112),'
            ' which is microseconds since 1601 '
            '(https://github.com/chromium/chromium/blob/d221f35c9153cee8627a3c982e3c967531248ea2/base/time/time.h#L509).'
            ' A file that does not decode is logged and not reported; none failed on the tested images. Window is'
            " Incognito for a file under the profile's OTR folder, the off-the-record state path "
            '(https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/chrome/browser/shared/model/profile/profile_ios.mm#L86-L93),'
            " Inactive for a session folder ending -Inactive, the suffix Chrome gives an inactive browser's "
            'session '
            '(https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/chrome/browser/sessions/model/session_util.mm#L25-L26),'
            " and Normal otherwise. Bundle ID is the MCMMetadataIdentifier of the app container's metadata plist,"
            ' as in Chrome Sync - Synced Tabs; an iTunes backup names the container by bundle identifier, and no '
            'backup holding these files was run. On the tested images the files belonged to '
            'com.google.chrome.ios, com.microsoft.msedge and com.brave.ios.browser. One row per tab, plus one per'
            ' snapshot no tab names (below). Tab ID is the tab folder name, the tab identifier as eight hex '
            'digits '
            '(https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/chrome/browser/sessions/model/session_loading.mm#L127-L130),'
            ' or the stableIdentifier for session.plist. In Tab List is Yes when the tab list names the tab '
            'folder and No when a data.pb folder is not in it; it is blank for a session.plist tab, as that '
            'format keeps no separate list. Brave held 5 unlisted folders (hc_ios18_7 4, hc_ios26 1); none held a'
            ' navigation entry, and their times are blank because the times come from the tab list. What an '
            "unlisted folder means is not established. Selected Tab is the list's active_index or the window's "
            "selectedIndex. Last Active and Created are the tab's last_active_time and creation_time, or "
            "lastActiveTime and creationTime. Entries counts the tab's navigation entries; Current URL and "
            'Current Title are those of the entry at the last committed index, the URL being the virtual URL '
            'where one is stored. Snapshot is the colour JPEG the browser saved for the tab, a file named by the '
            'snapshot identifier as a decimal number padded to at least eight digits '
            '(https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/chrome/browser/snapshots/model/image_file_manager.swift#L337-L342)'
            ' or, in the legacy layout, by the identifier string '
            '(https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/chrome/browser/snapshots/model/image_file_manager.swift#L346-L352),'
            ' with @2x for a 2x image. It is looked up in Snapshots/<session> beside SessionStorage under the tab'
            ' identifier in decimal, and in Sessions/<session>/Snapshots under the stableIdentifier; that the '
            'snapshot identifier equals the tab identifier is an observation (30 of 30 SessionStorage snapshots '
            'on the tested images), not a sourced rule. The bytes are checked for a JPEG header first, and grey '
            'copies are not shown. A colour snapshot in one of those folders that no tab of the session names '
            'gets its own row with In Tab List No, the snapshot identifier as Tab ID, no entries and blank times:'
            ' 5 on the tested images (abe_ios16 1, hickman_ios15 4), all in the session.plist layout. Snapshot '
            'was filled on 78 of the 97 tested rows; the Brave sessions on hc_ios18_7 and hc_ios26 had no '
            'Snapshots folder under Application Support, iphone11_ios17 had no snapshot file in its Sessions '
            'folders, and the other 4 (abe_ios16 2, magnet_ios16 1, otto_ios17 1) are tabs whose snapshot folder '
            "holds no colour file under the tab's identifier. When the browser took a snapshot is not "
            'established, so it shows the page as captured, not as it was when the device was seized. On the '
            'tested images 6 tabs were Incognito (plus 2 snapshot-only rows in Incognito folders) and 14 '
            'Inactive. On dexter_ios18 and otto_ios17 the 8 distinct http(s) addresses in Incognito tabs were in '
            "neither the browser's History database (urls and visits) nor the synced tabs in its Sync Data store,"
            ' read with the same reader as Chrome Sync - Synced Tabs. A tab row means the session file listed the'
            ' tab when it was last written; an unlisted-folder row or a snapshot-only row means only that the '
            'file was present. Not read: tab groups, openers, the pinned count, the certificate cache, request '
            'headers and page display state. Closed tabs in Sessions/Tabs_* are read by Chromium Session Tabs - '
            'Navigation Entries.'
        ),
        "paths": (
            '*/Library/Application Support/*/SessionStorage/*',
            '*/Library/Application Support/*/Sessions/*/session.plist',
            '*/Library/Application Support/*/Snapshots/*.jpg',
        ),
        "output_types": "standard",
        "artifact_icon": "browser",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 35 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "belkactf6_tar": "iOS 16.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 1 row",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 21 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 6 rows",
            "hc_ios26": "iOS 26.5.2 | 5 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 10 rows",
            "iphone11_ios17": "iOS 17.3 | 4 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 6 rows",
            "otto_ios17": "iOS 17.5.1 | 9 rows",
        },
    },
    "chrome_ios_open_tab_entries": {
        "name": "Chromium Open Tabs (iOS) - Navigation Entries",
        "description": "The navigation history entries of each tab a Chromium-based iOS browser kept in its "
                       "session storage, with the address, title and timestamp stored for each entry.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-01",
        "last_update_date": "2026-11-01",
        "requirements": "none",
        "category": "Chromium Sessions",
        "notes": (
            'Two storage formats are read. (1) SessionStorage/<session>/session_metadata.pb, the tab list '
            '(WebStateListStorage), and <tab>/data.pb for each tab (WebStateStorage), file names from '
            'https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/chrome/browser/sessions/model/session_constants.mm#L7-L17.'
            " They are decoded with the vendored blackboxprotobuf using the field numbers of Chromium's own "
            'protos at commit 1c1ecc6d '
            '(https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/chrome/browser/sessions/model/proto/storage.proto#L28-L42,'
            ' '
            'https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/web/public/session/proto/storage.proto#L18-L24,'
            ' '
            'https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/web/public/session/proto/metadata.proto#L27-L32,'
            ' '
            'https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/web/public/session/proto/navigation.proto#L52-L72).'
            ' Every commit to those files since they were created in 2023 was read: fields were only added, and '
            'no field number was reused. Each time is a Timestamp in microseconds that TimeFromProto reads as '
            'time since 1601-01-01 UTC '
            '(https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/web/public/session/proto/proto_util.cc#L16-L19).'
            " The tab's state.pb, the web view's own session state "
            '(https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/chrome/browser/sessions/model/session_restoration_service_impl.mm#L856-L863),'
            ' is not read. (2) The older Sessions/<session>/session.plist, an NSKeyedArchiver archive read with '
            "the core's plist helper: a list of windows (sessionWindows) or one window, each with its tabs "
            '(sessions) and selectedIndex '
            '(https://github.com/chromium/chromium/blob/d221f35c9153cee8627a3c982e3c967531248ea2/ios/chrome/browser/sessions/session_ios.mm#L15,'
            ' '
            'https://github.com/chromium/chromium/blob/d221f35c9153cee8627a3c982e3c967531248ea2/ios/chrome/browser/sessions/session_window_ios.mm#L18-L19);'
            ' per tab entries, lastCommittedItemIndex, stableIdentifier, lastActiveTime and creationTime '
            '(https://github.com/chromium/chromium/blob/e1f6ff24e62718c3879f6314659c3a32be0cf76f/ios/web/session/crw_session_storage.mm#L26-L34),'
            ' the two times read as microseconds since 1601 '
            '(https://github.com/chromium/chromium/blob/e1f6ff24e62718c3879f6314659c3a32be0cf76f/ios/web/session/crw_session_storage.mm#L155-L162);'
            ' per entry urlString, virtualUrlString, referrerUrlString, timestamp and title '
            '(https://github.com/chromium/chromium/blob/d221f35c9153cee8627a3c982e3c967531248ea2/ios/web/crw_navigation_item_storage.mm#L20-L26),'
            ' the timestamp a base::Time internal value '
            '(https://github.com/chromium/chromium/blob/d221f35c9153cee8627a3c982e3c967531248ea2/ios/web/crw_navigation_item_storage.mm#L109-L112),'
            ' which is microseconds since 1601 '
            '(https://github.com/chromium/chromium/blob/d221f35c9153cee8627a3c982e3c967531248ea2/base/time/time.h#L509).'
            ' A file that does not decode is logged and not reported; none failed on the tested images. Window is'
            " Incognito for a file under the profile's OTR folder, the off-the-record state path "
            '(https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/chrome/browser/shared/model/profile/profile_ios.mm#L86-L93),'
            " Inactive for a session folder ending -Inactive, the suffix Chrome gives an inactive browser's "
            'session '
            '(https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/chrome/browser/sessions/model/session_util.mm#L25-L26),'
            " and Normal otherwise. Bundle ID is the MCMMetadataIdentifier of the app container's metadata plist,"
            ' as in Chrome Sync - Synced Tabs; an iTunes backup names the container by bundle identifier, and no '
            'backup holding these files was run. On the tested images the files belonged to '
            'com.google.chrome.ios, com.microsoft.msedge and com.brave.ios.browser. One row per navigation entry '
            "of each tab, in the tab's own order (Index from 0). Current Entry is Yes for the entry at the tab's "
            "last committed index. URL is the entry's url or urlString. Virtual URL is written only when it "
            'differs from the URL by the current code '
            '(https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/web/navigation/navigation_item_impl.mm#L111-L113)'
            " and by Chrome 97's session.plist encoder "
            '(https://github.com/chromium/chromium/blob/d221f35c9153cee8627a3c982e3c967531248ea2/ios/web/crw_navigation_item_storage.mm#L150-L157),'
            ' and is blank when absent or empty. It was set on 16 of 134 protobuf entries. Of the 97 '
            'session.plist entries tested, 22 held one that differs from the URL, 24 had none and 51 held an '
            'empty value, so some version wrote it empty; which one was not established. Navigation Time is the '
            "entry's timestamp, filled on every tested entry. Referrer URL is the stored referrer. Tab ID, Window"
            ' and Bundle ID are as in Chromium Open Tabs (iOS) - Tabs and join the two artifacts. A page here '
            "need not appear in the browser's History."
        ),
        "paths": (
            '*/Library/Application Support/*/SessionStorage/*',
            '*/Library/Application Support/*/Sessions/*/session.plist',
        ),
        "output_types": "standard",
        "artifact_icon": "list",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 47 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "belkactf6_tar": "iOS 16.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 6 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 93 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 2 rows",
            "hc_ios26": "iOS 26.5.2 | 4 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 17 rows",
            "iphone11_ios17": "iOS 17.3 | 14 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 19 rows",
            "otto_ios17": "iOS 17.5.1 | 29 rows",
        },
    },
}

import datetime
import os
import plistlib
import re
import struct

from google.protobuf.message import DecodeError

from scripts import blackboxprotobuf
from scripts.context import Context
from scripts.ilapfuncs import artifact_processor, check_in_media, get_plist_content, logfunc

_CHROMIUM_EPOCH = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)
_CONTAINER = re.compile(r'(?:^|/)Containers/Data/Application/([^/]+)(?=/)')
_UUID = re.compile(r'^[0-9A-Fa-f]{8}(?:-[0-9A-Fa-f]{4}){3}-[0-9A-Fa-f]{12}$')
_METADATA_NAME = '.com.apple.mobile_container_manager.metadata.plist'
_bundle_ids = {}
_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError, OSError)

# Field numbers from Chromium's protos at 1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a:
# ios/chrome/browser/sessions/model/proto/storage.proto (WebStateListStorage) and
# ios/web/public/session/proto/{storage,metadata,navigation,common}.proto (WebStateStorage).
_TIMESTAMP = {'1': {'type': 'int', 'name': ''}}  # Timestamp.microseconds
_PAGE = {'1': {'type': 'str', 'name': ''}, '2': {'type': 'str', 'name': ''}}  # page_title, page_url
_METADATA = {
    '1': {'type': 'message', 'message_typedef': _TIMESTAMP, 'name': ''},  # creation_time
    '2': {'type': 'message', 'message_typedef': _TIMESTAMP, 'name': ''},  # last_active_time
    '3': {'type': 'message', 'message_typedef': _PAGE, 'name': ''},  # active_page
    '4': {'type': 'int', 'name': ''},  # navigation_item_count
}
_LIST = {
    '1': {'type': 'message', 'name': '', 'message_typedef': {  # items
        '1': {'type': 'int', 'name': ''},  # identifier
        '2': {'type': 'message', 'name': '', 'message_typedef': {
            '1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}},  # opener
        '3': {'type': 'message', 'message_typedef': _METADATA, 'name': ''},  # metadata
    }},
    '2': {'type': 'int', 'name': ''},  # active_index
    '3': {'type': 'int', 'name': ''},  # pinned_item_count
    '4': {'type': 'bytes', 'name': ''},  # groups, not read
}
_ITEM = {
    '1': {'type': 'str', 'name': ''},  # url
    '2': {'type': 'str', 'name': ''},  # virtual_url
    '3': {'type': 'str', 'name': ''},  # title
    '4': {'type': 'message', 'message_typedef': _TIMESTAMP, 'name': ''},  # timestamp
    '5': {'type': 'int', 'name': ''},  # user_agent
    '6': {'type': 'message', 'name': '', 'message_typedef': {
        '1': {'type': 'str', 'name': ''}, '2': {'type': 'int', 'name': ''}}},  # referrer
    '7': {'type': 'bytes', 'name': ''},  # http_request_headers, not read
    '8': {'type': 'bytes', 'name': ''},  # security_scoped_file_resource, not read
    '9': {'type': 'int', 'name': ''},  # was_created_automatically
    '10': {'type': 'str', 'name': ''},  # internal_scroll_to_text_fragment, not read
}
_WEB_STATE = {
    '1': {'type': 'int', 'name': ''},  # has_opener
    '2': {'type': 'message', 'message_typedef': _METADATA, 'name': ''},  # metadata
    '3': {'type': 'int', 'name': ''},  # user_agent
    '4': {'type': 'message', 'name': '', 'message_typedef': {  # navigation
        '1': {'type': 'int', 'name': ''},  # last_committed_item_index
        '2': {'type': 'message', 'message_typedef': _ITEM, 'name': ''},  # items
    }},
    '5': {'type': 'bytes', 'name': ''},  # certs_cache, not read
}


def _time(value):
    """Microseconds since 1601 (base::Time internal value) as an aware UTC datetime; 0 and blank stay blank."""
    if value in (None, '', 0):
        return ''
    try:
        return _CHROMIUM_EPOCH + datetime.timedelta(microseconds=int(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _text(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    return value if isinstance(value, str) else ''


def _list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _bundle_id(relative):
    """The bundle identifier of the app container, or ''. An iTunes backup names the container folder
    by bundle identifier; a full file system names it by UUID, resolved through the container's
    metadata plist (the same rule chromeSyncData.py uses)."""
    container = _CONTAINER.search(relative)
    if not container:
        return ''
    name = container.group(1)
    if not _UUID.match(name):
        return name
    root = relative[:container.end()]
    key = (Context.get_data_folder(), root)
    if key not in _bundle_ids:
        identifier = ''
        try:
            found = Context.get_seeker().search(f'*/Containers/Data/Application/{name}/{_METADATA_NAME}')
        except ValueError:  # no seeker outside a run
            found = []
        for path in found:
            if Context.get_relative_path(str(path)).replace('\\', '/') != f'{root}/{_METADATA_NAME}':
                continue
            try:
                with open(path, 'rb') as handle:
                    value = plistlib.load(handle)
            except (OSError, plistlib.InvalidFileException, ValueError):
                continue
            if isinstance(value, dict) and isinstance(value.get('MCMMetadataIdentifier'), str):
                identifier = value['MCMMetadataIdentifier']
        _bundle_ids[key] = identifier
    return _bundle_ids[key]


def _window(relative, session_id):
    """Incognito for the profile's OTR folder (ProfileIOS::GetOffTheRecordStatePath), Inactive for a
    session folder ending -Inactive (session_util.mm), Normal otherwise."""
    if '/OTR/' in relative:
        return 'Incognito'
    if session_id.endswith('-Inactive'):
        return 'Inactive'
    return 'Normal'


_COLOUR_SNAPSHOT = re.compile(r'^(?!.*Grey(?:@\dx)?\.jpg$)(?!.*tabTopToolBar)(.+?)(?:@\dx)?\.jpg$')


def _snapshot(snapshots, folder, names, used):
    """Media reference for the first colour snapshot in `folder` with one of `names`, or ''.
    Every name tried is added to `used`, so a file that is not a JPEG is not reported again."""
    for name in names:
        for candidate in (f'{name}@2x.jpg', f'{name}.jpg', f'{name}@3x.jpg'):
            path = snapshots.get((folder, candidate))
            if not path:
                continue
            used.add((folder, candidate))
            try:
                with open(path, 'rb') as handle:
                    if handle.read(3) != b'\xff\xd8\xff':
                        logfunc(f'Chromium Open Tabs (iOS): {candidate} is not a JPEG and is not shown')
                        continue
            except OSError:
                continue
            return check_in_media(path, name=candidate) or ''
    return ''


def _entries(items):
    out = []
    for item in items:
        if not isinstance(item, dict):
            continue
        referrer = item.get('6') if isinstance(item.get('6'), dict) else {}
        timestamp = item.get('4') if isinstance(item.get('4'), dict) else {}
        out.append({'url': _text(item.get('1')), 'virtual_url': _text(item.get('2')),
                    'title': _text(item.get('3')), 'time': _time(timestamp.get('1')),
                    'referrer': _text(referrer.get('1'))})
    return out


def _decode(path, typedef, label):
    try:
        with open(path, 'rb') as handle:
            data = handle.read()
        value, _ = blackboxprotobuf.decode_message(data, typedef)
        return value
    except _DECODE_ERRORS as ex:
        logfunc(f'Chromium Open Tabs (iOS): {label} did not decode and is not reported: {type(ex).__name__}: {ex}')
        return None


def _session_storage(context, files):
    """Tabs from SessionStorage/<session id>/session_metadata.pb and <%08x tab id>/data.pb."""
    tabs = []
    sessions = {}
    for path in files:
        norm = path.replace('\\', '/')
        match = re.search(r'/SessionStorage/([^/]+)/(?:session_metadata\.pb|([0-9a-f]{8})/data\.pb)$', norm)
        if match:
            sessions.setdefault(norm[:match.start(1) + len(match.group(1))], []).append(path)
    for session_dir, paths in sorted(sessions.items()):
        session_id = session_dir.rsplit('/', 1)[1]
        meta_path = next((p for p in paths if os.path.basename(p) == 'session_metadata.pb'), None)
        listed, active = [], None
        if meta_path:
            value = _decode(meta_path, _LIST, context.get_relative_path(meta_path))
            if value is not None:
                listed = [i for i in _list(value.get('1')) if isinstance(i, dict)]
                active = value.get('2', 0)
        order = {}
        for index, item in enumerate(listed):
            if isinstance(item.get('1'), int):
                order[format(item['1'] & 0xFFFFFFFF, '08x')] = (index, item)
        data = {p.replace('\\', '/').rsplit('/', 2)[1]: p for p in paths
                if os.path.basename(p) == 'data.pb'}
        for folder in sorted(data, key=lambda f, positions=order: (positions.get(f, (10 ** 9,))[0], f)):
            path = data[folder]
            relative = context.get_relative_path(path)
            value = _decode(path, _WEB_STATE, relative)
            if value is None:
                continue
            navigation = value.get('4') if isinstance(value.get('4'), dict) else {}
            index, item = order.get(folder, (None, None))
            metadata = (item or {}).get('3') if isinstance((item or {}).get('3'), dict) else {}
            tabs.append({
                'path': path, 'relative': relative, 'session_id': session_id,
                'tab_id': folder, 'listed': 'Yes' if item else 'No' if meta_path else '',
                'selected': '' if index is None else 'Yes' if index == active else 'No',
                'created': _time((metadata.get('1') or {}).get('1') if isinstance(metadata.get('1'), dict) else None),
                'last_active': _time((metadata.get('2') or {}).get('1') if isinstance(metadata.get('2'), dict) else None),
                'current': navigation.get('1', 0),
                'entries': _entries(_list(navigation.get('2'))),
                'snapshot_folder': session_dir.replace('/SessionStorage/', '/Snapshots/'),
                'snapshot_names': [f'{int(folder, 16):08d}'],
            })
    return tabs


def _session_plists(context, files):
    """Tabs from the older Sessions/<session id>/session.plist (NSKeyedArchiver; CRWSessionStorage)."""
    tabs = []
    for path in files:
        norm = path.replace('\\', '/')
        match = re.search(r'/Sessions/([^/]+)/session\.plist$', norm)
        if not match:
            continue
        relative = context.get_relative_path(path)
        try:
            with open(path, 'rb') as handle:
                root = get_plist_content(handle.read())
        except OSError as ex:
            logfunc(f'Chromium Open Tabs (iOS): could not read {relative}: {ex}')
            continue
        if not isinstance(root, dict):
            logfunc(f'Chromium Open Tabs (iOS): {relative} did not deserialize and is not reported')
            continue
        windows = root.get('sessionWindows') if isinstance(root.get('sessionWindows'), list) else [root]
        for window in windows:
            if not isinstance(window, dict):
                continue
            selected = window.get('selectedIndex')
            for index, session in enumerate(_list(window.get('sessions'))):
                if not isinstance(session, dict):
                    continue
                stable = _text(session.get('stableIdentifier'))
                entries = []
                for entry in _list(session.get('entries')):
                    if not isinstance(entry, dict):
                        continue
                    entries.append({'url': _text(entry.get('urlString')),
                                    'virtual_url': _text(entry.get('virtualUrlString')),
                                    'title': _text(entry.get('title')), 'time': _time(entry.get('timestamp')),
                                    'referrer': _text(entry.get('referrerUrlString'))})
                tabs.append({
                    'path': path, 'relative': relative,
                    'session_id': match.group(1), 'tab_id': stable, 'listed': '',
                    'selected': '' if not isinstance(selected, int) else 'Yes' if index == selected else 'No',
                    'created': _time(session.get('creationTime')),
                    'last_active': _time(session.get('lastActiveTime')),
                    'current': session.get('lastCommittedItemIndex', session.get('currentNavigationIndex', 0)),
                    'entries': entries,
                    'snapshot_folder': norm.rsplit('/', 1)[0] + '/Snapshots',
                    'snapshot_names': [stable] if stable else [],
                })
    return tabs


def _tabs(context):
    files = sorted(str(f) for f in context.get_files_found() if os.path.isfile(str(f)))
    return _session_storage(context, files) + _session_plists(context, files), files


@artifact_processor
def chrome_ios_open_tabs(context):
    data_headers = (
        ('Last Active', 'datetime'), ('Created', 'datetime'), 'Bundle ID', 'Window', 'Tab ID',
        'In Tab List', 'Selected Tab', 'Entries', 'Current URL', 'Current Title', ('Snapshot', 'media'),
        'Source File',
    )
    tabs, files = _tabs(context)
    snapshots = {}
    for path in files:
        norm = path.replace('\\', '/')
        if norm.endswith('.jpg') and '/Snapshots/' in norm:
            folder, name = norm.rsplit('/', 1)
            snapshots[(folder, name)] = path
    data_list, sources, used, folders = [], [], set(), {}
    for tab in tabs:
        current = tab['current'] if isinstance(tab['current'], int) else 0
        entry = tab['entries'][current] if 0 <= current < len(tab['entries']) else {}
        folders.setdefault(tab['snapshot_folder'], tab)
        data_list.append((
            tab['last_active'], tab['created'], _bundle_id(tab['relative']),
            _window(tab['relative'], tab['session_id']), tab['tab_id'], tab['listed'], tab['selected'],
            len(tab['entries']), entry.get('virtual_url') or entry.get('url', ''), entry.get('title', ''),
            _snapshot(snapshots, tab['snapshot_folder'], tab['snapshot_names'], used), tab['relative'],
        ))
        if tab['path'] not in sources:
            sources.append(tab['path'])
    # Colour snapshots in a read session's snapshot folder that no tab of the session names
    for (folder, name), path in sorted(snapshots.items()):
        match = _COLOUR_SNAPSHOT.match(name)
        if folder not in folders or (folder, name) in used or not match:
            continue
        for scale in ('@2x', '', '@3x'):  # one row per snapshot identifier, whatever scales are on disk
            used.add((folder, f'{match.group(1)}{scale}.jpg'))
        owner = folders[folder]
        media = _snapshot(snapshots, folder, [match.group(1)], used)
        if not media:
            continue
        relative = context.get_relative_path(path)
        data_list.append((
            '', '', _bundle_id(owner['relative']), _window(owner['relative'], owner['session_id']),
            match.group(1), 'No', '', 0, '', '', media, relative,
        ))
        sources.append(path)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def chrome_ios_open_tab_entries(context):
    data_headers = (
        ('Navigation Time', 'datetime'), 'Bundle ID', 'Window', 'Tab ID', 'Index', 'Current Entry', 'URL',
        'Virtual URL', 'Title', 'Referrer URL', 'Source File',
    )
    tabs, _ = _tabs(context)
    data_list, sources = [], []
    for tab in tabs:
        bundle = _bundle_id(tab['relative'])
        window = _window(tab['relative'], tab['session_id'])
        for index, entry in enumerate(tab['entries']):
            data_list.append((
                entry['time'], bundle, window, tab['tab_id'], index,
                'Yes' if index == tab['current'] else 'No', entry['url'], entry['virtual_url'],
                entry['title'], entry['referrer'], tab['relative'],
            ))
        if tab['entries'] and tab['path'] not in sources:
            sources.append(tab['path'])
    return data_headers, data_list, '\n'.join(sources)
