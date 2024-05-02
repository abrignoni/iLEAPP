import glob
import os
import nska_deserialize as nd
import sqlite3
import datetime
import io

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

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



def get_cloudkitCache(files_found, report_folder, seeker, wrap_text, timezone_offset):

    user_dictionary = {}
    description = 'CloudKit Cache'

    snapshots_array = []
    files_dictionary = {}
    for file_found in files_found:
        file_found = str(file_found)
        logfunc(file_found)
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
                                      file[6], file[7], file[8], file[9], file[0]))
                files_dictionary[snapshot[0]] = data_list
            db.close()

            #logfunc(str(len(snapshots_array)))
            for snapshot_record in snapshots_array:

                report = ArtifactHtmlReport(f'Cloudkit Cache - SnapshotID {snapshot_record["SnapshotID"]}')
                report.start_artifact_report(report_folder, f'Cloudkit Cache - SnapshotID {snapshot_record["SnapshotID"]}', description)

                snapshot_data_headers = ('Key', 'Value')
                #snapshot_data = [('SnapshotID', snapshot_record[0]), ('Committed', snapshot_record[1]), ('Created', snapshot_record[2])]
                report.write_artifact_data_table(snapshot_data_headers, list(snapshot_record.items()), file_found)

                report.add_section_heading("Files")
                report.add_script()
                data_headers = ('Modified', 'Relative Path', 'File ID', 'File Domain', 'Deleted', 'File Type', 'Size', 'Protection Class', 'ManifestID')
                #report.write_artifact_data_table(user_headers, user_list, '', write_location=False)
                report.write_artifact_data_table(data_headers, files_dictionary[snapshot_record['SnapshotID']], file_found, write_location=False, )
                report.end_artifact_report()

                tsvname = ''
                #tsv(report_folder, user_headers, user_list, tsvname)

    
__artifacts__ = {
    "cloudkitcache": (
        "Cloudkit",
        ('*/private/var/mobile/Library/Caches/Backup/cloudkit_cache.db*'),
        get_cloudkitCache)
}