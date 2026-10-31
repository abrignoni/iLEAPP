__artifacts_v2__ = {
    "appleWifiKnownNetworks": {
        "name": "WiFi Known Networks Info",
        "description": "Parses WiFi connection data for known networks",
        "author": "@AlexisBrignoni, @Hexordia",
        "creation_date": "2024-10-21",
        "last_update_date": "2026-10-30",
        "requirements": "none",
        "category": "WiFi Connections",
        "notes": "Parses multiple plist files with varying structures. Some fields may be blank. "
                 "Security Type is the SupportedSecurityTypes value of a com.apple.wifi.known-networks.plist entry, written as text; on every tested image the stored value is a string. "
                 "Also reads these plists inside a sysdiagnose archive (sysdiagnose_*.tar.gz or *_sysdiagnose.tar.gz), matched by file name anywhere in the archive; Source File then names the archive and the member. BSSID is shown with every octet as two hexadecimal digits (an octet can be stored without its leading zero), in the case stored.",
        "paths": ('*/com.apple.wifi.plist', 
                  '*/com.apple.wifi-networks.plist.backup', 
                  '*/com.apple.wifi.known-networks.plist',
                  '*/sysdiagnose_*.tar.gz', '*/*_sysdiagnose.tar.gz'),
        "output_types": ["html","lava","tsv"],
        "artifact_icon": "wifi",
        "sample_data": {
            "hickman_ios13_sysdiag": "iOS 13.3.1 | 1 row",
            "hickman_ios14_sysdiag": "iOS 14.3 | 1 row",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 0 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 8 rows",
            "dexter_ios18": "iOS 18.3.2 | 8 rows",
            "felix_ios17": "iOS 17.6.1 | 11 rows",
            "fsfull002_ios17": "iOS 17.1 | 5 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 17 rows",
            "iphone12_ios18": "iOS 18.7 | 2 rows",
            "iphone14plus_ios18": "iOS 18.0 | 3 rows",
            "otto_ios17": "iOS 17.5.1 | 33 rows",
            "abe_ios16": "iOS 16.5 | 55 rows",
            "felix23_ios16": "iOS 16.5 | 3 rows",
            "hickman_ios13": "iOS 13.3.1 | 1 row",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "jess_ios15": "iOS 15.0.2 | 6 rows",
            "magnet_ios16": "iOS 16.1.1 | 5 rows",
        }
    },
    "appleWifiKnownNetworksTimes": {
        "name": "WiFi Known Networks Times",
        "description": "Parses time-related data for known WiFi networks",
        "author": "@AlexisBrignoni, @Hexordia",
        "creation_date": "2024-10-21",
        "last_update_date": "2026-10-30",
        "requirements": "none",
        "category": "WiFi Connections",
        "notes": "Parses multiple plist files with varying structures. Some fields may be blank. "
                 "System Joined and User Joined are the stored JoinedBySystemAt and JoinedByUserAt "
                 "values; what sets each is not established here. "
                 "Also reads these plists inside a sysdiagnose archive (sysdiagnose_*.tar.gz or *_sysdiagnose.tar.gz), matched by file name anywhere in the archive; Source File then names the archive and the member. BSSID is shown with every octet as two hexadecimal digits (an octet can be stored without its leading zero), in the case stored.",
        "paths": ('*/com.apple.wifi.plist', 
                  '*/com.apple.wifi-networks.plist.backup', 
                  '*/com.apple.wifi.known-networks.plist',
                  '*/sysdiagnose_*.tar.gz', '*/*_sysdiagnose.tar.gz'),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "hickman_ios13_sysdiag": "iOS 13.3.1 | 1 row",
            "hickman_ios14_sysdiag": "iOS 14.3 | 1 row",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 0 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 8 rows",
            "dexter_ios18": "iOS 18.3.2 | 8 rows",
            "felix_ios17": "iOS 17.6.1 | 11 rows",
            "fsfull002_ios17": "iOS 17.1 | 5 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 17 rows",
            "iphone12_ios18": "iOS 18.7 | 2 rows",
            "iphone14plus_ios18": "iOS 18.0 | 3 rows",
            "otto_ios17": "iOS 17.5.1 | 33 rows",
            "abe_ios16": "iOS 16.5 | 55 rows",
            "felix23_ios16": "iOS 16.5 | 3 rows",
            "hickman_ios13": "iOS 13.3.1 | 1 row",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "jess_ios15": "iOS 15.0.2 | 6 rows",
            "magnet_ios16": "iOS 16.1.1 | 5 rows",
        }
    },
    "appleWifiScannedPrivate": {
        "name": "WiFi Scanned Networks (Private)",
        "description": "Entries of the 'List of scanned networks with private mac' list in "
                       "com.apple.wifi-private-mac-networks.plist, with their stored dates and "
                       "private MAC address values",
        "author": "@AlexisBrignoni, @Hexordia",
        "creation_date": "2023-05-24",
        "last_update_date": "2026-10-30",
        "requirements": "none",
        "category": "WiFi Connections",
        "notes": "The MAC Used For Network column holds the PRIVATE_MAC_ADDRESS_IN_USE value and "
                 "the Private MAC Computed For Network column holds the PRIVATE_MAC_ADDRESS_VALUE "
                 "value, both stored under PRIVATE_MAC_ADDRESS. The two header names are this "
                 "module's and are not sourced here. "
                 "Also reads these plists inside a sysdiagnose archive (sysdiagnose_*.tar.gz or *_sysdiagnose.tar.gz), matched by file name anywhere in the archive; Source File then names the archive and the member. BSSID is shown with every octet as two hexadecimal digits (an octet can be stored without its leading zero), in the case stored.",
        "paths": ('*/com.apple.wifi-private-mac-networks.plist',
                  '*/sysdiagnose_*.tar.gz', '*/*_sysdiagnose.tar.gz'),
        "output_types": "standard",
        "artifact_icon": "eye-off",
        "sample_data": {
            "hickman_ios13_sysdiag": "iOS 13.3.1 | 0 rows",
            "hickman_ios14_sysdiag": "iOS 14.3 | 1 row",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 13 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 2 rows",
            "dexter_ios18": "iOS 18.3.2 | 9 rows",
            "felix_ios17": "iOS 17.6.1 | 11 rows",
            "fsfull002_ios17": "iOS 17.1 | 2 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 17 rows",
            "iphone12_ios18": "iOS 18.7 | 2 rows",
            "iphone14plus_ios18": "iOS 18.0 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 35 rows",
            "abe_ios16": "iOS 16.5 | 47 rows",
            "felix23_ios16": "iOS 16.5 | 3 rows",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 5 rows",
        }
    },
    "appleWifiBSSList": {
        "name": "WiFi BSS List",
        "description": "Parses BSS (Basic Service Set) information for known WiFi networks",
        "author": "@JamesHabben, @Hexordia",
        "creation_date": "2023-05-25",
        "last_update_date": "2026-10-30",
        "requirements": "none",
        "category": "WiFi Connections",
        "notes": "Extracts BSS entries from the com.apple.wifi.known-networks.plist file, and from the 'List of known networks' entries of a com.apple.wifi.plist read inside a sysdiagnose archive. "
                 "Latitude, Longitude, Location Accuracy and Location Timestamp are the "
                 "LocationLatitude, LocationLongitude, LocationAccuracy and LocationTimestamp "
                 "values stored in each BSS entry; what they locate and how they were obtained is "
                 "not established here. "
                 "Also reads these plists inside a sysdiagnose archive (sysdiagnose_*.tar.gz or *_sysdiagnose.tar.gz), matched by file name anywhere in the archive; Source File then names the archive and the member. BSSID is shown with every octet as two hexadecimal digits (an octet can be stored without its leading zero), in the case stored.",
        "paths": ('*/com.apple.wifi.known-networks.plist',
                  '*/sysdiagnose_*.tar.gz', '*/*_sysdiagnose.tar.gz'),
        "output_types": "all",
        "artifact_icon": "wifi",
        "sample_data": {
            "hickman_ios13_sysdiag": "iOS 13.3.1 | 7 rows",
            "hickman_ios14_sysdiag": "iOS 14.3 | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 0 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 43 rows",
            "felix_ios17": "iOS 17.6.1 | 34 rows",
            "fsfull002_ios17": "iOS 17.1 | 3 rows",
            "hc_ios18_7": "iOS 18.7.8 | 5 rows",
            "iphone11_ios17": "iOS 17.3 | 100 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 6 rows",
            "otto_ios17": "iOS 17.5.1 | 194 rows",
            "abe_ios16": "iOS 16.5 | 271 rows",
            "felix23_ios16": "iOS 16.5 | 10 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 44 rows",
            "magnet_ios16": "iOS 16.1.1 | 37 rows",
        }
    }
}

