__artifacts_v2__ = {
    "mobileActivationLogs": {
        "name": "Mobile Activation Logs",
        "description": "Upgrade and Mobile Activation Startup events parsed from mobileactivationd.log "
                       "(including logs found inside sysdiagnose archives)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-09-10",
        "requirements": "none",
        "category": "Mobile Activation Logs",
        "notes": "",
        "paths": ('*/mobileactivationd.log*', '*/sysdiagnose_*.tar.gz'),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 23 rows",
            "dexter_ios18": "iOS 18.3.2 | 31 rows",
            "felix_ios17": "iOS 17.6.1 | 15 rows",
            "fsfull002_ios17": "iOS 17.1 | 31 rows",
            "hc_ios18_7": "iOS 18.7.8 | 89 rows",
            "iphone11_ios17": "iOS 17.3 | 25 rows",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "otto_ios17": "iOS 17.5.1 | 57 rows",
            "abe_ios16": "iOS 16.5 | 115 rows",
            "felix23_ios16": "iOS 16.5 | 66 rows",
            "hickman_ios13": "iOS 13.3.1 | 38 rows",
            "hickman_ios14": "iOS 14.3 | 82 rows",
            "jess_ios15": "iOS 15.0.2 | 17 rows",
        }
    }
}

import re
from datetime import datetime, timezone
from pathlib import Path

from scripts.ilapfuncs import artifact_processor, get_sysdiagnose_files

_DATE_RE = re.compile(r'(([A-Za-z]+[\s]+([a-zA-Z]+[\s]+[0-9]+)[\s]+([0-9]+\:[0-9]+\:[0-9]+)[\s]+'
                      r'([0-9]{4}))([\s]+[\[\d\]]+[\s]+[\<a-z\>]+[\s]+[\(\w\)]+[\s]+[A-Z]{2}\:[\s]+)'
                      r'([main\:\s]*.*)$)')
_UPGRADE_RE = re.compile(r'((.*)(Upgrade\s+from\s+[\w]+\s+to\s+[\w]+\s+detected\.$))')
_STARTUP = '____________________ Mobile Activation Startup _____________________'

_LOG_MATCH_RE = re.compile(r"mobileactivationd\.log(\.\d+)?$")

@artifact_processor
def mobileActivationLogs(context):
    data_headers = (('Datetime', 'datetime'), 'Event', 'Log Name')
    data_list = []
    source_files = []

    for file_obj, source in get_sysdiagnose_files(context.get_files_found(), _LOG_MATCH_RE):
        # 1. Separate base path and member name to correctly apply relative paths
        if ' >> ' in source:
            base_source, member = source.split(' >> ', 1)
            rel_source = f"{context.get_relative_path(base_source)} >> {member}"
            log_name = member
        else:
            rel_source = context.get_relative_path(source)
            log_name = Path(source).name
            
        # 2. Deduplicate on the full string (Relative Archive >> Member)
        if rel_source not in source_files:
            source_files.append(rel_source)
        
        # 3. Process the file
        for linecount, line in enumerate(file_obj, 1):
            match = _DATE_RE.match(line)
            if not match:
                continue
            try:
                dtime_obj = datetime.strptime(' '.join(match.group(3, 5, 4)),
                                              '%b %d %Y %H:%M:%S').replace(tzinfo=timezone.utc)
            except ValueError:
                continue
                
            values = match.group(7)
            if 'perform_data_migration' in values:
                upgrade_match = _UPGRADE_RE.search(values)
                if upgrade_match:
                    data_list.append((dtime_obj, upgrade_match.group(3), log_name))
            if _STARTUP in values:
                data_list.append((dtime_obj, f'Mobile Activation Startup at line: {linecount}', log_name))

    # 4. Join the fully prepared, deduplicated strings
    source_path = ', '.join(source_files)
    return data_headers, data_list, source_path