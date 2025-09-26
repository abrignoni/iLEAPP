__artifacts_v2__ = {
    "get_cloudkitCache": {
        "name": "CloudKit",
        "description": "",
        "author": "@snoop168",
        "creation_date": "2024-05-02",
        "last_update_date": "2025-09-26",
        "requirements": "none",
        "category": "CloudKit",
        "notes": "",
        "paths": ('*/mobile/Library/Caches/Backup/cloudkit_cache.db*',),
        "output_types": "standard",
    }
}

import nska_deserialize as nd
from scripts.ilapfuncs import logfunc, open_sqlite_db_readonly, artifact_processor
from scripts.context import Context

def get_snapshots(db):
    cursor = db.cursor()
    cursor.execute('''select snapshotID, committed, datetime(created,'unixepoch') as Created_Timestamp, snapshot from Snapshots''')
    return cursor.fetchall()

def get_manifests_for_snapshot(db, snapshot_id):
    cursor = db.cursor()
    cursor.execute('''
        SELECT Manifests.manifestID,  Manifests.domain, Files.fileID,  Files.domain,  datetime(NULLIF(Files.modified, 0), 'unixepoch') as Modified_Timestamp,  Files.relativePath,
        CASE
            WHEN Files.deleted = 0 THEN 'False'
            WHEN Files.deleted = 1 THEN  'True'
        END AS deleted,
        CASE
            WHEN Files.fileType = 0 THEN 'File'
            WHEN Files.fileType = 1 THEN 'Folder'
        END AS file_type,  
        Files.size,  Files.protectionClass from Manifests
        left join files on Files.manifestID = manifests.manifestID
        where Manifests.snapshotID = ?
        ''', (snapshot_id,))
    return cursor.fetchall()

@artifact_processor
def get_cloudkitCache(context:Context):

    snapshots_array = []
    files_dictionary = {}
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('cloudkit_cache.db'):
            logfunc(f"Running artifact on: {file_found}")
            db = open_sqlite_db_readonly(file_found)
            snapshots = get_snapshots(db)

            for snapshot in snapshots:
                deserialized_plist = nd.deserialize_plist_from_string(snapshot[3])
                snapshot_data = {
                    "SnapshotID": snapshot[0],
                    "Committed": snapshot[1],
                    "Created": snapshot[2],
                    "SnapshotModificationDate": deserialized_plist['SnapshotModificationDate'],
                    "DeviceUUID": deserialized_plist['DeviceUUID'],
                    "ProductVersion": deserialized_plist['ProductVersion'],
                    "BackupType": deserialized_plist['BackupType'],
                    "DeviceName": deserialized_plist['DeviceName'],
                    "BackupReason": deserialized_plist['BackupReason'],
                    "DeviceUUID": deserialized_plist['DeviceUUID'],
                    "SnapshotCreated": deserialized_plist['SnapshotCreated'],
                    "IsBackupAllowedOnCellular": deserialized_plist['IsBackupAllowedOnCellular']
                }
                snapshots_array.append(snapshot_data)
                data_list = []
                files = get_manifests_for_snapshot(db, snapshot[0])
                for file in files:
                    #logfunc(manifest[0])

                    data_list.append((file[4], file[5], file[2], file[3],
                                      file[6], file[7], file[8], file[9], file[0], file_found))
                files_dictionary[snapshot[0]] = data_list
            db.close()
            
    data_headers = ('Modified', 'Relative Path', 'File ID', 'File Domain', 'Deleted', 'File Type', 'Size', 'Protection Class', 'ManifestID', 'Source DB')
    return data_headers, data_list, ''
