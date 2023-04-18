import bencoding
import hashlib
import datetime
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows 

def timestampcalc(timevalue):
    timestamp = (datetime.datetime.fromtimestamp(int(timevalue)).strftime('%Y-%m-%d %H:%M:%S'))
    return timestamp

def get_torrentResumeinfo(files_found, report_folder, seeker, wrap_text):

    data_list = []
    for file_found in files_found:
        file_found = str(file_found)

        with open(file_found, 'rb') as f:
            decodedDict = bencoding.bdecode(f.read())
        
        aggregate = ''
        try:
            infoh= hashlib.sha1(bencoding.bencode(decodedDict[b"info"])).hexdigest()
            infohash = infoh
        except:
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
                aggregate = aggregate + f'{key.decode()}: {value} <br>' #add if value is binary decode
        
        data_list.append((textwrap.fill(file_found, width=25),infohash,aggregate.strip()))

    # Reporting
    title = "Torrent Resume Info"
    report = ArtifactHtmlReport(title)
    report.start_artifact_report(report_folder, title)
    report.add_script()
    data_headers = ('File', 'InfoHash', 'Data')
    report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Data'])
    report.end_artifact_report()
    
    tsv(report_folder, data_headers, data_list, title)

__artifacts__ = {
    "torrentResumeinfo": (
        "BitTorrent",
        ('*/*.resume'),
        get_torrentResumeinfo)
}