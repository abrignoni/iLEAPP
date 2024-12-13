__artifacts_v2__ = {
    "appleWifiKnownNetworks": {
        "name": "WiFi Known Networks Info",
        "description": "Parses WiFi connection data for known networks",
        "author": "@AlexisBrignoni",
        "version": "0.2",
        "date": "2024-10-21",
        "requirements": "none",
        "category": "WiFi Connections",
        "notes": "Parses multiple plist files with varying structures. Some fields may be blank.",
        "paths": ('*/com.apple.wifi.plist', 
                  '*/com.apple.wifi-networks.plist.backup', 
                  '*/com.apple.wifi.known-networks.plist'),
        "output_types": "standard"
    },
    "appleWifiKnownNetworksTimes": {
        "name": "WiFi Known Networks Times",
        "description": "Parses time-related data for known WiFi networks",
        "author": "@AlexisBrignoni",
        "version": "0.1",
        "date": "2024-10-21",
        "requirements": "none",
        "category": "WiFi Connections",
        "notes": "Parses multiple plist files with varying structures. Some fields may be blank.",
        "paths": ('*/com.apple.wifi.plist', 
                  '*/com.apple.wifi-networks.plist.backup', 
                  '*/com.apple.wifi.known-networks.plist'),
        "output_types": "standard"
    },
    "appleWifiScannedPrivate": {
        "name": "WiFi Scanned Networks (Private)",
        "description": "Parses WiFi connection data for networks scanned while using private MAC address",
        "author": "@AlexisBrignoni",
        "version": "0.1",
        "date": "2023-05-24",
        "requirements": "none",
        "category": "WiFi Connections",
        "notes": "",
        "paths": ('*/com.apple.wifi-private-mac-networks.plist',),
        "output_types": "standard"
    },
    "appleWifiBSSList": {
        "name": "WiFi BSS List",
        "description": "Parses BSS (Basic Service Set) information for known WiFi networks",
        "author": "@JamesHabben",
        "version": "0.1",
        "date": "2023-05-25",
        "requirements": "none",
        "category": "WiFi Connections",
        "notes": "Extracts detailed BSS information from the com.apple.wifi.plist file",
        "paths": ('*/com.apple.wifi.known-networks.plist',),
        "output_types": "standard"
    }
}

import glob
import plistlib
from scripts.ilapfuncs import device_info, artifact_processor, convert_plist_date_to_timezone_offset

def _bytes_to_mac_address(encoded_bytes):
    return ':'.join(f"{byte:02x}" for byte in encoded_bytes[:6])

def _decode_ssid(ssid_bytes):
    if isinstance(ssid_bytes, bytes):
        try:
            return ssid_bytes.decode('utf-8')
        except UnicodeDecodeError:
            return ssid_bytes.hex()
    return str(ssid_bytes)

