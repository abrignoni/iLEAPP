import os
import datetime
import json
import plistlib
import datetime
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, logdevinfo

def timestampcalc(timevalue):
    timestamp = (datetime.datetime.fromtimestamp(int(timevalue)).strftime('%Y-%m-%d %H:%M:%S'))
    return timestamp

    
def get_siminfo(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_lista = []
    data_listb = []
    
    for file_found in files_found:
        file_found = str(file_found)
    
        #file_found = './com.apple.commcenter.data.plist'
    
        with open(file_found, "rb") as fp:
                pl = plistlib.load(fp)
                for key, val in pl.items():
                    if key == 'PersonalWallet':
                        for x, y in val.items():
                            simid = x
                            for a, z in y.items():
                                cbver = z.get('cb_ver', '')
                                labelid = z.get('label-id', '')
                                labelidconf = z.get('label-id-confirmed', '')
                                tss = z.get('ts', '')
                                tss = timestampcalc(tss)
                                cbid = z.get('cb_id', '')
                                mdn = z.get('mdn', '')
                                esim = z.get('esim', '')
                                eapaka = z.get('eap_aka', '')
                                types = z.get('type', '')
                                nosrc = z.get('no_src', '')
                                data_lista.append((tss,mdn,esim,types,cbid,nosrc,labelid,labelidconf,eapaka,cbver))
                                
                    if key == 'unique-sim-label-store':
                        for x, y in val.items():
                            simlabelstoreid = x
                            tag = y.get('tag', '')
                            text = y.get('text', '')
                            ts = y.get('ts', '')
                            ts = timestampcalc(ts)
                            data_listb.append((ts,tag,simlabelstoreid,text))
                        
                        
    if data_lista:
        report = ArtifactHtmlReport('SIM - UUID')
        report.start_artifact_report(report_folder, 'SIM - UUID')
        report.add_script()
        data_headers = ('Timestamp Unknown','MDM','ESIM','Type','CB_ID','No_SRC','Label-ID','Label-ID Confirmed','EAP_AKA','CB_Ver')
        report.write_artifact_data_table(data_headers, data_lista, file_found)
        report.end_artifact_report()
        
        tsvname = f'SIM - UUID'
        tsv(report_folder, data_headers, data_lista, tsvname)
        
        tlactivity = f'SIM - UUID'
        timeline(report_folder, tlactivity, data_lista, data_headers)
        
    else:
        logfunc('No SIM - UUID data available')
        
    if data_listb:
        report = ArtifactHtmlReport('SIM - Unique Label Store')
        report.start_artifact_report(report_folder, 'SIM - Unique Label Store')
        report.add_script()
        data_headers = ('Timestamp','Tag','SIM Label Store ID','Text')
        report.write_artifact_data_table(data_headers, data_listb, file_found)
        report.end_artifact_report()
        
        tsvname = f'SIM - Unique Label Store'
        tsv(report_folder, data_headers, data_listb, tsvname)
        
        tlactivity = f'SIM - Unique Label Store'
        timeline(report_folder, tlactivity, data_listb, data_headers)
        
    else:
        logfunc('No SIM - Unique Label Store data available')

__artifacts__ = {
    "siminfo": (
        "SIM Info",
        ('*/com.apple.commcenter.data.plist'),
        get_siminfo)
}