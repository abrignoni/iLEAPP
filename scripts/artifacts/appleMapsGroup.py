__artifacts_v2__ = {
    "appleMapsGroup": {
        "name": "Apple Maps Group",
        "description": "",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-08-03",
        "last_update_date": "2025-10-08",
        "requirements": "none",
        "category": "Locations",
        "notes": "",
        "paths": ('*/Shared/AppGroup/*/Library/Preferences/group.com.apple.Maps.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "map-pin"
    }
}

import blackboxprotobuf
from scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content

@artifact_processor
def appleMapsGroup(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "group.com.apple.Maps.plist")
    data_list = []

    pl = get_plist_file_content(source_path)
    maps_activity = pl.get('MapsActivity', None)
    if maps_activity:
        types = {'1': {'type': 'message', 'message_typedef': 
                                {'1': {'type': 'int', 'name': ''}, 
                                '2': {'type': 'int', 'name': ''}, 
                                '5': {'type': 'message', 'message_typedef': 
                                            {'1': {'type': 'double', 'name': 'Latitude'},
                                            '2': {'type': 'double', 'name': 'Longitude'}, 
                                            '3': {'type': 'double', 'name': ''}, 
                                            '4': {'type': 'fixed64', 'name': ''}, 
                                            '5': {'type': 'double', 'name': ''}},
                                        'name': ''},
                                '7': {'type': 'int', 'name': ''}},
                        'name': ''}
                }    
        internal_deserialized_plist, di = blackboxprotobuf.decode_message(maps_activity, types)
        latitude = (internal_deserialized_plist['1']['5']['Latitude'])
        longitude = (internal_deserialized_plist['1']['5']['Longitude'])
        data_list.append((latitude, longitude))

    data_headers = ('Latitude', 'Longitude')     
    return data_headers, data_list, source_path
