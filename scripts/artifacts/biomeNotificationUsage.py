__artifacts_v2__ = {
    "get_biomeNotificationUsage": {
        "name": "Biome - Notification Usage",
        "description": "Parses the Notification Usage biome",
        "author": "Thijs van Meurs",
        "version": "0.0.1",
        "date": "2026-06-29",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/Biome/streams/restricted/Notification.Usage/*'),
        "output_types": "standard"
    }
}


import os
from datetime import timezone
import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv, logfunc


@artifact_processor
def get_biomeNotificationUsage(context):

    typess = {
                '1': {'name': '', 'type': 'str'}, '2': {'name': '', 'type': 'double'}, '3': {'name': '', 'type': 'int'},
                '4': {'name': '', 'type': 'str'}, '5': {'name': '', 'type': 'str'}, '8': {'name': '', 'type': 'str'}, '9': {'name': '', 'type': 'str'},
                '11': {'name': '', 'type': 'int'}, '12': {'name': '', 'type': 'str'}, '14': {'name': '', 'type': 'str'},
                '16': {'name': '', 'type': 'int'}, '18': {'name': '', 'type': 'int'}
              }

    data_list = []
    report_file = 'Unknown'
    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if not os.path.isfile(file_found) or 'tombstone' in file_found:
            continue
        report_file = os.path.dirname(file_found)

        try:
            for record in read_segb_file(file_found):
                ts = record.timestamp1.replace(tzinfo=timezone.utc)

                if record.state == EntryState.Written:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, typess)

                    raw_ts = protostuff.get('2')
                    timeStart = webkit_timestampsconv(raw_ts) if raw_ts is not None else None
                    appName = protostuff.get('14')
                    notificationContent = protostuff.get('8')
                    notificationContent2 = protostuff.get('12')

                    data_list.append((ts, timeStart, record.state.name, appName,
                                      notificationContent, notificationContent2, filename,
                                      record.data_start_offset))
        except ValueError as e:
            logfunc(f"Skipping {file_found}: {e}")
            continue

    data_headers = (('SEGB Timestamp', 'datetime'), ('Timestamp', 'datetime'), 'SEGB State',
                    'Application name', 'Notification content', 'Notification content 2',
                    'Filename', 'Offset')
    return data_headers, data_list, report_file