__artifacts_v2__ = {
    "spindump": {
        "name": "Sysdiagnose - Spin Dump Info",
        "description": "Parses spin dump details from Sysdiagnose",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "",
        "paths": (
            '*/spindump-nosymbols.txt',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings"
    }
}

from scripts.ilapfuncs import artifact_processor, device_info, get_sysdiagnose_files
    
def display_time(seconds):
    days = int(seconds / (24 * 3600))
    seconds -= days * (24 * 3600)
    hours = int(seconds / 3600)
    seconds -= hours * 3600
    minutes = int(seconds / 60)
    seconds -= minutes * 60
    return f"{days}d {hours}h {minutes}m {seconds}s"

@artifact_processor
def spindump(context):
    data_list = []
    source_paths = set()

    for file_obj, source_path in get_sysdiagnose_files(context.get_files_found(), "spindump-nosymbols.txt"):
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
            if 'Time Since Boot:' in line:
                entry = line.strip().split('Time Since Boot: ')
                sec_since_boot = entry[1][:-1]
                sec_since_boot = display_time(int(sec_since_boot))
                data_list.append(('Duration Since Boot',sec_since_boot,source_name))

                device_info('System Stats','Duration Since Boot',sec_since_boot,source_name)
                
            elif 'Time Awake Since Boot:' in line:
                entry = line.strip().split('Time Awake Since Boot: ')
                sec_awake_since_boot = entry[1][:-1]
                sec_awake_since_boot = display_time(int(sec_awake_since_boot))
                data_list.append(('Duration Awake Since Boot',sec_awake_since_boot,source_name))

                device_info('System Stats','Duration Awake Since Boot',sec_awake_since_boot,source_name)
                
            elif 'Time Since Wake:' in line:
                entry = line.strip().split('Time Since Wake: ')
                if 'n/a ' in line:
                    sec_since_wake = 'N/A (Machine Hasn\'t Slept)'
                else:
                    sec_since_wake = entry[1][:-1]
                    sec_since_wake = display_time(int(sec_since_wake))
                data_list.append(('Duration Since Wake',sec_since_wake,source_name))

                device_info('System Stats','Time Since Wake',sec_since_wake,source_name)
                
            elif 'Preferred User Language: ' in line:
                entry = line.strip().split('Preferred User Language: ')
                language = entry[1]
                data_list.append(('Preferred Language',language,source_name))

                device_info('Settings & Preferences','Preferred Language',language,source_name)
                
            elif 'Country Code: ' in line:
                entry = line.strip().split('Country Code: ')
                country_code = entry[1]
                data_list.append(('Country Code',country_code,source_name))
                
                device_info('Device Information','Country Code',country_code,source_name)
                
            elif 'Keyboards: ' in line:
                entry = line.strip().split('Keyboards: ')
                keyboards = entry[1]
                data_list.append(('Keyboard(s)',keyboards,source_name))
                
            elif 'Free disk space: ' in line:
                entry = line.strip().split('Free disk space: ')
                disk_space = entry[1].strip().split(', ')
                fds = disk_space[0]
                data_list.append(('Disk Space',fds,source_name))

                device_info('System Stats','Disk Space',fds,source_name)

    data_headers = ('Property','Value','Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))