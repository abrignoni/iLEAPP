__artifacts_v2__ = {
    "get_cacheRoutesGmap": {
        "name": "Google Maps Cache Routes",
        "description": "",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-08-03",
        "last_update_date": "2025-11-12",
        "requirements": "none",
        "category": "Locations",
        "notes": "",
        "paths": ('*/Library/Application Support/CachedRoutes/*.plist',),
        "output_types": "standard",
    }
}

import os
from datetime import datetime
from scripts.ilapfuncs import artifact_processor, get_plist_file_content

@artifact_processor
def get_cacheRoutesGmap(context):
    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        noext = os.path.splitext(filename)[0]
        noext = int(noext)
        datetime_time = datetime.fromtimestamp(noext/1000)
        datetime_time = str(datetime_time)
        deserialized = get_plist_file_content(file_found)
        if not deserialized or not isinstance(deserialized, dict):
            continue
        length = len(deserialized['$objects'])
        for x in range(length):
            try: 
                lat = deserialized['$objects'][x]['_coordinateLat']
                lon = deserialized['$objects'][x]['_coordinateLong'] #lat longs
                data_list.append((datetime_time, lat, lon, file_found))
            except (KeyError, TypeError):
                pass    
            

    data_headers = (('Timestamp', 'datetime'),'Latitude','Longitude','Source File')
    
    return data_headers, data_list, 'see Source File for more info'