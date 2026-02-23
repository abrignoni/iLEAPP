import os
import re
from packaging import version
from scripts.ilapfuncs import artifact_processor, iOS

def month_converter(month):
    months = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]
    month = months.index(month) + 1
    if month < 10:
        month = f"{month:02d}"
    return month

def day_converter(day):
    day = int(day)
    if day < 10:
        day = f"{day:02d}"
    return day

def line_splitting(line):
    datecheck = re.match(r"^[a-zA-Z]", line)
    if datecheck:
        splitline = line.split(' ',6)
        notice = splitline.pop(6)
        _, month, space, day, time, year = splitline
        if space == '':
            pass
        else:
            splitline = line.split(' ',5)
            notice = splitline.pop(5)
            _, month, day, time, year = splitline
        if 'Reboot detected' in notice:
            notice = notice.split('main: ')[1]
        else:
            if ':]: ' in notice:
                notice = notice.split(':]: ')[1]
            else:
                notice = notice.split(': ')[1]
        day = day_converter(day)
        month = month_converter(month)
        timestamp = (str(year) + "-" + str(month) + "-" + str(day) + " " + str(time))
        return((timestamp,notice))
    return None

def _parse_install_logs(files_found):
    """Parse mobile installation log files and return (data_list, data_list_reboot)."""
    data_list = []
    data_list_reboot = []
    for file_found in files_found:
        filename = os.path.basename(file_found)

        with open(file_found, 'r', encoding='utf8') as f:
            data = f.readlines()

        for line in data:
            if 'Attempting Delta patch update' in line:
                desc = 'Update'
                values = line_splitting(line)
                data_list.append((values[0],desc,values[1],filename))
            elif 'Installing <MIInstallableBundle' in line:
                desc = 'Install'
                values = line_splitting(line)
                data_list.append((values[0],desc,values[1],filename))
            elif 'Data container for' in line:
                desc = 'Container'
                values = line_splitting(line)
                data_list.append((values[0],desc,values[1],filename))
            elif 'Made container live for' in line:
                desc = 'Container Live'
                values = line_splitting(line)
                data_list.append((values[0],desc,values[1],filename))
            elif 'Reboot detected' in line:
                desc = 'Reboot'
                values = line_splitting(line)
                data_list_reboot.append((values[0],desc,values[1],filename))
                data_list.append((values[0],desc,values[1],filename))
            elif 'Install Successful for' in line:
                desc = 'Install Successful'
                values = line_splitting(line)
                data_list.append((values[0],desc,values[1],filename))
            elif 'Running installation as' in line:
                desc = 'Running Installation'
                values = line_splitting(line)
                data_list.append((values[0],desc,values[1],filename))
            elif 'Attempting Parallel patch update' in line:
                desc = 'Parallel Update'
                values = line_splitting(line)
                data_list.append((values[0],desc,values[1],filename))
            elif 'Uninstalling identifier' in line:
                desc = 'Uninstalling'
                values = line_splitting(line)
                data_list.append((values[0],desc,values[1],filename))
            elif 'Destroying container' in line:
                desc = 'Destroying'
                values = line_splitting(line)
                data_list.append((values[0],desc,values[1],filename))
    return data_list, data_list_reboot

@artifact_processor
def get_mobileInstallb_history(files_found, report_folder, seeker, wrap_text, timezone_offset):
    iosversion = iOS.get_version()
    if version.parse(iosversion) < version.parse("17"):
        return (), [], ''

    data_list, _ = _parse_install_logs(files_found)

    data_headers = ('Timestamp (Local)','Type','Notice','Source File')
    return data_headers, data_list, str(files_found[0]) if files_found else ''

@artifact_processor
def get_mobileInstallb_reboots(files_found, report_folder, seeker, wrap_text, timezone_offset):
    iosversion = iOS.get_version()
    if version.parse(iosversion) < version.parse("17"):
        return (), [], ''

    _, data_list_reboot = _parse_install_logs(files_found)

    data_headers = ('Timestamp (Local)','Type','Notice','Source File')
    return data_headers, data_list_reboot, str(files_found[0]) if files_found else ''

__artifacts_v2__ = {
    "get_mobileInstallb_history": {
        "name": "Mobile Installation Logs History",
        "description": "Mobile Installation Logs. All timestamps are in Local Time",
        "author": "",
        "version": "0.2",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Mobile Installation Logs",
        "notes": "",
        "paths": ('*/mobile_installation.log.*'),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    },
    "get_mobileInstallb_reboots": {
        "name": "Reboots - Mobile Installation Logs",
        "description": "Reboots - Mobile Installation Logs. All timestamps are in Local Time",
        "author": "",
        "version": "0.2",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Mobile Installation Logs",
        "notes": "",
        "paths": ('*/mobile_installation.log.*'),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
