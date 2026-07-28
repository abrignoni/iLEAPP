__artifacts_v2__ = {
    "mobileInstall_installed": {
        "name": "Apps - Installed",
        "description": "Apps whose most recent mobile_installation.log event is an install/update",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Mobile Installation Logs",
        "notes": "All timestamps are in LOCAL device time (the log records local time), not UTC.",
        "paths": ('**/mobile_installation.log.*', '**/sysdiagnose_*.tar.gz'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "download",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 143 rows",
            "dexter_ios18": "iOS 18.3.2 | 217 rows",
            "felix_ios17": "iOS 17.6.1 | 300 rows",
            "fsfull002_ios17": "iOS 17.1 | 259 rows",
            "hc_ios18_7": "iOS 18.7.8 | 205 rows",
            "iphone11_ios17": "iOS 17.3 | 175 rows",
            "iphone12_ios18": "iOS 18.7 | 245 rows",
            "iphone14plus_ios18": "iOS 18.0 | 264 rows",
            "otto_ios17": "iOS 17.5.1 | 232 rows",
            "abe_ios16": "iOS 16.5 | 218 rows",
            "felix23_ios16": "iOS 16.5 | 255 rows",
            "hickman_ios13": "iOS 13.3.1 | 196 rows",
            "hickman_ios14": "iOS 14.3 | 220 rows",
            "jess_ios15": "iOS 15.0.2 | 572 rows",
            "magnet_ios16": "iOS 16.1.1 | 279 rows",
        }
    },
    "mobileInstall_uninstalled": {
        "name": "Apps - Uninstalled",
        "description": "Apps whose most recent mobile_installation.log event is an uninstall/destroy",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Mobile Installation Logs",
        "notes": "All timestamps are in LOCAL device time (the log records local time), not UTC.",
        "paths": ('**/mobile_installation.log.*', '**/sysdiagnose_*.tar.gz'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "trash",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1 row",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 3 rows",
            "hickman_ios13": "iOS 13.3.1 | 21 rows",
            "hickman_ios14": "iOS 14.3 | 27 rows",
            "jess_ios15": "iOS 15.0.2 | 5 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "mobileInstall_historical": {
        "name": "Apps - Historical Combined",
        "description": "All app install/update/uninstall/container/reboot events from mobile_installation.log",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Mobile Installation Logs",
        "notes": "All timestamps are in LOCAL device time (the log records local time), not UTC.",
        "paths": ('**/mobile_installation.log.*', '**/sysdiagnose_*.tar.gz'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "list",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 783 rows",
            "dexter_ios18": "iOS 18.3.2 | 564 rows",
            "felix_ios17": "iOS 17.6.1 | 559 rows",
            "fsfull002_ios17": "iOS 17.1 | 544 rows",
            "hc_ios18_7": "iOS 18.7.8 | 305 rows",
            "iphone11_ios17": "iOS 17.3 | 317 rows",
            "iphone12_ios18": "iOS 18.7 | 489 rows",
            "iphone14plus_ios18": "iOS 18.0 | 745 rows",
            "otto_ios17": "iOS 17.5.1 | 584 rows",
            "abe_ios16": "iOS 16.5 | 686 rows",
            "felix23_ios16": "iOS 16.5 | 2113 rows",
            "hickman_ios13": "iOS 13.3.1 | 1389 rows",
            "hickman_ios14": "iOS 14.3 | 1309 rows",
            "jess_ios15": "iOS 15.0.2 | 861 rows",
            "magnet_ios16": "iOS 16.1.1 | 757 rows",
        }
    },
    "mobileInstall_reboots": {
        "name": "State - Reboots",
        "description": "Reboot events detected in mobile_installation.log",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Mobile Installation Logs",
        "notes": "All timestamps are in LOCAL device time (the log records local time), not UTC.",
        "paths": ('**/mobile_installation.log.*', '**/sysdiagnose_*.tar.gz'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "refresh",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 2 rows",
            "dexter_ios18": "iOS 18.3.2 | 4 rows",
            "felix_ios17": "iOS 17.6.1 | 2 rows",
            "fsfull002_ios17": "iOS 17.1 | 15 rows",
            "hc_ios18_7": "iOS 18.7.8 | 26 rows",
            "iphone11_ios17": "iOS 17.3 | 3 rows",
            "iphone12_ios18": "iOS 18.7 | 6 rows",
            "iphone14plus_ios18": "iOS 18.0 | 6 rows",
            "otto_ios17": "iOS 17.5.1 | 3 rows",
            "abe_ios16": "iOS 16.5 | 4 rows",
            "felix23_ios16": "iOS 16.5 | 23 rows",
            "hickman_ios13": "iOS 13.3.1 | 12 rows",
            "hickman_ios14": "iOS 14.3 | 9 rows",
            "jess_ios15": "iOS 15.0.2 | 7 rows",
            "magnet_ios16": "iOS 16.1.1 | 7 rows",
        }
    }
}

import io
import re
import tarfile

from scripts.ilapfuncs import artifact_processor

_MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
_UNINSTALL_ACTIONS = ('Destroying container', 'Uninstalling identifier')
_TAR_MEMBER_RE = re.compile(r"logs/MobileInstallation/mobile_installation\.log(\.\d+)?$")


def _first_group(line, *patterns):
    for pat in patterns:
        match = re.search(pat, line)
        if match:
            return match.group(1)
    return ''


def _parse_timestamp(line):
    """Convert the leading 'Wed Jan 15 10:30:00 2024' prefix into a local 'YYYY-MM-DD HH:MM:SS' string."""
    match = re.search(r"^(.*?)(?= \[)", line)
    if not match:
        return None
    parts = match.group(1).split()
    if len(parts) != 5:
        return None
    _weekday, month, day, time, year = parts
    try:
        month_num = _MONTHS.index(month) + 1
        return f'{year}-{month_num:02d}-{int(day):02d} {time}'
    except (ValueError, IndexError):
        return None


def _parse_events(lines):
    """Return a list of (timestamp_local, action, bundle_id, path) events from mobile_installation.log lines."""
    events = []
    for line in lines:
        ts = _parse_timestamp(line)
        if ts is None:
            continue
        if 'Install Successful for' in line:
            bundle = _first_group(line, r"(?<= for \(Placeholder:)(.*)(?=\))",
                                  r"(?<= for \(Customer:)(.*)(?=\))",
                                  r"(?<= for \(System:)(.*)(?=\))", r"(?<= for \()(.*)(?=\))")
            events.append((ts, 'Install successful', bundle, ''))
        if 'Destroying container ' in line:
            events.append((ts, 'Destroying container', _first_group(line, r"(?<=identifier )(.*)(?= at )"),
                           _first_group(line, r"(?<= at )(.*)$")))
        if 'Data container for' in line:
            events.append((ts, 'Data container moved', _first_group(line, r"(?<=for )(.*)(?= is now )"),
                           _first_group(line, r"(?<= at )(.*)$")))
        if 'Made container live for' in line:
            events.append((ts, 'Made container live', _first_group(line, r"(?<=for )(.*)(?= at)"),
                           _first_group(line, r"(?<= at )(.*)$")))
        if 'Uninstalling identifier ' in line:
            events.append((ts, 'Uninstalling identifier',
                           _first_group(line, r"(?<=Uninstalling identifier )(.*)"), ''))
        if 'main: Reboot detected' in line:
            events.append((ts, 'Reboot detected', '', ''))
        if 'Attempting Delta patch update of ' in line:
            events.append((ts, 'Attempting Delta patch',
                           _first_group(line, r"(?<=Attempting Delta patch update of )(.*)(?= from)"),
                           _first_group(line, r"(?<= from )(.*)$")))
    return events


def _iter_log_lines(files_found):
    """Yield (lines, source_full_path) for mobile_installation.log files and those inside sysdiagnose tars."""
    for filename in files_found:
        filename = str(filename)
        if 'mobile_installation' in filename:
            try:
                with open(filename, 'r', encoding='utf8', errors='ignore') as fp:
                    yield fp.readlines(), filename
            except OSError:
                continue
        elif 'sysdiagnose_' in filename and 'IN_PROGRESS_' not in filename:
            try:
                tar = tarfile.open(filename)
            except (tarfile.TarError, OSError):
                continue
            try:
                for member in tar.getmembers():
                    if not _TAR_MEMBER_RE.search(member.name):
                        continue
                    extracted = tar.extractfile(member)
                    if extracted is not None:
                        with io.TextIOWrapper(extracted, encoding='utf-8', errors='ignore') as tfp:
                            yield tfp.readlines(), filename
            finally:
                tar.close()


def _events_and_source(context):
    events = []
    sources = []
    for lines, source in _iter_log_lines(context.get_files_found()):
        rel = context.get_relative_path(source)
        if rel not in sources:
            sources.append(rel)
        events.extend(_parse_events(lines))
    return events, ', '.join(sources)


def _latest_per_bundle(events):
    """Most recent event per (non-empty) bundle id; local timestamp strings sort chronologically."""
    latest = {}
    for event in events:
        bundle = event[2]
        if not bundle:
            continue
        if bundle not in latest or event[0] > latest[bundle][0]:
            latest[bundle] = event
    return latest


@artifact_processor
def mobileInstall_installed(context):
    data_headers = ('Last Installed', 'Bundle ID')
    events, source = _events_and_source(context)
    data_list = [(ev[0], ev[2]) for ev in _latest_per_bundle(events).values()
                 if ev[1] not in _UNINSTALL_ACTIONS]
    return data_headers, data_list, source


@artifact_processor
def mobileInstall_uninstalled(context):
    data_headers = ('Last Uninstalled', 'Bundle ID')
    events, source = _events_and_source(context)
    data_list = [(ev[0], ev[2]) for ev in _latest_per_bundle(events).values()
                 if ev[1] in _UNINSTALL_ACTIONS]
    return data_headers, data_list, source


@artifact_processor
def mobileInstall_historical(context):
    data_headers = ('Timestamp', 'Event', 'Bundle ID', 'Event Path')
    events, source = _events_and_source(context)
    return data_headers, events, source


@artifact_processor
def mobileInstall_reboots(context):
    data_headers = ('Timestamp (Local Time)', 'Description')
    events, source = _events_and_source(context)
    data_list = [(ev[0], ev[1]) for ev in events if ev[1] == 'Reboot detected']
    return data_headers, data_list, source
