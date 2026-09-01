__artifacts_v2__ = {
    "sdl_disks": {
        "name": "Sysdiagnose - Disks",
        "description": "Parses Sysdiagnose disk information",
        "author": "@Hexordia",
        "creation_date": "2024-01-30",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "",
        "paths": ('*/disks.txt'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "hard-drive"
    }
}

import textwrap
from scripts.ilapfuncs import artifact_processor

@artifact_processor
def sdl_disks(context):
    data_list = []
    files_found = context.get_files_found()    
    
    for file_found in files_found:
        if 'PaxHeader' in file_found:
            continue
        else:
            source_name = str(context.get_relative_path(file_found))
            # Disks
            with open(file_found, encoding = 'utf-8', mode = 'r') as f:
                lines = f.readlines()[1:]
                
                for line in lines:
                    if '/' in line:
                        line_item = line.split()
                        data_list.append((textwrap.fill(line_item[0], width=75),line_item[1],line_item[2],line_item[3],line_item[4],line_item[5],line_item[6],line_item[7],line_item[8],source_name))
    # Disks Report  
    data_headers = ('File System','Size','Used','Available','Capacity','I Used','I Free','% I Used','Mounted On','Source File')
    
    return data_headers, data_list, 'See source file path(s) below:'