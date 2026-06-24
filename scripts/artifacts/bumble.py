__artifacts_v2__ = {
    "bumbleMessages": {
        "name": "Bumble - Messages",
        "description": "Bumble chat messages",
        "author": "@KevinPagano3",
        "version": "2.0",
        "date": "2022-04-16",
        "requirements": "none",
        "category": "Bumble",
        "notes": "",
        "paths": ('**/Library/Caches/Chat.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "message-circle"
    },
    "bumbleAccount": {
        "name": "Bumble - Account Details",
        "description": "Bumble local user account details (user id/name, app version, last location)",
        "author": "@KevinPagano3",
        "version": "2.0",
        "date": "2022-04-16",
        "requirements": "none",
        "category": "Bumble",
        "notes": "Last location timestamp is Cocoa/Mac absolute time, converted to UTC.",
        "paths": ('**/Documents/yap-database.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "user"
    }
}

import io
import plistlib

import nska_deserialize as nd

from scripts.ilapfuncs import (artifact_processor, get_sqlite_db_records, logfunc,
                               convert_unix_ts_to_utc, convert_cocoa_core_data_ts_to_utc)

_PLIST_ERRORS = (nd.DeserializeError, nd.biplist.NotBinaryPlistException,
                 nd.biplist.InvalidPlistException, nd.plistlib.InvalidFileException,
                 nd.ccl_bplist.BplistError, ValueError, TypeError, OSError, OverflowError)


def _load_blob_plist(blob):
    """Decode a YapDatabase value blob: NSKeyedArchiver via nska_deserialize, otherwise plain plist."""
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
        logfunc(f'Bumble: failed to read plist, error was: {ex}')
        return None


@artifact_processor
def bumbleMessages(context):
    data_headers = (('Created Timestamp', 'datetime'), ('Modified Timestamp', 'datetime'),
                    'Sender ID', 'Receiver ID', 'Message', 'Message Direction', 'Message Read')
    data_list = []

    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('Chat.sqlite'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        database2.data,
        CASE secondaryIndex_isReadIndex.isIncoming WHEN 0 THEN 'Outgoing' WHEN 1 THEN 'Incoming' END,
        CASE secondaryIndex_isReadIndex.isRead WHEN 0 THEN '' WHEN 1 THEN 'Yes' END
    FROM database2
    JOIN secondaryIndex_isReadIndex ON database2.rowid = secondaryIndex_isReadIndex.rowid
    '''
    for row in get_sqlite_db_records(source_path, query):
        plist = _load_blob_plist(row[0])
        if not isinstance(plist, dict) or 'self.dateCreated' not in plist:
            continue
        data_list.append((convert_unix_ts_to_utc(plist['self.dateCreated']),
                          convert_unix_ts_to_utc(plist.get('self.dateModified')),
                          plist.get('self.fromPersonUid', ''), plist.get('self.toPersonUid', ''),
                          plist.get('self.messageText', ''), row[1], row[2]))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def bumbleAccount(context):
    data_headers = ('Key', 'Value')
    data_list = []

    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('yap-database.sqlite'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

    query = '''
    SELECT data, key FROM database2
    WHERE key IN ('lastLocation', 'appVersion', 'userName', 'userId')
    '''
    for row in get_sqlite_db_records(source_path, query):
        plist = _load_blob_plist(row[0])
        if not isinstance(plist, dict):
            continue
        key = row[1]
        if key == 'userId':
            data_list.append(('User ID', str(plist.get('root', ''))))
        elif key == 'userName':
            data_list.append(('User Name', str(plist.get('root', ''))))
        elif key == 'appVersion':
            data_list.append(('App Version', str(plist.get('root', ''))))
        elif key == 'lastLocation':
            ts = plist.get('kCLLocationCodingKeyTimestamp')
            if ts is not None:
                data_list.append(('Timestamp', str(convert_cocoa_core_data_ts_to_utc(int(ts)))))
            data_list.append(('Last Latitude', plist.get('kCLLocationCodingKeyRawCoordinateLatitude', '')))
            data_list.append(('Last Longitude', plist.get('kCLLocationCodingKeyRawCoordinateLongitude', '')))

    return data_headers, data_list, context.get_relative_path(source_path)
