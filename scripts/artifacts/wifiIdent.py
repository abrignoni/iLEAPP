import plistlib
import struct
from datetime import datetime
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, kmlgen, tsv, is_platform_windows, open_sqlite_db_readonly

def timestampsconv(webkittime):
    unix_timestamp = webkittime + 978307200
    finaltime = datetime.utcfromtimestamp(unix_timestamp)
    return(finaltime)

def get_wifiIdent(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        with open(file_found, "rb") as fp:
            pl = plistlib.load(fp)
            #print(type(pl))
            for key, value in pl.items():
                #print(key, value)
                if key == 'Interfaces':
                    for y in value:
                        #print(y)
                        hexstring = (y['IOMACAddress'])
                        hexstring = "%x:%x:%x:%x:%x:%x" % struct.unpack("BBBBBB",hexstring)
                        userdefinedname = y['SCNetworkInterfaceInfo']['UserDefinedName']
                        bsdname = y['BSD Name']
                        
                        data_list.append((hexstring, userdefinedname, bsdname))
                        logdevinfo(f'MAC Address: {hexstring} - User Defined Name: {userdefinedname} - BSD Name: {bsdname}')
                    
    if len(data_list) > 0:
        description = 'WIFI Identifiers'
        report = ArtifactHtmlReport('WIFI Identifiers')
        report.start_artifact_report(report_folder, 'WIFI Identifiers')
        report.add_script()
        data_headers = ('MAC Address','User Defined Name','BSD Name')
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()
        
        tsvname = f'WIFI Identifiers'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('WIFI Identifiers')
        
__artifacts__ = {
    "wifiIdent": (
        "Identifiers",
        ('*/preferences/SystemConfiguration/NetworkInterfaces.plist'),
        get_wifiIdent)
}