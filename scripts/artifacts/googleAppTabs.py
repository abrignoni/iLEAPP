__artifacts_v2__ = {
    "google_app_tabs": {
        "name": "Google App - Tabs",
        "description": "Tabs the Google app (com.google.GoogleMobile) kept in its tab store, with the tab's start "
                       "and last modified times and the title and URL stored for the tab.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-04",
        "last_update_date": "2026-11-04",
        "requirements": "none",
        "category": "Google App",
        "notes": (
            'Reads GMO.SkylinerTabsPersistence/tabs.sqlite3 (table tabs) under Library/Application '
            'Support/Google/Users/<folder>. On the tested images every match was in the '
            'com.google.GoogleMobile app container; the path is not checked against the bundle identifier. '
            'The Google app is closed source, so no column here is sourced from its code. One row per tab. '
            'Last Modified and Started are last_modified_date_time and start_date_time read as seconds since '
            "2001-01-01 UTC. That epoch is measured, not sourced: each tab's pane stacks carry an NSDate per "
            'pane (_lastVisibleDate), which NSKeyedArchiver stores as seconds since 2001-01-01, and on 12 of '
            'the 13 tested tabs Last Modified was within 0.01 s of the latest pane time. On the 13th '
            '(hc_ios17_2) Last Modified was about an hour before it. Started preceded the first pane time on '
            'all 13. Title and URL are the title and url columns; on all 13 tabs the URL equalled the URL of '
            'the last pane in the backward stack. Backward Panes and Forward Panes count the panes in '
            'archived_backward_stack and archived_forward_stack, NSKeyedArchiver arrays of GMOPaneItem read '
            "with the core's plist helper; each pane is a row of Google App - Tab Panes. Current Pane ID is "
            "top_pane_id, which equalled the last backward pane's ID on all 13 tabs. Ordered Index is "
            'reported as stored: it was -1 on 10 of 13 tabs, and what -1 means is not established. Is Deleted '
            'and Deleted Date Time are the is_deleted and deleted_date_time columns, present only in the '
            'hc_ios26 schema, whose tabs table was empty. They are code-present and unexercised, reported as '
            'stored (the epoch of Deleted Date Time is not established), and blank where the columns do not '
            'exist, which is every tested row. User Folder is the Google/Users folder name; the same name '
            "occurred on all six images holding the app's Users folder, so what it is derived from is not "
            'established and it is not an account identifier. Not reported: snapshot_attributes, which held '
            "only the snapshot's layout rectangles and orientation (GMOPaneSnapshotAttributes) on every "
            'tested row. No -wal or -journal file was present on any tested image. Of the other GMO.* folders '
            'beside the tab store, none is read by this module: PageVisitData, '
            'FrequentlyVisitedContainerStorage, SessionedRecentsPersistenceInfo and CredentialProvider '
            '(credentials.sqlite3) were seen and are not covered here, nor are the other GMO.* folders '
            '(AccountConsentValue, PromoManager, Doodles, LabsAvailability, FeatureUsage, '
            'TranslateSearchboxLogging, BackgroundTask, NotificationSettingsSyncQueue, DeluxeChip, '
            'DomainsContactedSQLiteDatabase, SearchboxPrimitives), whose contents were not examined. '
            "Of the 40 registered iOS images, 6 hold the app's Users folder; "
            'abe_ios16 holds a GMO.SkylinerTabsPersistence folder with no tabs.sqlite3, and dexter_ios18 (two '
            'folders) and hc_ios26 hold an empty tabs table. The two encrypted iTunes backups were not '
            'checked; their decrypted copies hold no tab store.'
        ),
        "paths": (
            '*/Library/Application Support/Google/Users/*/GMO.SkylinerTabsPersistence/tabs.sqlite3*',
        ),
        "output_types": "standard",
        "artifact_icon": "browser",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 4 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 8 rows",
        },
    },
    "google_app_tab_panes": {
        "name": "Google App - Tab Panes",
        "description": "The panes (Google searches and web pages) archived in each Google app tab's backward and "
                       "forward pane stacks, with the last visible time, title and URL stored for each pane.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-04",
        "last_update_date": "2026-11-04",
        "requirements": "none",
        "category": "Google App",
        "notes": (
            "One row per GMOPaneItem in each tab's archived_backward_stack (Stack Backward), then its "
            "archived_forward_stack (Forward), read with the core's plist helper from tabs.sqlite3. Position "
            "counts from 0 in stored order. That the stacks are the tab's navigation history is an "
            'observation from the data, not sourced: on the 13 tested tabs the last backward pane was the '
            "tab's current pane (Current Pane Yes), the backward panes were in ascending Last Visible order, "
            "and each of the 4 forward panes (iphone12_ios18) had a Last Visible before the current pane's, "
            "which fits a pane the user went back from. Last Visible is the pane's _lastVisibleDate, an "
            'NSDate, shown in UTC. Pane Type is _navigationTarget as stored: search or web on iphone12_ios18. '
            'The hc_ios17_2 and hexordia_ios1651 panes have no _navigationTarget key (they carry '
            '_lastSignedOutURL instead), so Pane Type is blank on those 8 rows. Title and URL are _title and '
            "_URL; a search pane's URL is the Google search address with the query. In-Pane Back List and "
            "In-Pane Forward List are the pane's own _archivedBackList and _archivedForwardList, "
            'GMONavigationItem entries written as title | URL, one per line, with no time stored; the back '
            'list was filled on 7 of 25 rows and the forward list on 1. Pane ID is _paneId and joins Google '
            'App - Pane Navigation Entries. Not read: _archivedController, which was empty on iphone12_ios18 '
            '(the controller is in pane_archives.sqlite3 there) and on hc_ios17_2 and hexordia_ios1651 held '
            'an inline archive with a search query stack (GMOSearchQueryStack) or web view data in a format '
            'not established; and _snapshotIdentifier, because no file in iphone12_ios18 is named by any '
            'UUID-form tab, pane or snapshot identifier of its tabs, so no snapshot image was found to show.'
        ),
        "paths": (
            '*/Library/Application Support/Google/Users/*/GMO.SkylinerTabsPersistence/tabs.sqlite3*',
        ),
        "output_types": "standard",
        "artifact_icon": "layers",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 4 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 4 rows",
            "iphone12_ios18": "iOS 18.7 | 17 rows",
        },
    },
    "google_app_pane_navigation": {
        "name": "Google App - Pane Navigation Entries",
        "description": "The navigation entries the Google app's web view kept for each archived web pane, with the "
                       "address, title, referrer and timestamp stored for each entry.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-04",
        "last_update_date": "2026-11-04",
        "requirements": "none",
        "category": "Google App",
        "notes": (
            'Reads GMO.PaneSerializationPersistence/pane_archives.sqlite3 (table record: paneIdentifier, '
            "archivedPaneData), an NSKeyedArchiver archive of the pane's controller, read with the core's "
            "plist helper. For a web pane (GMOWebPaneController) the web view controller's "
            'webViewRestorableState holds a second archive whose protobufStorage object is a '
            "CWVWebViewProtobufStorage, the class of Chromium's embeddable web view; its storage value is a "
            'serialized web::proto::WebStateStorage '
            '(https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/web_view/internal/cwv_web_view.mm#L205-L209). '
            'That the Google app writes it with that code is inferred from the class name and from every '
            'stored value decoding, not sourced. It is decoded with the vendored blackboxprotobuf using the '
            "field numbers of Chromium's protos at commit 1c1ecc6d, the typedef of Chromium Open Tabs (iOS) "
            '(https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/web/public/session/proto/storage.proto#L18-L24, '
            'https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/web/public/session/proto/metadata.proto#L27-L32, '
            'https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/web/public/session/proto/navigation.proto#L52-L73). '
            'Each time is a Timestamp in microseconds since 1601-01-01 UTC '
            '(https://github.com/chromium/chromium/blob/1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a/ios/web/public/session/proto/proto_util.cc#L16-L19). '
            'As a check against a second record, on iphone12_ios18 each of the 19 entries whose pane is in a '
            "tab stack had a Navigation Time no more than 0.03 s after that pane's Last Visible in Google App "
            '- Tab Panes, and no entry was earlier than its Pane Created. One row per navigation entry, Index '
            'from 0 in stored order. Current Entry is Yes at last_committed_item_index, which proto3 leaves '
            'unwritten when it is 0. Pane Created and Pane Last Active are the metadata creation_time and '
            "last_active_time; Pane Last Active was earlier than the pane's Last Visible on every joined row. "
            "URL, Title and Referrer URL are the entry's url, title and referrer url; the referrer was filled "
            'on 15 of 20 entries. Virtual URL is not reported: it was empty on all 20. Tab ID is the tab '
            'whose backward or forward stack in the tabs.sqlite3 of the same Users folder holds the pane. It '
            'is blank on 1 of 20 entries, a pane no tab references; whether such a pane belonged to a closed '
            'tab is not established. Of the 19 records on iphone12_ios18, 3 are search panes '
            '(GMOSearchPaneController), which archive no web view and give no rows (their query is in the URL '
            'of Google App - Tab Panes), and 1 web pane stored no entry (its last committed index was -1). dexter_ios18 held two '
            'pane_archives.sqlite3 files with no records; no other tested image held one. Not read: the user '
            'agent, request headers and certificates cache.'
        ),
        "paths": (
            '*/Library/Application Support/Google/Users/*/GMO.PaneSerializationPersistence/pane_archives.sqlite3*',
            '*/Library/Application Support/Google/Users/*/GMO.SkylinerTabsPersistence/tabs.sqlite3*',
        ),
        "output_types": "standard",
        "artifact_icon": "list",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 20 rows",
        },
    },
}

