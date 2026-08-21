__artifacts_v2__ = {
    "safariTabsBrowserState": {
        "name": "Safari Browser - Tabs (BrowserState)",
        "description": "Open Safari tabs from BrowserState.db",
        "author": "@abrignoni", "creation_date": "2026-06-23", "last_update_date": "2026-08-21", "requirements": "none",
        "category": "Safari Browser", "notes": "",
        "paths": ('**/Safari/BrowserState.db*',),
        "output_types": "standard", "artifact_icon": "layout",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | com.apple.mobilesafari | 3 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 2 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 1 row",
            "abe_ios16": "iOS 16.5 | 2 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 10 rows",
            "hickman_ios14": "iOS 14.3 | 3 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "safariTabsiCloud": {
        "name": "Safari Browser - iCloud Tabs",
        "description": "Safari iCloud (cloud) tabs synced across devices",
        "author": "@abrignoni", "creation_date": "2026-06-23", "last_update_date": "2026-08-21", "requirements": "none",
        "category": "Safari Browser", "notes": "",
        "paths": ('**/Safari/CloudTabs.db*',),
        "output_types": "standard", "artifact_icon": "cloud",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 2 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 3 rows",
            "fsfull002_ios17": "iOS 17.1 | 1 row",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
            "iphone12_ios18": "iOS 18.7 | 2 rows",
            "iphone14plus_ios18": "iOS 18.0 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 23 rows",
            "abe_ios16": "iOS 16.5 | 28 rows",
            "felix23_ios16": "iOS 16.5 | 2 rows",
            "hickman_ios13": "iOS 13.3.1 | 2 rows",
            "hickman_ios14": "iOS 14.3 | 4 rows",
            "jess_ios15": "iOS 15.0.2 | 2 rows",
            "magnet_ios16": "iOS 16.1.1 | 1 row",
        }
    },
    "safariTabsDatabase": {
        "name": "Safari Browser - Tabs (SafariTabs)",
        "description": "Open normal and private Safari tabs from SafariTabs.db",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-28",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Safari Browser",
        "notes": "Public and LocalProfile are normal browsing; private is private browsing. "
                 "The bookmarks.last_modified and date_closed columns are NULL on every image "
                 "tested (iOS 18.7 and 26.5.2); the per-tab timestamps and state live in the "
                 "extra_attributes / local_attributes binary plists instead.",
        "paths": ("**/Safari/SafariTabs.db*",),
        "output_types": "standard",
        "artifact_icon": "layout",
        "sample_data": {
            "hickman_ios15": "iOS 15 | 4 rows",
            "jess_ios15": "iOS 15.0.2 | 2 rows",
            "magnet_ios16": "iOS 16.1.1 | 1 row",
            "felix_ios17": "iOS 17.6.1 | 4 rows",
            "iphone14plus_ios18": "iOS 18.0 | 11 rows",
            "hc_ios18_7": "iOS 18.7.8 | 4 rows",
        },
    }
}

import io
import plistlib
from datetime import datetime, timezone

import nska_deserialize as nd

from scripts.ilapfuncs import (
    artifact_processor, does_column_exist_in_db, does_table_exist_in_db,
    get_sqlite_db_records, logfunc,
)

_PLIST_ERRORS = (nd.DeserializeError, nd.biplist.NotBinaryPlistException,
                 nd.biplist.InvalidPlistException, nd.plistlib.InvalidFileException,
                 nd.ccl_bplist.BplistError, ValueError, TypeError, OSError, OverflowError)


def _aware_utc(value):
    """Tag a naive datetime as UTC (RecordCtime/RecordMtime deserialize naive); pass others through."""
    if isinstance(value, datetime) and value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _load_blob_plist(blob):
    """Decode a CloudKit system_fields blob: NSKeyedArchiver via nska_deserialize, else plain plist."""
    if blob is None:
        return None
    obj = io.BytesIO(blob)
    if blob.find(b'NSKeyedArchiver') == -1:
        try:
            return plistlib.load(obj)
        except (plistlib.InvalidFileException, ValueError, OSError):
            return None
    try:
        return nd.deserialize_plist(obj)
    except _PLIST_ERRORS as ex:
        logfunc(f'Safari iCloud Tabs: failed to read plist, error was: {ex}')
        return None


def _yes_no(value):
    """Render a plist boolean as Yes/No, leaving an absent key blank."""
    if value is None:
        return ''
    return 'Yes' if value else 'No'


def _find(context, filename):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith(filename):
            return file_found
    return ''


