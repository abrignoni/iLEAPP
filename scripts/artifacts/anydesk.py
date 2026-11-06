__artifacts_v2__ = {
    "anydeskConnectionHistory": {
        "name": "AnyDesk - Connection History",
        "description": "Lines of AnyDesk's connection_trace.txt, one row per line, split into direction, "
                       "date and time, the next word, a name field and two numeric fields, as stored",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "AnyDesk",
        "notes": "Reads Library/Application Support/.anydesk/connection_trace.txt in the app's Data "
                 "container. Each line is split with a pattern; a line that does not fit it is kept "
                 "whole in Raw Line (shown only for those lines) with the other columns blank, so no line is "
                 "dropped. Every column is shown as stored. Date and time carry no time zone in the file "
                 "and none was established here, so they are text and the artifact has no timeline. "
                 "Direction is the file's first word; in the one iOS sample Direction holds one value on all 4 rows ('Incoming'). "
                 "Mode is the word after the time; Mode (As Stored) holds one value on all 4 sample rows ('User'). Third-party write-ups of the "
                 "Windows client describe that position as an approval type (for example "
                 "User, Passwd, Token); that is not AnyDesk documentation and was not checked against "
                 "the iOS app, so no meaning is assigned here. "
                 "Name Field was blank on every line of the sample. ID 1 and ID 2 are the two numeric "
                 "fields; in the sample ID 1 (As Stored) holds one value on all 4 rows, ID 2 (As Stored) holds the "
                 "same value, and ID 2's meaning is not established. In the sample, neither equalled the device's own AnyDesk ID in "
                 "system.conf (ad.anynet.id), which the trace log (anydesk.trace) also names as Client-ID. "
                 "ID 1 In Preferences List says whether ID 1 appears in the "
                 "user.preference.already.connected.users list of the same container's "
                 "com.anydesk.AnyDesk.plist ('Yes', 'No', or blank when that plist or key is absent); in the sample "
                 "ID 1 In Preferences List holds one value on all 4 rows ('Yes'); "
                 "the key name is the app's, and what puts an ID on the list is not established. "
                 "Presence of a line shows that the app wrote it; a file with no lines, or no file, "
                 "is not evidence that no session took place, and the file's rotation or size limits "
                 "are not established. Data-proven on one iOS 7.x container (4 lines); other layouts "
                 "are untested. "
                 "Not parsed here: service.conf (key names only, see AnyDesk - Settings), "
                 "StoreKit/receipt, the Metal and dyld caches, the SplashBoard snapshots and "
                 "the saved scene state; they were listed in the sample container but not read for "
                 "connection data.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/.anydesk/connection_trace.txt',
                  '*/Containers/Data/Application/*/Library/Preferences/com.anydesk.AnyDesk.plist'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "device-desktop",
        "sample_data": {
            "private_ios_image_7": "AnyDesk 7.1.2 | 4 rows",
        }
    },
    "anydeskSettings": {
        "name": "AnyDesk - Settings",
        "description": "Key and value pairs from AnyDesk's system.conf, user.conf and "
                       "com.anydesk.AnyDesk.plist, and the key names of service.conf",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "AnyDesk",
        "notes": "system.conf and user.conf are 'key=value' text files in Library/Application Support/.anydesk; "
                 "their values are shown as stored. The preferences plist is read with plistlib; dates are "
                 "shown in UTC as the plist stores them, lists and dictionaries as JSON. "
                 "service.conf has keys named for a certificate, a private key and tokens; "
                 "only its key names are reported and every value is withheld "
                 "('(withheld)'). The same rule applies to any key of the other files whose name "
                 "contains 'pkey', 'cert' or 'token'. "
                 "Only a few keys have a meaning that can be checked from the data: "
                 "ad.anynet.id equalled the Client-ID the trace log names on the one sample, and "
                 "user.preference.install.date is a plist date. The meaning of the other "
                 "keys is not established and the key names are the app's. A key that is "
                 "absent is not evidence of a setting being off: no default is documented here. "
                 "Data-proven on one iOS 7.x container (system.conf 21 keys, user.conf 7, plist 4, "
                 "service.conf 6 key names); other versions may carry other keys. "
                 "Source File differs from row to row only when more than one container or file is read; "
                 "on the one-container sample Source File names 4 files on 38 rows and Store already separates "
                 "them one to one. "
                 "The App Group container group.com.anydesk.Anydesk had an empty .anydesk folder on the "
                 "sample and is not read.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/.anydesk/system.conf',
                  '*/Containers/Data/Application/*/Library/Application Support/.anydesk/user.conf',
                  '*/Containers/Data/Application/*/Library/Application Support/.anydesk/service.conf',
                  '*/Containers/Data/Application/*/Library/Preferences/com.anydesk.AnyDesk.plist'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "settings",
        "sample_data": {
            "private_ios_image_7": "AnyDesk 7.1.2 | 38 rows",
        }
    },
    "anydeskTraceStartups": {
        "name": "AnyDesk - Trace Log Startups",
        "description": "One row per block of anydesk.trace that starts at an app startup banner, with the "
                       "version the banner names and counts of the log lines in the block",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "AnyDesk",
        "notes": "anydesk.trace (Library/Application Support) is a text log. A new block starts at each "
                 "'AnyDesk iOS Startup' banner line; entries before the first banner, if any, form one extra row "
                 "(Starts With Startup Banner = No) with a blank Version and Build. Times are the log's own and carry no time zone, so they are "
                 "text, not a timeline; ordering is the file's order. "
                 "Version and Build come from the banner's Version and Build lines as stored. "
                 "The count columns are numbers of log lines, "
                 "not sessions or connections: Relay Established Lines counts "
                 "'Main relay connection established.', Relay Failed Lines counts lines starting "
                 "'Main relay connection failed', and Warning and Error Lines count entries "
                 "by the log's own level word. "
                 "What a relay connection means for use of the app is not established here. "
                 "Whole-file detail (every other log line) is not reproduced: the log held about "
                 "6,800 lines on the sample, almost all scheduler, IPC, DNS and "
                 "configuration messages. A trace of that size spanned several years, "
                 "so the log is not limited to recent use, but its rotation rules are not established. "
                 "No session or file-transfer lines were present in the sample trace, so none "
                 "are parsed; a trace from a device with such sessions may hold them. "
                 "Data-proven on one iOS 7.x container (79 banners, versions 7.0.2, 7.1.1 and 7.1.2).",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/anydesk.trace*',),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "file-text",
        "sample_data": {
            "private_ios_image_7": "AnyDesk 7.1.2 | 80 rows",
        }
    },
}