import datetime
import struct

from google.protobuf.message import DecodeError

from scripts import blackboxprotobuf
from scripts.ilapfuncs import (artifact_processor, get_plist_content, get_sqlite_db_records, logfunc,
                               open_sqlite_db_readonly)

_UTC = datetime.timezone.utc
_COCOA_EPOCH = datetime.datetime(2001, 1, 1, tzinfo=_UTC)
_CHROMIUM_EPOCH = datetime.datetime(1601, 1, 1, tzinfo=_UTC)
_USERS = '/Google/Users/'
_TABS = 'GMO.SkylinerTabsPersistence/tabs.sqlite3'
_PANES = 'GMO.PaneSerializationPersistence/pane_archives.sqlite3'
_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError)

# WebStateStorage field numbers from Chromium's protos at 1c1ecc6d7fc09a74cce2b4ac39ba9a1bfb9ab95a,
# ios/web/public/session/proto/{storage,metadata,navigation,common}.proto, as in chromeIosOpenTabs.py.
_TIMESTAMP = {'1': {'type': 'int', 'name': ''}}  # Timestamp.microseconds
_PAGE = {'1': {'type': 'str', 'name': ''}, '2': {'type': 'str', 'name': ''}}  # page_title, page_url
_METADATA = {
    '1': {'type': 'message', 'message_typedef': _TIMESTAMP, 'name': ''},  # creation_time
    '2': {'type': 'message', 'message_typedef': _TIMESTAMP, 'name': ''},  # last_active_time
    '3': {'type': 'message', 'message_typedef': _PAGE, 'name': ''},  # active_page
    '4': {'type': 'int', 'name': ''},  # navigation_item_count
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


def _cocoa(value):
    """Seconds since 2001-01-01 UTC as an aware datetime; blank stays blank."""
    if value in (None, ''):
        return ''
    try:
        return _COCOA_EPOCH + datetime.timedelta(seconds=float(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _nsdate(value):
    """nska_deserialize returns an NSDate as a naive datetime counted from 2001-01-01, so it is UTC."""
    if isinstance(value, datetime.datetime):
        return value if value.tzinfo else value.replace(tzinfo=_UTC)
    return ''


def _chromium(value):
    """Microseconds since 1601-01-01 UTC (base::Time internal value); 0 and blank stay blank."""
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


def _url(value):
    """An NSURL as nska_deserialize returns it (NS.base and NS.relative), or a plain string."""
    if isinstance(value, dict):
        base, relative = _text(value.get('NS.base')), _text(value.get('NS.relative'))
        return relative if not base else f'{base} {relative}'.strip()
    return _text(value)


def _store(context, path, store):
    """(key, user folder, relative path) for a store file. The key is the relative path of the
    Google/Users/<folder> directory, so two app containers holding the same folder name stay apart."""
    relative = context.get_relative_path(path).replace('\\', '/')
    head = relative[:-len(store)].rstrip('/')
    folder = head.rsplit(_USERS, 1)[1] if _USERS in head else ''
    return head, folder, relative


def _stores(context, store):
    found = []
    for path in sorted(str(f) for f in context.get_files_found()):
        if path.replace('\\', '/').endswith('/' + store):
            found.append(path)
    return found


def _stack(blob, label):
    """The GMOPaneItem dictionaries of one archived pane stack, in stored order."""
    if not blob:
        return []
    value = get_plist_content(blob)
    if not isinstance(value, list):
        logfunc(f'Google App - Tabs: {label} did not decode as a list of panes and is not reported')
        return []
    return [item for item in value if isinstance(item, dict)]


def _in_pane(items):
    """The GMONavigationItem entries of a pane's own back or forward list, one per line."""
    lines = []
    for item in _list(items):
        if not isinstance(item, dict):
            continue
        title, url = _text(item.get('_title')), _url(item.get('_URL'))
        lines.append(' | '.join(part for part in (title, url) if part))
    return '\n'.join(lines)


def _read_tabs(context):
    """Every tab row of every tabs.sqlite3, with its decoded pane stacks."""
    tabs, sources = [], []
    for path in _stores(context, _TABS):
        key, folder, _ = _store(context, path, _TABS)
        db = open_sqlite_db_readonly(path)
        if db is None:
            continue
        columns = {row[1] for row in db.execute('PRAGMA table_info(tabs)')}
        db.close()
        if not columns:
            logfunc(f'Google App - Tabs: no tabs table in {context.get_relative_path(path)}')
            sources.append(path)
            continue
        extra = [name if name in columns else f'NULL AS {name}' for name in ('is_deleted', 'deleted_date_time')]
        query = ('SELECT tab_identifier, ordered_index, start_date_time, last_modified_date_time, '
                 'archived_backward_stack, archived_forward_stack, title, url, top_pane_id, '
                 f'{", ".join(extra)} FROM tabs ORDER BY start_date_time')
        for row in get_sqlite_db_records(path, query):
            label = f'tab {row[0]} in {context.get_relative_path(path)}'
            tabs.append({
                'key': key, 'folder': folder, 'tab_id': row[0], 'ordered_index': row[1],
                'started': _cocoa(row[2]), 'modified': _cocoa(row[3]),
                'backward': _stack(row[4], label + ' (backward stack)'),
                'forward': _stack(row[5], label + ' (forward stack)'),
                'title': row[6] or '', 'url': row[7] or '', 'top_pane_id': row[8] or '',
                'is_deleted': '' if row[9] is None else row[9],
                'deleted': '' if row[10] is None else row[10],
            })
        sources.append(path)
    return tabs, sources


@artifact_processor
def google_app_tabs(context):
    data_headers = (
        ('Last Modified', 'datetime'), ('Started', 'datetime'), 'Title', 'URL', 'Backward Panes',
        'Forward Panes', 'Current Pane ID', 'Ordered Index (as stored)', 'Is Deleted (as stored)',
        'Deleted Date Time (as stored)', 'Tab ID', 'User Folder',
    )
    tabs, sources = _read_tabs(context)
    data_list = [(
        tab['modified'], tab['started'], tab['title'], tab['url'], len(tab['backward']), len(tab['forward']),
        tab['top_pane_id'], tab['ordered_index'], tab['is_deleted'], tab['deleted'], tab['tab_id'],
        tab['folder'],
    ) for tab in tabs]
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def google_app_tab_panes(context):
    data_headers = (
        ('Last Visible', 'datetime'), 'Tab ID', 'Stack', 'Position', 'Current Pane', 'Pane Type (as stored)',
        'Title', 'URL', 'In-Pane Back List', 'In-Pane Forward List', 'Pane ID', 'User Folder',
    )
    tabs, sources = _read_tabs(context)
    data_list = []
    for tab in tabs:
        for stack_name, stack in (('Backward', tab['backward']), ('Forward', tab['forward'])):
            for position, pane in enumerate(stack):
                pane_id = _text(pane.get('_paneId'))
                data_list.append((
                    _nsdate(pane.get('_lastVisibleDate')), tab['tab_id'], stack_name, position,
                    'Yes' if pane_id and pane_id == tab['top_pane_id'] else 'No',
                    _text(pane.get('_navigationTarget')), _text(pane.get('_title')), _url(pane.get('_URL')),
                    _in_pane(pane.get('_archivedBackList')), _in_pane(pane.get('_archivedForwardList')),
                    pane_id, tab['folder'],
                ))
    return data_headers, data_list, '\n'.join(sources)


def _data(value):
    """NSData or NSMutableData as nska_deserialize returns it: bytes, or a dict holding NS.data."""
    if isinstance(value, dict):
        value = value.get('NS.data')
    return value if isinstance(value, bytes) else None


def _web_state(blob, label):
    """The WebStateStorage of an archived GMOWebPaneController. Returns 'no web view' for a pane that
    archives no web view controller (a search pane), or None when the pane does not decode."""
    root = get_plist_content(blob)
    if not isinstance(root, dict):
        logfunc(f'Google App - Pane Navigation Entries: {label} did not decode and is not reported')
        return None
    controller = root.get('_webViewController')
    if controller is None:
        return 'no web view'
    state = _data(controller.get('webViewRestorableState')) if isinstance(controller, dict) else None
    inner = get_plist_content(state) if state else None
    if isinstance(inner, dict) and isinstance(inner.get('protobufStorage'), dict):
        inner = inner['protobufStorage']
    storage = inner.get('storage') if isinstance(inner, dict) else None
    if isinstance(storage, dict):
        storage = _data(storage)
    if not isinstance(storage, bytes):
        logfunc(f'Google App - Pane Navigation Entries: {label} holds no web view storage and is not reported')
        return None
    try:
        value, _ = blackboxprotobuf.decode_message(storage, _WEB_STATE)
        return value
    except _DECODE_ERRORS as ex:
        logfunc(f'Google App - Pane Navigation Entries: {label} did not decode and is not reported: '
                f'{type(ex).__name__}: {ex}')
        return None


@artifact_processor
def google_app_pane_navigation(context):
    data_headers = (
        ('Navigation Time', 'datetime'), ('Pane Created', 'datetime'), ('Pane Last Active', 'datetime'),
        'Tab ID', 'Index', 'Current Entry', 'URL', 'Title', 'Referrer URL', 'Pane ID',
        'User Folder',
    )
    tabs, _ = _read_tabs(context)
    owners = {}
    for tab in tabs:
        for pane in tab['backward'] + tab['forward']:
            owners.setdefault((tab['key'], _text(pane.get('_paneId'))), tab['tab_id'])
    data_list, sources = [], []
    for path in _stores(context, _PANES):
        key, folder, relative = _store(context, path, _PANES)
        query = 'SELECT paneIdentifier, archivedPaneData FROM record ORDER BY paneIdentifier'
        without = 0
        for pane_id, blob in get_sqlite_db_records(path, query):
            state = _web_state(blob, f'pane {pane_id} in {relative}') if blob else None
            if state == 'no web view':
                without += 1
                continue
            if not isinstance(state, dict):
                continue
            metadata = state.get('2') if isinstance(state.get('2'), dict) else {}
            created = _chromium((metadata.get('1') or {}).get('1')) if isinstance(metadata.get('1'), dict) else ''
            active = _chromium((metadata.get('2') or {}).get('1')) if isinstance(metadata.get('2'), dict) else ''
            navigation = state.get('4') if isinstance(state.get('4'), dict) else {}
            current = navigation.get('1', 0)  # proto3 leaves a 0 index unwritten
            for index, item in enumerate(_list(navigation.get('2'))):
                if not isinstance(item, dict):
                    continue
                referrer = item.get('6') if isinstance(item.get('6'), dict) else {}
                stamp = item.get('4') if isinstance(item.get('4'), dict) else {}
                data_list.append((
                    _chromium(stamp.get('1')), created, active, owners.get((key, pane_id), ''), index,
                    'Yes' if index == current else 'No', _text(item.get('1')), _text(item.get('3')), _text(referrer.get('1')), pane_id, folder,
                ))
        if without:
            logfunc(f'Google App - Pane Navigation Entries: {without} pane(s) in {relative} archive no web view '
                    '(search panes) and have no navigation entries')
        sources.append(path)
    return data_headers, data_list, '\n'.join(sources)
