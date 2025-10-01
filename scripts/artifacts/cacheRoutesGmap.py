__artifacts_v2__ = {
    "get_cacheRoutesGmap": {
        "name": "Google Maps Cache Routes",
        "description": "",
        "author": "@abrignoni",
        "creation_date": "2020-08-03",
        "last_update_date": "2025-04-13",
        "requirements": "none",
        "category": "Locations",
        "notes": "",
        "paths": ('*/Library/Application Support/CachedRoutes/*.plist',),
        "output_types": "standard",
    }
}

import os 

from scripts.ilapfuncs import artifact_processor, get_plist_content, convert_unix_ts_to_utc

@artifact_processor
def get_cacheRoutesGmap(context):
    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        noext = os.path.splitext(filename)[0]
        noext = int(noext)
        datetime_time = convert_unix_ts_to_utc(noext)
        datetime_time = str(datetime_time)
        with open(file_found, 'rb') as f:
            deserialized = get_plist_content(f)
            length = len(deserialized['$objects'])
            for x in range(length):
                try: 
                    lat = deserialized['$objects'][x]['_coordinateLat']
                    lon = deserialized['$objects'][x]['_coordinateLong'] #lat longs
                    data_list.append((datetime_time, lat, lon, file_found))
                except:
                    pass    
                
    data_headers = (('Timestamp', 'datetime'),'Latitude','Longitude','Source File')
            
    return data_headers, data_list, ''