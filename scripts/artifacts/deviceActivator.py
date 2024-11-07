__artifacts_v2__ = {
    "deviceActivator": {
        "name": "iOS Device Activator Data",
        "description": "Extracts device information from activation data",
        "author": "",
        "version": "1.0",
        "date": "2024-10-29",
        "requirements": "none",
        "category": "Device Information",
        "paths": ('*/mobile/Library/Logs/mobileactivationd/ucrt_oob_request.txt',),
        "output_types": "standard"
    }
}

import re
import base64
import os
from itertools import compress 
import xml.etree.ElementTree as ET
from scripts.ilapfuncs import logfunc, device_info, artifact_processor

@artifact_processor
def deviceActivator(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
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
            device_info("Network", "Ethernet MAC Address", x[1], file_found)
        if x[0] == 'BluetoothAddress':
            device_info("Network", "Bluetooth Address", x[1], file_found)
        if x[0] == 'WifiAddress':
            device_info("Network", "WiFi Address", x[1], file_found)
        if x[0] == 'ModelNumber':
            device_info("Device Information", "Model Number", x[1], file_found)
    
    if len(results) > 0:
        data_headers = ('Property', 'Property Value')
        return data_headers, results, file_found
    else:
        logfunc('No iOS Device Activator Data')
        return None