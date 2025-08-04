''' applicationStateDB.py - artifact plugin for applicationState.db

This artifact plugin focusses on the XBApplicationSnapshotManifest BLOBs in
applicationState.db. Initial experiments on an iPhone 8 with iOS version 16.7.7
indicate that the timestamps in these BLOBs are only stored or updated at a
moment when a user interacts with a device, for example when switching between
apps using the app selector.

When the device in our experiment was left untouched for a period of hours or
days, the timestamps were not updated. This indicates that the timestamps can
be used to investigate hypothesis concerning user-activity at the specific time
periods. A write-up of our experiments will be published online at which point
this docstring will be updated to contain the link to the write-up.

Support for applicationState.db is already present in applicationstate.py, but
that analysis is focussed on obtaining the bundleIdentifier, bundlePath and
sandboxPath. The XBApplicationSnapshotManifest BLOBs in applicationState.db are
related to .ktx files, for which support is also already available in iLEAPP in
the appSnapshots.py artificat script. However, in absence of .ktx files (i.e.
with a Logical dump), parsing the relevant timestamps from applicationState.db
can still be beneficial. Thus this additional artifact plugin.

Related work:

    https://abrignoni.blogspot.com/2019/09/ios-snapshots-triage-parser-working.html
    https://gforce4n6.blogspot.com/2019/09/a-quick-look-into-ios-snapshots.html
'''

import biplist
import io
import nska_deserialize as nd
import plistlib
import sys
from collections import namedtuple as _nt

from scripts.ilapfuncs import open_sqlite_db_readonly
from scripts.ilapfuncs import artifact_processor
from scripts.ilapfuncs import logfunc


__artifacts_v2__ = {
    "get_snapshot_metadata": {
        "name": "Application Snapshot metadata",
        "description": "Extract metadata about application snapshots from applicationState.db",
        "author": "@mxkrt",
        "version": "0.1",
        "date": "2025-08-04",
        "requirements": "none",
        "category": "App usage",
        "notes": "",
        "paths": ('*/mobile/Library/FrontBoard/applicationState.db*'),
        "output_types": ['html', 'tsv']
    },
    "add_creationDates_to_tl": {
        "name": "Application Snapshot creationDate",
        "description": "adds creationDate for application snapshot to timeline",
        "author": "@mxkrt",
        "version": "0.1",
        "date": "2025-08-04",
        "requirements": "none",
        "category": "App usage",
        "notes": "",
        "paths": ('*/mobile/Library/FrontBoard/applicationState.db*'),
        "output_types": "timeline"
    },
    "add_lastUsedDates_to_tl": {
        "name": "Application Snapshot lastUsedDate",
        "description": "adds lastUsedDate for application snapshot to timeline",
        "author": "@mxkrt",
        "version": "0.1",
        "date": "2025-08-04",
        "requirements": "none",
        "category": "App usage",
        "notes": "",
        "paths": ('*/mobile/Library/FrontBoard/applicationState.db*'),
        "output_types": "timeline"
    }
}


# simply get all (application, key, value) entries, post-process in code
_query = '''SELECT application_identifier_tab.application_identifier,
                    key_tab.key,
                    kvs.value
             FROM kvs LEFT JOIN application_identifier_tab
             ON application_identifier_tab.id = kvs.application_identifier
             LEFT JOIN key_tab ON kvs.key = key_tab.id
             ORDER BY application_identifier_tab.id
          '''


# namedtuple to represent the common fields from a snapshot
_snapshot = _nt('snapshot', 'bundleID snapshot_group snapshot_index '
                            'expirationDate lastUsedDate creationDate '
                            'launchInterfaceIdentifier relativePath '
                            'groupID imageScale fullScreen name '
                            'interfaceOrientation fileLocation '
                            'backgroundStyle identifier referenceSize '
                            'contentType imageOpaque requiredOSVersion')


@artifact_processor
def get_snapshot_metadata(files_found, report_folder, seeker, wrap_text, timezone_offset):

    # look for the first occurence of applicationState.db file
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('applicationState.db'):
            break

    data_list = _get_snapshots(file_found)
    data_headers = _snapshot._fields
    return data_headers, data_list, file_found


@artifact_processor
def add_creationDates_to_tl(files_found, report_folder, seeker, wrap_text, timezone_offset):

    # look for the first occurence of applicationState.db file
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('applicationState.db'):
            break

    data_list = _get_snapshots(file_found)
    # prepend the entry with the creation date
    new_data_list = []
    for entry in data_list:
        if entry.creationDate is '':
            continue
        new_entry = [entry.creationDate] + list(entry)
        new_data_list.append(new_entry)
    data_headers = ['creationDate'] + [fld for fld in _snapshot._fields]
    return data_headers, new_data_list, file_found


