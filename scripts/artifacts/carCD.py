import sqlite3
import plistlib
from datetime import datetime
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, kmlgen, tsv, is_platform_windows, open_sqlite_db_readonly

def timestampsconv(webkittime):
    unix_timestamp = webkittime + 978307200
    finaltime = datetime.utcfromtimestamp(unix_timestamp)
    return(finaltime)

def get_carCD(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        lastconn = contype = connected = disconnected = uid = ''
        
        with open(file_found, "rb") as fp:
            pl = plistlib.load(fp)
            #print(type(pl))
            for key, value in pl.items():
                #print(key, value)
                if key == 'LastVehicleConnection':
                    lastconn = value
                    contype = lastconn[2]
                    connected = timestampsconv(lastconn[0])
                    disconnected = timestampsconv(lastconn[1])
                    logdevinfo(f'Vehicle - Last Connected: {connected} - Last Disconnected: {disconnected} - Type: {contype}')
                    data_list.append((key, f'Last Connected: {connected} <br> Last Disconnected: {disconnected} <br> Type: {contype}'))
                    
                elif key == 'CalibrationUDID':
                    uid = value
                    logdevinfo(f'UDID: {uid}')
                    data_list.append((key, uid))
                else:
                    pass
                    
    if len(data_list) > 0:
        description = 'Last Car Connection and UDID'
        report = ArtifactHtmlReport('Last Car Connection and UDID')
        report.start_artifact_report(report_folder, 'Last Car Connection and UDID')
        report.add_script()
        data_headers = ('Key','Value')
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()
        
        tsvname = f'Last Car Connection and UDID'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('Last Car Connection and UDID')
        
__artifacts__ = {
    "carCD": (
        "Identifiers",
        ('*/Library/Caches/locationd/cache.plist'),
        get_carCD)
}