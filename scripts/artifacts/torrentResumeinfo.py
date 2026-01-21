__artifacts_v2__ = {
    'get_torrentResumeinfo': {
        'name': 'BitTorrent Resume Info',
        'description': 'Extracts resume data from BitTorrent files',
        'author': '@AlexisBrignoni',
        'creation_date': '2023-03-27',
        'last_update_date': '2025-11-28',
        'requirements': 'bencoding',
        'category': 'Downloads',
        'notes': '',
        'paths': ('*/*.resume',),
        'output_types': 'standard',
        'artifact_icon': 'download-cloud',
        'html_columns': ['Data']
    }
}

import bencoding
import hashlib
import textwrap
from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc
    )


@artifact_processor
def get_torrentResumeinfo(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found

        try:
            with open(file_found, 'rb') as f:
                decodedDict = bencoding.bdecode(f.read())
        except Exception:
            continue

        aggregate = ''
        infohash = ''
        try:
            if b"info" in decodedDict:
                infoh = hashlib.sha1(bencoding.bencode(decodedDict[b"info"])).hexdigest()
                infohash = infoh
        except:
            pass

        for key, value in decodedDict.items():
            key_str = key.decode('utf-8', 'ignore')
            if key_str == 'info':
                for x, y in value.items():
                    x_str = x.decode('utf-8', 'ignore')
                    if x_str == 'pieces':
                        pass
                    else:
                        aggregate += f'{x_str}: {y} <br>'
            elif key_str == 'pieces':
                pass
            elif key_str == 'creation date':
                ts_val = convert_unix_ts_to_utc(value)
                aggregate += f'{key_str}: {ts_val} <br>'
            else:
                aggregate += f'{key_str}: {value} <br>' 
        wrapped_path = textwrap.fill(file_found, width=50)
        data_list.append((wrapped_path, infohash, aggregate.strip()))

    data_headers = ('File', 'InfoHash', 'Data')

    return data_headers, data_list, source_path
