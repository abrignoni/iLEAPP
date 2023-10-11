import os
import plistlib
import nska_deserialize as nd
import datetime
from pathlib import Path
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_draftmessage(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        filename = os.path.basename(file_found) #reusing old code and adding new underneath. I know. "Cringe."
        path = Path(file_found)
        directoryname = (path.parent.name)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in file_found:
                continue
            else:
                pass
        else:
            continue
    
        modifiedtime = os.path.getmtime(file_found)
        modifiedtime = (datetime.datetime.fromtimestamp(int(modifiedtime)).strftime('%Y-%m-%d %H:%M:%S'))
        
        with open(file_found, 'rb') as fp:
            pl = plistlib.load(fp)
            deserialized_plist = nd.deserialize_plist_from_string(pl['text'])
            data_list.append((modifiedtime, directoryname, deserialized_plist['NSString']))
    
    if len(data_list) > 0:
        folderlocation = str(path.resolve().parents[1])
        description = ''
        report = ArtifactHtmlReport(f'Drafts - Native Messages')
        report.start_artifact_report(report_folder, f'Drafts - Native Messages', description)
        report.add_script()
        data_headers = ('Modified Time','Intended Recipient','Draft Message')
        report.write_artifact_data_table(data_headers, data_list, folderlocation)
        report.end_artifact_report()
        
        tsvname = f'Drafts - Native Messages'
        tsv(report_folder, data_headers, data_list, tsvname) # TODO: _csv.Error: need to escape, but no escapechar set
        
        tlactivity = f'Drafts - Native Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc(f'No data available for Drafts - Native Messages')
    

__artifacts__ = {
    "draftmessage": (
        "Draft Native Messages",
        ('*/SMS/Drafts/*/composition.plist'),
        get_draftmessage)
}