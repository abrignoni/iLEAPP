import os
import blackboxprotobuf
from datetime import *
from scripts.artifact_report import ArtifactHtmlReport
import ccl_segb
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, convert_utc_human_to_timezone, timestampsconv, convert_ts_int_to_utc


def get_biomeDKEventWifi(files_found, report_folder, seeker, wrap_text, timezone_offset):
    typedef = {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'str', 'name': 'Stream'},
                                                            '2': {'type': 'message',
                                                                  'message_typedef': {'1': {'type': 'int', 'name': ''},
                                                                                      '2': {'type': 'uint',
                                                                                            'name': ''}}, 'name': ''}},
                     'name': ''}, '2': {'type': 'double', 'name': 'startMinute'},
               '3': {'type': 'double', 'name': 'endMinute'}, '4': {'type': 'message', 'message_typedef': {
            '1': {'type': 'message',
                  'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'uint', 'name': ''}}, 'name': ''},
            '3': {'type': 'str', 'name': 'SSID'}}, 'name': ''}, '5': {'type': 'str', 'name': 'GUID'},
               '8': {'type': 'double', 'name': 'endTime'}, '10': {'type': 'int', 'name': 'Timezone'}}

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

            if state == 'Written':
                protostuff, _ = blackboxprotobuf.decode_message(record.data, typedef)
                endTime = timestampsconv(protostuff['endTime'])
                startMinute = timestampsconv(protostuff['startMinute'])
                endMinute = timestampsconv(protostuff['endMinute'])
                ssid = protostuff['4'].get('SSID')

                filename_offset = f'{filename} - {offset}'

                data_list.append((endTime, startMinute, endMinute, ssid, protostuff['GUID'], filename_offset))

    if len(data_list) > 0:
        description = ('Records with an SSID are periods when WiFi is connected. Records without an SSID are periods '
                       'that the WiFi is disconnected. Records contain a start and end time without seconds and in '
                       'addition there is another end timestamp that includes seconds. Note that these records should '
                       'match records found in the "Biome Device WiFi" module except the end time in this artifact '
                       'seems to be delayed by a fraction of a second. To determine the start time for a record you '
                       'must use the prior records end time.')
        report = ArtifactHtmlReport(f'Biome WIFI (DKEvent)')
        report.start_artifact_report(report_folder, f'Biome WIFI (DKEvent)', description)
        report.add_script()
        data_headers = ('End Time', 'Start Minute', 'End Minute', 'SSID', 'GUID', 'Filename & Offset')
        report.write_artifact_data_table(data_headers, data_list, directory_path)
        report.end_artifact_report()

        tsvname = f'Biome WIFI (DKEvent)'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Biome WIFI (DKEvent)'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc(f'No data available for Biome Device WIFI')
    

__artifacts__ = {
    "biomeDKEventWifi": (
        "Biome WIFI (DKEvent)",
        ('*/Biome/streams/restricted/_DKEvent.Wifi.Connection/local/*'),
        get_biomeDKEventWifi)
}