import re
import plistlib
from xml.parsers.expat import ExpatError

from scripts.ilapfuncs import device_info, artifact_processor, convert_plist_date_to_utc, get_sysdiagnose_files, logfunc
from datetime import datetime as _dt

_READ_ERRORS = (OSError, EOFError, plistlib.InvalidFileException, ExpatError, ValueError)

def _safe_plist_date(value):
    """Convert plist <date> objects to UTC; pass strings/None through unchanged."""
    return convert_plist_date_to_utc(value) if isinstance(value, _dt) else value

def _bytes_to_mac_address(encoded_bytes):
    return ':'.join(f"{byte:02x}" for byte in encoded_bytes[:6])

def _decode_ssid(ssid_bytes):
    if isinstance(ssid_bytes, bytes):
        try:
            return ssid_bytes.decode('utf-8')
        except UnicodeDecodeError:
            return ssid_bytes.hex()
    return str(ssid_bytes)

def _format_bssid(bssid_str):
    """Each octet as two hexadecimal digits (a plist can store one without its leading zero), case unchanged."""
    if not bssid_str or not isinstance(bssid_str, str):
        return bssid_str
    return ':'.join(octet.zfill(2) for octet in bssid_str.split(':'))

def _get_wifi_plists(context, target_regex_pattern):
    """Yield (plist_dict, relative_path, source_path) for WiFi plists, including embedded sysdiagnose archives."""
    target = re.compile(target_regex_pattern)
    for file_obj, source_path in get_sysdiagnose_files(context.get_files_found(), target, text_mode=False):
        rel = context.get_relative_path(source_path)
        try:
            deserialized = plistlib.loads(file_obj.read())
        except _READ_ERRORS as ex:
            logfunc(f'Failed to read {rel}: {ex}')
            continue
        
        if isinstance(deserialized, dict):
            yield deserialized, rel, source_path

