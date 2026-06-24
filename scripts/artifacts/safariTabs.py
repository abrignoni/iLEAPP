__artifacts_v2__ = {
    "safariTabsBrowserState": {
        "name": "Safari Browser - Tabs (BrowserState)",
        "description": "Open Safari tabs from BrowserState.db",
        "author": "", "version": "2.0", "date": "2026-06-23", "requirements": "none",
        "category": "Safari Browser", "notes": "",
        "paths": ('**/Safari/BrowserState.db*',),
        "output_types": "standard", "artifact_icon": "layout"
    },
    "safariTabsiCloud": {
        "name": "Safari Browser - iCloud Tabs",
        "description": "Safari iCloud (cloud) tabs synced across devices",
        "author": "", "version": "2.0", "date": "2026-06-23", "requirements": "none",
        "category": "Safari Browser", "notes": "",
        "paths": ('**/Safari/CloudTabs.db*',),
        "output_types": "standard", "artifact_icon": "cloud"
    }
}

import io
import plistlib

import nska_deserialize as nd

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, logfunc

_PLIST_ERRORS = (nd.DeserializeError, nd.biplist.NotBinaryPlistException,
                 nd.biplist.InvalidPlistException, nd.plistlib.InvalidFileException,
                 nd.ccl_bplist.BplistError, ValueError, TypeError, OSError, OverflowError)


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

    query = '''
    SELECT
        datetime(last_viewed_time + 978307200, 'unixepoch'),
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
        data_list.append((created, modified, row[1], row[2], row[3], row[4], row[5], mod_dev))

    return data_headers, data_list, context.get_relative_path(source_path)
