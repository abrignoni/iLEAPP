__artifacts_v2__ = {
    "get_biomeUseractmeta": {
        "name": "Biome - User Activity Metadata",
        "description": "Parses user activity metadata entries from biomes",
        "author": "@JohnHyla, @mattiaepi (Mattia Epifani), @AlexisBrignoni, Claude",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-11-24",
        "requirements": "none",
        "category": "Biome",
        "notes": "Timestamp, Activity Type (User Activity Data), Title, Bplist Data and "
                 "Payload Data are read from the property list stored in the userActivityData "
                 "field. Payload Data is that property list's payload field. In the 1,054 payloads "
                 "tested it held the bytes 4D 50 03 05 and one MessagePack value; it is written as "
                 "key = value entries separated by line breaks, with extension type 1 shown as a UUID, extension type 3 as a UTC date "
                 "(seconds since 2001-01-01) and extension type 0 as the URL string that follows it. "
                 "Container Data is the container field of the property list stored in "
                 "contentAttributeSetData, a binary key and value table starting DE BA 00 01; it is "
                 "written as key = value entries separated by line breaks, sorted by key, with tag 0x13 "
                 "values as UTC dates. The payload's values are MessagePack; no published "
                 "specification was found for its MP header, its extension types or the container "
                 "format. Both readers were written "
                 "for this artifact and checked against macOS's own decode of the same records "
                 "(NSUserActivity _initWithUserActivityData:, then userInfo and contentAttributeSet, "
                 "macOS 27.2.1 (26B131)): every payload "
                 "and container in the written records of the 23 iOS images tested matched key for "
                 "key and value for value, 1,054 payloads and 452 containers (on 11 of the images). No iOS copy of the "
                 "decoder was run. Container values seen were UTF-8 and UTF-16 strings, dates, "
                 "doubles, nulls, one boolean and 17 arrays of one item; arrays of more items are "
                 "read by the same code but were not seen, and a tag not seen is shown as not "
                 "decoded rather than dropped. Byte values longer than 256 bytes (343 of the 390 in "
                 "the tested payloads) are shown as their length and first 256 bytes in hex. A "
                 "payload or container that cannot be decoded is kept as its raw bytes and logged; no "
                 "record in the tested images took that path. "
                 "Bplist Data leaves out payload and contentAttributeSetData, which Payload Data and "
                 "Container Data show decoded. "
                 "Activity Type and Bundle ID are the activityType and "
                 "associatedBundleID fields of the BMUniversalRecentsMetadata class, read from "
                 "BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was "
                 "read. Activity Type was reported before as Description; the property-list value "
                 "reported before as Activity type is now Activity Type (User Activity Data). "
                 "On the 23 iOS images tested Activity Type and Activity Type (User Activity Data) were "
                 "identical on each of the 1,422 written rows; both are kept because they "
                 "come from different places in the record. Associated URL is field 6 (associatedURLString) of the BMUniversalRecentsMetadata class in BiomeLibrary.framework, macOS 27.2.1 (26B131); no iOS copy was read. It was not reported before as its own column. On the 23 iOS images tested it was set on 192 of 561 written UniversalRecents.UserActivity.Metadata rows (16 of the 17 images with written records) and 318 of 861 written UserActivityMetadata rows (6 of 6 images). On these 510 rows the same string also appeared inside Bplist Data.",
        "paths": (
            '*/Biome/streams/restricted/UserActivityMetadata/local*',
            '*/streams/*/UniversalRecents.UserActivity.Metadata/local/*',
        ),
        "output_types": "standard",
        "multiline_columns": ("Payload Data", "Container Data"),
        "artifact_icon": "activity",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 364 rows",
            "felix23_ios16": "iOS 16.5 | 166 rows",
            "jess_ios15": "iOS 15.0.2 | 72 rows",
            "magnet_ios16": "iOS 16.1.1 | 131 rows",
            "hc_ios18_7": "iOS 18.7.8 | 101 rows",
            "iphone11_ios17": "iOS 17.3 | 450 rows",
        }
    }
}


import os
import struct
import uuid
from datetime import timedelta, timezone
from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, convert_time_obj_to_utc, get_plist_content, logfunc

from datetime import datetime as _dt

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)

def _safe_time_obj(value):
    """Set UTC tzinfo on datetime objects; pass strings/None through unchanged."""
    return convert_time_obj_to_utc(value) if isinstance(value, _dt) else value


# Readers for the two binary fields of the userActivityData property list. Neither format
# has a published specification; both layouts were worked out from the bytes and checked
# against Foundation's own decode of the same records (see the notes).

