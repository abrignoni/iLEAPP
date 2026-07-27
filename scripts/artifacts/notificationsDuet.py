__artifacts_v2__ = {
    "get_notificationsDuet": {
        "name": "Notification Duet",
        "description": "Parses Duet/proactive userNotificationEvents SEGB records",
        "author": "@JohnHyla",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Notifications",
        "notes": "",
        "paths": ('*/userNotificationEvents/local/*',),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 16542 rows",
            "felix_ios17": "iOS 17.6.1 | 376 rows",
            "fsfull002_ios17": "iOS 17.1 | 183 rows",
            "hc_ios18_7": "iOS 18.7.8 | 353 rows",
            "iphone11_ios17": "iOS 17.3 | 27202 rows",
            "iphone14plus_ios18": "iOS 18.0 | 142 rows",
            "otto_ios17": "iOS 17.5.1 | 26256 rows",
            "abe_ios16": "iOS 16.5 | 18231 rows",
            "felix23_ios16": "iOS 16.5 | 5425 rows",
            "jess_ios15": "iOS 15.0.2 | 325 rows",
            "magnet_ios16": "iOS 16.1.1 | 269 rows",
        }
    }
}

import os
from datetime import timezone

from scripts import blackboxprotobuf

from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv

_TYPEDEF = {
    '1': {'type': 'message',
          'message_typedef': {'1': {'type': 'double', 'name': ''},
                              '2': {'type': 'str', 'name': ''},
                              '3': {'type': 'str', 'name': ''},
                              '4': {'type': 'str', 'name': ''},
                              '5': {'type': 'str', 'name': ''},
                              '6': {'type': 'int', 'name': ''},
                              '8': {'type': 'str', 'name': ''},
                              '9': {'type': 'message', 'message_typedef': {}, 'name': ''},
                              '10': {'type': 'str', 'name': ''},
                              '12': {'type': 'str', 'name': ''},
                              '13': {'type': 'str', 'name': ''},
                              '14': {'type': 'int', 'name': ''},
                              '15': {'type': 'int', 'name': ''},
                              '16': {'type': 'int', 'name': ''},
                              '17': {'type': 'int', 'name': ''},
                              '19': {'type': 'fixed64', 'name': ''},
                              '20': {'type': 'str', 'name': ''}},
          'name': ''},
    '2': {'type': 'int', 'name': ''},
    '3': {'type': 'double', 'name': ''},
    '4': {'type': 'str', 'name': ''},
    '5': {'type': 'int', 'name': ''}}


@artifact_processor
def get_notificationsDuet(context):
    data_headers = (('SEGB Timestamp', 'datetime'), ('Notification Time', 'datetime'),
                    ('Notification Time 2', 'datetime'), 'SEGB State', 'GUID', 'Title', 'Subtitle',
                    'Body', 'Bundle ID', 'Bundle ID 2', 'Optional Data', 'Person Identifier',
                    'Person Info', 'GUID 2', 'Filename', 'Offset')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.') or not os.path.isfile(file_found) or 'tombstone' in file_found:
            continue
        rel = context.get_relative_path(file_found)
        if rel not in sources:
            sources.append(rel)

        for record in read_segb_file(file_found):
            segb_time = record.timestamp1.replace(tzinfo=timezone.utc)
            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, _TYPEDEF)
                except Exception:  # pylint: disable=broad-exception-caught
                    continue  # malformed/variant record
                p1 = protostuff.get('1') or {}
                person_info = p1.get('20')
                if isinstance(person_info, list):
                    person_info = ', '.join(person_info)
                data_list.append((segb_time, webkit_timestampsconv(p1.get('1')),
                                  webkit_timestampsconv(protostuff.get('3')), record.state.name,
                                  p1.get('2'), p1.get('3'), p1.get('4'), p1.get('5'), p1.get('8'),
                                  p1.get('12'), p1.get('10'), p1.get('13'), person_info,
                                  protostuff.get('4'), filename, record.data_start_offset))
            elif record.state == EntryState.Deleted:
                data_list.append((segb_time, None, None, record.state.name, None, None, None, None,
                                  None, None, None, None, None, None, filename,
                                  record.data_start_offset))

    return data_headers, data_list, ', '.join(sources)
