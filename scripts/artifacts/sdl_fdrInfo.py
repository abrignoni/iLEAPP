__artifacts_v2__ = {
    "fdrInfo": {
        "name": "Sysdiagnose - Factory Data Reset Info",
        "description": "Parses factory data reset info from Sysdiagnose",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "Sysdiagnose - Settings & Preferences",
        "notes": "",
        "paths": ('*/logs/FDR/FDRDiagnosticReport.plist'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings"
    }
}

import plistlib
import textwrap
 
from scripts.ilapfuncs import artifact_processor, device_info

@artifact_processor
def fdrInfo(context):
    data_list = []
    source_paths = set()
    serialnumber = ''
    bt_mac = ''
    wifi_mac = ''
    imei = ''
    ime2 = ''
    seid = ''
    meid = ''
    eeid = ''
    tsid = ''
    mlb = ''
    arc = ''
    drp = ''
    nuid = ''

    for file_found in context.get_files_found():
        source_name = str(context.get_relative_path(file_found))
        source_paths.add(file_found)
        with open(file_found, 'rb') as f:
            pl = plistlib.load(f)
            
            verified = pl.get('VerifiedProperties')
            
            for item in verified:
                for key, value in item.items():
                    if 'SrNm' in key:
                        serialnumber = value.get('LiveProperty','')
                    elif 'BMac' in key:
                        bt_mac = value.get('LiveProperty','').upper()
                    elif 'WMac' in key:
                        wifi_mac = value.get('LiveProperty','').upper()
                    elif 'imei' in key:
                        imei = value.get('LiveProperty','')
                    elif 'ime2' in key:
                        ime2 = value.get('LiveProperty','')
                    elif 'seid' in key:
                        seid = value.get('LiveProperty','')
                    elif 'meid' in key:
                        meid = value.get('LiveProperty','')
                    elif 'eeid' in key:
                        eeid = value.get('LiveProperty','')
                    elif 'tsid' in key:
                        tsid = value.get('LiveProperty','')
                    elif 'mlb#' in key:
                        mlb = value.get('LiveProperty','')
                    elif 'arc#' in key:
                        arc = value.get('LiveProperty','')
                    elif 'drp#' in key:
                        drp = value.get('LiveProperty','')
                    elif 'nuid' in key:
                        nuid = value.get('LiveProperty','')
                    
            data_list.append((serialnumber,bt_mac,wifi_mac,imei,ime2,seid,meid,eeid,tsid,mlb,arc,textwrap.fill(drp, width=75),nuid,source_name))
            
    device_info("Device Identifier", "Serial Number", serialnumber, source_name)
    device_info("Device Identifier", "IMEI", imei, source_name)
    
    if ime2 != '':
        device_info("Device Identifier", "Serial Number", serialnumber, source_name)
    if meid != '':
        device_info("Device Identifier", "Mobile Equipment ID (MEID)", meid, source_name)
    if seid != '':
        device_info("Device Identifier", "Secure Element ID (SEID)", seid, source_name)
    if eeid != '':
        device_info("Device Identifier", "Embedded Identity Document (EID)", eeid, source_name)
        
    device_info("Device Identifier", "Bluetooth MAC Address", bt_mac, source_name)
    device_info("Device Identifier", "Wifi MAC Address (BSSID)", wifi_mac, source_name)
            
    data_headers = ('Serial Number','Bluetooth MAC','Wifi MAC','IMEI','IMEI2','Secure Element ID (SEID)','Mobile Equipment ID (MEID)','Embedded Identity Document (EID)','TSID','MLB','ARC','DRP','NUID','Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))