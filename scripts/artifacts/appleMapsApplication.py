__artifacts_v2__ = {
    "appleMapsApplication": {
        "name": "Apple Maps Last Activity Camera",
        "description": "",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-08-03",
        "last_update_date": "2024-12-20",
        "requirements": "none",
        "category": "Locations",
        "notes": "",
        "paths": ('*/Data/Application/*/Library/Preferences/com.apple.Maps.plist'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "map-pin"
    }
}


import blackboxprotobuf
from scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content

@artifact_processor
def appleMapsApplication(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "com.apple.Maps.plist")
    data_list = []
    
    plist = get_plist_file_content(source_path)
    
    types = {'1': {'type': 'double', 'name': 'Latitude'},
            '2': {'type': 'double', 'name': 'Longitude'}, 
            '3': {'type': 'double', 'name': ''}, 
            '4': {'type': 'fixed64', 'name': ''}, 
            '5': {'type': 'double', 'name': ''}
            }    
    
    protobuf = plist.get('__internal__LastActivityCamera', None)
    if protobuf:
        internal_plist, _ = blackboxprotobuf.decode_message(protobuf,types)
        latitude = (internal_plist['Latitude'])
        longitude = (internal_plist['Longitude'])
        
        data_list.append((latitude, longitude))
                            
    data_headers = ('Latitude','Longitude')
    return data_headers, data_list, source_path    