_MAC_EPOCH = _dt(2001, 1, 1, tzinfo=timezone.utc)
_BYTES_SHOWN = 256


class _Undecoded(Exception):
    """A value or structure the readers below do not know how to decode."""


def _mac_time_text(seconds):
    try:
        return (_MAC_EPOCH + timedelta(seconds=seconds)).isoformat(sep=' ')
    except (OverflowError, ValueError):
        return f'{seconds!r} (seconds since 2001-01-01 UTC, out of range)'


def _bytes_text(value):
    shown = value[:_BYTES_SHOWN].hex()
    if len(value) > _BYTES_SHOWN:
        return f'<{len(value)} bytes, first {_BYTES_SHOWN} shown> {shown}'
    return f'<{len(value)} bytes> {shown}'


def _lines(value, path, out):
    """Flatten a decoded value into 'key = value' lines."""
    if isinstance(value, dict):
        if not value and path:
            out.append(f'{path} = {{}}')
        for key, item in value.items():
            _lines(item, f'{path}.{key}' if path else str(key), out)
    elif isinstance(value, list):
        if not value:
            out.append(f'{path} = []')
        for index, item in enumerate(value):
            _lines(item, f'{path}[{index}]', out)
    else:
        if isinstance(value, bytes):
            value = _bytes_text(value)
        out.append(f'{path} = {value}')
    return out


# Payload: the bytes 'MP' 03 05, then one MessagePack value (https://github.com/msgpack/msgpack/blob/master/spec.md).
# Extension type 1 holds 16 bytes read as a UUID, type 3 an 8-byte little-endian double of
# seconds since 2001-01-01 UTC, and type 0 is followed by a MessagePack string read as a URL.

_PAYLOAD_MAGIC = b'MP\x03\x05'
# Nesting deeper than this, or an array that points back at itself, is refused as damaged.
_MAX_DEPTH = 64
# Container values one record may decode; array entries can point at shared or earlier values.
_MAX_VALUES = 100_000


def _mp_value(data, pos, depth=0):
    if depth > _MAX_DEPTH:
        raise _Undecoded(f'nesting deeper than {_MAX_DEPTH} at offset {pos}')
    tag = data[pos]
    pos += 1
    if tag <= 0x7f:
        return tag, pos
    if tag >= 0xe0:
        return tag - 0x100, pos
    if 0x80 <= tag <= 0x8f:
        return _mp_map(data, pos, tag & 0x0f, depth)
    if 0x90 <= tag <= 0x9f:
        return _mp_array(data, pos, tag & 0x0f, depth)
    if 0xa0 <= tag <= 0xbf:
        return _mp_take(data, pos, tag & 0x1f).decode('utf-8'), pos + (tag & 0x1f)
    if tag == 0xc0:
        return None, pos
    if tag in (0xc2, 0xc3):
        return tag == 0xc3, pos
    if tag in (0xc4, 0xc5, 0xc6, 0xd9, 0xda, 0xdb):
        width = {0xc4: 1, 0xc5: 2, 0xc6: 4, 0xd9: 1, 0xda: 2, 0xdb: 4}[tag]
        size = int.from_bytes(_mp_take(data, pos, width), 'big')
        pos += width
        raw = _mp_take(data, pos, size)
        return (raw.decode('utf-8') if tag >= 0xd9 else raw), pos + size
    if tag == 0xca:
        return struct.unpack_from('>f', data, pos)[0], pos + 4
    if tag == 0xcb:
        return struct.unpack_from('>d', data, pos)[0], pos + 8
    if 0xcc <= tag <= 0xd3:
        width = 1 << ((tag - 0xcc) % 4)
        return int.from_bytes(_mp_take(data, pos, width), 'big', signed=tag >= 0xd0), pos + width
    if tag in (0xdc, 0xdd, 0xde, 0xdf):
        width = 2 if tag in (0xdc, 0xde) else 4
        count = int.from_bytes(_mp_take(data, pos, width), 'big')
        reader = _mp_array if tag in (0xdc, 0xdd) else _mp_map
        return reader(data, pos + width, count, depth)
    if tag in (0xc7, 0xc8, 0xc9, 0xd4, 0xd5, 0xd6, 0xd7, 0xd8):
        if tag in (0xc7, 0xc8, 0xc9):
            width = {0xc7: 1, 0xc8: 2, 0xc9: 4}[tag]
            size = int.from_bytes(_mp_take(data, pos, width), 'big')
            pos += width
        else:
            size = {0xd4: 1, 0xd5: 2, 0xd6: 4, 0xd7: 8, 0xd8: 16}[tag]
        code = struct.unpack_from('b', data, pos)[0]
        pos += 1
        if code == 0:
            url, pos = _mp_value(data, pos, depth + 1)
            if not isinstance(url, str):
                raise _Undecoded('extension type 0 not followed by a string')
            return url, pos
        raw = _mp_take(data, pos, size)
        if code == 1 and size == 16:
            return str(uuid.UUID(bytes=raw)).upper(), pos + size
        if code == 3 and size == 8:
            return _mac_time_text(struct.unpack('<d', raw)[0]), pos + size
        return f'<extension type {code}> {raw.hex()}', pos + size
    raise _Undecoded(f'MessagePack tag 0x{tag:02x} at offset {pos - 1}')