@artifact_processor
def appleWifiKnownNetworks(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        with open(file_found, 'rb') as f:
            deserialized = plistlib.load(f)
            if 'KeepWiFiPoweredAirplaneMode' in deserialized:
                val = (deserialized['KeepWiFiPoweredAirplaneMode'])
                device_info('WiFi', 'Keep Wifi Powered Airplane Mode', val, file_found)

            if 'List of known networks' in deserialized:
                for known_network in deserialized['List of known networks']:
                    ssid = _decode_ssid(known_network.get('SSID_STR', b''))
                    bssid = known_network.get('BSSID', '')
                    net_usage = known_network.get('networkUsage', '')
                    country_code = known_network.get('80211D_IE', {}).get('IE_KEY_80211D_COUNTRY_CODE', '')
                    enabled = known_network.get('enabled', '')
                    carplay = known_network.get('CarPlayNetwork', known_network.get('CARPLAY_NETWORK', ''))
                    hidden = known_network.get('Hidden', '')

                    wps_info = known_network.get('WPS_PROB_RESP_IE', {})
                    device_name = wps_info.get('IE_KEY_WPS_DEV_NAME', '')
                    manufacturer = wps_info.get('IE_KEY_WPS_MANUFACTURER', '')
                    serial_number = wps_info.get('IE_KEY_WPS_SERIAL_NUM', '')
                    model_name = wps_info.get('IE_KEY_WPS_MODEL_NAME', '')

                    captive_profile = known_network.get('CaptiveProfile', {})
                    captive_network = captive_profile.get('CaptiveNetwork', '')
                    user_portal_url = captive_profile.get('UserPortalURL', '')

                    data_list.append([ssid, bssid, net_usage, country_code, device_name, manufacturer, 
                                      serial_number, model_name, enabled, carplay, hidden, captive_network, 
                                      user_portal_url, '', '', file_found])

            if 'com.apple.wifi.known-networks.plist' in file_found:
                for network_key, known_network in deserialized.items():
                    ssid = _decode_ssid(known_network.get('SSID', b''))
                    add_reason = known_network.get('AddReason', '')
                    bundle = known_network.get('BundleID', '')
                    hidden = known_network.get('Hidden', '')

                    os_specific = known_network.get('__OSSpecific__', {})
                    bssid = os_specific.get('BSSID', '')
                    net_usage = os_specific.get('networkUsage', '')
                    carplay = os_specific.get('CarPlayNetwork', known_network.get('CARPLAY_NETWORK', ''))

                    captive_profile = known_network.get('CaptiveProfile', {})
                    captive_network = captive_profile.get('CaptiveNetwork', '')
                    user_portal_url = captive_profile.get('UserPortalURL', '')

                    data_list.append([ssid, bssid, net_usage, '', '', '', '', '', '', carplay, hidden, 
                                      captive_network, user_portal_url, add_reason, bundle, file_found])

    data_headers = ('SSID', 'BSSID', 'Network Usage', 'Country Code', 'Device Name', 'Manufacturer', 
                    'Serial Number', 'Model Name', 'Enabled', 'Carplay Network', 'Hidden', 
                    'Captive Network', 'User Portal URL', 'Add Reason', 'Bundle ID', 'Source File')

    return data_headers, data_list, ','.join(files_found)

@artifact_processor
def appleWifiKnownNetworksTimes(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        with open(file_found, 'rb') as f:
            deserialized = plistlib.load(f)

            if 'List of known networks' in deserialized:
                for known_network in deserialized['List of known networks']:
                    ssid = _decode_ssid(known_network.get('SSID_STR', b''))
                    bssid = known_network.get('BSSID', '')
                    last_updated = convert_plist_date_to_timezone_offset(known_network.get('lastUpdated', ''), timezone_offset)
                    last_auto_joined = convert_plist_date_to_timezone_offset(known_network.get('lastAutoJoined', ''), timezone_offset)
                    last_joined = convert_plist_date_to_timezone_offset(known_network.get('lastJoined', ''), timezone_offset)
                    wnpmd = convert_plist_date_to_timezone_offset(known_network.get('WiFiNetworkPasswordModificationDate', ''), timezone_offset)
                    prev_joined = convert_plist_date_to_timezone_offset(known_network.get('prevJoined', ''), timezone_offset)

                    data_list.append([ssid, bssid, last_updated, last_auto_joined, last_joined, '', '', wnpmd, '', '', '', '', prev_joined, file_found])

            if 'com.apple.wifi.known-networks.plist' in file_found:
                for network_key, known_network in deserialized.items():
                    ssid = _decode_ssid(known_network.get('SSID', b''))
                    last_updated = convert_plist_date_to_timezone_offset(known_network.get('UpdatedAt', ''), timezone_offset)
                    system_joined = convert_plist_date_to_timezone_offset(known_network.get('JoinedBySystemAt', ''), timezone_offset)
                    user_joined = convert_plist_date_to_timezone_offset(known_network.get('JoinedByUserAt', ''), timezone_offset)
                    last_discovered = convert_plist_date_to_timezone_offset(known_network.get('LastDiscoveredAt', ''), timezone_offset)
                    added_at = convert_plist_date_to_timezone_offset(known_network.get('AddedAt', ''), timezone_offset)

                    captive_profile = known_network.get('CaptiveProfile', {})
                    whitelisted_probe_date = convert_plist_date_to_timezone_offset(captive_profile.get('WhitelistedCaptiveNetworkProbeDate', ''), timezone_offset)
                    captive_web_sheet_login_date = convert_plist_date_to_timezone_offset(captive_profile.get('CaptiveWebSheetLoginDate', ''), timezone_offset)

                    os_specific = known_network.get('__OSSpecific__', {})
                    bssid = os_specific.get('BSSID', '')
                    wnpmd = convert_plist_date_to_timezone_offset(os_specific.get('WiFiNetworkPasswordModificationDate', ''), timezone_offset)
                    prev_joined = convert_plist_date_to_timezone_offset(os_specific.get('prevJoined', ''), timezone_offset)

                    data_list.append([ssid, bssid, last_updated, '', '', system_joined, user_joined, wnpmd, 
                                      last_discovered, added_at, whitelisted_probe_date, captive_web_sheet_login_date, 
                                      prev_joined, file_found])

    data_headers = ('SSID', 'BSSID', ('Last Updated', 'datetime'), ('Last Auto Joined', 'datetime'), 
                    ('Last Joined', 'datetime'), ('System Joined', 'datetime'), ('User Joined', 'datetime'),
                    ('WiFi Network Password Modification Date', 'datetime'), ('Last Discovered', 'datetime'),
                    ('Added At', 'datetime'), ('Whitelisted Captive Network Probe Date', 'datetime'),
                    ('Captive Web Sheet Login Date', 'datetime'), ('Previous Joined', 'datetime'), 'Source File')

    return data_headers, data_list, ','.join(files_found)

@artifact_processor
def appleWifiScannedPrivate(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        with open(file_found, 'rb') as f:
            deserialized = plistlib.load(f)
            if 'List of scanned networks with private mac' in deserialized:
                for scanned_network in deserialized['List of scanned networks with private mac']:
                    ssid = scanned_network.get('SSID_STR', '')
                    bssid = scanned_network.get('BSSID', '')
                    last_updated = convert_plist_date_to_timezone_offset(scanned_network.get('lastUpdated', ''), timezone_offset)
                    last_joined = convert_plist_date_to_timezone_offset(scanned_network.get('lastJoined', ''), timezone_offset)
                    added_at = convert_plist_date_to_timezone_offset(scanned_network.get('addedAt', ''), timezone_offset)
                    in_known_networks = scanned_network.get('PresentInKnownNetworks', '')
                    link_down_timestamp = convert_plist_date_to_timezone_offset(scanned_network.get('LinkDownTimestamp', ''), timezone_offset)
                    mac_generation_timestamp = convert_plist_date_to_timezone_offset(scanned_network.get('MacGenerationTimeStamp', ''), timezone_offset)
                    first_join_with_new_mac_timestamp = convert_plist_date_to_timezone_offset(scanned_network.get('FirstJoinWithNewMacTimestamp', ''), timezone_offset)

                    private_mac = scanned_network.get('PRIVATE_MAC_ADDRESS', {})
                    private_mac_in_use = _bytes_to_mac_address(private_mac.get('PRIVATE_MAC_ADDRESS_IN_USE', b''))
                    private_mac_value = _bytes_to_mac_address(private_mac.get('PRIVATE_MAC_ADDRESS_VALUE', b''))
                    private_mac_valid = private_mac.get('PRIVATE_MAC_ADDRESS_VALID', '')

                    data_list.append([last_updated, ssid, bssid, added_at, last_joined, link_down_timestamp,
                                      mac_generation_timestamp, first_join_with_new_mac_timestamp,
                                      private_mac_in_use, private_mac_value, private_mac_valid, 
                                      in_known_networks, file_found])

    data_headers = (('Last Updated', 'datetime'), 'SSID', 'BSSID', ('Added At', 'datetime'), 
                    ('Last Joined', 'datetime'), ('Link Down Timestamp', 'datetime'),
                    ('MAC Generation Timestamp', 'datetime'), ('First Join With New MAC Timestamp', 'datetime'),
                    'MAC Used For Network', 'Private MAC Computed For Network', 'MAC Valid', 
                    'In Known Networks', 'Source File')

    return data_headers, data_list, ','.join(files_found)

@artifact_processor
def appleWifiBSSList(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        with open(file_found, 'rb') as f:
            deserialized = plistlib.load(f)
            if 'com.apple.wifi.known-networks.plist' in file_found:
                for network_key, known_network in deserialized.items():
                    ssid = _decode_ssid(known_network.get('SSID', b''))
                    bss_list = known_network.get('BSSList', [])
                    for bss in bss_list:
                        channel_flags = bss.get('ChannelFlags', '')
                        channel = bss.get('Channel', '')
                        last_associated_at = convert_plist_date_to_timezone_offset(bss.get('LastAssociatedAt', ''), timezone_offset)
                        bssid = bss.get('BSSID', '')
                        location_accuracy = bss.get('LocationAccuracy', '')
                        location_timestamp = convert_plist_date_to_timezone_offset(bss.get('LocationTimestamp', ''), timezone_offset)
                        location_latitude = bss.get('LocationLatitude', '')
                        location_longitude = bss.get('LocationLongitude', '')

                        data_list.append([
                            ssid, bssid, channel_flags, channel, last_associated_at,
                            location_accuracy, location_timestamp, location_latitude, location_longitude,
                            file_found
                        ])

            if 'List of known networks' in deserialized:
                for known_network in deserialized['List of known networks']:
                    ssid = known_network.get('SSID_STR', '')
                    bss_list = known_network.get('networkKnownBSSListKey', [])
                    for bss in bss_list:
                        channel = bss.get('CHANNEL', '')
                        last_roamed = convert_plist_date_to_timezone_offset(bss.get('lastRoamed', ''), timezone_offset)
                        bssid = bss.get('BSSID', '')
                        channel_flags = bss.get('CHANNEL_FLAGS', '')

                        data_list.append([
                            ssid, bssid, channel_flags, channel, last_roamed,
                            '', '', '', '',
                            file_found
                        ])

    data_headers = (
        'SSID', 'BSSID', 'Channel Flags', 'Channel', ('Last Associated/Roamed At', 'datetime'),
        'Location Accuracy', ('Location Timestamp', 'datetime'), 'Location Latitude', 'Location Longitude',
        'Source File'
    )

    return data_headers, data_list, ','.join(files_found)
