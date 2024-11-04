__artifacts_v2__ = {
    "webkitCacheRecords": {
        "name": "WebKit Cache Records",
        "description": "Extracts detailed information from WebKit Network Cache record files",
        "author": "@JamesHabben",
        "version": "1.0",
        "date": "2024-10-24",
        "requirements": "none",
        "category": "Browser",
        "notes": "",
        "paths": ('*/Library/Caches/WebKit/NetworkCache/Version*/Records/*/Resource/*',),
        "output_types": "standard",
        "research_mode": False # Set to True to include all fields
    }
}

import os
import struct
import json
from scripts.ilapfuncs import logfunc, artifact_processor
from datetime import datetime, timezone
from collections import OrderedDict


def read_vf(file):
    try:
        length_bytes = file.read(4)
        if len(length_bytes) < 4:
            return None, None  # Not enough data to read length
        length = struct.unpack('<I', length_bytes)[0]
        flag = file.read(1)
        if flag == b'\x00':
            # Unicode (UTF-16) encoding
            data = file.read(length * 2).decode('utf-16-le', errors='ignore')
        else:
            # UTF-8 encoding
            data = file.read(length).decode('utf-8', errors='ignore')
        return data, flag.hex()
    except struct.error:
        return None, None  # Error unpacking data

def extract_path_info(file_path):
    parts = file_path.split(os.sep)
    app_guid = ''
    records_guid = ''
    
    for i, part in enumerate(parts):
        if part == 'Application' and i + 1 < len(parts):
            app_guid = parts[i + 1]
        elif part == 'Records' and i + 1 < len(parts):
            records_guid = parts[i + 1]
    
    return app_guid, records_guid

def get_headers(research_mode):
    base_headers = (
        'Application GUID', 'Records GUID', 'File', 'URI', ('Timestamp', 'datetime'), 
        'Content Type', 'Body Size', 'Is Body Inline', 'HTTP Headers', 'Response Code', 
        'Full File Path'
    )
    
    research_headers = (
        'Application GUID', 'Records GUID', 'File', 'Header', 'Partition', 
        'Partition Flag', 'Type', 'Type Flag', 'URI', 'URI Flag', 
        'Marker', 'Filename', 'Foldername', 'Timestamp', 'Meta SHA1', 
        'Meta Size', 'Body SHA1', 'Body Size', 'Is Body Inline', 
        'Unknown Hash', 'Start of Meta', 'Meta URI', 'Meta URI Flag', 
        'Marker Content Type', 'Content Type', 'Content Type Flag', 
        'Body Size 2', 'Marker2', 'Encoding Type', 'Encoding Type Flag', 
        'Encoding Pad', 'Encoding Pad Flag', 'HTTP Type', 'HTTP Type Flag', 
        'HTTP Header Count', 'HTTP Headers', 'Has Cookie', 'Response Code', 
        'U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7', 'U8', 'Other Trailing Data', 
        'Trailing Size', 'Trailing Hash', 'Full File Path'
    )
    
    return research_headers if research_mode else base_headers

