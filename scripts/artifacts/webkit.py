import os
import struct
import json
from scripts.ilapfuncs import logfunc, artifact_processor

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
        "output_types": "standard"
    }
}

def read_vf(file):
    length = struct.unpack('>I', file.read(4))[0]
    flag = file.read(1)
    data = file.read(length).decode('utf-8', errors='ignore')
    return data

@artifact_processor
def webkitCacheRecords(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    data_headers = ('File', 'Header', 'Partition', 'Type', 'URI', 'Marker', 'Filename', 'Foldername', 
                    'Timestamp', 'Meta SHA1', 'Meta Size', 'Body SHA1', 'Body Size', 'Is Body Inline', 
                    'Unknown Hash', 'Meta URI', 'Content Type', 'Marker2', 'Unknown1', 'Unknown2', 
                    'HTTP Type', 'HTTP Header Count', 'HTTP Headers', 'Trailing Data')
    
    for file_found in files_found:
        with open(file_found, 'rb') as f:
            file_data = {}
            
            file_data['File'] = os.path.basename(file_found)
            file_data['Header'] = struct.unpack('>I', f.read(4))[0]
            file_data['Partition'] = read_vf(f)
            file_data['Type'] = read_vf(f)
            file_data['URI'] = read_vf(f)
            file_data['Marker'] = f.read(4).hex()
            file_data['Filename'] = f.read(20).hex()
            file_data['Foldername'] = f.read(20).hex()
            file_data['Timestamp'] = struct.unpack('>d', f.read(8))[0]
            file_data['Meta SHA1'] = f.read(20).hex()
            file_data['Meta Size'] = struct.unpack('>Q', f.read(8))[0]
            file_data['Body SHA1'] = f.read(20).hex()
            file_data['Body Size'] = struct.unpack('>Q', f.read(8))[0]
            file_data['Is Body Inline'] = "Yes" if f.read(1) == b'\x01' else "No"
            file_data['Unknown Hash'] = f.read(20).hex()
            
            f.seek(1, 1)  # Skip startofmeta
            file_data['Meta URI'] = read_vf(f)
            file_data['Content Type'] = read_vf(f)
            file_data['Marker2'] = f.read(12).hex()
            file_data['Unknown1'] = struct.unpack('>I', f.read(4))[0]
            file_data['Unknown2'] = f.read(1).hex()
            file_data['HTTP Type'] = read_vf(f)
            file_data['HTTP Header Count'] = struct.unpack('>Q', f.read(8))[0]
            
            http_headers = {}
            for _ in range(file_data['HTTP Header Count']):
                header = read_vf(f)
                value = read_vf(f)
                http_headers[header] = value
            file_data['HTTP Headers'] = json.dumps(http_headers)
            
            trailing_data = struct.unpack('>HHQQ', f.read(22))
            trailing_data += (f.read(26).hex(),)
            trailing_data += (read_vf(f),)
            trailing_data += (f.read(4).hex(),)
            trailing_data += (f.read(2).hex(),)
            trailing_data += (f.read(20).hex(),)
            file_data['Trailing Data'] = json.dumps(trailing_data)
            
            data_list.append(tuple(file_data.values()))
    
    return data_headers, data_list, ''