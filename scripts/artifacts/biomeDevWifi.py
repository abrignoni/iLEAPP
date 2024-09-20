import os
import blackboxprotobuf
from datetime import *
from scripts.artifact_report import ArtifactHtmlReport
import ccl_segb
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, convert_utc_human_to_timezone, timestampsconv, convert_ts_int_to_utc


def get_biomeDevWifi(files_found, report_folder, seeker, wrap_text, timezone_offset):

    typess = {'1': {'type': 'str', 'name': 'SSID'}, '2': {'type': 'int', 'name': 'Connect'}}

    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in file_found:
                continue
            else:
                pass
        else:
            continue
        
        directory_path = os.path.dirname(file_found)

        for record in ccl_segb.read_segb_file(file_found):
            offset = record.data_start_offset
            state = record.state.name
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if state == 'Written':
                protostuff, types = blackboxprotobuf.decode_message(record.data, typess)
                ssid = protostuff['SSID']
                status = 'Connected' if protostuff['Connect'] == 1 else 'Disconnected'
                filename_offset = f'{filename} - {offset}'

                data_list.append((ts, ssid, status, filename_offset))

    if len(data_list) > 0:
        description = ''
        report = ArtifactHtmlReport(f'Biome Device WIFI')
        report.start_artifact_report(report_folder, f'Biome Device WIFI', description)
        report.add_script()
        data_headers = ('Timestamp','SSID', 'Status', 'Filename & Offset')
        report.write_artifact_data_table(data_headers, data_list, directory_path)
        report.end_artifact_report()

        tsvname = f'Biome Device WIFI'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Biome Device WIFI'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc(f'No data available for Biome Device WIFI')
    

__artifacts__ = {
    "biomeDevWifi": (
        "Biome Device WIFI",
        ('*/Biome/streams/restricted/Device.Wireless.WiFi/local/*'),
        get_biomeDevWifi)
}
