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
        "output_types": "none",
        "function": "get_carCD"
    }
}

import plistlib
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, webkit_timestampsconv, lava_process_artifact, lava_insert_sqlite_data


def get_carCD(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
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
                    
    if len(data_list) > 0:

        report = ArtifactHtmlReport('Last Car Connection and UDID')
        report.start_artifact_report(report_folder, 'Last Car Connection and UDID')
        report.add_script()
        data_headers = ('Data Key','Data Value')
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()

        tsvname = f'Last Car Connection and UDID'
        tsv(report_folder, data_headers, data_list, tsvname)

        # Single table for LAVA output
        category = "Identifiers"
        module_name = "getcarCD"
        name = 'Last Car Connection and UDID'

        logfunc(f'Found {len(data_list)} records for Last Car Connection and UDID')

        table_name, object_columns, column_map = lava_process_artifact(category, module_name,
                                                                       name,
                                                                       data_headers,
                                                                       len(data_list))

        lava_insert_sqlite_data(table_name, data_list, object_columns, data_headers, column_map)

    else:
        logfunc(f'No records found for Last Car Connection and UDID')
