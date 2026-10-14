# pylint: disable=W0613
__artifacts_v2__ = {
    'tcc': {
        'name': 'Application Permissions',
        'description': 'Rows of the access table of TCC.db, from the extraction and from sysdiagnose archives in it. The Client (as stored) column is the client value as stored and the service name is shown without its kTCCService prefix',
        'author': '@AlexisBrignoni, Codex',
        'creation_date': '2020-12-15',
        'last_update_date': '2026-10-07',
        'requirements': 'none',
        'category': 'App Permissions',
        'notes': 'Access is the stored auth_value (0 shown as Not allowed, 2 as Allowed, 3 as Limited) or, on schemas without it, the allowed column (0 Not allowed, 1 Allowed). No source for these meanings is cited here; unrecognized values are reported as stored. Prompt Count is reported empty on schemas where the column is absent, and Last Modified is blank on schemas without a last_modified column. Client (as stored) reports the selected client value without classifying it as a bundle identifier or interpreting client_type. Original contribution and research credit: @KevinPagano3 and @johannplw.',
        'paths': (
            '*/mobile/Library/TCC/TCC.db*',
            '*/logs/Accessibility/TCC.db*',
            '*/sysdiagnose_*.tar.gz'
        ),
        'output_types': 'standard',
        'artifact_icon': 'key',
        'sample_data': {
            'ctf2020_ios12': 'iOS 12.4 | 46 rows',
            'dexter_ios18': 'iOS 18.3.2 | 141 rows',
            'felix_ios17': 'iOS 17.6.1 | 118 rows',
            'fsfull002_ios17': 'iOS 17.1 | 121 rows',
            'hc_ios18_7': 'iOS 18.7.8 | 109 rows',
            'iphone11_ios17': 'iOS 17.3 | 289 rows',
            'iphone12_ios18': 'iOS 18.7 | 143 rows',
            'iphone14plus_ios18': 'iOS 18.0 | 69 rows',
            'otto_ios17': 'iOS 17.5.1 | 185 rows',
            'abe_ios16': 'iOS 16.5 | 184 rows',
            'felix23_ios16': 'iOS 16.5 | 339 rows',
            'hickman_ios13': 'iOS 13.3.1 | 256 rows',
            'hickman_ios14': 'iOS 14.3 | 311 rows',
            'jess_ios15': 'iOS 15.0.2 | 76 rows',
            'magnet_ios16': 'iOS 16.1.1 | 66 rows',
            'ai16_ios26_sysdiag': 'iOS 26.5.2 | 160 rows',
            'hc_ios26_sysdiag': 'iOS 26 | 101 rows',
            'rodeo_ios17_sysdiag': 'iOS 17.3 | 289 rows',
        }
    }
}

import os
import re
import shutil
import sqlite3
import tarfile
import tempfile
import zlib
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, does_column_exist_in_db, convert_unix_ts_to_utc, get_sysdiagnose_files, logfunc

@artifact_processor
def tcc(context):
    data_list = []
    source_paths = set()

    # Route temp files into the report folder rather than the system temp directory
    base_temp = getattr(context, 'report_folder_base', tempfile.gettempdir())
    temp_dir = tempfile.mkdtemp(prefix='tcc_sysdiag_', dir=base_temp)

    db_paths_to_query = []
    
    # Catch TCC.db, TCC.db-wal, and TCC.db-shm to ensure complete extraction
    pattern = re.compile(r"TCC\.db(?:-wal|-shm)?$")

    try:
        for file_obj, source_path in get_sysdiagnose_files(context.get_files_found(), pattern):
            if 'PaxHeader' in source_path:
                continue

            source_name = str(context.get_relative_path(source_path))
            source_paths.add(source_path)

            # If it's a standalone extraction on disk, bypass the stream extraction and queue it for querying directly
            if ' >> ' not in source_path and not source_path.endswith('.tar.gz'):
                if source_path.endswith('TCC.db'):
                    db_paths_to_query.append((source_path, source_name))
                continue

            # Reconstruct the internal archive directory structure to ensure the db, wal, and shm remain adjacent
            parts = source_path.split(' >> ')
            if len(parts) == 2:
                archive_name = os.path.basename(parts[0])
                inner_path = parts[1].lstrip('/\\')
                out_path = os.path.join(temp_dir, archive_name, inner_path)
            else:
                # Fallback format for unexpected virtual path yields
                safe_name = source_path.replace(':', '_').replace('/', os.sep).replace('\\', os.sep).replace('>', '_')
                out_path = os.path.join(temp_dir, safe_name)

            os.makedirs(os.path.dirname(out_path), exist_ok=True)

            try:
                with open(out_path, 'wb') as f_out:
                    if hasattr(file_obj, 'buffer'):
                        shutil.copyfileobj(file_obj.buffer, f_out)
                    else:
                        while True:
                            chunk = file_obj.read(8192)
                            if not chunk:
                                break
                            if isinstance(chunk, str):
                                chunk = chunk.encode('latin-1')
                            f_out.write(chunk)
                
                # Queue the root db file for querying; the WAL and SHM will be accessed natively by SQLite
                if out_path.endswith('TCC.db'):
                    db_paths_to_query.append((out_path, source_name))
            except OSError as e:
                logfunc(f"TCC: OS Error extracting {source_path} to disk: {e}")
            except (EOFError, tarfile.TarError, zlib.error) as e:
                logfunc(f"TCC: Error reading {source_path} from its archive: {e}")

        # Process all successfully gathered TCC.db environments
        for db_path, source_name in db_paths_to_query:
            try:
                last_modified_timestamp_exists = does_column_exist_in_db(db_path, 'access', 'last_modified')
                prompt_count_exists = does_column_exist_in_db(db_path, 'access', 'prompt_count')

                if does_column_exist_in_db(db_path, 'access', 'auth_value'):
                    access = '''
                    case auth_value
                        when 0 then 'Not allowed'
                        when 2 then 'Allowed'
                        when 3 then 'Limited'
                        else auth_value
                    end as 'Access'
                    '''
                else:
                    access = '''
                    case allowed
                        when 0 then 'Not allowed'
                        when 1 then 'Allowed'
                        else allowed
                    end as 'Access'
                    '''

                # Unified query to ensure a consistent column count regardless of schema variations across different TCC.db instances
                query = f'''
                SELECT
                    {'last_modified' if last_modified_timestamp_exists else "'' AS last_modified"},
                    client,
                    service,
                    {access},
                    {'prompt_count' if prompt_count_exists else "'' AS prompt_count"}
                FROM access
                ORDER BY client, access.rowid
                '''

                db_records = get_sqlite_db_records(db_path, query)

                for record in db_records:
                    ts = convert_unix_ts_to_utc(record[0]) if last_modified_timestamp_exists and record[0] else ''
                    
                    data_list.append((
                        ts,
                        record[1],
                        record[2].replace('kTCCService', '') if record[2] else '',
                        record[3],
                        record[4],
                        source_name
                    ))
            except sqlite3.Error as e:
                logfunc(f"TCC: SQLite error querying {db_path}: {e}")

    finally:
        # Clean up the entire temporary hierarchy. ignore_errors ensures Windows locks do not crash the framework.
        shutil.rmtree(temp_dir, ignore_errors=True)

    data_headers = (
        ('Last Modified Timestamp', 'datetime'),
        'Client (as stored)',
        'Service',
        'Access',
        'Prompt Count',
        'Source File'
    )

    return data_headers, data_list, '\n'.join(sorted(source_paths))