def _mp_take(data, pos, size):
    if pos + size > len(data):
        raise _Undecoded(f'value at offset {pos} runs past the end')
    return data[pos:pos + size]


def _mp_map(data, pos, count, depth):
    result = {}
    for _ in range(count):
        key, pos = _mp_value(data, pos, depth + 1)
        result[str(key)], pos = _mp_value(data, pos, depth + 1)
    return result, pos


def _mp_array(data, pos, count, depth):
    result = []
    for _ in range(count):
        item, pos = _mp_value(data, pos, depth + 1)
        result.append(item)
    return result, pos


def _payload_text(payload, where):
    """Decoded payload as 'key = value' lines, or the raw bytes when it cannot be read."""
    try:
        if not payload.startswith(_PAYLOAD_MAGIC):
            raise _Undecoded('no MP header')
        value, end = _mp_value(payload, len(_PAYLOAD_MAGIC))
        if end != len(payload):
            raise _Undecoded(f'{len(payload) - end} bytes left after the value')
        return '\n'.join(_lines(value, '', []))
    except (_Undecoded, IndexError, struct.error, UnicodeDecodeError) as ex:
        logfunc(f'Biome User Activity Metadata: payload of {where} not decoded, raw bytes kept: {ex}')
        return payload


# Container: the bytes DE BA 00 01, the total length (u32 at 6) and the offset of the key
# name table (u32 at 10). An object table (count u16 at 0x21) of (offset u32, tag u8) entries
# ends at the key table; the entry tagged F1 is a dictionary whose entries are
# (key offset u32, value offset u32, tag u8). All integers little-endian.

_CONTAINER_MAGIC = b'\xde\xba\x00\x01'


def _cs_value(data, offset, tag, budget, depth=0):
    if depth > _MAX_DEPTH:
        raise _Undecoded(f'nesting deeper than {_MAX_DEPTH} at {offset}')
    budget[0] -= 1
    if budget[0] < 0:
        raise _Undecoded(f'more than {_MAX_VALUES} values')
    if tag == 0xf4:
        size, = struct.unpack_from('<I', data, offset)
        if size < 1 or data[offset + 3 + size] != 0:
            raise _Undecoded(f'string at {offset} not terminated')
        return data[offset + 4:offset + 3 + size].decode('utf-8')
    if tag == 0xf5:
        size, = struct.unpack_from('<I', data, offset)
        if offset + 4 + size > len(data):
            raise _Undecoded(f'string at {offset} runs past the end')
        return data[offset + 4:offset + 4 + size].decode('utf-16')
    if tag == 0x13:
        return _mac_time_text(struct.unpack_from('<d', data, offset)[0])
    if tag == 0x33:
        return struct.unpack_from('<d', data, offset)[0]
    if tag == 0xe0 and offset == 0:
        return None
    if tag == 0xe1 and offset == 1:
        return True
    if tag == 0xf0:
        size, count = struct.unpack_from('<IH', data, offset)
        end = offset + 4 + size
        return [_cs_value(data, *struct.unpack_from('<IB', data, end - 5 * count + 5 * index), budget, depth + 1)
                for index in range(count)]
    return f'<tag 0x{tag:02x}, value {offset}, not decoded>'


