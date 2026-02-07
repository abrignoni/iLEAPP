__artifacts_v2__ = {
    "webkitCacheRecords": {
        "name": "WebKit Cache Records",
        "description": "Extracts detailed information from WebKit Network Cache record files",
        "author": "@JamesHabben",
        "creation_date": "2024-10-24",
        "last_update_date": "2025-11-20",
        "requirements": "none",
        "category": "Browser",
        "notes": "",
        "paths": ('*/Library/Caches/WebKit/NetworkCache/Version*/Records/*/Resource/*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "research_mode": False
    }
}

import os
import struct
import json
from collections import OrderedDict
from scripts.ilapfuncs import (
    logfunc,
    artifact_processor,
    convert_unix_ts_to_utc
    )

def read_vf(file):
    try:
        length_bytes = file.read(4)
        if len(length_bytes) < 4:
            return None, None
        length = struct.unpack('<I', length_bytes)[0]
        flag = file.read(1)
        if flag == b'\x00':
            data = file.read(length * 2).decode('utf-16-le', errors='ignore')
        else:
            data = file.read(length).decode('utf-8', errors='ignore')
        return data, flag.hex()
    except struct.error:
        return None, None


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
        'Marker', 'Filename', 'Foldername', ('Timestamp', 'datetime'), 'Meta SHA1',
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
def webkitCacheRecords(context):
    files_found = context.get_files_found()
    data_list = []
    research_mode = __artifacts_v2__["webkitCacheRecords"].get("research_mode", False)
    data_headers = get_headers(research_mode)

    source_path_ref = ''

    for file_found in files_found:
        file_found = str(file_found)

        if os.path.isdir(file_found) or file_found.endswith('-blob') or file_found.endswith('.DS_Store'):
            continue

        if not source_path_ref:
            source_path_ref = file_found

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
                header_bytes = f.read(4)
                if len(header_bytes) < 4:
                    continue

                file_data['Header'] = struct.unpack('<I', header_bytes)[0]

                file_data['Partition'], file_data['Partition Flag'] = read_vf(f)
                file_data['Type'], file_data['Type Flag'] = read_vf(f)
                file_data['URI'], file_data['URI Flag'] = read_vf(f)
                file_data['Marker'] = struct.unpack('<i', f.read(4))[0]
                file_data['Filename'] = f.read(20).hex()
                file_data['Foldername'] = f.read(20).hex()

                timestamp = struct.unpack('<d', f.read(8))[0]
                file_data['Timestamp'] = convert_unix_ts_to_utc(timestamp)

                file_data['Meta SHA1'] = f.read(20).hex()
                file_data['Meta Size'] = struct.unpack('<Q', f.read(8))[0]
                file_data['Body SHA1'] = f.read(20).hex()
                file_data['Body Size'] = struct.unpack('<Q', f.read(8))[0]
                file_data['Is Body Inline'] = "Yes" if f.read(1) == b'\x01' else "No"
                file_data['Unknown Hash'] = f.read(20).hex()

                start_of_meta_pos = f.tell()
                file_data['Start of Meta'] = f.read(1).hex()
                file_data['Meta URI'], file_data['Meta URI Flag'] = read_vf(f)

                file_data['Marker Content Type'] = struct.unpack('<I', f.read(4))[0]
                if file_data['Marker Content Type'] < 0xFFFFFFFF:
                    f.seek(-4, 1)
                    file_data['Content Type'], file_data['Content Type Flag'] = read_vf(f)
                else:
                    file_data['Content Type'], file_data['Content Type Flag'] = '', ''

                file_data['Body Size 2'] = struct.unpack('<Q', f.read(8))[0]
                file_data['Marker2'] = struct.unpack('<I', f.read(4))[0]

                if file_data['Marker2'] < 0xFFFFFFFF:
                    f.seek(-4, 1)
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
                    sorted_http_headers = OrderedDict(sorted(http_headers.items()))
                    file_data['HTTP Headers'] = json.dumps(sorted_http_headers)
                    file_data['Has Cookie'] = 'Yes' if has_cookie else 'No'
                    headers_read = True
                else:
                    file_data['HTTP Headers'] = 'Skipped due to high header count'
                    file_data['Has Cookie'] = 'Unknown'
                    headers_read = False

                if headers_read:
                    remaining_bytes = file_data['Meta Size'] + start_of_meta_pos - f.tell() - 20
                    other_trailing_data = f.read(remaining_bytes)
                else:
                    f.seek(start_of_meta_pos + file_data['Meta Size'] - 92)
                    other_trailing_data = f.read(72)

                if len(other_trailing_data) >= 2:
                    file_data['Response Code'] = struct.unpack('<H', other_trailing_data[:2])[0]
                else:
                    file_data['Response Code'] = ''

                if not research_mode:
                    full_data = file_data
                    file_data = {header[0] if isinstance(header, tuple) else header: full_data.get(header[0] if isinstance(header, tuple) else header, '') for header in data_headers}

                row = []
                for header in data_headers:
                    key = header[0] if isinstance(header, tuple) else header
                    row.append(file_data.get(key, ''))
                data_list.append(tuple(row))

        except Exception as e:
            if research_mode:
                logfunc(f"Error processing {file_found}: {str(e)}")

    if not data_list:
        logfunc('No WebKit Cache Records were successfully parsed.')
        return data_headers, [], source_path_ref

    return data_headers, data_list, source_path_ref
