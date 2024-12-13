__artifacts_v2__ = {
    "get_biomeNotes": {
        "name": "Biome Notes",
        "description": "Parses notes entries from biomes",
        "author": "@JohnHyla",
        "version": "0.0.2",
        "date": "2024-10-17",
        "requirements": "none",
        "category": "Biome Notes",
        "notes": "",
        "paths": ('*/Biome/streams/restricted/NotesContent/local/*'),
        "output_types": "none",
        "function": "get_biomeNotes"
    }
}


import os
from datetime import timezone
import blackboxprotobuf
from pathlib import Path
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import webkit_timestampsconv, tsv, timeline, convert_utc_human_to_timezone, convert_time_obj_to_utc
from scripts.lavafuncs import lava_process_artifact, lava_insert_sqlite_data


def get_biomeNotes(files_found, report_folder, seeker, wrap_text, timezone_offset):

    category = "Biome Notes"
    module_name = "get_biomeNotes"
    data_headers = ('SEGB Timestamp', 'Timestamp', 'SEGB State', 'Record Num', 'Identifier 1', 'Identifier 2', 'Note')
    lava_data_headers = (('SEGB Timestamp', 'datetime'), ('Timestamp', 'datetime'), 'SEGB State', 'Record Num', 'Identifier 1', 'Identifier 2', 'Note')

    typess = {'1': {'type': 'str', 'name': ''}, '2': {'type': 'str', 'name': ''}, '3': {'type': 'double', 'name': ''}, '5': {'type': 'str', 'name': ''}}

    data_list = []
    record_counter = 0
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

        file_data_list_html = []
        file_data_list = []
        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                protostuff, types = blackboxprotobuf.decode_message(record.data)
                record_counter += 1
                time = (webkit_timestampsconv(protostuff['3']))
                time = convert_utc_human_to_timezone(time, timezone_offset)
                identifier1 = protostuff['1']
                identifier2 = protostuff['2']
                message = protostuff['5']
                messagehtml = (message.replace('\n', '<br>'))
                file_data_list.append((ts, time, record.state.name, record_counter, identifier1, identifier2, message, filename, record.data_start_offset))
                file_data_list_html.append((ts, time, record.state.name, record_counter, identifier1, identifier2, messagehtml, filename, record.data_start_offset))
                
                #write notes to report_folder
                
                output_file = Path(report_folder).joinpath(f'{record_counter}.txt')
                output_file.write_text(message)

            elif record.state == EntryState.Deleted:
                file_data_list.append((ts, None, record.state.name, None, None, None, None, filename,
                                       record.data_start_offset))
                file_data_list_html.append((ts, None, record.state.name, None, None, None, None, filename,
                                            record.data_start_offset))

        data_list.extend(file_data_list)
        
        if len(file_data_list) > 0:
            description = ''
            report = ArtifactHtmlReport(f'Biome Notes')
            report.start_artifact_report(report_folder, f'Biome Notes - {filename}', description)
            report.add_script()
            report.write_artifact_data_table(data_headers, file_data_list_html, file_found, html_no_escape=['Note'])
            report.end_artifact_report()
            
            tsvname = f'Biome Notes - {filename}'
            tsv(report_folder, data_headers, file_data_list, tsvname) # TODO: _csv.Error: need to escape, but no escapechar set
            
            tlactivity = f'Biome Notes - {filename}'
            timeline(report_folder, tlactivity, file_data_list, data_headers)

    # Single table for LAVA output
    table_name, object_columns, column_map = lava_process_artifact(category, module_name,
                                                                   'Biome Notes',
                                                                   lava_data_headers,
                                                                   len(data_list))

    lava_insert_sqlite_data(table_name, data_list, object_columns, lava_data_headers, column_map)
