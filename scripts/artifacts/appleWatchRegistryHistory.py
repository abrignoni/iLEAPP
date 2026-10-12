""" Apple Watch registry history: DeviceRegistry.state/history.plist

history.plist is an NSKeyedArchiver file whose NRDeviceCollectionHistory object holds one
data value in protobuf wire format. No schema for it is published. The field numbers below
were read from the files on the sample_data images and are the only ones this module
follows; anything else is skipped. A file that does not have this layout is
logged and gives no rows.

    history          1 varint, 2 entry (repeated), 3 not read
    entry            1 varint number, 2 double date, 3 device
    device           1 bytes(16) device id, 2 change
    change           1 varint type, 2 properties
    properties       1 name (repeated), 2 value (repeated). All names come before all
                     values. This module pairs them by position; the pairing is not sourced.
    value            1 varint (0 or 1 on the sample files, not read), 2 holder
    holder           1 typed
    typed            1 text | 2 number | 3 bytes(16) | 4 bytes | 5 size | 7 array,
                     9 varint beside 3 (reference into historySecureProperties.plist),
                     10 varint beside 2 (read here as a date mark; not sourced),
                     12 varint beside 4 (not read)
    number           1 varint, 2 float, 3 double, 5 varint,
                     7 varint (always 0 on the sample files, not read)
    size             1 float, 2 float
"""
__artifacts_v2__ = {
    "appleWatchRegistryDevices": {
        "name": "Apple Watch Registry Devices",
        "description": "One row per change type 0 entry in DeviceRegistry.state/history.plist, "
                       "with the device name, model, system version, identifiers and dates "
                       "stored in it.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-10",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "Apple Watch",
        "notes": "Each row is one entry of change type 0 in history.plist. On the sample_data "
                 "images that entry held 81 to 95 properties of one device. The file holds a "
                 "protobuf value. This module follows no published schema; the field layout it "
                 "reads is written at the top of the module and was taken from the 4 sample_data "
                 "images that have the file. A file in another layout is logged and gives no "
                 "rows. Entry Date is the entry's date, and Paired Date and Last Active Date are "
                 "the pairedDate and lastActiveDate properties. Each is a number read as seconds "
                 "since 2001-01-01 UTC and shown to the second. The epoch is not sourced: read "
                 "this way the 12 dates fall between 2020 and 2024. Paired Date falls on the day "
                 "of Entry Date on 3 images and about a year before it on iphone11_ios17. Name, "
                 "Product Type, Model Number, Hardware Model, System Name, System Version, "
                 "System Build Version, Is Paired and Is Active are the properties name, "
                 "productType, modelNumber, hwModelStr, systemName, systemVersion, "
                 "systemBuildVersion, isPaired and isActive, as stored. Serial Number, UDID, "
                 "IMEI, Bluetooth MAC Address and WiFi MAC Address are stored in history.plist "
                 "as 16-byte references and are shown as the value historySecureProperties.plist "
                 "holds under that reference; all 107 references on the 4 images were found "
                 "there. Device ID and Pairing ID are 16-byte values shown in UUID form. On all "
                 "4 images Device ID was equal to the name of the one folder under "
                 "mobile/Library/DeviceRegistry. On all 4 images Product Type began with Watch "
                 "and System Name was Watch OS. The row is the device as that entry records it: "
                 "later entries that change one property are in Apple Watch Registry History and "
                 "are not applied here. Each of the 4 files held 4 entries, one of them of type "
                 "0, and the entries were numbered from 17, 18, 27 and 39, so entries with lower "
                 "numbers are not in the file. The file was on 4 of the 23 sample_data images "
                 "(cookbook_ios1751, hickman_ios13, hickman_ios14, iphone11_ios17), 1 row each. "
                 "The other 19 have no history.plist under mobile/Library/DeviceRegistry.state. "
                 "Issue #1876 lists the DeviceRegistry folder; this file sits beside it and was "
                 "not named there.",
        "paths": ('*/mobile/Library/DeviceRegistry.state/history.plist',
                  '*/mobile/Library/DeviceRegistry.state/historySecureProperties.plist'),
        "output_types": "standard",
        "artifact_icon": "watch",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 1 rows",
            "hickman_ios14": "iOS 14.3 | 1 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 1 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 1 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
    "appleWatchRegistryHistory": {
        "name": "Apple Watch Registry History",
        "description": "One row per property in each entry of DeviceRegistry.state/history.plist, "
                       "with the entry date, device identifier, property name and value.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-10",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "Apple Watch",
        "notes": "Each row is one property of one entry in history.plist. The file holds a "
                 "protobuf value. This module follows no published schema; the field layout it "
                 "reads is written at the top of the module and was taken from the 4 sample_data "
                 "images that have the file. A file in another layout is logged and gives no "
                 "rows. Entry Date is the entry's date, a number read as seconds since "
                 "2001-01-01 UTC and shown to the second; the epoch is not sourced, and read "
                 "this way the dates fall between 2020 and 2024. Entry Number, Device ID and "
                 "Change Type are the entry's number, its 16-byte device identifier in UUID "
                 "form, and its change type as stored. Each file named one Device ID, equal to "
                 "the name of the one folder under mobile/Library/DeviceRegistry on that image. "
                 "On these images an entry of type 0 held 81 to 95 properties and an entry of "
                 "type 1 held one; what the types mean is not established. Each of the 4 files "
                 "held 4 entries, one of type 0 and three of type 1. Property is the stored "
                 "property name. Value Kind says how the value is stored: text, number, date "
                 "number, identifier (16 bytes shown in UUID form), secure property (a 16-byte "
                 "reference shown as the value historySecureProperties.plist holds under it; "
                 "when that value is a dictionary, set or data object it is shown as joined text "
                 "or hex, which happened on 24 of the 107 references), secure property not "
                 "found, size, array (items joined by commas; an item this module does not "
                 "decode is shown as <field N>, which happened on Dmin on all 4 images), or "
                 "field N bytes for a kind this module does not decode, where Value is the byte "
                 "count. On the 375 rows from the 4 images the kinds were number 147, secure "
                 "property 107, text 81, field 4 bytes 12, array 8, date number 8, identifier 8 "
                 "and size 4; no reference was missing. A date number is a number whose value "
                 "carries a field this module reads as a date mark; the mark is not sourced. "
                 "Value shows the number as stored and Value As Date reads it as seconds since "
                 "2001-01-01 UTC. It was seen on lastActiveDate and pairedDate. A whole number "
                 "of 2 to the 63rd power or more is shown as the negative it encodes in 64 bits, "
                 "which occurred on _RSSI only. The 12 type 1 entries held one property each: "
                 "capabilities (4), minPairingCompatibilityVersion (4), pairingSessionIdentifier "
                 "(2), migrationKeyRevision (1) and totalStorage (1). The third top-level field "
                 "of the history, one per file, is not read. The file was on 4 of the 23 "
                 "sample_data images (cookbook_ios1751 with 97 rows, hickman_ios13 84, "
                 "hickman_ios14 96, iphone11_ios17 98). The other 19 have no history.plist under "
                 "mobile/Library/DeviceRegistry.state. Issue #1876 lists the DeviceRegistry "
                 "folder; this file sits beside it and was not named there.",
        "paths": ('*/mobile/Library/DeviceRegistry.state/history.plist',
                  '*/mobile/Library/DeviceRegistry.state/historySecureProperties.plist'),
        "output_types": "standard",
        "artifact_icon": "watch",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 84 rows",
            "hickman_ios14": "iOS 14.3 | 96 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 98 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 97 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
}

import plistlib
import struct
import uuid

from scripts.ilapfuncs import (artifact_processor, convert_cocoa_core_data_ts_to_utc,
                               get_file_path, logfunc)

_VARINT, _FIXED64, _BYTES, _FIXED32 = 0, 1, 2, 5
# Properties shown in their own column of Apple Watch Registry Devices, in column order.
_DEVICE_COLUMNS = ('name', 'productType', 'modelNumber', 'hwModelStr', 'systemName',
                   'systemVersion', 'systemBuildVersion', 'serialNumber', 'UDID', 'IMEI',
                   'bluetoothMACAddress', 'WIFIMACAddress', 'isPaired', 'isActive', 'pairingID')


class _Layout(ValueError):
    """ The bytes are not in the layout this module reads. """


def _varint(data, pos):
    value = shift = 0
    while True:
        if pos >= len(data) or shift > 63:
            raise _Layout('varint')
        byte = data[pos]
        pos += 1
        value |= (byte & 0x7f) << shift
        shift += 7
        if not byte & 0x80:
            return value, pos


def _fields(data):
    """ Every field of one message as (number, wire type, value); bytes for sized types. """
    pos = 0
    out = []
    while pos < len(data):
        key, pos = _varint(data, pos)
        number, wire = key >> 3, key & 7
        if wire == _VARINT:
            value, pos = _varint(data, pos)
        elif wire in (_FIXED64, _FIXED32):
            size = 8 if wire == _FIXED64 else 4
            value, pos = data[pos:pos + size], pos + size
        elif wire == _BYTES:
            size, pos = _varint(data, pos)
            value, pos = data[pos:pos + size], pos + size
        else:
            raise _Layout(f'wire type {wire}')
        if number == 0 or pos > len(data):
            raise _Layout('field')
        out.append((number, wire, value))
    return out


def _one(fields, number, wire):
    """ The single field with this number and wire type, or None. """
    found = [value for num, typ, value in fields if num == number and typ == wire]
    return found[0] if len(found) == 1 else None


def _number(data):
    """ A number message as (value, is_double). A varint of 2**63 or more is shown negative. """
    for number, wire, value in _fields(data):
        if number in (1, 5) and wire == _VARINT:
            return (value - (1 << 64) if value >= 1 << 63 else value), False
        if number == 2 and wire == _FIXED32:
            return struct.unpack('<f', value)[0], False
        if number == 3 and wire == _FIXED64:
            return struct.unpack('<d', value)[0], True
    raise _Layout('number')


def _array(data):
    items = []
    for number, wire, value in _fields(data):
        if number == 1 and wire == _BYTES:
            items.append(value.decode('utf-8', errors='replace'))
        elif number == 2 and wire == _BYTES:
            items.append(str(_number(value)[0]))
        else:
            items.append(f'<field {number}>')
    return ', '.join(items)


def _typed(data, secure):
    """ One typed value as (text, kind, date). date is the Cocoa number of a marked date. """
    fields = _fields(data)
    number, wire, value = fields[0]
    if wire != _BYTES:
        raise _Layout('typed')
    if number == 1:
        return value.decode('utf-8', errors='replace'), 'text', None
    if number == 2:
        shown, is_double = _number(value)
        is_date = is_double and _one(fields, 10, _VARINT) is not None
        return str(shown), 'date number' if is_date else 'number', shown if is_date else None
    if number == 3 and len(value) == 16:
        identifier = str(uuid.UUID(bytes=bytes(value))).upper()
        if _one(fields, 9, _VARINT) is None:
            return identifier, 'identifier', None
        if identifier in secure:
            return secure[identifier], 'secure property', None
        return f'reference {identifier} not found in historySecureProperties.plist', \
            'secure property not found', None
    if number == 5:
        return ' x '.join(str(struct.unpack('<f', part)[0]) for num, typ, part in _fields(value)
                          if typ == _FIXED32), 'size', None
    if number == 7:
        return _array(value), 'array', None
    return f'{len(value)} bytes', f'field {number} bytes', None


def _entries(data, secure):
    """ Each entry as (number, date number, device id, change type, [(name, text, kind, date)]). """
    out = []
    for entry in (value for num, typ, value in _fields(data) if num == 2 and typ == _BYTES):
        fields = _fields(entry)
        date = _one(fields, 2, _FIXED64)
        device = _fields(_one(fields, 3, _BYTES) or b'')
        device_id = _one(device, 1, _BYTES)
        change = _fields(_one(device, 2, _BYTES) or b'')
        properties = _fields(_one(change, 2, _BYTES) or b'')
        names = [value.decode('utf-8', errors='replace')
                 for num, typ, value in properties if num == 1 and typ == _BYTES]
        values = [value for num, typ, value in properties if num == 2 and typ == _BYTES]
        if date is None or device_id is None or len(device_id) != 16 or len(names) != len(values):
            raise _Layout('entry')
        rows = []
        for name, value in zip(names, values):
            holder = _fields(_one(_fields(value), 2, _BYTES) or b'')
            typed = _one(holder, 1, _BYTES)
            if typed is None:
                raise _Layout('value')
            rows.append((name,) + _typed(typed, secure))
        out.append((_one(fields, 1, _VARINT), struct.unpack('<d', date)[0],
                    str(uuid.UUID(bytes=bytes(device_id))).upper(),
                    _one(change, 1, _VARINT), rows))
    return out


def _archive(path):
    """ The object list and root object of an NSKeyedArchiver file, or ([], {}). """
    try:
        with open(path, 'rb') as file:
            plist = plistlib.load(file)
        objects = plist['$objects']
        return objects, objects[plist['$top']['root'].data]
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError,
            plistlib.InvalidFileException) as error:
        logfunc(f'{path} did not read as an NSKeyedArchiver file: {error}')
        return [], {}


def _plain(objects, value, depth=0):
    """ An archived value as text. Collections are joined; other classes are named. """
    if isinstance(value, plistlib.UID):
        value = objects[value.data]
    if isinstance(value, bytes):
        return value.hex()
    if not isinstance(value, dict):
        return '' if value == '$null' else str(value)
    if depth > 4:
        return '...'
    items = [_plain(objects, item, depth + 1) for item in value.get('NS.objects', [])]
    if 'NS.keys' in value:
        keys = [_plain(objects, key, depth + 1) for key in value['NS.keys']]
        return '; '.join(f'{key}={item}' for key, item in zip(keys, items))
    if 'NS.objects' in value:
        return ', '.join(items)
    return f"<{objects[value['$class'].data].get('$classname', 'object')}>"


def _secure_properties(path):
    """ historySecureProperties.plist as {identifier: text}. {} when absent or unreadable. """
    if not path:
        return {}
    objects, root = _archive(path)
    secure = {}
    try:
        properties = objects[root['properties'].data]
        for key, value in zip(properties['NS.keys'], properties['NS.objects']):
            raw = objects[objects[key.data]['UUID'].data]['NS.uuidbytes']
            secure[str(uuid.UUID(bytes=bytes(raw))).upper()] = _plain(objects, value)
    except (KeyError, TypeError, IndexError, AttributeError, ValueError) as error:
        logfunc(f'{path}: secure properties were not read: {error}')
    return secure


def _history(context):
    """ (source path, entries). Entries are [] when the file is absent or not in the layout. """
    files = context.get_files_found()
    source_path = get_file_path(files, 'history.plist')
    if not source_path:
        return '', []
    secure = _secure_properties(get_file_path(files, 'historySecureProperties.plist'))
    objects, root = _archive(source_path)
    try:
        data = objects[root['data'].data]['NS.data']
        return source_path, _entries(bytes(data), secure)
    except (KeyError, TypeError, IndexError, AttributeError) as error:
        logfunc(f'{source_path} holds no history data: {error}')
    except (_Layout, struct.error) as error:
        logfunc(f'{source_path}: history is not in the layout this module reads ({error})')
    return source_path, []


def _date(number):
    return convert_cocoa_core_data_ts_to_utc(number) if number else ''


@artifact_processor
def appleWatchRegistryDevices(context):
    """ See artifact description """
    data_headers = (('Paired Date', 'datetime'), ('Last Active Date', 'datetime'),
                    ('Entry Date', 'datetime'), 'Entry Number', 'Device ID', 'Name',
                    'Product Type', 'Model Number', 'Hardware Model', 'System Name',
                    'System Version', 'System Build Version', 'Serial Number', 'UDID', 'IMEI',
                    'Bluetooth MAC Address', 'WiFi MAC Address', 'Is Paired', 'Is Active',
                    'Pairing ID')
    data_list = []
    source_path, entries = _history(context)
    for number, date, device_id, change_type, rows in entries:
        if change_type != 0:
            continue
        text = {name: shown for name, shown, _kind, _date_number in rows}
        dates = {name: date_number for name, _shown, _kind, date_number in rows}
        data_list.append((_date(dates.get('pairedDate')), _date(dates.get('lastActiveDate')),
                          _date(date), number, device_id)
                         + tuple(text.get(name, '') for name in _DEVICE_COLUMNS))
    return data_headers, data_list, source_path


@artifact_processor
def appleWatchRegistryHistory(context):
    """ See artifact description """
    data_headers = (('Entry Date', 'datetime'), ('Value As Date', 'datetime'), 'Entry Number',
                    'Device ID', 'Change Type', 'Property', 'Value', 'Value Kind')
    data_list = []
    source_path, entries = _history(context)
    for number, date, device_id, change_type, rows in entries:
        for name, shown, kind, date_number in rows:
            data_list.append((_date(date), _date(date_number), number, device_id, change_type,
                              name, shown, kind))
    return data_headers, data_list, source_path
