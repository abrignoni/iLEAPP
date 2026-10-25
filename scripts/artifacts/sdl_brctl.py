__artifacts_v2__ = {
    "brctl_containers": {
        "name": "Sysdiagnose - iCloud Drive Containers (brctl)",
        "description": "iCloud Drive containers listed by brctl in a sysdiagnose (brctl-container-list.txt), with the "
                       "sync state of the matching library from brctl-dump.txt, as printed",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": (
            "The brctl tool prints the iCloud Drive (CloudDocs, bird) containers of the signed-in account. "
            "One row per line of brctl-container-list.txt: Container ID, Localized Name, Documents "
            "(path) and Scope (the text in square brackets, for example Private: inInitialState) and "
            "Clients (bundle identifiers), all as printed. The library lines of brctl-dump.txt "
            "('- <identifier[length]> foreground|background {client:... server:... last-sync:... "
            "appuninstalled:...}') print each container identifier shortened, with runs of characters "
            "replaced by {n}. A dump line is matched to a container when the shortened identifier, "
            "read as a pattern, fits exactly one listed container identifier and "
            "that identifier fits no other dump line; otherwise Dump Match says No (no fit) or Ambiguous (more than one). Client State and Server "
            "State are the words printed after client: and server:, Last Sync is the printed time after "
            "last-sync: and App Uninstalled is the printed time after appuninstalled: (blank when the "
            "dump prints (null)). The times are printed without a zone in the dump; the dump header "
            "gives the time it was taken with an offset (dump taken at ... -0400 in the tested files) "
            "and the zone of the library times is not stated, so they are shown as printed. A client "
            "state of blocked-app-uninstalled and an App Uninstalled time are what the dump prints for "
            "a library whose app is no longer installed; what sets the time is not established. "
            "Dump Match was Yes on every row of the tested files. Dump "
            "lines without a matching container are listed with the shortened identifier in Container "
            "ID. A container listed here is registered for the account; it does not show that the app "
            "stored files. Observed on three sysdiagnoses (two iOS 26.6 of one device, one iOS 26.6.2 of another): "
            "71 containers and 71 dump library lines on the iOS 26.6 device, each container matching "
            "exactly one library line, with 27 of them in client state blocked-app-uninstalled and 1 more "
            "needs-sync|blocked-app-uninstalled; 34 containers, all matched, on the iOS 26.6.2 device. Not reported: per-item upload "
            "and download queues, which the dump prints as 'not dumping' for every library in the tested "
            "files."
            " Server State held one value on every row of the iOS 26.6.2 file (34 containers)."
        ),
        "paths": (
            '*/brctl-container-list.txt',
            '*/brctl-dump.txt',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cloud",
        "sample_data": {
            "local_sysdiag_ios26_6_a1": "iOS 26.6 sysdiagnose | 71 rows",
            "local_sysdiag_ios26_6_a2": "iOS 26.6 sysdiagnose | 71 rows",
            "local_sysdiag_ios26_6_2_b": "iOS 26.6.2 sysdiagnose | 34 rows",
        },
    },
    "brctl_boot_history": {
        "name": "Sysdiagnose - iCloud Drive Version History (brctl)",
        "description": "The boot_history lists printed at the top of brctl-dump.txt in a sysdiagnose: time, OS build "
                       "and CloudDocs version of each entry, as printed",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": (
            "The dump prints a boot_history block with the lists server_truth, client_truth and "
            "backup_detector. One row per printed entry: List, Time, OS Build, CloudDocs Version, Bird "
            "Schema, DB Schema and Device ID, all as printed. Time is printed without a zone and is "
            "shown as printed. Read plainly, each list gives the OS build the CloudDocs daemon recorded "
            "at that time, so a change of OS Build between entries marks an update seen by that daemon; "
            "the dump does not say what triggers an entry, and a missing build is not evidence that the "
            "device did not run it. The backup_detector entry has no time and a different field "
            "layout, so its Time is blank and the fields are as printed. Observed on three sysdiagnoses: on the iOS 26.6 device 10 entries in each of "
            "server_truth and client_truth spanning ten OS builds, and 5 entries on the iOS 26.6.2 device."
            " CloudDocs Version and DB Schema held one value on every row of the iOS 26.6.2 file (5 entries)."
        ),
        "paths": (
            '*/brctl-dump.txt',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "history",
        "sample_data": {
            "local_sysdiag_ios26_6_a1": "iOS 26.6 sysdiagnose | 21 rows",
            "local_sysdiag_ios26_6_a2": "iOS 26.6 sysdiagnose | 21 rows",
            "local_sysdiag_ios26_6_2_b": "iOS 26.6.2 sysdiagnose | 5 rows",
        },
    },
    "brctl_state": {
        "name": "Sysdiagnose - iCloud Drive Sync State (brctl)",
        "description": "Header, system and scheduler lines of brctl-dump.txt in a sysdiagnose, as printed",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": (
            "One row per printed key and value in the header block (dump time, database version, "
            "database ID, file system type), the system block (network, disk, power, optimize storage, "
            "device name, cellular) and the scheduler block (item counts, push environment, quota, "
            "sync status and the other lines), values as printed. The push token line is not reported. "
            "Device name is printed shortened by the tool (runs of characters replaced by {n}) and is "
            "shown as printed. The state is that of the moment the dump was taken, shown under "
            "'dump taken at'. Lines the tool prints in other blocks (per-library state) are in "
            "'Sysdiagnose - iCloud Drive Containers (brctl)'. Observed on three sysdiagnoses (two iOS 26.6 of "
            "one device, one iOS 26.6.2 of another)."
        ),
        "paths": (
            '*/brctl-dump.txt',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cloud-computing",
        "sample_data": {
            "local_sysdiag_ios26_6_a1": "iOS 26.6 sysdiagnose | 21 rows",
            "local_sysdiag_ios26_6_a2": "iOS 26.6 sysdiagnose | 21 rows",
            "local_sysdiag_ios26_6_2_b": "iOS 26.6.2 sysdiagnose | 21 rows",
        },
    },
}

