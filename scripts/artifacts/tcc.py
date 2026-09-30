__artifacts_v2__ = {
    'tcc': {
        'name': 'Application Permissions',
        'description': 'Extract application permissions from TCC.db database',
        'author': '@AlexisBrignoni - @KevinPagano3 - @johannplw',
        'creation_date': '2020-12-15',
        'last_update_date': '2026-09-29',
        'requirements': 'none',
        'category': 'App Permissions',
        'notes': 'auth_value meanings follow community-established TCC research; unrecognized values are reported as stored.',
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
            'felix23_ios16': 'iOS 16.5 | 127 rows',
            'hickman_ios13': 'iOS 13.3.1 | 130 rows',
            'hickman_ios14': 'iOS 14.3 | 154 rows',
            'jess_ios15': 'iOS 15.0.2 | 76 rows',
            'magnet_ios16': 'iOS 16.1.1 | 66 rows',
        }
    }
}

import os
import tempfile
import shutil
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, does_column_exist_in_db, convert_unix_ts_to_utc, get_sysdiagnose_files

@artifact_processor
def tcc(context):
    data_list = []
    source_paths = set()

    for file_obj, source_path in get_sysdiagnose_files(context.get_files_found(), "TCC.db"):
        source_name = str(context.get_relative_path(source_path))
        source_paths.add(source_path)

        db_path = source_path
        temp_db = None

        # Materialize the SQLite database to disk if it is streamed from a sysdiagnose archive
        if not os.path.isfile(source_path):
            temp_db = tempfile.NamedTemporaryFile(delete=False)
            try:
                if hasattr(file_obj, 'buffer'):
                    shutil.copyfileobj(file_obj.buffer, temp_db)
                else:
                    while True:
                        chunk = file_obj.read(8192)
                        if not chunk:
                            break
                        if isinstance(chunk, str):
                            chunk = chunk.encode('latin-1')
                        temp_db.write(chunk)
                temp_db.close()
                db_path = temp_db.name
            except Exception:
                temp_db.close()
                os.unlink(temp_db.name)
                continue

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
        except Exception:
            pass
        finally:
            # Clean up the temporary materialized database
            if temp_db and os.path.exists(temp_db.name):
                try:
                    os.unlink(temp_db.name)
                except OSError:
                    # Windows holds a lock if the SQLite connection failed to close gracefully
                    pass

    # Unified headers to support multiple databases with varying schemas in a single table output
    data_headers = (
        ('Last Modified Timestamp', 'datetime'),
        'Bundle ID',
        'Service',
        'Access',
        'Prompt Count',
        'Source File'
    )

    return data_headers, data_list, '\n'.join(sorted(source_paths))