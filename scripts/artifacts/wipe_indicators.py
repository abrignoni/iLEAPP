__artifacts_v2__ = {
    "wipe_indicators": {
        "name": "Wipe Indicators",
        "description": "Reports source metadata times for /root/.obliterated and /root/.bootstrapped from the seeker's FileInfo",
        "author": '@JohnHyla, @AlexisBrignoni, Codex',
        "creation_date": "2026-08-06",
        "version": "0.0.3",
        "date": "2024-10-17",
        "last_update_date": '2026-10-04',
        "requirements": "none",
        "category": "Identifiers",
        "notes": "Creation and modification values come from source FileInfo, not getmtime on the staged copy. A missing source time stays blank; tar lacks creation time, and zip requires an extended timestamp field. Directory input uses filesystem ctime for the creation slot, which is not necessarily birth time. The cited reference reads creation time for .obliterated and does not cover .bootstrapped. The file is not present in every extraction and extraction handling can disturb file times; corroborate with containermanagerd logs. Reference: Cellebrite, 'Upgrade From Null: Detecting iOS Wipe Artifacts', https://cellebrite.com/en/blog/upgrade-from-null-detecting-ios-wipe-artifacts/",
        "paths": ('*/root/.obliterated','*/root/.bootstrapped'),
        "output_types": "standard",
        "artifact_icon": "trash",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | 2 rows",
            "fsfull002_ios17": "iOS 17.1 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
            "iphone12_ios18": "iOS 18.7 | 2 rows",
            "iphone14plus_ios18": "iOS 18.0 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 2 rows",
            "felix23_ios16": "iOS 16.5 | 2 rows",
            "hickman_ios13": "iOS 13.3.1 | 2 rows",
            "hickman_ios14": "iOS 14.3 | 2 rows",
            "jess_ios15": "iOS 15.0.2 | 2 rows",
            "magnet_ios16": "iOS 16.1.1 | 2 rows",
        },
    }
}

import os
from scripts.ilapfuncs import device_info, artifact_processor, convert_unix_ts_to_utc

@artifact_processor
def wipe_indicators(context):
    files_found = context.get_files_found()
    data_list = []
    file_infos = context.get_seeker().file_infos
    source_path = ""
    
    for source_path in files_found:
        source_name = str(context.get_relative_path(source_path))
        source_name_log = os.path.basename(source_name.replace('\\', '/'))
        info = file_infos.get(source_path)
        created = convert_unix_ts_to_utc(info.creation_date) if info and info.creation_date else ''
        modified = convert_unix_ts_to_utc(info.modification_date) if info and info.modification_date else ''
    
        device_info("Wipe Indicators", f"{source_name_log}", created, source_name)
    
        data_list.append((created, modified, source_name_log, source_name))

    data_headers = (('Source Metadata Created', 'datetime'), ('Source Metadata Modified', 'datetime'),'Source File','Source Path')
    return data_headers, data_list, '\n'.join(sorted(str(file_found) for file_found in files_found))