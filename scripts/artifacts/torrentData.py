__artifacts_v2__ = {
    'get_TorrentData': {
        'name': 'BitTorrent Data',
        'description': 'Parses .torrent files to extract metadata and file lists.',
        'author': '@AlexisBrignoni',
        'creation_date': '2023-03-27',
        'last_update_date': '2025-11-28',
        'requirements': 'bencoding',
        'category': 'Downloads',
        'notes': '',
        'paths': ('*/*.torrent',),
        'output_types': 'standard',
        'artifact_icon': 'download-cloud',
        'html_columns': ['Files']
    }
}

import bencoding
import hashlib
import textwrap
from scripts.ilapfuncs import (
    artifact_processor,
    logfunc,
    convert_unix_ts_to_utc
)


@artifact_processor
def get_TorrentData(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found

        try:
            with open(file_found, 'rb') as f:
                encoded_data = f.read()
            
            decodedDict = bencoding.bdecode(encoded_data)
            
            aggregate = ''
            infohash = ''
            
            try:
                if b"info" in decodedDict:
                    infoh = hashlib.sha1(bencoding.bencode(decodedDict[b"info"])).hexdigest()
                    infohash = infoh.upper()
            except Exception:
                infohash = ''
            
            torrentname = ''
            
            for key, value in decodedDict.items():
                try:
                    key_str = key.decode('utf-8', 'ignore')
                except (UnicodeDecodeError, AttributeError):
                    key_str = str(key)

                if key_str == 'info':
                    for x, y in value.items():
                        try:
                            x_str = x.decode('utf-8', 'ignore')
                        except (UnicodeDecodeError, AttributeError):
                            x_str = str(x)

                        if x_str == 'pieces':
                            pass
                        elif x_str == 'files':
                            aggregate += '<table style="border: 1px solid black; border-collapse: collapse;">'
                            aggregate += '<tr><th style="border: 1px solid black; padding: 5px;">Path</th><th style="border: 1px solid black; padding: 5px;">Size</th></tr>'
                            
                            for file_item in y:
                                path_str = ''
                                size_str = ''
                                
                                if b'path' in file_item:
                                    try:
                                        path_parts = [p.decode('utf-8', 'ignore') for p in file_item[b'path']]
                                        path_str = "/".join(path_parts)
                                    except Exception:
                                        path_str = str(file_item[b'path'])
                                
                                if b'length' in file_item:
                                    size_str = str(file_item[b'length'])
                                
                                aggregate += f'<tr><td style="border: 1px solid black; padding: 5px;">{path_str}</td>'
                                aggregate += f'<td style="border: 1px solid black; padding: 5px;">{size_str}</td></tr>'
                            
                            aggregate += '</table>'

                        elif x_str == 'name':
                            try:
                                name_val = y.decode("utf-8", "ignore")
                            except (UnicodeDecodeError, AttributeError):
                                name_val = str(y)
                            torrentname = name_val
                            aggregate += f'Name: {name_val} <br>'

                        elif x_str == 'length':
                            size_val = str(y)
                            aggregate += f'Single File Size: {size_val} bytes <br>'

                        else:
                            try:
                                val_str = y.decode('utf-8', 'ignore') if isinstance(y, bytes) else str(y)
                                aggregate += f'{x_str}: {val_str} <br>'
                            except (UnicodeDecodeError, AttributeError):
                                pass

                elif key_str == 'pieces':
                    pass

                elif key_str == 'creation date':
                    ts_obj = convert_unix_ts_to_utc(value)
                    aggregate += f'{key_str}: {ts_obj} <br>'

                else:
                    try:
                        val_str = value.decode('utf-8', 'ignore') if isinstance(value, bytes) else str(value)
                        aggregate += f'{key_str}: {val_str} <br>'
                    except (UnicodeDecodeError, AttributeError):
                        pass
            
            aggregate = aggregate.strip()
            wrapped_path = textwrap.fill(file_found, width=50)
            data_list.append((torrentname, infohash, aggregate, wrapped_path))

        except Exception as e:
            logfunc(f"Error parsing torrent {file_found}: {str(e)}")

    data_headers = ('Torrent Name', 'Info Hash', 'Data', 'Source File')
    
    if not data_list:
        logfunc('No Torrent data found')
        return data_headers, [], source_path

    return data_headers, data_list, source_path