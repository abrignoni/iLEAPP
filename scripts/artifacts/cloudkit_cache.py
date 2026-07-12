""" cloudkit_cache.py """
__artifacts_v2__ = {
    "cloudkit_snapshots": {
        "name": "iCloud Backup Snapshots",
        "description": "Parses snapshot information from CloudKit cache",
        "author": "@JamesHabben",
        "creation_date": "2023-04-11",
        "last_update_date": "2026-05-30",
        "requirements": "none",
        "category": "CloudKit",
        "notes": "",
        "paths": ('*/Library/Caches/Backup/cloudkit_cache.db*',),
        "output_types": "standard",
        "artifact_icon": "cloud",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 3 rows",
            "dexter_ios18": "iOS 18.3.2 | 3 rows",
            "felix_ios17": "iOS 17.6.1 | 3 rows",
            "fsfull002_ios17": "iOS 17.1 | 3 rows",
            "hc_ios18_7": "iOS 18.7.8 | 4 rows",
            "iphone11_ios17": "iOS 17.3 | 3 rows",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "iphone14plus_ios18": "iOS 18.0 | 3 rows",
            "otto_ios17": "iOS 17.5.1 | 2 rows",
            "abe_ios16": "iOS 16.5 | 3 rows",
            "felix23_ios16": "iOS 16.5 | 3 rows",
            "hickman_ios13": "iOS 13.3.1 | 3 rows",
            "hickman_ios14": "iOS 14.3 | 3 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 1 row",
        }
    },
    "cloudkit_files": {
        "name": "iCloud Backup Files",
        "description": "Parses file listings from CloudKit cache snapshots",
        "author": "@JamesHabben",
        "creation_date": "2023-04-11",
        "last_update_date": "2026-05-30",
        "requirements": "none",
        "category": "CloudKit",
        "notes": "",
        "paths": ('*/Library/Caches/Backup/cloudkit_cache.db*',),
        "output_types": "standard",
        "artifact_icon": "file-text",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 11216 rows",
            "felix_ios17": "iOS 17.6.1 | 4537 rows",
            "fsfull002_ios17": "iOS 17.1 | 5658 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 11377 rows",
            "iphone12_ios18": "iOS 18.7 | 2970 rows",
            "iphone14plus_ios18": "iOS 18.0 | 3166 rows",
            "otto_ios17": "iOS 17.5.1 | 10037 rows",
            "abe_ios16": "iOS 16.5 | 9037 rows",
            "felix23_ios16": "iOS 16.5 | 4672 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 9004 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 1744 rows",
        }
    }
}

import nska_deserialize as nd

from scripts.ilapfuncs import (
    artifact_processor,
    get_sqlite_db_records,
    open_sqlite_db_readonly,
    convert_unix_ts_to_utc,
    convert_plist_date_to_utc
)

from datetime import datetime as _dt

def _safe_plist_date(value):
    """Convert plist <date> objects to UTC; pass strings/None through unchanged."""
    return convert_plist_date_to_utc(value) if isinstance(value, _dt) else value


def format_size(size):
    """
    Formats a byte size into a human-readable string with appropriate units (B, KiB, MiB, etc.).
    """
    if size is None or size == 0:
        return "0 B"
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PiB"


@artifact_processor
def cloudkit_snapshots(context):
    """
    Extracts iCloud backup snapshot metadata from the cloudkit_cache.db database.
    """
    files_found = context.get_files_found()
    data_list = []
    source_path = ""

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('cloudkit_cache.db'):
            continue

        source_path = context.get_relative_path(file_found)
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute('''
            SELECT 
                snapshotID, 
                committed, 
                created, 
                snapshot 
            FROM Snapshots
        ''')
        snapshots = cursor.fetchall()

        for snapshot in snapshots:
            snapshot_id = snapshot[0]
            committed = snapshot[1]
            created_ts = convert_unix_ts_to_utc(snapshot[2])

            deserialized_plist = nd.deserialize_plist_from_string(snapshot[3])

            mod_date = _safe_plist_date(deserialized_plist.get('SnapshotModificationDate'))
            device_uuid = deserialized_plist.get('DeviceUUID')
            product_version = deserialized_plist.get('ProductVersion')
            backup_type = deserialized_plist.get('BackupType')
            device_name = deserialized_plist.get('DeviceName')
            backup_reason = deserialized_plist.get('BackupReason')
            snapshot_created = _safe_plist_date(deserialized_plist.get('SnapshotCreated'))
            is_allowed_cellular = deserialized_plist.get('IsBackupAllowedOnCellular')

            # Calculate file count and total size
            cursor.execute('''
                SELECT count(*), sum(Files.size)
                FROM Files
                JOIN Manifests ON Files.manifestID = Manifests.manifestID
                WHERE Manifests.snapshotID = ?
            ''', (snapshot_id,))
            stats = cursor.fetchone()
            file_count = stats[0] if stats else 0
            total_size = stats[1] if stats else 0
            formatted_size = format_size(total_size)

            data_list.append((
                snapshot_id,
                committed,
                created_ts,
                mod_date,
                snapshot_created,
                device_uuid,
                device_name,
                product_version,
                backup_type,
                backup_reason,
                is_allowed_cellular,
                file_count,
                formatted_size
            ))

        db.close()

    data_headers = (
        'Snapshot ID',
        'Committed',
        ('Created Timestamp', 'datetime'),
        ('Snapshot Modification Timestamp', 'datetime'),
        ('Snapshot Created Timestamp', 'datetime'),
        'Device UUID',
        'Device Name',
        'Product Version',
        'Backup Type',
        'Backup Reason',
        'Is Backup Allowed On Cellular',
        'File Count',
        'Total File Size'
    )

    return data_headers, data_list, source_path


@artifact_processor
def cloudkit_files(context):
    """
    Extracts file listings associated with iCloud backup snapshots from the cloudkit_cache.db database.
    """
    files_found = context.get_files_found()
    data_list = []
    source_path = ""

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('cloudkit_cache.db'):
            continue

        source_path = context.get_relative_path(file_found)

        query = '''
            SELECT 
                Manifests.snapshotID,
                Files.modified,
                Files.relativePath,
                Files.fileID,
                Files.domain,
                CASE
                    WHEN Files.deleted = 0 THEN 'False'
                    WHEN Files.deleted = 1 THEN 'True'
                END AS deleted,
                CASE
                    WHEN Files.fileType = 0 THEN 'File'
                    WHEN Files.fileType = 1 THEN 'Folder'
                END AS file_type,  
                Files.size,
                Files.protectionClass,
                Manifests.manifestID
            FROM Manifests
            LEFT JOIN Files ON Files.manifestID = Manifests.manifestID
        '''

        db_records = get_sqlite_db_records(file_found, query)
        for record in db_records:
            modified_ts = convert_unix_ts_to_utc(record[1]) if record[1] else ""

            data_list.append((
                record[0],    # Snapshot ID
                modified_ts,  # Modified
                record[2],    # Relative Path
                record[3],    # File ID
                record[4],    # File Domain
                record[5],    # Deleted
                record[6],    # File Type
                record[7],    # Size
                record[8],    # Protection Class
                record[9]     # ManifestID
            ))

    data_headers = (
        'Snapshot ID',
        ('Modified', 'datetime'),
        'Relative Path',
        'File ID',
        'File Domain',
        'Deleted',
        'File Type',
        'Size',
        'Protection Class',
        'ManifestID'
    )

    return data_headers, data_list, source_path
