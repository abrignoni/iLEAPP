__artifacts_v2__ = {
    "dhcpHotspotClients": {
        "name": "DHCP Hotspot Clients",
        "description": "Information about devices that connected to the hotspot",
        "author": "@AlexisBrignoni",
        "creation_date": "2024-10-29",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "DHCP",
        "notes": "",
        "paths": ('*/db/dhcpd_leases*',),
        "output_types": "standard",
        "artifact_icon": "wifi",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 15 rows",
            "otto_ios17": "iOS 17.5.1 | 10 rows",
            "abe_ios16": "iOS 16.5 | 23 rows",
            "felix23_ios16": "iOS 16.5 | 23 rows",
        }
    }
}

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def dhcpHotspotClients(context):
    data_headers = ('Key Name', 'Value Data', 'Source File')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        rel = context.get_relative_path(file_found)
        with open(file_found, "r", encoding="utf-8") as filefrom:
            for line in filefrom:
                cline = line.strip()
                if "=" in cline:
                    splitline = cline.split("=")
                    data_list.append((splitline[0], splitline[1], rel))
        sources.append(rel)

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
