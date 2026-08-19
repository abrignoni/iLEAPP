__artifacts_v2__ = {
    "one_drive_files": {
        "name": "OneDrive - Files",
        "description": "Files and folders recorded in the OneDrive app's QTMetadata.db, with "
                       "stored timestamps, size, hash, owner and shared-by fields, sharing and "
                       "deletion state as stored, camera and location fields where present, and "
                       "a folder path reconstructed from the parent chain",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "OneDrive",
        "notes": "Timestamp columns hold Unix milliseconds and are reported in UTC; zero and "
                 "negative stored values are shown blank. Item Type, Deleted State, Sharing "
                 "Level, Vault Type and File Hash Type are undocumented codes reported as "
                 "stored. Folder Path is reconstructed by walking parentRid to the parent's "
                 "resourceId; a chain that does not resolve yields a partial or empty path. "
                 "Where fileHash and quickXorHash were both populated they held the same value "
                 "in tested data, and File Hash reports fileHash. Recent changes can sit in the "
                 "-wal sidecar; collect QTMetadata.db-wal and -shm with the database. The "
                 "database is documented at OneDrive/DatabaseQT/QTMetadata.db in the app's "
                 "shared AppGroup container by the SANS DFIR poster 'iOS Third-Party Apps "
                 "Forensics Reference Guide' (DFPS_iOS-APPS-v1.3_04-24); app data has also "
                 "been seen spelling the folder DatabaseQt, so the path pattern accepts both "
                 "spellings at any depth. Tables not parsed include item_moves, views, "
                 "search_results, my_analytics and recommendation tables.",
        "paths": ('*/DatabaseQ[Tt]/QTMetadata.db*',),
        "output_types": "all",
        "artifact_icon": "brand-onedrive",
    },
    "one_drive_accounts": {
        "name": "OneDrive - Accounts and Drives",
        "description": "Accounts and drives recorded in the OneDrive app's QTMetadata.db, with "
                       "the account id, drive path, service URLs and last sync time",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "OneDrive",
        "notes": "One row per drives row, joined to web_app on accountId and to sync_root on "
                 "the drive id. Drive Type and Server Type are undocumented codes reported as "
                 "stored. Last Sync Time is Unix milliseconds reported in UTC.",
        "paths": ('*/DatabaseQ[Tt]/QTMetadata.db*',),
        "output_types": "standard",
        "artifact_icon": "user-circle",
    },
    "one_drive_sharing_permissions": {
        "name": "OneDrive - Sharing Permissions",
        "description": "Sharing permission entries recorded in the OneDrive app's QTMetadata.db, "
                       "with the entity name, email, role as stored and the item they attach to",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "OneDrive",
        "notes": "Rows from permission_entity, joined through permission to the items row the "
                 "permission belongs to. Role, Entity Type and Link Type are reported as "
                 "stored; no value list ships in the database.",
        "paths": ('*/DatabaseQ[Tt]/QTMetadata.db*',),
        "output_types": "standard",
        "artifact_icon": "share",
    },
    "one_drive_stream_cache": {
        "name": "OneDrive - Stream Cache",
        "description": "Rows in the OneDrive app's stream_cache table, with access and sync "
                       "dates, the item they attach to and the stream file location as stored",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "OneDrive",
        "notes": "Stream Location is a path relative to the app's data area, reported as "
                 "stored; the cached content files themselves are not collected by this "
                 "artifact. Stream Type, Sync State, Progress and Error Code are undocumented "
                 "codes reported as stored. Dates are Unix milliseconds reported in UTC.",
        "paths": ('*/DatabaseQ[Tt]/QTMetadata.db*',),
        "output_types": "standard",
        "artifact_icon": "cloud-download",
    },
    "one_drive_offline_items": {
        "name": "OneDrive - Offline Selections",
        "description": "Rows in the OneDrive app's OfflineSelection.db explicit_offline_items "
                       "table, resolved to item names in QTMetadata.db when present",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "OneDrive",
        "notes": "Item Name is resolved by matching resource_id to items.resourceId in "
                 "QTMetadata.db when that database is present. The table content can reside "
                 "entirely in the -wal sidecar; collect OfflineSelection.db-wal and -shm "
                 "alongside the database.",
        "paths": ('*/DatabaseQ[Tt]/OfflineSelection.db*',
                  '*/DatabaseQ[Tt]/QTMetadata.db*'),
        "output_types": "standard",
        "artifact_icon": "cloud-off",
    },
}

from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    get_sqlite_db_records,
    null_absent_columns,
)


def _when(value):
    '''Convert a stored Unix-millisecond timestamp, keeping non-positive values empty.

    Date columns carry 0, empty strings and negative sentinel values; none of
    those is an observed event, so they are reported blank rather than as a
    misleading epoch-derived date.
    '''
    try:
        ts = int(value)
    except (TypeError, ValueError):
        return ''
    if ts <= 0:
        return ''
    return convert_unix_ts_to_utc(ts)


