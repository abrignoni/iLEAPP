import os
import blackboxprotobuf
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, convert_utc_human_to_timezone, timestampsconv
from ccl_segb import ccl_segb
from ccl_segb.ccl_segb_common import EntryState

def get_biomeDKInfocus(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    typess = {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'str', 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}, 
        '2': {'type': 'double', 'name': ''}, '3': {'type': 'double', 'name': ''}, '4': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}, '3': {'type': 'str', 'name': ''}}, 'name': ''}, '5': {'type': 'str', 'name': ''}, '7': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {}, 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}, '3': {'type': 'str', 'name': ''}}, 'name': ''}, '3': {'type': 'int', 'name': ''}}, 'name': ''}, '8': {'type': 'double', 'name': ''}, '10': {'type': 'int', 'name': ''}}

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
                report_file = os.path.dirname(file_found)
        else:
            continue
    
        for record in ccl_segb.read_segb_file(file_found):
            if record.state == EntryState.Written:
                protostuff, types = blackboxprotobuf.decode_message(record.data, typess)
                #print(protostuff)
                
                activity = (protostuff['1']['1'])
                timestart = (timestampsconv(protostuff['2']))
                timestart = convert_utc_human_to_timezone(timestart, timezone_offset)
                
                timeend = (timestampsconv(protostuff['3']))
                timeend = convert_utc_human_to_timezone(timeend, timezone_offset)
                
                timewrite = (timestampsconv(protostuff['8']))
                timewrite = convert_utc_human_to_timezone(timewrite, timezone_offset)
                
                actionguid = (protostuff['5'])
                bundleid = (protostuff['4']['3'])
                if protostuff.get('7', '') != '':
                    if isinstance(protostuff['7'], list):
                        transition = (protostuff['7'][0]['2']['3'])
                    else:
                        transition = (protostuff['7']['2']['3'])
                else:
                    transition = ''
                
                
                data_list.append((timestart, timeend, timewrite, activity, bundleid, transition, actionguid, filename))

    if len(data_list) > 0:

        description = ''
        report = ArtifactHtmlReport(f'Biome DKEvent AppInFocus')
        report.start_artifact_report(report_folder, f'Biome DKEvent AppInFocus', description)
        report.add_script()
        data_headers = ('Time Start','Time End','Time Write','Activity','Bundle ID','Transition','Action GUID', 'Filename')
        report.write_artifact_data_table(data_headers, data_list, report_file)
        report.end_artifact_report()

        tsvname = f'Biome DKEvent AppInFocus'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Biome DKEvent AppInFocus'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc(f'No data available for Biome AppInFocus')
    

__artifacts__ = {
    "biomeDKInFocus": (
        "Biome in Focus",
        ('*/biome/streams/restricted/_DKEvent.App.InFocus/local/*'),
        get_biomeDKInfocus)
}