import os
import re
import tarfile
import zlib

from scripts.ilapfuncs import artifact_processor, get_sysdiagnose_files, logfunc

_READ_ERRORS = (OSError, EOFError, tarfile.TarError, zlib.error)
_ANSI = re.compile(r'\x1b\[[0-9;]*m')

_CONTAINER = re.compile(
    r"^\s*id:(\S+) localizedName:'(.*?)' documents:'(.*?)' \[(.*?)\] clients:\s*(.*)$")
_LIBRARY = re.compile(r'^- <(\S+?)\[(\d+)\] (\S+) \{(.*)\}>$')
_HISTORY = re.compile(
    r'^\s+\[(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d(?:\.\d+)?)\] OS:(\S+) CloudDocs:(\S+) BirdSchema:(\S+) '
    r'DBSchema:(\S+)(?: DeviceID:(\S+))?')
_BACKUP = re.compile(r'^\s+\[([^\]]+)\] OS:(\S+) CloudDocs:(\S+) DBSchema:(\S+)')
_KEYVALUE = re.compile(r'^\s+\+ ([A-Za-z][A-Za-z0-9 \-]*?):\s+(.*?)\s*$')


def _archive_key(rel_or_source):
    """Key that pairs the files of one brctl folder: the archive (or disk) path and the folder."""
    archive, sep, member = rel_or_source.partition(' >> ')
    if not sep:
        return os.path.dirname(archive.replace('\\', '/')), ''
    return archive, os.path.dirname(member.replace('\\', '/'))


def _lines(file_obj, rel):
    try:
        text = file_obj.read().decode('utf-8', errors='replace')
    except _READ_ERRORS as ex:
        logfunc(f'Failed to read {rel}: {ex}')
        return None
    return [_ANSI.sub('', line) for line in text.splitlines()]


def _abbreviation_pattern(short):
    """Regex for an identifier printed with runs of characters replaced by {n}."""
    parts = re.split(r'(\{\d+\})', short)
    out = []
    for part in parts:
        match = re.fullmatch(r'\{(\d+)\}', part)
        out.append('.{%s}' % match.group(1) if match else re.escape(part))
    return re.compile('^' + ''.join(out) + '$')


def _field(body, name):
    match = re.search(r'(?:^|[ {])' + re.escape(name) + r':(\S+(?: \d\d:\d\d:\d\d(?:\.\d+)?)?)', body)
    return match.group(1).rstrip(',') if match else ''


def _libraries(lines):
    rows = []
    for line in lines:
        match = _LIBRARY.match(line)
        if not match:
            continue
        short, length, mode, body = match.groups()
        uninstalled = _field(body, 'appuninstalled')
        rows.append({
            'short': short, 'length': int(length), 'mode': mode,
            'client': _field(body, 'client'),
            'server': _field(body, 'server'),
            'last_sync': _field(body, 'last-sync'),
            'uninstalled': '' if uninstalled == '(null)' else uninstalled})
    return rows