def _yes_no(value):
    '''Render a stored boolean, keeping absence empty.'''
    if value is None:
        return ''
    return 'Yes' if value else 'No'


def _metadata_dbs(files_found):
    return [str(f) for f in files_found if str(f).endswith('QTMetadata.db')]


def _parent_paths(db_path):
    '''Folder name chain per resourceId, walked up through parentRid.'''
    names = {}
    parents = {}
    for record in get_sqlite_db_records(
            db_path, null_absent_columns(
                db_path, 'SELECT resourceId, parentRid, name FROM items')):
        if record[0] is None:
            continue
        names[record[0]] = record[2]
        parents[record[0]] = record[1]

    def path_for(resource_id):
        chain = []
        current = parents.get(resource_id)
        seen = set()
        while current and current in names and current not in seen and len(chain) < 50:
            seen.add(current)
            chain.append(names.get(current) or '')
            current = parents.get(current)
        return '/'.join(reversed(chain))

    return path_for


def _drive_map(db_path):
    '''Map drives._id to (accountId, drivePath).'''
    drives = {}
    for record in get_sqlite_db_records(
            db_path, null_absent_columns(
                db_path, 'SELECT _id, accountId, drivePath FROM drives')):
        drives[record[0]] = (record[1], record[2])
    return drives


@artifact_processor
def one_drive_files(context):
    data_list = []
    query = '''
    SELECT itemDate, creationDate, modifiedDateOnClient, lastAccess, dateTaken,
           dateShared, deletedDateTime, name, extension, size, itemType,
           iconType, deletedState, sharingLevelValue, vaultType, isOffline,
           ownerName, ownerCid, sharedByDisplayName, sharedByEmail, fileHash,
           fileHashType, latitude, longitude, altitude, cameraMake, cameraModel,
           resourceId, parentRid, driveId
    FROM items
    ORDER BY itemDate
    '''
    for db_path in _metadata_dbs(context.get_files_found()):
        path_for = _parent_paths(db_path)
        drives = _drive_map(db_path)
        for record in get_sqlite_db_records(db_path, null_absent_columns(db_path, query)):
            account_id, drive_path = drives.get(record['driveId'], ('', ''))
            data_list.append((
                _when(record['itemDate']),
                _when(record['creationDate']),
                _when(record['modifiedDateOnClient']),
                _when(record['lastAccess']),
                _when(record['dateTaken']),
                _when(record['dateShared']),
                _when(record['deletedDateTime']),
                record['name'],
                record['extension'],
                path_for(record['resourceId']),
                record['size'],
                record['itemType'],
                record['iconType'],
                record['deletedState'],
                record['sharingLevelValue'],
                record['vaultType'],
                _yes_no(record['isOffline']),
                record['ownerName'],
                record['ownerCid'],
                record['sharedByDisplayName'],
                record['sharedByEmail'],
                record['fileHash'],
                record['fileHashType'],
                record['latitude'],
                record['longitude'],
                record['altitude'],
                record['cameraMake'],
                record['cameraModel'],
                record['resourceId'],
                drive_path,
                account_id,
                context.get_relative_path(db_path),
            ))

    data_headers = (
        ('Item Date', 'datetime'),
        ('Creation Date', 'datetime'),
        ('Modified Date On Client', 'datetime'),
        ('Last Access Date', 'datetime'),
        ('Date Taken', 'datetime'),
        ('Date Shared', 'datetime'),
        ('Deleted Date Time', 'datetime'),
        'Name',
        'Extension',
        'Folder Path',
        'Size (bytes)',
        'Item Type (as stored)',
        'Icon Type (as stored)',
        'Deleted State (as stored)',
        'Sharing Level (as stored)',
        'Vault Type (as stored)',
        'Offline',
        'Owner Name',
        'Owner CID',
        'Shared By Name',
        'Shared By Email',
        'File Hash',
        'File Hash Type (as stored)',
        'Latitude',
        'Longitude',
        'Altitude',
        'Camera Make',
        'Camera Model',
        'Resource ID',
        'Drive Path',
        'Account ID',
        'Source Path',
    )
    return data_headers, data_list, 'See Source Path column'


