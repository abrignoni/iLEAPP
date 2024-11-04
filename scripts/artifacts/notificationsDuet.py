__artifacts_v2__ = {
    "get_notificationsDuet": {
        "name": "Notification Duet",
        "description": "Parses battery percentage entries from biomes",
        "author": "@JohnHyla",
        "version": "0.0.2",
        "date": "2024-10-17",
        "requirements": "none",
        "category": "Notifications",
        "notes": "",
        "paths": ('*/userNotificationEvents/local/*'),
        "output_types": "none",
        "function": "get_notificationsDuet"
    }
}


import os
import blackboxprotobuf
from datetime import timezone
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import webkit_timestampsconv, convert_utc_human_to_timezone, tsv
from scripts.artifact_report import ArtifactHtmlReport
from scripts.lavafuncs import lava_process_artifact, lava_insert_sqlite_data


def get_notificationsDuet(files_found, report_folder, seeker, wrap_text, timezone_offset):

    category = "Notifications Duet"
    module_name = "get_notificationsDuet"

    data_headers = ('SEGB Timestamp', 'Notification Time', 'Notification Time 2', 'SEGB State', 'GUID', 'Title',
                    'Subtitle','Body', 'Bundle ID', 'Bundle ID 2', 'Optional Data', 'Person Identifier', 'Person Info',
                    'GUID 2', 'Filename', 'Offset')
    lava_data_headers = (('SEGB Timestamp', 'datetime'), ('Notification Time', 'datetime'),
                         ('Notification Time 2', 'datetime'), 'SEGB State', 'GUID', 'Title', 'Subtitle', 'Body',
                         'Bundle ID', 'Bundle ID 2', 'Optional Data', 'Person Identifier', 'Person Info', 'GUID 2',
                         'Filename', 'Offset')

    typess = {'1': {'type': 'message',
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

    data_list = []
    report_file = 'Unknown'
    for file_found in files_found:
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in file_found:
                continue
            else:
                report_file = os.path.dirname(file_found)
        else:
            continue

        file_data_list = []
        for record in read_segb_file(file_found):

            segb_time = record.timestamp1
            segb_time = segb_time.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                protostuff, types = blackboxprotobuf.decode_message(record.data, typess)
                proto_time = webkit_timestampsconv(protostuff['1'].get('1'))
                proto_time2 = webkit_timestampsconv(protostuff.get('3'))
                guid = protostuff['1'].get('2')
                title = protostuff['1'].get('3')
                subtitle = protostuff['1'].get('4')
                body = (protostuff['1'].get('5'))
                bundle_id = protostuff['1'].get('8')
                bundle_id2 = protostuff['1'].get('12')
                optional_data = protostuff['1'].get('10')
                guid2 = protostuff.get('4')
                person_identifier = protostuff['1'].get('13')
                person_info = protostuff['1'].get('20')
                if isinstance(person_info, list):
                    person_info = ', '.join(person_info)

                file_data_list.append((segb_time, proto_time, proto_time2, record.state.name, guid,title,subtitle, body,
                                       bundle_id, bundle_id2, optional_data, person_identifier, person_info, guid2,
                                       filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                file_data_list.append((segb_time, None, None, record.state.name, None, None,None,None, None,None, None,
                                       None, None, None, filename, record.data_start_offset))

        data_list.extend(file_data_list)

        if len(file_data_list) > 0:
            description = ''
            report = ArtifactHtmlReport(f'Notifications Duet')
            report.start_artifact_report(report_folder, f'Notifications Duet - {filename}', description)
            report.add_script()
            report.write_artifact_data_table(data_headers, file_data_list, file_found)
            report.end_artifact_report()

            tsvname = f'Notifications Duet - {filename}'
            tsv(report_folder, data_headers, file_data_list, tsvname)  # TODO: _csv.Error: need to escape, but no escapechar set

    # Single table for LAVA output
    table_name, object_columns, column_map = lava_process_artifact(category, module_name,
                                                                   'Notifications Duet',
                                                                   lava_data_headers,
                                                                   len(data_list))

    lava_insert_sqlite_data(table_name, data_list, object_columns, lava_data_headers, column_map)