@artifact_processor
def appleWifiKnownNetworks(context):
    data_list = []
    source_files = set()
    target_re = r'com\.apple\.wifi(\.known-networks|\-networks)?\.plist(\.backup)?$'
    
    for deserialized, rel, source_path in _get_wifi_plists(context, target_re):
        source_files.add(source_path)
        
        if 'KeepWiFiPoweredAirplaneMode' in deserialized:
            val = (deserialized['KeepWiFiPoweredAirplaneMode'])
            device_info('WiFi', 'Keep Wifi Powered Airplane Mode', val, rel)

        if 'List of known networks' in deserialized:
            for known_network in deserialized['List of known networks']:
                ssid = _decode_ssid(known_network.get('SSID_STR', b''))
                bssid = _format_bssid(known_network.get('BSSID', ''))
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
                                    user_portal_url, '', '', '', rel])

        if 'com.apple.wifi.known-networks.plist' in rel:
            for _, known_network in deserialized.items():
                ssid = _decode_ssid(known_network.get('SSID', b''))
                add_reason = known_network.get('AddReason', '')
                bundle = known_network.get('BundleID', '')
                hidden = known_network.get('Hidden', '')
                security_type = str(known_network.get('SupportedSecurityTypes', ''))

                os_specific = known_network.get('__OSSpecific__', {})
                bssid = _format_bssid(os_specific.get('BSSID', ''))
                net_usage = os_specific.get('networkUsage', '')
                carplay = os_specific.get('CarPlayNetwork', known_network.get('CARPLAY_NETWORK', ''))

                captive_profile = known_network.get('CaptiveProfile', {})
                captive_network = captive_profile.get('CaptiveNetwork', '')
                user_portal_url = captive_profile.get('UserPortalURL', '')

                data_list.append([ssid, bssid, net_usage, '', '', '', '', '', '', carplay, hidden, 
                                    captive_network, user_portal_url, add_reason, bundle, security_type, rel])

    data_headers = ('SSID', 'BSSID', 'Network Usage', 'Country Code', 'Device Name', 'Manufacturer', 
                    'Serial Number', 'Model Name', 'Enabled', 'Carplay Network', 'Hidden', 
                    'Captive Network', 'User Portal URL', 'Add Reason', 'Bundle ID', 'Security Type', 'Source File')

    return data_headers, data_list, '\n'.join(sorted(source_files))

