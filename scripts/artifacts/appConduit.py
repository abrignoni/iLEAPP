"""
This module parses AppConduit log files to extract information about device
interactions between iPhone and other iOS devices (e.g., Apple Watch).
"""

__artifacts_v2__ = {
    'app_conduit': {
        'name': 'App Conduit',
        'description': 'The AppConduit log file stores information about \
            interactions between iPhone and other iOS devices, \
            i.e. Apple Watch',
        'author': '@ydkhatri',
        'creation_date': '2020-08-05',
        'last_update_date': '2025-04-05',
        'requirements': 'none',
        'category': 'App Conduit',
        'notes': '',
        'paths': ('*/mobile/Library/Logs/AppConduit/AppConduit.log.*',),
        'output_types': 'standard',
        'artifact_icon': 'activity'
    }
}

import pathlib
import re

from scripts.ilapfuncs import artifact_processor, get_txt_file_content, \
    convert_log_ts_to_utc


@artifact_processor
def app_conduit(context):
    """
    Parses each log file found and from lines that match a specific regular
    expression pattern extracts device connection and disconnection events,
    along with associated device information.
    """

    files_found = context.get_files_found()
    source_paths = set()
    data_list = []
    device_type_and_info = {}

    info = ''
    reg_filter = r'(([A-Za-z]+[\s]+([a-zA-Z]+[\s]+[0-9]+)[\s]+' + \
        r'([0-9]+\:[0-9]+\:[0-9]+)[\s]+([0-9]{4}))([\s]+[\[\d\]]+[\s]+' + \
        r'[\<a-z\>]+[\s]+[\(\w\)]+)[\s\-]+(((.*)(device+\:([\w]+\-[\w]+\-' + \
        r'[\w]+\-[\w]+\-[\w]+))(.*)$)))'
    date_filter = re.compile(reg_filter)

    for file_found in files_found:
        if file_found.startswith('\\\\?\\'):
            file_name = pathlib.Path(file_found[4:]).name
            file_location = pathlib.Path(file_found[4:]).parent
        else:
            file_name = pathlib.Path(file_found).name
            file_location = pathlib.Path(file_found).parent
        source_paths.add(str(file_location))

        file = get_txt_file_content(file_found)
        for line in file:
            line_match = re.match(date_filter, line)

            if line_match:
                date_time = line_match.group(3, 5, 4)
                conv_time = ' '.join(date_time)
                dtime_obj = convert_log_ts_to_utc(conv_time)

                values = line_match.group(9)
                device_id = line_match.group(11)

                if 'devicesAreNowConnected' in values:
                    pairing_id = line_match.group(12).split(' ')[3][:-1]
                    device_type = line_match.group(12).split(' ')[4]
                    device_model = context.get_device_model(device_type)
                    os_build = line_match.group(12).split(' ')[7].strip('()')
                    os_version = context.get_os_version(os_build, device_type)
                    device_type_and_info.setdefault(
                        pairing_id, {'device_type': device_type,
                                     'device_model': device_model,
                                     'os_build': os_build,
                                     'os_version': os_version})
                    info = 'Connected'
                    data_list.append((dtime_obj, info, device_id, pairing_id,
                                      device_type, device_model, os_build,
                                      os_version, file_name))
                if 'devicesAreNoLongerConnected' in values:
                    pairing_id = line_match.group(12).split(' ')[3][:-1]
                    device_info = device_type_and_info.get(pairing_id, {})
                    device_type = device_info.get('device_type', '')
                    device_model = device_info.get('device_model', '')
                    os_build = device_info.get('os_build', '')
                    os_version = device_info.get('os_version', '')
                    info = 'Disconnected'
                    data_list.append((dtime_obj, info, device_id, pairing_id,
                                      device_type, device_model, os_build,
                                      os_version, file_name))
                # if 'Resuming because' in values:
                #     info = 'Resumed'
                #     data_list.append((dtime_obj,info,device_id,device_type_tmp,file_name))
                # if 'Suspending because' in values:
                #     info = 'Suspended'
                #     data_list.append((dtime_obj,info,device_id,device_type_tmp,file_name))
                # if 'Starting reunion sync because device ' in values:
                #     info = 'Reachable again after reunion sync'
                #     data_list.append((dtime_obj,info,device_id,device_type_tmp,file_name))

    data_headers = (('Timestamp', 'datetime'), 'Device interaction',
                    'Device ID', 'Pairing ID', 'Device Type', 'Device Model',
                    'OS Build', 'OS Version', 'Log File Name')
    source_path = ', '.join(source_paths)

    return data_headers, data_list, source_path
