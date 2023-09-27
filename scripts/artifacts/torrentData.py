import sqlite3
import textwrap
import bencoding
import hashlib
from datetime import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, kmlgen

def get_TorrentData(files_found, report_folder, seeker, wrap_text):
    
    data_list = []
    
    for file_found in files_found:
        file_name = str(file_found)
        if file_found.endswith('.torrent'):
            
            with open(file_found, 'rb') as f:
                encoded_data = f.read()
                
            decodedDict = bencoding.bdecode(encoded_data)
            info_hash = hashlib.sha1(bencoding.bencode(decodedDict[b"info"])).hexdigest().upper()
                
            torrentihas = torrentname = spath = iname = tdown = tup = aggf = agg = ''
            for key,value in decodedDict.items():
                #print(key,value)
                if key == b'info':
                    for ikey, ivalue in value.items():
                        if ikey == b'piece length':
                            pass
                        if ikey == b'name':
                            torrentname = (ivalue.decode())
                            #print(torrentname)
                        if ikey == b'files':
                            aggf = '<table>'
                            for files in ivalue:
                                for iikey, iivalue in files.items():
                                    if iikey == b'length':
                                        lenghtf = (iivalue)
                                    if iikey == b'path':
                                        if len(iivalue) > 1:
                                            dirr = (iivalue[0].decode())
                                            filen = (iivalue[1].decode())
                                        else:
                                            dirr = ''
                                            filen = (iivalue[0].decode())
                                    #print(f'Path: {dirr}/{filen}')
                                aggf = aggf + f'<tr><td>{dirr}</td><td>{filen}</td></tr>'
                            aggf = aggf + f'</table>'    
                        #print(ikey, ivalue)
                elif key == b'trackers':
                    pass
                elif key == b'pieces':
                    pass
                elif key == b'peers':
                    pass
                elif key == b'banned_peers':
                    pass
                elif key == b'banned_peers6':
                    pass
                elif key == b'peers6':
                    pass
                elif key == b'mapped_files':
                    pass
                elif key == b'piece_priority':
                    pass
                elif key == b'file_priority':
                    pass
                elif key == b'info-hash':
                    pass #need to use bencode tools to reverse engineer the number
                elif key == b'info-hash2':
                    pass
                elif key == b'save_path':
                    spath = value.decode()
                elif key == b'name':
                    iname = value.decode()
                elif key == b'total_downloaded':
                    tdown = value
                elif key == b'total_uploaded':
                    tup = value
                else:
                    if (isinstance(value, int)):
                        value = value
                    elif (isinstance(value, list)):
                        value = str(value)
                    else:
                        value = value
                    
            data_list.append((torrentname,info_hash,aggf))
    
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Torrent Data')
        report.start_artifact_report(report_folder, 'Torrent Data')
        report.add_script()
        data_headers = ('Torrent Name','Info Hash','Path')
        report.write_artifact_data_table(data_headers, data_list, file_found,html_escape=False)
        report.end_artifact_report()
        
        tsvname = f'Torrent Data'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('No Torrent Data available')
        


__artifacts__ = {
        "TorrentData": (
                "Torrent Data",
                ('*/*.torrent'),
                get_TorrentData)
}