import json
import os
import plistlib
import re
from datetime import datetime

from scripts.ilapfuncs import artifact_processor, logfunc

WITHHELD = '(withheld)'
SECRET_KEY = re.compile(r'pkey|cert|token', re.IGNORECASE)

# Direction, date, time, the word after the time, then a free field and two numbers.
TRACE_LINE = re.compile(
    r'^(?P<direction>\S+)\s+(?P<date>\d{4}-\d\d-\d\d),\s*(?P<time>\d\d:\d\d(?::\d\d)?)\s+'
    r'(?P<mode>\S+)\s*(?P<name>.*?)\s*(?P<id1>\d+)\s+(?P<id2>\d+)\s*$')

LOG_ENTRY = re.compile(
    r'^\s*(?P<level>[a-z]+)\s+(?P<stamp>\d{4}-\d\d-\d\d \d\d:\d\d:\d\d(?:\.\d+)?)\s+(?P<rest>.*)$')


def _container_key(path):
    """The path segment after 'Application' (container UUID, or bundle id in a backup)."""
    parts = str(path).replace('\\', '/').split('/')
    for i, part in enumerate(parts[:-1]):
        if part == 'Application':
            return parts[i + 1]
    return os.path.dirname(str(path))


def _read_text(path):
    try:
        with open(path, 'rb') as f:
            return f.read().decode('utf-8', errors='replace')
    except OSError as ex:
        logfunc(f'AnyDesk: could not read {path}: {ex}')
        return None


def _read_plist(path):
    try:
        with open(path, 'rb') as f:
            data = plistlib.load(f)
    except (plistlib.InvalidFileException, ValueError, OSError) as ex:
        logfunc(f'AnyDesk: could not read plist {path}: {ex}')
        return None
    return data if isinstance(data, dict) else None


def _plist_value(value):
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')   # plist <date> is UTC
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, (dict, list)):
        return json.dumps(value, default=str)
    return value


def _conf_pairs(text):
    """key=value lines of an AnyDesk .conf file (value may be empty or contain '=')."""
    for line in text.splitlines():
        line = line.strip('\r\n')
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        key, sep, value = line.partition('=')
        yield key.strip(), (value if sep else '')


def _parts(path):
    return str(path).replace('\\', '/').split('/')


def _files(context, name, parent='.anydesk'):
    """Files called `name` whose folder is `parent`, so a same-named file of another app is ignored."""
    found = []
    for f in context.get_files_found():
        parts = _parts(f)
        if parts[-1] == name and parts[-2:-1] == [parent]:
            found.append(str(f))
    return sorted(found)


