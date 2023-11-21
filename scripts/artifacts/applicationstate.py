import biplist
import io
import nska_deserialize as nd
import plistlib
import sqlite3
import sys

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, open_sqlite_db_readonly

def get_applicationstate(files_found, report_folder, seeker, wrap_text, timezone_offset):
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select ait.application_identifier as ai, kvs.value as compat_info,
    (SELECT kvs.value from kvs left join application_identifier_tab on application_identifier_tab.id = kvs.application_identifier
    left join key_tab on kvs.key = key_tab.id  
    WHERE key_tab.key='XBApplicationSnapshotManifest' and kvs.key = key_tab.id
    and application_identifier_tab.id = ait.id
    ) as snap_info
    from kvs 
    left join application_identifier_tab ait on ait.id = kvs.application_identifier
    left join key_tab on kvs.key = key_tab.id 
    where key_tab.key='compatibilityInfo' 
    order by ait.id
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        snap_info_list = []
        for row in all_rows:
            bundleid = str(row[0])
            plist_file_object = io.BytesIO(row[1])
            if row[1].find(b'NSKeyedArchiver') == -1:
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
            if plist:
                if type(plist) is dict:
                    var1 = plist.get('bundleIdentifier', '')
                    var2 = plist.get('bundlePath', '')
                    var3 = plist.get('sandboxPath', '')
                    data_list.append((var1, var2, var3))
                    if row[2]:
                        snap_info_list.append((var1, var2, var3, row[2]))
                else:
                    logfunc(f'For {row[0]} Unexpected type "' + str(type(plist)) + '" found as plist root, can\'t process')
            else:
                logfunc(f'For {row[0]}, plist could not be read!')
        report = ArtifactHtmlReport('Application State')
        report.start_artifact_report(report_folder, 'Application State DB')
        report.add_script()
        data_headers = ('Bundle ID','Bundle Path','Sandbox Path')     
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Application State'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No Application State data available')

    db.close()
    return      

__artifacts__ = {
    "applicationstate": (
        "Installed Apps",
        ('**/applicationState.db'),
        get_applicationstate)
}