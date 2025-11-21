__artifacts_v2__ = {
    "deviceActivator": {
        "name": "iOS Device Activator Data",
        "description": "Extracts device information from activation data",
        "author": "",
        "creation_date": "2024-10-29",
        "last_update_date": "2025-11-21",
        "requirements": "none",
        "category": "Device Information",
        "paths": ('*/mobile/Library/Logs/mobileactivationd/ucrt_oob_request.txt',),
        "output_types": "standard"
    }
}

import re
import base64
import os
import xml.etree.ElementTree as ET
from scripts.ilapfuncs import device_info, artifact_processor

@artifact_processor
def deviceActivator(context):
    data_list = []
    files_found = context.get_files_found()
    file_found = str(files_found[0])
    report_folder = context.get_report_folder()
    
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
            device_info("Network", "Ethernet MAC Address", x[1], file_found)
        if x[0] == 'BluetoothAddress':
            device_info("Network", "Bluetooth Address", x[1], file_found)
        if x[0] == 'WifiAddress':
            device_info("Network", "WiFi Address", x[1], file_found)
        if x[0] == 'ModelNumber':
            device_info("Device Information", "Model Number", x[1], file_found)
    
    data_headers = ('Property', 'Property Value')
    return data_headers, results, file_found