__artifacts_v2__ = {
    "get_obliterated": {
        "name": "Obliterated Time",
        "description": "Parses obliterated timestamp",
        "author": "@JohnHyla",
        "version": "0.0.2",
        "date": "2024-10-17",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/root/.obliterated'),
        "output_types": "standard",
        "artifact_icon": "trash",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1 row",
            "felix_ios17": "iOS 17.6.1 | 1 row",
            "fsfull002_ios17": "iOS 17.1 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
            "otto_ios17": "iOS 17.5.1 | 1 row",
            "felix23_ios16": "iOS 16.5 | 1 row",
            "hickman_ios13": "iOS 13.3.1 | 1 row",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 1 row",
        },
    }
}

import datetime
from datetime import timezone
import os
from scripts.ilapfuncs import logdevinfo, artifact_processor

@artifact_processor
def get_obliterated(context):
    file_found = str(context.get_files_found()[0])
    
    modified_time = os.path.getmtime(file_found)
    utc_modified_date = datetime.datetime.fromtimestamp(modified_time, tz=timezone.utc)
    
    logdevinfo(f'<b>Obliterated Timestamp: </b>{utc_modified_date}')
    
    data_list = [(utc_modified_date,)]

    data_headers = (('Timestamp', 'datetime'), )

    return data_headers, data_list, file_found