def _cs_decode(data):
    if not data.startswith(_CONTAINER_MAGIC):
        raise _Undecoded('no DE BA 00 01 header')
    total, key_table = struct.unpack_from('<II', data, 6)
    if total != len(data):
        raise _Undecoded(f'length field {total}, data {len(data)} bytes')
    keys = {}
    pos = key_table
    while pos < len(data):
        size, = struct.unpack_from('<H', data, pos)
        if data[pos + 2 + size] != 0:
            raise _Undecoded(f'key name at {pos} not terminated')
        keys[pos - key_table] = data[pos + 2:pos + 2 + size].decode('utf-8')
        pos += size + 3
    count, = struct.unpack_from('<H', data, 0x21)
    result = {}
    budget = [_MAX_VALUES]
    for index in range(count):
        offset, tag = struct.unpack_from('<IB', data, key_table - 5 * count + 5 * index)
        if tag != 0xf1:
            continue
        size, entries = struct.unpack_from('<IH', data, offset)
        end = offset + 4 + size
        for entry in range(entries):
            key_offset, value_offset, value_tag = struct.unpack_from('<IIB', data, end - 9 * entries + 9 * entry)
            result[keys[key_offset]] = _cs_value(data, value_offset, value_tag, budget)
    return dict(sorted(result.items()))


def _container_text(field, where):
    """The contentAttributeSetData field as 'key = value' lines, or the raw bytes when it cannot be read."""
    if field in ('', None):
        return ''
    if isinstance(field, str):
        return field
    raw = field.get('NS.data') if isinstance(field, dict) else field
    inner = get_plist_content(raw) if isinstance(raw, bytes) else None
    container = inner.get('container') if isinstance(inner, dict) else None
    if not isinstance(container, bytes):
        logfunc(f'Biome User Activity Metadata: contentAttributeSetData of {where} has no container, kept as stored')
        return raw if isinstance(raw, bytes) else str(field)
    try:
        return '\n'.join(_lines(_cs_decode(container), '', []))
    except (_Undecoded, KeyError, IndexError, struct.error, UnicodeDecodeError) as ex:
        logfunc(f'Biome User Activity Metadata: container of {where} not decoded, raw bytes kept: {ex}')
        return container



@artifact_processor
def get_biomeUseractmeta(context):

    #typess = {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'str', 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}, '2': {'type': 'double', 'name': ''}, '3': {'type': 'double', 'name': ''}, '4': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}, '5': {'type': 'double', 'name': ''}}, 'name': ''}, '5': {'type': 'str', 'name': ''}, '8': {'type': 'double', 'name': ''}, '10': {'type': 'int', 'name': ''}}
    data_list = []
    source_dirs = set()
    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in context.get_relative_path(file_found):
                continue
        else:
            continue

        source_dirs.add(os.path.dirname(file_found))
        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    # field 6 is pinned so a URL string is never decoded as a nested message
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, {'6': {'type': 'bytes', 'name': ''}})
                except _DECODE_ERRORS as ex:
                    logfunc(f'Biome User Activity Metadata: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                bplistdata = (protostuff['2'])
                desc1 = (protostuff['4'].decode())
                desc2 = (protostuff['5'].decode())
                associated_url = protostuff.get('6')
                associated_url = associated_url.decode('utf-8', errors='replace') \
                    if isinstance(associated_url, bytes) else ''
                
                
                #deserialized_plist = nd.deserialize_plist_from_string(bplistdata)
                deserialized_plist = get_plist_content(bplistdata)
                if not deserialized_plist or not isinstance(deserialized_plist, dict):
                    logfunc(f'Biome User Activity Metadata: no property list in record at offset '
                            f'{record.data_start_offset} in {filename}')
                    continue
                
                title = (deserialized_plist.get('title',''))
                when = (deserialized_plist['when'])
                when = _safe_time_obj(when)
                actype = (deserialized_plist['activityType'])
                #exdate = (deserialized_plist.get('expirationDate',''))
                
                where = f'record at offset {record.data_start_offset} in {filename}'
                payload = deserialized_plist.get('payload', '')
                if isinstance(payload, bytes):
                    payload = _payload_text(payload, where)

                container = _container_text(deserialized_plist.get('contentAttributeSetData', ''), where)

                agg = ''
                for a, b in deserialized_plist.items():
                    if a in ('payload', 'contentAttributeSetData'):
                        pass
                    else:
                        if b == ' ':
                            b = 'NULL'
                        agg = agg + f'{a} = {b}<br>'
                
                data_list.append((ts, when, record.state.name, actype, desc1, desc2, title, associated_url, agg.strip(), payload,
                                  container, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, None, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Timestamp', 'datetime'), 'SEGB State',
                    'Activity Type (User Activity Data)', 'Activity Type', 'Bundle ID', 'Title', 'Associated URL', 'Bplist Data', 'Payload Data','Container Data', 'Filename',
                    'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
