import plistlib
import blackboxprotobuf
import scripts.artifacts.artGlobals

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 


def get_appleMapsGroup(files_found, report_folder, seeker, wrap_text, timezone_offset):
    versionnum = 0
    file_found = str(files_found[0])

    with open(file_found, 'rb') as f:
        deserialized_plist = plistlib.load(f)
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
        try:
            internal_deserialized_plist, di = blackboxprotobuf.decode_message((deserialized_plist['MapsActivity']),types)
            
            latitude =(internal_deserialized_plist['1']['5']['Latitude'])
            longitude =(internal_deserialized_plist['1']['5']['Longitude'])
            
            data_list = []
            data_list.append((latitude, longitude))
            report = ArtifactHtmlReport('Apple Maps Group')
            report.start_artifact_report(report_folder, 'Apple Maps Group')
            report.add_script()
            data_headers = ('Latitude','Longitude' )     
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Apple Maps Group'
            tsv(report_folder, data_headers, data_list, tsvname)
        except:
            logfunc('No data in Apple Maps Group')

__artifacts__ = {
    "applemapsgroup": (
        "Locations",
        ('**/Shared/AppGroup/*/Library/Preferences/group.com.apple.Maps.plist'),
        get_appleMapsGroup)
}


    