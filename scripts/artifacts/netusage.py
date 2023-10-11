import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_netusage(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('.sqlite'):
            continue # Skip all other files
    
        if 'netusage' in file_found:
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            select
            datetime(ZLIVEUSAGE.ZTIMESTAMP + 978307200,'unixepoch'),
            datetime(ZPROCESS.ZFIRSTTIMESTAMP + 978307200,'unixepoch'),
            datetime(ZPROCESS.ZTIMESTAMP + 978307200,'unixepoch'),
            ZPROCESS.ZBUNDLENAME,
            ZPROCESS.ZPROCNAME,
            case ZLIVEUSAGE.ZKIND
                when 0 then 'Process'
                when 1 then 'App'
            end,
            ZLIVEUSAGE.ZWIFIIN,
            ZLIVEUSAGE.ZWIFIOUT,
            ZLIVEUSAGE.ZWWANIN,
            ZLIVEUSAGE.ZWWANOUT,
            ZLIVEUSAGE.ZWIREDIN,
            ZLIVEUSAGE.ZWIREDOUT
            from ZLIVEUSAGE
            left join ZPROCESS on ZPROCESS.Z_PK = ZLIVEUSAGE.Z_PK
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Network Usage (netusage) - App Data')
                report.start_artifact_report(report_folder, 'Network Usage (netusage) - App Data')
                report.add_script()
                data_headers = ('Last Connect Timestamp','First Usage Timestamp','Last Usage Timestamp','Bundle Name','Process Name','Type','Wifi In (Bytes)','Wifi Out (Bytes)','Mobile/WWAN In (Bytes)','Mobile/WWAN Out (Bytes)','Wired In (Bytes)','Wired Out (Bytes)') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Network Usage (netusage) - App Data'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Network Usage (netusage) - App Data'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Network Usage (netusage) - App Data data available')
            
            cursor = db.cursor()
            cursor.execute('''
            select
            datetime(ZNETWORKATTACHMENT.ZFIRSTTIMESTAMP + 978307200,'unixepoch'),
            datetime(ZNETWORKATTACHMENT.ZTIMESTAMP + 978307200,'unixepoch'),
            ZNETWORKATTACHMENT.ZIDENTIFIER,
            case ZNETWORKATTACHMENT.ZKIND
                when 1 then 'Wifi'
                when 2 then 'Cellular'
            end,
            ZLIVEROUTEPERF.ZBYTESIN,
            ZLIVEROUTEPERF.ZBYTESOUT,
            ZLIVEROUTEPERF.ZCONNATTEMPTS,
            ZLIVEROUTEPERF.ZCONNSUCCESSES,
            ZLIVEROUTEPERF.ZPACKETSIN,
            ZLIVEROUTEPERF.ZPACKETSOUT
            from ZNETWORKATTACHMENT
            left join ZLIVEROUTEPERF on ZLIVEROUTEPERF.Z_PK = ZNETWORKATTACHMENT.Z_PK
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:

                report = ArtifactHtmlReport('Network Usage (netusage) - Connections')
                report.start_artifact_report(report_folder, 'Network Usage (netusage) - Connections')
                report.add_script()
                data_headers = ('First Connection Timestamp','Last Connection Timestamp','Network Name','Cell Tower ID/Wifi MAC','Network Type','Bytes In','Bytes Out','Connection Attempts','Connection Successes','Packets In','Packets Out') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                data_list = []
                for row in all_rows:

                    if row[2] == None:
                        data_list.append((row[0],row[1],'','',row[3],row[4],row[5],row[6],row[7],row[8],row[9]))
                    else:
                        id_split = row[2].split('-')
                        netname = id_split[0]
                        id_mac = id_split[1]
                
                        data_list.append((row[0],row[1],netname,id_mac,row[3],row[4],row[5],row[6],row[7],row[8],row[9]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Network Usage (netusage) - Connections'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Network Usage (netusage) - Connections'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Network Usage (netusage) - Connections data available')
            
            db.close()
        
        if 'DataUsage' in file_found:
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            select
            datetime(ZLIVEUSAGE.ZTIMESTAMP + 978307200,'unixepoch'),
            datetime(ZPROCESS.ZFIRSTTIMESTAMP + 978307200,'unixepoch'),
            datetime(ZPROCESS.ZTIMESTAMP + 978307200,'unixepoch'),
            ZPROCESS.ZBUNDLENAME,
            ZPROCESS.ZPROCNAME,
            case ZLIVEUSAGE.ZKIND
                when 0 then 'Process'
                when 1 then 'App'
                else ZLIVEUSAGE.ZKIND
            end,
            ZLIVEUSAGE.ZWIFIIN,
            ZLIVEUSAGE.ZWIFIOUT,
            ZLIVEUSAGE.ZWWANIN,
            ZLIVEUSAGE.ZWWANOUT
            from ZLIVEUSAGE
            left join ZPROCESS on ZPROCESS.Z_PK = ZLIVEUSAGE.Z_PK
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Network Usage (DataUsage) - App Data')
                report.start_artifact_report(report_folder, 'Network Usage (DataUsage) - App Data')
                report.add_script()
                data_headers = ('Last Connect Timestamp','First Usage Timestamp','Last Usage Timestamp','Bundle Name','Process Name','Type','Wifi In (Bytes)','Wifi Out (Bytes)','Mobile/WWAN In (Bytes)','Mobile/WWAN Out (Bytes)') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Network Usage (DataUsage) - App Data'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Network Usage (DataUsage) - App Data'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Network Usage (DataUsage) - App Data data available')
            
            db.close()

__artifacts__ = {
    "netusage": (
        "Network Usage",
        ('**/netusage.sqlite*','**/DataUsage.sqlite*'),
        get_netusage)
}