@artifact_processor
def appleWifiKnownNetworksTimes(context):
    data_list = []
    source_files = set()
    target_re = r'com\.apple\.wifi(\.known-networks|\-networks)?\.plist(\.backup)?$'
    
    for deserialized, rel, source_path in _get_wifi_plists(context, target_re):
        source_files.add(source_path)
        
        if 'List of known networks' in deserialized:
            for known_network in deserialized['List of known networks']:
                ssid = _decode_ssid(known_network.get('SSID_STR', b''))
                bssid = _format_bssid(known_network.get('BSSID', ''))
                last_updated = _safe_plist_date(known_network.get('lastUpdated', ''))
                last_auto_joined = _safe_plist_date(known_network.get('lastAutoJoined', ''))
                last_joined = _safe_plist_date(known_network.get('lastJoined', ''))
                wnpmd = _safe_plist_date(known_network.get('WiFiNetworkPasswordModificationDate', ''))
                prev_joined = _safe_plist_date(known_network.get('prevJoined', ''))

                data_list.append([last_updated, ssid, bssid, last_auto_joined, last_joined, '', '', wnpmd, '', '', '', '', prev_joined, rel])

        if 'com.apple.wifi.known-networks.plist' in rel:
            for _, known_network in deserialized.items():
                ssid = _decode_ssid(known_network.get('SSID', b''))
                last_updated = _safe_plist_date(known_network.get('UpdatedAt', ''))
                system_joined = _safe_plist_date(known_network.get('JoinedBySystemAt', ''))
                user_joined = _safe_plist_date(known_network.get('JoinedByUserAt', ''))
                last_discovered = _safe_plist_date(known_network.get('LastDiscoveredAt', ''))
                added_at = _safe_plist_date(known_network.get('AddedAt', ''))

                captive_profile = known_network.get('CaptiveProfile', {})
                whitelisted_probe_date = _safe_plist_date(captive_profile.get('WhitelistedCaptiveNetworkProbeDate', ''))
                captive_web_sheet_login_date = _safe_plist_date(captive_profile.get('CaptiveWebSheetLoginDate', ''))

                os_specific = known_network.get('__OSSpecific__', {})
                bssid = _format_bssid(os_specific.get('BSSID', ''))
                wnpmd = _safe_plist_date(os_specific.get('WiFiNetworkPasswordModificationDate', ''))
                prev_joined = _safe_plist_date(os_specific.get('prevJoined', ''))

                data_list.append([last_updated, ssid, bssid, '', '', system_joined, user_joined, wnpmd, 
                                    last_discovered, added_at, whitelisted_probe_date, captive_web_sheet_login_date, 
                                    prev_joined, rel])

    data_headers = (('Last Updated', 'datetime'), 'SSID', 'BSSID', ('Last Auto Joined', 'datetime'), 
                    ('Last Joined', 'datetime'), ('System Joined', 'datetime'), ('User Joined', 'datetime'),
                    ('WiFi Network Password Modification Date', 'datetime'), ('Last Discovered', 'datetime'),
                    ('Added At', 'datetime'), ('Whitelisted Captive Network Probe Date', 'datetime'),
                    ('Captive Web Sheet Login Date', 'datetime'), ('Previous Joined', 'datetime'), 'Source File')

    return data_headers, data_list, '\n'.join(sorted(source_files))

