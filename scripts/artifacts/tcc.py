__artifacts_v2__ = {
    'tcc': {
        'name': 'Application Permissions',
        'description': 'Extract application permissions from TCC.db database',
        'author': '@AlexisBrignoni - @KevinPagano3 - @johannplw - @C_Peter',
        'creation_date': '2020-12-15',
        'last_update_date': '2025-06-04',
        'requirements': 'none',
        'category': 'App Permissions',
        'notes': '',
        'paths': ('*/mobile/Library/TCC/TCC.db*','*/logs/Accessibility/TCC.db*','**/sysdiagnose_*.tar.gz'),
        'output_types': 'standard',
        'artifact_icon': 'key'
    }
}

import tarfile
import tempfile
import os

from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records, does_column_exist_in_db, \
    convert_unix_ts_to_utc


@artifact_processor
def tcc(files_found, report_folder, seeker, wrap_text, timezone_offset):
    temp_db = None
    for file_found in files_found:
        filename = os.path.basename(str(file_found))
        if filename == "TCC.db":
            source_path = get_file_path(files_found, filename)
            report_path = source_path
            break
        elif 'sysdiagnose_' in filename and not "IN_PROGRESS_" in filename:
            report_path = get_file_path(files_found, filename)
            tar = tarfile.open(report_path)
            root = tar.getmembers()[0].name.split('/')[0]
            try:
                tarf = tar.extractfile(f"{root}/logs/Accessibility/TCC.db")
                temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
                temp_db.write(tarf.read())
                temp_db.flush()
                temp_db.close()
                source_path = temp_db.name
            except:
                source_path = get_file_path(files_found, "TCC.db")
                report_path = source_path
                continue
        else:
            source_path = get_file_path(files_found, "TCC.db")
            report_path = source_path
            continue

    data_list = []

    last_modified_timestamp_exists = does_column_exist_in_db(
        source_path, 'access', 'last_modified')

    if does_column_exist_in_db(source_path, 'access', 'auth_value'):
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

    prompt_count_exists = does_column_exist_in_db(
        source_path, 'access', 'prompt_count')

    query = f'''
    SELECT
        {'last_modified,' if last_modified_timestamp_exists else ''}
        client,
        service,
        {access}
        {',prompt_count' if prompt_count_exists else ''}
    FROM access
    ORDER BY client
    '''

    if last_modified_timestamp_exists:
        data_headers = (
            ('Last Modified Timestamp', 'datetime'),
            'Bundle ID',
            'Service',
            'Access')
    else:
        data_headers = ('Bundle ID', 'Service', 'Access', 'Prompt Count')

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        if last_modified_timestamp_exists:
            last_modified_timestamp = convert_unix_ts_to_utc(
                record['last_modified'])
            data_list.append(
                (last_modified_timestamp, record[1],
                 record[2].replace('kTCCService', ''), record[3]))
        else:
            data_list.append((record[1], record[2].replace('kTCCService', ''),
                              record[3], record[4]))

    if temp_db and os.path.exists(temp_db.name):
        try: os.remove(temp_db.name)
        except: pass
    
    return data_headers, data_list, report_path
