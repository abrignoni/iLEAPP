__artifacts_v2__ = {
    "sdl_disks": {
        "name": "Sysdiagnose - Disks",
        "description": "Parses Sysdiagnose disk information",
        "author": "@Hexordia",
        "creation_date": "2024-01-30",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "",
        "paths": (
            '*/disks.txt',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "hard-drive"
    }
}

from scripts.ilapfuncs import artifact_processor, get_sysdiagnose_files

@artifact_processor
def sdl_disks(context):
    data_list = []
    source_paths = set()
        
    for file_obj, source_path in get_sysdiagnose_files(context.get_files_found(), "disks.txt"):
        if 'PaxHeader' in source_path:
            continue
            
        source_name = str(context.get_relative_path(source_path))
        
        try:
            # Read the raw stream directly to avoid text-mode line ending corruption
            if hasattr(file_obj, 'buffer'):
                file_content = file_obj.buffer.read()
            else:
                file_content = file_obj.read()
                
            if not file_content:
                continue
                
            # Decode bytes to a string for text processing
            if isinstance(file_content, bytes):
                file_content = file_content.decode('utf-8', errors='replace')
                
            lines = file_content.splitlines()[1:]
        except Exception:
            continue
            
        source_paths.add(source_path)
        
        for line in lines:
            if '/' in line:
                line_item = line.split()
                # Ensure we have enough columns to prevent IndexError
                if len(line_item) >= 9:
                    data_list.append((line_item[0],line_item[1],line_item[2],line_item[3],line_item[4],line_item[5],line_item[6],line_item[7],line_item[8],source_name))
                
    data_headers = ('File System','Size','Used','Available','Capacity','I Used','I Free','% I Used','Mounted On','Source File')
    
    return data_headers, data_list, '\n'.join(sorted(source_paths))