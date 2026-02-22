import bencoding
import hashlib
import datetime
import textwrap

from scripts.ilapfuncs import artifact_processor


def timestampcalc(timevalue):
    timestamp = (datetime.datetime.fromtimestamp(int(timevalue)).strftime('%Y-%m-%d %H:%M:%S'))
    return timestamp


@artifact_processor
def get_torrentResumeinfo(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_list = []
    file_found = str(files_found[0])

    for file_found in files_found:
        file_found = str(file_found)

        with open(file_found, 'rb') as f:
            decodedDict = bencoding.bdecode(f.read())

        aggregate = ''
        try:
            infoh = hashlib.sha1(bencoding.bencode(decodedDict[b"info"])).hexdigest()
            infohash = infoh
        except Exception:
            infohash = ''

        for key, value in decodedDict.items():
            if key.decode() == 'info':
                for x, y in value.items():
                    if x == b'pieces':
                        pass
                    else:
                        aggregate = aggregate + f'{x.decode()}: {y} <br>'
            elif key.decode() == 'pieces':
                pass
            elif key.decode() == 'creation date':
                aggregate = aggregate + f'{key.decode()}: {timestampcalc(value)} <br>'
            else:
                aggregate = aggregate + f'{key.decode()}: {value} <br>'

        data_list.append((textwrap.fill(file_found, width=25), infohash, aggregate.strip()))

    data_headers = ('File', 'InfoHash', 'Data')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_torrentResumeinfo": {
        "name": "Torrent Resume Info",
        "description": "BitTorrent resume file metadata.",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "BitTorrent",
        "notes": "",
        "paths": ('*/*.resume',),
        "output_types": "standard",
        "artifact_icon": "download",
        "html_columns": ["Data"]
    }
}
