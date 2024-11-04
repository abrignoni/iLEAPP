__artifacts_v2__ = {
    "appleMapsApplication": {
        "name": "Apple Maps Last Activity Camera",
        "description": " ",
        "author": "@AlexisBrignoni",
        "version": "0.2",
        "date": "2020-08-03",
        "requirements": "none",
        "category": "Locations",
        "notes": "",
        "paths": ('*/Data/Application/*/Library/Preferences/com.apple.Maps.plist'),
        "function": "get_appleMapsApplication",
        "output_types": ["html", "tsv", "lava"]
    }
}


import plistlib
import blackboxprotobuf
import scripts.artifacts.artGlobals

#from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, lava_process_artifact, lava_insert_sqlite_data

def get_appleMapsApplication(files_found, report_folder, seeker, wrap_text, timezone_offset):
    versionnum = 0
    file_found = str(files_found[0])
    
    with open(file_found, 'rb') as f:
        plist = plistlib.load(f)
        
        types = {'1': {'type': 'double', 'name': 'Latitude'},
                '2': {'type': 'double', 'name': 'Longitude'}, 
                '3': {'type': 'double', 'name': ''}, 
                '4': {'type': 'fixed64', 'name': ''}, 
                '5': {'type': 'double', 'name': ''}
                }    
        protobuf = plist.get('__internal__LastActivityCamera', None)
        if protobuf:
            internal_plist, di = blackboxprotobuf.decode_message(protobuf,types)
            latitude = (internal_plist['Latitude'])
            longitude = (internal_plist['Longitude'])
            
            data_list = []
            data_list.append((latitude, longitude))
            
            report = ArtifactHtmlReport('Apple Maps Last Activity Camera')
            report.start_artifact_report(report_folder, 'Apple Maps Last Activity Camera')
            report.add_script()
            data_headers = ('Latitude','Longitude' )     
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Apple Maps Last Activity Camera'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            category = "Apple Maps Last Activity Camera"
            module_name = "get_appleMapsApplication"
                
            data_headers = ['Latitude','Longitude']
            
        
            table_name1, object_columns1, column_map1 = lava_process_artifact(
                category, module_name, 'Apple Maps Last Activity Camera', data_headers, len(data_list))
            lava_insert_sqlite_data(table_name1, data_list, object_columns1, data_headers, column_map1)
        
        else:
            logfunc(f"No Apple Maps Last Activity Camera data available")