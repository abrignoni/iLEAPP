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
from scripts.ilapfuncs import artifact_processor, logfunc


@artifact_processor
def get_TorrentData(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found
        if not file_found.endswith('.torrent'):
            continue

        try:
            with open(file_found, 'rb') as f:
                encoded_data = f.read()
            decodedDict = bencoding.bdecode(encoded_data)
            info_hash = ''
            try:
                if b"info" in decodedDict:
                    info_hash = hashlib.sha1(bencoding.bencode(decodedDict[b"info"])).hexdigest().upper()
            except Exception:
                info_hash = ''

            torrentname = ''
            files_html = ''
            if b'info' in decodedDict:
                info = decodedDict[b'info']
                if b'name' in info:
                    try:
                        torrentname = info[b'name'].decode('utf-8', 'ignore')
                    except:
                        torrentname = str(info[b'name'])

                if b'files' in info:
                    files_html = '<table style="border: 1px solid black; border-collapse: collapse;">'
                    files_html += '<tr><th style="border: 1px solid black; padding: 5px;">Path</th><th style="border: 1px solid black; padding: 5px;">Size</th></tr>'

                    for file_info in info[b'files']:
                        path = ''
                        size = ''

                        if b'path' in file_info:
                            try:
                                path_parts = [p.decode('utf-8', 'ignore') for p in file_info[b'path']]
                                path = "/".join(path_parts)
                            except:
                                path = str(file_info[b'path'])
                        if b'length' in file_info:
                            size = str(file_info[b'length'])

                        files_html += f'<tr><td style="border: 1px solid black; padding: 5px;">{path}</td><td style="border: 1px solid black; padding: 5px;">{size}</td></tr>'
                    files_html += '</table>'
                elif b'length' in info:
                     size = str(info[b'length'])
                     files_html = f'Single File: {size} bytes'

            data_list.append((torrentname, info_hash, files_html, file_found))

        except Exception as e:
            logfunc(f"Error parsing torrent {file_found}: {str(e)}")

    data_headers = ('Torrent Name', 'Info Hash', 'Files', 'Source File')

    if not data_list:
        logfunc('No Torrent data found')
        return data_headers, [], source_path

    return data_headers, data_list, source_path
