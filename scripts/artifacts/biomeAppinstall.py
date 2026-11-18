__artifacts_v2__ = {
    "get_biomeAppinstall": {
        "name": "Biome - App Install",
        "description": "Records from the App.Install and _DKEvent.App.Install Biome streams.",
       "author": "@JohnHyla, @Gear-I",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Covers two Biome streams that carry different record layouts. _DKEvent.App.Install records are read with the field layout of CoreDuet's _DKPREvent class, read on macOS 27.2.1 (26B131); no iOS copy of the class was read. On the 20 images tested all 424 written records held only fields that class declares. Their metadata entries are picked by integer index, named from CoreDuet's own conversion of synthetic records: Title 2000 (title), Is Install 2001 (isInstall), Primary Category 2002 (primaryCategory) and Sub Categories 2003 (subCategories, stored as a keyed archive of an array; the items are shown joined by commas). Before, App Info, Bundle Info and App Info2 took the first three metadata entries by position; on the tested images the title was under App Info on all 177 rows that held one, and the primary category was under Bundle Info on all 176 rows that held one; and the isInstall entry, held by all 424 written _DKEvent.App.Install records, was not reported. The labels Activity, Timestamp, Time End and Time Write are not sourced here. App.Install records carry a bundle id and field 5, which the BMAppInstall class names isInstall, read from BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was read. Is Install reads True for 1 and False for 0 on both streams; on App.Install it was reported before as Event Value (as stored). On the tested images it held True on 411 and False on 13 of the 424 written _DKEvent.App.Install rows. On the tested images (343 written App.Install rows) Is Install held True on 330 rows and False on 13. The Stream column names the source stream for each row. Records whose SEGB state is Deleted are reported with their SEGB timestamp, state, stream, filename and offset only. Paths containing 'tombstone' are not parsed. On the tested images (25 tombstone files, 263 written records) each record held a 15-digit string, three or four integers and a six-letter word. None held a bundle identifier. The meaning of the fields is not established.",
        "paths": ('*/Biome/streams/restricted/_DKEvent.App.Install/local/*', '*/Biome/streams/restricted/App.Install/local/*'),
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 142 rows",
            "felix23_ios16": "iOS 16.5 | 88 rows",
            "magnet_ios16": "iOS 16.1.1 | 64 rows",
            "felix_ios17": "iOS 17.6.1 | 262 rows",
            "fsfull002_ios17": "iOS 17.1 | 120 rows",
            "iphone11_ios17": "iOS 17.3 | 151 rows",
            "otto_ios17": "iOS 17.5.1 | 244 rows",
            "dexter_ios18": "iOS 18.3.2 | 179 rows",
            "hc_ios18_7": "iOS 18.7.8 | 200 rows",
            "iphone12_ios18": "iOS 18.7 | 168 rows",
            "iphone14plus_ios18": "iOS 18.0 | 98 rows",
            "hc_ios26": "iOS 26.5.2 | 266 rows",
        }
    }
}

import os
import struct
from datetime import timezone
from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv, get_plist_content, logfunc