@artifact_processor
def add_lastUsedDates(files_found, report_folder, seeker, wrap_text, timezone_offset):

    # look for the first occurence of applicationState.db file
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('applicationState.db'):
            break

    data_list = _get_snapshots(file_found)
    # prepend the entry with the lastUsedDate
    new_data_list = []
    for entry in data_list:
        if entry.lastUsedDate is '':
            continue
        new_entry = [entry.lastUsedDate] + list(entry)
        new_data_list.append(new_entry)
    data_headers = ['lastUsedDate'] + [fld for fld in _snapshot._fields]
    return data_headers, new_data_list, file_found


def _get_snapshots(file_found):
    ''' actually performs the query and parses the snapshot entries '''

    # perform the query
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute(_query)
    all_rows = cursor.fetchall()
    db.close()

    # abort if we have no records
    if len(all_rows) == 0:
        logfunc('No Application State data available')
        return

    # group results by application identifier
    applications = _group_records(all_rows)

    # collect results in list
    snapshot_list = []

    # iterate over the applications and collect results
    for appid, keyvals in applications.items():

        # check if we have XBApplicationSnapshotManifest that we can parse
        snap_info = keyvals.get('XBApplicationSnapshotManifest')
        snap_info = _parse_blob(appid, 'XBApplicationSnapshotManifest', snap_info)
        if snap_info is None:
            continue

        # get compatibilityInfo blob so we can extract the BundleID
        compat_info =  keyvals.get('compatibilityInfo')
        compat_info = _parse_blob(appid, 'compatibilityInfo', compat_info)
        if compat_info is None:
            # in this case, simply use application identifier as bundleID
            logfunc(f"NOTE: application {appid} has no compatibilityInfo")
            bundleID = appid
        else:
            bundleID = compat_info.get('bundleIdentifier', '')

        # check if we have the correct version (proceed anyway if not)
        version = snap_info.get('version')
        if version != 3:
            logfunc(f"NOTE: plugin was developed for BLOB version 3, encountered {version}")

        # we apparently can have multiple "XBApplicationSnapshotGroup" entries
        snapshot_groups = snap_info.get('snapshots')
        for snapshot_group, metadata in snapshot_groups.items():
            identifier = metadata.get('identifier')
            if snapshot_group != identifier:
                # we expect identifier and snapshot_group to be equal
                logfunc(f"WARNING: assumption broken on identifier field")

            # get the snapshots
            snapshots = metadata.get('snapshots')
            if snapshots is None:
                # no snapshots are stored for this app, skip
                continue

            # if we get here, we have snapshots, get the required metadata
            for idx, snapshot in enumerate(snapshots):
                # the first three fields are bundleID, snapshot_group and index
                # within the list of snapshots
                vals = [bundleID, snapshot_group, idx]
                # remaining fields are fetched from the parsed snapshot dict
                for fld in _snapshot._fields[3:]:
                    vals.append(snapshot.get(fld))
                entry = _snapshot(*vals)
                snapshot_list.append(entry)
    return snapshot_list


def _group_records(all_rows):
    ''' group the records by application, checking for duplicate keys '''

    applications = {}
    for appid, key, value in all_rows:
        if appid in applications:
            if key in applications[appid]:
                # this should not actually happen!
                logfunc(f"Warning: ignored duplicate key {key} in applicationState.db for app {appid}")
                continue
            applications[appid][key] = value
        else:
            applications[appid] = {key:value}
    return applications


def _parse_blob(appid, key, blob):
    ''' parse the given data, similar to what is done in applicationstate.py '''

    if blob is None:
        return

    plist_file_object = io.BytesIO(blob)
    if blob.find(b'NSKeyedArchiver') == -1:
        if sys.version_info >= (3, 9):
            plist = plistlib.load(plist_file_object)
        else:
            plist = biplist.readPlist(plist_file_object)
    else:
        try:
            plist = nd.deserialize_plist(plist_file_object)
        except (nd.DeserializeError, nd.biplist.NotBinaryPlistException, nd.biplist.InvalidPlistException,
                nd.plistlib.InvalidFileException, nd.ccl_bplist.BplistError, ValueError, TypeError, OSError, OverflowError) as ex:
            logfunc(f'WARNING: Failed to read blob {key} for application {appid}, error was:' + str(ex))
            return

    if not isinstance(plist, dict):
        logfunc(f'WARNING: unexpected type for blob {key} for application {appid} :' +str(type(plist)))
    else:
        return plist
