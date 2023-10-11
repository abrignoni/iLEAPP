import sqlite3
import textwrap

from scripts.builds_ids import OS_build
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_biomeSync(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('.db'):
            continue # Skip all other files
    
        db = open_sqlite_db_readonly(file_found)

        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(last_sync_date,'unixepoch'),
        device_identifier,
        name,
        case platform
            when 1 then 'iPad'
            when 2 then 'iPhone'
            when 4 then 'macOS'
            when 6 then 'watchOS'
            else 'Unknown'
        end,
        model,
        case me
            when 0 then ''
            when 1 then 'Yes'
        end as 'Local Device'
        from DevicePeer
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:

            report = ArtifactHtmlReport('Biome Sync - Devices')
            report.start_artifact_report(report_folder, 'Biome Sync - Devices')
            report.add_script()
            data_headers = ('Last Sync Timestamp','Device ID','Name','Device Type','OS Build','OS Version','Local Device') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
            
                for key, value in OS_build.items():
                    if str(row[4]) == key:
                        os_build = value
                        break
                    else: os_build = 'Unknown'
            
                data_list.append((row[0],row[1],row[2],row[3],row[4],os_build,row[5]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Biome Sync - Devices'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Biome Sync - Devices'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Biome Sync - Devices data available')
        
            db.close()

__artifacts__ = {
    "biomeSync": (
        "Biome Sync",
        ('**/Biome/sync/sync.db*'),
        get_biomeSync)
}