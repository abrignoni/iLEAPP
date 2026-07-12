__artifacts_v2__ = {
    "appleMapsGroup": {
        "name": "Apple Maps Group",
        "description": "Parses cached location coordinates from the Apple Maps app group preferences (group.com.apple.Maps.plist).",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-08-03",
        "last_update_date": "2025-12-16",
        "requirements": "none",
        "category": "Locations",
        "notes": "",
        "paths": ('*/Shared/AppGroup/*/Library/Preferences/group.com.apple.Maps.plist',),
        "output_types": ["html", "tsv", "lava", "kml"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | com.apple.Maps | 1 row",
            "dexter_ios18": "iOS 18.3.2 | com.apple.Maps | 0 rows",
            "felix_ios17": "iOS 17.6.1 | com.apple.Maps | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | com.apple.Maps | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | com.apple.Maps | 0 rows",
            "iphone11_ios17": "iOS 17.3 | com.apple.Maps | 0 rows",
            "iphone12_ios18": "iOS 18.7 | com.apple.Maps | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | com.apple.Maps | 0 rows",
            "otto_ios17": "iOS 17.5.1 | com.apple.Maps | 0 rows",
            "abe_ios16": "iOS 16.5 | com.apple.Maps | 0 rows",
            "felix23_ios16": "iOS 16.5 | com.apple.Maps | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | com.apple.Maps | 0 rows",
            "hickman_ios14": "iOS 14.3 | com.apple.Maps | 0 rows",
            "jess_ios15": "iOS 15.0.2 | com.apple.Maps | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | com.apple.Maps | 0 rows",
        }
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
    # Check if plist is valid before processing
    if not pl or not isinstance(pl, dict):
        return (), [], ''
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
        internal_deserialized_plist, _ = blackboxprotobuf.decode_message(maps_activity, types)
        latitude = (internal_deserialized_plist['1']['5']['Latitude'])
        longitude = (internal_deserialized_plist['1']['5']['Longitude'])
        data_list.append((latitude, longitude))

    data_headers = ('Latitude', 'Longitude')     
    return data_headers, data_list, source_path