@artifact_processor
def anydeskConnectionHistory(context):
    data_headers = ('Time (As Stored)', 'Direction', 'Mode (As Stored)', 'Name Field (As Stored)',
                    'ID 1 (As Stored)', 'ID 2 (As Stored)', 'ID 1 In Preferences List',
                    'Raw Line', 'Source File')
    data_list = []
    sources = []

    connected = {}
    for plist_path in _files(context, 'com.anydesk.AnyDesk.plist', 'Preferences'):
        plist = _read_plist(plist_path)
        value = plist.get('user.preference.already.connected.users') if plist else None
        if isinstance(value, list):
            connected[_container_key(plist_path)] = {str(v) for v in value}

    for path in _files(context, 'connection_trace.txt'):
        text = _read_text(path)
        rel = context.get_relative_path(path)
        sources.append(rel)
        if text is None:
            continue
        known = connected.get(_container_key(path))
        for line in text.splitlines():
            if not line.strip():
                continue
            m = TRACE_LINE.match(line.strip())
            if not m:
                data_list.append(('', '', '', '', '', '', '', line.strip(), rel))
                continue
            in_list = '' if known is None else ('Yes' if m.group('id1') in known else 'No')
            data_list.append((f"{m.group('date')} {m.group('time')}", m.group('direction'),
                              m.group('mode'), m.group('name'), m.group('id1'), m.group('id2'),
                              in_list, '', rel))

    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def anydeskSettings(context):
    data_headers = ('Store', 'Key', 'Value', 'Source File')
    data_list = []
    sources = []

    for name, store in (('system.conf', 'system.conf'), ('user.conf', 'user.conf')):
        for path in _files(context, name):
            text = _read_text(path)
            rel = context.get_relative_path(path)
            sources.append(rel)
            if text is None:
                continue
            for key, value in _conf_pairs(text):
                data_list.append((store, key, WITHHELD if SECRET_KEY.search(key) else value, rel))

    for path in _files(context, 'service.conf'):
        text = _read_text(path)
        rel = context.get_relative_path(path)
        sources.append(rel)
        if text is None:
            continue
        for key, _ in _conf_pairs(text):
            data_list.append(('service.conf', key, WITHHELD, rel))

    for path in _files(context, 'com.anydesk.AnyDesk.plist', 'Preferences'):
        plist = _read_plist(path)
        rel = context.get_relative_path(path)
        sources.append(rel)
        if plist is None:
            continue
        for key, value in plist.items():
            value = _plist_value(value)
            data_list.append(('com.anydesk.AnyDesk.plist', key,
                              WITHHELD if SECRET_KEY.search(key) else value, rel))

    return data_headers, data_list, '\n'.join(sources)


def _new_block(stamp):
    return {'start': stamp, 'version': '', 'build': '', 'lines': 0, 'established': 0,
            'failed': 0, 'warning': 0, 'error': 0}


@artifact_processor
def anydeskTraceStartups(context):
    data_headers = ('Block Start (As Stored)', 'Starts With Startup Banner', 'Version', 'Version Detail (As Stored)', 'Build',
                    'Log Lines', 'Relay Established Lines', 'Relay Failed Lines',
                    'Warning Lines', 'Error Lines', 'Source File')
    data_list = []
    sources = []

    trace_files = []
    for f in context.get_files_found():
        parts = _parts(f)
        if parts[-1].startswith('anydesk.trace') and parts[-2:-1] == ['Application Support']:
            trace_files.append(str(f))
    trace_files.sort()
    for path in trace_files:
        text = _read_text(path)
        rel = context.get_relative_path(path)
        sources.append(rel)
        if text is None:
            continue

        blocks = []
        block = None
        for line in text.splitlines():
            m = LOG_ENTRY.match(line)
            if not m:
                continue
            stamp = m.group('stamp')
            message = m.group('rest').split(' - ', 1)[-1] if ' - ' in m.group('rest') else ''
            if '* AnyDesk iOS Startup *' in message:
                block = _new_block(stamp)
                block['banner'] = True
                blocks.append(block)
            elif block is None:
                block = _new_block(stamp)
                block['banner'] = False
                blocks.append(block)
            block['lines'] += 1
            level = m.group('level')
            if level == 'warning':
                block['warning'] += 1
            elif level == 'error':
                block['error'] += 1
            vm = re.match(r'^\* Version (\S+)(?: \((.*)\))?\s*$', message)
            if vm and not block['version']:
                block['version'] = vm.group(1)
                block['detail'] = vm.group(2) or ''
            bm = re.match(r'^\* Build (\S+)', message)
            if bm and not block['build']:
                block['build'] = bm.group(1)
            if message.startswith('Main relay connection established'):
                block['established'] += 1
            elif message.startswith('Main relay connection failed'):
                block['failed'] += 1

        for b in blocks:
            data_list.append((b['start'], 'Yes' if b['banner'] else 'No', b['version'], b.get('detail', ''), b['build'], b['lines'],
                              b['established'], b['failed'], b['warning'], b['error'], rel))

    return data_headers, data_list, '\n'.join(sources)
