import glob
import plistlib
import os
import datetime
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, kmlgen, timeline, tsv, is_platform_windows 


def get_cacheRoutesGmap(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        noext = os.path.splitext(filename)[0]
        noext = int(noext)
        datetime_time = datetime.datetime.fromtimestamp(noext/1000)
        datetime_time = str(datetime_time)
        with open(file_found, 'rb') as f:
            deserialized = plistlib.load(f)
            length = len(deserialized['$objects'])
            for x in range(length):
                try: 
                    lat = deserialized['$objects'][x]['_coordinateLat']
                    lon = deserialized['$objects'][x]['_coordinateLong'] #lat longs
                    data_list.append((datetime_time, lat, lon, file_found))
                except:
                    pass    
            
    if len(data_list) > 0:
        description = 'Google Maps Cache Routes'
        report = ArtifactHtmlReport('Locations')
        report.start_artifact_report(report_folder, 'Google Maps Cache Routes', description)
        report.add_script()
        data_headers = ('Timestamp','Latitude','Longitude','Source File')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Google Maps Cache Routes'
        tsv(report_folder, data_headers, data_list, tsvname)
    
        kmlactivity = 'Google Maps Cache Routes'
        kmlgen(report_folder, kmlactivity, data_list, data_headers)

__artifacts__ = {
    "cacheroutesgmap": (
        "Locations",
        ('**/Library/Application Support/CachedRoutes/*.plist'),
        get_cacheRoutesGmap)
}