import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows


def get_wifi(files_found, report_folder, seeker):
    data_list = []       
    file_found = str(files_found[0])

    with open(file_found, "rb") as fp:        
        pl = plistlib.load(fp)

        if 'List of known networks' in pl.keys():
            for dic in pl['List of known networks']: 
                ssid = dic['SSID_STR']
                bssid = ""
                if 'BSSID' in dic.keys():
                    bssid = dic['BSSID']
                        
                    netusage = ""    
                    if 'networkUsage' in dic.keys():             
                        netusage = str(dic['networkUsage'])
                    
                    countrycode = ""
                    if '80211D_IE' in dic.keys():
                        for key2, val2 in dic['80211D_IE'].items():
                            if key2 == 'IE_KEY_80211D_COUNTRY_CODE':
                                countrycode = val2

                    devname = ""
                    mfr = ""
                    serialnum = ""
                    modelname = ""
                    if 'WPS_PROB_RESP_IE' in dic.keys():
                        for key3, val3 in dic['WPS_PROB_RESP_IE'].items():
                                
                            if key3 == 'IE_KEY_WPS_DEV_NAME':
                                    devname = val3
                            if key3 == 'IE_KEY_WPS_MANUFACTURER':
                                    mfr = val3
                            if key3 == 'IE_KEY_WPS_SERIAL_NUM':
                                    serialnum = val3
                            if key3 == 'IE_KEY_WPS_MODEL_NAME':
                                modelname = val3
                        
                    lastjoined = ""    
                    if 'lastJoined' in dic.keys():
                        lastjoined = str(dic['lastJoined'])
                    lastautojoined = ""
                    if 'lastAutoJoined' in dic.keys():    
                        lastautojoined = str(dic['lastAutoJoined'])
                    enabled = ""    
                    if 'enabled' in dic.keys():
                        enabled = str(dic['enabled'])    
                        
                    data_list.append((ssid, bssid, netusage, countrycode, devname, mfr, serialnum, modelname, lastjoined, lastautojoined, enabled))

    if len(data_list) > 0:
        report = ArtifactHtmlReport('Wifi')
        report.start_artifact_report(report_folder, 'Wifi')
        report.add_script()
        data_headers = ('SSID','BSSID', 'Network usage', 'Country code', 'Device name', 'Manufacturer', 'Serial number', 'Model name', 'Last joined', 'Last autojoined', 'Enabled')     
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Wifi'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No Networks data')

    