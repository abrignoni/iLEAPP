__artifacts_v2__ = {
    'get_torrentinfo': {
        'name': 'BitTorrent Info',
        'description': 'Extracts metadata and file lists from .torrent files',
        'author': '@AlexisBrignoni',
        'creation_date': '2023-03-27',
        'last_update_date': '2025-11-28',
        'requirements': 'bencoding',
        'category': 'Downloads',
        'notes': '',
        'paths': ('*/*.torrent',),
        'output_types': 'standard',
        'artifact_icon': 'download',
        'html_columns': ['Data']
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
def get_torrentinfo(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found

        try:
            with open(file_found, 'rb') as f:
                decodedDict = bencoding.bdecode(f.read())

            aggregate = ''
            infohash = ''

            if b"info" in decodedDict:
                try:
                    infoh = hashlib.sha1(bencoding.bencode(decodedDict[b"info"])).hexdigest()
                    infohash = infoh.upper()
                except Exception as e:
                    infohash = ''

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

                                aggregate += f'File: {path_str} <br>Size: {size_str} bytes <br>'

                        elif x_str == 'name':
                             try:
                                 name_val = y.decode("utf-8", "ignore")
                             except:
                                 name_val = str(y)
                             aggregate += f'Name: {name_val} <br>'

                        elif x_str == 'length':
                             aggregate += f'Size: {y} bytes <br>'

                        else:
                             try:
                                val_str = y.decode('utf-8', 'ignore') if isinstance(y, bytes) else str(y)
                                aggregate += f'{x_str}: {val_str} <br>'
                             except:
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
                    except:
                        pass

            aggregate = aggregate.strip()
            wrapped_path = textwrap.fill(file_found, width=50)
            data_list.append((wrapped_path, infohash, aggregate))

        except Exception as e:
            logfunc(f"Error parsing {file_found}: {str(e)}")

    data_headers = ('File', 'InfoHash', 'Data')

    if not data_list:
        logfunc('No Torrent data found')
        return data_headers, [], source_path

    return data_headers, data_list, source_path
