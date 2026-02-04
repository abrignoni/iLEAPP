__artifacts_v2__ = {
    "get_biomeNotes": {
        "name": "Biome - Notes",
        "description": "Parses notes entries from biomes",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2025-10-31",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/Biome/streams/restricted/NotesContent/local/*'),
        "html_columns" : ['Note'],
        "output_types": "standard",
        "function": "get_biomeNotes"
    }
}


import os
from datetime import timezone
import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import webkit_timestampsconv, artifact_processor

@artifact_processor
def get_biomeNotes(context):

    data_headers = (('SEGB Timestamp', 'datetime'), ('Timestamp', 'datetime'), 'SEGB State', 'Record Num', 'Identifier 1', 
                    'Identifier 2', 'Note', 'Filename', 'Offset')

    # TODO: shouldn't it be used in decode_message?
    # typess = {
    #     '1': {'type': 'str', 'name': ''},
    #     '2': {'type': 'str', 'name': ''},
    #     '3': {'type': 'double', 'name': ''},
    #     '5': {'type': 'str', 'name': ''}
    # }

    data_list = []
    data_list_html = []
    record_counter = 0
    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in file_found:
                continue
        else:
            continue
        
        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                protostuff, _ = blackboxprotobuf.decode_message(record.data)
                record_counter += 1
                time = (webkit_timestampsconv(protostuff['3']))
                identifier1 = protostuff['1']
                identifier2 = protostuff['2']
                message = protostuff['5']
                messagehtml = (message.replace('\n', '<br>'))
                data_list.append((ts, time, record.state.name, record_counter, identifier1, identifier2, message, filename, record.data_start_offset))
                data_list_html.append((ts, time, record.state.name, record_counter, identifier1, identifier2, messagehtml, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, filename,
                                       record.data_start_offset))
                data_list_html.append((ts, None, record.state.name, None, None, None, None, filename,
                                            record.data_start_offset))

    return data_headers, (data_list, data_list_html), 'see Source File for more info'
