import gzip
import re
import os
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, kmlgen,tsv, is_platform_windows 


def get_tileApp(files_found, report_folder, seeker):
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('gz'):
            x=gzip.open
        elif file_found.endswith('log'):
            x=open
        
        counter = 0
        with x(file_found,'rt',) as f:
            for line in f:
                regexdate = r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}.\d{3}"
                datestamp = re.search(regexdate, line)  
                counter +=1
                if datestamp != None:
                    datestamp = datestamp.group(0)
                    regexlatlong = r"<[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)>"
                    latlong = re.search(regexlatlong, line)
                    if latlong != None:
                        latlong = latlong.group(0)
                        latlong = latlong.strip('<')
                        latlong = latlong.strip('>')
                        lat, longi = latlong.split(',')
                        head_tail = os.path.split(file_found) 
                        data_list.append((datestamp, lat.lstrip(), longi.lstrip(), counter, head_tail[1]))

    if len(data_list) > 0:
        description = 'Tile app log recorded langitude and longitude coordinates.'
        report = ArtifactHtmlReport('Locations')
        report.start_artifact_report(report_folder, 'Tile App Geolocation Logs', description)
        report.add_script()
        data_headers = ('Timestamp', 'Latitude', 'Longitude', 'Row Number', 'Source File' )     
        report.write_artifact_data_table(data_headers, data_list, head_tail[0])
        report.end_artifact_report()
        
        tsvname = 'Tile App Lat Long'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Tile App Lat Long'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
        kmlactivity = 'Tile App Lat Long'
        kmlgen(report_folder, kmlactivity, data_list, data_headers)
    
        