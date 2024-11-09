__artifacts_v2__ = {
    "get_carCD": {
        "name": "Last Car Connection and UDID",
        "description": "",
        "author": "@JohnHyla",
        "version": "0.0.2",
        "date": "2024-10-22",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/Library/Caches/locationd/cache.plist'),
        "output_types": ["lava", "tsv"],
    }
}

import plistlib
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logdevinfo, webkit_timestampsconv, artifact_processor


@artifact_processor
def get_carCD(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    data_list = []

    report_file = 'Unknown'
    for file_found in files_found:
        file_found = str(file_found)
        report_file = file_found
        
        lastconn = contype = connected = disconnected = uid = ''
        
        with open(file_found, "rb") as fp:
            pl = plistlib.load(fp)
            for key, value in pl.items():
                if key == 'LastVehicleConnection':
                    lastconn = value
                    contype = lastconn[2]
                    connected = webkit_timestampsconv(lastconn[0])
                    disconnected = webkit_timestampsconv(lastconn[1])
                    logdevinfo(f'<b>Vehicle - Last Connected: </b>{connected} - <b>Last Disconnected: </b>{disconnected} - <b>Type: </b>{contype}')
                    data_list.append((key, f'Last Connected: {connected} <br> Last Disconnected: {disconnected} <br> Type: {contype}'))
                    
                elif key == 'CalibrationUDID':
                    uid = value
                    logdevinfo(f'<b>UDID: </b>{uid}')
                    data_list.append((key, uid))
                else:
                    pass
    data_headers = ('Data Key', 'Data Value')

    if len(data_list) > 0:
        report = ArtifactHtmlReport('Last Car Connection and UDID')
        report.start_artifact_report(report_folder, 'Last Car Connection and UDID')
        report.add_script()
        report.write_artifact_data_table(data_headers, data_list, report_file, html_escape=False)
        report.end_artifact_report()

    return data_headers, data_list, report_file