@artifact_processor
def one_drive_accounts(context):
    data_list = []
    query = '''
    SELECT sync_root.lastSyncTime, drives.accountId, drives.driveResourceId,
           drives.drivePath, drives.driveDisplayName, drives.driveCanonicalName,
           drives.driveType, drives.serverType, sync_root.syncedFileCount,
           web_app.webAppUrl, web_app.microsoftGraphUrl, web_app.tenantHosts
    FROM drives
    LEFT JOIN web_app ON web_app.accountId = drives.accountId
    LEFT JOIN sync_root ON sync_root.driveId = drives._id
    ORDER BY drives._id
    '''
    for db_path in _metadata_dbs(context.get_files_found()):
        for record in get_sqlite_db_records(db_path, null_absent_columns(db_path, query)):
            data_list.append((
                _when(record[0]),
                record[1],
                record[2],
                record[3],
                record[4],
                record[5],
                record[6],
                record[7],
                record[8],
                record[9],
                record[10],
                record[11],
                context.get_relative_path(db_path),
            ))

    data_headers = (
        ('Last Sync Time', 'datetime'),
        'Account ID',
        'Drive Resource ID',
        'Drive Path',
        'Drive Display Name',
        'Drive Canonical Name',
        'Drive Type (as stored)',
        'Server Type (as stored)',
        'Synced File Count',
        'Web App URL',
        'Microsoft Graph URL',
        'Tenant Hosts',
        'Source Path',
    )
    return data_headers, data_list, 'See Source Path column'


@artifact_processor
def one_drive_sharing_permissions(context):
    data_list = []
    query = '''
    SELECT pe.permissionEntityName, pe.permissionEntityEmail,
           pe.permissionEntityRole, pe.permissionEntityType,
           pe.permissionEntityLinkType, pe.permissionEntityLinkName,
           pe.permissionEntityExpiration, pe.permissionEntityUserId,
           pe.permissionScopeResourceName, i.name, i.resourceId
    FROM permission_entity pe
    LEFT JOIN permission p ON p._id = pe.parentId
    LEFT JOIN items i ON i._id = p.parentId
    ORDER BY pe._id
    '''
    for db_path in _metadata_dbs(context.get_files_found()):
        for record in get_sqlite_db_records(db_path, null_absent_columns(db_path, query)):
            data_list.append((
                record[0],
                record[1],
                record[2],
                record[3],
                record[4],
                record[5],
                _when(record[6]),
                record[7],
                record[8],
                record[9],
                record[10],
                context.get_relative_path(db_path),
            ))

    data_headers = (
        'Entity Name',
        'Entity Email',
        'Role (as stored)',
        'Entity Type (as stored)',
        'Link Type (as stored)',
        'Link Name',
        ('Expiration', 'datetime'),
        'Entity User ID',
        'Scope Resource Name',
        'Item Name',
        'Item Resource ID',
        'Source Path',
    )
    return data_headers, data_list, 'See Source Path column'


@artifact_processor
def one_drive_stream_cache(context):
    data_list = []
    query = '''
    SELECT sc.last_access_date, sc.last_sync_date,
           sc.stream_last_modification_date, i.name, i.resourceId,
           sc.streamType, sc.sync_state, sc.progress, sc.error_code,
           sc.stream_location
    FROM stream_cache sc
    LEFT JOIN items i ON i._id = sc.parentId
    ORDER BY sc.last_access_date
    '''
    for db_path in _metadata_dbs(context.get_files_found()):
        for record in get_sqlite_db_records(db_path, null_absent_columns(db_path, query)):
            data_list.append((
                _when(record[0]),
                _when(record[1]),
                _when(record[2]),
                record[3],
                record[4],
                record[5],
                record[6],
                record[7],
                record[8],
                record[9],
                context.get_relative_path(db_path),
            ))

    data_headers = (
        ('Last Access Date', 'datetime'),
        ('Last Sync Date', 'datetime'),
        ('Stream Last Modification Date', 'datetime'),
        'Item Name',
        'Item Resource ID',
        'Stream Type (as stored)',
        'Sync State (as stored)',
        'Progress (as stored)',
        'Error Code (as stored)',
        'Stream Location',
        'Source Path',
    )
    return data_headers, data_list, 'See Source Path column'


@artifact_processor
def one_drive_offline_items(context):
    files_found = [str(f) for f in context.get_files_found()]
    data_list = []

    names = {}
    for db_path in _metadata_dbs(files_found):
        for record in get_sqlite_db_records(
                db_path, null_absent_columns(
                    db_path, 'SELECT resourceId, name FROM items')):
            if record[0] is not None:
                names.setdefault(record[0], record[1])

    for db_path in files_found:
        if not db_path.endswith('OfflineSelection.db'):
            continue
        for record in get_sqlite_db_records(
                db_path,
                'SELECT account_id, owner_id, resource_id FROM explicit_offline_items'):
            data_list.append((
                record[0],
                record[1],
                record[2],
                names.get(record[2], ''),
                context.get_relative_path(db_path),
            ))

    data_headers = (
        'Account ID',
        'Owner ID',
        'Resource ID',
        'Item Name',
        'Source Path',
    )
    return data_headers, data_list, 'See Source Path column'
