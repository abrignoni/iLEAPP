''' applicationStateDB.py - artifact plugin for applicationState.db

This artifact plugin analyses applicationState.db files. The original plugin by
Alexis Brignoni had basic support for applicationState.db files by extracting
bundleIdentifier, bundlePath and sandboxPath. This new version includes a
refactored version of the original plugin and adds support for
XBApplicationSnapshotManifest BLOBs in applicationState.db records.

Initial experiments on an iPhone 8 with iOS version 16.7.7 indicate that the
timestamps in these BLOBs are only stored or updated at a moment when a user
interacts with a device, for example when switching between apps using the app
selector. Note that the timestamps do not necessarily reflect the moment at
which the corresponding app was actively used in the foreground, so be careful
with the interpretation of these records.

When the device in our experiment was left untouched for a period of hours or
days, the timestamps were not updated. This indicates that the timestamps can
be used to investigate hypothesis concerning user-activity at the specific time
periods. A write-up of our experiments will be published online at which point
a link will be added to this plugin.

The XBApplicationSnapshotManifest BLOBs in applicationState.db are
related to .ktx files, for which support is also already available in iLEAPP in
the appSnapshots.py artifact script. However, in absence of .ktx files (i.e.
with a Logical dump), parsing the relevant timestamps from applicationState.db
can still be beneficial. Thus this additional artifact plugin.

Related work:

    https://abrignoni.blogspot.com/2019/09/ios-snapshots-triage-parser-working.html
    https://gforce4n6.blogspot.com/2019/09/a-quick-look-into-ios-snapshots.html
'''

__artifacts_v2__ = {
    "get_installed_apps": {
        "name": "Application State",
        "description": "Extract information about bundle container path and data path for Applications",
        "author": "@AlexisBrignoni - @mxkrt",
        "creation_date": "2025-08-27",
        "last_update_date": "2025-10-09",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "",
        "paths": ('*/mobile/Library/FrontBoard/applicationState.db*'),
        "output_types": ["html","tsv","lava"],
        "artifact_icon": "package"
    },
    "get_snapshot_creationDate": {
        "name": "Application Snapshot",
        "description": "Extract XBApplicationSnapshotManifest records from applicationState.db. " +\
                       "NOTE: these timestamps do not always indicate application usage " +\
                       "but experiments on an iPhone 8 with iOS 16.7.7 suggest that these " +\
                       "timestamps do indicate user-interaction with the " +\
                       "device, such as switching between apps.",
        "author": "@mxkrt",
        "creation_date": "2025-08-04",
        "last_update_date": "2025-10-09",
        "requirements": "none",
        "category": "Device Usage",
        "notes": "",
        "paths": ('*/mobile/Library/FrontBoard/applicationState.db*'),
        "output_types": "standard",
        "artifact_icon": "smartphone"
    },
    "get_snapshot_lastUsedDate": {
        "name": "Application Snapshot lastUsedDate",
        "description": "Extract XBApplicationSnapshotManifest records with a " +\
                       "lastUsedDate from applicationState.db. " +\
                       "NOTE: these timestamps do not always indicate application usage " +\
                       "but experiments on an iPhone 8 with iOS 16.7.7 suggest that these " +\
                       "timestamps do indicate user-interaction with the " +\
                       "device, such as switching between apps.",
        "author": "@mxkrt",
        "creation_date": "2025-08-04",
        "last_update_date": "2025-10-09",
        "requirements": "none",
        "category": "Device Usage",
        "notes": "",
        "paths": ('*/mobile/Library/FrontBoard/applicationState.db*'),
        "output_types": "standard",
        "artifact_icon": "smartphone"
    }
}

from collections import namedtuple as _nt
from scripts.ilapfuncs import artifact_processor, get_file_path,logfunc, open_sqlite_db_readonly, get_plist_content


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
_snapshot = _nt('snapshot', 'creationDate bundleID snapshot_group '
                            'snapshot_index expirationDate lastUsedDate '
                            'launchInterfaceIdentifier relativePath '
                            'groupID imageScale fullScreen name '
                            'interfaceOrientation fileLocation '
                            'backgroundStyle identifier referenceSize '
                            'contentType imageOpaque requiredOSVersion')

# display headers for the snapshot analysis results
_snapshot_headers = ('Creation Date', 'Bundle ID', 'Snapshot Group',
                     'Snapshot Index', 'Expiration Date', 'Last Used Date',
                     'Launch Interface Identifier', 'Relative Path',
                     'Group ID', 'Image Scale', 'Fullscreen', 'Name',
                     'Interface Orientation', 'File Location',
                     'Background Style', 'Identifier', 'Reference Size',
                     'Content Type', 'Image Opaque', 'Required OS Version')