@artifact_processor
def safariTabsBrowserState(context):
    data_headers = (('Associated Timestamp', 'datetime'), 'Title', 'URL', 'User Visible URL',
                    'Opened from Link', 'Private Browsing')
    data_list = []
    source_path = _find(context, 'BrowserState.db')
    if not source_path:
        return data_headers, data_list, ''

    # last_viewed_time is Apple absolute (Cocoa) time on iOS <= 18, but a Unix
    # timestamp on iOS 26+. Cocoa values for realistic dates stay well below the
    # 978307200 offset (which equals year 2032 in Cocoa time), while Unix values
    # are always above it, so the magnitude disambiguates the two encodings.
    query = '''
    SELECT
        CASE
            WHEN last_viewed_time > 978307200
                THEN datetime(last_viewed_time, 'unixepoch')
            ELSE datetime(last_viewed_time + 978307200, 'unixepoch')
        END,
        title, url, user_visible_url, opened_from_link, private_browsing
    FROM tabs
    '''
    for row in get_sqlite_db_records(source_path, query):
        data_list.append(tuple(row))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def safariTabsiCloud(context):
    data_headers = (('Created Timestamp', 'datetime'), ('Modified Timestamp', 'datetime'), 'Title',
                    'URL', 'Device Name', 'Device UUID', 'Tab UUID', 'Modified By')
    data_list = []
    source_path = _find(context, 'CloudTabs.db')
    if not source_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        cloud_tabs.system_fields, cloud_tabs.title, cloud_tabs.url,
        cloud_tab_devices.device_name, cloud_tabs.device_uuid, cloud_tabs.tab_uuid
    FROM cloud_tabs
    LEFT JOIN cloud_tab_devices ON cloud_tab_devices.device_uuid = cloud_tabs.device_uuid
    '''
    for row in get_sqlite_db_records(source_path, query):
        created = modified = mod_dev = ''
        plist = _load_blob_plist(row[0])
        if isinstance(plist, list):
            for entry in plist:
                if not isinstance(entry, dict):
                    continue
                for key, value in entry.items():
                    if key == 'RecordCtime':
                        created = value
                    elif key == 'RecordMtime':
                        modified = value
                    elif key == 'ModifiedByDevice':
                        mod_dev = value
        data_list.append((_aware_utc(created), _aware_utc(modified), row[1], row[2], row[3],
                          row[4], row[5], mod_dev))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def safariTabsDatabase(context):
    data_headers = (
        ("Last Modified", "datetime"), ("Date Closed", "datetime"), "Tab ID", "Title",
        "URL", "Parent ID", "Parent / Tab Group", "Browsing Mode",
        ("Last Visit Time", "datetime"), ("Date Last Viewed", "datetime"),
        "Opened from Link", "Tab Index", "Muted", "Showing Reader", "Tab UUID",
    )
    data_list = []
    source_path = _find(context, "SafariTabs.db")
    if not source_path or not does_table_exist_in_db(source_path, "bookmarks"):
        return data_headers, data_list, source_path

    # The attribute plists and external_uuid are absent from older/reduced
    # bookmarks schemas, so select them only when the columns really exist.
    extra_col = ('tab.extra_attributes'
                 if does_column_exist_in_db(source_path, 'bookmarks', 'extra_attributes')
                 else 'NULL')
    local_col = ('tab.local_attributes'
                 if does_column_exist_in_db(source_path, 'bookmarks', 'local_attributes')
                 else 'NULL')
    uuid_col = ('tab.external_uuid'
                if does_column_exist_in_db(source_path, 'bookmarks', 'external_uuid')
                else 'NULL')

    query = f"""
        WITH RECURSIVE ancestry(tab_id, ancestor_id, parent_id, ancestor_title, depth) AS (
            SELECT id, id, parent, title, 0
            FROM bookmarks
            WHERE url IS NOT NULL AND trim(url) != '' AND COALESCE(deleted, 0) = 0
            UNION ALL
            SELECT ancestry.tab_id, parent.id, parent.parent, parent.title, ancestry.depth + 1
            FROM ancestry
            JOIN bookmarks AS parent ON parent.id = ancestry.parent_id
            WHERE ancestry.depth < 20
        ),
        tab_context AS (
            SELECT tab_id,
                   MAX(CASE WHEN lower(ancestor_title) IN ('private', 'privatepinned')
                            THEN 1 ELSE 0 END) AS is_private
            FROM ancestry
            GROUP BY tab_id
        )
        SELECT CASE WHEN tab.last_modified IS NULL THEN NULL
                    WHEN tab.last_modified > 978307200
                        THEN datetime(tab.last_modified, 'unixepoch')
                    ELSE datetime(tab.last_modified + 978307200, 'unixepoch') END,
               CASE WHEN tab.date_closed IS NULL THEN NULL
                    WHEN tab.date_closed > 978307200
                        THEN datetime(tab.date_closed, 'unixepoch')
                    ELSE datetime(tab.date_closed + 978307200, 'unixepoch') END,
               tab.id, tab.title, tab.url, tab.parent,
               COALESCE(parent.title, CAST(tab.parent AS TEXT)),
               CASE
                   WHEN lower(CAST(tab.parent AS TEXT)) = 'private'
                        OR tab_context.is_private = 1 THEN 'Private'
                   WHEN lower(CAST(tab.parent AS TEXT)) IN ('public', 'localprofile', 'local')
                        THEN 'Normal'
                   ELSE 'Normal'
               END,
               {extra_col}, {local_col}, {uuid_col}
        FROM bookmarks AS tab
        LEFT JOIN bookmarks AS parent ON parent.id = tab.parent
        LEFT JOIN tab_context ON tab_context.tab_id = tab.id
        WHERE tab.url IS NOT NULL AND trim(tab.url) != '' AND COALESCE(tab.deleted, 0) = 0
        ORDER BY tab.order_index
    """
    for row in get_sqlite_db_records(source_path, query):
        # Safari keeps the per-tab timestamps and state in two binary plists rather
        # than in table columns: LastVisitTime/OpenedFromLink/TabIndex/IsMuted/
        # ShowingReader in local_attributes, DateLastViewed in extra_attributes.
        extra = _load_blob_plist(row[8])
        local = _load_blob_plist(row[9])
        extra = extra if isinstance(extra, dict) else {}
        local = local if isinstance(local, dict) else {}
        data_list.append((
            row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
            _aware_utc(local.get('LastVisitTime', '')),
            _aware_utc(extra.get('DateLastViewed', '')),
            _yes_no(local.get('OpenedFromLink')),
            local.get('TabIndex', ''),
            _yes_no(local.get('IsMuted')),
            _yes_no(local.get('ShowingReader')),
            row[10] or '',
        ))

    return data_headers, data_list, context.get_relative_path(source_path)
