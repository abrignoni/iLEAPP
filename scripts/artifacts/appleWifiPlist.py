import glob
import plistlib
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, tsv, is_platform_windows 

def hexify_byte(byte_to_convert):
    to_return = hex(byte_to_convert).replace('0x','')
    if len(to_return) < 2:
        to_return = "0" + to_return

    return to_return

def _bytes_to_mac_address(encoded_bytes):
    to_return = ''
    to_return = hexify_byte(encoded_bytes[0]) + ":" + hexify_byte(encoded_bytes[1]) + ":"
    to_return = to_return + hexify_byte(encoded_bytes[2]) + ":" + hexify_byte(encoded_bytes[3]) + ":"
    to_return = to_return + hexify_byte(encoded_bytes[4]) + ":" + hexify_byte(encoded_bytes[5])

    return to_return

def get_appleWifiPlist(files_found, report_folder, seeker, wrap_text, timezone_offset):
    known_data_list = []
    scanned_data_list = []
    known_files = []
    scanned_files = []
    for file_found in files_found:
        file_found = str(file_found)

        with open(file_found, 'rb') as f:
            deserialized = plistlib.load(f)
            if 'KeepWiFiPoweredAirplaneMode' in deserialized:
                val = (deserialized['KeepWiFiPoweredAirplaneMode'])
                logdevinfo(f"Keep Wifi Powered Airplane Mode: {val}")

            if 'List of known networks' in deserialized:
                known_files.append(file_found)
                for known_network in deserialized['List of known networks']:
                    ssid = ''
                    bssid = ''
                    last_updated = ''
                    last_auto_joined = ''
                    wnpmd = ''
                    net_usage = ''
                    country_code = ''
                    device_name = ''
                    manufacturer = ''
                    serial_number = ''
                    model_name = ''
                    enabled = ''
                    last_joined = ''
                    add_reason = ''
                    carplay = ''
                    bundle = ''
                    system_joined = ''
                    user_joined = ''

                    if 'SSID_STR' in known_network:
                        ssid = str(known_network['SSID_STR'])

                    if 'BSSID' in known_network:
                        bssid = str(known_network['BSSID'])

                    if 'networkUsage' in known_network:
                        net_usage = str(known_network['networkUsage'])

                    if '80211D_IE' in known_network:
                        if 'IE_KEY_80211D_COUNTRY_CODE' in known_network['80211D_IE']:
                            country_code = str(known_network['80211D_IE']['IE_KEY_80211D_COUNTRY_CODE'])

                    if 'lastUpdated' in known_network:
                        last_updated = str(known_network['lastUpdated'])

                    if 'lastAutoJoined' in known_network:
                        last_auto_joined = str(known_network['lastAutoJoined'])

                    if 'lastJoined' in known_network:
                        last_joined = str(known_network['lastJoined'])

                    if 'WiFiNetworkPasswordModificationDate' in known_network:
                        wnpmd = str(known_network['WiFiNetworkPasswordModificationDate'])

                    if 'enabled' in known_network:
                        enabled = str(known_network['enabled'])

                    if 'WPS_PROB_RESP_IE' in known_network:
                    
                        if 'IE_KEY_WPS_DEV_NAME' in known_network['WPS_PROB_RESP_IE']: 
                            device_name = known_network['WPS_PROB_RESP_IE']['IE_KEY_WPS_DEV_NAME']
                        if 'IE_KEY_WPS_MANUFACTURER' in known_network['WPS_PROB_RESP_IE']: 
                            manufacturer = known_network['WPS_PROB_RESP_IE']['IE_KEY_WPS_MANUFACTURER']
                        if 'IE_KEY_WPS_SERIAL_NUM' in known_network['WPS_PROB_RESP_IE']: 
                            serial_number = known_network['WPS_PROB_RESP_IE']['IE_KEY_WPS_SERIAL_NUM']
                        if 'IE_KEY_WPS_MODEL_NAME' in known_network['WPS_PROB_RESP_IE']: 
                            model_name = known_network['WPS_PROB_RESP_IE']['IE_KEY_WPS_MODEL_NAME']

                    if 'CARPLAY_NETWORK' in known_network:
                        carplay = str(known_network['CARPLAY_NETWORK'])
                    
                    known_data_list.append([ssid,
                                            bssid, 
                                            net_usage, 
                                            country_code, 
                                            device_name, 
                                            manufacturer, 
                                            serial_number, 
                                            model_name, 
                                            last_joined, 
                                            last_auto_joined, 
                                            system_joined,
                                            user_joined,
                                            last_updated, 
                                            enabled, 
                                            wnpmd, 
                                            carplay, 
                                            add_reason, 
                                            bundle, 
                                            file_found]) 

            if 'com.apple.wifi.known-networks.plist' in file_found:
                known_files.append(file_found)
                for network_key in deserialized:
                    known_network = deserialized[network_key]
                    ssid = ''
                    bssid = ''
                    last_updated = ''
                    last_auto_joined = ''
                    wnpmd = ''
                    net_usage = ''
                    country_code = ''
                    device_name = ''
                    manufacturer = ''
                    serial_number = ''
                    model_name = ''
                    enabled = ''
                    last_joined = ''
                    add_reason = ''
                    bundle = ''
                    system_joined = ''
                    user_joined = ''
                    carplay = ''

                    if 'SSID' in known_network:
                        ssid = str(known_network['SSID'])

                    if 'AddReason' in known_network:
                        add_reason = str(known_network['AddReason'])

                    if 'UpdatedAt' in known_network:
                        last_updated = str(known_network['UpdatedAt'])

                    if 'JoinedBySystemAt' in known_network:
                        system_joined = str(known_network['JoinedBySystemAt'])

                    if 'JoinedByUserAt' in known_network:
                        user_joined = str(known_network['JoinedByUserAt'])

                    if 'BundleID' in known_network:
                        bundle = str(known_network['BundleID'])

                    if '__OSSpecific__' in known_network:

                        if 'BSSID' in known_network['__OSSpecific__']:
                            bssid = str(known_network['__OSSpecific__']['BSSID'])

                        if 'networkUsage' in known_network['__OSSpecific__']:
                            net_usage = str(known_network['__OSSpecific__']['networkUsage'])

                        if 'WiFiNetworkPasswordModificationDate' in known_network['__OSSpecific__']:
                            wnpmd = str(known_network['__OSSpecific__']['WiFiNetworkPasswordModificationDate'])

                        if 'CARPLAY_NETWORK' in known_network['__OSSpecific__']:
                            carplay = str(known_network['__OSSpecific__']['CARPLAY_NETWORK'])

                    known_data_list.append([ssid,
                                            bssid, 
                                            net_usage, 
                                            country_code, 
                                            device_name, 
                                            manufacturer, 
                                            serial_number, 
                                            model_name, 
                                            last_joined, 
                                            last_auto_joined, 
                                            system_joined,
                                            user_joined,
                                            last_updated, 
                                            enabled, 
                                            wnpmd, 
                                            carplay, 
                                            add_reason, 
                                            bundle, 
                                            file_found]) 

            if 'List of scanned networks with private mac' in deserialized:
                scanned_files.append(file_found)
                for scanned_network in deserialized['List of scanned networks with private mac']:
                    ssid = ''
                    bssid = ''
                    last_updated = ''
                    last_joined = ''
                    private_mac_in_use = ''
                    private_mac_value = ''
                    private_mac_valid = ''
                    added_at = ''
                    in_known_networks = ''

                    if 'SSID_STR' in scanned_network:
                        ssid = str(scanned_network['SSID_STR'])

                    if 'BSSID' in scanned_network:
                        bssid = str(scanned_network['BSSID'])

                    if 'lastUpdated' in scanned_network:
                        last_updated = str(scanned_network['lastUpdated'])

                    if 'lastJoined' in scanned_network:
                        last_joined = str(scanned_network['lastJoined'])

                    if 'addedAt' in scanned_network:
                        added_at = str(scanned_network['addedAt'])

                    if 'PresentInKnownNetworks' in scanned_network:
                        in_known_networks = str(scanned_network['PresentInKnownNetworks'])

                    if 'PRIVATE_MAC_ADDRESS' in scanned_network:
                        if 'PRIVATE_MAC_ADDRESS_IN_USE' in scanned_network['PRIVATE_MAC_ADDRESS']:
                            private_mac_in_use = str(_bytes_to_mac_address(scanned_network['PRIVATE_MAC_ADDRESS']['PRIVATE_MAC_ADDRESS_IN_USE']))
                        if 'PRIVATE_MAC_ADDRESS_VALUE' in scanned_network['PRIVATE_MAC_ADDRESS']:
                            private_mac_value = str(_bytes_to_mac_address(scanned_network['PRIVATE_MAC_ADDRESS']['PRIVATE_MAC_ADDRESS_VALUE']))
                        if 'PRIVATE_MAC_ADDRESS_VALID' in scanned_network['PRIVATE_MAC_ADDRESS']:
                            private_mac_valid = str(scanned_network['PRIVATE_MAC_ADDRESS']['PRIVATE_MAC_ADDRESS_VALID'])
                    
                    scanned_data_list.append([ssid, bssid, added_at, last_joined, last_updated, private_mac_in_use, private_mac_value, private_mac_valid, in_known_networks, file_found]) 
            
    if len(known_data_list) > 0:
        description = 'WiFi known networks data. Dates are taken straight from the source plist.'
        report = ArtifactHtmlReport('Locations')
        report.start_artifact_report(report_folder, 'WiFi Known Networks', description)
        report.add_script()
        data_headers = ['SSID','BSSID','Network Usage','Country Code','Device Name','Manufacturer','Serial Number','Model Name','Last Joined','Last Auto Joined','System Joined','User Joined','Last Updated','Enabled','WiFi Network Password Modification Date','Carplay Network','Add Reason','Bundle ID','File']
        report.write_artifact_data_table(data_headers, known_data_list, ', '.join(known_files))
        report.end_artifact_report()
        
        tsvname = 'WiFi Known Networks'
        tsv(report_folder, data_headers, known_data_list, tsvname)
        
        tlactivity = 'WiFi Known Networks'
        timeline(report_folder, tlactivity, known_data_list, data_headers)
            
    if len(scanned_data_list) > 0:
        description = 'WiFi networks scanned while using fake ("private") MAC address. Dates are taken straight from the source plist.'
        report = ArtifactHtmlReport('Locations')
        report.start_artifact_report(report_folder, 'WiFi Networks Scanned (private)', description)
        report.add_script()
        data_headers = ['SSID','BSSID','Added At','Last Joined','Last Updated','MAC Used For Network','Private MAC Computed For Network','MAC Valid','In Known Networks','File']
        report.write_artifact_data_table(data_headers, scanned_data_list, ', '.join(scanned_files))
        report.end_artifact_report()
        
        tsvname = 'WiFi Networks Scanned (private)'
        tsv(report_folder, data_headers, scanned_data_list, tsvname)
        
        tlactivity = 'WiFi Networks Scanned (private)'
        timeline(report_folder, tlactivity, scanned_data_list, data_headers)

__artifacts__ = {
    "applewifiplist": (
        "Wifi Connections",
        ('**/com.apple.wifi.plist', '**/com.apple.wifi-networks.plist.backup', '**/com.apple.wifi.known-networks.plist', '**/com.apple.wifi-private-mac-networks.plist'),
        get_appleWifiPlist)
}