def _gather(context, targets):
    """{archive key: {target: (lines, source path)}} for the requested file names."""
    found = {}
    for target in targets:
        for file_obj, source_path in get_sysdiagnose_files(
                context.get_files_found(), target, text_mode=False):
            rel = context.get_relative_path(source_path)
            lines = _lines(file_obj, rel)
            if lines is not None:
                found.setdefault(_archive_key(source_path), {})[target] = (lines, source_path, rel)
    return found


@artifact_processor
def brctl_containers(context):
    data_headers = ('Container ID', 'Localized Name', 'Documents', 'Scope', 'Clients', 'Dump Match',
                    'Library Mode', 'Client State', 'Server State', 'Last Sync', 'App Uninstalled',
                    'Source File')
    data_list = []
    sources = []
    for _key, files in _gather(context, ('brctl-container-list.txt', 'brctl-dump.txt')).items():
        listed = files.get('brctl-container-list.txt')
        dump = files.get('brctl-dump.txt')
        libraries = _libraries(dump[0]) if dump else []
        containers = []
        if listed:
            sources.append(listed[1])
            for line in listed[0]:
                match = _CONTAINER.match(line)
                if match:
                    containers.append(match.groups())
        if dump:
            sources.append(dump[1])
        rel = ', '.join(x[2] for x in (listed, dump) if x)
        used = set()
        ids = [c[0] for c in containers]
        for identifier, name, documents, scope, clients in containers:
            matches = [(i, lib) for i, lib in enumerate(libraries)
                       if _abbreviation_pattern(lib['short']).match(identifier)]
            if len(matches) == 1 and sum(
                    1 for other in ids if _abbreviation_pattern(matches[0][1]['short']).match(other)) == 1:
                used.add(matches[0][0])
                lib = matches[0][1]
                status = 'Yes'
            else:
                lib = None
                status = 'Ambiguous' if matches else ('No' if dump else '')
            data_list.append((identifier, name, documents, scope, clients, status,
                              lib['mode'] if lib else '', lib['client'] if lib else '',
                              lib['server'] if lib else '', lib['last_sync'] if lib else '',
                              lib['uninstalled'] if lib else '', rel))
        for index, lib in enumerate(libraries):
            if index not in used and (not containers or not any(
                    _abbreviation_pattern(lib['short']).match(i) for i in ids)):
                data_list.append((lib['short'], '', '', '', '', 'Dump only', lib['mode'], lib['client'],
                                  lib['server'], lib['last_sync'], lib['uninstalled'], rel))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def brctl_boot_history(context):
    data_headers = ('List', 'Time (as printed)', 'OS Build', 'CloudDocs Version', 'Bird Schema',
                    'DB Schema', 'Device ID', 'Source File')
    data_list = []
    sources = []
    for _key, files in _gather(context, ('brctl-dump.txt',)).items():
        lines, source_path, rel = files['brctl-dump.txt']
        sources.append(source_path)
        section = None
        for line in lines:
            if line.startswith('boot_history'):
                section = ''
                continue
            if section is None:
                continue
            if line.startswith('server_state') or line.startswith('client_state'):
                break
            if re.match(r'^[a-z_]+$', line):
                section = line
                continue
            match = _HISTORY.match(line)
            if match and section:
                time, build, cloud, bird, schema, device = match.groups()
                data_list.append((section, time, build, cloud, bird, schema, device or '', rel))
                continue
            backup = _BACKUP.match(line) if section == 'backup_detector' else None
            if backup:
                data_list.append((section, '', backup.group(2), backup.group(3), '', backup.group(4),
                                  backup.group(1), rel))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def brctl_state(context):
    data_headers = ('Block', 'Key', 'Value', 'Source File')
    data_list = []
    sources = []
    for _key, files in _gather(context, ('brctl-dump.txt',)).items():
        lines, source_path, rel = files['brctl-dump.txt']
        sources.append(source_path)
        block = 'header'
        for line in lines:
            if line in ('system', 'scheduler'):
                block = line
                continue
            if line.startswith('boot_history'):
                block = 'boot_history'
                continue
            if line.startswith('server_state') or line.startswith('client_state') or line.startswith('users:'):
                block = line.rstrip(':')
                continue
            if line.startswith('- <'):
                break
            if block == 'header':
                taken = re.match(r'^dump taken at (.*)$', line)
                if taken:
                    data_list.append((block, 'dump taken at', taken.group(1), rel))
                    continue
                pair = re.match(r'^(database version|database ID|fsType):\s*(.*)$', line)
                if pair:
                    data_list.append((block, pair.group(1), pair.group(2), rel))
            elif block in ('system', 'scheduler'):
                item = _KEYVALUE.match(line)
                if item and item.group(1) != 'push token':
                    data_list.append((block, item.group(1), item.group(2), rel))
    return data_headers, data_list, '\n'.join(sources)
