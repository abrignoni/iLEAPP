import glob
import plistlib
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, tsv, is_platform_windows 


def get_appleWifiPlist(files_found, report_folder, seeker):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        
        with open(file_found, 'rb') as f:
            deserialized = plistlib.load(f)
            if 'KeepWiFiPoweredAirplaneMode' in deserialized:
                val = (deserialized['KeepWiFiPoweredAirplaneMode'])
                logdevinfo(f"Keep Wifi Powered Airplane Mode: {val}")

            length = len(deserialized['List of known networks'])
            for x in range(length):
                knownnetworks = deserialized['List of known networks'][x] 
                if 'SSID_STR' in knownnetworks:
                    ssid = (knownnetworks['SSID_STR'])
                else:
                    ssid = ''
                if 'BSSID' in knownnetworks:
                    bss = (knownnetworks['BSSID'])
                else:
                    bss = ''
                if 'lastUpdated' in knownnetworks:
                    lu = (knownnetworks['lastUpdated'])
                else:
                    lu = ''
                if 'lastAutoJoined' in knownnetworks:
                    laj = (knownnetworks['lastAutoJoined'])
                else:
                    laj = ''
                if 'WiFiNetworkPasswordModificationDate' in knownnetworks:
                    wnpmd = (knownnetworks['WiFiNetworkPasswordModificationDate'])
                else:
                    wnpmd = ''
                
                alldata = (deserialized['List of known networks'][x])
                data_list.append((laj, ssid, bss, lu, wnpmd, alldata )) 
            
    if len(data_list) > 0:
        description = 'WiFi known networks data. Dates are taken straight from the source plist.'
        report = ArtifactHtmlReport('Locations')
        report.start_artifact_report(report_folder, 'WiFi Known Networks', description)
        report.add_script()
        data_headers = ('Last Auto Joined','SSID','BSSID','Last Updated','WiFi Network Password Modification Date', 'All Data' )     
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'WiFi Known Networks'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'WiFi Known Networks'
        timeline(report_folder, tlactivity, data_list, data_headers)
    
        