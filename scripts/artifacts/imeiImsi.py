import datetime
import os
import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 

def get_imeiImsi(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            
            if key == 'PersonalWallet':
                val = (list(val.values())[0])
                lastgoodimsi = val['CarrierEntitlements']['lastGoodImsi']
                data_list.append(('Last Good IMSI', lastgoodimsi))
                logdevinfo(f"<b>Last Good IMSI: </b>{lastgoodimsi}")
                
                selfregitrationupdateimsi = val['CarrierEntitlements']['kEntitlementsSelfRegistrationUpdateImsi']
                data_list.append(('Self Registration Update IMSI', selfregitrationupdateimsi))
                logdevinfo(f"<b>Self Registration Update IMSI: </b>{selfregitrationupdateimsi}")
                
                selfregistrationupdateimei = val['CarrierEntitlements']['kEntitlementsSelfRegistrationUpdateImei']
                data_list.append(('Self Registration Update IMEI', selfregistrationupdateimei))
                logdevinfo(f"<b>Self Registration Update IMEI: </b>{selfregistrationupdateimei}")
                
            elif key == 'LastKnownICCI':
                lastknownicci = val
                data_list.append(('Last Known ICCI', lastknownicci))
                logdevinfo(f"<b>Last Known ICCI: </b>{lastknownicci}")
                
            elif key == 'PhoneNumber':
                phonenumber = val
                data_list.append(('Phone Number', val))
                logdevinfo(f"<b>Phone Number: </b>{val}")
                
            else:
                data_list.append((key, val ))
                
    if len(data_list) > 0:
        report = ArtifactHtmlReport('IMEI - IMSI')
        report.start_artifact_report(report_folder, 'IMEI - IMSI')
        report.add_script()
        data_headers = ('Key','Values' )     
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'IMEI - IMSI'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No IMEI - IMSI data in com.apple.commcenter.plist')

__artifacts__ = {
    "imeiImsi": (
        "Identifiers",
        ('*/wireless/Library/Preferences/com.apple.commcenter.plist'),
        get_imeiImsi)
}
