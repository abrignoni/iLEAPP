import os
import struct
import blackboxprotobuf
from datetime import *
from time import mktime
from io import StringIO
from io import BytesIO
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ccl import ccl_segb1
from scripts.ccl import ccl_segb2
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, convert_utc_human_to_timezone, timestampsconv, convert_ts_int_to_utc

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

def checksegbv(in_path):
    MAGIC = b"SEGB"
    with open(in_path, "rb") as f:
        magic = f.read(4)
        
    if magic != MAGIC:
        return (False)
    else:
        return (True)
    
def get_biomeDevWifi(files_found, report_folder, seeker, wrap_text, timezone_offset):

    typess = {'1': {'type': 'bytes', 'message_typedef': {'8': {'type': 'fixed64', 'name': ''}}, 'name': ''}, '2': {'type': 'int', 'name': ''}}
    

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
                    
                    protostuff, types = blackboxprotobuf.decode_message(data[8:], typess)
                    wifi = protostuff['1'].decode()
                    data_list.append((ts, offset, metadata_wifi, wifi))
                    
                else: #Deleted
                    #print(ts, offset, metadata_offset, state)
                    pass
                
                
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
                    wifi = protostuff['1'].decode()
                    data_list.append((ts1, offset,'',wifi))
                else:
                    pass
                    
        if len(data_list) > 0:
        
            description = ''
            report = ArtifactHtmlReport(f'Biome Device WIFI')
            report.start_artifact_report(report_folder, f'Biome Device WIFI - {filename}', description)
            report.add_script()
            data_headers = ('Timestamp','Offset','Metadata Offset','WiFi')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Biome Device WIFI - {filename}'
            tsv(report_folder, data_headers, data_list, tsvname) # TODO: _csv.Error: need to escape, but no escapechar set
            
            tlactivity = f'Biome Device WIFI - {filename}'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc(f'No data available for Biome Device WIFI')
    

__artifacts__ = {
    "biomeDevWifi": (
        "Biome Device WIFI",
        ('*/Biome/streams/restricted/Device.Wireless.WiFi/local/*'),
        get_biomeDevWifi)
}
