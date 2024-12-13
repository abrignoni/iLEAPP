__artifacts_v2__ = {
    "get_biomeUseractmeta": {
        "name": "Biome User Activity Metadata",
        "description": "Parses battery percentage entries from biomes",
        "author": "@JohnHyla",
        "version": "0.0.2",
        "date": "2024-10-17",
        "requirements": "none",
        "category": "Biome User Act Meta",
        "notes": "",
        "paths": ('*/Biome/streams/restricted/UserActivityMetadata/local*'),
        "output_types": "standard"
    }
}


import os
from datetime import timezone
import blackboxprotobuf
import nska_deserialize as nd
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, convert_time_obj_to_utc, convert_utc_human_to_timezone


@artifact_processor
def get_biomeUseractmeta(files_found, report_folder, seeker, wrap_text, timezone_offset):

    #typess = {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'str', 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}, '2': {'type': 'double', 'name': ''}, '3': {'type': 'double', 'name': ''}, '4': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}, '5': {'type': 'double', 'name': ''}}, 'name': ''}, '5': {'type': 'str', 'name': ''}, '8': {'type': 'double', 'name': ''}, '10': {'type': 'int', 'name': ''}}
    data_list = []
    report_file = 'Unknown'
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

        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                protostuff, types = blackboxprotobuf.decode_message(record.data)

                bplistdata = (protostuff['2'])
                desc1 = (protostuff['4'].decode())
                desc2 = (protostuff['5'].decode())
                
                
                deserialized_plist = nd.deserialize_plist_from_string(bplistdata)
                
                title = (deserialized_plist.get('title',''))
                when = (deserialized_plist['when'])
                when = convert_time_obj_to_utc(when)
                when = convert_utc_human_to_timezone(when, timezone_offset)
                actype = (deserialized_plist['activityType'])
                exdate = (deserialized_plist.get('expirationDate',''))
                
                if (deserialized_plist.get('payload', '')) != '':
                    payload = (deserialized_plist.get('payload'))
                else:
                    payload = ''
                    
                internalbplist = (deserialized_plist.get('contentAttributeSetData',''))
                
                if internalbplist != '':
                    if type(internalbplist) != str:
                        try:
                            internalbplist = (deserialized_plist['contentAttributeSetData']['NS.data'])
                        except Exception as ex:
                            print(ex)
                            print('Processing as bplist["container"] directly.')
                        deserialized_plist2 = nd.deserialize_plist_from_string(internalbplist)
                        container = (deserialized_plist2['container'])
                    else:
                        container = internalbplist
                else:
                    container =''
                
                agg = ''
                for a, b in deserialized_plist.items():
                    if a == 'payload':
                        pass
                    else:
                        if b == ' ':
                            b = 'NULL'
                        agg = agg + f'{a} = {b}<br>'
                
                data_list.append((ts, when, record.state.name, actype, desc1, desc2, title, agg.strip(), payload,
                                  container, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Timestamp', 'datetime'), 'SEGB State', 'Activity type',
                    'Description', 'Bundle ID', 'Title', 'Bplist Data', 'Payload Data','Container Data', 'Filename',
                    'Offset')

    return data_headers, data_list, report_file
