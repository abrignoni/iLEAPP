__artifacts_v2__ = {
    "anydeskConnectionHistory": {
        "name": "AnyDesk - Connection History",
        "description": "Lines of AnyDesk's connection_trace.txt, one row per line, split into direction, "
                       "date and time, the next word, a name field and two numeric fields",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "AnyDesk",
        "notes": "Reads Library/Application Support/.anydesk/connection_trace.txt in the app's Data "
                 "container. Each line is split with a pattern; a line that does not fit it is kept "
                 "whole in Raw Line (shown only for those lines) with the other columns blank, so no line is "
                 "dropped. Direction, Mode, ID 1 and ID 2 are shown as the line holds them. Date and Time "
                 "joins the line's date and time with one space and drops the comma between them. "
                 "Name Field has its surrounding spaces removed. ID 1 In Preferences List is derived, "
                 "see below. Date and time carry no time zone in the file "
                 "and none was established here, so they are text and the artifact has no timeline. "
                 "Direction is the file's first word; in the one research container Direction holds one value on all 4 rows ('Incoming'). "
                 "Mode is the word after the time; Mode (As Stored) holds one value on all 4 rows of that container ('User'). Third-party write-ups of the "
                 "Windows client describe that position as an approval type (for example "
                 "User, Passwd, Token); that is not AnyDesk documentation and was not checked against "
                 "the iOS app, so no meaning is assigned here. "
                 "Name Field was blank on every line of that container. ID 1 and ID 2 are the two numeric "
                 "fields; in that container ID 1 (As Stored) holds one value on all 4 rows, ID 2 (As Stored) holds the "
                 "same value, and ID 2's meaning is not established. In that container neither equalled the device's own AnyDesk ID in "
                 "system.conf (ad.anynet.id), which that container's trace log (anydesk.trace) also names as Client-ID. "
                 "ID 1 In Preferences List says whether ID 1 appears in the "
                 "user.preference.already.connected.users list of the same container's "
                 "com.anydesk.AnyDesk.plist ('Yes', 'No', or blank when that plist is absent or unreadable or the key is absent or not a list); in that container "
                 "ID 1 In Preferences List holds one value on all 4 rows ('Yes'); "
                 "the key name is the app's, and what puts an ID on the list is not established. "
                 "A line shows only that the file holds it; a file with no lines, or no file, "
                 "is not evidence that no session took place, and the file's rotation or size limits "
                 "are not established. Source File names the connection_trace.txt each row came from, because the "
                 "paths have a wildcard container segment and a device can hold more than one container. "
                 "Evidence base: the author's own testing on one research container with AnyDesk 7.1.2 installed "
                 "(the startup banners in its trace log also name 7.0.2 and 7.1.1), 4 lines. Everything said here about what was seen rests on that one "
                 "container; other versions and layouts are untested. "
                 "Not parsed here: service.conf (key names only, see AnyDesk - Settings), "
                 "StoreKit/receipt, the Metal and dyld caches, the SplashBoard snapshots and "
                 "the saved scene state; they were listed in that container but not read for "
                 "connection data.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/.anydesk/connection_trace.txt',
                  '*/Containers/Data/Application/*/Library/Preferences/com.anydesk.AnyDesk.plist'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "device-desktop",
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
                 "Lines starting with '#' are skipped. A plist value that is bytes is shown as hex. "
                 "In the one research container service.conf had keys named for a certificate, a private key and tokens; "
                 "only the key names of any service.conf are reported and every value is withheld "
                 "('(withheld)'). The same rule applies to any key of the other files whose name "
                 "contains 'pkey', 'cert' or 'token'. "
                 "In the one research container ad.anynet.id equalled the Client-ID its trace log names, and "
                 "user.preference.install.date is a plist date. The meaning of the keys is "
                 "not established and the key names are the app's. A key that is "
                 "absent is not evidence of a setting being off: no default is documented here. "
                 "Evidence base: the author's own testing on one research container with AnyDesk 7.1.2 installed "
                 "(the startup banners in its trace log also name 7.0.2 and 7.1.1): system.conf 21 keys, user.conf 7, plist 4, service.conf 6 key names. "
                 "Everything said here about what was seen rests on that one container; other versions "
                 "may carry other keys. "
                 "Store names the kind of file each row came from (system.conf, user.conf, service.conf or the "
                 "preferences plist); Source File names the file itself, because the paths have a "
                 "wildcard container segment and a device can hold more than one container. "
                 "The App Group container group.com.anydesk.Anydesk had an empty .anydesk folder in that "
                 "container and is not read.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/.anydesk/system.conf',
                  '*/Containers/Data/Application/*/Library/Application Support/.anydesk/user.conf',
                  '*/Containers/Data/Application/*/Library/Application Support/.anydesk/service.conf',
                  '*/Containers/Data/Application/*/Library/Preferences/com.anydesk.AnyDesk.plist'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "settings",
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
                 "(Starts With Startup Banner = No). Times are the log's own and carry no time zone, so they are "
                 "text, not a timeline; ordering is the file's order. "
                 "Version is the first word of the block's first Version line and the parenthetical "
                 "after it goes to Version Detail; Build is the first word of the block's first Build line. "
                 "A block with no such line has them blank, and a block before the first banner can "
                 "carry a Version or Build if such lines appear there. "
                 "Log Lines counts only lines that start with a level word and a timestamp; other "
                 "lines are not counted. "
                 "The count columns are numbers of log lines, "
                 "not sessions or connections: Relay Established Lines counts "
                 "'Main relay connection established.', Relay Failed Lines counts lines starting "
                 "'Main relay connection failed', and Warning and Error Lines count entries "
                 "by the log's own level word. "
                 "What a relay connection means for use of the app is not established here. "
                 "Whole-file detail (every other log line) is not reproduced: the log held about "
                 "6,800 lines in the one research container, almost all scheduler, IPC, DNS and "
                 "configuration messages. That trace spanned several years; its rotation rules "
                 "are not established. "
                 "The author found no lines in that trace that he could identify as session or "
                 "file-transfer entries, so none are parsed; a trace from a device with such "
                 "sessions may hold them. "
                 "Source File is kept because the paths have a wildcard container segment and the pattern "
                 "anydesk.trace* can match more than one file, for example a rotated copy; it matched "
                 "one file in the research container. "
                 "Evidence base: the author's own testing on one research container with AnyDesk 7.1.2 installed; "
                 "its trace held 79 startup banners naming versions 7.0.2, 7.1.1 and "
                 "7.1.2. Everything said here about what was seen rests on that one container; other "
                 "layouts are untested.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/anydesk.trace*',),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "file-text",
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
    data_headers = ('Date and Time', 'Direction', 'Mode (As Stored)', 'Name Field',
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
