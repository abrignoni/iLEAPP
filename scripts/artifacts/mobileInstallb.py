__artifacts_v2__ = {
    "mobileInstallb": {
        "name": "Mobile Installation Logs History",
        "description": "App install/update/uninstall and reboot events from mobile_installation.log (iOS 17+)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Mobile Installation Logs",
        "notes": "All timestamps are in LOCAL device time (the log records local time), not UTC.",
        "paths": ('*/mobile_installation.log.*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "package",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 700 rows",
            "felix_ios17": "iOS 17.6.1 | 697 rows",
            "fsfull002_ios17": "iOS 17.1 | 714 rows",
            "hc_ios18_7": "iOS 18.7.8 | 408 rows",
            "iphone11_ios17": "iOS 17.3 | 416 rows",
            "iphone12_ios18": "iOS 18.7 | 681 rows",
            "iphone14plus_ios18": "iOS 18.0 | 960 rows",
            "otto_ios17": "iOS 17.5.1 | 714 rows",
        }
    },
    "mobileInstallb_reboots": {
        "name": "Reboots - Mobile Installation Logs",
        "description": "Reboot events from mobile_installation.log (iOS 17+)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Mobile Installation Logs",
        "notes": "All timestamps are in LOCAL device time (the log records local time), not UTC.",
        "paths": ('*/mobile_installation.log.*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "refresh",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 4 rows",
            "felix_ios17": "iOS 17.6.1 | 2 rows",
            "fsfull002_ios17": "iOS 17.1 | 15 rows",
            "hc_ios18_7": "iOS 18.7.8 | 26 rows",
            "iphone11_ios17": "iOS 17.3 | 3 rows",
            "iphone12_ios18": "iOS 18.7 | 6 rows",
            "iphone14plus_ios18": "iOS 18.0 | 6 rows",
            "otto_ios17": "iOS 17.5.1 | 3 rows",
        }
    }
}

import re

from packaging import version

from scripts.ilapfuncs import artifact_processor, iOS

_MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# marker substring -> event Type label (first match wins, matching the original elif order)
_EVENTS = {
    'Attempting Delta patch update': 'Update',
    'Installing <MIInstallableBundle': 'Install',
    'Data container for': 'Container',
    'Made container live for': 'Container Live',
    'Reboot detected': 'Reboot',
    'Install Successful for': 'Install Successful',
    'Running installation as': 'Running Installation',
    'Attempting Parallel patch update': 'Parallel Update',
    'Uninstalling identifier': 'Uninstalling',
    'Destroying container': 'Destroying',
}


def _line_splitting(line):
    if not re.match(r"^[a-zA-Z]", line):
        return None
    splitline = line.split(' ', 6)
    if len(splitline) < 7:
        return None
    notice = splitline.pop(6)
    _weekday, month, space, day, time, year = splitline
    if space != '':
        splitline = line.split(' ', 5)
        notice = splitline.pop(5)
        _weekday, month, day, time, year = splitline
    if 'Reboot detected' in notice:
        notice = notice.split('main: ')[-1]
    elif ':]: ' in notice:
        notice = notice.split(':]: ')[-1]
    else:
        notice = notice.split(': ')[-1]
    try:
        month_num = _MONTHS.index(month) + 1
    except ValueError:
        return None
    timestamp = f'{year}-{month_num:02d}-{int(day):02d} {time}'
    return timestamp, notice.strip()


def _parse(context):
    """Return (rows, source) where rows are (timestamp_local, type, notice, source_rel); iOS 17+ only."""
    rows = []
    sources = []
    if version.parse(iOS.get_version()) < version.parse("17"):
        return rows, ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        rel = context.get_relative_path(file_found)
        try:
            with open(file_found, 'r', encoding='utf8', errors='ignore') as f:
                lines = f.readlines()
        except OSError:
            continue
        if rel not in sources:
            sources.append(rel)
        for line in lines:
            for marker, desc in _EVENTS.items():
                if marker in line:
                    values = _line_splitting(line)
                    if values:
                        rows.append((values[0], desc, values[1], rel))
                    break

    return rows, ', '.join(sources)


@artifact_processor
def mobileInstallb(context):
    data_headers = ('Timestamp (Local)', 'Type', 'Notice', 'Source File')
    rows, source = _parse(context)
    return data_headers, rows, source


@artifact_processor
def mobileInstallb_reboots(context):
    data_headers = ('Timestamp (Local)', 'Type', 'Notice', 'Source File')
    rows, source = _parse(context)
    return data_headers, [row for row in rows if row[1] == 'Reboot'], source
