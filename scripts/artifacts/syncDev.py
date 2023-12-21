import sqlite3
import scripts.builds_ids
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly


def get_syncDev(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('sync.db'):
            db = open_sqlite_db_readonly(file_found)
            db.row_factory = sqlite3.Row 
            cursor = db.cursor()
            cursor.execute('''
            Select * from DevicePeer
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
    
    if usageentries > 0:
        data_list = []
        
        for row in all_rows:
            guid = row['device_identifier']
            me = row['me']
            name = row['name']
            model = row['model']
            platform = row['platform']
            lastsyncdate = row['last_sync_date']
            
            platformtext = scripts.builds_ids.platforms.get(platform)
            modeltext = scripts.builds_ids.OS_build.get(model)
            data_list.append((lastsyncdate,guid,model,modeltext,platform,platformtext,me,name))
            
        
        description = 'Under the Me column a 1 means remote and a 0 means local.'
        report = ArtifactHtmlReport('Sync.db - Devices')
        report.start_artifact_report(report_folder, 'Sync.db - Devices', description)
        report.add_script()
        data_headers = ('Last Sync Date','GUID','Model','Model Text','Platform','Platform Text','Me','Name' )     
        report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Media'])
        report.end_artifact_report()
        
        tsvname = 'Sync.db - Devices'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('No Sync.db - Devices data available')
    
    
__artifacts__ = {
    "syncDev": (
        "Synced Devices",
        ('*/Biome/sync/sync.db*'),
        get_syncDev)
}