__artifacts_v2__ = {
    "tcc": {
        "name": "TCC",
        "description": "Parses application permissions",
        "author": "@AlexisBrignoni - @KevinPagano3 - @johannplw",
        "version": "0.6",
        "date": "2023-10-24",
        "requirements": "none",
        "category": "App Permissions",
        "notes": "",
        "paths": ('*TCC.db*',),
        "function": "get_tcc"
    }
}

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, does_column_exist_in_db, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_tcc(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('TCC.db'):
            break
        
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()

    if does_column_exist_in_db(db, 'access', 'last_modified'):
        last_modified_timestamp = "datetime(last_modified,'unixepoch') as 'Last Modified Timestamp'"
    else:
        last_modified_timestamp = ""
    
    if does_column_exist_in_db(db, 'access', 'auth_value'):
        access = '''
        case auth_value
            when 0 then 'Not allowed'
            when 2 then 'Allowed'
            when 3 then 'Limited'
            else auth_value
        end as "Access"
        '''
    else:
        access = '''
        case allowed
            when 0 then 'Not allowed'
            when 1 then 'Allowed'
            else allowed
        end as "Access"
        '''

    prompt_count = does_column_exist_in_db(db, 'access', 'prompt_count')

    cursor.execute(f'''
    select {last_modified_timestamp if last_modified_timestamp else "''"},
    client,
    service,
    {access},
    {'prompt_count' if prompt_count else "''"}
    from access
    order by client
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list =[]
        for row in all_rows:
            if last_modified_timestamp:
                timestamp = convert_ts_human_to_utc(row[0])
                timestamp = convert_utc_human_to_timezone(timestamp,timezone_offset)        
                data_list.append((timestamp, row[1], row[2].replace("kTCCService",""), row[3]))
            else:
                data_list.append((row[1], row[2].replace("kTCCService",""), row[3], row[4]))

    if usageentries > 0:
        description = "Applications permissions"
        report = ArtifactHtmlReport('TCC - Permissions')
        report.start_artifact_report(report_folder, 'TCC - Permissions', description)
        report.add_script()
        if last_modified_timestamp:
            data_headers = ('Last Modified Timestamp','Bundle ID','Service','Access')
        else:
            data_headers = ('Bundle ID','Service','Access','Prompt Count')
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()
        tsvname = 'TCC - Permissions'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'TCC - Permissions'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No data available in TCC database.')
    
__artifacts__ = {
    "tcc": (
        "App Permissions",
        ('*TCC.db*'),
        get_tcc)
}
    