def _text(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    if value is None or isinstance(value, (dict, list)):
        return ''
    return str(value)


def _metadata_by_index(entries):
    """_DKEvent metadata entries keyed by integer index (field 7.N.3), with their value.

    Index names, read from CoreDuet.framework on macOS 27.2.1 (26B131) through _DKEvent
    fromPBCodable: on synthetic records: 2000 title, 2001 isInstall, 2002 primaryCategory,
    2003 subCategories (_DKAppInstallMetadataKey).
    """
    if isinstance(entries, dict):
        entries = [entries]
    found = {}
    for entry in entries or []:
        if not isinstance(entry, dict) or not isinstance(entry.get('3'), int):
            continue
        value = entry.get('2') if isinstance(entry.get('2'), dict) else {}
        for field in ('3', '4', '6'):
            if field in value:
                found[entry['3']] = value[field]
                break
    return found


def _subcategories(value):
    """subCategories is stored as a blob holding a keyed archive of an array; show its items, or the blob size."""
    if not isinstance(value, bytes):
        return _text(value)
    plist = get_plist_content(value)
    if isinstance(plist, list):
        return ', '.join(_text(item) for item in plist)
    return f'<{len(value)} bytes>'


@artifact_processor
def get_biomeAppinstall(context):

    typess = {
        '1': {
            'type': 'message',
            'message_typedef': {
                '1': {'type': 'str', 'name': ''},
                '2': {
                    'type': 'message',
                    'message_typedef': {
                        '1': {'type': 'int', 'name': ''},
                        '2': {'type': 'int', 'name': ''}
                    },
                    'name': ''
                }
            },
            'name': ''
        },
        '2': {'type': 'double', 'name': ''},
        '3': {'type': 'double', 'name': ''},
        '4': {
            'type': 'message',
            'message_typedef': {
                '1': {
                    'type': 'message',
                    'message_typedef': {
                        '1': {'type': 'int', 'name': ''},
                        '2': {'type': 'int', 'name': ''}
                    },
                    'name': ''
                },
                '3': {'type': 'str', 'name': ''}
            },
            'name': ''
        },
        '5': {'type': 'str', 'name': ''},
        '7': {
            'type': 'message',
            'message_typedef': {
                '1': {'type': 'bytes', 'name': ''},
                '2': {
                    'type': 'message',
                    'message_typedef': {
                        '1': {
                            'type': 'message',
                            'message_typedef': {
                                '1': {'type': 'int', 'name': ''},
                                '2': {'type': 'int', 'name': ''}
                            },
                            'name': ''
                        },
                        '4': {'type': 'int', 'name': ''},
                        '3': {'type': 'str', 'name': ''},
                        '6': {'type': 'bytes', 'name': ''}
                    },
                    'name': ''
                },
                '3': {'type': 'int', 'name': ''}
            },
            'name': ''
        },
        '8': {'type': 'double', 'name': ''},
        '10': {'type': 'int', 'name': ''}
    }

    # App.Install records are a different message from _DKEvent.App.Install: a bundle id
    # and a single integer. Applying the typedef above to them fails on every record, so
    # the stream directory selects the layout.
    minimal_typess = {
        '1': {'type': 'str', 'name': ''},
        '5': {'type': 'int', 'name': ''}
    }

    data_list = []
    source_dirs = set()

    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found)

        if filename.startswith('.'):
            continue

        if not os.path.isfile(file_found):
            continue

        if 'tombstone' in context.get_relative_path(file_found):
            continue

        parent = os.path.dirname(file_found)
        is_dkevent = '_DKEvent.App.Install' in parent
        stream = '_DKEvent.App.Install' if is_dkevent else 'App.Install'

        source_dirs.add(parent)
        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                if not is_dkevent:
                    try:
                        minimal, _ = blackboxprotobuf.decode_message(record.data, minimal_typess)
                    except (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError) as ex:
                        logfunc(f"Skipping biomeAppinstall record due to protobuf decode error: {ex} |"
                                f"File: {context.get_relative_path(file_found)} | "
                                f"Offset: {record.data_start_offset}"
                                )
                        continue
                    data_list.append((
                        ts, None, None, None, record.state.name, stream, None,
                        minimal.get('1', ''), None, None, None, None,
                        {1: 'True', 0: 'False'}.get(minimal.get('5'), ''), filename,
                        record.data_start_offset
                    ))
                    continue
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, typess)

                    activity = protostuff['1']['1']
                    # an NSDate sentinel converts to ''; kept as None, as in the Deleted rows
                    timestart = webkit_timestampsconv(protostuff['2']) or None
                    timeend = webkit_timestampsconv(protostuff['3']) or None

                    bundleid = protostuff['4']['3']
                    actionguid = protostuff['5']
                    meta = _metadata_by_index(protostuff.get('7'))
                    is_install = meta.get(2001)
                    is_install = {1: 'True', 0: 'False'}.get(is_install, '') \
                        if isinstance(is_install, int) else ''

                    timewrite = webkit_timestampsconv(protostuff['8']) or None
                except (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError) as ex:
                    logfunc(f"Skipping biomeAppinstall record due to protobuf decode error: {ex} |"
                    f"File: {context.get_relative_path(file_found)} | "
                    f"Offset: {record.data_start_offset}"
                    )
                    continue

                data_list.append((
                    ts,
                    timestart,
                    timeend,
                    timewrite,
                    record.state.name,
                    stream,
                    activity,
                    bundleid,
                    _text(meta.get(2000)),
                    _text(meta.get(2002)),
                    _subcategories(meta.get(2003)),
                    actionguid,
                    is_install,
                    filename,
                    record.data_start_offset
                ))

            elif record.state == EntryState.Deleted:
                data_list.append((
                    ts,
                    None,
                    None,
                    None,
                    record.state.name,
                    stream,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    filename,
                    record.data_start_offset
                ))

    data_headers = (
        ('SEGB Timestamp', 'datetime'),
        ('Timestamp', 'datetime'),
        ('Time End', 'datetime'),
        ('Time Write', 'datetime'),
        'SEGB State',
        'Stream',
        'Activity',
        'Bundle ID',
        'Title',
        'Primary Category',
        'Sub Categories',
        'Action GUID',
        'Is Install',
        'Filename',
        'Offset'
    )

    return data_headers, data_list, '\n'.join(sorted(source_dirs))


