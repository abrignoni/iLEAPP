import bencoding
import hashlib

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_TorrentData(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_list = []
    file_found = str(files_found[0])

    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('.torrent'):

            with open(file_found, 'rb') as f:
                encoded_data = f.read()

            decodedDict = bencoding.bdecode(encoded_data)
            info_hash = hashlib.sha1(bencoding.bencode(decodedDict[b"info"])).hexdigest().upper()

            torrentname = aggf = ''
            for key, value in decodedDict.items():
                if key == b'info':
                    for ikey, ivalue in value.items():
                        if ikey == b'name':
                            try:
                                torrentname = ivalue.decode()
                            except Exception:
                                torrentname = ivalue
                        if ikey == b'files':
                            aggf = '<table>'
                            for files in ivalue:
                                dirr = ''
                                filen = ''
                                for iikey, iivalue in files.items():
                                    if iikey == b'path':
                                        if len(iivalue) > 1:
                                            try:
                                                dirr = iivalue[0].decode()
                                                filen = iivalue[1].decode()
                                            except Exception:
                                                dirr = iivalue[0]
                                                filen = iivalue[1]
                                        else:
                                            dirr = ''
                                            try:
                                                filen = iivalue[0].decode()
                                            except Exception:
                                                filen = iivalue[0]
                                aggf = aggf + f'<tr><td>{dirr}</td><td>{filen}</td></tr>'
                            aggf = aggf + '</table>'

            data_list.append((torrentname, info_hash, aggf))

    data_headers = ('Torrent Name', 'Info Hash', 'Path')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_TorrentData": {
        "name": "Torrent Data",
        "description": "Parsed torrent file data including names and file paths.",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Torrent Data",
        "notes": "",
        "paths": ('*/*.torrent',),
        "output_types": "standard",
        "artifact_icon": "download",
        "html_columns": ["Path"]
    }
}
