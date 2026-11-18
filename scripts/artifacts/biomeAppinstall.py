__artifacts_v2__ = {
    "get_biomeAppinstall": {
        "name": "Biome - App Install",
        "description": "Records from the App.Install and _DKEvent.App.Install Biome streams.",
       "author": "@JohnHyla, @Gear-I",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Covers two Biome streams that carry different record layouts. _DKEvent.App.Install records are read with a fixed layout. The labels Activity, Bundle Info, App Info, App Info2, Timestamp, Time End and Time Write are not sourced here. App.Install records carry a bundle id and field 5, which the BMAppInstall class names isInstall, read from BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was read. Is Install reads True for 1 and False for 0, is blank for _DKEvent.App.Install rows, and was reported before as Event Value (as stored). On the tested images (343 written App.Install rows) Is Install held True on 330 rows and False on 13. The Stream column names the source stream for each row. Records whose SEGB state is Deleted are reported with their SEGB timestamp, state, stream, filename and offset only. Paths containing 'tombstone' are not parsed. On the tested images (25 tombstone files, 263 written records) each record held a 15-digit string, three or four integers and a six-letter word. None held a bundle identifier. The meaning of the fields is not established.",
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
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv, logfunc

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
                '1': {
                    'type': 'message',
                    'message_typedef': {},
                    'name': ''
                },
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
                        '3': {'type': 'str', 'name': ''}
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
                    timestart = webkit_timestampsconv(protostuff['2'])
                    timeend = webkit_timestampsconv(protostuff['3'])

                    bundleid = protostuff['4']['3']
                    actionguid = protostuff['5']
                    appinfo1 = appinfo2 = bundleinfo = ''

                    if protostuff.get('7', '') != '':
                        if isinstance(protostuff['7'], list):
                            if len(protostuff['7']) < 3:
                                appinfo1 = protostuff['7'][0]['2'].get('3', '')
                            else:
                                appinfo1 = protostuff['7'][0]['2'].get('3', '')
                                bundleinfo = protostuff['7'][1]['2'].get('3', '')
                                appinfo2 = protostuff['7'][2]['2'].get('3', '')

                    timewrite = webkit_timestampsconv(protostuff['8'])
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
                    bundleinfo,
                    appinfo1,
                    appinfo2,
                    actionguid,
                    '',
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
        'Bundle Info',
        'App Info',
        'App Info2',
        'Action GUID',
        'Is Install',
        'Filename',
        'Offset'
    )

    return data_headers, data_list, '\n'.join(sorted(source_dirs))


