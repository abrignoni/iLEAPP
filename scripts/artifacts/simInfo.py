import datetime
import plistlib

from scripts.ilapfuncs import artifact_processor

def timestampcalc(timevalue):
    timestamp = (datetime.datetime.fromtimestamp(int(timevalue)).strftime('%Y-%m-%d %H:%M:%S'))
    return timestamp


@artifact_processor
def get_siminfo_uuid(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []

    for file_found in files_found:
        file_found = str(file_found)

        with open(file_found, "rb") as fp:
            pl = plistlib.load(fp)
            for key, val in pl.items():
                if key == 'PersonalWallet':
                    for x, y in val.items():
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
                            data_list.append((tss,mdn,esim,types,cbid,nosrc,labelid,labelidconf,eapaka,cbver))

    data_headers = ('Timestamp Unknown','MDM','ESIM','Type','CB_ID','No_SRC','Label-ID','Label-ID Confirmed','EAP_AKA','CB_Ver')
    return data_headers, data_list, file_found


@artifact_processor
def get_siminfo_label_store(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []

    for file_found in files_found:
        file_found = str(file_found)

        with open(file_found, "rb") as fp:
            pl = plistlib.load(fp)
            for key, val in pl.items():
                if key == 'unique-sim-label-store':
                    for x, y in val.items():
                        tag = y.get('tag', '')
                        text = y.get('text', '')
                        ts = y.get('ts', '')
                        ts = timestampcalc(ts)
                        data_list.append((ts,tag,x,text))

    data_headers = ('Timestamp','Tag','SIM Label Store ID','Text')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_siminfo_uuid": {
        "name": "SIM - UUID",
        "description": "",
        "author": "",
        "version": "0.2",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "SIM Info",
        "notes": "",
        "paths": ('*/com.apple.commcenter.data.plist'),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    },
    "get_siminfo_label_store": {
        "name": "SIM - Unique Label Store",
        "description": "",
        "author": "",
        "version": "0.2",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "SIM Info",
        "notes": "",
        "paths": ('*/com.apple.commcenter.data.plist'),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
