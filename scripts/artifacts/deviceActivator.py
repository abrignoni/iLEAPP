import re
import base64
import os
from itertools import compress 
import xml.etree.ElementTree as ET

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, logdevinfo, is_platform_windows

def get_deviceActivator(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    alllines = ''    
    file_found = str(files_found[0])

    with open(file_found, 'r') as f_in:
        for line in f_in:
            line = line.strip()
            alllines = alllines + line

    found = re.findall('<key>ActivationInfoXML</key><data>(.*)</data><key>RKCertification</key><data>', alllines)
    base64_message= found[0]

    data = base64.b64decode(base64_message)
    
    outpath = os.path.join(report_folder, "results.xml")
    with open(outpath, 'wb') as f_out:
        f_out.write(data)
    
    xmlfile = outpath
    tree = ET.parse(xmlfile)
    root = tree.getroot()

    for elem in root:
        for elemx in elem:
            for elemz in elemx:
                data_list.append(str(elemz.text).strip())

    it = iter(data_list)     
    results = list(zip(it, it))
    
    for x in results:
        if x[0] == 'EthernetMacAddress':
            logdevinfo(f"Ethernet Mac Address: {x[1]}")
        if x[0] == 'BluetoothAddress':
            logdevinfo(f"Bluetooth Address: {x[1]}")
        if x[0] == 'WifiAddress':
            logdevinfo(f"Wifi Address: {x[1]}") 
        if x[0] == 'ModelNumber':
            logdevinfo(f"Model Number: {x[1]}")
            
    if len(results) > 0:
        report = ArtifactHtmlReport('iOS Device Activator Data')
        report.start_artifact_report(report_folder, 'iOS Device Activator Data')
        report.add_script()
        data_headers = ('Key','Values')     
        report.write_artifact_data_table(data_headers, results, file_found)
        report.end_artifact_report()
        
        tsvname = 'iOS Device Activator Data'
        tsv(report_folder, data_headers, results, tsvname)
    else:
        logfunc('No iOS Device Activator Data')

__artifacts__ = {
    "deviceactivator": (
        "IOS Build",
        ('*/mobile/Library/Logs/mobileactivationd/ucrt_oob_request.txt'),
        get_deviceActivator)
}