@artifact_processor
def appleWifiScannedPrivate(context):
    data_list = []
    source_files = set()
    target_re = r'com\.apple\.wifi-private-mac-networks\.plist$'
    
    for deserialized, rel, source_path in _get_wifi_plists(context, target_re):
        source_files.add(source_path)
        
        if 'List of scanned networks with private mac' in deserialized:
            for scanned_network in deserialized['List of scanned networks with private mac']:
                ssid = scanned_network.get('SSID_STR', '')
                bssid = _format_bssid(scanned_network.get('BSSID', ''))
                last_updated = _safe_plist_date(scanned_network.get('lastUpdated', ''))
                last_joined = _safe_plist_date(scanned_network.get('lastJoined', ''))
                added_at = _safe_plist_date(scanned_network.get('addedAt', ''))
                in_known_networks = scanned_network.get('PresentInKnownNetworks', '')
                link_down_timestamp = _safe_plist_date(scanned_network.get('LinkDownTimestamp', ''))
                mac_generation_timestamp = _safe_plist_date(scanned_network.get('MacGenerationTimeStamp', ''))
                first_join_with_new_mac_timestamp = _safe_plist_date(scanned_network.get('FirstJoinWithNewMacTimestamp', ''))

                private_mac = scanned_network.get('PRIVATE_MAC_ADDRESS', {})
                private_mac_in_use = _bytes_to_mac_address(private_mac.get('PRIVATE_MAC_ADDRESS_IN_USE', b''))
                private_mac_value = _bytes_to_mac_address(private_mac.get('PRIVATE_MAC_ADDRESS_VALUE', b''))
                private_mac_valid = private_mac.get('PRIVATE_MAC_ADDRESS_VALID', '')

                data_list.append([last_updated, added_at, last_joined, link_down_timestamp,
                                    mac_generation_timestamp, first_join_with_new_mac_timestamp,
                                    ssid, bssid, private_mac_in_use, private_mac_value, private_mac_valid, 
                                    in_known_networks, rel])

    data_headers = (('Last Updated', 'datetime'), ('Added At', 'datetime'), 
                    ('Last Joined', 'datetime'), ('Link Down Timestamp', 'datetime'),
                    ('MAC Generation Timestamp', 'datetime'), ('First Join With New MAC Timestamp', 'datetime'),
                    'SSID', 'BSSID', 'MAC Used For Network', 'Private MAC Computed For Network', 'MAC Valid', 
                    'In Known Networks', 'Source File')

    return data_headers, data_list, '\n'.join(sorted(source_files))

@artifact_processor
def appleWifiBSSList(context):
    data_list = []
    source_files = set()
    target_re = r'com\.apple\.wifi(\.known-networks)?\.plist$'
    
    for deserialized, rel, source_path in _get_wifi_plists(context, target_re):
        source_files.add(source_path)
        
        if 'com.apple.wifi.known-networks.plist' in rel:
            for _, known_network in deserialized.items():
                ssid = _decode_ssid(known_network.get('SSID', b''))
                bss_list = known_network.get('BSSList', [])
                for bss in bss_list:
                    channel_flags = bss.get('ChannelFlags', '')
                    channel = bss.get('Channel', '')
                    last_associated_at = _safe_plist_date(bss.get('LastAssociatedAt', ''))
                    bssid = _format_bssid(bss.get('BSSID', ''))
                    location_accuracy = bss.get('LocationAccuracy', '')
                    location_timestamp = _safe_plist_date(bss.get('LocationTimestamp', ''))
                    location_latitude = bss.get('LocationLatitude', '')
                    location_longitude = bss.get('LocationLongitude', '')

                    data_list.append([
                        ssid, bssid, channel_flags, channel, last_associated_at,
                        location_accuracy, location_timestamp, location_latitude, location_longitude,
                        rel
                    ])

        if 'List of known networks' in deserialized:
            for known_network in deserialized['List of known networks']:
                ssid = known_network.get('SSID_STR', '')
                bss_list = known_network.get('networkKnownBSSListKey', [])
                for bss in bss_list:
                    channel = bss.get('CHANNEL', '')
                    last_roamed = _safe_plist_date(bss.get('lastRoamed', ''))
                    bssid = _format_bssid(bss.get('BSSID', ''))
                    channel_flags = bss.get('CHANNEL_FLAGS', '')

                    data_list.append([
                        ssid, bssid, channel_flags, channel, last_roamed,
                        '', '', '', '',
                        rel
                    ])

    data_headers = (
        'SSID', 'BSSID', 'Channel Flags', 'Channel', ('Last Associated/Roamed At', 'datetime'),
        'Location Accuracy', ('Location Timestamp', 'datetime'), 'Latitude', 'Longitude',
        'Source File'
    )

    return data_headers, data_list, '\n'.join(sorted(source_files))