__artifacts_v2__ = {
    "imeiImsi": {
        "name": "IMEI - IMSI",
        "description": "Lists the keys of the first com.apple.commcenter.plist found, as stored. Under PersonalWallet only the first entry's lastGoodImsi, kEntitlementsSelfRegistrationUpdateImsi and kEntitlementsSelfRegistrationUpdateImei are reported.",
        "author": "@AlexisBrignoni - @stark4n6",
        "version": "0.3",
        "creation_date": "2023-10-03",
        "last_update_date": "2025-02-04",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/wireless/Library/Preferences/com.apple.commcenter.plist'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "hash",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 20 rows",
            "dexter_ios18": "iOS 18.3.2 | 23 rows",
            "felix_ios17": "iOS 17.6.1 | 23 rows",
            "fsfull002_ios17": "iOS 17.1 | 21 rows",
            "hc_ios18_7": "iOS 18.7.8 | 18 rows",
            "iphone11_ios17": "iOS 17.3 | 21 rows",
            "iphone12_ios18": "iOS 18.7 | 18 rows",
            "iphone14plus_ios18": "iOS 18.0 | 22 rows",
            "otto_ios17": "iOS 17.5.1 | 21 rows",
            "abe_ios16": "iOS 16.5 | 20 rows",
            "felix23_ios16": "iOS 16.5 | 21 rows",
            "hickman_ios13": "iOS 13.3.1 | 22 rows",
            "hickman_ios14": "iOS 14.3 | 23 rows",
            "jess_ios15": "iOS 15.0.2 | 22 rows",
            "magnet_ios16": "iOS 16.1.1 | 21 rows",
        }
    },
    "imeiImsiPersonalWallet": {
        "name": "CommCenter - PersonalWallet Field",
        "description": "The decoded PersonalWallet field of the first selected CommCenter plist, with field presence and native value types.",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-10-06",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "One document-field row is reported for the first selected dictionary-root "
                 "com.apple.commcenter.plist, including when PersonalWallet is absent, null, empty "
                 "or not a dictionary. This is not a wallet count. The legacy IMEI - IMSI artifact "
                 "by @AlexisBrignoni and @stark4n6 and its device-info entries are unchanged; this "
                 "artifact adds no device-info entries. The compact typed JSON keeps decoded "
                 "wallet keys, all fields, order, repeated values and key presence. Integer and "
                 "UID values use decimal text, real values use parsed big-endian binary64 "
                 "hexadecimal bits, data uses base64, and dates keep decoded components without "
                 "assigning a timezone. Dictionaries use ordered typed key/value pairs. This "
                 "preserves supported plistlib-decoded values, not original plist bytes, XML "
                 "spelling, duplicate dictionary keys collapsed by decoding or binary object "
                 "identity. Original source exports retain byte evidence. Only the first input "
                 "plist is read; later matched files and legacy malformed-wallet handling remain "
                 "outside this artifact. Stored values do not establish active SIM, subscriber "
                 "or device/person ownership, current validity or meanings of unknown keys.",
        "paths": ('*/wireless/Library/Preferences/com.apple.commcenter.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "hash",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 1 row",
        },
    }
}

import base64
from datetime import datetime
import json
import plistlib
import struct
from scripts.ilapfuncs import artifact_processor, device_info, logfunc

@artifact_processor
def imeiImsi(context):
    data_list = []
    source_path = str(context.get_files_found()[0])
    
    with open(source_path, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            if key == 'PersonalWallet':
                val = (list(val.values())[0])
                lastgoodimsi = val['CarrierEntitlements'].get('lastGoodImsi','')
                data_list.append(('Last Good IMSI', lastgoodimsi))
                device_info("Cellular", "Last Good IMSI", lastgoodimsi, source_path)
                
                selfregitrationupdateimsi = val['CarrierEntitlements'].get('kEntitlementsSelfRegistrationUpdateImsi','')
                data_list.append(('Self Registration Update IMSI', selfregitrationupdateimsi))
                device_info("Cellular", "Self Registration Update IMSI", selfregitrationupdateimsi, source_path)
                
                selfregistrationupdateimei = val['CarrierEntitlements'].get('kEntitlementsSelfRegistrationUpdateImei','')
                data_list.append(('Self Registration Update IMEI', selfregistrationupdateimei))
                device_info("Cellular", "Self Registration Update IMEI", selfregistrationupdateimei, source_path)
                
            elif key == 'LastKnownICCI':
                lastknownicci = val
                data_list.append(('Last Known ICCI', lastknownicci))
                device_info("Cellular", "Last Known ICCI", lastknownicci, source_path)
                
            elif key == 'PhoneNumber':
                data_list.append(('Phone Number', val))
                device_info("Cellular", "Phone Number", val, source_path)
                
            else:
                data_list.append((key, val ))
    
    data_headers = ('Property', 'Property Value')
    return data_headers, data_list, source_path



def _wallet_value_node(value):
    """Retain supported decoded plist values using collision-safe type nodes."""
    if value is None:
        kind, encoded = 'null', None
    elif isinstance(value, bool):
        kind, encoded = 'bool', value
    elif isinstance(value, str):
        kind, encoded = 'string', value
    elif isinstance(value, int):
        kind, encoded = 'integer', str(value)
    elif isinstance(value, float):
        kind, encoded = 'real', struct.pack('>d', value).hex()
    elif isinstance(value, bytes):
        kind, encoded = 'data', base64.b64encode(value).decode('ascii')
    elif isinstance(value, datetime):
        kind, encoded = 'date', value.isoformat()
    elif isinstance(value, plistlib.UID):
        kind, encoded = 'uid', str(value.data)
    elif isinstance(value, list):
        kind, encoded = 'array', [_wallet_value_node(item) for item in value]
    elif isinstance(value, dict):
        kind = 'dictionary'
        encoded = [[_wallet_value_node(key), _wallet_value_node(item)]
                   for key, item in value.items()]
    else:
        raise TypeError(f'Unsupported wallet field value type: {type(value).__name__}')
    return {'type': kind, 'value': encoded}


def _wallet_field_json(content):
    """Distinguish missing PersonalWallet from present null or empty values."""
    envelope = {'present': 'PersonalWallet' in content}
    if 'PersonalWallet' in content:
        envelope['value'] = _wallet_value_node(content['PersonalWallet'])
    return json.dumps(envelope, ensure_ascii=True, separators=(',', ':'), allow_nan=False)


@artifact_processor
def imeiImsiPersonalWallet(context):
    source_path = str(context.get_files_found()[0])
    source_file = context.get_relative_path(source_path)
    headers = ('PersonalWallet Field (Typed JSON)',)
    with open(source_path, 'rb') as stream:
        content = plistlib.load(stream)
    if not isinstance(content, dict):
        logfunc(f'CommCenter PersonalWallet: {source_file[:240]!r}: '
                'root is not a dictionary; field presence was not evaluated')
        return headers, [], source_file
    return headers, [(_wallet_field_json(content),)], source_file