@artifact_processor
def webkitCacheRecords(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    research_mode = __artifacts_v2__["webkitCacheRecords"].get("research_mode", False)
    data_headers = get_headers(research_mode)
    
    for file_found in files_found:
        if file_found.endswith('-blob'):
            continue
        if research_mode:
            logfunc(f"Processing {file_found}")
        app_guid, records_guid = extract_path_info(file_found)
        file_data = {
            'Application GUID': app_guid,
            'Records GUID': records_guid,
            'File': os.path.basename(file_found),
            'Full File Path': file_found
        }
        try:
            with open(file_found, 'rb') as f:
                file_data['Header'] = struct.unpack('<I', f.read(4))[0]
                file_data['Partition'], file_data['Partition Flag'] = read_vf(f)
                file_data['Type'], file_data['Type Flag'] = read_vf(f)
                file_data['URI'], file_data['URI Flag'] = read_vf(f)
                
                file_data['Marker'] = struct.unpack('<i', f.read(4))[0] 
                file_data['Filename'] = f.read(20).hex()
                file_data['Foldername'] = f.read(20).hex()
                timestamp = struct.unpack('<d', f.read(8))[0]
                file_data['Timestamp'] = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
                file_data['Meta SHA1'] = f.read(20).hex()
                file_data['Meta Size'] = struct.unpack('<Q', f.read(8))[0]
                file_data['Body SHA1'] = f.read(20).hex()
                file_data['Body Size'] = struct.unpack('<Q', f.read(8))[0]
                file_data['Is Body Inline'] = "Yes" if f.read(1) == b'\x01' else "No"
                file_data['Unknown Hash'] = f.read(20).hex()
                
                # Metadata Block
                start_of_meta_pos = f.tell()
                file_data['Start of Meta'] = f.read(1).hex()
                file_data['Meta URI'], file_data['Meta URI Flag'] = read_vf(f)
                
                file_data['Marker Content Type'] = struct.unpack('<I', f.read(4))[0]
                if file_data['Marker Content Type'] < 0xFFFFFFFF:
                    f.seek(-4, 1)  # Move back 4 bytes
                    file_data['Content Type'], file_data['Content Type Flag'] = read_vf(f)
                else:
                    file_data['Content Type'], file_data['Content Type Flag'] = '', ''
                
                file_data['Body Size 2'] = struct.unpack('<Q', f.read(8))[0]
                file_data['Marker2'] = struct.unpack('<I', f.read(4))[0]
                
                if file_data['Marker2'] < 0xFFFFFFFF:
                    f.seek(-4, 1)  # Move back 4 bytes
                    file_data['Encoding Type'], file_data['Encoding Type Flag'] = read_vf(f)
                else:
                    file_data['Encoding Type'], file_data['Encoding Type Flag'] = '', ''
                
                file_data['Encoding Pad'], file_data['Encoding Pad Flag'] = read_vf(f)
                file_data['HTTP Type'], file_data['HTTP Type Flag'] = read_vf(f)
                file_data['HTTP Header Count'] = struct.unpack('<Q', f.read(8))[0]
                
                if file_data['HTTP Header Count'] <= 100:
                    http_headers = {}
                    has_cookie = False
                    for _ in range(file_data['HTTP Header Count']):
                        header, _ = read_vf(f)
                        value, _ = read_vf(f)
                        if header is not None and value is not None:
                            http_headers[header] = value
                            if 'cookie' in header.lower():
                                has_cookie = True
                    # Sort the HTTP headers alphabetically
                    sorted_http_headers = OrderedDict(sorted(http_headers.items()))
                    file_data['HTTP Headers'] = json.dumps(sorted_http_headers)
                    file_data['Has Cookie'] = 'Yes' if has_cookie else 'No'
                    headers_read = True
                else:
                    file_data['HTTP Headers'] = 'Skipped due to high header count'
                    file_data['Has Cookie'] = 'Unknown'
                    headers_read = False
                
                # Read trailing data
                if headers_read:
                    remaining_bytes = file_data['Meta Size'] + start_of_meta_pos - f.tell() - 20
                    other_trailing_data = f.read(remaining_bytes)
                else:
                    f.seek(start_of_meta_pos + file_data['Meta Size'] - 92)
                    other_trailing_data = f.read(72)
                
                # Extract response code and unknown bytes from trailing data
                file_data['Response Code'] = struct.unpack('<H', other_trailing_data[:2])[0]
                file_data['U1'] = other_trailing_data[2]
                file_data['U2'] = other_trailing_data[3]
                file_data['U3'] = other_trailing_data[4:11].hex()
                file_data['U4'] = other_trailing_data[11]
                file_data['U5'] = other_trailing_data[12:19].hex()
                file_data['U6'] = other_trailing_data[19]
                file_data['U7'] = other_trailing_data[20:27].hex()
                file_data['U8'] = other_trailing_data[27]
                file_data['Other Trailing Data'] = f'"{other_trailing_data[28:].hex()}"'
                file_data['Trailing Size'] = len(other_trailing_data)
                
                file_data['Trailing Hash'] = f.read(20).hex()

                if not research_mode:
                    full_data = file_data
                    file_data = {header: full_data.get(header, '') for header in data_headers}
 
                
        except Exception as e:
            if research_mode:
                logfunc(f"Error processing {file_found}: {str(e)}")
        finally:
            # Append whatever data we have, even if it's incomplete
            data_list.append(tuple(file_data.get(header, '') for header in data_headers))
    
    return data_headers, data_list, ''
