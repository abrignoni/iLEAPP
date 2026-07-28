""" torrentinfo """
__artifacts_v2__ = {
    'torrent_info': {
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

import hashlib
from html import escape
import bencoding
from bencoding.decoder import DecoderError

from scripts.ilapfuncs import (
    artifact_processor,
    logfunc,
    convert_unix_ts_to_utc
)


def _decode_torrent_value(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', 'ignore')
    return str(value)


@artifact_processor
def torrent_info(context):
    """ see artifact description """
    files_found = context.get_files_found()
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found

        try:
            with open(file_found, 'rb') as f:
                decoded_dict = bencoding.bdecode(f.read())

            aggregate = ''
            infohash = ''

            if b"info" in decoded_dict:
                try:
                    infoh = hashlib.sha1(bencoding.bencode(decoded_dict[b"info"])).hexdigest()
                    infohash = infoh.upper()
                except (KeyError, TypeError, ValueError):
                    infohash = ''

            for key, value in decoded_dict.items():
                key_str = _decode_torrent_value(key)

                if key_str == 'info':
                    for x, y in value.items():
                        x_str = _decode_torrent_value(x)

                        if x_str == 'pieces':
                            continue

                        elif x_str == 'files':
                            for file_item in y:
                                path_str = ''
                                size_str = ''

                                if b'path' in file_item:
                                    try:
                                        path_parts = [_decode_torrent_value(p) for p in file_item[b'path']]
                                        path_str = '/'.join(path_parts)
                                    except (AttributeError, TypeError):
                                        path_str = _decode_torrent_value(file_item[b'path'])

                                if b'length' in file_item:
                                    size_str = str(file_item[b'length'])

                                aggregate += f'File: {escape(path_str)} <br>Size: {escape(size_str)} bytes <br>'

                        elif x_str == 'name':
                            name_val = _decode_torrent_value(y)
                            aggregate += f'Name: {escape(name_val)} <br>'

                        elif x_str == 'length':
                            aggregate += f'Size: {escape(str(y))} bytes <br>'

                        else:
                            val_str = _decode_torrent_value(y)
                            aggregate += f'{escape(x_str)}: {escape(val_str)} <br>'

                elif key_str == 'pieces':
                    continue

                elif key_str == 'creation date':
                    ts_obj = convert_unix_ts_to_utc(value)
                    aggregate += f'{escape(key_str)}: {escape(str(ts_obj))} <br>'

                else:
                    val_str = _decode_torrent_value(value)
                    aggregate += f'{escape(key_str)}: {escape(val_str)} <br>'

            aggregate = aggregate.strip()
            relative_path = context.get_relative_path(file_found)
            data_list.append((relative_path, infohash, aggregate))

        except (DecoderError, OSError, TypeError, ValueError) as e:
            logfunc(f"Error parsing {file_found}: {str(e)}")

    data_headers = ('File', 'InfoHash', 'Data')

    if not data_list:
        logfunc('No Torrent data found')
        return data_headers, [], source_path

    return data_headers, data_list, source_path
