import datetime
import io
import nska_deserialize as nd
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly


def get_safariTabs(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if not file_found.endswith('.db'):
            continue
        
        if 'BrowserState' in file_found:
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute("""
            select
            datetime(last_viewed_time+978307200,'unixepoch'), 
            title, 
            url, 
            user_visible_url, 
            opened_from_link, 
            private_browsing
            from
            tabs
            """)

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            data_list = []    
            if usageentries > 0:
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))
            
                description = ''
                report = ArtifactHtmlReport('Safari Browser - Tabs (BrowserState)')
                report.start_artifact_report(report_folder, 'Safari Browser - Tabs (BrowserState)', description)
                report.add_script()
                data_headers = ('Last Viewed Time','Title','URL','User Visible URL','Opened from Link', 'Private Browsing')     
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = 'Safari Browser - Tabs (BrowserState)'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'Safari Browser - Tabs (BrowserState)'
                timeline(report_folder, tlactivity, data_list, data_headers)
                
            else:
                logfunc('No Safari Browser - Tabs (BrowserState) available in table')
            
            db.close()
            
        if 'CloudTabs' in file_found:
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute("""
            select
            cloud_tabs.system_fields,
            cloud_tabs.title,
            cloud_tabs.url,
            cloud_tab_devices.device_name,
            cloud_tabs.device_uuid,
            cloud_tabs.tab_uuid
            from cloud_tabs
            left join cloud_tab_devices on cloud_tab_devices.device_uuid = cloud_tabs.device_uuid
            """)

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            data_list = []    
            if usageentries > 0:
                for row in all_rows:
                
                    plist_file_object = io.BytesIO(row[0])
                    if row[0] is None:
                        pass
                    else:
                        if row[0].find(b'NSKeyedArchiver') == -1:
                            if sys.version_info >= (3, 9):
                                plist = plistlib.load(plist_file_object)
                            else:
                                plist = biplist.readPlist(plist_file_object)
                        else:
                            try:
                                plist = nd.deserialize_plist(plist_file_object)
                            except (nd.DeserializeError, nd.biplist.NotBinaryPlistException, nd.biplist.InvalidPlistException,
                                            nd.plistlib.InvalidFileException, nd.ccl_bplist.BplistError, ValueError, TypeError, OSError, OverflowError) as ex:
                                logfunc(f'Failed to read plist for {row[0]}, error was:' + str(ex))
                    
                    for x in plist:
                        for keys, values in x.items():
                            if keys == 'RecordCtime':
                                created_timestamp = values
                            if keys == 'RecordMtime':
                                modified_timestamp = values
                            if keys == 'ModifiedByDevice':
                                mod_dev = values
                                
                    data_list.append((created_timestamp, modified_timestamp, row[1], row[2], row[3], row[4], row[5], mod_dev))
            
                description = ''
                report = ArtifactHtmlReport('Safari Browser - iCloud Tabs')
                report.start_artifact_report(report_folder, 'Safari Browser - iCloud Tabs', description)
                report.add_script()
                data_headers = ('Created Timestamp','Modified Timestamp','Title','URL','Device Name','Device UUID','Tab UUID','Modified By')
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = 'Safari Browser - iCloud Tabs'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'Safari Browser - iCloud Tabs'
                timeline(report_folder, tlactivity, data_list, data_headers)
                
            else:
                logfunc('No Safari Browser - iCloud Tabs available in table')
            
            db.close()
        

__artifacts__ = {
    "safariTabs": (
        "Safari Browser",
        ('**/Safari/BrowserState.db*','**/Safari/CloudTabs.db*'),
        get_safariTabs)
}