@artifact_processor
def get_installed_apps(context):
    ''' get bundle container path and sandbox data path for installed applications '''
    
    files_found = context.get_files_found()
    file_found = get_file_path(files_found, 'applicationState.db')

    # get the records grouped by application identifier
    applications = _do_query(file_found)
    if applications is None:
        return (), [], ''

    data_headers = ('Bundle ID','Bundle Path','Sandbox Path')
    data_list = []
    # iterate over the applications and collect results
    for appid, keyvals in applications.items():
        compat_info =  keyvals.get('compatibilityInfo')
        compat_info = get_plist_content(compat_info)
        if compat_info is None or not isinstance(compat_info, dict):
            logfunc(f"NOTE: application {appid} has no compatibilityInfo")
            continue
        else:
            bundleID = compat_info.get('bundleIdentifier', '')
            bundlePath = compat_info.get('bundlePath', '')
            sandboxPath = compat_info.get('sandboxPath', '')
            data_list.append((bundleID, bundlePath, sandboxPath))
    return data_headers, data_list, file_found


@artifact_processor
def get_snapshot_creationDate(context):
    ''' main artifact processor, parses XBApplicationSnapshotManifest snapshots '''

    files_found = context.get_files_found()
    file_found = get_file_path(files_found, 'applicationState.db')

    data_list = _get_snapshots(file_found)
    # TODO: Shouldn't we do any date handling?
    data_headers = _snapshot_headers[:]
    data_headers[0] = ('Creation Date', 'datetime')
    data_headers[4] = ('Expiration Date', 'datetime')
    data_headers[5] = ('Last Used Date', 'datetime')
    return data_headers, data_list, file_found


@artifact_processor
def get_snapshot_lastUsedDate(context):
    ''' add the lastUsedDate for each snapshot to the timeline '''

    # for file_found in context.get_files_found():
    #     file_found = str(file_found)
    #     if file_found.endswith('applicationState.db'):
    #         break

    files_found = context.get_files_found()
    file_found = get_file_path(files_found, 'applicationState.db')

    data_list = _get_snapshots(file_found)
    new_data_list = []
    for entry in data_list:
        if entry.lastUsedDate == '':
            continue
        # swap lastUsedDate and creationDate columns,
        # keeping other fields in the same place
        new_entry = [entry.lastUsedDate]
        for fld in _snapshot._fields:
            if fld == 'lastUsedDate':
                new_entry.append(entry.creationDate)
            elif fld == 'creationDate':
                continue
            else:
                new_entry.append(getattr(entry, fld))
        new_data_list.append(new_entry)

    # swap Last Used Date and Creation Date in headers as well
    last_idx = _snapshot_headers.index('Last Used Date')
    new_headers = [hdr for hdr in _snapshot_headers[1:] if hdr != 'Last Used Date']
    new_headers.insert(0, 'Last Used Date')
    new_headers.insert(last_idx, 'Creation Date')

    return new_headers, new_data_list, file_found


def _do_query(file_found):
    ''' perform the query and return all records grouped by application '''

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
    return applications


def _get_snapshots(file_found):
    ''' process the snapshot entries in XBApplicationSnapshotManifest records
    '''

    # get the records grouped by application
    applications = _do_query(file_found)
    if applications is None:
        return

    # collect results in list
    snapshot_list = []

    # iterate over the applications and collect results
    for appid, keyvals in applications.items():

        # check if we have XBApplicationSnapshotManifest that we can parse
        snap_info = keyvals.get('XBApplicationSnapshotManifest')
        snap_info = get_plist_content(snap_info)
        if snap_info is None or not isinstance(snap_info, dict):
            continue

        # get compatibilityInfo blob so we can extract the BundleID
        compat_info =  keyvals.get('compatibilityInfo')
        compat_info = get_plist_content(compat_info)
        if compat_info is None or not isinstance(compat_info, dict):
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
                # first get the creationDate, which is used as first field
                vals = [snapshot.get('creationDate')]
                # next three fields are bundleID, snapshot_group and index
                # within the list of snapshots
                vals.extend([bundleID, snapshot_group, idx])
                # remaining fields are fetched from the parsed snapshot dict
                for fld in _snapshot._fields[4:]:
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
