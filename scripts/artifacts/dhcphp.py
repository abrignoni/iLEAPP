__artifacts_v2__ = {
    "dhcpHotspotClients": {
        "name": "DHCP Hotspot Clients",
        "description": "Information about devices that connected to the hotspot",
        "author": "@AlexisBrignoni",
        "version": "1.0",
        "date": "2024-10-29",
        "requirements": "none",
        "category": "DHCP",
        "paths": ('*/db/dhcpd_leases*'),
        "output_types": "standard"
    }
}


from scripts.ilapfuncs import artifact_processor

@artifact_processor
def dhcpHotspotClients(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []

    for file_found in files_found:
        with open(file_found, "r") as filefrom:
            for line in filefrom:
                cline = line.strip()
                if "=" in cline:
                    splitline = cline.split("=")
                    data_list.append((splitline[0], splitline[1], file_found))
    
    data_headers = ('Key Name', 'Value Data', 'Source File')   
    return data_headers, data_list, ''
