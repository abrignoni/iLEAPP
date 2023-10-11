import json
import datetime
import scripts.artifacts.artGlobals #use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows 

def get_icloudMeta(files_found, report_folder, seeker, wrap_text, timezone_offset):
    counter = 0
    for file_found in files_found:
        file_found = str(file_found)
        counter = counter + 1
        data_list = []
        with open(file_found, "r") as filecontent:
            for line in filecontent:
                jsonconv = json.loads(line)
                length = len(jsonconv)
                for i in range(length):
                    docid = (jsonconv[i].get('document_id', ''))
                    parid = (jsonconv[i].get('parent_id', ''))
                    name = (jsonconv[i].get('name', ''))
                    typee = (jsonconv[i].get('type', ''))
                    deleted= (jsonconv[i].get('deleted', ''))
                    mtime = (jsonconv[i].get('mtime', ''))
                    if mtime > 0:
                        mtime = datetime.datetime.fromtimestamp(mtime/1000)
                    else:
                        mtime = ''
                    ctime = (jsonconv[i].get('ctime', ''))
                    if ctime > 0:
                        ctime = datetime.datetime.fromtimestamp(ctime/1000)
                    else:
                        ctime = ''
                    btime = (jsonconv[i].get('btime', ''))
                    if btime > 0:
                        btime = datetime.datetime.fromtimestamp(btime/1000)
                    else:
                        btime = ''
                    size = (jsonconv[i].get('size', ''))
                    zone = (jsonconv[i].get('zone', ''))
                    exe = (jsonconv[i]['file_flags'].get('is_executable', ''))
                    hid = (jsonconv[i]['file_flags'].get('is_hidden', ''))
                    lasteditor = (jsonconv[i].get('last_editor_name', ''))
                    if lasteditor:
                        lasteditorname = json.loads(jsonconv[i]['last_editor_name'])
                        lasteditorname = (lasteditorname.get('name', ''))
                    else:
                        lasteditorname = ''
                    basehash = (jsonconv[i].get('basehash', ''))
                    data_list.append((btime, ctime, mtime, name, lasteditorname, docid, parid, typee, deleted, size, zone, exe, hid))	
            
        
            if len(data_list) > 0:
                report = ArtifactHtmlReport('iCloud - File Metadata'+' '+str(counter))
                report.start_artifact_report(report_folder, 'iCloud - File Metadata'+' '+str(counter))
                report.add_script()
                data_headers = ('Btime','Ctime','Mtime', 'Name', 'Last Editor Name', 'Doc ID', 'Parent ID', 'Type', 'Deleted?','Size', 'Zone', 'Executable?','Hidden?')   
                report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                report.end_artifact_report()
                
                tsvname = 'iCloud - File Metadata'
                tsv(report_folder, data_headers, data_list, tsvname)
            else:
                logfunc('No data available')

__artifacts__ = {
    "icloudmeta": (
        "iCloud Returns",
        ('*/iclouddrive/Metadata.txt'),
        get_icloudMeta)
}
