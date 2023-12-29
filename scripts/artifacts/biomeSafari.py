import os
import struct
import blackboxprotobuf
from datetime import *
from time import mktime
from io import StringIO
from io import BytesIO
from scripts.ccl import ccl_segb1
from scripts.ccl import ccl_segb2
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, convert_utc_human_to_timezone, timestampsconv, convert_ts_int_to_utc

def checksegbv(in_path):
    MAGIC = b"SEGB"
    with open(in_path, "rb") as f:
        magic = f.read(4)
        
    if magic != MAGIC:
        return (False)
    else:
        return (True)

def utf8_in_extended_ascii(input_string, *, raise_on_unexpected=False):
    """Returns a tuple of bool (whether mis-encoded utf-8 is present) and str (the converted string)"""
    output = []  # individual characters, join at the end
    is_in_multibyte = False  # True if we're currently inside a utf-8 multibyte character
    multibytes_expected = 0
    multibyte_buffer = []
    mis_encoded_utf8_present = False
    
    def handle_bad_data(index, character):
        if not raise_on_unexpected: # not raising, so we dump the buffer into output and append this character
            output.extend(multibyte_buffer)
            multibyte_buffer.clear()
            output.append(character)
            nonlocal is_in_multibyte
            is_in_multibyte = False
            nonlocal multibytes_expected
            multibytes_expected = 0
        else:
            raise ValueError(f"Expected multibyte continuation at index: {index}")
            
    for idx, c in enumerate(input_string):
        code_point = ord(c)
        if code_point <= 0x7f or code_point > 0xf4:  # ASCII Range data or higher than you get for mis-encoded utf-8:
            if not is_in_multibyte:
                output.append(c)  # not in a multibyte, valid ascii-range data, so we append
            else:
                handle_bad_data(idx, c)
        else:  # potentially utf-8
            if (code_point & 0xc0) == 0x80:  # continuation byte
                if is_in_multibyte:
                    multibyte_buffer.append(c)
                else:
                    handle_bad_data(idx, c)
            else:  # start-byte
                if not is_in_multibyte:
                    assert multibytes_expected == 0
                    assert len(multibyte_buffer) == 0
                    while (code_point & 0x80) != 0:
                        multibytes_expected += 1
                        code_point <<= 1
                    multibyte_buffer.append(c)
                    is_in_multibyte = True
                else:
                    handle_bad_data(idx, c)
                    
        if is_in_multibyte and len(multibyte_buffer) == multibytes_expected:  # output utf-8 character if complete
            utf_8_character = bytes(ord(x) for x in multibyte_buffer).decode("utf-8")
            output.append(utf_8_character)
            multibyte_buffer.clear()
            is_in_multibyte = False
            multibytes_expected = 0
            mis_encoded_utf8_present = True
        
    if multibyte_buffer:  # if we have left-over data
        handle_bad_data(len(input_string), "")
    
    return mis_encoded_utf8_present, "".join(output)

def get_biomeSafari(files_found, report_folder, seeker, wrap_text, timezone_offset):

    typess = {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'str', 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}, '2': {'type': 'double', 'name': ''}, '3': {'type': 'double', 'name': ''}, '4': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}, '3': {'type': 'str', 'name': ''}}, 'name': ''}, '5': {'type': 'str', 'name': ''}, '6': {'type': 'message', 'message_typedef': {'1': {'type': 'str', 'name': ''}, '2': {'type': 'str', 'name': ''}, '3': {'type': 'str', 'name': ''}, '4': {'type': 'str', 'name': ''}, '6': {'type': 'int', 'name': ''}}, 'name': ''}, '7': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {}, 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}, '3': {'type': 'str', 'name': ''}}, 'name': ''}, '3': {'type': 'int', 'name': ''}}, 'name': ''}, '8': {'type': 'fixed64', 'name': ''}, '10': {'type': 'int', 'name': ''}}
    

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
            
        data_list = []
        if (checksegbv(file_found)): #SEGB v2
            for record in ccl_segb2.read_segb2_file(file_found):
                offset = record.data_start_offset
                metadata_offset = record.metadata.metadata_offset
                state = record.metadata.state.name
                ts = record.metadata.creation
                ts = ts.replace(tzinfo=timezone.utc)
                data = record.data
                
                if state == 'Written':
                    
                    protostuff, types = blackboxprotobuf.decode_message(data[8:],typess)
                    #print(protostuff)
                    #print(offset, metadata_offset, ts, state)
                    activity = (protostuff['1']['1'])
                    timestart = (timestampsconv(protostuff['2']))
                    url = (protostuff['4']['3'])
                    guid = (protostuff['5'])
                    detail1 = (protostuff['6']['1'])
                    detail2 = (protostuff['6']['2'])
                    detail3 = (protostuff['6']['4'])
                    title = (protostuff['7']['2']['3'])
                    
                    
                    data_list.append((ts, '', offset, metadata_offset, state, timestart, activity, title, url, detail1, detail2, detail3, guid))
                else: #Deleted
                    data_list.append((ts, '', offset, metadata_offset, state, '', '', '', '', '', '', '', ''))
                
                
                
        else: #SEGB v1
            for record in ccl_segb1.read_segb1_file(file_found):
                offset = record.data_start_offset
                data = record.data
                ts1 = record.timestamp1
                ts2 = record.timestamp2
                ts1 = ts1.replace(tzinfo=timezone.utc)
                ts2 = ts2.replace(tzinfo=timezone.utc)
                
                if data[0:1] == b'\x00':
                    state = 'Deleted'
                else:
                    state = 'Written'
                    
                if state == 'Written':
                    protostuff, types = blackboxprotobuf.decode_message(data,typess)
                    #print(protostuff)
                    #print(offset, metadata_offset, ts, state)
                    activity = (protostuff['1']['1'])
                    timestart = (timestampsconv(protostuff['2']))
                    print(timestart)
                    url = (protostuff['4']['3'])
                    guid = (protostuff['5'])
                    detail1 = (protostuff['6']['1'])
                    detail2 = (protostuff['6']['2'])
                    detail3 = (protostuff['6']['4'])
                    title = (protostuff['7']['2']['3'])
                    
                    #print(offset, ts1, ts2)
                    data_list.append((ts1, ts2, offset, '', state, timestart, activity, title, url, detail1, detail2, detail3, guid))
                        

        if len(data_list) > 0:
        
            description = ''
            report = ArtifactHtmlReport(f'Biome Safari')
            report.start_artifact_report(report_folder, f'Biome Safari - {filename}', description)
            report.add_script()
            data_headers = ('Timestamp SEGB','Timestamp SEGB','Offset','Metadata Offset','State','Timestamp','Activity', 'Title', 'URL', 'Detail', 'Detail', 'Detail', 'GUID')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Biome Safari - {filename}'
            tsv(report_folder, data_headers, data_list, tsvname) # TODO: _csv.Error: need to escape, but no escapechar set
            
            tlactivity = f'Biome Safari - {filename}'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc(f'No data available for Biome Safari')
    

__artifacts__ = {
    "biomeSafari": (
        "Biome Safari",
        ('*/biome/streams/restricted/_DKEvent.Safari.History/local/*'),
        get_biomeSafari)
}
