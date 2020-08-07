import plistlib
import blackboxprotobuf
import scripts.artifacts.artGlobals

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 


def get_appleMapsApplication(files_found, report_folder, seeker):
    versionnum = 0
    file_found = str(files_found[0])
    
    with open(file_found, 'rb') as f:
        deserialized_plist = plistlib.load(f)
        
        types = {'1': {'type': 'double', 'name': 'Latitude'},
                '2': {'type': 'double', 'name': 'Longitude'}, 
                '3': {'type': 'double', 'name': ''}, 
                '4': {'type': 'fixed64', 'name': ''}, 
                '5': {'type': 'double', 'name': ''}
                }    
        
        internal_deserialized_plist, di = blackboxprotobuf.decode_message((deserialized_plist['__internal__LastActivityCamera']),types)
        latitude = (internal_deserialized_plist['Latitude'])
        longitude = (internal_deserialized_plist['Longitude'])
        
        data_list = []
        data_list.append((latitude, longitude))
        report = ArtifactHtmlReport('Apple Maps App')
        report.start_artifact_report(report_folder, 'Apple Maps App')
        report.add_script()
        data_headers = ('Latitude','Longitude' )     
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Apple Maps Application'
        tsv(report_folder, data_headers, data_list, tsvname)
    

            